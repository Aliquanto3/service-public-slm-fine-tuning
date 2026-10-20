"""Jeu à cibles sélectionnées (story 15.3, O3) : preuve de la chaîne contre le jeu source.

`verifier_selection` prouve qu'un `train.jsonl` n'est que le jeu source où, dans l'ordre :

- les lignes des Tâches ni sélectionnées ni retirées sont copiées à l'octet près ;
- chaque ligne d'une Tâche sélectionnée est copiée à l'octet près (gagnant Mistral), remplacée
  par une ligne v2 de même session, même entrée (messages avant la cible) et mêmes outils
  (gagnant de la base locale), ou absente (écartée) ;
- les lignes des Tâches retirées sont absentes.

Aucune ligne n'est réécrite ici (D1). Placé dans `core` : partagé par `data` (écriture) et
`train` (relecture au chargement), comme `core.sous_ensemble`. La cible d'une ligne v2 est
recontrôlée à part, contre le journal local (`train.chargement.recontroler_cibles`).
"""

from __future__ import annotations

import json
from collections.abc import Collection
from typing import Any

from slmsp.core.erreurs import ProvenanceInvalide

__all__ = ["verifier_selection"]


def _lignes(octets: bytes) -> list[bytes]:
    return [texte for texte in octets.split(b"\n") if texte.strip()]


def _session(ligne: dict[str, Any]) -> Any:
    return (ligne.get("meta") or {}).get("session_id")


def verifier_selection(
    octets: bytes, source: bytes, taches: Collection[str], retirees: Collection[str]
) -> None:
    """Lève `ProvenanceInvalide` si `octets` n'est pas une sélection de `source` (voir module)."""
    sorties = _lignes(octets)
    if octets != b"".join(ligne + b"\n" for ligne in sorties):
        raise ProvenanceInvalide("jeu sélectionné : une ligne JSON par exemple, LF final attendu")
    lignes_source = _lignes(source)
    rang = 0
    for numero, brute in enumerate(sorties, start=1):
        ligne = json.loads(brute)
        origine: dict[str, Any] | None = None
        while rang < len(lignes_source):
            candidate = json.loads(lignes_source[rang])
            rang += 1
            if _session(candidate) == _session(ligne) and candidate.get("tache") == ligne.get(
                "tache"
            ):
                origine = candidate
                break
            if candidate.get("tache") not in taches and candidate.get("tache") not in retirees:
                raise ProvenanceInvalide(
                    f"jeu sélectionné : ligne source {rang} (Tâche {candidate.get('tache')}) "
                    "absente alors que sa Tâche n'est ni sélectionnée ni retirée"
                )
        if origine is None:
            raise ProvenanceInvalide(
                f"jeu sélectionné : ligne {numero} hors du jeu source ou dans le désordre"
            )
        tache = origine.get("tache")
        if tache in retirees:
            raise ProvenanceInvalide(f"jeu sélectionné : ligne {numero} d'une Tâche retirée")
        if brute == lignes_source[rang - 1]:
            continue
        if (
            tache not in taches
            or ligne.get("schema_version") != 2
            or ligne.get("messages", [])[:-1] != origine.get("messages", [])[:-1]
            or (ligne.get("tools") or []) != (origine.get("tools") or [])
        ):
            raise ProvenanceInvalide(
                f"jeu sélectionné : ligne {numero} ni copiée de la source, ni cible sélectionnée "
                "de même entrée"
            )
    for reste in lignes_source[rang:]:
        tache = json.loads(reste).get("tache")
        if tache not in taches and tache not in retirees:
            raise ProvenanceInvalide(
                f"jeu sélectionné : ligne source de Tâche {tache} absente du jeu"
            )
