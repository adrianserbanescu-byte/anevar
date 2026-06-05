"""Pornire: incarca config, deschide browserul, ruleaza serverul local.

Robust pentru rulare pe ALT calculator (.exe):
- datele (baza SQLite, rapoarte, jurnal) se ancoreaza LANGA executabil, nu in
  directorul curent (care pe alt PC poate fi altul / read-only);
- daca folderul .exe-ului e read-only, cade pe %LOCALAPPDATA%\\EvaluareANEVAR;
- orice eroare la pornire se scrie in `eroare-pornire.log` si consola ramane
  deschisa, ca utilizatorul sa vada mesajul (nu mai e flash-and-close).
"""
from __future__ import annotations

import contextlib
import os
import socket
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path

import uvicorn

from evaluare.config import Settings, load_env_file
from evaluare.db.storage import Storage
from evaluare.logging_setup import configure_logging, get_logger
from evaluare.web.app import create_app

log = get_logger(__name__)

HOST = "127.0.0.1"
PORT = 8000


def _baza_scriere() -> Path:
    """Director writable pentru date/jurnal: langa .exe daca se poate, altfel %LOCALAPPDATA%."""
    baza = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path.cwd()
    try:
        proba = baza / ".scriere_test"
        proba.write_text("x", encoding="utf-8")
        proba.unlink()
        return baza
    except OSError:
        alt = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "EvaluareANEVAR"
        alt.mkdir(parents=True, exist_ok=True)
        return alt


def _incarca_env() -> None:
    """Incarca .env din directorul curent SI de langa executabil (cazul .exe)."""
    load_env_file(".env")                                   # directorul curent
    if getattr(sys, "frozen", False):                       # rulat ca .exe (PyInstaller)
        load_env_file(Path(sys.executable).parent / ".env")  # langa executabil


def _deschide_browser_cand_e_gata() -> None:
    """Deschide browserul DOAR dupa ce serverul accepta conexiuni (evita ERR_CONNECTION_REFUSED).

    Exe-ul onefile dezarhiveaza si porneste serverul in cateva secunde; un timer fix se deschide
    prea devreme. Asteptam ca portul sa fie disponibil (max ~30s).
    """
    for _ in range(120):
        try:
            with socket.create_connection((HOST, PORT), timeout=0.5):
                break
        except OSError:
            time.sleep(0.25)
    webbrowser.open(f"http://{HOST}:{PORT}/")


def _ruleaza(baza: Path) -> None:
    _incarca_env()
    # Ancoreaza datele langa .exe (absolut), daca nu sunt deja setate prin .env.
    os.environ.setdefault("DB_PATH", str(baza / "date" / "evaluari.db"))
    os.environ.setdefault("OUTPUT_DIR", str(baza / "date"))
    configure_logging(log_dir=baza)
    settings = Settings.from_env()
    # Avertisment: baza SQLite intr-un folder de sync cloud poate da „database locked”.
    cale = str(settings.db_path).lower()
    if any(m in cale for m in ("onedrive", "dropbox", "google drive", "googledrive")):
        log.warning("Baza de date e intr-un folder de sincronizare cloud (%s) — risc de "
                    "blocare a fisierului. Recomandat: muta aplicatia intr-un folder local.",
                    settings.db_path.parent)
    storage = Storage(settings.db_path)
    storage.init()
    try:
        copie = storage.backup(baza / "backups", keep=10)
        if copie is not None:
            log.info("Backup creat: %s", copie)
    except Exception as e:
        log.warning("Backup la pornire esuat: %s", e)
    app = create_app(storage=storage, client=settings.narrative_client())

    log.info("Pornire server pe http://%s:%s (date in %s)", HOST, PORT, baza)
    threading.Thread(target=_deschide_browser_cand_e_gata, daemon=True).start()
    uvicorn.run(app, host=HOST, port=PORT)


def main() -> None:
    baza = _baza_scriere()
    try:
        _ruleaza(baza)
    except Exception:
        tb = traceback.format_exc()
        with contextlib.suppress(OSError):
            (baza / "eroare-pornire.log").write_text(tb, encoding="utf-8")
        sys.stderr.write("\n=== EROARE LA PORNIRE ===\n" + tb + "\n")
        sys.stderr.write(f"Detalii salvate in: {baza / 'eroare-pornire.log'}\n")
        if getattr(sys, "frozen", False):
            with contextlib.suppress(EOFError):
                input("\nApasa Enter pentru a inchide fereastra...")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
