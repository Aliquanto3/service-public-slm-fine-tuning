"""Registre des moteurs de benchmark : nom -> module, chargé paresseusement (AD-16).

Un moteur est un module exposant `executer(config, contexte) -> SortieMoteur`. Les moteurs
réels (`lm_eval`, `traduction`, `bfcl`) importent des outils lourds (extra `bench`) : ils ne
sont importés qu'au moment de l'exécution du benchmark. Un test enregistre un moteur factice
par `enregistrer_moteur`.
"""

from __future__ import annotations

import importlib
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from slmsp.core.config import env_sous_processus
from slmsp.core.erreurs import ConfigurationInvalide

if TYPE_CHECKING:
    from slmsp.core.artefacts import Run
    from slmsp.core.schemas.bench import Variante

MOTEURS: dict[str, str] = {
    "lm_eval": "slmsp.benchmarks.moteurs.lm_eval",
    "traduction": "slmsp.benchmarks.moteurs.traduction",
    "bfcl": "slmsp.benchmarks.moteurs.bfcl",
}
"""Moteurs livrés : nom -> module (stories 6.2 et 6.3)."""

ENV_HORS_LIGNE = {"HF_HUB_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"}
ENV_UTF8 = {"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
"""Sans cela, `lm_eval` plante sur Windows en affichant son tableau (flèches ↑↓, cp1252 sous
tube) APRÈS avoir écrit ses résultats : code non nul, donc benchmark en erreur à tort."""

_ENREGISTRES: dict[str, Callable[..., Any]] = {}


@dataclass(frozen=True)
class ContexteBench:
    """Ce que l'orchestrateur donne à un moteur."""

    modele_ref: str
    variante: Variante
    run: Run
    racine: Path
    variante_llamacpp: str = "cpu"

    @property
    def dossier_jeux(self) -> Path:
        """`<racine>/data/raw/benchmarks` (rempli par `slmsp fetch benchmarks`)."""
        return self.racine / "data" / "raw" / "benchmarks"


@dataclass
class SortieMoteur:
    """Ce qu'un moteur rend ; l'orchestrateur en fait un `ResultatBench`."""

    scores: Mapping[str, float | int | None] = field(default_factory=dict)
    outil: str | None = None
    outil_version: str | None = None
    jeu_version: str | None = None
    seed: int | None = None
    batch_size: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    saute: str | None = None
    """Motif si le benchmark ne s'applique pas à ce modèle ou cette variante."""


def enregistrer_moteur(nom: str, executer: Callable[..., SortieMoteur]) -> None:
    """Enregistre un moteur en mémoire (tests, extensions)."""
    _ENREGISTRES[nom] = executer


def moteur_connu(nom: str) -> bool:
    return nom in MOTEURS or nom in _ENREGISTRES


def charger_moteur(nom: str) -> Callable[..., SortieMoteur]:
    """Fonction `executer` du moteur `nom` ; importe son module à la première demande."""
    if nom in _ENREGISTRES:
        return _ENREGISTRES[nom]
    if nom not in MOTEURS:
        connus = ", ".join(sorted({*MOTEURS, *_ENREGISTRES}))
        raise ConfigurationInvalide(f"moteur inconnu : {nom} (connus : {connus})")
    module = MOTEURS[nom]
    try:
        return importlib.import_module(module).executer
    except ModuleNotFoundError as exc:
        if exc.name == module:
            raise ConfigurationInvalide(f"moteur {nom} pas encore livré ({module} absent)") from exc
        raise ConfigurationInvalide(
            f"moteur {nom} indisponible : module manquant {exc.name} ; installer l'extra uv `bench`"
        ) from exc


def env_outil(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Environnement d'un outil tiers : `env_sous_processus()`, HF hors ligne, sortie en UTF-8.

    `HF_HOME` y est imposé à `<models>/.cache-hf` : c'est là que `lm_eval` lit ses jeux."""
    return {**env_sous_processus(base), **ENV_HORS_LIGNE, **ENV_UTF8}


def lancer_outil(
    commande: Sequence[str],
    *,
    cwd: str | Path | None = None,
    timeout: float | None = None,
    env_supplementaire: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Lance un outil tiers (sans shell) avec `env_outil()` ; ne lève pas sur code non nul.

    `env_supplementaire` s'ajoute à l'environnement (valeurs non secrètes seulement).
    """
    return subprocess.run(
        list(commande),
        cwd=cwd,
        env={**env_outil(), **(env_supplementaire or {})},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


__all__ = [
    "MOTEURS",
    "ContexteBench",
    "SortieMoteur",
    "charger_moteur",
    "enregistrer_moteur",
    "env_outil",
    "lancer_outil",
    "moteur_connu",
]
