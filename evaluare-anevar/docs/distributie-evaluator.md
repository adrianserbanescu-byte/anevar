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

## Pași pentru tine (împachetare)

1. Copiază `dist\evaluare-anevar.exe` într-un folder nou (ex. `Evaluare-ANEVAR\`).
2. Copiază `.env.example` în același folder, redenumește-l `.env`, pune cheia.
3. Arhivează folderul (`.zip`) și trimite-l.
4. (opțional) Atașează și `docs\exemplu-raport-breaza.docx` ca exemplu de ieșire.
