"""Persistenta locala a dosarelor de evaluare (SQLite).

Include migrare de schema (PRAGMA user_version) si backup consistent (API SQLite),
ca datele evaluatorului sa fie protejate intre versiuni si la coruperi accidentale.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from evaluare.models.report_context import ReportContext

# Versiunea curenta a schemei. Fiecare intrare = lista de instructiuni SQL pentru a
# ajunge la acea versiune de la cea anterioara. Adauga versiuni noi la coada.
SCHEMA_VERSION = 2
_MIGRATIONS: dict[int, list[str]] = {
    1: [
        """
        CREATE TABLE IF NOT EXISTS evaluari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_nume TEXT NOT NULL,
            valoare_finala TEXT NOT NULL,
            context_json TEXT NOT NULL
        )
        """
    ],
    2: [
        # Coada de anunturi importate din extensia de browser (persistenta, dedup pe URL).
        """
        CREATE TABLE IF NOT EXISTS import_anunturi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sursa_url TEXT NOT NULL UNIQUE,
            anunt_json TEXT NOT NULL,
            creat_la TEXT NOT NULL
        )
        """
    ],
}


class Storage:
    """Stocheaza dosare ReportContext ca JSON, cu un sumar pentru listare."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(self.db_path))

    def init(self) -> None:
        """Aplica migrarile lipsa pana la SCHEMA_VERSION (idempotent)."""
        with self._connect() as conn:
            ver = conn.execute("PRAGMA user_version").fetchone()[0]
            for v in range(ver + 1, SCHEMA_VERSION + 1):
                for stmt in _MIGRATIONS[v]:
                    conn.executescript(stmt)
                conn.execute(f"PRAGMA user_version = {v}")  # int controlat, nu input

    def backup(self, backups_dir: Path | str, keep: int = 10) -> Path | None:
        """Copie consistenta a bazei intr-un fisier datat; pastreaza ultimele `keep`."""
        if not self.db_path.exists():
            return None
        backups_dir = Path(backups_dir)
        backups_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = backups_dir / f"evaluari-{stamp}.db"
        with self._connect() as src, sqlite3.connect(str(dest)) as dst:
            src.backup(dst)                                  # API SQLite = copie consistenta
        copii = sorted(backups_dir.glob("evaluari-*.db"))
        for old in copii[:-keep] if keep > 0 else []:
            old.unlink(missing_ok=True)
        return dest

    def save(self, ctx: ReportContext) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO evaluari (client_nume, valoare_finala, context_json) "
                "VALUES (?, ?, ?)",
                (
                    ctx.meta.client_nume,
                    str(ctx.reconciled.valoare_finala),
                    ctx.model_dump_json(),
                ),
            )
            return int(cur.lastrowid)

    def load(self, eid: int) -> ReportContext:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT context_json FROM evaluari WHERE id = ?", (eid,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Dosar inexistent: {eid}")
        return ReportContext.model_validate_json(row[0])

    def list(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, client_nume, valoare_finala FROM evaluari ORDER BY id DESC"
            ).fetchall()
        return [
            {"id": r[0], "client_nume": r[1], "valoare_finala": r[2]} for r in rows
        ]

    # ── Coada de anunturi importate din extensia de browser ──────────────────────
    def adauga_anunt_importat(self, anunt: dict) -> int:
        """Adauga un anunt in coada (dedup pe sursa_url). Returneaza nr. total din coada."""
        url = anunt.get("sursa_url") or ""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO import_anunturi (sursa_url, anunt_json, creat_la) "
                "VALUES (?, ?, ?)",
                (url, json.dumps(anunt, ensure_ascii=False),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            return int(conn.execute("SELECT COUNT(*) FROM import_anunturi").fetchone()[0])

    def listeaza_anunturi_importate(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT anunt_json FROM import_anunturi ORDER BY id"
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def sterge_anunturi_importate(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM import_anunturi")
