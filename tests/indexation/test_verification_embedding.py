"""Mesure H-EMB et `slmsp index verifier-embedding` (story 2.4)."""

from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

from slmsp.cli import CodeSortie, main
from slmsp.cli import index as cli_index
from slmsp.core.artefacts import ouvrir_run
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.schemas.mesure import ResultatMesure
from slmsp.index.config import charger_config_index
from slmsp.index.lecture import IndexLocal
from slmsp.indexation.verification_embedding import (
    NOM_DETAIL,
    NOM_RESULTAT,
    REPLI_F16,
    REPLI_Q8,
    cosinus_par_ligne,
    recall_a_k,
    tirer_rangs,
    verdict_h_emb,
    verifier_embedding,
)


class EmbedderBruite:
    """Embedder factice : vecteur MediaTech du texte, bruité de `sigma` (graine fixe)."""

    dimension = 1024

    def __init__(self, factice, sigma: float, graine: int = 3) -> None:
        self._par_texte = {
            ligne[5]: factice.vecteurs[rang].astype(np.float32)
            for rang, ligne in enumerate(factice.lignes)
        }
        self.sigma = sigma
        self._rng = np.random.default_rng(graine)
        self.textes: list[str] = []

    def vectoriser(self, textes):
        self.textes += list(textes)
        base = np.stack([self._par_texte[t] for t in textes])
        bruit = self._rng.standard_normal(base.shape).astype(np.float32)
        bruit /= np.linalg.norm(bruit, axis=1, keepdims=True)
        mixte = base + self.sigma * bruit
        return (mixte / np.linalg.norm(mixte, axis=1, keepdims=True)).astype(np.float32)


def _config(echantillon: int = 20, k: int = 5):
    config = charger_config_index()
    reglage = config.verification_embedding.model_copy(update={"echantillon": echantillon, "k": k})
    return config.model_copy(update={"taille_bloc": 16, "verification_embedding": reglage})


def test_config_production() -> None:
    reglage = charger_config_index().verification_embedding
    assert (reglage.echantillon, reglage.graine, reglage.k) == (200, 42, 10)
    assert reglage.seuil_cosinus_moyen == 0.99 and reglage.baisse_recall_max == 0.02


def test_cosinus_par_ligne() -> None:
    a = np.array([[1, 0], [0, 2], [1, 1]], dtype=np.float32)
    b = np.array([[2, 0], [1, 0], [-1, -1]], dtype=np.float16)
    np.testing.assert_allclose(cosinus_par_ligne(a, b), [1.0, 0.0, -1.0], atol=1e-7)
    with pytest.raises(ValueError, match="formes"):
        cosinus_par_ligne(a, b[:2])
    with pytest.raises(ValueError, match="nul"):
        cosinus_par_ligne(np.zeros((1, 2), dtype=np.float32), b[:1])


def test_recall_a_k() -> None:
    assert recall_a_k(np.array([3, 1, 2]), np.array([1, 2, 3])) == 1.0
    assert recall_a_k(np.array([1, 9, 8, 7]), np.array([1, 2, 3, 4])) == 0.25
    with pytest.raises(ValueError):
        recall_a_k(np.array([1]), np.array([], dtype=np.int64))


@pytest.mark.parametrize(
    ("cosinus", "recall", "verdict"),
    [
        (0.99, 0.98, "confirmee"),
        (1.0, 1.0, "confirmee"),
        (0.9899, 1.0, "infirmee"),
        (1.0, 0.9799, "infirmee"),
    ],
)
def test_verdict(cosinus: float, recall: float, verdict: str) -> None:
    obtenu, repli = verdict_h_emb(cosinus, recall, 0.99, 0.02)
    assert obtenu == verdict and repli == (REPLI_Q8 if verdict == "infirmee" else None)


def test_repli_f16_si_deja_en_f16() -> None:
    assert verdict_h_emb(0.5, 0.5, 0.99, 0.02, "bge-m3-f16") == ("infirmee", REPLI_F16)
    assert "F16" in REPLI_Q8 and "Anaël" in REPLI_Q8 and "Anaël" in REPLI_F16


def test_tirage_sans_remise_et_reproductible() -> None:
    premier = tirer_rangs(50, 20, 42)
    np.testing.assert_array_equal(premier, tirer_rangs(50, 20, 42))
    assert len(set(premier.tolist())) == 20 and premier.max() < 50
    assert len(tirer_rangs(50, 500, 42)) == 50


def test_mesure_confirmee(fabrique_index) -> None:
    factice = fabrique_index((30, 20))
    embedder = EmbedderBruite(factice, sigma=0.001)
    resultat = verifier_embedding(factice.racine, None, _config(), embedder)
    assert resultat.verdict == "confirmee" and resultat.repli is None
    assert resultat.mesure == "h-emb" and resultat.hypothese == "H-EMB"
    assert resultat.index_version == factice.version
    assert resultat.valeurs["cosinus_moyen"] > 0.999 and resultat.valeurs["recall_moyen"] >= 0.98
    assert resultat.valeurs["cosinus_min"] <= resultat.valeurs["cosinus_moyen"]
    assert resultat.seuils == {"cosinus_moyen": 0.99, "recall_min": pytest.approx(0.98)}
    assert resultat.parametres["echantillon"] == 20 and resultat.parametres["graine"] == 42
    assert resultat.parametres["modele"] == "bge-m3"
    assert len(embedder.textes) == 20 and len(set(embedder.textes)) == 20

    run = ouvrir_run(resultat.run_id, racine=factice.racine)
    assert "-h-emb-" in resultat.run_id and run.statut_courant() == "complet"
    assert run.manifeste.type == "measure" and run.manifeste.graine == 42
    ecrit = ResultatMesure.model_validate_json((run.dossier / NOM_RESULTAT).read_bytes())
    assert ecrit == resultat
    detail = json.loads((run.dossier / NOM_DETAIL).read_bytes())
    assert len(detail) == 20 and {"rang", "chunk_id", "cosinus", "recall"} <= set(detail[0])
    rang = detail[0]["rang"]
    assert detail[0]["chunk_id"] == factice.lignes[rang][0]
    assert np.mean([d["cosinus"] for d in detail]) == pytest.approx(
        resultat.valeurs["cosinus_moyen"]
    )


def test_mesure_infirmee_cosinus_et_recall(fabrique_index) -> None:
    factice = fabrique_index((30, 20))
    embedder = EmbedderBruite(factice, sigma=1.5)
    resultat = verifier_embedding(factice.racine, None, _config(), embedder, modele="bge-m3")
    assert resultat.verdict == "infirmee" and resultat.repli == REPLI_Q8
    assert resultat.valeurs["cosinus_moyen"] < 0.99
    assert resultat.valeurs["recall_moyen"] < 0.98
    run = ouvrir_run(resultat.run_id, racine=factice.racine)
    assert run.statut_courant() == "complet"


def test_echantillon_et_graine_en_parametres(fabrique_index) -> None:
    factice = fabrique_index((30, 20))
    resultat = verifier_embedding(
        factice.racine,
        None,
        _config(),
        EmbedderBruite(factice, 0.01),
        echantillon=500,
        graine=7,
    )
    assert resultat.parametres["echantillon"] == 50  # borné au corpus
    assert resultat.parametres["echantillon_demande"] == 500 and resultat.parametres["graine"] == 7


def test_erreurs(fabrique_index, tmp_path) -> None:
    factice = fabrique_index((30, 20))
    with pytest.raises(ValueError, match="échantillon"):
        verifier_embedding(
            factice.racine, None, _config(), EmbedderBruite(factice, 0), echantillon=0
        )
    embedder = EmbedderBruite(factice, 0)
    embedder.dimension = 8
    with pytest.raises(ManifesteInvalide, match="dimension"):
        verifier_embedding(factice.racine, None, _config(), embedder)
    with pytest.raises(ManifesteInvalide):
        verifier_embedding(tmp_path / "vide", None, _config(), EmbedderBruite(factice, 0))


def test_forme_inattendue_termine_le_run_en_erreur(fabrique_index) -> None:
    factice = fabrique_index((30, 20))

    class Court(EmbedderBruite):
        def vectoriser(self, textes):
            return super().vectoriser(textes)[:-1]

    with pytest.raises(ValueError, match="forme"):
        verifier_embedding(factice.racine, None, _config(), Court(factice, 0.01))
    (dossier,) = (factice.racine / "runs" / "measure").iterdir()
    assert ouvrir_run(dossier.name, racine=factice.racine).statut_courant() == "partiel-erreur"


def test_cli(fabrique_index, monkeypatch, capsys) -> None:
    factice = fabrique_index((30, 20))
    demandes = []

    def ouvrir(modele: str, variante: str):
        demandes.append((modele, variante))
        return contextlib.nullcontext((EmbedderBruite(factice, 0.01), {"gguf": "x.gguf"}))

    monkeypatch.setattr(cli_index, "_ouvrir_embedder", ouvrir)
    code = main(
        ["index", "verifier-embedding", "--racine", str(factice.racine), "--echantillon", "10"]
    )
    assert code == int(CodeSortie.SUCCES)
    sortie = capsys.readouterr().out
    assert "H-EMB" in sortie and "confirmee" in sortie and "cosinus moyen" in sortie
    assert "recall@10" in sortie and "run " in sortie
    assert demandes == [("bge-m3", "cpu")]
    (dossier,) = (factice.racine / "runs" / "measure").iterdir()
    ecrit = ResultatMesure.model_validate_json((dossier / NOM_RESULTAT).read_bytes())
    assert ecrit.parametres["echantillon"] == 10
    assert ecrit.parametres["serveur"] == {"gguf": "x.gguf"}


def test_cli_aide(capsys) -> None:
    main(["index", "verifier-embedding", "--help"])
    sortie = capsys.readouterr().out
    assert "--echantillon" in sortie and "--graine" in sortie and "--modele" in sortie


@pytest.mark.lent
def test_mesure_reelle_h_emb() -> None:
    """H-EMB réelle : exige l'Index v1, le GGUF BGE-M3 et llama-server (`SLMSP_RACINE_REELLE`)."""
    racine = os.environ.get("SLMSP_RACINE_REELLE")
    if not racine or not (Path(racine) / "index").is_dir():
        pytest.skip("SLMSP_RACINE_REELLE absent ou sans Index")
    code = main(["index", "verifier-embedding", "--racine", racine])
    assert code == int(CodeSortie.SUCCES)


def test_voisins_excluent_le_chunk_lui_meme(fabrique_index) -> None:
    from slmsp.indexation.verification_embedding import _voisins

    factice = fabrique_index((30, 20))
    config = _config()
    with IndexLocal(factice.dossier, taille_bloc=config.taille_bloc) as index:
        vecteur = np.array(index.vecteurs()[3], dtype=np.float32)
        voisins = _voisins(index, vecteur, 5, 3)
    assert 3 not in voisins and len(voisins) == 5
