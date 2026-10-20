"""Manifeste du Jeu d'évaluation gelé `eval/jeu/<version>/MANIFEST.json` (AD-25, SPEC §6).

Écrit une seule fois par `slmsp eval gel`, en JSON canonique suivi d'un LF, par création
exclusive. Les empreintes sont des SHA-256 du contenu aux fins de ligne normalisées en LF
(`REGLE_EMPREINTE`) : avec `core.autocrlf=true` et sans `.gitattributes`, les octets du
disque dépendent du checkout, pas le contenu normalisé.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Final, Literal, Self

from pydantic import AwareDatetime, Field, StringConstraints, field_validator, model_validator

from slmsp.core.schemas import SchemaBase, Sha256, SousSchema

REGLE_EMPREINTE: Final = "sha256 du contenu, fins de ligne normalisées en LF (CRLF -> LF)"
"""Règle de calcul des empreintes, inscrite telle quelle dans chaque manifeste."""

IdItem = Annotated[str, StringConstraints(pattern=r"^[A-Z]+-[0-9]{3,}$")]


class FichierManifeste(SousSchema):
    """Un fichier gelé : chemin relatif à la racine du dépôt, rôle et empreinte."""

    chemin: str
    """Chemin POSIX relatif à la racine du dépôt, sans `.`, `..`, lecteur ni barre inverse."""
    role: Literal["items", "cassette", "grille"]
    sha256: Sha256

    @field_validator("chemin")
    @classmethod
    def _chemin_relatif(cls, chemin: str) -> str:
        parties = chemin.split("/")
        if (
            not chemin
            or "\\" in chemin
            or ":" in chemin
            or chemin.startswith("/")
            or any(partie in ("", ".", "..") for partie in parties)
        ):
            raise ValueError("chemin POSIX relatif à la racine du dépôt attendu")
        return chemin


class Echantillons(SousSchema):
    """Échantillons tirés une seule fois au gel, identiques pour tous les modèles évalués."""

    graine: int
    second_juge: list[IdItem]
    relecture: list[IdItem]


class ManifesteJeu(SchemaBase):
    """Contenu de `eval/jeu/<version>/MANIFEST.json`."""

    schema_version: Literal[1] = 1
    version: Annotated[str, StringConstraints(pattern=r"^(?:v[0-9]+(?:\.[0-9]+)?|dev[0-9]+)$")]
    statut: Literal["provisoire", "relu", "relu-llm"]
    cree_le: AwareDatetime
    regle_empreinte: Literal[REGLE_EMPREINTE] = REGLE_EMPREINTE  # type: ignore[valid-type]
    fichiers: list[FichierManifeste] = Field(min_length=1)
    nb_items: int = Field(ge=0)
    composition: dict[str, dict[str, int]]
    """Code de Tâche → difficulté → nombre d'items."""
    ecarts: list[str] = Field(default_factory=list)
    """Écarts de composition avec SPEC §2 (non bloquants en `provisoire`)."""
    echantillons: Echantillons
    date_reference: date | None = None
    """Ancre de date des références (v1.1) : montants et dates font foi à cette date. Absente
    des manifestes antérieurs (v1.0), qui restent valides ; jamais postérieure au gel."""

    @model_validator(mode="after")
    def _fichiers_coherents(self) -> Self:
        chemins = [f.chemin for f in self.fichiers]
        doublons = sorted({c for c in chemins if chemins.count(c) > 1})
        if doublons:
            raise ValueError(f"chemins en double dans `fichiers` : {', '.join(doublons)}")
        for role in ("items", "grille"):
            nombre = sum(f.role == role for f in self.fichiers)
            if nombre != 1:
                raise ValueError(f"exactement un fichier de rôle `{role}` attendu ({nombre})")
        if self.date_reference is not None and self.date_reference > self.cree_le.date():
            raise ValueError(
                f"`date_reference` ({self.date_reference}) postérieure à la date du gel "
                f"({self.cree_le.date()})"
            )
        return self
