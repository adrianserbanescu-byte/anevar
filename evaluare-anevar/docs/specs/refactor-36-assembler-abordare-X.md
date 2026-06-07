# Spec refactor #36 — `assembler.py` → `abordare_X` (single source of truth)

> ⚠ **CLARIFICARE BUCKET (2026-06-07, sesiune A):** acest refactor atinge **METODOLOGIA DE EVALUARE**
> (cum se calculează valoarea finală pe abordările cost/comparație/venit). Este **bucket-B** (cere
> evaluator senior înainte de implementare), NU autonom. Spec-ul rămâne ca **propunere documentată**;
> implementarea trece prin validare evaluator + Adi.
>
> Decizia Adi #36 (2026-06-07): **opțiunea (a)** — refactor `assembler.py:130-158` să folosească
> `abordare_cost/comparatie/venit` din `engine/abordari.py` + `engine/venit.py` în loc de
> `evaluate_cost/evaluate_market/evalueaza_venit`. Single source of truth aliniat SEV 2025.
>
> Spec generat în sesiunea C (worktree `anevar-c`). **NU implementează — doar îndrumă.**
> Implementare: sesiune B / loop autonom **DOAR DUPĂ** evaluator senior confirmă că refactor-ul
> nu schimbă rezultatele numerice (toate cele 87+ teste pe `abordare_X` și `assembler.py` trebuie
> să rămână identice — refactor pur, zero semantic change).

---

## 1. Starea curentă (de ce e dual)

`construieste_context()` în `assembler.py:114-192` folosește direct motoarele interne și împachetează
manual rezultatele în `RezultatAbordare`:

```python
# assembler.py:130-158 (curent)
cost_result = evaluate_cost(inp.building, valoare_teren=valoare_teren)
market_result = evaluate_market(inp.comparables, suprafata_subiect=inp.building.acd)
venit_result = evalueaza_venit(inp.date_venit)

rezultate.append(RezultatAbordare(abordare="cost", valoare=cost_result.valoare_cost))
rezultate.append(RezultatAbordare(abordare="comparatie", valoare=market_result.valoare_piata))
rezultate.append(RezultatAbordare(abordare="venit", valoare=venit_pt_reconciliere))
```

Concomitent, `engine/abordari.py` + `engine/venit.py` definesc 3 funcții **paralele** care fac
exact același lucru, plus că **populează `detalii`**:

```python
# engine/abordari.py:24-30
def abordare_cost(building, valoare_teren) -> RezultatAbordare:
    res = evaluate_cost(building, valoare_teren=valoare_teren)
    return RezultatAbordare(
        abordare="cost", valoare=res.valoare_cost,
        detalii={"cin": str(res.cin), "cib": str(res.cib),
                 "depreciere_fizica": str(res.depreciere_fizica)},
    )

# engine/abordari.py:33-38
def abordare_comparatie(comparables, suprafata_subiect) -> RezultatAbordare:
    res = evaluate_market(comparables, suprafata_subiect=suprafata_subiect)
    return RezultatAbordare(
        abordare="comparatie", valoare=res.valoare_piata,
        detalii={"index_selectat": res.index_selectat},
    )

# engine/venit.py:50-52
def abordare_venit(d: DateVenit) -> RezultatAbordare:
    r = evalueaza_venit(d)
    return RezultatAbordare(abordare="venit", valoare=r.valoare, detalii={"noi": str(r.noi)})
```

**Bonus colateral identificat:** după refactor, `RezultatAbordare.detalii` va include **CIN/CIB/depreciere fizică** (cost), **index selectat** (comparație), **NOI** (venit). Aceste detalii sunt acum **pierdute** și ar putea fi folosite în raport.

---

## 2. Conflict tehnic identificat

`construieste_context()` are nevoie de **AMBELE**:

1. `RezultatAbordare` (pentru `reconcile_profil()` → reconciliere) ✅ produs de `abordare_X`
2. `cost_result: CostResult` și `market_result: MarketResult` (stocate în `ReportContext` pentru raport) ❌ NU produs de `abordare_X` curent

Dacă apelezi DOAR `abordare_X`, pierzi `cost_result`/`market_result` interne. Dacă apelezi AMBELE, ai apeluri duble (`evaluate_cost` rulează de 2x).

---

## 3. Opțiuni de implementare

### Opțiunea α — `abordare_X` returnează tuple (recomandat)

Modifică `abordare_X` să returneze AMBELE rezultate:

```python
# engine/abordari.py — propus
def abordare_cost(
    building: BuildingData, valoare_teren: Decimal | None
) -> tuple[RezultatAbordare, CostResult]:
    res = evaluate_cost(building, valoare_teren=valoare_teren)
    return RezultatAbordare(
        abordare="cost", valoare=res.valoare_cost,
        detalii={"cin": str(res.cin), "cib": str(res.cib),
                 "depreciere_fizica": str(res.depreciere_fizica)},
    ), res

# assembler.py — propus
ra_cost, cost_result = abordare_cost(inp.building, valoare_teren=valoare_teren)
rezultate.append(ra_cost)
# cost_result rămâne disponibil pentru ReportContext
```

**Pro:**
- Single source: tot ce calculează cost (sau comparație, sau venit) trece printr-o funcție
- `RezultatAbordare.detalii` populat automat (raport mai bogat)
- Apel unic (zero overhead)

**Contra:**
- Schimbă signatura publică a `abordare_X` — **breaking change** pentru orice consumer extern
- 88 teste importă `abordare_X` și se așteaptă la `RezultatAbordare` direct
- Necesită update sincronizat în teste

**Risc test:** `tests/test_abordari.py`, `tests/test_faza0_echivalenta.py`, `tests/test_venit.py` apelează `abordare_X` și verifică `RezultatAbordare`. Refactor → toate apelurile devin `ra, _ = abordare_X(...)`.

### Opțiunea β — `abordare_X` rămâne thin, nou apel separat pentru detalii

```python
# engine/abordari.py — nimic schimbat
# assembler.py — propus
cost_result = evaluate_cost(inp.building, valoare_teren=valoare_teren)
rezultate.append(abordare_cost_from_result(cost_result))  # helper nou
```

**Pro:** API public `abordare_X` neschimbat.
**Contra:** Helper duplicat, NU rezolvă „single source of truth" — încă 2 căi de a obține `RezultatAbordare`.

### Opțiunea γ — Wrapper extins cu return rich

```python
# engine/abordari.py — nou format
@dataclass(frozen=True)
class AbordareCostFull:
    rezultat: RezultatAbordare
    internal: CostResult

def abordare_cost_full(building, valoare_teren) -> AbordareCostFull:
    res = evaluate_cost(building, valoare_teren=valoare_teren)
    ra = RezultatAbordare(abordare="cost", valoare=res.valoare_cost, detalii={...})
    return AbordareCostFull(rezultat=ra, internal=res)

# `abordare_cost` (legacy) rămâne backwards-compatible:
def abordare_cost(building, valoare_teren) -> RezultatAbordare:
    return abordare_cost_full(building, valoare_teren).rezultat
```

**Pro:** API extins compat înapoi; testele nu se schimbă.
**Contra:** 2 funcții cu nume similare (cost vs cost_full); UX dev mai confuz.

### Opțiunea δ — Refactor complet `ReportContext`

Elimină `cost_result`/`market_result` din `ReportContext`. Raportul citește totul din
`rezultate: list[RezultatAbordare]` cu `detalii` populat.

**Pro:** Cel mai curat conceptual.
**Contra:** Blast radius enorm (`report/generator.py`, `report/sectiuni.py`, `report/secțiunile docx`, teste). Risc regresie pe raport.

---

## 4. Recomandare

**Opțiunea α (tuple return)** — single source, schimbare API mică, beneficiu colateral
(detalii populate). Costul: actualizarea testelor (87+ apeluri, ~30 min mecanic).

Justificare:
- Vechi: 3 surse de adevăr (`evaluate_X`, `abordare_X`, manual în assembler)
- Nou: 1 sursă (`abordare_X`), care intern apelează `evaluate_X` și împachetează
- Test cost mecanic; semantic neschimbat (acceleratorul refactoringului IDE poate face find-replace)

---

## 5. Pași de implementare (pentru sesiune B sau loop autonom)

### Faza 1 — Refactor `engine/abordari.py` + `engine/venit.py`

Modifică cele 3 funcții să returneze `tuple[RezultatAbordare, InternalResult]`:

```python
# engine/abordari.py
from evaluare.engine.cost import CostResult, evaluate_cost
from evaluare.engine.market import MarketResult, evaluate_market

def abordare_cost(building, valoare_teren) -> tuple[RezultatAbordare, CostResult]:
    res = evaluate_cost(building, valoare_teren=valoare_teren)
    ra = RezultatAbordare(
        abordare="cost", valoare=res.valoare_cost,
        detalii={"cin": str(res.cin), "cib": str(res.cib),
                 "depreciere_fizica": str(res.depreciere_fizica)},
    )
    return ra, res

def abordare_comparatie(comparables, suprafata_subiect) -> tuple[RezultatAbordare, MarketResult]:
    res = evaluate_market(comparables, suprafata_subiect=suprafata_subiect)
    ra = RezultatAbordare(
        abordare="comparatie", valoare=res.valoare_piata,
        detalii={"index_selectat": res.index_selectat},
    )
    return ra, res

# engine/venit.py
def abordare_venit(d: DateVenit) -> tuple[RezultatAbordare, RezultatVenit]:
    r = evalueaza_venit(d)
    ra = RezultatAbordare(abordare="venit", valoare=r.valoare, detalii={"noi": str(r.noi)})
    return ra, r
```

### Faza 2 — Refactor `assembler.py:construieste_context`

```python
# assembler.py — schimbă blocul 130-158
cost_result = None
ra_cost = None
if inp.building.elements:
    ra_cost, cost_result = abordare_cost(inp.building, valoare_teren=valoare_teren)

market_result = None
ra_market = None
if inp.comparables:
    ra_market, market_result = abordare_comparatie(
        inp.comparables, suprafata_subiect=inp.building.acd
    )

venit_result = None
ra_venit = None
if inp.date_venit is not None:
    ra_venit, venit_result = abordare_venit(inp.date_venit)

# dcf rămâne neschimbat (nu există abordare_dcf)
dcf_valoare = None
if inp.date_dcf is not None:
    dcf_valoare = evalueaza_dcf(inp.date_dcf.fluxuri, inp.date_dcf.rata_actualizare,
                                inp.date_dcf.valoare_reziduala)

rezultate = []
if ra_cost is not None:
    rezultate.append(ra_cost)
if ra_market is not None:
    rezultate.append(ra_market)

# Venit/DCF: tot ce e curent neschimbat — DCF nu are abordare_X dedicată
venit_pt_reconciliere = None
if inp.metoda == "dcf":
    venit_pt_reconciliere = dcf_valoare
elif venit_result is not None:
    venit_pt_reconciliere = venit_result.valoare
if venit_pt_reconciliere is not None:
    if inp.metoda == "dcf":
        # DCF nu trece prin abordare_venit; păstrăm wrap manual
        rezultate.append(RezultatAbordare(abordare="venit", valoare=venit_pt_reconciliere,
                                          detalii={"sursa": "dcf"}))
    else:
        rezultate.append(ra_venit)
```

### Faza 3 — Actualizează importurile

În `assembler.py` adaugă:
```python
from evaluare.engine.abordari import abordare_cost, abordare_comparatie, RezultatAbordare
from evaluare.engine.venit import abordare_venit, evalueaza_venit, evalueaza_dcf, ...
```

Elimină:
```python
# from evaluare.engine.cost import evaluate_cost      # dacă rămâne nefolosit
# from evaluare.engine.market import evaluate_market  # dacă rămâne nefolosit
```

> **Atenție:** verifică dacă `evaluate_cost`/`evaluate_market` mai au consumatori în alte module
> (testele pot să importe direct motoarele).

### Faza 4 — Actualizează teste

Caută `abordare_cost(`, `abordare_comparatie(`, `abordare_venit(` în `tests/`:

```bash
grep -rn "abordare_\(cost\|comparatie\|venit\)" tests/
```

În fiecare loc:
```python
# Vechi:
r = abordare_cost(b, valoare_teren=Decimal("100000"))
assert r.abordare == "cost"

# Nou:
r, _ = abordare_cost(b, valoare_teren=Decimal("100000"))
assert r.abordare == "cost"
```

Fișiere afectate (din audit anterior):
- `tests/test_abordari.py` (2 puncte)
- `tests/test_faza0_echivalenta.py` (2 puncte)
- `tests/test_venit.py` (1 punct)

---

## 6. Verificare

```bash
cd evaluare-anevar
ruff check src tests
pytest -q --cov=evaluare --cov-report=term-missing
```

Target: **531 teste verzi** (nu scădem coverage). `fail_under=90` păstrat.

---

## 7. Beneficii colaterale documentate

După refactor, `RezultatAbordare.detalii` populat → raportul poate cita:
- Pentru cost: **CIN, CIB, depreciere fizică** (acum afișate în secțiunea cost a raportului)
- Pentru comparație: **index selectat** (care comparabil a fost ales ca referință)
- Pentru venit: **NOI** (Net Operating Income — cifră cheie SEV 2025)

Aceste detalii erau **invizibile în raport** până acum. După refactor, `report/generator.py` poate
opta să le includă (nu obligatoriu — backward compatible).

---

## 8. Decupling risc

**Risc:** schimbarea signaturii rupe consumeri externi (cazul rar — funcțiile nu apar în API public,
doar în `engine/` intern).

**Mitigare:** opțional, pot crea ALIAS-uri pentru backward-compat:
```python
def abordare_cost_only(building, valoare_teren) -> RezultatAbordare:
    """Backward-compat alias (deprecated, va fi eliminat în vN+2)."""
    return abordare_cost(building, valoare_teren)[0]
```

Dar nu e necesar dacă verificăm cross-references înainte (vezi pas Faza 3).

---

## 9. Acceptare

Refactor #36 e considerat FINISHED când:
- [ ] Cele 3 funcții `abordare_X` returnează `tuple[RezultatAbordare, InternalResult]`
- [ ] `assembler.py:construieste_context` folosește `abordare_X`, NU `evaluate_X` direct (pentru cost/comparație/venit)
- [ ] Toate testele verzi (531+)
- [ ] `pytest --cov` ≥ 90% pe `evaluare`
- [ ] `ruff check` curat
- [ ] Decizia #36 marcată RESOLVED-IMPLEMENTAT în `.memplan/decisions/log.mem`
- [ ] Task `impl-refactor-assembler-abordare-X` marcat `status=done` în `.memplan/inbox/tasks.mem`

---

*Generat în sesiunea C (worktree `anevar-c`, ramura `sesiune-c`) — docs only, fără editări de cod.*
*Implementarea recomandată: sesiune B sau loop autonom după ce sesiune A face merge spec-ului în master.*
