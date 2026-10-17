---
title: 'Hybrides Gated DeltaNet admis pour la Baseline, registre des Modèles de base candidats'
type: 'feature'
created: '2026-10-17'
status: 'review'
baseline_commit: 'd24006d'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/planning-artifacts/decisions.md (D7, D8)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-modeles-octobre-2026.md'
warnings:
  - 'Règle de taille : « 2B au plus » (D8) contre « 2B et plus exclus » (etat-run-2026-10-16, décision de 09h) ; Qwen3.5-2B y était exclu.'
deferred: []
---

## Intent
Décisions d'Anaël du 2026-10-17 (option 2 et règle de taille). Le contrôle `dense` (story 8.1) écartait les hybrides Gated DeltaNet (`linear_attention`), alors que D7 visait Mamba. Qwen3.5-2B et Qwen3.5-0.8B tournent avec llama.cpp b11429. Seuls l'entraînement et `lm_eval` HF sont lents sous Windows (pas de `flash-linear-attention` ni de `causal-conv1d`). On les admet donc pour la Baseline seulement, et on tient un registre des Modèles de base candidats.

## Approach
- `src/slmsp/fetch/verifications.py` : `COUCHES_INFERENCE_SEULE = {"linear_attention"}`. `_controle_dense` reçoit la fiche (`ConfigModele`). Une couche `mamba` ou d'un type inconnu écarte toujours le modèle. Des couches `linear_attention` donnent `ok` (« hybride Gated DeltaNet admis pour l'inférence, non entraînable ») si la fiche porte `entrainable = false`, sinon `echec` (« inscrire entrainable = false »).
- **Garde-fou dans le contrôle lui-même** : `verifier_config_hf` reçoit déjà la fiche. Un test qui parcourrait les fiches ne verrait pas `config.json`, qui est hors dépôt. La validation de la fiche ne le voit pas non plus.
- `config/modeles/qwen3.5-2b.toml` et `qwen3.5-0.8b.toml` : `entrainable = false`, et des commentaires qui renvoient à D8. `train run` les refuse par le mécanisme Bonsai déjà en place.
- `minicpm5-2b.toml` et `gemma-4-e2b.toml` : en-tête « ÉCARTÉ (taille > 2B…) ». Les fiches sont conservées.
- `decisions.md` : D8, qui précise D7, puis le registre (un tableau : slug, dépôt HF, paramètres texte servis, statut, raison, date, source).
- Ajout demandé par l'orchestrateur : `config/modeles/granite-4.0-1b.toml` porte `lm_eval_batch_size = 2`. Sur le portable (6 Go de VRAM), `auto` provoque des OOM. C'est la valeur de départ de `docs/reprise-deuxieme-pc.md` §5, à confirmer par mesure. Test : `test_toml_particularites`.
- Run réel : `runs/fetch/20261017-194644-modeles-f773` (qwen3.5-0.8b, 5 contrôles ok, 0 octet transféré).

## Tests
`tests/fetch/test_verifications.py` :
- `test_dense_admet_gated_deltanet_non_entrainable` ;
- `test_dense_gated_deltanet_exige_entrainable_false` ;
- `test_dense_hybride_mixte_ecarte_meme_non_entrainable` (mamba, type inconnu) ;
- `test_mamba_ecarte_meme_non_entrainable` ;
- `test_dense_liste_fermee…`, réaligné : un type inconnu remplace `linear_attention` ;
- `test_toml_modeles_octobre` et `test_toml_modeles_moins_2b`, réalignés sur `entrainable`.

`tests/train/test_run.py` : `test_hybrides_gated_deltanet_refuses` (fiches réelles des deux Qwen). Tests ciblés : 896 passés (`tests/fetch`, `tests/train/test_run.py`, `tests/core`), puis 93 passés sur les deux fichiers modifiés ; contrôle rapide OK.

## Auto Run Result
- Statut : review. Pas de fusion. `sprint-status.yaml` n'est pas modifié.
- Décision prise seul : un modèle qui mêle `linear_attention` et `mamba` (ou un type inconnu) est écarté, même avec `entrainable = false`.
- `decisions.md` est modifié sur demande expresse de l'orchestrateur (décisions d'Anaël), alors que les consignes l'interdisent par défaut.
- **À confirmer par Anaël** :
  - **Seuil de la règle de taille.** D8 dit « 2B au plus » en paramètres servis, mais `etat-run-2026-10-16.md` (décision de 09h) dit « exclusion des modèles de 2B paramètres et plus » et range Qwen3.5-2B parmi les exclus. La passation dit aussi « < 2B ». Le registre suit la consigne reçue (qwen3.5-2b à 1,88 B servis, Baseline seulement).
  - **Chiffres de paramètres.** Ils viennent du comptage de l'orchestrateur et ne sont pas revérifiés ici, faute de réseau. Les modèles sans mesure sont notés d'après leur nom ou leur source.
- Le run de qwen3.5-2b n'est pas relancé : ses poids ne sont pas sur ce PC. Son run de la tour fait foi.
- `minicpm-v-4.7-1b` (Gated DeltaNet, retiré) garde `entrainable` par défaut : son contrôle `dense` reste en échec, ce qui est sans objet puisqu'il est retiré.
