# -*- mode: python ; coding: utf-8 -*-
"""Spec PyInstaller pentru aplicatia de evaluare ANEVAR.

Produce un singur executabil `evaluare-anevar.exe` care porneste serverul local
si deschide browserul. Include sabloanele Jinja2 si colecteaza dependentele cu
importuri dinamice (uvicorn, anthropic).
"""
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

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
    excludes=["PIL._avif", "PIL.AvifImagePlugin", "tkinter", "test",
              "lib2to3", "PIL.ImageTk", "cryptography",
              "numpy", "scipy", "pandas", "matplotlib", "sklearn", "sympy"],
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
    upx=False,          # UPX corupea binare native (ex. PIL\_imagingft.pyd -> „decompression -1"); dezactivat
    upx_exclude=[],
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
