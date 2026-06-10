"""Regresie RUNDA 9 (re-audit ultracode robustete): 7 cai input-netrusted -> 500, toate inchise.

a407aa4 a validat FORMATUL ISO al datelor AML, dar RUNDA 9 a gasit o clasa noua de erori 500 pe
build #4, ratata de 2 runde anterioare de testare:

  Clasa A (overflow aritmetic pe an): data ISO valida dar an absurd (9999) trecea de validatorul de
    format si crapa downstream in aritmetica de date — date(an>9999) (risc._adauga_luni),
    replace(year=...) (store._adauga_ani), +timedelta (raportare.suspendare_pana_la) -> 500.
    Fix: validatorii marginesc anul la [1900, 2200] (validare_data.verifica_an_plauzibil) -> 422.
  Clasa B (split-inainte-de-try): un data-URL fara virgula ("data:") -> split(",",1)[1] IndexError,
    ridicat INAINTE de try/except -> 500. Fix: `and "," in x` -> cade pe b64decode -> 4xx (sau poza
    sarita gratios la raport.docx).
  Clasa C (Infinity Decimal): JSON-LD price=1e400 -> json.loads -> float('inf') -> Decimal('Infinity')
    -> ParsedListing (pydantic finite_number) ValidationError neprinsa -> 500. Fix: _to_decimal taie
    non-finite la sursa + guard ValueError in routerul /api/import-anunt -> 200 (pret dezbracat) / 422.
"""
from decimal import Decimal

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

P = {"nume": "Ion", "prenume": "Pop"}


def _client(tmp_path):
    s = Storage(tmp_path / "t.db")
    s.init()

    def fake_pdf(docx):
        from pathlib import Path
        p = Path(docx).with_suffix(".pdf")
        p.write_bytes(b"%PDF-1.4 fake\n%%EOF")
        return p

    return TestClient(create_app(storage=s, client=None, pdf_converter=fake_pdf))


def _eval_payload() -> dict:
    return {
        "meta": {"client_nume": "Ion Popescu", "adresa": "Str. 1", "numar_cadastral": "123",
                 "carte_funciara": "CF123", "evaluator_nume": "Maria", "evaluator_legitimatie": "1",
                 "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                                   "cost_unitar": "2000", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                             {"varsta": 15, "depreciere": "0.15"}]},
        "valoare_teren": "100000", "metoda": "cost"}


# --------------------------------------------------------------------------- #
# Clasa A — an absurd (9999) -> 422, NU 500 (overflow aritmetic pe data)
# --------------------------------------------------------------------------- #
def test_runda9_aml_evalueaza_an_absurd_422(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/aml/evalueaza", json={"azi": "9999-12-31", "client_pf": {"persoana": P}})
    assert r.status_code == 422


def test_runda9_aml_evaluare_risc_docx_an_absurd_422(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/aml/evaluare-risc.docx", json={"azi": "9999-12-31", "client_pf": {"persoana": P}})
    assert r.status_code == 422


def test_runda9_aml_rtn_data_tranzactie_an_absurd_422(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/aml/rtn.docx", json={"azi": "2026-01-01",
               "rtn": {"suma_eur": "10000", "data_tranzactie": "9999-12-31"}})
    assert r.status_code == 422


def test_runda9_aml_rts_data_inregistrare_an_absurd_422(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/aml/rts.docx", json={"azi": "2026-01-01",
               "rts": {"motiv": "x", "data_inregistrare": "9999-12-31"}})
    assert r.status_code == 422


def test_runda9_aml_pep_data_incetare_an_absurd_422(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/aml/evalueaza", json={"azi": "2026-01-01",
               "client_pf": {"persoana": P,
                             "pep": {"este_pep": True, "data_incetare_functie": "9999-01-01"}}})
    assert r.status_code == 422


def test_runda9_aml_an_normal_inca_acceptat_200(tmp_path):
    # non-regresie: datele plauzibile raman acceptate (marginirea nu rupe fluxul normal)
    c = _client(tmp_path)
    r = c.post("/api/aml/rtn.docx", json={"azi": "2026-01-01",
               "rtn": {"suma_eur": "10000", "data_tranzactie": "2026-01-10"}})
    assert r.status_code == 200


# --------------------------------------------------------------------------- #
# Clasa B — data-URL fara virgula -> NU 500 (IndexError pe split[1])
# --------------------------------------------------------------------------- #
def test_runda9_ingestie_dataurl_fara_virgula_400(tmp_path):
    c = _client(tmp_path)
    r = c.post("/api/ingestie", json={"tip": "cf", "continut": "data:application/pdf;base64"})
    assert r.status_code == 400


def test_runda9_import_docx_dataurl_fara_virgula_nu_500(tmp_path):
    c = _client(tmp_path)
    c.post("/api/cont", json={"nume": "Adi", "legitimatie": "8717"})
    r = c.post("/api/dosar/import-docx", json={"nume_fisier": "x.docx", "continut": "data:"})
    assert r.status_code < 500


def test_runda9_raport_docx_foto_invalida_sarita_200(tmp_path):
    c = _client(tmp_path)
    eid = c.post("/api/evaluare",
                 json={**_eval_payload(), "photos": ["data:"], "documente": ["data:"]}).json()["id"]
    r = c.get(f"/api/evaluare/{eid}/raport.docx")
    assert r.status_code == 200   # poza/doc invalid -> sarit gratios, raportul se genereaza


# --------------------------------------------------------------------------- #
# Clasa C — Infinity Decimal -> NU 500 (ValidationError neprinsa)
# --------------------------------------------------------------------------- #
def test_runda9_import_anunt_jsonld_infinity_nu_500(tmp_path):
    c = _client(tmp_path)
    html = '<script type="application/ld+json">{"price": 1e400, "floorSize": 100}</script>'
    r = c.post("/api/import-anunt", json={"html": html, "url": "http://x"})
    assert r.status_code < 500   # Infinity dezbracat (pret=None), restul parseaza -> 200


def test_runda9_to_decimal_respinge_non_finite():
    from evaluare.importers.url_parser import _to_decimal, _to_decimal_ro
    assert _to_decimal(float("inf")) is None
    assert _to_decimal(float("nan")) is None
    assert _to_decimal(1e400) is None              # literal Python 1e400 == float('inf')
    assert _to_decimal_ro(float("inf")) is None
    assert _to_decimal("123.45") == Decimal("123.45")     # non-regresie: finit ramane valid
    assert _to_decimal_ro("351,46") == Decimal("351.46")  # non-regresie
