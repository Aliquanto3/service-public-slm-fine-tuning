"""Configuration du Harnais (`config/harnais.toml`, D-nuit-A3-2).

`ConfigHarnais` est figée. La story 4.2 la crée ; les stories 4.3 et 4.4 la lisent sans la
modifier. `recherche.k` et `recherche.seuil_pertinence` ne sont pas dans
`config/harnais.toml` : ils viennent de `config/index.toml` par `slmsp.index.config`, leur
source unique (story 2.3). Q demande toutefois son propre nombre de passages, `question.passages`
(story 16.2).
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from pydantic import ConfigDict, Field, PositiveInt

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.index.config import ConfigIndex, charger_config_index

NOM_CONFIG: Final = "harnais.toml"

VERSION_HARNAIS: Final = 2
"""Version du harnais d'évaluation (epic 16). 2 : Q à 8 passages et préfixe dédoublonné
(story 16.2) ; 16.3 et 16.8 ajoutent leurs sections sans réincrémenter. Un run de génération
sans version est lu comme version 1."""


class _Fige(ModeleConfig):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ConfigOutils(_Fige):
    """Boucle d'outils (story 4.3)."""

    iterations_max: int = Field(gt=0)
    delai_appel_s: float = Field(gt=0)


class ConfigModes(_Fige):
    """Sonde du Mode connecté (story 4.3)."""

    periode_sonde_s: float = Field(gt=0)
    delai_sonde_s: float = Field(gt=0)


class ConfigGeneration(_Fige):
    """Longueur de sortie par défaut des Tâches (correctif F2).

    Section facultative de `config/harnais.toml` : ses valeurs par défaut s'appliquent si
    elle est absente. `par_tache` fixe le plafond d'une Tâche (code) ; les Tâches de
    `reecriture` (CO, TR), qui réécrivent un texte d'entrée, reçoivent un plafond
    proportionnel au prompt mesuré (`harness.budget.plafond_reecriture`) : au moins
    `max_tokens`, `facteur_reecriture × prompt + marge_reecriture`, borné par le contexte.
    """

    max_tokens: int = Field(default=1024, gt=0)
    par_tache: dict[str, PositiveInt] = Field(default_factory=dict)
    reecriture: tuple[str, ...] = ("CO", "TR")
    facteur_reecriture: float = Field(default=1.5, gt=0)
    marge_reecriture: int = Field(default=256, ge=0)


class ConfigCompteRendu(_Fige):
    """Découpage des comptes rendus longs (story 4.4)."""

    reserve_sortie_tokens: int = Field(gt=0)
    chevauchement_paragraphes: int = Field(ge=0)


class ConfigVerification(_Fige):
    """Vérification en ligne d'une page officielle (FR-12, story 13.5).

    Section facultative de `config/harnais.toml` : ses valeurs par défaut s'appliquent si
    elle est absente.
    """

    active: bool = True
    delai_s: float = Field(default=10.0, gt=0)
    taille_max_octets: int = Field(default=2_000_000, gt=0)
    caracteres_max_page: int = Field(default=8000, gt=0)
    max_tokens: int = Field(default=400, gt=0)


class ConfigRecherche(_Fige):
    """Recherche dans l'Index local : copie de `config/index.toml` (source unique)."""

    k: int = Field(gt=0)
    seuil_pertinence: float = Field(ge=-1.0, le=1.0)


class ConfigDedoublonnage(_Fige):
    """Dédoublonnage du préfixe commun des passages d'une même page (story 16.2)."""

    prefixe_min_caracteres: int = Field(default=80, ge=1)


class ConfigQuestion(_Fige):
    """Question (story 16.2) : nombre de passages propre à Q, distinct de `recherche.k`."""

    passages: int = Field(default=8, gt=0)


class _FichierHarnais(_Fige):
    schema_version: Literal[1]
    outils: ConfigOutils
    modes: ConfigModes
    compte_rendu: ConfigCompteRendu
    verification: ConfigVerification = Field(default_factory=ConfigVerification)
    generation: ConfigGeneration = Field(default_factory=ConfigGeneration)
    dedoublonnage: ConfigDedoublonnage = Field(default_factory=ConfigDedoublonnage)
    question: ConfigQuestion = Field(default_factory=ConfigQuestion)


class ConfigHarnais(_Fige):
    """Configuration complète du Harnais."""

    outils: ConfigOutils
    modes: ConfigModes
    compte_rendu: ConfigCompteRendu
    recherche: ConfigRecherche
    verification: ConfigVerification = Field(default_factory=ConfigVerification)
    generation: ConfigGeneration = Field(default_factory=ConfigGeneration)
    dedoublonnage: ConfigDedoublonnage = Field(default_factory=ConfigDedoublonnage)
    question: ConfigQuestion = Field(default_factory=ConfigQuestion)


def chemin_config_harnais() -> Path:
    """`<racine du projet>/config/harnais.toml`."""
    return racine_projet() / "config" / NOM_CONFIG


def charger_config_harnais(
    chemin: str | Path | None = None, *, config_index: ConfigIndex | None = None
) -> ConfigHarnais:
    """Lit `config/harnais.toml` (ou `chemin`) et y joint `k` et le seuil de l'Index.

    `config_index` vaut `charger_config_index()` par défaut. Lève `ConfigurationInvalide`
    si un fichier est absent ou non conforme.
    """
    fichier = charger_toml(
        chemin if chemin is not None else chemin_config_harnais(), _FichierHarnais
    )
    index = config_index if config_index is not None else charger_config_index()
    return ConfigHarnais(
        outils=fichier.outils,
        modes=fichier.modes,
        compte_rendu=fichier.compte_rendu,
        verification=fichier.verification,
        generation=fichier.generation,
        dedoublonnage=fichier.dedoublonnage,
        question=fichier.question,
        recherche=ConfigRecherche(k=index.k, seuil_pertinence=index.seuil_pertinence),
    )


__all__ = [
    "VERSION_HARNAIS",
    "ConfigCompteRendu",
    "ConfigDedoublonnage",
    "ConfigGeneration",
    "ConfigHarnais",
    "ConfigModes",
    "ConfigOutils",
    "ConfigQuestion",
    "ConfigRecherche",
    "ConfigVerification",
    "chemin_config_harnais",
    "charger_config_harnais",
]
