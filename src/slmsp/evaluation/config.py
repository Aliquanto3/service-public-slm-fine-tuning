"""Constantes du Jeu d'évaluation (SPEC §2, §5.4, §7) et chemins du gel.

Les cibles reprennent celles de `eval/outils/construire_jeu.py` (outil hors paquet, jamais
importé). Les parts sont des fractions exactes : `ceil(0,2 × 15)` vaut 3, pas 4.
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from pathlib import Path
from typing import Final

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
