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
  température, longueur maximale ; optionnelle, valeurs par défaut ci-dessous) ;
- `[generateur.plafonds_mots]` : plafond de mots de la réponse cible par Tâche, consigne de
  longueur des gabarits (story 9.10 ; optionnelle, vide par défaut). Le Générateur relit
  la même table (`slmsp.mistral.generateur.charger_plafonds_mots`) ;
- `[juge_donnees]` : juge de données DeepSeek via OpenRouter (story O1, `slmsp data juger`),
  réglages d'appel et seuils d'acceptation par Tâche (`[juge_donnees.seuils.<TACHE>]`, note
  `>=` seuil ; optionnelle, valeurs par défaut ci-dessous).
- `[alignement]` : alignement entraînement / évaluation (story O5) : formulations génériques
  de consigne d'Agent rendues dans le message user (`consignes_agent`, par Tâche, tirées par
  graine) et longueur visée des textes sources LC (`longueur_sources_lc`). Optionnelle, vide
  par défaut (rien n'est aligné).

Le fichier est lu par `slmsp.core.config.charger_toml` (clés inconnues refusées) : toute
non-conformité lève `ConfigurationInvalide`, sans citer la valeur saisie.
"""

from __future__ import annotations

import math
import re
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Final, Literal

from pydantic import Field, StrictInt, StringConstraints, field_validator, model_validator

from slmsp.core.config import ModeleConfig, charger_toml, plafonds_re_evaluation, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.items import N_DEFAUT

__all__ = [
    "CRITERES_JUGE_DONNEES",
    "TACHES_A_CONSIGNE",
    "TACHES_PLAFONNABLES",
    "PART_GENERIQUE_MAX",
    "PART_GENERIQUE_MIN",
    "AlignementDonnees",
    "ConfigDonnees",
    "JugeDonneesConfig",
    "LongueurSourcesLC",
    "charger_config_donnees",
]

NOM_DONNEES: Final = "donnees.toml"
PART_GENERIQUE_MIN: Final = 0.10
PART_GENERIQUE_MAX: Final = 0.20
TACHES_PLAFONNABLES: Final = ("Q", "RD", "CR", "LC", "CT", "generique")
"""Tâches admises dans `[generateur.plafonds_mots]` : CO suit la longueur de son texte, RE a
son propre plafond (`longueur_demandee`)."""

CRITERES_JUGE_DONNEES: Final[dict[str, dict[str, int]]] = {
    "CR": {"invention": 1, "structure": 1},
    "LC": {"fidelite": 2, "termes": 1},
    "CT": {"conformite": 2, "invention": 1},
}
"""Critères notés par le juge de données (story O1), par Tâche : note maximale (0 à max).
CR a en plus `couverture` (rappel calculé par le code, dans [0, 1])."""
CRITERES_CALCULES: Final[dict[str, frozenset[str]]] = {"CR": frozenset({"couverture"})}
TACHES_A_CONSIGNE: Final = ("CR", "LC", "CT", "RE", "CO")
"""Tâches dont le prompt déclare l'emplacement `consigne` et dont l'évaluation en porte une."""

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
        # ValueError sans la valeur saisie (règle de `charger_toml`) ; un evaluation.toml
        # illisible (ConfigurationInvalide) est converti de même.
        try:
            connues = set(plafonds_re_evaluation())
        except ConfigurationInvalide:
            raise ValueError("[re.longueurs] de evaluation.toml illisible") from None
        if any(v not in connues for v in valeurs):
            raise ValueError("longueur RE inconnue de [re.longueurs] de evaluation.toml")
        return valeurs

    graine: Annotated[StrictInt, Field(ge=0)] = 42
    """Graine du tirage ; une même amorce de texte reçoit toujours la même longueur."""


class GenerateurDonnees(ModeleConfig):
    """Table `[generateur]` : plafonds de mots des réponses cibles (story 9.10)."""

    plafonds_mots: dict[str, Annotated[StrictInt, Field(gt=0)]] = Field(default_factory=dict)
    """Plafond de mots par Tâche (`TACHES_PLAFONNABLES`), consigne de longueur seulement."""

    @field_validator("plafonds_mots")
    @classmethod
    def _taches_connues(cls, valeurs: dict[str, int]) -> dict[str, int]:
        if any(tache not in TACHES_PLAFONNABLES for tache in valeurs):
            raise ValueError(f"tâche inconnue (attendu parmi : {', '.join(TACHES_PLAFONNABLES)})")
        return valeurs


def _seuils_defaut() -> dict[str, dict[str, float]]:
    return {
        "CR": {"invention": 1, "structure": 1, "couverture": 0.8},
        "LC": {"fidelite": 2, "termes": 1},
        "CT": {"conformite": 2, "invention": 1},
    }


class JugeDonneesConfig(ModeleConfig):
    """Table `[juge_donnees]` : juge de données DeepSeek via OpenRouter (story O1).

    La réservation au registre compte toujours `max_tokens` ; l'estimation affichée compte
    `sortie_estimee + marge_raisonnement` tokens de sortie (bornés par `max_tokens`).
    """

    modele: Texte = "deepseek/deepseek-v4-pro"
    temperature: float | None = Field(default=0.0, ge=0, le=0, allow_inf_nan=False)
    max_tokens: Annotated[StrictInt, Field(ge=1)] = 16000
    effort_raisonnement: Literal["minimal", "low", "medium", "high"] | None = "low"
    format_reponse: Literal["json_schema", "json_object"] = "json_schema"
    sortie_estimee: Annotated[StrictInt, Field(ge=1)] = 1500
    marge_raisonnement: Annotated[StrictInt, Field(ge=0)] = 8000
    usage_budget: Texte = "juge-donnees-openrouter"
    seuils: dict[str, dict[str, Annotated[float, Field(ge=0, allow_inf_nan=False)]]] = Field(
        default_factory=_seuils_defaut
    )

    @field_validator("seuils")
    @classmethod
    def _seuils_connus(cls, valeurs: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
        for tache, seuils in valeurs.items():
            criteres = CRITERES_JUGE_DONNEES.get(tache)
            if criteres is None:
                raise ValueError(
                    f"tâche inconnue (attendu parmi : {', '.join(CRITERES_JUGE_DONNEES)})"
                )
            calcules = CRITERES_CALCULES.get(tache, frozenset())
            for critere, seuil in seuils.items():
                if critere in calcules:
                    if seuil > 1:
                        raise ValueError(f"seuil {tache}.{critere} hors de [0, 1]")
                elif critere not in criteres:
                    raise ValueError(f"critère inconnu pour {tache}")
                elif seuil > criteres[critere]:
                    raise ValueError(f"seuil {tache}.{critere} au-delà de la note maximale")
        # Fusion par critère : une Tâche absente, ou un critère absent d'une Tâche surchargée,
        # garde son seuil par défaut (une table partielle ne retire aucun seuil).
        fusion = _seuils_defaut()
        for tache, seuils in valeurs.items():
            fusion[tache].update(seuils)
        for tache, seuils in fusion.items():
            if not any(seuil > 0 for seuil in seuils.values()):
                raise ValueError(f"seuils {tache} tous nuls : la Tâche accepterait tout")
        return fusion

    @property
    def sortie_estimation(self) -> int:
        """Tokens de sortie comptés par candidat dans l'estimation (raisonnement compris)."""
        return min(self.max_tokens, self.sortie_estimee + self.marge_raisonnement)

    @property
    def effort_cle(self) -> str:
        """Part « effort » de la clé du cache : température, effort et format de réponse."""
        temperature = "sans" if self.temperature is None else f"{self.temperature:g}"
        effort = self.effort_raisonnement or "aucun"
        return f"temperature-{temperature}+effort-{effort}+{self.format_reponse}"


class LongueurSourcesLC(ModeleConfig):
    """Longueur visée des textes sources LC : médiane d'évaluation ± `tolerance`."""

    mediane_mots: Annotated[StrictInt, Field(ge=1)]
    """Médiane (mots) de l'entrée LC du Jeu d'évaluation (statistique, jamais un texte)."""
    tolerance: Annotated[float, Field(gt=0, lt=1, allow_inf_nan=False)] = 0.3
    """Écart relatif admis autour de la médiane (0,3 = ± 30 %)."""

    @property
    def mots_min(self) -> int:
        return max(1, math.ceil(self.mediane_mots * (1 - self.tolerance)))

    @property
    def mots_max(self) -> int:
        return math.floor(self.mediane_mots * (1 + self.tolerance))


class AlignementDonnees(ModeleConfig):
    """Table `[alignement]` : mêmes consignes d'Agent et mêmes longueurs qu'à l'évaluation."""

    graine: Annotated[StrictInt, Field(ge=0)] = 42
    """Graine du tirage de la consigne : une même session reçoit toujours la même."""
    consignes_agent: dict[str, list[Texte]] = Field(default_factory=dict)
    """Formulations génériques d'outillage (des consignes, jamais des réponses), par Tâche de
    `TACHES_A_CONSIGNE` ; une Tâche absente n'a pas de consigne à l'entraînement."""
    longueur_sources_lc: LongueurSourcesLC | None = None

    @field_validator("consignes_agent")
    @classmethod
    def _consignes_valides(cls, valeurs: dict[str, list[str]]) -> dict[str, list[str]]:
        if any(tache not in TACHES_A_CONSIGNE for tache in valeurs):
            raise ValueError(f"tâche inconnue (attendu parmi : {', '.join(TACHES_A_CONSIGNE)})")
        if any(not variantes for variantes in valeurs.values()):
            raise ValueError("au moins une formulation par Tâche")
        return valeurs


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
    generateur: GenerateurDonnees = Field(default_factory=GenerateurDonnees)
    juge_donnees: JugeDonneesConfig = Field(default_factory=JugeDonneesConfig)
    alignement: AlignementDonnees = Field(default_factory=AlignementDonnees)

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
