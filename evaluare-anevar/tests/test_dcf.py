from decimal import Decimal

import pytest

from evaluare.engine.venit import evalueaza_dcf


def test_dcf_un_singur_flux():
    # 110000 / 1.1 = 100000.00
    assert evalueaza_dcf([Decimal("110000")], rata_actualizare=Decimal("0.10")) == Decimal("100000.00")


def test_dcf_flux_plus_rezidual():
    # flux 100000/1.1 = 90909.09 ; rezidual 110000/1.1 = 100000.00 ; total 190909.09
    v = evalueaza_dcf([Decimal("100000")], rata_actualizare=Decimal("0.10"),
                      valoare_reziduala=Decimal("110000"))
    assert v == Decimal("190909.09")


def test_dcf_trei_ani():
    # 100000 pe 3 ani la 10% (fara rezidual): 90909.09+82644.63+75131.48 = 248685.20
    v = evalueaza_dcf([Decimal("100000"), Decimal("100000"), Decimal("100000")],
                      rata_actualizare=Decimal("0.10"))
    assert v == Decimal("248685.20")


def test_dcf_rata_invalida():
    with pytest.raises(ValueError):
        evalueaza_dcf([Decimal("100000")], rata_actualizare=Decimal("0"))


def test_dcf_fara_fluxuri():
    with pytest.raises(ValueError):
        evalueaza_dcf([], rata_actualizare=Decimal("0.10"))
