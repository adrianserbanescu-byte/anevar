"""Raportare AML — praguri RTN, conversie EUR/LEI, termene, anti-fragmentare, RTS."""
from decimal import Decimal

from evaluare.aml.raportare import (
    RaportRTN,
    RaportRTS,
    eur_din_lei,
    lei_din_eur,
    necesita_rtn,
    suspendare_pana_la,
    termen_rtn,
    tranzactii_legate,
)


# --------------------------------------------------------------------------- #
# Prag RTN (numerar) — Legea art. 7(1): limita minima = echiv. 10.000 €
# --------------------------------------------------------------------------- #
def test_necesita_rtn_prag():
    assert necesita_rtn(Decimal("9999")) is False
    assert necesita_rtn(Decimal("10000")) is True
    assert necesita_rtn(Decimal("10000.01")) is True


# --------------------------------------------------------------------------- #
# Conversie EUR/LEI la cursul BNR (Norme art. 21(2))
# --------------------------------------------------------------------------- #
def test_conversie_eur_lei():
    curs = Decimal("4.97")
    assert eur_din_lei(Decimal("49700"), curs) == Decimal("10000")
    assert lei_din_eur(Decimal("10000"), curs) == Decimal("49700")


def test_rtn_din_lei_la_curs():
    curs = Decimal("5.00")
    # 50.000 lei / 5 = 10.000 € -> RTN
    assert necesita_rtn(eur_din_lei(Decimal("50000"), curs)) is True
    # 49.000 lei / 5 = 9.800 € -> fara RTN
    assert necesita_rtn(eur_din_lei(Decimal("49000"), curs)) is False


# --------------------------------------------------------------------------- #
# Termen RTN = +3 zile lucratoare (Legea art. 7(7))
# --------------------------------------------------------------------------- #
def test_termen_rtn_sare_peste_weekend():
    # 2026-06-03 e miercuri -> +3 zile lucratoare = luni 2026-06-08
    assert termen_rtn("2026-06-03") == "2026-06-08"


def test_termen_rtn_de_vineri():
    # 2026-06-05 e vineri -> +3 zile lucratoare = miercuri 2026-06-10
    assert termen_rtn("2026-06-05") == "2026-06-10"


# --------------------------------------------------------------------------- #
# Suspendare dupa RTS — termen care expira nelucratoare se proroga (art. 8(3),(10))
# --------------------------------------------------------------------------- #
def test_suspendare_proroga_la_zi_lucratoare():
    # vineri + 1 zi -> sambata -> prorogat la luni
    assert suspendare_pana_la("2026-06-05") == "2026-06-08"
    # miercuri + 1 zi -> joi (lucratoare)
    assert suspendare_pana_la("2026-06-03") == "2026-06-04"


# --------------------------------------------------------------------------- #
# Anti-fragmentare (Legea art. 7(4)) — transe legate sub 15.000 € care insumate depasesc
# --------------------------------------------------------------------------- #
def test_tranzactii_legate_insumeaza_peste_prag():
    transe = [
        {"suma_eur": Decimal("8000"), "data": "2026-06-01"},
        {"suma_eur": Decimal("8000"), "data": "2026-06-02"},
    ]
    assert tranzactii_legate(transe, fereastra_zile=30) is True


def test_tranzactii_nelegate_in_afara_ferestrei():
    transe = [
        {"suma_eur": Decimal("8000"), "data": "2026-01-01"},
        {"suma_eur": Decimal("8000"), "data": "2026-06-02"},
    ]
    assert tranzactii_legate(transe, fereastra_zile=30) is False


def test_tranzactii_sub_prag_total():
    transe = [
        {"suma_eur": Decimal("5000"), "data": "2026-06-01"},
        {"suma_eur": Decimal("6000"), "data": "2026-06-02"},
    ]
    assert tranzactii_legate(transe, fereastra_zile=30) is False


# --------------------------------------------------------------------------- #
# Structuri RTN / RTS
# --------------------------------------------------------------------------- #
def test_raport_rtn_se_construieste():
    r = RaportRTN(suma_eur=Decimal("12000"), data_tranzactie="2026-06-03")
    assert r.tip == "RTN"
    assert r.termen == "2026-06-08"
    assert r.transmis is False


def test_raport_rts_are_avertisment_tipping_off():
    r = RaportRTS(motiv="presiune pentru valoare predeterminată", data_inregistrare="2026-06-05")
    assert r.tip == "RTS"
    assert "divulg" in r.avertisment_tipping_off.lower() or "art. 38" in r.avertisment_tipping_off
    assert r.suspendare_pana_la == "2026-06-08"
