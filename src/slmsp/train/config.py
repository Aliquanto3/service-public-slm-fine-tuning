"""Configuration de l'entraînement : `config/entrainement.toml` (AD-22).

Créé par la story 10.3 (`ConfigCouts`, protocole de mesure du coût) ; la story 10.4 le
complète (`RunConfig`).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet


class ConfigCouts(ModeleConfig):
    """Protocole de mesure du coût d'un Run (FR-33)."""

    pas_chauffe: int = Field(ge=0)
    periode_echantillonnage_ms: int = Field(ge=1)


class ConfigEntrainement(ModeleConfig):
    """Contenu de `config/entrainement.toml`."""

    couts: ConfigCouts


def chemin_config_entrainement() -> Path:
    return racine_projet() / "config" / "entrainement.toml"


def charger_config_entrainement(chemin: str | Path | None = None) -> ConfigEntrainement:
    return charger_toml(chemin or chemin_config_entrainement(), ConfigEntrainement)
