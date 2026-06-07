# Topicuri de definit prin brainstorming / grill-me (mai târziu)

> Teme de design care merită o sesiune dedicată (skill `superpowers:brainstorming` sau `grill-me`) înainte de
> implementare. NU le implementez până nu le definim împreună.

## T1 (2026-06-07) — Istoricul proiectelor local + afișarea documentelor generate anterior
**De definit prin brainstorming/grill-me:**
1. **Cum salvăm istoricul proiectelor LOCAL** — structura, ce reținem per dosar/proiect, cum versionăm,
   retenția, metadatele (când, ce format, ce valoare finală), eventual o „bibliotecă"/index de proiecte.
2. **Cum afișăm documentele generate anterior** — UI: listă de dosare/proiecte, versiunile fiecărui raport
   (`.docx`/`.pdf`), deschidere/descărcare/reprevizualizare, căutare/filtrare, deschidere a versiunilor vechi.

**Context existent (de la care pornim, nu de la zero):**
- Model „**folder = adevăr**": fiecare dosar = un folder cu `dosar.json` + versiuni `raport-*.docx` (retenție 10).
- `/incepe` are deja „**Încarcă dosar salvat**" (tabel dosare cu „Deschide") + „Dosare dispărute".
- Backup `.zip` al tuturor dosarelor există.
- Acum raportul se generează în **docx / pdf / ambele** (versiunea `.docx` se salvează mereu în folder).

**Întrebări de spart la sesiune:** istoricul = doar lista de dosare sau un „dashboard de proiecte" cu
preview-uri? Reținem și PDF-urile generate ca versiuni (acum doar `.docx` e persistat)? Cum legăm
versiunile raportului de momentul generării + parametrii? Căutare după client/adresă/dată/valoare?

> Reminder programat: 2026-06-07, după ora 12 (vezi `schedule`/cron). La fire → notificare + pornim sesiunea.
