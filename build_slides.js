const pptxgen = require("pptxgenjs");
const path = require("path");
const os = require("os");

// Paletă „registru cadastral / topograf" (aceeași identitate ca aplicația).
const P = {
  ink: "16263D", ink2: "21314E", parchLt: "E9E0CC", paper: "F2EEE2",
  card: "FBF8F0", sand: "FBF3DE",
  sienna: "9D4A25", siennaDeep: "7C3A1B", brass: "B08D57", brassHi: "D9C08A",
  cadastral: "2F6B4F", text: "1F2D45", muted: "5A6270", white: "FFFFFF",
  line: "D7CDB4", green: "2F6B4F", red: "9C2C1B",
  triB: "27408B", triY: "D7A92B", triR: "A5301F",
};
const HF = "Georgia", BF = "Segoe UI";
const DEMO = path.join(os.tmpdir(), "demo");

const pres = new pptxgen();
pres.defineLayout({ name: "W", width: 13.333, height: 7.5 });
pres.layout = "W";
pres.author = "Aplicatie evaluare ANEVAR";
pres.title = "Prezentare pentru evaluator";
const W = 13.333, H = 7.5;

const shadow = () => ({ type: "outer", color: "16263D", blur: 7, offset: 3, angle: 135, opacity: 0.12 });

// bandă tricoloră subțire (drapel)
function tricolor(slide, x, y, w, h) {
  const seg = w / 3;
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w: seg, h, fill: { color: P.triB } });
  slide.addShape(pres.shapes.RECTANGLE, { x: x + seg, y, w: seg, h, fill: { color: P.triY } });
  slide.addShape(pres.shapes.RECTANGLE, { x: x + 2 * seg, y, w: seg, h, fill: { color: P.triR } });
}

function header(slide, kicker, title) {
  slide.background = { color: P.paper };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.55, w: 0.16, h: 0.5, fill: { color: P.sienna } });
  slide.addText(kicker.toUpperCase(), { x: 0.85, y: 0.5, w: 11.5, h: 0.3, fontFace: BF, fontSize: 12, color: P.sienna, bold: true, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.83, y: 0.78, w: 11.8, h: 0.7, fontFace: HF, fontSize: 30, color: P.ink, bold: true, margin: 0 });
  // riglă de alamă sub titlu
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.85, y: 1.46, w: 11.6, h: 0.025, fill: { color: P.brass } });
}
function footer(slide, n, dark) {
  const col = dark ? P.parchLt : P.muted;
  slide.addText("Registru de evaluare ANEVAR  ·  aplicație locală offline  ·  document pentru review",
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
s.background = { color: P.ink };
tricolor(s, 0, 0, W, 0.22);
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 6.5, w: W, h: 1.0, fill: { color: P.ink2 } });
s.addText("REGISTRU DE EVALUARE · ANEVAR", { x: 0.9, y: 2.05, w: 11.5, h: 0.5, fontFace: BF, fontSize: 16, color: P.brassHi, bold: true, charSpacing: 4, margin: 0 });
s.addText("Asistent de evaluare imobiliară", { x: 0.9, y: 2.6, w: 11.5, h: 1.2, fontFace: HF, fontSize: 40, color: P.white, bold: true, margin: 0 });
s.addText("Casă + teren, apartament, comercial, industrial, agricol — pentru garantare, IFRS, asigurare, impozitare, litigiu",
  { x: 0.9, y: 4.15, w: 11.4, h: 0.9, fontFace: BF, fontSize: 17, color: P.parchLt, margin: 0 });
s.addText("Ce face aplicația · cum e gândită · ce metodologie aplică · ce e validat · ce urmează",
  { x: 0.9, y: 6.72, w: 11.5, h: 0.5, fontFace: BF, fontSize: 13, color: P.parchLt, valign: "middle", margin: 0 });

/* ---------- S2 CE ESTE ---------- */
s = pres.addSlide(); header(s, "Pe scurt", "Ce este aplicația");
const puncte = [
  ["Asistă evaluatorul, nu îl înlocuiește", "Automatizează partea repetitivă — calcule, căutare de comparabile, redactarea raportului. Evaluatorul decide și verifică (om în buclă)."],
  ["Rulează local, ca un singur fișier .exe", "Se deschide o pagină în browser, pe calculatorul propriu. Fără instalări, fără server extern — funcționează offline."],
  ["Datele rămân pe calculator", "Singurul moment când ceva pleacă în exterior e redactarea textului cu AI — și acolo datele personale sunt anonimizate înainte."],
];
puncte.forEach((p, i) => {
  const y = 1.7 + i * 1.6;
  card(s, 0.85, y, 11.6, 1.4);
  dot(s, 1.15, y + 0.5, P.sienna, String(i + 1));
  s.addText(p[0], { x: 1.75, y: y + 0.22, w: 10.4, h: 0.4, fontFace: HF, fontSize: 18, bold: true, color: P.ink, margin: 0 });
  s.addText(p[1], { x: 1.75, y: y + 0.66, w: 10.4, h: 0.6, fontFace: BF, fontSize: 14, color: P.text, margin: 0 });
});
footer(s, 2);

/* ---------- S3 ARHITECTURA ---------- */
s = pres.addSlide(); header(s, "Cum e gândită", "Module care lucrează împreună");
const comp = [
  ["Motor de calcul", "Cost (CIN), comparație (teren + casă), venit (capitalizare directă + DCF), reconciliere și alocare — pe tip de proprietate și scop.", P.sienna],
  ["Descoperire comparabile", "Caută anunțuri în zonă, le citește, le punctează după similaritate și propune cele mai potrivite.", P.cadastral],
  ["Generator de raport + AML", "Raportul Word (SEV 2025) cu text, grile și fotografii; plus modulul AML (Legea 129/2019): KYC, risc, documente.", P.brass],
  ["Wizard în 5 pași", "Ghidează evaluatorul de la identificarea proprietății până la descărcarea raportului.", P.green],
];
comp.forEach((c, i) => {
  const x = 0.85 + (i % 2) * 6.0, y = 1.75 + Math.floor(i / 2) * 2.45;
  card(s, x, y, 5.6, 2.2);
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.14, h: 2.2, fill: { color: c[2] } });
  s.addText(c[0], { x: x + 0.4, y: y + 0.28, w: 5.0, h: 0.5, fontFace: HF, fontSize: 20, bold: true, color: P.ink, margin: 0 });
  s.addText(c[1], { x: x + 0.4, y: y + 0.9, w: 5.0, h: 1.1, fontFace: BF, fontSize: 13.5, color: P.text, margin: 0 });
});
s.addText("Filosofia: fiecare cifră poate fi verificată — aplicația arată cum a ajuns la fiecare rezultat, nu doar valoarea finală.",
  { x: 0.85, y: 6.5, w: 11.6, h: 0.35, fontFace: BF, fontSize: 13, italic: true, color: P.muted, margin: 0 });
footer(s, 3);

/* ---------- S4 METODOLOGIE TEREN ---------- */
s = pres.addSlide(); header(s, "Metodologia · teren", "Grila de comparație în două etape");
function etapaBox(x, titlu, sub, items, col) {
  card(s, x, 1.85, 5.4, 3.1);
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.85, w: 5.4, h: 0.7, fill: { color: col } });
  s.addText(titlu, { x: x + 0.3, y: 1.95, w: 4.9, h: 0.5, fontFace: HF, fontSize: 17, bold: true, color: P.white, margin: 0 });
  s.addText(sub, { x: x + 0.3, y: 2.65, w: 4.9, h: 0.4, fontFace: BF, fontSize: 12.5, italic: true, color: P.muted, margin: 0 });
  s.addText(items.map(t => ({ text: t, options: { bullet: true, breakLine: true, fontSize: 13, color: P.text } })),
    { x: x + 0.35, y: 3.05, w: 4.85, h: 1.8, fontFace: BF, paraSpaceAfter: 5, margin: 0 });
}
etapaBox(0.85, "Etapa 1 — Tranzacție", "aplicare secvențială (compus)",
  ["Ofertă → tranzacție", "Drept de proprietate, finanțare", "Condiții de vânzare, cheltuieli", "Condițiile pieței"], P.ink);
s.addShape(pres.shapes.LINE, { x: 6.3, y: 3.3, w: 0.6, h: 0, line: { color: P.sienna, width: 3, endArrowType: "triangle" } });
etapaBox(6.95, "Etapa 2 — Proprietate", "aplicare aditivă pe prețul de bază",
  ["Localizare, acces, utilități", "Suprafață, deschidere", "Înclinație, tip teren", "Regim juridic / urbanism"], P.cadastral);
card(s, 0.85, 5.2, 11.5, 1.45, P.sand);
s.addText([
  { text: "Selecție: ", options: { bold: true, color: P.siennaDeep } },
  { text: "comparabilul cu ajustarea brută minimă pe etapa de proprietate (ofertă→tranzacție NU se contorizează).   ", options: { color: P.text } },
  { text: "Valoarea terenului = ", options: { bold: true, color: P.siennaDeep } },
  { text: "preț/mp corectat al comparabilului ales × suprafața terenului.", options: { color: P.text } },
], { x: 1.15, y: 5.35, w: 10.9, h: 1.15, fontFace: BF, fontSize: 14.5, valign: "middle", margin: 0 });
footer(s, 4);

/* ---------- S5 METODOLOGIE CASA + COST + VENIT ---------- */
s = pres.addSlide(); header(s, "Metodologia · casă, cost, venit", "Comparație pe preț total · cost · venit");
card(s, 0.85, 1.8, 5.7, 4.6);
s.addText("Casă — grilă pe preț total", { x: 1.15, y: 2.0, w: 5.1, h: 0.5, fontFace: HF, fontSize: 18, bold: true, color: P.ink, margin: 0 });
s.addText([
  "Aceleași două etape (tranzacție secvențial + proprietate aditiv), dar pe prețul TOTAL.",
  "Diferența de mărime se tratează ca ajustare valorică de arie utilă (preț unitar × diferență mp).",
  "Fiecare comparabil este astfel „adus” la subiect.",
  "Valoarea prin comparație = prețul total corectat al comparabilului ales.",
].map(t => ({ text: t, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } })),
  { x: 1.2, y: 2.6, w: 5.1, h: 3.6, fontFace: BF, fontSize: 13.5, color: P.text, margin: 0 });

card(s, 6.85, 1.8, 5.6, 4.6);
s.addText("Cost (CIN) și venit", { x: 7.15, y: 2.0, w: 5.0, h: 0.5, fontFace: HF, fontSize: 18, bold: true, color: P.ink, margin: 0 });
s.addText([
  "Cost de înlocuire net, segregat pe elemente (catalog IROVAL).",
  "CIN = CIB × (1 − depr. fizică) × (1 − funcțională) × (1 − externă); valoare = CIN + teren.",
  "Venit: capitalizare directă (VBP din grila de chirii) sau DCF (fluxuri actualizate + valoare reziduală).",
  "Reconciliere (cost / comparație / venit) + alocare: construcții = proprietate − teren.",
  "Conform SEV 103 „Abordări” și SEV 105 „Modele de evaluare”.",
].map(t => ({ text: t, options: { bullet: true, breakLine: true, paraSpaceAfter: 7 } })),
  { x: 7.2, y: 2.6, w: 5.0, h: 3.6, fontFace: BF, fontSize: 13, color: P.text, margin: 0 });
footer(s, 5);

/* ---------- S6 VALIDARE ---------- */
s = pres.addSlide();
s.background = { color: P.ink };
s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.55, w: 0.16, h: 0.5, fill: { color: P.brassHi } });
s.addText("VALIDARE", { x: 0.85, y: 0.5, w: 11, h: 0.3, fontFace: BF, fontSize: 12, color: P.brassHi, bold: true, charSpacing: 3, margin: 0 });
s.addText("Reproduce exact grilele reale", { x: 0.83, y: 0.78, w: 11.8, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: P.white, margin: 0 });
s.addText("Valorile de teren din patru dosare reale, reproduse la cent (EUR):", { x: 0.85, y: 1.7, w: 11.5, h: 0.4, fontFace: BF, fontSize: 15, color: P.parchLt, margin: 0 });
const stats = [["Mâneciu", "44.000"], ["Brașov", "78.000"], ["Bușteni", "34.000"], ["Breaza", "67.000"]];
stats.forEach((st, i) => {
  const x = 0.85 + i * 2.95;
  s.addShape(pres.shapes.RECTANGLE, { x, y: 2.4, w: 2.7, h: 2.0, fill: { color: P.ink2 }, line: { color: P.brass, width: 1 } });
  s.addText(st[1], { x, y: 2.7, w: 2.7, h: 0.9, align: "center", fontFace: HF, fontSize: 38, bold: true, color: P.brassHi, margin: 0 });
  s.addText("EUR", { x, y: 3.55, w: 2.7, h: 0.3, align: "center", fontFace: BF, fontSize: 12, color: P.parchLt, margin: 0 });
  s.addText(st[0], { x, y: 3.9, w: 2.7, h: 0.4, align: "center", fontFace: BF, fontSize: 15, bold: true, color: P.white, margin: 0 });
});
s.addText([
  { text: "Toate comparabilele de teren  ·  prețurile totale ale comparabilelor de casă  ·  costul (CIN)  ", options: { color: P.parchLt } },
  { text: "— reproduse exact.", options: { color: P.brassHi, bold: true } },
], { x: 0.85, y: 4.9, w: 11.6, h: 0.5, fontFace: BF, fontSize: 15, margin: 0 });
s.addText("Acoperit de 375 de teste automate (verzi). Aceeași logică de calcul ca dosarele reale.",
  { x: 0.85, y: 5.55, w: 11.6, h: 0.5, fontFace: BF, fontSize: 13, italic: true, color: P.parchLt, margin: 0 });
footer(s, 6, true);

/* ---------- S7 WIZARD FLOW ---------- */
s = pres.addSlide(); header(s, "Fluxul de lucru", "Wizardul în cinci pași");
const pasi = [
  ["1", "Adresă & lucrare", "Județ/localitate, client, beneficiar, evaluator, date"],
  ["2", "Proprietatea", "Tip proprietate, teren, arii, an, elemente de cost, atribute"],
  ["3", "Comparabile", "Căutare automată, import din link sau introducere manuală"],
  ["4", "Metodă & calcul", "Abordare, monedă, curs BNR, fotografii, calcul + alerte"],
  ["5", "Raport", "Generează și descarcă documentul Word, editabil"],
];
pasi.forEach((p, i) => {
  const x = 0.7 + i * 2.45;
  s.addShape(pres.shapes.OVAL, { x: x + 0.85, y: 2.0, w: 0.75, h: 0.75, fill: { color: P.sienna } });
  s.addText(p[0], { x: x + 0.85, y: 2.0, w: 0.75, h: 0.75, align: "center", valign: "middle", fontFace: HF, fontSize: 26, bold: true, color: P.white, margin: 0 });
  if (i < 4) s.addShape(pres.shapes.LINE, { x: x + 1.7, y: 2.38, w: 0.72, h: 0, line: { color: P.brass, width: 2 } });
  card(s, x + 0.15, 3.1, 2.15, 2.5);
  s.addText(p[1], { x: x + 0.25, y: 3.3, w: 1.95, h: 0.7, align: "center", fontFace: HF, fontSize: 15, bold: true, color: P.ink, margin: 0 });
  s.addText(p[2], { x: x + 0.28, y: 4.05, w: 1.9, h: 1.4, align: "center", fontFace: BF, fontSize: 12, color: P.text, margin: 0 });
});
s.addText("Stepper clickabil + panou „Date dosar” cu recapitulare live · interfață în stil registru cadastral.",
  { x: 0.85, y: 6.0, w: 11.6, h: 0.4, fontFace: BF, fontSize: 13, italic: true, color: P.muted, margin: 0 });
footer(s, 7);

/* ---------- S8 DESCOPERIRE ---------- */
s = pres.addSlide(); header(s, "Date externe", "Descoperirea automată de comparabile");
const flow = [
  ["Caută", "Anunțuri pe portaluri imobiliare, în zona aleasă"],
  ["Citește", "Extrage atributele din descriere (an, stare, finisaj, încălzire, suprafețe)"],
  ["Punctează", "Similaritate după 6 criterii ponderate față de subiect"],
  ["Explică", "Pentru fiecare criteriu: referință, găsit, diferență, pondere"],
];
flow.forEach((f, i) => {
  const y = 1.85 + i * 1.16;
  card(s, 0.85, y, 7.4, 1.0);
  dot(s, 1.1, y + 0.33, P.cadastral, String(i + 1));
  s.addText(f[0], { x: 1.7, y: y + 0.12, w: 2.0, h: 0.75, valign: "middle", fontFace: HF, fontSize: 17, bold: true, color: P.ink, margin: 0 });
  s.addText(f[1], { x: 3.5, y: y + 0.12, w: 4.6, h: 0.78, valign: "middle", fontFace: BF, fontSize: 13, color: P.text, margin: 0 });
});
card(s, 8.55, 1.85, 3.9, 4.47, P.ink);
s.addText("Import prin extensie de browser", { x: 8.8, y: 2.1, w: 3.4, h: 0.7, fontFace: HF, fontSize: 16, bold: true, color: P.brassHi, margin: 0 });
s.addText([
  { text: "Evaluatorul deschide MANUAL un anunț pe storia.ro / imobiliare.ro și apasă un buton — extensia trimite pagina în aplicație. Fără scraping automat, fără anti-bot.", options: { breakLine: true, paraSpaceAfter: 8 } },
  { text: "Anunțurile intră într-o coadă persistentă; din ele populează direct grila. Prețurile sunt din OFERTE — ajustarea ofertă→tranzacție o pune evaluatorul.", options: {} },
],
  { x: 8.8, y: 2.85, w: 3.45, h: 3.3, fontFace: BF, fontSize: 13, color: P.parchLt, valign: "top", margin: 0 });
footer(s, 8);

/* ---------- S9 RAPORT ---------- */
s = pres.addSlide(); header(s, "Rezultatul", "Raportul Word generat");
s.addText([
  "Copertă, scrisoare de transmitere",
  "Declarație de conformitate și certificare",
  "Termeni de referință (SEV 101)",
  "7 capitole de analiză (cu grilele de calcul, SEV 106)",
  "Alocarea valorii",
  "Riscul asociat garanției (GEV 520)",
  "Anexe: surse comparabile + fotografii",
  "Casetă de semnătură",
].map(t => ({ text: t, options: { bullet: { code: "2713" }, breakLine: true, paraSpaceAfter: 7 } })),
  { x: 1.0, y: 1.85, w: 6.4, h: 4.6, fontFace: BF, fontSize: 15, color: P.text, margin: 0 });
card(s, 7.7, 1.85, 4.8, 3.3);
try { s.addImage({ path: path.join(DEMO, "fata.png"), x: 7.95, y: 2.1, w: 4.3, h: 1.35, sizing: { type: "cover", w: 4.3, h: 1.35 } }); } catch (e) {}
try { s.addImage({ path: path.join(DEMO, "curte.png"), x: 7.95, y: 3.55, w: 4.3, h: 1.35, sizing: { type: "cover", w: 4.3, h: 1.35 } }); } catch (e) {}
s.addText("Anexa foto — pozele intră direct în raport", { x: 7.7, y: 5.2, w: 4.8, h: 0.35, align: "center", fontFace: BF, fontSize: 11, italic: true, color: P.muted, margin: 0 });
card(s, 7.7, 5.65, 4.8, 0.85, P.sand);
s.addText("Textul de analiză e redactat cu AI pe baza cifrelor — evaluatorul revizuiește.",
  { x: 7.9, y: 5.72, w: 4.45, h: 0.72, valign: "middle", fontFace: BF, fontSize: 12.5, color: P.text, margin: 0 });
footer(s, 9);

/* ---------- S10 GDPR ---------- */
s = pres.addSlide(); header(s, "Confidențialitate", "Datele personale nu ajung la AI");
const gdpr = [
  ["Date reale", "Nume, adresă, cadastral, CF, evaluator", P.ink],
  ["Anonimizare", "Înlocuite cu marcaje: [CLIENT], [ADRESA]...", P.sienna],
  ["AI", "Primește DOAR text anonimizat", P.cadastral],
  ["Demascare locală", "Numele reale revin pe calculator", P.green],
];
gdpr.forEach((g, i) => {
  const x = 0.85 + i * 3.0;
  card(s, x, 2.2, 2.7, 2.4);
  s.addShape(pres.shapes.RECTANGLE, { x, y: 2.2, w: 2.7, h: 0.12, fill: { color: g[2] } });
  s.addText(g[0], { x: x + 0.2, y: 2.5, w: 2.3, h: 0.6, fontFace: HF, fontSize: 16, bold: true, color: P.ink, margin: 0 });
  s.addText(g[1], { x: x + 0.2, y: 3.15, w: 2.35, h: 1.3, fontFace: BF, fontSize: 13, color: P.text, margin: 0 });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: x + 2.72, y: 3.4, w: 0.26, h: 0, line: { color: P.muted, width: 2, endArrowType: "triangle" } });
});
s.addText("Restul calculelor și generarea documentului se fac integral pe calculatorul evaluatorului.",
  { x: 0.85, y: 5.1, w: 11.6, h: 0.5, fontFace: BF, fontSize: 14, italic: true, color: P.muted, margin: 0 });
footer(s, 10);

/* ---------- S11 DE FACUT ---------- */
s = pres.addSlide(); header(s, "Onestitate", "Ce mai e de făcut");
const todo = [
  "Surse de date oficiale: catalog IROVAL (costuri unitare), BIG, ANCPI — necesită acces/membru ANEVAR",
  "Liste AML live (sancțiuni UE/ONU, PEP) — momentan injectabile, de reîmprospătat din surse oficiale",
  "Validarea juridică finală a textelor AML generate (de către un jurist)",
  "Semnătură digitală a .exe (elimină avertismentul SmartScreen)",
  "Mai multă testare cu cititor de ecran (NVDA) și pe cazuri reale variate",
];
todo.forEach((t, i) => {
  const y = 1.9 + i * 0.92;
  card(s, 0.85, y, 11.6, 0.76);
  s.addShape(pres.shapes.RECTANGLE, { x: 0.85, y, w: 0.12, h: 0.76, fill: { color: P.sienna } });
  s.addText(t, { x: 1.25, y, w: 11.0, h: 0.76, valign: "middle", fontFace: BF, fontSize: 14, color: P.text, margin: 0 });
});
footer(s, 11);

/* ---------- S12 INTREBARI ---------- */
s = pres.addSlide();
s.background = { color: P.ink };
tricolor(s, 0, 0, W, 0.22);
s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.7, w: 0.16, h: 0.5, fill: { color: P.brassHi } });
s.addText("CE FEEDBACK CAUT", { x: 0.85, y: 0.66, w: 11, h: 0.3, fontFace: BF, fontSize: 12, color: P.brassHi, bold: true, charSpacing: 3, margin: 0 });
s.addText("Întrebări pentru tine", { x: 0.83, y: 0.95, w: 11.8, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: P.white, margin: 0 });
const q = [
  "Metodologia terenului (două etape, selecție pe ajustare brută minimă, fără ofertă) — corectă?",
  "Metodologia casei (preț total, arie utilă ca ajustare valorică) și regula de selecție — corecte?",
  "Abordarea prin venit (capitalizare directă + DCF) și grila de chirii — în regulă?",
  "Reconcilierea și alocarea (construcții = proprietate − teren) — în regulă pentru garantare?",
  "Raportul (declarații, termeni, GEV 520, anexe) — complet și acceptabil pentru bănci?",
  "Orice ar face raportul respins sau ar trebui adăugat.",
];
s.addText(q.map((t, i) => ({ text: (i + 1) + ".   " + t, options: { breakLine: true, paraSpaceAfter: 11, color: P.parchLt } })),
  { x: 1.0, y: 1.95, w: 11.2, h: 4.4, fontFace: BF, fontSize: 16, margin: 0 });
s.addText("Orice observație, chiar și „așa nu se face”, e exact ce caut. Mulțumesc pentru timp.",
  { x: 1.0, y: 6.55, w: 11.2, h: 0.5, fontFace: HF, fontSize: 15, italic: true, bold: true, color: P.brassHi, margin: 0 });

pres.writeFile({ fileName: path.join("docs", "prezentare-aplicatie.pptx") }).then(f => console.log("scris:", f));
