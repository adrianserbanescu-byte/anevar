"""Store SEPARAT pentru drafturile RTS/RTN si dosarele AML (tipping-off, Legea art. 38).

Datele AML — in special rapoartele de tranzactii suspecte — NU se pastreaza in dosarul de
evaluare/client. Acest store scrie intr-un director dedicat, separat de baza de date a evaluarilor,
cu retentie 5 ani (Legea art. 21). Append-only, fisiere JSON per inregistrare.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from evaluare.aml.constante import RETENTIE_ANI


def _adauga_ani(data_iso: str, ani: int) -> str:
    from datetime import date
    d = date.fromisoformat(data_iso)
    try:
        return d.replace(year=d.year + ani).isoformat()
    except ValueError:  # 29 feb
        return d.replace(year=d.year + ani, day=28).isoformat()


class StoreAML:
    """Persistenta locala, separata de dosarul de evaluare. Un fisier JSON per inregistrare."""

    def __init__(self, dir_baza: Path | str):
        self.dir = Path(dir_baza)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _next_id(self, prefix: str) -> int:
        existente = list(self.dir.glob(f"{prefix}_*.json"))
        return len(existente) + 1

    def salveaza(self, tip: str, continut: dict, data: str) -> dict:
        """Salveaza o inregistrare (tip: rts|rtn|dosar) cu data de retentie calculata."""
        idx = self._next_id(tip)
        inreg = {
            "id": idx,
            "tip": tip,
            "data": data,
            "data_retentie": _adauga_ani(data, RETENTIE_ANI),
            "continut": continut,
        }
        cale = self.dir / f"{tip}_{idx:04d}.json"
        cale.write_text(json.dumps(inreg, ensure_ascii=False, indent=2), encoding="utf-8")
        return inreg

    def listeaza(self, tip: Optional[str] = None) -> list[dict]:
        prefix = tip or "*"
        fisiere = sorted(self.dir.glob(f"{prefix}_*.json"))
        return [json.loads(f.read_text(encoding="utf-8")) for f in fisiere]

    def citeste(self, tip: str, idx: int) -> dict:
        cale = self.dir / f"{tip}_{idx:04d}.json"
        if not cale.exists():
            raise KeyError(f"{tip} #{idx} inexistent.")
        return json.loads(cale.read_text(encoding="utf-8"))
