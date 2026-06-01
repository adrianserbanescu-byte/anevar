"""Scoringul de similaritate pentru descoperirea comparabilelor (vezi spec 5.3).

Produce un ScoreBreakdown cu un camp `explicatie` auto-continut (formula cu numere),
astfel incat rezultatul sa fie inteles fara a citi specificatia.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from evaluare.discovery.profiles import (
    SubjectProfile, CandidateProfile, AttributeBreakdown, ScoreBreakdown,
)

# Ponderi dupa prioritatea atributelor (spec 5.3). De calibrat ulterior.
PONDERI = {"an": 5, "stare": 4, "finisaj": 3, "incalzire": 2, "teren": 1}

PRAG_AN = 25                 # ani peste care diferenta e maxima
TREPTE_STARE = 4             # 5 trepte -> diferenta maxima 4
TREPTE_FINISAJ = 3           # 4 trepte -> diferenta maxima 3
PRAG_INCREDERE_LIPSA = 3     # >= 3 atribute lipsa -> incredere scazuta


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


def d_teren(s: Decimal, c: Decimal) -> float:
    if s == 0:
        return 1.0
    return min(float(abs(s - c) / s), 1.0)


def _d_pentru(nume: str, sv, cv) -> Optional[float]:
    if sv is None or cv is None:
        return None
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
    raise ValueError(f"Atribut necunoscut: {nume}")


_ETICHETE = {"an": "An", "stare": "Stare", "finisaj": "Finisaj",
             "incalzire": "Încălzire", "teren": "Teren"}


def scor_candidat(subiect: SubjectProfile, candidat: CandidateProfile) -> ScoreBreakdown:
    """Scoreaza un candidat fata de subiect; intoarce breakdown + explicatie."""
    atribute: list[AttributeBreakdown] = []
    suma_contributii = 0.0
    suma_ponderi = 0
    termeni_formula: list[str] = []
    ponderi_formula: list[str] = []
    necunoscute = 0

    for nume in ["an", "stare", "finisaj", "incalzire", "teren"]:
        sv = getattr(subiect, nume)
        cv = getattr(candidat, nume)
        pondere = PONDERI[nume]
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
    relevanta = round(100 * (1 - dissim))
    cunoscute = 5 - necunoscute
    incredere_scazuta = necunoscute >= PRAG_INCREDERE_LIPSA

    numarator = " + ".join(termeni_formula) if termeni_formula else "0"
    numitor = "+".join(ponderi_formula) if ponderi_formula else "1"
    excluse = [_ETICHETE[n] for n in ["an", "stare", "finisaj", "incalzire", "teren"]
               if getattr(subiect, n) is None or getattr(candidat, n) is None]
    nota_excluse = (f" {', '.join(excluse)}: nementionat (exclus din calcul)."
                    if excluse else "")
    explicatie = (
        f"Relevanță {relevanta}% = 100 × (1 − ({numarator}) / ({numitor})) "
        f"= 100 × (1 − {dissim:.3f}).{nota_excluse}"
    )

    return ScoreBreakdown(
        relevanta=relevanta, dissimilaritate=round(dissim, 4), atribute=atribute,
        atribute_cunoscute=cunoscute, incredere_scazuta=incredere_scazuta,
        explicatie=explicatie,
    )


def metodologie() -> list[dict]:
    """Descrie metodologia de scoring pentru afișare (tabel UI, înainte de rezultate)."""
    total = sum(PONDERI.values())  # 15
    randuri = [
        ("An", "an", "min(|an_subiect - an_anunt| / 25, 1)"),
        ("Stare", "stare", "|treapta_subiect - treapta_anunt| / 4  (5 trepte)"),
        ("Finisaj", "finisaj", "|treapta_subiect - treapta_anunt| / 3  (4 trepte)"),
        ("Încălzire", "incalzire", "0 (aceeasi) / 0.5 (aceeasi familie) / 1 (diferita)"),
        ("Teren", "teren", "min(|teren_subiect - teren_anunt| / teren_subiect, 1)"),
    ]
    out = []
    for i, (eticheta, cheie, formula) in enumerate(randuri, start=1):
        p = PONDERI[cheie]
        out.append({
            "nr": i, "atribut": eticheta, "pondere": p,
            "cota": f"{round(100 * p / total)}%", "formula": formula,
        })
    return out
