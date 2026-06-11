"""Scriitor XLSX minimal, FARA dependente externe.

App-ul ruleaza offline, impachetat cu PyInstaller, fara `openpyxl`. Pentru exportul de registru
(o singura foaie, antet + randuri) e suficient un `.xlsx` valid cu **inline strings** (fara tabel de
shared strings). Valorile numerice se scriu ca numere; restul ca text. Tot ce intra se escapeaza XML.

Un `.xlsx` e un ZIP cu cateva piese XML; producem setul minim pe care Excel/LibreOffice il deschid:
`[Content_Types].xml`, `_rels/.rels`, `xl/workbook.xml`, `xl/_rels/workbook.xml.rels`, foaia.
"""
from __future__ import annotations

import io
import zipfile
from collections.abc import Iterable, Sequence
from decimal import Decimal

_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
    "</Types>"
)
_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
    "</Relationships>"
)
_WB_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
    "</Relationships>"
)


# Caractere de control interzise de XML 1.0: tot sub 0x20, mai putin TAB/LF/CR. Daca ajung RAW intr-un
# `<t>`, fisierul `.xlsx` devine XML invalid -> Excel/LibreOffice il resping ca fiind corupt.
_PERICULOASE_INCEPUT = ("=", "+", "-", "@")   # prefixe de formula (CSV/XLSX formula injection)


def _curata_control(s: str) -> str:
    """Scoate caracterele de control invalide in XML 1.0 (sub 0x20), pastrand TAB/LF/CR."""
    return "".join(c for c in s if c in "\t\n\r" or ord(c) >= 0x20)


def _neutralizeaza_formula(s: str) -> str:
    """Prefixeaza cu apostrof (') o celula TEXT care incepe cu un caracter de formula (= + - @) sau cu
    TAB/CR, ca Excel/LibreOffice sa o trateze ca text literal, nu ca formula LIVE (CSV/formula injection,
    CWE-1236). Aplicat o singura data, centralizat, ca exporturile CSV si XLSX sa fie consistente."""
    if s and (s[0] in _PERICULOASE_INCEPUT or s[0] in ("\t", "\r")):
        return "'" + s
    return s


def _esc(s: str) -> str:
    s = _curata_control(s)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def _col(idx: int) -> str:
    """Index 0 -> 'A', 25 -> 'Z', 26 -> 'AA' (litera de coloana Excel)."""
    s = ""
    idx += 1
    while idx > 0:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def _celula(col: int, rand: int, val: object) -> str:
    ref = f"{_col(col)}{rand}"
    if isinstance(val, bool):                 # bool e subclasa de int -> trateaza-l intai, ca text
        val = "DA" if val else "NU"
    if isinstance(val, (int, float, Decimal)):
        return f'<c r="{ref}"><v>{val}</v></c>'
    text = "" if val is None else str(val)
    # Ordine: curata INTAI caracterele de control (altfel un `\x01=cmd` ar ramane `=cmd` dupa curatare,
    # re-expunand prefixul de formula), apoi neutralizeaza prefixul de formula, apoi escapeaza XML.
    text = _neutralizeaza_formula(_curata_control(text))
    return (f'<c r="{ref}" t="inlineStr"><is>'
            f'<t xml:space="preserve">{_esc(text)}</t></is></c>')


def workbook(antete: Sequence[object], randuri: Iterable[Sequence[object]],
             nume_foaie: str = "Registru") -> bytes:
    """Produce bytes-ul unui `.xlsx` cu o foaie: primul rand = `antete`, apoi `randuri`."""
    toate = [list(antete)] + [list(r) for r in randuri]
    randuri_xml = []
    for ri, r in enumerate(toate, start=1):
        celule = "".join(_celula(ci, ri, v) for ci, v in enumerate(r))
        randuri_xml.append(f'<row r="{ri}">{celule}</row>')
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(randuri_xml)}</sheetData></worksheet>'
    )
    nume = _esc(nume_foaie[:31]) or "Foaie1"   # numele foii: max 31 caractere (limita Excel)
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets><sheet name="{nume}" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CONTENT_TYPES)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("xl/workbook.xml", workbook_xml)
        z.writestr("xl/_rels/workbook.xml.rels", _WB_RELS)
        z.writestr("xl/worksheets/sheet1.xml", sheet)
    return buf.getvalue()
