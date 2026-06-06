"""Verificari de accesibilitate (WCAG 2.1 AA) pe paginile aplicatiei — regresie pe atribute cheie."""
import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


@pytest.mark.parametrize("ruta", ["/wizard", "/aml", "/grila", "/descoperire"])
def test_pagina_are_landmark_main(client, ruta):
    html = client.get(ruta).text
    assert "<main" in html and "</main>" in html


@pytest.mark.parametrize("ruta", ["/wizard", "/aml", "/grila"])
def test_pagina_are_nav_landmark(client, ruta):
    assert "<nav" in client.get(ruta).text


def test_wizard_labels_asociate_si_stepper(client):
    html = client.get("/wizard").text
    assert 'for="judet"' in html and 'for="client_nume"' in html
    # stepper numerotat clickabil (a inlocuit bara de progres)
    assert 'class="stepper"' in html
    assert 'data-pas="1"' in html and 'data-pas="5"' in html
    assert "Comparabile" in html and "Raport" in html   # etichetele pasilor
    assert 'role="status"' in html          # mesaje de stare anuntate


def test_aml_labels_asociate(client):
    html = client.get("/aml").text
    assert 'for="tip_entitate"' in html and 'for="nume"' in html
    assert 'aria-live="polite"' in html


def test_grila_labels_si_helper(client):
    html = client.get("/grila").text
    assert 'for="supr-teren"' in html and 'for="t-judet"' in html
    assert "const $ = id => document.getElementById(id);" in html   # bug-fix helper
    assert 'scope="col"' in html


def test_descoperire_labels(client):
    html = client.get("/descoperire").text
    assert 'for="judet"' in html and 'for="incalzire"' in html
    assert 'role="status"' in html


@pytest.mark.parametrize("ruta", ["/wizard", "/aml", "/grila", "/descoperire"])
def test_pagina_are_skip_link(client, ruta):
    html = client.get(ruta).text
    assert 'class="skip-link"' in html
    assert 'id="continut"' in html


def test_wizard_date_inputs_au_type_date(client):
    html = client.get("/wizard").text
    assert 'id="data_evaluarii"' in html
    # campul de data foloseste type="date"
    import re
    assert re.search(r'<input[^>]*id="data_evaluarii"[^>]*type="date"', html) or \
           re.search(r'<input[^>]*type="date"[^>]*id="data_evaluarii"', html)
    assert 'autocomplete="name"' in html


# ── UI nou (curent): cont / incepe / dosar ───────────────────────────────────
@pytest.fixture
def curent_client(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    storage = Storage(tmp_path / "t.db")
    storage.init()
    c = TestClient(create_app(storage=storage, client=None))
    c.post("/api/cont", json={"nume": "Adi S", "legitimatie": "8717",
                              "format_dosar": ["id_client", "nume_client", "tip_proprietate"]})
    return c


@pytest.mark.parametrize("ruta", ["/cont", "/incepe"])
def test_curent_pagina_landmark_skip_nav(curent_client, ruta):
    html = curent_client.get(ruta).text
    assert "<main" in html and 'class="skip-link"' in html and 'id="continut"' in html
    assert "<nav" in html                                  # landmark de navigare


def test_cont_labels_asociate(curent_client):
    html = curent_client.get("/cont").text
    assert 'for="nume"' in html and 'for="legitimatie"' in html
    assert 'autocomplete="name"' in html


def test_incepe_tabel_scope_col(curent_client):
    curent_client.post("/api/dosar", json={"wizard": {"nume_client": "Ana"}})
    curent_client.get("/incepe")                           # populează indexul
    html = curent_client.get("/incepe").text
    assert 'scope="col"' in html and "Acțiuni" in html


def test_dosar_tablist_si_aria(curent_client):
    uid = curent_client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    html = curent_client.get(f"/dosar/{uid}").text
    assert "<nav" in html and 'class="skip-link"' in html
    assert 'role="tablist"' in html and 'role="tabpanel"' in html
    assert 'aria-controls="p-raport"' in html and 'aria-selected="true"' in html
    assert 'aria-labelledby="t-raport"' in html            # panou legat de tab
