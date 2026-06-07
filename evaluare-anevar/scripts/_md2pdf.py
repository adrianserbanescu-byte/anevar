"""Convertește documentele de livrat din .md în HTML stilizat (apoi LibreOffice → PDF).

Rulează: python scripts/_md2pdf.py   → scrie HTML în docs/pdf/_html/
Apoi:    soffice --headless --convert-to pdf --outdir docs/pdf docs/pdf/_html/*.html
"""
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "pdf" / "_html"

# Pachetele de livrat (relativ la docs/)
FISIERE = [
    "livrabile-finale.md",
    "manual-utilizare.md", "SLA-suport.md", "plan-incident-breach.md", "cerere-aviz-asigurator.md",
    "protocol-peer-review-evaluator.md", "audit-aml-pentru-jurist.md", "pachet-validare-banci.md",
    "legal/00-evaluare-juridica-RO.md",
    "legal/10-termeni-si-conditii-DRAFT.md", "legal/11-politica-confidentialitate-DRAFT.md",
    "legal/12-acord-licenta-EULA-DRAFT.md", "legal/13-DPA-acord-prelucrare-DRAFT.md",
    "legal/14-disclaimer-profesional-DRAFT.md",
    "gdpr/politica-prelucrare-MODEL.md", "gdpr/formular-consimtamant-MODEL.md",
    "review-app/00-explicatie-aplicatie-pentru-review.md",
    "review-app/_metodologie.md", "review-app/_raport-conformitate.md",
    "review-app/_arhitectura.md", "review-app/_aml-ui.md",
]

CSS = """
@page { size: A4; margin: 1.4cm; }
body { font-family: 'Calibri','Segoe UI',Arial,sans-serif; font-size: 10pt; color: #1b2a3d; line-height: 1.4;
       word-wrap: break-word; overflow-wrap: anywhere; }
h1,h2,h3,h4 { font-family: 'Georgia','Cambria',serif; color: #1f3a5f; }
h1 { font-size: 19pt; border-bottom: 2px solid #c9a227; padding-bottom: 5px; margin-bottom: 12px; }
h2 { font-size: 14pt; margin-top: 18px; }
h3 { font-size: 11.5pt; margin-top: 13px; }
table { border-collapse: collapse; width: 100%; margin: 9px 0; font-size: 8.3pt; table-layout: fixed; }
th,td { border: 1px solid #b9c2cf; padding: 4px 6px; text-align: left; vertical-align: top;
        word-wrap: break-word; overflow-wrap: anywhere; }
th { background: #e4eaf3; color: #13243b; font-weight: bold; }
code { background: #f2f2f2; padding: 1px 3px; font-family: Consolas,monospace; font-size: 8.5pt;
       word-break: break-all; }
pre { background: #f5f6f8; padding: 8px; border-left: 3px solid #c9a227; white-space: pre-wrap; }
blockquote { border-left: 3px solid #c9a227; margin: 8px 0; padding: 4px 12px; color: #4a5666; background: #fafbfc; }
a { color: #1f3a5f; text-decoration: none; }
hr { border: none; border-top: 1px solid #d8dce3; margin: 13px 0; }
ul,ol { margin: 6px 0 6px 0; }
li { margin: 2px 0; }
"""

TPL = ("<!DOCTYPE html><html lang='ro'><head><meta charset='utf-8'>"
       "<style>{css}</style></head><body>{body}</body></html>")

OUT.mkdir(parents=True, exist_ok=True)
n = 0
for rel in FISIERE:
    src = DOCS / rel
    if not src.exists():
        print(f"  LIPSĂ: {rel}")
        continue
    html = markdown.markdown(src.read_text(encoding="utf-8"),
                             extensions=["tables", "fenced_code", "sane_lists", "nl2br"])
    flat = rel.replace("/", "-").rsplit(".", 1)[0] + ".html"
    (OUT / flat).write_text(TPL.format(css=CSS, body=html), encoding="utf-8")
    n += 1
print(f"HTML scris: {n} fișiere în {OUT}")
