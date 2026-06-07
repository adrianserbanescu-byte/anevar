# 🔒 BLOCAT pe Adi — lista unică a deciziilor pe care doar tu le poți lua

> Sursă unică de adevăr pentru tot ce mă blochează (eu fac restul autonom). Agregat din:
> `00-SINTEZA-lansare-pentru-Adi.md`, `plan-maine-2026-06-06.md` §B, auditurile din `docs/audit/`,
> `strategie-comercializare-intrebari.md`. Actualizat: 2026-06-06 (sesiune autonomă).

## A. Lansare pe piață — validări externe (drumul critic, asincron la terți)
1. **Avocat AML** (Legea 129) — audit pe `audit-aml-pentru-jurist.md`. **BLOCANT ABSOLUT** (risc penal).
2. **2-3 evaluatori seniori** — peer-review pe `protocol-peer-review-evaluator.md` (validează premisa produsului + metodologia).
3. **Jurist GDPR** — validează `docs/legal/` (DPA art. 28, transfer LLM extra-UE/SCC, încadrare AI Act).
4. **Asigurătorul de răspundere profesională ANEVAR** — confirmă că rapoartele asistate AI sunt **acoperite** (council #2; poate exclude → „comercial mort"). *Nou, important.*
5. **Validare bancă** — pilot pe 20-30 dosare reale cu departamentul **Risc/IT** al UNEI bănci, **după** fixurile de metodologie (nu 2-3 rapoarte ad-hoc).

## B. Achiziții / conturi (doar tu)
6. **Certificat code-signing** (~150-300 €/an) — fără el, SmartScreen sperie profesioniștii.
7. **Conturi externe** pentru gateway: Supabase + Google OAuth + Stripe (Faza 0 comercializare).
8. **Screening AML:** API live (OpenSanctions) **vs.** dezactivare totală cu trimitere la surse oficiale.

## C. Decizii de produs — UI nou / dosar (din plan-maine §B; le tranșăm la brainstorm #1)
9. **Ordine creare dosar:** gol-apoi-completezi (acum) vs. modal de identitate înainte de folder.
10. ✅ **REZOLVAT (2026-06-07):** **Blocare identitate — trigger HIBRID TRIPLU:** (1) checkpoint asumare (om-în-buclă) + (2) prima generare `.docx` + (3) **upload fișiere submise** (ex. `.docx` editat returnat de bancă/client) — trigger NOU. ADR-003 trebuie refăcut cu varianta hibrid+upload. Cuplat cu #34.
11. **„Importă dosarul tău" =** raport `.docx` (acum) vs. folder (`importa_folder`, adoptă/clonează).
12. **Format-nume vs. câmpuri-identitate** (`CAMPURI_NUME_DOSAR` ⊃ `CAMPURI_IDENTITATE`?).
13. ✅ **REZOLVAT (2026-06-07):** **Monedă implicită = EUR la scop „garantare"** (LEI rămâne pentru alte scopuri). Băncile RO cer EUR pe garanție.
14. ✅ **REZOLVAT (2026-06-07):** **Generează cere Calcul reușit (DA).** Single source of truth — dacă calcul eșuat, raportul nu se generează (422 sau buton dezactivat).
15. ✅ **REZOLVAT (2026-06-07):** **Home — opțiunile comerciale ASCUNSE complet pe build offline.** Pur tehnic, fără teasere.
16. ✅ **REZOLVAT (2026-06-07):** **Popover „!" — DA, șterg** (era patch tranzitiv, mapping vechi→nou validat).

## C2. Decizii din council-ul pe feature-uri (2026-06-06) — vezi `9-topicuri-decizie.md` + `council-plan-UI-nou.md`
24. ✅ **REZOLVAT (2026-06-07): P0 conformitate SEV 2025 — gating DOAR pe volum** (vezi runda decizii comerciale pentru exact câte poze gratis, recomandare council: 10-20). Cuplat cu modelul comercial #20.
25. 🟡 **AMÂNAT — revizităm după runda decizii comerciale.** **Regenerare AI (feature B):** confirmă conceptul — implicit **TEMPLATE** (păstrează vocea, actualizează valori) + diff per capitol + override. Apoi îl construiesc.
26. ✅ **REZOLVAT (2026-06-07): Confirmă matricea implicită** (Zonă/Piață=GHIDARE, Descriere=DIFERIT) + detecția PII la import.

## D. Decizii arhitecturale (din auditul tehnic)
17. **Migrare SQLite-vechi → foldere:** dosarele din `/dosare` (SQLite) și `/incepe` (foldere) sunt mulțimi disjuncte. Le punți, le lași separate, sau retragi stocarea veche?
18. **Retragere UI vechi (wizard/formular)?** Noul UI = unic țintă pe termen lung — când oprim întreținerea celui vechi?
19. **Paritate UI nou:** adaug în UI nou grila de teren + chirii/venit/DCF + anexă foto/documente? (datorie de paritate — vezi `audit/2026-06-06-SINTEZA-audituri.md`).

## E. Comercial / preț (din strategie-comercializare-intrebari.md)
20. ✅ **REZOLVAT (2026-06-07): Pro 299-399 lei/lună, o singură treaptă la lansare.** Pe valoare, mai sus; 1 tier simplu; ajustez după primii useri.
21. ✅ **REZOLVAT (2026-06-07): DA — validez cu 5 evaluatori reali ÎNAINTE de Stripe/gateway.** Confirmă premisa produsului înainte de investiția în infra (1-2 săptămâni outreach).
22. ✅ **REZOLVAT (2026-06-07): Supabase Studio + SQL views.** Zero cost build, views pe nevoi, scalabil cu Postgres.
22bis. ✅ **REZOLVAT (2026-06-07): Anexă foto — 10 poze gratis, peste = plată** (cuplat cu #24). Acoperitor pentru evaluare medie; gating clar; recomandare council.

## F. Decizii minore de design (impact mic)
23. `.cross-ui` în antet+subsol (cerut de tine) — păstrăm complet sau simplificăm antetul la „⇄ Schimbă interfața"?
24bis. Emoji vs. iconografie SVG topograf (termen mediu).

## G. Conformitate tip×scop (din `conformitate/E-matrice-tip-scop.md`, loop special) — Bucket B (evaluator)
27. **Inversiune GEV (cea mai gravă):** `IMPOZITARE→GEV_630` și `RAPORTARE_FINANCIARA→GEV_500` par **schimbate**
    (GEV 500 = „valoare impozabilă"; raportarea = SEV 430/justă). **Asertat în teste** → intenționat sau bug? Tu confirmi.
28. **Impozitare:** `tip_valoare="piata"` vs „valoare impozabilă" distinctă (standard l.4059); cost nemarcat obligatoriu.
29. **Câmp `ghid` unic** nu poate cita simultan 2 ghiduri (garantare: GEV 520 scop + GEV 630 metodă). Refactor model = A, dar regula = B.

## H. AML / juridic (din `conformitate/F-lege-norme-aml.md`, loop special) — Bucket C (jurist)
30. **Eroare de citare în disclaimer AML:** textul citează „Legea 129/2019 art. 33" pentru SANCȚIUNI — greșit;
    corect **art. 43/44 (contravenții) + art. 49 (penal)**.
    ✅ **Corectat (2026-06-06): art. 33 → art. 43/44/49** în `aml/documente.py` (`_antet`) + `docs/audit-aml-pentru-jurist.md` §3 pct. 4; test `test_garduri_council.py` actualizat. **Doar numărul articolului schimbat — restul formulării NEATINS. Necesită confirmare jurist (bucket C).**
    ✅ **Aplicat și în UI (2026-06-06):** aceeași corectură art. 33 → art. 43/44/49 în `aml.html` (disclaimer + confirm RTS/RTN)
    și `curent/dosar.html` (banner AML + confirm RTS/RTN). `art. 38` (tipping-off/non-divulgare) **lăsat neschimbat — e corect**.
    **Tot textul juridic e doar numărul articolului; PENDING confirmare jurist (bucket C) — dacă juristul spune altă încadrare, schimb peste tot.**
31. **Goluri AML noi (jurist):** informare GDPR client înainte de relație (art. 22(2)); ștergere date la expirarea retenției
    (art. 21(4)); coborârea pragului beneficiar-real la risc sporit (Norme art. 16(4)(e)); monitorizare continuă (avem one-shot).
32. ✅ **Închis:** pragul de „3.000 €" din auditul vechi e **INFIRMAT** — nu există în lege (toate celelalte praguri sunt corecte).
36. **Descoperire D4 — pivot ANCPI/notariat (preț FINAL tranzacționat) — NEALINIERE de validat juridic (decizia Adi: bucket C):**
    - **Problema (council, ridicată doar de Claude):** anunțurile de pe portaluri = preț **ASK** (cerere), umflat tipic **+10–15%** față de prețul real tranzacționat. Comparabilele construite din anunțuri moștenesc distorsiunea → supraevaluare sistematică dacă nu se ajustează.
    - **Soluția propusă:** acces la prețurile **FINALE** din **ANCPI** (carte funciară) / **notariat (UNNPR)** ca „strat 0" mult mai exact decât anunțurile.
    - **Nealinierea juridică (de ce e bucket C):** datele ANCPI/notariat **NU sunt public-accesibile** pentru agregare/scraping; accesul cere **temei legal** + ridică **GDPR** pe datele de tranzacție (preț + identitatea părților). De validat de jurist: *putem accesa + folosi legal aceste date într-un tool comercial?*
    - **Mitigare curentă (dacă NU):** rămânem pe anunțuri + **ajustare ofertă→tranzacție** (GEV 520 §4.3.4) — deja în aplicație. Dacă DA → cel mai mare salt de acuratețe al „Descoperă".

## I. ADR-uri formale (din `docs/adr/`) — AVANSATE 2026-06-07 (rămân doar deciziile tale)
- **ADR-002** (SQLite→foldere): ✅ **script de migrare implementat** (`src/evaluare/migrare.py` + CLI + teste, ne-distructiv/idempotent). Rămân: declanșatorii Fazei 2/3 (#17/#18).
- **ADR-003** (lock identitate): ✅ declanșator **DECIS (#10 hibrid)** + **fundație implementată** (amprentă SHA256 per versiune + `asumat_la` + trigger upload-submis + tamper-evidence în audit). Rămân: enforcement read-only + clonare + identitate cod-fiscal (decizii UX/produs — #10/#12).
- **ADR-004** (AI gateway): ✅ **offline-fallback verificat (test)**. Rămân: jurist GDPR transfer extra-UE/DPA/AI Act (#3/#4) + conturi externe (#7).

## J. Audit final + LLM council (2026-06-06) — Bucket-A REZOLVAT; rămân pe tine:
33. **Criptare la repaus (PII pe disc)** — SQLite + dosare + rapoarte sunt în CLAR. Decizie: (a) doar disclaimer
    „protecția discului = responsabilitatea evaluatorului/operator de date", (b) ghidaj BitLocker la instalare, sau
    (c) criptare cu parolă în app. Council: minim (a)+(b). **Bucket C (jurist) + decizie produs.**
34. ✅ **REZOLVAT (2026-06-07): Trigger lock = HIBRID TRIPLU** — vezi #10. **IMPLEMENTAT INTEGRAL ÎN COD (2026-06-07):**
    hash integritate per versiune + `asumat_la` + trigger upload-submis + **identitate read-only** + **clonare „Dosar nou"**
    + **de-lock cu motiv→Audit** + **`.lock` de concurență**. ADR-003 închis (rămâne doar #12, set identitate cod-fiscal).
35. **Minim lansare sigură (ordinea councilului):** (1) disclaimere juridice în raport [jurist] · (2) alerte
    metodologice trasabile [evaluator] · (3) ✅ **lock identitate [#34 — IMPLEMENTAT]** · (4) gardă re-încadrare anexe [evaluator].
> ✅ Făcute de mine din audit+council (Bucket A): anti-SSRF, gardă Host (anti DNS-rebind), grilă→422, fix dată
> tăcută, pierdere date localități, CNP prefix 9, limită DoS, igienă temp .docx (PII). Vezi `docs/audit-final/`.

## K. Audit skill-uri Claude Code (2026-06-07) — vezi `audit-skills-2026-06-07.md`
> Restul recomandărilor de la cele 6 skill-uri sunt autonome și sunt deja în `AUTONOM-taskuri.md`
> secțiunea „🔧 Audit skill-uri (2026-06-07)". Aici rămân doar deciziile.

36. ✅ **REZOLVAT (2026-06-07): Opțiunea (a) — refactorizez `assembler.py:130-158`** să cheme `abordare_cost/comparatie/venit` în loc de `evaluate_cost/evaluate_market/evalueaza_venit`. O singură sursă de adevăr aliniată SEV 2025.

37. ✅ **REZOLVAT (2026-06-07): Opțiunea (a) — marchez deprecat ACUM** + log fiecare hit pe `/api/evaluare/*`. Telemetrie ușoară: când deprecăm UI vechi (§D.18) avem date concrete cine îl folosește.

> **Regula de aur (respectată peste tot):** aplicația **avertizează**, nu decide. Metodologia și
> pragurile legale **nu se ating** fără semnătura unui evaluator senior / jurist.
> Tot ce NU e aici îl fac eu autonom (cod, teste, build, documente, audituri).
