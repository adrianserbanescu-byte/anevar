# Brief de council — Pagina „Descoperă": ranking comparabile imobiliare (RO)

> Notă pentru panel: ipotezele noastre interne sunt formulate ca **întrebări deschise**, nu ca decizii luate. Vrem ideile voastre independente — nu confirmarea unei rețete. Acolo unde menționăm o direcție pe care o luăm în considerare, e doar pentru context, nu pentru a vă ancora. Neutralitatea e intenționată în formularea **fiecărei** întrebări, nu doar în această notă: dacă o întrebare pare să presupună un răspuns, contestați premisa.

---

## 0. Convenții și jargon (pentru un cititor din afara proiectului)

- **Subiect** = proprietatea evaluată (cea pentru care căutăm comparabile). **Candidat / anunț** = un anunț comparat cu subiectul.
- **Numerotarea categoriilor** (vezi §2): **1** = casă+teren, **2** = apartament, **3** = spațiu industrial, **4** = teren agricol, **5** = proprietate specială. Folosim notația `#1…#5` pe tot parcursul.
- Nume interne de cod (apar doar ca **dovadă** că am verificat pe sursă, irelevante pentru panel): `scoring.py`, `extractor.py`, `orchestrator.py`, `fetch_html`, `_SEGMENT`.
- `__NEXT_DATA__` = blocul JSON cu date structurate pe care site-urile Next.js (ex. storia.ro) îl embed-ează în pagina HTML; din el extragem câmpuri „curate", fără a ghici din text.
- `slug` = forma normalizată a numelui localității din URL (ex. „Breaza").

---

## 1. Context: ce face „Descoperă" acum

**Scop.** Aplicația evaluează proprietăți (casă + teren, garantare credit). Pagina „Descoperă" găsește anunțuri **comparabile** cu proprietatea evaluată (subiectul), pe o categorie, într-o arie geografică, și le **rankează după relevanță** (0–100%).

**Pipeline-ul (verificat pe cod, 2026-06-07):**
`căutare pe portal → scrape HTML (`fetch_html`, HTTP direct) → parsare anunț (HTML / `__NEXT_DATA__`) → extracție atribute (LLM, Claude) → scor determinist → rank`.

**Pașii utilizatorului:**
1. Caută (categorie + locație) → „Descoperă" selectează anunțurile potrivite în acea arie, pe categorie.
2. Fiecare anunț primește un **ranking de relevanță 0–100%** calculat dintr-un set de **criterii principale**.
3. Userul poate adăuga **criterii SECUNDARE** proprii (linii libere „nume: valoare_dorită") → acestea **NU intră în calculul rankingului**; doar se verifică în text și se afișează (potrivit / diferit / nementionat + citat din anunț).
4. Se afișează rankingul + linkul; userul salvează ce consideră.

**Rolul AI/LLM (extractor).** LLM-ul lucrează **exclusiv pe textul anunțului** (nu pe imagini). Extrage atributele primare: an construcție, stare (treaptă 1–5), finisaj (treaptă 1–4), tip încălzire, teren (mp), plus **dovezi (citate)** din text. Evaluează și criteriile secundare ale userului. Fără client LLM disponibil sau la eșec → **fallback determinist**.

**Sursa fiecărui atribut de ranking (relevant pentru Q5).**
- **Din date structurate / parsare** (nu depind de LLM): suprafață construită, an, teren (mp), încălzire (la storia, din enum). Suprafața construită folosită la potrivire e luată **din parser, nu din LLM** (confirmat în `orchestrator.py`: `extraction.profile.suprafata_construita = parsed.suprafata`).
- **Dependente de LLM pe text**: stare (scala 1–5), finisaj (scala 1–4). *Finisaj* nu există în datele structurate; *stare* structurală are doar 3 valori text (vezi §3), pe care doar LLM-ul le mapează pe scala 1–5.

**Scale ordinale (ce înseamnă treptele).**
- **Stare 1–5**: 1 = cea mai proastă (de renovat / la roșu), 5 = cea mai bună (nou / impecabil). Maparea celor 3 valori storia: `to_renovation` → treaptă joasă, `to_completion` → treaptă mijlocie, `ready_to_use` → treaptă înaltă; conversia 3→5 trepte o face LLM-ul, **nu** e o regulă deterministă în date.
- **Finisaj 1–4**: 1 = finisaj minimal/brut, 4 = finisaj premium.

**Ranking — criterii principale, ponderi și formulă (confirmate în cod, `scoring.py`):**

> Legendă formule: `s` = valoarea atributului la **subiect**; `c` = valoarea aceluiași atribut la **candidat** (anunțul comparat). `d ∈ [0,1]` = distanța (disimilaritatea): 0 = identic, 1 = maxim diferit.

| Atribut | Pondere | Distanță d ∈ [0,1] față de subiect | Sursă |
|---|---|---|---|
| Suprafață construită | ×5 | diferență relativă: `min(\|s−c\| / s, 1)` | parser |
| An construcție | ×5 | `min(\|s−c\| / 25, 1)` (plafonat la 25 ani) | parser |
| Stare (1–5) | ×4 | `min(\|s−c\| / 4, 1)` (trepte) | LLM |
| Finisaj (1–4) | ×3 | `min(\|s−c\| / 3, 1)` (trepte) | LLM |
| Încălzire | ×2 | 0 identic / 0.5 aceeași familie / 1 diferit | parser (storia) |
| Teren (mp) | ×1 | diferență relativă: `min(\|s−c\| / s, 1)` | parser |

- **Plafonarea `min(…, 1)`** se aplică la toate; la stare/finisaj plafonul nu se atinge în practică (diferența maximă reală e 4, respectiv 3), dar e în cod — îl notăm pentru fidelitate.
- **„Aceeași familie" la încălzire** = grup de tipuri considerate echivalente, comparate pe prefixul tipului (ex. variante de centrală pe gaz între ele vs. o sursă complet diferită precum sobă). Definiția exactă a familiilor e un detaliu de implementare deschis criticii la Q1.
- **Formula de relevanță:** `Relevanță = 100 × (1 − Σ(pondere × d) / Σ ponderi cunoscute)`.
- Atributele **nementionate se exclud din numitor** (nu penalizează). La **≥3 atribute lipsă** → marcaj „încredere scăzută".
- Explicația e **auto-conținută** (formula cu numere reale per anunț).
- **Reguli speciale:**
  - La categoria *teren*, relevanța = doar similaritatea de suprafață.
  - **Penalizare lipsă suprafață:** la **orice anunț fără suprafață structurată** (`if not parsed.suprafata`, `orchestrator.py`) → se scad **−30 din relevanța finală (0–100)** + se adaugă marcajul „completează manual". Frecvent atinge anunțuri OLX (text liber), **dar regula e declanșată de lipsa suprafeței, NU de portalul OLX** — și alte surse cu text liber cad sub ea. Se aplică anunțurilor intrate prin extensie / import URL (vezi §3: OLX nu e în căutarea automată).

**Criterii secundare (cum le-am gândit azi).** User scrie linii libere „nume: valoare_dorită"; LLM verifică în text → potrivit/diferit/nementionat + citat; se afișează, dar **NU distorsionează** scorul determinist auditabil.

**Golul fundamental.** Modelul de ranking există **complet doar pentru #1 (casă + teren)**; #4 (teren agricol) doar parțial (calea „teren" = doar suprafață); **#2/#3/#5 sunt NEMODELATE** — folosesc implicit modelul casei, netunat.

---

## 2. Cele 5 categorii (din UI-ul real)

1. **Casă individuală + teren** — clară, singura modelată complet.
2. **Apartament** — clară.
3. **Spațiu industrial** (hală / depozit) — clară.
4. **Teren agricol** — clară (calea „teren" = doar suprafață).
5. **Proprietate specială** (hotel, benzinărie…) — **CATCH-ALL** („restul"), eterogenă.

> Confirmat în cod: căutarea automată construiește URL doar pentru `casa` și `teren` (segmente `_SEGMENT`). Deci e și o problemă de **ACOPERIRE a căutării**, nu doar de scoring — deși, de ex., storia ARE `/vanzare/apartament`, noi nu generăm acel URL.

---

## 3. Constatări din investigație (verificate pe cod + anunțuri reale)

> Notă: tot ce urmează e verificat pe cod sau pe anunțuri reale, **cu o excepție marcată explicit**: geocoding-ul/distanțele NU sunt implementate azi — afirmația de fezabilitate e o evaluare, nu o constatare pe cod existent.

- **Căutare automată = doar 2 portaluri:** `imobiliare.ro` + `storia.ro`. **OLX.ro NU e în căutarea automată** (apare doar prin coada extensiei de browser / import URL direct); OLX dă preț, rar suprafață.
- **Granularitate căutare:** județ + localitate (în URL). Categorii doar `casa` și `teren`. **NU există** segmente pentru apartament/industrial/agricol/special; **niciun input** de stradă/cartier/număr.
- **Ce expune fiecare portal** (testat pe Breaza/Prahova):
  - **storia.ro:** date **STRUCTURATE** din `__NEXT_DATA__` — cele mai bogate: preț, monedă, supr. casă, supr. teren, an, încălzire, material, tip clădire, stare, nr. camere, etaje.
  - **imobiliare.ro:** parsare din text — mai sărac (preț, supr., an, material, etaje; fără încălzire/tip/stare/camere în eșantion).
  - **olx.ro:** doar prin extensie; preț, rar suprafață.
- **Dicționarul nostru** = maparea enum-urilor storia (`gas/urban/detached/ready_to_use/wood/brick`…) → normalizat RO. **Tunat pe schema storia.**
- **Extragem mai mult decât scorăm:** material, tip clădire, nr. camere, etaje se extrag, dar **NU intră în ranking** (oportunitate ridicată la Q1, mai ales nr. camere/etaj la apartament #2).
- **Goluri de date:** *finisaj* NU există în datele structurate (vine doar din LLM); *stare* structural = text cu 3 valori (`ready_to_use/to_completion/to_renovation`), dar scoringul vrea 1–5 → potrivire doar prin LLM. Consecință: două criterii cu pondere mare (stare ×4, finisaj ×3) depind **100% de LLM-ul pe text** — un risc de fiabilitate de discutat (vezi Q1).
- **Precizie locație:** căutarea „teren/Breaza" a întors un anunț din Gura Beliei (localitate vecină, scăpată de filtrul pe slug) → **granularitate insuficientă**.
- **Dimensiunea API (important).** Pipeline-ul = scraping HTTP direct (`fetch_html`) + parsare HTML/`__NEXT_DATA__` + LLM (Claude) pe textul scrapuit. **Perplexity NU e în pipeline.** **Verificat INDEPENDENT de două ori (2026-06-07), eșantion mic dar concordant:** (A) **extracție** — cerem Perplexity să extragă câmpuri dintr-un URL storia dat → a întors **`{}` (gol)**, nu accesează pagina; (B) **discovery** — cerem „găsește 4 anunțuri reale cu URL" → din 4 URL-uri returnate, **3 au dat 404** (anunțuri inexistente, fabricate) și **1 a fost real (200)**, deși prețurile/JSON-ul păreau plauzibile. Adică datele „structurate" întoarse de Perplexity erau parțial **inventate**, nu regăsite. Concluzie de lucru (de contestat, nu prescriptivă): **bogăția reală vine din HTML brut + JSON storia**, ancorat în anunțul real; un API de *search/discovery* riscă să halucineze, iar un LLM e sigur mai degrabă la **extracția din text pe care i-l dăm noi**, nu la obținerea/regăsirea datelor structurate.
- **Alte site-uri RO:** **VDI.ro și Imoradar24.ro acoperă COMERCIAL + INDUSTRIAL** — exact golul nostru pe #3 (industrial) și #5 (special/comercial), pe care imobiliare/storia nu le acoperă bine. Plus HomeZZ.ro, CompariImobiliare.ro (agregator), Publi24.ro, anuntul.ro. **Fiecare cere parser propriu** → modelarea #3/#5 depinde și de adăugarea acestor surse.
- **Geocoding / distanțe RO (NU e implementat azi — nu apare în cod).** Pe baza datelor publice disponibile (extracte OSM România / dataset comunitar OSM-RO / SIRUTA), pare **fezabil tehnic** să obținem coordonate offline (localitate, eventual stradă), gratuit. Subliniem: aceasta e o **evaluare de fezabilitate**, nu o constatare verificată pe cod existent. Rămâne deschis **dacă și cum** ar trebui folosit.

---

## 4. Ce vrem să îmbunătățim (teme de discutat)

1. **Criterii principale per tip de proprietate.** Azi avem doar casa; ne întrebăm ce set + ponderi s-ar potrivi pentru toate 5, inclusiv #5 (catch-all eterogenă).
2. **Inputuri de locație granulare și conștiente de categorie:** pe lângă județ + localitate, eventual sat/comună/oraș/stradă și **CARTIER (zonă)**. Ne întrebăm **dacă/când** cartierul devine un criteriu relevant — în special la apartamente — și cum l-am colecta. (Nu îl tratăm ca cerință stabilită.)
3. **Criteriile secundare în UI:** cum le **prezentăm și colectăm** per tip (ce sugerăm userului să adauge la apartament vs. industrial vs. special); rămân în afara scorului sau unele devin principale?
4. **Granularitatea locației după tipul localității** *(întrebare deschisă, fără concluzie pre-decisă)*: la ce nivel devine relevantă locația și **variază** acest prag cu mărimea localității (sat mic vs. oraș mare)? Context, nu răspuns: într-un sat strada apare rar în anunțuri; într-un oraș mare aceeași stradă se poate întinde pe km (Str. Timișoara nr. 113 vs nr. 1). Lăsăm panelul să spună **dacă** strada contează la fiecare nivel.
5. **Distanța ca factor — deschis dacă o folosim.** Azi locația e doar filtru de căutare, **NU intră în scor**. Întrebarea deschisă: ar trebui distanța să influențeze rankingul deloc, și dacă da, prin ce mecanism?

> Punctele 2/4/5 sunt **PER tipul de proprietate**.

---

## 5. Întrebările pentru council (Q1–Q8)

**Q1 — Criterii principale per categorie.** Pentru fiecare dintre cele 5 categorii (atenție la #5 catch-all): ce criterii principale ați pune în ranking, cu ce ponderi și ce formule de similaritate? Pentru #5 — set minimal comun + criterii pe sub-tip, sau altă strategie?
Sub-întrebări:
- *(Acoperire)* Azi construim URL de căutare doar pentru casă/teren — deci e și o problemă de **ACOPERIRE a căutării**, nu doar de scoring. Pentru #3 industrial și #5 comercial/special, sursele care lipsesc azi ar putea fi **VDI.ro / Imoradar24.ro** (imobiliare/storia nu acoperă bine comercialul) — deci modelarea acestor categorii depinde și de **adăugarea de parsere noi**. Cum prioritizați acoperirea vs. scoringul?
- *(Atribute deja extrase)* Avem deja extrase, dar **nescorate**: material, tip clădire, nr. camere, etaje. Care dintre ele ar trebui promovate în ranking și la ce categorii (ex. nr. camere / etaj la apartament)?
- *(Risc LLM)* Stare (×4) și finisaj (×3) au pondere mare dar provin **doar din LLM pe text** (nu din date structurate). Cum tratăm riscul de fiabilitate: reducem ponderea când vin doar din LLM, marcăm în UI, cerem confirmare, sau altă strategie?

**Q2 — Criterii secundare în UI per tip.** Cum le tratăm pentru fiecare tip de proprietate — rămân în afara scorului (cum sunt azi) sau unele devin principale, și cum decidem care promovează? Și cum le **colectăm / prezentăm diferit per tip** în UI (ce sugerăm userului să adauge la apartament vs. industrial vs. special)?

**Q3 — Granularitate locație per tip.** La ce nivel de granularitate (localitate vs. stradă + număr vs. cartier) devine relevantă locația, pentru fiecare tip de proprietate? Variază pragul cu mărimea localității (sat vs. oraș mare) — și **dacă** da, cum am decide pragul **automat** (când urcăm de la „localitate" la „stradă/cartier")? Lăsăm deschis dacă la sat strada contează deloc.

**Q4 — Distanța în ranking.** **Ar trebui distanța să influențeze rankingul?** Dacă da, prin ce mecanism — și aici listăm opțiuni fără a prefera una: (a) caracteristică ponderată în formula existentă; (b) filtru gradual la căutare; (c) tie-breaker la egalitate de scor; (d) penalizare separată **afișată** dar în afara scorului; (e) **a NU o include în scor deloc**. Cu ce greutate față de atributele fizice, per tip? Cum am calcula distanța subiect ↔ anunț?
Notă pe căutare vs. extracție: stradă/număr **APAR în textul anunțului** (le putem extrage după ce avem pagina), dar portalurile **NU permit căutare/filtrare** după ele (nu putem cere „doar str. X"). Cum exploatăm un atribut pe care îl putem **citi post-hoc**, dar nu **interoga**?

**Q5 (NOU) — Ce API e potrivit (dacă vreunul) pentru cele 3 site-uri.** Pentru imobiliare/storia/olx, știind că azi facem **scraping HTTP direct + extracție LLM pe text**: premisa noastră de lucru (verificată independent de **două** ori, eșantion mic — de contestat sau confirmat) e că **bogăția datelor vine din HTML brut + `__NEXT_DATA__` storia, pe care un API de *search* NU ți le dă**, iar testele au arătat că un API de tip Perplexity ori întoarce gol, ori **fabrică** anunțuri (3/4 URL-uri inexistente) în loc să le regăsească. Întrebarea: ce tip de API ar aduce valoare reală și **unde anume** în pipeline — la *search/discovery*, la *fetch*, sau **doar la extracția din text**? Sau scraping-ul direct rămâne abordarea corectă? Vă rugăm tratați premisa „search-API nu poate da datele structurate" ca ipoteza-cheie de validat sau respins.

**Q6 (NOU) — OLX și încrederea per sursă în UI.** Două întrebări separate, fără a presupune un răspuns:
- (a) **Merită păstrat OLX în pipeline**, dat fiind că dă date sărace (preț, rar suprafață)? Argumente pro/contra.
- (b) **Indiferent de (a)**, are sens să afișăm un **scor / grad de încredere PER SURSĂ** (imobiliare/storia/olx) — **NU în formula de ranking**, ci doar **AFIȘAT în UI** (ex. „încredere sursă")? Dacă da, cum îl definim și cum îl comunicăm userului fără a-l deruta?

**Q7 (NOU) — Robustețea extracției cu mai multe surse.** Pornind de la **problemă**, nu de la o soluție: **cum am putea crește robustețea / acoperirea extracției folosind, eventual, mai multe surse sau extractoare?** Ce arhitecturi sunt posibile — inclusiv opțiunea de **a NU adăuga nimic** și a rămâne la abordarea actuală (un scraper + un LLM) — și cu ce trade-off-uri (consistență, latență, cost, drift între surse)?
*Una* dintre opțiunile de evaluat (nu propunerea centrală): un „consiliu de API-uri" care caută în paralel pe mai multe surse/extractoare, apoi un „API-lider" consolidează / atribuie un scor de încredere. *Ipoteză nevalidată de marcat ca atare:* presupunem că interogarea ar fi ieftină — vă rugăm verificați și acest assumption. Merită această arhitectură față de status quo? *(Delimitare: Q6 = grad de încredere PER SURSĂ afișat în UI; Q7 = arhitectură de orchestrare multi-API. Sunt întrebări distincte — Q7 poate folosi conceptul din Q6, dar nu e același lucru.)*

**Q8 — Riscuri, dependențe, prioritizare.** Care sunt riscurile, dependențele și **ordinea de prioritate** recomandată pentru tot ce e mai sus: modelare per categorie, acoperire căutare (inclusiv surse noi pentru #3/#5), locație granulară, eventuala distanță în scor, dependența de LLM pentru stare/finisaj, încredere per sursă, și eventualul consiliu de API-uri?

---

*Reamintire de neutralitate: toate cele de mai sus sunt întrebări deschise. Nu propunem soluții decise — cerem panelului direcții independente, cu argumente și trade-off-uri. Unde am inclus o premisă de lucru (ex. la Q5/Q7), e marcată explicit ca ipoteză de validat sau respins, nu ca fapt stabilit.*