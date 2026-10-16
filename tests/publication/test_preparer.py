from __future__ import annotations

import shutil
import socket
from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.canonique import sha256_fichier
from slmsp.core.erreurs import ConfigurationInvalide, ManifesteInvalide
from slmsp.core.items import N_DEFAUT, empreintes_texte
from slmsp.publication.config import charger_config
from slmsp.publication.preparer import preparer, versions_du_jeu

SLUG = "granite-4.0-1b"
DEPOT = Path(__file__).resolve().parents[2]


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


EMPREINTES_FACTICES = frozenset({"0" * 16})


def _preparer(racine: Path, export_id: str, comparatif: Path, tmp_path: Path, **kw):
    kw.setdefault("empreintes", EMPREINTES_FACTICES)
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
    protegees = frozenset(empreintes_texte(phrase, N_DEFAUT))
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
            empreintes=EMPREINTES_FACTICES,
        )


def test_export_incomplet_refuse(racine, comparatif, tmp_path) -> None:
    with pytest.raises(ManifesteInvalide, match="introuvable"):
        _preparer(racine, "20260101-000000-x-abcd", comparatif, tmp_path)


def test_cli_prepare_sans_envoi(racine, export_id, comparatif, tmp_path, capsys) -> None:
    # Sans empreintes injectées, la CLI lit le vrai Jeu (copie en lecture seule dans la racine).
    for sous in ("jeu", "calibrage"):
        shutil.copytree(DEPOT / "eval" / sous, racine / "eval" / sous)
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


def test_refus_successifs_ne_se_recouvrent_pas(racine, export_id, comparatif, tmp_path) -> None:
    comparatif.write_text("Modèle certifié ISO 42001.\n", encoding="utf-8")
    noms = {_preparer(racine, export_id, comparatif, tmp_path).dossier.name for _ in range(3)}
    assert noms == {"dossier.refuse", "dossier.refuse.2", "dossier.refuse.3"}
    assert not (tmp_path / "dossier").exists()
    assert not (tmp_path / "dossier.part").exists()


def test_erreur_en_cours_de_route_ne_laisse_rien(
    racine, export_id, comparatif, tmp_path, monkeypatch
) -> None:
    def casse(*_a: object, **_k: object) -> None:
        raise OSError("disque plein")

    monkeypatch.setattr("slmsp.publication.preparer.fiche.rendre_fiche", casse)
    with pytest.raises(OSError, match="disque plein"):
        _preparer(racine, export_id, comparatif, tmp_path)
    assert not (tmp_path / "dossier").exists()
    assert not (tmp_path / "dossier.part").exists()
    assert not (tmp_path / "dossier.refuse").exists()


def test_succes_ne_laisse_pas_de_part(racine, export_id, comparatif, tmp_path) -> None:
    (tmp_path / "dossier.part").mkdir()
    (tmp_path / "dossier.part" / "reste").write_text("x", encoding="utf-8")
    rapport = _preparer(racine, export_id, comparatif, tmp_path)
    assert rapport.dossier == (tmp_path / "dossier").resolve()
    assert not (tmp_path / "dossier.part").exists()
    assert not (rapport.dossier / "reste").exists()


def test_jeux_proteges_vide_refuse(racine, export_id, comparatif, tmp_path) -> None:
    modifier_config(racine, 'jeux_proteges = ["v1.0", "v1.1", "calibrage"]', "jeux_proteges = []")
    with pytest.raises(ConfigurationInvalide, match="jeux_proteges est vide"):
        _preparer(racine, export_id, comparatif, tmp_path, empreintes=None)


def test_jeux_proteges_incomplet_refuse(racine, export_id, comparatif, tmp_path) -> None:
    for version in ("v1.0", "v1.1", "v2.0"):
        (racine / "eval" / "jeu" / version).mkdir(parents=True)
    (racine / "eval" / "calibrage").mkdir()
    (racine / "eval" / "calibrage" / "echantillon-calibrage.jsonl").write_text("", encoding="utf-8")
    assert versions_du_jeu(racine) == ["v1.0", "v1.1", "v2.0", "calibrage"]
    with pytest.raises(ConfigurationInvalide, match=r"ne couvre pas v2\.0$"):
        _preparer(racine, export_id, comparatif, tmp_path, empreintes=None)
    modifier_config(racine, ', "calibrage"]', "]")
    with pytest.raises(ConfigurationInvalide, match=r"ne couvre pas v2\.0, calibrage$"):
        _preparer(racine, export_id, comparatif, tmp_path, empreintes=None)


def test_versions_du_depot_toutes_protegees() -> None:
    """Sur le dépôt réel : la config couvre chaque version de `eval/jeu/` et le calibrage."""
    config = charger_config(DEPOT)
    assert set(versions_du_jeu(DEPOT)) <= set(config.jeux_proteges)


def test_verifie_le_futur_refuse(racine, export_id, comparatif, tmp_path) -> None:
    modifier_config(racine, "verifie_le = 2026-10-17", "verifie_le = 2999-01-01")
    with pytest.raises(ConfigurationInvalide, match="dans le futur"):
        _preparer(racine, export_id, comparatif, tmp_path)


def test_fuite_contre_data_train(racine, export_id, comparatif, tmp_path) -> None:
    phrase = "<mot1> <mot2> <mot3> <mot4> <mot5> <mot6> <mot7> <mot8>"
    (racine / "data" / "train").mkdir()
    (racine / "data" / "train" / "ex.jsonl").write_text(phrase + "\n", encoding="utf-8")
    comparatif.write_text(phrase + "\n", encoding="utf-8")
    rapport = _preparer(racine, export_id, comparatif, tmp_path)
    assert any("jeu d'entraînement" in b for b in rapport.bloquants)
