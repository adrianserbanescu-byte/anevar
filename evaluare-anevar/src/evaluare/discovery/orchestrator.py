"""Orchestratorul descoperirii: search → scrape → parse → extract → score → rank."""
from __future__ import annotations

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
        breakdown = scor_candidat(subiect, extraction.profile)
        rezultate.append(CandidateResult(
            url=url, titlu=parsed.titlu, pret=parsed.pret, suprafata=parsed.suprafata,
            breakdown=breakdown, secundare=extraction.secundare,
        ))
    rezultate.sort(key=lambda r: r.breakdown.relevanta, reverse=True)
    return rezultate
