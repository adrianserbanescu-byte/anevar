from decimal import Decimal

from evaluare.profil import CASA_TEREN_GARANTARE, ProfilEvaluare


def test_profil_default():
    p = ProfilEvaluare()
    assert p.tip_activ == "casa"
    assert p.scop == "garantare_credit"
    assert p.tip_valoare == "piata"
    assert p.abordari_aplicabile == ["cost", "comparatie"]
    assert p.ghid == "GEV_520"


def test_profil_predefinit_casa_teren():
    assert CASA_TEREN_GARANTARE.tip_activ == "casa"
    assert CASA_TEREN_GARANTARE.ghid == "GEV_520"
    assert "venit" not in CASA_TEREN_GARANTARE.abordari_aplicabile


def test_profil_comercial_cu_venit():
    p = ProfilEvaluare(tip_activ="comercial", ghid="GEV_630",
                       abordari_aplicabile=["venit", "comparatie"],
                       ponderi={"venit": Decimal("0.7"), "comparatie": Decimal("0.3")})
    assert p.tip_activ == "comercial"
    assert p.abordari_aplicabile[0] == "venit"
    assert p.ponderi["venit"] == Decimal("0.7")


def test_sectiuni_per_tip_structura_livrabilului():
    # Structura sectiunilor de raport per tip (vezi SECTIUNI_PER_TIP):
    from evaluare.profil import sectiuni_pentru_tip
    # teren / agricol: fara constructie
    assert sectiuni_pentru_tip("teren").constructie is False
    assert sectiuni_pentru_tip("agricol").constructie is False
    # apartament: fara teren standalone + nota cota indiviza
    assert sectiuni_pentru_tip("apartament").teren_standalone is False
    assert sectiuni_pentru_tip("apartament").nota_cota_indiviza is True
    # comercial: venit principal, costul de regula nu se aplica
    assert sectiuni_pentru_tip("comercial").venit_principal is True
    assert sectiuni_pentru_tip("comercial").abordare_cost is False
    # casa: toate sectiunile (implicit)
    casa = sectiuni_pentru_tip("casa")
    assert casa.constructie is True and casa.teren_standalone is True
    assert casa.nota_cota_indiviza is False and casa.venit_principal is False
    assert casa.abordare_cost is True


def test_sectiuni_pentru_tip_necunoscut_e_implicit():
    # Tip necunoscut/absent -> structura implicita (toate sectiunile), backward-compatible.
    from evaluare.profil import SectiuniTip, sectiuni_pentru_tip
    assert sectiuni_pentru_tip("ceva_inexistent") == SectiuniTip()
    assert sectiuni_pentru_tip(None) == SectiuniTip()
