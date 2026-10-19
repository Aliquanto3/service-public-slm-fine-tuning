"""Sous-ensemble d'un jeu SFT par Tâche : sélection pure et preuve.

`lignes_de_taches` extrait d'un `train.jsonl` les lignes (octets inchangés, ordre conservé)
des Tâches demandées ; `verifier_sous_ensemble` prouve qu'un jeu restreint n'est que cela.
Aucune ligne n'est réécrite (D1). Placé dans `core` : partagé par `data` (écriture) et
`train` (relecture au chargement).
"""

from __future__ import annotations

import json
from collections.abc import Collection

from slmsp.core.erreurs import ProvenanceInvalide

__all__ = ["lignes_de_taches", "verifier_sous_ensemble"]


def lignes_de_taches(source: bytes, taches: Collection[str]) -> list[bytes]:
    """Lignes (sans saut de ligne final) de `source` dont la clé `tache` est dans `taches`."""
    gardees: list[bytes] = []
    for texte in source.split(b"\n"):
        if texte.strip() and json.loads(texte).get("tache") in taches:
            gardees.append(texte)
    return gardees


def verifier_sous_ensemble(octets: bytes, source: bytes, taches: Collection[str]) -> None:
    """Lève `ProvenanceInvalide` si `octets` n'est pas exactement le sous-ensemble de `source`."""
    attendu = b"".join(ligne + b"\n" for ligne in lignes_de_taches(source, taches))
    if octets != attendu:
        raise ProvenanceInvalide(
            "jeu restreint : train.jsonl n'est pas le sous-ensemble du jeu source "
            f"pour les Tâches {', '.join(sorted(taches))}"
        )
