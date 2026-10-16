"""Différences par mots entre un texte et sa correction (story 13.1, FR-17, UX-DR13).

Calcul pur, sans dépendance (`difflib`). Les deux textes sont normalisés en NFC.

Approche hiérarchique, pour que des corrections dispersées dans un long texte restent visibles
une à une :
1. comparaison par phrases et lignes ;
2. dans les seuls blocs modifiés, comparaison par mots (un mot, ou un signe de ponctuation, avec
   l'espace qui le précède ; une marque combinante ou une séquence emoji reste collée à sa base).

Les segments « égal » et « suppression » redonnent `avant` (en NFC), ceux « égal » et « ajout »
redonnent `apres`, aux espaces horizontales près : pour la comparaison, toute espace horizontale
(y compris l'espace insécable) est ignorée, donc un changement d'espacement seul n'est pas une
correction, et un segment « égal » reprend l'espacement de `avant`. Les retours à la ligne comptent.

Coût borné : préfixe et suffixe communs retirés, puis si le produit des tailles d'un bloc
modifié dépasse `LIMITE_PRODUIT` (25 000 000, soit 5 000 mots par côté), ce bloc est rendu comme
un seul bloc supprimé suivi d'un seul bloc ajouté (grossier mais exact, jamais d'explosion
quadratique).
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Final, Literal, TypedDict

EGAL: Final = "egal"
AJOUT: Final = "ajout"
SUPPRESSION: Final = "suppression"
LIMITE_PRODUIT: Final = 25_000_000  # ~5 000 x 5 000 éléments par bloc modifié (< 1 s en pratique)
_PHRASES: Final = re.compile(r".*?(?:[.!?…]+(?=\s|$)[^\S\n]*\n*|\n+|$)", re.DOTALL)
_ESPACES_HORIZONTALES: Final = re.compile(r"[^\S\n]+")
_ZWJ: Final = "‍"

Genre = Literal["egal", "ajout", "suppression"]


class Segment(TypedDict):
    type: Genre
    texte: str


def _cle(element: str) -> str:
    return _ESPACES_HORIZONTALES.sub("", element)


def _est_modificateur(c: str) -> bool:
    return unicodedata.category(c).startswith("M") or "\U0001f3fb" <= c <= "\U0001f3ff"


def _graphemes(texte: str) -> list[str]:
    """Groupes simples : base + marques combinantes, séquences ZWJ, drapeaux (paires)."""
    groupes: list[str] = []
    colle = False  # le caractère suivant se colle au groupe en cours (après ZWJ)
    for c in texte:
        if groupes and (colle or _est_modificateur(c) or c == _ZWJ):
            groupes[-1] += c
            colle = c == _ZWJ
        elif (
            groupes
            and "\U0001f1e6" <= c <= "\U0001f1ff"
            and len(groupes[-1]) == 1
            and "\U0001f1e6" <= groupes[-1] <= "\U0001f1ff"
        ):
            groupes[-1] += c
        else:
            groupes.append(c)
            colle = False
    return groupes


def _genre_graphe(g: str) -> str:
    c = g[0]
    if c.isspace():
        return "e"
    if c.isalnum() or c == "_":
        return "m"
    return "p"


def _decouper(texte: str) -> list[str]:
    """Mots et ponctuation, chacun précédé de ses espaces (une espace finale reste à part)."""
    elements: list[str] = []
    precedent = ""  # genre du dernier groupe lu
    for g in _graphemes(texte):
        genre = _genre_graphe(g)
        if genre == "e":
            if precedent == "e":
                elements[-1] += g
            else:
                elements.append(g)
        elif precedent == "e" or (genre == "m" and precedent == "m"):
            elements[-1] += g
        else:
            elements.append(g)
        precedent = genre
    return elements


def _phrases(texte: str) -> list[str]:
    return [p for p in _PHRASES.findall(texte) if p]


def _ajouter(segments: list[Segment], genre: Genre, elements: list[str]) -> None:
    texte = "".join(elements)
    if not texte:
        return
    if segments and segments[-1]["type"] == genre:
        segments[-1]["texte"] += texte
    else:
        segments.append({"type": genre, "texte": texte})


def _comparer(a: list[str], b: list[str], segments: list[Segment], *, plus_fin: bool) -> None:
    """Ajoute les segments de `a` vers `b` ; `plus_fin` : raffiner les blocs modifiés par mots."""
    ka = [_cle(x) for x in a]
    kb = [_cle(x) for x in b]
    debut = 0
    limite = min(len(a), len(b))
    while debut < limite and ka[debut] == kb[debut]:
        debut += 1
    fin = 0
    while fin < limite - debut and ka[-1 - fin] == kb[-1 - fin]:
        fin += 1
    _ajouter(segments, EGAL, a[:debut])
    fin_a, fin_b = len(a) - fin, len(b) - fin
    if (fin_a - debut) * (fin_b - debut) > LIMITE_PRODUIT:
        _ajouter(segments, SUPPRESSION, a[debut:fin_a])
        _ajouter(segments, AJOUT, b[debut:fin_b])
    else:
        comparaison = SequenceMatcher(None, ka[debut:fin_a], kb[debut:fin_b], autojunk=False)
        for operation, i1, i2, j1, j2 in comparaison.get_opcodes():
            bloc_a, bloc_b = a[debut + i1 : debut + i2], b[debut + j1 : debut + j2]
            if operation == "equal":
                _ajouter(segments, EGAL, bloc_a)
            elif plus_fin and bloc_a and bloc_b:
                _comparer(
                    _decouper("".join(bloc_a)),
                    _decouper("".join(bloc_b)),
                    segments,
                    plus_fin=False,
                )
            else:
                _ajouter(segments, SUPPRESSION, bloc_a)
                _ajouter(segments, AJOUT, bloc_b)
    _ajouter(segments, EGAL, a[fin_a:])


def calculer(avant: str, apres: str) -> list[Segment]:
    """Segments `{"type": "egal"|"ajout"|"suppression", "texte": str}` consécutifs et fusionnés."""
    # NFC : « é » composé ou décomposé est le même mot.
    texte_a = unicodedata.normalize("NFC", avant)
    texte_b = unicodedata.normalize("NFC", apres)
    segments: list[Segment] = []
    _comparer(_phrases(texte_a), _phrases(texte_b), segments, plus_fin=True)
    return segments


def identiques(segments: list[Segment]) -> bool:
    """Vrai quand aucune insertion ni suppression n'est marquée."""
    return all(s["type"] == EGAL for s in segments)
