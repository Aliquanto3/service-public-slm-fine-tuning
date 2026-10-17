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

---

# Seconde campagne (décision d'Anaël, 17/10) : MiniCPM5-2B, MiniCPM5-1B et Gemma-4-E2B

**MiniCPM-V-4.7-1B est abandonné** : retiré de la Baseline. Sa config reste (commentaire d'en-tête ajouté), aucun run à lancer.

## Épinglage (SHA de commit, SHA-256 et tailles lus dans l'API HF via la passerelle, 2026-10-17)
| Slug | Dépôt HF (révision) | GGUF retenu | Licence |
|---|---|---|---|
| `minicpm5-2b` | `openbmb/MiniCPM5-2B` (f974000) | `openbmb/MiniCPM5-2B-GGUF` Q4_K_M (1,56 Go) et `[gguf_f16]` (5,04 Go) | Apache 2.0 |
| `minicpm5-1b` | `openbmb/MiniCPM5-1B` (87179e5) | `openbmb/MiniCPM5-1B-GGUF` Q4_K_M (688 Mo) et `[gguf_f16]` (2,17 Go) | Apache 2.0 |
| `gemma-4-e2b` | `google/gemma-4-E2B-it` (3e22461) | `google/gemma-4-E2B-it-qat-q4_0-gguf` : `gemma-4-E2B_q4_0-it.gguf` (3,35 Go), pas de `[gguf_f16]` | Apache 2.0 |

- Accès : les trois dépôts HF et les GGUF sont publics (`gated` faux). Aucun blocage Gemma.
- Gemma : **Q4_0 QAT, pas Q4_K_M**. Dans `eval run`, l'étiquette `q4_k_m` désigne la section `[gguf]` : écart à noter dans le comparatif (comme Bonsai). Google ne publie pas de GGUF F16 officiel : pas de `[gguf_f16]`, banc « avant » à décider (à confirmer par Anaël). Le projecteur `gemma-4-E2B-it-mmproj.gguf` n'est pas épinglé (vision et audio exclues, `exclure_vision`).
- MiniCPM5 : `exclure_vision = false` (texte seul, aucun `vision_config`). Les trois modèles : contexte 8192, cache f16, `reasoning = "off"`, `enable_thinking = false` (le template MiniCPM5 ouvre `<think>`), `protocole_outils = "natif"` (non sondé, à trancher par la sonde 8.2).
- `config/publication.toml` : trois entrées Apache 2.0, sans `verifie_le`.
- `chat_template_force = true` pour `minicpm5-2b` seulement (contrôle `chat_template` : template GGUF différent ; run `fetch/20261017-061650-modeles-6ca4`). Templates HF et GGUF identiques pour `minicpm5-1b` et `gemma-4-e2b`.

## Compatibilité llama.cpp b11429 et contrôles 8.1
Runs `fetch` : `20261017-061207-modeles-5969` (1B), `20261017-061650-modeles-6ca4` (2B, échec `chat_template` corrigé), `20261017-062639-modeles-81f5` (2B et Gemma, tout ok).
| Modèle | Architecture GGUF | b11429 | `dense` |
|---|---|---|---|
| minicpm5-2b, minicpm5-1b | `llama` (LlamaForCausalLM, 42 couches pour la 2B) | oui, charge en CPU | passe (pas de `layer_types`) |
| gemma-4-e2b | `gemma4` | oui, charge en CPU | passe (35 couches d'attention, sliding et full) |

## Essais CPU (`--device none -ngl 0`, T = 0, « Quelle est la capitale de la France ? Réponds en une phrase. »)
- minicpm5-1b : « La capitale de la France est Paris. » à 22,8 tok/s.
- minicpm5-2b (template HF forcé) : même réponse, 11,1 tok/s.
- gemma-4-e2b : même réponse, 3,3 tok/s (la machine est chargée par les benchmarks ; le débit est sans doute sous-estimé).

## Reports et points à confirmer par Anaël
- Gemma : écart de quantification (Q4_0 QAT) et absence de F16 officiel, voir plus haut.
- Entraînement : MiniCPM5 est un llama dense (aucune difficulté attendue) ; Gemma-4-E2B (embeddings par couche, `gemma4` multimodal) n'a pas été essayé avec l'épinglage transformers : à vérifier avant tout fine-tuning.
- Poids HF téléchargés dans le dépôt principal (`models/`), F16 non téléchargés (`--f16` plus tard).
- Commandes de Baseline : celles de la première campagne, avec les slugs `minicpm5-2b`, `minicpm5-1b` et `gemma-4-e2b`.
- Tests : `test_toml_modeles_octobre_2` et `test_toml_modeles_octobre_2_particularites` dans `tests/fetch/test_verifications.py`.
