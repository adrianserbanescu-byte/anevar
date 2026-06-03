"""Rezultate ale descoperirii: extracție LLM și candidat scorat."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

from evaluare.discovery.profiles import CandidateProfile, ScoreBreakdown

StareSecundar = Literal["potrivit", "diferit", "nementionat"]


class SecondaryAttributeResult(BaseModel):
    """Rezultatul unui atribut secundar (FYI) pentru un candidat."""

    nume: str
    stare: StareSecundar
    valoare_gasita: Optional[str] = None


class CandidateExtraction(BaseModel):
    """Ce a extras LLM-ul dintr-un anunț: profil primar + atribute secundare."""

    profile: CandidateProfile
    secundare: list[SecondaryAttributeResult] = Field(default_factory=list)


class CandidateResult(BaseModel):
    """Un candidat complet, scorat și gata de afișat/selectat."""

    url: str
    titlu: str = ""
    pret: Optional[Decimal] = None
    suprafata: Optional[Decimal] = None             # suprafata casei
    teren: Optional[Decimal] = None                 # suprafata terenului
    pret_mp: Optional[Decimal] = None               # €/mp construit - DOAR daca terenul e comparabil
    breakdown: ScoreBreakdown
    secundare: list[SecondaryAttributeResult] = Field(default_factory=list)
