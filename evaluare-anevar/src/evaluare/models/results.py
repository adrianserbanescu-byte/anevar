"""Structuri de iesire pentru motoarele de calcul."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CostResult(BaseModel):
    """Rezultatul abordarii prin cost."""

    valoare_teren: Decimal | None = None
    cib: Decimal                        # cost de inlocuire brut
    vcp: Decimal                        # varsta cronologica ponderata
    depreciere_fizica: Decimal          # fractie (Dfn)
    cin: Decimal                        # cost de inlocuire net
    valoare_cost: Decimal | None = None   # teren + CIN (None daca terenul nu e evaluat)


class MarketResult(BaseModel):
    """Rezultatul abordarii prin piata."""

    preturi_unitare_corectate: list[Decimal] = Field(default_factory=list)
    ajustari_brute: list[Decimal] = Field(default_factory=list)
    ajustari_nete: list[Decimal] = Field(default_factory=list)
    index_selectat: int                                      # cel mai similar (referinta)
    indici_mediati: list[int] = Field(default_factory=list)  # M2: comparabilele incluse in medie
    valoare_piata: Decimal                                   # MEDIA preturilor corectate ale lor


class ReconciledResult(BaseModel):
    """Rezultatul reconcilierii finale."""

    valoare_finala: Decimal
    metoda_selectata: Literal["piata", "cost", "ponderata", "venit"]
    valoare_fara_tva: bool = True
    nota: str = ""


class LandResult(BaseModel):
    """Rezultatul evaluarii terenului prin grila de comparatie."""

    preturi_mp_corectate: list[Decimal] = Field(default_factory=list)
    ajustari_brute: list[Decimal] = Field(default_factory=list)
    ajustari_nete: list[Decimal] = Field(default_factory=list)
    index_selectat: int                                      # cel mai similar (referinta)
    indici_mediati: list[int] = Field(default_factory=list)  # M2: comparabilele incluse in medie
    pret_mp_ales: Decimal                                    # MEDIA pretului/mp al lor
    valoare_teren: Decimal


class RentResult(BaseModel):
    """Rezultatul grilei de chirii comparabile (chirie de piata -> abordarea prin venit)."""

    chirii_mp_corectate: list[Decimal] = Field(default_factory=list)
    ajustari_brute: list[Decimal] = Field(default_factory=list)
    ajustari_nete: list[Decimal] = Field(default_factory=list)
    index_selectat: int
    chirie_mp_aleasa: Decimal          # chirie lunara/mp selectata
    chirie_lunara: Decimal             # chirie_mp_aleasa * suprafata subiect
    venit_brut_potential: Decimal      # chirie_lunara * 12 (anual, intra in DateVenit)
