"""Alocarea numarului de lucrare secvential pe an: `AAAA/NNNN`.

Procedura de arhivare ANEVAR §11 cere ca denumirea/indexarea dosarului sa contina minim
**nr. lucrare + an**; §6 il foloseste ca **numar de identificare a raportului** (recomandat pe
coperta). Aici alocam atomic urmatorul numar pe an, refolosind tiparul O_EXCL din `aml/store`:
doi creatori concurenti de dosare nu pot primi acelasi numar.

Numerele alocate sunt urme persistente (fisiere-marcaj `<an>_<NNNN>`), separate de dosar — un dosar
sters NU elibereaza numarul (golurile sunt normale intr-un registru, ca la numerotarea facturilor).
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path


def _baza_registru() -> Path:
    """Radacina datelor de registru, sub OUTPUT_DIR (langa `dosare/`). Citita la fiecare apel
    (testele monkeypatch-eaza OUTPUT_DIR per test)."""
    out = os.environ.get("OUTPUT_DIR") or "date"
    return Path(out) / "registru"


def _dir_numere() -> Path:
    return _baza_registru() / "numere"


def _urmatorul_liber(d: Path, an: int) -> int:
    """Cel mai mare NNNN deja alocat pentru `an`, + 1 (1 daca anul e gol). Doar punct de plecare —
    alocarea reala ramane atomica (O_EXCL) in `aloca`."""
    maxim = 0
    for p in d.glob(f"{an}_*"):
        try:
            n = int(p.name.split("_", 1)[1])
        except (ValueError, IndexError):
            continue                         # fisier strain in folder -> ignorat
        maxim = max(maxim, n)
    return maxim + 1


def aloca(an: int | None = None) -> str:
    """Aloca ATOMIC urmatorul numar de lucrare pentru `an` (implicit anul curent). Intoarce `AAAA/NNNN`.

    `os.O_CREAT|os.O_EXCL` garanteaza un singur castigator per nume de fisier: la coliziune (alt
    proces a luat acel index intre estimare si creare) incrementam si reincercam pana prindem un slot
    liber — la fel ca alocarea de id din `aml/store.salveaza`.
    """
    an = an if an is not None else datetime.now().year
    d = _dir_numere()
    d.mkdir(parents=True, exist_ok=True)
    idx = _urmatorul_liber(d, an)
    while True:
        cale = d / f"{an}_{idx:04d}"
        try:
            fd = os.open(cale, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            break
        except FileExistsError:              # alt proces a luat acest index -> urmatorul
            idx += 1
    return f"{an}/{idx:04d}"
