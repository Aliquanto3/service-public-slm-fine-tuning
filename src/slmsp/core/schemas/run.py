"""Manifeste de run `run.json` et lignes d'état `etat.jsonl` (AD-21, AD-25, AD-26).

`run.json` est écrit une fois, à la création du run, avec `statut = en_cours`, et n'est
jamais réécrit. Le statut courant est la dernière ligne valide d'`etat.jsonl` (`EtatRun`).
"""

from __future__ import annotations

from typing import Annotated, Any, Final, Literal

from pydantic import AwareDatetime, Field, StringConstraints

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema

Statut = Literal["en_cours", "complet", "partiel-budget", "partiel-erreur", "interrompu", "degrade"]
"""Statuts d'un run (AD-25) ; `degrade` marque un résultat obtenu avec une doublure (D5)."""

STATUTS_FINAUX: Final[frozenset[str]] = frozenset(
    {"complet", "partiel-budget", "partiel-erreur", "interrompu", "degrade"}
)
"""Statuts acceptés par `Run.terminer` (tous sauf `en_cours`)."""

MOTIF_RUN_ID: Final = r"^\d{8}-\d{6}-[a-z0-9.-]+-[0-9a-f]{4}$"
"""`AAAAMMJJ-HHMMSS-<slug>-<4 hex>` (AD-21)."""

MOTIF_TYPE: Final = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
"""Type de run : `eval-generation`, `data-seed`, `bench`… (un seul segment de chemin)."""

ModeleRef = Annotated[
    str,
    StringConstraints(pattern=r"^(base:[a-z0-9.-]+|ft:\d{8}-\d{6}-[a-z0-9.-]+-[0-9a-f]{4})$"),
]
"""Modèle évalué : `base:<slug>` ou `ft:<run_id du Run d'entraînement>`."""


class Gpu(SousSchema):
    """Carte graphique vue par NVML."""

    nom: str
    memoire_octets: int = Field(ge=0)


class Environnement(SousSchema):
    """Empreinte de la machine et du code au lancement du run (AD-21)."""

    os: str
    machine: str
    cpu: str
    nb_coeurs: int | None = None
    python: str
    gpus: list[Gpu] = Field(default_factory=list)
    pilote_nvidia: str | None = None
    cuda: str | None = None
    paquets: dict[str, str] = Field(default_factory=dict)
    git_commit: str | None = None
    git_modifie: bool | None = None


class RunManifest(SchemaBase):
    """Contenu de `runs/<type>/<run_id>/run.json` (AD-25)."""

    schema_version: Literal[1] = 1
    type: Annotated[str, StringConstraints(pattern=MOTIF_TYPE)]
    run_id: Annotated[str, StringConstraints(pattern=MOTIF_RUN_ID)]
    cree_le: AwareDatetime
    parents: list[Annotated[str, StringConstraints(pattern=MOTIF_RUN_ID)]] = Field(
        default_factory=list
    )
    modele_ref: ModeleRef | None = None
    quantification: Literal["f16", "q4_k_m"] | None = None
    variante_llamacpp: Literal["cpu", "cuda"] | None = None
    llamacpp_tag: Annotated[str, StringConstraints(pattern=r"^b\d+$")] | None = None
    chat_template_sha256: Sha256 | None = None
    jeu_version: str | None = None
    index_version: str | None = None
    statut: Statut = "en_cours"
    couverture: dict[str, Any] | None = None
    config: dict[str, Any]
    graine: int | None = None
    environnement: Environnement
    entrees: dict[str, Sha256] = Field(default_factory=dict)
    """Nom logique de chaque entrée → SHA-256 du fichier."""


class EtatRun(SchemaBase):
    """Une ligne d'`etat.jsonl` : changement de statut, en ajout seul."""

    schema_version: Literal[1] = 1
    horodatage: AwareDatetime
    statut: Statut
    pid: int
    motif: str | None = None
