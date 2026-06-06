# A — Conformitate cadru general + raportare (SEV 100 / 101 / 102 / 106)

> **Audit de conformitate** al aplicației (cod livrat) + planurilor viitoare față de
> **SEV 2025** (ediția 15 apr. 2025, în vigoare 1 iul. 2025, HCN 2/2025).
> Domeniu: **CADRUL GENERAL** (SEV 100), **TERMENII DE REFERINȚĂ** (SEV 101),
> **TIPURILE VALORII** (SEV 102) și **DOCUMENTARE + RAPORTARE** (SEV 106, în special
> cele 18 cerințe minime ale raportului §30.6 (a)–(r)).
> Aplicația **asistă** un evaluator autorizat ANEVAR; ea NU semnează raportul — multe
> cerințe sunt „acoperite de un câmp/secțiune-șablon" pe care evaluatorul îl completează/asumă.
>
> Standard sursă: `C:\Users\adyse\anevar\md files\standardele-de-evaluare-a-bunurilor-2025.md`.
> Cod sursă auditat: `evaluare-anevar/src/evaluare/report/{generator,sectiuni,anonymizer}.py`,
> `models/{meta,report_context}.py`, `assembler.py`, `profil.py`.
> Legendă status: ✅ implementat · 🟡 parțial · ❌ lipsă · 📋 planificat.
> Bucket: **A** = îl pot face eu (cod) · **B** = ține de evaluator (date/raționament) · **C** = jurist.
> Data auditului: 2026-06-06.

---

## 1. SEV 106 §30.6 — cele 18 cerințe minime ale raportului (a)–(r)

| # | Cerință (SEV ref) | Status | Unde (fișier/doc) | Gap + recomandare | Bucket |
|---|---|---|---|---|---|
| a | **Termenii de referință conveniți** (106 §30.6 a; 101 §20.1, l.558-625) | ✅ | `generator.py:213-289` `_termeni_referinta` — secțiune dedicată cu client, scop, tip valoare, monedă/curs, date, identificare, premise, evaluator, natură/amploare, surse, ESG, specialist, restricții | „Conveniți **în scris** între client și evaluator înainte de finalizare" (101 §20.2, l.626) NU e materializat: nu există contract/comandă semnată generată de app. Recomandare: șablon de **scrisoare de acceptare / contract** (poate fi în tab Documente). | A (șablon) + B (semnătura părților) |
| b | **Activele/datoriile supuse evaluării** (106 §30.6 b; l.2551) | ✅ | `_coperta` `generator.py:128-130`, `_termeni_referinta:232-235`, cap. 4 `:609-633` (teren, construcție, apartament, agricol, industrial); `meta.adresa/numar_cadastral/carte_funciara` | Identificarea cadastrală provine din câmpuri introduse de evaluator (corect). Notele demo marchează cadastral/CF ca PLACEHOLDER — de eliminat în producție. | B |
| c | **Identitatea evaluatorului** (106 §30.6 c; 101 §20.1 e, l.574) | ✅ | `meta.evaluator_nume`, `evaluator_legitimatie`; apare în copertă, scrisoare, termeni (`:262-265`), declarație, semnătură (`:545-554`) | Acoperit. Lipsește numai firma/PFA și nr. autorizație ANEVAR distinct de legitimație (opțional). | B |
| d | **Clientul** (106 §30.6 d; 101 §20.1 b, l.566) | ✅ | `meta.client_nume`, `client_tip`; copertă, termeni `:217`, cap. 1 `:580` | Acoperit (intern/extern nu e modelat explicit, dar `client_tip` acoperă persoană fizică/juridică). | B |
| e | **Utilizarea desemnată** (106 §30.6 e; 101 §20.1 c, l.570) | ✅ | `meta.scop`; copertă, scrisoare, termeni `:220`, cap. 1 | Acoperit. `scop` e text liber cu implicit „Garantarea creditului ipotecar". | B |
| f | **Utilizatorii desemnați** (106 §30.6 f; 101 §20.1 d, l.572) | 🟡 | `meta.beneficiar` (banca/finanțator); termeni `:218-219`; GEV 520 „utilizatorul desemnat = creditorul" `:251-253` | `beneficiar` e opțional (`""`). Dacă lipsește, raportul NU enunță explicit utilizatorul desemnat și restricția. La garantare ar trebui **obligatoriu**. Recomandare: validare „beneficiar obligatoriu la scop=garantare". | A (validare) + B |
| g | **Moneda(ele) evaluării** (106 §30.6 g; 101 §20.1 f, l.581) | ✅ | `meta.moneda` + `curs_valutar`; termeni `:222-225`, copertă echiv. LEI `:101-107` | Acoperit, cu echivalent LEI la curs BNR. Decizie deschisă (plan B7): implicit EUR la garantare în loc de LEI. | A (implicit) + B |
| h | **Data(ele) evaluării** (106 §30.6 h; 101 §20.1 g, l.584) | ✅ | `meta.data_evaluarii`, `data_raportului`, `data_inspectiei`, `valabilitate`; termeni `:226-231` | Acoperit, inclusiv distincția dată evaluare ≠ dată raport (cerută la l.584-586 și 30.6 r). | B |
| i | **Tipul(urile) valorii utilizat(e)** (106 §30.6 i; 101 §20.1 h, l.587; 102 §20.4, l.753) | 🟡 | `meta.tip_valoare` (implicit „Valoarea de piață (SEV 102)"); termeni `:221`, cap. 1 `:586`; mapare scop→tip valoare în `dosar.html:257` | **Gap cheie:** tipul valorii e enunțat, dar **sursa definiției NU e citată/explicată** în corpul raportului. 101 §20.1(h) și 102 §20.4 (l.754-755) cer „sursa definiției ... trebuie citată sau acesta trebuie explicat". Definiția valorii de piață (SEV 102 A10) nu apare. Recomandare: paragraf-șablon cu **definiția + sursa** pe tip valoare. | A |
| j | **Abordarea/abordările în evaluare** (106 §30.6 j; l.2562) | ✅ | cap. 6 `:642-648` (referă SEV 103/105); `profil.abordari_aplicabile`; secțiuni cost/comparație/venit `sectiuni.py:14-16` | Acoperit. Abordările aplicabile vin din profil; reconcilierea (cap. 7) justifică selecția. | A/B |
| k | **Metoda(ele)/modelul(ele) de evaluare** (106 §30.6 k; l.2563) | ✅ | cap. 6 grile/tabele `generator.py:295-378` (comparație, teren, cost segregat, venit/capitalizare `:652-664`, DCF `:665-667`) | Acoperit cu tabele de calcul reale. | A/B |
| l | **Sursele + modul de selectare a datelor semnificative** (106 §30.6 l; 101 §20.1 j, l.598) | 🟡 | termeni `:271-275`; nota comparabile `:319-323`; Anexa 1 surse `:508-514` | Surse enunțate generic + linkuri comparabile în anexă. Lipsește descrierea **modului de selectare** (de ce aceste comparabile, criterii de respingere) ca text structurat — acum e doar listă de linkuri + frază-șablon. Recomandare: secțiune „criterii de selecție" (poate fi AI + editată). | A (schelet) + B (raționament) |
| m | **Date ESG semnificative (mediu, social, guvernanță)** (106 §30.6 m; 101 §20.1 m, l.609) | 🟡 | termeni `:276-280` — paragraf-șablon ESG fix (menționează certificat energetic) | **Text identic indiferent de input** — nu reflectă date ESG reale ale proprietății (nu există câmp pentru clasa energetică, riscuri de mediu/inundații etc.). Conform ca declarație minimă, dar nu „datele de intrare ESG utilizate **și luate în considerare**". Recomandare: câmp clasă energetică + flag risc + text condiționat. | A (câmpuri) + B |
| n | **Ipoteze semnificative/speciale + condiții limitative** (106 §30.6 n; 102 §50-60, l.807-856) | ✅ | cap. 2 `:595-600`; premise în termeni `:236-245`; ipoteze speciale GEV 520 `:254-260`; vânzare forțată/lichidare `:450-463` | Acoperit (text AI + șabloane). Ipoteza specială de „vânzare forțată" e tratată cu factor orientativ + avertisment. Bun. De asigurat că ipotezele speciale concrete sunt marcate distinct (102 §60.1). | A/B |
| o | **Constatările unui specialist/furnizor extern** (106 §30.6 o; 100 §30, l.460-481) | 🟡 | termeni `:281-284` — „nu a fost cazul utilizării unui specialist" (fix) | Text **hardcodat „nu a fost cazul"**. Dacă în realitate se folosește un expert (geotehnic, structurist), raportul ar declara fals. 100 §30.1-30.3 cer prezentarea procesului/constatărilor + evaluarea competenței. Recomandare: flag „s-a folosit specialist?" + câmpuri (nume, domeniu, constatări). | A (câmpuri) + B |
| p | **Valoarea + raționamentul evaluării** (106 §30.6 p; l.2570) | ✅ | valoare în copertă/scrisoare/cap.1/cap.7 `:672-681`; reconciliere `:672-677`; motorul de calcul (determinist) | Valoarea = calcul determinist; raționamentul de reconciliere e text (AI/șablon) editabil. Acoperit. | A/B |
| q | **Declarația de conformitate cu SEV** (106 §30.6 q; 100 §10.3/§40, l.423-426; 106 §30.8, l.2576) | ✅ | `_declaratie_conformitate` `generator.py:192-210`; scrisoare `:164-172`; clauză ghid GEV `:179-189` | Acoperit explicit (SEV 2025 + ghid GEV per profil). **Atenție §30.8** (l.2576): dacă o limitare afectează conformitatea, NU se afirmă conformitatea — app afirmă **necondiționat** conformitatea, fără verificare a limitărilor (ex. comparabile <3, ESG lipsă). Recomandare: condiționează declarația de trecerea validărilor (vezi golul #2 din Top 5). | A |
| r | **Data raportului** (poate diferi de data evaluării) (106 §30.6 r; l.2572) | ✅ | `meta.data_raportului`; copertă, termeni, cap. 1, semnătură | Acoperit, distinct de data evaluării. | B |

---

## 2. SEV 100 — Cadrul general (principii, verificarea calității, specialist, conformitate)

| Cerință (SEV ref) | Status | Unde (fișier/doc) | Gap + recomandare | Bucket |
|---|---|---|---|---|
| **Principiile evaluatorului — etică, competență, obiectivitate** (100 §10.1-10.2, l.415-422) | ✅ | declarație `:199-207` (fără interes, onorariu necondiționat, competență, asigurare RC); GEV 520 independență `:251-253` | Acoperit ca declarații. Etica e a evaluatorului (persoană), app doar o materializează. | B |
| **Conformitatea declarată cu standardele SEV** (100 §10.3, l.423-426) | ✅ | declarație + scrisoare (SEV 2025, HCN 2/2025) | Acoperit. | A |
| **Scepticism profesional** (100 §10.4, l.432-434) | 🟡 | implicit în motorul de validări (`engine/validation.py`) + verificarea de consistență cost↔piață `:407-419` + fixurile de import (refuz pagină-listă) | Nu apare ca **declarație** în raport; e doar comportament intern. Acceptabil (scepticismul e al omului), dar verificarea de consistență e un plus util de evidențiat. | A/B |
| **Procedura de verificare a calității procesului** (100 §20, l.435-459) | 🟡 | checklist GEV 520 `:465-488`; verificare consistență `:407-419`; tab Audit (planificat, `9-topicuri-decizie.md` Topic 6) | §20.5 cere **documentarea** procedurilor de verificare. Checklist-ul e neînregistrat (☐ needifuzat). Recomandare: persistă bifele + traseul de audit (urma de calcul inline — planificat). | A |
| **Utilizarea unui specialist — evaluarea competenței + prezentare** (100 §30, l.460-481) | 🟡 | termeni `:281-284` (negație fixă) | Vezi §30.6(o). Lipsesc câmpuri pentru specialist. | A + B |
| **Devieri / cerințe legale care au prioritate asupra SEV** (100 §40.4-40.6, l.491-503) | ❌ | — | Nu există mecanism de a declara devieri sau cerințe legale care prevalează (ex. cerință de creditor). Rar la garantare standard, dar absent. Recomandare: câmp opțional „devieri/cerințe legale". | A (câmp) + C (conținut) |
| **Documentarea ediției SEV (date retrospective)** (100 §50.2, l.523-527) | 🟡 | declarație fixează „ediția 2025" | Pentru evaluări cu **dată retrospectivă** ar trebui ediția SEV aplicabilă la acea dată — app presupune mereu 2025. Recomandare: derivă ediția din `data_evaluarii`. | A |

---

## 3. SEV 101 — Termeni de referință (elemente care nu sunt deja în §30.6)

| Cerință (SEV ref) | Status | Unde | Gap + recomandare | Bucket |
|---|---|---|---|---|
| **Natura și amploarea activităților + limitări** (101 §20.1 i, l.590-597) | ✅ | termeni `:266-270` (fără investigații distructive/geotehnice/juridice) | Acoperit ca șablon. | A/B |
| **Restricții de utilizare/difuzare/publicare** (101 §20.1 o, l.616) | ✅ | termeni `:285-289`; scrisoare „exclusiv în scopul menționat" | Acoperit. | A |
| **Tipul raportului / model de document livrat** (101 §20.1 n, l.612) | ✅ | termeni `:285-289` (raport scris narativ) | Acoperit. | A |
| **Acord scris pe termenii de referință înainte de finalizare** (101 §20.2-20.3, l.626-632) | ❌ | — | Nu se generează/păstrează un acord scris client-evaluator. Recomandare: șablon comandă/contract + bifă „termeni conveniți". (Vezi §30.6 a.) | A (șablon) + C (clauze) + B |
| **Tip valoare adecvat utilizării desemnate** (101 §20.1 h + 102 §10.1, l.587, l.700-704) | ✅ | mapare scop→tip valoare `dosar.html:257`; `PROFIL_DUPA_SCOP` `assembler.py:53-58` | Adecvarea e automată per scop (garantare→piață, raportare→justă, asigurare→asigurare). Bun. Doar **sursa definiției** lipsește (§30.6 i). | A |

---

## 4. SEV 102 — Tipuri ale valorii + premise + cea mai bună utilizare

| Cerință (SEV ref) | Status | Unde | Gap + recomandare | Bucket |
|---|---|---|---|---|
| **Selectarea tipului valorii adecvat** (102 §10.1, §20.4, l.700-704, l.753) | ✅ | `profil.tip_valoare` (piata/investitie/justa/lichidare/asigurare/chirie) `profil.py:12`; mapare per scop | Modelul suportă tipurile SEV. Acoperit la nivel de selecție. | A/B |
| **Citarea/explicarea sursei definiției tipului valorii** (102 §20.4, l.754-755; A10-A80) | ❌ | doar eticheta „Valoarea de piață (SEV 102)" | **Gol material** (vezi §30.6 i). Definiția + cadrul conceptual (A10.2, l.886-962) nu sunt redate. Recomandare: bibliotecă de definiții pe tip valoare, inserate automat în termeni. | A |
| **Cea mai bună utilizare (CMBU) — fizic posibil / legal permis / fezabil financiar** (102 A90, l.1124-1154; valoare de piață reflectă CMBU A10.4 l.970) | 🟡 | cap. 5 CMBU `:635-640` (text AI sau „de completat") | Secțiune există, dar conținutul e **AI generic sau placeholder**, fără cele 3 teste structurate (fizic/legal/financiar) și fără referință la urbanism/zonare (A90.6 b). Recomandare: schelet cu cele 3 criterii + câmp zonare. | A (schelet) + B (concluzie) |
| **Premisa valorii (utilizare continuă / lichidare / vânzare forțată/ordonată)** (102 §10.3, A100-A120, l.708-716, l.1155-1213) | ✅ | premisă „utilizare continuă" în termeni `:236-245`; vânzare forțată/lichidare GEV 520 `:450-463` | Acoperit. Premisa de bază + lichidare (factor) la garantare. La vânzare forțată — motivele constrângerii (A120.2, l.1185) ar trebui explicite ca ipoteză specială. | A/B |
| **Ipoteze rezonabile/argumentate prin date de piață** (102 §50.4, §60.2, l.830-833, l.853-856) | 🟡 | ipoteze cap. 2 (AI/șablon) | Ipotezele sunt redate; „argumentarea prin date de piață" depinde de evaluator. App nu forțează legarea ipotezei de o sursă. | B |
| **Factori specifici entității / sinergie excluse din valoarea de piață** (102 §30, §40, l.761-806) | 🟡 | definiția valorii de piață nu e redată (vezi mai sus) | Relevanță redusă la casă+teren garantare (fără sinergie). Acoperit implicit prin tip valoare = piață, dar neexplicitat. Prioritate joasă. | A (la nevoie) |
| **Costuri de tranzacționare excluse / fără TVA** (102 §70, l.857-861) | ✅ | `_fara_tva` `:97-98`; checklist „fără TVA" `:471` | Acoperit (valoarea fără TVA). | A |
| **Alocarea valorii pe componente** (102 §80, l.865-875) | ✅ | `_adauga_alocare` `:384-419` (proprietate = teren + construcții); `sectiuni.py:18` | Acoperit, cu verificare de consistență față de CIN (>20% → avertisment). Bun, peste minim. | A |

---

## Top 5 goluri de conformitate

1. **Sursa/definiția tipului valorii nu e citată în raport** — ❌ (SEV 102 §20.4 l.754-755; SEV 101
   §20.1 h l.587; SEV 106 §30.6 i). Raportul enunță „Valoarea de piață (SEV 102)" dar **nu redă
   definiția și nici cadrul conceptual** (SEV 102 A10.2, l.886-962). Cerință explicită: „sursa
   definiției ... trebuie citată sau acesta trebuie explicat". **Fix (Bucket A, mic):** o bibliotecă
   de definiții pe tip valoare (piață/justă/investiție/lichidare/asigurare) inserată automat în
   secțiunea Termeni de referință. **Cel mai ieftin câștig de conformitate.**

2. **Declarația de conformitate e necondiționată** — ❌/🟡 (SEV 106 §30.8, l.2576-2578; SEV 100
   §40.6). App afirmă conformitatea SEV chiar dacă validările cad (comparabile <3, depreciere
   anormală, ESG absent). Standardul interzice afirmarea conformității când o limitare o afectează.
   **Fix (Bucket A):** leagă `_declaratie_conformitate` de rezultatul `valideaza()` — dacă există
   Issue-uri blocante, înlocuiește cu o notă de neconformitate / avertisment către evaluator.

3. **Specialist + ESG = text hardcodat, nu date reale** — 🟡 (SEV 106 §30.6 m și o, l.2566-2569;
   SEV 100 §30, l.460-481). „Nu a fost cazul unui specialist" și paragraful ESG sunt **fixe**,
   indiferent de input → risc de declarație falsă dacă se folosește un expert sau există date
   energetice/risc. **Fix (Bucket A + B):** flag „s-a folosit specialist?" (+ nume/domeniu/constatări)
   și câmp clasă energetică / risc de mediu, cu text condiționat.

4. **Lipsește acordul scris pe termenii de referință** — ❌ (SEV 101 §20.2-20.3, l.626-632; SEV 106
   §30.6 a). Termenii apar în raport, dar nu există un document **convenit în scris înainte de
   finalizare** (comandă/contract). **Fix:** șablon de scrisoare de acceptare/contract (Bucket A
   pentru schelet, **C** pentru clauze juridice, B pentru semnătură). Se leagă de tab-ul Documente.

5. **Utilizatorul desemnat opțional la garantare + CMBU placeholder** — 🟡 (SEV 106 §30.6 f, l.2558;
   SEV 102 A90, l.1124-1154). (a) `beneficiar` poate fi gol → raportul nu enunță utilizatorul
   desemnat și restricția de utilizare, deși la garantare creditorul e obligatoriu. **Fix (A):**
   validare „beneficiar obligatoriu la scop=garantare". (b) Secțiunea CMBU e adesea text AI generic
   fără cele 3 teste (fizic/legal/financiar) și fără referință la zonare. **Fix (A schelet + B
   concluzie):** structurează CMBU pe cele 3 criterii din A90.6.

---

## Rezumat (≤180 cuvinte)

Raportul `.docx` acoperă **bine** cadrul SEV 2025: din cele 18 cerințe minime (SEV 106 §30.6),
**~12 sunt complet acoperite** (termeni de referință, active, evaluator, client, scop, monedă, date,
abordări, metode, ipoteze, valoare+raționament, declarație de conformitate, data raportului) și
restul sunt **parțiale**. Structura `generator.py` urmează fidel shell-ul SEV 106 + GEV 520, cu motor
de calcul determinist, anonimizare GDPR înainte de AI, alocarea valorii și o verificare de consistență
cost↔piață peste minimul standardului.

**Cele mai importante goluri**, toate rezolvabile în cod (Bucket A): (1) **definiția/sursa tipului
valorii nu e citată** (SEV 102 §20.4) — câștigul cel mai ieftin; (2) **declarația de conformitate e
necondiționată**, contrar SEV 106 §30.8; (3) **specialist și ESG hardcodate** (risc de afirmație
falsă); (4) lipsa **acordului scris** pe termeni (necesită și jurist — Bucket C); (5) **utilizator
desemnat opțional** la garantare + **CMBU placeholder** fără cele 3 teste A90.

Planurile viitoare (tab Audit, identitate, hash input SEV) ajută trasabilitatea, dar **niciunul nu
acoperă golurile 1-3** — recomand prioritizarea lor înainte de release.
