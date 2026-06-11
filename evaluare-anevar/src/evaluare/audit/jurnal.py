"""Jurnal de audit append-only, inlantuit prin hash (tamper-evident).

Fiecare eveniment include hash-ul evenimentului anterior; alterarea oricarui eveniment rupe lantul.
Ceasul (clock) este injectabil pentru reproducibilitate in teste.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC

from pydantic import BaseModel, Field

GENESIS = "0" * 64


def _acum() -> str:
    # UTC tz-aware (audit): timestamp neambiguu, reproductibil intre masini, imun la fusul local/DST.
    # Lantul ramane verificabil oricum (verifica() re-hashuieste timestamp-ul stocat, nu ceasul curent).
    from datetime import datetime

    return datetime.now(UTC).isoformat(timespec="seconds")


def _hash(index: int, timestamp: str, tip: str, detalii: str, hash_anterior: str) -> str:
    payload = f"{index}|{timestamp}|{tip}|{detalii}|{hash_anterior}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class EvenimentAudit(BaseModel):
    """Un eveniment in jurnal (intrare, sursa externa, calcul, generare raport)."""

    index: int
    timestamp: str
    tip: str
    detalii: str = ""
    hash_anterior: str
    hash: str


class JurnalAudit(BaseModel):
    """Jurnal append-only, inlantuit prin hash. `clock` injectabil pentru teste."""

    evenimente: list[EvenimentAudit] = Field(default_factory=list)

    def inregistreaza(
        self, tip: str, detalii: dict | str | None = None,
        clock: Callable[[], str] = _acum,
    ) -> EvenimentAudit:
        """Adauga un eveniment legat prin hash de cel anterior."""
        det = detalii if isinstance(detalii, str) else json.dumps(
            detalii or {}, sort_keys=True, ensure_ascii=False, default=str
        )
        index = len(self.evenimente)
        anterior = self.evenimente[-1].hash if self.evenimente else GENESIS
        ts = clock()
        ev = EvenimentAudit(
            index=index, timestamp=ts, tip=tip, detalii=det,
            hash_anterior=anterior, hash=_hash(index, ts, tip, det, anterior),
        )
        self.evenimente.append(ev)
        return ev

    def verifica(self) -> bool:
        """True daca lantul e intact (niciun eveniment alterat sau reordonat)."""
        anterior = GENESIS
        for i, ev in enumerate(self.evenimente):
            if ev.index != i or ev.hash_anterior != anterior:
                return False
            if ev.hash != _hash(ev.index, ev.timestamp, ev.tip, ev.detalii, ev.hash_anterior):
                return False
            anterior = ev.hash
        return True
