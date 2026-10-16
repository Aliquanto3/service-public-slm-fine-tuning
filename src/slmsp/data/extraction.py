"""Extracteur pur et versionné des réponses brutes Mistral (story 9.6, AD-3 verrou 4).

Seule voie par laquelle un texte d'entraînement sort d'une réponse journalisée : `build`
refabrique chaque ligne avec ces fonctions, puis compare octet par octet. Aucune lecture,
aucun état, aucune transformation du texte (pas de `strip`, pas de normalisation) : le
contenu est celui de `choices[0].message.content`, tel que Mistral l'a renvoyé.

`VERSION_EXTRACTEUR` s'incrémente à tout changement de comportement ; elle est inscrite dans
`meta.version_extracteur` de chaque ligne et dans le MANIFEST du jeu.
"""

from __future__ import annotations

from typing import Any, Final

from slmsp.core.erreurs import ProvenanceInvalide
from slmsp.mistral.generateur import message_assistant, raison_de_fin

__all__ = ["VERSION_EXTRACTEUR", "extraire_contenu", "extraire_message"]

VERSION_EXTRACTEUR: Final = 1


def extraire_message(brut: bytes | str | None) -> dict[str, Any]:
    """Message `assistant` de la réponse brute : `role`, `content` et `tool_calls` éventuels.

    Une réponse tronquée (`finish_reason = length`) est refusée. Lève `ProvenanceInvalide`.
    """
    message = message_assistant(brut)
    if raison_de_fin(brut) == "length":
        raise ProvenanceInvalide("réponse tronquée (finish_reason = length)")
    return message


def extraire_contenu(brut: bytes | str | None) -> str:
    """Contenu texte, sans appel d'outil, de la réponse brute. Lève `ProvenanceInvalide`."""
    message = extraire_message(brut)
    contenu = message.get("content")
    if "tool_calls" in message or not isinstance(contenu, str):
        raise ProvenanceInvalide("réponse brute : contenu texte seul attendu")
    return contenu
