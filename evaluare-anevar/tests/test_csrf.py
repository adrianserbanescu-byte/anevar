"""SEC-3 (audit securitate 2026-06-08): middleware CSRF.

Un site strain din browser (Origin: evil.com) NU poate declansa mutatii pe API-ul local
(ar putea sterge dosare / corupe date prin CSRF). Origin local / extensie de browser / fara Origin = permis.
"""
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

_PAYLOAD = {"mesaj": "x", "sentiment": "", "pagina": "t", "url": "t", "tester": ""}


def _client(tmp_path):
    st = Storage(tmp_path / "t.db")
    st.init()
    return TestClient(create_app(storage=st, client=None))


def test_csrf_origin_strain_respins(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/feedback", json=_PAYLOAD, headers={"Origin": "https://evil.com"})
    assert r.status_code == 403


def test_csrf_local_extensie_fara_origin_permise(tmp_path):
    c = _client(tmp_path)
    assert c.post("/api/feedback", json=_PAYLOAD, headers={"Origin": "http://127.0.0.1:8000"}).status_code != 403
    assert c.post("/api/feedback", json=_PAYLOAD, headers={"Origin": "chrome-extension://abc"}).status_code != 403
    assert c.post("/api/feedback", json=_PAYLOAD).status_code != 403  # fara Origin (ne-browser) -> permis


def test_csrf_get_neafectat(tmp_path):
    c = _client(tmp_path)
    # GET-urile nu-s mutatii -> nu sunt blocate de CSRF nici cu Origin strain
    assert c.get("/api/status", headers={"Origin": "https://evil.com"}).status_code == 200
