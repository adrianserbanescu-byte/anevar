const pptxgen = require("pptxgenjs");
const path = require("path");
const os = require("os");

const P = {
  navy: "152A4E", navy2: "1E3A66", ice: "CFE0F5", bg: "F5F7FB",
  card: "FFFFFF", gold: "D9A227", teal: "2A9D8F", text: "1A2233",
  muted: "5C6679", white: "FFFFFF", line: "DDE3EE", green: "2E7D5B", red: "B23A48",
};
const HF = "Georgia", BF = "Calibri";
const DEMO = path.join(os.tmpdir(), "demo");

const pres = new pptxgen();
pres.defineLayout({ name: "W", width: 13.333, height: 7.5 });
pres.layout = "W";
pres.author = "Aplicatie evaluare ANEVAR";
pres.title = "Prezentare pentru evaluator";
const W = 13.333, H = 7.5;

const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.13 });

function header(slide, kicker, title) {
  slide.background = { color: P.bg };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.55, w: 0.16, h: 0.5, fill: { color: P.gold } });
  slide.addText(kicker.toUpperCase(), { x: 0.85, y: 0.5, w: 11.5, h: 0.3, fontFace: BF, fontSize: 12, color: P.gold, bold: true, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.83, y: 0.78, w: 11.8, h: 0.7, fontFace: HF, fontSize: 30, color: P.navy, bold: true, margin: 0 });
}
function footer(slide, n, dark) {
  const col = dark ? P.ice : P.muted;
  slide.addText("Aplicatie de asistenta la evaluare  ·  casa + teren  ·  document pentru review",
    { x: 0.6, y: 7.05, w: 10.5, h: 0.3, fontFace: BF, fontSize: 9, color: col, margin: 0 });
  slide.addText(String(n), { x: 12.4, y: 7.05, w: 0.4, h: 0.3, fontFace: BF, fontSize: 9, color: col, align: "right", margin: 0 });
}
function card(slide, x, y, w, h, fill) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill || P.card }, line: { color: P.line, width: 1 }, shadow: shadow() });
}
function dot(slide, x, y, color, label) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: 0.34, h: 0.34, fill: { color } });
  slide.addText(label, { x: x + 0.04, y: y + 0.02, w: 0.26, h: 0.3, align: "center", valign: "middle", fontFace: HF, fontSize: 14, bold: true, color: P.white, margin: 0 });
}

/* ---------- S1 TITLE ---------- */
let s = pres.addSlide();
s.background = { color: P.navy };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.22, fill: { color: P.gold } });
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 6.5, w: W, h: 1.0, fill: { color: P.navy2 } });
s.addText("ASISTENT DE EVALUARE IMOBILIARA", { x: 0.9, y: 2.05, w: 11.5, h: 0.5, fontFace: BF, fontSize: 16, color: P.gold, bold: true, charSpacing: 4, margin: 0 });
s.addText("Casa individuala + teren, pentru garantarea creditului", { x: 0.9, y: 2.6, w: 11.5, h: 1.2, fontFace: HF, fontSize: 40, color: P.white, bold: true, margin: 0 });
s.addText("Document de prezentare pentru review — destinat unui evaluator autorizat ANEVAR",
  { x: 0.9, y: 4.15, w: 11.0, h: 0.6, fontFace: BF, fontSize: 17, color: P.ice, margin: 0 });
s.addText("Ce face aplicatia · cum e gandita · ce metodologie aplica · ce e validat · ce urmeaza",
  { x: 0.9, y: 6.72, w: 11.5, h: 0.5, fontFace: BF, fontSize: 13, color: P.ice, valign: "middle", margin: 0 });

/* ---------- S2 CE ESTE ---------- */
s = pres.addSlide(); header(s, "Pe scurt", "Ce este aplicatia");
const puncte = [
  ["Asista evaluatorul, nu il inlocuieste", "Automatizeaza partea repetitiva — calcule, cautare de comparabile, redactarea raportului. Evaluatorul decide si verifica."],
  ["Ruleaza local, ca un singur fisier .exe", "Se deschide o pagina in browser, pe calculatorul propriu. Fara instalari complicate, fara server extern."],
  ["Datele raman pe calculator", "Singurul moment cand ceva pleaca in exterior e redactarea textului cu AI — si acolo datele personale sunt anonimizate inainte."],
];
puncte.forEach((p, i) => {
  const y = 1.7 + i * 1.6;
  card(s, 0.85, y, 11.6, 1.4);
  dot(s, 1.15, y + 0.5, P.navy, String(i + 1));
  s.addText(p[0], { x: 1.75, y: y + 0.22, w: 10.4, h: 0.4, fontFace: HF, fontSize: 18, bold: true, color: P.navy, margin: 0 });
  s.addText(p[1], { x: 1.75, y: y + 0.66, w: 10.4, h: 0.6, fontFace: BF, fontSize: 14, color: P.text, margin: 0 });
});
footer(s, 2);

/* ---------- S3 ARHITECTURA ---------- */
s = pres.addSlide(); header(s, "Cum e gandita", "Patru parti care lucreaza impreuna");
const comp = [
  ["Motor de calcul", "Cost (CIN), grila de teren, grila de casa, reconciliere si alocarea valorii — dupa metodologia ANEVAR.", P.navy],
  ["Descoperire comparabile", "Cauta anunturi in zona, le citeste, le puncteaza dupa similaritate si propune cele mai potrivite.", P.teal],
  ["Generator de raport", "Construieste documentul Word: coperta, declaratii, capitole de analiza, anexe — cu text si fotografii.", P.gold],
  ["Wizard in 5 pasi", "Ghideaza evaluatorul de la identificarea proprietatii pana la descarcarea raportului.", P.green],
];
comp.forEach((c, i) => {
  const x = 0.85 + (i % 2) * 6.0, y = 1.75 + Math.floor(i / 2) * 2.45;
  card(s, x, y, 5.6, 2.2);
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.14, h: 2.2, fill: { color: c[2] } });
  s.addText(c[0], { x: x + 0.4, y: y + 0.28, w: 5.0, h: 0.5, fontFace: HF, fontSize: 20, bold: true, color: P.navy, margin: 0 });
  s.addText(c[1], { x: x + 0.4, y: y + 0.9, w: 5.0, h: 1.1, fontFace: BF, fontSize: 14, color: P.text, margin: 0 });
});
s.addText("Filosofia: fiecare cifra poate fi verificata — aplicatia arata cum a ajuns la fiecare rezultat, nu doar valoarea finala.",
  { x: 0.85, y: 6.5, w: 11.6, h: 0.35, fontFace: BF, fontSize: 13, italic: true, color: P.muted, margin: 0 });
footer(s, 3);

/* ---------- S4 METODOLOGIE TEREN ---------- */
s = pres.addSlide(); header(s, "Metodologia · teren", "Grila de comparatie in doua etape");
function etapaBox(x, titlu, sub, items, col) {
  card(s, x, 1.85, 5.4, 3.1);
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.85, w: 5.4, h: 0.7, fill: { color: col } });
  s.addText(titlu, { x: x + 0.3, y: 1.95, w: 4.9, h: 0.5, fontFace: HF, fontSize: 17, bold: true, color: P.white, margin: 0 });
  s.addText(sub, { x: x + 0.3, y: 2.65, w: 4.9, h: 0.4, fontFace: BF, fontSize: 12.5, italic: true, color: P.muted, margin: 0 });
  s.addText(items.map(t => ({ text: t, options: { bullet: true, breakLine: true, fontSize: 13, color: P.text } })),
    { x: x + 0.35, y: 3.05, w: 4.85, h: 1.8, fontFace: BF, paraSpaceAfter: 5, margin: 0 });
}
etapaBox(0.85, "Etapa 1 — Tranzactie", "aplicare secventiala (compus)",
  ["Oferta -> tranzactie", "Drept de proprietate, finantare", "Conditii de vanzare, cheltuieli", "Conditiile pietei"], P.navy);
s.addShape(pres.shapes.LINE, { x: 6.3, y: 3.3, w: 0.6, h: 0, line: { color: P.gold, width: 3, endArrowType: "triangle" } });
etapaBox(6.95, "Etapa 2 — Proprietate", "aplicare aditiva pe pretul de baza",
  ["Localizare, acces, utilitati", "Suprafata, deschidere", "Inclinatie, tip teren", "Regim juridic / urbanism"], P.teal);
card(s, 0.85, 5.2, 11.5, 1.45, "FBF3DE");
s.addText([
  { text: "Selectie: ", options: { bold: true, color: P.navy } },
  { text: "comparabilul cu ajustarea bruta minima pe etapa de proprietate (oferta->tranzactie NU se contorizeaza).   ", options: { color: P.text } },
  { text: "Valoarea terenului = ", options: { bold: true, color: P.navy } },
  { text: "pret/mp corectat al comparabilului ales × suprafata terenului.", options: { color: P.text } },
], { x: 1.15, y: 5.35, w: 10.9, h: 1.15, fontFace: BF, fontSize: 14.5, valign: "middle", margin: 0 });
footer(s, 4);

/* ---------- S5 METODOLOGIE CASA + COST ---------- */
s = pres.addSlide(); header(s, "Metodologia · casa si cost", "Grila pe pret total + abordarea prin cost");
card(s, 0.85, 1.8, 5.7, 4.6);
s.addText("Casa — grila pe pret total", { x: 1.15, y: 2.0, w: 5.1, h: 0.5, fontFace: HF, fontSize: 18, bold: true, color: P.navy, margin: 0 });
s.addText([
  "Aceleasi doua etape (tranzactie secvential + proprietate aditiv), dar pe pretul TOTAL.",
  "Diferenta de marime se trateaza ca ajustare valorica de arie utila (pret unitar × diferenta mp).",
  "Fiecare comparabil este astfel 'adus' la subiect.",
  "Valoarea prin comparatie = pretul total corectat al comparabilului ales.",
].map(t => ({ text: t, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } })),
  { x: 1.2, y: 2.6, w: 5.1, h: 3.6, fontFace: BF, fontSize: 13.5, color: P.text, margin: 0 });

card(s, 6.85, 1.8, 5.6, 4.6);
s.addText("Abordarea prin cost (CIN)", { x: 7.15, y: 2.0, w: 5.0, h: 0.5, fontFace: HF, fontSize: 18, bold: true, color: P.navy, margin: 0 });
s.addText([
  "Cost de inlocuire net, segregat pe elemente (catalog IROVAL).",
  "CIN = CIB × (1-depr. fizica) × (1-depr. functionala) × (1-depr. externa).",
  "Depreciere fizica interpolata dupa varsta ponderata.",
  "Valoare prin cost = CIN + valoarea terenului.",
  "Reconciliere (piata / cost / ponderata) + alocare: constructii = proprietate - teren.",
].map(t => ({ text: t, options: { bullet: true, breakLine: true, paraSpaceAfter: 7 } })),
  { x: 7.2, y: 2.6, w: 5.0, h: 3.6, fontFace: BF, fontSize: 13.5, color: P.text, margin: 0 });
footer(s, 5);

/* ---------- S6 VALIDARE ---------- */
s = pres.addSlide();
s.background = { color: P.navy };
s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.55, w: 0.16, h: 0.5, fill: { color: P.gold } });
s.addText("VALIDARE", { x: 0.85, y: 0.5, w: 11, h: 0.3, fontFace: BF, fontSize: 12, color: P.gold, bold: true, charSpacing: 3, margin: 0 });
s.addText("Reproduce exact grilele reale", { x: 0.83, y: 0.78, w: 11.8, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: P.white, margin: 0 });
s.addText("Valorile de teren din patru dosare reale, reproduse la cent (EUR):", { x: 0.85, y: 1.7, w: 11.5, h: 0.4, fontFace: BF, fontSize: 15, color: P.ice, margin: 0 });
const stats = [["Maneciu", "44.000"], ["Brasov", "78.000"], ["Busteni", "34.000"], ["Breaza", "67.000"]];
stats.forEach((st, i) => {
  const x = 0.85 + i * 2.95;
  s.addShape(pres.shapes.RECTANGLE, { x, y: 2.4, w: 2.7, h: 2.0, fill: { color: P.navy2 }, line: { color: P.gold, width: 1 } });
  s.addText(st[1], { x, y: 2.7, w: 2.7, h: 0.9, align: "center", fontFace: HF, fontSize: 40, bold: true, color: P.gold, margin: 0 });
  s.addText("EUR", { x, y: 3.55, w: 2.7, h: 0.3, align: "center", fontFace: BF, fontSize: 12, color: P.ice, margin: 0 });
  s.addText(st[0], { x, y: 3.9, w: 2.7, h: 0.4, align: "center", fontFace: BF, fontSize: 15, bold: true, color: P.white, margin: 0 });
});
s.addText([
  { text: "Toate cele 12 comparabile de teren  ·  preturile totale ale comparabilelor de casa (Busteni)  ·  costul (CIN)  ", options: { color: P.ice } },
  { text: "— reproduse exact.", options: { color: P.gold, bold: true } },
], { x: 0.85, y: 4.9, w: 11.6, h: 0.6, fontFace: BF, fontSize: 15, margin: 0 });
s.addText("Aceasta este dovada ca aplicatia aplica aceeasi logica de calcul ca dosarele tale.",
  { x: 0.85, y: 5.6, w: 11.6, h: 0.5, fontFace: BF, fontSize: 13, italic: true, color: P.ice, margin: 0 });
footer(s, 6, true);

/* ---------- S7 WIZARD FLOW ---------- */
s = pres.addSlide(); header(s, "Fluxul de lucru", "Wizardul in cinci pasi");
const pasi = [
  ["1", "Adresa & lucrare", "Judet/localitate, client, beneficiar, evaluator, date"],
  ["2", "Proprietatea", "Teren, arii, an, elemente de cost, depreciere, atribute"],
  ["3", "Comparabile", "Cautare automata, import din link sau introducere manuala"],
  ["4", "Metoda & calcul", "Metoda, moneda, curs, fotografii, calcul + alerte"],
  ["5", "Raport", "Genereaza si descarca documentul Word, editabil"],
];
pasi.forEach((p, i) => {
  const x = 0.7 + i * 2.45;
  s.addShape(pres.shapes.OVAL, { x: x + 0.85, y: 2.0, w: 0.75, h: 0.75, fill: { color: P.navy } });
  s.addText(p[0], { x: x + 0.85, y: 2.0, w: 0.75, h: 0.75, align: "center", valign: "middle", fontFace: HF, fontSize: 26, bold: true, color: P.gold, margin: 0 });
  if (i < 4) s.addShape(pres.shapes.LINE, { x: x + 1.7, y: 2.38, w: 0.72, h: 0, line: { color: P.line, width: 2 } });
  card(s, x + 0.15, 3.1, 2.15, 2.5);
  s.addText(p[1], { x: x + 0.25, y: 3.3, w: 1.95, h: 0.7, align: "center", fontFace: HF, fontSize: 15, bold: true, color: P.navy, margin: 0 });
  s.addText(p[2], { x: x + 0.28, y: 4.05, w: 1.9, h: 1.4, align: "center", fontFace: BF, fontSize: 12, color: P.text, margin: 0 });
});
footer(s, 7);

/* ---------- S8 DESCOPERIRE ---------- */
s = pres.addSlide(); header(s, "Date externe", "Descoperirea automata de comparabile");
const flow = [
  ["Cauta", "Anunturi pe portaluri imobiliare, in zona aleasa"],
  ["Citeste", "Extrage atributele din descriere (an, stare, finisaj, incalzire, suprafete)"],
  ["Puncteaza", "Similaritate dupa 6 criterii ponderate fata de subiect"],
  ["Explica", "Pentru fiecare criteriu: referinta, gasit, diferenta, pondere"],
];
flow.forEach((f, i) => {
  const y = 1.85 + i * 1.16;
  card(s, 0.85, y, 7.4, 1.0);
  dot(s, 1.1, y + 0.33, P.teal, String(i + 1));
  s.addText(f[0], { x: 1.7, y: y + 0.12, w: 2.0, h: 0.75, valign: "middle", fontFace: HF, fontSize: 17, bold: true, color: P.navy, margin: 0 });
  s.addText(f[1], { x: 3.5, y: y + 0.12, w: 4.6, h: 0.78, valign: "middle", fontFace: BF, fontSize: 13, color: P.text, margin: 0 });
});
card(s, 8.55, 1.85, 3.9, 4.47, P.navy);
s.addText("De ce conteaza", { x: 8.8, y: 2.1, w: 3.4, h: 0.4, fontFace: HF, fontSize: 17, bold: true, color: P.gold, margin: 0 });
s.addText("Evaluatorul intelege DE CE un anunt e mai relevant decat altul — fara sa acceseze documentatia tehnica. Comparabilele alese pot popula direct grila; ajustarile le pune evaluatorul.",
  { x: 8.8, y: 2.6, w: 3.45, h: 3.4, fontFace: BF, fontSize: 14, color: P.ice, valign: "top", margin: 0 });
footer(s, 8);

/* ---------- S9 RAPORT ---------- */
s = pres.addSlide(); header(s, "Rezultatul", "Raportul Word generat");
s.addText([
  "Coperta, scrisoare de transmitere",
  "Declaratie de conformitate si certificare",
  "Termeni de referinta",
  "7 capitole de analiza (cu grilele de calcul)",
  "Alocarea valorii",
  "Riscul asociat garantiei (GEV 520)",
  "Anexe: surse comparabile + fotografii",
  "Caseta de semnatura",
].map(t => ({ text: t, options: { bullet: { code: "2713" }, breakLine: true, paraSpaceAfter: 7 } })),
  { x: 1.0, y: 1.85, w: 6.4, h: 4.6, fontFace: BF, fontSize: 15, color: P.text, margin: 0 });
card(s, 7.7, 1.85, 4.8, 3.3);
try { s.addImage({ path: path.join(DEMO, "fata.png"), x: 7.95, y: 2.1, w: 4.3, h: 1.35, sizing: { type: "cover", w: 4.3, h: 1.35 } }); } catch (e) {}
try { s.addImage({ path: path.join(DEMO, "curte.png"), x: 7.95, y: 3.55, w: 4.3, h: 1.35, sizing: { type: "cover", w: 4.3, h: 1.35 } }); } catch (e) {}
s.addText("Anexa foto — pozele intra direct in raport", { x: 7.7, y: 5.2, w: 4.8, h: 0.35, align: "center", fontFace: BF, fontSize: 11, italic: true, color: P.muted, margin: 0 });
card(s, 7.7, 5.65, 4.8, 0.85, "FBF3DE");
s.addText("Textul de analiza e redactat cu AI pe baza cifrelor — evaluatorul revizuieste.",
  { x: 7.9, y: 5.72, w: 4.45, h: 0.72, valign: "middle", fontFace: BF, fontSize: 12.5, color: P.text, margin: 0 });
footer(s, 9);

/* ---------- S10 GDPR ---------- */
s = pres.addSlide(); header(s, "Confidentialitate", "Datele personale nu ajung la AI");
const gdpr = [
  ["Date reale", "Nume, adresa, cadastral, CF, evaluator", P.navy],
  ["Anonimizare", "Inlocuite cu marcaje: [CLIENT], [ADRESA]...", P.gold],
  ["AI", "Primeste DOAR text anonimizat", P.teal],
  ["Demascare locala", "Numele reale revin pe calculator", P.green],
];
gdpr.forEach((g, i) => {
  const x = 0.85 + i * 3.0;
  card(s, x, 2.2, 2.7, 2.4);
  s.addShape(pres.shapes.RECTANGLE, { x, y: 2.2, w: 2.7, h: 0.12, fill: { color: g[2] } });
  s.addText(g[0], { x: x + 0.2, y: 2.5, w: 2.3, h: 0.6, fontFace: HF, fontSize: 16, bold: true, color: P.navy, margin: 0 });
  s.addText(g[1], { x: x + 0.2, y: 3.15, w: 2.35, h: 1.3, fontFace: BF, fontSize: 13, color: P.text, margin: 0 });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: x + 2.72, y: 3.4, w: 0.26, h: 0, line: { color: P.muted, width: 2, endArrowType: "triangle" } });
});
s.addText("Restul calculelor si generarea documentului se fac integral pe calculatorul evaluatorului.",
  { x: 0.85, y: 5.1, w: 11.6, h: 0.5, fontFace: BF, fontSize: 14, italic: true, color: P.muted, margin: 0 });
footer(s, 10);

/* ---------- S11 DE FACUT ---------- */
s = pres.addSlide(); header(s, "Onestitate", "Ce mai e de facut");
const todo = [
  "Validarea grilei de casa si pe celelalte dosare reale (Maneciu, Brasov)",
  "Cursul valutar — momentan introdus manual (nu automat de la BNR)",
  "Anexa cu documente (extras CF, acte) — momentan marcaj 'de atasat'",
  "Export PDF al raportului (acum Word, salvabil ca PDF manual)",
  "Mai multa testare pe cazuri reale variate",
];
todo.forEach((t, i) => {
  const y = 1.9 + i * 0.92;
  card(s, 0.85, y, 11.6, 0.76);
  s.addShape(pres.shapes.RECTANGLE, { x: 0.85, y, w: 0.12, h: 0.76, fill: { color: P.gold } });
  s.addText(t, { x: 1.25, y, w: 11.0, h: 0.76, valign: "middle", fontFace: BF, fontSize: 15, color: P.text, margin: 0 });
});
footer(s, 11);

/* ---------- S12 INTREBARI ---------- */
s = pres.addSlide();
s.background = { color: P.navy };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.22, fill: { color: P.gold } });
s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.7, w: 0.16, h: 0.5, fill: { color: P.gold } });
s.addText("CE FEEDBACK CAUT", { x: 0.85, y: 0.66, w: 11, h: 0.3, fontFace: BF, fontSize: 12, color: P.gold, bold: true, charSpacing: 3, margin: 0 });
s.addText("Intrebari pentru tine", { x: 0.83, y: 0.95, w: 11.8, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: P.white, margin: 0 });
const q = [
  "Metodologia terenului (doua etape, selectie pe ajustare bruta minima, fara oferta) — corecta?",
  "Metodologia casei (pret total, arie utila ca ajustare valorica) si regula de selectie — corecte?",
  "Reconcilierea si alocarea (constructii = proprietate - teren) — in regula pentru garantare?",
  "Raportul (declaratii, termeni, GEV 520, anexe) — complet si acceptabil pentru banci?",
  "Validarile automate (minim comparabile, outlier, limita ajustare) — praguri potrivite?",
  "Orice ar face raportul respins sau ar trebui adaugat.",
];
s.addText(q.map((t, i) => ({ text: (i + 1) + ".   " + t, options: { breakLine: true, paraSpaceAfter: 11, color: P.ice } })),
  { x: 1.0, y: 1.95, w: 11.2, h: 4.4, fontFace: BF, fontSize: 16, margin: 0 });
s.addText("Orice observatie, chiar si 'asa nu se face', e exact ce caut. Multumesc pentru timp.",
  { x: 1.0, y: 6.55, w: 11.2, h: 0.5, fontFace: HF, fontSize: 15, italic: true, bold: true, color: P.gold, margin: 0 });

pres.writeFile({ fileName: path.join("docs", "prezentare-aplicatie.pptx") }).then(f => console.log("scris:", f));
