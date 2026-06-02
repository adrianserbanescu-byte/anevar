from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_wizard_page_loads_with_5_steps(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/wizard")
    assert resp.status_code == 200
    body = resp.text
    for i in range(1, 6):
        assert f'id="pas-{i}"' in body
    # referinta catre endpoint-urile reutilizate
    assert "/api/descopera" in body
    assert "/api/evaluare" in body
    assert "localStorage" in body


def test_wizard_pas1_are_dropdown_judet_localitate(tmp_path):
    client = _client(tmp_path)
    body = client.get("/wizard").text
    assert '<select id="judet"' in body
    assert '<select id="localitate"' in body
    assert "/api/localitati" in body
    assert 'id="adresa_strada"' in body


def test_wizard_are_atribute_secundare(tmp_path):
    client = _client(tmp_path)
    body = client.get("/wizard").text
    assert 'id="atribute_secundare"' in body
    assert "Atribute secundare" in body


def test_wizard_are_campuri_gbf_noi(tmp_path):
    client = _client(tmp_path)
    body = client.get("/wizard").text
    for camp in ['id="beneficiar"', 'id="proprietar"', 'id="data_inspectiei"',
                 'id="moneda"', 'id="curs_valutar"']:
        assert camp in body


def test_wizard_are_upload_foto(tmp_path):
    client = _client(tmp_path)
    body = client.get("/wizard").text
    assert 'id="foto"' in body
    assert 'type="file"' in body
    assert "photos:FOTOS" in body
