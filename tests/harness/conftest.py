"""Fixtures du Harnais : doublures des ports, table des Tâches, configuration.

`factices.py` est chargé sous le nom `harness_factices` (les tests sont importés en mode
`importlib`, sans paquet) : `from harness_factices import FakeLlm`. Le marqueur
`integration` (avec `lent`) désigne le test réel sur Granite 1B, BGE-M3 et l'Index :
`SLMSP_VENDOR_DIR=<principal>/vendor SLMSP_MODELS_DIR=<principal>/models
uv run pytest tests/harness -m integration -s`.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

NOM_FACTICES = "harness_factices"


def _charger_factices() -> ModuleType:
    if NOM_FACTICES in sys.modules:
        return sys.modules[NOM_FACTICES]
    spec = importlib.util.spec_from_file_location(
        NOM_FACTICES, Path(__file__).resolve().parent / "factices.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[NOM_FACTICES] = module
    spec.loader.exec_module(module)
    return module


_charger_factices()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "integration: exécute les vrais binaires llama.cpp et modèles (avec `lent`)"
    )


@pytest.fixture(scope="session")
def table():
    from slmsp.harness.taches import charger_taches

    return charger_taches()


@pytest.fixture(scope="session")
def config_harnais():
    from slmsp.harness.config import charger_config_harnais

    return charger_config_harnais()


@pytest.fixture(autouse=True)
def _registre_vierge():
    """Le registre des traitements est mis en cache : chaque test repart d'un cache vide."""
    from slmsp.harness.taches import traitement

    traitement.cache_clear()
    yield
    traitement.cache_clear()
