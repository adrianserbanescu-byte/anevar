"""Modele pentru comparabile si grila de ajustari."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

AdjustmentType = Literal["procentuala", "valorica"]
AdjustmentStage = Literal["tranzactie", "proprietate"]


class Adjustment(BaseModel):
    """O corectie aplicata unui comparabil pentru un element de comparatie.

    Pentru `procentuala`, `valoare` e o fractie (0.05 = +5%, -0.03 = -3%).
    Pentru `valorica`, `valoare` e o suma in lei (adunata la pretul curent).

    `etapa` separa cele doua etape ale grilei reale (GBF/ANEVAR):
    - `tranzactie`: ajustari de piata (oferta->tranzactie, drept, finantare, conditii
      de vanzare, cheltuieli, conditiile pietei) — aplicate SECVENTIAL (compus);
    - `proprietate`: caracteristici fizice/juridice — aplicate ADITIV pe pretul de baza
      rezultat dupa etapa de tranzactie. Doar acestea conteaza in ajustarea bruta.
    """

    element: str
    tip: AdjustmentType
    valoare: Decimal
    etapa: AdjustmentStage = "proprietate"
    justificare: str = ""


class Comparable(BaseModel):
    """Un comparabil de piata (proprietate intreaga)."""

    sursa: str = "manual"               # "manual" sau URL
    pret: Decimal = Field(gt=0)
    suprafata: Decimal = Field(gt=0)    # mp (numitorul pentru pretul unitar)
    tip_oferta: Literal["oferta", "tranzactie"] = "oferta"
    data_oferta: str | None = None
    adjustments: list[Adjustment] = Field(default_factory=list)


class LandComparable(BaseModel):
    """Un comparabil de teren."""

    # Sursa datelor: "manual" sau URL. Optional (default None) pentru a nu afecta
    # constructiile existente. Folosit la anti-contaminare + ierarhia datelor de
    # intrare SEV 104 / SEV 230 §100.2 (comparabil direct/indirect), simetric cu
    # `Comparable.sursa` (gap B2-N1 / G12 din SEV-2025-gap-implementare).
    sursa: str | None = None
    pret_mp: Decimal = Field(gt=0)
    suprafata: Decimal = Field(gt=0)
    localizare: str | None = None
    data: str | None = None
    adjustments: list[Adjustment] = Field(default_factory=list)


class RentComparable(BaseModel):
    """Un comparabil de inchiriere (chirie lunara pe mp), pentru grila de chirii.

    `chirie_mp` e chiria lunara pe metru patrat (ex. EUR/mp/luna). Ajustarile
    folosesc aceeasi metodologie in doua etape (tranzactie compus + proprietate aditiv)
    ca grila de teren; doar etapa de proprietate conteaza in ajustarea bruta.
    """

    chirie_mp: Decimal = Field(gt=0)
    suprafata: Decimal = Field(gt=0)
    localizare: str | None = None
    data: str | None = None
    adjustments: list[Adjustment] = Field(default_factory=list)
