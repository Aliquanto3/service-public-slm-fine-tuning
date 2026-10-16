"""Jeu construit, provenance, contraintes et pré-tokenisation (story 10.4).

Contenus factices (`<réponse-factice-…>`) : aucune donnée d'entraînement rédigée.
"""

from __future__ import annotations

import json

import pytest

from slmsp.core.erreurs import ConfigurationInvalide, LectureInterdite, ManifesteInvalide
from slmsp.inference.serveur import charger_config_modele
from slmsp.train import chargement
from slmsp.train.masque import IGNORE


def test_jeu_valide(projet) -> None:
    projet.ecrire_jeu()
    jeu = chargement.charger_jeu("v1", racine=projet.racine)
    assert len(jeu.lignes) == 3 and jeu.ligne()["run_build"] == "20261016-120000-v1-abcd"
    assert chargement.recontroler_appel_ids(jeu.lignes, racine=projet.racine) == 3


def test_jeu_absent(projet) -> None:
    with pytest.raises(chargement.JeuAbsent, match="aucun jeu de dépannage"):
        chargement.charger_jeu("v1", racine=projet.racine)


@pytest.mark.parametrize(
    ("manifeste", "message"),
    [
        ({"type_run": "data-filter"}, "data-build"),
        ({"version": "v2"}, "version"),
        ({"sha256_train": "0" * 64}, "SHA-256"),
        ({"run_id": "pas-un-run"}, "data-build"),
    ],
)
def test_manifeste_refuse(projet, manifeste: dict, message: str) -> None:
    projet.ecrire_jeu(manifeste=manifeste)
    with pytest.raises(ManifesteInvalide, match=message):
        chargement.charger_jeu("v1", racine=projet.racine)


def test_ligne_non_conforme(projet, factices) -> None:
    ligne = factices.ligne(1)
    ligne["meta"]["appel_ids"] = []
    projet.ecrire_jeu(lignes=[ligne])
    with pytest.raises(ManifesteInvalide, match=":1 : ligne non conforme"):
        chargement.charger_jeu("v1", racine=projet.racine)


@pytest.mark.parametrize(
    ("usages", "message"),
    [
        ({"appel-2": ("juge-second", "ok")}, "usage juge-second"),
        ({"appel-2": ("generation", "erreur")}, "statut erreur"),
    ],
)
def test_appel_ids_hors_generation(projet, usages: dict, message: str) -> None:
    projet.ecrire_jeu(usages=usages)
    jeu = chargement.charger_jeu("v1", racine=projet.racine)
    with pytest.raises(ManifesteInvalide, match=message):
        chargement.recontroler_appel_ids(jeu.lignes, racine=projet.racine)


def test_appel_id_inconnu(projet) -> None:
    projet.ecrire_jeu()
    jeu = chargement.charger_jeu("v1", racine=projet.racine)
    jeu.lignes[0].meta.appel_ids.append("appel-fantome")
    with pytest.raises(ManifesteInvalide, match="appel-fantome"):
        chargement.recontroler_appel_ids(jeu.lignes, racine=projet.racine)


def test_lecture_hors_liste_interdite(projet) -> None:
    projet.ecrire_jeu()
    jeu = chargement.charger_jeu("v1", racine=projet.racine)
    autre = projet.racine / "runs" / "eval-notation" / "x" / "appels-mistral.sqlite"
    with pytest.raises(LectureInterdite):
        chargement.recontroler_appel_ids(jeu.lignes, journal=autre, racine=projet.racine)
    with pytest.raises(LectureInterdite):
        chargement.recontroler_appel_ids(
            jeu.lignes, journal=projet.racine / "data" / "raw" / "j.sqlite", racine=projet.racine
        )


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ({"layer_types": ["attention", "mamba"]}, "Mamba"),
        ({"text_config": {"layers_block_type": ["mamba", "attention"]}}, "Mamba"),
        ({"quantization_config": {"quant_method": "fp8"}}, "FP8"),
        ({"vision_config": {}}, "encodeur vision"),
    ],
)
def test_contraintes_refusees(config: dict, message: str) -> None:
    with pytest.raises(ConfigurationInvalide, match=message):
        chargement.controler_contraintes(config, "m", exclure_vision=False)


def test_vision_exclue_acceptee() -> None:
    resume = chargement.controler_contraintes(
        {"model_type": "mistral3", "vision_config": {}}, "m", exclure_vision=True
    )
    assert resume["vision_config"] == "exclu"


def test_pretokenisation_tronque_ids_et_labels_ensemble(factices) -> None:
    tokenizer = factices.Tokenizer()
    config = charger_config_modele("granite-4.0-1b")
    lignes = [chargement._Ligne.model_validate(factices.ligne(i, mots=8)) for i in (1, 2)]
    complet, _ = chargement.pretokeniser(
        tokenizer, lignes, longueur_max=10_000, config_modele=config
    )
    longueur = len(complet[0]["input_ids"]) - 5
    exemples, stats = chargement.pretokeniser(
        tokenizer, lignes, longueur_max=longueur, config_modele=config
    )
    assert stats["tronques"] == 2 and stats["retenus"] == 2
    for exemple, entier in zip(exemples, complet, strict=True):
        assert len(exemple["input_ids"]) == len(exemple["labels"]) == longueur
        assert exemple["labels"] == entier["labels"][:longueur]
    assert tokenizer.appels_tools[0] is not None  # protocole natif : outils transmis


def test_exemple_sans_supervision_ecarte(factices) -> None:
    tokenizer = factices.Tokenizer()
    config = charger_config_modele("granite-4.0-1b")
    lignes = [chargement._Ligne.model_validate(factices.ligne(1))]
    exemples, stats = chargement.pretokeniser(
        tokenizer, lignes, longueur_max=8, config_modele=config
    )
    assert exemples == [] and stats["ecartes_sans_supervision"] == 1


def test_collateur() -> None:
    lot = chargement.CollateurMasque(pad_id=0)(
        [
            {"input_ids": [5, 6, 7], "labels": [IGNORE, 6, 7]},
            {"input_ids": [5], "labels": [5]},
        ]
    )
    assert lot["input_ids"][1] == [5, 0, 0]
    assert lot["labels"][1] == [5, IGNORE, IGNORE]
    assert lot["attention_mask"] == [[1, 1, 1], [1, 0, 0]]


def test_sha_chat_template(factices) -> None:
    tokenizer = factices.Tokenizer()
    assert len(chargement.sha_chat_template(tokenizer)) == 64
    tokenizer.chat_template = None
    with pytest.raises(ConfigurationInvalide):
        chargement.sha_chat_template(tokenizer)
    tokenizer.chat_template = {"default": "x"}
    assert chargement.sha_chat_template(tokenizer) != json.dumps({"default": "x"})
