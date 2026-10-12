"""Fixtures du registre de budget : TOML de test dans `tmp_path`, tarifs ronds.

Le modèle factice `m-test` coûte 1 $ par million de tokens en entrée comme en sortie
(direct) et 0,5 $ en batch ; le taux USD → EUR vaut 1. Une réservation de
`max_tokens = 1_000_000` sans entrée coûte donc exactement 1 € en direct.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget

MILLION = 1_000_000

TARIFS_TEST = """
schema_version = 1

[taux_usd_eur]
valeur = 1.0
date = 2026-10-12
source = "test"

[modeles."m-test"]
devise = "USD"
date = 2026-10-12
source = "test"

[modeles."m-test".modes.direct]
entree = 1.0
sortie = 1.0
ecriture_cache = 2.0
lecture_cache = 0.1

[modeles."m-test".modes.batch]
entree = 0.5
sortie = 0.5
ecriture_cache = 1.0
lecture_cache = 0.05

[modeles."m-sans-cache"]
devise = "USD"
date = 2026-10-12
source = "test"

[modeles."m-sans-cache".modes.direct]
entree = 1.0
sortie = 1.0
"""


def texte_budgets(
    *,
    campagne: str = "campagne-test",
    marge: float = 0.0,
    majoration: float = 1.0,
    anthropic: float = 10.0,
    mistral: float = 30.0,
    generation: float = 25.0,
    juge: float = 5.0,
) -> str:
    return f"""
schema_version = 1
campagne_id = "{campagne}"
marge_eur = {marge}
majoration_entree = {majoration}

[postes.anthropic]
plafond_eur = {anthropic}

[postes.mistral]
plafond_eur = {mistral}

[postes.mistral.sous_postes]
generation = {generation}
juge = {juge}

[imputations]
generation = "mistral.generation"
validation = "mistral.generation"
juge-second = "mistral.juge"
juge-principal = "anthropic"
"""


@dataclass
class FichiersConfig:
    budgets: Path
    tarifs: Path

    def ouvrir(self) -> RegistreBudget:
        return RegistreBudget(charger_budgets(self.budgets), charger_tarifs(self.tarifs))


@pytest.fixture
def config_test(tmp_path: Path) -> Callable[..., FichiersConfig]:
    """Fabrique : écrit `budgets.toml` (paramétrable) et `tarifs.toml` dans `tmp_path`."""
    compteur = iter(range(1_000))

    def ecrire(**parametres: float | str) -> FichiersConfig:
        dossier = tmp_path / f"config-{next(compteur)}"
        dossier.mkdir()
        budgets = dossier / "budgets.toml"
        tarifs = dossier / "tarifs.toml"
        budgets.write_text(texte_budgets(**parametres), encoding="utf-8")  # type: ignore[arg-type]
        tarifs.write_text(TARIFS_TEST, encoding="utf-8")
        return FichiersConfig(budgets, tarifs)

    return ecrire


@pytest.fixture
def registre(config_test: Callable[..., FichiersConfig]) -> RegistreBudget:
    """Registre par défaut : anthropic 10, mistral 30 (generation 25, juge 5), marge 0."""
    return config_test().ouvrir()


def _lignes(registre: RegistreBudget) -> list[dict[str, Any]]:
    with closing(sqlite3.connect(registre.chemin)) as connexion:
        connexion.row_factory = sqlite3.Row
        requete = "SELECT * FROM reservations ORDER BY id"
        return [dict(ligne) for ligne in connexion.execute(requete)]


def _modifier(registre: RegistreBudget, requete: str, parametres: tuple[Any, ...]) -> None:
    with closing(sqlite3.connect(registre.chemin)) as connexion, connexion:
        connexion.execute(requete, parametres)


@pytest.fixture
def lignes() -> Callable[[RegistreBudget], list[dict[str, Any]]]:
    """Lecteur de toutes les lignes du registre, par identifiant croissant."""
    return _lignes


@pytest.fixture
def modifier() -> Callable[[RegistreBudget, str, tuple[Any, ...]], None]:
    """Modification directe de la base (simulation d'un PID mort ou recyclé)."""
    return _modifier
