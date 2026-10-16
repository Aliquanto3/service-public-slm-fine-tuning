"""Pilote des sources MediaTech et `slmsp fetch sources` de bout en bout."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.artefacts import EspaceInsuffisant
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.fetch import sources
from slmsp.fetch.config import ConfigSources, charger_config_sources

REV_A = "a" * 40
REV_B = "b" * 40
CONTENUS = {"p0": b"parquet 0" * 20, "p1": b"parquet 1" * 30, "c": b"catalogue" * 10}


def _url(depot: str, revision: str, chemin: str) -> str:
    return f"https://huggingface.co/datasets/{depot}/resolve/{revision}/{chemin}"


def _config(outils) -> ConfigSources:
    def fichier(chemin: str, cle: str) -> dict:
        return {"chemin": chemin, "sha256": outils.sha(CONTENUS[cle]), "taille": len(CONTENUS[cle])}

    return ConfigSources.model_validate(
        {
            "jeux": [
                {
                    "nom": "service-public",
                    "depot": "Org/service-public",
                    "revision": REV_A,
                    "licence": "etalab-2.0",
                    "fichiers": [
                        fichier("data/sp-latest/part_0.parquet", "p0"),
                        fichier("data/sp-latest/part_1.parquet", "p1"),
                    ],
                },
                {
                    "nom": "catalogue",
                    "depot": "Org/catalogue",
                    "revision": REV_B,
                    "licence": "etalab-2.0",
                    "fichiers": [fichier("data/cat/part_0.parquet", "c")],
                },
            ]
        }
    )


def _servir(banc) -> None:
    banc.serveur.servir(
        _url("Org/service-public", REV_A, "data/sp-latest/part_0.parquet"), CONTENUS["p0"]
    )
    banc.serveur.servir(
        _url("Org/service-public", REV_A, "data/sp-latest/part_1.parquet"), CONTENUS["p1"]
    )
    banc.serveur.servir(_url("Org/catalogue", REV_B, "data/cat/part_0.parquet"), CONTENUS["c"])


def test_disposition_et_url_resolve(banc, outils, tmp_path: Path) -> None:
    _servir(banc)
    lignes = []
    sources.executer(banc.telechargeur(), _config(outils), tmp_path, consigner=lignes.append)
    base = tmp_path / "data" / "raw" / "mediatech"
    assert (base / "service-public" / REV_A / "part_0.parquet").read_bytes() == CONTENUS["p0"]
    assert (base / "service-public" / REV_A / "part_1.parquet").read_bytes() == CONTENUS["p1"]
    assert (base / "catalogue" / REV_B / "part_0.parquet").read_bytes() == CONTENUS["c"]
    for requete in banc.serveur.requetes:
        assert requete.url.host == "huggingface.co"
        assert "/resolve/" in requete.url.path
    assert [(ligne["jeu"], ligne["revision"], ligne["statut"]) for ligne in lignes] == [
        ("service-public", REV_A, "telecharge"),
        ("service-public", REV_A, "telecharge"),
        ("catalogue", REV_B, "telecharge"),
    ]
    assert lignes[0]["licence"] == "etalab-2.0"
    assert lignes[0]["sha256"] == outils.sha(CONTENUS["p0"])


def test_choix_du_jeu(banc, outils, tmp_path: Path) -> None:
    _servir(banc)
    lignes = []
    sources.executer(
        banc.telechargeur(), _config(outils), tmp_path, jeux=["catalogue"], consigner=lignes.append
    )
    assert [ligne["jeu"] for ligne in lignes] == ["catalogue"]
    with pytest.raises(ConfigurationInvalide, match="jeu inconnu"):
        sources.executer(banc.telechargeur(), _config(outils), tmp_path, jeux=["absent"])


def test_noms_de_fichiers_en_double(outils, tmp_path: Path) -> None:
    config = _config(outils)
    jeu = config.jeux[1]
    double = jeu.fichiers[0].model_copy(update={"chemin": "autre/part_0.parquet"})
    config.jeux[1] = jeu.model_copy(update={"fichiers": [jeu.fichiers[0], double]})
    with pytest.raises(ConfigurationInvalide, match="même nom|le nom"):
        sources.planifier(config, tmp_path)


def test_espace_verifie_avant_toute_requete(banc, outils, tmp_path: Path) -> None:
    _servir(banc)
    telechargeur = banc.telechargeur(outils.reglages(marge_espace=10**18))
    with pytest.raises(EspaceInsuffisant):
        sources.executer(telechargeur, _config(outils), tmp_path)
    assert banc.serveur.requetes == []


def test_reutilisation_sans_requete(banc, outils, tmp_path: Path) -> None:
    local = tmp_path / "eval-sources"
    local.mkdir()
    for cle, contenu in CONTENUS.items():
        (local / f"{cle}.parquet").write_bytes(contenu)
    lignes = []
    telechargeur = banc.telechargeur(reutiliser=[local])
    sources.executer(telechargeur, _config(outils), tmp_path / "racine", consigner=lignes.append)
    assert {ligne["statut"] for ligne in lignes} == {"reutilise"}
    assert banc.serveur.requetes == []


# --- CLI ----------------------------------------------------------------------------------

SOURCES_TOML = """
[[jeux]]
nom = "catalogue"
depot = "Org/catalogue"
revision = "{rev}"
licence = "etalab-2.0"

[[jeux.fichiers]]
chemin = "data/cat/part_0.parquet"
sha256 = "{sha}"
taille = {taille}
"""


def test_cli_sources_de_bout_en_bout(banc, outils, cli, capsys) -> None:
    _servir(banc)
    (cli.config / "sources.toml").write_text(
        SOURCES_TOML.format(rev=REV_B, sha=outils.sha(CONTENUS["c"]), taille=len(CONTENUS["c"])),
        encoding="utf-8",
    )
    assert main(["fetch", "sources", "--racine", str(cli.racine)]) == 0
    destination = cli.racine / "data" / "raw" / "mediatech" / "catalogue" / REV_B
    assert (destination / "part_0.parquet").read_bytes() == CONTENUS["c"]
    run = outils.lire_run(cli.racine)
    assert run.manifeste["type"] == "fetch"
    assert run.manifeste["run_id"].split("-")[2] == "sources"
    assert "config/sources.toml" in run.manifeste["entrees"]
    (ligne,) = run.fichiers
    assert ligne["depot"] == "Org/catalogue"
    assert ligne["fichier"] == "data/cat/part_0.parquet"
    assert ligne["revision"] == REV_B
    assert ligne["octets"] == len(CONTENUS["c"])
    assert ligne["sha256"] == outils.sha(CONTENUS["c"])
    assert ligne["statut"] == "telecharge"
    assert run.statuts == ["en_cours", "complet"]
    (requete,) = banc.serveur.requetes
    assert requete.headers["Authorization"] == "Bearer jeton-factice"
    assert [(e.profil, e.hote, e.statut) for e in banc.journal.lister()] == [
        ("outillage", "huggingface.co", "envoyee")
    ]
    assert run.manifeste["run_id"] in capsys.readouterr().out


def test_cli_sources_sha_faux(banc, outils, cli, capsys) -> None:
    _servir(banc)
    (cli.config / "sources.toml").write_text(
        SOURCES_TOML.format(rev=REV_B, sha="0" * 64, taille=len(CONTENUS["c"])),
        encoding="utf-8",
    )
    assert main(["fetch", "sources", "--racine", str(cli.racine)]) == 1
    erreurs = capsys.readouterr().err
    assert "SHA-256" in erreurs
    run = outils.lire_run(cli.racine)
    assert f"run {run.manifeste['run_id']} : {run.dossier}" in erreurs
    assert run.statuts == ["en_cours", "partiel-erreur"]
    destination = cli.racine / "data" / "raw" / "mediatech" / "catalogue" / REV_B
    assert not (destination / "part_0.parquet").exists()


def _ecrire_sources(cli, outils) -> None:
    (cli.config / "sources.toml").write_text(
        SOURCES_TOML.format(rev=REV_B, sha=outils.sha(CONTENUS["c"]), taille=len(CONTENUS["c"])),
        encoding="utf-8",
    )


def test_cli_sources_reutiliser(banc, outils, cli, tmp_path: Path) -> None:
    _ecrire_sources(cli, outils)
    local = tmp_path / "eval-sources"
    local.mkdir()
    (local / "copie.parquet").write_bytes(CONTENUS["c"])
    arguments = ["fetch", "sources", "--racine", str(cli.racine), "--reutiliser", str(local)]
    assert main(arguments) == 0
    run = outils.lire_run(cli.racine)
    (ligne,) = run.fichiers
    assert ligne["statut"] == "reutilise" and ligne["octets"] == 0
    assert ligne["source"] == str(local / "copie.parquet")
    assert run.manifeste["config"]["reutiliser"] == [str(local.resolve())]
    assert run.statuts == ["en_cours", "complet"]
    assert banc.serveur.requetes == []


def test_cli_reutiliser_dossier_absent(outils, cli, tmp_path: Path, capsys) -> None:
    _ecrire_sources(cli, outils)
    absent = tmp_path / "absent"
    arguments = ["fetch", "sources", "--racine", str(cli.racine), "--reutiliser", str(absent)]
    assert main(arguments) == 1
    assert "n'est pas un dossier existant" in capsys.readouterr().err
    assert not (cli.racine / "runs").exists()


def test_cli_interruption(outils, cli, monkeypatch, capsys) -> None:
    _ecrire_sources(cli, outils)

    def interrompre(*_args, **_kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(sources, "executer", interrompre)
    with pytest.raises(KeyboardInterrupt):
        main(["fetch", "sources", "--racine", str(cli.racine)])
    run = outils.lire_run(cli.racine)
    assert run.statuts == ["en_cours", "interrompu"]
    assert f"run {run.manifeste['run_id']} : {run.dossier}" in capsys.readouterr().err


def test_cli_configuration_invalide_sans_run(cli, capsys) -> None:
    (cli.config / "sources.toml").write_text("jeux = []\n", encoding="utf-8")
    assert main(["fetch", "sources", "--racine", str(cli.racine)]) == 1
    assert "sources.toml" in capsys.readouterr().err
    assert not (cli.racine / "runs").exists()


# --- Configuration versionnée ----------------------------------------------------------


def test_config_versionnee() -> None:
    config = charger_config_sources()
    assert [jeu.nom for jeu in config.jeux] == [
        "service-public",
        "data-gouv-datasets-catalog",
        "piaf",
    ]
    assert [len(jeu.fichiers) for jeu in config.jeux] == [1, 3, 1]
    assert config.jeux[0].revision == "7ddda096b33d48dbda8143fc8c349a8b0e031a3a"
    assert config.jeux[1].revision == "11f3d3c9481ad478dbcff52e85d73b7fd10533ce"
    assert config.jeux[2].depot == "AgentPublic/piaf"
    assert config.jeux[2].revision == "bda8c063bc7297180796cd835d1974c0bc71c521"
    assert sum(f.taille for jeu in config.jeux for f in jeu.fichiers) == 663_393_073 + 650_352


@pytest.mark.reseau
def test_sources_reelles_conformes() -> None:
    """Réseau : taille et `X-Linked-Etag` publiés = config (HEAD seulement)."""
    from slmsp.fetch.config import charger_config_fetch
    from slmsp.fetch.hf import Telechargeur, client_hf, jeton_hf, url_hf

    config = charger_config_sources()
    with client_hf(jeton_hf()) as client:
        telechargeur = Telechargeur(client, charger_config_fetch())
        for jeu in config.jeux:
            for fichier in jeu.fichiers:
                meta = telechargeur.metadonnees_hf(
                    url_hf(jeu.depot, fichier.chemin, jeu.revision, type_depot="dataset")
                )
                assert (meta.taille, meta.sha256) == (fichier.taille, fichier.sha256)
