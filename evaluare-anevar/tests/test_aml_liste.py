"""Liste externe injectabile + screening tolerant (diacritice + similaritate)."""
from evaluare.aml.liste import Liste, este_tara_risc, incarca_liste, screening


def test_screening_potrivire_exacta():
    liste = Liste(sanctiuni=["Ion Popescu"])
    rez = screening("Ion Popescu", liste)
    assert len(rez) == 1
    assert rez[0].lista == "sancțiuni"
    assert rez[0].scor >= 0.99


def test_screening_tolerant_la_diacritice():
    liste = Liste(sanctiuni=["Ștefan Mărginean"])
    rez = screening("Stefan Marginean", liste)
    assert len(rez) == 1


def test_screening_fara_potrivire():
    liste = Liste(sanctiuni=["Cineva Altcineva"])
    assert screening("Ion Popescu", liste) == []


def test_screening_nume_gol():
    assert screening("", Liste(sanctiuni=["X"])) == []


def test_tara_risc():
    liste = Liste(tari_risc_inalt=["Coreea de Nord"], tari_necooperante=[])
    r = este_tara_risc("coreea de nord", liste)
    assert r["risc_inalt"] is True
    assert r["necooperanta"] is False


def test_incarca_liste_din_pachet():
    # fisierul placeholder din pachet exista si se incarca
    liste = incarca_liste()
    assert isinstance(liste, Liste)
    assert liste.actualizat is not None
    assert "Iran" in liste.tari_risc_inalt


def test_incarca_liste_dir_inexistent(tmp_path):
    liste = incarca_liste(tmp_path / "nimic")
    assert liste.sanctiuni == [] and liste.pep_functii == []
