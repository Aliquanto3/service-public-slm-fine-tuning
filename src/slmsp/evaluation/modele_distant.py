"""Référence `distant:<slug>` : modèle servi par une API compatible OpenAI (story 17.1).

`<slug>` désigne la fiche `config/modeles-distants/<slug>.toml` (`FicheDistante`) :
fournisseur (`openrouter` seul ici), identifiant du modèle chez lui, hébergeur épinglé
(nom renvoyé par OpenRouter dans `provider`), quantification annoncée, protocole d'outils
(`natif`), raisonnement (`off`) et contexte (borne de l'estimation des tokens d'entrée).

Un modèle distant n'a ni GGUF, ni quantification llama.cpp, ni variante : seule la phase
génération de `slmsp eval run` l'accepte (`modele_ref.resoudre` le refuse). Ses sorties
servent à la mesure, jamais à l'entraînement (D1).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, StringConstraints

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.evaluation.modele_ref import MOTIF_REF
from slmsp.fournisseurs.client import FOURNISSEURS, ConfigFournisseur

PREFIXE: Final = "distant:"
DOSSIER_FICHES: Final = Path("config") / "modeles-distants"


class FicheDistante(ModeleConfig):
    """Contenu de `config/modeles-distants/<slug>.toml`."""

    schema_version: Literal[1]
    fournisseur: Literal["openrouter"]
    modele_id: Annotated[str, StringConstraints(pattern=r"^[a-z0-9._-]+/[a-z0-9._:-]+$")]
    hebergeur: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    """Nom de l'hébergeur tel qu'OpenRouter le renvoie dans `provider` (ex. `DeepInfra`)."""
    quantification: Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+$")]
    """Quantification annoncée (filtre `provider.quantizations` d'OpenRouter : `fp8`…)."""
    protocole_outils: Literal["natif"] = "natif"
    reasoning: Literal["off"] = "off"
    contexte: int = Field(gt=0)
    """Contexte du modèle (tokens) : borne l'estimation des tokens d'entrée réservés."""


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
        ref, slug, fiche, chemin, sha256_fichier(chemin), FOURNISSEURS[fiche.fournisseur]
    )


__all__ = [
    "PREFIXE",
    "FicheDistante",
    "ModeleDistant",
    "chemin_fiche",
    "est_distant",
    "resoudre_distant",
    "sha256_fichier",
]
