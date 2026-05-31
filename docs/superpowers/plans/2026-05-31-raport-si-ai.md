# Raport SEV 103 + AI narativ — Implementation Plan (Plan 2/3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformă rezultatele nucleului de calcul (Plan 1) într-un raport de evaluare `.docx` conform SEV 103, cu narativ generat de Claude (Anthropic) și anonimizare a datelor personale înainte de orice apel API.

**Architecture:** Trei module noi peste biblioteca `evaluare` existentă: (1) `report.anonymizer` — maschează datele personale și le restaurează; (2) `ai.narrative` — generează textul capitolelor prin Claude, cu client injectabil (testabil fără rețea) și fallback fără cheie; (3) `report.generator` — asamblează un `.docx` SEV 103 (7 capitole, tabel grilă comparație, tabel costuri segregate) cu `python-docx`. Un model agregat `ReportContext` leagă datele de proprietate, comparabilele și rezultatele motoarelor într-un singur obiect de intrare.

**Tech Stack:** Python 3.11+, Pydantic v2, `python-docx`, `anthropic` SDK (cu prompt caching), pytest.

**Spec sursă:** `docs/superpowers/specs/2026-05-31-agent-evaluare-anevar-mvp-design.md` (secțiunile 6 AI narativ, 7 Generarea raportului).
**Depinde de:** Plan 1 (nucleu calcul) — modele și motoare în `src/evaluare/`. Branch curent: `feature/nucleu-calcul`.

**Decizii confirmate:** furnizor AI = Anthropic Claude; template = generic SEV 103 inspirat din structura modelului GBF; format = `.docx` editabil; strategie = API cloud cu anonimizare; fallback fără cheie = placeholdere de text (numerele rămân complete).

---

## Structura de fișiere (Plan 2)

```
evaluare-anevar/
├── pyproject.toml                  # MODIFICAT: adauga python-docx, anthropic
├── src/evaluare/
│   ├── models/
│   │   ├── meta.py                 # NOU: EvaluationMeta (client, scop, date, evaluator)
│   │   ├── narrative.py            # NOU: NarrativeSection
│   │   └── report_context.py       # NOU: ReportContext (agregatul de intrare al raportului)
│   ├── report/
│   │   ├── __init__.py             # NOU
│   │   ├── anonymizer.py           # NOU: mascare/demascare date personale
│   │   └── generator.py            # NOU: genereaza .docx SEV 103
│   └── ai/
│       ├── __init__.py             # NOU
│       └── narrative.py            # NOU: client Claude injectabil + fallback
└── tests/
    ├── test_meta_models.py         # NOU
    ├── test_anonymizer.py          # NOU
    ├── test_narrative.py           # NOU (cu client fals, fara retea)
    └── test_report_generator.py    # NOU (genereaza .docx si il reciteste)
```

**Responsabilități:**
- `models/meta.py` — datele administrative ale lucrării (cine, ce scop, ce date).
- `models/narrative.py` — o secțiune de text generat (capitol + text).
- `models/report_context.py` — agregă tot ce are nevoie raportul, ca generatorul să primească un singur obiect.
- `report/anonymizer.py` — un singur loc pentru regulile GDPR de mascare; nu știe despre AI sau docx.
- `ai/narrative.py` — singurul loc care vorbește cu Claude; client injectabil ⇒ testabil offline.
- `report/generator.py` — singurul loc care produce `.docx`; nu face calcule, nu cheamă AI.

---

## Phase 0 — Dependențe

### Task 0: Adaugă python-docx și anthropic

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Adaugă dependențele**

În `pyproject.toml`, înlocuiește blocul `dependencies = [...]` cu:
```toml
dependencies = [
    "pydantic>=2.6",
    "python-docx>=1.1",
    "anthropic>=0.40",
]
```

- [ ] **Step 2: Instalează**

Run (din `evaluare-anevar/`): `python -m pip install -e ".[dev]"`
Expected: instalare reușită a `python-docx` și `anthropic` (plus dependențele lor).
Dacă rețeaua dă timeout, reia cu `python -m pip install --timeout 120 --retries 5 python-docx anthropic`.

- [ ] **Step 3: Verifică importurile**

Run: `python -c "import docx, anthropic; print('ok')"`
Expected: `ok`.

- [ ] **Step 4: Confirmă suita existentă încă trece**

Run: `python -m pytest -q`
Expected: 38 passed.

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/pyproject.toml
git commit -m "chore: adauga python-docx si anthropic pentru raport+AI"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină mesajul cu linia:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 1 — Modele agregate

### Task 1: `models/meta.py` și `models/narrative.py`

**Files:**
- Create: `src/evaluare/models/meta.py`
- Create: `src/evaluare/models/narrative.py`
- Test: `tests/test_meta_models.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_meta_models.py`:
```python
from evaluare.models.meta import EvaluationMeta
from evaluare.models.narrative import NarrativeSection


def test_evaluation_meta_required_and_defaults():
    m = EvaluationMeta(
        client_nume="Ion Popescu",
        adresa="Str. Exemplu nr. 1, Bucuresti",
        numar_cadastral="123456",
        carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu",
        evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16",
        data_raportului="2026-01-16",
    )
    assert m.client_tip == "Persoana fizica"          # default
    assert m.scop == "Garantarea creditului ipotecar"  # default
    assert m.moneda == "LEI"                            # default
    assert m.client_nume == "Ion Popescu"


def test_narrative_section():
    s = NarrativeSection(capitol="Analiza pietei", text="Piata locala...")
    assert s.capitol == "Analiza pietei"
    assert s.text == "Piata locala..."
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_meta_models.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.models.meta'`.

- [ ] **Step 3: Implementează modelele**

`src/evaluare/models/meta.py`:
```python
"""Datele administrative ale lucrarii de evaluare."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class EvaluationMeta(BaseModel):
    """Identificarea lucrarii: client, scop, date, evaluator."""

    client_nume: str
    client_tip: str = "Persoana fizica"
    adresa: str
    numar_cadastral: str
    carte_funciara: str
    scop: str = "Garantarea creditului ipotecar"
    tip_valoare: str = "Valoarea de piata (SEV 104)"
    data_evaluarii: str                 # ISO sau text, ex. "2026-01-16"
    data_raportului: str
    valabilitate: Optional[str] = None
    evaluator_nume: str
    evaluator_legitimatie: str
    moneda: str = "LEI"
```

`src/evaluare/models/narrative.py`:
```python
"""Sectiuni de text narativ generate pentru raport."""
from __future__ import annotations

from pydantic import BaseModel


class NarrativeSection(BaseModel):
    """Un capitol de text narativ (titlu + continut)."""

    capitol: str
    text: str
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_meta_models.py -v`
Expected: PASS (2 teste).

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/models/meta.py evaluare-anevar/src/evaluare/models/narrative.py evaluare-anevar/tests/test_meta_models.py
git commit -m "feat: modele meta lucrare + sectiune narativa"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

### Task 2: `models/report_context.py` — agregatul de intrare

**Files:**
- Create: `src/evaluare/models/report_context.py`
- Test: `tests/test_report_context.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_report_context.py`:
```python
from decimal import Decimal

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.results import CostResult, ReconciledResult
from evaluare.models.report_context import ReportContext


def _meta() -> EvaluationMeta:
    return EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )


def test_report_context_holds_everything():
    ctx = ReportContext(
        meta=_meta(),
        land=LandData(suprafata=Decimal("500")),
        building=BuildingData(
            au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
            elements=[CostElement(element="S", cod="X", um="mp",
                                  cantitate=Decimal("10"), cost_unitar=Decimal("100"),
                                  an_pif=2015)],
            depreciation_points=[DepreciationPoint(varsta=10, depreciere=Decimal("0.1"))],
        ),
        comparables=[],
        cost_result=CostResult(cib=Decimal("1000"), vcp=Decimal("10"),
                               depreciere_fizica=Decimal("0.1"), cin=Decimal("900"),
                               valoare_cost=Decimal("1400")),
        market_result=None,
        reconciled=ReconciledResult(valoare_finala=Decimal("1400"),
                                    metoda_selectata="cost"),
    )
    assert ctx.meta.client_nume == "Ion Popescu"
    assert ctx.reconciled.valoare_finala == Decimal("1400")
    assert ctx.market_result is None
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_report_context.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează modelul**

`src/evaluare/models/report_context.py`:
```python
"""Agregatul care leaga toate datele necesare generarii raportului."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.models.results import CostResult, MarketResult, ReconciledResult
from evaluare.models.narrative import NarrativeSection


class ReportContext(BaseModel):
    """Tot ce are nevoie generatorul de raport, intr-un singur obiect."""

    meta: EvaluationMeta
    land: LandData
    building: BuildingData
    comparables: list[Comparable] = Field(default_factory=list)
    land_comparables: list[LandComparable] = Field(default_factory=list)
    cost_result: Optional[CostResult] = None
    market_result: Optional[MarketResult] = None
    reconciled: ReconciledResult
    narrative: list[NarrativeSection] = Field(default_factory=list)
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_report_context.py -v`
Expected: PASS (1 test).

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/models/report_context.py evaluare-anevar/tests/test_report_context.py
git commit -m "feat: ReportContext (agregat de intrare pentru raport)"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Anonimizare (GDPR)

### Task 3: `report/anonymizer.py`

**Files:**
- Create: `src/evaluare/report/__init__.py`  (empty)
- Create: `src/evaluare/report/anonymizer.py`
- Test: `tests/test_anonymizer.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_anonymizer.py`:
```python
from evaluare.models.meta import EvaluationMeta
from evaluare.report.anonymizer import build_anonymizer


def _meta() -> EvaluationMeta:
    return EvaluationMeta(
        client_nume="Ion Popescu",
        adresa="Str. Exemplu nr. 1, Bucuresti",
        numar_cadastral="123456",
        carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )


def test_mask_removes_personal_data():
    anon = build_anonymizer(_meta())
    text = "Proprietatea lui Ion Popescu de pe Str. Exemplu nr. 1, Bucuresti, cad. 123456, CF123456."
    masked = anon.mask(text)
    assert "Ion Popescu" not in masked
    assert "Str. Exemplu nr. 1, Bucuresti" not in masked
    assert "123456" not in masked
    assert "CF123456" not in masked
    assert "[CLIENT]" in masked
    assert "[ADRESA]" in masked
    assert "[CADASTRAL]" in masked
    assert "[CF]" in masked


def test_unmask_restores_personal_data():
    anon = build_anonymizer(_meta())
    masked = "Proprietatea [CLIENT] de pe [ADRESA], cad. [CADASTRAL], [CF]."
    restored = anon.unmask(masked)
    assert "Ion Popescu" in restored
    assert "Str. Exemplu nr. 1, Bucuresti" in restored
    assert "123456" in restored
    assert "CF123456" in restored


def test_mask_then_unmask_roundtrip():
    anon = build_anonymizer(_meta())
    text = "Ion Popescu, Str. Exemplu nr. 1, Bucuresti, 123456, CF123456."
    assert anon.unmask(anon.mask(text)) == text


def test_empty_fields_are_skipped():
    meta = _meta()
    meta.carte_funciara = ""
    anon = build_anonymizer(meta)
    # nu trebuie sa inlocuiasca string gol (ar corupe tot textul)
    assert anon.mask("text oarecare") == "text oarecare"
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_anonymizer.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.report'`.

- [ ] **Step 3: Implementează anonimizatorul**

`src/evaluare/report/__init__.py` — empty file.

`src/evaluare/report/anonymizer.py`:
```python
"""Anonimizarea datelor personale inainte de orice apel AI (GDPR).

Inlocuieste valorile sensibile cu marcaje (token-uri) inainte de trimitere si
le restaureaza dupa primirea textului. Cea mai lunga valoare se inlocuieste
prima, ca o valoare sa nu fie subsir al alteia.
"""
from __future__ import annotations

from pydantic import BaseModel

from evaluare.models.meta import EvaluationMeta


class Anonymizer(BaseModel):
    """Pereche de mapari real<->token pentru mascare/demascare."""

    real_to_token: dict[str, str]

    def mask(self, text: str) -> str:
        """Inlocuieste valorile reale cu token-uri (cele mai lungi intai)."""
        result = text
        for real in sorted(self.real_to_token, key=len, reverse=True):
            result = result.replace(real, self.real_to_token[real])
        return result

    def unmask(self, text: str) -> str:
        """Inlocuieste token-urile la loc cu valorile reale."""
        result = text
        for real, token in self.real_to_token.items():
            result = result.replace(token, real)
        return result


def build_anonymizer(meta: EvaluationMeta) -> Anonymizer:
    """Construieste anonimizatorul din datele personale ale lucrarii."""
    candidates = {
        meta.client_nume: "[CLIENT]",
        meta.adresa: "[ADRESA]",
        meta.numar_cadastral: "[CADASTRAL]",
        meta.carte_funciara: "[CF]",
        meta.evaluator_nume: "[EVALUATOR]",
    }
    real_to_token = {real: token for real, token in candidates.items() if real}
    return Anonymizer(real_to_token=real_to_token)
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_anonymizer.py -v`
Expected: PASS (4 teste).

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/report/__init__.py evaluare-anevar/src/evaluare/report/anonymizer.py evaluare-anevar/tests/test_anonymizer.py
git commit -m "feat: anonimizare date personale (mask/unmask) pentru GDPR"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — AI narativ (Claude)

### Task 4: `ai/narrative.py` — client injectabil + fallback

**Files:**
- Create: `src/evaluare/ai/__init__.py`  (empty)
- Create: `src/evaluare/ai/narrative.py`
- Test: `tests/test_narrative.py`

**Context de design:** narativul nu trebuie să atingă rețeaua în teste. Definim un protocol
`NarrativeClient` (o metodă `complete(system, user) -> str`). `generate_narrative` primește un
client (sau `None`). Cu `None` → fallback cu placeholdere. Implementarea reală cu Claude
(`AnthropicNarrativeClient`) folosește SDK-ul `anthropic` cu **prompt caching** pe blocul de
sistem (regulile SEV se repetă la fiecare capitol). Datele trimise sunt **deja anonimizate**;
textul primit este **demascat** local.

- [ ] **Step 1: Scrie testul care eșuează (folosește un client fals, fără rețea)**

`tests/test_narrative.py`:
```python
from decimal import Decimal

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.results import ReconciledResult, CostResult
from evaluare.models.report_context import ReportContext
from evaluare.report.anonymizer import build_anonymizer
from evaluare.ai.narrative import generate_narrative, CAPITOLE_NARATIVE


def _ctx() -> ReportContext:
    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    return ReportContext(
        meta=meta,
        land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("322.75"), acd=Decimal("351.46"),
                              an_referinta=2025),
        cost_result=CostResult(cib=Decimal("2000000"), vcp=Decimal("34"),
                               depreciere_fizica=Decimal("0.35"), cin=Decimal("1300000"),
                               valoare_cost=Decimal("1400000")),
        reconciled=ReconciledResult(valoare_finala=Decimal("1400000"),
                                    metoda_selectata="cost"),
    )


class FakeClient:
    """Client de test: intoarce un text si retine ce a primit."""

    def __init__(self):
        self.calls = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        # raspuns care contine un token, ca sa verificam demascarea
        return "Proprietatea [CLIENT] are valoarea estimata."


def test_generate_narrative_produces_one_section_per_chapter():
    ctx = _ctx()
    client = FakeClient()
    anon = build_anonymizer(ctx.meta)
    sections = generate_narrative(ctx, client=client, anonymizer=anon)
    assert len(sections) == len(CAPITOLE_NARATIVE)
    assert {s.capitol for s in sections} == set(CAPITOLE_NARATIVE)


def test_generate_narrative_unmasks_client_data():
    ctx = _ctx()
    client = FakeClient()
    anon = build_anonymizer(ctx.meta)
    sections = generate_narrative(ctx, client=client, anonymizer=anon)
    # textul demascat trebuie sa contina numele real, nu token-ul
    assert all("Ion Popescu" in s.text for s in sections)
    assert all("[CLIENT]" not in s.text for s in sections)


def test_generate_narrative_never_sends_real_client_name_to_client():
    ctx = _ctx()
    client = FakeClient()
    anon = build_anonymizer(ctx.meta)
    generate_narrative(ctx, client=client, anonymizer=anon)
    # niciun prompt trimis catre client nu contine numele real
    for system, user in client.calls:
        assert "Ion Popescu" not in system
        assert "Ion Popescu" not in user


def test_fallback_without_client_returns_placeholders():
    ctx = _ctx()
    sections = generate_narrative(ctx, client=None, anonymizer=None)
    assert len(sections) == len(CAPITOLE_NARATIVE)
    assert all(s.text.strip() for s in sections)   # placeholder ne-gol
    assert any("[de completat" in s.text.lower() for s in sections)
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_narrative.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.ai'`.

- [ ] **Step 3: Implementează modulul narativ**

`src/evaluare/ai/__init__.py` — empty file.

`src/evaluare/ai/narrative.py`:
```python
"""Generarea narativului raportului prin Claude (Anthropic), cu fallback.

Datele trimise sunt deja anonimizate; textul primit este demascat local.
Clientul este injectabil pentru testare fara retea.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional, Protocol

from evaluare.models.report_context import ReportContext
from evaluare.models.narrative import NarrativeSection
from evaluare.report.anonymizer import Anonymizer

# Capitolele analitice pentru care AI genereaza text (numerele raman deterministe).
CAPITOLE_NARATIVE = [
    "Prezentarea datelor de piata",
    "Descrierea juridica si fizica a proprietatii",
    "Analiza celei mai bune utilizari (CMBU)",
    "Justificarea ajustarilor aplicate",
    "Reconcilierea rezultatelor si concluzia valorii",
]

SYSTEM_PROMPT = (
    "Esti un evaluator imobiliar autorizat ANEVAR. Scrii sectiuni de raport de "
    "evaluare in limba romana, profesional si conform standardelor SEV (editia in "
    "vigoare). Folosesti EXCLUSIV datele numerice furnizate; nu inventezi si nu "
    "modifici cifre. Pastrezi marcajele de forma [CLIENT], [ADRESA], [CADASTRAL], "
    "[CF], [EVALUATOR] exact cum apar. Scrii doar textul capitolului cerut, fara titlu."
)


class NarrativeClient(Protocol):
    """Interfata minima a unui client de generare text."""

    def complete(self, system: str, user: str) -> str:
        ...


def _facts(ctx: ReportContext) -> str:
    """Construieste un rezumat textual al datelor calculate (date de intrare AI)."""
    linii = [
        f"Scop evaluare: {ctx.meta.scop}.",
        f"Tip valoare: {ctx.meta.tip_valoare}. Moneda: {ctx.meta.moneda}.",
        f"Suprafata teren: {ctx.land.suprafata} mp; categorie: {ctx.land.categorie}.",
        f"Arie utila (Au): {ctx.building.au} mp; arie construita desfasurata (Acd): "
        f"{ctx.building.acd} mp; an referinta: {ctx.building.an_referinta}.",
        f"Valoare finala reconciliata: {ctx.reconciled.valoare_finala} "
        f"{ctx.meta.moneda} (metoda: {ctx.reconciled.metoda_selectata}).",
    ]
    if ctx.cost_result is not None:
        c = ctx.cost_result
        linii.append(
            f"Abordarea prin cost: CIB={c.cib}, Vcp={c.vcp} ani, "
            f"depreciere fizica={c.depreciere_fizica}, CIN={c.cin}, "
            f"valoare prin cost={c.valoare_cost}."
        )
    if ctx.market_result is not None:
        m = ctx.market_result
        linii.append(
            f"Abordarea prin piata: valoare={m.valoare_piata}, "
            f"comparabil selectat index {m.index_selectat}, "
            f"numar comparabile={len(ctx.comparables)}."
        )
    return "\n".join(linii)


def _placeholder(capitol: str) -> str:
    return f"[de completat: {capitol}. Generare AI dezactivata - introduceti textul manual.]"


def generate_narrative(
    ctx: ReportContext,
    client: Optional[NarrativeClient],
    anonymizer: Optional[Anonymizer],
) -> list[NarrativeSection]:
    """Genereaza cate o sectiune narativa per capitol.

    Fara client -> placeholdere. Cu client: trimite datele anonimizate si
    demascheaza raspunsul.
    """
    if client is None:
        return [NarrativeSection(capitol=c, text=_placeholder(c)) for c in CAPITOLE_NARATIVE]

    facts = _facts(ctx)
    if anonymizer is not None:
        facts = anonymizer.mask(facts)

    sections: list[NarrativeSection] = []
    for capitol in CAPITOLE_NARATIVE:
        user = (
            f"Capitol de redactat: {capitol}.\n\n"
            f"Date calculate (deja anonimizate):\n{facts}\n\n"
            f"Scrie textul acestui capitol."
        )
        raw = client.complete(SYSTEM_PROMPT, user)
        text = anonymizer.unmask(raw) if anonymizer is not None else raw
        sections.append(NarrativeSection(capitol=capitol, text=text))
    return sections


class AnthropicNarrativeClient:
    """Client real Claude (Anthropic) cu prompt caching pe blocul de sistem."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6",
                 max_tokens: int = 1024):
        import anthropic  # import local: nu e necesar in testele cu client fals

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def complete(self, system: str, user: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=[{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": user}],
        )
        return "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        )
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_narrative.py -v`
Expected: PASS (4 teste). (Testele folosesc `FakeClient`; `AnthropicNarrativeClient` nu e
instanțiat în teste, deci nu se face niciun apel real.)

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/ai/__init__.py evaluare-anevar/src/evaluare/ai/narrative.py evaluare-anevar/tests/test_narrative.py
git commit -m "feat: narativ AI (client Claude injectabil, anonimizare, fallback)"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 4 — Generator raport .docx

### Task 5: `report/generator.py` — capitole + tabele

**Files:**
- Create: `src/evaluare/report/generator.py`
- Test: `tests/test_report_generator.py`

**Context de design:** `genereaza_raport(ctx, output_path)` produce un `.docx` cu cele 7 capitole
SEV 103. Capitolele 1-5,7 conțin date din `meta`/`land`/`building`/`reconciled` + textul narativ
(dacă există în `ctx.narrative`). Capitolul 6 conține tabelele: grila de comparație (dacă există
`market_result`) și tabelul costurilor segregate (dacă există elemente). Testul generează fișierul
într-un `tmp_path` și îl recitește cu `python-docx` ca să verifice că textul-cheie e prezent.

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_report_generator.py`:
```python
from decimal import Decimal

from docx import Document

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.results import CostResult, ReconciledResult
from evaluare.models.report_context import ReportContext
from evaluare.models.narrative import NarrativeSection
from evaluare.report.generator import genereaza_raport


def _ctx() -> ReportContext:
    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1, Bucuresti",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    return ReportContext(
        meta=meta,
        land=LandData(suprafata=Decimal("500"), categorie="intravilan"),
        building=BuildingData(
            au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
            elements=[
                CostElement(element="Structura", cod="X", um="mp",
                            cantitate=Decimal("100"), cost_unitar=Decimal("2000"),
                            an_pif=2015),
            ],
            depreciation_points=[DepreciationPoint(varsta=10, depreciere=Decimal("0.1"))],
        ),
        cost_result=CostResult(cib=Decimal("200000"), vcp=Decimal("10"),
                               depreciere_fizica=Decimal("0.10"), cin=Decimal("180000"),
                               valoare_cost=Decimal("280000")),
        reconciled=ReconciledResult(valoare_finala=Decimal("280000"),
                                    metoda_selectata="cost"),
        narrative=[NarrativeSection(capitol="Analiza celei mai bune utilizari (CMBU)",
                                    text="Cea mai buna utilizare este cea rezidentiala.")],
    )


def _all_text(path) -> str:
    doc = Document(str(path))
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


def test_genereaza_raport_creeaza_fisier(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    assert out.exists()
    # se deschide ca document Word valid
    Document(str(out))


def test_raportul_contine_datele_cheie(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    text = _all_text(out)
    assert "Ion Popescu" in text
    assert "Garantarea creditului ipotecar" in text
    assert "280000" in text                       # valoarea finala
    assert "CIN" in text or "180000" in text       # tabel cost
    assert "Cea mai buna utilizare" in text        # narativ inserat


def test_raportul_are_cele_sapte_capitole(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    doc = Document(str(out))
    headings = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
    titlu = "\n".join(headings)
    for nr in ["1.", "2.", "3.", "4.", "5.", "6.", "7."]:
        assert nr in titlu
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_report_generator.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.report.generator'`.

- [ ] **Step 3: Implementează generatorul**

`src/evaluare/report/generator.py`:
```python
"""Generator de raport .docx conform structurii SEV 103 (7 capitole)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from docx import Document
from docx.document import Document as DocxDocument

from evaluare.models.report_context import ReportContext


def _narativ(ctx: ReportContext, capitol: str) -> Optional[str]:
    """Returneaza textul narativ pentru un capitol, daca exista."""
    for sectiune in ctx.narrative:
        if sectiune.capitol == capitol:
            return sectiune.text
    return None


def _adauga_grila_comparatie(doc: DocxDocument, ctx: ReportContext) -> None:
    if ctx.market_result is None or not ctx.comparables:
        doc.add_paragraph("Abordarea prin piata nu a fost aplicata (a se vedea reconcilierea).")
        return
    doc.add_paragraph("Grila de comparatie directa:")
    m = ctx.market_result
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Comparabil"
    hdr[1].text = "Pret unitar corectat"
    hdr[2].text = "Ajustare bruta"
    hdr[3].text = "Selectat"
    for i, comp in enumerate(ctx.comparables):
        pret = m.preturi_unitare_corectate[i] if i < len(m.preturi_unitare_corectate) else ""
        bruta = m.ajustari_brute[i] if i < len(m.ajustari_brute) else ""
        row = table.add_row().cells
        row[0].text = f"{i}"
        row[1].text = str(pret)
        row[2].text = str(bruta)
        row[3].text = "DA" if i == m.index_selectat else ""


def _adauga_tabel_cost(doc: DocxDocument, ctx: ReportContext) -> None:
    if not ctx.building.elements:
        return
    doc.add_paragraph("Tabelul costurilor segregate:")
    table = doc.add_table(rows=1, cols=5)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Element"
    hdr[1].text = "Cod"
    hdr[2].text = "Cantitate"
    hdr[3].text = "Cost unitar"
    hdr[4].text = "Cost de nou"
    for el in ctx.building.elements:
        row = table.add_row().cells
        row[0].text = el.element
        row[1].text = el.cod
        row[2].text = str(el.cantitate)
        row[3].text = str(el.cost_unitar)
        row[4].text = str(el.cost_nou())
    if ctx.cost_result is not None:
        c = ctx.cost_result
        doc.add_paragraph(
            f"CIB = {c.cib}; Vcp = {c.vcp} ani; depreciere fizica = {c.depreciere_fizica}; "
            f"CIN = {c.cin}."
        )


def genereaza_raport(ctx: ReportContext, output_path: Path | str) -> Path:
    """Construieste si salveaza raportul .docx. Returneaza calea fisierului."""
    doc = Document()
    meta = ctx.meta

    doc.add_heading("RAPORT DE EVALUARE", level=0)

    # 1. Sinteza evaluarii si certificare
    doc.add_heading("1. SINTEZA EVALUARII SI CERTIFICARE", level=1)
    doc.add_paragraph(f"Client: {meta.client_nume} ({meta.client_tip}).")
    doc.add_paragraph(f"Proprietatea: {meta.adresa}; nr. cadastral {meta.numar_cadastral}; "
                      f"{meta.carte_funciara}.")
    doc.add_paragraph(f"Scopul evaluarii: {meta.scop}.")
    doc.add_paragraph(f"Tipul valorii: {meta.tip_valoare}.")
    doc.add_paragraph(f"Data evaluarii: {meta.data_evaluarii}; data raportului: "
                      f"{meta.data_raportului}.")
    doc.add_paragraph(
        f"VALOAREA ESTIMATA: {ctx.reconciled.valoare_finala} {meta.moneda} "
        f"(metoda selectata: {ctx.reconciled.metoda_selectata}). "
        f"{'Valoarea nu contine TVA.' if ctx.reconciled.valoare_fara_tva else ''}"
    )
    doc.add_paragraph(
        f"Declar pe proprie raspundere independenta evaluatorului si absenta conflictelor "
        f"de interese. Evaluator: {meta.evaluator_nume}, legitimatia "
        f"{meta.evaluator_legitimatie}."
    )

    # 2. Ipoteze generale si speciale
    doc.add_heading("2. IPOTEZE GENERALE SI SPECIALE", level=1)
    doc.add_paragraph(_narativ(ctx, "Ipoteze generale si speciale")
                      or "Ipoteze limitative standard privind structura de rezistenta si solul.")

    # 3. Prezentarea datelor de piata
    doc.add_heading("3. PREZENTAREA DATELOR DE PIATA", level=1)
    doc.add_paragraph(_narativ(ctx, "Prezentarea datelor de piata")
                      or "Analiza pietei locale [de completat].")

    # 4. Descrierea juridica si fizica
    doc.add_heading("4. DESCRIEREA JURIDICA SI FIZICA A PROPRIETATII", level=1)
    doc.add_paragraph(f"Teren: {ctx.land.suprafata} mp, categorie {ctx.land.categorie}.")
    doc.add_paragraph(f"Constructie: Au {ctx.building.au} mp, Acd {ctx.building.acd} mp, "
                      f"an referinta {ctx.building.an_referinta}.")
    descriere = _narativ(ctx, "Descrierea juridica si fizica a proprietatii")
    if descriere:
        doc.add_paragraph(descriere)

    # 5. Analiza CMBU
    doc.add_heading("5. ANALIZA CELEI MAI BUNE UTILIZARI (CMBU)", level=1)
    doc.add_paragraph(_narativ(ctx, "Analiza celei mai bune utilizari (CMBU)")
                      or "Analiza CMBU [de completat].")

    # 6. Aplicarea metodelor de calcul
    doc.add_heading("6. APLICAREA METODELOR DE CALCUL", level=1)
    _adauga_grila_comparatie(doc, ctx)
    _adauga_tabel_cost(doc, ctx)
    justificare = _narativ(ctx, "Justificarea ajustarilor aplicate")
    if justificare:
        doc.add_paragraph(justificare)

    # 7. Reconcilierea si concluzia valorii
    doc.add_heading("7. RECONCILIEREA REZULTATELOR SI CONCLUZIA VALORII", level=1)
    doc.add_paragraph(_narativ(ctx, "Reconcilierea rezultatelor si concluzia valorii")
                      or "Reconcilierea metodelor [de completat].")
    doc.add_paragraph(
        f"Valoarea finala: {ctx.reconciled.valoare_finala} {meta.moneda}. "
        f"{'Valoarea exprimata nu contine TVA.' if ctx.reconciled.valoare_fara_tva else ''}"
    )

    output_path = Path(output_path)
    doc.save(str(output_path))
    return output_path
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_report_generator.py -v`
Expected: PASS (3 teste).

- [ ] **Step 5: Commit (din repo root)**

```bash
git add evaluare-anevar/src/evaluare/report/generator.py evaluare-anevar/tests/test_report_generator.py
git commit -m "feat: generator raport .docx SEV 103 (capitole + tabele grila/cost)"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 5 — Verificare finală

### Task 6: Smoke test end-to-end (calcul → narativ fallback → .docx)

**Files:**
- Test: `tests/test_end_to_end.py`

- [ ] **Step 1: Scrie testul end-to-end**

`tests/test_end_to_end.py`:
```python
from decimal import Decimal

from docx import Document

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.report_context import ReportContext
from evaluare.engine.cost import evaluate_cost
from evaluare.engine.reconciliation import reconcile
from evaluare.ai.narrative import generate_narrative
from evaluare.report.generator import genereaza_raport


def test_full_pipeline_cost_only(tmp_path):
    # date casa + teren, doar abordarea prin cost (fara comparabile)
    building = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        elements=[
            CostElement(element="Structura", cod="X", um="mp",
                        cantitate=Decimal("351.46"), cost_unitar=Decimal("5725.67"),
                        an_pif=2015),
        ],
        depreciation_points=[
            DepreciationPoint(varsta=5, depreciere=Decimal("0.05")),
            DepreciationPoint(varsta=15, depreciere=Decimal("0.15")),
        ],
    )
    cost = evaluate_cost(building, valoare_teren=Decimal("100000"))
    reconciled = reconcile(market=None, cost=cost, metoda="cost")

    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1, Bucuresti",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    ctx = ReportContext(meta=meta, land=LandData(suprafata=Decimal("500")),
                        building=building, cost_result=cost, market_result=None,
                        reconciled=reconciled)
    # fara client AI -> placeholdere
    ctx.narrative = generate_narrative(ctx, client=None, anonymizer=None)

    out = tmp_path / "raport_complet.docx"
    genereaza_raport(ctx, out)
    assert out.exists()
    doc = Document(str(out))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Ion Popescu" in text
    assert str(reconciled.valoare_finala) in text
```

- [ ] **Step 2: Rulează testul end-to-end**

Run: `python -m pytest tests/test_end_to_end.py -v`
Expected: PASS (1 test).

- [ ] **Step 3: Rulează întreaga suită**

Run: `python -m pytest -q`
Expected: toate testele trec (Plan 1 + Plan 2).

- [ ] **Step 4: Commit (din repo root)**

```bash
git add evaluare-anevar/tests/test_end_to_end.py
git commit -m "test: smoke end-to-end calcul -> raport .docx"
```
Nu folosi `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Recapitulare acoperire spec (Plan 2)

| Cerință spec | Task |
|---|---|
| Anonimizare date personale înainte de apel AI (GDPR) | Task 3 |
| Narativ AI din date calculate, fără a inventa numere | Task 4 |
| Client Claude cu prompt caching + fallback fără cheie | Task 4 |
| Demascare locală a textului primit | Task 4 |
| Raport .docx cu cele 7 capitole SEV 103 | Task 5 |
| Tabel grilă comparație + tabel costuri segregate | Task 5 |
| Pipeline complet calcul → raport | Task 6 |
| Model administrativ (client, scop, evaluator) | Task 1 |
| Agregat de intrare pentru raport | Task 2 |

**Rămâne pentru Planul 3:** aplicația web FastAPI/HTMX, importatori (manual + URL imobiliare.ro/storia.ro),
SQLite (istoric/audit), împachetare PyInstaller într-un `.exe`.

**Input necesar de la evaluator după Plan 2:** o cheie API Anthropic (pentru a activa narativul real),
plus un raport de garantare credit real pentru a rafina template-ul și a verifica calitatea textului.
