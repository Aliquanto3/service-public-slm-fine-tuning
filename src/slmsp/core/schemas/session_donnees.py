"""Sessions de génération de l'étape `generate` (story 9.4) : plan, résultats, abandons.

Une session est l'unité de génération d'un exemple : un ou plusieurs appels du Générateur
Mistral sous un même `session_id` déterministe (Tâche, gabarits, amorces, passages, outils).
Fichiers du run `runs/data-generate/<run_id>/` :

- `plan.jsonl` : `SessionPlanifiee`, écrit une fois à la création du run, relu à la reprise ;
- `brut.jsonl` : `SessionBrute`, une ligne par session terminée (lue par `validate`, 9.5) ;
- `abandons.jsonl` : `AbandonSession`, session close sans exemple, avec son motif ;
- `incidents.jsonl` : `IncidentSession`, panne de transport MCP, session réessayée à la reprise.

Aucun de ces schémas ne porte de texte généré : seulement des identifiants (appels du journal
Mistral, amorces, chunks de l'Index, chemins de cassettes) et des compteurs.
"""

from __future__ import annotations

from typing import Annotated, Final, Literal, get_args

from pydantic import Field, StringConstraints

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema

MOTIF_SESSION_ID: Final = r"^[a-z0-9]+-[0-9a-f]{24}$"
"""`<tâche en minuscules>-<24 hex>` : compatible avec le Générateur et les cassettes."""

MotifAbandon = Literal[
    "appel_non_conforme",
    "fuite_identifiant",
    "tours_max",
    "sans_appel_outil",
    "erreur_outil",
    "reponse_tronquee",
    "sans_contenu",
    "cassette_incoherente",
    "provenance_invalide",
]
MOTIFS_ABANDON: Final[tuple[str, ...]] = get_args(MotifAbandon)

SessionId = Annotated[str, StringConstraints(pattern=MOTIF_SESSION_ID)]
AppelId = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{32}$")]


class RefGabarit(SousSchema):
    """Gabarit d'un appel de la session : identifiant, version et SHA-256 du fichier."""

    id: Annotated[str, StringConstraints(pattern=r"^[a-z0-9-]+$")]
    version: int = Field(ge=1)
    sha256: Sha256


class PassagePlan(SousSchema):
    """Passage de l'Index retenu au plan pour une session Q (champs de `core.ports.Passage`)."""

    chunk_id: str
    doc_id: str
    source: str
    titre: str
    url: str
    texte: str
    date_snapshot: str | None
    score: float


class SessionPlanifiee(SchemaBase):
    """Une ligne de `plan.jsonl`."""

    schema_version: Literal[1] = 1
    session_id: SessionId
    tache: str
    rang: int = Field(ge=0)
    """Position dans le plan : l'ordre d'exécution (AD-5)."""
    gabarits: list[RefGabarit] = Field(min_length=1)
    """Chaîne des gabarits, dans l'ordre des appels (CR : transcription puis compte rendu)."""
    amorce_ids: list[str] = Field(min_length=1)
    passages: list[PassagePlan] | None = None
    """Passages de l'Index (Q seulement), après retrait des URL protégées."""
    outils_sha256: Sha256 | None = None
    """`tools_list_sha256` de `config/outils-mcp.toml` (Tâches outillées seulement)."""


class SessionBrute(SchemaBase):
    """Une ligne de `brut.jsonl` : session terminée, réponse finale = dernier appel."""

    schema_version: Literal[1] = 1
    session_id: SessionId
    tache: str
    appel_ids: list[AppelId] = Field(min_length=1)
    amorce_ids: list[str] = Field(min_length=1)
    amorces_derivees: list[str] = Field(default_factory=list)
    cassettes: list[str] = Field(default_factory=list)
    """Chemins POSIX relatifs à la racine, dans l'ordre des tours d'outils."""
    passages: list[str] | None = None
    """`chunk_id` des passages fournis (Q seulement)."""
    index_version: str | None = None
    appels_nouveaux: int = Field(ge=0)
    appels_reutilises: int = Field(ge=0)


class AbandonSession(SchemaBase):
    """Une ligne de `abandons.jsonl` : session close sans exemple (jamais rejouée)."""

    schema_version: Literal[1] = 1
    session_id: SessionId
    tache: str
    motif: MotifAbandon
    detail: str
    appel_ids: list[AppelId] = Field(default_factory=list)
    cassettes: list[str] = Field(default_factory=list)


class IncidentSession(SchemaBase):
    """Une ligne de `incidents.jsonl` : panne de transport MCP, session réessayée à la reprise."""

    schema_version: Literal[1] = 1
    session_id: SessionId
    tache: str
    type: str
    detail: str
    appel_ids: list[AppelId] = Field(default_factory=list)
