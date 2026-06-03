"""Store separat AML (tipping-off) — persistenta drafturilor RTS/RTN, retentie 5 ani."""
from evaluare.aml.store import StoreAML


def test_salveaza_si_listeaza(tmp_path):
    store = StoreAML(tmp_path / "aml")
    r = store.salveaza("rts", {"motiv": "test"}, "2026-06-03")
    assert r["id"] == 1
    assert r["tip"] == "rts"
    assert r["data_retentie"] == "2031-06-03"   # +5 ani
    toate = store.listeaza("rts")
    assert len(toate) == 1
    assert toate[0]["continut"]["motiv"] == "test"


def test_id_incremental(tmp_path):
    store = StoreAML(tmp_path / "aml")
    store.salveaza("rtn", {"a": 1}, "2026-06-03")
    r2 = store.salveaza("rtn", {"a": 2}, "2026-06-04")
    assert r2["id"] == 2


def test_separare_pe_tip(tmp_path):
    store = StoreAML(tmp_path / "aml")
    store.salveaza("rts", {"x": 1}, "2026-06-03")
    store.salveaza("rtn", {"y": 1}, "2026-06-03")
    assert len(store.listeaza("rts")) == 1
    assert len(store.listeaza("rtn")) == 1
    assert len(store.listeaza()) == 2


def test_citeste(tmp_path):
    store = StoreAML(tmp_path / "aml")
    store.salveaza("rts", {"motiv": "abc"}, "2026-06-03")
    assert store.citeste("rts", 1)["continut"]["motiv"] == "abc"


def test_store_e_separat_de_dosar(tmp_path):
    # directorul AML e distinct de baza de date a evaluarilor
    db = tmp_path / "evaluari.db"
    db.write_text("fake")
    store = StoreAML(tmp_path / "aml_confidential")
    store.salveaza("rts", {"x": 1}, "2026-06-03")
    assert (tmp_path / "aml_confidential").is_dir()
    assert not any("rts" in p.name for p in [db])
