from pathlib import Path

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

FIXTURES = Path(__file__).parent / "fixtures"


def _app(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    search_html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    listing_html = (FIXTURES / "imobiliare_listing_nextdata.html").read_text(encoding="utf-8")

    def fetcher(url):
        return listing_html if "/oferta/" in url else search_html

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":"2010"},'
                    '"stare":{"treapta":4,"text":"renovat"},'
                    '"finisaj":{"treapta":4,"text":"lux"},'
                    '"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                    '"teren":{"valoare":400,"text":"400"},"secundare":[]}')

    return create_app(storage=storage, client=FakeClient(), fetcher=fetcher)


def test_post_descopera_returns_metodologie_and_candidati(tmp_path):
    client = TestClient(_app(tmp_path))
    payload = {"portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
               "subiect": {"an": 2013, "stare": 3, "finisaj": 4,
                           "incalzire": "centrala_gaz", "teren": "500"},
               "atribute_secundare": [], "max_candidati": 5}
    resp = client.post("/api/descopera", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["metodologie"]) == 6
    assert len(data["candidati"]) == 3
    c0 = data["candidati"][0]
    assert "relevanta" in c0 and "explicatie" in c0 and "pret" in c0


def test_descoperire_page_has_methodology_before_results(tmp_path):
    client = TestClient(_app(tmp_path))
    resp = client.get("/descoperire")
    assert resp.status_code == 200
    body = resp.text
    assert "Metodologie" in body
    assert 'id="metodologie"' in body
    assert 'id="rezultate"' in body
    assert body.index('id="metodologie"') < body.index('id="rezultate"')


def test_descopera_candidat_are_pret_mp(tmp_path):
    client = TestClient(_app(tmp_path))
    payload = {"portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
               "subiect": {"an": 2013}, "atribute_secundare": [], "max_candidati": 3}
    data = client.post("/api/descopera", json=payload).json()
    c0 = data["candidati"][0]
    assert "pret_mp" in c0
    assert c0["pret_mp"] is not None   # pret 249900 / supr 130 -> ~1922
