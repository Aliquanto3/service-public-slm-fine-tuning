"""`EmbedderLlama` (EmbedderPort) contre le serveur factice."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from slmsp.core.ports import EmbedderPort
from slmsp.inference.embedding import EmbedderLlama
from slmsp.inference.processus import ErreurInference


@pytest.fixture
def embedder(serveur_factice: Any) -> Any:
    with EmbedderLlama(serveur_factice.port, taille_lot=2) as instance:
        yield instance


def test_est_un_embedderport(embedder: EmbedderLlama) -> None:
    assert isinstance(embedder, EmbedderPort)
    assert embedder.dimension == 1024


def test_vectoriser(embedder: EmbedderLlama, serveur_factice: Any, factice) -> None:
    textes = ["a", "b", "c"]
    matrice = embedder.vectoriser(textes)
    assert matrice.shape == (3, 1024) and matrice.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(matrice, axis=1), 1.0, rtol=1e-6)
    # Le serveur renvoie les vecteurs dans l'ordre inverse : remis par `index`.
    for ligne, texte in zip(matrice, textes, strict=True):
        attendu = np.asarray(factice.vecteur(texte), dtype=np.float32)
        np.testing.assert_allclose(ligne, attendu / np.linalg.norm(attendu), rtol=1e-6)
    assert [corps["input"] for corps in serveur_factice.corps("/v1/embeddings")] == [
        ["a", "b"],
        ["c"],
    ]


def test_liste_vide(embedder: EmbedderLlama, serveur_factice: Any) -> None:
    assert embedder.vectoriser([]).shape == (0, 1024)
    assert serveur_factice.requetes == []


def test_chaine_seule_refusee(embedder: EmbedderLlama) -> None:
    with pytest.raises(TypeError):
        embedder.vectoriser("abc")


def test_dimension_inattendue(embedder: EmbedderLlama, serveur_factice: Any) -> None:
    serveur_factice.scenario.embeddings = lambda textes: [
        {"index": i, "embedding": [1.0] * 768} for i in range(len(textes))
    ]
    with pytest.raises(ErreurInference, match="dimension"):
        embedder.vectoriser(["a"])


def test_vecteur_nul(embedder: EmbedderLlama, serveur_factice: Any) -> None:
    serveur_factice.scenario.embeddings = lambda textes: [
        {"index": i, "embedding": [0.0] * 1024} for i in range(len(textes))
    ]
    with pytest.raises(ErreurInference, match="nul"):
        embedder.vectoriser(["a"])


def test_nombre_de_vecteurs_inattendu(embedder: EmbedderLlama, serveur_factice: Any) -> None:
    serveur_factice.scenario.embeddings = lambda textes: []
    with pytest.raises(ErreurInference):
        embedder.vectoriser(["a"])


def test_texte_trop_long_tronque(serveur_factice: Any) -> None:
    """Un texte au-delà du contexte est tronqué avant l'envoi (sinon HTTP 500 du serveur)."""
    serveur_factice.scenario.tokens = lambda texte: list(range(len(texte)))
    with EmbedderLlama(serveur_factice.port, contexte_max=100) as instance:
        instance.vectoriser(["x" * 1000, "court"])
    envoyes = serveur_factice.corps("/v1/embeddings")[0]["input"]
    assert len(envoyes[0]) <= 100 - 16
    assert envoyes[1] == "court"


def test_texte_tronque_compte_et_journalise(
    serveur_factice: Any, caplog: pytest.LogCaptureFixture
) -> None:
    serveur_factice.scenario.tokens = lambda texte: list(range(len(texte)))
    with EmbedderLlama(serveur_factice.port, contexte_max=100) as instance:
        with caplog.at_level("WARNING", logger="slmsp.inference.embedding"):
            instance.vectoriser(["x" * 1000, "court"])
        assert instance.textes_tronques == 1
    assert "tronqué" in caplog.text


def test_texte_court_sans_appel_tokenize(serveur_factice: Any) -> None:
    with EmbedderLlama(serveur_factice.port, contexte_max=100) as instance:
        instance.vectoriser(["court", "y" * 84])
        assert instance.textes_tronques == 0
    assert serveur_factice.corps("/tokenize") == []


def test_tokenize_en_erreur(serveur_factice: Any) -> None:
    serveur_factice.scenario.statut_tokenize = 500
    with EmbedderLlama(serveur_factice.port, contexte_max=100) as instance:
        with pytest.raises(ErreurInference):
            instance.vectoriser(["x" * 1000])


def test_tokenize_reponse_illisible(serveur_factice: Any) -> None:
    serveur_factice.scenario.tokens = lambda texte: None
    with EmbedderLlama(serveur_factice.port, contexte_max=100) as instance:
        with pytest.raises(ErreurInference):
            instance.vectoriser(["x" * 1000])
