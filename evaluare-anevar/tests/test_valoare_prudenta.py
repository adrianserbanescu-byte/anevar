"""Valoarea prudentă (valoarea de garanție) — CRR III / Reg. UE 575 art. 229 + 208 (gap B2-RV1/RV2).

Verifică modulul `evaluare.valoare_prudenta`: estimarea valorii prudente din valoarea de piață + parametri
prudențiali (art. 229), formula de reevaluare (art. 208), textul explicativ pentru raport și clarificarea
că valoarea prudentă NU înlocuiește valoarea de piață SEV.

Invarianții critici (poziția CRR art. 229):
  - valoarea prudentă ESTE ÎNTOTDEAUNA ≤ valoarea de piață (lit. c — nu poate depăși valoarea de piață);
  - valoarea prudentă NU poate fi negativă;
  - cu parametri impliciți (toți 0) -> valoarea prudentă = valoarea de piață (caz neutru).
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from evaluare.valoare_prudenta import (
    REFERINTA_CRR,
    TEXT_EXPLICATIV_VALOARE_PRUDENTA,
    ParametriValoarePrudenta,
    RezultatValoarePrudenta,
    estimeaza_valoare_prudenta,
    genereaza_nota_valoare_prudenta,
    valoare_garantie_reevaluare,
)


# ── Caz neutru (parametri impliciți) ──────────────────────────────────────────
def test_parametri_impliciti_dau_valoare_prudenta_egala_cu_valoarea_de_piata():
    r = estimeaza_valoare_prudenta(Decimal("500000"))
    assert r.valoare_prudenta == Decimal("500000")
    assert r.valoare_piata == Decimal("500000")
    assert r.reducere_totala == Decimal("0")
    assert r.reducere_pct == Decimal("0")


def test_accepta_valoarea_de_piata_ca_float_int_str():
    assert estimeaza_valoare_prudenta(500000).valoare_prudenta == Decimal("500000")
    assert estimeaza_valoare_prudenta(500000.0).valoare_prudenta == Decimal("500000")
    assert estimeaza_valoare_prudenta("500000").valoare_prudenta == Decimal("500000")


# ── Mecanica art. 229 (discount creștere + haircut sustenabilitate + excludere) ─
def test_discount_de_crestere_reduce_valoarea():
    p = ParametriValoarePrudenta(discount_crestere_pct=Decimal("10"))
    r = estimeaza_valoare_prudenta(Decimal("500000"), p)
    assert r.valoare_prudenta == Decimal("450000")
    assert r.discount_crestere_lei == Decimal("50000")
    assert r.reducere_totala == Decimal("50000")


def test_haircut_sustenabilitate_se_aplica_dupa_discountul_de_crestere():
    # discount 10% -> 450000; haircut 10% pe 450000 -> 45000; rezultat 405000 (compunere, nu 20% direct).
    p = ParametriValoarePrudenta(
        discount_crestere_pct=Decimal("10"),
        haircut_sustenabilitate_pct=Decimal("10"),
    )
    r = estimeaza_valoare_prudenta(Decimal("500000"), p)
    assert r.discount_crestere_lei == Decimal("50000")
    assert r.haircut_sustenabilitate_lei == Decimal("45000")
    assert r.valoare_prudenta == Decimal("405000")


def test_excluderea_elementelor_speculative_este_suma_fixa():
    p = ParametriValoarePrudenta(excludere_elemente_speculative=Decimal("25000"))
    r = estimeaza_valoare_prudenta(Decimal("500000"), p)
    assert r.excludere_speculativa_lei == Decimal("25000")
    assert r.valoare_prudenta == Decimal("475000")


def test_combinatie_completa_de_parametri():
    p = ParametriValoarePrudenta(
        discount_crestere_pct=Decimal("8"),
        haircut_sustenabilitate_pct=Decimal("5"),
        excludere_elemente_speculative=Decimal("10000"),
    )
    r = estimeaza_valoare_prudenta(Decimal("600000"), p)
    # 600000 - 8% = 552000; - 5% pe 552000 = 524400; - 10000 = 514400
    assert r.valoare_prudenta == Decimal("514400")
    assert r.reducere_totala == Decimal("600000") - Decimal("514400")


# ── Invarianți CRR art. 229 ───────────────────────────────────────────────────
@pytest.mark.parametrize("vp", ["100000", "350000", "1000000", "7777777"])
@pytest.mark.parametrize(
    "params",
    [
        {"discount_crestere_pct": Decimal("0")},
        {"discount_crestere_pct": Decimal("25")},
        {"haircut_sustenabilitate_pct": Decimal("40")},
        {"excludere_elemente_speculative": Decimal("50000")},
        {
            "discount_crestere_pct": Decimal("100"),
            "haircut_sustenabilitate_pct": Decimal("100"),
        },
    ],
)
def test_valoarea_prudenta_nu_depaseste_niciodata_valoarea_de_piata(vp, params):
    r = estimeaza_valoare_prudenta(vp, ParametriValoarePrudenta(**params))
    assert r.valoare_prudenta <= r.valoare_piata


def test_valoarea_prudenta_nu_este_niciodata_negativa():
    # excludere mai mare decât valoarea -> plafonat la 0, nu negativ.
    p = ParametriValoarePrudenta(excludere_elemente_speculative=Decimal("999999999"))
    r = estimeaza_valoare_prudenta(Decimal("500000"), p)
    assert r.valoare_prudenta == Decimal("0")
    assert r.reducere_totala == Decimal("500000")
    # Mutation guard: la reducere completă, procentul de reducere = exact 100 (numărătorul
    # `reducere` și numitorul `vp_r` din formula reducere_pct trebuie să fie ambii valoarea de piață).
    assert r.reducere_pct == Decimal("100")


def test_discount_de_100_la_suta_duce_la_zero():
    p = ParametriValoarePrudenta(discount_crestere_pct=Decimal("100"))
    r = estimeaza_valoare_prudenta(Decimal("500000"), p)
    assert r.valoare_prudenta == Decimal("0")


def test_valoare_de_piata_negativa_arunca():
    with pytest.raises(ValueError):
        estimeaza_valoare_prudenta(Decimal("-1"))


def test_valoare_de_piata_zero_nu_arunca_si_da_zero():
    r = estimeaza_valoare_prudenta(Decimal("0"))
    assert r.valoare_prudenta == Decimal("0")
    assert r.reducere_pct == Decimal("0")  # nu împarte la zero


# ── Validarea parametrilor ────────────────────────────────────────────────────
def test_procentele_in_afara_intervalului_0_100_sunt_respinse():
    with pytest.raises(ValidationError):
        ParametriValoarePrudenta(discount_crestere_pct=Decimal("101"))
    with pytest.raises(ValidationError):
        ParametriValoarePrudenta(haircut_sustenabilitate_pct=Decimal("-1"))


def test_excluderea_negativa_este_respinsa():
    with pytest.raises(ValidationError):
        ParametriValoarePrudenta(excludere_elemente_speculative=Decimal("-5"))


# ── Procentul de reducere raportat la valoarea de piață ───────────────────────
def test_reducere_pct_este_corecta():
    p = ParametriValoarePrudenta(discount_crestere_pct=Decimal("20"))
    r = estimeaza_valoare_prudenta(Decimal("500000"), p)
    assert r.reducere_pct == Decimal("20")


# ── Formula de reevaluare art. 208 (min[media istorică; valoare curentă]) ──────
def test_reevaluare_fara_istoric_intoarce_valoarea_curenta():
    assert valoare_garantie_reevaluare(Decimal("500000")) == Decimal("500000")
    assert valoare_garantie_reevaluare(Decimal("500000"), []) == Decimal("500000")


def test_reevaluare_plafoneaza_la_media_istorica_in_piata_in_crestere():
    # media(400000, 420000, 440000) = 420000 < 500000 curent -> se plafonează la 420000.
    rez = valoare_garantie_reevaluare(
        Decimal("500000"),
        [Decimal("400000"), Decimal("420000"), Decimal("440000")],
    )
    assert rez == Decimal("420000")


def test_reevaluare_urmeaza_valoarea_curenta_cand_e_sub_media():
    # media(400000, 420000, 440000) = 420000 > 380000 curent -> ia valoarea curentă (mai mică).
    rez = valoare_garantie_reevaluare(
        Decimal("380000"),
        [Decimal("400000"), Decimal("420000"), Decimal("440000")],
    )
    assert rez == Decimal("380000")


def test_reevaluare_media_se_calculeaza_pe_numarul_real_de_valori():
    # Mutation guard: media = sum / len(anterioare). Cu 2 valori, divizorul TREBUIE să fie 2.
    # media(300000, 500000) = 400000 < 600000 curent -> plafonat la 400000.
    # Un mutant care schimbă divizorul (ex. constantă, len+/-1) ar rata exact 400000.
    rez = valoare_garantie_reevaluare(
        Decimal("600000"),
        [Decimal("300000"), Decimal("500000")],
    )
    assert rez == Decimal("400000")


def test_reevaluare_media_rotunjita_jumatate_in_sus():
    # Mutation guard: media e rotunjită la leu întreg cu ROUND_HALF_UP. mean(100, 101) = 100.5
    # -> 101 (half-up), NU 100 (trunchiere). Distinge round_lei corect de o trunchiere.
    rez = valoare_garantie_reevaluare(
        Decimal("500000"),
        [Decimal("100"), Decimal("101")],
    )
    assert rez == Decimal("101")


def test_reevaluare_egalitate_medie_egal_curent():
    # Mutation guard pe operatorul de plafonare: când media == curentul, min => acea valoare,
    # indiferent dacă mutantul ar fi min/max (ambele dau egalul). Verifică totuși non-eroare la egalitate.
    rez = valoare_garantie_reevaluare(Decimal("400000"), [Decimal("400000")])
    assert rez == Decimal("400000")


def test_reevaluare_valoare_curenta_negativa_arunca():
    with pytest.raises(ValueError):
        valoare_garantie_reevaluare(Decimal("-1"), [Decimal("100")])


# ── Textul explicativ pentru raport ───────────────────────────────────────────
def test_textul_explicativ_afirma_distinctia_fata_de_valoarea_de_piata():
    t = TEXT_EXPLICATIV_VALOARE_PRUDENTA.lower()
    assert "distinct" in t
    assert "garant" in t


def test_textul_explicativ_clarifica_ca_nu_inlocuieste_valoarea_de_piata_sev():
    # Clarificarea critică din task: e DISTINCTĂ de valoarea de piață SEV, NU o înlocuiește.
    t = TEXT_EXPLICATIV_VALOARE_PRUDENTA
    assert "NU înlocuiește" in t
    assert "SEV 102" in t


def test_textul_explicativ_enumera_cele_trei_criterii_art_229():
    t = TEXT_EXPLICATIV_VALOARE_PRUDENTA.lower()
    assert "creștere" in t  # (a) fără așteptări de creștere
    assert "sustenabil" in t  # (b) ajustare de sustenabilitate
    assert "nu poate depăși valoarea de piață" in t  # (c) plafonare


def test_referinta_crr_citeaza_articolele_relevante():
    assert "575" in REFERINTA_CRR
    assert "229" in REFERINTA_CRR
    assert "208" in REFERINTA_CRR


# ── Nota de raport (text + cifre auditabile) ──────────────────────────────────
def test_nota_de_raport_contine_explicatia_si_cifrele():
    p = ParametriValoarePrudenta(discount_crestere_pct=Decimal("10"))
    r = estimeaza_valoare_prudenta(Decimal("500000"), p)
    nota = genereaza_nota_valoare_prudenta(r)
    assert TEXT_EXPLICATIV_VALOARE_PRUDENTA in nota
    assert "450000" in nota  # valoarea prudentă
    assert "500000" in nota  # valoarea de piață
    assert "lei" in nota


def test_rezultatul_este_un_model_pydantic_cu_parametri_atasati():
    p = ParametriValoarePrudenta(haircut_sustenabilitate_pct=Decimal("5"))
    r = estimeaza_valoare_prudenta(Decimal("500000"), p)
    assert isinstance(r, RezultatValoarePrudenta)
    assert r.parametri is p
