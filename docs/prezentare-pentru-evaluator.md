# Aplicație de asistență la evaluarea imobiliară (casă + teren) — prezentare pentru review

*Document de prezentare pentru un evaluator autorizat ANEVAR. Scop: să înțelegi rapid ce face
aplicația, cum e gândită, ce metodologie aplică, ce e deja validat și ce mai e de făcut — și să-mi
spui dacă metodologia și raportul sunt corecte și complete pentru utilizare reală.*

---

## 1. Pe scurt: ce este

Este o aplicație care **asistă evaluatorul** la întocmirea unui raport de evaluare pentru o
**casă individuală cu teren**, în scopul **garantării unui credit**. Nu înlocuiește evaluatorul:
automatizează partea repetitivă (calcule, căutare de comparabile, redactarea raportului) și lasă
evaluatorul să decidă și să verifice.

Rulează ca un **singur fișier executabil** pe calculatorul evaluatorului (Windows). Nu necesită
instalări complicate: se deschide o pagină în browser, local, pe calculatorul propriu. Datele
rămân pe calculator; singurul moment în care ceva pleacă în exterior este generarea textului
narativ cu inteligență artificială — și acolo datele personale sunt **anonimizate înainte**
(detalii la secțiunea despre confidențialitate).

Ideea centrală: evaluatorul introduce datele proprietății, aplicația calculează valoarea după
metodologia ANEVAR și produce un **raport Word** gata de editat și predat.

---

## 2. Cum e gândită aplicația (la nivel înalt)

Aplicația are patru părți care lucrează împreună:

1. **Motorul de calcul** — face matematica evaluării: abordarea prin cost (CIN), grila de
   comparație pentru teren, grila de comparație pentru casă, reconcilierea și alocarea valorii.
2. **Descoperirea de comparabile** — caută anunțuri în zona aleasă, le citește, le punctează după
   similaritate cu proprietatea evaluată și propune cele mai potrivite.
3. **Generatorul de raport** — construiește documentul Word în structura uzuală (copertă,
   declarații, termeni de referință, capitolele de analiză, anexe), cu text narativ și fotografii.
4. **Interfața pas-cu-pas (wizardul)** — ghidează evaluatorul prin cinci pași, de la identificarea
   proprietății până la descărcarea raportului.

Filosofia de bază: **fiecare cifră trebuie să poată fi verificată**. Aplicația arată cum a ajuns la
fiecare rezultat (ce comparabil a ales și de ce, ce ajustări a aplicat, cum a punctat similaritatea),
nu doar valoarea finală.

---

## 3. Metodologia de calcul — partea cea mai importantă de verificat

Metodologia nu a fost inventată. A fost **aliniată la grile reale**, din patru dosare de evaluare
deja întocmite (Maneciu, Brașov, Bușteni, Breaza), atât pentru teren cât și pentru casă. Aplicația
**reproduce exact** valorile din acele dosare — aceasta este dovada că aplică aceeași logică.

### Terenul — grilă de comparație în două etape

Pentru teren, aplicația lucrează cu prețul în euro pe metru pătrat și aplică ajustările în **două
etape**, exact ca în grilele reale:

- **Etapa de tranzacție** (ofertă→tranzacție, drept de proprietate, finanțare, condiții de vânzare,
  cheltuieli, condițiile pieței): ajustările se aplică **secvențial**, una după alta, pe prețul
  curent → rezultă un preț de bază.
- **Etapa de proprietate** (localizare, acces, suprafață, deschidere, înclinație etc.): ajustările
  se aplică **aditiv** pe prețul de bază — adică se însumează procentele și se aplică o singură dată.

Comparabilul **ales** este cel cu **ajustarea brută minimă** pe etapa de proprietate (cel mai
asemănător), iar valoarea terenului = prețul pe metru pătrat corectat al acelui comparabil ×
suprafața terenului evaluat.

*De verificat de tine:* această separare pe două etape și faptul că ajustarea ofertă→tranzacție
**nu se contorizează** în ajustarea brută de selecție — corespund practicii tale?

### Casa — grilă de comparație pe preț total

Pentru casă, aplicația lucrează cu **prețul total** (nu pe metru pătrat), tot în două etape
(tranzacție secvențial + proprietate aditiv). Diferența de mărime între comparabile și subiect se
tratează printr-o **ajustare valorică de arie utilă** (preț unitar × diferența de suprafață), așa
încât fiecare comparabil este „adus" la subiect. Valoarea prin comparație = prețul total corectat al
comparabilului ales.

*O observație onestă:* în dosarele reale, celula de „ajustare brută" folosită pentru a alege
comparabilul nu urmează o formulă unică (la unele comparabile exclude localizarea, la altele nu).
Aplicația folosește o **regulă unică și transparentă** (ajustarea brută minimă pe etapa de
proprietate). Prețurile totale corectate se reproduc exact; alegerea comparabilului poate diferi de
marcajul manual din foaie în cazuri la limită. *De verificat: ce regulă de selecție preferi?*

### Abordarea prin cost (CIN)

Costul de înlocuire net se calculează segregat, pe elemente (catalog IROVAL): cost de înlocuire brut
× (1 − depreciere fizică) × (1 − depreciere funcțională) × (1 − depreciere externă), cu deprecierea
fizică interpolată după vârsta ponderată. Valoarea prin cost = CIN + valoarea terenului. Acest modul
a fost calibrat pe un model de calcul real și reproduce valoarea așteptată.

### Reconcilierea și alocarea

Aplicația reconciliază abordările (piață / cost / ponderată, la alegerea evaluatorului) și adaugă
**alocarea valorii**: valoarea construcțiilor = valoarea proprietății − valoarea terenului.

---

## 4. Fluxul de lucru (wizardul în cinci pași)

1. **Adresă și lucrare** — județ și localitate din liste (cu diacritice), date de identificare,
   client, beneficiar/finanțator, evaluator, date.
2. **Proprietatea** — teren, arii (utilă, construită desfășurată), an, elemente de cost, depreciere,
   plus atributele de potrivire pentru căutarea comparabilelor.
3. **Comparabile** — căutare automată în zonă, sau import dintr-un anunț după link, sau introducere
   manuală. Aplicația rankează candidații după similaritate; evaluatorul bifează ce e potrivit.
4. **Metodă și calcul** — alegerea metodei, monedă, curs, **fotografii pentru anexă**, apoi calcul,
   cu **alertele de validare** (prea puține comparabile, valori aberante, ajustări prea mari).
5. **Raport** — generează și descarcă documentul Word, editabil înainte de predare.

---

## 5. Descoperirea automată de comparabile

La pasul 3, aplicația caută anunțuri pe portaluri imobiliare în zona aleasă, le citește descrierea,
extrage atributele (an, stare, finisaj, încălzire, suprafețe) și **punctează similaritatea** cu
proprietatea evaluată, după șase criterii ponderate (suprafață construită, an, stare, finisaj,
încălzire, teren). Punctajul este **explicat complet**: pentru fiecare criteriu se arată valoarea
de referință, valoarea găsită, diferența și ponderea — astfel încât evaluatorul să înțeleagă de ce
un anunț e mai relevant decât altul, fără să acceseze documentația tehnică.

Comparabilele alese pot popula direct grila de comparație; evaluatorul adaugă apoi ajustările.

---

## 6. Raportul generat

Documentul Word respectă structura uzuală a unui raport pentru garantarea creditului:

- copertă, scrisoare de transmitere, **declarație de conformitate și certificare** (independență,
  conflict de interese, conformitate cu standardele ANEVAR);
- **termeni de referință** (client, beneficiar, scop, tip de valoare, monedă, curs, date);
- cele șapte capitole de analiză (sinteză, ipoteze, date de piață, descrierea proprietății, cea mai
  bună utilizare, aplicarea metodelor cu grilele de calcul, reconcilierea);
- **alocarea valorii**, **riscul asociat garanției (GEV 520)**, **anexe** (surse comparabile +
  fotografiile proprietății), casetă de semnătură.

Textul de analiză (ipoteze, piață, descriere, cea mai bună utilizare, justificarea ajustărilor,
reconciliere, risc GEV 520) poate fi **redactat automat cu inteligență artificială**, pe baza
cifrelor calculate — evaluatorul îl revizuiește și îl ajustează. Textul este curățat de elemente
nepotrivite (citări web, formatare markdown) ca să arate ca o proză profesională.

---

## 7. Confidențialitate (GDPR)

Singurul moment când date pleacă în afara calculatorului este redactarea narativului cu AI. Înainte
de orice apel, datele personale (nume client, adresă, număr cadastral, carte funciară, evaluator)
sunt **înlocuite cu marcaje** (de exemplu „[CLIENT]"), iar textul primit este **demascat local**.
Astfel, serviciul de AI nu primește niciodată date cu caracter personal. Restul calculelor și
generarea documentului se fac integral pe calculatorul evaluatorului.

---

## 8. Ce este deja validat

- **Terenul:** valorile a patru dosare reale (Maneciu, Brașov, Bușteni, Breaza) se reproduc exact —
  prețurile corectate pentru toate cele 12 comparabile și valorile finale (44.000 / 78.000 / 34.000
  / 67.000 euro).
- **Casa:** prețurile totale corectate ale comparabilelor dintr-un dosar real (Bușteni) se reproduc
  exact.
- **Costul (CIN):** reprodus pe un model de calcul real.
- Întreaga aplicație funcționează **cap-coadă** ca executabil: căutare comparabile, calcul, narativ
  AI, raport cu fotografii.

---

## 9. Ce mai e de făcut (limitări actuale)

- Validarea grilei de **casă** și pe celelalte dosare reale (Maneciu, Brașov) — am datele, mai e de
  rulat.
- **Cursul valutar** se introduce manual (nu se preia automat de la BNR).
- **Anexa cu documente** (extras CF, acte cadastrale) este momentan un marcaj „de atașat" — se poate
  adăuga încărcare de fișiere, ca la fotografii.
- **Export PDF** al raportului (acum este Word, care se poate salva ca PDF manual).
- Mai multă testare „pe teren", pe cazuri reale variate.

---

## 10. Întrebări pentru tine (ce feedback caut)

1. **Metodologia terenului:** separarea în două etape (tranzacție secvențial + proprietate aditiv) și
   selecția pe ajustarea brută minimă, **fără** a contoriza ofertă→tranzacție — sunt corecte și
   conforme practicii?
2. **Metodologia casei:** abordarea pe preț total, cu arie utilă tratată ca ajustare valorică, și
   valoarea = prețul total corectat al comparabilului ales — este corectă? Ce **regulă de selecție**
   a comparabilului preferi (cea unică și transparentă din aplicație, sau alta)?
3. **Reconcilierea și alocarea:** abordarea aleasă (piață / cost / ponderată) și alocarea
   construcții = proprietate − teren — sunt în regulă pentru scopul de garantare?
4. **Raportul:** structura și conținutul (declarații, termeni de referință, GEV 520, anexe) sunt
   **complete și acceptabile pentru bănci**? Lipsește ceva esențial?
5. **Validările automate** (minim de comparabile, valori aberante, limită de ajustare): pragurile
   sunt potrivite?
6. **Orice altceva** care, din experiența ta, ar face raportul respins sau ar trebui adăugat.

*Mulțumesc pentru timp. Orice observație, chiar și „așa nu se face", e exact ce caut.*
