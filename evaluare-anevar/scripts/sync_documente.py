"""Copiază documentele livrate din `docs/` în `src/evaluare/data/documente/` (împachetate în .exe).

Rulează înainte de build dacă s-au schimbat documentele. Sursa de adevăr rămâne `docs/`;
aici doar oglindim ce e în `evaluare.documente.REGISTRU` ca să fie disponibile offline în app.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

RADACINA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADACINA / "src"))

from evaluare.documente import REGISTRU, baza  # noqa: E402

SURSA = RADACINA / "docs"


def main() -> int:
    dest = baza()
    dest.mkdir(parents=True, exist_ok=True)
    copiate, lipsa = 0, []
    for d in REGISTRU:
        src = SURSA / d["fisier"]
        if not src.exists():
            lipsa.append(d["fisier"])
            continue
        tinta = dest / d["fisier"]
        tinta.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, tinta)
        copiate += 1
    print(f"Documente copiate: {copiate}/{len(REGISTRU)} -> {dest}")
    if lipsa:
        print("LIPSĂ (verifică docs/):", ", ".join(lipsa))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
