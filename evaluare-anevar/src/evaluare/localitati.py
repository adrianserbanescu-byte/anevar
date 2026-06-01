"""Liste judete + localitati (statice) cu slug-uri compatibile portalurilor imobiliare."""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).parent / "data" / "judete_localitati.json"


def slugify(text: str) -> str:
    """lowercase, fara diacritice, secvente non-alfanumerice -> o cratima."""
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_DATA, encoding="utf-8") as f:
        return json.load(f)


def judete() -> list[dict]:
    """Lista celor 42 de judete: [{nume, slug}], ordonate alfabetic."""
    return _load()["judete"]


def localitati(judet_slug: str) -> list[dict]:
    """Localitatile dintr-un judet: [{nume, slug}]. Lista goala daca judetul nu exista."""
    return _load()["localitati"].get(judet_slug, [])
