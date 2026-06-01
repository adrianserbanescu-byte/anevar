"""Orchestratorul descoperirii: search → scrape → parse → extract → score → rank."""
from __future__ import annotations

from decimal import Decimal
from typing import Callable, Optional

from bs4 import BeautifulSoup

from evaluare.ai.narrative import NarrativeClient
from evaluare.importers.url_parser import fetch_html, parse_listing_html
from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.portal_search import cauta_anunturi
from evaluare.discovery.extractor import extrage_atribute
from evaluare.discovery.scoring import scor_candidat
from evaluare.discovery.results import CandidateResult


def extrage_descriere(html: str, max_caractere: int = 4000) -> str:
    """Extrage un text reprezentativ al anuntului (titlu + meta + corp), trunchiat."""
    soup = BeautifulSoup(html, "html.parser")
    parti: list[str] = []
    t = soup.find("title")
    if t and t.get_text():
        parti.append(t.get_text(strip=True))
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        parti.append(md["content"])
    parti.append(soup.get_text(" ", strip=True)[:max_caractere])
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
            pret_mp=pret_mp, breakdown=breakdown, secundare=extraction.secundare,
        ))
    rezultate.sort(key=lambda r: r.breakdown.relevanta, reverse=True)
    return rezultate
