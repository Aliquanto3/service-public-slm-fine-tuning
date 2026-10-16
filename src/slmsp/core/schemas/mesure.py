"""Résultat d'une mesure technique `runs/measure/<run_id>/resultat.json` (AD-25).

Première version (story 2.3, H-VEC), étendue par la story 6.4. Une mesure confronte des
`valeurs` à des `seuils` et conclut par un verdict sur l'hypothèse ; si l'hypothèse est
infirmée, `repli` décrit la solution de rechange consignée (sans être implémentée).
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Self

from pydantic import AwareDatetime, Field, StringConstraints, model_validator

from slmsp.core.schemas import SchemaBase
from slmsp.core.schemas.run import MOTIF_RUN_ID, Environnement

Verdict = Literal["confirmee", "infirmee", "sans-objet"]


class ResultatMesure(SchemaBase):
    """Contenu de `resultat.json` d'un run `measure`."""

    schema_version: Literal[1] = 1
    mesure: Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
    """Identifiant de la mesure (`h-vec`…), aussi slug du run."""
    hypothese: str = Field(min_length=1)
    """Hypothèse d'architecture mesurée (`H-VEC`…)."""
    run_id: Annotated[str, StringConstraints(pattern=MOTIF_RUN_ID)]
    mesure_le: AwareDatetime
    index_version: str | None = None
    parametres: dict[str, Any]
    valeurs: dict[str, float | int | None]
    seuils: dict[str, float]
    verdict: Verdict
    repli: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    conformite: dict[str, bool] = Field(default_factory=dict)
    """Conformité à une exigence (`nfr-1`…) ; vide pour les mesures sans exigence (story 6.4)."""
    environnement: Environnement | None = None
    """Empreinte de la machine de mesure (story 6.4)."""
    avertissement: str | None = None
    """Réserve de lecture (la machine de développement n'est pas le PC cible)."""

    @model_validator(mode="after")
    def _repli_si_infirmee(self) -> Self:
        if self.verdict == "infirmee" and not self.repli:
            raise ValueError("une hypothèse infirmée porte son repli")
        return self
