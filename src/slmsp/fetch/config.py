"""Configuration du téléchargeur `slmsp fetch` (AD-22, AD-28).

`config/fetch.toml` (relances, blocs, seuils d'espace disque), `config/sources.toml` (jeux
MediaTech), `config/llamacpp.toml` et `config/modeles/<slug>.toml`. Les fichiers sont lus
sous `dossier_config()` (`<racine du projet>/config`), jamais sous `--racine` : la
configuration suit le code exécuté.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

from pydantic import Field, StringConstraints, field_validator

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas import Sha256
from slmsp.core.schemas.config_llamacpp import ConfigLlamacpp
from slmsp.core.schemas.config_modele import ConfigModele, RevisionHf

MOTIF_SLUG = re.compile(r"[a-z0-9.-]+")
MOTIF_DEPOT = r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$"
"""Dépôt Hugging Face `organisation/nom`."""

Depot = Annotated[str, StringConstraints(pattern=MOTIF_DEPOT)]


def dossier_config() -> Path:
    """Dossier des fichiers de configuration : `<racine du projet>/config`."""
    return racine_projet() / "config"


class ConfigTelechargement(ModeleConfig):
    """Relances, taille des blocs et vérification de l'espace disque."""

    essais: int = Field(ge=1)
    attente_initiale: float = Field(ge=0)
    attente_max: float = Field(ge=0)
    taille_bloc: int = Field(gt=0)
    seuil_verification_espace: int = Field(ge=0)
    marge_espace: int = Field(ge=0)
    facteur_extraction: float = Field(ge=1)


class ConfigFetch(ModeleConfig):
    """Contenu de `config/fetch.toml`."""

    telechargement: ConfigTelechargement


def chemin_sur(chemin: str) -> str:
    """Valide un chemin relatif de dépôt (`/` comme séparateur, sans `..` ni racine)."""
    parties = chemin.split("/")
    if (
        not chemin
        or "\\" in chemin
        or ":" in chemin
        or chemin.startswith("/")
        or any(partie in ("", ".", "..") for partie in parties)
    ):
        raise ValueError(f"chemin de dépôt invalide : {chemin!r}")
    return chemin


def chemin_config(chemin: str, origine: str) -> str:
    """`chemin_sur` pour une valeur lue en configuration : lève `ConfigurationInvalide`."""
    try:
        return chemin_sur(chemin)
    except ValueError as exc:
        raise ConfigurationInvalide(f"{origine} : {exc}") from None


class FichierSource(ModeleConfig):
    """Fichier d'un jeu : chemin dans le dépôt, SHA-256 et taille attendus."""

    chemin: str
    sha256: Sha256
    taille: int = Field(ge=0)

    @field_validator("chemin")
    @classmethod
    def _chemin(cls, valeur: str) -> str:
        return chemin_sur(valeur)


class JeuSource(ModeleConfig):
    """Jeu de données Hugging Face épinglé par commit."""

    nom: Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9.-]*$")]
    depot: Depot
    revision: RevisionHf
    licence: Annotated[str, StringConstraints(min_length=1)]
    fichiers: list[FichierSource] = Field(min_length=1)


class ConfigSources(ModeleConfig):
    """Contenu de `config/sources.toml`."""

    jeux: list[JeuSource] = Field(min_length=1)

    @field_validator("jeux")
    @classmethod
    def _noms_uniques(cls, valeur: list[JeuSource]) -> list[JeuSource]:
        noms = [jeu.nom for jeu in valeur]
        if len(noms) != len(set(noms)):
            raise ValueError("deux jeux portent le même nom")
        return valeur


def _dossier(dossier: str | Path | None) -> Path:
    return Path(dossier) if dossier is not None else dossier_config()


def charger_config_fetch(dossier: str | Path | None = None) -> ConfigTelechargement:
    """Section `[telechargement]` de `<dossier>/fetch.toml`."""
    return charger_toml(_dossier(dossier) / "fetch.toml", ConfigFetch).telechargement


def charger_config_sources(dossier: str | Path | None = None) -> ConfigSources:
    """Jeux de `<dossier>/sources.toml`."""
    return charger_toml(_dossier(dossier) / "sources.toml", ConfigSources)


def charger_config_llamacpp(dossier: str | Path | None = None) -> ConfigLlamacpp:
    """Version figée de llama.cpp, `<dossier>/llamacpp.toml`."""
    return charger_toml(_dossier(dossier) / "llamacpp.toml", ConfigLlamacpp)


def charger_config_modele(slug: str, dossier: str | Path | None = None) -> ConfigModele:
    """Configuration du modèle `slug`, `<dossier>/modeles/<slug>.toml`.

    Lève `ConfigurationInvalide` pour un slug hors `^[a-z0-9.-]+$` ou un fichier absent.
    """
    if not isinstance(slug, str) or not MOTIF_SLUG.fullmatch(slug) or slug.strip(".") != slug:
        raise ConfigurationInvalide(f"slug de modèle invalide : {slug!r}")
    return charger_toml(_dossier(dossier) / "modeles" / f"{slug}.toml", ConfigModele)


__all__ = [
    "ConfigFetch",
    "ConfigSources",
    "ConfigTelechargement",
    "FichierSource",
    "JeuSource",
    "charger_config_fetch",
    "charger_config_llamacpp",
    "charger_config_modele",
    "charger_config_sources",
    "chemin_config",
    "chemin_sur",
    "dossier_config",
]
