from evaluare.profil import CASA_TEREN_GARANTARE, ProfilEvaluare
from evaluare.report.sectiuni import sectiuni_pentru_profil, ID_SECTIUNI


def test_casa_teren_garantare_are_gev520_fara_venit():
    ids = sectiuni_pentru_profil(CASA_TEREN_GARANTARE)
    assert "coperta" in ids
    assert "gev_520" in ids
    assert "abordare_venit" not in ids


def test_comercial_gev630_are_venit_fara_gev520():
    p = ProfilEvaluare(tip_activ="comercial", ghid="GEV_630",
                       abordari_aplicabile=["venit", "comparatie"])
    ids = sectiuni_pentru_profil(p)
    assert "abordare_venit" in ids
    assert "gev_520" not in ids


def test_toate_id_urile_sunt_unice():
    assert len(ID_SECTIUNI) == len(set(ID_SECTIUNI))


def test_sectiunile_de_abordare_urmeaza_abordarile_din_profil():
    ids = sectiuni_pentru_profil(CASA_TEREN_GARANTARE)
    assert "abordare_cost" in ids and "abordare_comparatie" in ids
    p = ProfilEvaluare(tip_activ="comercial", ghid="GEV_630",
                       abordari_aplicabile=["venit", "comparatie"])
    ids2 = sectiuni_pentru_profil(p)
    assert "abordare_venit" in ids2 and "abordare_comparatie" in ids2
    assert "abordare_cost" not in ids2
