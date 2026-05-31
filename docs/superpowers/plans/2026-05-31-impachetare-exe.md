# Împachetare executabil (PyInstaller) — Plan 4 (parțial: doar `.exe`)

**Goal:** Livrarea aplicației web locale ca un singur executabil Windows cu dublu-click, fără ca utilizatorul să instaleze Python sau dependențe.

**Status:** ✅ DONE (partea de împachetare). Importul comparabilelor prin URL rămâne amânat
până la decizia de strategie (Apify vs scraping direct).

## Artefacte

- `run.py` — punct de intrare pentru PyInstaller; apelează `evaluare.__main__.main()`.
- `evaluare-anevar.spec` — config PyInstaller: include șabloanele Jinja2 (`web/templates`),
  colectează submodulele cu importuri dinamice (`uvicorn`, `anthropic`).
- `start.bat` — pornire din sursă (variantă de dezvoltare, necesită Python).

## Build

Din `evaluare-anevar/`:
```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean evaluare-anevar.spec
```
Rezultat: `dist/evaluare-anevar.exe` (~42 MB, un singur fișier).

## Rulare

Dublu-click pe `dist/evaluare-anevar.exe` → pornește serverul pe `http://127.0.0.1:8000/`
și deschide automat browserul. Cheia API (opțional, pentru narativ AI) se pune într-un
fișier `.env` lângă executabil: `ANTHROPIC_API_KEY=sk-ant-...`.

## Smoke test efectuat

Executabilul pornit → `GET /` returnează 200 cu formularul HTML; serverul uvicorn rulează
corect; oprire curată. Verificat la build.

## Rămâne (Plan 4 — partea a doua, amânată)

Import comparabile prin paste URL (imobiliare.ro / storia.ro). Necesită decizie de strategie:
- **API Apify** (stabil, plătit, token necesar), sau
- **scraping direct** (gratis, fragil, risc anti-bot/ToS).

Modul nou propus: `evaluare/importers/url_parser.py` cu teste pe fixturi HTML salvate
(nu live), plus un endpoint `POST /api/import-url` care întoarce un `Comparable` parțial
completat pentru a fi confirmat de evaluator în formular.
