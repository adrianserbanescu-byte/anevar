"""Store SEPARAT pentru drafturile RTS/RTN si dosarele AML (tipping-off, Legea art. 38).

Datele AML — in special rapoartele de tranzactii suspecte — NU se pastreaza in dosarul de
evaluare/client. Acest store scrie intr-un director dedicat, separat de baza de date a evaluarilor,
cu retentie 5 ani (Legea art. 21). Append-only, fisiere JSON per inregistrare.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

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
        # 0o700 (owner-only) — directorul cu RTS/RTN (tipping-off) nu trebuie listabil de alti
        # utilizatori; fisierele individuale sunt deja 0o600. Pe Windows modul e ignorat (no-op).
        self.dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    def _next_id(self, prefix: str) -> int:
        """Estimare a urmatorului id (len+1). DOAR un punct de plecare — alocarea reala e atomica
        in `salveaza` (O_EXCL). Singur, len+1 e racy: doi scriitori concurenti vad acelasi count."""
        existente = list(self.dir.glob(f"{prefix}_*.json"))
        return len(existente) + 1

    def salveaza(self, tip: str, continut: dict, data: str) -> dict:
        """Salveaza o inregistrare (tip: rts|rtn|dosar) cu data de retentie calculata.

        Alocare ATOMICA a id-ului (F-4, hardening concurenta): `os.O_CREAT|os.O_EXCL` garanteaza ca
        un singur scriitor castiga un nume de fisier dat — doi scriitori concurenti care pornesc de la
        acelasi `idx` nu se mai SUPRASCRIU (vechiul `len(glob)+1` -> acelasi nume -> RTS pierdut). La
        coliziune, incrementam `idx` si reincercam pana prindem un slot liber. Pastreaza id-ul secvential
        (+ compatibilitatea cu `citeste(tip, idx)`), spre deosebire de un nume pe uuid.
        """
        idx = self._next_id(tip)
        while True:
            cale = self.dir / f"{tip}_{idx:04d}.json"
            try:
                fd = os.open(cale, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                break
            except FileExistsError:                # alt scriitor a luat acest idx -> urmatorul
                idx += 1
        inreg = {
            "id": idx,
            "tip": tip,
            "data": data,
            "data_retentie": _adauga_ani(data, RETENTIE_ANI),
            "continut": continut,
        }
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(inreg, f, ensure_ascii=False, indent=2)
        return inreg

    def listeaza(self, tip: str | None = None) -> list[dict]:
        prefix = tip or "*"
        fisiere = sorted(self.dir.glob(f"{prefix}_*.json"))
        return [json.loads(f.read_text(encoding="utf-8")) for f in fisiere]

    def citeste(self, tip: str, idx: int) -> dict:
        cale = self.dir / f"{tip}_{idx:04d}.json"
        if not cale.exists():
            raise KeyError(f"{tip} #{idx} inexistent.")
        return json.loads(cale.read_text(encoding="utf-8"))
