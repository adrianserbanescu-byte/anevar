# MODEL — Politică de prelucrare a datelor cu caracter personal

> ⚠️ **MODEL/DRAFT — de validat de un jurist (GDPR) și de adaptat la cabinet** înainte de folosire.
> Punctele B12/C5 din plan. Operatorul de date = evaluatorul/cabinetul, NU aplicația.

## 1. Operator
[Nume evaluator / Cabinet], CIF/CNP ____, adresă ____, e-mail ____, telefon ____.

## 2. Categorii de date prelucrate
- Date de identificare ale clientului/proprietarului: nume, adresă, CNP (dacă e necesar), date de contact.
- Date despre imobil: adresă, număr cadastral, carte funciară, fotografii.
- (AML, dacă e cazul) date KYC, beneficiar real.

## 3. Scopul și temeiul legal
- **Întocmirea raportului de evaluare** — executarea contractului (art. 6(1)(b) GDPR) + interes
  legitim profesional (art. 6(1)(f)).
- **Conformitate AML** — obligație legală (art. 6(1)(c) GDPR; Legea 129/2019).

## 4. Sub-procesatori (IMPORTANT — asistentul AI)
Pentru redactarea textului de analiză, raportul poate folosi un serviciu AI extern
(**Anthropic** și/sau **Perplexity**). Acestor servicii li se transmite **doar text anonimizat**
(numele/adresa/CF/cadastral sunt înlocuite cu marcaje `[CLIENT]`, `[ADRESA]` etc. înainte de
trimitere; demascarea se face local). 
- **De clarificat juridic:** acord de prelucrare (DPA) cu furnizorul AI; localizarea serverelor
  (UE/SUA); politica de retenție și de antrenare a furnizorului.
- **Alternativă fără AI:** aplicația funcționează și **complet offline** (text-șablon, fără niciun
  transfer extern) — recomandat pentru cazuri sensibile.

## 5. Perioada de păstrare
Conform obligațiilor profesionale ANEVAR și AML (de regulă 5 ani de la încheierea relației).

## 6. Drepturile persoanei vizate
Acces, rectificare, ștergere, restricționare, opoziție, portabilitate; plângere la **ANSPDCP**.

## 7. Securitate
Date păstrate **local** (calculatorul evaluatorului), bază SQLite; backup periodic; acces restricționat.
