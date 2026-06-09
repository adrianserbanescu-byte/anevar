"""M2 (decizia Adi): valoarea = MEDIA primelor `nr_comparabile_medie` comparabile (default 3 = minimul
legal). Set nou de teste pe N=3, ca sa prindem variatii ale motorului de calcul (cerere Adi 2026-06-08).
Grilele reale GBF valideaza cazul N=1 (selectie unica) — vezi test_land/test_market."""
from decimal import Decimal

from evaluare.engine.land import evaluate_land
from evaluare.engine.market import evaluate_market
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.models.comparable import Adjustment, Comparable, LandComparable

_N1 = MetodologieConfig(nr_comparabile_medie=1)


def _adj(el, val):
    return Adjustment(element=el, tip="procentuala", valoare=Decimal(str(val)), etapa="proprietate")


def _casa(adj_pct):
    # pret 100000, o ajustare de proprietate -> corectat = 100000*(1+adj), gross = |adj|
    return Comparable(pret=Decimal("100000"), suprafata=Decimal("100"), adjustments=[_adj("a", adj_pct)])


def _teren(adj_pct):
    return LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"), adjustments=[_adj("a", adj_pct)])


def test_default_nr_comparabile_medie_e_3():
    assert IMPLICIT.nr_comparabile_medie == 3        # minimul legal (decizia Adi)


def test_market_medie_top3_exclude_cel_mai_ajustat():
    # gross: 0.02 / 0.04 / 0.06 / 0.50 -> top-3 = primele 3; al 4-lea (cel mai ajustat) e EXCLUS din medie
    comps = [_casa(0.02), _casa(0.04), _casa(0.06), _casa(0.50)]
    r = evaluate_market(comps)                        # default N=3
    assert r.index_selectat == 0                      # cel mai similar (referinta)
    assert r.valoare_piata == Decimal("104000")       # media (102000+104000+106000)/3, NU 150000
    # N=1 -> doar comparabilul unic cel mai similar
    assert evaluate_market(comps, cfg=_N1).valoare_piata == Decimal("102000.00")


def test_teren_medie_top3_exclude_cel_mai_ajustat():
    comps = [_teren(0.02), _teren(0.04), _teren(0.06), _teren(0.50)]
    r = evaluate_land(comps, Decimal("1000"))         # default N=3
    assert r.index_selectat == 0
    assert r.pret_mp_ales == Decimal("104")           # media €/mp (102+104+106)/3
    assert r.valoare_teren == Decimal("104000")       # 104 * 1000 mp
    # N=1 -> €/mp al comparabilului unic
    assert evaluate_land(comps, Decimal("1000"), cfg=_N1).pret_mp_ales == Decimal("102.00")


def test_medie_se_limiteaza_la_numarul_de_comparabile():
    # default N=3 dar doar 2 comparabile -> media celor 2 (nu crapa, nu cere 3)
    comps = [Comparable(pret=Decimal("100000"), suprafata=Decimal("100")),
             Comparable(pret=Decimal("120000"), suprafata=Decimal("100"))]
    assert evaluate_market(comps).valoare_piata == Decimal("110000")     # (100000+120000)/2


def test_nr_comparabile_medie_din_config_override():
    from evaluare.engine.metodologie import din_override
    assert din_override({"nr_comparabile_medie": 2}).nr_comparabile_medie == 2
    assert din_override({"nr_comparabile_medie": 0}).nr_comparabile_medie == IMPLICIT.nr_comparabile_medie
    assert din_override({"nr_comparabile_medie": 99}).nr_comparabile_medie == IMPLICIT.nr_comparabile_medie


# ── Fix-uri din verificarea adversariala M2 ─────────────────────────────────────────────────────
def test_indici_mediati_expusi_pentru_trasabilitate():
    # raportul/UI trebuie sa stie CARE comparabile s-au mediat (nu doar index_selectat)
    comps = [_casa(0.02), _casa(0.06), _casa(0.04)]            # gross: 0=.02, 1=.06, 2=.04
    assert sorted(evaluate_market(comps).indici_mediati) == [0, 1, 2]   # N=3 -> toate
    assert evaluate_market(comps, cfg=_N1).indici_mediati == [0]        # N=1 -> doar cel mai similar
    assert sorted(evaluate_land([_teren(0.02), _teren(0.06), _teren(0.04)],
                                Decimal("1000")).indici_mediati) == [0, 1, 2]


def test_valoare_finala_rotunjita_la_medie_nonexacta():
    # M2: o medie care nu se imparte exact NU trebuie sa ajunga cu 28 cifre in API/jurnal de audit
    from evaluare.engine.abordari import RezultatAbordare
    from evaluare.engine.reconciliation import reconcile_profil
    rez = [RezultatAbordare(abordare="comparatie", valoare=Decimal("100000.3333333333333333333"))]
    assert reconcile_profil(rez, "comparatie").valoare_finala == Decimal("100000.33")


def test_grila_casa_respecta_override_persistat(tmp_path):
    # Fix major: /api/grila-casa foloseste configul persistat (M2), la fel ca /calcul si grila-teren
    from fastapi.testclient import TestClient

    from evaluare.db.storage import Storage
    from evaluare.engine.metodologie_store import salveaza_override
    from evaluare.web.app import create_app
    storage = Storage(tmp_path / "t.db")
    storage.init()
    client = TestClient(create_app(storage=storage, client=None, fetcher=lambda u: ""))
    comps = [{"pret": "100000", "suprafata": "100",
              "adjustments": [{"element": "a", "tip": "procentuala", "valoare": "0.02"}]},
             {"pret": "100000", "suprafata": "100",
              "adjustments": [{"element": "a", "tip": "procentuala", "valoare": "0.04"}]}]
    payload = {"suprafata_subiect": "100", "comparabile": comps}
    # default N=3 (limitat la 2 comparabile): media (102000 + 104000)/2 = 103000
    assert Decimal(client.post("/api/grila-casa", json=payload).json()["valoare_piata"]) == Decimal("103000")
    # override N=1 -> doar comparabilul unic = 102000
    salveaza_override(storage.db_path.parent, {"nr_comparabile_medie": 1})
    assert Decimal(client.post("/api/grila-casa",
                               json=payload).json()["valoare_piata"]) == Decimal("102000.00")
