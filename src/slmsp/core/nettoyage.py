"""Nettoyage déterministe des cibles d'un jeu SFT (story 9.9) : transformation pure et preuve.

`nettoyer_cible` retire la ligne de préambule « Voici … » d'une réponse cible (version 1), puis
une première ligne qui n'est qu'un titre (version 2, story 9.10), rien d'autre (D1 : aucun
texte n'est rédigé ni réécrit). Chaque jeu nettoyé se revérifie avec la règle de sa version
(MANIFEST `nettoyage.version`) : un jeu de version 1 (v4) reste vérifiable.

`verifier_nettoyage` prouve qu'un jeu nettoyé ne
diffère de son jeu source que par cette transformation : chaque ligne nettoyée est, à l'octet
près en JSON canonique, la ligne source de même rang d'origine dont le `content` du dernier
message vaut `nettoyer_cible(content)` ; seules manquent les lignes dont le rang est déclaré
écarté (MANIFEST `nettoyage.ecartes`), l'ordre est conservé.

Placé dans `core` : partagé par `data` (écriture du jeu) et `train` (relecture au chargement).
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from typing import Any, Final, Literal

from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import ProvenanceInvalide

__all__ = [
    "VERSION_NETTOYAGE",
    "VERSIONS_NETTOYAGE",
    "analyser_preambule",
    "analyser_cible",
    "analyser_titre",
    "cible_nettoyable",
    "ligne_nettoyee",
    "nettoyer_cible",
    "verifier_nettoyage",
]

VERSION_NETTOYAGE: Final = 2
"""Version courante de `nettoyer_cible` : une autre règle change ce numéro (MANIFEST
`nettoyage`). 1 : préambule « Voici » ; 2 : préambule puis titre de tête."""
VERSIONS_NETTOYAGE: Final = frozenset({1, 2})
"""Versions que `nettoyer_cible` sait rejouer (revérification des jeux déjà nettoyés)."""

Preambule = Literal["retire", "garde", "seul"]

_RE_TETE: Final = re.compile(r"^[#*_\s\uFEFF]*")
_RE_FIN: Final = re.compile(r"[*_\s]*$")
_RE_GRAS: Final = re.compile(r"\*\*[^*]+\*\*|__[^_]+__")
_RE_TITRE: Final = re.compile(r"\*\*[^*]+\*\*|#.*")
"""Ligne qui n'est qu'un titre (une fois ôtés les espaces) : `**…**` seul, ou `#…`."""


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


def analyser_titre(texte: str) -> tuple[str, bool]:
    """`(texte nettoyé, titre retiré)` : titre de tête de `texte` (version 2).

    Seule la première ligne non vide est examinée, jamais au-delà. Si elle n'est qu'un titre
    (`**…**` seul sur la ligne, ou ligne `#…`) et qu'un texte non vide la suit, elle est ôtée
    avec les lignes vides qui l'entourent ; sinon `texte` est rendu tel quel.
    """
    lignes = texte.split("\n")
    debut = next((i for i, ligne in enumerate(lignes) if ligne.strip()), None)
    if debut is None or _RE_TITRE.fullmatch(lignes[debut].strip().lstrip("﻿")) is None:
        return texte, False
    suite = next((i for i in range(debut + 1, len(lignes)) if lignes[i].strip()), None)
    if suite is None:
        return texte, False
    return "\n".join(lignes[suite:]), True


def analyser_cible(
    texte: str, version: int = VERSION_NETTOYAGE
) -> tuple[str, Preambule | None, bool]:
    """`(texte nettoyé, statut du préambule, titre retiré)` selon la règle de `version`.

    Version 1 : préambule seul (`analyser_preambule`). Version 2 : préambule, puis titre de
    tête (`analyser_titre`) sur le texte restant. Lève `ValueError` pour une autre version.
    """
    if version not in VERSIONS_NETTOYAGE:
        raise ValueError(f"version de nettoyage {version} inconnue")
    texte, statut = analyser_preambule(texte)
    if version == 1:
        return texte, statut, False
    texte, titre = analyser_titre(texte)
    return texte, statut, titre


def nettoyer_cible(texte: str, version: int = VERSION_NETTOYAGE) -> str:
    """`texte` nettoyé selon la règle de `version` (`analyser_cible`)."""
    return analyser_cible(texte, version)[0]


def cible_nettoyable(ligne: dict[str, Any]) -> dict[str, Any] | None:
    """Dernier message de `ligne` si son `content` est une chaîne sans `tool_calls`."""
    messages = ligne.get("messages")
    if not isinstance(messages, list) or not messages:
        return None
    dernier = messages[-1]
    if not isinstance(dernier, dict) or "tool_calls" in dernier:
        return None
    return dernier if isinstance(dernier.get("content"), str) else None


def ligne_nettoyee(octets: bytes, version: int = VERSION_NETTOYAGE) -> bytes:
    """JSON canonique de la ligne source `octets`, cible passée par `nettoyer_cible`."""
    ligne = json.loads(octets)
    cible = cible_nettoyable(ligne) if isinstance(ligne, dict) else None
    if cible is not None:
        cible["content"] = nettoyer_cible(cible["content"], version)
    return json_canonique(ligne)


def _lignes(octets: bytes) -> list[bytes]:
    return [ligne for ligne in octets.split(b"\n") if ligne.strip()]


def verifier_nettoyage(
    octets_nettoyes: bytes,
    octets_source: bytes,
    rangs_ecartes: Sequence[int],
    version: int = VERSION_NETTOYAGE,
) -> None:
    """Lève `ProvenanceInvalide` si le jeu nettoyé n'est pas issu du jeu source par la règle
    de `version` (`VERSIONS_NETTOYAGE` ; une autre version est refusée).

    Les lignes source gardées sont toutes celles dont le rang (0 = première ligne non vide)
    n'est pas dans `rangs_ecartes` (MANIFEST `nettoyage.ecartes`). La n-ième ligne nettoyée
    doit valoir `ligne_nettoyee` de la n-ième ligne gardée, à l'octet près : une ligne en
    trop, en moins, déplacée ou dont un octet diffère hors de la transformation est refusée.
    """
    if version not in VERSIONS_NETTOYAGE:
        raise ProvenanceInvalide(f"version de nettoyage {version} inconnue")
    try:
        source = _lignes(octets_source)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ProvenanceInvalide(f"jeu source illisible : {exc}") from None
    ecartes = set(rangs_ecartes)
    if len(ecartes) != len(rangs_ecartes) or any(not 0 <= r < len(source) for r in ecartes):
        raise ProvenanceInvalide(
            f"rangs écartés invalides (doublon ou hors des {len(source)} lignes source)"
        )
    gardees = [ligne for rang, ligne in enumerate(source) if rang not in ecartes]
    nettoyees = _lignes(octets_nettoyes)
    if len(nettoyees) != len(gardees):
        raise ProvenanceInvalide(
            f"{len(nettoyees)} lignes nettoyées pour {len(gardees)} lignes source gardées "
            f"({len(source)} moins {len(ecartes)} écartées)"
        )
    for numero, (ligne, origine) in enumerate(zip(nettoyees, gardees, strict=True), start=1):
        try:
            attendue = ligne_nettoyee(origine, version)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ProvenanceInvalide(f"jeu source illisible : {exc}") from None
        if ligne != attendue:
            raise ProvenanceInvalide(
                f"ligne {numero} du jeu nettoyé : n'est pas le nettoyage (version "
                f"{version}) de la ligne source de même rang d'origine"
            )
