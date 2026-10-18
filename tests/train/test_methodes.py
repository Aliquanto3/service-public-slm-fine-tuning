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


# --- Test réel : base bf16 non quantifiée, PEFT, gradient checkpointing (CPU) ----------------


def _modele_minuscule_bf16():
    torch = pytest.importorskip("torch")
    transformers = pytest.importorskip("transformers")
    pytest.importorskip("peft")
    torch.manual_seed(0)
    config = transformers.LlamaConfig(
        vocab_size=64,
        hidden_size=16,
        intermediate_size=32,
        num_hidden_layers=2,
        num_attention_heads=2,
        num_key_value_heads=2,
    )
    return torch, transformers.LlamaForCausalLM(config).to(torch.bfloat16)


def test_bf16_reel_adaptateurs_fp32_base_bf16_gradient_avec_checkpointing() -> None:
    """Chemin `bf16` réel : pas de cast, LoRA fp32, gradient jusqu'aux adaptateurs."""
    torch, modele = _modele_minuscule_bf16()
    from types import SimpleNamespace  # noqa: PLC0415

    import peft  # noqa: PLC0415

    pile = SimpleNamespace(peft=peft, torch=torch)
    modele = methodes.preparer_base_quantifiee(pile, modele, "bf16")
    modele.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    config = _config("qlora")
    modele = methodes.poser_adaptateur(pile, modele, methodes.plan_methode("qlora"), config)
    modele.train()
    assert modele.base_model.model.is_gradient_checkpointing

    lora = {n: p for n, p in modele.named_parameters() if "lora_" in n}
    base = {n: p for n, p in modele.named_parameters() if "lora_" not in n}
    assert lora and all(p.dtype == torch.float32 and p.requires_grad for p in lora.values())
    assert all(p.dtype == torch.bfloat16 and not p.requires_grad for p in base.values())

    entree = torch.randint(0, 64, (1, 12))
    sortie = modele(input_ids=entree, labels=entree)
    assert torch.isfinite(sortie.loss)
    sortie.loss.backward()
    # lora_B est nul à l'initialisation : son gradient, lui, ne l'est pas.
    gradients_b = [p.grad for n, p in lora.items() if "lora_B" in n]
    assert gradients_b and all(g is not None for g in gradients_b)
    assert any(float(g.abs().sum()) > 0 for g in gradients_b)
    assert all(p.grad is None for p in base.values())


def test_fp32_kbit_reel_caste_la_base_non_quantifiee() -> None:
    """Témoin : `prepare_model_for_kbit_training` passe les normes en fp32 (évité en bf16)."""
    torch, modele = _modele_minuscule_bf16()
    from types import SimpleNamespace  # noqa: PLC0415

    import peft  # noqa: PLC0415

    modele.is_loaded_in_4bit = True  # comme une base nf4 (le cast ne vise que les bases k-bit)
    modele = methodes.preparer_base_quantifiee(SimpleNamespace(peft=peft), modele, "fp32-kbit")
    normes = [p for n, p in modele.named_parameters() if "norm" in n]
    assert normes and all(p.dtype == torch.float32 for p in normes)
