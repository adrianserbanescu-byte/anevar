from decimal import Decimal
from pathlib import Path

from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.orchestrator import extrage_descriere, descopera

FIXTURES = Path(__file__).parent / "fixtures"


def test_extrage_descriere_include_text():
    html = "<html><head><title>Casa</title></head><body><p>Finisaje de lux, 4 camere.</p></body></html>"
    txt = extrage_descriere(html)
    assert "Finisaje de lux" in txt


def test_descopera_pipeline_complet():
    search_html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    listing_html = (FIXTURES / "imobiliare_listing_nextdata.html").read_text(encoding="utf-8")

    def fetcher(url):
        if "/oferta/" in url:
            return listing_html
        return search_html

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":"2010"},'
                    '"stare":{"treapta":4,"text":"renovat"},'
                    '"finisaj":{"treapta":4,"text":"lux"},'
                    '"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                    '"teren":{"valoare":400,"text":"400"},"secundare":[]}')

    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    rez = descopera("imobiliare", judet="ilfov", localitate="otopeni", subiect=subiect,
                    atribute_secundare=[], fetcher=fetcher, client=FakeClient(),
                    max_candidati=5)
    assert len(rez) == 3
    assert all(r.breakdown.relevanta > 0 for r in rez)
    relev = [r.breakdown.relevanta for r in rez]
    assert relev == sorted(relev, reverse=True)
    assert rez[0].pret == Decimal("249900")
    assert rez[0].suprafata == Decimal("130")
