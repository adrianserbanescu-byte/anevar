# MAJOR features pending

Index al feature-urilor majore discutate (brainstorming), de implementat după decizie.
Fiecare subiect are propriul `.md` în `docs/specs/`. Actualizat: 2026-06-06.

| # | Subiect | Status | Mărime / loc | Spec |
|---|---------|--------|--------------|------|
| 1 | Refacere logică UI „output-first" (+ pașii unui dosar) | de brainstormat · **deblochează #2 și #4** | mare · în app | [specs/1-ui-output-first.md](specs/1-ui-output-first.md) |
| 2 | Rapoarte salvate + dosar cu identitate | **brainstorm parțial** · stocare buildabilă, identitate depinde de #1 | mediu · în app | [specs/2-rapoarte-salvate.md](specs/2-rapoarte-salvate.md) |
| 3 | Localități adăugate de user | de brainstormat | **mic · buildabil acum** | [specs/3-localitati-user.md](specs/3-localitati-user.md) |
| 4 | Comercializare (tool local premium + AI gateway) | **spec + plan complet ✅** | mare · proiect separat (cloud) | [design](specs/4-comercializare.md) · [plan implementare](specs/4-comercializare-plan-implementare.md) |

## Pe scurt

- **#1 — UI output-first:** refacere completă a paginilor/tab-urilor pornind de la raport (output)
  spre date. Vizual (cere mockup-uri). De făcut după feedback-ul de la review.
- **#2 — Rapoarte salvate:** dosarele se salvează deja în SQLite (`storage.save`); lipsește
  pagina de management (listă, re-deschide, redenumește, descarcă `.docx`, șterge) + re-hidratare
  wizard. Jumătate e gata în cod → livrabil rapid, util și la review.
- **#3 — Localități user:** userul adaugă localități proprii căutabile (tabel nou + integrare în
  `/api/localitati` + buton în wizard). Cel mai mic.
- **#4 — Comercializare:** app local + AI gateway online (Supabase + Stripe), metrare **per raport
  AI**, abonament tot-în-unu, Google auth, 2 sesiuni concurente. COGS ~zero → marjă ~90%. Proiect
  mare, infra externă, vine **după** review. **Spec + plan de implementare complete** (MVP pe
  task-uri + faze 2/3 schițate). Gata de construit când decizi.

## Feature-uri derivate din brainstorm (2026-06-06)
| # | Subiect | Status | Spec |
|---|---------|--------|------|
| B | Regenerare text AI (strict/template/nou, per capitol, versiuni) | notat | [note-viitoare.md](specs/note-viitoare.md) |
| D | Import „dosar asemănător" (merge AI capitole + matrice master_config) | notat | [note-viitoare.md](specs/note-viitoare.md) |

> Parking-lot complet cu toate comentariile ce impactează viitorul: [specs/note-viitoare.md](specs/note-viitoare.md).
> Decizie nouă: **fără duplicare veche/nou** — noul UI = unicul țintă (mapăm toate feature-urile vechi).

## Dependență descoperită (2026-06-06)
Brainstorming-ul lui #2 a scos la iveală că **identitatea unui dosar** (ce câmpuri se blochează
și declanșează „dosar nou + credit") e definită de **fluxul UI al dosarului = #1**. Deci:

> **#1 (pașii UI ai unui dosar) deblochează partea de identitate din #2 ȘI metrarea din #4.**

## Recomandare de ordine (revizuită)
1. **Buildabil acum, independent:** partea de **stocare** din #2 (folder-per-dosar, versiuni
   `.docx`, pagină management, re-hidratare) + **#3** (localități). Cresc valoarea la review.
2. **Apoi #1** (fluxul UI al dosarului) — definește câmpurile de identitate → deblochează
   partea de identitate/credit din #2 și metrarea din #4.
3. **#4** — la final, când decizi monetizarea (spec + plan gata).

> Aplicația curentă rămâne **gata de trimis la review** independent de astea. Acestea sunt
> dezvoltări *după*.
