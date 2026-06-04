# Faza 2 — Comercial / venit (abordarea prin venit în flux) — Plan de implementare

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Checkbox steps.

**Goal:** Evaluare prin **abordarea prin venit** (capitalizare directă) end-to-end, aditiv: profil
`COMERCIAL_INCHIRIAT`, `EvaluationInput` acceptă `date_venit`, `construieste_context` rulează venitul și îl
reconciliază prin `reconcile_profil`, raportul randează o secțiune de venit (condițional), wizardul oferă
metoda „venit" + câmpurile de venit. Motoarele cost/comparație rămân neschimbate; casă+teren neschimbat.

**Tech:** Python 3.12, Pydantic v2, pytest, FastAPI/Jinja, JS. Motorul `evalueaza_venit` există din Faza 0.
**Validare:** pe standard (SEV/IVS + GEV 630) + exemple sintetice; dosar real = sarcină marcată.

---

## Task 1: Profil `COMERCIAL_INCHIRIAT`
**Files:** Modify `src/evaluare/profil.py` · Test `tests/test_profil_comercial.py`
- [ ] **Step 1** — `tests/test_profil_comercial.py`:
```python
from evaluare.profil import COMERCIAL_INCHIRIAT


def test_profil_comercial():
    assert COMERCIAL_INCHIRIAT.tip_activ == "comercial"
    assert COMERCIAL_INCHIRIAT.ghid == "GEV_630"
    assert COMERCIAL_INCHIRIAT.abordari_aplicabile == ["venit", "comparatie"]
```
- [ ] **Step 2** — run → FAIL.
- [ ] **Step 3** — append to `src/evaluare/profil.py`:
```python
COMERCIAL_INCHIRIAT = ProfilEvaluare(
    tip_activ="comercial", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["venit", "comparatie"], ghid="GEV_630",
)
```
- [ ] **Step 4** — 1 passed; FULL suite green. — [ ] **Step 5** — commit `"Faza 2: profil COMERCIAL_INCHIRIAT"`.

---

## Task 2: `date_venit` în flux + `venit_result`/`date_venit` pe `ReportContext`
**Files:** Modify `src/evaluare/assembler.py`, `src/evaluare/models/report_context.py` · Test `tests/test_assembler_venit.py`

Context: `EvaluationInput` (în `assembler.py`) are `metoda: Literal["piata","cost","ponderata"]`. În
`construieste_context` se construiește `rezultate: list[RezultatAbordare]` (cost + comparatie) și se cheamă
`reconcile_profil(rezultate, primara, ponderi)`. `evalueaza_venit(DateVenit) -> RezultatVenit(noi, valoare)`
și `DateVenit` sunt în `evaluare.engine.venit`.

- [ ] **Step 1** — `tests/test_assembler_venit.py`:
```python
from decimal import Decimal

from evaluare.assembler import EvaluationInput, construieste_context


def _input_venit():
    return EvaluationInput(
        meta={"client_nume": "C", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF",
              "evaluator_nume": "E", "evaluator_legitimatie": "1",
              "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        land={"suprafata": "200"},
        building={"au": "300", "acd": "320", "an_referinta": 2025, "elements": [],
                  "depreciation_points": []},
        valoare_teren="0", metoda="venit",
        date_venit={"venit_brut_potential": "100000", "grad_neocupare": "0.05",
                    "cheltuieli_exploatare": "20000", "rata_capitalizare": "0.08"},
    )


def test_evaluare_prin_venit():
    ctx = construieste_context(_input_venit(), client=None)
    assert ctx.reconciled.metoda_selectata == "venit"
    assert ctx.reconciled.valoare_finala == Decimal("937500.00")
    assert ctx.venit_result is not None and ctx.venit_result.noi == Decimal("75000.00")
    assert ctx.date_venit is not None
```
- [ ] **Step 2** — run → FAIL (metoda "venit" invalid / date_venit field missing).
- [ ] **Step 3a** — `src/evaluare/models/report_context.py`: add import + two fields:
```python
from evaluare.engine.venit import DateVenit, RezultatVenit  # add to imports
# in class ReportContext, after `profil`:
    venit_result: Optional[RezultatVenit] = None
    date_venit: Optional[DateVenit] = None
```
- [ ] **Step 3b** — `src/evaluare/assembler.py`:
  - imports: add `from evaluare.engine.venit import DateVenit, evalueaza_venit`.
  - `EvaluationInput`: change `metoda: Literal["piata", "cost", "ponderata"] = "cost"` to
    `metoda: Literal["piata", "cost", "ponderata", "venit"] = "cost"`; add field `date_venit: Optional[DateVenit] = None`.
  - In `construieste_context`, after `market_result` is computed and BEFORE building `rezultate`, compute venit:
    ```python
    venit_result = None
    if inp.date_venit is not None:
        venit_result = evalueaza_venit(inp.date_venit)
    ```
  - When building `rezultate` (the `RezultatAbordare` list), after appending cost and comparatie, add:
    ```python
    if venit_result is not None:
        rezultate.append(RezultatAbordare(abordare="venit", valoare=venit_result.valoare))
    ```
  - In the metoda→primara mapping, add a branch for "venit" BEFORE the cost/piata/ponderata ones:
    ```python
    if inp.metoda == "venit":
        primara, ponderi = "venit", None
    elif inp.metoda == "cost":
        primara, ponderi = "cost", None
    elif inp.metoda == "piata":
        primara, ponderi = "comparatie", None
    else:
        primara = "comparatie"
        ponderi = {"comparatie": inp.pondere_piata, "cost": Decimal("1") - inp.pondere_piata}
    ```
  - In the `ReportContext(...)` construction add: `venit_result=venit_result, date_venit=inp.date_venit,`.
- [ ] **Step 4** — `python -m pytest tests/test_assembler_venit.py -q` → 1 passed. FULL suite green. `pyflakes src/evaluare/assembler.py src/evaluare/models/report_context.py` clean. If a house value test breaks, STOP (BLOCKED).
- [ ] **Step 5** — commit `"Faza 2: date_venit in flux + venit_result pe ReportContext"`.

---

## Task 3: Raport — secțiunea „Abordarea prin venit" (condițional)
**Files:** Modify `src/evaluare/report/generator.py` · Test `tests/test_report_venit.py`

Adăugăm o secțiune randată DOAR când `ctx.venit_result` există (casă neschimbată → cele 12 teste de raport rămân verzi). Plasare: în capitolul abordărilor (lângă tabelul de cost / grila de comparație).

- [ ] **Step 1** — `tests/test_report_venit.py`: refolosește helperul de context din `test_report_generator.py`; setează `ctx.venit_result` și `ctx.date_venit` (din `evaluare.engine.venit`: `RezultatVenit(noi=Decimal('75000.00'), valoare=Decimal('937500.00'))` și `DateVenit(venit_brut_potential=Decimal('100000'), grad_neocupare=Decimal('0.05'), cheltuieli_exploatare=Decimal('20000'), rata_capitalizare=Decimal('0.08'))`), generează `.docx`, citește textul; assert conține „Abordarea prin venit" și „937" (valoarea) și „capitalizare". Un context fără venit → textul NU conține „Abordarea prin venit".
- [ ] **Step 2** — run → FAIL.
- [ ] **Step 3** — în `generator.py`, găsește funcția care scrie capitolul de abordări (cea care cheamă `_adauga_tabel_cost(doc, ctx)` și/sau `_adauga_grila_comparatie(doc, ctx)`). Imediat după acel apel, adaugă:
```python
    if ctx.venit_result is not None:
        doc.add_heading("Abordarea prin venit (capitalizare directă)", level=2)
        dv, vr = ctx.date_venit, ctx.venit_result
        if dv is not None:
            doc.add_paragraph(
                f"Venit brut potențial: {dv.venit_brut_potential} lei/an; "
                f"neocupare {dv.grad_neocupare}; cheltuieli {dv.cheltuieli_exploatare} lei/an; "
                f"rată de capitalizare {dv.rata_capitalizare}."
            )
        doc.add_paragraph(
            f"Venit net din exploatare (NOI): {vr.noi} lei. "
            f"Valoare = NOI / rată = {vr.valoare} lei."
        )
```
(Dacă funcția primește `adnotari`, păstrează semnătura; nu schimba nimic existent.)
- [ ] **Step 4** — noul test + cele 12 din `test_report_generator.py` verzi; FULL suite green; pyflakes clean.
- [ ] **Step 5** — commit `"Faza 2: sectiune raport - abordarea prin venit (conditional)"`.

---

## Task 4: Wizard — metoda „venit" + câmpuri de venit
**Files:** Modify `src/evaluare/web/templates/wizard.html` · Test `tests/test_web_wizard.py`

La Pas 4 (Metodă & calcul) există `<select id="metoda">` cu cost/piata/ponderata. Adăugăm opțiunea
„venit" și un bloc de câmpuri de venit (`vbp`, `neocupare`, `cheltuieli`, `rata_cap`) afișat când metoda
e „venit". În `asambleaza()`, când câmpurile sunt completate, trimite `date_venit` în payload.

- [ ] **Step 1** — adaugă în `tests/test_web_wizard.py`:
```python
def test_wizard_are_metoda_venit(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'value="venit"' in body
    assert 'id="vbp"' in body and 'id="rata_cap"' in body
```
- [ ] **Step 2** — run → FAIL.
- [ ] **Step 3** — în `wizard.html`:
  - În `<select id="metoda">`, adaugă `<option value="venit">Venit (capitalizare directă)</option>`.
  - Adaugă pe `#metoda` un `onchange` care arată/ascunde blocul de venit:
    `onchange="document.getElementById('venit-fields').style.display=this.value==='venit'?'block':'none'"`.
  - Imediat după select-ul de metodă (sau lângă el), adaugă:
    ```html
    <div id="venit-fields" style="display:none">
      <label for="vbp">Venit brut potențial (lei/an)</label><input id="vbp">
      <label for="neocupare">Grad neocupare (0–1)</label><input id="neocupare" value="0">
      <label for="cheltuieli">Cheltuieli exploatare (lei/an)</label><input id="cheltuieli" value="0">
      <label for="rata_cap">Rată de capitalizare (0–1)</label><input id="rata_cap">
      <small class="hint">Pentru metoda „venit": valoare = NOI ÷ rată de capitalizare.</small>
    </div>
    ```
  - Adaugă în `CAMPURI`: `"vbp","neocupare","cheltuieli","rata_cap"`.
  - În `asambleaza()`, înainte de `return`, construiește `date_venit` și include-l în payload când metoda e „venit" și `vbp`+`rata_cap` sunt completate:
    ```javascript
    let date_venit=null;
    if($("metoda").value==="venit" && $("vbp").value && $("rata_cap").value){
      date_venit={venit_brut_potential:$("vbp").value, grad_neocupare:$("neocupare").value||"0",
        cheltuieli_exploatare:$("cheltuieli").value||"0", rata_capitalizare:$("rata_cap").value};
    }
    ```
    și adaugă `date_venit` în obiectul returnat (lângă `metoda`): dacă `date_venit` e `null`, e ok (backend-ul îl ignoră).
- [ ] **Step 4** — noul test trece; FULL suite green.
- [ ] **Step 5** — commit `"Faza 2: wizard - metoda venit + campuri de venit"`.

---

## Task 5: Verificare finală + rebuild exe
- [ ] `python -m pytest -q` → all green. `python -m pyflakes src/` → clean.
- [ ] Rebuild exe + smoke: `POST /api/evaluare` cu `metoda="venit"` + `date_venit` → 200, `valoare_finala=937500.00`,
      `metoda="venit"`; `GET /wizard` conține `value="venit"`.
- [ ] Commit final dacă e cazul.

## Self-review
- Profil → T1. Flux venit → T2. Raport → T3. Wizard → T4. Verificare → T5.
- Aditiv: `date_venit` Optional/None; metoda extinsă (compatibil); secțiunea de raport condițională.
- Amânat în continuare: refactor complet generator pe `SectiuneSpec`, Protocol `Abordare`, `detalii` tipizat,
  DCF + grilă chirii (Faza 6). Validare pe dosar real comercial — marcată.
