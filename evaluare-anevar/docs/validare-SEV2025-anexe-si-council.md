# Validare SEV 2025 — anexe obligatorii + verificare feedback council vs. standard

> Verificare cerută de Adi (cu feedback Google) pe `md files/standardele-de-evaluare-a-bunurilor-2025.md`
> (14.034 linii) + celelalte `.md`. Întrebări: (1) sunt OK cu opinia council-ului că anexele foto/documente
> sunt obligatorii? (2) mai e vreun feedback council care contrazice logica noastră? (3) ceva NOU vs. ce avem/planificăm?

## 1. Anexele foto + documente — DA, council-ul are DREPTATE (cu o corecție de citare)
**Verdict: sunt de acord cu council-ul — anexele (fotografii + extras CF/cadastral + fișe) sunt cerință de
conformitate, NU feature comercial.** Dovezi din chiar standardul oficial:
- **GEV 630 (Evaluarea bunurilor imobile)** — ghidul operativ RO pentru imobile: lista de conținut a raportului
  include explicit „**Anexele raportului de evaluare (Fișe clădiri, fotografii etc.)**" (linia 5645). Secțiunea
  „Culegerea datelor și descrierea proprietății imobiliare" (§16-29) + „Raportare" (§110-112) cer inspecție + probe.
- **Inspecție + fotografii:** „evaluatorul trebuie să inspecteze... va prezenta în raportul de evaluare **fotografii
  din exterior**. Neinspectarea... va fi justificată" (linia 4079). Memoria proiectului confirmă: *„GEV 630 mandates
  physical building inspection with photographic and documentation annexes"*.
- **SEV 230 §120 „Documentare și raportare"** (specific imobile) + **SEV 106 §30.6(l)** („sursele utilizate și modul
  de selectare a informațiilor") cer documentarea probelor care susțin valoarea.

**Corecție de citare (important):** feedback-ul Google citează „**SEV 102 Documentare și conformare**" — aceasta e
**numerotarea VECHE**. În SEV **2025** standardele au fost **renumerotate**: „SEV 102" e acum *„Tipuri ale valorii"*,
iar documentarea/raportarea e în **SEV 106** (fostul SEV 103) + SEV 230 §120 + **GEV 630** (operativ). Substanța
afirmației Google e corectă; doar numărul standardului e depășit. Concluzia practică e identică: **fără anexe, raportul
e incomplet/neconform** pentru bancă/ANAF/instanță.

**Consecință pentru noi:** decizia noastră de a trata atașarea foto/scanuri ca **feature comercial** intră în conflict
cu conformitatea SEV. **Recomandare (escaladată în [`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md) §C2, pct. 24):** suportul de
atașare anexe = **P0 de conformitate** în UI nou; gating doar pe VOLUM (ex. 10-20 poze gratis), nu pe existență.
*Notă de guvernanță:* e materie de metodologie/conformitate (bucket B) — eu doar construiesc suportul de atașare;
pragurile/volumul le confirmi tu/un evaluator.

## 2. Alt feedback council care contrazice logica noastră? — NU, cu o nuanță confirmată
- **Preț-total vs €/mp (council #1):** am verificat — standardul (GEV 630 §44-58, abordarea prin piață) **NU impune**
  literal €/mp; e uzanță de verificare bancară. Auditul meu anterior se confirmă: e problemă de **formă** (prezentare),
  nu de fond; abordarea noastră „alertăm, nu blocăm" rămâne corectă. **Niciun contraziceri de fond.**
- **Selecția pe ajustare brută totală (council #1):** aliniată cu SEV 230/GEV 630 (minimizarea ajustărilor) — o adoptăm.
- **Consistență cost↔piață, AML, GDPR:** nimic în standard nu contrazice gardurile noastre (sunt alerte, nu modifică formula).

## 3. Ceva NOU identificat în `md files/` vs. ce avem/planificăm
| Element | Unde | Statut la noi | Recomandare |
|---|---|---|---|
| **Anexe foto/documente obligatorii** | GEV 630, l.5645/4079 | gated comercial (greșit) | **Re-încadrare P0** (vezi §1) |
| **SEV 400 „Verificarea evaluării"** (serviciu separat: un verificator EPI verifică raportul altui evaluator; proces vs. valoare) | standard l.123/361 | **nu îl avem** | Modul ADIACENT viitor (nu e în scopul MVP garantare); de notat în backlog |
| **Studiu de piață pt. „valori minime" impozitare** (hcd-74: evaluatorii depun anual valorile minime pe piață) | anexa-hcd-74 | **nu îl avem** | Deliverable DIFERIT (anual, impozitare), nu raport individual; out-of-scope MVP, posibil modul viitor |
| **Valoarea de lichidare — definiție SCHIMBATĂ în 2025** (Anexă A60) | standard l.224 | notat „factor lichidare" bucket B (council #1) | Relevant la GEV 520 garantare; rămâne decizie evaluator |
| **GEV 500 Anexa 4 modificată** (clădiri nerezidențiale, impozitare) | standard l.299 | avem framing GEV pe scop | irelevant pt. garantare rezidențială; OK |
| **ESG ca dată de intrare în raport** (SEV 106 §30.6(m): „factori de mediu, sociali și de guvernanță") | standard l.2566 | avem mențiune ESG în raport | de verificat că secțiunea ESG e prezentă (avem deja) |

**Concluzie §3:** nimic care să ne răstoarne logica de bază. Singurul impact REAL imediat = **anexele foto/documente**
(confirmat de standard, nu doar de council). Restul (SEV 400 verificare, studiu valori minime) = module adiacente
viitoare, în afara scopului MVP de garantare. „Valoarea de lichidare" + ESG = deja pe radar.

## 4. Ce fac eu de aici (autonom) vs. ce decizi tu
- **Autonom:** construiesc suportul de **atașare anexe** în UI nou (sub-tab Anexe: Foto + Documente, stocate în
  `dosare/{uuid}/anexe/`, thumbnail, legendă, compresie) — DAR aștept confirmarea ta pe **re-încadrare** (era decizia ta
  „comercial"). Adaug SEV 400 + studiu-valori-minime în backlog ca module adiacente.
- **Tu decizi:** re-încadrarea anexelor (P0 conformitate vs. comercial-pe-volum) — [`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md) §C2.
