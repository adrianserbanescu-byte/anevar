"""Extractoare regex pe textul documentelor (CF, releveu, plan, CPE). Tolerante la diacritice.

Filozofia (ca la url_parser): regex pe text intai; VLM doar ca plasa de siguranta (vezi vlm.py).
Toate campurile sunt optionale — se propun, evaluatorul confirma.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from evaluare.ingestie.models import DateExtraseCF, DateReleveu, DatePlan, DateCPE


def _num(s: str) -> Optional[Decimal]:
    """Parseaza un numar din text RO. '.' = mii daca urmeaza 3 cifre; ',' = zecimala."""
    s = (s or "").strip()
    if not s:
        return None
    if "," in s:                       # virgula = zecimala; punct = mii
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):   # 1.910 / 12.500 -> mii
        s = s.replace(".", "")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def extrage_cf(text: str) -> DateExtraseCF:
    """Extras de carte funciara: nr. cadastral, CF, suprafata, proprietari, sarcini."""
    d = DateExtraseCF()
    m = re.search(r"(?:nr\.?\s*cadastral|num[ăa]r\s+cadastral|cad\.?)\s*:?\s*(\d{2,7})",
                  text, re.IGNORECASE)
    if m:
        d.numar_cadastral = m.group(1)
    m = re.search(r"(?:carte\s+funciar[ăa]|\bCF)\s*(?:nr\.?)?\s*:?\s*(\d{2,7})", text, re.IGNORECASE)
    if m:
        d.carte_funciara = m.group(1)
    m = re.search(r"suprafa[țtţ][ăaã]\s*(?:de)?\s*:?\s*([\d.,]+)\s*m\.?p", text, re.IGNORECASE)
    if m:
        d.suprafata = _num(m.group(1))
    for m in re.finditer(r"proprietar[i]?\s*:?\s*([A-ZȘȚĂÂÎ][\w .\-ȘșȚțĂăÂâÎî]{4,50})",
                         text, re.IGNORECASE):
        nume = m.group(1).strip(" .")
        if nume and nume.lower() not in (p.lower() for p in d.proprietari):
            d.proprietari.append(nume)
    m = re.search(r"(f[ăa]r[ăa]\s+sarcini|ipotec[ăaã][^.\n]{0,40})", text, re.IGNORECASE)
    if m:
        d.sarcini = m.group(1).strip()
    return d


def extrage_releveu(text: str) -> DateReleveu:
    """Releveu: arie utila, arie construita, regim de inaltime."""
    d = DateReleveu()
    m = re.search(r"(?:arie|suprafa[țtţ][ăaã])\s+util[ăaã]\s*:?\s*([\d.,]+)", text, re.IGNORECASE)
    if m:
        d.arie_utila = _num(m.group(1))
    m = re.search(r"(?:arie|suprafa[țtţ][ăaã])\s+construit[ăaã]\s*:?\s*([\d.,]+)", text, re.IGNORECASE)
    if m:
        d.arie_construita = _num(m.group(1))
    m = re.search(r"regim\s+(?:de\s+)?[îi]n[ăaã]l[țtţ]ime\s*:?\s*([SDP][A-Za-z0-9+]{1,16})",
                  text, re.IGNORECASE)
    if m:
        d.regim_inaltime = m.group(1)
    return d


def extrage_plan(text: str) -> DatePlan:
    """Plan de amplasament: suprafata teren si deschidere (front stradal)."""
    d = DatePlan()
    m = re.search(r"suprafa[țtţ][ăaã]\s+teren\s*:?\s*([\d.,]+)", text, re.IGNORECASE)
    if not m:
        m = re.search(r"\bS\s*=\s*([\d.,]+)\s*m\.?p", text, re.IGNORECASE)
    if m:
        d.suprafata_teren = _num(m.group(1))
    m = re.search(r"(?:deschidere|front\s+stradal)\s*:?\s*([\d.,]+)\s*m\b", text, re.IGNORECASE)
    if m:
        d.deschidere = _num(m.group(1))
    return d


def extrage_cpe(text: str) -> DateCPE:
    """Certificat de performanta energetica: clasa + consum."""
    d = DateCPE()
    m = re.search(r"clas[ăaã]\s+(?:energetic[ăaã]|de\s+eficien[țtţ][ăaã]\s+energetic[ăaã])"
                  r"\s*:?\s*([A-G])\b", text, re.IGNORECASE)
    if m:
        d.clasa_energetica = m.group(1).upper()
    m = re.search(r"consum[^\d]{0,30}([\d.,]+)\s*kwh", text, re.IGNORECASE)
    if m:
        d.consum = _num(m.group(1))
    return d
