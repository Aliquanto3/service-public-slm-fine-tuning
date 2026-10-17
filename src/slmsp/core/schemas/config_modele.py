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


SourceGguf = Literal["officielle", "communautaire", "conversion"]
"""Origine du GGUF : dépôt de l'éditeur (ou de ggml-org), dépôt communautaire réputé, ou
conversion maison au tag llama.cpp `tag_conversion`."""


class FichierGguf(SousSchema):
    """Poids GGUF servis par `llama-server`.

    `revision` épingle le commit du dépôt `depot` ; absente, le GGUF est pris à la révision
    du modèle (même dépôt) ou à `main` résolu à la volée (autre dépôt).
    """

    depot: str
    fichier: str
    sha256: Sha256
    revision: RevisionHf | None = None
    source: SourceGguf | None = None
    tag_conversion: str | None = None

    @model_validator(mode="after")
    def _tag_si_conversion(self) -> FichierGguf:
        if (self.tag_conversion is not None) != (self.source == "conversion"):
            raise ValueError(
                'gguf.tag_conversion est requis pour source = "conversion", et seulement pour elle'
            )
        return self


PrecisionGguf = Literal["f16", "bf16"]
"""Précision réelle d'un GGUF non quantifié (BF16 quand l'éditeur ne publie pas de F16)."""


class FichierGgufF16(FichierGguf):
    """GGUF non quantifié du modèle de base (`[gguf_f16]`), variante `avant` du banc.

    `precision` est obligatoire : la clé de variante reste `f16`, mais la précision réelle
    (F16 ou BF16) est reportée dans les runs d'évaluation et les résultats du banc.
    """

    precision: PrecisionGguf


class ConfigModele(SchemaBase):
    """Paramètres d'un modèle (AD-6) et de son téléchargement figé (AD-28)."""

    schema_version: Literal[1] = 1
    depot_hf: str
    revision: RevisionHf
    fichiers: list[str]
    sha256_fichiers: dict[str, Sha256] = Field(default_factory=dict)
    """SHA-256 attendu de fichiers de `fichiers` (indispensable pour un fichier non LFS)."""
    gguf: FichierGguf
    gguf_f16: FichierGgufF16 | None = None
    """GGUF F16 (ou BF16 à défaut, voir `precision`) du modèle de base : variante `avant`."""
    contexte: int = Field(gt=0)
    cache_kv: Literal["f16", "q8_0", "q4_0"] = "f16"
    threads: int | None = Field(default=None, gt=0)
    reasoning: Literal["off", "on", "auto"] = "off"
    chat_template_kwargs: dict[str, Any] = Field(default_factory=dict)
    protocole_outils: Literal["natif", "json-generique", "balises-tool-call"]
    exclure_vision: bool = False
    chat_template_force: bool = False
    embedding: bool = False
    entrainable: bool = True
    """Faux pour un modèle évalué tel quel (poids ternaires, GGUF seul) : `train run` le refuse."""
    pooling: Literal["cls", "mean", "last"] | None = None

    @model_validator(mode="after")
    def _coherence(self) -> ConfigModele:
        inconnus = sorted(set(self.sha256_fichiers) - set(self.fichiers))
        if inconnus:
            raise ValueError(f"sha256_fichiers : fichiers absents de `fichiers` : {inconnus}")
        if (
            self.gguf.depot == self.depot_hf
            and self.gguf.revision is not None
            and self.gguf.revision != self.revision
        ):
            raise ValueError("gguf.revision diffère de revision pour le même dépôt")
        f16 = self.gguf_f16
        if (
            f16 is not None
            and f16.depot == self.depot_hf
            and f16.revision is not None
            and f16.revision != self.revision
        ):
            raise ValueError("gguf_f16.revision diffère de revision pour le même dépôt")
        return self

    def gguf_pour(self, quantification: str) -> FichierGguf | None:
        """GGUF de base de la quantification (`q4_k_m` : `gguf`, `f16` : `gguf_f16`)."""
        return self.gguf_f16 if quantification == "f16" else self.gguf

    def precision_gguf(self, quantification: str) -> str | None:
        """Précision réelle du GGUF de base (`q4_k_m`, `f16` ou `bf16`), None s'il manque."""
        if quantification != "f16":
            return quantification
        return self.gguf_f16.precision if self.gguf_f16 is not None else None

    @model_validator(mode="after")
    def _pooling_si_embedding(self) -> ConfigModele:
        if (self.pooling is not None) != self.embedding:
            raise ValueError("pooling est requis pour un modèle d'embedding, et seulement pour lui")
        return self
