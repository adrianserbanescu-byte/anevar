# Grila de ajustări (UI) + cablare teren — Implementation Plan (B)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Expune grila de ajustări (tabel editabil) pentru teren și casă, calculează valoarea prin endpoint-uri, și cablează valoarea de teren (din grilă) în abordarea prin cost + alocare.

**Architecture:** Endpoint-uri `POST /api/grila-teren` (folosește `evaluate_land`) și `POST /api/grila-casa` (folosește `evaluate_market`) care întorc grila calculată (prețuri corectate, ajustare brută, comparabil selectat, valoare). Assembler-ul folosește `land_comparables` (dacă există) pentru a calcula `valoare_teren` și adaugă `land_result` + alocarea în `ReportContext`. Pagina nouă `/grila` cu tabele editabile (rânduri = elemente de ajustare, coloane = comparabile).

**Tech Stack:** Python 3.11+, FastAPI, pytest. Fără dependențe noi.

**Spec sursă:** `docs/superpowers/specs/2026-06-02-evaluare-teren-si-grila-ajustari-design.md`.
**Depinde de:** Plan A (motor teren). Branch: `master`.
**Reutilizat:** `engine/land.py::evaluate_land`, `engine/market.py::evaluate_market`,
`engine/reconciliation.py::aloca_constructii`, modelele `LandComparable`/`Comparable`/`LandResult`.

---

## Phase 1 — Endpoint-uri de calcul grilă

### Task 1: `POST /api/grila-teren` și `POST /api/grila-casa`

**Files:**
- Modify: `src/evaluare/web/app.py`
- Test: `tests/test_web_grila.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_web_grila.py`:
```python
from decimal import Decimal

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_grila_teren(tmp_path):
    client = _client(tmp_path)
    payload = {
        "suprafata_subiect": "1000",
        "comparabile": [
            {"pret_mp": "100", "suprafata": "450",
             "adjustments": [{"element": "A", "tip": "procentuala", "valoare": "0.05"}]},
            {"pret_mp": "120", "suprafata": "500",
             "adjustments": [{"element": "A", "tip": "procentuala", "valoare": "-0.30"}]},
        ],
    }
    resp = client.post("/api/grila-teren", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["index_selectat"] == 0
    assert Decimal(data["valoare_teren"]) == Decimal("105000.00")


def test_grila_casa(tmp_path):
    client = _client(tmp_path)
    payload = {
        "suprafata_subiect": "100",
        "comparabile": [
            {"pret": "500000", "suprafata": "100",
             "adjustments": [{"element": "A", "tip": "procentuala", "valoare": "0.05"}]},
            {"pret": "520000", "suprafata": "100",
             "adjustments": [{"element": "A", "tip": "procentuala", "valoare": "-0.20"}]},
            {"pret": "510000", "suprafata": "100", "adjustments": []},
        ],
    }
    resp = client.post("/api/grila-casa", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "valoare_piata" in data
    assert "index_selectat" in data
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_grila.py -v`
Expected: FAIL (404).

- [ ] **Step 3: Adaugă endpoint-urile în `app.py`**

Importuri (lângă celelalte):
```python
from decimal import Decimal as _Decimal
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.engine.land import evaluate_land
from evaluare.engine.market import evaluate_market
```
Modele de cerere (la nivel de modul, lângă `ImportUrlRequest`):
```python
class GrilaTerenRequest(BaseModel):
    suprafata_subiect: _Decimal
    comparabile: list[LandComparable]


class GrilaCasaRequest(BaseModel):
    suprafata_subiect: _Decimal
    comparabile: list[Comparable]
```
Rute în `create_app`, înainte de `return app`:
```python
    @app.post("/api/grila-teren")
    def grila_teren(req: GrilaTerenRequest) -> dict:
        r = evaluate_land(req.comparabile, req.suprafata_subiect)
        return {
            "preturi_mp_corectate": [str(p) for p in r.preturi_mp_corectate],
            "ajustari_brute": [str(b) for b in r.ajustari_brute],
            "index_selectat": r.index_selectat,
            "pret_mp_ales": str(r.pret_mp_ales),
            "valoare_teren": str(r.valoare_teren),
        }

    @app.post("/api/grila-casa")
    def grila_casa(req: GrilaCasaRequest) -> dict:
        r = evaluate_market(req.comparabile, req.suprafata_subiect)
        return {
            "preturi_unitare_corectate": [str(p) for p in r.preturi_unitare_corectate],
            "ajustari_brute": [str(b) for b in r.ajustari_brute],
            "index_selectat": r.index_selectat,
            "valoare_piata": str(r.valoare_piata),
        }
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_grila.py -v`
Expected: PASS (2 teste). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/tests/test_web_grila.py
git commit -m "feat: endpoint-uri /api/grila-teren si /api/grila-casa (calcul grila)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Cablarea terenului în assembler + alocare

### Task 2: `construieste_context` folosește grila de teren + alocare

**Files:**
- Modify: `src/evaluare/models/report_context.py` (adaugă land_result, alocare)
- Modify: `src/evaluare/assembler.py`
- Test: `tests/test_assembler.py` (extinde)

- [ ] **Step 1: Scrie testul care eșuează**

Adaugă în `tests/test_assembler.py`:
```python
def test_valoare_teren_din_grila_de_teren():
    from evaluare.models.comparable import Adjustment, LandComparable
    inp = EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("1000")),
        building=_building_with_elements(),
        land_comparables=[
            LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("450"),
                           adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("0.05"))]),
        ],
        metoda="cost",
    )
    ctx = construieste_context(inp, client=None)
    # valoare teren = 105 EUR/mp * 1000 mp = 105000 (din grila, NU din valoare_teren manual)
    assert ctx.land_result is not None
    assert ctx.land_result.valoare_teren == Decimal("105000.00")
    # alocarea exista
    assert ctx.alocare_constructii is not None
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_assembler.py::test_valoare_teren_din_grila_de_teren -v`
Expected: FAIL (ctx nu are land_result).

- [ ] **Step 3a: Adaugă câmpuri în `ReportContext`**

În `src/evaluare/models/report_context.py`, adaugă importul:
```python
from evaluare.models.results import CostResult, MarketResult, ReconciledResult, LandResult
```
(înlocuiește linia existentă de import results cu cea care include `LandResult`)
Și adaugă câmpurile în clasa `ReportContext` (după `reconciled`):
```python
    land_result: Optional[LandResult] = None
    alocare_constructii: Optional[Decimal] = None
```
(asigură `Decimal` importat: `from decimal import Decimal`)

- [ ] **Step 3b: Modifică `construieste_context` în `assembler.py`**

Adaugă importurile:
```python
from evaluare.engine.land import evaluate_land
from evaluare.engine.reconciliation import reconcile, aloca_constructii
```
(linia `reconcile` există deja — extinde-o cu `aloca_constructii`)

Înlocuiește blocul de calcul (de la `cost_result = None` până la crearea `ctx`) cu:
```python
    # teren: daca exista comparabile de teren, valoarea se calculeaza prin grila
    land_result = None
    valoare_teren = inp.valoare_teren
    if inp.land_comparables:
        land_result = evaluate_land(inp.land_comparables, inp.land.suprafata)
        valoare_teren = land_result.valoare_teren

    cost_result = None
    if inp.building.elements:
        cost_result = evaluate_cost(inp.building, valoare_teren=valoare_teren)

    market_result = None
    if inp.comparables:
        market_result = evaluate_market(inp.comparables, suprafata_subiect=inp.building.acd)

    reconciled = reconcile(
        market=market_result, cost=cost_result,
        metoda=inp.metoda, pondere_piata=inp.pondere_piata,
    )

    alocare = None
    if valoare_teren is not None:
        alocare = aloca_constructii(reconciled.valoare_finala, valoare_teren)

    ctx = ReportContext(
        meta=inp.meta, land=inp.land, building=inp.building,
        comparables=inp.comparables, land_comparables=inp.land_comparables,
        cost_result=cost_result, market_result=market_result, reconciled=reconciled,
        land_result=land_result, alocare_constructii=alocare,
    )
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_assembler.py -v`
Expected: PASS. Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/models/report_context.py evaluare-anevar/src/evaluare/assembler.py evaluare-anevar/tests/test_assembler.py
git commit -m "feat: valoare teren din grila de comparatie in cost + alocare in context"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — Pagina de grilă editabilă

### Task 3: pagina `/grila` (tabel teren + tabel casă) — construită direct la execuție

**Files:**
- Create: `src/evaluare/web/templates/grila.html`
- Modify: `src/evaluare/web/app.py` (ruta `GET /grila`)
- Test: `tests/test_web_grila.py` (extinde)

**Context de design:** pagina conține două grile editabile:
- **Grilă teren:** rânduri = preț (EUR/mp) + cele 17 elemente procentuale; coloane = 3 comparabile;
  buton „Calculează" → `POST /api/grila-teren` → afișează prețuri corectate, ajustare brută,
  comparabilul selectat, valoarea terenului.
- **Grilă casă:** rânduri = preț + suprafață + elementele de casă (procentuale și valorice — marcate);
  buton „Calculează" → `POST /api/grila-casa`.
JS-ul construiește `adjustments` per comparabil din celulele non-goale (tip = procentuală/valorică
după element). Catalogul de elemente e definit în JS.

- [ ] **Step 1: Extinde testul**

Adaugă în `tests/test_web_grila.py`:
```python
def test_pagina_grila_se_incarca(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/grila")
    assert resp.status_code == 200
    assert "Grilă teren" in resp.text
    assert "Grilă casă" in resp.text
    assert "/api/grila-teren" in resp.text
    assert "/api/grila-casa" in resp.text
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_grila.py::test_pagina_grila_se_incarca -v`
Expected: FAIL (404).

- [ ] **Step 3: Creează `grila.html` și ruta**

Adaugă ruta în `app.py` (înainte de `return app`):
```python
    @app.get("/grila", response_class=HTMLResponse)
    def pagina_grila(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "grila.html", {})
```
Creează `src/evaluare/web/templates/grila.html` cu: titlu, două secțiuni („Grilă teren" și
„Grilă casă"), fiecare cu un tabel editabil construit din JS pe baza catalogului de elemente,
input pentru suprafața subiectului și numărul de comparabile (implicit 3), buton „Calculează" care
apelează endpoint-ul respectiv și afișează rezultatul (prețuri corectate, ajustare brută per
comparabil, comparabilul selectat evidențiat, valoarea finală). Referă explicit string-urile
„/api/grila-teren" și „/api/grila-casa" în JS. (HTML-ul complet se redactează la execuție.)

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_grila.py -v`
Expected: PASS. Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/src/evaluare/web/templates/grila.html evaluare-anevar/tests/test_web_grila.py
git commit -m "feat: pagina /grila (tabele editabile teren + casa cu calcul)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 4 — Verificare + împachetare

### Task 4: Suită + rebuild exe + link în wizard

**Files:**
- Modify: `src/evaluare/web/templates/wizard.html` (link către `/grila`)

- [ ] **Step 1: Adaugă link către grilă în wizard** (lângă linkurile alternative din header)
```html
 · <a href="/grila">grilă detaliată (teren + casă)</a>
```

- [ ] **Step 2: Suită completă**

Run: `python -m pytest -q` → toate verzi.

- [ ] **Step 3: Rebuild + smoke**

Run (din `evaluare-anevar/`, oprește exe-urile vechi): `python -m PyInstaller --noconfirm --clean evaluare-anevar.spec` apoi copiază `.env` în `dist/`. Pornește exe-ul și verifică `GET /grila` → 200.

- [ ] **Step 4: Commit final**
```bash
git add -A
git commit -m "feat: link grila in wizard + rebuild" || echo "nimic"
```

---

## Recapitulare acoperire spec (Plan B)

| Cerință spec | Task |
|---|---|
| Endpoint calcul grilă teren | Task 1 |
| Endpoint calcul grilă casă | Task 1 |
| Valoare teren din grilă → cost | Task 2 |
| Alocarea valorii în context | Task 2 |
| UI grilă editabilă (teren + casă) | Task 3 |
| Integrare (link din wizard) | Task 4 |

**Rămâne ulterior:** pre-popularea grilelor cu comparabilele descoperite (preț/suprafață),
afișarea grilei de teren + alocării în raportul .docx, validarea pe cele 4 seturi reale.
