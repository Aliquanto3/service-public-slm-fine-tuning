"""Entrée du journal des Requêtes sortantes (AD-4, story 1.4).

Chaque requête vue par la passerelle réseau (`slmsp.net`) donne exactement une entrée :
envoyée, échouée ou bloquée. L'entrée ne contient ni URL complète, ni en-tête, ni corps
(hors `termes` d'un appel d'outil), ni secret.
"""

from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, ConfigDict

from slmsp.core.ports import Mode
from slmsp.core.schemas import SchemaBase

StatutRequete = Literal["envoyee", "echouee", "bloquee-liste", "bloquee-mode"]
"""Issue d'une requête : partie, partie en erreur, refusée par profil ou par Mode."""

ProfilReseau = Literal["assistant", "outillage", "aucun", "eval-distant", "modele-externe"]
"""Profils de la passerelle (AD-4) ; `eval-distant` : génération d'un modèle distant (17.1) ;
`modele-externe` : modèle externe de l'application, règle calculée au lancement (17.4)."""


class EntreeJournalRequetes(SchemaBase):
    """Une Requête sortante, envoyée ou bloquée (schéma figé)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    horodatage: AwareDatetime
    profil: ProfilReseau
    hote: str
    methode: str
    outil: str | None = None
    termes: str | None = None
    """Arguments de l'appel d'outil, en JSON canonique."""
    statut: StatutRequete
    mode: Mode | None = None
