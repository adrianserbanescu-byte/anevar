from evaluare.models.meta import EvaluationMeta
from evaluare.models.narrative import NarrativeSection


def test_evaluation_meta_required_and_defaults():
    m = EvaluationMeta(
        client_nume="Ion Popescu",
        adresa="Str. Exemplu nr. 1, Bucuresti",
        numar_cadastral="123456",
        carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu",
        evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16",
        data_raportului="2026-01-16",
    )
    assert m.client_tip == "Persoana fizica"          # default
    assert m.scop == "Garantarea creditului ipotecar"  # default
    assert m.moneda == "LEI"                            # default
    assert m.client_nume == "Ion Popescu"


def test_narrative_section():
    s = NarrativeSection(capitol="Analiza pietei", text="Piata locala...")
    assert s.capitol == "Analiza pietei"
    assert s.text == "Piata locala..."
