# -*- mode: python ; coding: utf-8 -*-
"""Spec PyInstaller pentru aplicatia de evaluare ANEVAR.

Produce un singur executabil `evaluare-anevar.exe` care porneste serverul local
si deschide browserul. Include sabloanele Jinja2 si colecteaza dependentele cu
importuri dinamice (uvicorn, anthropic).
"""
import os

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# build-optim: UPX e OPT-IN. Implicit OPRIT -> build mai rapid (UPX adauga ~30s), fara
# dependenta externa si fara warning-uri cand UPX lipseste. Se activeaza setand env-ul
# ANEVAR_UPX_DIR la folderul cu upx.exe (o face `scripts/build.py --upx`). Castig: ~3 MB
# (PyInstaller deja comprima PKG-ul cu zlib, deci UPX adauga doar marja LZMA pe DLL-urile mari).
_UPX_DIR = os.environ.get("ANEVAR_UPX_DIR", "")
_UPX_ENABLED = bool(_UPX_DIR)

hiddenimports = (
    collect_submodules("uvicorn")
    + collect_submodules("anthropic")
    + ["evaluare", "evaluare.__main__"]
)

datas = collect_data_files("anthropic") + [
    ("src/evaluare/web/templates", "evaluare/web/templates"),
    ("src/evaluare/data", "evaluare/data"),
    ("src/evaluare/aml/data", "evaluare/aml/data"),
]

a = Analysis(
    ["run.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # PIL._avif (Pillow 12 AVIF) corupea arhiva PKG -> „decompression -1" la
    # pornirea exe-ului; nu folosim AVIF (doar poze standard in raport).
    # PIL._avif (Pillow 12) corupea arhiva PKG. tkinter/test = GUI/teste nefolosite
    # de un server local -> excluse pentru a reduce dimensiunea .exe (D5).
    # cryptography\_rust.pyd corupea arhiva PKG („decompression -1"); nefolosit de
    # runtime-ul nostru (HTTPS merge prin ssl stdlib, nu prin pachetul cryptography).
    # numpy/scipy/pandas/matplotlib/sklearn/sympy: NU sunt importate de aplicatie
    # (verificat: la incarcarea completa se incarca doar lxml). PyInstaller le tragea
    # doar pentru ca sunt instalate in mediu -> ~120 MB inutili. Excluse explicit.
    # build-optim: excludem si module pure-Python care intra in graf dar NU sunt folosite
    # de serverul impachetat (masurat pe Analysis-00.toc): pygments ~4.4MB (syntax highlight,
    # doar pt pytest), setuptools/pkg_resources ~1.8MB + pydoc_data ~0.5MB (unelte/help).
    # pytest/_pytest/pip/wheel oricum nu intra in run.py -> excludere = no-op defensiv.
    excludes=["PIL._avif", "PIL.AvifImagePlugin", "tkinter", "test",
              "lib2to3", "PIL.ImageTk", "cryptography",
              "numpy", "scipy", "pandas", "matplotlib", "sklearn", "sympy",
              "pygments", "pydoc_data", "setuptools", "pkg_resources",
              "pip", "wheel", "pytest", "_pytest", "doctest"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="evaluare-anevar",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # build-optim: UPX (opt-in, vezi _UPX_ENABLED sus). Istoric corupea EXTENSIILE native (.pyd,
    # ex. PIL\_imagingft.pyd -> „decompression -1"), asa ca le excludem TOATE, plus interpretorul,
    # runtime-ul C si OpenSSL (HTTPS). Cand e activ, ramane comprimat `mupdfcpp64.dll` (~26MB,
    # plain C++ DLL). Validat: boot + rute + /api/ingestie (calea fitz/mupdf) sub UPX.
    upx=_UPX_ENABLED,
    upx_exclude=[
        "*.pyd",                                   # toate extensiile native (categoria coruptibila)
        "api-ms-win-*.dll", "ucrtbase.dll",        # stub-uri WinAPI/UCRT — UPX da eroare pe ele
        "vcruntime140.dll", "vcruntime140_1.dll",  # runtime C
        "python312.dll", "python3.dll",            # interpretor
        "libcrypto-3.dll", "libssl-3.dll",         # OpenSSL (HTTPS - nu riscam)
    ],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico",          # siglă casă (assets/icon.ico, vezi scripts/_make_icon.py)
    version="version_info.txt",      # metadate Windows (Properties → Details)
)
