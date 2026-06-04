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
    excludes=["PIL._avif", "PIL.AvifImagePlugin"],
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
)
