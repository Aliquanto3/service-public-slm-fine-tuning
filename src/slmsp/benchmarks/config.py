"""Configuration déclarative des benchmarks : un fichier `config/benchmarks/<nom>.toml` chacun.

Ajouter un benchmark dont le moteur existe ne demande aucune modification de code (FR-28).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import Field, StringConstraints, model_validator

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.bench import JeuBench, Variante

Cible = Literal["hf", "gguf"]
Quantification = Literal["avant", "apres", "les-deux"]


class BenchmarkConfig(ModeleConfig):
    """Contenu d'un fichier `config/benchmarks/<nom>.toml`."""

    nom: Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_.-]*$")]
    description: str = ""
    moteur: Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]*$")]
    tache: Annotated[str, StringConstraints(min_length=1)]
    fewshot: int = Field(default=0, ge=0)
    limite: int | None = Field(default=None, gt=0)
    cible: Cible
    quantification: Quantification
    socle: bool = False
    """Fait partie du socle (`bench run --socle`)."""
    options: dict[str, Any] = Field(default_factory=dict)
    """Réglages propres au moteur (paires de langues, sous-échantillon…)."""
    jeux: list[JeuBench] = Field(default_factory=list)

    @model_validator(mode="after")
    def _hf_avant_seulement(self) -> Self:
        if self.cible == "hf" and self.quantification != "avant":
            raise ValueError("la cible hf (poids HF) ne vaut qu'avant quantification")
        return self

    def variantes(self) -> list[Variante]:
        """Variantes à exécuter, `avant` d'abord."""
        if self.quantification == "les-deux":
            return ["avant", "apres"]
        return ["avant"] if self.quantification == "avant" else ["apres"]


def dossier_benchmarks() -> Path:
    """`<racine du projet>/config/benchmarks`."""
    return racine_projet() / "config" / "benchmarks"


def charger_benchmarks(dossier: str | Path | None = None) -> dict[str, BenchmarkConfig]:
    """Benchmarks de `<dossier>/*.toml`, triés par nom ; le nom est celui du fichier."""
    base = Path(dossier) if dossier is not None else dossier_benchmarks()
    if not base.is_dir():
        raise ConfigurationInvalide(f"dossier des benchmarks introuvable : {base}")
    configs: dict[str, BenchmarkConfig] = {}
    for chemin in sorted(base.glob("*.toml")):
        config = charger_toml(chemin, BenchmarkConfig)
        if config.nom != chemin.stem:
            raise ConfigurationInvalide(
                f"{chemin} : nom « {config.nom} » différent du nom du fichier « {chemin.stem} »"
            )
        configs[config.nom] = config
    return configs


__all__ = ["BenchmarkConfig", "charger_benchmarks", "dossier_benchmarks"]
