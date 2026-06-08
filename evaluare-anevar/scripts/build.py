"""Build al executabilului (.exe).

Curăță artefactele de output, curăță folderele %TEMP%\\_MEI* rămase (care cauzau
„decompression -1"), rulează PyInstaller și raportează dimensiunea. Din rădăcina proiectului:

    python scripts/build.py            # build INCREMENTAL (reutilizează cache-ul de analiză -> rapid)
    python scripts/build.py --clean    # build COMPLET (șterge build/ + --clean -> reproductibil, lent)
    python scripts/build.py --upx      # + UPX pe mupdfcpp64.dll (-~3 MB, +~30s; cere upx.exe)
    python scripts/build.py --smoke    # + smoke test (pornește exe-ul, lovește /api/status)

Optimizare viteză (build-optim): implicit NU mai ștergem `build/` și NU mai pasăm `--clean`,
deci PyInstaller reutilizează cache-ul de analiză (Analysis-00.toc + PYZ). Câștigul e mare pe
medii cu multe pachete instalate (analiza domină — cazul build-urilor de ~24 min) și marginal pe
build-uri mici (acolo domină asamblarea binarelor). Foloseşte `--clean` cand schimbi spec-ul/
dependenţele sau vrei un build 100% reproductibil. Pe Windows, scoate folderul de build din
scanarea Defender (real-time) — e cauza frecventă a build-urilor foarte lente.
"""
from __future__ import annotations

import contextlib
import os
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


def curata(full: bool) -> None:
    # dist/ se șterge mereu (output proaspăt). build/ DOAR la --clean: altfel îl PĂSTRĂM,
    # ca PyInstaller să reutilizeze cache-ul de analiză (Analysis-00.toc/PYZ) -> build incremental.
    tinte = ("build", "dist") if full else ("dist",)
    for d in tinte:
        p = RADACINA / d
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
    # foldere temporare _MEI* rămase (corup arhiva la pornirea exe-ului).
    # Sărim peste cele ÎN FOLOSINȚĂ (ex. serverul live care rulează): pe Windows un folder cu fișiere
    # deschise nu poate fi redenumit -> testăm cu un rename. Așa build-ul NU mai ucide instanța live.
    temp = Path(tempfile.gettempdir())
    n = 0
    for mei in temp.glob("_MEI*"):
        liber = mei.with_name(mei.name + ".rm")
        try:
            mei.rename(liber)            # reușește DOAR dacă nimeni nu-l ține deschis
        except OSError:
            continue                     # în uz -> îl lăsăm intact (nu corupem exe-ul care rulează)
        shutil.rmtree(liber, ignore_errors=True)
        n += 1
    pastrat = "" if full else " (build/ păstrat pt cache)"
    print(f"Curățat: {', '.join(tinte)}/, {n} folder(e) _MEI temporare libere.{pastrat}")


def gaseste_upx() -> str | None:
    """Caută upx.exe: pe PATH, în env UPX_DIR, sau într-un `.upx/` local. Returnează folderul sau None."""
    pe_path = shutil.which("upx")
    if pe_path:
        return str(Path(pe_path).parent)
    env_dir = os.environ.get("UPX_DIR")
    if env_dir and (Path(env_dir) / "upx.exe").exists():
        return env_dir
    for cand in (RADACINA / ".upx").glob("**/upx.exe"):
        return str(cand.parent)
    return None


def build(full: bool, upx_dir: str | None = None) -> int:
    t0 = time.time()
    cmd = [sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm"]
    if full:
        cmd.append("--clean")            # invalidează cache-ul (build complet, reproductibil)
    env = os.environ.copy()
    if upx_dir:
        cmd += ["--upx-dir", upx_dir]
        env["ANEVAR_UPX_DIR"] = upx_dir  # spec-ul citește asta ca să activeze upx=True
        print(f"UPX activat (din {upx_dir}) — exe mai mic cu ~3 MB, build cu ~30s mai lent.")
    r = subprocess.run(cmd, cwd=RADACINA, env=env)
    if r.returncode != 0:
        print("BUILD EȘUAT.")
        return r.returncode
    if not EXE.exists():
        print("BUILD: exe-ul nu a fost creat.")
        return 1
    mb = EXE.stat().st_size / 1e6
    mod = "complet" if full else "incremental"
    print(f"\n✓ Build OK ({mod}) în {time.time() - t0:.0f}s — {EXE.name}: {mb:.0f} MB")
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
    full = "--clean" in sys.argv     # build complet (fără cache) doar la cerere explicită
    upx_dir = None
    if "--upx" in sys.argv:          # opt-in: comprimă mupdfcpp64.dll cu UPX (-~3 MB, +~30s)
        upx_dir = gaseste_upx()
        if upx_dir is None:
            print("AVERTISMENT: --upx cerut dar upx.exe nu a fost găsit (PATH / UPX_DIR / .upx/). "
                  "Continui FĂRĂ UPX.")
    curata(full)
    cod = build(full, upx_dir)
    if cod == 0 and "--smoke" in sys.argv:
        cod = smoke()
    return cod


if __name__ == "__main__":
    raise SystemExit(main())
