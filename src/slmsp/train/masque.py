"""Masque de perte par rendu incrémental (story 10.2, AD-7, H-MASQUE).

Implémentation unique du masque, partagée par tous les Runs (TRL, Unsloth). Pour chaque
message `assistant` d'indice k, le tour est le texte compris entre le rendu des k premiers
messages avec l'amorce de génération et le rendu des k+1 premiers messages : contenu,
`tool_calls` sérialisés par le template, fin de tour (et ce que le template écrit ensuite
dans ce rendu, par exemple un saut de ligne). Le texte complet est tokenisé avec les
positions de caractères ; un token appartient à un tour `assistant` s'il est contenu dans
ce tour. Tous les autres labels valent -100.

Le masque refuse (`ErreurMasque`) ce qu'il ne peut pas prouver : rendu incrémental qui n'est
pas un préfixe du rendu complet (template qui réécrit l'historique, par exemple en retirant
le raisonnement des tours passés), ou token à cheval sur une frontière de tour. Le repli est
alors une variante d'entraînement du template, limitée aux balises `generation` (epic 10).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from slmsp.core.erreurs import SlmspError
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.train.rendu import apply_chat_template

IGNORE = -100
"""Valeur d'étiquette ignorée par la perte."""

VERSION_MASQUE = 1
"""À inscrire dans `run.json` : deux Runs d'une campagne partagent la version du masque."""


class ErreurMasque(SlmspError):
    """Le masque d'une conversation ne peut pas être établi de façon sûre."""


@dataclass(frozen=True)
class RenduMasque:
    texte: str
    input_ids: list[int]
    labels: list[int]
    tours: list[tuple[int, int]]
    """Intervalles `[debut, fin)` en caractères des tours `assistant` dans `texte`."""


def intervalles_assistant(
    tokenizer: Any,
    messages: Sequence[Mapping[str, Any]],
    *,
    tools: Sequence[Mapping[str, Any]] | None = None,
    config: ConfigModele | None = None,
) -> tuple[str, list[tuple[int, int]]]:
    """Texte rendu et intervalles de caractères des tours `assistant` (rendu incrémental)."""
    options: dict[str, Any] = {"tools": tools, "config": config}
    texte = apply_chat_template(tokenizer, messages, **options)
    tours: list[tuple[int, int]] = []
    for k, message in enumerate(messages):
        if message.get("role") != "assistant":
            continue
        try:
            amorce = apply_chat_template(
                tokenizer, messages[:k], add_generation_prompt=True, **options
            )
        except Exception as erreur:
            # k == 0 : le template ne rend pas une liste vide (ou injecte un préambule
            # que l'on ne sait pas borner sans message précédent).
            raise ErreurMasque(
                f"l'amorce du message assistant {k} n'est pas calculable ({erreur})"
            ) from erreur
        debut = len(amorce)
        jusque = apply_chat_template(tokenizer, messages[: k + 1], **options)
        if len(jusque) <= debut:
            raise ErreurMasque(f"le message assistant {k} ne produit aucun texte")
        if not texte.startswith(amorce) or not texte.startswith(jusque):
            raise ErreurMasque(
                f"le rendu du message {k} n'est pas un préfixe du rendu complet : "
                "le template réécrit l'historique (variante `generation` requise)"
            )
        tours.append((debut, len(jusque)))
    return texte, tours


def calculer_masque(
    tokenizer: Any,
    messages: Sequence[Mapping[str, Any]],
    *,
    tools: Sequence[Mapping[str, Any]] | None = None,
    config: ConfigModele | None = None,
) -> RenduMasque:
    """`input_ids` et `labels` (-100 hors des tours `assistant`) d'une conversation."""
    texte, tours = intervalles_assistant(tokenizer, messages, tools=tools, config=config)
    try:
        encodage = tokenizer(texte, add_special_tokens=False, return_offsets_mapping=True)
        ids = [int(i) for i in encodage["input_ids"]]
        positions = [(int(a), int(b)) for a, b in encodage["offset_mapping"]]
    except (NotImplementedError, KeyError, ValueError) as erreur:
        raise ErreurMasque(
            f"positions de caractères indisponibles (tokenizer rapide requis) : {erreur}"
        ) from erreur
    labels: list[int] = []
    for indice, (a, b) in enumerate(positions):
        dedans = next((t for t in tours if t[0] <= a < t[1]), None)
        if dedans is None:
            if any(a < t[0] < b or a < t[1] < b for t in tours):
                raise ErreurMasque(f"le token {indice} chevauche le début d'un tour assistant")
            labels.append(IGNORE)
        elif b > dedans[1]:
            raise ErreurMasque(f"le token {indice} déborde de la fin d'un tour assistant")
        else:
            labels.append(ids[indice])
    return RenduMasque(texte=texte, input_ids=ids, labels=labels, tours=tours)


def texte_non_masque(tokenizer: Any, rendu: RenduMasque) -> str:
    """Texte des tokens non masqués (contrôle d'égalité avec les tours du rendu officiel)."""
    gardes = [i for i, etiquette in enumerate(rendu.labels) if etiquette != IGNORE]
    return tokenizer.decode([rendu.input_ids[i] for i in gardes]) if gardes else ""
