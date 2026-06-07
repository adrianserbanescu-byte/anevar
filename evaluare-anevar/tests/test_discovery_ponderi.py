"""Ponderi config-driven per categorie (P0.1 + P0.2).

P0.1: structura config-driven, casa + restul = modelul de baza (behavior-preserving).
P0.2: APARTAMENTUL are model propriu (promoveaza nr_camere/etaj, fara teren); valorile = propunerea
council, calibrabile de Adi. Casa ramane IDENTICA (golden)."""
from decimal import Decimal

from evaluare.discovery.ponderi import (
    PONDERI_APARTAMENT,
    PONDERI_BAZA,
    PONDERI_PER_CATEGORIE,
    ponderi_pentru,
)
from evaluare.discovery.profiles import CandidateProfile, SubjectProfile
from evaluare.discovery.scoring import metodologie, scor_candidat

NEAPARTAMENT = ["casa", "comercial", "industrial", "agricol", "special"]


def test_categoriile_nonapartament_raman_baza():
    # behavior-preserving: tot ce nu e apartament foloseste modelul casei
    for tip in NEAPARTAMENT:
        assert PONDERI_PER_CATEGORIE[tip] == PONDERI_BAZA, tip


def test_apartament_are_model_propriu():
    p = ponderi_pentru("apartament")
    assert p == PONDERI_APARTAMENT
    assert "nr_camere" in p and "etaj" in p     # atribute promovate la apartament (P0.2)
    assert "teren" not in p                     # terenul nu conteaza la apartament
    assert list(p)[0] == "suprafata_construita"  # ordinea = ordinea de afisare/scorare


def test_ponderi_pentru_default_necunoscut_si_copie():
    assert ponderi_pentru() == PONDERI_BAZA
    assert ponderi_pentru(None) == PONDERI_BAZA
    assert ponderi_pentru("inexistent") == PONDERI_BAZA
    # întoarce o COPIE — mutarea ei nu afectează configul sursă
    p = ponderi_pentru("casa")
    p["an"] = 999
    assert PONDERI_PER_CATEGORIE["casa"]["an"] == 5


def test_scor_casa_behavior_preserving_golden():
    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    candidat = CandidateProfile(an=2008, stare=4, finisaj=4, incalzire="centrala_gaz",
                                teren=None, texte={"an": "2008"})
    b = scor_candidat(subiect, candidat)                 # default = casa
    assert b.relevanta == 86                             # golden — neschimbat de P0.2
    for tip in NEAPARTAMENT:                              # toate non-apartament = identic
        assert scor_candidat(subiect, candidat, ponderi=ponderi_pentru(tip)).relevanta == 86


def test_apartament_scoreaza_nr_camere():
    # apartament: nr_camere intra in scor; potrivire perfecta pe atributele cunoscute -> 100
    subiect = SubjectProfile(suprafata_construita=Decimal("60"), an=2015, stare=4, nr_camere=2)
    candidat = CandidateProfile(suprafata_construita=Decimal("60"), an=2015, stare=4, nr_camere=2)
    b = scor_candidat(subiect, candidat, ponderi=ponderi_pentru("apartament"))
    assert b.relevanta == 100
    camere = next(a for a in b.atribute if a.nume == "Camere")
    assert camere.cunoscut is True and camere.pondere == 4
    # terenul NU apare in scorul apartamentului
    assert all(a.nume != "Teren" for a in b.atribute)


def test_filtru_apartament_plus_minus_1_camera():
    from evaluare.discovery.orchestrator import _apartament_exclus
    assert _apartament_exclus("apartament", 2, 4) is True       # dif 2 -> exclus
    assert _apartament_exclus("apartament", 2, 3) is False      # dif 1 -> ok
    assert _apartament_exclus("apartament", 2, 2) is False      # identic
    assert _apartament_exclus("apartament", None, 4) is False   # subiect necunoscut -> nu filtram
    assert _apartament_exclus("apartament", 2, None) is False   # candidat necunoscut -> nu filtram
    assert _apartament_exclus("casa", 2, 5) is False            # nu se aplica la casa
    assert _apartament_exclus(None, 2, 5) is False


def test_metodologie_apartament_difera_de_casa():
    mc = {r["atribut"] for r in metodologie()}                       # casa (default)
    ma = {r["atribut"] for r in metodologie(ponderi_pentru("apartament"))}
    assert "Teren" in mc and "Teren" not in ma
    assert "Camere" in ma and "Etaj" in ma
    # casa neschimbata (behavior-preserving)
    assert mc == {"Supr. construită", "An", "Stare", "Finisaj", "Încălzire", "Teren"}
