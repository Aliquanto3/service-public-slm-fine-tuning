---
title: 'Option precision_base : cast fp32 de prepare_model_for_kbit_training optionnel'
type: 'feature'
created: '2026-10-18'
status: review
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/enquete-entrainement-hybrides-2026-10-18.md'
warnings: []
deferred: []
---

## Intent

**Problème :** `prepare_model_for_kbit_training` passe en fp32 embeddings, normes et conv1d, et les activations avec le gradient checkpointing. Sur MiniCPM5-2B (6 Go), sans lui : 3,72 Gio à 4096 tokens et 4,69 à 8192, contre un débordement à 4096 avec lui ; pertes identiques sur quelques pas.

**Décision (Anaël, 2026-10-18) :** rendre le cast optionnel et mesurer les deux.

## Décision d'implémentation

- Clé de run `precision_base` : `"fp32-kbit"` (défaut, comportement inchangé) ou `"bf16"` (base bf16, pas de `prepare_model_for_kbit_training`, `model.enable_input_require_grads()` ; `use_reentrant=False` inchangé ; poids LoRA en fp32 comme PEFT les crée).
- Méthodes quantifiées seules concernées (qlora, dora, orpo, rslora) : c'est là que le cast était appelé. `lora` et `pissa` (bf16 sans quantification) ne l'appelaient pas : la clé y est acceptée et sans effet. `qlora-unsloth` refuse `bf16` (pile Unsloth).
- Empreinte : `precision_base` est dans `CLES_INVARIANTS`. Comme `decoupage_masque`, la clé n'est écrite (invariants et `toml` résolu de `run.json`) que hors défaut ; absente = `fp32-kbit` (`DEFAUTS_INVARIANTS`). Les runs d'avant restent reconnus et reprenables ; un run bf16 garde sa valeur à la reprise (la config résolue diffère sinon).
- Sonde `slmsp train sonde-env --precision-base {fp32-kbit,bf16,les-deux}` (défaut `fp32-kbit`). `les-deux` recharge le modèle une fois par variante (en `qlora` ; en `lora`, une seule mesure) ; chaque mesure porte `precision_base`, `sonde.json` ajoute `precisions_base` et `longueur_max_ok_par_precision`, `run.json` consigne l'option.

## Critères d'acceptation

1. Défaut : `prepare_model_for_kbit_training` appelé, sonde et runs identiques à avant.
2. `bf16` : non appelé, `enable_input_require_grads` appelé.
3. TOML : valeur inconnue refusée.
4. Campagne : deux runs de `precision_base` différents sont refusés ; un run sans la clé vaut `fp32-kbit`.
5. Sonde `les-deux` : lignes distinguées dans le rapport, la sortie console et `sonde.json`.

## Tests

`tests/train/test_methodes.py`, `test_config.py`, `test_run.py`, `test_environnement.py` (faux modèles et mocks, CPU). Aucune mesure GPU lancée.

## Auto Run Result

- Statut : à relire. Reports : sondes réelles `--precision-base les-deux` (MiniCPM5-2B, 4096 et 8192) et court run bf16 de validation (convergence, qualité) à lancer quand le GPU est libre.
- À confirmer par Anaël : clé absente du `run.json` au défaut (choix de rétrocompatibilité stricte de la reprise, plutôt que l'écrire toujours) ; `bf16` sans effet sur lora/pissa plutôt que refusé.
