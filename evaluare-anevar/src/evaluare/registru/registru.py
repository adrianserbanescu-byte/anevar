"""Registrul de evidenta a rapoartelor de evaluare — Procedura de arhivare ANEVAR §6.

Registru OBLIGATORIU pentru monitorizarea extinsa ANEVAR. Randurile se DERIVA din dosarele de pe
disc (`dosare_fs`, sursa de adevar), nu dintr-un tabel separat care s-ar putea desincroniza: fiecare
dosar = un rand. Campurile (~13, §6) vin din snapshot-ul wizardului salvat in `dosar.json` + numarul
de lucrare alocat la creare (`nr_lucrare`) + clasificarea de risc AML retinuta pe dosar (`risc_aml`).

Export: CSV (UTF-8 cu BOM, prietenos cu Excel-ul romanesc) si XLSX (scriitor minim, fara dependente).
"""
from __future__ import annotations

import csv
import io

from evaluare import dosare_fs as fs
from evaluare.registru import xlsx_min

# (cheie, eticheta) — ordinea = ordinea coloanelor in pagina + CSV + XLSX. Acopera cele ~13 campuri
# din Procedura §6 (nr. contract+data sunt comasate intr-o coloana; cele 3 date raman separate).
COLOANE: list[tuple[str, str]] = [
    ("nr_lucrare", "Nr. identificare"),
    ("contract", "Contract (nr./dată)"),
    ("client", "Client"),
    ("utilizatori", "Utilizatori desemnați"),
    ("obiect", "Obiect + localizare"),
    ("proprietar", "Proprietar"),
    ("tip", "Tip (PI/BM/Î/IF)"),
    ("scop", "Scop"),
    ("onorariu", "Onorariu"),
    ("data_evaluarii", "Data evaluării"),
    ("data_raportului", "Data raportului"),
    ("data_predarii", "Data predării"),
    ("verificator", "Verificare internă"),
    ("risc_aml", "Risc AML client"),
    ("observatii", "Observații"),
]

_SCOP_ETICHETA = {
    "garantare": "Garantarea creditului ipotecar",
    "raportare_financiara": "Raportare financiară (IFRS)",
    "asigurare": "Asigurare",
    "impozitare": "Impozitare",
    "litigii": "Litigiu",
}
# Categoriile motorului AML (redus/standard/sporit) -> terminologia Procedurii §6 (scăzut/mediu/ridicat).
_RISC_ETICHETA = {
    "redus": "scăzut", "standard": "mediu", "sporit": "ridicat",
    "scazut": "scăzut", "mediu": "mediu", "ridicat": "ridicat",
}
# Clasa de bun (Procedura §6): PI=imobiliare, BM=mobile, Î=intreprinderi, IF=instrumente financiare.
# App-ul evalueaza exclusiv bunuri imobile -> randurile sunt mereu PI.
_CLASA_BUN = "PI"


def _g(wizard: dict, *chei: str) -> str:
    """Prima valoare ne-goala dintre `chei` (toleranta la variante de denumire a campului)."""
    for c in chei:
        v = wizard.get(c)
        if v not in (None, "", []):
            return str(v).strip()
    return ""


def _contract(w: dict) -> str:
    nr, data = _g(w, "nr_contract", "contract_nr"), _g(w, "data_contract", "contract_data")
    return " / ".join(x for x in (nr, data) if x)


def _obiect(w: dict) -> str:
    tip = _g(w, "tip_proprietate") or "imobil"
    localizare = ", ".join(x for x in (
        _g(w, "adresa_strada", "adresa"),
        _g(w, "localitate_alt", "localitate"),
        _g(w, "judet"),
    ) if x)
    cad = _g(w, "numar_cadastral")
    parti = [tip]
    if localizare:
        parti.append(localizare)
    if cad:
        parti.append(f"nr. cad. {cad}")
    return "; ".join(parti)


def _verificator(w: dict) -> str:
    nume, data = _g(w, "verificator_intern_nume"), _g(w, "data_verificare_interna")
    return " / ".join(x for x in (nume, data) if x)


def rand(dosar: dict) -> dict:
    """Un rand de registru dintr-un dosar (`dosar.json`). Include `uid` (pt link de export, nu coloana)."""
    w = dosar.get("wizard", {}) or {}
    scop = _g(w, "scop")
    # `risc_aml` poate fi pe dosar (top-level) sau in wizard; il stringificam INAINTE de `.get` ca o
    # valoare nehashabila (lista/dict, dintr-un `dosar.json` fabricat/importat) sa NU arunce TypeError.
    risc = str(dosar.get("risc_aml") or "").strip() or _g(w, "risc_aml")
    return {
        "uid": dosar.get("uuid", ""),
        "nr_lucrare": dosar.get("nr_lucrare") or "—",
        "contract": _contract(w),
        "client": _g(w, "nume_client", "client_nume") or "—",
        "utilizatori": _g(w, "beneficiar", "utilizator_desemnat"),
        "obiect": _obiect(w),
        "proprietar": _g(w, "proprietar") or _g(w, "nume_client", "client_nume"),
        "tip": _CLASA_BUN,
        "scop": _SCOP_ETICHETA.get(scop, scop),
        "onorariu": _g(w, "onorariu"),
        "data_evaluarii": _g(w, "data_evaluarii"),
        "data_raportului": _g(w, "data_raportului"),
        "data_predarii": _g(w, "data_predarii"),
        "verificator": _verificator(w),
        "risc_aml": _RISC_ETICHETA.get(risc, risc),
        "observatii": _g(w, "observatii_registru", "inspectie_observatii"),
    }


# Cache in-process pe semnatura de mtime-uri: pagina `/registru` + cele 3 exporturi (json/csv/xlsx)
# apeleaza fiecare `randuri()`; fara cache = ~Nx re-citiri+parse JSON per rafala de cereri. Cache-ul
# se invalideaza automat cand orice `dosar.json` se schimba (mtime) sau cand se adauga/sterge un dosar.
_cache_randuri: tuple[object, list[dict]] | None = None


def _semnatura_dosare() -> object:
    """Semnatura ieftina a starii dosarelor pe disc: {uid: mtime_ns} pentru fiecare `dosar.json`.

    Orice creare/stergere/modificare schimba semnatura -> cache miss. Daca `stat` esueaza pentru un
    fisier, e omis (va fi reconsiderat la urmatorul apel)."""
    b = fs.baza()
    if not b.exists():
        return ()
    sig: list[tuple[str, int]] = []
    for f in b.glob("*/dosar.json"):
        try:
            sig.append((f.parent.name, f.stat().st_mtime_ns))
        except OSError:
            continue
    sig.sort()
    return tuple(sig)


def randuri() -> list[dict]:
    """Toate randurile de registru, sortate dupa numarul de lucrare (ordinea de inregistrare).

    Memoizat pe semnatura de mtime-uri (`_semnatura_dosare`): apeluri repetate intre care nimic nu s-a
    schimbat pe disc reutilizeaza rezultatul (returneaza o copie, ca apelantii sa nu mute cache-ul).
    """
    global _cache_randuri
    sig = _semnatura_dosare()
    if _cache_randuri is not None and _cache_randuri[0] == sig:
        return [dict(r) for r in _cache_randuri[1]]
    out: list[dict] = []
    for antet in fs.listeaza():
        uid = antet.get("uuid")
        if not uid:
            continue
        try:
            out.append(rand(fs.incarca(uid)))
        except (KeyError, ValueError, TypeError):
            # dosar sters/ilizibil intre listare si citire, sau `dosar.json` fabricat cu tipuri ostile
            # (ex. `risc_aml` lista/dict) -> sarit, NU darama tot registrul pentru toti.
            continue
    out.sort(key=lambda r: r.get("nr_lucrare") or "")
    _cache_randuri = (sig, [dict(r) for r in out])
    return out


def _matrice(rr: list[dict]) -> tuple[list[str], list[list[str]]]:
    antete = [et for _, et in COLOANE]
    randuri_val = [[r.get(cheie, "") for cheie, _ in COLOANE] for r in rr]
    return antete, randuri_val


def csv_text(rr: list[dict] | None = None) -> str:
    """Registrul ca text CSV, cu BOM UTF-8 in fata (Excel RO il deschide corect cu diacritice).

    Celulele care incep cu un caracter de formula (`= + - @`, TAB, CR) sunt prefixate cu apostrof
    (`xlsx_min._neutralizeaza_formula`) ca Excel/LibreOffice sa nu le execute ca formule LIVE
    (CSV/formula injection, CWE-1236). Antetele sunt fixe (din `COLOANE`) -> nu necesita neutralizare.
    """
    rr = randuri() if rr is None else rr
    antete, randuri_val = _matrice(rr)
    randuri_val = [[xlsx_min._neutralizeaza_formula(c) for c in rand] for rand in randuri_val]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(antete)
    w.writerows(randuri_val)
    return "﻿" + buf.getvalue()


def xlsx_bytes(rr: list[dict] | None = None) -> bytes:
    """Registrul ca workbook `.xlsx` (o foaie 'Registru'), fara dependente externe."""
    rr = randuri() if rr is None else rr
    antete, randuri_val = _matrice(rr)
    return xlsx_min.workbook(antete, randuri_val, nume_foaie="Registru")
