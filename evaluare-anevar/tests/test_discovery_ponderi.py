"""P0.1 — refactor BEHAVIOR-PRESERVING: ponderile devin config-driven per categorie, dar toate
categoriile = valorile de bază deocamdată → scorurile rămân IDENTICE. Acest test dovedește asta."""
from decimal import Decimal

from evaluare.discovery.ponderi import PONDERI_BAZA, PONDERI_PER_CATEGORIE, ponderi_pentru
from evaluare.discovery.profiles import CandidateProfile, SubjectProfile
from evaluare.discovery.scoring import metodologie, scor_candidat


def test_toate_categoriile_egale_cu_baza():
    # Compromis temporar: orice categorie folosește valorile casei → zero schimbare de comportament.
    for tip, p in PONDERI_PER_CATEGORIE.items():
        assert p == PONDERI_BAZA, f"{tip} diferă de bază (schimbare de comportament neintenționată)"


def test_ponderi_pentru_default_necunoscut_si_copie():
    assert ponderi_pentru() == PONDERI_BAZA
    assert ponderi_pentru(None) == PONDERI_BAZA
    assert ponderi_pentru("inexistent") == PONDERI_BAZA
    assert ponderi_pentru("apartament") == PONDERI_BAZA          # deocamdată identic
    # întoarce o COPIE — mutarea ei nu afectează configul sursă
    p = ponderi_pentru("casa")
    p["an"] = 999
    assert PONDERI_PER_CATEGORIE["casa"]["an"] == 5


def test_scor_identic_indiferent_de_categorie():
    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    candidat = CandidateProfile(an=2008, stare=4, finisaj=4, incalzire="centrala_gaz",
                                teren=None, texte={"an": "2008"})
    baza = scor_candidat(subiect, candidat)                      # default (None → bază)
    assert baza.relevanta == 86                                  # golden — prinde orice deviație
    for tip in PONDERI_PER_CATEGORIE:
        b = scor_candidat(subiect, candidat, ponderi=ponderi_pentru(tip))
        assert b.relevanta == baza.relevanta
        assert b.explicatie == baza.explicatie


def test_metodologie_identica_default_vs_categorie():
    assert metodologie() == metodologie(ponderi=ponderi_pentru("apartament"))
