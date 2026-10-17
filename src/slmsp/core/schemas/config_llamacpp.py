"""Version figée de llama.cpp, `config/llamacpp.toml` (AD-6, AD-28).

Les binaires `cpu` et `cuda` (avec `cudart`) et les sources viennent du même tag ; chaque
archive et chaque binaire extrait est vérifié par son SHA-256.

Version commune : `config/llamacpp.toml`. Un modèle peut en désigner une autre par le champ
`llamacpp` de sa configuration (décision d'Anaël du 2026-10-17, Bonsai) : elle est décrite
par `config/llamacpp/<tag>.toml`, au même schéma, et rangée sous `vendor/llama.cpp/<tag>/`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, StringConstraints, field_validator

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema

ASSETS_REQUIS = ("cpu", "cuda", "cudart")

MOTIF_TAG: Final = r"^(b\d+|[a-z][a-z0-9]*-b\d+-[0-9a-f]{7,40})$"
"""Tag amont (`b11429`) ou de fork (`prism-b10777-e3de715`) : sert aussi de nom de dossier."""

TagLlamacpp = Annotated[str, StringConstraints(pattern=MOTIF_TAG)]


def fichier_config(dossier_config: Path, version: str | None = None) -> Path:
    """`<config>/llamacpp.toml` (version commune) ou `<config>/llamacpp/<version>.toml`."""
    if version is None:
        return dossier_config / "llamacpp.toml"
    return dossier_config / "llamacpp" / f"{version}.toml"


class Asset(SousSchema):
    """Archive publiée avec la version (`nom` dans la release, empreinte attendue)."""

    nom: str
    sha256: Sha256


class ConfigLlamacpp(SchemaBase):
    """Tag llama.cpp figé, archives de la release et empreintes des binaires extraits."""

    schema_version: Literal[1] = 1
    tag: TagLlamacpp
    depot: str = "ggml-org/llama.cpp"
    assets: dict[Literal["cpu", "cuda", "cudart"], Asset]
    sources: Asset | None = None
    """Archive des sources (conversion HF → GGUF) ; facultative pour une version réservée."""
    binaires: dict[str, Sha256] = Field(default_factory=dict)
    """Chemin relatif d'un binaire extrait → SHA-256."""

    @field_validator("assets")
    @classmethod
    def _trois_assets(cls, valeur: dict[str, Asset]) -> dict[str, Asset]:
        if set(valeur) != set(ASSETS_REQUIS):
            raise ValueError(f"assets doit contenir exactement {', '.join(ASSETS_REQUIS)}")
        return valeur
