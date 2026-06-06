# 00 · SINTEZĂ pentru Adi — drumul către lansarea pe piață (citește asta ÎNTÂI)

> Sesiune autonomă de noapte, 2026-06-06. Acesta e documentul-umbrelă: îți spune **ce să
> citești**, **opinia mea agregată** (am auditat și consiliul LLM, și propriile mele analize),
> și **lista unică la care să spui «DA»**. Detaliile sunt în documentele țintă de mai jos.
> Partea de marketing e exclusă intenționat (nu e scopul exercițiului).

---

## 0. Harta documentelor (toate noi, din noaptea asta)

| Vrei să… | Citește |
|----------|---------|
| Vezi planul de lansare + auditul consiliului LLM + „Spune DA" în 13 pași | [`plan-lansare-piata.md`](plan-lansare-piata.md) |
| Decizi pe comercial: admin, update, crash-telemetrie, preț, „nu înlocuim evaluatorul" | [`strategie-comercializare-intrebari.md`](strategie-comercializare-intrebari.md) |
| Vezi riscurile juridice + documentele legale (RO) | [`legal/00-evaluare-juridica-RO.md`](legal/00-evaluare-juridica-RO.md) + `legal/10..14-*-DRAFT.md` |
| Vezi ce am livrat azi-noapte pe produs + deciziile de UI | [`plan-maine-2026-06-06.md`](plan-maine-2026-06-06.md) |
| Vezi feature-urile majore + dependențele | [`features-majore-pending.md`](features-majore-pending.md) |

**Documente juridice DRAFT produse** (toate marcate „necesită avocat RO"): Termeni & Condiții,
Politică de confidențialitate (GDPR), EULA, **DPA art. 28**, Disclaimer profesional. → `docs/legal/`

---

## 1. Opinia mea agregată (am auditat consiliul ȘI propriile analize)

**Verdict într-o frază:** produsul tehnic e gata și solid (473 teste + 49 e2e, 8 garduri verificate
în cod, exe 50 MB); ce te oprește de la lansare **nu e cod**, ci **3 validări umane** (evaluator,
jurist AML, jurist GDPR) + **2 decizii de conformitate** (kill-switch de versiune, screening AML).

**Unde consiliul LLM a avut dreptate** (confirm independent, am recitit cele 1055 de linii):
- ✅ **Selecția comparabilei pe «ajustare la proprietate» în loc de «brută totală»** — eroare reală
  de fond; un verificator de bancă o penalizează. Merg mai departe decât panelul: schimbă **criteriul
  de selecție**, nu doar afișarea. (Necesită confirmarea evaluatorului — schimbă valori pe dosare.)
- ✅ **Consistența cost↔piață** (deprecierea implicită de 29% pe Breaza) — cea mai bună observație din
  review, derivată din **datele tale reale**. Gardul de alertă pe care l-ai pus deja e răspunsul corect.
- ✅ **AML** — risc serios; auditul juridic e blocant absolut.

**Unde consiliul a greșit / a exagerat** (și sunt de acord cu propriul meu agent care a prins asta):
- ⚠️ **Preț-total vs €/mp ridicat la «red flag critic»** = artefact de chairman. 3 din 4 membri au
  spus că e **matematic echivalent**. E o problemă de **formă** (prezentare pentru verificatorul de
  bancă), nu de fond. Fix ieftin (un strat de afișare €/mp), nu rescriere de motor.
- ⚠️ **Consiliul a citit o stare veche**: a vorbit de exe 176 MB (acum **50 MB**) și de riscul cloud-sync
  (deja gestionat în cod, fallback `%LOCALAPPDATA%`). Ai grijă să nu acționezi pe premise expirate.
- ⚠️ **A ratat AI Act-ul** (Reg. UE 2024/1689) și **update-ul-ca-risc-de-conformitate** — ambele apar
  acum în docs/legal + plan-lansare.

**Ce subevaluează TOATĂ lumea (opinia mea proprie, peste consiliu și peste agenții mei):**
1. **Transferul de răspundere e și scut juridic, și propunere de valoare — și trăiește în UI, nu în
   disclaimer.** „Omul în buclă" te protejează legal DOAR dacă momentul în care evaluatorul își asumă
   valoarea e **explicit în interfață** (un pas de confirmare/semnătură la «Generează»), nu doar scris
   în Termeni. Recomand: la generarea raportului, un checkpoint „confirm că am verificat și îmi asum
   valoarea X" — un singur element de UI care servește simultan juridicul (§00-evaluare-juridica риск
   #3) și filozofia „nu înlocuim evaluatorul".
2. **Cea mai serioasă obiecție de fond a fost îngropată:** ajustarea de suprafață **liniară** (Δmp×preț)
   e greșită economic la diferențe mari (mp-ul marginal e **degresiv**). E mai importantă decât
   preț-total-vs-€/mp și e corect pusă ca item de validat cu evaluatorul.
3. **Validează ÎNAINTE de a construi infrastructura** (sunt total de acord cu agentul de strategie):
   planul comercial construiește gateway+Stripe pentru **0 clienți validați**. Inversează ordinea —
   5 evaluatori reali pe exe gratuit întâi. Partea tehnică e ~80% gata; partea **comercială**
   (adopție, încredere, suport, churn, canal) e subdezvoltată.

**Out-of-the-box pentru ce urmează** (mindset implicit + lateral):
- **Metrica-far = «timp economisit», afișată discret în app** („ai economisit ~3,5h pe acest dosar").
  Construiește narativa de valoare care justifică prețul pe valoare ȘI întărește „instrument, nu
  înlocuitor". Ieftin de pus, greu de copiat ca poziționare.
- **Termen mediu: «sistem de operare al dosarului»**, nu „generator de raport". Arhitectura
  folder=adevăr + versiuni + import + audit-trail (deja construită) te poziționează pentru
  versionare/predare la peer-review/istoric — un șanț competitiv dincolo de narativul AI.

---

## 2. Ce e GATA / ÎN LUCRU / PLANIFICAT / NEPLANIFICAT (agregat)

- **(A) GATA:** motorul de calcul + grile + AML + GDPR + raport .docx; **noul UI output-first**
  (cont→ÎNCEPE→workspace) funcțional; import .docx; audit portaluri + fixuri; 8 garduri post-council;
  exe 50 MB; 473 teste + 49 e2e. Documente juridice DRAFT + planuri de lansare/strategie (azi-noapte).
- **(B) ÎN LUCRU (cod, îl fac eu autonom):** acoperire teste (generator/ocr), tab GDPR distinct,
  e2e extensie; cele 8 items din [plan-maine §F].
- **(C) PLANIFICAT (din topicuri abordate, așteaptă decizie):** identitatea dosarului + lock (#1/#2);
  regenerare text AI (B) + import asemănător (D); gateway comercial (#4); localități user (#3).
- **(D) NEPLANIFICAT dar recomand:** checkpoint de asumare în UI (vezi §1.1); metrica „timp economisit";
  telemetrie crash opt-in; auto-update semnat; poziționarea „dossier OS".

---

## 3. Lista UNICĂ la care spui «DA» (consolidată din toate documentele)

> Dedupată din: `plan-lansare-piata.md` (13 pași), `strategie-comercializare-intrebari.md` (decizii),
> `legal/00` (must-decide avocat), `plan-maine §B` (decizii UI). **Marcaj:** 🧑 = doar tu poți decide ·
> 🤖 = îl pot face eu pe cod după ce confirmi.

### Poarta 0 — Validări externe (drumul critic; pornesc ACUM, în paralel; materialul e deja scris)
1. 🧑 Trimite `audit-aml-pentru-jurist.md` unui **avocat AML** (Legea 129). **BLOCANT ABSOLUT.**
2. 🧑 Trimite `protocol-peer-review-evaluator.md` la **2-3 evaluatori seniori** (validează premisa produsului).
3. 🧑 Dă `legal/*` + `gdpr/*-MODEL.md` unui **jurist GDPR** (confirmă: DPA, transfer LLM extra-UE, AI Act).
4. 🧑 Trimite `pachet-validare-banci.md` + raport demo la **2-3 bănci**.

### Poarta 1 — Garduri de conformitate (le fac eu; tu confirmi/cumperi)
5. 🤖 **Dezactivează RTS/RTN by default** până la auditul AML (activare explicită după).
6. 🤖 **Notificare de versiune obligatorie / kill-switch** reglementar (~1 zi).
7. 🤖 **Checkpoint de asumare în UI la «Generează»** (semnătură evaluator — juridic + filozofie). *(nou, recomandarea mea §1.1)*
8. 🧑 **Cumpără certificat code-signing** (~150-300 €/an) — fără el, SmartScreen sperie profesioniștii.

### Poarta 2 — Aplici ce decid experții (gated de Poarta 0)
9. 🤖 Răspunsurile evaluatorilor (B1-B8: €/mp prezentare, **selecție pe brută totală**, **ajustare degresivă**, lichidare, risc garanție).
10. 🤖 Răspunsurile juristului AML (prag numerar, screening live vs. dezactivat) + ale juristului GDPR (DPA, SCC, AI Act).

### Poarta 3 — Comercializare (după ce produsul e validat; validează ÎNAINTE de a construi)
11. 🧑 **Validează cu 5 evaluatori reali pe exe gratuit** ÎNAINTE de a construi gateway/Stripe (recomandarea mea + a agentului de strategie).
12. 🧑 Creezi conturile externe (Supabase/Google/Stripe — Faza 0).
13. 🤖 Construiesc MVP gateway + **telemetrie crash opt-in** + **auto-update semnat** + master-admin (Supabase Studio, nu panou custom la <20 useri).

### Decizii de produs (din plan-maine §B — le tranșăm la brainstorm #1, nu blochează lansarea)
14. 🧑 Ordine creare dosar · blocare identitate · import .docx vs folder · format-nume vs identitate · monedă EUR la garantare · Calcul→Generează o singură sursă.

---

## 4. Ce decizi DOAR tu (rezumat absolut)
1. **Pe cine** trimiți la peer-review / jurist AML / jurist GDPR (drumul critic — terți, asincron).
2. **Screening AML:** API live (OpenSanctions) vs. dezactivare cu trimitere la surse oficiale.
3. **Code-signing:** cumperi acum (~200 €/an) sau lansezi cu disclaimer SmartScreen.
4. **Ordinea comercială:** validezi cu evaluatori reali ÎNAINTE de a construi infrastructura? (recomand: DA).
5. **Preț:** treaptă unică la lansare; recomand **pe valoare, mai sus** (testează Pro la 299-399 lei/lună) — detalii în `strategie §5`.

> **Dacă spui «DA» la structura de mai sus**, eu pornesc imediat: pașii 🤖 5,6,7,13(telemetrie) +
> continui lista de cod sigură din plan-maine §F. Pașii 🧑 sunt drumul critic și depind de tine —
> de aceea Poarta 0 trebuie pornită în prima ta zi (validările durează la terți, nu la mine).
> **Regula de aur, respectată peste tot:** aplicația **avertizează**, nu decide; metodologia și
> pragurile legale **nu se ating** fără semnătura unui evaluator senior / jurist.
