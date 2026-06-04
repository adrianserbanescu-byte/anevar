# Faza 1 — Apartament (rezidențial, garantare credit) — Plan de implementare

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Checkbox steps.

**Goal:** Suport pentru evaluarea **apartamentului** prin comparație (+cost), strict aditiv:
profil `APARTAMENT_GARANTARE`, câmpuri specifice de apartament (etaj, nivel bloc, an bloc, cotă teren),
descriere de raport adaptată, selector „tip proprietate" în wizard. Motorul de comparație rămâne neschimbat.

**Architecture:** Câmpuri opționale noi pe `BuildingData` (default `None` → casă neschimbată). Profil nou.
Descrierea din raport adaugă o linie „Apartament: …" doar când câmpurile sunt prezente. Wizardul capătă un
selector care arată câmpurile de apartament și le trimite în payload. Fără modificări de motor de calcul.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, FastAPI/Jinja, vanilla JS. Fără dependențe noi.

---

## Task 1: Profil `APARTAMENT_GARANTARE`

**Files:** Modify `src/evaluare/profil.py` · Test `tests/test_profil_apartament.py`

- [ ] **Step 1** — `tests/test_profil_apartament.py`:
```python
from evaluare.profil import APARTAMENT_GARANTARE


def test_profil_apartament():
    assert APARTAMENT_GARANTARE.tip_activ == "apartament"
    assert APARTAMENT_GARANTARE.scop == "garantare_credit"
    assert APARTAMENT_GARANTARE.ghid == "GEV_520"
    assert APARTAMENT_GARANTARE.abordari_aplicabile == ["comparatie", "cost"]
```
- [ ] **Step 2** — `python -m pytest tests/test_profil_apartament.py -q` → FAIL (ImportError).
- [ ] **Step 3** — append to `src/evaluare/profil.py` (after `CASA_TEREN_GARANTARE`):
```python
APARTAMENT_GARANTARE = ProfilEvaluare(
    tip_activ="apartament", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["comparatie", "cost"], ghid="GEV_520",
)
```
- [ ] **Step 4** — tests pass (1).
- [ ] **Step 5** — `git add -A && git commit -m "Faza 1: profil APARTAMENT_GARANTARE"`

---

## Task 2: Câmpuri de apartament pe `BuildingData` + validare

**Files:** Modify `src/evaluare/models/property.py`, `src/evaluare/engine/validation.py` · Test `tests/test_apartament_model.py`

`BuildingData` are deja câmpuri opționale (`ac`, `structura`, `finisaje`, `clasa_energetica`). Adăugăm încă
patru, toate `Optional`, default `None` (casă neschimbată). `valideaza_proprietate(land, building)` există
în `validation.py` și întoarce `list[Issue]` (`Issue(nivel="blocheaza"|"alerteaza", mesaj=...)`).

- [ ] **Step 1** — `tests/test_apartament_model.py`:
```python
from decimal import Decimal

from evaluare.models.property import BuildingData, LandData
from evaluare.engine.validation import valideaza_proprietate


def _land():
    return LandData(suprafata=Decimal("1"))


def _ap(**kw):
    base = dict(au=Decimal("60"), acd=Decimal("70"), an_referinta=2025)
    base.update(kw)
    return BuildingData(**base)


def test_campuri_apartament_optionale():
    b = _ap(etaj=3, nr_niveluri_bloc=10, an_bloc=2008, cota_teren_indiviza=Decimal("12.5"))
    assert b.etaj == 3 and b.nr_niveluri_bloc == 10 and b.an_bloc == 2008
    assert b.cota_teren_indiviza == Decimal("12.5")


def test_casa_fara_campuri_apartament():
    b = _ap()
    assert b.etaj is None and b.an_bloc is None


def test_etaj_peste_numar_niveluri_blocheaza():
    issues = valideaza_proprietate(_land(), _ap(etaj=12, nr_niveluri_bloc=10))
    assert any(i.nivel == "blocheaza" and "etaj" in i.mesaj.lower() for i in issues)


def test_etaj_in_limite_ok():
    issues = valideaza_proprietate(_land(), _ap(etaj=3, nr_niveluri_bloc=10))
    assert not any("etaj" in i.mesaj.lower() for i in issues)
```
- [ ] **Step 2** — run → FAIL (no etaj field).
- [ ] **Step 3a** — in `src/evaluare/models/property.py`, inside `BuildingData`, after `clasa_energetica`:
```python
    # apartament (optionale; None pentru casa)
    etaj: Optional[int] = None
    nr_niveluri_bloc: Optional[int] = None
    an_bloc: Optional[int] = None
    cota_teren_indiviza: Optional[Decimal] = None
```
- [ ] **Step 3b** — in `src/evaluare/engine/validation.py`, inside `valideaza_proprietate`, before `return issues`:
```python
    if (building.etaj is not None and building.nr_niveluri_bloc is not None
            and building.etaj > building.nr_niveluri_bloc):
        issues.append(Issue(nivel="blocheaza",
                            mesaj="Etajul nu poate depasi numarul de niveluri ale blocului."))
```
- [ ] **Step 4** — tests pass (4) + FULL suite green. `pyflakes` clean.
- [ ] **Step 5** — commit `"Faza 1: campuri apartament pe BuildingData + validare etaj<=niveluri"`

---

## Task 3: Descrierea de raport adaptată apartamentului

**Files:** Modify `src/evaluare/report/generator.py` · Test `tests/test_report_apartament.py`

Funcția care scrie capitolul „4. DESCRIEREA…" conține:
```python
    doc.add_paragraph(
        f"Constructie: Au {ctx.building.au} mp, Acd {ctx.building.acd} mp, "
        f"an referinta {ctx.building.an_referinta}."
    )
```
Adăugăm o linie „Apartament: …" DOAR când există câmpuri de apartament (casă neschimbată → cele 12 teste
`test_report_generator.py` rămân verzi).

- [ ] **Step 1** — `tests/test_report_apartament.py` (urmează tiparul din `test_report_generator.py`:
construiește un `ReportContext` minim, generează `.docx` într-un `tmp_path`, citește textul cu `python-docx`).
CITEȘTE întâi `tests/test_report_generator.py` ca să refolosești helperul de construcție a contextului și de
extragere a textului. Testul: un context cu `building.etaj=3, nr_niveluri_bloc=10, an_bloc=2008` → textul
raportului conține „Apartament" și „etaj 3"; un context fără aceste câmpuri → textul NU conține „Apartament:".
- [ ] **Step 2** — run → FAIL.
- [ ] **Step 3** — în `generator.py`, imediat după paragraful „Constructie: …":
```python
    if ctx.building.etaj is not None or ctx.building.an_bloc is not None:
        parti = []
        if ctx.building.etaj is not None:
            niv = f"/{ctx.building.nr_niveluri_bloc}" if ctx.building.nr_niveluri_bloc else ""
            parti.append(f"etaj {ctx.building.etaj}{niv}")
        if ctx.building.an_bloc is not None:
            parti.append(f"an bloc {ctx.building.an_bloc}")
        if ctx.building.cota_teren_indiviza is not None:
            parti.append(f"cota teren indiviza {ctx.building.cota_teren_indiviza} mp")
        doc.add_paragraph("Apartament: " + ", ".join(parti) + ".")
```
- [ ] **Step 4** — noul test + cele 12 din `test_report_generator.py` verzi; FULL suite verde.
- [ ] **Step 5** — commit `"Faza 1: descriere raport adaptata apartamentului (conditional)"`

---

## Task 4: Wizard — selector „tip proprietate" + câmpuri apartament

**Files:** Modify `src/evaluare/web/templates/wizard.html` · Test `tests/test_web_wizard.py`

Aditiv în wizard: la Pas 2 (Proprietatea subiect) adăugăm un `<select id="tip_proprietate">` (casă/apartament)
și un bloc de câmpuri de apartament (`etaj`, `nr_niveluri_bloc`, `an_bloc`, `cota_teren_indiviza`) ascuns
implicit, afișat când se alege „apartament". În `asambleaza()`, când câmpurile sunt completate, se adaugă în
obiectul `building`. Adăugăm id-urile noi în lista `CAMPURI` (persistență localStorage).

- [ ] **Step 1** — adaugă în `tests/test_web_wizard.py`:
```python
def test_wizard_are_selector_tip_proprietate(tmp_path):
    body = _client(tmp_path).get("/wizard").text
    assert 'id="tip_proprietate"' in body
    assert 'id="etaj"' in body and 'id="an_bloc"' in body
```
- [ ] **Step 2** — run → FAIL.
- [ ] **Step 3** — în `wizard.html`:
  - La începutul Pas 2 (`<section id="pas-2">`, după `<h2>` / `<p class="rezumat">`), adaugă:
    ```html
    <label for="tip_proprietate">Tip proprietate</label>
    <select id="tip_proprietate" onchange="document.getElementById('ap-fields').style.display=this.value==='apartament'?'block':'none'">
      <option value="casa">Casă individuală + teren</option>
      <option value="apartament">Apartament</option>
    </select>
    <div id="ap-fields" style="display:none">
      <label for="etaj">Etaj</label><input id="etaj" type="number">
      <label for="nr_niveluri_bloc">Număr niveluri bloc</label><input id="nr_niveluri_bloc" type="number">
      <label for="an_bloc">An construcție bloc</label><input id="an_bloc" type="number">
      <label for="cota_teren_indiviza">Cotă teren indiviză (mp)</label><input id="cota_teren_indiviza">
      <small class="hint">Câmpuri pentru apartament; la „Casă" se ignoră.</small>
    </div>
    ```
  - În JS, adaugă în array-ul `CAMPURI` cele cinci id-uri noi:
    `"tip_proprietate","etaj","nr_niveluri_bloc","an_bloc","cota_teren_indiviza"`.
  - În funcția `asambleaza()`, în obiectul `building`, după `acd`/`an_referinta`, adaugă (trimite doar dacă e completat):
    ```javascript
    // câmpuri apartament (doar dacă sunt completate)
    if($("etaj").value) building.etaj=parseInt($("etaj").value);
    if($("nr_niveluri_bloc").value) building.nr_niveluri_bloc=parseInt($("nr_niveluri_bloc").value);
    if($("an_bloc").value) building.an_bloc=parseInt($("an_bloc").value);
    if($("cota_teren_indiviza").value) building.cota_teren_indiviza=$("cota_teren_indiviza").value;
    ```
    (Adaptează la forma reală a obiectului `building` din `asambleaza()` — CITEȘTE funcția întâi; `building`
    e construit ca obiect literal, adaugă proprietățile condiționat după construcție dacă e mai curat.)
- [ ] **Step 4** — noul test trece; FULL suite verde; pornește exe local nu e necesar aici.
- [ ] **Step 5** — commit `"Faza 1: wizard — selector tip proprietate + campuri apartament"`

---

## Task 5: Verificare finală + rebuild exe

- [ ] `python -m pytest -q` → all green.
- [ ] `python -m pyflakes src/` → clean.
- [ ] Rebuild exe + smoke: pornește exe, `POST /api/evaluare` cu un building care are `etaj`/`an_bloc` și
      `metoda="piata"` (3 comparabile) → 200, `valoare_finala>0`; `GET /wizard` → 200 cu `id="tip_proprietate"`.
- [ ] Commit final dacă e cazul.

## Self-review
- Profil apartament → T1. Câmpuri + validare → T2. Raport → T3. Wizard → T4. Verificare → T5.
- Aditiv: toate câmpurile `Optional`/`None`; casă neschimbată (regresie pe `test_report_generator` + suită).
