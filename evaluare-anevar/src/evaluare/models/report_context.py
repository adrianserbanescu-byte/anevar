"""Agregatul care leaga toate datele necesare generarii raportului."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.models.results import CostResult, MarketResult, ReconciledResult, LandResult
from evaluare.models.narrative import NarrativeSection
from evaluare.profil import ProfilEvaluare, CASA_TEREN_GARANTARE
from evaluare.engine.venit import DateVenit, RezultatVenit


class ReportContext(BaseModel):
    """Tot ce are nevoie generatorul de raport, intr-un singur obiect."""

    meta: EvaluationMeta
    land: LandData
    building: BuildingData
    comparables: list[Comparable] = Field(default_factory=list)
    land_comparables: list[LandComparable] = Field(default_factory=list)
    cost_result: Optional[CostResult] = None
    market_result: Optional[MarketResult] = None
    reconciled: ReconciledResult
    land_result: Optional[LandResult] = None
    alocare_constructii: Optional[Decimal] = None
    photos: list[str] = Field(default_factory=list)   # data-URL base64 pentru anexa foto
    documente: list[str] = Field(default_factory=list)  # data-URL base64 (scanuri) -> Anexa 3
    narrative: list[NarrativeSection] = Field(default_factory=list)
    profil: ProfilEvaluare = Field(default_factory=lambda: CASA_TEREN_GARANTARE)
    venit_result: Optional[RezultatVenit] = None
    date_venit: Optional[DateVenit] = None
