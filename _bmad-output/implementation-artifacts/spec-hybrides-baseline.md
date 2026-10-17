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
warnings: []
deferred:
  - 'fetch modeles --candidats (verifications.CANDIDATS, ordre D4) liste encore ministral-3-3b, smollm3-3b, qwen-4b et ministral-3-8b, écartés par le registre D8, et aucun des candidats actuels : à réaligner sur décision d''Anaël (ordre D4).'
---

## Intent
Décisions d'Anaël du 2026-10-17, confirmées en session principale : hybrides Gated DeltaNet admis pour la Baseline seulement, règle de taille « 2B au plus » en paramètres texte servis, Qwen3.5-2B gardé (cela remplace la décision de 09h et la formule « < 2B » de la passation, `etat-run-2026-10-16.md`). Le contrôle `dense` (story 8.1) écartait les hybrides Gated DeltaNet (`linear_attention`), alors que D7 visait Mamba. Qwen3.5-2B et Qwen3.5-0.8B tournent avec llama.cpp b11429. Seuls l'entraînement et `lm_eval` HF sont lents sous Windows (pas de `flash-linear-attention` ni de `causal-conv1d`). On les admet donc pour la Baseline seulement, et on tient un registre des Modèles de base candidats.

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
  - **Chiffres de paramètres.** Ils viennent du comptage de l'orchestrateur et ne sont pas revérifiés ici, faute de réseau. Les modèles sans mesure sont notés d'après leur nom ou leur source.
- Le run de qwen3.5-2b n'est pas relancé : ses poids ne sont pas sur ce PC. Son run de la tour fait foi.
- `minicpm-v-4.7-1b` (Gated DeltaNet, retiré) garde `entrainable` par défaut : son contrôle `dense` reste en échec, ce qui est sans objet puisqu'il est retiré.

## Revue
Revue Opus du 2026-10-17, une passe, avec la liste du second avis (Haiku).

| Sévérité | Source | Constat | Suite |
|---|---|---|---|
| medium | second avis 1 | `train sonde-env` (avec ou sans `--unsloth`) ne lisait pas `entrainable` : seule l'absence de poids ou le `vision_config` des Qwen l'arrêtait, et un modèle non entraînable texte seul aurait lancé `SFTTrainer.train()`. | Corrigé : `environnement.exiger_entrainable`, point commun à `train run` et `sonde-env`, avant la lecture des poids et le verrou. `controler_config_modele` lit `config.json`, pas la fiche : il ne convenait pas. Test `test_cli_modele_non_entrainable_refuse` (deux Qwen et Bonsai, avec et sans `--unsloth`), en échec sans le correctif. |
| medium | second avis 2 | `dense` ne lisait que `layer_types` à la racine et sous `text_config` : une couche Mamba sous `llm_config` ou dans `layers_block_type` donnait « modèle dense ». | Corrigé : toutes les sous-configurations dict, à toute profondeur, et les clés `CLES_TYPES_COUCHE` (`layer_types`, `layers_block_type`, `layer_block_types`, `block_types`, `hybrid_override_pattern`). Une valeur qui n'est pas une liste non vide donne `echec` (« format non reconnu »). Le contrôle `fp8` profite du même parcours. Verdicts réels inchangés sur les `config.json` présents : granite dense (40 couches), minicpm5-1b et eurollm denses, qwen3.5-0.8b admis non entraînable. qwen3.5-2b n'est pas sur ce PC, mais sa structure est la même (`text_config.layer_types`). |
| high, requalifié en medium (documentaire) | second avis 3 | D8 ne disait pas que la règle et le maintien de Qwen3.5-2B remplacent la décision de 09h et la passation ; « option 2 » n'était pas expliqué ; la spec gardait un « À confirmer » devenu sans objet. | Corrigé : D8 cite la décision d'Anaël, confirmée en session, et ce qu'elle remplace ; « option 2 » est explicité ; le point et l'avertissement sont retirés de la spec. |
| low | second avis 4 | Motivation flash-linear-attention et causal-conv1d sans source. | Corrigé : D8 cite `spec-modeles-octobre-2026.md`, « Écarts et points à confirmer par Anaël ». |
| low | second avis 5 | Couverture de sonde-env et d'Unsloth. | Corrigé avec le constat 1. |
| low | revue | `fetch modeles --candidats` (`CANDIDATS`, ordre D4) liste des modèles écartés par le registre et aucun candidat actuel : il téléchargerait ministral-3-8b et qwen-4b. | Reporté : l'ordre D4 relève d'Anaël (voir `deferred`). |
| low | revue | Côté entraînement, `controler_config_modele` et `controler_contraintes` ne lisent encore que la racine et `text_config`. | Reporté, sans impact : `exiger_entrainable` passe avant, et seuls des modèles denses sont entraînables. |
| low | revue | `minicpm5-2b` et `gemma-4-e2b` gardent leur entrée dans `config/publication.toml`. | Rejeté : sans effet, aucun modèle fine-tuné à publier pour eux. |
| — | revue | Complexité : 0 constat (aucune structure qui grossit pendant l'exécution n'est touchée). | — |
