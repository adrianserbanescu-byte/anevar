"""Serviciu AML: orchestreaza evaluarea unei relatii (risc + indicatori + screening + documente).

Pur (fara I/O de retea); datele KYC raman local. Returneaza un rezultat structurat pe care
endpoint-ul il expune evaluatorului (om-in-bucla).
"""
from __future__ import annotations

from evaluare.aml.incadrare import necesita_persoana_desemnata
from evaluare.aml.indicatori import SemnaleIndicatori, evalueaza_indicatori, propune_rts
from evaluare.aml.liste import Liste, avertisment_liste, screening
from evaluare.aml.models import ClientPF, ClientPJ, EvaluareRisc
from evaluare.aml.risc import ScopEvaluare, Semnale, evalueaza_risc

Client = ClientPF | ClientPJ

# Maparea scopului evaluarii (din dosar/meta) -> scopul AML (factor de risc — Ghidul SB/FT, cap. 2).
# Cheile acopera ambele vocabulare folosite in app: `profil.Scop` (garantare_credit/vanzare/litigii/…)
# si forme libere din `meta.scop` (text RO, ex. „Garantarea creditului ipotecar"). Necunoscut -> None
# (neutru) — aditiv, nu introduce factori noi de risc fara semnal explicit.
_SCOP_AML_DIN_DOSAR: dict[str, ScopEvaluare] = {
    # garantare credit — banca dubleaza DD -> risc redus
    "garantare_credit": "garantare_credit",
    "garantare": "garantare_credit",
    # scop fiscal / raportare -> risc redus
    "impozitare": "impozitare",
    "raportare_financiara": "raportare_financiara",
    # vanzare/cumparare pe piata libera -> risc mai mare
    "vanzare": "vanzare_piata",
    "vanzare_piata": "vanzare_piata",
    # fuziuni & achizitii -> risc
    "mna": "mna",
    # lichidare / insolventa / executare silita -> risc (subevaluare/supraevaluare)
    "lichidare": "lichidare_insolventa_executare",
    "insolventa": "lichidare_insolventa_executare",
    "executare": "lichidare_insolventa_executare",
    "executare_silita": "lichidare_insolventa_executare",
    "lichidare_insolventa_executare": "lichidare_insolventa_executare",
}

# Cuvinte-cheie pentru `meta.scop` liber (text RO). Cautate ca substring pe forma normalizata.
_SCOP_AML_DUPA_CUVANT: tuple[tuple[str, ScopEvaluare], ...] = (
    ("garantare", "garantare_credit"),
    ("credit", "garantare_credit"),
    ("ipotec", "garantare_credit"),       # „ipotecar"
    ("impozit", "impozitare"),
    ("fiscal", "impozitare"),
    ("raportare", "raportare_financiara"),
    ("contabil", "raportare_financiara"),
    ("insolvent", "lichidare_insolventa_executare"),
    ("lichidare", "lichidare_insolventa_executare"),
    ("executare", "lichidare_insolventa_executare"),
    ("vanzare", "vanzare_piata"),
    ("cumparare", "vanzare_piata"),
    ("fuziun", "mna"),
    ("achizit", "mna"),
)

_DIACRITICE = str.maketrans("ăâîșşțţ", "aaisstt")


def scop_aml_din_dosar(scop: str | None) -> ScopEvaluare | None:
    """Normalizeaza scopul evaluarii (din dosar/meta) la scopul AML (factor de risc).

    Accepta atat coduri (`profil.Scop`, ex. „garantare_credit") cat si text liber RO
    (`meta.scop`, ex. „Garantarea creditului ipotecar"). Returneaza None pentru scop necunoscut/gol
    -> factorul „produs/serviciu" ramane neutru (aditiv, fara regresie)."""
    if not scop:
        return None
    cheie = scop.strip().lower().translate(_DIACRITICE)
    if cheie in _SCOP_AML_DIN_DOSAR:
        return _SCOP_AML_DIN_DOSAR[cheie]
    for cuvant, scop_aml in _SCOP_AML_DUPA_CUVANT:
        if cuvant in cheie:
            return scop_aml
    return None


def _nume_screening(client: Client) -> list[str]:
    nume: list[str] = []
    if isinstance(client, ClientPF):
        nume.append(f"{client.persoana.nume} {client.persoana.prenume}".strip())
    else:
        nume.append(client.denumire)
        if client.reprezentant_legal.nume:
            nume.append(f"{client.reprezentant_legal.nume} {client.reprezentant_legal.prenume}".strip())
        for br in client.beneficiari_reali:
            nume.append(f"{br.nume} {br.prenume}".strip())
    return [n for n in nume if n]


def _avertismente_conformitate(
    client: Client,
    evaluare: EvaluareRisc,
    *,
    sursa_fonduri: str | None,
    sursa_avere: str | None,
    aprobare_conducere_pep: bool,
) -> list[str]:
    """Avertismente aditive, NON-blocante, pentru evaluator (om-in-bucla).

    (a) Risc RIDICAT (sporit) cu EDD incomplet — Legea art. 17(1)-(3): la masuri suplimentare trebuie
        stabilita sursa fondurilor/averii si, pentru PEP, aprobarea conducerii superioare.
    (b) PJ fara consultarea Registrului Beneficiarilor Reali (RBR) — Legea art. 19(5).
    Aici doar semnalam; nu blocam fluxul si nu schimbam categoria de risc."""
    avertismente: list[str] = []

    if evaluare.categorie == "sporit":
        edd_lipsa: list[str] = []
        if not (sursa_fonduri and sursa_fonduri.strip()):
            edd_lipsa.append("sursa fondurilor")
        if not (sursa_avere and sursa_avere.strip()):
            edd_lipsa.append("sursa averii")
        # Aprobarea conducerii e ceruta de EDD doar cand exista un PEP efectiv in motivele de sporit.
        pep_in_motive = any("PEP" in m for m in evaluare.motive_sporit)
        if pep_in_motive and not aprobare_conducere_pep:
            edd_lipsa.append("aprobarea conducerii superioare (PEP)")
        if edd_lipsa:
            avertismente.append(
                "Risc ridicat necesită EDD: completați "
                + ", ".join(edd_lipsa)
                + " — Legea art. 17(1)."
            )

    if isinstance(client, ClientPJ) and not client.consultat_rbr:
        avertismente.append(
            "PJ fără consultarea Registrului Beneficiarilor Reali (RBR): "
            "consultați RBR și atașați extrasul — Legea art. 19(5)."
        )

    return avertismente


def evalueaza_relatie(
    tip_entitate: str,
    client: Client,
    *,
    azi: str,
    semnale_risc: Semnale | None = None,
    semnale_indicatori: SemnaleIndicatori | None = None,
    liste: Liste | None = None,
    scop: str | None = None,
    sursa_fonduri: str | None = None,
    sursa_avere: str | None = None,
    aprobare_conducere_pep: bool = False,
) -> dict:
    """Evalueaza o relatie de afaceri: categorie risc, indicatori, screening, documente necesare.

    `scop` = scopul evaluarii din dosar/meta (cod `profil.Scop` sau text liber RO din `meta.scop`);
    se propaga in `Semnale.scop` (factor de risc „produs/serviciu") daca nu a fost deja setat explicit
    in `semnale_risc`. Campurile EDD (`sursa_fonduri`/`sursa_avere`/`aprobare_conducere_pep`) provin
    din DosarAML si alimenteaza avertismentele de conformitate (aditiv, non-blocant)."""
    semnale_indicatori = semnale_indicatori or SemnaleIndicatori()

    # (1) Propaga scopul din dosar/meta in semnalele de risc, fara a suprascrie un scop deja dat
    # explicit in semnale_risc (precedenta semnalului explicit). Aditiv si backward-compatible.
    scop_aml = scop_aml_din_dosar(scop)
    if scop_aml is not None:
        if semnale_risc is None:
            semnale_risc = Semnale(scop=scop_aml)
        elif semnale_risc.scop is None:
            semnale_risc = semnale_risc.model_copy(update={"scop": scop_aml})

    evaluare: EvaluareRisc = evalueaza_risc(client, semnale_risc, azi=azi)
    indicatori = evalueaza_indicatori(semnale_indicatori)
    rts = propune_rts(semnale_indicatori)

    potriviri = []
    if liste is not None:
        screening_avertisment = avertisment_liste(liste, azi=azi)
        for nume in _nume_screening(client):
            potriviri.extend(p.model_dump() for p in screening(nume, liste))
    else:
        screening_avertisment = "Screening pe liste neefectuat (liste neinjectate)."

    documente = ["norme_interne", "evaluare_risc", "fisa_kyc"]
    if necesita_persoana_desemnata(tip_entitate):
        documente.append("decizie_desemnare")
    if rts:
        documente.append("rts")

    avertismente = _avertismente_conformitate(
        client, evaluare,
        sursa_fonduri=sursa_fonduri, sursa_avere=sursa_avere,
        aprobare_conducere_pep=aprobare_conducere_pep,
    )

    return {
        "evaluare_risc": evaluare.model_dump(mode="json"),
        "categorie": evaluare.categorie,
        "nivel_masuri": evaluare.nivel_masuri,
        "motive_sporit": evaluare.motive_sporit,
        "indicatori": [i.model_dump() for i in indicatori],
        "propune_rts": rts,
        "screening": potriviri,
        "screening_avertisment": screening_avertisment,
        "necesita_persoana_desemnata": necesita_persoana_desemnata(tip_entitate),
        "documente_necesare": documente,
        "avertismente": avertismente,
    }
