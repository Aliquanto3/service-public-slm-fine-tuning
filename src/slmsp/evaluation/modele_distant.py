"""Référence `distant:<slug>` : modèle servi par une API compatible OpenAI (story 17.1).

`<slug>` désigne la fiche `config/modeles-distants/<slug>.toml` (`FicheDistante`) :
fournisseur (`openrouter`, `mistral` ou `ovh`, story 17.1b), identifiant du modèle chez lui,
hébergeur épinglé et quantification annoncée (OpenRouter seulement : nom renvoyé dans
`provider`), protocole d'outils (`natif`), raisonnement (`off`) et contexte (borne de
l'estimation des tokens d'entrée). Chez `mistral` et `ovh`, l'hébergeur est le fournisseur
lui-même : aucun hébergeur épinglé, aucun contrôle de `provider`.

Un modèle distant n'a ni GGUF, ni quantification llama.cpp, ni variante : seule la phase
génération de `slmsp eval run` l'accepte (`modele_ref.resoudre` le refuse). Ses sorties
servent à la mesure, jamais à l'entraînement (D1).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, StringConstraints, model_validator

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.evaluation.modele_ref import MOTIF_REF
from slmsp.fournisseurs.client import OPENROUTER, ConfigFournisseur
from slmsp.inference.fournisseurs import PRESETS

PREFIXE: Final = "distant:"
DOSSIER_FICHES: Final = Path("config") / "modeles-distants"
MOTIF_MODELE_OPENROUTER: Final = re.compile(r"^[a-z0-9._-]+/[a-z0-9._:-]+$")


def _config(nom: str, nom_secret: str) -> ConfigFournisseur:
    url = PRESETS[nom].url_base
    assert url is not None
    return ConfigFournisseur(nom=nom, base_url=url, nom_secret=nom_secret)


FOURNISSEURS_DISTANTS: Final[dict[str, ConfigFournisseur]] = {
    "openrouter": OPENROUTER,
    "mistral": _config("mistral", "MISTRAL_API_KEY"),
    "ovh": _config("ovh", "OVH_AI_ENDPOINTS_ACCESS_TOKEN"),
}
"""Fournisseurs d'un modèle distant : URL de base (presets de la story 17.4) et secret."""


class FicheDistante(ModeleConfig):
    """Contenu de `config/modeles-distants/<slug>.toml`."""

    schema_version: Literal[1]
    fournisseur: Literal["openrouter", "mistral", "ovh"]
    modele_id: Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9._-]+(/[A-Za-z0-9._:-]+)?$")]
    hebergeur: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] | None = None
    """Nom de l'hébergeur tel qu'OpenRouter le renvoie dans `provider` (ex. `DeepInfra`) ;
    exigé chez OpenRouter, refusé ailleurs."""
    quantification: Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+$")] | None = None
    """Quantification annoncée (filtre `provider.quantizations` d'OpenRouter : `fp8`…) ;
    exigée chez OpenRouter, facultative ailleurs (consignée seulement)."""
    protocole_outils: Literal["natif"] = "natif"
    reasoning: Literal["off"] = "off"
    contexte: int = Field(gt=0)
    """Contexte du modèle (tokens) : borne l'estimation des tokens d'entrée réservés."""

    @model_validator(mode="after")
    def _selon_fournisseur(self) -> FicheDistante:
        if self.fournisseur == "openrouter":
            if not MOTIF_MODELE_OPENROUTER.fullmatch(self.modele_id):
                raise ValueError("modele_id OpenRouter attendu sous la forme famille/modèle")
            if self.hebergeur is None or self.quantification is None:
                raise ValueError("hebergeur et quantification exigés chez OpenRouter")
        else:
            if self.hebergeur is not None:
                raise ValueError(f"aucun hébergeur épinglé chez {self.fournisseur}")
            if self.modele_id.lower().endswith("latest"):
                raise ValueError("alias mouvant (latest) refusé : épingler une version")
        return self

    @property
    def epingle(self) -> bool:
        """Vrai si l'hébergeur est épinglé et contrôlé dans `provider` (OpenRouter)."""
        return self.fournisseur == "openrouter"

    @property
    def hebergeur_consigne(self) -> str:
        """Hébergeur consigné au run : l'épinglé, ou le fournisseur lui-même."""
        return self.hebergeur or self.fournisseur


@dataclass(frozen=True)
class ModeleDistant:
    """Modèle distant résolu : référence, fiche, fichier et son SHA-256, fournisseur."""

    ref: str
    slug: str
    fiche: FicheDistante
    chemin: Path
    sha256: str
    fournisseur: ConfigFournisseur

    @property
    def slug_run(self) -> str:
        return f"distant-{self.slug}"


def est_distant(ref: object) -> bool:
    """Vrai pour une référence `distant:<…>` (sans la valider)."""
    return isinstance(ref, str) and ref.startswith(PREFIXE)


def chemin_fiche(slug: str) -> Path:
    return racine_projet() / DOSSIER_FICHES / f"{slug}.toml"


def sha256_fichier(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def resoudre_distant(ref: str) -> ModeleDistant:
    """Résout `distant:<slug>` ; `ValueError` (forme), `ConfigurationInvalide` (fiche)."""
    if not est_distant(ref) or not MOTIF_REF.fullmatch(ref):
        raise ValueError(f"référence distante invalide : {ref!r} (distant:<slug>)")
    slug = ref.removeprefix(PREFIXE)
    chemin = chemin_fiche(slug)
    fiche = charger_toml(chemin, FicheDistante)
    return ModeleDistant(
        ref, slug, fiche, chemin, sha256_fichier(chemin), FOURNISSEURS_DISTANTS[fiche.fournisseur]
    )


__all__ = [
    "FOURNISSEURS_DISTANTS",
    "PREFIXE",
    "FicheDistante",
    "ModeleDistant",
    "chemin_fiche",
    "est_distant",
    "resoudre_distant",
    "sha256_fichier",
]
