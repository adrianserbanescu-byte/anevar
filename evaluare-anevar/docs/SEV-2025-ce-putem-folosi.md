# SEV 2025 — ce putem folosi în aplicație (LIVRABIL 1)

> **Scop (cum a cerut Adi):** „întâi ne spune ce putem folosi". Acest document rezumă structura
> Standardelor de evaluare a bunurilor — ediția 2025 (în vigoare **1 iulie 2025**, HCN nr. 2/2025) și
> separă ce e **RELEVANT + USABIL** pentru aplicația noastră (evaluare **casă + teren pentru garantarea
> creditului bancar**) de ce **NU se aplică** (întreprinderi, instrumente financiare, mașini etc.).
>
> **Sursă:** `C:\Users\adyse\anevar\md files\standardele-de-evaluare-a-bunurilor-2025.md` (SEV 2025 complet,
> ~14.000 linii). Citatele de paragraf se referă la numerotarea internă a fiecărui SEV/GEV.
>
> ⚠️ **Document de analiză metodologică.** Decizia de conformitate revine evaluatorului autorizat /
> ANEVAR, nu aplicației. Acesta e input pentru produs, nu o referință normativă în sine.

---

## 1. Structura standardului — ce conține

SEV 2025 = adaptarea IVS 2024 (International Valuation Standards) + un standard european (EVS/TEGoVA) +
ghidurile ANEVAR (GEV). Structura pe trei mari familii:

### A. Standarde generale (se aplică la ORICE evaluare) — **toate relevante pentru noi**

| Cod | Titlu | Pentru noi |
|---|---|---|
| **SEV 100** | Cadrul general al evaluării (IVS 100) | Principiile evaluatorului, **scepticism profesional** (par. 10.4), procedura de verificare a calității procesului (par. 20), utilizarea unui specialist. **NOU/rescris.** |
| **SEV 101** | Termenii de referință ai evaluării (IVS 101) | Ce trebuie agreat cu clientul; termeni noi: **specialist** și **factori ESG**. **Modificat consistent.** |
| **SEV 102** | Tipuri ale valorii (IVS 102) | Definiția valorii de piață, valoare justă, lichidare, asigurare; **„scopul evaluării" → „utilizare desemnată"**. Restructurat (Anexă nouă). |
| **SEV 103** | Abordări în evaluare (IVS 103) | Cele 3 abordări (piață/venit/cost) + metodele lor (mutate în Anexă). |
| **SEV 104** | Informații și date de intrare (IVS 104) | **STANDARD NOU.** Ierarhia datelor, selectarea datelor de intrare, **Anexa ESG**. |
| **SEV 105** | Modele de evaluare (IVS 105) | **STANDARD NOU.** Selectarea/utilizarea modelelor de evaluare. |
| **SEV 106** | Documentare și raportare (IVS 106) | **Rescris cu modificări de anvergură** (fostul SEV 103 Raportare). Conținutul minim al raportului. |

### B. Standarde pentru active — **doar familia „bunuri imobile" ne privește**

| Cod | Titlu | Relevanță pentru app |
|---|---|---|
| **SEV 230** | Drepturi asupra proprietății imobiliare (IVS 400) | ✅ **CORE.** Ce drept se evaluează, tipuri de valoare imobiliară, cele 3 abordări aplicate la imobiliar, chiria, ierarhia drepturilor. Conține și comentarii de aplicabilitate în România (Cod Civil). |
| **GEV 630** | Evaluarea bunurilor imobile | ✅ **CORE METODOLOGIC.** Ghidul detaliat pas-cu-pas (termeni de referință → culegere date → analiză → CMBU → cele 3 abordări → evaluarea terenului → reconciliere → raportare). Aplicabil **numai** de evaluatori cu specializarea **EPI**. |
| **GEV 520** | Evaluarea pentru garantarea împrumutului | ✅ **CORE — scopul nostru #1.** Cadrul obligatoriu pentru rapoarte cu utilizare desemnată „garantare". Înregistrare **BIG**, ESG, secțiune nouă **ANAF**, Anexa A1–A10. |
| **SEV 233** | Proprietatea în curs de construire (IVS 410) | ⚠️ Relevant doar dacă app-ul va trata imobile în construcție (metoda reziduală a terenului trimite la el). Nu e folosit azi. |
| **GEV 232** | Evaluarea proprietății generatoare de afaceri (PGA) | ⚠️ Relevant doar la tipul „comercial/special" cu venit din afacere (hotel, benzinărie etc.). Abordare principală = **venit**. |
| **GEV 500** | Estimarea valorii impozabile a clădirilor | ⚠️ Relevant doar pentru scopul „impozitare". App-ul are profilul, dar nu motorul GEV 500 propriu-zis. |
| SEV 200/210/220, GEV 600 | Întreprinderi, active necorporale, datorii | ❌ **NU se aplică.** |
| SEV 300, SEV 620, GEV 620 | Mașini, echipamente, stocuri | ❌ **NU se aplică** (decât marginal: echipamente atașate construcției — GEV 630 §120). |
| SEV 250 | Instrumente financiare | ❌ **NU se aplică.** |

### C. Standarde pentru utilizări specifice

| Cod | Titlu | Relevanță |
|---|---|---|
| **SEV 400** | Verificarea evaluării | ✅ Relevant: definește neconformități **majore/minore**, raport corespunzător/necorespunzător, **regula celor 20%**, verificarea internă a băncii. App-ul nu face verificare, dar GEV 520 §18 o cere. |
| **SEV 430** | Evaluarea pentru raportarea financiară | ⚠️ Doar scopul „raportare financiară" (valoare justă / IFRS 13). |
| **SEV 450** | Evaluarea costurilor în scopul asigurării (EVGN 6) | ✅ **NOU.** Doar scopul „asigurare": valoarea = cost de **reconstrucție** (cost de înlocuire **brut**, nedeprecat, fără teren). App-ul îl implementează deja în `ASIGURARE`. |

---

## 2. Ce e RELEVANT + USABIL pentru aplicație (casă + teren, garantare credit)

Pentru fluxul nostru principal (casă + teren → garantare credit bancar), **lanțul de standarde efectiv
aplicabil este**:

```
SEV 100/101/102/103/104/105/106  (cadrul general, mereu)
        +
SEV 230  (dreptul imobiliar evaluat)
        +
GEV 630  (metodologia imobiliară — cele 3 abordări, terenul, reconcilierea)
        +
GEV 520  (particularizările de garantare: BIG, independență, ESG, ipoteze speciale)
```

**Elementele USABILE direct în produs (ce trebuie să producă/verifice app-ul):**

1. **Cele 3 abordări de valoare** (GEV 630 §40–80): piață, venit, cost — cu reguli clare de când se
   aplică fiecare (vezi Livrabil 2 pentru matricea per tip). La **garantare**, GEV 520 §31 recomandă ca
   abordarea prin cost **să NU fie principală** pentru bunuri imobile (caracteristica de lichiditate).
2. **Tipul valorii = valoare de piață** (GEV 520 §20) — fără TVA; orice alt tip cere instrucțiune scrisă
   de la creditor.
3. **Minim 3 comparabile**, oferte admise dacă-s analizate critic (GEV 630 §51, §57; GEV 520 §33).
4. **Regula reconcilierii:** **interzisă media aritmetică/ponderată** a valorilor din abordări diferite ca
   simplu artificiu (GEV 630 §107); selecția se argumentează. **A doua abordare „formală" e interzisă**
   dacă una singură e suficientă și susținută (GEV 630 §108, GEV 520 §32).
5. **Regula celor 20%** (GEV 630 §109, SEV 400 §29): o diferență ≤20% între două evaluări cu aceiași
   termeni nu e a priori neconformitate.
6. **CMBU (cea mai bună utilizare)** — obligatoriu de prezentat concluzia (GEV 630 §35–39).
7. **Analiza pieței / aria de piață** — obligatoriu, individualizată pe proprietate (GEV 630 §30–34).
8. **Set de documente** (GEV 630 §16, GEV 520 §46): act proprietate, **extras CF**, **certificat de
   urbanism** (la terenuri libere/în construire), documentație cadastrală, **certificat energetic** (CPE).
9. **Suprafețe din document autorizat** (GEV 630 §25–27, GEV 520 §47): dacă diferă de acte → instrucțiuni
   de la creditor; evaluatorul nu are competență de măsurare.
10. **Înregistrare BIG** (GEV 520 §58, §83–84): rezultatul evaluării imobiliare pentru garantare se înscrie
    în Baza Imobiliară de Garanții ANEVAR; raportul final conține **recipisa**. **Excepție: ANAF** (§78) —
    NU se înregistrează în BIG.
11. **Independență + conflict de interese** (GEV 520 A3, §79, §81 — inclusiv **cerințele EBA**).
12. **ESG** (GEV 520 §86–88, SEV 104 Anexă): riscuri fizice + certificat energetic, cu disclaimerul de
    competență („calitatea de evaluator nu oferă competență de cuantificare a riscurilor fizice").
13. **Conținut minim de raport** (SEV 106 + GEV 630 §110–112 + GEV 520 A5): identificarea proprietății,
    tipul + premisa valorii + **sursa definiției**, ipoteze/ipoteze speciale într-o secțiune distinctă,
    documentarea/inspecția, comentariu asupra performanței garanției (cei 4 factori A5 a–d).

---

## 3. Ce NU se aplică (de exclus din produs)

- **Întreprinderi / participații / fond de comerț** (SEV 200, GEV 600) — alt domeniu.
- **Active necorporale, datorii nefinanciare** (SEV 210, SEV 220).
- **Mașini, echipamente, instalații, stocuri** (SEV 300, SEV 620, GEV 620) — cu o singură excepție de
  graniță: **echipamentele atașate construcției** (centrală, ascensor) pot fi factorizate în valoarea
  proprietății — GEV 630 §120.
- **Instrumente financiare** (SEV 250).
- **Evaluarea pentru raportarea financiară** (SEV 430), **impozitare** (GEV 500), **asigurare** (SEV 450) —
  relevante DOAR dacă utilizatorul alege explicit acel scop; nu pentru fluxul de garantare. App-ul are deja
  profiluri pentru ele, dar nu sunt pe calea critică „bancă".
- **Executarea silită** (GEV 520 §77) — explicit în afara standardului; se aplică legislația specifică.

---

## 4. Ce e NOU / SCHIMBAT în SEV 2025 care ne afectează

Din secțiunea oficială „Modificări ale SEV 2025 față de SEV 2022" (liniile 170–378 din standard), filtrat
pe ce atinge fluxul nostru:

| # | Schimbare | Impact pe app |
|---|---|---|
| N1 | **SEV 104 și SEV 105 = standarde NOI** (informații/date de intrare + modele de evaluare) | Introduce **ierarhia datelor de intrare** și **Anexa ESG**. App-ul trebuie să documenteze sursa/selecția datelor (parțial făcut în narativ). |
| N2 | **SEV 106 rescris** (fostul SEV 103 Raportare), modificări de anvergură | Conținutul minim al raportului s-a schimbat — de re-validat checklistul de raport. |
| N3 | **„scopul evaluării" → „utilizare desemnată"** (SEV 102) | Terminologie: peste tot „utilizare desemnată". App-ul folosește deja `utilizator_desemnat`. |
| N4 | **SEV 100: scepticism profesional + procedură de verificare a calității** (par. 10.4, 20) | Declarația de conformitate trebuie să le menționeze (app-ul o face deja — `generator.py:261–265`). |
| N5 | **SEV 101: termeni noi — specialist + factori ESG** | Termenii de referință trebuie să acopere ESG și recursul la specialist. |
| N6 | **SEV 310 ELIMINAT** (evaluări imobiliare pentru garantare) → **preluat în GEV 520** | GEV 520 e acum singurul ghid de garantare; nu mai există standard separat de imobiliar-garantare. |
| N7 | **GEV 520: două secțiuni NOI** — (a) **utilizator desemnat ANAF**, (b) **Anexă A1–A10** detaliată; „modificări de anvergură" | **Cel mai mare impact.** ANAF → fără BIG; Anexa = cerințele de conținut ale raportului. (Vezi Livrabil 3.) |
| N8 | **SEV 450 = standard NOU** (costuri în scop de asigurare) | App-ul îl implementează deja (`ASIGURARE` = cost de reconstrucție brut). |
| N9 | **GEV 630: paragrafe noi** — 12 l)/m), 42, 64, 120 + renumerotări | §42 (o singură metodă când datele observabile ajung), §64 (corelare tip venit ↔ tip rată), §120 (echipamente atașate). De verificat acoperirea. |
| N10 | **SEV 230 restructurat** — secțiuni noi 30, 100, 110, 120; paragrafe noi 40.2–40.7 | Cadrul general, informații/date, modele de evaluare, documentare/raportare ca secțiuni dedicate. |
| N11 | **SEV 400: glosar nou + neconformități majore/minore** | Definește pragul de „raport corespunzător/necorespunzător" — relevant când banca verifică. |
| N12 | **ESG ca cerință transversală** (SEV 101/104/106 + GEV 520/630) | **Novație 2025.** Trebuie să apară în termeni de referință și în raport, cu disclaimer de competență. |

---

## 5. Recomandări suplimentare (idei de livrabil/feature — Adi a invitat)

Pe lângă cele 3 livrabile cerute, lucruri utile identificate în timpul analizei:

1. **Checklist de conformitate „pre-emitere" per scop, în UI** (nu doar în .docx). App-ul are deja un
   checklist în raport (`generator.py:583+`), dar e static. Un **checklist live** care se bifează din
   datele dosarului (CPE prezent? recipisă BIG? min 3 comparabile? CMBU completat?) ar prinde lipsuri
   **înainte** de a trimite la bancă. Sursa de cerințe = `docs/GEV520-2025-crosscheck.md` (deja existent).

2. **Validator de „a doua abordare formală"** (GEV 630 §108 / GEV 520 §32): când utilizatorul aplică
   `ponderata` cu o pondere ~0 pe a doua abordare, app-ul ar trebui să alerteze („a doua abordare e
   formală — fie o argumentezi, fie folosești o singură abordare").

3. **Garda „cost nu e abordare principală la garantare"** (GEV 520 §31): la profil `GEV_520` + tip imobil,
   dacă metoda selectată = `cost` fără justificare (lipsă piață + lipsă venit, §34 — cu accept scris al
   creditorului), emite o **alertă** de conformitate. Azi codul permite tăcut `metoda=cost`.

4. **Suport SEV 104 — ierarhia datelor de intrare** ca metadată pe fiecare comparabilă (comparabil
   direct / indirect / general de piață / altă sursă — SEV 230 §100.2). Ar întări auditabilitatea.

5. **Bloc ESG generat condiționat** (riscuri fizice + CPE) cu disclaimerul de competență — e cel mai mare
   gol normativ 2025 rămas neimplementat (vezi `GEV520-2025-crosscheck.md` #24–26 și Livrabil 3).

6. **Acoperirea tipului „comercial" și a terenului standalone în UI** — `profil.py` definește `comercial`
   (abordare prin venit, GEV 630/232) și `teren`, dar dropdown-ul din `dosar.html` nu le expune. Pentru
   proprietăți generatoare de venit (cel mai des refuzate de evaluarea globală — GEV 520 §67), abordarea
   prin venit e principala; lipsa tipului în UI înseamnă că nu pot fi evaluate corect. (Vezi Livrabil 3, G2.)

---

**Documente conexe:**
- `docs/SEV-2025-cerinte-per-tip-imobil.md` (Livrabil 2 — matricea per tip).
- `docs/SEV-2025-gap-implementare.md` (Livrabil 3 — gap cerințe vs. cod).
- `docs/GEV520-2025-crosscheck.md` (crosscheck existent GEV 520 — pe care Livrabil 3 îl extinde).
