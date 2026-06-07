"""ADR-002: migrare ne-distructivă SQLite -> foldere."""
from __future__ import annotations

import sqlite3

from evaluare import dosare_fs as fs
from evaluare.db.storage import Storage
from evaluare.migrare import migreaza

_WIZ = '{"scop":"garantare","tip_proprietate":"casa","nume_client":"Pop","id_client":"D1"}'


def _seed(tmp_path, monkeypatch, wizard=_WIZ):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    monkeypatch.setenv("DB_PATH", str(tmp_path / "date" / "evaluari.db"))
    (tmp_path / "date").mkdir(parents=True, exist_ok=True)
    db = tmp_path / "date" / "evaluari.db"
    Storage(db).init()
    with sqlite3.connect(db) as c:
        c.execute("INSERT INTO evaluari (client_nume, valoare_finala, context_json, nume, wizard_json) "
                  "VALUES (?,?,?,?,?)", ("Pop", "100000", "{}", "1_Pop_casa", wizard))
    return db


def test_dry_run_nu_scrie(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    rez = migreaza(apply=False)
    assert rez["total"] == 1 and rez["migrate"] == 1 and rez["sarite"] == 0
    # dry-run: niciun folder-dosar creat
    assert not fs.baza().exists() or not any(p.is_dir() for p in fs.baza().iterdir())


def test_apply_creeaza_folder_si_e_idempotent(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    rez = migreaza(apply=True)
    assert rez["migrate"] == 1
    folders = [p for p in fs.baza().iterdir() if p.is_dir() and (p / "dosar.json").exists()]
    assert len(folders) == 1
    # re-rulare: deja migrat -> nu re-migrează (marcaj migrated_uuid)
    assert migreaza(apply=True)["migrate"] == 0


def test_skip_pe_dosar_fara_wizard(tmp_path, monkeypatch):
    db = _seed(tmp_path, monkeypatch)
    with sqlite3.connect(db) as c:   # rând fără wizard_json
        c.execute("INSERT INTO evaluari (client_nume, valoare_finala, context_json, nume) "
                  "VALUES (?,?,?,?)", ("Fara", "0", "{}", "2_Fara"))
    rez = migreaza(apply=True)
    assert rez["migrate"] == 1 and rez["sarite"] == 1   # unul migrat, unul sărit (fără wizard)
