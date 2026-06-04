"""Configurare centralizata a jurnalizarii (logging).

Pana acum aplicatia nu avea logging: erorile prinse cu `except Exception` dispareau
fara urma, iar cand .exe-ul se comporta neasteptat pe teren nu exista niciun jurnal
de diagnoza. Acest modul ofera:

- `configure_logging()` - apelat o singura data la pornire (in __main__.main);
- in modul .exe (`sys.frozen`) scrie si intr-un fisier rotativ langa executabil;
- `get_logger(__name__)` - helper folosit in module pentru a obtine un logger.

Designul e minimal si fara dependinte externe (doar stdlib `logging`).
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
_configured = False


def _log_dir() -> Path | None:
    """Directorul pentru fisierul de jurnal: langa .exe cand e impachetat, altfel None."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return None


def configure_logging(level: int = logging.INFO, log_dir: Path | None = None) -> None:
    """Configureaza root logger-ul cu o consola si (in .exe) un fisier rotativ.

    Idempotent: apelurile repetate nu adauga handlere duplicate (util in teste).
    """
    global _configured
    if _configured:
        return

    root = logging.getLogger()
    root.setLevel(level)
    formatter = logging.Formatter(_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    target_dir = log_dir if log_dir is not None else _log_dir()
    if target_dir is not None:
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            fh = RotatingFileHandler(
                target_dir / "evaluare-anevar.log",
                maxBytes=1_000_000,
                backupCount=3,
                encoding="utf-8",
            )
            fh.setFormatter(formatter)
            root.addHandler(fh)
        except OSError:
            # Daca nu putem scrie fisierul (permisiuni), ramanem doar pe consola.
            root.warning("Nu s-a putut deschide fisierul de jurnal in %s", target_dir)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Logger pe modul. Nu forteaza configurarea (apelantii pot loga inainte de setup)."""
    return logging.getLogger(name)
