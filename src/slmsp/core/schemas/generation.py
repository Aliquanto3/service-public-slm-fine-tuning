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

from pydantic import (
    Field,
    SerializerFunctionWrapHandler,
    ValidationError,
    field_validator,
    model_serializer,
)

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
    tronquee: bool | None = None
    """Sortie coupée : le `Fin` du flux a la raison `longueur` (`finish_reason` `length` de
    llama-server, sur au moins un appel pour un CR découpé) ou `boucle` (garde-fou anti-boucle
    du Harnais, story 16.3).
    `None` pour une ligne écrite avant ce champ (report W2) ; une sortie tronquée garde le
    statut `ok`. Hors de `sortie_canonique`, il n'entre pas dans la clé du cache des verdicts."""

    verdict_passages: Literal["oui", "non", "illisible"] | None = None
    """Verdict de la vérification des passages de Q (story 16.8), recopié de l'évènement
    `verification-passages` de la trace ; `None` sans vérification (abstention désactivée,
    autre Tâche, ligne antérieure). Hors de `sortie_canonique`, hors de la clé du cache."""

    @model_serializer(mode="wrap")
    def _omettre_verdict_absent(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """`verdict_passages` absent de la ligne quand il vaut `None` : abstention désactivée,
        lignes identiques à celles d'avant la story 16.8."""
        donnees = handler(self)
        if donnees.get("verdict_passages") is None:
            donnees.pop("verdict_passages", None)
        return donnees

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
