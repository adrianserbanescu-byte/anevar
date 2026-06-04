from decimal import Decimal

from evaluare.models.property import (
    BuildingData,
    CostElement,
    DepreciationPoint,
    LandData,
)


def test_cost_element_computes_cost_nou_and_varsta():
    el = CostElement(
        element="Infrastructura",
        cod="FCV2",
        um="mp",
        cantitate=Decimal("128.90"),
        cost_unitar=Decimal("919"),
        an_pif=1945,
    )
    assert el.cost_nou() == Decimal("118459.10")
    assert el.varsta(an_referinta=2025) == 80


def test_building_data_holds_elements_and_areas():
    b = BuildingData(
        ac=None,
        au=Decimal("322.75"),
        acd=Decimal("351.46"),
        an_referinta=2025,
        elements=[
            CostElement(element="Structura", cod="X", um="mp",
                        cantitate=Decimal("100"), cost_unitar=Decimal("10"),
                        an_pif=2015),
        ],
        depreciation_points=[
            DepreciationPoint(varsta=30, depreciere=Decimal("0.31")),
            DepreciationPoint(varsta=35, depreciere=Decimal("0.36")),
        ],
    )
    assert b.acd == Decimal("351.46")
    assert b.functional_depreciation == Decimal("0")
    assert b.external_depreciation == Decimal("0")
    assert len(b.elements) == 1


def test_land_data_basic():
    land = LandData(suprafata=Decimal("500"), categorie="intravilan")
    assert land.suprafata == Decimal("500")
    assert land.categorie == "intravilan"
