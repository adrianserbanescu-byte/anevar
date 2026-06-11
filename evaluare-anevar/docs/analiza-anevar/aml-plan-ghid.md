# AML/CFT — Plan de măsuri (H47/2026) + Ghid de evaluare a riscurilor SB/FT — analiză vs. cod

> **Tema:** `aml-plan-ghid`. Analiză a două documente ANEVAR și confruntarea lor cu modulul AML al aplicației.
>
> **Documente-sursă:**
> - `Anexa nr. 1 — Plan de măsuri AML/CFT pentru evaluatorii autorizați (HCD nr. 62/2025, modificată prin HCD 47/2026)` — **document NOU**, organizatoric/sectorial.
> - `Ghid de evaluare a riscurilor SB/FT pentru evaluatorii autorizați ANEVAR` — operațional, factori de risc + tipologii.
>
> **Cod analizat:** `src/evaluare/aml/` (models, risc, liste, indicatori, documente, raportare, store, incadrare, serviciu, constante) + `src/evaluare/web/routers/aml.py` + `src/evaluare/web/schemas.py`.
>
> **Regulă de prioritate aplicată:** SEV 2025 are PRIORITATE; în rest documentul mai NOU câștigă. Aici nu apare contradicție directă cu SEV 2025 (ambele documente sunt *sub*-ordonate Legii 129/2019 și complementare SEV 100, care doar trimite la „legislația aplicabilă"). Prioritatea relevantă e între cele două documente AML — vezi §2.
>
> Stare: ✅ implementat corect · 🟡 parțial · 🔴 lipsă · ⛔ greșit/contradicție
> Severitate: **blocant** (B) · **important** (M) · **minor** (m)

---

## 1. CE CONȚIN documentele + CE-I UTIL pentru app

### 1.1. Planul de măsuri AML/CFT (H47/2026) — `anexa-nr-1-plan-de-m-suri...`

Document **organizatoric, la nivel de sector/asociație**, nu o procedură per-lucrare. Cele 6 capitole:

| Cap. | Conținut | Ce-i util pentru app |
|---|---|---|
| **I.** Îmbunătățirea aplicării Legii 129/2019 | 5 arii de conformare: (1) **desemnare responsabil ONPCSB** (PJ da / PF nu — direct evaluatorul), cont în sistemul electronic ONPCSB; (2) **proceduri standard KYC + evaluare risc** (formular unificat, categorii redus/mediu/ridicat, screening sancțiuni/PEP, **actualizare anuală** a datelor); (3) **identificare beneficiar real** (Reg. Comerțului, Registrul beneficiarilor reali, declarație pe proprie răspundere); (4) **arhivare 5 ani** (registru al lucrărilor, securitate digitală); (5) **raportare RTS/RTN** + monitorizare continuă + tipping-off. | Confirmă și completează modelul de date și fluxul implementat. **Esențial:** „decizie internă de desemnare" (nu se mai trimite adresă la ONPCSB), „cod de raportor doar dacă există obligația", **actualizare anuală a clienților pe termen lung**, **declarație pe proprie răspundere a clientului** privind BR. |
| **II.** Control intern și audit conformitate | Norme interne documentate + **revizuire anuală**; structură/audit intern la firme medii-mari (self-audit anual pe lucrări aleatorii); ton de la conducere. | Confirmă generatorul de **norme interne** + nevoia de **dată de revizuire** și self-audit (nu e în app). |
| **III.** Instruire și formare continuă | Curs anual obligatoriu + testare; AML în examenul inițial; bibliotecă AML online; workshop-uri. | În afara scopului app (proces ANEVAR), dar app poate **genera materiale** (FAQ, modele). |
| **IV.** Date de supraveghere | ANEVAR agregă chestionarele și ajustează criteriile de risc/inspecție. | Proces ANEVAR; irelevant direct pentru app, dar **profil de risc per client** se aliniază ideii. |
| **V.** Monitorizare extinsă + raportări anuale | Checklist AML în Nota de inspecție; **registru al lucrărilor cu nivelul de risc per client**, verificat la inspecție. | **Direct util:** app trebuie să poată produce/exporta **registrul de lucrări cu risc** și dosarul AML pe care îl cere inspectorul. |
| **VI.** Concluzii + tabel termene | Indicatori-țintă: 100% responsabil desemnat, 100% formular KYC, BR de la 36,8% → 80%, 0 documente AML lipsă la control, min. 1 RTS dacă apare caz. | Țintele = checklist de conformitate pe care app îl poate susține. |

**Statistici-cheie din plan** (utile ca avertismente în UI): doar **36,8%** consultă registrul BR; doar **33%** fac verificări PEP suplimentare; doar **28%** pentru jurisdicții de risc; **0 RTS/RTN** transmise 2021–2024 (sub-raportare).

### 1.2. Ghidul de evaluare a riscurilor SB/FT — `ghid-de-evaluare-a-riscurilor...`

Document **operațional, per-lucrare** — sufletul motorului de risc. 4 categorii de factori + clasificare + măsuri + tipologii:

1. **Tipologia clientului / beneficiarului:** PF vs PJ; rezident vs nerezident; **PEP → automat risc ridicat**; structuri opace/offshore/firme-paravan/acțiuni la purtător; reputație/istoric/sector sensibil (imobiliare, crypto, jocuri de noroc, metale prețioase); **comportament față de KYC** (evaziv = alarmă).
2. **Tipul și scopul evaluării** (factor de risc nou față de cod): vânzare/cumpărare piață liberă = **risc mai mare**; M&A; **lichidare/insolvență/executare silită = risc** (subevaluare frauduloasă); **garantare credit bancar = risc redus** (banca dublează DD) DAR atenție la presiunea „valoare mare ca să iau credit maxim"; impozitare/raportare financiară = risc redus.
3. **Indicatori de risc / semnale de alarmă:** lipsă transparență/refuz BR; comportament evaziv/presiuni/urgență artificială + onorariu peste piață; **frecvență neobișnuită** a solicitărilor; **documentație insuficientă/falsificată**; tranzacții repetitive cu același activ; **BR ascuns**; diferențe mari piață↔preț tranzacționat; revânzări rapide succesive; mită prin proprietăți; credite ipotecare multiple/umflate.
4. **Risc geografic:** liste negre (Coreea de Nord, Iran); FATF/UE țări terțe cu deficiențe; non-SEE; paradisuri fiscale (Panama, Cayman, Seychelles, BVI); zone de conflict/sancțiuni regionale (Rusia, Belarus); **amplasarea bunului** (de ce nu un evaluator local?).

**Clasificare scăzut/mediu/ridicat** cu criterii orientative + **măsuri pe niveluri** (simplificate/standard/suplimentare-EDD). EDD = **sursa fondurilor/averii**, **aprobarea conducerii** pentru PEP, monitorizare sporită, screening extins, dreptul de a **refuza lucrarea**. **Documentarea raționamentului** de încadrare e obligatorie; păstrarea dovezilor (capturi de ecran).

**4 tipologii / studii de caz:** (1) PEP + subevaluare pentru mită; (2) investitor străin + companie paravan + supraevaluare; (3) credit fraudulos pe evaluare umflată; (4) spălare prin revânzări succesive (cu rol util BIG).

**Ce-i cel mai util pentru app:** tot capitolul 2 (scopul ca factor de risc), EDD = sursa fondurilor + aprobare conducere, documentarea justificării de încadrare, registrul de clienți cu nivel de risc.

---

## 2. RELEVANȚA vs. SEV 2025 + CONTRADICȚII rezolvate

**SEV 2025 nu tratează direct AML** — `SEV 100 — Cadrul general` cere doar ca evaluatorul să respecte și să menționeze în raport „cerințele legale aplicabile" (inclusiv Legea 129/2019), iar înainte de misiune să-și verifice clientul pentru a evita implicarea în activități ilegale. Ghidul însuși confirmă acest lucru (cap. „Corelare cu SEV 100"). **Deci nu există conflict de fond SEV 2025 ↔ AML**; AML e o cerință de conformitate *în interiorul* SEV.

**Punct de joncțiune cu SEV/codul:** ghidul recomandă ca raportul să menționeze la secțiunea de conformitate „evaluarea a fost efectuată în conformitate cu standardele SEV și cu legislația aplicabilă (inclusiv Legea 129/2019)". Codul generatorului de raport (`report/generator.py`, declarația SEV 100) **nu** include această frază AML — punct de legătură între cele două module (vezi G9).

### Contradicții rezolvate (între cele două documente AML și cu codul)

| # | Tensiune | Cine câștigă + de ce |
|---|---|---|
| C1 | **Desemnare responsabil:** versiuni vechi cereau „adresă la ONPCSB"; Planul H47/2026 spune că numele **nu se mai comunică** la ONPCSB — e nevoie doar de **decizie internă**. | **Planul H47/2026** (mai nou). Codul e deja aliniat: `documente.genereaza_decizie_desemnare` produce decizie internă, nu adresă. Totuși **tabelul de sinteză din plan (rândul „Desemnare responsabil ONPCSB")** spune încă „Transmiterea către ONPCSB a desemnării" — contradicție *internă* a planului; câștigă **corpul** documentului (text normativ explicit), tabelul e rezumat neglijent. App-ul a procedat corect. |
| C2 | **Cine are obligația responsabilului:** Planul — PJ da, PF/PFA nu (responsabilitate directă). | Concordă cu `incadrare.necesita_persoana_desemnata` (PFA/PF → False). ✅ |
| C3 | **PEP = risc ridicat automat** (ghid) vs. scoring ponderat (cod). | **Ghidul + Legea art. 17** (regulă HARD). Codul implementează corect: `risc._client_pep_efectiv` forțează „sporit" indiferent de scor. ✅ |
| C4 | **Beneficiar real ne-identificabil:** ghidul spune „evaluatorul nu ar trebui să continue relația"; codul doar marchează `consultat_registru_central`/`neconcordanta_registru`, fără a bloca. | **Ghidul** (mai strict, aliniat Legii). Codul lasă decizia evaluatorului (om-în-buclă), ceea ce e acceptabil, dar nu emite un avertisment/indicator când BR lipsește la PJ — vezi G3. |
| C5 | **Definiție beneficiar real:** prag >25% în cod vs. „identifică cine controlează în ultimă instanță" în documente. | Fără conflict — `constante.PRAG_BENEFICIAR_REAL = 0.25` e pragul legal art. 4(2); documentele descriu același concept. ✅ |

**Concluzie §2:** documentele AML **completează** SEV 2025, nu îl contrazic. Codul e deja aliniat la regulile HARD (PEP, sancțiuni, țară risc înalt, tranzacție complexă, canal la distanță) și la praguri (numerar 10k€, ocazional 15k€, retenție 5 ani). Gap-urile sunt de **acoperire** (factori și pași pe care documentele îi cer, dar app-ul nu îi colectează/calculează încă), nu de corectitudine.

---

## 3. GAP-URI de implementare (ce ar trebui app-ul să adauge)

### 0. Ce e DEJA SOLID (ca să nu reparăm ce merge)

| Cerință document | Cod | Stare |
|---|---|---|
| 4 categorii de factori de risc (client/produs/canal/geografic) cu ponderi | `risc.evalueaza_risc` + `models.FactorRisc` | ✅ |
| Reguli HARD → „sporit": PEP efectiv, sancțiuni, țară risc înalt, tranzacție complexă, canal la distanță | `risc.py:135-156` | ✅ |
| PEP efectiv = titular + 12 luni post-funcție (art. 3(6)) | `risc.pep_efectiv` + `constante.PERIOADA_POST_PEP_LUNI` | ✅ |
| 3 niveluri de măsuri (simplificate/standard/suplimentare) mapate pe categorie | `risc.nivel_masuri` | ✅ |
| Cei 10 indicatori de suspiciune (HCD 58 art. 6(10)) + propunere RTS | `indicatori.py` | ✅ |
| Screening tolerant sancțiuni/PEP (fără decizie automată, „verifică manual") | `liste.screening` | ✅ |
| Verificare țară risc înalt / necooperantă | `liste.este_tara_risc` | ✅ |
| Identificare BR la PJ (model + procent + tip control + PEP + flag registru) | `models.BeneficiarReal`, `ClientPJ` | ✅ |
| Decizie de desemnare DOAR la PJ (PFA exclus) | `incadrare`, `documente.genereaza_decizie_desemnare` | ✅ |
| Praguri RTN 10k€, conversie BNR, anti-fragmentare 15k€, termen 3 zile lucrătoare | `raportare.py`, `constante.py` | ✅ |
| RTS cu avertisment tipping-off + store SEPARAT de dosar (art. 38), retenție 5 ani | `raportare.py`, `store.StoreAML`, router `aml_dir` | ✅ |
| Generare norme interne (7 capitole, Norme art. 8(1) a-g) | `documente.genereaza_norme_interne` | ✅ |
| Fișă KYC + evaluare de risc .docx, igienă PII (fișier temp șters) | `documente`, `routers/aml.py:_doc_response` | ✅ |
| Reevaluare periodică pe categorie (12/24/36 luni) | `risc._LUNI_REEVALUARE`, `data_reevaluare` | ✅ |

---

### GAP-uri

#### G1 🔴 — Scopul/tipul evaluării NU e factor de risc **[blocant]**
**Cerință (ghid, cap. 2 — întreg):** scopul evaluării este un factor de risc de sine stătător. Vânzare pe piață liberă = risc mai mare; **lichidare/insolvență/executare silită = risc** (subevaluare frauduloasă); M&A = risc; garantare credit / impozitare / raportare financiară = risc redus. Planul (cap. I.2) cere ca formularul KYC să cuprindă „natura și scopul evaluării".
**Cod:** `risc.Semnale` are doar `tranzactie_uzuala`/`tranzactie_complexa` (booleeni generici); nu există câmp `scop`/`tip_evaluare` care să modeleze automat factorul „produs/serviciu". Evaluatorul trebuie să traducă manual scopul în `tranzactie_complexa`, ceea ce **anulează** ghidarea pe care o cere ghidul.
**De ce blochează:** e fix domeniul app-ului (garantare credit) și exact factorul pe care ghidul îl dezvoltă cel mai mult; lipsa lui face evaluarea de risc incompletă față de checklist-ul de inspecție.
**Recomandare:** adaugă `scop: Literal["garantare_credit","vanzare_piata","mna","lichidare_insolventa_executare","impozitare","raportare_financiara",...]` în `Semnale`; mapează în `f_produs` (lichidare/insolvență/executare + vânzare piață liberă → ridică; garantare/impozitare/raportare → coboară). Expune-l în `AmlEvaluareRequest` și în `aml.html`.

#### G2 🔴 — EDD: sursa fondurilor + aprobarea conducerii pentru PEP nu sunt colectate/cerute **[blocant]**
**Cerință:** pentru risc ridicat, ghidul + Legea art. 17 cer **EDD**: (a) **obținerea de informații despre sursa fondurilor și a averii** clientului; (b) **aprobarea conducerii de rang superior** înainte de a iniția/continua relația cu un PEP; (c) monitorizare sporită.
**Cod:** `nivel_masuri` returnează doar eticheta „suplimentare". Nu există câmp `sursa_fonduri` în niciun model, nici flag `aprobare_conducere_pep`, nici un checklist EDD generat. Fișa KYC nu listează pașii EDD obligatorii.
**De ce blochează:** EDD e cerința legală centrală la risc ridicat; un raport AML care declară „măsuri suplimentare" fără a documenta sursa fondurilor + aprobarea conducerii nu trece o inspecție.
**Recomandare:** câmpuri `sursa_fonduri: str | None` și `aprobare_conducere: bool` în `DosarAML`/KYC; când `categorie == "sporit"`, serviciul întoarce un **checklist EDD** (sursa fondurilor obținută? aprobare conducere pentru PEP? monitorizare sporită setată?) și fișa KYC le tipărește ca rubrici obligatorii.

#### G3 🟡 — BR lipsă la PJ nu generează avertisment/indicator **[important]**
**Cerință:** Planul (I.3) face din răspunsul „NU" la identificarea BR un **factor de risc**; ghidul spune că imposibilitatea identificării BR e „semnal de alarmă clar" și că relația „nu ar trebui continuată". Țintă: consultarea registrului BR de la 36,8% → 80%.
**Cod:** `ClientPJ.beneficiari_reali` poate fi listă goală fără nicio consecință; `serviciu.evalueaza_relatie` nu semnalează absența BR la PJ. `consultat_registru_central`/`neconcordanta_registru` există pe `BeneficiarReal` dar nu intră în logica de risc.
**Recomandare:** în `serviciu`/`risc`, dacă `client` e PJ și `beneficiari_reali == []` (sau niciunul cu `consultat_registru_central`), adaugă un motiv/indicator „beneficiar real neidentificat — Legea art. 4/art. 17" și ridică factorul client. Tipărește în fișa KYC un avertisment vizibil (deja există placeholder „De completat" — de promovat la alertă).

#### G4 🟡 — Indicatori din ghid neacoperiți de cei 10 din HCD 58 **[important]**
**Cerință (ghid, cap. 3):** semnale de alarmă suplimentare: **frecvență neobișnuită / repetată a solicitărilor** pentru același client/activ; **revânzări rapide succesive** (carte funciară); **documentație insuficientă/falsificată**; **diferență mare piață↔preț tranzacționat fără justificare**; **onorariu peste piață pentru a influența rezultatul**; **structură offshore/companie-paravan în poziția de cumpărător/client**.
**Cod:** `indicatori.INDICATORI` are 10 chei (HCD 58). Unele se suprapun (`istoric_atipic_tranzactionare`, `presiune_valoare_predeterminata`), dar lipsesc explicit: revânzări rapide succesive, diferență mare valoare↔preț, onorariu peste piață, structură offshore/paravan, documentație falsificată ca atare.
**De ce contează:** tipologiile 2-4 din ghid (paravan/supraevaluare, credit fraudulos, revânzări) nu au indicator dedicat care să declanșeze propunerea de RTS.
**Recomandare:** extinde `SemnaleIndicatori`/`INDICATORI` cu chei noi (temei: ghidul + Ghidul ONPCSB imobiliar feb. 2022 citat de ghid), păstrând cei 10 din HCD 58 ca bază obligatorie.

#### G5 🟡 — Registru al lucrărilor de evaluare cu nivel de risc per client — neexportabil **[important]**
**Cerință:** Planul (cap. V) + ghidul („Registru al clienților și lucrărilor cu nivelurile de risc") cer un **registru/index** (nume client, nr. contract, scop, risc redus/mediu/ridicat, cine a evaluat/revizuit), **cerut explicit de ANEVAR la monitorizarea extinsă** și verificat la inspecție.
**Cod:** `store.StoreAML` persistă RTS/RTN/dosar ca fișiere JSON separate, dar **nu există un export consolidat „registru de lucrări cu risc"** și niciun endpoint care să-l producă. `serviciu.evalueaza_relatie` returnează rezultatul per-relație, dar nu se agregă într-un registru.
**De ce contează:** e fix artefactul pe care inspectorul îl cere; lipsa lui = neconformitate la control.
**Recomandare:** endpoint `GET /api/aml/registru` (sau export .xlsx/.docx) care agregă dosarele AML cu: client, scop, categorie de risc, dată evaluare, dată reevaluare, indicatori activi, RTS asociat (fără a divulga conținutul RTS — doar marcaj).

#### G6 🟡 — Declarație pe proprie răspundere a clientului privind BR — negenerata **[important]**
**Cerință:** Planul (I.3) recomandă ca la dosar să fie păstrată **declarația pe proprie răspundere a clientului** privind realitatea informațiilor despre BR; pentru risc ridicat, ghidul cere declarație/documente privind sursa fondurilor.
**Cod:** generatorul de documente (`documente.py`) produce norme, evaluare risc, decizie, KYC, RTN, RTS — **dar nu o declarație de client** (BR / sursa fondurilor).
**Recomandare:** `genereaza_declaratie_client(...)` (BR + sursa fondurilor) ca al 7-lea generator + endpoint `/api/aml/declaratie-client.docx`.

#### G7 🟡 — Actualizare/revizuire anuală: termen calculat dar fără reminder/flux **[important]**
**Cerință:** Planul (I.2) cere **actualizarea anuală** a datelor pentru clienții pe termen lung + imediat la schimbări semnificative (clientul devine PEP etc.); (II) cere **revizuirea anuală a normelor interne**.
**Cod:** `risc.data_reevaluare` calculează termenul (12/24/36 luni) și `documente` îl tipărește, dar **nu există** un mecanism de listare a dosarelor cu reevaluare scadentă, nici câmp de „dată revizuire norme interne" în generatorul de norme.
**Recomandare:** endpoint care listează dosarele AML cu `data_reevaluare <= azi` (scadente); câmp `data_revizuire` în antetul normelor interne.

#### G8 🟡 — Documentarea raționamentului de încadrare a riscului **[important]**
**Cerință (ghid, „Notă"):** evaluatorul **trebuie să documenteze raționamentul** pentru încadrarea într-un nivel de risc (mai ales când alege „mediu" în loc de „ridicat" în prezența unor factori); la măsuri simplificate, justificarea e obligatorie.
**Cod:** `EvaluareRisc.motive_sporit` documentează DOAR motivele de „sporit". Nu există câmp de **justificare liberă a evaluatorului** pentru „redus"/„standard" (de ce nu e mai sus) sau pentru aplicarea măsurilor simplificate.
**Recomandare:** câmp `justificare_incadrare: str` pe `EvaluareRisc`, tipărit în documentul de evaluare de risc; obligatoriu (sau avertizat) când se aplică măsuri simplificate.

#### G9 🟡 — Mențiunea AML în declarația de conformitate a raportului SEV **[important — punte AML↔SEV]**
**Cerință (ghid, „Corelare cu SEV 100"):** raportul ar trebui să menționeze la conformitate „...în conformitate cu standardele SEV și cu legislația aplicabilă (inclusiv Legea 129/2019)".
**Cod:** declarația SEV 100 din `report/generator.py:261-265` nu include trimiterea la Legea 129/2019.
**Recomandare:** o frază în declarația de conformitate (profil garantare) — punte minimă între modulul AML și generatorul de raport.

#### G10 🟡 — Sector de activitate / industrie sensibilă a clientului — necolectat **[minor→important]**
**Cerință (ghid, cap. 1):** clienții din sectoare sensibile (imobiliare, schimb valutar/crypto, jocuri de noroc, metale prețioase, construcții, arme) → prudență sporită; Planul (IV) menționează „industrii sensibile precum jocuri de noroc, crypto" ca factor de risc.
**Cod:** `PersoanaFizica.ocupatie` și `ClientPJ` nu au câmp de „sector/industrie cu risc"; nu intră în scoring.
**Recomandare:** câmp opțional `sector_risc: bool`/listă în `Semnale` care ridică factorul client.

#### G11 🟡 — Geografie: țara clientului ≠ amplasarea bunului, și PEP-screening pe BR **[minor]**
**Cerință (ghid, cap. 4):** trebuie evaluate **separat** țara de rezidență a clientului/BR ȘI amplasarea bunului; non-SEE și paradisuri fiscale = risc chiar dacă nu pe lista neagră.
**Cod:** `Semnale` are doar `tara_risc_inalt`/`tara_risc_redus` (un singur set boolean). `liste.este_tara_risc` verifică o țară, dar serviciul nu rulează screening de țară automat pe rezidența clientului vs. amplasarea bunului, nici nu distinge non-SEE/paradis fiscal de listă neagră.
**Recomandare:** câmpuri distincte `tara_client`/`tara_bun` + integrare `este_tara_risc` în `serviciu.evalueaza_relatie`; categorie „paradis fiscal/non-SEE" ca risc mediu.

#### G12 🟡 — Listele de sancțiuni/PEP: fără date încărcate + fără dată de actualizare vizibilă **[minor, operațional]**
**Cerință:** Planul (I.5) menționează liste de sancțiuni transmise **lunar** de ANEVAR; screening-ul presupune liste actualizate.
**Cod:** `liste.incarca_liste` citește `aml/data/liste.json`; dacă lipsește → liste GOALE (screening returnează 0 fără avertisment). `Liste.actualizat` există dar nu e expus în răspunsul de screening/UI.
**De ce contează (risc de fals negativ):** un evaluator poate crede că „a verificat" când de fapt listele sunt goale.
**Recomandare:** când listele sunt goale sau `actualizat` e vechi (> ~30 zile), `serviciu` să întoarcă un avertisment „liste neîncărcate/expirate — screening neconcludent, verificați manual"; expune `actualizat` în răspuns. (Disclaimerul din `documente._antet` spune deja „Aplicația NU efectuează verificări automate pe listele de sancțiuni/PEP" — de aliniat cu comportamentul real de screening tolerant.)

#### G13 🟡 — Refuzul lucrării / întreruperea relației nu e modelat **[minor]**
**Cerință (ghid, măsuri risc ridicat):** dacă riscul nu poate fi atenuat, evaluatorul are **dreptul/obligația de a refuza** lucrarea; la suspiciune fermă, întrerupe orice activitate care ar alerta clientul și întocmește RTS.
**Cod:** nu există un rezultat „recomandare: refuz/întrerupere" în `serviciu.evalueaza_relatie`, deși propune RTS.
**Recomandare:** când există indicatori gravi (sau sancțiuni), serviciul să întoarcă un flag `recomandare_refuz`/`recomandare_intrerupere` cu temeiul, fără a lua decizia automat (om-în-buclă).

---

## 4. Prioritizare

**🔴 Blocante (acoperire de risc incompletă față de checklist-ul de inspecție):**
1. **G1** — scopul/tipul evaluării ca factor de risc (fix domeniul garantare credit).
2. **G2** — EDD: sursa fondurilor + aprobare conducere PEP (cerința legală centrală la risc ridicat).

**🟠 Importante:**
3. G3 (BR lipsă → alertă), G5 (registru de lucrări exportabil), G6 (declarație client BR/sursă fonduri), G7 (reminder reevaluare + revizuire norme), G8 (justificare încadrare), G9 (mențiune AML în raportul SEV), G4 (indicatori suplimentari din ghid).

**🟡 Minore / operaționale:**
4. G10 (sector sensibil), G11 (geografie client vs. bun), G12 (liste goale → avertisment), G13 (recomandare refuz/întrerupere).

> **Notă de încredere:** codul AML e **corect** pe regulile HARD și praguri (verificat în `risc.py`, `constante.py`, `raportare.py`, `store.py`). Gap-urile sunt de **acoperire** (câmpuri/pași pe care documentele îi cer și pe care motorul nu îi colectează încă), nu de logică greșită. Singura contradicție rezolvabilă în favoarea app-ului: C1 (tabelul planului spune „transmitere la ONPCSB", dar corpul normativ spune „doar decizie internă" — app-ul a procedat corect).

**Documente-sursă:** `md files/converted/anexa-nr-1-plan-de-m-suri-aml-cft-modificat-prin-h-47-2026.txt`, `md files/converted/ghid-de-evaluare-a-riscurilor-sb-ft-pentru-evaluatorii-autoriza-i-anevar.txt`. **Cod:** `src/evaluare/aml/*`, `src/evaluare/web/routers/aml.py`, `src/evaluare/web/schemas.py`.
