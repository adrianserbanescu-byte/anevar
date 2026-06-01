# Dropdown județ + localitate în wizard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Înlocuiește Pas 1 al wizard-ului (adresă free-text + LLM) cu dropdown județ + dropdown localitate cascadat (slug-uri identice cu imobiliare.ro) + free-text pentru restul adresei.

**Architecture:** Un fișier de date static `data/judete_localitati.json` (generat o dată dintr-o sursă publică), modul `localitati.py` care îl încarcă, endpoint `GET /api/localitati`, și modificarea Pas 1 din `wizard.html` (dropdown-uri cascadate + override + slug-uri directe în descoperire).

**Tech Stack:** Python 3.11+, FastAPI, pytest. Fără dependențe noi.

**Spec sursă:** `docs/superpowers/specs/2026-06-01-localitati-dropdown-design.md`.
**Depinde de:** wizard-ul existent. Branch: `feature/nucleu-calcul`.
**Sursă date (confirmată accesibilă):** `https://raw.githubusercontent.com/virgil-av/judet-oras-localitati-romania/master/judete.json` — `{"judete":[{"auto","nume","localitati":[{"nume","simplu?"}]}]}`.

---

## Structura de fișiere

```
evaluare-anevar/
├── scripts/build_localitati.py     # NOU: descarca + normalizeaza -> JSON static (rulat manual)
├── src/evaluare/
│   ├── localitati.py               # NOU: incarca JSON, slugify, judete()/localitati()
│   ├── data/judete_localitati.json # NOU: dataset generat (commis, impachetat in exe)
│   └── web/app.py                  # MODIFICAT: GET /api/localitati
├── evaluare-anevar.spec            # MODIFICAT: include data/ in build
└── tests/
    ├── test_localitati.py          # NOU
    └── test_web_localitati.py      # NOU
```

---

## Phase 1 — Slugify + script de build + dataset

### Task 1: `localitati.py` (slugify + loader) și generarea dataset-ului

**Files:**
- Create: `src/evaluare/localitati.py`
- Create: `scripts/build_localitati.py`
- Create: `src/evaluare/data/judete_localitati.json`  (generat de script)
- Test: `tests/test_localitati.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_localitati.py`:
```python
from evaluare.localitati import slugify, judete, localitati


def test_slugify_normalizeaza():
    assert slugify("Ilfov") == "ilfov"
    assert slugify("Alba Iulia") == "alba-iulia"
    assert slugify("Baia de Arieş") == "baia-de-aries"
    assert slugify("Ceru-Băcăinţi") == "ceru-bacainti"
    assert slugify("Sfântu Gheorghe") == "sfantu-gheorghe"


def test_judete_returneaza_42():
    j = judete()
    assert len(j) == 42
    assert all("nume" in x and "slug" in x for x in j)
    # ordonate alfabetic dupa nume
    nume = [x["nume"] for x in j]
    assert nume == sorted(nume)
    # contine Ilfov
    assert any(x["slug"] == "ilfov" for x in j)


def test_localitati_pentru_judet():
    loc = localitati("ilfov")
    assert len(loc) > 0
    assert all("nume" in x and "slug" in x for x in loc)
    assert any(x["slug"] == "otopeni" for x in loc)


def test_localitati_judet_inexistent_lista_goala():
    assert localitati("xxx") == []
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_localitati.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.localitati'`.

- [ ] **Step 3a: Implementează `localitati.py`**

`src/evaluare/localitati.py`:
```python
"""Liste judete + localitati (statice) cu slug-uri compatibile portalurilor imobiliare."""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).parent / "data" / "judete_localitati.json"


def slugify(text: str) -> str:
    """lowercase, fara diacritice, secvente non-alfanumerice -> o cratima."""
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_DATA, encoding="utf-8") as f:
        return json.load(f)


def judete() -> list[dict]:
    """Lista celor 42 de judete: [{nume, slug}], ordonate alfabetic."""
    return _load()["judete"]


def localitati(judet_slug: str) -> list[dict]:
    """Localitatile dintr-un judet: [{nume, slug}]. Lista goala daca judetul nu exista."""
    return _load()["localitati"].get(judet_slug, [])
```

- [ ] **Step 3b: Scrie scriptul de build**

`scripts/build_localitati.py`:
```python
"""Genereaza src/evaluare/data/judete_localitati.json din sursa publica (rulat manual)."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from evaluare.localitati import slugify  # noqa: E402

SURSA = ("https://raw.githubusercontent.com/virgil-av/"
         "judet-oras-localitati-romania/master/judete.json")
IESIRE = Path(__file__).resolve().parents[1] / "src" / "evaluare" / "data" / "judete_localitati.json"


def main() -> None:
    raw = urllib.request.urlopen(SURSA, timeout=30).read()
    data = json.loads(raw)
    judete = []
    localitati = {}
    for j in data["judete"]:
        jslug = slugify(j["nume"])
        judete.append({"nume": j["nume"], "slug": jslug})
        vazute = set()
        lista = []
        for loc in j.get("localitati", []):
            nume = loc.get("simplu") or loc["nume"]
            slug = slugify(loc["nume"])
            if slug and slug not in vazute:
                vazute.add(slug)
                lista.append({"nume": loc["nume"], "slug": slug})
        localitati[jslug] = sorted(lista, key=lambda x: x["nume"])
    judete.sort(key=lambda x: x["nume"])
    IESIRE.parent.mkdir(parents=True, exist_ok=True)
    with open(IESIRE, "w", encoding="utf-8") as f:
        json.dump({"judete": judete, "localitati": localitati}, f,
                  ensure_ascii=False, indent=0)
    total = sum(len(v) for v in localitati.values())
    print(f"Scris {len(judete)} judete, {total} localitati -> {IESIRE}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3c: Generează dataset-ul**

Run (din `evaluare-anevar/`): `python scripts/build_localitati.py`
Expected: `Scris 42 judete, <mii> localitati -> .../judete_localitati.json`. Dacă rețeaua dă
timeout, reîncearcă; sursa a fost confirmată accesibilă.

- [ ] **Step 4: Rulează testele**

Run: `python -m pytest tests/test_localitati.py -v`
Expected: PASS (4 teste). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/localitati.py evaluare-anevar/scripts/build_localitati.py evaluare-anevar/src/evaluare/data/judete_localitati.json evaluare-anevar/tests/test_localitati.py
git commit -m "feat: liste judete+localitati statice (slugify) + script build dataset"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Endpoint

### Task 2: `GET /api/localitati`

**Files:**
- Modify: `src/evaluare/web/app.py`
- Test: `tests/test_web_localitati.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_web_localitati.py`:
```python
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_get_localitati(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/api/localitati")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["judete"]) == 42
    assert any(j["slug"] == "ilfov" for j in data["judete"])
    assert any(l["slug"] == "otopeni" for l in data["localitati"]["ilfov"])
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_localitati.py -v`
Expected: FAIL (404).

- [ ] **Step 3: Adaugă endpoint-ul în `app.py`**

Adaugă importul (lângă celelalte):
```python
from evaluare.localitati import judete as _judete, localitati as _localitati
```
Adaugă ruta în `create_app`, înainte de `return app`:
```python
    @app.get("/api/localitati")
    def lista_localitati() -> dict:
        judete = _judete()
        return {"judete": judete,
                "localitati": {j["slug"]: _localitati(j["slug"]) for j in judete}}
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_localitati.py -v`
Expected: PASS (1 test). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/tests/test_web_localitati.py
git commit -m "feat: endpoint GET /api/localitati"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — Pas 1 wizard cu dropdown-uri

### Task 3: Modifică `wizard.html` (Pas 1)

**Files:**
- Modify: `src/evaluare/web/templates/wizard.html`
- Test: `tests/test_web_wizard.py` (extinde)

**Context de design:** înlocuiește în Pas 1 input-ul `adresa` + input-urile `judet`/`localitate` cu:
dropdown județ (`id="judet"`), dropdown localitate (`id="localitate"`), input free-text stradă
(`id="adresa_strada"`). Populează din `/api/localitati` la încărcare; cascadează localitatea la
schimbarea județului. Opțiune „altă localitate" → input text `id="localitate_alt"`. La asamblare,
`judet`/`localitate` = slug-urile selectate; `adresa` (raport) = `{strada}, {localitate nume}, {judet nume}`.

- [ ] **Step 1: Extinde testul**

În `tests/test_web_wizard.py`, adaugă:
```python
def test_wizard_pas1_are_dropdown_judet_localitate(tmp_path):
    client = _client(tmp_path)
    body = client.get("/wizard").text
    assert '<select id="judet"' in body
    assert '<select id="localitate"' in body
    assert "/api/localitati" in body
    assert 'id="adresa_strada"' in body
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_wizard.py::test_wizard_pas1_are_dropdown_judet_localitate -v`
Expected: FAIL.

- [ ] **Step 3: Modifică `wizard.html`**

(a) Înlocuiește, în secțiunea `id="pas-1"`, blocul de la `<label>Adresa proprietății</label>` până
la linia cu `<span id="zona_status"...></p>` (adresa + județ/localitate text + zona_status) cu:
```html
  <label>Județ</label>
  <select id="judet"></select>
  <label>Localitate</label>
  <select id="localitate"></select>
  <input id="localitate_alt" placeholder="altă localitate (slug)" style="display:none">
  <small class="hint">Județ și localitate aleg slug-ul exact folosit la căutarea comparabilelor.</small>
  <label>Stradă, număr (rest adresă)</label>
  <input id="adresa_strada" size="50" placeholder="Str. Exemplu nr. 10">
```
(b) În lista `CAMPURI`, înlocuiește `"adresa"` și păstrează `"judet","localitate"`; adaugă
`"adresa_strada"` și `"localitate_alt"`. (Scoate `"adresa"` din listă dacă nu mai există input cu
acel id.) Lista devine, la început:
```javascript
const CAMPURI = ["judet","localitate","localitate_alt","adresa_strada","client_nume",
 "numar_cadastral","carte_funciara","evaluator_nume","evaluator_legitimatie",
 "data_evaluarii","data_raportului","suprafata_teren","au","acd","an_referinta",
 "valoare_teren","elemente","depreciere","attr_an","attr_stare","attr_finisaj",
 "attr_incalzire","comparabile","metoda"];
```
(c) Înlocuiește funcția `deriveZona` cu popularea dropdown-urilor (nu mai apelăm `/api/zona`):
```javascript
let LOCALITATI = {};
async function incarcaLocalitati(){
  try{ const r=await fetch("/api/localitati"); const d=await r.json();
    LOCALITATI=d.localitati;
    const js=$("judet"); js.innerHTML='<option value="">— județ —</option>'+
      d.judete.map(j=>`<option value="${j.slug}">${j.nume}</option>`).join("");
    js.addEventListener("change", populeazaLocalitati);
    populeazaLocalitati();
  }catch(e){ /* fara liste: raman goale */ }
}
function populeazaLocalitati(){
  const ls=$("localitate"); const lst=LOCALITATI[$("judet").value]||[];
  ls.innerHTML='<option value="">— localitate —</option>'+
    lst.map(l=>`<option value="${l.slug}">${l.nume}</option>`).join("")+
    '<option value="__alt__">— altă localitate (scriu) —</option>';
  ls.addEventListener("change", ()=>{ 
    $("localitate_alt").style.display = ls.value==="__alt__" ? "inline" : "none"; });
}
function localitateSlug(){ const v=$("localitate").value;
  return v==="__alt__" ? ($("localitate_alt").value.trim()) : v; }
```
(d) În handler-ul butonului „Înainte", înlocuiește `if(pas===1){ await deriveZona(); }` cu nimic
(pasul 1 nu mai cheamă LLM); dropdown-urile se populează la încărcare.
(e) În `btn-descopera`, schimbă `localitate:$("localitate").value` în `localitate:localitateSlug()`.
(f) În `asambleaza()`, schimbă `adresa:$("adresa").value` în:
```javascript
      adresa:[$("adresa_strada").value, ($("localitate").selectedOptions[0]||{}).text||"",
              ($("judet").selectedOptions[0]||{}).text||""].filter(Boolean).join(", "),
```
(g) La final, înlocuiește linia `incarca(); arata();` cu:
```javascript
incarcaLocalitati().then(()=>{ incarca(); populeazaLocalitati(); arata(); });
```

- [ ] **Step 4: Rulează testele**

Run: `python -m pytest tests/test_web_wizard.py -v`
Expected: PASS (toate, inclusiv noul test). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/web/templates/wizard.html evaluare-anevar/tests/test_web_wizard.py
git commit -m "feat: Pas 1 wizard cu dropdown judet+localitate (slug exact) + rest adresa free-text"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 4 — Împachetare + verificare

### Task 4: Include `data/` în .exe + rebuild + smoke

**Files:**
- Modify: `evaluare-anevar.spec`

- [ ] **Step 1: Adaugă datele în spec**

În `evaluare-anevar.spec`, în lista `datas`, adaugă o intrare pentru folderul de date (lângă
`("src/evaluare/web/templates", "evaluare/web/templates")`):
```python
    ("src/evaluare/data", "evaluare/data"),
```

- [ ] **Step 2: Suită completă**

Run: `python -m pytest -q`
Expected: toate verzi.

- [ ] **Step 3: Rebuild + smoke**

Run (din `evaluare-anevar/`; oprește orice proces care blochează exe-ul):
```bash
python -m PyInstaller --noconfirm --clean evaluare-anevar.spec
```
Apoi pornește exe-ul și verifică endpoint-ul:
```bash
cd dist && ./evaluare-anevar.exe &
sleep 12
python -c "import urllib.request,json; d=json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/localitati').read()); print('judete:', len(d['judete']), '| otopeni:', any(l['slug']=='otopeni' for l in d['localitati']['ilfov']))"
taskkill //F //IM evaluare-anevar.exe
```
Expected: `judete: 42 | otopeni: True`.

- [ ] **Step 4: Commit final**
```bash
git add evaluare-anevar/evaluare-anevar.spec
git commit -m "build: include data/ (liste localitati) in executabil"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Recapitulare acoperire spec

| Cerință spec | Task |
|---|---|
| Slug normalizare compatibil portaluri | Task 1 (slugify) |
| Dataset complet (toate localitățile) din sursă publică, build o dată | Task 1 (script + JSON) |
| Endpoint pentru liste | Task 2 |
| Dropdown județ + localitate cascadat + override + rest free-text | Task 3 |
| Slug-uri directe în descoperire (fără LLM) | Task 3 (e, f) |
| Inclus în .exe | Task 4 |
