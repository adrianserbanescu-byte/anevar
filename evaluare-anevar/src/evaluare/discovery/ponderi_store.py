"""Persistență locală a ponderilor editate de evaluator (override peste `ponderi.py`).

Override-ul e un json simplu (`ponderi_override.json`) lângă directorul `date/`. Dacă lipsește,
ponderile efective = cele din `ponderi.py` (default). Așa, calibrarea lui Adi (D1) e doar date,
nu cod, și se schimbă din UI (D1 al lui C) prin endpointul `/api/descopera/config-ponderi`.
"""
from __future__ import annotations

import json
from pathlib import Path

from evaluare.discovery.ponderi import fuzioneaza_override
from evaluare.logging_setup import get_logger

log = get_logger(__name__)

NUME_FISIER = "ponderi_override.json"


def cale_override(date_dir: Path | str) -> Path:
    return Path(date_dir) / NUME_FISIER


def incarca_override(date_dir: Path | str) -> dict:
    """Override-ul brut salvat (sau {} dacă lipsește / e corupt — nu crăpăm, cădem pe default)."""
    cale = cale_override(date_dir)
    if not cale.exists():
        return {}
    try:
        date = json.loads(cale.read_text(encoding="utf-8"))
        return date if isinstance(date, dict) else {}
    except (ValueError, OSError) as e:
        log.warning("Override ponderi ilizibil (%s): %s — folosesc default", cale, e)
        return {}


def ponderi_efective(date_dir: Path | str) -> dict[str, dict[str, float]]:
    """Ponderile per categorie = default (ponderi.py) cu override-ul aplicat peste."""
    return fuzioneaza_override(incarca_override(date_dir))


def salveaza_override(date_dir: Path | str, override: dict) -> dict:
    """Fuzionează `override` peste cel existent (editare parțială pe categorie) și-l scrie. Întoarce
    override-ul stocat (cumulat). Validarea valorilor se face în endpoint, înainte de a ajunge aici.
    """
    existent = incarca_override(date_dir)
    for cat, ponderi in override.items():
        if isinstance(ponderi, dict):
            existent.setdefault(cat, {}).update(ponderi)
    cale = cale_override(date_dir)
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(json.dumps(existent, ensure_ascii=False, indent=2), encoding="utf-8")
    return existent
