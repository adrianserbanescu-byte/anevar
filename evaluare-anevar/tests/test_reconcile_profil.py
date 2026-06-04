from decimal import Decimal

from evaluare.engine.abordari import RezultatAbordare
from evaluare.engine.reconciliation import reconcile_profil


def _r(abordare, val):
    return RezultatAbordare(abordare=abordare, valoare=Decimal(val) if val is not None else None)


def test_primara_disponibila():
    rez = [_r("cost", "300000"), _r("comparatie", "320000")]
    out = reconcile_profil(rez, primara="comparatie")
    assert out.valoare_finala == Decimal("320000")
    assert out.metoda_selectata == "piata"        # comparatie = piata


def test_venit_primar():
    rez = [_r("venit", "800000"), _r("comparatie", "780000")]
    out = reconcile_profil(rez, primara="venit")
    assert out.valoare_finala == Decimal("800000")
    assert out.metoda_selectata == "venit"


def test_fallback_cand_primara_lipseste():
    rez = [_r("comparatie", None), _r("cost", "300000")]
    out = reconcile_profil(rez, primara="comparatie")
    assert out.valoare_finala == Decimal("300000")
    assert out.metoda_selectata == "cost"
    assert out.nota != ""


def test_ponderata():
    rez = [_r("comparatie", "320000"), _r("cost", "300000")]
    out = reconcile_profil(rez, primara="comparatie",
                           ponderi={"comparatie": Decimal("0.5"), "cost": Decimal("0.5")})
    assert out.valoare_finala == Decimal("310000")
    assert out.metoda_selectata == "ponderata"
