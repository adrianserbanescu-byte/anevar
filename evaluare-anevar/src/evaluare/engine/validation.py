"""Loops de validare: blocheaza propagarea erorilor sau alerteaza evaluatorul."""
from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from statistics import median
from typing import Literal

from pydantic import BaseModel

from evaluare.engine.land import ajustare_bruta as ajustare_bruta_teren
from evaluare.engine.land import pret_mp_corectat
from evaluare.engine.market import ajustare_bruta, pret_total_corectat, pret_unitar_brut
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.models.property import BuildingData, LandData

Nivel = Literal["blocheaza", "alerteaza"]

# Praguri default (alias la config) — valorile efective vin din MetodologieConfig (M5, configurabil).
LIMITA_AJUSTARE_BRUTA = IMPLICIT.limita_ajustare_bruta
PRAG_OUTLIER = IMPLICIT.prag_outlier   # deviatie relativa fata de mediana
MIN_COMPARABILE = IMPLICIT.min_comparabile

# --------------------------------------------------------------------------- #
# Euristici de OMOGENITATE / RECENȚĂ / PROXIMITATE (articole-piata-1/2; SINTEZA I-9, I-10).
# Praguri practice din procesul în 6 pași (Nicolescu): comparabile vândute în ultimele 3–6 luni,
# rază < 1 km la garantare. SEV 2025 NU le fixează numeric -> sunt ALERTE (euristici), nu blocaje.
# --------------------------------------------------------------------------- #

# I-9 — banda de dispersie a pretului unitar brut sub care comparabilele sunt „segment unic"
# (capcana (a) Nicolescu): preturi unitare foarte apropiate intre ele = un singur nivel de pret/confort,
# imagine nereprezentativa a pietei. Fractie din mediana (max-min)/mediana.
PRAG_SEGMENT_UNIC = Decimal("0.03")     # < 3% dispersie totala -> segment de pret unic (alerta)

# I-9 — recenta: comparabile mai vechi de ~6 luni -> alerta (3-6 luni in articol; folosim 6 luni = capatul lax)
PRAG_RECENTA_LUNI = 6

# I-9 — proximitate: la garantare, comparabile din alta localitate fara ajustare de localizare -> alerta
# (capcana (d) Nicolescu: sub-piata socio-economica gresita). Detectie pe text (localitate diferita).


def _parse_data(s: str | None) -> date | None:
    """Extrage o data dintr-un text liber (accepta ISO `2025-01-15`, `15.01.2025`, `15/01/2025`).
    Returneaza None daca nu se poate parsa (camp gol / format necunoscut) — fara exceptii."""
    if not s:
        return None
    txt = s.strip()
    # ISO: 2025-01-15 (sau cu ora dupa)
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", txt)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    # RO: 15.01.2025 / 15/01/2025 (zi.luna.an)
    m = re.search(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", txt)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def _luni_intre(mai_vechi: date, mai_nou: date) -> int:
    """Numar aproximativ de luni intregi intre doua date (mai_nou - mai_vechi)."""
    luni = (mai_nou.year - mai_vechi.year) * 12 + (mai_nou.month - mai_vechi.month)
    if mai_nou.day < mai_vechi.day:
        luni -= 1
    return max(0, luni)


def _localitate(text: str | None) -> str | None:
    """Normalizeaza un text de localizare pentru comparatie grosiera (lower, fara diacritice uzuale,
    fara spatii multiple). Returneaza None daca textul e gol."""
    if not text or not text.strip():
        return None
    t = text.strip().lower()
    for a, b in (("ă", "a"), ("â", "a"), ("î", "i"), ("ș", "s"), ("ş", "s"), ("ț", "t"), ("ţ", "t")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t)


class Issue(BaseModel):
    """O problema de validare."""

    nivel: Nivel
    mesaj: str


def valideaza_proprietate(land: LandData, building: BuildingData) -> list[Issue]:
    """Valideaza datele fizice/cadastrale ale proprietatii."""
    issues: list[Issue] = []
    if land.suprafata <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Suprafata terenului trebuie sa fie > 0."))
    if building.au <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Aria utila (Au) trebuie sa fie > 0."))
    if building.acd <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Aria construita desfasurata (Acd) trebuie sa fie > 0."))
    if building.au > building.acd:
        issues.append(Issue(nivel="blocheaza", mesaj="Au nu poate depasi Acd."))
    if (building.etaj is not None and building.nr_niveluri_bloc is not None
            and building.etaj > building.nr_niveluri_bloc):
        issues.append(Issue(nivel="blocheaza",
                            mesaj="Etajul nu poate depasi numarul de niveluri ale blocului."))
    return issues


def valideaza_omogenitate(comparables: list[Comparable],
                          data_evaluarii: str | None = None) -> list[Issue]:
    """I-9 — euristici de OMOGENITATE a comparabilelor de piata (cele 4 capcane Nicolescu + recenta).

    ADITIV, doar ALERTE (SEV nu fixeaza pragurile). Verifica:
      (a) `segment de pret unic` — toate preturile unitare brute intr-o banda foarte ingusta (< 3%):
          comparabilele acopera un singur nivel de pret/confort -> imagine nereprezentativa a pietei;
      (d) `sub-piata socio-economica gresita` — comparabile fara nicio ajustare de localizare (cand
          unul ar trebui sa o aiba) NU se poate decide aici fara coordonate; ramane pe garda de
          proximitate teren / pe recenta;
      `recenta` — comparabile mai vechi de PRAG_RECENTA_LUNI fata de data evaluarii (3-6 luni in proces).
    Pragurile (a) si recenta sunt suficiente fara coordonate; (b)/(c) cad pe outlier + ajustare bruta.
    """
    issues: list[Issue] = []
    if len(comparables) < 2:
        return issues

    # (a) segment de pret unic — dispersia totala a pretului unitar brut
    preturi = [pret_unitar_brut(c) for c in comparables]
    med = Decimal(str(median([float(p) for p in preturi])))
    if med > 0:
        disp = (max(preturi) - min(preturi)) / med
        if disp < PRAG_SEGMENT_UNIC:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=(f"Omogenitate (capcana «segment de pret unic»): toate comparabilele au pretul "
                       f"unitar intr-o banda foarte ingusta ({disp:.1%} dispersie). Verificati ca "
                       f"selectia acopera niveluri de pret/confort reprezentative pentru piata, nu un "
                       f"singur segment."),
            ))

    # recenta — comparabile mai vechi de prag fata de data evaluarii
    ref = _parse_data(data_evaluarii)
    if ref is not None:
        for i, c in enumerate(comparables):
            d = _parse_data(c.data_oferta)
            if d is None:
                continue
            luni = _luni_intre(d, ref)
            if luni > PRAG_RECENTA_LUNI:
                issues.append(Issue(
                    nivel="alerteaza",
                    mesaj=(f"Comparabilul {i}: vechime ~{luni} luni (> {PRAG_RECENTA_LUNI} luni fata de "
                           f"data evaluarii). Procesul de evaluare pentru garantare prefera comparabile "
                           f"din ultimele 3-6 luni; o comparabila veche poate denatura valoarea."),
                ))
    return issues


def valideaza_oferta_tranzactie(comparables: list[Comparable]) -> list[Issue]:
    """I-10 — comparabil pe OFERTA fara ajustare oferta->tranzactie (risc speculativ).

    ADITIV, doar ALERTE. Cand `tip_oferta == "oferta"` si NU exista nicio ajustare in etapa de
    tranzactie (negociere / oferta->tranzactie), pretul de oferta intra necorectat in valoare —
    prefera in general tranzactii reale (Nicolescu: ofertele urmaresc adesea interese speculative).
    """
    issues: list[Issue] = []
    for i, c in enumerate(comparables):
        if c.tip_oferta != "oferta":
            continue
        are_tranzactie = any(a.etapa == "tranzactie" for a in c.adjustments)
        if not are_tranzactie:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=(f"Comparabilul {i} este o OFERTA fara nicio ajustare in etapa de tranzactie "
                       f"(oferta->tranzactie / negociere). Pretul de oferta poate fi supraevaluat; "
                       f"aplicati o ajustare oferta->tranzactie sau retineti o tranzactie reala."),
            ))
    return issues


def valideaza_anti_contaminare(comparables: list[Comparable]) -> list[Issue]:
    """m-2 — garda anti-contaminare: valoarea minima din grilele notariale (HCD 74 art. 111) NU e
    valoare de piata SEV si NU poate fi sursa de comparabile.

    ADITIV, doar ALERTE. Detecteaza pe `sursa` text care indica o grila/studiu notarial
    (notar/notarial/grila notariala/HCD 74/expertize notariale). Daca o astfel de sursa apare ca
    pret comparabil, semnaleaza riscul de contaminare a valorii de piata.
    """
    issues: list[Issue] = []
    semnale = ("notar", "notarial", "grila notar", "grilă notar", "hcd 74", "hcd74",
               "expertize notariale", "camera notar")
    for i, c in enumerate(comparables):
        s = (c.sursa or "").lower()
        if any(sem in s for sem in semnale):
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=(f"Comparabilul {i}: sursa pare a fi o grila/studiu notarial (HCD 74 art. 111). "
                       f"Valoarea minima din grilele notariale NU este valoare de piata (SEV 102) si "
                       f"NU poate fi folosita ca sursa de comparabile — exclude-l din grila."),
            ))
    return issues


def valideaza_comparabile(comparables: list[Comparable],
                          cfg: MetodologieConfig = IMPLICIT,
                          data_evaluarii: str | None = None) -> list[Issue]:
    """Valideaza numarul, outlierii si limitele de ajustare ale comparabilelor (praguri din config — M5).

    Pe langa gardile M5 istorice, ruleaza si euristicile aditive de omogenitate/recenta (I-9),
    oferta->tranzactie (I-10) si anti-contaminare notariala (m-2) — toate ca ALERTE (nu blocheaza).
    `data_evaluarii` (optionala) activeaza garda de recenta.
    """
    issues: list[Issue] = []
    if len(comparables) < cfg.min_comparabile:
        issues.append(Issue(
            nivel="blocheaza",
            mesaj=f"Sunt necesare minimum {cfg.min_comparabile} comparabile (gasite: {len(comparables)}).",
        ))
        return issues

    preturi = [pret_unitar_brut(c) for c in comparables]
    med = Decimal(str(median([float(p) for p in preturi])))
    if med > 0:
        for i, p in enumerate(preturi):
            deviatie = abs(p - med) / med
            if deviatie > cfg.prag_outlier:
                issues.append(Issue(
                    nivel="alerteaza",
                    mesaj=f"Comparabilul {i} este outlier (deviatie {deviatie:.0%} fata de mediana).",
                ))

    for i, c in enumerate(comparables):
        if pret_total_corectat(c) <= 0:    # ajustari care duc pretul corectat la <=0 -> valoare nonsens
            issues.append(Issue(
                nivel="blocheaza",
                mesaj=f"Comparabilul {i}: pretul corectat este <= 0 (ajustari prea mari) — verifica ajustarile.",
            ))
        g = ajustare_bruta(c)
        if g > cfg.limita_ajustare_bruta:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=f"Comparabilul {i}: ajustare bruta {g:.0%} depaseste limita de {cfg.limita_ajustare_bruta:.0%}.",
            ))

    # Euristici aditive (I-9 / I-10 / m-2) — doar alerte, nu schimba comportamentul de blocare.
    issues += valideaza_omogenitate(comparables, data_evaluarii)
    issues += valideaza_oferta_tranzactie(comparables)
    issues += valideaza_anti_contaminare(comparables)
    return issues


def _are_ajustare_localizare_teren(comp: LandComparable) -> bool:
    """True daca un comparabil de teren are o ajustare cu element care contine «localiz»/«zona»."""
    return any("localiz" in a.element.lower() or "zona" in a.element.lower()
               for a in comp.adjustments)


def valideaza_proximitate_teren(comparables: list[LandComparable],
                                localizare_subiect: str | None = None) -> list[Issue]:
    """I-9 (teren) — garda de PROXIMITATE / sub-piata (capcana (d) Nicolescu): un comparabil de teren
    dintr-o ALTA localitate decat subiectul, FARA ajustare de localizare, risca sa apartina unei alte
    sub-piete socio-economice. ADITIV, doar ALERTE.

    Daca `localizare_subiect` lipseste, compara comparabilele intre ele: cele dintr-o localitate
    minoritara (diferita de majoritatea), fara ajustare de localizare -> alerta.
    """
    issues: list[Issue] = []
    if len(comparables) < 2:
        return issues

    subj = _localitate(localizare_subiect)
    if subj is None:
        # fara subiect: localitatea de referinta = cea mai frecventa intre comparabile
        locuri = [_localitate(c.localizare) for c in comparables]
        cunoscute = [loc for loc in locuri if loc is not None]
        if not cunoscute:
            return issues
        subj = max(set(cunoscute), key=cunoscute.count)

    for i, c in enumerate(comparables):
        loc = _localitate(c.localizare)
        if loc is None or loc == subj:
            continue
        if not _are_ajustare_localizare_teren(c):
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=(f"Comparabilul de teren {i} pare din alta localitate/zona ({c.localizare}) decat "
                       f"referinta, fara o ajustare de localizare. Verificati ca apartine aceleiasi "
                       f"sub-piete (capcana «sub-piata socio-economica gresita»)."),
            ))
    return issues


def valideaza_omogenitate_teren(comparables: list[LandComparable],
                                data_evaluarii: str | None = None) -> list[Issue]:
    """I-9 (teren) — segment de pret unic + recenta, simetric cu `valideaza_omogenitate` de la piata."""
    issues: list[Issue] = []
    if len(comparables) < 2:
        return issues
    preturi = [pret_mp_corectat(c) for c in comparables]
    med = Decimal(str(median([float(p) for p in preturi])))
    if med > 0:
        disp = (max(preturi) - min(preturi)) / med
        if disp < PRAG_SEGMENT_UNIC:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=(f"Omogenitate teren (capcana «segment de pret unic»): toate comparabilele de teren "
                       f"au pretul/mp intr-o banda foarte ingusta ({disp:.1%}). Verificati ca acopera "
                       f"niveluri de pret reprezentative."),
            ))
    ref = _parse_data(data_evaluarii)
    if ref is not None:
        for i, c in enumerate(comparables):
            d = _parse_data(c.data)
            if d is None:
                continue
            luni = _luni_intre(d, ref)
            if luni > PRAG_RECENTA_LUNI:
                issues.append(Issue(
                    nivel="alerteaza",
                    mesaj=(f"Comparabilul de teren {i}: vechime ~{luni} luni (> {PRAG_RECENTA_LUNI} luni). "
                           f"Preferati comparabile din ultimele 3-6 luni."),
                ))
    return issues


def valideaza_oferta_tranzactie_teren(comparables: list[LandComparable]) -> list[Issue]:
    """I-10 (teren) — risc speculativ pe OFERTE de teren. `LandComparable` nu are flag `tip_oferta`,
    deci semnalul e prezenta unei ajustari oferta->tranzactie in etapa de tranzactie: daca NICIUN
    comparabil de teren nu are vreo ajustare in etapa de tranzactie, alerta generala (ofertele de teren
    urmaresc adesea interese speculative — Nicolescu). ADITIV, doar ALERTE."""
    issues: list[Issue] = []
    if not comparables:
        return issues
    vreo_tranzactie = any(
        any(a.etapa == "tranzactie" for a in c.adjustments) for c in comparables
    )
    if not vreo_tranzactie:
        issues.append(Issue(
            nivel="alerteaza",
            mesaj=("Niciun comparabil de teren nu are o ajustare in etapa de tranzactie "
                   "(oferta->tranzactie). Daca preturile sunt OFERTE, aplicati o ajustare "
                   "oferta->tranzactie — riscul speculativ e mai mare la teren."),
        ))
    return issues


def valideaza_comparabile_teren(comparables: list[LandComparable],
                                cfg: MetodologieConfig = IMPLICIT,
                                localizare_subiect: str | None = None,
                                data_evaluarii: str | None = None) -> list[Issue]:
    """Valideaza comparabilele de TEREN — SIMETRIC cu valideaza_comparabile pt piata (gardile M5 lipseau
    la teren): numar minim, outlieri (deviatie de la mediana pretului/mp corectat), pret/mp corectat <= 0,
    limita ajustarii brute. `cfg.teren_selectie_include_eur` (M1) decide daca ajustarea bruta numara EUR.

    Pe langa gardile M5, ruleaza euristicile aditive de omogenitate/recenta (I-9), proximitate/sub-piata
    (I-9, capcana (d)) si oferta->tranzactie (I-10) — toate ca ALERTE."""
    issues: list[Issue] = []
    if len(comparables) < cfg.min_comparabile:
        issues.append(Issue(
            nivel="blocheaza",
            mesaj=f"Sunt necesare minimum {cfg.min_comparabile} comparabile de teren "
                  f"(gasite: {len(comparables)}).",
        ))
        return issues

    inc = cfg.teren_selectie_include_eur
    preturi = [pret_mp_corectat(c) for c in comparables]
    med = Decimal(str(median([float(p) for p in preturi])))
    if med > 0:
        for i, p in enumerate(preturi):
            deviatie = abs(p - med) / med
            if deviatie > cfg.prag_outlier:
                issues.append(Issue(
                    nivel="alerteaza",
                    mesaj=f"Comparabilul de teren {i} este outlier "
                          f"(deviatie {deviatie:.0%} fata de mediana).",
                ))

    for i, c in enumerate(comparables):
        if pret_mp_corectat(c) <= 0:
            issues.append(Issue(
                nivel="blocheaza",
                mesaj=f"Comparabilul de teren {i}: pretul/mp corectat este <= 0 (ajustari prea mari).",
            ))
        g = ajustare_bruta_teren(c, inc)
        if g > cfg.limita_ajustare_bruta:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=f"Comparabilul de teren {i}: ajustare bruta {g:.0%} depaseste limita de "
                      f"{cfg.limita_ajustare_bruta:.0%}.",
            ))

    # Euristici aditive (I-9 / I-10) — doar alerte.
    issues += valideaza_omogenitate_teren(comparables, data_evaluarii)
    issues += valideaza_proximitate_teren(comparables, localizare_subiect)
    issues += valideaza_oferta_tranzactie_teren(comparables)
    return issues


def valideaza_depreciere(building: BuildingData) -> list[Issue]:
    """Cere justificare pentru deprecierea functionala/externa nenula."""
    issues: list[Issue] = []
    are_depreciere = (
        building.functional_depreciation > 0 or building.external_depreciation > 0
    )
    if are_depreciere and not building.justificare_depreciere.strip():
        issues.append(Issue(
            nivel="blocheaza",
            mesaj="Deprecierea functionala/externa nenula necesita justificare scrisa.",
        ))
    return issues


# Avertisment GEV 520 §31/§34 — abordarea prin COST ca abordare PRINCIPALA la garantare cere
# acordul SCRIS al creditorului. Non-blocant, aditiv: doar se anexeaza la nota reconcilierii.
_AVERT_COST_GARANTARE = (
    "Abordarea prin cost ca abordare principala la garantare necesita acordul scris al "
    "creditorului (GEV 520 §31/§34)."
)


def valideaza_metoda_vs_ghid(metoda, profil) -> str | None:
    """Garda non-blocanta: metoda/abordarea PRINCIPALA = cost SI ghidul profilului = GEV_520.

    GEV 520 §31/§34 cer ACORDUL SCRIS al creditorului pentru a folosi abordarea prin cost ca
    abordare principala la garantare. Intoarce un AVERTISMENT (text) in acest caz, altfel None.
    Aditiv / backward-compatible: orice alta metoda sau orice alt ghid -> None (comportament neschimbat).
    """
    if metoda == "cost" and getattr(profil, "ghid", None) == "GEV_520":
        return _AVERT_COST_GARANTARE
    return None


def valideaza_profil(profil) -> list[Issue]:
    """Avertismente de consistenta a profilului de evaluare."""
    issues: list[Issue] = []
    if not profil.abordari_aplicabile:
        issues.append(Issue(nivel="blocheaza",
                            mesaj="Profilul nu are nicio abordare aplicabila."))
    for cheie in profil.ponderi:
        if cheie not in profil.abordari_aplicabile:
            issues.append(Issue(nivel="alerteaza",
                                mesaj=f"Ponderea {cheie} nu corespunde unei abordari aplicabile."))
    return issues
