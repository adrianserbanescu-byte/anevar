# Instalarea aplicațiilor pe Mac — ghid pentru om (cu explicații)

> **Varianta recomandată: nu instala nimic manual.** Sesiunea Claude Code autonomă face tot
> (vezi `instructiuni-bootstrap-mac.md`, Partea A). Acest document există ca să ÎNȚELEGI ce
> se instalează și de ce — și ca plan B dacă vrei să faci pașii cu mâna ta.

## Dicționar — ce sunt uneltele astea

| Unealtă | Pe scurt | De ce ne trebuie |
|---|---|---|
| **Homebrew (`brew`)** | „Magazinul de aplicații" al Mac-ului pentru terminal. `brew install X` descarcă, instalează și ține la zi programul X. | Prin el se instalează aproape tot ce urmează, cu câte o comandă. |
| **Xcode Command Line Tools** | Pachetul de bază Apple cu `git` și compilatoare. | Cerut de Homebrew și de orice lucru cu cod. |
| **`gh` (GitHub CLI)** | Unealta oficială GitHub pentru terminal. Te loghezi O DATĂ (`gh auth login` — deschide browserul), apoi orice operație cu GitHub merge fără parole. | Clonarea repo-ului privat `anevar` + lucrul cu Actions (build-ul .exe). |
| **Python 3.12** | Limbajul în care e scrisă aplicația de evaluare. | Aplicația rulează pe Mac din sursă (nu există .exe pe Mac). |
| **`venv` (virtual environment)** | Un „sertar" izolat de Python în folderul proiectului (`.venv/`): conține EXACT bibliotecile aplicației, la versiunile din `requirements.lock`, fără să se amestece cu restul sistemului. | Aplicația rulează identic ca pe Windows; nimic nu se strică când alt program vrea altă versiune de bibliotecă. |
| **Node.js** | Mediu de rulare JavaScript. | Cerut de unele plugin-uri Claude (playwright, claude-mem prin `npx`). |
| **LibreOffice** | Suită de birou gratuită; ne interesează doar motorul ei `soffice`. | Conversia rapoartelor `.docx` → PDF (aplicația îl găsește singură la calea standard de Mac). |
| **Bun + uv** | Medii de rulare rapide (JavaScript, respectiv Python). | Worker-ul claude-mem rulează pe Bun; uv e folosit de unele unelte. Installerul claude-mem le pune și singur — manual e doar mai predictibil. |
| **ripgrep + jq** | Căutare ultra-rapidă în fișiere; procesare JSON în terminal. | Folosite de hooks și scripturi. |
| **semgrep** | Scaner de securitate pentru cod. | Cerut de plugin-ul static-analysis (trailofbits). |
| **Claude Code / Claude Desktop** | Mediul în care lucrezi cu mine. Desktop și CLI împart același `~/.claude` (sesiuni, plugin-uri, settings). | Evident :) Login cu contul Max prin browser; pe Mac credențialele intră în Keychain. |
| **VS Code, iTerm2, Chrome** | Editor de cod, terminal mai bun, browser pentru extensia „Claude in Chrome". | Confort + paritate cu setup-ul de pe Windows. |

## Pașii de instalare (dacă îi faci manual)

Deschide aplicația **Terminal** (Launchpad → Terminal) și rulează pe rând:

```bash
# 1. Uneltele de bază Apple (git, compilatoare) — apare un dialog, acceptă
xcode-select --install

# 2. Homebrew — „magazinul" din care instalăm restul
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
#    la final, installerul îți arată 1-2 comenzi de adăugat în PATH — rulează-le!

# 3. Uneltele de linie de comandă
brew install python@3.12 node git gh semgrep ripgrep jq uv
curl -fsSL https://bun.sh/install | bash

# 4. Aplicațiile desktop
brew install --cask libreoffice google-chrome visual-studio-code iterm2

# 5. Claude Code (nativ, cu auto-update) + login
curl -fsSL https://claude.ai/install.sh | bash
claude        # primul start deschide browserul -> loghează-te cu contul tău Max
#    Claude Desktop (aplicația cu ferestre): descarcă de la https://claude.ai/download

# 6. Login GitHub (o singură dată)
gh auth login --web
gh auth setup-git
```

## Verificare rapidă (totul trebuie să răspundă cu o versiune)

```bash
brew --version && python3.12 --version && node --version && git --version
gh --version && bun --version && uv --version
/Applications/LibreOffice.app/Contents/MacOS/soffice --version
claude --version
```

## Ce NU instalezi

- **UPX** — folosit doar la build-ul Windows al .exe-ului (care se face prin GitHub Actions / PC-ul vechi).
- **Nimic din `~/.claude/plugins` de pe Windows** — plugin-urile se REINSTALEAZĂ pe Mac (o face bootstrap-ul), nu se copiază.
- **`.credentials.json` de pe Windows** — pe Mac autentificarea stă în Keychain; te loghezi pur și simplu din nou.

> După aplicații urmează proiectul în sine (clonare în `~/claude/anevar`, venv, teste) —
> acelea sunt pașii A3–A7 din `instructiuni-bootstrap-mac.md`, pe care sesiunea autonomă
> îi face singură.
