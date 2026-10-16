"""`slmsp fetch benchmarks` : transport factice, aucun réseau."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.fetch import benchmarks

REV = "c" * 40
CONTENU = b"jeu de test factice " * 5
URL = f"https://huggingface.co/datasets/Org/jeu-libre/resolve/{REV}/data/train.parquet"
URL_COND = f"https://huggingface.co/datasets/Org/jeu-cond/resolve/{REV}/data/dev.parquet"


def toml_benchmark(nom: str, jeux: str) -> str:
    return (
        f'nom = "{nom}"\nmoteur = "factice"\ntache = "t"\ncible = "gguf"\n'
        f'quantification = "avant"\n{jeux}'
    )


def jeu(nom: str, depot: str, sha: str, chemin: str, acces: str = "libre") -> str:
    return (
        f'\n[[jeux]]\nnom = "{nom}"\ndepot = "{depot}"\nrevision = "{REV}"\nacces = "{acces}"\n'
        f'licence = "mit"\n\n[[jeux.fichiers]]\nchemin = "{chemin}"\nsha256 = "{sha}"\n'
        f"taille = {len(CONTENU)}\n"
    )


@pytest.fixture
def decl(cli, outils) -> Path:
    dossier = cli.config / "benchmarks"
    dossier.mkdir()
    sha = outils.sha(CONTENU)
    (dossier / "libre.toml").write_text(
        toml_benchmark("libre", jeu("jeu-libre", "Org/jeu-libre", sha, "data/train.parquet")),
        encoding="utf-8",
    )
    (dossier / "cond.toml").write_text(
        toml_benchmark(
            "cond", jeu("jeu-cond", "Org/jeu-cond", sha, "data/dev.parquet", "conditionnel")
        ),
        encoding="utf-8",
    )
    (dossier / "libre2.toml").write_text(
        toml_benchmark("libre2", jeu("jeu-libre", "Org/jeu-libre", sha, "data/train.parquet")),
        encoding="utf-8",
    )
    (dossier / "sans.toml").write_text(
        toml_benchmark("sans", '\n[[jeux]]\nnom = "libre-non-epingle"\ndepot = "Org/autre"\n'),
        encoding="utf-8",
    )
    return dossier


def test_telechargement_epingle_conditionnel_saute_et_consigne(cli, banc, decl, outils, capsys):
    banc.serveur.servir(URL, CONTENU)
    banc.serveur.servir(URL_COND, b"", pannes=[], redirection=None)
    del banc.serveur.fichiers[URL_COND]  # 404 : accès refusé au jeu conditionnel
    assert main(["fetch", "benchmarks", "--racine", str(cli.racine)]) == 0
    destination = (
        cli.racine / "data" / "raw" / "benchmarks" / "jeu-libre" / REV / "data" / "train.parquet"
    )
    assert destination.read_bytes() == CONTENU
    run = outils.lire_run(cli.racine)
    par_jeu = {ligne["jeu"]: ligne for ligne in run.fichiers}
    assert par_jeu["jeu-libre"]["statut"] == "telecharge"
    assert par_jeu["jeu-libre"]["revision"] == REV
    assert par_jeu["jeu-cond"]["statut"] == "acces-conditionnel"
    assert par_jeu["libre-non-epingle"]["statut"] == "non-epingle"
    assert len([ligne for ligne in run.fichiers if ligne["jeu"] == "jeu-libre"]) == 1
    assert run.statuts == ["en_cours", "complet"]
    for requete in banc.serveur.requetes:
        assert requete.url.host == "huggingface.co" and "/resolve/" in requete.url.path
    assert "acces-conditionnel" in capsys.readouterr().out


def test_jeu_libre_en_echec_n_est_pas_saute(cli, banc, decl, outils, capsys) -> None:
    assert main(["fetch", "benchmarks", "libre", "--racine", str(cli.racine)]) == 1
    assert outils.lire_run(cli.racine).statuts == ["en_cours", "partiel-erreur"]
    assert "404" in capsys.readouterr().err


def test_choix_du_benchmark(cli, banc, decl, outils) -> None:
    banc.serveur.servir(URL, CONTENU)
    assert main(["fetch", "benchmarks", "libre", "--racine", str(cli.racine)]) == 0
    assert [ligne["jeu"] for ligne in outils.lire_run(cli.racine).fichiers] == ["jeu-libre"]


def test_benchmark_inconnu_et_dossier_absent(cli, decl, tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="benchmark inconnu : absent"):
        benchmarks.lire_jeux(decl, ["absent"])
    with pytest.raises(ConfigurationInvalide, match="introuvable"):
        benchmarks.lire_jeux(tmp_path / "rien")


def test_jeu_declare_differemment(decl) -> None:
    (decl / "libre2.toml").write_text(
        toml_benchmark("libre2", jeu("jeu-libre", "Org/jeu-libre", "d" * 64, "data/train.parquet")),
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationInvalide, match="déclaré différemment"):
        benchmarks.lire_jeux(decl)


def test_config_versionnee_se_lit() -> None:
    from slmsp.fetch.config import dossier_config

    noms = {jeu.nom for jeu in benchmarks.lire_jeux(dossier_config() / "benchmarks")}
    assert {"mcq-eval", "flores-200"} <= noms
