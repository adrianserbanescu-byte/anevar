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


def test_dosar_nume_implicit_si_redenumire(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    eid = db.save(_ctx())                                   # nume implicit „Client — cadastral"
    row = db.list()[0]
    assert row["id"] == eid
    assert row["nume"] == "Ion Popescu — 123"
    assert row["creat_la"]                                  # are timestamp
    db.redenumeste(eid, "Casa Breaza – garantare BT")
    assert db.list()[0]["nume"] == "Casa Breaza – garantare BT"


def test_dosar_nume_explicit_si_stergere(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    eid = db.save(_ctx(), nume="Dosar special")
    assert db.list()[0]["nume"] == "Dosar special"
    db.sterge(eid)
    assert db.list() == []


def test_migrare_v3_la_v4_adauga_coloane(tmp_path):
    import sqlite3

    # baza veche la v3 (fara nume/creat_la in evaluari)
    p = tmp_path / "v3.db"
    with sqlite3.connect(str(p)) as conn:
        conn.execute("CREATE TABLE evaluari (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                     "client_nume TEXT, valoare_finala TEXT, context_json TEXT)")
        conn.execute("PRAGMA user_version = 3")
    db = Storage(p)
    db.init()                                              # aplica migrarea 4
    db.save(_ctx(), nume="dupa migrare")
    assert db.list()[0]["nume"] == "dupa migrare"


def test_migrare_idempotenta_dupa_crash_inainte_de_user_version(tmp_path):
    import sqlite3

    from evaluare.db.storage import SCHEMA_VERSION

    # F-5 (crash-recovery): ALTER-urile v4 au rulat, dar crash INAINTE de PRAGMA user_version=4 ->
    # la urmatorul start init() re-ruleaza ALTER pe coloane deja existente. Inainte de fix:
    # OperationalError 'duplicate column name: nume' -> APP-UL NU MAI PORNEA (reparare manuala DB).
    p = tmp_path / "crash.db"
    Storage(p).init()                                      # schema completa v4...
    with sqlite3.connect(str(p)) as conn:
        conn.execute("PRAGMA user_version = 3")            # ...dar versiunea NU a apucat sa avanseze
    db = Storage(p)
    db.init()                                              # nu mai crapa: reia si avanseaza versiunea
    with sqlite3.connect(str(p)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    db.save(_ctx(), nume="dupa recuperare")                # baza ramane functionala
    assert db.list()[0]["nume"] == "dupa recuperare"


def test_coada_import_persista_si_deduplica(tmp_path):
    db = Storage(tmp_path / "test.db")
    db.init()
    assert db.listeaza_anunturi_importate() == []
    n = db.adauga_anunt_importat({"sursa_url": "https://x.ro/1", "pret": "150000"})
    assert n == 1
    # acelasi URL -> ignorat (dedup)
    n2 = db.adauga_anunt_importat({"sursa_url": "https://x.ro/1", "pret": "999"})
    assert n2 == 1
    db.adauga_anunt_importat({"sursa_url": "https://x.ro/2", "pret": "200000"})
    # persista: o noua instanta Storage pe acelasi fisier vede ambele anunturi
    db2 = Storage(tmp_path / "test.db")
    lista = db2.listeaza_anunturi_importate()
    assert len(lista) == 2
    assert lista[0]["pret"] == "150000"  # primul ramane cel original, nu suprascris
    db2.sterge_anunturi_importate()
    assert db.listeaza_anunturi_importate() == []


def test_migrare_v1_la_v2_adauga_tabela_import(tmp_path):
    import sqlite3

    # simuleaza o baza veche la versiunea 1 (doar tabela evaluari)
    p = tmp_path / "vechi.db"
    with sqlite3.connect(str(p)) as conn:
        conn.executescript(
            "CREATE TABLE evaluari (id INTEGER PRIMARY KEY, client_nume TEXT, "
            "valoare_finala TEXT, context_json TEXT)"
        )
        conn.execute("PRAGMA user_version = 1")
    # init aplica migrarea lipsa -> coada de import devine utilizabila
    db = Storage(p)
    db.init()
    assert db.adauga_anunt_importat({"sursa_url": "https://x.ro/3", "pret": "1"}) == 1
