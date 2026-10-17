"""Configuration du pipeline de données : `config/donnees.toml` (AD-17, AD-22, D1.2, D4).

- `[mistral]` : préalables du Générateur (date de vérification des conditions commerciales,
  méthode, URL et SHA de la page relue, liste stable de modèles). Une chaîne vide vaut
  « pas encore vérifié » (`None`) : le Générateur refuse alors de démarrer
  (`slmsp.mistral.generateur.charger_prealables`, qui lit la même table) ;
- `[volumes]` : volumes cibles par Tâche, Traduction exclue ; part `generique` dans
  [0,10 ; 0,20] du total (D4) ;
- `[deduplication]`, `[anti_fuite]` : n-grammes et seuils de l'étape `filter`, dans ]0, 1] ;
- `[relecture]` : échantillon de relecture humaine ;
- `[seed]` : paramètres de l'étape `seed` (longueurs de résumé RE du Jeu, tirées par
  graine ; optionnelle, valeurs par défaut ci-dessous) ;
- `[preferences]` : génération locale de la réponse rejetée des paires ORPO (graine,
  température, longueur maximale ; optionnelle, valeurs par défaut ci-dessous).

Le fichier est lu par `slmsp.core.config.charger_toml` (clés inconnues refusées) : toute
non-conformité lève `ConfigurationInvalide`, sans citer la valeur saisie.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Final, Literal

from pydantic import Field, StrictInt, StringConstraints, field_validator, model_validator

from slmsp.core.config import ModeleConfig, charger_toml, longueurs_re_evaluation, racine_projet
from slmsp.core.items import N_DEFAUT

__all__ = [
    "PART_GENERIQUE_MAX",
    "PART_GENERIQUE_MIN",
    "ConfigDonnees",
    "charger_config_donnees",
]

NOM_DONNEES: Final = "donnees.toml"
PART_GENERIQUE_MIN: Final = 0.10
PART_GENERIQUE_MAX: Final = 0.20

_RE_SHA256 = re.compile(r"[0-9a-f]{64}")

Texte = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Volume = Annotated[StrictInt, Field(ge=0)]
Seuil = Annotated[float, Field(gt=0, le=1, allow_inf_nan=False)]
TailleNgrammes = Annotated[StrictInt, Field(ge=1)]


def _vide_en_none(valeur: Any) -> Any:
    return None if isinstance(valeur, str) and valeur.strip() == "" else valeur


class MistralDonnees(ModeleConfig):
    """Table `[mistral]` : préalables du Générateur (D1.2)."""

    conditions_verifiees_le: date | None
    methode_verification: Texte
    conditions_url: Annotated[str, StringConstraints(pattern=r"^https://\S+$")]
    conditions_sha256: str | None
    modeles_stables: list[Texte] = Field(min_length=1)

    @field_validator("conditions_verifiees_le", "conditions_sha256", mode="before")
    @classmethod
    def _vide(cls, valeur: Any) -> Any:
        return _vide_en_none(valeur)

    @field_validator("conditions_sha256")
    @classmethod
    def _sha(cls, valeur: str | None) -> str | None:
        if valeur is not None and not _RE_SHA256.fullmatch(valeur):
            raise ValueError("SHA-256 attendu : 64 caractères hexadécimaux minuscules, ou vide")
        return valeur

    @model_validator(mode="after")
    def _date_et_sha_ensemble(self) -> MistralDonnees:
        if (self.conditions_verifiees_le is None) != (self.conditions_sha256 is None):
            raise ValueError(
                "conditions_verifiees_le et conditions_sha256 doivent être tous deux "
                "renseignés ou tous deux vides"
            )
        return self


class VolumesDonnees(ModeleConfig):
    """Table `[volumes]` : exemples cibles par Tâche (Traduction exclue)."""

    Q: Volume
    RD: Volume
    CR: Volume
    LC: Volume
    CO: Volume
    RE: Volume
    CT: Volume
    generique: Volume

    @property
    def total(self) -> int:
        """Somme des volumes de toutes les Tâches, `generique` compris."""
        return sum(self.par_tache().values())

    def par_tache(self) -> dict[str, int]:
        """Volumes par Tâche, dans l'ordre du fichier."""
        return {nom: getattr(self, nom) for nom in type(self).model_fields}

    @model_validator(mode="after")
    def _part_generique(self) -> VolumesDonnees:
        total = self.total
        if total == 0:
            raise ValueError("le total des volumes doit être strictement positif")
        part = self.generique / total
        if not PART_GENERIQUE_MIN <= part <= PART_GENERIQUE_MAX:
            raise ValueError(
                f"la part generique doit rester entre {PART_GENERIQUE_MIN:.0%} et "
                f"{PART_GENERIQUE_MAX:.0%} du total (D4)"
            )
        return self


class DeduplicationDonnees(ModeleConfig):
    """Table `[deduplication]` : doublons exacts et proches (motif `doublon`)."""

    n_ngrammes: TailleNgrammes = N_DEFAUT
    seuil_jaccard: Seuil


class AntiFuiteDonnees(ModeleConfig):
    """Table `[anti_fuite]` : fuites du Jeu d'évaluation (`fuite_ngram`, `fuite_cosinus`)."""

    n_ngrammes: TailleNgrammes = N_DEFAUT
    seuil_jaccard: Seuil
    seuil_cosinus: Seuil


class RelectureDonnees(ModeleConfig):
    """Table `[relecture]` : échantillon de relecture humaine (non bloquant)."""

    taille_echantillon: Annotated[StrictInt, Field(ge=1)]
    graine: Annotated[StrictInt, Field(ge=0)]


class PreferencesDonnees(ModeleConfig):
    """Table `[preferences]` : génération de la réponse rejetée (story 9.7)."""

    graine: Annotated[StrictInt, Field(ge=0)] = 42
    """Graine de base ; la paire de rang `i` utilise `graine + i`."""
    temperature: Annotated[float, Field(ge=0, le=2, allow_inf_nan=False)] = 0.8
    max_tokens: Annotated[StrictInt, Field(ge=1)] = 1024


class SeedDonnees(ModeleConfig):
    """Table `[seed]` : paramètres de l'étape `seed` (aucun contenu rédigé)."""

    re_longueurs: list[str] = Field(
        default_factory=lambda: ["courte", "moyenne", "detaillee"], min_length=1
    )
    """Longueurs de résumé tirées pour `RE/longueur_demandee`, dans la forme du Jeu gelé : clés de
    `[re.longueurs]` de `config/evaluation.toml` (sans accent)."""

    @field_validator("re_longueurs")
    @classmethod
    def _longueurs_connues(cls, valeurs: list[str]) -> list[str]:
        connues = set(longueurs_re_evaluation())
        inconnues = [v for v in valeurs if v not in connues]
        if inconnues:
            raise ValueError(
                f"longueurs RE inconnues de [re.longueurs] : {inconnues} "
                f"(admises : {sorted(connues)})"
            )
        return valeurs

    graine: Annotated[StrictInt, Field(ge=0)] = 42
    """Graine du tirage ; une même amorce de texte reçoit toujours la même longueur."""


class ConfigDonnees(ModeleConfig):
    """Contenu de `config/donnees.toml`."""

    schema_version: Literal[1]
    mistral: MistralDonnees
    volumes: VolumesDonnees
    deduplication: DeduplicationDonnees
    anti_fuite: AntiFuiteDonnees
    relecture: RelectureDonnees
    preferences: PreferencesDonnees = Field(default_factory=PreferencesDonnees)
    seed: SeedDonnees = Field(default_factory=SeedDonnees)

    @property
    def total(self) -> int:
        """Volume total visé, toutes Tâches confondues."""
        return self.volumes.total


def charger_config_donnees(chemin: str | Path | None = None) -> ConfigDonnees:
    """Lit `donnees.toml` (défaut : `<racine du projet>/config/donnees.toml`).

    Lève `ConfigurationInvalide` si le fichier est absent, illisible ou non conforme.
    """
    return charger_toml(
        chemin if chemin is not None else racine_projet() / "config" / NOM_DONNEES,
        ConfigDonnees,
    )
