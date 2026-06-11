"""Garda non-blocanta GEV 520 §31/§34 — abordarea prin COST ca abordare PRINCIPALA la garantare
cere acordul SCRIS al creditorului.

`valideaza_metoda_vs_ghid(metoda, profil)` intoarce un AVERTISMENT (text) cand metoda = "cost" SI
profilul are ghid = "GEV_520"; altfel None. Garda e ADITIVA / non-blocanta: nu schimba valoarea,
nu blocheaza emiterea — in assembler doar se anexeaza la `ReconciledResult.nota`.
"""
from evaluare.assembler import EvaluationInput, construieste_context
from evaluare.engine.validation import valideaza_metoda_vs_ghid
from evaluare.profil import (
    AGRICOL,
    APARTAMENT_GARANTARE,
    CASA_TEREN_GARANTARE,
    COMERCIAL_INCHIRIAT,
    INDUSTRIAL,
)

# ── Unit: valideaza_metoda_vs_ghid ────────────────────────────────────────────────────────────────

def test_cost_plus_gev520_da_avertisment():
    msg = valideaza_metoda_vs_ghid("cost", CASA_TEREN_GARANTARE)
    assert msg is not None
    assert "GEV 520" in msg
    assert "acordul scris" in msg
    assert "creditor" in msg.lower()


def test_cost_plus_gev520_apartament_da_avertisment():
    # Apartament la garantare e tot GEV_520 -> avertisment.
    assert valideaza_metoda_vs_ghid("cost", APARTAMENT_GARANTARE) is not None


def test_cost_plus_alt_ghid_da_none():
    # Cost dar ghid != GEV_520 (GEV_630) -> fara avertisment.
    assert valideaza_metoda_vs_ghid("cost", INDUSTRIAL) is None       # GEV_630
    assert valideaza_metoda_vs_ghid("cost", COMERCIAL_INCHIRIAT) is None  # GEV_630
    assert valideaza_metoda_vs_ghid("cost", AGRICOL) is None          # GEV_630


def test_piata_plus_gev520_da_none():
    # Alta metoda (piata) cu GEV_520 -> fara avertisment (comportament neschimbat).
    assert valideaza_metoda_vs_ghid("piata", CASA_TEREN_GARANTARE) is None


def test_alte_metode_plus_gev520_da_none():
    # ponderata / venit / dcf cu GEV_520 -> fara avertisment (doar "cost" e gardat).
    for metoda in ("ponderata", "venit", "dcf"):
        assert valideaza_metoda_vs_ghid(metoda, CASA_TEREN_GARANTARE) is None


# ── Integrare assembler: avertismentul ajunge pe nota reconcilierii ───────────────────────────────

def _input(metoda):
    return EvaluationInput(
        meta={"client_nume": "X", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF",
              "evaluator_nume": "E", "evaluator_legitimatie": "1",
              "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        land={"suprafata": "500"},
        building={"au": "100", "acd": "120", "an_referinta": 2025,
                  "elements": [{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                                "cost_unitar": "2000", "an_pif": 2015}],
                  "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                          {"varsta": 15, "depreciere": "0.15"}]},
        comparables=[{"pret": "250000", "suprafata": "120"},
                     {"pret": "260000", "suprafata": "125"},
                     {"pret": "240000", "suprafata": "118"}],
        valoare_teren="100000", metoda=metoda,
    )


def test_assembler_cost_garantare_ataseaza_avertisment_pe_nota():
    # Profil implicit = CASA_TEREN_GARANTARE (GEV_520) + metoda cost -> avertismentul pe nota.
    ctx = construieste_context(_input("cost"), client=None)
    assert ctx.profil.ghid == "GEV_520"
    assert "GEV 520" in ctx.reconciled.nota
    assert "acordul scris" in ctx.reconciled.nota
    # Non-blocant: valoarea finala se emite normal.
    assert ctx.reconciled.valoare_finala > 0
    assert ctx.reconciled.metoda_selectata == "cost"


def test_assembler_piata_garantare_fara_avertisment():
    # Metoda piata cu GEV_520 -> nu apare avertismentul de cost (comportament neschimbat).
    ctx = construieste_context(_input("piata"), client=None)
    assert ctx.profil.ghid == "GEV_520"
    assert "GEV 520 §31" not in ctx.reconciled.nota
    assert "acordul scris" not in ctx.reconciled.nota


def test_assembler_cost_alt_ghid_fara_avertisment():
    # Tip industrial -> profil GEV_630; metoda cost -> garda NU se aplica (alt ghid).
    inp = _input("cost")
    inp.tip_proprietate = "industrial"
    ctx = construieste_context(inp, client=None)
    assert ctx.profil.ghid == "GEV_630"
    assert "acordul scris" not in ctx.reconciled.nota
