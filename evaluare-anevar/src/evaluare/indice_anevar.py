"""Indicele imobiliar ANEVAR — variatiile trimestriale % ale valorii de piata/mp, pe orase.

Date publice (pagina e randata cu Google Charts; valorile sunt in JS-ul paginii, in
`arrayToDataTable`). Utile pentru ajustarea „conditiile pietei (timp)" intre data evaluarii si
data unei comparabile. Fetcher injectabil pentru testare offline.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable

from bs4 import BeautifulSoup

from evaluare.importers.url_parser import fetch_html

INDICE_URL = ("https://www.anevar.ro/p/informatii-din-piata/informatii-statistice-anevar/"
              "indicele-imobiliar-anevar")


def _parse(html: str) -> dict:
    """Extrage primul tabel Google Charts (orase) -> {orase: [...], perioade: [...]}"""
    sc = " ".join((s.string or s.get_text() or "")
                  for s in BeautifulSoup(html, "html.parser").find_all("script"))
    m = re.search(r"arrayToDataTable\(\s*(\[.*?\])\s*\)", sc, re.S)
    if not m:
        return {"orase": [], "perioade": []}
    raw = m.group(1).replace("\n", " ").replace("\r", " ")
    raw = re.sub(r"(?<=[\s,\[])\+(\d)", r"\1", raw)   # +2.5 -> 2.5
    raw = re.sub(r",\s*\]", "]", raw)                  # virgule finale
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return {"orase": [], "perioade": []}
    if not data or not isinstance(data[0], list):
        return {"orase": [], "perioade": []}
    orase = [str(x) for x in data[0][1:]]
    perioade = [
        {"perioada": str(row[0]).strip(), "valori": dict(zip(orase, row[1:], strict=False))}
        for row in data[1:] if isinstance(row, list) and len(row) > 1
    ]
    return {"orase": orase, "perioade": perioade}


def indice_anevar(fetcher: Callable[[str], str] | None = None) -> dict:
    """Returneaza indicele imobiliar ANEVAR (orase + variatii trimestriale %)."""
    html = (fetcher or fetch_html)(INDICE_URL)
    return _parse(html)
