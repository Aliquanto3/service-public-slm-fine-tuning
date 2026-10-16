"""Schémas des Benchmarks (AD-16, AD-25) : jeu épinglé et `ResultatBench`.

`JeuBench` décrit un jeu de données d'un benchmark (dépôt Hugging Face, révision figée,
fichiers attendus) ; `slmsp fetch benchmarks` le télécharge sous `data/raw/benchmarks/`.
`ResultatBench` est le contenu de `runs/bench/<run_id>/<benchmark>--<variante>.json`.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints, field_validator

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema
from slmsp.core.schemas.config_modele import RevisionHf
from slmsp.core.schemas.run import MOTIF_RUN_ID, ModeleRef

Variante = Literal["avant", "apres"]
"""Poids évalués : `avant` quantification (HF ou GGUF f16), `apres` (GGUF q4_k_m)."""

StatutBench = Literal["ok", "erreur", "saute"]


class FichierJeu(SousSchema):
    """Fichier d'un jeu : chemin dans le dépôt, SHA-256 et taille attendus."""

    chemin: str
    sha256: Sha256
    taille: int = Field(ge=0)

    @field_validator("chemin")
    @classmethod
    def _chemin(cls, valeur: str) -> str:
        parties = valeur.split("/")
        if (
            not valeur
            or "\\" in valeur
            or ":" in valeur
            or any(partie in ("", ".", "..") for partie in parties)
        ):
            raise ValueError(f"chemin de dépôt invalide : {valeur!r}")
        return valeur


class JeuBench(SousSchema):
    """Jeu de données d'un benchmark, épinglé par commit.

    Sans `revision` ou sans `fichiers`, le jeu n'est pas encore épinglé : `fetch benchmarks`
    le saute et le consigne (`non-epingle`).
    """

    nom: Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9._-]*$")]
    depot: Annotated[
        str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")
    ]
    revision: RevisionHf | None = None
    acces: Literal["libre", "conditionnel"] = "libre"
    licence: str | None = None
    fichiers: list[FichierJeu] = Field(default_factory=list)


class ConfigurationExecution(SousSchema):
    """Réglages du benchmark au moment du run."""

    fewshot: int = Field(ge=0)
    limite: int | None = None
    seed: int | None = None
    """Graine passée à l'outil (`None` : l'outil n'en prend pas)."""
    batch_size: str | None = None
    """Taille de lot effective (`auto` : choisie par l'outil selon la mémoire)."""
    options: dict[str, Any] = Field(default_factory=dict)


class ResultatBench(SchemaBase):
    """Un benchmark exécuté sur une variante (avant ou après quantification)."""

    schema_version: Literal[1] = 1
    run_id: Annotated[str, StringConstraints(pattern=MOTIF_RUN_ID)]
    benchmark: str
    moteur: str
    tache: str
    modele_ref: ModeleRef
    variante: Variante
    cible: Literal["hf", "gguf"]
    statut: StatutBench
    motif: str | None = None
    """Cause de l'erreur ou du saut."""
    scores: dict[str, float | int | None] = Field(default_factory=dict)
    jeu_version: str | None = None
    outil: str | None = None
    outil_version: str | None = None
    configuration: ConfigurationExecution
    duree_s: float = Field(ge=0)
    details: dict[str, Any] = Field(default_factory=dict)
