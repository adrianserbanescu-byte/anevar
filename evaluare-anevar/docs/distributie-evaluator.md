# Cum trimiți aplicația (+ cheia API) către un evaluator

## Ce trimiți — 2 fișiere, în ACELAȘI folder

```
Evaluare-ANEVAR\
  evaluare-anevar.exe     ← aplicația (din dist\)
  .env                    ← cheia API (fișier text, vezi mai jos)
```

**Da — ambele trebuie să fie în același folder.** La pornire, `.exe` citește fișierul `.env`
din folderul în care se află el (și din directorul curent). Dacă `.env` e în altă parte, cheia
nu e găsită și aplicația merge fără AI (text-șablon).

## Fișierul `.env`

Text simplu, o linie cu cheia. Pornește de la `.env.example` (redenumește-l în `.env`):

```
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxx
```

(sau `ANTHROPIC_API_KEY=sk-ant-...` dacă folosești Claude). Atât. Fără ghilimele, fără spații.

## Fără cheie?

Aplicația **funcționează oricum** — doar că textul de analiză e generat din șabloane, nu prin AI.
Calculele, grilele, rapoartele `.docx` și AML merg identic.

## Atenții importante

1. **Cheia e vizibilă în `.env` (text simplu).** Cine are fișierul îți poate folosi cheia
   (și consumă din bugetul tău). Recomandat: dă o cheie **dedicată, cu limită de buget**, sau
   cere evaluatorului să-și ia cheia lui (și să o pună singur în `.env`).
2. **Nu pune folderul într-un cloud sincronizat** (OneDrive/Dropbox/Google Drive). SQLite +
   sincronizare = risc de corupere; aplicația te avertizează la pornire dacă detectează asta.
3. **Windows 10/11** (nu Windows 7). La prima rulare, SmartScreen poate avertiza (exe nesemnat):
   „More info" → „Run anyway".
4. **Date locale**: la prima rulare, lângă `.exe` se creează automat `date\` (baza + rapoarte)
   și `backups\`. Nu trebuie create manual.

## Cum primești feedback-ul de la evaluator

Aplicația are un buton **„✎ Feedback"** (jos-dreapta, pe orice pagină). Evaluatorul scrie
o observație + 👍/👎 și apasă Trimite. Feedback-ul se **salvează local, offline** (în baza de
date a aplicației lui — nu are nevoie de internet sau cont Google).

Ca să-l citești, cere-i evaluatorului să-ți trimită înapoi unul din:
- folderul `date\` de lângă exe (conține `evaluari.db`), SAU
- exportul direct: deschide `http://127.0.0.1:8000/api/feedback.csv` în aplicația lui → un CSV.

Apoi tu vezi tot la `http://127.0.0.1:8000/feedback` (pornind aplicația pe baza primită) sau
deschizi CSV-ul în Excel.

> Opțional, widgetul poate trimite **și** în Google Forms (canal la distanță, în timp real) —
> completează `FB_CONFIG` din `_feedback.html` cu ID-urile formularului. Fără asta, feedback-ul
> tot se salvează local.

## Pași pentru tine (împachetare)

1. Copiază `dist\evaluare-anevar.exe` într-un folder nou (ex. `Evaluare-ANEVAR\`).
2. Copiază `.env.example` în același folder, redenumește-l `.env`, pune cheia.
3. Arhivează folderul (`.zip`) și trimite-l.
4. (opțional) Atașează și `docs\exemplu-raport-breaza.docx` ca exemplu de ieșire.
