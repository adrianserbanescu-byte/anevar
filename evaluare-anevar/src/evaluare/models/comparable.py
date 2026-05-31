"""Modele pentru comparabile si grila de ajustari."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

AdjustmentType = Literal["procentuala", "valorica"]


class Adjustment(BaseModel):
    """O corectie aplicata unui comparabil pentru un element de comparatie.

    Pentru `procentuala`, `valoare` e o fractie (0.05 = +5%, -0.03 = -3%).
    Pentru `valorica`, `valoare` e o suma in lei (adunata la pretul curent).
    """

    element: str
    tip: AdjustmentType
    valoare: Decimal
    justificare: str = ""


class Comparable(BaseModel):
    """Un comparabil de piata (proprietate intreaga)."""

    sursa: str = "manual"               # "manual" sau URL
    pret: Decimal
    suprafata: Decimal                  # mp (numitorul pentru pretul unitar)
    tip_oferta: Literal["oferta", "tranzactie"] = "oferta"
    data_oferta: Optional[str] = None
    adjustments: list[Adjustment] = Field(default_factory=list)


class LandComparable(BaseModel):
    """Un comparabil de teren."""

    pret_mp: Decimal
    suprafata: Decimal
    localizare: Optional[str] = None
    data: Optional[str] = None
    adjustments: list[Adjustment] = Field(default_factory=list)
