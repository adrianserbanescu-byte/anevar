# Instrucțiuni bootstrap Mac — pentru sesiunea Claude Code autonomă (NU pentru om)

> **Cum se folosește (Adi) — singurii 2 pași umani:**
> 1. Instalează Claude Code pe Mac și loghează-te: `curl -fsSL https://claude.ai/install.sh | bash`
>    apoi `claude` (se deschide browserul → login cu contul Max). Atât.
> 2. Pornește o sesiune cu bypass permissions (`claude --dangerously-skip-permissions`, sau
>    echivalentul din Claude Desktop) și dă-i ca PRIM MESAJ întreg conținutul acestui fișier
>    (copy-paste; repo-ul e privat, sesiunea nu-l poate citi de pe GitHub înainte de `gh auth`).
>
> De aici încolo totul e treaba sesiunii: execută Partea A integral singură (inclusiv restul
> instalărilor — brew, unelte, aplicații), te strigă doar la pașii marcați 🙋; Partea B doar
> când îi dai arhiva de transfer. Ghidul explicativ pentru tine (ce e brew/gh/venv):
> `instructiuni-instalare-aplicatii-mac.md`.

---

## CONTEXT (pentru sesiunea care execută)

Ești pe un **Mac nou, cu macOS proaspăt instalat**. Adi migrează de pe Windows
(`C:\Users\adyse`) proiectul **anevar** (aplicație evaluare imobiliară ANEVAR — Python
3.11+/FastAPI, repo `adrianserbanescu-byte/anevar`) plus mediul Claude Code. Planul complet
al migrării e în `plan-migrare-mac.md` la rădăcina repo-ului (citește-l după clonare —
Faza 2/2b/3 sunt treaba ta; Faza 6 NU e treaba ta).

Misiunea ta: **execută tot ce se poate fără datele de pe Windows (Partea A), apoi, doar
dacă primești arhiva de transfer, Partea B.** Windows-ul rămâne sursa de adevăr.

Deciziile D1–D4 sunt deja LUATE (vezi secțiunea „Decizii" din `plan-migrare-mac.md`):
calea de lucru e `~/claude/anevar`; build-ul .exe merge prin GitHub Actions
(`.github/workflows/release-exe.yml`, la rădăcină) cu PC-ul Windows ca fallback;
FĂRĂ worktree-uri suplimentare (D3 anulată — sesiunile B–F și worktree-urile lor au fost
desființate pe 2026-06-11; A lucrează cu agenți); sesiuni — decide pilotul (B5).

## REGULI (rulezi cu bypass permissions — disciplina e a ta)

1. **Nimic distructiv:** nu ștergi, nu suprascrii fișiere existente fără backup `.bak`.
2. **Idempotent:** înainte de orice instalare verifică dacă există deja (`command -v`, `brew list`).
3. **Gate-uri:** la fiecare punct marcat GATE, dacă verificarea pică → STOP pe acea ramură,
   notează în jurnal, continuă cu restul, raportează la final.
4. **NU seta `ANTHROPIC_API_KEY`** nicăieri (ar suprascrie abonamentul Max cu facturare API).
5. **NU atinge Faza 6** (migrarea în masă a sesiunilor) — doar Adi decide ziua cutover.
6. **Jurnal:** ține progresul în `~/bootstrap-log.md` (mută-l în `~/claude/anevar/` după clonare):
   pas, comandă, rezultat, gate trecut/picat.
7. Întreabă-l pe Adi DOAR la pașii marcați 🙋 (restul — autonom, fără pauze).

---

## PARTEA A — fără date de pe Windows (execută acum, cap-coadă)

### A1. Unelte de bază
```bash
xcode-select --install 2>/dev/null || echo "CLT deja instalat"
# Homebrew (dacă lipsește):
command -v brew || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Pe Apple Silicon adaugă brew în PATH (urmează instrucțiunile afișate de installer)
brew install python@3.12 node git gh semgrep ripgrep jq uv
brew install --cask libreoffice google-chrome visual-studio-code iterm2
curl -fsSL https://bun.sh/install | bash    # Bun — necesar pt. claude-mem
```
GATE A1: `python3.12 --version`, `node --version`, `git --version`, `gh --version`,
`soffice --version` (sau `/Applications/LibreOffice.app/Contents/MacOS/soffice --version`) — toate răspund.

### A2. Capcana nr. 1 din plan: retenția sesiunilor — ÎNAINTE de orice copiere de transcripturi
Adaugă `"cleanupPeriodDays": 365` în `~/.claude/settings.json` (creează fișierul dacă lipsește,
merge JSON corect — nu suprascrie alte chei):
```bash
python3 - <<'EOF'
import json, pathlib
p = pathlib.Path.home()/".claude"/"settings.json"
p.parent.mkdir(exist_ok=True)
d = json.loads(p.read_text()) if p.exists() else {}
d["cleanupPeriodDays"] = 365
p.write_text(json.dumps(d, indent=2))
print("OK:", p)
EOF
```
GATE A2: `python3 -c "import json,pathlib;print(json.loads((pathlib.Path.home()/'.claude'/'settings.json').read_text())['cleanupPeriodDays'])"` → 365.

### A3. GitHub auth + clonare proiect
```bash
gh auth login --web      # 🙋 cere browserul — anunță-l pe Adi că trebuie să confirme în browser
gh auth setup-git
mkdir -p ~/claude
gh repo clone adrianserbanescu-byte/anevar ~/claude/anevar
cd ~/claude/anevar && git log --oneline -3   # sanity
```
NU crea worktree-uri suplimentare (anevar-b/c/d au fost desființate pe 2026-06-11 odată cu
sesiunile B–F; A lucrează pe agent work style, cu worktrees automate sub `.claude/worktrees/`).

### A4. Mediu Python + GATE-ul principal
```bash
cd ~/claude/anevar/evaluare-anevar
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock && pip install -e . --no-deps && pip install -e .[dev]
pytest -n auto
```
GATE A4 (cel mai important): țintă **~707 passed, 0 failed**. Suita a rulat până acum doar
pe Windows — dacă pică teste, NU „repara" codul; documentează exact ce pică (nume test +
eroare) în jurnal și raportează. Excepție permisă: teste skip pe soffice/platформă.

### A5. Validări aplicație
```bash
python -c "from evaluare.report.pdf import _gaseste_soffice; print(_gaseste_soffice())"  # trebuie cale LibreOffice
ANEVAR_NO_BROWSER=1 python -m evaluare &   # pornește pe 8000
sleep 3 && curl -s http://127.0.0.1:8000/api/status && kill %1
npx playwright install chromium            # pt. e2e (scripts/_e2e.py)
```

### A6. Marketplaces + plugins Claude Code
Încearcă întâi CLI-ul: `claude plugin --help`. Dacă există subcomenzi marketplace/install,
folosește-le; altfel scrie blocurile declarative în `~/.claude/settings.json` (merge, nu
suprascrie) — Claude Code va propune instalarea la următoarea pornire:
```json
"extraKnownMarketplaces": {
  "anthropic-agent-skills": {"source": {"source": "github", "repo": "anthropics/skills"}},
  "easier-life-skills":     {"source": {"source": "github", "repo": "dan323/easier-life-skills"}},
  "trailofbits":            {"source": {"source": "github", "repo": "trailofbits/skills"}},
  "claude-code-plugins-plus": {"source": {"source": "github", "repo": "jeremylongshore/claude-code-plugins-plus-skills"}}
},
"enabledPlugins": {
  "superpowers@claude-plugins-official": true, "frontend-design@claude-plugins-official": true,
  "skill-creator@claude-plugins-official": true, "pr-review-toolkit@claude-plugins-official": true,
  "apollo@claude-plugins-official": true, "context7@claude-plugins-official": true,
  "desktop-commander@claude-plugins-official": true, "figma@claude-plugins-official": true,
  "ui5@claude-plugins-official": true, "github@claude-plugins-official": true,
  "microsoft-docs@claude-plugins-official": true, "amplitude@claude-plugins-official": true,
  "playwright@claude-plugins-official": true, "outputai@claude-plugins-official": true,
  "logfire@claude-plugins-official": true, "pyright-lsp@claude-plugins-official": true,
  "security-guidance@claude-plugins-official": true, "claude-md-management@claude-plugins-official": true,
  "document-skills@anthropic-agent-skills": true, "claude-api@anthropic-agent-skills": true,
  "example-skills@anthropic-agent-skills": true,
  "find-skills@easier-life-skills": true, "docs@easier-life-skills": true,
  "security-review@easier-life-skills": true, "dependency-audit@easier-life-skills": true,
  "code-audit@easier-life-skills": true, "cost-tracker@easier-life-skills": true,
  "memplan@easier-life-skills": true, "workflow@easier-life-skills": true,
  "brainstorm@easier-life-skills": true,
  "testing-handbook-skills@trailofbits": true,
  "modern-python@trailofbits": true, "property-based-testing@trailofbits": true,
  "dimensional-analysis@trailofbits": true, "git-cleanup@trailofbits": true,
  "supply-chain-risk-auditor@trailofbits": true,
  "zeroize-audit@trailofbits": true, "static-analysis@trailofbits": true,
  "differential-review@trailofbits": true, "audit-context-building@trailofbits": true,
  "agentic-actions-auditor@trailofbits": true, "gh-cli@trailofbits": true,
  "fp-check@trailofbits": false,
  "site-audit@easier-life-skills": true
}
```
(Listă VERIFICATĂ 2026-06-11 contra `installed_plugins.json` de pe Windows: TOATE cele 45 de
plugin-uri — 36 user-scope + cele 8 foste project-scope (decizie Adi: pe Mac trec la user scope;
`fp-check` rămâne dezactivat) — sunt în blocul de mai sus; al 45-lea, claude-mem, se instalează la A7.)
NU scrie plugin-uri în `~/claude/anevar/.claude/settings.local.json` — pe Mac toate sunt la
user scope (decizie Adi, 2026-06-11); fișierul de proiect rămâne doar pentru hook-ul live-up (B4).

### A7. claude-mem
```bash
npx claude-mem install --ide claude-code --provider claude   # Node 20+; folosește Bun instalat la A1
npx claude-mem status    # GATE A7: worker running
```
NU restaura încă DB-ul de pe Windows (asta e Partea B / Faza 6).

### A8. Raport final Partea A
Tabel în `~/claude/anevar/bootstrap-log.md`: fiecare gate (A1–A7) cu ✅/❌ + detalii la ❌.
Mesaj sumar către Adi cu ce a trecut, ce a picat, ce așteaptă (arhiva pt. Partea B).

---

## PARTEA B — DOAR când Adi îți dă arhiva de transfer 🙋 (cere-i calea, ex. /Volumes/...)

B1. **Skills:** `cp -R <arhiva>/claude-skills/* ~/.claude/skills/` (creează dirul dacă lipsește).
B2. **live-up.py — DOAR el** (restul `anevar-mailbox/` = sistem istoric A–F, desființat 2026-06-11,
    NU se repune în funcțiune): ia `live-up.py` din arhivă sau din repo (dacă a fost mutat în
    `evaluare-anevar/scripts/`). Dacă mai are `ROOT = Path(r"C:\Users\adyse...")` hardcodat →
    rescrie pentru Mac: ROOT din env `ANEVAR_ROOT` (default `~/claude/anevar/evaluare-anevar`)
    și pornire `python -m evaluare` (nu `.exe`) cu env `OUTPUT_DIR`, `DB_PATH`, `ANEVAR_NO_BROWSER=1`.
B3. **Date aplicație:** `cp -R <arhiva>/app-date/* ~/claude/anevar/evaluare-anevar/live/date/`;
    apoi `sqlite3 ~/claude/anevar/evaluare-anevar/live/date/evaluari.db "PRAGMA integrity_check;"` → ok.
B4. **Hooks:** global (`~/.claude/settings.json`) — recreează echivalentele Windows cu căi Mac:
    Stop+SubagentStop → `python3 ~/.claude/plugins/cache/easier-life-skills/cost-tracker/*/hooks/cost-tracker.py`;
    PreToolUse → memplan `pretooluse-start.py` + (matcher Edit|Write|MultiEdit) security-guidance
    `security_reminder_hook.py`; PostToolUse → memplan `memplan-post-tooluse.py`.
    Folosește căile REALE din cache după instalarea plugin-urilor (glob, nu ghici).
    Proiect (`~/claude/anevar/.claude/settings.local.json`) — UserPromptSubmit:
    DOAR `python3 <cale>/live-up.py` (vezi B2). NU recrea hook-ul `mailbox.py` (sistem desființat).
B5. **PILOT sesiune (capcana nr. 2):**
    `mkdir -p ~/.claude/projects/-Users-$(whoami)-claude-anevar` și copiază din arhivă UN singur
    `.jsonl` + subfolderul `<session-id>/` aferent. Apoi cere-i lui Adi 🙋 să verifice în
    Claude Desktop (proiectul ~/claude/anevar → istoricul de sesiuni) dacă sesiunea pilot apare și
    se deschide. Raportează rezultatul — decide strategia Fazei 6 (D4).
B6. **claude-mem restore (doar test, dacă arhiva conține un snapshot):**
    `npx claude-mem stop` → copiază `claude-mem.db` + `chroma/` → `sqlite3 ... "PRAGMA integrity_check;"`
    → `npx claude-mem restart` → `npx claude-mem status` + un search de probă.
    NU copia `settings.json` al claude-mem de pe Windows.

## CE NU FACI (anti-pattern, repetat intenționat)
- Nu copiezi `~/.claude/plugins` sau `.credentials.json` de pe Windows.
- Nu muți TOATE sesiunile (Faza 6 = decizia lui Adi).
- Nu „repari" teste picate modificând logica aplicației.
- Nu pornești migrarea claude-mem cu workerul pornit.
