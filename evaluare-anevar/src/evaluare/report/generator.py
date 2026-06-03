"""Generator de raport .docx in structura GBF / SEV (shell complet + 7 capitole).

Shell GBF: copertA, scrisoare de transmitere, declaratie de conformitate, termeni de
referintA, cele 7 capitole de analiza (raportare conform SEV 106), alocarea valorii, riscul GEV 520, anexe, semnatura.
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
from docx.shared import Inches, Pt, RGBColor

from evaluare.models.report_context import ReportContext

# Note de provenienta (mod demo/review): explica ce e calculat, extras, AI, exemplu sau placeholder.
ADNOTARI = {
    "legenda": ("LEGENDA NOTELOR DEMO (text colorat, NU apare in raportul real): "
                "[CALCULAT]=produs de motorul de calcul; [EXTRAS]=preluat automat din anunt; "
                "[INTRODUS]=completat de evaluator; [AI]=text generat de inteligenta artificiala; "
                "[SABLON]=text fix standard; [EXEMPLU]/[PLACEHOLDER]=valori demonstrative de inlocuit."),
    "coperta": ("[INTRODUS] Identificarea (client, cadastral, CF, evaluator) e introdusa de evaluator — "
                "aici valori generice/placeholder. [CALCULAT] VALOAREA estimata e calculata real de motor."),
    "scrisoare": "[SABLON+CALCULAT] Text-sablon fix, completat automat cu valoarea calculata. Functional.",
    "declaratie": "[SABLON] Declaratii standard ANEVAR — text fix. Functional.",
    "termeni": ("[INTRODUS] Compilati automat din campurile lucrarii (client, beneficiar, scop, moneda, "
                "curs, date). Functional."),
    "cap1": "[CALCULAT] Sinteza generata automat din rezultatele calculate. Functional.",
    "cap2": "[AI] Text narativ generat de inteligenta artificiala; de revizuit de evaluator.",
    "cap3": "[AI] Analiza de piata descriptiva (AI) — NU pe o baza de date de tranzactii reale.",
    "cap4": ("[EXTRAS/INTRODUS] Date fizice extrase din anunt / introduse de evaluator (reale). "
             "Nr. cadastral si CF aici sunt PLACEHOLDER."),
    "cap5": "[AI] Analiza celei mai bune utilizari generata de AI.",
    "cap6": ("[CALCULAT] Grilele (teren + casa) si costul CIN sunt calculate real de motor. "
             "[EXTRAS] Preturile/suprafetele comparabilelor sunt reale (din anunturi). "
             "[EXEMPLU] Ajustarile din grila sunt demonstrative — de stabilit de evaluator la inspectie."),
    "cap7": "[CALCULAT] Selectia metodei si valoarea finala sunt calculate. [AI] Textul explicativ.",
    "alocare": "[CALCULAT] Valoare constructii = valoare proprietate − valoare teren.",
    "gev520": "[AI] Text standard GEV 520 generat de AI; de adaptat la caz.",
    "anexe": ("[EXTRAS] Sursele comparabilelor sunt linkuri reale. [EXEMPLU] Fotografiile sunt "
              "exemplificative. [PLACEHOLDER] Documentele cadastrale — de atasat."),
    "semnatura": "[PLACEHOLDER] Caseta de semnatura — de completat de evaluator.",
}


def _nota(doc: DocxDocument, cheie: str, adnotari: bool) -> None:
    """Adauga o nota de provenienta (colorata, italic) sub un titlu — doar in modul demo."""
    if not adnotari:
        return
    text = ADNOTARI.get(cheie, "")
    if not text:
        return
    p = doc.add_paragraph()
    run = p.add_run("▮ NOTA DEMO — " + text)
    run.italic = True
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0xB0, 0x6A, 0x00)


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


def _b2(v) -> str:
    """Rotunjeste la 2 zecimale (preturi unitare, EUR/mp)."""
    try:
        return f"{Decimal(str(v)).quantize(Decimal('0.01'))}"
    except Exception:
        return str(v)


def _pct(v) -> str:
    """Fractie -> procent cu 2 zecimale (0.1727 -> '17.27%')."""
    try:
        return f"{(Decimal(str(v)) * 100).quantize(Decimal('0.01'))}%"
    except Exception:
        return str(v)


def _fara_tva(ctx: ReportContext) -> str:
    return "Valoarea nu contine TVA." if ctx.reconciled.valoare_fara_tva else ""


def _echiv_lei(ctx: ReportContext) -> str:
    """Echivalentul in LEI al valorii finale (daca moneda e EUR si exista curs BNR)."""
    curs = ctx.meta.curs_valutar
    if curs is None or (ctx.meta.moneda or "").upper() == "LEI":
        return ""
    lei = ctx.reconciled.valoare_finala * curs
    return f" (echivalent ~{_fmt(lei)} LEI la cursul BNR {curs})"


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
def _coperta(doc: DocxDocument, ctx: ReportContext, adnotari: bool = False) -> None:
    meta = ctx.meta
    doc.add_heading("RAPORT DE EVALUARE", level=0)
    _nota(doc, "legenda", adnotari)
    _nota(doc, "coperta", adnotari)
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
        f"VALOAREA ESTIMATA: {_fmt(ctx.reconciled.valoare_finala)} {meta.moneda}"
        f"{_echiv_lei(ctx)}. {_fara_tva(ctx)}"
    ).bold = True
    doc.add_page_break()


def _scrisoare_transmitere(doc: DocxDocument, ctx: ReportContext, adnotari: bool = False) -> None:
    meta = ctx.meta
    doc.add_heading("SCRISOARE DE TRANSMITERE", level=1)
    _nota(doc, "scrisoare", adnotari)
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
        "ANEVAR, editia 2025 (in vigoare de la 1 iulie 2025, aprobate prin HCN nr. 2/2025), "
        "si cu Ghidul GEV 520 — Evaluarea pentru garantarea imprumutului. Poate fi utilizat "
        "exclusiv in scopul mentionat, de catre utilizatorul desemnat."
    )
    doc.add_paragraph(
        f"Cu deosebita consideratie, {meta.evaluator_nume}, "
        f"membru ANEVAR, legitimatia {meta.evaluator_legitimatie}."
    )


def _declaratie_conformitate(doc: DocxDocument, ctx: ReportContext, adnotari: bool = False) -> None:
    doc.add_heading("DECLARATIE DE CONFORMITATE SI CERTIFICARE", level=1)
    _nota(doc, "declaratie", adnotari)
    afirmatii = [
        "Prezentul raport a fost elaborat in conformitate cu Standardele de evaluare a bunurilor "
        "ANEVAR (SEV), editia 2025, in vigoare de la 1 iulie 2025 (HCN nr. 2/2025), "
        "incluzand Ghidul GEV 520 — Evaluarea pentru garantarea imprumutului.",
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


def _termeni_referinta(doc: DocxDocument, ctx: ReportContext, adnotari: bool = False) -> None:
    meta = ctx.meta
    doc.add_heading("TERMENI DE REFERINTA AI EVALUARII", level=1)
    _nota(doc, "termeni", adnotari)
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
        "cu exceptia celor mentionate explicit in raport. Daca este ocupata de proprietar, se "
        "evalueaza in ipoteza transferului ca bun liber/disponibil (GEV 520, A8)."
    )
    # GEV 520 A3 (SEV 101): independenta / implicare materiala
    doc.add_paragraph(
        "Independenta: evaluatorul declara ca nu are nicio implicare materiala, prezenta sau "
        "anterioara, cu bunul evaluat, cu debitorul sau cu un debitor potential, care sa afecteze "
        "obiectivitatea (GEV 520, A3; SEV 101). Utilizatorul desemnat al raportului este creditorul "
        "nominalizat; orice alta utilizare necesita personalizare de catre evaluator."
    )
    # GEV 520 A4: ipoteze speciale (ex. vanzare fortata / perioada de marketing limitata)
    doc.add_paragraph(
        "Ipoteze speciale: daca se solicita o valoare in premisa unei vanzari fortate sau cu "
        "perioada de marketing limitata, aceasta se precizeaza distinct; valoarea pe ipoteza "
        "speciala este valabila numai la data evaluarii si poate sa nu fie realizabila la o data "
        "viitoare (GEV 520, A4-A5)."
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
        row[1].text = _b2(pret)
        row[2].text = _pct(bruta)
        row[3].text = "DA" if i == m.index_selectat else ""
    doc.add_paragraph(
        f"Valoarea prin comparatie de piata: {_fmt(m.valoare_piata)} {ctx.meta.moneda}."
    )
    doc.add_paragraph(
        "Sursele comparabilelor au caracter indicativ (oferte de pe portaluri publice); "
        "preturile si atributele au fost verificate si retinute de evaluator pe baza "
        "rationamentului profesional."
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
        row[1].text = _b2(pret)
        row[2].text = _pct(bruta)
        row[3].text = "DA" if i == lr.index_selectat else ""
    doc.add_paragraph(
        f"Valoarea terenului = {_b2(lr.pret_mp_ales)} EUR/mp x {ctx.land.suprafata} mp = "
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
        row[2].text = _b2(el.cantitate)
        row[3].text = _b2(el.cost_unitar)
        row[4].text = _fmt(el.cost_nou())
    if ctx.cost_result is not None:
        c = ctx.cost_result
        doc.add_paragraph(
            f"CIB = {_fmt(c.cib)}; Vcp = {_b2(c.vcp)} ani; depreciere fizica = "
            f"{_pct(c.depreciere_fizica)}; CIN = {_fmt(c.cin)}; "
            f"valoare prin cost (CIN + teren) = {_fmt(c.valoare_cost)} {ctx.meta.moneda}."
        )


# --------------------------------------------------------------------------- #
# Back matter (alocare, risc GEV 520, anexe, semnatura)
# --------------------------------------------------------------------------- #
def _adauga_alocare(doc: DocxDocument, ctx: ReportContext, adnotari: bool = False) -> None:
    if ctx.alocare_constructii is None:
        return
    doc.add_heading("ALOCAREA VALORII", level=1)
    _nota(doc, "alocare", adnotari)
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


def _adauga_risc_garantie(doc: DocxDocument, ctx: ReportContext, adnotari: bool = False) -> None:
    doc.add_heading("RISCUL ASOCIAT GARANTIEI (GEV 520)", level=1)
    _nota(doc, "gev520", adnotari)
    txt = _narativ(ctx, "Riscul asociat garantiei (GEV 520)")
    doc.add_paragraph(
        txt or
        "Evaluarea pentru garantarea imprumutului respecta cerintele Ghidului GEV 520. Au fost "
        "analizati factorii relevanti pentru estimarea de catre creditor a performantei garantiei "
        "pe perioada creditului, precum si gradul de adecvare al proprietatii ca garantie."
    )
    # GEV 520, Anexa A5: factorii obligatorii de comentat
    doc.add_paragraph("Factori relevanti pentru performanta garantiei (GEV 520, A5):")
    for f in (
        "activitatea curenta si tendintele pietei relevante;",
        "cererea anterioara, curenta si viitoare pentru tipul de bun si pentru localizare;",
        "cererea potentiala sau probabila pentru alte utilizari, la data evaluarii;",
        "impactul evenimentelor previzibile la data evaluarii asupra valorii viitoare a garantiei "
        "pe perioada creditului.",
    ):
        doc.add_paragraph(f, style="List Bullet")
    doc.add_paragraph(
        "Lichiditate si vandabilitate: se apreciaza lichiditatea pietei locale, gradul de adecvare "
        "al proprietatii ca garantie si perioada de comercializare estimata."
    )
    doc.add_paragraph(
        "Inregistrare BIG: raportul, avand utilizarea desemnata de garantare a imprumutului, se "
        "inregistreaza in Baza Imobiliara de Garantii (BIG), conform reglementarilor ANEVAR."
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


def _adauga_anexe(doc: DocxDocument, ctx: ReportContext, adnotari: bool = False) -> None:
    doc.add_heading("ANEXE", level=1)
    _nota(doc, "anexe", adnotari)
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

    doc.add_paragraph("Anexa 3 — Documente cadastrale, extras CF si acte juridice:")
    doc_inserate = 0
    for data_url in ctx.documente:
        stream = _decode_foto(data_url)
        if stream is None:
            continue
        try:
            doc.add_picture(stream, width=Inches(5.5))
            doc_inserate += 1
        except Exception:
            continue
    if doc_inserate == 0:
        doc.add_paragraph("[de atasat].")


def _adauga_semnatura(doc: DocxDocument, ctx: ReportContext, adnotari: bool = False) -> None:
    meta = ctx.meta
    _nota(doc, "semnatura", adnotari)
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
def genereaza_raport(
    ctx: ReportContext, output_path: Path | str, adnotari: bool = False
) -> Path:
    """Construieste si salveaza raportul .docx. Returneaza calea fisierului.

    Cu `adnotari=True`, insereaza note de provenienta (mod demo/review) sub fiecare sectiune:
    ce e calculat real, extras automat, generat de AI, exemplu sau placeholder.
    """
    doc = Document()
    meta = ctx.meta

    # --- Shell GBF (front matter) ---
    _coperta(doc, ctx, adnotari)
    _scrisoare_transmitere(doc, ctx, adnotari)
    _declaratie_conformitate(doc, ctx, adnotari)
    _termeni_referinta(doc, ctx, adnotari)

    # --- Cele 7 capitole de analiza (raportare conform SEV 106 Documentare si raportare) ---
    doc.add_heading("1. SINTEZA EVALUARII SI CERTIFICARE", level=1)
    _nota(doc, "cap1", adnotari)
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
    _nota(doc, "cap2", adnotari)
    doc.add_paragraph(
        _narativ(ctx, "Ipoteze generale si speciale")
        or "Ipoteze limitative standard privind structura de rezistenta si solul."
    )

    doc.add_heading("3. PREZENTAREA DATELOR DE PIATA", level=1)
    _nota(doc, "cap3", adnotari)
    doc.add_paragraph(
        _narativ(ctx, "Prezentarea datelor de piata")
        or "Analiza pietei locale [de completat]."
    )

    doc.add_heading("4. DESCRIEREA JURIDICA SI FIZICA A PROPRIETATII", level=1)
    _nota(doc, "cap4", adnotari)
    doc.add_paragraph(f"Teren: {ctx.land.suprafata} mp, categorie {ctx.land.categorie}.")
    doc.add_paragraph(
        f"Constructie: Au {ctx.building.au} mp, Acd {ctx.building.acd} mp, "
        f"an referinta {ctx.building.an_referinta}."
    )
    descriere = _narativ(ctx, "Descrierea juridica si fizica a proprietatii")
    if descriere:
        doc.add_paragraph(descriere)

    doc.add_heading("5. ANALIZA CELEI MAI BUNE UTILIZARI (CMBU)", level=1)
    _nota(doc, "cap5", adnotari)
    doc.add_paragraph(
        _narativ(ctx, "Analiza celei mai bune utilizari (CMBU)")
        or "Analiza CMBU [de completat]."
    )

    doc.add_heading("6. APLICAREA METODELOR DE CALCUL", level=1)
    _nota(doc, "cap6", adnotari)
    _adauga_grila_comparatie(doc, ctx)
    _adauga_grila_teren(doc, ctx)
    _adauga_tabel_cost(doc, ctx)
    justificare = _narativ(ctx, "Justificarea ajustarilor aplicate")
    if justificare:
        doc.add_paragraph(justificare)

    doc.add_heading("7. RECONCILIEREA REZULTATELOR SI CONCLUZIA VALORII", level=1)
    _nota(doc, "cap7", adnotari)
    doc.add_paragraph(
        _narativ(ctx, "Reconcilierea rezultatelor si concluzia valorii")
        or "Reconcilierea metodelor [de completat]."
    )
    doc.add_paragraph(
        f"Valoarea finala: {_fmt(ctx.reconciled.valoare_finala)} {meta.moneda}"
        f"{_echiv_lei(ctx)}. {_fara_tva(ctx)}"
    )

    # --- Shell GBF (back matter) ---
    _adauga_alocare(doc, ctx, adnotari)
    _adauga_risc_garantie(doc, ctx, adnotari)
    _adauga_anexe(doc, ctx, adnotari)
    _adauga_semnatura(doc, ctx, adnotari)

    output_path = Path(output_path)
    doc.save(str(output_path))
    return output_path
