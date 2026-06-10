"""Regresie: path-param `eid` peste max int64 → 422 (gard Pydantic), nu 500 (SQLite Overflow).

Detectat de safety net schemathesis (seed=1, max-examples=10) pe build #4: SQLite INTEGER e
8 bytes (max 2^63-1 = 9223372036854775807); int Python e BigInt nelimitat -> orice eid mai mare
crapă INSERT/SELECT cu `OverflowError: Python int too large to convert to SQLite INTEGER` -> 500
nehandelat. Garda `Annotated[int, Path(ge=1, le=2**63-1)]` aliasata ca `EvaluareId` în router.

Acoperă toate cele 7 endpoint-uri /api/evaluare/{eid}/* + pagina HTML /evaluare/{eid} (8 total).

Owner: D (Rol 2, finding safety net + harden-eid-overflow). Backwards-compat: int-uri normale
(eid < 2^63) trec exact ca înainte; doar valorile peste max int64 sunt respinse (acum 422).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

INT64_MAX = 2**63 - 1
PESTE_INT64 = 2**63                              # primul int care depășește INTEGER SQLite


def _client(tmp_path) -> TestClient:
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


# ─── Smoke: cazul "normal" int < 2^63 (nu schimbă comportamentul existent) ────
def test_eid_normal_int_trece_validation(tmp_path):
    """eid=999 (sau orice int rezonabil) NU e blocat de garda noua: 404 pe inexistent, nu 422."""
    client = _client(tmp_path)
    r = client.get("/api/evaluare/999")
    assert r.status_code == 404                  # dosar inexistent, dar a TRECUT prin Pydantic


def test_eid_la_limita_int64_inca_trece(tmp_path):
    """eid = 2^63-1 (max int64) e valoarea limita admisa de Pydantic; tot 404 pe inexistent."""
    client = _client(tmp_path)
    r = client.get(f"/api/evaluare/{INT64_MAX}")
    assert r.status_code == 404                  # accepta valoarea, dosarul nu există


# ─── Garda noua: eid > 2^63-1 → 422 pe toate endpoint-urile ────────────────────
def test_eid_peste_int64_returns_422_pe_get_evaluare(tmp_path):
    """GET /api/evaluare/{eid} cu eid > 2^63 → 422 (era 500 cu SQLite OverflowError)."""
    client = _client(tmp_path)
    r = client.get(f"/api/evaluare/{PESTE_INT64}")
    assert r.status_code == 422


def test_eid_peste_int64_returns_422_pe_sterge(tmp_path):
    """POST /api/evaluare/{eid}/sterge — endpoint-ul pe care Schemathesis a expus 500."""
    client = _client(tmp_path)
    r = client.post(f"/api/evaluare/{PESTE_INT64}/sterge")
    assert r.status_code == 422


def test_eid_peste_int64_returns_422_pe_raport(tmp_path):
    """GET /api/evaluare/{eid}/raport.docx — descarcare raport pe eid imposibil."""
    client = _client(tmp_path)
    r = client.get(f"/api/evaluare/{PESTE_INT64}/raport.docx")
    assert r.status_code == 422


def test_eid_peste_int64_returns_422_pe_redenumeste(tmp_path):
    client = _client(tmp_path)
    r = client.post(f"/api/evaluare/{PESTE_INT64}/redenumeste", json={"nume": "X"})
    assert r.status_code == 422


def test_eid_peste_int64_returns_422_pe_snapshot(tmp_path):
    client = _client(tmp_path)
    r = client.post(f"/api/evaluare/{PESTE_INT64}/snapshot", json={})
    assert r.status_code == 422


def test_eid_peste_int64_returns_422_pe_dosar(tmp_path):
    client = _client(tmp_path)
    r = client.get(f"/api/evaluare/{PESTE_INT64}/dosar")
    assert r.status_code == 422


def test_eid_peste_int64_returns_422_pe_audit(tmp_path):
    client = _client(tmp_path)
    r = client.get(f"/api/evaluare/{PESTE_INT64}/audit.txt")
    assert r.status_code == 422


def test_eid_peste_int64_returns_422_pe_pagina_html(tmp_path):
    """Pagina HTML /evaluare/{eid} (nu /api): aceeasi garda Pydantic la nivel de router."""
    client = _client(tmp_path)
    r = client.get(f"/evaluare/{PESTE_INT64}")
    assert r.status_code == 422


# ─── Garda inferioara: eid = 0 sau negativ → 422 (ge=1) ────────────────────────
def test_eid_zero_returns_422(tmp_path):
    """eid=0 era invalid logic (id-urile incep de la 1); acum si garda Pydantic blocheaza explicit."""
    client = _client(tmp_path)
    r = client.get("/api/evaluare/0")
    assert r.status_code == 422
