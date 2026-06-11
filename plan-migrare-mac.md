# Plan de migrare: Windows → Mac (proiect anevar + mediu Claude Code)

> Creat: 2026-06-11 · Orchestrat cu `/make-plan` · Cont: același Claude Max (login nou pe Mac, nimic de migrat la auth)
> Principiu: **sesiunile de lucru se migrează ULTIMELE** — totul altceva se pregătește din timp, fără downtime.
> Fiecare fază e autonomă: poate fi executată într-un chat nou, cu referințele de mai jos.

---

## Faza 0 — Constatări (descoperire, 2026-06-11) + decizii necesare

### Fapte verificate (surse: repo, ~/.claude, docs oficiale)

**Inventar de migrat (~3 GB total):**
| Componentă | Locație Windows | Mărime | Metodă migrare |
|---|---|---|---|
| Cod (1 worktree) | `anevar` (b/c/d ȘTERSE 2026-06-11 — A e pe agent work style, B–F desființate) | — | git clone |
| live-up.py (hook server live) | `C:\Users\adyse\anevar-mailbox\live-up.py` | mic | **NU e în git** → port + copiere (restul mailbox-ului = istoric, nu se migrează) |
| Date runtime app | `evaluare-anevar/live/date/` (+ `date/` în worktree) | <1 MB | copiere manuală (gitignored) |
| Transcripturi sesiuni anevar | `~/.claude/projects/C--Users-adyse-anevar/` | 437 MB, 43 jsonl | copiere + redenumire folder (ULTIMA) |
| Memorie auto (14 fișiere md) | `...C--Users-adyse-anevar/memory/` | mic | copiere cu transcripturile |
| claude-mem DB | `~/.claude-mem/` (db 24 MB + chroma 50 MB) | ~80 MB | install pe Mac + restore DB |
| Plugins (39) + marketplaces (6) | `~/.claude/plugins/` (1,39 GB) | — | **NU se copiază** → reinstalare declarativă |
| Skills user-level (182) | `~/.claude/skills/` | 15 MB | copiere directă (portabile) |
| settings + hooks | `~/.claude/settings.json`, `anevar/.claude/settings.local.json` | — | rescriere căi (5 hook-uri globale + 2 proiect) |

**Encoding sesiuni (verificat empiric pe 3 cazuri):** orice caracter non-alfanumeric → `-`.
`C:\Users\adyse\anevar` → `C--Users-adyse-anevar`; pe Mac `/Users/adi/claude/anevar` → `-Users-adi-claude-anevar`.

**Căi Windows hardcodate în cod (doar 3):**
- `anevar-mailbox/live-up.py:14` — `ROOT = Path(r"C:\Users\adyse\anevar\evaluare-anevar")` + pornește `.exe`
- `evaluare-anevar/scripts/export_chat.py:14` — cale `~/.claude/projects/...` hardcodată
- `evaluare-anevar/src/evaluare/report/pdf.py:26-27` — candidați soffice Windows, dar **include deja calea macOS** ✓

**Branch-uri nepushed (risc de pierdere):** `win7-build` (12 commits), `Fix-fuzz-deadline` (1), plus a9ced01, c2a4283, 7fe8496, 7058aec, bf36fe9.

**Capcane documentate:**
1. `cleanupPeriodDays` default 30 zile — la primul start pe Mac, transcripturile mai vechi de 30 zile se ȘTERG. Setează 365 ÎNAINTE de copiere.
2. Portabilitatea transcripturilor între mașini pe CLI e **nedocumentată oficial** (doar Agent SDK o garantează) → pilot obligatoriu (Faza 3.5).
3. `.credentials.json` NU funcționează pe Mac (Keychain) — login nou prin browser; nu seta `ANTHROPIC_API_KEY` (ar factura API în loc de Max).
4. claude-mem: oprește worker-ul înainte de copierea DB (altfel copie ruptă din `-wal`); NU copia `settings.json` (căi Windows); restore cross-OS nedocumentat → păstrează Windows-ul ca sursă de adevăr până la validare.
5. **`.exe` se construiește DOAR pe Windows** (PyInstaller nu cross-compilează). Produsul livrat evaluatorilor e Windows .exe.

### Decizii — LUATE 2026-06-11 (grill cu Adi)
- [x] **D1 — Build .exe:** GitHub Actions (`windows-latest`) ca pipeline principal **+ PC-ul Windows păstrat ca fallback** până la 2-3 release-uri reușite. Job creat: `.github/workflows/release-exe.yml` la **rădăcina** repo-ului. ⚠️ Descoperire: `evaluare-anevar/.github/workflows/ci.yml` NU rulează pe GitHub (Actions citește doar `.github/` de la rădăcină) — mutarea CI-ului e task separat.
- [x] **D2 — Calea proiectului pe Mac:** `~/claude/anevar` (actualizat 2026-06-11, era `~/Projects/anevar`) → folder sesiuni encodat `-Users-adi-claude-anevar`. Atenție la distincția `~/claude/` (folder de proiecte) vs `~/.claude/` (config Claude, cu punct).
- [x] **D3 — Worktree-urile b/c/d:** ~~se migrează toate~~ **ANULATĂ 2026-06-11**: A s-a mutat pe *agent work style* (agenți în `.claude/worktrees/`, gestionați automat) → sesiunile B–F și worktree-urile lor nu mai au sens. Worktree-urile b/c/d au fost șterse (branch-urile rămân pe origin; docs nesalvate din c copiate în `evaluare-anevar/docs/`). **Se migrează doar `anevar`.**
- [x] **D4 — Sesiunile:** **decide pilotul** (Faza 3.5) — relevant acum doar pentru sesiunea A (+ sesiunea de migrare). Dacă transcriptul copiat se deschide corect → copiezi transcripturile dorite la cutover; altfel → sesiune nouă din memorie + claude-mem (handoff scris rămâne plasa de siguranță pentru A).

---

## Faza 1 — Pregătire pe Windows (fără downtime; se poate face treptat, de azi)

**Ce se face:**
1. **Push tot ce e local-only:**
   ```bash
   git push origin win7-build Fix-fuzz-deadline
   git branch -a --no-merged   # verifică ce mai e nepushed
   git log --branches --not --remotes --oneline   # trebuie să iasă GOL
   ```
   Commit/finalizează WIP-ul curent (storage.py + test_storage.py — patch F-5; docs GDPR/LINDDUN + audituri salvate din fostul worktree c; flux-livrabile-audit.png).
2. **Salvează DOAR `live-up.py`** (hook-ul de server live) — recomandat: mută-l în repo (`evaluare-anevar/scripts/`) cu portarea de la 1.3. Restul `anevar-mailbox/` (mailbox.py, watch_A.py, inbox-uri) = sistem istoric A–F, desființat 2026-06-11 — arhivează-l în transfer doar ca referință, nu se repune în funcțiune pe Mac.
3. **Portabilitate cod (3 fix-uri mici, se pot face acum):**
   - `live-up.py`: înlocuiește ROOT hardcodat cu env var `ANEVAR_ROOT` + fallback pe detectare; pe Mac va porni `python -m evaluare` (nu `.exe`).
   - `export_chat.py`: derivă calea din `Path.home() / ".claude" / "projects"` + encoding-ul documentat în Faza 0.
   - verificare: `grep -rn "adyse\|C:\\\\Users" --include="*.py"` → doar rezultate intenționate.
4. **Generează lista de reinstalare plugins:** din `~/.claude/plugins/installed_plugins.json` — extrage perechile plugin@marketplace (39) și cele 6 marketplace-uri. Blocurile `enabledPlugins` + `extraKnownMarketplaces` din `~/.claude/settings.json` se transferă declarativ (Claude Code oferă prompt de instalare la prima rulare). Marketplace lipsă din settings: `thedotmack` (îl adaugă installerul claude-mem).
5. **Arhiva de transfer „non-git"** (USB/cloud), structură:
   ```
   transfer/
     claude-skills/          ← ~/.claude/skills (182 skills, portabile)
     claude-settings/        ← settings.json (ca REFERINȚĂ pt. rescris hooks, nu copiere 1:1)
     anevar-mailbox/         ← tot folderul
     app-date/               ← evaluare-anevar/live/date + live/backups + date/ din worktree
     claude-mem/             ← se umple în Faza 6 (DB-ul final); acum doar un backup de test
     sesiuni/                ← se umple în Faza 6; acum doar 1 transcript pilot pt. Faza 3.5
   ```

**Verificare Fazei 1:** `git log --branches --not --remotes` gol; grep căi hardcodate curat; arhiva există și conține skills+mailbox+date; suita de teste verde local (707 passed).

**Anti-pattern:** NU copia `~/.claude/plugins` și `~/.claude/.credentials.json` în arhivă — nu sunt portabile (căi `installPath` Windows; auth pe Mac = Keychain).

---

## Faza 2 — Setup de bază pe Mac (oricând, independent de Windows)

**Ce se face:**
```bash
# 1. Unelte de bază
xcode-select --install                       # git, compilatoare
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12 node git
brew install --cask libreoffice              # soffice — pdf.py îl găsește la /Applications/LibreOffice.app/... (cale deja în cod)

# 2. Claude Code (nativ, cu auto-update — recomandat de docs)
curl -fsSL https://claude.ai/install.sh | bash
claude    # primul start → login browser cu contul Max; NU seta ANTHROPIC_API_KEY

# 3. Clonare proiect (cale conform D2)
git clone https://github.com/adrianserbanescu-byte/anevar.git ~/claude/anevar
cd ~/claude/anevar
# (fără worktree-uri suplimentare — D3 anulată; agenții lui A își fac singuri worktrees sub .claude/worktrees/)

# 4. Mediu Python reproductibil (exact ca în README)
cd ~/claude/anevar/evaluare-anevar
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock && pip install -e . --no-deps
pip install -e .[dev]

# 5. Validare
pytest -n auto          # țintă: 707 passed (CI rulează pe Windows; aici confirmăm portabilitatea)
python -m evaluare      # app pe http://127.0.0.1:8000
```

### 2b. Aplicații utile pentru Claude Code (Mac proaspăt instalat — recomandat)

Legate de setup-ul real de pe Windows (plugin-uri/unelte folosite efectiv acolo):

```bash
# CLI-uri cerute de plugin-urile instalate
brew install gh                  # gh-cli@trailofbits + PR-uri GitHub; apoi: gh auth login
brew install semgrep             # static-analysis@trailofbits (scanări Semgrep)
brew install ripgrep jq          # căutare rapidă + procesare JSON în hooks/scripturi
brew install oven-sh/bun/bun uv  # claude-mem (worker pe Bun; uv pt. chroma) — npx claude-mem install
                                 #   le instalează oricum automat, dar manual e mai predictibil

# Aplicații desktop
brew install --cask visual-studio-code   # extensia Claude Code pt. IDE
brew install --cask iterm2               # terminal mai bun pt. CLI (alternativ: ghostty)
brew install --cask google-chrome        # extensia „Claude in Chrome" (MCP) — folosită pe Windows
# Claude Desktop (sesiunile desktop / ccd): descarcă de la https://claude.ai/download

# Pentru testarea e2e (scripts/_e2e.py) + plugin-ul playwright
npx playwright install chromium
```

Notă: `sqlite3` și `git` vin deja cu macOS/Xcode CLT; UPX NU e necesar pe Mac (doar la build-ul Windows, conform D1).

**Verificare:** suita verde pe macOS; app servește pe 8000; `python -c "from evaluare.report.pdf import _gaseste_soffice; print(_gaseste_soffice())"` găsește LibreOffice; generare raport .docx + conversie PDF funcționează.

**Anti-pattern:** nu instala Python prin alt manager decât cel decis (un singur interpret, altfel hook-urile vor arăta spre alt python); nu rula `npm install -g claude-mem` (nu înregistrează hooks — doar `npx claude-mem install`, în Faza 3).

---

## Faza 3 — Mediu Claude Code pe Mac (plugins, skills, settings, claude-mem)

**Ce se face:**
1. **Retenție ÎNAINTE de orice copiere de sesiuni** — în `~/.claude/settings.json` pe Mac:
   ```json
   { "cleanupPeriodDays": 365 }
   ```
2. **Marketplaces + plugins (reinstalare, nu copiere):**
   ```
   /plugin marketplace add anthropics/skills
   /plugin marketplace add dan323/easier-life-skills
   /plugin marketplace add trailofbits/skills
   /plugin marketplace add jeremylongshore/claude-code-plugins-plus-skills
   ```
   apoi transferă blocurile `enabledPlugins` + `extraKnownMarketplaces` din settings-ul Windows (din arhivă, `claude-settings/`) și acceptă prompturile de instalare; plugin-urile locale (trailofbits etc.) se reinstalează din proiect (`~/claude/anevar`).
3. **Skills:** copiază `transfer/claude-skills/` → `~/.claude/skills/`.
4. **Hooks — rescriere pentru macOS** (echivalentele celor 5 globale + 2 de proiect):
   - global (Stop, SubagentStop, PreToolUse×2, PostToolUse): `python3` + căile noi din `~/.claude/plugins/cache/...` (apar după reinstalarea plugin-urilor cost-tracker/memplan/security-guidance);
   - proiect (`~/claude/anevar/.claude/settings.local.json`, UserPromptSubmit): DOAR `python3` pe `live-up.py` portat (Faza 1.2). Hook-ul `mailbox.py` NU se recreează — sistemul A–F e desființat (2026-06-11).
5. **claude-mem:**
   ```bash
   npx claude-mem install        # Node 20+; Bun/uv se instalează automat
   npx claude-mem stop           # oprește workerul înainte de restore
   cp transfer/claude-mem/claude-mem.db ~/.claude-mem/claude-mem.db
   cp -R transfer/claude-mem/chroma ~/.claude-mem/chroma
   sqlite3 ~/.claude-mem/claude-mem.db "PRAGMA integrity_check;"   # trebuie "ok"
   npx claude-mem restart && npx claude-mem status
   ```
   NU copia `~/.claude-mem/settings.json` de pe Windows (căi hardcodate; Mac-ul își generează unul corect).

### Faza 3.5 — PILOT de portabilitate sesiuni (de-riscarea Fazei 6) ⚠️ critic
Portabilitatea transcripturilor pe CLI e nedocumentată — testăm cu O sesiune înainte de cutover:
```bash
mkdir -p ~/.claude/projects/-Users-adi-claude-anevar
# copiază UN .jsonl (+ subfolderul <session-id>/ aferent) din transfer/sesiuni/
cd ~/claude/anevar && claude --resume    # sesiunea pilot trebuie să apară în picker și să se deschidă
```
- Dacă merge → Faza 6 = copiere în masă.
- Dacă nu merge / se deschide degradat (cwd Windows înăuntru) → activezi fallback-ul D4: handoff-uri scrise per sesiune + memorie + claude-mem (cunoștințele tot migrează, doar istoricul conversațional rămâne arhivat).

**Verificare Fazei 3:** `/plugin` arată plugin-urile instalate; un hook de test rulează fără eroare (rulează orice tool și verifică lipsa erorilor de hook); `claude-mem status` = running + un search găsește o observație veche de pe Windows; sesiunea pilot listată la `/resume`.

**Anti-pattern:** nu copia folderul `~/.claude/plugins` de pe Windows; nu porni claude-mem restore cu workerul activ; nu copia transcripturi înainte de `cleanupPeriodDays`.

---

## Faza 4 — Servicii pe Mac (server live)

**Ce se face:**
1. **Server live pe 8000:** pe Mac nu există `.exe` → serverul live rulează din sursă:
   `cd ~/claude/anevar/evaluare-anevar && OUTPUT_DIR=live/date DB_PATH=live/date/evaluari.db ANEVAR_NO_BROWSER=1 python -m evaluare` (detașat).
   `live-up.py` portat (Faza 1.3) îl supraveghează din hook-ul UserPromptSubmit, ca acum. Opțional: `launchd` plist pentru pornire la boot (echivalentul „LIVE permanent").
2. **Date aplicație:** copiază `transfer/app-date/` → `~/claude/anevar/evaluare-anevar/live/date/` (+ `date/` în worktree dacă folosit). Verifică `PRAGMA integrity_check` pe `evaluari.db`.
3. ~~Mailbox~~ — nu se mai migrează (sistem A–F desființat 2026-06-11); arhiva `anevar-mailbox/` rămâne doar referință istorică.

**Verificare:** kill server → următorul prompt în Claude îl repornește automat (hook live-up); dosarele vechi vizibile în UI pe Mac.

---

## Faza 5 — Pipeline build .exe (conform deciziei D1)

**IMPLEMENTAT (D1, 2026-06-11):** job nou `.github/workflows/release-exe.yml` la **rădăcina repo-ului** (nu în `evaluare-anevar/.github/` — acela NU e citit de GitHub): declanșare pe tag `v*` sau manual (`workflow_dispatch`), runner `windows-latest`, `requirements.lock` + PyInstaller, `python scripts/build.py --clean --smoke-offline`, artifact `evaluare-anevar.exe` (fără UPX în CI → ~40,6 MB; diferența e ~3 MB). Test: declanșează manual din GitHub → Actions → „Release exe" → Run workflow, apoi compară artifact-ul cu un build local de pe PC.
**Fallback (D1):** PC-ul Windows rămâne disponibil pentru `python scripts/build.py --clean --upx` până la 2-3 release-uri reușite prin Actions.
**Task separat (descoperit la D1):** `ci.yml` trebuie mutat și el la rădăcină (`.github/workflows/`) cu `defaults.run.working-directory: evaluare-anevar`, altfel CI-ul nu rulează deloc pe GitHub.

**Verificare:** un build complet produce `.exe` (~37-40 MB) care trece smoke testul; documentează în `docs/build.md` noua procedură.

**Anti-pattern:** nu încerca PyInstaller pe Mac pentru ținta Windows (nu cross-compilează); nu uita excluderile UPX din spec (libcrypto/libssl — HTTPS se strică).

---

## Faza 6 — ULTIMA: migrarea sesiunilor de lucru (ziua cutover, ~2-3 ore downtime)

**Precondiție:** Fazele 2–5 verificate verde pe Mac; pilotul 3.5 concludent.

**Pe Windows (dimineața cutover):**
1. Sesiunea A își scrie handoff-ul (stare, branch-uri, next steps) — indiferent de rezultatul pilotului (plasă de siguranță).
2. Ultimul push: toate branch-urile + working tree curat (sau stash documentat în handoff).
3. Oprește loop-ul autonom AML (dacă mai rulează) și serverul live; `npx claude-mem stop` (checkpoint WAL).
4. Copiază FINAL în arhivă: `~/.claude-mem/` (db+chroma), `~/.claude/projects/C--Users-adyse-anevar/` complet (transcripturi + subfolderele sesiune + `memory/`), `app-date/` la zi.

**Pe Mac:**
5. `git pull` în `~/claude/anevar`.
6. Transcripturi: conținutul folderului Windows → `~/.claude/projects/-Users-adi-claude-anevar/` (numele NOU encodat — nu păstra numele `C--Users-adyse-anevar`!). Inclusiv `memory/`. (Worktree-uri: nu mai există — D3 anulată.)
7. claude-mem: restore final DB+chroma (procedura din Faza 3.5, cu workerul oprit), restart, `claude-mem search` pe un termen recent.
8. Repornește sesiunea A: din transcript (dacă pilotul a confirmat resume cross-OS) sau sesiune nouă care citește handoff + memorie + claude-mem.
9. Repornește serverul live; repornește loop-ul autonom dacă e cazul.

**Verificare (gate final):** `/resume` în `~/claude/anevar` listează sesiunile vechi; memoria auto se încarcă (MEMORY.md vizibil în context la sesiune nouă); claude-mem regăsește observații pre-migrare; mailbox-ul livrează mesaje; serverul live servește dosarele vechi; suita de teste verde.

**Rollback:** Windows-ul rămâne NEATINS (sursă de adevăr) minim 1-2 săptămâni. Orice eșec pe Mac → continui pe Windows fără pierderi.

---

## Faza 7 — Verificare finală + curățenie (după 1-2 săptămâni de rulare pe Mac)

- [ ] Toate fluxurile critice exersate pe Mac: dosar nou → evaluare → raport .docx → PDF (soffice) → AML; export `_md2pdf.py` (PDF + DOCX conform regulii proiectului).
- [ ] Un release `.exe` produs prin noul pipeline (D1) și verificat pe un Windows real (poate chiar PC-ul vechi, ultima lui sarcină).
- [ ] `grep -rn "C:\\\\Users\|adyse" ~/claude/anevar ~/claude/anevar-mailbox --include="*.py" --include="*.json"` — fără rămășițe Windows neintenționate.
- [ ] Memoria auto actualizată: regulile legate de Windows (build Win7 parcat, PowerShell) marcate ca istorice; calea proiectului nouă.
- [ ] Abia apoi: decomisionare/ștergere date de pe Windows.

---

## Referințe (citate de agenții de descoperire)
- Sesiuni & encoding: code.claude.com/docs/en/sessions + claude-directory (cleanupPeriodDays; layout jsonl) — encoding verificat empiric local pe 3 foldere.
- Auth Max: code.claude.com/docs/en/authentication (Keychain pe Mac; fără limită de device documentată; ANTHROPIC_API_KEY are prioritate — de evitat).
- claude-mem: docs.claude-mem.ai/installation + troubleshooting (backup db documentat; migrare cross-OS NEdocumentată → pilot + Windows ca sursă de adevăr).
- Plugins: code.claude.com/docs/en/discover-plugins (`extraKnownMarketplaces`/`enabledPlugins` declarativ; copierea folderului plugins nesuportată).
- Build: `evaluare-anevar/docs/build.md`, `deploy-checklist-exe.md`, `evaluare-anevar.spec`, `.github/workflows/ci.yml` (windows-latest).
