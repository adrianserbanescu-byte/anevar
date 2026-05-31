from evaluare.models.meta import EvaluationMeta
from evaluare.report.anonymizer import build_anonymizer


def _meta() -> EvaluationMeta:
    return EvaluationMeta(
        client_nume="Ion Popescu",
        adresa="Str. Exemplu nr. 1, Bucuresti",
        numar_cadastral="123456",
        carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )


def test_mask_removes_personal_data():
    anon = build_anonymizer(_meta())
    text = "Proprietatea lui Ion Popescu de pe Str. Exemplu nr. 1, Bucuresti, cad. 123456, CF123456."
    masked = anon.mask(text)
    assert "Ion Popescu" not in masked
    assert "Str. Exemplu nr. 1, Bucuresti" not in masked
    assert "123456" not in masked
    assert "CF123456" not in masked
    assert "[CLIENT]" in masked
    assert "[ADRESA]" in masked
    assert "[CADASTRAL]" in masked
    assert "[CF]" in masked


def test_unmask_restores_personal_data():
    anon = build_anonymizer(_meta())
    masked = "Proprietatea [CLIENT] de pe [ADRESA], cad. [CADASTRAL], [CF]."
    restored = anon.unmask(masked)
    assert "Ion Popescu" in restored
    assert "Str. Exemplu nr. 1, Bucuresti" in restored
    assert "123456" in restored
    assert "CF123456" in restored


def test_mask_then_unmask_roundtrip():
    anon = build_anonymizer(_meta())
    text = "Ion Popescu, Str. Exemplu nr. 1, Bucuresti, 123456, CF123456."
    assert anon.unmask(anon.mask(text)) == text


def test_empty_fields_are_skipped():
    meta = _meta()
    meta.carte_funciara = ""
    anon = build_anonymizer(meta)
    # nu trebuie sa inlocuiasca string gol (ar corupe tot textul)
    assert anon.mask("text oarecare") == "text oarecare"
