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


def test_evaluation_meta_big_esg_fields_defaults():
    """Campurile BIG/ESG noi sunt optionale -> constructiile existente raman valide.

    Acelasi set minim de campuri ca testul de baza; verificam doar valorile implicite
    ale campurilor adaugate (gap S-4 cod_postal, S-5 riscuri_fizice, G7 CPE).
    """
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
    assert m.cod_postal is None                # default
    assert m.riscuri_fizice == []              # default factory (lista goala)
    assert m.certificat_energetic is None      # default
    # lista implicita e o instanta proprie, nu un default mutabil partajat
    m.riscuri_fizice.append("seismic")
    other = EvaluationMeta(
        client_nume="Alt Client",
        adresa="Str. Alta nr. 2",
        numar_cadastral="654321",
        carte_funciara="CF654321",
        evaluator_nume="Maria Ionescu",
        evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16",
        data_raportului="2026-01-16",
    )
    assert other.riscuri_fizice == []


def test_evaluation_meta_big_esg_fields_set():
    """Campurile BIG/ESG pot fi populate (cod postal, riscuri fizice, CPE)."""
    m = EvaluationMeta(
        client_nume="Ion Popescu",
        adresa="Str. Exemplu nr. 1, Bucuresti",
        numar_cadastral="123456",
        carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu",
        evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16",
        data_raportului="2026-01-16",
        cod_postal="010101",
        riscuri_fizice=["inundabilitate", "seismic"],
        certificat_energetic="Clasa B",
    )
    assert m.cod_postal == "010101"
    assert m.riscuri_fizice == ["inundabilitate", "seismic"]
    assert m.certificat_energetic == "Clasa B"


def test_narrative_section():
    s = NarrativeSection(capitol="Analiza pietei", text="Piata locala...")
    assert s.capitol == "Analiza pietei"
    assert s.text == "Piata locala..."
