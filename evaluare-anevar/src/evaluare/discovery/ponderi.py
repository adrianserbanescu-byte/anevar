"""Config-driven al ponderilor de scoring pentru descoperire — PER CATEGORIE de proprietate.

P0.1 (refactor BEHAVIOR-PRESERVING): structura devine config-driven (un set de ponderi pe
`tip_activ`), dar — ⚠️ COMPROMIS TEMPORAR — **toate** categoriile folosesc deocamdată ACELEAȘI
valori (cele istorice ale casei). Astfel scorurile rămân IDENTICE; nu se schimbă niciun comportament.

Valorile efective ale ponderilor sunt DECIZIE de metodologie (bucket B / Adi — vezi D1–D5 din
`docs/descoperire-redesign/plan-implementare.md`). Vor fi calibrate ulterior și/sau expuse EDITABIL
în UI. **Nu schimba valorile aici fără decizia evaluatorului** — când se decide, se modifică DOAR
acest config (fără cod).
"""
from __future__ import annotations

import math

# Ponderile istorice (modelul casei) — sursa unică de adevăr până la calibrarea Adi.
PONDERI_BAZA: dict[str, int] = {
    "suprafata_construita": 5, "an": 5, "stare": 4, "finisaj": 3, "incalzire": 2, "teren": 1,
}

# APARTAMENT (P0.2) — model propriu: la apartament, NUMĂRUL DE CAMERE și ETAJUL sunt drivere majore,
# iar terenul e irelevant. Set + ponderi = PROPUNEREA council (calibrabilă de Adi, bucket B).
# Ordinea cheilor = ordinea de afișare/parcurgere. `etaj` e inclus structural; rămâne „nementionat"
# (exclus din calcul) până se extrage etajul din anunț — fără efect negativ până atunci.
PONDERI_APARTAMENT: dict[str, int] = {
    "suprafata_construita": 7, "etaj": 5, "nr_camere": 4, "an": 3, "stare": 2,
}

# Ponderi per categorie de proprietate (`tip_activ`). Casa + restul = modelul de bază (compromis
# temporar, behavior-preserving); APARTAMENTUL are model propriu (P0.2). Valorile = decizie Adi.
PONDERI_PER_CATEGORIE: dict[str, dict[str, int]] = {
    "casa": dict(PONDERI_BAZA),
    "apartament": dict(PONDERI_APARTAMENT),
    "comercial": dict(PONDERI_BAZA),
    "industrial": dict(PONDERI_BAZA),
    "agricol": dict(PONDERI_BAZA),
    "special": dict(PONDERI_BAZA),
}


def ponderi_pentru(tip_activ: str | None = None) -> dict[str, int]:
    """Ponderile pentru o categorie de proprietate.

    `tip_activ` necunoscut sau None → ponderile de bază (modelul casei). Behavior-preserving:
    cât timp toate categoriile = `PONDERI_BAZA`, rezultatul e identic indiferent de `tip_activ`.
    Întoarce o COPIE (nu referința la config), ca apelantul să nu mute accidental sursa.
    """
    if not tip_activ:
        return dict(PONDERI_BAZA)
    return dict(PONDERI_PER_CATEGORIE.get(tip_activ, PONDERI_BAZA))


# ── Axe de radar (D2) ────────────────────────────────────────────────────────────────────────
# Maparea atribut → axă pentru radarul multi-axă al lui C. CONFIG, calibrabil de Adi (bucket B).
# „Locație" rămâne goală (None) până la geocoding (P1.2) — n-avem încă semnal de localizare în scor.
AXE: list[str] = ["locatie", "fizic", "calitate", "functional"]
AXA_ATRIBUT: dict[str, str] = {
    "suprafata_construita": "fizic", "an": "fizic", "teren": "fizic",
    "stare": "calitate", "finisaj": "calitate",
    "nr_camere": "functional", "etaj": "functional", "incalzire": "functional",
}


def fuzioneaza_override(override: dict | None) -> dict[str, dict[str, float]]:
    """Aplică override-ul (ponderi editate de user) peste valorile default, DOAR pe categorii și
    atribute cunoscute (ignoră restul, ca să nu injecteze chei străine). Întoarce un dict nou.
    """
    rezultat: dict[str, dict[str, float]] = {
        cat: dict(p) for cat, p in PONDERI_PER_CATEGORIE.items()
    }
    if not isinstance(override, dict):
        return rezultat
    for cat, ponderi in override.items():
        if cat not in rezultat or not isinstance(ponderi, dict):
            continue
        for atr, val in ponderi.items():
            if (atr in rezultat[cat] and isinstance(val, (int, float))
                    and not isinstance(val, bool) and math.isfinite(val)):
                rezultat[cat][atr] = val
    return rezultat
