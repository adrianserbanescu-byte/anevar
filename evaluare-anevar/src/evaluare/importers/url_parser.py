"""Import comparabile dintr-un anunt online (scraping direct).

AVERTISMENT: scraping-ul direct poate incalca Termenii si Conditiile site-urilor
si se poate strica la schimbari de layout. Folosit pe raspunderea evaluatorului.
Parserul prefera datele structurate schema.org (stabile) si degradeaza gratios.
"""
from __future__ import annotations

import json
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


def parse_listing_html(html: str, sursa_url: str = "") -> ParsedListing:
    """Extrage pret, moneda si suprafata din HTML-ul unui anunt."""
    soup = BeautifulSoup(html, "html.parser")
    pret: Optional[Decimal] = None
    moneda: Optional[str] = None
    suprafata: Optional[Decimal] = None

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

    titlu = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        titlu = title_tag.string.strip()

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
