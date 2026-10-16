from __future__ import annotations

import socket
from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.canonique import sha256_fichier
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.items import N_DEFAUT, _empreintes_texte
from slmsp.publication.preparer import preparer

SLUG = "granite-4.0-1b"


def modifier_config(racine: Path, ancien: str, nouveau: str) -> None:
    chemin = racine / "config" / "publication.toml"
    texte = chemin.read_text(encoding="utf-8")
    assert ancien in texte
    chemin.write_text(texte.replace(ancien, nouveau), encoding="utf-8")


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch: pytest.MonkeyPatch) -> None:
    def interdit(*_a: object, **_k: object) -> None:
        raise AssertionError("connexion réseau interdite")

    monkeypatch.setattr(socket.socket, "connect", interdit)


def _preparer(racine: Path, export_id: str, comparatif: Path, tmp_path: Path, **kw):
    return preparer(
        racine=racine,
        modele=SLUG,
        export_run=export_id,
        comparatif=comparatif,
        sortie=tmp_path / "dossier",
        **kw,
    )


def test_dossier_complet(racine, export_id, comparatif, tmp_path) -> None:
    rapport = _preparer(racine, export_id, comparatif, tmp_path)
    assert rapport.publiable, rapport.bloquants
    d = rapport.dossier
    assert sorted(p.name for p in d.iterdir()) == [
        "COMPARATIF.md",
        "LICENSE",
        "README.md",
        "SHA256SUMS",
        "modele-q4_k_m.gguf",
    ]
    fiche = (d / "README.md").read_text(encoding="utf-8")
    assert "license: apache-2.0" in fiche
    assert sha256_fichier(d / "modele-q4_k_m.gguf") in fiche
    assert "etalab-2.0" in fiche  # Registre des licences
    assert len(rapport.emplacements) == 4
    assert "modele-q4_k_m.gguf" in (d / "SHA256SUMS").read_text(encoding="utf-8")


def test_licence_la_plus_permissive(racine, export_id, comparatif, tmp_path) -> None:
    modifier_config(
        racine, 'ordre_permissivite = ["apache-2.0"]', 'ordre_permissivite = ["mit", "apache-2.0"]'
    )
    modifier_config(
        racine,
        'licences_compatibles = ["apache-2.0"]',
        'licences_compatibles = ["apache-2.0", "mit"]',
    )
    (racine / "config" / "licences" / "mit.txt").write_text("<texte-factice>", encoding="utf-8")
    rapport = _preparer(racine, export_id, comparatif, tmp_path)
    assert rapport.licence == "mit"
    assert "license: mit" in (rapport.dossier / "README.md").read_text(encoding="utf-8")


def test_aucune_licence_compatible_echoue(racine, export_id, comparatif, tmp_path) -> None:
    modifier_config(
        racine, 'licences_compatibles = ["apache-2.0"]', 'licences_compatibles = ["gpl-3.0"]'
    )
    with pytest.raises(ConfigurationInvalide, match="aucune licence de sortie"):
        _preparer(racine, export_id, comparatif, tmp_path)


def test_licence_non_relue_echoue(racine, export_id, comparatif, tmp_path) -> None:
    modifier_config(racine, "verifie_le = 2026-10-17\n", "")
    with pytest.raises(ConfigurationInvalide, match="non relue"):
        _preparer(racine, export_id, comparatif, tmp_path)


def test_comparatif_certifie_refuse(racine, export_id, comparatif, tmp_path) -> None:
    comparatif.write_text("Modèle certifié ISO 42001.\n", encoding="utf-8")
    rapport = _preparer(racine, export_id, comparatif, tmp_path)
    assert not rapport.publiable
    assert rapport.dossier.name == "dossier.refuse"


def test_fuite_du_jeu_refusee(racine, export_id, comparatif, tmp_path) -> None:
    phrase = "<mot1> <mot2> <mot3> <mot4> <mot5> <mot6> <mot7> <mot8>"
    comparatif.write_text(phrase + "\n", encoding="utf-8")
    protegees = frozenset(_empreintes_texte(phrase, N_DEFAUT))
    rapport = _preparer(racine, export_id, comparatif, tmp_path, empreintes=protegees)
    assert any("Jeu d'évaluation" in b for b in rapport.bloquants)


def test_source_dans_eval_refusee(racine, export_id, tmp_path) -> None:
    interdit = racine / "eval" / "jeu" / "comparatif.md"
    interdit.parent.mkdir(parents=True)
    interdit.write_text("<factice>", encoding="utf-8")
    with pytest.raises(ConfigurationInvalide, match="interdite"):
        preparer(
            racine=racine,
            modele=SLUG,
            export_run=export_id,
            comparatif=interdit,
            sortie=tmp_path / "dossier",
        )


def test_export_incomplet_refuse(racine, comparatif, tmp_path) -> None:
    with pytest.raises(Exception, match="introuvable"):
        _preparer(racine, "20260101-000000-x-abcd", comparatif, tmp_path)


def test_cli_prepare_sans_envoi(racine, export_id, comparatif, tmp_path, capsys) -> None:
    sortie = tmp_path / "cli"
    code = main(
        [
            "publication",
            "preparer",
            "--modele",
            SLUG,
            "--export",
            export_id,
            "--comparatif",
            str(comparatif),
            "--sortie",
            str(sortie),
            "--racine",
            str(racine),
        ]
    )
    assert code == 0
    assert "téléversement manuel" in capsys.readouterr().out
    assert main(["publication", "envoyer"]) != 0
