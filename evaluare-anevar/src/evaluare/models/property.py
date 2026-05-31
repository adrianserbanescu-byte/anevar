"""Modele pentru proprietatea subiect: teren si constructie."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CostElement(BaseModel):
    """Un element constructiv din metoda costurilor segregate (catalog IROVAL)."""

    element: str            # ex. "Infrastructura", "Structura", "Finisaje"
    cod: str                # cod catalog IROVAL, ex. "FCV2"
    um: str                 # unitate de masura, ex. "mp", "buc"
    cantitate: Decimal
    cost_unitar: Decimal    # lei/u.m. (fara TVA) din catalog
    an_pif: int             # anul punerii in functiune / modernizare al elementului

    def cost_nou(self) -> Decimal:
        """Cost de nou (fara TVA) = cantitate * cost unitar."""
        return self.cantitate * self.cost_unitar

    def varsta(self, an_referinta: int) -> int:
        """Varsta cronologica = an de referinta - an PIF."""
        return an_referinta - self.an_pif


class DepreciationPoint(BaseModel):
    """Un punct din tabelul de depreciere fizica (varsta -> fractie depreciere)."""

    varsta: int
    depreciere: Decimal = Field(ge=0, le=1)     # fractie, ex. 0.31 pentru 31%


class BuildingData(BaseModel):
    """Datele fizice si de cost ale constructiei."""

    ac: Optional[Decimal] = None        # arie construita la sol
    au: Decimal                         # arie utila
    acd: Decimal                        # arie construita desfasurata
    an_referinta: int                   # anul datei de referinta a evaluarii
    elements: list[CostElement] = Field(default_factory=list)
    depreciation_points: list[DepreciationPoint] = Field(default_factory=list)
    functional_depreciation: Decimal = Decimal("0")   # C_nf (0 implicit; >0 la credit cu justificare)
    external_depreciation: Decimal = Decimal("0")      # C_ex
    justificare_depreciere: str = ""
    structura: Optional[str] = None
    finisaje: Optional[str] = None
    clasa_energetica: Optional[str] = None


class LandData(BaseModel):
    """Datele terenului."""

    suprafata: Decimal                  # mp
    categorie: str = "intravilan"       # intravilan / extravilan
    deschidere: Optional[Decimal] = None
    utilitati: list[str] = Field(default_factory=list)
    restrictii_urbanism: Optional[str] = None
