"""Regresie pe corecturile de corectitudine din auto-review (rutare venit/DCF, ponderi, NOI)."""
from decimal import Decimal

import pytest
from pydantic import ValidationError

from evaluare.assembler import EvaluationInput, construieste_context
from evaluare.engine.venit import DateVenit, evalueaza_venit


def _meta():
    return {"client_nume": "C", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF",
            "evaluator_nume": "E", "evaluator_legitimatie": "1",
            "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"}


def _building():
    return {"au": "100", "acd": "120", "an_referinta": 2025, "elements": [],
            "depreciation_points": []}


# C2 — metoda ceruta fara date -> eroare clara, nu fallback tacut
def test_venit_cerut_fara_date_ridica_eroare():
    inp = EvaluationInput(meta=_meta(), land={"suprafata": "1"}, building=_building(),
                          comparables=[{"pret": "300000", "suprafata": "120"},
                                       {"pret": "310000", "suprafata": "122"},
                                       {"pret": "290000", "suprafata": "118"}],
                          valoare_teren="0", metoda="venit")
    with pytest.raises(ValueError):
        construieste_context(inp, client=None)


def test_dcf_cerut_fara_date_ridica_eroare():
    inp = EvaluationInput(meta=_meta(), land={"suprafata": "1"}, building=_building(),
                          comparables=[{"pret": "300000", "suprafata": "120"},
                                       {"pret": "310000", "suprafata": "122"},
                                       {"pret": "290000", "suprafata": "118"}],
                          valoare_teren="0", metoda="dcf")
    with pytest.raises(ValueError):
        construieste_context(inp, client=None)


# C1 — DCF ales nu e suprascris de capitalizare (si invers): metoda decide care intra
def test_dcf_ales_foloseste_dcf_chiar_daca_exista_si_capitalizare():
    inp = EvaluationInput(
        meta=_meta(), land={"suprafata": "1"}, building=_building(), valoare_teren="0",
        metoda="dcf",
        date_venit={"venit_brut_potential": "80000", "rata_capitalizare": "0.10"},  # capitalizare = 800000
        date_dcf={"fluxuri": ["110000"], "rata_actualizare": "0.10", "valoare_reziduala": "0"},  # DCF = 100000
    )
    ctx = construieste_context(inp, client=None)
    assert ctx.reconciled.valoare_finala == Decimal("100000.00")   # DCF, nu 800000


# C3 — pondere_piata in afara [0,1] e respinsa la validare
def test_pondere_piata_peste_unu_respinsa():
    with pytest.raises(ValidationError):
        EvaluationInput(meta=_meta(), land={"suprafata": "1"}, building=_building(),
                        metoda="ponderata", pondere_piata=Decimal("2"))


# I1 — NOI <= 0 ridica eroare (cheltuieli > venit efectiv)
def test_noi_negativ_ridica_eroare():
    with pytest.raises(ValueError):
        evalueaza_venit(DateVenit(venit_brut_potential=Decimal("50000"),
                                  cheltuieli_exploatare=Decimal("60000"),
                                  rata_capitalizare=Decimal("0.08")))
