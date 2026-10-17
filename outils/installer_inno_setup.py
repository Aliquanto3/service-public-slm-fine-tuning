"""Télécharge et installe Inno Setup pour l'utilisateur courant (story 12.13).

Version, URL et SHA-256 viennent de `config/outillage.toml`. Téléchargement par la passerelle
(profil `outillage`), vérification de l'empreinte avant exécution, puis installation sans droits
administrateur : `/CURRENTUSER /VERYSILENT /DIR=<vendor>/inno-setup`.

    uv run --no-sync python outils/installer_inno_setup.py [--vendor <dossier>]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPOT / "src"))

from slmsp.core.canonique import sha256_fichier  # noqa: E402


def charger_config() -> dict[str, object]:
    donnees = tomllib.loads((DEPOT / "config" / "outillage.toml").read_text(encoding="utf-8"))
    return dict(donnees["inno-setup"])


def telecharger(url: str, cible: Path) -> None:
    from slmsp.net import client

    with client("outillage", follow_redirects=True) as c:
        reponse = c.get(url)
    reponse.raise_for_status()
    cible.write_bytes(reponse.content)


def installer(vendor: Path, telecharger_fn=telecharger) -> Path:
    cfg = charger_config()
    dossier = vendor / str(cfg["dossier"])
    iscc = dossier / "ISCC.exe"
    if iscc.is_file():
        return iscc
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / f"innosetup-{cfg['version']}.exe"
        telecharger_fn(str(cfg["url"]), exe)
        if sha256_fichier(exe) != cfg["sha256"]:
            raise SystemExit("ECHEC : SHA-256 d'Inno Setup différent de config/outillage.toml")
        cmd = [str(exe), "/CURRENTUSER", "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
        if subprocess.run([*cmd, f"/DIR={dossier}"], check=False).returncode != 0:
            raise SystemExit("ECHEC : l'installation d'Inno Setup a échoué")
    if not iscc.is_file():
        raise SystemExit(f"ECHEC : {iscc} absent après installation")
    return iscc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    p.add_argument("--vendor", default=os.environ.get("SLMSP_VENDOR_DIR", str(DEPOT / "vendor")))
    iscc = installer(Path(p.parse_args(argv).vendor))
    print(iscc)  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
