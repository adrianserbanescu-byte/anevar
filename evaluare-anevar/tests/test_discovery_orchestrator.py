from decimal import Decimal
from pathlib import Path

from evaluare.discovery.orchestrator import descopera, extrage_descriere
from evaluare.discovery.profiles import SubjectProfile

FIXTURES = Path(__file__).parent / "fixtures"


def test_extrage_descriere_include_text():
    html = "<html><head><title>Casa</title></head><body><p>Finisaje de lux, 4 camere.</p></body></html>"
    txt = extrage_descriere(html)
    assert "Finisaje de lux" in txt


def test_extrage_descriere_din_nextdata_storia():
    # storia: descrierea bogata (cu specs) e in __NEXT_DATA__ ad.description, NU in body randat
    desc = ("Casa in Breaza, deschidere la strada 30 m. Suprafata utila 180 mp, amprenta la sol "
            "100 mp, desfasurata 220 mp. Regim inaltime P+2E+M. Pereti tip sandwich, fundatie beton, "
            "acoperis tabla. Incalzire centrala gaz Ariston. An constructie 2010.")
    html = ('<html><head><title>Casa Breaza</title></head><body>'
            '<p>chrome si footer fara specs</p>'
            f'<script id="__NEXT_DATA__" type="application/json">'
            f'{{"props":{{"pageProps":{{"ad":{{"description":"<p>{desc}</p>"}}}}}}}}</script>'
            '</body></html>')
    txt = extrage_descriere(html)
    assert "P+2E+M" in txt
    assert "sandwich" in txt
    assert "180 mp" in txt
    assert "footer fara specs" not in txt   # NU mai luam corpul randat sarac


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
    assert rez[0].teren == Decimal("400")   # terenul e propagat in rezultat (afisare)


def test_build_search_url_teren():
    from evaluare.discovery.portal_search import build_search_url
    u = build_search_url("imobiliare", "Prahova", "Breaza", categorie="teren")
    assert "vanzare-terenuri/judetul-prahova/breaza" in u
    s = build_search_url("storia", "Prahova", "", categorie="teren")
    assert "rezultate/vanzare/teren/prahova" in s


def test_descopera_teren_pipeline():
    from decimal import Decimal

    from evaluare.discovery.orchestrator import descopera_teren
    search = '<html><body><a href="/oferta/teren-breaza-1">t1</a></body></html>'
    listing = ('<html><head><title>Teren Breaza 1000 mp</title>'
               '<script type="application/ld+json">'
               '{"@type":"Offer","price":"50000","priceCurrency":"EUR",'
               '"floorSize":{"value":"1000"}}</script></head><body>x</body></html>')

    def fetcher(url):
        return listing if "/oferta/" in url else search

    rez = descopera_teren("imobiliare", "prahova", "breaza",
                          suprafata_subiect=Decimal("1000"), fetcher=fetcher)
    assert len(rez) == 1
    assert rez[0].pret == Decimal("50000")
    assert rez[0].suprafata == Decimal("1000")
    assert rez[0].pret_mp == Decimal("50")     # 50000 / 1000
    assert rez[0].relevanta == 100             # suprafata identica cu subiectul
