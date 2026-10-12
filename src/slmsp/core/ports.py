"""Ports du Harnais et des adaptateurs (AD-1, AD-9, AD-14).

Les adaptateurs (inférence, index, MCP, passerelle réseau, Modes, journal) implémentent ces
protocoles et reçoivent leurs dépendances par injection : `net` reçoit un `ModePort`, il
n'importe jamais `harness`. Les protocoles sont vérifiables par `isinstance`
(`runtime_checkable` : présence des membres seulement).
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Protocol, runtime_checkable

from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray

Mode = Literal["connecte", "hors-ligne-detecte", "hors-ligne-force"]
"""Mode de l'Assistant (FR-10)."""


@dataclass(frozen=True)
class Passage:
    """Passage de l'Index local renvoyé par `VectorStore.rechercher` (AD-9)."""

    chunk_id: str
    doc_id: str
    source: str
    titre: str
    url: str
    texte: str
    date_snapshot: str | None
    score: float


@runtime_checkable
class LlmPort(Protocol):
    """Modèle de génération (llama-server en v1)."""

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Jeton | AppelOutil | AppelNonConforme | Fin]:
        """Génère en flux : jetons, appels d'outils (conformes ou non), puis `Fin`."""
        ...

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        """Nombre de tokens de l'entrée rendue par le chat template."""
        ...


@runtime_checkable
class EmbedderPort(Protocol):
    """Vectorisation des requêtes (BGE-M3 en v1), partagée par le Harnais et `data`."""

    @property
    def dimension(self) -> int: ...

    def vectoriser(self, textes: Sequence[str]) -> NDArray[np.float32]:
        """Matrice `(len(textes), dimension)` en float32, normalisée L2."""
        ...


@runtime_checkable
class VectorStore(Protocol):
    """Recherche dans l'Index local."""

    def rechercher(self, vecteur: NDArray[np.float32], k: int) -> list[Passage]:
        """Les `k` passages les plus proches, par score décroissant."""
        ...


@runtime_checkable
class ToolPort(Protocol):
    """Outils exposés au modèle (MCP data.gouv en v1)."""

    def lister_outils(self) -> list[dict[str, Any]]:
        """Schémas des outils au format `tools` OpenAI."""
        ...

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        """Appelle l'outil `nom` et renvoie son résultat."""
        ...


@runtime_checkable
class NetGate(Protocol):
    """Passerelle réseau unique (AD-4)."""

    def client(self, profil: str) -> Any:
        """Client HTTP gardé pour `profil`."""
        ...

    def verifier(
        self,
        profil: str,
        methode: str,
        url: str,
        *,
        outil: str | None = None,
        termes: Any = None,
    ) -> None:
        """Lève `HoteBloque` si la requête est refusée (profil, Liste blanche, Mode)."""
        ...


@runtime_checkable
class ModePort(Protocol):
    """Source du Mode courant (sonde ou Mode forcé)."""

    def mode_courant(self) -> Mode: ...


@runtime_checkable
class JournalRequetes(Protocol):
    """Journal des Requêtes sortantes (entrées `EntreeJournalRequetes`, story 1.4)."""

    def inscrire(self, entree: Any) -> None: ...

    def lister(self, limite: int | None = None) -> list[Any]: ...
