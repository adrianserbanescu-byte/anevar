"""Persistență locală a ponderilor editate de evaluator (override peste `ponderi.py`).

Override-ul e un json simplu (`ponderi_override.json`) lângă directorul `date/`. Dacă lipsește,
ponderile efective = cele din `ponderi.py` (default). Așa, calibrarea lui Adi (D1) e doar date,
nu cod, și se schimbă din UI (D1 al lui C) prin endpointul `/api/descopera/config-ponderi`.
"""
from __future__ import annotations

import json
import math
import os
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


def _curata(override: dict) -> dict[str, dict[str, float]]:
    """Păstrează doar categorii=dict cu valori numerice FINITE (curăță și fișiere hand-edited)."""
    curat: dict[str, dict[str, float]] = {}
    for cat, ponderi in override.items():
        if not isinstance(ponderi, dict):
            continue
        vals = {a: v for a, v in ponderi.items()
                if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)}
        if vals:
            curat[cat] = vals
    return curat


def salveaza_override(date_dir: Path | str, override: dict) -> dict:
    """Fuzionează `override` peste cel existent (editare parțială pe categorie) și-l scrie ATOMIC.
    Întoarce override-ul stocat (cumulat, curățat). Robust la stare coruptă pe disc: o categorie
    non-dict existentă e înlocuită, nu provoacă AttributeError. Validarea valorilor = în endpoint.
    """
    existent = incarca_override(date_dir)
    for cat, ponderi in override.items():
        if not isinstance(ponderi, dict):
            continue
        dst = existent.get(cat)
        if not isinstance(dst, dict):          # categorie coruptă (hand-edit/legacy) -> reinițializează
            dst = {}
            existent[cat] = dst
        dst.update(ponderi)
    curat = _curata(existent)                  # nu persista NaN/Inf/non-dict
    cale = cale_override(date_dir)
    cale.parent.mkdir(parents=True, exist_ok=True)
    tmp = cale.with_name(cale.name + ".tmp")   # scriere atomică: scrie temp + os.replace
    tmp.write_text(json.dumps(curat, ensure_ascii=False, indent=2, allow_nan=False),
                   encoding="utf-8")
    os.replace(tmp, cale)
    return curat
