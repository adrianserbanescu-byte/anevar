from decimal import Decimal

import pytest

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


def test_fara_valori_ridica_eroare():
    with pytest.raises(ValueError):
        reconcile_profil([_r("cost", None)], primara="cost")


def test_ponderata_degenerata_o_singura_abordare():
    # ponderi date dar doar o abordare are valoare -> NU "ponderata", cu nota
    rez = [_r("comparatie", "320000"), _r("cost", None)]
    out = reconcile_profil(rez, primara="comparatie",
                           ponderi={"comparatie": Decimal("0.5"), "cost": Decimal("0.5")})
    assert out.valoare_finala == Decimal("320000")
    assert out.metoda_selectata == "piata"
    assert out.nota != ""


def test_ponderata_declara_abordarea_calculata_dar_neponderata():
    # Optiunea b (decizia Adi): o abordare CALCULATA dar NEPONDERATA (ex. venitul la o ponderare
    # piata/cost) e declarata EXPLICIT in nota -> valoarea finala nu diverge TACUT de indicatii.
    rez = [_r("cost", "300000"), _r("comparatie", "280000"), _r("venit", "350000")]
    r = reconcile_profil(rez, primara="comparatie",
                         ponderi={"comparatie": Decimal("0.5"), "cost": Decimal("0.5")})
    assert r.valoare_finala == Decimal("290000.00")        # media cost+comparatie (venitul exclus)
    assert "venit" in r.nota.lower() and "nu este inclusa" in r.nota.lower()
    # fara abordari excluse -> nota goala (comportament nemodificat)
    r2 = reconcile_profil([_r("cost", "300000"), _r("comparatie", "280000")], primara="comparatie",
                          ponderi={"comparatie": Decimal("0.5"), "cost": Decimal("0.5")})
    assert r2.nota == ""


def test_ponderata_normalizeaza_ponderile_care_nu_insumeaza_1():
    # reconcile_profil NORMALIZEAZA (imparte la suma ponderilor) cand ponderile nu insumeaza 1.
    # Mutation testing (lane B): fara acest test, mutatia Div->Mult la calculul ponderat supravietuieste
    # (toate celelalte teste folosesc ponderi care insumeaza 1 -> /1 == *1 = mutant echivalent).
    rez = [_r("comparatie", "300000"), _r("cost", "200000")]
    r = reconcile_profil(rez, primara="comparatie",
                         ponderi={"comparatie": Decimal("0.6"), "cost": Decimal("0.2")})  # suma = 0.8
    # (300000*0.6 + 200000*0.2) / 0.8 = 220000 / 0.8 = 275000
    assert r.valoare_finala == Decimal("275000.00")
