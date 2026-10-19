"""Nettoyage déterministe des cibles d'un jeu SFT (story 9.9) : transformation pure et preuve.

`nettoyer_cible` retire la ligne de préambule « Voici … » d'une réponse cible, rien d'autre
(D1 : aucun texte n'est rédigé ni réécrit). `verifier_nettoyage` prouve qu'un jeu nettoyé ne
diffère de son jeu source que par cette transformation : chaque ligne nettoyée est, à l'octet
près en JSON canonique, la ligne source de même rang d'origine dont le `content` du dernier
message vaut `nettoyer_cible(content)` ; les lignes écartées manquent, l'ordre est conservé.

Placé dans `core` : partagé par `data` (écriture du jeu) et `train` (relecture au chargement).
"""

from __future__ import annotations

import json
import re
from typing import Any, Final, Literal

from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import ProvenanceInvalide

__all__ = [
    "VERSION_NETTOYAGE",
    "analyser_preambule",
    "cible_nettoyable",
    "ligne_nettoyee",
    "nettoyer_cible",
    "verifier_nettoyage",
]

VERSION_NETTOYAGE: Final = 1
"""Version de `nettoyer_cible` : une autre règle change ce numéro (MANIFEST `nettoyage`)."""

Preambule = Literal["retire", "garde", "seul"]

_RE_TETE: Final = re.compile(r"^[#*_\s]*")
_RE_FIN: Final = re.compile(r"[*_\s]*$")
_RE_GRAS: Final = re.compile(r"\*\*[^*]+\*\*|__[^_]+__")


def analyser_preambule(texte: str) -> tuple[str, Preambule | None]:
    """`(texte nettoyé, statut)` du préambule « Voici » de `texte`.

    Statut `None` si la première ligne non vide ne commence pas par « Voici » (marqueurs de
    tête `#`, `*`, `_` et espaces ignorés) ; `seul` si rien ne la suit ; `garde` si elle ne
    finit pas par `:` (hors `*`, `_`, espaces) sans être entièrement en gras, ou si elle
    contient un lien (`](`, `http`) ; `retire` sinon : elle est ôtée avec les lignes vides
    qui l'entourent. Seul un statut `retire` change le texte.
    """
    lignes = texte.split("\n")
    debut = next((i for i, ligne in enumerate(lignes) if ligne.strip()), None)
    if debut is None:
        return texte, None
    premiere = lignes[debut]
    if not _RE_TETE.sub("", premiere).startswith("Voici"):
        return texte, None
    suite = next((i for i in range(debut + 1, len(lignes)) if lignes[i].strip()), None)
    if suite is None:
        return texte, "seul"
    deux_points = _RE_FIN.sub("", premiere).endswith(":")
    en_gras = _RE_GRAS.fullmatch(premiere.strip()) is not None
    lien = "](" in premiere or "http" in premiere
    if (deux_points or en_gras) and not lien:
        return "\n".join(lignes[suite:]), "retire"
    return texte, "garde"


def nettoyer_cible(texte: str) -> str:
    """`texte` sans sa ligne de préambule « Voici » retirable (`analyser_preambule`)."""
    return analyser_preambule(texte)[0]


def cible_nettoyable(ligne: dict[str, Any]) -> dict[str, Any] | None:
    """Dernier message de `ligne` si son `content` est une chaîne sans `tool_calls`."""
    messages = ligne.get("messages")
    if not isinstance(messages, list) or not messages:
        return None
    dernier = messages[-1]
    if not isinstance(dernier, dict) or "tool_calls" in dernier:
        return None
    return dernier if isinstance(dernier.get("content"), str) else None


def ligne_nettoyee(octets: bytes) -> bytes:
    """JSON canonique de la ligne source `octets`, cible passée par `nettoyer_cible`."""
    ligne = json.loads(octets)
    cible = cible_nettoyable(ligne) if isinstance(ligne, dict) else None
    if cible is not None:
        cible["content"] = nettoyer_cible(cible["content"])
    return json_canonique(ligne)


def _lignes(octets: bytes) -> list[bytes]:
    return [ligne for ligne in octets.split(b"\n") if ligne.strip()]


def verifier_nettoyage(octets_nettoyes: bytes, octets_source: bytes) -> None:
    """Lève `ProvenanceInvalide` si le jeu nettoyé n'est pas issu du jeu source.

    Chaque ligne nettoyée doit valoir `ligne_nettoyee` d'une ligne source, dans l'ordre des
    rangs d'origine (sous-suite : les lignes écartées manquent). Un octet différent ailleurs
    que dans la transformation (cible ou autre message) ou un ordre changé est refusé.
    """
    try:
        attendues = [ligne_nettoyee(ligne) for ligne in _lignes(octets_source)]
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ProvenanceInvalide(f"jeu source illisible : {exc}") from None
    rang = 0
    for numero, ligne in enumerate(_lignes(octets_nettoyes), start=1):
        while rang < len(attendues) and attendues[rang] != ligne:
            rang += 1
        if rang == len(attendues):
            raise ProvenanceInvalide(
                f"ligne {numero} du jeu nettoyé : aucune ligne source dont elle soit le "
                f"nettoyage (version {VERSION_NETTOYAGE}), dans l'ordre d'origine"
            )
        rang += 1
