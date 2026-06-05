# #2 — Rapoarte salvate + dosar cu identitate

Status: **brainstorm parțial** (2026-06-06). Partea de stocare/management = buildabilă acum;
partea de **identitate/credit depinde de #1** (fluxul UI definește câmpurile obligatorii).

## Idee
La fiecare generare, dosarul + documentul se salvează local. Userul poate reveni, edita,
regenera, șterge, redenumi. În plus — concept nou din brainstorm — fiecare dosar are o
**identitate blocată** care leagă consumul de credit de **proprietatea evaluată**, nu de timp.

## Decizii luate
1. **Stocare = dosar (JSON) + folder dedicat per dosar.** Ex. `date/dosare/<id>-<cadastral>/` cu:
   - dosarul (JSON — **sursa de adevăr**),
   - **toate generările `.docx` datate** (istoric de versiuni),
   - pozele/atașamentele.
   Dosarul rămâne sursa; `.docx`-urile sunt snapshot-uri → ai și fișierul, și curățenia.
2. **Identitate blocată (legată de #4 — metrare):**
   - Un set de **câmpuri obligatorii** se **blochează la prima generare** (când se consumă creditul).
   - **Editezi date secundare** (comparabile, ajustări, poze, narativ) → regenerezi **gratis**;
     fiecare generare = o **versiune nouă** în folder.
   - **Modifici un câmp de identitate** → prompt: *„Se va crea un dosar NOU (+1 credit). Vrei să
     preiei informațiile care se potrivesc din dosarul actual?"* → da: dosar nou, credit nou,
     folder nou, pre-completat cu ce se potrivește.
   - Înlocuiește „fereastra de grație în timp" din #4 — mai bun (blochează abuzul „altă
     proprietate", lasă iterația liberă).

## ⛔ Depinde de #1 (de rezolvat acolo)
- **Care câmpuri = identitatea blocată?** Se decide când definim **pașii UI ai unui dosar** (#1).
  - Ipoteza utilizatorului: cel puțin **tip evaluare (scop) + tip proprietate** declanșează dosar nou.
  - Candidați suplimentari (de confirmat la #1): nr. cadastral, CF, adresă.
- Logica „preia informațiile care se potrivesc" la crearea dosarului nou.

## Ce avem deja în cod
- `storage.save(ctx)` / `list()` / `load(eid)` — dosarele se salvează deja în `evaluari`.
- Lipsește: folder-per-dosar + versiuni `.docx`, pagina de management, re-hidratare wizard,
  redenumire, identitate/lock.

## ✅ IMPLEMENTAT (2026-06-06) — partea de stocare
- Migrare schema **v4** (`nume`, `creat_la`, `wizard_json`).
- `storage`: `save(nume)`, `redenumeste`, `sterge`, `set_wizard_snapshot`, `get_dosar`, `list` cu meta.
- Versionare: fiecare `.docx` generat se salvează datat în `date/dosare/<id>/`.
- Endpoint-uri: redenumire / snapshot / dosar / ștergere (+ folder).
- Pagină **/dosare** (listă, Deschide=re-hidratare wizard, Redenumește, Descarcă .docx, Șterge) + nav.
- +10 teste; 421 suită verde.

## Mai rămas buildabil (nu depinde de #1)
- Migrare schema **v4**: `evaluari.nume`, `evaluari.creat_la`, `evaluari.identitate_hash`(nullable).
- Folder-per-dosar + salvarea fiecărui `.docx` generat (datat) în el.
- Pagină `/dosare`: listă (nume, client, valoare, dată) + Deschide / Redenumește / Descarcă
  versiune `.docx` / Șterge.
- Re-hidratare wizard din `context_json`.

## Blocat pe #1 (de făcut după fluxul UI)
- Definirea câmpurilor de identitate + blocarea lor în UI.
- Promptul „dosar nou + credit + preia ce se potrivește".
- Legarea cu metrarea #4 (consum credit la identitate nouă).
