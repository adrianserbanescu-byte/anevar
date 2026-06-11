from decimal import Decimal

import pytest

from evaluare.engine.venit import (
    RATA_ACT_MAX,
    RATA_ACT_MIN,
    DateDCF,
    abordare_dcf,
    evalueaza_dcf,
    valideaza_rata_actualizare,
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


# --------------------------------------------------------------------------- #
# B2-DCF — sursa + banda de plauzibilitate pentru rata de ACTUALIZARE (simetric cu rata de capit.).
# valideaza_rata_actualizare = alerta NON-blocanta (SEV 103 A20.31-A20.34); rata libera ramane fallback.
# --------------------------------------------------------------------------- #
def test_rata_actualizare_in_banda_fara_alerta():
    assert valideaza_rata_actualizare(Decimal("0.10")) is None
    # capetele intervalului sunt acceptate (inclusiv).
    assert valideaza_rata_actualizare(RATA_ACT_MIN) is None
    assert valideaza_rata_actualizare(RATA_ACT_MAX) is None


def test_rata_actualizare_sub_prag_da_alerta():
    msg = valideaza_rata_actualizare(Decimal("0.03"))
    assert msg is not None
    assert "sub pragul" in msg


def test_rata_actualizare_peste_prag_da_alerta():
    # 20 in loc de 0.20 — exact confuzia de unitate pe care banda o prinde.
    msg = valideaza_rata_actualizare(Decimal("20"))
    assert msg is not None
    assert "peste pragul" in msg


def test_rata_actualizare_nepozitiva_da_alerta():
    assert valideaza_rata_actualizare(Decimal("0")) is not None
    assert valideaza_rata_actualizare(Decimal("-0.05")) is not None


def test_validare_rata_actualizare_nu_blocheaza_calculul():
    # Alerta e doar informativa: evalueaza_dcf calculeaza normal si pe o rata in afara benzii.
    v = evalueaza_dcf([Decimal("110000")], rata_actualizare=Decimal("0.03"))
    assert v == Decimal("106796.12")  # 110000/1.03


def test_datedcf_sursa_implicita_goala_backward_compatible():
    # Campul nou e optional: modelul se construieste fara el, ca inainte.
    d = DateDCF(fluxuri=[Decimal("100000")], rata_actualizare=Decimal("0.10"))
    assert d.sursa_rata_actualizare == ""


def test_abordare_dcf_expune_alerta_si_sursa_in_detalii():
    d = DateDCF(
        fluxuri=[Decimal("100000")], rata_actualizare=Decimal("0.03"),
        sursa_rata_actualizare="WACC build-up 2026",
    )
    r = abordare_dcf(d)
    assert r.abordare == "venit"
    assert r.valoare == Decimal("97087.38")  # 100000/1.03
    assert "sub pragul" in r.detalii["alerta_rata_actualizare"]
    assert r.detalii["sursa_rata_actualizare"] == "WACC build-up 2026"


def test_abordare_dcf_fara_alerta_cand_rata_plauzibila():
    d = DateDCF(fluxuri=[Decimal("110000")], rata_actualizare=Decimal("0.10"))
    r = abordare_dcf(d)
    assert r.valoare == Decimal("100000.00")
    assert "alerta_rata_actualizare" not in r.detalii
    assert "sursa_rata_actualizare" not in r.detalii  # sursa goala => nu se expune
