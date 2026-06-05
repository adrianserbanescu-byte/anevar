# #1 — Redesign UI „output-first" + cadrul cu două versiuni

Status: **în definire** (2026-06-06). Vizual → folosește mockup-uri.

## Cadrul cu două versiuni (decis)
- La deschiderea aplicației → **ecran de alegere** între:
  - **„Versiune veche"** = toate paginile actuale (wizard + grile + descoperire + aml + dosare),
    UI **înghețat** (doar titlu marcat), atins **doar** la upgrade de feature.
  - **„Versiune curentă"** = set NOU de pagini, complet redesignat (output-first). Se definește acum.
- Alegerea e reținută local (poate fi schimbată).
- **Dublăm toate paginile** (izolare totală a experienței), DAR la nivel de **UI/template** —
  **backend-ul/API-ul rămâne COMUN** (ambele versiuni lovesc același `/api/*`).

## ⚖️ REGULA PERMANENTĂ de mentenanță („de aici încolo")
- **Upgrade de feature/funcționalitate → în AMBELE versiuni** (vechea rămâne funcțională la zi).
  - De obicei = backend comun (automat) + sârmuire UI în ambele template-uri.
- **Lucru pur de UI → DOAR în „versiunea curentă"** (cea nouă).
- Când nu e clar care e cazul → **se întreabă utilizatorul**.
- Versiunea veche se modifică doar la nevoie (feature) → **cu întrebare înainte**.

## Arhitectură de implementare (probabilă)
- Template-uri: `templates/` (versiune veche) + `templates/curent/` (versiune nouă). Backend
  (routere, engine, storage, `/api/*`) = neschimbat, comun.
- Selector de versiune: cookie/localStorage `versiune_ui` → routerul de pagini alege folderul de
  template. Ecran `/alege` la prima deschidere.

## ⏳ Următorul pas (de definit ACUM)
**Cum e organizat wizardul nou la nivel de PAGINI și INFO** (output-first):
- Pornim de la raport (output) spre date?
- Câte pagini/pași, ce conține fiecare, ce se comasează?
- Ce câmpuri sunt obligatorii (→ definește identitatea dosarului din #2 + metrarea #4).
- Cum arată fluxul (mockup-uri).

## Dependențe deblocate de #1
- #2 (identitatea dosarului — care câmpuri se blochează).
- #4 (metrarea pe identitate).
