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


# Secțiunile de abordare apar doar dacă abordarea respectivă e în profil.abordari_aplicabile.
_ABORDARE_SECTIUNE = {
    "abordare_cost": "cost",
    "abordare_comparatie": "comparatie",
    "abordare_venit": "venit",
}


def sectiuni_pentru_profil(profil: ProfilEvaluare) -> list[str]:
    """Returnează id-urile de secțiuni aplicabile profilului (ghid + abordări), în ordine."""
    out: list[str] = []
    for sid, ghiduri in _REGISTRU:
        if not (ghiduri == "*" or profil.ghid in ghiduri):
            continue
        abordare = _ABORDARE_SECTIUNE.get(sid)
        if abordare is not None and abordare not in profil.abordari_aplicabile:
            continue
        out.append(sid)
    return out
