
from evaluare.assembler import EvaluationInput, construieste_context


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


def test_context_are_profil_default():
    ctx = construieste_context(_input("cost"), client=None)
    assert ctx.profil is not None
    assert ctx.profil.tip_activ == "casa"  # implicit, fără tip_proprietate


def test_tip_proprietate_conduce_profilul():
    # Tipul ales în wizard (Pas 2) determină profilul raportului (tip activ + ghid GEV).
    asteptari = {"apartament": ("apartament", "GEV_520"), "industrial": ("industrial", "GEV_630"),
                 "agricol": ("agricol", "GEV_630"), "special": ("special", "GEV_630"),
                 "casa": ("casa", "GEV_520")}
    for tip, (tip_activ, ghid) in asteptari.items():
        inp = _input("cost")
        inp.tip_proprietate = tip
        ctx = construieste_context(inp, client=None)
        assert ctx.profil.tip_activ == tip_activ, tip
        assert ctx.profil.ghid == ghid, tip


def test_tip_necunoscut_pastreaza_profil_implicit():
    inp = _input("cost")
    inp.tip_proprietate = "ceva_inexistent"
    ctx = construieste_context(inp, client=None)
    assert ctx.profil.tip_activ == "casa"


def test_reconciliere_identica_pe_cele_trei_metode():
    for metoda in ("cost", "piata", "ponderata"):
        ctx = construieste_context(_input(metoda), client=None)
        assert ctx.reconciled.valoare_finala > 0
        asteptat = {"cost": "cost", "piata": "piata", "ponderata": "ponderata"}[metoda]
        assert ctx.reconciled.metoda_selectata == asteptat
