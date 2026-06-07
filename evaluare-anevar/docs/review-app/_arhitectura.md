# Arhitectura aplicației Evaluare ANEVAR — note de REVIEW

> Document factual pentru review (audiență mixtă: evaluatori + IT/risc de bancă).
> Sursa = codul, nu presupuneri. Referințele la fișiere sunt relative la
> `C:/Users/adyse/anevar/evaluare-anevar/`. Actualizat: 2026-06-07.

Aplicație **desktop, offline, single-user**: server web local care rulează în fundal și se
folosește prin browser. Generează rapoarte de evaluare `.docx` (casă + teren, garantare credit)
și documente de conformitate (AML / GDPR). Datele (PII: nume client, CNP, adrese) **rămân pe
calculatorul evaluatorului** — nu există backend remote.

---

## 1. Tech stack

| Strat | Tehnologie | Versiune (din `pyproject.toml`) |
|---|---|---|
| Limbaj | Python | `>=3.11`; build `.exe` pe **3.12** (`.github/workflows/ci.yml`) |
| Web framework | **FastAPI** | `>=0.110,<1` |
| Server ASGI | **uvicorn** | `>=0.29,<1` (rulat in-process, single worker) |
| Templating | **Jinja2** | `>=3.1,<4` |
| Validare I/O | **pydantic** | `>=2.6,<3` (toate request-urile = modele Pydantic) |
| Persistență (1) | **SQLite** (`sqlite3` stdlib) | — (fluxul vechi + cozi auxiliare) |
| Persistență (2) | **foldere pe disc** (`dosare_fs`) | — (fluxul nou „folder = adevăr") |
| Generare doc | **python-docx** | `>=1.1,<2` |
| Scraping/parsare | **requests** + **beautifulsoup4** | `>=2.31,<3` / `>=4.12,<5` |
| PDF / OCR | **PyMuPDF (fitz)** | `>=1.24,<2` |
| AI (opțional) | **anthropic** SDK + Perplexity (HTTP) | `>=0.40,<1` |
| Imagini (tranzitiv) | **Pillow** | `>=11,<13` |
| Împachetare | **PyInstaller** → `evaluare-anevar.exe` | onefile, **console=True**, ~50 MB |

Limite superioare pe major fixate intenționat (o actualizare majoră poate strica build-ul `.exe`,
ex. Pillow 12 a inclus binarul `_avif` care corupea arhiva). Versiunile exacte verificate sunt în
`requirements.lock`; CI verifică lockfile-ul la zi (`scripts/lock.py --check`).

**Dependențe excluse explicit din `.exe`** (`evaluare-anevar.spec:40-42`): `numpy`, `scipy`,
`pandas`, `matplotlib`, `sklearn`, `sympy` (NU sunt importate — economisesc ~120 MB),
plus `cryptography`, `PIL._avif`, `tkinter`, `test` (corupeau arhiva PKG / nefolosite). UPX
dezactivat (corupea binare native). HTTPS merge prin `ssl` din stdlib, nu prin pachetul
`cryptography`.

---

## 2. Cum rulează

**Punct de intrare:** `src/evaluare/__main__.py` → `run.py` (în `.spec`). Pașii (`_ruleaza`):

1. **Determină directorul de date writable** (`_baza_scriere`): lângă `.exe` dacă se poate scrie
   acolo (test real cu fișier-probă `.scriere_test`); altfel **fallback pe
   `%LOCALAPPDATA%\EvaluareANEVAR`**. În dezvoltare = directorul curent (`Path.cwd()`).
2. **Încarcă `.env`** din directorul curent ȘI de lângă `.exe` (`_incarca_env`); `os.environ.setdefault`
   — nu suprascrie variabile deja setate.
3. **Ancorează datele** (dacă nu sunt deja în `.env`):
   `DB_PATH = <baza>/date/evaluari.db`, `OUTPUT_DIR = <baza>/date`.
4. **Logging** (`configure_logging`, scrie și în fișier rotativ lângă `.exe` în mod frozen).
5. **Avertisment cloud-sync**: dacă `DB_PATH` conține `onedrive`/`dropbox`/`google drive`
   → warning „risc de blocare a fișierului" (SQLite în folder sincronizat = `database locked`).
6. **Init storage SQLite** + **backup la pornire** (`storage.backup`, păstrează 10).
7. **Pornește serverul**: `uvicorn.run(app, host="127.0.0.1", port=8000)`.
8. **Deschide browserul** pe `http://127.0.0.1:8000/` — dar **doar după ce portul acceptă
   conexiuni** (`_deschide_browser_cand_e_gata`, thread daemon, retry ~30s) — evită
   `ERR_CONNECTION_REFUSED` la dezarhivarea onefile.

**Host/port hardcodate:** `HOST = "127.0.0.1"`, `PORT = 8000` (`__main__.py:31-32`). **Bind doar
pe loopback** — neexpus în rețea (confirmat în audit, security #8).

**Robustețe la pornire:** orice excepție în `_ruleaza` → scrisă în `eroare-pornire.log` + afișată
pe consolă; în mod `.exe` așteaptă `Enter` (nu mai e „flash-and-close").

### Modelul de stocare — DOUĂ paradigme coexistă

**(A) „Folder = adevăr" (UI-ul NOU, output-first)** — `src/evaluare/dosare_fs.py`.
Fiecare dosar = un folder `<OUTPUT_DIR>/dosare/<uuid4>/` cu:
- `dosar.json` — semnătura: `uuid`, `creator_legitimatie`+`creator_nume`, `identitate` (câmpuri
  blocabile), snapshot `wizard`, timestamps.
- `raport-<timestamp>.docx` — versiuni generate (**retenție: ultimele 10**, `PASTREAZA_VERSIUNI`).

La pornire/listare se **scanează folderele** (`listeaza()` via `glob("*/dosar.json")`) — NU există
o bază autoritară. Un `_index.json` reține „ce am văzut ultima dată", folosit DOAR pentru `diff()`
(existente / noi / dispărute) — detectează dosare adăugate sau șterse manual pe disc.
Scriere **atomică** (`_scrie_atomic`: tmp + `os.replace`) → fără corupție la crash.
Câmpuri de IDENTITATE blocate după creare (`CAMPURI_IDENTITATE`): `scop`, `tip_proprietate`,
`nume_client`, `id_client`, `judet`, `localitate`.

**(B) SQLite (fluxul VECHI + cozi auxiliare)** — `src/evaluare/db/storage.py`.
`Storage` peste `evaluari.db`, cu **migrare de schemă** (`PRAGMA user_version`, `SCHEMA_VERSION=4`)
și **backup consistent** prin API-ul SQLite (`src.backup(dst)`). Tabele:
- `evaluari` — dosare vechi (ReportContext serializat JSON + sumar + snapshot wizard).
- `import_anunturi` — coada de anunțuri de la extensie (dedup pe `sursa_url`, UNIQUE).
- `feedback` — feedback testeri (local, offline).

SQL **100% parametrizat** (fără concatenare) — fără SQL injection.

> Notă de review: cele două modele rulează în paralel. Dosarele NOI se salvează pe foldere
> (`curent.py`); fluxul vechi (`evaluare.py`) încă scrie în SQLite. `curent.py:/api/dosar/{uid}/calcul`
> a fost introdus tocmai ca să NU mai scrie rânduri orfane în SQLite la fiecare „Calculează".

---

## 3. Inventar module / endpoint-uri

App-ul (`web/app.py:create_app`) compune 7 routere pe domenii (ADR-001), fiecare expune
`build_router(deps) -> APIRouter`. Dependențele (`Deps`): storage, client AI, fetcher HTTP, templates.

### `routers/curent.py` — UI NOU (cont + dosare pe foldere)
| Metodă | Rută | Rol |
|---|---|---|
| GET | `/cont` | pagina cont local |
| POST | `/api/cont` | creează/actualizează contul evaluatorului |
| GET | `/incepe` | homepage UI nou (listă dosare + `diff` disc) |
| POST | `/api/dosar` | creează dosar nou (folder + `dosar.json`) |
| POST | `/api/dosar/import-docx` | import raport `.docx` → dosar nou (identitate din nume+text) |
| GET | `/dosar/{uid}` | workspace dosar (HTML) |
| GET | `/api/dosar/{uid}` | citește `dosar.json` |
| POST | `/api/dosar/{uid}/salveaza` | salvează câmpurile wizard |
| POST | `/api/dosar/{uid}/sterge` | șterge folderul dosarului |
| POST | `/api/dosar/{uid}/scoate-din-index` | scoate dosar dispărut din `_index.json` |
| POST | `/api/dosar/{uid}/calcul` | calcul valoare FĂRĂ persistență SQLite |
| POST | `/api/dosar/{uid}/audit.txt` | urmă de audit (jurnal hash + validare încrucișată) |
| POST | `/api/dosar/{uid}/raport.docx` | generează `.docx` + versionează în folder (temp șters după trimitere) |
| GET | `/api/backup-dosare.zip` | arhivează TOATE dosarele într-un `.zip` |

### `routers/evaluare.py` — flux VECHI (SQLite)
`POST /api/evaluare` (creează+salvează), `GET /api/evaluare/{eid}`,
`GET /api/evaluare/{eid}/raport.docx` (`?demo=1` = note de proveniență),
`/redenumeste`, `/snapshot`, `/dosar`, `/sterge`, `GET /api/evaluare/{eid}/audit.txt`,
`GET /api/backup.db`, `GET /evaluare/{eid}` (pagina rezultat).

### `routers/grile.py` — grile de comparabile
`POST /api/grila-teren`, `/api/grila-casa`, `/api/grila-chirii` (motoarele `engine/`);
`GET /grila`. **ValueError → 422** (date insuficiente, nu 500 — fix hardening).

### `routers/descoperire.py` — descoperire comparabile + extensie
`POST /api/descopera` (casă), `/api/descopera-teren`, `POST /api/import-anunt` (de la extensie),
`GET /api/anunturi-importate`, `/sterge`, `/sterge-unul`, `GET /descoperire`.
Erori de rețea portal → **502** cu mesaj „adaugă manual".

### `routers/piata.py` — instrumente de piață / ingestie
`POST /api/import-url` (scraping un anunț; pagină-listă → 422), `POST /api/ingestie`
(PDF/OCR: cf/releveu/plan/cpe), `POST /api/zona` (derivă județ/localitate),
`GET /api/curs-bnr`, `/api/indice-anevar`, `/api/localitati`.

### `routers/aml.py` — conformitate AML (Legea 129/2019) + GDPR
`POST /api/aml/evalueaza` (scor risc + liste), generatoare `.docx`:
`/norme-interne`, `/evaluare-risc`, `/decizie`, `/fisa-kyc`, `/rtn`, `/rts`;
`/api/gdpr/politica.docx`, `/api/gdpr/consimtamant.docx`; `GET /aml`.
**RTN/RTS persistate SEPARAT** de dosar (`<db>.parent/aml_confidential/`, `StoreAML`) — tipping-off,
art. 38.

### `routers/pagini.py` — pagini HTML + status + feedback
`GET /api/status` (versiune+uptime+nr. coadă — ping-ul extensiei), `GET /` (alegere UI),
`/documente`, `/documente/{slug}`, `/formular`, `/wizard`, `/dosare`,
`POST /api/feedback` (+ CSV lângă `.exe`), `GET /api/feedback`, `/api/feedback.csv`, `/feedback`.

> Notă review: API-ul local **NU are autentificare** (single-user, loopback). Securitatea se
> bazează pe garda Host + bind loopback (vezi §5), nu pe credențiale.

---

## 4. Date externe (cum intră informația de piață)

Patru canale, toate **manual-driven** sau cu degradare gratioasă; niciunul nu rulează scraping
automat/de fundal:

**(a) Descoperire portaluri** — `discovery/` (`portal_search` + `orchestrator` + `extractor` +
`scoring`). Pipeline: **caută** (construiește URL de căutare pe judeţ/localitate, portaluri fixe
`imobiliare`/`storia` — `BAZE` hardcodat) → **citește** anunțurile (`fetch_html`) →
**parsează** (`parse_listing_html`: JSON-LD → `__NEXT_DATA__` → og:meta/regex) →
**punctează** (`scor_candidat`, relevanță 0-100) → **explică** (breakdown + atribute + avertismente).
Anunțurile fără suprafață sunt **declasate** și marcate „completează manual"; paginile de
listă/căutare sunt detectate și sărite (`pagina_lista`). Opțional, un client AI extrage atribute
secundare din descriere. **Avertisment în cod**: scraping direct poate încălca ToS-ul site-urilor.

**(b) Extensia de browser** — `extensie-browser/` (Manifest V3). **Omul navighează MANUAL** pe
storia.ro / imobiliare.ro / olx.ro; un buton flotant (`content.js`) trimite DOM-ul paginii
curente către service worker (`background.js`), care îl `POST`-ează la `http://127.0.0.1:8000/api/import-anunt`.
**Zero scraping automat, zero polling, zero anti-bot** (afirmat în manifest + cod). `content.js`
detectează că pagina e un anunț individual (nu listă) înainte de trimitere. Permisiuni minime:
`activeTab`, `storage` + `host_permissions` pe cele 3 portaluri + loopback. Aplicația acceptă POST-ul
prin CORS restrâns la `chrome-extension://*` / `moz-extension://*` (`app.py:40-45`).

**(c) Import `.docx`** — `importers/docx_dosar.py`. Strategie pe 2 straturi:
**(1)** numele fișierului dă identitatea sigură (`<id> <nume client> <tip> <localitate>`, ex.
`21766 Bololoi Daniela-Doina locuinta Busteni.docx`); **(2)** textul (paragrafe + tabele) dă extra
best-effort prin regex (beneficiar/bancă, scop, data inspecției, județ din localitate). Câmpurile
negăsite rămân **goale** — fără ghicire tăcută. `.docx` ilizibil → degradează la parsarea numelui.

**(d) Ingestie PDF/OCR** — `ingestie/` (`ocr.py` + `extractoare.py`). `extrage_text`: text încorporat
din PDF digital via `fitz` (PyMuPDF); dacă PDF-ul e scanat (text < 20 caractere) și un `ocr_fn`
e injectat, rulează OCR (injectabil → fără dependență dură). Extractoare regex tolerante la diacritice
pentru **CF** (cadastral, CF, suprafață, proprietari, sarcini), **releveu** (arie utilă/construită,
regim înălțime), **plan** (suprafață teren, deschidere), **CPE** (clasă energetică, consum).
Toate câmpurile opționale — se propun, evaluatorul confirmă.

**(e) Surse de referință** — `GET /api/curs-bnr` (curs BNR), `/api/indice-anevar` (indice ANEVAR),
ambele cu fetch live + fallback 502 dacă nu e internet.

---

## 5. Securitate (hardening recent + pozitive)

Model de amenințare (din `docs/audit-final/security.md`): serverul e pe loopback fără auth;
atacatorii relevanți NU sunt din rețea, ci **(a)** pagini web vizitate de evaluator
(CORS/CSRF/DNS-rebinding pe localhost), **(b)** conținut extern procesat (URL anunț → SSRF; HTML
portal; `.docx`/PDF importate), **(c)** fișiere de dosar importate.

### Hardening implementat (Bucket A — toate rezolvate)

| Apărare | Unde | Ce face |
|---|---|---|
| **Anti-SSRF** | `importers/url_parser.py:391-418` (`_url_public_sigur`/`fetch_html`) | `fetch_html` acceptă DOAR `http(s)` către un host care rezolvă la **IP public**. Rezolvă DNS (`getaddrinfo`) și **respinge** loopback / privat / link-local / reserved / multicast / unspecified (127/8, 10/8, 192.168, **169.254.169.254** metadata etc.). Blochează port-scan intern / SSRF blind. |
| **Gardă Host (anti DNS-rebinding)** | `web/app.py:29-37` (middleware `doar_host_local`) | Respinge orice cerere al cărei `Host` ≠ `{127.0.0.1, localhost, ::1, testserver}` → **403**. Un site (evil.com) care rezolvă la 127.0.0.1 trimite `Host: evil.com` → respins → nu poate șterge dosare / exfiltra PII prin API-ul local. |
| **Grilă → 422** | `routers/grile.py` (+ `curent.py:_context`) | `ValueError` la <3 comparabile prins → **422** clar (înainte: 500 neprins). |
| **Limită DoS base64 (~25 MB)** | `curent.py:76` (import-docx) + `piata.py:57` (ingestie) | Lungimea payload-ului base64 > 35M caractere (~26 MB decodat) → **413**, înainte de `b64decode` (evită OOM/umplere disc pe single-process uvicorn). |
| **Igienă temp `.docx` (PII)** | `curent.py:193-195` | `.docx`-ul temporar din `%TEMP%` e șters după trimitere (`BackgroundTask`); versiunea persistă DOAR în folderul dosarului. |
| **Anonimizare CNP** | `report/anonymizer.py` (regex extins prefix „9") | CNP (inclusiv prefix 9 / rezidenți) mascat înainte de trimiterea la AI. |
| **Dosar corupt → 404** | `dosare_fs.py:77-81` (`incarca`) | `dosar.json` ilizibil/corupt → `KeyError` → **404** la caller (nu 500). |
| **Path traversal mitigat** | `curent.py:84-88`, `dosare_fs.py:43` | Import folosește `Path(nume).name` într-un tmpdir unic; numele de folder = mereu `uuid4()` (nu input user). |

### Pozitive confirmate (audit)
- **SQL 100% parametrizat** (`db/storage.py`) — fără SQL injection.
- **Bind loopback** `127.0.0.1` (nu `0.0.0.0`) — neexpus în LAN.
- **Fără** `eval` / `exec` / `os.system` / `subprocess` (runtime) / `pickle` / `yaml.load` (grep curat).
- **Scriere atomică** a fișierelor de dosar (`os.replace`).
- **CORS fără `allow_credentials`**; restrâns la extensii de browser.
- **Igienă loguri verificată curată**: doar hash-uri / erori, **fără PII** (nume / CNP / adresă);
  descoperirea loghează doar URL-uri publice + județ/localitate; nivel **INFO** în producție;
  `RotatingFileHandler` (1 MB × 3) limitează mărimea.

### Riscuri reziduale / observații pentru review (NU sunt rezolvate în cod)
- **Fără autentificare** pe API-ul local (acceptabil pentru single-user + loopback + gardă Host,
  dar de notat pentru risc bancar).
- **Lipsă lock de identitate la finalizare** (Bucket B/Adi): modificarea CNP/preț DUPĂ generare,
  fără urmă în jurnal = risc de fraudă semnalat de council. Motorul de jurnal hash EXISTĂ
  (`audit/jurnal.py`); lipsește lock-ul la asumare (ADR-003 / pending).
- **Fără criptare la repaus**: SQLite + dosare + rapoarte = **PII în clar pe disc**. Minim propus:
  ghidaj BitLocker SAU disclaimer „protecția discului = responsabilitatea evaluatorului (operator
  de date)" (pending jurist).
- **Scurgere PII parțială la AI** (security #6, doar cu gateway activ): `beneficiar`/numele băncii
  poate ajunge neanonimizat la furnizorul AI extern. Relevant doar dacă se configurează o cheie API.
- **Import folder dosar** (`dosare_fs.importa_folder`, security #4): nu validează schema/tipurile/
  mărimea fișierelor copiate (apel intern, neexpus prin HTTP în codul citit) — Bucket B.

### Acoperire de teste
- **496 funcții de test** în **87 fișiere** `tests/test_*.py` (`def test_`).
- Din care **126 teste web/HTTP** (17 fișiere `test_web_*.py`) prin **FastAPI `TestClient`** —
  acoperă endpoint-uri, **accesibilitate WCAG 2.1 AA** (`test_web_a11y.py`: landmark `<main>`/`<nav>`),
  hardening URL (`test_url_parser_hardened.py`), garduri council (`test_garduri_council.py`),
  end-to-end de calcul (`test_end_to_end.py`).
- **Smoke E2E Playwright** (headless): `scripts/_pw_smoke.py` — încărcare pagini fără erori de
  consolă, cablare câmpuri/butoane, fluxuri între pagini (localStorage), comutare tab-uri.
- **Coverage gate: `fail_under = 90`** (`pyproject.toml`); suita acoperă ~94%.
- **CI** (`.github/workflows/ci.yml`, `windows-latest`, Python 3.12): ruff + verificare lockfile +
  pytest cu `--cov`.
- **Smoke build**: `scripts/build.py --smoke` pornește `.exe`-ul și lovește `/api/status` (200).

> Notă: `docs/audit-final/00-sinteza-audit-final.md` citează „507 teste + 90 e2e" — cifră istorică
> dintr-un snapshot anterior; numărătoarea curentă a codului este cea de mai sus (496 / 87 fișiere).

---

## Anexă — fișiere cheie

| Subiect | Fișier |
|---|---|
| Compunere app + middleware securitate | `src/evaluare/web/app.py` |
| Pornire / data dir / browser | `src/evaluare/__main__.py` |
| Stocare foldere („adevăr") | `src/evaluare/dosare_fs.py` |
| Stocare SQLite + migrări + backup | `src/evaluare/db/storage.py` |
| Cont local evaluator | `src/evaluare/cont.py` |
| Config + client AI | `src/evaluare/config.py` |
| Logging (rotativ, fără PII) | `src/evaluare/logging_setup.py` |
| Routere | `src/evaluare/web/routers/{curent,evaluare,grile,descoperire,piata,aml,pagini}.py` |
| Anti-SSRF + parsare anunț | `src/evaluare/importers/url_parser.py` |
| Import `.docx` → wizard | `src/evaluare/importers/docx_dosar.py` |
| Ingestie PDF/OCR + extractoare | `src/evaluare/ingestie/{ocr,extractoare}.py` |
| Descoperire (pipeline) | `src/evaluare/discovery/{portal_search,orchestrator}.py` |
| Extensie browser | `extensie-browser/{manifest.json,content.js,background.js}` |
| Build `.exe` | `scripts/build.py`, `evaluare-anevar.spec`, `pyproject.toml` |
| Audit securitate (sursă) | `docs/audit-final/{security.md,00-sinteza-audit-final.md}` |
