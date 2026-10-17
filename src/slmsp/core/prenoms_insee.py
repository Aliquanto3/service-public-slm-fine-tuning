"""Sélection des prénoms du fichier national de l'INSEE (story 12.3).

Fonction pure, partagée par `slmsp fetch prenoms` (qui génère `app/ressources/prenoms.txt`) et
par `app.anonymisation` (qui le relit) : `core` est la seule couche qu'ils partagent.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

OCCURRENCES_MINIMALES = 20  # prénoms INSEE retenus : au moins autant de naissances cumulées


def prenoms_depuis_csv_insee(
    lignes: Iterable[str], *, minimum: int = OCCURRENCES_MINIMALES
) -> list[str]:
    """Prénoms distincts du fichier INSEE (`sexe;preusuel;annais;nombre`), triés.

    Écarte `_PRENOMS_RARES`, les prénoms de moins de 3 lettres et ceux qui totalisent moins de
    `minimum` naissances (mots courants rares). Sert à produire `ressources/prenoms.txt`.
    """
    totaux: Counter[str] = Counter()
    for numero, ligne in enumerate(lignes):
        champs = ligne.strip().split(";")
        if numero == 0 or len(champs) < 4 or not champs[3].isdigit():
            continue
        prenom = champs[1].strip()
        if prenom and not prenom.startswith("_") and len(prenom) > 2:
            totaux[prenom.lower()] += int(champs[3])
    return sorted(prenom for prenom, total in totaux.items() if total >= minimum)
