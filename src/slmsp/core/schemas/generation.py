"""Ligne `Generation` de `generations.jsonl`, phase génération du banc (AD-13, FR-25).

Une ligne par item du Jeu d'évaluation, en ajout seul. `sortie_canonique` est la seule
partie jugée par la notation (story 5.6) : texte généré, appels d'outils (sans leur `id`)
et sources citées, sans aucune durée ni identifiant aléatoire, pour qu'un même modèle
déterministe donne la même sortie à l'octet près. `trace` garde le flux complet des
évènements (`core.evenements.vers_dict`), avertissements du Bac à sable compris ; la
durée de génération est à part (`duree_ms`).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, ValidationError, field_validator

from slmsp.core.evenements import Source, depuis_dict
from slmsp.core.schemas import SchemaBase, SousSchema

CodeTache = Literal["Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR"]


class AppelCanonique(SousSchema):
    """Appel d'outil émis par le modèle : nom et arguments, sans l'`id` de l'appel."""

    nom: str
    arguments: dict[str, Any]


class SortieCanonique(SousSchema):
    """Sortie jugée d'un item : texte, appels d'outils et sources citées."""

    texte: str
    appels_outils: list[AppelCanonique] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)


class Generation(SchemaBase):
    """Une ligne de `runs/eval-generation/<run_id>/generations.jsonl`."""

    schema_version: Literal[1] = 1
    item_id: str
    tache: CodeTache
    statut: Literal["ok", "erreur"]
    sortie_canonique: SortieCanonique
    trace: list[dict[str, Any]]
    """Évènements du flux en dicts (`vers_dict`), jetons consécutifs fusionnés."""
    duree_ms: int = Field(ge=0)

    @field_validator("trace")
    @classmethod
    def _evenements_valides(cls, trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for rang, evenement in enumerate(trace):
            try:
                depuis_dict(evenement)
            except ValidationError as exc:
                erreurs = exc.error_count()
                raise ValueError(f"évènement {rang} invalide : {erreurs} erreur(s)") from None
        return trace
