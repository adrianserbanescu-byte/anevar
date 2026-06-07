# Manual de utilizare — Evaluare ANEVAR

> Ghid pentru evaluatorul autorizat ANEVAR. Versiune draft, 2026-06-07. Aplicația **asistă** evaluatorul;
> nu îl înlocuiește și nu decide valoarea — toate cifrele se verifică și se asumă de evaluator.

## 1. Instalare și pornire
1. Dezarhivează folderul aplicației oriunde (ex. pe Desktop).
2. Dublu-clic pe **`evaluare-anevar.exe`**.
3. La prima rulare, Windows SmartScreen poate avertiza (aplicația nu e încă semnată digital):
   **„Informații suplimentare" → „Executare oricum"**.
4. Se deschide automat o pagină în browser la **`http://127.0.0.1:8000`** (local, offline).
5. Închidere: închizi fereastra neagră (consola) a aplicației.

**Funcționare fără cheie AI:** aplicația merge integral și fără internet/cheie — doar că textul narativ
e generat din șabloane în loc de AI. Calculele, grilele, raportul `.docx` și AML sunt identice. Pentru
narativ AI, vezi `distributie-evaluator.md` (fișierul `.env` cu cheia).

## 2. Prima configurare — contul
La prima accesare, mergi pe **„Homepage nou"** și creează-ți contul (o singură dată):
- **Nume evaluator** + **legitimația ANEVAR**.
- **Formatul numelui de dosar** — bifezi în ordine câmpurile care vor compune numele folderului fiecărui
  dosar (minim 3, ex. `id_client · nume_client · tip_proprietate`), cu previzualizare live.

## 3. Crearea unui dosar
Din **ÎNCEPE** ai trei opțiuni:
- **Dosar nou** — completezi câmpurile de identitate (cele din formatul ales). `tip_proprietate` și `scop`
  se **blochează** după creare (intră în identitatea dosarului).
- **Încarcă dosar salvat** — redeschizi un dosar existent (din folderul lui).
- **Importă dosarul tău** — încarci un raport `.docx` existent; aplicația pre-completează identitatea din
  numele fișierului și din text.

Toate câmpurile de dată au **format românesc** și **blochează datele viitoare** (max = azi).

## 4. Spațiul de lucru (workspace)
Salvarea e **automată, în folderul dosarului** (la fiecare modificare; indicator „● salvat în folder").
Patru tab-uri:

### 4.1 Tab RAPORT — 5 sub-tab-uri
- **Proprietate** — identitatea + descrierea. Poți **pre-completa din PDF** (extras CF / releveu / plan /
  certificat energetic) cu butonul de ingestie → verifici valorile extrase. Completezi: județ/localitate
  (liste), adresă, cadastral, CF, proprietar, beneficiar (banca), drept evaluat, act, **sarcini/grevări**
  (din extras CF — important la garantare), cele 3 date (raport/evaluare/inspecție), **inspecția**
  (amploare, însoțitor, observații). Câmpurile fizice se schimbă după **tipul proprietății** (apartament /
  industrial / agricol / teren / construcție). Plus utilități, cale de acces, regim urbanistic (POT/CUT),
  și — pentru abordarea prin cost — elementele de cost + tabelul de depreciere.
- **Comparabile** — trei moduri de a aduce comparabile:
  1. **Descoperire inline** pe portaluri (imobiliare.ro / storia.ro) — alegi zona, aplicația caută,
     citește, punctează după similaritate și explică fiecare criteriu; bifezi candidații → intră în grilă.
  2. **Import dintr-un link** sau din **extensia de browser** (deschizi manual un anunț și apeși butonul
     extensiei — fără scraping automat).
  3. **Introducere manuală.**
  Apoi completezi **grilele de ajustări** (casă / teren / chirii), fiecare pe **două etape**: „tranzacție"
  (ofertă→tranzacție, drept, condiții — aplicate compus) și „proprietate" (caracteristici fizice/juridice —
  aplicate aditiv). Aplicația **avertizează** dacă ajustarea brută depășește **25%** (GEV 520). Prețurile
  din portaluri sunt din **OFERTE** — ajustarea ofertă→tranzacție o pui tu.
- **Calcul** — alegi **metoda** (cost / piață / ponderată / venit / DCF), moneda, cursul BNR (auto). Apeși
  **„Calculează"** → vezi valoarea finală + eventualele **alerte de validare** (ex. Au > Acd, sub 3
  comparabile, outlier). Alertele nu blochează — tu decizi.
- **Anexe** — încarci **fotografiile** (Anexa 2) și **scanurile/documentele** (Anexa 3); intră direct în
  raportul `.docx`. Cerință de conformitate SEV 2025 / GEV 630.
- **Generează** — vezi §4.5.

### 4.2 Tab AML
Pentru obligațiile Legii 129/2019: alegi tipul entității tale (PFA/PJ), datele clientului (PF/PJ), bifezi
PEP, semnalele de risc și cei 10 indicatori de suspiciune. **„Evaluează relația"** → afișează categoria de
risc, nivelul de măsuri, motivele de risc sporit și dacă **se propune RTS**. Apoi generezi documentele
(.docx): norme interne, evaluare de risc, fișă KYC, decizie de desemnare (doar societate), RTN, RTS.
⚠️ **Aplicația NU verifică automat** listele de sancțiuni/PEP — confirmi manual din surse oficiale
(OpenSanctions, EU Sanctions Map). Documentele AML sunt **DRAFT** — a se valida cu un jurist.

### 4.3 Tab GDPR
Generezi modelele `.docx`: **politică de prelucrare** + **acord de consimțământ**. Operatorul de date ești
**tu** (evaluatorul). Datele personale sunt **anonimizate** înainte de orice apel AI; datele AML nu pleacă
niciodată către AI.

### 4.4 Tab AUDIT
**„Generează urma de audit"** → un jurnal hash-înlănțuit + validare încrucișată a valorilor curente
(trasabilitate la control).

### 4.5 Generarea raportului + checkpoint de asumare
1. Bifezi declarația de asumare: *„Confirm că am verificat datele și îmi asum profesional valoarea și
   conținutul raportului, ca evaluator autorizat ANEVAR."* — butonul **„Generează"** rămâne blocat până
   bifezi (om-în-buclă; semnătura îți aparține).
2. Dacă lipsesc datele evaluării/raportului, aplicația cere confirmare (o dată greșită afectează
   valabilitatea juridică la garantare).
3. Se descarcă raportul **`.docx`** (editabil). Fiecare generare = o **versiune persistentă** în folderul
   dosarului (istoric). În raport: toate valorile sunt deterministe; textul narativ e draft, de revizuit.

## 5. Versiuni, backup, dosare
Fiecare dosar = un **folder** cu `dosar.json` + versiunile `raport-*.docx` (se păstrează ultimele 10).
Poți face **backup** (arhivă `.zip` a tuturor dosarelor) din bara de jos a workspace-ului. Un dosar șters
manual din disc apare în „Dosare dispărute" → „scoate din listă".

## 6. Depanare (FAQ)
- **Nu se deschide browserul** → intră manual pe `http://127.0.0.1:8000`.
- **SmartScreen blochează** → „Informații suplimentare" → „Executare oricum".
- **Descoperirea nu găsește nimic** → verifică internetul / zona; portalul poate fi temporar indisponibil
  (aplicația te anunță) — adaugi comparabilele manual.
- **Narativ „[de completat]"** → rulezi fără cheie AI (sau fără internet); completezi manual sau adaugi
  cheia (`.env`).
- **PDF import nu extrage** → PDF-ul poate fi scanat fără text; verifici/completezi manual.

> **Răspundere:** aplicația oferă asistență de calcul și redactare. Metodologia, valoarea și semnătura
> aparțin evaluatorului autorizat ANEVAR. Textele juridice/AML sunt modele — a se valida cu un jurist.
