"""Generator de raport .docx in structura GBF / SEV (shell complet + 7 capitole).

Shell GBF: copertA, scrisoare de transmitere, declaratie de conformitate, termeni de
referintA, cele 7 capitole SEV 103, alocarea valorii, riscul GEV 520, anexe, semnatura.
"""
from __future__ import annotations

import base64
import binascii
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Optional

from docx import Document
from docx.document import Document as DocxDocument
from docx.shared import Inches

from evaluare.models.report_context import ReportContext


def _narativ(ctx: ReportContext, capitol: str) -> Optional[str]:
    """Returneaza textul narativ pentru un capitol, daca exista."""
    for sectiune in ctx.narrative:
        if sectiune.capitol == capitol:
            return sectiune.text
    return None


def _fmt(v) -> str:
    """Formateaza un numar cu separator de mii (stil RO) fara zecimale inutile."""
    try:
        d = Decimal(str(v)).quantize(Decimal("1"))
        return f"{int(d):,}".replace(",", ".")
    except Exception:
        return str(v)


def _fara_tva(ctx: ReportContext) -> str:
    return "Valoarea nu contine TVA." if ctx.reconciled.valoare_fara_tva else ""


def _valoare_teren(ctx: ReportContext):
    """Valoarea terenului folosita in raport (din grila daca exista, altfel din alocare)."""
    if ctx.land_result is not None:
        return ctx.land_result.valoare_teren
    if ctx.alocare_constructii is not None:
        return ctx.reconciled.valoare_finala - ctx.alocare_constructii
    return None


# --------------------------------------------------------------------------- #
# Front matter (shell GBF)
# --------------------------------------------------------------------------- #
def _coperta(doc: DocxDocument, ctx: ReportContext) -> None:
    meta = ctx.meta
    doc.add_heading("RAPORT DE EVALUARE", level=0)
    p = doc.add_paragraph()
    p.add_run("Proprietate imobiliara: casa de locuit si teren aferent").bold = True
    doc.add_paragraph(f"Adresa: {meta.adresa}")
    doc.add_paragraph(f"Numar cadastral: {meta.numar_cadastral}; {meta.carte_funciara}")
    doc.add_paragraph(f"Client: {meta.client_nume} ({meta.client_tip})")
    if meta.proprietar:
        doc.add_paragraph(f"Proprietar: {meta.proprietar}")
    if meta.beneficiar:
        doc.add_paragraph(f"Beneficiar / Finantator: {meta.beneficiar}")
    doc.add_paragraph(f"Scopul evaluarii: {meta.scop}")
    doc.add_paragraph(
        f"Evaluator: {meta.evaluator_nume}, membru ANEVAR, "
        f"legitimatia {meta.evaluator_legitimatie}"
    )
    doc.add_paragraph(
        f"Data evaluarii: {meta.data_evaluarii}; Data raportului: {meta.data_raportului}"
    )
    vp = doc.add_paragraph()
    vp.add_run(
        f"VALOAREA ESTIMATA: {_fmt(ctx.reconciled.valoare_finala)} {meta.moneda}. "
        f"{_fara_tva(ctx)}"
    ).bold = True
    doc.add_page_break()


def _scrisoare_transmitere(doc: DocxDocument, ctx: ReportContext) -> None:
    meta = ctx.meta
    doc.add_heading("SCRISOARE DE TRANSMITERE", level=1)
    catre = meta.client_nume + (f" / {meta.beneficiar}" if meta.beneficiar else "")
    doc.add_paragraph(f"Catre: {catre}")
    doc.add_paragraph(
        f"Va transmitem raportul de evaluare a proprietatii imobiliare situate in "
        f"{meta.adresa}, intocmit in scopul: {meta.scop}. In urma analizelor efectuate, "
        f"valoarea de piata estimata a proprietatii este de {_fmt(ctx.reconciled.valoare_finala)} "
        f"{meta.moneda}, la data evaluarii ({meta.data_evaluarii}). {_fara_tva(ctx)}"
    )
    doc.add_paragraph(
        "Raportul a fost elaborat in conformitate cu Standardele de evaluare a bunurilor "
        "ANEVAR in vigoare si poate fi utilizat exclusiv in scopul mentionat."
    )
    doc.add_paragraph(
        f"Cu deosebita consideratie, {meta.evaluator_nume}, "
        f"membru ANEVAR, legitimatia {meta.evaluator_legitimatie}."
    )


def _declaratie_conformitate(doc: DocxDocument, ctx: ReportContext) -> None:
    doc.add_heading("DECLARATIE DE CONFORMITATE SI CERTIFICARE", level=1)
    afirmatii = [
        "Prezentul raport a fost elaborat in conformitate cu Standardele de evaluare ANEVAR "
        "(SEV) in vigoare la data raportului.",
        "Faptele prezentate in raport sunt reale si corecte, dupa cunostinta evaluatorului.",
        "Analizele, opiniile si concluziile sunt limitate numai de ipotezele si conditiile "
        "limitative prezentate.",
        "Evaluatorul nu are niciun interes prezent sau de perspectiva in proprietatea evaluata "
        "si niciun interes personal cu privire la partile implicate.",
        "Onorariul evaluatorului nu este conditionat de exprimarea unei valori predeterminate "
        "sau de marimea valorii estimate.",
        "Evaluatorul este membru ANEVAR, detine competenta necesara si asigurarea de raspundere "
        "civila profesionala in vigoare.",
    ]
    for a in afirmatii:
        doc.add_paragraph(a, style="List Bullet")


def _termeni_referinta(doc: DocxDocument, ctx: ReportContext) -> None:
    meta = ctx.meta
    doc.add_heading("TERMENI DE REFERINTA AI EVALUARII", level=1)
    doc.add_paragraph(f"Clientul evaluarii: {meta.client_nume} ({meta.client_tip}).")
    if meta.beneficiar:
        doc.add_paragraph(f"Beneficiarul / utilizatorul desemnat: {meta.beneficiar}.")
    doc.add_paragraph(f"Scopul evaluarii: {meta.scop}.")
    doc.add_paragraph(f"Tipul valorii estimate: {meta.tip_valoare}.")
    moneda_txt = f"Moneda raportarii: {meta.moneda}."
    if meta.curs_valutar is not None:
        moneda_txt += f" Curs de schimb EUR/LEI: {meta.curs_valutar}."
    doc.add_paragraph(moneda_txt)
    date_txt = f"Data evaluarii: {meta.data_evaluarii}. Data raportului: {meta.data_raportului}."
    if meta.data_inspectiei:
        date_txt += f" Data inspectiei: {meta.data_inspectiei}."
    if meta.valabilitate:
        date_txt += f" Valabilitate: {meta.valabilitate}."
    doc.add_paragraph(date_txt)
    doc.add_paragraph(
        f"Identificarea proprietatii: {meta.adresa}, nr. cadastral {meta.numar_cadastral}, "
        f"{meta.carte_funciara}."
    )
    doc.add_paragraph(
        "Premise: proprietatea este evaluata in ipoteza utilizarii continue, libera de sarcini, "
        "cu exceptia celor mentionate explicit in raport."
    )


# --------------------------------------------------------------------------- #
# Tabele de calcul
# --------------------------------------------------------------------------- #
def _adauga_grila_comparatie(doc: DocxDocument, ctx: ReportContext) -> None:
    if ctx.market_result is None or not ctx.comparables:
        doc.add_paragraph("Abordarea prin piata nu a fost aplicata (a se vedea reconcilierea).")
        return
    doc.add_paragraph("Grila de comparatie directa pe pret total (proprietate intreaga):")
    m = ctx.market_result
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Comparabil"
    hdr[1].text = "Pret total corectat"
    hdr[2].text = "Ajustare bruta"
    hdr[3].text = "Selectat"
    for i, comp in enumerate(ctx.comparables):
        pret = m.preturi_unitare_corectate[i] if i < len(m.preturi_unitare_corectate) else ""
        bruta = m.ajustari_brute[i] if i < len(m.ajustari_brute) else ""
        row = table.add_row().cells
        row[0].text = f"{i + 1}"
        row[1].text = str(pret)
        row[2].text = str(bruta)
        row[3].text = "DA" if i == m.index_selectat else ""
    doc.add_paragraph(
        f"Valoarea prin comparatie de piata: {_fmt(m.valoare_piata)} {ctx.meta.moneda}."
    )


def _adauga_grila_teren(doc: DocxDocument, ctx: ReportContext) -> None:
    if ctx.land_result is None or not ctx.land_comparables:
        return
    doc.add_paragraph("Grila de comparatie pentru teren (EUR/mp):")
    lr = ctx.land_result
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Comparabil teren"
    hdr[1].text = "Pret/mp corectat"
    hdr[2].text = "Ajustare bruta"
    hdr[3].text = "Selectat"
    for i, c in enumerate(ctx.land_comparables):
        pret = lr.preturi_mp_corectate[i] if i < len(lr.preturi_mp_corectate) else ""
        bruta = lr.ajustari_brute[i] if i < len(lr.ajustari_brute) else ""
        row = table.add_row().cells
        eticheta = f"{i + 1}" + (f" — {c.localizare}" if c.localizare else "")
        row[0].text = eticheta
        row[1].text = str(pret)
        row[2].text = str(bruta)
        row[3].text = "DA" if i == lr.index_selectat else ""
    doc.add_paragraph(
        f"Valoarea terenului = {lr.pret_mp_ales} EUR/mp x {ctx.land.suprafata} mp = "
        f"{_fmt(lr.valoare_teren)} EUR."
    )


def _adauga_tabel_cost(doc: DocxDocument, ctx: ReportContext) -> None:
    if not ctx.building.elements:
        return
    doc.add_paragraph("Tabelul costurilor segregate (abordarea prin cost):")
    table = doc.add_table(rows=1, cols=5)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Element"
    hdr[1].text = "Cod"
    hdr[2].text = "Cantitate"
    hdr[3].text = "Cost unitar"
    hdr[4].text = "Cost de nou"
    for el in ctx.building.elements:
        row = table.add_row().cells
        row[0].text = el.element
        row[1].text = el.cod
        row[2].text = str(el.cantitate)
        row[3].text = str(el.cost_unitar)
        row[4].text = str(el.cost_nou())
    if ctx.cost_result is not None:
        c = ctx.cost_result
        doc.add_paragraph(
            f"CIB = {_fmt(c.cib)}; Vcp = {c.vcp} ani; depreciere fizica = "
            f"{c.depreciere_fizica}; CIN = {_fmt(c.cin)}; "
            f"valoare prin cost (CIN + teren) = {_fmt(c.valoare_cost)} {ctx.meta.moneda}."
        )


# --------------------------------------------------------------------------- #
# Back matter (alocare, risc GEV 520, anexe, semnatura)
# --------------------------------------------------------------------------- #
def _adauga_alocare(doc: DocxDocument, ctx: ReportContext) -> None:
    if ctx.alocare_constructii is None:
        return
    doc.add_heading("ALOCAREA VALORII", level=1)
    vt = _valoare_teren(ctx)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Componenta"
    table.rows[0].cells[1].text = f"Valoare ({ctx.meta.moneda})"
    randuri = [
        ("Valoarea proprietatii (estimata)", ctx.reconciled.valoare_finala),
        ("din care: Valoarea terenului", vt),
        ("din care: Valoarea constructiilor (alocata)", ctx.alocare_constructii),
    ]
    for nume, val in randuri:
        r = table.add_row().cells
        r[0].text = nume
        r[1].text = _fmt(val) if val is not None else "-"
    doc.add_paragraph(
        "Valoarea constructiilor a fost obtinuta prin alocare: valoarea proprietatii minus "
        "valoarea terenului estimata prin comparatie directa."
    )


def _adauga_risc_garantie(doc: DocxDocument, ctx: ReportContext) -> None:
    doc.add_heading("RISCUL ASOCIAT GARANTIEI (GEV 520)", level=1)
    txt = _narativ(ctx, "Riscul asociat garantiei (GEV 520)")
    if txt:
        doc.add_paragraph(txt)
    else:
        doc.add_paragraph(
            "Evaluarea pentru garantarea imprumutului respecta cerintele GEV 520. Au fost "
            "analizate: lichiditatea si activitatea pietei locale, gradul de adecvare al "
            "proprietatii ca garantie, vandabilitatea si expunerea estimata pe piata, precum si "
            "sensibilitatea valorii la variatiile conditiilor de piata. In opinia evaluatorului, "
            "proprietatea este adecvata ca garantie pentru scopul declarat."
        )


def _decode_foto(data_url: str) -> Optional[BytesIO]:
    """Extrage bytes dintr-un data-URL base64 (sau base64 simplu). None daca e invalid."""
    if not data_url:
        return None
    payload = data_url.split(",", 1)[1] if data_url.startswith("data:") else data_url
    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError):
        return None
    if not raw:
        return None
    return BytesIO(raw)


def _adauga_anexe(doc: DocxDocument, ctx: ReportContext) -> None:
    doc.add_heading("ANEXE", level=1)
    doc.add_paragraph("Anexa 1 — Comparabile utilizate (surse):")
    surse = [c.sursa for c in ctx.comparables if c.sursa and c.sursa != "manual"]
    if surse:
        for u in surse:
            doc.add_paragraph(u, style="List Bullet")
    else:
        doc.add_paragraph("Comparabile introduse manual.", style="List Bullet")

    doc.add_paragraph("Anexa 2 — Planse fotografice ale proprietatii:")
    inserate = 0
    for data_url in ctx.photos:
        stream = _decode_foto(data_url)
        if stream is None:
            continue
        try:
            doc.add_picture(stream, width=Inches(5.5))
            inserate += 1
        except Exception:
            continue  # fisier imagine corupt / format neacceptat -> sarim
    if inserate == 0:
        doc.add_paragraph("[de atasat].")

    doc.add_paragraph("Anexa 3 — Documente cadastrale, extras CF si acte juridice [de atasat].")


def _adauga_semnatura(doc: DocxDocument, ctx: ReportContext) -> None:
    meta = ctx.meta
    doc.add_paragraph("")
    doc.add_paragraph("Intocmit,")
    p = doc.add_paragraph()
    p.add_run(meta.evaluator_nume).bold = True
    doc.add_paragraph(f"Evaluator autorizat ANEVAR, legitimatia {meta.evaluator_legitimatie}")
    doc.add_paragraph(f"Data: {meta.data_raportului}")
    doc.add_paragraph("Semnatura / stampila: ______________________")


# --------------------------------------------------------------------------- #
# Asamblare
# --------------------------------------------------------------------------- #
def genereaza_raport(ctx: ReportContext, output_path: Path | str) -> Path:
    """Construieste si salveaza raportul .docx. Returneaza calea fisierului."""
    doc = Document()
    meta = ctx.meta

    # --- Shell GBF (front matter) ---
    _coperta(doc, ctx)
    _scrisoare_transmitere(doc, ctx)
    _declaratie_conformitate(doc, ctx)
    _termeni_referinta(doc, ctx)

    # --- Cele 7 capitole SEV 103 ---
    doc.add_heading("1. SINTEZA EVALUARII SI CERTIFICARE", level=1)
    doc.add_paragraph(f"Client: {meta.client_nume} ({meta.client_tip}).")
    doc.add_paragraph(
        f"Proprietatea: {meta.adresa}; nr. cadastral {meta.numar_cadastral}; "
        f"{meta.carte_funciara}."
    )
    doc.add_paragraph(f"Scopul evaluarii: {meta.scop}.")
    doc.add_paragraph(f"Tipul valorii: {meta.tip_valoare}.")
    doc.add_paragraph(
        f"Data evaluarii: {meta.data_evaluarii}; data raportului: {meta.data_raportului}."
    )
    doc.add_paragraph(
        f"VALOAREA ESTIMATA: {_fmt(ctx.reconciled.valoare_finala)} {meta.moneda} "
        f"(metoda selectata: {ctx.reconciled.metoda_selectata}). {_fara_tva(ctx)}"
    )

    doc.add_heading("2. IPOTEZE GENERALE SI SPECIALE", level=1)
    doc.add_paragraph(
        _narativ(ctx, "Ipoteze generale si speciale")
        or "Ipoteze limitative standard privind structura de rezistenta si solul."
    )

    doc.add_heading("3. PREZENTAREA DATELOR DE PIATA", level=1)
    doc.add_paragraph(
        _narativ(ctx, "Prezentarea datelor de piata")
        or "Analiza pietei locale [de completat]."
    )

    doc.add_heading("4. DESCRIEREA JURIDICA SI FIZICA A PROPRIETATII", level=1)
    doc.add_paragraph(f"Teren: {ctx.land.suprafata} mp, categorie {ctx.land.categorie}.")
    doc.add_paragraph(
        f"Constructie: Au {ctx.building.au} mp, Acd {ctx.building.acd} mp, "
        f"an referinta {ctx.building.an_referinta}."
    )
    descriere = _narativ(ctx, "Descrierea juridica si fizica a proprietatii")
    if descriere:
        doc.add_paragraph(descriere)

    doc.add_heading("5. ANALIZA CELEI MAI BUNE UTILIZARI (CMBU)", level=1)
    doc.add_paragraph(
        _narativ(ctx, "Analiza celei mai bune utilizari (CMBU)")
        or "Analiza CMBU [de completat]."
    )

    doc.add_heading("6. APLICAREA METODELOR DE CALCUL", level=1)
    _adauga_grila_comparatie(doc, ctx)
    _adauga_grila_teren(doc, ctx)
    _adauga_tabel_cost(doc, ctx)
    justificare = _narativ(ctx, "Justificarea ajustarilor aplicate")
    if justificare:
        doc.add_paragraph(justificare)

    doc.add_heading("7. RECONCILIEREA REZULTATELOR SI CONCLUZIA VALORII", level=1)
    doc.add_paragraph(
        _narativ(ctx, "Reconcilierea rezultatelor si concluzia valorii")
        or "Reconcilierea metodelor [de completat]."
    )
    doc.add_paragraph(
        f"Valoarea finala: {_fmt(ctx.reconciled.valoare_finala)} {meta.moneda}. "
        f"{_fara_tva(ctx)}"
    )

    # --- Shell GBF (back matter) ---
    _adauga_alocare(doc, ctx)
    _adauga_risc_garantie(doc, ctx)
    _adauga_anexe(doc, ctx)
    _adauga_semnatura(doc, ctx)

    output_path = Path(output_path)
    doc.save(str(output_path))
    return output_path
