"""Modul BIG (Baza Imobiliară de Garanții ANEVAR) — pregătirea datelor de export raport -> BIG.

Scopul #1 al aplicației (GEV 520 §7): raportul de evaluare realizat **pentru bancă, în scopul
garantării creditului** trebuie înregistrat în BIG. Acest modul este **pur logică + date** (fără
wiring web, fără rețea, fără integrare online cu portalul BIG): construiește payload-ul cu câmpurile
minime cerute de formularul BIG, dintr-un dosar/meta al aplicației, și verifică (checklist) că toate
câmpurile minime sunt prezente înainte de o eventuală transmitere manuală în portal.

Câmpurile minime BIG (din manualul de utilizare ANEVAR-BIG „big@anevar.ro" — formularul on-line de
introducere a unei evaluări, secțiunile: selecția băncii, tip/subtip proprietate, localizare,
descriere, informații raport, recipisă). Manualul (Scopul proiectului) precizează explicit conținutul
bazei: „tipul proprietăţii evaluate, suprafaţa, localitatea unde se află proprietatea respectivă,
codul poştal, data evaluării, concluzia evaluatorului cu privire la valoarea de piaţă".

NON-GOAL: integrarea online cu portalul BIG (autentificare, transmitere). Aici doar **pregătim**
datele + producem checklist-ul de lipsuri. Confidențialitate: datele rămân locale (niciun apel AI).
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

# ── Nomenclatoare BIG (liste predefinite din formular) ───────────────────────────────────────────
# Manualul: formularul folosește „nomenclatoare" (liste de valori predefinite). Tipul proprietății se
# alege primul, apoi subtipul (dependent de tip). Reproducem maparea tipurilor interne ale aplicației
# (`profil.TipActiv`) la „tip proprietate" BIG. Subtipul rămâne la latitudinea evaluatorului (listă
# deschisă în BIG, dependentă de tip) — îl transportăm ca text dacă e cunoscut.
TipProprietateBIG = Literal["rezidential", "comercial", "industrial", "teren", "agricol", "special"]

# Maparea TipActiv (intern) -> tip proprietate BIG. `casa`/`apartament` = Rezidențial; `agricol` are
# propriul tip; restul direct. Subtipul BIG implicit (sugestie) per tip activ intern.
_TIP_ACTIV_LA_BIG: dict[str, TipProprietateBIG] = {
    "casa": "rezidential",
    "apartament": "rezidential",
    "teren": "teren",
    "comercial": "comercial",
    "industrial": "industrial",
    "agricol": "agricol",
    "special": "special",
}

_SUBTIP_IMPLICIT: dict[str, str] = {
    "casa": "Casă/vilă",
    "apartament": "Apartament în bloc",
    "teren": "Teren intravilan",
    "comercial": "Spațiu comercial",
    "industrial": "Hală/spațiu industrial",
    "agricol": "Teren agricol extravilan",
    "special": "Proprietate cu destinație specială",
}


def tip_proprietate_big(tip_activ: str) -> TipProprietateBIG | None:
    """Mapează tipul de activ intern (`profil.TipActiv`) la tipul de proprietate BIG. None dacă necunoscut."""
    return _TIP_ACTIV_LA_BIG.get((tip_activ or "").strip().lower())


def subtip_implicit(tip_activ: str) -> str | None:
    """Sugestia de subtip BIG pentru un tip de activ intern (evaluatorul îl poate suprascrie)."""
    return _SUBTIP_IMPLICIT.get((tip_activ or "").strip().lower())


# ── Câmpurile minime de export raport -> BIG ─────────────────────────────────────────────────────
class CampuriMinimeBIG(BaseModel):
    """Câmpurile minime ale unei înregistrări BIG (sumarul introdus din raportul de evaluare).

    Reflectă formularul on-line BIG: selecția băncii + tip/subtip proprietate + localizare (cod
    poștal, județ, localitate, stradă) + descriere (suprafață) + informații raport (valoare de piață,
    monedă, data evaluării, abordare) + identificarea evaluatorului și a raportului.

    Câmpurile marcate „minim obligatoriu" în `valideaza_campuri_minime`:
      - banca (beneficiar / utilizator desemnat — creditorul pentru care s-a întocmit raportul)
      - tip_proprietate + subtip_proprietate
      - cod_postal + judet + localitate
      - suprafata
      - valoare_piata + moneda + data_evaluarii
      - evaluator_nume + evaluator_legitimatie + nr_raport
    """

    # — Selecția băncii (manual: „se alege o bancă pentru care membrul titular va introduce informații")
    banca: str = ""                              # banca finanțatoare / creditorul (utilizator desemnat)
    cod_bic: str | None = None                   # codul BIC al băncii (opțional; folosit la autentificare bancă)

    # — Tip și subtip proprietate (nomenclatoare)
    tip_proprietate: TipProprietateBIG | None = None
    subtip_proprietate: str | None = None        # listă dependentă de tip (text BIG)

    # — Localizare proprietate (cod poștal -> județ/localitate/stradă auto în portal)
    cod_postal: str | None = None
    judet: str | None = None
    localitate: str | None = None
    strada: str | None = None                    # opțional (se completează din cod poștal în portal)

    # — Descriere proprietate
    suprafata: Decimal | None = Field(default=None, gt=0)   # mp (teren) sau arie utilă/desfășurată (construcție)
    um_suprafata: str = "mp"
    utilitati: list[str] = Field(default_factory=list)      # listă predefinită (apă/canal/gaz/curent etc.)
    an_constructie: int | None = None                       # pentru construcții

    # — Informații raport (concluzia evaluatorului)
    valoare_piata: Decimal | None = Field(default=None, gt=0)   # concluzia: valoarea de piață
    moneda: str = "RON"                          # moneda concluziei (RON / EUR)
    abordare: str | None = None                  # abordarea principală (cost / comparație / venit)
    scop: str = "garantarea creditului"          # BIG colectează doar evaluări pentru garantare
    data_evaluarii: str | None = None            # data de referință a valorii (ISO yyyy-mm-dd)
    data_raportului: str | None = None

    # — Identificarea evaluatorului și a raportului (membru titular ANEVAR)
    evaluator_nume: str = ""
    evaluator_legitimatie: str = ""              # nr. de legitimație ANEVAR (membru titular)
    nr_raport: str | None = None                 # nr. de identificare a raportului (nr. de lucrare AAAA/NNNN)


# Câmpurile considerate „minim obligatoriu" pentru o înregistrare BIG validă (cheie -> etichetă RO).
# Ordinea = ordinea logică a formularului (bancă -> tip -> localizare -> descriere -> raport -> evaluator).
CAMPURI_OBLIGATORII: dict[str, str] = {
    "banca": "Banca / utilizatorul desemnat (creditorul)",
    "tip_proprietate": "Tipul proprietății",
    "subtip_proprietate": "Subtipul proprietății",
    "cod_postal": "Codul poștal",
    "judet": "Județul",
    "localitate": "Localitatea",
    "suprafata": "Suprafața",
    "valoare_piata": "Valoarea de piață (concluzia evaluatorului)",
    "moneda": "Moneda",
    "data_evaluarii": "Data evaluării",
    "evaluator_nume": "Numele evaluatorului",
    "evaluator_legitimatie": "Legitimația ANEVAR a evaluatorului",
    "nr_raport": "Numărul de identificare a raportului",
}


def _gol(valoare: object) -> bool:
    """Un câmp e considerat lipsă dacă e None sau șir gol (după strip). 0/Decimal('0') ar fi prinse de gt=0."""
    if valoare is None:
        return True
    if isinstance(valoare, str):
        return not valoare.strip()
    return False


def valideaza_campuri_minime(campuri: CampuriMinimeBIG) -> list[str]:
    """Întoarce lista etichetelor câmpurilor minime BIG LIPSĂ (gol => listat). Listă goală = complet.

    Folosit ca checklist înainte de transmiterea manuală în portalul BIG: dacă lista e nevidă,
    înregistrarea NU e gata de trimis.
    """
    lipsuri: list[str] = []
    for camp, eticheta in CAMPURI_OBLIGATORII.items():
        if _gol(getattr(campuri, camp, None)):
            lipsuri.append(eticheta)
    return lipsuri


def este_complet(campuri: CampuriMinimeBIG) -> bool:
    """True dacă toate câmpurile minime BIG sunt prezente (gata de înregistrare)."""
    return not valideaza_campuri_minime(campuri)


# ── Mapper: dosar/meta al aplicației -> payload BIG ──────────────────────────────────────────────
def construieste_payload_big(
    *,
    meta: dict | None = None,
    profil: dict | None = None,
    localizare: dict | None = None,
    descriere: dict | None = None,
    valoare_finala: Decimal | str | float | None = None,
) -> CampuriMinimeBIG:
    """Construiește câmpurile BIG dintr-un dosar/meta al aplicației (dict-uri simple, fără dependențe).

    Acceptă dict-uri (nu modele pydantic) ca să rămână cuplat lejer cu restul aplicației:
      - `meta`: câmpurile administrative (client, beneficiar/banca, evaluator, date, nr lucrare) —
        forma `EvaluationMeta` (vezi models/meta.py).
      - `profil`: profilul evaluării (`tip_activ`, `abordari_aplicabile`) — vezi profil.py.
      - `localizare`: {cod_postal, judet, localitate, strada}.
      - `descriere`: {suprafata, um_suprafata, utilitati, an_constructie}.
      - `valoare_finala`: concluzia (ReconciledResult.valoare_finala); dacă lipsește, se ia din
        `meta['valoare_piata']` dacă există.

    Toate cheile sunt opționale: ce lipsește rămâne gol -> apare în checklist-ul de lipsuri.
    """
    meta = meta or {}
    profil = profil or {}
    localizare = localizare or {}
    descriere = descriere or {}

    tip_activ = str(profil.get("tip_activ", "") or "")
    tip_big = tip_proprietate_big(tip_activ)
    subtip = profil.get("subtip_proprietate") or subtip_implicit(tip_activ)

    abordari = profil.get("abordari_aplicabile") or []
    abordare = abordari[0] if abordari else profil.get("abordare")

    val = valoare_finala if valoare_finala is not None else meta.get("valoare_piata")

    return CampuriMinimeBIG(
        banca=str(meta.get("beneficiar", "") or ""),
        cod_bic=meta.get("cod_bic"),
        tip_proprietate=tip_big,
        subtip_proprietate=subtip,
        cod_postal=localizare.get("cod_postal"),
        judet=localizare.get("judet"),
        localitate=localizare.get("localitate"),
        strada=localizare.get("strada"),
        suprafata=_dec(descriere.get("suprafata")),
        um_suprafata=str(descriere.get("um_suprafata", "mp") or "mp"),
        utilitati=list(descriere.get("utilitati", []) or []),
        an_constructie=descriere.get("an_constructie"),
        valoare_piata=_dec(val),
        moneda=str(meta.get("moneda", "RON") or "RON"),
        abordare=_eticheta_abordare(abordare),
        data_evaluarii=meta.get("data_evaluarii"),
        data_raportului=meta.get("data_raportului"),
        evaluator_nume=str(meta.get("evaluator_nume", "") or ""),
        evaluator_legitimatie=str(meta.get("evaluator_legitimatie", "") or ""),
        nr_raport=meta.get("nr_lucrare"),
    )


_ABORDARE_RO = {"cost": "Costuri", "comparatie": "Comparație directă", "venit": "Venit"}


def _eticheta_abordare(abordare: str | None) -> str | None:
    if not abordare:
        return None
    return _ABORDARE_RO.get(str(abordare).strip().lower(), str(abordare))


def _dec(valoare: Decimal | str | float | int | None) -> Decimal | None:
    """Convertește în Decimal tolerant (None / gol -> None). Valori ne-numerice -> None (nu aruncă)."""
    if valoare is None or valoare == "":
        return None
    if isinstance(valoare, Decimal):
        return valoare
    try:
        return Decimal(str(valoare))
    except (ValueError, ArithmeticError):
        return None


# ── Recipisa BIG (cod unic persistent + rectificative + audit trail) ─────────────────────────────
TipInregistrareBIG = Literal["initiala", "rectificativa"]


class RecipisaBIG(BaseModel):
    """Recipisa primită la salvarea unei înregistrări în BIG.

    Manual (secțiunea „Recipisa"): la salvare, dacă datele sunt corecte, utilizatorul primește o
    recipisă cu un **cod unic de identificare** a raportului în baza de date. Acest cod e PERSISTENT
    (stabil) și e folosit pentru **înregistrări rectificative**: „în cazul în care au fost introduse
    informații eronate se pot face înregistrări rectificative pe baza codului unic. Toate
    înregistrările sunt păstrate în baza de date" (audit trail inalterabil).

    Aici modelăm recipisa LOCAL (cod generat determinist din identificatorii raportului) — codul real
    vine de la portalul BIG la transmitere; câmpul `cod_unic` poate fi suprascris cu cel oficial.
    """

    cod_unic: str                                # cod unic persistent (identifică raportul în BIG)
    tip: TipInregistrareBIG = "initiala"
    cod_unic_corectat: str | None = None         # la rectificativă: codul înregistrării corectate
    emisa_la: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    nr_raport: str | None = None                 # nr. de lucrare (legătura cu dosarul)


def genereaza_cod_unic(campuri: CampuriMinimeBIG) -> str:
    """Generează un cod unic LOCAL (determinist) pentru o înregistrare BIG.

    Format `BIG-<legitimatie>-<nr_raport>-<hash8>`, unde hash8 = primii 8 hex din SHA-256 peste
    identificatorii stabili (legitimație + nr raport + cod poștal + valoare). Determinist: aceleași
    date -> același cod (idempotent). Codul OFICIAL vine de la portal — acesta e un substitut local
    stabil pentru identificare/legătură până la transmitere.
    """
    legit = (campuri.evaluator_legitimatie or "x").strip() or "x"
    nr = (campuri.nr_raport or "x").strip().replace("/", "-") or "x"
    seed = "|".join([
        legit, nr,
        campuri.cod_postal or "",
        str(campuri.valoare_piata or ""),
    ])
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8]
    return f"BIG-{legit}-{nr}-{h}"


def emite_recipisa(campuri: CampuriMinimeBIG, *, cod_unic: str | None = None) -> RecipisaBIG:
    """Emite recipisa pentru o înregistrare INIȚIALĂ. Ridică ValueError dacă lipsesc câmpuri minime.

    `cod_unic` poate fi cel returnat de portalul BIG (oficial); altfel se generează local determinist.
    """
    lipsuri = valideaza_campuri_minime(campuri)
    if lipsuri:
        raise ValueError(
            "Înregistrare BIG incompletă — câmpuri minime lipsă: " + ", ".join(lipsuri)
        )
    return RecipisaBIG(
        cod_unic=cod_unic or genereaza_cod_unic(campuri),
        tip="initiala",
        nr_raport=campuri.nr_raport,
    )


def emite_rectificativa(
    campuri: CampuriMinimeBIG, cod_unic_corectat: str, *, cod_unic: str | None = None
) -> RecipisaBIG:
    """Emite o recipisă RECTIFICATIVĂ pe baza codului unic al înregistrării corectate (manual: „pe
    baza codului unic"). Înregistrarea inițială rămâne în BIG (audit trail) — aceasta o corectează.
    """
    cod_unic_corectat = (cod_unic_corectat or "").strip()
    if not cod_unic_corectat:
        raise ValueError("Rectificativa necesită codul unic al înregistrării corectate.")
    lipsuri = valideaza_campuri_minime(campuri)
    if lipsuri:
        raise ValueError(
            "Rectificativă BIG incompletă — câmpuri minime lipsă: " + ", ".join(lipsuri)
        )
    return RecipisaBIG(
        cod_unic=cod_unic or genereaza_cod_unic(campuri),
        tip="rectificativa",
        cod_unic_corectat=cod_unic_corectat,
        nr_raport=campuri.nr_raport,
    )
