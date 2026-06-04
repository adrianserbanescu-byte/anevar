"""Agregatul care leaga toate datele necesare generarii raportului."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from evaluare.engine.venit import DateVenit, RezultatVenit
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.models.meta import EvaluationMeta
from evaluare.models.narrative import NarrativeSection
from evaluare.models.property import BuildingData, LandData
from evaluare.models.results import CostResult, LandResult, MarketResult, ReconciledResult
from evaluare.profil import CASA_TEREN_GARANTARE, ProfilEvaluare


class ReportContext(BaseModel):
    """Tot ce are nevoie generatorul de raport, intr-un singur obiect."""

    meta: EvaluationMeta
    land: LandData
    building: BuildingData
    comparables: list[Comparable] = Field(default_factory=list)
    land_comparables: list[LandComparable] = Field(default_factory=list)
    cost_result: CostResult | None = None
    market_result: MarketResult | None = None
    reconciled: ReconciledResult
    land_result: LandResult | None = None
    alocare_constructii: Decimal | None = None
    photos: list[str] = Field(default_factory=list)   # data-URL base64 pentru anexa foto
    documente: list[str] = Field(default_factory=list)  # data-URL base64 (scanuri) -> Anexa 3
    narrative: list[NarrativeSection] = Field(default_factory=list)
    profil: ProfilEvaluare = Field(default_factory=lambda: CASA_TEREN_GARANTARE)
    venit_result: RezultatVenit | None = None
    date_venit: DateVenit | None = None
    dcf_valoare: Decimal | None = None
