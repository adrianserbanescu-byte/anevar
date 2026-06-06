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
10. **Blocare identitate după prima generare** (read-only + cale „dosar nou + credit") — declanșator?
11. **„Importă dosarul tău" =** raport `.docx` (acum) vs. folder (`importa_folder`, adoptă/clonează).
12. **Format-nume vs. câmpuri-identitate** (`CAMPURI_NUME_DOSAR` ⊃ `CAMPURI_IDENTITATE`?).
13. **Monedă implicită** EUR la scop „garantare" (acum LEI).
14. **Calcul→Generează:** o singură sursă de adevăr (Generează cere Calcul reușit?).
15. **Home cu 5 opțiuni, 2 dezactivate** (comercial) — teasere vs. ascunse pe build offline.
16. **Popover „!" temporar** — confirmi că-l ștergem după validarea mapării vechi→nou?

## C2. Decizii din council-ul pe feature-uri (2026-06-06) — vezi `9-topicuri-decizie.md` + `council-plan-UI-nou.md`
24. 🔴 **Anexa foto/scanuri = cerință de CONFORMITATE SEV 2025 (CONFIRMAT în standard, nu doar de council).**
    Bază: **GEV 630** listează „Anexele raportului (Fișe clădiri, **fotografii** etc.)" + cere inspecție cu „fotografii
    din exterior" (l.5645/4079); SEV 230 §120 + SEV 106 §30.6. (Google cita „SEV 102" = numerotare veche; substanța e corectă.)
    Gating-ul TOTAL ca feature comercial face raportul incomplet/neconform pt bancă/ANAF/instanță. **Decizie: re-încadrăm
    atașarea anexelor ca P0 de conformitate (gating doar pe VOLUM, ex. 10-20 poze gratis)?** Detalii: [`validare-SEV2025-anexe-si-council.md`](validare-SEV2025-anexe-si-council.md).
25. 🟡 **Regenerare AI (feature B):** confirmă conceptul — implicit **TEMPLATE** (păstrează vocea, actualizează valori)
    + diff per capitol + override. Apoi îl construiesc.
26. 🟡 **Import asemănător (feature D):** confirmă matricea implicită (Zonă/Piață=GHIDARE, Descriere=DIFERIT) +
    detecția PII la import. Apoi îl construiesc.

## D. Decizii arhitecturale (din auditul tehnic)
17. **Migrare SQLite-vechi → foldere:** dosarele din `/dosare` (SQLite) și `/incepe` (foldere) sunt mulțimi disjuncte. Le punți, le lași separate, sau retragi stocarea veche?
18. **Retragere UI vechi (wizard/formular)?** Noul UI = unic țintă pe termen lung — când oprim întreținerea celui vechi?
19. **Paritate UI nou:** adaug în UI nou grila de teren + chirii/venit/DCF + anexă foto/documente? (datorie de paritate — vezi `audit/2026-06-06-SINTEZA-audituri.md`).

## E. Comercial / preț (din strategie-comercializare-intrebari.md)
20. **Model de preț:** recomand pe valoare, mai sus (Pro ~299-399 lei/lună), o singură treaptă la lansare.
21. **Ordinea comercială:** validezi cu 5 evaluatori reali ÎNAINTE de a construi gateway/Stripe? (recomand: DA).
22. **Master-admin:** Supabase Studio + view-uri SQL (recomandat) vs. panou custom.

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

## I. ADR-uri formale propuse (din `docs/adr/`, loop special) — confirmi declanșatorii
- **ADR-002** (SQLite→foldere): confirmi declanșatorii Fazei 2/3 (migrare + retragere) → #17/#18.
- **ADR-003** (lock identitate): confirmi declanșatorul exact de lock — „prima generare .docx" vs „checkpoint asumare" → #10.
- **ADR-004** (AI gateway): risc transfer LLM extra-UE/SCC + DPA art. 28 + AI Act → #3/#4; conturi externe → #7.

> **Regula de aur (respectată peste tot):** aplicația **avertizează**, nu decide. Metodologia și
> pragurile legale **nu se ating** fără semnătura unui evaluator senior / jurist.
> Tot ce NU e aici îl fac eu autonom (cod, teste, build, documente, audituri).
