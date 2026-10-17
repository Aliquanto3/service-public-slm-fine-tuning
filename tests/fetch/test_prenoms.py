"""Pilote `slmsp fetch prenoms` : archive factice, aucune requête réelle."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.prenoms_insee import OCCURRENCES_MINIMALES, prenoms_depuis_csv_insee
from slmsp.fetch import prenoms
from slmsp.fetch.hf import ArchiveInvalide, ShaInvalide

URL = "https://www.insee.fr/fr/statistiques/fichier/7633685/nat2022_csv.zip"
CSV = (
    "sexe;preusuel;annais;nombre\n"
    "1;_PRENOMS_RARES;1900;500\n"
    "1;PRENOM-FACTICE-A;2000;15\n"
    "2;PRENOM-FACTICE-A;2001;10\n"
    "1;AB;2000;900\n"
    "1;PRENOM-FACTICE-B;2000;5\n"
)


def _config(outils, contenu: bytes) -> prenoms.ConfigPrenoms:
    return prenoms.ConfigPrenoms(
        url=URL,
        sha256=outils.sha(contenu),
        taille=len(contenu),
        membre="fictif.csv",
        licence="etalab-2.0",
    )


def test_generation_avec_regles(banc, outils, tmp_path: Path) -> None:
    archive = outils.ecrire_zip(tmp_path / "ref.zip", {"fictif.csv": CSV.encode()})
    banc.serveur.servir(URL, archive)
    sortie = tmp_path / "prenoms.txt"
    lignes: list[dict] = []
    _, nombre = prenoms.executer(
        banc.telechargeur(),
        _config(outils, archive),
        tmp_path / "racine",
        sortie=sortie,
        extraire=prenoms_depuis_csv_insee,
        minimum=OCCURRENCES_MINIMALES,
        consigner=lignes.append,
    )
    texte = sortie.read_text(encoding="utf-8")
    assert nombre == 1
    assert texte.splitlines()[-1] == "prenom-factice-a"  # 25 naissances cumulées
    assert "ab" not in texte.splitlines() and "prenom-factice-b" not in texte
    assert texte.startswith("# ") and "Licence Ouverte 2.0" in texte
    assert lignes[0]["prenoms"] == 1 and lignes[0]["statut"] == "telecharge"
    assert {r.url.host for r in banc.serveur.requetes} == {"www.insee.fr"}
    assert {r.method for r in banc.serveur.requetes} == {"GET"}


def test_sha_different_refuse(banc, outils, tmp_path: Path) -> None:
    archive = outils.ecrire_zip(tmp_path / "ref.zip", {"fictif.csv": CSV.encode()})
    banc.serveur.servir(URL, archive + b"x")
    sortie = tmp_path / "prenoms.txt"
    with pytest.raises(ShaInvalide):
        prenoms.executer(
            banc.telechargeur(),
            _config(outils, archive),
            tmp_path / "racine",
            sortie=sortie,
            extraire=prenoms_depuis_csv_insee,
            minimum=OCCURRENCES_MINIMALES,
        )
    assert not sortie.exists()


def test_config_reelle_epinglee() -> None:
    config = prenoms.charger_config_prenoms()
    assert config.url.startswith("https://www.insee.fr/") and config.licence == "etalab-2.0"
    assert len(config.sha256) == 64 and config.taille > 0


def test_membre_trop_gros_refuse(outils, tmp_path: Path) -> None:
    archive = outils.ecrire_zip(tmp_path / "gros.zip", {"fictif.csv": b"a;b\n" * 1000})
    chemin = tmp_path / "gros.zip"
    assert archive and len(prenoms.lignes_csv(chemin, "fictif.csv", limite=4000)) == 1000
    with pytest.raises(ArchiveInvalide, match="dépasse"):
        prenoms.lignes_csv(chemin, "fictif.csv", limite=3999)


def test_taille_annoncee_mensongere_plafonnee(outils, tmp_path: Path, monkeypatch) -> None:
    outils.ecrire_zip(tmp_path / "gros.zip", {"fictif.csv": b"a;b\n" * 1000})
    # file_size falsifié à la baisse : refus quand même (zipfile ou plafond du flux).
    original = zipfile.ZipFile.getinfo

    def getinfo(self, nom):
        info = original(self, nom)
        info.file_size = 10
        return info

    monkeypatch.setattr(zipfile.ZipFile, "getinfo", getinfo)
    with pytest.raises(ArchiveInvalide):
        prenoms.lignes_csv(tmp_path / "gros.zip", "fictif.csv", limite=100)


def test_cli_prenoms_de_bout_en_bout(banc, outils, cli, tmp_path: Path, monkeypatch) -> None:
    archive = outils.ecrire_zip(tmp_path / "ref.zip", {"fictif.csv": CSV.encode()})
    banc.serveur.servir(URL, archive)
    monkeypatch.setattr(prenoms, "charger_config_prenoms", lambda: _config(outils, archive))
    (cli.config / "outillage.toml").write_text("# fictif", encoding="utf-8")
    sortie = tmp_path / "sortie" / "prenoms.txt"
    code = main(["fetch", "prenoms", "--racine", str(cli.racine), "--sortie", str(sortie)])
    assert code == 0
    assert sortie.read_text(encoding="utf-8").splitlines()[-1] == "prenom-factice-a"
    run = outils.lire_run(cli.racine)
    assert run.statuts == ["en_cours", "complet"]
    assert run.fichiers[0]["prenoms"] == 1
    assert {r.url.host for r in banc.serveur.requetes} == {"www.insee.fr"}
