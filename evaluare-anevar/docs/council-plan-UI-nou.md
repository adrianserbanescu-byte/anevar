# Council pe „planul pentru noul UI" — comparație cu planul meu + ce adopt

> Rezultatul council-ului adițional cerut de Adi: fiecare model a dat PLANUL LUI individual pentru
> noul UI. Mai jos: **agregatul lor**, **comparația cu planul meu** ([`plan-UI-nou-Claude.md`](plan-UI-nou-Claude.md)),
> și **ce preiau** în planul de dezvoltare. Leaderboard: gpt-5.1 & sonnet-4.5 la egalitate #1; gemini #3; grok #4.
> Brieful trimis: [`council-brief-UI-nou.md`](council-brief-UI-nou.md). Actualizat: 2026-06-06.

## 1. Agregatul council-ului (consens puternic, 4 modele)
1. **Folder = sursa de adevăr; SQLite = doar index/cache.** (identic cu noi)
2. **Workspace:** header fix (status Draft/De-verificat/Asumat/Generat + adresă) + 5 tab-uri
   `[Raport][AML][GDPR][Audit][Anexe]` + sub-tab-uri Raport `[Proprietate][Comparabile][Calcul][Generează]`.
   (identic cu ce am construit)
3. **Lock la checkpoint-ul de asumare** → ireversibil + timestamp + **hash SHA256 al folderului** (audit
   inalterabil); de-lock cu motiv + audit trail. + un fișier `.lock` pentru deschidere concurentă → read-only.
4. **Calcul→Generează:** cele 8 garduri ca bannere de alertă; «Generează» BLOCAT până se sting alertele
   roșii critice + bifa de asumare. (identic cu planul meu; bifa deja implementată)
5. **Descoperire integrată** split-screen/drawer în Comparabile (caută stânga → trage/importă în grilă
   dreapta) + fallback manual obligatoriu.
6. **Anexa foto = P0, NU comercial** — UNANIM: „produsul e nelansabil fără poze; banca respinge raportul;
   SEV o cere". Gating doar pe VOLUM (free: 10-20 poze), nu pe existență.
7. **Stack:** HTMX + Alpine.js (NU React/Node) ca să nu umfle PyInstaller. (noi: Jinja + JS vanilla — aceeași filozofie)
8. **Retragere UI vechi în 3 faze:** T+0 banner „Legacy" → T+60 redirect + migrare automată → T+90 ștergere cod.
9. **Riscuri:** desincronizare folder↔UI (file watcher), parser portaluri fragil (fail-safe + import manual),
   AI/GDPR (masking regex pe câmpul de text), lock fără undo (confirmare + 3 verificări pre-lock).
10. **Dependențe:** `python-docx` să lipească zeci de poze fără să strice paginarea ANEVAR; schema pt hash lock; script migrare.

## 2. Comparație: planul meu vs. council
| Temă | Planul meu | Council | Verdict |
|------|-----------|---------|---------|
| Folder=adevăr, SQLite index | ✅ | ✅ | **Acord total** (deja implementat) |
| 5 tab-uri + 4 sub-tab-uri | ✅ | ✅ | **Acord total** (deja implementat) |
| Lock la prima generare/asumare | ✅ | ✅ + **hash SHA256 folder** + fișier `.lock` | **Adopt hash + .lock** (le adăugam) |
| Calcul→Generează gated + etichetare AI/determinist | ✅ | ✅ (gardurile sting Generează) | **Acord**; adopt „alertele roșii sting Generează" |
| Descoperire în Comparabile | ✅ (sub-tab) | ✅ (split-screen/drawer + fallback) | **Adopt split-screen + fallback manual** |
| Anexă foto | „gated comercial = decizia ta" | **P0, SEV o cere, doar volum gated** | **Diverg — escaladez la tine (vezi §4)** |
| Retragere UI vechi 3 faze | ✅ | ✅ (T+0/T+60/T+90 + migrare) | **Acord** |
| Conținut tab-uri (status inline + detaliu la click) | ✅ | ✅ (status cards + lazy) | **Acord** (din Q2 Topic 6) |
| Stack | Jinja + JS vanilla | HTMX + Alpine | **Păstrez vanilla** (echivalent, fără dependență nouă) |

**Unde council-ul mă întrece (preiau):** hash SHA256 al folderului la asumare (audit inalterabil, aliniat SEV);
fișier `.lock` + read-only la deschidere concurentă; file-watcher pentru editări manuale în Explorer;
descoperirea ca split-screen (nu doar sub-tab). **Unde sunt mai conservator decât council:** anexa foto — eu am
respectat decizia ta de gating comercial; council-ul spune ferm că e cerință SEV, nu premium (escaladare, nu o decid eu).
**Unde council-ul greșește/exagerează:** HTMX/Alpine ca „dependență critică" — e preferință, nu necesitate;
noi avem deja dinamism cu JS vanilla fără să umflăm exe-ul. „pywin32" (gemini) — nu-l folosim, `python-docx` e suficient.

## 3. Ce preiau în planul de dezvoltare (autonom, fără decizie)
- [ ] **Hash SHA256 al folderului dosarului la asumare** + stocat în `dosar.json` (`asumat_la`, `hash`) — audit inalterabil.
- [ ] **Fișier `.lock` per dosar** la deschidere + mod read-only dacă e deschis în altă parte.
- [ ] **Descoperirea ca split-screen în sub-tab-ul Comparabile** (caută → bifează → importă în grilă) + fallback manual.
- [ ] **OLX downgrade explicit** la scor (suprafață lipsă) + flag „⚠ completează suprafața" + validare roșie la Generează (din Q3).
- [ ] **Localități user** în `localitati_custom.json` (lângă date), merge runtime, slug auto-transliterat + override + „Testează URL" (din Q3) — DAR e marcat „de brainstormat" de tine, deci doar pregătesc, nu activez fără OK.

## 4. Ce ESCALADEZ la tine (decizie de produs — vezi BLOCAT-pe-Adi.md)
- **Anexa foto/scanuri: council UNANIM spune că e cerință SEV 2025, nu feature comercial** — gating-ul total face
  aplicația „nelansabilă pentru rapoarte reale". Recomandarea convergentă: **implementeaz-o ACUM**, gated doar pe
  VOLUM (ex. 10-20 poze gratis). Tu ai decis-o comercială; te rog confirmă dacă o re-încadrăm ca P0 de conformitate.
- **Regenerare AI (Q2 Topic 3):** implicit **TEMPLATE** (păstrează vocea evaluatorului, actualizează valorile) +
  diff vizual per capitol + override per capitol. Confirmă conceptul înainte să-l construiesc.
- **Import asemănător (Q2 Topic 4):** matrice în config (DIFERIT/GHIDARE/PARTICULARIZAT) + **detecție PII la import**
  (regex CNP/adresă → avertisment) + „doar TEXT, nu valori". Confirmă matricea implicită.
