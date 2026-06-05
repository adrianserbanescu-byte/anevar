# #4 — Comercializare: tool local premium cu AI metrat

Status: **brainstorm complet** (2026-06-06). Următorul pas: plan de implementare (când se decide).
Proiect mare, separat de app-ul desktop — necesită infra externă (cloud, Stripe, Google OAuth).
Logic, vine **după** review-ul cu evaluatorul.

## Viziune
Aplicația rămâne **tool desktop local/offline** vândut **evaluatorilor individuali** ANEVAR.
Ambiție: mic, mentenanță redusă, venit recurent suplimentar.

## Arhitectură
```
APP DESKTOP (offline)            ──HTTPS, doar date anonimizate──▶   AI GATEWAY (online, al tău)
• calcul, grile, AML, GDPR                                          1. autentifică contul (Google)
• asamblare raport .docx                                           2. validează sesiunea
• narativ ȘABLON (gratis)                                          3. verifică cota
• login + token semnat (grație offline)        ◀──narativ AI──     4. cheamă LLM cu CHEIA TA
• TOT clientul rămâne local                                        5. scade 1 raport + log facturare
```
- **Local (mereu funcțional, offline):** date client, calcule, grile, AML, GDPR, `.docx`,
  narativ-șablon. Fără internet → tot iese un raport complet (fără lustruirea AI).
- **Gateway (online, doar la „Generează AI"):** primește doar text **anonimizat**, cheamă AI-ul
  cu cheia ta, metrează. E și motorul de **licențiere** (exe copiat fără cont = fără AI).

## Metrare (busola: metrezi DOAR ce te costă — apelul LLM; tot ce e local e gratis)
- **Unitate facturată = 1 narativ AI per dosar** (nu fișierul `.docx`).
- `.docx` re-descărcat, editări, recalcule, AML, GDPR, audit, raport-șablon = **gratis, nelimitat**.
- **Cache:** narativul se reține în dosar → regenerare `.docx` după modificări minore = gratis.
- **Fereastră de grație:** re-rulări AI ale aceluiași dosar (ex. 48h / primele 2-3) = gratis.
- **Descoperirea** (verificare atribute secundare per anunț) + derivarea zonei = AI mic, **inclus
  gratis** (cost neglijabil; monitorizat, plafonat doar dacă apare abuz).

## Costuri reale (din consum real Perplexity)
- ~**$0.005/apel** (≈ jumătate de cent). Un raport „bogat" (narativ ~6-7 + descoperire ~8-12 +
  zonă ~1) ≈ **$0.08-0.10**; raport „slab" (comparabile manuale) ≈ **$0.035**.
- COGS per evaluator activ: ~**$2-3/lună** (30 rapoarte), ~$8 la 100. **Neglijabil.**
- Implicație: **cota nu acoperă cost (e ~zero) — e pentru tiering + anti-abuz.** Poți fi generos.

## Prețuri (indicative — DE VALIDAT cu 5-10 evaluatori)
Ancoră de valoare: raport manual = **4h (senior) → 8h (junior)**; tool → ~1-1.5h ⇒ economie
**2.5-6.5h/raport** ≈ **350-490 lei/raport** valoare. Clientul final plătește 400-1.500 lei/raport.

| Treaptă | Preț/lună | Rapoarte AI | Pentru cine |
|---|---|---|---|
| Solo | ~99 lei (€20) | 10 | volum mic |
| Pro | ~199 lei (€40) | 40 | evaluator activ |
| Nelimitat | ~349 lei (€70) | fair-use ~150 | foarte activ |
| Pachet extra | ~49 lei | +10 | depășiri |

Plus: **plan anual −2 luni**; **trial 14 zile** sau primele 3 rapoarte AI gratis (restul merge
oricum în trial). Marjă ~80-95%. Risc real = **adopția**, nu costul → mesaj central: „economisești 3h/raport".

## Autentificare
- **Google Sign-In** (principal): auto sign-in (refresh tăcut), zero parole stocate, identitate
  reală. Flux desktop: app deschide browserul → autorizezi → revine pe `localhost`. Abonament
  Stripe legat de emailul contului.
- **Fallback: email „magic link"** (fără parolă) pentru cine nu vrea Google.

## Enforcement licență (1 licență = 1 utilizator)
- **2 sesiuni concurente** permise (laptop + desktop, fără să se scoată reciproc).
- Sesiunile se țin în **baza gateway-ului** (nu RAM — serverless). Login nou peste limită →
  cea mai veche sesiune e invalidată.
- **La fiecare apel AI**, app-ul trimite tokenul; gateway-ul verifică sesiunea activă:
  validă → rulează; înlocuită → respinge cu „Ai fost deconectat — cont folosit pe alt dispozitiv".
- **Cotă** = plasă de siguranță (partajarea consumă mai repede). **Nelimitat** se bazează pe
  legarea de sesiune.
- **Grație offline:** token de drept semnat valid 7-14 zile → app merge offline; re-validează
  când prinde net. La expirare blochează **doar AI-ul** (restul rămâne citibil).
- **Semnale soft:** gateway loghează IP/oră → pattern suspect = flag pentru review manual, NU
  ban automat (evaluatorii călătoresc).
- Onest: piratarea 100% nu se poate; ținta = partajarea ocazională între colegi, care devine
  inutilă (te scoate din cont + fracțiune de cotă).

## Stack (mentenanță mică)
**Supabase** (auth Google + magic-link + Postgres) + **Stripe** (Checkout + Customer Portal) +
o **funcție edge** = proxy AI. Tu scrii doar proxy-ul AI + 2-3 ecrane. Restul e gata făcut.

## MVP (faza 1 — primul leu)
1. Gateway: login Google, tabel sesiuni (max 2), tabel cotă, proxy AI (validează→verifică→cheamă
   →scade→log), Stripe Checkout (1 treaptă) + webhook.
2. App: ecran login, stocare tokeni + token de drept, **rutează narativul + descoperirea prin
   gateway**, afișează cota + mesaje (limită/sesiune).
3. Mini-landing cu abonare (Stripe Checkout găzduit).

## Roadmap
| Fază | Ce | Scop |
|---|---|---|
| 0 (acum) | app la review (fără comercializare) | feedback |
| 1 — MVP | 1 treaptă + Google + metrare + Stripe | primul leu + validare 2-3 plătitori |
| 2 | trepte + pachete + magic-link + plan anual + UI cotă | scalare |
| 3 | gestionare sesiuni, semnale anti-abuz, canal update-uri | maturizare |

## Confidențialitate / GDPR / legal (de aprofundat la implementare)
- Gateway-ul vede **doar date anonimizate** → argument de vânzare + GDPR mai simplu.
- Termeni de serviciu, politică de date, facturare RO (TVA), reguli ANEVAR privind tool-uri
  comerciale — de verificat cu jurist/contabil (bucket C).

## Decizii luate / rămase
- ✅ tool local premium · ✅ gateway online acceptat · ✅ metrare per raport · ✅ abonament
  tot-în-unu · ✅ Google auth + email fallback · ✅ 2 sesiuni concurente.
- ⏳ DE VALIDAT: pragurile de preț exacte (cu evaluatori reali); termeni legali; alegere finală
  de provider cloud.
