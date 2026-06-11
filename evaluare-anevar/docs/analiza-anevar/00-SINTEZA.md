# 00 — SINTEZA CONSOLIDATĂ a analizei documentelor ANEVAR (pentru coordonatorul A)

> Consolidează cele **7 analize tematice** din `docs/analiza-anevar/` (aml-plan-ghid, aml-forme-norme,
> articole-piata-1, articole-piata-2, standarde-calitate, legal-norme-proceduri, crawl-anevar-ro)
> confruntate cu **SEV 2025 + codul aplicației** (flux casă+teren / garantare credit).
>
> **Verdict global:** NU există contradicție de fond cu SEV 2025. Documentele AML/legale/procedurale
> **completează** SEV 2025 pe zonele neacoperite (AML, arhivare, registru, GDPR); articolele de piață
> **operaționalizează** GEV 630/SEV 233; glosarul = vocabularul canonic 2025. Backend-ul (motor + AML)
> e **corect și mai bogat decât formularele-model**. Gap-ul dominant e de **acoperire/UI și de flux**,
> nu de logică greșită.
>
> Severitate: **[blocant]** = blochează un raport/dosar conform sau o obligație legală · **[important]** ·
> **[minor]**

---

## 1. CE PUTEM FOLOSI (top resurse + insight-uri, grupate)

### A. AML / Legea 129/2019 — reguli operaționale (din `aml-plan-ghid`, `aml-forme-norme`, `legal-norme-proceduri`)
- **SCOPUL evaluării ca factor de risc** (Ghid cap. 2 — exact domeniul app-ului): lichidare / insolvență /
  executare silită = risc (subevaluare frauduloasă); vânzare piață liberă & M&A = risc; **garantare credit
  bancar = risc redus** (banca dublează due diligence) DAR atenție la presiunea „valoare mare → credit maxim";
  impozitare/raportare = risc redus.
- **EDD la risc ridicat** (Legea art. 17 + Ghid): sursa fondurilor + a averii clientului + **aprobarea
  conducerii de rang superior pentru PEP** + monitorizare sporită + dreptul/obligația de a refuza lucrarea.
- **Beneficiar real din surse oficiale** (certificat constatator Reg. Comerțului + extras RBR) + **declarație
  pe proprie răspundere** la dosar; răspunsul „NU" la identificarea BR devine factor de risc; **RBR gratuit**
  pentru evaluatori ca entități raportoare (confirmat în pagina-index ANEVAR).
- **Registrul lucrărilor de evaluare cu nivel de risc per client** (Plan cap. V) — cerut EXPLICIT și verificat
  la inspecție; ~13 câmpuri (nume, nr. contract, scop, risc, cine a evaluat/revizuit).
- **Indicatori suplimentari față de cei 10 din HCD 58** (Ghid cap. 3): frecvență neobișnuită, revânzări rapide,
  diferență mare piață-preț nejustificată, onorariu peste piață pentru a influența rezultatul, structură
  offshore/companie-paravan, documentație falsificată.
- **Geografie evaluată separat** pentru țara clientului/BR vs. amplasarea bunului; non-SEE + paradisuri fiscale
  (Panama, Cayman, Seychelles, BVI) = risc chiar dacă nu pe lista neagră; liste sancțiuni transmise **lunar** de ANEVAR.
- **Confirmat solid în cod:** reguli HARD (PEP efectiv, sancțiuni, țară risc înalt, tranzacție complexă, canal
  la distanță forțează „sporit"), praguri (numerar 10k EUR, ocazional/anti-fragmentare 15k EUR), retenție 5 ani,
  RTN +3 zile lucrătoare, suspendare RTS +24h, tipping-off (RTS stocat separat în `aml_confidential/`),
  decizie de desemnare doar la PJ (PFA exclus).

### B. Metodologie de piață / venit / teren (din `articole-piata-1` + `articole-piata-2`)
- **Cele 4 capcane ale selecției de comparabile** (segment de preț unic, proiecte depășite funcțional, selecție
  necorespunzătoare, sub-piață socio-economică greșită) → reguli de validare a omogenității în `engine/market.py`.
- **Cele 4 metode de derivare a ratei de capitalizare din piață** (vânzare-închiriere etc.) + build-up — manual
  direct pentru `engine/venit.py`, unde rata e azi input liber (singura gardă: rată>0).
- **Defalcarea OPEX / „service charge"** (15+ poziții) + distincția chirie brută/netă + fond de rulment ≠ OPEX —
  defalcă scalarul `cheltuieli_exploatare` din `DateVenit`.
- **Metoda reziduală / a parcelării terenului** (cele 5 întrebări ale dezvoltatorului + durata de absorbție) —
  `engine/land.py` acoperă doar comparația EUR/mp din cele două metode admise de SEV 233/GEV 630.
- **Principii economice de cartier** (progresie/regresie/conformitate + faza de ciclu) → bază pentru ajustarea de
  localizare, CMBU și riscul GEV 520 A5(a).
- **Procesul în 6 pași pe scopul de garantare** (min 3 comparabile, 3–6 luni, <1 km, valoare contributorie ≠ cost,
  supra-îmbunătățiri ≈ recuperare 0, reconciliere ca plajă) — validează deciziile existente + expune garduri lipsă
  (recență/proximitate comparabile, valoare terminală DCF Gordon/exit-cap).
- **Distincția ofertă speculativă vs. tranzacție reală** la teren → ajustare ofertă→tranzacție obligatorie când
  comparabilele sunt doar oferte; checklist de riscuri fizice teren (inundabil, contaminare, topografie, formă).

### C. Calitate / terminologie / dosar (din `standarde-calitate`, `legal-norme-proceduri`)
- **Glosarul oficial ANEVAR** = dicționarul canonic 2025 (include ESG, specialist, scepticism profesional, AVM,
  riscul evaluării, utilizare/utilizator desemnat). Termeni de adoptat în UI/raport: „utilizare desemnată"
  (fostul Scop), „abordarea prin piață" (fostă „comparație").
- **Verificare internă a calității pre-emitere** (pașii a–e) — azi doar AFIRMAT în declarația de conformitate
  (`generator.py:261–265`), nu existent ca procedură/checklist.
- **Structura formală a dosarului de lucru** în 4 secțiuni (Contractare / Info client / Prelucrări evaluator /
  Raport preliminar+final) + confidențialitate/integritate/retenție.
- **Procedura de arhivare ANEVAR §4–6** = lista exactă a documentelor de dosar + registru ~13 câmpuri + structura
  `2025_NrLucrare_NumeClient` (mapează ~1:1 pe `dosare_fs.py`).
- **Retenție min. 5 ani** pentru TOATE documentele misiunii (nu doar AML); **Recipisa BIG/BIF** = document anexat
  obligatoriu la dosar (Procedura §4 + GEV 520 §83–84).
- **Graniță anti-contaminare:** valoarea minimă din studiile notariale (HCD 74 art. 111) NU e valoare de piață SEV
  și NU poate fi sursă pentru rapoarte — app-ul nu trebuie să amestece grile notariale cu comparabilele.

---

## 2. GAP-URI DE IMPLEMENTARE (prioritizate, cu document-sursă)

### [BLOCANT]
| # | Gap | Sursă |
|---|-----|-------|
| S-1 | **Scopul/tipul evaluării NU e factor de risc** în motorul AML (lichidare/insolvență/executare = risc; garantare = redus) | aml-plan-ghid G1 |
| S-2 | **EDD risc ridicat nu colectează sursa fondurilor/averii + aprobarea conducerii pentru PEP** (cerință legală centrală art. 17) | aml-plan-ghid G2 |
| S-3 | **RBR (Registrul Beneficiarilor Reali)** — câmp în model, absent din UI și din fișa KYC | aml-forme-norme |
| S-4 | **Manual BIG + recipisa BIG ca artefact de flux** (scopul #1 al app-ului: garantare credit; azi doar text) — necesită descărcare manual + câmp/atașament | crawl-anevar-ro; legal-norme-proceduri G(BIG/BIF) |
| S-5 | **Secțiune ESG / riscuri fizice** (PdV ANEVAR garantare) — deja urmărit ca **G1 blocant** în `SEV-2025-gap-implementare.md`; întărit de articole-piata + glosar | crawl-anevar-ro; articole-piata-1; standarde-calitate |

### [IMPORTANT]
| # | Gap | Sursă |
|---|-----|-------|
| I-1 | **Registrul de evidență a rapoartelor de evaluare** (~13 câmpuri) lipsește ca livrabil exportabil (cerut la inspecție + Procedura §6) | legal-norme-proceduri; aml-plan-ghid G5 |
| I-2 | **Număr de lucrare secvențial** (AAAA/NNNN) + câmp verificare internă (cine+când) + dată retenție 5 ani pe dosarul de evaluare + export per-dosar pentru audit | legal-norme-proceduri |
| I-3 | **Declarație pe proprie răspundere a clientului** (BR + sursa fondurilor) negenerată | aml-plan-ghid G6 |
| I-4 | **Beneficiar real lipsă la PJ nu generează avertisment/indicator de risc**; **PEP** trimite doar bifa (fără categorie/tip/data încetării) | aml-plan-ghid G3; aml-forme-norme |
| I-5 | **Indicatorii din ghid** neacoperiți de cei 10 din HCD 58 (revânzări rapide, onorariu-influență, offshore etc.) | aml-plan-ghid G4 |
| I-6 | **Pas de verificare internă a calității pre-emitere** (checklist QC live) + **pas de acceptare a misiunii** (conflict de interese, competență) | standarde-calitate G-Q1, G-Q4 |
| I-7 | **Rata de capitalizare = input liber** — fără derivare din piață, fără validare de plauzibilitate, fără documentarea sursei | articole-piata-2 G1 |
| I-8 | **Cheltuieli de exploatare = scalar unic** — fără defalcare OPEX și fără distincția chirie brută/netă | articole-piata-2 G2 |
| I-9 | **Validarea omogenității comparabilelor** (segment unic + aceeași sub-piață) + **gardă recență/proximitate** lipsesc din `engine/validation.py` | articole-piata-1; articole-piata-2 G7 |
| I-10 | **Ajustarea ofertă→tranzacție** neimpusă când comparabilele sunt doar oferte (risc speculativ la teren) | articole-piata-1; articole-piata-2 |
| I-11 | **Metoda reziduală / a parcelării terenului** (`land.py` are doar comparație EUR/mp) | articole-piata-1; articole-piata-2 G5 |
| I-12 | **Analiză de piață structurată** (fază ciclu cartier, segment de preț, tendință) + **CMBU pe cele 4 teste** — azi narativ AI liber/placeholder | articole-piata-1 |
| I-13 | **Câmp de riscuri ecologice/fizice teren** (rezervoare îngropate, inundabil, alunecări, contaminare) — întărește S-5/ESG | articole-piata-1; articole-piata-2 |
| I-14 | **Actualizare/revizuire anuală** (date client + norme interne): termen calculat dar fără reminder/flux | aml-plan-ghid G7 |
| I-15 | **Mențiunea AML în declarația de conformitate** a raportului SEV (punte AML↔raport) | aml-plan-ghid G9 |
| I-16 | **Structura formală a dosarului de lucru** (4 secțiuni ANEVAR + integritate/retenție) | standarde-calitate G-Q2; legal-norme-proceduri |
| I-17 | **Versiuni AML actualizate** (HCD 62 cu CFH 74/2025, oct. 2025) + **politica GDPR ANEVAR** înlocuită oct. 2025 (de aliniat draft-urile GDPR) | crawl-anevar-ro |
| I-18 | **Date oficiale de piață ANEVAR** (Indice imobiliar + rapoarte trimestriale rezidențiale) pentru `indice_anevar.py` + secțiunea analiza pieței | crawl-anevar-ro |
| I-19 | **Valoarea terminală DCF** = sumă manuală; lipsesc Gordon și exit-cap | articole-piata-2 G4 |

### [MINOR]
| # | Gap | Sursă |
|---|-----|-------|
| m-1 | Audit terminologic UI+raport vs. glosar (Scop→Utilizare desemnată, comparație→abordarea prin piață) + glosar in-app + întărire disclaimer „nu este AVM" | standarde-calitate G-T1/T2/T3 |
| m-2 | Gardă anti-contaminare comparabile din grile notariale (HCD 74 art. 111) | standarde-calitate G-S1 |
| m-3 | Conceptul de supra-îmbunătățire (cost ≫ valoare contributorie) + disclaimer „evaluare ≠ studiu de fezabilitate/absorbție" | articole-piata-1; articole-piata-2 G8 |
| m-4 | Câmpuri identificare PJ/împuternicit/traducere + „modalitate identificare BR" + măsuri de atenuare ca checklist + persistență dosar AML | aml-forme-norme |
| m-5 | Criptarea arhivei electronice (Procedura §10); permisiunile 0o700/0o600 sunt no-op pe Windows (mediul-țintă) | legal-norme-proceduri |
| m-6 | Disclaimer din `documente.py` contrazice screening-ul real (G12) | aml-plan-ghid |

---

## 3. CONTRADICȚII GĂSITE + REZOLVARE (regula: SEV 2025 / cerința mai exigentă câștigă)

| # | Contradicție | Rezolvare |
|---|--------------|-----------|
| C-1 | Tabelul de sinteză al Planului AML zice încă „transmitere la ONPCSB a desemnării", dar corpul normativ + HCD 62 zic că numele NU se mai comunică (doar decizie internă) | **Corpul normativ câștigă** — app-ul procedează deja corect (decizie internă, fără adresă ONPCSB) |
| C-2 | Definiția colocvială a valorii de piață din articole vs. SEV 102 | **SEV 102 câștigă** — deja în cod |
| C-3 | „Terenul crește mereu în timp" (articol) vs. nuanțarea ciclică | **Nuanțarea ciclică câștigă** — fără automatism de apreciere în motor |
| C-4 | UI „Scop" vs. glosar 2025 „Utilizare desemnată"; UI „comparație" vs. „abordarea prin piață" | **Glosar 2025 câștigă** — renumire în UI/raport (m-1) |
| C-5 | Termen de păstrare: SEV 106 „rezonabil" vs. Legea 129/2019 + ANEVAR „min. 5 ani" | **5 ani câștigă** — deja în AML; de extins pe dosarul de evaluare (I-2) |
| C-6 | Studii notariale (HCD 74 art. 111) ca posibilă sursă de valori vs. SEV | **SEV câștigă** — studiile notariale NU sunt valoare de piață, gardă anti-contaminare (m-2) |
| C-7 | Disclaimer din `documente.py` (zice că nu face screening) vs. screening-ul real implementat | **Codul real câștigă** — corectează textul disclaimer-ului (m-6) |

---

## 4. DOCUMENTE LIPSĂ de descărcat de pe anevar.ro (WebFetch e blocat 403 — descărcare manuală/alt canal)

| Prioritate | Document | URL |
|---|---|---|
| **blocant** | BIG — Manual de utilizare (recipisa + câmpuri export) | `anevar.ro/images/documente/manual_utilizare_ad-3_0.pdf` |
| **blocant** | PdV ANEVAR — aprecierea riscurilor fizice la garantare (acoperă ESG/riscul evaluării) | `anevar.ro/noutate/235/...` |
| important | HCD 62 actualizat cu CFH 74/2025 (formular KYC consolidat, oct. 2025) | `anevar.ro/images/_upload/hcd-62-actualizata-cfh-74-2025.pdf` |
| important | Pagina-index Ghiduri L.129/2019 (modelele AML curente) | `anevar.ro/p/profesie/aplicarea-legii-1292019/ghiduri-si-documente-utile...` |
| important | Indicele imobiliar ANEVAR (sursă `indice_anevar.py`) | `anevar.ro/p/informatii-din-piata/informatii-statistice-anevar/indicele-imobiliar-anevar` |
| important | Analize imobiliare — rapoarte trimestriale rezidențiale | `anevar.ro/p/informatii-din-piata/analize-imobiliare` |
| important | Politica de protecție a datelor ANEVAR (înlocuită oct. 2025 — alinia draft-urile GDPR) | pagina ANEVAR protecția datelor |
| opțional | Glosar de termeni oficial (live, © 2026) — audit terminologic | `anevar.ro/p/glosar-de-termeni` |
| opțional | Bazele evaluării 2024 (referință formule motor) | `anevar.ro/images/_upload/brosura-bazele-evaluarii-2024.pdf` |

---

## 5. AGENȚI DE IMPLEMENTARE de pornit + ORDINE

**Principiu:** backend AML + motor sunt corecte → majoritatea muncii e **UI + flux + documente**, nu rescriere de
motor. Grupez pe zone independente (pot rula în worktree-uri paralele) cu ordonare pe dependențe.

**Val 1 — descărcare resurse (blocant pentru restul, fără cod):**
- **Agent A0 — „resurse anevar.ro"**: descarcă manual cele 9 documente din §4 în `docs/analiza-anevar/surse/`
  (prioritate BIG manual + PdV riscuri fizice + HCD 62/CFH 74 + politica GDPR). Deblochează A2, A3, A6.

**Val 2 — paralel (după A0):**
- **Agent A1 — „AML risc & EDD" (motor)**: S-1 (scop = factor risc) + S-2 (EDD: sursă fonduri/avere + aprobare
  conducere PEP) + I-5 (indicatori ghid) + I-4 (BR lipsă→risc, PEP categorie/tip/dată). Atinge `aml/risc.py`,
  `aml/indicatori.py`, `aml/models`.
- **Agent A2 — „AML UI & documente KYC"**: S-3 (RBR în UI + fișă KYC) + I-3 (declarație proprie răspundere) +
  m-4 (câmpuri PJ/împuternicit, măsuri atenuare). Atinge `aml.html`, `aml/documente.py`. Depinde de HCD 62/CFH 74 (A0).
- **Agent A3 — „garantare & ESG/BIG"**: S-4 (recipisă BIG ca atașament/câmp) + S-5/I-13 (secțiune ESG + riscuri
  fizice — coordonează cu **G1 din `SEV-2025-gap-implementare.md`** ca să nu dublezi). Depinde de A0 (BIG manual + PdV).
- **Agent A4 — „motor venit & teren"**: I-7 (rată capitalizare: derivare+validare+sursă) + I-8 (defalcare OPEX,
  chirie brută/netă) + I-11 (metodă reziduală teren) + I-19 (valoare terminală DCF Gordon/exit-cap). Atinge
  `engine/venit.py`, `engine/land.py`. Pur izolat, poate porni imediat.
- **Agent A5 — „validare comparabile & analiză piață"**: I-9 (omogenitate + recență/proximitate) + I-10
  (ofertă→tranzacție) + I-12 (analiză piață structurată + CMBU 4 teste) + m-2 (anti-contaminare notarial) + m-3
  (supra-îmbunătățire). Atinge `engine/validation.py`, `engine/market.py`, `report/generator.py`. Pur izolat.

**Val 3 — flux & conformitate (după ce S-1..S-3 ating modelele AML):**
- **Agent A6 — „registru & dosar de evaluare"**: I-1 (registrul rapoartelor exportabil) + I-2 (nr. lucrare
  secvențial + verificare internă + retenție 5 ani + export per-dosar) + I-16 (structura dosarului 4 secțiuni) +
  I-14 (reminder actualizare/revizuire anuală). Atinge `dosare_fs.py`, `storage.py`, flux livrabile.
- **Agent A7 — „QC & acceptare misiune"**: I-6 (checklist QC pre-emitere live + pas acceptare misiune) + I-15
  (mențiune AML în declarația de conformitate). Atinge `report/generator.py`, flux pre-emitere.

**Val 4 — cosmetică (oricând, low-risk):**
- **Agent A8 — „terminologie & GDPR"**: m-1 (audit terminologic + glosar in-app + disclaimer „nu e AVM") +
  m-6 (corectare disclaimer `documente.py`) + I-17 (alinia draft-urile GDPR la politica ANEVAR oct. 2025) +
  m-5 (criptare arhivă; notă permisiuni no-op pe Windows) + I-18 (cablare date oficiale ANEVAR în
  `indice_anevar.py` — depinde de A0).

**Ordine sintetică:** A0 → {A1, A4, A5} în paralel imediat; {A2, A3} după A0; A6/A7 după A1–A3 ating modelele;
A8 oricând. Notă pe text juridic AML: respectă regula de memorie — nu edita/commit textul juridic AML în
foreground (loop-ul autonom îl deține); A1/A2 ating LOGICA și UI, nu corpul normativ generat.
