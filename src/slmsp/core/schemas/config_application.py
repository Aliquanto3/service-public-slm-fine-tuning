"""Configuration de l'application Windows, `config/application.toml` (AD-23, story 12.1)."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, field_validator

from slmsp.core.config import charger_toml, racine_projet
from slmsp.core.schemas import SchemaBase


class ConfigApplication(SchemaBase):
    """Modèle embarqué, variante, threads, dossier de données et langues de traduction."""

    schema_version: Literal[1] = 1
    modele: str
    variante: Literal["cpu", "cuda"] = "cpu"
    threads: Annotated[int, Field(ge=1)] | None = None
    dossier_donnees: Annotated[str, Field(min_length=1)]
    langues_traduction: list[Annotated[str, Field(min_length=2)]]

    @field_validator("modele")
    @classmethod
    def _modele_connu(cls, valeur: str) -> str:
        fichier = racine_projet() / "config" / "modeles" / f"{valeur}.toml"
        if valeur.startswith("base:") or not valeur or not fichier.is_file():
            raise ValueError(
                f"modèle « {valeur} » inconnu : un fichier config/modeles/<slug>.toml est attendu"
            )
        return valeur


def charger_config_application() -> ConfigApplication:
    """`config/application.toml` (lève `ConfigurationInvalide` : fichier, clé ou slug fautifs)."""
    return charger_toml(racine_projet() / "config" / "application.toml", ConfigApplication)


__all__ = ["ConfigApplication", "charger_config_application"]
