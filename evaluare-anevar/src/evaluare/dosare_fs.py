"""Stocarea dosarelor pe FOLDERE (sursa de adevăr) — pentru UI-ul nou.

Fiecare dosar = un folder `<baza>/dosare/<uuid>/` cu:
  - `dosar.json`  : semnătura (uuid, creator legitimație+nume, identitate, snapshot wizard, date)
  - `raport-*.docx` : versiuni generate

La pornire se SCANEAZĂ folderele (nu o bază autoritară). Un `_index.json` reține „ce am văzut
ultima dată", folosit DOAR pentru diff (existente / noi / dispărute). Vezi docs/specs/1-ui-output-first.md.
"""
from __future__ import annotations

import json
import os
import shutil
import uuid as _uuid
from datetime import datetime
from pathlib import Path

from evaluare.master_config import nume_dosar

# Câmpurile de IDENTITATE (blocate după creare; schimbarea lor → dosar nou). Setul exact se
# rafinează la #1; minim: scop + tip + client + id_client (+ județ/localitate dacă-s în titlu).
CAMPURI_IDENTITATE = ("scop", "tip_proprietate", "nume_client", "id_client", "judet", "localitate")


def baza() -> Path:
    out = os.environ.get("OUTPUT_DIR") or "date"
    return Path(out) / "dosare"


def _acum() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _identitate(wizard: dict) -> dict:
    return {c: wizard.get(c, "") for c in CAMPURI_IDENTITATE if wizard.get(c)}


def creeaza(creator_legitimatie: str, creator_nume: str, wizard: dict,
            format_dosar: list[str] | None = None) -> str:
    """Creează un dosar nou (folder + dosar.json). Returnează uuid-ul."""
    uid = str(_uuid.uuid4())
    folder = baza() / uid
    folder.mkdir(parents=True, exist_ok=True)
    ident = _identitate(wizard)
    dosar = {
        "uuid": uid,
        "nume": nume_dosar(format_dosar, wizard),
        "creator_legitimatie": str(creator_legitimatie),
        "creator_nume": creator_nume,
        "creat_la": _acum(),
        "modificat_la": _acum(),
        "identitate": ident,
        "wizard": wizard,
    }
    _scrie(uid, dosar)
    return uid


def _scrie(uid: str, dosar: dict) -> None:
    (baza() / uid / "dosar.json").write_text(
        json.dumps(dosar, ensure_ascii=False, indent=2), encoding="utf-8")


def incarca(uid: str) -> dict:
    f = baza() / uid / "dosar.json"
    if not f.exists():
        raise KeyError(f"Dosar inexistent: {uid}")
    return json.loads(f.read_text(encoding="utf-8"))


def salveaza_wizard(uid: str, wizard: dict) -> dict:
    """Actualizează datele wizard ale unui dosar (modificat_la). Returnează dosarul."""
    dosar = incarca(uid)
    dosar["wizard"] = wizard
    dosar["modificat_la"] = _acum()
    _scrie(uid, dosar)
    return dosar


def redenumeste(uid: str, nume: str) -> None:
    dosar = incarca(uid)
    dosar["nume"] = nume
    _scrie(uid, dosar)


def sterge(uid: str) -> None:
    shutil.rmtree(baza() / uid, ignore_errors=True)


def adauga_versiune_docx(uid: str, sursa: Path) -> str:
    """Copiază un .docx generat în folderul dosarului (datat). Returnează numele fișierului."""
    folder = baza() / uid
    folder.mkdir(parents=True, exist_ok=True)
    nume = f"raport-{datetime.now():%Y%m%d-%H%M%S}.docx"
    shutil.copy(sursa, folder / nume)
    return nume


def listeaza() -> list[dict]:
    """Scanează folderele cu `dosar.json`. Returnează antetele, ordonate după ultima modificare."""
    b = baza()
    out: list[dict] = []
    if not b.exists():
        return out
    for f in b.glob("*/dosar.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        out.append({k: d.get(k) for k in
                    ("uuid", "nume", "creator_legitimatie", "creator_nume",
                     "creat_la", "modificat_la", "identitate")})
    out.sort(key=lambda d: d.get("modificat_la") or "", reverse=True)
    return out


# ── Diff vs index „ultima vedere" (existente / noi / dispărute) ──────────────────
def _fisier_index() -> Path:
    return baza() / "_index.json"


def _citeste_index() -> dict:
    f = _fisier_index()
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def diff() -> dict:
    """Compară folderele de pe disc cu indexul „ultima vedere".

    Returnează {existente, noi, disparute} + actualizează indexul. „noi" = pe disc, nu în index
    (candidate la import/adoptare). „disparute" = în index, nu pe disc.
    """
    index = _citeste_index()
    pe_disc = {d["uuid"]: d for d in listeaza()}
    existente = [d for uid, d in pe_disc.items() if uid in index]
    noi = [d for uid, d in pe_disc.items() if uid not in index]
    disparute = [{"uuid": uid, **meta} for uid, meta in index.items() if uid not in pe_disc]
    # actualizează indexul cu ce e pe disc acum
    nou_index = {uid: {"nume": d.get("nume"), "modificat_la": d.get("modificat_la")}
                 for uid, d in pe_disc.items()}
    _fisier_index().parent.mkdir(parents=True, exist_ok=True)
    _fisier_index().write_text(json.dumps(nou_index, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"existente": existente, "noi": noi, "disparute": disparute}


def sterge_din_index(uid: str) -> None:
    """Scoate un dosar dispărut din index (folderul nu mai există)."""
    index = _citeste_index()
    if uid in index:
        del index[uid]
        _fisier_index().write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Import folder dosar ──────────────────────────────────────────────────────────
def importa_folder(src: Path, legitimatie_curenta: str, creator_nume: str) -> dict:
    """Importă un folder de dosar.

    Valid doar dacă conține `dosar.json` în formatul nostru. Dacă creatorul == legitimația
    curentă -> adoptă (același uuid, gratis). Dacă diferă -> dosar NOU (uuid nou, legat de
    userul curent). Returnează {uuid, e_nou}.
    """
    sj = Path(src) / "dosar.json"
    if not sj.exists():
        raise ValueError("Folderul nu conține un dosar.json în formatul aplicației.")
    try:
        dosar = json.loads(sj.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ValueError("dosar.json invalid.") from e
    acelasi = str(dosar.get("creator_legitimatie")) == str(legitimatie_curenta)
    if acelasi:
        uid = dosar.get("uuid") or str(_uuid.uuid4())
        e_nou = False
    else:
        uid = str(_uuid.uuid4())                       # dosar nou pentru userul curent
        dosar["uuid"] = uid
        dosar["creator_legitimatie"] = str(legitimatie_curenta)
        dosar["creator_nume"] = creator_nume
        dosar["creat_la"] = _acum()
        e_nou = True
    dest = baza() / uid
    dest.mkdir(parents=True, exist_ok=True)
    # copiază toate fișierele din folderul sursă (docx etc.)
    for item in Path(src).iterdir():
        if item.is_file() and item.name != "dosar.json":
            shutil.copy(item, dest / item.name)
    dosar["modificat_la"] = _acum()
    _scrie(uid, dosar)
    return {"uuid": uid, "e_nou": e_nou}
