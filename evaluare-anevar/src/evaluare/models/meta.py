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
    tip_drept: str = "drept de proprietate deplină"   # dreptul evaluat (SEV 230 §40.1)
    act_proprietate: str | None = None                 # titlul (ex. contract vânzare nr/dată) — GEV 630 §16
    sarcini: str | None = None                         # ipoteci/servituți din CF (SEV 230 §140; critic la garantare)
    scop: str = "Garantarea creditului ipotecar"
    tip_valoare: str = "Valoarea de piață (SEV 102)"
    data_evaluarii: str                 # ISO sau text, ex. "2026-01-16"
    data_raportului: str
    data_inspectiei: str | None = None
    inspectie_amploare: str | None = None     # interior+exterior / doar exterior / limitată (GEV 630 §24)
    inspectie_insotitor: str | None = None    # cine a însoțit la inspecție (§44)
    inspectie_observatii: str | None = None   # neconcordanțe scriptic↔faptic / limitări (§111.a.3)
    valabilitate: str | None = None
    evaluator_nume: str
    evaluator_legitimatie: str
    moneda: str = "LEI"
    curs_valutar: Decimal | None = None   # EUR -> LEI la data evaluarii
