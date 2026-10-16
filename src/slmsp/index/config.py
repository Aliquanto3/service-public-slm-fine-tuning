"""Configuration et disposition de l'Index local (AD-9, AD-22).

`config/index.toml` est toujours lu sous `<racine du projet>/config`, même quand
`--racine` désigne un autre dépôt : la configuration suit le code exécuté. L'Index vit sous
`<racine>/index/<AAAAMMJJ>/` (version = date du snapshot le plus récent des sources) avec
trois fichiers : `vectors.f16.npy`, `chunks.sqlite` et `MANIFEST.json`.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, StringConstraints, field_validator

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.core.schemas.config_modele import RevisionHf

NOM_VECTEURS: Final = "vectors.f16.npy"
NOM_CHUNKS: Final = "chunks.sqlite"
NOM_MANIFESTE: Final = "MANIFEST.json"
NOM_CONFIG: Final = "index.toml"

MOTIF_VERSION: Final = r"^\d{8}$"
"""Version d'un Index : `AAAAMMJJ` (date du snapshot)."""

_MOTIF_VERSION = re.compile(MOTIF_VERSION)

NomSource = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9.-]*$")]


class ColonnesSource(ModeleConfig):
    """Colonnes du parquet lues pour chaque champ de `chunks.sqlite`."""

    chunk_id: str = Field(min_length=1)
    doc_id: str = Field(min_length=1)
    titre: str = Field(min_length=1)
    url: str = Field(min_length=1)
    texte: str = Field(min_length=1)


class SourceIndex(ModeleConfig):
    """Source de l'Index : jeu MediaTech épinglé et date de son snapshot."""

    nom: NomSource
    jeu: NomSource
    revision: RevisionHf
    date_snapshot: date
    colonnes: ColonnesSource


class ConfigMesureVec(ModeleConfig):
    """Paramètres et seuils de la mesure H-VEC."""

    requetes: int = Field(gt=0)
    graine: int
    k: int = Field(gt=0)
    seuil_p95_ms: float = Field(gt=0)
    seuil_ram_mo: float = Field(gt=0)


class ConfigVerifEmbedding(ModeleConfig):
    """Paramètres et seuils de la mesure H-EMB (`slmsp index verifier-embedding`)."""

    echantillon: int = Field(default=200, gt=0)
    graine: int = 42
    k: int = Field(default=10, gt=0)
    seuil_cosinus_moyen: float = Field(default=0.99, gt=0, le=1)
    baisse_recall_max: float = Field(default=0.02, ge=0, le=1)
    """Baisse maximale tolérée du recall@k, en fraction (0,02 = 2 points)."""


class ConfigIndex(ModeleConfig):
    """Contenu de `config/index.toml`."""

    schema_version: Literal[1]
    modele_embedding: str = Field(min_length=1)
    colonne_vecteurs: str = Field(min_length=1)
    dimension: int = Field(gt=0)
    taille_bloc: int = Field(gt=0)
    k: int = Field(gt=0)
    seuil_pertinence: float = Field(ge=-1.0, le=1.0)
    taille_lot_lecture: int = Field(gt=0)
    sources: list[SourceIndex] = Field(min_length=1)
    mesure: ConfigMesureVec
    verification_embedding: ConfigVerifEmbedding = Field(default_factory=ConfigVerifEmbedding)

    @field_validator("sources")
    @classmethod
    def _noms_uniques(cls, valeur: list[SourceIndex]) -> list[SourceIndex]:
        noms = [source.nom for source in valeur]
        if len(noms) != len(set(noms)):
            raise ValueError("deux sources portent le même nom")
        return valeur

    def version(self) -> str:
        """Version de l'Index : date de snapshot la plus récente des sources, `AAAAMMJJ`."""
        return max(source.date_snapshot for source in self.sources).strftime("%Y%m%d")


def chemin_config_index() -> Path:
    """`<racine du projet>/config/index.toml`."""
    return racine_projet() / "config" / NOM_CONFIG


def charger_config_index(chemin: str | Path | None = None) -> ConfigIndex:
    """Lit et valide `config/index.toml` (ou `chemin`) ; lève `ConfigurationInvalide`."""
    return charger_toml(chemin if chemin is not None else chemin_config_index(), ConfigIndex)


def dossier_index(racine: str | Path | None = None) -> Path:
    """`<racine>/index` (racine du projet par défaut), en chemin absolu."""
    base = Path(racine) if racine is not None else racine_projet()
    return base.resolve() / "index"


def version_valide(version: object) -> bool:
    """Vrai si `version` est une chaîne `AAAAMMJJ`."""
    return isinstance(version, str) and _MOTIF_VERSION.fullmatch(version) is not None


__all__ = [
    "MOTIF_VERSION",
    "NOM_CHUNKS",
    "NOM_CONFIG",
    "NOM_MANIFESTE",
    "NOM_VECTEURS",
    "ColonnesSource",
    "ConfigIndex",
    "ConfigMesureVec",
    "ConfigVerifEmbedding",
    "SourceIndex",
    "charger_config_index",
    "chemin_config_index",
    "dossier_index",
    "version_valide",
]
