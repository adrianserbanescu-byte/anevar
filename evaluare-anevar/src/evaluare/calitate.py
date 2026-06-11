"""Verificarea interna a calitatii (QC) inainte de emiterea raportului — gap G-Q1.

Materializeaza recomandarea ANEVAR «Asigurarea calitatii in activitatea de evaluare» (elementul 5:
supervizare si verificare interna a calitatii INAINTE de emiterea raportului) si cerinta SEV 100
par. 20 (procedura de verificare a calitatii procesului). Transforma AFIRMATIA din declaratia de
conformitate (report/generator.py) intr-un checklist EFECTIV, bifat automat din datele dosarului.

Fiecare punct de control are un `nivel` (severitatea daca NU e trecut):
  - "blocheaza"  -> opreste emiterea raportului (mirror «autorizeaza emiterea doar dupa efectuarea
                   ajustarilor necesare»);
  - "alerteaza"  -> doar avertizeaza inainte de emitere (evaluatorul decide).

Reutilizeaza pragurile/validatorii din `engine/validation.py` (min_comparabile) si logica de valoare
imposibila din `audit/validare_x.py` (valoare finala <= 0), ca sa nu dubleze sursa de adevar.
"""
from __future__ import annotations

import datetime
import unicodedata

from pydantic import BaseModel

from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.engine.validation import Nivel
from evaluare.models.report_context import ReportContext

# Maparea metodei reconciliate -> abordarile pe care le presupune (pentru adecvarea la profil).
_ABORDARI_METODA: dict[str, set[str]] = {
    "piata": {"comparatie"},
    "cost": {"cost"},
    "venit": {"venit"},
    "ponderata": {"comparatie", "cost"},
}

# Radacina (fara diacritice, lowercase) a tipului de valoare asteptat per profil — verificare laxa a
# alinierii tip-valoare-din-raport <-> scop/profil, fara fals-pozitive pe formularile uzuale.
_RADACINA_TIP_VALOARE: dict[str, str] = {
    "piata": "pia", "investitie": "invest", "justa": "just",
    "lichidare": "lichid", "asigurare": "asigur", "chirie": "chir",
}


class ElementCalitate(BaseModel):
    """Un punct de control din verificarea interna a calitatii, bifat automat din date."""

    cheie: str            # identificator stabil (ex. "comparabile_minime")
    titlu: str            # textul afisat in checklist
    trecut: bool          # bifat automat: True = punctul de control trece
    nivel: Nivel          # severitatea daca NU e trecut: "blocheaza" | "alerteaza"
    detaliu: str = ""     # confirmare sau ce anume lipseste / de corectat
    referinta: str = ""   # ancora normativa (SEV / recomandarea de asigurare a calitatii)


def _fara_diacritice(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _e_garantare(ctx: ReportContext) -> bool:
    """Scopul evaluarii este garantarea creditului (GEV 520)? — declanseaza verificarile specifice."""
    return ctx.profil.scop == "garantare_credit"


def _e_placeholder(text: str) -> bool:
    """Un capitol narativ negenerat (placeholder offline «[de completat: ...]») sau gol."""
    t = (text or "").strip().lower()
    return (not t) or ("[de completat" in t)


def _parse_data(s: str | None) -> datetime.date | None:
    """Data ISO (YYYY-MM-DD) tolerant; None daca textul nu e o data ISO (datele pot fi text liber)."""
    if not s:
        return None
    try:
        return datetime.date.fromisoformat(str(s).strip()[:10])
    except (ValueError, TypeError):
        return None


def _item_comparabile(ctx: ReportContext, cfg: MetodologieConfig) -> ElementCalitate:
    """Minimum `cfg.min_comparabile` comparabile in grilele care contribuie efectiv la valoare.

    Reutilizeaza pragul M5 (`min_comparabile`) din metodologie — aceeasi sursa ca `valideaza_comparabile`.
    Comparabilele de PIATA conteaza doar cand metoda reconciliata e piata/ponderata; cele de TEREN ori
    de cate ori exista grila de teren (intra mereu in valoare).
    """
    n = cfg.min_comparabile
    nevoie_piata = ctx.reconciled.metoda_selectata in ("piata", "ponderata")
    nevoie_teren = bool(ctx.land_comparables)
    titlu = f"Minimum {n} comparabile in grilele care contribuie la valoare"
    referinta = "SEV 104 (date); metodologie M5 (min_comparabile)"
    if not nevoie_piata and not nevoie_teren:
        return ElementCalitate(
            cheie="comparabile_minime", titlu=titlu, trecut=True, nivel="blocheaza",
            detaliu="Abordarea prin piata nu a contribuit la valoare; comparabilele nu sunt obligatorii.",
            referinta=referinta)
    lipsuri: list[str] = []
    if nevoie_piata and len(ctx.comparables) < n:
        lipsuri.append(f"grila de piata are {len(ctx.comparables)} (<{n})")
    if nevoie_teren and len(ctx.land_comparables) < n:
        lipsuri.append(f"grila de teren are {len(ctx.land_comparables)} (<{n})")
    trecut = not lipsuri
    return ElementCalitate(
        cheie="comparabile_minime", titlu=titlu, trecut=trecut, nivel="blocheaza",
        detaliu=(f"Comparabile suficiente (>= {n}).") if trecut else "; ".join(lipsuri),
        referinta=referinta)


def _item_cmbu(ctx: ReportContext) -> ElementCalitate:
    """Analiza celei mai bune utilizari (CMBU) este concluzionata (nu inca un placeholder)."""
    sec = next((s for s in ctx.narrative if "CMBU" in s.capitol
                or "bune utiliz" in _fara_diacritice(s.capitol).lower()), None)
    trecut = sec is not None and not _e_placeholder(sec.text)
    return ElementCalitate(
        cheie="cmbu_concluzionat",
        titlu="Analiza celei mai bune utilizari (CMBU) este concluzionata",
        trecut=trecut, nivel="alerteaza",
        detaliu=("CMBU concluzionata." if trecut
                 else "Sectiunea CMBU lipseste sau e inca un placeholder — concluzionati utilizarea."),
        referinta="SEV 100 par. 20; CMBU (GEV 630)")


def _item_tip_valoare(ctx: ReportContext) -> ElementCalitate:
    """Tipul valorii este declarat (obligatoriu, SEV 102) si citeaza standardul-sursa."""
    tv = (ctx.meta.tip_valoare or "").strip()
    titlu = "Tipul valorii declarat, cu sursa (standardul) citata"
    referinta = "SEV 102 (tipuri ale valorii)"
    if not tv:
        return ElementCalitate(
            cheie="tip_valoare_sursa", titlu=titlu, trecut=False, nivel="blocheaza",
            detaliu="Tipul valorii nu este declarat — obligatoriu pentru raport (SEV 102).",
            referinta=referinta)
    citeaza = any(tok in tv.upper() for tok in ("SEV", "GEV", "IVS"))
    return ElementCalitate(
        cheie="tip_valoare_sursa", titlu=titlu, trecut=citeaza, nivel="alerteaza",
        detaliu=(f"Tip valoare: «{tv}»." if citeaza
                 else f"Tipul valorii «{tv}» nu citeaza standardul-sursa (ex. SEV 102)."),
        referinta=referinta)


def _item_documente(ctx: ReportContext) -> ElementCalitate:
    """Documente justificative (extras CF / cadastral / CPE) atasate la dosar (-> Anexa 3)."""
    n = len(ctx.documente)
    trecut = n > 0
    return ElementCalitate(
        cheie="documente_anexate",
        titlu="Documente justificative (extras CF / cadastral / CPE) atasate la dosar",
        trecut=trecut, nivel="alerteaza",
        detaliu=(f"{n} document(e) atasat(e) (Anexa 3)." if trecut
                 else "Niciun document justificativ atasat — Anexa 3 va fi goala; atasati CF/plan/CPE."),
        referinta="Asigurarea calitatii — dosarul de lucru («Informatii de la client»)")


def _item_coerenta(ctx: ReportContext) -> ElementCalitate:
    """Coerenta moneda + date: moneda uzuala, data raportului >= data evaluarii, inspectie <= evaluare."""
    meta = ctx.meta
    moneda = (meta.moneda or "").strip().upper()
    d_eval = _parse_data(meta.data_evaluarii)
    d_rap = _parse_data(meta.data_raportului)
    d_insp = _parse_data(meta.data_inspectiei)
    probleme_b: list[str] = []
    probleme_a: list[str] = []
    if moneda not in ("LEI", "RON", "EUR"):
        probleme_a.append(f"moneda «{meta.moneda}» nu este una uzuala (LEI/EUR)")
    if d_eval and d_rap and d_rap < d_eval:
        probleme_b.append("data raportului este anterioara datei evaluarii")
    if d_eval and d_insp and d_insp > d_eval:
        probleme_a.append("data inspectiei este ulterioara datei evaluarii")
    titlu = "Coerenta monedei si a datelor (evaluare / raport / inspectie)"
    referinta = "SEV 100 par. 20 (coerenta datelor de intrare)"
    if probleme_b:
        return ElementCalitate(
            cheie="coerenta_moneda_data", titlu=titlu, trecut=False, nivel="blocheaza",
            detaliu="; ".join(probleme_b + probleme_a), referinta=referinta)
    if probleme_a:
        return ElementCalitate(
            cheie="coerenta_moneda_data", titlu=titlu, trecut=False, nivel="alerteaza",
            detaliu="; ".join(probleme_a), referinta=referinta)
    return ElementCalitate(
        cheie="coerenta_moneda_data", titlu=titlu, trecut=True, nivel="blocheaza",
        detaliu="Moneda si datele sunt coerente.", referinta=referinta)


def _item_adecvare(ctx: ReportContext) -> ElementCalitate:
    """Adecvarea concluziei la scop: valoare pozitiva + metoda si tip valoare aliniate profilului."""
    titlu = "Adecvarea concluziei la scop (valoare pozitiva, metoda si tip valoare aliniate profilului)"
    referinta = "SEV 100 par. 20 (adecvarea concluziilor la scop)"
    if ctx.reconciled.valoare_finala <= 0:
        return ElementCalitate(
            cheie="adecvare_scop", titlu=titlu, trecut=False, nivel="blocheaza",
            detaliu="Valoarea finala estimata este <= 0 — concluzia nu este utilizabila.",
            referinta=referinta)
    probleme: list[str] = []
    metoda = ctx.reconciled.metoda_selectata
    necesare = _ABORDARI_METODA.get(metoda, set())
    aplicabile = set(ctx.profil.abordari_aplicabile)
    if necesare and not (necesare & aplicabile):
        probleme.append(f"metoda «{metoda}» nu corespunde abordarilor aplicabile profilului "
                        f"({', '.join(sorted(aplicabile)) or '—'})")
    rad = _RADACINA_TIP_VALOARE.get(ctx.profil.tip_valoare)
    tv_norm = _fara_diacritice(ctx.meta.tip_valoare or "").lower()
    if rad and tv_norm and rad not in tv_norm:
        probleme.append(f"tipul valorii din raport «{ctx.meta.tip_valoare}» nu pare aliniat cu "
                        f"profilul ({ctx.profil.tip_valoare})")
    trecut = not probleme
    return ElementCalitate(
        cheie="adecvare_scop", titlu=titlu, trecut=trecut, nivel="alerteaza",
        detaliu=("Concluzia este adecvata scopului." if trecut else "; ".join(probleme)),
        referinta=referinta)


def _item_riscuri_fizice(ctx: ReportContext) -> ElementCalitate:
    """ESG / riscuri fizice verificate — la garantare (GEV 520 §86-88), `meta.riscuri_fizice` populat.

    Reutilizeaza campul `meta.riscuri_fizice` (lista de etichete, deja pe master) si pozitia modulului
    `esg.py`: riscurile fizice se MENTIONEAZA, nu se cuantifica. La garantare, daca lista e populata ->
    riscurile au fost analizate (trece); altfel -> avertizare «verifica riscurile fizice» (nu blocheaza —
    ramane decizia evaluatorului, mirror «warn before»). In afara garantarii -> neaplicabil (trece).
    """
    titlu = "ESG / riscuri fizice verificate (la garantare, GEV 520)"
    referinta = "GEV 520 §86-88; pozitia ANEVAR riscuri fizice (esg.py)"
    if not _e_garantare(ctx):
        return ElementCalitate(
            cheie="esg_riscuri_fizice", titlu=titlu, trecut=True, nivel="alerteaza",
            detaliu="Scopul nu este garantarea creditului — verificarea riscurilor fizice nu este ceruta.",
            referinta=referinta)
    riscuri = [r for r in (ctx.meta.riscuri_fizice or []) if str(r).strip()]
    trecut = bool(riscuri)
    return ElementCalitate(
        cheie="esg_riscuri_fizice", titlu=titlu, trecut=trecut, nivel="alerteaza",
        detaliu=(f"Riscuri fizice analizate/semnalate: {', '.join(riscuri)}." if trecut
                 else "Verifica riscurile fizice (inundabilitate, seismic, alunecari) — niciunul "
                      "semnalat in dosar; preia documentele oficiale puse la dispozitie de client."),
        referinta=referinta)


def _item_valoare_prudenta(ctx: ReportContext) -> ElementCalitate:
    """Valoare prudenta considerata — la garantare, nota optionala (valoare_prudenta.py, CRR art. 229/208).

    Reaminteste evaluatorului ca, la garantarea creditului, ar trebui considerata valoarea prudenta
    (baza de valoare distincta, ADITIONALA valorii de piata — vezi `valoare_prudenta.py`). Nivel ATENTIE,
    niciodata blocant: interpretarea CRR e neoficializata in RO, deci ramane o optiune asumata de
    evaluator. In afara garantarii -> neaplicabil (trece).
    """
    titlu = "Valoare prudenta (de garantie) considerata — nota optionala (la garantare)"
    referinta = "CRR — Reg. (UE) 575 art. 229/208 (valoare_prudenta.py); interpretare neoficializata RO"
    if not _e_garantare(ctx):
        return ElementCalitate(
            cheie="valoare_prudenta_considerata", titlu=titlu, trecut=True, nivel="alerteaza",
            detaliu="Scopul nu este garantarea creditului — valoarea prudenta nu este relevanta.",
            referinta=referinta)
    return ElementCalitate(
        cheie="valoare_prudenta_considerata", titlu=titlu, trecut=False, nivel="alerteaza",
        detaliu="La garantare, considerati estimarea valorii prudente (de garantie) alaturi de valoarea "
                "de piata (optional, asumat de evaluator) — vezi modulul valoare prudenta (CRR art. 229).",
        referinta=referinta)


def verifica_calitate(ctx: ReportContext,
                      cfg: MetodologieConfig = IMPLICIT) -> list[ElementCalitate]:
    """Checklist-ul complet de verificare interna a calitatii, bifat automat din `ctx`.

    Acopera (minim): min. comparabile, CMBU concluzionata, tip valoare + sursa, documente anexate,
    coerenta moneda/date, adecvarea concluziei la scop. La garantarea creditului adauga (aditiv, doar
    nivel ATENTIE, niciodata blocant): ESG / riscuri fizice verificate (GEV 520) si nota «valoare
    prudenta considerata» (CRR). `cfg` = pragurile de metodologie (M5).
    """
    return [
        _item_comparabile(ctx, cfg),
        _item_cmbu(ctx),
        _item_tip_valoare(ctx),
        _item_documente(ctx),
        _item_coerenta(ctx),
        _item_adecvare(ctx),
        _item_riscuri_fizice(ctx),
        _item_valoare_prudenta(ctx),
    ]


def blocaje(checklist: list[ElementCalitate]) -> list[ElementCalitate]:
    """Punctele de control ESUATE care BLOCHEAZA emiterea (nivel="blocheaza")."""
    return [e for e in checklist if not e.trecut and e.nivel == "blocheaza"]


def avertismente(checklist: list[ElementCalitate]) -> list[ElementCalitate]:
    """Punctele de control ESUATE care doar AVERTIZEAZA (nivel="alerteaza")."""
    return [e for e in checklist if not e.trecut and e.nivel == "alerteaza"]


def emisibil(checklist: list[ElementCalitate]) -> bool:
    """Raportul poate fi emis? (niciun blocaj de calitate)."""
    return not blocaje(checklist)


def rezumat(checklist: list[ElementCalitate]) -> dict:
    """Forma serializabila pentru UI/API: checklist + emisibil + numarul de blocaje/avertismente."""
    return {
        "emisibil": emisibil(checklist),
        "blocaje": len(blocaje(checklist)),
        "avertismente": len(avertismente(checklist)),
        "checklist": [e.model_dump() for e in checklist],
    }
