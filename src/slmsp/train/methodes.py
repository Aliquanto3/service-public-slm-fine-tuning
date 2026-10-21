"""Méthode d'entraînement → quantification, adaptateur PEFT et entraîneur TRL (story 10.4).

Passer d'une méthode à l'autre ne change que le TOML (AD-18) : la table `PLANS` décrit
chaque méthode par trois données, la base (nf4 4 bits ou bf16), les options de
`LoraConfig` et l'entraîneur.

| méthode | base | `LoraConfig` | entraîneur |
| --- | --- | --- | --- |
| `qlora` (M1) | nf4 4 bits | — | `SFTTrainer` |
| `lora` (M2) | bf16 | — | `SFTTrainer` |
| `dora` (M3) | nf4 4 bits | `use_dora=True` | `SFTTrainer` |
| `orpo` (M4) | nf4 4 bits | — | `trl.experimental.orpo.ORPOTrainer` |
| `rslora` | nf4 4 bits | `use_rslora=True` | `SFTTrainer` |
| `pissa` | bf16 (incompatible avec nf4) | `init_lora_weights="pissa"` | `SFTTrainer` |

| `qlora-unsloth` | nf4 4 bits (Unsloth) | — | sous-processus `envs/unsloth` (`variante_unsloth`) |

`qlora-unsloth` est une variante de vitesse, déléguée à l'environnement isolé (story 10.5).
`assistant_only_loss` de TRL n'est pas utilisé : le jeu est pré-tokenisé avec les labels de
`train.masque`. La pile (torch, transformers, peft, trl) est injectée (`environnement.Pile`).
"""

from __future__ import annotations

import importlib
import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final, Literal

from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train import kl_base
from slmsp.train.config import RunConfig
from slmsp.train.couts import ARGUMENTS_TRAINER
from slmsp.train.environnement import (
    CIBLES_TOUTES_LINEAIRES,
    ErreurQuantification,
    Pile,
    cibles_lora,
    classe_modele,
)

Entraineur = Literal["sft", "orpo", "unsloth"]


@dataclass(frozen=True)
class PlanMethode:
    """Traduction d'une méthode : base 4 bits ou non, options LoRA, entraîneur."""

    methode: str
    quantification_4bits: bool
    lora: dict[str, Any] = field(default_factory=dict)
    entraineur: Entraineur = "sft"

    def ligne(self) -> dict[str, Any]:
        """Description consignée dans `run.json`."""
        return asdict(self)


PLANS: Final[Mapping[str, PlanMethode]] = {
    "qlora": PlanMethode("qlora", True),
    "lora": PlanMethode("lora", False),
    "dora": PlanMethode("dora", True, {"use_dora": True}),
    "orpo": PlanMethode("orpo", True, entraineur="orpo"),
    "rslora": PlanMethode("rslora", True, {"use_rslora": True}),
    "pissa": PlanMethode("pissa", False, {"init_lora_weights": "pissa"}),
    "qlora-unsloth": PlanMethode("qlora-unsloth", True, entraineur="unsloth"),
}

CIBLES_LORA: Final = CIBLES_TOUTES_LINEAIRES
"""Toutes les couches linéaires sauf la tête de sortie : ni `embed_tokens` ni `lm_head`.
Un modèle `multimodal` reçoit une regex sur `language_model` (`cibles_lora`, défini dans
`environnement` pour être partagé avec la sonde)."""


def plan_methode(methode: str) -> PlanMethode:
    """Plan de `methode` ; lève `ConfigurationInvalide` pour une méthode inconnue."""
    try:
        return PLANS[methode]
    except KeyError:
        raise ConfigurationInvalide(
            f"méthode inconnue : {methode!r} (attendu : {', '.join(PLANS)})"
        ) from None


def config_bnb(pile: Pile) -> Any:
    """`BitsAndBytesConfig` nf4, double quantification, calcul en bf16."""
    return pile.transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=pile.torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )


def config_lora(pile: Pile, plan: PlanMethode, config: RunConfig, cibles: str = CIBLES_LORA) -> Any:
    """`LoraConfig` du Run : rang, alpha et dropout du TOML, options de la méthode, `cibles`."""
    hp = config.hyperparametres
    return pile.peft.LoraConfig(
        r=hp.lora_rang,
        lora_alpha=hp.lora_alpha,
        lora_dropout=hp.lora_dropout,
        bias="none",
        target_modules=cibles,
        task_type="CAUSAL_LM",
        **plan.lora,
    )


def pas_total(config: RunConfig, nb_exemples: int) -> int:
    """Pas d'optimisation du Run : `pas_max`, sinon `epoques` passes sur le jeu."""
    hp = config.hyperparametres
    if hp.pas_max is not None:
        return hp.pas_max
    par_epoque = math.ceil(max(nb_exemples, 1) / (hp.taille_lot * hp.accumulation))
    return max(1, math.ceil(par_epoque * hp.epoques))


def arguments_entrainement(
    config: RunConfig,
    plan: PlanMethode,
    *,
    dossier_checkpoints: str | Path,
    nb_exemples: int,
    specifiques: Mapping[str, Any] | None = None,
    cpu: bool = False,
) -> dict[str, Any]:
    """Arguments de `SFTConfig` (ou `ORPOConfig`) : complets, consignés dans le run.

    Aucun rapport, aucune publication, jamais de `save_total_limit` ; un checkpoint tous
    les `pas_sauvegarde` pas sous `dossier_checkpoints`. `specifiques` (arguments exigés
    par l'architecture, `environnement.arguments_specifiques`) ne vaut que pour SFT et ne
    peut remplacer aucun argument commun. `cpu` sert au test réel sur un modèle minuscule.
    """
    hp = config.hyperparametres
    total = pas_total(config, nb_exemples)
    arguments: dict[str, Any] = dict(
        output_dir=str(dossier_checkpoints),
        report_to="none",
        push_to_hub=False,
        save_strategy="steps",
        save_steps=hp.pas_sauvegarde,
        save_only_model=False,
        max_steps=total,
        per_device_train_batch_size=hp.taille_lot,
        gradient_accumulation_steps=hp.accumulation,
        learning_rate=hp.taux_apprentissage,
        lr_scheduler_type=hp.planificateur,
        warmup_steps=int(total * hp.echauffement_ratio),
        logging_steps=1,
        logging_strategy="steps",
        disable_tqdm=True,
        bf16=not cpu,
        use_cpu=cpu,
        gradient_checkpointing=not cpu,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_length=config.longueur_max,
        remove_unused_columns=False,
        seed=config.graine,
        data_seed=config.graine,
        dataloader_num_workers=0,
        dataloader_pin_memory=False,
        optim="adamw_torch",
        **ARGUMENTS_TRAINER,
    )
    if plan.entraineur == "orpo":
        arguments["beta"] = hp.orpo_beta
        return arguments
    arguments.update(packing=False, padding_free=False)
    arguments["dataset_kwargs"] = {"skip_prepare_dataset": True}
    for cle, valeur in (specifiques or {}).items():
        if cle in arguments:
            raise ConfigurationInvalide(f"argument d'entraînement spécifique en conflit : {cle}")
        arguments[cle] = valeur
    return arguments


def _est_oom(pile: Pile, exc: BaseException) -> bool:
    erreur_oom = getattr(getattr(pile.torch, "cuda", None), "OutOfMemoryError", None)
    if isinstance(erreur_oom, type) and isinstance(exc, erreur_oom):
        return True
    return "out of memory" in str(exc).lower()


def _vient_de_bitsandbytes(exc: BaseException) -> bool:
    if isinstance(exc, ImportError):
        return True
    texte = f"{type(exc).__module__} {exc}".lower()
    return "bitsandbytes" in texte or "bnb" in texte.split()


def preparer_base_quantifiee(pile: Pile, modele: Any, precision_base: str) -> Any:
    """Prépare une base 4 bits au gradient checkpointing (`precision_base`, voir `RunConfig`).

    `fp32-kbit` : `prepare_model_for_kbit_training` (embeddings, normes et conv1d en fp32).
    `bf16` : sans ce cast ; `enable_input_require_grads` suffit à faire circuler le gradient
    avec le checkpointing (poids LoRA fp32, comme PEFT les crée).
    """
    if precision_base == "bf16":
        modele.enable_input_require_grads()
        return modele
    return pile.peft.prepare_model_for_kbit_training(
        modele,
        use_gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )


def charger_modele(
    pile: Pile,
    dossier: Path,
    plan: PlanMethode,
    *,
    cpu: bool = False,
    precision_base: str = "fp32-kbit",
    multimodal: str | None = None,
) -> Any:
    """Poids du Modèle de base, en nf4 4 bits ou en bf16 selon le plan (GPU 0, ou CPU).

    `precision_base` ne joue que pour une base quantifiée : sans quantification, le cast
    `prepare_model_for_kbit_training` n'a jamais été appelé. La classe vient de
    `environnement.classe_modele` (`multimodal` de la fiche).

    Seule une erreur d'import ou de bitsandbytes devient `ErreurQuantification` ; une
    erreur de mémoire et toute autre exception sont propagées telles quelles (W4.3).
    """
    torch = pile.torch
    classe = classe_modele(pile, multimodal)
    arguments: dict[str, Any] = {
        "dtype": torch.float32 if cpu else torch.bfloat16,
        "attn_implementation": "sdpa",
        "low_cpu_mem_usage": True,
    }
    if not cpu:
        arguments["device_map"] = {"": 0}
    if not plan.quantification_4bits:
        modele = classe.from_pretrained(str(dossier), **arguments)
    else:
        try:
            if pile.bitsandbytes is None:
                pile.bitsandbytes = importlib.import_module("bitsandbytes")
            arguments["quantization_config"] = config_bnb(pile)
            modele = classe.from_pretrained(str(dossier), **arguments)
            modele = preparer_base_quantifiee(pile, modele, precision_base)
        except Exception as exc:
            if _est_oom(pile, exc) or not _vient_de_bitsandbytes(exc):
                raise
            raise ErreurQuantification(
                f"chargement 4 bits nf4 impossible : {type(exc).__name__} : {exc}"
            ) from exc
    modele.config.use_cache = False
    return modele


def poser_adaptateur(
    pile: Pile,
    modele: Any,
    plan: PlanMethode,
    config: RunConfig,
    multimodal: str | None = None,
) -> Any:
    """Adaptateur PEFT neuf ; l'appelant a posé la graine avant (W4.4). Cibles de
    `cibles_lora` : `language_model` seul pour un modèle `multimodal`."""
    cibles = cibles_lora(modele, multimodal)
    return pile.peft.get_peft_model(modele, config_lora(pile, plan, config, cibles))


def creer_entraineur(
    pile: Pile,
    plan: PlanMethode,
    *,
    modele: Any,
    tokenizer: Any,
    jeu: Any,
    collateur: Any,
    arguments: Mapping[str, Any],
    callbacks: Sequence[Any] = (),
    kl: float = 0.0,
    kl_temperature: float = 1.0,
    journal: kl_base.Journal | None = None,
) -> Any:
    """`SFTTrainer` (jeu pré-tokenisé, collateur du masque) ou `ORPOTrainer`.

    ORPO reçoit des paires `{prompt, chosen, rejected}` déjà rendues en texte
    (`chargement.preparer_preferences`) et garde son collateur de paires (`collateur` ignoré).
    `kl` > 0 (QLoRA seulement) : `SFTTrainer` avec le terme KL vers la base (`train.kl_base`),
    pertes journalisées par `journal` ; `kl` = 0 : `SFTTrainer` tel quel.
    """
    if kl > 0 and plan.methode != "qlora":
        raise ConfigurationInvalide(
            f"kl_base > 0 n'est permis qu'avec methode = qlora (reçu : {plan.methode})"
        )
    if plan.entraineur == "orpo":
        orpo = importlib.import_module("trl.experimental.orpo")
        return orpo.ORPOTrainer(
            model=modele,
            args=orpo.ORPOConfig(**arguments),
            train_dataset=jeu,
            processing_class=tokenizer,
            callbacks=list(callbacks),
        )
    communs: dict[str, Any] = dict(
        model=modele,
        args=pile.trl.SFTConfig(**arguments),
        train_dataset=jeu,
        data_collator=collateur,
        processing_class=tokenizer,
        callbacks=list(callbacks),
    )
    if kl > 0:
        classe = kl_base.classe_entraineur_kl(pile.trl.SFTTrainer, pile.torch)
        return classe(**communs, kl_base=kl, kl_temperature=kl_temperature, journal=journal)
    return pile.trl.SFTTrainer(**communs)
