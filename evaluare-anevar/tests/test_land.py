from decimal import Decimal

import pytest

from evaluare.models.comparable import Adjustment, LandComparable
from evaluare.engine.land import pret_mp_corectat, evaluate_land


def test_pret_mp_corectat_secvential():
    c = LandComparable(pret_mp=Decimal("20"), suprafata=Decimal("500"),
                       adjustments=[
                           Adjustment(element="Ofertă→Tranzacție", tip="procentuala", valoare=Decimal("-0.10")),
                           Adjustment(element="Deschidere", tip="procentuala", valoare=Decimal("0.10")),
                       ])
    # 20 * 0.90 * 1.10 = 19.80
    assert pret_mp_corectat(c) == Decimal("19.80")


def test_pret_mp_corectat_valorica():
    c = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("400"),
                       adjustments=[Adjustment(element="X", tip="valorica", valoare=Decimal("5"))])
    assert pret_mp_corectat(c) == Decimal("105")


def test_evaluate_land_selecteaza_ajustare_bruta_minima():
    c0 = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("450"),
                        adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("0.05"))])
    c1 = LandComparable(pret_mp=Decimal("120"), suprafata=Decimal("500"),
                        adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("-0.30"))])
    r = evaluate_land([c0, c1], suprafata_subiect=Decimal("1000"))
    assert r.index_selectat == 0
    assert r.pret_mp_ales == Decimal("105.00")
    assert r.valoare_teren == Decimal("105000.00")
    assert r.ajustari_brute[0] == Decimal("0.05")


def test_evaluate_land_fara_comparabile_ridica():
    with pytest.raises(ValueError):
        evaluate_land([], suprafata_subiect=Decimal("1000"))
