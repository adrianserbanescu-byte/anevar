"""Cautare anunturi pe portal: construieste URL de cautare + extrage URL-uri de anunt.

AVERTISMENT: scraping direct - poate incalca ToS si se poate strica la schimbari de layout.
"""
from __future__ import annotations

import re
from typing import Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from evaluare.importers.url_parser import fetch_html

BAZE = {
    "imobiliare": "https://www.imobiliare.ro",
    "storia": "https://www.storia.ro",
}


# Segmentul de URL per portal si categorie (casa vs teren)
_SEGMENT = {
    ("imobiliare", "casa"): "vanzare-case-vile/judetul-{j}",
    ("imobiliare", "teren"): "vanzare-terenuri/judetul-{j}",
    ("storia", "casa"): "ro/rezultate/vanzare/casa/{j}",
    ("storia", "teren"): "ro/rezultate/vanzare/teren/{j}",
}


def build_search_url(portal: str, judet: str, localitate: str = "",
                     categorie: str = "casa") -> str:
    """Construieste URL-ul paginii de cautare (casa sau teren). Fara localitate -> pe judet."""
    judet = judet.strip().lower()
    localitate = (localitate or "").strip().lower()
    if portal not in BAZE:
        raise ValueError(f"Portal necunoscut: {portal}")
    seg = _SEGMENT.get((portal, categorie))
    if seg is None:
        raise ValueError(f"Categorie necunoscuta: {categorie}")
    baza = f"{BAZE[portal]}/{seg.format(j=judet)}"
    return f"{baza}/{localitate}" if localitate else baza


def extract_listing_urls(html: str, baza: str) -> list[str]:
    """Extrage URL-urile anunturilor individuale (linkuri /oferta/) dintr-o pagina de cautare."""
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    vazute = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.search(r"/oferta/", href):
            absolut = urljoin(baza + "/", href)
            if absolut not in vazute:
                vazute.add(absolut)
                urls.append(absolut)
    return urls


def cauta_anunturi(
    portal: str, judet: str, localitate: str,
    fetcher: Callable[[str], str] = fetch_html, categorie: str = "casa",
) -> list[str]:
    """Descarca pagina de cautare si intoarce URL-urile anunturilor. Fetcher injectabil.

    Incearca intai localitatea; daca da eroare (ex. 404 - unele orase au URL diferit pe storia)
    sau nu gaseste anunturi, cade pe cautarea la nivel de judet.
    """
    incercari = [localitate, ""] if localitate else [""]
    for loc in incercari:
        try:
            html = fetcher(build_search_url(portal, judet, loc, categorie))
        except Exception:
            continue
        urls = extract_listing_urls(html, baza=BAZE[portal])
        if urls:
            return urls
    return []
