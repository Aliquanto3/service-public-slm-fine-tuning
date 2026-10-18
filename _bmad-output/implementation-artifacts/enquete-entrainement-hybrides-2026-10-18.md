# Spike : QLoRA des Qwen3.5 hybrides et contexte long sur le portable (2026-10-18)

Matériel : RTX 3060 Laptop 6 Gio, pilote 617.42, Windows 11, WSL2 Ubuntu (noyau 6.6.87, 15 Gio de RAM).
Sonde : `sonde.py` (ce dossier). Elle imite `slmsp train sonde-env` : nf4 avec double quantification et calcul en bf16, LoRA r16/α32 sans dropout, SFTTrainer de TRL, batch 1, gradient checkpointing non réentrant, `adamw_torch`, lr 2e-4, tokens aléatoires (graine 1234), 1 pas de chauffe puis 3 pas mesurés, un processus par longueur, statut `debordement` au-delà de 90 % de la VRAM.
Pile identique partout, celle de `uv.lock` : torch 2.14.1+cu130, transformers 5.17.0, peft 0.21.2, trl 1.13.0, bitsandbytes 0.50.2, accelerate 1.15.0, datasets 5.1.0.
Résultats bruts : `resultats/*.json` et `resultats/*.log`. Aucun fichier des dépôts ni de `models/` n'a été modifié.

## Constat principal (il vaut aussi pour MiniCPM5 et pour Windows)

Ce n'est pas Linux qui fait gagner la mémoire. C'est `peft.prepare_model_for_kbit_training`, appelé par la sonde (`environnement.charger_modele`) et par `methodes.py`, qui coûte cher : il convertit en fp32 tout ce qui n'est pas quantifié (embeddings de 248k×2048 ou de 130k×2048, normes, conv1d). Les activations passent alors elles aussi en fp32.
Sans cet appel (variante `--sans-prepare`, qui garde seulement `enable_input_require_grads()` et le gradient checkpointing, avec une base en bf16), la VRAM baisse de 1,5 à 2,5 Gio. Les pertes restent identiques à 0,01 près (par exemple 14,63 → 12,99 dans les deux cas).

## Piste 1 : WSL2 avec les noyaux Linux

- Installé en espace utilisateur (sans sudo, qui demande un mot de passe) : uv 0.13.1, venv Python 3.12.15 dans `~/slmsp-spike/.venv`, la pile du lock plus torchvision 0.29.1, flash-linear-attention et fla-core 0.5.2, liger-kernel 0.8.4 et kernels 0.16.2.
- WSL n'a ni gcc ni nvcc. Triton a besoin d'un compilateur C pour son lanceur : `ziglang` 0.17 (pip) fait l'affaire, avec la variable `CC=~/slmsp-spike/bin/cc`, un script qui appelle `python -m ziglang cc`.
- `causal-conv1d` n'a pas pu être installé : sa compilation exige nvcc, et aucune roue n'existe pour torch 2.14. Le repli torch de la conv1d coûte peu.
- Les noyaux du hub HF (`use_kernels=True`, mamba-ssm v2) chargent, mais ils sont plus lents (835 t/s contre 1104 à 4096) : écartés.
- Le chemin rapide est contrôlé de deux façons. D'abord par l'avertissement de transformers « `X` is falling back to its reference PyTorch implementation » : avec fla, seul `causal_conv1d_fn` le déclenche ; sans fla, `chunk_gated_delta_rule` le déclenche aussi. Ensuite par la fermeture du décorateur (`implementation = fla.ops.gated_delta_rule.chunk.chunk_gated_delta_rule`) et par l'écart de débit.
- Le premier pas compile les noyaux Triton : 80 à 100 s une fois, puis le cache sert.

Qwen3.5-2B est chargé par `AutoModelForImageTextToText` (classe `Qwen3_5ForConditionalGeneration`), avec sa tour vision. Le LoRA cible seulement `.*language_model.*` : 16,8 M paramètres entraînables, 0 paramètre de la tour vision (168 M) entraînable.

| Modèle | Variante | Longueur | VRAM réservée | Tokens/s | Statut |
|---|---|---|---|---|---|
| Qwen3.5-2B | fla, avec cast fp32 | 1024 | 5,78 | 658 | débordement |
| Qwen3.5-2B | fla, avec cast fp32 | 2048 | 6,01 | 270 | débordement |
| Qwen3.5-2B | fla, avec cast fp32 | 4096 | 6,56 | 82 | débordement |
| Qwen3.5-2B | **fla, sans cast** | 1024 | 3,48 | 1006 | ok |
| Qwen3.5-2B | **fla, sans cast** | 2048 | 3,39 | 1074 | ok |
| Qwen3.5-2B | **fla, sans cast** | 4096 | 3,68 | 1104 | ok |
| Qwen3.5-2B | **fla, sans cast** | 8192 | 4,34 | 1090 | ok |
| Qwen3.5-2B | fla, sans cast | 16384 | 6,69 | 328 | débordement |
| Qwen3.5-2B | repli torch, sans cast | 1024 / 2048 / 4096 | 3,26 / 3,54 / 4,07 | 392 / 385 / 551 | ok |
| Qwen3.5-0.8B | fla, sans cast | 4096 / 8192 | 2,41 / 2,85 | 1777 / 1745 | ok |
| Qwen3.5-0.8B | fla, avec cast fp32 | 4096 | 3,95 | 1300 | ok |

Sous WSL, fla est 2 à 2,8 fois plus rapide que le repli torch.

## Piste 2 : Windows natif, repli torch (venv principal en lecture seule, `.venv\Scripts\python.exe -I sonde.py`)

Le multimodal se charge sans torchvision. La tour vision est gelée, comme sous WSL.

| Modèle | Variante | Longueur | VRAM réservée | Tokens/s | Statut |
|---|---|---|---|---|---|
| Qwen3.5-2B | torch, sans cast | 1024 | 3,26 | 608 | ok |
| Qwen3.5-2B | torch, sans cast | 2048 | 3,54 | 633 | ok |
| Qwen3.5-2B | torch, sans cast | 4096 | 4,09 | 536 | ok |
| Qwen3.5-2B | torch, sans cast | 8192 | 5,35 | 375 | ok (près du seuil) |

Le repli torch n'est pas rédhibitoire sous Windows : de 540 à 630 t/s jusqu'à 4096, du même ordre que la référence MiniCPM5 (693 t/s). Il était plus lent sous WSL (≈ 390 t/s), un écart non expliqué.

## Piste 3 : Windows natif avec triton-windows et fla (venv séparé `venv-triton`)

Installé : triton-windows 3.8.0.post29, flash-linear-attention 0.5.2 et la même pile que le lock. Aucun compilateur n'est à installer : triton-windows embarque le sien. Ça marche du premier coup, et seul `causal_conv1d_fn` reste en repli.

| Modèle | Variante | Longueur | VRAM réservée | Tokens/s | Statut |
|---|---|---|---|---|---|
| Qwen3.5-2B | fla, sans cast | 2048 | 3,55 | 1042 | ok |
| Qwen3.5-2B | fla, sans cast | 4096 | 3,70 | 1054 | ok |
| Qwen3.5-2B | fla, sans cast | 8192 | 4,31 | 516 | ok |

À 8192, Windows tombe à 516 t/s contre 1090 sous WSL. La cause n'a pas été cherchée (autotune, température ou WDDM). Mesure unique, à refaire.

## Piste 4 : MiniCPM5-2B en contexte long

| Système | Variante | Longueur | VRAM réservée | Tokens/s | Statut |
|---|---|---|---|---|---|
| Windows (référence du jour) | avec cast (sonde du dépôt) | 2048 / 4096 | 5,07 / 5,79 | 693 / 621 | ok / débordement |
| WSL | avec cast (sonde du dépôt) | 2048 / 4096 | 5,07 / 5,88 | 762 / 110 | ok / débordement |
| WSL | **sans cast** | 4096 / 8192 | 3,72 / 4,61 | 947 / 857 | ok |
| WSL | Liger (`use_liger_kernel`, `loss_type=nll`), avec cast | 4096 / 8192 | 5,54 / 7,39 | 789 / 93 | débordement |
| **Windows** | **sans cast** | 4096 / 8192 | 3,72 / 4,69 | 766 / 596 | ok |

Linux seul ne change rien : la même sonde y donne 5,07 Gio à 2048 et déborde à 4096. Liger n'apporte rien, parce que TRL 1.13 calcule déjà la perte par blocs (`chunked_nll`). Unsloth n'a pas été retenté : inutile, puisque 8192 tient déjà sans lui, sous Windows natif.

## Garder la tour vision : faisable

- On charge `AutoModelForImageTextToText`. La tour est quantifiée en nf4 par défaut, ce qui est sans effet, car elle ne sert pas dans une passe texte seul. Elle reste gelée, et le LoRA, ciblé par une regex sur `language_model`, ne la touche pas.
- Pour l'export, `train/export.py` charge `AutoModelForCausalLM`. Il faudra charger la classe ConditionalGeneration en bf16, fusionner l'adaptateur (`merge_and_unload`) et sauvegarder le modèle complet. Le GGUF texte se convertit avec llama.cpp et le `mmproj` d'origine reste valable, puisque la vision n'a pas changé. Ce point n'a pas été vérifié de bout en bout dans ce spike.

## À changer dans slmsp pour un vrai chemin d'entraînement

1. **Le cast fp32** (gain immédiat, tous modèles) : rendre optionnel `prepare_model_for_kbit_training` dans `environnement.charger_modele` et dans `methodes.py`, à remplacer par `enable_input_require_grads()` plus le gradient checkpointing. La sonde devra mesurer les deux variantes. Décision de fond, à confirmer par Anaël : la stabilité numérique sur un vrai run (normes en bf16) reste à vérifier, même si c'est la pratique d'Unsloth.
2. **Les multimodaux** : `controler_config_modele` refuse tout `vision_config`. Il faudrait l'accepter si le modèle est déclaré `multimodal = "geler-vision"` dans `config/modeles/<slug>.toml`, charger alors ConditionalGeneration et cibler le LoRA par une regex sur `language_model` (au lieu de `all-linear`, qui toucherait la tour). Le contrôle « 0 paramètre vision entraînable » est à consigner dans `sonde.json`.
3. **`exiger_entrainable`** : passer `entrainable = true` dans `qwen3.5-2b.toml` et `qwen3.5-0.8b.toml`, ce qui revient sur la décision D8, à confirmer par Anaël. Il faut aussi un contrôle du chemin rapide : enregistrer dans la sonde les avertissements « falling back », et refuser ou signaler un run sur le repli torch au-delà de 4096.
4. **Où entraîner** : Windows natif suffit. Il faut un groupe de dépendances optionnel `train-gdn` (`triton-windows`, `flash-linear-attention`) dans `pyproject.toml`, ou un `envs/gdn` comme `envs/unsloth`. WSL n'est pas nécessaire. S'il le devenait, le venv vivrait dans `~/slmsp-spike` (poids copiés en ext4 : la lecture par `/mnt/c` est correcte, mais la copie de 10 Gio prend environ 2 min). Les runs reviendraient par une écriture directe sous `/mnt/c/.../runs/`, avec les chemins portables de `environnement.chemin_portable`. Le verrou `gpu.lock` devrait alors être partagé entre les deux systèmes. Il faudrait aussi `CC` (ziglang), faute de gcc.
5. **Mémoire** : avec la base en bf16, le chargement de Qwen3.5-2B occupe déjà 1,8 Gio, dont 1 Gio d'embeddings liés en bf16. Ne pas mettre `lm_head` dans les cibles : TRL `chunked_nll` le refuse.

## Recommandation

1. Rester sous Windows natif.
2. Corriger d'abord le cast fp32 : MiniCPM5-2B passe alors à 8192 tokens (4,7 Gio, environ 600 à 770 t/s) sur le portable, sans la tour 8 Go.
3. Pour Qwen3.5-2B, ajouter triton-windows et fla dans un environnement séparé, et entraîner avec la tour vision gelée : environ 1050 t/s jusqu'à 4096, et 8192 qui tient.
4. Le repli torch (≈ 600 t/s) reste un secours acceptable jusqu'à 4096.

WSL2 n'apporte un gain net que sur la vitesse à 8192, et la mesure Windows à 8192 est à refaire avant de conclure.
