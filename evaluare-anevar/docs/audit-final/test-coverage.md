# Audit de acoperire cu teste — funcționalitate adăugată recent

Scop: identifică **goluri reale de acoperire** (prioritizate după risc) pentru codul nou,
nu metrici brute. Suita actuală: **501 teste unit + 90 verificări e2e**; `fail_under = 90`,
acoperire reală **94%** (`pyproject.toml`). Acoperirea pe LINII e bună — golurile de mai jos
sunt majoritar de **comportament/contract** (căi de eroare, cap-coadă), nu linii neatinse.

## Constatări verificate empiric (rulate în acest audit)
- `/api/grila-casa` și `/api/grila-teren` cu `comparabile: []` → **HTTP 500** (ValueError din
  motor neprins). `/api/grila-chirii` are `try/except → 422` (`grile.py:42-45`). **Asimetrie + bug.**
- `/api/grila-casa` cu **1 comparabil** (sub `MIN_COMPARABILE=3`) → 200, fără gardă la nivel de grilă.
- `calcul` cu suprafață negativă → 200 + 1 alertă (`valideaza`); `raport.docx`/`calcul` cu
  `metoda=piata` și 0–1 comparabile → 200 (reconciliere tolerantă). Contractul „alerte" nu e aserit.

## Tabel goluri

| # | Prioritate | Zonă necoperită | Scenariu de test lipsă | Tip | Efort |
|---|-----------|-----------------|------------------------|-----|-------|
| 1 | 🔴 P0 | `grile.py` `/api/grila-casa` & `/api/grila-teren` — listă goală → **500** (motor aruncă `ValueError`, fără `try/except` ca la chirii) | POST cu `comparabile: []` → așteaptă **422** (nu 500); paritate cu `test_grila_chirii_fara_comparabile_422`. Expune și un bug, nu doar un gol | unit | S |
| 2 | 🔴 P0 | **Flux e2e complet cap-coadă**: `_pw_smoke.py` se oprește la „Generează activ după asumare" (l.329) — NU apasă butonul, NU descarcă `.docx`, NU verifică conținutul/dimensiunea | Click `#genereaza` → interceptează download-ul → asertă `.docx` > N bytes (și opțional „VALOAREA ESTIMATA" în text). Singurul artefact livrabil real nu e validat e2e | e2e | M |
| 3 | 🟠 P1 | `curent.py:140-171` `audit.txt` — ramurile condiționale `market_result`/`cost_result`/`land_result` (liniile 162/166/170 neacoperite) | Apel `audit.txt` cu payload care produce TOATE cele 3 rezultate (cost+piață+teren) → asertă că textul conține `rezultat_piata`, `rezultat_cost`, `rezultat_teren` | unit | S |
| 4 | 🟠 P1 | `curent.py` `calcul` — câmpul `alerte` nu e aserit niciodată (doar `valoare_finala`/`metoda` în `test_web_curent.py:97-101`) | `calcul` cu input invalid (Au>Acd sau suprafață ≤0) → asertă `alerte` negol + `nivel="blocheaza"`. Contractul de validare e expus prin API dar netestat | unit | S |
| 5 | 🟠 P1 | Grile: **ajustare brută peste prag (25%)** — `validation.LIMITA_AJUSTARE_BRUTA` testat doar prin `/api/evaluare` și e2e; grilele dedicate nu asertă alerta | `/api/grila-casa` cu ajustare proprietate 0.30 → verifică detectarea outlier/ajustare brută (sau documentează că grila NU raportează alerte — gol de contract) | unit | S |
| 6 | 🟠 P1 | `report/generator.py:664` (bloc **Apartament** în descriere) + `:678` (`inspectie_observatii`) + `:714-715` (DCF) — câmpuri conformitate populate neacoperite | `genereaza_raport` cu `building.etaj/an_bloc/cota_teren_indiviza` setate → asertă „Apartament:" în text; separat, `inspectie_observatii` + `dcf_valoare` | unit | S |
| 7 | 🟡 P2 | `generator._tip_valoare_txt` (l.92-101) — testat doar slug „piata"; ramurile **slug necunoscut** și **frază deja citată (SEV/IVS/IFRS)** neacoperite | Test unit direct: `_tip_valoare_txt("lichidare fortata")` → conține „SEV 102"; `_tip_valoare_txt("valoare just IVS 104")` → returnat neschimbat | unit | S |
| 8 | 🟡 P2 | `piata.py:62-63` ingestie — happy-path `extrage_text` + `extractor(text).model_dump` pe **PDF gol/valid** neacoperit (doar căile 400 tip/base64 sunt testate în `test_web_routers_gaps`) | `/api/ingestie` cu PDF digital minimal (fitz) tip `cf` → 200 + câmpuri `model_dump`; și PDF gol → 200 cu câmpuri None (nu crash) | unit | S |
| 9 | 🟡 P2 | `curent.py` `import-docx` — folder temporar șters pe `finally` (l.84-85) + ramura `Path(req.nume_fisier).name or "import.docx"` (path-traversal) neacoperite explicit | Import `.docx` cu nume_fisier conținând `../` → asertă dosar creat + fără scriere în afara temp (regresie pe fixul de securitate documentat) | unit | S |
| 10 | 🟡 P2 | `dosare_fs.py:134-135` & `:198-199` — `dosar.json` corupt în `listeaza()` / `importa_folder()` (ramuri `except OSError/ValueError`) | `listeaza()` cu un `dosar.json` invalid pe disc → e sărit, nu aruncă; `importa_folder` cu json corupt → `ValueError("dosar.json invalid")` | unit | S |
| 11 | 🟡 P2 | `orchestrator.descopera_teren` (l.179-183) — ramurile `fetch eșuat` și `pagina_lista` la descoperirea de TEREN; `descoperire.py:46-49` (`/api/descopera-teren`) integral neacoperit | Test `descopera_teren` cu fetcher care aruncă pe un URL + un URL pagină-listă → sare ambele; + smoke pe endpoint `/api/descopera-teren` | unit | M |
| 12 | 🟢 P3 | `report/generator.py:386` (`_adauga_grila_teren` ramura coloană lipsă) + `:542-543`/`:570-571` (anexe — surse/documente prezente) | Raport cu `comparables[].sursa` ≠ „manual" → Anexa 1 listează sursele (bullet); deja există foto/docx, lipsește calea „surse comparabile" | unit | S |

## Top 3 care merită teste noi acum
- **#1** (grilă goală → 500): bug live + asimetrie; test trivial, valoare mare.
- **#2** (e2e descărcare `.docx`): singurul livrabil real nevalidat cap-coadă.
- **#4/#5** (contractul `alerte` + pragul 25% pe grile): logica de prudență ANEVAR e expusă prin API dar neaserită la acest nivel.

Efort: S ≈ <30 min, M ≈ 30–90 min.
