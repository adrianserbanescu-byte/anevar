"""Alocarea numarului de lucrare secvential pe an (`AAAA/NNNN`), atomica (Procedura §6/§11)."""
from __future__ import annotations

import pytest


@pytest.fixture
def baza(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    return tmp_path


def test_aloca_secvential_pe_an(baza):
    from evaluare.registru import numar
    assert numar.aloca(2026) == "2026/0001"
    assert numar.aloca(2026) == "2026/0002"
    assert numar.aloca(2026) == "2026/0003"


def test_anii_au_contoare_separate(baza):
    from evaluare.registru import numar
    assert numar.aloca(2026) == "2026/0001"
    assert numar.aloca(2027) == "2027/0001"        # an nou -> reincepe de la 0001
    assert numar.aloca(2026) == "2026/0002"


def test_aloca_implicit_anul_curent(baza):
    from datetime import datetime

    from evaluare.registru import numar
    nr = numar.aloca()
    an, seq = nr.split("/")
    assert an == str(datetime.now().year) and seq == "0001"


def test_numere_unice_chiar_la_multe_alocari(baza):
    from evaluare.registru import numar
    numere = {numar.aloca(2030) for _ in range(50)}
    assert len(numere) == 50                        # fara duplicate
    assert "2030/0050" in numere                    # contiguu pana la 50


def test_reia_de_la_maxul_existent(baza, monkeypatch):
    # O_EXCL: daca un marcaj exista deja (alt proces), alocarea sare peste el, nu il suprascrie.
    from evaluare.registru import numar
    d = numar._dir_numere()
    d.mkdir(parents=True, exist_ok=True)
    (d / "2026_0001").write_text("")
    (d / "2026_0005").write_text("")               # gol intre 1 si 5 — alocarea continua de la max+1
    assert numar.aloca(2026) == "2026/0006"
