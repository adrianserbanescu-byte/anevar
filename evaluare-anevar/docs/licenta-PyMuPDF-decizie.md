# Licență PyMuPDF — memo de decizie (P0 legal pre-lansare comercială)

> **Întrebarea:** PyMuPDF e dual-licențiat **AGPL-3.0 / comercial Artifex**. Aplicația se distribuie ca
> `.exe` (PyInstaller). Putem lansa comercial fără să open-source-uim tot codul și fără să plătim Artifex?
>
> **Răspuns scurt: DA — pentru că PyMuPDF e folosit într-un singur loc, banal, ușor de înlocuit cu o
> bibliotecă permisivă (`pypdf`, BSD). Nu e nevoie nici de AGPL, nici de licență Artifex.**
>
> Flag inițial: sesiunea D (audit licențe). Acest memo adaugă stratul lipsă: *cât de greu e de rezolvat*.
> ⚠️ Document de analiză — decizia finală (și eventualul cost Artifex) rămân ale tale. Zero fix aplicat.

---

## 1. Cât de adâncă e dependența? (răspuns: foarte superficială)

PyMuPDF (`fitz`) apare în **un singur fișier**, pentru **o singură operație** — extragere de text:

`evaluare-anevar/src/evaluare/ingestie/ocr.py` → `text_din_pdf()`:
```python
import fitz                                   # PyMuPDF
doc = fitz.open(stream=bytes(sursa), filetype="pdf")   # sau fitz.open(path)
return "\n".join(p.get_text() for p in doc)
```

- Folosește DOAR `fitz.open()` + `page.get_text()`. **Fără** randare, layout-analysis, adnotări, generare PDF.
- Generarea PDF a raportului folosește **LibreOffice/soffice** (`report/pdf.py`), NU PyMuPDF.
- `extrage_text()` are deja fallback OCR injectabil + tratare grațioasă a excepțiilor → înlocuirea nu atinge contractul public al modulului.

**Concluzie:** suprafața de înlocuit ≈ **6 linii**, contenită, cu testabilitate ușoară pe PDF-uri reale (extras CF, CPE).

## 2. Ce cere de fapt AGPL-3.0 la distribuirea unui `.exe`

- AGPL ⊇ GPL: **distribuirea** (conveying) binarului care înglobează MuPDF/PyMuPDF obligă la oferirea
  **codului sursă al ÎNTREGII aplicații** sub AGPL. (Clauza „Affero" §13 — network use — nu se aplică la un
  desktop offline, dar obligația GPL de conveying se aplică oricum.)
- **Declanșatorul e DISTRIBUȚIA.** Cât timp folosești app-ul intern (nedistribuit), nu există obligație.
  P0 apare exact pe scenariul de lansare = `.exe` livrat evaluatorilor/clienților.
- PyInstaller (GPLv2 + linking exception) = **OK** pentru `.exe` proprietar — nu el e problema, ci payload-ul MuPDF.

Surse: [Artifex Licensing](https://artifex.com/licensing) · [PyMuPDF — About/Licensing](https://pymupdf.readthedocs.io/en/latest/about.html) · [Licence discussion #971](https://github.com/pymupdf/PyMuPDF/discussions/971) · [AGPL/version issue #4504](https://github.com/pymupdf/pymupdf/issues/4504)

## 3. Cele 3 ieșiri

| Opțiune | Ce implică | Cost | Verdict |
|---|---|---|---|
| **A. Înlocuire cu bibliotecă permisivă** | rescrii `text_din_pdf()` (~6 linii) + swap dep în `pyproject.toml`/`requirements.lock` + re-test extragere | **timp mic, 0 lei, 0 obligații** | ✅ **RECOMANDAT** |
| B. Cumperi licență comercială Artifex | păstrezi PyMuPDF identic | **cost recurent** (orientativ vehiculat $10k–50k/an, **NECONFIRMAT** — se cere ofertă la Artifex) + procurement | ❌ disproporționat pt o extragere de text |
| C. Open-source întreaga app sub AGPL | tot codul devine AGPL/freeware | „gratis" dar **incompatibil cu lansarea comercială** | ❌ contrazice planul de piață |

## 4. Alternative permisive pentru nevoia reală (extragere text PDF digital)

| Bibliotecă | Licență | Tip | Potrivire pt cazul nostru |
|---|---|---|---|
| **`pypdf`** | **BSD** | pur Python (fără binar) | ✅ **cel mai simplu**: 0 binar de împachetat în `.exe`, licență permisivă, viteza (10–20× mai lent) irelevantă pe PDF-uri mici (CF/CPE single-doc) |
| **`pypdfium2`** | **Apache-2.0 / BSD-3** | binding C la PDFium (Google) | ✅ aproape de viteza/fidelitatea PyMuPDF; dar **reintroduce un binar compilat** de împachetat (ca acum) |
| `pdfplumber` | MIT | pe pdfminer.six | ⚠️ char-level + tabele; arbore de dependențe mai greu; overkill pt text simplu |
| `pikepdf` | MPL-2.0 | manipulare PDF | ❌ **nu extrage text** — neaplicabil |

Surse: [Python PDF ecosystem (Thoma)](https://martinthoma.medium.com/the-python-pdf-ecosystem-in-2024-2cad87732e49) · [pypdf comparisons](https://pypdf.readthedocs.io/en/stable/meta/comparisons.html) · [pypdfium2 (PyPI)](https://pypi.org/project/pypdfium2/)

## 5. Recomandare

**Opțiunea A cu `pypdf` (BSD).** Motive:
1. Elimină complet riscul AGPL (licență permisivă, fără obligație de cod sursă).
2. **Bonus de împachetare:** `pypdf` e pur-Python → scoți un **binar compilat** din bundle-ul `.exe`
   (mai puține bătăi de cap PyInstaller, în spiritul pinning-ului existent din `pyproject.toml`).
3. Schimbarea e izolată la `ocr.py` (~6 linii) + dep swap; OCR-ul de rezervă rămâne neatins.
4. Dacă mai târziu apare nevoie de fidelitate/viteză mai mare la extragere → `pypdfium2` (tot permisiv) e upgrade-ul.

Schiță de înlocuire (pentru cine implementează — NU aplicată aici):
```python
from pypdf import PdfReader
import io
def text_din_pdf(sursa):
    r = PdfReader(io.BytesIO(bytes(sursa)) if isinstance(sursa,(bytes,bytearray)) else str(sursa))
    return "\n".join((p.extract_text() or "") for p in r.pages)
```
Apoi: `pyproject.toml` `PyMuPDF>=1.24,<2` → `pypdf>=4,<6`; regenerează `requirements.lock`; rulează testele de ingestie pe un extras CF + un CPE real.

## 6. Cui revine

- **Implementarea** atinge `ingestie/ocr.py` (motor) → lane B sau A, **decizia ta**. Eu (E) raportez, nu fixez.
- **Efort estimat:** mic (1 fișier + dep + 1-2 teste de extragere). Risc: mic (modul cu fallback + tratare excepții deja prezente).
