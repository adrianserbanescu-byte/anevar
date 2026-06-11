from decimal import Decimal

import pytest

from evaluare.engine.cost import (
    compute_cib,
    compute_cin,
    compute_vcp,
    depreciere_externa_din_pierdere,
    depreciere_fizica_liniara,
    depreciere_functionala_supradimensionare,
    evaluate_cost,
    interpolate_depreciation,
)
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint


def gbf_elements() -> list[CostElement]:
    """Elementele segregate exacte din modelul de referinta GBF."""
    data = [
        ("Infrastructura", "FCV2", "mp", "128.90", "919", 1945),
        ("Structura", "8ZPOROT30PFS", "mp", "128.90", "1398.9", 1945),
        ("Structura", "8ZIDCAR30ES", "mp", "160.06", "2056.0", 1945),
        ("Structura", "8ZPOROT30M", "mp", "62.50", "740.1", 1945),
        ("Finisaje", "SCAMOZ", "buc", "2.00", "8247.1", 1945),
        ("Finisaje", "FOBFS", "mp", "351.46", "2694.7", 2015),
        ("Instalatii electrice", "ELINGR", "mp", "351.46", "339", 2015),
        ("Instalatii sanitare", "LAVWC", "buc", "2.00", "5292.5", 2015),
        ("Instalatii sanitare", "CHINOX", "buc", "2.00", "4112", 2015),
        ("Instalatii de incalzire", "INCCONV", "mp", "351.46", "308", 2015),
        ("Invelitoare", "INVTL", "mp", "154.60", "831", 2015),
    ]
    return [
        CostElement(element=e, cod=c, um=u,
                    cantitate=Decimal(q), cost_unitar=Decimal(cu), an_pif=y)
        for e, c, u, q, cu, y in data
    ]


def test_compute_cib_matches_gbf():
    cib = compute_cib(gbf_elements())
    assert abs(cib - Decimal("2012343")) < Decimal("50")


def test_compute_vcp_matches_gbf():
    vcp = compute_vcp(gbf_elements(), an_referinta=2025)
    assert abs(vcp - Decimal("34.02")) < Decimal("0.05")


def test_interpolate_depreciation_matches_gbf():
    points = [
        DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
        DepreciationPoint(varsta=35, depreciere=Decimal("0.36")),
    ]
    dfn = interpolate_depreciation(Decimal("34.02"), points)
    assert abs(dfn - Decimal("0.3502")) < Decimal("0.0005")


def test_compute_cin_matches_gbf():
    cin = compute_cin(cib=Decimal("2012343"), dfn=Decimal("0.3502"),
                      c_nf=Decimal("0"), c_ex=Decimal("0"))
    assert abs(cin - Decimal("1307558")) < Decimal("100")


def test_evaluate_cost_end_to_end_matches_gbf():
    building = BuildingData(
        au=Decimal("322.75"),
        acd=Decimal("351.46"),
        an_referinta=2025,
        elements=gbf_elements(),
        depreciation_points=[
            DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
            DepreciationPoint(varsta=35, depreciere=Decimal("0.36")),
        ],
    )
    result = evaluate_cost(building, valoare_teren=None)
    assert abs(result.cib - Decimal("2012343")) < Decimal("50")
    assert abs(result.vcp - Decimal("34.02")) < Decimal("0.05")
    assert abs(result.cin - Decimal("1307558")) < Decimal("200")
    assert result.valoare_cost is None


def test_evaluate_cost_adds_land_value():
    building = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        elements=gbf_elements(),
        depreciation_points=[
            DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
            DepreciationPoint(varsta=35, depreciere=Decimal("0.36")),
        ],
    )
    result = evaluate_cost(building, valoare_teren=Decimal("100000"))
    assert result.valoare_cost == result.cin + Decimal("100000")


def test_interpolate_single_point_returns_that_point():
    points = [DepreciationPoint(varsta=20, depreciere=Decimal("0.40"))]
    assert interpolate_depreciation(Decimal("5"), points) == Decimal("0.40")
    assert interpolate_depreciation(Decimal("99"), points) == Decimal("0.40")


def test_evaluate_cost_with_no_elements_gives_zero():
    building = BuildingData(
        au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
        elements=[],
        depreciation_points=[
            DepreciationPoint(varsta=10, depreciere=Decimal("0.10")),
        ],
    )
    result = evaluate_cost(building, valoare_teren=None)
    assert result.cib == Decimal("0")
    assert result.cin == Decimal("0")


# ---------------------------------------------------------------------------
# Depreciere fizica LINIARA pe durata de viata (Bazele evaluarii 2024)
# ---------------------------------------------------------------------------


def test_depreciere_liniara_la_jumatatea_vietii():
    # 30 ani din 60 = 50% depreciere fizica.
    assert depreciere_fizica_liniara(Decimal("30"), Decimal("60")) == Decimal("0.5")


def test_depreciere_liniara_zero_la_constructie_noua():
    assert depreciere_fizica_liniara(Decimal("0"), Decimal("60")) == Decimal("0")


def test_depreciere_liniara_clamp_la_1_peste_durata():
    # O constructie care si-a depasit durata de viata e depreciata fizic 100%, nu peste.
    assert depreciere_fizica_liniara(Decimal("80"), Decimal("60")) == Decimal("1")


def test_depreciere_liniara_durata_invalida_arunca():
    with pytest.raises(ValueError):
        depreciere_fizica_liniara(Decimal("10"), Decimal("0"))


def test_depreciere_liniara_varsta_negativa_arunca():
    with pytest.raises(ValueError):
        depreciere_fizica_liniara(Decimal("-1"), Decimal("60"))


def test_evaluate_cost_metoda_liniara_fara_tabel():
    # Fara depreciation_points, dar cu durata_viata_totala -> metoda liniara.
    building = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        elements=gbf_elements(),
        durata_viata_totala=Decimal("80"),
    )
    result = evaluate_cost(building, valoare_teren=None)
    vcp_exact = compute_vcp(gbf_elements(), an_referinta=2025)
    dfn_asteptat = depreciere_fizica_liniara(vcp_exact, Decimal("80"))
    assert result.depreciere_fizica == dfn_asteptat
    # CIN = CIB * (1 - Dfn) cu C_nf = C_ex = 0.
    assert result.cin == compute_cin(result.cib, dfn_asteptat, Decimal("0"), Decimal("0"))


def test_evaluate_cost_tabelul_are_prioritate_fata_de_liniar():
    # Daca exista AMBELE, tabelul (metoda implicita) castiga — comportament neschimbat.
    points = [DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
              DepreciationPoint(varsta=35, depreciere=Decimal("0.36"))]
    building = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        elements=gbf_elements(), depreciation_points=points,
        durata_viata_totala=Decimal("80"),
    )
    vcp_exact = compute_vcp(gbf_elements(), an_referinta=2025)
    result = evaluate_cost(building)
    assert result.depreciere_fizica == interpolate_depreciation(vcp_exact, points)


def test_evaluate_cost_fara_metoda_de_depreciere_arunca():
    building = BuildingData(
        au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
        elements=gbf_elements(),
    )
    with pytest.raises(ValueError):
        evaluate_cost(building)


# ---------------------------------------------------------------------------
# Depreciere FUNCTIONALA din supradimensionare (cost reproducere - inlocuire)
# ---------------------------------------------------------------------------


def test_depreciere_functionala_supradimensionare():
    # Reproducere 1000, inlocuire 800 -> 20% depreciere functionala.
    c_nf = depreciere_functionala_supradimensionare(Decimal("1000"), Decimal("800"))
    assert c_nf == Decimal("0.2")


def test_depreciere_functionala_zero_fara_supradimensionare():
    assert depreciere_functionala_supradimensionare(Decimal("1000"), Decimal("1000")) == Decimal("0")


def test_depreciere_functionala_inlocuire_peste_reproducere_arunca():
    with pytest.raises(ValueError):
        depreciere_functionala_supradimensionare(Decimal("800"), Decimal("1000"))


def test_depreciere_functionala_reproducere_invalida_arunca():
    with pytest.raises(ValueError):
        depreciere_functionala_supradimensionare(Decimal("0"), Decimal("0"))


# ---------------------------------------------------------------------------
# Depreciere EXTERNA / economica din pierdere de utilitate
# ---------------------------------------------------------------------------


def test_depreciere_externa_din_pierdere():
    # Pierdere 50.000 dintr-o referinta de 500.000 -> 10% depreciere externa.
    c_ex = depreciere_externa_din_pierdere(Decimal("50000"), Decimal("500000"))
    assert c_ex == Decimal("0.1")


def test_depreciere_externa_clamp_la_1():
    assert depreciere_externa_din_pierdere(Decimal("600"), Decimal("500")) == Decimal("1")


def test_depreciere_externa_referinta_invalida_arunca():
    with pytest.raises(ValueError):
        depreciere_externa_din_pierdere(Decimal("100"), Decimal("0"))


def test_cele_trei_forme_se_combina_in_cin():
    # Toate cele trei forme alimenteaza compute_cin, multiplicativ (in cascada).
    cib = Decimal("1000000")
    dfn = depreciere_fizica_liniara(Decimal("20"), Decimal("80"))           # 0.25
    c_nf = depreciere_functionala_supradimensionare(Decimal("1000"), Decimal("900"))  # 0.10
    c_ex = depreciere_externa_din_pierdere(Decimal("30000"), Decimal("300000"))       # 0.10
    cin = compute_cin(cib, dfn, c_nf, c_ex)
    # 1.000.000 * 0.75 * 0.90 * 0.90 = 607.500
    assert cin == Decimal("607500.00") or abs(cin - Decimal("607500")) < Decimal("1")


# ---------------------------------------------------------------------------
# An PIF la nivel de CLADIRE (Building.an_pif) — varsta = an_referinta - an_pif
# ---------------------------------------------------------------------------


def test_building_an_pif_seteaza_varsta_la_nivel_de_cladire():
    # Cu an_pif pe cladire, varsta folosita la depreciere = an_referinta - an_pif
    # (2025 - 1995 = 30), NU varsta cronologica ponderata pe elemente (~34 din GBF).
    points = [DepreciationPoint(varsta=30, depreciere=Decimal("0.30")),
              DepreciationPoint(varsta=40, depreciere=Decimal("0.50"))]
    building = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        an_pif=1995, elements=gbf_elements(), depreciation_points=points,
    )
    result = evaluate_cost(building)
    # Varsta = 30 -> primul nod al tabelului -> Dfn = 0.30 exact.
    assert result.depreciere_fizica == Decimal("0.30")
    assert result.vcp == Decimal("30.00")


def test_building_an_pif_suprascrie_varsta_ponderata_pe_elemente():
    # Elementele au an_pif diferiti (1945 si 2015 -> Vcp ponderat ~34), dar an_pif
    # pe cladire (2010) forteaza varsta = 2025 - 2010 = 15 pentru TOATA cladirea.
    building = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        an_pif=2010, elements=gbf_elements(),
        durata_viata_totala=Decimal("60"),
    )
    result = evaluate_cost(building)
    # Metoda liniara pe varsta de cladire: 15 / 60 = 0.25, NU varsta ponderata (~34/60).
    dfn_asteptat = depreciere_fizica_liniara(Decimal("15"), Decimal("60"))
    assert result.depreciere_fizica == dfn_asteptat
    assert result.vcp == Decimal("15.00")
    # Diferit fata de varsta ponderata pe elemente (sanity check).
    vcp_ponderat = compute_vcp(gbf_elements(), an_referinta=2025)
    assert result.vcp != vcp_ponderat.quantize(Decimal("0.01"))


def test_fara_building_an_pif_comportament_neschimbat():
    # Fara an_pif pe cladire -> varsta = compute_vcp (an_pif per-element), exact ca azi.
    points = [DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
              DepreciationPoint(varsta=35, depreciere=Decimal("0.36"))]
    building_fara = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        elements=gbf_elements(), depreciation_points=points,
    )
    assert building_fara.an_pif is None  # default backward-compat
    result = evaluate_cost(building_fara)
    vcp_ponderat = compute_vcp(gbf_elements(), an_referinta=2025)
    assert result.depreciere_fizica == interpolate_depreciation(vcp_ponderat, points)
    assert result.vcp == vcp_ponderat.quantize(Decimal("0.01"))


def test_building_an_pif_egal_cu_an_referinta_da_varsta_zero():
    # Cladire pusa in functiune chiar in anul de referinta -> varsta 0 -> Dfn liniar 0.
    building = BuildingData(
        au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
        an_pif=2025, elements=gbf_elements(),
        durata_viata_totala=Decimal("60"),
    )
    result = evaluate_cost(building)
    assert result.vcp == Decimal("0.00")
    assert result.depreciere_fizica == Decimal("0")


def test_cost_dfn_interpoleaza_pe_vcp_exact_nu_rotunjit():
    # Politica unica de rotunjire (#3): Dfn se interpoleaza pe vcp EXACT, nu pe vcp rotunjit la 0.01
    # (rotunjirea inainte de interpolare introducea un mic efect de prag). vcp RAPORTAT ramane rotunjit.
    elements = gbf_elements()
    building = BuildingData(
        au=Decimal("351"), acd=Decimal("351"), an_referinta=2025, elements=elements,
        depreciation_points=[DepreciationPoint(varsta=30, depreciere=Decimal("0.30")),
                             DepreciationPoint(varsta=40, depreciere=Decimal("0.50"))],
    )
    vcp_exact = compute_vcp(elements, an_referinta=2025)
    r = evaluate_cost(building)
    assert r.depreciere_fizica == interpolate_depreciation(vcp_exact, building.depreciation_points)
    assert r.vcp == vcp_exact.quantize(Decimal("0.01"))   # vcp raportat = rotunjit (doar afisare)
