"""Emplacements d'un courrier type : détection et contrôles (story 13.3, FR-14).

Un emplacement est un libellé entre crochets sur une seule ligne, sans crochet imbriqué
(« [à compléter] », « [date de la décision] »). Fonctions pures, sans dépendance.

- `segmenter` découpe un texte en segments `texte` et `emplacement`, dont la concaténation
  redonne le texte d'origine.
- `libelles_presents` : chaque libellé attendu figure tel quel (crochets compris). C'est la règle
  du contrôle automatique CT de la notation, que `evaluation.controles` importe d'ici.
- `champ_rendu_par_une_valeur` : la ligne « Intitulé : … » d'un champ non fourni porte une
  valeur, et non un emplacement (« aucun champ non fourni rendu par une valeur »).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from typing import Final, Literal, TypedDict

LONGUEUR_MAX: Final = 120
"""Longueur maximale du libellé d'un emplacement (au-delà, ce n'est pas un emplacement)."""

_RE_EMPLACEMENT: Final = re.compile(rf"\[[^\[\]\n]{{1,{LONGUEUR_MAX}}}\]")
_DECOR: Final = "*_#> \t"


class Segment(TypedDict):
    type: Literal["texte", "emplacement"]
    texte: str


def segmenter(texte: str) -> list[Segment]:
    """Segments successifs ; un `emplacement` garde ses crochets. Texte vide : liste vide."""
    segments: list[Segment] = []
    position = 0
    for m in _RE_EMPLACEMENT.finditer(texte):
        if not m.group()[1:-1].strip():
            continue
        if m.start() > position:
            segments.append({"type": "texte", "texte": texte[position : m.start()]})
        segments.append({"type": "emplacement", "texte": m.group()})
        position = m.end()
    if position < len(texte):
        segments.append({"type": "texte", "texte": texte[position:]})
    return segments


def detecter(texte: str) -> list[str]:
    """Emplacements du texte, dans l'ordre, crochets compris."""
    return [s["texte"] for s in segmenter(texte) if s["type"] == "emplacement"]


def libelles_presents(texte: str, libelles: Iterable[str]) -> dict[str, bool]:
    """Pour chaque libellé attendu, sa présence telle quelle dans le texte."""
    return {libelle: libelle in texte for libelle in libelles}


def _normaliser(texte: str) -> str:
    sans_accent = "".join(
        c for c in unicodedata.normalize("NFD", texte.casefold()) if not unicodedata.combining(c)
    )
    return sans_accent.strip(_DECOR)


_RE_PUCE: Final = re.compile(r"^\s*(?:[-+*•–]|\d+[.)])\s+")


def champ_rendu_par_une_valeur(texte: str, intitule: str) -> bool:
    """Vrai si une ligne « <intitulé> : valeur » ne porte aucun emplacement.

    L'intitulé se compare sans casse ni accent, en ignorant la mise en forme (gras, titre, puce).
    La valeur compte dès qu'il reste du texte une fois les emplacements retirés (« Objet : valeur
    [date] » est rendu par une valeur). Sans ligne d'intitulé, ou avec une valeur vide ou faite
    d'emplacements seuls, le champ n'est pas jugé rendu par une valeur.
    """
    cible = _normaliser(intitule)
    for ligne in texte.splitlines():
        tete, separateur, valeur = _RE_PUCE.sub("", ligne).partition(":")
        if not separateur or _normaliser(tete) != cible:
            continue
        reste = _RE_EMPLACEMENT.sub("", valeur).strip(_DECOR)
        if any(c.isalnum() for c in reste):
            return True
    return False
