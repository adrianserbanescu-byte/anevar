# Audit de securitate — P0#1 (2026-06-08)

> Cerere Adi (audituri prioritare). Lane C. Target: evaluare-anevar (Python/FastAPI,
> PII/AML/GDPR, upload .docx/PDF, generare documente, scraping portaluri, server local 127.0.0.1).
> Read-only. Unelte: grep patterns + pip-audit (172 pachete).

## Sumar

| Severitate | Nr |
|------------|----|
| Critical | 0 |
| High | 0 |
| Medium | 2 (SEC-1, SEC-2) |
| Low | 2 (SEC-3, SEC-4) |

Dependente: 0 CVE pe 172 pachete (pip-audit). Secrete: 0.

## SEC-1 [Medium-High] Path traversal pe operatiile de dosar
Categorie OWASP A01/A03 - dosare_fs.py (incarca/salveaza/sterge), rute /api/dosar/{uid}/...
uid din URL e folosit direct: baza()/uid/"dosar.json" (incarca), shutil.rmtree(baza()/uid) (sterge).
uid e generat ca uuid4() doar la CREARE; la citire/scriere/stergere vine din path-ul user FARA
validare. Un uid = ".." (sau encoded) urca in afara bazei. sterge() cu rmtree pe baza()/.. = date/
-> pierdere dosare + DB + backup.
FIX: valideaza uid ca UUID (uuid.UUID(uid) sau regex) la intrarea in dosare_fs sau in rute; 404 daca nu-i UUID.

## SEC-2 [Medium] XSS prin continut scrape-uit
Categorie OWASP A03 - descoperire.html:323,173, wizard.html, curent/dosar.html (JS)
Titlul si URL-ul anunturilor (din portaluri EXTERNE, necontrolate) sunt injectate in innerHTML si
href fara escaping: ${c.titlu}, href="${c.url}". Un anunt malitios cu img onerror in titlu, sau
href javascript:, executa JS in pagina evaluatorului (acces la localStorage: dosare, cont).
FIX: escapeHtml() pe valorile text inainte de innerHTML; valideaza URL (doar http/https) inainte de href.

## SEC-3 [Low-Medium] Lipsa protectie CSRF pe mutatii
Categorie OWASP A01 - POST-uri creeaza/sterge/salveaza dosar
App local accesibil din browser. Middleware doar_host_local respinge Host non-local, dar NU opreste
CSRF (browserul victimei trimite Host corect). O pagina web malitioasa -> fetch no-cors catre
127.0.0.1:8000/api/dosar/.../sterge -> mutatie/stergere. Amplifica SEC-1.
FIX: verificare Origin/Referer pe mutatii, sau token CSRF.

## SEC-4 [Low] PRAGMA cu f-string (non-issue)
db/storage.py:80 - f"PRAGMA user_version = {v}". v e int controlat din cod (versiune migrare), NU
input user; SQLite nu accepta bind params la PRAGMA. Sigur. Notat pentru completitudine.

## Curat (verificat, fara probleme)
- Secrete/credentiale hardcodate: 0 (.env.example = doar placeholdere)
- SQL injection: parametrizat (exceptie PRAGMA int = SEC-4)
- Command injection (shell=True/os.system/eval/exec): 0
- Deserializare nesigura: 0
- TLS verify=False: 0
- Jinja autoescape: ON; |safe doar pe continut de incredere (docs whitelist, iconuri, ornament cartus)
- Path traversal /documente/{slug}: IMPOSIBIL (slug = cheie de dict whitelist _PE_SLUG)
- SSRF scraping: scazut (domeniu portal fix in build_search_url)
- Dependente: 0 CVE (urllib3/idna deja pinned proactiv)

## Owner remediere
- SEC-1 (uid UUID): C sau B (atinge dosare_fs = shell ADR-003 al lui A -> coordonez cu A)
- SEC-2 (XSS scrape): C (lane UI; cuplat cu rollout step-2 JS)
- SEC-3 (CSRF): A (sistem/middleware)

---
## Status remediere (actualizat 12:49)
- **SEC-1** path traversal uid — ✅ **REZOLVAT** (B, commit 864c839): validare UUID `_cale(uid)` pe toate
  operațiile dosar + 404 pe uid invalid; verificare adversarială GO (0 bypass, 0 regresie); teste dedicate.
- **SEC-2** XSS scrape — ✅ **REZOLVAT**: descoperire.html + wizard.html (C, escapeHtml+urlSafe);
  dosar.html (A, commit 0ec2c3e, esc()+urlSig() pe randCand+randCoada + check Playwright cu payload malițios).
- **SEC-3** CSRF — la A (arhitectural, non-blocant pt MVP local).
- **SEC-4** PRAGMA — non-issue (notat).
- **Deps CVE / secrete** — 0.

**Concluzie:** ambele findings actabile (SEC-1, SEC-2) închise. Rămâne doar SEC-3 (CSRF, A, non-blocant).
