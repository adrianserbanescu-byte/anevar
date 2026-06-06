# Audit datorie tehnică — aplicația ANEVAR (`evaluare-anevar/`)

> Domeniu: după sesiunea cu mult cod nou (UI „output-first" ~1000 linii, 3 grile JS, ingestie, conformitate).
> Principiu: prioritizez refactorizările care **reduc riscul/întreținerea fără rescrieri riscante** ale codului funcțional.
> NU am modificat cod. Ordonat după **impact ÷ risc** (sus = cel mai bun raport).
> Data: 2026-06-06.

## Tabel datorie (ordonat impact ÷ risc)

| # | Impact | Risc refactor | Zonă | Datorie | Acțiune | Bucket |
|---|--------|---------------|------|---------|---------|--------|
| 1 | Mare | Mic | `curent/dosar.html` L809-978 | **3 grile JS quasi-identice** (casă/teren/chirii): fiecare = IIFE cu același schelet `build tabel → compForm() → calc → import`. Diferă doar: lista `ELEM_*`, prefix clasă (`g-`/`gt-`/`gc-`), endpoint, cheia preț (`pret`/`pret_mp`/`chirie_mp`), parserul rezultatului. ~170 linii, ~75% dublate. Grilele NU există în `wizard.html` (doar aici) → unificarea atinge UN fișier. | Builder parametrizat `creeazaGrila({wrap, prefix, elem, endpoint, cheiePret, randRezultat})`. 1 funcție + 3 config-uri. | A (UI pur) |
| 2 | Mare | Mic | `curent/dosar.html` (1028 linii) | **Monolit HTML+JS+Jinja**. Cuplaj Jinja↔JS = DOAR 3 puncte: `UID`, `WIZARD\|tojson`, `cont.nume/legitimatie` (L378-379, L774), toate în capul blocului `<script>` #2. Restul (grile, AML, descoperire, ingestie, anexe, tab-uri, salvare) e **JS pur, fără Jinja** → extractibil. | Mută JS-ul pur în `_dosar.js` (include Jinja, ca `_helpers.js`); păstrează un mic `<script>` cu cele 3 globale `var UID/WIZARD/CONT`. Reduce fișierul ~60%. | A (UI pur) |
| 3 | Mare | Mic | `curent.py` ↔ `evaluare.py` | **Funcția `audit.txt` duplicată ~identic** (curent.py L140-171 vs evaluare.py L99-129): aceeași secvență de 8× `j.inregistreaza(...)`. Diferă doar sursa ctx (`fs.incarca`+`construieste_context` vs `storage.load`). | Extrage `_construieste_jurnal(ctx) -> JurnalAudit` într-un helper partajat (ex. `audit/raport_audit.py`); ambele rute îl apelează. | A |
| 4 | Mare | Mediu | dualitate stocare (ADR-002, BLOCAT #17) | **2 căi de persistență paralele**: vechi SQLite (`/api/evaluare`, `evaluare.py`) vs nou foldere (`/api/dosar/*`, `curent.py`). Mulțimi disjuncte. `EvaluationInput`/`construieste_context`/`genereaza_raport` partajate (bine), dar 2 seturi de rute CRUD+raport+audit. Întreținere dublă la fiecare feature. | **Decizie Adi** (BLOCAT #17): punte / separare / retragere SQLite. NU rescrie acum — e blocat pe decizie. | B (Adi) |
| 5 | Mediu | Mediu | UI vechi (BLOCAT #18) | **Dualitate UI**: `wizard.html` (777) + `form.html` (179) + `grila.html` (346) vs `curent/dosar.html` (1027). `asambleaza()` reimplementat în wizard + dosar (drift). UI nou = ținta unică pe termen lung. | **Decizie Adi** (BLOCAT #18): când oprim întreținerea UI vechi. Până atunci: nu adăuga feature-uri noi în UI vechi. | B (Adi) |
| 6 | Mic | Mic | `dosar.html` L381-406, L447-501 | **Popover „!" (MAPARE vechi→nou)** marcat explicit „TEMPORAR (dev); se va șterge" (L380). ~25 linii date + logica de injectare partajată cu „?" (AJUTOR). | După validarea mapării (BLOCAT #16): șterge `MAPARE` + ramura `is-map` din `injecteazaPopover`. Quick win, dar gated pe confirmare Adi. | B (Adi) |
| 7 | Mic | Mic | toate routerele | **Import-uri în corpul funcțiilor** (≈40 ocurențe: aml.py 24, curent.py 8, piata.py, evaluare.py…). Intenționat parțial (lazy, timp de pornire .exe), dar inconsecvent — unele module sunt importate lazy într-un router și top-level în altul. | Lasă lazy ce justifică pornirea .exe (documentează o dată regula); ridică la top-level import-urile stdlib ieftine (`io`, `base64`, `zipfile`) unde nu ajută. Cosmetic. | A |
| 8 | — | — | `profil.py` `TipValoare="lichidare"` | **NU e cod mort** (ipoteza din brief = infirmată). `lichidare` e literal viu folosit de `report/generator.py` (L86, L481-512, secțiunea B4 „valoare de lichidare"). `ProfilEvaluare`/`profil.py` e puternic cablat (assembler, generator, sectiuni, report_context) + ~18 fișiere de test. **Nu atinge.** | Niciuna. Notat ca fals-pozitiv ca să nu fie șters din greșeală. | — |

## „Quick wins sigure" (impact mare/mediu, risc mic; fără decizie Adi)

- **#1 — Unifică cele 3 grile** într-un builder parametrizat. Cel mai bun raport impact/risc: un singur fișier (`dosar.html`), comportament identic, acoperit vizual la rulare. Reduce ~120 linii.
- **#2 — Extrage JS-ul pur din `dosar.html` în `_dosar.js`**. Blocantul presupus (interpolarea Jinja) e doar 3 globale izolate sus → restul e mecanic. Aceeași strategie deja folosită pentru `_helpers.js`/`_design.css`.
- **#3 — Deduplică `audit.txt`** între `curent.py` și `evaluare.py` (extrage `_construieste_jurnal(ctx)`). Pur back-end, ușor de testat.
- **#7 — Curăță import-urile lazy** stdlib ieftine (cosmetic, risc aproape nul).

Recomandare ordine: **#1 → #3 → #2** (grilele și jurnalul sunt cele mai sigure; extracția JS e mai mecanică dar atinge un fișier critic — fă-o cu rulare de verificare după).

## „Refactor mare — necesită grijă" (blocat pe decizie / risc structural)

- **#4 dualitate stocare SQLite vs foldere** și **#5 dualitate UI vechi/nou** sunt **datorie de arhitectură reală și ACUM costisitoare** (întreținere dublă), dar **NU se ating fără decizia lui Adi** (BLOCAT #17/#18, ADR-002). Sunt riscante (cod funcțional, ambele căi în uz). Recomandare interimară: îngheață feature-urile pe UI/stocarea veche; orice feature nou doar în UI nou + foldere.
- **#6 popover „!"** și ștergerea `MAPARE` — trivial tehnic, dar gated pe BLOCAT #16 (confirmarea mapării).

## Ce e ACUM riscant vs cosmetic

- **Riscant (cost de întreținere activ):** dualitatea de stocare (#4) și UI (#5) — fiecare feature nou se plătește de două ori și `asambleaza()` deja a divergat între wizard și dosar. Riscul nu e în cod, ci în *creșterea* lui până la decizie.
- **Datorie sigură de plătit acum:** #1/#2/#3 — reduc volumul și drift-ul fără a schimba comportamentul.
- **Cosmetic:** #7 (import-uri lazy), #6 (popover temporar, dar gated).
- **Fals-pozitiv:** #8 — `lichidare`/`ProfilEvaluare` NU sunt cod mort; nu șterge.

## Note pozitive (sănătate bună)

- `ruff` cu set bun (E/F/I/B/UP/SIM/C4) + `pytest-cov` cu **`fail_under=90`** (suita ~94%) — gard solid de regresie.
- `app.py` deja modularizat pe routere pe domenii (ADR-001), `Deps` injectat curat.
- `_helpers.js`/`_design.css` deja extrase ca include-uri Jinja — **precedent direct** pentru #1/#2.
- Niciun `# TODO`/`# HACK`/`# FIXME` real în cod (`XXX` apare doar ca placeholder de `entry.XXX` în `_feedback.html`, intenționat).
