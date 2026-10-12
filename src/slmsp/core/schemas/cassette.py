"""Cassette MCP : une session JSON-RPC par fichier, format unique (AD-10).

Format du calibrage (`server`, `recorded_at`, `initialize`, `interactions[{request,
response}]`) plus `schema_version` et `tools_list_sha256`. Une interaction peut porter
`simulation` (panne simulée), avec alors `response` nul. `initialize` peut être nul pour une
cassette de panne écrite sans réseau.
"""

from __future__ import annotations

from typing import Any, Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema

TypeSimulation = Literal["delai_depasse", "erreur_http", "injoignable"]
"""Pannes simulables ; chacune correspond à une exception de `slmsp.mcp.erreurs`."""


class Simulation(SousSchema):
    """Panne simulée à la place d'une réponse ; `statut` seulement pour `erreur_http`."""

    type: TypeSimulation
    statut: int | None = Field(default=None, ge=100, le=599)

    @model_validator(mode="after")
    def _statut_http_seulement(self) -> Self:
        if self.statut is not None and self.type != "erreur_http":
            raise ValueError("`statut` n'est permis que pour une simulation `erreur_http`")
        return self


class Interaction(SousSchema):
    """Une requête JSON-RPC et sa réponse, ou la panne simulée qui la remplace."""

    request: dict[str, Any]
    response: dict[str, Any] | None
    simulation: Simulation | None = None

    @model_validator(mode="after")
    def _reponse_ou_simulation(self) -> Self:
        if self.simulation is None and self.response is None:
            raise ValueError("une interaction porte une `response` ou une `simulation`")
        if self.simulation is not None and self.response is not None:
            raise ValueError("une interaction simulée a une `response` nulle")
        return self


class Cassette(SchemaBase):
    """Contenu d'un fichier de cassette MCP (calibrage, Jeu d'évaluation, données)."""

    schema_version: Literal[1]
    server: str
    recorded_at: AwareDatetime
    initialize: dict[str, Any] | None
    tools_list_sha256: Sha256
    interactions: list[Interaction]
