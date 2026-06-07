# Checklist livrare `.exe` evaluare-anevar

> Pre-rebuild + livrare către tester / evaluator / piață. Customizat pe procesul **single-`.exe`
> Windows desktop** (nu server deploy). Bazat pe `engineering:deploy-checklist`.
>
> **Cum se folosește:** copiezi secțiunea relevantă în fișierul de release (`docs/release-NN.md`)
> și bifezi pe măsură. Versionează deciziile de skip (nu lăsa neglijent).

---

## 0. Identificare release

- **Versiune:** ……… (incrementează `pyproject.toml` + `version_info.txt` Windows)
- **Data:** ………
- **Build maker:** ……… (Adi local + GitHub Actions CI)
- **Destinatar:** ☐ tester intern · ☐ 1-3 evaluatori beta · ☐ pilot bancă · ☐ piață deschisă
- **Tip release:** ☐ patch (fix bug) · ☐ minor (feature) · ☐ major (UI/format raport)

---

## 1. Pre-Build (verificări de mediu)

### 1.1 Cod & dependențe

- [ ] **`git status` curat** pe `master` — nu există modificări locale neaschimbate
- [ ] **`git pull` rulat** — sincronizat cu origin (autonomous loop nu rulează lucruri în paralel)
- [ ] **`scripts/lock.py --check` verde** — `requirements.lock` reflectă `pyproject.toml`
  > ⚠ După orice modificare în `pyproject.toml`, regenerezi cu `python scripts/lock.py` și
  > commit-uiești AMBELE fișiere ÎMPREUNĂ. Loop-ul autonom uneori uită pasul lock.
- [ ] **Pyproject pin-uri verificate manual:**
  - `Pillow>=11,<13` (binarul `_avif` din Pillow 12 corupe arhiva PKG → constrângere strictă)
  - `urllib3>=2.7.0` (PYSEC-2026-141/142)
  - `idna>=3.15` (CVE-2026-45409)
- [ ] **`pip-audit -r requirements.lock`** → 0 vulnerabilități
  > Dacă apare ceva nou: rulează `/dependency-audit` skill pentru evaluare + decide stop/go.

### 1.2 Cod & teste

- [ ] **CI verde pe HEAD** — verifică ultima rulare GitHub Actions (windows-latest, py3.12)
- [ ] **`ruff check src tests scripts`** — fără warnings
- [ ] **`pytest -q --cov=evaluare --cov-report=term-missing`** — toate verzi + `fail_under=90`
- [ ] **E2E rulat local** — `python -m playwright install` apoi suita e2e
- [ ] **Audit module verificat** — `pytest tests/test_audit*.py` (jurnal hash-chain integritate)
- [ ] **Nu ai modificat AML în foreground** — vezi protocol: AML/legal = bucket C, doar loop autonom
  > Verifică: `git log --oneline HEAD~5..HEAD -- src/evaluare/aml/` — modificările trebuie să fie
  > revert-uri sau pending-jurist, nu editare directă text juridic.

### 1.3 Documentație & livrabile

- [ ] **CHANGELOG.md actualizat** cu intrare pentru versiune (rulează `docs:changelog` skill pe `git log v(N-1)..HEAD`)
- [ ] **README.md cere pre-rec actualizate** (versiune Python, dependențe noi)
- [ ] **Sinteza pentru tester** dacă livrezi pachet: `packaging/CITESTE-MA.txt` adaptat la noul release

---

## 2. Build `.exe` (pasul executiv)

- [ ] **Mediu curat:** `.venv\Scripts\activate` + `pip install -r requirements.lock` (nu globalul)
- [ ] **`python scripts/build.py`** rulat (`PyInstaller` → `dist/evaluare-anevar.exe`)
- [ ] **Verifică dimensiune:** trebuie ~50 MB (creștere bruscă > 10 MB = pachet nedorit bundled — investighează)
- [ ] **Metadate Windows verificate:** drag pe `.exe` → Properties → Details → versiunea, autor, descriere
- [ ] **Siglă vizibilă în taskbar** (commit `cb45edd`: casă albă pe albastru)

---

## 3. Smoke-test (post-build, pre-livrare)

### 3.1 Pe mașina de build

- [ ] **Dublu-click `.exe`** → pornește server local (verifică terminal/log) + browser deschis automat
- [ ] **Pas SmartScreen documentat:** „Windows protected your PC" → **More info → Run anyway**
  > După `§B.6` (cert code-signing) → pas eliminat. Până atunci, instruiește testerul.
- [ ] **Flow happy-path** (≤ 10 minute):
  - creează cont
  - creează dosar (fie scratch, fie import .docx)
  - completează cap-coadă: identitate → date proprietate → comparabile → grilă → calcul → raport
  - download `.docx` raport — verifică deschidere în Word (formatare bună, nu erori)
  - **AML:** flow KYC + decizie + RTN/RTS (PDF-uri generate corect, semnături în loc)
  - **Audit trail:** /api/dosar/{uid}/audit.txt — hash-chain consistent
  - **Backup:** /api/backup-dosare.zip — descarcă, deschide, verifică structura

### 3.2 Pe Win10/11 curat (VM sau alt PC)

- [ ] **Copiază `.exe` izolat** (fără Python pe sistem) — verifică că pornește fără dependențe externe
- [ ] **Test pe Windows 8.1** (dacă target-ul include) sau notează „nu mai suportat" în release notes

### 3.3 Verificări specifice ANEVAR/SEV

- [ ] **Raport `.docx` conform GEV 630:** descrierea proprietății include utilități, regim urbanistic,
      act de proprietate, cale de acces, sarcini CF (vezi commits `016915c`, `6e1fbe8`, `990d410`)
- [ ] **Sursă tipului valorii citată:** SEV 102 referențiat (commit `40f142b`)
- [ ] **Alerte prudențiale GEV 520:** grila de ajustări declanșează la 25%
- [ ] **Diacritice OK:** verifică nume/localitate cu „ș/ț/ă/â" în raport (ANCPI, BNR)

---

## 4. Livrare

### 4.1 Pachet pentru tester / evaluator

- [ ] **Zip:** `evaluare-anevar-vX.Y.zip` cu `.exe` + `CITESTE-MA.txt` + raport demo + (opțional) feedback form
- [ ] **Disclaimer atașat:** „Beta, nu pentru predare la bancă/instanță fără semnătură evaluator senior"
- [ ] **Email/Slack handover:** ce s-a schimbat (extrage din CHANGELOG), ce ai nevoie să teste

### 4.2 Pilot bancă (când va fi cazul — §A.5)

- [ ] **Validare prealabilă cu departamentul Risc/IT al băncii** (NU livra direct la operațional)
- [ ] **20-30 dosare reale** pentru pilot (nu 2-3 ad-hoc)
- [ ] **Acord scris** privind clauze AI, semnătură evaluator, lichidare anti-AI dispută

### 4.3 Piață deschisă (§B / §E — când conturi+cert sunt gata)

- [ ] **Cert code-signing aplicat** (§B.6 ~150-300€/an) → SmartScreen dispare
- [ ] **Landing page + checkout activ** (Stripe + OAuth, vezi §B.7)
- [ ] **Master-admin tooluri ready** (Supabase Studio sau panou custom, §E.22)
- [ ] **Polița asigurare răspundere profesională ANEVAR** verifică acoperă AI (§A.4)

---

## 5. Post-Livrare (monitorizare)

- [ ] **Inbox feedback monitorizat 48h** — verifică widget feedback din UI + email
- [ ] **Cost-tracker verificat după 7 zile** — `~/.claude/cost-log.jsonl` agregat
- [ ] **No-regression confirmation** după 1 săptămână — întreabă testerul activ
- [ ] **Memplan updated:** decizii noi/risk-uri în `.memplan/decisions/log.mem`,
      tasks completate marcate `status=done`

---

## 6. Rollback (când lucrurile se duc rău)

### Trigger-uri rollback

- ☐ **Crash la pornire** raportat de 2+ testeri
- ☐ **Date corupte** în dosar (`dosar.json` ilizibil, raport `.docx` gol)
- ☐ **PII leak** (parametri în URL, log-uri, sau în `.docx` generat)
- ☐ **Calcul greșit** (regresie pe abordare cost/comparație/venit)

### Procedură

1. **Notifică imediat** testerul/evaluatorul: „NU folosi `vX.Y`, rămâi la `vX.Y-1`"
2. **`git revert <commit-livrare>`** + rebuild rapid `.exe` cu versiunea anterioară
3. **Postmortem în 24h** — adaugă în `.memplan/memory/failures.mem` cu cauză + fix
4. **NU șterge .zip-ul stricat** — păstrează pentru analiză + scuze documentate

---

## Note tehnice

- **Conformitate Pillow:** NU upgrada peste 12.x — `_avif` corupe arhiva PKG (incidentul tău documentat)
- **Lock identitate `dosar.json`:** după ce Adi confirmă §J.34 + ADR-003 → adaugă pas „verifică
  jurnalul de modificări identitate" în smoke-test
- **AI gateway:** după ADR-004 → pas „verifică quota AI online" + „fallback la text-șablon
  funcționează când API down"

---

*Generat: 2026-06-07 — skill `engineering:deploy-checklist` aplicat pe contextul `evaluare-anevar`.*
*Sursă unică de adevăr pentru livrare. Modifică doar prin PR + review (NU live în prod).*
