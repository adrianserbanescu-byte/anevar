# 🤖 Listă de taskuri autonome (citită + actualizată la fiecare loop)

> **Protocol loop (instrucțiune Adi):** la fiecare job de loop → (1) actualizez ÎNTÂI lista de mai jos,
> (2) aleg și rezolv tot ce pot face singur (fără input de la Adi), (3) la următorul loop reiau.
> Ce e blocat pe Adi → [`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md) (NU le ating). Actualizat: 2026-06-06.

## 🔄 În curs (checkpoint — app-ul s-a restartat în timpul council-ului)
- [ ] **9 topicuri → LLM council în 3 interogări** (feature/module): Q1 ✅ (topics 1,5,7 — făcut, am salvat răspunsurile),
      Q2 ⏳ (topics 3,4,6 — întrerupt de restart, de reluat), Q3 ☐ (topics 2,8,9).
- [ ] **Sinteză 9 topicuri**: direcție propusă + plan, cu analiza individuală + agregată a council-ului + opinia mea.
- [ ] **Council ADIȚIONAL** (cerut de Adi): cere fiecărui model PLANUL LUI pentru noul UI (context exhaustiv:
      fișiere exportate, descoperire+AI, UI vechi, toate feature-urile, obiective). Compar cu planul meu + agregat.
- [ ] **Widget feedback**: verific că a supraviețuit în tot noul UI; sigur era în subsol — dacă nu e și în antet, îl adaug.
- [ ] **Fișier de sinteză a nopții**: tot ce am făcut singur + ce s-a identificat + recomandări + ce s-a rezolvat +
      cum am implementat planificarea + cât am folosit din feedback-uri.

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
