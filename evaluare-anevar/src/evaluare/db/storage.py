"""Persistenta locala a dosarelor de evaluare (SQLite)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from evaluare.models.report_context import ReportContext


class Storage:
    """Stocheaza dosare ReportContext ca JSON, cu un sumar pentru listare."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(self.db_path))

    def init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluari (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_nume TEXT NOT NULL,
                    valoare_finala TEXT NOT NULL,
                    context_json TEXT NOT NULL
                )
                """
            )

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
