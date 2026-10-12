"""Reprend la fabrique d'Index factice de `tests/index/conftest.py`."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

CHEMIN = Path(__file__).resolve().parents[1] / "index" / "conftest.py"


def _charger() -> ModuleType:
    nom = "slmsp_tests_index_fabrique"
    if nom in sys.modules:
        return sys.modules[nom]
    spec = importlib.util.spec_from_file_location(nom, CHEMIN)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


fabrique = _charger()
fabrique_index = fabrique.fabrique_index
