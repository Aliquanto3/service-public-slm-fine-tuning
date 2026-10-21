"""Mesure de chaque appel LLM et plafond de dépense (story 17.6, amendements 2 et 3).

- `MesureAppel` : ce qu'un client relève d'un appel (tokens, durée, premier token, coût),
  **sans** texte de demande ni de réponse, ni clé. `estime` : tokens estimés (caractères ÷ 2,5)
  faute d'usage renvoyé ; `interrompu` : flux coupé, erreur après le premier jeton ou arrêt.
- `ObservateurAppels` : reçoit une mesure par appel (branché dans `ClientOpenAI._appel` et
  dans le flux de `ClientLlama`) ; une erreur de l'observateur n'interrompt jamais l'appel.
- `PlafondPort` : réservation du coût pire cas avant chaque tentative HTTP, régularisation
  au coût mesuré (ou estimé) ensuite.
- `contexte_mesure` : échange et Tâche de l'appel en cours (variable de contexte posée par le
  pont dans le fil qui consomme le flux).
"""

from __future__ import annotations

import json
import logging
import math
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Final, Protocol

LOGGER: Final = logging.getLogger("slmsp.inference.mesures")
CARACTERES_PAR_TOKEN: Final = 2.5
"""Diviseur prudent de l'estimation (revue 17.6 : ÷ 2,5 plutôt que ÷ 3, plus de tokens comptés)."""
MAJORATION_ENTREE: Final = 1.25
"""Majoration de l'entrée estimée pour le pire cas (amendement 3)."""
TOKENS_PAR_UNITE: Final = 1_000_000
FOURNISSEUR_LOCAL: Final = "local"

_CONTEXTE: ContextVar[tuple[str | None, str | None]] = ContextVar(
    "slmsp_contexte_mesure", default=(None, None)
)


@contextmanager
def contexte_mesure(*, echange: str | None = None, tache: str | None = None) -> Iterator[None]:
    """Rattache les mesures des appels faits dans ce bloc à `echange` et `tache`."""
    jeton = _CONTEXTE.set((echange, tache))
    try:
        yield
    finally:
        _CONTEXTE.reset(jeton)


def contexte_courant() -> tuple[str | None, str | None]:
    """`(echange, tache)` posés par `contexte_mesure`, sinon `(None, None)`."""
    return _CONTEXTE.get()


def estimer_tokens(caracteres: int) -> int:
    """Estimation prudente : caractères ÷ 2,5, arrondi au-dessus."""
    return math.ceil(max(0, caracteres) / CARACTERES_PAR_TOKEN)


def caracteres_entree(corps: Mapping[str, Any]) -> int:
    """Taille de l'entrée d'une requête (messages et outils, en JSON)."""
    return len(
        json.dumps(
            {"messages": corps.get("messages") or [], "tools": corps.get("tools") or []},
            ensure_ascii=False,
        )
    )


@dataclass(frozen=True)
class Tarif:
    """Tarif d'un modèle en euros par million de tokens."""

    entree: float
    sortie: float

    def cout(self, tokens_entree: int, tokens_sortie: int) -> float:
        return (tokens_entree * self.entree + tokens_sortie * self.sortie) / TOKENS_PAR_UNITE

    def pire_cas(self, caracteres: int, max_tokens: int, tentatives: int) -> float:
        """Pire cas (amendement 3) : (entrée estimée × 1,25 au tarif d'entrée + `max_tokens`
        au tarif de sortie) × `tentatives` (1 + relances restantes)."""
        entree = math.ceil(estimer_tokens(caracteres) * MAJORATION_ENTREE)
        return self.cout(entree, max(0, max_tokens)) * max(1, tentatives)


@dataclass(frozen=True)
class MesureAppel:
    """Une ligne de mesure (voir le module). `cout_eur` `None` : tarif inconnu."""

    fournisseur: str
    hote: str | None
    modele: str
    tokens_entree: int
    tokens_sortie: int
    estime: bool
    interrompu: bool
    duree_ms: int
    premier_token_ms: int | None
    cout_eur: float | None
    motif: str | None = None
    echange: str | None = None
    tache: str | None = None

    @property
    def local(self) -> bool:
        return self.fournisseur == FOURNISSEUR_LOCAL


class ObservateurAppels(Protocol):
    def mesurer(self, mesure: MesureAppel) -> None: ...


class PlafondPort(Protocol):
    def reserver(self, hote: str, modele: str, montant: float) -> Any | None:
        """Réserve `montant` € : un jeton, ou `None` si le plafond serait dépassé."""
        ...

    def regulariser(self, jeton: Any, cout: float) -> None:
        """Remplace la réservation `jeton` par le coût `cout` €."""
        ...


def notifier(observateur: ObservateurAppels | None, mesure: MesureAppel) -> None:
    """Remet la mesure à l'observateur avec le contexte courant ; ne lève jamais."""
    if observateur is None:
        return
    echange, tache = contexte_courant()
    if mesure.echange is None and mesure.tache is None:
        mesure = MesureAppel(**{**mesure.__dict__, "echange": echange, "tache": tache})
    try:
        observateur.mesurer(mesure)
    except Exception as exc:
        LOGGER.error("mesure d'appel non enregistrée (%s)", type(exc).__name__)


def usage_tokens(usage: Mapping[str, Any] | None) -> tuple[int, int] | None:
    """`(prompt_tokens, completion_tokens)` de l'usage renvoyé, sinon `None`."""
    if not isinstance(usage, Mapping):
        return None
    entree, sortie = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if not all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in (entree, sortie)):
        return None
    return int(entree), int(sortie)  # type: ignore[arg-type]


__all__ = [
    "FOURNISSEUR_LOCAL",
    "MesureAppel",
    "ObservateurAppels",
    "PlafondPort",
    "Tarif",
    "caracteres_entree",
    "contexte_courant",
    "contexte_mesure",
    "estimer_tokens",
    "notifier",
    "usage_tokens",
]
