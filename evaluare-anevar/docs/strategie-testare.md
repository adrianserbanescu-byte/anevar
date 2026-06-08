# Strategie de testare — Evaluare ANEVAR

Document viu. Se actualizează la fiecare dezvoltare nouă (vezi §8 „Mentenanță").
Ultima actualizare: 2026-06-08 (paralelizare suită `-n auto` + §10 optimizarea execuției).

> **Proprietate (Rol owner testare = sesiunea D):** framework-ul de testare, strategia,
> optimizarea execuției (viteză suită, e2e harness, coverage-gates) și actualizarea acestui
> document. **Excepție:** testele per-feature scrise de fiecare sesiune pentru codul ei rămân
> ale autorului — owner-ul deține structura din jur, nu conținutul lor de business.

## 0. Principii

1. **Piramida**: multe teste unitare (rapide, pe motor/parsere), câteva de integrare (HTTP),
   puține end-to-end (Playwright pe browser). Confidență mare la cost de mentenanță mic.
2. **Acoperă ce contează**: căile critice de business (calculul valorii, grilele de ajustare,
   parserele de anunțuri, cablarea profilului), tratarea erorilor, limitele de securitate
   (anonimizare GDPR, disclaimere AML), integritatea datelor (persistență + migrare).
3. **Determinism**: zero rețea în teste. Tot ce iese în internet (portaluri, BNR, ANEVAR, AI)
   se injectează prin `fetcher`/`client` sau se face monkeypatch.
4. **Guard, nu doar happy-path**: fiecare modul are cel puțin un test de eroare/limită.
5. **Prag de acoperire**: minim **90%** global (gate în CI). Scădere = test lipsă, nu „normal".

## 1. Hartă: ce testăm, cu ce tip, unde

| Strat | Module | Tip test | Fișiere |
|------|--------|----------|---------|
| **Calculator (motor)** | `engine/` (cost, market, land, chirie, venit, dcf, reconciliation, validation, abordari) | unitar, numeric exact (Decimal) | `test_engine_*`, `test_cost`, `test_market`, … |
| **Parsere / import** | `importers/url_parser`, `discovery/*`, `ingestie/*` | unitar pe fixturi HTML/PDF | `test_url_parser*`, `test_discovery*`, `test_ingestie` |
| **Asamblare / profil** | `assembler`, `profil`, `models/*` | unitar (input→context) | `test_assembler*`, `test_report_context` |
| **Raport** | `report/generator`, `report/anonymizer`, `report/sectiuni` | unitar (.docx generat, conținut) | `test_report_*`, `test_generator*` |
| **AML** | `aml/risc`, `indicatori`, `raportare`, `documente`, `store` | unitar | `test_aml_*`, `test_web_aml` |
| **Persistență** | `db/storage` (migrare, backup, coadă import) | unitar | `test_storage` |
| **API (HTTP)** | `web/routers/*` | integrare (TestClient) | `test_web_*` |
| **UI nou „curent"** | `cont`, `dosare_fs`, `master_config`, `routers/curent`, import `.docx` | unitar + integrare | `test_dosare_fs`, `test_master_config`, `test_web_curent`, `test_importers_docx_dosar` |
| **UI / fluxuri** | șabloane Jinja + JS | end-to-end (Playwright) | `scripts/_pw_smoke.py` |
| **Conectivitate** | frontend↔backend (fetch↔rute), localStorage, import→câmpuri | static (grep) + e2e | review §6 + Playwright |

## 2. Calculator (motorul de evaluare) — prioritate maximă

**Ce**: corectitudinea numerică a fiecărei abordări + reconcilierea.
**Cum**: teste unitare cu `Decimal`, valori cunoscute, toleranță zero.

Cazuri obligatorii per abordare:
- **Cost** (`engine/cost`): CIB = Σ(cantitate×cost_unitar); depreciere fizică interpolată pe
  vârstă; CIN = CIB − depreciere; valoare = CIN + teren. Edge: 0 elemente, vârstă peste ultimul punct.
- **Piață** (`engine/market`): ajustare pe suprafață (Au), alegerea comparabilei cu ajustarea
  brută minimă. Edge: 1 comparabil, comparabile identice, outlier.
- **Teren** (`engine/land`): preț/mp corectat × suprafață. Edge: o singură comparabilă.
- **Chirii→venit** (`engine/chirie` + `venit`): chirie/mp × supr × 12 = VBP; NOI = VBP×(1−neocupare)−chelt;
  valoare = NOI ÷ rată cap. Edge: neocupare 0/1, rată cap mică.
- **DCF**: Σ flux/(1+r)^t + rezidual/(1+r)^n.
- **Reconciliere** (`engine/reconciliation`): primară explicită; ponderată; alocare teren/construcție.
  Edge: o singură abordare, ponderi extreme.
- **Validare** (`engine/validation`): Au≤Acd, min 3 comparabile, limită ajustare, outlier.

**Țintă acoperire motor: 100%** (e inima aplicației).

## 3. Parsere / import — robustețe pe date reale

**Ce**: extragerea preț/suprafață/atribute din anunțuri (storia/imobiliare/olx) și documente (CF/releveu/plan/CPE).
**Cum**: fixturi reale în `tests/fixtures/` (HTML) — fără rețea.

Cazuri:
- JSON-LD (schema.org) recursiv; `__NEXT_DATA__` (storia: area vs terrain_area); og:meta + regex fallback.
- Degradare grațioasă: pagină fără date → câmpuri None, fără excepție.
- Caracteristici: an, încălzire, material, tip clădire, nr. camere, etaje.
- **Gardă pagină-listă** (audit 2026-06-06): un URL trunchiat/expirat → pagină de listă/căutare;
  parserul **NU** trebuie să extragă tăcut prețul unui anunț promovat. `pagina_lista=True` →
  `to_comparable` și `/api/import-url` refuză; discovery sare peste. (`test_url_parser`:
  `test_pagina_de_lista_*`, `test_anunt_real_nu_e_marcat_ca_lista`.)
- **Teren ≠ casă**: „N mp teren" în titlu se atribuie terenului, nu suprafeței casei
  (`test_mp_teren_in_titlu_nu_e_confundat_*`).
- Ingestie PDF: cf→cadastral/CF/teren/proprietar; releveu→Au/Acd; plan→teren; OCR fallback.
- **Import dosar din `.docx`** (`docx_dosar`): nume fișier = identitate (id/nume/tip/localitate→județ);
  text = beneficiar/scop/dată; robust la docx ilizibil (rămâne pe filename).

**Regulă**: orice portal/format nou adăugat ⇒ **fixtură + test** în aceeași dezvoltare.
**Audit live periodic**: înainte de release, rulează parserul pe 3 anunțuri reale/portal
(imobiliare/storia/olx) și compară cu titlul paginii (ground truth). Portalurile schimbă HTML-ul.

## 4. Asamblare + profil — cablarea metodologiei

**Ce**: input web → `EvaluationInput` → `construieste_context` → profil + rezultate.
Cazuri (recent adăugate):
- `tip_proprietate` → profil (casa/apartament/industrial/agricol/special) + ghid GEV.
- `scop` → profil (raportare→justă/GEV500, asigurare, impozitare, litigii); garantare→tipul decide.
- Combinație: scop special păstrează tipul de activ ales.
- Agricol: fără elemente de cost (doar comparație).
- Profilul afectează **framing-ul raportului, nu formula** (test: aceeași valoare pe metodă fixă).

## 5. API (HTTP) — integrare cu TestClient

Fiecare endpoint: happy-path + cel puțin o eroare. Rețeaua se injectează (`fetcher`) sau monkeypatch.
- `/api/evaluare` (POST): calcul + alerte; 404 la dosar inexistent; raport.docx; audit.txt.
- `/api/grila-{teren,casa,chirii}`: calcul corect; 422 la date invalide.
- `/api/import-url`, `/api/import-anunt`: parsare; coadă; dedup; ștergere (totală + individuală).
- `/api/descopera(-teren)`: candidați + metodologie (fetcher fixtură).
- `/api/curs-bnr`, `/api/indice-anevar`: 200/404/502 (monkeypatch sursa).
- `/api/ingestie`: 400 tip necunoscut / base64 invalid; 200 extragere.
- `/api/zona`, `/api/localitati`, `/api/status`: structură răspuns.
- AML: `/api/aml/evalueaza` + documentele .docx; GDPR .docx.
- **UI nou „curent"**: `/api/cont` (422 fără nume/legitimație), `/api/dosar` (403 fără cont),
  `/dosar/{uid}` (404 inexistent), `/api/dosar/{uid}/salveaza`, `/raport.docx` (versiune în folder),
  `/api/dosar/import-docx` (200 pre-completat / 400 conținut invalid / 403 fără cont). (`test_web_curent`.)

## 6. Conectivitate frontend↔backend (review + e2e)

**Static** (rulabil ca grep, vezi §8): fiecare `fetch()` din șabloane are rută de backend;
fiecare cheie localStorage are ambele capete (scriere+citire).
**Dinamic** (Playwright, `scripts/_pw_smoke.py`): 30 verificări —
- încărcare pagini fără erori de consolă;
- wizard: dropdown județ, recap live, comutare tip Pas 2 (grupuri show/hide), calcul;
- grilă: comutare tab-uri (+ tastatură săgeți);
- descoperire: empty state; import-anunț → coadă → panou → grilă;
- fluxuri localStorage (prefill grilă, VBP grilă→wizard);
- AML: banner legal.

## 7. Cum rulezi

```bash
# Unit + integrare (serial — pentru debugging clar, -x, pdb):
python -m pytest -q
# PARALEL (toata suita, ~2x mai rapid: ~131s -> ~61s pe 8 nuclee) — recomandat local + CI:
python -m pytest -n auto -q
# Cu acoperire + linii lipsă (paralel; pytest-cov combina worker-ii):
python -m pytest -n auto --cov=evaluare --cov-report=term-missing
# Lint:
python -m ruff check src/ tests/
# End-to-end Playwright (manual, cere chromium + server pe 8765):
PYTHONPATH=src python scripts/_serve_test.py &   # terminal 1
PYTHONIOENCODING=utf-8 PYTHONPATH=src python scripts/_pw_smoke.py   # terminal 2
```

CI (`.github/workflows`): rulează pytest + ruff la fiecare push. E2E Playwright e manual
(necesită browser) — de rulat înainte de fiecare release de `.exe`.

## 8. Mentenanță — upgrade la dezvoltări noi

La **orice** dezvoltare nouă, în aceeași tură:
1. **Endpoint nou** → test HTTP (happy + o eroare) în `test_web_*`.
2. **Portal/format nou** → fixtură în `tests/fixtures/` + test parser.
3. **Câmp/profil/abordare nou** → test unitar + actualizează §2-4 din acest document.
4. **Flux UI nou** → adaugă o verificare în `scripts/_pw_smoke.py`.
5. **Buton/import nou** → confirmă în review-ul de conectivitate (§6) că duce datele în câmpul corect.
6. Rulează `pytest --cov`; dacă acoperirea scade sub 90%, adaugă testul lipsă (gate CI).

Comanda de verificare a conectivității (orfani frontend→backend):
```bash
cd src/evaluare/web/templates
diff <(grep -rhoE "fetch\(['\"\`][^'\"\`]+" *.html | sed -E "s/fetch\(['\"\`]//" | sort -u) \
     <(cd ../routers && grep -rhoE '@router\.(get|post)\("[^\"]+' *.py | sed -E 's/.*\("//' | sort -u)
```

## 9. Goluri cunoscute (de redus în timp)

| Modul | Acoperire | De ce e greu | Plan |
|------|-----------|--------------|------|
| `ai/narrative` | ~82% | apeluri rețea AI | mock client pe căile de eroare |
| `curs_bnr`, `indice_anevar` | ~82-89% | rețea | testat la nivel HTTP cu monkeypatch |
| `ingestie/ocr` | ~76% | OCR pe PDF scanat | fixtură PDF mică + test fallback |
| `report/generator` | ~88% | multe ramuri de raport | teste pe secțiunile rare (lichidare, DCF) |

> Nu urmărim 100% global cu orice preț — urmărim 100% pe **motor** și pe **căile critice**,
> ≥90% în rest. Codul de rețea pură și framework-ul sunt excepții documentate.

## 10. Optimizarea execuției (framework — owner: sesiunea D)

**Țintă:** suită rapidă (sub ~3 min), determinism păstrat, coverage-gate intact. Bucla de
feedback scurtă = teste rulate des = regresii prinse devreme.

### 10.1 Paralelizare (`pytest-xdist`)
- `pytest -n auto` distribuie testele pe toate nucleele. Măsurat: **~131s → ~61s** (8 nuclee,
  579 teste) — ~2.1×. Testele sunt deja izolate (fiecare cu `tmp_path` / fixturi proprii,
  zero rețea), deci paralelizarea e sigură — **549+ → 579 passed identic pe `-n auto`**.
- **NU** punem `-n auto` în `addopts` implicit: rularea serială rămâne default-ul pentru
  debugging clar (`-x`, `pdb`, output ne-întrețesut). Paralel = explicit (CI + rulări full locale).
- CI (`.github/workflows/ci.yml`) rulează `pytest -n auto --cov` — `pytest-cov` combină automat
  acoperirea per-worker, deci gate-ul `fail_under=90` rămâne valid (verificat: 93.6% pe `-n auto`).

### 10.2 Coverage-gate
- Prag `fail_under = 90` în `[tool.coverage.report]` (pyproject). Scădere sub prag = CI roșu.
- `--cov-report=term-missing` arată liniile lipsă; `omit`-uri documentate: `__main__.py`, `vlm.py`.

### 10.3 Teste lente (candidați de izolat dacă suita crește)
Cele mai lente (din `--durations`): `test_docx_to_pdf_real_cu_libreoffice` (~4s, pornește
LibreOffice), `test_settings_with_key_builds_client` (~4s, import `anthropic`), setup-urile
`TestClient` din `test_web_curent` (~1s/test). Dacă devin un cost real, se pot marca pentru
rulare opțională (marker `slow`) **fără** a le modifica logica (sunt teste per-feature ale altor sesiuni).

### 10.4 e2e (Playwright)
`scripts/_pw_smoke.py` (30 verificări) rămâne manual (cere browser + server pe 8765); de rulat
înainte de fiecare release `.exe`. Vezi §6. Plan: harness reproductibil + integrare opțională în CI.

### 10.5 Procedură owner la re-sync cu master
La fiecare schimbare de framework: `test-optim` trage din `origin/master`, rulează `pytest -n auto`
(verde) + `lock.py --check` + `ruff`, actualizează acest document. NU se modifică testele de
business ale altor sesiuni; se optimizează doar structura/execuția din jur.
