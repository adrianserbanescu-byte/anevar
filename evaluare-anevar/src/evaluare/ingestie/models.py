"""Modele pentru datele extrase din documentele proprietatii (toate optionale, de confirmat)."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class DateExtraseCF(BaseModel):
    """Extras de carte funciara: identificare juridica + suprafata + sarcini."""

    numar_cadastral: Optional[str] = None
    carte_funciara: Optional[str] = None
    suprafata: Optional[Decimal] = None        # mp (teren sau imobil, dupa caz)
    proprietari: list[str] = Field(default_factory=list)
    sarcini: Optional[str] = None              # ex. "fara sarcini" / "ipoteca ..."


class DateReleveu(BaseModel):
    """Releveu: arii si regim de inaltime."""

    arie_utila: Optional[Decimal] = None
    arie_construita: Optional[Decimal] = None
    regim_inaltime: Optional[str] = None       # ex. P+2E+M


class DatePlan(BaseModel):
    """Plan de amplasament si delimitare: suprafata teren si deschidere."""

    suprafata_teren: Optional[Decimal] = None
    deschidere: Optional[Decimal] = None       # front stradal (m)


class DateCPE(BaseModel):
    """Certificat de performanta energetica."""

    clasa_energetica: Optional[str] = None      # A..G
    consum: Optional[Decimal] = None            # kWh/mp/an
