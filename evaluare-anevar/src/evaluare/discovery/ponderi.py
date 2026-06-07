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

# Ponderile istorice (modelul casei) — sursa unică de adevăr până la calibrarea Adi.
PONDERI_BAZA: dict[str, int] = {
    "suprafata_construita": 5, "an": 5, "stare": 4, "finisaj": 3, "incalzire": 2, "teren": 1,
}

# Ponderi per categorie de proprietate (`tip_activ`). COMPROMIS TEMPORAR: toate = PONDERI_BAZA
# (comportament identic cu modelul casei). Când Adi decide D1–D5, se schimbă DOAR aici.
PONDERI_PER_CATEGORIE: dict[str, dict[str, int]] = {
    "casa": dict(PONDERI_BAZA),
    "apartament": dict(PONDERI_BAZA),
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
