"""Exceptions partagées par les deux adaptateurs de `ToolPort` (rejeu et direct, AD-10).

Une erreur de transport est identique en direct et en rejeu : le rejeu d'une interaction
portant `simulation = {type, statut?}` lève la classe de `PAR_TYPE_SIMULATION[type]`.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar, Final

from slmsp.core.erreurs import SlmspError


class ErreurTransportMcp(SlmspError):
    """Échec de transport d'un appel MCP (déclenche le repli sur l'Index local)."""

    type_simulation: ClassVar[str]


class DelaiDepasse(ErreurTransportMcp):
    """L'appel MCP a dépassé son délai."""

    type_simulation = "delai_depasse"


class ErreurHttp(ErreurTransportMcp):
    """Le serveur MCP a répondu par un statut HTTP d'erreur."""

    type_simulation = "erreur_http"

    def __init__(self, message: str, *, statut: int | None = None):
        super().__init__(message)
        self.statut = statut


class Injoignable(ErreurTransportMcp):
    """Le serveur MCP est injoignable (connexion impossible)."""

    type_simulation = "injoignable"


PAR_TYPE_SIMULATION: Final[Mapping[str, type[ErreurTransportMcp]]] = MappingProxyType(
    {classe.type_simulation: classe for classe in (DelaiDepasse, ErreurHttp, Injoignable)}
)
"""Type de simulation d'une cassette → exception levée au rejeu."""


class CassetteInvalide(SlmspError):
    """Cassette absente, illisible ou non conforme au format (le message ne cite aucune valeur)."""
