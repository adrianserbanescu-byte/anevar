# Raport de conformitate — structura raportului .docx + stare SEV 2025

> Document de REVIEW pentru evaluatori. Note **factuale** extrase din cod + docuri de conformitate.
> Surse primare: `src/evaluare/report/generator.py` (structura .docx), `src/evaluare/ai/narrative.py`
> (split AI/determinist), `src/evaluare/models/{meta,property,results,report_context}.py`,
> `src/evaluare/profil.py`, `docs/conformitate/00-SINTEZA-conformitate.md` + `E-matrice-tip-scop.md`,
> `docs/audit-ui-nou/00-REVIEW-si-plan.md`. Citările de cod sunt pe versiunea de la data scrierii (2026-06-07).
> NB: numerotarea liniilor din SINTEZA (`l.505-542`) e ușor în urma codului actual; ancorele reale sunt funcțiile
> numite mai jos.

---

## 1. Structura raportului .docx (în ordinea generării)

Punctul de intrare: `genereaza_raport(ctx, output_path, adnotari=False)` (`generator.py:591-740`). Documentul
e construit liniar prin `python-docx` în următoarea ordine. Structura declarată = „shell GBF" + cele 7 capitole de
analiză raportate conform SEV 106.

### Front matter (shell GBF)

| # | Secțiune (titlu efectiv în .docx) | Funcție | Conținut |
|---|-----------------------------------|---------|----------|
| 1 | **RAPORT DE EVALUARE** (copertă, Heading 0) | `_coperta` (145-172) | Tip proprietate ("casă de locuit și teren aferent"), adresă, nr. cadastral + CF, client (nume+tip), proprietar (dacă diferă), beneficiar/finanțator, scop, evaluator (nume+legitimație ANEVAR), data evaluării + data raportului, **VALOAREA ESTIMATĂ** (valoare finală + monedă, echivalent LEI dacă moneda=EUR și există curs BNR, mențiune „fără TVA"). Page break la final. |
| 2 | **SCRISOARE DE TRANSMITERE** (Heading 1) | `_scrisoare_transmitere` (175-199) | Adresant (client / beneficiar), frază de transmitere cu adresă+scop+valoare de piață la data evaluării, paragraf de conformitate (SEV ediția 2025, HCN 2/2025, în vigoare 1 iulie 2025) + clauza de ghid GEV aplicabil (din profil), restricție de utilizare, formulă de încheiere semnată de evaluator. |
| 3 | **DECLARAȚIE DE CONFORMITATE ȘI CERTIFICARE** (Heading 1) | `_declaratie_conformitate` (215-233) | 6 afirmații standard ANEVAR ca listă cu buline: conformitate SEV 2025 + ghid GEV, fapte reale/corecte, limitarea prin ipoteze, absența interesului, onorariu necondiționat de valoare, calitatea de membru ANEVAR + asigurare RC profesională. **Certificarea e combinată în această secțiune** (titlu „...ȘI CERTIFICARE"); o certificare distinctă pe „Sinteză" apare și la cap. 1. |
| 4 | **TERMENI DE REFERINȚĂ AI EVALUĂRII** (Heading 1) | `_termeni_referinta` (236-320) | Cel mai bogat bloc de conformitate. Vezi detaliul de câmpuri în §2. Acoperă SEV 101 §20.1 (elementele termenilor de referință), SEV 102 (tip valoare+sursă), SEV 230 (drept + sarcini CF), și — condiționat de `ghid=="GEV_520"` — clauze de independență (GEV 520 A3 / SEV 101) și ipoteze speciale (GEV 520 A4-A5). |

### Cele 7 capitole de analiză (raportare SEV 106)

Generate inline în corpul `genereaza_raport` (608-729), fiecare ca Heading 1 numerotat:

| Cap. | Titlu | Sursă text | Conținut |
|------|-------|-----------|----------|
| 1 | **SINTEZA EVALUĂRII ȘI CERTIFICARE** | determinist | Recapitulare client, proprietate (cadastral/CF), scop, tip valoare (cu sursă), date, VALOAREA ESTIMATĂ + metoda selectată, „fără TVA". |
| 2 | **IPOTEZE GENERALE ȘI SPECIALE** | AI (fallback fix) | Narativ AI; fallback: „Ipoteze limitative standard privind structura de rezistență și solul." |
| 3 | **PREZENTAREA DATELOR DE PIAȚĂ** | AI (fallback fix) | Analiză descriptivă de piață (AI); fallback „[de completat]". **NU se bazează pe o bază de date de tranzacții reale.** |
| 4 | **DESCRIEREA JURIDICĂ ȘI FIZICĂ A PROPRIETĂȚII** | determinist + AI | Teren (suprafață, categorie; dacă agricol: categorie folosință + clasă calitate), acces (GEV 630 §28), utilități (§28), regim urbanistic/restricții POT-CUT (§16), construcție (Au/Acd/an referință), bloc condiționat apartament (etaj/nr. niveluri/an bloc/cotă teren indiviză), bloc industrial (înălțime liberă), **inspecția** (dată/amploare/însoțitor — GEV 630 §24/§44) + observații/neconcordanțe (§111.a.3). Opțional un paragraf narativ AI la final. |
| 5 | **ANALIZA CELEI MAI BUNE UTILIZĂRI (CMBU)** | AI (fallback fix) | Narativ AI; fallback „[de completat]". |
| 6 | **APLICAREA METODELOR DE CALCUL** | determinist (grile) + AI (justificare) | Paragraf-cadru SEV 103/105 (≈IVS 103/105) + **grilele de calcul** (vezi mai jos). La final, narativ AI „Justificarea ajustărilor aplicate" dacă există. |
| 7 | **RECONCILIEREA REZULTATELOR ȘI CONCLUZIA VALORII** | AI (fallback fix) + determinist | Narativ AI de reconciliere; fallback „[de completat]". Apoi rândul determinist: valoare finală + echivalent LEI + „fără TVA". |

**Grilele de calcul din cap. 6** (toate tabele `Table Grid`, numere deterministe):
- `_adauga_grila_comparatie` (326-354): grilă comparație directă pe preț total, 4 coloane (Comparabil / Preț total corectat / Ajustare brută % / Selectat DA), + valoarea prin comparație + notă de caracter indicativ al surselor. Dacă lipsește `market_result`/`comparables` → text „Abordarea prin piață nu a fost aplicată".
- `_adauga_grila_teren` (357-381): grilă teren EUR/mp, 4 coloane (cu etichetă de localizare), + formula `preț_mp_ales × suprafață = valoare teren`.
- `_adauga_tabel_cost` (384-409): tabel costuri segregate (abordarea prin cost), 5 coloane (Element / Cod IROVAL / Cantitate / Cost unitar / Cost de nou), + linia CIB / Vcp / depreciere fizică / CIN / valoare prin cost.
- Abordarea prin venit (capitalizare directă, Heading 2): dacă `venit_result` ≠ None — venit brut potențial, neocupare, cheltuieli, rată capitalizare, NOI, valoare = NOI/rată.
- Abordarea prin venit (DCF, Heading 2): dacă `dcf_valoare` ≠ None — valoarea prin actualizarea fluxurilor.

### Back matter (shell GBF)

| # | Secțiune | Funcție | Conținut |
|---|----------|---------|----------|
| 5 | **ALOCAREA VALORII** (Heading 1) | `_adauga_alocare` (415-450) | Tabel 2 coloane: valoarea proprietății, din care valoarea terenului, din care valoarea construcțiilor (alocată = proprietate − teren). **Verificare de consistență GEV 520**: dacă |CIN − valoare construcții alocată|/CIN > 20%, inserează un paragraf bold de avertizare (deprecierea implicită trebuie justificată, altfel poate fi semnalată la verificarea bancară). Apare doar dacă `alocare_constructii` ≠ None. |
| 6 | **RISCUL ASOCIAT GARANȚIEI (GEV 520)** (Heading 1) | `_adauga_risc_garantie` (453-519) | **Generată DOAR dacă `ctx.profil.ghid == "GEV_520"`** (gated în 733-734). Conține: narativ AI (fallback fix); cei 4 factori obligatorii GEV 520 A5 ca buline; aprecieri lichiditate/vandabilitate/perioadă de comercializare; mențiune înregistrare BIG; **valoarea de lichidare/vânzare forțată** = valoare piață × factor fix **0.85** (marcat explicit „orientativ", factor final 0.80–0.90 de stabilit de evaluator). Apoi sub-secțiune **CERTIFICAREA CONFORMITĂȚII RAPORTULUI (GEV 520)** — checklist de 16 puncte cu casete ☐ de bifat de evaluator (de aliniat la Anexa 1 a GEV 520). |
| 7 | **ANEXE** (Heading 1) | `_adauga_anexe` (536-573) | Anexa 1 — comparabile utilizate (surse: linkuri reale din anunțuri, sau „introduse manual"). Anexa 2 — planșe fotografice: embedează imaginile din `ctx.photos` (data-URL base64, decodate prin `_decode_foto`; imagini corupte sunt sărite; dacă 0 inserate → „[de atașat]"). Anexa 3 — documente cadastrale/extras CF/acte juridice: idem din `ctx.documente`. |
| 8 | **Casetă de semnătură** (fără heading) | `_adauga_semnatura` (576-585) | „Întocmit," + nume evaluator (bold) + „Evaluator autorizat ANEVAR, legitimația ..." + data raportului + „Semnătura / ștampila: ____". |

**Notă structurală:** scrisoarea de transmitere, declarația de conformitate și termenii de referință sunt în
front matter (înaintea capitolelor); riscul GEV 520, alocarea, anexele și semnătura sunt în back matter (după cap. 7).
Secțiunea de risc GEV 520 + certificarea ei sunt **condiționate de ghid**, deci absente din rapoartele care nu sunt
de garantare a creditului.

---

## 2. Câmpurile de conformitate rendate (cu sursă standard) + comportament la lipsă

Toate sunt produse de `_termeni_referinta` și cap. 4, din `EvaluationMeta` (`models/meta.py`) și `LandData`
(`models/property.py`). „Avertisment la lipsă" = textul exact emis când câmpul e gol.

| Câmp | Standard | Unde | Comportament la lipsă |
|------|----------|------|------------------------|
| **Tip valoare + sursă** | SEV 102 §20.4 + SEV 106 §30.6(i) | termeni + cap.1/7, via `_tip_valoare_txt` (92-101) | Slug cunoscut ("piata"→„valoare de piață (SEV 102 / IVS 104)"); frază care conține deja SEV/IVS/IFRS → neschimbată; altfel se adaugă „(conform SEV 102 — Tipuri ale valorii)". Implicit `meta.tip_valoare="Valoarea de piață (SEV 102)"`. |
| **Drept evaluat** | SEV 230 (§40.1) | termeni (259) | Implicit „drept de proprietate deplină (SEV 230)". Întotdeauna rendat. |
| **Sarcini / grevări (extras CF)** | SEV 230 §140 (critic la garantare) | termeni (262-266) | Dacă lipsesc → **avertisment**: „nu au fost declarate; de verificat în extrasul de carte funciară actualizat (relevant pentru garantare)." |
| **Act de proprietate** | GEV 630 §16 | termeni (260-261) | Opțional — rendat doar dacă există (`meta.act_proprietate`); altfel **omis tăcut** (fără avertisment). |
| **Inspecția: amploare / însoțitor / dată** | GEV 630 §24/§44 | cap. 4 (668-676) | Dacă niciunul nu e setat → **avertisment**: „amploarea și însoțitorul nu au fost declarate (de completat)." |
| **Inspecția: observații/neconcordanțe** | GEV 630 §111.a.3 | cap. 4 (677-678) | Opțional — rendat doar dacă există; altfel omis tăcut. |
| **Regim teren (intravilan/extravilan)** | GEV 630 §16; SEV 230 §40 | cap. 4 (642), „categorie" | Implicit `LandData.categorie="intravilan"`. Întotdeauna rendat. Pentru agricol: + categorie folosință + clasă calitate (643-645). |
| **Utilități** | GEV 630 §28 | cap. 4 (648-649) | Opțional (listă) — rendat doar dacă lista nu e goală; altfel omis tăcut. |
| **Regim urbanistic (POT/CUT) / restricții** | GEV 630 §16 | cap. 4 (650-651), `restrictii_urbanism` | Opțional — rendat doar dacă există; altfel omis tăcut. |
| **Cale de acces** | GEV 630 §28 | cap. 4 (646-647), `acces` | Opțional — rendat doar dacă există; altfel omis tăcut. |
| **Scop, client, beneficiar, moneda+curs, date** | SEV 101 §20.1 | termeni (240-254) | Scop/client/monedă/date întotdeauna rendate; beneficiar, curs, data inspecției, valabilitate doar dacă există. |
| **Elemente suplimentare SEV 101 §20.1** | SEV 101 §20.1 e/i/j/n/o; SEV 106 §30.6 m/o | termeni (292-320) | Întotdeauna rendate ca text fix: evaluator, natura/amploarea activităților, sursa informațiilor, factori ESG, specialist, tipul raportului + restricții de difuzare. |

**Tipar de comportament:** câmpurile **critice la garantare** (sarcini CF, inspecție amploare/însoțitor) emit
**avertismente vizibile** când lipsesc; câmpurile descriptive opționale (act, utilități, POT/CUT, acces, observații)
sunt **omise tăcut** — absența lor nu e semnalată în raport. (Limită cunoscută, relevantă pentru reviewer.)

---

## 3. Split AI vs determinist

Principiu de proiectare (declarat în `narrative.py` + SYSTEM_PROMPT): **AI scrie doar proza narativă; toate
numerele rămân deterministe.** Prompt-ul de sistem instruiește explicit „Folosești EXCLUSIV datele numerice
furnizate; nu inventezi și nu modifici cifre" + interdicție de a inventa surse/studii/citate legislative +
formulări prudente pentru aprecieri de piață (`narrative.py:63-73`).

**AI (narativ)** — 7 capitole în `CAPITOLE_NARATIVE` (`narrative.py:17-25`), generate de `generate_narrative`
(181-212) prin client Claude (`AnthropicNarrativeClient`, model implicit `claude-sonnet-4-6`, `temperature=0.2`,
prompt caching pe blocul de sistem) sau Perplexity sonar; **fără client → placeholdere** „[de completat...]":
1. Ipoteze generale și speciale (cap. 2)
2. Prezentarea datelor de piață (cap. 3)
3. Descrierea juridică și fizică a proprietății (paragraf adițional în cap. 4)
4. Analiza CMBU (cap. 5)
5. Justificarea ajustărilor aplicate (în cap. 6)
6. Reconcilierea rezultatelor și concluzia valorii (cap. 7)
7. Riscul asociat garanției GEV 520 (secțiune back matter, doar la garantare)

Fiecare capitol primește un „îndrumar" de conținut (`GHID_CAPITOL`, 28-61) care ghidează structura, **nu**
cifrele. Datele numerice trimise la AI (`_facts`, 114-155) sunt rotunjite la 2 zecimale și **anonimizate** înainte
de trimitere (`anonymizer.mask` + plasă de siguranță GDPR `filtreaza_pii_rezidual` pentru CNP/telefon/email scăpate,
77-88); textul primit e demascat local (`anonymizer.unmask`) și curățat de citări web/markdown (`_curata_narativ`,
170-178).

**Determinist** — restul: toată identificarea/metadatele (copertă, scrisoare, declarație, termeni), **toate
valorile și grilele** (comparație, teren, cost, venit/DCF), alocarea valorii, valoarea de lichidare (factor 0.85),
verificarea de consistență GEV 520, checklist-ul GEV 520, anexele. Valoarea finală, metoda selectată, CIN/CIB,
ajustările etc. provin din `results.py` (motorul de calcul), nu din AI. **Niciun audit nu a găsit erori de
aritmetică** (SINTEZA §Verdict; matrice §4).

**Modul `adnotari` (note de proveniență)** — `genereaza_raport(..., adnotari=True)` activează `_nota` (50-61),
care inserează sub fiecare titlu o „NOTĂ DEMO" colorată (italic, 8.5pt, portocaliu) explicând proveniența
secțiunii. Dicționarul `ADNOTARI` (21-47) folosește taxonomia:
`[CALCULAT]` (motor de calcul) · `[EXTRAS]` (din anunț) · `[INTRODUS]` (de evaluator) · `[AI]` (text generat) ·
`[SABLON]` (text fix standard) · `[EXEMPLU]`/`[PLACEHOLDER]` (valori demonstrative de înlocuit). Exemple: copertă
= [INTRODUS] identificare + [CALCULAT] valoare; cap. 3 = [AI] „NU pe o bază de date de tranzacții reale"; cap. 6 =
[CALCULAT] grile + [EXTRAS] prețuri comparabile + [EXEMPLU] ajustări demonstrative; semnătură = [PLACEHOLDER].
**Notele NU apar în raportul real** (`adnotari=False` implicit); sunt strict pentru demo/review.

---

## 4. Standardele citate (ediția 2025) și unde apar

Ediția SEV 2025 (în vigoare 1 iulie 2025, HCN nr. 2/2025) — citată în scrisoarea de transmitere (188-190) și
declarația de conformitate (219-221).

| Standard | Unde în raport |
|----------|----------------|
| **SEV 101** (Termenii misiunii de evaluare) | termeni §20.1 e/i/j/n/o (293-320); independență GEV 520 A3 trimite la SEV 101 (279-284) |
| **SEV 102** (Tipuri ale valorii / IVS 104) | tip valoare + sursă, `_TIP_VALOARE_TXT` + `_tip_valoare_txt` (83-101); checklist GEV 520 (502) |
| **SEV 103** (Abordări în evaluare ≈ IVS 103) | cap. 6 paragraf-cadru (693-696) |
| **SEV 105** (Modele de evaluare ≈ IVS 105) | cap. 6 paragraf-cadru (693-696) |
| **SEV 106** (Documentare și raportare) | docstring + structura celor 7 capitole; §30.6 m/o citat în termeni (308-315) |
| **SEV 230** (Drepturi asupra proprietății imobiliare) | drept evaluat (259), sarcini CF (262-266) |
| **GEV 520** (Evaluarea pentru garantarea împrumutului) | clauză ghid (203), premise A8 (273-276), independență A3 (279-284), ipoteze speciale A4-A5 (286-291), secțiune risc A5 + lichidare + checklist (453-519), verificare consistență alocare (438-450) |
| **GEV 630** (Evaluarea bunurilor imobile) | clauză ghid (204); descriere fizică §16/§24/§28/§44/§111 (cap. 4); tip valoare asigurare (88) |
| **GEV 500** (Estimarea valorii impozabile a clădirilor) | clauză ghid (205); `_TIP_VALOARE_TXT` impozabilă (88) |
| **IVS 104 / IFRS 13** | în textul tipurilor de valoare (84-88) |

Clauza de ghid GEV efectiv citată e determinată de `ctx.profil.ghid` prin `_GHID_CLAUZA`/`_ghid_clauza`
(202-212) — deci raportul citează **un singur** ghid GEV (cel din profil). Vezi limita din §5 (matrice).

---

## 5. Starea de conformitate SEV 2025 (din SINTEZA + matrice)

Buckets: **A** = cod, non-metodologie (rezolvabil de echipă) · **B** = evaluator senior (metodologie/praguri/framing) ·
**C** = jurist. **Verdict general:** aplicația e solidă și în mare conformă — raportul .docx urmează fidel scheletul
SEV 106 + GEV 520, motorul implementează corect cele 3 abordări, **niciun audit nu a găsit erori de aritmetică**.
Golurile sunt de (a) completitudine a raportului, (b) metodologie de calibrat de evaluator, (c) un blocaj de UI.

### ✅ REZOLVAT (Bucket A, cu teste)
- **#3 Tip valoare + sursă** în raport (SEV 102 / IVS 104), slug→denumire lizibilă (`_tip_valoare_txt`).
- **#6 Descrierea proprietății completă**: tip drept, sarcini CF, act proprietate, regim teren, proprietar,
  utilități, regim urbanistic (POT/CUT), cale de acces — GEV 630 §16/§28 + SEV 230 §40/§140.
- **#7 Inspecția**: amploare + însoțitor + observații/neconcordanțe (avertizează dacă lipsesc) + fix `data_inspectiei`.
- **#1 (backend) Anexe** foto/scanuri embedate în raport (`_adauga_anexe`) — backend funcțional.

### 🟠 RĂMÂNE — Bucket A (cod, neatins intenționat)
- **#4** `tip_valoare` propagat doar prin `meta` (nu derivat din profil) + `TipValoare="lichidare"` cod mort →
  un tip de valoare ≠ piață nu poate fi cerut efectiv prin profil (atinge lichidarea = devine B).
- **#8** Recipisa BIG e doar narativă (cerută ca element formal) — câmp + integrare externă.

### 🟡 RĂMÂNE — Bucket B (evaluator: alerte metodologice; NU se atinge formula)
Aplicația **avertizează, nu blochează**. Goluri semnalabile prin ALERTE fără a schimba calculul:
- **#9** Neaplicarea unei abordări nu cere justificare + divergența/media mecanică între abordări negardată (SEV 103 §40.3/§10.7/§10.9).
- **#10** Selecția comparabilei = regulă unică „brută minimă" (risc de alunecare spre AVM) (SEV 105; A10.6(f)).
- **#11** Ajustări liniare fără justificare obligatorie + lipsă gardă pe ajustarea NETĂ (SEV 103 §20.5, A10.8).
- **#12** DCF: valoare terminală = sumă manuală, fără Gordon/exit; rată nedocumentată.
- **#13** Cost: ignoră indirectele + profitul promotorului; depreciere pe vârstă cronologică liniară.
- **#14** **Valoarea de lichidare: factor fix 0.85 auto-generat**; lipsesc cele 2 premise (ordonată/forțată) +
  declararea premisei (def. A60 schimbată în 2025) — GEV 520 A120; SEV 102 A60. *(vizibil direct în raport, 482-494)*
- **#15** Cost ca abordare principală la imobil fără gardă (GEV 520 §31/§34).
- **#2 Declarația de conformitate e necondiționată** — raportul afirmă „conform SEV" chiar dacă validările cad
  (SEV 106 §30.8). Marcat P0 în SINTEZA; fixul tehnic (gardă) = A, **dar wording-ul = confirmă evaluatorul**.
- **Framing ghid GEV (din matrice E):** câmpul unic `ghid` nu poate ține simultan ghidul de scop + ghidul de metodă.
  - **2.1 Inversiune încrucișată** `IMPOZITARE→GEV_630` vs `RAPORTARE_FINANCIARA→GEV_500` — **asertată în teste**
    (`test_assembler_profil.py:51-52`), deci decizie de framing, nu regresie. GEV 500 e ghidul de impozitare;
    raportarea financiară se face pe SEV 430 / valoare justă. → confirmă evaluatorul (improbabil intenționat).
  - **2.4** Garantare industrial/agricol/special pe `GEV_630` pierd referința GEV 520 (obligatoriu la garantare);
    casă/apartament pe `GEV_520` pierd GEV 630. Recomandare: raportul să **citeze ambele** (520 ca utilizare
    desemnată + 630 ca metodă).
  - **2.6** Asigurare → `GEV_630` în loc de SEV 450; litigii → `GEV_630` fără SEV 230 §20.6. Metodologic acceptabil,
    dar trasabilitatea ghidului de scop lipsește.

### 🔵 RĂMÂNE — Bucket C (jurist) / module viitoare
- **#16 SEV 400 „Verificarea evaluării"** — absent integral (GEV 520 §18 îl invocă); modul viitor.
- **#17** Acord scris pe termenii de referință (SEV 101 §20.2) + disclaimer „asistare, nu AVM" + ESG real
  (nu hardcodat) — C / B.
- Tip valoare la **litigii** per speță (despăgubire/prejudiciu/justă) — B/C.
- **AML/legal (F):** pragurile corecte; eroare de citare disclaimer (art. 33 → art. 43/44/49) + 3 goluri GDPR —
  toate bucket C, escaladate (deținute de loop-ul autonom AML, nu de acest review).

### 🔴 Blocaj de UI (P0, nu de backend)
- **#1 Anexe foto/documente blocate în UI nou** (`dosar.html` „comercial"): **backendul EXISTĂ și e funcțional**
  (`_adauga_anexe`; wizardul le atașează). Deblocarea = portare wizard→dosar (frontend), **nu dezvoltare backend**.
  Întreg UI-ul nou are regresii 100% de frontend (curs EUR, câmpuri dinamice per tip, descoperire comparabile,
  AML/GDPR/audit in-place) — vezi `docs/audit-ui-nou/00-REVIEW-si-plan.md`.

---

### Rezumat pentru reviewer (1 frază)
Raportul .docx este complet structural (shell GBF + 7 capitole SEV 106 + alocare + risc GEV 520 condiționat + anexe +
semnătură), cu **toate numerele deterministe** și **doar proza narativă scrisă de AI** (anonimizat, fără cifre
inventate); conformitatea de completitudine descriptivă e rezolvată (Bucket A), iar ce rămâne e **metodologie de
calibrat de evaluator** (factor lichidare 0.85, declarație de conformitate necondiționată, framing ghid GEV) și
**chestiuni de jurist** (SEV 400, ESG, AML/GDPR).
