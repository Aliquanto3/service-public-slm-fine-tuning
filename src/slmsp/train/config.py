"""Configuration de l'entraînement : `config/entrainement.toml` (story 10.3).

Créé par la story 10.3 avec le protocole de mesure du coût (`ConfigCouts`, FR-33) ; la
story 10.4 le complète (`RunConfig`). Le fichier est lu par `core.config.charger_toml`
(clés inconnues refusées). `config/mesures.toml` reste à la story 6.4 : `train` n'importe
pas `measure` (AD-1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from pydantic import Field

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet

__all__ = ["ConfigCouts", "ConfigEntrainement", "charger_config_entrainement"]

NOM_ENTRAINEMENT: Final = "entrainement.toml"


class ConfigCouts(ModeleConfig):
    """Protocole de mesure du coût d'un Run."""

    pas_chauffe: int = Field(ge=0)
    periode_echantillonnage_ms: int = Field(gt=0)
    indice_gpu: int = Field(ge=0)


class ConfigEntrainement(ModeleConfig):
    """Contenu de `config/entrainement.toml`."""

    schema_version: Literal[1]
    couts: ConfigCouts


def charger_config_entrainement(chemin: str | Path | None = None) -> ConfigEntrainement:
    """Lit `entrainement.toml` (défaut : `<racine du projet>/config/entrainement.toml`)."""
    return charger_toml(
        chemin if chemin is not None else racine_projet() / "config" / NOM_ENTRAINEMENT,
        ConfigEntrainement,
    )
