"""Pilote des modèles (`config/modeles/<slug>.toml`) et `slmsp fetch modeles`."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

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


GGUF_F16 = b"GGUF f16 factice " * 40


def test_gguf_f16_telecharge_seulement_avec_l_option(banc, outils, tmp_path: Path) -> None:
    config = _config(
        outils,
        gguf_f16={
            "depot": "org/modele-GGUF",
            "fichier": "m-f16.gguf",
            "sha256": outils.sha(GGUF_F16),
            "precision": "f16",
        },
    )
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF, REV)
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-f16.gguf"), GGUF_F16, REV)
    modeles.executer(banc.telechargeur(), [("base", config)], tmp_path)
    assert not (tmp_path / "base" / "gguf" / "m-f16.gguf").exists()
    lignes = []
    modeles.executer(
        banc.telechargeur(), [("base", config)], tmp_path, f16=True, consigner=lignes.append
    )
    assert (tmp_path / "base" / "gguf" / "m-f16.gguf").read_bytes() == GGUF_F16
    assert [ligne["fichier"] for ligne in lignes] == ["m-q8_0.gguf", "m-f16.gguf"]


def test_gguf_f16_sha_different_de_la_config(banc, outils, tmp_path: Path) -> None:
    config = _config(
        outils,
        gguf_f16={
            "depot": "org/modele-GGUF",
            "fichier": "m-f16.gguf",
            "sha256": "0" * 64,
            "precision": "f16",
        },
    )
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF, REV)
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-f16.gguf"), GGUF_F16, REV)
    with pytest.raises(ShaInvalide):
        modeles.executer(banc.telechargeur(), [("base", config)], tmp_path, f16=True)


@pytest.mark.parametrize(
    ("slug", "precision"),
    [
        ("granite-4.0-1b", "bf16"),
        ("ministral-3-3b", "bf16"),
        ("qwen-4b", "f16"),
        ("smollm3-3b", "f16"),
    ],
)
def test_configs_reelles_declarent_un_gguf_f16_epingle(slug: str, precision: str) -> None:
    config = charger_config_modele(slug)
    assert config.gguf_f16 is not None
    assert config.gguf_f16.revision is not None and config.gguf_f16.source is not None
    # Précision relevée sur Hugging Face (nom du fichier publié), pas recalculée.
    assert config.gguf_f16.precision == precision
    assert precision in config.gguf_f16.fichier.lower()
    assert config.precision_gguf("f16") == precision


def test_gguf_f16_precision_obligatoire(outils) -> None:
    with pytest.raises(ValidationError, match="precision"):
        _config(outils, gguf_f16={"depot": "o/d", "fichier": "m-f16.gguf", "sha256": "0" * 64})


def test_gguf_f16_revision_differente_du_meme_depot(outils) -> None:
    with pytest.raises(ValidationError, match="gguf_f16.revision"):
        _config(
            outils,
            gguf_f16={
                "depot": "org/modele-GGUF",
                "fichier": "m-f16.gguf",
                "sha256": "0" * 64,
                "revision": "b" * 40,
                "precision": "bf16",
            },
        )


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


def test_gguf_revision_epinglee_sans_resolution_de_main(banc, outils, tmp_path: Path) -> None:
    epinglee = "e" * 40
    config = _config(
        outils,
        depot_hf="org/base",
        gguf={
            "depot": "tiers/base-GGUF",
            "fichier": "b.gguf",
            "sha256": outils.sha(GGUF),
            "revision": epinglee,
            "source": "communautaire",
        },
    )
    _servir_lfs(banc, outils, _url("tiers/base-GGUF", epinglee, "b.gguf"), GGUF)  # sans commit
    lignes = []
    modeles.executer(banc.telechargeur(), [("base", config)], tmp_path, consigner=lignes.append)
    assert (tmp_path / "base" / "gguf" / "b.gguf").read_bytes() == GGUF
    assert lignes[0]["revision"] == epinglee
    assert banc.serveur.requetes_vers("/resolve/main/") == []
    assert {str(r.url) for r in banc.serveur.requetes} == {
        _url("tiers/base-GGUF", epinglee, "b.gguf")
    }


def test_fichier_non_lfs_avec_sha_de_la_config(banc, outils, tmp_path: Path) -> None:
    config = _config(
        outils, fichiers=["config.json"], sha256_fichiers={"config.json": outils.sha(b"{}")}
    )
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF)
    banc.serveur.servir(
        _url("org/modele-GGUF", REV, "config.json"), b"{}", en_tetes_head={"Content-Length": "2"}
    )
    lignes = []
    modeles.executer(banc.telechargeur(), [("emb", config)], tmp_path, consigner=lignes.append)
    assert (tmp_path / "emb" / "hf" / "config.json").read_bytes() == b"{}"
    assert lignes[1]["sha256"] == outils.sha(b"{}") and lignes[1]["statut"] == "telecharge"


def test_fichier_hf_present_sans_requete(banc, outils, tmp_path: Path) -> None:
    config = _config(
        outils,
        fichiers=["sous/config.json"],
        sha256_fichiers={"sous/config.json": outils.sha(b"{}")},
    )
    (tmp_path / "emb" / "gguf").mkdir(parents=True)
    (tmp_path / "emb" / "gguf" / "m-q8_0.gguf").write_bytes(GGUF)
    (tmp_path / "emb" / "hf" / "sous").mkdir(parents=True)
    (tmp_path / "emb" / "hf" / "sous" / "config.json").write_bytes(b"{}")
    lignes = []
    modeles.executer(banc.telechargeur(), [("emb", config)], tmp_path, consigner=lignes.append)
    assert banc.serveur.requetes == []
    assert [ligne["statut"] for ligne in lignes] == ["deja-present", "deja-present"]


def test_fichier_hf_present_mais_altere(banc, outils, tmp_path: Path) -> None:
    config = _config(
        outils, fichiers=["config.json"], sha256_fichiers={"config.json": outils.sha(b"{}")}
    )
    (tmp_path / "emb" / "gguf").mkdir(parents=True)
    (tmp_path / "emb" / "gguf" / "m-q8_0.gguf").write_bytes(GGUF)
    (tmp_path / "emb" / "hf").mkdir(parents=True)
    (tmp_path / "emb" / "hf" / "config.json").write_bytes(b"{ }")
    with pytest.raises(ShaInvalide, match="rien n'est écrit"):
        modeles.executer(banc.telechargeur(), [("emb", config)], tmp_path)
    assert banc.serveur.requetes == []
    assert (tmp_path / "emb" / "hf" / "config.json").read_bytes() == b"{ }"


def test_etag_hf_different_du_sha_de_la_config(banc, outils, tmp_path: Path) -> None:
    config = _config(
        outils,
        fichiers=["model.safetensors"],
        sha256_fichiers={"model.safetensors": outils.sha(b"attendu")},
    )
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF)
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "model.safetensors"), POIDS)
    with pytest.raises(ShaInvalide, match="X-Linked-Etag .* différent du SHA-256 de la config"):
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


def test_cli_modeles_f16(banc, outils, cli, capsys) -> None:
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-q8_0.gguf"), GGUF, REV)
    _servir_lfs(banc, outils, _url("org/modele-GGUF", REV, "m-bf16.gguf"), GGUF_F16, REV)
    toml = MODELE_TOML.format(rev=REV, sha=outils.sha(GGUF))
    (cli.config / "modeles" / "sans-f16.toml").write_text(toml, encoding="utf-8")
    (cli.config / "modeles" / "avec-f16.toml").write_text(
        toml
        + '\n[gguf_f16]\ndepot = "org/modele-GGUF"\nfichier = "m-bf16.gguf"\n'
        + f'sha256 = "{outils.sha(GGUF_F16)}"\nprecision = "bf16"\n',
        encoding="utf-8",
    )
    racine = ["--racine", str(cli.racine)]
    assert main(["fetch", "modeles", "avec-f16", "sans-f16", "--f16", *racine]) == 0
    assert (cli.models / "avec-f16" / "gguf" / "m-bf16.gguf").read_bytes() == GGUF_F16
    assert not (cli.models / "sans-f16" / "gguf" / "m-bf16.gguf").exists()
    assert "sans-f16 : pas de section gguf_f16" in capsys.readouterr().err
    assert outils.lire_run(cli.racine).manifeste["config"]["f16"] is True


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
