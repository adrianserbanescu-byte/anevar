"""Margine de an plauzibil pentru datele AML.

a407aa4 a adaugat validatori de FORMAT ISO pe campurile de tip data (azi, data_tranzactie,
data_inregistrare, data_incetare_functie), dar nu si pe LIMITE. O data ISO valida dar absurda
(ex. 9999-12-31) trecea de validare si crapa downstream in aritmetica de date:
  - risc._adauga_luni: date(base.year + luni//12, ...) -> ValueError year out of range
  - store._adauga_ani: d.replace(year=d.year + 5) -> ValueError (an > 9999)
  - raportare.suspendare_pana_la: date.fromisoformat(...) + timedelta -> OverflowError
Toate -> HTTP 500 (RUNDA 9). Marginirea anului la intrare le transforma in 422 (input invalid).
"""
from __future__ import annotations

from datetime import date

# Datele de retentie (+5 ani, Legea art. 21) si de reevaluare (+max 36 luni) adauga cel mult
# ~5 ani peste data de intrare: 2200 + 5 = 2205, mult sub limita anului maxim al lui `date` (9999),
# deci nu mai apare overflow. 1900 = limita inferioara rezonabila pentru o data de tranzactie/PEP.
AN_MIN_DATA = 1900
AN_MAX_DATA = 2200


def verifica_an_plauzibil(d: date) -> None:
    """Ridica ValueError daca anul lui `d` e in afara [AN_MIN_DATA, AN_MAX_DATA].

    Apelata de validatorii Pydantic dupa `date.fromisoformat`, transforma o data implauzibila in
    422 (input invalid) in loc de 500 (overflow aritmetic downstream)."""
    if not (AN_MIN_DATA <= d.year <= AN_MAX_DATA):
        raise ValueError(
            f"Anul datei ({d.year}) este implauzibil; foloseste un an intre "
            f"{AN_MIN_DATA} si {AN_MAX_DATA}."
        )
