"""Import comparabile dintr-un anunt online (scraping direct).

AVERTISMENT: scraping-ul direct poate incalca Termenii si Conditiile site-urilor
si se poate strica la schimbari de layout. Folosit pe raspunderea evaluatorului.
Parserul prefera datele structurate schema.org (stabile) si degradeaza gratios.
"""
from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from evaluare.models.comparable import Comparable

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class ParsedListing(BaseModel):
    """Datele extrase dintr-un anunt (partiale, de confirmat de evaluator)."""

    pret: Optional[Decimal] = None
    moneda: Optional[str] = None
    suprafata: Optional[Decimal] = None         # suprafata casei (construita/utila)
    suprafata_teren: Optional[Decimal] = None   # suprafata terenului, daca e in date structurate
    titlu: str = ""
    sursa_url: str = ""


def _to_decimal(value) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value).replace(" ", "").replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


def _iter_nodes(data):
    """Itereaza recursiv nodurile dintr-un obiect JSON-LD (dict/list/@graph)."""
    if isinstance(data, list):
        for item in data:
            yield from _iter_nodes(item)
    elif isinstance(data, dict):
        yield data
        if "@graph" in data:
            yield from _iter_nodes(data["@graph"])


def _din_nextdata(soup) -> tuple:
    """Cauta pret si suprafata in blobul __NEXT_DATA__ (Next.js).

    Acopera structuri reale: imobiliare (key=="surface") si storia (caracteristica
    cu label=="area" -> suprafata casei; "terrain_area" e terenul, ignorat).
    """
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        return None, None, None, None
    raw = tag.get_text()
    if not raw:
        return None, None, None, None
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return None, None, None, None
    pret = moneda = supr = teren = None
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if "price" in node and isinstance(node["price"], dict):
                pret = pret or _to_decimal(node["price"].get("value"))
                moneda = moneda or node["price"].get("currency")
            # imobiliare: {key: "surface", value: "130"}
            if node.get("key") == "surface":
                supr = supr or _to_decimal(node.get("value"))
            # storia: {label: "area", values: ["220"]} = casa; "terrain_area" = teren
            lbl = node.get("label")
            if lbl == "area" and isinstance(node.get("values"), list) and node["values"]:
                supr = supr or _to_decimal(node["values"][0])
            if lbl == "terrain_area" and isinstance(node.get("values"), list) and node["values"]:
                teren = teren or _to_decimal(node["values"][0])
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return pret, moneda, supr, teren


def _cauta_in_jsonld(data) -> tuple:
    """Cautare recursiva in JSON-LD: pret (maximul = total), moneda, suprafata (floorSize).

    Robust la structuri reale: pretul poate fi sub Offer.priceSpecification.price, iar
    floorSize poate fi scalar (400) sau dict ({value: 400}).
    """
    preturi: list = []
    suprafete: list = []

    def walk(o):
        if isinstance(o, dict):
            if "price" in o:
                p = _to_decimal(o.get("price"))
                if p is not None and p > 0:
                    preturi.append((p, o.get("priceCurrency")))
            if "floorSize" in o:
                fs = o.get("floorSize")
                v = _to_decimal(fs.get("value")) if isinstance(fs, dict) else _to_decimal(fs)
                if v is not None and v > 0:
                    suprafete.append(v)
            for val in o.values():
                walk(val)
        elif isinstance(o, list):
            for val in o:
                walk(val)

    walk(data)
    pret = moneda = supr = None
    if preturi:
        pret, moneda = max(preturi, key=lambda x: x[0])   # totalul, nu pretul/mp
    if suprafete:
        supr = suprafete[0]                                # prima = cladirea (floorSize)
    return pret, moneda, supr


def parse_listing_html(html: str, sursa_url: str = "") -> ParsedListing:
    """Extrage pret, moneda si suprafata; incearca, in ordine: JSON-LD (recursiv),
    __NEXT_DATA__, og:meta + regex pe titlu/descriere."""
    soup = BeautifulSoup(html, "html.parser")
    pret: Optional[Decimal] = None
    moneda: Optional[str] = None
    suprafata: Optional[Decimal] = None
    suprafata_teren: Optional[Decimal] = None

    # 1) JSON-LD (recursiv, robust la nesting real: priceSpecification, floorSize scalar)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.get_text() or "")
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        p, m, s = _cauta_in_jsonld(data)
        pret = pret or p
        moneda = moneda or m
        suprafata = suprafata or s

    # 2) __NEXT_DATA__ (include suprafata terenului - storia)
    p2, m2, s2, t2 = _din_nextdata(soup)
    pret = pret or p2
    moneda = moneda or m2
    suprafata = suprafata or s2
    suprafata_teren = suprafata_teren or t2

    titlu = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        titlu = title_tag.string.strip()

    # 3) og:meta (title + description) + regex, pentru ce a ramas
    text_cautare = titlu
    for prop in ("og:title", "og:description"):
        og = soup.find("meta", property=prop)
        if og and og.get("content"):
            text_cautare += " " + og["content"]
    if suprafata is None:
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*mp", text_cautare, re.IGNORECASE)
        if m:
            suprafata = _to_decimal(m.group(1))
    if pret is None:
        m = re.search(r"(\d[\d.\s]{3,})\s*(eur|euro|€|lei)", text_cautare, re.IGNORECASE)
        if m:
            pret = _to_decimal(m.group(1).replace(".", "").replace(" ", ""))
            moneda = moneda or m.group(2).upper().replace("EURO", "EUR").replace("€", "EUR")

    return ParsedListing(pret=pret, moneda=moneda, suprafata=suprafata,
                         suprafata_teren=suprafata_teren, titlu=titlu, sursa_url=sursa_url)


def to_comparable(parsed: ParsedListing) -> Comparable:
    """Construieste un Comparable dintr-un ParsedListing (cere pret + suprafata)."""
    if parsed.pret is None or parsed.suprafata is None:
        raise ValueError(
            "Anuntul nu contine pret si suprafata; completati manual comparabilul."
        )
    return Comparable(
        sursa=parsed.sursa_url or "url",
        pret=parsed.pret,
        suprafata=parsed.suprafata,
        tip_oferta="oferta",
    )


def fetch_html(url: str) -> str:
    """Descarca HTML-ul unui anunt (live). Nu se foloseste in teste."""
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    return resp.text


def import_from_url(
    url: str, fetcher: Callable[[str], str] = fetch_html
) -> ParsedListing:
    """Descarca si parseaza un anunt. Fetcher injectabil pentru testare offline."""
    html = fetcher(url)
    return parse_listing_html(html, sursa_url=url)
