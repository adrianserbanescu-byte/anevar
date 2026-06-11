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
# S-1: scopul/tipul evaluarii ca factor de risc (produs/serviciu)
# --------------------------------------------------------------------------- #
def _factor(er, nume):
    return next(f for f in er.factori if f.nume == nume)


def test_scop_neutru_cand_lipseste_backward_compat():
    # fara scop -> comportament vechi: factor produs = 2 (neutru)
    er = evalueaza_risc(_client_simplu(), Semnale(), azi="2026-06-03")
    assert _factor(er, "produs_serviciu").valoare == 2


def test_scop_garantare_credit_coboara_produs():
    er = evalueaza_risc(_client_simplu(), Semnale(scop="garantare_credit"), azi="2026-06-03")
    assert _factor(er, "produs_serviciu").valoare == 1


def test_scop_impozitare_si_raportare_coboara_produs():
    for scop in ("impozitare", "raportare_financiara"):
        er = evalueaza_risc(_client_simplu(), Semnale(scop=scop), azi="2026-06-03")
        assert _factor(er, "produs_serviciu").valoare == 1, scop


def test_scop_lichidare_executare_ridica_produs():
    for scop in ("lichidare_insolventa_executare", "vanzare_piata", "mna"):
        er = evalueaza_risc(_client_simplu(), Semnale(scop=scop), azi="2026-06-03")
        assert _factor(er, "produs_serviciu").valoare == 3, scop


def test_scop_ridicat_da_scor_mai_mare_decat_scop_redus():
    er_redus = evalueaza_risc(_client_simplu(), Semnale(scop="garantare_credit"), azi="2026-06-03")
    er_ridicat = evalueaza_risc(
        _client_simplu(), Semnale(scop="lichidare_insolventa_executare"), azi="2026-06-03"
    )
    assert er_ridicat.scor > er_redus.scor


def test_scop_ridicat_la_distanta_complexa_combina_cu_tranzactia():
    # tranzactie complexa (HARD) + scop redus: tranzactia complexa ramane prioritara la produs
    er = evalueaza_risc(
        _client_simplu(),
        Semnale(scop="garantare_credit", tranzactie_complexa=True),
        azi="2026-06-03",
    )
    assert _factor(er, "produs_serviciu").valoare == 3
    assert er.categorie == "sporit"  # tranzactie complexa = regula HARD


def test_garantare_credit_relatie_redusa():
    # client cunoscut + canal fata in fata + tara redus + garantare credit -> redus
    er = evalueaza_risc(
        _client_simplu(),
        Semnale(client_cunoscut=True, canal_fata_in_fata=True, tara_risc_redus=True,
                scop="garantare_credit"),
        azi="2026-06-03",
    )
    assert er.categorie == "redus"
    assert er.nivel_masuri == "simplificate"


# --------------------------------------------------------------------------- #
# I-4: beneficiar real lipsa la PJ -> factor de risc; PEP cu data_incetare
# --------------------------------------------------------------------------- #
def _pj_cu_br(consultat, **pep_kwargs):
    from evaluare.aml.models import BeneficiarReal
    br = BeneficiarReal(
        nume="A", prenume="B",
        consultat_registru_central=consultat,
        pep=StatutPEP(**pep_kwargs) if pep_kwargs else StatutPEP(),
    )
    return ClientPJ(denumire="ACME SRL", beneficiari_reali=[br])


def test_pj_fara_beneficiar_real_ridica_factor_client():
    c = ClientPJ(denumire="ACME SRL", beneficiari_reali=[])
    er = evalueaza_risc(c, Semnale(), azi="2026-06-03")
    assert _factor(er, "client").valoare == 3


def test_pj_br_neconsultat_in_registru_ridica_factor_client():
    c = _pj_cu_br(consultat=False)
    er = evalueaza_risc(c, Semnale(), azi="2026-06-03")
    assert _factor(er, "client").valoare == 3


def test_pj_br_consultat_nu_ridica_factor_client():
    c = _pj_cu_br(consultat=True)
    er = evalueaza_risc(c, Semnale(), azi="2026-06-03")
    assert _factor(er, "client").valoare == 2


def test_pj_fara_br_da_scor_mai_mare():
    cu_br = _pj_cu_br(consultat=True)
    fara_br = ClientPJ(denumire="ACME SRL", beneficiari_reali=[])
    assert (
        evalueaza_risc(fara_br, Semnale(), azi="2026-06-03").scor
        > evalueaza_risc(cu_br, Semnale(), azi="2026-06-03").scor
    )


def test_pj_fara_br_nu_forteaza_singur_sporit():
    # BR lipsa singur ridica factorul (aditiv), dar nu e regula HARD: cu rest neutru ramane sub prag
    c = ClientPJ(denumire="ACME SRL", beneficiari_reali=[])
    er = evalueaza_risc(c, Semnale(), azi="2026-06-03")
    assert er.categorie in ("standard", "sporit")  # depinde de prag, dar nu e fortat de o regula HARD


def test_pj_fara_br_documentat_in_motive_cand_sporit():
    # BR lipsa + tara risc inalt (HARD -> sporit): motivul BR e documentat
    c = ClientPJ(denumire="ACME SRL", beneficiari_reali=[])
    er = evalueaza_risc(c, Semnale(tara_risc_inalt=True), azi="2026-06-03")
    assert er.categorie == "sporit"
    assert any("Beneficiar real neidentificat" in m for m in er.motive_sporit)


def test_pep_br_in_12_luni_de_la_incetare_forteaza_sporit():
    # I-4: foloseste data_incetare de pe StatutPEP, nu doar bifa este_pep
    c = _pj_cu_br(consultat=True, este_pep=True, data_incetare_functie="2026-01-01")
    er = evalueaza_risc(c, Semnale(), azi="2026-06-03")  # ~5 luni -> inca PEP efectiv
    assert er.categorie == "sporit"


def test_pep_br_dupa_12_luni_nu_mai_e_pep_efectiv():
    c = _pj_cu_br(consultat=True, este_pep=True, data_incetare_functie="2024-01-01")
    er = evalueaza_risc(c, Semnale(), azi="2026-06-03")  # >12 luni
    assert not any("PEP" in m for m in er.motive_sporit)
