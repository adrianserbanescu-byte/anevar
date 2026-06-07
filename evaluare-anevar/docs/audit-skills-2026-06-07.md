# Audit skill-uri Claude Code (2026-06-07)

Raport detaliat din rularea celor 6 skill-uri instalate din marketplace-ul
`dan323/easier-life-skills`: **dependency-audit, find-dead-code, improve-logging,
changelog, security-review, find-breaking-rest-api**.

**Taskurile actionabile sunt mutate în [`AUTONOM-taskuri.md`](AUTONOM-taskuri.md)**
sub secțiunea „🔧 Audit skill-uri (2026-06-07)". Deciziile pe Adi în
[`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md) §J.

---

## 1. `dependency-audit`

**3 vulnerabilități**, 12 pachete outdated (din 40 scanate).

### Vulnerabilități (acțiune imediată)

| Sev | Pachet | Curent | CVE/ID | Descriere | Fix |
|---|---|---|---|---|---|
| **High** | `urllib3` | 2.6.3 | PYSEC-2026-141 | Cross-origin redirects via ProxyManager ignoră `assert_same_host=False` | 2.7.0 |
| **High** | `urllib3` | 2.6.3 | PYSEC-2026-142 | Decompresses full response în loc de porțiunea cerută cu `read(amt=N)` | 2.7.0 |
| **Moderate** | `idna` | 3.13 | CVE-2026-45409 | Bypass al fix-ului CVE-2024-3651 cu payload-uri unicode | 3.15+ |

### Outdated fără CVE (programat)

`anthropic 0.105 → 0.107`, `uvicorn 0.48 → 0.49`, `pydantic-core 2.46 → 2.47`,
`click`, `pytest-cov`, `requests`, `lxml`, `ruff`, `soupsieve`, `certifi`.

`npm audit`: **0 vulnerabilități**, `pptxgenjs` la zi.

---

## 2. `find-dead-code`

13 candidate reale (excluzând AML și routere FastAPI care sunt invocate prin
dispatch framework).

### High confidence (verifică, apoi posibil de șters)

- `engine/reconciliation.py:13` — `reconcile`
- `engine/validation.py:90` — `valideaza_profil`
- `engine/chirie.py:85` — `date_venit_din_chirie`
- `money.py:14,19` — `round_lei`, `pct`
- `localitati.py:13` — `slugify`
- `report/sectiuni.py:35` — `sectiuni_pentru_profil`
- `dosare_fs.py:190` — `importa_folder` (endpoint legacy)
- `importers/url_parser.py:372` — `to_comparable`
- `web/app.py:31` — `doar_host_local` (atenție: e middleware aplicat dinamic)
- `audit/raport_audit.py:19` — `scrie_audit` (verifică, modul recent)

### Posibil intentional (decizie Adi → §J BLOCAT)

- `engine/abordari.py:25,34` — `abordare_cost`, `abordare_comparatie`
- `engine/venit.py:51` — `abordare_venit`

  Sunt API public pentru cele 4 abordări ANEVAR. Fluxul curent (`web/routers/evaluare.py`)
  nu pare să le cheme direct — verifică dacă sunt expuse sau dead.

### Excluse (motiv)

- 51 funcții `web/routers/*` — toate `@router.get/post/delete/...`, dispatch FastAPI
- ~90 atribute Pydantic în `aml/models.py`, `ingestie/models.py`, `discovery/profiles.py` —
  câmpuri DTO legitime
- **Tot ce e în `aml/`** — respectat protocolul „AML = bucket C"

---

## 3. `improve-logging`

Doar **7/85 fișiere `src/` emit log-uri** (8% coverage). 40 except blocks fără
logging și fără re-raise — eșuează silent.

### Module fără NICI un log

| Modul | Importanță |
|---|---|
| `engine/` (abordari, chirie, reconciliation, validation, venit) | **Calculul de bază** — fără audit trail |
| `report/` | **Generarea `.docx`** — nu știi ce a mers/nu a mers |
| `web/app.py` și `web/deps.py` | **Bootstrap FastAPI** — pornirea cere observabilitate |
| `web/routers/{aml,curent,evaluare,descoperire,grile}` | **REST endpoints** — 5/7 routere sunt mute |
| `ingestie/{extractoare,vlm}` | Procesare documente — eșecuri tăcute |
| `importers/url_parser.py` | Parsing extern — 8 except blocks fără log |
| `audit/raport_audit.py` | **Ironic — modulul de audit nu emite log** |

### Silent failures (cele mai expuse)

| Fișier | Linii | Comportament |
|---|---|---|
| `importers/url_parser.py` | 55, 69, 98, 140, 158, 304, 396, 402 | `return None` / `False` la 8 except |
| `discovery/extractor.py` | 48, 65, 168 | `return None` la fetch eșuat |
| `dosare_fs.py` | 79, 138, 158 | `dosar.json` corupt → 404 fără log (commit `515fffd`) |
| `indice_anevar.py` | 33 | Index ANEVAR neîncărcat → `{}` în tăcere |
| `zona.py` | 47 | `pass` în except — anti-pattern declarat |
| `cont.py` | 28 | `return None` la cont absent |
| `ai/narrative.py` | 102, 110 | `return str(x)` fallback fără indicii |

---

## 4. `changelog`

**Generat:** `CHANGELOG.md` la rădăcina proiectului (33 KB, 499 linii).
Categorizat pe Securitate / Robustețe / Conformitate ANEVAR / UI nou / AML /
Audituri / Council LLM / Bugfixuri / Loop autonom / Documentație / Diverse,
grupat pe fiecare dintre cele 8 zile cu activitate (2026-05-31 → 2026-06-07,
381 commits).

---

## 5. `security-review` (OWASP Top-10)

**Verdict global:** stare bună. Codul arată multiple iterații de hardening
(commits `Hardening`, `Securitate`, `Audit final`).

| OWASP | Risc | Stare |
|---|---|---|
| A01 Broken Access Control | Aplicație single-user locală, fără auth | **By design** — protejat de `doar_host_local` middleware (anti-DNS-rebinding) |
| A02 Crypto Failures | — | ✓ Niciun secret hardcodat |
| A03 Injection | — | ✓ Niciun `eval`/`exec`/`os.system`/`shell=True`/SQL raw |
| A04 Insecure Design | — | ✓ `debug=True` absent, CORS NU e wildcard |
| A05 Misconfiguration | CORS restrâns la `chrome-extension://*` și `moz-extension://*` | ✓ Strict |
| A07 Auth/Identification | hashlib.sha256 pentru audit-chain (legit) | ✓ |
| A08 Software Integrity | — | ✓ Niciun `pickle.loads`/`yaml.load` |
| A09 Logging Failures | 7/85 fișiere emit log; 40 except silent | ⚠ Acoperit la skill-ul `improve-logging` |
| A10 SSRF | `_url_public_sigur(url)` validează în `url_parser.py:416` | ✓ — verifică și pentru `curs_bnr.py` și `ai/narrative.py` (URL static, dar fii defensiv) |

### Findings prioritizate

| # | Severitate | Componentă | Detalii |
|---|---|---|---|
| 1 | **High** | `requirements.lock` | `urllib3 2.6.3` + `idna 3.13` — vezi §1 |
| 2 | **Medium** | `curs_bnr.py:18`, `ai/narrative.py:230` | `requests` direct, fără `_url_public_sigur` — URL-uri statice acum, fii defensiv |
| 3 | **Low** | `web/routers/curent.py:97-149` | `{uid}` path params — adaugă regex Pydantic `r"^[a-f0-9-]{36}$"` ca defense-in-depth |
| 4 | **Info** | `import-docx` la `routers/curent.py:64` | **Exemplu de urmat** — `_uuid.uuid4()` tmpdir + `.name` taie traversal + limita 25MB + cleanup în `finally` |

---

## 6. `find-breaking-rest-api`

**Zero breaking changes** în ultimele 100 commits.

| Comparație | Total HEAD | Adăugate | Eliminate / schimbate path |
|---|---|---|---|
| HEAD vs HEAD~50 | 62 | 2 | **0** |
| HEAD vs HEAD~100 | 62 | 21 | **0** |

Coexistența `/api/evaluare/...` (vechi) + `/api/dosar/...` (UI nou) — vezi
decizia §D.18 din `BLOCAT-pe-Adi.md` (retragerea UI vechi).

---

## Sumar acțiuni

Toate taskurile autonome → [`AUTONOM-taskuri.md`](AUTONOM-taskuri.md) secțiunea
„🔧 Audit skill-uri (2026-06-07)".

Decizii necesare Adi → [`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md) §J.
