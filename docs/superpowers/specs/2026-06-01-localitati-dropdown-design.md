# Adresă cu dropdown județ + localitate — Design

**Data:** 2026-06-01
**Status:** Draft pentru review
**Context:** Îmbunătățire a Pas 1 din wizard: în loc de adresă free-text + extracție LLM, folosim
**dropdown-uri pentru județ și localitate** cu valori (slug-uri) identice cu site-urile imobiliare,
plus free-text pentru restul adresei. Construit peste wizard-ul existent.

---

## 1. Scop și motivație

Județul și localitatea **construiesc URL-ul de căutare** a comparabilelor (ex.
`imobiliare.ro/vanzare-case-vile/judetul-ilfov/otopeni`). Dacă valoarea nu se potrivește exact cu
slug-ul site-ului, căutarea eșuează. Dropdown-urile cu slug-uri pre-validate **garantează potrivirea**
și **elimină dependența de LLM** (extracția `/api/zona`) pentru câmpurile critice.

Județ + localitate sunt astfel **identificate explicit** și folosite direct în matching-ul cu
anunțurile similare. Restul adresei (stradă, număr) rămâne free-text, doar pentru raport.

---

## 2. Decizii confirmate

| Dimensiune | Decizie |
|---|---|
| Acoperire localități | **Toate** (orașe + comune), din lista administrativă |
| Sursă date (build o singură dată) | `virgil-av/judet-oras-localitati-romania` (confirmat accesibil) |
| Slug | Generat prin normalizare (lowercase, fără diacritice, spații/special → cratimă) |
| Actualizare | Statică în aplicație; reîmprospătată **on-request** (rulezi scriptul de build) |
| Override | Opțiune „altă localitate (scriu)" → free text, pentru cazurile rare de slug diferit |
| LLM `/api/zona` | Nu se mai folosește în wizard pentru județ/localitate (rămâne disponibil, dar deterministe = dropdown) |

---

## 3. Datele

- **Build (o singură dată, reîmprospătabil):** un script descarcă JSON-ul sursă, normalizează și
  salvează `src/evaluare/data/judete_localitati.json` în formatul:
  ```json
  {
    "judete": [{"nume": "Ilfov", "slug": "ilfov"}, ...],          // 42, ordonate alfabetic
    "localitati": {
      "ilfov": [{"nume": "Otopeni", "slug": "otopeni"}, {"nume": "Corbeanca", "slug": "corbeanca"}, ...],
      ...
    }
  }
  ```
- Fișierul e **inclus în aplicație** (commis în git, împachetat în .exe). Runtime-ul **nu** descarcă
  nimic.
- **Slug normalizare:** `lowercase` → NFKD strip diacritice → orice secvență non-alfanumerică → o
  cratimă → trim cratime. „Baia de Arieş" → `baia-de-aries`.

---

## 4. Backend

- Modul `evaluare/localitati.py`: încarcă `judete_localitati.json`; expune `judete()` și
  `localitati(judet_slug)`.
- Endpoint `GET /api/localitati`: întoarce structura completă (≈ câteva sute KB, o singură cerere la
  încărcarea paginii). Frontend-ul cascadează client-side (fără alte cereri).
- Scriptul de build `scripts/build_localitati.py` (rulat manual la nevoie) regenerează fișierul.

---

## 5. Frontend (Pas 1 wizard)

```
Județ:      <select>  ← populat din /api/localitati (42, alfabetic). value = slug
Localitate: <select>  ← cascadat la schimbarea județului. value = slug
            + opțiune „— altă localitate (scriu) —" → afișează un input text (slug manual)
Stradă, număr, bloc etc.: <input free text>
```

- La „Descoperă" (Pas 3): se folosesc **slug-urile** județ + localitate direct în `/api/descopera`.
- Adresa pentru raport = compunere: `{stradă text}, {Localitate nume}, {Județ nume}`.
- `localStorage` salvează selecțiile (slug + nume) ca până acum.

---

## 6. Integrarea cu ce există

- Înlocuiește cele 4 câmpuri din Pas 1 (`adresa` free-text + `judet`/`localitate` text + apel
  `/api/zona`) cu: dropdown județ + dropdown localitate + free-text restul adresei.
- `/api/descopera` rămâne neschimbat (primește deja `judet`, `localitate`).
- `/api/zona` (LLM) rămâne în cod pentru formularul monolit, dar wizard-ul nu îl mai apelează.
- Restul wizard-ului (Pași 2-5) neschimbat.

---

## 7. Non-goals

- Tragerea dinamică a listelor la runtime (rămâne statică, reîmprospătată manual).
- Liste pe sectoare/cartiere (doar județ + localitate).
- Eliminarea `/api/zona` (rămâne pentru formularul monolit / compatibilitate).

---

## 8. Pasul următor

Spec → plan. Pași: (1) script build + generare `judete_localitati.json` din sursă; (2) modul
`localitati.py` + endpoint `GET /api/localitati` (TDD); (3) modificarea Pas 1 din `wizard.html`
(dropdown-uri cascadate + override + free-text rest); (4) verificare + rebuild .exe.
