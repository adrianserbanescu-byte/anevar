"""Geocoding OFFLINE + distanta geografica (haversine).

Tabelul de coordonate e BUNDLE-uit (data/coordonate_localitati.json, generat la build-time din
GeoNames de scripts/genereaza_coordonate.py) — la runtime app-ul ramane offline, zero retea.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).parent / "data" / "coordonate_localitati.json"


def _slug(text: str) -> str:  # identic cu discovery.portal_search._slug (consistenta slug-urilor)
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = text.strip().lower()
    return re.sub(r"\s+", "-", text)


@lru_cache(maxsize=1)
def _tabel() -> dict:
    return json.loads(_DATA.read_text(encoding="utf-8"))


def coordonate(judet: str, localitate: str) -> tuple[float, float] | None:
    """(lat, lng) pentru o localitate (nume sau slug), sau None daca nu e in tabel."""
    hit = _tabel().get(_slug(judet), {}).get(_slug(localitate))
    return (hit[0], hit[1]) if hit else None


def distanta_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distanta haversine in km (raza medie a Pamantului, 6371 km)."""
    f1, f2 = math.radians(lat1), math.radians(lat2)
    df = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def localitate_din_url(url: str, judet: str) -> str | None:
    """Slug-ul localitatii detectat in URL-ul anuntului (ex. /oferta/casa-breaza-12 -> breaza).

    Cauta slug-urile localitatilor judetului ca SEGMENT delimitat de '-' sau '/' in URL si prefera
    cel mai LUNG match (abrud-sat castiga in fata lui abrud). None daca nimic nu se potriveste —
    apelantul cade pe localitatea cautata.
    """
    u = (url or "").lower()
    best: str | None = None
    for slug in _tabel().get(_slug(judet), {}):
        if best is not None and len(slug) <= len(best):
            continue
        if re.search(rf"(?:^|[-/]){re.escape(slug)}(?:[-/.]|$)", u):
            best = slug
    return best
