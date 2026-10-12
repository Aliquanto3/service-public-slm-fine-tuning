"""Amorce du générateur : une ligne de `amorces.jsonl`, artefact de l'étape `seed` (AD-3 verrou 5).

Une amorce est un texte inséré tel quel dans un emplacement `{nom}` d'un gabarit du
générateur. Sa provenance est l'une de :

- `public` : une ligne d'un jeu public téléchargé (`jeu`, `revision`, `ligne` requis,
  interdits ailleurs : une amorce n'a qu'une provenance) ;
- `mistral` : une réponse Mistral journalisée (`appel_id` requis, interdit ailleurs) ;
- `anael` : réservé (décision différée d'Anaël) ; le Générateur le refuse.

`sha_texte` est l'empreinte SHA-256 du texte en UTF-8 ; le Générateur la recalcule avant
tout appel. Aucune provenance `claude` n'existe.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, StringConstraints, model_validator

from slmsp.core.schemas import SchemaBase, Sha256

MOTIF_AMORCE_ID = r"^[a-z0-9][a-z0-9._-]*$"
MOTIF_EMPLACEMENT = r"^[a-z_]+$"

AuteurContenu = Literal["public", "mistral", "anael"]


class Amorce(SchemaBase):
    """Une amorce de `amorces.jsonl` (contrat de la story 9.3)."""

    schema_version: Literal[1]
    amorce_id: Annotated[str, StringConstraints(pattern=MOTIF_AMORCE_ID)]
    tache: Annotated[str, StringConstraints(min_length=1)]
    emplacement: Annotated[str, StringConstraints(pattern=MOTIF_EMPLACEMENT)]
    texte: Annotated[str, StringConstraints(min_length=1)]
    sha_texte: Sha256
    auteur_contenu: AuteurContenu
    jeu: Annotated[str, StringConstraints(min_length=1)] | None = None
    revision: Annotated[str, StringConstraints(min_length=1)] | None = None
    ligne: Annotated[int, Field(ge=0)] | None = None
    appel_id: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{32}$")] | None = None

    @model_validator(mode="after")
    def _provenance(self) -> Self:
        if self.auteur_contenu == "public":
            manquants = [cle for cle in ("jeu", "revision", "ligne") if getattr(self, cle) is None]
            if manquants:
                raise ValueError(f"amorce publique sans {', '.join(manquants)}")
        else:
            presents = [
                cle for cle in ("jeu", "revision", "ligne") if getattr(self, cle) is not None
            ]
            if presents:
                raise ValueError(f"{', '.join(presents)} réservés aux amorces publiques")
        if self.auteur_contenu == "mistral":
            if self.appel_id is None:
                raise ValueError("amorce Mistral sans appel_id")
        elif self.appel_id is not None:
            raise ValueError("appel_id réservé aux amorces Mistral")
        return self
