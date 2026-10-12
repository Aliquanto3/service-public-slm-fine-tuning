"""Schémas d'artefacts partagés (AD-25) : un module par schéma, sans réexport.

Chaque schéma de fichier dérive de `SchemaBase` (clés inconnues refusées, `schema_version`).
Les sous-modèles imbriqués dérivent de `SousSchema` (clés inconnues refusées, sans version :
la version est portée par le schéma englobant). Importer le schéma voulu par son module,
par exemple `from slmsp.core.schemas.run import RunManifest`.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
"""Empreinte SHA-256 en hexadécimal minuscule."""


class SchemaBase(BaseModel):
    """Base de tout schéma de fichier : clés inconnues refusées, version du schéma."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int


class SousSchema(BaseModel):
    """Base des sous-modèles imbriqués dans un schéma : clés inconnues refusées."""

    model_config = ConfigDict(extra="forbid")
