# Audit de usability / interacțiune — app ANEVAR (2026-06-07)

> Metodă: skill `webapp-testing` (Playwright, interacțiune reală) — detecție automată (erori consolă, overflow,
> tokeni expuși, câmpuri fără label, date-inputs) + review euristic pe screenshots. Complementar auditului VIZUAL (Rams).
> Sursă: `scripts/_usability_audit.py` (regenerabil). Screenshots: `docs/design-audit/ux-*.png`.

## 🔴 HIGH — interacțiune (le lovești de fiecare dată)
1. **Date-pickere — 6 inputuri** (incepe×1, dosar×4, aml×1): **(a)** se deschid DOAR pe iconița mică de calendar, nu pe tot field-ul *(observația ta #2)*; **(b)** format `mm/dd/yyyy` (locale OS) pe app declarat ro-RO.
   → Fix: `input.showPicker()` la click pe TOT field-ul + afișare consistentă `zz.ll.aaaa`. **Lane: A (helper partajat de dată).**

## 🟠 MED
2. **Tokeni interni expuși în text** — incepe + cont: `scop_data_raport_nume_evaluator`; dosar: `cost_unitar`. Userul vede convenția internă de nume.
   → Fix: etichetă prietenoasă („Scop · Dată raport · Nume evaluator"). **Lane: C (incepe/cont) + A (dosar).**
3. **incepe — paginație/layout** *(observația ta #1)*: butoane cu lățimi inegale, ritm vertical neuniform (header → „Conectat" → butoane → tabel), whitespace mare.
   → Fix: butoane în grup coerent (lățimi egale), ritm consistent. **Lane: C (incepe.html).**
4. **Câmpuri fără label/aria-label** — dosar×2. a11y + claritate. → adaugă etichete. **Lane: A (dosar.html).**
5. **dosar — 2 rânduri de tab-uri** (domeniu + sub-tab) — ambiguu „pe ce nivel sunt". → un nivel sau clarificare vizuală. **Lane: A.**
6. **Comparabile încă CSV** — dosar: `comparabile`/`comparabile_teren` = textarea `preț;suprafață` (am convertit doar cost/depreciere). → grid editabil. **Lane: A (coordonat cu C).**

## 🟡 LOW (e tool DESKTOP — mobil nu e target, dar arată layout ne-fluid)
7. **Overflow orizontal la 390px** — aml (528px), grila (548px) → scroll lateral pe telefon. **Lane: C.**
8. **Tabel navy-header pentru 1 rând** (incepe/dosare) — greu vizual pt puține elemente. **Lane: C.**
9. **Verifică empty-state pe incepe** la 0 dosare (C a pus pe feedback_list/dosare; incepe?). **Lane: C.**

## Notă
- Auditul automat NU prinde estetică/ierarhie (alea-s în auditul Rams `AUDIT.md`). Ăsta = interacțiune + obiective măsurabile.
- Date-pickerele + tokenii expuși = cel mai mare ROI (lovești la fiecare dosar).
