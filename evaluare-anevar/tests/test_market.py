from decimal import Decimal

import pytest

from evaluare.engine.market import (
    ajustare_bruta,
    ajustare_neta,
    evaluate_market,
    pret_total_corectat,
    pret_unitar_brut,
)
from evaluare.models.comparable import Adjustment, Comparable


def _adj(element, valoare, etapa="proprietate", tip="procentuala"):
    return Adjustment(element=element, tip=tip, valoare=Decimal(str(valoare)), etapa=etapa)


def test_pret_unitar_brut():
    c = Comparable(pret=Decimal("500000"), suprafata=Decimal("100"))
    assert pret_unitar_brut(c) == Decimal("5000")


def test_pret_total_doua_etape():
    # tranzactie -5% secvential pe total: 500000 -> 475000 ; proprietate +10% aditiv -> 522500
    c = Comparable(pret=Decimal("500000"), suprafata=Decimal("100"),
                   adjustments=[_adj("Negociere", -0.05, "tranzactie"),
                                _adj("Localizare", 0.10)])
    assert pret_total_corectat(c) == Decimal("522500.00")


def test_pret_total_proprietate_aditiv_cu_valorica():
    # baza 500000 ; proprietate: +10% si -20000 EUR (aditiv): 500000*1.10 - 20000 = 530000
    c = Comparable(pret=Decimal("500000"), suprafata=Decimal("100"),
                   adjustments=[_adj("Localizare", 0.10),
                                _adj("Arie utila", -20000, tip="valorica")])
    assert pret_total_corectat(c) == Decimal("530000.00")


def test_ajustare_bruta_si_neta_proprietate():
    c = Comparable(pret=Decimal("500000"), suprafata=Decimal("100"),
                   adjustments=[_adj("A", -0.03), _adj("B", 0.10)])
    assert ajustare_bruta(c) == Decimal("0.13")   # |-0.03| + |0.10|
    assert ajustare_neta(c) == Decimal("0.07")    # -0.03 + 0.10


def test_evaluate_market_valoare_egala_cu_totalul_ales():
    # comp0: gross 0.05 ; comp1: gross 0.20 -> selecteaza comp0
    comp0 = Comparable(pret=Decimal("480000"), suprafata=Decimal("100"),
                       adjustments=[_adj("A", 0.05)])
    comp1 = Comparable(pret=Decimal("520000"), suprafata=Decimal("100"),
                       adjustments=[_adj("A", -0.20)])
    result = evaluate_market([comp0, comp1])
    assert result.index_selectat == 0
    # valoarea = totalul corectat al comp0 = 480000 * 1.05 = 504000 (NU x suprafata)
    assert result.valoare_piata == Decimal("504000.00")


def test_evaluate_market_fara_comparabile_ridica():
    with pytest.raises(ValueError):
        evaluate_market([])


# --------------------------------------------------------------------------- #
# Regresie pe grila reala de casa GBF (Busteni, foaie "G. Comparatii locuinta").
# Verifica reproducerea EXACTA a preturilor totale corectate ale celor 4 comparabile.
# Etapa de tranzactie: negociere -5%. Etapa de proprietate: % si EUR (aditiv pe baza).
# --------------------------------------------------------------------------- #
def _comp_casa(pret_initial, fizice):
    adj = [_adj("Negociere", -0.05, "tranzactie")]
    for el, tip, val in fizice:
        adj.append(_adj(el, val, tip=tip))
    return Comparable(pret=Decimal(str(pret_initial)), suprafata=Decimal("1"), adjustments=adj)


BUSTENI_CASA = [
    # (pret_initial, [(element, tip, valoare)]) ; final asteptat din celula reala
    (_comp_casa(219000, [("Localizare", "procentuala", "-0.05"),
                         ("Suprafata teren", "valorica", "2128"),
                         ("Arie utila", "valorica", "-59517.69921212121"),
                         ("PIF", "procentuala", "-0.015"),
                         ("Finisaje", "procentuala", "-0.04117519826964672"),
                         ("Alte", "valorica", "4000")]),
     "132570.5507878788"),
    (_comp_casa(220000, [("Localizare", "procentuala", "-0.05"),
                         ("Suprafata teren", "valorica", "3584"),
                         ("Arie utila", "valorica", "-83620.9174"),
                         ("PIF", "procentuala", "0.10"),
                         ("Acces", "procentuala", "-0.05"),
                         ("Curte", "valorica", "-2500"),
                         ("Finisaje", "procentuala", "0.09569377990430622"),
                         ("Incalzire", "valorica", "5000")]),
     "151463.0826"),
    (_comp_casa(220000, [("Localizare", "procentuala", "-0.07"),
                         ("Suprafata teren", "valorica", "1792"),
                         ("Arie utila", "valorica", "-66262.70331428571"),
                         ("PIF", "procentuala", "0.08"),
                         ("Finisaje", "procentuala", "-0.04098803827751196")]),
     "138052.79668571427"),
    (_comp_casa(243000, [("Localizare", "procentuala", "-0.15"),
                         ("Suprafata teren", "valorica", "3472"),
                         ("Arie utila", "valorica", "-39143.845347222225"),
                         ("PIF", "procentuala", "-0.06"),
                         ("Finisaje", "procentuala", "-0.04678362573099415"),
                         ("Alte", "valorica", "4000")]),
     "139899.65465277777"),
]


@pytest.mark.parametrize("comp,final_asteptat", BUSTENI_CASA)
def test_regresie_casa_reala_busteni(comp, final_asteptat):
    # pretul total corectat reproduce celula reala (la 6 zecimale)
    assert round(pret_total_corectat(comp), 6) == round(Decimal(final_asteptat), 6)


# Regresie pe inca doua grile reale de casa (Maneciu, Brasov). Per comparabil: pret initial,
# negociere (etapa tranzactie) si suma ajustarilor valorice de proprietate (EUR) -> pret final.
# Sursa: foaia "G. Comparatii locuinta". final = pret*(1+negociere) + suma EUR.
_REAL_CASA = {
    "Maneciu": [
        ("110000", "-0.05", "-52918.01136363636", "51581.98863636364"),
        ("87500", "-0.05", "23205.735625", "106330.735625"),
        ("87500", "-0.05", "-26444.330357142855", "56680.669642857145"),
        ("128500", "-0.05", "-61630.044384057976", "60444.95561594202"),
    ],
    "Brasov": [
        ("400000", "-0.1", "-23743.60521739132", "336256.39478260867"),
        ("275000", "-0.05", "26631.791499999985", "287881.7915"),
        ("275000", "-0.1", "96613.88866666665", "344113.88866666664"),
        ("370000", "-0.1", "21887.429188022652", "354887.4291880226"),
    ],
}


@pytest.mark.parametrize("oras", list(_REAL_CASA.keys()))
def test_regresie_casa_reala_maneciu_brasov(oras):
    for pret, neg, sum_eur, final in _REAL_CASA[oras]:
        c = Comparable(pret=Decimal(pret), suprafata=Decimal("1"), adjustments=[
            _adj("Negociere", neg, "tranzactie"),
            _adj("Ajustari proprietate", sum_eur, tip="valorica"),
        ])
        assert round(pret_total_corectat(c), 2) == round(Decimal(final), 2), f"{oras} {pret}"


def test_regresie_casa_busteni_grila_completa():
    comps = [c for c, _ in BUSTENI_CASA]
    r = evaluate_market(comps)
    # toate preturile totale corectate reproduc celulele reale
    asteptate = [Decimal(f) for _, f in BUSTENI_CASA]
    for got, exp in zip(r.preturi_unitare_corectate, asteptate, strict=True):
        assert round(got, 4) == round(exp, 4)
    # selectia foloseste regula curata (ajustare bruta minima pe etapa de proprietate)
    assert r.valoare_piata == r.preturi_unitare_corectate[r.index_selectat]
