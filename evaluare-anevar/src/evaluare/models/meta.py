"""Datele administrative ale lucrarii de evaluare."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class EvaluationMeta(BaseModel):
    """Identificarea lucrarii: client, scop, date, evaluator."""

    client_nume: str
    client_tip: str = "Persoana fizica"
    adresa: str
    numar_cadastral: str
    carte_funciara: str
    scop: str = "Garantarea creditului ipotecar"
    tip_valoare: str = "Valoarea de piata (SEV 104)"
    data_evaluarii: str                 # ISO sau text, ex. "2026-01-16"
    data_raportului: str
    valabilitate: Optional[str] = None
    evaluator_nume: str
    evaluator_legitimatie: str
    moneda: str = "LEI"
