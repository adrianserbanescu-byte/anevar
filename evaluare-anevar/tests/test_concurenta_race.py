"""Hardening adversarial — RACE CONDITIONS pe stocarea pe fisiere (dispatch A, lane F).

App-ul stocheaza dosarele pe FOLDERE (dosare/<uid>/dosar.json) si AML pe fisiere JSON. Fiecare
mutatie e un READ-MODIFY-WRITE neatomic: `incarca()` (citeste tot JSON-ul) -> muta dict -> `_scrie()`
(os.replace, atomic doar la WRITE, nu pe toata secventa). Sub requesturi concurente pe acelasi uid
=> lost-update / TOCTOU / overwrite. Fiecare test de mai jos demonstreaza o coruptie / pierdere de
date / 500 reproductibil(a). Marcate `xfail(strict=True)` => trec automat la VERDE cand se aplica fix-ul
(garda devine regresie). Vezi raportul catre A (2026-06-10).
"""
from __future__ import annotations

import json
import threading

import pytest

from evaluare.aml.store import StoreAML


@pytest.fixture
def fsmod(tmp_path, monkeypatch):
    """Modulul dosare_fs cu OUTPUT_DIR izolat in tmp (fs.baza() citeste OUTPUT_DIR)."""
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    from evaluare import dosare_fs as fs
    return fs


def _dummy_docx(folder, nume="raport-x.docx"):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / nume).write_bytes(b"PK\x03\x04 dummy docx")
    return nume


# ── F-4 (HIGH, item 4): StoreAML._next_id = len(glob)+1 -> overwrite la append concurent ──────────
def test_aml_next_id_coliziune_deterministica(tmp_path):
    # Doua apeluri _next_id INAINTE de scriere vad acelasi count -> acelasi id -> al doilea overwrite.
    store = StoreAML(tmp_path / "aml")
    id1 = store._next_id("rts")
    id2 = store._next_id("rts")
    assert id1 == id2 == 1, "ambele calcule vad 0 fisiere -> ambele aleg id=1 (coliziune)"


def test_aml_salveaza_concurent_pastreaza_toate_rapoartele(tmp_path):
    # FIXAT (F-4): 12 RTS salvate SIMULTAN (barrier) -> alocare atomica O_EXCL -> 12 fisiere distincte,
    # zero suprascriere. Inainte de fix: 1-3 fisiere (9-11 RTS pierdute). Regresie pt pierderea de date AML.
    store = StoreAML(tmp_path / "aml")
    N = 12
    barrier = threading.Barrier(N)
    erori: list = []

    def worker(i: int):
        try:
            barrier.wait()
            store.salveaza("rts", {"tranzactie": i}, "2026-01-01")
        except Exception as e:                       # noqa: BLE001 — captam orice in thread
            erori.append(e)

    ts = [threading.Thread(target=worker, args=(i,)) for i in range(N)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert not erori, f"exceptii in scriitori concurenti: {erori}"
    fisiere = list((tmp_path / "aml").glob("rts_*.json"))
    print(f"\n[F-4 FIXAT] RTS salvate={N}, fisiere pe disc={len(fisiere)} (pierdute={N - len(fisiere)})")
    assert len(fisiere) == N, f"pierdere de date AML: {N - len(fisiere)} RTS-uri suprascrise"
    # id-uri unice si contigue 1..N (alocare secventiala pastrata sub concurenta)
    ids = sorted(json.loads(f.read_text(encoding="utf-8"))["id"] for f in fisiere)
    assert ids == list(range(1, N + 1)), f"id-uri ne-unice/lacunare: {ids}"


# ── F-1 (HIGH): lost-update pe dosar.json — /salveaza vs generare raport (ADR-003) ────────────────
@pytest.mark.xfail(strict=True, reason="F-1: RMW neatomic -> /salveaza concurent sterge versiuni/asumat_la")
def test_salveaza_concurent_cu_generare_pierde_integritatea(fsmod):
    fs = fsmod
    uid = fs.creeaza("8717", "Adi", {"nume_client": "X"})
    folder = fs._cale(uid)
    nume = _dummy_docx(folder)
    # Writer A (salveaza_wizard) citeste PRIMUL (snapshot stale)...
    snap = fs.incarca(uid)
    # ...Writer B (generare raport) ruleaza COMPLET: seteaza versiuni + asumat_la + blocat.
    fs._inregistreaza_versiune(uid, nume, "generat")
    assert "versiuni" in fs.incarca(uid) and fs.incarca(uid).get("asumat_la")
    # ...Writer A continua cu snapshot-ul STALE si suprascrie -> integritatea ADR-003 DISPARE.
    snap["wizard"]["nume_client"] = "Y"
    fs._scrie(uid, snap)
    dupa = fs.incarca(uid)
    assert dupa.get("versiuni"), "F-1: versiuni (hash integritate) sterse de /salveaza concurent"
    assert dupa.get("asumat_la"), "F-1: asumat_la sters -> dosar de-asumat tacut"


# ── F-2 (MED/HIGH) — FIXAT: /salveaza (sau deblocheaza) vs /sterge nu mai da 500, ci 404 ──────────
def test_scrie_dupa_sterge_concurent_da_keyerror_nu_filenotfound(fsmod):
    fs = fsmod
    uid = fs.creeaza("8717", "Adi", {"nume_client": "X"})
    snap = fs.incarca(uid)                            # salveaza_wizard pas 1: citire OK
    fs.sterge(uid)                                    # /sterge concurent: rmtree pe folder
    # salveaza_wizard pas final: _scrie intr-un folder inexistent -> ACUM KeyError (nu FileNotFoundError).
    with pytest.raises(KeyError):
        fs._scrie(uid, snap)


def test_salveaza_pe_dosar_sters_mid_rmw_da_404_nu_500(tmp_path, monkeypatch):
    # Fereastra TOCTOU (folder sters INTRE incarca si _scrie) simulata fortand _scrie_atomic sa arunce
    # FileNotFoundError. Dupa fix, _scrie o traduce in KeyError -> router 404 (nu 500 nehandelat).
    from fastapi.testclient import TestClient

    from evaluare.db.storage import Storage
    from evaluare.web.app import create_app
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    s = Storage(tmp_path / "d.db")
    s.init()
    client = TestClient(create_app(storage=s, client=None), raise_server_exceptions=False)
    client.post("/api/cont", json={"nume": "Adi", "legitimatie": "8717"})
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "X"}}).json()["uuid"]
    import evaluare.dosare_fs as fs

    def _boom(*a, **k):                               # folderul „dispare" exact la scriere
        raise FileNotFoundError("folder sters concurent")
    monkeypatch.setattr(fs, "_scrie_atomic", _boom)
    r = client.post(f"/api/dosar/{uid}/salveaza", json={"nume_client": "Y"})
    print(f"\n[F-2] /salveaza cu folder sters mid-RMW -> HTTP {r.status_code} (fixat: 404, nu 500)")
    assert r.status_code == 404, "dosar sters concurent -> 404, nu 500 nehandelat"


# ── F-3 (MED): deblocheaza vs asumare -> blocat ramane in stare gresita + versiune pierduta ───────
@pytest.mark.xfail(strict=True, reason="F-3: RMW neatomic -> deblocheaza stale lasa blocat=False dupa asumare")
def test_deblocheaza_concurent_cu_asumare_lasa_identitatea_editabila(fsmod):
    fs = fsmod
    uid = fs.creeaza("8717", "Adi", {"nume_client": "X"})
    folder = fs._cale(uid)
    fs._inregistreaza_versiune(uid, _dummy_docx(folder, "raport-1.docx"), "generat")  # asumare 1: blocat=True
    # deblocheaza citeste PRIMUL (blocat=True, o singura versiune)...
    snapD = fs.incarca(uid)
    # ...a 2-a asumare ruleaza intre timp (versiuni=[v1,v2], blocat=True)...
    fs._inregistreaza_versiune(uid, _dummy_docx(folder, "raport-2.docx"), "generat")
    # ...deblocheaza scrie cu snapshot-ul STALE: blocat=False + doar v1.
    snapD["deblocari"] = [{"la": fs._acum(), "motiv": "typo"}]
    snapD["blocat"] = False
    fs._scrie(uid, snapD)
    dupa = fs.incarca(uid)
    # ADR-003: dupa o asumare proaspata identitatea trebuie sa fie BLOCATA; aici a ramas editabila.
    assert fs.este_blocat(dupa), "F-3: blocat=False dupa o asumare -> identitate editabila (viol. ADR-003)"
    assert len(dupa.get("versiuni", [])) == 2, "F-3: a 2-a versiune (hash integritate) pierduta"
