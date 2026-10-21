"""Recherche dans l'Index local pour le Harnais (AD-9).

La requête est vectorisée par l'`EmbedderPort`, puis le `VectorStore` renvoie les `k`
passages les plus proches. Seuls les passages de score `>= seuil` sont gardés : le seuil
de pertinence est appliqué ici, pas par l'Index. `k` et le seuil viennent de
`config/index.toml` par `slmsp.index.config` (source unique) ; `depuis_config` les lit.
Le pipeline `data` (story 9.4) réutilise cette classe.
"""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

from slmsp.core.erreurs import SlmspError
from slmsp.index.config import ConfigIndex, charger_config_index

if TYPE_CHECKING:
    from slmsp.core.ports import EmbedderPort, Passage, VectorStore


LOGGER = logging.getLogger("slmsp.harness.recherche_index")


def _textes_tronques(embedder: object) -> int:
    """Compteur `textes_tronques` de l'embedder s'il en a un (entier), sinon 0."""
    valeur = getattr(embedder, "textes_tronques", 0)
    return valeur if isinstance(valeur, int) and not isinstance(valeur, bool) else 0


class RequeteVide(SlmspError):
    """Requête de recherche vide."""


class RechercheIndex:
    """Recherche des passages pertinents de l'Index local."""

    def __init__(
        self, embedder: EmbedderPort, vector_store: VectorStore, k: int, seuil: float
    ) -> None:
        if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
            raise ValueError(f"k doit être un entier > 0 (reçu {k!r})")
        if not math.isfinite(seuil):
            raise ValueError(f"seuil doit être un nombre fini (reçu {seuil!r})")
        self.embedder = embedder
        self.vector_store = vector_store
        self.k = k
        self.seuil = float(seuil)
        self.requetes_tronquees = 0
        """Requêtes tronquées par l'embedder (contexte) depuis la création."""

    def rechercher(self, requete: str, k: int | None = None) -> list[Passage]:
        """Passages de score `>= seuil` parmi les `k` plus proches, par score décroissant.

        `k` remplace pour cet appel celui de l'instance (Q, story 16.2).
        """
        if k is not None and (isinstance(k, bool) or not isinstance(k, int) or k <= 0):
            raise ValueError(f"k doit être un entier > 0 (reçu {k!r})")
        if not requete.strip():
            raise RequeteVide("requête de recherche vide")
        # La troncature (à micro-lot - 16 tokens) est faite par l'embedder, qui la compte dans
        # `textes_tronques` et la journalise ; on relève ici l'écart, sans dupliquer la logique.
        avant = _textes_tronques(self.embedder)
        matrice = self.embedder.vectoriser([requete])
        if _textes_tronques(self.embedder) > avant:
            self.requetes_tronquees += 1
            LOGGER.warning(
                "recherche : requête de %d caractères tronquée par l'embedder", len(requete)
            )
        passages = self.vector_store.rechercher(matrice[0], self.k if k is None else k)
        return [passage for passage in passages if passage.score >= self.seuil]


def depuis_config(
    embedder: EmbedderPort, vector_store: VectorStore, config: ConfigIndex | None = None
) -> RechercheIndex:
    """`RechercheIndex` avec `k` et `seuil_pertinence` de `config/index.toml` (ou `config`)."""
    index = config if config is not None else charger_config_index()
    return RechercheIndex(embedder, vector_store, index.k, index.seuil_pertinence)


__all__ = ["RechercheIndex", "RequeteVide", "depuis_config"]
