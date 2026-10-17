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
alors le découpage par tour (`decoupage_masque = "par-tour"` dans la fiche du Modèle,
spec-masque-minicpm5) : un exemple par tour `assistant`, dont le texte est l'amorce officielle
(historique rendu par le template, `add_generation_prompt=True`) suivie du corps du tour, seul
supervisé. Texte et tokens sont alors ceux de l'inférence à chaque tour (`calculer_masques`).
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
        if len(jusque) <= debut and amorce.startswith(jusque):
            raise ErreurMasque(f"le message assistant {k} ne produit aucun texte")
        if not jusque.startswith(amorce):
            # Cas de MiniCPM5 avec `enable_thinking = false` : l'amorce de génération se
            # termine par un bloc de raisonnement vide que le tour rendu ne contient pas.
            raise ErreurMasque(
                f"l'amorce de génération du message {k} n'est pas un préfixe du rendu de ce "
                "tour : le template écrit à la génération un texte absent du tour rendu (par "
                "exemple un bloc de raisonnement vide) ou réécrit l'historique"
            )
        if not texte.startswith(jusque):
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
    ids, positions = _tokeniser(tokenizer, texte)
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


def _tokeniser(tokenizer: Any, texte: str) -> tuple[list[int], list[tuple[int, int]]]:
    try:
        encodage = tokenizer(texte, add_special_tokens=False, return_offsets_mapping=True)
        ids = [int(i) for i in encodage["input_ids"]]
        positions = [(int(a), int(b)) for a, b in encodage["offset_mapping"]]
    except (NotImplementedError, KeyError, ValueError) as erreur:
        raise ErreurMasque(
            f"positions de caractères indisponibles (tokenizer rapide requis) : {erreur}"
        ) from erreur
    return ids, positions


def amorce_et_corps(
    tokenizer: Any,
    messages: Sequence[Mapping[str, Any]],
    k: int,
    *,
    tools: Sequence[Mapping[str, Any]] | None = None,
    config: ConfigModele | None = None,
) -> tuple[str, str]:
    """Découpage par tour : amorce officielle du message `assistant` `k` et corps de ce tour.

    L'amorce est `apply_chat_template(messages[:k], add_generation_prompt=True)`, le texte
    envoyé au modèle à l'inférence. Le corps est la suite du rendu de `messages[:k+1]` après
    l'ouverture du tour : l'amorce entière si le rendu la prolonge, sinon l'amorce privée de
    `bloc_amorce` (déclaré dans la fiche) si le template n'écrit pas ce bloc dans un tour rendu.
    """
    message = messages[k]
    if message.get("role") != "assistant":
        raise ValueError(f"le message {k} n'est pas un message assistant")
    raisonnement = message.get("reasoning_content")
    if isinstance(raisonnement, str) and raisonnement.strip():
        raise ErreurMasque(
            f"le message assistant {k} porte un `reasoning_content` : le découpage par tour "
            "ne supervise pas de raisonnement (amorce sans raisonnement à l'inférence)"
        )
    bloc = config.bloc_amorce if config is not None else None
    contenu = message.get("content")
    if bloc and isinstance(contenu, str):
        marqueurs = [ligne for ligne in bloc.splitlines() if ligne.strip()]
        present = next((m for m in marqueurs if m in contenu), None)
        if present is not None:
            raise ErreurMasque(
                f"le contenu du message assistant {k} contient « {present} » (balise du bloc "
                "d'amorce) : le template le réécrirait, aucun bloc n'est ajouté"
            )
    options: dict[str, Any] = {"tools": tools, "config": config}
    try:
        amorce = apply_chat_template(tokenizer, messages[:k], add_generation_prompt=True, **options)
    except Exception as erreur:
        raise ErreurMasque(
            f"l'amorce du message assistant {k} n'est pas calculable ({erreur})"
        ) from erreur
    jusque = apply_chat_template(tokenizer, messages[: k + 1], **options)
    if jusque.startswith(amorce):
        corps = jusque[len(amorce) :]
    elif bloc and amorce.endswith(bloc) and jusque.startswith(amorce[: -len(bloc)]):
        corps = jusque[len(amorce) - len(bloc) :]
    else:
        raise ErreurMasque(
            f"le rendu du message assistant {k} ne prolonge pas l'amorce de génération"
            + (" privée de `bloc_amorce`" if bloc else "")
            + " : ouverture du tour introuvable (bloc_amorce à déclarer, ou kwargs changés)"
        )
    if not corps:
        raise ErreurMasque(f"le message assistant {k} ne produit aucun texte")
    return amorce, corps


def masque_du_tour(
    tokenizer: Any,
    messages: Sequence[Mapping[str, Any]],
    k: int,
    *,
    tools: Sequence[Mapping[str, Any]] | None = None,
    config: ConfigModele | None = None,
) -> RenduMasque:
    """Exemple du tour `assistant` `k` : amorce officielle (masquée) puis corps (supervisé).

    Contrôle bloquant au niveau des tokens : la tokenisation de l'amorce seule est exactement
    le début des `input_ids` de l'exemple, et aucun token ne chevauche la frontière. Le modèle
    voit donc à l'entraînement les tokens qu'il reçoit à l'inférence avant de générer.
    """
    amorce, corps = amorce_et_corps(tokenizer, messages, k, tools=tools, config=config)
    texte = amorce + corps
    ids, positions = _tokeniser(tokenizer, texte)
    ids_amorce, _ = _tokeniser(tokenizer, amorce)
    debut = len(amorce)
    if any(a < debut < b for a, b in positions):
        raise ErreurMasque(f"un token du message {k} chevauche la fin de l'amorce")
    n_amorce = sum(b <= debut for _, b in positions)
    if ids[:n_amorce] != ids_amorce:
        raise ErreurMasque(
            f"les tokens de l'amorce du message {k} diffèrent de ceux de l'amorce seule"
        )
    labels = [IGNORE] * n_amorce + ids[n_amorce:]
    return RenduMasque(texte=texte, input_ids=ids, labels=labels, tours=[(debut, len(texte))])


def calculer_masques(
    tokenizer: Any,
    messages: Sequence[Mapping[str, Any]],
    *,
    tools: Sequence[Mapping[str, Any]] | None = None,
    config: ConfigModele | None = None,
) -> list[RenduMasque]:
    """Exemples d'une conversation selon `decoupage_masque` de la fiche du Modèle.

    `conversation` (défaut) : un exemple, `calculer_masque`. `par-tour` : un exemple par
    message `assistant` (`masque_du_tour`), aucun sans tour `assistant`.
    """
    if config is None or config.decoupage_masque == "conversation":
        return [calculer_masque(tokenizer, messages, tools=tools, config=config)]
    return [
        masque_du_tour(tokenizer, messages, k, tools=tools, config=config)
        for k, message in enumerate(messages)
        if message.get("role") == "assistant"
    ]


def empreinte_decoupage(config: ConfigModele) -> dict[str, Any] | None:
    """Découpage inscrit dans les invariants d'un Run (`None` : `conversation`, défaut)."""
    if config.decoupage_masque == "conversation":
        return None
    return {"mode": config.decoupage_masque, "bloc_amorce": config.bloc_amorce}


def texte_non_masque(tokenizer: Any, rendu: RenduMasque) -> str:
    """Texte des tokens non masqués (contrôle d'égalité avec les tours du rendu officiel)."""
    gardes = [i for i, etiquette in enumerate(rendu.labels) if etiquette != IGNORE]
    return tokenizer.decode([rendu.input_ids[i] for i in gardes]) if gardes else ""
