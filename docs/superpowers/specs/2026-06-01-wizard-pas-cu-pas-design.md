# Wizard pas-cu-pas (pornind de la o adresă) — Design

**Data:** 2026-06-01
**Status:** Draft pentru review
**Context:** Un flux ghidat care înlocuiește formularul uriaș de evaluare cu 5 pași, pornind de la
o singură adresă. Construit peste tot ce există (Planurile 1-4 + modulul Descoperire).

---

## 1. Scop și principiu

Evaluatorul tastează **o adresă o singură dată**; aplicația îl ghidează prin 5 pași și
reutilizează adresa pentru (a) metadatele raportului și (b) zona de căutare a comparabilelor.

**Limitare onestă, asumată:** adresa NU poate completa datele fizice ale casei (suprafețe, an,
finisaje, încălzire) — acestea vin din actele cadastrale și se introduc manual (viitor: OCR
cadastral). Adresa bootstrap-ează doar locația/zona și metadatele.

---

## 2. Decizii confirmate

| Dimensiune | Decizie |
|---|---|
| Starea wizard-ului | În browser (JS) + `localStorage` (supraviețuiește refresh-ului; NU dosar SQLite) |
| Derivare zonă din adresă | LLM extrage `{județ, localitate}` din adresă; evaluatorul confirmă |
| Backend nou | Un singur endpoint: `POST /api/zona`. Restul reutilizează endpoint-urile existente |
| Pagina | `GET /wizard` (poate deveni ulterior pagina principală) |

---

## 3. Pașii wizard-ului

```
Pas 1 — Adresă & lucrare
   Intrare: adresă + client, scop, evaluator, date.
   Acțiune: la „Înainte", POST /api/zona(adresa) → {județ, localitate} (LLM) → pre-completate,
            evaluatorul confirmă/corectează.

Pas 2 — Proprietatea subiect
   Intrare: teren (suprafață) + construcție (Au, Acd, an referință, elemente cost, depreciere)
            + cele 5 atribute primare (an, stare 1-5, finisaj 1-4, încălzire, teren).
   [Nu se derivă din adresă — se introduc manual.]

Pas 3 — Comparabile
   Acțiune: „Descoperă" apelează AUTOMAT POST /api/descopera cu zona (Pas 1) + atributele
            subiectului (Pas 2) → listă rankată cu breakdown → evaluatorul bifează.
   Fallback: adăugare manuală (pret;suprafata) sau prin URL (POST /api/import-url).
   Rezultat: lista de comparabile selectate.

Pas 4 — Metodă & calcul
   Intrare: metoda (cost / piață / ponderată).
   Acțiune: POST /api/evaluare cu tot dosarul asamblat → valoarea finală + metoda.
   Afișare: valoarea + (opțional) breakdown-ul.

Pas 5 — Raport
   Acțiune: link descărcare GET /api/evaluare/{id}/raport.docx.
```

**Ordinea e obligatorie:** Descoperirea (Pas 3) are nevoie de atributele subiectului (Pas 2) ca să
rankeze după similaritate; fără ele ar fi doar o listă nerankată. De aceea adresa nu poate sări
direct la comparabile.

Bară de progres (1/5 … 5/5) + butoane „Înapoi/Înainte". Validare minimă per pas înainte de avans.

---

## 4. Componenta nouă de backend: `POST /api/zona`

- **Intrare:** `{ "adresa": "Str. Exemplu nr.10, Otopeni, Ilfov" }`
- **Ieșire:** `{ "judet": "ilfov", "localitate": "otopeni" }`
- **Mecanism:** clientul LLM injectat (același ca la narativ/extracție) extrage `{județ,
  localitate}` din adresă — ancorat în text, fără invenție. JSON validat.
- **Fallback fără cheie:** parsare simplă (ultimele 2 segmente despărțite de virgulă →
  localitate, județ), pe care evaluatorul oricum o confirmă. Niciodată blocant.
- Reutilizează `create_app(..., client=...)` (clientul deja injectat).

---

## 5. Frontend (starea în browser)

- O singură pagină `wizard.html`; pașii sunt secțiuni comutate din JS (un singur pas vizibil).
- Stare: un obiect JS acumulat pe pași, **serializat în `localStorage`** la fiecare „Înainte"
  (resume după refresh). Buton „Reset dosar" golește starea.
- La final, obiectul se mapează exact la `EvaluationInput` existent → POST /api/evaluare.
- Reutilizează integral endpoint-urile: `/api/zona` (nou), `/api/descopera`, `/api/import-url`,
  `/api/evaluare`, `/api/evaluare/{id}/raport.docx`.

---

## 6. Conectarea cu ce există

- **Date:** comparabilele bifate la Pas 3 devin liniile `comparables` din `EvaluationInput`
  (prin câmpurile pret/suprafata), exact ca azi. Zero schimbare în motorul de calcul.
- **Subiect → descoperire:** atributele de la Pas 2 alimentează `SubjectProfile` la Pas 3.
- **Adresă → zonă + metadate:** o intrare, două folosințe.
- Formularul „monolit" existent (`/`) rămâne disponibil ca alternativă (nu îl ștergem).

---

## 7. Non-goals

- Dosar persistent în SQLite reluabil între sesiuni (rămâne `localStorage`).
- Auto-completarea datelor fizice din adresă (imposibil fără cadastru/OCR).
- Geocodare/hartă (eventual ulterior).
- Înlocuirea formularului monolit (coexistă).

---

## 8. Pasul următor

Spec → plan de implementare. Nucleul de construit: endpoint-ul `POST /api/zona` (TDD cu client
fals) + pagina `wizard.html` cu cei 5 pași și orchestrarea în JS (testat că pagina încarcă și că
endpoint-ul zona răspunde). Integrarea cu endpoint-urile existente nu necesită modificări la ele.
