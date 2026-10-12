# Recherche : méthodes de fine-tuning sur RTX 3050 8 Go (2026-10-11, passe superficielle)

Les estimations de VRAM sont **non mesurées**. Il faut les calibrer par un essai réel avant d'en tirer des conclusions.

## Méthodes faisables

| Méthode | 1B | 3B | Verdict |
|---|---|---|---|
| LoRA bf16 | ~4-6 Go | ~9-11 Go | 3B hors budget à 4k |
| QLoRA NF4 | ~2-3 Go | ~4,5-6,5 Go | Voie principale pour le 3B |
| DoRA | LoRA + 10-30 % | idem | Faisable, plus lent |
| rsLoRA | = LoRA | = LoRA | Gratuit, utile à rang élevé |
| PiSSA / LoftQ | ≈ LoRA + init | idem | Faisable, gain incertain |
| GaLore | ~6-8 Go | ≥ 15 Go | 1B seulement, lent |
| Full FT | borderline (optimiseur 8 bits) | impossible | 1B seulement, non garanti |
| DPO | ~1,5-2× SFT | idem | Après SFT |
| ORPO / SimPO | sans modèle de référence | idem | Moins coûteux que DPO |
| KTO | données non appariées acceptées | idem | |

## Frameworks
- **TRL + PEFT** : le choix le plus propre pour comparer.
  - La méthode se choisit dans `LoraConfig` : `use_dora`, `use_rslora`, `init_lora_weights="pissa"|"loftq"`.
  - Trainers disponibles : SFT, DPO, ORPO, KTO, CPO/SimPO.
  - GaLore via `optim="galore_adamw"`.
- **Unsloth** :
  - Windows natif supporté ([guide](https://www.unsloth.ai/docs/get-started/install/windows-installation)).
  - Granite 4.0 supporté, y compris en full fine-tuning ([page](https://unsloth.ai/docs/models/tutorials-how-to-fine-tune-and-run-llms/ibm-granite-4.0)).
  - Notebook Ministral 3 3B listé, mais non vérifié.
  - SmolLM3 non vérifié.
  - Sert de mesure de vitesse parallèle, pas de socle de comparaison.
- **LLaMA-Factory** : bascule de méthode par YAML, support des modèles cibles non vérifié.
- **Axolotl** : plutôt WSL2 ou multi-GPU.
- **torchtune** : maintenance incertaine, déconseillé.

## Protocole équitable
- Mêmes données, graine, ordre des exemples, chat template et masquage de la perte (assistant seul).
- Rapporter les deux budgets : à tokens vus égaux et à durée égale.
- Petit balayage taux d'apprentissage × rang par méthode. Même nombre de paramètres entraînables (toutes les couches linéaires).
- Métriques de vitesse :
  - tokens/s hors padding, après 10 étapes de chauffe ;
  - temps jusqu'à une perte de validation cible ;
  - VRAM max (`torch.cuda.max_memory_allocated/reserved` + `nvidia-smi`) ;
  - énergie (`nvidia-smi power.draw` échantillonné toutes les 200 ms et intégré en Wh, ou CodeCarbon / pynvml).
- Évaluer avant et après sur le jeu tenu à part, avec 3 graines si possible, puis **à nouveau après quantification GGUF**.
- Environnement figé : pilote, CUDA, torch, réglage d'attention, mode d'alimentation.

## Pièges
- **Granite 4 H (Mamba2)** : les noyaux `mamba-ssm` et `causal-conv1d` posent problème sous Windows. Préférer le 1B dense.
- **Ministral 3** : l'encodeur vision est à geler ou exclure. Il faut aussi vérifier la classe de chargement et l'export GGUF.
- **Export GGUF** : fusionner le LoRA en 16 bits, convertir avec llama.cpp, quantifier, puis re-tester le tool calling.
- **Chat template** : utiliser le template officiel à l'entraînement comme à l'inférence. Vérifier le rendu des messages `tool`, les jetons de fin, le BOS en double et le mode think/no_think de SmolLM3.

## Recommandation
Comparer en priorité :
1. QLoRA (référence) ;
2. LoRA bf16 sur le 1B ;
3. DoRA ou rsLoRA (PiSSA en variante) ;
4. ORPO ou DPO après le SFT.

En option, full fine-tuning ou GaLore sur le 1B.

Stack : TRL + PEFT, avec Unsloth en mesure de vitesse parallèle.

## Points non vérifiés
- SmolLM3 et Ministral 3 dans chaque framework.
- Toutes les valeurs de VRAM.
- PiSSA et LoftQ dans la version actuelle de PEFT.
