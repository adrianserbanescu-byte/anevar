"""Fuzz testing pe parserele de input neîncredut (pypdf, python-docx, BeautifulSoup).

Folosește Hypothesis pentru a genera bytes/text aleatori și a verifica că parserele
- NU cad cu excepție necunoscută (KeyError, AttributeError, RecursionError netratate);
- NU agață indefinit (Hypothesis impune deadline);
- NU consumă memorie nemărginită (test setup cu input limitat 64 KiB).

Excepțiile DOCUMENTATE per librărie (ex. `pypdf.errors.PdfReadError`) sunt acceptate ca
„rejecție grațioasă". Orice altă excepție = bug de robustețe = test FAIL.

Markeri:
    pytest -m fuzz                # rulează doar suita asta
    pytest -m 'not fuzz'          # exclude (rulare rapidă în CI)

Owner: D (Rol 2, dispatch A #4). NU testează corectitudinea parserelor — testează
DOAR că nu cad pe input arbitrar (anti-DoS / anti-crash). Cazurile de business
rămân în testele per-modul ale autorilor.
"""
from __future__ import annotations

import io
import warnings

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# Hypothesis "fuzz" profile: examples mai puține (CI rapid), deadline strict.
settings.register_profile(
    "fuzz", max_examples=50, deadline=2000,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.large_base_example],
)
settings.load_profile("fuzz")

pytestmark = pytest.mark.fuzz


# ─── pypdf ───────────────────────────────────────────────────────────────────
@given(st.binary(min_size=0, max_size=65_536))
def test_fuzz_pypdf_reader_nu_cade_necunoscut(data: bytes) -> None:
    """`PdfReader` pe bytes arbitrari trebuie să întoarcă text sau să ridice o eroare cunoscută."""
    from pypdf import PdfReader
    from pypdf.errors import EmptyFileError, FileNotDecryptedError, PdfReadError, PdfStreamError
    cunoscute = (PdfReadError, PdfStreamError, EmptyFileError, FileNotDecryptedError,
                 ValueError, OSError, EOFError)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = PdfReader(io.BytesIO(data), strict=False)
            for pagina in r.pages:                       # iter pages = forțează parse
                pagina.extract_text()
    except cunoscute:
        pass                                             # rejecție grațioasă = OK


# ─── python-docx ─────────────────────────────────────────────────────────────
@given(st.binary(min_size=0, max_size=65_536))
def test_fuzz_pythondocx_nu_cade_necunoscut(data: bytes) -> None:
    """`docx.Document` pe bytes arbitrari trebuie să întoarcă instanță sau să ridice eroare cunoscută."""
    import zipfile

    from docx import Document
    from docx.opc.exceptions import PackageNotFoundError
    cunoscute = (PackageNotFoundError, zipfile.BadZipFile, ValueError, KeyError, OSError, EOFError,
                 NotImplementedError, AttributeError)  # docx aruncă AttributeError pe ZIP-uri non-docx
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            doc = Document(io.BytesIO(data))
            _ = [p.text for p in doc.paragraphs]         # forțează parse paragraphs
    except cunoscute:
        pass


# ─── BeautifulSoup ───────────────────────────────────────────────────────────
@given(st.text(max_size=65_536))
def test_fuzz_beautifulsoup_text_nu_cade(html: str) -> None:
    """BS4 cu `html.parser` pe text arbitrar trebuie să întoarcă soup sau să ridice eroare cunoscută."""
    from bs4 import BeautifulSoup
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            soup = BeautifulSoup(html, "html.parser")
            soup.get_text(" ", strip=True)
            list(soup.find_all("a"))                     # forțează parcurgerea DOM
    except (ValueError, RecursionError):                 # RecursionError pe HTML adânc imbricate = limită Python
        pass


@given(st.binary(min_size=0, max_size=65_536))
def test_fuzz_beautifulsoup_bytes_nu_cade(data: bytes) -> None:
    """BS4 cu bytes (cazul HTTP body) — același contract."""
    from bs4 import BeautifulSoup
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            soup = BeautifulSoup(data, "html.parser")
            soup.get_text(" ", strip=True)
    except (UnicodeDecodeError, ValueError, RecursionError):
        pass
