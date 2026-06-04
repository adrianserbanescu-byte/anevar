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
