# #3 — Localități adăugate de utilizator

Status: **de brainstormat** (încadrat). **Cel mai mic / livrabil rapid** — feature local.

## Idee
Userul poate adăuga localități proprii (care nu există în datasetul curent), care devin apoi
**căutabile** — în wizard (dropdown) și la descoperirea de comparabile.

## Ce avem azi
- `localitati.py` + dataset fix; `GET /api/localitati` → județe + localități; wizardul are deja
  opțiunea „altă localitate (scriu)" cu cod fără diacritice generat manual de user.
- Lipsește: **persistarea** localităților adăugate + integrarea lor în liste/căutare.

## Întrebări deschise (de rezolvat la brainstorm)
- Unde se stochează? (tabel nou `localitati_user` în SQLite — migrare schema)
- Câmpuri: nume cu diacritice (pt. raport) + slug fără diacritice (pt. portaluri) + județ.
  Generăm slug-ul automat din nume (avem deja regula ă→a etc.)?
- Apar amestecate cu cele oficiale în dropdown sau într-o secțiune „Ale mele"?
- Validare: județ valid, fără duplicate.
- (Relația cu #4: dacă devine multi-user candva, localitățile sunt per-cont — dar acum local.)

## Schiță tehnică (probabilă)
- Migrare schema: tabel `localitati_user(judet, nume, slug)`.
- `POST /api/localitati/adauga` (nume + județ → slug auto) ; `GET /api/localitati` le include.
- UI: în wizard Pas 1, buton „➕ Adaugă localitate" lângă dropdown.
