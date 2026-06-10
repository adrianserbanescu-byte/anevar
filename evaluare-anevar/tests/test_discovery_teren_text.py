"""FIX teren-in-formula (dispatch A): terenul din TITLU/descriere trebuie sa intre in scor.

Inainte, terenul venea doar din datele structurate (JSON-LD/__NEXT_DATA__). Cand un anunt
avea terenul DOAR in titlu ("teren 257 mp"), `candidat.teren` ramanea None -> atributul „teren"
era exclus TACIT din formula relevantei (afisa „Teren: nementionat") desi exista in anunt.
"""
from decimal import Decimal

from evaluare.discovery.orchestrator import _teren_din_text, descopera
from evaluare.discovery.profiles import SubjectProfile


def test_teren_din_text_formate_ro():
    assert _teren_din_text("Casa 4 camere, teren 257 mp - Otopeni") == Decimal("257")
    assert _teren_din_text("Vila P+1, teren de 1.910 mp, Tunari") == Decimal("1910")
    assert _teren_din_text("Casa cu 2000 mp teren") == Decimal("2000")
    assert _teren_din_text("Sup. teren: 300 mp") == Decimal("300")
    assert _teren_din_text("Casa, 120 mp construiti, teren 1 200 mp") == Decimal("1200")
    assert _teren_din_text("teren: 500mp") == Decimal("500")


def test_teren_din_text_fara_teren_returneaza_none():
    assert _teren_din_text("Apartament 3 camere 75 mp") is None
    assert _teren_din_text("") is None
    assert _teren_din_text("Casa frumoasa fara metraj") is None
    # valoare implauzibila (sub prag) -> ignorata
    assert _teren_din_text("teren 5 mp") is None


def test_descopera_extrage_teren_din_titlu():
    # Anunt cu terenul DOAR in titlu (fara JSON-LD/__NEXT_DATA__ pentru teren) -> trebuie sa
    # ajunga in scor, NU sa fie exclus.
    search = '<html><body><a href="/oferta/casa-cu-teren-1">x</a></body></html>'
    listing = (
        '<html><head><title>Casa 4 camere, teren 257 mp - Otopeni</title>'
        '<script type="application/ld+json">'
        '{"@type":"Offer","price":"200000","priceCurrency":"EUR"}</script>'
        '<meta property="og:description" content="Casa moderna, suprafata utila 120 mp.">'
        '</head><body>Descriere: casa frumoasa in Otopeni.</body></html>'
    )

    def fetcher(url):
        return listing if "/oferta/" in url else search

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2015,"text":"2015"},"stare":{"treapta":4,"text":"buna"},'
                    '"finisaj":{"treapta":4,"text":"lux"},'
                    '"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                    '"teren":{"valoare":null,"text":""},"secundare":[]}')

    subiect = SubjectProfile(suprafata_construita=Decimal("120"), an=2013, stare=3,
                             finisaj=4, incalzire="centrala_gaz", teren=Decimal("300"))
    rez = descopera("imobiliare", judet="ilfov", localitate="otopeni", subiect=subiect,
                    atribute_secundare=[], fetcher=fetcher, client=FakeClient(), max_candidati=3)
    assert len(rez) == 1
    cand = rez[0]
    # terenul extras din titlu intra in rezultat...
    assert cand.teren == Decimal("257")
    # ...si in formula relevantei (atributul „Teren" e cunoscut, nu exclus)
    teren_attr = [a for a in cand.breakdown.atribute if a.nume == "Teren"]
    assert teren_attr and teren_attr[0].cunoscut is True
    assert "Teren: nementionat" not in cand.breakdown.explicatie
