"""Modele AML — KYC, beneficiar real, PEP, evaluare de risc, dosar."""
from decimal import Decimal

from evaluare.aml.models import (
    BeneficiarReal,
    ClientPF,
    ClientPJ,
    DosarAML,
    EvaluareRisc,
    FactorRisc,
    PersoanaFizica,
    StatutPEP,
)


def test_persoana_fizica_minima():
    p = PersoanaFizica(nume="Popescu", prenume="Ion")
    assert p.nume == "Popescu"
    assert p.cnp is None
    assert p.tip_act is None


def test_beneficiar_real_mosteneste_pf_si_are_procent():
    br = BeneficiarReal(
        nume="Ionescu", prenume="Maria", procent=Decimal("0.30"),
        tip_control="proprietate",
    )
    assert isinstance(br, PersoanaFizica)
    assert br.procent == Decimal("0.30")
    assert br.tip_control == "proprietate"
    assert br.consultat_registru_central is False
    assert br.pep.este_pep is False


def test_statut_pep():
    pep = StatutPEP(
        este_pep=True, categorie="parlamentar", tip="titular",
        data_incetare_functie="2025-01-01",
    )
    assert pep.este_pep is True
    assert pep.categorie == "parlamentar"


def test_client_pf_default():
    c = ClientPF(persoana=PersoanaFizica(nume="X", prenume="Y"))
    assert c.tip == "PF"
    assert c.pep.este_pep is False


def test_client_pj_cu_beneficiari():
    c = ClientPJ(
        denumire="ACME SRL", cui="RO123",
        reprezentant_legal=PersoanaFizica(nume="Rep", prenume="Legal"),
        beneficiari_reali=[
            BeneficiarReal(nume="A", prenume="B", procent=Decimal("0.60")),
        ],
    )
    assert c.tip == "PJ"
    assert len(c.beneficiari_reali) == 1
    assert c.traducere_legalizata is False


def test_evaluare_risc_cu_factori():
    er = EvaluareRisc(
        factori=[
            FactorRisc(nume="client", valoare=3, pondere=2),
            FactorRisc(nume="geografic", valoare=1, pondere=1),
        ],
        scor=Decimal("2.3"), categorie="sporit", nivel_masuri="suplimentare",
        motive_sporit=["PEP"],
    )
    assert er.categorie == "sporit"
    assert er.factori[0].nume == "client"
    assert er.nivel_masuri == "suplimentare"


def test_dosar_aml_se_construieste():
    d = DosarAML(
        tip_entitate_evaluator="PFA",
        client_pf=ClientPF(persoana=PersoanaFizica(nume="X", prenume="Y")),
        evaluare_risc=EvaluareRisc(categorie="standard"),
    )
    assert d.tip_entitate_evaluator == "PFA"
    assert d.client_pf is not None
    assert d.client_pj is None
    assert d.evaluare_risc.categorie == "standard"
