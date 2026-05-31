# Aplicația web locală (introducere manuală) — Implementation Plan (Plan 3/4)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** O aplicație web care rulează local (browser pe `localhost`), în care evaluatorul introduce datele unei case+teren, apasă un buton și descarcă raportul `.docx` — folosind motoarele și generatorul deja construite, cu activarea opțională a narativului AI prin cheie API.

**Architecture:** Server FastAPI peste biblioteca `evaluare`. Un strat de **config** citește cheia Anthropic dintr-un `.env` local (activarea AI). Un **assembler** transformă datele de intrare în rezultate (rulează motoarele) și produce `ReportContext`. Un strat de **storage** SQLite persistă dosarele pentru istoric/audit. Rutele FastAPI expun un **API JSON** (testabil cu TestClient) plus o **pagină HTML** simplă cu formular. Raportul `.docx` se generează la cerere și se descarcă.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, Jinja2, SQLite (stdlib), httpx (test), pytest. Reutilizează `evaluare.*` din Planurile 1-2.

**Spec sursă:** `docs/superpowers/specs/2026-05-31-agent-evaluare-anevar-mvp-design.md`.
**Depinde de:** Plan 1 (motoare) + Plan 2 (raport+AI). Branch curent: `feature/nucleu-calcul`.

**Decizii:** introducere manuală a datelor (inclusiv comparabile); activare AI prin `.env` (fallback fără cheie); raport `.docx` descărcabil; date stocate local (SQLite). Import URL și împachetare `.exe` = Planul 4.

---

## Structura de fișiere (Plan 3)

```
evaluare-anevar/
├── pyproject.toml                  # MODIFICAT: fastapi, uvicorn, jinja2, httpx(dev)
├── .gitignore                      # NOU: exclude .env, *.db, date/
├── src/evaluare/
│   ├── config.py                   # NOU: incarca .env, Settings, client AI
│   ├── assembler.py                # NOU: EvaluationInput -> ruleaza motoare -> ReportContext
│   ├── db/
│   │   ├── __init__.py             # NOU
│   │   └── storage.py              # NOU: SQLite save/load/list dosare
│   └── web/
│       ├── __init__.py             # NOU
│       ├── app.py                  # NOU: FastAPI (API JSON + pagina formular + download)
│       └── templates/
│           ├── form.html           # NOU: formular introducere date
│           └── result.html         # NOU: rezultat + buton download
└── tests/
    ├── test_config.py              # NOU
    ├── test_storage.py             # NOU
    ├── test_assembler.py           # NOU
    └── test_web_api.py             # NOU (TestClient, fara retea)
```

**Responsabilități:**
- `config.py` — singurul loc care știe de `.env` și de cheia API; produce clientul AI (sau `None`).
- `assembler.py` — orchestrarea motoarelor; nu știe de web, nu știe de SQLite.
- `db/storage.py` — persistența; nu știe de web.
- `web/app.py` — rutele HTTP; deleagă către assembler/storage/generator.

---

## Phase 0 — Dependențe și .gitignore

### Task 0: Adaugă dependențele web și `.gitignore`

**Files:**
- Modify: `pyproject.toml`
- Create: `.gitignore`

- [ ] **Step 1: Adaugă dependențele**

În `pyproject.toml`, blocul `dependencies` devine:
```toml
dependencies = [
    "pydantic>=2.6",
    "python-docx>=1.1",
    "anthropic>=0.40",
    "fastapi>=0.110",
    "uvicorn>=0.29",
    "jinja2>=3.1",
]
```
Și blocul `dev`:
```toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "httpx>=0.27"]
```

- [ ] **Step 2: Creează `.gitignore` (la `evaluare-anevar/.gitignore`)**

```gitignore
# Secrete si date locale - nu se urca niciodata in git
.env
*.db
date/
__pycache__/
*.pyc
.pytest_cache/
build/
dist/
*.spec
```

- [ ] **Step 3: Instalează**

Run (din `evaluare-anevar/`): `python -m pip install -e ".[dev]"`
Dacă rețeaua dă timeout: `python -m pip install --timeout 120 --retries 5 fastapi uvicorn jinja2 httpx`.

- [ ] **Step 4: Verifică importurile + suita existentă**

Run: `python -c "import fastapi, uvicorn, jinja2, httpx; print('ok')"` → `ok`.
Run: `python -m pytest -q` → 53 passed.

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/pyproject.toml evaluare-anevar/.gitignore
git commit -m "chore: dependinte web (fastapi/uvicorn/jinja2) + .gitignore"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 1 — Config și activarea AI

### Task 1: `config.py` — `.env`, Settings, client AI

**Files:**
- Create: `src/evaluare/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_config.py`:
```python
from evaluare.config import load_env_file, Settings


def test_load_env_file_sets_environ(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("ANTHROPIC_API_KEY=sk-test-123\nNARRATIVE_MODEL=claude-sonnet-4-6\n",
                   encoding="utf-8")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    load_env_file(env)
    import os
    assert os.environ["ANTHROPIC_API_KEY"] == "sk-test-123"


def test_settings_without_key_has_no_client(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    s = Settings.from_env()
    assert s.api_key is None
    assert s.narrative_client() is None      # fallback: fara AI


def test_settings_with_key_builds_client(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
    s = Settings.from_env()
    assert s.api_key == "sk-test-123"
    client = s.narrative_client()
    # construit, dar fara apel real (constructorul nu face request)
    assert client is not None
    assert client.__class__.__name__ == "AnthropicNarrativeClient"


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("NARRATIVE_MODEL", raising=False)
    s = Settings.from_env()
    assert s.model == "claude-sonnet-4-6"
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.config'`.

- [ ] **Step 3: Implementează `config.py`**

`src/evaluare/config.py`:
```python
"""Configurarea aplicatiei: incarcarea .env si activarea clientului AI."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from evaluare.ai.narrative import AnthropicNarrativeClient, NarrativeClient


def load_env_file(path: Path | str = ".env") -> None:
    """Incarca variabile dintr-un fisier .env in os.environ (nu suprascrie existente)."""
    path = Path(path)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


class Settings:
    """Setarile efective ale aplicatiei, citite din mediu."""

    def __init__(self, api_key: Optional[str], model: str, output_dir: Path, db_path: Path):
        self.api_key = api_key
        self.model = model
        self.output_dir = output_dir
        self.db_path = db_path

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.environ.get("ANTHROPIC_API_KEY") or None
        model = os.environ.get("NARRATIVE_MODEL", "claude-sonnet-4-6")
        output_dir = Path(os.environ.get("OUTPUT_DIR", "date"))
        db_path = Path(os.environ.get("DB_PATH", "date/evaluari.db"))
        return cls(api_key=api_key, model=model, output_dir=output_dir, db_path=db_path)

    def narrative_client(self) -> Optional[NarrativeClient]:
        """Clientul AI daca exista cheie; altfel None (fallback fara AI)."""
        if not self.api_key:
            return None
        return AnthropicNarrativeClient(api_key=self.api_key, model=self.model)
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_config.py -v`
Expected: PASS (4 teste). (Niciun apel API real — `AnthropicNarrativeClient.__init__` doar
construiește clientul SDK, nu trimite request.)

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/config.py evaluare-anevar/tests/test_config.py
git commit -m "feat: config (.env + Settings) si activarea clientului AI"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Persistență SQLite

### Task 2: `db/storage.py` — save/load/list dosare

**Files:**
- Create: `src/evaluare/db/__init__.py`  (empty)
- Create: `src/evaluare/db/storage.py`
- Test: `tests/test_storage.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_storage.py`:
```python
from decimal import Decimal

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.results import ReconciledResult
from evaluare.models.report_context import ReportContext
from evaluare.db.storage import Storage


def _ctx() -> ReportContext:
    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. 1", numar_cadastral="123",
        carte_funciara="CF123", evaluator_nume="Maria", evaluator_legitimatie="1",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    return ReportContext(
        meta=meta, land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("100"), acd=Decimal("120"), an_referinta=2025),
        reconciled=ReconciledResult(valoare_finala=Decimal("300000"), metoda_selectata="cost"),
    )


def test_save_and_load_roundtrip(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    eid = db.save(_ctx())
    loaded = db.load(eid)
    assert loaded.meta.client_nume == "Ion Popescu"
    assert loaded.reconciled.valoare_finala == Decimal("300000")


def test_list_returns_saved_summaries(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    db.save(_ctx())
    db.save(_ctx())
    rows = db.list()
    assert len(rows) == 2
    assert all(r["client_nume"] == "Ion Popescu" for r in rows)
    assert all("valoare_finala" in r for r in rows)


def test_load_missing_raises(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    import pytest
    with pytest.raises(KeyError):
        db.load(9999)
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_storage.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.db'`.

- [ ] **Step 3: Implementează `storage.py`**

`src/evaluare/db/__init__.py` — empty file.

`src/evaluare/db/storage.py`:
```python
"""Persistenta locala a dosarelor de evaluare (SQLite)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from evaluare.models.report_context import ReportContext


class Storage:
    """Stocheaza dosare ReportContext ca JSON, cu un sumar pentru listare."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(self.db_path))

    def init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluari (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_nume TEXT NOT NULL,
                    valoare_finala TEXT NOT NULL,
                    context_json TEXT NOT NULL
                )
                """
            )

    def save(self, ctx: ReportContext) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO evaluari (client_nume, valoare_finala, context_json) "
                "VALUES (?, ?, ?)",
                (
                    ctx.meta.client_nume,
                    str(ctx.reconciled.valoare_finala),
                    ctx.model_dump_json(),
                ),
            )
            return int(cur.lastrowid)

    def load(self, eid: int) -> ReportContext:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT context_json FROM evaluari WHERE id = ?", (eid,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Dosar inexistent: {eid}")
        return ReportContext.model_validate_json(row[0])

    def list(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, client_nume, valoare_finala FROM evaluari ORDER BY id DESC"
            ).fetchall()
        return [
            {"id": r[0], "client_nume": r[1], "valoare_finala": r[2]} for r in rows
        ]
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_storage.py -v`
Expected: PASS (3 teste).

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/db/__init__.py evaluare-anevar/src/evaluare/db/storage.py evaluare-anevar/tests/test_storage.py
git commit -m "feat: storage SQLite (save/load/list dosare)"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — Assembler (orchestrarea motoarelor)

### Task 3: `assembler.py` — input → ReportContext

**Files:**
- Create: `src/evaluare/assembler.py`
- Test: `tests/test_assembler.py`

**Context de design:** `EvaluationInput` este corpul cererii: `meta`, `land`, `building`,
`comparables`, `valoare_teren` (opțional), `metoda` (implicit "cost"). `construieste_context`
rulează motoarele: cost dacă există elemente; piață dacă există comparabile (cu suprafața
subiectului = `building.acd`); reconciliază; generează narativul (cu clientul AI dat sau fallback).

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_assembler.py`:
```python
from decimal import Decimal

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.comparable import Adjustment, Comparable
from evaluare.assembler import EvaluationInput, construieste_context


def _meta() -> EvaluationMeta:
    return EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. 1", numar_cadastral="123",
        carte_funciara="CF123", evaluator_nume="Maria", evaluator_legitimatie="1",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )


def _building_with_elements() -> BuildingData:
    return BuildingData(
        au=Decimal("100"), acd=Decimal("120"), an_referinta=2025,
        elements=[CostElement(element="S", cod="X", um="mp",
                              cantitate=Decimal("120"), cost_unitar=Decimal("2000"),
                              an_pif=2015)],
        depreciation_points=[DepreciationPoint(varsta=5, depreciere=Decimal("0.05")),
                             DepreciationPoint(varsta=15, depreciere=Decimal("0.15"))],
    )


def test_construieste_context_cost_only():
    inp = EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("500")),
        building=_building_with_elements(), comparables=[],
        valoare_teren=Decimal("100000"), metoda="cost",
    )
    ctx = construieste_context(inp, client=None)
    assert ctx.cost_result is not None
    assert ctx.market_result is None
    assert ctx.reconciled.metoda_selectata == "cost"
    # valoare prin cost = CIN + teren
    assert ctx.reconciled.valoare_finala == ctx.cost_result.valoare_cost
    # narativ fallback prezent
    assert len(ctx.narrative) > 0


def test_construieste_context_market():
    inp = EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("100"), acd=Decimal("120"), an_referinta=2025),
        comparables=[
            Comparable(pret=Decimal("360000"), suprafata=Decimal("120"),
                       adjustments=[Adjustment(element="A", tip="procentuala",
                                               valoare=Decimal("0.05"))]),
            Comparable(pret=Decimal("372000"), suprafata=Decimal("120")),
            Comparable(pret=Decimal("366000"), suprafata=Decimal("120")),
        ],
        metoda="piata",
    )
    ctx = construieste_context(inp, client=None)
    assert ctx.market_result is not None
    assert ctx.reconciled.metoda_selectata == "piata"
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_assembler.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează `assembler.py`**

`src/evaluare/assembler.py`:
```python
"""Orchestrarea motoarelor: din datele de intrare -> ReportContext complet."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.models.report_context import ReportContext
from evaluare.ai.narrative import generate_narrative, NarrativeClient
from evaluare.report.anonymizer import build_anonymizer
from evaluare.engine.cost import evaluate_cost
from evaluare.engine.market import evaluate_market
from evaluare.engine.reconciliation import reconcile


class EvaluationInput(BaseModel):
    """Datele de intrare ale unei evaluari (corpul cererii web)."""

    meta: EvaluationMeta
    land: LandData
    building: BuildingData
    comparables: list[Comparable] = Field(default_factory=list)
    land_comparables: list[LandComparable] = Field(default_factory=list)
    valoare_teren: Optional[Decimal] = None
    metoda: Literal["piata", "cost", "ponderata"] = "cost"
    pondere_piata: Decimal = Decimal("0.5")


def construieste_context(
    inp: EvaluationInput, client: Optional[NarrativeClient]
) -> ReportContext:
    """Ruleaza motoarele si asambleaza ReportContext (inclusiv narativul)."""
    cost_result = None
    if inp.building.elements:
        cost_result = evaluate_cost(inp.building, valoare_teren=inp.valoare_teren)

    market_result = None
    if inp.comparables:
        market_result = evaluate_market(inp.comparables, suprafata_subiect=inp.building.acd)

    reconciled = reconcile(
        market=market_result, cost=cost_result,
        metoda=inp.metoda, pondere_piata=inp.pondere_piata,
    )

    ctx = ReportContext(
        meta=inp.meta, land=inp.land, building=inp.building,
        comparables=inp.comparables, land_comparables=inp.land_comparables,
        cost_result=cost_result, market_result=market_result, reconciled=reconciled,
    )

    anonymizer = build_anonymizer(inp.meta)
    ctx.narrative = generate_narrative(ctx, client=client, anonymizer=anonymizer)
    return ctx
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_assembler.py -v`
Expected: PASS (2 teste). (client=None → narativ fallback; niciun apel AI.)

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/assembler.py evaluare-anevar/tests/test_assembler.py
git commit -m "feat: assembler (input -> motoare -> ReportContext)"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 4 — API FastAPI + download

### Task 4: `web/app.py` — API JSON (creare, citire, download .docx)

**Files:**
- Create: `src/evaluare/web/__init__.py`  (empty)
- Create: `src/evaluare/web/app.py`
- Test: `tests/test_web_api.py`

**Context de design:** `create_app(storage, client)` returnează o aplicație FastAPI cu storage și
client AI injectate (testabil cu un storage temporar și client=None). Rute:
- `POST /api/evaluare` — corp `EvaluationInput` → rulează assembler, salvează, întoarce `{id, valoare_finala, metoda}`
- `GET /api/evaluare/{id}` — întoarce sumarul dosarului
- `GET /api/evaluare/{id}/raport.docx` — generează și descarcă `.docx`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_web_api.py`:
```python
from decimal import Decimal

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


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
    storage = Storage(tmp_path / "t.db")
    storage.init()
    app = create_app(storage=storage, client=None)
    return TestClient(app)


def test_post_evaluare_returns_id_and_value(tmp_path):
    client = _client(tmp_path)
    resp = client.post("/api/evaluare", json=_payload())
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["metoda"] == "cost"
    assert Decimal(data["valoare_finala"]) > 0


def test_get_evaluare_returns_summary(tmp_path):
    client = _client(tmp_path)
    eid = client.post("/api/evaluare", json=_payload()).json()["id"]
    resp = client.get(f"/api/evaluare/{eid}")
    assert resp.status_code == 200
    assert resp.json()["client_nume"] == "Ion Popescu"


def test_download_raport_docx(tmp_path):
    client = _client(tmp_path)
    eid = client.post("/api/evaluare", json=_payload()).json()["id"]
    resp = client.get(f"/api/evaluare/{eid}/raport.docx")
    assert resp.status_code == 200
    ct = resp.headers["content-type"]
    assert "officedocument.wordprocessingml.document" in ct
    # un .docx este un fisier zip -> incepe cu "PK"
    assert resp.content[:2] == b"PK"


def test_get_missing_evaluare_404(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/api/evaluare/9999")
    assert resp.status_code == 404
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_api.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.web'`.

- [ ] **Step 3: Implementează `app.py`**

`src/evaluare/web/__init__.py` — empty file.

`src/evaluare/web/app.py`:
```python
"""Aplicatia web FastAPI: API JSON pentru evaluare + descarcare raport."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from evaluare.assembler import EvaluationInput, construieste_context
from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage
from evaluare.report.generator import genereaza_raport

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def create_app(storage: Storage, client: Optional[NarrativeClient]) -> FastAPI:
    """Construieste aplicatia cu storage si client AI injectate."""
    app = FastAPI(title="Evaluare ANEVAR")

    @app.post("/api/evaluare")
    def creeaza_evaluare(inp: EvaluationInput) -> dict:
        ctx = construieste_context(inp, client=client)
        eid = storage.save(ctx)
        return {
            "id": eid,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        }

    @app.get("/api/evaluare/{eid}")
    def citeste_evaluare(eid: int) -> dict:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        return {
            "id": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        }

    @app.get("/api/evaluare/{eid}/raport.docx")
    def descarca_raport(eid: int) -> FileResponse:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        out = Path(tempfile.gettempdir()) / f"raport_{eid}.docx"
        genereaza_raport(ctx, out)
        return FileResponse(str(out), media_type=DOCX_MIME, filename=f"raport_{eid}.docx")

    return app
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_api.py -v`
Expected: PASS (4 teste).

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/web/__init__.py evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/tests/test_web_api.py
git commit -m "feat: API FastAPI (creare evaluare, citire, download .docx)"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 5 — Pagina cu formular + pornire

### Task 5: Formular HTML + ruta de pornire

**Files:**
- Create: `src/evaluare/web/templates/form.html`
- Create: `src/evaluare/web/templates/result.html`
- Modify: `src/evaluare/web/app.py` (adaugă rutele HTML `/` și `/evaluare/{eid}` și montarea Jinja2)
- Create: `src/evaluare/__main__.py`  (pornire server + deschide browser)
- Test: `tests/test_web_pages.py`

**Context de design:** o pagină `/` cu formular care postează către `/api/evaluare` (prin fetch
JSON) și o pagină de rezultat. Formularul acoperă câmpurile esențiale; elementele de cost se adaugă
dinamic (un mic script). Testul verifică doar că paginile se încarcă (200) și conțin marcaje cheie —
nu testează JavaScript.

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_web_pages.py`:
```python
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_home_page_loads_form(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Evaluare" in resp.text
    assert "<form" in resp.text


def test_result_page_loads(tmp_path):
    client = _client(tmp_path)
    payload = {
        "meta": {"client_nume": "Ion Popescu", "adresa": "Str. 1",
                 "numar_cadastral": "123", "carte_funciara": "CF123",
                 "evaluator_nume": "Maria", "evaluator_legitimatie": "1",
                 "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp",
                                   "cantitate": "120", "cost_unitar": "2000", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                             {"varsta": 15, "depreciere": "0.15"}]},
        "valoare_teren": "100000", "metoda": "cost",
    }
    eid = client.post("/api/evaluare", json=payload).json()["id"]
    resp = client.get(f"/evaluare/{eid}")
    assert resp.status_code == 200
    assert "Ion Popescu" in resp.text
    assert "raport.docx" in resp.text   # link de descarcare
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_pages.py -v`
Expected: FAIL (rutele `/` și `/evaluare/{eid}` nu există încă).

- [ ] **Step 3a: Creează template-urile**

`src/evaluare/web/templates/form.html`:
```html
<!DOCTYPE html>
<html lang="ro">
<head><meta charset="utf-8"><title>Evaluare ANEVAR</title></head>
<body>
<h1>Evaluare imobiliara ANEVAR — casa + teren</h1>
<form id="f">
  <h2>Client si lucrare</h2>
  Nume client: <input name="client_nume" required><br>
  Adresa: <input name="adresa" required><br>
  Nr. cadastral: <input name="numar_cadastral" required><br>
  Carte funciara: <input name="carte_funciara" required><br>
  Evaluator: <input name="evaluator_nume" required>
  Legitimatie: <input name="evaluator_legitimatie" required><br>
  Data evaluarii: <input name="data_evaluarii" value="2026-01-16">
  Data raportului: <input name="data_raportului" value="2026-01-16"><br>
  <h2>Teren si constructie</h2>
  Suprafata teren (mp): <input name="suprafata_teren" value="500"><br>
  Au (mp): <input name="au" value="100">
  Acd (mp): <input name="acd" value="120">
  An referinta: <input name="an_referinta" value="2025"><br>
  Valoare teren (lei): <input name="valoare_teren" value="100000"><br>
  <h2>Elemente de cost (un rand per element)</h2>
  <textarea name="elemente" rows="4" cols="80"
   placeholder="element;cod;um;cantitate;cost_unitar;an_pif (cate unul pe linie)">Structura;X;mp;120;2000;2015</textarea><br>
  <h2>Depreciere fizica (puncte varsta;fractie)</h2>
  <textarea name="depreciere" rows="2" cols="40"
   placeholder="varsta;fractie">5;0.05
15;0.15</textarea><br>
  <button type="submit">Genereaza evaluarea</button>
</form>
<pre id="rezultat"></pre>
<script>
document.getElementById('f').addEventListener('submit', async (e) => {
  e.preventDefault();
  const d = Object.fromEntries(new FormData(e.target).entries());
  const elements = d.elemente.trim().split('\n').filter(Boolean).map(l => {
    const [element, cod, um, cantitate, cost_unitar, an_pif] = l.split(';');
    return {element, cod, um, cantitate, cost_unitar, an_pif: parseInt(an_pif)};
  });
  const depreciation_points = d.depreciere.trim().split('\n').filter(Boolean).map(l => {
    const [varsta, depreciere] = l.split(';');
    return {varsta: parseInt(varsta), depreciere};
  });
  const payload = {
    meta: {client_nume: d.client_nume, adresa: d.adresa,
           numar_cadastral: d.numar_cadastral, carte_funciara: d.carte_funciara,
           evaluator_nume: d.evaluator_nume, evaluator_legitimatie: d.evaluator_legitimatie,
           data_evaluarii: d.data_evaluarii, data_raportului: d.data_raportului},
    land: {suprafata: d.suprafata_teren},
    building: {au: d.au, acd: d.acd, an_referinta: parseInt(d.an_referinta),
               elements, depreciation_points},
    valoare_teren: d.valoare_teren, metoda: 'cost'
  };
  const r = await fetch('/api/evaluare', {method:'POST',
    headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  const res = await r.json();
  if (res.id) { window.location = '/evaluare/' + res.id; }
  else { document.getElementById('rezultat').textContent = JSON.stringify(res, null, 2); }
});
</script>
</body>
</html>
```

`src/evaluare/web/templates/result.html`:
```html
<!DOCTYPE html>
<html lang="ro">
<head><meta charset="utf-8"><title>Rezultat evaluare</title></head>
<body>
<h1>Rezultat evaluare</h1>
<p>Client: <strong>{{ client_nume }}</strong></p>
<p>Valoare finala: <strong>{{ valoare_finala }} LEI</strong> (metoda: {{ metoda }})</p>
<p><a href="/api/evaluare/{{ eid }}/raport.docx">Descarca raport.docx</a></p>
<p><a href="/">Evaluare noua</a></p>
</body>
</html>
```

- [ ] **Step 3b: Adaugă rutele HTML și Jinja2 în `app.py`**

În `src/evaluare/web/app.py`, adaugă importurile la început (lângă celelalte):
```python
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
```
Imediat după `def create_app(...) -> FastAPI:` și `app = FastAPI(...)`, adaugă:
```python
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
```
Apoi adaugă cele două rute (înainte de `return app`):
```python
    @app.get("/", response_class=HTMLResponse)
    def pagina_formular(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "form.html", {})

    @app.get("/evaluare/{eid}", response_class=HTMLResponse)
    def pagina_rezultat(request: Request, eid: int) -> HTMLResponse:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        return templates.TemplateResponse(request, "result.html", {
            "eid": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        })
```

- [ ] **Step 3c: Creează entry-point-ul de pornire**

`src/evaluare/__main__.py`:
```python
"""Pornire: incarca config, deschide browserul, ruleaza serverul local."""
from __future__ import annotations

import threading
import webbrowser

import uvicorn

from evaluare.config import load_env_file, Settings
from evaluare.db.storage import Storage
from evaluare.web.app import create_app

HOST = "127.0.0.1"
PORT = 8000


def main() -> None:
    load_env_file(".env")
    settings = Settings.from_env()
    storage = Storage(settings.db_path)
    storage.init()
    app = create_app(storage=storage, client=settings.narrative_client())

    threading.Timer(1.0, lambda: webbrowser.open(f"http://{HOST}:{PORT}/")).start()
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_pages.py -v`
Expected: PASS (2 teste). Apoi suita completă: `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/web/templates/form.html evaluare-anevar/src/evaluare/web/templates/result.html evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/src/evaluare/__main__.py evaluare-anevar/tests/test_web_pages.py
git commit -m "feat: pagina formular + rezultat + entry-point pornire server local"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 6 — Verificare finală

### Task 6: Rulează suita + verifică pornirea reală a serverului

**Files:** niciunul (verificare)

- [ ] **Step 1: Rulează toată suita**

Run: `python -m pytest -q`
Expected: toate testele trec (Plan 1 + 2 + 3).

- [ ] **Step 2: Pornește serverul real și verifică pagina (smoke manual automatizat)**

Run (din `evaluare-anevar/`, pe fundal, apoi oprește):
```bash
PYTHONPATH=src python -m uvicorn evaluare.web.app:create_app --factory --host 127.0.0.1 --port 8011 &
sleep 3
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8011/').status)"
```
Notă: `create_app` cere argumente, deci `--factory` simplu nu merge cu argumente. Pentru smoke,
folosește în schimb un mic script:
```bash
PYTHONPATH=src python -c "
import threading, time, urllib.request, uvicorn
from evaluare.db.storage import Storage
from evaluare.web.app import create_app
s = Storage('date/smoke.db'); s.init()
app = create_app(storage=s, client=None)
cfg = uvicorn.Config(app, host='127.0.0.1', port=8011, log_level='error')
server = uvicorn.Server(cfg)
t = threading.Thread(target=server.run, daemon=True); t.start()
time.sleep=__import__('time').sleep; time.sleep(2)
print('status', urllib.request.urlopen('http://127.0.0.1:8011/').status)
server.should_exit = True
"
```
Expected: `status 200`.

- [ ] **Step 3: Commit final (dacă a rămas ceva, ex. fișiere smoke de șters)**

```bash
git status
# sterge eventualele artefacte (date/smoke.db) daca apar
git add -A
git commit -m "test: verificare pornire server local" || echo "nimic de comis"
```

---

## Recapitulare acoperire spec (Plan 3)

| Cerință spec | Task |
|---|---|
| Aplicație web locală (browser, localhost) | Task 4, 5 |
| Introducere manuală a datelor | Task 5 (formular) |
| Activare AI prin cheie API (.env) + fallback | Task 1 |
| Persistență locală (SQLite, istoric/audit) | Task 2 |
| Orchestrarea motoarelor (calcul complet) | Task 3 |
| Descărcare raport .docx | Task 4 |
| Date rămân local (GDPR) | Task 1, 2 (.env + SQLite local, .gitignore) |
| Pornire cu deschidere automată a browserului | Task 5 (`__main__.py`) |

**Rămâne pentru Planul 4:** import comparabile prin paste URL (imobiliare.ro/storia.ro — necesită
decizie strategie: scraping direct vs API Apify), împachetare PyInstaller într-un `.exe` cu
dublu-click.

**Input necesar de la evaluator după Plan 3:** cheia API Anthropic în `.env` (pentru narativ real);
testarea aplicației pe o evaluare reală și compararea valorii cu un raport făcut manual.
