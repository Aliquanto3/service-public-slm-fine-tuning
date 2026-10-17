"""Hiérarchie unique des erreurs de `slmsp` et codes de sortie de la CLI.

Chaque sous-classe de `SlmspError` porte son `code_sortie` ; la CLI convertit toute
`SlmspError` non rattrapée en ce code, avec un message sans trace technique. Un message
d'erreur ne cite jamais la valeur d'un secret.
"""

from __future__ import annotations

from enum import IntEnum
from typing import ClassVar


class CodeSortie(IntEnum):
    """Codes de sortie de la CLI (Consistency Conventions du spine)."""

    SUCCES = 0
    ERREUR = 1
    USAGE = 2
    BUDGET_EPUISE = 3
    MANIFESTE_INVALIDE = 4
    RESSOURCE_OCCUPEE = 5


class SlmspError(Exception):
    """Racine de toutes les erreurs métier de `slmsp`."""

    code_sortie: ClassVar[CodeSortie] = CodeSortie.ERREUR


class BudgetEpuise(SlmspError):
    """Le plafond d'un poste ou d'un sous-poste de budget serait dépassé."""

    code_sortie = CodeSortie.BUDGET_EPUISE


class ManifesteInvalide(SlmspError):
    """Un manifeste (run, jeu, données) est absent, illisible ou incohérent."""

    code_sortie = CodeSortie.MANIFESTE_INVALIDE


class RessourceOccupee(SlmspError):
    """Une ressource exclusive de la machine (verrou GPU…) est détenue par un autre processus."""

    code_sortie = CodeSortie.RESSOURCE_OCCUPEE

    def __init__(self, message: str, *, pid: int | None = None, commande: str | None = None):
        super().__init__(message)
        self.pid = pid
        self.commande = commande


class HoteBloque(SlmspError):
    """Requête refusée par la passerelle réseau (hôte hors liste, Mode hors ligne)."""


class AppelNonConforme(SlmspError):
    """Appel d'outil ou d'API qui ne respecte pas le contrat attendu."""


class SchemaOutilModifie(SlmspError):
    """Le schéma d'un outil MCP a changé par rapport à sa référence."""


class SourceSansLicence(SlmspError):
    """Une source est utilisée sans licence inscrite au registre."""


class ProvenanceInvalide(SlmspError):
    """La provenance d'un artefact ne peut être établie ou ne convient pas."""


class ReponseTronquee(ProvenanceInvalide):
    """Une réponse Mistral s'est arrêtée sur `finish_reason = length` : texte incomplet."""


class LectureInterdite(SlmspError):
    """Lecture refusée par le lecteur contrôlé."""


class TarifInconnu(SlmspError):
    """Aucun tarif connu pour le modèle ou le mode demandé (jamais de tarif par défaut)."""


class ConfigurationInvalide(SlmspError):
    """Fichier de configuration absent, illisible ou non conforme à son modèle."""


class SecretManquant(SlmspError):
    """Secret absent ou vide dans le fichier `.env` (le message ne cite aucune valeur)."""


class ContexteDepasse(SlmspError):
    """Le prompt et la sortie réservée ne tiennent pas dans le contexte du Modèle (correctif F2).

    Levée par le Harnais quand même un prompt sans passage dépasse le budget, et par le
    client llama-server (sous-classe `ContexteServeurDepasse`) quand le serveur refuse la
    requête pour dépassement de contexte. Le service la rend en évènement `contexte-depasse`.
    """
