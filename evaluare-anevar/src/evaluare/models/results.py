"""Structuri de iesire pentru motoarele de calcul."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CostResult(BaseModel):
    """Rezultatul abordarii prin cost."""

    valoare_teren: Optional[Decimal] = None
    cib: Decimal                        # cost de inlocuire brut
    vcp: Decimal                        # varsta cronologica ponderata
    depreciere_fizica: Decimal          # fractie (Dfn)
    cin: Decimal                        # cost de inlocuire net
    valoare_cost: Optional[Decimal] = None   # teren + CIN (None daca terenul nu e evaluat)


class MarketResult(BaseModel):
    """Rezultatul abordarii prin piata."""

    preturi_unitare_corectate: list[Decimal] = Field(default_factory=list)
    ajustari_brute: list[Decimal] = Field(default_factory=list)
    ajustari_nete: list[Decimal] = Field(default_factory=list)
    index_selectat: int
    valoare_piata: Decimal


class ReconciledResult(BaseModel):
    """Rezultatul reconcilierii finale."""

    valoare_finala: Decimal
    metoda_selectata: Literal["piata", "cost", "ponderata"]
    valoare_fara_tva: bool = True
    nota: str = ""
