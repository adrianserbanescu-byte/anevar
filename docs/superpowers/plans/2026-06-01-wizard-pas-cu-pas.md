# Wizard pas-cu-pas (pornind de la o adresă) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Un flux ghidat în 5 pași, pornind de la o adresă tastată o singură dată, care reutilizează endpoint-urile existente. Adaugă un singur endpoint nou (`POST /api/zona`) și o pagină wizard cu starea în browser (`localStorage`).

**Architecture:** `evaluare/zona.py` (extrage județ+localitate din adresă cu LLM injectabil, fallback fără cheie) → endpoint `POST /api/zona`. Pagina `wizard.html` + ruta `GET /wizard` orchestrează în JS cei 5 pași, asamblează `EvaluationInput` și apelează endpoint-urile existente (`/api/zona`, `/api/descopera`, `/api/import-url`, `/api/evaluare`, download). Formularul monolit `/` rămâne neatins.

**Tech Stack:** Python 3.11+, FastAPI/Jinja2, pytest. Fără dependențe noi.

**Spec sursă:** `docs/superpowers/specs/2026-06-01-wizard-pas-cu-pas-design.md`.
**Depinde de:** toate planurile anterioare (motor, raport, web, descoperire). Branch: `feature/nucleu-calcul`.
**Reutilizat:** `NarrativeClient` (protocol `.complete(system, user) -> str`); `create_app(storage, client, fetcher)`.

---

## Structura de fișiere

```
evaluare-anevar/
├── src/evaluare/
│   ├── zona.py                     # NOU: extrage judet+localitate din adresa
│   └── web/
│       ├── app.py                  # MODIFICAT: POST /api/zona + GET /wizard
│       └── templates/
│           └── wizard.html         # NOU: 5 pasi, stare in browser + localStorage
└── tests/
    ├── test_zona.py                # NOU
    └── test_web_wizard.py          # NOU (TestClient)
```

---

## Phase 1 — Derivarea zonei din adresă

### Task 1: `evaluare/zona.py`

**Files:**
- Create: `src/evaluare/zona.py`
- Test: `tests/test_zona.py`

**Context de design:** `extrage_zona(adresa, client)` cere LLM-ului `{judet, localitate}` (normalizate
lowercase, fără diacritice), ancorat în adresa dată. Fără client → fallback: ultimele 2 segmente
despărțite de virgulă. Niciodată blocant (evaluatorul confirmă oricum).

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_zona.py`:
```python
from evaluare.zona import extrage_zona


class FakeClient:
    def __init__(self, raspuns):
        self.raspuns = raspuns
    def complete(self, system, user):
        return self.raspuns


def test_extrage_zona_cu_llm():
    client = FakeClient('{"judet": "ilfov", "localitate": "otopeni"}')
    judet, localitate = extrage_zona("Str. Exemplu nr. 10, Otopeni, Ilfov", client=client)
    assert judet == "ilfov"
    assert localitate == "otopeni"


def test_extrage_zona_fallback_fara_client():
    judet, localitate = extrage_zona("Str. Exemplu 10, Otopeni, Ilfov", client=None)
    # ultimele 2 segmente, normalizate lowercase
    assert judet == "ilfov"
    assert localitate == "otopeni"


def test_extrage_zona_fallback_o_singura_parte():
    judet, localitate = extrage_zona("Otopeni", client=None)
    assert localitate == "otopeni"
    assert judet is None


def test_extrage_zona_llm_json_invalid_degradeaza():
    client = FakeClient("nu e json")
    judet, localitate = extrage_zona("Str X, Otopeni, Ilfov", client=client)
    # cade pe fallback, nu arunca exceptie
    assert localitate == "otopeni"
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_zona.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.zona'`.

- [ ] **Step 3: Implementează `zona.py`**

`src/evaluare/zona.py`:
```python
"""Derivarea judet+localitate dintr-o adresa libera (LLM injectabil, fallback)."""
from __future__ import annotations

import json
import re
import unicodedata
from typing import Optional

from evaluare.ai.narrative import NarrativeClient

SYSTEM_ZONA = (
    "Extragi judetul si localitatea dintr-o adresa din Romania. Raspunzi EXCLUSIV cu JSON "
    "valid: {\"judet\": \"...\", \"localitate\": \"...\"}, cu valori lowercase fara diacritice. "
    "Daca nu poti determina un camp, pune null. Nu inventezi."
)


def _normalizeaza(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.strip().lower() or None


def _fallback(adresa: str) -> tuple[Optional[str], Optional[str]]:
    parti = [p.strip() for p in adresa.split(",") if p.strip()]
    if len(parti) >= 2:
        return _normalizeaza(parti[-1]), _normalizeaza(parti[-2])
    if len(parti) == 1:
        return None, _normalizeaza(parti[0])
    return None, None


def extrage_zona(
    adresa: str, client: Optional[NarrativeClient]
) -> tuple[Optional[str], Optional[str]]:
    """Intoarce (judet, localitate) din adresa. LLM daca exista client, altfel fallback."""
    if client is not None:
        try:
            raw = client.complete(SYSTEM_ZONA, f"Adresa: {adresa}")
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(m.group(0) if m else raw)
            judet = _normalizeaza(data.get("judet"))
            localitate = _normalizeaza(data.get("localitate"))
            if localitate or judet:
                return judet, localitate
        except (ValueError, TypeError, AttributeError):
            pass
    return _fallback(adresa)
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_zona.py -v`
Expected: PASS (4 teste).

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/zona.py evaluare-anevar/tests/test_zona.py
git commit -m "feat: extragere judet+localitate din adresa (LLM injectabil + fallback)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

### Task 2: endpoint `POST /api/zona`

**Files:**
- Modify: `src/evaluare/web/app.py`
- Test: `tests/test_web_zona.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_web_zona.py`:
```python
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_post_zona_fallback(tmp_path):
    client = _client(tmp_path)
    resp = client.post("/api/zona", json={"adresa": "Str. X 10, Otopeni, Ilfov"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["judet"] == "ilfov"
    assert data["localitate"] == "otopeni"
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_zona.py -v`
Expected: FAIL (endpoint inexistent).

- [ ] **Step 3: Adaugă endpoint-ul în `app.py`**

În `src/evaluare/web/app.py`, adaugă importul (lângă celelalte):
```python
from evaluare.zona import extrage_zona
```
Adaugă modelul de cerere (lângă `ImportUrlRequest`):
```python
class ZonaRequest(BaseModel):
    adresa: str
```
Adaugă ruta în `create_app`, înainte de `return app`:
```python
    @app.post("/api/zona")
    def deriva_zona(req: ZonaRequest) -> dict:
        judet, localitate = extrage_zona(req.adresa, client=client)
        return {"judet": judet, "localitate": localitate}
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_zona.py -v`
Expected: PASS (1 test). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/tests/test_web_zona.py
git commit -m "feat: endpoint POST /api/zona (adresa -> judet+localitate)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Pagina wizard

### Task 3: `wizard.html` + ruta `GET /wizard`

**Files:**
- Modify: `src/evaluare/web/app.py`
- Create: `src/evaluare/web/templates/wizard.html`
- Test: `tests/test_web_wizard.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_web_wizard.py`:
```python
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_wizard_page_loads_with_5_steps(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/wizard")
    assert resp.status_code == 200
    body = resp.text
    for i in range(1, 6):
        assert f'id="pas-{i}"' in body
    # referinta catre endpoint-urile reutilizate
    assert "/api/zona" in body
    assert "/api/descopera" in body
    assert "/api/evaluare" in body
    assert "localStorage" in body
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_wizard.py -v`
Expected: FAIL (ruta inexistentă → 404).

- [ ] **Step 3a: Adaugă ruta în `app.py`**

În `src/evaluare/web/app.py`, în `create_app`, înainte de `return app`:
```python
    @app.get("/wizard", response_class=HTMLResponse)
    def pagina_wizard(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "wizard.html", {})
```

- [ ] **Step 3b: Creează `wizard.html`**

`src/evaluare/web/templates/wizard.html`:
```html
<!DOCTYPE html>
<html lang="ro">
<head><meta charset="utf-8"><title>Evaluare — wizard</title>
<style>
 body{font-family:Arial,sans-serif;max-width:900px;margin:20px auto;line-height:1.5}
 .pas{display:none;border:1px solid #ddd;padding:16px;margin-top:10px}
 .pas.activ{display:block}
 .bara{background:#eee;height:8px;border-radius:4px;margin:8px 0}
 .bara>div{background:#2a7;height:8px;border-radius:4px;transition:width .2s}
 label{font-weight:bold;display:block;margin-top:6px}
 .hint{color:#666;font-size:.85em}
 input,select,textarea{font-size:1em}
 .candidat{border:1px solid #eee;padding:8px;margin:6px 0}
 button{margin-top:10px}
</style></head>
<body>
<h1>Evaluare imobiliară — pas cu pas</h1>
<div class="bara"><div id="progres" style="width:20%"></div></div>
<p id="eticheta-pas"></p>

<!-- PAS 1 -->
<section id="pas-1" class="pas activ">
  <h2>Pas 1 — Adresă & lucrare</h2>
  <label>Adresa proprietății</label>
  <input id="adresa" size="60" placeholder="Str. ..., Localitate, Județ">
  <small class="hint">Tastată o dată: alimentează raportul și zona de căutare a comparabilelor.</small>
  <label>Nume client</label><input id="client_nume">
  <label>Nr. cadastral</label><input id="numar_cadastral">
  <label>Carte funciară</label><input id="carte_funciara">
  <label>Evaluator</label><input id="evaluator_nume">
  <label>Legitimație</label><input id="evaluator_legitimatie">
  <label>Data evaluării</label><input id="data_evaluarii" value="2026-01-16">
  <label>Data raportului</label><input id="data_raportului" value="2026-01-16">
  <p>Județ/localitate (derivate din adresă, confirmă):
     Județ <input id="judet" size="12"> Localitate <input id="localitate" size="14">
     <span id="zona_status" class="hint"></span></p>
</section>

<!-- PAS 2 -->
<section id="pas-2" class="pas">
  <h2>Pas 2 — Proprietatea subiect</h2>
  <label>Suprafață teren (mp)</label><input id="suprafata_teren" value="500">
  <label>Au (mp)</label><input id="au" value="100">
  <label>Acd (mp)</label><input id="acd" value="120">
  <label>An referință</label><input id="an_referinta" value="2025">
  <label>Valoare teren (lei)</label><input id="valoare_teren" value="100000">
  <label>Elemente de cost (element;cod;um;cantitate;cost_unitar;an_pif)</label>
  <textarea id="elemente" rows="3" cols="80">Structura;X;mp;120;2000;2015</textarea>
  <label>Depreciere fizică (varsta;fractie)</label>
  <textarea id="depreciere" rows="2" cols="30">5;0.05
15;0.15</textarea>
  <h3>Atribute pentru potrivire (descoperire)</h3>
  An <input id="attr_an" value="2013" size="5">
  Stare(1-5) <input id="attr_stare" value="3" size="3">
  Finisaj(1-4) <input id="attr_finisaj" value="4" size="3">
  Încălzire <input id="attr_incalzire" value="centrala_gaz" size="14">
</section>

<!-- PAS 3 -->
<section id="pas-3" class="pas">
  <h2>Pas 3 — Comparabile</h2>
  <button type="button" id="btn-descopera">Descoperă comparabile în zonă</button>
  <span id="desc_status" class="hint"></span>
  <div id="candidati"></div>
  <label>Comparabile selectate (pret;suprafata, editabile)</label>
  <textarea id="comparabile" rows="4" cols="30"></textarea>
</section>

<!-- PAS 4 -->
<section id="pas-4" class="pas">
  <h2>Pas 4 — Metodă & calcul</h2>
  <select id="metoda">
    <option value="cost">Cost (CIN + teren)</option>
    <option value="piata">Piață (comparație)</option>
    <option value="ponderata">Ponderată</option>
  </select>
  <button type="button" id="btn-calc">Calculează</button>
  <div id="rezultat-calc"></div>
</section>

<!-- PAS 5 -->
<section id="pas-5" class="pas">
  <h2>Pas 5 — Raport</h2>
  <div id="link-raport"></div>
</section>

<div>
  <button type="button" id="inapoi">◀ Înapoi</button>
  <button type="button" id="inainte">Înainte ▶</button>
  <button type="button" id="reset">Reset dosar</button>
</div>

<script>
const PASI = 5; let pas = 1; let evaluareId = null;
const $ = id => document.getElementById(id);
const CAMPURI = ["adresa","client_nume","numar_cadastral","carte_funciara","evaluator_nume",
 "evaluator_legitimatie","data_evaluarii","data_raportului","judet","localitate",
 "suprafata_teren","au","acd","an_referinta","valoare_teren","elemente","depreciere",
 "attr_an","attr_stare","attr_finisaj","attr_incalzire","comparabile","metoda"];

function salveaza(){ const s={}; CAMPURI.forEach(c=>{if($(c))s[c]=$(c).value});
  localStorage.setItem("wizard", JSON.stringify(s)); }
function incarca(){ try{ const s=JSON.parse(localStorage.getItem("wizard")||"{}");
  CAMPURI.forEach(c=>{if($(c)&&s[c]!=null)$(c).value=s[c]}); }catch(e){} }
function arata(){ for(let i=1;i<=PASI;i++) $("pas-"+i).classList.toggle("activ", i===pas);
  $("progres").style.width=(pas*100/PASI)+"%"; $("eticheta-pas").textContent="Pas "+pas+" / "+PASI;
  $("inapoi").disabled=(pas===1); }

$("inainte").addEventListener("click", async ()=>{
  if(pas===1){ await deriveZona(); }
  if(pas<PASI){ pas++; salveaza(); arata(); }
});
$("inapoi").addEventListener("click", ()=>{ if(pas>1){pas--; arata();} });
$("reset").addEventListener("click", ()=>{ localStorage.removeItem("wizard"); location.reload(); });

async function deriveZona(){
  if($("judet").value && $("localitate").value) return;
  $("zona_status").textContent="Derivez zona...";
  try{ const r=await fetch("/api/zona",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({adresa:$("adresa").value})}); const z=await r.json();
    if(z.judet) $("judet").value=z.judet; if(z.localitate) $("localitate").value=z.localitate;
    $("zona_status").textContent="(confirmă)"; }
  catch(e){ $("zona_status").textContent="introdu manual"; }
}

$("btn-descopera").addEventListener("click", async ()=>{
  $("desc_status").textContent="Caut...";
  const payload={portal:"imobiliare", judet:$("judet").value, localitate:$("localitate").value,
    subiect:{an:parseInt($("attr_an").value)||null, stare:parseInt($("attr_stare").value)||null,
      finisaj:parseInt($("attr_finisaj").value)||null, incalzire:$("attr_incalzire").value||null,
      teren:$("suprafata_teren").value||null}, atribute_secundare:[], max_candidati:8};
  try{ const r=await fetch("/api/descopera",{method:"POST",
      headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
    const res=await r.json(); $("desc_status").textContent=res.candidati.length+" candidați";
    $("candidati").innerHTML=res.candidati.map((c,i)=>
      `<div class="candidat"><label><input type="checkbox" class="bif" data-pret="${c.pret||''}"
       data-supr="${c.suprafata||''}"> <b>${c.relevanta}%</b> — ${c.pret||'?'} / ${c.suprafata||'?'} mp
       <a href="${c.url}" target="_blank">link</a></label>
       <div class="hint">${c.explicatie}</div></div>`).join("");
    document.querySelectorAll(".bif").forEach(b=>b.addEventListener("change",aduna)); }
  catch(e){ $("desc_status").textContent="eroare căutare"; }
});
function aduna(){ const linii=[...document.querySelectorAll(".bif:checked")]
  .map(b=>b.dataset.pret+";"+b.dataset.supr); $("comparabile").value=linii.join("\n"); }

function asambleaza(){
  const elements=$("elemente").value.trim().split("\n").filter(Boolean).map(l=>{
    const[element,cod,um,cantitate,cost_unitar,an_pif]=l.split(";");
    return{element,cod,um,cantitate,cost_unitar,an_pif:parseInt(an_pif)};});
  const dp=$("depreciere").value.trim().split("\n").filter(Boolean).map(l=>{
    const[varsta,depreciere]=l.split(";"); return{varsta:parseInt(varsta),depreciere};});
  const comparables=$("comparabile").value.trim().split("\n").filter(Boolean).map(l=>{
    const[pret,suprafata]=l.split(";"); return{pret,suprafata};});
  return{meta:{client_nume:$("client_nume").value,adresa:$("adresa").value,
      numar_cadastral:$("numar_cadastral").value,carte_funciara:$("carte_funciara").value,
      evaluator_nume:$("evaluator_nume").value,evaluator_legitimatie:$("evaluator_legitimatie").value,
      data_evaluarii:$("data_evaluarii").value,data_raportului:$("data_raportului").value},
    land:{suprafata:$("suprafata_teren").value},
    building:{au:$("au").value,acd:$("acd").value,an_referinta:parseInt($("an_referinta").value),
      elements,depreciation_points:dp}, comparables,
    valoare_teren:$("valoare_teren").value, metoda:$("metoda").value};
}

$("btn-calc").addEventListener("click", async ()=>{
  $("rezultat-calc").textContent="Calculez...";
  try{ const r=await fetch("/api/evaluare",{method:"POST",
      headers:{"Content-Type":"application/json"}, body:JSON.stringify(asambleaza())});
    const res=await r.json(); evaluareId=res.id;
    $("rezultat-calc").innerHTML=`<p><b>Valoare: ${res.valoare_finala} LEI</b> (${res.metoda})</p>`;
    $("link-raport").innerHTML=`<a href="/api/evaluare/${res.id}/raport.docx">Descarcă raport.docx</a>`;
  }catch(e){ $("rezultat-calc").textContent="eroare calcul"; }
});

incarca(); arata();
</script>
</body></html>
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_wizard.py -v`
Expected: PASS (1 test). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/src/evaluare/web/templates/wizard.html evaluare-anevar/tests/test_web_wizard.py
git commit -m "feat: pagina wizard 5 pasi (stare in browser + localStorage)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — Verificare finală

### Task 4: Suită completă + rebuild .exe + smoke

- [ ] **Step 1: Rulează toată suita**

Run: `python -m pytest -q`
Expected: toate testele trec.

- [ ] **Step 2: Smoke — pagina wizard pornește din server real**

Run (din `evaluare-anevar/`):
```bash
PYTHONPATH=src python -c "
import threading, time, urllib.request, uvicorn
from evaluare.db.storage import Storage
from evaluare.web.app import create_app
s=Storage('date/smoke.db'); s.init()
app=create_app(storage=s, client=None)
cfg=uvicorn.Config(app, host='127.0.0.1', port=8015, log_level='error')
srv=uvicorn.Server(cfg); threading.Thread(target=srv.run, daemon=True).start()
time.sleep(2)
b=urllib.request.urlopen('http://127.0.0.1:8015/wizard').read().decode()
print('wizard:', 'id=\"pas-1\"' in b, 'localStorage:', 'localStorage' in b)
srv.should_exit=True
"
```
Expected: `wizard: True localStorage: True`.

- [ ] **Step 3: Reconstruiește executabilul**

Run (din `evaluare-anevar/`, asigură-te că niciun proces nu blochează exe-ul):
```bash
python -m PyInstaller --noconfirm --clean evaluare-anevar.spec
```
Expected: `dist/evaluare-anevar.exe` reconstruit.

- [ ] **Step 4: Commit final (dacă a rămas ceva)**
```bash
git status
git add -A && git commit -m "chore: verificare wizard + rebuild exe" || echo "nimic de comis"
```

---

## Recapitulare acoperire spec

| Cerință spec | Task |
|---|---|
| Derivare județ+localitate din adresă (LLM + fallback) | Task 1 |
| Endpoint `POST /api/zona` | Task 2 |
| Wizard 5 pași, stare în browser + `localStorage` | Task 3 |
| Adresă → zonă (Pas 1) + descoperire automată (Pas 3) | Task 3 (JS) |
| Asamblare `EvaluationInput` → `/api/evaluare` + download | Task 3 (JS) |
| Reutilizare endpoint-uri existente, monolitul `/` neatins | Task 2, 3 |

**Notă:** orchestrarea JS (localStorage, apeluri între pași) nu e testată unitar (logică de browser);
testele verifică încărcarea paginii, structura celor 5 pași și endpoint-ul `/api/zona`. Verificarea
funcțională completă se face manual rulând `python -m evaluare` și parcurgând wizard-ul.
