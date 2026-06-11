from decimal import Decimal

import pytest

from evaluare.engine.venit import (
    CheltuieliExploatare,
    DateVenit,
    RezultatVenit,
    abordare_venit,
    evalueaza_venit,
    rata_build_up,
    rata_din_comparabile,
    rata_din_vanzare_inchiriere,
    valideaza_rata_capitalizare,
)


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


def test_grad_neocupare_peste_unu_invalid():
    with pytest.raises(ValueError):
        DateVenit(venit_brut_potential=Decimal("100000"), grad_neocupare=Decimal("1.5"),
                  rata_capitalizare=Decimal("0.08"))


def test_cheltuieli_negative_invalide():
    with pytest.raises(ValueError):
        DateVenit(venit_brut_potential=Decimal("100000"), cheltuieli_exploatare=Decimal("-1"),
                  rata_capitalizare=Decimal("0.08"))


# --------------------------------------------------------------------------- #
# I-7 — derivarea ratei de capitalizare din piata + build-up + validare + sursa.
# --------------------------------------------------------------------------- #
def test_rata_din_vanzare_inchiriere_exemplul_articol():
    # Articolul: pret 1.000.000, chirie neta 80.000 -> 8%.
    assert rata_din_vanzare_inchiriere(Decimal("1000000"), Decimal("80000")) == Decimal("0.08")


def test_rata_din_vanzare_inchiriere_pret_invalid():
    with pytest.raises(ValueError):
        rata_din_vanzare_inchiriere(Decimal("0"), Decimal("80000"))


def test_rata_din_comparabile_media():
    # (1.000.000, 80.000)->0.08 ; (1.000.000, 100.000)->0.10 ; media = 0.09
    perechi = [(Decimal("1000000"), Decimal("80000")), (Decimal("1000000"), Decimal("100000"))]
    assert rata_din_comparabile(perechi) == Decimal("0.09")


def test_rata_din_comparabile_fara_perechi():
    with pytest.raises(ValueError):
        rata_din_comparabile([])


def test_rata_build_up_insumeaza_componentele():
    # fara risc 0.04 + prima risc 0.03 + nelichiditate 0.01 + recuperare 0.005 = 0.085
    r = rata_build_up(Decimal("0.04"), Decimal("0.03"),
                      prima_nelichiditate=Decimal("0.01"), recuperare_capital=Decimal("0.005"))
    assert r == Decimal("0.085")


def test_rata_build_up_componenta_negativa_invalida():
    with pytest.raises(ValueError):
        rata_build_up(Decimal("0.04"), Decimal("-0.01"))


def test_valideaza_rata_in_interval_nicio_alerta():
    assert valideaza_rata_capitalizare(Decimal("0.08")) is None


def test_valideaza_rata_prea_mica_alerta():
    assert valideaza_rata_capitalizare(Decimal("0.005")) is not None


def test_valideaza_rata_prea_mare_alerta():
    # 0.8 in loc de 0.08 — exact riscul din articol (x10 deformare).
    assert valideaza_rata_capitalizare(Decimal("0.8")) is not None


def test_abordare_venit_alerta_rata_aberanta_dar_calculeaza():
    # rata aberanta (0.80) -> calculul nu blocheaza, dar abordarea expune alerta.
    d = DateVenit(venit_brut_potential=Decimal("80000"), rata_capitalizare=Decimal("0.80"),
                  sursa_rata="vanzare-inchiriere comparabila X")
    r = abordare_venit(d)
    assert r.valoare == Decimal("100000.00")
    assert "alerta_rata" in r.detalii
    assert r.detalii["sursa_rata"] == "vanzare-inchiriere comparabila X"


def test_abordare_venit_rata_plauzibila_fara_alerta():
    d = DateVenit(venit_brut_potential=Decimal("80000"), rata_capitalizare=Decimal("0.10"))
    r = abordare_venit(d)
    assert "alerta_rata" not in r.detalii


def test_date_venit_sursa_rata_optionala_backward_compatible():
    # Fara sursa_rata, modelul ramane valid (default "").
    d = DateVenit(venit_brut_potential=Decimal("80000"), rata_capitalizare=Decimal("0.10"))
    assert d.sursa_rata == ""


# --------------------------------------------------------------------------- #
# I-8 — defalcarea cheltuielilor de exploatare (OPEX) + fond de rulment != OPEX.
# --------------------------------------------------------------------------- #
def test_cheltuieli_exploatare_total_insumeaza_pozitiile():
    c = CheltuieliExploatare(taxe=Decimal("5000"), asigurare=Decimal("2000"),
                             administrare=Decimal("3000"), intretinere=Decimal("4000"),
                             utilitati=Decimal("6000"))
    assert c.total() == Decimal("20000")


def test_fond_rulment_nu_intra_in_opex():
    # Articol: fondul de rulment (capital) NU se capitalizeaza ca OPEX recurent.
    c = CheltuieliExploatare(taxe=Decimal("10000"), fond_rulment=Decimal("50000"))
    assert c.total() == Decimal("10000")


def test_opex_defalcat_se_mapeaza_pe_scalarul_existent():
    # Modul defalcat -> total -> scalarul DateVenit produce ACELASI rezultat ca modul simplu.
    opex = CheltuieliExploatare(taxe=Decimal("5000"), utilitati=Decimal("8000"),
                                management=Decimal("7000"))
    d_defalcat = DateVenit(venit_brut_potential=Decimal("100000"), grad_neocupare=Decimal("0.05"),
                           cheltuieli_exploatare=opex.total(), rata_capitalizare=Decimal("0.08"))
    d_scalar = DateVenit(venit_brut_potential=Decimal("100000"), grad_neocupare=Decimal("0.05"),
                         cheltuieli_exploatare=Decimal("20000"), rata_capitalizare=Decimal("0.08"))
    assert evalueaza_venit(d_defalcat).valoare == evalueaza_venit(d_scalar).valoare


def test_cheltuieli_exploatare_pozitie_negativa_invalida():
    with pytest.raises(ValueError):
        CheltuieliExploatare(taxe=Decimal("-1"))
