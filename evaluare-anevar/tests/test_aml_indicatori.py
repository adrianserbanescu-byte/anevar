"""Indicatori de suspiciune (HCD 58 art. 6(10)) — checklist specific evaluarii."""
from evaluare.aml.indicatori import (
    INDICATORI,
    SemnaleIndicatori,
    evalueaza_indicatori,
    propune_rts,
)


def test_catalog_are_10_indicatori():
    assert len(INDICATORI) == 10
    # fiecare are cheie, text si citat
    for ind in INDICATORI:
        assert ind.cheie and ind.text and ind.temei


def test_niciun_semnal_nicio_alerta():
    rez = evalueaza_indicatori(SemnaleIndicatori())
    assert rez == []
    assert propune_rts(SemnaleIndicatori()) is False


def test_presiune_valoare_predeterminata_alerteaza():
    s = SemnaleIndicatori(presiune_valoare_predeterminata=True)
    rez = evalueaza_indicatori(s)
    assert len(rez) == 1
    assert rez[0].cheie == "presiune_valoare_predeterminata"
    assert propune_rts(s) is True


def test_mai_multe_semnale():
    s = SemnaleIndicatori(
        graba_excesiva=True, pep_implicat=True, drepturi_litigioase=True,
    )
    chei = {i.cheie for i in evalueaza_indicatori(s)}
    assert chei == {"graba_excesiva", "pep_implicat", "drepturi_litigioase"}


def test_toate_semnalele_active():
    s = SemnaleIndicatori(**{i.cheie: True for i in INDICATORI})
    assert len(evalueaza_indicatori(s)) == 10
