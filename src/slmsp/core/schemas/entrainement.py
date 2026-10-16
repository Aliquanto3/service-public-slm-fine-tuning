"""Jeu d'entraînement versionné `data/train/vN/` (story 9.6, AD-25, FR-29).

`train.jsonl` : une `LigneEntrainement` par exemple, en JSON canonique. `MANIFEST.json` :
`ManifesteJeuEntrainement`, écrit une fois avec le jeu (une version n'est jamais réécrite).
Les lignes ne sont jamais écrites à la main : elles sont refabriquées à partir des réponses
Mistral journalisées par `slmsp.data.build` (D1.1, AD-3 verrou 4).
"""

from __future__ import annotations

from datetime import date as Jour
from typing import Annotated, Any, Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from slmsp.core.messages import ConversationInvalide, valider_conversation
from slmsp.core.schemas import SchemaBase, Sha256, SousSchema
from slmsp.core.schemas.run import MOTIF_RUN_ID
from slmsp.core.schemas.session_donnees import AppelId, SessionId

Variante = Literal["diffusable", "recherche"]
TYPE_RUN_BUILD: Final = "data-build"
VersionJeu = Annotated[str, StringConstraints(pattern=r"^v[0-9]+$")]
RunId = Annotated[str, StringConstraints(pattern=MOTIF_RUN_ID)]


class EnteteManifesteJeu(BaseModel):
    """Contrat minimal du MANIFEST, contrôlé par `train.chargement` (clés en plus acceptées).

    `ManifesteJeuEntrainement` l'étend : un seul contrat entre `data build` et `train run`.
    """

    model_config = ConfigDict(extra="allow")

    version: VersionJeu
    type_run: Literal["data-build"]
    run_id: RunId


class MetaLigne(SousSchema):
    """Provenance d'une ligne : tout se retrouve au journal Mistral et au Registre."""

    generateur: str
    """Modèle(s) résolu(s) des appels, séparés par « + » s'il y en a plusieurs."""
    appel_ids: list[AppelId] = Field(min_length=1)
    session_id: SessionId
    version_gabarit: dict[str, int]
    """Identifiant du gabarit du générateur → version, pour chaque appel de la session."""
    version_extracteur: int = Field(ge=1)
    source: list[str] = Field(min_length=1)
    """Identifiants des sources du Registre des licences (triés)."""
    licence: list[str] = Field(min_length=1)
    """Licence de chaque source, dans le même ordre que `source`."""
    date: Jour
    """Jour du dernier appel de la session (journal Mistral)."""


class LigneEntrainement(SchemaBase):
    """Une ligne de `train.jsonl`."""

    schema_version: Literal[1] = 1
    messages: list[dict[str, Any]] = Field(min_length=2)
    tools: list[dict[str, Any]] = Field(default_factory=list)
    tache: str
    meta: MetaLigne

    @model_validator(mode="after")
    def _conversation(self) -> Self:
        try:
            valider_conversation(self.messages)
        except ConversationInvalide as exc:
            raise ValueError(str(exc)) from None
        attendu = "user" if self.tache == "generique" else "system"
        if self.messages[0].get("role") != attendu:
            raise ValueError(f"messages[0] doit être « {attendu} » (Tâche {self.tache})")
        if self.messages[-1].get("role") != "assistant":
            raise ValueError("le dernier message doit être « assistant »")
        if len(self.meta.source) != len(self.meta.licence):
            raise ValueError("source et licence de même longueur attendues")
        return self


class ConditionsMistral(SousSchema):
    """Vérification des conditions commerciales Mistral (D1.2)."""

    verifiees_le: Jour | None
    url: str | None
    sha256: Sha256 | None


Nom = Annotated[str, StringConstraints(min_length=1)]


class ManifesteJeuEntrainement(EnteteManifesteJeu, SchemaBase):
    """Contenu de `data/train/vN/MANIFEST.json` (`run_id` : le run `data-build`)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    type_run: Literal["data-build"] = TYPE_RUN_BUILD
    variante: Variante
    cree_le: Jour
    statut: Literal["complet", "partiel-budget", "partiel-erreur"]
    filter_run_id: RunId
    validate_run_id: RunId
    generate_run_id: RunId
    sha256_train: Sha256
    nb_lignes: int = Field(ge=1)
    comptes_par_tache: dict[str, int]
    rejets_par_motif: dict[str, int]
    """Rejets de `validate` et de `filter`, additionnés par motif."""
    registre: dict[str, Any]
    """Instantané du Registre des licences (`RegistreLicences.instantane`)."""
    sha_gabarits: dict[Nom, Sha256]
    sha_prompts: dict[Nom, Sha256]
    sha_outils_mcp: Sha256
    conditions_mistral: ConditionsMistral
    modeles_generateurs: list[str]
    version_extracteur: int = Field(ge=1)
