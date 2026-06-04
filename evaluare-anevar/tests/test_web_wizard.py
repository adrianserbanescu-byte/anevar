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


def test_wizard_are_buton_raport_demo(tmp_path):
    client = _client(tmp_path)
    body = client.get("/wizard").text
    assert 'id="btn-raport-demo"' in body
    assert "?demo=1" in body


def test_wizard_are_selector_tip_proprietate(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'id="tip_proprietate"' in body
    assert 'id="etaj"' in body and 'id="an_bloc"' in body


def test_wizard_retine_identitatea_evaluatorului(tmp_path):
    # B3: nume + legitimatie evaluator retinute intre sesiuni, separat de dosar
    body = _client(tmp_path).get("/wizard").text
    assert 'localStorage.setItem("evaluator"' in body      # sticky store dedicat
    assert "incarcaEvaluator()" in body                     # pre-completare la init
    assert '"evaluator_nume","evaluator_legitimatie"' in body
    # reset sterge doar dosarul, nu identitatea evaluatorului
    assert 'localStorage.removeItem("wizard")' in body
    assert 'localStorage.removeItem("evaluator")' not in body


def test_wizard_are_metoda_venit(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'value="venit"' in body
    assert 'id="vbp"' in body and 'id="rata_cap"' in body


def test_wizard_are_industrial(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'value="industrial"' in body
    assert 'id="inaltime_libera"' in body


def test_wizard_are_agricol(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'value="agricol"' in body
    assert 'id="categorie_folosinta"' in body


def test_wizard_are_selector_scop(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'id="scop"' in body
    assert 'value="raportare_financiara"' in body and 'value="litigii"' in body


def test_wizard_are_metoda_dcf(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'value="dcf"' in body
    assert 'id="dcf_fluxuri"' in body and 'id="dcf_rata"' in body


def test_wizard_are_special(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'value="special"' in body
