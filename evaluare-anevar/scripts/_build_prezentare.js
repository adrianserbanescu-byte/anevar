/* Generează docs/prezentare-aplicatie.pptx — prezentarea «Registru de Evaluare · ANEVAR» pentru evaluatori.
 * Rulează: node scripts/_build_prezentare.js   (necesită: npm i -g pptxgenjs)
 * Acum deck-ul are GENERATOR (înainte era construit manual) — reproductibil + ușor de actualizat.
 */
const pptxgen = require("pptxgenjs");
const path = require("path");

// ── Paletă «registru/cadastral»: navy dominant + accent auriu (oficial) + hârtie deschisă ──
const INK = "13243B";     // navy foarte închis — titlu + concluzie
const NAVY = "1F3A5F";    // albastru aplicație (dominant)
const GOLD = "C9A227";    // accent auriu (registru oficial)
const PAPER = "F5F6F8";   // fundal conținut (deschis)
const ICE = "E4EAF3";     // panou albastru deschis
const SLATE = "5B6B7F";   // text secundar
const INKTX = "1B2A3D";   // text corp închis
const WHITE = "FFFFFF";
const HF = "Georgia", BF = "Calibri";   // serif oficial pt titluri + sans curat pt corp

const pres = new pptxgen();
pres.defineLayout({ name: "W", width: 13.333, height: 7.5 });
pres.layout = "W";
pres.author = "Evaluare ANEVAR";
pres.title = "Registru de Evaluare · ANEVAR";
const W = 13.333, H = 7.5, MX = 0.62;
const sh = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function footer(s, n) {
  s.addShape(pres.shapes.LINE, { x: MX, y: 7.04, w: W - 2 * MX, h: 0, line: { color: "D8DCE3", width: 1 } });
  s.addText("Registru de evaluare ANEVAR  ·  aplicație locală offline  ·  document pentru review",
    { x: MX, y: 7.08, w: 10.5, h: 0.32, fontFace: BF, fontSize: 9, color: SLATE, align: "left", valign: "middle", margin: 0 });
  s.addText(String(n), { x: W - MX - 0.5, y: 7.08, w: 0.5, h: 0.32, fontFace: BF, fontSize: 9, color: SLATE, align: "right", valign: "middle", margin: 0 });
}
function head(s, kicker, title) {
  s.addShape(pres.shapes.RECTANGLE, { x: MX, y: 0.52, w: 0.17, h: 0.17, fill: { color: GOLD } });
  s.addText(kicker.toUpperCase(), { x: MX + 0.28, y: 0.46, w: 11, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: GOLD, charSpacing: 3, margin: 0, valign: "middle" });
  s.addText(title, { x: MX, y: 0.82, w: W - 2 * MX, h: 0.72, fontFace: HF, fontSize: 30, bold: true, color: NAVY, margin: 0, valign: "middle" });
}
function numCircle(s, x, y, n, d = 0.5, fill = NAVY) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill } });
  // text închis pe auriu (alb pe auriu = contrast slab), alb pe navy
  s.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: HF, fontSize: 17, bold: true, color: fill === GOLD ? INK : WHITE, margin: 0 });
}

// ════════════════ SLIDE 1 — TITLU ════════════════
let s = pres.addSlide(); s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.16, fill: { color: GOLD } });
// siglă: chiar icoana aplicației (casă albă pe albastru) — consecvent cu .exe
s.addImage({ path: path.resolve(__dirname, "..", "assets", "logo.png"), x: MX, y: 0.92, w: 1.06, h: 1.06 });
s.addText("REGISTRU DE EVALUARE", { x: MX, y: 2.55, w: 12, h: 0.9, fontFace: HF, fontSize: 50, bold: true, color: WHITE, charSpacing: 1, margin: 0 });
s.addText("· ANEVAR", { x: MX, y: 3.5, w: 12, h: 0.6, fontFace: HF, fontSize: 30, color: GOLD, margin: 0 });
s.addText("Asistent de evaluare imobiliară", { x: MX, y: 4.25, w: 12, h: 0.5, fontFace: BF, fontSize: 21, color: "C7D2E2", margin: 0 });
s.addText("Casă + teren · apartament · comercial · industrial · agricol — pentru garantare, IFRS, asigurare, impozitare, litigiu",
  { x: MX, y: 4.85, w: 12.1, h: 0.5, fontFace: BF, fontSize: 13.5, color: "8FA1B8", margin: 0 });
s.addShape(pres.shapes.LINE, { x: MX, y: 5.75, w: 12.1, h: 0, line: { color: "33476A", width: 1 } });
s.addText("Ce face aplicația  ·  cum e gândită  ·  ce metodologie aplică  ·  ce e validat  ·  ce urmează",
  { x: MX, y: 5.9, w: 12.1, h: 0.4, fontFace: BF, fontSize: 13, italic: true, color: "A9B8CC", margin: 0 });

// ════════════════ SLIDE 2 — PE SCURT ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Pe scurt", "Ce este aplicația");
const sc = [
  ["Asistă evaluatorul, nu îl înlocuiește", "Automatizează partea repetitivă — calcule, căutare de comparabile, redactarea raportului. Evaluatorul decide și verifică (om în buclă)."],
  ["Rulează local, ca un singur .exe", "Se deschide o pagină în browser, pe calculatorul propriu. Fără instalări, fără server extern — funcționează offline."],
  ["Datele rămân pe calculator", "Singurul moment când ceva pleacă în exterior e redactarea textului cu AI — și acolo datele personale sunt anonimizate înainte."],
];
sc.forEach((c, i) => {
  const x = MX + i * 4.06;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.85, w: 3.8, h: 4.4, rectRadius: 0.09, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.85, w: 3.8, h: 0.12, fill: { color: GOLD } });
  numCircle(s, x + 0.35, 2.25, i + 1, 0.62);
  s.addText(c[0], { x: x + 0.32, y: 3.1, w: 3.2, h: 0.95, fontFace: HF, fontSize: 17.5, bold: true, color: NAVY, margin: 0, valign: "top" });
  s.addText(c[1], { x: x + 0.32, y: 4.05, w: 3.2, h: 2.0, fontFace: BF, fontSize: 13, color: INKTX, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });
});
footer(s, 2);

// ════════════════ SLIDE 3 — CUM E GÂNDITĂ ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Cum e gândită", "Module care lucrează împreună");
const mod = [
  ["Motor de calcul", "Cost (CIN), comparație (teren + casă), venit (capitalizare directă + DCF), reconciliere și alocare — pe tip de proprietate și scop."],
  ["Descoperire comparabile", "Caută anunțuri în zonă, le citește, le punctează după similaritate și propune cele mai potrivite."],
  ["Generator de raport + AML", "Raport Word (SEV 2025) cu text, grile și fotografii; plus modulul AML (Legea 129/2019): KYC, risc, documente."],
  ["Wizard în 5 pași", "Ghidează evaluatorul de la identificarea proprietății până la descărcarea raportului."],
];
mod.forEach((m, i) => {
  const x = MX + (i % 2) * 6.15, y = 1.8 + Math.floor(i / 2) * 1.95;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.9, h: 1.78, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.13, h: 1.78, fill: { color: NAVY } });
  s.addText(m[0], { x: x + 0.35, y: y + 0.2, w: 5.4, h: 0.45, fontFace: HF, fontSize: 17, bold: true, color: NAVY, margin: 0 });
  s.addText(m[1], { x: x + 0.35, y: y + 0.68, w: 5.35, h: 1.0, fontFace: BF, fontSize: 12.5, color: INKTX, margin: 0, valign: "top", lineSpacingMultiple: 1.03 });
});
s.addText([{ text: "Filosofia: ", options: { bold: true, color: NAVY } }, { text: "fiecare cifră poate fi verificată — aplicația arată cum a ajuns la fiecare rezultat, nu doar valoarea finală.", options: { italic: true, color: INKTX } }],
  { x: MX, y: 5.85, w: 12.1, h: 0.5, fontFace: BF, fontSize: 13.5, align: "center", margin: 0 });
footer(s, 3);

// ════════════════ SLIDE 4 — METODOLOGIA TEREN ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Metodologia · teren", "Grila de comparație în două etape");
const et = [
  ["Etapa 1 — Tranzacție", "aplicare secvențială (compus)", ["Ofertă → tranzacție", "Drept de proprietate, finanțare", "Condiții de vânzare, cheltuieli", "Condițiile pieței"]],
  ["Etapa 2 — Proprietate", "aplicare aditivă pe prețul de bază", ["Localizare, acces, utilități", "Suprafață, deschidere", "Înclinație, tip teren", "Regim juridic / urbanism"]],
];
et.forEach((e, i) => {
  const x = MX + i * 6.15;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.8, w: 5.9, h: 3.15, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.8, w: 5.9, h: 0.66, fill: { color: i === 0 ? NAVY : GOLD } });
  s.addText(e[0], { x: x + 0.3, y: 1.8, w: 5.3, h: 0.66, fontFace: HF, fontSize: 16.5, bold: true, color: i === 0 ? WHITE : INK, margin: 0, valign: "middle" });
  s.addText(e[1], { x: x + 0.3, y: 2.5, w: 5.3, h: 0.3, fontFace: BF, fontSize: 11.5, italic: true, color: SLATE, margin: 0 });
  s.addText(e[2].map((t, k) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: k < 3 ? 5 : 0 } })),
    { x: x + 0.35, y: 2.9, w: 5.25, h: 1.9, fontFace: BF, fontSize: 13, color: INKTX, margin: 0, valign: "top" });
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 5.2, w: 12.1, h: 1.05, rectRadius: 0.07, fill: { color: ICE } });
s.addText([{ text: "Selecție: ", options: { bold: true, color: NAVY } },
  { text: "comparabilul cu ajustarea brută minimă pe etapa de proprietate (ofertă→tranzacție NU se contorizează).  ", options: { color: INKTX } },
  { text: "Valoarea terenului = preț/mp corectat al comparabilului ales × suprafața terenului.", options: { color: INKTX, italic: true } }],
  { x: MX + 0.35, y: 5.2, w: 11.4, h: 1.05, fontFace: BF, fontSize: 13, valign: "middle", margin: 0, lineSpacingMultiple: 1.05 });
footer(s, 4);

// ════════════════ SLIDE 5 — METODOLOGIA CASĂ / COST / VENIT ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Metodologia · casă, cost, venit", "Comparație pe preț total · cost · venit");
const col = [
  ["Casă — grilă pe preț total", [
    "Aceleași două etape (tranzacție secvențial + proprietate aditiv), dar pe prețul TOTAL.",
    "Diferența de mărime = ajustare valorică de arie utilă (preț unitar × diferență mp).",
    "Fiecare comparabil este «adus» la subiect.",
    "Valoarea prin comparație = prețul total corectat al comparabilului ales."]],
  ["Cost (CIN) și venit", [
    "Cost de înlocuire net, segregat pe elemente (catalog IROVAL).",
    "CIN = CIB × (1−depr. fizică) × (1−funcțională) × (1−externă); valoare = CIN + teren.",
    "Venit: capitalizare directă (VBP din grila de chirii) sau DCF (fluxuri + valoare reziduală).",
    "Reconciliere (cost / comparație / venit) + alocare: construcții = proprietate − teren."]],
];
col.forEach((c, i) => {
  const x = MX + i * 6.15;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.8, w: 5.9, h: 3.5, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.8, w: 0.13, h: 3.5, fill: { color: i === 0 ? NAVY : GOLD } });
  s.addText(c[0], { x: x + 0.35, y: 2.0, w: 5.4, h: 0.45, fontFace: HF, fontSize: 16.5, bold: true, color: NAVY, margin: 0 });
  s.addText(c[1].map((t, k) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: k < 3 ? 7 : 0 } })),
    { x: x + 0.38, y: 2.5, w: 5.3, h: 2.6, fontFace: BF, fontSize: 12.5, color: INKTX, margin: 0, valign: "top", lineSpacingMultiple: 1.03 });
});
s.addText("Conform SEV 103 «Abordări» și SEV 105 «Modele de evaluare».",
  { x: MX, y: 5.55, w: 12.1, h: 0.5, fontFace: BF, fontSize: 13, italic: true, align: "center", color: SLATE, margin: 0 });
footer(s, 5);

// ════════════════ SLIDE 6 — VALIDARE ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Validare", "Reproduce exact grilele reale");
s.addText("Valorile de teren din patru dosare reale, reproduse la cent (EUR):",
  { x: MX, y: 1.75, w: 12, h: 0.4, fontFace: BF, fontSize: 14.5, color: INKTX, margin: 0 });
const stat = [["44.000", "Mâneciu"], ["78.000", "Brașov"], ["34.000", "Bușteni"], ["67.000", "Breaza"]];
stat.forEach((v, i) => {
  const x = MX + i * 3.06;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.4, w: 2.85, h: 2.4, rectRadius: 0.09, fill: { color: NAVY }, shadow: sh() });
  s.addText(v[0], { x, y: 2.75, w: 2.85, h: 0.95, align: "center", fontFace: HF, fontSize: 41, bold: true, color: WHITE, margin: 0 });
  s.addText("EUR", { x, y: 3.7, w: 2.85, h: 0.35, align: "center", fontFace: BF, fontSize: 13, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
  s.addText(v[1], { x, y: 4.08, w: 2.85, h: 0.5, align: "center", fontFace: BF, fontSize: 15, color: "C7D2E2", margin: 0 });
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 5.25, w: 12.1, h: 1.05, rectRadius: 0.07, fill: { color: ICE } });
s.addText([{ text: "Toate ", options: { bold: true, color: NAVY } },
  { text: "comparabilele de teren · prețurile totale ale comparabilelor de casă · costul (CIN) — ", options: { color: INKTX } },
  { text: "reproduse exact. ", options: { bold: true, color: NAVY } },
  { text: "Aplicația nu «inventează» cifre: aplică aceeași metodă ca evaluatorul, transparent.", options: { italic: true, color: INKTX } }],
  { x: MX + 0.35, y: 5.25, w: 11.4, h: 1.05, fontFace: BF, fontSize: 13, valign: "middle", margin: 0, lineSpacingMultiple: 1.05 });
footer(s, 6);

// ════════════════ SLIDE 7 — FLUXUL DE LUCRU ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Fluxul de lucru", "Wizardul în cinci pași");
const steps = [
  ["Adresă & lucrare", "Județ/localitate, client, beneficiar, evaluator, date"],
  ["Proprietatea", "Tip, teren, arii, an, elemente de cost, atribute"],
  ["Comparabile", "Căutare automată, import din link sau manual"],
  ["Metodă & calcul", "Abordare, monedă, curs BNR, fotografii, calcul + alerte"],
  ["Raport", "Generează și descarcă documentul Word, editabil"],
];
steps.forEach((st, i) => {
  const x = MX + i * 2.42;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.15, w: 2.26, h: 3.3, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
  numCircle(s, x + 0.83, 1.78, i + 1, 0.62, i === 4 ? GOLD : NAVY);
  s.addText(st[0], { x: x + 0.15, y: 2.7, w: 1.96, h: 0.7, align: "center", fontFace: HF, fontSize: 14.5, bold: true, color: NAVY, margin: 0, valign: "top" });
  s.addText(st[1], { x: x + 0.18, y: 3.45, w: 1.9, h: 1.8, align: "center", fontFace: BF, fontSize: 11.5, color: INKTX, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });
  if (i < 4) s.addText("→", { x: x + 2.05, y: 1.78, w: 0.55, h: 0.62, align: "center", valign: "middle", fontFace: BF, fontSize: 22, bold: true, color: GOLD, margin: 0 });
});
s.addText("Stepper clickabil + panou «Date dosar» cu recapitulare live · interfață în stil registru cadastral.",
  { x: MX, y: 6.0, w: 12.1, h: 0.5, fontFace: BF, fontSize: 13, italic: true, align: "center", color: SLATE, margin: 0 });
footer(s, 7);

// ════════════════ SLIDE 8 — DATE EXTERNE ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Date externe", "Descoperirea automată de comparabile");
const ext = [["Caută", "Anunțuri pe portaluri, în zona aleasă"], ["Citește", "Extrage atribute (an, stare, finisaj, suprafețe)"], ["Punctează", "Similaritate, 6 criterii ponderate vs. subiect"], ["Explică", "Per criteriu: referință, găsit, diferență, pondere"]];
ext.forEach((e, i) => {
  const x = MX + i * 3.06;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.95, w: 2.85, h: 1.95, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
  numCircle(s, x + 0.3, 2.2, i + 1, 0.5);
  s.addText(e[0], { x: x + 0.95, y: 2.2, w: 1.8, h: 0.5, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0, valign: "middle" });
  s.addText(e[1], { x: x + 0.3, y: 2.85, w: 2.4, h: 0.95, fontFace: BF, fontSize: 12, color: INKTX, margin: 0, valign: "top", lineSpacingMultiple: 1.03 });
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 4.2, w: 12.1, h: 2.0, rectRadius: 0.08, fill: { color: INK }, shadow: sh() });
s.addShape(pres.shapes.RECTANGLE, { x: MX, y: 4.2, w: 0.14, h: 2.0, fill: { color: GOLD } });
s.addText("Import prin extensie de browser", { x: MX + 0.4, y: 4.4, w: 11.4, h: 0.45, fontFace: HF, fontSize: 17, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "Evaluatorul deschide MANUAL un anunț pe storia.ro / imobiliare.ro și apasă un buton — extensia trimite pagina în aplicație. Fără scraping automat, fără anti-bot.", options: { breakLine: true, paraSpaceAfter: 6 } },
  { text: "Anunțurile intră într-o coadă persistentă și populează direct grila. Prețurile sunt din OFERTE — ajustarea ofertă→tranzacție o pune evaluatorul.", options: {} }],
  { x: MX + 0.4, y: 4.92, w: 11.3, h: 1.2, fontFace: BF, fontSize: 13, color: "C7D2E2", margin: 0, valign: "top", lineSpacingMultiple: 1.04 });
footer(s, 8);

// ════════════════ SLIDE 9 — REZULTATUL ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Rezultatul", "Raportul Word generat");
const secs = ["Copertă + scrisoare de transmitere", "Declarație de conformitate și certificare", "Termeni de referință (SEV 101)", "7 capitole de analiză + grilele de calcul (SEV 106)", "Drept evaluat, sarcini CF, utilități, regim urbanistic", "Alocarea valorii + riscul garanției (GEV 520)", "Anexe: surse comparabile + fotografii + casetă semnătură"];
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: 1.85, w: 7.2, h: 4.4, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
s.addText(secs.map((t, k) => ({ text: t, options: { bullet: { code: "2713", indent: 18 }, breakLine: true, paraSpaceAfter: k < secs.length - 1 ? 9 : 0 } })),
  { x: MX + 0.4, y: 2.15, w: 6.5, h: 3.8, fontFace: BF, fontSize: 13.5, color: INKTX, margin: 0, valign: "top" });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX + 7.55, y: 1.85, w: 4.55, h: 4.4, rectRadius: 0.08, fill: { color: ICE } });
s.addText("Anexa foto", { x: MX + 7.85, y: 2.15, w: 4.0, h: 0.4, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
s.addText("Pozele intră direct în raport.", { x: MX + 7.85, y: 2.6, w: 4.0, h: 0.5, fontFace: BF, fontSize: 13, color: INKTX, margin: 0 });
s.addShape(pres.shapes.LINE, { x: MX + 7.85, y: 3.3, w: 3.9, h: 0, line: { color: "C2CEDF", width: 1 } });
s.addText("Text redactat cu AI", { x: MX + 7.85, y: 3.5, w: 4.0, h: 0.4, fontFace: HF, fontSize: 16, bold: true, color: NAVY, margin: 0 });
s.addText("Textul de analiză e scris pe baza cifrelor deterministe — evaluatorul revizuiește și își asumă.",
  { x: MX + 7.85, y: 3.95, w: 4.0, h: 1.6, fontFace: BF, fontSize: 13, color: INKTX, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });
footer(s, 9);

// ════════════════ SLIDE 10 — CONFIDENȚIALITATE ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Confidențialitate (GDPR)", "Datele personale nu ajung la AI");
const flow = [["Date reale", "Nume, adresă, cadastral, CF, evaluator", NAVY], ["Anonimizare", "Înlocuite cu marcaje: [CLIENT], [ADRESA]…", NAVY], ["AI", "Primește DOAR text anonimizat", NAVY], ["Demascare locală", "Numele reale revin pe calculator", NAVY]];
flow.forEach((f, i) => {
  const x = MX + i * 3.06;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.35, w: 2.7, h: 2.3, rectRadius: 0.09, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x, y: 2.35, w: 2.7, h: 0.12, fill: { color: f[2] } });
  s.addText(String(i + 1), { x: x + 0.2, y: 2.6, w: 0.7, h: 0.6, fontFace: HF, fontSize: 30, bold: true, color: f[2], margin: 0 });
  s.addText(f[0], { x: x + 0.25, y: 3.25, w: 2.3, h: 0.5, fontFace: HF, fontSize: 15.5, bold: true, color: NAVY, margin: 0, valign: "top" });
  s.addText(f[1], { x: x + 0.25, y: 3.75, w: 2.3, h: 0.85, fontFace: BF, fontSize: 11.5, color: INKTX, margin: 0, valign: "top", lineSpacingMultiple: 1.03 });
  if (i < 3) s.addText("→", { x: x + 2.62, y: 2.35, w: 0.5, h: 2.3, align: "center", valign: "middle", fontFace: BF, fontSize: 22, bold: true, color: GOLD, margin: 0 });
});
s.addText("Restul calculelor și generarea documentului se fac integral pe calculatorul evaluatorului. CNP/telefon/e-mail scăpat e prins de o plasă suplimentară înainte de AI.",
  { x: MX, y: 5.3, w: 12.1, h: 0.7, fontFace: BF, fontSize: 13, italic: true, align: "center", color: SLATE, margin: 0, lineSpacingMultiple: 1.05 });
footer(s, 10);

// ════════════════ SLIDE 11 — ONESTITATE ════════════════
s = pres.addSlide(); s.background = { color: PAPER }; head(s, "Onestitate", "Ce mai e de făcut");
const lim = [
  ["Surse de date oficiale", "Catalog IROVAL (costuri unitare), BIG, ANCPI — necesită acces / membru ANEVAR."],
  ["Liste AML live", "Sancțiuni UE/ONU, PEP — momentan injectabile, de reîmprospătat din surse oficiale."],
  ["Calibrare metodologică", "Pragurile și regulile de selecție se confirmă de un evaluator senior."],
  ["Validare juridică", "Textele AML/GDPR și semnătura digitală a .exe — de confirmat cu juristul."],
];
lim.forEach((l, i) => {
  const y = 1.95 + i * 1.12;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y, w: 12.1, h: 0.98, rectRadius: 0.06, fill: { color: WHITE }, line: { color: "E2E6EC", width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x: MX, y, w: 0.12, h: 0.98, fill: { color: GOLD } });
  s.addText(l[0], { x: MX + 0.4, y: y + 0.05, w: 3.7, h: 0.88, fontFace: HF, fontSize: 15, bold: true, color: NAVY, margin: 0, valign: "middle" });
  s.addText(l[1], { x: MX + 4.2, y: y + 0.05, w: 7.7, h: 0.88, fontFace: BF, fontSize: 13, color: INKTX, margin: 0, valign: "middle", lineSpacingMultiple: 1.03 });
});
s.addText("Aplicația AVERTIZEAZĂ, nu decide — limitările sunt declarate deschis, nu ascunse.",
  { x: MX, y: 6.5, w: 12.1, h: 0.4, fontFace: BF, fontSize: 13, italic: true, align: "center", color: SLATE, margin: 0 });
footer(s, 11);

// ════════════════ SLIDE 12 — CE FEEDBACK CAUT (concluzie) ════════════════
s = pres.addSlide(); s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.16, fill: { color: GOLD } });
s.addShape(pres.shapes.RECTANGLE, { x: MX, y: 0.62, w: 0.17, h: 0.17, fill: { color: GOLD } });
s.addText("CE FEEDBACK CAUT", { x: MX + 0.28, y: 0.56, w: 11, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: GOLD, charSpacing: 3, margin: 0, valign: "middle" });
s.addText("Întrebări pentru tine", { x: MX, y: 0.92, w: 12, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: WHITE, margin: 0 });
const qs = [
  "Metodologia terenului (două etape, selecție pe ajustare brută minimă, fără ofertă) — corectă?",
  "Metodologia casei (preț total, arie utilă ca ajustare valorică) și regula de selecție — corecte?",
  "Abordarea prin venit (capitalizare directă + DCF) și grila de chirii — în regulă?",
  "Reconcilierea și alocarea (construcții = proprietate − teren) — în regulă pentru garantare?",
  "Raportul (declarații, termeni, GEV 520, anexe) — complet și acceptabil pentru bănci?",
  "Orice ar face raportul respins sau ar trebui adăugat.",
];
qs.forEach((q, i) => {
  const y = 1.95 + i * 0.72;
  numCircle(s, MX, y, i + 1, 0.5, GOLD);   // tot auriu: pe fundal navy, cercurile navy erau invizibile
  s.addText(q, { x: MX + 0.72, y, w: 11.3, h: 0.5, fontFace: BF, fontSize: 14.5, color: "E6ECF5", margin: 0, valign: "middle", lineSpacingMultiple: 1.0 });
});
s.addShape(pres.shapes.LINE, { x: MX, y: 6.4, w: 12.1, h: 0, line: { color: "33476A", width: 1 } });
s.addText([{ text: "Orice observație, chiar și «așa nu se face», e exact ce caut. ", options: { color: WHITE, bold: true } }, { text: "Mulțumesc pentru timp.", options: { color: GOLD, italic: true } }],
  { x: MX, y: 6.5, w: 12.1, h: 0.45, fontFace: BF, fontSize: 14, margin: 0, valign: "middle" });

const out = path.resolve(__dirname, "..", "..", "docs", "prezentare-aplicatie.pptx");
pres.writeFile({ fileName: out }).then(() => console.log("Deck scris:", out));
