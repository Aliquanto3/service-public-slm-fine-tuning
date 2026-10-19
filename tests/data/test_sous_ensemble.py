"""Sous-ensemble par Tâche du jeu SFT (`data build --sous-ensemble`) : comptes, identité des
lignes, refus, déterminisme, chargement et chaînage avec un jeu nettoyé.

Tous les textes sont des jetons artificiels (D1) ; aucun appel réseau.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.artefacts import ouvrir_run
from slmsp.core.canonique import sha256_hex
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide
from slmsp.core.sous_ensemble import verifier_sous_ensemble
from slmsp.data.sous_ensemble import lancer_sous_ensemble
from slmsp.train.chargement import charger_jeu

from .test_nettoyage import JEU, ecrire_source, ligne, nettoyer
from .test_preferences import LlmScripte
from .test_preferences import lancer as lancer_preferences

JEU_PT = [
    ligne(1, "Q", "<reponse-factice-1>"),
    ligne(2, "CR", "<reponse-factice-2>"),
    ligne(3, "RD", "<reponse-factice-3>"),
    ligne(4, "CT", "<reponse-factice-4>"),
    ligne(5, "Q", "<reponse-factice-5>"),
    ligne(6, "Q", "<reponse-factice-6>"),
    ligne(7, "LC", "<reponse-factice-7>"),
]
JEU_PT[5]["tache"] = "generique"  # Tâche sans prompt système
JEU_PT[5]["messages"] = [JEU_PT[5]["messages"][1], JEU_PT[5]["messages"][2]]


def sous_ensemble(racine: Path, run_id: str, taches: list[str]) -> Any:
    return lancer_sous_ensemble(
        racine=racine, build_run_id=run_id, taches=taches, consigner=lambda _m: None
    )


def lire_lignes(chemin: Path) -> list[bytes]:
    return [t for t in chemin.read_bytes().split(b"\n") if t]


def test_comptes_et_lignes_identiques_a_la_source(tmp_path: Path) -> None:
    run_id, octets = ecrire_source(tmp_path, JEU_PT)
    resultat = sous_ensemble(tmp_path, run_id, ["generique", "Q", "RD"])

    assert resultat.version == "v2"
    source = lire_lignes(tmp_path / "data" / "train" / "v1" / "train.jsonl")
    gardees = lire_lignes(resultat.dossier / "train.jsonl")
    # Octets identiques, dans l'ordre de la source.
    assert gardees == [source[i] for i in (0, 2, 4, 5)]
    assert resultat.rapport["par_tache"]["CR"] == {"avant": 1, "apres": 0}
    assert resultat.rapport["par_tache"]["Q"] == {"avant": 2, "apres": 2}

    brut = json.loads((resultat.dossier / "MANIFEST.json").read_bytes())
    assert brut["comptes_par_tache"] == {"Q": 2, "RD": 1, "generique": 1}
    assert brut["nb_lignes"] == 4
    assert brut["sha256_train"] == sha256_hex(b"".join(t + b"\n" for t in gardees))
    assert "nettoyage" not in brut
    assert brut["sous_ensemble"] == {
        "depuis_build": run_id,
        "depuis_version": "v1",
        "sha256_train_source": sha256_hex(octets),
        "taches": ["Q", "RD", "generique"],
        "comptes_source": {"CR": 1, "CT": 1, "LC": 1, "Q": 2, "RD": 1, "generique": 1},
    }
    assert brut["filter_run_id"] == "20261017-151827-filter-e914"
    assert ouvrir_run(resultat.run.run_id, racine=tmp_path).statut_courant() == "complet"
    jeu = charger_jeu("v2", racine=tmp_path)
    assert len(jeu.lignes) == 4


def test_tache_inconnue_refusee_sans_version(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    with pytest.raises(ManifesteInvalide, match="XX"):
        sous_ensemble(tmp_path, run_id, ["Q", "XX"])
    with pytest.raises(ManifesteInvalide, match="absente"):
        sous_ensemble(tmp_path, run_id, ["q"])  # casse exacte
    assert not (tmp_path / "data" / "train" / "v2").exists()
    assert [p.name for p in (tmp_path / "runs" / "data-build").iterdir()] == [run_id]


def test_sous_ensemble_vide_refuse(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    with pytest.raises(ManifesteInvalide, match="au moins une"):
        sous_ensemble(tmp_path, run_id, [])
    assert not (tmp_path / "data" / "train" / "v2").exists()


def test_deterministe_deux_builds_meme_sha(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    premier = sous_ensemble(tmp_path, run_id, ["Q", "RD"])
    second = sous_ensemble(tmp_path, run_id, ["RD", "Q", "Q"])  # ordre et doublons sans effet
    assert (premier.version, second.version) == ("v2", "v3")
    assert (premier.dossier / "train.jsonl").read_bytes() == (
        second.dossier / "train.jsonl"
    ).read_bytes()
    sha = [
        json.loads((r.dossier / "MANIFEST.json").read_bytes())["sha256_train"]
        for r in (premier, second)
    ]
    assert sha[0] == sha[1]
    # Revue S2 : MANIFEST identiques hors identité de la version et de son run.
    manifestes = [json.loads((r.dossier / "MANIFEST.json").read_bytes()) for r in (premier, second)]
    for m in manifestes:
        del m["version"], m["run_id"], m["cree_le"]
    assert manifestes[0] == manifestes[1]
    # Les artefacts de la source et du premier build ne sont jamais réécrits.
    assert (premier.dossier / "MANIFEST.json").is_file()


def test_jeu_deja_restreint_refuse(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    premier = sous_ensemble(tmp_path, run_id, ["Q", "RD"])
    with pytest.raises(ManifesteInvalide, match="déjà restreint"):
        sous_ensemble(tmp_path, premier.run.run_id, ["Q"])


def test_sur_jeu_nettoye_chaine_reverifiee(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU)
    nettoye = nettoyer(tmp_path, run_id)  # v2, avec écart (CR) et bloc nettoyage
    resultat = sous_ensemble(tmp_path, nettoye.run.run_id, ["Q", "LC"])
    assert resultat.version == "v3"
    brut = json.loads((resultat.dossier / "MANIFEST.json").read_bytes())
    assert "nettoyage" not in brut
    assert brut["sous_ensemble"]["nettoyage_source"]["ecartes"] == [
        {"rang": 2, "motif": "longueur", "tokens": 6}
    ]
    assert charger_jeu("v3", racine=tmp_path).manifeste["comptes_par_tache"] == {"LC": 2, "Q": 2}
    # Le jeu nettoyé source est altéré : le sous-ensemble ne se charge plus.
    source = tmp_path / "data" / "train" / "v2" / "train.jsonl"
    source.write_bytes(source.read_bytes() + b"\n")
    with pytest.raises(ManifesteInvalide, match="sha256_train_source"):
        charger_jeu("v3", racine=tmp_path)


def test_ligne_alteree_refusee_au_chargement(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    resultat = sous_ensemble(tmp_path, run_id, ["Q", "RD"])
    train = resultat.dossier / "train.jsonl"
    lignes = lire_lignes(train)
    train.write_bytes(b"".join(t + b"\n" for t in lignes[:-1]))  # ligne retirée
    manifeste = resultat.dossier / "MANIFEST.json"
    brut = json.loads(manifeste.read_bytes())
    brut["sha256_train"] = sha256_hex(train.read_bytes())  # SHA recalculé : seule la preuve échoue
    manifeste.write_text(json.dumps(brut), "utf-8")
    with pytest.raises(ProvenanceInvalide, match="sous-ensemble"):
        charger_jeu("v2", racine=tmp_path)


def test_verifier_sous_ensemble_ordre_change_refuse() -> None:
    a, b = (json.dumps({"tache": "Q", "n": i}).encode() for i in (1, 2))
    source = a + b"\n" + b + b"\n"
    verifier_sous_ensemble(source, source, ["Q"])
    with pytest.raises(ProvenanceInvalide):
        verifier_sous_ensemble(b + b"\n" + a + b"\n", source, ["Q"])


@pytest.mark.parametrize(
    "options",
    [
        [],
        ["--taches", ""],
        ["--taches", "Q", "--modele", "base:slug-factice"],
        ["--taches", "Q", "--variante", "diffusable"],
        ["--taches", "Q", "--nettoyage"],
        ["--taches", "Q", "--preferences"],
    ],
)
def test_cli_usage(options: list[str]) -> None:
    code = main(["data", "build", "--sous-ensemble", "--depuis", "x", *options])
    assert code == CodeSortie.USAGE


def test_cli_nominal_et_tache_inconnue(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    base = ["data", "build", "--sous-ensemble", "--depuis", run_id, "--racine", str(tmp_path)]
    assert main([*base, "--taches", "Q,XX"]) == CodeSortie.USAGE
    assert "XX" in capsys.readouterr().err
    assert main([*base, "--taches", "Q, RD"]) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert "Q : 2 → 2" in sortie and "CR : 1 → 0" in sortie and "jeu v2 (3 lignes)" in sortie


def test_ligne_modifiee_refusee_au_chargement(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    resultat = sous_ensemble(tmp_path, run_id, ["Q", "RD"])
    train = resultat.dossier / "train.jsonl"
    train.write_bytes(train.read_bytes().replace(b"<reponse-factice-3>", b"<reponse-factice-x>"))
    manifeste = resultat.dossier / "MANIFEST.json"
    brut = json.loads(manifeste.read_bytes())
    brut["sha256_train"] = sha256_hex(train.read_bytes())
    manifeste.write_text(json.dumps(brut), "utf-8")
    with pytest.raises(ProvenanceInvalide, match="sous-ensemble"):
        charger_jeu("v2", racine=tmp_path)


@pytest.mark.parametrize(("cle", "valeur"), [("nb_lignes", 2), ("comptes_par_tache", {"Q": 3})])
def test_comptes_du_manifest_recoupes_au_chargement(tmp_path: Path, cle: str, valeur: Any) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    resultat = sous_ensemble(tmp_path, run_id, ["Q", "RD"])
    manifeste = resultat.dossier / "MANIFEST.json"
    brut = json.loads(manifeste.read_bytes())
    brut[cle] = valeur
    manifeste.write_text(json.dumps(brut), "utf-8")
    with pytest.raises(ManifesteInvalide, match="recoupe"):
        charger_jeu("v2", racine=tmp_path)


def test_nettoyage_d_un_sous_ensemble_refuse(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU)
    resultat = sous_ensemble(tmp_path, run_id, ["Q", "LC"])
    with pytest.raises(ManifesteInvalide, match="restreint"):
        nettoyer(tmp_path, resultat.run.run_id)
    assert not (tmp_path / "data" / "train" / "v3").exists()


def test_preferences_depuis_un_sous_ensemble(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU_PT)
    restreint = sous_ensemble(tmp_path, run_id, ["Q", "RD"])  # v2, 3 lignes
    llm = LlmScripte(*[f"<rejetee-factice-{i}>" for i in (1, 2, 3)])
    resultat = lancer_preferences(tmp_path, restreint.run.run_id, llm)
    assert resultat.version == "v3"
    brut = json.loads((resultat.dossier / "MANIFEST.json").read_bytes())
    assert (brut["jeu_sft_version"], brut["build_run_id"]) == ("v2", restreint.run.run_id)
    assert brut["comptes_par_tache"] == {"Q": 2, "RD": 1}
    assert "sous_ensemble" not in brut
    assert len(charger_jeu("v3", racine=tmp_path, fichier="preferences.jsonl").lignes) == 3


def test_cli_taches_sans_sous_ensemble_refuse(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["data", "build", "--depuis", "x", "--taches", "Q"])
    assert code == CodeSortie.USAGE
    assert "--sous-ensemble" in capsys.readouterr().err
