"""Lecture tolérante d'une sortie JSON de modèle (bloc de code, texte autour).

Partagée par le juge tiers (`slmsp.judge.tiers`) et le juge de données
(`slmsp.data.juge_donnees`) : `data` ne peut pas importer `slmsp.judge` (AD-1).
"""

from __future__ import annotations

import json

__all__ = ["extraire_json"]


def _objet_equilibre(texte: str, debut: int) -> str | None:
    """Objet JSON `{…}` commençant à `debut` (accolades équilibrées, chaînes comprises)."""
    profondeur, dans_chaine, echappe = 0, False, False
    for position in range(debut, len(texte)):
        car = texte[position]
        if dans_chaine:
            if echappe:
                echappe = False
            elif car == "\\":
                echappe = True
            elif car == '"':
                dans_chaine = False
        elif car == '"':
            dans_chaine = True
        elif car == "{":
            profondeur += 1
        elif car == "}":
            profondeur -= 1
            if profondeur == 0:
                return texte[debut : position + 1]
    return None


def extraire_json(texte: str) -> str | None:
    """Texte JSON d'une sortie, toléré dans un bloc de code ou entouré de texte.

    Sortie entière si elle se lit telle quelle ; sinon premier objet `{…}` lisible ; `None`
    si aucun. Le Juge principal garde sa lecture stricte.
    """
    brut = texte.strip()
    try:
        json.loads(brut)
        return brut
    except ValueError:
        pass
    debut = brut.find("{")
    while debut != -1:
        candidat = _objet_equilibre(brut, debut)
        if candidat is not None:
            try:
                json.loads(candidat)
                return candidat
            except ValueError:
                pass
        debut = brut.find("{", debut + 1)
    return None
