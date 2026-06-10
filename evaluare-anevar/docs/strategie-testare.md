# Strategie de testare — Evaluare ANEVAR

Document viu. Se actualizează la fiecare dezvoltare nouă (vezi §8 „Mentenanță").
Ultima actualizare: 2026-06-09 (§11 securitate SEC-1/2/3 + PDF→DOCX + Imoradar P1.1 + igienă PII loguri).

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
| **Parsere / import** | `importers/url_parser`, `discovery/*` (storia/imobiliare/olx/**imoradar**), `ingestie/*` | unitar pe fixturi HTML/PDF | `test_url_parser*`, `test_discovery*` (+ `test_discovery_imoradar`), `test_ingestie` |
| **Securitate** | path-traversal (`dosare_fs`), CSRF (`web/app` middleware), XSS (escape scrape), PII loguri | unitar + e2e | `test_dosare_fs_security`, `test_csrf`, `test_documente` (escape); vezi **§11** |
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
# End-to-end Playwright — runner unic (auto-pornește serverul izolat pe :8765, rulează tot):
python scripts/_e2e.py             # pw_smoke + toate _check_*.py (6/6 OK ~67s pe baseline)
python scripts/_e2e.py xss grid    # doar potrivirile pe nume
python scripts/_e2e.py --list      # listează scripturile descoperite
# Prerechizite: `python -m playwright install chromium` (o dată).
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
| **SEC-2 XSS client-side** | — | escaparea (`escapeHtml`/`urlSafe`) e în JS pe conținut scrape-uit randat în `dosar.html`/`descoperire.html`; greu de testat unitar | verificare e2e (`_pw_smoke`); coordonare cu B (audit #7) dacă merită un test de randare |
| **PII loguri (aserțiune negativă)** | parțial | se loghează `creator_legitimatie` (ID prof.), NU numele — dar nu există încă un test care să afirme că **numele NU apare** în log | gap de propus implementatorilor (B/audit): un test negativ pe conținutul jurnalului |

> Nu urmărim 100% global cu orice preț — urmărim 100% pe **motor** și pe **căile critice**,
> ≥90% în rest. Codul de rețea pură și framework-ul sunt excepții documentate.

## 10. Optimizarea execuției (framework — owner: sesiunea D)

**Țintă:** suită rapidă (sub ~3 min), determinism păstrat, coverage-gate intact. Bucla de
feedback scurtă = teste rulate des = regresii prinse devreme.

### 10.1 Paralelizare (`pytest-xdist`)
- `pytest -n auto` distribuie testele pe toate nucleele. Măsurat: **~117s serial → ~60-82s paralel**
  (8 nuclee, **617 teste** la 2026-06-10) — ~2×. Testele sunt izolate (`tmp_path`/fixturi proprii,
  zero rețea), deci paralelizarea e sigură — **617 passed identic pe `-n auto`** (verificat
  post-rebase pe `672f5b1` disclaimer aplicație→evaluator; precedent: M2 media top-N de la B,
  fix critic rotunjire, audit #7 coverage).
- **NU** punem `-n auto` în `addopts` implicit: rularea serială rămâne default-ul pentru
  debugging clar (`-x`, `pdb`, output ne-întrețesut). Paralel = explicit (CI + rulări full locale).
- CI rulează **`pytest -n auto --dist loadscope --max-worker-restart=4 --cov`**, precedat de
  `python -m compileall -q src tests`. `pytest-cov` combină acoperirea per-worker → gate
  `fail_under=90` valid (93.6%).

> **⚠️ Flakiness xdist sub LOAD (2026-06-09):** pe o mașină **supraîncărcată** (mai multe sesiuni
> rulând simultan), `-n auto` poate pica TRANZITORIU la colectare (`ImportError` pe module, ex.
> `test_zona`) — workeri care mor sub presiune CPU/RAM. **Nu e bug de cod** (serial e mereu verde).
> Mitigări aplicate în CI: `compileall` (elimină race-ul `.pyc` între workeri), `--max-worker-restart=4`
> (repornește workerii morți în loc să pice run-ul), `--dist loadscope` (mai puțin re-setup).
> **Pe CI dedicat (GitHub, 2-4 nuclee, low-load) e robust.** **Local, sub load greu (sesiuni paralele):
> folosește `pytest` serial sau `pytest -n 2`** — serialul rămâne gate-ul determinist de referință.

### 10.2 Coverage-gate
- Prag `fail_under = 90` în `[tool.coverage.report]` (pyproject). Scădere sub prag = CI roșu.
- `--cov-report=term-missing` arată liniile lipsă; `omit`-uri documentate: `__main__.py`, `vlm.py`.

### 10.3 Teste lente (candidați de izolat dacă suita crește)
Cele mai lente (din `--durations`): `test_docx_to_pdf_real_cu_libreoffice` (~4s, pornește
LibreOffice), `test_settings_with_key_builds_client` (~4s, import `anthropic`), setup-urile
`TestClient` din `test_web_curent` (~1s/test). Dacă devin un cost real, se pot marca pentru
rulare opțională (marker `slow`) **fără** a le modifica logica (sunt teste per-feature ale altor sesiuni).

### 10.4 e2e (Playwright) — harness consolidat
Înainte: rulare manuală a 6 scripturi independente (`_pw_smoke.py` + 5 × `_check_*.py`), fiecare
cu propriul boilerplate, plus server pornit separat (`_serve_test.py`) într-un alt terminal.

Acum: **runner unic** `scripts/_e2e.py` (owner: D, Rol 2):
- pornește serverul izolat (`_serve_test.py`, port 8765, DB+date temporare în `%TEMP%`, fără AI);
- rulează toate scripturile descoperite (`_pw_smoke.py` + `_check_*.py`) ca subprocese;
- agregează rezultatele (OK/FAIL per script, durată, ultimele linii la fail);
- oprește serverul la final;
- exit code = numărul de scripturi eșuate (0 = toate verzi → integrabil în CI/release).

Comenzi:
```bash
python scripts/_e2e.py                 # toată suita e2e (boot server, run, stop server)
python scripts/_e2e.py xss grid        # doar scripturile al căror nume conține „xss" sau „grid"
python scripts/_e2e.py --no-server URL # rulează contra unui server existent (ex. http://127.0.0.1:8000)
python scripts/_e2e.py --fail-fast     # oprește la primul fail (util pentru iterare locală)
python scripts/_e2e.py --quiet         # output minimal (o linie sumar — pentru scripturi de gate)
python scripts/_e2e.py --json          # raport JSON pe stdout (consum machine; pentru CI viitor)
python scripts/_e2e.py --list          # listează scripturile descoperite
```
Baseline (2026-06-09): **8/8 OK în ~114s** (boot server + Chromium incluse; `_pw_smoke.py` domină
~26s; auto-descoperă scripturile noi — `_check_descoperire_tip` + `_check_dosar_beneficiar` apărute
între timp s-au integrat fără modificări la runner, validând designul glob). Rulează LOCAL (nu în CI):
cere `chromium` instalat (`python -m playwright install chromium`), prea greu pentru CI-ul curent.
**A rula înainte de fiecare release `.exe`** — vezi checklist-ul complet de release în
[`docs/build.md` §3](build.md#3-release-checklist-înainte-de-a-publica-un-exe-ca-artefact)
(gate-ul leagă pytest + e2e + build canonic + smoke).

> **Decizie luată: NU paralelizăm scripturile e2e între ele.** Toate fac `POST /api/cont` +
> `POST /api/dosar` pe ACELAȘI server izolat — paralelizarea naivă ar produce race-uri pe starea
> partajată (overwrite cont, conflicte UID, dosare amestecate). Un server-per-script ar costa
> 6× boot. Verdictul: serialul cu izolare prin server e cel mai bun raport risc/câștig.

> NU am atins logica scripturilor individuale (sunt teste per-feature, rămân ale autorilor); doar
> le-am consolidat într-un runner reproductibil.

### 10.5 Procedură owner la re-sync cu master
La fiecare schimbare de framework: `test-optim` trage din `origin/master`, rulează `pytest -n auto`
(verde) + `lock.py --check` + `ruff`, actualizează acest document. NU se modifică testele de
business ale altor sesiuni; se optimizează doar structura/execuția din jur.

## 11. Securitate + dezvoltări 2026-06-08/09 (ce se testează acum)

### 11.1 Audit de securitate P0 (SEC-1/2/3) — închis
| # | Risc | Fix | Teste |
|---|------|-----|-------|
| **SEC-1** | path traversal pe `uid` de dosar (`../`) | UUID canonic; rute dau 404 (nu 500) pe uid invalid; `importa_folder` canonicalizează | `test_dosare_fs_security.py` (4 teste: uid non-UUID respins, ștergere-traversal NU distruge baza, rute→404, canonicalizare) |
| **SEC-2** | XSS din conținut scrape-uit randat în UI | `escapeHtml` + `urlSafe` în JS (`dosar.html`/`descoperire.html`); escapare markdown în documente | `test_documente.py::test_md_escape_html` (markdown). **Escaparea JS client-side = gap unit → e2e** (vezi §9) |
| **SEC-3** | CSRF (mutații cross-site) | middleware care respinge POST cu `Origin` străin; permite extensia locală fără Origin; GET neafectat | `test_csrf.py` (3 teste: origin străin respins / extensie locală permisă / GET neafectat) |

> Regulă nouă (securitate): orice fix de securitate ⇒ **test dedicat** (`test_<aria>_security.py` sau
> `test_csrf.py`) în aceeași dezvoltare, cu cazul de ATAC (nu doar happy-path). Owner-ul verifică
> existența testului la integrare; conținutul rămâne al autorului fixului.

### 11.2 PDF→DOCX (livrabile)
Livrabilele (raport, GDPR, AML) se generează **doar `.docx`** — selectorul de format a fost scos;
conversia în PDF e o acțiune LOCALĂ a utilizatorului („salvează ca PDF"). Convertorul
`report/pdf.docx_to_pdf` (LibreOffice/Word) rămâne pentru calea locală.
Teste: `test_web_curent::test_raport_mereu_docx_fara_pdf` (raport mereu .docx, fără fmt=pdf/ambele),
`test_web_api::test_download_raport_docx`, `test_report_pdf` (convertor local + căile de indisponibilitate).

### 11.3 Imoradar (P1.1) + diacritice
Portal nou `imoradar` în discovery, cu slugify de diacritice/spații pentru URL-ul de căutare.
Teste: `test_discovery_imoradar.py` (6: build-URL casă/teren, **slugify diacritice**, portal/categorie
necunoscute→raise, extragere URL-uri listing, parsare preț/supr/poză, căutare cu fetcher injectat)
+ fixturi `tests/fixtures/imoradar_{listing,search}.html`. Respectă regula §3 (portal nou ⇒ fixtură + test).

### 11.4 Igienă PII în loguri (audit #9)
La crearea unui dosar se loghează **legitimația** (ID profesional), NU numele evaluatorului (PII).
Acoperit pozitiv (`creator_legitimatie` în `test_dosare_fs`); **aserțiunea negativă** („numele NU
apare în jurnal") e un gap de propus implementatorilor — vezi §9.
