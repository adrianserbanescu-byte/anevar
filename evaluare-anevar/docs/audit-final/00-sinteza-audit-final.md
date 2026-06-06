# Sinteză audituri finale (securitate · buguri/eșecuri silențioase · datorie tehnică · acoperire teste)

> 4 audituri paralele pe starea CURENTĂ (app desktop offline ANEVAR, post-recuperare paritate UI + conformitate).
> Detalii: [`security.md`](security.md) · [`bugs-silent.md`](bugs-silent.md) · [`tech-debt.md`](tech-debt.md) · [`test-coverage.md`](test-coverage.md).
> Bucket: A=îl fac eu (cod sigur) · B=evaluator · C=jurist. Actualizat: 2026-06-06.

## ✅ Bucket A — TOATE REZOLVATE (commit hardening, validate de council, +6 teste, 507 teste + 90 e2e)
> #5 dată (azi+confirm) · #2 gardă Host anti-rebind · #1 anti-SSRF · #3 grilă→422 · #4 pierdere date localități ·
> #7 creare r.ok · #8 CNP prefix 9 · #6 limită DoS 25MB. Tabelul de mai jos = starea inițială (istoric).

## 🔴 Bucket A — de reparat (confirmate de ≥1 audit, sigure, fără metodologie/legal) [REZOLVAT ↑]
| # | Problemă | Sursă | Fix | Sev |
|---|----------|-------|-----|-----|
| 1 | **SSRF** — `/api/import-url` + `/api/descopera` fac `requests.get` pe URL controlat de user, fără validare schemă/host, urmărind redirecturi (port-scan intern, 169.254.169.254) | sec #1 | validează schemă http/https + blochează IP privat/loopback/link-local + limitează redirecturi | Înalt |
| 2 | **CSRF / DNS-rebinding** — API local fără auth + fără verificare `Host` → orice site poate șterge dosare / declanșa import; rebind citește PII/backup | sec #2 | middleware care respinge `Host` ≠ localhost/127.0.0.1 | Înalt |
| 3 | **Grilă casă/teren → HTTP 500** la <3 comparabile (ValueError neprins); chirii prinde corect → 422 | bugs #2 + cov #1 | `try/except ValueError → 422` la grila-casa/teren (ca la chirii) | Înalt (bug) |
| 4 | **Pierdere date localități** — `/api/localitati` eșuat → `.catch()` gol → selecturi goale fără mesaj + auto-save suprascrie județ/localitate salvate cu „" | bugs #1 | catch cu mesaj + NU lăsa salveaza să suprascrie cu gol când populerea a eșuat | Înalt (bug, eu l-am introdus) |
| 5 | **Dată hardcodată** `||"2026-01-16"` injectată tăcut în meta dacă userul nu pune dată (risc juridic la garantare) | bugs #3 | fără fallback fix; cere data sau lasă gol/azi explicit | Mediu (legal-risk) |
| 6 | **DoS base64 nelimitat** la import-docx/ingestie/foto | sec #3 | limită de mărime payload | Mediu |
| 7 | **Creare dosar fără `r.ok`/try-catch** (`incepe.html`) → promisiune necatchuită, buton mut | bugs #4 | verifică `r.ok` (ca la import-docx) | Mediu |
| 8 | **Anonimizare CNP** ratează prefixul „9"; `beneficiar` trimis în clar la AI | sec #4 | extinde regexul CNP; (beneficiar=nume bancă, risc mic) | Scăzut/GDPR |
| 9 | **e2e incomplet** — nu apasă Generează / nu descarcă .docx (singurul livrabil nevalidat cap-coadă) | cov #2 | e2e: asumare → Generează → download → conținut | Test |

## 🟢 Bucket A — quick wins de calitate (impact mare / risc mic, din tech-debt)
- Unifică cele 3 grile JS (~75% duplicate, doar în `dosar.html`) într-un builder parametrizat.
- Extrage JS-ul din `dosar.html` în `_dosar.js` (cuplaj Jinja = doar UID/WIZARD/cont).
- Dedupe `audit.txt` între `curent.py` și `evaluare.py`.
> Refactor — valoros dar opțional; **bugurile/securitatea au prioritate**.

## 🔵 Confirmări pozitive (nu sunt probleme)
SQL parametrizat (zero injection) · bind loopback · fără eval/exec/subprocess/pickle · `md_to_html` escapează · `.env` NU în backup-zip · path-traversal mitigat (uuid+`.name`) · `TipValoare="lichidare"` NU e cod mort (folosit în raport) · coverage 94% (>90 gate).

## 🧭 Council (4 modele, chairman Gemini 3.1) — ce au RATAT auditurile (critic pre-lansare)
Validat: CSRF/DNS-rebind = risc REAL (rezolvat ↑); #5 dată = cea mai gravă (rezolvat ↑). NOI, de adăugat:
- **Jurnal de audit imuabil + LOCK la finalizare** — modificarea CNP/preț DUPĂ generare fără urmă = risc de fraudă
  (control ANEVAR/BNR). Motor de jurnal hash EXISTĂ (`audit/jurnal.py`); lipsește lock-ul la asumare → ADR-003 / BLOCAT #10.
- **Criptare la repaus** — SQLite + dosare + rapoarte = PII în clar pe disc. Minim: ghidaj BitLocker SAU disclaimer
  „protecția discului = responsabilitatea evaluatorului (operator de date)". → BLOCAT (Adi/jurist).
- **Igienă fișiere temp + loguri** — `%TEMP%` (OCR/.docx) + log la 500 pot scăpa PII. Verifică curățarea robustă la crash +
  loguri fără payload în producție. → Bucket A (de verificat/întărit).
- Zip-bomb/macro la import: limita de mărime (↑) ajută; docx/PDF nu se execută (doar parsate) → risc macro mic.

## ⏸️ Bucket B/C — escaladate (BLOCAT-pe-Adi)
Metodologie (alerte ajustări, declarație conformitate) = evaluator · AML/GDPR text + **criptare-la-repaus/disclaimer** = jurist ·
**lock identitate la finalizare** + anexe/preț/migrare = Adi. Minim lansare sigură (council): disclaimere juridice în raport →
alerte metodologice trasabile → lock identitate → gardă re-încadrare anexe.

## Stare: Bucket A = REZOLVAT (cod + teste + build). Bucket B/C + council-noi = BLOCAT-pe-Adi.md.
