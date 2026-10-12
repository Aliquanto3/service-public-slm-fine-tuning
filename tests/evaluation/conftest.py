"""Fixtures de la phase génération du banc (story 5.3).

`tests/harness/factices.py` est chargé sous le nom `harness_factices`, comme dans
`tests/harness/conftest.py`. Règle D1.1 : `FakeLlmDeterministe` produit des mots
aléatoires (`mots`), jamais un texte rédigé. Le Jeu d'évaluation (v1.0 gelé, cassettes,
grille, calibrage) est copié dans `tmp_path` : les originaux ne sont jamais modifiés.
Le marqueur `integration` (avec `lent`) désigne le test réel sur Granite 1B.
"""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

NOM_FACTICES = "harness_factices"
RACINE = Path(__file__).resolve().parents[2]
SLUG = "granite-4.0-1b"
SHA_TEMPLATE = "ab" * 32
ITEMS_8 = ("Q-001", "RD-001", "CR-001", "LC-001", "CO-001", "RE-001", "CT-001", "NR-001")
"""Un item par Tâche du jeu v1.0."""


def _charger_factices() -> ModuleType:
    if NOM_FACTICES in sys.modules:
        return sys.modules[NOM_FACTICES]
    spec = importlib.util.spec_from_file_location(
        NOM_FACTICES, RACINE / "tests" / "harness" / "factices.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[NOM_FACTICES] = module
    spec.loader.exec_module(module)
    return module


factices = _charger_factices()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "integration: exécute les vrais binaires llama.cpp et modèles (avec `lent`)"
    )


def _empreinte(messages: Sequence[Mapping[str, Any]]) -> str:
    h = hashlib.sha256()
    for message in messages:
        h.update(str(message.get("role")).encode("utf-8") + b"\x00")
        h.update(str(message.get("content")).encode("utf-8") + b"\x01")
    return h.hexdigest()


class FakeLlmDeterministe:
    """`LlmPort` déterministe : mots aléatoires semés par le SHA des `(role, content)`.

    Avec `tools` et sans message `tool` dans la conversation (premier tour de la Recherche
    de données), émet un `AppelOutil` `search_datasets` à requête aléatoire. `lever(messages)`
    peut rendre une exception, levée au milieu du flux. Enregistre chaque appel.
    """

    def __init__(
        self, lever: Callable[[Sequence[Mapping[str, Any]]], BaseException | None] | None = None
    ) -> None:
        self.lever = lever
        self.appels: list[dict[str, Any]] = []

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Any]:
        from slmsp.core.evenements import AppelOutil, Fin, Jeton

        self.appels.append(
            {
                "messages": [dict(m) for m in messages],
                "tools": tools,
                "options": dict(options) if options is not None else None,
            }
        )
        graine = _empreinte(messages)
        erreur = self.lever(messages) if self.lever is not None else None

        def flux() -> Iterator[Any]:
            texte = factices.mots(12, graine)
            yield Jeton(texte=texte[:10])
            if erreur is not None:
                raise erreur
            yield Jeton(texte=texte[10:])
            if tools and not any(m.get("role") == "tool" for m in messages):
                yield AppelOutil(
                    id=f"appel-{graine[:12]}",
                    nom="search_datasets",
                    arguments={"query": factices.mots(2, f"requete-{graine}")},
                )
            yield Fin(raison="terminee", usage=dict(factices.USAGE))

        return flux()

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        return sum(len(str(m.get("content") or "").split()) for m in messages)


def passages_factices() -> list[Any]:
    """Passages factices : trois de service-public, deux du catalogue data.gouv."""
    import dataclasses

    passages = [factices.passage(n, 0.9 - n / 100) for n in range(1, 4)]
    passages += [
        dataclasses.replace(factices.passage(n, 0.8 - n / 100), source="data-gouv-datasets-catalog")
        for n in range(4, 6)
    ]
    return passages


def harnais_factice(llm: Any | None = None) -> Any:
    from slmsp.evaluation.assemblage import HarnaisEvaluation
    from slmsp.harness.config import charger_config_harnais
    from slmsp.harness.taches import charger_taches

    return HarnaisEvaluation(
        llm=llm if llm is not None else FakeLlmDeterministe(),
        embedder=factices.FakeEmbedder(),
        vector_store=factices.FakeVectorStore(passages_factices()),
        config=charger_config_harnais(),
        taches=charger_taches(),
        description={"generation": {"factice": True}, "embedding": {"factice": True}},
        chat_template_sha256=SHA_TEMPLATE,
        index_version="factice",
        llamacpp_tag="b11429",
    )


class Fabrique:
    """Fabrique de Harnais factice ; enregistre ses appels `(modele, variante, racine)`."""

    def __init__(self, llm: Any | None = None, sha_template: str = SHA_TEMPLATE) -> None:
        self.llm = llm
        self.sha_template = sha_template
        self.appels: list[tuple[Any, str, Path]] = []

    @contextmanager
    def __call__(self, modele: Any, variante: str, racine: Path) -> Iterator[Any]:
        self.appels.append((modele, variante, racine))
        harnais = harnais_factice(self.llm)
        harnais.chat_template_sha256 = self.sha_template
        yield harnais


@pytest.fixture
def fabrique() -> Fabrique:
    return Fabrique()


@pytest.fixture
def depot_eval(tmp_path: Path) -> Path:
    """Racine temporaire avec une copie de `eval/` (jeu v1.0, cassettes, grille, calibrage)."""
    racine = tmp_path / "depot"
    source = RACINE / "eval"
    cible = racine / "eval"
    shutil.copytree(source / "jeu" / "v1.0", cible / "jeu" / "v1.0")
    shutil.copytree(source / "cassettes", cible / "cassettes")
    shutil.copytree(source / "calibrage", cible / "calibrage")
    shutil.copyfile(source / "grille-juge-v1.md", cible / "grille-juge-v1.md")
    return racine


@pytest.fixture
def modeles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """`SLMSP_MODELS_DIR` temporaire avec un GGUF factice de Granite 1B."""
    from slmsp.inference.serveur import charger_config_modele

    dossier = tmp_path / "modeles"
    gguf = dossier / SLUG / "gguf" / charger_config_modele(SLUG).gguf.fichier
    gguf.parent.mkdir(parents=True)
    gguf.write_bytes(b"GGUF-factice")
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(dossier))
    return dossier


# Les tests importent ces doublures par `from evaluation_factices import ...` (mode importlib).
sys.modules.setdefault("evaluation_factices", sys.modules[__name__])
