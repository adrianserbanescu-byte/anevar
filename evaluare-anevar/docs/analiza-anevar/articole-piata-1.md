# Articole metodologie piață (set 1) — analiză pentru aplicație

> **Temă:** `articole-piata-1`. Patru articole metodologice de Adrian Nicolescu despre **analiza pieței,
> factorii de valoare și terenuri**, citite pentru INSIGHT-uri direct utilizabile în motorul de evaluare
> casă+teren / garantare credit al aplicației.
>
> **Surse (.txt convertite, `C:\Users\adyse\anevar\md files\converted\`):**
> 1. *Care este diferenta dintre fezabilitatea de piata si evaluare* — distincția evaluare vs. studiu de fezabilitate.
> 2. *Cresterea valorii proprietatii imobiliare* — forțele care mișcă valoarea (piață locală, cartier, teren, costuri).
> 3. *INFLUENTE IN LUPTA PENTRU SEGMENTUL DE PIATA* — competitivitatea proprietății (localizare, fizic, imagine).
> 4. *Piata terenurilor: investitii sau speculatii* — terenuri libere, CMBU, durata de absorbție, rezidual.
>
> **Referință de prioritate:** SEV 2025 (`standardele-de-evaluare-a-bunurilor-2025.md`) + analizele
> existente `docs/SEV-2025-*.md`. **Regula contradicțiilor:** SEV 2025 are prioritate; în rest, documentul
> mai nou câștigă. Articolele NU au dată — sunt teorie clasică de evaluare (IVS/Appraisal Institute);
> le tratez ca **material doctrinar consistent cu, dar subordonat** SEV 2025.
>
> ⚠️ Document de analiză metodologică (input de produs). Decizia de conformitate revine evaluatorului ANEVAR.

---

## 1. CE CONȚINE + CE-I UTIL pentru aplicație

### Articol 1 — Fezabilitate de piață vs. evaluare

**Conține:** distincția dintre cele două tipuri de cercetare imobiliară. **Evaluarea** răspunde la „ce
valoare va avea?" (estimare a valorii la o dată); **studiul de fezabilitate** răspunde la „dacă construiesc
aici, vor exista cumpărători?" (capacitatea pieței de a susține un proiect). Cele 3 abordări clasice (cost,
venit, comparație). Critică tare a metodei comparabilelor când e folosită prost: (a) comparabile la un singur
nivel de preț/confort; (b) proiecte vechi, depășite funcțional, comparate cu unele moderne; (c) selecție
necorespunzătoare → imagine falsă a pieței; (d) comparabile din **afara pieței efective** (alt segment
socio-economic) → eroare de exemplificare.

**Util pentru app:**
- Cele 4 capcane ale selecției de comparabile = **reguli de validare** concrete pentru grila de piață
  (vezi GAP G2). Aplicația deja selectează pe ajustare brută minimă (`engine/market.py:99`), dar **nu
  verifică omogenitatea segmentului** (comparabile dintr-o singură categorie de preț, sau din altă
  sub-piață) — exact capcanele (a) și (d).
- Validează că abordarea prin comparație măsoară valoare, NU vandabilitate/absorbție — relevant la **teren
  de dezvoltare** (vezi articol 4) unde durata de absorbție contează.

### Articol 2 — Creșterea valorii proprietății imobiliare

**Conține:** taxonomia forțelor care determină valoarea, structurată pe niveluri:
1. **Piața locală** — cerere/oferta, **cicluri** (4 faze), inegalități pe categorii de preț.
2. **Cartierul** — cele 3 principii economice: **majorare** (progresie — casa ieftină câștigă din vecini
   mai scumpi), **reducere** (regresie — casa scumpă pierde din vecini mai ieftini), **conformitate**
   (îmbunătățirile trebuie să respecte dimensiunea/vârsta/starea/stilul vecinătății pentru valoare maximă).
   Ciclul de cartier: dezvoltare → stabilitate → declin → revitalizare.
3. **Terenul** — crește de regulă în timp, dar afectat de autorizații, cost curățare/acces/utilități;
   respectă majorare/reducere/conformitate; valoare maximă la acces bun, deschidere la drum, suprafață
   similară loturilor din cartier.
4. **Costurile de construcție** — cresc costul de înlocuire (deci valoarea), dar îmbunătățirile se depreciază.
5. Reguli practice: clarificare juridică (drept de acces, limite cadastrale, utilități, autorizații,
   riscuri ecologice — rezervoare îngropate); îmbunătățiri care se amortizează (izolație, încălzire) vs.
   cele care recuperează doar 60–80%; **supra-îmbunătățirea** (peste media cartierului) nu mai adaugă valoare.

**Util pentru app:**
- **Principiile progresie/regresie/conformitate** = baza teoretică a ajustării de **localizare** și a
  **CMBU**. App-ul are câmp de localizare în grilă, dar nu cere/argumentează explicit poziția față de
  cartier (cea mai ieftină / cea mai scumpă / conformă). Util ca **prompt structurat** la CMBU și la
  justificarea ajustărilor.
- **Faza de ciclu a cartierului** (dezvoltare/stabilitate/declin/revitalizare) = câmp util în analiza de
  piață (GAP G8 din Livrabilul 3) și legat direct de GEV 520 A5 (a) „activitatea curentă și tendințele pieței".
- **Supra-îmbunătățirea / depreciere funcțională din neconformitate** — confirmă tratamentul existent al
  deprecierii funcționale (`engine/cost.py`, `validation.py:130`), dar oferă criteriul concret: „peste
  media cartierului = depreciere funcțională/economică recuperabilă parțial".
- Lista juridică (drept de acces, limite, utilități, autorizații, riscuri ecologice) = se mapează pe
  câmpurile meta (`sarcini`, `acces`, `utilitati`, `restrictii_urbanism`) și pe **riscuri fizice ESG**
  (rezervoare îngropate, alunecări — vezi GAP ESG G1 din Livrabil 3).

### Articol 3 — Influențe în lupta pentru segmentul de piață

**Conține:** ce face o proprietate (generatoare de venit) competitivă. Două „arme": **localizarea** și
**setul de caracteristici fizice**. Concepte:
- **Eficiență funcțională** — adecvarea spațiilor la utilizare; scăderea ei = **depreciere funcțională**
  (poate duce la abandon / reconversie).
- **Durabilitate fizică** — perioada în care clădirea rămâne productivă.
- **Localizare + vecinătate + factori de mediu** — statut socio-economic al vecinătății, facilități suport
  (școli, biserici, magazine, poliție), bariere psihologice, **schimbări de zonare** (rezidențial→comercial
  crește valoarea terenului dar scade competitivitatea ca închiriere rezidențială).
- **Cererea** — interacțiune cu raritatea și prețul substituenților apropiați.
- **Imaginea** — diferențe percepute > diferențe fizice; arhitectură/calitate/reputație → preț premium și
  vulnerabilitate scăzută în competiție.

**Util pentru app:**
- Pentru tipul **comercial/închiriat** (profil `COMERCIAL_INCHIRIAT`, abordare venit): factorii de
  competitivitate = exact ipotezele de venit (nivel chirie, neocupare) care trebuie argumentate (GEV 630 §71).
  Util ca **checklist de argumentare a chiriei și ratei de neocupare**.
- **Schimbarea de zonare ca dublă forță** (scade competitivitatea rezidențială / crește valoarea terenului)
  = exact tensiunea CMBU teren vs. construcție — util la analiza CMBU și la **terenuri cu potențial de
  reconversie**.
- **Substituenți + raritate** = fundamentul economic al principiului substituției din abordarea prin
  comparație; întărește regula „comparabile din aceeași sub-piață".

### Articol 4 — Piața terenurilor: investiții sau speculații

**Conține:** dinamica terenurilor libere. Prețurile de ofertă urmăresc adesea **interese speculative**,
necorelate cu tranzacții reale sau cu utilizarea optimă viitoare. Probleme la evaluarea terenului liber:
- CMBU reală poate diferi de planurile urbanistice (dacă vecinii sub aceeași utilizare au neocupare mare →
  utilizare alternativă).
- Comparabilele presupun utilizări specifice — pot să nu fie cu adevărat comparabile.
- **Durata de absorbție** (timpul de vânzare a dezvoltării după finalizare) = variabilă critică de valoare
  în abordarea dezvoltării; comparabilele trebuie să aibă potențial de utilizare **și** durată de absorbție
  similare.
- **Valoarea reziduală** a terenului = valoarea proprietății terminate minus costurile de dezvoltare;
  trebuie testată din prisma investitorului (analiză de risc, modificări de cost/durată).
- **Investitor-întreprinzător** (dezvoltă, depinde de cererea finală) vs. **speculator pe termen scurt**
  (revinde cu câștig, depinde de ciclul de piață). Speculatorii pot exploda prețurile peste costul economic
  rezonabil.

**Util pentru app:**
- Justifică **metoda reziduală și analiza parcelării (DCF)** pentru teren — neimplementate (GAP G9 din
  Livrabil 3, GEV 630 §97–102). Articolul oferă logica: rezidual = valoare finită − cost dezvoltare, testat
  cu risc.
- **Durata de absorbție** = câmp/concept absent din motor. Critic pentru teren de dezvoltare și pentru
  abordarea dezvoltării.
- **Distincția ofertă speculativă vs. tranzacție reală** = regulă de validare pentru comparabilele de teren:
  app-ul acceptă oferte (`tip_oferta="oferta"`) dar nu marchează riscul speculativ și nu impune ajustarea
  ofertă→tranzacție pe etapa de tranzacție când comparabilele sunt doar oferte.

---

## 2. RELEVANȚA vs SEV 2025 + CONTRADICȚII rezolvate

### Aliniere (articolele întăresc SEV 2025, nu îl contrazic)

| Concept articol | Corespondent SEV 2025 | Verdict |
|---|---|---|
| 3 abordări (cost/venit/comparație) | SEV 103 / GEV 630 §40–80 | Identic. Articolele = versiunea didactică. |
| Capcanele comparabilelor (segment, omogenitate) | GEV 630 §56–57 (elemente de comparație, comparabile din aceeași sub-piață) + SEV 230 §100.2 (ierarhia datelor) | Articolul **concretizează** cerința; aplicabil ca validare. |
| Progresie/regresie/conformitate (cartier) | GEV 630 §30–34 (analiza pieței) + §35–39 (CMBU) — principii de evaluare clasice | Aliniat; SEV nu le numește dar le presupune. |
| Eficiență funcțională / durabilitate fizică | GEV 630 §78 (depreciere fizică/funcțională/externă) | Identic conceptual. Articolul 3 = sursa teoretică a deprecierii funcționale. |
| CMBU teren liber, durata de absorbție, rezidual | GEV 630 §81–102 (evaluarea terenului: extracție, alocare, **reziduală** §97, **parcelare/DCF** §101) | **SEV 2025 cere explicit** aceste metode; articolul 4 le motivează. |
| Schimbarea de zonare (dublă forță) | GEV 630 §35–39 (CMBU: permis legal) + certificat urbanism (§16) | Aliniat. |
| Distincția evaluare vs. fezabilitate | SEV 102 (tipuri ale valorii) — fezabilitatea NU e tip de valoare | Aliniat; util ca disclaimer de scop. |

### Contradicții rezolvate (cine câștigă + de ce)

**C1 — „Comparabile selectate" pentru fezabilitate vs. pentru evaluare (articol 1).**
Articolul critică folosirea comparabilelor pentru fezabilitate (susținerea pieței), nu pentru valoare.
**Câștigă SEV 2025 (necontrazis):** GEV 630 folosește comparabilele strict pentru **valoare** (§51–57), iar
fezabilitatea/absorbția apare doar în metoda reziduală/parcelare (§97–102). **Implicație app:** grila de
comparație (`market.py`) rămâne corectă pentru valoare; absorbția se tratează separat (la teren de dezvoltare).

**C2 — „Valoarea de piață = prețul pe care l-ar dori vânzătorul / cumpărătorul" (articol 1).**
Definiția din articol e colocvială/aproximativă. **Câștigă SEV 2025:** SEV 102 §20 definește riguros valoarea
de piață (suma estimată, vânzător/cumpărător hotărâți, în condiții de echilibru, după marketing adecvat,
fără constrângere). **Implicație app:** definiția canonică e deja în cod (`models/meta.py:28` →
`tip_valoare="Valoarea de piață (SEV 102)"`, sursa în `generator.py:108–128`). Articolul NU se folosește
ca sursă de definiție.

**C3 — „Valoarea terenului crește de regulă în timp" (articol 2).**
Afirmație generală, contrazisă chiar de articolul 4 (speculații, cicluri). **Câștigă abordarea SEV 2025 +
articol 4 (mai nuanțat):** valoarea terenului depinde de CMBU, absorbție, ciclu — nu crește monoton.
**Implicație app:** niciun automatism de „apreciere a terenului în timp"; valoarea rămâne strict din
comparabile/rezidual la data evaluării.

**C4 — Articolele tratează frecvent perspectiva de venit/închiriere (articol 3, „chirie").**
Pentru fluxul nostru principal (casă+teren rezidențial / garantare), abordarea principală e **piața**
(GEV 520 §31 + Livrabil 2). **Câștigă SEV 2025:** factorii de competitivitate din articolul 3 se aplică la
profil **comercial/închiriat**, NU se importă forțat în evaluarea rezidențială prin comparație.

> **Concluzie §2:** Niciun articol nu contrazice SEV 2025 pe fond. Sunt material **doctrinar consistent**
> care concretizează cerințe deja existente în GEV 630 (analiza pieței, CMBU, depreciere, evaluarea
> terenului). Valoarea lor = **operaționalizarea** acestor cerințe în câmpuri/validări/prompturi.

---

## 3. GAP-URI de implementare (ce ar trebui app-ul să facă/adauge)

> Stare verificată în cod: ✅ există · 🟡 parțial · 🔴 lipsă. Severitate: **blocant** / **important** / **minor**.
> Mai jos = gap-uri DERIVATE din aceste articole. Cele care dublează Livrabilul 3 sunt marcate [≈ G_n].

### GAP-A — Analiza de piață structurată (faza de ciclu, segment, tendințe) **[important]** 🔴
**Insight (art. 2, 3):** piața/cartierul au cicluri (dezvoltare/stabilitate/declin/revitalizare) și
inegalități pe segmente de preț. **Stare cod:** capitolul „PREZENTAREA DATELOR DE PIATA"
(`generator.py:735–740`) e narativ AI liber sau placeholder „Analiza pietei locale [de completat]"; nicio
metadată structurată. **Recomandare:** câmpuri minime în analiza de piață — `faza_ciclu_cartier`
(enum: dezvoltare/stabilitate/declin/revitalizare), `tendinta_preturi` (creștere/stabil/scădere),
`segment_pret_subiect` (poziția în cartier: cel mai ieftin / mediu / cel mai scump). Hrănesc direct
narativul de piață ȘI riscul GEV 520 A5(a). [≈ G8]

### GAP-B — Validarea omogenității comparabilelor (segment + sub-piață) **[important]** 🟡
**Insight (art. 1, capcanele a–d):** comparabile dintr-un singur nivel de preț, sau din altă sub-piață
socio-economică, dau imagine falsă. **Stare cod:** `validation.py` verifică număr min, outlier pe mediană,
limita de ajustare brută — **dar NU** verifică dispersia de preț unitar (segment unic) sau apartenența la
aceeași sub-piață/localitate a comparabilelor. **Recomandare:** (1) alertă dacă toate comparabilele au preț
unitar brut într-o bandă foarte îngustă vs. subiect (segment nereprezentativ); (2) alertă dacă ajustarea de
localizare lipsește când comparabilele sunt din localități diferite. Întărește `valideaza_comparabile`.

### GAP-C — Ajustarea ofertă→tranzacție obligatorie când comparabilele sunt doar oferte **[important]** 🟡
**Insight (art. 4):** prețurile de ofertă pentru terenuri urmăresc interese speculative, necorelate cu
tranzacții. **Stare cod:** `Comparable.tip_oferta` / `LandComparable` acceptă oferte, etapa de tranzacție
există (`market.py:_pret_baza_tranzactie`), dar nimic nu **impune** o ajustare ofertă→tranzacție când
`tip_oferta="oferta"`. **Recomandare:** alertă „comparabil pe ofertă fără ajustare ofertă→tranzacție în
etapa de tranzacție" — mai ales la teren (risc speculativ). Concretizează GEV 630 §57 (oferte admise dacă
analizate critic).

### GAP-D — Metoda reziduală + durata de absorbție pentru teren **[important pentru teren de dezvoltare; minor pentru flux rezidențial]** 🔴
**Insight (art. 4):** teren liber cu potențial de dezvoltare → valoare reziduală (proprietate finită −
cost dezvoltare), testată cu risc; **durata de absorbție** = variabilă critică. **Stare cod:**
`engine/land.py` implementează DOAR comparația vânzărilor; reziduala/parcelarea lipsesc; niciun câmp de
absorbție. **Recomandare:** (la prioritate medie) metoda reziduală + câmp `durata_absorbtie` pentru teren
intravilan de dezvoltare. [≈ G9] Pentru fluxul casă+teren rezidențial obișnuit rămâne minor (comparația e
„cea mai adecvată" — GEV 630 §83).

### GAP-E — CMBU cu argumentare structurată pe cele 4 teste + principii de cartier **[important]** 🟡
**Insight (art. 2, 4):** CMBU = permis legal + posibil fizic + fezabil financiar + maxim productiv;
principiile progresie/regresie/conformitate; pentru teren, CMBU poate diferi de zonare. **Stare cod:** CMBU
e text narativ AI liber (`generator.py:785–790`, ghid în `narrative.py:42`) — menționează cele 4 teste în
prompt, dar **nu există câmpuri** care să forțeze evaluatorul să bifeze fiecare test sau să noteze poziția
față de cartier. **Recomandare:** mini-formular CMBU (4 checkbox-uri + notă „utilizare alternativă dacă
zonarea diferă de CMBU reală"), care să devină input determinist pentru narativ (nu doar prompt AI).

### GAP-F — Riscuri fizice/juridice ca listă de verificare (drept acces, limite, utilități, ecologic) **[important]** 🟡
**Insight (art. 2, lista juridică):** drept de acces neînregistrat, limite cadastrale neclare, utilități
fără drept legal, construcții neautorizate, **riscuri ecologice** (rezervoare îngropate) = semnale care
reduc valoarea. **Stare cod:** există `sarcini`, `acces`, `utilitati`, `restrictii_urbanism` în
`models/property.py` / `meta.py`, dar **nu** un câmp de **riscuri ecologice/fizice** — care e exact golul
ESG (riscuri fizice) din Livrabil 3 G1. **Recomandare:** câmp `riscuri_fizice` (inundabil, alunecări,
rezervoare îngropate, contaminare) care alimentează atât descrierea, cât și secțiunea ESG. [≈ G1, întărește]

### GAP-G — Disclaimer „evaluare ≠ studiu de fezabilitate" pe scop **[minor]** 🔴
**Insight (art. 1):** confuzia frecventă evaluare↔fezabilitate. **Stare cod:** raportul declară scopul, dar
nu clarifică explicit că NU este un studiu de fezabilitate / absorbție de piață. **Recomandare:** o frază
în ipotezele/limitările raportului: „prezentul raport estimează valoarea la data evaluării și nu constituie
un studiu de fezabilitate sau de absorbție a pieței". Ieftin, reduce expunerea de interpretare.

### GAP-H — Tratarea „supra-îmbunătățirii" în depreciere funcțională **[minor]** 🟡
**Insight (art. 2):** îmbunătățiri peste media cartierului nu adaugă valoare (depreciere funcțională
supra-adecvare). **Stare cod:** deprecierea funcțională există ca input numeric cu justificare obligatorie
(`validation.py:130`), dar fără ghidare conceptuală. **Recomandare:** hint în UI/ghid: „supra-adecvarea
(finisaje/dotări peste standardul cartierului) se reflectă în deprecierea funcțională". Doar documentar.

---

**Documente conexe:** `docs/SEV-2025-ce-putem-folosi.md`, `docs/SEV-2025-cerinte-per-tip-imobil.md`,
`docs/SEV-2025-gap-implementare.md` (Livrabil 3 — gap-urile G1/G8/G9 referite mai sus).
