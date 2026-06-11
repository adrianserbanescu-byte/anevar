"""Cod poștal din adresă, via serviciul oficial Poșta Română (online, cu cache + fallback grațios).

SURSĂ ALEASĂ: Poșta Română — endpoint-ul AJAX al paginii `cauta-cod-postal.html`. E interogabil
CURAT programatic (POST form-encoded, răspuns JSON, fără captcha / anti-bot la momentul scrierii):

    POST https://www.posta-romana.ro/cnpr-app/modules/cauta-cod-postal/ajax/cautare_pentru_cod.php?q=
    body: k_adresa=<strada>&k_judet=<nume judet>&k_localitate=<nume localitate>&k_lang=ro
    -> {"formular": "<fragment HTML cu rânduri 'cod-postal-line'>", "found": 0|1}

Fiecare rând conține: COD POȘTAL (6 cifre) | județ | localitate | „Strada … nr. A-B; C-D" | oficiu.
În RO codul poștal e per SEGMENT de stradă (interval de numere), deci o stradă poate avea mai multe
coduri — alegem rândul al cărui interval acoperă `nr`, altfel primul rezultat (+ flag de ambiguitate).
Fără stradă: serviciul întoarce codul de bază al localității (strada = „-").

ROBUSTEȚE (cerință produs): timeout scurt; la orice eroare / timeout / offline / „not found"
-> `{"cod": None, "sursa": ..., "mesaj": ...}`, NICIODATĂ excepție care să rupă pagina (câmpul rămâne
manual). Cache pe cheia de adresă normalizată (lookup repetat = zero rețea).

DE CE NU fallback offline (dataset RO localitate->cod / Nominatim): nu există dataset poștal bundle-uit
în repo (tabelul `data/coordonate_localitati.json` are doar lat/lng, nu coduri poștale), iar codul e
per-stradă/număr — un fallback „un cod per localitate" ar fi adesea GREȘIT pentru orașe. Nominatim/OSM
nu acoperă fiabil codul poștal pe stradă în RO și ar adăuga o a doua dependență de rețea. Prin urmare
fallback-ul corect aici e: degradare grațioasă la `cod=None` + mesaj, câmpul rămâne editabil manual.
"""
from __future__ import annotations

import re
import threading
from typing import Any

import requests
from bs4 import BeautifulSoup

from evaluare.logging_setup import get_logger

log = get_logger(__name__)

ENDPOINT = (
    "https://www.posta-romana.ro/cnpr-app/modules/cauta-cod-postal/ajax/cautare_pentru_cod.php?q="
)
SURSA = "posta-romana"
_TIMEOUT = 5.0          # secunde — scurt; serviciul răspunde tipic sub 1s
_MAX_REZULTATE = 12     # plafon rânduri întoarse apelantului (anti-payload imens)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.posta-romana.ro/cauta-cod-postal.html",
}

_COD_RE = re.compile(r"\b(\d{6})\b")          # cod poștal RO = exact 6 cifre
# Intervale de numere din coloana stradă: „nr. 1-59; 2-68" (par/impar), sau „nr. 85" (un singur nr).
_INTERVAL_RE = re.compile(r"(\d+)\s*-\s*(\d+)")
_NR_SIMPLU_RE = re.compile(r"\bnr\.?\s*(\d+)\b", re.IGNORECASE)

# Cache proces-local, thread-safe. Cheia = adresa normalizată; valoarea = payload-ul deja construit.
_cache: dict[str, dict[str, Any]] = {}
_cache_lock = threading.Lock()


def _cheie(judet: str, localitate: str, strada: str, nr: str) -> str:
    """Cheie de cache stabilă: lowercase + spații colapsate (diacriticele rămân, contează la match)."""
    parti = [re.sub(r"\s+", " ", (x or "").strip().lower()) for x in (judet, localitate, strada, nr)]
    return "|".join(parti)


def _nr_int(nr: str) -> int | None:
    """Primul grup de cifre din `nr` (ex. „12B" -> 12, „bl. 4" -> 4); None dacă nu există cifre."""
    m = re.search(r"\d+", nr or "")
    return int(m.group()) if m else None


def _interval_acopera(text_strada: str, nr: int) -> bool:
    """True dacă vreun interval „A-B" din textul coloanei stradă conține `nr` (sau `nr` apare ca atare).

    Intervalele Poșta Română sunt adesea pe paritate (1-59 impare, 2-68 pare); fiind permisivi (nu
    verificăm paritatea) evităm să respingem un match corect doar din cauza convenției de afișare.
    """
    for m in _INTERVAL_RE.finditer(text_strada):
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo > hi:
            lo, hi = hi, lo
        if lo <= nr <= hi:
            return True
    # număr unic „nr. 85" fără interval
    return any(int(m.group(1)) == nr for m in _NR_SIMPLU_RE.finditer(text_strada))


def _parse_formular(html: str) -> list[dict[str, str]]:
    """Extrage rândurile (cod, judet, localitate, strada, oficiu) din fragmentul HTML `formular`.

    Fiecare rând = `<div class="... cod-postal-line">` cu 5 coloane `<p>`. Rândul „nu a furnizat
    niciun rezultat" nu conține cod de 6 cifre -> e ignorat natural. Robust la HTML parțial/ostil
    (BeautifulSoup nu ridică pe markup stricat; lipsa unei coloane -> string gol)."""
    soup = BeautifulSoup(html or "", "html.parser")
    randuri: list[dict[str, str]] = []
    for linie in soup.select(".cod-postal-line"):
        celule = [p.get_text(strip=True) for p in linie.find_all("p")]
        cod = ""
        for c in celule:
            m = _COD_RE.search(c)
            if m:
                cod = m.group(1)
                break
        if not cod:
            continue   # rând fără cod (mesaj de eroare / antet) — sărim
        randuri.append({
            "cod": cod,
            "judet": celule[1] if len(celule) > 1 else "",
            "localitate": celule[2] if len(celule) > 2 else "",
            "strada": celule[3] if len(celule) > 3 else "",
        })
        if len(randuri) >= _MAX_REZULTATE:
            break
    return randuri


def _alege(randuri: list[dict[str, str]], nr: str) -> tuple[dict[str, str] | None, bool]:
    """Alege rândul potrivit pt `nr`. Întoarce (rand_ales, ambiguu).

    - 0 rânduri -> (None, False)
    - 1 rând -> (acel rând, False)
    - >1 rânduri + `nr` care cade într-un interval -> (rândul respectiv, False)
    - >1 rânduri fără potrivire pe `nr` -> (primul, True)  # ambiguu: alegem primul, semnalăm
    """
    if not randuri:
        return None, False
    if len(randuri) == 1:
        return randuri[0], False
    nr_i = _nr_int(nr)
    if nr_i is not None:
        for r in randuri:
            if _interval_acopera(r["strada"], nr_i):
                return r, False
    return randuri[0], True


def _rezultat(cod: str | None, mesaj: str, *, candidati: list[dict[str, str]] | None = None,
              ambiguu: bool = False) -> dict[str, Any]:
    """Construiește payload-ul standard al lookup-ului (formă stabilă, contractul endpoint-ului)."""
    return {
        "cod": cod,
        "sursa": SURSA,
        "mesaj": mesaj,
        "ambiguu": ambiguu,
        "candidati": candidati or [],
    }


def cauta_cod_postal(
    judet: str,
    localitate: str,
    strada: str = "",
    nr: str = "",
    *,
    session: requests.Session | None = None,
    timeout: float = _TIMEOUT,
) -> dict[str, Any]:
    """Caută codul poștal pentru o adresă RO via Poșta Română. NU ridică NICIODATĂ; degradare grațioasă.

    Întoarce dict cu cheile: `cod` (str 6 cifre sau None), `sursa`, `mesaj`, `ambiguu` (bool — mai
    multe coduri pe stradă și nu am putut dezambigua pe `nr`), `candidati` (listă rânduri brute pt UI).

    `session` injectabil pentru teste (mock pe `.post`). Cache pe (judet, localitate, strada, nr).
    """
    judet = (judet or "").strip()
    localitate = (localitate or "").strip()
    strada = (strada or "").strip()
    nr = (nr or "").strip()
    if not judet or not localitate:
        return _rezultat(None, "Județ și localitate sunt obligatorii pentru căutarea codului poștal.")

    cheie = _cheie(judet, localitate, strada, nr)
    with _cache_lock:
        memo = _cache.get(cheie)
    if memo is not None:
        return dict(memo)   # copie defensivă (apelantul nu mutează cache-ul partajat)

    try:
        poster = session.post if session is not None else requests.post
        resp = poster(
            ENDPOINT,
            data={"k_adresa": strada, "k_judet": judet, "k_localitate": localitate, "k_lang": "ro"},
            headers=_HEADERS,
            timeout=timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as e:
        log.info("Poșta Română indisponibil (judet=%s, loc=%s): %s", judet, localitate, e)
        return _rezultat(None, "Serviciul Poșta Română nu a răspuns. Completează codul poștal manual.")
    except ValueError as e:   # JSON invalid (inclusiv json.JSONDecodeError, subclasă de ValueError)
        log.info("Răspuns Poșta Română neparsabil (judet=%s, loc=%s): %s", judet, localitate, e)
        return _rezultat(None, "Răspuns invalid de la Poșta Română. Completează codul poștal manual.")

    formular = payload.get("formular", "") if isinstance(payload, dict) else ""
    randuri = _parse_formular(formular)
    if not randuri:
        rez = _rezultat(None, "Nu am găsit niciun cod poștal pentru această adresă. "
                              "Verifică adresa sau completează manual.")
        with _cache_lock:
            _cache[cheie] = rez
        return dict(rez)

    ales, ambiguu = _alege(randuri, nr)
    if ambiguu:
        mesaj = ("Strada are mai multe coduri poștale (pe intervale de numere). Verifică numărul; "
                 "am ales primul rezultat.")
    else:
        mesaj = "Cod poștal găsit (Poșta Română)."
    rez = _rezultat(ales["cod"] if ales else None, mesaj, candidati=randuri, ambiguu=ambiguu)
    with _cache_lock:
        _cache[cheie] = rez
    return dict(rez)


def _goleste_cache() -> None:
    """Golește cache-ul proces-local (folosit de teste pentru izolare)."""
    with _cache_lock:
        _cache.clear()
