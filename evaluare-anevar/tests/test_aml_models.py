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


# ---------------------------------------------------------------------------
# S-2 EDD — sursa fonduri/avere, aprobare conducere PEP, monitorizare sporita
# Toate OPTIONALE (default None/False) -> backward-compatible.
# ---------------------------------------------------------------------------

def test_dosar_aml_edd_default_optionale():
    """Campurile EDD lipsesc din constructiile vechi -> default None/False."""
    d = DosarAML(tip_entitate_evaluator="PFA")
    assert d.sursa_fonduri is None
    assert d.sursa_avere is None
    assert d.aprobare_conducere_superioara_pep is False
    assert d.monitorizare_sporita is False


def test_dosar_aml_edd_completat():
    d = DosarAML(
        tip_entitate_evaluator="PJ",
        sursa_fonduri="Vanzare imobil anterior + economii",
        sursa_avere="Activitate antreprenoriala 2005-2020",
        aprobare_conducere_superioara_pep=True,
        monitorizare_sporita=True,
    )
    assert d.sursa_fonduri.startswith("Vanzare")
    assert d.sursa_avere.startswith("Activitate")
    assert d.aprobare_conducere_superioara_pep is True
    assert d.monitorizare_sporita is True


# ---------------------------------------------------------------------------
# S-3 RBR — consultat_rbr + nr/data extras, pe ClientPJ.
# ---------------------------------------------------------------------------

def test_client_pj_rbr_default_optional():
    """ClientPJ vechi (fara RBR) ramane valid -> default False/None."""
    c = ClientPJ(denumire="ACME SRL", cui="RO123")
    assert c.consultat_rbr is False
    assert c.nr_extras_rbr is None
    assert c.data_extras_rbr is None


def test_client_pj_rbr_completat():
    c = ClientPJ(
        denumire="ACME SRL", cui="RO123",
        consultat_rbr=True,
        nr_extras_rbr="RBR-2026-001",
        data_extras_rbr="2026-06-11",
    )
    assert c.consultat_rbr is True
    assert c.nr_extras_rbr == "RBR-2026-001"
    assert c.data_extras_rbr == "2026-06-11"


# ---------------------------------------------------------------------------
# I-4 — modalitate_identificare pe BeneficiarReal (optionala).
# ---------------------------------------------------------------------------

def test_beneficiar_real_modalitate_identificare_default():
    br = BeneficiarReal(nume="A", prenume="B")
    assert br.modalitate_identificare is None


def test_beneficiar_real_modalitate_identificare_setata():
    br = BeneficiarReal(
        nume="A", prenume="B", procent=Decimal("0.40"),
        modalitate_identificare="extras_rbr",
    )
    assert br.modalitate_identificare == "extras_rbr"


# ---------------------------------------------------------------------------
# StatutPEP — categorie/tip/data_incetare deja exista; verificam ca nu s-a stricat.
# ---------------------------------------------------------------------------

def test_statut_pep_are_categorie_tip_data_incetare():
    pep = StatutPEP(
        este_pep=True, categorie="sef_stat_guvern", tip="membru_familie",
        data_incetare_functie="2024-12-31",
    )
    assert pep.categorie == "sef_stat_guvern"
    assert pep.tip == "membru_familie"
    assert pep.data_incetare_functie == "2024-12-31"


def test_statut_pep_default_gol_ramane_valid():
    """Constructie minima (doar este_pep) — backward-compatible."""
    pep = StatutPEP()
    assert pep.este_pep is False
    assert pep.categorie is None
    assert pep.tip is None
    assert pep.data_incetare_functie is None


# ---------------------------------------------------------------------------
# Backward-compat global: constructiile existente (fara campuri noi) neafectate.
# ---------------------------------------------------------------------------

def test_backward_compat_constructii_minime():
    """Niciun camp nou nu e obligatoriu -> modelele se construiesc fara argumente."""
    assert DosarAML().sursa_fonduri is None
    assert ClientPJ().consultat_rbr is False
    assert BeneficiarReal().modalitate_identificare is None
