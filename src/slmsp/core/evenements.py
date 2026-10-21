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
    """Source citée : passage de l'Index local, résultat MCP ou page vérifiée en ligne.

    `numero` est le renvoi `[n]` du texte généré qui la cite (passage de l'Index), s'il existe.
    `origine = "verification"` : page officielle consultée par la vérification en ligne
    (FR-12, story 13.5) ; `date` est alors la date de consultation.
    """

    numero: int | None = Field(default=None, ge=1)
    titre: str
    url: str
    origine: Literal["index", "mcp", "verification"]
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


class Verification(_Fige):
    """Résultat d'une vérification en ligne d'une page officielle (FR-12, story 13.5).

    `verdict` : `concordant` (la page confirme la réponse), `difference` (la page diffère),
    `indisponible` (Mode hors ligne, hôte refusé, délai dépassé, page illisible, comparaison
    non concluante). `url` et `titre` valent `None` si aucune source citée n'a pu être
    choisie. `date_consultation` est un horodatage ISO 8601 en UTC. `extrait` est le
    passage de la page qui diffère, recopié tel quel, s'il a pu être retrouvé dans la page.
    """

    type: Literal["verification"] = "verification"
    url: str | None
    titre: str | None
    date_consultation: str
    verdict: Literal["concordant", "difference", "indisponible"]
    phrase: str
    extrait: str | None = None


class Fin(_Fige):
    """Fin du flux, avec la raison et l'usage en tokens s'il est connu.

    `urls_inventees` liste les URL du texte généré absentes des passages, des résultats
    d'outils et des textes saisis (`harness.citations`) ; le texte n'est jamais réécrit.
    `boucle` : sortie coupée par le garde-fou anti-boucle du Harnais (story 16.3).
    """

    type: Literal["fin"] = "fin"
    raison: Literal["terminee", "longueur", "boucle", "interrompue"]
    usage: dict[str, int] | None = None
    urls_inventees: list[str] = Field(default_factory=list)


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
    | Verification
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
