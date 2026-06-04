from evaluare.profil import ASIGURARE, IMPOZITARE, LITIGII, RAPORTARE_FINANCIARA


def test_raportare_financiara():
    assert RAPORTARE_FINANCIARA.scop == "raportare_financiara"
    assert RAPORTARE_FINANCIARA.tip_valoare == "justa"
    assert RAPORTARE_FINANCIARA.ghid == "GEV_500"


def test_asigurare():
    assert ASIGURARE.scop == "asigurare"
    assert ASIGURARE.tip_valoare == "asigurare"


def test_impozitare():
    assert IMPOZITARE.scop == "impozitare"


def test_litigii():
    assert LITIGII.scop == "litigii"
