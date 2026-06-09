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


def extract_listing_urls(html: str, baza: str, prefer: str = "", strict: bool = False) -> list[str]:
    """Extrage URL-urile anunturilor individuale (linkuri /oferta/) dintr-o pagina de cautare.

    `prefer` (ex. localitatea) — daca e dat SI exista anunturi al caror slug il contine,
    intoarce doar pe acelea. Astfel anunturile PROMOVATE din alta localitate (ex. un anunt
    Pipera afisat pe cautarea Breaza) nu mai intra in setul de comparabile.
    `strict` — daca prefer e dat dar NICIUN anunt nu-l contine: cu strict=False intoarce toate
    (mai bine ceva decat nimic — ex. pe pagina localitatii, unde toate-s din localitate); cu
    strict=True intoarce [] (ex. pe pagina de JUDET, ca sa nu aducem anunturi din alte localitati).
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
        if strict:               # pagina de judet (localitatea a dat 404) fara anunturi din
            return []            # localitate -> [] (NU tot judetul), ca sa nu aducem alte localitati
    return urls


def cauta_anunturi(
    portal: str, judet: str, localitate: str,
    fetcher: Callable[[str], str] = fetch_html, categorie: str = "casa",
) -> list[str]:
    """Descarca pagina de cautare si intoarce URL-urile anunturilor. Fetcher injectabil.

    Cu localitate: incearca pagina localitatii; la 404/goala cade pe pagina judetului DAR
    filtreaza STRICT pe localitate (NU aduce tot judetul — cerinta Adi: doar localitatea aleasa;
    localitatile vecine se adauga EXPLICIT, vezi orchestrator.descopera). Fara localitate: judet.
    """
    incercari = [localitate, ""] if localitate else [""]
    for loc in incercari:
        try:
            html = fetcher(build_search_url(portal, judet, loc, categorie))
        except Exception as e:
            log.debug("Cautare esuata (portal=%s, judet=%s, loc=%r): %s", portal, judet, loc, e)
            continue
        # Filtram MEREU pe localitatea ceruta (si pe pagina de judet din fallback); pe fallback-ul
        # de judet (loc="") cerem STRICT -> [] daca niciun anunt nu e in localitate (fara leak).
        urls = extract_listing_urls(html, baza=BAZE[portal], prefer=localitate,
                                    strict=bool(localitate) and loc == "")
        if urls:
            return urls
    return []


def cauta_anunturi_multi(
    portal: str, judet: str, localitati: str,
    fetcher: Callable[[str], str] = fetch_html, categorie: str = "casa",
) -> list[str]:
    """Cauta pe MAI MULTE localitati (separate prin virgula) si combina rezultatele, dedup.

    Asa userul adauga localitatile vecine pe care le vrea (cerinta Adi), fara geocoding:
    fiecare localitate e cautata STRICT (cauta_anunturi nu aduce tot judetul), apoi se reunesc
    in ordine. Sir gol / o singura localitate -> comportament identic cu cauta_anunturi.
    """
    parti = [p.strip() for p in (localitati or "").split(",") if p.strip()]
    if len(parti) <= 1:
        return cauta_anunturi(portal, judet, parti[0] if parti else "",
                              fetcher=fetcher, categorie=categorie)
    vazute: list[str] = []
    for loc in parti:
        for u in cauta_anunturi(portal, judet, loc, fetcher=fetcher, categorie=categorie):
            if u not in vazute:
                vazute.append(u)
    return vazute
