"""Environnement d'entraînement Windows et mesure H-WIN-TRAIN (story 10.1).

`sonder` contrôle le matériel (CUDA, capacité, bf16), charge un Modèle de base en 4 bits
nf4 (QLoRA) ou en bf16 (LoRA), y pose un adaptateur LoRA PEFT, puis exécute quelques pas
de `trl.SFTTrainer` sur des **tokens aléatoires** (graine fixe, aucune donnée réelle), une
longueur de séquence après l'autre. Pour chaque longueur : perte et finitude, VRAM
maximale (`max_memory_allocated` / `max_memory_reserved`), débit en tokens/s hors padding
après un pas de chauffe (batch 1, ni troncature ni padding), et un statut `ok`, `oom` ou
`debordement` (VRAM réservée au-delà de `FRACTION_DEBORDEMENT` de la mémoire de la carte :
débordement probable en mémoire partagée WDDM). Après un `oom` ou un `debordement`, les
longueurs suivantes ne sont pas tentées.

Les arguments d'entraînement propres à une architecture (`arguments_specifiques`) ne sont
posés que si la configuration du modèle les exige. Les chemins écrits dans les artefacts
versionnés passent par `chemin_portable` : aucun chemin absolu de la machine.

Replis (spine, consignés dans `methodes.json`) : si le chargement 4 bits échoue, LoRA bf16
sur `granite-4.0-1b` seulement (`qlora` et `dora` indisponibles) ; si Unsloth échoue,
TRL + PEFT seuls (`qlora-unsloth` indisponible).

`sonder_unsloth` tente le pas équivalent dans l'environnement uv isolé `envs/unsloth/`, en
sous-processus (`uv run --frozen --project envs/unsloth python envs/unsloth/sonde.py`), par
`inference.processus.executer` avec `env_sous_processus()`. Le résultat revient sur la
sortie standard, en une ligne `SLMSP-RESULTAT <json>` : `slmsp` n'importe jamais `unsloth`.

torch, transformers, trl, peft, bitsandbytes et datasets ne sont importés que dans les
fonctions (jamais au chargement du module) : les tests unitaires tournent sans l'extra
`train`, avec une pile simulée injectée.
"""

from __future__ import annotations

import gc
import importlib
import importlib.metadata
import json
import math
import random
import shutil
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from slmsp.core.artefacts import chemin_autorise, lire
from slmsp.core.config import (
    ENV_IMPOSE,
    appliquer_environnement_impose,
    dossier_modeles,
    env_sous_processus,
    racine_projet,
)
from slmsp.core.erreurs import ConfigurationInvalide, SlmspError
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.core.var import dossier_var
from slmsp.inference import processus

METHODES_SONDE: Final = ("qlora", "lora")
"""Méthodes qu'exécute la sonde : QLoRA nf4 (M1) ou LoRA bf16 (M2)."""

PRECISIONS_BASE: Final = ("fp32-kbit", "bf16")
"""Précisions de la base d'un run quantifié (`train.config.PrecisionBase`)."""
PRECISION_LES_DEUX: Final = "les-deux"
"""Option de la sonde : chaque longueur est mesurée dans les deux précisions."""

METHODES: Final = ("qlora", "lora", "dora", "orpo", "rslora", "pissa", "qlora-unsloth")
"""Méthodes et variantes du spine dont `methodes.json` donne la disponibilité."""

SLUG_REPLI_BF16: Final = "granite-4.0-1b"
"""Seul Modèle de base admis en LoRA bf16 quand bitsandbytes échoue (repli du spine)."""

LONGUEURS_DEFAUT: Final = (512, 1024, 2048, 4096)
PAS_DEFAUT: Final = 3
"""Pas mesurés par longueur, après le pas de chauffe."""
PAS_CHAUFFE: Final = 1
GRAINE: Final = 1234

CAPACITE_MIN: Final = (8, 0)
"""Ampere et au-delà : bf16 natif."""
CAPACITE_FP8: Final = (8, 9)
"""Ada et au-delà : FP8 natif (la RTX 3050, en 8.6, ne l'a pas)."""

LORA_RANG: Final = 16
LORA_ALPHA: Final = 32

MARQUEUR_RESULTAT: Final = "SLMSP-RESULTAT "
"""Préfixe de la ligne de résultat JSON du sous-processus Unsloth."""
DOSSIER_TRAVAIL_UNSLOTH: Final = "unsloth"
"""Dossier courant du sous-processus, sous `SLMSP_VAR_DIR` (cache de compilation Unsloth)."""
DELAI_UNSLOTH: Final = 3600.0
"""Le premier `uv run` synchronise `envs/unsloth/` : plusieurs minutes possibles."""

STATUTS_LONGUEUR: Final = ("ok", "oom", "debordement", "erreur", "non-tentee")

FRACTION_DEBORDEMENT: Final = 0.90
"""Part de `total_memory` au-delà de laquelle la VRAM réservée signale un débordement.

Sous Windows (WDDM), `total_memory` compte aussi la mémoire tenue par le bureau et le
pilote : le pilote déborde en mémoire partagée avant que la VRAM réservée par torch
n'atteigne la mémoire totale. Comparer à 100 % laissait passer des longueurs déjà en
débordement (SmolLM3 3B à 2048 : 95 %)."""


class ErreurQuantification(SlmspError):
    """Le chargement en 4 bits (bitsandbytes) a échoué."""


# --- Pile d'entraînement (imports paresseux) ----------------------------------------------


@dataclass
class Pile:
    """Modules de la pile d'entraînement, injectables par les tests."""

    torch: Any
    transformers: Any
    peft: Any
    trl: Any
    datasets: Any
    bitsandbytes: Any = None
    """Importé au premier chargement 4 bits s'il n'est pas fourni."""


def charger_pile() -> Pile:
    """Importe torch, transformers, peft, trl et datasets (lève `ImportError`/`OSError`).

    `appliquer_environnement_impose()` est appelé avant tout import lourd. bitsandbytes
    n'est importé qu'au chargement 4 bits : son absence ne bloque que QLoRA.
    """
    appliquer_environnement_impose()
    noms = ("torch", "transformers", "peft", "trl", "datasets")
    modules = {nom: importlib.import_module(nom) for nom in noms}
    return Pile(**modules)


def versions_pile() -> dict[str, str | None]:
    """Versions installées de la pile (`None` si le paquet manque), sans l'importer."""
    versions: dict[str, str | None] = {}
    for nom in ("torch", "transformers", "trl", "peft", "bitsandbytes", "accelerate", "datasets"):
        try:
            versions[nom] = importlib.metadata.version(nom)
        except importlib.metadata.PackageNotFoundError:
            versions[nom] = None
    return versions


# --- Contrôles ----------------------------------------------------------------------------


@dataclass
class ControleMateriel:
    """Résultat de `controler_materiel` ; `bloquant` vaut le motif d'arrêt, sinon `None`."""

    cuda: bool
    nom: str | None = None
    capacite: tuple[int, int] | None = None
    bf16: bool | None = None
    fp8: bool | None = None
    memoire_totale: int | None = None
    version_cuda: str | None = None
    version_torch: str | None = None
    bloquant: str | None = None

    def ligne(self) -> dict[str, Any]:
        return {
            "cuda": self.cuda,
            "nom": self.nom,
            "capacite": None if self.capacite is None else f"{self.capacite[0]}.{self.capacite[1]}",
            "bf16": self.bf16,
            "fp8": self.fp8,
            "memoire_totale": self.memoire_totale,
            "version_cuda": self.version_cuda,
            "version_torch": self.version_torch,
            "bloquant": self.bloquant,
        }


def controler_materiel(torch: Any) -> ControleMateriel:
    """CUDA disponible, capacité ≥ 8.0 (bf16 natif), bf16 supporté ; FP8 relevé (8.9 et +)."""
    version_torch = str(getattr(torch, "__version__", "")) or None
    version_cuda = getattr(getattr(torch, "version", None), "cuda", None)
    if not torch.cuda.is_available():
        return ControleMateriel(
            cuda=False,
            version_cuda=version_cuda,
            version_torch=version_torch,
            bloquant="CUDA indisponible (torch.cuda.is_available() est faux)",
        )
    capacite = tuple(int(x) for x in torch.cuda.get_device_capability(0))
    proprietes = torch.cuda.get_device_properties(0)
    controle = ControleMateriel(
        cuda=True,
        nom=str(torch.cuda.get_device_name(0)),
        capacite=(capacite[0], capacite[1]),
        bf16=bool(torch.cuda.is_bf16_supported()),
        fp8=capacite >= CAPACITE_FP8,
        memoire_totale=int(proprietes.total_memory),
        version_cuda=version_cuda,
        version_torch=version_torch,
    )
    if capacite < CAPACITE_MIN:
        controle.bloquant = (
            f"capacité CUDA {capacite[0]}.{capacite[1]} inférieure à "
            f"{CAPACITE_MIN[0]}.{CAPACITE_MIN[1]} : bf16 natif absent"
        )
    elif not controle.bf16:
        controle.bloquant = "bf16 non supporté par la carte"
    return controle


def dossier_poids(slug: str, *, racine: str | Path | None = None) -> Path:
    """`<SLMSP_MODELS_DIR>/<slug>/hf/`, validé pour le lecteur `train` (AD-24)."""
    dossier = chemin_autorise(dossier_modeles() / slug / "hf", "train", racine=racine)
    if not dossier.is_dir():
        raise ConfigurationInvalide(
            f"poids absents pour « {slug} » : {dossier} (préparer le modèle par "
            "`slmsp fetch modeles` ; SLMSP_MODELS_DIR pointe le dossier models/)"
        )
    return dossier


def lire_config_modele(dossier: Path, *, racine: str | Path | None = None) -> dict[str, Any]:
    """`config.json` des poids, lu par le lecteur contrôlé `train`."""
    brut = lire(dossier / "config.json", "train", racine=racine)
    try:
        config = json.loads(brut.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigurationInvalide(f"{dossier / 'config.json'} : JSON invalide ({exc})") from None
    if not isinstance(config, dict):
        raise ConfigurationInvalide(f"{dossier / 'config.json'} : objet JSON attendu")
    return config


def _sous_configs(config: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    yield config
    texte = config.get("text_config")
    if isinstance(texte, Mapping):
        yield texte


def exiger_entrainable(config: ConfigModele, slug: str) -> None:
    """Refuse (`ConfigurationInvalide`) un modèle à `entrainable = false` (Bonsai, hybrides
    Gated DeltaNet de la décision D8) : point de contrôle commun à `train run` et à
    `train sonde-env` (avec ou sans `--unsloth`), avant toute lecture des poids."""
    if not config.entrainable:
        raise ConfigurationInvalide(
            f"{slug} : modèle non entraînable (`entrainable = false` dans "
            f"config/modeles/{slug}.toml), évalué sans fine-tuning"
        )


def controler_config_modele(config: Mapping[str, Any], slug: str) -> dict[str, Any]:
    """Refuse (`ConfigurationInvalide`) les poids FP8, une couche Mamba, un encodeur vision.

    Renvoie le résumé des contrôles passés (type de modèle, couches, quantification).
    """
    if "vision_config" in config:
        raise ConfigurationInvalide(
            f"{slug} : modèle multimodal (`vision_config` présent) ; la sonde ne charge pas "
            "l'encodeur vision (Ministral 3 hors sonde)"
        )
    for sous in _sous_configs(config):
        quantification = sous.get("quantization_config")
        if isinstance(quantification, Mapping):
            texte = json.dumps(quantification, sort_keys=True).lower()
            if "fp8" in texte or "float8" in texte or "e4m3" in texte:
                raise ConfigurationInvalide(
                    f"{slug} : poids FP8 (`quantization_config`), non gérés par la carte "
                    "(capacité 8.6) ; préférer le dépôt officiel bf16"
                )
        couches = sous.get("layer_types")
        if isinstance(couches, list) and any("mamba" in str(c).lower() for c in couches):
            raise ConfigurationInvalide(
                f"{slug} : couche Mamba dans `layer_types` (modèle hybride écarté)"
            )
    couches = config.get("layer_types")
    return {
        "model_type": config.get("model_type"),
        "architectures": config.get("architectures"),
        "couches": sorted({str(c) for c in couches}) if isinstance(couches, list) else None,
        "vocab_size": config.get("vocab_size"),
        "torch_dtype": config.get("torch_dtype") or config.get("dtype"),
        "quantization_config": "quantization_config" in config,
        "vision_config": False,
    }


# --- Arguments d'entraînement --------------------------------------------------------------


def _nombre(valeur: Any) -> float | None:
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        return None
    return float(valeur)


def _a_des_experts(config: Mapping[str, Any]) -> bool:
    cles = ("num_local_experts", "num_experts", "n_routed_experts")
    return any((_nombre(config.get(cle)) or 0) > 0 for cle in cles)


def arguments_specifiques(config_modele: Mapping[str, Any]) -> dict[str, Any]:
    """Arguments `SFTConfig` qu'exige l'architecture du modèle, et seulement eux.

    - `loss_type="nll"` si la configuration déclare `logits_scaling` ≠ 1 (Granite) : la
      perte `chunked_nll` par défaut de TRL 1.13 recalcule les logits sans cette mise à
      l'échelle (logits 8 fois trop grands, perte ~70 au lieu de ~13 sur tokens aléatoires).
    - `router_aux_loss_coef=0.0` si la configuration déclare un routeur
      (`output_router_logits` ou `router_aux_loss_coef`) sans aucun expert (Granite 4.0 1B,
      `num_local_experts = 0`) : TRL la prendrait pour un MoE et échouerait.

    Un modèle sans ces particularités (SmolLM3, Qwen) garde les valeurs par défaut de TRL.
    """
    specifiques: dict[str, Any] = {}
    for sous in _sous_configs(config_modele):
        echelle = _nombre(sous.get("logits_scaling"))
        if echelle is not None and echelle != 1.0:
            specifiques["loss_type"] = "nll"
        routeur = "output_router_logits" in sous or "router_aux_loss_coef" in sous
        if routeur and not _a_des_experts(sous):
            specifiques["router_aux_loss_coef"] = 0.0
    return specifiques


def arguments_entrainement(
    dossier_sortie: str | Path,
    *,
    longueur: int,
    pas: int,
    graine: int = GRAINE,
    specifiques: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Arguments `SFTConfig` sûrs : aucun rapport, aucune publication, aucun checkpoint.

    Batch 1, `max_length = longueur` et jeu pré-tokenisé (`skip_prepare_dataset`) : ni
    troncature ni padding. Jamais de `save_total_limit`. `specifiques` (voir
    `arguments_specifiques`) complète les arguments communs sans pouvoir les remplacer.
    """
    communs = _arguments_communs(dossier_sortie, longueur=longueur, pas=pas, graine=graine)
    for cle, valeur in (specifiques or {}).items():
        if cle in communs:
            raise ConfigurationInvalide(f"argument d'entraînement spécifique en conflit : {cle}")
        communs[cle] = valeur
    return communs


def _arguments_communs(
    dossier_sortie: str | Path, *, longueur: int, pas: int, graine: int
) -> dict[str, Any]:
    return dict(
        output_dir=str(dossier_sortie),
        report_to="none",
        push_to_hub=False,
        save_strategy="no",
        max_steps=int(pas),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=2e-4,
        lr_scheduler_type="constant",
        warmup_steps=0,
        logging_steps=1,
        logging_strategy="steps",
        disable_tqdm=True,
        bf16=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_length=int(longueur),
        packing=False,
        padding_free=False,
        dataset_kwargs={"skip_prepare_dataset": True},
        remove_unused_columns=False,
        seed=int(graine),
        data_seed=int(graine),
        dataloader_num_workers=0,
        dataloader_pin_memory=False,
        optim="adamw_torch",
    )


def tokens_aleatoires(
    nombre: int, longueur: int, vocab: int, *, graine: int, exclus: Iterable[int] = ()
) -> list[list[int]]:
    """`nombre` séquences de `longueur` tokens tirés uniformément (graine fixe)."""
    if vocab <= 1:
        raise ValueError(f"vocabulaire trop petit : {vocab}")
    exclus = {int(t) for t in exclus if t is not None}
    tirage = random.Random(graine * 100_003 + longueur)
    sequences = []
    for _ in range(nombre):
        sequence = []
        while len(sequence) < longueur:
            jeton = tirage.randrange(vocab)
            if jeton not in exclus:
                sequence.append(jeton)
        sequences.append(sequence)
    return sequences


# --- Chargement ---------------------------------------------------------------------------


def charger_modele(
    pile: Pile, dossier: Path, methode: str, precision_base: str = "fp32-kbit"
) -> Any:
    """Charge les poids en 4 bits nf4 (`qlora`) ou en bf16 (`lora`), sur le GPU 0.

    `precision_base` ne joue qu'en `qlora` : `fp32-kbit` (cast de `prepare_model_for_kbit_training`)
    ou `bf16` (sans ce cast, `enable_input_require_grads` seul).

    Un échec du chargement 4 bits (bitsandbytes absent ou en panne) lève
    `ErreurQuantification` ; une erreur de mémoire CUDA est propagée telle quelle.
    """
    torch = pile.torch
    transformers = pile.transformers
    arguments: dict[str, Any] = {
        "dtype": torch.bfloat16,
        "device_map": {"": 0},
        "attn_implementation": "sdpa",
        "low_cpu_mem_usage": True,
    }
    if methode == "qlora":
        try:
            if pile.bitsandbytes is None:
                pile.bitsandbytes = importlib.import_module("bitsandbytes")
            arguments["quantization_config"] = transformers.BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
            modele = transformers.AutoModelForCausalLM.from_pretrained(str(dossier), **arguments)
        except torch.cuda.OutOfMemoryError:
            raise
        except Exception as exc:  # bitsandbytes : ImportError, RuntimeError, OSError…
            raise ErreurQuantification(
                f"chargement 4 bits nf4 impossible : {type(exc).__name__} : {exc}"
            ) from exc
        if precision_base == "bf16":
            modele.enable_input_require_grads()
        else:
            modele = pile.peft.prepare_model_for_kbit_training(
                modele,
                use_gradient_checkpointing=True,
                gradient_checkpointing_kwargs={"use_reentrant": False},
            )
    elif methode == "lora":
        modele = transformers.AutoModelForCausalLM.from_pretrained(str(dossier), **arguments)
    else:
        raise ConfigurationInvalide(
            f"méthode de sonde inconnue : {methode!r} (attendu : {', '.join(METHODES_SONDE)})"
        )
    modele.config.use_cache = False
    return modele


def poser_lora(pile: Pile, modele: Any) -> Any:
    """Adaptateur LoRA PEFT (rang 16, alpha 32, toutes les couches linéaires)."""
    config = pile.peft.LoraConfig(
        r=LORA_RANG,
        lora_alpha=LORA_ALPHA,
        lora_dropout=0.0,
        bias="none",
        target_modules="all-linear",
        task_type="CAUSAL_LM",
    )
    return pile.peft.get_peft_model(modele, config)


def charger_tokenizer(pile: Pile, dossier: Path) -> Any:
    tokenizer = pile.transformers.AutoTokenizer.from_pretrained(str(dossier))
    if getattr(tokenizer, "pad_token", None) is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


# --- Mesure par longueur ------------------------------------------------------------------


def _fini(valeur: Any) -> bool:
    return isinstance(valeur, (int, float)) and math.isfinite(float(valeur))


def json_sur(obj: Any) -> Any:
    """Copie de `obj` sérialisable en JSON strict : NaN et infinis deviennent des chaînes."""
    if isinstance(obj, float) and not math.isfinite(obj):
        return str(obj)
    if isinstance(obj, Mapping):
        return {str(cle): json_sur(valeur) for cle, valeur in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_sur(valeur) for valeur in obj]
    return obj


def _liberer(pile: Pile) -> None:
    gc.collect()
    try:
        pile.torch.cuda.empty_cache()
    except Exception:  # noqa: BLE001 - nettoyage au mieux
        pass


def _est_oom(pile: Pile, exc: BaseException) -> bool:
    if isinstance(exc, pile.torch.cuda.OutOfMemoryError):
        return True
    return isinstance(exc, RuntimeError) and "out of memory" in str(exc).lower()


def mesurer_longueur(
    pile: Pile,
    modele: Any,
    tokenizer: Any,
    *,
    longueur: int,
    pas: int,
    graine: int,
    vocab: int,
    dossier_sortie: Path,
    memoire_totale: int,
    specifiques: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Un pas de chauffe puis `pas` pas mesurés de `SFTTrainer` à la longueur `longueur`."""
    torch = pile.torch
    total = PAS_CHAUFFE + pas
    exclus = {
        getattr(tokenizer, "pad_token_id", None),
        getattr(tokenizer, "bos_token_id", None),
        getattr(tokenizer, "eos_token_id", None),
    }
    sequences = tokens_aleatoires(total, longueur, vocab, graine=graine, exclus=exclus)
    jeu = pile.datasets.Dataset.from_dict({"input_ids": sequences})
    arguments = arguments_entrainement(
        dossier_sortie, longueur=longueur, pas=total, graine=graine, specifiques=specifiques
    )

    durees: list[float] = []
    pertes: list[float] = []

    class Chrono(pile.transformers.TrainerCallback):
        debut = 0.0

        def on_step_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            torch.cuda.synchronize()
            self.debut = time.perf_counter()

        def on_step_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            torch.cuda.synchronize()
            durees.append(time.perf_counter() - self.debut)

        def on_log(
            self, args: Any, state: Any, control: Any, logs: Any = None, **kwargs: Any
        ) -> None:
            if logs and "loss" in logs:
                pertes.append(float(logs["loss"]))

    mesure: dict[str, Any] = {"longueur": longueur, "pas": pas, "pas_chauffe": PAS_CHAUFFE}
    entraineur = None
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    try:
        entraineur = pile.trl.SFTTrainer(
            model=modele,
            args=pile.trl.SFTConfig(**arguments),
            train_dataset=jeu,
            processing_class=tokenizer,
            callbacks=[Chrono()],
        )
        entraineur.train()
    except BaseException as exc:
        if not _est_oom(pile, exc):
            if isinstance(exc, Exception):
                mesure.update(statut="erreur", erreur=f"{type(exc).__name__} : {exc}")
                return _completer(pile, mesure, durees, pertes, longueur, memoire_totale)
            raise
        mesure.update(statut="oom", erreur=f"{type(exc).__name__} : {str(exc)[:300]}")
        return _completer(pile, mesure, durees, pertes, longueur, memoire_totale)
    finally:
        del entraineur
        _liberer(pile)
    mesure["statut"] = "ok"
    return _completer(pile, mesure, durees, pertes, longueur, memoire_totale)


def _completer(
    pile: Pile,
    mesure: dict[str, Any],
    durees: list[float],
    pertes: list[float],
    longueur: int,
    memoire_totale: int,
) -> dict[str, Any]:
    torch = pile.torch
    alloue = int(torch.cuda.max_memory_allocated())
    reserve = int(torch.cuda.max_memory_reserved())
    mesurees = durees[PAS_CHAUFFE:]
    duree = sum(mesurees)
    mesure.update(
        perte=pertes[-1] if pertes else None,
        pertes=pertes,
        perte_finie=bool(pertes) and all(_fini(p) for p in pertes),
        max_memory_allocated=alloue,
        max_memory_reserved=reserve,
        memoire_totale=memoire_totale,
        seuil_debordement=seuil_debordement(memoire_totale),
        durees_pas_s=[round(d, 4) for d in durees],
        tokens_par_s=(longueur * len(mesurees) / duree) if mesurees and duree > 0 else None,
    )
    if mesure["statut"] == "ok" and deborde(reserve, memoire_totale):
        mesure["statut"] = "debordement"
    return mesure


def seuil_debordement(memoire_totale: int) -> int:
    """VRAM réservée au-delà de laquelle une mesure est en `debordement` (0 : inconnu)."""
    return int(memoire_totale * FRACTION_DEBORDEMENT) if memoire_totale else 0


def deborde(reserve: Any, memoire_totale: Any) -> bool:
    """VRAM réservée au-delà de `FRACTION_DEBORDEMENT` de la mémoire totale (connue)."""
    if not isinstance(reserve, int) or not isinstance(memoire_totale, int):
        return False
    seuil = seuil_debordement(memoire_totale)
    return seuil > 0 and reserve > seuil


# --- Disponibilité des méthodes -------------------------------------------------------------


def methodes_disponibles(
    *,
    slug: str,
    methode_demandee: str,
    methode_effective: str | None,
    pas_reussi: bool,
    motif_quantification: str | None = None,
    unsloth: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Disponibilité de chaque méthode du spine, et replis appliqués (`methodes.json`).

    Statuts : `verifiee` (un pas fini a tourné), `deduite` (même pile qu'une méthode
    vérifiée), `indisponible` (échec constaté, avec motif), `non-sondee`.
    """
    methodes: dict[str, dict[str, Any]] = {}
    replis: list[str] = []

    def poser(nom: str, statut: str, motif: str) -> None:
        methodes[nom] = {"statut": statut, "motif": motif}

    if not pas_reussi or methode_effective is None:
        for nom in METHODES:
            poser(nom, "non-sondee", "aucun pas d'entraînement réussi")
        if methode_effective is not None:
            poser(methode_effective, "indisponible", "aucun pas d'entraînement réussi")
    elif methode_effective == "qlora":
        poser("qlora", "verifiee", "pas QLoRA nf4 (TRL + PEFT + bitsandbytes) réussi")
        poser("dora", "deduite", "base 4 bits et PEFT (use_dora) vérifiés par QLoRA")
        poser("lora", "deduite", "LoRA bf16 : même pile TRL + PEFT, sans bitsandbytes")
    else:  # lora
        poser("lora", "verifiee", "pas LoRA bf16 (TRL + PEFT) réussi")
        if motif_quantification is not None:
            motif = f"bitsandbytes en échec : {motif_quantification}"
            poser("qlora", "indisponible", motif)
            poser("dora", "indisponible", motif)
            methodes["lora"]["motif"] += f" ; repli limité à {SLUG_REPLI_BF16}"
            replis.append(f"sans bitsandbytes : LoRA bf16 sur {SLUG_REPLI_BF16} seulement")
        else:
            poser("qlora", "non-sondee", "chargement 4 bits non tenté (--methode lora)")
            poser("dora", "non-sondee", "chargement 4 bits non tenté (--methode lora)")
    if pas_reussi and methode_effective is not None:
        for nom in ("orpo", "rslora", "pissa"):
            poser(nom, "deduite", f"TRL + PEFT vérifiés par {methode_effective}")

    if unsloth is None:
        poser("qlora-unsloth", "non-sondee", "sonde Unsloth non demandée (--unsloth)")
    elif unsloth.get("ok"):
        poser("qlora-unsloth", "verifiee", "pas Unsloth réussi dans envs/unsloth")
    else:
        poser("qlora-unsloth", "indisponible", str(unsloth.get("erreur") or "échec Unsloth"))
        replis.append("sans Unsloth : TRL + PEFT seuls (qlora-unsloth indisponible)")

    return {
        "slug": slug,
        "methode_demandee": methode_demandee,
        "methode_effective": methode_effective,
        "methodes": {nom: methodes[nom] for nom in METHODES},
        "disponibles": [n for n in METHODES if methodes[n]["statut"] in ("verifiee", "deduite")],
        "indisponibles": [n for n in METHODES if methodes[n]["statut"] == "indisponible"],
        "replis": replis,
    }


# --- Sonde ----------------------------------------------------------------------------------


@dataclass
class ResultatSonde:
    """Contenu de `sonde.json`, `methodes.json` et statut du run."""

    sonde: dict[str, Any]
    statut: str
    motif: str | None = None
    methode_effective: str | None = None
    motif_quantification: str | None = None
    pas_reussi: bool = False
    replis: list[str] = field(default_factory=list)


def variantes_precision(methode: str, precision_base: str) -> tuple[str, ...]:
    """Précisions à mesurer : `les-deux` en `qlora` ; `lora` (sans cast) n'en mesure qu'une."""
    if precision_base == PRECISION_LES_DEUX:
        return PRECISIONS_BASE if methode == "qlora" else ("fp32-kbit",)
    return (precision_base,)


def _verifier_parametres(
    methode: str, longueurs: Sequence[int], pas: int, precision_base: str = "fp32-kbit"
) -> None:
    if precision_base not in (*PRECISIONS_BASE, PRECISION_LES_DEUX):
        raise ConfigurationInvalide(
            f"precision_base inconnue : {precision_base!r} "
            f"(attendu : {', '.join((*PRECISIONS_BASE, PRECISION_LES_DEUX))})"
        )
    if methode not in METHODES_SONDE:
        raise ConfigurationInvalide(
            f"méthode de sonde inconnue : {methode!r} (attendu : {', '.join(METHODES_SONDE)})"
        )
    if not longueurs or any(int(n) < 8 for n in longueurs):
        raise ConfigurationInvalide("longueurs : au moins une, chacune ≥ 8 tokens")
    if int(pas) < 1:
        raise ConfigurationInvalide("pas : au moins 1 pas mesuré")


def sonder(
    *,
    slug: str,
    dossier: Path,
    config_modele: Mapping[str, Any],
    methode: str = "qlora",
    longueurs: Sequence[int] = LONGUEURS_DEFAUT,
    pas: int = PAS_DEFAUT,
    graine: int = GRAINE,
    precision_base: str = "fp32-kbit",
    dossier_travail: Path,
    pile: Pile | None = None,
    journal: Callable[[str], None] = lambda _m: None,
    racine: Path | None = None,
) -> ResultatSonde:
    """Contrôle le matériel puis mesure QLoRA (ou LoRA bf16) aux longueurs données.

    Ne lève pas pour un échec constaté (CUDA absente, bitsandbytes en panne, OOM) : il est
    consigné dans le résultat, avec le statut du run (`complet`, `degrade`,
    `partiel-erreur`). Les chemins de `sonde` sont portables (`chemin_portable`, relatifs
    à `racine` pour ceux du run).
    """
    _verifier_parametres(methode, longueurs, pas, precision_base)
    appliquer_environnement_impose()
    specifiques = arguments_specifiques(config_modele)
    arguments_affiches = arguments_entrainement(
        dossier_travail,
        longueur=int(longueurs[0]),
        pas=PAS_CHAUFFE + int(pas),
        graine=graine,
        specifiques=specifiques,
    )
    arguments_affiches["output_dir"] = chemin_portable(dossier_travail, racine=racine)
    sonde: dict[str, Any] = {
        "slug": slug,
        "dossier_poids": chemin_portable(dossier, racine=racine),
        "methode_demandee": methode,
        "methode": None,
        "precision_base_demandee": precision_base,
        "longueurs": [int(n) for n in longueurs],
        "pas": int(pas),
        "pas_chauffe": PAS_CHAUFFE,
        "graine": int(graine),
        "donnees": "tokens aléatoires (graine fixe), aucune donnée réelle",
        "versions": versions_pile(),
        "controles_modele": controler_config_modele(config_modele, slug),
        "lora": {"r": LORA_RANG, "alpha": LORA_ALPHA, "target_modules": "all-linear"},
        "env_impose": dict(ENV_IMPOSE),
        "arguments_entrainement": arguments_affiches,
        "arguments_specifiques": specifiques,
        "fraction_debordement": FRACTION_DEBORDEMENT,
        "mesures": [],
        "replis": [],
    }
    if pile is None:
        try:
            pile = charger_pile()
        except (ImportError, OSError) as exc:
            motif = f"pile d'entraînement indisponible : {type(exc).__name__} : {exc}"
            sonde["erreur"] = motif
            return ResultatSonde(sonde=sonde, statut="partiel-erreur", motif=motif)

    materiel = controler_materiel(pile.torch)
    sonde["controles_materiel"] = materiel.ligne()
    if materiel.bloquant is not None:
        sonde["erreur"] = materiel.bloquant
        return ResultatSonde(sonde=sonde, statut="partiel-erreur", motif=materiel.bloquant)

    effective = methode
    motif_quantification: str | None = None
    replis: list[str] = []
    variantes = variantes_precision(methode, precision_base)
    sonde["precisions_base"] = list(variantes)
    modele = None
    try:
        for variante in variantes:
            if effective != methode:  # repli LoRA bf16 : la précision de la base n'a plus d'objet
                break
            journal(f"chargement de {slug} ({methode}, base {variante})")
            try:
                modele = charger_modele(pile, dossier, methode, variante)
            except ErreurQuantification as exc:
                motif_quantification = str(exc)
                sonde["erreur_quantification"] = motif_quantification
                if slug != SLUG_REPLI_BF16:
                    motif = f"{motif_quantification} ; repli LoRA bf16 réservé à {SLUG_REPLI_BF16}"
                    sonde["erreur"] = motif
                    return ResultatSonde(
                        sonde=sonde,
                        statut="partiel-erreur",
                        motif=motif,
                        motif_quantification=motif_quantification,
                    )
                effective = "lora"
                replis.append(f"sans bitsandbytes : LoRA bf16 sur {SLUG_REPLI_BF16} seulement")
                journal(f"repli : {replis[-1]}")
                modele = charger_modele(pile, dossier, "lora")
            sonde["methode"] = effective
            modele = poser_lora(pile, modele)
            tokenizer = charger_tokenizer(pile, dossier)
            vocab = int(config_modele.get("vocab_size") or len(tokenizer))
            vocab = min(vocab, len(tokenizer)) if len(tokenizer) else vocab
            arret = False
            for longueur in longueurs:
                if arret:
                    sonde["mesures"].append(
                        {
                            "longueur": int(longueur),
                            "statut": "non-tentee",
                            "precision_base": variante,
                        }
                    )
                    continue
                journal(
                    f"longueur {longueur} ({variante}) : {pas} pas après "
                    f"{PAS_CHAUFFE} pas de chauffe"
                )
                mesure = mesurer_longueur(
                    pile,
                    modele,
                    tokenizer,
                    longueur=int(longueur),
                    pas=int(pas),
                    graine=int(graine),
                    vocab=vocab,
                    dossier_sortie=dossier_travail,
                    memoire_totale=materiel.memoire_totale or 0,
                    specifiques=specifiques,
                )
                mesure["precision_base"] = variante
                sonde["mesures"].append(mesure)
                journal(
                    f"longueur {longueur} ({variante}) : {mesure['statut']}, "
                    f"perte {mesure.get('perte')}, "
                    f"VRAM réservée {mesure.get('max_memory_reserved')}"
                )
                arret = mesure["statut"] != "ok"
            modele = None
            _liberer(pile)
    except BaseException as exc:
        if isinstance(exc, Exception) and _est_oom(pile, exc):
            motif = f"mémoire GPU insuffisante au chargement : {type(exc).__name__}"
            sonde["erreur"] = motif
            return ResultatSonde(sonde=sonde, statut="partiel-erreur", motif=motif)
        raise
    finally:
        del modele
        _liberer(pile)

    reussies = [m for m in sonde["mesures"] if m.get("statut") == "ok" and m.get("perte_finie")]
    sonde["longueur_max_ok"] = max((m["longueur"] for m in reussies), default=None)
    sonde["longueur_max_ok_par_precision"] = {
        v: max((m["longueur"] for m in reussies if m.get("precision_base") == v), default=None)
        for v in variantes
    }
    sonde["replis"] = replis
    pas_reussi = bool(reussies)
    if not pas_reussi:
        motif = "aucun pas d'entraînement réussi avec une perte finie"
        sonde["erreur"] = motif
        statut, motif_run = "partiel-erreur", motif
    elif replis:
        statut, motif_run = "degrade", "; ".join(replis)
    else:
        statut, motif_run = "complet", None
    return ResultatSonde(
        sonde=sonde,
        statut=statut,
        motif=motif_run,
        methode_effective=effective,
        motif_quantification=motif_quantification,
        pas_reussi=pas_reussi,
        replis=replis,
    )


# --- Unsloth (sous-processus isolé) ----------------------------------------------------------


def projet_unsloth() -> Path:
    """`<racine du projet>/envs/unsloth/`."""
    return racine_projet() / "envs" / "unsloth"


def commande_unsloth(entree: Path, *, uv: str | None = None) -> list[str]:
    """`uv run --frozen --project envs/unsloth python envs/unsloth/sonde.py <entree>`.

    `--frozen` : la commande tourne sous `gpu.lock` ; uv utilise `envs/unsloth/uv.lock`
    tel quel, sans le résoudre de nouveau ni le réécrire (pas de mise à jour silencieuse
    des versions ni de modification d'un fichier versionné pendant la mesure).
    """
    executable = uv or shutil.which("uv")
    if not executable:
        raise FileNotFoundError("exécutable uv introuvable dans le PATH")
    projet = projet_unsloth()
    return [
        executable,
        "run",
        "--frozen",
        "--project",
        str(projet),
        "python",
        str(projet / "sonde.py"),
        str(entree),
    ]


def lire_resultat_unsloth(sortie: str) -> dict[str, Any] | None:
    """Dernière ligne `SLMSP-RESULTAT <json>` de la sortie du sous-processus."""
    for ligne in reversed(sortie.splitlines()):
        ligne = ligne.strip()
        if ligne.startswith(MARQUEUR_RESULTAT):
            try:
                resultat = json.loads(ligne[len(MARQUEUR_RESULTAT) :])
            except json.JSONDecodeError:
                return None
            return resultat if isinstance(resultat, dict) else None
    return None


def entree_unsloth(
    *,
    dossier: Path,
    dossier_sortie: Path,
    longueur: int,
    pas: int,
    graine: int,
    vocab: int,
    specifiques: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Configuration JSON passée au script `envs/unsloth/sonde.py`.

    Elle contient des chemins absolus (le sous-processus en a besoin) : elle est écrite
    sous `SLMSP_VAR_DIR`, jamais telle quelle dans un run versionné (voir `entree_portable`).
    """
    return {
        "dossier_poids": str(dossier),
        "dossier_sortie": str(dossier_sortie),
        "longueur": int(longueur),
        "pas": int(pas),
        "pas_chauffe": PAS_CHAUFFE,
        "graine": int(graine),
        "vocab": int(vocab),
        "lora": {"r": LORA_RANG, "alpha": LORA_ALPHA},
        "arguments_specifiques": dict(specifiques or {}),
    }


def entree_portable(entree: Mapping[str, Any], *, racine: Path | None = None) -> dict[str, Any]:
    """Copie de `entree_unsloth` sans chemin absolu, pour le run versionné."""
    copie = dict(entree)
    for cle in ("dossier_poids", "dossier_sortie"):
        if cle in copie:
            copie[cle] = chemin_portable(copie[cle], racine=racine)
    return copie


def dossier_travail_unsloth() -> Path:
    """`<SLMSP_VAR_DIR>/unsloth/` : dossier courant du sous-processus et de son entrée."""
    return dossier_var() / DOSSIER_TRAVAIL_UNSLOTH


# --- Chemins portables ------------------------------------------------------------------------


def _relatif(chemin: Path, base: Path) -> str | None:
    try:
        return chemin.relative_to(base).as_posix()
    except ValueError:
        return None


def chemin_portable(chemin: str | Path, *, racine: Path | None = None) -> str:
    """Chemin sans préfixe propre à la machine, pour un artefact versionné.

    Dans l'ordre : `$SLMSP_MODELS_DIR/...` (poids), `$SLMSP_VAR_DIR/...` (état machine),
    relatif à `racine` (le dossier des runs), puis relatif à la racine du projet. Hors de
    ces dossiers, seul le nom du fichier est gardé.
    """
    cible = Path(chemin).resolve()
    bases: list[tuple[Path, str]] = [
        (dossier_modeles(), "$SLMSP_MODELS_DIR"),
        (dossier_var().resolve(), "$SLMSP_VAR_DIR"),
    ]
    if racine is not None:
        bases.append((Path(racine).resolve(), ""))
    bases.append((racine_projet(), ""))
    for base, prefixe in bases:
        relatif = _relatif(cible, base)
        if relatif is None:
            continue
        if prefixe:
            return prefixe if relatif in ("", ".") else f"{prefixe}/{relatif}"
        return relatif or "."
    return cible.name


def commande_portable(arguments: Sequence[str], *, racine: Path | None = None) -> list[str]:
    """Commande sans chemin absolu : nom de l'exécutable, chemins rendus portables."""
    portable: list[str] = []
    for position, argument in enumerate(arguments):
        if position == 0:
            portable.append(Path(argument).name)
        elif Path(argument).is_absolute():
            portable.append(chemin_portable(argument, racine=racine))
        else:
            portable.append(argument)
    return portable


def sonder_unsloth(
    entree: Path,
    *,
    journal: Path,
    delai: float = DELAI_UNSLOTH,
    executer: Callable[..., tuple[int, str]] | None = None,
    racine: Path | None = None,
) -> dict[str, Any]:
    """Tente le pas Unsloth en sous-processus ; ne lève pas (échec → `ok` faux, `erreur`).

    Le résultat ne contient que des chemins portables (`chemin_portable`).
    """
    executer = executer or processus.executer
    resultat: dict[str, Any] = {
        "ok": False,
        "entree": chemin_portable(entree, racine=racine),
        "journal": chemin_portable(journal, racine=racine),
    }
    try:
        arguments = commande_unsloth(entree)
    except FileNotFoundError as exc:
        resultat["erreur"] = str(exc)
        return resultat
    resultat["commande"] = commande_portable(arguments, racine=racine)
    # Unsloth écrit `unsloth_compiled_cache/` dans le dossier courant : hors du dépôt.
    travail = dossier_travail_unsloth()
    travail.mkdir(parents=True, exist_ok=True)
    resultat["cwd"] = chemin_portable(travail, racine=racine)
    debut = time.monotonic()
    try:
        code, sortie = executer(
            arguments,
            delai=delai,
            role="unsloth-sonde",
            journal=journal,
            env=env_sous_processus(),
            cwd=travail,
        )
    except Exception as exc:  # noqa: BLE001 - échec consigné comme repli
        resultat["erreur"] = f"{type(exc).__name__} : {str(exc)[-2000:]}"
        resultat["duree_s"] = round(time.monotonic() - debut, 1)
        return resultat
    resultat["duree_s"] = round(time.monotonic() - debut, 1)
    resultat["code"] = code
    sous = lire_resultat_unsloth(sortie)
    if sous is not None:
        resultat["resultat"] = sous
        resultat["debordement"] = deborde(
            sous.get("max_memory_reserved"), sous.get("memoire_totale")
        )
    if code == 0 and sous is not None and sous.get("ok"):
        resultat["ok"] = True
    else:
        detail = (sous or {}).get("erreur") if sous else None
        resultat["erreur"] = detail or (
            f"code de sortie {code} ; fin de la sortie : {sortie[-1500:].strip()}"
        )
    return resultat


__all__ = [
    "FRACTION_DEBORDEMENT",
    "GRAINE",
    "LONGUEURS_DEFAUT",
    "METHODES",
    "METHODES_SONDE",
    "PAS_DEFAUT",
    "SLUG_REPLI_BF16",
    "ControleMateriel",
    "ErreurQuantification",
    "Pile",
    "ResultatSonde",
    "arguments_entrainement",
    "arguments_specifiques",
    "charger_modele",
    "charger_pile",
    "chemin_portable",
    "commande_portable",
    "commande_unsloth",
    "controler_config_modele",
    "controler_materiel",
    "deborde",
    "dossier_poids",
    "dossier_travail_unsloth",
    "entree_portable",
    "exiger_entrainable",
    "entree_unsloth",
    "json_sur",
    "lire_config_modele",
    "lire_resultat_unsloth",
    "mesurer_longueur",
    "methodes_disponibles",
    "projet_unsloth",
    "seuil_debordement",
    "sonder",
    "sonder_unsloth",
    "tokens_aleatoires",
]
