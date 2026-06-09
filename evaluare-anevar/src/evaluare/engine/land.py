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

from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
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


def _eur_ca_fractie(comp: LandComparable) -> Decimal:
    """Ajustarile valorice (EUR) de proprietate, SUMATE ALGEBRIC (cu semn), ca fractie din baza.
    Pentru ajustarea NETA (suma cu semn)."""
    baza = _pret_baza_tranzactie(comp)
    suma_eur = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    return suma_eur / baza if baza != 0 else _ZERO


def _eur_brut_fractie(comp: LandComparable) -> Decimal:
    """Ajustarile valorice (EUR) de proprietate, ABS-FIECARE-APOI-SUMA, ca fractie din baza.

    Pentru ajustarea BRUTA (criteriul de selectie) — la fel ca `market.ajustare_bruta`: ajustarile de
    semn opus NU se anuleaza (altfel un comparabil greu ajustat ar parea „cel mai usor" si ar fi ales gresit).
    """
    baza = _pret_baza_tranzactie(comp)
    suma = sum((abs(a.valoare) for a in comp.adjustments
                if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    return suma / baza if baza != 0 else _ZERO


def ajustare_bruta(comp: LandComparable, include_eur: bool = True) -> Decimal:
    """Ajustarea bruta de proprietate (criteriul de selectie): suma valorilor ABSOLUTE.

    Procentualele direct; cele VALORICE (EUR) abs-fiecare-apoi-suma / baza DOAR daca `include_eur`
    (M1, default True = CONSISTENT cu abordarea prin piata; False = doar procentuale, varianta veche).
    """
    g = sum((abs(a.valoare) for a in comp.adjustments
             if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    if include_eur:
        g += _eur_brut_fractie(comp)
    return g


def ajustare_neta(comp: LandComparable, include_eur: bool = True) -> Decimal:
    """Suma algebrica a ajustarilor de proprietate (procentuale + EUR/baza daca `include_eur`)."""
    n = sum((a.valoare for a in comp.adjustments
             if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    if include_eur:
        n += _eur_ca_fractie(comp)
    return n


def evaluate_land(
    comparables: list[LandComparable], suprafata_subiect: Decimal,
    cfg: MetodologieConfig = IMPLICIT,
) -> LandResult:
    """Ruleaza grila de teren. Valoarea = MEDIA pretului/mp corectat al celor mai similare
    `cfg.nr_comparabile_medie` comparabile (M2; default = minimul legal). N=1 -> comparabilul unic.

    `cfg.teren_selectie_include_eur` (M1) decide daca selectia numara si ajustarile valorice (EUR).
    """
    if not comparables:
        raise ValueError("Sunt necesare comparabile de teren.")
    inc = cfg.teren_selectie_include_eur
    preturi = [pret_mp_corectat(c) for c in comparables]
    brute = [ajustare_bruta(c, inc) for c in comparables]
    nete = [ajustare_neta(c, inc) for c in comparables]
    ordine = sorted(range(len(comparables)), key=lambda i: brute[i])   # cele mai similare intai
    index = ordine[0]
    n = min(max(1, cfg.nr_comparabile_medie), len(comparables))
    pret_ales = sum((preturi[i] for i in ordine[:n]), _ZERO) / n       # media top-N €/mp (N=1 -> unic)
    valoare = pret_ales * suprafata_subiect
    return LandResult(
        preturi_mp_corectate=preturi, ajustari_brute=brute, ajustari_nete=nete,
        index_selectat=index, indici_mediati=sorted(ordine[:n]),   # comparabilele mediate (M2)
        pret_mp_ales=pret_ales, valoare_teren=valoare,
    )
