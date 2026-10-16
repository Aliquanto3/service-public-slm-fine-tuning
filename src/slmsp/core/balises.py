"""Protocole d'outils `balises-tool-call` (SmolLM3) : réécriture de l'historique.

Le template de SmolLM3 demande au modèle des appels `<tool_call>{"name", "arguments"}</tool_call>`
dans le texte, mais ignore `message.tool_calls` : un tour `assistant` qui ne porte que des
`tool_calls` disparaîtrait du rendu. `messages_balises` réécrit ces appels en balises dans
`content`. Partagé par l'inférence (`inference.client`) et l'entraînement (`train.chargement`),
pour que le modèle voie le même format dans les deux cas.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Final

PROTOCOLE_BALISES: Final = "balises-tool-call"
BALISE_OUVRANTE: Final = "<tool_call>"
BALISE_FERMANTE: Final = "</tool_call>"


def messages_balises(messages: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Copie des messages où les `tool_calls` d'un tour `assistant` sont réécrits en balises.

    Chaque appel devient `<tool_call>\\n{"name", "arguments"}\\n</tool_call>`, ajouté après le
    `content`. L'ordre « texte, puis appels » est celui que produit le client : il cesse de
    lire un tour après le premier `</tool_call>` (seuls d'autres appels consécutifs sont
    encore lus), si bien qu'un tour `assistant` n'a jamais de texte après ses appels.
    """
    resultat: list[dict[str, Any]] = []
    for message in messages:
        copie = dict(message)
        appels = copie.get("tool_calls")
        if copie.get("role") == "assistant" and appels:
            blocs = []
            for appel in appels:
                fonction = appel.get("function") or {}
                arguments = fonction.get("arguments")
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        pass
                objet = json.dumps(
                    {"name": fonction.get("name"), "arguments": arguments}, ensure_ascii=False
                )
                blocs.append(f"{BALISE_OUVRANTE}\n{objet}\n{BALISE_FERMANTE}")
            contenu = copie.get("content") or ""
            copie["content"] = "\n".join(([contenu] if contenu else []) + blocs)
            del copie["tool_calls"]
        resultat.append(copie)
    return resultat


__all__ = ["BALISE_FERMANTE", "BALISE_OUVRANTE", "PROTOCOLE_BALISES", "messages_balises"]
