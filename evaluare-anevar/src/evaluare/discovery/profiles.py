"""Modele pentru descoperirea comparabilelor: profiluri si breakdown de scor."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class SubjectProfile(BaseModel):
    """Atributele primare ale casei evaluate (normalizate pentru scoring)."""

    an: Optional[int] = None                # an constructie
    stare: Optional[int] = None             # treapta 1-5 (1=degradata .. 5=noua)
    finisaj: Optional[int] = None           # treapta 1-4 (1=modest .. 4=lux)
    incalzire: Optional[str] = None         # categorie normalizata (ex. "centrala_gaz")
    teren: Optional[Decimal] = None         # mp


class CandidateProfile(BaseModel):
    """Atributele primare extrase pentru un candidat + textul brut gasit (dovada)."""

    an: Optional[int] = None
    stare: Optional[int] = None
    finisaj: Optional[int] = None
    incalzire: Optional[str] = None
    teren: Optional[Decimal] = None
    texte: dict[str, str] = Field(default_factory=dict)   # ex {"an": "2008"}


class AttributeBreakdown(BaseModel):
    """Detalierea unui atribut in scor (pentru afisare auditabila)."""

    nume: str
    valoare_subiect: Optional[str] = None
    valoare_candidat: Optional[str] = None      # textul brut gasit in anunt
    d: Optional[float] = None                   # dissimilaritate [0,1]; None daca necunoscut
    pondere: int = 0
    contributie: Optional[float] = None         # pondere * d; None daca necunoscut
    cunoscut: bool = True


class ScoreBreakdown(BaseModel):
    """Rezultatul complet al scorarii unui candidat."""

    relevanta: int                              # 0-100
    dissimilaritate: float
    atribute: list[AttributeBreakdown]
    atribute_cunoscute: int
    incredere_scazuta: bool
    explicatie: str                             # formula exacta cu numere (auto-continuta)
