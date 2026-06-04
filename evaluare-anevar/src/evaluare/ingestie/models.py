"""Modele pentru datele extrase din documentele proprietatii (toate optionale, de confirmat)."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class DateExtraseCF(BaseModel):
    """Extras de carte funciara: identificare juridica + suprafata + sarcini."""

    numar_cadastral: str | None = None
    carte_funciara: str | None = None
    suprafata: Decimal | None = None        # mp (teren sau imobil, dupa caz)
    proprietari: list[str] = Field(default_factory=list)
    sarcini: str | None = None              # ex. "fara sarcini" / "ipoteca ..."


class DateReleveu(BaseModel):
    """Releveu: arii si regim de inaltime."""

    arie_utila: Decimal | None = None
    arie_construita: Decimal | None = None
    regim_inaltime: str | None = None       # ex. P+2E+M


class DatePlan(BaseModel):
    """Plan de amplasament si delimitare: suprafata teren si deschidere."""

    suprafata_teren: Decimal | None = None
    deschidere: Decimal | None = None       # front stradal (m)


class DateCPE(BaseModel):
    """Certificat de performanta energetica."""

    clasa_energetica: str | None = None      # A..G
    consum: Decimal | None = None            # kWh/mp/an
