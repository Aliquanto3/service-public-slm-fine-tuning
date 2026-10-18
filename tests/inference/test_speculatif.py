"""Décodage spéculatif de `ServeurLlama` : arguments, compatibilité du brouillon, consignation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from slmsp.core.config import dossier_modeles
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.inference.client import ClientLlama
from slmsp.inference.serveur import ServeurLlama, Speculatif, charger_config_modele

CIBLE, BROUILLON = "minicpm5-2b", "minicpm5-1b"


@pytest.fixture
def modeles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    dossier = tmp_path / "models"
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(dossier))
    return dossier.resolve()


def _serveur(vendor, speculatif=None, slug: str = CIBLE) -> ServeurLlama:
    config = charger_config_modele(slug)
    return ServeurLlama(
        config, "cpu", slug=slug, config_llamacpp=vendor.config, speculatif=speculatif
    )


def test_sans_speculatif_la_ligne_est_inchangee(vendor_factice, modeles: Path) -> None:
    defaut = _serveur(vendor_factice).arguments(5555)
    assert "--spec-type" not in defaut and "-md" not in defaut
    assert defaut == _serveur(vendor_factice, None).arguments(5555)
    assert "speculatif" not in _serveur(vendor_factice).description()


def test_arguments_brouillon(vendor_factice, modeles: Path) -> None:
    config = charger_config_modele(CIBLE).model_copy(update={"threads": 4})
    instance = ServeurLlama(
        config,
        "cpu",
        slug=CIBLE,
        config_llamacpp=vendor_factice.config,
        speculatif=Speculatif("brouillon", BROUILLON, 5),
    )
    base = ServeurLlama(config, "cpu", slug=CIBLE, config_llamacpp=vendor_factice.config)
    arguments = instance.arguments(5555)
    gguf = modeles / BROUILLON / "gguf" / "MiniCPM5-1B-Q4_K_M.gguf"
    assert arguments[: len(base.arguments(5555))] == base.arguments(5555)
    assert arguments[len(base.arguments(5555)) :] == [
        "-md", str(gguf), "--spec-type", "draft-simple",
        "-ctkd", "f16", "-ctvd", "f16", "--spec-draft-n-max", "5", "-td", "4",
    ]  # fmt: skip
    description = instance.description()
    assert description["speculatif"] == {"mode": "brouillon", "brouillon": BROUILLON, "n_max": 5}
    assert description["gguf_brouillon"] == gguf.name


def test_n_max_par_defaut_et_threads_absents(vendor_factice, modeles: Path) -> None:
    arguments = _serveur(vendor_factice, {"mode": "brouillon", "brouillon": BROUILLON}).arguments(1)
    assert arguments[arguments.index("--spec-draft-n-max") + 1] == "3"
    assert "-td" not in arguments


def test_arguments_ngram(vendor_factice, modeles: Path) -> None:
    instance = _serveur(vendor_factice, {"mode": "ngram"})
    arguments = instance.arguments(5555)
    assert arguments[-2:] == ["--spec-type", "ngram-simple"]
    assert "-md" not in arguments and instance.gguf_brouillon is None
    assert instance.description()["speculatif"]["mode"] == "ngram"


def test_vocabulaire_different_refuse(vendor_factice, modeles: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="tokenizer.json différent"):
        _serveur(vendor_factice, Speculatif("brouillon", "granite-4.0-1b"))


def test_vocab_size_different_refuse(vendor_factice, modeles: Path) -> None:
    for slug, taille in ((CIBLE, 1000), (BROUILLON, 2000)):
        (modeles / slug).mkdir(parents=True)
        (modeles / slug / "config.json").write_text(
            json.dumps({"vocab_size": taille}), encoding="utf-8"
        )
    with pytest.raises(ConfigurationInvalide, match="vocab_size"):
        _serveur(vendor_factice, Speculatif("brouillon", BROUILLON))


@pytest.mark.parametrize(
    "valeur",
    [
        {"mode": "autre"},
        {"mode": "brouillon"},
        {"mode": "ngram", "brouillon": BROUILLON},
        {"mode": "ngram", "n_max": 4},
        {"mode": "brouillon", "brouillon": BROUILLON, "n_max": 0},
        {"brouillon": BROUILLON},
        {"mode": "brouillon", "brouillon": BROUILLON, "inconnu": 1},
        {"mode": "brouillon", "brouillon": "../x"},
    ],
)
def test_speculatif_invalide(valeur: dict) -> None:
    with pytest.raises(ConfigurationInvalide):
        Speculatif.depuis(valeur)


def test_embedding_refuse(vendor_factice, modeles: Path) -> None:
    config = charger_config_modele("bge-m3")
    with pytest.raises(ConfigurationInvalide, match="génération"):
        ServeurLlama(config, "cpu", slug="bge-m3", speculatif={"mode": "ngram"})


def test_gguf_brouillon_absent_refuse_au_demarrage(vendor_factice, modeles: Path) -> None:
    instance = _serveur(vendor_factice, Speculatif("brouillon", BROUILLON))
    gguf = modeles / CIBLE / "gguf" / "MiniCPM5-2B-Q4_K_M.gguf"
    gguf.parent.mkdir(parents=True)
    gguf.write_bytes(b"GGUF factice")
    with pytest.raises(ConfigurationInvalide, match="brouillon absent"):
        instance.demarrer()


@pytest.mark.lent
@pytest.mark.integration
def test_reel_demarrage_avec_brouillon(vendor_reel: Path, tmp_path: Path) -> None:
    """Vrai llama-server CPU avec brouillon : options acceptées, `timings` du décodage."""
    base = dossier_modeles()
    for slug, fichier in (
        (CIBLE, "MiniCPM5-2B-Q4_K_M.gguf"),
        (BROUILLON, "MiniCPM5-1B-Q4_K_M.gguf"),
    ):
        if not (base / slug / "gguf" / fichier).is_file():
            pytest.skip(f"GGUF absent : {slug}")
    config = charger_config_modele(CIBLE).model_copy(update={"contexte": 1024, "threads": 4})
    with ServeurLlama(
        config,
        "cpu",
        slug=CIBLE,
        speculatif=Speculatif("brouillon", BROUILLON, 4),
        journal=tmp_path / "serveur.log",
    ) as serveur:
        evenements = list(
            serveur.client().generer(
                [{"role": "user", "content": "Écris une phrase sur la mer."}],
                options={"temperature": 0, "seed": 42, "max_tokens": 24},
            )
        )
    usage = evenements[-1].usage or {}
    assert usage.get("draft_n", 0) > 0, usage
    assert 0 <= usage["draft_n_accepted"] <= usage["draft_n"]


def test_client_recupere_les_timings_du_flux(serveur_factice) -> None:
    """`draft_n` et `draft_n_accepted` du dernier morceau rejoignent `Fin.usage`."""
    serveur_factice.scenario.chat = [
        {"choices": [{"delta": {"content": "<jeton-factice>"}}]},
        {
            "choices": [{"delta": {}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 1, "total_tokens": 8},
            "timings": {"draft_n": 6, "draft_n_accepted": 4, "predicted_n": 1},
        },
    ]
    with ClientLlama(serveur_factice.port) as client:
        fin = list(client.generer([{"role": "user", "content": "<question-factice>"}]))[-1]
    assert fin.usage is not None
    assert (fin.usage["draft_n"], fin.usage["draft_n_accepted"]) == (6, 4)
    assert fin.usage["completion_tokens"] == 1
