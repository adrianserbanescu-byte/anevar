"""Pornire: incarca config, deschide browserul, ruleaza serverul local."""
from __future__ import annotations

import threading
import webbrowser

import uvicorn

from evaluare.config import load_env_file, Settings
from evaluare.db.storage import Storage
from evaluare.web.app import create_app

HOST = "127.0.0.1"
PORT = 8000


def main() -> None:
    load_env_file(".env")
    settings = Settings.from_env()
    storage = Storage(settings.db_path)
    storage.init()
    app = create_app(storage=storage, client=settings.narrative_client())

    threading.Timer(1.0, lambda: webbrowser.open(f"http://{HOST}:{PORT}/")).start()
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
