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
    suprafata: Optional[Decimal] = None
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
    """Cauta pret si suprafata in blobul __NEXT_DATA__ (Next.js)."""
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None, None, None
    try:
        data = json.loads(tag.string)
    except (ValueError, TypeError):
        return None, None, None
    pret = moneda = supr = None
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if "price" in node and isinstance(node["price"], dict):
                pret = pret or _to_decimal(node["price"].get("value"))
                moneda = moneda or node["price"].get("currency")
            if node.get("key") == "surface":
                supr = supr or _to_decimal(node.get("value"))
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return pret, moneda, supr


def parse_listing_html(html: str, sursa_url: str = "") -> ParsedListing:
    """Extrage pret, moneda si suprafata; incearca, in ordine: JSON-LD, __NEXT_DATA__,
    og:meta, regex pe titlu."""
    soup = BeautifulSoup(html, "html.parser")
    pret: Optional[Decimal] = None
    moneda: Optional[str] = None
    suprafata: Optional[Decimal] = None

    # 1) JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for node in _iter_nodes(data):
            offers = node.get("offers")
            if isinstance(offers, dict):
                if pret is None and "price" in offers:
                    pret = _to_decimal(offers.get("price"))
                    moneda = moneda or offers.get("priceCurrency")
            if pret is None and node.get("@type") == "Offer" and "price" in node:
                pret = _to_decimal(node.get("price"))
                moneda = moneda or node.get("priceCurrency")
            floor = node.get("floorSize")
            if suprafata is None and isinstance(floor, dict):
                suprafata = _to_decimal(floor.get("value"))

    # 2) __NEXT_DATA__
    if pret is None or suprafata is None:
        p2, m2, s2 = _din_nextdata(soup)
        pret = pret or p2
        moneda = moneda or m2
        suprafata = suprafata or s2

    titlu = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        titlu = title_tag.string.strip()

    # 3) og:meta + 4) regex pe titlu, pentru ce a ramas
    text_cautare = titlu
    og = soup.find("meta", property="og:title")
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
                         titlu=titlu, sursa_url=sursa_url)


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
