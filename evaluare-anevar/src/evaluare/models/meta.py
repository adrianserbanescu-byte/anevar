"""Datele administrative ale lucrarii de evaluare."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class EvaluationMeta(BaseModel):
    """Identificarea lucrarii: client, scop, date, evaluator."""

    client_nume: str
    client_tip: str = "Persoana fizica"
    beneficiar: str = ""                 # banca finantatoare / utilizator desemnat
    proprietar: str | None = None     # daca difera de client
    adresa: str
    numar_cadastral: str
    carte_funciara: str
    scop: str = "Garantarea creditului ipotecar"
    tip_valoare: str = "Valoarea de piață (SEV 102)"
    data_evaluarii: str                 # ISO sau text, ex. "2026-01-16"
    data_raportului: str
    data_inspectiei: str | None = None
    valabilitate: str | None = None
    evaluator_nume: str
    evaluator_legitimatie: str
    moneda: str = "LEI"
    curs_valutar: Decimal | None = None   # EUR -> LEI la data evaluarii
