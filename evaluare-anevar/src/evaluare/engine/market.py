"""Abordarea prin piata: grila de comparatie directa pe pret TOTAL (model GBF/ANEVAR).

Validat pe grilele reale de casa (Maneciu/Brasov/Busteni). Metodologia are doua etape:
  1. Etapa de TRANZACTIE (negociere, componente non-imobiliare, drept, finantare, conditii
     vanzare, cheltuieli, conditiile pietei) — aplicata SECVENTIAL pe pretul total -> pret de baza.
  2. Etapa de PROPRIETATE (localizare, suprafata teren, arie utila, destinatie, PIF, acces, curte,
     finisaje, incalzire, alte) — aplicata ADITIV pe pretul de baza:
       final = baza * (1 + suma % proprietate) + suma EUR proprietate.

Diferenta de suprafata (arie utila) se trateaza ca ajustare VALORICA (EUR/mp x delta), deci fiecare
comparabila e adusa la subiect; valoarea = pretul total corectat al comparabilei alese (NU pret
unitar x suprafata). Selectie = ajustare bruta minima pe etapa de proprietate (regula unica).
"""
from __future__ import annotations

from decimal import Decimal

from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.models.comparable import Comparable
from evaluare.models.results import MarketResult

_UNU = Decimal("1")
_ZERO = Decimal("0")


def pret_unitar_brut(comp: Comparable) -> Decimal:
    """Pret unitar brut = pret / suprafata (indicator de afisare / detectie outlier)."""
    return comp.pret / comp.suprafata


def _pret_baza_tranzactie(comp: Comparable) -> Decimal:
    """Pretul total dupa etapa de tranzactie (ajustari secventiale, compus)."""
    pret = comp.pret
    for adj in comp.adjustments:
        if adj.etapa != "tranzactie":
            continue
        if adj.tip == "procentuala":
            pret = pret * (_UNU + adj.valoare)
        else:
            pret = pret + adj.valoare
    return pret


def pret_total_corectat(comp: Comparable) -> Decimal:
    """Pret total corectat: tranzactie (secvential) + proprietate (aditiv pe baza)."""
    baza = _pret_baza_tranzactie(comp)
    suma_pct = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    suma_eur = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    return baza * (_UNU + suma_pct) + suma_eur


def ajustare_bruta(comp: Comparable) -> Decimal:
    """Ajustarea bruta a etapei de proprietate, ca fractie din pretul de baza.

    Insumeaza valorile absolute ale ajustarilor de proprietate (procentualele direct,
    cele valorice raportate la pretul de baza). Criteriul de selectie (minim).
    """
    baza = _pret_baza_tranzactie(comp)
    g = sum((abs(a.valoare) for a in comp.adjustments
             if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    suma_eur = sum((abs(a.valoare) for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    if baza != 0:
        g += suma_eur / baza
    return g


def ajustare_neta(comp: Comparable) -> Decimal:
    """Ajustarea neta a etapei de proprietate (suma algebrica), ca fractie din baza."""
    baza = _pret_baza_tranzactie(comp)
    n = sum((a.valoare for a in comp.adjustments
             if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    suma_eur = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    if baza != 0:
        n += suma_eur / baza
    return n


def evaluate_market(
    comparables: list[Comparable], suprafata_subiect: Decimal | None = None,
    cfg: MetodologieConfig = IMPLICIT,
) -> MarketResult:
    """Ruleaza grila de comparatie pe pret total.

    Selectia: comparabilele cu ajustarea bruta minima (etapa de proprietate). Valoarea de piata =
    MEDIA preturilor totale corectate ale celor mai similare `cfg.nr_comparabile_medie` comparabile
    (M2; default = minimul legal de comparabile). `nr_comparabile_medie=1` -> comparabilul unic cel
    mai similar (comportament istoric). `index_selectat` ramane cel mai similar (referinta).
    `suprafata_subiect` este pastrat pentru compatibilitate, dar nu mai intra in formula.
    """
    if not comparables:
        raise ValueError("Sunt necesare comparabile pentru abordarea prin piata.")
    preturi = [pret_total_corectat(c) for c in comparables]
    brute = [ajustare_bruta(c) for c in comparables]
    nete = [ajustare_neta(c) for c in comparables]
    ordine = sorted(range(len(comparables)), key=lambda i: brute[i])   # cele mai similare intai
    index_selectat = ordine[0]
    n = min(max(1, cfg.nr_comparabile_medie), len(comparables))
    valoare = sum((preturi[i] for i in ordine[:n]), Decimal("0")) / n  # media top-N (N=1 -> selectie unica)
    return MarketResult(
        preturi_unitare_corectate=preturi,
        ajustari_brute=brute,
        ajustari_nete=nete,
        index_selectat=index_selectat,
        valoare_piata=valoare,
    )
