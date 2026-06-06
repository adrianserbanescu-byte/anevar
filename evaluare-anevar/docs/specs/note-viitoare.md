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

## Decizii deschise din noul UI (audit 2026-06-06) — de tranșat la brainstorm #1
Detaliile + recomandările sunt în [`../plan-maine-2026-06-06.md`](../plan-maine-2026-06-06.md) §B:
1. Ordine creare dosar: gol-apoi-completezi (acum) vs. modal de identitate înainte de folder.
2. **Lock identitate după prima generare** (read-only + cale „dosar nou + credit") — nu e forțat încă.
3. „Importă dosarul tău" = raport `.docx` (acum) vs. folder (`importa_folder`, adoptă/clonează).
4. Reconciliere `CAMPURI_NUME_DOSAR` (format nume) vs. `CAMPURI_IDENTITATE` (set blocabil).
5. Home: 5 opțiuni cu 2 dezactivate (comercial) — teasere vs. ascunse pe build offline.
6. Calcul→Generează: o singură sursă de adevăr (Generează cere Calcul reușit?).
7. Moneda implicită EUR la scop „garantare".
8. **Popover „!" (mapare wizard vechi→nou) e TEMPORAR** — de șters după validarea mapării.

## Regenerarea textului AI (feature B — ține de #2 versiuni + narativ AI)
- La „**Generează**", dacă dosarul are DEJA un raport (generat SAU importat): pentru fiecare
  capitol free-text se arată **textul vechi** din **cel mai recent** dintre {ultimul generat, import}.
- **Opțiunile per capitol vin din MATRICEA din master_administration** (care servește AMBELE cazuri):
  - **regenerare** (același dosar) → vechi.tip+scop == nou.tip+scop → matricea = „compatibil" → toate
    capitolele reutilizabile;
  - **import asemănător** (tip/scop diferit) → matricea decide per capitol: **diferit** (nu importă) /
    **ghidare** (Perplexity ia în considerare textul) / **particularizat** (ignoră textul).
- Userul **alege per capitol**: **Strict** (AI modifică doar valorile calculate, text minim schimbat) /
  **Template** (textul vechi = șablon, valorile se schimbă) / **Generare nouă (free)**.
- **Opțional**, userul adaugă **hint-uri text** per capitol pentru opțiunea aleasă; poate alege și ce
  **versiune** anterioară să folosească (din folder). AI folosește hint-ul doar dacă-l consideră relevant.

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
