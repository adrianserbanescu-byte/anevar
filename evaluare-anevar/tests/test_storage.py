from decimal import Decimal

from evaluare.db.storage import Storage
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.report_context import ReportContext
from evaluare.models.results import ReconciledResult


def _ctx() -> ReportContext:
    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. 1", numar_cadastral="123",
        carte_funciara="CF123", evaluator_nume="Maria", evaluator_legitimatie="1",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    return ReportContext(
        meta=meta, land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("100"), acd=Decimal("120"), an_referinta=2025),
        reconciled=ReconciledResult(valoare_finala=Decimal("300000"), metoda_selectata="cost"),
    )


def test_save_and_load_roundtrip(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    eid = db.save(_ctx())
    loaded = db.load(eid)
    assert loaded.meta.client_nume == "Ion Popescu"
    assert loaded.reconciled.valoare_finala == Decimal("300000")


def test_list_returns_saved_summaries(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    db.save(_ctx())
    db.save(_ctx())
    rows = db.list()
    assert len(rows) == 2
    assert all(r["client_nume"] == "Ion Popescu" for r in rows)
    assert all("valoare_finala" in r for r in rows)


def test_load_missing_raises(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    import pytest
    with pytest.raises(KeyError):
        db.load(9999)


def test_init_seteaza_versiunea_de_schema(tmp_path):
    import sqlite3

    from evaluare.db.storage import SCHEMA_VERSION
    db = Storage(tmp_path / "test.db")
    db.init()
    db.init()  # idempotent
    with sqlite3.connect(str(db.db_path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION


def test_backup_creeaza_copie_si_pastreaza_ultimele(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    db.save(_ctx())
    bdir = tmp_path / "backups"
    copie = db.backup(bdir, keep=2)
    assert copie is not None and copie.exists()
    # backup-ul e o bază validă cu același dosar
    restaurat = Storage(copie)
    assert len(restaurat.list()) == 1


def test_backup_fara_baza_returneaza_none(tmp_path):
    db = Storage(tmp_path / "inexistent.db")
    assert db.backup(tmp_path / "backups") is None
