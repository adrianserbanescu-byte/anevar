# Audit consolidat ANEVAR — 2026-06-11

Sinteza tuturor findings-urilor colectate de **13 lentile** de audit (securitate OWASP, robustete, Nielsen, UX journey, accesibilitate WCAG 2.2 AA, cod-calitate, performanta, error-handling, AML logic, conformitate raport SEV 2025/GEV 520, consistenta cross-pagina, test-coverage, gap-functional).

**Status: READ-ONLY.** Nimic nu a fost implementat. Documentul serveste pentru prioritizare si aprobare inainte de orice modificare.

---

## 1. Sumar dupa deduplicare

Dupa fuziunea findings-urilor raportate de mai multe lentile (acelasi fisier + aceeasi problema), au rezultat **49 findings unice** din 56 raportate brut (7 dubluri cross-lentila fuzionate).

| Severitate | Numar findings unice |
|-----------|----------------------|
| **HIGH**  | 5 |
| **MEDIUM**| 24 |
| **LOW**   | 20 |
| **TOTAL** | **49** |

### Distributie pe lentila (findings brute, inainte de dedup)

| Lentila | HIGH | MED | LOW | Total |
|---------|:----:|:---:|:---:|:-----:|
| Securitate OWASP | 0 | 1 | 3 | 4 |
| Robustete | 0 | 2 | 1 | 3 |
| Nielsen 10 (feature noi) | 2 | 3 | 3 | 8 |
| UX journey | 1 | 2 | 0 | 3 |
| Accesibilitate WCAG 2.2 AA | 0 | 2 | 2 | 4 |
| Cod-calitate (src/evaluare) | 0 | 3 | 1 | 4 |
| Performanta | 2 | 4 | 3 | 9 |
| Error-handling / silent-failures | 0 | 3 | 2 | 5 |
| AML logic | 0 | 2 | 1 | 3 |
| Conformitate raport (SEV/GEV) | 0 | 2 | 1 | 3 |
| Consistenta cross-pagina | 0 | 4 | 7 | 11 |
| Test-coverage | 0 | 1 | 2 | 3 |
| Gap-functional / nealiniat | 1 | 3 | 2 | 6 |
| **Total brut** | **6** | **32** | **26** | **64** |

### Dubluri cross-lentila fuzionate (7)

| Problema | Findings fuzionate | ID consolidat |
|----------|--------------------|---------------|
| AML data hardcodata 2026-06-03 fara max=azi | H4 + UJ-REST(partial) + CONS-07(partial) | **D-01** (HIGH→MED) |
| aml/descoperire orfane din nav global | H3 + UJ-REST(partial) | **D-02** |
| base64 fara garda virgula → HTTP 500 | SEC-A-02 + CQ-04(mentiune) | **SEC-A-02** |
| Grila nu impinge comparabile in dosar | GF1 + UJ-REST(partial) | **GF1** |
| Mediana = element median nereal | CQ-04(mentiune) + PERF(implicit) | **CQ-04** |
| genereaza-demo nu e gated de checkbox asumare | UJ-REST(partial) | **D-03** |
| Etichete buton generare raport divergente | CONS-08 + H8(partial) | **CONS-08** |

> Notă: H4 (Nielsen) si CONS-07 (consistenta) raportau aceeasi data hardcodata; UJ-REST le grupa cu alte 3 probleme. Le-am separat: data hardcodata = **D-01**, nav orfana = **D-02**, demo-gate = **D-03**, iar grila-push = **GF1**.

---

## 2. Findings HIGH (5)

### H1 — Descoperire fara feedback de progres, dublu-submit
- **Locatie:** `descoperire.html:530-558`
- **Lentila:** Nielsen 10 (feature noi)
- **Descriere:** Submit la fetch fara status/disabled; mesaj abia dupa raspuns. Scraping de secunde fara feedback; permite dublu-submit.
- **Fix sugerat:** Status + disabled inainte de fetch; re-activeaza in `finally`.
- **Confidence:** certa

### H2 — Descoperire nu verifica `r.ok`, eroare necaptata la 4xx/5xx
- **Locatie:** `descoperire.html:548-560`
- **Lentila:** Nielsen 10 (feature noi)
- **Descriere:** Acceseaza `res.candidati.length` fara a verifica `r.ok`; la 422/500 fara `candidati` arunca eroare in afara `try/catch`, fara mesaj catre utilizator.
- **Fix sugerat:** Verifica `r.ok` cu mesaj + `return`; gardeaza `candidati`.
- **Confidence:** certa

### UJ-1 — Valoarea de piata nu e persistata; BIG arata mereu „lipsa"
- **Locatie:** `registru.py:77`, `dosare_fs.py`
- **Lentila:** UX journey
- **Descriere:** Calculul returneaza `valoare_finala` dar nu o salveaza niciodata in `dosar.json`; nu exista un astfel de camp in `dosar.html`. In consecinta verificarea BIG (Baza de Informatii pentru Garantare) raporteaza valoarea ca lipsa pentru toate dosarele.
- **Fix sugerat:** Persista `valoare_finala` la calcul sau la generarea raportului.
- **Confidence:** certa

### GF1 — Ajustarile din grila NU intra in evaluare/raport (comparabile trimise brute) *(fuzionat cu UJ-REST grila-dead-end)*
- **Locatie:** `web/templates/curent/dosar.html:1396-1397, 1500`; `assembler.py:195-196`
- **Lentile:** Gap-functional + UX journey
- **Descriere:** `asambleaza()` construieste `comparables`/`land_comparables` ca `{pret, suprafata}` FARA cheia `adjustments`. Butonul «Trimite preturile in Comparabile» impinge in textarea doar `c.pret+';'+c.suprafata`, deci ajustarile calculate in grila se arunca. `construieste_context` apeleaza `evaluate_market` pe comparabile FARA ajustari → valoarea de piata persistata = media preturilor BRUTE. In raport «Ajustare bruta» apare 0% pe toate randurile, iar anexa «Desfasuratorul ajustarilor» se omite mereu. Valoarea din raport difera de cea afisata in grila. (UX journey raporta acelasi simptom ca „grila dead-end: nu poate impinge comparabile in dosar".)
- **Fix sugerat:** Pastreaza ajustarile end-to-end: `g-import` scrie un format cu ajustari (JSON ascuns/atribut data per comparabil), sau `asambleaza()` citeste direct `compForm()` din cele 3 grile si trimite `comparables[].adjustments`. Minim: avertizeaza vizibil ca grila e doar calculator daca ramane deconectata.
- **Confidence:** certa

### PERF-1 — Descoperire: fetch HTTP + LLM strict secventiale (50+50 seriale)
- **Locatie:** `discovery/orchestrator.py:178-239, 291-307`
- **Lentila:** Performanta
- **Descriere:** Bucla pe URL-uri: fiecare candidat face `fetcher(url)` blocant (15s) plus `client.complete` LLM blocant (60s). `max_candidati=50` da 50 fetch + 50 LLM seriale per request, ocupand un worker minute intregi. `fetch_html` nu foloseste `requests.Session`.
- **Fix sugerat:** `ThreadPoolExecutor` + `requests.Session`; LLM in paralel cu un cap, sau lazy pe top-N; pastreaza apararea anti-SSRF.
- **Confidence:** certa

---

## 3. Findings MEDIUM (24)

### SEC-A-01 — CSV/formula injection in exportul de feedback (inconsecvent cu registru)
- **Locatie:** `web/routers/pagini.py:43` si `:156-158` (`_scrie_feedback_fisier` + `/api/feedback.csv`)
- **Lentila:** Securitate OWASP
- **Descriere:** Exporturile CSV de feedback scriu campuri controlate de user (mesaj, tester, pagina, url, sentiment) direct prin `csv.writer` FARA neutralizarea prefixelor de formula (`= + - @` TAB CR). Spre deosebire de exportul de registru (`registru.csv_text` aplica `xlsx_min._neutralizeaza_formula`), aici o intrare `mesaj="=cmd|'/C calc'!A1"` ramane neprefixata → interpretata ca formula LIVE in Excel/LibreOffice (CWE-1236). Impact redus (feedback local), dar e exact clasa deja reparata in registru.
- **Fix sugerat:** Refoloseste `xlsx_min._neutralizeaza_formula` pe fiecare camp inainte de `writerow` in ambele locuri.
- **Confidence:** certa

### R17-1 — Liste de comparabile nemarginite (lipseste `max_length`) → DoS CPU/memorie
- **Locatie:** `models/comparable.py:41,56,71`; `assembler.py:89-90`; `web/schemas.py:104,109,114`
- **Lentila:** Robustete
- **Descriere:** Listele `comparables`/`land_comparables` si `comparabile` (cele 3 scheme Grila), plus `adjustments` imbricate, nu au `Field(max_length=...)`. Endpoint-uri afectate: `/api/evaluare`, `/api/dosar/{uid}/calcul`, `/raport.docx`, `/audit.txt`, `/api/grila-*`. Motorul face `sorted(...)` O(n log n) + pase O(n) + iterare per-comparabil. Un client local poate trimite zeci/sute de mii de comparabile (sub plafonul global de 50MB) → rafala CPU + operatii Decimal. Aceeasi clasa de DoS inchisa in RUNDA 15 pentru `riscuri_fizice` (30) si `beneficiari_reali` (200) — listele de comparabile au fost omise.
- **Fix sugerat:** `Field(max_length=...)`: comparabile ≤ 200, `adjustments` ≤ 50 per comparabil. Respinge 422 inainte de motor.
- **Confidence:** probabila

### R17-2 — Liste nemarginite `elements`/`depreciation_points`/`utilitati`/`photos`/`documente` → amplificator .docx
- **Locatie:** `models/property.py:42,43,68`; `assembler.py:103-104`
- **Lentila:** Robustete
- **Descriere:** `BuildingData.elements`, `depreciation_points`, `LandData.utilitati`, `photos`/`documente` (data-URL base64) nu au `max_length`. La `/raport.docx` fiecare element devine paragraf XML in python-docx; serializarea .docx e amplificator mai greu decat motorul. `photos`/`documente` base64 mari incarca memoria la decodare + inglobare. Acelasi vector cu F-15-1, inchis doar pentru `riscuri_fizice`.
- **Fix sugerat:** `max_length` realist: elements ≤ 100, depreciation_points ≤ 50, utilitati ≤ 30, photos ≤ 30, documente ≤ 30. Respinge 422 la marginea API.
- **Confidence:** probabila

### H3 / D-02 — AML & descoperire lipsesc din nav global; AML orfan *(fuzionat: H3 + UJ-REST)*
- **Locatie:** `_nav_cross.html:4-15`
- **Lentile:** Nielsen 10 + UX journey
- **Descriere:** Nav-ul global nu listeaza `aml`/`descoperire`. Pagina AML standalone nu are link de intrare in UI → orfana.
- **Fix sugerat:** Adauga in `_nav_cross` sau redirectioneaza la dosar.
- **Confidence:** probabila

### H5 — Tip comercial/industrial/special cauta tacut ca o casa
- **Locatie:** `dosar.html:1057-1073`
- **Lentila:** Nielsen 10 (feature noi)
- **Descriere:** Tipurile comercial/industrial/special sunt mapate la casa+teren; comercialul (generator de venit) primeste comparabile rezidentiale fara explicatie in hint.
- **Fix sugerat:** Hint explicit ca nu exista cautare comerciala, e proxy Casa+teren.
- **Confidence:** probabila

### UJ-2 — Pastila BIG deschide JSON brut (dead-end)
- **Locatie:** `registru.html:63`
- **Lentila:** UX journey
- **Descriere:** Pastila linkeaza catre endpoint-ul JSON, fara o vizualizare HTML lizibila.
- **Fix sugerat:** Randeaza o vizualizare HTML de checklist.
- **Confidence:** certa

### D-03 — `genereaza-demo` nu e gated de checkbox-ul de asumare *(din UJ-REST)*
- **Locatie:** `dosar.html:1690`
- **Lentila:** UX journey
- **Descriere:** Butonul `genereaza-demo` nu e conditionat de bifa de asumare a ipotezelor, spre deosebire de generarea raportului oficial.
- **Fix sugerat:** Gate butonul demo de aceeasi asumare.
- **Confidence:** certa

### A11Y-01 — Widget custom `role=checkbox` (asumare flux) fara focus vizibil
- **Locatie:** `flux_livrabile.html:216`
- **Lentila:** Accesibilitate WCAG 2.2 AA
- **Descriere:** `flAsume` e un `div role=checkbox tabindex=0` operabil la tastatura (Space/Enter) dar fara `focus-visible` dedicat; inelul implicit e slab pe tema de pergament. Fratii `flRtn`/`flRts` sunt `button` (OK). WCAG 2.4.7 / 2.4.11: nu se vede focusul pe controlul care deblocheaza generarea raportului.
- **Fix sugerat:** Adauga `focus-visible` pe `.fl-assume` (outline sienna 2px offset 2px), sau transforma in `button`.
- **Confidence:** probabila

### A11Y-02 — Buton import fara `aria-busy`
- **Locatie:** `incepe.html:157,166`
- **Lentila:** Accesibilitate WCAG 2.2 AA
- **Descriere:** Butonul „importa" schimba textul in operatie dar nu pune `aria-busy`, inconsecvent cu `dosar.html:1680,1687`. Starea de ocupat nu e expusa programatic. WCAG 4.1.2.
- **Fix sugerat:** Seteaza `aria-busy=true` la start, elimina la final; text fara emoji ca nume accesibil.
- **Confidence:** probabila

### CQ-01 — Cod mort `pdf_converter`
- **Locatie:** `report/pdf.py`; `web/deps.py:31`; `web/app.py:44`
- **Lentila:** Cod-calitate
- **Descriere:** `report/pdf.py` injectat ca `Deps.pdf_converter`, dar nicio ruta nu il apeleaza; aplicatia nu mai face PDF din 2026-06-08.
- **Fix sugerat:** Elimina sau marcheaza dormant.
- **Confidence:** certa

### CQ-02 — Duplicare median+outlier de 4x
- **Locatie:** `engine/validation.py:128,222,300,368`
- **Lentila:** Cod-calitate
- **Descriere:** Bloc median + bucla outlier identic, repetat de 4 ori.
- **Fix sugerat:** Extrage `_mediana` si `_issues_outlier`.
- **Confidence:** certa

### CQ-03 — Duplicare jurnal audit
- **Locatie:** `routers/evaluare.py:169` vs `curent.py:263`
- **Lentila:** Cod-calitate
- **Descriere:** ~20 linii verbatim in ambele `audit.txt`.
- **Fix sugerat:** Extrage `construieste_jurnal_baza`.
- **Confidence:** certa

### PERF-2 — `localitate_din_url`: pana la 664 regex necompilate per candidat
- **Locatie:** `geo.py:44-58` din `descoperire.py:35-40`
- **Lentila:** Performanta
- **Descriere:** Itereaza toate slug-urile judetului (664 max, 13225 total) compiland `re.search` cu `re.escape` in f-string per iteratie, fara cache. O data per candidat (50) → circa 33.000 compilari per `descopera`.
- **Fix sugerat:** Tokenizeaza URL o data si cauta prin set-membership (cel mai lung match); optional `lru_cache` pe `(url, judet)`.
- **Confidence:** certa

### PERF-3 — curs BNR si indice ANEVAR fara cache (zilnic/trimestrial)
- **Locatie:** `curs_bnr.py:23-37`; `indice_anevar.py:99-116`
- **Lentila:** Performanta
- **Descriere:** `curs_bnr` face `requests.get` la fiecare apel desi cursul e zilnic; `indice_anevar` descarca + parseaza pagina live desi e trimestrial. Fara TTL → lovesc reteaua mereu.
- **Fix sugerat:** Cache cu TTL (curs pe zi, indice pe ore) via dict + `time.monotonic`; fallback offline neschimbat.
- **Confidence:** certa

### PERF-4 — `NEXT_DATA` `json.loads` de 3 ori + BeautifulSoup de 2 ori per anunt
- **Locatie:** `importers/url_parser.py:101-135,167-176,367`; `orchestrator.py:32-39,67`
- **Lentila:** Performanta
- **Descriere:** Per candidat, BeautifulSoup e construit de 2 ori pe acelasi HTML; blobul `NEXT_DATA` (sute KB) e `json.loads` de 3 ori. O(n) repetat de 3x.
- **Fix sugerat:** Un singur BeautifulSoup (paseaza `soup`) si un singur `json.loads` pe `NEXT_DATA`, dict-ul pasat catre cele trei functii.
- **Confidence:** certa

### PERF-5 — `aml_evalueaza` async face citire fisier blocanta necacheata pe event-loop
- **Locatie:** `web/routers/aml.py:103-124`; `aml/liste.py:61-67`
- **Lentila:** Performanta
- **Descriere:** `aml_evalueaza` e `async def` deci ruleaza pe event-loop, nu pe threadpool; cheama `incarca_liste` cu `read_text` + `json.loads` sincron la fiecare evaluare, fara cache. Blocheaza event-loop-ul sub sarcina.
- **Fix sugerat:** Fa handlerul `def` (threadpool) sau `run_in_threadpool`; cacheaza `incarca_liste` pe `mtime`.
- **Confidence:** certa

### PERF-6 — `/registru` re-citeste acelasi `dosar.json` de pana la 3 ori (N+1)
- **Locatie:** `web/routers/registru.py:103-122`; `registru/registru.py:141-164`; `dosare_fs.py:343-384`
- **Lentila:** Performanta
- **Descriere:** `randuri` face glob + `fs.listeaza` (read fiecare `dosar.json`) + `fs.incarca` per uid (a doua citire); `pagina_registru` cheama iar `fs.incarca` per uid pentru BIG (a treia). `pregateste_big` necacheat.
- **Fix sugerat:** Cacheaza dosarul complet o data si refoloseste-l pentru rand + BIG; sau memoizeaza `pregateste_big` pe `mtime`.
- **Confidence:** certa

### EH-01 — Fisier temporar `.docx` cu PII nu e sters niciodata (raport legacy)
- **Locatie:** `web/routers/evaluare.py:131-141` (`descarca_raport`)
- **Lentila:** Error-handling / silent-failures
- **Descriere:** In `descarca_raport` (calea legacy SQLite, inca inregistrata in `app.py`), raportul se scrie in `tempfile.gettempdir()/raport_{eid}.docx` si se returneaza cu `FileResponse(...)` FARA `background=`. Spre deosebire de `genereaza`/`_doc_response` (care ataseaza `BackgroundTask` de stergere), aici fisierul nu se sterge niciodata, nici pe succes. Nume PREDICTIBIL (fara token) → alt utilizator local poate citi/suprascrie un .docx cu PII (nume client, adresa, CNP).
- **Fix sugerat:** Scrie in fisier cu token unic + `background=BackgroundTask(lambda: Path(out).unlink(missing_ok=True))` la `FileResponse`.
- **Confidence:** certa

### EH-02 — Dosar omis TACIT din registrul oficial, fara urma in log
- **Locatie:** `registru/registru.py:156-161` (`randuri`)
- **Lentila:** Error-handling / silent-failures
- **Descriere:** `randuri()` (sursa canonica pentru `/registru` + exporturile CSV/XLSX — Procedura de arhivare ANEVAR §6) sare peste orice dosar cu `dosar.json` ilizibil/corupt la `except (KeyError, ValueError, TypeError): continue`. Skip-ul e doar comentat, NU logat (modulul nici nu importa un logger). Un raport poate disparea TACIT din registrul oficial; exporturile il omit fara ca evaluatorul sa stie.
- **Fix sugerat:** Adauga un logger si logheaza `log.warning("Dosar omis din registru (ilizibil/otravit) uid=%s: %s", uid, e)` inainte de `continue`; optional contor „dosare omise" in UI.
- **Confidence:** certa

### EH-03 — Inregistrarea integritatii + marcarea asumarii esueaza TACIT (cursa concurenta)
- **Locatie:** `dosare_fs.py:192-213` (`_inregistreaza_versiune`), apelat din `adauga_versiune_docx:169-184`
- **Lentila:** Error-handling / silent-failures
- **Descriere:** `_inregistreaza_versiune` la `try: dosar = incarca(uid) except (KeyError, ValueError): return` iese TACIT daca dosarul a fost sters/corupt intre copiere si reincarcare. In acea ramura NU se scriu: hash-ul de integritate, `asumat_la` (ADR-003), `blocat=True`, intrarea in `versiuni[]`. Totusi raportul iese cu 200 OK → dosar NEASUMAT/NEBLOCAT fara amprenta de integritate, contrar tamper-evidence SEV 2025/GEV 520. Fereastra ingusta, dar esec complet tacit pe cale critica de conformitate.
- **Fix sugerat:** Logheaza `log.warning("Versiune .docx neinregistrata ... uid=%s", uid)` in `except`, si/sau propaga eroare ca endpoint-ul de raport sa nu raporteze succes cand asumarea/integritatea nu s-au persistat.
- **Confidence:** probabila

### AML-LOGIC-1 — Maparea scopului din text liber alege riscul mai mic la cuvinte mixte
- **Locatie:** `aml/serviciu.py:41-75`
- **Lentila:** AML logic
- **Descriere:** In `_SCOP_AML_DUPA_CUVANT` cuvintele de risc redus preced pe cele de risc ridicat si se opreste la prima potrivire. Proba: „credit pentru achizitie" da `garantare_credit` (factor 1) desi contine „achizit" (factor 3). Scop mixt clasificat ca risc redus.
- **Fix sugerat:** Returneaza scopul cu factor maxim, nu prima potrivire.
- **Confidence:** certa

### AML-LOGIC-2 — BR neidentificat la PJ forteaza singur „sporit", contrar documentatiei
- **Locatie:** `aml/risc.py:118-127`
- **Lentila:** AML logic
- **Descriere:** BR (beneficiar real) neconsultat seteaza factor client 3, pondere 2; cu rest neutru → scor 2.333 peste pragul 2.2 → „sporit", desi comentariile spun ca nu forteaza singur. Testul 210-214 maskeaza.
- **Fix sugerat:** Muta la HARD sau scade ponderea.
- **Confidence:** certa

### CONF-01 — Scrisoarea de transmitere afirma neconditionat „valoarea de PIATA" — contrazice profilul ASIGURARE (SEV 450) si lichidare/justa
- **Locatie:** `report/generator.py:409-414` (`_scrisoare_transmitere`)
- **Lentila:** Conformitate raport (SEV/GEV)
- **Descriere:** `_scrisoare_transmitere` randeaza fix „valoarea de piata estimata ... este de {valoare} {moneda}", ignorand `meta.tip_valoare`. Pentru profilul ASIGURARE restul raportului eticheteaza corect „valoare de asigurare ... conform SEV 450", dar scrisoarea spune „valoarea de PIATA" → raport intern contradictoriu (SEV 102: piata ≠ asigurare/lichidare/justa). Atinsa de toate profilurile (apelata neconditionat in `genereaza_raport`).
- **Fix sugerat:** Foloseste eticheta derivata din tipul valorii: `_tip_valoare_txt(meta.tip_valoare)` sau text neutru „valoarea estimata ({tip valoare})".
- **Confidence:** certa

### CONF-02 — Coperta hardcodeaza „casa de locuit si teren aferent" pentru orice tip de imobil
- **Locatie:** `report/generator.py:371-372` (`_coperta`)
- **Lentila:** Conformitate raport (SEV/GEV)
- **Descriere:** `_coperta` scrie fix „Proprietate imobiliara: casa de locuit si teren aferent" fara ramificare pe tip, desi app-ul suporta 7 tipuri (`TipActiv`). Pentru apartament (fara teren in proprietate exclusiva — GEV 630 §118.a), teren liber, hala/spatiu comercial → mislabel pe identificarea proprietatii (SEV 106 / GEV 630 §110-112).
- **Fix sugerat:** Deriva descrierea din `profil.tip_activ` (mapare tip→eticheta).
- **Confidence:** certa

### CONS-01 — Moneda nationala „RON" in subsol vs „LEI" in tot restul aplicatiei
- **Locatie:** `web/templates/_footer.html:7`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** Subsolul (pe TOATE paginile) afiseaza „316.000,00 RON". Restul aplicatiei foloseste consecvent „LEI" (optiuni moneda, etichete, texte de curs). Singura aparitie „RON" e in `_footer.html:7`; toate celelalte 20+ sunt LEI/lei.
- **Fix sugerat:** Inlocuieste „RON" cu „LEI" in `_footer.html:7`.
- **Confidence:** certa

### CONS-02 — Simbol valuta neuniform: „€"/„€/mp" (UI vechi) vs „EUR"/„EUR/mp" (UI nou)
- **Locatie:** `grila.html:337,340`; `descoperire.html:245,405,429,744`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** Aceeasi marime afisata cu „€" in unele locuri si „EUR" in altele, neuniform intre UI vechi/nou si chiar in aceeasi pagina. UI nou (`dosar.html`) foloseste consecvent „EUR".
- **Fix sugerat:** Standardizeaza „EUR"/„EUR/mp" (ca in UI nou) in `grila.html` si `descoperire.html`, eliminand „€".
- **Confidence:** certa

### CONS-03 — Indicii decimale contradictorii in `dosar.html`: virgula la curs (normalizat) vs punct la rate (ne-normalizat)
- **Locatie:** `dosar.html:426` vs `433,436,445,313`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** `curs_valutar` arata „ex. 4,9750" (virgula, normalizat cu `.replace(",",".")` la L1414), dar `rata_cap`/`neocupare`/`rata_actualizare`/depreciere sugereaza punct si sunt trimise BRUT, fara normalizare. Un utilizator amorsat de hint-ul curs poate introduce „0,08" la rata, ramas ne-normalizat. `wizard.html` difera invers.
- **Fix sugerat:** Unifica indiciile decimale si aplica aceeasi normalizare virgula→punct pe toate campurile numerice.
- **Confidence:** certa

### CONS-04 — Lista „Tip proprietate" difera intre creare dosar (`/incepe`) si workspace (`dosar.html`)
- **Locatie:** `incepe.html:52-54` vs `dosar.html:141-144`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** Dropdown-ul din `/incepe` ofera 5 optiuni (LIPSESTE „comercial"); cel din workspace ofera 6 (cu „comercial"). Ambele alimenteaza acelasi camp, iar valoarea aleasa la creare intra in identitatea dosarului → utilizatorul nu poate alege „Comercial" la creare.
- **Fix sugerat:** Adauga `<option value="comercial">Comercial (generator de venit)</option>` in `incepe.html`.
- **Confidence:** certa

### TC-1 — Ramura de eroare BIG din routerul registru e netestata (422 + `eroare:True` nereachable de testele existente)
- **Locatie:** `web/routers/registru.py:114-120` si `:158-161`
- **Lentila:** Test-coverage
- **Descriere:** Ramurile `except (ValidationError, ValueError)` pentru dosare otravite sunt reachable dar neatinse de teste. Testele „otravit" existente folosesc `suprafata_teren=0` / `valoare_finala=-1`, convertite de `_pozitiv()` la None inainte de pydantic → calea fericita (200), nu ramura de eroare. Un `an_referinta` ne-numeric face `pregateste_big` sa arunce ValidationError → `/big` 422, `/registru` ramura `eroare:True`. Un refactor care slabeste `try/except` ar produce un 500 nedetectat.
- **Fix sugerat:** 2 teste cu `an_referinta` ne-numeric: (a) `/api/dosar/{uid}/big` → 422; (b) `/registru` → 200 cu pastila de eroare.
- **Confidence:** certa

### GF2 — Celulele grilei de ajustari nu au `id` → nu se salveaza automat (se pierd la reincarcare)
- **Locatie:** `dosar.html:778, 1466, 1523, 1577`
- **Lentila:** Gap-functional
- **Descriere:** `snapshot()` persista DOAR `main input/select/textarea` cu `id` (`if(e.id)`). Inputurile grilelor (`g-aj`, `gt-aj`, `gc-aj`, `g-pret`/`g-sup`) sunt generate cu `class`+`data-*` FARA `id` → toata grila de ajustari dispare la refresh. Combinat cu GF1, munca de gridding e efemera de doua ori.
- **Fix sugerat:** Aloca id-uri stabile (`g-aj-<e>-<i>`) sau serializeaza separat starea celor 3 grile in snapshot.
- **Confidence:** certa

### GF3 — Grila de ajustari plafonata rigid la 3 comparabile (NC=3), fara «adauga comparabil»
- **Locatie:** `dosar.html:1442, 1507, 1562`
- **Lentila:** Gap-functional
- **Descriere:** Cele 3 grile au `NC=3` hardcodat, fara control de a adauga a 4-a coloana. Un evaluator pentru garantare grileaza frecvent 4-6 comparabile (verificatorul bancar prefera >3). Plafonul forteaza sub-utilizarea comparabilelor sau editarea in textarea (ocolind grila, pierzand ajustarile — GF1).
- **Fix sugerat:** `NC` dinamic cu buton «+ comparabil» (re-render pastrand valorile); plafon superior rezonabil (~8).
- **Confidence:** certa

### GF4 — Metoda «Ponderata» selectabila, dar fara camp de pondere in UI (50/50 hardcodat tacit)
- **Locatie:** `dosar.html:421, 1431-1434`; `assembler.py:93, 239-240`
- **Lentila:** Gap-functional
- **Descriere:** Dropdown-ul ofera «Ponderata» dar `asambleaza()` nu seteaza niciodata `pondere_piata`; default 0.5 → reconciliere {comparatie:0.5, cost:0.5}. Un evaluator care alege ponderata NU poate seta ponderile (ex. 70/30) → primeste tacit 50/50. La garantare, justificarea ponderilor e asteptare standard.
- **Fix sugerat:** Input de pondere vizibil cand metoda=ponderata; trimite `pondere_piata`; afiseaza ponderea efectiva pe rezultat/raport.
- **Confidence:** certa

---

## 4. Findings LOW (20)

### SEC-A-02 — IndexError nehandelat (HTTP 500) la data-URL malformat pe `/incarca-submis` *(fuzionat cu CQ-04 mentiune)*
- **Locatie:** `web/routers/curent.py:375` (`incarca_submis`)
- **Lentile:** Securitate OWASP + Cod-calitate
- **Descriere:** `req.continut.split(",", 1)[1] if req.continut.startswith("data:")` fara garda `and "," in req.continut`. Un payload „data:...base64NOCOMMA" → `IndexError` nehandelat → HTTP 500. Siblings (`import_docx`, `ingestie`) au garda corecta (fix RUNDA 9); acesta a fost ratat. DoS minor + inconsecventa.
- **Fix sugerat:** `payload = req.continut.split(",",1)[1] if req.continut.startswith("data:") and "," in req.continut else req.continut`.
- **Confidence:** certa

### SEC-A-03 — „testserver" ramane permanent in allowlist-ul de host in productie
- **Locatie:** `web/app.py:72` (`_HOSTURI_LOCALE`)
- **Lentila:** Securitate OWASP
- **Descriere:** Garda anti-DNS-rebinding include „testserver" (host TestClient) si in productie → o cerere `Host: testserver` trece. Risc real scazut, dar e un afordament de test scurs in allowlist (igiena).
- **Fix sugerat:** Adauga „testserver" doar conditionat (var de mediu de test) sau injecteaza setul de hosturi in `create_app` si extinde-l din conftest.
- **Confidence:** probabila

### SEC-A-04 — SSRF: fereastra TOCTOU DNS-rebinding intre validare si fetch (limitare cunoscuta)
- **Locatie:** `importers/url_parser.py:494-535` (`_url_public_sigur` + `fetch_html`)
- **Lentila:** Securitate OWASP
- **Descriere:** `_url_public_sigur` rezolva hostname-ul si verifica IP-urile, apoi `requests.get` re-rezolva separat la conectare. DNS cu TTL=0 poate returna IP public la validare si IP intern (127.0.0.1 / 169.254.169.254) la conexiune. Apararea pe redirecturi e foarte buna; prima conexiune pastreaza fereastra. Limitare de defense-in-depth, nu breasa demonstrata (endpoint-uri local-only).
- **Fix sugerat:** Pin pe IP-ul validat (HTTPAdapter custom care forteaza IP-ul + pastreaza Host header), sau sesiune cu rezolvare cache-uita identica.
- **Confidence:** de-verificat

### R17-3 — Plafonul global de 50MB ocolibil prin `Transfer-Encoding: chunked`
- **Locatie:** `web/app.py:94-97` (`doar_host_local`)
- **Lentila:** Robustete
- **Descriere:** Garda anti-DoS se bazeaza EXCLUSIV pe `Content-Length`. Un request `chunked` fara `Content-Length` → `cl=None` → conditia se sare; `call_next` lasa corpul nemarginit sa fie buffer-uit/deserializat. Slabeste mitigarea pe care se bazeaza R17-1/R17-2. LOW (local-only + CSRF-gated pe Origin).
- **Fix sugerat:** Plafon si pe corpul STREAM-uit (413 la depasire), sau respinge lipsa `Content-Length` la metode mutante, sau limita la nivel uvicorn/Starlette.
- **Confidence:** de-verificat

### H6 — Comentariu spune 20 dar paginarea e 50
- **Locatie:** `dosar.html:1092,1139` (si `descoperire.html:569`)
- **Lentila:** Nielsen 10
- **Descriere:** `PAGINA=50` dar comentariile spun 20. Capcana de mentenanta.
- **Fix sugerat:** Aliniaza comentariile la 50.
- **Confidence:** certa

### H7 — AML accepta formular gol fara validare
- **Locatie:** `aml.html:123`
- **Lentila:** Nielsen 10
- **Descriere:** „Evalueaza" trimite cu campuri goale; eroarea de backend e generica. Risc scazut pe date inexistente.
- **Fix sugerat:** Valideaza clientul inainte de submit; propaga detaliul erorii.
- **Confidence:** probabila

### H8 — Etichete inconsistente „Importa" vs „Trimite la grila"
- **Locatie:** `dosar.html:1277` (vs `descoperire.html:754`)
- **Lentila:** Nielsen 10
- **Descriere:** „Importa" (dosar) vs „Trimite la grila" (descoperire) pentru aceeasi actiune.
- **Fix sugerat:** Un singur verb in ambele panouri.
- **Confidence:** certa

### A11Y-03 — Label orfana cu `for` inexistent; sub-tab programatic nu muta focusul
- **Locatie:** `dosar.html:363,809,1670,1743`
- **Lentila:** Accesibilitate WCAG 2.2 AA
- **Descriere:** (1) `label for=d-url-btn-l` trimite la un id inexistent (WCAG 1.3.1, impact minim). (2) Subtab face doar `click`; la nav-inainte/inapoi + `la-gen` focusul ramane pe controlul vechi, fara anunt de schimbare de context (WCAG 2.4.3).
- **Fix sugerat:** Inlocuieste label-ul cu `span aria-hidden` si scoate `for`. Muta focusul pe tab/panou (tabindex 0) la activari programatice.
- **Confidence:** probabila

### A11Y-04 — Emoji fara text alt; lipsa `aria-current` in nav; stare „done" stepper doar CSS
- **Locatie:** `dosar.html:951,1024,777`; `_nav_cross.html:7-14`; `flux_livrabile.html:24-25`
- **Lentila:** Accesibilitate WCAG 2.2 AA
- **Descriere:** (1) Emoji calendar/scan/salvare fara `aria-hidden`, citite inconsecvent de SR (WCAG 1.1.1). (2) Niciun link cross-ui nu primeste `aria-current=page` desi stilul exista (WCAG 2.4.8). (3) `fl-step done` foloseste `font-size:0` + pseudoelement pentru bifa, neexpus consecvent de SR (WCAG 1.3.1).
- **Fix sugerat:** Infasoara emoji in `span aria-hidden`; adauga conditional `aria-current=page`; adauga `span sr-only` „finalizat" pe pasul done.
- **Confidence:** probabila

### CQ-04 — Igiena: helpere dublate, `descopera` lunga, importuri locale, base64 dublat, mediana, walk `__NEXT_DATA__` 3x
- **Locatie:** `orchestrator.py:159,257`; `curent.py:122,375`; `url_parser.py:95,161`; `validation.py:44,67`
- **Lentila:** Cod-calitate
- **Descriere:** Helpere `_acum`/`_luni_intre`/`_to_decimal`/`_parse_data` dublate cross-modul; `descopera()` ~85 linii; importuri functie-locale repetate; base64 dublat (incarca_submis fara garda virgula → 500, vezi SEC-A-02); `mediana = eur_mp[len//2]` nereala; walk `__NEXT_DATA__` de 3x (vezi PERF-4).
- **Fix sugerat:** Centralizeaza helpere; `_imbogateste_profil`; promoveaza importuri; `_decodeaza_upload` + garda; `statistics.median`; `_incarca_nextdata`.
- **Confidence:** probabila

### PERF-7 — `config_efectiv`/`ponderi_efective` re-citesc override JSON de mai multe ori per request
- **Locatie:** `engine/metodologie_store.py:24-39`; `curent.py:52-54,242,336,346`
- **Lentila:** Performanta
- **Descriere:** `config_efectiv` re-citeste `metodologie_override.json` fara cache; `_metodologie_cfg` apelat 2x in calcul, 3x+ in raport.docx. Read + parse redundant per request.
- **Fix sugerat:** Calculeaza configul o data per request si paseaza-l, sau cacheaza `incarca_override` pe `mtime`.
- **Confidence:** probabila

### PERF-8 — `/api/localitati` reconstruieste maparea a 13.000 localitati per cerere, fara cache
- **Locatie:** `web/routers/piata.py:107-111`
- **Lentila:** Performanta
- **Descriere:** Construieste maparea slug→localitati pentru 42 judete (13.225 intrari, 646KB) la fiecare request; `_load` e `lru_cache` dar comprehension-ul + serializarea se refac mereu.
- **Fix sugerat:** Memoizeaza payload-ul asamblat (`lru_cache maxsize=1`) sau ETag/Cache-Control.
- **Confidence:** probabila

### PERF-9 — `construieste_context` + narativ AI (7 capitole seriale) refacut pe fiecare endpoint
- **Locatie:** `web/routers/curent.py:56-61`; `ai/narrative.py:199-212`
- **Lentila:** Performanta
- **Descriere:** `calcul`/`calitate`/`raport.docx` reconstruiesc integral contextul pe acelasi input; cu AI activ, `generate_narrative` face 7 apeluri LLM secventiale per raport.
- **Fix sugerat:** Paralelizeaza cele 7 apeluri narative; optional cache scurt pe hash-ul inputului.
- **Confidence:** de-verificat

### EH-04 — Fisier `.docx` temporar cu PII ramane orfan pe calea de eroare a generarii
- **Locatie:** `web/routers/curent.py:350-362` (`genereaza`)
- **Lentila:** Error-handling / silent-failures
- **Descriere:** Task-ul `_sterge(out)` se ataseaza DOAR pe calea de succes. Daca `genereaza_raport`/`adauga_versiune_docx` arunca (disc plin, docx corupt, dosar sters concurent), exceptia se propaga (500) iar `out` cu PII ramane in tempdir. Spre deosebire de EH-01, aici exista curatare pe succes; lipseste pe eroare.
- **Fix sugerat:** `try/except` care sterge `out` (`unlink(missing_ok=True)`) inainte de re-arunca, sau context manager cu cleanup garantat.
- **Confidence:** certa

### EH-05 — Cont evaluator corupt → tratat TACIT ca «inexistent» (identitate posibil pierduta la suprascriere)
- **Locatie:** `cont.py:21-29` (`incarca_cont`) + `salveaza_cont:32-43`
- **Lentila:** Error-handling / silent-failures
- **Descriere:** `incarca_cont` face `except (OSError, ValueError): return None`. Un `cont.json` care EXISTA dar e corupt e indistinct de «niciun cont», fara log. In aval (`import_docx`: „Creeaza intai un cont") userul e derutat, iar `salveaza_cont` SUPRASCRIE fisierul, pierzand tacit identitatea/legitimatia (care apare pe rapoarte + registru).
- **Fix sugerat:** Logheaza `log.warning("cont.json ilizibil ... tratat ca inexistent")`; optional redenumeste in `cont.json.corupt` inainte de suprascriere.
- **Confidence:** probabila

### AML-LOGIC-3 — Prag PEP 12 luni off-by-one; data viitoare tacita; scop necunoscut neutru; indicatori grei nu urca categoria
- **Locatie:** `aml/risc.py:71-87`; `serviciu.py:61-75`; `indicatori.py:43-54`
- **Lentila:** AML logic
- **Descriere:** (a) `pep_efectiv` cere luni strict sub 12; la exact 12 da False, dar legea spune „cel putin 12 luni". (b) Data incetare dupa azi → luni negative care trec pragul → `pep=True`, tacit. (c) Scop necunoscut da factor produs neutru fara legatura cu `scop_nedefinit`; indicatorii grei (antecedente_penale, drepturi_litigioase, pep_implicat) declanseaza doar RTS, nu urca categoria.
- **Fix sugerat:** (a) `<= 12`. (b) Avertisment cand data incetare e dupa azi. (c) Confirma cu juristul daca scop nedefinit + indicatorii grei contribuie la scor.
- **Confidence:** de-verificat

### CONF-03 — Sectiunea de lichidare echivaleaza „valoarea de lichidare" cu „vanzare fortata" — baze distincte in SEV 102
- **Locatie:** `report/generator.py:819-825` (`_adauga_risc_garantie`)
- **Lentila:** Conformitate raport (SEV/GEV)
- **Descriere:** Titlul „Valoarea de lichidare (vanzare fortata):" trateaza cei doi termeni ca sinonimi. In SEV 102 sunt baze/ipoteze DISTINCTE. GEV520-2025-crosscheck #20 le trateaza impreuna ca uzanta de garantare (factor 0,85), deci impact mic.
- **Fix sugerat:** „Valoare in ipoteza unei vanzari intr-un termen limitat (vanzare fortata)" sau separa explicit cele doua concepte.
- **Confidence:** de-verificat

### CONS-05 — Format numar neuniform in `grila.html`: `toLocaleString` fara zecimale vs `fmtRo` (2 zecimale)
- **Locatie:** `grila.html:340` vs `394,419-426`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** Pretul terenurilor descoperite e `(+c.pret).toLocaleString('ro-RO')` (fara zecimale), in timp ce rezultatele grilei folosesc `fmtRo()` (2 zecimale). „316.000" intr-un tabel, „316.000,00" in altul, pe aceeasi pagina.
- **Fix sugerat:** Inlocuieste cu `fmtRo(c.pret)` la `grila.html:340`.
- **Confidence:** certa

### CONS-06 — Lipsa diacritice in etichete vizibile pe `descoperire.html` (UI vechi neactualizata)
- **Locatie:** `descoperire.html:128,140,142`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** „Judet:" (corect „Județ"), „Incalzire" (corect „Încălzire"), „Stare(1-5)" fara spatiu. Restul aplicatiei foloseste diacritice corecte; `descoperire.html` e singura pagina cu etichete ASCII.
- **Fix sugerat:** „Județ:", „Încălzire", „Stare (1–5)".
- **Confidence:** certa

### D-01 / CONS-07 — Comportament neuniform al datei implicite; pagini vechi cu date hardcodate stale *(fuzionat: H4 + CONS-07 + UJ-REST partial)*
- **Locatie:** `aml.html:48`; `form.html:44,49`; `wizard.html:118,122` vs `curent/dosar.html` (azi dinamic)
- **Lentile:** Nielsen 10 + Consistenta cross-pagina + UX journey
- **Descriere:** `aml.html` „Data evaluării" hardcodata la `2026-06-03` (fara `max=azi`, accepta date viitoare, injectata in RTS); `form.html`/`wizard.html` hardcodate la `2026-01-16`; UI nou (`dosar.html`/`incepe.html`) auto-completeaza cu data de azi. Paginile vechi arata o data fixa stale; aml.html accepta date viitoare desi `dosar.html` pune `max=azi`.
- **Fix sugerat:** Elimina value-urile hardcodate; pre-completeaza cu data curenta + `max=azi` (ca in UI nou), sau lasa goale consecvent.
- **Confidence:** certa

### CONS-08 — Eticheta butonului de generare raport (si „cu note") difera intre pagini *(fuzionat cu H8 partial)*
- **Locatie:** `dosar.html:484-485`; `flux_livrabile.html:218-219`; `wizard.html:362`; `result.html:34-35`
- **Lentile:** Consistenta cross-pagina + Nielsen 10
- **Descriere:** Aceeasi actiune are etichete diferite: „Generează și descarcă raportul (.docx)" / „...raportul" / „...raportul .docx" / „Descarcă raportul .docx". Butonul secundar: „Raport cu note (demo)" / „(review)" / „cu note".
- **Fix sugerat:** Standardizeaza un singur text principal („Generează și descarcă raportul (.docx)") si secundar („Raport cu note") in cele 4 sabloane.
- **Confidence:** certa

### CONS-09 — Etichete AML prescurtate diferit intre `/aml` si AML-ul incorporat in `dosar.html`
- **Locatie:** `aml.html:104,114,115,117` vs `dosar.html:537,544,545,547`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** Aceiasi indicatori (value-urile coincid, backend consistent) au etichete vizibile diferite: „Tranzacție complexă / neobișnuită" vs „Tranzacție complexă", etc. Acelasi check cu text diferit pe doua ecrane.
- **Fix sugerat:** Aliniaza textul checkbox-urilor AML din `dosar.html` cu `aml.html`, pastrand value-urile.
- **Confidence:** certa

### CONS-10 — Etichete metode/DCF si Au/Acd divergente intre UI vechi (form/wizard) si UI nou (dosar)
- **Locatie:** `form.html:59,64,82`; `wizard.html:196,200,295,298,312-319` vs `dosar.html:302,303,420-422,442-446`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** Concepte identice, etichete diferite: „Au — arie utilă" vs „Arie utilă"; „Piață (comparație)" vs „Piață (grilă de comparație)" vs „Piață"; „Venit — DCF" vs „DCF"; id-uri/label-uri DCF diferite; „Categorie de folosință" vs „Categorie folosință".
- **Fix sugerat:** Uniformizeaza etichetele intre `wizard.html`/`form.html` si `dosar.html`; daca UI vechi e depreciat, documenteaza-l.
- **Confidence:** certa

### CONS-11 — Format data in liste: ISO afisat brut, desi exista helper `dd.mm.yyyy` nefolosit
- **Locatie:** `incepe.html:80,84,137`; `feedback_list.html:27`; `dosare.html:37`
- **Lentila:** Consistenta cross-pagina
- **Descriere:** Listele afiseaza data ISO „yyyy-mm-dd hh:mm:ss" brut din server, desi `incepe.html` defineste `roData()` (→ `dd.mm.yyyy`) folosit DOAR la numele dosarului. Utilizatorul vede ISO in liste, dar conventia ro-RO e sugerata altundeva.
- **Fix sugerat:** Aplica formatarea ro-RO (`roData`) la coloanele de data din tabele.
- **Confidence:** probabila

### TC-2 — Ramura „data inspectiei ulterioara datei evaluarii" din QC coerenta e netestata
- **Locatie:** `calitate.py:166-167` (`_item_coerenta`)
- **Lentila:** Test-coverage
- **Descriere:** `_item_coerenta` are 3 semnale; testele acopera moneda + data raportului < evaluare, dar NICIUN test nu seteaza `data_inspectiei > data_evaluarii`. Un mutant care inverseaza comparatia ar supravietui.
- **Fix sugerat:** Caz `_ctx(meta_over={"data_evaluarii":"2026-01-16","data_inspectiei":"2026-02-01"})`; aserteaza `trecut is False`, `nivel=="alerteaza"`, emisibil ramane True.
- **Confidence:** certa

### TC-3 — Ramura „tip valoare nealiniat profilului" din QC adecvare e netestata
- **Locatie:** `calitate.py:199-203` (`_item_adecvare`, `_RADACINA_TIP_VALOARE`)
- **Lentila:** Test-coverage
- **Descriere:** A doua ramura (tip valoare ne-aliniat, ex. profil „piata" dar `meta.tip_valoare` = „Valoare de investitie") nu e acoperita. Mutarea verificarii sau a dict-ului nu ar fi prinsa.
- **Fix sugerat:** Test cu profil radacina „piata" dar `meta.tip_valoare` alt tip; aserteaza `adecvare_scop.trecut is False` + mesaj de nealiniere de tip valoare.
- **Confidence:** probabila

### GF5 — Lipsa camp de justificare per ajustare in UI, desi modelul si raportul il sustin
- **Locatie:** `dosar.html:1477,1533,1587`; `models/comparable.py:30`
- **Lentila:** Gap-functional
- **Descriere:** `Adjustment.justificare: str` exista, dar UI-ul construieste fiecare ajustare doar ca `{element, tip, valoare, etapa}`, fara cale de a introduce justificarea. SEV 103 §20.5 / A10.8 cer justificarea ajustarilor nenule. Combinat cu GF1, ajustarile oricum nu ajung in raport.
- **Fix sugerat:** Nota de justificare per ajustare nenula (al doilea rand/tooltip), serializata in `adjustments[].justificare`.
- **Confidence:** certa

### GF6 — Metoda liniara de depreciere (`durata_viata_totala`) acceptata de backend, dar neexpusa in UI
- **Locatie:** `dosar.html:312-313`; `models/property.py:46`; `engine/cost.py:176-182`
- **Lentila:** Gap-functional
- **Descriere:** Backend-ul accepta tabel de interpolare SAU metoda liniara pe `durata_viata_totala`, dar UI ofera DOAR textarea „Depreciere fizica (varsta → fractie)". Tabel gol la metoda cost → `ValueError` → 422, desi metoda liniara (uzuala) ar fi rezolvat. Plus: textarea cere fractia 0-1 fara hint clar ca „31" (procent) e respins cu 422 generic.
- **Fix sugerat:** Camp „durata de viata totala (ani)" ca alternativa (folosit cand tabelul e gol); valideaza/hint fractie vs procent.
- **Confidence:** certa

---

## 5. Note de prioritizare

- **Cluster „grila → raport" (GF1+GF2+GF3+GF4+GF5):** cea mai consistenta deficienta functionala. GF1 (HIGH) este radacina — ajustarile evaluatorului nu ajung in raport — iar restul amplifica (pierdere la refresh, plafon rigid, pondere ascunsa, fara justificare). Merita tratat ca un singur efort de „conectare a grilei la motor".
- **Cluster „PII temporar .docx" (EH-01, EH-04):** doua scurgeri de fisiere cu date personale (una pe succes-legacy, una pe eroare). Mici ca efort, importante ca expunere de date.
- **Cluster „cache/N+1" (PERF-3, PERF-4, PERF-5, PERF-6, PERF-7, PERF-8):** castiguri de performanta cu risc scazut; PERF-1/PERF-2 (HIGH/MED) au cel mai mare impact pe latenta perceputa.
- **Cluster AML (AML-LOGIC-1, AML-LOGIC-2, AML-LOGIC-3):** logica de risc — necesita confirmare juridica inainte de modificare (vezi politica AML din memorie: text juridic AML detinut de loop-ul autonom, pending jurist). NU implementa autonom.
- **Cluster „consistenta cross-pagina" (CONS-01..11):** majoritar cosmetic/copy; UI vechi (`form.html`, `wizard.html`, `descoperire.html`, `grila.html`) ramane in urma UI-ului nou (`dosar.html`). Decizie de produs: aliniat vs depreciat.
- **Conformitate raport (CONF-01, CONF-02):** mislabel-uri randate care contrazic standardul (scrisoare „valoare de piata" pe profil asigurare; coperta „casa+teren" pe orice tip). Risc la verificarea bancara — prioritate inaintea cosmeticelor.

> Toate fixurile de mai sus sunt **propuneri**. Niciun cod nu a fost modificat. AML si textul juridic necesita aprobare jurist; gap-urile functionale (GF*) si conformitatea (CONF*) sunt decizii de produs.
