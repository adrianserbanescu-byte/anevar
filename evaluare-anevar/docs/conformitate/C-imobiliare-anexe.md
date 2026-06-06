# C — Conformitate IMOBILIARE + ANEXE (SEV 230 / SEV 233 / GEV 630 vs. aplicație + planuri)

> Audit de conformitate ANEVAR pe standardele IMOBILIARE din SEV 2025, față de codul aplicației
> (`evaluare-anevar/src/evaluare/`) și planuri (`docs/`). Aplicația ASISTĂ evaluatorul la casă+teren
> pentru garantare credit — regula: **avertizează, nu decide**.
> Refs standard: `md files/standardele-de-evaluare-a-bunurilor-2025.md`.
> Legendă status: ✅ acoperit · 🟡 parțial / cu lacună · ❌ lipsă · 📋 decizie/scop evaluator.
> Bucket: **A** = cod (îl fac autonom) · **B** = metodologie/conformitate (prag legal — decide evaluator/jurist) · **C** = produs/comercial (decide Adi).

## Tabel de conformitate

| Cerință (ref) | Status | Unde | Gap + recomandare | Bucket |
|---|---|---|---|---|
| **Inspecția proprietății — de regulă obligatorie; neinspectarea/parțial = motivată în raport** (GEV 630 §21-22, l.5890-5900) | 🟡 | `models/meta.py:23` `data_inspectiei`; raport `generator.py` `_termeni_referinta` (l.227) menționează data inspecției | Captăm DATA inspecției, dar nu există câmp de **amploare/constatări** și nici clauză automată „neinspectare → motiv obligatoriu". Recomandare: câmp „amploare inspecție" + dacă lipsește data → ipoteză specială auto în raport. | A |
| **Obligația de FOTOGRAFII (planșe + din exterior)** (GEV 630 §111.a.(1) l.6371 „fotografii"; cuprins „Anexele raportului… fotografii etc." l.5645) | 🟡 | Backend: `generator.py` `_adauga_anexe` → Anexa 2 (l.516-528) inserează `ctx.photos`; UI **vechi** `wizard.html:341-345` are upload foto | Backend + UI vechi OK. **UI NOU (`dosar.html:149`) blochează atașarea** („vine cu versiunea comercială") → în noul flux raportul iese fără foto = neconform. Vezi secțiunea ANEXE. | A + C |
| **Descrierea proprietății — date fizice minime** (acces, utilități+distanțe, caract. fizice teren+construcții, utilizare la data eval.) (GEV 630 §28 l.5931-5936) | 🟡 | `models/property.py` (LandData/BuildingData), `report_context`, raport cap.4 (`generator.py:609-633`) | Avem: suprafață, Au, Acd, AC, structură, finisaje, clasă energetică, regim înălțime, utilități (listă în LandData). **Lipsesc câmpuri structurate: acces/dificultăți de acces, distanța până la utilități, utilizarea la data evaluării.** UI nou (`dosar.html`) NU expune nici `utilitati`, `structura`, `finisaje`, `clasa_energetica`. Recomandare: adaugă aceste câmpuri în UI nou + descriere acces. | A |
| **Dreptul de proprietate supus evaluării identificat** (GEV 630 §11.d l.5792 „dreptul de proprietate"; SEV 230 §40.1 l.2747) | 🟡 | `models/meta.py` (cadastral, CF, proprietar); raport `_termeni_referinta` premise „libera de sarcini" (l.236) | Identificăm cadastral/CF/proprietar, dar **tipul dreptului (deplin/dezmembrământ: uzufruct, superficie, servitute) nu e câmp**; se presupune „drept deplin, liber de sarcini". `DateExtraseCF.sarcini` se extrage, dar nu se propagă structurat în raport. Recomandare: câmp „drept evaluat" + listare sarcini din CF în descriere. | A (câmp) / B (raționament) |
| **Sarcini / drepturi derivate care afectează valoarea** (SEV 230 §40.1.b l.2748, §140 ierarhia drepturilor l.3046) | 🟡 | `ingestie/models.py:16` `DateExtraseCF.sarcini`; extractor `extrage_cf` (l.47) | Sarcinile se EXTRAG din CF dar **nu apar într-o secțiune dedicată a raportului** și nu modifică premisa. Recomandare: afișează sarcinile extrase + cere confirmare; reflectă-le în descrierea juridică (cap.4). | A |
| **Suprafețe din document de specialitate (cadastru); diferențe act↔măsurat → contact utilizator + ipoteză** (GEV 630 §25-26 l.5912-5927) | 🟡 | `ingestie/` extrage suprafețe din CF/releveu/plan; `validation.py:31-38` validează >0 și Au≤Acd | Validăm coerența numerică, dar **nu există verificare „suprafață act vs. suprafață măsurată"** cu alertă + ipoteză specială. Recomandare: dacă CF.suprafata ≠ plan.suprafata_teren → alertă + clauză în termeni de referință. | A |
| **Corespondență scriptic ↔ faptic la inspecție, neconcordanțe în raport** (GEV 630 §24 l.5906, §111.a.(3) l.6378) | ❌ | — | Nu există mecanism de marcare a neconcordanțelor scriptic/faptic. Recomandare: câmp liber „neconcordanțe constatate la inspecție" → secțiune dedicată în raport (cerință explicită §111.a.3). | A |
| **Evaluarea terenului — CMBU + comparația vânzărilor (metodă principală)** (GEV 630 §81-91 l.6233-6272) | ✅ | `engine/land.py` grilă 2 etape (tranzacție compus + proprietate aditiv), selecție pe ajustare brută minimă; raport `_adauga_grila_teren` (l.326) | Conform: comparația vânzărilor, elemente de comparație, ajustări argumentabile (`Adjustment.justificare`). CMBU teren e narativ (cap.5, AI draft). OK. | ✅ |
| **Elemente de comparație teren** (drepturi, finanțare, condiții vânzare, piață, localizare, fizice, acces, utilități, zonare) (GEV 630 §90 l.6266) | 🟡 | `models/comparable.py` `LandComparable.adjustments` (element liber) | Modelul permite orice element ca ajustare, dar **lista de elemente nu e impusă/ghidată**; UI nou trimite doar `pret_mp;suprafata` fără ajustări (grila detaliată e în `/grila`). Acceptabil (evaluatorul completează în grilă). | A (ghidare opțională) |
| **Metode alternative teren (extracție, alocare, reziduală, capitalizare rentă)** (GEV 630 §82, §92-102 l.6236-6324) | 📋 | doar comparația vânzărilor | Doar comparația e implementată. Pentru garantare rezidențială e suficient (metoda principală). Alternativele = backlog, scop evaluator. | 📋 |
| **CMBU prezentat în raport** (GEV 630 §35-39 l.5968-5981) | 🟡 | raport cap.5 (`generator.py:635-640`), `_narativ` AI | Secțiunea există dar e text AI „[de completat]" dacă lipsește narativul. Conținut OK ca structură; raționamentul rămâne al evaluatorului. | B |
| **Cele 3 abordări + justificarea neaplicării** (GEV 630 §40-43, §104 l.5982-6000, l.6332) | ✅ | `engine/abordari.py`, `reconciliation.py`, `report/sectiuni.py` (secțiuni cost/comparație/venit pe profil) | Cost + comparație + venit/DCF implementate; reconcilierea selectează (nu medie aritmetică — conform §107 l.6348). OK. | ✅ |
| **Abordarea prin venit — NOI, VBP→VBE, rată capitalizare argumentată** (GEV 630 §59-71 l.6104-6178) | ✅ | `engine/venit.py`, UI nou `dosar.html:103-113` (VBP, neocupare, cheltuieli, rată), raport cap.6 (l.652-664) | Capitalizare directă + DCF; câmpuri în UI nou. OK. | ✅ |
| **Abordarea prin cost — CIN, tipuri depreciere, surse cost** (GEV 630 §72-80 l.6179-6231) | ✅ | `engine/cost.py`, `models/property.py` (CostElement, depreciere fizică/funcțională/externă), raport `_adauga_tabel_cost` | Catalog IROVAL, depreciere fizică interpolată + funcțională/externă cu justificare obligatorie (`validation.py:76-87`). OK. | ✅ |
| **Date de intrare imobiliare — surse explicate, justificate, documentate** (SEV 230 §100.5 l.3018; GEV 630 §29 l.5937) | 🟡 | raport `_termeni_referinta` (l.271 sursa info), `_adauga_grila_comparatie` notă surse (l.319), `discovery/` capturează `url`/`sursa` | Sursele comparabilelor sunt reale (URL în `Comparable.sursa`, `discovery/results.py`). **Lipsește documentarea sursei pentru: cost (catalog), rată capitalizare, suprafețe** ca text per-dată. Recomandare: notă de sursă lângă fiecare dată semnificativă. | A / B |
| **Ierarhia informațiilor comparabile (direct → indirect → piață)** (SEV 230 §100.2 l.3002) | 📋 | `discovery/scoring.py` scorează relevanța | Scoring de relevanță există, dar ierarhia formală nu e etichetată. Minor pt. garantare. | 📋 |
| **Min. comparabile + ajustări justificate + limite** (GEV 630 §52, §57-58 l.6028, l.6084-6103) | ✅ | `validation.py` MIN_COMPARABILE=3, outlieri, LIMITA_AJUSTARE_BRUTA=25%; `Adjustment.justificare` | Blochează <3 comparabile; alertează outlieri/ajustări mari. Conform (alertă, nu blocare rigidă — aliniat §109 l.6354 toleranța 20%). | ✅ |
| **Document set: act proprietate, extras CF, certificat urbanism (teren liber/în construire), CPE/ESG** (GEV 630 §16 l.5854-5863) | 🟡 | `ingestie/` parsează CF, releveu, plan, CPE | Parsăm CF + CPE + plan. **Certificat de urbanism (POT/CUT/restricții) NU are extractor/model** — relevant pt. teren liber/CMBU; **act de proprietate** nu e modelat. Recomandare: model `DateCU` (POT/CUT/destinație/restricții) + slot act proprietate. | A |
| **ESG ca dată de intrare în raport** (SEV 230 §100.6 l.3020; GEV 630 §12.m; SEV 106 §30.6.m) | ✅ | raport `_termeni_referinta` paragraf ESG (l.276-280); `clasa_energetica` în BuildingData | Paragraf ESG prezent + clasă energetică din CPE. OK. | ✅ |
| **Proprietatea în curs de construire (dacă nefinalizat) — metoda reziduală, % execuție, autorizație** (SEV 233 l.3367-4021; GEV 630 §73 „faza de proiect" l.6189) | 📋 | `profil.py` are tip „special"; cost are „construcții în faza de proiect" conceptual | Nu există flux dedicat „în curs de construire" (% stadiu fizic, autorizație construire, metoda reziduală teren). Out-of-scope pt. casă finalizată; backlog dacă apar imobile nefinalizate la garantare. | 📋 |
| **Raportare — identificare prin adresă + copii extrase cadastrale + copii acte + hartă + fotografii** (GEV 630 §111.a.(1) l.6366-6374) | 🟡 | raport `_adauga_anexe` Anexa 1/2/3 (l.505-542) | Structura Anexelor există (surse comparabile, foto, documente cadastrale/CF/acte). **Conținutul efectiv depinde de atașări** — blocate în UI nou. **Hartă de referință / extras de localizare lipsește** ca element. | A + C |
| **Alocarea valorii teren↔construcții (argumentată; fără medie)** (GEV 630 §113-119 l.6408-6444) | ✅ | `generator.py` `_adauga_alocare` (l.384) + verificare consistență cost↔piață >20% (GEV 520) | Alocare prin deducerea valorii terenului + alertă dacă alocarea construcției deviază >20% de CIN. Conform. | ✅ |
| **Declarația de conformitate cu SEV / explicarea neconformității** (GEV 630 §12.p l.5836; §110) | ✅ | `generator.py` `_declaratie_conformitate` (l.192), `_scrisoare_transmitere` (l.164) | Declarație SEV 2025 + clauză GEV aplicabil. OK. **Dar:** dacă raportul iese fără inspecție/foto, declarația de conformitate devine **falsă** — vezi Top 5 #1. | ✅ / risc |

---

## Top 5 goluri

1. **ANEXE foto/documente blocate în UI nou (neconformitate directă).** `dosar.html:149-150` tratează atașarea ca „versiune comercială"; backend-ul (`generator.py` `_adauga_anexe`, `report_context.photos/documente`) și UI-ul vechi (`wizard.html:341-348`) o suportă deja complet. În noul flux raportul se generează **fără fotografii și fără extras CF/cadastral** — încălcă GEV 630 §111.a.(1) l.6371 + cuprins l.5645, în timp ce declarația de conformitate (`_declaratie_conformitate`) afirmă conformitate SEV. **Fix (bucket A):** portează upload-ul foto/documente din wizard în tab-ul Anexe; gating doar pe VOLUM. *Decizia de re-încadrare (C/B) e a lui Adi — `BLOCAT-pe-Adi.md` §C2 pct.24.*

2. **Neconcordanțe scriptic↔faptic + amploarea inspecției — necaptate** (GEV 630 §24, §111.a.(3) l.5906/6378). Captăm doar `data_inspectiei`. Standardul cere prezentarea explicită a oricărei neconcordanțe și a amplorii inspecției. **Fix (A):** câmp „amploare inspecție" + „neconcordanțe constatate" → secțiune raport; auto-ipoteză specială când inspecția lipsește (§21).

3. **Tipul dreptului + sarcinile din CF nu sunt structurate în descriere** (SEV 230 §40.1.b, §140; GEV 630 §11.d). Se presupune „drept deplin, liber de sarcini"; `DateExtraseCF.sarcini` se extrage dar nu ajunge într-o secțiune juridică. **Fix (A câmp / B raționament):** câmp „drept evaluat" (deplin/uzufruct/superficie/servitute) + listare sarcini în cap.4.

4. **Date fizice obligatorii incomplete în UI nou + lipsă acces/utilități-distanțe** (GEV 630 §28 l.5931). UI nou (`dosar.html`) nu expune `utilitati`, `structura`, `finisaje`, `clasa_energetica` și nu există câmp „acces / dificultăți de acces" ori „distanța până la utilități". **Fix (A):** adaugă câmpurile fizice existente în modele la UI nou + descriere acces.

5. **Certificat de urbanism (POT/CUT/restricții) + act de proprietate nemodelate** (GEV 630 §16 l.5858). Pentru teren liber / CMBU și pentru identificarea dreptului. Avem extractoare CF/releveu/plan/CPE, dar nu CU și nu slot pentru actul de proprietate. **Fix (A):** model `DateCU` + slot act proprietate în ingestie.

---

## ANEXE OBLIGATORII (foto / documente) — stadiu

**Verdict: cerință de CONFORMITATE, nu feature comercial — confirmat de standard.**
- GEV 630 cuprins: „Anexele raportului de evaluare (Fișe clădiri, **fotografii** etc.)" (l.5645) și §111.a.(1) l.6366-6374: identificarea proprietății în raport se face „prin adresă, **copii ale extraselor din documentația cadastrală**, **copii ale actelor de proprietate**, hartă de referință, **fotografii**…".
- SEV 230 §120 „Documentare și raportare" (l.3028) + SEV 106 §30.6 (sursele și modul de selectare a informațiilor) cer documentarea probelor.
- `validare-SEV2025-anexe-si-council.md` (l.7-29) și `BLOCAT-pe-Adi.md` §C2 pct.24 (l.30-34) **confirmă** re-încadrarea ca **P0 de conformitate** (gating doar pe volum).

**Stadiu tehnic (descoperit în cod):**

| Componentă | Stadiu | Dovadă |
|---|---|---|
| Model date anexe | ✅ există | `report_context.py:30-31` `photos: list[str]`, `documente: list[str]` (data-URL base64) |
| Randare în raport (Anexa 2 foto) | ✅ funcțional | `generator.py:516-528` `_adauga_anexe`, decode base64 `_decode_foto` (l.491) |
| Randare în raport (Anexa 3 CF/cadastral/acte) | ✅ funcțional | `generator.py:530-542` |
| Anexa 1 — surse comparabile | ✅ funcțional | `generator.py:508-514` (URL-uri reale din `Comparable.sursa`) |
| Upload în **UI VECHI** (wizard) | ✅ funcțional | `wizard.html:341-348` (input file foto+doc), `:548-573` (FOTOS/DOCUMENTE→base64), `:667-668` (în payload) |
| Upload în **UI NOU** (dosar) | ❌ **BLOCAT** | `dosar.html:149-150` „Atașarea fișierelor vine cu versiunea comercială"; `asambleaza()` (l.252-269) NU include `photos`/`documente` |
| Persistare anexe pe folder (`dosare/{uuid}/anexe/`) | ❌ lipsă | upload-ul vechi e doar in-memory pe sesiune (`wizard.html:548` „nu se salvează"); planul cere stocare pe folder (`validare-…md:54`) |
| Hartă de referință / extras localizare | ❌ lipsă | necerut în cod; element §111.a.(1) |
| Clauză auto „neinspectare → motiv" | ❌ lipsă | `generator.py` nu impune |

**Concluzie ANEXE:** lanțul backend este COMPLET; singurul blocaj real e **UI-ul nou**, unde atașarea e gated comercial — ceea ce face raportul generat din noul flux **neconform** (fără foto + fără extras CF/acte) deși declară conformitate SEV. Deblocarea = muncă de cod (bucket A: portare din wizard + persistare pe folder); pragul de volum gratuit rămâne decizie Adi/evaluator (bucket C/B).

---

## Rezumat (≤180 cuvinte)

Abordările de evaluare imobiliară sunt solide și conforme: cele 3 abordări (cost/piață/venit+DCF), grila de teren în 2 etape cu selecție pe ajustare brută minimă (GEV 630 §81-91), alocarea valorii cu verificare cost↔piață, min. 3 comparabile, declarație de conformitate SEV 2025, ESG. Motorul de raport **suportă deja complet** anexele foto + documente CF/cadastral/acte (`generator.py` `_adauga_anexe`, `report_context.photos/documente`), iar UI-ul VECHI (wizard) le atașează funcțional.

Golul critic: **UI-ul NOU (`dosar.html:149`) blochează atașarea anexelor** ca „versiune comercială" — raportul iese fără fotografii și fără extras CF, încălcând GEV 630 §111.a.(1) (l.6371) și cuprinsul l.5645, deși declară conformitate. Confirmat ca P0 de conformitate în `validare-SEV2025-anexe-si-council.md` și `BLOCAT-pe-Adi.md` §C2.24.

Lacune secundare (bucket A): inspecție (amploare + neconcordanțe scriptic/faptic §24/§111.a.3), tipul dreptului + sarcini CF în descriere, date fizice (acces, utilități-distanțe §28) absente din UI nou, certificat urbanism + act proprietate nemodelate (§16). Toate sunt corectabile prin cod; pragurile rămân decizia evaluatorului.
