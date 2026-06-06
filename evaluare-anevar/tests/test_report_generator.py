from decimal import Decimal

from docx import Document

from evaluare.models.meta import EvaluationMeta
from evaluare.models.narrative import NarrativeSection
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.report_context import ReportContext
from evaluare.models.results import CostResult, ReconciledResult
from evaluare.report.generator import genereaza_raport


def _ctx() -> ReportContext:
    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1, Bucuresti",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    return ReportContext(
        meta=meta,
        land=LandData(suprafata=Decimal("500"), categorie="intravilan"),
        building=BuildingData(
            au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
            elements=[
                CostElement(element="Structura", cod="X", um="mp",
                            cantitate=Decimal("100"), cost_unitar=Decimal("2000"),
                            an_pif=2015),
            ],
            depreciation_points=[DepreciationPoint(varsta=10, depreciere=Decimal("0.1"))],
        ),
        cost_result=CostResult(cib=Decimal("200000"), vcp=Decimal("10"),
                               depreciere_fizica=Decimal("0.10"), cin=Decimal("180000"),
                               valoare_cost=Decimal("280000")),
        reconciled=ReconciledResult(valoare_finala=Decimal("280000"),
                                    metoda_selectata="cost"),
        narrative=[NarrativeSection(capitol="Analiza celei mai bune utilizari (CMBU)",
                                    text="Cea mai buna utilizare este cea rezidentiala.")],
    )


def _all_text(path) -> str:
    doc = Document(str(path))
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


def test_genereaza_raport_creeaza_fisier(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    assert out.exists()
    # se deschide ca document Word valid
    Document(str(out))


def test_raportul_contine_datele_cheie(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    text = _all_text(out)
    assert "Ion Popescu" in text
    assert "Garantarea creditului ipotecar" in text
    assert "280.000" in text                       # valoarea finala (formatata)
    assert "CIN" in text or "180.000" in text       # tabel cost
    assert "Cea mai buna utilizare" in text        # narativ inserat


def test_tipul_valorii_citeaza_sursa(tmp_path):
    # SEV 102 §20.4 + SEV 106 §30.6(i): slug-ul de tip valoare („piata", cum îl setează un profil)
    # devine denumire lizibilă + sursa definiției în raport (nu mai afișează slug-ul brut).
    ctx = _ctx()
    ctx.meta.tip_valoare = "piata"
    out = tmp_path / "raport.docx"
    genereaza_raport(ctx, out)
    text = _all_text(out)
    assert "Tipul valorii" in text
    assert "valoare de piață" in text                # slug -> denumire lizibilă
    assert "SEV 102" in text                          # sursa/definiția tipului valorii
    assert "estimate: piata." not in text             # nu mai afișează slug-ul brut


def test_raportul_declara_dreptul_si_sarcinile(tmp_path):
    # SEV 230 §40.1/§140: raportul declară dreptul evaluat + sarcinile CF (critic la garantare).
    ctx = _ctx()
    ctx.meta.sarcini = "ipotecă în favoarea Băncii X"
    out = tmp_path / "raport.docx"
    genereaza_raport(ctx, out)
    text = _all_text(out)
    assert "Dreptul evaluat" in text and "SEV 230" in text
    assert "ipotecă în favoarea Băncii X" in text


def test_sarcini_nedeclarate_avertizeaza(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)            # sarcini=None implicit
    text = _all_text(out)
    assert "Sarcini" in text and "de verificat în extrasul de carte funciară" in text


def test_raportul_are_cele_sapte_capitole(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    doc = Document(str(out))
    headings = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
    titlu = "\n".join(headings)
    for nr in ["1.", "2.", "3.", "4.", "5.", "6.", "7."]:
        assert nr in titlu


def test_adnotari_demo_doar_cand_sunt_cerute(tmp_path):
    fara = tmp_path / "fara.docx"
    genereaza_raport(_ctx(), fara, adnotari=False)
    assert "NOTA DEMO" not in _all_text(fara)
    assert "LEGENDA NOTELOR DEMO" not in _all_text(fara)

    cu = tmp_path / "cu.docx"
    genereaza_raport(_ctx(), cu, adnotari=True)
    text = _all_text(cu)
    assert "NOTA DEMO" in text
    assert "LEGENDA NOTELOR DEMO" in text
    assert "[CALCULAT]" in text and "[AI]" in text and "[EXEMPLU]" in text


def test_termeni_referinta_acopera_sev_101_si_esg(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    text = _all_text(out)
    assert "Sursa informatiilor" in text          # SEV 101 20.1 j
    assert "ESG" in text and "guvernanta" in text  # SEV 101/106 m (nou 2025)
    assert "Natura si amploarea activitatilor" in text  # 20.1 i
    assert "difuzarea sau publicarea" in text      # 20.1 o
    assert "Specialist" in text                    # 30.6 o


def test_raportul_conform_sev_2025_si_gev_520(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    text = _all_text(out)
    # editia 2025 citata
    assert "editia 2025" in text or "ediția 2025" in text
    # tip valoare actualizat (SEV 102, nu SEV 104)
    assert "SEV 102" in text
    assert "SEV 104" not in text
    # factorii obligatorii GEV 520 A5
    assert "GEV 520, A5" in text
    assert "tendintele pietei" in text
    assert "valorii viitoare a garantiei" in text
    # inregistrare BIG
    assert "Baza Imobiliara de Garantii (BIG)" in text


def test_raportul_arata_echivalent_lei(tmp_path):
    ctx = _ctx()
    ctx.meta.moneda = "EUR"
    ctx.meta.curs_valutar = Decimal("5")     # 280000 EUR -> 1.400.000 LEI
    out = tmp_path / "raport.docx"
    genereaza_raport(ctx, out)
    text = _all_text(out)
    assert "echivalent" in text
    assert "1.400.000 LEI" in text


def test_raportul_are_shell_gbf(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    text = _all_text(out)
    for sectiune in ["SCRISOARE DE TRANSMITERE", "DECLARATIE DE CONFORMITATE",
                     "TERMENI DE REFERINTA", "RISCUL ASOCIAT GARANTIEI (GEV 520)",
                     "ANEXE", "Intocmit,"]:
        assert sectiune in text


def _ctx_cu_teren() -> ReportContext:
    from evaluare.engine.land import evaluate_land
    from evaluare.engine.reconciliation import aloca_constructii
    from evaluare.models.comparable import Adjustment, LandComparable
    ctx = _ctx()
    comps = [
        LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("450"), localizare="Zona A",
                       adjustments=[Adjustment(element="A", tip="procentuala",
                                               valoare=Decimal("0.05"))]),
        LandComparable(pret_mp=Decimal("120"), suprafata=Decimal("500"),
                       adjustments=[Adjustment(element="A", tip="procentuala",
                                               valoare=Decimal("-0.30"))]),
    ]
    lr = evaluate_land(comps, ctx.land.suprafata)
    ctx.land_comparables = comps
    ctx.land_result = lr
    ctx.alocare_constructii = aloca_constructii(ctx.reconciled.valoare_finala, lr.valoare_teren)
    return ctx


_PNG_1x1 = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
            "AAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")


def test_raportul_embeddeaza_fotografiile(tmp_path):
    ctx = _ctx()
    ctx.photos = [_PNG_1x1, "data:image/png;base64,GUNOI_INVALID==", _PNG_1x1]
    out = tmp_path / "raport.docx"
    genereaza_raport(ctx, out)
    doc = Document(str(out))
    # cele doua imagini valide sunt inserate; cea invalida e sarita fara eroare
    assert len(doc.inline_shapes) == 2
    text = _all_text(out)
    assert "Planse fotografice" in text
    assert "[de atasat]" not in text.split("Anexa 2")[1].split("Anexa 3")[0]


def test_raportul_embeddeaza_documentele_anexa3(tmp_path):
    ctx = _ctx()
    ctx.documente = [_PNG_1x1]
    out = tmp_path / "raport.docx"
    genereaza_raport(ctx, out)
    doc = Document(str(out))
    assert len(doc.inline_shapes) >= 1
    text = _all_text(out)
    dupa_anexa3 = text.split("Anexa 3")[1]
    assert "[de atasat]" not in dupa_anexa3


def test_raportul_anexa_foto_placeholder_fara_poze(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)   # fara photos
    text = _all_text(out)
    dupa_anexa2 = text.split("Anexa 2")[1].split("Anexa 3")[0]
    assert "[de atasat]" in dupa_anexa2


def test_raportul_contine_grila_teren_si_alocare(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx_cu_teren(), out)
    text = _all_text(out)
    assert "Grila de comparatie pentru teren" in text
    assert "Pret/mp corectat" in text
    assert "ALOCAREA VALORII" in text
    assert "Valoarea constructiilor" in text
