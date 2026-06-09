"""Abordări de evaluare cu ieșire comună (RezultatAbordare), peste motoarele existente."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from evaluare.engine.cost import evaluate_cost
from evaluare.engine.market import evaluate_market
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.models.comparable import Comparable
from evaluare.models.property import BuildingData

NumeAbordare = Literal["cost", "comparatie", "venit"]


class RezultatAbordare(BaseModel):
    """Ieșirea comună a oricărei abordări — folosită la reconciliere pe profil."""

    abordare: NumeAbordare
    valoare: Decimal | None = None
    detalii: dict = Field(default_factory=dict)


def abordare_cost(building: BuildingData, valoare_teren: Decimal | None) -> RezultatAbordare:
    res = evaluate_cost(building, valoare_teren=valoare_teren)
    return RezultatAbordare(
        abordare="cost", valoare=res.valoare_cost,
        detalii={"cin": str(res.cin), "cib": str(res.cib),
                 "depreciere_fizica": str(res.depreciere_fizica)},
    )


def abordare_comparatie(comparables: list[Comparable], suprafata_subiect: Decimal,
                        cfg: MetodologieConfig = IMPLICIT) -> RezultatAbordare:
    res = evaluate_market(comparables, suprafata_subiect=suprafata_subiect, cfg=cfg)
    return RezultatAbordare(
        abordare="comparatie", valoare=res.valoare_piata,
        detalii={"index_selectat": res.index_selectat},
    )
