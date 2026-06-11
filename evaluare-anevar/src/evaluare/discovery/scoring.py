"""Scoringul de similaritate pentru descoperirea comparabilelor (vezi spec 5.3).

Produce un ScoreBreakdown cu un camp `explicatie` auto-continut (formula cu numere),
astfel incat rezultatul sa fie inteles fara a citi specificatia.
"""
from __future__ import annotations

from decimal import Decimal

from evaluare.discovery.ponderi import AXA_ATRIBUT, AXE, PONDERI_BAZA
from evaluare.discovery.profiles import (
    AttributeBreakdown,
    CandidateProfile,
    ScoreBreakdown,
    SubjectProfile,
)

# Ponderile sunt acum CONFIG-DRIVEN per categorie (vezi `ponderi.py`). `PONDERI` rămâne alias la
# setul de bază (modelul casei) pentru compatibilitate; `scor_candidat`/`metodologie` acceptă
# `ponderi` explicit, cu default = baza → comportament identic dacă nu se dă altceva.
PONDERI = PONDERI_BAZA

# Ordinea de parcurgere a atributelor primare la scorare.
ORDINE = ["suprafata_construita", "an", "stare", "finisaj", "incalzire", "teren"]

PRAG_AN = 25                 # ani peste care diferenta e maxima
TREPTE_STARE = 4             # 5 trepte -> diferenta maxima 4
TREPTE_FINISAJ = 3           # 4 trepte -> diferenta maxima 3
PRAG_ETAJ = 4                # diferenta de etaje peste care e maxima (apartament)
PRAG_INCREDERE_LIPSA = 3     # >= 3 atribute lipsa -> incredere scazuta

# ── Ajustari metodologice ADITIVE (recenta / proximitate / segment) ───────────────────────────
# Operationalizeaza garda G7 (articole-piata-2 §1.3 + GAP-B din articole-piata-1): proximitatea si
# RECENTA sunt principii de selectie a comparabilelor, distincte de similaritatea de atribute. Le
# aplicam ca FACTOR multiplicativ pe relevanta (post-atribute), NU ca atribut in formula — ca sa nu
# alteram contractul ScoreBreakdown.atribute si formula auditabila. Pragurile = EURISTICI (SEV 103
# A10.7 prefera recenta/proximitate dar NU fixeaza cifre) → calibrabile de Adi (bucket B).
RECENTA_GRATIE_ZILE = 180        # ~6 luni: pana aici, comparabila e „proaspata" (fara penalizare)
RECENTA_PRAG_ZILE = 540          # ~18 luni: la/peste acest prag se aplica penalizarea maxima de recenta
RECENTA_PENALIZARE_MAX = 0.30    # taie cel mult 30% din relevanta pt. anunturi foarte vechi
PROXIMITATE_GRATIE_KM = 1.0      # <1 km: aceeasi micro-piata (fara penalizare) — articol „raza <1 km"
PROXIMITATE_PRAG_KM = 15.0       # >=15 km: penalizare maxima (alta sub-piata, risc de eroare de segment)
PROXIMITATE_PENALIZARE_MAX = 0.35  # taie cel mult 35% din relevanta pt. comparabile foarte departate
SEGMENT_BONUS = 0.05             # +5% (cap la 100) cand candidatul e pe EXACT acelasi segment/sub-piata
SEGMENT_PENALIZARE = 0.20        # −20% cand segmentul difera explicit (capcana (d): alta sub-piata)


def _factor_recenta(vechime_zile: int | None) -> tuple[float, str | None]:
    """Factor de recenta in [1−RECENTA_PENALIZARE_MAX, 1]. None/proaspata → 1.0 (niciun efect).

    Liniar intre gratie (~6 luni) si prag (~18 luni); plafonat. Garanteaza backward-compat: lipsa
    datei (None) NU schimba scorul.
    """
    if vechime_zile is None or vechime_zile <= RECENTA_GRATIE_ZILE:
        return 1.0, None
    span = max(RECENTA_PRAG_ZILE - RECENTA_GRATIE_ZILE, 1)
    frac = min((vechime_zile - RECENTA_GRATIE_ZILE) / span, 1.0)
    factor = 1.0 - RECENTA_PENALIZARE_MAX * frac
    return factor, f"recență −{round((1 - factor) * 100)}%"


def _factor_proximitate(distanta_km: float | None) -> tuple[float, str | None]:
    """Factor de proximitate in [1−PROXIMITATE_PENALIZARE_MAX, 1]. None/aproape → 1.0 (niciun efect)."""
    if distanta_km is None or distanta_km <= PROXIMITATE_GRATIE_KM:
        return 1.0, None
    span = max(PROXIMITATE_PRAG_KM - PROXIMITATE_GRATIE_KM, 0.001)
    frac = min((distanta_km - PROXIMITATE_GRATIE_KM) / span, 1.0)
    factor = 1.0 - PROXIMITATE_PENALIZARE_MAX * frac
    return factor, f"proximitate −{round((1 - factor) * 100)}%"


def _factor_segment(segment_subiect: str | None, segment_candidat: str | None) -> tuple[float, str | None]:
    """Bonus/penalizare de segment. Match exact → +SEGMENT_BONUS; segment explicit diferit → −penalizare.

    Daca oricare segment lipseste (None) → factor 1.0 (niciun efect = backward-compatible).
    Normalizam case/spatii ca sa nu ratam un match doar din formatare.
    """
    if not segment_subiect or not segment_candidat:
        return 1.0, None
    s = segment_subiect.strip().lower()
    c = segment_candidat.strip().lower()
    if s == c:
        return 1.0 + SEGMENT_BONUS, f"segment exact +{round(SEGMENT_BONUS * 100)}%"
    return 1.0 - SEGMENT_PENALIZARE, f"segment diferit −{round(SEGMENT_PENALIZARE * 100)}%"


def d_an(s: int, c: int) -> float:
    return min(abs(s - c) / PRAG_AN, 1.0)


def d_stare(s: int, c: int) -> float:
    return min(abs(s - c) / TREPTE_STARE, 1.0)


def d_finisaj(s: int, c: int) -> float:
    return round(min(abs(s - c) / TREPTE_FINISAJ, 1.0), 4)


def d_incalzire(s: str, c: str) -> float:
    if s == c:
        return 0.0
    fam_s = s.split("_")[0] if s else ""
    fam_c = c.split("_")[0] if c else ""
    if fam_s and fam_s == fam_c:
        return 0.5
    return 1.0


def _d_relativ(s: Decimal, c: Decimal) -> float:
    """Diferenta relativa pentru suprafete (teren / construit)."""
    if s == 0:
        return 1.0
    return min(float(abs(s - c) / s), 1.0)


def d_teren(s: Decimal, c: Decimal) -> float:
    return _d_relativ(s, c)


def d_suprafata(s: Decimal, c: Decimal) -> float:
    return _d_relativ(s, c)


def d_camere(s: int, c: int) -> float:
    """Distanta pe numarul de camere (apartament): 0 identic, 0.5 o camera, 1 doua+."""
    return min(abs(s - c) / 2, 1.0)


def d_etaj(s: int, c: int) -> float:
    """Distanta pe etaj (apartament), liniara (calibrabil de Adi).

    TODO (bucket B / council): penalizare NELINIARA — parter/ultimul etaj difera categoric de
    etajele intermediare. Deocamdata liniara, ca structura; valoarea = decizie de metodologie.
    """
    return min(abs(s - c) / PRAG_ETAJ, 1.0)


def _d_pentru(nume: str, sv, cv) -> float | None:
    if sv is None or cv is None:
        return None
    if nume == "suprafata_construita":
        return d_suprafata(sv, cv)
    if nume == "an":
        return d_an(sv, cv)
    if nume == "stare":
        return d_stare(sv, cv)
    if nume == "finisaj":
        return d_finisaj(sv, cv)
    if nume == "incalzire":
        return d_incalzire(sv, cv)
    if nume == "teren":
        return d_teren(sv, cv)
    if nume == "nr_camere":
        return d_camere(sv, cv)
    if nume == "etaj":
        return d_etaj(sv, cv)
    raise ValueError(f"Atribut necunoscut: {nume}")


_ETICHETE = {"suprafata_construita": "Supr. construită", "an": "An", "stare": "Stare",
             "finisaj": "Finisaj", "incalzire": "Încălzire", "teren": "Teren",
             "nr_camere": "Camere", "etaj": "Etaj"}

# Formula de distanta per atribut (pt. tabelul de metodologie din UI).
_FORMULE = {
    "suprafata_construita": "min(|supr_subiect - supr_anunt| / supr_subiect, 1)",
    "an": "min(|an_subiect - an_anunt| / 25, 1)",
    "stare": "|treapta_subiect - treapta_anunt| / 4  (5 trepte)",
    "finisaj": "|treapta_subiect - treapta_anunt| / 3  (4 trepte)",
    "incalzire": "0 (aceeasi) / 0.5 (aceeasi familie) / 1 (diferita)",
    "teren": "min(|teren_subiect - teren_anunt| / teren_subiect, 1)",
    "nr_camere": "min(|camere_subiect - camere_anunt| / 2, 1)",
    "etaj": "min(|etaj_subiect - etaj_anunt| / 4, 1)",
}


def scor_candidat(subiect: SubjectProfile, candidat: CandidateProfile,
                  ponderi: dict[str, int] | None = None) -> ScoreBreakdown:
    """Scoreaza un candidat fata de subiect; intoarce breakdown + explicatie.

    `ponderi` = setul de ponderi per atribut (config-driven, per categorie). None → baza (casa),
    deci comportament identic cu varianta istorica daca nu se transmite nimic.
    """
    ponderi = ponderi if ponderi is not None else PONDERI_BAZA
    atribute: list[AttributeBreakdown] = []
    suma_contributii = 0.0
    suma_ponderi = 0
    termeni_formula: list[str] = []
    ponderi_formula: list[str] = []
    necunoscute = 0
    axe_contrib: dict[str, float] = dict.fromkeys(AXE, 0.0)   # pt radarul D2 (scor pe axe)
    axe_pond: dict[str, float] = dict.fromkeys(AXE, 0.0)

    for nume in ponderi:        # atributele + ordinea = configul categoriei (config-driven)
        sv = getattr(subiect, nume)
        cv = getattr(candidat, nume)
        pondere = ponderi[nume]
        d = _d_pentru(nume, sv, cv)
        valoare_candidat = candidat.texte.get(nume) or (str(cv) if cv is not None else None)
        valoare_subiect = str(sv) if sv is not None else None
        if d is None:
            necunoscute += 1
            atribute.append(AttributeBreakdown(
                nume=_ETICHETE[nume], valoare_subiect=valoare_subiect,
                valoare_candidat=valoare_candidat, d=None, pondere=pondere,
                contributie=None, cunoscut=False,
            ))
            continue
        contributie = pondere * d
        suma_contributii += contributie
        suma_ponderi += pondere
        axa = AXA_ATRIBUT.get(nume)               # acumuleaza pe axa de radar (D2)
        if axa in axe_contrib:
            axe_contrib[axa] += contributie
            axe_pond[axa] += pondere
        termeni_formula.append(f"{pondere}×{d:.2f}")
        ponderi_formula.append(str(pondere))
        atribute.append(AttributeBreakdown(
            nume=_ETICHETE[nume], valoare_subiect=valoare_subiect,
            valoare_candidat=valoare_candidat, d=round(d, 4), pondere=pondere,
            contributie=round(contributie, 4), cunoscut=True,
        ))

    if suma_ponderi == 0:
        dissim = 1.0
    else:
        dissim = suma_contributii / suma_ponderi
    relevanta_atribute = round(100 * (1 - dissim))
    cunoscute = len(ponderi) - necunoscute
    incredere_scazuta = necunoscute >= PRAG_INCREDERE_LIPSA

    numarator = " + ".join(termeni_formula) if termeni_formula else "0"
    numitor = "+".join(ponderi_formula) if ponderi_formula else "1"
    excluse = [_ETICHETE[n] for n in ponderi
               if getattr(subiect, n) is None or getattr(candidat, n) is None]
    nota_excluse = (f" {', '.join(excluse)}: nementionat (exclus din calcul)."
                    if excluse else "")

    # ── Ajustari metodologice (recenta / proximitate / segment) ───────────────────────────────
    # Aplicate MULTIPLICATIV pe relevanta de atribute. Fiecare factor e 1.0 cand semnalul lipseste
    # (None) → daca NICIUN semnal nu e prezent, `relevanta == relevanta_atribute` (backward-compat).
    f_rec, et_rec = _factor_recenta(getattr(candidat, "vechime_zile", None))
    f_prox, et_prox = _factor_proximitate(getattr(candidat, "distanta_km", None))
    f_seg, et_seg = _factor_segment(
        getattr(subiect, "segment", None), getattr(candidat, "segment", None))
    ajustari = [e for e in (et_rec, et_prox, et_seg) if e]
    factor_total = f_rec * f_prox * f_seg
    relevanta = relevanta_atribute if not ajustari else max(
        0, min(100, round(relevanta_atribute * factor_total)))

    nota_ajustari = (f" Ajustări metodologice: {', '.join(ajustari)} "
                     f"(relevanță pe atribute {relevanta_atribute}% → {relevanta}%)."
                     if ajustari else "")
    explicatie = (
        f"Relevanță {relevanta_atribute}% = 100 × (1 − ({numarator}) / ({numitor})) "
        f"= 100 × (1 − {dissim:.3f}).{nota_excluse}{nota_ajustari}"
    )

    # Scor pe fiecare axă (0-100); None dacă axa n-are atribute cunoscute (ex. „locatie" pâna la geocoding).
    axe = {ax: (round(100 * (1 - axe_contrib[ax] / axe_pond[ax])) if axe_pond[ax] > 0 else None)
           for ax in AXE}

    return ScoreBreakdown(
        relevanta=relevanta, dissimilaritate=round(dissim, 4), atribute=atribute,
        atribute_cunoscute=cunoscute, incredere_scazuta=incredere_scazuta,
        explicatie=explicatie, axe=axe,
        relevanta_atribute=relevanta_atribute, ajustari=ajustari,
    )


def metodologie(ponderi: dict[str, int] | None = None) -> list[dict]:
    """Descrie metodologia de scoring pentru afișare (tabel UI, înainte de rezultate).

    `ponderi` per categorie (config-driven); None → baza (casa)."""
    ponderi = ponderi if ponderi is not None else PONDERI_BAZA
    total = sum(ponderi.values()) or 1
    # Config-driven: atributele + ordinea vin din config (casa → 6 randuri ca inainte; apartament → setul lui).
    return [
        {"nr": i, "atribut": _ETICHETE.get(cheie, cheie), "pondere": p,
         "cota": f"{round(100 * p / total)}%", "formula": _FORMULE.get(cheie, "")}
        for i, (cheie, p) in enumerate(ponderi.items(), start=1)
    ]
