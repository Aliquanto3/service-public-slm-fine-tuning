"""Amorce du générateur : une ligne de `amorces.jsonl`, artefact de l'étape `seed` (AD-3 verrou 5).

Une amorce est un texte inséré tel quel dans un emplacement `{nom}` d'un gabarit du
générateur. Sa provenance est l'une de :

- `public` : une ligne d'un jeu public téléchargé (`jeu`, `revision`, `ligne` requis,
  interdits ailleurs : une amorce n'a qu'une provenance) ;
- `mistral` : une réponse Mistral journalisée (`appel_id` requis, interdit ailleurs) ;
- `anael` : réservé (décision différée d'Anaël) ; le Générateur le refuse ;
- `config` : un paramètre de configuration tiré par graine, sans contenu rédigé (`lie_a`
  requis, interdit ailleurs : l'amorce jointe dans le même appel). Seuls les emplacements de
  `EMPLACEMENTS_CONFIG` l'admettent, avec un texte de la forme `<n> mots`.

Une amorce `mistral` reprend soit le contenu entier de la réponse journalisée, soit la
valeur de la clé `emplacement` de l'objet JSON que ce contenu porte (`texte_de_reponse`).

`sha_texte` est l'empreinte SHA-256 du texte en UTF-8 ; le Générateur la recalcule avant
tout appel. Aucune provenance `claude` n'existe.
"""

from __future__ import annotations

import json
import re
from typing import Annotated, Any, Final, Literal, Self

from pydantic import Field, StringConstraints, model_validator

from slmsp.core.schemas import SchemaBase, Sha256

MOTIF_AMORCE_ID = r"^[a-z0-9][a-z0-9._-]*$"
MOTIF_EMPLACEMENT = r"^[a-z_]+$"

AuteurContenu = Literal["public", "mistral", "anael"]
"""Auteurs de contenu admis au Registre des licences."""
AuteurAmorce = Literal["public", "mistral", "anael", "config"]
"""Provenances d'une amorce : celles du Registre, plus `config` (paramètre tiré par graine)."""

EMPLACEMENTS_CONFIG: Final[frozenset[tuple[str, str]]] = frozenset({("RE", "longueur_demandee")})
"""(Tâche, emplacement) qui admettent une amorce `config`."""
MOTIF_TEXTE_CONFIG: Final = r"[1-9][0-9]{1,3} mots"
"""Forme du texte d'une amorce `config` : une longueur en mots (10 à 9999)."""

_RE_CLOTURE = re.compile(r"\A```[A-Za-z]*[ \t]*\n(.*)\n[ \t]*```\Z", re.DOTALL)


class Amorce(SchemaBase):
    """Une amorce de `amorces.jsonl` (contrat de la story 9.3)."""

    schema_version: Literal[1]
    amorce_id: Annotated[str, StringConstraints(pattern=MOTIF_AMORCE_ID)]
    tache: Annotated[str, StringConstraints(min_length=1)]
    emplacement: Annotated[str, StringConstraints(pattern=MOTIF_EMPLACEMENT)]
    texte: Annotated[str, StringConstraints(min_length=1)]
    sha_texte: Sha256
    auteur_contenu: AuteurAmorce
    jeu: Annotated[str, StringConstraints(min_length=1)] | None = None
    revision: Annotated[str, StringConstraints(min_length=1)] | None = None
    ligne: Annotated[int, Field(ge=0)] | None = None
    appel_id: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{32}$")] | None = None
    lie_a: Annotated[str, StringConstraints(pattern=MOTIF_AMORCE_ID)] | None = None
    """Amorce `config` seulement : l'amorce jointe avec elle dans le même appel."""

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
        if self.auteur_contenu == "config":
            if self.lie_a is None:
                raise ValueError("amorce config sans lie_a")
            if (self.tache, self.emplacement) not in EMPLACEMENTS_CONFIG:
                raise ValueError("emplacement non admis pour une amorce config")
            if not re.fullmatch(MOTIF_TEXTE_CONFIG, self.texte):
                raise ValueError("texte d'amorce config hors de la forme admise")
        elif self.lie_a is not None:
            raise ValueError("lie_a réservé aux amorces config")
        return self


def texte_de_reponse(contenu: Any, emplacement: str) -> str | None:
    """Valeur (chaîne non vide, sans espaces de bord) de la clé `emplacement` de l'objet JSON
    porté par `contenu`, éventuellement entouré d'une clôture de code ; `None` sinon."""
    if not isinstance(contenu, str):
        return None
    texte = contenu.strip()
    cloture = _RE_CLOTURE.match(texte)
    if cloture:
        texte = cloture.group(1).strip()
    try:
        objet = json.loads(texte)
    except ValueError:
        return None
    valeur = objet.get(emplacement) if isinstance(objet, dict) else None
    if not isinstance(valeur, str) or not valeur.strip():
        return None
    return valeur.strip()


def texte_mistral_conforme(contenu: Any, amorce: Amorce) -> bool:
    """Vrai si le texte de l'amorce `mistral` est le contenu journalisé, ou la valeur de sa
    clé `emplacement` dans l'objet JSON de ce contenu."""
    if contenu == amorce.texte:
        return True
    return texte_de_reponse(contenu, amorce.emplacement) == amorce.texte
