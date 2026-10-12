"""Pilote des modèles (`config/modeles/<slug>.toml`) et `slmsp fetch modeles`."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.config import dossier_modeles
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.fetch import modeles
from slmsp.fetch.config import charger_config_modele
from slmsp.fetch.hf import ShaInvalide, TelechargementEchoue

REV = "c" * 40
COMMIT_MAIN = "d" * 40
GGUF = b"GGUF factice " * 40
POIDS = b"poids factices " * 30


def _url(depot: str, revision: str, chemin: str) -> str:
    return f"https://huggingface.co/{depot}/resolve/{revision}/{chemin}"


def _config(outils, **valeurs) -> ConfigModele:
    donnees = {
        "depot_hf": "org/modele-GGUF",
        "revision": REV,
        "fichiers": [],
        "gguf": {"depot": "org/modele-GGUF", "fichier": "m-q8_0.gguf", "sha256": outils.sha(GGUF)},
        "contexte": 512,
        "protocole_outils": "natif",
        "embedding": True,
        "pooling": "cls",
    }
    donnees.update(valeurs)
    return ConfigModele.model_validate(donnees)


def _servir_lfs(banc, outils, url: str, contenu: bytes, commit: str | None = None) -> None:
    en_tetes = {
        "Location": "https://cas-bridge.xethub.hf.co/objet",
        "X-Linked-Size": str(len(contenu)),
        "X-Linked-Etag": f'"{outils.sha(contenu)}"',
    }
    if commit:
        en_tetes["X-Repo-Commit"] = commit
    banc.serveur.servir(url, contenu, statut_head=302, en_tetes_head=en_tetes)


def test_gguf_nominal(banc, outils, tmp_path: Path) -> None:
    url = _url("org/modele-GGUF", REV, "m-q8_0.gguf")
    _servir_lfs(banc, outils, url, GGUF, REV)
    lignes = []
    modeles.executer(
        banc.telechargeur(), [("emb", _config(outils))], tmp_path, consigner=lignes.append
    )
    assert (tmp_path / "emb" / "gguf" / "m-q8_0.gguf").read_bytes() == GGUF
    assert [r.method for r in banc.serveur.requetes] == ["HEAD", "GET"]
    (ligne,) = lignes
    assert ligne["modele"] == "emb" and ligne["genre"] == "gguf"
    assert ligne["depot"] == "org/modele-GGUF" and ligne["revision"] == REV
    assert ligne["sha256"] == outils.sha(GGUF) and ligne["octets"] == len(GGUF)


def test_gguf_present_sans_requete(banc, outils, tmp_path: Path) -> None:
    destination = tmp_path / "emb" / "gguf" / "m-q8_0.gguf"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(GGUF)
    lignes = []
    modeles.executer(
        banc.telechargeur(), [("emb", _config(outils))], tmp_path, consigner=lignes.append
    )
    assert banc.serveur.requetes == []
    assert lignes[0]["statut"] == "deja-present"


def test_etag_different_de_la_config(banc, outils, tmp_path: Path) -> None:
    url = _url("org/modele-GGUF", REV, "m-q8_0.gguf")
    _servir_lfs(banc, outils, url, b"autre GGUF")
    with pytest.raises(ShaInvalide, match="X-Linked-Etag"):
        modeles.executer(banc.telechargeur(), [("emb", _config(outils))], tmp_path)
    assert [r.method for r in banc.serveur.requetes] == ["HEAD"]
    assert not (tmp_path / "emb").exists()


def test_gguf_d_un_autre_depot(banc, outils, tmp_path: Path) -> None:
    config = _config(
        outils,
        depot_hf="org/base",
        gguf={"depot": "tiers/base-GGUF", "fichier": "q/b.gguf", "sha256": outils.sha(GGUF)},
    )
    _servir_lfs(banc, outils, _url("tiers/base-GGUF", "main", "q/b.gguf"), GGUF, COMMIT_MAIN)
    banc.serveur.servir(_url("tiers/base-GGUF", COMMIT_MAIN, "q/b.gguf"), GGUF)
    lignes = []
    modeles.executer(banc.telechargeur(), [("base", config)], tmp_path, consigner=lignes.append)
    assert (tmp_path / "base" / "gguf" / "b.gguf").read_bytes() == GGUF
    assert lignes[0]["revision"] == COMMIT_MAIN
    get = banc.serveur.requetes_vers("/resolve/", "GET")
    assert [str(r.url) for r in get] == [_url("tiers/base-GGUF", COMMIT_MAIN, "q/b.gguf")]


def test_gguf_d_un_autre_depot_sans_commit(banc, outils, tmp_path: Path) -> None:
    config = _config(
        outils,
        depot_hf="org/base",
        gguf={"depot": "tiers/base-GGUF", "fichier": "b.gguf", "sha256": outils.sha(GGUF)},
    )
    _servir_lfs(banc, outils, _url("tiers/base-GGUF", "main", "b.gguf"), GGUF)
    with pytest.raises(TelechargementEchoue, match="X-Repo-Commit"):
        modeles.executer(banc.telechargeur(), [("base", config)], tmp_path)


def test_fichiers_hf(banc, outils, tmp_path: Path) -> None:
    config = _config(outils, fichiers=["model.safetensors", "sous/poids.bin"])
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF)
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "model.safetensors"), POIDS)
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "sous/poids.bin"), b"bin")
    lignes = []
    modeles.executer(banc.telechargeur(), [("emb", config)], tmp_path, consigner=lignes.append)
    assert (tmp_path / "emb" / "hf" / "model.safetensors").read_bytes() == POIDS
    assert (tmp_path / "emb" / "hf" / "sous" / "poids.bin").read_bytes() == b"bin"
    assert [ligne["genre"] for ligne in lignes] == ["gguf", "hf", "hf"]
    assert {ligne["revision"] for ligne in lignes} == {REV}


def test_fichier_hf_sans_sha(banc, outils, tmp_path: Path) -> None:
    config = _config(outils, fichiers=["config.json"])
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF)
    banc.serveur.servir(
        _url("org/modele-GGUF", REV, "config.json"), b"{}", en_tetes_head={"Content-Length": "2"}
    )
    with pytest.raises(ShaInvalide, match="aucun SHA-256 attendu"):
        modeles.executer(banc.telechargeur(), [("emb", config)], tmp_path)
    assert banc.serveur.requetes_vers("/resolve/", "GET") == []


def test_chemin_hostile_refuse(banc, outils, tmp_path: Path) -> None:
    config = _config(outils, fichiers=["../evasion.bin"])
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF)
    with pytest.raises(ConfigurationInvalide, match="chemin de dépôt invalide"):
        modeles.executer(banc.telechargeur(), [("emb", config)], tmp_path)


def test_espace_insuffisant_avant_telechargement(banc, outils, tmp_path: Path) -> None:
    from slmsp.core.artefacts import EspaceInsuffisant

    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF, REV)
    telechargeur = banc.telechargeur(outils.reglages(marge_espace=10**18))
    with pytest.raises(EspaceInsuffisant):
        modeles.executer(telechargeur, [("emb", _config(outils))], tmp_path)
    assert [r.method for r in banc.serveur.requetes] == ["HEAD"]
    assert not (tmp_path / "emb").exists()


def test_slug_invalide() -> None:
    for slug in ("../bge-m3", "BGE", "a/b", ".."):
        with pytest.raises(ConfigurationInvalide, match="slug"):
            charger_config_modele(slug)


# --- CLI ----------------------------------------------------------------------------------

MODELE_TOML = """
schema_version = 1
depot_hf = "org/modele-GGUF"
revision = "{rev}"
fichiers = []
contexte = 512
embedding = true
pooling = "cls"
protocole_outils = "natif"

[gguf]
depot = "org/modele-GGUF"
fichier = "m-q8_0.gguf"
sha256 = "{sha}"
"""


def test_cli_modeles_de_bout_en_bout(banc, outils, cli) -> None:
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF, REV)
    (cli.config / "modeles" / "emb-test.toml").write_text(
        MODELE_TOML.format(rev=REV, sha=outils.sha(GGUF)), encoding="utf-8"
    )
    assert main(["fetch", "modeles", "emb-test", "--racine", str(cli.racine)]) == 0
    assert dossier_modeles() == cli.models
    destination = cli.models / "emb-test" / "gguf" / "m-q8_0.gguf"
    assert outils.sha(destination.read_bytes()) == outils.sha(GGUF)
    run = outils.lire_run(cli.racine)
    assert run.manifeste["config"]["slugs"] == ["emb-test"]
    assert "config/modeles/emb-test.toml" in run.manifeste["entrees"]
    (ligne,) = run.fichiers
    assert (ligne["depot"], ligne["fichier"], ligne["revision"]) == (
        "org/modele-GGUF",
        "m-q8_0.gguf",
        REV,
    )
    assert ligne["statut"] == "telecharge" and ligne["octets"] == len(GGUF)
    assert run.statuts == ["en_cours", "complet"]
    assert len(banc.journal.lister()) == len(banc.serveur.requetes) == 2  # HEAD, GET
    assert all(e.profil == "outillage" for e in banc.journal.lister())

    # Relance : rien n'est retéléchargé, aucune requête.
    banc.serveur.requetes.clear()
    assert main(["fetch", "modeles", "emb-test", "--racine", str(cli.racine)]) == 0
    assert banc.serveur.requetes == []


def test_cli_modele_inconnu(cli, capsys) -> None:
    assert main(["fetch", "modeles", "absent", "--racine", str(cli.racine)]) == 1
    assert "absent.toml" in capsys.readouterr().err
    assert not (cli.racine / "runs").exists()


# --- Configuration versionnée ----------------------------------------------------------


def test_config_bge_m3() -> None:
    config = charger_config_modele("bge-m3")
    assert config.depot_hf == config.gguf.depot == "ggml-org/bge-m3-Q8_0-GGUF"
    assert config.revision == "9eba04c5d75ba5a1595e45de734d36bef4e5cb98"
    assert config.gguf.fichier == "bge-m3-q8_0.gguf"
    assert config.gguf.sha256.startswith("aa473d51")
    assert (config.embedding, config.pooling, config.contexte, config.fichiers) == (
        True,
        "cls",
        8192,
        [],
    )


@pytest.mark.reseau
def test_bge_m3_reel_conforme() -> None:
    """Réseau : taille et `X-Linked-Etag` du GGUF publié = config (HEAD seulement)."""
    from slmsp.fetch.config import charger_config_fetch
    from slmsp.fetch.hf import Telechargeur, client_hf, jeton_hf, url_hf

    config = charger_config_modele("bge-m3")
    with client_hf(jeton_hf()) as client:
        meta = Telechargeur(client, charger_config_fetch()).metadonnees_hf(
            url_hf(config.gguf.depot, config.gguf.fichier, config.revision)
        )
    assert (meta.taille, meta.sha256) == (634_553_760, config.gguf.sha256)
    assert meta.commit == config.revision
