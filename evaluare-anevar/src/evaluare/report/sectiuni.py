"""Registru de secțiuni de raport. Profilul + ghidul decid ce secțiuni apar."""
from __future__ import annotations

from evaluare.profil import ProfilEvaluare

# Fiecare secțiune: (id, ghiduri în care apare). "*" = în toate ghidurile.
_REGISTRU = [
    ("coperta", "*"),
    ("scrisoare_transmitere", "*"),
    ("declaratie_conformitate", "*"),
    ("termeni_referinta", "*"),
    ("descriere_proprietate", "*"),
    ("analiza_piata", "*"),
    ("abordare_cost", "*"),
    ("abordare_comparatie", "*"),
    ("abordare_venit", ("GEV_630",)),
    ("reconciliere", "*"),
    ("alocare_valoare", ("GEV_520", "GEV_630")),
    ("gev_520", ("GEV_520",)),
    ("raportare_financiara", ("GEV_500",)),
    ("anexe", "*"),
]

ID_SECTIUNI = [s[0] for s in _REGISTRU]


def sectiuni_pentru_profil(profil: ProfilEvaluare) -> list[str]:
    """Returnează id-urile de secțiuni aplicabile profilului, în ordine."""
    out = []
    for sid, ghiduri in _REGISTRU:
        if ghiduri == "*" or profil.ghid in ghiduri:
            out.append(sid)
    return out
