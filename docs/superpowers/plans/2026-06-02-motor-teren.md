# Motor evaluare teren prin comparație — Implementation Plan (A)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Motorul determinist de evaluare a terenului prin grilă de comparație (3 comparabile, ajustări secvențiale, selecție pe ajustare brută minimă, valoare = preț_unitar × suprafață), plus alocarea valorii (V_construcții = V_proprietate − V_teren). Reutilizează mecanica grilei de casă.

**Architecture:** Modul nou `engine/land.py` care reutilizează aplicarea ajustărilor și indicatorii din `engine/market.py` (funcționează pe `.adjustments`), dar pornește de la prețul EUR/mp direct. Model `LandResult` în `models/results.py`. Helper de alocare în `engine/reconciliation.py`.

**Tech Stack:** Python 3.11+, Pydantic v2, pytest. Fără dependențe noi.

**Spec sursă:** `docs/superpowers/specs/2026-06-02-evaluare-teren-si-grila-ajustari-design.md`.
**Depinde de:** motorul existent. Branch: `master` (lucrăm direct, e ramura curentă curată).
**Reutilizat:** `models/comparable.py::LandComparable` (are deja `pret_mp`, `suprafata`, `adjustments`),
`models/comparable.py::Adjustment` (procentuală/valorică), `engine/market.py::ajustare_bruta/ajustare_neta`.

**Rămâne pentru Plan B:** UI grilă detaliată (tabel ajustări) + cablarea valorii de teren calculate în
abordarea prin cost și în formular/wizard.

---

## Phase 1 — Model rezultat teren

### Task 1: `LandResult` în `models/results.py`

**Files:**
- Modify: `src/evaluare/models/results.py`
- Test: `tests/test_results_models.py` (extinde)

- [ ] **Step 1: Scrie testul care eșuează**

Adaugă în `tests/test_results_models.py`:
```python
def test_land_result_fields():
    from evaluare.models.results import LandResult
    r = LandResult(
        preturi_mp_corectate=[Decimal("15.77"), Decimal("20")],
        ajustari_brute=[Decimal("0.14"), Decimal("0.27")],
        ajustari_nete=[Decimal("-0.04"), Decimal("0.10")],
        index_selectat=0,
        pret_mp_ales=Decimal("15.77"),
        valoare_teren=Decimal("44000"),
    )
    assert r.index_selectat == 0
    assert r.valoare_teren == Decimal("44000")
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_results_models.py::test_land_result_fields -v`
Expected: FAIL cu `ImportError: cannot import name 'LandResult'`.

- [ ] **Step 3: Adaugă modelul în `results.py`**

La finalul `src/evaluare/models/results.py`:
```python
class LandResult(BaseModel):
    """Rezultatul evaluarii terenului prin grila de comparatie."""

    preturi_mp_corectate: list[Decimal] = Field(default_factory=list)
    ajustari_brute: list[Decimal] = Field(default_factory=list)
    ajustari_nete: list[Decimal] = Field(default_factory=list)
    index_selectat: int
    pret_mp_ales: Decimal
    valoare_teren: Decimal
```
(Dacă `Field` nu e importat în fișier, adaugă `from pydantic import BaseModel, Field`.)

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_results_models.py -v`
Expected: PASS.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/models/results.py evaluare-anevar/tests/test_results_models.py
git commit -m "feat: model LandResult (rezultat evaluare teren)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Motorul de teren

### Task 2: `engine/land.py`

**Files:**
- Create: `src/evaluare/engine/land.py`
- Test: `tests/test_land.py`

**Context de design:** terenul are preț în EUR/mp (`LandComparable.pret_mp`). Ajustările (toate
procentuale în practică, dar suportăm și valorice) se aplică secvențial pe prețul curent. Selecția =
comparabilul cu ajustare brută minimă. Valoarea = preț_mp_corectat_ales × suprafață_subiect.
Indicatorii `ajustare_bruta`/`ajustare_neta` se reutilizează din `engine/market.py` (operează pe
`.adjustments`).

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_land.py`:
```python
from decimal import Decimal

from evaluare.models.comparable import Adjustment, LandComparable
from evaluare.engine.land import pret_mp_corectat, evaluate_land


def test_pret_mp_corectat_secvential():
    c = LandComparable(pret_mp=Decimal("20"), suprafata=Decimal("500"),
                       adjustments=[
                           Adjustment(element="Ofertă→Tranzacție", tip="procentuala", valoare=Decimal("-0.10")),
                           Adjustment(element="Deschidere", tip="procentuala", valoare=Decimal("0.10")),
                       ])
    # 20 * 0.90 * 1.10 = 19.80
    assert pret_mp_corectat(c) == Decimal("19.80")


def test_pret_mp_corectat_valorica():
    c = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("400"),
                       adjustments=[Adjustment(element="X", tip="valorica", valoare=Decimal("5"))])
    assert pret_mp_corectat(c) == Decimal("105")


def test_evaluate_land_selecteaza_ajustare_bruta_minima():
    # comp0: ajustare bruta 0.05 ; comp1: 0.30 -> selecteaza comp0
    c0 = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("450"),
                        adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("0.05"))])
    c1 = LandComparable(pret_mp=Decimal("120"), suprafata=Decimal("500"),
                        adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("-0.30"))])
    r = evaluate_land([c0, c1], suprafata_subiect=Decimal("1000"))
    assert r.index_selectat == 0
    # pret corectat comp0 = 100 * 1.05 = 105 ; valoare = 105 * 1000 = 105000
    assert r.pret_mp_ales == Decimal("105.00")
    assert r.valoare_teren == Decimal("105000.00")
    assert r.ajustari_brute[0] == Decimal("0.05")


def test_evaluate_land_fara_comparabile_ridica():
    import pytest
    with pytest.raises(ValueError):
        evaluate_land([], suprafata_subiect=Decimal("1000"))
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_land.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.engine.land'`.

- [ ] **Step 3: Implementează `land.py`**

`src/evaluare/engine/land.py`:
```python
"""Evaluarea terenului prin grila de comparatie directa (EUR/mp).

Mecanica identica cu grila de casa: ajustari secventiale, selectie pe ajustare bruta minima.
Difera doar pretul de pornire (EUR/mp direct) si formula valorii (pret_mp x suprafata).
"""
from __future__ import annotations

from decimal import Decimal

from evaluare.models.comparable import LandComparable
from evaluare.models.results import LandResult
from evaluare.engine.market import ajustare_bruta, ajustare_neta


def pret_mp_corectat(comp: LandComparable) -> Decimal:
    """Aplica ajustarile secvential pe pretul EUR/mp (procentual: *(1+v); valoric: +v)."""
    pret = comp.pret_mp
    for adj in comp.adjustments:
        if adj.tip == "procentuala":
            pret = pret * (Decimal("1") + adj.valoare)
        else:
            pret = pret + adj.valoare
    return pret


def evaluate_land(
    comparables: list[LandComparable], suprafata_subiect: Decimal
) -> LandResult:
    """Ruleaza grila de teren si selecteaza comparabilul cu ajustare bruta minima.

    Valoarea terenului = pret_mp corectat al comparabilului ales * suprafata subiectului.
    """
    if not comparables:
        raise ValueError("Sunt necesare comparabile de teren.")
    preturi = [pret_mp_corectat(c) for c in comparables]
    brute = [ajustare_bruta(c) for c in comparables]
    nete = [ajustare_neta(c) for c in comparables]
    index = min(range(len(comparables)), key=lambda i: brute[i])
    pret_ales = preturi[index]
    valoare = pret_ales * suprafata_subiect
    return LandResult(
        preturi_mp_corectate=preturi, ajustari_brute=brute, ajustari_nete=nete,
        index_selectat=index, pret_mp_ales=pret_ales, valoare_teren=valoare,
    )
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_land.py -v`
Expected: PASS (4 teste). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/engine/land.py evaluare-anevar/tests/test_land.py
git commit -m "feat: motor evaluare teren prin grila de comparatie (EUR/mp, selectie ajustare bruta minima)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — Alocarea valorii

### Task 3: helper de alocare în `engine/reconciliation.py`

**Files:**
- Modify: `src/evaluare/engine/reconciliation.py`
- Test: `tests/test_reconciliation.py` (extinde)

- [ ] **Step 1: Scrie testul care eșuează**

Adaugă în `tests/test_reconciliation.py`:
```python
def test_aloca_constructii():
    from evaluare.engine.reconciliation import aloca_constructii
    # V_constructii = V_proprietate - V_teren
    assert aloca_constructii(Decimal("300000"), Decimal("100000")) == Decimal("200000")
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_reconciliation.py::test_aloca_constructii -v`
Expected: FAIL cu `ImportError: cannot import name 'aloca_constructii'`.

- [ ] **Step 3: Adaugă funcția în `reconciliation.py`**

La finalul `src/evaluare/engine/reconciliation.py`:
```python
def aloca_constructii(
    valoare_proprietate: Decimal, valoare_teren: Decimal
) -> Decimal:
    """Alocarea valorii (din rapoarte): valoarea constructiilor = proprietate - teren."""
    return valoare_proprietate - valoare_teren
```
(Asigură-te că `Decimal` e importat în fișier.)

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_reconciliation.py -v`
Expected: PASS. Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/engine/reconciliation.py evaluare-anevar/tests/test_reconciliation.py
git commit -m "feat: alocarea valorii (V_constructii = V_proprietate - V_teren)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 4 — Verificare

### Task 4: Suită completă

- [ ] **Step 1: Rulează toată suita**

Run: `python -m pytest -q`
Expected: toate testele trec (inclusiv motorul de teren + alocare).

- [ ] **Step 2: Commit final (dacă a rămas ceva)**
```bash
git status
git add -A && git commit -m "test: verificare motor teren" || echo "nimic de comis"
```

---

## Recapitulare acoperire spec (Plan A)

| Cerință spec | Task |
|---|---|
| Motor teren: ajustări secvențiale EUR/mp | Task 2 |
| Selecție pe ajustare brută minimă | Task 2 (reutilizează market) |
| Valoare teren = preț_mp_ales × suprafață | Task 2 |
| Model rezultat teren | Task 1 |
| Alocarea valorii (V_construcții) | Task 3 |

**Rămâne (Plan B):** UI grilă detaliată (tabel ajustări teren + casă), cablarea valorii de teren
calculate în abordarea prin cost (`valoare_cost = CIN + valoare_teren_grila`), afișarea alocării și
a grilei de teren în rezultate/raport, regresie pe cele 4 seturi reale (evaluatorul introduce grila
reală și compară valoarea).
