# Audit de design — app evaluare ANEVAR (Dieter Rams, 2026-06-07)

> Metodă: skill `claude-mem:design-is` (10 principii Rams, 0–3, verdict keep/refine/redesign).
> Probe: 12 screenshot-uri full-page (`docs/design-audit/screens/`) + 3 subagente de evidență + cod.
> Scop: rank „cât de proaste sunt paginile" + verdict per pagină → plan de refacere UI/UX coerent (v1 + v1.5).

## Concluzia de bază (cea care economisește bani)
**Sistemul de design e BUN — NU-l aruncăm.** Există un limbaj vizual unitar, distinctiv și onest
(`_design.css`: scală 4px, scală de tip, paletă WCAG-adnotată, temă „registru cadastral / topograf" —
cartuș, tricolor, busolă, hârtie milimetrică, serif de document). E **mai bun decât 90% din tool-urile B2B**.

Deci nu e „redesign de la zero", ci: **REFINE la nivel de SISTEM** (câteva defecte transversale) +
**REDESIGN țintit** la 2 pagini cu UX prost + **RETRAGERE** a paginilor v0 vechi.

## Defecte TRANSVERSALE (lovesc toate paginile — prioritate maximă)
1. **#8 Thoroughness — stări lipsă + date-pickere native nestilizate.** Aproape nicăieri: focus vizibil
   consistent, error/validare, loading, empty cu CTA. Date-pickerele native arată **„mm/dd/yyyy" (format US)**
   pe un app declarat **ro-RO** — bug de locale + rupere de temă (workspace).
2. **#10 Little design — ornament fără funcție.** „SCARA 1:500 / SISTEM STEREO 70", busola, crucile din colț =
   decor pur pe un tool utilitar. Nav duplicat (header + footer). Tag-uri DOCX/LOG/ZIP repetate pe fiecare rând.
3. **Inconsistență de paletă (#3/#6).** Butonul CTA **rust/maro** + butoane **verzi/teal** (cont, wizard, formular)
   ies din navy/gold. **Iconografie pe emoji** (40 apariții) = cel mai off-brand + dependent de platformă.
4. **Bug de wrap în stepper-ul v1.5:** „Proprietat e", „Conformit ate" — cardurile prea înguste rup cuvintele.

## RANK (rău → bun) + verdict per pagină
| # | Pagină | Tier | Verdict | De ce (probă) |
|---|--------|------|---------|---------------|
| 1 | **12-formular-VECHI** | D | **RETRAGE** | v0 legacy: valori default = string-uri JSON/CSV brute expuse userului; verde off-paletă; wall-of-text. |
| 2 | **11-wizard-VECHI** | D | **RETRAGE** | v0 legacy: 4+ accente (teal/verde), panou flotant care suprapune formularul, pattern wizard datat. |
| 3 | **06-descoperire** | C | **REDESIGN** | câmpuri cu lățimi ragged (numerice minuscule vs text late), label orfan „Casa subiect:", CTA rust slab. *(deja în redesign B+C)* |
| 4 | **04-dosar-workspace** | C | **REDESIGN (data-entry)** | CSV/`;`-free-text pt cost/depreciere („Structura;X;mp;120…") = error-prone; date US; 2 rânduri de tab-uri ambigue; formular monolit lung. Shell-ul rămâne. |
| 5 | **07-aml** | B | **REFINE++** | 14 checkbox-uri într-o listă plată; 4 familii de accent pe o pagină; 2 butoane rust egale (fără ierarhie). |
| 6 | **08-grila** | B | **REFINE++** | cea mai „app-like" (grila navy-header e bună!) dar dublează formularul Descoperire; 2 CTA-uri rust egale. |
| 7 | **05-dosare** | A | **REFINE** | empty-state fără CTA (trimite la „wizard" cu link text); whitespace orizontal masiv; ornament greu. |
| 8 | **02-flux-livrabile (v1.5)** | A | **REFINE (funcțional)** | cel mai bogat vizual DAR ne-funcțional (carduri statice — F0/F1 rezolvă) + bug wrap stepper + densitate. |
| 9 | **10-cont** | A | **REFINE** | buton primar verde/oliv off-paletă; jumătatea dreaptă goală. |
| 10 | **09-documente** | A | **REFINE (minor)** | calm, editorial, bun; doar dunga multicoloră de sus + nav utilitar înghesuit. |
| 11 | **03-incepe (v1)** | A | **REFINE** | curat, aerisit; expune token intern „id_client_nume_client_…"; fără empty-state. |
| 12 | **01-index** | A | **REFINE / repensează conceptul** | cel mai polish. DAR: „alege interfața (v0/v1/v1.5)" e un smell de produs — userul n-ar trebui să aleagă versiunea. |

**Tier A** = bone bune, refine. **B** = refine greu (densitate/duplicare). **C** = redesign (UX rupt). **D** = retrage (v0).

## VERDICT DE SISTEM: **REFINE** (limbajul e bun) + redesign țintit + retragere v0
Nu „NEW", nu „REDESIGN total". Mutările cu cel mai mare leverage:
1. **#8 — pune un strat de stări GLOBAL** (focus-ring consistent, error/validare, loading, empty-cu-CTA) în `_design.css` + **stilizează date-pickerele** la ro-RO (`zz.ll.aaaa`). Lovește toate paginile.
2. **#3/#6 — disciplina paletei:** un singur CTA primar (decide navy SAU gold SAU rust — nu 3), elimină verde/teal, **înlocuiește emoji cu iconuri SVG** topograf (deja pe roadmap).
3. **#10 — taie ornamentul mut** (SCARA 1:500 etc.) sau fă-l opțional; de-duplică nav header/footer; comasează formularul-Descoperire duplicat (grila ↔ descoperire).
4. **C — redesign data-entry:** workspace (înlocuiește CSV-free-text cu câmpuri structurate/tabel editabil + date ro-RO) + descoperire (grid de câmpuri consistent).
5. **D — retrage v0** (wizard/formular) — aliniat ADR-002 (migrare SQLite→foldere); nu le redesigna, le scoți.
6. **v1.5 funcțional** (F0/F1) + repensează `/index`: nu „alege versiunea" ci o singură ușă (v1.5) → app.

## Lane-uri
- **Sistem (#8/#3/#10):** `_design.css` + partials — **C** (cu A pe review), lovește tot → cel mai mare ROI.
- **Redesign workspace data-entry:** **A** (e shell-ul meu, ADR-003) + C pe UI.
- **Descoperire:** **B** (motor) + **C** (UI) — deja în curs.
- **Retragere v0:** **A** (rute + cleanup) când Adi confirmă (#18 BLOCAT).
