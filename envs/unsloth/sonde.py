"""Sonde Unsloth (story 10.1) : un pas QLoRA équivalent, dans l'environnement isolé.

Appel : `uv run --frozen --project envs/unsloth python envs/unsloth/sonde.py <entree.json>`,
par `slmsp.train.environnement.sonder_unsloth`, avec `env_sous_processus()`.

L'entrée JSON donne `dossier_poids`, `dossier_sortie` (dossier de travail de
l'entraîneur, dans le run), `longueur`, `pas`, `pas_chauffe`, `graine`, `vocab`,
`lora` (`r`, `alpha`) et `arguments_specifiques` (arguments `SFTConfig` qu'exige
l'architecture du modèle, calculés par `slmsp.train.environnement.arguments_specifiques`).
Le script charge les poids locaux en 4 bits par `FastLanguageModel`, pose LoRA, exécute
`pas_chauffe + pas` pas de `trl.SFTTrainer` sur des **tokens aléatoires** (graine fixe,
aucune donnée réelle), puis écrit une seule ligne `SLMSP-RESULTAT <json>` sur la sortie
standard : `ok`, perte, VRAM maximale, tokens/s après la chauffe, versions, ou `erreur` et
la fin de la trace. Code de sortie : 0 si le pas a réussi avec une perte finie, 1 sinon.

Aucun rapport (`report_to="none"`), aucune publication, aucun checkpoint ; Hugging Face
et Unsloth sont mis hors ligne et sans statistiques.
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
import time
import traceback
from importlib import metadata
from pathlib import Path
from typing import Any

MARQUEUR = "SLMSP-RESULTAT "

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


def tokens_aleatoires(
    nombre: int, longueur: int, vocab: int, graine: int, exclus: set[int]
) -> list[list[int]]:
    tirage = random.Random(graine * 100_003 + longueur)
    sequences = []
    for _ in range(nombre):
        sequence: list[int] = []
        while len(sequence) < longueur:
            jeton = tirage.randrange(vocab)
            if jeton not in exclus:
                sequence.append(jeton)
        sequences.append(sequence)
    return sequences


def sonder(entree: dict[str, Any]) -> dict[str, Any]:
    os.environ.update(ENV_HORS_LIGNE)
    # Unsloth s'importe avant transformers, trl et peft (il les modifie à l'import).
    import unsloth  # noqa: F401, I001
    from unsloth import FastLanguageModel

    import torch
    from datasets import Dataset
    from transformers import TrainerCallback
    from trl import SFTConfig, SFTTrainer

    longueur = int(entree["longueur"])
    pas = int(entree["pas"])
    chauffe = int(entree.get("pas_chauffe", 1))
    graine = int(entree["graine"])
    lora = entree.get("lora", {})
    resultat: dict[str, Any] = {"longueur": longueur, "pas": pas, "pas_chauffe": chauffe}

    modele, tokenizer = FastLanguageModel.from_pretrained(
        model_name=entree["dossier_poids"],
        max_seq_length=longueur,
        dtype=torch.bfloat16,
        load_in_4bit=True,
        local_files_only=True,
    )
    cibles = sorted(
        {
            nom.rsplit(".", 1)[-1]
            for nom, module in modele.named_modules()
            if isinstance(module, torch.nn.Linear) and "lm_head" not in nom
        }
    )
    modele = FastLanguageModel.get_peft_model(
        modele,
        r=int(lora.get("r", 16)),
        lora_alpha=int(lora.get("alpha", 32)),
        lora_dropout=0.0,
        bias="none",
        target_modules=cibles,
        use_gradient_checkpointing="unsloth",
        random_state=graine,
    )
    resultat["target_modules"] = cibles
    texte = getattr(tokenizer, "tokenizer", tokenizer)
    if getattr(texte, "pad_token", None) is None:
        texte.pad_token = texte.eos_token
    vocab = int(entree.get("vocab") or 0) or len(texte)
    vocab = min(vocab, len(texte))
    exclus = {
        t
        for t in (texte.pad_token_id, texte.bos_token_id, texte.eos_token_id)
        if isinstance(t, int)
    }
    sequences = tokens_aleatoires(chauffe + pas, longueur, vocab, graine, exclus)
    jeu = Dataset.from_dict({"input_ids": sequences})

    durees: list[float] = []
    pertes: list[float] = []

    class Chrono(TrainerCallback):
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

    arguments = SFTConfig(
        output_dir=str(entree["dossier_sortie"]),
        report_to="none",
        push_to_hub=False,
        save_strategy="no",
        max_steps=chauffe + pas,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=2e-4,
        lr_scheduler_type="constant",
        warmup_steps=0,
        logging_steps=1,
        disable_tqdm=True,
        bf16=True,
        max_length=longueur,
        packing=False,
        padding_free=False,
        dataset_kwargs={"skip_prepare_dataset": True},
        remove_unused_columns=False,
        seed=graine,
        data_seed=graine,
        dataloader_num_workers=0,
        dataloader_pin_memory=False,
        **dict(entree.get("arguments_specifiques") or {}),
    )
    torch.cuda.reset_peak_memory_stats()
    entraineur = SFTTrainer(
        model=modele,
        args=arguments,
        train_dataset=jeu,
        processing_class=texte,
        callbacks=[Chrono()],
    )
    entraineur.train()

    mesurees = durees[chauffe:]
    duree = sum(mesurees)
    resultat.update(
        perte=pertes[-1] if pertes else None,
        pertes=pertes,
        perte_finie=bool(pertes) and all(math.isfinite(p) for p in pertes),
        max_memory_allocated=int(torch.cuda.max_memory_allocated()),
        max_memory_reserved=int(torch.cuda.max_memory_reserved()),
        memoire_totale=int(torch.cuda.get_device_properties(0).total_memory),
        durees_pas_s=[round(d, 4) for d in durees],
        tokens_par_s=(longueur * len(mesurees) / duree) if mesurees and duree > 0 else None,
    )
    resultat["ok"] = bool(resultat["perte_finie"])
    if not resultat["ok"]:
        resultat["erreur"] = "perte non finie ou absente"
    return resultat


def principal(arguments: list[str]) -> int:
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8", errors="replace")
    resultat: dict[str, Any] = {"ok": False}
    try:
        if len(arguments) != 1:
            raise ValueError("usage : sonde.py <entree.json>")
        entree = json.loads(Path(arguments[0]).read_text(encoding="utf-8"))
        resultat.update(sonder(entree))
    except BaseException as exc:  # tout échec est rendu en JSON au parent
        resultat["ok"] = False
        resultat["erreur"] = f"{type(exc).__name__} : {str(exc)[:2000]}"
        resultat["trace"] = traceback.format_exc()[-4000:]
    resultat["versions"] = versions()
    print(MARQUEUR + json.dumps(resultat, ensure_ascii=True), flush=True)  # W4.6 : pas de cp1252
    return 0 if resultat.get("ok") else 1


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
