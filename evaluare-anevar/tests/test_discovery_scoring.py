from decimal import Decimal

from evaluare.discovery.profiles import CandidateProfile, SubjectProfile
from evaluare.discovery.scoring import (
    PONDERI,
    d_an,
    d_finisaj,
    d_incalzire,
    d_stare,
    d_teren,
    scor_candidat,
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


# ── Ajustari metodologice ADITIVE (recenta / proximitate / segment) ──────────────────────────

def _perfect():
    """Subiect+candidat identici pe atribute → relevanta de atribute = 100 (baza de la care
    se vad ajustarile in clar)."""
    s = SubjectProfile(suprafata_construita=Decimal("120"), an=2013, stare=3, finisaj=4,
                       incalzire="centrala_gaz", teren=Decimal("500"))
    c = CandidateProfile(suprafata_construita=Decimal("120"), an=2013, stare=3, finisaj=4,
                         incalzire="centrala_gaz", teren=Decimal("500"))
    return s, c


def test_fara_semnale_relevanta_identica_si_relevanta_atribute_egala():
    """BACKWARD-COMPAT: fara recenta/proximitate/segment, scorul e identic cu cel istoric."""
    s, c = _perfect()
    b = scor_candidat(s, c)
    assert b.relevanta == 100
    assert b.relevanta_atribute == 100      # campul nou e populat, dar egal cu relevanta
    assert b.ajustari == []                  # nicio ajustare aplicata


def test_recenta_anunt_proaspat_nu_penalizeaza():
    s, c = _perfect()
    c.vechime_zile = 90                      # sub pragul de gratie (~6 luni)
    b = scor_candidat(s, c)
    assert b.relevanta == 100
    assert b.ajustari == []


def test_recenta_anunt_vechi_penalizeaza_relevanta():
    s, c = _perfect()
    c.vechime_zile = 540                     # la pragul maxim → penalizare maxima (30%)
    b = scor_candidat(s, c)
    assert b.relevanta_atribute == 100
    assert b.relevanta == 70                 # 100 * (1 - 0.30)
    assert any("recență" in a for a in b.ajustari)
    assert "Ajustări metodologice" in b.explicatie


def test_proximitate_aproape_nu_penalizeaza_departe_da():
    s, c = _perfect()
    c.distanta_km = 0.5                      # <1 km: aceeasi micro-piata
    assert scor_candidat(s, c).relevanta == 100
    c.distanta_km = 15.0                     # la pragul maxim → penalizare maxima (35%)
    b = scor_candidat(s, c)
    assert b.relevanta == 65                 # 100 * (1 - 0.35)
    assert any("proximitate" in a for a in b.ajustari)


def test_segment_exact_da_bonus_capat_la_100():
    s, c = _perfect()
    s.segment = "rezidential_premium"
    c.segment = "Rezidential_Premium"        # match exact (case-insensitive)
    b = scor_candidat(s, c)
    # bonus +5% dar relevanta de atribute deja 100 → plafonata la 100
    assert b.relevanta == 100
    assert any("segment exact" in a for a in b.ajustari)


def test_segment_exact_bonus_vizibil_sub_100():
    s = SubjectProfile(an=2013, stare=3, segment="rezidential")
    c = CandidateProfile(an=2008, stare=3, segment="rezidential")   # an difera putin
    b = scor_candidat(s, c)
    assert b.relevanta == min(100, round(b.relevanta_atribute * 1.05))
    assert b.relevanta >= b.relevanta_atribute


def test_segment_diferit_penalizeaza():
    s, c = _perfect()
    s.segment = "rezidential"
    c.segment = "comercial"                  # alta sub-piata (capcana (d))
    b = scor_candidat(s, c)
    assert b.relevanta == 80                 # 100 * (1 - 0.20)
    assert any("segment diferit" in a for a in b.ajustari)


def test_ajustari_se_combina_multiplicativ():
    s, c = _perfect()
    c.vechime_zile = 540                     # factor 0.70 (recenta maxima)
    c.distanta_km = 15.0                     # factor 0.65 (proximitate maxima)
    b = scor_candidat(s, c)
    # 100 * 0.70 * 0.65 = 45.5 → ~45 (rotunjire la limita de .5; ambii factori se aplica)
    assert b.relevanta in (45, 46)
    assert b.relevanta < 70                  # strict mai mic decat o singura ajustare de recenta
    assert len(b.ajustari) == 2


def test_ajustari_nu_scad_sub_zero():
    s = SubjectProfile(an=1900, stare=1, finisaj=1, segment="rezidential")
    c = CandidateProfile(an=2024, stare=5, finisaj=4, segment="comercial",
                         vechime_zile=540, distanta_km=15.0)
    b = scor_candidat(s, c)
    assert 0 <= b.relevanta <= 100
