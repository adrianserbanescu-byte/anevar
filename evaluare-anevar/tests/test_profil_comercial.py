from evaluare.profil import COMERCIAL_INCHIRIAT


def test_profil_comercial():
    assert COMERCIAL_INCHIRIAT.tip_activ == "comercial"
    assert COMERCIAL_INCHIRIAT.ghid == "GEV_630"
    assert COMERCIAL_INCHIRIAT.abordari_aplicabile == ["venit", "comparatie"]
