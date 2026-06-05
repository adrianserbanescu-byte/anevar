# MAJOR features pending

Index al feature-urilor majore discutate (brainstorming), de implementat după decizie.
Fiecare subiect are propriul `.md` în `docs/specs/`. Actualizat: 2026-06-06.

| # | Subiect | Status | Mărime / loc | Spec |
|---|---------|--------|--------------|------|
| 1 | Refacere logică UI „output-first" | de brainstormat | mare · în app | [specs/1-ui-output-first.md](specs/1-ui-output-first.md) |
| 2 | Rapoarte salvate (revenire/editare/regenerare/ștergere) | de brainstormat | **mediu · buildabil acum** | [specs/2-rapoarte-salvate.md](specs/2-rapoarte-salvate.md) |
| 3 | Localități adăugate de user | de brainstormat | **mic · buildabil acum** | [specs/3-localitati-user.md](specs/3-localitati-user.md) |
| 4 | Comercializare (tool local premium + AI gateway) | **brainstorm complet** | mare · proiect separat (cloud) | [specs/4-comercializare.md](specs/4-comercializare.md) |

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
  mare, infra externă, vine **după** review. Spec complet scris.

## Recomandare de ordine (de discutat)
1. **Acum / înainte de review:** #2 (rapoarte salvate) și #3 (localități) — locale, rapide, cresc
   valoarea pentru evaluatorul care testează.
2. **După feedback-ul de la review:** #1 (UI output-first) — redesign informat de ce zic testerii.
3. **Când decizi monetizarea:** #4 (comercializare) — proiect separat, cu spec gata.

> Aplicația curentă rămâne **gata de trimis la review** independent de astea. Acestea sunt
> dezvoltări *după*.
