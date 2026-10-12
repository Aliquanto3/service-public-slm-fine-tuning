"""Critère 3 de la story 1.1 : `pyproject.toml` (Python, socle, extras d'AD-2, torch CUDA)."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]

LOURDS = {
    "torch",
    "transformers",
    "trl",
    "peft",
    "bitsandbytes",
    "unsloth",
    "lm-eval",
    "bfcl-eval",
    "anthropic",
    "mistralai",
    "datasets",
    "duckdb",
    "pyarrow",
}
EXTRAS = {"fetch", "data", "judge", "bench", "train", "app"}


def _nom(exigence: str) -> str:
    """Nom normalisé (PEP 503) d'une exigence comme `torch==2.14.1`."""
    nom = re.match(r"[A-Za-z0-9._-]+", exigence.strip())
    assert nom is not None, exigence
    return re.sub(r"[-_.]+", "-", nom.group(0)).lower()


@pytest.fixture(scope="module")
def pyproject() -> dict:
    with (RACINE / "pyproject.toml").open("rb") as fichier:
        return tomllib.load(fichier)


def test_python_312(pyproject: dict) -> None:
    assert pyproject["project"]["requires-python"] == "==3.12.*"


def test_socle_sans_bibliotheque_lourde(pyproject: dict) -> None:
    noms = {_nom(d) for d in pyproject["project"]["dependencies"]}
    assert not noms & LOURDS


def test_extras_et_torch_dans_train_seulement(pyproject: dict) -> None:
    extras = pyproject["project"]["optional-dependencies"]
    assert EXTRAS <= set(extras)
    avec_torch = {nom for nom, deps in extras.items() if "torch" in {_nom(d) for d in deps}}
    assert avec_torch == {"train"}


def test_torch_depuis_index_cuda_explicite(pyproject: dict) -> None:
    uv = pyproject["tool"]["uv"]
    nom_index = uv["sources"]["torch"]["index"]
    index = {i["name"]: i for i in uv["index"]}[nom_index]
    assert index["explicit"] is True
    assert "download.pytorch.org/whl/cu130" in index["url"]
