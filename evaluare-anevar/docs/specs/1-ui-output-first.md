# #1 — UI nou „output-first" (UI-ul unic, țintă)

Status: **în definire** (2026-06-06). Vizual. Depinde de #4 (începe cu cont).

## Decizie de cadru (2026-06-06)
- **FĂRĂ duplicare** veche/nou. **Noul UI = unicul UI țintă.** Vechiul = **referință** din care
  **mapăm TOATE feature-urile** (paritate obligatorie — vezi lista de mapat mai jos).
- Noul UI **începe cu cont** (Google SSO / email+parolă + legitimație ANEVAR) + alegerea
  **formatului numelui de dosar** (din `master_config`). → depinde de #4 (gateway).

## Structura noului UI
1. **Cont** (o dată): creare cont + format nume dosar. [#4]
2. **Homepage „ÎNCEPE"** — 5 opțiuni:
   1. **Creare** dosar nou
   2. **Încărcare** dosar salvat (local)
   3. **Importă dosarul tău** (în lucru)
   4. **Importă dosar asemănător** [Slice D]
   5. **Demo** [#4 — cont fără abonament]
3. **Home UI dosar** = workspace per dosar (aici se face evaluarea; aici se mapează feature-urile vechi).

## Comportament per opțiune (din brainstorm)
- **Creare:** userul definește info obligatorie = câmpurile din template-ul de nume + câmpuri
  FORȚAT obligatorii (tip proprietate, scop), unele auto-completate dacă lipsesc (ex. `id_client`).
  → intră în **Home UI dosar**.
- **Încărcare:** → direct în **Home UI dosar**.
- **Importă dosarul tău:** alege fișiere; **obligatoriu** json-ul (semnat cu legitimația lui),
  opțional restul output-urilor app; i se spune ce se poate importa; alege „import & creează local"
  sau „anulează".
- **Importă asemănător [Slice D]:** întrebat tip+scop nou și ale dosarului importat; alege fișiere;
  matricea de compatibilitate capitole free-text (importat vs nou) = în `master_config`. Vezi
  [note-viitoare.md](note-viitoare.md).
- **Demo [#4]:** → Home UI dosar pentru un dosar mostly-hardcoded.

## ⏳ Următorul pas de definit: **Home UI dosar** (workspace)
Cum e organizată evaluarea în noul UI — pornind de la output (raport) spre date. Aici trebuie
**mapate toate feature-urile vechiului UI** (vezi mai jos).

## Feature-uri ale UI-ului vechi DE MAPAT în noul UI (paritate)
- Wizard: identificare (adresă/cadastral/CF/client/beneficiar/scop/evaluator/date), proprietate
  subiect (teren/construcție/elemente cost/depreciere; per tip: apartament/industrial/agricol),
  comparabile (descoperire + import URL + manual + grilă), metodă & calcul (cost/piață/ponderată/
  venit/DCF), monedă+curs BNR, anexe (foto/documente), generare raport `.docx` (+ demo + audit).
- Grile (teren/casă/chirii) · Descoperire comparabile · AML (+ documente) · GDPR · Dosare salvate.
- Extensie browser (import anunțuri) · ingestie PDF (pre-completare).

## Dependențe deblocate de #1
- #2 (identitatea dosarului — care câmpuri se blochează) · #4 (metrarea pe identitate).
