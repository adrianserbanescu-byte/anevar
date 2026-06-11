"""Registrul de evidenta a rapoartelor de evaluare (Procedura §6): randuri + export CSV/XLSX."""
from __future__ import annotations

import io
import zipfile

import pytest


@pytest.fixture
def baza(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    return tmp_path


def _creeaza(**wizard):
    import evaluare.dosare_fs as fs
    w = {"scop": "garantare", "tip_proprietate": "casa", "nume_client": "Pop Ion",
         "numar_cadastral": "12345", "data_raportului": "2026-02-01"}
    w.update(wizard)
    return fs.creeaza("L1", "Evaluator", w)


def test_rand_acopera_campurile_sectiunii_6(baza):
    from evaluare.registru import registru as reg
    _creeaza(beneficiar="Banca X", proprietar="Pop Ion", onorariu="1500",
             data_evaluarii="2026-01-20", data_predarii="2026-02-03",
             verificator_intern_nume="Ionescu", data_verificare_interna="2026-01-31",
             risc_aml="sporit", nr_contract="77/2026", data_contract="2026-01-10",
             observatii_registru="fara observatii")
    r = reg.randuri()
    assert len(r) == 1
    row = r[0]
    assert row["nr_lucrare"].endswith("/0001")
    assert row["contract"] == "77/2026 / 2026-01-10"
    assert row["client"] == "Pop Ion"
    assert row["utilizatori"] == "Banca X"
    assert "nr. cad. 12345" in row["obiect"]
    assert row["proprietar"] == "Pop Ion"
    assert row["tip"] == "PI"                                  # bun imobil
    assert row["scop"] == "Garantarea creditului ipotecar"    # slug -> eticheta
    assert row["onorariu"] == "1500"
    assert row["data_evaluarii"] == "2026-01-20"
    assert row["data_raportului"] == "2026-02-01"
    assert row["data_predarii"] == "2026-02-03"
    assert row["verificator"] == "Ionescu / 2026-01-31"
    assert row["risc_aml"] == "ridicat"                        # sporit -> ridicat (§6)
    assert row["observatii"] == "fara observatii"


def test_randuri_sortate_dupa_nr_lucrare(baza):
    from evaluare.registru import registru as reg
    _creeaza(nume_client="Unu")
    _creeaza(nume_client="Doi")
    _creeaza(nume_client="Trei")
    numere = [r["nr_lucrare"] for r in reg.randuri()]
    assert numere == sorted(numere)
    assert len(numere) == 3 and len(set(numere)) == 3


def test_csv_are_bom_antete_si_valori(baza):
    from evaluare.registru import registru as reg
    _creeaza(nume_client="Popescu", onorariu="2200")
    csv = reg.csv_text()
    assert csv.startswith("﻿")                            # BOM pentru Excel RO
    assert "Nr. identificare" in csv and "Onorariu" in csv
    assert "Popescu" in csv and "2200" in csv


def test_xlsx_este_zip_valid_cu_valori(baza):
    from evaluare.registru import registru as reg
    _creeaza(nume_client="Georgescu", risc_aml="redus")
    data = reg.xlsx_bytes()
    assert data[:2] == b"PK"                                   # semnatura ZIP
    z = zipfile.ZipFile(io.BytesIO(data))
    necesare = {"[Content_Types].xml", "_rels/.rels", "xl/workbook.xml",
                "xl/_rels/workbook.xml.rels", "xl/worksheets/sheet1.xml"}
    assert necesare.issubset(set(z.namelist()))
    sheet = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert "Georgescu" in sheet
    assert "Nr. identificare" in sheet                         # antetul e primul rand
    assert "scăzut" in sheet                                   # redus -> scăzut


def test_xlsx_escapeaza_xml(baza):
    from evaluare.registru import registru as reg
    _creeaza(nume_client="A & <B>")
    sheet = zipfile.ZipFile(io.BytesIO(reg.xlsx_bytes())).read("xl/worksheets/sheet1.xml").decode()
    assert "A &amp; &lt;B&gt;" in sheet                        # caractere XML escapate
    assert "<B>" not in sheet.replace("&lt;B&gt;", "")         # niciun '<B>' neescapat


def test_registru_gol(baza):
    from evaluare.registru import registru as reg
    assert reg.randuri() == []
    assert reg.csv_text().startswith("﻿")                 # doar antetul, fara randuri
    assert reg.xlsx_bytes()[:2] == b"PK"
