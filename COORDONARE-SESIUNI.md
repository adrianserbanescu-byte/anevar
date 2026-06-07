# 🔀 Coordonare între sesiuni Claude paralele — model WORKTREE (robust)

> 3 sesiuni Claude lucrează simultan. Ca să NU se suprapună, fiecare lucrează în **propriul director
> (git worktree) pe propria ramură**, și integrăm pe `master` prin merge. Sesiunea A e **owner de deploy**.

## 📌 Fapte canonice (valabile pentru TOATE sesiunile)
- **Punctul de intrare principal = «Flux livrabile v1.5»** (badge „recomandat" pe `index.html`). E versiunea
  curentă/principală; v1 și v0 rămân doar ca referință. Orice muncă nouă pe UI/flux țintește **v1.5**.

## 📬 Mailbox între sesiuni (comunicare fără copy-paste — merge ȘI în modul auto)
Script: `C:\Users\adyse\anevar-mailbox\mailbox.py` (în afara git; sesiunea = **auto-detectată din cwd**:
…anevar-b→B, …anevar-c→C, altfel A). Doar I/O pe fișiere → **fără aprobare** (merge în unsupervised) +
**persistent** (ținta poate fi oprită; vede mesajele la următorul `check`).
- **Trimite:** `python C:\Users\adyse\anevar-mailbox\mailbox.py send <A|B|C|all> <mesaj…>`
- **Citește (noile mele):** `python C:\Users\adyse\anevar-mailbox\mailbox.py check`  ·  **fără marcaj:** `… peek`  ·  **cine sunt:** `… whoami`

**Convenție:** fiecare sesiune face `check` la **începutul fiecărei iterații de loop** (sau când reia lucrul).
Exemple: B/C când au ramura gata → `… send A "sesiune-b: push pe X, gata de merge"`; A asignează →
`… send C "ia taskul Y"`. (`send_message` MCP rămâne fallback când vrei livrare „ca user turn", dar cere
modul supervised + ținta activă.)

## Cine, unde, ce ramură
| Sesiune | Director de lucru | Ramură | Rol |
|---------|-------------------|--------|-----|
| **A** | `C:\Users\adyse\anevar` (principal) | `master` | **owner deploy**: integrare (merge), build, server live, push master |
| **B** | `C:\Users\adyse\anevar-b` | `sesiune-b` | feature/logging etc. |
| **C** | `C:\Users\adyse\anevar-c` | `sesiune-c` | feature/docs etc. |

**Sesiunea B:** `cd C:\Users\adyse\anevar-b` și lucrează acolo (ești deja pe `sesiune-b`).
**Sesiunea C:** `cd C:\Users\adyse\anevar-c` și lucrează acolo (ești deja pe `sesiune-c`).
Worktree-urile sunt directoare SEPARATE — editările tale nu se mai văd în directorul altei sesiuni. 🎉

## Reguli
1. **Lucrezi DOAR în directorul tău.** Niciun fișier nu mai e partajat → zero editări care se suprascriu.
2. **Commit pe ramura ta** (`git add <fișiere> && git commit`), apoi **`git push origin sesiune-b`** (sau `-c`).
3. **Integrare pe master = doar sesiunea A.** Când ai o bucată gata: anunță / push ramura → A face
   `git merge sesiune-b` pe master, rezolvă conflictele (vizibile, nu pierdute), testează, buildează, deploy.
4. **Build (PyInstaller) + server live (port 8000) = DOAR sesiunea A**, din `master`. (3 build-uri simultane
   corup `build/`+`dist/`; 2 exe pe 8000 se ciocnesc.)
5. **Teste:** oricine, în worktree-ul lui (folosesc directoare temporare). Serverul de test e pe **8765** —
   nu porni un al doilea simultan. **Eliberează 8000 înainte de orice smoke pe exe** (altfel testezi instanța veche).
6. **Dacă atingi UI** (`templates/*.html`): rulează ȘI actualizează e2e (`scripts/_pw_smoke.py`), nu doar `pytest` —
   un selector stale după ce ștergi un element rupe validarea la deploy (s-a întâmplat: b03decc a scos popover-ul
   `!` din `dosar.html` fără să scoată verificarea din e2e; A a prins-o la integrare).

## Procedura de DEPLOY (sesiunea A, pe `master`)
1. `git merge sesiune-b` / `sesiune-c` (sau cherry-pick) → rezolvă conflicte → `git push origin master`.
2. Rulează suita + e2e (sanity).
3. `python evaluare-anevar/scripts/build.py` → `dist/evaluare-anevar.exe`.
4. **Validează FĂRĂ downtime** — pornește build-ul nou pe ALT port cât timp live rămâne pe 8000:
   `ANEVAR_PORT=8011 ANEVAR_NO_BROWSER=1 OUTPUT_DIR=<temp> ./dist/evaluare-anevar.exe` → curl `127.0.0.1:8011`.
5. **Hot-swap live:** oprește instanța veche (8000) → copiază exe-ul nou în `evaluare-anevar/live/` → pornește cu
   `ANEVAR_NO_BROWSER=1`. Server: `http://127.0.0.1:8000`, date în `evaluare-anevar/date/`. Downtime ~secunde.

## De ce worktree și nu doar branch
Cele 3 sesiuni rulau în ACELAȘI director → branch-urile NU le izolau (lucrau pe aceleași fișiere de pe disc).
Worktree = director fizic separat per ramură → izolare reală. Comenzi:
`git worktree list` · `git worktree remove <dir>` (când o sesiune termină).
