"""Configuration de l'entraînement (AD-18) : `config/entrainement.toml`.

Créé par la story 10.3 avec le protocole de mesure du coût (`ConfigCouts`) ; la story 10.4
y ajoute `RunConfig` et le reste du protocole. Le fichier est lu sous
`<racine du projet>/config`, comme les autres configurations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from pydantic import Field

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet

NOM_CONFIG: Final = "entrainement.toml"


class ConfigCouts(ModeleConfig):
    """Protocole de mesure du coût d'un Run (FR-33), identique pour toutes les méthodes."""

    pas_chauffe: int = Field(ge=0)
    """Pas d'optimisation exclus de la mesure du débit."""
    periode_nvml_ms: int = Field(gt=0)
    """Période d'échantillonnage NVML (puissance, mémoire), en millisecondes."""


class ConfigEntrainement(ModeleConfig):
    """Contenu de `config/entrainement.toml`."""

    schema_version: Literal[1]
    couts: ConfigCouts


def chemin_config_entrainement() -> Path:
    """`<racine du projet>/config/entrainement.toml`."""
    return racine_projet() / "config" / NOM_CONFIG


def charger_config_entrainement(chemin: str | Path | None = None) -> ConfigEntrainement:
    """Lit et valide `config/entrainement.toml` (ou `chemin`) ; lève `ConfigurationInvalide`."""
    return charger_toml(
        chemin if chemin is not None else chemin_config_entrainement(), ConfigEntrainement
    )


__all__ = [
    "NOM_CONFIG",
    "ConfigCouts",
    "ConfigEntrainement",
    "charger_config_entrainement",
    "chemin_config_entrainement",
]
