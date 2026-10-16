"""Entraînement QLoRA Unsloth (story 10.5), dans l'environnement isolé.

Appel : `uv run --frozen --project envs/unsloth python envs/unsloth/entrainer.py <entree.json>`,
par `slmsp.train.unsloth`, avec `env_sous_processus()`. Aucune dépendance sur `slmsp`.

L'entrée JSON donne `dossier_poids`, `jeu` (JSON `{"pad_token_id", "exemples": [{"input_ids",
"labels"}]}` pré-tokenisé par `slmsp.train.masque`, jamais recalculé ici), `dossier_adaptateur`,
`longueur`, `graine`, `lora` (`r`, `alpha`, `dropout`), `checkpointing` (`true` ou `"unsloth"`),
`pas_chauffe` et `arguments` (arguments `SFTConfig` complets, construits par le parent).
Le script charge les poids locaux en 4 bits, pose LoRA, entraîne avec `trl.SFTTrainer` et le
collateur à labels, sauvegarde l'adaptateur puis écrit une ligne `SLMSP-RESULTAT <json>` (ASCII)
sur la sortie standard : coûts bruts, pertes, quantification réellement appliquée, versions.
Code de sortie : 0 si l'adaptateur est sauvegardé avec des pertes finies, 1 sinon.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
import traceback
from importlib import metadata
from pathlib import Path
from typing import Any

MARQUEUR = "SLMSP-RESULTAT "
IGNORE = -100

ENV_HORS_LIGNE = {
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "WANDB_MODE": "disabled",
    "DO_NOT_TRACK": "1",
    "UNSLOTH_DISABLE_STATISTICS": "1",
}


def versions() -> dict[str, str | None]:
    resultat: dict[str, str | None] = {}
    for nom in ("unsloth", "unsloth_zoo", "torch", "transformers", "trl", "peft", "bitsandbytes"):
        try:
            resultat[nom] = metadata.version(nom)
        except metadata.PackageNotFoundError:
            resultat[nom] = None
    return resultat


class Collateur:
    """Complète à droite : `pad_id` pour les ids, `IGNORE` pour les labels, masque 0.

    Compte les tokens hors padding vus (`tokens`), pour le débit (FR-33).
    """

    def __init__(self, pad_id: int, torch: Any) -> None:
        self.pad_id = pad_id
        self.torch = torch
        self.tokens = 0

    def __call__(self, exemples: list[dict[str, list[int]]]) -> dict[str, Any]:
        longueur = max(len(e["input_ids"]) for e in exemples)
        lots: dict[str, list[list[int]]] = {"input_ids": [], "labels": [], "attention_mask": []}
        for e in exemples:
            n = len(e["input_ids"])
            manque = longueur - n
            self.tokens += n
            lots["input_ids"].append(list(e["input_ids"]) + [self.pad_id] * manque)
            lots["labels"].append(list(e["labels"]) + [IGNORE] * manque)
            lots["attention_mask"].append([1] * n + [0] * manque)
        return {k: self.torch.tensor(v, dtype=self.torch.long) for k, v in lots.items()}


def lire_jeu(chemin: str | Path) -> tuple[list[dict[str, list[int]]], int]:
    """Exemples pré-tokenisés (`input_ids`, `labels` de même longueur) et id du padding."""
    donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
    exemples = donnees["exemples"]
    if not exemples:
        raise ValueError("jeu pré-tokenisé vide")
    for numero, e in enumerate(exemples):
        if len(e["input_ids"]) != len(e["labels"]) or not e["input_ids"]:
            raise ValueError(f"exemple {numero} : input_ids et labels de longueurs différentes")
    return exemples, int(donnees["pad_token_id"])


def debit(
    points: list[tuple[float, int]], debut: float, pas_chauffe: int
) -> tuple[int | None, float | None, float | None]:
    """(tokens mesurés, durée mesurée, tokens/s) après `pas_chauffe` pas.

    `points` : (instant, tokens cumulés hors padding) à la fin de chaque pas ; `debut` :
    instant du début de l'entraînement. Sans pas au-delà de la chauffe : tout à `None`.
    """
    if len(points) <= pas_chauffe:
        return None, None, None
    ref = points[pas_chauffe - 1] if pas_chauffe > 0 else (debut, 0)
    fin = points[-1]
    tokens, duree = fin[1] - ref[1], fin[0] - ref[0]
    return tokens, duree, (tokens / duree if duree > 0 else None)


def quantification(modele: Any) -> dict[str, Any]:
    """Quantification réellement appliquée (`config.quantization_config`), en JSON."""
    config = getattr(getattr(modele, "config", None), "quantization_config", None)
    if config is None:
        return {}
    donnees = config.to_dict() if hasattr(config, "to_dict") else dict(config)
    cles = (
        "load_in_4bit",
        "bnb_4bit_quant_type",
        "bnb_4bit_use_double_quant",
        "bnb_4bit_compute_dtype",
    )
    return {c: str(donnees[c]) if c.endswith("dtype") else donnees[c] for c in cles if c in donnees}


def entrainer(entree: dict[str, Any]) -> dict[str, Any]:
    os.environ.update(ENV_HORS_LIGNE)
    # Unsloth s'importe avant transformers, trl et peft (il les modifie à l'import).
    import unsloth  # noqa: F401, I001
    from unsloth import FastLanguageModel

    import torch
    from datasets import Dataset
    from transformers import TrainerCallback, set_seed
    from trl import SFTConfig, SFTTrainer

    exemples, pad_id = lire_jeu(entree["jeu"])
    longueur = int(entree["longueur"])
    graine = int(entree["graine"])
    chauffe = int(entree.get("pas_chauffe", 10))
    lora = entree.get("lora", {})
    resultat: dict[str, Any] = {"exemples": len(exemples), "pas_chauffe": chauffe}

    set_seed(graine)  # avant le chargement et l'adaptateur, comme M1 (W4.4)
    modele, tokenizer = FastLanguageModel.from_pretrained(
        model_name=entree["dossier_poids"],
        max_seq_length=longueur,
        dtype=torch.bfloat16,
        load_in_4bit=True,
        local_files_only=True,
    )
    resultat["quantification"] = quantification(modele)
    cibles = sorted(
        {
            nom.rsplit(".", 1)[-1]
            for nom, module in modele.named_modules()
            if isinstance(module, torch.nn.Linear) and "lm_head" not in nom
        }
    )
    # W4.5 : `True` (checkpointing standard) par défaut ; "unsloth" déporte les activations
    # en RAM CPU et fausse la VRAM mesurée.
    modele = FastLanguageModel.get_peft_model(
        modele,
        r=int(lora.get("r", 16)),
        lora_alpha=int(lora.get("alpha", 32)),
        lora_dropout=float(lora.get("dropout", 0.0)),
        bias="none",
        target_modules=cibles,
        use_gradient_checkpointing=entree.get("checkpointing", True),
        random_state=graine,
    )
    resultat["target_modules"] = cibles
    texte = getattr(tokenizer, "tokenizer", tokenizer)
    collateur = Collateur(pad_id, torch)
    points: list[tuple[float, int]] = []
    pertes: list[dict[str, Any]] = []
    debut_entrainement = [0.0, 0.0]

    class Chrono(TrainerCallback):
        def on_train_begin(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            torch.cuda.synchronize()
            debut_entrainement[0] = time.perf_counter()
            debut_entrainement[1] = time.time()

        def on_step_end(self, args: Any, state: Any, control: Any, **kwargs: Any) -> None:
            torch.cuda.synchronize()
            points.append((time.perf_counter(), collateur.tokens))

        def on_log(
            self, args: Any, state: Any, control: Any, logs: Any = None, **kwargs: Any
        ) -> None:
            if logs and "loss" in logs:
                pertes.append({"pas": int(state.global_step), "perte": float(logs["loss"])})

    arguments = SFTConfig(**dict(entree["arguments"]))
    torch.cuda.reset_peak_memory_stats()
    entraineur = SFTTrainer(
        model=modele,
        args=arguments,
        train_dataset=Dataset.from_list(exemples),
        data_collator=collateur,
        processing_class=texte,
        callbacks=[Chrono()],
    )
    entraineur.train()
    fin_perf, fin_epoch = time.perf_counter(), time.time()
    perte_finie = bool(pertes) and all(math.isfinite(p["perte"]) for p in pertes)
    if perte_finie:  # jamais d'adaptateur pour une perte NaN : il bloquerait la reprise
        entraineur.model.save_pretrained(str(entree["dossier_adaptateur"]))

    tokens, duree_mesuree, rapport = debit(points, debut_entrainement[0], chauffe)
    resultat.update(
        pas=len(points),
        duree_s=fin_perf - debut_entrainement[0],
        debut_epoch=debut_entrainement[1],
        fin_epoch=fin_epoch,
        tokens_total=collateur.tokens,
        tokens_mesures=tokens,
        duree_mesuree_s=duree_mesuree,
        debit_tokens_par_s=rapport,
        pertes=pertes,
        perte_finie=perte_finie,
        max_memory_allocated=int(torch.cuda.max_memory_allocated()),
        max_memory_reserved=int(torch.cuda.max_memory_reserved()),
        memoire_totale=int(torch.cuda.get_device_properties(0).total_memory),
    )
    resultat["ok"] = bool(resultat["perte_finie"])
    if not resultat["ok"]:
        resultat["erreur"] = "perte non finie ou absente"
    return resultat


def principal(arguments: list[str]) -> int:
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8", errors="replace")  # W4.6 : pas de cp1252
    resultat: dict[str, Any] = {"ok": False}
    try:
        if len(arguments) != 1:
            raise ValueError("usage : entrainer.py <entree.json>")
        entree = json.loads(Path(arguments[0]).read_text(encoding="utf-8"))
        resultat.update(entrainer(entree))
    except BaseException as exc:  # tout échec est rendu en JSON au parent
        resultat["ok"] = False
        resultat["erreur"] = f"{type(exc).__name__} : {str(exc)[:2000]}"
        resultat["trace"] = traceback.format_exc()[-4000:]
    resultat["versions"] = versions()
    print(MARQUEUR + json.dumps(resultat, ensure_ascii=True), flush=True)
    return 0 if resultat.get("ok") else 1


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
