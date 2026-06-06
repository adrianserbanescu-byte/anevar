# 9 topicuri de decis (feature-uri/module) — analiză + direcție propusă

> Cele 9 topicuri cele mai importante de decis pe **feature-uri/module** (NU juridic/comercial).
> Trimise la LLM council în 3 interogări (fiecare = context complet + 3 topicuri). Mai jos:
> **analiza mea pe toate 9** + **verdictul council-ului** unde e disponibil + **direcția propusă**.
> Stare council: **Q1 ✅** (topics 1,5,7) · **Q2 ✅** (topics 3,4,6) · **Q3 ✅** (topics 2,8,9) · **+ council pe plan-UI ✅**
> (vezi [`council-plan-UI-nou.md`](council-plan-UI-nou.md)). Toate cele 4 interogări rulate; Sonnet/gpt-5.1 au dominat clasamentul.
> Decizii care rămân ale tale: vezi [`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md). Actualizat: 2026-06-06.

---

## INTEROGAREA 1 (Dosar / identitate / stocare / flux) — council ✅

### TOPIC 1 — Identitatea dosarului + blocarea ei
**Council Q1 (consens puternic, Sonnet #1):** identitate = `(scop, tip_proprietate, COD FISCAL client [CNP/CUI], județ, localitate)`.
**EXCLUDE `nume_client`** din identitatea „tare" (variații „Ion Popescu"/„Popescu Ion") — ancora stabilă e
codul fiscal. Blocare automată la **prima generare reușită de `.docx`** (nu la draft/calcul). Schimbarea unui
câmp „tare" → dialog „Modifici identitatea = DOSAR NOU; clonez datele tehnice + comparabilele?". Greșeli de
tastare → buton „Deblochează corectură tipografică", înregistrat în tab-ul **Audit**.
**Opinia mea (de acord, cu rafinare):** azi avem `id_client` free-text + `nume_client` în identitate. Rafinez:
**ancoră pe cod fiscal**, numele rămâne editabil. Cheia UX care face rigiditatea acceptabilă e **clonarea care
păstrează munca tehnică** — fără ea, userii caută workaround-uri. Blocarea la generarea finală (nu la calcul)
permite iterații de calibrare. **Risc:** user schimbă clientul după generare → inconsistență; mitigat de dialogul roșu.

### TOPIC 5 — Stocare: coexistența SQLite ↔ foldere
**Council Q1 (consens):** folderele = sursa unică de adevăr. Migrare **unidirecțională** SQLite→foldere în 3 faze
(~6 luni): (1) coexistență (nou=foldere, vechi=SQLite), (2) buton one-time „Migrează în folder" per dosar vechi +
**feature-freeze pe UI vechi**, (3) retragere UI vechi, SQLite **read-only** (recuperare de urgență). Script
**ne-distructiv** + log de migrare obligatoriu.
**Opinia mea (de acord):** am redus deja divergența — «Calculează» din UI nou nu mai scrie rânduri orfane în SQLite
(`/api/dosar/{uid}/calcul`). Adaug: migrarea citește SQLite → creează `dosar.json`, marchează `migrated` în SQLite
(reversibil). **Risc:** mapare greșită a anexelor vechi → testare + log + skip-pe-eroare.

### TOPIC 7 — Fluxul Calcul → Generează (sursă unică + etichetare AI/determinist)
**Council Q1 (consens):** sursă unică = rezultatul calculului din `dosar.json`. «Generează» blocat până există
**Calcul valid salvat** + checkbox de asumare bifat. Orice input modificat → calcul revine la **Draft** + banner
roșu „date perimate, recalculează" (diff de timestamp). Etichetare: `[Determinist]` pe toate numerele (cu
**hash al input-urilor** pentru reproducibilitate audit SEV), `[Asistență AI]` pe proză; marcajele vizuale AI
există în UI dar **dispar în `.docx` semnat** (evaluatorul își asumă integral).
**Opinia mea (de acord; parțial implementat):** checkbox-ul de asumare există deja (l-am pus). De adăugat:
persist calc în `dosar.json` (`calcul_final` + timestamp), banner de invalidare, hash-ul de input (idee SEV
puternică). Etichetarea AI/determinist e ieftină și valoroasă reputațional.

---

## INTEROGAREA 2 (Funcții AI + conținut workspace) — council ✅ (Sonnet #1)

### TOPIC 3 — Regenerarea textului AI la „Generează" (feature B)
**Council (consens):** ecran **diff per capitol** (text vechi vs. preview nou) ÎNAINTE de generare; **mod global +
override per capitol**; **implicit TEMPLATE** (păstrează vocea evaluatorului, actualizează valorile) — 3/4 modele
(grok: STRICT); diff vizual post-generare; hint-uri opționale per capitol; micro-descrieri de 1 rând STRICT/TEMPLATE.
**Opinia mea:** dacă dosarul are deja raport, per capitol AI arăt textul vechi + 3 opțiuni: **Strict** (AI schimbă
doar valorile, text minim), **Template** (textul vechi = șablon), **Generare nouă**. + hint-uri text opționale.
**Implicit recomandat:** **Strict** la regenerare (același dosar) — păstrează proza deja validată de evaluator;
un buton „toate capitolele Strict" + override per capitol pentru power-useri. Matricea din `master_config`
decide ce capitole sunt reutilizabile. **Risc:** încărcare cognitivă → controalele per-capitol sub un toggle „avansat".

### TOPIC 4 — Import „dosar asemănător" (feature D)
**Council (consens):** tabel rezumat (Capitol | preview text | decizie matrice | override) + confirmare explicită;
**avertisment ferm „doar TEXT, nu valori"**; **detecție PII la import** (regex CNP/adresă → avertisment — adăugat de
Sonnet); flag `imported_template_from` pt audit; implicit: Zonă/Piață=GHIDARE, Descriere clădire/teren=DIFERIT, AML/Audit/GDPR=DIFERIT.
**Opinia mea:** import `.docx/.pdf` similar; matricea decide per capitol free-text: **diferit** (nu importă) /
**ghidare** (AI ia în considerare) / **particularizat** (AI ignoră). **Valorile NU se importă, doar textul.**
Siguranță: **rezumat per capitol + confirmare explicită** înainte de aplicare; niciodată auto-aplicat.
**Implicit:** ghidare pentru capitolele compatibile (același tip+scop), diferit altfel. **Risc:** context vechi/greșit
care biasează AI-ul → mitigat de confirmare + regula „valorile nu se importă".

### TOPIC 6 — Conținutul tab-urilor de output (AML/GDPR/Audit/Anexe)
**Council (consens):** **status cards inline + detaliu la click** (anti-aglomerare/memory). AML: semafor risc +
scor + indicatori L129 expandabili. GDPR: status consimțământ + generare formular la cerere. Audit: timeline/urmă
de calcul inline (collapsed log + export). Anexe: grid thumbnail lazy-load + viewer OS. (identic cu opinia mea)
**Opinia mea:** păstrăm „output-first" fără aglomerare — **inline doar ce are conținut real**, link la detaliu în rest.
- **AML:** badge inline cu **starea de risc** (verde/galben/roșu) calculată din dosar + link la `/aml` pentru detaliu.
- **GDPR:** link la politică + disclaimer (deja) + starea consimțământului (bifă).
- **Audit:** **urma de calcul inline** după Calcul (trace-ul determinist = „output-ul" care justifică valoarea).
- **Anexe:** upload foto + scanuri (leagă de Topic 2). **Risc:** tab-uri pe jumătate goale → notă clară „vine cu…".

---

## INTEROGAREA 3 (Completitudine date + UI) — council ✅ (Sonnet #1)

### TOPIC 2 — Paritate UI nou: grila teren + chirii/venit/DCF + anexă foto/documente
**Council (3/4 — DIVERG de decizia ta):** anexa foto + scanuri CF/cadastral sunt **OBLIGATORII per SEV 2025** →
gating-ul total e „anti-pattern, face aplicația inutilizabilă". Recomandare: **fă-le ACUM** (sub-tab Anexe: Foto +
Documente, drag-drop, thumbnail, legendă, stocate în `dosare/{uuid}/anexe/`, compresie JPEG); gating doar pe **VOLUM**.
Grok (minoritar) susține gating. → **escaladat la tine** (BLOCAT-pe-Adi).
**Opinia mea:** grila teren ✅ + venit/DCF ✅ făcute. Anexa foto: am respectat decizia ta de gating; council-ul o
contestă ferm ca cerință de conformitate. Decizi tu re-încadrarea. motorul suportă tot; `asambleaza()` (JS) omite `land_comparables`, `pondere_piata`, `date_venit`,
`date_dcf`, `photos`, `documente`. De adăugat incremental în UI nou: (a) **grila de teren** (sub Comparabile) —
prioritar (casă+teren garantare); (b) **anexă foto + scanuri** (Anexe) — cerute în raport; (c) **venit/DCF** —
metodă avansată cu câmpuri proprii (rar la garantare). **Risc:** aglomerare → progressive disclosure pentru avansate.

### TOPIC 8 — Descoperire comparabile: portaluri (OLX) + călire + integrare în UI nou
**Council (consens):** integrare **split-screen în Comparabile** (căutare stânga → bifează → importă în grilă dreapta)
+ fallback manual. OLX: **păstrat dar declasat** (scor penalizat pt suprafață lipsă, flag „⚠ suprafață lipsă",
completare manuală + validare roșie la Generează) — majoritar; gemini/grok ar scoate OLX. imobiliare/storia prioritare.
**Opinia mea:** imobiliare+storia merg corect; OLX dă prețul dar rar suprafața structurată. Recomand: imobiliare+
storia primare; OLX best-effort cu „completează suprafața manual"; călesc extragerea listei (preferință localitate
făcută; adaug filtru de categorie ca să sară promovatele cross-categorie); **integrez descoperirea în sub-tab-ul
Comparabile** din UI nou (acum trimite în pagină separată). **Risc:** HTML-ul portalurilor driftează → regula
„audit live pe 3 anunțuri/portal înainte de release" (deja în strategia de testare).

### TOPIC 9 — Localități adăugate de user (#3)
**Council (consens):** fișier user separat (`localitati_custom.json` lângă date, NU împachetat), merge runtime (union),
marcaj `(custom)`; **slug auto-transliterat** (unidecode) + **override manual** + buton **„Testează URL"**; validare
**non-blocking** (warning, nu eroare, la 0 rezultate). gemini/grok: SQLite + mapare la „localitate părinte" (slug-ul
comunei pt căutare, nume custom în raport) — idee bună pt sate mici.
**Opinia mea:** modul mic, izolat. Userul adaugă localități proprii (în `OUTPUT_DIR/localitati_user.json` —
consecvent cu folder=adevăr), îmbinate cu `judete_localitati.json` împachetat la căutare; buton în wizard + UI nou.
**Implicit:** aditiv, nu suprascrie niciodată setul împachetat. **Risc:** mic. *Notă: spec-ul zice „de brainstormat" —
nu îl construiesc fără decizia ta, dar îl analizez aici fiindcă l-ai pus pe lista celor 9.*

---

## Direcția propusă + plan (toate 9, ordonate pe dependență)

> Secvență optimă (ce întâi, ce după), ținând cont de council Q1 + analiza mea. Council Q2/Q3 se va folosi
> pentru a rafina topicurile 2,3,4,6,8,9 la reconectare.

1. **Nucleul dosarului (fundație, deblochează metrarea):** Topic 1 (identitate + lock pe cod fiscal) +
   Topic 7 (Calcul→Generează cu sursă unică, persistă calc + banner perimat + etichetare) + Topic 5 (migrare
   stocare în 3 faze). Council Q1 puternic aliniat. **Necesită confirmarea ta pe declanșatorul de lock (BLOCAT #10).**
2. **Paritate (prerequisit pentru retragerea UI vechi):** Topic 2 — grila teren → anexe foto → venit/DCF.
3. **Output-first complet:** Topic 6 — stare AML inline, urmă audit inline, anexe.
4. **Funcții AI:** Topic 3 (regenerare per capitol) + Topic 4 (import asemănător) — după nucleu + matricea master.
5. **Îmbunătățiri:** Topic 8 (descoperire în UI nou + OLX/călire) + Topic 9 (localități user).

**Ce pot face eu autonom de aici** (fără decizie): Topic 7 (persist calc + banner + etichetare), Topic 8 (călire
descoperire + integrare în sub-tab), Topic 2 (grila teren în UI nou — feature de paritate). **Ce te așteaptă:**
declanșatorul de lock identitate (#10), retragerea UI vechi (#18), construirea #3 localități (era „de brainstormat").

> **De completat la reconectarea council-ului:** Q2 (topics 3,4,6), Q3 (topics 2,8,9), plus council-ul ADIȚIONAL
> cerut de Adi (fiecare model își dă PLANUL lui pentru noul UI — comparat cu al meu). Vezi `AUTONOM-taskuri.md`.
