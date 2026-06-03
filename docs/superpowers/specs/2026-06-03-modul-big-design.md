# Modul BIG (Baza Imobiliară de Garanții) — Design

**Data:** 2026-06-03
**Status:** Draft (planificat — LATER în roadmap)
**Context:** BIG este baza ANEVAR cu informații centralizate din rapoartele de evaluare realizate de
membri **pentru garantarea împrumutului**. GEV 520 §7 cere ca raportul cu utilizarea desemnată de
garantare să fie **înregistrat în BIG**, iar reutilizarea de alt creditor să modifice înregistrarea.
Sursă: anevar.ro/p/baze-de-date-big-si-bif.

---

## 1. Problema

Astăzi comparabilele vin din **portaluri publice** (oferte indicative). BIG conține **date reale de
tranzacționare/evaluare pentru garantare**, sursa cea mai autoritară pentru cazul nostru. În plus,
**înregistrarea raportului în BIG este o cerință GEV 520** pe care aplicația o menționează, dar nu o
realizează.

## 2. Scop

1. **Import comparabile din BIG** ca sursă primară (alături de descoperirea din portaluri), pentru
   grilele de casă și teren.
2. **Înregistrarea raportului în BIG** (utilizator desemnat de garantare) și gestionarea
   re-personalizării pentru alt creditor.
3. (Opțional) **Rapoartele statistice BIG** și **Indicele imobiliar ANEVAR** ca input pentru
   ajustarea „condițiile pieței (timp)".

**Non-goal:** reproducerea aplicației BIG; ocolirea regulilor de acces ANEVAR.

## 3. Dependență critică: ACCES

BIG necesită **autentificare de membru ANEVAR** și un mod de acces programatic (API sau export).
Acest spec presupune existența unuia dintre:
- un **API/serviciu** oferit de ANEVAR (preferat), sau
- **export/import de fișiere** (CSV/Excel) din interfața BIG.

Fără acces, modulul rămâne neimplementabil — de clarificat devreme cu ANEVAR/filiala. Acesta este
**cel mai mare risc** al modulului.

## 4. Arhitectură (modul nou `big/`)

```
src/evaluare/big/
  client.py        # autentificare + apeluri BIG (API) SAU import fisiere export
  models.py        # ComparabilBIG, InregistrareBIG
  import_comp.py   # mapare ComparabilBIG -> Comparable / LandComparable (grile)
  inregistrare.py  # construieste/transmite inregistrarea raportului in BIG
```

- **Client injectabil** (ca `NarrativeClient`/`fetcher`): permite testare fără rețea și înlocuirea
  ușoară a mecanismului de acces (API vs fișiere).
- **Confidențialitate:** datele din BIG se folosesc local; nicio dată personală nu pleacă spre AI.

## 5. Integrare cu aplicația

- La descoperire (casă/teren), o **sursă suplimentară „BIG"** lângă „imobiliare/storia", marcată ca
  **date de garantare reale** (prioritate față de oferte publice).
- La generarea raportului: pas de **înregistrare în BIG** cu utilizatorul desemnat; raportul reține
  ID-ul înregistrării; secțiunea GEV 520 confirmă înregistrarea (azi e doar text).
- Re-personalizare pentru alt creditor (GEV 520 §7) → actualizează înregistrarea.

## 6. Riscuri / dependențe

- **Acces ANEVAR (blocant)** — fără API/export autorizat, modulul nu se poate construi.
- **Reguli de utilizare BIG** — drepturi, GDPR, condiții de membru; necesită confirmare.
- **Stabilitatea interfeței** — dacă accesul e prin export manual, mapările se pot schimba.

## 7. Pași de implementare (rezumat)
1. Clarificare acces BIG cu ANEVAR (API vs export) — **precondiție**.
2. `big/client.py` (injectabil) + `big/models.py` — TDD cu client fals.
3. `big/import_comp.py` — mapare la `Comparable`/`LandComparable`; sursă „BIG" în descoperire.
4. `big/inregistrare.py` — înregistrarea raportului + ID în `ReportContext`; confirmare în GEV 520.
5. (Opțional) Indicele ANEVAR pentru ajustarea „condițiile pieței".
