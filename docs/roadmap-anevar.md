# Roadmap produs — Asistent de evaluare ANEVAR (casă + teren, garantare credit)

**Data actualizării:** 2026-06-03
**Driver:** cercetare pe anevar.ro (standarde SEV 2025, GEV 520, baze BIG/BIF, Indicele imobiliar,
Legea 129/2019 AML, IROVAL). Format: **Now / Next / Later** (evită falsa precizie a datelor).

---

## Status overview (ce e DEJA funcțional)

| Componentă | Stare |
|---|---|
| Motor cost CIN segregat (IROVAL-style) | **Done** — validat pe model real |
| Grilă teren (2 etape) + grilă casă (preț total) | **Done** — validate pe 4 dosare reale GBF |
| Reconciliere + alocare valoare | **Done** |
| Raport .docx (shell GBF + 7 capitole + GEV 520 + anexe + foto) | **Done** |
| Narativ AI (anonimizat GDPR) | **Done** |
| Descoperire comparabile (imobiliare/storia) + extragere structurată | **Done** |
| Wizard 5 pași + exe onefile | **Done** |

---

## Constatări ANEVAR care schimbă prioritățile (informația nouă)

1. **SEV 2025 în vigoare de la 1 iulie 2025** (HCN nr. 2/2025), aliniat la numerotarea **IVS**:
   IVS 103 (Abordări), IVS 105 (Modele), **IVS 106 (Documentare și raportare)**, IVS 400 (Drepturi
   imobiliare). → terminologia raportului (acum „SEV 103/104/105") poate fi neactuală.
2. **GEV 520 — Evaluarea pentru garantarea împrumutului** = exact scopul aplicației → secțiunea de
   risc trebuie aliniată la conținutul obligatoriu al ghidului 2025.
3. **BIG (Baza Imobiliară de Garanții)** — baza ANEVAR cu date din rapoarte reale **de garantare**;
   sursa cea mai autoritară de comparabile pentru cazul nostru (azi folosim portaluri publice).
4. **Indicele imobiliar ANEVAR** — dinamica valorilor/mp → input direct pentru ajustarea
   „condițiile pieței (timp)" din grile.
5. **Legea 129/2019 (AML)** — evaluatorul e entitate raportoare: KYC, beneficiar real, screening
   sancțiuni/jurisdicții necooperante, raportarea tranzacțiilor suspecte. Azi neacoperit.
6. **Constrângere ANEVAR:** studiile de piață / anunțurile nu pot fi singura sursă de valori de
   referință → comparabilele descoperite trebuie marcate „indicative, de verificat de evaluator"
   (deja avem adnotările demo; de întărit ca disclaimer permanent).

---

## NOW — committed (0–4 săptămâni)

> Conformitate cu standardele curente + quick-wins de încredere. Scop atinsabil cu efort mic-mediu.

| # | Item | Driver ANEVAR | Efort | Status |
|---|---|---|---|---|
| 1 | **Citează explicit SEV ediția 2025** (HCN 2/2025) în declarația de conformitate și termenii de referință | SEV 2025 | S | **Done** |
| 2 | **Checklist GEV 520** — secțiunea de risc include acum factorii obligatorii A5 (a–d), ipoteze speciale/vânzare forțată (A4), independență/implicare materială (A3), ipoteza transfer liber (A8), înregistrare BIG (§7) | GEV 520 | M | **Done** |
| 3 | **Aliniere terminologie SEV 2025** (tip valoare → SEV 102; raportare → SEV 106; termeni → SEV 101) | SEV 2025 | S | **Done** |
| 4 | **Disclaimer permanent pe comparabile** „surse indicative, verificate de evaluator" (nu doar în modul demo) | Constrângere ANEVAR | S | **Done** |
| 5 | **Curs BNR automat** EUR/LEI (feed public BNR + buton „↻ Curs BNR") | Practică | S | **Done** |
| 6 | **Export PDF** al raportului | Cerere utilizator | S | Documentat (Word → Salvează ca PDF; convertor in-app necesită dependență externă) |
| 7 | **Validare numerică** pe dosarele de casă rămase (Maneciu, Brașov) — acum 3/3 dosare reproduse | Încredere | S | **Done** |

**Capacitate Now:** rezonabilă (toate S/M, fără dependențe externe).

---

## NEXT — planned (1–3 luni)

> Acuratețe metodologică + integrarea datelor oficiale ANEVAR (fără acces special unde se poate).

| # | Item | Driver ANEVAR | Efort | Dependență |
|---|---|---|---|---|
| 8 | **Indicele imobiliar ANEVAR** → input pentru ajustarea „condițiile pieței (timp)" în grile | Indicele ANEVAR | M | **Done** — date publice parsate (`/api/indice-anevar`) + buton în grilă; verificat live |
| 9 | **Grilă de teren cu comparabile reale** (descoperire de anunțuri de teren, nu doar casă) | Acuratețe | M | **Done** — `/api/descopera-teren` + UI în grilă; verificat live (Breaza) |
| 10 | **Import catalog costuri IROVAL** pentru CIN (€/mp actualizat pe categorii) | IROVAL | M | Blocat — catalog cu acces |
| 11 | **Anexa 3 — upload documente** (extras CF, plan cadastral, acte) | Structură raport | S | **Done** |
| 12 | **exe semnat + instrucțiuni evaluator** (evită SmartScreen, distribuție curată) | Distribuție | M | Documentat — necesită certificat code-signing |

---

## LATER — directional (3–6+ luni, pariuri strategice)

> Valoare mare, dar necesită acces/coordonare externă sau efort substanțial.

| # | Item | Driver ANEVAR | Efort | Notă |
|---|---|---|---|---|
| 13 | **Integrare BIG (Baza Imobiliară de Garanții)** ca sursă primară de comparabile pentru garanție | BIG | L | Necesită acces membru ANEVAR / API; cea mai autoritară sursă |
| 14 | **Modul AML / Legea 129/2019** — KYC client + beneficiar real, screening sancțiuni/PEP/jurisdicții necooperante, jurnal + flag tranzacții suspecte | Legea 129/2019 | L | Diferențiator de conformitate; entitate raportoare |
| 15 | **Contribuție automată la BIG/BIF** din rapoartele generate (dacă ANEVAR permite) | BIG/BIF | L | Depinde de specificațiile ANEVAR |
| 16 | **Suport multi-tip proprietate** (apartament, comercial) dincolo de casă+teren | Extindere piață | L | — |

---

## Riscuri și dependențe

- **Acces la date ANEVAR (BIG/BIF, IROVAL):** itemii 10, 13, 15 depind de acces de membru / API ANEVAR
  — de clarificat devreme cu ANEVAR/filiala. Cel mai mare risc de blocaj.
- **GEV 520 — conținut exact:** itemul 2 necesită citirea ghidului oficial 2025 (PDF SEV 2025) pentru
  checklist precis; fără el, riscăm o secțiune incompletă pentru bănci.
- **AML (item 14):** complexitate de reglementare; necesită validare juridică, nu doar tehnică.
- **Code-signing (item 12):** cost certificat + proces; altfel distribuția rămâne cu avertisment SmartScreen.

## Schimbări față de starea anterioară (acest update)

- **Adăugat** ca teme noi, derivate din cercetarea ANEVAR: conformitate SEV 2025/IVS, GEV 520 checklist,
  integrare BIG/BIF, Indicele ANEVAR, modul AML 129/2019, catalog IROVAL.
- **Repriorizat:** conformitatea cu standardele 2025 urcă în **Now** (raportul trebuie să fie „la zi");
  integrarea datelor oficiale (BIG) devine pariul strategic principal în **Later**.
- **Confirmat ca Done:** motoarele de calcul + raportul + descoperirea (validate).

---

### Surse (anevar.ro)
- Standarde de evaluare (SEV 2025): https://www.anevar.ro/p/despre-anevar/standarde-de-evaluare
- Colecția SEV 2025 (PDF): https://www.anevar.ro/images/_upload/standardele-de-evaluare-a-bunurilor-2025.pdf
- Baze BIG/BIF: https://www.anevar.ro/p/baze-de-date-big-si-bif
- Indicele imobiliar ANEVAR: https://www.anevar.ro/p/informatii-din-piata/informatii-statistice-anevar/indicele-imobiliar-anevar
- Aplicarea Legii 129/2019 (AML): https://www.anevar.ro/p/aplicarea-legii-1292019
- Informații statistice ANEVAR: https://www.anevar.ro/p/informatii-din-piata/informatii-statistice-anevar
