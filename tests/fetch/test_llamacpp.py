"""Pilote llama.cpp : release GitHub, archives vérifiées, extraction sans écrasement."""

from __future__ import annotations

import stat
import subprocess
import zipfile
from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.artefacts import EspaceInsuffisant
from slmsp.core.schemas.config_llamacpp import ConfigLlamacpp
from slmsp.fetch import llamacpp
from slmsp.fetch.config import charger_config_llamacpp
from slmsp.fetch.hf import ArchiveInvalide, ShaInvalide, TelechargementEchoue

DEPOT = "org/llama.cpp"
TAG = "b1"
URL_API = f"https://api.github.com/repos/{DEPOT}/releases/tags/{TAG}"
URL_SOURCES = f"https://github.com/{DEPOT}/archive/refs/tags/{TAG}.zip"

MEMBRES = {
    "cpu": {"llama-server.exe": b"serveur cpu", "ggml-cpu.dll": b"cpu" * 50},
    "cuda": {"llama-server.exe": b"serveur cuda", "ggml-cuda.dll": b"cuda" * 50},
    "cudart": {"cudart64_12.dll": b"cudart" * 40},
    "sources": {
        "llama.cpp-b1/": b"",
        "llama.cpp-b1/README.md": b"lisez-moi",
        "llama.cpp-b1/gguf-py/gguf/__init__.py": b"# gguf",
    },
}
NOMS = {
    "cpu": "llama-b1-bin-win-cpu-x64.zip",
    "cuda": "llama-b1-bin-win-cuda-12.4-x64.zip",
    "cudart": "cudart-llama-bin-win-cuda-12.4-x64.zip",
    "sources": "llama.cpp-b1-sources.zip",
}


@pytest.fixture
def release(banc, outils, tmp_path: Path):
    """Archives générées, servies par une release factice ; renvoie (config, octets)."""
    octets = {
        cle: outils.ecrire_zip(tmp_path / "zips" / NOMS[cle], membres)
        for cle, membres in MEMBRES.items()
    }
    assets = []
    for cle in ("cpu", "cuda", "cudart"):
        telechargement = f"https://github.com/{DEPOT}/releases/download/{TAG}/{NOMS[cle]}"
        cdn = f"https://release-assets.githubusercontent.com/{NOMS[cle]}"
        banc.serveur.servir(telechargement, redirection=cdn)
        banc.serveur.servir(cdn, octets[cle])
        assets.append(
            {
                "name": NOMS[cle],
                "size": len(octets[cle]),
                "digest": f"sha256:{outils.sha(octets[cle])}",
                "browser_download_url": telechargement,
            }
        )
    banc.serveur.servir(URL_API, json={"tag_name": TAG, "assets": assets})
    codeload = f"https://codeload.github.com/{DEPOT}/zip/refs/tags/{TAG}"
    banc.serveur.servir(URL_SOURCES, redirection=codeload)
    banc.serveur.servir(codeload, octets["sources"])
    config = ConfigLlamacpp.model_validate(
        {
            "tag": TAG,
            "depot": DEPOT,
            "assets": {
                cle: {"nom": NOMS[cle], "sha256": outils.sha(octets[cle])}
                for cle in ("cpu", "cuda", "cudart")
            },
            "sources": {"nom": NOMS["sources"], "sha256": outils.sha(octets["sources"])},
        }
    )
    return config, octets


@pytest.fixture
def sans_sous_processus(monkeypatch: pytest.MonkeyPatch) -> None:
    def interdit(*_args, **_kwargs):
        raise AssertionError("fetch ne lance aucun sous-processus")

    monkeypatch.setattr(subprocess, "Popen", interdit)


def test_installation_complete(banc, release, tmp_path: Path, sans_sous_processus) -> None:
    config, octets = release
    lignes, extractions = [], []
    racine = tmp_path / "racine"
    resultats = llamacpp.executer(
        banc.telechargeur(),
        config,
        racine,
        consigner=lignes.append,
        consigner_extraction=extractions.append,
    )
    base = racine / "vendor" / "llama.cpp" / TAG
    assert (base / "bin-cpu" / "llama-server.exe").read_bytes() == b"serveur cpu"
    assert (base / "bin-cuda" / "llama-server.exe").read_bytes() == b"serveur cuda"
    assert (base / "bin-cuda" / "cudart64_12.dll").exists()
    assert (base / "src" / "README.md").read_bytes() == b"lisez-moi"
    assert (base / "src" / "gguf-py" / "gguf" / "__init__.py").exists()
    assert not (base / "src" / "llama.cpp-b1").exists()
    assert {r.statut for r in resultats} == {"telecharge"}
    assert [ligne["fichier"] for ligne in lignes] == [NOMS[c] for c in NOMS]
    for ligne in lignes:
        assert ligne["revision"] == TAG and ligne["depot"] == DEPOT
        assert ligne["octets"] == ligne["taille"] > 0
    assert [e["statut"] for e in extractions] == ["extrait"] * 4
    for nom in NOMS.values():
        assert (base / "archives" / f"{nom}.extrait.json").exists()
    hotes = {e.hote for e in banc.journal.lister()}
    assert hotes == {
        "api.github.com",
        "github.com",
        "release-assets.githubusercontent.com",
        "codeload.github.com",
    }
    assert {e.profil for e in banc.journal.lister()} == {"outillage"}
    assert all(
        "Authorization" not in r.headers for r in banc.serveur.requetes
    )  # aucun jeton vers GitHub


def test_relance_idempotente(banc, release, tmp_path: Path) -> None:
    config, _ = release
    racine = tmp_path / "racine"
    llamacpp.executer(banc.telechargeur(), config, racine)
    banc.serveur.requetes.clear()
    lignes, extractions = [], []
    llamacpp.executer(
        banc.telechargeur(),
        config,
        racine,
        consigner=lignes.append,
        consigner_extraction=extractions.append,
    )
    assert banc.serveur.requetes == []
    assert {ligne["statut"] for ligne in lignes} == {"deja-present"}
    assert {e["statut"] for e in extractions} == {"deja-extrait"}


def test_extraction_reprise_sans_marqueur(banc, release, tmp_path: Path) -> None:
    config, _ = release
    racine = tmp_path / "racine"
    llamacpp.executer(banc.telechargeur(), config, racine)
    archives = racine / "vendor" / "llama.cpp" / TAG / "archives"
    marqueur = archives / f"{NOMS['cpu']}.extrait.json"
    marqueur.rename(archives / "ancien-marqueur.json")  # extraction interrompue simulée
    extractions = []
    llamacpp.executer(banc.telechargeur(), config, racine, consigner_extraction=extractions.append)
    assert extractions[0]["statut"] == "extrait"
    assert extractions[0]["ecrits"] == 0 and extractions[0]["deja_presents"] == 2


def test_digest_different_de_la_config(banc, release, tmp_path: Path) -> None:
    config, _ = release
    autre = config.model_copy(
        update={
            "assets": {
                **config.assets,
                "cpu": config.assets["cpu"].model_copy(update={"sha256": "0" * 64}),
            }
        }
    )
    with pytest.raises(ShaInvalide, match="digest publié"):
        llamacpp.executer(banc.telechargeur(), autre, tmp_path / "racine")
    assert [r.url.host for r in banc.serveur.requetes] == ["api.github.com"]


def test_asset_absent_de_la_release(banc, release, tmp_path: Path) -> None:
    config, _ = release
    banc.serveur.fichiers[URL_API].json = {"assets": []}
    with pytest.raises(TelechargementEchoue, match="absent de la release"):
        llamacpp.executer(banc.telechargeur(), config, tmp_path / "racine")


def test_binaires_verifies(banc, outils, release, tmp_path: Path) -> None:
    config, _ = release
    bon = config.model_copy(
        update={"binaires": {"bin-cpu/llama-server.exe": outils.sha(b"serveur cpu")}}
    )
    extractions = []
    llamacpp.executer(
        banc.telechargeur(), bon, tmp_path / "a", consigner_extraction=extractions.append
    )
    assert extractions[-1]["binaires_verifies"] == 1
    faux = config.model_copy(update={"binaires": {"bin-cpu/llama-server.exe": "1" * 64}})
    with pytest.raises(ShaInvalide, match="llama-server.exe"):
        llamacpp.executer(banc.telechargeur(), faux, tmp_path / "b")


def test_archive_au_mauvais_sha(banc, release, tmp_path: Path) -> None:
    config, _ = release
    faux = config.model_copy(
        update={"sources": config.sources.model_copy(update={"sha256": "2" * 64})}
    )
    racine = tmp_path / "racine"
    with pytest.raises(ShaInvalide):
        llamacpp.executer(banc.telechargeur(), faux, racine)
    archives = racine / "vendor" / "llama.cpp" / TAG / "archives"
    assert not (archives / NOMS["sources"]).exists()
    assert list(archives.glob(f"{NOMS['sources']}.sha-invalide-*"))
    assert not (racine / "vendor" / "llama.cpp" / TAG / "bin-cpu").exists()


# --- Extraction ----------------------------------------------------------------------------


def _zip_brut(chemin: Path, nom: str, contenu: bytes = b"x", mode: int | None = None) -> Path:
    with zipfile.ZipFile(chemin, "w") as zf:
        info = zipfile.ZipInfo(nom)
        if mode is not None:
            info.external_attr = mode << 16
        zf.writestr(info, contenu)
    return chemin


@pytest.mark.parametrize(
    "nom",
    ["../evil.txt", "a/../../evil.txt", "/absolu.txt", "C:/windows.txt", "\\\\serveur\\x"],
)
def test_zip_hostile(outils, tmp_path: Path, nom: str) -> None:
    archive = _zip_brut(tmp_path / "hostile.zip", nom)
    cible = tmp_path / "cible"
    with pytest.raises(ArchiveInvalide):
        llamacpp.extraire(archive, cible, outils.reglages(), sha256="0" * 64)
    assert not cible.exists()
    assert not (tmp_path / "evil.txt").exists()


def test_zip_avec_lien_symbolique(outils, tmp_path: Path) -> None:
    archive = _zip_brut(tmp_path / "lien.zip", "lien", b"/etc/passwd", stat.S_IFLNK | 0o777)
    with pytest.raises(ArchiveInvalide, match="lien"):
        llamacpp.extraire(archive, tmp_path / "cible", outils.reglages(), sha256="0" * 64)


def test_sources_sans_racine_unique(outils, tmp_path: Path) -> None:
    archive = tmp_path / "s.zip"
    outils.ecrire_zip(archive, {"a/x": b"1", "b/y": b"2"})
    with pytest.raises(ArchiveInvalide, match="racine unique"):
        llamacpp.extraire(
            archive, tmp_path / "cible", outils.reglages(), sha256="0" * 64, retirer_racine=True
        )


def test_extraction_sans_ecraser(outils, tmp_path: Path) -> None:
    archive = tmp_path / "a.zip"
    outils.ecrire_zip(archive, {"x.dll": b"nouveau", "y.dll": b"y"})
    cible = tmp_path / "cible"
    cible.mkdir()
    (cible / "x.dll").write_bytes(b"ancien")
    with pytest.raises(ArchiveInvalide, match="rien n'est écrasé"):
        llamacpp.extraire(archive, cible, outils.reglages(), sha256="0" * 64)
    assert (cible / "x.dll").read_bytes() == b"ancien"
    assert not llamacpp.chemin_marqueur(archive).exists()


def test_extraction_espace_verifie(outils, tmp_path: Path) -> None:
    archive = tmp_path / "a.zip"
    outils.ecrire_zip(archive, {"x.dll": b"x"})
    with pytest.raises(EspaceInsuffisant):
        llamacpp.extraire(
            archive, tmp_path / "cible", outils.reglages(marge_espace=10**18), sha256="0" * 64
        )
    assert not (tmp_path / "cible").exists()


def test_zip_illisible(outils, tmp_path: Path) -> None:
    archive = tmp_path / "a.zip"
    archive.write_bytes(b"pas un zip")
    with pytest.raises(ArchiveInvalide, match="illisible"):
        llamacpp.extraire(archive, tmp_path / "cible", outils.reglages(), sha256="0" * 64)


@pytest.mark.parametrize("nom", ["x.dll.", "x.dll ", "dossier./x.dll"])
def test_zip_nom_ambigu_sous_windows(outils, tmp_path: Path, nom: str) -> None:
    archive = _zip_brut(tmp_path / "ambigu.zip", nom)
    cible = tmp_path / "cible"
    with pytest.raises(ArchiveInvalide, match="ambigu"):
        llamacpp.extraire(archive, cible, outils.reglages(), sha256="0" * 64)
    assert not cible.exists()


def test_zip_doublon_de_casse(outils, tmp_path: Path) -> None:
    archive = tmp_path / "casse.zip"
    outils.ecrire_zip(archive, {"A.dll": b"1", "a.dll": b"2"})
    cible = tmp_path / "cible"
    with pytest.raises(ArchiveInvalide, match="doublon"):
        llamacpp.extraire(archive, cible, outils.reglages(), sha256="0" * 64)
    assert not cible.exists()


def test_espace_insuffisant_avant_telechargement(banc, outils, release, tmp_path: Path) -> None:
    config, octets = release
    archives = sum(len(octets[cle]) for cle in ("cpu", "cuda", "cudart"))
    # Les archives seules restent sous le seuil : seule l'extraction estimée le dépasse.
    reglages = outils.reglages(seuil_verification_espace=archives, marge_espace=10**18)
    with pytest.raises(EspaceInsuffisant):
        llamacpp.executer(banc.telechargeur(reglages), config, tmp_path / "racine")
    assert [r.url.host for r in banc.serveur.requetes] == ["api.github.com"]
    assert not (tmp_path / "racine" / "vendor" / "llama.cpp" / TAG / "archives").exists()


# --- CLI ----------------------------------------------------------------------------------


def test_cli_llamacpp_de_bout_en_bout(banc, outils, release, cli, sans_sous_processus) -> None:
    config, _ = release
    lignes = [f'schema_version = 1\ntag = "{TAG}"\ndepot = "{DEPOT}"\n']
    for cle, asset in config.assets.items():
        lignes.append(f'[assets.{cle}]\nnom = "{asset.nom}"\nsha256 = "{asset.sha256}"\n')
    lignes.append(f'[sources]\nnom = "{config.sources.nom}"\nsha256 = "{config.sources.sha256}"\n')
    (cli.config / "llamacpp.toml").write_text("\n".join(lignes), encoding="utf-8")
    assert main(["fetch", "llamacpp", "--racine", str(cli.racine)]) == 0
    base = cli.racine / "vendor" / "llama.cpp" / TAG
    for dossier in ("bin-cpu", "bin-cuda", "src"):
        assert (base / dossier).is_dir()
    run = outils.lire_run(cli.racine)
    assert run.statuts == ["en_cours", "complet"]
    assert [ligne["fichier"] for ligne in run.fichiers] == list(NOMS.values())
    assert all(ligne["revision"] == TAG and ligne["sha256"] for ligne in run.fichiers)
    assert len(run.extractions) == 4
    assert len(banc.journal.lister()) == len(banc.serveur.requetes) == 9  # API + 3 × 2 + 2
    assert all("Authorization" not in r.headers for r in banc.serveur.requetes)


# --- Configuration versionnée ----------------------------------------------------------


def test_config_versionnee() -> None:
    config = charger_config_llamacpp()
    assert config.tag == "b11429"
    assert config.depot == "ggml-org/llama.cpp"
    assert config.assets["cpu"].nom == "llama-b11429-bin-win-cpu-x64.zip"
    assert config.assets["cuda"].nom == "llama-b11429-bin-win-cuda-12.4-x64.zip"
    assert config.assets["cudart"].nom == "cudart-llama-bin-win-cuda-12.4-x64.zip"
    assert config.sources.sha256.startswith("2c140392")


@pytest.mark.reseau
def test_release_reelle_conforme(tmp_path: Path) -> None:
    """Réseau : la release publiée correspond à `config/llamacpp.toml` (aucun téléchargement)."""
    from slmsp import net
    from slmsp.fetch.config import charger_config_fetch
    from slmsp.fetch.hf import Telechargeur

    config = charger_config_llamacpp()
    with net.client("outillage", follow_redirects=True) as client:
        prevues = llamacpp.lire_release(Telechargeur(client, charger_config_fetch()), config)
    assert {p.nom for p in prevues} == {a.nom for a in config.assets.values()}
    assert all(p.taille for p in prevues)
