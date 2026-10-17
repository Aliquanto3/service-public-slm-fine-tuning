"""Budget de prompt des Tâches (correctif F2).

Budget : `taille_contexte − sortie réservée`. `taille_contexte` est l'attribut optionnel du
`LlmPort` (`ClientLlama` le reçoit de `ServeurLlama.client()`) ; la sortie réservée est le
`max_tokens` de l'appel (`reserve_sortie`), que le service fixe par défaut
(`config.generation`). Une sortie réservée qui laisse moins de `BUDGET_MIN` tokens au prompt
lève `ContexteDepasse` avec un message explicite. Les messages sont mesurés tels qu'ils sont
envoyés (système, historique, passages, entrée et, en Mode connecté, schéma `tools` et
résultats d'outils) par `LlmPort.compter_tokens` (`/apply-template` puis `/tokenize` de
llama-server) : aucune estimation.

`borner_passages` :

- sans `taille_contexte` (contexte inconnu), les passages sont rendus tels quels, sans mesure ;
- si tout tient, les passages sont rendus tels quels (une seule mesure) ;
- sinon, les passages les moins bien classés (en fin de liste, la recherche les rend par
  score décroissant) sont retirés un à un jusqu'à tenir : une mesure par retrait. Pour
  k = 5 passages dont 1 ou 2 à retirer (cas attendu à contexte 2048), c'est 2 ou 3 mesures,
  pas plus qu'une dichotomie (3 ou 4) ; chaque mesure est locale (quelques ms) ;
- en dernier recours, si aucun passage complet ne tient mais que le prompt sans passage
  tient, le premier passage est tronqué à une frontière de mot et suivi de `MARQUE_COUPE`
  (au plus `ESSAIS_TRONCATURE` mesures) ; à défaut, aucun passage n'est fourni ;
- si même le prompt sans passage dépasse le budget, `ContexteDepasse` est levée (le service
  émet `Erreur(contexte-depasse)`).

`borner_resultats` borne de même les résultats d'outils d'un tour de la Recherche de
données avant le tour suivant : chacun est tronqué en proportion, puis remplacé par
`MARQUE_COUPE` si cela ne suffit pas ; `ContexteDepasse` si même alors le prompt dépasse.

Repli (comportement d'avant F2) : si la mesure échoue (`/apply-template` ou `/tokenize` en
erreur), les messages partent sans budget, avec un avertissement journalisé (sans le message
de l'exception, qui pourrait citer le prompt) ; un vrai dépassement sera alors refusé par
le serveur (`ContexteServeurDepasse`).

Les mesures (deux requêtes locales chacune) précèdent la génération : elles comptent dans le
délai au premier token, mesuré depuis l'appel au service.
"""

from __future__ import annotations

import dataclasses
import logging
import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Final

from slmsp.core.erreurs import ContexteDepasse
from slmsp.core.ports import Passage
from slmsp.harness.taches import ContexteTache

LOGGER: Final = logging.getLogger("slmsp.harness")

MARQUE_COUPE: Final = " […]"
"""Fin d'un passage ou d'un résultat d'outil tronqué pour tenir dans le contexte."""
ESSAIS_TRONCATURE: Final = 4
MARGE_TRONCATURE: Final = 0.9
"""Facteur de sécurité appliqué à la longueur estimée d'un texte tronqué."""
BUDGET_MIN: Final = 64
"""Tokens minimaux laissés au prompt par la sortie réservée (en deçà : `ContexteDepasse`)."""

Construire = Callable[[Sequence[Passage]], Sequence[Mapping[str, Any]]]
"""Messages complets de l'appel pour une liste de passages."""
ConstruireResultats = Callable[[Sequence[str]], Sequence[Mapping[str, Any]]]
"""Messages complets de l'appel pour une liste de contenus de résultats d'outils."""


def reserve_sortie(ctx: ContexteTache) -> int:
    """`max_tokens` de l'appel, ou `config.generation.max_tokens` si l'appelant n'en fixe pas."""
    demande = ctx.options_llm.get("max_tokens")
    if isinstance(demande, int) and not isinstance(demande, bool) and demande > 0:
        return demande
    return ctx.config.generation.max_tokens


def _taille(ctx: ContexteTache) -> int | None:
    taille = getattr(ctx.llm, "taille_contexte", None)
    if not isinstance(taille, int) or isinstance(taille, bool):
        return None
    return taille


def budget_prompt(ctx: ContexteTache) -> int | None:
    """Tokens disponibles pour le prompt, ou `None` si le contexte du Modèle est inconnu.

    Lève `ContexteDepasse` si la sortie réservée ne laisse pas `BUDGET_MIN` tokens au prompt.
    """
    taille = _taille(ctx)
    if taille is None:
        return None
    reserve = reserve_sortie(ctx)
    budget = taille - reserve
    if budget < BUDGET_MIN:
        raise ContexteDepasse(
            f"Tâche {ctx.tache.code} : max_tokens {reserve} laisse {budget} tokens au prompt "
            f"sur un contexte de {taille} (minimum {BUDGET_MIN})"
        )
    return budget


def _sans_budget(ctx: ContexteTache, exc: Exception) -> None:
    LOGGER.warning(
        "Tâche %s : mesure du prompt impossible (%s) : envoi sans budget de prompt",
        ctx.tache.code,
        type(exc).__name__,
    )


def borner_passages(
    ctx: ContexteTache, passages: Sequence[Passage], construire: Construire
) -> list[Passage]:
    """Passages retenus pour que les messages de `construire` tiennent dans le budget."""
    candidats = list(passages)
    budget = budget_prompt(ctx)
    if budget is None:
        return candidats
    try:
        retenus = _borner(ctx, candidats, construire, budget)
    except ContexteDepasse:
        raise
    except Exception as exc:  # repli d'avant F2 : la mesure n'est qu'un garde-fou
        _sans_budget(ctx, exc)
        return candidats
    if len(retenus) != len(candidats) or (retenus and retenus[0] is not candidats[0]):
        LOGGER.info(
            "Tâche %s : %d passage(s) sur %d fourni(s) pour tenir dans le contexte (budget %d)",
            ctx.tache.code,
            len(retenus),
            len(candidats),
            budget,
        )
    return retenus


def _borner(
    ctx: ContexteTache, candidats: list[Passage], construire: Construire, budget: int
) -> list[Passage]:
    mesures: dict[int, int] = {}

    def prefixe(k: int) -> int:
        if k not in mesures:
            mesures[k] = ctx.llm.compter_tokens(construire(candidats[:k]))
        return mesures[k]

    k = len(candidats)
    while k > 0 and prefixe(k) > budget:
        k -= 1
    if prefixe(k) > budget:
        raise ContexteDepasse(
            f"Tâche {ctx.tache.code} : le prompt sans passage fait {prefixe(0)} tokens, "
            f"au-delà du budget de {budget} (contexte moins {reserve_sortie(ctx)} réservés "
            "à la sortie)"
        )
    if k == 0 and candidats:
        coupe = _tronquer(
            candidats[0],
            prefixe(0),
            prefixe(1),
            budget,
            lambda liste: ctx.llm.compter_tokens(construire(liste)),
        )
        return [coupe] if coupe is not None else []
    return candidats[:k]


def _couper(texte: str, ratio: float) -> str:
    """Début de `texte` (fraction `ratio` des caractères), coupé à une frontière de mot."""
    return texte[: int(len(texte) * ratio)].rsplit(" ", 1)[0].rstrip()


def _tronquer(
    passage: Passage,
    sans: int,
    tokens: int,
    budget: int,
    mesurer: Callable[[Sequence[Passage]], int],
) -> Passage | None:
    """`passage` tronqué à une frontière de mot pour tenir dans `budget`, ou `None`.

    `sans` est la mesure du prompt sans passage, `tokens` celle avec le passage entier. La
    longueur est réduite en proportion des tokens disponibles (avec `MARGE_TRONCATURE`),
    puis vérifiée par une mesure.
    """
    texte = passage.texte
    for _ in range(ESSAIS_TRONCATURE):
        exces = tokens - sans
        if exces <= 0:
            return None
        coupe = _couper(texte, min(MARGE_TRONCATURE, MARGE_TRONCATURE * (budget - sans) / exces))
        if not coupe:
            return None
        texte = coupe
        candidat = dataclasses.replace(passage, texte=texte + MARQUE_COUPE)
        tokens = mesurer([candidat])
        if tokens <= budget:
            return candidat
    return None


def borner_resultats(
    ctx: ContexteTache,
    contenus: Sequence[str],
    construire: ConstruireResultats,
    tools: Sequence[Mapping[str, Any]] | None,
) -> list[str]:
    """Contenus des résultats d'outils d'un tour, bornés pour que le tour suivant tienne.

    `construire(contenus)` rend les messages complets du tour suivant ; ils sont mesurés avec
    le schéma `tools` (majorant si le tour suivant n'offre plus d'outil). Chaque contenu est
    tronqué en proportion du dépassement (au plus `ESSAIS_TRONCATURE` mesures), puis remplacé
    par `MARQUE_COUPE` ; `ContexteDepasse` si même alors le prompt dépasse le budget.
    """
    textes = list(contenus)
    budget = budget_prompt(ctx)
    if budget is None or not textes:
        return textes

    def mesurer(liste: Sequence[str]) -> int:
        return ctx.llm.compter_tokens(construire(liste), tools)

    marque = MARQUE_COUPE.strip()
    try:
        tokens = mesurer(textes)
        if tokens <= budget:
            return textes
        vides = [marque] * len(textes)
        base = mesurer(vides)
        if base > budget:
            raise ContexteDepasse(
                f"Tâche {ctx.tache.code} : le prompt sans résultat d'outil fait {base} tokens, "
                f"au-delà du budget de {budget}"
            )
        for _ in range(ESSAIS_TRONCATURE):
            exces = tokens - base
            if exces <= 0:
                break
            ratio = min(MARGE_TRONCATURE, MARGE_TRONCATURE * (budget - base) / exces)
            textes = [_couper(texte.removesuffix(MARQUE_COUPE), ratio) for texte in textes]
            textes = [f"{texte}{MARQUE_COUPE}" if texte else marque for texte in textes]
            tokens = mesurer(textes)
            if tokens <= budget:
                break
        if tokens > budget:
            textes = vides
    except ContexteDepasse:
        raise
    except Exception as exc:  # repli d'avant F2 : la mesure n'est qu'un garde-fou
        _sans_budget(ctx, exc)
        return list(contenus)
    LOGGER.info(
        "Tâche %s : résultats d'outils tronqués pour tenir dans le contexte (budget %d)",
        ctx.tache.code,
        budget,
    )
    return textes


def plafond_reecriture(ctx: ContexteTache, messages: Sequence[Mapping[str, Any]]) -> int:
    """`max_tokens` d'une Tâche de réécriture (CO, TR) : proportionnel au prompt mesuré.

    `max(generation.max_tokens, ceil(facteur_reecriture × prompt) + marge_reecriture)`, borné
    par `taille_contexte − prompt` quand le contexte est connu. Le prompt (consigne, historique
    et entrée) majore l'entrée : le plafond est généreux, jamais une cible. Si la mesure
    échoue, `generation.max_tokens` (avertissement journalisé) ; si le prompt remplit déjà le
    contexte, `ContexteDepasse`.
    """
    generation = ctx.config.generation
    try:
        prompt = ctx.llm.compter_tokens(messages)
    except Exception as exc:  # repli : plafond par défaut
        _sans_budget(ctx, exc)
        return generation.max_tokens
    plafond = max(
        generation.max_tokens,
        math.ceil(generation.facteur_reecriture * prompt) + generation.marge_reecriture,
    )
    taille = _taille(ctx)
    if taille is None:
        return plafond
    reste = taille - prompt
    if reste < 1:
        raise ContexteDepasse(
            f"Tâche {ctx.tache.code} : le prompt fait {prompt} tokens, contexte de {taille}"
        )
    return min(plafond, reste)


__all__ = [
    "BUDGET_MIN",
    "ESSAIS_TRONCATURE",
    "MARQUE_COUPE",
    "borner_passages",
    "borner_resultats",
    "budget_prompt",
    "plafond_reecriture",
    "reserve_sortie",
]
