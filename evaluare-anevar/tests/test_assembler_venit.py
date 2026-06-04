from decimal import Decimal

from evaluare.assembler import EvaluationInput, construieste_context


def _input_venit():
    return EvaluationInput(
        meta={"client_nume": "C", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF",
              "evaluator_nume": "E", "evaluator_legitimatie": "1",
              "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        land={"suprafata": "200"},
        building={"au": "300", "acd": "320", "an_referinta": 2025, "elements": [],
                  "depreciation_points": []},
        valoare_teren="0", metoda="venit",
        date_venit={"venit_brut_potential": "100000", "grad_neocupare": "0.05",
                    "cheltuieli_exploatare": "20000", "rata_capitalizare": "0.08"},
    )


def test_evaluare_prin_venit():
    ctx = construieste_context(_input_venit(), client=None)
    assert ctx.reconciled.metoda_selectata == "venit"
    assert ctx.reconciled.valoare_finala == Decimal("937500.00")
    assert ctx.venit_result is not None and ctx.venit_result.noi == Decimal("75000.00")
    assert ctx.date_venit is not None
