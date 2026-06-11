from decimal import Decimal

from evaluare.models.comparable import (
    Adjustment,
    Comparable,
    LandComparable,
)


def test_adjustment_percentage_and_value():
    a = Adjustment(element="Localizare", tip="procentuala", valoare=Decimal("-0.05"),
                   justificare="pozitie inferioara")
    assert a.tip == "procentuala"
    assert a.valoare == Decimal("-0.05")


def test_comparable_with_adjustments():
    c = Comparable(
        sursa="manual",
        pret=Decimal("500000"),
        suprafata=Decimal("100"),
        tip_oferta="oferta",
        adjustments=[
            Adjustment(element="Conditii de vanzare", tip="procentuala",
                       valoare=Decimal("-0.03"), justificare="oferta activa"),
        ],
    )
    assert c.pret == Decimal("500000")
    assert len(c.adjustments) == 1


def test_land_comparable():
    lc = LandComparable(pret_mp=Decimal("80"), suprafata=Decimal("450"),
                        localizare="zona X")
    assert lc.pret_mp == Decimal("80")


def test_land_comparable_sursa_default_backward_compat():
    """Constructiile existente (fara `sursa`) raman valide; default None (gap B2-N1)."""
    lc = LandComparable(pret_mp=Decimal("80"), suprafata=Decimal("450"))
    assert lc.sursa is None


def test_land_comparable_with_sursa():
    """`sursa` poate fi setat (URL sau 'manual') pe terenuri, simetric cu Comparable."""
    lc = LandComparable(
        pret_mp=Decimal("80"),
        suprafata=Decimal("450"),
        sursa="https://exemplu.ro/anunt-teren",
    )
    assert lc.sursa == "https://exemplu.ro/anunt-teren"
