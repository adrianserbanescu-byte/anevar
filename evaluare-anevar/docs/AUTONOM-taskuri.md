# 🤖 Listă de taskuri autonome (citită + actualizată la fiecare loop)

> **Protocol loop (instrucțiune Adi):** la fiecare job de loop → (1) actualizez ÎNTÂI lista de mai jos,
> (2) aleg și rezolv tot ce pot face singur (fără input de la Adi), (3) la următorul loop reiau.
> Ce e blocat pe Adi → [`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md) (NU le ating). Actualizat: 2026-06-06.

## 🔄 BLOCAT EXTERN — MCP llm-council offline (la fiecare loop: verific statusul; dacă e UP, rulez ÎN ORDINE)
> Adi (2026-06-06): „retry at the loop the council status; if yes resume Q2 & Q3 then the additional one".
> NU rula council acum în interacțiune — DOAR la loop, după ce verifici că `mcp__llm-council__ask_council` există.

1. [ ] **Council Q2** (topics 3,4,6 — funcții AI + conținut workspace). `include_member_responses=true`.
2. [ ] **Council Q3** (topics 2,8,9 — paritate + descoperire + localități). `include_member_responses=true`.
       → foldez Q2+Q3 (chairman + individual + analiza mea) în `9-topicuri-decizie.md`.
3. [ ] **Council ADIȚIONAL — „planul lor pentru noul UI"** (cerere Adi, verbatim mai jos):
       „rulează încă un llm-council audit în care ceri planul lor pentru noul UI și cum ar trebui să îl
       definim. Poți să le dai contextul de până acum discutat, dar cere-le să îți facă planul lor INDIVIDUAL.
       În afară de contextul exhaustiv asupra proiectului, dă-le toate informațiile despre: **fișiere exportate**,
       **descoperire și cum funcționează + AI**, **vechiul UI**, **toate feature-urile aplicației** și **obiectivele
       setate de noi**. Cere-le planul și detalierea lor, **riscuri și dependențe**. Compară output-ul fiecăruia
       cu al meu ȘI output-ul agregat al lor vs. opinia mea. Preia ce consider potrivit în planul meu de dezvoltare."
       → `include_member_responses=true`; rezultat în `docs/council-plan-UI-nou.md` + integrare în planul de dezvoltare.

## ✅ Făcut în acest loop
- [x] **Analiza mea pe toate 9 topicuri** + council Q1 → `9-topicuri-decizie.md`.
- [x] **Widget feedback** verificat: lipsea din tot UI-ul nou (era doar în `_topbar`) → mutat în `_footer` comun
      (apare pe toate paginile, vechi+nou). +test. Restul linkurilor neafectate.
- [x] **Fișier de sinteză a nopții** → `00-SINTEZA-NOAPTE-2026-06-06.md`.
- [x] Polish auto-safe: badge „recomandat" verde + aria-hidden emoji (index).
- [x] Listă autonomă creată (acest fișier) + checkpoint durabil la restart.

## ☐ Datorie tehnică autonomă (din auditul tehnic; le pot face fără decizie de produs)
- [ ] `listeaza()` — cache pe mtime via `_index.json` (evită rescanarea N fișiere la fiecare /incepe).
- [ ] Îngustez `except Exception` prea largi + logging (docx_dosar, dosare_fs.diff).
- [ ] Retenție versiuni `.docx` în folderul dosarului (acum cresc nelimitat).
- [ ] Nume fișiere temporare unice (uid+timestamp) în `gettempdir()` (evită coliziuni).
- [ ] Extind avertismentul cloud-sync să acopere și `date/dosare/`.

## ☐ Acoperire teste (țintă ≥90%, urc golurile cunoscute)
- [ ] `report/generator` (~88%) — secțiuni rare (lichidare/DCF).
- [ ] Ramuri de eroare neacoperite în `documente.py` (deja 9 teste; verific liniile lipsă).

## ☐ Polish UI auto-safe (din audituri, fără decizie de produs)
- [ ] Badge „recomandat" pe index → verde (`b-high`) în loc de chihlimbar.
- [ ] Câteva mesaje de eroare cu ghidaj (UX-copy: „Generarea a eșuat" → ce + cum repar).
- [ ] `aria-hidden` pe emoji din `index.html`/documente unde lipsește.

## ✅ Rezolvate în această sesiune de noapte (rezumat — detalii în sinteza nopții)
- Noul UI „output-first" complet (cont→ÎNCEPE→workspace) + import .docx + cont „Adi S" + 4 dosare exemplu.
- Index de alegere UI + pagină Documente (convertor MD→HTML propriu) + cross-linkuri antet/subsol.
- Audit import portaluri (live, 2 fixuri) + 5 audituri (a11y/UX/design/tehnic/cod) → 8 fixuri auto-safe.
- Checkpoint de asumare (om în buclă) în Generează. Calcul fără persistență SQLite (rând orfan reparat).
- Pachet lansare: sinteză + plan-lansare + strategie + evaluare juridică RO + 5 documente DRAFT.
- 2× LLM council (review #1 stare veche + #2 stare curentă pe decizia de lansare).
- 487 teste + 57 e2e, exe 50 MB, tot pe GitHub.
