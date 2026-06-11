"""Regresie RUNDA 17 (hardening robustete, DoS): R17-1 + R17-2 prin Field(max_length=...).

Aceeasi clasa de DoS inchisa in RUNDA 15 pentru `riscuri_fizice` (30) / `beneficiari_reali` (200):
listele de comparabile + elemente erau omise. Fix-uri aditive, backward-compatible (valorile
normale trec; peste plafon -> ValidationError/422 inainte de motor / serializare docx).

R17-1 (DoS CPU/memorie): liste de comparabile nemarginite.
  - `Comparable` / `LandComparable` / `RentComparable` `.adjustments` -> max_length=50.
  - Cele 3 scheme grila (`GrilaTerenRequest`/`GrilaCasaRequest`/`GrilaChiriiRequest`)
    `.comparabile` -> max_length=200.
R17-2 (amplificator .docx / memorie): liste de elemente nemarginite.
  - `BuildingData.elements` -> 100, `.depreciation_points` -> 50.
  - `LandData.utilitati` -> 30.
  - `ReportContext.photos` / `.documente` (data-URL base64) -> 30 fiecare.
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from evaluare.models.comparable import (
    Adjustment,
    Comparable,
    LandComparable,
    RentComparable,
)
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.report_context import ReportContext
from evaluare.models.results import ReconciledResult
from evaluare.web.schemas import GrilaCasaRequest, GrilaChiriiRequest, GrilaTerenRequest


def _adj() -> Adjustment:
    return Adjustment(element="Localizare", tip="procentuala", valoare=Decimal("-0.05"))


def _comp() -> Comparable:
    return Comparable(pret=Decimal("500000"), suprafata=Decimal("100"))


def _land_comp() -> LandComparable:
    return LandComparable(pret_mp=Decimal("80"), suprafata=Decimal("450"))


def _rent_comp() -> RentComparable:
    return RentComparable(chirie_mp=Decimal("10"), suprafata=Decimal("60"))


def _cost_el() -> CostElement:
    return CostElement(element="Structura", cod="X", um="mp",
                       cantitate=Decimal("100"), cost_unitar=Decimal("10"), an_pif=2015)


# ------------------------------------------------ R17-1 adjustments <=50 (toate 3 comparabilele)
def test_comparable_adjustments_peste_50_respins():
    with pytest.raises(ValidationError):
        Comparable(pret=Decimal("500000"), suprafata=Decimal("100"),
                   adjustments=[_adj() for _ in range(51)])


def test_land_comparable_adjustments_peste_50_respins():
    with pytest.raises(ValidationError):
        LandComparable(pret_mp=Decimal("80"), suprafata=Decimal("450"),
                       adjustments=[_adj() for _ in range(51)])


def test_rent_comparable_adjustments_peste_50_respins():
    with pytest.raises(ValidationError):
        RentComparable(chirie_mp=Decimal("10"), suprafata=Decimal("60"),
                       adjustments=[_adj() for _ in range(51)])


def test_adjustments_lista_uriasa_respinsa():
    with pytest.raises(ValidationError):
        Comparable(pret=Decimal("500000"), suprafata=Decimal("100"),
                   adjustments=[_adj() for _ in range(200_000)])


def test_adjustments_exact_50_ok():
    c = Comparable(pret=Decimal("500000"), suprafata=Decimal("100"),
                   adjustments=[_adj() for _ in range(50)])
    assert len(c.adjustments) == 50


def test_adjustments_normale_ok():
    # Backward-compat: o grila reala are cateva elemente de comparatie.
    c = Comparable(pret=Decimal("500000"), suprafata=Decimal("100"),
                   adjustments=[_adj(), _adj(), _adj()])
    assert len(c.adjustments) == 3


# ------------------------------------------------ R17-1 comparabile <=200 (cele 3 scheme grila)
def test_grila_teren_comparabile_peste_200_respins():
    with pytest.raises(ValidationError):
        GrilaTerenRequest(suprafata_subiect=Decimal("450"),
                          comparabile=[_land_comp() for _ in range(201)])


def test_grila_casa_comparabile_peste_200_respins():
    with pytest.raises(ValidationError):
        GrilaCasaRequest(suprafata_subiect=Decimal("100"),
                         comparabile=[_comp() for _ in range(201)])


def test_grila_chirii_comparabile_peste_200_respins():
    with pytest.raises(ValidationError):
        GrilaChiriiRequest(suprafata_subiect=Decimal("60"),
                           comparabile=[_rent_comp() for _ in range(201)])


def test_grila_casa_comparabile_lista_uriasa_respinsa():
    with pytest.raises(ValidationError):
        GrilaCasaRequest(suprafata_subiect=Decimal("100"),
                         comparabile=[_comp() for _ in range(100_000)])


def test_grila_casa_comparabile_exact_200_ok():
    r = GrilaCasaRequest(suprafata_subiect=Decimal("100"),
                         comparabile=[_comp() for _ in range(200)])
    assert len(r.comparabile) == 200


def test_grila_comparabile_normale_ok():
    # Backward-compat: uzul real e 3-6 comparabile.
    r = GrilaTerenRequest(suprafata_subiect=Decimal("450"),
                          comparabile=[_land_comp() for _ in range(4)])
    assert len(r.comparabile) == 4


# ------------------------------------------------ R17-2 BuildingData.elements <=100
def test_building_elements_peste_100_respins():
    with pytest.raises(ValidationError):
        BuildingData(au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
                     elements=[_cost_el() for _ in range(101)])


def test_building_elements_uriase_respinse():
    with pytest.raises(ValidationError):
        BuildingData(au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
                     elements=[_cost_el() for _ in range(50_000)])


def test_building_elements_exact_100_ok():
    b = BuildingData(au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
                     elements=[_cost_el() for _ in range(100)])
    assert len(b.elements) == 100


# ------------------------------------------------ R17-2 BuildingData.depreciation_points <=50
def test_building_depreciation_points_peste_50_respins():
    pts = [DepreciationPoint(varsta=i, depreciere=Decimal("0.1")) for i in range(51)]
    with pytest.raises(ValidationError):
        BuildingData(au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
                     depreciation_points=pts)


def test_building_depreciation_points_exact_50_ok():
    pts = [DepreciationPoint(varsta=i, depreciere=Decimal("0.1")) for i in range(50)]
    b = BuildingData(au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
                     depreciation_points=pts)
    assert len(b.depreciation_points) == 50


def test_building_lists_normale_ok():
    # Backward-compat: catalog IROVAL real are cateva zeci de elemente + cateva puncte de depreciere.
    b = BuildingData(
        au=Decimal("100"), acd=Decimal("100"), an_referinta=2025,
        elements=[_cost_el(), _cost_el()],
        depreciation_points=[DepreciationPoint(varsta=30, depreciere=Decimal("0.31"))],
    )
    assert len(b.elements) == 2
    assert len(b.depreciation_points) == 1


# ------------------------------------------------ R17-2 LandData.utilitati <=30
def test_land_utilitati_peste_30_respins():
    with pytest.raises(ValidationError):
        LandData(suprafata=Decimal("500"), utilitati=[f"u{i}" for i in range(31)])


def test_land_utilitati_uriase_respinse():
    with pytest.raises(ValidationError):
        LandData(suprafata=Decimal("500"), utilitati=["x"] * 100_000)


def test_land_utilitati_exact_30_ok():
    land = LandData(suprafata=Decimal("500"), utilitati=[f"u{i}" for i in range(30)])
    assert len(land.utilitati) == 30


def test_land_utilitati_normale_ok():
    land = LandData(suprafata=Decimal("500"), utilitati=["apa", "canalizare", "gaz", "curent"])
    assert len(land.utilitati) == 4


# ------------------------------------------------ R17-2 ReportContext.photos / .documente <=30
def _ctx(**kw) -> ReportContext:
    return ReportContext(
        meta=EvaluationMeta(
            client_nume="Ion Popescu", adresa="Str. Exemplu 1",
            numar_cadastral="123456", carte_funciara="CF123456",
            evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
            data_evaluarii="2026-01-16", data_raportului="2026-01-16",
        ),
        land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("100"), acd=Decimal("100"), an_referinta=2025),
        reconciled=ReconciledResult(valoare_finala=Decimal("1400"), metoda_selectata="cost"),
        **kw,
    )


def test_context_photos_peste_30_respins():
    with pytest.raises(ValidationError):
        _ctx(photos=["data:image/png;base64,AAAA"] * 31)


def test_context_documente_peste_30_respins():
    with pytest.raises(ValidationError):
        _ctx(documente=["data:application/pdf;base64,AAAA"] * 31)


def test_context_photos_uriase_respinse():
    with pytest.raises(ValidationError):
        _ctx(photos=["x"] * 100_000)


def test_context_photos_documente_exact_30_ok():
    ctx = _ctx(
        photos=["data:image/png;base64,AAAA"] * 30,
        documente=["data:application/pdf;base64,AAAA"] * 30,
    )
    assert len(ctx.photos) == 30
    assert len(ctx.documente) == 30


def test_context_photos_documente_normale_ok():
    ctx = _ctx(photos=["data:image/png;base64,AAAA"], documente=[])
    assert len(ctx.photos) == 1
    assert ctx.documente == []
