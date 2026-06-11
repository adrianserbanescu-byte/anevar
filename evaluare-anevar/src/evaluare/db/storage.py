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
SCHEMA_VERSION = 4
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
    3: [
        # Feedback de la testeri/evaluator (local, offline). Citit din baza returnata.
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creat_la TEXT NOT NULL,
            pagina TEXT,
            url TEXT,
            sentiment TEXT,
            mesaj TEXT,
            tester TEXT
        )
        """
    ],
    4: [
        # Dosare salvate: nume editabil + data crearii + snapshot câmpuri wizard (re-deschidere).
        "ALTER TABLE evaluari ADD COLUMN nume TEXT",
        "ALTER TABLE evaluari ADD COLUMN creat_la TEXT",
        "ALTER TABLE evaluari ADD COLUMN wizard_json TEXT",
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
                    try:
                        conn.executescript(stmt)
                    except sqlite3.OperationalError as e:
                        # F-5 (crash-recovery): crash INTRE un ALTER TABLE aplicat si avansarea
                        # user_version -> la urmatorul start re-rulam ALTER-ul pe o coloana deja
                        # existenta -> 'duplicate column name' -> app-ul NU mai pornea. Coloana
                        # deja prezenta = migrarea era aplicata -> sigur de ignorat (CREATE TABLE
                        # e deja IF NOT EXISTS). Orice alta eroare ramane fatala.
                        if "duplicate column name" not in str(e).lower():
                            raise
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

    def save(self, ctx: ReportContext, nume: str | None = None) -> int:
        # Nume implicit: „Client — cadastral" (editabil ulterior).
        nume = nume or " — ".join(
            x for x in (ctx.meta.client_nume, ctx.meta.numar_cadastral) if x) or "Dosar"
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO evaluari (client_nume, valoare_finala, context_json, nume, creat_la) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    ctx.meta.client_nume,
                    str(ctx.reconciled.valoare_finala),
                    ctx.model_dump_json(),
                    nume,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            assert cur.lastrowid is not None  # setat după un INSERT reușit
            return int(cur.lastrowid)

    def redenumeste(self, eid: int, nume: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE evaluari SET nume = ? WHERE id = ?", (nume, eid))

    def sterge(self, eid: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM evaluari WHERE id = ?", (eid,))

    def set_wizard_snapshot(self, eid: int, snapshot: dict) -> None:
        """Reține câmpurile brute ale wizardului pentru re-deschiderea dosarului."""
        with self._connect() as conn:
            conn.execute("UPDATE evaluari SET wizard_json = ? WHERE id = ?",
                         (json.dumps(snapshot, ensure_ascii=False), eid))

    def get_dosar(self, eid: int) -> dict:
        """Datele pentru re-deschidere: nume + snapshot wizard (sau None)."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT nume, wizard_json FROM evaluari WHERE id = ?", (eid,)).fetchone()
        if row is None:
            raise KeyError(f"Dosar inexistent: {eid}")
        return {"id": eid, "nume": row[0],
                "wizard": json.loads(row[1]) if row[1] else None}

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
                "SELECT id, client_nume, valoare_finala, nume, creat_la "
                "FROM evaluari ORDER BY id DESC"
            ).fetchall()
        return [
            {"id": r[0], "client_nume": r[1], "valoare_finala": r[2],
             "nume": r[3], "creat_la": r[4]} for r in rows
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

    def sterge_anunt_importat(self, sursa_url: str) -> int:
        """Sterge un singur anunt din coada dupa URL. Returneaza nr. ramas in coada."""
        with self._connect() as conn:
            conn.execute("DELETE FROM import_anunturi WHERE sursa_url = ?", (sursa_url,))
            return int(conn.execute("SELECT COUNT(*) FROM import_anunturi").fetchone()[0])

    # ── Feedback de la testeri (local, offline) ──────────────────────────────────
    def adauga_feedback(self, fb: dict) -> int:
        """Salveaza un feedback. Returneaza nr. total de feedback-uri."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO feedback (creat_la, pagina, url, sentiment, mesaj, tester) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fb.get("pagina"), fb.get("url"),
                 fb.get("sentiment"), fb.get("mesaj"), fb.get("tester")),
            )
            return int(conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0])

    def listeaza_feedback(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, creat_la, pagina, url, sentiment, mesaj, tester "
                "FROM feedback ORDER BY id DESC"
            ).fetchall()
        chei = ("id", "creat_la", "pagina", "url", "sentiment", "mesaj", "tester")
        return [dict(zip(chei, r, strict=True)) for r in rows]
