from decimal import Decimal

from evaluare.discovery.profiles import SubjectProfile, CandidateProfile
from evaluare.discovery.scoring import (
    d_an, d_stare, d_finisaj, d_incalzire, d_teren, PONDERI, scor_candidat,
)


def test_d_an():
    assert d_an(2013, 2008) == 0.2
    assert d_an(2013, 2013) == 0.0
    assert d_an(2013, 1900) == 1.0      # cap la 1


def test_d_stare_si_finisaj():
    assert d_stare(3, 4) == 0.25        # |3-4|/4
    assert d_finisaj(2, 4) == round(2/3, 4)


def test_d_incalzire():
    assert d_incalzire("centrala_gaz", "centrala_gaz") == 0.0
    assert d_incalzire("centrala_gaz", "centrala_lemn") == 0.5   # aceeasi familie
    assert d_incalzire("centrala_gaz", "sobe") == 1.0


def test_d_teren():
    assert d_teren(Decimal("500"), Decimal("450")) == 0.1
    assert d_teren(Decimal("500"), Decimal("0")) == 1.0


def test_ponderi():
    assert PONDERI == {"suprafata_construita": 5, "an": 5, "stare": 4,
                       "finisaj": 3, "incalzire": 2, "teren": 1}


def test_suprafata_construita_intra_in_scor():
    from evaluare.discovery.scoring import d_suprafata
    assert d_suprafata(Decimal("120"), Decimal("108")) == 0.1
    subiect = SubjectProfile(suprafata_construita=Decimal("120"), an=2013)
    candidat = CandidateProfile(suprafata_construita=Decimal("120"), an=2013)
    b = scor_candidat(subiect, candidat)
    # potrivire perfecta pe ambele -> relevanta 100, ambele cunoscute
    assert b.relevanta == 100
    supr = next(a for a in b.atribute if a.nume == "Supr. construită")
    assert supr.cunoscut is True
    assert supr.pondere == 5


def test_scor_candidat_exemplul_din_spec_86():
    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    candidat = CandidateProfile(an=2008, stare=4, finisaj=4, incalzire="centrala_gaz",
                                teren=None,
                                texte={"an": "2008", "stare": "renovat 2021",
                                       "finisaj": "lux", "incalzire": "centrala gaz"})
    b = scor_candidat(subiect, candidat)
    assert b.relevanta == 86
    assert b.atribute_cunoscute == 4
    assert b.incredere_scazuta is False
    teren = next(a for a in b.atribute if a.nume == "Teren")
    assert teren.cunoscut is False
    assert teren.contributie is None
    assert "86%" in b.explicatie
    assert "5×0.20" in b.explicatie or "5*0.20" in b.explicatie
    assert "(5+4+3+2)" in b.explicatie


def test_incredere_scazuta_cand_3_din_5_lipsesc():
    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    candidat = CandidateProfile(an=2008, stare=4)   # finisaj, incalzire, teren lipsesc
    b = scor_candidat(subiect, candidat)
    assert b.incredere_scazuta is True
    assert b.atribute_cunoscute == 2
