"""Regresie RUNDA 16 (hardening robustete pe suprafata DESCOPERIRE + IMPORT): 5 findings.

Toate sunt clase de eroare NEACOPERITE de rundele anterioare (nu sunt `ValueError`), pe input
HTML/text NETRUSTED din portaluri / extensia de browser. Vezi docs/audit-robustete-runda16-2026-06-11.md.

F-16-1 (HIGH): `json.loads` pe JSON adanc imbricat (`[[[…]]]`) -> `RecursionError` (subclasa de
  RuntimeError, NU de ValueError) -> scapa de toate garile `except (…, ValueError)` -> 500. Fix:
  largim clauzele `except` din parser/orchestrator la `RecursionError` (4+1 locuri cu json.loads).
F-16-2 (HIGH, ReDoS): regexul „N mp" + regexul de pret pe titlu/og (attacker-controlled) -> un titlu
  enorm de cifre fara unitate/moneda backtrack-uia super-/patratic -> blocheaza workerul zeci de
  secunde. Fix: cifre marginite (1..7 / 3..18 cifre) + `text_cautare` truncat inainte de regex.
F-16-3 (HIGH, ReDoS): `_RE_TEREN_TEXT` (orchestrator) pe titlu/descriere -> idem. Fix: repetitii
  marginite (`{0,12}`) + text truncat.
F-16-4 (MEDIUM): `max_candidati` nemarginit/negativ (1e9, -5) acceptat de schema -> amplifica
  fetch/parse. Fix: `Field(ge=1, le=50)` (default 50 pastrat).
F-16-5 (LOW): `_int_safe(int(float('inf')))` pe iesire LLM ostila (`an: 1e400`) -> `OverflowError`
  (subclasa de ArithmeticError, NU de ValueError) -> 500. Fix: garda largita la `ArithmeticError`.
"""
from __future__ import annotations

import time
from decimal import Decimal

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from pydantic import ValidationError

import evaluare.discovery.orchestrator as orch
import evaluare.importers.url_parser as up
from evaluare.db.storage import Storage
from evaluare.discovery.extractor import extrage_atribute
from evaluare.discovery.profiles import SubjectProfile
from evaluare.web.app import create_app
from evaluare.web.schemas import DescoperaRequest, DescoperaTerenRequest

# Adancimea de imbricare care depaseste limita de recursie a decoderului C din CPython la json.loads.
_NESTED = "[" * 3000 + "0" + "]" * 3000


def _client(tmp_path) -> TestClient:
    s = Storage(tmp_path / "t.db")
    s.init()
    return TestClient(create_app(storage=s, client=None))


# ---- pre-conditii: payload-urile chiar declanseaza clasele de eroare vizate (altfel testele sunt goale)
def test_precond_json_adanc_da_recursionerror():
    import json
    with pytest.raises(RecursionError):
        json.loads(_NESTED)
    assert not issubclass(RecursionError, ValueError)   # de aceea scapa de garile vechi


def test_precond_int_inf_da_overflowerror():
    with pytest.raises(OverflowError):
        int(float("inf"))
    assert issubclass(OverflowError, ArithmeticError)
    assert not issubclass(OverflowError, ValueError)


# ============================================================ F-16-1: RecursionError din json.loads
def test_f16_1_parser_jsonld_adanc_nu_crapa():
    html = f'<script type="application/ld+json">{_NESTED}</script>'
    p = up.parse_listing_html(html, "http://x")   # nu trebuie sa ridice RecursionError
    assert p.pret is None


def test_f16_1_parser_nextdata_adanc_nu_crapa():
    html = f'<script id="__NEXT_DATA__">{_NESTED}</script>'
    p = up.parse_listing_html(html, "http://x")
    assert p.pret is None and p.suprafata is None


def test_f16_1_orchestrator_descriere_nextdata_adanc_nu_crapa():
    soup = BeautifulSoup(f'<script id="__NEXT_DATA__">{_NESTED}</script>', "html.parser")
    assert orch._descriere_din_nextdata(soup, 4000) == ""   # degradeaza gratios, nu RecursionError


def test_f16_1_import_anunt_jsonld_adanc_422_nu_500(tmp_path):
    c = _client(tmp_path)
    html = f'<script type="application/ld+json">{_NESTED}</script>'
    r = c.post("/api/import-anunt", json={"html": html, "url": "http://x"})
    assert r.status_code != 500
    assert r.status_code in (200, 422)


def test_f16_1_import_anunt_nextdata_adanc_422_nu_500(tmp_path):
    c = _client(tmp_path)
    html = f'<script id="__NEXT_DATA__">{_NESTED}</script>'
    r = c.post("/api/import-anunt", json={"html": html, "url": "http://x"})
    assert r.status_code != 500


def test_f16_1_import_url_adanc_nu_500(tmp_path):
    # fetcher ostil injecteaza HTML cu blob adanc -> nu 500
    s = Storage(tmp_path / "t.db")
    s.init()
    html = f'<script type="application/ld+json">{_NESTED}</script>'
    c = TestClient(create_app(storage=s, client=None, fetcher=lambda url: html))
    r = c.post("/api/import-url", json={"url": "http://example.com/anunt"})
    assert r.status_code != 500


# ============================================================ F-16-2: ReDoS pe „N mp" + pret (titlu)
def test_f16_2_titlu_enorm_rapid_nu_hang():
    t0 = time.perf_counter()
    up.parse_listing_html("<title>" + "1" * 20000 + " X</title>", "http://x")
    dt = time.perf_counter() - t0
    assert dt < 1.0, f"parse_listing_html a durat {dt:.2f}s pe un titlu de 20k cifre (ReDoS)"


def test_f16_2_og_description_enorm_rapid():
    html = ('<html><head><title>Casa</title>'
            '<meta property="og:description" content="' + "1" * 20000 + ' X">'
            "</head><body></body></html>")
    t0 = time.perf_counter()
    up.parse_listing_html(html, "http://x")
    assert time.perf_counter() - t0 < 1.0


def test_f16_2_extrage_in_continuare_valori_legitime():
    # marginirea regex-urilor NU rupe extractia normala (regresie de comportament)
    p = up.parse_listing_html("<title>Vila 220 mp Pipera 500000 EUR</title>")
    assert p.suprafata == Decimal("220")
    assert p.pret == Decimal("500000")
    assert p.moneda == "EUR"


def test_f16_2_pret_cu_separatori_inca_prins():
    p = up.parse_listing_html("<title>Casa noua 2.000.000 EUR Cluj</title>")
    assert p.pret == Decimal("2000000")
    assert p.moneda == "EUR"


# ============================================================ F-16-3: ReDoS pe _RE_TEREN_TEXT
def test_f16_3_teren_text_enorm_rapid_nu_hang():
    t0 = time.perf_counter()
    orch._teren_din_text("teren " + "1" * 50000 + "X")
    dt = time.perf_counter() - t0
    assert dt < 1.0, f"_teren_din_text a durat {dt:.2f}s pe 50k cifre (ReDoS)"


def test_f16_3_teren_text_punct_spatiu_enorm_rapid():
    t0 = time.perf_counter()
    orch._teren_din_text("teren " + "1. " * 5000 + "X")
    assert time.perf_counter() - t0 < 1.0


def test_f16_3_teren_text_legitim_inca_prins():
    assert orch._teren_din_text("teren 257 mp") == Decimal("257")
    assert orch._teren_din_text("257 mp teren") == Decimal("257")
    assert orch._teren_din_text("teren de 1.910 mp") == Decimal("1910")


# ============================================================ F-16-4: max_candidati marginit la schema
def _subiect() -> SubjectProfile:
    return SubjectProfile(suprafata_construita=Decimal("100"))


@pytest.mark.parametrize("val", [10**9, -5, 0, 51])
def test_f16_4_descopera_max_candidati_invalid_respins(val):
    with pytest.raises(ValidationError):
        DescoperaRequest(judet="cluj", localitate="x", subiect=_subiect(), max_candidati=val)


@pytest.mark.parametrize("val", [10**9, -5, 0, 51])
def test_f16_4_descopera_teren_max_candidati_invalid_respins(val):
    with pytest.raises(ValidationError):
        DescoperaTerenRequest(judet="cluj", max_candidati=val)


def test_f16_4_default_50_pastrat():
    assert DescoperaRequest(judet="cluj", localitate="x", subiect=_subiect()).max_candidati == 50
    assert DescoperaTerenRequest(judet="cluj").max_candidati == 50


@pytest.mark.parametrize("val", [1, 20, 50])
def test_f16_4_valori_in_interval_acceptate(val):
    assert DescoperaRequest(judet="cluj", localitate="x", subiect=_subiect(),
                            max_candidati=val).max_candidati == val
    assert DescoperaTerenRequest(judet="cluj", max_candidati=val).max_candidati == val


def test_f16_4_endpoint_descopera_max_candidati_uria_422(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/descopera", json={
        "judet": "cluj", "localitate": "cluj-napoca",
        "subiect": {"suprafata_construita": "100"}, "max_candidati": 10**9})
    assert r.status_code == 422


# ============================================================ F-16-5: OverflowError din _int_safe
class _EvilClient:
    def __init__(self, payload: str):
        self.payload = payload

    def complete(self, system, user):
        return self.payload


def test_f16_5_an_infinit_scalar_nu_crapa():
    ext = extrage_atribute("text", [("garaj", "da")],
                           _EvilClient('{"an": 1e400, "secundare": []}'))
    assert ext.profile.an is None   # OverflowError prins -> None, nu 500


def test_f16_5_an_infinit_dict_nu_crapa():
    ext = extrage_atribute("text", [("garaj", "da")],
                           _EvilClient('{"an": {"valoare": 1e400}, "secundare": []}'))
    assert ext.profile.an is None


def test_f16_5_int_safe_overflow_intoarce_none():
    from evaluare.discovery.extractor import _int_safe
    assert _int_safe(float("inf")) is None
    assert _int_safe(float("-inf")) is None
    assert _int_safe(float("nan")) is None
    assert _int_safe("2010") == 2010   # cazul normal inca merge
