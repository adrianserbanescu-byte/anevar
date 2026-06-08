"""SEC-1 (audit P0#1): path traversal pe `uid` de dosar.

`uid` vine din path-ul user (`/api/dosar/{uid}/...`) si era folosit NEVALIDAT in `baza()/uid` la
incarca/salveaza/STERGE. `sterge` face `shutil.rmtree` -> un uid cu „.." putea sterge `date/`
(toate dosarele + DB). Fix: `_cale()` valideaza uid ca UUID. Aceste teste DOVEDESC ca traversal-ul
nu mai poate iesi din baza si ca rutele intorc 404 (nu 500) pe uid invalid."""
import uuid

import pytest

from evaluare import dosare_fs as fs

# Payload-uri de traversal / uid-uri invalide
RELE = ["..", "../..", "../", "a/../..", "....//", "%2e%2e", "../../../../etc",
        "/etc/passwd", "", "not-a-uuid", "../dosare", "\\..\\..", "dosare/../.."]


def test_cale_respinge_uid_nonuuid_accepta_uuid():
    for rau in RELE:
        with pytest.raises(KeyError):
            fs._cale(rau)
    u = str(uuid.uuid4())
    assert fs._cale(u).name == u                 # un UUID valid trece + ramane sub baza
    assert fs._cale(u).parent == fs.baza()


def test_sterge_traversal_NU_distruge_baza(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "out"))
    uid = fs.creeaza("L1", "Eval", {"scop": "garantare"})
    # fisier critic LANGA dosare/ (ar fi sters de un rmtree(baza()/'..') nevalidat)
    sentinela = (tmp_path / "out" / "NU_STERGE.txt")
    sentinela.write_text("date critice", encoding="utf-8")
    for rau in ["..", "../..", "../dosare", "not-a-uuid"]:
        with pytest.raises(KeyError):
            fs.sterge(rau)
        with pytest.raises(KeyError):
            fs.incarca(rau)
    assert sentinela.exists()                    # baza INTACTA -> traversal blocat
    assert fs.incarca(uid)["uuid"] == uid        # dosarul valid inca merge
    fs.sterge(uid)                               # stergerea valida functioneaza
    assert not (fs.baza() / uid).exists()


def test_rute_dosar_uid_invalid_dau_404_nu_500(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "out"))
    from fastapi.testclient import TestClient

    from evaluare.db.storage import Storage
    from evaluare.web.app import create_app
    storage = Storage(tmp_path / "t.db")
    storage.init()
    client = TestClient(create_app(storage=storage, client=None, fetcher=lambda u: ""))

    assert client.get("/api/dosar/not-a-uuid").status_code == 404
    assert client.post("/api/dosar/not-a-uuid/sterge").status_code == 404
    assert client.post("/api/dosar/not-a-uuid/salveaza", json={}).status_code == 404
    assert client.post("/api/dosar/not-a-uuid/cloneaza").status_code == 404
    # unlock = best-effort (sendBeacon la inchiderea ferestrei) -> 200, NU 500, pe uid invalid
    assert client.post("/api/dosar/not-a-uuid/unlock", json={"token": "x"}).status_code == 200
