# Modul Ingestie documente (OCR + vision-language) — Design

**Data:** 2026-06-03
**Status:** Draft (planificat)
**Context:** Sistemul 1 din specificația inițială. Astăzi aplicația preia date din **anunțuri**;
documentele proprietății (carte funciară, releveu, plan de amplasament, certificat energetic) se
introduc manual de evaluator. Acestea conțin exact datele de identificare și fizice necesare.

---

## 1. Problema

Datele de intrare (suprafețe, nr. cadastral, CF, regim înălțime, an, încadrare energetică) sunt
introduse manual din documente PDF/scan. Ingestia automată ar reduce efortul și erorile de
transcriere.

## 2. Scop

Modul care **parsează documentele uzuale** și propune câmpuri pre-completate (de confirmat de
evaluator):
- **Carte funciară (extras CF):** nr. cadastral, nr. CF, proprietari, suprafețe, sarcini/ipoteci.
- **Releveu:** arii (utilă, construită), compartimentare, niveluri.
- **Plan de amplasament și delimitare:** suprafață teren, vecinătăți, deschidere/front.
- **Certificat de performanță energetică (CPE):** clasa energetică, consum.

**Non-goal:** validarea juridică a documentelor (rămâne a evaluatorului); semnătura digitală.

## 3. Arhitectură (modul nou `ingestie/`)

```
src/evaluare/ingestie/
  ocr.py           # extragere text (OCR) din PDF/imagine scanata
  vlm.py           # extragere structurata cu model vision-language (campuri -> valori), client injectabil
  extractoare.py   # parsere per tip document (CF, releveu, plan, CPE) cu regex + VLM
  models.py        # DateExtraseCF, DateReleveu, DatePlan, DateCPE
```

- **Două straturi:** OCR (text) pentru documente text-based; **VLM** (vision-language) pentru
  layout/tabele/scanuri unde OCR pur eșuează. Clientul VLM e **injectabil** (ca `NarrativeClient`),
  testabil fără rețea.
- **GDPR:** documentele conțin date personale → **anonimizare înainte** de orice apel la model
  extern (reutilizează `report/anonymizer.py`), demascare locală.

## 4. Integrare

- Pas/secțiune în wizard: **„Încarcă documente"** → câmpurile extrase pre-completează Pas 1/2
  (identificare + proprietate), marcate „[EXTRAS din document — verifică]".
- Documentele încărcate intră oricum în **Anexa 3** a raportului (mecanism existent).
- Reutilizează adnotările de proveniență: câmpurile auto-extrase apar ca `[EXTRAS]`.

## 5. Riscuri / dependențe

- **Acuratețe OCR/VLM** pe scanuri de calitate slabă → design „propune, nu decide"; evaluatorul
  confirmă fiecare câmp.
- **Cost/limită model VLM** → opțional, activabil; fallback la introducere manuală.
- **Diversitate de formate** CF/releveu între OCPI-uri → parsere tolerante + VLM ca plasă de
  siguranță.

## 6. Pași de implementare (rezumat)
1. `ingestie/models.py` (date extrase per tip document) — TDD.
2. `ingestie/ocr.py` (text din PDF/imagine) + fixturi.
3. `ingestie/vlm.py` (client injectabil) + `extractoare.py` (CF/releveu/plan/CPE).
4. Wizard: „Încarcă documente" → pre-completare câmpuri (marcate EXTRAS), cu anonimizare la apel.
