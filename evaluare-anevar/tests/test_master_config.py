"""Master config: compunerea numelui de dosar din template + valori."""
from evaluare.master_config import (
    NUME_DOSAR_MIN_CAMPURI,
    TEMPLATE_NUME_IMPLICIT,
    nume_dosar,
)


def test_nume_dosar_template_implicit():
    n = nume_dosar(None, {"id_client": "D001", "nume_client": "Pop", "tip_proprietate": "casa"})
    assert n == "D001_Pop_casa"


def test_nume_dosar_template_custom_si_lipsa():
    n = nume_dosar(["legitimatie", "id_client"], {"legitimatie": "12345"})
    assert n == "12345_?"          # id_client lipsă -> „?"


def test_template_implicit_are_minim_campuri():
    assert len(TEMPLATE_NUME_IMPLICIT) >= NUME_DOSAR_MIN_CAMPURI
