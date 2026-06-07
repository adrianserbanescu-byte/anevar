"""Modele pentru descoperirea comparabilelor: profiluri si breakdown de scor."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class SubjectProfile(BaseModel):
    """Atributele primare ale proprietatii evaluate (normalizate pentru scoring)."""

    suprafata_construita: Decimal | None = None   # mp (suprafata casei, ex. Acd)
    an: int | None = None                # an constructie
    stare: int | None = None             # treapta 1-5 (1=degradata .. 5=noua)
    finisaj: int | None = None           # treapta 1-4 (1=modest .. 4=lux)
    incalzire: str | None = None         # categorie normalizata (ex. "centrala_gaz")
    teren: Decimal | None = None         # mp (suprafata teren)
    nr_camere: int | None = None         # numar de camere (driver major la apartament)
    etaj: int | None = None              # etajul (apartament); 0 = parter. Extractie pending la apartament.


class CandidateProfile(BaseModel):
    """Atributele primare extrase pentru un candidat + textul brut gasit (dovada)."""

    suprafata_construita: Decimal | None = None   # mp (din anunt, via parser)
    an: int | None = None
    stare: int | None = None
    finisaj: int | None = None
    incalzire: str | None = None
    teren: Decimal | None = None
    nr_camere: int | None = None
    etaj: int | None = None
    texte: dict[str, str] = Field(default_factory=dict)   # ex {"an": "2008"}


class AttributeBreakdown(BaseModel):
    """Detalierea unui atribut in scor (pentru afisare auditabila)."""

    nume: str
    valoare_subiect: str | None = None
    valoare_candidat: str | None = None      # textul brut gasit in anunt
    d: float | None = None                   # dissimilaritate [0,1]; None daca necunoscut
    pondere: int = 0
    contributie: float | None = None         # pondere * d; None daca necunoscut
    cunoscut: bool = True


class ScoreBreakdown(BaseModel):
    """Rezultatul complet al scorarii unui candidat."""

    relevanta: int                              # 0-100
    dissimilaritate: float
    atribute: list[AttributeBreakdown]
    atribute_cunoscute: int
    incredere_scazuta: bool
    explicatie: str                             # formula exacta cu numere (auto-continuta)
