"""Runner unic pentru harness-ul end-to-end (Playwright).

Pornește un server izolat pe :8765 (vezi `_serve_test.py` — DB+date temporare, fără AI),
rulează toate scripturile `_pw_smoke.py` + `_check_*.py` ca subprocese (exit 0 = OK,
exit ≠ 0 = FAIL), agreg rezultatele și raportează. Exit cod = numărul de scripturi eșuate.

Folosire:
    python scripts/_e2e.py                    # toată suita e2e (pornește serverul, rulează tot, oprește serverul)
    python scripts/_e2e.py xss grid           # doar scripturile al căror nume conține "xss" sau "grid"
    python scripts/_e2e.py --no-server URL    # rulează contra unui server deja pornit (ex. http://127.0.0.1:8000)
    python scripts/_e2e.py --list             # listează scripturile descoperite și ies

Owner: sesiunea D (Rol 2 — framework testare). NU modifică testele individuale; doar le
agreg într-un runner reproductibil.
"""
from __future__ import annotations

import contextlib
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
SCRIPTS = RADACINA / "scripts"
SERVE_TEST = SCRIPTS / "_serve_test.py"
PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"
TIMEOUT_BOOT = 20            # secunde max să aștept ca serverul să răspundă
TIMEOUT_SCRIPT = 90          # secunde max per script (Playwright + boot browser)

# UTF-8 pe consola Windows (cp1252 ar crăpa la diacritice).
for _f in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, ValueError):
        _f.reconfigure(encoding="utf-8")


def descopera_scripturi(filtre: list[str]) -> list[Path]:
    """`_pw_smoke.py` + toate `_check_*.py`. Cu filtre, păstrează doar potrivirile (case-insensitive)."""
    toate = [SCRIPTS / "_pw_smoke.py"] + sorted(SCRIPTS.glob("_check_*.py"))
    toate = [f for f in toate if f.exists()]
    if not filtre:
        return toate
    f_low = [x.lower() for x in filtre]
    return [f for f in toate if any(x in f.name.lower() for x in f_low)]


def port_liber(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def asteapta_server(timeout: int) -> bool:
    """Așteaptă ca portul să accepte conexiuni (server pornit)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", PORT)) == 0:
                return True
        time.sleep(0.3)
    return False


def porneste_server() -> subprocess.Popen:
    if not port_liber(PORT):
        raise SystemExit(f"Portul {PORT} e ocupat — închide procesul care îl folosește, "
                         f"sau rulează cu --no-server <URL>.")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(RADACINA / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    print(f"→ Pornesc serverul de test ({SERVE_TEST.name}) pe :{PORT}…", flush=True)
    proc = subprocess.Popen(
        [sys.executable, str(SERVE_TEST)],
        cwd=RADACINA, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not asteapta_server(TIMEOUT_BOOT):
        proc.terminate()
        raise SystemExit(f"Serverul nu a răspuns pe {BASE} în {TIMEOUT_BOOT}s.")
    print(f"✓ Server gata: {BASE}", flush=True)
    return proc


def ruleaza_script(script: Path, baza: str) -> tuple[bool, float, str]:
    """Rulează un script; returnează (ok, durata_s, ultimele_linii_stdout/stderr)."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(RADACINA / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    t0 = time.time()
    try:
        r = subprocess.run(
            [sys.executable, str(script), baza],
            cwd=RADACINA, env=env, capture_output=True, text=True,
            timeout=TIMEOUT_SCRIPT, encoding="utf-8", errors="replace",
        )
        dt = time.time() - t0
        out = (r.stdout or "") + (r.stderr or "")
        ultim = "\n".join(out.strip().splitlines()[-3:])
        return r.returncode == 0, dt, ultim
    except subprocess.TimeoutExpired:
        return False, time.time() - t0, f"TIMEOUT după {TIMEOUT_SCRIPT}s"


def main(argv: list[str]) -> int:
    if "--list" in argv:
        for f in descopera_scripturi([]):
            print(f.name)
        return 0

    # --no-server <URL>: nu pornim server propriu, folosim unul existent.
    baza = BASE
    server_extern = False
    if "--no-server" in argv:
        i = argv.index("--no-server")
        if i + 1 >= len(argv):
            print("--no-server cere un URL după.", file=sys.stderr)
            return 2
        baza = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
        server_extern = True
        print(f"→ Folosesc serverul extern: {baza}", flush=True)

    filtre = [a for a in argv if not a.startswith("--")]
    scripturi = descopera_scripturi(filtre)
    if not scripturi:
        print(f"Nicio potrivire pentru filtrele: {filtre}", file=sys.stderr)
        return 2

    proc = None if server_extern else porneste_server()
    try:
        rezultate: list[tuple[Path, bool, float, str]] = []
        print(f"\n=== Rulez {len(scripturi)} script(uri) e2e ===", flush=True)
        for sc in scripturi:
            print(f"\n→ {sc.name}", flush=True)
            ok, dt, ultim = ruleaza_script(sc, baza)
            marca = "✓ OK" if ok else "✗ FAIL"
            print(f"  {marca}  ({dt:.1f}s)")
            if not ok and ultim:
                print(f"  ultimele linii:\n    " + ultim.replace("\n", "\n    "))
            rezultate.append((sc, ok, dt, ultim))
    finally:
        if proc is not None:
            proc.terminate()
            with contextlib.suppress(Exception):
                proc.wait(timeout=5)

    trecute = sum(1 for _, ok, _, _ in rezultate if ok)
    esuate = len(rezultate) - trecute
    total_dt = sum(dt for _, _, dt, _ in rezultate)
    print(f"\n=== {trecute}/{len(rezultate)} OK · {esuate} FAIL · {total_dt:.1f}s total ===")
    if esuate:
        print("ESEC:")
        for sc, ok, _, _ in rezultate:
            if not ok:
                print(f"  - {sc.name}")
    return esuate                            # exit code = nr. eșuate (0 = tot OK)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
