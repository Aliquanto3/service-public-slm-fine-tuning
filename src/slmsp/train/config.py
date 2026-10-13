"""Configuration d'entraînement : `config/entrainement.toml` (stories 10.3 et 10.4).

La story 10.3 crée le module avec `ConfigCouts` (protocole de mesure du coût d'un Run,
section `[couts]`). La story 10.4 le complète (`RunConfig`, sections de campagne).
`config/mesures.toml` reste à la story 6.4 : `train` ne peut pas importer `measure` (AD-1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from pydantic import Field

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet

NOM_ENTRAINEMENT: Final = "entrainement.toml"


class ConfigCouts(ModeleConfig):
    """Section `[couts]` : protocole de mesure du coût d'un Run (FR-33)."""

    pas_chauffe: int = Field(default=10, ge=0)
    """Pas d'optimisation exclus du calcul du débit."""
    periode_echantillonnage_ms: int = Field(default=200, ge=1)
    """Période d'échantillonnage NVML (puissance, mémoire), en millisecondes."""


class ConfigEntrainement(ModeleConfig):
    """Contenu de `config/entrainement.toml`."""

    schema_version: Literal[1]
    couts: ConfigCouts = Field(default_factory=ConfigCouts)


def charger_entrainement(chemin: str | Path | None = None) -> ConfigEntrainement:
    """Lit `entrainement.toml` (défaut : `<racine du projet>/config/entrainement.toml`).

    Lève `ConfigurationInvalide` si le fichier est absent, illisible ou non conforme.
    """
    return charger_toml(
        chemin if chemin is not None else racine_projet() / "config" / NOM_ENTRAINEMENT,
        ConfigEntrainement,
    )
