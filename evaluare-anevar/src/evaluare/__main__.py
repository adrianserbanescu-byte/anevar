"""Pornire: incarca config, deschide browserul, ruleaza serverul local."""
from __future__ import annotations

import sys
import threading
import webbrowser
from pathlib import Path

import uvicorn

from evaluare.config import load_env_file, Settings
from evaluare.db.storage import Storage
from evaluare.web.app import create_app

HOST = "127.0.0.1"
PORT = 8000


def _incarca_env() -> None:
    """Incarca .env din directorul curent SI de langa executabil (cazul .exe)."""
    load_env_file(".env")                                   # directorul curent
    if getattr(sys, "frozen", False):                       # rulat ca .exe (PyInstaller)
        load_env_file(Path(sys.executable).parent / ".env")  # langa executabil


def main() -> None:
    _incarca_env()
    settings = Settings.from_env()
    storage = Storage(settings.db_path)
    storage.init()
    app = create_app(storage=storage, client=settings.narrative_client())

    threading.Timer(1.0, lambda: webbrowser.open(f"http://{HOST}:{PORT}/")).start()
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
