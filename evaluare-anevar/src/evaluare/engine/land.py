"""Evaluarea terenului prin grila de comparatie directa (EUR/mp).

Mecanica identica cu grila de casa: ajustari secventiale, selectie pe ajustare bruta minima.
Difera doar pretul de pornire (EUR/mp direct) si formula valorii (pret_mp x suprafata).
"""
from __future__ import annotations

from decimal import Decimal

from evaluare.models.comparable import LandComparable
from evaluare.models.results import LandResult
from evaluare.engine.market import ajustare_bruta, ajustare_neta


def pret_mp_corectat(comp: LandComparable) -> Decimal:
    """Aplica ajustarile secvential pe pretul EUR/mp (procentual: *(1+v); valoric: +v)."""
    pret = comp.pret_mp
    for adj in comp.adjustments:
        if adj.tip == "procentuala":
            pret = pret * (Decimal("1") + adj.valoare)
        else:
            pret = pret + adj.valoare
    return pret


def evaluate_land(
    comparables: list[LandComparable], suprafata_subiect: Decimal
) -> LandResult:
    """Ruleaza grila de teren si selecteaza comparabilul cu ajustare bruta minima.

    Valoarea terenului = pret_mp corectat al comparabilului ales * suprafata subiectului.
    """
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
