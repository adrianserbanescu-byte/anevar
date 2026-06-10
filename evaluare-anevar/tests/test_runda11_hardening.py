"""Regresie RUNDA 11 (hardening ultracode): nume_fisier user-controlat -> OSError -> 500.

import-docx + incarca-submis faceau `tmp = tmpdir / (Path(req.nume_fisier).name or "...")` apoi
`tmp.write_bytes(raw)` intr-un try/finally FARA except. Un nume > limita OS (~255 char) sau cu
caractere invalide Windows -> OSError neprins -> HTTP 500 (5 cazuri confirmate determinist). Acum
`_nume_fisier_sigur` curata + plafoneaza numele -> write reuseste (4xx/2xx, nu 500).
"""
import base64

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app
from evaluare.web.routers.curent import _nume_fisier_sigur


def _client(tmp_path):
    s = Storage(tmp_path / "t.db")
    s.init()
    return TestClient(create_app(storage=s, client=None))


def _cont(c):
    c.post("/api/cont", json={"nume": "Adi", "legitimatie": "8717"})


def test_nume_fisier_sigur_unit():
    assert _nume_fisier_sigur("../../etc/passwd", "d.docx") == "passwd"   # .name taie traversal
    assert _nume_fisier_sigur("..", "d.docx") == "d.docx"                  # gol -> implicit
    assert _nume_fisier_sigur("", "d.docx") == "d.docx"
    assert len(_nume_fisier_sigur("A" * 300 + ".docx", "d.docx")) <= 150   # cap anti-OSError
    sanit = _nume_fisier_sigur('a<>:"|?*b.docx', "d.docx")                 # caractere invalide
    assert all(ch not in sanit for ch in '<>:"|?*')


def test_import_docx_nume_fisier_lung_nu_500(tmp_path):
    c = _client(tmp_path)
    _cont(c)
    continut = base64.b64encode(b"PK\x03\x04 nu-e-docx-valid").decode()  # extrage degradeaza gratios
    r = c.post("/api/dosar/import-docx", json={"nume_fisier": "A" * 300 + ".docx", "continut": continut})
    assert r.status_code < 500


def test_import_docx_nume_fisier_invalid_nu_500(tmp_path):
    c = _client(tmp_path)
    _cont(c)
    continut = base64.b64encode(b"PK\x03\x04 x").decode()
    r = c.post("/api/dosar/import-docx", json={"nume_fisier": '..\\..\\<>:"|?*.docx', "continut": continut})
    assert r.status_code < 500


def test_dcf_fluxuri_cap_anti_dos():
    # DateDCF.fluxuri fara limita -> evalueaza_dcf factor**t O(n^2) -> hang (RUNDA 11). Cap 200.
    from decimal import Decimal

    import pytest
    from pydantic import ValidationError

    from evaluare.engine.venit import DateDCF
    DateDCF(fluxuri=[Decimal("1")] * 200, rata_actualizare=Decimal("0.1"))          # 200 = OK
    with pytest.raises(ValidationError):
        DateDCF(fluxuri=[Decimal("1")] * 201, rata_actualizare=Decimal("0.1"))      # >200 -> respins

