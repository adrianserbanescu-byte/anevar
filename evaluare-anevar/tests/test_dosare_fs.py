"""Stocarea pe foldere (sursa de adevăr) + contul local."""
from __future__ import annotations

import pytest


@pytest.fixture
def baza(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    return tmp_path


def _wizard(**extra):
    w = {"scop": "garantare", "tip_proprietate": "casa", "nume_client": "Pop",
         "id_client": "D001", "au": "100", "acd": "120"}
    w.update(extra)
    return w


def test_cont_creare_si_incarcare(baza):
    from evaluare import cont
    assert cont.incarca_cont() is None
    c = cont.salveaza_cont("Adi S", "8717", ["id_client", "nume_client", "scop", "tip_proprietate"])
    assert c["nume"] == "Adi S" and c["legitimatie"] == "8717"
    assert cont.incarca_cont()["format_dosar"][0] == "id_client"


def test_creeaza_listeaza_incarca(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard(),
                     format_dosar=["id_client", "nume_client", "scop", "tip_proprietate"])
    lst = fs.listeaza()
    assert len(lst) == 1 and lst[0]["uuid"] == uid
    assert lst[0]["nume"] == "D001_Pop_garantare_casa"
    d = fs.incarca(uid)
    assert d["wizard"]["au"] == "100"
    assert d["identitate"]["scop"] == "garantare"
    assert d["creator_legitimatie"] == "8717"


def test_retentie_versiuni_docx(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    folder = fs.baza() / uid
    # pre-existente: 12 versiuni vechi (sortabile înaintea celei reale)
    for i in range(12):
        (folder / f"raport-2020{i:02d}01-000000-000000.docx").write_text("x", encoding="utf-8")
    sursa = baza / "nou.docx"
    sursa.write_text("raport nou", encoding="utf-8")
    fs.adauga_versiune_docx(uid, sursa)
    versiuni = list(folder.glob("raport-*.docx"))
    assert len(versiuni) == fs.PASTREAZA_VERSIUNI          # 10 (cele mai vechi șterse)


def test_salveaza_redenumeste_sterge(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    fs.salveaza_wizard(uid, _wizard(au="150"))
    assert fs.incarca(uid)["wizard"]["au"] == "150"
    fs.redenumeste(uid, "Dosar redenumit")
    assert fs.incarca(uid)["nume"] == "Dosar redenumit"
    fs.sterge(uid)
    assert fs.listeaza() == []


def test_diff_noi_existente_disparute(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    d1 = fs.diff()                                     # prima dată: e „nou"
    assert len(d1["noi"]) == 1 and d1["noi"][0]["uuid"] == uid
    d2 = fs.diff()                                     # a doua: e „existent"
    assert len(d2["existente"]) == 1 and d2["noi"] == []
    fs.sterge(uid)
    d3 = fs.diff()                                     # șters → „dispărut"
    assert len(d3["disparute"]) == 1 and d3["disparute"][0]["uuid"] == uid


def test_import_acelasi_user_adopta(baza, tmp_path):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    src = fs.baza() / uid
    r = fs.importa_folder(src, "8717", "Adi S")        # același evaluator
    assert r["e_nou"] is False and r["uuid"] == uid


def test_import_alt_user_devine_dosar_nou(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    src = fs.baza() / uid
    r = fs.importa_folder(src, "9999", "Alt Evaluator")  # alt evaluator
    assert r["e_nou"] is True and r["uuid"] != uid
    d = fs.incarca(r["uuid"])
    assert d["creator_legitimatie"] == "9999"


def test_import_folder_invalid_ridica(baza, tmp_path):
    from evaluare import dosare_fs as fs
    gol = tmp_path / "gol"
    gol.mkdir()
    with pytest.raises(ValueError):
        fs.importa_folder(gol, "8717", "Adi S")
