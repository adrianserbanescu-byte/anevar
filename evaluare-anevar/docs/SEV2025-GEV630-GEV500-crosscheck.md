# SEV 2025 — GEV 630 / GEV 500 / SEV 104-ESG — checklist de conformitate raport vs. cod

> **Scop:** extinde cross-check-ul de conformitate SEV 2025 (după [GEV520-2025-crosscheck.md](GEV520-2025-crosscheck.md))
> pe alte 3 zone pe care aplicația le implementează, dar care nu erau acoperite:
> **(1) GEV 630 — Evaluarea bunurilor imobile** (abordarea prin venit: capitalizare directă + DCF, alocarea valorii),
> **(2) GEV 500 — Estimarea valorii impozabile a clădirilor** (profil `GEV_500` / secțiunea `raportare_financiara`),
> **(3) Anexa ESG de la SEV 104** (referită de GEV 520 §86–88; relevanță transversală în rapoarte).
>
> **Sursă:** `SEV 2025` (Standardele de evaluare a bunurilor, ed. 2025) — descărcat de pe
> [anevar.ro/images/_upload/sev-2025.pdf](https://www.anevar.ro/images/_upload/sev-2025.pdf)
> (fișier integral ~8,7 MB). Paragrafe citate: **GEV 630** p. 113–125 (§§ 59–116),
> **GEV 500** p. 99–105 (§§ 1–47), **SEV 104 Anexă A10** p. 51–52, **GEV 520 §86–88** p. 295–296.
> **În vigoare de la 1 iulie 2025** (Conferința Națională, hotărârea nr. 2/9 aprilie 2025).
>
> ⚠️ **Document de lucru (DRAFT).** Citatele au **diacriticele reconstruite** din extragerea PDF→text
> (pdftotext strică diacriticele); înainte de a fi tratate ca referință normativă, se confruntă cu PDF-ul
> oficial. **Decizia de conformitate revine evaluatorului autorizat / ANEVAR, nu aplicației** — aplicația
> nu poartă răspundere pentru conținutul rapoartelor generate.
>
> 📌 **Notă GEV 500 / Decizia 18.12.2025:** ANEVAR a înlocuit Anexele 3 și 4 ale GEV 500 prin Decizie
> (în vigoare 19.12.2025). **Codul aplicației NU citează formule din Anexa 3/4 a GEV 500** (verificat:
> niciun text „impozabil / BIF / Anexa 4 GEV 500" în `src/`), deci nu e expus la caducitatea formulelor —
> referința `Anexa 3` din `assembler.py` se referă la *anexa de scanuri a raportului generic*, nu la
> anexele GEV 500. **Safe.** (vezi §3.D)

---

## 1. Unde trăiesc cele 3 zone în cod

| Aspect | Fișier | Note |
|---|---|---|
| Profiluri (ce ghid / abordări) | [profil.py](../src/evaluare/profil.py) | `GEV_630`, `GEV_500`; `abordari_aplicabile` include `venit` |
| Registru secțiuni de raport | [report/sectiuni.py](../src/evaluare/report/sectiuni.py) | `abordare_venit`→`(GEV_630)`; `alocare_valoare`→`(GEV_520, GEV_630)`; `raportare_financiara`→`(GEV_500)` |
| Motor venit — capitalizare directă | [engine/venit.py:35](../src/evaluare/engine/venit.py) | `evalueaza_venit`: NOI = (VBP − neocupare − cheltuieli); valoare = NOI ÷ rată |
| Motor venit — DCF | [engine/venit.py:56](../src/evaluare/engine/venit.py) | `evalueaza_dcf`: Σ flux_t/(1+r)^t + reziduală/(1+r)^n |
| Text raport „Abordarea prin venit" | [report/generator.py:762–777](../src/evaluare/report/generator.py) | capitalizare directă + DCF; doar dacă `venit_result`/`dcf_valoare` sunt setate |
| Text raport „Alocarea valorii" | [report/generator.py:470–505](../src/evaluare/report/generator.py) | `_adauga_alocare`: proprietate − teren = construcții |
| Reconciliere (selecția valorii) | [engine/reconciliation.py](../src/evaluare/engine/reconciliation.py) | conține și mod **„ponderata"** (medie ponderată) — vezi contradicția #GEV630-7 / #GEV500-5 |
| Secțiune `raportare_financiara` (text) | — | **înregistrată în `sectiuni.py:20` dar FĂRĂ generator de text** în `generator.py` (vezi #GEV500-1) |
| ESG (text raport) | — | **inexistent** în `src/` (verificat: zero „ESG / certificat energetic / factori de mediu") |

> Notă structurală: secțiunea de risc/garantare (`_adauga_risc_garantie`) și checklistul rulează **doar pe
> `GEV_520`** (`generator.py:795`). Pe `GEV_630` și `GEV_500` raportul folosește aceeași schelă de 7 capitole
> + alocare, fără un bloc de text dedicat ghidului respectiv.

---

## 2A. GEV 630 — Evaluarea bunurilor imobile → acoperire în cod

Legendă: ✅ acoperit · ⚠️ parțial · ❌ lipsă/contradicție

### Abordarea prin venit (metodologie)

| # | Cerință GEV 630 (2025) | § | Cod | Stare |
|---|---|---|---|---|
| 630-1 | Metodele abordării prin venit sunt variații ale DCF; cele mai folosite: **DCF** și **capitalizarea directă** | §61 | `venit.py:35` (cap. directă) + `venit.py:56` (DCF) | ✅ ambele implementate |
| 630-2 | **Capitalizare directă** = venit anual așteptat ÷ rată adecvată (sau × multiplicator) | §65 | `evalueaza_venit` (valoare = NOI ÷ rată) | ✅ (varianta ÷ rată; multiplicatorul de venit nu e oferit) |
| 630-3 | **Corelarea tipului de venit cu rata** (net↔rată netă, brut↔rată brută) | §64 | `venit.py` — folosește NOI cu `rata_capitalizare`; **nicio validare** că rata e „netă" | ⚠️ corelarea e lăsată integral pe seama evaluatorului, fără gardă |
| 630-4 | Evaluarea se face **de regulă cu venitul net din exploatare (NOI)**; alt tip de venit → se argumentează în raport | §66 | `DateVenit`/`RezultatVenit` calculează explicit NOI = VBP − pierderi − cheltuieli | ✅ (NOI e singura formă suportată — conform „de regulă") |
| 630-5 | **VBP → VBE → NOI**: VBP la 100% ocupare; VBE = VBP − neocupare/neîncasare; NOI = VBE − cheltuieli proprietar (nerecuperabile) | §67–70 | `venit.py:39–41` (pierdere=VBP×grad_neocupare; NOI=venit_efectiv−cheltuieli) | ✅ lanțul VBP→VBE→NOI e corect modelat |
| 630-6 | NOI **nu** scade: impozit pe venitul proprietarului, serviciul datoriei, amortizarea contabilă | §70 | nu există câmpuri pentru acestea în `DateVenit` (deci nu se scad) | ✅ implicit conform (nu sunt incluse în model) |
| 630-7 | **DCF**: valoare prezentă = previziuni venituri/cheltuieli + **valoare terminală**, actualizate | §63 | `evalueaza_dcf` (Σ fluxuri + `valoare_reziduala`) | ✅ structura DCF + reziduală e corectă |
| 630-8 | Toți indicatorii (chiria de piață, rata de neocupare, cheltuieli, **rata de capitalizare/actualizare**) trebuie **argumentați** în raport: surse + verificare + mod de calcul | §71 | textul raportului afișează *valorile* (generator.py:766–770) dar **nu cere/afișează sursele și argumentarea** ratei | ⚠️ **gol de raportare**: ratele apar fără secțiune de argumentare a surselor |

### Concluzia asupra valorii & raportare

| # | Cerință GEV 630 (2025) | § | Cod | Stare |
|---|---|---|---|---|
| 630-9 | **Interzis** stabilirea valorii prin **media aritmetică sau ponderată** a două/mai multe valori din abordări diferite | §107 | `reconciliation.py` are mod **„ponderata"**: `market_value*pondere + cost_value*(1−pondere)` (L61–64) și medie ponderată multi-abordare (L100–104) | ❌ **CONTRADICȚIE** — vezi §3.A |
| 630-10 | Nu se aplică o **a doua abordare doar formal** când o singură abordare e adecvată și bazată pe date suficiente | §108 | reconcilierea selectează abordarea disponibilă; nu forțează a doua | ✅ (nu impune a doua abordare) |
| 630-11 | Raționamentul de selecție a rezultatului final trebuie **prezentat în raport** (importanța diferită a metodelor) | §104–106 | cap. 7 „Reconciliere" e narativ (AI/manual), `generator.py:782–787` | ⚠️ depinde de naratorul AI / completare manuală; nu e impus structural |
| 630-12 | Diferența ≤ 20% între evaluări cu aceiași termeni nu e *a priori* neconformitate; > 20% cere argumentare | §109 | verificarea cost↔alocare la prag **20%** (`generator.py:497`) e singura gardă similară | ⚠️ pragul 20% e folosit doar la consistența cost-piață, nu ca regulă generală de raportare |
| 630-13 | Conținut raport conform **SEV 106**; + precizări: identificare proprietate, tip+premisa valorii, documentare/inspecție, **ipoteze și ipoteze speciale într-o secțiune distinctă** | §110–111 | schela de 7 capitole + termeni de referință acoperă SEV 106 (vezi crosscheck SEV 106) | ⚠️ „ipoteze speciale într-o secțiune distinctă" — de confirmat că există secțiune dedicată, nu doar inline |
| 630-14 | Rezultatul poate fi o **valoare** (rotunjită) **sau un interval** când există factori de risc semnificativi | §112 | `valoare_finala` e mereu o singură valoare (Decimal); intervalul nu e suportat | ⚠️ intervalul de valori nu e modelat |

### Alocarea valorii (particularități, §113–116)

| # | Cerință GEV 630 (2025) | § | Cod | Stare |
|---|---|---|---|---|
| 630-15 | La raportare financiară (alocare), valoarea de piață a proprietății se **alocă pe teren + construcție** → valori juste ale componentelor | §113–114 | `_adauga_alocare`: construcții = proprietate − teren (`generator.py:483, 490`) | ✅ mecanismul de alocare există |
| 630-16 | Alocarea: una dintre modalități = **deducerea valorii de piață a terenului** din valoarea proprietății → valoarea construcției | §116 a) | `generator.py:166–167` (`valoare_finala − alocare_constructii`) + text L490–492 | ✅ (metoda „proprietate − teren") |
| 630-17 | Procesul de alocare are la bază **raționamentul evaluatorului** și trebuie **argumentat** în raport | §115 | textul afirmă metoda dar nu solicită argumentarea raționamentului | ⚠️ argumentarea alocării nu e cerută explicit |

---

## 2B. GEV 500 — Estimarea valorii impozabile a clădirilor → acoperire în cod

> ⚠️ **Avertisment de mapare profil (vezi și obs. 2689 din memorie):** în [profil.py](../src/evaluare/profil.py)
> profilul **`RAPORTARE_FINANCIARA`** este mapat pe **`ghid="GEV_500"`** (L54–57), iar profilul
> **`IMPOZITARE`** este mapat pe **`ghid="GEV_630"`** (L62–65). **Aceasta este o inversiune:** GEV 500 este
> ghidul de **impozitare** (valoare impozabilă a clădirilor), NU de raportare financiară. Tabelul de mai jos
> verifică cerințele *reale* ale GEV 500 (impozitare) față de ce face profilul `GEV_500` din cod.

| # | Cerință GEV 500 (2025) | § | Cod | Stare |
|---|---|---|---|---|
| 500-1 | Există un **ghid de impozitare** dedicat, cu raport care respectă **„Cuprins"-ul din Anexa 4** și capitole specifice impozitării | §38, §41 | profil `GEV_500` există, dar secțiunea `raportare_financiara` din `sectiuni.py:20` **nu are generator de text** în `generator.py` | ❌ **secțiune înregistrată dar goală** — vezi §3.B |
| 500-2 | Valoarea impozabilă **se referă doar la construcții**, nu la teren | §2 | nimic în cod nu restrânge la construcții pe profil `GEV_500`; modelul evaluează proprietatea integral | ⚠️ neacoperit (modelul nu izolează construcția ca rezultat final pe impozitare) |
| 500-3 | Valoarea impozabilă **nu este** valoare de piață/justă și **nu se înregistrează în situațiile financiare** | §4–6 | profil `GEV_500` are `tip_valoare="justa"` (via `RAPORTARE_FINANCIARA`) | ❌ **contradicție de tip valoare** (vezi #500-mapare): impozabilul ≠ justă |
| 500-4 | Abordări aplicabile: **cost pentru valoarea impozabilă**, venit, piață; **abordarea prin cost e obligatorie** dacă se aplică una singură; valoarea impozabilă **nu include TVA** | §13–14 | profil `RAPORTARE_FINANCIARA→GEV_500` are `["venit","comparatie","cost"]`; fără regula „cost obligatoriu la o singură abordare" | ⚠️ abordările există, dar regula de obligativitate a costului nu e implementată |
| 500-5 | Selecția rezultatului: **interzisă media aritmetică/ponderată**; regula 35 (cea mai mică valoare / prag 10%) | §34–35 | `reconciliation.py` mod „ponderata" (medie ponderată) + **nicio implementare a regulii §35** | ❌ **CONTRADICȚIE + gol** — vezi §3.A |
| 500-6 | Alocarea valorii pe teren/construcție prin **deducerea valorii terenului estimat la CMBU** | §31–33 | `_adauga_alocare` deduce terenul, dar prin „comparație directă", **nu** explicit „pentru CMBU" (`generator.py:491`) | ⚠️ alocarea există; baza „CMBU a terenului" nu e explicitată |
| 500-7 | Abordarea prin cost pentru impozitare: cost de nou − depreciere fizică/funcțională; **fără depreciere economică/externă**; **fără profitul dezvoltatorului și fără costuri de finanțare** | §15, §23 | motorul de cost (`engine/cost.py`) e generic; nu există variantă „valoare impozabilă" care să excludă deprecierea externă | ⚠️ neacoperit pe profil `GEV_500` (cost generic, nu „cost pentru valoare impozabilă") |
| 500-8 | Raportul pentru impozitare e final **doar cu recipisa BIF** (Baza de Informații Fiscale) | §39 | **zero** referință la **BIF** în cod (verificat); doar **BIG** (garantare) e menționat, și acela doar pe `GEV_520` | ❌ **gol** — BIF nu e modelat |
| 500-9 | Data emiterii ≥ 1 ianuarie a anului următor datei evaluării | §42 | nicio validare de dată specifică impozitării | ❌ lipsă |
| 500-10 | Diferența ≤ 20% nu e *a priori* neconformitate | §46 | ca la 630-12 | ⚠️ idem |

> 📌 **Despre Decizia 18.12.2025 (Anexele 3 și 4 GEV 500):** întrebarea era dacă app-ul **citează formule
> din Anexa 4**. **Răspuns: NU.** Căutarea în `src/` nu găsește niciun text de tip formulă impozitare,
> rang localitate, coeficient 1,4 (§36) sau „Anexa 4 GEV 500". App-ul nu reproduce conținutul anexelor, deci
> **nu e afectat de înlocuirea Anexelor 3/4**. Singura referință „Anexa 3/4" din cod
> ([assembler.py:99](../src/evaluare/assembler.py)) e despre *atașarea scanurilor CF în anexa raportului
> generic*, fără legătură cu GEV 500. **Safe — confirmat.**

---

## 2C. SEV 104 — Anexa ESG (factori de mediu, sociali și de guvernanță) → acoperire în cod

> GEV 520 §86 trimite la **Anexa ESG de la SEV 104**; §87–88 detaliază riscurile fizice și certificatul
> energetic. Anexa SEV 104 A10 (p. 51–52) enumeră factorii E/S/G și regula de luare în considerare.

| # | Cerință SEV 104-ESG / GEV 520 §86–88 | § | Cod | Stare |
|---|---|---|---|---|
| ESG-1 | Impactul factorilor ESG semnificativi **trebuie luat în considerare** în estimarea valorii (calitativ și cantitativ) | SEV 104 A10.1–A10.2 | **inexistent** în `src/` | ❌ lipsă completă |
| ESG-2 | Factorii **de mediu** (poluare, biodiversitate, schimbări climatice — riscuri curente și viitoare, dezastre naturale, eficiență energetică…) | A10.3 | — | ❌ lipsă |
| ESG-3 | Factorii **sociali** (relații cu comunitatea, sănătate, drepturile omului, condiții de muncă…) | A10.4 | — | ❌ lipsă (relevanță redusă la imobiliar rezidențial, dar normativ aplicabil) |
| ESG-4 | Factorii **de guvernanță** (în special pentru PGA / comercial) | A10.5 | — | ❌ lipsă |
| ESG-5 | Factorii ESG se iau în considerare **în măsura în care sunt măsurabili** și considerați rezonabili de un evaluator care aplică raționamentul profesional | A10.6 | — | ❌ lipsă |
| ESG-6 | **Riscuri fizice — disclaimer de competență:** calitatea de evaluator autorizat **nu oferă competență** de apreciere/cuantificare/ierarhizare a gravității riscurilor fizice | GEV 520 §87 a) | — | ❌ lipsă (disclaimerul de competență ar trebui în raport) |
| ESG-7 | Dacă creditorul **furnizează date** privind riscuri fizice și piața permite → evaluatorul poate analiza/cuantifica; altfel **menționează că nu le poate cuantifica** (raportul rămâne conform) | §87 b–c | — | ❌ lipsă |
| ESG-8 | Evaluatorul poate **informa creditorul** asupra unor evidențe din inspecție, cu rezerva că **nu e o opinie calificată** | §87 d) | — | ❌ lipsă |
| ESG-9 | **Certificatul energetic** (CPE / clădire verde): dacă e furnizat, evaluatorul analizează/cuantifică sau menționează lipsa evidențelor de piață (raportul rămâne conform) | §88 | — | ❌ lipsă (vezi și crosscheck GEV 520 #26) |

> Aceasta confirmă și extinde golul ESG semnalat în [GEV520-2025-crosscheck.md](GEV520-2025-crosscheck.md) (#24–26):
> ESG e o **novație 2025 obligatorie transversal** și lipsește complet din generatorul de raport, pe toate profilurile.

---

## 3. Concluzie — diferențe care contează (priorizate)

### A. 🔴 Conflict real (de reparat) — media ponderată a abordărilor

**#630-9 / #500-5 — Reconcilierea prin medie ponderată.**
`engine/reconciliation.py` (L61–64 și L100–104) poate stabili valoarea finală ca **medie ponderată** a
valorilor din abordări diferite (`market_value*pondere_piata + cost_value*pondere_cost`), marcată
`metoda_selectata="ponderata"`. Atât **GEV 630 §107** cât și **GEV 500 §34** interzic explicit
*„stabilirea valorii … prin aplicarea mediei aritmetice sau a mediei ponderate a două sau mai multe valori
obținute din aplicarea unor abordări … diferite"*. Pe un raport real, dacă se selectează modul „ponderata"
pe două abordări, **valoarea concluzionată ar fi neconformă** cu ghidurile. → de eliminat/blocat media
ponderată ca metodă de **concluzie** (rămâne acceptabilă doar ca analiză internă, nu ca valoare finală),
sau de restrâns la cazul excepției legale (§34: „cu excepția cazurilor în care reglementările legale impun").

### B. 🟠 Goluri normative (lipsesc complet)

- **#500-1 — Secțiunea `raportare_financiara` (`GEV_500`) este înregistrată în `sectiuni.py:20` dar NU are
  generator de text** în `generator.py` (cum are `gev_520`). Pe profil `GEV_500`, raportul iese fără bloc
  dedicat impozitării (capitole Anexa 4, recipisă BIF §39, regula §35).
- **#ESG-1…ESG-9 — ESG inexistent** în tot `src/`: niciun text pentru factori de mediu/sociali/guvernanță,
  disclaimerul de competență pe riscuri fizice (§87) sau tratarea certificatului energetic (§88). Novație 2025
  obligatorie, transversală pe toate profilurile.
- **#500-8 / #500-9 — BIF + data ≥ 1 ian:** recipisa BIF (Baza de Informații Fiscale, §39) și constrângerea
  de dată a emiterii (§42) nu există în cod (cod-ul cunoaște doar **BIG**, pe garantare).

### C. 🟠 Inversiune de mapare profil↔ghid (de clarificat cu evaluatorul)

- **`profil.py` L54–65:** `RAPORTARE_FINANCIARA → GEV_500` și `IMPOZITARE → GEV_630`. **GEV 500 este ghidul
  de impozitare**, nu de raportare financiară; raportarea financiară se sprijină pe GEV 630/SEV 230 + IVS.
  În plus `RAPORTARE_FINANCIARA` are `tip_valoare="justa"`, dar GEV 500 reglementează **valoarea impozabilă**
  (§4–6: *nu* e valoare justă). Maparea pare inversată/etichetată greșit. (Confirmă obs. memorie 2689.)

### D. 🟡 Întăriri (parțial acoperite)

- **#630-8** argumentarea surselor ratei de capitalizare/actualizare în raport (acum doar valori, fără surse);
- **#630-3** corelarea net↔rată netă (fără gardă în motor); **#630-14** rezultat ca interval de valori;
- **#500-2 / #500-7** izolarea construcției + „cost pentru valoare impozabilă" (fără depreciere externă, fără
  profit dezvoltator) pe profil `GEV_500`; **#500-6** alocarea explicit „pe CMBU a terenului";
- **#630-17** argumentarea raționamentului de alocare; **#630-11** raționamentul de reconciliere impus structural.

### E. ✅ Solid (matchuri exacte cu ghidul)

- **Motorul de venit** (#630-1…630-7): capitalizare directă cu lanțul **VBP→VBE→NOI** corect (§67–70),
  DCF cu valoare reziduală (§63), NOI fără serviciul datoriei/amortizare (§70) — toate conforme.
- **Alocarea valorii** prin „proprietate − teren" (#630-15, 630-16; §113–116).
- **GEV 500 / Anexa 4 — formule:** app-ul **nu** citează formule din anexele GEV 500, deci e **imun** la
  înlocuirea Anexelor 3/4 prin Decizia 18.12.2025 (#500 nota D).

---

## 4. Modificări concrete propuse în cod (pentru sesiunea de fix, nu aici)

1. **`engine/reconciliation.py` — blochează media ponderată ca *valoare de concluzie*** (#630-9/#500-5):
   pe `GEV_630`/`GEV_500`, modul „ponderata" să nu producă `valoare_finala`; obligă selecția unei singure
   valori (cu raționament), conform §107/§34. Excepție legală explicită doar unde e impusă (§34 final).
2. **`generator.py` — adaugă generator de text pentru `raportare_financiara`/`GEV_500`** (#500-1): bloc cu
   capitolele Anexa 4, mențiunea recipisei **BIF** (#500-8), regula de selecție §35, restrângerea la construcții (#500-2).
3. **`generator.py` — secțiune ESG transversală** (#ESG-1…9): factori E/S/G (SEV 104 A10), disclaimerul de
   competență pe riscuri fizice (§87 a–d) și tratarea certificatului energetic (§88). Aplicabilă pe toate profilurile.
4. **`profil.py` — corectează/etichetează maparea profil↔ghid** (#C): clarifică `RAPORTARE_FINANCIARA` vs
   `IMPOZITARE` față de GEV 500 (impozitare) și `tip_valoare` (impozabilă ≠ justă).
5. **`generator.py:762–777` — adaugă argumentarea surselor** pentru rata de capitalizare/actualizare (§71, #630-8)
   și a raționamentului de alocare (§115, #630-17).
6. **Teste:** caz `GEV_630` cu două abordări care asertează că NU se produce o valoare ponderată; caz `GEV_500`
   care asertează prezența blocului impozitare + BIF; caz ESG pe `GEV_520`.

> Toate textele rămân *draft generat de aplicație*; **evaluatorul autorizat validează și își asumă conținutul**
> (conform disclaimerului existent în rapoarte). Aplicația nu poartă răspundere normativă.
