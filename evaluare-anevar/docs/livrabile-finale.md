# Livrabile finale — registru pe criterii

> Inventar al lucrurilor care se **livrează cuiva**, organizat pe mai multe criterii (destinatar, stare,
> poartă de lansare, format). Artefactele tehnice sunt deja construite; ce te oprește e validarea umană +
> câteva decizii. Owner: **A**=eu (cod, gata) · **B**=evaluator senior · **C**=jurist · **🧑**=decizie Adi.
> Actualizat: 2026-06-07.

## 0. Tabel master — toate livrabilele
| # | Livrabil | Format | Cui | Scop | Stare | Owner | Locație |
|---|----------|--------|-----|------|-------|-------|---------|
| 1 | **Aplicația** (executabil) | `.exe` 48 MB | toți | produsul | ✅ gata | A | `dist/evaluare-anevar.exe` |
| 2 | **Pachet feedback** | `.zip` 48 MB | testeri / 5 evaluatori | încercare + feedback | ✅ gata | A | `packaging/evaluare-anevar-feedback.zip` |
| 3 | **Pachet evaluator (exe + cheie AI)** | folder (`.exe`+`.env`) | evaluator cu AI | uz cu narativ AI | ✅ gata (proces scris) | A/🧑 | `distributie-evaluator.md` + `.env.example` |
| 4 | **Extensie browser** | `manifest.json`+`content.js` | evaluator | import anunțuri din portal | ✅ gata | A | `extensie-browser/` |
| 5 | **Raport demo Breaza** | `.docx` 54 KB | evaluator + bancă | exemplu output (anonimizat) | ✅ regenerat azi | A | `docs/exemplu-raport-breaza.docx` |
| 6 | **Prezentarea aplicației** | `.pptx` 12 slide | evaluator / stakeholderi | explică produsul | ✅ refăcut azi | A | `docs/prezentare-aplicatie.pptx` |
| 7 | **Protocol peer-review** | `.md` | 2–3 evaluatori seniori | validează metodologia | ✅ text gata | A scrie / B validează | `docs/protocol-peer-review-evaluator.md` |
| 8 | **Audit AML pentru jurist** | `.md` | jurist AML | **blocant absolut** | ✅ text gata | C | `docs/audit-aml-pentru-jurist.md` |
| 9 | **Pachet juridic (5 drafturi)** | `.md` DRAFT | jurist | T&C, confidențialitate, EULA, DPA, disclaimer | ✅ DRAFT | C | `docs/legal/10..14` + `00-evaluare-juridica-RO` |
| 10 | **Pachet GDPR (2 modele)** | `.md` MODEL | jurist GDPR | consimțământ + politică prelucrare | ✅ MODEL | C | `docs/gdpr/` |
| 11 | **Pachet validare bănci** | scrisoare `.md` + raport demo | 2–3 bănci (Risc/garanții) | validare formă raport | ✅ gata | C/🧑 trimite | `docs/pachet-validare-banci.md` + #5 |
| 12 | **Instrucțiuni evaluator / CITEȘTE-MĂ** | `.md` / `.txt` | evaluator / tester | cum pornește + ce testează | ✅ gata | A | `docs/instructiuni-evaluator.md` + zip |
| 13 | **Conformitate + audit (suport)** | `.md` | validatori / Adi | dovada conformității SEV 2025 + hardening | ✅ gata | A | `docs/conformitate/`, `docs/audit-final/`, `docs/adr/` |
| 14 | **Sinteze + plan de lansare (decizie)** | `.md` | **Adi** | ce decizi / pe cine trimiți | ✅ gata | 🧑 | `00-SINTEZA-lansare`, `plan-lansare-piata`, `BLOCAT-pe-Adi` |

## 1. Pe DESTINATAR (cui livrezi)
- **Tester / 5 evaluatori (feedback informal):** #2 pachet feedback (sau #3 cu cheie AI) · #12 instrucțiuni.
- **Evaluator senior (peer-review metodologic):** #5 raport demo · #6 prezentare · #7 protocol · (opțional #1 exe).
- **Jurist AML:** #8 audit AML *(BLOCANT)* · #9 (partea AML).
- **Jurist GDPR:** #9 + #10 (DPA, transfer LLM extra-UE, AI Act).
- **Bănci (Risc/IT):** #11 scrisoare + #5 raport demo anonimizat → (pilot 20–30 dosare *după* metodologie).
- **Asigurător răspundere ANEVAR:** [`cerere-aviz-asigurator.md`](cerere-aviz-asigurator.md) — „rapoarte asistate AI sunt acoperite" ✅ redactat (șablon).
- **Adi (decizii):** #14 + #13.

## 2. Pe STARE de pregătire
- ✅ **Gata de livrat ACUM (Bucket A, fără blocaje):** #1, #2, #3, #4, #5, #6, #12, #13 — și #7/#8/#9/#10/#11 ca **drafturi de trimis** (validarea o face terțul).
- ⏳ **Se finalizează DUPĂ validare externă:** metodologia (B, din #7) · textele AML/GDPR (C, din #8–#10) · forma pt bănci (#11).
- ⛔ **Blocat pe tine (🧑):** vezi `BLOCAT-pe-Adi §J` — code-signing, lock identitate la finalizare, criptare-la-repaus, preț.
- ✅ **Create (2026-06-07):** [`manual-utilizare.md`](manual-utilizare.md) · [`SLA-suport.md`](SLA-suport.md) · [`plan-incident-breach.md`](plan-incident-breach.md) · [`cerere-aviz-asigurator.md`](cerere-aviz-asigurator.md) · **etichetarea „AI (proză) vs determinist (toate numerele)" în raport** (în Termeni de referință, cu test). *(Drafturile juridice rămân de validat de jurist.)*

## 3. Pe POARTĂ de lansare (din planul de lansare)
- **Poarta 0 — validări externe (drumul critic, pornesc în paralel):** #7 (evaluatori) · #8 (jurist AML) · #9+#10 (jurist GDPR) · #11 (bănci) · aviz asigurător.
- **Poarta 1 — garduri conformitate (le fac eu / tu cumperi):** checkpoint asumare (✅ făcut azi-noapte) · kill-switch versiune · **code-signing 🧑** · RTS/RTN off by default.
- **Poarta 2 — aplici ce decid experții:** răspunsuri evaluatori (B) + juriști (C) → le implementez eu.
- **Poarta 3 — comercializare:** validează cu 5 evaluatori reali ÎNAINTE de gateway/Stripe.

## 4. Pe FORMAT (gata vs de pregătit pentru livrare)
- ✅ **Format final:** #1 `.exe` · #2 `.zip` · #5 `.docx` · #6 `.pptx`.
- 📄 **De convertit `.md` → PDF** pentru livrare profesională la **jurist/bancă** (#7–#11): un PDF curat arată serios; pot genera PDF-urile la cerere.
- 🔒 **Lipsește semnătura digitală** pe `.exe` (#1) → SmartScreen avertizează; necesită certificat (🧑).

## 5. Ce aș face EU în continuare (sigur, fără să te blochez)
1. Convertesc pachetele de trimis (#7–#11) în **PDF** curat, gata de atașat la e-mail.
2. ✅ **FĂCUT (2026-06-07):** drafturile lipsă — manual de utilizare, SLA suport, plan incident/breach, cerere de aviz asigurător.
3. ✅ **FĂCUT (2026-06-07):** etichetarea „AI (proză) vs determinist (toate numerele)" în raport (Termeni de referință + test).
> Toate sunt Bucket A. Restul (cumpărare cert, pe cine trimiți, preț) sunt deciziile tale din `BLOCAT-pe-Adi`.
> Rămas din lista mea: **#1 conversia pachetelor în PDF** (la cerere).
