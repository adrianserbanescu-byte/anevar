"""Config de metodologie (audit #3): M1 selecție teren + M3 pondere + M5 praguri + E1 rotunjire,
ca opțiuni cu default sensibil + override (decizia Adi). Mirror al config-ponderi (D1)."""
from decimal import Decimal

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.engine.abordari import RezultatAbordare
from evaluare.engine.land import evaluate_land
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig, din_override
from evaluare.engine.metodologie_store import cale_override, config_efectiv, salveaza_override
from evaluare.engine.reconciliation import reconcile_profil
from evaluare.models.comparable import Adjustment, LandComparable
from evaluare.web.app import create_app


def _adj(el, val, etapa="proprietate", tip="procentuala"):
    return Adjustment(element=el, tip=tip, valoare=Decimal(str(val)), etapa=etapa)


# ── M1: selecția la teren include (sau nu) ajustările EUR ─────────────────────────────────────
def test_M1_selectie_teren_include_eur_schimba_alegerea():
    A = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"),
                       adjustments=[_adj("pct", 0.10)])                      # gross pct = 0.10
    B = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"),
                       adjustments=[_adj("pct", 0.02), _adj("eur", 50, tip="valorica")])  # 0.02 + 50/100
    # vechi (include_eur=False): B are gross 0.02 < 0.10 -> B (index 1)
    old = evaluate_land([A, B], Decimal("500"), MetodologieConfig(teren_selectie_include_eur=False))
    assert old.index_selectat == 1
    # M1 default (include_eur=True): gross B = 0.02 + 0.50 = 0.52 > 0.10 -> A (index 0)
    new = evaluate_land([A, B], Decimal("500"))
    assert new.index_selectat == 0


# ── override / config ─────────────────────────────────────────────────────────────────────────
def test_din_override_valid_invalid_necunoscut():
    cfg = din_override({"teren_selectie_include_eur": False, "min_comparabile": 5,
                        "limita_ajustare_bruta": "0.30", "prag_outlier": "abc", "necunoscut": 1})
    assert cfg.teren_selectie_include_eur is False
    assert cfg.min_comparabile == 5
    assert cfg.limita_ajustare_bruta == Decimal("0.30")
    assert cfg.prag_outlier == IMPLICIT.prag_outlier        # "abc" invalid -> default
    assert din_override({}) == IMPLICIT
    assert din_override(None) == IMPLICIT


def test_store_round_trip_si_corupt(tmp_path):
    assert config_efectiv(tmp_path) == IMPLICIT
    salveaza_override(tmp_path, {"min_comparabile": 4, "teren_selectie_include_eur": False})
    cfg = config_efectiv(tmp_path)
    assert cfg.min_comparabile == 4 and cfg.teren_selectie_include_eur is False
    cale_override(tmp_path).write_text("{nu-i json", encoding="utf-8")
    assert config_efectiv(tmp_path) == IMPLICIT             # corupt -> default, fără crash


# ── E1: rotunjirea valorii finale din config ───────────────────────────────────────────────────
def test_E1_reconcile_profil_rotunjire_din_config():
    rez = [RezultatAbordare(abordare="comparatie", valoare=Decimal("100")),
           RezultatAbordare(abordare="cost", valoare=Decimal("101"))]
    ponderi = {"comparatie": Decimal("1"), "cost": Decimal("2")}   # (100 + 202)/3 = 100.666...
    assert reconcile_profil(rez, "comparatie", ponderi).valoare_finala == Decimal("100.67")
    r2 = reconcile_profil(rez, "comparatie", ponderi,
                          cfg=MetodologieConfig(rotunjire_valoare=Decimal("1")))
    assert r2.valoare_finala == Decimal("101")


# ── Endpoint GET/POST ──────────────────────────────────────────────────────────────────────────
def test_endpoint_metodologie_config_get_post(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    client = TestClient(create_app(storage=storage, client=None, fetcher=lambda u: ""))
    data = client.get("/api/metodologie-config").json()
    assert data["editabil"] is True
    assert data["config"]["teren_selectie_include_eur"] is True       # default M1
    assert data["config"]["min_comparabile"] == 3
    # POST: schimba praguri + M1
    r = client.post("/api/metodologie-config",
                    json={"config": {"min_comparabile": 4, "teren_selectie_include_eur": False,
                                     "necunoscut": 1}})
    assert r.status_code == 200 and r.json()["ok"] is True
    assert r.json()["config"]["min_comparabile"] == 4
    # persistat -> GET reflecta
    assert client.get("/api/metodologie-config").json()["config"]["min_comparabile"] == 4
    assert client.get("/api/metodologie-config").json()["config"]["teren_selectie_include_eur"] is False
