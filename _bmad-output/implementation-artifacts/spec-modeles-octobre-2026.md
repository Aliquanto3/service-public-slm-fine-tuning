---
title: 'Modèles de base d''octobre 2026 : Qwen3.5-2B, Bonsai-2-4B (Q2_0), MiniCPM-V-4.7-1B'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md (story 8.1)'
warnings: []
deferred: []
---

## Intent
Décision d'Anaël (17/10) : trois Modèles de base candidats de plus pour la Baseline. Qwen3.5-2B est candidat au fine-tuning. Bonsai-2-4B, ternaire en Q2_0, est le candidat « sans fine-tuning » du chemin no-go. MiniCPM-V-4.7-1B est multimodal, avec la vision exclue. On les épingle comme les candidats de la story 8.1 et on vérifie leur compatibilité avec llama.cpp b11429. Les modèles ne sont pas ajoutés à `CANDIDATS`, qui reste l'ordre D4 : ils se téléchargent par slug.

## Approach
- `config/modeles/qwen3.5-2b.toml`, `bonsai-2-4b.toml` et `minicpm-v-4.7-1b.toml` : révisions au SHA de commit, SHA-256 et tailles lus dans l'API Hugging Face via la passerelle du projet (`preparer_hf`, `client_hf`). Les fichiers non LFS sont hachés après lecture. Valeurs communes : `exclure_vision = true`, `reasoning = "off"`, `chat_template_kwargs = { enable_thinking = false }`, contexte 8192, cache f16, `protocole_outils = "natif"` (non sondé, à confirmer par la sonde 8.2).
- **Qwen3.5-2B** : il n'existe pas de GGUF Qwen officiel (ni ggml-org). On prend le GGUF communautaire unsloth (`Qwen3.5-2B-Q4_K_M.gguf`, comme pour qwen-4b). Le `[gguf_f16]` est le BF16 d'unsloth, qui ne publie pas de F16. Le contrôle `chat_template` a constaté un template GGUF différent de celui du tokenizer HF : `chat_template_force = true`, avec le template exporté.
- **Bonsai-2-4B** : GGUF seul (`fichiers = []`), fichier `Ternary-Bonsai-2-4B-Q2_0.gguf`, pas de `[gguf_f16]`. Nouveau champ de schéma `entrainable: bool = True` dans `ConfigModele`. `entrainable = false` pour Bonsai : `train run` lève `ConfigurationInvalide` (« modèle non entraînable ») avant toute lecture des poids et toute création de run.
- **MiniCPM-V-4.7-1B** : GGUF officiel OpenBMB, en Q4_K_M et en F16.
- Registre des licences (`config/publication.toml`) : Apache 2.0, lue sur les trois cartes. Une entrée pour qwen3.5-2b et une pour minicpm-v-4.7-1b. Bonsai n'en a pas : aucun modèle fine-tuné à publier.

## Compatibilité avec llama.cpp b11429 (`llama-server --version` : build 11429, commit d81235049)
| Modèle | Architecture GGUF | b11429 | Constat |
|---|---|---|---|
| qwen3.5-2b | `qwen35` (hybride Gated DeltaNet) | **oui** | Charge en CPU et répond correctement. |
| minicpm-v-4.7-1b | texte `qwen35` (`qwen3_5_text`) | **oui** (texte seul) | Charge en CPU et répond correctement. Projecteur `minicpmv` 4.7 non testé (vision exclue). |
| bonsai-2-4b | `qwen35`, type `q2_0` | **non** : charge mais produit du charabia | Le type `q2_0` est connu, mais les métadonnées `prism.hadamard.*` (rotation d'activation) sont ignorées. |

Pour Bonsai, il faut une build amont qui applique le runtime d'activation Hadamard (`prism.hadamard.*`). Selon la carte du modèle, c'est le cas de « recent master ». La documentation PrismML cite la PR amont #24448 (Q2_0 natif), encore en cours d'après elle. **Le numéro minimal de build reste à relever** : l'outillage n'a pas d'accès à GitHub. Monter la version épinglée (`config/llamacpp.toml`) changerait le moteur de toute la Baseline. Il faudrait alors **re-mesurer la Baseline** de tous les candidats (génération v1.1, mesures, socle GGUF), sans quoi les résultats ne sont plus comparables. L'autre voie est un binaire réservé à Bonsai, mais l'écart de moteur doit alors être consigné. **À confirmer par Anaël.**

## Essais (CPU, `--device none -ngl 0`, une question, T = 0)
Question : « Quelle est la capitale de la France ? Réponds en une phrase. »
- qwen3.5-2b (template HF forcé) : « La capitale de la France est Paris. » Débit de 25 tok/s.
- minicpm-v-4.7-1b : « La capitale de la France est Paris. » Débit de 30 tok/s.
- bonsai-2-4b : tokens incohérents et multilingues, 4,5 tok/s. Inutilisable en b11429.

Runs de téléchargement (dépôt principal) :
- `runs/fetch/20261017-052245-modeles-67a6` (bonsai) : serveur ok, les autres contrôles sont sans objet.
- `runs/fetch/20261017-052420-modeles-f92e` (minicpm) : `dense` en échec, le reste ok.
- `runs/fetch/20261017-052846-modeles-a55f` (qwen3.5) : `dense` et `chat_template` en échec. Le second est corrigé par `chat_template_force`.

## Commandes de Baseline (q4_k_m, CPU, depuis le dépôt principal)
Pour chaque slug parmi `qwen3.5-2b` et `minicpm-v-4.7-1b` :
```
uv run slmsp eval run --modele base:<slug> --quantification q4_k_m --jeu v1.1 --variante cpu --phase generation
uv run slmsp eval run --modele base:<slug> --phase notation --depuis <run_generation>   # API payante : orchestrateur
uv run slmsp measure run --modele base:<slug> --quantification q4_k_m
uv run --extra bench slmsp bench run --modele base:<slug> --socle --cible gguf --quantification apres --variante-llamacpp cpu
```
Bonsai : mêmes commandes, à lancer **seulement après** la montée de version de llama.cpp. `measure run` se lance sans `--quantification`, car le fichier porte Q2_0 et non Q4_K_M. Dans `eval run`, l'étiquette `q4_k_m` désigne la section `[gguf]`, qui est ici en Q2_0 : l'écart est à noter dans le comparatif. Le banc HF bf16 est exclu par décision d'Anaël (cible : PC sans GPU, 16 Go).

## Écarts et points à confirmer par Anaël
- **Contrôle `dense` (D7)** : Qwen3.5-2B et MiniCPM ont 18 couches `linear_attention` (Gated DeltaNet) sur 24. Le contrôle de la story 8.1 les « écarte », alors que D7 visait les hybrides Mamba. Le code n'a pas été modifié. Il faut décider s'il faut admettre `linear_attention`, et vérifier l'entraînement sous Windows : sans `flash-linear-attention` ni `causal-conv1d`, transformers bascule sur une implémentation torch lente. À confirmer par Anaël.
- **Bonsai et la température** : la carte recommande T = 0,7, top_p 0,8 et presence_penalty 1,5 en non-thinking. L'évaluation reste gloutonne (protocole commun, T = 0) : c'est un écart assumé.
- **MiniCPM et transformers** : le modèle déclare `minicpmv4_7` (config écrite avec transformers 5.18.0), alors que l'épinglage est en 5.17.0 et ne connaît que `minicpmv4_6`. L'entraînement et un éventuel adaptateur lm-eval HF sont donc reportés.
- `[gguf_f16]` est épinglé pour qwen3.5-2b et minicpm, mais n'a pas été téléchargé.

## Tests
- `tests/fetch/test_verifications.py` : `test_toml_modeles_octobre` (trois slugs) et `test_toml_modeles_octobre_particularites`.
- `tests/train/test_run.py` : `test_modele_non_entrainable_refuse`.

## Auto Run Result
- Slugs `qwen3.5-2b`, `bonsai-2-4b` et `minicpm-v-4.7-1b`, hors `CANDIDATS` : c'est le choix le plus réversible.
- Champ `entrainable` plutôt qu'une liste en dur, avec le refus placé dans `train.run.executer`. Le refus ne porte pas sur l'export ni sur `eval`.
- Pour Bonsai, `source = "officielle"`, car le dépôt est celui de l'éditeur Prism ML.
