"""Lecture de l'Index local, recherche exacte et `slmsp index info` (story 2.3)."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.ports import Passage, VectorStore
from slmsp.index.config import NOM_CHUNKS, NOM_MANIFESTE, NOM_VECTEURS
from slmsp.index.lecture import (
    IndexLocal,
    candidats_top_k,
    fusionner_top_k,
    lire_manifeste,
    ouvrir_index,
    versions_disponibles,
)

DIMENSION = 1024


def _reference(vecteurs: np.ndarray, requete: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Force brute numpy float32 : score décroissant puis rang croissant."""
    scores = vecteurs.astype(np.float32) @ requete
    ordre = np.lexsort((np.arange(len(scores)), -scores))[:k]
    return ordre, scores[ordre]


def _requetes(factice) -> list[np.ndarray]:
    rng = np.random.default_rng(123)
    aleatoire = rng.standard_normal(DIMENSION).astype(np.float32)
    aleatoire /= np.linalg.norm(aleatoire)
    return [
        aleatoire,
        factice.vecteurs[11].astype(np.float32),
        -factice.vecteurs[40].astype(np.float32),
    ]


# --- Recherche exacte ------------------------------------------------------------------


TAILLES_BLOC = [1, 3, 5, 16, 61, 62, 4096]
VALEURS_K = (1, 3, 10, 61, 62)


@pytest.mark.parametrize("taille_bloc", TAILLES_BLOC)
def test_recherche_egale_reference_float32(fabrique_index, taille_bloc: int) -> None:
    """Vecteurs aléatoires : rangs de la référence, scores à l'arrondi float32 près (BLAS)."""
    factice = fabrique_index()
    with IndexLocal(factice.dossier, taille_bloc=taille_bloc) as index:
        for requete in _requetes(factice):
            for k in VALEURS_K:
                rangs, scores = index.classer(requete, k)
                attendus, scores_attendus = _reference(factice.vecteurs, requete, k)
                np.testing.assert_array_equal(rangs, attendus)
                np.testing.assert_allclose(scores, scores_attendus, rtol=0, atol=1e-6)
                assert scores.dtype == np.float32


def _vecteurs_dyadiques(n: int, graine: int) -> np.ndarray:
    """Quatre composantes ±0,5 par ligne (norme 1) : tout produit scalaire est exact."""
    rng = np.random.default_rng(graine)
    vecteurs = np.zeros((n, DIMENSION), dtype=np.float32)
    for ligne in vecteurs:
        ligne[rng.choice(48, size=4, replace=False)] = rng.choice([-0.5, 0.5], size=4)
    return vecteurs


@pytest.mark.parametrize("taille_bloc", TAILLES_BLOC)
def test_recherche_identique_au_bit_avec_ex_aequo(fabrique_index, taille_bloc: int) -> None:
    """Sommes partielles exactes : rangs et scores égaux au bit près, ex-aequo nombreux."""
    factice = fabrique_index(
        (37, 25), vecteurs=[_vecteurs_dyadiques(37, 1), _vecteurs_dyadiques(25, 2)]
    )
    rng = np.random.default_rng(5)
    requetes = [
        np.where(np.arange(DIMENSION) < 48, rng.integers(-8, 9, DIMENSION) / 16, 0).astype(
            np.float32
        )
        for _ in range(3)
    ] + [factice.vecteurs[30].astype(np.float32)]
    with IndexLocal(factice.dossier, taille_bloc=taille_bloc) as index:
        for requete in requetes:
            scores_complets = factice.vecteurs.astype(np.float32) @ requete
            assert len(np.unique(scores_complets)) < len(scores_complets)  # ex-aequo présents
            for k in VALEURS_K:
                rangs, scores = index.classer(requete, k)
                attendus, scores_attendus = _reference(factice.vecteurs, requete, k)
                np.testing.assert_array_equal(rangs, attendus)
                np.testing.assert_array_equal(scores, scores_attendus)


def test_candidats_et_fusion_top_k() -> None:
    scores = np.array([0.5, 0.9, 0.5, 0.1, 0.9, 0.5], dtype=np.float32)
    assert candidats_top_k(scores, 1).tolist() == [1, 4]
    assert candidats_top_k(scores, 3).tolist() == [0, 1, 2, 4, 5]
    assert candidats_top_k(scores, 6).tolist() == [0, 1, 2, 3, 4, 5]
    rangs = np.array([10, 3, 7, 1, 2, 8], dtype=np.int64)
    fusion_rangs, fusion_scores = fusionner_top_k(rangs, scores, 4)
    assert fusion_rangs.tolist() == [2, 3, 7, 8]
    assert fusion_scores.tolist() == pytest.approx([0.9, 0.9, 0.5, 0.5])


def test_rechercher_remplit_les_passages(fabrique_index) -> None:
    factice = fabrique_index()
    requete = factice.vecteurs[45].astype(np.float32)
    with IndexLocal(factice.dossier, taille_bloc=8) as index:
        assert isinstance(index, VectorStore)
        passages = index.rechercher(requete, 5)
    attendus, scores = _reference(factice.vecteurs, requete, 5)
    assert attendus[0] == 45
    assert all(isinstance(p, Passage) for p in passages)
    for passage, rang, score in zip(passages, attendus, scores, strict=True):
        chunk_id, doc_id, source, titre, url, texte = factice.lignes[rang]
        assert (passage.chunk_id, passage.doc_id, passage.source) == (chunk_id, doc_id, source)
        assert (passage.titre, passage.url, passage.texte) == (titre, url, texte)
        attendue = next(s for s in factice.config.sources if s.nom == source).date_snapshot
        assert passage.date_snapshot == attendue.isoformat()
        assert isinstance(passage.score, float) and passage.score == float(score)
    assert [p.score for p in passages] == sorted((p.score for p in passages), reverse=True)


def test_ex_aequo_departages_par_rang_croissant(fabrique_index) -> None:
    # Lignes unitaires e_i : le score vaut exactement requete[i], quel que soit le découpage.
    base = np.eye(6, DIMENSION, dtype=np.float32)
    # e_0 est répété aux rangs 0, 3, 7, 9 (sources confondues) : scores égaux.
    premiere = np.stack([base[0], base[1], base[2], base[0], base[3]])
    seconde = np.stack([base[4], base[5], base[0], base[1], base[0]])
    factice = fabrique_index((5, 5), vecteurs=[premiere, seconde])
    requete = np.zeros(DIMENSION, dtype=np.float32)
    requete[:6] = [0.9, 0.1, 0.2, 0.3, 0.4, 0.5]
    for taille_bloc in (1, 2, 3, 10):
        with IndexLocal(factice.dossier, taille_bloc=taille_bloc) as index:
            rangs, scores = index.classer(requete, 3)
            assert rangs.tolist() == [0, 3, 7]
            assert scores.tolist() == [np.float32(0.9)] * 3
            rangs, _ = index.classer(requete, 5)
            assert rangs.tolist() == [0, 3, 7, 9, 6]


def test_k_superieur_a_n_renvoie_n_resultats(fabrique_index) -> None:
    factice = fabrique_index((4, 3))
    with IndexLocal(factice.dossier, taille_bloc=2) as index:
        passages = index.rechercher(factice.vecteurs[2].astype(np.float32), 100)
    assert len(passages) == 7
    assert len({p.chunk_id for p in passages}) == 7


@pytest.mark.parametrize("k", [0, -1, True, 2.0, "3"])
def test_k_invalide(fabrique_index, k) -> None:
    factice = fabrique_index((3, 2))
    with IndexLocal(factice.dossier) as index, pytest.raises(ValueError, match="k doit"):
        index.rechercher(factice.vecteurs[0].astype(np.float32), k)


@pytest.mark.parametrize(
    "requete",
    [
        np.zeros(1023, dtype=np.float32),
        np.zeros(1025, dtype=np.float32),
        np.zeros((2, 1024), dtype=np.float32),
        np.full(1024, np.nan, dtype=np.float32),
        np.concatenate([np.ones(1023), [np.inf]]).astype(np.float32),
        "pas un vecteur",
    ],
    ids=["1023", "1025", "deux-lignes", "nan", "inf", "texte"],
)
def test_requete_invalide(fabrique_index, requete) -> None:
    factice = fabrique_index((3, 2))
    with IndexLocal(factice.dossier) as index, pytest.raises(ValueError):
        index.rechercher(requete, 2)


def test_requete_ligne_unique_acceptee(fabrique_index) -> None:
    factice = fabrique_index((3, 2))
    with IndexLocal(factice.dossier) as index:
        passages = index.rechercher(factice.vecteurs[1:2].astype(np.float32), 1)
    assert passages[0].chunk_id == factice.lignes[1][0]


def test_index_ferme(fabrique_index) -> None:
    factice = fabrique_index((3, 2))
    index = IndexLocal(factice.dossier)
    index.fermer()
    index.fermer()
    with pytest.raises(ManifesteInvalide, match="fermé"):
        index.rechercher(factice.vecteurs[0].astype(np.float32), 1)


def test_base_ouverte_en_lecture_seule(fabrique_index) -> None:
    factice = fabrique_index((3, 2))
    with IndexLocal(factice.dossier) as index:
        index.rechercher(factice.vecteurs[0].astype(np.float32), 2)
        with pytest.raises(sqlite3.OperationalError):
            index._connexion.execute("DELETE FROM chunks")
        index.verifier()


# --- Versions et ouverture -----------------------------------------------------------


def test_versions_et_ouverture_de_la_plus_recente(fabrique_index, tmp_path: Path) -> None:
    ancien = fabrique_index((3, 2), dates=[date(2026, 1, 2), date(2026, 1, 3)])
    recent = fabrique_index((4, 2), dates=[date(2026, 5, 1), date(2026, 4, 1)])
    (tmp_path / "index" / ".20261231.en-cours-ab12").mkdir()
    (tmp_path / "index" / "notes").mkdir()
    assert versions_disponibles(tmp_path) == ["20260103", "20260501"]
    assert (ancien.version, recent.version) == ("20260103", "20260501")
    with ouvrir_index(tmp_path) as index:
        assert index.version == "20260501" and index.nb_chunks == 6
        assert index.date_snapshot == "2026-05-01"
        assert index.taille_bloc == 4096
    with ouvrir_index(tmp_path, "20260103", taille_bloc=2) as index:
        assert index.nb_chunks == 5 and index.taille_bloc == 2


def test_index_absent(tmp_path: Path) -> None:
    assert versions_disponibles(tmp_path) == []
    with pytest.raises(ManifesteInvalide, match="aucun Index"):
        ouvrir_index(tmp_path)


@pytest.mark.parametrize("version", ["20990101", "2026", "../index", "20260926/.."])
def test_version_inconnue(fabrique_index, version: str) -> None:
    factice = fabrique_index((3, 2))
    with pytest.raises(ManifesteInvalide, match="inconnue"):
        ouvrir_index(factice.racine, version)


def _copie(factice, tmp_path: Path) -> Path:
    cible = tmp_path / "copie" / "index" / factice.version
    shutil.copytree(factice.dossier, cible)
    return cible


def test_forme_des_vecteurs_incoherente(fabrique_index, tmp_path: Path) -> None:
    factice = fabrique_index((3, 2))
    cible = _copie(factice, tmp_path)
    (cible / NOM_VECTEURS).unlink()
    np.save(cible / NOM_VECTEURS, factice.vecteurs[:4])
    with pytest.raises(ManifesteInvalide, match="incohérents"):
        IndexLocal(cible)


def test_type_des_vecteurs_incoherent(fabrique_index, tmp_path: Path) -> None:
    factice = fabrique_index((3, 2))
    cible = _copie(factice, tmp_path)
    (cible / NOM_VECTEURS).unlink()
    np.save(cible / NOM_VECTEURS, factice.vecteurs.astype(np.float32))
    with pytest.raises(ManifesteInvalide, match="incohérents"):
        IndexLocal(cible)


def test_lignes_sqlite_incoherentes(fabrique_index, tmp_path: Path) -> None:
    factice = fabrique_index((3, 2))
    cible = _copie(factice, tmp_path)
    connexion = sqlite3.connect(cible / NOM_CHUNKS)
    connexion.execute("DELETE FROM chunks WHERE rang = 4")
    connexion.commit()
    connexion.close()
    with pytest.raises(ManifesteInvalide, match="ligne"):
        IndexLocal(cible)


def test_manifeste_absent_ou_invalide(fabrique_index, tmp_path: Path) -> None:
    factice = fabrique_index((3, 2))
    cible = _copie(factice, tmp_path)
    contenu = json.loads((cible / NOM_MANIFESTE).read_text(encoding="utf-8"))
    (cible / NOM_MANIFESTE).unlink()
    with pytest.raises(ManifesteInvalide, match="illisible"):
        IndexLocal(cible)
    contenu["nb_chunks"] = 99
    (cible / NOM_MANIFESTE).write_text(json.dumps(contenu), encoding="utf-8")
    with pytest.raises(ManifesteInvalide, match="invalide"):
        IndexLocal(cible)


def _manifeste_modifie(factice, tmp_path: Path, modifier) -> Path:
    cible = _copie(factice, tmp_path)
    contenu = json.loads((cible / NOM_MANIFESTE).read_text(encoding="utf-8"))
    modifier(contenu)
    (cible / NOM_MANIFESTE).write_bytes(json.dumps(contenu).encode("utf-8"))
    return cible


def test_manifeste_version_differente_de_la_date_refusee(fabrique_index, tmp_path: Path) -> None:
    def decaler(contenu: dict) -> None:
        contenu["date_snapshot"] = "2026-09-27"

    cible = _manifeste_modifie(fabrique_index((3, 2)), tmp_path, decaler)
    with pytest.raises(ManifesteInvalide, match="date du snapshot"):
        lire_manifeste(cible)


def test_manifeste_sources_homonymes_refusees(fabrique_index, tmp_path: Path) -> None:
    def homonymes(contenu: dict) -> None:
        contenu["sources"][1]["nom"] = contenu["sources"][0]["nom"]

    cible = _manifeste_modifie(fabrique_index((3, 2)), tmp_path, homonymes)
    with pytest.raises(ManifesteInvalide, match="même nom"):
        lire_manifeste(cible)


def test_version_du_manifeste_differente_du_dossier(fabrique_index, tmp_path: Path) -> None:
    factice = fabrique_index((3, 2))
    cible = tmp_path / "copie" / "index" / "20200101"
    shutil.copytree(factice.dossier, cible)
    with pytest.raises(ManifesteInvalide, match="nom du dossier"):
        IndexLocal(cible)


def test_verifier_detecte_un_fichier_modifie(fabrique_index, tmp_path: Path) -> None:
    factice = fabrique_index((3, 2))
    cible = _copie(factice, tmp_path)
    with IndexLocal(cible) as index:
        index.verifier()
    with (cible / NOM_VECTEURS).open("r+b") as flux:
        flux.seek(-2, os.SEEK_END)
        octets = flux.read(2)
        flux.seek(-2, os.SEEK_END)
        flux.write(bytes(b ^ 0x01 for b in octets))
    with IndexLocal(cible) as index, pytest.raises(ManifesteInvalide, match="SHA-256"):
        index.verifier()


# --- CLI ---------------------------------------------------------------------------------


def test_cli_info(fabrique_index, capsys: pytest.CaptureFixture[str]) -> None:
    factice = fabrique_index((4, 3))
    assert main(["index", "info", "--racine", str(factice.racine)]) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert f"Index {factice.version}" in sortie
    assert "date du snapshot : 2026-09-26" in sortie
    assert "chunks : 7" in sortie
    assert "service-public : 4 chunks" in sortie
    assert "data-gouv-datasets-catalog : 3 chunks" in sortie
    assert "SHA-256" not in sortie


def test_cli_info_verifier(fabrique_index, capsys: pytest.CaptureFixture[str]) -> None:
    factice = fabrique_index((4, 3))
    code = main(
        ["index", "info", "--racine", str(factice.racine), "--version", "20260926", "--verifier"]
    )
    assert code == CodeSortie.SUCCES
    assert "SHA-256 vérifiés" in capsys.readouterr().out
    with (factice.dossier / NOM_CHUNKS).open("ab") as flux:
        flux.write(b"\0")
    code = main(["index", "info", "--racine", str(factice.racine), "--verifier"])
    assert code == CodeSortie.MANIFESTE_INVALIDE
    assert "SHA-256" in capsys.readouterr().err


def test_cli_info_sans_index(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["index", "info", "--racine", str(tmp_path)]) == CodeSortie.MANIFESTE_INVALIDE
    assert "aucun Index" in capsys.readouterr().err
    code = main(["index", "info", "--racine", str(tmp_path), "--version", "20260101"])
    assert code == CodeSortie.MANIFESTE_INVALIDE


# --- Fermeture runtime -----------------------------------------------------------------


def test_lecture_et_cli_sans_pyarrow_ni_duckdb() -> None:
    code = (
        "import sys, slmsp.index.lecture, slmsp.cli.index; "
        "lourds = sorted(m for m in sys.modules if m.split('.')[0] in ('pyarrow', 'duckdb')); "
        "print(lourds); sys.exit(1 if lourds else 0)"
    )
    resultat = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        encoding="utf-8",
        cwd=racine_projet(),
        check=False,
    )
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr


def test_contient_url(fabrique_index) -> None:
    factice = fabrique_index()
    with IndexLocal(factice.dossier) as index:
        url = factice.lignes[0][4]
        assert index.contient_url(url) is True
        assert index.contient_url(url + "-absente") is False
