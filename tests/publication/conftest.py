"""Racine factice du dossier de publication : runs et chiffres synthétiques, aucun réseau."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from slmsp.core.artefacts import nouveau_run

DEPOT = Path(__file__).resolve().parents[2]
SLUG = "granite-4.0-1b"


@pytest.fixture
def racine(tmp_path: Path) -> Path:
    r = tmp_path / "racine"
    (r / "config" / "modeles").mkdir(parents=True)
    (r / "config" / "licences").mkdir()
    (r / "data").mkdir()
    shutil.copy(DEPOT / "config" / "licences" / "apache-2.0.txt", r / "config" / "licences")
    shutil.copy(DEPOT / "config" / "modeles" / f"{SLUG}.toml", r / "config" / "modeles")
    shutil.copy(DEPOT / "data" / "registre-licences.toml", r / "data")
    config = (DEPOT / "config" / "publication.toml").read_text(encoding="utf-8")
    config = config.replace(
        f'[modeles."{SLUG}"]\n', f'[modeles."{SLUG}"]\nverifie_le = 2026-10-17\n'
    )
    (r / "config" / "publication.toml").write_text(config, encoding="utf-8")
    return r


@pytest.fixture
def export_id(racine: Path) -> str:
    run = nouveau_run("export", SLUG, {}, racine=racine, llamacpp_tag="b11429")
    contenu = {
        "fichiers": {"q4_k_m": "modele-q4_k_m.gguf", "f16": "modele-f16.gguf"},
        "controles": {"bloquants": [], "alertes": []},
    }
    (run.dossier / "export.json").write_text(json.dumps(contenu), encoding="utf-8")
    (run.dossier / "modele-q4_k_m.gguf").write_bytes(b"<gguf-factice>")
    run.terminer("complet")
    return run.run_id


@pytest.fixture
def comparatif(tmp_path: Path) -> Path:
    chemin = tmp_path / "comparatif.md"
    chemin.write_text("# Comparatif\n\nGain factice : <valeur-factice>.\n", encoding="utf-8")
    return chemin
