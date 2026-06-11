"""Dosare salvate: redenumire, snapshot+re-deschidere, ștergere, versiuni .docx, pagina."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    s = Storage(tmp_path / "d.db")
    s.init()
    c = TestClient(create_app(storage=s, client=None))
    c._baza = tmp_path
    c.storage = s
    return c


def _payload():
    return {
        "meta": {"client_nume": "Ion Pop", "adresa": "A", "numar_cadastral": "777",
                 "carte_funciara": "CF", "evaluator_nume": "E", "evaluator_legitimatie": "1",
                 "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                                   "cost_unitar": "2000", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"}]},
        "valoare_teren": "100000", "metoda": "cost",
    }


def _creeaza(client) -> int:
    return client.post("/api/evaluare", json=_payload()).json()["id"]


def test_nume_implicit_si_redenumire(client):
    eid = _creeaza(client)
    # Numele implicit + redenumirea se verifică pe sursa de adevăr (storage), nu pe pagina HTML:
    # ruta legacy /dosare e acum un redirect către /incepe (gap UX F1-1, audit 2026-06-11).
    assert client.storage.list()[0]["nume"] == "Ion Pop — 777"
    client.post(f"/api/evaluare/{eid}/redenumeste", json={"nume": "Apartament X"})
    assert client.storage.list()[0]["nume"] == "Apartament X"


def test_dosare_redirect_la_incepe(client):
    # Gap UX F1-1: /dosare (lista SQLite legacy, dead-end) -> redirect la lista canonică /incepe#salvate.
    r = client.get("/dosare", follow_redirects=False)
    assert r.status_code in (302, 307) and r.headers["location"] == "/incepe#salvate"


def test_snapshot_si_redeschidere(client):
    eid = _creeaza(client)
    # fără snapshot încă
    assert client.get(f"/api/evaluare/{eid}/dosar").json()["wizard"] is None
    client.post(f"/api/evaluare/{eid}/snapshot", json={"client_nume": "Ion Pop", "au": "100"})
    d = client.get(f"/api/evaluare/{eid}/dosar").json()
    assert d["wizard"]["au"] == "100" and d["wizard"]["client_nume"] == "Ion Pop"


def test_versiune_docx_salvata_in_folder(client):
    eid = _creeaza(client)
    r = client.get(f"/api/evaluare/{eid}/raport.docx")
    assert r.status_code == 200
    folder = client._baza / "date" / "dosare" / str(eid)
    versiuni = list(folder.glob("raport-*.docx"))
    assert len(versiuni) == 1 and versiuni[0].stat().st_size > 1000


def test_stergere_dosar_si_folder(client):
    eid = _creeaza(client)
    client.get(f"/api/evaluare/{eid}/raport.docx")              # creează folder + versiune
    folder = client._baza / "date" / "dosare" / str(eid)
    assert folder.exists()
    client.post(f"/api/evaluare/{eid}/sterge")
    assert client.get("/api/evaluare/" + str(eid)).status_code == 404
    assert not folder.exists()


def test_dosar_inexistent_404(client):
    assert client.get("/api/evaluare/9999/dosar").status_code == 404
