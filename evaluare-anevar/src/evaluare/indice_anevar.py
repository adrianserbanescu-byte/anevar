"""Indicele imobiliar ANEVAR — variatiile trimestriale % ale valorii de piata/mp, pe orase.

Date publice (pagina e randata cu Google Charts; valorile sunt in JS-ul paginii, in
`arrayToDataTable`). Utile pentru ajustarea „conditiile pietei (timp)" intre data evaluarii si
data unei comparabile. Fetcher injectabil pentru testare offline.

OFFLINE-FIRST: cand pagina live nu e disponibila (fara retea, 403, layout schimbat), modulul
cade pe un tabel offline (`INDICE_OFFLINE`) extras dintr-un raport rezidential publicat, astfel
incat motorul de ajustare „timp" sa functioneze si fara internet. Tabelul e o ANCORA istorica,
nu inlocuieste datele live; vezi `SURSA_OFFLINE`.

PERF (PERF-3): indicele se publica trimestrial, dar `indice_anevar` descarca + parsa pagina live
la fiecare apel. Cacheam rezultatul parsat al caii de retea reale (fetcher implicit `fetch_html`)
cu un TTL de cateva ore (`_TTL_INDICE_SEC`), masurat cu `time.monotonic` (ceas monoton, fara sa
strice determinismul testelor). Cand se injecteaza un alt `fetcher` (teste / date proaspete) se
ocoleste cache-ul. Fallback-ul offline NU se cacheaza (ca un eveniment de retea ulterior sa poata
reveni la datele live).
"""
from __future__ import annotations

import json
import re
import time
from collections.abc import Callable

from bs4 import BeautifulSoup

from evaluare.importers.url_parser import fetch_html

INDICE_URL = ("https://www.anevar.ro/p/informatii-din-piata/informatii-statistice-anevar/"
              "indicele-imobiliar-anevar")

# TTL: indicele e trimestrial -> cateva ore sunt amplu suficiente; pastram rezultatul parsat al
# caii de retea reale. {url: (monotonic_expira, rezultat_parsat)}
_TTL_INDICE_SEC = 6 * 60 * 60
_CACHE_INDICE: dict[str, tuple[float, dict]] = {}


def _goleste_cache() -> None:
    """Goleste cache-ul indicelui live (pentru izolarea testelor)."""
    _CACHE_INDICE.clear()

# --- Fallback offline ---------------------------------------------------------------------------
# Sursa: raport „Piața imobiliară rezidențială – Trimestrul II 2021" (Analize Imobiliare /
# Imobiliare.ro, partener oficial ANEVAR pentru datele din piață — vezi pagina „Date din piață"
# de pe anevar.ro). Sectiunea „Situația în marile orașe - apartamente de vânzare" (p. 11).
# Valorile sunt variatii procentuale ale pretului mediu/mp util al apartamentelor, pe cele 11
# mari orase (>200.000 locuitori) monitorizate:
#   - „Q1-Q2/2021" = evolutia trimestriala (T2 2021 vs T1 2021), in %;
#   - „Q2-2020 → Q2-2021" = evolutia anuala (ultimele 12 luni), in %.
# Pastram aceeasi forma cu cea parsata din pagina live: {"orase": [...], "perioade": [...]}.
SURSA_OFFLINE = (
    "Analize Imobiliare / Imobiliare.ro — „Piața imobiliară rezidențială, Trimestrul II 2021”, "
    "secțiunea „Situația în marile orașe – apartamente de vânzare” (preț mediu/mp util)."
)

# orase in ordinea din raport (clasamentul pretului mediu/mp, T2 2021)
_ORASE_OFFLINE = [
    "Cluj-Napoca", "Bucuresti", "Constanta", "Brasov", "Timisoara",
    "Craiova", "Iasi", "Oradea", "Galati", "Ploiesti", "Braila",
]

# evolutia trimestriala (T2 2021 vs T1 2021), % — raport p. 11 (prozã + grafic)
_TRIM_2021_T2 = {
    "Craiova": 4.8, "Brasov": 4.7, "Bucuresti": 4.0, "Constanta": 3.3,
    "Cluj-Napoca": 2.2, "Iasi": 1.9, "Timisoara": 1.6, "Ploiesti": 1.5,
    "Braila": 1.5, "Oradea": 1.4, "Galati": 1.2,
}

# evolutia anuala (T2 2021 vs T2 2020), % — raport p. 11 (prozã + grafic)
_ANUAL_2021_T2 = {
    "Brasov": 10.1, "Craiova": 9.0, "Galati": 6.5, "Constanta": 6.4,
    "Bucuresti": 5.7, "Cluj-Napoca": 5.2, "Ploiesti": 5.2, "Oradea": 5.0,
    "Iasi": 4.9, "Braila": 4.5, "Timisoara": 2.8,
}


def _tabel_offline() -> dict:
    """Construieste fallback-ul offline in aceeasi forma ca `_parse` (orase + perioade)."""
    return {
        "orase": list(_ORASE_OFFLINE),
        "perioade": [
            {"perioada": "Q1-Q2/2021",
             "valori": {o: _TRIM_2021_T2[o] for o in _ORASE_OFFLINE}},
            {"perioada": "Q2-2020 → Q2-2021",
             "valori": {o: _ANUAL_2021_T2[o] for o in _ORASE_OFFLINE}},
        ],
        "offline": True,
        "sursa": SURSA_OFFLINE,
    }


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
    """Returneaza indicele imobiliar ANEVAR (orase + variatii trimestriale %).

    Offline-first: incearca pagina live (prin `fetcher` injectat sau `fetch_html`); daca
    descarcarea esueaza (fara retea / 403 / eroare) SAU pagina nu mai contine tabelul asteptat
    (rezultat gol), cade pe `_tabel_offline()` ca fallback. Backward-compatible: cand pagina live
    intoarce date valide, comportamentul ramane neschimbat.

    PERF-3: rezultatul caii de retea reale (fetcher implicit `fetch_html`) e cacheat cu TTL
    (`_TTL_INDICE_SEC`). Un `fetcher` injectat (teste / date proaspete) ocoleste cache-ul.
    """
    # Cache DOAR pe calea de retea reala; un fetcher injectat (teste) ocoleste cache-ul.
    cacheabil = fetcher is None or fetcher is fetch_html
    if cacheabil:
        intrare = _CACHE_INDICE.get(INDICE_URL)
        if intrare is not None and intrare[0] > time.monotonic():
            return intrare[1]
    try:
        html = (fetcher or fetch_html)(INDICE_URL)
        rezultat = _parse(html)
    except Exception:
        # retea indisponibila / 403 / orice eroare de fetch -> fallback offline, nu propaga.
        return _tabel_offline()
    if not rezultat.get("perioade"):
        # pagina a raspuns, dar fara tabelul Google Charts asteptat -> fallback offline.
        # NU cacheam fallback-ul: lasam un fetch ulterior sa revina la datele live.
        return _tabel_offline()
    if cacheabil:
        _CACHE_INDICE[INDICE_URL] = (time.monotonic() + _TTL_INDICE_SEC, rezultat)
    return rezultat
