"""Débit en génération et délai au premier token d'une Question (FR-26, NFR-2, NFR-3).

Le chronomètre part à l'appel de `repondre` : le délai au premier token comprend donc
l'embedding de la requête, la recherche dans l'Index et le traitement du prompt. Le débit
est (tokens - 1) divisé par la durée entre le premier jeton et la fin : N tokens ne
couvrent que N-1 intervalles.
Les tokens sont ceux de `Fin.usage["completion_tokens"]` s'il est fourni, sinon le nombre de
`Jeton` reçus (approximation consignée). `exiger_usage` (décodage spéculatif, dont les tokens
acceptés arrivent groupés) refuse cette approximation : `MesureEchouee` sans `completion_tokens`.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from statistics import median

import numpy as np

from slmsp.core.evenements import Erreur, Evenement, Fin, Jeton


class MesureEchouee(RuntimeError):
    """La génération a renvoyé une erreur ou aucun jeton."""


@dataclass(frozen=True)
class MesureQuestion:
    premier_token_s: float
    tokens: int
    duree_generation_s: float
    debit_tps: float | None
    tokens_estimes: bool
    prompt_tokens: int | None = None
    brouillon_proposes: int | None = None
    """`timings.draft_n` du serveur (décodage spéculatif), `None` s'il ne l'expose pas."""
    brouillon_acceptes: int | None = None
    """`timings.draft_n_accepted`, `None` s'il ne l'expose pas."""


def mesurer_question(
    evenements: Iterable[Evenement],
    horloge: Callable[[], float] = time.perf_counter,
    *,
    exiger_usage: bool = False,
) -> MesureQuestion:
    """Consomme le flux d'évènements d'une Question et en tire les temps."""
    debut = horloge()
    premier: float | None = None
    jetons = 0
    usage: int | None = None
    prompt: int | None = None
    proposes: int | None = None
    acceptes: int | None = None
    for evenement in evenements:
        if isinstance(evenement, Erreur):
            raise MesureEchouee(f"{evenement.code} : {evenement.message}")
        if isinstance(evenement, Jeton):
            if premier is None:
                premier = horloge()
            jetons += 1
        elif isinstance(evenement, Fin) and evenement.usage:
            valeur = evenement.usage.get("completion_tokens")
            usage = valeur if isinstance(valeur, int) and valeur > 0 else None
            brut = evenement.usage.get("prompt_tokens")
            prompt = brut if isinstance(brut, int) and brut > 0 else None
            draft, accepte = evenement.usage.get("draft_n"), evenement.usage.get("draft_n_accepted")
            if isinstance(draft, int) and isinstance(accepte, int):
                proposes, acceptes = draft, accepte
    fin = horloge()
    if premier is None:
        raise MesureEchouee("aucun jeton généré")
    if exiger_usage and usage is None:
        raise MesureEchouee(
            "usage.completion_tokens absent : débit non mesurable en décodage spéculatif "
            "(le nombre de morceaux reçus n'est pas un compte de tokens fiable)"
        )
    tokens = usage if usage is not None else jetons
    duree = fin - premier
    # Un seul token ou une durée nulle ne donne pas de débit.
    debit = (tokens - 1) / duree if tokens > 1 and duree > 0 else None
    return MesureQuestion(
        premier - debut, tokens, duree, debit, usage is None, prompt, proposes, acceptes
    )


def mediane_p95(valeurs: list[float]) -> tuple[float, float]:
    """Médiane et p95 (interpolation linéaire) ; `ValueError` si la liste est vide."""
    if not valeurs:
        raise ValueError("aucune valeur à résumer")
    return float(median(valeurs)), float(np.percentile(np.asarray(valeurs), 95))
