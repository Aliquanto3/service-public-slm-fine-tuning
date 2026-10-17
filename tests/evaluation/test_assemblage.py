"""Assemblage réel du Harnais d'évaluation (story 5.3) : serveurs, Index et `/props` simulés.

`ouvrir_harnais` est exécuté tel quel ; seuls `ServeurLlama`, `ouvrir_index` et `lire_props`
sont remplacés, sans binaire llama.cpp ni modèle. Le test réel (`lent`) reste dans
`test_generation_reel.py`.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.evaluation import assemblage
from slmsp.inference.processus import ErreurInference
from slmsp.inference.serveur import charger_config_llamacpp

TEMPLATE = "<template-factice>{{ messages }}"


class ServeurFactice:
    """`ServeurLlama` factice : enregistre ses arguments et son arrêt."""

    def __init__(self, config: Any, variante: str, *, port: int, **options: Any) -> None:
        self.config = config
        self.variante = variante
        self.port = port
        self.options = options
        self.arrete = False

    def __enter__(self) -> ServeurFactice:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.arrete = True

    def client(self) -> tuple[str, ServeurFactice]:
        return ("client", self)

    def embedder(self) -> tuple[str, ServeurFactice]:
        return ("embedder", self)

    def description(self) -> dict[str, Any]:
        return {"slug": self.options["slug"], "variante": self.variante}


@pytest.fixture
def serveurs(monkeypatch: pytest.MonkeyPatch) -> list[ServeurFactice]:
    crees: list[ServeurFactice] = []

    def fabriquer(config: Any, variante: str, **options: Any) -> ServeurFactice:
        serveur = ServeurFactice(config, variante, port=18000 + len(crees), **options)
        crees.append(serveur)
        return serveur

    @contextmanager
    def index(racine: Path) -> Iterator[Any]:
        yield SimpleNamespace(version="<index-factice>", racine=racine)

    monkeypatch.setattr(assemblage, "ServeurLlama", fabriquer)
    monkeypatch.setattr(assemblage, "ouvrir_index", index)
    return crees


CONFIG_MODELE = SimpleNamespace(llamacpp=None)


def modele(tmp_path: Path, config: Any = CONFIG_MODELE) -> Any:
    return SimpleNamespace(config=config, slug="granite-4.0-1b", gguf=tmp_path / "modele.gguf")


def test_ouvrir_harnais_empreintes_et_serveurs(
    serveurs: list[ServeurFactice], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    ports: list[int] = []

    def props(port: int) -> dict[str, Any]:
        ports.append(port)
        return {"chat_template": TEMPLATE}

    monkeypatch.setattr(assemblage, "lire_props", props)
    resolu = modele(tmp_path)
    with assemblage.ouvrir_harnais(resolu, "cuda", tmp_path) as harnais:
        generation, embedding = serveurs
        assert harnais.chat_template_sha256 == assemblage.sha256_texte(TEMPLATE)
        assert ports == [generation.port]  # template du serveur de génération
        assert harnais.index_version == "<index-factice>"
        assert harnais.vector_store.racine == tmp_path.resolve()
        assert harnais.llamacpp_tag == charger_config_llamacpp().tag
        assert harnais.llm == ("client", generation)
        assert harnais.embedder == ("embedder", embedding)

        assert generation.config is CONFIG_MODELE and generation.variante == "cuda"
        assert generation.options["slug"] == "granite-4.0-1b"
        assert generation.options["gguf"] == resolu.gguf
        assert embedding.variante == "cpu"  # embedding toujours sur CPU
        assert embedding.options["slug"] == assemblage.SLUG_EMBEDDING
        assert all(s.options["prendre_verrou_gpu"] is False for s in serveurs)
        assert not any(s.arrete for s in serveurs)
    assert all(s.arrete for s in serveurs)


def test_ouvrir_harnais_version_llamacpp_reservee(
    serveurs: list[ServeurFactice], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Un modèle à version réservée (Bonsai) : génération et `llamacpp_tag` sur cette version,
    embedding sur la version commune."""
    monkeypatch.setattr(assemblage, "lire_props", lambda port: {"chat_template": TEMPLATE})
    config = SimpleNamespace(llamacpp="prism-b10777-e3de715")
    with assemblage.ouvrir_harnais(modele(tmp_path, config), "cpu", tmp_path) as harnais:
        generation, embedding = serveurs
        assert harnais.llamacpp_tag == "prism-b10777-e3de715"
        assert generation.options["config_llamacpp"].tag == "prism-b10777-e3de715"
        assert embedding.options["config_llamacpp"].tag == charger_config_llamacpp().tag


def test_ouvrir_harnais_racine_index(
    serveurs: list[ServeurFactice], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(assemblage, "lire_props", lambda port: {"chat_template": TEMPLATE})
    autre = tmp_path / "index"
    with assemblage.ouvrir_harnais(modele(tmp_path), "cpu", tmp_path, racine_index=autre) as h:
        assert h.vector_store.racine == autre


@pytest.mark.parametrize("props", [{}, {"chat_template": ""}, {"chat_template": 3}])
def test_ouvrir_harnais_sans_chat_template(
    props: dict[str, Any],
    serveurs: list[ServeurFactice],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(assemblage, "lire_props", lambda port: props)
    with (
        pytest.raises(ErreurInference, match="chat_template absent"),
        assemblage.ouvrir_harnais(modele(tmp_path), "cpu", tmp_path),
    ):
        pass
    assert len(serveurs) == 2 and all(s.arrete for s in serveurs)
