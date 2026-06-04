from decimal import Decimal

import pytest

from evaluare.engine.venit import DateVenit, RezultatVenit, evalueaza_venit, abordare_venit


def test_capitalizare_directa_simpla():
    # VBP 100.000; neocupare 5%; cheltuieli 20.000; rata 8% -> NOI=75.000; valoare=937.500
    d = DateVenit(venit_brut_potential=Decimal("100000"), grad_neocupare=Decimal("0.05"),
                  cheltuieli_exploatare=Decimal("20000"), rata_capitalizare=Decimal("0.08"))
    r = evalueaza_venit(d)
    assert isinstance(r, RezultatVenit)
    assert r.noi == Decimal("75000.00")
    assert r.valoare == Decimal("937500.00")


def test_fara_neocupare_fara_cheltuieli():
    d = DateVenit(venit_brut_potential=Decimal("80000"), rata_capitalizare=Decimal("0.10"))
    r = evalueaza_venit(d)
    assert r.noi == Decimal("80000.00")
    assert r.valoare == Decimal("800000.00")


def test_rata_capitalizare_invalida():
    with pytest.raises(ValueError):
        evalueaza_venit(DateVenit(venit_brut_potential=Decimal("10000"),
                                  rata_capitalizare=Decimal("0")))


def test_abordare_venit_adaptor():
    d = DateVenit(venit_brut_potential=Decimal("80000"), rata_capitalizare=Decimal("0.10"))
    r = abordare_venit(d)
    assert r.abordare == "venit"
    assert r.valoare == Decimal("800000.00")
    assert "noi" in r.detalii
