"""Test réel de la Question : Granite 1B (CPU), BGE-M3 (CPU) et l'Index local (story 4.2).

Marqué `lent` et `integration`, exclu par défaut. Lancer :
`SLMSP_VENDOR_DIR=<principal>/vendor SLMSP_MODELS_DIR=<principal>/models
uv run pytest tests/harness -m integration -s`.

Racine de l'Index : `SLMSP_INDEX_RACINE`, sinon la racine du projet si elle porte un
Index, sinon le dépôt principal (`git rev-parse --git-common-dir`, cas d'un worktree).
Le test est sauté si un binaire, un modèle ou l'Index manque.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from slmsp.core.config import dossier_modeles, racine_projet
from slmsp.core.evenements import Avertissement, Fin, Jeton, Sources
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.harness.config import charger_config_harnais
from slmsp.harness.service import AssistantService
from slmsp.index.lecture import ouvrir_index, versions_disponibles
from slmsp.inference import serveur
from slmsp.inference.serveur import ServeurLlama

GRANITE = "granite-4.0-1b"
QWEN = "qwen-4b"
GGUF = {
    GRANITE: ("ibm-granite/granite-4.0-1b", "granite-4.0-1b-Q4_K_M.gguf"),
    QWEN: ("Qwen/Qwen3-4B-Instruct-2507", "Qwen3-4B-Instruct-2507-Q4_K_M.gguf"),
}
BGE_GGUF = "bge-m3/gguf/bge-m3-q8_0.gguf"
QUESTION = "Comment renouveler sa carte nationale d'identité ?"


def config_generation(slug: str) -> ConfigModele:
    depot, fichier = GGUF[slug]
    return ConfigModele.model_validate(
        {
            "depot_hf": depot,
            "revision": "0" * 40,
            "fichiers": [],
            "gguf": {"depot": "local", "fichier": fichier, "sha256": "0" * 64},
            "contexte": 4096,
            "protocole_outils": "natif",
        }
    )


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


def prerequis(slug: str) -> Path:
    dossier = serveur.dossier_llamacpp()
    if not (dossier / "bin-cpu" / "llama-server.exe").is_file():
        pytest.skip(f"llama.cpp absent sous {dossier} (définir SLMSP_VENDOR_DIR)")
    for relatif in (f"{slug}/gguf/{GGUF[slug][1]}", BGE_GGUF):
        if not (dossier_modeles() / relatif).is_file():
            pytest.skip(f"modèle absent : {dossier_modeles() / relatif} (SLMSP_MODELS_DIR)")
    racine = racine_index()
    if racine is None:
        pytest.skip("Index local absent (définir SLMSP_INDEX_RACINE)")
    return racine


@pytest.mark.lent
@pytest.mark.integration
@pytest.mark.parametrize("slug", [GRANITE, QWEN])
def test_reel_question_fondee(slug: str) -> None:
    """Granite 1B (cible de la story) et Qwen3 4B (témoin qui suit la consigne de citation)."""
    racine = prerequis(slug)
    config = charger_config_harnais()
    with (
        ServeurLlama(config_generation(slug), "cpu", slug=slug) as generation,
        ServeurLlama(serveur.charger_config_modele("bge-m3"), "cpu", slug="bge-m3") as embedding,
        ouvrir_index(racine) as index,
    ):
        service = AssistantService(
            generation.client(), embedding.embedder(), index, None, None, config
        )
        passages = service.recherche.rechercher(QUESTION)
        options: dict[str, Any] = {"temperature": 0, "seed": 42, "max_tokens": 300}
        evenements = list(
            service.repondre("Q", [{"role": "user", "content": QUESTION}], options=options)
        )

    fin = evenements[-1]
    assert isinstance(fin, Fin), f"le flux se termine par {fin!r}"
    texte = "".join(e.texte for e in evenements if isinstance(e, Jeton))
    (sources,) = [e for e in evenements if isinstance(e, Sources)]
    (alerte,) = [e for e in evenements if isinstance(e, Avertissement)]
    print(f"\nPassages pertinents : {len(passages)} (seuil {config.recherche.seuil_pertinence})")
    for numero, p in enumerate(passages, start=1):
        print(f"  passage [{numero}] {p.score:.3f} {p.titre} — {p.url} ({p.date_snapshot})")
    print(f"Réponse : {texte}")
    for source in sources.sources:
        print(f"Source [{source.numero}] {source.titre} — {source.url} ({source.date})")
    print(f"{alerte.message} | usage : {fin.usage} | URL inventées : {fin.urls_inventees}")

    types = [type(e) for e in evenements]
    assert types[-3:] == [Sources, Avertissement, Fin]
    assert texte.strip()
    assert isinstance(fin, Fin) and fin.raison in ("terminee", "longueur")
    assert fin.usage is not None and "delai_premier_token_ms" in fin.usage
    assert alerte.code == "avis-juridique" and alerte.message == "Ne vaut pas avis juridique."
    assert passages, "aucun passage pertinent pour la question de test"
    assert all(p.url.startswith("https://") and p.date_snapshot for p in passages)
    urls_index = {p.url for p in passages}
    assert all(s.url in urls_index and s.origine == "index" for s in sources.sources)
    assert all(s.date for s in sources.sources)
    numeros = [s.numero for s in sources.sources]
    assert all(n is not None for n in numeros) and len(set(numeros)) == len(numeros)
    if slug == GRANITE and not sources.sources:
        # `Sources` ne liste que les passages cités par `[n]` (Design Notes de la story 4.2) :
        # Granite 1B de base ne cite pas (constaté sur plusieurs questions). Le Harnais n'y
        # peut rien sans réécrire le texte ; c'est l'objet de l'affinage. Le témoin Qwen3 4B
        # montre la chaîne complète avec des citations réelles.
        pytest.xfail("Granite 1B de base ne cite aucun passage [n] : Sources vide")
    assert sources.sources, f"{slug} : aucune citation [n] dans la réponse"
