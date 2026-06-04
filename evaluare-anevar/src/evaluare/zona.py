"""Derivarea judet+localitate dintr-o adresa libera (LLM injectabil, fallback)."""
from __future__ import annotations

import json
import re
import unicodedata

from evaluare.ai.narrative import NarrativeClient

SYSTEM_ZONA = (
    "Extragi judetul si localitatea dintr-o adresa din Romania. Raspunzi EXCLUSIV cu JSON "
    "valid: {\"judet\": \"...\", \"localitate\": \"...\"}, cu valori lowercase fara diacritice. "
    "Daca nu poti determina un camp, pune null. Nu inventezi."
)


def _normalizeaza(text: str | None) -> str | None:
    if not text:
        return None
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.strip().lower() or None


def _fallback(adresa: str) -> tuple[str | None, str | None]:
    parti = [p.strip() for p in adresa.split(",") if p.strip()]
    if len(parti) >= 2:
        return _normalizeaza(parti[-1]), _normalizeaza(parti[-2])
    if len(parti) == 1:
        return None, _normalizeaza(parti[0])
    return None, None


def extrage_zona(
    adresa: str, client: NarrativeClient | None
) -> tuple[str | None, str | None]:
    """Intoarce (judet, localitate) din adresa. LLM daca exista client, altfel fallback."""
    if client is not None:
        try:
            raw = client.complete(SYSTEM_ZONA, f"Adresa: {adresa}")
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(m.group(0) if m else raw)
            judet = _normalizeaza(data.get("judet"))
            localitate = _normalizeaza(data.get("localitate"))
            if localitate or judet:
                return judet, localitate
        except (ValueError, TypeError, AttributeError):
            pass
    return _fallback(adresa)
