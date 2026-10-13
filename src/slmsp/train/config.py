"""Configuration de l'entraînement (AD-18), lue depuis `config/entrainement.toml`.

La story 10.3 crée ce module avec `ConfigCouts` (protocole de mesure du coût) ; la story
10.4 le complète (`RunConfig`, hyperparamètres). Les clés inconnues sont refusées.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from pydantic import Field

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet

NOM_ENTRAINEMENT: Final = "entrainement.toml"


class ConfigCouts(ModeleConfig):
    """Protocole de mesure du coût d'un Run (FR-33)."""

    pas_chauffe: int = Field(ge=0)
    periode_echantillonnage_ms: int = Field(gt=0)


class ConfigEntrainement(ModeleConfig):
    """Contenu de `config/entrainement.toml`."""

    schema_version: Literal[1]
    couts: ConfigCouts


def charger_config_entrainement(chemin: str | Path | None = None) -> ConfigEntrainement:
    """Charge et valide `config/entrainement.toml` (ou `chemin`)."""
    defaut = racine_projet() / "config" / NOM_ENTRAINEMENT
    return charger_toml(chemin if chemin is not None else defaut, ConfigEntrainement)
