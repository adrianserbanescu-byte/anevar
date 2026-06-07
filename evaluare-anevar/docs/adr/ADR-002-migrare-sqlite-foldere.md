# ADR-002: Stocarea pe foldere ca sursă unică de adevăr (retragerea SQLite-ului vechi)

**Status:** Acceptat (direcție) — **scriptul de migrare e implementat și testat** (`src/evaluare/migrare.py`
+ CLI `scripts/migreaza_sqlite_foldere.py` + `tests/test_migrare.py`); declanșatorii Fazei 2/3 (când rulează
+ când se retrage SQLite) rămân decizia Adi (`BLOCAT-pe-Adi.md` #17, #18).
**Date:** 2026-06-06 (actualizat 2026-06-07: script implementat)
**Deciders:** proprietarul proiectului (Adrian)

## Context

Aplicația are **două sisteme de persistență disjuncte**, scrise pentru două UI-uri diferite:

- **SQLite vechi** (`src/evaluare/db/storage.py`): o bază unică `evaluari.db` (tabel `evaluari`
  + `import_anunturi` + `feedback`), schema versionată prin `PRAGMA user_version` (acum v4),
  backup consistent via API-ul SQLite. Alimentează UI-ul vechi (wizard/formular). Dosarele au
  cheie `INTEGER id`.
- **Stocarea pe foldere** (`src/evaluare/dosare_fs.py`): fiecare dosar = un folder
  `<OUTPUT_DIR>/dosare/<uuid>/` cu `dosar.json` (semnătură: uuid, creator, identitate, snapshot
  wizard) + versiuni `raport-*.docx`. La pornire se **scanează** folderele (nu o bază autoritară);
  un `_index.json` reține „ultima vedere" doar pentru diff. Alimentează UI-ul nou „output-first".

Forțe în joc:

- **Risc de divergență:** două surse de adevăr înseamnă date care se pot contrazice. Am avut deja
  un caz concret — «Calculează» din UI nou scria **rânduri orfane** în SQLite (reparat: acum scrie
  în `dosar.json` prin `/api/dosar/{uid}/calcul`). Cât timp ambele sisteme acceptă scrieri,
  reapariția divergenței e o chestiune de timp.
- **Council Q1 (consens):** folderele = **sursa unică de adevăr**; SQLite degradat la index/cache,
  apoi retras (vezi `9-topicuri-decizie.md` Topic 5, `council-plan-UI-nou.md` §1.1).
- **Folderul e portabil și auditabil:** un dosar = un director copiabil/arhivabil, lizibil în
  Explorer, aliniat cu modelul de licențiere (un folder = o identitate de proprietate) și cu
  cerința de anexe (foto/scanuri stocate lângă `dosar.json`). SQLite-ul nu oferă nimic din astea.
- **Date reale de protejat:** `Storage.backup()` și migrările de schemă există tocmai fiindcă
  baza veche conține munca evaluatorului. Retragerea trebuie să fie **ne-distructivă** și reversibilă
  până la confirmarea finală.
- **Produs offline (`.exe` PyInstaller):** migrarea rulează **local**, fără I/O extern; nicio
  dependență nouă.

## Decision

**Stocarea pe foldere (`dosare_fs`) devine sursa unică de adevăr.** SQLite-ul vechi este retras
printr-o **migrare unidirecțională** (SQLite → foldere), niciodată invers, în **3 faze**:

### Faza 1 — Coexistență (acum)
- Nou = foldere; vechi = SQLite (citit/scris doar de UI-ul vechi).
- Niciun flux nou nu mai scrie în SQLite din UI-ul nou (orfanul deja reparat).
- Fără presiune pe user; cele două lumi rulează în paralel.

### Faza 2 — Buton „Migrează" + feature-freeze pe UI vechi
- Buton **one-time „Migrează în folder"** per dosar vechi: citește rândul din `evaluari`
  (`context_json` + `wizard_json` + `nume` + `creat_la`) → creează `dosare/<uuid>/dosar.json`
  (+ copiază anexele/`.docx` dacă există) → marchează rândul `migrated` în SQLite (**reversibil**,
  nu șterge).
- **Feature-freeze pe UI-ul vechi**: nu mai primește funcționalități noi; intră în întreținere.
- Script **ne-distructiv** + **log de migrare obligatoriu** (ce s-a migrat, ce s-a sărit, de ce);
  skip-pe-eroare (un dosar prost-format nu blochează lotul).

### Faza 3 — Retragere
- UI-ul vechi oprit; codul de scriere SQLite eliminat.
- SQLite trecut **read-only** (păstrat pentru recuperare de urgență), apoi retras complet.
- `db/storage.py` rămâne în repo doar cât timp e nevoie de citire de urgență.

## Options Considered

### Opțiunea A: Păstrăm ambele sisteme la nesfârșit
Punte bidirecțională sau pur și simplu le lăsăm separate.

| Dimensiune | Evaluare |
|------------|----------|
| Complexitate | Mare (sincronizare permanentă) |
| Risc de divergență | Permanent ridicat |
| Cost de întreținere | Dublu (două scheme, două backup-uri) |

**Pros:** zero migrare; UI-ul vechi rămâne intact.
**Cons:** consacrarea a două surse de adevăr; orfanul deja apărut o dată; fiecare feature trebuie
scris de două ori; modelul de licențiere (folder = identitate) nu se poate baza pe SQLite.

### Opțiunea B: Migrare bruscă (big-bang)
Un singur script convertește tot, șterge SQLite, taie UI-ul vechi într-un singur release.

| Dimensiune | Evaluare |
|------------|----------|
| Complexitate | Medie |
| Risc | Mare (ireversibil dacă maparea greșește) |
| Reversibilitate | Slabă |

**Pros:** scapă instant de dualitate.
**Cons:** un bug de mapare a anexelor/contextului pierde date reale **fără cale de întoarcere**;
niciun interval de validare; userul nu are timp să verifice migrarea per dosar.

### Opțiunea C: Migrare unidirecțională în 3 faze (recomandat)
Coexistență → buton „migrează" + feature-freeze → retragere; SQLite read-only ca plasă.

| Dimensiune | Evaluare |
|------------|----------|
| Complexitate | Medie |
| Risc | Mic (ne-distructiv, reversibil până la Faza 3) |
| Reversibilitate | Bună (marcaj `migrated`, fără ștergere) |

**Pros:** o singură sursă de adevăr la final; fiecare pas e verificabil; userul controlează ritmul;
SQLite rămâne plasă de siguranță; aliniat council Q1.
**Cons:** perioadă de tranziție (~luni) cu două sisteme vii; cod de migrare + log de scris și testat.

## Consequences

### Pozitive
- **O singură sursă de adevăr** → dispare clasa de bug-uri „rândul orfan / date care se contrazic".
- Dosarul devine o **unitate portabilă** (copiabilă/arhivabilă/importabilă — `importa_folder`),
  baza modelului de licențiere și a anexelor.
- Migrare **ne-distructivă, reversibilă** până la Faza 3; SQLite păstrat pentru recuperare.
- Backup-ul devine trivial (copiezi un director), fără API special.

### Negative
- **Perioadă de coexistență** cu două sisteme vii (risc rezidual de confuzie până la Faza 3).
- Cost de **cod de migrare + log + testare** a mapării (în special anexele și `context_json` vechi).
- Pierdem **interogarea SQL** ad-hoc peste dosare (acceptabil: volumul e mic, scanarea folderelor
  e suficientă; un index extern poate reveni dacă apare nevoia).
- `import_anunturi` și `feedback` (tot în SQLite vechi) trebuie reevaluate separat — **nu** sunt
  dosare; decizie deschisă dacă migrează, rămân sau se retrag odată cu UI-ul vechi.

## Action Items

1. [ ] Confirmare Adi pe **declanșatorii fazelor** (când Faza 2, când Faza 3 — `BLOCAT-pe-Adi.md` #17, #18).
2. [x] ✅ **Implementat:** `migrare.migreaza(apply)` — dry-run + `--apply`; mapează `wizard_json` → `dosar.json`, copiază rapoartele (`tip="import"`), skip-pe-eroare, jurnal returnat. CLI + teste.
3. [x] ✅ **Implementat:** marcaj `migrated_uuid` în SQLite (reversibil, ne-distructiv, **idempotent** — re-rularea nu re-migrează).
4. [ ] Buton „Migrează în folder" per dosar vechi în UI-ul vechi (Faza 2) — *opțional; CLI-ul acoperă deja migrarea în lot*.
5. [ ] Decizie pentru `import_anunturi` + `feedback` (migrare / păstrare / retragere).
6. [ ] Faza 3: SQLite read-only + eliminare cod de scriere; smoke pe import/listare/diff din `dosare_fs`.

> **Decizie cerută Adi:** aprob direcția (folderele = adevăr, SQLite retras unidirecțional în 3 faze)
> și stabilesc declanșatorii pentru Faza 2 (feature-freeze) și Faza 3 (retragere)?
