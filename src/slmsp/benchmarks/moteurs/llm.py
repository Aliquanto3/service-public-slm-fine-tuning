"""`LlmPort` d'un benchmark : le GGUF de la variante servi par `llama-server` (AD-16).

Les moteurs `traduction` et `bfcl` génèrent par le même adaptateur que le Harnais
(`ClientLlama`). `options.base_url` (serveur déjà lancé, sur 127.0.0.1) évite le démarrage ;
le verrou GPU reste celui de l'orchestrateur (`prendre_verrou_gpu=False`).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from slmsp.benchmarks.moteurs import ContexteBench
from slmsp.benchmarks.moteurs.lm_eval import HOTES_LOCAUX, resoudre_gguf
from slmsp.core.erreurs import ConfigurationInvalide

if TYPE_CHECKING:
    from slmsp.benchmarks.config import BenchmarkConfig
    from slmsp.core.ports import LlmPort


@contextmanager
def llm_gguf(config: BenchmarkConfig, contexte: ContexteBench) -> Iterator[LlmPort]:
    """Client du serveur du GGUF de la variante ; `ConfigurationInvalide` si non servable."""
    from slmsp.inference.client import ClientLlama
    from slmsp.inference.serveur import ServeurLlama

    url = config.options.get("base_url")
    if url:
        analyse = urlsplit(str(url))
        if analyse.hostname not in HOTES_LOCAUX or analyse.port is None:
            raise ConfigurationInvalide(f"options.base_url doit viser 127.0.0.1:<port> : {url}")
        client = ClientLlama(analyse.port)
        try:
            yield client
        finally:
            client.fermer()
        return
    slug, modele_config, gguf = resoudre_gguf(contexte)
    serveur = ServeurLlama(
        modele_config,
        contexte.variante_llamacpp,  # type: ignore[arg-type]
        slug=slug,
        gguf=gguf,
        prendre_verrou_gpu=False,
        parallele=contexte.parallele,
    )
    with serveur:
        yield serveur.client()


__all__ = ["llm_gguf"]
