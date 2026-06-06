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
24. Emoji vs. iconografie SVG topograf (termen mediu).

> **Regula de aur (respectată peste tot):** aplicația **avertizează**, nu decide. Metodologia și
> pragurile legale **nu se ating** fără semnătura unui evaluator senior / jurist.
> Tot ce NU e aici îl fac eu autonom (cod, teste, build, documente, audituri).
