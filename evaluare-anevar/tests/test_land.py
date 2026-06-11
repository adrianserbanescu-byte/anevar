from decimal import Decimal

import pytest

from evaluare.engine.land import (
    DateTerenRezidual,
    evaluate_land,
    pret_mp_corectat,
    teren_rezidual,
)
from evaluare.engine.metodologie import MetodologieConfig
from evaluare.models.comparable import Adjustment, LandComparable

# Grilele reale GBF au folosit SELECTIA comparabilului unic (N=1). Validam acel caz; media top-N
# (M2, default 3) e testata separat in test_metodologie_m2. Vezi docs/audit-metodologie-3.
_N1 = MetodologieConfig(nr_comparabile_medie=1)


def _adj(element, valoare, etapa="proprietate", tip="procentuala"):
    return Adjustment(element=element, tip=tip, valoare=Decimal(str(valoare)), etapa=etapa)


def test_etapa_tranzactie_secventiala_proprietate_aditiva():
    # tranzactie -10% (secvential) pe 20 -> 18; proprietate +10% (aditiv) -> 18*1.10 = 19.80
    c = LandComparable(pret_mp=Decimal("20"), suprafata=Decimal("500"),
                       adjustments=[_adj("Oferta", -0.10, "tranzactie"),
                                    _adj("Deschidere", 0.10)])
    assert pret_mp_corectat(c) == Decimal("19.80")


def test_proprietate_aditiv_nu_compus():
    # doua ajustari de proprietate -0.04 si +0.10 -> aditiv: baza*(1+0.06), NU compus
    c = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"),
                       adjustments=[_adj("Suprafata", -0.04), _adj("Deschidere", 0.10)])
    assert pret_mp_corectat(c) == Decimal("106.00")  # 100*(1+0.06)


def test_ajustare_valorica_proprietate():
    c = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("400"),
                       adjustments=[_adj("X", 5, tip="valorica")])
    assert pret_mp_corectat(c) == Decimal("105")


def test_evaluate_land_selecteaza_ajustare_bruta_minima():
    c0 = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("450"),
                        adjustments=[_adj("A", 0.05)])
    c1 = LandComparable(pret_mp=Decimal("120"), suprafata=Decimal("500"),
                        adjustments=[_adj("A", -0.30)])
    r = evaluate_land([c0, c1], suprafata_subiect=Decimal("1000"), cfg=_N1)
    assert r.index_selectat == 0
    assert r.pret_mp_ales == Decimal("105.00")
    assert r.valoare_teren == Decimal("105000.00")
    assert r.ajustari_brute[0] == Decimal("0.05")


def test_evaluate_land_fara_comparabile_ridica():
    with pytest.raises(ValueError):
        evaluate_land([], suprafata_subiect=Decimal("1000"))


# --------------------------------------------------------------------------- #
# Regresie pe grilele reale GBF (sursa: foaie de calcul "grila" din fisierele
# de teren Maneciu / Brasov / Busteni / Breaza). Fiecare ajustare = (element, %),
# oferta->tranzactie e etapa de tranzactie, restul etapa de proprietate.
# --------------------------------------------------------------------------- #
def _comp(pret, ofer, fizice):
    adj = [_adj("Oferta-Tranzactie", ofer, "tranzactie")]
    adj += [_adj(e, v) for e, v in fizice]
    return LandComparable(pret_mp=Decimal(str(pret)), suprafata=Decimal("1"), adjustments=adj)


REAL = {
    "Maneciu": {
        "supr": "2776", "idx": 0, "valoare": 44000,
        "comps": [
            _comp(16.53, -0.10, [("Suprafata", -0.04), ("Deschidere", 0.10)]),
            _comp(28.39, -0.10, [("Acces", -0.10), ("Suprafata", -0.15), ("Deschidere", 0.02)]),
            _comp(20.0, -0.10, [("Localizare", 0.05), ("Acces", -0.10), ("Suprafata", -0.05),
                                ("Deschidere", 0.12)]),
        ],
        "pret_ales": "15.76962",
    },
    "Brasov": {
        "supr": "808", "idx": 1, "valoare": 78000,
        "comps": [
            _comp(104.0, -0.05, [("Localizare", -0.02), ("Acces", 0.03), ("Suprafata", -0.05),
                                 ("Deschidere", 0.07)]),
            _comp(96.92, -0.05, [("Localizare", -0.02), ("Acces", 0.03), ("Suprafata", -0.03),
                                 ("Deschidere", 0.07)]),
            _comp(75.72, -0.05, [("Localizare", 0.05), ("Suprafata", 0.07), ("Deschidere", 0.25)]),
        ],
        "pret_ales": "96.67770",
    },
    "Busteni": {
        "supr": "305", "idx": 0, "valoare": 34000,
        "comps": [
            _comp(120.0, -0.05, [("Localizare", -0.05), ("Suprafata", 0.01), ("Deschidere", 0.02)]),
            _comp(119.0, -0.05, [("Localizare", -0.05), ("Suprafata", 0.05), ("Deschidere", -0.05),
                                 ("Inclinatie", 0.05)]),
            _comp(140.0, -0.05, [("Localizare", -0.05), ("Suprafata", 0.02), ("Deschidere", -0.15)]),
        ],
        "pret_ales": "111.72000",
    },
    "Breaza": {
        "supr": "900", "idx": 2, "valoare": 67000,
        "comps": [
            _comp(73.0, -0.05, [("Suprafata", -0.03), ("Deschidere", 0.08)]),
            _comp(70.0, -0.05, [("Localizare", -0.05), ("Suprafata", -0.03), ("Deschidere", 0.18),
                                ("Inclinatie", 0.05)]),
            _comp(75.0, -0.05, [("Suprafata", 0.05)]),
        ],
        "pret_ales": "74.81250",
    },
}


@pytest.mark.parametrize("nume", list(REAL.keys()))
def test_regresie_grila_reala(nume):
    d = REAL[nume]
    r = evaluate_land(d["comps"], suprafata_subiect=Decimal(d["supr"]), cfg=_N1)
    assert r.index_selectat == d["idx"], f"{nume}: comparabil selectat gresit"
    # pretul/mp corectat al comparabilului ales reproduce celula reala
    assert round(r.pret_mp_ales, 5) == Decimal(d["pret_ales"]), f"{nume}: pret/mp gresit"
    # valoarea rotunjita la mia cea mai apropiata = valoarea raportata GBF
    val_rot = round(r.valoare_teren / 1000) * 1000
    assert val_rot == d["valoare"], f"{nume}: valoare {r.valoare_teren} -> {val_rot} != {d['valoare']}"


# --------------------------------------------------------------------------- #
# I-11 — metoda REZIDUALA / a parcelarii terenului (abordare optionala, aditiva).
# --------------------------------------------------------------------------- #
def test_teren_rezidual_parcelare_loturi():
    # 10 loturi x 50.000 = GDV 500.000 ; costuri 200.000 ; profit 20% din GDV = 100.000
    # teren = 500.000 - 200.000 - 100.000 = 200.000
    d = DateTerenRezidual(nr_loturi=10, pret_lot=Decimal("50000"),
                          costuri_dezvoltare=Decimal("200000"), profit_procent=Decimal("0.20"))
    r = teren_rezidual(d)
    assert r.valoare_dezvoltare == Decimal("500000.00")
    assert r.profit_dezvoltator == Decimal("100000.00")
    assert r.valoare_teren == Decimal("200000.00")


def test_teren_rezidual_gdv_direct_si_profit_suma():
    # GDV direct 800.000 ; costuri 500.000 ; profit suma fixa 120.000 -> teren 180.000
    d = DateTerenRezidual(valoare_dezvoltare=Decimal("800000"),
                          costuri_dezvoltare=Decimal("500000"), profit_suma=Decimal("120000"))
    r = teren_rezidual(d)
    assert r.valoare_dezvoltare == Decimal("800000.00")
    assert r.profit_dezvoltator == Decimal("120000.00")
    assert r.valoare_teren == Decimal("180000.00")


def test_teren_rezidual_profit_combinat_procent_si_suma():
    # GDV 1.000.000 ; profit 10% (100.000) + suma 50.000 = 150.000 ; costuri 400.000 -> teren 450.000
    d = DateTerenRezidual(valoare_dezvoltare=Decimal("1000000"),
                          costuri_dezvoltare=Decimal("400000"),
                          profit_procent=Decimal("0.10"), profit_suma=Decimal("50000"))
    r = teren_rezidual(d)
    assert r.profit_dezvoltator == Decimal("150000.00")
    assert r.valoare_teren == Decimal("450000.00")


def test_teren_rezidual_loturi_au_prioritate_fata_de_gdv_direct():
    # nr_loturi > 0 -> se foloseste nr_loturi x pret_lot, valoare_dezvoltare e ignorata.
    d = DateTerenRezidual(nr_loturi=4, pret_lot=Decimal("100000"),
                          valoare_dezvoltare=Decimal("999999"),
                          costuri_dezvoltare=Decimal("100000"))
    r = teren_rezidual(d)
    assert r.valoare_dezvoltare == Decimal("400000.00")


def test_teren_rezidual_fara_dezvoltare_ridica():
    with pytest.raises(ValueError):
        teren_rezidual(DateTerenRezidual(costuri_dezvoltare=Decimal("100000")))


def test_teren_rezidual_negativ_ridica():
    # costuri + profit > GDV -> dezvoltarea nu lasa valoare reziduala terenului.
    d = DateTerenRezidual(valoare_dezvoltare=Decimal("300000"),
                          costuri_dezvoltare=Decimal("280000"), profit_suma=Decimal("50000"))
    with pytest.raises(ValueError):
        teren_rezidual(d)


def test_teren_rezidual_nu_afecteaza_comparatia_directa():
    # Sanity: metoda reziduala e separata; comparatia EUR/mp ramane neschimbata.
    c = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"),
                       adjustments=[_adj("Deschidere", 0.10)])
    assert pret_mp_corectat(c) == Decimal("110.00")
