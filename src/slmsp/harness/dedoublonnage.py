"""Dédoublonnage du préfixe commun des passages d'une même page (story 16.2, harnais v2).

Les chunks d'une page de l'Index commencent tous par le même titre et la même introduction.
À l'assemblage (sans reconstruire l'Index), le préfixe n'est gardé que dans le premier passage
de la page ; il est retiré des suivants. Les `Passage` ne portent pas de métadonnée de
préfixe : il est déduit du plus long préfixe commun aux textes de la page, coupé sur une
limite de ligne ou de mot, et ignoré sous `prefixe_min`. L'ordre des passages est inchangé.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import replace

from slmsp.core.ports import Passage


def _prefixe_commun(textes: Sequence[str]) -> str:
    """Plus long préfixe commun, coupé sur une limite de mot (blanc ou fin de texte)."""
    commun = os.path.commonprefix(list(textes))
    # Le préfixe est gardé entier s'il s'arrête, dans chaque texte, sur un blanc ou sur la
    # fin du texte ; sinon il est coupé après son dernier blanc (ligne ou espace), y compris
    # quand un texte est entièrement le préfixe d'un autre (« …ABCDE » / « …ABCDEF fin »).
    if all(len(t) == len(commun) or t[len(commun)].isspace() for t in textes):
        return commun
    coupe = max(commun.rfind("\n"), commun.rfind(" "))
    return commun[: coupe + 1] if coupe > 0 else ""


def dedoublonner_prefixes(passages: Sequence[Passage], prefixe_min: int) -> list[Passage]:
    """Passages dont le préfixe commun de leur page est retiré, sauf du premier de chaque page."""
    pages: dict[str, list[int]] = {}
    for rang, passage in enumerate(passages):
        pages.setdefault(passage.doc_id, []).append(rang)
    resultat = list(passages)
    for rangs in pages.values():
        if len(rangs) < 2:
            continue
        prefixe = _prefixe_commun([passages[r].texte for r in rangs])
        if len(prefixe.strip()) < prefixe_min:
            continue
        for rang in rangs[1:]:
            reste = passages[rang].texte[len(prefixe) :].lstrip()
            if reste:  # un passage réduit au préfixe reste intact
                resultat[rang] = replace(passages[rang], texte=reste)
    return resultat


__all__ = ["dedoublonner_prefixes"]
