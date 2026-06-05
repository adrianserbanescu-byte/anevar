# #2 — Rapoarte salvate (revenire / editare / regenerare / ștergere)

Status: **de brainstormat** (încadrat). **Cel mai buildabil acum** — feature local, izolat.

## Idee
La fiecare generare de document, raportul/dosarul se salvează local. Userul poate:
- reveni la rapoarte salvate, le poate **modifica și regenera**,
- **importa** dosarul înapoi în web (re-deschide în wizard) sau accesa documentul ca `.docx`,
- **șterge** din documentele salvate,
- (posibil) **redenumi** dosarele.

## Ce avem deja în cod (avantaj — jumătate e gata)
- `storage.save(ctx)` salvează deja fiecare evaluare în tabela `evaluari` (JSON complet) +
  `storage.list()` / `storage.load(eid)`. Deci dosarele SE salvează deja.
- Lipsește: o **pagină de management** (listă, re-deschide, redenumește, șterge) + re-hidratarea
  wizardului dintr-un dosar salvat + (opțional) salvarea fișierului `.docx` pe disc lângă exe.

## Întrebări deschise (de rezolvat la brainstorm)
- Salvăm și fișierul `.docx` generat pe disc (lângă exe, ca la feedback) sau doar dosarul (JSON)
  din care regenerăm `.docx` la cerere? (recomandare inițială: dosarul e sursa de adevăr;
  `.docx` se regenerează — evită fișiere învechite)
- Redenumire: câmp `nume_dosar` nou în `evaluari` (migrare schema v4).
- Ștergere: doar dosarul din DB, sau și `.docx`-urile asociate de pe disc?
- Re-deschidere: cum re-hidratăm exact toate câmpurile wizardului din `context_json`?
- Relația cu #4: dosarele salvate țin și narativul AI cache-uit (regenerare `.docx` = gratis).

## Schiță tehnică (probabilă)
- Migrare schema **v4**: `evaluari.nume`, `evaluari.creat_la`.
- Pagină `/dosare`: listă (nume, client, valoare, dată) + acțiuni Deschide / Redenumește /
  Descarcă `.docx` / Șterge.
- Endpoint re-hidratare: `GET /api/evaluare/{id}/dosar` → JSON pentru pre-completarea wizardului.
