from decimal import Decimal

import pytest

from evaluare.engine.venit import (
    evalueaza_dcf,
    valoare_terminala_exit_cap,
    valoare_terminala_gordon,
)


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


# --------------------------------------------------------------------------- #
# I-19 — valoarea terminala DCF: Gordon (crestere perpetua) + exit-cap (rata terminala).
# --------------------------------------------------------------------------- #
def test_valoare_terminala_gordon():
    # NOI 100.000, r 0.10, g 0.02 -> 100000*1.02/(0.10-0.02) = 102000/0.08 = 1.275.000
    vt = valoare_terminala_gordon(Decimal("100000"), Decimal("0.10"), Decimal("0.02"))
    assert vt == Decimal("1275000.00")


def test_valoare_terminala_gordon_necesita_r_mai_mare_decat_g():
    with pytest.raises(ValueError):
        valoare_terminala_gordon(Decimal("100000"), Decimal("0.05"), Decimal("0.05"))


def test_valoare_terminala_gordon_noi_invalid():
    with pytest.raises(ValueError):
        valoare_terminala_gordon(Decimal("0"), Decimal("0.10"), Decimal("0.02"))


def test_valoare_terminala_exit_cap():
    # NOI an urmator 110.000 / rata terminala 0.09 = 1.222.222,22
    vt = valoare_terminala_exit_cap(Decimal("110000"), Decimal("0.09"))
    assert vt == Decimal("1222222.22")


def test_valoare_terminala_exit_cap_rata_invalida():
    with pytest.raises(ValueError):
        valoare_terminala_exit_cap(Decimal("110000"), Decimal("0"))


def test_valoare_terminala_alimenteaza_dcf():
    # Valoarea terminala (Gordon) intra ca valoare_reziduala in evalueaza_dcf, actualizata la prezent.
    vt = valoare_terminala_gordon(Decimal("100000"), Decimal("0.10"), Decimal("0.02"))
    v = evalueaza_dcf([Decimal("100000")], rata_actualizare=Decimal("0.10"), valoare_reziduala=vt)
    # flux 100000/1.1 = 90909.09 ; terminala 1275000/1.1 = 1159090.91 ; total 1250000.00
    assert v == Decimal("1250000.00")
