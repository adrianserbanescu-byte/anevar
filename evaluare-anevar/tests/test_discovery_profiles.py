from decimal import Decimal

from evaluare.discovery.profiles import (
    SubjectProfile,
    CandidateProfile,
    AttributeBreakdown,
    ScoreBreakdown,
)


def test_subject_profile_optional_fields():
    s = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                       teren=Decimal("500"))
    assert s.an == 2013
    assert s.teren == Decimal("500")
    s2 = SubjectProfile()
    assert s2.an is None


def test_candidate_profile_holds_raw_texts():
    c = CandidateProfile(an=2008, stare=4, finisaj=4, incalzire="centrala_gaz",
                         teren=None, texte={"an": "2008", "stare": "renovat 2021"})
    assert c.an == 2008
    assert c.teren is None
    assert c.texte["stare"] == "renovat 2021"


def test_breakdown_structures():
    ab = AttributeBreakdown(nume="An", valoare_subiect="2013", valoare_candidat="2008",
                            d=0.2, pondere=5, contributie=1.0, cunoscut=True)
    assert ab.contributie == 1.0
    sb = ScoreBreakdown(relevanta=86, dissimilaritate=0.143, atribute=[ab],
                        atribute_cunoscute=4, incredere_scazuta=False,
                        explicatie="Relevanță 86% = ...")
    assert sb.relevanta == 86
    assert sb.atribute[0].nume == "An"
