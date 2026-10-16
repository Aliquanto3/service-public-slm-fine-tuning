"""Différences par mots entre un texte et sa correction (story 13.1, FR-17, UX-DR13).

Calcul pur, sans dépendance (`difflib`). Les deux textes sont normalisés en NFC puis
découpés en mots, espaces et
signes de ponctuation ; les espaces sont des éléments à part entière, donc la concaténation des
segments « égal » et « suppression » redonne `avant` (en NFC), et celle des segments « égal » et
« ajout » redonne `apres`.

Coût borné : le préfixe et le suffixe communs sont retirés d'abord, puis, si le produit des
tailles restantes dépasse `LIMITE_PRODUIT`, le milieu est rendu comme un seul bloc supprimé
suivi d'un seul bloc ajouté (résultat grossier mais exact, jamais d'explosion quadratique).
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Final, Literal, TypedDict

EGAL: Final = "egal"
AJOUT: Final = "ajout"
SUPPRESSION: Final = "suppression"
LIMITE_PRODUIT: Final = 4_000_000  # ~2 000 x 2 000 éléments : quelques secondes au pire
_ELEMENTS: Final = re.compile(r"\s+|\w+|[^\w\s]", re.UNICODE)

Genre = Literal["egal", "ajout", "suppression"]


class Segment(TypedDict):
    type: Genre
    texte: str


def _decouper(texte: str) -> list[str]:
    return _ELEMENTS.findall(texte)


def _ajouter(segments: list[Segment], genre: Genre, elements: list[str]) -> None:
    texte = "".join(elements)
    if not texte:
        return
    if segments and segments[-1]["type"] == genre:
        segments[-1]["texte"] += texte
    else:
        segments.append({"type": genre, "texte": texte})


def calculer(avant: str, apres: str) -> list[Segment]:
    """Segments `{"type": "egal"|"ajout"|"suppression", "texte": str}` consécutifs et fusionnés."""
    # NFC : « é » composé ou décomposé est le même mot (et une marque combinante reste collée).
    a = _decouper(unicodedata.normalize("NFC", avant))
    b = _decouper(unicodedata.normalize("NFC", apres))
    ka, kb = a, b
    debut = 0
    while debut < min(len(a), len(b)) and ka[debut] == kb[debut]:
        debut += 1
    fin = 0
    while fin < min(len(a), len(b)) - debut and ka[-1 - fin] == kb[-1 - fin]:
        fin += 1
    milieu_a, milieu_b = slice(debut, len(a) - fin), slice(debut, len(b) - fin)
    segments: list[Segment] = []
    _ajouter(segments, EGAL, a[:debut])
    if (len(a) - fin - debut) * (len(b) - fin - debut) > LIMITE_PRODUIT:
        _ajouter(segments, SUPPRESSION, a[milieu_a])
        _ajouter(segments, AJOUT, b[milieu_b])
    else:
        comparaison = SequenceMatcher(None, ka[milieu_a], kb[milieu_b], autojunk=False)
        base_a, base_b = milieu_a.start, milieu_b.start
        for operation, i1, i2, j1, j2 in comparaison.get_opcodes():
            if operation == "equal":
                _ajouter(segments, EGAL, a[base_a + i1 : base_a + i2])
            else:
                _ajouter(segments, SUPPRESSION, a[base_a + i1 : base_a + i2])
                _ajouter(segments, AJOUT, b[base_b + j1 : base_b + j2])
    _ajouter(segments, EGAL, a[len(a) - fin :])
    return segments


def identiques(segments: list[Segment]) -> bool:
    """Vrai quand aucune insertion ni suppression n'est marquée."""
    return all(s["type"] == EGAL for s in segments)
