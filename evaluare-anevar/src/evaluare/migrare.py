"""Migrare ne-distructivă SQLite (UI vechi) -> foldere (UI nou) — ADR-002, Faza 2.

Logica e aici (testabilă); CLI-ul e în `scripts/migreaza_sqlite_foldere.py`.
NU șterge nimic din SQLite; marchează coloana `migrated_uuid` (reversibil) ca să nu re-migreze.
Skip-pe-eroare: un dosar prost-format nu blochează lotul. Rulează local (offline), fără I/O extern.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from evaluare import cont as cont_mod
from evaluare import dosare_fs as fs
from evaluare.db.storage import Storage


def _db_path() -> Path:
    return Path(os.environ.get("DB_PATH")
                or (Path(os.environ.get("OUTPUT_DIR") or "date") / "evaluari.db"))


def _folder_vechi(eid: int) -> Path:
    return Path(os.environ.get("OUTPUT_DIR") or "date") / "dosare" / str(eid)


def _migrated_uuid(db: Path, eid: int) -> str | None:
    with sqlite3.connect(db) as c:
        cols = [r[1] for r in c.execute("PRAGMA table_info(evaluari)")]
        if "migrated_uuid" not in cols:
            return None
        r = c.execute("SELECT migrated_uuid FROM evaluari WHERE id=?", (eid,)).fetchone()
    return r[0] if r else None


def migreaza(apply: bool = False) -> dict:
    """Migrează dosarele din SQLite în foldere. `apply=False` = dry-run (raportează, nu scrie).

    Întoarce `{db, total, migrate, sarite, jurnal}`. Idempotent: rândurile deja migrate se sar.
    """
    db = _db_path()
    if not db.exists():
        return {"db": str(db), "total": 0, "migrate": 0, "sarite": 0, "jurnal": ["Nicio bază SQLite."]}
    st = Storage(db)
    st.init()
    cont = cont_mod.incarca_cont() or {}
    legit, nume_ev = cont.get("legitimatie", "migrat"), cont.get("nume", "(migrat din SQLite)")
    if apply:
        with sqlite3.connect(db) as c:   # asigură coloana de marcaj (reversibil, ne-distructiv)
            if "migrated_uuid" not in [r[1] for r in c.execute("PRAGMA table_info(evaluari)")]:
                c.execute("ALTER TABLE evaluari ADD COLUMN migrated_uuid TEXT")
    randuri = st.list()
    jurnal: list[str] = []
    migrate = sarite = 0
    for r in randuri:
        eid = r["id"]
        try:
            if _migrated_uuid(db, eid):
                jurnal.append(f"[{eid}] {r['nume']}: deja migrat -> sărit")
                continue
            wiz = st.get_dosar(eid).get("wizard")
            if not wiz:
                jurnal.append(f"[{eid}] {r['nume']}: fără wizard_json -> SĂRIT")
                sarite += 1
                continue
            fv = _folder_vechi(eid)
            nr = len(list(fv.glob("raport-*.docx"))) if fv.exists() else 0
            if not apply:
                jurnal.append(f"[{eid}] {r['nume']}: s-ar crea folder + {nr} rapoarte")
                migrate += 1
                continue
            uid = fs.creeaza(legit, nume_ev, wiz)
            if fv.exists():
                for doc in sorted(fv.glob("raport-*.docx")):
                    fs.adauga_versiune_docx(uid, doc, tip="import")
            with sqlite3.connect(db) as c:
                c.execute("UPDATE evaluari SET migrated_uuid=? WHERE id=?", (uid, eid))
            jurnal.append(f"[{eid}] {r['nume']} -> {uid[:8]} ({nr} rapoarte)")
            migrate += 1
        except Exception as e:  # noqa: BLE001 — skip-pe-eroare: un dosar prost nu blochează lotul
            jurnal.append(f"[{eid}] {r['nume']}: EROARE {e} -> SĂRIT")
            sarite += 1
    return {"db": str(db), "total": len(randuri), "migrate": migrate, "sarite": sarite, "jurnal": jurnal}
