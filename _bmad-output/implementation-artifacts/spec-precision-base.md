---
title: 'Option precision_base : cast fp32 de prepare_model_for_kbit_training optionnel'
type: 'feature'
created: '2026-10-18'
status: done
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
- Sonde `slmsp train sonde-env --precision-base {fp32-kbit,bf16,les-deux}` (défaut `fp32-kbit`). `les-deux` recharge le modèle une fois par variante (en `qlora` ; en `lora`, une seule mesure étiquetée `sans-objet`, repli LoRA bf16 compris) ; chaque mesure porte `precision_base`, `sonde.json` ajoute `precisions_base` (précisions réellement mesurées) et `longueur_max_ok_par_precision` ; `longueur_max_ok` vaut celle de la première précision mesurée (`fp32-kbit` en `les-deux`, le défaut des runs). Un OOM au chargement de la seconde variante garde les mesures de la première (statut `degrade`, `erreur_chargement`, mesures `non-tentee`). `run.json` consigne l'option.

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

## Revue

Revue Opus du 2026-10-18 sur 83282fd (second avis Haiku repris point par point). Aucune mesure GPU : test réel sur CPU avec un Llama minuscule bf16 et PEFT 0.21.2.

| Sév. | Source | Constat | Suite | Motif |
|---|---|---|---|---|
| medium | second avis 1 | `longueur_max_ok` racine = maximum des deux précisions | corrigé | Elle vaut maintenant celle de la première précision mesurée (`fp32-kbit` en `les-deux`, la précision seule sinon) ; tests `test_sonde_les_deux_longueur_max_racine_celle_du_defaut` (fp32 16, bf16 64, racine 16) et `test_sonde_bf16_seule_longueur_max_racine`. |
| medium | second avis 2 | Aucun test réel du chemin bf16 | corrigé | `test_bf16_reel_adaptateurs_fp32_base_bf16_gradient_avec_checkpointing` : `preparer_base_quantifiee` puis `poser_adaptateur` réels, checkpointing `use_reentrant=False` actif ; LoRA fp32 entraînables, base bf16 gelée, perte finie, gradient non nul sur `lora_B`, aucun sur la base. Témoin `fp32-kbit` : normes castées en fp32. La base est non quantifiée (bnb exige CUDA). |
| low | second avis 3 | `lora` en `les-deux` étiqueté `fp32-kbit` | corrigé | Étiquette `sans-objet` pour toute mesure LoRA bf16 (méthode `lora` ou repli), quelle que soit l'option. |
| low | second avis 4 | `_bloquer` écrit `precision_base` au défaut | corrigé | `_toml_resolu` commun au run lancé et au run bloqué ; assertion ajoutée à `test_jeu_absent_consigne_bloque`. |
| low | second avis 5 | lora/pissa : « sans effet » mais invariant | rejeté (docstring précisée) | Normaliser lora/pissa à `fp32-kbit` empêcherait un run lora de rejoindre une campagne `bf16` (l'invariant les refuserait) : c'est l'inverse du but. La clé reste acceptée et comparée ; les TOML lora/pissa d'une campagne `bf16` la déclarent. |
| low | second avis 6 | `precision_base` non transmise à Unsloth | rejeté (consigné) | Run : `qlora-unsloth` refuse déjà `bf16` (`RunConfig`). Sonde : `--unsloth` mesure la pile Unsloth dans son propre environnement, avec sa propre préparation ; `unsloth.json` n'a pas de précision de base et n'est pas comparé aux lignes `precision_base`. |
| low | second avis 7 | OOM au chargement de la variante 2 : tout est perdu | corrigé | Au-delà de la première variante, les mesures déjà faites sont gardées, la variante en échec et les suivantes sont `non-tentee`, `erreur_chargement` est écrit, statut `degrade`. OOM à la première : `partiel-erreur` inchangé. Deux tests. |
| low | second avis 8 | Champs nouveaux dans `sonde.json` | rejeté | Aucun lecteur de `sonde.json` dans `src/` ni `outils/` (seul `cli/train.py` l'écrit) ; les nouveaux champs n'affectent rien. |
| low | second avis 9 | ORPO chaîné à un SFT d'une autre précision | rejeté (consigné) | L'adaptateur SFT (poids LoRA fp32) se charge sur l'une ou l'autre base ; si le SFT est dans la même campagne, l'invariant refuse déjà l'écart. Hors campagne commune, l'écart est permis et consigné dans les invariants de chaque run. |
| — | revue | Complexité : 0 constat | — | `sonder` reparcourt les mesures une fois par précision à la fin (2 × quelques longueurs) ; pas de structure qui grossit sans borne. |

Report (GPU occupé) : sondes réelles `--precision-base les-deux` sur MiniCPM5-2B à 4096 et 8192, puis un court run qlora `bf16` (perte comparable au `fp32-kbit`, adaptateur rechargeable par l'évaluation) ; vérifier aussi qu'une base nf4 réelle garde ses normes en bf16 avec `bf16` (`named_parameters`).
