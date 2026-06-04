from decimal import Decimal

from evaluare.assembler import EvaluationInput, construieste_context


def _input_dcf():
    return EvaluationInput(
        meta={"client_nume": "C", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF",
              "evaluator_nume": "E", "evaluator_legitimatie": "1",
              "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        land={"suprafata": "200"},
        building={"au": "300", "acd": "320", "an_referinta": 2025, "elements": [],
                  "depreciation_points": []},
        valoare_teren="0", metoda="dcf",
        date_dcf={"fluxuri": ["100000", "100000", "100000"], "rata_actualizare": "0.10",
                  "valoare_reziduala": "0"},
    )


def test_evaluare_prin_dcf():
    ctx = construieste_context(_input_dcf(), client=None)
    assert ctx.reconciled.metoda_selectata == "venit"
    assert ctx.reconciled.valoare_finala == Decimal("248685.20")
    assert ctx.dcf_valoare == Decimal("248685.20")
