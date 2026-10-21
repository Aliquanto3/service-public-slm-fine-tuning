"""Garde-fou anti-boucle du décodage (story 16.3, levier 5 du diagnostic D0).

Arrêt déterministe d'une sortie qui boucle, sans pénalité de répétition : les options de
décodage ne changent pas, et une sortie qui ne boucle pas reste identique octet pour octet.
Deux critères, seuils dans `[anti_boucle]` de `config/harnais.toml` (`ConfigAntiBoucle`) :

- **ligne** : une même ligne non vide (comparée sans ses blancs de bord, et seulement si elle
  porte au moins un caractère alphanumérique) revient plus de `repetitions_ligne_max` fois ;
  la coupure tombe au début de cette ligne, qui n'est jamais émise ;
- **n-grammes** : sur les `fenetre_mots` derniers mots, la part des `taille_ngramme`-grammes
  déjà vus dans la fenêtre dépasse `part_ngrammes_max` ; la coupure tombe au début de la
  ligne du mot qui déclenche, ou au texte déjà émis s'il va plus loin : ce critère ne retient
  aucun jeton, la sortie relayée peut donc garder le début de la ligne en cours.

Les mots sans caractère alphanumérique (`|`, `---`, `........`, `***`) ne comptent pas pour les
n-grammes, comme les lignes qui n'en portent aucun pour le critère des lignes : séparateurs de
tableaux Markdown et pointillés d'un formulaire ne déclenchent jamais.

Périmètre : le garde-fou n'agit que dans le Harnais (`AssistantService._flux`), donc à
l'évaluation (`evaluation.generation`) et dans l'application. Les appels directs au
`LlmPort` hors Harnais n'en ont pas : `data/candidats.py`, `data/preferences.py`,
`benchmarks/moteurs/llm.py` (génération de données et bancs bruts, raisons de fin inchangées).

`DetecteurBoucle` est incrémental et pur (texte en entrée, position de coupure en sortie) : le
même code sert au flux du Harnais (`borner_boucles`, évaluation et application) et au rejeu
hors ligne (`point_de_coupure`). `borner_boucles` retient les seuls `Jeton` d'une ligne qui
pourrait devenir une répétition de trop, et les rend inchangés dès qu'elle s'en écarte ; sur
coupure, il émet exactement le texte jusqu'à la coupure (le dernier `Jeton` tronqué si besoin)
puis `Fin(raison="boucle")`. Un flux épuisé sans `Fin` ni `Erreur` rend ses jetons retenus.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterator
from typing import Final

from slmsp.core.evenements import Erreur, Evenement, Fin, Jeton
from slmsp.harness.config import ConfigAntiBoucle

__all__ = ["RAISON_BOUCLE", "DetecteurBoucle", "borner_boucles", "point_de_coupure"]

RAISON_BOUCLE: Final = "boucle"
_MOT: Final = re.compile(r"\S+")
_ALPHANUM: Final = re.compile(r"\w")


class DetecteurBoucle:
    """Détecteur incrémental : `ajouter(morceau)` rend la position de coupure, ou `None`."""

    def __init__(self, config: ConfigAntiBoucle) -> None:
        self._config = config
        self._texte = ""
        self._debut_ligne = 0
        self._fin_mots = 0
        self._comptes: Counter[str] = Counter()
        self._satures: set[str] = set()
        self._mots: list[str] = []
        self.coupure: int | None = None

    def ajouter(self, morceau: str) -> int | None:
        """Ajoute `morceau` au texte reçu ; position (dans tout le texte) de la coupure."""
        if self.coupure is not None:
            return self.coupure
        depart = len(self._texte)
        self._texte += morceau
        while (fin := self._texte.find("\n", max(depart, self._debut_ligne))) != -1:
            if (coupure := self._mots_jusqua(fin)) is not None or (
                coupure := self._ligne(self._debut_ligne, fin)
            ) is not None:
                self.coupure = coupure
                return coupure
            self._debut_ligne = fin + 1
            depart = fin + 1
        dernier_blanc = max(self._texte.rfind(c) for c in (" ", "\t", "\r"))
        if dernier_blanc >= self._fin_mots:
            self.coupure = self._mots_jusqua(dernier_blanc)
        return self.coupure

    def retenir_depuis(self) -> int:
        """Position à partir de laquelle le texte reçu ne doit pas encore être émis.

        C'est le début de la ligne en cours si elle peut encore devenir une répétition de
        trop (préfixe d'une ligne déjà vue `repetitions_ligne_max` fois), sinon la fin du texte.
        """
        # Comparée sans blancs de bord, comme les clés : une ligne suivie d'espaces ou d'un
        # retour chariot (CRLF) reste retenue, et la ligne de trop n'est jamais émise.
        partielle = self._texte[self._debut_ligne :].strip()
        if any(cle.startswith(partielle) for cle in self._satures):
            return self._debut_ligne
        return len(self._texte)

    def _ligne(self, debut: int, fin: int) -> int | None:
        cle = self._texte[debut:fin].strip()
        if not _ALPHANUM.search(cle):
            return None
        self._comptes[cle] += 1
        if self._comptes[cle] > self._config.repetitions_ligne_max:
            return debut
        if self._comptes[cle] == self._config.repetitions_ligne_max:
            self._satures.add(cle)
        return None

    def _mots_jusqua(self, limite: int) -> int | None:
        """Compte les mots complets de `[_fin_mots, limite)` ; coupure n-grammes éventuelle."""
        config = self._config
        for trouve in _MOT.finditer(self._texte, self._fin_mots, limite):
            if not _ALPHANUM.search(trouve.group()):
                continue
            self._mots.append(trouve.group())
            fenetre = self._mots[-config.fenetre_mots :]
            if len(fenetre) < config.fenetre_mots:
                continue
            n = config.taille_ngramme
            grammes = [tuple(fenetre[i : i + n]) for i in range(len(fenetre) - n + 1)]
            repetes = len(grammes) - len(set(grammes))
            del self._mots[: -config.fenetre_mots]
            if repetes / len(grammes) > config.part_ngrammes_max:
                self._fin_mots = limite
                return self._texte.rfind("\n", 0, trouve.start()) + 1
        self._fin_mots = limite
        return None


def point_de_coupure(texte: str, config: ConfigAntiBoucle) -> int | None:
    """Position où le garde-fou couperait `texte` reçu d'un bloc (rejeu hors ligne)."""
    return DetecteurBoucle(config).ajouter(texte)


def borner_boucles(flux: Iterator[Evenement], config: ConfigAntiBoucle) -> Iterator[Evenement]:
    """Relaie `flux` ; sur boucle, coupe le texte et termine par `Fin(raison="boucle")`.

    Inactif (`config.actif` faux), le flux est relayé tel quel. L'appelant ferme `flux`.
    """
    if not config.actif:
        yield from flux
        return
    detecteur = DetecteurBoucle(config)
    retenus: list[Jeton] = []
    emis = 0
    for evenement in flux:
        if not isinstance(evenement, Jeton):
            yield from retenus
            retenus.clear()
            yield evenement
            if isinstance(evenement, Fin | Erreur):
                return
            continue
        retenus.append(evenement)
        coupure = detecteur.ajouter(evenement.texte)
        limite = detecteur.retenir_depuis() if coupure is None else max(coupure, emis)
        while retenus and emis + len(retenus[0].texte) <= limite:
            jeton = retenus.pop(0)
            emis += len(jeton.texte)
            yield jeton
        if coupure is not None:
            if retenus and limite > emis:
                yield Jeton(texte=retenus[0].texte[: limite - emis])
            yield Fin(raison=RAISON_BOUCLE)
            return
    yield from retenus
