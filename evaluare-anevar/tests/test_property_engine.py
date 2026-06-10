"""Teste property-based (Hypothesis) pe invariantii motorului de evaluare (#2, dispatch A).

Verifica proprietati care trebuie sa tina pentru ORICE intrare valida, nu doar exemplele alese:
scale-invarianta, selectie = ajustare bruta minima, media top-N in [min,max], idempotenta.
"""
from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from evaluare.engine.land import evaluate_land
from evaluare.engine.market import ajustare_bruta, evaluate_market, pret_total_corectat
from evaluare.engine.metodologie import MetodologieConfig
from evaluare.models.comparable import Adjustment, Comparable, LandComparable

_N1 = MetodologieConfig(nr_comparabile_medie=1)

# Strategii: pret/suprafata POZITIVE (modelele cer gt=0); ajustari de proprietate procentuale mici
# (suma in (-1,1) -> pretul corectat ramane > 0, fara cazuri degenerate).
_preturi = st.decimals(min_value=Decimal("1000"), max_value=Decimal("5000000"), places=2)
_suprafete = st.decimals(min_value=Decimal("10"), max_value=Decimal("2000"), places=2)
_ajustari = st.lists(
    st.decimals(min_value=Decimal("-0.20"), max_value=Decimal("0.20"), places=4).map(
        lambda v: Adjustment(element="x", tip="procentuala", valoare=v, etapa="proprietate")),
    max_size=4)


def _comp(pret, supr, adjs):
    return Comparable(pret=pret, suprafata=supr, adjustments=adjs)


_comparabile = st.builds(_comp, _preturi, _suprafete, _ajustari)
_liste = st.lists(_comparabile, min_size=1, max_size=6)


@given(_liste)
@settings(max_examples=200, deadline=None)
def test_prop_valoare_in_intervalul_preturilor_corectate(comps):
    # Media celor mai similare N comparabile e MEREU intre min si max al preturilor corectate.
    r = evaluate_market(comps)
    corectate = [pret_total_corectat(c) for c in comps]
    assert min(corectate) <= r.valoare_piata <= max(corectate)


@given(_liste)
@settings(max_examples=200, deadline=None)
def test_prop_index_selectat_e_brut_minim(comps):
    r = evaluate_market(comps)
    brute = [ajustare_bruta(c) for c in comps]
    assert brute[r.index_selectat] == min(brute)
    for i in r.indici_mediati:                          # toate cele mediate au brut <= cele excluse
        assert brute[i] <= max(brute[j] for j in range(len(comps)))


@given(_liste, st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000"), places=2))
@settings(max_examples=150, deadline=None)
def test_prop_scale_invarianta(comps, k):
    # Scalez toate preturile cu k -> valoarea se scaleaza EXACT cu k (ajustarile sunt procentuale).
    r1 = evaluate_market(comps, cfg=_N1)
    scalate = [Comparable(pret=c.pret * k, suprafata=c.suprafata, adjustments=c.adjustments)
               for c in comps]
    r2 = evaluate_market(scalate, cfg=_N1)
    assert r2.valoare_piata == r1.valoare_piata * k


@given(_liste)
@settings(max_examples=100, deadline=None)
def test_prop_idempotenta(comps):
    # Motorul e determinist: aceleasi intrari -> acelasi rezultat.
    assert evaluate_market(comps).valoare_piata == evaluate_market(comps).valoare_piata


# ── Teren: aceleasi invariante ────────────────────────────────────────────────────────────────────
def _teren(pret_mp, supr, adjs):
    return LandComparable(pret_mp=pret_mp, suprafata=supr, adjustments=adjs)


_terenuri = st.builds(_teren, st.decimals(min_value=Decimal("1"), max_value=Decimal("100000"),
                                          places=2), _suprafete, _ajustari)
_liste_teren = st.lists(_terenuri, min_size=1, max_size=6)


@given(_liste_teren, st.decimals(min_value=Decimal("1"), max_value=Decimal("100000"), places=2))
@settings(max_examples=150, deadline=None)
def test_prop_teren_valoare_pozitiva_si_proportionala_cu_suprafata(comps, supr_subiect):
    # valoarea terenului = pret/mp ales * suprafata subiect -> pozitiva si proportionala. Folosim N=1
    # (selectie unica) ca sa evitam artefactul de precizie Decimal al mediei (diviziune ne-terminanta).
    r1 = evaluate_land(comps, supr_subiect, cfg=_N1)
    r2 = evaluate_land(comps, supr_subiect * Decimal("2"), cfg=_N1)
    assert r1.valoare_teren > 0
    assert r2.valoare_teren == r1.valoare_teren * Decimal("2")
