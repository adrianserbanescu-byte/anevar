"""Cont LOCAL al evaluatorului (versiunea curentă a UI-ului, pre-gateway).

Stochează identitatea evaluatorului + formatul numelui de dosar într-un fișier `cont.json`
lângă datele aplicației. La activarea comercializării (#4), contul vine din gateway-ul online;
aici e varianta locală (un singur evaluator per instalare).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from evaluare.master_config import TEMPLATE_NUME_IMPLICIT


def _fisier_cont() -> Path:
    out = os.environ.get("OUTPUT_DIR") or "date"
    return Path(out) / "cont.json"


def incarca_cont() -> dict | None:
    """Returnează contul local sau None dacă nu există."""
    f = _fisier_cont()
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def salveaza_cont(nume: str, legitimatie: str,
                  format_dosar: list[str] | None = None) -> dict:
    """Creează/actualizează contul local. Returnează contul salvat."""
    cont = {
        "nume": nume.strip(),
        "legitimatie": str(legitimatie).strip(),
        "format_dosar": format_dosar or list(TEMPLATE_NUME_IMPLICIT),
    }
    f = _fisier_cont()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(cont, ensure_ascii=False, indent=2), encoding="utf-8")
    return cont
