"""Configuration de l'application Windows, `config/application.toml` (AD-23, story 12.1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator

from slmsp.core.config import charger_toml, etendre_chemin, racine_projet
from slmsp.core.schemas import SchemaBase

_MOTIF_SLUG = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
_MOTIF_LANGUE = re.compile(r"^[a-z]{2,3}(?:-[A-Z]{2})?$")


class ConfigApplication(SchemaBase):
    """Modèle embarqué, variante, threads, dossier de données et langues de traduction."""

    schema_version: Literal[1] = 1
    modele: str
    variante: Literal["cpu", "cuda"] = "cpu"
    threads: Annotated[int, Field(ge=1)] | None = None
    dossier_donnees: Annotated[str, Field(min_length=1)]
    langues_traduction: Annotated[list[str], Field(min_length=1)]

    @field_validator("modele")
    @classmethod
    def _modele_connu(cls, valeur: str) -> str:
        # Forme vérifiée d'abord : ni `..`, ni séparateur, ni `base:` (chemin sous config/).
        if not _MOTIF_SLUG.fullmatch(valeur):
            raise ValueError("slug de modèle mal formé : attendu ^[a-z0-9]+([.-][a-z0-9]+)*$")
        fichier = racine_projet() / "config" / "modeles" / f"{valeur}.toml"
        if not fichier.is_file():
            raise ValueError(
                f"modèle « {valeur} » inconnu : un fichier config/modeles/<slug>.toml est attendu"
            )
        return valeur

    @field_validator("langues_traduction")
    @classmethod
    def _langues_valides(cls, valeur: list[str]) -> list[str]:
        if any(not _MOTIF_LANGUE.fullmatch(code) for code in valeur):
            raise ValueError("code de langue mal formé : attendu ISO 639 (ex. « en », « pt-BR »)")
        if len(set(valeur)) != len(valeur):
            raise ValueError("langues_traduction contient des doublons")
        return valeur

    def chemin_donnees(self) -> Path:
        """`dossier_donnees` étendu (`%LOCALAPPDATA%`…) ; `ConfigurationInvalide` sinon."""
        return etendre_chemin(self.dossier_donnees)


def charger_config_application() -> ConfigApplication:
    """`config/application.toml` (lève `ConfigurationInvalide` : fichier, clé ou slug fautifs)."""
    return charger_toml(racine_projet() / "config" / "application.toml", ConfigApplication)


__all__ = ["ConfigApplication", "charger_config_application"]
