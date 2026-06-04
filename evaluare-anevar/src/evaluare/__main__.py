"""Pornire: incarca config, deschide browserul, ruleaza serverul local."""
from __future__ import annotations

import socket
import sys
import threading
import time
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


def main() -> None:
    configure_logging()
    _incarca_env()
    settings = Settings.from_env()
    storage = Storage(settings.db_path)
    storage.init()
    app = create_app(storage=storage, client=settings.narrative_client())

    log.info("Pornire server pe http://%s:%s", HOST, PORT)
    threading.Thread(target=_deschide_browser_cand_e_gata, daemon=True).start()
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
