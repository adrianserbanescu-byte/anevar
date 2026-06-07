"""Stocarea dosarelor pe FOLDERE (sursa de adevăr) — pentru UI-ul nou.

Fiecare dosar = un folder `<baza>/dosare/<uuid>/` cu:
  - `dosar.json`  : semnătura (uuid, creator legitimație+nume, identitate, snapshot wizard, date)
  - `raport-*.docx` : versiuni generate

La pornire se SCANEAZĂ folderele (nu o bază autoritară). Un `_index.json` reține „ce am văzut
ultima dată", folosit DOAR pentru diff (existente / noi / dispărute). Vezi docs/specs/1-ui-output-first.md.
"""
from __future__ import annotations

import contextlib
import hashlib
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


def este_blocat(dosar: dict) -> bool:
    """ADR-003: identitatea e read-only dacă dosarul a fost asumat și nu e momentan deblocat.

    `blocat` se setează la fiecare asumare (generare/submit) și se șterge la `deblocheaza`. Pentru
    dosarele vechi (fără câmpul `blocat`) se derivă din `asumat_la` (asumat ⇒ blocat).
    """
    return bool(dosar.get("blocat", bool(dosar.get("asumat_la"))))


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
        "format_dosar": list(format_dosar) if format_dosar else None,
        "creator_legitimatie": str(creator_legitimatie),
        "creator_nume": creator_nume,
        "creat_la": _acum(),
        "modificat_la": _acum(),
        "identitate": ident,
        "wizard": wizard,
    }
    _scrie(uid, dosar)
    return uid


def _scrie_atomic(cale: Path, text: str) -> None:
    """Scrie atomic: fișier temporar lângă țintă + os.replace (evită coruptia la crash)."""
    tmp = cale.with_suffix(cale.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, cale)


def _scrie(uid: str, dosar: dict) -> None:
    _scrie_atomic(baza() / uid / "dosar.json",
                  json.dumps(dosar, ensure_ascii=False, indent=2))


def incarca(uid: str) -> dict:
    f = baza() / uid / "dosar.json"
    if not f.exists():
        raise KeyError(f"Dosar inexistent: {uid}")
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        # dosar.json corupt/ilizibil -> tratat ca „nu poate fi încărcat" (404 la caller), nu 500.
        raise KeyError(f"Dosar ilizibil (fișier corupt): {uid}") from e


def salveaza_wizard(uid: str, wizard: dict) -> dict:
    """Actualizează datele wizard ale unui dosar (modificat_la). Returnează dosarul.

    Recalculează numele din formatul memorat (un dosar creat gol nu mai rămâne „?_?_?"
    după ce userul completează identitatea) și reîmprospătează identitatea blocabilă.
    """
    dosar = incarca(uid)
    if este_blocat(dosar):                            # ADR-003: identitate read-only după asumare
        vechi = dosar.get("wizard", {})
        for c in CAMPURI_IDENTITATE:                  # îngheață câmpurile de identitate la valorile asumate
            if c in vechi:
                wizard[c] = vechi[c]
            else:
                wizard.pop(c, None)
    dosar["wizard"] = wizard
    dosar["identitate"] = _identitate(wizard)
    if dosar.get("format_dosar"):
        dosar["nume"] = nume_dosar(dosar["format_dosar"], wizard)
    dosar["modificat_la"] = _acum()
    _scrie(uid, dosar)
    return dosar


def redenumeste(uid: str, nume: str) -> None:
    dosar = incarca(uid)
    dosar["nume"] = nume
    _scrie(uid, dosar)


def sterge(uid: str) -> None:
    shutil.rmtree(baza() / uid, ignore_errors=True)


PASTREAZA_VERSIUNI = 10   # câte versiuni .docx păstrăm per dosar (retenție)


def adauga_versiune_docx(uid: str, sursa: Path, tip: str = "generat") -> str:
    """Copiază un .docx generat în folderul dosarului (datat). Returnează numele fișierului.

    Păstrează ultimele `PASTREAZA_VERSIUNI` versiuni (șterge cele mai vechi) ca să nu crească nelimitat.
    Numele include microsecunde → unic chiar la generări rapide succesive.
    `tip`: „generat" (raport asumat la «Generează») sau „import" (raport-sursă atașat la import).
    """
    folder = baza() / uid
    folder.mkdir(parents=True, exist_ok=True)
    nume = f"raport-{datetime.now():%Y%m%d-%H%M%S-%f}.docx"
    shutil.copy(sursa, folder / nume)
    vechi = sorted(folder.glob("raport-*.docx"))     # sortate cronologic (numele = timestamp)
    for v in vechi[:-PASTREAZA_VERSIUNI]:
        v.unlink(missing_ok=True)
    _inregistreaza_versiune(uid, nume, tip)          # ADR-003: hash de integritate + moment asumare
    return nume


def _hash_fisier(cale: Path) -> str:
    """SHA256 al unui fișier (amprentă de integritate)."""
    return hashlib.sha256(cale.read_bytes()).hexdigest()


def _inregistreaza_versiune(uid: str, nume: str, tip: str) -> None:
    """ADR-003: înregistrează în dosar.json hash-ul + momentul fiecărei versiuni (audit inalterabil).

    O versiune „generat" (asumată la «Generează») setează `asumat_la` la prima generare. Permite
    verificarea ulterioară că fișierul `.docx` asumat NU a fost alterat (vezi `verifica_integritate`).
    """
    folder = baza() / uid
    try:
        dosar = incarca(uid)
    except (KeyError, ValueError):
        return
    # păstrăm doar înregistrările pentru fișiere care încă există (versiunile vechi se rotesc)
    versiuni = [v for v in dosar.get("versiuni", []) if (folder / v.get("fisier", "")).exists()]
    versiuni.append({"fisier": nume, "hash": _hash_fisier(folder / nume), "la": _acum(), "tip": tip})
    dosar["versiuni"] = versiuni
    # Trigger de asumare (ADR-003, decizia Adi #10 — hibrid): „generat" (prima generare .docx)
    # SAU „submis" (fișier finalizat încărcat, ex. returnat de bancă/client). „import" NU asumă.
    if tip in ("generat", "submis"):
        dosar.setdefault("asumat_la", _acum())       # prima asumare (timestamp imuabil)
        dosar["blocat"] = True                        # (re)blochează identitatea (read-only) la fiecare asumare
    dosar["modificat_la"] = _acum()
    _scrie(uid, dosar)


def verifica_integritate(uid: str) -> list[dict]:
    """ADR-003: reverifică hash-ul fiecărei versiuni salvate vs. cel înregistrat la asumare.

    Întoarce, per versiune: `{fisier, la, tip, exista, ok}` — `ok=False` = fișierul a fost
    modificat/alterat după asumare (sau lipsește). Tamper-evidence aliniat SEV 2025 / GEV 520.
    """
    folder = baza() / uid
    dosar = incarca(uid)
    rez = []
    for v in dosar.get("versiuni", []):
        f = folder / v.get("fisier", "")
        exista = f.exists()
        rez.append({"fisier": v.get("fisier"), "la": v.get("la"), "tip": v.get("tip"),
                    "exista": exista, "ok": exista and _hash_fisier(f) == v.get("hash")})
    return rez


def deblocheaza(uid: str, motiv: str) -> dict:
    """ADR-003: deblochează identitatea pentru o corectură tipografică (decizia Adi: motiv → Audit).

    Înregistrează `{la, motiv}` în `deblocari[]` (urmă de audit) și pune `blocat=False`. Următoarea
    asumare (generare/submit) re-blochează automat. `motiv` e obligatoriu (altfel ValueError).
    """
    motiv = (motiv or "").strip()
    if not motiv:
        raise ValueError("Motivul deblocării e obligatoriu (intră în urma de audit).")
    dosar = incarca(uid)
    deblocari = list(dosar.get("deblocari", []))
    deblocari.append({"la": _acum(), "motiv": motiv[:500]})
    dosar["deblocari"] = deblocari
    dosar["blocat"] = False
    dosar["modificat_la"] = _acum()
    _scrie(uid, dosar)
    return dosar


def cloneaza(uid: str) -> str:
    """ADR-003: clonează munca tehnică într-un dosar NOU (uuid nou, neasumat, identitate editabilă).

    Folosit când userul vrea altă identitate după asumare („modifici identitatea = DOSAR NOU"):
    copiază wizardul-sursă (comparabile, calcule, descriere) într-un dosar proaspăt — fără `asumat_la`,
    `blocat`, `versiuni` — unde identitatea poate fi schimbată. Dosarul-sursă rămâne intact + asumat.
    """
    sursa = incarca(uid)
    return creeaza(sursa.get("creator_legitimatie", ""), sursa.get("creator_nume", ""),
                   dict(sursa.get("wizard", {})), sursa.get("format_dosar"))


# ── Lock de deschidere concurentă (ADR-003 item 7) ───────────────────────────────
LOCK_TTL_SEC = 90        # un `.lock` mai vechi de atât = orfan (instanță închisă brusc)


def _fisier_lock(uid: str) -> Path:
    return baza() / uid / ".lock"


def _varsta_sec(cale: Path) -> float | None:
    try:
        return datetime.now().timestamp() - cale.stat().st_mtime
    except OSError:
        return None


def marcheaza_lock(uid: str, token: str) -> bool:
    """Marchează/reîmprospătează lock-ul de deschidere. Întoarce True dacă dosarul era deja deschis de
    ALTĂ fereastră (lock proaspăt, alt token) — semnal de editare concurentă (avertisment soft)."""
    cale = _fisier_lock(uid)
    concurent = False
    varsta = _varsta_sec(cale)
    if varsta is not None and varsta < LOCK_TTL_SEC:
        try:
            detinut = json.loads(cale.read_text(encoding="utf-8")).get("token")
            concurent = bool(detinut and detinut != token)
        except (OSError, ValueError):
            concurent = False
    with contextlib.suppress(OSError):
        _scrie_atomic(cale, json.dumps({"token": token, "la": _acum()}))
    return concurent


def elibereaza_lock(uid: str, token: str) -> None:
    """Eliberează lock-ul dacă e deținut de acest token (la închiderea ferestrei)."""
    cale = _fisier_lock(uid)
    try:
        detinut = json.loads(cale.read_text(encoding="utf-8")).get("token")
    except (OSError, ValueError):
        return
    if detinut == token:
        with contextlib.suppress(OSError):
            cale.unlink(missing_ok=True)


def curata_lock_uri_orfane() -> int:
    """La pornire: șterge `.lock`-urile orfane (> TTL) rămase de la instanțe închise brusc. Întoarce nr."""
    b = baza()
    n = 0
    if not b.exists():
        return 0
    for cale in b.glob("*/.lock"):
        varsta = _varsta_sec(cale)
        if varsta is not None and varsta >= LOCK_TTL_SEC:
            with contextlib.suppress(OSError):
                cale.unlink(missing_ok=True)
                n += 1
    return n


_CAMPURI_ANTET = ("uuid", "nume", "creator_legitimatie", "creator_nume",
                  "creat_la", "modificat_la", "identitate")


def _fisier_cache() -> Path:
    return baza() / "_cache_antete.json"


def listeaza() -> list[dict]:
    """Scanează folderele cu `dosar.json`. Returnează antetele, ordonate după ultima modificare.

    Cache pe `mtime_ns` (`_cache_antete.json`): un `dosar.json` neschimbat NU se recitește/reparsează
    la fiecare apel (ex. la fiecare `/incepe`). Cache-ul e derivat — coruperea/lipsa lui = reconstruire.
    """
    b = baza()
    if not b.exists():
        return []
    cache: dict = {}
    cf = _fisier_cache()
    if cf.exists():
        try:
            cache = json.loads(cf.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cache = {}
    out: list[dict] = []
    cache_nou: dict = {}
    schimbat = False
    for f in b.glob("*/dosar.json"):
        uid = f.parent.name
        try:
            mtime = f.stat().st_mtime_ns
        except OSError:
            continue
        intrare = cache.get(uid)
        if intrare and intrare.get("mtime") == mtime:
            antet = intrare["antet"]                 # cache hit: niciun read/parse
        else:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            antet = {k: d.get(k) for k in _CAMPURI_ANTET}
            schimbat = True
        cache_nou[uid] = {"mtime": mtime, "antet": antet}
        out.append(antet)
    if schimbat or len(cache_nou) != len(cache):     # scrie doar când s-a schimbat ceva (sau s-a șters un dosar)
        with contextlib.suppress(OSError):
            _scrie_atomic(cf, json.dumps(cache_nou, ensure_ascii=False))
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
    _scrie_atomic(_fisier_index(), json.dumps(nou_index, ensure_ascii=False, indent=2))
    return {"existente": existente, "noi": noi, "disparute": disparute}


def sterge_din_index(uid: str) -> None:
    """Scoate un dosar dispărut din index (folderul nu mai există)."""
    index = _citeste_index()
    if uid in index:
        del index[uid]
        _scrie_atomic(_fisier_index(), json.dumps(index, ensure_ascii=False, indent=2))


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
