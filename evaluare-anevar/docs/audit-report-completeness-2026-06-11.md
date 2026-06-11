# Audit completitudine RAPORT de evaluare vs. GEV 520 (garantare credit) — 2026-06-11

> **Scop:** verificare READ-ONLY a generatorului de raport (`src/evaluare/report/generator.py`
> + `models/report_context.py`, `models/meta.py`, `models/property.py`, `assembler.py`,
> `ai/narrative.py`) — conține raportul .docx generat TOATE elementele cerute de un raport
> conform **GEV 520 „Evaluarea pentru garantarea împrumutului"** (ediția SEV 2025, în vigoare
> 1 iul 2025)? Persona: evaluator autorizat ANEVAR. Tip activ: casă + teren, garantare credit.
>
> **Surse normative consultate:** SEV 2025 (anevar.ro), GEV 520 ed. 2025 (ANAF user + Anexă
> nouă + ESG ca termen definit + referință SEV 340 EVIP / certificat energetic), plus doc-ul
> intern existent `docs/GEV520-2025-crosscheck.md` (confruntat și extins aici cu starea ACTUALĂ
> a codului din 2026-06-11).

---

## 0. Verdict de ansamblu

Scheletul raportului este **solid și bine peste medie** pentru un raport SEV/GEV: shell GBF complet
(copertă, scrisoare de transmitere, declarație de conformitate, termeni de referință, 7 capitole de
analiză, alocarea valorii, secțiune de risc GEV 520, anexe, semnătură) + checklist de conformitate
de 16 puncte + verificare de consistență cost↔piață + valoare de lichidare + condiționare BIG pe
`utilizator_desemnat`. **Elementele „de bază" cerute la garantare sunt prezente.**

Lipsurile rămase sunt concentrate în **noutățile normative GEV 520 ed. 2025** (ESG / riscuri fizice
/ certificat energetic – SEV 340; re-desemnarea utilizatorului; declarația de conflict de interese
tip EBA; recipisa BIG) și în **câteva câmpuri de model care există dar NU ajung în raport**
(`clasa_energetica`, `structura`, `finisaje`, `ac`). Niciuna nu blochează emiterea, dar mai multe
ar fi semnalate la **verificarea bancară** sau la un peer-review ANEVAR.

Elementele cerute explicit în brief, prezente azi: identificare + drepturi ✅; scop + client/banca ✅;
data evaluării + data raportului ✅; premise/ipoteze speciale ✅ (parțial, vezi F-08); inspecție ✅
(parțial, vezi F-05); descriere piață ✅ (narativ AI); cele 3 abordări cu justificare ✅; comparabile
+ ajustări + ofertă→tranzacție ✅; reconciliere ✅; HBU/CMBU ✅; valoarea finală + monedă + curs ✅
(dar **NU în litere** — vezi F-01); declarații conformitate + limitări + semnătură/legitimație ✅;
anexe (poze, comparabile, calcule) ✅.

---

## 1. Ce ESTE prezent (confirmat în cod)

| Element cerut (GEV 520 / SEV 106) | Unde, în `generator.py` | Stare |
|---|---|---|
| Identificare proprietate (adresă, cadastral, CF) | `_coperta` L181-182, `_termeni` L290-293, cap.1 L714, cap.4 | ✅ |
| Dreptul evaluat + act proprietate + sarcini/grevări CF | `_termeni` L294-301 (SEV 230) | ✅ |
| Scopul/utilizarea + client/destinatar (banca) | `_coperta` L188, `_scrisoare`, `_termeni` L275-278 | ✅ |
| Data evaluării + data raportului (+ data inspecției, valabilitate) | `_coperta` L194, `_termeni` L284-289 | ✅ |
| Tip valoare + SURSA definiției (SEV 102/IVS 104) | `_tip_valoare_txt` L110-128 | ✅ |
| Premise + ipoteză utilizare continuă + ipoteze speciale GEV 520 | `_termeni` L302-326 (A4-A5, A8) | ✅ |
| Independență / lipsă implicare materială (GEV 520 A3) | `_termeni` L312-319 | ✅ |
| Inspecție (dată, amploare, însoțitor, observații) | cap.4 L770-780 | ✅ (vezi F-05) |
| Descriere piață | cap.3 (narativ AI) | ✅ (vezi F-04) |
| Cele 3 abordări (piață/cost/venit/DCF) + justificare selecție | cap.6 L792-820, reconciliere cap.7 | ✅ |
| Grile comparabile + ajustări + ofertă→tranzacție | `_adauga_grila_*` L376-442, checklist L606 | ✅ |
| Reconcilierea valorilor | cap.7 L822-833 (+ `reconciled.nota`) | ✅ |
| CMBU / HBU | cap.5 L785-790 | ✅ |
| Valoarea finală + monedă + curs + echivalent LEI + fără TVA | `_coperta` L196-200, `_echiv_lei`, cap.7 | ✅ (dar NU în litere — F-01) |
| Declarații de conformitate (SEV 2025 + GEV + SEV 100) | `_declaratie_conformitate` L245-268 | ✅ |
| Limitări / restricții de utilizare | `_termeni` L351-355 | ✅ |
| Semnătură + legitimație evaluator | `_adauga_semnatura` L675-684 | ✅ |
| Anexe: comparabile (surse), foto, documente cadastrale/CF | `_adauga_anexe` L631-672 | ✅ |
| Alocarea valorii teren/construcții + verificare consistență | `_adauga_alocare` L476-511 | ✅ |
| Factorii A5 de performanță a garanției (a-d) | `_adauga_risc_garantie` L542-550 | ✅ |
| Valoarea de lichidare / vânzare forțată (factor evaluator) | L568-581 | ✅ |
| Înregistrare BIG condiționată pe utilizator (creditor/ANAF) | L555-567 + checklist | ✅ (corectează contradicția #23 din crosscheck) |
| Checklist de conformitate (16 puncte) | L594-612 | ✅ |
| Transparență instrument software + AI | `_termeni` L356-370 | ✅ |
| Disclaimer aplicație (draft, răspunderea = evaluator) | `_disclaimer_aplicatie` L78-88 | ✅ |

---

## 2. Ce LIPSEȘTE sau e INCOMPLET (priorizat)

Vezi findings structurate. Pe scurt:

**🔴 HIGH**
- **F-01** Valoarea finală **NU este redată în litere** (cuvinte) — uzanță fermă a rapoartelor de
  garantare și element așteptat la verificarea bancară.
- **F-02** **ESG / riscuri fizice** (GEV 520 §86-88, SEV 104 Anexa ESG) — secțiune nouă obligatorie
  în ed. 2025, complet absentă (doar o frază în termeni la L343).
- **F-03** **Certificat energetic / SEV 340 (EVIP)** — câmpul `clasa_energetica` există în model
  (`property.py:49`) dar NU se redă nicăieri; GEV 520 §88 cere analiza/menționarea lui.

**🟠 MEDIUM**
- **F-04** Capitolul „Prezentarea datelor de piață" = 100% text AI fără bază de tranzacții; la
  client=None devine simplu placeholder „[de completat]". Fără back-stop determinist.
- **F-05** Inspecția nu distinge **interior/exterior** și nu marchează explicit că a fost făcută de
  evaluatorul autorizat (GEV 520 §44 cere ambele).
- **F-06** **Re-desemnarea utilizatorului** (GEV 520 ed. 2025, novație): raport întocmit pentru alt
  scop NU e utilizabil la garantare fără re-desemnare + modificare BIG — absent din termeni/checklist.
- **F-07** **Declarație conflict de interese tip EBA** + **plata necondiționată** de acordarea
  creditului (GEV 520 §81-82) — distincte de declarația de independență; absente.
- **F-08** Câmpuri de model **nerandate** în descrierea fizică (cap.4): `structura`, `finisaje`,
  `ac` (arie construită la sol), `deschidere` teren — date introduse de evaluator dar pierdute în raport.

**🟡 LOW**
- **F-09** **Recipisa BIG** — checklistul spune „se înregistrează în BIG", dar GEV 520 §83-84 cere
  dovada scrisă (recipisa) atașată; formulare de întărit.
- **F-10** Anexa „calcule" — grilele și tabelul de cost apar în cap.6, nu ca anexă dedicată de calcul;
  lipsește o **Anexă cu desfășurătorul ajustărilor pe criterii** (doar pret corectat + ajustare brută
  totală sunt redate, nu ajustările individuale pe atribut).

---

## 3. Recomandare de prioritizare

1. **F-01** (valoarea în litere) — efort mic, impact mare la bancă. Quick win.
2. **F-08** (randare câmpuri existente) — efort mic, doar adăugare de paragrafe în cap.4.
3. **F-03 + F-02** (certificat energetic + ESG) — noutatea normativă 2025; o secțiune `_adauga_esg`
   pe profil GEV_520 + redarea `clasa_energetica`, cu disclaimerul de competență (§87).
4. **F-05, F-06, F-07, F-09** — întăriri de text/checklist, efort mic-mediu fiecare.
5. **F-04, F-10** — îmbunătățiri de fond (back-stop piață, desfășurător ajustări), efort mediu.

> Toate textele rămân *draft generat de aplicație*; conformitatea finală o validează și o asumă
> evaluatorul autorizat ANEVAR (conform disclaimerului existent din raport).
