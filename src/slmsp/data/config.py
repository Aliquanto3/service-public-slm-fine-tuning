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
- `[verification]` : contrôles déterministes des cibles CR, LC, CT avant le juge de données
  (story O6a, `slmsp data generate --verifiee`) ; optionnelle, règles par défaut ci-dessous.

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
    "CODES_VALIDATE",
    "CODES_VERIFICATION",
    "CRITERES_JUGE_DONNEES",
    "TACHES_A_CONSIGNE",
    "TACHES_PLAFONNABLES",
    "PART_GENERIQUE_MAX",
    "PART_GENERIQUE_MIN",
    "AlignementDonnees",
    "ConfigDonnees",
    "CandidatsDonnees",
    "JugeAlternatif",
    "JugeDonneesConfig",
    "LongueurSourcesLC",
    "VerificationConfig",
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


class JugeAlternatif(ModeleConfig):
    """Table `[juge_donnees.juges.<nom>]` : réglages d'un autre juge OpenRouter (story 15.2).

    Chaque champ présent remplace celui de `[juge_donnees]` ; les seuils et la grille restent
    ceux du juge de données.
    """

    modele: Texte
    temperature: Annotated[float, Field(ge=0, le=0, allow_inf_nan=False)] | None = 0.0
    max_tokens: Annotated[StrictInt, Field(ge=1)] = 16000
    effort_raisonnement: Literal["minimal", "low", "medium", "high"] | None = None
    sortie_estimee: Annotated[StrictInt, Field(ge=1)] = 1500
    marge_raisonnement: Annotated[StrictInt, Field(ge=0)] = 0


class CandidatsDonnees(ModeleConfig):
    """Table `[candidats]` : candidats multiples de la sélection des cibles (story 15.2)."""

    graine: Annotated[StrictInt, Field(ge=0)] = 42
    """Graine de base ; la ligne de rang `i` utilise `graine + i` (comme `[preferences]`)."""
    max_tokens: Annotated[StrictInt, Field(ge=1)] = 1024
    """Longueur maximale d'un candidat de la base locale."""
    modele_openrouter: Texte = "deepseek/deepseek-v4-pro"
    temperature_openrouter: Annotated[float, Field(ge=0, le=2, allow_inf_nan=False)] = 0.3
    max_tokens_openrouter: Annotated[StrictInt, Field(ge=1)] = 8000
    """Sortie maximale, raisonnement compris ; réservée au registre à chaque appel (pire cas)."""
    effort_raisonnement: Literal["minimal", "low", "medium", "high"] | None = "low"
    usage_budget: Texte = "generateur-openrouter"
    appels_paralleles: Annotated[StrictInt, Field(ge=1, le=32)] = 4
    delai_lecture: float = Field(default=900.0, gt=0, allow_inf_nan=False)
    delai_appel: float = Field(default=900.0, gt=0, allow_inf_nan=False)
    duree_totale_max_appel: float = Field(default=1800.0, gt=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def _delais_coherents(self) -> CandidatsDonnees:
        if self.duree_totale_max_appel < self.delai_appel:
            raise ValueError("duree_totale_max_appel inférieure à delai_appel")
        return self


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
    delai_lecture: float = Field(default=900.0, gt=0, allow_inf_nan=False)
    """Délai de lecture HTTP (s) : DeepSeek V4 Pro raisonne ~2,8 min par appel (calibrage O1)."""
    delai_appel: float = Field(default=900.0, gt=0, allow_inf_nan=False)
    """Délai total d'une tentative (s)."""
    duree_totale_max_appel: float = Field(default=1800.0, gt=0, allow_inf_nan=False)
    """Durée maximale d'un appel, réessais compris (s) ; au moins `delai_appel`."""
    appels_paralleles: Annotated[StrictInt, Field(ge=1, le=32)] = 8
    """Jugements menés en parallèle (threads) ; verdicts écrits dans l'ordre des candidats."""
    seuils: dict[str, dict[str, Annotated[float, Field(ge=0, allow_inf_nan=False)]]] = Field(
        default_factory=_seuils_defaut
    )
    juges: dict[str, JugeAlternatif] = Field(default_factory=dict)
    """Autres juges, choisis par `data juger --juge <nom>` (`deepseek` : cette table)."""

    def pour_juge(self, nom: str) -> JugeDonneesConfig:
        """Configuration du juge `nom` (`deepseek` : celle-ci) ; `ValueError` si inconnu."""
        if nom == "deepseek":
            return self
        alternatif = self.juges.get(nom)
        if alternatif is None:
            connus = ", ".join(["deepseek", *sorted(self.juges)])
            raise ValueError(f"juge inconnu : {nom!r} (attendu parmi : {connus})")
        return self.model_copy(update=alternatif.model_dump())

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

    @model_validator(mode="after")
    def _delais_coherents(self) -> JugeDonneesConfig:
        if self.duree_totale_max_appel < self.delai_appel:
            raise ValueError("duree_totale_max_appel inférieure à delai_appel")
        return self

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


# --- Vérification des cibles (story O6a) ---------------------------------------------------

CODES_VALIDATE: Final = frozenset(
    {
        "url_inventee",
        "valeur_absente",
        "cr_sections_manquantes",
        "ct_format_incomplet",
        "lc_valeur_perdue",
    }
)
"""Codes partagés avec `validate` : toujours bloquants (une cible acceptée par la vérification
n'est jamais rejetée ensuite par `validate`)."""
CODES_VERIFICATION: Final = frozenset(
    CODES_VALIDATE
    | {
        "nom_absent",
        "cr_sections_desordre",
        "cr_plafond_mots",
        "cr_actions_vide",
        "lc_modalite_perdue",
        "lc_modalite_reduite",
        "lc_conseil_ajoute",
        "lc_titre",
        "lc_gain_lisibilite",
        "ct_blocs",
        "ct_sans_emplacement",
    }
)
"""Codes des contrôles déterministes de `slmsp.data.verification`."""


def _exceptions_noms_defaut() -> list[str]:
    titres = (
        "Participants Points Décisions Décision Actions Action Objet Références Référence Réf "
        "Ordre Compte Rendu Synthèse Contexte Pièces Pièce Signature Responsable Échéance Copie"
    )
    civilites = (
        "M MM Mme Mmes Mlle Madame Monsieur Mesdames Messieurs Maître Docteur Dr Me Pr N V Cf "
        "Tél Courriel"
    )
    calendrier = (
        "Janvier Février Mars Avril Mai Juin Juillet Août Septembre Octobre Novembre Décembre "
        "Lundi Mardi Mercredi Jeudi Vendredi Samedi Dimanche"
    )
    institutions = "État République Française Français"
    return f"{titres} {civilites} {calendrier} {institutions}".split()


def _lc_marqueurs_defaut() -> dict[str, list[str]]:
    return {
        "condition": [
            r"\bsi\b",
            r"\bs['’]ils?\b",
            r"\bsauf\b",
            r"\bà condition\b",
            r"\bsous réserve\b",
            r"\ben cas d(?:e\b|['’])",
            r"\blorsqu(?:e\b|['’])",
            r"\bquand\b",
            r"\bdès qu(?:e\b|['’])",
            r"\bau cas où\b",
        ],
        "restriction": [
            r"\buniquement\b",
            r"\bseulement\b",
            r"\bexclusivement\b",
            r"\bseule?s?\b",
            r"\bne\b[^.;!?\n]{0,60}?\bqu(?:e\b|['’])",
            r"\bn['’][^.;!?\n]{0,60}?\bqu(?:e\b|['’])",
        ],
        "obligation": [
            r"\bdoi(?:t|s|vent)\b",
            r"\bdev(?:ez|ons|oir|ra|ras|rez|rons|ront|rait|raient)\b",
            r"\bobligatoires?\b",
            r"\bobligatoirement\b",
            r"\bobligations?\b",
            r"\bobligée?s?\b",
            r"\btenue?s? d(?:e\b|['’])",
            r"\bil (?:vous )?(?:faut|faudra)\b",
            r"\bnécessaires?\b",
        ],
        "permission": [
            r"\bpeu(?:t|x|vent)\b",
            r"\bpouv(?:ez|ons|oir|ait|aient)\b",
            r"\bpourr(?:a|as|ez|ons|ont|ait|aient)\b",
            r"\bpossibles?\b",
            r"\bpossibilités?\b",
            r"\b(?:avez|avons|a|ont|avoir|aurez|aura|auront) (?:le )?droit\b",
            r"\bautorisée?s?\b",
        ],
        "interdiction": [
            r"\binterdite?s?\b",
            r"\binterdiction\b",
            r"\bdéfendu\b",
            r"\bne (?:peu\w*|pouv\w*|pourr\w*|doi\w*|dev\w*) pas\b",
            r"\bpas (?:le )?droit\b",
            r"\bn['’](?:est|êtes|sont) pas (?:autorisé|permis)",
        ],
        "echeance": [
            r"\bau plus tard\b",
            r"\bavant (?:le|la|l['’]|ce|cette)\b",
            r"\bdans un délai\b",
            r"\bdélais?\b",
            r"\bjusqu['’]",
        ],
    }


def _lc_conseils_defaut() -> list[str]:
    return [
        r"\bnous vous conseillons\b",
        r"\bn['’]hésitez pas\b",
        r"\bpensez à\b",
        r"\bil est recommandé\b",
        r"\bnous vous recommandons\b",
        r"\bil est conseillé\b",
    ]


def _ct_blocs_defaut() -> dict[str, str]:
    return {
        "lieu_date": (
            r"^[^\n]{0,60}\ble\s+(?:\[[^\]\n]+\]|\d{1,2}(?:er)?\s+[^\W\d_]+\s+\d{4}"
            r"|\d{1,2}/\d{1,2}/\d{4})[ .*_]*$"
        ),
        "objet": r"^[#*_\s]*objet\b[^\n:]{0,40}:",
        "references": (
            r"^[#*_\s\[]*(?:[nv]\s*/\s*|vos\s+|nos\s+)?r[ée]f(?:[ée]rences?|\.)?(?![^\W_])"
        ),
        "appel": (
            r"^[#*_\s]*(?:madame|monsieur|mesdames|messieurs|ma[iî]tre|docteur"
            r"|\[[^\]\n]*(?:civilit|appel)[^\]\n]*\])[^\n]{0,60},[*_\s]*$"
        ),
        "politesse": (
            r"\b(?:agr[ée]er|salutations|consid[ée]ration|sentiments|cordialement"
            r"|respectueusement)\b"
        ),
        "signature": (
            r"^[#*_\s]*(?:\[[^\]\n]*(?:signat|nom|qualit|fonction|pr[ée]nom)[^\]\n]*\]"
            r"|l[ea]\s+\S+|p\.?\s*o\.?\s|pour\s+l[ea]\b|sign(?:[ée]|ature\b))"
        ),
    }


def _expressions_valides(expressions: list[str]) -> None:
    for expression in expressions:
        try:
            re.compile(expression)
        except re.error:
            raise ValueError("expression régulière invalide") from None


class VerificationConfig(ModeleConfig):
    """Table `[verification]` : contrôles déterministes des cibles CR, LC, CT (story O6a).

    Règles d'outillage (expressions et listes), jamais un exemple de réponse (D1).
    """

    essais_max: Annotated[StrictInt, Field(ge=1, le=3)] = 3
    """Essais par session au total : 1 essai puis au plus 2 régénérations (story O6b)."""
    gain_km_min: Annotated[float, Field(allow_inf_nan=False)] = 10.0
    """Gain de Kandel-Moles minimal d'une cible LC (copie de `gain_km_min` d'`evaluation.toml` :
    le paquet `data` ne lit pas la config d'évaluation)."""
    graine: Annotated[StrictInt, Field(ge=0)] = 42
    """Graine des tirages de `echantillon.md` et `calibrage.md`."""
    echantillon: Annotated[StrictInt, Field(ge=0)] = 5
    """Cibles retenues tirées par Tâche, et cibles écartées tirées, dans `echantillon.md`."""
    calibrage: Annotated[StrictInt, Field(ge=0)] = 20
    """Refus tirés dans `calibrage.md`."""
    non_bloquants: list[str] = Field(
        default_factory=lambda: ["nom_absent", "lc_gain_lisibilite", "lc_modalite_perdue"]
    )
    """Codes non bloquants : consignés (verification.jsonl, rapport) sans refuser la cible ;
    ni transmis au juge ni à la régénération."""
    exceptions_noms: list[Texte] = Field(default_factory=_exceptions_noms_defaut)
    """Mots capitalisés jamais tenus pour des noms propres (casse et accents ignorés)."""
    lc_marqueurs: dict[str, list[Texte]] = Field(default_factory=_lc_marqueurs_defaut)
    """Classes de modalité et de condition LC : expressions régulières par classe."""
    lc_conseils: list[Texte] = Field(default_factory=_lc_conseils_defaut)
    """Formules de conseil refusées dans une cible LC quand la source ne les porte pas."""
    ct_blocs: dict[str, Texte] = Field(default_factory=_ct_blocs_defaut)
    """Blocs détectables d'un CT, dans l'ordre attendu (expressions régulières)."""

    @field_validator("non_bloquants")
    @classmethod
    def _codes_connus(cls, codes: list[str]) -> list[str]:
        if any(code not in CODES_VERIFICATION for code in codes):
            raise ValueError("code de vérification inconnu")
        if any(code in CODES_VALIDATE for code in codes):
            raise ValueError("un code partagé avec validate reste bloquant")
        return codes

    @field_validator("lc_marqueurs")
    @classmethod
    def _marqueurs_valides(cls, valeurs: dict[str, list[str]]) -> dict[str, list[str]]:
        for expressions in valeurs.values():
            if not expressions:
                raise ValueError("au moins une expression par classe")
            _expressions_valides(expressions)
        return valeurs

    @field_validator("lc_conseils")
    @classmethod
    def _conseils_valides(cls, valeurs: list[str]) -> list[str]:
        _expressions_valides(valeurs)
        return valeurs

    @field_validator("ct_blocs")
    @classmethod
    def _blocs_valides(cls, valeurs: dict[str, str]) -> dict[str, str]:
        _expressions_valides(list(valeurs.values()))
        return valeurs


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


class AlignementCtDonnees(ModeleConfig):
    """Table `[alignement_ct]` : origines admises de la formulation de `data build --aligner-ct`.

    Liste fermée tenue par Anaël (D1) : la commande refuse toute origine absente de la liste,
    donc tout alignement tant qu'elle est vide (défaut).
    """

    origines_admises: list[Texte] = Field(default_factory=list)


class ConfigDonnees(ModeleConfig):
    """Contenu de `config/donnees.toml`."""

    schema_version: Literal[1]
    mistral: MistralDonnees
    volumes: VolumesDonnees
    deduplication: DeduplicationDonnees
    anti_fuite: AntiFuiteDonnees
    relecture: RelectureDonnees
    preferences: PreferencesDonnees = Field(default_factory=PreferencesDonnees)
    candidats: CandidatsDonnees = Field(default_factory=CandidatsDonnees)
    seed: SeedDonnees = Field(default_factory=SeedDonnees)
    generateur: GenerateurDonnees = Field(default_factory=GenerateurDonnees)
    juge_donnees: JugeDonneesConfig = Field(default_factory=JugeDonneesConfig)
    alignement: AlignementDonnees = Field(default_factory=AlignementDonnees)
    alignement_ct: AlignementCtDonnees = Field(default_factory=AlignementCtDonnees)
    verification: VerificationConfig = Field(default_factory=VerificationConfig)

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
