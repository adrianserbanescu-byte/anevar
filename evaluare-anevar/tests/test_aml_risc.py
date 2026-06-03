"""Motor de risc AML — scor, categorie, nivel de masuri, reguli HARD (Legea art. 16/17)."""
from evaluare.aml.models import ClientPF, ClientPJ, PersoanaFizica, StatutPEP
from evaluare.aml.risc import (
    Semnale, evalueaza_risc, nivel_masuri, pep_efectiv,
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
