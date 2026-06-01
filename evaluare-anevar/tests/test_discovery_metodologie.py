from evaluare.discovery.scoring import metodologie


def test_metodologie_are_6_atribute_cu_formula_pondere_cota():
    m = metodologie()
    assert len(m) == 6
    assert m[0]["atribut"] == "Supr. construită"
    assert m[0]["pondere"] == 5
    an = next(r for r in m if r["atribut"] == "An")
    assert an["pondere"] == 5
    assert an["cota"] == "25%"        # 5/20
    assert "25" in an["formula"]
    assert {r["atribut"] for r in m} == {
        "Supr. construită", "An", "Stare", "Finisaj", "Încălzire", "Teren"}
