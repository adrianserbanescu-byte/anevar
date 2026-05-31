"""Abordarea prin cost: CIB segregat, Vcp, depreciere fizica, CIN."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from evaluare.models.property import BuildingData, CostElement, DepreciationPoint
from evaluare.models.results import CostResult


def compute_cib(elements: list[CostElement]) -> Decimal:
    """Cost de inlocuire brut = suma costurilor de nou ale elementelor."""
    return sum((el.cost_nou() for el in elements), Decimal("0"))


def compute_vcp(elements: list[CostElement], an_referinta: int) -> Decimal:
    """Varsta cronologica ponderata = sum(varsta_i * cost_i) / sum(cost_i)."""
    total_cost = compute_cib(elements)
    if total_cost == Decimal("0"):
        return Decimal("0")
    weighted = sum(
        (Decimal(el.varsta(an_referinta)) * el.cost_nou() for el in elements),
        Decimal("0"),
    )
    return weighted / total_cost


def interpolate_depreciation(
    vcp: Decimal, points: list[DepreciationPoint]
) -> Decimal:
    """Depreciere fizica prin interpolare liniara intre punctele tabelului.

    Dfn = D1 + (D2 - D1) / (V2 - V1) * (Vcp - V1)
    Sub/peste limitele tabelului se foloseste primul/ultimul punct (clamp).
    """
    if not points:
        raise ValueError("Tabelul de depreciere este gol.")
    ordered = sorted(points, key=lambda p: p.varsta)
    if vcp <= ordered[0].varsta:
        return ordered[0].depreciere
    if vcp >= ordered[-1].varsta:
        return ordered[-1].depreciere
    for low, high in zip(ordered, ordered[1:]):
        if low.varsta <= vcp <= high.varsta:
            v1, d1 = Decimal(low.varsta), low.depreciere
            v2, d2 = Decimal(high.varsta), high.depreciere
            return d1 + (d2 - d1) / (v2 - v1) * (vcp - v1)
    raise AssertionError("interpolare: caz logic neatins")


def compute_cin(
    cib: Decimal, dfn: Decimal, c_nf: Decimal, c_ex: Decimal
) -> Decimal:
    """Cost de inlocuire net = CIB * (1-Dfn) * (1-C_nf) * (1-C_ex)."""
    one = Decimal("1")
    return cib * (one - dfn) * (one - c_nf) * (one - c_ex)


def evaluate_cost(
    building: BuildingData, valoare_teren: Optional[Decimal] = None
) -> CostResult:
    """Ruleaza abordarea prin cost completa pentru o constructie."""
    cib = compute_cib(building.elements)
    vcp = compute_vcp(building.elements, building.an_referinta)
    vcp = vcp.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    dfn = interpolate_depreciation(vcp, building.depreciation_points)
    cin = compute_cin(
        cib, dfn, building.functional_depreciation, building.external_depreciation
    )
    valoare_cost = None
    if valoare_teren is not None:
        valoare_cost = cin + valoare_teren
    return CostResult(
        valoare_teren=valoare_teren,
        cib=cib,
        vcp=vcp,
        depreciere_fizica=dfn,
        cin=cin,
        valoare_cost=valoare_cost,
    )
