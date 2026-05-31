"""Abordarea prin piata: grila de comparatie directa (SEV 105)."""
from __future__ import annotations

from decimal import Decimal

from evaluare.models.comparable import Comparable
from evaluare.models.results import MarketResult


def pret_unitar_brut(comp: Comparable) -> Decimal:
    """Pret unitar brut = pret / suprafata."""
    return comp.pret / comp.suprafata


def aplica_ajustari(comp: Comparable) -> Decimal:
    """Aplica ajustarile ierarhic, secvential, pe pretul curent.

    Procentuala: pret *= (1 + valoare). Valorica: pret += valoare.
    Ordinea de aplicare este ordinea din lista `adjustments`.
    """
    pret = pret_unitar_brut(comp)
    for adj in comp.adjustments:
        if adj.tip == "procentuala":
            pret = pret * (Decimal("1") + adj.valoare)
        else:  # valorica
            pret = pret + adj.valoare
    return pret


def ajustare_bruta(comp: Comparable) -> Decimal:
    """Suma absoluta a corectiilor procentuale (indicator de calitate)."""
    return sum(
        (abs(a.valoare) for a in comp.adjustments if a.tip == "procentuala"),
        Decimal("0"),
    )


def ajustare_neta(comp: Comparable) -> Decimal:
    """Suma algebrica a corectiilor procentuale."""
    return sum(
        (a.valoare for a in comp.adjustments if a.tip == "procentuala"),
        Decimal("0"),
    )


def evaluate_market(
    comparables: list[Comparable], suprafata_subiect: Decimal
) -> MarketResult:
    """Ruleaza grila de comparatie si selecteaza comparabilul cel mai credibil.

    Selectia: comparabilul cu ajustarea bruta minima (cel mai similar).
    Valoarea = pretul unitar corectat al acelui comparabil * suprafata subiect.
    """
    if not comparables:
        raise ValueError("Sunt necesare comparabile pentru abordarea prin piata.")
    preturi = [aplica_ajustari(c) for c in comparables]
    brute = [ajustare_bruta(c) for c in comparables]
    nete = [ajustare_neta(c) for c in comparables]
    index_selectat = min(range(len(comparables)), key=lambda i: brute[i])
    valoare = preturi[index_selectat] * suprafata_subiect
    return MarketResult(
        preturi_unitare_corectate=preturi,
        ajustari_brute=brute,
        ajustari_nete=nete,
        index_selectat=index_selectat,
        valoare_piata=valoare,
    )
