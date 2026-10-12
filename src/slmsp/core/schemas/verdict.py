"""Verdict d'un Juge sur un item (AD-12), commun au Juge principal et au second juge.

Un verdict note l'item critère par critère (`criteres`) : une note et sa justification, ou,
pour `presence_elements` (CR, RE), un élément de référence par ligne. Un verdict `invalide`
(deux sorties non conformes au schéma) n'a ni critère ni confiance : l'item est exclu du
score et compté à part. Le Juge ne calcule aucun score (`slmsp.evaluation.scores`).
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from slmsp.core.schemas import SchemaBase, SousSchema


class NoteCritere(SousSchema):
    """Note d'un critère et sa justification d'une phrase."""

    note: int | float
    justification: str


class ElementPresent(SousSchema):
    """Présence d'un élément de référence (`D1`, `A2`, `P3`…) dans la sortie."""

    ref: str
    present: int | float
    justification: str


class Verdict(SchemaBase):
    """Verdict d'un Juge sur un item ; `invalide` ⇔ ni critère ni confiance."""

    schema_version: Literal[1] = 1
    id: str
    criteres: dict[str, NoteCritere | list[ElementPresent]]
    inventions: list[str]
    confiance: Literal["haute", "moyenne", "basse"] | None
    invalide: bool = False

    @model_validator(mode="after")
    def _invalide_sans_critere(self) -> Self:
        if self.invalide:
            conforme = not self.criteres and self.confiance is None
        else:
            conforme = bool(self.criteres) and self.confiance is not None
        if not conforme:
            raise ValueError(
                "un verdict invalide n'a ni critère ni confiance, et un verdict valide a les deux"
            )
        return self

    @classmethod
    def invalide_pour(cls, identifiant: str) -> Verdict:
        """Verdict `invalide` de l'item `identifiant` (deux sorties non conformes)."""
        return cls(id=identifiant, criteres={}, inventions=[], confiance=None, invalide=True)
