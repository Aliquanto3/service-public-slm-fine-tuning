"""Configuration d'un modèle candidat, `config/modeles/<slug>.toml` (AD-6, AD-28).

Ces valeurs servent à l'inférence (`llama-server`) comme à l'entraînement, et sont
archivées dans `run.json`. `chat_template_force` signale un chat template corrigé, exporté
sous `models/<slug>/chat_template.jinja` et passé explicitement au serveur.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints, model_validator

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema

RevisionHf = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
"""Révision Hugging Face figée : SHA de commit complet (40 hexadécimaux minuscules)."""


class FichierGguf(SousSchema):
    """Poids GGUF servis par `llama-server`."""

    depot: str
    fichier: str
    sha256: Sha256


class ConfigModele(SchemaBase):
    """Paramètres d'un modèle (AD-6) et de son téléchargement figé (AD-28)."""

    schema_version: Literal[1] = 1
    depot_hf: str
    revision: RevisionHf
    fichiers: list[str]
    gguf: FichierGguf
    contexte: int = Field(gt=0)
    cache_kv: Literal["f16", "q8_0", "q4_0"] = "f16"
    threads: int | None = Field(default=None, gt=0)
    reasoning: Literal["off", "on", "auto"] = "off"
    chat_template_kwargs: dict[str, Any] = Field(default_factory=dict)
    protocole_outils: Literal["natif", "json-generique"]
    exclure_vision: bool = False
    chat_template_force: bool = False
    embedding: bool = False
    pooling: Literal["cls", "mean", "last"] | None = None

    @model_validator(mode="after")
    def _pooling_si_embedding(self) -> ConfigModele:
        if (self.pooling is not None) != self.embedding:
            raise ValueError("pooling est requis pour un modèle d'embedding, et seulement pour lui")
        return self
