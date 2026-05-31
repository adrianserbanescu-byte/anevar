from decimal import Decimal

from evaluare.models.comparable import Adjustment, Comparable
from evaluare.engine.market import (
    pret_unitar_brut,
    aplica_ajustari,
    ajustare_bruta,
    ajustare_neta,
    evaluate_market,
)


def test_pret_unitar_brut():
    c = Comparable(pret=Decimal("500000"), suprafata=Decimal("100"))
    assert pret_unitar_brut(c) == Decimal("5000")


def test_aplica_ajustari_procentuala_secvential():
    # 5000 * (1 - 0.03) = 4850 ; apoi 4850 * (1 + 0.10) = 5335
    c = Comparable(
        pret=Decimal("500000"), suprafata=Decimal("100"),
        adjustments=[
            Adjustment(element="Conditii de vanzare", tip="procentuala",
                       valoare=Decimal("-0.03")),
            Adjustment(element="Localizare", tip="procentuala",
                       valoare=Decimal("0.10")),
        ],
    )
    assert aplica_ajustari(c) == Decimal("5335.00")


def test_aplica_ajustari_valorica():
    # 5000 + 200 (valorica) = 5200
    c = Comparable(
        pret=Decimal("500000"), suprafata=Decimal("100"),
        adjustments=[
            Adjustment(element="Utilitati", tip="valorica", valoare=Decimal("200")),
        ],
    )
    assert aplica_ajustari(c) == Decimal("5200")


def test_ajustare_bruta_si_neta():
    c = Comparable(
        pret=Decimal("500000"), suprafata=Decimal("100"),
        adjustments=[
            Adjustment(element="A", tip="procentuala", valoare=Decimal("-0.03")),
            Adjustment(element="B", tip="procentuala", valoare=Decimal("0.10")),
        ],
    )
    assert ajustare_bruta(c) == Decimal("0.13")   # |-0.03| + |0.10|
    assert ajustare_neta(c) == Decimal("0.07")    # -0.03 + 0.10


def test_evaluate_market_selecteaza_ajustarea_bruta_minima():
    # comp0: ajustare bruta 0.05 ; comp1: ajustare bruta 0.20 -> selecteaza comp0
    comp0 = Comparable(
        pret=Decimal("480000"), suprafata=Decimal("100"),
        adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("0.05"))],
    )
    comp1 = Comparable(
        pret=Decimal("520000"), suprafata=Decimal("100"),
        adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("-0.20"))],
    )
    result = evaluate_market([comp0, comp1], suprafata_subiect=Decimal("110"))
    assert result.index_selectat == 0
    # pret corectat comp0 = 4800 * 1.05 = 5040 ; * 110 = 554400
    assert result.valoare_piata == Decimal("554400.00")
