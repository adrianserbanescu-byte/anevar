"""Grila de chirii comparabile -> chirie de piata -> abordarea prin venit."""
from decimal import Decimal

import pytest

from evaluare.engine.chirie import (
    chirie_mp_corectata, date_venit_din_chirie, evalueaza_chirie,
)
from evaluare.engine.venit import evalueaza_venit
from evaluare.models.comparable import Adjustment, RentComparable


def _comp(chirie, supr, adj=None):
    return RentComparable(chirie_mp=Decimal(chirie), suprafata=Decimal(supr),
                          adjustments=adj or [])


def test_fara_ajustari_chirie_mp_neschimbata():
    c = _comp("10", "50")
    assert chirie_mp_corectata(c) == Decimal("10")


def test_etapa_proprietate_aditiva():
    # 10 * (1 + (-0.10)) = 9.00
    c = _comp("10", "50", [Adjustment(element="stare", tip="procentuala",
                                      valoare=Decimal("-0.10"), etapa="proprietate")])
    assert chirie_mp_corectata(c) == Decimal("9.00")


def test_etapa_tranzactie_compus_apoi_proprietate():
    # tranzactie -5% (compus): 10*0.95=9.5 ; proprietate +10% aditiv: 9.5*1.10=10.45
    c = _comp("10", "50", [
        Adjustment(element="oferta", tip="procentuala", valoare=Decimal("-0.05"), etapa="tranzactie"),
        Adjustment(element="finisaj", tip="procentuala", valoare=Decimal("0.10"), etapa="proprietate"),
    ])
    assert chirie_mp_corectata(c) == Decimal("10.45")


def test_selecteaza_ajustare_bruta_minima_si_vbp_anual():
    comps = [
        _comp("12", "100", [Adjustment(element="x", tip="procentuala",
                                       valoare=Decimal("-0.20"), etapa="proprietate")]),  # bruta 0.20
        _comp("10", "100", [Adjustment(element="y", tip="procentuala",
                                       valoare=Decimal("0.05"), etapa="proprietate")]),   # bruta 0.05 -> ales
    ]
    r = evalueaza_chirie(comps, Decimal("100"))
    assert r.index_selectat == 1
    assert r.chirie_mp_aleasa == Decimal("10.50")          # 10*1.05
    assert r.chirie_lunara == Decimal("1050.00")            # 10.50 * 100
    assert r.venit_brut_potential == Decimal("12600.00")    # *12


def test_fara_comparabile_ridica_eroare():
    with pytest.raises(ValueError):
        evalueaza_chirie([], Decimal("100"))


def test_suprafata_nula_ridica_eroare():
    with pytest.raises(ValueError):
        evalueaza_chirie([_comp("10", "50")], Decimal("0"))


def test_chirie_alimenteaza_abordarea_prin_venit():
    r = evalueaza_chirie([_comp("10", "100")], Decimal("100"))
    # VBP = 10*100*12 = 12000; NOI = 12000 (fara cheltuieli) ; valoare = 12000/0.08 = 150000
    dv = date_venit_din_chirie(r, rata_capitalizare=Decimal("0.08"))
    assert dv.venit_brut_potential == Decimal("12000.00")
    rv = evalueaza_venit(dv)
    assert rv.valoare == Decimal("150000.00")
