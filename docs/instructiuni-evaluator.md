# Instrucțiuni — Aplicația de asistență la evaluare (casă + teren)

*Document scurt pentru evaluatorul care primește aplicația. Se poate salva și ca .txt.*

## Ce este
O aplicație care te ajută să întocmești raportul de evaluare pentru **casă + teren, garantarea
creditului**: introduci datele, ea calculează (cost CIN, grilă casă, grilă teren, reconciliere,
alocare) și generează **raportul Word** conform standardelor ANEVAR în vigoare (SEV 2025, GEV 520).

## Cum pornești
1. **Dublu-click** pe `evaluare-anevar.exe`.
2. La prima rulare, Windows poate afișa **„Windows protected your PC"** (aplicația e nesemnată).
   Apasă **„More info" → „Run anyway"**. (Normal pentru un program distribuit fără certificat.)
3. Se deschide automat browserul la **`http://localhost:8000`** cu wizardul în 5 pași.
   (Dacă nu se deschide, intră manual la adresa de mai sus.)
4. Lângă `.exe` se creează un folder `date/` (baza de date locală) — lasă-l acolo.

## Fluxul de lucru (5 pași)
1. **Adresă & lucrare** — județ/localitate, client, beneficiar (banca), evaluator, date.
   - *Pornire rapidă:* poți **importa dintr-un PDF** (extras CF, releveu, plan) → câmpurile se
     pre-completează (verifică-le).
2. **Proprietatea** — teren, arii (Au/Acd), an, elemente de cost, depreciere, atribute.
3. **Comparabile** — descoperă automat în zonă, importă din link sau adaugă manual; bifezi ce e ok.
4. **Metodă & calcul** — metoda, monedă, **curs BNR (buton)**, fotografii, documente, apoi calculezi;
   apar **alertele de validare**.
5. **Raport** — generează `.docx` (normal sau **cu note demo**) și **urma de audit (.txt)**.

## Inteligența artificială este OPȚIONALĂ
- **Fără cheie AI:** funcționează tot calculul, descoperirea (preț/suprafață/caracteristici),
  raportul — textul de analiză rămâne „[de completat]".
- **Cu cheie AI:** se redactează automat și textul narativ (ipoteze, piață, CMBU, GEV 520) — pe care
  îl revizuiești. Cheia se pune într-un fișier `.env` lângă `.exe` (cere-o firmei/asociației, nu
  folosi cheia altcuiva).

## Confidențialitate (GDPR)
Datele rămân pe calculatorul tău. Singurul moment când ceva pleacă în exterior este redactarea
textului cu AI — și acolo **datele personale sunt anonimizate înainte** (nume, adresă, cadastral,
CF), iar textul primit este demascat local.

## Ce produce
- **Raport `.docx`** — structură GBF/ANEVAR (copertă, declarații, termeni de referință, cele 7
  capitole, GEV 520, alocare, anexe foto + documente, semnătură). Editabil; pentru PDF → în Word
  „Salvează ca → PDF".
- **Urmă de audit `.txt`** — jurnal cu marcaj de timp și hash (integritate verificabilă).

## Important de știut
- **Comparabilele din portaluri sunt orientative** — verifică-le; raportul precizează acest lucru.
- **Ajustările din grile** sunt judecata ta profesională (aplicația nu le impune).
- **Valoarea** o decizi tu; AI-ul doar redactează, nu evaluează.

## Probleme frecvente
- **Pornire lentă prima dată** — normal (se dezarhivează în temp).
- **„localhost refuză conexiunea"** — așteaptă câteva secunde după pornire și reîncarcă pagina.
- **Portul 8000 ocupat** — închide alt program care îl folosește, apoi repornește `.exe`.
- **Antivirus blochează** — exe-ul e nesemnat; adaugă-l la excepții dacă ai încredere în sursă.
