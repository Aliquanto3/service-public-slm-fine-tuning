"""Évènements typés du Harnais, sérialisables en aller-retour (AD-14).

`AssistantService.repondre` renvoie un itérateur de ces évènements, consommé à l'identique
par la CLI, l'application et le banc. Chaque évènement est un modèle pydantic figé, discriminé
par son champ `type`. `vers_dict` produit un dict JSON stable ; `depuis_dict` le relit.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class _Fige(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Jeton(_Fige):
    """Fragment de texte généré, en flux."""

    type: Literal["jeton"] = "jeton"
    texte: str


class AppelOutil(_Fige):
    """Appel d'outil valide émis par le modèle."""

    type: Literal["appel-outil"] = "appel-outil"
    id: str
    nom: str
    arguments: dict[str, Any]


class ResultatOutil(_Fige):
    """Résultat (ou erreur) d'un appel d'outil, rattaché à l'appel par `id`."""

    type: Literal["resultat-outil"] = "resultat-outil"
    id: str
    nom: str
    resultat: Any
    erreur: bool = False


class AppelNonConforme(_Fige):
    """Appel d'outil refusé avant envoi (nom inconnu, arguments invalides) (AD-8)."""

    type: Literal["appel-non-conforme"] = "appel-non-conforme"
    nom: str | None
    arguments_bruts: str
    motif: str


class Source(_Fige):
    """Source citée : passage de l'Index local ou résultat MCP."""

    titre: str
    url: str
    origine: Literal["index", "mcp"]
    date: str | None = None
    extrait: str | None = None


class Sources(_Fige):
    """Sources de la réponse."""

    type: Literal["sources"] = "sources"
    sources: list[Source]


class Avertissement(_Fige):
    """Avertissement non bloquant destiné à l'Agent."""

    type: Literal["avertissement"] = "avertissement"
    code: str
    message: str


class Progression(_Fige):
    """Avancement d'une étape longue (`total` inconnu : `None`)."""

    type: Literal["progression"] = "progression"
    etape: str
    fait: int = Field(ge=0)
    total: int | None = Field(default=None, ge=0)


class Repli(_Fige):
    """Repli d'une source sur une autre (MCP indisponible → Index local, FR-9)."""

    type: Literal["repli"] = "repli"
    motif: str
    vers: Literal["index"]


class Fin(_Fige):
    """Fin du flux, avec la raison et l'usage en tokens s'il est connu."""

    type: Literal["fin"] = "fin"
    raison: Literal["terminee", "longueur", "interrompue"]
    usage: dict[str, int] | None = None


class Erreur(_Fige):
    """Erreur qui termine le flux."""

    type: Literal["erreur"] = "erreur"
    code: str
    message: str


Evenement = Annotated[
    Jeton
    | AppelOutil
    | ResultatOutil
    | AppelNonConforme
    | Sources
    | Avertissement
    | Progression
    | Repli
    | Fin
    | Erreur,
    Field(discriminator="type"),
]

_ADAPTATEUR: TypeAdapter[Evenement] = TypeAdapter(Evenement)


def vers_dict(evenement: Evenement) -> dict[str, Any]:
    """Dict JSON de l'évènement, avec sa clé `type` (champs `None` conservés)."""
    return evenement.model_dump(mode="json")


def depuis_dict(donnees: Any) -> Evenement:
    """Reconstruit un évènement ; lève `pydantic.ValidationError` si `type` est inconnu."""
    return _ADAPTATEUR.validate_python(donnees)
