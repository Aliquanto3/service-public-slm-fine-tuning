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


class CibleLigne(SousSchema):
    """Cible d'une ligne v2 (story 15.3) : sortie du Modèle de base local `source`
    (`slm:<slug>`), relue dans `generations-locales.sqlite` sous `appel_local_id`."""

    source: Annotated[str, StringConstraints(pattern=r"^slm:[A-Za-z0-9][A-Za-z0-9._-]*$")]
    appel_local_id: Annotated[str, StringConstraints(min_length=1)]


class MetaLigne(SousSchema):
    """Provenance d'une ligne : tout se retrouve au journal Mistral et au Registre.

    v1 : `appel_ids` (au moins un) couvre l'entrée et la cible. v2 (`cible` présent) :
    `appel_ids` ne porte que les appels Mistral de l'**entrée** (vide si l'entrée est publique)
    et la cible vient du journal local (`cible`).
    """

    generateur: str
    """Modèle(s) résolu(s) des appels, séparés par « + » s'il y en a plusieurs."""
    appel_ids: list[AppelId]
    session_id: SessionId
    version_gabarit: dict[str, int]
    """Identifiant du gabarit du générateur → version, pour chaque appel de la session."""
    version_extracteur: int = Field(ge=1)
    source: list[str] = Field(min_length=1)
    """Identifiants des sources du Registre des licences (triés)."""
    licence: list[str] = Field(min_length=1)
    """Licence de chaque source, dans le même ordre que `source`."""
    date: Jour
    """Jour du dernier appel de la session (journal Mistral, ou journal local en v2)."""
    cible: CibleLigne | None = Field(default=None, exclude_if=lambda v: v is None)

    @model_validator(mode="after")
    def _appels(self) -> Self:
        if self.cible is None and not self.appel_ids:
            raise ValueError("appel_ids : au moins un appel Mistral attendu sans « cible »")
        return self


class LigneEntrainement(SchemaBase):
    """Une ligne de `train.jsonl` : v1 (cible Mistral) ou v2 (cible locale, `meta.cible`)."""

    schema_version: Literal[1, 2] = 1
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
        if (self.schema_version == 2) != (self.meta.cible is not None):
            raise ValueError("meta.cible présent si et seulement si schema_version = 2")
        return self


class ConditionsMistral(SousSchema):
    """Vérification des conditions commerciales Mistral (D1.2)."""

    verifiees_le: Jour | None
    url: str | None
    sha256: Sha256 | None


Nom = Annotated[str, StringConstraints(min_length=1)]


class Ecart(SousSchema):
    """Ligne source écartée par le nettoyage : rang d'origine (0 = première ligne), motif."""

    rang: int = Field(ge=0)
    motif: Literal["longueur"]
    tokens: int = Field(ge=1)


class Nettoyage(SousSchema):
    """Provenance d'un jeu nettoyé (story 9.9) : `data build --nettoyage`.

    Le jeu est la suite des lignes du jeu `depuis_version` (run `depuis_build`, SHA
    `sha256_train_source`) passées par `core.nettoyage.nettoyer_cible` de version `version`,
    sauf les rangs de `ecartes` : cibles de plus de `plafond_tokens` tokens (tokenizer de SHA
    `tokenizer_sha256`). Aucune autre ligne ne peut manquer (`verifier_nettoyage`).
    """

    version: int = Field(ge=1)
    depuis_build: RunId
    depuis_version: VersionJeu
    sha256_train_source: Sha256
    plafond_tokens: int = Field(ge=1)
    tokenizer_sha256: Sha256
    lc_signales: int = Field(ge=0)
    """Exemples LC gardés dont un élément vérifiable de la source manque à la cible."""
    ecartes: list[Ecart]
    """Lignes source absentes du jeu, rangs strictement croissants."""

    @model_validator(mode="after")
    def _ecartes(self) -> Self:
        rangs = [e.rang for e in self.ecartes]
        if any(a >= b for a, b in zip(rangs, rangs[1:], strict=False)):
            raise ValueError("ecartes : rangs strictement croissants attendus")
        if any(e.tokens <= self.plafond_tokens for e in self.ecartes):
            raise ValueError("ecartes : un écart « longueur » ne dépasse pas plafond_tokens")
        return self


class SousEnsemble(SousSchema):
    """Provenance d'un jeu restreint à certaines Tâches : `data build --sous-ensemble`.

    Le jeu est la suite, à l'octet près et dans l'ordre, des lignes du jeu `depuis_version`
    (run `depuis_build`, SHA `sha256_train_source`) dont la Tâche figure dans `taches`
    (`core.sous_ensemble.verifier_sous_ensemble`). `comptes_source` : comptes par Tâche du jeu
    source. Si le jeu source était nettoyé, son bloc `nettoyage` est repris tel quel dans
    `nettoyage_source` : ses `ecartes` désignent des rangs du jeu amont du nettoyage, non
    transposables au sous-ensemble ; le MANIFEST du sous-ensemble n'a donc pas de bloc
    `nettoyage` propre, et `train.chargement` revérifie la chaîne de nettoyage du jeu source.
    """

    depuis_build: RunId
    depuis_version: VersionJeu
    sha256_train_source: Sha256
    taches: list[Nom] = Field(min_length=1)
    """Tâches gardées, triées, sans doublon."""
    comptes_source: dict[str, int]
    nettoyage_source: Nettoyage | None = Field(default=None, exclude_if=lambda v: v is None)

    @model_validator(mode="after")
    def _taches(self) -> Self:
        if self.taches != sorted(set(self.taches)):
            raise ValueError("taches : liste triée sans doublon attendue")
        return self


class AlignementCt(SousSchema):
    """Provenance d'un jeu dont les prompts CT sont alignés sur leur cible (story 16.3).

    Le jeu est l'alignement exact (`core.alignement_ct.verifier_alignement`) du jeu
    `depuis_version` (run `depuis_build`, SHA `sha256_train_source`) : chaque ligne CT dont la
    cible porte des emplacements reçoit `formulation`, `{libelles}` remplacé par ces
    emplacements ; les autres lignes sont copiées à l'octet près. `origine_formulation` dit d'où
    vient le texte de `formulation` (jamais un texte rédigé par Claude, D1). Comme pour
    `sous_ensemble`, le bloc `nettoyage` du jeu source est repris dans `nettoyage_source`.
    """

    depuis_build: RunId
    depuis_version: VersionJeu
    sha256_train_source: Sha256
    formulation: str = Field(min_length=1)
    origine_formulation: str = Field(min_length=1)
    lignes_modifiees: int = Field(ge=0)
    comptes_source: dict[str, int]
    nettoyage_source: Nettoyage | None = Field(default=None, exclude_if=lambda v: v is None)


class BilanSelection(SousSchema):
    """Bilan d'une Tâche sélectionnée : lignes source, retenues, gagnants par source, écarts."""

    lignes_source: int = Field(ge=0)
    retenues: int = Field(ge=0)
    gagnants: dict[Nom, int]
    """Source du gagnant (`mistral`, `slm:<slug>`) → nombre de lignes."""
    part_base: float | None = Field(ge=0, le=1)
    """Part des gagnants de la base locale parmi les retenues (`None` sans ligne retenue)."""
    score_moyen: float | None = Field(ge=0, le=1)
    ecartees: dict[Nom, int]
    """Lignes écartées par motif : `sans_candidat` (aucun candidat pour la ligne) ou
    `aucun_accepte` (candidats tous refusés ou ignorés)."""


class Selection(SousSchema):
    """Provenance d'un jeu dont les cibles de `taches` sont sélectionnées (story 15.3, O3).

    Le jeu est la suite, dans l'ordre, des lignes du jeu `depuis_version` (run `depuis_build`,
    SHA `sha256_train_source`) : lignes des Tâches hors `taches` et hors `retirees` copiées à
    l'octet près ; lignes de `taches` copiées (gagnant Mistral), remplacées par une ligne v2 de
    même entrée (gagnant de la base locale `base`) ou écartées ; lignes de `retirees` absentes
    (`core.selection.verifier_selection`). Le détail par ligne (gagnant, notes, score) est dans
    `selection.jsonl` du run, de SHA `sha256_detail`.
    """

    depuis_build: RunId
    depuis_version: VersionJeu
    sha256_train_source: Sha256
    nettoyage_source: Nettoyage | None = Field(default=None, exclude_if=lambda v: v is None)
    candidats_run_id: RunId
    sha256_candidats: Sha256
    verdicts: dict[RunId, Sha256] = Field(min_length=1)
    """Run `data-juger` → SHA de son `verdicts.jsonl`."""
    juge: Nom
    """Modèle du juge de données dont le verdict `accepte` décide (DeepSeek, règle O1)."""
    sha_grilles: dict[Nom, Sha256]
    base: Annotated[str, StringConstraints(pattern=r"^slm:[A-Za-z0-9][A-Za-z0-9._-]*$")]
    version_nettoyage: int = Field(ge=1)
    """Règle `nettoyer_cible` appliquée aux cibles locales (recontrôlée par `train run`)."""
    tokenizer_sha256: Sha256
    taches: list[Nom] = Field(min_length=1)
    retirees: list[Nom]
    par_tache: dict[Nom, BilanSelection]
    candidats_ignores: dict[Nom, int]
    """Candidats ignorés par motif (source OpenRouter, sans verdict, verdict invalide…)."""
    sha256_detail: Sha256
    runs_partiels: list[RunId] = Field(default_factory=list, exclude_if=lambda v: not v)
    """Runs sources (candidats, jugements) non `complet` admis par `--accepter-partiel`."""
    sans_verdict_par_tache: dict[Nom, int] = Field(default_factory=dict)
    """Candidats sans verdict du juge principal, par Tâche (non nuls seulement)."""
    avertissements: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _taches(self) -> Self:
        for nom in ("taches", "retirees"):
            valeurs = getattr(self, nom)
            if valeurs != sorted(set(valeurs)):
                raise ValueError(f"{nom} : liste triée sans doublon attendue")
        if set(self.taches) & set(self.retirees):
            raise ValueError("une Tâche ne peut être à la fois sélectionnée et retirée")
        return self


class ManifesteJeuEntrainement(EnteteManifesteJeu, SchemaBase):
    """Contenu de `data/train/vN/MANIFEST.json` (`run_id` : le run `data-build`).

    v2 : jeu à cibles sélectionnées (bloc `selection`, story 15.3) ; v1 sinon.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1, 2] = 1
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
    generateur_preversion: bool = Field(default=False, exclude_if=lambda v: not v)
    """Story S5 : vrai si un modèle de `modeles_generateurs` (identifiants exacts renvoyés par
    l'API) est hors de la liste stable (`modeles_stables`) : préversion du Générateur."""
    version_extracteur: int = Field(ge=1)
    mode_outils: Literal["local", "connecte"] = "local"
    """Début de conversation des Tâches à outils : `local` (v1, « Passages… / Demande : … »
    sans passage) ou `connecte` (demande seule, comme `messages_connecte`). Informatif : hors
    de l'empreinte d'entraînement, qui contrôle `sha256_train` au chargement et distingue le
    jeu par sa version et son run de build (`train.run.CLES_INVARIANTS`)."""
    nettoyage: Nettoyage | None = Field(default=None, exclude_if=lambda v: v is None)
    """Présent sur un jeu nettoyé (story 9.9) : `train.chargement` revérifie la chaîne."""
    sous_ensemble: SousEnsemble | None = Field(default=None, exclude_if=lambda v: v is None)
    """Présent sur un jeu restreint à certaines Tâches : `train.chargement` revérifie la chaîne."""
    alignement_ct: AlignementCt | None = Field(default=None, exclude_if=lambda v: v is None)
    """Présent sur un jeu aux prompts CT alignés (story 16.3) : `train.chargement` revérifie."""
    selection: Selection | None = Field(default=None, exclude_if=lambda v: v is None)
    """Présent sur un jeu à cibles sélectionnées (v2) : `train.chargement` revérifie la chaîne
    et `train run` les cibles locales."""

    @model_validator(mode="after")
    def _version(self) -> Self:
        if (self.schema_version == 2) != (self.selection is not None):
            raise ValueError("bloc « selection » présent si et seulement si schema_version = 2")
        return self


# --- Paires de préférence ORPO (story 9.7, FR-34, D-nuit-A1-21) ---------------------------------

DEROGATION_ORPO: Final = (
    "Dérogation FR-34 : les paires ORPO ne sont pas à données égales avec le SFT. La réponse "
    "choisie est la réponse de l'exemple SFT validé ; la réponse rejetée est une génération "
    "du Modèle de base local (slm:<slug>), journalisée dans generations-locales.sqlite. "
    "Aucun verdict du Juge Claude n'est utilisé."
)


class EnteteMetaPaire(BaseModel):
    """Contrat minimal de `meta` d'une paire, contrôlé par `train.chargement`."""

    model_config = ConfigDict(extra="allow")

    appel_ids: list[str] = Field(min_length=1)


class EntetePaire(BaseModel):
    """Contrat minimal d'une ligne de `preferences.jsonl`, contrôlé par `train.chargement`.

    `PairePreference` l'étend : un seul contrat entre `data build --preferences` et
    `train run`. `prompt` : messages avant la réponse ; `chosen`, `rejected` : messages de
    la réponse retenue et de la réponse rejetée.
    """

    model_config = ConfigDict(extra="allow")

    prompt: list[dict[str, Any]] = Field(min_length=1)
    chosen: list[dict[str, Any]] = Field(min_length=1)
    rejected: list[dict[str, Any]] = Field(min_length=1)
    tools: list[dict[str, Any]] | None = None
    tache: str
    meta: EnteteMetaPaire


class MetaPaire(EnteteMetaPaire):
    """Provenance d'une paire : `appel_ids` désigne les appels Mistral de la réponse choisie."""

    model_config = ConfigDict(extra="forbid")

    session_id: SessionId
    generateur_rejected: str
    """`slm:<slug>` : Modèle de base local ayant produit la réponse rejetée."""
    appel_local_id: str
    """Appel du journal `generations-locales.sqlite` de la réponse rejetée."""
    source: list[str] = Field(min_length=1)
    licence: list[str] = Field(min_length=1)


class PairePreference(EntetePaire, SchemaBase):
    """Une ligne de `preferences.jsonl`."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    meta: MetaPaire  # type: ignore[assignment]

    @model_validator(mode="after")
    def _conversations(self) -> Self:
        for cle in ("chosen", "rejected"):
            reponse = getattr(self, cle)
            try:
                valider_conversation([*self.prompt, *reponse])
            except ConversationInvalide as exc:
                raise ValueError(f"{cle} : {exc}") from None
            if reponse[-1].get("role") != "assistant":
                raise ValueError(f"{cle} : le dernier message doit être « assistant »")
        return self


class ManifestePreferences(EnteteManifesteJeu, SchemaBase):
    """`data/train/vN/MANIFEST.json` d'une version de paires (`sha256_preferences`)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    type_run: Literal["data-build"] = TYPE_RUN_BUILD
    variante: Variante
    cree_le: Jour
    statut: Literal["complet"] = "complet"
    build_run_id: RunId
    """Run `data-build` du jeu SFT dont viennent les réponses choisies."""
    jeu_sft_version: VersionJeu
    sha256_train: Sha256
    sha_outils_mcp: Sha256 | None = None
    """Repris du jeu SFT source : outils rendus à l'entraînement contrôlés (R7)."""
    sha256_preferences: Sha256
    nb_paires: int = Field(ge=1)
    comptes_par_tache: dict[str, int]
    ecartees_par_motif: dict[str, int]
    modele: Nom
    """`base:<slug>`."""
    generateur_rejected: Nom
    """`slm:<slug>`."""
    graine: int = Field(ge=0)
    temperature: float = Field(ge=0)
    max_tokens: int = Field(ge=1)
    derogation_fr34: str
    utilise_verdicts_juge: Literal[False] = False
