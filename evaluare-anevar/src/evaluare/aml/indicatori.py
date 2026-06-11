"""Indicatori de suspiciune specifici evaluarii (HCD 58/2023 art. 6(10)).

Orice indicator activ = motiv de analiza si, dupa caz, propunere de RTS (raport tranzactie
suspecta) catre persoana responsabila / ONPCSB (Legea art. 6; HCD 58 art. 7).

Pe langa cei 10 indicatori de baza din HCD 58, catalogul include indicatori SUPLIMENTARI
specifici pietei imobiliare, preluati din "Ghid privind indicatori de suspiciune si tipologii
de spalare a banilor pe piata imobiliara" (ONPCSB, 15 feb. 2022). Acestia acopera tipologiile
ONPCSB T1 (ascunderea beneficiarului real prin societati-paravan) si T2 (canalizarea fondurilor
prin credite ipotecare), plus convertirea rapida si revanzarile succesive.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# Categorii de catalog: cei 10 de baza (HCD 58) vs. cei specifici pietei imobiliare (ghid ONPCSB).
CategorieIndicator = Literal["hcd58_baza", "ghid_imobiliar"]

# Temeiuri (citate de sursa).
_TEMEI_HCD58 = "HCD 58/2023 art. 6(10)"
_TEMEI_GHID = "Ghid ONPCSB indicatori SB piata imobiliara (15 feb. 2022)"


class Indicator(BaseModel):
    cheie: str
    text: str
    temei: str = _TEMEI_HCD58
    categorie: CategorieIndicator = "hcd58_baza"


# Cei 10 indicatori de baza, in ordinea din HCD 58 art. 6(10).
INDICATORI_HCD58: list[Indicator] = [
    Indicator(cheie="graba_excesiva",
              text="Comportament suspect: grabă excesivă a clientului."),
    Indicator(cheie="presiune_documente_insuficiente",
              text="Presiuni pentru întocmirea raportului fără documente suficiente."),
    Indicator(cheie="nemultumire_nejustificata",
              text="Nemulțumire nejustificată a clientului."),
    Indicator(cheie="presiune_valoare_predeterminata",
              text="Presiuni pentru obținerea unei anumite valori și/sau opinii."),
    Indicator(cheie="scop_nedefinit",
              text="Nedefinirea scopului concret al evaluării."),
    Indicator(cheie="pep_implicat",
              text="Persoane expuse public (PEP) implicate în operațiunile juridice legate de evaluare."),
    Indicator(cheie="istoric_atipic_tranzactionare",
              text="Istoric atipic de mare al tranzacționării bunului într-o perioadă scurtă."),
    Indicator(cheie="tranzactii_in_dezacord_cu_piata",
              text="Tranzacții anterioare (vânzări/închirieri) în total dezacord cu piața, nejustificate."),
    Indicator(cheie="drepturi_litigioase",
              text="Existența unor drepturi litigioase în legătură cu activul evaluat."),
    Indicator(cheie="antecedente_penale",
              text="Antecedente penale ale persoanelor implicate."),
]

# Indicatori SUPLIMENTARI specifici pietei imobiliare (Ghid ONPCSB feb. 2022).
# Aditivi fata de cei 10 de baza; declanseaza aceeasi analiza/propunere de RTS.
INDICATORI_GHID_IMOBILIAR: list[Indicator] = [
    # Tipologia ONPCSB de convertire rapida / revanzari (T „flipping”).
    Indicator(cheie="revanzari_rapide_pret_diferit",
              text="Revânzări rapide succesive ale aceluiași imobil, cu creștere/scădere "
                   "semnificativă și nejustificată a prețului.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="cumparari_frecvente_fara_crestere_portofoliu",
              text="Client care cumpără și vinde proprietăți în mod frecvent, fără ca numărul "
                   "de proprietăți deținute să crească (flipping).",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="diferenta_mare_piata_pret",
              text="Diferență mare, nejustificată, între valoarea de piață și prețul de "
                   "tranzacționare declarat (sub/supraevaluare).",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="pret_sub_valoarea_de_piata",
              text="Preț de vânzare semnificativ sub prețul pieței (posibilă subevaluare cu "
                   "plata diferenței „la negru”).",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="onorariu_peste_piata",
              text="Onorariu oferit peste nivelul pieței pentru a influența rezultatul/opinia "
                   "evaluării.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    # Tipologia ONPCSB T1 — ascunderea beneficiarului real (societate-paravan / offshore / interpus).
    Indicator(cheie="structura_offshore_paravan",
              text="Cumpărător/client persoană juridică cu structură opacă: societate-paravan, "
                   "offshore, acțiuni la purtător sau structură complexă a acționariatului.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="companie_fara_substanta",
              text="Compania proprietară nu are activitate fiscală, angajați, sediu real sau "
                   "prezență web și/sau e recent înființată, cu resurse mici față de valoarea "
                   "proprietății.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="proprietar_interpus",
              text="Indicii de proprietar interpus (nominee): titular cu venituri/patrimoniu "
                   "insuficiente, rudă/asociat al beneficiarului real ori legat de un PEP.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="adresa_neclara",
              text="Adresă neclară a proprietarului (căsuță poștală, sediu la cabinet de avocat/notar).",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    # Tipologia ONPCSB T2 — canalizarea fondurilor prin credite ipotecare.
    Indicator(cheie="credite_ipotecare_multiple_sau_umflate",
              text="Credite ipotecare multiple, supradimensionate față de valoare sau ipotecări "
                   "repetate ale aceluiași imobil.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="venituri_neconcordante",
              text="Neconcordanță între veniturile/patrimoniul clientului și valoarea proprietății "
                   "ori standardul de viață.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    # Riscuri de finantare / numerar atipic.
    Indicator(cheie="plati_numerar_atipice",
              text="Plăți în numerar atipice (avans, rate ipotecare sau renovări plătite cu "
                   "numerar/fonduri de proveniență neclară).",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="cumparare_fara_vizionare",
              text="Cumpărător care achiziționează fără a vedea proprietatea sau fără interes "
                   "vizibil pentru caracteristicile acesteia.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="distanta_geografica_inexplicabila",
              text="Distanță geografică mare și inexplicabilă între locația proprietății și cea a "
                   "cumpărătorului (de ce nu un evaluator/cumpărător local?).",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
    Indicator(cheie="vanzare_prin_cesiune",
              text="Vânzare prin cesiune înainte de contractul final (cumpărător intermediar "
                   "neînregistrat pe titlu), eventual repetată.",
              temei=_TEMEI_GHID, categorie="ghid_imobiliar"),
]

# Catalog complet (de baza + specifici imobiliarei), in ordine stabila.
INDICATORI: list[Indicator] = [*INDICATORI_HCD58, *INDICATORI_GHID_IMOBILIAR]

_CHEI = [i.cheie for i in INDICATORI]


class SemnaleIndicatori(BaseModel):
    """Bifele evaluatorului pentru toti indicatorii (implicit toate False)."""

    # --- Cei 10 de baza (HCD 58 art. 6(10)) ---
    graba_excesiva: bool = False
    presiune_documente_insuficiente: bool = False
    nemultumire_nejustificata: bool = False
    presiune_valoare_predeterminata: bool = False
    scop_nedefinit: bool = False
    pep_implicat: bool = False
    istoric_atipic_tranzactionare: bool = False
    tranzactii_in_dezacord_cu_piata: bool = False
    drepturi_litigioase: bool = False
    antecedente_penale: bool = False

    # --- Suplimentari, specifici pietei imobiliare (Ghid ONPCSB feb. 2022) ---
    revanzari_rapide_pret_diferit: bool = False
    cumparari_frecvente_fara_crestere_portofoliu: bool = False
    diferenta_mare_piata_pret: bool = False
    pret_sub_valoarea_de_piata: bool = False
    onorariu_peste_piata: bool = False
    structura_offshore_paravan: bool = False
    companie_fara_substanta: bool = False
    proprietar_interpus: bool = False
    adresa_neclara: bool = False
    credite_ipotecare_multiple_sau_umflate: bool = False
    venituri_neconcordante: bool = False
    plati_numerar_atipice: bool = False
    cumparare_fara_vizionare: bool = False
    distanta_geografica_inexplicabila: bool = False
    vanzare_prin_cesiune: bool = False

    # observatii libere ale evaluatorului. max_length (F-15-4): o observatie legitima e scurta;
    # plafonul opreste balonarea raspunsului /api/aml/evalueaza (campul e reflectat inapoi).
    observatii: str = Field(default="", max_length=2000)

    model_config = {"extra": "forbid"}


def evalueaza_indicatori(semnale: SemnaleIndicatori) -> list[Indicator]:
    """Returneaza indicatorii activi (bifati), in ordinea din catalog."""
    activi = {c for c in _CHEI if getattr(semnale, c)}
    return [i for i in INDICATORI if i.cheie in activi]


def propune_rts(semnale: SemnaleIndicatori) -> bool:
    """Daca exista cel putin un indicator activ => se propune analiza/RTS (HCD 58 art. 7)."""
    return any(getattr(semnale, c) for c in _CHEI)
