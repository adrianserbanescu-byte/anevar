"""Motor de risc AML — scor, categorie, nivel de masuri, reguli HARD (Legea art. 16/17)."""
from evaluare.aml.models import ClientPF, ClientPJ, PersoanaFizica, StatutPEP
from evaluare.aml.risc import (
    Semnale,
    evalueaza_risc,
    nivel_masuri,
    pep_efectiv,
)


def _client_simplu():
    return ClientPF(persoana=PersoanaFizica(nume="Popescu", prenume="Ion"))


# --------------------------------------------------------------------------- #
# pep_efectiv
# --------------------------------------------------------------------------- #
def test_pep_efectiv_titular_activ():
    assert pep_efectiv(StatutPEP(este_pep=True), azi="2026-06-03") is True


def test_pep_efectiv_in_12_luni_de_la_incetare():
    pep = StatutPEP(este_pep=True, data_incetare_functie="2026-01-01")
    assert pep_efectiv(pep, azi="2026-06-03") is True   # ~5 luni


def test_pep_neefectiv_dupa_12_luni():
    pep = StatutPEP(este_pep=True, data_incetare_functie="2024-01-01")
    assert pep_efectiv(pep, azi="2026-06-03") is False  # >12 luni


def test_pep_neefectiv_daca_nu_e_pep():
    assert pep_efectiv(StatutPEP(este_pep=False), azi="2026-06-03") is False


# --------------------------------------------------------------------------- #
# nivel_masuri
# --------------------------------------------------------------------------- #
def test_nivel_masuri_pe_categorie():
    assert nivel_masuri("redus") == "simplificate"
    assert nivel_masuri("standard") == "standard"
    assert nivel_masuri("sporit") == "suplimentare"


# --------------------------------------------------------------------------- #
# evalueaza_risc — categorii
# --------------------------------------------------------------------------- #
def test_client_normal_standard():
    er = evalueaza_risc(_client_simplu(), Semnale(), azi="2026-06-03")
    assert er.categorie == "standard"
    assert er.nivel_masuri == "standard"


def test_risc_redus_da_sdd():
    er = evalueaza_risc(
        _client_simplu(),
        Semnale(client_cunoscut=True, tranzactie_uzuala=True, canal_fata_in_fata=True,
                tara_risc_redus=True),
        azi="2026-06-03",
    )
    assert er.categorie == "redus"
    assert er.nivel_masuri == "simplificate"


def test_pep_forteaza_sporit_si_edd():
    c = ClientPF(persoana=PersoanaFizica(nume="X", prenume="Y"),
                 pep=StatutPEP(este_pep=True))
    er = evalueaza_risc(c, Semnale(), azi="2026-06-03")
    assert er.categorie == "sporit"
    assert er.nivel_masuri == "suplimentare"
    assert any("PEP" in m for m in er.motive_sporit)


def test_tara_risc_inalt_forteaza_sporit():
    er = evalueaza_risc(_client_simplu(), Semnale(tara_risc_inalt=True), azi="2026-06-03")
    assert er.categorie == "sporit"
    assert any("risc înalt" in m or "risc inalt" in m for m in er.motive_sporit)


def test_lista_sanctiuni_forteaza_sporit():
    er = evalueaza_risc(_client_simplu(), Semnale(pe_lista_sanctiuni=True), azi="2026-06-03")
    assert er.categorie == "sporit"


def test_tranzactie_complexa_forteaza_sporit():
    er = evalueaza_risc(_client_simplu(), Semnale(tranzactie_complexa=True), azi="2026-06-03")
    assert er.categorie == "sporit"


def test_beneficiar_real_pep_forteaza_sporit():
    from evaluare.aml.models import BeneficiarReal
    c = ClientPJ(
        denumire="ACME SRL",
        beneficiari_reali=[
            BeneficiarReal(nume="A", prenume="B", pep=StatutPEP(este_pep=True)),
        ],
    )
    er = evalueaza_risc(c, Semnale(), azi="2026-06-03")
    assert er.categorie == "sporit"


def test_evaluare_risc_seteaza_factori_si_data_reevaluare():
    er = evalueaza_risc(_client_simplu(), Semnale(), azi="2026-06-03")
    assert len(er.factori) == 4
    assert er.data == "2026-06-03"
    assert er.data_reevaluare is not None and er.data_reevaluare > er.data


# --------------------------------------------------------------------------- #
# Graniste (mutation testing lane B — risc.py era 33%): _luni_intre, praguri, reevaluare
# --------------------------------------------------------------------------- #
def test_luni_intre_exact_la_granita():
    from evaluare.aml.risc import _luni_intre
    assert _luni_intre("2024-06-10", "2026-08-20") == 26   # 2*12 + 2 (kills *12->/12, an Add->Sub)
    assert _luni_intre("2025-01-15", "2026-01-10") == 11   # 12 + 0, ziua 10<15 -> -1 (kills Lt->Gt, -=1)
    assert _luni_intre("2025-06-10", "2025-08-20") == 2    # acelasi an
    assert _luni_intre("2026-03-15", "2026-03-15") == 0    # acelasi punct


def test_pep_efectiv_la_granita_de_12_luni():
    pep11 = StatutPEP(este_pep=True, data_incetare_functie="2025-07-10")
    assert pep_efectiv(pep11, azi="2026-06-15") is True    # 11 luni (< 12) -> efectiv
    pep13 = StatutPEP(este_pep=True, data_incetare_functie="2025-05-10")
    assert pep_efectiv(pep13, azi="2026-06-15") is False   # 13 luni (>= 12) -> neefectiv


def _ev(**semnale):
    return evalueaza_risc(_client_simplu(), Semnale(**semnale), azi="2026-06-15")


def test_categorie_pe_scor_si_granita_redus_standard():
    from decimal import Decimal
    r0 = _ev(client_cunoscut=True, tranzactie_uzuala=True,
             canal_fata_in_fata=True, tara_risc_redus=True)              # toate 1
    assert r0.scor == Decimal("1.0") and r0.categorie == "redus"
    r1 = _ev(client_cunoscut=True, tara_risc_redus=True)                 # (1*2+2+2+1*2)/6 = 1.333...
    assert r1.categorie == "redus"                                       # <= 1.4
    r2 = _ev(tranzactie_uzuala=True, canal_fata_in_fata=True)            # (2*2+1+1+2*2)/6 = 1.666...
    assert r2.categorie == "standard"                                    # > 1.4 (kills pragul 1.4)
    r3 = _ev()                                                           # toate default 2 -> 2.0
    assert r3.scor == Decimal("2.0") and r3.categorie == "standard"


def test_sanctiuni_forteaza_sporit_si_factor_client_3():
    from decimal import Decimal
    # pe lista de sanctiuni (NU PEP) -> regula HARD 'sporit' + f_client=3 (kills L92 Or->And, f=3)
    r = _ev(pe_lista_sanctiuni=True)
    assert r.categorie == "sporit" and r.motive_sporit
    # scor cu f_client=3, restul default 2: (3*2+2+2+2*2)/6 = 14/6 = 2.333...
    assert r.scor == Decimal("14") / Decimal("6")


def test_data_reevaluare_pe_categorie():
    # data_reevaluare = azi + _LUNI_REEVALUARE[categorie] (redus 36 / standard 24 / sporit 12)
    redus = _ev(client_cunoscut=True, tranzactie_uzuala=True,
                canal_fata_in_fata=True, tara_risc_redus=True)
    assert redus.data_reevaluare == "2029-06-15"            # +36 luni (kills _adauga_luni + const 36)
    standard = _ev()
    assert standard.data_reevaluare == "2028-06-15"         # +24 luni
    sporit = _ev(pe_lista_sanctiuni=True)
    assert sporit.data_reevaluare == "2027-06-15"           # +12 luni (kills const 12 L25)


def test_scor_fiecare_factor_sporit_contribuie_3():
    # fiecare semnal 'sporit' (produs/canal/geo) contribuie f=3 la SCOR, chiar daca regula HARD forteaza
    # categoria sporit (scorul ramane informativ). Acopera valorile-factor 3 (mascate de HARD in categorie).
    from decimal import Decimal
    assert _ev(tranzactie_complexa=True).scor == Decimal("13") / Decimal("6")   # produs=3: (2*2+3+2+2*2)/6
    assert _ev(canal_la_distanta=True).scor == Decimal("13") / Decimal("6")     # canal=3
    assert _ev(tara_risc_inalt=True).scor == Decimal("14") / Decimal("6")       # geo=3 (pondere 2)
