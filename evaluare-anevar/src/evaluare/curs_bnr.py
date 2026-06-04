"""Cursul de schimb BNR (feed public XML, fara autentificare).

Cursurile BNR sunt exprimate ca RON per 1 unitate de valuta (ex. EUR 5.2592 = 1 EUR = 5.2592 RON).
Pentru unele valute exista un multiplicator (ex. HUF: per 100). Pentru EUR multiplicatorul este 1.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from decimal import Decimal

BNR_URL = "https://www.bnr.ro/nbrfxrates.xml"


def _fetch(url: str) -> str:
    import requests  # import local: nu e necesar in teste cu fetcher injectat

    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()
    return resp.text


def curs_bnr(moneda: str = "EUR", fetcher: Callable[[str], str] | None = None) -> dict | None:
    """Returneaza {moneda, curs (Decimal, RON/unitate), data} sau None daca nu se gaseste."""
    text = (fetcher or _fetch)(BNR_URL)
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
