from decimal import Decimal

from evaluare.models.property import BuildingData, CostElement, DepreciationPoint
from evaluare.engine.cost import (
    compute_cib,
    compute_vcp,
    interpolate_depreciation,
    compute_cin,
    evaluate_cost,
)


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
