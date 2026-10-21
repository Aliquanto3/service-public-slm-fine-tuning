"""Alignement des prompts CT d'entraînement sur leur cible (story 16.3) : transformation pure.

Chaque ligne CT reçoit, à la fin du premier paragraphe de son message `user` (« Consigne : »),
une consigne de libellés : `formulation` où `{libelles}` est remplacé par les emplacements entre
crochets **extraits de la cible Mistral de la ligne** (ordre de première apparition, sans
doublon). Le prompt s'aligne sur la cible : aucune cible n'est réécrite (D1), aucun appel. La
`formulation` vient de l'appelant (texte d'origine non-Claude, documentée au MANIFEST) : ce
module n'en contient aucune. Les autres lignes sont copiées à l'octet près, dans l'ordre.

Placé dans `core` : partagé par `data` (écriture) et `train` (relecture au chargement).
"""

from __future__ import annotations

import json
import re
from typing import Any, Final

from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide

__all__ = [
    "EMPLACEMENT_LIBELLES",
    "TACHE_CT",
    "aligner_jeu",
    "aligner_ligne",
    "extraire_libelles",
    "valider_formulation",
    "verifier_alignement",
]

TACHE_CT: Final = "CT"
EMPLACEMENT_LIBELLES: Final = "{libelles}"
PREFIXE_CONSIGNE: Final = "Consigne :\n"
SEPARATEUR_LIBELLES: Final = ", "
_LIBELLE: Final = re.compile(r"\[[^\[\]\n]+\]")


def extraire_libelles(cible: str) -> list[str]:
    """Emplacements `[...]` de `cible` (crochets compris), ordre de première apparition."""
    return list(dict.fromkeys(trouve.group() for trouve in _LIBELLE.finditer(cible)))


def valider_formulation(formulation: str) -> None:
    """Lève `ManifesteInvalide` si `formulation` n'a pas exactement un `{libelles}`.

    Aucune autre accolade n'est admise (rendu par remplacement simple, pas de `format`).
    """
    reste = formulation.replace(EMPLACEMENT_LIBELLES, "", 1)
    if (
        not formulation.strip()
        or EMPLACEMENT_LIBELLES not in formulation
        or "{" in reste
        or "}" in reste
        or "\n" in formulation
    ):
        raise ManifesteInvalide(
            f"formulation de la consigne de libellés : une ligne avec exactement un "
            f"{EMPLACEMENT_LIBELLES} et aucune autre accolade attendue"
        )


def _message(ligne: dict[str, Any], role: str) -> dict[str, Any]:
    for message in ligne.get("messages") or []:
        if message.get("role") == role:
            return message
    raise ManifesteInvalide(f"ligne CT sans message {role}")


def aligner_ligne(texte: bytes, formulation: str) -> tuple[bytes, bool]:
    """`(ligne, modifiee)` : la ligne CT alignée, ou `texte` inchangé (autre Tâche, sans libellé).

    Lève `ManifesteInvalide` pour une ligne CT dont le message `user` ne commence pas par
    « Consigne : » suivi d'un paragraphe.
    """
    ligne = json.loads(texte)
    if ligne.get("tache") != TACHE_CT:
        return texte, False
    cible = _message(ligne, "assistant").get("content")
    libelles = extraire_libelles(cible if isinstance(cible, str) else "")
    if not libelles:
        return texte, False
    user = _message(ligne, "user")
    contenu = user.get("content")
    fin = contenu.find("\n\n") if isinstance(contenu, str) else -1
    if not isinstance(contenu, str) or not contenu.startswith(PREFIXE_CONSIGNE) or fin == -1:
        raise ManifesteInvalide("ligne CT : message user « Consigne : » puis paragraphe attendu")
    consigne = formulation.replace(EMPLACEMENT_LIBELLES, SEPARATEUR_LIBELLES.join(libelles), 1)
    user["content"] = f"{contenu[:fin]} {consigne}{contenu[fin:]}"
    return json_canonique(ligne), True


def aligner_jeu(source: bytes, formulation: str) -> tuple[bytes, int]:
    """`(train.jsonl aligné, lignes modifiées)` depuis le `train.jsonl` `source`."""
    valider_formulation(formulation)
    sortie: list[bytes] = []
    modifiees = 0
    for texte in source.split(b"\n"):
        if not texte.strip():
            continue
        ligne, modifiee = aligner_ligne(texte, formulation)
        sortie.append(ligne + b"\n")
        modifiees += modifiee
    return b"".join(sortie), modifiees


def verifier_alignement(octets: bytes, source: bytes, formulation: str, modifiees: int) -> None:
    """Lève `ProvenanceInvalide` si `octets` n'est pas exactement l'alignement de `source`."""
    attendu, compte = aligner_jeu(source, formulation)
    if octets != attendu or compte != modifiees:
        raise ProvenanceInvalide(
            "jeu aligné : train.jsonl n'est pas l'alignement CT du jeu source "
            "(formulation ou lignes modifiées différentes)"
        )
