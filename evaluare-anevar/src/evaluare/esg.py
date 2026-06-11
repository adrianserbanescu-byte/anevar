"""ESG / riscuri fizice in evaluarea pentru garantarea imprumutului — gap S-5 / G1.

Materializeaza poziția oficiala ANEVAR «Punct de vedere referitor la aprecierea riscurilor fizice in
activitatea de evaluare pentru garantarea imprumutului» + GEV 520 §86–88. Modul PUR (logica + date), fara
wiring in generator/UI (follow-up separat).

Poziția de fond ANEVAR (esențiala pentru cum trateaza app-ul aceste riscuri):
  1. Cadrul normativ = GEV 520 (+ SEV 230 in nomenclatura SEV 2025; PdV-ul citeaza «SEV 310» —
     nomenclatura veche, de validat de jurist — vezi `docs/analiza-anevar/batch2/big-esg-garantare.md` §2.2).
  2. Incadrarea riscurilor fizice pe o scala de probabilitate EXCEDE competența evaluatorului autorizat
     (necesita expertiza specifica + autorizare din partea autoritaților statului).
  3. Exista autoritați oficiale care furnizeaza date de Risc/Hazard/Vulnerabilitate
     (ISU, ANM, INHGA, MMAP, ISC) + societați de asigurari care cuantifica aceste riscuri.
  4. Mecanismul corect: clientul/utilizatorul pune la dispoziție documentele oficiale inca din
     documentarea primara; pe baza lor evaluatorul PREIA informația CA ATARE in raport.
  5. Raportul de garantare NU are rolul de a ierarhiza/clasifica riscurile fizice; orice clasificare se
     face IN AFARA raportului de evaluare, de o persoana cu competențe specifice.

Regula de aur a acestui modul: se MENȚIONEAZA, NU se CUANTIFICA. Nicio funcție nu produce scoruri,
ierarhii sau probabilitați — doar text de menționare + preluarea sursei oficiale furnizate de client.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

# ── Catalogul autoritaților-sursa oficiale (nomenclator pentru atasarea sursei per risc) ──────────────
# Sursa: PdV ANEVAR, notele 1–5. Sunt autoritați ale statului cu atribuții de a furniza date oficiale
# (Risc / Hazard / Vulnerabilitate). «asigurator» = societați de asigurari care monitorizeaza/cuantifica.
AUTORITATI_SURSA: dict[str, str] = {
    "ISU": "Inspectoratul pentru Situații de Urgența",
    "ANM": "Administrația Naționala de Meteorologie",
    "INHGA": "Institutul Național de Hidrologie și Gospodarire a Apelor",
    "MMAP": "Ministerul Mediului, Apelor și Padurilor",
    "ISC": "Inspectoratul de Stat in Construcții",
    "asigurator": "Societate de asigurari (monitorizare/cuantificare riscuri)",
}


class RiscFizic(BaseModel):
    """Un risc fizic din catalogul ANEVAR, cu sursa oficiala de verificare recomandata.

    `surse_recomandate` = chei din `AUTORITATI_SURSA` (autoritați care pot emite documentul oficial pe
    baza caruia informația se preia CA ATARE in raport). NU contine scoruri/probabilitați (poziția ANEVAR).
    """

    cheie: str                       # identificator stabil (ex. "cutremure")
    denumire: str                    # denumirea afisata (textual din PdV)
    descriere: str                   # ce acopera riscul
    surse_recomandate: list[str]     # chei din AUTORITATI_SURSA — autoritați de verificare


# ── Catalogul celor 8 riscuri fizice (textual din PdV ANEVAR) ─────────────────────────────────────────
CATALOG_RISCURI_FIZICE: list[RiscFizic] = [
    RiscFizic(
        cheie="cutremure",
        denumire="Cutremure",
        descriere="Activitate seismica — risc de avariere structurala a construcției la mișcari seismice.",
        surse_recomandate=["ISC", "MMAP"],
    ),
    RiscFizic(
        cheie="alunecari_teren",
        denumire="Alunecari de teren / stabilitatea masivelor de pamant",
        descriere="Instabilitatea versanților și a masivelor de pamant care poate afecta terenul/construcția.",
        surse_recomandate=["MMAP", "ISC"],
    ),
    RiscFizic(
        cheie="falie_surpare",
        denumire="Zone de falie sau surpare, alunecari de teren",
        descriere="Amplasamente in zone de falie geologica sau predispuse la surpare/prabușire de teren.",
        surse_recomandate=["MMAP", "ISC"],
    ),
    RiscFizic(
        cheie="activitate_vulcanica",
        denumire="Activitatea vulcanica",
        descriere="Risc de fenomene vulcanice in zona amplasamentului.",
        surse_recomandate=["MMAP"],
    ),
    RiscFizic(
        cheie="furtuni_extreme",
        denumire="Furtuni extreme",
        descriere="Fenomene meteorologice extreme (vant, furtuni) cu potențial de avariere a construcției.",
        surse_recomandate=["ANM"],
    ),
    RiscFizic(
        cheie="inundatii",
        denumire="Inundații și revarsari ale apelor",
        descriere="Risc de inundație din revarsarea cursurilor de apa sau a apelor pluviale.",
        surse_recomandate=["INHGA", "ANM", "MMAP"],
    ),
    RiscFizic(
        cheie="grindina_precipitatii",
        denumire="Caderi de grindina, precipitații extreme",
        descriere="Grindina și precipitații extreme cu potențial de avariere a acoperișului/anvelopei.",
        surse_recomandate=["ANM"],
    ),
    RiscFizic(
        cheie="incendii",
        denumire="Incendii exterioare sau interioare",
        descriere="Risc de incendiu provenit din surse interioare sau exterioare construcției.",
        surse_recomandate=["ISU"],
    ),
]

# Index pentru acces rapid pe cheie.
_INDEX_RISCURI: dict[str, RiscFizic] = {r.cheie: r for r in CATALOG_RISCURI_FIZICE}

# Disclaimerul de competența (formularea fidela poziției ANEVAR + GEV 520 §87). Apare in secțiunea ESG
# indiferent ce riscuri sunt identificate — delimiteaza competența evaluatorului.
DISCLAIMER_COMPETENTA: str = (
    "Incadrarea riscurilor fizice pe o scala de probabilitate de producere excede competențele "
    "profesiei de evaluator autorizat, intrucat impune o expertiza specifica ce necesita, de regula, "
    "autorizare din partea autoritaților statului. Informațiile privind riscurile fizice se preiau "
    "ca atare din documentele oficiale puse la dispoziție de client/utilizator (expertize, plan de "
    "prevenire și aparare impotriva dezastrelor) ori din datele furnizate de autoritați abilitate "
    "(ISU, ANM, INHGA, MMAP, ISC) sau de societați de asigurari. Prezentul raport NU ierarhizeaza și "
    "NU clasifica riscurile fizice; orice clasificare/ierarhizare a acestora se realizeaza in afara "
    "raportului de evaluare, de catre o persoana cu competențe specifice in domeniu."
)


class RiscIdentificat(BaseModel):
    """Un risc fizic identificat in dosar + sursa oficiala (daca documentul a fost furnizat de client).

    `document_furnizat` = flag «document oficial furnizat de client da/nu» (mecanismul din PdV). `sursa` =
    cheie din `AUTORITATI_SURSA` (de unde provine documentul); `observatie` = informația preluata ca atare.
    NU exista camp de scor/probabilitate — modulul nu cuantifica.
    """

    cheie: str                        # cheie din CATALOG_RISCURI_FIZICE
    document_furnizat: bool = False   # documentul oficial a fost pus la dispoziție de client?
    sursa: str = ""                   # cheie din AUTORITATI_SURSA (ISU/ANM/INHGA/MMAP/ISC/asigurator)
    # informația preluata ca atare din documentul oficial. max_length (F-15-4): o observatie
    # legitima e scurta; intra in genereaza_sectiune_esg -> docx ca atare, deci plafonul opreste
    # balonarea documentului oficial.
    observatie: str = Field(default="", max_length=2000)


def risc(cheie: str) -> RiscFizic | None:
    """Riscul fizic din catalog dupa cheie (None daca cheia nu exista)."""
    return _INDEX_RISCURI.get(cheie)


def chei_riscuri() -> list[str]:
    """Cheile celor 8 riscuri fizice, in ordinea din PdV."""
    return [r.cheie for r in CATALOG_RISCURI_FIZICE]


def descriere_sursa(cheie_sursa: str) -> str:
    """Denumirea completa a autoritații-sursa dupa cheie (sau cheia in clar daca e necunoscuta)."""
    return AUTORITATI_SURSA.get(cheie_sursa, cheie_sursa)


def _eticheta_sursa(ri: RiscIdentificat) -> str:
    """Eticheta sursei pentru un risc identificat (denumire completa daca e in nomenclator)."""
    return descriere_sursa(ri.sursa) if ri.sursa else ""


def genereaza_sectiune_esg(identificate: list[RiscIdentificat] | None = None) -> str:
    """Textul secțiunii ESG / riscuri fizice pentru raport (MENȚIONARE, nu cuantificare).

    Pentru fiecare risc identificat:
      - daca `document_furnizat` -> se preia sursa oficiala (autoritatea) + observația, CA ATARE;
      - daca NU -> se menționeaza ca nu au fost puse la dispoziție documente oficiale (necuantificare).
    Daca nu s-a identificat niciun risc -> nota ca nu au fost semnalate riscuri fizice / documente.
    Secțiunea se incheie INTOTDEAUNA cu `DISCLAIMER_COMPETENTA` (delimitarea competenței — GEV 520 §87).

    Returneaza text simplu (paragrafe separate prin linie goala), conform poziției ANEVAR: fara scoruri,
    fara ierarhii, fara probabilitați.
    """
    identificate = identificate or []
    linii: list[str] = [
        "Riscuri fizice (ESG) cu relevanța pentru garantarea imprumutului (GEV 520):",
    ]

    if not identificate:
        linii.append(
            "Pana la data raportului nu au fost semnalate riscuri fizice specifice amplasamentului și "
            "nu au fost puse la dispoziția evaluatorului documente oficiale in acest sens."
        )
    else:
        for ri in identificate:
            rf = risc(ri.cheie)
            denumire = rf.denumire if rf else ri.cheie
            if ri.document_furnizat:
                eticheta = _eticheta_sursa(ri)
                detaliu = f" (sursa: {eticheta})" if eticheta else ""
                obs = f" {ri.observatie.strip()}" if ri.observatie.strip() else ""
                linii.append(
                    f"- {denumire}: informație preluata ca atare din document oficial furnizat de "
                    f"client/utilizator{detaliu}.{obs}"
                )
            else:
                linii.append(
                    f"- {denumire}: nu au fost puse la dispoziția evaluatorului documente oficiale; "
                    "riscul este menționat, fara cuantificare."
                )

    linii.append(DISCLAIMER_COMPETENTA)
    return "\n\n".join(linii)


class ElementChecklistEsg(BaseModel):
    """Un punct din checklist-ul «ai verificat riscurile fizice?» pentru un risc din catalog."""

    cheie: str               # cheie din CATALOG_RISCURI_FIZICE
    denumire: str            # denumirea afisata
    verificat: bool          # riscul a fost analizat (identificat in dosar)?
    document_furnizat: bool  # documentul oficial a fost pus la dispoziție de client?
    sursa: str = ""          # autoritatea-sursa (daca a fost atasata)
    surse_recomandate: list[str] = Field(default_factory=list)  # autoritați de verificare sugerate


def checklist_riscuri_fizice(
    identificate: list[RiscIdentificat] | None = None,
) -> list[ElementChecklistEsg]:
    """Checklist «ai verificat riscurile fizice?» — un punct pentru fiecare din cele 8 riscuri.

    Marcheaza ce riscuri au fost analizate (`verificat`) și daca documentul oficial a fost furnizat de
    client. Ramane un instrument de MENȚIONARE/verificare — nu produce scoruri sau ierarhii.
    """
    identificate = identificate or []
    by_cheie: dict[str, RiscIdentificat] = {ri.cheie: ri for ri in identificate}
    rezultat: list[ElementChecklistEsg] = []
    for rf in CATALOG_RISCURI_FIZICE:
        ri = by_cheie.get(rf.cheie)
        rezultat.append(
            ElementChecklistEsg(
                cheie=rf.cheie,
                denumire=rf.denumire,
                verificat=ri is not None,
                document_furnizat=bool(ri and ri.document_furnizat),
                sursa=(ri.sursa if ri else ""),
                surse_recomandate=list(rf.surse_recomandate),
            )
        )
    return rezultat


def riscuri_neverificate(checklist: list[ElementChecklistEsg]) -> list[ElementChecklistEsg]:
    """Riscurile fizice care NU au fost inca analizate in dosar (pentru avertizarea evaluatorului)."""
    return [e for e in checklist if not e.verificat]


def toate_verificate(checklist: list[ElementChecklistEsg]) -> bool:
    """Toate cele 8 riscuri fizice au fost analizate (verificate) in dosar?"""
    return all(e.verificat for e in checklist)
