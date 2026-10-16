"""Configuration du dossier de publication (`config/publication.toml`, AD-22)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from pydantic import Field, field_validator

from slmsp.core.config import ModeleConfig, charger_toml

NOM_CONFIG = "publication.toml"


class ModelePublication(ModeleConfig):
    """Licences de sortie compatibles avec la licence d'un Modèle de base."""

    licences_compatibles: list[str] = Field(default_factory=list)
    verifie_le: date | None = None
    """Date à laquelle la licence du Modèle de base a été relue ; absente : dossier refusé."""


class ConfigPublication(ModeleConfig):
    schema_version: int = 1
    jeux_proteges: list[str] = Field(default_factory=list)
    ordre_permissivite: list[str] = Field(min_length=1)
    sections_obligatoires: list[str]
    mention_non_certification: str = Field(min_length=1)
    formulations_interdites: list[str]
    mentions_non_certification: list[str]
    motifs_secrets: list[str]
    modeles: dict[str, ModelePublication] = Field(default_factory=dict)

    @field_validator("formulations_interdites", "motifs_secrets")
    @classmethod
    def _regex_valides(cls, valeurs: list[str]) -> list[str]:
        for valeur in valeurs:
            try:
                re.compile(valeur)
            except re.error as exc:
                raise ValueError(f"expression régulière invalide ({exc})") from None
        return valeurs


def charger_config(racine: Path) -> ConfigPublication:
    return charger_toml(racine / "config" / NOM_CONFIG, ConfigPublication)
