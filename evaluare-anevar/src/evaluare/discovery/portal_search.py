"""Cautare anunturi pe portal: construieste URL de cautare + extrage URL-uri de anunt.

AVERTISMENT: scraping direct - poate incalca ToS si se poate strica la schimbari de layout.
"""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from evaluare.importers.url_parser import fetch_html
from evaluare.logging_setup import get_logger

log = get_logger(__name__)

BAZE = {
    "imobiliare": "https://www.imobiliare.ro",
    "storia": "https://www.storia.ro",
    "imoradar": "https://www.imoradar24.ro",
}


# Segmentul de URL per portal si categorie (casa vs teren)
# Imoradar24 (P1.1): agregator cu slug curat /{cat}-de-vanzare/judetul-{j}/{localitate} si anunturi
# /oferta/...; paginile de anunt sunt self-hosted (parserul generic extrage pret/supr/poza din JSON-LD+og).
_SEGMENT = {
    ("imobiliare", "casa"): "vanzare-case-vile/judetul-{j}",
    ("imobiliare", "teren"): "vanzare-terenuri/judetul-{j}",
    ("storia", "casa"): "ro/rezultate/vanzare/casa/{j}",
    ("storia", "teren"): "ro/rezultate/vanzare/teren/{j}",
    ("imoradar", "casa"): "case-de-vanzare/judetul-{j}",
    ("imoradar", "teren"): "terenuri-de-vanzare/judetul-{j}",
}


def _slug(text: str) -> str:
    """Normalizeaza pentru URL: pliaza diacriticele (ă->a, ț->t, ...), lowercase, spatii -> '-'.

    Esential pentru județele/localitatile cu diacritice (Bistrița-Năsăud, Brăila, Timiș, Argeș...):
    fara asta URL-ul de cautare contine diacritice brute si portalul da 404 -> zero comparabile.
    """
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = text.strip().lower()
    return re.sub(r"\s+", "-", text)


def build_search_url(portal: str, judet: str, localitate: str = "",
                     categorie: str = "casa") -> str:
    """Construieste URL-ul paginii de cautare (casa sau teren). Fara localitate -> pe judet."""
    judet = _slug(judet)
    localitate = _slug(localitate)
    if portal not in BAZE:
        raise ValueError(f"Portal necunoscut: {portal}")
    seg = _SEGMENT.get((portal, categorie))
    if seg is None:
        raise ValueError(f"Categorie necunoscuta: {categorie}")
    baza = f"{BAZE[portal]}/{seg.format(j=judet)}"
    return f"{baza}/{localitate}" if localitate else baza


def extract_listing_urls(html: str, baza: str, prefer: str = "") -> list[str]:
    """Extrage URL-urile anunturilor individuale (linkuri /oferta/) dintr-o pagina de cautare.

    `prefer` (ex. localitatea) — daca e dat SI exista anunturi al caror slug il contine,
    intoarce doar pe acelea. Astfel anunturile PROMOVATE din alta localitate (ex. un anunt
    Pipera afisat pe cautarea Breaza) nu mai intra in setul de comparabile. Daca niciunul nu
    se potriveste, intoarce toate (mai bine ceva decat nimic).
    """
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
    prefer = (prefer or "").strip().lower()
    if prefer:
        potrivite = [u for u in urls if prefer in u.lower()]
        if potrivite:
            return potrivite
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
        except Exception as e:
            log.debug("Cautare esuata (portal=%s, judet=%s, loc=%r): %s", portal, judet, loc, e)
            continue
        # la cautarea pe localitate, preferam anunturile cu localitatea in slug (taie promovate)
        urls = extract_listing_urls(html, baza=BAZE[portal], prefer=loc)
        if urls:
            return urls
    return []
