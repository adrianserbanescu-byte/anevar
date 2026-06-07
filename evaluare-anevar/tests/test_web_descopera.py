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


def test_post_descopera_teren_returns_candidati(tmp_path):
    # acoperă endpointul /api/descopera-teren (era 0% acoperit) — flux happy-path.
    client = TestClient(_app(tmp_path))
    payload = {"portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
               "suprafata_subiect": "500", "max_candidati": 5}
    resp = client.post("/api/descopera-teren", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "candidati" in data and isinstance(data["candidati"], list)
    for c in data["candidati"]:   # structura fiecărui candidat-teren
        assert "url" in c and "pret_mp" in c and "relevanta" in c


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


def test_descopera_fetch_esuat_nu_crapa(tmp_path):
    # robustețe: portal căzut / fără rețea -> NU 500; fie 200 cu listă goală, fie 502 clar.
    import requests as _rq
    storage = Storage(tmp_path / "t.db")
    storage.init()

    def fetcher_cazut(url):
        raise _rq.ConnectionError("portal indisponibil")

    client = TestClient(create_app(storage=storage, client=None, fetcher=fetcher_cazut))
    payload = {"portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
               "subiect": {}, "atribute_secundare": [], "max_candidati": 3}
    r = client.post("/api/descopera", json=payload)
    assert r.status_code in (200, 502)
    if r.status_code == 200:
        assert r.json()["candidati"] == []
    rt = client.post("/api/descopera-teren", json={
        "portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
        "suprafata_subiect": "500", "max_candidati": 3})
    assert rt.status_code in (200, 502)


def test_descoperire_page_has_methodology_before_results(tmp_path):
    client = TestClient(_app(tmp_path))
    resp = client.get("/descoperire")
    assert resp.status_code == 200
    body = resp.text
    assert "Metodologie" in body
    assert 'id="metodologie"' in body
    assert 'id="rezultate"' in body
    assert body.index('id="metodologie"') < body.index('id="rezultate"')


def test_descoperire_eticheta_calitativa_d3(tmp_path):
    # D3 (decizie Adi): eticheta CALITATIVA = semnal primar; numarul ramane afisat dar SECUNDAR.
    body = TestClient(_app(tmp_path)).get("/descoperire").text
    assert "relevantaText" in body            # implementarea canonica (C); D3-ul lui B a fost descartat la merge
    for label in ("Foarte relevant", "Relevant", "Slab relevant", "Date insuficiente"):
        assert label in body, f"lipseste eticheta calitativa: {label}"
    assert "opacity:.7" in body               # numarul ramane afisat, dar marcat secundar (estompat)


def test_pret_mp_afisat_doar_cand_teren_comparabil(tmp_path):
    client = TestClient(_app(tmp_path))
    # candidatul (FakeClient) are teren=400. Subiect teren 420 -> comparabil -> pret/mp afisat
    p_comp = {"portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
              "subiect": {"an": 2013, "teren": "420"}, "atribute_secundare": [], "max_candidati": 3}
    c0 = client.post("/api/descopera", json=p_comp).json()["candidati"][0]
    assert c0["pret_mp"] is not None       # 249900/130 ~ 1922

    # Subiect teren 2000 -> teren necomparabil cu 400 -> pret/mp ascuns
    p_diff = {"portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
              "subiect": {"an": 2013, "teren": "2000"}, "atribute_secundare": [], "max_candidati": 3}
    c0d = client.post("/api/descopera", json=p_diff).json()["candidati"][0]
    assert c0d["pret_mp"] is None
    assert c0["pret_mp"] is not None   # pret 249900 / supr 130 -> ~1922
