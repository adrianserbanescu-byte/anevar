# Nucleul de calcul — Evaluare casă + teren — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construiește biblioteca Python deterministă care calculează valoarea unei case + teren prin abordarea prin piață (grila de comparație) și prin cost (CIN, costuri segregate), apoi le reconciliază — cu teste de regresie pe modelul real GBF.

**Architecture:** Bibliotecă pură Python (fără I/O, fără web, fără AI) organizată în module cu o singură responsabilitate: modele de date (Pydantic v2), `cost` engine, `market` engine, `reconciliation`, `validation`. Toate calculele folosesc `Decimal` pentru precizie monetară. Fiecare motor e testat independent cu valori cunoscute.

**Tech Stack:** Python 3.11+, Pydantic v2, pytest, `decimal.Decimal`.

Acesta este **Planul 1 din 3** pentru MVP-ul de evaluare ANEVAR. Produce o bibliotecă testabilă care generează valorile corecte. Planurile următoare adaugă: (2) generarea raportului .docx + AI narativ; (3) aplicația web FastAPI + importatori + împachetare PyInstaller.

**Spec sursă:** `docs/superpowers/specs/2026-05-31-agent-evaluare-anevar-mvp-design.md`

---

## Structura de fișiere (Planul 1)

```
evaluare-anevar/
├── pyproject.toml                  # config proiect + pytest
├── src/evaluare/
│   ├── __init__.py
│   ├── money.py                    # helper Decimal (parsare, rotunjire)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── property.py             # LandData, BuildingData, CostElement, DepreciationPoint
│   │   ├── comparable.py           # Comparable, LandComparable, Adjustment, AdjustmentGrid
│   │   └── results.py              # CostResult, MarketResult, ReconciledResult
│   └── engine/
│       ├── __init__.py
│       ├── cost.py                 # CIB segregat, Vcp, depreciere, CIN, valoare teren
│       ├── market.py               # preț unitar, ajustări ierarhice, indicatori, selecție
│       ├── reconciliation.py       # reconciliere piață vs cost
│       └── validation.py           # loops de validare (blochează/alertează)
└── tests/
    ├── __init__.py
    ├── test_money.py
    ├── test_cost.py                # regresie pe modelul GBF
    ├── test_market.py
    ├── test_reconciliation.py
    └── test_validation.py
```

**Responsabilități:**
- `money.py` — un singur loc pentru conversii și rotunjiri Decimal, ca toate motoarele să fie consistente.
- `models/property.py` — datele de intrare fizice (teren + construcție + elemente de cost).
- `models/comparable.py` — comparabilele și grila de ajustări.
- `models/results.py` — structurile de ieșire (rezultatele fiecărui motor).
- `engine/cost.py` — abordarea prin cost; nu știe nimic despre piață.
- `engine/market.py` — abordarea prin piață; nu știe nimic despre cost.
- `engine/reconciliation.py` — combină cele două rezultate.
- `engine/validation.py` — verificări transversale înainte de raport.

---

## Phase 0 — Scaffold proiect

### Task 0: Inițializare proiect și pytest

**Files:**
- Create: `pyproject.toml`
- Create: `src/evaluare/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Creează `pyproject.toml`**

```toml
[project]
name = "evaluare-anevar"
version = "0.1.0"
description = "Nucleu de calcul pentru evaluare imobiliara ANEVAR (casa + teren)"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.6",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

- [ ] **Step 2: Creează fișierele de pachet goale**

`src/evaluare/__init__.py`:
```python
"""Nucleu de calcul pentru evaluare imobiliara ANEVAR."""
```

`tests/__init__.py`:
```python
```

- [ ] **Step 3: Instalează dependențele**

Run: `python -m pip install -e ".[dev]"`
Expected: instalare reușită a `pydantic` și `pytest`.

- [ ] **Step 4: Verifică pytest rulează (fără teste încă)**

Run: `python -m pytest -q`
Expected: `no tests ran` (exit code 5) — confirmă că pytest funcționează.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/evaluare/__init__.py tests/__init__.py
git commit -m "chore: scaffold proiect evaluare-anevar + pytest"
```

---

## Phase 1 — Helper monetar (Decimal)

### Task 1: `money.py` — conversie și rotunjire consistentă

**Files:**
- Create: `src/evaluare/money.py`
- Test: `tests/test_money.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_money.py`:
```python
from decimal import Decimal

from evaluare.money import to_money, round_lei, pct


def test_to_money_from_float_and_str():
    assert to_money(919) == Decimal("919")
    assert to_money("1398.9") == Decimal("1398.9")
    assert to_money(128.90) == Decimal("128.90")


def test_round_lei_rounds_to_whole_lei_half_up():
    assert round_lei(Decimal("118459.1")) == Decimal("118459")
    assert round_lei(Decimal("118459.5")) == Decimal("118460")


def test_pct_converts_percentage_to_fraction():
    assert pct(35) == Decimal("0.35")
    assert pct(Decimal("4.71")) == Decimal("0.0471")
```

- [ ] **Step 2: Rulează testul ca să confirmi eșecul**

Run: `python -m pytest tests/test_money.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.money'`.

- [ ] **Step 3: Implementează `money.py`**

`src/evaluare/money.py`:
```python
"""Conversie si rotunjire monetara consistenta (Decimal)."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def to_money(value: float | int | str | Decimal) -> Decimal:
    """Converteste orice numeric la Decimal fara erori de virgula mobila."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_lei(value: Decimal) -> Decimal:
    """Rotunjeste la leu intreg (jumatate in sus)."""
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def pct(value: float | int | str | Decimal) -> Decimal:
    """Converteste un procent (ex. 35) la fractie (0.35)."""
    return to_money(value) / Decimal("100")
```

- [ ] **Step 4: Rulează testul ca să confirmi că trece**

Run: `python -m pytest tests/test_money.py -v`
Expected: PASS (3 teste).

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/money.py tests/test_money.py
git commit -m "feat: helper monetar Decimal (to_money, round_lei, pct)"
```

---

## Phase 2 — Modele de date

### Task 2: `models/property.py` — teren, construcție, elemente de cost

**Files:**
- Create: `src/evaluare/models/__init__.py`
- Create: `src/evaluare/models/property.py`
- Test: `tests/test_property_models.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_property_models.py`:
```python
from decimal import Decimal

from evaluare.models.property import (
    CostElement,
    DepreciationPoint,
    BuildingData,
    LandData,
)


def test_cost_element_computes_cost_nou_and_varsta():
    el = CostElement(
        element="Infrastructura",
        cod="FCV2",
        um="mp",
        cantitate=Decimal("128.90"),
        cost_unitar=Decimal("919"),
        an_pif=1945,
    )
    assert el.cost_nou() == Decimal("118459.10")
    assert el.varsta(an_referinta=2025) == 80


def test_building_data_holds_elements_and_areas():
    b = BuildingData(
        ac=None,
        au=Decimal("322.75"),
        acd=Decimal("351.46"),
        an_referinta=2025,
        elements=[
            CostElement(element="Structura", cod="X", um="mp",
                        cantitate=Decimal("100"), cost_unitar=Decimal("10"),
                        an_pif=2015),
        ],
        depreciation_points=[
            DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
            DepreciationPoint(varsta=35, depreciere=Decimal("0.36")),
        ],
    )
    assert b.acd == Decimal("351.46")
    assert b.functional_depreciation == Decimal("0")
    assert b.external_depreciation == Decimal("0")
    assert len(b.elements) == 1


def test_land_data_basic():
    land = LandData(suprafata=Decimal("500"), categorie="intravilan")
    assert land.suprafata == Decimal("500")
    assert land.categorie == "intravilan"
```

- [ ] **Step 2: Rulează testul ca să confirmi eșecul**

Run: `python -m pytest tests/test_property_models.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.models'`.

- [ ] **Step 3: Implementează modelele**

`src/evaluare/models/__init__.py`:
```python
```

`src/evaluare/models/property.py`:
```python
"""Modele pentru proprietatea subiect: teren si constructie."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CostElement(BaseModel):
    """Un element constructiv din metoda costurilor segregate (catalog IROVAL)."""

    element: str            # ex. "Infrastructura", "Structura", "Finisaje"
    cod: str                # cod catalog IROVAL, ex. "FCV2"
    um: str                 # unitate de masura, ex. "mp", "buc"
    cantitate: Decimal
    cost_unitar: Decimal    # lei/u.m. (fara TVA) din catalog
    an_pif: int             # anul punerii in functiune / modernizare al elementului

    def cost_nou(self) -> Decimal:
        """Cost de nou (fara TVA) = cantitate * cost unitar."""
        return self.cantitate * self.cost_unitar

    def varsta(self, an_referinta: int) -> int:
        """Varsta cronologica = an de referinta - an PIF."""
        return an_referinta - self.an_pif


class DepreciationPoint(BaseModel):
    """Un punct din tabelul de depreciere fizica (varsta -> fractie depreciere)."""

    varsta: int
    depreciere: Decimal     # fractie, ex. 0.31 pentru 31%


class BuildingData(BaseModel):
    """Datele fizice si de cost ale constructiei."""

    ac: Optional[Decimal] = None        # arie construita la sol
    au: Decimal                         # arie utila
    acd: Decimal                        # arie construita desfasurata
    an_referinta: int                   # anul datei de referinta a evaluarii
    elements: list[CostElement] = Field(default_factory=list)
    depreciation_points: list[DepreciationPoint] = Field(default_factory=list)
    functional_depreciation: Decimal = Decimal("0")   # C_nf (0 implicit; >0 la credit cu justificare)
    external_depreciation: Decimal = Decimal("0")      # C_ex
    structura: Optional[str] = None
    finisaje: Optional[str] = None
    clasa_energetica: Optional[str] = None


class LandData(BaseModel):
    """Datele terenului."""

    suprafata: Decimal                  # mp
    categorie: str = "intravilan"       # intravilan / extravilan
    deschidere: Optional[Decimal] = None
    utilitati: list[str] = Field(default_factory=list)
    restrictii_urbanism: Optional[str] = None
```

- [ ] **Step 4: Rulează testul ca să confirmi că trece**

Run: `python -m pytest tests/test_property_models.py -v`
Expected: PASS (3 teste).

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/models/__init__.py src/evaluare/models/property.py tests/test_property_models.py
git commit -m "feat: modele proprietate (teren, constructie, elemente cost segregat)"
```

---

### Task 3: `models/comparable.py` — comparabile și grilă de ajustări

**Files:**
- Create: `src/evaluare/models/comparable.py`
- Test: `tests/test_comparable_models.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_comparable_models.py`:
```python
from decimal import Decimal

from evaluare.models.comparable import (
    Adjustment,
    Comparable,
    LandComparable,
)


def test_adjustment_percentage_and_value():
    a = Adjustment(element="Localizare", tip="procentuala", valoare=Decimal("-0.05"),
                   justificare="pozitie inferioara")
    assert a.tip == "procentuala"
    assert a.valoare == Decimal("-0.05")


def test_comparable_with_adjustments():
    c = Comparable(
        sursa="manual",
        pret=Decimal("500000"),
        suprafata=Decimal("100"),
        tip_oferta="oferta",
        adjustments=[
            Adjustment(element="Conditii de vanzare", tip="procentuala",
                       valoare=Decimal("-0.03"), justificare="oferta activa"),
        ],
    )
    assert c.pret == Decimal("500000")
    assert len(c.adjustments) == 1


def test_land_comparable():
    lc = LandComparable(pret_mp=Decimal("80"), suprafata=Decimal("450"),
                        localizare="zona X")
    assert lc.pret_mp == Decimal("80")
```

- [ ] **Step 2: Rulează testul ca să confirmi eșecul**

Run: `python -m pytest tests/test_comparable_models.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează modelele**

`src/evaluare/models/comparable.py`:
```python
"""Modele pentru comparabile si grila de ajustari."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

AdjustmentType = Literal["procentuala", "valorica"]


class Adjustment(BaseModel):
    """O corectie aplicata unui comparabil pentru un element de comparatie.

    Pentru `procentuala`, `valoare` e o fractie (0.05 = +5%, -0.03 = -3%).
    Pentru `valorica`, `valoare` e o suma in lei (adunata la pretul curent).
    """

    element: str
    tip: AdjustmentType
    valoare: Decimal
    justificare: str = ""


class Comparable(BaseModel):
    """Un comparabil de piata (proprietate intreaga)."""

    sursa: str = "manual"               # "manual" sau URL
    pret: Decimal
    suprafata: Decimal                  # mp (numitorul pentru pretul unitar)
    tip_oferta: Literal["oferta", "tranzactie"] = "oferta"
    data_oferta: Optional[str] = None
    adjustments: list[Adjustment] = Field(default_factory=list)


class LandComparable(BaseModel):
    """Un comparabil de teren."""

    pret_mp: Decimal
    suprafata: Decimal
    localizare: Optional[str] = None
    data: Optional[str] = None
    adjustments: list[Adjustment] = Field(default_factory=list)
```

- [ ] **Step 4: Rulează testul ca să confirmi că trece**

Run: `python -m pytest tests/test_comparable_models.py -v`
Expected: PASS (3 teste).

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/models/comparable.py tests/test_comparable_models.py
git commit -m "feat: modele comparabile + ajustari (piata si teren)"
```

---

### Task 4: `models/results.py` — structurile de ieșire

**Files:**
- Create: `src/evaluare/models/results.py`
- Test: `tests/test_results_models.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_results_models.py`:
```python
from decimal import Decimal

from evaluare.models.results import CostResult, MarketResult, ReconciledResult


def test_cost_result_fields():
    r = CostResult(
        valoare_teren=Decimal("36000"),
        cib=Decimal("2012343"),
        vcp=Decimal("34.02"),
        depreciere_fizica=Decimal("0.3502"),
        cin=Decimal("1307558"),
        valoare_cost=Decimal("1343558"),
    )
    assert r.cin == Decimal("1307558")
    assert r.valoare_cost == Decimal("1343558")


def test_market_result_fields():
    r = MarketResult(
        preturi_unitare_corectate=[Decimal("4500"), Decimal("4600")],
        ajustari_brute=[Decimal("0.10"), Decimal("0.18")],
        index_selectat=0,
        valoare_piata=Decimal("450000"),
    )
    assert r.index_selectat == 0
    assert r.valoare_piata == Decimal("450000")


def test_reconciled_result_fields():
    r = ReconciledResult(
        valoare_finala=Decimal("450000"),
        metoda_selectata="piata",
        valoare_fara_tva=True,
    )
    assert r.metoda_selectata == "piata"
```

- [ ] **Step 2: Rulează testul ca să confirmi eșecul**

Run: `python -m pytest tests/test_results_models.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează modelele**

`src/evaluare/models/results.py`:
```python
"""Structuri de iesire pentru motoarele de calcul."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CostResult(BaseModel):
    """Rezultatul abordarii prin cost."""

    valoare_teren: Optional[Decimal] = None
    cib: Decimal                        # cost de inlocuire brut
    vcp: Decimal                        # varsta cronologica ponderata
    depreciere_fizica: Decimal          # fractie (Dfn)
    cin: Decimal                        # cost de inlocuire net
    valoare_cost: Optional[Decimal] = None   # teren + CIN (None daca terenul nu e evaluat)


class MarketResult(BaseModel):
    """Rezultatul abordarii prin piata."""

    preturi_unitare_corectate: list[Decimal] = Field(default_factory=list)
    ajustari_brute: list[Decimal] = Field(default_factory=list)
    ajustari_nete: list[Decimal] = Field(default_factory=list)
    index_selectat: int
    valoare_piata: Decimal


class ReconciledResult(BaseModel):
    """Rezultatul reconcilierii finale."""

    valoare_finala: Decimal
    metoda_selectata: Literal["piata", "cost", "ponderata"]
    valoare_fara_tva: bool = True
    nota: str = ""
```

- [ ] **Step 4: Rulează testul ca să confirmi că trece**

Run: `python -m pytest tests/test_results_models.py -v`
Expected: PASS (3 teste).

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/models/results.py tests/test_results_models.py
git commit -m "feat: modele rezultate (cost, piata, reconciliere)"
```

---

## Phase 3 — Cost Engine (piesa critică, regresie pe modelul GBF)

### Task 5: `engine/cost.py` — CIB, Vcp, depreciere, CIN

**Files:**
- Create: `src/evaluare/engine/__init__.py`
- Create: `src/evaluare/engine/cost.py`
- Test: `tests/test_cost.py`

- [ ] **Step 1: Scrie testul de regresie pe modelul GBF (eșuează)**

Acest test reproduce tabelul real din `model_impozitare_Enachescu Cristian Nicolae 2026.pdf`.
Valorile țintă: CIB ≈ 2.012.343 lei, Vcp ≈ 34,02 ani, Dfn ≈ 0,3502, CIN ≈ 1.307.558 lei.
Toleranța acoperă rotunjirea per-element din raportul original.

`tests/test_cost.py`:
```python
from decimal import Decimal

from evaluare.models.property import BuildingData, CostElement, DepreciationPoint
from evaluare.engine.cost import (
    compute_cib,
    compute_vcp,
    interpolate_depreciation,
    compute_cin,
    evaluate_cost,
)


def gbf_elements() -> list[CostElement]:
    """Elementele segregate exacte din modelul de referinta GBF."""
    data = [
        ("Infrastructura", "FCV2", "mp", "128.90", "919", 1945),
        ("Structura", "8ZPOROT30PFS", "mp", "128.90", "1398.9", 1945),
        ("Structura", "8ZIDCAR30ES", "mp", "160.06", "2056.0", 1945),
        ("Structura", "8ZPOROT30M", "mp", "62.50", "740.1", 1945),
        ("Finisaje", "SCAMOZ", "buc", "2.00", "8247.1", 1945),
        ("Finisaje", "FOBFS", "mp", "351.46", "2694.7", 2015),
        ("Instalatii electrice", "ELINGR", "mp", "351.46", "339", 2015),
        ("Instalatii sanitare", "LAVWC", "buc", "2.00", "5292.5", 2015),
        ("Instalatii sanitare", "CHINOX", "buc", "2.00", "4112", 2015),
        ("Instalatii de incalzire", "INCCONV", "mp", "351.46", "308", 2015),
        ("Invelitoare", "INVTL", "mp", "154.60", "831", 2015),
    ]
    return [
        CostElement(element=e, cod=c, um=u,
                    cantitate=Decimal(q), cost_unitar=Decimal(cu), an_pif=y)
        for e, c, u, q, cu, y in data
    ]


def test_compute_cib_matches_gbf():
    cib = compute_cib(gbf_elements())
    assert abs(cib - Decimal("2012343")) < Decimal("50")


def test_compute_vcp_matches_gbf():
    vcp = compute_vcp(gbf_elements(), an_referinta=2025)
    assert abs(vcp - Decimal("34.02")) < Decimal("0.05")


def test_interpolate_depreciation_matches_gbf():
    points = [
        DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
        DepreciationPoint(varsta=35, depreciere=Decimal("0.36")),
    ]
    dfn = interpolate_depreciation(Decimal("34.02"), points)
    assert abs(dfn - Decimal("0.3502")) < Decimal("0.0005")


def test_compute_cin_matches_gbf():
    cin = compute_cin(cib=Decimal("2012343"), dfn=Decimal("0.3502"),
                      c_nf=Decimal("0"), c_ex=Decimal("0"))
    assert abs(cin - Decimal("1307558")) < Decimal("100")


def test_evaluate_cost_end_to_end_matches_gbf():
    building = BuildingData(
        au=Decimal("322.75"),
        acd=Decimal("351.46"),
        an_referinta=2025,
        elements=gbf_elements(),
        depreciation_points=[
            DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
            DepreciationPoint(varsta=35, depreciere=Decimal("0.36")),
        ],
    )
    result = evaluate_cost(building, valoare_teren=None)
    assert abs(result.cib - Decimal("2012343")) < Decimal("50")
    assert abs(result.vcp - Decimal("34.02")) < Decimal("0.05")
    assert abs(result.cin - Decimal("1307558")) < Decimal("200")
    # Fara teren evaluat -> valoare_cost ramane None
    assert result.valoare_cost is None


def test_evaluate_cost_adds_land_value():
    building = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        elements=gbf_elements(),
        depreciation_points=[
            DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
            DepreciationPoint(varsta=35, depreciere=Decimal("0.36")),
        ],
    )
    result = evaluate_cost(building, valoare_teren=Decimal("100000"))
    assert result.valoare_cost == result.cin + Decimal("100000")
```

- [ ] **Step 2: Rulează testul ca să confirmi eșecul**

Run: `python -m pytest tests/test_cost.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.engine'`.

- [ ] **Step 3: Implementează `cost.py`**

`src/evaluare/engine/__init__.py`:
```python
```

`src/evaluare/engine/cost.py`:
```python
"""Abordarea prin cost: CIB segregat, Vcp, depreciere fizica, CIN."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from evaluare.models.property import BuildingData, CostElement, DepreciationPoint
from evaluare.models.results import CostResult


def compute_cib(elements: list[CostElement]) -> Decimal:
    """Cost de inlocuire brut = suma costurilor de nou ale elementelor."""
    return sum((el.cost_nou() for el in elements), Decimal("0"))


def compute_vcp(elements: list[CostElement], an_referinta: int) -> Decimal:
    """Varsta cronologica ponderata = sum(varsta_i * cost_i) / sum(cost_i)."""
    total_cost = compute_cib(elements)
    if total_cost == 0:
        return Decimal("0")
    weighted = sum(
        (Decimal(el.varsta(an_referinta)) * el.cost_nou() for el in elements),
        Decimal("0"),
    )
    return weighted / total_cost


def interpolate_depreciation(
    vcp: Decimal, points: list[DepreciationPoint]
) -> Decimal:
    """Depreciere fizica prin interpolare liniara intre punctele tabelului.

    Dfn = D1 + (D2 - D1) / (V2 - V1) * (Vcp - V1)
    Sub/peste limitele tabelului se foloseste primul/ultimul punct (clamp).
    """
    if not points:
        raise ValueError("Tabelul de depreciere este gol.")
    ordered = sorted(points, key=lambda p: p.varsta)
    if vcp <= ordered[0].varsta:
        return ordered[0].depreciere
    if vcp >= ordered[-1].varsta:
        return ordered[-1].depreciere
    for low, high in zip(ordered, ordered[1:]):
        if low.varsta <= vcp <= high.varsta:
            v1, d1 = Decimal(low.varsta), low.depreciere
            v2, d2 = Decimal(high.varsta), high.depreciere
            return d1 + (d2 - d1) / (v2 - v1) * (vcp - v1)
    return ordered[-1].depreciere  # nu ar trebui atins


def compute_cin(
    cib: Decimal, dfn: Decimal, c_nf: Decimal, c_ex: Decimal
) -> Decimal:
    """Cost de inlocuire net = CIB * (1-Dfn) * (1-C_nf) * (1-C_ex)."""
    one = Decimal("1")
    return cib * (one - dfn) * (one - c_nf) * (one - c_ex)


def evaluate_cost(
    building: BuildingData, valoare_teren: Optional[Decimal] = None
) -> CostResult:
    """Ruleaza abordarea prin cost completa pentru o constructie."""
    cib = compute_cib(building.elements)
    vcp = compute_vcp(building.elements, building.an_referinta)
    dfn = interpolate_depreciation(vcp, building.depreciation_points)
    cin = compute_cin(
        cib, dfn, building.functional_depreciation, building.external_depreciation
    )
    valoare_cost = None
    if valoare_teren is not None:
        valoare_cost = cin + valoare_teren
    return CostResult(
        valoare_teren=valoare_teren,
        cib=cib,
        vcp=vcp,
        depreciere_fizica=dfn,
        cin=cin,
        valoare_cost=valoare_cost,
    )
```

- [ ] **Step 4: Rulează testul ca să confirmi că trece**

Run: `python -m pytest tests/test_cost.py -v`
Expected: PASS (7 teste). Cost Engine reproduce modelul GBF în limitele de toleranță.

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/engine/__init__.py src/evaluare/engine/cost.py tests/test_cost.py
git commit -m "feat: Cost Engine (CIB segregat, Vcp, depreciere, CIN) cu regresie GBF"
```

---

## Phase 4 — Market Engine (grila de comparație)

### Task 6: `engine/market.py` — preț unitar, ajustări ierarhice, selecție

**Files:**
- Create: `src/evaluare/engine/market.py`
- Test: `tests/test_market.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_market.py`:
```python
from decimal import Decimal

from evaluare.models.comparable import Adjustment, Comparable
from evaluare.engine.market import (
    pret_unitar_brut,
    aplica_ajustari,
    ajustare_bruta,
    ajustare_neta,
    evaluate_market,
)


def test_pret_unitar_brut():
    c = Comparable(pret=Decimal("500000"), suprafata=Decimal("100"))
    assert pret_unitar_brut(c) == Decimal("5000")


def test_aplica_ajustari_procentuala_secvential():
    # 5000 * (1 - 0.03) = 4850 ; apoi 4850 * (1 + 0.10) = 5335
    c = Comparable(
        pret=Decimal("500000"), suprafata=Decimal("100"),
        adjustments=[
            Adjustment(element="Conditii de vanzare", tip="procentuala",
                       valoare=Decimal("-0.03")),
            Adjustment(element="Localizare", tip="procentuala",
                       valoare=Decimal("0.10")),
        ],
    )
    assert aplica_ajustari(c) == Decimal("5335.00")


def test_aplica_ajustari_valorica():
    # 5000 + 200 (valorica) = 5200
    c = Comparable(
        pret=Decimal("500000"), suprafata=Decimal("100"),
        adjustments=[
            Adjustment(element="Utilitati", tip="valorica", valoare=Decimal("200")),
        ],
    )
    assert aplica_ajustari(c) == Decimal("5200")


def test_ajustare_bruta_si_neta():
    c = Comparable(
        pret=Decimal("500000"), suprafata=Decimal("100"),
        adjustments=[
            Adjustment(element="A", tip="procentuala", valoare=Decimal("-0.03")),
            Adjustment(element="B", tip="procentuala", valoare=Decimal("0.10")),
        ],
    )
    assert ajustare_bruta(c) == Decimal("0.13")   # |−0.03| + |0.10|
    assert ajustare_neta(c) == Decimal("0.07")    # −0.03 + 0.10


def test_evaluate_market_selecteaza_ajustarea_bruta_minima():
    # comp0: ajustare bruta 0.05 ; comp1: ajustare bruta 0.20 -> selecteaza comp0
    comp0 = Comparable(
        pret=Decimal("480000"), suprafata=Decimal("100"),
        adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("0.05"))],
    )
    comp1 = Comparable(
        pret=Decimal("520000"), suprafata=Decimal("100"),
        adjustments=[Adjustment(element="A", tip="procentuala", valoare=Decimal("-0.20"))],
    )
    result = evaluate_market([comp0, comp1], suprafata_subiect=Decimal("110"))
    assert result.index_selectat == 0
    # pret corectat comp0 = 4800 * 1.05 = 5040 ; * 110 = 554400
    assert result.valoare_piata == Decimal("554400.00")
```

- [ ] **Step 2: Rulează testul ca să confirmi eșecul**

Run: `python -m pytest tests/test_market.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.engine.market'`.

- [ ] **Step 3: Implementează `market.py`**

`src/evaluare/engine/market.py`:
```python
"""Abordarea prin piata: grila de comparatie directa (SEV 105)."""
from __future__ import annotations

from decimal import Decimal

from evaluare.models.comparable import Comparable
from evaluare.models.results import MarketResult


def pret_unitar_brut(comp: Comparable) -> Decimal:
    """Pret unitar brut = pret / suprafata."""
    return comp.pret / comp.suprafata


def aplica_ajustari(comp: Comparable) -> Decimal:
    """Aplica ajustarile ierarhic, secvential, pe pretul curent.

    Procentuala: pret *= (1 + valoare). Valorica: pret += valoare.
    Ordinea de aplicare este ordinea din lista `adjustments`.
    """
    pret = pret_unitar_brut(comp)
    for adj in comp.adjustments:
        if adj.tip == "procentuala":
            pret = pret * (Decimal("1") + adj.valoare)
        else:  # valorica
            pret = pret + adj.valoare
    return pret


def ajustare_bruta(comp: Comparable) -> Decimal:
    """Suma absoluta a corectiilor procentuale (indicator de calitate)."""
    return sum(
        (abs(a.valoare) for a in comp.adjustments if a.tip == "procentuala"),
        Decimal("0"),
    )


def ajustare_neta(comp: Comparable) -> Decimal:
    """Suma algebrica a corectiilor procentuale."""
    return sum(
        (a.valoare for a in comp.adjustments if a.tip == "procentuala"),
        Decimal("0"),
    )


def evaluate_market(
    comparables: list[Comparable], suprafata_subiect: Decimal
) -> MarketResult:
    """Ruleaza grila de comparatie si selecteaza comparabilul cel mai credibil.

    Selectia: comparabilul cu ajustarea bruta minima (cel mai similar).
    Valoarea = pretul unitar corectat al acelui comparabil * suprafata subiect.
    """
    if not comparables:
        raise ValueError("Sunt necesare comparabile pentru abordarea prin piata.")
    preturi = [aplica_ajustari(c) for c in comparables]
    brute = [ajustare_bruta(c) for c in comparables]
    nete = [ajustare_neta(c) for c in comparables]
    index_selectat = min(range(len(comparables)), key=lambda i: brute[i])
    valoare = preturi[index_selectat] * suprafata_subiect
    return MarketResult(
        preturi_unitare_corectate=preturi,
        ajustari_brute=brute,
        ajustari_nete=nete,
        index_selectat=index_selectat,
        valoare_piata=valoare,
    )
```

- [ ] **Step 4: Rulează testul ca să confirmi că trece**

Run: `python -m pytest tests/test_market.py -v`
Expected: PASS (5 teste).

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/engine/market.py tests/test_market.py
git commit -m "feat: Market Engine (grila de comparatie, ajustari ierarhice, selectie)"
```

---

## Phase 5 — Reconciliere

### Task 7: `engine/reconciliation.py` — reconciliere piață vs cost

**Files:**
- Create: `src/evaluare/engine/reconciliation.py`
- Test: `tests/test_reconciliation.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_reconciliation.py`:
```python
from decimal import Decimal

import pytest

from evaluare.models.results import CostResult, MarketResult
from evaluare.engine.reconciliation import reconcile


def make_market(value: Decimal) -> MarketResult:
    return MarketResult(index_selectat=0, valoare_piata=value)


def make_cost(value: Decimal | None) -> CostResult:
    return CostResult(
        cib=Decimal("2000000"), vcp=Decimal("34"),
        depreciere_fizica=Decimal("0.35"), cin=Decimal("1300000"),
        valoare_cost=value,
    )


def test_reconcile_prefers_market_when_selected():
    r = reconcile(make_market(Decimal("450000")), make_cost(Decimal("460000")),
                  metoda="piata")
    assert r.metoda_selectata == "piata"
    assert r.valoare_finala == Decimal("450000")


def test_reconcile_uses_cost_when_selected():
    r = reconcile(make_market(Decimal("450000")), make_cost(Decimal("460000")),
                  metoda="cost")
    assert r.metoda_selectata == "cost"
    assert r.valoare_finala == Decimal("460000")


def test_reconcile_weighted_average():
    r = reconcile(make_market(Decimal("400000")), make_cost(Decimal("500000")),
                  metoda="ponderata", pondere_piata=Decimal("0.6"))
    # 400000*0.6 + 500000*0.4 = 440000
    assert r.metoda_selectata == "ponderata"
    assert r.valoare_finala == Decimal("440000.0")


def test_reconcile_falls_back_to_market_when_cost_unavailable():
    r = reconcile(make_market(Decimal("450000")), make_cost(None), metoda="cost")
    # cost indisponibil -> foloseste piata si noteaza
    assert r.metoda_selectata == "piata"
    assert r.valoare_finala == Decimal("450000")
    assert "indisponibil" in r.nota.lower()


def test_reconcile_raises_when_no_approach_available():
    with pytest.raises(ValueError):
        reconcile(None, make_cost(None), metoda="piata")
```

- [ ] **Step 2: Rulează testul ca să confirmi eșecul**

Run: `python -m pytest tests/test_reconciliation.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează `reconciliation.py`**

`src/evaluare/engine/reconciliation.py`:
```python
"""Reconcilierea valorilor din abordarea prin piata si prin cost."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from evaluare.models.results import CostResult, MarketResult, ReconciledResult

Metoda = Literal["piata", "cost", "ponderata"]


def reconcile(
    market: Optional[MarketResult],
    cost: Optional[CostResult],
    metoda: Metoda = "piata",
    pondere_piata: Decimal = Decimal("0.5"),
) -> ReconciledResult:
    """Selecteaza valoarea finala din cele doua abordari.

    - "piata": foloseste valoarea de piata
    - "cost": foloseste valoarea prin cost (teren + CIN)
    - "ponderata": medie ponderata (pondere_piata pentru piata)
    Daca abordarea ceruta nu e disponibila, cade pe cealalta si noteaza motivul.
    """
    market_value = market.valoare_piata if market is not None else None
    cost_value = cost.valoare_cost if cost is not None else None

    if market_value is None and cost_value is None:
        raise ValueError("Nicio abordare nu produce o valoare utilizabila.")

    if metoda == "piata":
        if market_value is not None:
            return ReconciledResult(valoare_finala=market_value, metoda_selectata="piata")
        return ReconciledResult(
            valoare_finala=cost_value, metoda_selectata="cost",
            nota="Abordarea prin piata indisponibila; s-a folosit abordarea prin cost.",
        )

    if metoda == "cost":
        if cost_value is not None:
            return ReconciledResult(valoare_finala=cost_value, metoda_selectata="cost")
        return ReconciledResult(
            valoare_finala=market_value, metoda_selectata="piata",
            nota="Abordarea prin cost indisponibila; s-a folosit abordarea prin piata.",
        )

    # ponderata
    if market_value is None or cost_value is None:
        disponibila = market_value if market_value is not None else cost_value
        metoda_disp = "piata" if market_value is not None else "cost"
        return ReconciledResult(
            valoare_finala=disponibila, metoda_selectata=metoda_disp,
            nota="O abordare indisponibila; ponderarea nu s-a putut aplica.",
        )
    pondere_cost = Decimal("1") - pondere_piata
    valoare = market_value * pondere_piata + cost_value * pondere_cost
    return ReconciledResult(valoare_finala=valoare, metoda_selectata="ponderata")
```

- [ ] **Step 4: Rulează testul ca să confirmi că trece**

Run: `python -m pytest tests/test_reconciliation.py -v`
Expected: PASS (5 teste).

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/engine/reconciliation.py tests/test_reconciliation.py
git commit -m "feat: reconciliere piata vs cost (selectie + ponderare + fallback)"
```

---

## Phase 6 — Validări

### Task 8: `engine/validation.py` — loops de control (blochează/alertează)

**Files:**
- Create: `src/evaluare/engine/validation.py`
- Test: `tests/test_validation.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_validation.py`:
```python
from decimal import Decimal

from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.comparable import Adjustment, Comparable
from evaluare.engine.validation import (
    Issue,
    valideaza_proprietate,
    valideaza_comparabile,
    valideaza_depreciere,
)


def _building(au="322.75", acd="351.46", c_nf="0", justif_nf="") -> BuildingData:
    return BuildingData(
        au=Decimal(au), acd=Decimal(acd), an_referinta=2025,
        functional_depreciation=Decimal(c_nf),
        elements=[CostElement(element="S", cod="X", um="mp",
                              cantitate=Decimal("10"), cost_unitar=Decimal("100"),
                              an_pif=2015)],
        depreciation_points=[DepreciationPoint(varsta=10, depreciere=Decimal("0.1"))],
        justificare_depreciere=justif_nf,
    )


def test_blocheaza_cand_au_mai_mare_decat_acd():
    land = LandData(suprafata=Decimal("500"))
    building = _building(au="400", acd="351.46")
    issues = valideaza_proprietate(land, building)
    assert any(i.nivel == "blocheaza" and "Au" in i.mesaj for i in issues)


def test_blocheaza_cand_suprafata_teren_zero():
    land = LandData(suprafata=Decimal("0"))
    building = _building()
    issues = valideaza_proprietate(land, building)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_proprietate_valida_fara_probleme():
    land = LandData(suprafata=Decimal("500"))
    building = _building()
    issues = valideaza_proprietate(land, building)
    assert all(i.nivel != "blocheaza" for i in issues)


def test_blocheaza_sub_3_comparabile():
    comps = [Comparable(pret=Decimal("1"), suprafata=Decimal("1"))]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_alerteaza_ajustare_bruta_peste_25_la_suta():
    comps = [
        Comparable(pret=Decimal("1"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("1"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("1"), suprafata=Decimal("1"),
                   adjustments=[Adjustment(element="A", tip="procentuala",
                                           valoare=Decimal("0.30"))]),
    ]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "alerteaza" and "ajustare" in i.mesaj.lower() for i in issues)


def test_alerteaza_outlier_dupa_mediana():
    comps = [
        Comparable(pret=Decimal("500"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("510"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("2000"), suprafata=Decimal("1")),  # outlier
    ]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "alerteaza" and "outlier" in i.mesaj.lower() for i in issues)


def test_blocheaza_depreciere_functionala_fara_justificare():
    building = _building(c_nf="0.10", justif_nf="")
    issues = valideaza_depreciere(building)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_depreciere_functionala_cu_justificare_ok():
    building = _building(c_nf="0.10", justif_nf="uzura interioara avansata")
    issues = valideaza_depreciere(building)
    assert all(i.nivel != "blocheaza" for i in issues)
```

- [ ] **Step 2: Rulează testul ca să confirmi eșecul**

Run: `python -m pytest tests/test_validation.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Extinde modelul cu câmpul de justificare, apoi implementează validatorul**

Testul folosește `BuildingData.justificare_depreciere`, care nu există încă. Adaugă-l întâi.

`src/evaluare/models/property.py` — adaugă în clasa `BuildingData`, imediat după linia
`external_depreciation: Decimal = Decimal("0")`:
```python
    justificare_depreciere: str = ""
```

Acum implementează validatorul:

`src/evaluare/engine/validation.py`:
```python
"""Loops de validare: blocheaza propagarea erorilor sau alerteaza evaluatorul."""
from __future__ import annotations

from decimal import Decimal
from statistics import median
from typing import Literal

from pydantic import BaseModel

from evaluare.models.property import BuildingData, LandData
from evaluare.models.comparable import Comparable
from evaluare.engine.market import pret_unitar_brut, ajustare_bruta

Nivel = Literal["blocheaza", "alerteaza"]

LIMITA_AJUSTARE_BRUTA = Decimal("0.25")
PRAG_OUTLIER = Decimal("0.50")   # deviatie relativa fata de mediana
MIN_COMPARABILE = 3


class Issue(BaseModel):
    """O problema de validare."""

    nivel: Nivel
    mesaj: str


def valideaza_proprietate(land: LandData, building: BuildingData) -> list[Issue]:
    """Valideaza datele fizice/cadastrale ale proprietatii."""
    issues: list[Issue] = []
    if land.suprafata <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Suprafata terenului trebuie sa fie > 0."))
    if building.au <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Aria utila (Au) trebuie sa fie > 0."))
    if building.acd <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Aria construita desfasurata (Acd) trebuie sa fie > 0."))
    if building.au > building.acd:
        issues.append(Issue(nivel="blocheaza", mesaj="Au nu poate depasi Acd."))
    return issues


def valideaza_comparabile(comparables: list[Comparable]) -> list[Issue]:
    """Valideaza numarul, outlierii si limitele de ajustare ale comparabilelor."""
    issues: list[Issue] = []
    if len(comparables) < MIN_COMPARABILE:
        issues.append(Issue(
            nivel="blocheaza",
            mesaj=f"Sunt necesare minimum {MIN_COMPARABILE} comparabile (gasite: {len(comparables)}).",
        ))
        return issues

    preturi = [pret_unitar_brut(c) for c in comparables]
    med = Decimal(str(median([float(p) for p in preturi])))
    if med > 0:
        for i, p in enumerate(preturi):
            deviatie = abs(p - med) / med
            if deviatie > PRAG_OUTLIER:
                issues.append(Issue(
                    nivel="alerteaza",
                    mesaj=f"Comparabilul {i} este outlier (deviatie {deviatie:.0%} fata de mediana).",
                ))

    for i, c in enumerate(comparables):
        if ajustare_bruta(c) > LIMITA_AJUSTARE_BRUTA:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=f"Comparabilul {i}: ajustare bruta {ajustare_bruta(c):.0%} depaseste limita de {LIMITA_AJUSTARE_BRUTA:.0%}.",
            ))
    return issues


def valideaza_depreciere(building: BuildingData) -> list[Issue]:
    """Cere justificare pentru deprecierea functionala/externa nenula."""
    issues: list[Issue] = []
    are_depreciere = (
        building.functional_depreciation > 0 or building.external_depreciation > 0
    )
    if are_depreciere and not building.justificare_depreciere.strip():
        issues.append(Issue(
            nivel="blocheaza",
            mesaj="Deprecierea functionala/externa nenula necesita justificare scrisa.",
        ))
    return issues
```

- [ ] **Step 4: Rulează testul ca să confirmi că trece**

Run: `python -m pytest tests/test_validation.py -v`
Expected: PASS (8 teste).

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/engine/validation.py src/evaluare/models/property.py tests/test_validation.py
git commit -m "feat: loops de validare (proprietate, comparabile, depreciere)"
```

---

## Phase 7 — Verificare finală

### Task 9: Rulează întreaga suită + verifică acoperirea

**Files:** niciunul (verificare)

- [ ] **Step 1: Rulează toate testele**

Run: `python -m pytest -v`
Expected: PASS pentru toate suitele (money, modele, cost, market, reconciliere, validare).

- [ ] **Step 2: Confirmă testul de regresie GBF**

Run: `python -m pytest tests/test_cost.py::test_evaluate_cost_end_to_end_matches_gbf -v`
Expected: PASS — Cost Engine reproduce CIN ≈ 1.307.558 lei din modelul real.

- [ ] **Step 3: Commit final (dacă a rămas ceva)**

```bash
git add -A
git commit -m "test: verificare completa nucleu de calcul" || echo "nimic de comis"
```

---

## Recapitulare acoperire spec (Planul 1)

| Cerință spec | Task |
|---|---|
| Modele de date (teren, construcție, elemente cost) | Task 2 |
| Comparabile + grilă ajustări | Task 3 |
| Structuri de ieșire | Task 4 |
| CIB segregat + Vcp + depreciere + CIN (regresie GBF) | Task 5 |
| Grila de comparație + ajustări ierarhice + indicatori + selecție | Task 6 |
| Reconciliere piață vs cost (cu fallback) | Task 7 |
| Validări (proprietate, comparabile, depreciere) | Task 8 |
| Precizie monetară Decimal | Task 1 |

**Rămâne pentru Planurile 2 și 3:** anonimizare + AI narativ + generator .docx (Plan 2);
FastAPI/HTMX + importatori (manual + URL) + SQLite + PyInstaller (Plan 3).
