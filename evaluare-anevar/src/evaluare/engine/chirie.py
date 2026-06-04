"""Grila de chirii comparabile -> chirie de piata -> abordarea prin venit.

Aceeasi metodologie in doua etape ca grila de teren (validata GBF/ANEVAR):
  1. Etapa de TRANZACTIE (oferta->tranzactie, conditiile pietei etc.) — ajustari
     aplicate SECVENTIAL (compus) pe chiria/mp -> chirie de baza.
  2. Etapa de PROPRIETATE (caracteristici fizice/juridice) — ajustari aplicate
     ADITIV: final = baza * (1 + suma % proprietate) + suma valorica proprietate.

Ajustarea bruta (criteriul de selectie) = suma valorilor absolute ale ajustarilor
procentuale din etapa de proprietate. Comparabilul ales = cel cu ajustare bruta minima.
Chiria de piata = chirie/mp corectata aleasa; venitul brut potential anual al
subiectului = chirie/mp aleasa * suprafata * 12 (intra in DateVenit.venit_brut_potential).
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from evaluare.engine.venit import DateVenit
from evaluare.models.comparable import RentComparable
from evaluare.models.results import RentResult

_UNU = Decimal("1")
_ZERO = Decimal("0")
_BANI = Decimal("0.01")
_LUNI = Decimal("12")


def _chirie_baza_tranzactie(comp: RentComparable) -> Decimal:
    """Chiria/mp dupa etapa de tranzactie (ajustari secventiale, compus)."""
    chirie = comp.chirie_mp
    for adj in comp.adjustments:
        if adj.etapa != "tranzactie":
            continue
        if adj.tip == "procentuala":
            chirie = chirie * (_UNU + adj.valoare)
        else:
            chirie = chirie + adj.valoare
    return chirie


def chirie_mp_corectata(comp: RentComparable) -> Decimal:
    """Chiria/mp corectata: etapa de tranzactie (compus) + etapa de proprietate (aditiv)."""
    baza = _chirie_baza_tranzactie(comp)
    suma_pct = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    suma_eur = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    return baza * (_UNU + suma_pct) + suma_eur


def ajustare_bruta(comp: RentComparable) -> Decimal:
    """Suma valorilor absolute ale ajustarilor procentuale din etapa de proprietate."""
    return sum((abs(a.valoare) for a in comp.adjustments
                if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)


def ajustare_neta(comp: RentComparable) -> Decimal:
    """Suma algebrica a ajustarilor procentuale din etapa de proprietate."""
    return sum((a.valoare for a in comp.adjustments
                if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)


def evalueaza_chirie(
    comparables: list[RentComparable], suprafata_subiect: Decimal
) -> RentResult:
    """Ruleaza grila de chirii si selecteaza comparabilul cu ajustare bruta minima."""
    if not comparables:
        raise ValueError("Sunt necesare comparabile de chirie.")
    if suprafata_subiect <= 0:
        raise ValueError("Suprafata subiectului trebuie sa fie > 0.")
    chirii = [chirie_mp_corectata(c) for c in comparables]
    brute = [ajustare_bruta(c) for c in comparables]
    nete = [ajustare_neta(c) for c in comparables]
    index = min(range(len(comparables)), key=lambda i: brute[i])
    chirie_aleasa = chirii[index]
    chirie_lunara = (chirie_aleasa * suprafata_subiect).quantize(_BANI, rounding=ROUND_HALF_UP)
    vbp = (chirie_lunara * _LUNI).quantize(_BANI, rounding=ROUND_HALF_UP)
    return RentResult(
        chirii_mp_corectate=chirii, ajustari_brute=brute, ajustari_nete=nete,
        index_selectat=index, chirie_mp_aleasa=chirie_aleasa,
        chirie_lunara=chirie_lunara, venit_brut_potential=vbp,
    )


def date_venit_din_chirie(
    rezultat: RentResult,
    rata_capitalizare: Decimal,
    grad_neocupare: Decimal = _ZERO,
    cheltuieli_exploatare: Decimal = _ZERO,
) -> DateVenit:
    """Construieste DateVenit din chiria de piata (venit brut potential anual)."""
    return DateVenit(
        venit_brut_potential=rezultat.venit_brut_potential,
        grad_neocupare=grad_neocupare,
        cheltuieli_exploatare=cheltuieli_exploatare,
        rata_capitalizare=rata_capitalizare,
    )
