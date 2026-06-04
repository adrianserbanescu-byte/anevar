"""Raportare AML: praguri RTN, conversie EUR/LEI (curs BNR), termene legale, anti-fragmentare, RTS.

RTN = raport tranzactii numerar (>= 10.000 €). RTS = raport tranzactie suspecta. Ambele se
transmit EXCLUSIV la ONPCSB (rapoarte.onpcsb.ro); aplicatia pregateste continutul, evaluatorul
transmite. Drafturile se stocheaza SEPARAT de dosar (tipping-off, Legea art. 38).
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, Field

from evaluare.aml.constante import (
    PRAG_ANTIFRAGMENTARE_EUR,
    PRAG_NUMERAR_EUR,
    TERMEN_RTN_ZILE_LUCRATOARE,
)

_AVERTISMENT_TIPPING_OFF = (
    "ATENȚIE — interdicție de divulgare (tipping-off, Legea 129/2019 art. 38): este interzisă "
    "informarea clientului sau a terților cu privire la transmiterea/întocmirea acestui raport. "
    "Document confidențial, păstrat separat de dosarul de evaluare."
)


def _cuantizeaza(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# --------------------------------------------------------------------------- #
# Praguri si conversie
# --------------------------------------------------------------------------- #
def necesita_rtn(suma_eur) -> bool:
    """Tranzactie cu numerar a carei limita minima = echiv. 10.000 € (Legea art. 7(1))."""
    return Decimal(str(suma_eur)) >= PRAG_NUMERAR_EUR


def eur_din_lei(lei, curs) -> Decimal:
    """Echivalent EUR din LEI la cursul BNR (Norme art. 21(2))."""
    return _cuantizeaza(Decimal(str(lei)) / Decimal(str(curs)))


def lei_din_eur(eur, curs) -> Decimal:
    return _cuantizeaza(Decimal(str(eur)) * Decimal(str(curs)))


# --------------------------------------------------------------------------- #
# Zile lucratoare / termene
# --------------------------------------------------------------------------- #
def _este_lucratoare(d: date) -> bool:
    # Luni=0 ... Duminica=6. (Sarbatorile legale ar trebui adaugate ca lista de exceptii.)
    return d.weekday() < 5


def _adauga_zile_lucratoare(d: date, n: int) -> date:
    cur = d
    ramase = n
    while ramase > 0:
        cur = cur + timedelta(days=1)
        if _este_lucratoare(cur):
            ramase -= 1
    return cur


def _urmatoarea_lucratoare(d: date) -> date:
    cur = d
    while not _este_lucratoare(cur):
        cur = cur + timedelta(days=1)
    return cur


def termen_rtn(data_tranzactie: str) -> str:
    """Termenul de transmitere RTN = +3 zile lucratoare (Legea art. 7(7))."""
    d = date.fromisoformat(data_tranzactie)
    return _adauga_zile_lucratoare(d, TERMEN_RTN_ZILE_LUCRATOARE).isoformat()


def suspendare_pana_la(data_inregistrare_rts: str) -> str:
    """Suspendarea tranzactiei dupa RTS: +24h, prorogat daca expira nelucratoare (art. 8(3),(10))."""
    d = date.fromisoformat(data_inregistrare_rts) + timedelta(days=1)
    return _urmatoarea_lucratoare(d).isoformat()


# --------------------------------------------------------------------------- #
# Anti-fragmentare (Legea art. 7(4))
# --------------------------------------------------------------------------- #
def tranzactii_legate(transe: list[dict], fereastra_zile: int = 30) -> bool:
    """True daca transe legate (in fereastra) insumeaza >= pragul de 15.000 € (anti-fragmentare).

    Fiecare transa: {"suma_eur": Decimal, "data": "yyyy-mm-dd"}. Se considera „legate" transele
    aflate intr-o fereastra glisanta de `fereastra_zile`.
    """
    if not transe:
        return False
    ordonate = sorted(transe, key=lambda t: t["data"])
    for i, baza in enumerate(ordonate):
        d0 = date.fromisoformat(baza["data"])
        suma = Decimal("0")
        for t in ordonate[i:]:
            if (date.fromisoformat(t["data"]) - d0).days <= fereastra_zile:
                suma += Decimal(str(t["suma_eur"]))
        if suma >= PRAG_ANTIFRAGMENTARE_EUR:
            return True
    return False


# --------------------------------------------------------------------------- #
# Structuri de raport (stocate separat de dosar)
# --------------------------------------------------------------------------- #
class RaportRTN(BaseModel):
    """Raport tranzactie cu numerar (>= 10.000 €)."""

    tip: str = "RTN"
    suma_eur: Decimal
    data_tranzactie: str
    descriere: str = ""
    transmis: bool = False
    data_transmitere: str | None = None

    @property
    def termen(self) -> str:
        return termen_rtn(self.data_tranzactie)


class RaportRTS(BaseModel):
    """Raport tranzactie suspecta — confidential, separat de dosar (tipping-off)."""

    tip: str = "RTS"
    motiv: str
    data_inregistrare: str
    indicatori: list[str] = Field(default_factory=list)
    transmis: bool = False
    data_transmitere: str | None = None
    avertisment_tipping_off: str = _AVERTISMENT_TIPPING_OFF

    @property
    def suspendare_pana_la(self) -> str:
        return suspendare_pana_la(self.data_inregistrare)
