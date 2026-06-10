"""Orchestratorul descoperirii: search → scrape → parse → extract → score → rank."""
from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal

from bs4 import BeautifulSoup

from evaluare.ai.narrative import NarrativeClient
from evaluare.discovery.extractor import extrage_atribute
from evaluare.discovery.ponderi import ponderi_pentru
from evaluare.discovery.portal_search import cauta_anunturi_multi
from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.results import CandidateResult, LandDiscoveryResult
from evaluare.discovery.scoring import scor_candidat
from evaluare.importers.url_parser import fetch_html, parse_listing_html
from evaluare.logging_setup import get_logger

log = get_logger(__name__)


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


def _apartament_exclus(tip_activ: str | None, subiect_camere, candidat_camere) -> bool:
    """Filtru de eligibilitate la APARTAMENT: candidatul cu >1 cameră diferență față de subiect NU
    e comparabil (council, abordare in 2 pasi: filtru + scor). Doar la `tip_activ == "apartament"`
    si doar cand ambele numere de camere sunt cunoscute (altfel nu filtram, ca sa nu pierdem candidati).
    """
    return (tip_activ == "apartament" and subiect_camere is not None
            and candidat_camere is not None and abs(candidat_camere - subiect_camere) > 1)


def descopera(
    portal: str, judet: str, localitate: str, subiect: SubjectProfile,
    atribute_secundare: list, fetcher: Callable[[str], str] = fetch_html,
    client: NarrativeClient | None = None, max_candidati: int = 20,
    tip_activ: str | None = None, ponderi: dict | None = None,
) -> list[CandidateResult]:
    """Pipeline complet de descoperire. Întoarce candidați rankați după relevanță.

    `tip_activ` selectează ponderile per categorie (config-driven). None → ponderile de bază
    (modelul casei) → comportament identic cu varianta istorică. `ponderi` (opțional) suprascrie
    ponderile efective ale categoriei (ex. override-ul editat de evaluator, persistat local).
    """
    ponderi = ponderi if ponderi is not None else ponderi_pentru(tip_activ)
    # #3 (Adi): apartament -> sectiunea de APARTAMENTE a portalului. Fara asta, cauta_anunturi_multi
    # cade pe "casa" (default) -> apartamentul aducea CASE. tip_activ schimba doar ponderile + filtrul.
    categorie = "apartament" if tip_activ == "apartament" else "casa"
    urls = cauta_anunturi_multi(portal, judet, localitate, fetcher=fetcher,
                                categorie=categorie)[:max_candidati]
    rezultate: list[CandidateResult] = []
    for url in urls:
        try:
            html = fetcher(url)
        except Exception as e:
            log.debug("Anunt sarit (fetch esuat) %s: %s", url, e)
            continue
        parsed = parse_listing_html(html, sursa_url=url)
        if parsed.pagina_lista:                 # pagină de listă/căutare, nu anunț -> sare
            log.debug("Anunt sarit (pagina de lista) %s", url)
            continue
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
        # numarul de camere din date structurate (driver major la apartament — P0.2)
        if parsed.nr_camere is not None:
            extraction.profile.nr_camere = parsed.nr_camere
            extraction.profile.texte.setdefault("nr_camere", str(parsed.nr_camere))
        # GAP #3 (audit comparabile): an + încălzire din datele STRUCTURATE (parser/JSON-LD) au
        # prioritate când există; altfel rămâne valoarea LLM. Înainte erau aruncate -> cu client=None
        # (config validă) veneau null deși existau în pagină -> atribute excluse tăcut din scor.
        if parsed.an is not None:
            extraction.profile.an = parsed.an
            extraction.profile.texte.setdefault("an", str(parsed.an))
        if parsed.incalzire:
            extraction.profile.incalzire = parsed.incalzire
            extraction.profile.texte.setdefault("incalzire", parsed.incalzire)
        if _apartament_exclus(tip_activ, subiect.nr_camere, parsed.nr_camere):
            log.debug("Apartament sarit (camere %s vs subiect %s, dif >1) %s",
                      parsed.nr_camere, subiect.nr_camere, url)
            continue
        breakdown = scor_candidat(subiect, extraction.profile, ponderi)
        # OLX (și alte anunțuri cu text liber) dau adesea prețul fără suprafață structurată →
        # declasăm scorul + marcăm „completează manual" (council 2026-06-06, Topic 8).
        if not parsed.suprafata:
            breakdown.relevanta = max(0, breakdown.relevanta - 30)
            breakdown.explicatie = (f"{breakdown.explicatie} ⚠ Suprafață lipsă — "
                                    "completează manual înainte de a folosi în grilă.").strip()
        pret_mp = _pret_mp_daca_teren_comparabil(parsed, subiect, extraction.profile.teren)
        rezultate.append(CandidateResult(
            url=url, titlu=parsed.titlu, pret=parsed.pret, suprafata=parsed.suprafata,
            teren=extraction.profile.teren, pret_mp=pret_mp, poza=parsed.poza,
            breakdown=breakdown, secundare=extraction.secundare,
        ))
    _marcheaza_pret_atipic(rezultate)   # GAP #4 (audit comparabile): marchează outlierii €/mp
    # GAP #2 (audit comparabile): candidații cu `incredere_scazuta` (>=3 atribute lipsă — anunț
    # expirat/truncat) merg la COADĂ, chiar dacă relevanța brută pe puținele atribute cunoscute e mare
    # (un singur atribut apropiat dădea 96% înșelător). În fiecare grupă: ordine după relevanță.
    rezultate.sort(key=lambda r: (r.breakdown.incredere_scazuta, -r.breakdown.relevanta))
    return rezultate


def _marcheaza_pret_atipic(rezultate: list[CandidateResult]) -> None:
    """GAP #4 (audit comparabile, calibrat la re-auditul final): marchează — NU exclude — anunțurile cu
    €/mp PUTERNIC atipic (factor 3 sub/peste mediana setului). €/mp e construit (include terenul), deci o
    variație ±50% e legitimă (teren premium) -> marcăm doar outlierii extremi = preț tastat greșit (ex. 1€);
    aplicația AVERTIZEAZĂ, evaluatorul decide. Nevoie de >=3 prețuri valide ca mediana să fie semnificativă."""
    eur_mp = sorted(r.pret / r.suprafata for r in rezultate
                    if r.pret and r.suprafata and r.suprafata > 0)
    if len(eur_mp) < 3:
        return
    mediana = eur_mp[len(eur_mp) // 2]
    if mediana <= 0:
        return
    for r in rezultate:
        if not (r.pret and r.suprafata and r.suprafata > 0):
            continue
        val = r.pret / r.suprafata
        # Re-audit final: €/mp e CONSTRUIT (include valoarea terenului) -> o casă genuină pe teren mare/
        # premium are €/mp legitim mai mare; un prag de ±50% o marca FALS-pozitiv. Marcăm doar outlierii
        # EXTREMI (factor 3 sub/peste mediană) = preț tastat greșit (ex. 1€), nu variația legitimă de teren.
        if val < mediana / 3 or val > mediana * 3:
            r.breakdown.explicatie = (f"{r.breakdown.explicatie} ⚠ Preț/mp puternic atipic "
                                      "(de câteva ori sub/peste mediana setului) — verifică prețul.").strip()


def _relevanta_teren(supr, subiect_supr) -> int:
    """Relevanta 0-100 pe baza similaritatii de suprafata (criteriul dominant la teren)."""
    if not supr or supr <= 0 or not subiect_supr or subiect_supr <= 0:
        return 50
    dif = abs(supr - subiect_supr) / subiect_supr
    return max(0, round(100 * (1 - min(Decimal("1"), dif))))


def descopera_teren(
    portal: str, judet: str, localitate: str, suprafata_subiect: Decimal | None = None,
    fetcher: Callable[[str], str] = fetch_html, max_candidati: int = 20,
) -> list[LandDiscoveryResult]:
    """Descopera comparabile de TEREN: cauta anunturi de teren, calculeaza EUR/mp si relevanta.

    Relevanta = similaritatea de suprafata (la teren, pretul/mp depinde puternic de suprafata).
    """
    urls = cauta_anunturi_multi(portal, judet, localitate, fetcher=fetcher, categorie="teren")
    urls = urls[:max_candidati]
    rezultate: list[LandDiscoveryResult] = []
    for url in urls:
        try:
            parsed = parse_listing_html(fetcher(url), sursa_url=url)
        except Exception as e:
            log.debug("Anunt teren sarit (fetch/parse esuat) %s: %s", url, e)
            continue
        if parsed.pagina_lista:                 # pagină de listă/căutare, nu anunț -> sare
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
