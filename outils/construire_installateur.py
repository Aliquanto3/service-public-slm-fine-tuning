"""Construit l'installateur Inno Setup de l'Assistant (story 12.13, FR-21, FR-22, Q2, Q3, Q4, Q6).

Prend le dossier `dist/AssistantSP` (12.12), appelle `ISCC.exe` avec `packaging/assistantsp.iss`
puis écrit l'empreinte SHA-256 de l'installateur (Q4, pas de signature) dans un fichier
`<installateur>.sha256` publié avec lui.

    uv run --no-sync python outils/construire_installateur.py
    uv run --no-sync python outils/construire_installateur.py --iscc <chemin>/ISCC.exe

ISCC est cherché dans : `--iscc`, `SLMSP_ISCC`, `vendor/innosetup/ISCC.exe`,
`%LOCALAPPDATA%/Programs/Inno Setup 6/ISCC.exe`, puis le PATH. Aucun téléchargement ici
(hôte jrsoftware.org hors passerelle) : voir `docs/installation-dsi.md`.
Variante « pack complet » (Q2) : `--pack-complet <MicrosoftEdgeWebView2RuntimeInstallerX64.exe>`.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPOT / "src"))

from slmsp.core.canonique import sha256_fichier  # noqa: E402

SCRIPT_ISS = DEPOT / "packaging" / "assistantsp.iss"
NOM_SORTIE = "AssistantSP-Setup"
LIMITE_DECOUPAGE = 2_000_000_000  # au-delà : DiskSpanning (Inno Setup limite un .exe à 2 Go)


class ErreurInstallateur(Exception):
    """Compilateur ou paquet introuvable, compilation échouée."""


def version_application() -> str:
    donnees = tomllib.loads((DEPOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(donnees["project"]["version"])


def trouver_iscc(explicite: str | None = None, env: dict[str, str] | None = None) -> Path:
    """Premier `ISCC.exe` trouvé (voir l'en-tête) ; `ErreurInstallateur` sinon."""
    env = dict(os.environ) if env is None else env
    candidats: list[Path] = []
    for valeur in (explicite, env.get("SLMSP_ISCC")):
        if valeur:  # chemin demandé explicitement : absent = échec, pas de repli silencieux
            if not Path(valeur).is_file():
                raise ErreurInstallateur(f"ISCC.exe explicite introuvable : {valeur}")
            return Path(valeur)
    candidats.append(DEPOT / "vendor" / "innosetup" / "ISCC.exe")
    local = env.get("LOCALAPPDATA")
    if local:
        candidats.append(Path(local) / "Programs" / "Inno Setup 6" / "ISCC.exe")
    for c in candidats:
        if c.is_file():
            return c
    sur_path = shutil.which("ISCC", path=env.get("PATH"))
    if sur_path:
        return Path(sur_path)
    raise ErreurInstallateur(
        "ISCC.exe introuvable : installer Inno Setup pour l'utilisateur courant "
        "(voir docs/installation-dsi.md) ou passer --iscc."
    )


def taille_paquet(source: Path) -> int:
    return sum(p.stat().st_size for p in source.rglob("*") if p.is_file())


def decoupage_necessaire(source: Path) -> bool:
    return taille_paquet(source) > LIMITE_DECOUPAGE


def commande_iscc(
    iscc: Path,
    *,
    source: Path,
    sortie: Path,
    version: str,
    decoupage: bool,
    pack_complet: Path | None = None,
    script: Path = SCRIPT_ISS,
) -> list[str]:
    cmd = [str(iscc), "/Q", f"/DVersionApp={version}", f"/DDossierSource={source}"]
    cmd.append(f"/DDossierSortie={sortie}")
    if decoupage:
        cmd.append("/DDecoupage=1")
    if pack_complet is not None:
        cmd.append(f"/DPackComplet={pack_complet}")
    cmd.append(str(script))
    return cmd


def fichiers_installateur(sortie: Path, version: str) -> list[Path]:
    """`.exe` et, si le paquet est découpé, ses tranches `-N.bin`."""
    base = f"{NOM_SORTIE}-{version}"
    exe = sortie / f"{base}.exe"
    tranches = sorted(
        sortie.glob(f"{base}-*.bin"), key=lambda p: int(re.findall(r"\d+", p.stem)[-1])
    )
    return [exe, *tranches]


def ecrire_empreintes(fichiers: list[Path]) -> Path:
    """`<installateur>.exe.sha256`, format `sha256sum` (`<hex> *<nom>`), une ligne par fichier."""
    lignes = [f"{sha256_fichier(f)} *{f.name}" for f in fichiers]
    cible = fichiers[0].with_name(fichiers[0].name + ".sha256")
    cible.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return cible


def _executer(cmd: list[str]) -> int:
    try:
        return subprocess.run(cmd, check=False).returncode
    except OSError as exc:
        raise ErreurInstallateur(f"ISCC non exécutable : {exc}") from exc


def nettoyer_anciens(sortie: Path, version: str) -> None:
    """Supprime exe, tranches et `.sha256` d'un build précédent de la même version."""
    base = f"{NOM_SORTIE}-{version}"
    anciens = [*sortie.glob(f"{base}-*.bin"), sortie / f"{base}.exe", sortie / f"{base}.exe.sha256"]
    for ancien in anciens:
        ancien.unlink(missing_ok=True)


def construire(args: argparse.Namespace, executer: Callable[[list[str]], int] = _executer) -> Path:
    source = Path(args.source)
    if not (source / "AssistantSP.exe").is_file():
        raise ErreurInstallateur(
            f"paquet absent : {source / 'AssistantSP.exe'} "
            "(lancer outils/construire_application.py)"
        )
    pack = Path(args.pack_complet).resolve() if args.pack_complet else None
    if pack is not None and not pack.is_file():
        raise ErreurInstallateur(f"pack WebView2 introuvable : {pack}")
    iscc = trouver_iscc(args.iscc)
    sortie = Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    version = args.version or version_application()
    nettoyer_anciens(sortie, version)
    cmd = commande_iscc(
        iscc,
        source=source.resolve(),
        sortie=sortie.resolve(),
        version=version,
        decoupage=decoupage_necessaire(source),
        pack_complet=pack,
    )
    if executer(cmd) != 0:
        raise ErreurInstallateur(f"ISCC a échoué : {' '.join(cmd)}")
    fichiers = fichiers_installateur(sortie, version)
    manquants = [f for f in fichiers if not f.is_file()]
    if manquants:
        raise ErreurInstallateur(f"installateur non produit : {manquants[0]}")
    return ecrire_empreintes(fichiers)


def lire_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    p.add_argument("--source", default=str(DEPOT / "dist" / "AssistantSP"))
    p.add_argument("--sortie", default=str(DEPOT / "dist" / "installateur"))
    p.add_argument("--iscc", default=None, help="chemin de ISCC.exe")
    p.add_argument("--version", default=None, help="défaut : version de pyproject.toml")
    p.add_argument("--pack-complet", default=None, help="installateur autonome WebView2 (Q2)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        empreintes = construire(lire_arguments(argv))
    except ErreurInstallateur as exc:
        print(f"ECHEC : {exc}", file=sys.stderr)  # noqa: T201
        return 2
    print(f"empreintes : {empreintes}")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
