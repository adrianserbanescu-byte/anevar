"""Orchestratorul descoperirii: search → scrape → parse → extract → score → rank."""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Callable, Optional

from bs4 import BeautifulSoup

from evaluare.ai.narrative import NarrativeClient
from evaluare.importers.url_parser import fetch_html, parse_listing_html
from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.portal_search import cauta_anunturi
from evaluare.discovery.extractor import extrage_atribute
from evaluare.discovery.scoring import scor_candidat
from evaluare.discovery.results import CandidateResult, LandDiscoveryResult


def _descriere_din_nextdata(soup, max_caractere: int) -> str:
    """Descrierea completa a agentului din __NEXT_DATA__ (storia/Next.js: ad.description).

    Pe site-urile randate client-side (storia), descrierea bogata + lista de specificatii NU
    sunt in HTML-ul static (corpul randat are doar chrome + footer); ele sunt in blobul JSON
    __NEXT_DATA__, in campul `description` (HTML). Luam cel mai lung astfel de camp si scoatem
    tag-urile.
    """
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        return ""
    raw = tag.get_text()
    if not raw:
        return ""
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return ""
    best = ""
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            d = node.get("description")
            if isinstance(d, str) and len(d) > len(best):
                best = d
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    if not best:
        return ""
    text = BeautifulSoup(best, "html.parser").get_text(" ", strip=True)
    return text[:max_caractere]


def extrage_descriere(html: str, max_caractere: int = 4000) -> str:
    """Extrage textul reprezentativ al anuntului: titlu + meta + DESCRIEREA REALA.

    Prioritate: descrierea completa din __NEXT_DATA__ (storia) — contine toata descrierea
    agentului + lista de specificatii. Daca lipseste (ex. imobiliare, randat server-side),
    cade pe corpul paginii dupa titlul „Descriere(a proprietatii)".
    """
    soup = BeautifulSoup(html, "html.parser")
    parti: list[str] = []
    t = soup.find("title")
    if t and t.get_text():
        parti.append(t.get_text(strip=True))
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        parti.append(md["content"])

    # 1) descrierea bogata din __NEXT_DATA__ (storia & alte site-uri Next.js)
    nd = _descriere_din_nextdata(soup, max_caractere)
    if len(nd) >= 200:
        parti.append(nd)
        return " ".join(parti)

    # 2) fallback: corpul paginii (imobiliare e randat server-side -> descrierea e in body)
    body = soup.get_text(" ", strip=True)
    idx = body.lower().find("descrierea propriet")
    if idx < 0:
        idx = body.lower().find("descriere")
    if idx >= 0:
        parti.append(body[idx:idx + max_caractere])
    else:
        parti.append(body[:max_caractere])
    return " ".join(parti)


TOLERANTA_TEREN = Decimal("0.40")   # +-40%: peste asta, terenul nu e comparabil


def _pret_mp_daca_teren_comparabil(parsed, subiect, teren_candidat):
    """€/mp construit, DOAR daca terenul candidatului e comparabil cu al subiectului.

    Pe un anunt de casa+teren, €/mp construit amesteca valoarea terenului. Are sens
    doar cand terenul e similar (atunci contributia terenului e aproape constanta).
    """
    if parsed.pret is None or not parsed.suprafata or parsed.suprafata <= 0:
        return None
    st = subiect.teren
    if st is None or st <= 0 or teren_candidat is None:
        return None
    if abs(teren_candidat - st) / st > TOLERANTA_TEREN:
        return None
    return round(parsed.pret / parsed.suprafata)


def descopera(
    portal: str, judet: str, localitate: str, subiect: SubjectProfile,
    atribute_secundare: list, fetcher: Callable[[str], str] = fetch_html,
    client: Optional[NarrativeClient] = None, max_candidati: int = 8,
) -> list[CandidateResult]:
    """Pipeline complet de descoperire. Întoarce candidați rankați după relevanță."""
    urls = cauta_anunturi(portal, judet, localitate, fetcher=fetcher)[:max_candidati]
    rezultate: list[CandidateResult] = []
    for url in urls:
        try:
            html = fetcher(url)
        except Exception:
            continue
        parsed = parse_listing_html(html, sursa_url=url)
        descriere = extrage_descriere(html)
        extraction = extrage_atribute(descriere, atribute_secundare, client=client)
        # suprafata casei pentru potrivire = suprafata reala din anunt (parser, nu LLM)
        extraction.profile.suprafata_construita = parsed.suprafata
        if parsed.suprafata is not None:
            extraction.profile.texte.setdefault("suprafata_construita", str(parsed.suprafata))
        # suprafata terenului din date structurate (storia) are prioritate fata de LLM
        if parsed.suprafata_teren is not None:
            extraction.profile.teren = parsed.suprafata_teren
            extraction.profile.texte.setdefault("teren", str(parsed.suprafata_teren))
        breakdown = scor_candidat(subiect, extraction.profile)
        pret_mp = _pret_mp_daca_teren_comparabil(parsed, subiect, extraction.profile.teren)
        rezultate.append(CandidateResult(
            url=url, titlu=parsed.titlu, pret=parsed.pret, suprafata=parsed.suprafata,
            teren=extraction.profile.teren, pret_mp=pret_mp, breakdown=breakdown,
            secundare=extraction.secundare,
        ))
    rezultate.sort(key=lambda r: r.breakdown.relevanta, reverse=True)
    return rezultate


def _relevanta_teren(supr, subiect_supr) -> int:
    """Relevanta 0-100 pe baza similaritatii de suprafata (criteriul dominant la teren)."""
    if not supr or supr <= 0 or not subiect_supr or subiect_supr <= 0:
        return 50
    dif = abs(supr - subiect_supr) / subiect_supr
    return max(0, round(100 * (1 - min(Decimal("1"), dif))))


def descopera_teren(
    portal: str, judet: str, localitate: str, suprafata_subiect: Optional[Decimal] = None,
    fetcher: Callable[[str], str] = fetch_html, max_candidati: int = 8,
) -> list[LandDiscoveryResult]:
    """Descopera comparabile de TEREN: cauta anunturi de teren, calculeaza EUR/mp si relevanta.

    Relevanta = similaritatea de suprafata (la teren, pretul/mp depinde puternic de suprafata).
    """
    from evaluare.discovery.portal_search import cauta_anunturi

    urls = cauta_anunturi(portal, judet, localitate, fetcher=fetcher, categorie="teren")
    urls = urls[:max_candidati]
    rezultate: list[LandDiscoveryResult] = []
    for url in urls:
        try:
            parsed = parse_listing_html(fetcher(url), sursa_url=url)
        except Exception:
            continue
        supr = parsed.suprafata_teren or parsed.suprafata
        pret_mp = None
        if parsed.pret is not None and supr and supr > 0:
            pret_mp = round(parsed.pret / supr)
        nota = "" if pret_mp is not None else "fara pret/suprafata clare — verifica manual"
        rezultate.append(LandDiscoveryResult(
            url=url, titlu=parsed.titlu, pret=parsed.pret, suprafata=supr, pret_mp=pret_mp,
            relevanta=_relevanta_teren(supr, suprafata_subiect), nota=nota,
        ))
    rezultate.sort(key=lambda r: r.relevanta, reverse=True)
    return rezultate
