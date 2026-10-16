"""`config/mesures.toml` : protocole de mesure FR-26 (questions, répétitions, seuils NFR)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet


class SeuilsNfr(ModeleConfig):
    """Seuils des exigences non fonctionnelles (Go = 1024³ octets)."""

    ram_max_go: float = Field(gt=0)
    ram_cible_go: float = Field(gt=0)
    debit_min_tps: float = Field(gt=0)
    premier_token_max_s: float = Field(gt=0)
    taille_max_go: float = Field(gt=0)


class ConfigMesures(ModeleConfig):
    schema_version: Literal[1]
    questions: list[str] = Field(min_length=1)
    repetitions: int = Field(gt=0)
    echauffement: int = Field(ge=0)
    plafond_threads: int = Field(gt=0)
    periode_ms: int = Field(gt=0)
    seuils: SeuilsNfr


def charger_config_mesures(chemin: str | Path | None = None) -> ConfigMesures:
    """`config/mesures.toml` (lève `ConfigurationInvalide`)."""
    return charger_toml(chemin or racine_projet() / "config" / "mesures.toml", ConfigMesures)
