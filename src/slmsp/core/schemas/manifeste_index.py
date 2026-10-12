"""Manifeste de l'Index local `index/<AAAAMMJJ>/MANIFEST.json` (AD-9, AD-25).

Écrit une seule fois par `slmsp index build`, en JSON canonique suivi d'un LF, par création
exclusive. `fichiers` porte le SHA-256 de `vectors.f16.npy` et de `chunks.sqlite` ; chaque
source porte le SHA-256 des parquet lus. La date du snapshot (`AAAA-MM-JJ`) est lisible par
`slmsp index info`.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, Field, StringConstraints, model_validator

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema

Version = Annotated[str, StringConstraints(pattern=r"^\d{8}$")]
"""Version d'un Index : `AAAAMMJJ`."""


class SourceManifeste(SousSchema):
    """Une source de l'Index : jeu MediaTech épinglé, comptes et parquet lus."""

    nom: str = Field(min_length=1)
    jeu: str = Field(min_length=1)
    revision: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
    date_snapshot: date
    nb_chunks: int = Field(ge=0)
    nb_ecartes: int = Field(ge=0)
    """Lignes écartées : vecteur nul, illisible, de mauvaise dimension, de norme nulle ou non
    finie."""
    parquet: dict[str, Sha256]
    """Nom du fichier parquet lu -> SHA-256."""


class ManifesteIndex(SchemaBase):
    """Contenu de `index/<version>/MANIFEST.json`."""

    schema_version: Literal[1] = 1
    version: Version
    date_snapshot: date
    cree_le: AwareDatetime
    modele_embedding: str = Field(min_length=1)
    colonne_vecteurs: str = Field(min_length=1)
    dimension: int = Field(gt=0)
    dtype: Literal["float16"] = "float16"
    nb_chunks: int = Field(gt=0)
    sources: list[SourceManifeste] = Field(min_length=1)
    fichiers: dict[str, Sha256]
    """Nom du fichier de l'Index -> SHA-256."""

    @model_validator(mode="after")
    def _coherence(self) -> Self:
        if self.version != self.date_snapshot.strftime("%Y%m%d"):
            raise ValueError("version différente de la date du snapshot")
        if sum(source.nb_chunks for source in self.sources) != self.nb_chunks:
            raise ValueError("nb_chunks différent de la somme des chunks par source")
        noms = [source.nom for source in self.sources]
        if len(noms) != len(set(noms)):
            raise ValueError("deux sources portent le même nom")
        return self

    def chunks_par_source(self) -> dict[str, int]:
        """Nom de chaque source -> nombre de chunks indexés, dans l'ordre des rangs."""
        return {source.nom: source.nb_chunks for source in self.sources}
