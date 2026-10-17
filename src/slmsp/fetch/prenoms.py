"""Pilote `slmsp fetch prenoms` : fichier national des prénoms de l'INSEE (story 12.3).

URL, SHA-256 et taille viennent de `config/outillage.toml` (`[prenoms-insee]`). L'archive est
téléchargée par la passerelle (profil `outillage`), vérifiée, puis `prenoms_depuis_csv_insee`
en tire `ressources/prenoms.txt` (au moins 20 naissances cumulées, au moins 3 lettres). Aucun
prénom n'est écrit à la main.
"""

from __future__ import annotations

import tomllib
import zipfile
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.fetch.config import dossier_config
from slmsp.fetch.hf import ArchiveInvalide, ResultatFichier, Telechargeur


class ConfigPrenoms(BaseModel):
    """Section `[prenoms-insee]` de `config/outillage.toml`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    taille: int = Field(gt=0)
    membre: str
    licence: str


def charger_config_prenoms(dossier: Path | None = None) -> ConfigPrenoms:
    chemin = (dossier or dossier_config()) / "outillage.toml"
    try:
        section = tomllib.loads(chemin.read_text(encoding="utf-8"))["prenoms-insee"]
        return ConfigPrenoms.model_validate(section)
    except (OSError, KeyError, tomllib.TOMLDecodeError, ValidationError) as exc:
        raise ConfigurationInvalide(f"{chemin} : [prenoms-insee] illisible ({exc})") from None


def dossier_archive(racine: str | Path) -> Path:
    """`<racine>/data/raw/insee/prenoms`."""
    return Path(racine) / "data" / "raw" / "insee" / "prenoms"


def lignes_csv(archive: Path, membre: str) -> list[str]:
    try:
        with zipfile.ZipFile(archive) as zf:
            return zf.read(membre).decode("utf-8").splitlines()
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError) as exc:
        raise ArchiveInvalide(f"{archive} : {membre} illisible ({type(exc).__name__})") from None


def entete(config: ConfigPrenoms, minimum: int) -> str:
    return (
        "# Prénoms de France (fichier national INSEE 1900-2022), Licence Ouverte 2.0.\n"
        f"# Source : {config.url}\n"
        f"# SHA-256 de l'archive : {config.sha256}\n"
        f"# Règles : au moins {minimum} naissances cumulées, au moins 3 lettres.\n"
        "# Fichier généré par `slmsp fetch prenoms` : ne pas modifier à la main.\n"
    )


def executer(
    telechargeur: Telechargeur,
    config: ConfigPrenoms,
    racine: str | Path,
    *,
    sortie: Path,
    extraire: Callable[[Iterable[str]], list[str]],
    minimum: int,
    consigner: Callable[[dict[str, Any]], None] = lambda _ligne: None,
) -> tuple[ResultatFichier, int]:
    """Télécharge et vérifie l'archive, écrit `sortie` ; rend le résultat et le nombre de prénoms.

    `extraire` (`prenoms_depuis_csv_insee`, injecté par la CLI : `fetch` ignore `app`) applique
    les règles de sélection, dont le seuil `minimum` de naissances.
    """
    destination = dossier_archive(racine) / Path(config.url).name
    resultat = telechargeur.telecharger(config.url, destination, config.sha256, config.taille)
    prenoms = extraire(lignes_csv(destination, config.membre))
    if not prenoms:
        raise ArchiveInvalide(f"{destination} : aucun prénom retenu")
    sortie.parent.mkdir(parents=True, exist_ok=True)
    with open(sortie, "w", encoding="utf-8", newline="\n") as f:
        f.write(entete(config, minimum) + "\n".join(prenoms) + "\n")
    consigner(
        {
            "url": config.url,
            "licence": config.licence,
            "octets": resultat.octets,
            "taille": resultat.taille,
            "sha256": resultat.sha256,
            "statut": resultat.statut,
            "destination": str(destination),
            "sortie": str(sortie),
            "prenoms": len(prenoms),
        }
    )
    return resultat, len(prenoms)


__all__ = ["ConfigPrenoms", "charger_config_prenoms", "executer", "lignes_csv"]
