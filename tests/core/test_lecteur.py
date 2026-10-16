"""Lecteur contrôlé `data` / `train` (critères 5 et 6, story 1.3, AD-24)."""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pytest

from slmsp.core.artefacts import chemin_autorise, lire, lire_texte, ouvrir_sqlite_lecture
from slmsp.core.erreurs import CodeSortie, LectureInterdite
from slmsp.core.var import dossier_var, ouvrir_sqlite

FICHIERS = [
    "data/raw/x.parquet",
    "data/cassettes/c.json",
    "data/registre-licences.toml",
    "data/train/v1/train.jsonl",
    "runs/data-seed/20261012-101500-v1-0a1f/a.jsonl",
    "runs/eval-generation/20261012-101500-granite-0a1f/generations.jsonl",
    "runs/eval/20261012-101500-granite-0a1f/x.json",
    "runs/bench/20261012-101500-granite-0a1f/x.json",
    "config/outils-mcp.toml",
    "config/taches.toml",
    "config/prompts/generateur/g.txt",
    "index/2026-10/MANIFEST.json",
    "eval/jeu/v1/Q.jsonl",
]


@pytest.fixture
def racine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    racine = tmp_path / "projet"
    for relatif in FICHIERS:
        chemin = racine / relatif
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_bytes(f"<contenu-factice:{relatif}>".encode())
    modeles = tmp_path / "modeles"
    (modeles / "granite").mkdir(parents=True)
    (modeles / "granite" / "config.json").write_bytes(b"{}")
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(modeles))
    var = dossier_var()
    for nom in ("appels-mistral.sqlite", "verdicts.sqlite", "budget.sqlite"):
        connexion = ouvrir_sqlite(var / nom)  # WAL, comme en production
        connexion.execute("CREATE TABLE t (x INTEGER)")
        connexion.execute("INSERT INTO t VALUES (1)")
        connexion.commit()
        connexion.close()
    return racine


@pytest.mark.parametrize(
    "relatif",
    [
        "data/raw/x.parquet",
        "data/cassettes/c.json",
        "data/registre-licences.toml",
        "runs/data-seed/20261012-101500-v1-0a1f/a.jsonl",
        "config/outils-mcp.toml",
        "config/prompts/generateur/g.txt",
        "index/2026-10/MANIFEST.json",
    ],
)
def test_data_permis(racine: Path, relatif: str) -> None:
    assert lire(relatif, "data", racine=racine) == f"<contenu-factice:{relatif}>".encode()
    assert lire(racine / relatif, "data", racine=racine) == lire(relatif, "data", racine=racine)
    assert lire_texte(relatif, "data", racine=racine) == f"<contenu-factice:{relatif}>"


def test_data_lit_le_journal_mistral(racine: Path) -> None:
    journal = dossier_var() / "appels-mistral.sqlite"
    assert lire(journal, "data", racine=racine).startswith(b"SQLite format 3")


@pytest.mark.parametrize(
    "relatif",
    [
        "eval/jeu/v1/Q.jsonl",
        "runs/eval-generation/20261012-101500-granite-0a1f/generations.jsonl",
        "runs/eval/20261012-101500-granite-0a1f/x.json",
        "runs/bench/20261012-101500-granite-0a1f/x.json",
        "data/raw/../../eval/jeu/v1/Q.jsonl",
        "data/raw/../train/v1/train.jsonl",
        "config/taches.toml",
        "data/train/v1/train.jsonl",
        "runs/data-seed/../eval-generation/20261012-101500-granite-0a1f/generations.jsonl",
        "../hors-projet.txt",
    ],
)
def test_data_refuse(racine: Path, relatif: str) -> None:
    with pytest.raises(LectureInterdite) as erreur:
        lire(relatif, "data", racine=racine)
    message = str(erreur.value)
    assert "« data »" in message
    assert str((racine / relatif).resolve()) in message
    assert erreur.value.code_sortie == CodeSortie.ERREUR


@pytest.mark.parametrize("nom", ["verdicts.sqlite", "budget.sqlite"])
def test_data_refuse_autres_bases_var(racine: Path, nom: str) -> None:
    with pytest.raises(LectureInterdite):
        lire(dossier_var() / nom, "data", racine=racine)
    with pytest.raises(LectureInterdite):
        ouvrir_sqlite_lecture(dossier_var() / nom, "data", racine=racine)


def test_train_permis(racine: Path, tmp_path: Path) -> None:
    assert lire("data/train/v1/train.jsonl", "train", racine=racine).startswith(b"<contenu")
    assert lire(tmp_path / "modeles" / "granite" / "config.json", "train", racine=racine) == b"{}"
    assert lire(dossier_var() / "appels-mistral.sqlite", "train", racine=racine)


@pytest.mark.parametrize(
    "relatif",
    [
        "data/raw/x.parquet",
        "eval/jeu/v1/Q.jsonl",
        "runs/data-seed/20261012-101500-v1-0a1f/a.jsonl",
        "config/outils-mcp.toml",
        "index/2026-10/MANIFEST.json",
        "data/train/../raw/x.parquet",
    ],
)
def test_train_refuse(racine: Path, relatif: str) -> None:
    with pytest.raises(LectureInterdite, match="« train »"):
        lire(relatif, "train", racine=racine)


RUN_TRAIN = "runs/train/20261016-120000-m1-qlora-abcd"


def test_train_lit_l_adaptateur_d_un_run_train(racine: Path) -> None:
    """AD-24 étendu (décision A1 du 2026-10-16) : export et ORPO lisent l'adaptateur."""
    fichier = racine / RUN_TRAIN / "adaptateur" / "adapter_config.json"
    fichier.parent.mkdir(parents=True)
    fichier.write_bytes(b"{}")
    assert lire(fichier, "train", racine=racine) == b"{}"
    assert chemin_autorise(fichier.parent, "train", racine=racine) == fichier.parent.resolve()


@pytest.mark.parametrize(
    "relatif",
    [
        f"{RUN_TRAIN}/run.json",
        f"{RUN_TRAIN}/checkpoints/checkpoint-1/x.bin",
        f"{RUN_TRAIN}/adaptateur/../run.json",
        "runs/train/pas-un-run-id/adaptateur/a.json",
        "runs/export/20261016-120000-m1-qlora-abcd/adaptateur/a.json",
    ],
)
def test_train_refuse_le_reste_des_runs(racine: Path, relatif: str) -> None:
    with pytest.raises(LectureInterdite, match="« train »"):
        chemin_autorise(relatif, "train", racine=racine)


def test_data_ne_lit_pas_l_adaptateur(racine: Path) -> None:
    with pytest.raises(LectureInterdite, match="« data »"):
        chemin_autorise(f"{RUN_TRAIN}/adaptateur/a.json", "data", racine=racine)


@pytest.mark.parametrize("lecteur", ["data", "train"])
def test_refus_explicite_du_cache_verdicts(racine: Path, lecteur: str) -> None:
    # Le motif prouve le refus explicite, pas un simple « hors de la liste d'accès ».
    with pytest.raises(LectureInterdite, match="cache des verdicts"):
        lire(dossier_var() / "verdicts.sqlite", lecteur, racine=racine)


def test_nom_du_cache_verdicts_aligne_sur_le_juge() -> None:
    # `core` ne peut pas importer `judge` : le test garde les deux constantes alignées.
    from slmsp.core.artefacts import NOM_CACHE_VERDICTS
    from slmsp.judge.cache import NOM_CACHE

    assert NOM_CACHE_VERDICTS == NOM_CACHE


@pytest.mark.parametrize("lecteur", ["eval", "", "DATA", "judge"])
def test_lecteur_inconnu(racine: Path, lecteur: str) -> None:
    with pytest.raises(ValueError):
        lire("data/raw/x.parquet", lecteur, racine=racine)


def test_lien_symbolique_vers_eval(racine: Path) -> None:
    lien = racine / "data" / "raw" / "lien"
    try:
        os.symlink(racine / "eval" / "jeu", lien, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("création de lien symbolique refusée par le système")
    with pytest.raises(LectureInterdite, match="eval"):
        lire("data/raw/lien/v1/Q.jsonl", "data", racine=racine)


@pytest.mark.skipif(sys.platform != "win32", reason="jonction NTFS : Windows seulement")
def test_jonction_windows_vers_eval(racine: Path) -> None:
    import _winapi

    lien = racine / "data" / "raw" / "jonction"
    _winapi.CreateJunction(str(racine / "eval" / "jeu"), str(lien))
    assert (lien / "v1" / "Q.jsonl").is_file()
    with pytest.raises(LectureInterdite, match="eval"):
        lire("data/raw/jonction/v1/Q.jsonl", "data", racine=racine)


@pytest.mark.skipif(sys.platform != "win32", reason="jonction NTFS : Windows seulement")
def test_base_en_jonction_reste_lisible(tmp_path: Path) -> None:
    import _winapi

    principal = tmp_path / "principal" / "raw"
    principal.mkdir(parents=True)
    (principal / "x.parquet").write_bytes(b"<parquet-factice>")
    racine = tmp_path / "worktree"
    (racine / "data").mkdir(parents=True)
    _winapi.CreateJunction(str(principal), str(racine / "data" / "raw"))
    assert lire("data/raw/x.parquet", "data", racine=racine) == b"<parquet-factice>"


def test_lien_symbolique_fichier_vers_eval(racine: Path) -> None:
    lien = racine / "data" / "raw" / "q.jsonl"
    try:
        os.symlink(racine / "eval" / "jeu" / "v1" / "Q.jsonl", lien)
    except (OSError, NotImplementedError):
        pytest.skip("création de lien symbolique refusée par le système")
    with pytest.raises(LectureInterdite):
        lire(lien, "data", racine=racine)


@pytest.mark.skipif(sys.platform != "win32", reason="casse ignorée seulement sous Windows")
def test_casse_ignoree_sous_windows(racine: Path) -> None:
    assert lire("DATA/Raw/x.parquet", "data", racine=racine).startswith(b"<contenu")
    with pytest.raises(LectureInterdite):
        lire("EVAL/jeu/v1/Q.jsonl", "data", racine=racine)
    with pytest.raises(LectureInterdite):
        lire(
            "Runs/EVAL-generation/20261012-101500-granite-0a1f/generations.jsonl",
            "data",
            racine=racine,
        )


def test_chemin_autorise_renvoie_le_chemin_resolu(racine: Path) -> None:
    resolu = chemin_autorise("data/raw/../raw/x.parquet", "data", racine=racine)
    assert resolu == (racine / "data" / "raw" / "x.parquet").resolve()


def test_sqlite_en_lecture_seule(racine: Path) -> None:
    connexion = ouvrir_sqlite_lecture(
        dossier_var() / "appels-mistral.sqlite", "train", racine=racine
    )
    try:
        assert connexion.execute("SELECT x FROM t").fetchall() == [(1,)]
        with pytest.raises(sqlite3.OperationalError):
            connexion.execute("INSERT INTO t VALUES (2)")
    finally:
        connexion.close()


def test_sqlite_refuse_hors_liste(racine: Path) -> None:
    with pytest.raises(LectureInterdite):
        ouvrir_sqlite_lecture("eval/jeu/v1/Q.jsonl", "data", racine=racine)
