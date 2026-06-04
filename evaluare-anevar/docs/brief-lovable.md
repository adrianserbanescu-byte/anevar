# Brief pentru Lovable — concept vizual „Evaluare ANEVAR"

> **Scop:** Lovable produce DOAR conceptul vizual (aspect, culori, tipografie, componente).
> Nu implementăm logică/React în produs — designul va fi portat manual în șabloanele
> existente (server-rendered Jinja + CSS). De aceea: **cere CSS curat cu variabile
> (design tokens), nu stiluri inline aleatorii**, și **fără dependențe de CDN** (fonturi
> incluse local), ca să pot copia valorile direct.

## Instrucțiune de pus în Lovable (copiază blocul)

```
Construiește un CONCEPT VIZUAL (nu logică funcțională) pentru o aplicație desktop
locală de evaluare imobiliară conform standardelor ANEVAR (România). Estetică:
„registru cadastral / topograf" — hârtie-pergament caldă, cerneală bleumarin,
accent sienna de topograf + verde cadastral, linii fine de alamă, tipografie cu
serife de document (gen Constantia/Cambria) pentru titluri + sans (Segoe UI) pentru
text, cifre tabulare pentru valori. Bandă-antet discretă în tricolor. Aspect sobru,
profesional, de document oficial — NU stil „SaaS modern colorat".

Livrează toate culorile, spațierile, razele și umbrele ca variabile CSS (:root)
și nu folosi fonturi de la Google Fonts/CDN — folosește fonturi de sistem.

Ecrane de proiectat (vezi descrierile de mai jos): Wizard (5 pași), Grile de
comparabile, Descoperire, AML, Pagina de rezultat, Formular clasic.
```

## Ecranele reale (proiectează-le pe acestea)

1. **Wizard** (ecranul principal) — flux în **5 pași** cu un **stepper numerotat clickabil**:
   `Adresă · Subiect · Comparabile · Calcul · Raport`. Stări pas: făcut / activ / următor.
   - Pas 1 (Adresă): dropdown județ + localitate, adresă, date dosar (client, beneficiar,
     scop, proprietar), identitate evaluator (nume + legitimație), 3 date calendaristice.
   - Pas 2 (Subiect): selector tip proprietate (casă+teren / apartament / comercial /
     industrial / agricol / special); câmpuri condiționate de tip (ex. AU/ACD, etaj, an bloc).
   - Pas 3 (Comparabile + metodă): tabel de comparabile; selector metodă (cost / piață /
     venit-capitalizare / venit-DCF); câmpuri de venit (VBP, neocupare, cheltuieli, rată cap)
     sau DCF (fluxuri, rată, valoare reziduală).
   - Pas 4 (Calcul): rezultate intermediare, valori formatate ro-RO (`316.000,00`).
   - Pas 5 (Raport): buton generare `.docx` + variantă „demo" cu note de proveniență.

2. **Grile de comparabile** (`/grila`) — **3 tabele** (teren / casă / chirii), fiecare cu
   rânduri de comparabile + coloane de ajustări (procentuale/valorice), rând de rezultat
   (preț/mp ales, valoare). Pastile/badge-uri pentru selecția indexului.

3. **Descoperire** (`/descoperire`) — formular de căutare pe portaluri (portal, județ,
   localitate) + listă de candidați cu scor de relevanță, preț, suprafață, explicație.

4. **AML** (`/aml`) — formular KYC (persoană fizică/juridică), evaluare de risc cu
   pastile de categorie (redus/mediu/ridicat), butoane de generare documente (.docx).

5. **Rezultat** (`/evaluare/{id}`) — card mare cu valoarea finală, moneda, echivalent
   valutar, metoda selectată.

6. **Formular clasic** (`/formular`) — toate câmpurile pe o pagină (alternativă la wizard).

## Componente de stilizat (ca să acopere tot ce am)

- Stepper numerotat (conectori care se umplu), carduri-pas cu margine de registru.
- Tabele-registru (zebra discretă, cifre tabulare, antet cu linie de alamă).
- Butoane: primar (sienna), secundar (contur), pastile de stare/risc.
- Inputuri, select, fieldset/legend, mesaje de eroare, mesaje de stare (role=status).
- Bară-antet tricoloră + „kicker" de marcă pe titlu, fundal cu grilă cartografică fină.
- Bară de progres / accent auriu→sienna.

## Ce primesc eu înapoi și ce fac cu el

- Din repo-ul de concept iau **variabilele CSS** (paletă, type scale, spațieri, umbre,
  raze) + stilurile de componente și le port în `templates/_design.css`.
- Adaptez markup-ul șabloanelor (Jinja) cât e nevoie ca să prindă noile clase, **fără**
  să schimb logica JS sau API-ul. Rezultatul rămâne `.exe` offline, server-rendered.

## Contract de date (opțional, dacă vrei și layout cât mai fidel)

Pot exporta specificația OpenAPI a API-ului (`/openapi.json`) — o lipești în Lovable ca
să cunoască numele exacte ale câmpurilor. Nu e obligatoriu pentru un concept pur vizual,
dar face mockup-urile să folosească etichetele reale.
```
