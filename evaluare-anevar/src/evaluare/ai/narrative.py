"""Generarea narativului raportului prin Claude (Anthropic), cu fallback.

Datele trimise sunt deja anonimizate; textul primit este demascat local.
Clientul este injectabil pentru testare fara retea.
"""
from __future__ import annotations

from typing import Optional, Protocol

from evaluare.models.report_context import ReportContext
from evaluare.models.narrative import NarrativeSection
from evaluare.report.anonymizer import Anonymizer

# Capitolele analitice pentru care AI genereaza text (numerele raman deterministe).
CAPITOLE_NARATIVE = [
    "Ipoteze generale si speciale",
    "Prezentarea datelor de piata",
    "Descrierea juridica si fizica a proprietatii",
    "Analiza celei mai bune utilizari (CMBU)",
    "Justificarea ajustarilor aplicate",
    "Reconcilierea rezultatelor si concluzia valorii",
    "Riscul asociat garantiei (GEV 520)",
]

# Indrumar scurt per capitol: ce trebuie sa contina (ghideaza AI-ul, nu cifrele).
GHID_CAPITOL = {
    "Ipoteze generale si speciale": (
        "Enunta ipotezele si conditiile limitative standard: se presupune titlu valabil si "
        "liber de sarcini (cu exceptiile mentionate), structura de rezistenta corespunzatoare, "
        "fara investigatii geotehnice/ascunse; raportul se foloseste exclusiv in scopul declarat."
    ),
    "Prezentarea datelor de piata": (
        "Descrie pe scurt piata imobiliara locala relevanta (cerere/oferta, lichiditate, "
        "tendinte), pe baza zonei si a comparabilelor utilizate."
    ),
    "Descrierea juridica si fizica a proprietatii": (
        "Descrie proprietatea: situarea juridica (cadastral/CF), terenul (suprafata, categorie) "
        "si constructia (arii, an, regim de inaltime), in proza profesionala."
    ),
    "Analiza celei mai bune utilizari (CMBU)": (
        "Argumenteaza cea mai buna utilizare (permis legal, posibil fizic, fezabil financiar, "
        "maxim productiv); de regula utilizarea rezidentiala existenta."
    ),
    "Justificarea ajustarilor aplicate": (
        "Justifica logica ajustarilor din grila (etapa de tranzactie vs proprietate) si de ce "
        "comparabilul selectat are ajustarea bruta minima."
    ),
    "Reconcilierea rezultatelor si concluzia valorii": (
        "Compara abordarile aplicate (piata/cost), explica ponderarea/selectia metodei si "
        "concluzioneaza valoarea finala."
    ),
    "Riscul asociat garantiei (GEV 520)": (
        "Analizeaza riscul pentru garantarea creditului conform GEV 520: lichiditatea si "
        "activitatea pietei locale, gradul de adecvare al proprietatii ca garantie, "
        "vandabilitatea si expunerea estimata, sensibilitatea valorii la conditiile pietei."
    ),
}

SYSTEM_PROMPT = (
    "Esti un evaluator imobiliar autorizat ANEVAR. Scrii sectiuni de raport de "
    "evaluare in limba romana, profesional si conform standardelor SEV (editia in "
    "vigoare). Folosesti EXCLUSIV datele numerice furnizate; nu inventezi si nu "
    "modifici cifre. Pastrezi marcajele de forma [CLIENT], [ADRESA], [CADASTRAL], "
    "[CF], [EVALUATOR] exact cum apar. Scrii doar textul capitolului cerut, fara titlu."
)


class NarrativeClient(Protocol):
    """Interfata minima a unui client de generare text."""

    def complete(self, system: str, user: str) -> str:
        ...


def _facts(ctx: ReportContext) -> str:
    """Construieste un rezumat textual al datelor calculate (date de intrare AI)."""
    linii = [
        f"Scop evaluare: {ctx.meta.scop}.",
        f"Tip valoare: {ctx.meta.tip_valoare}. Moneda: {ctx.meta.moneda}.",
        f"Suprafata teren: {ctx.land.suprafata} mp; categorie: {ctx.land.categorie}.",
        f"Arie utila (Au): {ctx.building.au} mp; arie construita desfasurata (Acd): "
        f"{ctx.building.acd} mp; an referinta: {ctx.building.an_referinta}.",
        f"Valoare finala reconciliata: {ctx.reconciled.valoare_finala} "
        f"{ctx.meta.moneda} (metoda: {ctx.reconciled.metoda_selectata}).",
    ]
    if ctx.cost_result is not None:
        c = ctx.cost_result
        linii.append(
            f"Abordarea prin cost: CIB={c.cib}, Vcp={c.vcp} ani, "
            f"depreciere fizica={c.depreciere_fizica}, CIN={c.cin}, "
            f"valoare prin cost={c.valoare_cost}."
        )
    if ctx.market_result is not None:
        m = ctx.market_result
        linii.append(
            f"Abordarea prin piata (pret total): valoare={m.valoare_piata}, "
            f"comparabil selectat index {m.index_selectat}, "
            f"numar comparabile={len(ctx.comparables)}."
        )
    if ctx.land_result is not None:
        lr = ctx.land_result
        linii.append(
            f"Teren prin comparatie: {lr.pret_mp_ales} EUR/mp x {ctx.land.suprafata} mp = "
            f"{lr.valoare_teren} (comparabil selectat index {lr.index_selectat}, "
            f"din {len(ctx.land_comparables)} comparabile de teren)."
        )
    if ctx.alocare_constructii is not None:
        linii.append(
            f"Alocarea valorii: valoare constructii (alocata) = {ctx.alocare_constructii}."
        )
    if ctx.meta.beneficiar:
        linii.append(f"Beneficiar / finantator: {ctx.meta.beneficiar}.")
    return "\n".join(linii)


def _placeholder(capitol: str) -> str:
    return f"[de completat: {capitol}. Generare AI dezactivata - introduceti textul manual.]"


def generate_narrative(
    ctx: ReportContext,
    client: Optional[NarrativeClient],
    anonymizer: Optional[Anonymizer],
) -> list[NarrativeSection]:
    """Genereaza cate o sectiune narativa per capitol.

    Fara client -> placeholdere. Cu client: trimite datele anonimizate si
    demascheaza raspunsul.
    """
    if client is None:
        return [NarrativeSection(capitol=c, text=_placeholder(c)) for c in CAPITOLE_NARATIVE]

    facts = _facts(ctx)
    if anonymizer is not None:
        facts = anonymizer.mask(facts)

    sections: list[NarrativeSection] = []
    for capitol in CAPITOLE_NARATIVE:
        ghid = GHID_CAPITOL.get(capitol, "")
        indrumar = f"Indrumar (ce sa contina): {ghid}\n\n" if ghid else ""
        user = (
            f"Capitol de redactat: {capitol}.\n\n"
            f"{indrumar}"
            f"Date calculate (deja anonimizate):\n{facts}\n\n"
            f"Scrie textul acestui capitol (2-4 paragrafe, proza profesionala)."
        )
        raw = client.complete(SYSTEM_PROMPT, user)
        text = anonymizer.unmask(raw) if anonymizer is not None else raw
        sections.append(NarrativeSection(capitol=capitol, text=text))
    return sections


class PerplexityNarrativeClient:
    """Client Perplexity (sonar) cu interfata .complete(system, user).

    API compatibil OpenAI (chat completions). Folosit pentru extractie din text dat,
    derivare zona si narativ. Constructorul NU face apel (doar retine cheia).
    """

    def __init__(self, api_key: str, model: str = "sonar", max_tokens: int = 1024):
        self._key = api_key
        self._model = model
        self._max_tokens = max_tokens

    def complete(self, system: str, user: str) -> str:
        import requests  # import local: nu e necesar in testele cu client fals

        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {self._key}",
                     "Content-Type": "application/json"},
            json={
                "model": self._model,
                "max_tokens": self._max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class AnthropicNarrativeClient:
    """Client real Claude (Anthropic) cu prompt caching pe blocul de sistem."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6",
                 max_tokens: int = 1024):
        import anthropic  # import local: nu e necesar in testele cu client fals

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def complete(self, system: str, user: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=[{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": user}],
        )
        return "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        )
