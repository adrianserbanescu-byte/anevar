"""Abordarea prin venit — capitalizare directă (NOI ÷ rată de capitalizare)."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, Field

from evaluare.engine.abordari import RezultatAbordare

_BANI = Decimal("0.01")


class DateVenit(BaseModel):
    """Intrările pentru capitalizarea directă (sume anuale; procente ca fracție [0,1])."""

    venit_brut_potential: Decimal = Field(ge=0)
    grad_neocupare: Decimal = Field(default=Decimal("0"), ge=0, lt=1)
    cheltuieli_exploatare: Decimal = Field(default=Decimal("0"), ge=0)
    rata_capitalizare: Decimal


class RezultatVenit(BaseModel):
    noi: Decimal
    valoare: Decimal


class DateDCF(BaseModel):
    """Intrari DCF: fluxuri anuale + rata de actualizare + valoare reziduala."""

    fluxuri: list[Decimal]
    rata_actualizare: Decimal
    valoare_reziduala: Decimal = Decimal("0")


def evalueaza_venit(d: DateVenit) -> RezultatVenit:
    """Valoare = (VBP − pierderi neocupare − cheltuieli) ÷ rată de capitalizare."""
    if d.rata_capitalizare <= 0:
        raise ValueError("Rata de capitalizare trebuie să fie > 0.")
    pierdere = d.venit_brut_potential * d.grad_neocupare
    venit_efectiv = d.venit_brut_potential - pierdere
    noi = (venit_efectiv - d.cheltuieli_exploatare).quantize(_BANI, rounding=ROUND_HALF_UP)
    if noi <= 0:
        raise ValueError(
            f"Venitul net din exploatare (NOI) rezultat este <= 0 ({noi}); "
            "verificati cheltuielile / gradul de neocupare fata de venitul brut."
        )
    valoare = (noi / d.rata_capitalizare).quantize(_BANI, rounding=ROUND_HALF_UP)
    return RezultatVenit(noi=noi, valoare=valoare)


def abordare_venit(d: DateVenit) -> RezultatAbordare:
    r = evalueaza_venit(d)
    return RezultatAbordare(abordare="venit", valoare=r.valoare, detalii={"noi": str(r.noi)})


def evalueaza_dcf(fluxuri: list[Decimal], rata_actualizare: Decimal,
                  valoare_reziduala: Decimal = Decimal("0")) -> Decimal:
    """Valoare prin actualizarea fluxurilor de numerar (DCF).

    value = Σ flux_t/(1+r)^t (t=1..n) + valoare_reziduala/(1+r)^n.
    """
    if rata_actualizare <= 0:
        raise ValueError("Rata de actualizare trebuie să fie > 0.")
    if not fluxuri:
        raise ValueError("Sunt necesare fluxuri de numerar pentru DCF.")
    factor = Decimal("1") + rata_actualizare
    total = Decimal("0")
    for t, flux in enumerate(fluxuri, start=1):
        total += Decimal(flux) / (factor ** t)
    n = len(fluxuri)
    total += Decimal(valoare_reziduala) / (factor ** n)
    return total.quantize(_BANI, rounding=ROUND_HALF_UP)
