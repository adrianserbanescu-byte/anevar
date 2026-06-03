# Modul Audit trail (validare & conformitate) — Design

**Data:** 2026-06-03
**Status:** Draft (planificat)
**Context:** Sistemul 5 din specificația inițială („Validare & conformitate") este parțial
implementat: **validări SEV** (`engine/validation.py`) ✅ și **anonimizare GDPR** (`report/anonymizer`)
✅. Lipsesc **audit trail** (urmă de audit) și **validarea încrucișată** sistematizată.

---

## 1. Problema

Astăzi calculele și sursele sunt vizibile în raport (transparență), dar nu există o **înregistrare
persistentă, cu marcaj de timp**, a deciziilor și surselor unui dosar: ce comparabile au fost
folosite, ce ajustări, ce surse externe (portal/BNR/BIG/ANCPI), ce versiune de standarde, cine și
când. Pentru garantarea creditului și pentru o eventuală contestare, urma de audit e valoroasă.

## 2. Scop

Modul care produce, per dosar, o **urmă de audit** completă și o **validare încrucișată** finală:
- jurnal de evenimente (intrări, surse externe interogate, calcule, generări de raport) cu
  timestamp și hash;
- snapshot al inputurilor și rezultatelor (reproducibilitate);
- raport de **validare încrucișată** (consistență între abordări, plauzibilitate, încadrare în
  pragurile SEV) înainte de finalizare.

**Non-goal:** semnătură electronică calificată (separat); stocare în cloud.

## 3. Arhitectură (modul nou `audit/`)

```
src/evaluare/audit/
  jurnal.py        # inregistrare evenimente (append-only) per dosar, cu timestamp + hash
  snapshot.py      # serializare input+rezultat (reproducere) legata de dosar
  validare_x.py    # validari incrucisate (piata vs cost, plauzibilitate, praguri SEV)
  raport_audit.py  # exporta urma de audit (anexa interna / fisier separat)
```

- **Append-only** (fiecare eveniment înlănțuit prin hash) → integritate verificabilă.
- Persistență în SQLite existentă (extindere `db/storage.py`), legat de ID-ul dosarului.
- Reutilizează validările existente; adaugă **validarea încrucișată** ca pas final.

## 4. Integrare

- Transparent: fiecare apel important (descoperire, BNR, calcul, generare raport) scrie în jurnal.
- Înainte de generarea raportului: **raport de validare încrucișată** (alertele existente +
  consistența între abordări) — blocant pentru alertele critice.
- Opțional: export al urmei de audit ca fișier separat (nu în raportul clientului).

## 5. Riscuri / dependențe
- **Volum/performanță** jurnal — design simplu, append-only, local.
- **Confidențialitate** — urma de audit conține date personale → rămâne locală, intră sub aceleași
  reguli GDPR (anonimizare la orice export către AI; aici nu se exportă).

## 6. Pași de implementare (rezumat)
1. `audit/jurnal.py` (append-only + hash) + extindere `db/storage.py` — TDD.
2. `audit/snapshot.py` (serializare input+rezultat).
3. `audit/validare_x.py` (validare încrucișată) — integrare în fluxul de finalizare.
4. `audit/raport_audit.py` (export urmă de audit).
