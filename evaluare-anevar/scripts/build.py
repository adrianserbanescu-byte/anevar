"""Build al executabilului (.exe).

Curăță artefactele de output, curăță folderele %TEMP%\\_MEI* rămase (care cauzau
„decompression -1"), rulează PyInstaller și raportează dimensiunea. Din rădăcina proiectului:

    python scripts/build.py            # build INCREMENTAL (reutilizează cache-ul de analiză -> rapid)
    python scripts/build.py --clean    # build COMPLET (șterge build/ + --clean -> reproductibil, lent)
    python scripts/build.py --upx      # + UPX pe mupdfcpp64.dll (-~3 MB, +~30s; cere upx.exe)
    python scripts/build.py --smoke    # + smoke test (pornește exe-ul, lovește /api/status)
    python scripts/build.py --smoke-offline   # + smoke offline (5 rute locale; nu apeleaza extern)

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


def _seteaza_reproductibilitate(env: dict) -> None:
    """Setează SOURCE_DATE_EPOCH + PYTHONHASHSEED pt build PyInstaller reproductibil bit-by-bit.

    - PYTHONHASHSEED fixat → ordinea dict-urilor/set-urilor pe care PyInstaller le serializează e stabilă.
    - SOURCE_DATE_EPOCH = timpul commit-ului HEAD (UNIX s) → timestamp-urile incluse în PE deterministe.
    Honor pentru valori deja prezente în env (CI poate suprascrie); fallback: HEAD-ul git, apoi 0.
    """
    env.setdefault("PYTHONHASHSEED", "0")
    if "SOURCE_DATE_EPOCH" not in env:
        try:                                # timpul commit-ului HEAD = ancoră stabilă, per-commit deterministă
            r = subprocess.run(["git", "-C", str(RADACINA), "log", "-1", "--format=%ct"],
                               capture_output=True, text=True, timeout=5, check=True)
            ts = r.stdout.strip()
            env["SOURCE_DATE_EPOCH"] = ts if ts else "0"
        except (subprocess.SubprocessError, OSError):
            env["SOURCE_DATE_EPOCH"] = "0"


def build(full: bool, upx_dir: str | None = None) -> int:
    t0 = time.time()
    cmd = [sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm"]
    if full:
        cmd.append("--clean")            # invalidează cache-ul (build complet, reproductibil)
    env = os.environ.copy()
    _seteaza_reproductibilitate(env)     # PYTHONHASHSEED + SOURCE_DATE_EPOCH (vezi docstring)
    if upx_dir:
        cmd += ["--upx-dir", upx_dir]
        env["ANEVAR_UPX_DIR"] = upx_dir  # spec-ul citește asta ca să activeze upx=True
        print(f"UPX activat (din {upx_dir}) — exe mai mic cu ~3 MB, build cu ~30s mai lent.")
    print(f"Reproductibilitate: PYTHONHASHSEED={env['PYTHONHASHSEED']} SOURCE_DATE_EPOCH={env['SOURCE_DATE_EPOCH']}")
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


def smoke_offline() -> int:
    """Verifica ca exe-ul booteaza si raspunde la rute LOCALE fara apel extern (offline-friendly).

    Nu apeleaza endpoint-uri care fac request-uri externe la pornire (BNR/ANEVAR/AI). Cele lazy
    (lovite la cerere) ramân OK; importul lor pe boot ar pica daca DNS/network e taiat. Aici
    portul, host-ul si rutele sunt strict locale.
    """
    import urllib.error
    import urllib.request

    port = int(os.environ.get("ANEVAR_PORT", "8155"))
    base = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["ANEVAR_PORT"] = str(port)
    env["ANEVAR_NO_BROWSER"] = "1"
    print(f"Smoke offline: pornesc exe-ul pe port {port}…")
    proc = subprocess.Popen([str(EXE)], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(20):
            time.sleep(1)
            with contextlib.suppress(OSError):
                with urllib.request.urlopen(f"{base}/api/status", timeout=2) as r:
                    if r.status == 200:
                        break
        else:
            print("✗ Smoke offline: serverul nu a raspuns in 20s.")
            return 1
        rute = ("/api/status", "/", "/incepe", "/dosare", "/documente")
        esuate = []
        for r in rute:
            try:
                with urllib.request.urlopen(f"{base}{r}", timeout=5) as resp:
                    cod = resp.status
            except urllib.error.HTTPError as e:
                cod = e.code
            except OSError:
                cod = 0
            marca = "✓" if 200 <= cod < 400 else "✗"
            print(f"  {marca} {cod}  {r}")
            if not (200 <= cod < 400):
                esuate.append(r)
        if esuate:
            print(f"✗ Smoke offline: {len(esuate)} ruta(e) au esuat: {esuate}")
            return 1
        print("✓ Smoke offline OK — flux local complet fara apel extern.")
        return 0
    finally:
        proc.terminate()


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
    if cod == 0 and "--smoke-offline" in sys.argv:
        cod = smoke_offline()
    return cod


if __name__ == "__main__":
    raise SystemExit(main())
