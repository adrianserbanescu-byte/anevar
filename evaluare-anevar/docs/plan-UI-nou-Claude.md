# Planul meu (Claude) pentru noul UI — cum ar trebui definit

> Planul MEU independent, de comparat cu cel al fiecărui model din council (când revine MCP-ul) +
> cu agregatul lor. Vezi cererea în `AUTONOM-taskuri.md` pkt. 3 și brieful în `council-brief-UI-nou.md`.
> Ancorat în: council Q1 (topics 1,5,7), cele 5 audituri, `9-topicuri-decizie.md`, obiectivele proiectului.

## Principiu director
Noul UI servește **un singur scop**: să ducă evaluatorul de la „am un client + o proprietate" la „am un
raport `.docx` conform, pe care îl semnez și îl asum", cu **minimum de fricțiune** și **maximum de trasabilitate**.
„Output-first" = navighezi după **livrabil** (Raport/AML/GDPR/Audit/Anexe), nu după pași de wizard. AI-ul atinge
DOAR proza; toate numerele rămân deterministe și etichetate ca atare.

## 1. Structura de pagini (propunerea mea)
```
/            → Alegere interfață (nou vs wizard) — tranzitoriu, până retragem wizardul
/cont        → Cont evaluator (identitate + format nume dosar) — o singură dată
/incepe      → Hub: 5 acțiuni + lista dosarelor (din diff foldere)
/dosar/{uuid}→ Workspace = inima aplicației (tab-uri output + sub-tab-uri de lucru)
/documente   → Toate documentele (juridice/strategie) — offline
```
**Decizie:** păstrez `/` ca selector DOAR cât timp coexistă wizardul; după retragere, `/` → `/incepe`.

## 2. Workspace-ul dosarului (cel mai important)
**Tab-uri output (rândul de sus):** `[📄 Raport] [🛡 AML] [🔒 GDPR] [🧾 Audit] [📎 Anexe]`.
**Sub-tab-uri Raport (fluxul de lucru):** `[Proprietate] [Comparabile] [Calcul] [Generează]`.

Reguli de conținut (rezolvă Topic 6 — inline vs link, fără aglomerare):
- **Raport** = locul unde introduci date + generezi. Restul tab-urilor = **stare + acces**, nu re-introducere.
- **AML:** badge de stare risc (verde/galben/roșu) calculat din dosar + buton „deschide AML" (detaliu).
- **GDPR:** stare consimțământ (bifă) + linkuri la politică/disclaimer (deja). 
- **Audit:** **urma de calcul inline** după Calcul (trace determinist = „output-ul" care justifică valoarea) — asta
  e diferențiatorul „output-first": auditul nu e un placeholder, e dovada.
- **Anexe:** foto + scanuri. **Atașarea de fișiere = gated comercial** (decizia ta) → acum doar listează ce s-a
  atașat la import (.docx) + ingestie PDF.

## 3. Identitatea dosarului (Topic 1 — aliniat cu council Q1)
- Identitate „tare" = `(scop, tip_proprietate, COD FISCAL client [CNP/CUI], județ, localitate)`. **Numele
  clientului NU e identitate** (variații) — e editabil. Ancora = codul fiscal.
- **Lock la prima generare `.docx` reușită** (nu la draft/calcul — permite calibrare).
- Schimbarea unui câmp „tare" → dialog „DOSAR NOU; clonez datele tehnice + comparabilele?". Clonarea care
  **păstrează munca** e cheia care face rigiditatea acceptabilă.
- Corectură tipografică (nume/adresă non-identitate) → permisă oricând, **înregistrată în Audit**.
- **Dependență:** declanșatorul exact de lock = decizia ta (BLOCAT #10). Restul îl pot construi.

## 4. Fluxul Calcul → Generează (Topic 7 — aliniat cu council Q1; parțial implementat)
- Sursă unică de valoare = rezultatul Calcul salvat în `dosar.json` (`calcul_final` + timestamp + **hash input**).
- «Generează» blocat până: (a) Calcul valid salvat, (b) checkbox de asumare bifat (✅ deja). 
- Orice input modificat după Calcul → status „perimat" + banner roșu „recalculează" (diff timestamp).
- Etichetare: `[Determinist]` pe numere (cu hash pt reproducibilitate SEV), `[Asistență AI]` pe proză;
  marcajele AI vizibile în UI, **dispar în `.docx` semnat** (evaluatorul asumă integral).

## 5. Descoperire integrată (Topic 8)
- Mut descoperirea în **sub-tab-ul Comparabile** (acum trimite în pagină separată). Cauți → bifezi candidați →
  intră direct în grilă (construcție/teren). imobiliare+storia primare; OLX best-effort cu „completează suprafața".
- Călire: filtru de categorie la extragerea listei (taie promovatele cross-categorie). Audit live înainte de release.

## 6. Paritate cu wizardul (Topic 2) — prerequisit pentru retragerea UI vechi
Ordine: (a) grila teren ✅ făcut; (b) chirii→venit/DCF (metodă avansată, progressive disclosure); (c) anexă
foto/documente (gated comercial). Fără paritate completă, **nu** retragem wizardul.

## 7. Retragerea UI vechi (Topic 5 — aliniat council Q1)
Migrare unidirecțională SQLite→foldere în 3 faze (~6 luni): coexistență → buton „Migrează în folder" per dosar
vechi + feature-freeze wizard → wizard read-only, apoi scos din meniu. Script ne-distructiv + log.

## 8. Riscuri (planul meu)
| Risc | Mitigare |
|------|----------|
| Workspace aglomerat (tab-uri pe jumătate goale) | inline doar ce are conținut real; restul = stare + link |
| Lock-ul de identitate frustrează | clonarea-care-păstrează-munca + corectură tipografică în Audit |
| Drift schemă JS `asambleaza()` ↔ Python `EvaluationInput` | pe termen mediu: endpoint care întoarce schema / generare din Pydantic |
| Migrarea SQLite→foldere pierde anexe | ne-distructiv + log + skip-pe-eroare + SQLite read-only ca failback |
| „Output-first" percepută ca AI decide valoarea | etichetare [Determinist]/[AI] + checkpoint asumare (✅) |

## 9. Dependențe
- **Decizii Adi (BLOCAT-pe-Adi.md):** declanșator lock (#10), retragere wizard (#18), anexă foto (gated), localități #3.
- **Council Q2/Q3 + plan-UI** (la reconectare) — pentru rafinare topics 2,3,4,6,8,9.
- **Brainstorm #1** (identitate) deblochează metrarea comercială (#4).

## 10. Ordinea pe care o propun (ce fac eu autonom vs ce te așteaptă)
1. **Autonom acum:** Topic 7 (persist calc + banner perimat + etichetare AI/determinist), Topic 8 (descoperire în
   sub-tab + călire), Topic 2b (venit/DCF în UI nou).
2. **După decizia ta:** lock identitate (#10), migrare/retragere wizard (#18), anexă foto, localități.
3. **După council:** rafinez topics 3/4/6 (regenerare AI, import asemănător, conținut tab-uri).
