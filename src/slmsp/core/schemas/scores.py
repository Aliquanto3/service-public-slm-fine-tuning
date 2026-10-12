"""Scores de Tâche d'un run `eval-notation` : `scores.json` (AD-12, FR-39).

`scores.json` est le JSON canonique de `Scores` suivi d'un LF. Il ne porte ni identifiant du
run de notation, ni horodatage, ni coût de la session : relancer la notation avec un cache
de verdicts plein le reproduit à l'octet près. Les scores sont arrondis à 4 décimales, les
coûts à 6. Toutes les formules vivent dans `slmsp.evaluation.scores` ; le Juge n'en
calcule aucune.

`verdicts_relus` vaut toujours faux à l'écriture : `slmsp.evaluation.relecture.charger_scores`
le pose à la lecture si un `relecture-validee.json` daté existe dans le run.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema
from slmsp.core.schemas.run import ModeleRef


class Effectifs(SousSchema):
    """Effectifs d'une Tâche."""

    notes: int = Field(ge=0)
    """Items entrés dans le score."""
    juges: int = Field(ge=0)
    """Items au verdict valide du Juge principal."""
    invalides: int = Field(ge=0)
    """Items au verdict `invalide` (deux sorties non conformes), exclus du score."""
    non_juges: int = Field(ge=0)
    """Items soumis au Juge mais non jugés (budget, erreur d'API), exclus du score."""
    en_erreur: int = Field(ge=0)
    """Items en erreur à la génération, exclus du score et jamais jugés."""
    second_juge: int = Field(ge=0)
    """Items au verdict valide du second juge."""


class StatutsTache(SousSchema):
    """Statuts qui qualifient un Score de Tâche."""

    jeu_statut: str
    """`provisoire`, `relu` (manifeste) ou `calibrage`."""
    verdicts_relus: bool = False
    fragile: bool = False
    """Kappa de Tâche calculable et sous le seuil `kappa_fragile`."""
    plafonne_lc: bool = False


class KappaTache(SousSchema):
    """Accord entre le Juge principal et le second juge sur l'échantillon."""

    valeur: float | None = None
    """Minimum des kappas calculables par critère (`None` si aucun)."""
    par_critere: dict[str, float | None] = Field(default_factory=dict)
    effectif: int = Field(default=0, ge=0)
    """Items jugés valides par les deux juges."""


class ScoreTache(SousSchema):
    """Score d'une Tâche, de 0 à 100 (`None` sans item noté)."""

    tache: Literal["Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR"]
    score: float | None
    composantes: dict[str, float | None] = Field(default_factory=dict)
    rapportes: dict[str, Any] = Field(default_factory=dict)
    """Critères rapportés hors score (structure, clarté, longueur, gain de Kandel-Moles…)."""
    effectifs: Effectifs
    statuts: StatutsTache
    kappa: KappaTache
    cout_juge_eur: float = Field(ge=0)
    manifeste_sha256: Sha256 | None = None


class Scores(SchemaBase):
    """Contenu de `runs/eval-notation/<run_id>/scores.json`."""

    schema_version: Literal[1] = 1
    run_generation: str
    modele_ref: ModeleRef | None = None
    quantification: Literal["f16", "q4_k_m"] | None = None
    jeu_version: str
    jeu_statut: str
    manifeste_sha256: Sha256 | None = None
    version_texte: int
    taches: dict[str, ScoreTache]
    cout_juge_total_eur: float = Field(ge=0)
