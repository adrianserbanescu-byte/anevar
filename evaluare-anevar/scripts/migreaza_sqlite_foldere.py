"""CLI: migrare ne-distructivă SQLite (UI vechi) -> foldere (UI nou). ADR-002, Faza 2.

  python scripts/migreaza_sqlite_foldere.py            # DRY-RUN (doar raportează)
  python scripts/migreaza_sqlite_foldere.py --apply    # creează folderele + copiază rapoartele

Folosește DB_PATH / OUTPUT_DIR din mediu (ca aplicația). Logica e în src/evaluare/migrare.py.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evaluare.migrare import migreaza  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Migrare ne-distructivă SQLite -> foldere (ADR-002).")
    ap.add_argument("--apply", action="store_true", help="aplică migrarea (altfel dry-run)")
    args = ap.parse_args()
    rez = migreaza(apply=args.apply)
    print(("APLIC" if args.apply else "DRY-RUN") + f": {rez['total']} dosare în {rez['db']}\n")
    for linie in rez["jurnal"]:
        print("  " + linie)
    print(f"\n{'Migrate' if args.apply else 'De migrat'}: {rez['migrate']} | Sărite: {rez['sarite']}")
    if not args.apply and rez["migrate"]:
        print("Rulează din nou cu --apply pentru a aplica.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
