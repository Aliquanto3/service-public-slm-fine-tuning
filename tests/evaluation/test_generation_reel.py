"""Test réel de la phase génération : Granite 1B Q4_K_M (CPU), BGE-M3 et l'Index (story 5.3).

Marqué `lent` et `integration`, exclu par défaut. Lancer :
`SLMSP_VENDOR_DIR=<principal>/vendor SLMSP_MODELS_DIR=<principal>/models
uv run pytest tests/evaluation -m integration -s`.

Le jeu v1.0 est copié dans `tmp_path` (le run y est écrit). Racine de l'Index :
`SLMSP_INDEX_RACINE`, sinon la racine du projet si elle porte un Index, sinon le dépôt
principal (cas d'un worktree). Le test est sauté si un binaire, un modèle ou l'Index manque.
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from evaluation_factices import ITEMS_8, SLUG

from slmsp.core.config import dossier_modeles, racine_projet
from slmsp.core.schemas.generation import Generation
from slmsp.evaluation.assemblage import ouvrir_harnais
from slmsp.evaluation.generation import FICHIER_GENERATIONS, lancer_generation
from slmsp.index.lecture import versions_disponibles
from slmsp.inference import serveur

GGUF_BGE = "bge-m3/gguf/bge-m3-q8_0.gguf"


def _depot_principal() -> Path | None:
    git = shutil.which("git")
    if git is None:
        return None
    try:
        sortie = subprocess.run(
            [git, "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=racine_projet(),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return Path(sortie).parent if sortie else None


def racine_index() -> Path | None:
    """Racine qui porte `index/<version>/`, ou `None`."""
    valeur = os.environ.get("SLMSP_INDEX_RACINE", "").strip()
    candidates = [Path(valeur)] if valeur else [racine_projet(), _depot_principal()]
    for racine in candidates:
        if racine is not None and versions_disponibles(racine):
            return racine
    return None


def prerequis() -> Path:
    dossier = serveur.dossier_llamacpp()
    if not (dossier / "bin-cpu" / "llama-server.exe").is_file():
        pytest.skip(f"llama.cpp absent sous {dossier} (définir SLMSP_VENDOR_DIR)")
    fichier = serveur.charger_config_modele(SLUG).gguf.fichier
    for relatif in (f"{SLUG}/gguf/{fichier}", GGUF_BGE):
        if not (dossier_modeles() / relatif).is_file():
            pytest.skip(f"modèle absent : {dossier_modeles() / relatif} (SLMSP_MODELS_DIR)")
    racine = racine_index()
    if racine is None:
        pytest.skip("Index local absent (définir SLMSP_INDEX_RACINE)")
    return racine


@pytest.mark.lent
@pytest.mark.integration
def test_reel_generation_huit_items(depot_eval: Path) -> None:
    index = prerequis()
    rapport = lancer_generation(
        f"base:{SLUG}",
        "q4_k_m",
        "v1.0",
        variante="cpu",
        items=ITEMS_8,
        racine=depot_eval,
        fabrique=functools.partial(ouvrir_harnais, racine_index=index),
        rapporter=lambda g, rang, total: print(f"[{rang}/{total}] {g.item_id} {g.statut}"),
    )

    run = rapport.run
    brut = json.loads((run.dossier / "run.json").read_text(encoding="utf-8"))
    print(f"\nrun : {run.dossier} ; statut {rapport.statut} ; durées {rapport.durees_ms}")
    assert brut["modele_ref"] == f"base:{SLUG}" and brut["quantification"] == "q4_k_m"
    assert brut["variante_llamacpp"] == "cpu" and brut["jeu_version"] == "v1.0"
    assert brut["index_version"] and len(brut["chat_template_sha256"]) == 64
    assert brut["config"]["serveur"]["generation"]["arguments"]
    generations = [Generation.model_validate(g) for g in run.lire_jsonl(FICHIER_GENERATIONS)]
    assert sorted(g.item_id for g in generations) == sorted(ITEMS_8)
    assert rapport.connexions_bloquees == []
    for generation in generations:
        print(f"{generation.item_id} {generation.statut} : {generation.sortie_canonique.texte!r}")
    assert all(g.statut == "ok" for g in generations), rapport.statut
    assert rapport.statut == "complet"
