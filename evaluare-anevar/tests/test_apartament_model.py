from decimal import Decimal

from evaluare.engine.validation import valideaza_proprietate
from evaluare.models.property import BuildingData, LandData


def _land():
    return LandData(suprafata=Decimal("1"))


def _ap(**kw):
    base = {"au": Decimal("60"), "acd": Decimal("70"), "an_referinta": 2025}
    base.update(kw)
    return BuildingData(**base)


def test_campuri_apartament_optionale():
    b = _ap(etaj=3, nr_niveluri_bloc=10, an_bloc=2008, cota_teren_indiviza=Decimal("12.5"))
    assert b.etaj == 3 and b.nr_niveluri_bloc == 10 and b.an_bloc == 2008
    assert b.cota_teren_indiviza == Decimal("12.5")


def test_casa_fara_campuri_apartament():
    b = _ap()
    assert b.etaj is None and b.an_bloc is None


def test_etaj_peste_numar_niveluri_blocheaza():
    issues = valideaza_proprietate(_land(), _ap(etaj=12, nr_niveluri_bloc=10))
    assert any(i.nivel == "blocheaza" and "etaj" in i.mesaj.lower() for i in issues)


def test_etaj_in_limite_ok():
    issues = valideaza_proprietate(_land(), _ap(etaj=3, nr_niveluri_bloc=10))
    assert not any("etaj" in i.mesaj.lower() for i in issues)
