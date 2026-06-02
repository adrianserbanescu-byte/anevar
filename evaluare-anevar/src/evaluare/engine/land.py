"""Evaluarea terenului prin grila de comparatie directa (EUR/mp).

Metodologia reala GBF/ANEVAR are DOUA etape (validata pe 4 grile reale: Maneciu, Brasov,
Busteni, Breaza):
  1. Etapa de TRANZACTIE (oferta->tranzactie, drept, finantare, conditii vanzare, cheltuieli,
     conditiile pietei) — ajustarile se aplica SECVENTIAL (compus) -> pret de baza.
  2. Etapa de PROPRIETATE (caracteristici fizice/juridice) — ajustarile se aplica ADITIV pe
     pretul de baza: final = baza * (1 + suma % proprietate) + suma EUR proprietate.

Ajustarea bruta (criteriul de selectie) = suma valorilor absolute ale ajustarilor procentuale
din etapa de proprietate (etapa de tranzactie NU se contorizeaza). Comparabilul ales = cel cu
ajustare bruta minima. Valoarea terenului = pret/mp corectat ales * suprafata subiectului.
"""
from __future__ import annotations

from decimal import Decimal

from evaluare.models.comparable import LandComparable
from evaluare.models.results import LandResult

_UNU = Decimal("1")
_ZERO = Decimal("0")


def _pret_baza_tranzactie(comp: LandComparable) -> Decimal:
    """Pretul dupa etapa de tranzactie (ajustari secventiale, compus)."""
    pret = comp.pret_mp
    for adj in comp.adjustments:
        if adj.etapa != "tranzactie":
            continue
        if adj.tip == "procentuala":
            pret = pret * (_UNU + adj.valoare)
        else:
            pret = pret + adj.valoare
    return pret


def pret_mp_corectat(comp: LandComparable) -> Decimal:
    """Pretul/mp corectat final: etapa de tranzactie (compus) + etapa de proprietate (aditiv)."""
    baza = _pret_baza_tranzactie(comp)
    suma_pct = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    suma_eur = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    return baza * (_UNU + suma_pct) + suma_eur


def ajustare_bruta(comp: LandComparable) -> Decimal:
    """Suma valorilor absolute ale ajustarilor procentuale din etapa de proprietate."""
    return sum((abs(a.valoare) for a in comp.adjustments
                if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)


def ajustare_neta(comp: LandComparable) -> Decimal:
    """Suma algebrica a ajustarilor procentuale din etapa de proprietate."""
    return sum((a.valoare for a in comp.adjustments
                if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)


def evaluate_land(
    comparables: list[LandComparable], suprafata_subiect: Decimal
) -> LandResult:
    """Ruleaza grila de teren si selecteaza comparabilul cu ajustare bruta minima."""
    if not comparables:
        raise ValueError("Sunt necesare comparabile de teren.")
    preturi = [pret_mp_corectat(c) for c in comparables]
    brute = [ajustare_bruta(c) for c in comparables]
    nete = [ajustare_neta(c) for c in comparables]
    index = min(range(len(comparables)), key=lambda i: brute[i])
    pret_ales = preturi[index]
    valoare = pret_ales * suprafata_subiect
    return LandResult(
        preturi_mp_corectate=preturi, ajustari_brute=brute, ajustari_nete=nete,
        index_selectat=index, pret_mp_ales=pret_ales, valoare_teren=valoare,
    )
