# -*- mode: python ; coding: utf-8 -*-
"""Gecord PyInstaller spec shared by Windows and Linux.

Use this same file on both systems, but run PyInstaller separately on each OS.
PyInstaller does not cross-compile Windows executables from Linux or vice versa.
"""
from pathlib import Path

PROJECT_DIR = Path(SPECPATH)

# IMPORTANT: Change "main.py" to the exact name of Gecord's main Python file.
MAIN_SCRIPT = PROJECT_DIR / "main.py"

if not MAIN_SCRIPT.is_file():
    raise FileNotFoundError(
        f"Main Python file not found: {MAIN_SCRIPT}\n"
        "Edit MAIN_SCRIPT in pyinstaller.spec to match your actual filename."
    )

# Include static assets if present. The app must store mutable data such as
# geccord_data.json and debug.log in a writable user-data folder at runtime.
datas = []
for filename in ("logo.png",):
    asset = PROJECT_DIR / filename
    if asset.is_file():
        datas.append((str(asset), "."))

a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "kivy",
        "kivy.core.window",
        "kivy.core.text",
        "kivy.core.image",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Gecord",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

# Build separately on Windows and Linux with:
#   python -m PyInstaller pyinstaller.spec
