from decimal import Decimal

from evaluare.engine.validation import (
    valideaza_comparabile,
    valideaza_depreciere,
    valideaza_proprietate,
)
from evaluare.models.comparable import Adjustment, Comparable
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData


def _building(au="322.75", acd="351.46", c_nf="0", justif_nf="") -> BuildingData:
    return BuildingData(
        au=Decimal(au), acd=Decimal(acd), an_referinta=2025,
        functional_depreciation=Decimal(c_nf),
        elements=[CostElement(element="S", cod="X", um="mp",
                              cantitate=Decimal("10"), cost_unitar=Decimal("100"),
                              an_pif=2015)],
        depreciation_points=[DepreciationPoint(varsta=10, depreciere=Decimal("0.1"))],
        justificare_depreciere=justif_nf,
    )


def test_blocheaza_cand_au_mai_mare_decat_acd():
    land = LandData(suprafata=Decimal("500"))
    building = _building(au="400", acd="351.46")
    issues = valideaza_proprietate(land, building)
    assert any(i.nivel == "blocheaza" and "Au" in i.mesaj for i in issues)


def test_blocheaza_cand_suprafata_teren_zero():
    land = LandData(suprafata=Decimal("0"))
    building = _building()
    issues = valideaza_proprietate(land, building)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_proprietate_valida_fara_probleme():
    land = LandData(suprafata=Decimal("500"))
    building = _building()
    issues = valideaza_proprietate(land, building)
    assert all(i.nivel != "blocheaza" for i in issues)


def test_blocheaza_sub_3_comparabile():
    comps = [Comparable(pret=Decimal("1"), suprafata=Decimal("1"))]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_alerteaza_ajustare_bruta_peste_25_la_suta():
    comps = [
        Comparable(pret=Decimal("1"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("1"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("1"), suprafata=Decimal("1"),
                   adjustments=[Adjustment(element="A", tip="procentuala",
                                           valoare=Decimal("0.30"))]),
    ]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "alerteaza" and "ajustare" in i.mesaj.lower() for i in issues)


def test_alerteaza_outlier_dupa_mediana():
    comps = [
        Comparable(pret=Decimal("500"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("510"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("2000"), suprafata=Decimal("1")),  # outlier
    ]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "alerteaza" and "outlier" in i.mesaj.lower() for i in issues)


def test_blocheaza_depreciere_functionala_fara_justificare():
    building = _building(c_nf="0.10", justif_nf="")
    issues = valideaza_depreciere(building)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_depreciere_functionala_cu_justificare_ok():
    building = _building(c_nf="0.10", justif_nf="uzura interioara avansata")
    issues = valideaza_depreciere(building)
    assert all(i.nivel != "blocheaza" for i in issues)


def test_valideaza_comparabile_teren_m5_simetric_cu_piata():
    # #7: gardile M5 (min 3, outlier, limita ajustare, pret<=0) aplicate si la comparabilele de TEREN.
    from decimal import Decimal

    from evaluare.engine.validation import valideaza_comparabile_teren
    from evaluare.models.comparable import Adjustment, LandComparable

    def _t(pret_mp, adj=None):
        return LandComparable(pret_mp=Decimal(pret_mp), suprafata=Decimal("500"),
                              adjustments=adj or [])

    # <3 comparabile de teren -> blocheaza
    iss = valideaza_comparabile_teren([_t("100")])
    assert any(i.nivel == "blocheaza" and "teren" in i.mesaj for i in iss)
    # 3 comparabile: unul outlier (300 vs mediana 100) + unul cu ajustare bruta 40% (> 25%)
    comps = [_t("100"), _t("300"),
             _t("100", [Adjustment(element="x", tip="procentuala",
                                   valoare=Decimal("0.40"), etapa="proprietate")])]
    iss2 = valideaza_comparabile_teren(comps)
    assert any("outlier" in i.mesaj and "teren" in i.mesaj for i in iss2)        # 300 e outlier
    assert any("ajustare bruta" in i.mesaj and "teren" in i.mesaj for i in iss2)  # 0.40 > 0.25


def test_assembler_valideaza_aplica_garda_pe_comparabile_teren():
    # #7: assembler.valideaza ruleaza acum gardile si pe land_comparables (nu doar piata).
    from decimal import Decimal

    from evaluare.assembler import EvaluationInput, valideaza
    from evaluare.models.comparable import LandComparable
    inp = EvaluationInput(
        meta={"client_nume": "X", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF",
              "evaluator_nume": "E", "evaluator_legitimatie": "1", "data_evaluarii": "2026-01-01",
              "data_raportului": "2026-01-01"},
        land={"suprafata": "500"}, building={"au": "100", "acd": "120", "an_referinta": 2025},
        land_comparables=[LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"))],  # doar 1 -> <3
        metoda="cost",
    )
    issues = valideaza(inp)
    assert any("comparabile de teren" in i.mesaj for i in issues)   # garda M5 pe teren a rulat


# --------------------------------------------------------------------------- #
# I-9 — OMOGENITATEA comparabilelor (cele 4 capcane Nicolescu) + recenta + proximitate.
# Toate sunt ALERTE (nu blocheaza); aditive peste gardile M5 existente.
# --------------------------------------------------------------------------- #
def _comp(pret, suprafata="100", tip_oferta="oferta", data_oferta=None, sursa="manual", adj=None):
    from evaluare.models.comparable import Comparable
    return Comparable(pret=Decimal(str(pret)), suprafata=Decimal(suprafata), tip_oferta=tip_oferta,
                      data_oferta=data_oferta, sursa=sursa, adjustments=adj or [])


def test_i9_segment_pret_unic_alerteaza():
    # capcana (a): toate preturile unitare brute intr-o banda foarte ingusta (<3%) -> alerta segment unic.
    from evaluare.engine.validation import valideaza_omogenitate
    comps = [_comp(500000), _comp(501000), _comp(502000)]   # dispersie ~0.4% < 3%
    iss = valideaza_omogenitate(comps)
    assert any(i.nivel == "alerteaza" and "segment de pret unic" in i.mesaj for i in iss)


def test_i9_segment_diversificat_nu_alerteaza():
    # preturi unitare bine dispersate -> NU se semnaleaza segment unic.
    from evaluare.engine.validation import valideaza_omogenitate
    comps = [_comp(400000), _comp(500000), _comp(620000)]   # dispersie mare
    iss = valideaza_omogenitate(comps)
    assert not any("segment de pret unic" in i.mesaj for i in iss)


def test_i9_recenta_comparabila_veche_alerteaza():
    # comparabila cu data oferta > 6 luni fata de data evaluarii -> alerta de recenta.
    from evaluare.engine.validation import valideaza_omogenitate
    comps = [_comp(400000, data_oferta="2024-01-10"),
             _comp(500000, data_oferta="2025-06-01"),
             _comp(620000, data_oferta="2025-06-01")]
    iss = valideaza_omogenitate(comps, data_evaluarii="2025-06-15")
    # prima e veche de ~17 luni
    assert any(i.nivel == "alerteaza" and "vechime" in i.mesaj for i in iss)


def test_i9_recenta_data_ro_format_si_recent_ok():
    # format RO (15.01.2025) parsabil; comparabile recente (< 6 luni) -> fara alerta de recenta.
    from evaluare.engine.validation import valideaza_omogenitate
    comps = [_comp(400000, data_oferta="15.05.2025"),
             _comp(500000, data_oferta="01.06.2025"),
             _comp(620000, data_oferta="10.06.2025")]
    iss = valideaza_omogenitate(comps, data_evaluarii="2025-06-15")
    assert not any("vechime" in i.mesaj for i in iss)


def test_i10_oferta_fara_ajustare_tranzactie_alerteaza():
    # I-10: comparabil pe OFERTA fara nicio ajustare in etapa de tranzactie -> alerta risc speculativ.
    from evaluare.engine.validation import valideaza_oferta_tranzactie
    from evaluare.models.comparable import Adjustment
    comps = [_comp(500000, tip_oferta="oferta"),
             _comp(510000, tip_oferta="tranzactie"),
             _comp(520000, tip_oferta="oferta",
                   adj=[Adjustment(element="Negociere", tip="procentuala",
                                   valoare=Decimal("-0.05"), etapa="tranzactie")])]
    iss = valideaza_oferta_tranzactie(comps)
    msgs = [i.mesaj for i in iss]
    assert any("OFERTA fara nicio ajustare" in m for m in msgs)
    # comp1 e tranzactie, comp2 are ajustare tranzactie -> doar comp0 alerteaza
    assert sum("OFERTA fara nicio ajustare" in m for m in msgs) == 1


def test_m2_anti_contaminare_grila_notariala_alerteaza():
    # m-2: o comparabila cu sursa grila/studiu notarial (HCD 74) -> alerta anti-contaminare.
    from evaluare.engine.validation import valideaza_anti_contaminare
    comps = [_comp(500000, sursa="grila notariala Camera Notarilor 2025"),
             _comp(510000, sursa="https://imobiliare.ro/anunt-1"),
             _comp(520000, sursa="HCD 74 art 111")]
    iss = valideaza_anti_contaminare(comps)
    msgs = [i.mesaj for i in iss if i.nivel == "alerteaza"]
    assert sum("grila/studiu notarial" in m for m in msgs) == 2   # comp0 + comp2


def test_valideaza_comparabile_integreaza_euristicile_aditive():
    # gardile M5 raman; in plus, valideaza_comparabile ruleaza I-9/I-10/m-2 (alerte) si NU schimba blocarile.
    from evaluare.engine.validation import valideaza_comparabile
    comps = [_comp(500000, sursa="grila notariala"),   # m-2
             _comp(501000, tip_oferta="oferta"),        # I-10 + segment unic (I-9)
             _comp(502000, tip_oferta="oferta")]
    iss = valideaza_comparabile(comps, data_evaluarii="2025-06-15")
    msgs = " ".join(i.mesaj for i in iss)
    assert "segment de pret unic" in msgs       # I-9
    assert "OFERTA fara nicio ajustare" in msgs  # I-10
    assert "grila/studiu notarial" in msgs       # m-2
    # nu blocheaza (sunt 3 comparabile valide)
    assert all(i.nivel == "alerteaza" for i in iss)


def test_i9_proximitate_teren_alta_localitate_alerteaza():
    # I-9 (teren) capcana (d): comparabil de teren din alta localitate, fara ajustare de localizare -> alerta.
    from evaluare.engine.validation import valideaza_proximitate_teren
    from evaluare.models.comparable import Adjustment, LandComparable
    comps = [
        LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"), localizare="Brasov"),
        LandComparable(pret_mp=Decimal("110"), suprafata=Decimal("500"), localizare="Brasov"),
        LandComparable(pret_mp=Decimal("120"), suprafata=Decimal("500"), localizare="Bucuresti"),  # alta
    ]
    iss = valideaza_proximitate_teren(comps, localizare_subiect="Brasov")
    assert any(i.nivel == "alerteaza" and "alta localitate" in i.mesaj for i in iss)
    # daca acelasi comparabil are ajustare de localizare -> NU alerteaza
    comps[2] = LandComparable(pret_mp=Decimal("120"), suprafata=Decimal("500"), localizare="Bucuresti",
                              adjustments=[Adjustment(element="Localizare", tip="procentuala",
                                                      valoare=Decimal("-0.1"))])
    iss2 = valideaza_proximitate_teren(comps, localizare_subiect="Brasov")
    assert not any("alta localitate" in i.mesaj for i in iss2)


def test_i10_oferta_tranzactie_teren_fara_etapa_alerteaza():
    # I-10 (teren): niciun comparabil de teren cu ajustare in etapa de tranzactie -> alerta speculativa.
    from evaluare.engine.validation import valideaza_oferta_tranzactie_teren
    from evaluare.models.comparable import Adjustment, LandComparable
    comps = [LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500")),
             LandComparable(pret_mp=Decimal("110"), suprafata=Decimal("500"))]
    iss = valideaza_oferta_tranzactie_teren(comps)
    assert any(i.nivel == "alerteaza" and "etapa de tranzactie" in i.mesaj for i in iss)
    # daca macar unul are ajustare de tranzactie -> NU alerteaza
    comps[0] = LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"),
                              adjustments=[Adjustment(element="Negociere", tip="procentuala",
                                                      valoare=Decimal("-0.05"), etapa="tranzactie")])
    iss2 = valideaza_oferta_tranzactie_teren(comps)
    assert not any("etapa de tranzactie" in i.mesaj for i in iss2)


def test_valideaza_comparabile_teren_integreaza_euristicile():
    # valideaza_comparabile_teren ruleaza acum si omogenitate + proximitate + oferta->tranzactie (alerte).
    from evaluare.engine.validation import valideaza_comparabile_teren
    from evaluare.models.comparable import LandComparable
    comps = [LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"), localizare="Brasov"),
             LandComparable(pret_mp=Decimal("101"), suprafata=Decimal("500"), localizare="Brasov"),
             LandComparable(pret_mp=Decimal("102"), suprafata=Decimal("500"), localizare="Cluj")]
    iss = valideaza_comparabile_teren(comps, localizare_subiect="Brasov", data_evaluarii="2025-06-15")
    msgs = " ".join(i.mesaj for i in iss)
    assert "segment de pret unic" in msgs        # I-9 omogenitate
    assert "alta localitate" in msgs             # I-9 proximitate (Cluj)
    assert "etapa de tranzactie" in msgs         # I-10 (niciuna are tranzactie)
