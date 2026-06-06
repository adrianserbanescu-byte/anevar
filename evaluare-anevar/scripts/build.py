"""Build reproductibil al executabilului (.exe).

Un singur pas: curăță artefactele vechi (inclusiv folderele %TEMP%\\_MEI* rămase de la
rulări anterioare, care cauzau „decompression -1"), rulează PyInstaller și raportează
dimensiunea. Rulează din rădăcina proiectului:

    python scripts/build.py            # build curat + raport dimensiune
    python scripts/build.py --smoke    # + smoke test (pornește exe-ul, lovește /api/status)
"""
from __future__ import annotations

import contextlib
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Consola Windows e cp1252 implicit -> print cu diacritice crapă. Forțăm UTF-8.
for _flux in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, ValueError):
        _flux.reconfigure(encoding="utf-8")

RADACINA = Path(__file__).resolve().parents[1]
SPEC = RADACINA / "evaluare-anevar.spec"
EXE = RADACINA / "dist" / "evaluare-anevar.exe"


def curata() -> None:
    for d in ("build", "dist"):
        p = RADACINA / d
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
    # foldere temporare _MEI* rămase (corup arhiva la pornirea exe-ului)
    temp = Path(tempfile.gettempdir())
    n = 0
    for mei in temp.glob("_MEI*"):
        try:
            shutil.rmtree(mei, ignore_errors=True)
            n += 1
        except OSError:
            pass
    print(f"Curățat: build/, dist/, {n} folder(e) _MEI temporare.")


def build() -> int:
    t0 = time.time()
    r = subprocess.run([sys.executable, "-m", "PyInstaller", str(SPEC),
                        "--noconfirm", "--clean"], cwd=RADACINA)
    if r.returncode != 0:
        print("BUILD EȘUAT.")
        return r.returncode
    if not EXE.exists():
        print("BUILD: exe-ul nu a fost creat.")
        return 1
    mb = EXE.stat().st_size / 1e6
    print(f"\n✓ Build OK în {time.time() - t0:.0f}s — {EXE.name}: {mb:.0f} MB")
    return 0


def smoke() -> int:
    import urllib.request
    print("Smoke: pornesc exe-ul…")
    proc = subprocess.Popen([str(EXE)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(20):
            time.sleep(1)
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/api/status", timeout=2) as resp:
                    if resp.status == 200:
                        print("✓ Smoke OK — /api/status răspunde 200.")
                        return 0
            except OSError:
                continue
        print("✗ Smoke: serverul nu a răspuns în 20s.")
        return 1
    finally:
        proc.terminate()


def main() -> int:
    curata()
    cod = build()
    if cod == 0 and "--smoke" in sys.argv:
        cod = smoke()
    return cod


if __name__ == "__main__":
    raise SystemExit(main())
