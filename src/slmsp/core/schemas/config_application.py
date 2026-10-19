"""Configuration de l'application Windows, `config/application.toml` (AD-23, story 12.1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from slmsp.core.config import charger_toml, etendre_chemin, racine_projet
from slmsp.core.langues import LANGUES
from slmsp.core.schemas import SchemaBase

_MOTIF_SLUG = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")


def _slug_connu(valeur: str) -> str:
    # Forme vérifiée d'abord : ni `..`, ni séparateur, ni `base:` (chemin sous config/).
    if not _MOTIF_SLUG.fullmatch(valeur):
        raise ValueError("slug de modèle mal formé : attendu ^[a-z0-9]+([.-][a-z0-9]+)*$")
    fichier = racine_projet() / "config" / "modeles" / f"{valeur}.toml"
    if not fichier.is_file():
        raise ValueError(
            f"modèle « {valeur} » inconnu : un fichier config/modeles/<slug>.toml est attendu"
        )
    return valeur


class ConfigApplication(SchemaBase):
    """Modèle embarqué, variante, threads, dossier de données et langues de traduction."""

    schema_version: Literal[1] = 1
    modele: str
    modeles_embarques: Annotated[list[str], Field(min_length=1)]
    variante: Literal["cpu", "cuda"] = "cpu"
    threads: Annotated[int, Field(ge=1)] | None = None
    dossier_donnees: Annotated[str, Field(min_length=1)]
    langues_traduction: Annotated[list[str], Field(min_length=1)]

    @model_validator(mode="before")
    @classmethod
    def _liste_par_defaut(cls, donnees: object) -> object:
        # Rétrocompatibilité : sans `modeles_embarques`, la liste vaut `[modele]`.
        if isinstance(donnees, dict) and "modeles_embarques" not in donnees and "modele" in donnees:
            return {**donnees, "modeles_embarques": [donnees["modele"]]}
        return donnees

    @field_validator("modele")
    @classmethod
    def _modele_connu(cls, valeur: str) -> str:
        return _slug_connu(valeur)

    @field_validator("modeles_embarques")
    @classmethod
    def _modeles_connus(cls, valeur: list[str]) -> list[str]:
        for slug in valeur:
            _slug_connu(slug)
        if len(set(valeur)) != len(valeur):
            raise ValueError("modeles_embarques contient des doublons")
        return valeur

    @model_validator(mode="after")
    def _defaut_embarque(self) -> ConfigApplication:
        if self.modele not in self.modeles_embarques:
            raise ValueError(
                f"le modèle par défaut « {self.modele} » doit figurer dans modeles_embarques"
            )
        return self

    @field_validator("langues_traduction")
    @classmethod
    def _langues_valides(cls, valeur: list[str]) -> list[str]:
        inconnues = [code for code in valeur if code not in LANGUES]
        if inconnues:
            raise ValueError(
                f"langue(s) non gérée(s) par la Tâche TR : {', '.join(inconnues)} "
                f"(attendu parmi {', '.join(LANGUES)})"
            )
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
