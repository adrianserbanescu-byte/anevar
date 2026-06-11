"""Avertismente non-blocante GEV 630 la reconcilierea valorilor (SEV 2025).

Verifica regulile §107 (media ponderata interzisa ca CONCLUZIE), §108 (a doua abordare doar formala)
si §109 (diferenta > 20% intre abordari cere justificare). Avertismentele sunt ADITIVE: nu schimba
valoarea finala si nu blocheaza nimic — doar se anexeaza la `ReconciledResult.nota`.
"""
from decimal import Decimal

from evaluare.engine.abordari import RezultatAbordare
from evaluare.engine.reconciliation import reconcile, reconcile_profil
from evaluare.models.results import CostResult, MarketResult


def _market(value: Decimal) -> MarketResult:
    return MarketResult(index_selectat=0, valoare_piata=value)


def _cost(value: Decimal | None) -> CostResult:
    return CostResult(
        cib=Decimal("2000000"), vcp=Decimal("34"),
        depreciere_fizica=Decimal("0.35"), cin=Decimal("1300000"), valoare_cost=value,
    )


def _r(abordare, val):
    return RezultatAbordare(abordare=abordare, valoare=Decimal(val) if val is not None else None)


# ── §107 — media ponderata INTERZISA ca valoare de concluzie ──────────────────────────────────────

def test_107_avertisment_la_ponderare_reconcile():
    # reconcile() in mod "ponderata" -> avertisment §107, dar valoarea NU se schimba (non-blocant).
    r = reconcile(_market(Decimal("400000")), _cost(Decimal("440000")),
                  metoda="ponderata", pondere_piata=Decimal("0.5"))
    assert r.metoda_selectata == "ponderata"
    assert r.valoare_finala == Decimal("420000.00")        # 400k*0.5 + 440k*0.5 — neschimbat
    assert "§107" in r.nota
    assert "ponderat" in r.nota.lower()


def test_107_avertisment_la_ponderare_reconcile_profil():
    r = reconcile_profil([_r("comparatie", "320000"), _r("cost", "300000")], primara="comparatie",
                         ponderi={"comparatie": Decimal("0.5"), "cost": Decimal("0.5")})
    assert r.metoda_selectata == "ponderata"
    assert r.valoare_finala == Decimal("310000")           # neschimbat fata de testul existent
    assert "§107" in r.nota


def test_107_nu_apare_la_selectie_unica():
    # Selectie de o singura abordare (nu ponderare) -> fara avertismentul §107.
    r = reconcile(_market(Decimal("450000")), _cost(Decimal("460000")), metoda="piata")
    assert "§107" not in r.nota


# ── §108 — a doua abordare doar FORMALA (simpla verificare) ───────────────────────────────────────

def test_108_a_doua_abordare_calculata_dar_neutilizata():
    # Doua abordari calculate, dar concluzia ia o singura valoare -> nota §108 (de justificat rolul).
    r = reconcile_profil([_r("comparatie", "320000"), _r("cost", "315000")], primara="comparatie")
    assert r.metoda_selectata == "piata"
    assert r.valoare_finala == Decimal("320000")           # valoarea selectata, neschimbata
    assert "§108" in r.nota


def test_108_nu_apare_cu_o_singura_abordare():
    # O singura abordare calculata -> nu exista "a doua abordare", deci fara §108.
    r = reconcile_profil([_r("comparatie", "320000")], primara="comparatie")
    assert "§108" not in r.nota
    assert r.nota == ""                                    # nicio nota — comportament curat


def test_108_nu_apare_la_ponderare():
    # La ponderare toate abordarile contribuie -> nu e "a doua abordare doar formala".
    r = reconcile_profil([_r("comparatie", "320000"), _r("cost", "315000")], primara="comparatie",
                         ponderi={"comparatie": Decimal("0.5"), "cost": Decimal("0.5")})
    assert "§108" not in r.nota


# ── §109 — diferenta > 20% intre abordari cere justificare ────────────────────────────────────────

def test_109_diferenta_peste_20_la_suta():
    # piata 500k vs cost 400k -> 25% > 20% -> avertisment §109.
    r = reconcile(_market(Decimal("500000")), _cost(Decimal("400000")), metoda="piata")
    assert "§109" in r.nota
    assert r.valoare_finala == Decimal("500000")           # neschimbat


def test_109_diferenta_sub_20_nu_avertizeaza():
    # piata 450k vs cost 460k -> ~2.2% < 20% -> fara §109.
    r = reconcile(_market(Decimal("450000")), _cost(Decimal("460000")), metoda="piata")
    assert "§109" not in r.nota


def test_109_la_limita_exact_20_nu_avertizeaza():
    # exact 20% (500k vs 600k = 20% din 500k) -> NU avertizeaza (regula e STRICT > 20%).
    r = reconcile(_market(Decimal("600000")), _cost(Decimal("500000")), metoda="piata")
    assert "§109" not in r.nota


def test_109_profil_pereche_peste_prag():
    # venit 350k vs comparatie 280k -> 25% > 20% -> §109 chiar daca primara e comparatie.
    r = reconcile_profil([_r("comparatie", "280000"), _r("venit", "350000")], primara="comparatie")
    assert "§109" in r.nota


# ── Aditiv / backward-compatible: valoarea finala nu se modifica de avertismente ─────────────────

def test_avertismentele_nu_schimba_valoarea():
    base = reconcile_profil([_r("comparatie", "320000"), _r("cost", "300000")], primara="comparatie")
    assert base.valoare_finala == Decimal("320000")        # selectia primara, intacta
    # diferenta cost↔comparatie = 6.7% < 20% -> fara §109; dar §108 (a doua abordare) prezent
    assert "§109" not in base.nota
    assert "§108" in base.nota


def test_indisponibilitatea_pastreaza_nota_existenta():
    # cand o abordare lipseste, nota de fallback existenta ramane (nu o suprascriem cu avertismente).
    r = reconcile(_market(Decimal("450000")), _cost(None), metoda="cost")
    assert "indisponibil" in r.nota.lower()
    assert r.valoare_finala == Decimal("450000")
