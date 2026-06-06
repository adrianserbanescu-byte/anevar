"""Registrul documentelor livrate + un mic convertor Markdown→HTML (fără dependențe).

Documentele se „parchează" în pagina `/documente` (UI nou și vechi au link în antet/subsol).
Conținutul e împachetat în `.exe` (vezi `evaluare/data/documente/`), deci e disponibil offline.
Convertorul acoperă strict ce folosesc documentele noastre: titluri, liste, tabele, citate,
`cod`, **bold**, [link](url), linie orizontală. Nu e un parser MD general.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

# slug, titlu, categorie, fisier, descriere. Ordinea = ordinea afișării.
REGISTRU: list[dict] = [
    {"slug": "sinteza-lansare", "categorie": "Strategie & lansare",
     "titlu": "Sinteză lansare (citește prima)", "fisier": "00-SINTEZA-lansare-pentru-Adi.md",
     "descriere": "Documentul-umbrelă: opinia agregată + lista unică de aprobat."},
    {"slug": "plan-lansare", "categorie": "Strategie & lansare",
     "titlu": "Plan de lansare pe piață", "fisier": "plan-lansare-piata.md",
     "descriere": "Audit consiliu LLM + release-readiness + «Spune DA» în pași."},
    {"slug": "strategie-comercializare", "categorie": "Strategie & lansare",
     "titlu": "Strategie comercializare (întrebări)", "fisier": "strategie-comercializare-intrebari.md",
     "descriere": "7 decizii: admin, update, crash-telemetrie, preț, instrument-nu-înlocuitor."},
    {"slug": "plan-maine", "categorie": "Strategie & lansare",
     "titlu": "Plan & decizii produs", "fisier": "plan-maine-2026-06-06.md",
     "descriere": "Livrările pe produs + deciziile de UI deschise + backlog."},
    {"slug": "evaluare-juridica", "categorie": "Juridic (DRAFT — necesită avocat)",
     "titlu": "Evaluare juridică (RO)", "fisier": "legal/00-evaluare-juridica-RO.md",
     "descriere": "Matrice de riscuri juridice + acțiuni obligatorii înainte de lansare."},
    {"slug": "termeni-conditii", "categorie": "Juridic (DRAFT — necesită avocat)",
     "titlu": "Termeni și condiții", "fisier": "legal/10-termeni-si-conditii-DRAFT.md",
     "descriere": "Condiții de utilizare a aplicației."},
    {"slug": "politica-confidentialitate", "categorie": "Juridic (DRAFT — necesită avocat)",
     "titlu": "Politică de confidențialitate (GDPR)", "fisier": "legal/11-politica-confidentialitate-DRAFT.md",
     "descriere": "Ce date, unde, anonimizare la AI, sub-împuterniciți."},
    {"slug": "eula", "categorie": "Juridic (DRAFT — necesită avocat)",
     "titlu": "Acord de licență (EULA)", "fisier": "legal/12-acord-licenta-EULA-DRAFT.md",
     "descriere": "Licențiere software + limitarea răspunderii."},
    {"slug": "dpa", "categorie": "Juridic (DRAFT — necesită avocat)",
     "titlu": "Acord de prelucrare (DPA, art. 28)", "fisier": "legal/13-DPA-acord-prelucrare-DRAFT.md",
     "descriere": "Furnizor ca persoană împuternicită + anexa sub-împuterniciților."},
    {"slug": "disclaimer-profesional", "categorie": "Juridic (DRAFT — necesită avocat)",
     "titlu": "Disclaimer profesional", "fisier": "legal/14-disclaimer-profesional-DRAFT.md",
     "descriere": "Aplicația asistă; valoarea și semnătura aparțin evaluatorului ANEVAR."},
]
_PE_SLUG = {d["slug"]: d for d in REGISTRU}


def baza() -> Path:
    """Folderul cu documentele împachetate (lângă cod, inclus în .exe)."""
    return Path(__file__).parent / "data" / "documente"


def listeaza() -> list[dict]:
    """Documentele care există efectiv pe disc, în ordinea registrului."""
    return [d for d in REGISTRU if (baza() / d["fisier"]).exists()]


def incarca(slug: str) -> tuple[dict, str]:
    """Returnează (meta, html) pentru un document. KeyError dacă nu există."""
    meta = _PE_SLUG.get(slug)
    if meta is None:
        raise KeyError(slug)
    f = baza() / meta["fisier"]
    if not f.exists():
        raise KeyError(slug)
    return meta, md_to_html(f.read_text(encoding="utf-8"))


# ── Convertor Markdown → HTML (minimal, suficient pentru documentele noastre) ────────
def _url_sigur(u: str) -> str:
    """Permite doar URL-uri sigure (http/https/mailto/relativ/ancoră); altfel „#".

    Blochează `javascript:`, `data:` etc. și escapează ghilimelele (anti-injecție în atribut).
    """
    u = u.strip()
    if re.match(r"^(https?:|mailto:)", u, re.IGNORECASE) or u.startswith(("/", "#", ".")):
        return html.escape(u, quote=True)
    return "#"


def _inline(text: str) -> str:
    """Formatare în linie: escape HTML, apoi **bold**, `cod`, [link](url) (URL filtrat)."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{_url_sigur(m.group(2))}">{m.group(1)}</a>', text)
    return text


def md_to_html(md: str) -> str:
    """Convertor MD restrâns: titluri, hr, citate, liste (ul/ol), tabele, paragrafe."""
    out: list[str] = []
    linii = md.replace("\r\n", "\n").split("\n")
    i, n = 0, len(linii)
    while i < n:
        ln = linii[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):                             # bloc de cod (fence)
            i += 1
            buf = []
            while i < n and not linii[i].strip().startswith("```"):
                buf.append(html.escape(linii[i], quote=False))
                i += 1
            i += 1                                          # sare peste fence-ul de închidere
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
        elif re.match(r"^---+$", s):                        # linie orizontală
            out.append("<hr>")
            i += 1
        elif s.startswith("#"):                             # titlu (coborât cu 1 nivel: cartușul
            niv = len(s) - len(s.lstrip("#"))               # paginii deține deja <h1>, deci în
            niv = min(max(niv, 1) + 1, 6)                   # corpul documentului pornim de la <h2>)
            out.append(f"<h{niv}>{_inline(s[len(s) - len(s.lstrip('#')):].strip())}</h{niv}>")
            i += 1
        elif s.startswith(">"):                             # citat (poate pe mai multe linii)
            buf = []
            while i < n and linii[i].strip().startswith(">"):
                buf.append(_inline(linii[i].strip()[1:].strip()))
                i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>")
        elif s.lstrip().startswith(("- ", "* ")):           # listă neordonată
            out.append("<ul>")
            while i < n and linii[i].strip()[:2] in ("- ", "* "):
                out.append("<li>" + _inline(linii[i].strip()[2:]) + "</li>")
                i += 1
            out.append("</ul>")
        elif re.match(r"^\d+\.\s", s):                       # listă ordonată
            out.append("<ol>")
            while i < n and re.match(r"^\d+\.\s", linii[i].strip()):
                out.append("<li>" + _inline(re.sub(r"^\d+\.\s", "", linii[i].strip())) + "</li>")
                i += 1
            out.append("</ol>")
        elif s.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", linii[i + 1]):
            out.append(_tabel(linii, i))                    # tabel (antet + separator + rânduri)
            i += 2
            while i < n and linii[i].strip().startswith("|"):
                i += 1
        else:                                               # paragraf (linii consecutive)
            buf = []
            while i < n and linii[i].strip() and not _e_bloc(linii[i].strip()):
                buf.append(_inline(linii[i].strip()))
                i += 1
            out.append("<p>" + "<br>".join(buf) + "</p>")
    return "\n".join(out)


def _e_bloc(s: str) -> bool:
    """True dacă linia începe un alt bloc (titlu/listă/citat/hr/tabel/cod)."""
    return (s.startswith(("#", ">", "|", "```")) or s.lstrip()[:2] in ("- ", "* ")
            or bool(re.match(r"^\d+\.\s", s)) or bool(re.match(r"^---+$", s)))


def _celule(rand: str) -> list[str]:
    return [c.strip() for c in rand.strip().strip("|").split("|")]


def _tabel(linii: list[str], i: int) -> str:
    antet = _celule(linii[i])
    out = ["<table><thead><tr>"]
    out += [f"<th>{_inline(c)}</th>" for c in antet]
    out.append("</tr></thead><tbody>")
    j = i + 2
    while j < len(linii) and linii[j].strip().startswith("|"):
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in _celule(linii[j])) + "</tr>")
        j += 1
    out.append("</tbody></table>")
    return "".join(out)
