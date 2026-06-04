from decimal import Decimal

from evaluare.discovery.profiles import CandidateProfile, ScoreBreakdown
from evaluare.discovery.results import (
    CandidateExtraction,
    CandidateResult,
    SecondaryAttributeResult,
)


def test_secondary_result():
    s = SecondaryAttributeResult(nume="tamplarie", stare="diferit",
                                 valoare_gasita="lemn stratificat")
    assert s.stare == "diferit"


def test_candidate_extraction():
    e = CandidateExtraction(profile=CandidateProfile(an=2008),
                            secundare=[SecondaryAttributeResult(nume="garaj",
                                       stare="potrivit", valoare_gasita="da")])
    assert e.profile.an == 2008
    assert e.secundare[0].nume == "garaj"


def test_candidate_result():
    b = ScoreBreakdown(relevanta=86, dissimilaritate=0.143, atribute=[],
                       atribute_cunoscute=4, incredere_scazuta=False, explicatie="...")
    r = CandidateResult(url="https://x", titlu="Casa", pret=Decimal("250000"),
                        suprafata=Decimal("180"), breakdown=b, secundare=[])
    assert r.pret == Decimal("250000")
    assert r.breakdown.relevanta == 86
