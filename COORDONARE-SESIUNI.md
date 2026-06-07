# 🔀 Coordonare între sesiuni Claude paralele — model WORKTREE (robust)

> 3 sesiuni Claude lucrează simultan. Ca să NU se suprapună, fiecare lucrează în **propriul director
> (git worktree) pe propria ramură**, și integrăm pe `master` prin merge. Sesiunea A e **owner de deploy**.

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
