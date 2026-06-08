"""Persistență locală a configului de metodologie editat de evaluator (override peste default-uri).

Override = json simplu (`metodologie_override.json`) lângă `date/`. Absent → default (`IMPLICIT`).
Mirror al `discovery/ponderi_store.py`: scriere atomică, robust la fișier corupt (degradează la default).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from evaluare.engine.metodologie import MetodologieConfig, ca_dict, din_override
from evaluare.logging_setup import get_logger

log = get_logger(__name__)

NUME_FISIER = "metodologie_override.json"


def cale_override(date_dir: Path | str) -> Path:
    return Path(date_dir) / NUME_FISIER


def incarca_override(date_dir: Path | str) -> dict:
    cale = cale_override(date_dir)
    if not cale.exists():
        return {}
    try:
        date = json.loads(cale.read_text(encoding="utf-8"))
        return date if isinstance(date, dict) else {}
    except (ValueError, OSError) as e:
        log.warning("Override metodologie ilizibil (%s): %s — folosesc default", cale, e)
        return {}


def config_efectiv(date_dir: Path | str) -> MetodologieConfig:
    """Configul efectiv = default (IMPLICIT) cu override-ul evaluatorului aplicat peste."""
    return din_override(incarca_override(date_dir))


def salveaza_override(date_dir: Path | str, override: dict) -> dict:
    """Validează override-ul (prin din_override → ca_dict, doar câmpuri/tipuri cunoscute) și-l scrie
    ATOMIC. Întoarce configul efectiv serializat (dict). Un câmp invalid e ignorat (cade pe default)."""
    cfg = din_override(override)            # validează + normalizează (ignoră chei/tipuri necunoscute)
    serializat = ca_dict(cfg)
    cale = cale_override(date_dir)
    cale.parent.mkdir(parents=True, exist_ok=True)
    tmp = cale.with_name(cale.name + ".tmp")
    tmp.write_text(json.dumps(serializat, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, cale)
    return serializat
