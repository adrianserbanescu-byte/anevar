from evaluare.profil import APARTAMENT_GARANTARE


def test_profil_apartament():
    assert APARTAMENT_GARANTARE.tip_activ == "apartament"
    assert APARTAMENT_GARANTARE.scop == "garantare_credit"
    assert APARTAMENT_GARANTARE.ghid == "GEV_520"
    assert APARTAMENT_GARANTARE.abordari_aplicabile == ["comparatie", "cost"]
