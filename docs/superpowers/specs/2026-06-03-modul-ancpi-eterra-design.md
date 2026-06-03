# Modul ANCPI / e-Terra (conectivitate cadastrală) — Design

**Data:** 2026-06-03
**Status:** Draft (planificat)
**Context:** Sistemul 2 din specificația inițială („Conectivitate date externe") este parțial
implementat: **scraping portaluri** (discovery) ✅ și **indici BNR** (curs_bnr) ✅. Lipsește
componenta **ANCPI/e-Terra** — verificarea cadastrală oficială a proprietății.

---

## 1. Problema

Identificarea proprietății (nr. cadastral, CF, suprafețe, proprietari, sarcini) se introduce manual
sau se extrage din documente. Verificarea împotriva **registrului oficial ANCPI/e-Terra** ar
confirma datele și ar reduce riscul de eroare/fraudă.

## 2. Scop

Modul care interoghează ANCPI/e-Terra (în limita accesului disponibil) pentru:
- confirmarea **identificării imobilului** după nr. cadastral / CF;
- **suprafețe** și **categorie de folosință** oficiale;
- (dacă e disponibil) starea sarcinilor/ipotecilor.

**Non-goal:** obținerea de extrase oficiale cu valoare juridică (rămâne procedura ANCPI a
evaluatorului); ocolirea regulilor de acces.

## 3. Dependență critică: ACCES

e-Terra/ANCPI necesită **cont și drepturi** (instituțional / abonament). Acest spec presupune un
**client injectabil** care abstractizează accesul (API oficial dacă există, altfel
confirmare/căutare în limita permisă). Fără acces autorizat, modulul rămâne neimplementabil — de
clarificat cu ANCPI. **Cel mai mare risc.**

## 4. Arhitectură (modul nou `ancpi/`)

```
src/evaluare/ancpi/
  client.py        # acces e-Terra (injectabil) — abstractizeaza mecanismul de acces
  models.py        # ImobilANCPI (cadastral, CF, suprafete, categorie, sarcini)
  verificare.py    # compara datele introduse/extrase cu cele oficiale -> diferente semnalate
```

- **Client injectabil** (ca `fetcher`/`NarrativeClient`) → testabil fără rețea.
- **Confidențialitate:** datele rămân locale; nu se trimit la AI.

## 5. Integrare

- La Pas 1 (identificare): buton **„Verifică în e-Terra"** după nr. cadastral/CF → afișează datele
  oficiale și **diferențele** față de cele introduse (suprafață, categorie).
- Rezultatul (confirmat) intră în termenii de referință / descrierea juridică, marcat ca sursă
  oficială.

## 6. Riscuri / dependențe
- **Acces ANCPI (blocant).**
- **Termeni de utilizare / GDPR** ai e-Terra.
- **Disponibilitatea API** — dacă nu există API, modulul se limitează la verificare manuală asistată.

## 7. Pași de implementare (rezumat)
1. Clarificare acces e-Terra — **precondiție**.
2. `ancpi/client.py` (injectabil) + `ancpi/models.py` — TDD cu client fals.
3. `ancpi/verificare.py` — comparare date introduse vs oficiale, semnalarea diferențelor.
4. Wizard Pas 1: „Verifică în e-Terra" + afișarea diferențelor.
