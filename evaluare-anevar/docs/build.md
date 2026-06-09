# Build & distribuție — `evaluare-anevar.exe`

Cum se construiește executabilul de distribuție, **reproductibil offline** (item pre-lansare).

## 1. Build canonic (rapid)

Pe un **venv curat Python 3.12** (nu env-ul global — vezi §3 de ce contează pentru dimensiune):

```powershell
cd evaluare-anevar
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.lock pyinstaller
.\.venv312\Scripts\python.exe scripts\build.py --clean --upx   # --upx optional (cere upx.exe; -~3 MB)
#   -> dist\evaluare-anevar.exe  (~37.6 MB cu UPX; ~40.6 MB fără)
```

- `--clean` = build complet reproductibil (șterge `build/` + invalidează cache-ul PyInstaller).
- `--upx` = comprimă `mupdfcpp64.dll` (auto-descoperă `upx.exe` din PATH / `UPX_DIR` / `.upx/`). Opțional.
- **Smoke** (NU pe portul 8000 = live): pornește exe-ul cu `ANEVAR_PORT=8155 ANEVAR_NO_BROWSER=1`,
  apoi verifică `GET /api/status` (200) + câteva pagini + `POST /api/ingestie` (calea fitz/mupdf).
- Build measured: ~113s pe venv curat; exe 37.6 MB; smoke complet verde.

> **De ce venv curat:** pe un env Python global poluat (ex. pachete instalate de la skill-uri de
> science), PyInstaller trage tranzitiv module în plus → exe **~44 MB** în loc de 37.6 MB. Dimensiunea
> canonică (cea mai mică) cere un venv care are DOAR dependențele proiectului.

## 2. Reproducere OFFLINE (independentă de PyPI) — recomandat pentru lansare

**Problema:** `requirements.lock` fixează versiuni exacte (ex. `anthropic==0.105.2`,
`certifi==2026.4.22`) care **nu mai sunt pe PyPI public** — au fost obținute dintr-un index/cache
diferit. Un `venv` proaspăt + `pip install -r requirements.lock` pe altă mașină **eșuează**
(„No matching distribution"). Soluția: împachetăm toate wheel-urile o dată și instalăm din ele.

### 2.1 Generare bundle de wheel-uri (o dată, de pe mașina care ARE versiunile în cache)

```powershell
cd evaluare-anevar
.\.venv312\Scripts\python.exe -m pip download -r requirements.lock pyinstaller -d packaging\wheels
#   -> packaging\wheels\*.whl  (49 wheel-uri, ~50 MB; include pyinstaller + tranzitivele)
```

### 2.2 Build OFFLINE pe ORICE mașină (zero acces la PyPI)

```powershell
cd evaluare-anevar
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install --no-index --find-links packaging\wheels -r requirements.lock pyinstaller
.\.venv312\Scripts\python.exe scripts\build.py --clean   # (+ --upx dacă ai upx.exe)
```

**Verificat:** venv proaspăt + `pip install --no-index --find-links packaging\wheels …` instalează
complet (fastapi + pydantic + fitz + anthropic + pyinstaller) fără nicio conexiune la PyPI. ✓

### 2.3 Unde trăiește bundle-ul de wheel-uri
`packaging/wheels/` (~50 MB) e **gitignored** (nu umflăm repo-ul). Pentru lansare, arhivează-l ca
artefact de release (ex. `packaging/evaluare-anevar-wheels.zip`) lângă exe. Decizie de luat cu
owner-ul de release: commit în repo (self-contained, +50 MB) **sau** artefact extern (repo curat).

## 3. Release checklist (înainte de a publica un `.exe` ca artefact)

Gate pre-distribuție — toate trebuie ✓ înainte de a da exe-ul evaluatorilor:

```powershell
# 1) suita pytest verde (gate de unitate + integrare)
.\.venv312\Scripts\python.exe -m compileall -q src tests
.\.venv312\Scripts\python.exe -m pytest -n auto --dist loadscope --max-worker-restart=4 -q --cov=evaluare

# 2) harness e2e verde (Playwright; verifică fluxurile UI reale)
.\.venv312\Scripts\python.exe scripts\_e2e.py
#   sau pe CI/wrapper: ... scripts\_e2e.py --quiet   (o linie sumar, exit code = nr eșuate)

# 3) build canonic (vezi §1; venv curat, --clean --upx)
.\.venv312\Scripts\python.exe scripts\build.py --clean --upx

# 4) smoke pe exe-ul produs (PORT DIFERIT de live = 8000; ex. 8155)
$env:ANEVAR_PORT="8155"; $env:ANEVAR_NO_BROWSER="1"
.\dist\evaluare-anevar.exe   # apoi GET /api/status -> 200, plus câteva pagini
```

Criterii de oprire a release-ului (orice = STOP):
- Pytest: ≥1 fail sau coverage <90% (gate-ul `fail_under=90`).
- e2e: orice script `_check_*` sau `_pw_smoke.py` cu exit ≠ 0 (`_e2e.py` întoarce nr eșuate).
- Build: `BUILD EȘUAT.` sau exe lipsă în `dist/`.
- Smoke: `/api/status` ≠ 200 în 20s; sau una dintre paginile cheie ≠ 200.

Detalii și ce acoperă fiecare nivel: `docs/strategie-testare.md` (master test plan).

## 4. Prerechizite & note

- **Python 3.12** (build-ul de producție). Pentru Windows 7 vezi `docs/win7-build.md` (parcat).
- **UPX** (opțional, pentru `--upx`): binar portabil; pus pe PATH sau în `.upx/` (gitignored).
- **Windows Defender:** exclude folderul de build din scanarea real-time — altfel build-urile sunt
  mult mai lente (cauză frecventă a build-urilor de „24 min").
- **Server live (portul 8000):** `scripts/build.py` curăță folderele `%TEMP%/_MEI*` cu un *rename-guard*
  (sare peste cele în folosință) → rebuild-ul NU omoară instanța live. NU rula smoke-ul pe 8000.
- **Spec/excludes/UPX:** detalii în `evaluare-anevar.spec` (excludes măsurate pe `Analysis-00.toc`;
  UPX opt-in via `ANEVAR_UPX_DIR`).
