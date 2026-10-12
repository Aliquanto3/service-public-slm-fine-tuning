"""Critères 8 et 9 de la story 1.1 : `.gitignore` conforme à AD-21 et `.env.example`."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]

IGNORES = [
    "index/",
    "var/",
    "vendor/",
    "models/",
    "data/raw/",
    "data/train/v1/train.jsonl",
    "runs/train/x/checkpoints/a",
    "runs/train/x/adaptateur/a",
    "a.gguf",
    "a.safetensors",
    ".env",
    "data/cache/x",
    "outputs/x",
    "wandb/x",
    "a.bin",
    "a.parquet",
    "index/v1/x",
    "a.pt",
    "a.ckpt",
]

VERSIONNES = [
    "runs/eval-notation/x/run.json",
    "runs/eval-notation/x/scores.json",
    "runs/eval-notation/x/verdicts.jsonl",
    "data/train/v1/MANIFEST.json",
    "data/registre-licences.toml",
    ".env.example",
    "src/slmsp/index/__init__.py",
    "runs/compare/x/rapport.md",
    "src/slmsp/data/__init__.py",
    "src/slmsp/train/__init__.py",
    "src/slmsp/budget/__init__.py",
]


def _ignore(chemin: str) -> bool:
    git = shutil.which("git")
    if git is None:
        pytest.skip("git introuvable")
    resultat = subprocess.run(
        [git, "check-ignore", "--no-index", "-q", chemin],
        cwd=RACINE,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultat.returncode in (0, 1), resultat.stderr
    return resultat.returncode == 0


@pytest.mark.parametrize("chemin", IGNORES)
def test_chemin_ignore(chemin: str) -> None:
    assert _ignore(chemin)


@pytest.mark.parametrize("chemin", VERSIONNES)
def test_chemin_versionne(chemin: str) -> None:
    assert not _ignore(chemin)


def test_anciennes_regles_en_bloc_retirees() -> None:
    regles = {
        ligne.strip()
        for ligne in (RACINE / ".gitignore").read_text(encoding="utf-8").splitlines()
        if ligne.strip() and not ligne.lstrip().startswith("#")
    }
    assert not regles & {"runs/", "/runs/", "checkpoints/", "/checkpoints/"}


def test_env_example() -> None:
    lignes = (RACINE / ".env.example").read_text(encoding="utf-8").splitlines()
    for cle in ("MISTRAL_API_KEY", "ANTHROPIC_API_KEY", "HF_TOKEN"):
        assert f"{cle}=" in lignes, cle
    assert any(ligne.startswith("#") and "SLMSP_VAR_DIR" in ligne for ligne in lignes)
    assert not any(ligne.startswith("SLMSP_VAR_DIR") for ligne in lignes)
