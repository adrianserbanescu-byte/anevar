# F — Conformitate AML: Legea 129/2019 + Normele ONPCSB (Ordin 37/2021) vs. modulul `aml/`

> Re-analiză de conformitate pe textul **integral** al celor două acte:
> `md files/LEGE nr.md` (Legea nr. 129/2019, M.Of.) + `md files/NORME din 2 martie 2021…md`
> (Norme ONPCSB de aplicare, aprobate prin Ordinul 37/2021, M.Of. 240/09.03.2021).
> Comparat cu `src/evaluare/aml/` (constante, models, incadrare, risc, indicatori, raportare, documente, store, liste, serviciu).
> **Bucket:** **A**=cod (eu) · **B**=evaluator (praguri/metodologie de afaceri) · **C**=jurist (validare juridică, escaladare).
> ⚠️ **AML = bucket C.** Acest fișier NU modifică cod — doar inventariază și escaladează. Actualizat: 2026-06-06.
> Legendă status: ✅ acoperit · 🟡 parțial · ❌ lipsește.

## Verdict general
Modulul `aml/` este **bine ancorat legal și în mare conformă** pentru profilul „evaluator autorizat = entitate raportoare”.
**Pragurile-cheie sunt CORECTE** (10.000 € numerar, 15.000 € ocazional/anti-fragmentare, 1.000 € transfer fonduri, 25%+1 beneficiar real,
3 zile lucrătoare RTN, 24h suspendare, 5 ani retenție, 12 luni post-PEP). Îngrijorarea din `audit-aml-pentru-jurist.md` privind un
prag de **3.000 €** pentru tranzacții ocazionale **NU se confirmă** în Legea 129/2019 (vezi „Diferențe noi”, pct. 1).
Golurile reale sunt: (a) **monitorizarea continuă** a relației (cod = evaluare one-shot), (b) **obligația GDPR de informare** a clientului
înainte de relație (art. 22(2)), (c) **ștergerea datelor** la expirarea retenției (art. 21(4)), (d) **coborârea pragului de 25%** la risc sporit
(Norme art. 16(4)(e)), (e) o **eroare de citare** în disclaimer (art. 33 ≠ sancțiuni; corect art. 43/44/49).

---

## Tabel de conformitate

| # | Cerință (LEGE / NORME ref) | Status | Unde (cod `aml/`) | Diferență / gol + recomandare | Bucket |
|---|----------------------------|--------|-------------------|-------------------------------|--------|
| 1 | **Evaluatorul = entitate raportoare.** Persoane care prestează servicii/comercializează bunuri cu tranzacții numerar ≥ 10.000 € intră sub incidență (L. art. 5(1)(i); profesiile liberale ce participă „în orice operațiune… vizând bunuri imobile” — art. 5(1)(f)) | ✅ | întreg modulul; `audit-aml-pentru-jurist.md` §1 | Încadrarea evaluatorului la 5(1)(i) (și posibil 5(1)(f) când participă la operațiuni imobiliare) — **de confirmat de jurist care literă se aplică**, fiindcă atrage regimuri ușor diferite (ex. 5(1)(i) e exceptat de persoană desemnată, 5(1)(f) nu). | **C** |
| 2 | **KYC standard** (identificare + verificare client; beneficiar real; scop/natură relație; monitorizare continuă) — L. art. 11(1)(a–d); N. art. 16(1) | 🟡 | `models.py` (PF/PJ/BR), `documente.genereaza_fisa_kyc` | Câmpurile a–c acoperite. **Lit. (d) „monitorizarea continuă… pe toată durata relației” NU e modelată** (evaluare one-shot). Recomandare: documentat ca limitare; monitorizarea = sarcină a evaluatorului. | **C** (+B) |
| 3 | **KYC verificat ÎNAINTE de tranzacție / relație** — L. art. 11(8) | 🟡 | `serviciu.evalueaza_relatie` | Codul nu impune secvențierea temporală (verificare → tranzacție). E proces de afaceri; de notat în norme interne. | **C** |
| 4 | **Imposibilitatea aplicării KYC ⇒ nu se inițiază/continuă + RTS** — L. art. 11(9); N. art. 19(1) | 🟡 | `indicatori.propune_rts`, `documente.genereaza_rts` | RTS se propune din indicatori, dar **nu există branch explicit „KYC incomplet ⇒ refuz + RTS”**. Recomandare: indicator dedicat „client refuză identificarea / date neactualizate” (cf. art. 6(1)(d)). | **C** |
| 5 | **Beneficiar real, definiție + prag 25%+1 acțiune** — L. art. 4(2)(a)(1), (d) | ✅ | `constante.PRAG_BENEFICIAR_REAL = 0.25`; `models.BeneficiarReal` | Corect. Acoperă și „senior management” ca fallback (art. 4(2)(a)(2)) prin `TipControlBR="senior_management"`. | — |
| 6 | **La risc sporit, pragul de 25% se POATE coborî** — N. art. 16(4)(e) | ❌ | `constante`, `risc.py` | Pragul e fix 0.25 indiferent de categorie. La „sporit”, norma cere coborârea pragului BR. Recomandare: la EDD, prompt evaluatorului să identifice BR sub 25%. | **C** (+A când se decide) |
| 7 | **Identificare: date PF (stare civilă/act), PJ (acte constitutive/CUI/reprezentant)** — L. art. 15(1); N. art. 18(1) | ✅ | `models.PersoanaFizica`, `ClientPJ` | Câmpuri prezente (CNP, tip_act, serie/nr, reprezentant_legal). | — |
| 8 | **PJ străină: traducere legalizată în română** — L. art. 15(2); N. art. 18 | ✅ | `models.ClientPJ.traducere_legalizata`; `documente` marchează „NU — necesară (art. 15(2))” | Corect, inclusiv avertismentul în fișa KYC. | — |
| 9 | **Măsuri simplificate doar la risc redus** — L. art. 16(1)(2); N. art. 16(2) | ✅ | `risc.nivel_masuri` (redus→simplificate) | Mapare corectă. Factorii de risc redus (art. 16(2)) reflectați în `Semnale` (țară risc redus, client cunoscut, canal față-în-față). | — |
| 10 | **Măsuri suplimentare (EDD) la risc sporit; PEP; țări risc înalt; tranzacții complexe; relație la distanță** — L. art. 17(1)(2); N. art. 16(4) | ✅ (reguli HARD) | `risc.evalueaza_risc` (reguli HARD → „sporit”) | Regulile HARD forțează „sporit” corect. **Dar sub-obligațiile EDD din art. 17(9) (aprobare conducere superioară, sursa averii/fondurilor, monitorizare sporită) NU sunt enumerate** în output. Recomandare: checklist EDD în documentul de risc. | **C** |
| 11 | **PEP: definiție (funcții a–h), familie, asociați; relevant ≥ 12 luni după încetare** — L. art. 3(2)(4)(5)(6); art. 17(1)(c) | ✅ | `models.CategoriePEP/TipPEP/StatutPEP`; `risc.pep_efectiv`; `constante.PERIOADA_POST_PEP_LUNI = 12` | Corect. Cele 8 categorii (a–h) mapate 1:1; logica „titular activ sau în primele 12 luni” corectă (`_luni_intre`). | — |
| 12 | **Screening sancțiuni internaționale** (verificabil pe onpcsb.ro, secț. „sancțiuni internaționale”) + demonstrarea îndeplinirii — N. art. 17(i) | 🟡 | `liste.py`, `serviciu._nume_screening` | Norma cere **verificare pe surse oficiale + dovada** — NU impune explicit API live. Abordarea (liste injectabile + „posibilă potrivire, verifică manual”) e **admisibilă** dacă evaluatorul e dirijat către sursa oficială și se păstrează dovada. Recomandare jurist: confirmă că trimiterea către onpcsb.ro + bifă manuală satisface „demonstrarea concretă”. | **C** |
| 13 | **RTS — raport tranzacții suspecte, exclusiv la Oficiu, „de îndată”, înainte de tranzacție** — L. art. 6(1)(2), art. 8(1); N. art. 19(1)(2) | ✅ | `raportare.RaportRTS`, `documente.genereaza_rts`, `indicatori.propune_rts` | Conținut + flux corecte. RTS indiferent de prag/risc (N. art. 19(2)) reflectat. | — |
| 14 | **RTN — raport tranzacții numerar ≥ 10.000 €, în 3 zile lucrătoare, indiferent de justificare** — L. art. 7(1)(7); N. art. 20(1)(3) | ✅ | `constante.PRAG_NUMERAR_EUR=10000`, `TERMEN_RTN_ZILE_LUCRATOARE=3`; `raportare.necesita_rtn`, `termen_rtn` | Corect, inclusiv calculul zilelor lucrătoare. | — |
| 15 | **Anti-fragmentare: tranșe < 15.000 € cu elemente comune** — L. art. 7(4); N. art. 20(2) | ✅ | `constante.PRAG_ANTIFRAGMENTARE_EUR=15000`; `raportare.tranzactii_legate` | Corect. „Termenul în care elementele comune prezintă relevanță” = parametrizabil (`fereastra_zile=30`) — de stabilit în normele interne (art. 7(4) cere acest scenariu documentat). | **B/C** |
| 16 | **Conversie EUR↔LEI la cursul BNR din ziua tranzacției** — N. art. 21(2) | ✅ | `raportare.eur_din_lei/lei_din_eur` | Corect (comentariu cod citează N. art. 21(2)). | — |
| 17 | **Suspendarea tranzacției 24h după înregistrare RTS; prorogare dacă expiră nelucrătoare** — L. art. 8(3)(10) | ✅ | `constante.SUSPENDARE_ORE=24`; `raportare.suspendare_pana_la` | Corect. **Atenție conceptuală:** art. 8(4) (Oficiul → 48h) și art. 8(6) (Parchet → +72h) sunt acțiuni ale autorităților, NU obligații ale evaluatorului — corect că nu sunt modelate. | — |
| 18 | **Format/transmitere rapoarte = doar electronic, prin canalele Oficiului (ordin președinte)** — L. art. 8(11)(12) | 🟡 | `documente` (drafturi .docx) + text „rapoarte.onpcsb.ro” | Aplicația **pregătește conținutul**; transmiterea efectivă în formatul ONPCSB o face evaluatorul pe portal. Corect ca scop, dar de evidențiat că .docx ≠ format oficial de transmitere. | **C** |
| 19 | **Persoană desemnată — obligatorie, MAI PUȚIN PF și entități art. 5(1)(i)** — L. art. 23(1)(4); N. art. 5, **art. 7** | ✅ | `incadrare.necesita_persoana_desemnata`; `documente.genereaza_decizie_desemnare` (refuză pt. PFA) | Corect: N. art. 7 scutește explicit PF/PFA. **Dar dacă evaluatorul e încadrat la 5(1)(f) (nu (i)), excepția art. 23(4) NU se aplică** → leagă de pct. 1. De clarificat de jurist. | **C** |
| 20 | **Persoana desemnată: testare competență + reluare la modificări legislative; cazier/reputație** — N. art. 5(4)(b), (6), (7) | 🟡 | `documente.genereaza_decizie_desemnare` (atribuții) | Decizia listează atribuții, dar **nu surprinde testarea/competența/cazierul** cerute de N. art. 5. Recomandare: secțiune „selecție și testare” în decizie. | **C** |
| 21 | **Norme interne — conținut minim (7 documente a–g)** — L. art. 24(1)(a–e); N. **art. 8(1)(a–g)** | ✅ | `documente._CAPITOLE_NORME` (7 capitole) + `genereaza_norme_interne` | Cele 7 capitole mapează 1:1 pe N. art. 8(1)(a–g) (raportare/păstrare, KYC, administrare riscuri, control intern, protecție personal, whistleblowing, instruire). Superset corect al art. 24(1). Necesită adaptare la entitate (corect semnalat ca draft). | — |
| 22 | **Aprobare + monitorizare norme la nivelul conducerii de rang superior; revizuire** — L. art. 24(3); N. art. 8(5) | ✅ | `documente._antet` (clauză „Aprobat… conducere de rang superior… se revizuiește”) | Clauza prezentă în antet. | — |
| 23 | **Audit independent dacă se depășesc ≥ 2 din 3 praguri (16M active / 32M CA / 50 salariați)** — L. art. 24(2); N. **art. 9** | ✅ | `incadrare.necesita_audit_independent`; `constante.PRAG_AUDIT_*` | Corect, inclusiv „ultimul exercițiu financiar încheiat” și comparația strictă „depășesc”. | — |
| 24 | **Instruire periodică + evaluare angajați; programe de recunoaștere SB/FT** — L. art. 24(4)(5); N. art. 8(1)(g), art. 10–11 | 🟡 | `documente._CAPITOLE_NORME` cap. 7 | Acoperit ca **politică** în norme, dar fără artefact de evidență a instruirii (registru/atestate). Pentru PFA solo, relevanța e redusă. Recomandare: notă în norme. | **C** |
| 25 | **Evaluarea de risc (factori client/produs/canal/geografic, ponderare, categorisire, reevaluare periodică)** — L. art. 25; N. art. 12–14 | ✅ | `risc.evalueaza_risc`, `models.EvaluareRisc/FactorRisc` | Cei 4 factori + ponderi + scor + categorie + `data_reevaluare`. Conform N. art. 13(c–e). | — |
| 26 | **Reevaluare/monitorizare periodică pe parcursul relației** — N. art. 12(3), 13(f)(g), 16(2)(d) | 🟡 | `risc._LUNI_REEVALUARE` → `data_reevaluare` | Codul **calculează** data reevaluării, dar **nu există flux de re-rulare/alertă** (one-shot). Recomandare: documentat ca responsabilitate a evaluatorului; eventual reminder. | **C** (+A) |
| 27 | **Indicatori de suspiciune specifici evaluării (cei 10)** — HCD 58/2023 art. 6(10); flux RTS — L. art. 6 | ✅ | `indicatori.INDICATORI` (10), `SemnaleIndicatori`, `propune_rts` | Cei 10 indicatori reproduși; orice indicator activ → propunere RTS. Sursă = HCD 58 (deja analizat în `hcd-58-instructiuni-oncpsb.md`). | — |
| 28 | **Identificarea BR prin Registrul central (ONRC/MJ/ANAF); evidența măsurilor** — L. art. 19(1)(4)(10) | 🟡 | `models.BeneficiarReal.consultat_registru_central`, `neconcordanta_registru` | Există doar **flag-uri** (bifă „consultat” + „neconcordanță”), fără integrare ONRC. Norma cere ca entitatea „să se bazeze pe registrul central” + raportarea neconcordanțelor. Recomandare: confirmă jurist dacă bifa + dovadă atașată e suficientă. | **C** |
| 29 | **Păstrare evidențe 5 ani de la încetarea relației / tranzacția ocazională; prelungire max. 5 ani** — L. art. 21(1)(2)(3); N. art. 22(2)(3) | ✅ | `constante.RETENTIE_ANI=5`, `RETENTIE_PRELUNGIRE_MAX_ANI=5`; `store.StoreAML` (calc. `data_retentie`) | Corect ca durată. Store separat, append-only. | — |
| 30 | **Ștergerea datelor cu caracter personal la expirarea retenției** — L. art. 21(4) | ❌ | `store.py` | Store-ul **calculează** `data_retentie` dar **NU implementează ștergerea** la expirare (append-only, fără purge). Recomandare: rutină de ștergere/anonimizare la expirare (sau procedură manuală documentată). | **C** (+A) |
| 31 | **Prelucrare date doar în scop AML; informare client ÎNAINTE de relație (GDPR)** — L. art. 22(1)(2)(3) | ❌ | — (lipsește) | **NU există notă de informare GDPR** către client (identitate operator, scop, destinatari, drepturi acces/rectificare) cerută de art. 22(2). Recomandare: șablon „informare prelucrare date AML” generat odată cu fișa KYC. | **C** (+A) |
| 32 | **Interdicția divulgării (tipping-off)** — L. art. 38(1)(2) | ✅ | `raportare._AVERTISMENT_TIPPING_OFF`, `RaportRTS`, `store` separat | Corect: avertisment vizibil în RTS, stocare separată de dosar. Excepțiile art. 38(3) (grup, aceeași profesie) irelevante pentru evaluator solo. | — |
| 33 | **Confidențialitate; răspundere; sancțiuni** — L. art. 33 (info la cerere, 15 zile), **art. 43–44** (contravenții: PF 25.000–150.000 lei + complementare), **art. 49** (infracțiune SB, 3–10 ani) | 🟡 | `documente._antet` (disclaimer) | **EROARE DE CITARE:** disclaimerul spune „art. 33 prevede sancțiuni (inclusiv penale)”. **Art. 33 este despre solicitări de informații (răspuns în 15 zile), NU sancțiuni.** Corect: contravenții = **art. 43** (PF amenzi 25.000–150.000 lei) + **art. 44** (sancțiuni complementare: suspendare autorizație, declarație publică etc.), infracțiunea de spălare = **art. 49**. Recomandare: corectează referința în disclaimer. (Aceeași greșeală apare și în `audit-aml-pentru-jurist.md` §3 pct. 4 și §3 pct. 3.) | **C** (+A: simplă corectare text) |
| 34 | **Răspuns la solicitări Oficiu în 15 zile (sistem care permite identificarea relațiilor pe 5 ani)** — L. art. 33(2)(3); N. art. 23 | 🟡 | `store.StoreAML.listeaza/citeste` | Store-ul permite regăsirea, dar nu există un flux „răspuns la cerere Oficiu”. Acceptabil pentru scop; de notat. | **C** |

---

## Diferențe noi față de ce aveam (vs. `audit-aml-pentru-jurist.md`)

1. **Pragul de 3.000 € pentru tranzacții ocazionale — INFIRMAT.** Întrebarea deschisă #1 din `audit-aml-pentru-jurist.md`
   („pragul ar putea fi 3.000 €”) **nu are temei** în Legea 129/2019. Textul integral confirmă: tranzacții ocazionale generale
   **15.000 €** (art. 13(1)(b)(1)), transfer de fonduri **1.000 €** (art. 13(1)(b)(2)), comercianți bunuri/servicii în numerar
   **10.000 €** (art. 5(1)(i) + art. 13(1)(c)). Evaluatorul folosește corect 10.000 € numerar și 15.000 € pentru KYC ocazional.
   **Recomandare: închide întrebarea #1 — pragurile din cod sunt corecte.**
2. **Eroare de citare a sancțiunilor (art. 33 → corect art. 43/44/49)** — nedetectată în auditul anterior. Vezi rândul 33.
3. **Obligația GDPR de informare prealabilă a clientului (art. 22(2))** — **complet absentă** din cod și din auditul anterior.
   Gol nou de conformitate (rândul 31).
4. **Ștergerea datelor la expirarea retenției (art. 21(4))** — auditul anterior trata doar *durata* (5 ani); **obligația de
   ștergere** efectivă nu era acoperită (rândul 30).
5. **Coborârea pragului BR de 25% la risc sporit (Norme art. 16(4)(e))** — cerință EDD nouă, neacoperită (rândul 6).
6. **Sub-obligațiile EDD pentru PEP (art. 17(9): aprobare conducere + sursa averii + monitorizare sporită)** — codul forțează
   corect „sporit”, dar nu enumeră aceste 3 acțiuni concrete (rândul 10).
7. **Confirmat OK (fără diferență):** persoană desemnată exceptată pentru PFA (N. art. 7), praguri audit 16M/32M/50 (N. art. 9),
   cele 7 capitole de norme interne (N. art. 8(1)(a–g)), 12 luni post-PEP (art. 3(6)/17(1)(c)) — toate exacte.

## Top 5 goluri AML (prioritizate, toate bucket C — escaladare la jurist)

1. **GDPR — informarea clientului înainte de relație (art. 22(2)).** ❌ Lipsește complet. Risc: contravenție art. 43(1)(a).
   → Șablon „notă de informare prelucrare date AML” + decizie jurist asupra conținutului minim.
2. **Ștergerea datelor la expirarea retenției (art. 21(4)).** ❌ Store-ul nu purjează. → Procedură (manuală sau automată) de
   ștergere/anonimizare la `data_retentie`; decizie jurist privind excepțiile (alte obligații legale de păstrare).
3. **Corectarea referinței de sancțiuni în disclaimer (art. 33 → art. 43/44/49).** 🟡 Eroare de citare în `documente.py` și
   `audit-aml-pentru-jurist.md`. → Corectură simplă de text, dar **necesită validare jurist** (AML = bucket C).
4. **Monitorizarea continuă + reevaluarea periodică a relației (art. 11(1)(d); N. art. 12(3), 13(f)(g)).** 🟡 Evaluare one-shot.
   → Clarificare jurist: cât revine aplicației vs. evaluatorului; eventual mecanism de reminder pe `data_reevaluare`.
5. **EDD incomplet la risc sporit: coborârea pragului BR sub 25% (N. art. 16(4)(e)) + sub-obligațiile PEP (art. 17(9)).** ❌/🟡
   → Checklist EDD în documentul de risc; decizie jurist asupra obligativității coborârii pragului BR pentru evaluator.

---

### Anexă — articole citate (verificate pe text integral)
**LEGEA 129/2019:** art. 3 (PEP, alin. 2 lit. a–h, alin. 6 = 12 luni) · art. 4 (beneficiar real, 25%+1) · art. 5(1)(f)(i) (entități
raportoare) · art. 6 (RTS) · art. 7(1)(4)(5)(7) (RTN 10.000 €, anti-fragmentare 15.000 €, transfer 2.000 € remitere, 3 zile lucr.) ·
art. 8(1)(3)(10)(11)(12) (suspendare 24h, transmitere electronică) · art. 11 (KYC standard, alin. 8 = înainte de tranzacție, alin. 9 = refuz+RTS) ·
art. 13(1)(b)(c) (praguri ocazional 15.000 €/transfer 1.000 €/numerar 10.000 €) · art. 15 (date identificare, alin. 2 = traducere legalizată) ·
art. 16 (măsuri simplificate) · art. 17(1)(2)(9)(14) (EDD, PEP, factori risc sporit) · art. 19 (registru BR) · art. 21 (retenție 5 ani, alin. 3 prelungire, alin. 4 ștergere) ·
art. 22 (prelucrare date + informare client) · art. 23(1)(4) (persoană desemnată, excepție PF/5(1)(i)) · art. 24(1)(2)(3) (norme interne, audit) ·
art. 33 (solicitări info, 15 zile) · art. 38 (tipping-off) · art. 43–44 (contravenții + complementare) · art. 49 (infracțiune SB, 3–10 ani).
**NORME (Ordin 37/2021):** art. 5 (persoană desemnată, testare) · art. 7 (excepție PFA) · art. 8(1)(a–g) (norme interne, 7 documente) ·
art. 9 (audit 16M/32M/50, 2 din 3) · art. 12–14 (evaluarea riscurilor) · art. 16 (măsuri standard/simplificate/suplimentare, alin. 4(e) = coborâre prag BR) ·
art. 17 (conținut KYC, lit. i = sancțiuni pe onpcsb.ro) · art. 18 (date identificare) · art. 19 (RTS de îndată) · art. 20 (RTN 10.000 €, 3 zile lucr.) ·
art. 21 (transmitere, curs BNR) · art. 22 (păstrare evidențe 5 ani).
