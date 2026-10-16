# -*- mode: python ; coding: utf-8 -*-
# PyInstaller `onedir` (Q3, jamais `onefile`). Lancé par `outils/construire_application.py`,
# qui passe la liste des données dans le fichier JSON désigné par SLMSP_PLAN_BUILD.
import json
import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

DEPOT = Path(SPECPATH).parent
sys.path.insert(0, str(DEPOT / "outils"))
from construire_application import EXCLUSIONS, NOM_APPLICATION  # noqa: E402

PLAN = Path(os.environ["SLMSP_PLAN_BUILD"])
donnees = [tuple(couple) for couple in json.loads(PLAN.read_text("utf-8"))]
cachees = []
for paquet in (
    "slmsp.app", "slmsp.harness", "slmsp.index", "slmsp.inference",
    "slmsp.net", "slmsp.mcp", "slmsp.core",
):
    cachees += collect_submodules(paquet)

a = Analysis(
    [str(DEPOT / "packaging" / "lanceur.py")],
    pathex=[str(DEPOT / "src")],
    datas=donnees,
    hiddenimports=cachees,
    excludes=list(EXCLUSIONS),
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # onedir
    name=NOM_APPLICATION,
    console=False,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, upx=False, name=NOM_APPLICATION)
