"""Constantes du Jeu d'évaluation (SPEC §2, §5.4, §7), chemins du gel, config de notation.

Les cibles reprennent celles de `eval/outils/construire_jeu.py` (outil hors paquet, jamais
importé). Les parts sont des fractions exactes : `ceil(0,2 × 15)` vaut 3, pas 4.

`charger_evaluation` lit `config/evaluation.toml` (story 5.6) : équivalences typographiques
de la Correction, plafonds de longueur des résumés et seuils des Scores de Tâche.
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, StringConstraints

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.core.items import CODES_THEMATIQUES

CIBLES: Final[Mapping[str, tuple[int, int, int]]] = {
    "Q": (20, 25, 15),
    "RD": (15, 15, 10),
    "CR": (8, 10, 7),
    "LC": (8, 10, 7),
    "CO": (5, 5, 5),
    "RE": (5, 5, 5),
    "CT": (5, 5, 5),
    "NR": (10, 10, 10),
}
"""SPEC §2 : items visés par Tâche, en (facile, moyen, difficile)."""

CIBLE_Q_SANS_REPONSE: Final = 8
CIBLE_Q_PART_AMORCES: Final = Fraction(1, 2)
"""Au moins la moitié des Q viennent d'amorces réelles (SPEC §2, profil des amorces)."""
CORPUS_AMORCES: Final[tuple[str, ...]] = ("sp_questions_corpus", "assistant_ia_questions_corpus")
CIBLE_RD_VALEURS: Final = 5
CIBLE_RD_REPLI: Final = 4
CIBLE_RD_PRODUCTEURS: Final = 6
"""Minimum de producteurs de données distincts parmi les RD."""
CIBLE_CR_LONGUES: Final = 5
SEUIL_CR_LONGUE_MOTS: Final = 4000
"""Une transcription CR est longue au-delà de ce nombre de mots (`core.texte.compter_mots`,
sur les textes de `entree` hors `consigne`)."""

PARTS_THEMES: Final[Mapping[str, Fraction]] = {
    "social-autonomie": Fraction(30, 100),
    "etat-civil-papiers": Fraction(15, 100),
    "travail-emploi": Fraction(15, 100),
    "collectivites": Fraction(15, 100),
    "famille-education-sante": Fraction(15, 100),
    "fiscalite-locale": Fraction(10, 100),
}
"""SPEC §2 : part visée de chaque thème parmi les Tâches thématiques (mêmes slugs, même
ordre que `slmsp.core.items.THEMES` ; un test le vérifie)."""

TACHES_THEMATIQUES: Final[tuple[str, ...]] = CODES_THEMATIQUES

TACHES_JUGEES: Final[tuple[str, ...]] = ("Q", "CR", "LC", "RE", "CT", "NR")
"""Tâches notées par un Juge (RD et CO sont notées par contrôles automatiques)."""

PART_SECOND_JUGE: Final = Fraction(1, 5)
MIN_SECOND_JUGE: Final = 3
"""Second juge : par Tâche jugée présente, `min(n, max(3, ceil(n / 5)))` items."""
PART_RELECTURE: Final = Fraction(1, 5)
MIN_RELECTURE: Final = 1
"""Relecture humaine : par strate Tâche × difficulté, `min(n, max(1, ceil(n / 5)))`."""

STATUTS_GEL: Final[tuple[str, ...]] = ("provisoire", "relu")
"""`provisoire` : écarts de composition inscrits, non bloquants ; `relu` : bloquants."""

NOM_MANIFESTE: Final = "MANIFEST.json"
NOM_ITEMS: Final = "items.jsonl"


def dossier_jeu(racine: Path, version: str) -> Path:
    """`<racine>/eval/jeu/<version>/`."""
    return racine / "eval" / "jeu" / version


def chemin_manifeste(racine: Path, version: str) -> Path:
    """`<racine>/eval/jeu/<version>/MANIFEST.json`."""
    return dossier_jeu(racine, version) / NOM_MANIFESTE


def chemin_revue(racine: Path, version: str) -> Path:
    """Export de relecture : `<racine>/eval/revue/echantillon-revue-<version>.md`."""
    return racine / "eval" / "revue" / f"echantillon-revue-{version}.md"


def chemin_grille(racine: Path) -> Path:
    """Grille du Juge hachée dans le manifeste : `<racine>/eval/grille-juge-v1.md`."""
    return racine / "eval" / "grille-juge-v1.md"


def chemin_config_outils(racine: Path) -> Path:
    """Outils MCP figés : `<racine>/config/outils-mcp.toml`."""
    return racine / "config" / "outils-mcp.toml"


# --- Notation : `config/evaluation.toml` (story 5.6) ------------------------------------------

NOM_EVALUATION: Final = "evaluation.toml"


class ConfigCO(ModeleConfig):
    """Section `[co]` : équivalences typographiques de la Correction (motif → forme commune)."""

    equivalences: dict[Annotated[str, StringConstraints(min_length=1)], str] = Field(
        default_factory=dict
    )


class LongueursRE(ModeleConfig):
    """Section `[re.longueurs]` : plafond de mots d'un résumé par longueur demandée."""

    courte: int = Field(ge=1)
    moyenne: int = Field(ge=1)
    detaillee: int = Field(ge=1)


class ConfigRE(ModeleConfig):
    """Section `[re]`."""

    longueurs: LongueursRE


class Seuils(ModeleConfig):
    """Section `[seuils]` : kappa fragile, gain de Kandel-Moles minimal, plafond LC."""

    kappa_fragile: float = Field(ge=-1, le=1, allow_inf_nan=False)
    gain_km_min: float = Field(allow_inf_nan=False)
    plafond_lc: float = Field(ge=0, le=100, allow_inf_nan=False)


class ConfigEvaluation(ModeleConfig):
    """Contenu de `config/evaluation.toml`."""

    schema_version: Literal[1]
    co: ConfigCO
    re: ConfigRE
    seuils: Seuils


def charger_evaluation(chemin: str | Path | None = None) -> ConfigEvaluation:
    """Lit `evaluation.toml` (défaut : `<racine du projet>/config/evaluation.toml`).

    Lève `ConfigurationInvalide` si le fichier est absent, illisible ou non conforme.
    """
    return charger_toml(
        chemin if chemin is not None else racine_projet() / "config" / NOM_EVALUATION,
        ConfigEvaluation,
    )
