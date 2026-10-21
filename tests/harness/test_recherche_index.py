"""`harness.recherche_index` : top-k et seuil de pertinence (story 4.2, AD-9)."""

from __future__ import annotations

import pytest
from harness_factices import FakeEmbedder, FakeVectorStore, mots, passage

from slmsp.harness.recherche_index import RechercheIndex, RequeteVide, depuis_config
from slmsp.index.config import charger_config_index


def test_seuil_inclusif_et_k() -> None:
    passages = [passage(1, 0.9), passage(2, 0.5), passage(3, 0.49), passage(4, 0.95)]
    embedder, store = FakeEmbedder(), FakeVectorStore(passages)
    recherche = RechercheIndex(embedder, store, 3, 0.5)
    requete = mots(5, "requete")
    trouves = recherche.rechercher(requete)
    assert [p.chunk_id for p in trouves] == ["c4", "c1", "c2"]
    assert embedder.textes == [requete]
    assert store.appels == [3]
    assert RechercheIndex(embedder, store, 2, 0.5).rechercher(requete) == trouves[:2]


def test_k_de_l_appel_remplace_celui_de_l_instance() -> None:
    # Q demande son propre k (story 16.2) sans changer celui de l'instance.
    store = FakeVectorStore([passage(i, 0.9) for i in range(1, 10)])
    recherche = RechercheIndex(FakeEmbedder(), store, 5, 0.5)
    assert len(recherche.rechercher("requete", k=8)) == 8
    assert len(recherche.rechercher("requete")) == 5
    assert store.appels == [8, 5]
    for invalide in (0, True, 2.0):
        with pytest.raises(ValueError, match="k doit"):
            recherche.rechercher("requete", k=invalide)


def test_requete_vide() -> None:
    with pytest.raises(RequeteVide):
        RechercheIndex(FakeEmbedder(), FakeVectorStore(), 3, 0.5).rechercher("  ")


@pytest.mark.parametrize(("k", "seuil"), [(0, 0.5), (True, 0.5), (2.0, 0.5), (3, float("nan"))])
def test_parametres_invalides(k, seuil) -> None:
    with pytest.raises(ValueError):
        RechercheIndex(FakeEmbedder(), FakeVectorStore(), k, seuil)


def test_depuis_config() -> None:
    config = charger_config_index()
    recherche = depuis_config(FakeEmbedder(), FakeVectorStore())
    assert (recherche.k, recherche.seuil) == (config.k, config.seuil_pertinence)
    autre = config.model_copy(update={"k": 2, "seuil_pertinence": 0.1})
    recherche = depuis_config(FakeEmbedder(), FakeVectorStore(), autre)
    assert (recherche.k, recherche.seuil) == (2, 0.1)


class _EmbedderTronquant(FakeEmbedder):
    """Simule `EmbedderLlama` : tronque au-delà de `limite` caractères et le compte."""

    def __init__(self, limite: int) -> None:
        super().__init__()
        self.limite = limite
        self.textes_tronques = 0

    def vectoriser(self, textes):
        self.textes_tronques += sum(len(t) > self.limite for t in textes)
        return super().vectoriser(textes)


def test_requete_tronquee_signalee_sans_erreur(caplog) -> None:
    embedder, store = _EmbedderTronquant(10), FakeVectorStore([passage(1, 0.9)])
    recherche = RechercheIndex(embedder, store, 3, 0.5)
    with caplog.at_level("WARNING", logger="slmsp.harness.recherche_index"):
        assert [p.chunk_id for p in recherche.rechercher("x" * 50)] == ["c1"]
    assert recherche.requetes_tronquees == 1
    assert "tronquée" in caplog.text
    recherche.rechercher("court")
    assert recherche.requetes_tronquees == 1


def test_embedder_sans_compteur_inchange() -> None:
    recherche = RechercheIndex(FakeEmbedder(), FakeVectorStore(), 3, 0.5)
    recherche.rechercher("x" * 50)
    assert recherche.requetes_tronquees == 0


def test_compteur_non_entier_ignore() -> None:
    embedder = FakeEmbedder()
    embedder.textes_tronques = object()  # doublure de type MagicMock
    recherche = RechercheIndex(embedder, FakeVectorStore(), 3, 0.5)
    recherche.rechercher("x" * 50)
    assert recherche.requetes_tronquees == 0


def test_passages_catalogue_reporte_le_compteur() -> None:
    from slmsp.harness.taches.recherche import passages_catalogue

    recherche = RechercheIndex(_EmbedderTronquant(10), FakeVectorStore(), 3, 0.5)
    passages_catalogue(recherche, "x" * 50)
    passages_catalogue(recherche, "court")
    assert recherche.requetes_tronquees == 1
