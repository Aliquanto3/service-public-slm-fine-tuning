"""Configuration d'entraînement : `config/entrainement.toml` (AD-18).

Créé par la story 10.3 (`ConfigCouts`, protocole de mesure du coût d'un Run) ; la story
10.4 le complète (`RunConfig`). Le fichier est lu sous `<racine du projet>/config`, jamais
sous `--racine` : la configuration suit le code exécuté.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet


class ConfigCouts(ModeleConfig):
    """Protocole de mesure du coût d'un Run (`[couts]`)."""

    pas_chauffe: int = Field(ge=0)
    """Pas d'optimisation écartés avant de mesurer le débit."""
    periode_echantillonnage: float = Field(gt=0)
    """Secondes entre deux relevés NVML."""
    indice_gpu: int = Field(ge=0)


class ConfigEntrainement(ModeleConfig):
    """Contenu de `config/entrainement.toml`."""

    couts: ConfigCouts


def charger_config_couts(dossier: str | Path | None = None) -> ConfigCouts:
    """Section `[couts]` de `<dossier>/entrainement.toml` (défaut : `<racine>/config`)."""
    base = Path(dossier) if dossier is not None else racine_projet() / "config"
    return charger_toml(base / "entrainement.toml", ConfigEntrainement).couts
