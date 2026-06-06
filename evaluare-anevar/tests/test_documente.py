"""Convertorul Markdown→HTML + registrul de documente (pagina /documente)."""
from __future__ import annotations

from evaluare.documente import incarca, listeaza, md_to_html


def test_md_titluri_si_hr():
    h = md_to_html("# Unu\n## Doi\n\n---")
    assert "<h1>Unu</h1>" in h and "<h2>Doi</h2>" in h and "<hr>" in h


def test_md_bold_cod_link():
    h = md_to_html("Text **gros**, `cod` și [aici](/x).")
    assert "<strong>gros</strong>" in h and "<code>cod</code>" in h
    assert '<a href="/x">aici</a>' in h


def test_md_liste():
    h = md_to_html("- a\n- b").replace("\n", "")
    assert "<ul><li>a</li><li>b</li></ul>" in h
    o = md_to_html("1. x\n2. y").replace("\n", "")
    assert "<ol><li>x</li><li>y</li></ol>" in o


def test_md_tabel():
    h = md_to_html("| A | B |\n|---|---|\n| 1 | 2 |")
    assert "<table>" in h and "<th>A</th>" in h and "<td>1</td>" in h and "<td>2</td>" in h


def test_md_citat():
    h = md_to_html("> o notă\n> pe două rânduri")
    assert "<blockquote>" in h and "o notă" in h


def test_md_escape_html():
    h = md_to_html("Un <script>rău</script> & altele")
    assert "<script>" not in h and "&lt;script&gt;" in h and "&amp;" in h


def test_registru_are_documente_impachetate():
    lst = listeaza()
    assert len(lst) >= 5                                   # cel puțin juridicele + sinteza
    assert any(d["slug"] == "disclaimer-profesional" for d in lst)


def test_incarca_document_si_inexistent():
    meta, html = incarca("disclaimer-profesional")
    assert meta["titlu"] and "<" in html                   # are conținut HTML
    import pytest
    with pytest.raises(KeyError):
        incarca("nu-exista")
