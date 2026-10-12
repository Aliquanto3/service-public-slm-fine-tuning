"""Version figée de llama.cpp, `config/llamacpp.toml` (AD-6, AD-28).

Les binaires `cpu` et `cuda` (avec `cudart`) et les sources viennent du même tag ; chaque
archive et chaque binaire extrait est vérifié par son SHA-256.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema

ASSETS_REQUIS = ("cpu", "cuda", "cudart")


class Asset(SousSchema):
    """Archive publiée avec la version (`nom` dans la release, empreinte attendue)."""

    nom: str
    sha256: Sha256


class ConfigLlamacpp(SchemaBase):
    """Tag llama.cpp figé, archives de la release et empreintes des binaires extraits."""

    schema_version: Literal[1] = 1
    tag: Annotated[str, StringConstraints(pattern=r"^b\d+$")]
    depot: str = "ggml-org/llama.cpp"
    assets: dict[Literal["cpu", "cuda", "cudart"], Asset]
    sources: Asset
    binaires: dict[str, Sha256] = Field(default_factory=dict)
    """Chemin relatif d'un binaire extrait → SHA-256."""

    @field_validator("assets")
    @classmethod
    def _trois_assets(cls, valeur: dict[str, Asset]) -> dict[str, Asset]:
        if set(valeur) != set(ASSETS_REQUIS):
            raise ValueError(f"assets doit contenir exactement {', '.join(ASSETS_REQUIS)}")
        return valeur
