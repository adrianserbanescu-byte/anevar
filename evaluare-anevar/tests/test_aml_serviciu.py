"""Serviciu AML (evalueaza_relatie) — wiring scop din dosar + avertismente EDD/RBR.

Aditiv, non-blocant: scopul evaluarii intra ca factor de risc „produs/serviciu"; la risc sporit cu EDD
incomplet sau la PJ fara RBR consultat, serviciul intoarce avertismente (om-in-bucla), fara a bloca.
"""
from evaluare.aml.models import (
    BeneficiarReal,
    ClientPF,
    ClientPJ,
    PersoanaFizica,
    StatutPEP,
)
from evaluare.aml.risc import Semnale
from evaluare.aml.serviciu import evalueaza_relatie, scop_aml_din_dosar

AZI = "2026-06-03"


def _pf(nume="Popescu", prenume="Ion", **kw):
    return ClientPF(persoana=PersoanaFizica(nume=nume, prenume=prenume), **kw)


def _pj(**kw):
    kw.setdefault("denumire", "ACME SRL")
    kw.setdefault("reprezentant_legal", PersoanaFizica(nume="Rep", prenume="Legal"))
    return ClientPJ(**kw)


# --------------------------------------------------------------------------- #
# scop_aml_din_dosar — normalizare cod / text liber RO
# --------------------------------------------------------------------------- #
def test_scop_cod_profil_garantare():
    assert scop_aml_din_dosar("garantare_credit") == "garantare_credit"


def test_scop_cod_profil_vanzare_mapat_pe_vanzare_piata():
    assert scop_aml_din_dosar("vanzare") == "vanzare_piata"


def test_scop_text_liber_garantare_credit_ipotecar():
    assert scop_aml_din_dosar("Garantarea creditului ipotecar") == "garantare_credit"


def test_scop_text_liber_lichidare_cu_diacritice():
    assert scop_aml_din_dosar("Lichidare / executare silită") == "lichidare_insolventa_executare"


def test_scop_text_liber_impozitare():
    assert scop_aml_din_dosar("Stabilirea impozitului local") == "impozitare"


def test_scop_necunoscut_sau_gol_e_none():
    assert scop_aml_din_dosar(None) is None
    assert scop_aml_din_dosar("") is None
    assert scop_aml_din_dosar("ceva fara legatura") is None


# --------------------------------------------------------------------------- #
# Propagarea scopului in scor (factorul produs/serviciu)
# --------------------------------------------------------------------------- #
def test_scop_de_risc_ridica_factorul_produs():
    # vanzare_piata -> factor produs/serviciu = 3 (vs neutru fara scop)
    fara = evalueaza_relatie("PFA", _pf(), azi=AZI)
    cu = evalueaza_relatie("PFA", _pf(), azi=AZI, scop="vanzare_piata")
    f_cu = {f["nume"]: f["valoare"] for f in cu["evaluare_risc"]["factori"]}
    f_fara = {f["nume"]: f["valoare"] for f in fara["evaluare_risc"]["factori"]}
    assert f_fara["produs_serviciu"] == 2
    assert f_cu["produs_serviciu"] == 3


def test_scop_redus_coboara_factorul_produs():
    cu = evalueaza_relatie("PFA", _pf(), azi=AZI, scop="garantare_credit")
    f = {x["nume"]: x["valoare"] for x in cu["evaluare_risc"]["factori"]}
    assert f["produs_serviciu"] == 1


def test_semnal_explicit_are_precedenta_fata_de_scop_dosar():
    # Daca semnale_risc.scop e setat explicit, scopul din dosar NU il suprascrie.
    res = evalueaza_relatie(
        "PFA", _pf(), azi=AZI,
        semnale_risc=Semnale(scop="garantare_credit"),  # explicit redus
        scop="vanzare_piata",                           # dosar -> ar ridica
    )
    f = {x["nume"]: x["valoare"] for x in res["evaluare_risc"]["factori"]}
    assert f["produs_serviciu"] == 1  # a castigat semnalul explicit


def test_scop_necunoscut_nu_schimba_comportamentul():
    fara = evalueaza_relatie("PFA", _pf(), azi=AZI)
    cu = evalueaza_relatie("PFA", _pf(), azi=AZI, scop="scop-inexistent")
    assert cu["evaluare_risc"]["factori"] == fara["evaluare_risc"]["factori"]


# --------------------------------------------------------------------------- #
# Avertisment EDD la risc sporit
# --------------------------------------------------------------------------- #
def _pf_pep():
    return _pf(pep=StatutPEP(este_pep=True))


def test_edd_incomplet_la_sporit_pep_da_avertisment():
    res = evalueaza_relatie("PJ", _pf_pep(), azi=AZI)
    assert res["categorie"] == "sporit"
    av = " ".join(res["avertismente"])
    assert "EDD" in av
    assert "sursa fondurilor" in av
    assert "aprobarea conducerii" in av


def test_edd_complet_la_sporit_pep_fara_avertisment_edd():
    res = evalueaza_relatie(
        "PJ", _pf_pep(), azi=AZI,
        sursa_fonduri="salariu + economii", sursa_avere="mostenire",
        aprobare_conducere_pep=True,
    )
    assert res["categorie"] == "sporit"
    assert not any("EDD" in a for a in res["avertismente"])


def test_edd_sporit_fara_pep_nu_cere_aprobare_conducere():
    # sporit din tara risc inalt (nu PEP) -> EDD cere sursa fonduri/avere, NU aprobarea PEP.
    res = evalueaza_relatie(
        "PFA", _pf(), azi=AZI,
        semnale_risc=Semnale(tara_risc_inalt=True),
    )
    assert res["categorie"] == "sporit"
    av = " ".join(res["avertismente"])
    assert "EDD" in av
    assert "aprobarea conducerii" not in av


def test_fara_avertisment_edd_la_risc_standard():
    res = evalueaza_relatie("PFA", _pf(), azi=AZI)
    assert res["categorie"] == "standard"
    assert not any("EDD" in a for a in res["avertismente"])


# --------------------------------------------------------------------------- #
# Avertisment RBR la PJ
# --------------------------------------------------------------------------- #
def test_pj_fara_rbr_da_avertisment():
    res = evalueaza_relatie("PJ", _pj(consultat_rbr=False), azi=AZI)
    assert any("RBR" in a for a in res["avertismente"])


def test_pj_cu_rbr_consultat_fara_avertisment_rbr():
    res = evalueaza_relatie(
        "PJ",
        _pj(consultat_rbr=True, nr_extras_rbr="RBR-123",
            beneficiari_reali=[BeneficiarReal(nume="Be", prenume="Real",
                                              consultat_registru_central=True)]),
        azi=AZI,
    )
    assert not any("RBR" in a for a in res["avertismente"])


def test_pf_nu_primeste_avertisment_rbr():
    res = evalueaza_relatie("PFA", _pf(), azi=AZI)
    assert not any("RBR" in a for a in res["avertismente"])


# --------------------------------------------------------------------------- #
# Backward-compat: cheia avertismente exista mereu; campurile vechi nemodificate
# --------------------------------------------------------------------------- #
def test_rezultatul_pastreaza_cheile_existente_si_adauga_avertismente():
    res = evalueaza_relatie("PFA", _pf(), azi=AZI)
    for cheie in ("categorie", "nivel_masuri", "motive_sporit", "indicatori",
                  "propune_rts", "screening", "documente_necesare"):
        assert cheie in res
    assert isinstance(res["avertismente"], list)
