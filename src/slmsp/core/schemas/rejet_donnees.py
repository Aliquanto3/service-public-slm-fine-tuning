"""Rejet d'un exemple par les étapes `validate` et `filter` (story 9.5, FR-30).

Une ligne de `rejets.jsonl` désigne une session de `brut.jsonl` écartée, avec son motif. Elle
ne porte aucun texte généré : `detail` ne contient que des comptes et des identifiants.
Les lignes conservées (`valides.jsonl`, `retenus.jsonl`) sont des `SessionBrute` inchangées.
"""

from __future__ import annotations

from typing import Final, Literal, get_args

from slmsp.core.schemas import SchemaBase
from slmsp.core.schemas.session_donnees import SessionId

MotifValidation = Literal[
    "trace_divergente",
    "appel_non_conforme",
    "url_inventee",
    "valeur_absente",
    "infidele",
]
MotifFiltre = Literal["fuite_ngram", "fuite_cosinus", "doublon"]
MOTIFS_VALIDATION: Final[tuple[str, ...]] = get_args(MotifValidation)
MOTIFS_FILTRE: Final[tuple[str, ...]] = get_args(MotifFiltre)


class RejetExemple(SchemaBase):
    """Une ligne de `rejets.jsonl` (étapes `validate` et `filter`)."""

    schema_version: Literal[1] = 1
    session_id: SessionId
    tache: str
    etape: Literal["validate", "filter"]
    motif: MotifValidation | MotifFiltre
    detail: str
