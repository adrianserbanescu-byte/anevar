from evaluare.discovery.scoring import metodologie


def test_metodologie_are_5_atribute_cu_formula_pondere_cota():
    m = metodologie()
    assert len(m) == 5
    an = m[0]
    assert an["atribut"] == "An"
    assert an["pondere"] == 5
    assert an["cota"] == "33%"
    assert "25" in an["formula"]
    assert {r["atribut"] for r in m} == {"An", "Stare", "Finisaj", "Încălzire", "Teren"}
