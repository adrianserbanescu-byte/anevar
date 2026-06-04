# Evaluare ANEVAR

Aplicație locală pentru **evaluare imobiliară conform standardelor ANEVAR** (SEV 2025,
ghiduri GEV 500/520/630): casă + teren, apartament, comercial, industrial, agricol și
proprietăți speciale, prin cele patru abordări (cost, comparație, venit-capitalizare,
venit-DCF), cu generare de raport `.docx` și modul AML separat.

Rulează **integral local** (un singur `.exe`, fără cloud obligatoriu). Naratorul AI
(Claude) este opțional — fără cheie API, raportul folosește text-șablon.

## Cerințe

- Python **3.11+** (build-ul de distribuție folosește 3.12)
- Windows (executabilul țintă); codul e portabil, dezvoltarea merge pe orice OS

## Instalare (dezvoltare)

```bash
python -m venv .venv && .venv\Scripts\activate      # optional, recomandat
pip install -e .[dev]                                # intervale din pyproject.toml
```

Pentru a reproduce **exact** mediul verificat (cel din care se împachetează `.exe`-ul):

```bash
pip install -r requirements.lock
pip install -e . --no-deps
```

## Rulare

```bash
python -m evaluare
```

Pornește serverul pe <http://127.0.0.1:8000> și deschide browserul. Pagini principale:

| Rută | Descriere |
|------|-----------|
| `/wizard` | Flux ghidat în pași (recomandat) |
| `/grila` | Grile de comparabile: teren, casă, **chirii → venit** |
| `/descoperire` | Descoperire comparabile din portaluri |
| `/aml` | Modul AML (KYC, risc, documente) |
| `/formular` | Formular clasic (alternativă) |

### Configurare (opțională)

Variabile de mediu (sau fișier `.env` în directorul curent / lângă `.exe`):

| Variabilă | Implicit | Rol |
|-----------|----------|-----|
| `ANTHROPIC_API_KEY` | – | activează naratorul AI (fără ea: text-șablon) |
| `NARRATIVE_MODEL` | `claude-sonnet-4-6` | modelul folosit pentru narativ |
| `DB_PATH` | `date/evaluari.db` | baza SQLite cu dosarele |
| `OUTPUT_DIR` | `date` | director pentru fișiere generate |

## Teste & calitate

```bash
pytest -q                          # suita completă (370+ teste)
ruff check src tests scripts       # lint
python scripts/lock.py --check     # verifică lockfile la zi
```

Cârlige pre-commit (lint + teste la fiecare commit):

```bash
pip install pre-commit && pre-commit install
```

## Împachetare `.exe`

```bash
python -m PyInstaller evaluare-anevar.spec --noconfirm --clean
# rezultat: dist/evaluare-anevar.exe (onefile)
```

Note de împachetare (lecții învățate, vezi comentariile din `evaluare-anevar.spec`):

- `upx=False` — UPX corupea binare native Pillow (`_imagingft` → „decompression -1").
- `PIL._avif` exclus — Pillow 12 a inclus un binar AVIF care corupea arhiva PKG.
- La probleme de pornire, curăță folderele temporare `_MEI*` din `%TEMP%`.

Executabilul scrie un jurnal rotativ `evaluare-anevar.log` **lângă `.exe`** (util
pentru diagnoză pe teren).

## Structura

```
src/evaluare/
  engine/        # motoare de calcul (cost GBF, comparație, teren, venit, chirie, DCF)
  models/        # modele Pydantic (proprietate, comparabile, rezultate)
  report/        # generator raport .docx (SEV)
  discovery/     # descoperire comparabile din portaluri
  ingestie/      # extragere text din PDF (CF, CPE) + OCR injectabil
  aml/           # modul AML (risc, indicatori, raportare, documente)
  web/           # aplicația FastAPI
    app.py       #   composition root (compune routerele)
    deps.py      #   Deps (storage/client/fetcher/templates) — vezi docs/adr/ADR-001
    schemas.py   #   modele Pydantic pentru request bodies
    routers/     #   routere pe domenii: evaluare, grile, descoperire, aml, piata, pagini
    templates/   #   șabloane HTML + _design.css + _helpers.js
  logging_setup.py
scripts/         # utilitare (lock.py, build_localitati.py, export_chat.py, …)
tests/           # 370+ teste pytest
```

## Reproducerea dependențelor

`requirements.lock` fixează închiderea exactă a dependențelor proiectului. După un
upgrade verificat, regenerează-l:

```bash
python scripts/lock.py
```

Limitele superioare pe major din `pyproject.toml` previn salturile care strică
împachetarea (de ex. Pillow 12).
