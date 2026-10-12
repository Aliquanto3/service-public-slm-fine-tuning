"""Découpage des textes longs en morceaux qui tiennent dans un budget de tokens (story 4.4).

Fonctions pures : le résultat ne dépend que du texte, de `mesurer`, du budget et du
chevauchement. `mesurer(texte)` donne la taille, en tokens, de ce qui serait envoyé au
modèle pour ce texte (le traitement des comptes rendus mesure les messages `CR-morceau`
complets par `LlmPort.compter_tokens`).

Règles :

- Un paragraphe est un bloc séparé des autres par une ligne vide ; ses blancs de début et
  de fin sont retirés. Les morceaux sont faits de paragraphes entiers, joints par une
  ligne vide, empaquetés de façon gloutonne dans l'ordre du texte.
- Aucune troncature : un paragraphe plus grand que le budget est redécoupé en lignes, puis
  en phrases, puis en mots. Seul un mot isolé plus grand que le budget est gardé tel quel
  (le dépassement reste visible côté serveur).
- Chevauchement : les `chevauchement` dernières unités nouvelles du morceau i ouvrent le
  morceau i+1. Il est réduit, jusqu'à zéro, quand il empêcherait d'ajouter au moins une
  unité nouvelle dans le budget : le découpage avance toujours.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Final

JOINT_PARAGRAPHES: Final = "\n\n"
JOINT_LIGNES: Final = "\n"
JOINT_MOTS: Final = " "

_LIGNE_VIDE: Final = re.compile(r"\n[^\S\n]*(?:\n[^\S\n]*)+")
"""Ligne vide : seulement des blancs, Unicode compris (espace insécable, etc.)."""
_FIN_DE_PHRASE: Final = re.compile(r"(?<=[.!?…])\s+")


def paragraphes(texte: str) -> list[str]:
    """Blocs de `texte` séparés par une ligne vide, blancs de bord retirés, vides exclus."""
    normalise = texte.replace("\r\n", "\n").replace("\r", "\n")
    return [bloc.strip() for bloc in _LIGNE_VIDE.split(normalise) if bloc.strip()]


def empaqueter[T](
    unites: Sequence[T], mesurer: Callable[[Sequence[T]], int], budget: int
) -> list[list[T]]:
    """Groupes consécutifs d'`unites`, chacun aussi grand que possible sous `budget`.

    `mesurer` reçoit un groupe candidat. Une unité seule plus grande que le budget forme
    son propre groupe. Lève `ValueError` si `budget <= 0`.
    """
    _verifier_budget(budget)
    groupes: list[list[T]] = []
    courant: list[T] = []
    for unite in unites:
        if courant and mesurer([*courant, unite]) <= budget:
            courant.append(unite)
            continue
        if courant:
            groupes.append(courant)
        courant = [unite]
    if courant:
        groupes.append(courant)
    return groupes


def regrouper(
    unites: Sequence[str], mesurer: Callable[[str], int], budget: int, *, joint: str
) -> list[list[str]]:
    """`empaqueter` sur des textes : un groupe est mesuré joint par `joint`."""
    return empaqueter(unites, lambda groupe: mesurer(joint.join(groupe)), budget)


def _scinder(texte: str, mesurer: Callable[[str], int], budget: int, niveau: int) -> list[str]:
    """Morceaux de `texte` sous le budget, en descendant lignes → phrases → mots."""
    if mesurer(texte) <= budget:
        return [texte]
    niveaux: tuple[tuple[Callable[[str], list[str]], str], ...] = (
        (lambda t: [ligne.strip() for ligne in t.split("\n") if ligne.strip()], JOINT_LIGNES),
        (lambda t: [p.strip() for p in _FIN_DE_PHRASE.split(t) if p.strip()], JOINT_MOTS),
        (lambda t: t.split(), JOINT_MOTS),
    )
    for indice in range(niveau, len(niveaux)):
        separer, joint = niveaux[indice]
        parties = separer(texte)
        if len(parties) > 1:
            pieces = [
                p for partie in parties for p in _scinder(partie, mesurer, budget, indice + 1)
            ]
            return [joint.join(g) for g in regrouper(pieces, mesurer, budget, joint=joint)]
    return [texte]


def _verifier_budget(budget: int) -> None:
    if budget <= 0:
        raise ValueError(f"budget de découpage invalide : {budget} (attendu > 0)")


def decouper(
    texte: str, mesurer: Callable[[str], int], budget: int, chevauchement: int = 0
) -> list[str]:
    """Morceaux de `texte`, chacun mesuré `<= budget` (sauf un mot isolé trop grand).

    Coupe entre paragraphes ; reprend au début de chaque morceau les `chevauchement`
    dernières unités nouvelles du précédent (réduit si nécessaire pour avancer). Même
    entrée, mêmes morceaux. Lève `ValueError` si `budget <= 0` ou `chevauchement < 0`.
    """
    _verifier_budget(budget)
    if chevauchement < 0:
        raise ValueError(f"chevauchement invalide : {chevauchement} (attendu >= 0)")
    unites = [piece for bloc in paragraphes(texte) for piece in _scinder(bloc, mesurer, budget, 0)]

    def tient(debut: int, fin: int) -> bool:
        return mesurer(JOINT_PARAGRAPHES.join(unites[debut:fin])) <= budget

    morceaux: list[str] = []
    suivant = 0  # première unité pas encore couverte
    nouvelles = 0  # unités nouvelles du morceau précédent
    while suivant < len(unites):
        for reprise in range(min(chevauchement, nouvelles), -1, -1):
            debut = suivant - reprise
            if reprise and not tient(debut, suivant + 1):
                continue  # chevauchement réduit : il empêcherait d'avancer
            fin = suivant + 1
            while fin < len(unites) and tient(debut, fin + 1):
                fin += 1
            break
        morceaux.append(JOINT_PARAGRAPHES.join(unites[debut:fin]))
        nouvelles = fin - suivant
        suivant = fin
    return morceaux


__all__ = [
    "JOINT_LIGNES",
    "JOINT_MOTS",
    "JOINT_PARAGRAPHES",
    "decouper",
    "empaqueter",
    "paragraphes",
    "regrouper",
]
