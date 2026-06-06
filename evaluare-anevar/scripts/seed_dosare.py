"""Seed local: contul „Adi S" (8717) + importă cele 4 rapoarte exemplu ca dosare-folder.

Rulează O DATĂ pe mașina dezvoltatorului (fișierele exemplu sunt private, NU intră în repo).
Creează în `<OUTPUT_DIR>/` (implicit `date/` lângă cwd): cont.json + dosare/<uuid>/ cu
dosar.json (câmpuri pre-completate din raport) + raportul .docx atașat ca versiune.

  python scripts/seed_dosare.py                 # caută în ~/Downloads
  python scripts/seed_dosare.py C:/cale/rapoarte
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from evaluare import cont as cont_mod  # noqa: E402
from evaluare import dosare_fs as fs  # noqa: E402
from evaluare.importers.docx_dosar import extrage_din_docx  # noqa: E402

FORMAT = ["id_client", "nume_client", "scop", "tip_proprietate"]   # IDclient_numeclient_scop_tip
EXEMPLE = ("21468", "21766", "21820", "21922")


def main() -> int:
    sursa = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads"
    os.environ.setdefault("OUTPUT_DIR", str(Path.cwd() / "date"))
    print(f"OUTPUT_DIR = {os.environ['OUTPUT_DIR']}")

    cont = cont_mod.salveaza_cont("Adi S", "8717", FORMAT)
    print(f"Cont: {cont['nume']} (legitimație {cont['legitimatie']}), format = {'_'.join(FORMAT)}")

    fisiere = sorted(f for f in sursa.glob("*.docx") if any(e in f.name for e in EXEMPLE))
    if not fisiere:
        print(f"⚠ Niciun raport exemplu (.docx cu id {EXEMPLE}) în {sursa}")
        return 1

    for f in fisiere:
        wizard = extrage_din_docx(f)
        uid = fs.creeaza(cont["legitimatie"], cont["nume"], wizard, format_dosar=FORMAT)
        shutil.copy(f, fs.baza() / uid / f"raport-import{f.suffix}")
        nume = fs.incarca(uid)["nume"]
        print(f"  ✓ {nume}  [{uid[:8]}]  ← {f.name}")

    print(f"\n{len(fisiere)} dosare create. Deschide aplicația -> ÎNCEPE -> «Dosare salvate».")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
