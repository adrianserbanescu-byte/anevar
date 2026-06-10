# GEV 520 (SEV 2025) — checklist de conformitate raport vs. cod

> **Scop:** extrage cerințele oficiale de *conținut al raportului* din Ghidul **GEV 520
> „Evaluarea pentru garantarea împrumutului"** (ediția 2025) și le pune față în față cu ce
> generează/verifică aplicația azi, pentru a alinia checklistul din cod la **Anexa GEV 520 în vigoare**.
>
> **Sursă:** `SEV 2025` (Standardele de evaluare a bunurilor, ed. 2025), GEV 520 — descărcat de pe
> [anevar.ro/images/_upload/sev-2025.pdf](https://www.anevar.ro/images/_upload/sev-2025.pdf), p. 283–298
> (secțiune) + Anexa (paragrafele A1–A10). **În vigoare de la 1 iulie 2025** (Conferința Națională,
> hotărârea nr. 2/9 aprilie 2025).
>
> ⚠️ **Document de lucru (DRAFT).** Citatele au diacriticele reconstruite din extragerea PDF→text;
> înainte de a fi tratat ca referință normativă, se confruntă cu PDF-ul oficial. Decizia de
> conformitate revine evaluatorului autorizat / ANEVAR, nu aplicației.

---

## 1. Unde trăiește conformitatea GEV 520 în cod

| Aspect | Fișier | Note |
|---|---|---|
| Secțiuni de raport (registru) | [report/sectiuni.py](../src/evaluare/report/sectiuni.py) | secțiunile `gev_520`, `alocare_valoare` apar doar pe profil `GEV_520` |
| Conținut raport (text GEV 520) | [report/generator.py](../src/evaluare/report/generator.py) | `_adauga_risc_garantie` (L508+), termeni de referință GEV 520 (L300–320), verificare consistență (L500) |
| Checklist conformitate (16 puncte) | [report/generator.py:556](../src/evaluare/report/generator.py) | marcat în cod: *„de aliniat la Anexa 1 a GEV 520 în vigoare"* — **acesta e ținta alinierii** |
| Validare calcul (nu conținut) | [engine/validation.py](../src/evaluare/engine/validation.py), [audit/validare_x.py](../src/evaluare/audit/validare_x.py) | praguri date, comparabile, divergență abordări |
| Urma de audit (tamper-log) | [audit/raport_audit.py](../src/evaluare/audit/raport_audit.py) | **NU** e despre conformitate GEV 520 — e lanțul hash de evenimente |

> Notă: `raport_audit.py` (ținta inițială discutată) este urma de audit cripto, nu verificarea
> raportului față de GEV 520. Checklistul de conformitate efectiv este în `generator.py:556–573`.

---

## 2. Cerințe oficiale GEV 520 (2025) → acoperire în cod

Legendă: ✅ acoperit · ⚠️ parțial · ❌ lipsă/contradicție

### A. Termeni de referință & independență

| # | Cerință GEV 520 (2025) | §  | Cod | Stare |
|---|---|---|---|---|
| 1 | Indicarea oricărei **implicări materiale** a evaluatorului cu bunul / debitorul / un debitor potențial | A3 / SEV 101 §20.1(e) | `generator.py:308–313` | ✅ |
| 2 | **Utilizator desemnat = creditorul nominalizat**; orice altă utilizare cere personalizare | A3 | `generator.py:311–313` | ✅ |
| 3 | **Ipoteze speciale** (vânzare forțată / perioadă de marketing limitată) precizate în termeni; valabile doar la data evaluării | A4 | `generator.py:315–320` | ✅ |
| 4 | Clauză de **independență** în documentul contractual (interzice rezultat prestabilit) | §79 | — | ⚠️ ține de contract, nu de raport; de menționat în declarație |
| 5 | Declarații exprese privind **lipsa conflictului de interese, inclusiv cerințele EBA** | §81 | — | ❌ **lipsă** (checklistul cere doar „declarația de conformitate și independență") |
| 6 | Plata serviciului **nu e condiționată** de acceptarea garanției / acordarea creditului | §82 | — | ⚠️ de adăugat ca declarație |

### B. Inspecție & identificare

| # | Cerință GEV 520 (2025) | §  | Cod | Stare |
|---|---|---|---|---|
| 7 | Inspecția **exterioară ȘI interioară** este **obligatorie** | §44 | checklist „identificată și inspectată" | ⚠️ nu distinge int/ext |
| 8 | În raport: **data inspecției**, **numele persoanei care a realizat-o (evaluator autorizat)**, numele solicitantului/persoanei desemnate care a însoțit | §44 | parțial (data inspecției apare în descriere) | ⚠️ **persoana care a însoțit** nu e capturată |
| 9 | Menționarea expresă a oricărei **neclarități de identificare** + instrucțiuni primite de la creditor | §45 | — | ❌ lipsă punct dedicat |
| 10 | Set de documente obligatorii (act proprietate, extras CF actualizat, **certificat energetic al fiecărei clădiri**, …) | §46, L14864 | act+CF da; **CPE nu** | ⚠️ certificatul energetic nu e cerut explicit |

### C. Comentariul asupra performanței garanției (miezul Anexei A5)

| # | Cerință GEV 520 (2025) | §  | Cod | Stare |
|---|---|---|---|---|
| 11 | a) activitatea curentă și **tendințele pieței** relevante | A5 a | `generator.py:521` | ✅ |
| 12 | b) cererea **anterioară/curentă/viitoare** pentru tip de bun și localizare | A5 b | `generator.py:522` | ✅ |
| 13 | c) cerere potențială/probabilă pentru **alte utilizări** la data evaluării | A5 c | `generator.py:523` | ✅ |
| 14 | d) impactul **evenimentelor previzibile** asupra valorii viitoare a garanției (ex. opțiune reziliere chiriaș) | A5 d | `generator.py:524–525` | ✅ |
| 15 | Atenție la **chirie peste piață** (lease above-market): a se ignora sau a contabiliza riscuri suplimentare | A6+ | — | ⚠️ de adăugat notă |
| 16 | **PGA** (proprietate generatoare de afaceri): scenariu de bază convenit cu creditorul (going concern / OER / utilizare alternativă / încetare) | Anexă | — | ⚠️ relevant doar comercial/PGA |
| 17 | **Active epuizabile**: durata de viață estimată + rata de diminuare precizate clar | Anexă | — | ⚠️ de adăugat când e cazul |

### D. Valoare, ipoteze speciale, vânzare forțată

| # | Cerință GEV 520 (2025) | §  | Cod | Stare |
|---|---|---|---|---|
| 18 | Pe ipoteză specială, raportul include: (1) explicarea ipotezei, (2) comentariu diferență față de valoarea de piață, (3) că valoarea poate să nu fie realizabilă la o dată viitoare | A6 e) 1–3 | `generator.py:315–320` parțial | ⚠️ punctele 2 și 3 de explicitat |
| 19 | Bun ocupat de proprietar → evaluat în ipoteza **transferului liber/disponibil** | Anexă / A8 | `generator.py:300–304` | ✅ |
| 20 | **Valoarea de lichidare / vânzare forțată** estimată (factor stabilit de evaluator, tipic 0,80–0,90) | uzanță garantare | `generator.py:536–549` | ✅ (factor orientativ 0,85, marcat „de evaluator") |

### E. Înregistrare BIG & utilizator desemnat

| # | Cerință GEV 520 (2025) | §  | Cod | Stare |
|---|---|---|---|---|
| 21 | Raportul final RE conține **dovada scrisă (recipisa)** de înregistrare în **BIG** pentru utilizatorul desemnat | §83–84 | `generator.py:532–535` + checklist „se înregistrează în BIG" | ⚠️ de întărit: **recipisa**, nu doar „se înregistrează" |
| 22 | **Re-desemnarea utilizatorului:** un raport întocmit pentru alt scop (raportare financiară, asigurare, impozitare) **NU poate fi folosit de creditor** pentru garantare fără re-desemnare + modificarea înregistrării BIG | secț. „Evaluarea cu utilizator desemnat", L14508–14536 | — | ❌ **lipsă (novație 2025)** |
| 23 | **Evaluarea cu utilizator desemnat ANAF** (reeșalonare datorii): urmează GEV 520, dar aceste rapoarte **NU se înregistrează în BIG** | §77–78 | — | ❌ **CONTRADICȚIE:** codul afirmă necondiționat „se înregistrează în BIG" |

### F. Factori ESG (novație 2025, §86–88)

| # | Cerință GEV 520 (2025) | §  | Cod | Stare |
|---|---|---|---|---|
| 24 | Factorii ESG tratați conform Anexei ESG din SEV 104 | §86 | — | ❌ lipsă |
| 25 | **Riscuri fizice** ESG: evaluatorul autorizat **nu are competență** de cuantificare; dacă creditorul furnizează date și piața permite, le poate analiza; altfel menționează că nu le poate cuantifica (raportul rămâne conform) | §87 a–d | — | ❌ lipsă |
| 26 | **Certificat energetic** (CPE / clădire verde): dacă e furnizat, evaluatorul îl analizează/cuantifică sau menționează lipsa evidențelor de piață | §88 | — | ❌ lipsă (vezi și #10) |

### G. Checklist conformitate (verificat de evaluator)

| # | Cerință GEV 520 (2025) | Cod | Stare |
|---|---|---|---|
| 27 | Valoarea = valoare de piață (SEV 102/IVS 104), fără TVA | `generator.py:557` | ✅ |
| 28 | Data evaluării + data raportului precizate | `generator.py:558` | ✅ |
| 29 | Scop (garantare) declarat în termeni | `generator.py:559` | ✅ |
| 30 | Min. 3 comparabile; oferte ajustate la nivel de tranzacție | `generator.py:561,568` + `validation.py:52` | ✅ |
| 31 | CMBU analizată | `generator.py:565` | ✅ |
| 32 | Evaluator autorizat ANEVAR + asigurare răspundere profesională | `generator.py:571` | ✅ |
| 33 | Declarație de conformitate și de independență semnată | `generator.py:572` | ✅ |

---

## 3. Concluzie — diferențe care contează (priorizate)

**🔴 Conflict real (de reparat):**
- **#23 — ANAF:** codul scrie necondiționat *„Raportul se înregistrează în BIG"* (`generator.py:532–535`),
  dar pentru garanția în favoarea ANAF (reeșalonare) raportul **NU se înregistrează în BIG** (§77–78).
  Pe un dosar ANAF, raportul curent ar afirma ceva fals. → de făcut condițional.

**🟠 Goluri normative 2025 (lipsesc complet din raport/checklist):**
- **#22 — Re-desemnarea utilizatorului** (raport pentru alt scop ≠ utilizabil la garantare fără re-desemnare + BIG).
- **#24–26 — ESG**: secțiune nouă obligatorie (riscuri fizice + certificat energetic), cu *disclaimerul de competență*.
- **#5 — Declarație conflict de interese conform EBA** (distinctă de declarația de independență).

**🟡 Întăriri (parțial acoperite):**
- **#8** persoana care a însoțit inspecția + **#7** int/ext explicit;
- **#9** neclarități de identificare; **#21** recipisa BIG (nu doar „se înregistrează");
- **#18** punctele 2–3 ale ipotezei speciale; **#10** certificatul energetic în setul de documente;
- **#6** plata necondiționată; **#15–17** chirie peste piață / PGA / active epuizabile (după caz).

**✅ Solid (matchuri exacte cu Anexa):** A5 a–d (cei 4 factori de performanță a garanției, #11–14),
ipoteza transfer liber (#19), valoarea de lichidare cu factor lăsat evaluatorului (#20), nucleul checklistului (#27–33).

---

## 4. Modificări concrete propuse în cod

1. **`generator.py` — BIG condiționat de utilizatorul desemnat (#23).**
   Introdu un câmp profil/meta `utilizator_desemnat ∈ {creditor, ANAF}`; pentru `ANAF`, înlocuiește
   afirmația BIG cu *„Raportul nu se înregistrează în BIG (utilizator desemnat ANAF — GEV 520 §77–78)."*
   și scoate punctul „se înregistrează în BIG" din checklist pe acest caz.

2. **`generator.py` — secțiune ESG nouă (`_adauga_esg`) pe profil GEV_520 (#24–26).**
   Riscuri fizice (cu disclaimerul „calitatea de evaluator autorizat nu oferă competență de cuantificare")
   + certificat energetic. Adaugă 2 puncte în checklist.

3. **`generator.py:556–573` — extinde checklistul** cu: recipisa BIG (#21), conflict de interese EBA (#5),
   plata necondiționată (#6), persoana care a însoțit inspecția (#8), neclarități de identificare (#9),
   certificat energetic furnizat (#10/26).

4. **Re-desemnare utilizator (#22):** o notă în termenii de referință + un punct de checklist
   („dacă raportul a fost întocmit inițial pentru alt scop, a fost re-desemnat utilizatorul și modificată
   înregistrarea BIG").

5. **Test:** extinde testele ADR-003/profil cu un caz `utilizator_desemnat=ANAF` care asertează că textul BIG
   se schimbă și că checklistul nu mai conține înregistrarea BIG.

> Toate textele rămân *draft generat de aplicație*; evaluatorul autorizat validează și își asumă conținutul
> (conform disclaimerului existent în `raport_audit.py` / rapoarte).
