# Faza 0 — Fundația platformei (profil + abordări + venit + secțiuni) — Plan de implementare

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended)
> or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Introduce cadrul configurabil (ProfilEvaluare + abordări interschimbabile + abordarea prin venit
prin capitalizare directă + registru de secțiuni de raport), **strict aditiv**, fără a modifica fluxul
existent — cele 281 de teste rămân verzi.

**Architecture:** Module noi pure (profil, abordari, venit, sectiuni) + o funcție nouă de reconciliere pe
profil. Motoarele existente (cost/market/land) sunt împachetate prin adaptoare care produc un
`RezultatAbordare` comun; nimic din codul validat nu se rescrie. Compatibilitate înapoi garantată prin
teste de echivalență.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, Decimal. Fără dependențe noi.

**Referință spec:** `docs/superpowers/specs/2026-06-04-platforma-evaluare-imobiliara-master-design.md` (§5).

---

## File Structure
- Create: `src/evaluare/profil.py` — `ProfilEvaluare` + enumuri + profiluri predefinite.
- Create: `src/evaluare/engine/abordari.py` — `RezultatAbordare` + adaptoare `abordare_cost`, `abordare_comparatie`.
- Create: `src/evaluare/engine/venit.py` — `DateVenit`, `RezultatVenit`, `evalueaza_venit`, `abordare_venit`.
- Modify: `src/evaluare/models/results.py` — extinde `ReconciledResult.metoda_selectata` cu `"venit"`.
- Modify: `src/evaluare/engine/reconciliation.py` — adaugă `reconcile_profil(...)` (NU schimbă `reconcile`).
- Create: `src/evaluare/report/sectiuni.py` — registru de secțiuni + `sectiuni_pentru_profil`.
- Modify: `src/evaluare/models/report_context.py` — adaugă câmpul `profil` (default profil casă+teren).
- Tests: `tests/test_profil.py`, `tests/test_abordari.py`, `tests/test_venit.py`,
  `tests/test_reconcile_profil.py`, `tests/test_sectiuni.py`, `tests/test_faza0_echivalenta.py`.

---

## Task 1: `ProfilEvaluare` — modelul de configurare

**Files:**
- Create: `src/evaluare/profil.py`
- Test: `tests/test_profil.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_profil.py
from decimal import Decimal
from evaluare.profil import ProfilEvaluare, CASA_TEREN_GARANTARE


def test_profil_default():
    p = ProfilEvaluare()
    assert p.tip_activ == "casa"
    assert p.scop == "garantare_credit"
    assert p.tip_valoare == "piata"
    assert p.abordari_aplicabile == ["cost", "comparatie"]
    assert p.ghid == "GEV_520"


def test_profil_predefinit_casa_teren():
    assert CASA_TEREN_GARANTARE.tip_activ == "casa"
    assert CASA_TEREN_GARANTARE.ghid == "GEV_520"
    assert "venit" not in CASA_TEREN_GARANTARE.abordari_aplicabile


def test_profil_comercial_cu_venit():
    p = ProfilEvaluare(tip_activ="comercial", ghid="GEV_630",
                       abordari_aplicabile=["venit", "comparatie"],
                       ponderi={"venit": Decimal("0.7"), "comparatie": Decimal("0.3")})
    assert p.tip_activ == "comercial"
    assert p.abordari_aplicabile[0] == "venit"
    assert p.ponderi["venit"] == Decimal("0.7")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_profil.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'evaluare.profil'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/evaluare/profil.py
"""ProfilEvaluare — sursa de adevăr a unei evaluări (tip activ, scop, tip valoare, abordări, ghid)."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

TipActiv = Literal["casa", "teren", "apartament", "comercial", "industrial", "agricol", "special"]
Scop = Literal["garantare_credit", "raportare_financiara", "asigurare", "impozitare",
               "vanzare", "litigii", "expropriere", "aport"]
TipValoare = Literal["piata", "investitie", "justa", "lichidare", "asigurare", "chirie"]
Abordare = Literal["cost", "comparatie", "venit"]
Ghid = Literal["GEV_520", "GEV_630", "GEV_500", "none"]


class ProfilEvaluare(BaseModel):
    """Configurarea unei evaluări: ce tip, în ce scop, ce valoare, ce abordări, ce ghid."""

    tip_activ: TipActiv = "casa"
    scop: Scop = "garantare_credit"
    tip_valoare: TipValoare = "piata"
    abordari_aplicabile: list[Abordare] = Field(default_factory=lambda: ["cost", "comparatie"])
    ponderi: dict[str, Decimal] = Field(default_factory=dict)
    ghid: Ghid = "GEV_520"


# Profil predefinit = comportamentul actual al aplicației.
CASA_TEREN_GARANTARE = ProfilEvaluare(
    tip_activ="casa", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["cost", "comparatie"], ghid="GEV_520",
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_profil.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/profil.py tests/test_profil.py
git commit -m "Faza 0: ProfilEvaluare + profil predefinit casa+teren"
```

---

## Task 2: Abordări interschimbabile — adaptoare peste motoarele existente

**Files:**
- Create: `src/evaluare/engine/abordari.py`
- Test: `tests/test_abordari.py`

Motoarele existente (`evaluate_cost`, `evaluate_market`) NU se modifică; adaptoarele doar le împachetează
într-un `RezultatAbordare` comun, ca reconcilierea să poată lucra uniform.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_abordari.py
from decimal import Decimal

from evaluare.engine.abordari import RezultatAbordare, abordare_cost, abordare_comparatie
from evaluare.models.property import BuildingData
from evaluare.models.comparable import Comparable


def _building():
    return BuildingData(
        au=Decimal("100"), acd=Decimal("120"), an_referinta=2025,
        elements=[{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                   "cost_unitar": "2000", "an_pif": 2015}],
        depreciation_points=[{"varsta": 5, "depreciere": "0.05"},
                             {"varsta": 15, "depreciere": "0.15"}],
    )


def test_abordare_cost_produce_rezultat():
    r = abordare_cost(_building(), valoare_teren=Decimal("100000"))
    assert isinstance(r, RezultatAbordare)
    assert r.abordare == "cost"
    assert r.valoare is not None and r.valoare > 0
    assert "cin" in r.detalii


def test_abordare_comparatie_produce_rezultat():
    comps = [Comparable(pret=Decimal("250000"), suprafata=Decimal("120")),
             Comparable(pret=Decimal("260000"), suprafata=Decimal("125")),
             Comparable(pret=Decimal("240000"), suprafata=Decimal("118"))]
    r = abordare_comparatie(comps, suprafata_subiect=Decimal("120"))
    assert r.abordare == "comparatie"
    assert r.valoare is not None and r.valoare > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_abordari.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'evaluare.engine.abordari'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/evaluare/engine/abordari.py
"""Abordări de evaluare cu ieșire comună (RezultatAbordare), peste motoarele existente."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

from evaluare.engine.cost import evaluate_cost
from evaluare.engine.market import evaluate_market
from evaluare.models.comparable import Comparable
from evaluare.models.property import BuildingData

NumeAbordare = Literal["cost", "comparatie", "venit"]


class RezultatAbordare(BaseModel):
    """Ieșirea comună a oricărei abordări — folosită la reconciliere pe profil."""

    abordare: NumeAbordare
    valoare: Optional[Decimal] = None
    detalii: dict = Field(default_factory=dict)


def abordare_cost(building: BuildingData, valoare_teren: Optional[Decimal]) -> RezultatAbordare:
    res = evaluate_cost(building, valoare_teren=valoare_teren)
    return RezultatAbordare(
        abordare="cost", valoare=res.valoare_cost,
        detalii={"cin": str(res.cin), "cib": str(res.cib),
                 "depreciere_fizica": str(res.depreciere_fizica)},
    )


def abordare_comparatie(comparables: list[Comparable], suprafata_subiect: Decimal) -> RezultatAbordare:
    res = evaluate_market(comparables, suprafata_subiect=suprafata_subiect)
    return RezultatAbordare(
        abordare="comparatie", valoare=res.valoare_piata,
        detalii={"index_selectat": res.index_selectat},
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_abordari.py -q`
Expected: PASS (2 passed). Dacă semnătura `BuildingData`/`Comparable` diferă, copiază forma exactă din
`tests/test_web_api.py` (payload-ul de acolo e valid) și ajustează construcția obiectelor.

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/engine/abordari.py tests/test_abordari.py
git commit -m "Faza 0: RezultatAbordare + adaptoare cost/comparatie peste motoarele existente"
```

---

## Task 3: Abordarea prin venit — capitalizare directă

**Files:**
- Create: `src/evaluare/engine/venit.py`
- Test: `tests/test_venit.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_venit.py
from decimal import Decimal

import pytest

from evaluare.engine.venit import DateVenit, RezultatVenit, evalueaza_venit, abordare_venit


def test_capitalizare_directa_simpla():
    # VBP 100.000; neocupare 5%; cheltuieli 20.000; rata 8% -> NOI=75.000; valoare=937.500
    d = DateVenit(venit_brut_potential=Decimal("100000"), grad_neocupare=Decimal("0.05"),
                  cheltuieli_exploatare=Decimal("20000"), rata_capitalizare=Decimal("0.08"))
    r = evalueaza_venit(d)
    assert isinstance(r, RezultatVenit)
    assert r.noi == Decimal("75000.00")
    assert r.valoare == Decimal("937500.00")


def test_fara_neocupare_fara_cheltuieli():
    d = DateVenit(venit_brut_potential=Decimal("80000"), rata_capitalizare=Decimal("0.10"))
    r = evalueaza_venit(d)
    assert r.noi == Decimal("80000.00")
    assert r.valoare == Decimal("800000.00")


def test_rata_capitalizare_invalida():
    with pytest.raises(ValueError):
        evalueaza_venit(DateVenit(venit_brut_potential=Decimal("10000"),
                                  rata_capitalizare=Decimal("0")))


def test_abordare_venit_adaptor():
    d = DateVenit(venit_brut_potential=Decimal("80000"), rata_capitalizare=Decimal("0.10"))
    r = abordare_venit(d)
    assert r.abordare == "venit"
    assert r.valoare == Decimal("800000.00")
    assert "noi" in r.detalii
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_venit.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'evaluare.engine.venit'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/evaluare/engine/venit.py
"""Abordarea prin venit — capitalizare directă (NOI ÷ rată de capitalizare)."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel

from evaluare.engine.abordari import RezultatAbordare

_BANI = Decimal("0.01")


class DateVenit(BaseModel):
    """Intrările pentru capitalizarea directă (sume anuale; procente ca fracție [0,1])."""

    venit_brut_potential: Decimal
    grad_neocupare: Decimal = Decimal("0")
    cheltuieli_exploatare: Decimal = Decimal("0")
    rata_capitalizare: Decimal


class RezultatVenit(BaseModel):
    noi: Decimal
    valoare: Decimal


def evalueaza_venit(d: DateVenit) -> RezultatVenit:
    """Valoare = (VBP − pierderi neocupare − cheltuieli) ÷ rată de capitalizare."""
    if d.rata_capitalizare <= 0:
        raise ValueError("Rata de capitalizare trebuie să fie > 0.")
    pierdere = d.venit_brut_potential * d.grad_neocupare
    venit_efectiv = d.venit_brut_potential - pierdere
    noi = (venit_efectiv - d.cheltuieli_exploatare).quantize(_BANI, rounding=ROUND_HALF_UP)
    valoare = (noi / d.rata_capitalizare).quantize(_BANI, rounding=ROUND_HALF_UP)
    return RezultatVenit(noi=noi, valoare=valoare)


def abordare_venit(d: DateVenit) -> RezultatAbordare:
    r = evalueaza_venit(d)
    return RezultatAbordare(abordare="venit", valoare=r.valoare, detalii={"noi": str(r.noi)})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_venit.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/engine/venit.py tests/test_venit.py
git commit -m "Faza 0: abordarea prin venit (capitalizare directa) + adaptor"
```

---

## Task 4: Reconciliere pe profil (aditivă, nu schimbă `reconcile`)

**Files:**
- Modify: `src/evaluare/models/results.py` (extinde `metoda_selectata`)
- Modify: `src/evaluare/engine/reconciliation.py` (adaugă `reconcile_profil`)
- Test: `tests/test_reconcile_profil.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_reconcile_profil.py
from decimal import Decimal

from evaluare.engine.abordari import RezultatAbordare
from evaluare.engine.reconciliation import reconcile_profil


def _r(abordare, val):
    return RezultatAbordare(abordare=abordare, valoare=Decimal(val) if val is not None else None)


def test_primara_disponibila():
    rez = [_r("cost", "300000"), _r("comparatie", "320000")]
    out = reconcile_profil(rez, primara="comparatie")
    assert out.valoare_finala == Decimal("320000")
    assert out.metoda_selectata == "piata"        # comparatie = piata


def test_venit_primar():
    rez = [_r("venit", "800000"), _r("comparatie", "780000")]
    out = reconcile_profil(rez, primara="venit")
    assert out.valoare_finala == Decimal("800000")
    assert out.metoda_selectata == "venit"


def test_fallback_cand_primara_lipseste():
    rez = [_r("comparatie", None), _r("cost", "300000")]
    out = reconcile_profil(rez, primara="comparatie")
    assert out.valoare_finala == Decimal("300000")
    assert out.metoda_selectata == "cost"
    assert out.nota != ""


def test_ponderata():
    rez = [_r("comparatie", "320000"), _r("cost", "300000")]
    out = reconcile_profil(rez, primara="comparatie",
                           ponderi={"comparatie": Decimal("0.5"), "cost": Decimal("0.5")})
    assert out.valoare_finala == Decimal("310000")
    assert out.metoda_selectata == "ponderata"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_reconcile_profil.py -q`
Expected: FAIL — `ImportError: cannot import name 'reconcile_profil'`

- [ ] **Step 3a: Extinde `metoda_selectata` în `models/results.py`**

În `src/evaluare/models/results.py`, schimbă linia din `ReconciledResult`:

```python
    metoda_selectata: Literal["piata", "cost", "ponderata"]
```

în:

```python
    metoda_selectata: Literal["piata", "cost", "ponderata", "venit"]
```

(Adăugarea unei valori la `Literal` e compatibilă înapoi — valorile existente rămân valide.)

- [ ] **Step 3b: Adaugă `reconcile_profil` în `engine/reconciliation.py`**

Adaugă la finalul fișierului (nu modifica `reconcile`):

```python
from typing import Dict  # adaugă la importurile existente daca lipseste

# Maparea numelui de abordare la eticheta de metodă din raport.
_METODA = {"cost": "cost", "comparatie": "piata", "venit": "venit"}


def reconcile_profil(rezultate, primara, ponderi=None):
    """Reconciliază o listă de RezultatAbordare după profil.

    - `primara`: numele abordării preferate (cost/comparatie/venit).
    - `ponderi`: dacă e dat (dict nume->Decimal), face medie ponderată pe abordările cu valoare.
    Dacă primara lipsește, cade pe prima abordare disponibilă și notează motivul.
    """
    valori = {r.abordare: r.valoare for r in rezultate if r.valoare is not None}
    if not valori:
        raise ValueError("Nicio abordare nu produce o valoare utilizabilă.")

    if ponderi:
        total_pondere = sum(ponderi[a] for a in ponderi if a in valori)
        if total_pondere > 0:
            valoare = sum(valori[a] * ponderi[a] for a in ponderi if a in valori) / total_pondere
            return ReconciledResult(valoare_finala=valoare, metoda_selectata="ponderata")

    if primara in valori:
        return ReconciledResult(valoare_finala=valori[primara],
                                metoda_selectata=_METODA[primara])
    # fallback
    abordare_disp = next(iter(valori))
    return ReconciledResult(
        valoare_finala=valori[abordare_disp], metoda_selectata=_METODA[abordare_disp],
        nota=f"Abordarea „{primara}" indisponibilă; s-a folosit „{abordare_disp}".",
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_reconcile_profil.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/models/results.py src/evaluare/engine/reconciliation.py tests/test_reconcile_profil.py
git commit -m "Faza 0: reconcile_profil (aditiv) + metoda_selectata extinsa cu 'venit'"
```

---

## Task 5: Registru de secțiuni de raport, pe profil/ghid

**Files:**
- Create: `src/evaluare/report/sectiuni.py`
- Test: `tests/test_sectiuni.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sectiuni.py
from evaluare.profil import CASA_TEREN_GARANTARE, ProfilEvaluare
from evaluare.report.sectiuni import sectiuni_pentru_profil, ID_SECTIUNI


def test_casa_teren_garantare_are_gev520_fara_venit():
    ids = sectiuni_pentru_profil(CASA_TEREN_GARANTARE)
    assert "coperta" in ids
    assert "gev_520" in ids
    assert "abordare_venit" not in ids


def test_comercial_gev630_are_venit_fara_gev520():
    p = ProfilEvaluare(tip_activ="comercial", ghid="GEV_630",
                       abordari_aplicabile=["venit", "comparatie"])
    ids = sectiuni_pentru_profil(p)
    assert "abordare_venit" in ids
    assert "gev_520" not in ids


def test_toate_id_urile_sunt_unice():
    assert len(ID_SECTIUNI) == len(set(ID_SECTIUNI))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_sectiuni.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'evaluare.report.sectiuni'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/evaluare/report/sectiuni.py
"""Registru de secțiuni de raport. Profilul + ghidul decid ce secțiuni apar."""
from __future__ import annotations

from evaluare.profil import ProfilEvaluare

# Fiecare secțiune: (id, ghiduri în care apare). "*" = în toate ghidurile.
_REGISTRU = [
    ("coperta", "*"),
    ("scrisoare_transmitere", "*"),
    ("declaratie_conformitate", "*"),
    ("termeni_referinta", "*"),
    ("descriere_proprietate", "*"),
    ("analiza_piata", "*"),
    ("abordare_cost", "*"),
    ("abordare_comparatie", "*"),
    ("abordare_venit", ("GEV_630",)),
    ("reconciliere", "*"),
    ("alocare_valoare", ("GEV_520", "GEV_630")),
    ("gev_520", ("GEV_520",)),
    ("raportare_financiara", ("GEV_500",)),
    ("anexe", "*"),
]

ID_SECTIUNI = [s[0] for s in _REGISTRU]


def sectiuni_pentru_profil(profil: ProfilEvaluare) -> list[str]:
    """Returnează id-urile de secțiuni aplicabile profilului, în ordine."""
    out = []
    for sid, ghiduri in _REGISTRU:
        if ghiduri == "*" or profil.ghid in ghiduri:
            out.append(sid)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_sectiuni.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/report/sectiuni.py tests/test_sectiuni.py
git commit -m "Faza 0: registru de sectiuni de raport pe profil/ghid"
```

---

## Task 6: Profil în `ReportContext` + echivalența casă+teren

**Files:**
- Modify: `src/evaluare/models/report_context.py` (adaugă câmpul `profil`)
- Test: `tests/test_faza0_echivalenta.py`

Scop: dovedim că reconcilierea pe profil reproduce **exact** valoarea reconcilierii actuale pentru cazul
casă+teren — adică „celula" existentă se remapează corect în cadru.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_faza0_echivalenta.py
from decimal import Decimal

from evaluare.engine.abordari import abordare_cost, abordare_comparatie
from evaluare.engine.reconciliation import reconcile, reconcile_profil
from evaluare.models.comparable import Comparable
from evaluare.models.property import BuildingData
from evaluare.engine.cost import evaluate_cost
from evaluare.engine.market import evaluate_market
from evaluare.models.report_context import ReportContext
from evaluare.profil import CASA_TEREN_GARANTARE


def _building():
    return BuildingData(
        au=Decimal("100"), acd=Decimal("120"), an_referinta=2025,
        elements=[{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                   "cost_unitar": "2000", "an_pif": 2015}],
        depreciation_points=[{"varsta": 5, "depreciere": "0.05"},
                             {"varsta": 15, "depreciere": "0.15"}],
    )


def test_reconcile_profil_echivalent_cu_reconcile_pe_cost():
    b = _building()
    cost = evaluate_cost(b, valoare_teren=Decimal("100000"))
    vechi = reconcile(market=None, cost=cost, metoda="cost")
    nou = reconcile_profil([abordare_cost(b, valoare_teren=Decimal("100000"))], primara="cost")
    assert nou.valoare_finala == vechi.valoare_finala
    assert nou.metoda_selectata == vechi.metoda_selectata == "cost"


def test_reconcile_profil_echivalent_pe_piata():
    comps = [Comparable(pret=Decimal("250000"), suprafata=Decimal("120")),
             Comparable(pret=Decimal("260000"), suprafata=Decimal("125")),
             Comparable(pret=Decimal("240000"), suprafata=Decimal("118"))]
    market = evaluate_market(comps, suprafata_subiect=Decimal("120"))
    vechi = reconcile(market=market, cost=None, metoda="piata")
    nou = reconcile_profil([abordare_comparatie(comps, suprafata_subiect=Decimal("120"))],
                           primara="comparatie")
    assert nou.valoare_finala == vechi.valoare_finala
    assert nou.metoda_selectata == "piata"


def test_report_context_are_profil_default():
    # ReportContext acceptă un profil; default = casă+teren/garantare
    ctx = ReportContext.model_construct()
    assert hasattr(ctx, "profil") or "profil" in ReportContext.model_fields
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_faza0_echivalenta.py -q`
Expected: FAIL — `test_report_context_are_profil_default` eșuează (câmpul `profil` nu există încă).
Primele două teste ar trebui să treacă deja (validează echivalența).

- [ ] **Step 3: Adaugă câmpul `profil` în `ReportContext`**

În `src/evaluare/models/report_context.py`: adaugă importul și câmpul (cu default = profilul casă+teren,
ca să nu schimbe nimic existent):

```python
from evaluare.profil import ProfilEvaluare, CASA_TEREN_GARANTARE  # adaugă la importuri

# în clasa ReportContext, printre câmpuri:
    profil: ProfilEvaluare = CASA_TEREN_GARANTARE
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_faza0_echivalenta.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/evaluare/models/report_context.py tests/test_faza0_echivalenta.py
git commit -m "Faza 0: profil in ReportContext (default casa+teren) + teste de echivalenta"
```

---

## Task 7: Verificare finală + rebuild exe

**Files:** niciunul nou.

- [ ] **Step 1: Rulează suita completă**

Run: `python -m pytest -q`
Expected: PASS — **toate** testele (cele 281 existente + ~19 noi). Dacă vreun test existent pică,
înseamnă că o modificare NU a fost aditivă — investighează (cel mai probabil `metoda_selectata` sau un
import circular) înainte de a continua.

- [ ] **Step 2: Lint**

Run: `python -m pyflakes src/`
Expected: fără ieșire (cod curat).

- [ ] **Step 3: Rebuild exe**

```bash
# oprește orice instanță care ține portul 8000
# (PowerShell: Get-Process evaluare-anevar -ErrorAction SilentlyContinue | Stop-Process -Force)
python -m PyInstaller --clean --noconfirm evaluare-anevar.spec
```
Expected: „Build complete!". (Modulele noi sunt importate normal; nu necesită intrări noi în `.spec`.)

- [ ] **Step 4: Smoke — pornește exe + verifică o pagină**

Pornește `dist/evaluare-anevar.exe`, apoi `GET http://127.0.0.1:8000/wizard` → 200. (Faza 0 e backend; UI
neschimbat.)

- [ ] **Step 5: Commit final**

```bash
git add -A
git commit -m "Faza 0: verificare finala — suita verde + exe reimpachetat"
```

---

## Self-review (acoperire spec §5)
- §5.1 `profil.py` → Task 1 ✅ · `engine/abordari.py` → Task 2 ✅ · `engine/venit.py` → Task 3 ✅ ·
  `reconciliation` extins → Task 4 ✅ · `report/sectiuni.py` → Task 5 ✅ · `report_context` profil → Task 6 ✅.
- §5.2 flux de date: abordări → RezultatAbordare → reconcile_profil → valoare; secțiuni pe profil → Task 4+5 ✅.
- §5.3 erori: rată ≤ 0 (Task 3), nicio abordare (Task 4) ✅.
- §5.4 testare: regresie (Task 7) + module noi (Task 1-6) ✅.
- §5.5 fără DCF/grilă chirii/UI nou — respectat (niciun task nu le include).
