"""Regresie RUNDA 12 (hardening robustete): 3 findings confirmate determinist.

F-12-1 (HIGH, 500): curs_valutar extrem (ex. 1E-30) -> fmt_numar(val/curs) quantize ->
  decimal.InvalidOperation neprins -> 500 la GET /evaluare/{id}. Fix defense-in-depth:
  (a) fmt_numar prinde ArithmeticError -> fallback; (b) curs_valutar marginit (gt=0, le=1e6)
  -> 422 inca de la /api/evaluare; (c) blocul 'echiv' din pagina_rezultat prinde ArithmeticError.

F-12-2 (MEDIUM, DoS): SequenceMatcher O(n*m) pe nume KYC nemarginite -> ~10s CPU la 500K char.
  Fix: max_length pe nume/prenume/denumire (200) + trunchiere defensiva in _similar.

F-12-3 (LOW): ClientPJ.beneficiari_reali lista nemarginita. Fix: max_length=1000.
"""
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from evaluare.aml.liste import Liste, _similar, screening
from evaluare.aml.models import ClientPJ, PersoanaFizica
from evaluare.db.storage import Storage
from evaluare.models.meta import EvaluationMeta
from evaluare.web.app import create_app
from evaluare.web.format import fmt_numar


def _payload() -> dict:
    return {
        "meta": {
            "client_nume": "Ion Popescu", "adresa": "Str. 1",
            "numar_cadastral": "123", "carte_funciara": "CF123",
            "evaluator_nume": "Maria", "evaluator_legitimatie": "1",
            "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16",
        },
        "land": {"suprafata": "500"},
        "building": {
            "au": "100", "acd": "120", "an_referinta": 2025,
            "elements": [{"element": "S", "cod": "X", "um": "mp",
                          "cantitate": "120", "cost_unitar": "2000", "an_pif": 2015}],
            "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                    {"varsta": 15, "depreciere": "0.15"}],
        },
        "valoare_teren": "100000",
        "metoda": "cost",
    }


def _client(tmp_path):
    s = Storage(tmp_path / "t.db")
    s.init()
    return TestClient(create_app(storage=s, client=None))


# ---------------------------------------------------------------- F-12-1 (a) fmt_numar robust
def test_fmt_numar_curs_extrem_nu_crapa():
    # val/curs cu curs=1E-30 -> ~1e35 -> quantize("0.01") arunca InvalidOperation. Acum nu 500.
    val = Decimal("316000")
    rez = fmt_numar(val / Decimal("1E-30"))
    assert isinstance(rez, str) and rez               # nu arunca, intoarce ceva afisabil


def test_fmt_numar_normal_neschimbat():
    assert fmt_numar(Decimal("316000")) == "316.000,00"   # comportamentul normal pastrat


# ---------------------------------------------------------------- F-12-1 proba originala: 1E-30
def test_curs_valutar_1e30_nu_mai_da_500(tmp_path):
    # Proba auditului: POST cu curs=1E-30 -> 200; apoi GET /evaluare -> inainte 500 (fmt_numar
    # quantize crapa la val/curs ~1e35). 1E-30 e un mic pozitiv valid (trece gt=0/le=1e6), deci
    # nu e respins la POST — dar fmt_numar robust (a) + try/except echiv (c) tin GET la 200.
    c = _client(tmp_path)
    p = _payload()
    p["meta"]["moneda"] = "LEI"
    p["meta"]["curs_valutar"] = "1E-30"
    r = c.post("/api/evaluare", json=p)
    assert r.status_code == 200
    eid = r.json()["id"]
    assert c.get(f"/evaluare/{eid}").status_code == 200    # inainte: 500


# ---------------------------------------------------------------- F-12-1 (b) curs marginit -> 422
def test_curs_valutar_prea_mare_respins_422():
    p = _payload()
    p["meta"]["curs_valutar"] = "2000000"              # > 1e6
    assert _client_post(p).status_code == 422


def test_curs_valutar_zero_respins_422():
    p = _payload()
    p["meta"]["curs_valutar"] = "0"                    # gt=0
    assert _client_post(p).status_code == 422


def _client_post(payload):
    import tempfile
    from pathlib import Path
    s = Storage(Path(tempfile.mkdtemp()) / "t.db")
    s.init()
    return TestClient(create_app(storage=s, client=None)).post("/api/evaluare", json=payload)


def test_curs_valutar_real_ramane_200_si_pagina_ok(tmp_path):
    # Curs valutar real (4.97 RON/EUR) ramane 200 + pagina afiseaza echivalentul EUR.
    c = _client(tmp_path)
    p = _payload()
    p["meta"]["moneda"] = "LEI"
    p["meta"]["curs_valutar"] = "4.97"
    r = c.post("/api/evaluare", json=p)
    assert r.status_code == 200
    eid = r.json()["id"]
    html = c.get(f"/evaluare/{eid}")
    assert html.status_code == 200
    assert "EUR" in html.text


def _meta(**kw) -> dict:
    return dict(
        client_nume="X", adresa="A", numar_cadastral="1", carte_funciara="CF",
        evaluator_nume="E", evaluator_legitimatie="1",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16", **kw,
    )


def test_meta_curs_prea_mare_la_nivel_de_model():
    with pytest.raises(ValidationError):
        EvaluationMeta(**_meta(curs_valutar=Decimal("2000000")))   # > 1e6
    with pytest.raises(ValidationError):
        EvaluationMeta(**_meta(curs_valutar=Decimal("0")))         # gt=0
    # curs valutar real -> acceptat
    assert EvaluationMeta(**_meta(curs_valutar=Decimal("4.97"))).curs_valutar == Decimal("4.97")


# ---------------------------------------------------------------- F-12-2 nume marginite (DoS)
def test_nume_500k_respins_422():
    with pytest.raises(ValidationError):
        PersoanaFizica(nume="A" * 500_000, prenume="Ion")


def test_denumire_pj_500k_respins_422():
    with pytest.raises(ValidationError):
        ClientPJ(denumire="A" * 500_000)


def test_nume_normal_ramane_valid():
    p = PersoanaFizica(nume="Popescu", prenume="Ion-Alexandru")
    assert p.nume == "Popescu"


def test_similar_trunchiaza_si_e_rapid():
    import time
    t0 = time.perf_counter()
    _similar("A" * 500_000, "B" * 500_000)            # fara trunchiere = ~secunde
    assert time.perf_counter() - t0 < 1.0             # cu trunchiere = instant


def test_screening_nume_lung_nu_face_dos():
    import time
    liste = Liste(sanctiuni=["Ion Popescu"], pep_functii=[])
    t0 = time.perf_counter()
    screening("X" * 500_000, liste)
    assert time.perf_counter() - t0 < 1.0


# ---------------------------------------------------------------- F-12-3 beneficiari_reali <=1000
def test_beneficiari_reali_peste_1000_respins():
    from evaluare.aml.models import BeneficiarReal
    br = [BeneficiarReal(nume="A", prenume="B") for _ in range(1001)]
    with pytest.raises(ValidationError):
        ClientPJ(denumire="ACME", beneficiari_reali=br)


def test_beneficiari_reali_in_limita_ok():
    from evaluare.aml.models import BeneficiarReal
    br = [BeneficiarReal(nume="A", prenume="B") for _ in range(10)]
    c = ClientPJ(denumire="ACME", beneficiari_reali=br)
    assert len(c.beneficiari_reali) == 10
