"""Generator de raport .docx conform structurii SEV 103 (7 capitole)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from docx import Document
from docx.document import Document as DocxDocument

from evaluare.models.report_context import ReportContext


def _narativ(ctx: ReportContext, capitol: str) -> Optional[str]:
    """Returneaza textul narativ pentru un capitol, daca exista."""
    for sectiune in ctx.narrative:
        if sectiune.capitol == capitol:
            return sectiune.text
    return None


def _adauga_grila_comparatie(doc: DocxDocument, ctx: ReportContext) -> None:
    if ctx.market_result is None or not ctx.comparables:
        doc.add_paragraph("Abordarea prin piata nu a fost aplicata (a se vedea reconcilierea).")
        return
    doc.add_paragraph("Grila de comparatie directa:")
    m = ctx.market_result
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Comparabil"
    hdr[1].text = "Pret unitar corectat"
    hdr[2].text = "Ajustare bruta"
    hdr[3].text = "Selectat"
    for i, comp in enumerate(ctx.comparables):
        pret = m.preturi_unitare_corectate[i] if i < len(m.preturi_unitare_corectate) else ""
        bruta = m.ajustari_brute[i] if i < len(m.ajustari_brute) else ""
        row = table.add_row().cells
        row[0].text = f"{i}"
        row[1].text = str(pret)
        row[2].text = str(bruta)
        row[3].text = "DA" if i == m.index_selectat else ""


def _adauga_tabel_cost(doc: DocxDocument, ctx: ReportContext) -> None:
    if not ctx.building.elements:
        return
    doc.add_paragraph("Tabelul costurilor segregate:")
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
            f"CIB = {c.cib}; Vcp = {c.vcp} ani; depreciere fizica = {c.depreciere_fizica}; "
            f"CIN = {c.cin}."
        )


def genereaza_raport(ctx: ReportContext, output_path: Path | str) -> Path:
    """Construieste si salveaza raportul .docx. Returneaza calea fisierului."""
    doc = Document()
    meta = ctx.meta

    doc.add_heading("RAPORT DE EVALUARE", level=0)

    # 1. Sinteza evaluarii si certificare
    doc.add_heading("1. SINTEZA EVALUARII SI CERTIFICARE", level=1)
    doc.add_paragraph(f"Client: {meta.client_nume} ({meta.client_tip}).")
    doc.add_paragraph(f"Proprietatea: {meta.adresa}; nr. cadastral {meta.numar_cadastral}; "
                      f"{meta.carte_funciara}.")
    doc.add_paragraph(f"Scopul evaluarii: {meta.scop}.")
    doc.add_paragraph(f"Tipul valorii: {meta.tip_valoare}.")
    doc.add_paragraph(f"Data evaluarii: {meta.data_evaluarii}; data raportului: "
                      f"{meta.data_raportului}.")
    doc.add_paragraph(
        f"VALOAREA ESTIMATA: {ctx.reconciled.valoare_finala} {meta.moneda} "
        f"(metoda selectata: {ctx.reconciled.metoda_selectata}). "
        f"{'Valoarea nu contine TVA.' if ctx.reconciled.valoare_fara_tva else ''}"
    )
    doc.add_paragraph(
        f"Declar pe proprie raspundere independenta evaluatorului si absenta conflictelor "
        f"de interese. Evaluator: {meta.evaluator_nume}, legitimatia "
        f"{meta.evaluator_legitimatie}."
    )

    # 2. Ipoteze generale si speciale
    doc.add_heading("2. IPOTEZE GENERALE SI SPECIALE", level=1)
    doc.add_paragraph(_narativ(ctx, "Ipoteze generale si speciale")
                      or "Ipoteze limitative standard privind structura de rezistenta si solul.")

    # 3. Prezentarea datelor de piata
    doc.add_heading("3. PREZENTAREA DATELOR DE PIATA", level=1)
    doc.add_paragraph(_narativ(ctx, "Prezentarea datelor de piata")
                      or "Analiza pietei locale [de completat].")

    # 4. Descrierea juridica si fizica
    doc.add_heading("4. DESCRIEREA JURIDICA SI FIZICA A PROPRIETATII", level=1)
    doc.add_paragraph(f"Teren: {ctx.land.suprafata} mp, categorie {ctx.land.categorie}.")
    doc.add_paragraph(f"Constructie: Au {ctx.building.au} mp, Acd {ctx.building.acd} mp, "
                      f"an referinta {ctx.building.an_referinta}.")
    descriere = _narativ(ctx, "Descrierea juridica si fizica a proprietatii")
    if descriere:
        doc.add_paragraph(descriere)

    # 5. Analiza CMBU
    doc.add_heading("5. ANALIZA CELEI MAI BUNE UTILIZARI (CMBU)", level=1)
    doc.add_paragraph(_narativ(ctx, "Analiza celei mai bune utilizari (CMBU)")
                      or "Analiza CMBU [de completat].")

    # 6. Aplicarea metodelor de calcul
    doc.add_heading("6. APLICAREA METODELOR DE CALCUL", level=1)
    _adauga_grila_comparatie(doc, ctx)
    _adauga_tabel_cost(doc, ctx)
    justificare = _narativ(ctx, "Justificarea ajustarilor aplicate")
    if justificare:
        doc.add_paragraph(justificare)

    # 7. Reconcilierea si concluzia valorii
    doc.add_heading("7. RECONCILIEREA REZULTATELOR SI CONCLUZIA VALORII", level=1)
    doc.add_paragraph(_narativ(ctx, "Reconcilierea rezultatelor si concluzia valorii")
                      or "Reconcilierea metodelor [de completat].")
    doc.add_paragraph(
        f"Valoarea finala: {ctx.reconciled.valoare_finala} {meta.moneda}. "
        f"{'Valoarea exprimata nu contine TVA.' if ctx.reconciled.valoare_fara_tva else ''}"
    )

    output_path = Path(output_path)
    doc.save(str(output_path))
    return output_path
