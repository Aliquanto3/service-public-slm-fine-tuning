"""Fixtures de `tests/app` : doublures du Harnais (`tests/harness/factices.py`) par chemin."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

NOM = "harness_factices"


def charger_factices() -> ModuleType:
    if NOM in sys.modules:
        return sys.modules[NOM]
    chemin = Path(__file__).parents[1] / "harness" / "factices.py"
    spec = importlib.util.spec_from_file_location(NOM, chemin)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[NOM] = module
    spec.loader.exec_module(module)
    return module


charger_factices()
