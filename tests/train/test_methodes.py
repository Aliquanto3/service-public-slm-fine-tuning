"""Méthode → quantification, LoRA et entraîneur (story 10.4), sur pile simulée."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train import methodes
from slmsp.train.config import RunConfig
from slmsp.train.environnement import ErreurQuantification


def _config(methode: str = "qlora", **hp: object) -> RunConfig:
    return RunConfig.model_validate(
        {
            "campagne": "c",
            "modele": "m",
            "methode": methode,
            "jeu_version": "v1",
            "graine": 5,
            "longueur_max": 128,
            "hyperparametres": hp,
            **({"sft_run_id": "20261016-120000-m1-abcd"} if methode == "orpo" else {}),
        }
    )


@pytest.mark.parametrize(
    ("methode", "quatre_bits", "lora", "entraineur"),
    [
        ("qlora", True, {}, "sft"),
        ("lora", False, {}, "sft"),
        ("dora", True, {"use_dora": True}, "sft"),
        ("orpo", True, {}, "orpo"),
        ("rslora", True, {"use_rslora": True}, "sft"),
        ("pissa", False, {"init_lora_weights": "pissa"}, "sft"),
    ],
)
def test_plan_par_methode(
    methode: str, quatre_bits: bool, lora: dict, entraineur: str, pile
) -> None:
    plan = methodes.plan_methode(methode)
    assert (plan.quantification_4bits, plan.lora, plan.entraineur) == (
        quatre_bits,
        lora,
        entraineur,
    )
    config_lora = methodes.config_lora(pile, plan, _config(methode))
    assert config_lora["target_modules"] == "all-linear"
    assert {k: config_lora[k] for k in lora} == lora
    assert config_lora["r"] == 16


def test_plan_qlora_unsloth() -> None:
    plan = methodes.plan_methode("qlora-unsloth")
    assert plan.entraineur == "unsloth" and plan.quantification_4bits


def test_arguments_sft(tmp_path: Path) -> None:
    arguments = methodes.arguments_entrainement(
        _config(pas_sauvegarde=50),
        methodes.plan_methode("qlora"),
        dossier_checkpoints=tmp_path,
        nb_exemples=100,
        specifiques={"loss_type": "nll"},
    )
    assert "save_total_limit" not in arguments
    assert arguments["report_to"] == "none" and arguments["push_to_hub"] is False
    assert arguments["save_strategy"] == "steps" and arguments["save_steps"] == 50
    assert arguments["include_num_input_tokens_seen"] == "non_padding"
    assert arguments["seed"] == arguments["data_seed"] == 5
    assert arguments["max_steps"] == 13  # ceil(100 / (1 × 8)) pas pour une époque
    assert arguments["dataset_kwargs"] == {"skip_prepare_dataset": True}
    assert arguments["loss_type"] == "nll" and arguments["max_length"] == 128


def test_arguments_orpo_sans_options_sft(tmp_path: Path) -> None:
    arguments = methodes.arguments_entrainement(
        _config("orpo", orpo_beta=0.2),
        methodes.plan_methode("orpo"),
        dossier_checkpoints=tmp_path,
        nb_exemples=8,
        specifiques={"loss_type": "nll"},
    )
    assert arguments["beta"] == 0.2
    assert "dataset_kwargs" not in arguments and "loss_type" not in arguments


def test_argument_specifique_en_conflit(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="seed"):
        methodes.arguments_entrainement(
            _config(),
            methodes.plan_methode("lora"),
            dossier_checkpoints=tmp_path,
            nb_exemples=1,
            specifiques={"seed": 1},
        )


def test_pas_total() -> None:
    assert methodes.pas_total(_config(pas_max=7), 1000) == 7
    assert methodes.pas_total(_config(epoques=2.0, accumulation=4), 10) == 6


def test_chargement_4_bits(pile, tmp_path: Path) -> None:
    modele = methodes.charger_modele(pile, tmp_path, methodes.plan_methode("dora"))
    assert pile.arguments_modele["quantization_config"][1]["bnb_4bit_quant_type"] == "nf4"
    assert modele.config.use_cache is False
    methodes.charger_modele(pile, tmp_path, methodes.plan_methode("pissa"))
    assert "quantization_config" not in pile.arguments_modele


@pytest.mark.parametrize("methode", ["qlora", "dora", "orpo", "rslora"])
def test_precision_defaut_appelle_prepare_kbit(pile, tmp_path: Path, methode: str) -> None:
    methodes.charger_modele(pile, tmp_path, methodes.plan_methode(methode))
    assert pile.appels_base == ["kbit"]


@pytest.mark.parametrize("methode", ["qlora", "dora", "orpo", "rslora"])
def test_precision_bf16_sans_prepare_kbit(pile, tmp_path: Path, methode: str) -> None:
    modele = methodes.charger_modele(
        pile, tmp_path, methodes.plan_methode(methode), precision_base="bf16"
    )
    assert pile.appels_base == ["grads"]  # enable_input_require_grads, pas de cast fp32
    assert modele.config.use_cache is False


@pytest.mark.parametrize("precision", ["fp32-kbit", "bf16"])
def test_precision_sans_effet_hors_quantification(pile, tmp_path: Path, precision: str) -> None:
    for methode in ("lora", "pissa"):
        methodes.charger_modele(
            pile, tmp_path, methodes.plan_methode(methode), precision_base=precision
        )
    assert pile.appels_base == []


@pytest.mark.parametrize(
    ("erreur", "attendue"),
    [
        (ImportError("bitsandbytes absent"), ErreurQuantification),
        (RuntimeError("bitsandbytes : CUDA setup failed"), ErreurQuantification),
        (RuntimeError("CUDA out of memory"), RuntimeError),
        (ValueError("config inattendue"), ValueError),
    ],
)
def test_seules_les_erreurs_bitsandbytes_sont_converties(
    pile, tmp_path: Path, erreur: Exception, attendue: type
) -> None:
    def lever(*_a: object, **_k: object) -> None:
        raise erreur

    pile.transformers.AutoModelForCausalLM.from_pretrained = lever
    with pytest.raises(attendue) as info:
        methodes.charger_modele(pile, tmp_path, methodes.plan_methode("qlora"))
    if attendue is not ErreurQuantification:
        assert info.value is erreur


def test_entraineur_sft_recoit_le_collateur(pile, tmp_path: Path) -> None:
    collateur = object()
    entraineur = methodes.creer_entraineur(
        pile,
        methodes.plan_methode("lora"),
        modele="m",
        tokenizer="t",
        jeu=[],
        collateur=collateur,
        arguments={"max_steps": 1},
        callbacks=["cb"],
    )
    assert entraineur.collateur is collateur and entraineur.callbacks == ["cb"]
