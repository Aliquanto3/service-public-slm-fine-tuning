"""Fixtures de l'inférence : serveur factice, `vendor/` factice, binaires et modèles réels.

Les tests réels sont marqués `lent` et `integration` ; ils lisent `SLMSP_VENDOR_DIR` et
`SLMSP_MODELS_DIR` (dépôt principal) et sont sautés si les fichiers manquent :
`SLMSP_VENDOR_DIR=<principal>/vendor SLMSP_MODELS_DIR=<principal>/models
uv run pytest tests/inference -m integration -s`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import pytest

from slmsp.core.config import dossier_modeles
from slmsp.core.schemas.config_llamacpp import ConfigLlamacpp
from slmsp.inference import serveur

ICI = Path(__file__).resolve().parent
CHEMIN_FACTICE = ICI / "serveur_factice.py"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "integration: exécute les vrais binaires llama.cpp et modèles (avec `lent`)"
    )


def _charger_factice() -> ModuleType:
    nom = "slmsp_tests_serveur_factice"
    if nom in sys.modules:
        return sys.modules[nom]
    spec = importlib.util.spec_from_file_location(nom, CHEMIN_FACTICE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def factice() -> ModuleType:
    """Module `serveur_factice` (classes `ServeurFactice`, `Scenario`, aides SSE)."""
    return _charger_factice()


@pytest.fixture
def serveur_factice(factice: ModuleType) -> Iterator[object]:
    """Serveur factice démarré sur un port libre de `127.0.0.1`."""
    with factice.ServeurFactice() as instance:
        yield instance


@pytest.fixture(autouse=True)
def _empreintes_oubliees(monkeypatch: pytest.MonkeyPatch) -> None:
    """Chaque test revérifie les SHA-256 des binaires (cache par processus)."""
    monkeypatch.setattr(serveur, "_empreintes_verifiees", set())


@dataclass
class VendorFactice:
    racine: Path
    config: ConfigLlamacpp

    @property
    def tag(self) -> Path:
        return self.racine / "llama.cpp" / self.config.tag


FICHIERS_FACTICES = {
    "bin-cpu/llama-server.exe": b"serveur cpu factice",
    "bin-cuda/llama-server.exe": b"serveur cuda factice",
    "bin-cuda/ggml-cuda.dll": b"dll cuda factice",
    "bin-cpu/llama-quantize.exe": b"quantize factice",
    "src/convert_hf_to_gguf.py": b"# conversion factice\n",
    "src/gguf-py/gguf/__init__.py": b"",
}


@pytest.fixture
def vendor_factice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> VendorFactice:
    """`SLMSP_VENDOR_DIR` factice : binaires de quelques octets, empreintes cohérentes."""
    reelle = serveur.charger_config_llamacpp()
    racine = tmp_path / "vendor"
    base = racine / "llama.cpp" / reelle.tag
    binaires = {}
    for relatif, contenu in FICHIERS_FACTICES.items():
        chemin = base / relatif
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_bytes(contenu)
        if not relatif.startswith("src/gguf-py"):
            binaires[relatif] = hashlib.sha256(contenu).hexdigest()
    monkeypatch.setenv("SLMSP_VENDOR_DIR", str(racine))
    return VendorFactice(racine, reelle.model_copy(update={"binaires": binaires}))


# --- Fichiers réels ----------------------------------------------------------------------------


@pytest.fixture
def vendor_reel() -> Path:
    """`<vendor>/llama.cpp/<tag>/` réel ; saute le test s'il est incomplet."""
    dossier = serveur.dossier_llamacpp()
    for variante in ("cpu", "cuda"):
        if not (dossier / f"bin-{variante}" / "llama-server.exe").is_file():
            pytest.skip(f"llama.cpp absent sous {dossier} (définir SLMSP_VENDOR_DIR)")
    return dossier


GRANITE_GGUF = "granite-4.0-1b/gguf/granite-4.0-1b-Q4_K_M.gguf"
BGE_GGUF = "bge-m3/gguf/bge-m3-q8_0.gguf"


@pytest.fixture
def modeles_reels() -> Path:
    """`dossier_modeles()` réel avec Granite 1B et BGE-M3 ; saute le test sinon."""
    dossier = dossier_modeles()
    for relatif in (GRANITE_GGUF, BGE_GGUF):
        if not (dossier / relatif).is_file():
            pytest.skip(f"modèle absent : {dossier / relatif} (définir SLMSP_MODELS_DIR)")
    return dossier
