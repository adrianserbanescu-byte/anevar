from evaluare.profil import SPECIAL


def test_profil_special():
    assert SPECIAL.tip_activ == "special"
    assert SPECIAL.ghid == "GEV_630"
    assert "venit" in SPECIAL.abordari_aplicabile
