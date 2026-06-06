# Inventar complet de controale — DIFF UI vechi → UI nou

> Audit literal, control cu control. Sursă „vechi": `wizard.html`, `descoperire.html`, `grila.html`, `aml.html`, `form.html`.
> Sursă „nou": `curent/dosar.html`, `curent/incepe.html`, `curent/cont.html`.
> Legendă **În UI nou?**: ✅ = echivalent funcțional complet · 🟡 = parțial / există dar diferit / reachabil doar prin link la pagina veche · ❌ = lipsește complet.
> Legendă **Impact**: critic (blochează un flux de conformitate/calcul) · mare (funcție utilă pierdută) · mic (cosmetic / redundant).

Notă de context pentru navigare: UI-ul nou (`dosar.html`) păstrează un link „Grile ↗" către `/grila` și bara `_nav_cross.html` linkează `/wizard` (UI vechi). Deci paginile vechi rămân **reachabile**, dar NU sunt integrate în workspace-ul nou. Acolo unde singurul acces e prin link la pagina veche, marchez 🟡 (nu ✅), fiindcă owner-ul cere paritate în UI-ul nou, nu doar „undeva în aplicație".

---

## A. Identificare / lucrare (Pas 1 wizard + form.html)

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `doc-tip` (cf/releveu/plan/cpe) | select | Tip document pentru import/ingestie PDF | ❌ | Nu există ingestia PDF în UI nou | mare |
| `doc-ingestie` | input file (PDF) | Pre-completare câmpuri din PDF (cadastral, CF, suprafețe, arii) | ❌ | Lipsește complet pornirea rapidă „importă din PDF" | mare |
| `ingestie-status` | span status | Feedback ingestie | ❌ | — | mic |
| `judet` (wizard) | select (din /api/localitati) | Județ din listă, cu nume diacritice + slug auto | 🟡 | `judet` în nou e **input text liber** (fără listă, fără diacritice auto) | mare |
| `localitate` (wizard) | select (din /api/localitati) | Localitate din listă, nume diacritice + slug auto | 🟡 | `localitate` în nou e **input text liber** (fără listă populată din API) | mare |
| `localitate_alt` | input | „Altă localitate" (cod fără diacritice) | 🟡 | Acoperit implicit de input liber, dar fără logica slug | mic |
| `adresa_strada` | input | Stradă, număr | ✅ | `adresa_strada` (Proprietate) | — |
| `client_nume` | input | Nume client | ✅ | `nume_client` (Proprietate) | — |
| `proprietar` | input | Proprietar dacă diferă de client | ❌ | Nu există câmp `proprietar` în nou (nici în meta payload) | mare |
| `numar_cadastral` | input | Nr. cadastral | ✅ | `numar_cadastral` | — |
| `carte_funciara` | input | Carte funciară | ✅ | `carte_funciara` | — |
| `beneficiar` | input | Beneficiar / bancă | ✅ | `beneficiar` | — |
| `scop` | select (5 opțiuni) | Scopul evaluării | ✅ | `scop` (aceleași 5 opțiuni) | — |
| `evaluator_nume` | input | Evaluator (persistă între sesiuni) | 🟡 | Mutat în pagina `/cont` (`nume`); nu se editează din dosar | mic |
| `evaluator_legitimatie` | input | Legitimație ANEVAR | 🟡 | Mutat în `/cont` (`legitimatie`) | mic |
| `data_evaluarii` | input date | Data evaluării | ✅ | `data_evaluarii` | — |
| `data_raportului` | input date | Data raportului | ✅ | `data_raportului` | — |
| `data_inspectiei` | input date | Data inspecției (opțional) | ✅ | `data_inspectiei` („Data vizită") | — |

---

## B. Proprietatea subiect — date fizice per tip (Pas 2 wizard)

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `tip_proprietate` (5 opțiuni) | select | Tip proprietate → câmpuri dinamice | ✅ | `tip_proprietate`, cu `aplicaTip()` identic | — |
| `etaj` | input number | Etaj (apartament) | ✅ | `etaj` (fieldset ap-fields) | — |
| `nr_niveluri_bloc` | input number | Niveluri bloc | ✅ | `nr_niveluri_bloc` | — |
| `an_bloc` | input number | An construcție bloc | ✅ | `an_bloc` | — |
| `cota_teren_indiviza` | input | Cotă teren indiviză (mp) | ✅ | `cota_teren_indiviza` | — |
| `inaltime_libera` | input | Înălțime liberă (industrial) | ✅ | `inaltime_libera` (ind-fields) | — |
| `categorie_folosinta` | select | Categorie folosință (agricol) | ✅ | `categorie_folosinta` | — |
| `clasa_calitate` | input number | Clasă calitate 1–5 (agricol) | ✅ | `clasa_calitate` | — |
| `suprafata_teren` | input | Suprafață teren (mp) | ✅ | `suprafata_teren` | — |
| `valoare_teren` | input | Valoare teren (lei) | ✅ | `valoare_teren` | — |
| `au` | input | Arie utilă | ✅ | `au` | — |
| `acd` | input | Arie construită desfășurată | ✅ | `acd` | — |
| `an_referinta` | input | An referință (vârstă) | ✅ | `an_referinta` | — |
| `elemente` | textarea | Elemente de cost (IROVAL) | ✅ | `elemente` | — |
| `depreciere` | textarea | Depreciere fizică (vârstă;fracție) | ✅ | `depreciere` | — |

---

## C. Comparabile — descoperire inline (Pas 3 wizard)

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `attr_an` | input | An construcție subiect (potrivire) | ✅ | `d-an` (subtab Comparabile) | — |
| `attr_stare` (select 1–5, etichete) | select | Stare construcție | 🟡 | `d-stare` e **input number** (fără etichetele „Degradată/Nouă") | mic |
| `attr_finisaj` (select 1–4, etichete) | select | Nivel finisaj | 🟡 | `d-finisaj` e **input number** (fără etichete) | mic |
| `attr_incalzire` | input | Tip încălzire (normalizat) | ✅ | `d-incalzire` | — |
| (teren subiect → potrivire) | (din suprafata_teren) | Teren ca atribut | ✅ | `d-teren` | — |
| `atribute_secundare` | textarea | Atribute secundare FYI (AI verifică în anunț) | ❌ | În nou `atribute_secundare:[]` e **hardcodat gol** — câmpul nu există în UI | mare |
| `btn-descopera` | button | Descoperă comparabile în zonă | ✅ | `d-cauta` „Caută comparabile" | — |
| `desc_status` | span | Status căutare | ✅ | `d-status` | — |
| `candidati` (listă + checkbox `.bif`) | container | Candidați bifabili, tabel atribute, explicații | 🟡 | `d-rezultate`: bifabil + relevanță + explicație, dar **fără tabelul de atribute** (Criteriu/Referință/Găsit/d/Pondere) și fără secundare | mare |
| `url_import_w` | input | Link anunț individual (imobiliare/storia) | ❌ | Nu există import-din-URL individual în UI nou | mare |
| `btn-import-url` | button | Import din URL | ❌ | — | mare |
| `import_url_status` | span | Status import URL | ❌ | — | mic |
| `comparabile` | textarea | Comparabile grilă (preț;suprafață) | ✅ | `comparabile` | — |
| (n/a în wizard) | textarea | — | ➕ | `comparabile_teren` — **nou are în plus** comparabile teren inline | (bonus) |

---

## D. Descoperire comparabile — pagina dedicată (descoperire.html)

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `portal` (select) | select | imobiliare.ro / storia.ro | ✅ | `d-portal` în dosar | — |
| `judet` / `localitate` | input | Zona căutare | ✅ | `d-judet` / `d-localitate` | — |
| `an`/`stare`/`finisaj`/`incalzire`/`teren` | input | Casa subiect (potrivire) | ✅ | `d-an`…`d-teren` | — |
| `secundare` | textarea | Atribute secundare | ❌ | Lipsește în nou (vezi C) | mare |
| submit „Caută comparabile" | button | Pornește căutarea | ✅ | `d-cauta` | — |
| `#metodologie` (tabel scoring) | render | Tabel metodologie ponderi/cote/formulă d | ❌ | Nu se afișează metodologia scoring în nou | mic |
| tabel atribute per candidat | render | Criteriu/Referință/Găsit/d/Pondere | 🟡 | Lipsește în render-ul inline din nou | mare |
| badge relevanță (high/mid/low) | render | Cod culoare relevanță | ✅ | badge b-high/b-mid în nou | — |
| „Copiază comparabilele bifate" | button | Copiază preț;suprafață în `<pre>` | ❌ | Nu există în nou (importul direct le pune în textarea) | mic |
| „Trimite bifatele la grila casă" (`laGrila`) | button | Prefill grilă casă (localStorage) | 🟡 | În nou „Importă bifate în grilă" pune în textarea `comparabile`, NU în grila casă din `/grila` | mic |
| **Secțiune „Anunțuri importate din extensie"** | section | Coadă din extensia de browser | ❌ | Lipsește complet în UI nou | mare |
| `lista-importate` (checkbox `.bif-import`) | render | Anunțuri din extensie, bifabile | ❌ | — | mare |
| `laGrilaImport` | button | Trimite bifatele la grila casă | ❌ | — | mare |
| `goleseImport` | button | Golește coada extensie | ❌ | — | mic |
| `sterge-unul` (per anunț) | button | Scoate un anunț din coadă | ❌ | — | mic |

---

## E. Grile de ajustare — teren / casă / chirii (grila.html)

> Întreaga pagină `/grila` NU e integrată în UI-ul nou. UI-ul nou doar **linkează** `/grila` (target _blank) din subtab-ul Comparabile. Deci grilele detaliate (ajustări secvențiale pe etape) sunt 🟡 „reachabile via link", nu native în dosar.

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| Tab `tab-teren` / `tab-casa` / `tab-chirii` | tab | Comutare tip grilă | 🟡 | Doar link `/grila`; nu în dosar | mare |
| Buton „↻ Indicele ANEVAR" (`incarcaIndice`) | button | Indice imobiliar ANEVAR (ajustare timp) | 🟡 | Doar în `/grila`; nu în dosar | mare |
| `indice-status` / `indice-rez` | render | Tabel variație %/trimestru | 🟡 | idem | mare |
| **Grilă teren**: input `data-pret` × N comp | input | Preț EUR/mp comparabile | 🟡 | Doar `/grila`. În dosar există doar `comparabile_teren` (preț/mp;supr, fără ajustări) | mare |
| 17 elemente ajustare teren (Ofertă→Tranzacție, Drept proprietate, Finanțare, Condiții vânzare, Cheltuieli post-vânzare, Condițiile pieței, Localizare, Acces, Utilități, Suprafață, Deschidere, Înclinație, Tip teren, Document urbanistic, Regim juridic, Regim economic, Indicatori urbanism) | input × N | Ajustări % pe element | 🟡 | Doar `/grila`. Ajustările detaliate pe etape lipsesc din dosar | mare |
| `supr-teren` | input | Suprafață teren subiect | 🟡 | Doar `/grila` (în dosar e `suprafata_teren`, dar fără calcul grilă) | mare |
| „Calculează grila teren" | button | Calcul valoare teren din grilă | 🟡 | Doar `/grila` | mare |
| **Descoperă terenuri în zonă**: `t-portal`/`t-judet`/`t-loc` | select+input | Căutare terenuri reale → €/mp | ❌ | Lipsește complet (nici în dosar, doar parțial în pagina /grila veche) | mare |
| „Caută terenuri" (`descoperaTeren`) | button | /api/descopera-teren | ❌ | Nu există descoperire teren în UI nou | mare |
| `t-add` „➕ grilă" (per teren găsit) | button | Pune €/mp în grila teren | ❌ | — | mare |
| **Grilă casă**: `data-pret` + `data-supr` × N | input | Preț ofertă + suprafață comp | 🟡 | Doar `/grila` | mare |
| 16 elemente ajustare casă (Negociere, Componente non-imobiliare, Drept proprietate, Finanțare, Condiții vânzare, Condițiile pieței, Localizare, Suprafață teren EUR/mp, Arie utilă EUR, Destinație, PIF/vechime, Acces, Curte, Finisaje, Sistem încălzire, Alte elemente) | input × N | Ajustări %/valorice | 🟡 | Doar `/grila` | mare |
| `supr-casa` (ACD subiect) | input | Suprafață subiect ACD | 🟡 | Doar `/grila` | mare |
| „Calculează grila casă" | button | Calcul valoare prin comparație | 🟡 | Doar `/grila` | mare |
| **Grilă chirii**: `data-pret` (chirie/mp) × N | input | Chirie EUR/mp/lună comparabile | 🟡 | Doar `/grila` | mare |
| 9 elemente ajustare chirii (Ofertă→Contract, Condițiile pieței, Localizare, Suprafață, Etaj/poziție, Finisaje/stare, Dotări, Destinație, Cheltuieli incluse) | input × N | Ajustări chirie | 🟡 | Doar `/grila` | mare |
| `supr-chirii` | input | Suprafață închiriabilă subiect | 🟡 | Doar `/grila` | mare |
| „Calculează grila chirii" | button | Venit brut potențial anual | 🟡 | Doar `/grila` | mare |
| „➕ trimite VBP în wizard" (`trimiteVbpWizard`) | button | Trimite VBP → wizard metoda venit (localStorage) | ❌ | Lipsește; în nou VBP se introduce manual în `vbp`, fără punte din grila chirii | mare |

---

## F. Calcul / metode (Pas 4 wizard + form.html)

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `adresa_raport` | textarea | Adresă cu diacritice pentru raport | ❌ | Lipsește; în nou adresa se compune din `adresa_strada+localitate+judet` (fără editare diacritice dedicată) | mare |
| `metoda` (5 opțiuni: cost/piață/ponderată/venit/dcf) | select | Metoda de calcul | ✅ | `metoda` (aceleași 5) | — |
| `vbp` | input | Venit brut potențial (venit) | ✅ | `vbp` (grup-venit) | — |
| `neocupare` | input | Grad neocupare | ✅ | `neocupare` | — |
| `cheltuieli` | input | Cheltuieli exploatare | ✅ | `cheltuieli` | — |
| `rata_cap` | input | Rată capitalizare | ✅ | `rata_cap` | — |
| `dcf_fluxuri` | textarea | Fluxuri anuale DCF | ✅ | `fluxuri` (grup-dcf) | — |
| `dcf_rata` | input | Rată actualizare DCF | ✅ | `rata_actualizare` | — |
| `dcf_rezidual` | input | Valoare reziduală DCF | ✅ | `valoare_reziduala` | — |
| `moneda` (EUR/LEI) | select | Monedă raportare | ✅ | `moneda` | — |
| `curs_valutar` | input | Curs EUR/LEI | ✅ | `curs_valutar` | — |
| `btn-curs-bnr` „↻ Curs BNR (azi)" | button | Preia curs BNR oficial | 🟡 | În nou se ia **automat** când moneda=EUR (`tragCurs`); NU există buton manual de reîmprospătare | mic |
| `curs_status` | span | Status curs | ✅ | `curs-info` | — |
| `foto` | input file (image multiple) | Fotografii Anexa 2 | ✅ | `up-foto` (subtab Anexe) | — |
| `foto-preview` (+ buton „șterge" per poză) | render | Previzualizare + ștergere foto | 🟡 | `lista-foto` afișează thumb-uri dar **fără buton de ștergere individuală** | mic |
| `doc` | input file | Documente scanuri Anexa 3 | ✅ | `up-doc` | — |
| `doc-preview` (+ „șterge") | render | Previzualizare + ștergere doc | 🟡 | `lista-doc` listează dar **fără ștergere individuală** | mic |
| `btn-calc` „Calculează" | button | Calcul valoare | ✅ | `calc` „Calculează" | — |
| `rezultat-calc` (+ alerte validare) | render | Valoare finală + alerte (blochează/avertizează) | 🟡 | `rezultat` afișează valoarea, dar **NU randează lista de alerte** `res.alerte` (outlier, prea puține comp, ajustare mare) | mare |
| (form.html) `metoda` 3 opțiuni | select | cost/piață/ponderată | ✅ | acoperit de `metoda` (5 opțiuni) | — |
| (form.html) `url_import` + `btn_import` | input+button | Import URL → comparabile | ❌ | Vezi C (lipsește import URL) | mare |

---

## G. Generare raport (Pas 5 wizard)

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `btn-raport` „Generează și descarcă .docx" | button | Generează raportul | ✅ | `genereaza` (gated de checkbox asumare) | — |
| `btn-raport-demo` „Raport cu note (demo)" | button | Raport cu adnotări proveniență | ✅ | `genereaza-demo` | — |
| `btn-audit` „Urmă de audit (.txt)" | button | Descarcă urma de audit | ✅ | `gen-audit` (+ tab Audit dedicat) | — |
| `link-raport` | render status | Mesaj „întâi calculează" | ✅ | `gen-status` | — |
| (n/a vechi) checkbox `asumare` | checkbox | Asumare profesională (blochează generarea) | ➕ | **Nou are în plus** gate de asumare | (bonus) |

---

## H. AML / KYC (aml.html)

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `tip_entitate` (PFA/PJ) | select | Tip entitate evaluator | ✅ | `aml_tip_entitate` | — |
| `azi` | input date | Data evaluării AML | ✅ | `aml_azi` | — |
| `tip_client` (PF/PJ) | select | Tip client (toggle PJ) | ✅ | `aml_tip_client` | — |
| `nume` / `prenume` / `cnp` | input | Date client PF | ✅ | `aml_nume` / `aml_prenume` / `aml_cnp` | — |
| `pep` | checkbox | Client/BR este PEP | ✅ | `aml_pep` | — |
| `denumire` / `cui` (PJ) | input | Date persoană juridică | ✅ | `aml_denumire` / `aml_cui` | — |
| `tara_risc_inalt` | checkbox | Țară cu risc înalt | ✅ | `aml_tara_risc_inalt` | — |
| `pe_lista_sanctiuni` | checkbox | Pe listă de sancțiuni | ✅ | `aml_pe_lista_sanctiuni` | — |
| `tranzactie_complexa` | checkbox | Tranzacție complexă | ✅ | `aml_tranzactie_complexa` | — |
| `canal_la_distanta` | checkbox | Relație la distanță | ✅ | `aml_canal_la_distanta` | — |
| 10 indicatori suspiciune (`.ind`: graba_excesiva … antecedente_penale) | checkbox × 10 | Indicatori HCD 58 art. 6(10) | ✅ | `.aml-ind` × 10 (toate prezente) | — |
| „Evaluează relația" (`evalueaza`) | button | Evaluare risc AML | ✅ | `aml-eval` | — |
| `rez` + butoane documente (norme_interne, evaluare_risc, fisa_kyc, decizie, rts) | render+button | Generare documente AML | ✅ | `aml-rez` + butoane data-url (același set) | — |
| confirm RTS/RTN (art. 33) | dialog | Avertisment legal RTS | ✅ | păstrat în `amlDescarca` | — |

---

## I. GDPR (aml.html → secțiune Documente GDPR)

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| „Politică de prelucrare" (`/api/gdpr/politica.docx`) | button | Generează politica | ✅ | `gdpr-politica` (tab GDPR) | — |
| „Acord consimțământ client" (`/api/gdpr/consimtamant.docx`) | button | Generează acordul | ✅ | `gdpr-consimtamant` | — |

---

## J. Audit

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `btn-audit` (Pas 5) → audit.txt | button | Urmă de audit | ✅ | `audit-gen` (tab Audit) + `gen-audit` (Generează) | — |
| (n/a vechi) afișare inline urmă audit | render | — | ➕ | **Nou are în plus** `audit-out` (afișare în pagină) | (bonus) |

---

## K. Anexe

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| `foto` + `doc` (la Pas 4) | input file | Anexa 2 / Anexa 3 | ✅ | subtab Anexe (`up-foto`/`up-doc`) + tab Anexe (redirect) | — |
| ștergere individuală fișier | button | Scoate o poză/doc | 🟡 | Lipsește în nou (vezi F) | mic |

---

## L. Navigare / utilitare / backup

| Control (vechi) | Tip | Scop | În UI nou? | Unde în nou / ce lipsește | Impact |
|---|---|---|---|---|---|
| Stepper 1–5 (butoane pas) | button × 5 | Navigare între pași | ✅ | tab-uri + sub-tab-uri (Proprietate/Comparabile/Calcul/Anexe/Generează) | — |
| `inapoi` „◀ Înapoi" | button | Pas anterior | ✅ | `nav-inapoi` | — |
| `inainte` „Înainte ▶" | button | Pas următor | ✅ | `nav-inainte` | — |
| `reset` „Reset dosar" | button | Golește dosarul | ✅ | `reset-dosar` (cu confirm) | — |
| „💾 Backup dosare" (`/api/backup.db`) | a.btn | Descarcă backup .db cu toate dosarele | ❌ | **Lipsește complet** în UI nou (modelul nou e folder pe disc, dar nu există buton de backup) | mare |
| „📄 Formular clasic" (`/formular`) | a.btn | Toate câmpurile pe o pagină | 🟡 | Nu există link în UI nou; pagina veche reachabilă doar prin `/wizard` indirect | mic |
| top-nav: Evaluare/Dosare/Grile/Descoperire/AML | a × 5 | Navigare globală | 🟡 | În nou: tab-uri în dosar + `_nav_cross` (Alege interfața / Homepage nou / Wizard vechi / Documente). Grile/Descoperire/AML separate nu sunt în nav-ul nou (AML e tab; Grile/Descoperire doar link punctual) | mic |
| „📄 Documente" (`_nav_cross`) | a.btn | Documente livrate | ✅ | prezent în nou (`/documente`, btn în btn-bar + nav) | — |

---

## M. Homepage nou + Cont (incepe.html, cont.html) — controale fără echivalent în vechi

> Acestea sunt **bonus** în UI nou (gestiune dosare/cont). Le listez pentru completitudine; nu reprezintă lipsuri.

| Control (nou) | Tip | Scop | Echivalent vechi |
|---|---|---|---|
| `nou` „➕ Dosar nou" + `form-nou` + `creeaza-nou` | button/form | Creează dosar cu identitate | (vechi: dosarul exista implicit, salvat în SQLite) |
| `importa` + `fisier-import` (.docx) → import-docx | button/file | Importă dosar dintr-un .docx | ❌ în vechi (bonus nou) |
| „Import asemănător" / „Demo" (disabled, comercial) | button | Placeholder comercial | ❌ |
| tabel „Dosare salvate" + „Deschide" | render/a | Listă dosare (noi/existente) | parțial: `/dosare` (UI vechi, neinclus aici) |
| „scoate din listă" (dispărute) | button | Curăță index dosare șterse | ❌ |
| `/cont`: `nume`, `legitimatie`, checkboxes `fmt`, `preview`, `salveaza` | input/checkbox/button | Identitate evaluator + format nume dosar | parțial: în vechi evaluatorul era pe wizard (localStorage), fără format dosar |

---

# ❌ LIPSESC COMPLET (ordonate după impact)

**Impact MARE:**
1. **Ingestie PDF (pornire rapidă)** — `doc-tip` + `doc-ingestie` + `aplicaIngestie`. Pre-completarea câmpurilor din extras CF / releveu / plan a dispărut. *(Pas 1 wizard)*
2. **Atribute secundare de potrivire** — `atribute_secundare` (wizard) + `secundare` (descoperire). În nou e hardcodat `atribute_secundare:[]`; nu poți cere AI-ului să verifice tâmplărie/garaj/panouri în anunțuri.
3. **Import comparabil din URL** — `url_import_w`+`btn-import-url` (wizard), `url_import`+`btn_import` (form). Lipirea unui link imobiliare.ro/storia.ro pentru extragere preț+suprafață nu există în nou.
4. **Coada „Anunțuri importate din extensie de browser"** — toată secțiunea din descoperire.html (`lista-importate`, `laGrilaImport`, `goleseImport`, `sterge-unul`). Integrarea cu extensia de browser e absentă.
5. **Descoperă terenuri în zonă** — `t-portal`/`t-judet`/`t-loc` + „Caută terenuri" (`descoperaTeren`) + „➕ grilă" (`t-add`) + `/api/descopera-teren`. Lipsește total.
6. **Punte VBP grilă chirii → metodă venit** — `trimiteVbpWizard` / preluare `vbp_din_grila`. În nou VBP se introduce manual, fără legătura automată din grila de chirii.
7. **Buton „💾 Backup dosare"** (`/api/backup.db`) — descărcarea unei copii a tuturor dosarelor nu există în UI nou.
8. **Câmp `proprietar`** (dacă diferă de client) — nu există în UI nou (nici în payload-ul meta).
9. **`adresa_raport`** (adresă cu diacritice pt raport) — editarea dedicată a adresei finale lipsește; nou compune automat din 3 câmpuri.
10. **Randarea alertelor de validare la calcul** — `res.alerte` (blochează/avertizează: outlier, <3 comparabile, ajustare prea mare) NU e afișată în `rezultat` (nou). Owner pierde semnalele prudențiale.

**Impact MIC:**
11. Tabel **metodologie scoring** (descoperire) — `randMetodologie`.
12. „Copiază comparabilele bifate" (`copiaza`) → `<pre>`.
13. Ștergere individuală foto/doc din previzualizare.
14. Buton manual „↻ Curs BNR" (nou ia automat).
15. Link „📄 Formular clasic" în nav.

# 🟡 PARȚIALE (ordonate după impact)

**Impact MARE:**
1. **Toate grilele de ajustare (teren/casă/chirii)** — `/grila` NU e integrată în dosar; doar link `target=_blank`. Cele 17+16+9 elemente de ajustare pe etape, plus „Indicele ANEVAR", rămân în pagina veche. UI nou are doar `comparabile_teren` (preț/mp;supr, fără ajustări). Aceasta e cea mai mare zonă „parțială".
2. **Tabelul de atribute per candidat** la descoperire (Criteriu / Referință subiect / Găsit în anunț / d / Pondere) — absent în render-ul inline din nou; vezi doar relevanță % + explicație.
3. **Lista candidaților** — în nou fără tabel detaliat și fără afișarea atributelor secundare per candidat.
4. **județ / localitate ca select din /api/localitati** — în nou sunt input-uri text libere (pierzi listele cu diacritice + slug automat pentru portaluri).
5. **Alerte validare** (vezi și ❌ #10) — parțial: structura există în payload dar nu se randează.

**Impact MIC:**
6. `attr_stare` / `attr_finisaj` ca select cu etichete → în nou input number fără etichete.
7. `evaluator_nume` / `evaluator_legitimatie` mutate în `/cont` (nu se editează din dosar).
8. „Trimite la grila casă" → în nou pune în textarea, nu în grila `/grila`.
9. Curs BNR — automat, fără buton manual.
10. Foto/doc fără ștergere individuală.

---

# TOTAL

- **Controale vechi inventariate (unice, funcționale):** ~118
  (wizard ~57, descoperire ~18, grila ~60+ inputuri de grilă numărate ca grupuri → ~25 grupuri/controale distincte, aml ~24, form parțial redundant ~3 unice).
- **✅ Acoperite complet în UI nou:** ~62
- **🟡 Parțiale (există dar diferit / doar via link la pagina veche):** ~30
- **❌ Lipsesc complet în UI nou:** ~26 (15 mare-impact funcțional + 11 mic) — vezi listele de mai sus; cele cu adevărat critice de business: ingestie PDF, atribute secundare, import URL, coadă extensie, descoperă teren, punte VBP, backup, alerte validare, proprietar, adresa_raport.

> Cea mai mare gaură nu e un singur buton, ci **migrarea grilelor de ajustare** (`/grila`) în workspace-ul nou: ~50 de inputuri de ajustare pe etape + Indicele ANEVAR + descoperă-teren rămân în afara dosarului. Apoi modulul de **descoperire** și-a pierdut: atributele secundare, importul din URL, coada din extensie, tabelul de atribute și metodologia. În final, lipsesc utilitarele transversale (**ingestie PDF**, **backup**) și semnalele de **validare la calcul**.
