# Parking lot — decizii/comentarii ce impactează feature-uri viitoare

Notițe din brainstorming de adus în discuție **când ajungem la feature-ul respectiv** (sau la
finalul celor 4 brainstorming-uri). Actualizat: 2026-06-06.

## Pentru noul UI (#1) / dosare (#2)
- **Fără duplicare veche/nou.** Noul UI = unicul, țintă; vechiul = referință pentru maparea
  feature-urilor. (Suprascrie decizia „două versiuni").
- **Folder = adevăr** + diff la pornire (existente / noi / **dispărute**) + categorie „dosare dispărute".
- **Identitate dosar** = câmpurile obligatorii alese în noul UI; unele FORȚAT obligatorii
  (tip proprietate, scop), altele auto-completate dacă userul nu le dă (ex. `id_client`).
  Modificarea lor → **dosar nou + 1 credit**.
- **Denumire dosar** = template per-user din `master_config` (min 3 câmpuri); `id_client` unic,
  free-text la creare, **needitabil ulterior** (la import cere ID nou).
- **„Home UI dosar"** = workspace per dosar, în care intri după oricare din cele 5 opțiuni.

## Regenerarea textului AI (feature nou, derivat — ține de #2 versiuni + narativ AI)
- La FIECARE generare de raport pentru un dosar cu generare anterioară, userul e întrebat (o dată),
  per capitol free-text: folosește textul anterior ca **template strict** / **template general** /
  **generare nouă**; poate alege ce **versiune** anterioară; poate adăuga **textul lui** (marcat
  strict/template) + **instrucțiuni suplimentare** pentru AI (la strict + generare nouă).
- AI folosește textul userului ca strict/template doar dacă-l consideră relevant.

## Import „dosar asemănător" (sub-proiect — Slice D)
- Întrebat tip+scop nou și tip+scop al dosarului importat.
- **Matrice de compatibilitate** între capitolele free-text (importat vs nou) → în
  **master_config** (generată la build). Stări per capitol:
  - **diferit** → nu importă;
  - **ghidare** → Perplexity ia în considerare textul importat la generare;
  - **particularizat** → Perplexity nu se uită la importat.
- Valori calculate → se importă doar VALORI din raportul importat.
- Doar **rapoarte de evaluare completă**; upload doar `.docx`/`.pdf`; rezumat per capitol + confirmare.

## Comercial (#4 / Slice C)
- **Cont obligatoriu** la deschiderea noului UI (Google SSO / email+parolă) + legitimație ANEVAR.
- **Demo** pentru cont fără abonament: vede toate 5 opțiunile, accesează doar demo.
- **Pagină master-admin** (doar tu): gestionezi userii + câmpurile pe care ei nu le pot schimba.
- **UUID per-user** (din opțiuni hardcoded), modificabil de admin în DB.
- **Anti-fals** real = semnătură pe gateway (HMAC), nu criptare locală (cheia ar fi în app = teatru).
- **Backup online** al dosarelor = stocare în gateway.
- Ștergerea legitimației — doar admin, din DB online.
