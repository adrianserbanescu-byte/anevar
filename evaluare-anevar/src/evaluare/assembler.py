"""Orchestrarea motoarelor: din datele de intrare -> ReportContext complet."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.models.report_context import ReportContext
from evaluare.ai.narrative import generate_narrative, NarrativeClient
from evaluare.report.anonymizer import build_anonymizer
from evaluare.engine.cost import evaluate_cost
from evaluare.engine.market import evaluate_market
from evaluare.engine.reconciliation import reconcile
from evaluare.engine.validation import (
    Issue, valideaza_proprietate, valideaza_comparabile, valideaza_depreciere,
)


class EvaluationInput(BaseModel):
    """Datele de intrare ale unei evaluari (corpul cererii web)."""

    meta: EvaluationMeta
    land: LandData
    building: BuildingData
    comparables: list[Comparable] = Field(default_factory=list)
    land_comparables: list[LandComparable] = Field(default_factory=list)
    valoare_teren: Optional[Decimal] = None
    metoda: Literal["piata", "cost", "ponderata"] = "cost"
    pondere_piata: Decimal = Decimal("0.5")


def valideaza(inp: EvaluationInput) -> list[Issue]:
    """Ruleaza validarile SEV relevante pentru metoda aleasa.

    - proprietate (suprafete, Au<=Acd) si depreciere: mereu;
    - comparabile (min 3, outlier, limita ajustare): doar la metodele care folosesc piata.
    """
    issues: list[Issue] = []
    issues += valideaza_proprietate(inp.land, inp.building)
    issues += valideaza_depreciere(inp.building)
    if inp.metoda in ("piata", "ponderata"):
        issues += valideaza_comparabile(inp.comparables)
    return issues


def construieste_context(
    inp: EvaluationInput, client: Optional[NarrativeClient]
) -> ReportContext:
    """Ruleaza motoarele si asambleaza ReportContext (inclusiv narativul)."""
    cost_result = None
    if inp.building.elements:
        cost_result = evaluate_cost(inp.building, valoare_teren=inp.valoare_teren)

    market_result = None
    if inp.comparables:
        market_result = evaluate_market(inp.comparables, suprafata_subiect=inp.building.acd)

    reconciled = reconcile(
        market=market_result, cost=cost_result,
        metoda=inp.metoda, pondere_piata=inp.pondere_piata,
    )

    ctx = ReportContext(
        meta=inp.meta, land=inp.land, building=inp.building,
        comparables=inp.comparables, land_comparables=inp.land_comparables,
        cost_result=cost_result, market_result=market_result, reconciled=reconciled,
    )

    anonymizer = build_anonymizer(inp.meta)
    ctx.narrative = generate_narrative(ctx, client=client, anonymizer=anonymizer)
    return ctx
