"""Budget de prompt des Tâches à passages (correctif F2).

Budget : `taille_contexte − sortie réservée`. `taille_contexte` est l'attribut optionnel du
`LlmPort` (`ClientLlama` le reçoit de `ServeurLlama.client()`) ; la sortie réservée est le
`max_tokens` de l'appel (`reserve_sortie`), que le service fixe par défaut à
`config.generation.max_tokens`. Les messages sont mesurés tels qu'ils sont envoyés (système,
historique, passages et entrée) par `LlmPort.compter_tokens` (`/apply-template` puis
`/tokenize` de llama-server) : aucune estimation.

`borner_passages` :

- sans `taille_contexte` (contexte inconnu), les passages sont rendus tels quels, sans mesure ;
- si tout tient, les passages sont rendus tels quels (une seule mesure) ;
- sinon, les passages les moins bien classés (en fin de liste, la recherche les rend par
  score décroissant) sont retirés un à un jusqu'à tenir ;
- en dernier recours, si aucun passage complet ne tient mais que le prompt sans passage
  tient, le premier passage est tronqué à une frontière de mot et suivi de `MARQUE_COUPE`
  (au plus `ESSAIS_TRONCATURE` mesures) ; à défaut, aucun passage n'est fourni ;
- si même le prompt sans passage dépasse le budget, `ContexteDepasse` est levée (le service
  émet `Erreur(contexte-depasse)`).
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Final

from slmsp.core.erreurs import ContexteDepasse
from slmsp.core.ports import Passage
from slmsp.harness.taches import ContexteTache

LOGGER: Final = logging.getLogger("slmsp.harness")

MARQUE_COUPE: Final = " […]"
"""Fin d'un passage tronqué pour tenir dans le contexte."""
ESSAIS_TRONCATURE: Final = 4
MARGE_TRONCATURE: Final = 0.9
"""Facteur de sécurité appliqué à la longueur estimée d'un passage tronqué."""

Construire = Callable[[Sequence[Passage]], Sequence[Mapping[str, Any]]]
"""Messages complets de l'appel pour une liste de passages."""


def reserve_sortie(ctx: ContexteTache) -> int:
    """`max_tokens` de l'appel, ou `config.generation.max_tokens` si l'appelant n'en fixe pas."""
    demande = ctx.options_llm.get("max_tokens")
    if isinstance(demande, int) and not isinstance(demande, bool) and demande > 0:
        return demande
    return ctx.config.generation.max_tokens


def budget_prompt(ctx: ContexteTache) -> int | None:
    """Tokens disponibles pour le prompt, ou `None` si le contexte du Modèle est inconnu."""
    taille = getattr(ctx.llm, "taille_contexte", None)
    if not isinstance(taille, int) or isinstance(taille, bool):
        return None
    return taille - reserve_sortie(ctx)


def borner_passages(
    ctx: ContexteTache, passages: Sequence[Passage], construire: Construire
) -> list[Passage]:
    """Passages retenus pour que les messages de `construire` tiennent dans le budget."""
    retenus = list(passages)
    budget = budget_prompt(ctx)
    if budget is None:
        return retenus

    def mesurer(liste: Sequence[Passage]) -> int:
        return ctx.llm.compter_tokens(construire(liste))

    tokens = mesurer(retenus)
    if tokens <= budget:
        return retenus
    while retenus and tokens > budget:
        retenus.pop()
        tokens = mesurer(retenus)
    if tokens > budget:
        raise ContexteDepasse(
            f"Tâche {ctx.tache.code} : le prompt sans passage fait {tokens} tokens, "
            f"au-delà du budget de {budget} (contexte moins {reserve_sortie(ctx)} réservés "
            "à la sortie)"
        )
    if not retenus and passages:
        coupe = _tronquer(passages[0], tokens, budget, mesurer)
        if coupe is not None:
            retenus = [coupe]
    LOGGER.info(
        "Tâche %s : %d passage(s) sur %d fourni(s) pour tenir dans le contexte (budget %d)",
        ctx.tache.code,
        len(retenus),
        len(passages),
        budget,
    )
    return retenus


def _tronquer(
    passage: Passage, sans: int, budget: int, mesurer: Callable[[Sequence[Passage]], int]
) -> Passage | None:
    """`passage` tronqué à une frontière de mot pour tenir dans `budget`, ou `None`.

    `sans` est la mesure du prompt sans passage. La longueur est réduite en proportion des
    tokens disponibles (avec `MARGE_TRONCATURE`), puis vérifiée par une mesure.
    """
    texte = passage.texte
    tokens = mesurer([passage])
    for _ in range(ESSAIS_TRONCATURE):
        exces = tokens - sans
        if exces <= 0:
            return None
        ratio = min(MARGE_TRONCATURE, MARGE_TRONCATURE * (budget - sans) / exces)
        coupe = texte[: int(len(texte) * ratio)].rsplit(" ", 1)[0].rstrip()
        if not coupe:
            return None
        texte = coupe
        candidat = dataclasses.replace(passage, texte=texte + MARQUE_COUPE)
        tokens = mesurer([candidat])
        if tokens <= budget:
            return candidat
    return None


__all__ = [
    "ESSAIS_TRONCATURE",
    "MARQUE_COUPE",
    "borner_passages",
    "budget_prompt",
    "reserve_sortie",
]
