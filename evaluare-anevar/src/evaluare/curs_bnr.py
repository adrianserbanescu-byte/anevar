"""Cursul de schimb BNR (feed public XML, fara autentificare).

Cursurile BNR sunt exprimate ca RON per 1 unitate de valuta (ex. EUR 5.2592 = 1 EUR = 5.2592 RON).
Pentru unele valute exista un multiplicator (ex. HUF: per 100). Pentru EUR multiplicatorul este 1.

PERF (PERF-3): cursul BNR se publica o data pe zi lucratoare, dar `curs_bnr` lovea reteaua la
fiecare apel. Cacheam textul XML descarcat de feed-ul live (cheie unica, intregul feed contine
toate valutele) cu un TTL de o zi (`_TTL_CURS_SEC`), masurat cu `time.monotonic` (ceas monoton,
nu afectat de schimbari de ceas de sistem si fara sa strice determinismul testelor). Cache-ul se
aplica DOAR caii de retea reale (fetcher implicit); cand se injecteaza un `fetcher` (teste sau
caller care vrea date proaspete) se ocoleste complet. Fallback-ul offline ramane neschimbat.
"""
from __future__ import annotations

import re
import time
from collections.abc import Callable
from decimal import Decimal

BNR_URL = "https://www.bnr.ro/nbrfxrates.xml"

# TTL: cursul e zilnic -> ~1 zi. Pastram feed-ul live (text XML) in cache, nu rezultatul parsat,
# ca sa servim orice valuta din acelasi feed fara a re-lovi reteaua.
_TTL_CURS_SEC = 24 * 60 * 60

# {url: (monotonic_expira, text_xml)}
_CACHE_FEED: dict[str, tuple[float, str]] = {}


def _fetch(url: str) -> str:
    import requests  # import local: nu e necesar in teste cu fetcher injectat

    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()
    return resp.text


def _goleste_cache() -> None:
    """Goleste cache-ul feed-ului BNR (pentru izolarea testelor)."""
    _CACHE_FEED.clear()


def _fetch_cacheat(url: str) -> str:
    """Descarca feed-ul live prin `_fetch`, cu cache TTL (cursul e zilnic)."""
    acum = time.monotonic()
    intrare = _CACHE_FEED.get(url)
    if intrare is not None and intrare[0] > acum:
        return intrare[1]
    text = _fetch(url)
    _CACHE_FEED[url] = (acum + _TTL_CURS_SEC, text)
    return text


def curs_bnr(moneda: str = "EUR", fetcher: Callable[[str], str] | None = None) -> dict | None:
    """Returneaza {moneda, curs (Decimal, RON/unitate), data} sau None daca nu se gaseste.

    Cand `fetcher` nu e injectat, foloseste calea de retea reala cu cache TTL (cursul e zilnic).
    Cand `fetcher` e injectat (teste / date proaspete), se ocoleste cache-ul.
    """
    text = (fetcher or _fetch_cacheat)(BNR_URL)
    m_data = re.search(r'date="([0-9-]+)"', text)
    m_rate = re.search(
        rf'<Rate\s+currency="{re.escape(moneda)}"([^>]*)>([0-9.]+)</Rate>', text
    )
    if not m_rate:
        return None
    atribute, valoare = m_rate.group(1), m_rate.group(2)
    curs = Decimal(valoare)
    m_mult = re.search(r'multiplier="(\d+)"', atribute)
    if m_mult:
        curs = curs / Decimal(m_mult.group(1))   # ex. HUF per 100 -> per 1
    return {"moneda": moneda, "curs": curs, "data": m_data.group(1) if m_data else None}
