---
title: 'lm-eval : adaptateur hf-mistral3 pour Ministral 3 (QCM sur poids HF)'
type: 'bugfix'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** `slmsp bench run --modele base:ministral-3-3b --socle` échoue sur toutes les tâches lm-eval à cible `hf` : `--model hf` charge via `AutoModelForCausalLM`, qui ne connaît pas `Mistral3ForConditionalGeneration` (transformers 5.17).

**Approach:** lm-eval 0.4.13 fournit l'adaptateur `hf-mistral3` (`lm_eval/models/mistral3.py` : charge `Mistral3ForConditionalGeneration`, backend causal, logits texte seul). Le moteur choisit le modèle lm-eval d'après `architectures` du `config.json` des poids ; défaut `hf`.

## Boundaries & Constraints

**Always:** `--model hf` inchangé pour les autres architectures et pour un `config.json` absent ou illisible ; `--model_args` inchangé.

**Never:** pas de champ de configuration modèle ni de changement de schéma ; pas de modification de lm-eval ni de transformers.

</intent-contract>

## Code Map

- `src/slmsp/benchmarks/moteurs/lm_eval.py` : `MODELES_PAR_ARCHITECTURE`, `modele_hf(poids)`, utilisé par `arguments_hf`.
- `tests/benchmarks/test_lm_eval.py` : détection (paramétré) et argv `--model hf-mistral3`.

## Verification

- Tests ciblés : `uv run pytest -q --tb=short tests/benchmarks/test_lm_eval.py`.
- Réel CPU (hors `slmsp`, GPU occupé) : `python -m lm_eval --model hf-mistral3 --model_args pretrained=<models>/ministral-3-3b/hf,dtype=bfloat16 --device cpu --batch_size 1 --tasks global_mmlu_fr --num_fewshot 0 --limit 2 --include_path src/slmsp/benchmarks/taches_lmeval`, HF hors ligne : 48 requêtes loglikelihood, `global_mmlu_fr acc = 0.5833 ± 0.1443` (12 items), 1 min 34 s.

## Auto Run Result

- Décision : détection par `config.json` plutôt qu'un champ `classe_hf` dans `config/modeles/*.toml` (plus simple : aucun schéma touché, couvre `hf-bf16` comme `hf`, réversible en retirant une entrée du dictionnaire).
- Les poids vision (Pixtral) sont chargés en mémoire par l'adaptateur, mais aucune image n'entre : évaluation texte seule, cohérente avec `exclure_vision`.
