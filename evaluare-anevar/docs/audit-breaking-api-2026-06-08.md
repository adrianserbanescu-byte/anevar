# Audit #5 — Breaking REST API Change Report

Comparing: `6150190` (pre-redesign discovery) → `HEAD` (`03dacf1`) | 2026-06-08 | sesiunea B
Route files changed: 5 (`curent.py`, `descoperire.py`, `evaluare.py`, `pagini.py`) + `schemas.py`
Verificat automat: `git diff` pe routere — **0 endpoint-uri eliminate (`- @router`)**, **0 chei de răspuns
eliminate (`- "key":`)**, **0 semnături de rută schimbate**.

---

## Summary

| Endpoint | Change | Severity | Client action |
|----------|--------|----------|---------------|
| `POST /api/descopera` | Response field **added**: `candidati[].axe`, `candidati[].poza` | — (non-breaking) | Opțional: consumă noile câmpuri |
| `GET/POST /api/descopera/config-ponderi` | Endpoint **nou** | — (non-breaking) | Opțional |
| `POST /api/descopera`, `/api/descopera-teren` | Request: `max_candidati` default **8 → 20** | LOW (behavioral) | Clienții care OMIT câmpul primesc până la 20 (nu 8) |
| `POST /api/descopera` | Request field **added**: `tip_activ` (opțional) | — (non-breaking) | — |
| `POST /api/descopera` | `candidati[].atribute[].pondere`: **int → float** | LOW (type widening) | JSON `5` → `5.0`; consumatorii JS îl tratează identic |
| `POST /api/dosar/{uid}/*` | uid non-UUID → **404** (era 500 / path-traversal) | — (îmbunătățire SEC-1) | Clienții legitimi trimit UUID-uri valide → neafectați |

**Total breaking: 0** | Total non-breaking/aditive: 5 | Note behavioral/type: 2

---

## Breaking Changes

**None.** Niciun câmp/endpoint eliminat, redenumit sau cu metodă/tip incompatibil schimbat.

---

## Note (non-breaking, dar de documentat)

### 1. `max_candidati` default 8 → 20  [LOW · behavioral]
`schemas.py` (DescoperaRequest, DescoperaTerenRequest). Contractul e neschimbat (câmp opțional); doar
*default-ul* la omitere s-a ridicat. Impact real: UI-ul trimite mereu valoarea explicit (1–50); extensia
de browser **nu** apelează `/api/descopera` (doar `/api/anunturi-importate`). Deci impact practic = zero.

### 2. `atribute[].pondere` int → float  [LOW · type widening]
`profiles.py:AttributeBreakdown.pondere`. Necesar pentru robustețe (ponderile editabile pot fi non-întregi
fără a crăpa scorarea). Singurul consumator = `descoperire.html` (JS, tolerant: `5.0` se randează „5").
**Nu se revertează** — ar reintroduce riscul de crash pe override-uri fracționare. Opțional (cosmetic):
un field-serializer care emite int la valori întregi; nerecomandat (over-engineering pe un non-issue).

### 3. SEC-1 — `/api/dosar/{uid}/*` → 404 pe uid non-UUID  [îmbunătățire]
Înainte: uid nevalidat → 500 sau path-traversal (rmtree în afara bazei). Acum: `_cale()` validează UUID →
404. Nu afectează clienții legitimi (trimit UUID-uri valide).

---

## Recommended next steps

- **Nimic de fixat** — redesign-ul API discovery (config-ponderi / c.axe / c.poza / tip_activ / max20) e
  **backward-compatible** (pur aditiv). Politica „implementează fix-urile pe măsură" → niciun fix necesar la #5.
- Dacă pe viitor apare un consumator API **strict-tipat** (nu JS) al `/api/descopera`, reconsideră nota #2
  (pondere float) — momentan irelevant.
- Recomand un **tag de versiune** (ex. `v0.2.0`) la următoarea integrare pe master, ca viitoarele audituri
  breaking-API să aibă un baseline curat (acum nu există tag-uri → baseline ales manual).
