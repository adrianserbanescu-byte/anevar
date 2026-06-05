# Conectarea widgetului de feedback la Google Forms (opțional)

Feedback-ul se salvează deja **local** (fișier `feedback-<data>.csv` lângă exe + în baza de
date). Google Forms e un canal **suplimentar, la distanță**: vezi răspunsurile în timp real,
fără să aștepți fișierul de la evaluator. Configurarea durează ~5 minute.

## Pasul 1 — Creează formularul

1. Intră pe <https://forms.google.com> → formular nou (gol).
2. Adaugă **exact 5 întrebări**, toate de tip „Răspuns scurt" (sau „Paragraf" la Mesaj),
   în această ordine (numele exact nu contează, ordinea conceptuală da):
   1. **Mesaj** (paragraf)
   2. **Pagină**
   3. **URL**
   4. **Reacție**
   5. **Nume tester**
3. ⚙️ Setări → dezactivează **„Colectează adrese de e-mail"** și **„Limitează la 1 răspuns"**
   (altfel testerii externi nu pot trimite). Lasă formularul public (oricine cu linkul).

## Pasul 2 — Ia `FORM_ID`

Apasă **Trimite (Send)** → tab-ul cu pictograma de link 🔗 → copiază linkul. Arată ca:

```
https://docs.google.com/forms/d/e/1FAIpQLSxxxxxxxxxxxxxxxxxxxxxxxx/viewform
```

Partea `1FAIpQLSxxxx...` (între `/d/e/` și `/viewform`) = **FORM_ID**.

## Pasul 3 — Ia cele 5 `entry.XXXX` (ID-urile câmpurilor)

1. Meniul **⋮** (dreapta sus) → **„Obține link precompletat" / „Get pre-filled link"**.
2. Scrie o valoare-test în fiecare câmp (ex. „m", „p", „u", „r", „t") → **„Obține linkul"**.
3. Copiază linkul generat. Conține perechi de forma:
   ```
   ...?entry.111111111=m&entry.222222222=p&entry.333333333=u&entry.444444444=r&entry.555555555=t
   ```
4. Notează ce număr `entry.` corespunde fiecărui câmp (după valoarea-test pe care ai pus-o):
   - Mesaj → `entry.111111111`
   - Pagină → `entry.222222222`
   - URL → `entry.333333333`
   - Reacție → `entry.444444444`
   - Nume tester → `entry.555555555`

## Pasul 4 — Pune valorile în aplicație

În `src/evaluare/web/templates/_feedback.html`, în obiectul `FB_CONFIG`:

```js
var FB_CONFIG = {
  formId:    "1FAIpQLSxxxxxxxxxxxxxxxxxxxxxxxx",  // FORM_ID (Pasul 2)
  message:   "entry.111111111",                  // Mesaj
  page:      "entry.222222222",                  // Pagină
  url:       "entry.333333333",                  // URL
  sentiment: "entry.444444444",                  // Reacție
  tester:    "entry.555555555"                   // Nume tester
};
```

Apoi **reconstruiește `.exe`** ca să intre modificarea.

## Mai simplu

Dă-mi cele 6 valori (FORM_ID + cele 5 `entry.`) și **le pun eu** în `FB_CONFIG` și reconstruiesc
exe-ul. Tu doar creezi formularul și copiezi linkul precompletat aici.

> Notă: chiar dacă nu configurezi Google, feedback-ul tot se salvează local (fișier + DB).
