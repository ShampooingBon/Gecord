
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

# Dossier contenant ce fichier .spec
PROJECT_DIR = Path(SPECPATH)

# Fichier Python principal de Gecord
MAIN_SCRIPT = PROJECT_DIR / "gecord_app.py"

# Fichiers de ressources
LOGO = PROJECT_DIR / "logo.png"

a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=[
        (str(LOGO), "."),
    ] if LOGO.exists() else [],
    hiddenimports=[
        "kivy",
        "kivy.core.window",
        "kivy.core.text",
        "kivy.core.image",
        "kivy.uix",
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
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

