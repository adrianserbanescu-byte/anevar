"""Regresie: JS inline din template-urile RANDATE (Jinja efectiv) trebuie sa fie sintactic valid.

Context bug (commit 624e0f0): un `{{ icon('import') }}` pus intr-un STRING JS in dosar.html
randa `<svg class="ico" ... viewBox="0 0 16 16" ...>` — cu GHILIMELE DUBLE — in interiorul unui
string JS deja delimitat cu ghilimele duble. Rezultatul: string-ul se inchidea prematur la primul
`"` din SVG si TOT scriptul devenea sintactic invalid (eroare de parsare) -> intreg JS-ul mort.

De ce verificarea veche NU a prins-o: agentii rulau `node --check` pe JS-ul cu Jinja STRIPAT
(`{{ ... }}` scos cu regex). Stripat, `{{ icon('import') }}` disparea complet, deci string-ul ramanea
valid si `node --check` trecea — desi pagina REALA (cu Jinja randat) era rupta.

Acest test inchide gaura: RANDEAZA template-urile prin Jinja (efectiv, nu stripat), extrage fiecare
bloc `<script>` inline (fara `src=`), si ruleaza `node --check` pe el. Pica pe bug-ul vechi (SVG cu
ghilimele duble intr-un string dublu = eroare de sintaxa) si trece pe master curent (deja reparat).
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

# Blocuri <script> inline (fara atribut src=). Non-greedy, case-insensitive, peste linii.
_SCRIPT_RE = re.compile(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL)

# Paginile fara dosar care contin JS inline relevant.
_PAGINI_SIMPLE = ("/descoperire", "/grila", "/registru", "/aml")


def _node() -> str | None:
    """Calea catre executabilul `node`, sau None daca nu e in PATH."""
    return shutil.which("node")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    s = Storage(tmp_path / "d.db")
    s.init()
    c = TestClient(create_app(storage=s, client=None))
    c._baza = tmp_path
    return c


def _cont(client):
    """Creeaza contul evaluatorului (necesar pentru a crea un dosar)."""
    return client.post("/api/cont", json={"nume": "Adi S", "legitimatie": "8717"})


def _extrage_scripturi_inline(html: str) -> list[str]:
    """Toate blocurile <script> inline (fara src) din HTML, neglijand cele goale."""
    return [m.group(1) for m in _SCRIPT_RE.finditer(html) if m.group(1).strip()]


def _verifica_js_valid(node: str, html: str, eticheta: str) -> None:
    """Ruleaza `node --check` pe fiecare bloc <script> inline din `html`."""
    scripturi = _extrage_scripturi_inline(html)
    assert scripturi, f"{eticheta}: nu am gasit niciun bloc <script> inline (regex/ruta gresita?)"
    for i, js in enumerate(scripturi):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", delete=False, encoding="utf-8"
        ) as f:
            f.write(js)
            cale = f.name
        try:
            r = subprocess.run(
                [node, "--check", cale],
                capture_output=True,
                text=True,
            )
        finally:
            Path(cale).unlink(missing_ok=True)
        assert r.returncode == 0, (
            f"{eticheta}: blocul <script> #{i} are JS invalid sintactic.\n"
            f"node --check stderr:\n{r.stderr}"
        )


def test_js_inline_valid_pe_pagini_simple(client):
    """Paginile fara dosar: JS inline (Jinja randat) trebuie sa treaca `node --check`."""
    node = _node()
    if node is None:
        pytest.skip("node indisponibil")
    for ruta in _PAGINI_SIMPLE:
        r = client.get(ruta)
        assert r.status_code == 200, f"{ruta} -> {r.status_code}"
        _verifica_js_valid(node, r.text, eticheta=ruta)


def test_js_inline_valid_pe_pagina_dosar(client):
    """Pagina de dosar: aici traia bug-ul `{{ icon('import') }}` in string JS.

    Randam dosarul REAL (cu Jinja efectiv), nu un JS cu Jinja stripat — exact conditia in care
    `{{ icon('import') }}` expandeaza la `<svg class="ico" ...>` si rupea string-ul JS. Pe master
    curent (📥 in loc de icon()) trece; pe bug-ul vechi ar pica cu eroare de sintaxa.
    """
    node = _node()
    if node is None:
        pytest.skip("node indisponibil")
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "X"}}).json()["uuid"]
    r = client.get(f"/dosar/{uid}")
    assert r.status_code == 200, f"/dosar/{uid} -> {r.status_code}"
    _verifica_js_valid(node, r.text, eticheta=f"/dosar/{uid}")
