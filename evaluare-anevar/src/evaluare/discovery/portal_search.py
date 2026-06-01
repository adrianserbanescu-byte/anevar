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


def build_search_url(portal: str, judet: str, localitate: str) -> str:
    """Construieste URL-ul paginii de cautare pentru case+teren intr-o zona."""
    judet = judet.strip().lower()
    localitate = localitate.strip().lower()
    if portal == "imobiliare":
        return f"{BAZE['imobiliare']}/vanzare-case-vile/judetul-{judet}/{localitate}"
    if portal == "storia":
        return f"{BAZE['storia']}/ro/rezultate/vanzare/casa/{judet}/{localitate}"
    raise ValueError(f"Portal necunoscut: {portal}")


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
    fetcher: Callable[[str], str] = fetch_html,
) -> list[str]:
    """Descarca pagina de cautare si intoarce URL-urile anunturilor. Fetcher injectabil."""
    url = build_search_url(portal, judet, localitate)
    html = fetcher(url)
    return extract_listing_urls(html, baza=BAZE[portal])
