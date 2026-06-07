from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_index_is_alegere_ui(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    # pagina principala este acum alegerea interfetei (UI nou vs wizard vechi)
    assert "Alege interfața" in resp.text
    assert 'href="/incepe"' in resp.text and 'href="/wizard"' in resp.text


def test_wizard_inca_la_ruta_proprie(tmp_path):
    resp = _client(tmp_path).get("/wizard")
    assert resp.status_code == 200 and 'id="pas-1"' in resp.text


def test_flux_livrabile_pagina(tmp_path):
    # harta de proces a livrabilelor: rută proprie + elementele cheie + cele 7 panouri
    resp = _client(tmp_path).get("/flux-livrabile")
    assert resp.status_code == 200
    html = resp.text
    assert "Fluxul livrabilelor" in html
    assert 'class="fl-stepper"' in html and 'class="fl-dock"' in html
    assert "Nivel 1 · Firmă" in html and "Notă de informare GDPR" in html
    assert 'data-step="6"' in html                          # panourile 0..6 randate server-side


def test_flux_livrabile_in_nav(tmp_path):
    # link-ul „Flux livrabile" apare în cross-nav pe paginile aplicației
    assert 'href="/flux-livrabile"' in _client(tmp_path).get("/wizard").text


def test_cross_nav_pe_pagini(tmp_path):
    # link-urile UI nou / UI vechi / Documente apar în antet/subsol pe paginile vechi și noi
    client = _client(tmp_path)
    for ruta in ("/wizard", "/grila", "/aml"):
        html = client.get(ruta).text
        assert 'class="cross-ui"' in html and 'href="/documente"' in html and 'href="/incepe"' in html


def test_widget_feedback_pe_tot_ui_nou_si_vechi(tmp_path):
    # widget-ul de feedback (mutat în subsolul comun) trebuie să apară pe TOATE paginile
    client = _client(tmp_path)
    for ruta in ("/", "/wizard", "/documente", "/incepe", "/cont"):
        assert 'id="fb-open"' in client.get(ruta).text, f"lipsește widget feedback pe {ruta}"


def test_documente_index_si_render(tmp_path):
    client = _client(tmp_path)
    idx = client.get("/documente")
    assert idx.status_code == 200 and "Documente" in idx.text
    assert "/documente/disclaimer-profesional" in idx.text       # card prezent
    doc = client.get("/documente/disclaimer-profesional")
    assert doc.status_code == 200 and "<article" in doc.text      # conținut randat
    assert client.get("/documente/nu-exista").status_code == 404


def test_formular_monolit_la_ruta_noua(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/formular")
    assert resp.status_code == 200
    assert "<form" in resp.text
    assert 'name="metoda"' in resp.text          # selector de metoda
    assert "Import din URL" in resp.text          # buton import
    assert 'name="comparabile"' in resp.text      # sectiune comparabile


def test_result_page_loads(tmp_path):
    client = _client(tmp_path)
    payload = {
        "meta": {"client_nume": "Ion Popescu", "adresa": "Str. 1",
                 "numar_cadastral": "123", "carte_funciara": "CF123",
                 "evaluator_nume": "Maria", "evaluator_legitimatie": "1",
                 "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp",
                                   "cantitate": "120", "cost_unitar": "2000", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                             {"varsta": 15, "depreciere": "0.15"}]},
        "valoare_teren": "100000", "metoda": "cost",
    }
    eid = client.post("/api/evaluare", json=payload).json()["id"]
    resp = client.get(f"/evaluare/{eid}")
    assert resp.status_code == 200
    assert "Ion Popescu" in resp.text
    assert "raport.docx" in resp.text   # link de descarcare
