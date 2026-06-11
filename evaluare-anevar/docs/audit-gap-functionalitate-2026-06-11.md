# Audit gap funcționalitate — evaluare casă+teren pentru garantare credit

> **Dimensiune:** gap-functionalitate (ce FUNCȚIONALITATE NECESARĂ LIPSEȘTE pentru un raport complet și conform, utilizabil de bancă)
> **Data:** 2026-06-11 · **Mod:** READ-ONLY · **Standard:** SEV 2025, GEV 520 (garantare credit), GEV 630 (construcții)
> **Scop de bază analizat:** casă + teren, garantarea creditului ipotecar, persona = evaluator autorizat ANEVAR.
> **Surse:** cod `src/evaluare/{engine,report,assembler,profil,models,web}` + `docs/conformitate/{D,00-SINTEZA}` + auditele existente.

## Rezumat executiv

Aplicația este **solidă pe motorul de calcul** (3 abordări, reconciliere, grile teren/casă/chirii, garduri prudențiale,
urmă de audit hash) și pe **scheletul de raport** (.docx GBF + 7 capitole SEV 106 + declarații GEV 520). Niciun audit nu a
găsit erori de aritmetică. Golurile rămase sunt **funcționale**, nu de calcul, și se grupează în 5 clase:

1. **Pași de metodologie cu valoare auto-generată riscantă** (valoarea de lichidare = factor fix 0.85; cost ca abordare primară fără gardă) → steaguri roșii la verificarea bancară.
2. **Elemente de dosar formal lipsă** (recipisă BIG, coordonate Stereo 70, listă documente necesare/lipsă, certificat energetic) — exact rubricile pe care le bifează un verificator de bancă.
3. **Câmpuri de model existente DAR neexpuse în UI** (`clasa_energetica`, `structura`, `finisaje`, `justificare_depreciere`, `tip_valoare`, `utilizator_desemnat`) — backend capabil, formularul nu le colectează.
4. **Validări profesionale lipsă la momentul potrivit** (CMBU e doar proză AID, nu o verificare; lipsă gardă pe ajustarea netă și justificarea ajustărilor; lipsă gardă „cost primar la imobil").
5. **Modul de verificare SEV 400 absent integral** — invocat explicit de GEV 520 §18; multe bănci cer verificare independentă.

Cele mai multe sunt rezolvabile **în cod, fără atingerea metodologiei** (plumbing + câmpuri + secțiuni). Excepția care
cere efort mare/extern este SEV 400.

---

## BLOCANTE pentru un raport acceptat la bancă (P0–P1)

### G1. Valoarea de lichidare = factor fix 0.85 auto-generat, nealiniat la A60-2025
`report/generator.py:570-581` produce automat „valoarea de lichidare (vânzare forțată)" = valoare_piață × **0.85**, marcat
„orientativ". Definiția A60 s-a **modificat în 2025**: două premise (vânzare **ordonată** + **forțată**), iar evaluatorul
**trebuie să declare premisa**. A120.1 spune că prețul „nu poate fi estimat realist" fără cunoașterea constrângerii. O bancă
strictă respinge o valoare de lichidare nefundamentată. **Lipsă:** mecanism de declarare a premisei + gating pe ipoteză
specială scrisă a creditorului + eliminarea factorului auto. Severitate **high**.

### G2. Cost ca abordare PRINCIPALĂ la imobil, fără gardă GEV 520 §31/§34
`assembler.py:229-238` + `profil.py:29` (`CASA_TEREN_GARANTARE` are `["cost","comparatie"]` cu **cost primul**) permit
`metoda="cost"` primară la casă fără niciun avertisment. GEV 520 §34 cere ca la imobile costul **să NU fie abordarea
principală** (lichiditate) și să se aplice doar cu **accept scris al creditorului**. Un raport pe casă condus de cost e
steag roșu la bancă. **Lipsă:** alertă prudențială condiționată de profil GEV_520. Severitate **high**.

### G3. Recipisa BIG lipsește ca element formal (doar text narativ)
`report/generator.py:563-567` afirmă narativ că raportul „se înregistrează în BIG". GEV 520 §83-84 cer ca raportul final să
**conțină recipisa** de înregistrare. Nu există câmp `recipisa_big` în `models/meta.py` și nici avertisment la finalizare că
lipsa recipisei = raport incomplet. **Lipsă:** câmp + reamintire. Severitate **high** (raportul pleacă „incomplet" formal).

### G4. Lista documentelor necesare / lipsă + ipoteze în lipsa lor — absentă
GEV 520 §24/§46 cer o listă structurată a documentelor (extras CF actualizat, certificat de urbanism, certificat energetic,
documentație cadastrală, autorizație de construire / proces-verbal de recepție) + enumerarea celor **lipsă** + **ipotezele**
adoptate în lipsa lor. Anexa 3 (`generator.py:658-672`) doar atașează scanuri, fără listă de verificare a completitudinii.
**Lipsă:** secțiune dedicată „documente necesare / primite / lipsă + ipoteze". Severitate **high**.

### G5. Certificat de performanță energetică (CPE) neexpus în UI și netratat ESG
Modelul `BuildingData` are deja `clasa_energetica` (`models/property.py:49`), iar ingestia recunoaște tip document „cpe"
(`dosar.html:100`), DAR **nu există input** în tabul Proprietate pentru clasa energetică și nu apare în raport. GEV 520
§86-88 (ESG) cere tratarea performanței energetice + a riscurilor fizice, cu limitarea de competență. **Lipsă:** câmp UI +
randare în descriere + paragraf ESG §87. Severitate **medium-high**.

### G6. Coordonate Stereo 70 / ortofotoplan / Geoportal ANCPI — absente
GEV 520 §52 cere identificarea terenului prin adresă **+ coordonate Stereo 70 / referință ortofotoplan / Geoportal ANCPI**.
`models/meta.py` are doar `adresa`, `numar_cadastral`, `carte_funciara`. **Lipsă:** câmp coordonate / mențiune extras plan
cadastral în identificare. Severitate **medium**.

---

## METODOLOGIE / VALIDĂRI PROFESIONALE LIPSĂ (P2 — alertăm, nu blocăm)

### G7. CMBU (cea mai bună utilizare) = doar proză AI, nu o verificare structurată
Capitolul 5 (`generator.py:785-790`) și `ai/narrative.py:42-45` produc doar **text AI** pe CMBU. Nu există nicio verificare
a celor 4 teste (permis legal / posibil fizic / fezabil financiar / maxim productiv) și niciun semnal când utilizarea
existentă diferă de CMBU (ex. teren intravilan sub-utilizat). Pentru garantare, banca vrea CMBU argumentată, nu generică.
**Lipsă:** structurare pe 4 teste + alertă „utilizare actuală ≠ CMBU". Severitate **medium**.

### G8. Justificarea ajustărilor + gardă pe ajustarea NETĂ — absente
`engine/validation.py` gardează doar ajustarea **brută** (>25% alertează) și prețul corectat <=0. SEV 103 §20.5 / A10.8 cer
**justificarea obligatorie a ajustărilor nenule** și o gardă pe ajustarea **netă** (ajustări care se anulează reciproc dar
ascund comparabile slabe). **Lipsă:** alertă „ajustare nenulă fără justificare" + prag pe ajustarea netă. Severitate **medium**.

### G9. Neaplicarea unei abordări nu cere justificare + divergența mecanică între abordări
SEV 103 §40.3/§10.7 cer justificarea **neaplicării** unei abordări. `reconcile_profil` (`reconciliation.py`) face media
mecanică fără a gardă divergența excesivă între indicații înainte de mediere (există doar `valideaza_incrucisat` la 30% pe
piață↔cost, post-factum). **Lipsă:** prompt/câmp „de ce nu s-a aplicat abordarea X" + gardă de divergență la reconciliere.
Severitate **medium**.

### G10. Cost: ignoră costurile indirecte + profitul promotorului; depreciere liniară pe vârstă
`engine/cost.py` calculează CIB = Σ(cantitate×cost_unitar) — **doar costuri directe**. A30.11-A30.19 includ costurile
indirecte și (pentru valoarea de piață) profitul dezvoltatorului. Deprecierea e strict pe vârstă cronologică interpolată,
fără funcțional/extern auto. Checklistul propriu (`generator.py:601`) afirmă „costul exclude profitul dezvoltatorului" —
corect pentru garantare, dar lipsește linia de costuri indirecte. **Lipsă:** câmp costuri indirecte (opțional) + notă. Severitate **low-medium**.

### G11. DCF: valoare terminală = sumă manuală, fără Gordon/exit; rată nedocumentată
`engine/venit.py` (DCF) primește `valoare_reziduala` ca **input manual**, fără model Gordon/exit-yield și fără documentarea
ratei de actualizare (A20.22-A20.34). Pentru casă+teren la garantare DCF e rar, dar profilurile SPECIAL/INDUSTRIAL îl
folosesc. **Lipsă:** calcul valoare terminală + justificare rată. Severitate **low** (out-of-scope pentru casă, relevant la extindere).

---

## CÂMPURI/CAPABILITĂȚI BACKEND NEEXPUSE ÎN UI (plumbing — efort mic, impact direct)

### G12. `tip_valoare` selectabil — lipsă (hardcodat)
`models/meta.py:28` are `tip_valoare="Valoarea de piață (SEV 102)"` text liber; `profil.TipValoare` listează `"lichidare"`
ca **cod mort** (niciun profil nu îl folosește). Nu există mecanism UI/profil prin care evaluatorul să **ceară un tip de
valoare ≠ piață** ca termen de referință (GEV 520 §20). **Lipsă:** expunere selectabilă a tipului valorii. Severitate **low-medium**.

### G13. `utilizator_desemnat` (creditor/ANAF) — neexpus în UI
`meta.utilizator_desemnat` condiționează corect textul BIG (creditor → se înregistrează; ANAF → nu), DAR nu există input în
`dosar.html` — rămâne mereu pe default „creditor". **Lipsă:** select în tabul Proprietate. Severitate **low**.

### G14. `justificare_depreciere`, `structura`, `finisaje` — în model, neexpuse în UI
`BuildingData` are `justificare_depreciere`, `structura`, `finisaje` (`property.py:46-48`). Validarea
`valideaza_depreciere` **blochează** dacă deprecierea funcțională/externă e nenulă fără justificare — dar UI-ul nu oferă nici
câmpul de depreciere funcțională/externă, nici cel de justificare, deci evaluatorul nu poate satisface garda dacă o atinge
prin import. **Lipsă:** câmpuri UI pentru structură/finisaje (descriere) + depreciere funcțională/externă + justificare. Severitate **low-medium**.

---

## INTEGRĂRI / MODULE LIPSĂ (P3)

### G15. SEV 400 „Verificarea evaluării" — modul absent integral
GEV 520 §18 invocă explicit SEV 400. Nu există rol de verificator, raport de verificare, nici declarația de verificare
(SEV 400 §21-26). Multe bănci cer verificare independentă (evaluator cu specializarea VE, ≠ autorul). **Lipsă:** cel puțin un
„mod verificator" intern care rulează gardurile existente (`engine/validation`, `audit/validare_x`) și produce un raport de
neconformități în limbajul SEV 400; verificarea formală rămâne sarcină externă. Severitate **medium** (efort mare).

### G16. Verificare automată sancțiuni/PEP — lipsă (declarat explicit)
Tabul AML (`dosar.html:434`) avertizează corect că aplicația **NU verifică automat** sancțiuni/PEP și trimite manual la
OpenSanctions / EU Sanctions Map. Pentru un flux complet de garantare (KYC), integrarea unei verificări automate (sau cel
puțin deep-link pre-completat cu numele clientului) ar reduce un pas manual cu risc de omisiune. **Lipsă:** integrare/deep-link
verificare liste. Severitate **low** (acceptabil ca manual, dar e o capabilitate lipsă).

### G17. Grile notariale 2026 ca ancoră de plauzibilitate — neintegrate
Pentru garantare, o verificare a valorii estimate față de **grilele notariale** (ancoră oficială RO 2026) ar fi un control
de plauzibilitate util la verificarea bancară. Curs BNR e integrat automat (`curs_bnr.py` + `/api/curs-bnr`), dar grilele
notariale nu. **Lipsă:** import/comparație cu grila notarială pe localitate. Severitate **low**.

---

## Notă de încredere

Toate findings-urile se bazează pe citirea directă a codului (căi + linii indicate) și pe auditele de conformitate
existente (`docs/conformitate/D-garantare-adiacente.md`, `00-SINTEZA-conformitate.md`), care confirmă independent G1–G6,
G8–G11, G15. G5, G12–G14 sunt confirmate prin compararea câmpurilor de model cu inputurile expuse în `dosar.html`.
