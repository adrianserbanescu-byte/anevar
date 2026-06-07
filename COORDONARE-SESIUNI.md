# 🔀 Coordonare între sesiuni Claude paralele

> Sunt mai multe sesiuni Claude care lucrează simultan pe acest repo. Ca să NU ne suprapunem,
> fiecare sesiune respectă regulile de mai jos și își declară banda în tabel. Citește ÎNTÂI acest
> fișier la fiecare reluare; actualizează-ți rândul când schimbi ce lucrezi.

## Reguli de aur
1. **Editezi DOAR fișierele din banda ta** (vezi tabelul). Dacă ai nevoie de un fișier din altă bandă,
   notează în tabel și anunță (sau cere owner-ului benzii respective).
2. **UN SINGUR owner de „deploy"** face: `scripts/build.py` (PyInstaller), serverul **live pe 8000**,
   și **`git push` pe master**. Celelalte sesiuni NU buildează și NU pornesc exe pe 8000 (3 build-uri
   simultane corup `build/`+`dist/`; 2 exe pe 8000 se ciocnesc). Owner deploy curent: **vezi tabel**.
3. **Înainte de orice smoke test:** eliberează portul 8000 (`Stop-Process evaluare-anevar`) — altfel
   testezi instanța veche. (Lecție din 2026-06-07.)
4. **Commit mic + des, scoped** (`git add <fișierele tale>`, NU `git add -A`) ca să nu iei munca
   necommisă a altei sesiuni. Dacă `push` e respins (non-fast-forward): `git pull --rebase` apoi push.
5. **Ideal:** lucrează pe **branch/worktree** propriu și fă merge pe master prin PR (zero curse).

## Benzi (cine ce atinge) — actualizați-vă rândul
| Sesiune | Bandă (foldere/fișiere) | Lucrează acum la | Owner deploy? |
|---------|--------------------------|------------------|---------------|
| **A (ADR/build/live)** | `docs/adr/`, `dosare_fs.py`, `migrare.py`, `report/pdf.py`, build + server live | ADR-002/003/004 (gata); ține serverul live pe 8000 | **DA** (build + push + live) |
| B | *(declară-ți banda)* | *(ex. logging/observability — `logging_setup.py` + `log.*` în routere)* | nu |
| C | *(declară-ți banda)* | *(ex. docs/deliverables / UI templates)* | nu |

## Stare „deploy" partajată
- **Server live:** `http://127.0.0.1:8000` — pornit din `evaluare-anevar/live/evaluare-anevar.exe` (detașat),
  date în `evaluare-anevar/date/`. **Doar owner-ul deploy îl oprește/repornește** (hot-swap la build validat).
- **Build:** `dist/` + `build/` — doar owner-ul deploy rulează `build.py`.
- **Teste:** suita pytest + e2e (server de test pe **8765**) — oricine poate rula (folosesc directoare temporare),
  dar NU porni un al doilea server pe 8765 simultan.

> Dacă vrei, schimbă owner-ul de deploy sau benzile — doar actualizează tabelul și anunță sesiunile.
