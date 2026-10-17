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
| bonsai-2-4b | `qwen35`, type `q2_0` | **non** : charge mais produit du charabia | Le type `q2_0` est connu, mais les métadonnées `prism.hadamard.*` (rotation d'activation) sont ignorées. Tourne avec le binaire réservé `prism-b10777-e3de715` (section suivante). |

Pour Bonsai, il faut une build amont qui applique le runtime d'activation Hadamard (`prism.hadamard.*`). Selon la carte du modèle, c'est le cas de « recent master ». La documentation PrismML cite la PR amont #24448 (Q2_0 natif), encore en cours d'après elle. **Le numéro minimal de build reste à relever** : l'outillage n'a pas d'accès à GitHub. Monter la version épinglée (`config/llamacpp.toml`) changerait le moteur de toute la Baseline. Il faudrait alors **re-mesurer la Baseline** de tous les candidats (génération v1.1, mesures, socle GGUF), sans quoi les résultats ne sont plus comparables. L'autre voie est un binaire réservé à Bonsai, mais l'écart de moteur doit alors être consigné. **Tranché par Anaël le 17/10 : binaire réservé** (section suivante).

## Binaire llama.cpp réservé à Bonsai (décision d'Anaël du 17/10)
- **Version** : `prism-b10777-e3de715` du fork `PrismML-Eng/llama.cpp`, branche `prism` (build 10777, commit `e3de715222b2667c54a267441159a5729f11155e`, publiée le 14/10). C'est la release épinglée par `PrismML-Eng/Bonsai-demo` (`setup.ps1`, `$ReleaseTag`, commit `db871ea` du 15/10), un cran après `prism-b10776-d00e252` cité par la carte. Lue en GET par la passerelle `outillage`, règle `github`.
- **Archives** (SHA-256 = `digest` publié par GitHub) : `llama-prism-b10777-e3de715-bin-win-cpu-x64.zip` (`cff7eeff…23c4`), `…-bin-win-cuda-12.4-x64.zip` (`fa5874a1…3462`), `cudart-llama-bin-win-cuda-12.4-x64.zip` (`8c79a9b2…d1e6`, identique à celle de b11429, réutilisée par lien dur). Binaires extraits (SHA calculés à l'extraction) : `bin-cpu/llama-server.exe` `42373a44…ff4b`, `bin-cuda/llama-server.exe` `e95c81a7…29d7`, `bin-cuda/ggml-cuda.dll` `385ccf23…0c27`. Pas d'archive des sources : Bonsai n'est ni converti ni quantifié.
- **Configuration** : `config/llamacpp/<tag>.toml`, au schéma de `config/llamacpp.toml` (tag de fork admis, `[sources]` devenu facultatif). Champ optionnel `llamacpp = "<tag>"` dans `config/modeles/<slug>.toml` (seul Bonsai le porte). Sans ce champ, le modèle garde la version commune b11429.
- **Résolution** : `serveur.config_llamacpp_modele(config)`. `ServeurLlama` la prend par défaut, donc le serveur, le banc (lm-eval, moteur LLM), les mesures et `fetch modeles` utilisent le binaire du modèle. L'assemblage d'évaluation sert la génération avec la version du modèle et l'embedding (BGE-M3) avec la version commune. Un `config_llamacpp` explicite contraire au modèle est refusé.
- **Consignation dans `run.json`** : `llamacpp_tag` (éval et sonde d'outils, banc dès qu'une cible est GGUF) et `tag_llamacpp` de la description des serveurs (éval, mesures). `measure run` compte la taille des binaires de la version du modèle de génération.
- **Fetch** : `slmsp fetch llamacpp --version prism-b10777-e3de715`, même mécanisme (archives vérifiées, extraction sans écrasement, binaires vérifiés) sous `vendor/llama.cpp/prism-b10777-e3de715/bin-{cpu,cuda}`. Run `runs/fetch/20261017-055925-llamacpp-fdce` (dépôt principal) : 2 archives téléchargées, cudart réutilisée.

## Essais (CPU, `--device none -ngl 0`, une question, T = 0)
Question : « Quelle est la capitale de la France ? Réponds en une phrase. »
- qwen3.5-2b (template HF forcé) : « La capitale de la France est Paris. » Débit de 25 tok/s.
- minicpm-v-4.7-1b : « La capitale de la France est Paris. » Débit de 30 tok/s.
- bonsai-2-4b : tokens incohérents et multilingues, 4,5 tok/s. Inutilisable en b11429.
- bonsai-2-4b avec `prism-b10777-e3de715` (CPU, par `ServeurLlama`, thinking désactivé, T = 0) : « La capitale de la France est Paris. » Une seconde question (« Explique en deux phrases ce qu'est une carte d'identité. ») reçoit deux phrases françaises cohérentes, avec une approximation de fond (« numéro de passeport »). La rotation est donc appliquée. Débit en génération de 5,3 à 6,5 tok/s, prompt à 8 tok/s : ces noyaux ternaires sont lents sur CPU, c'est à noter pour les mesures et la durée de la Baseline.

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
Bonsai : mêmes commandes avec `base:bonsai-2-4b`. Le binaire `prism-b10777-e3de715` est choisi par la configuration du modèle, sans option. Il faut d'abord `uv run slmsp fetch llamacpp --version prism-b10777-e3de715` (déjà fait dans le dépôt principal). `measure run` se lance sans `--quantification`, car le fichier porte Q2_0 et non Q4_K_M. Dans `eval run`, l'étiquette `q4_k_m` désigne la section `[gguf]`, qui est ici en Q2_0 : l'écart est à noter dans le comparatif. Le banc HF bf16 est exclu par décision d'Anaël (cible : PC sans GPU, 16 Go).

## Écarts et points à confirmer par Anaël
- **Contrôle `dense` (D7)** : Qwen3.5-2B et MiniCPM ont 18 couches `linear_attention` (Gated DeltaNet) sur 24. Le contrôle de la story 8.1 les « écarte », alors que D7 visait les hybrides Mamba. Le code n'a pas été modifié. Il faut décider s'il faut admettre `linear_attention`, et vérifier l'entraînement sous Windows : sans `flash-linear-attention` ni `causal-conv1d`, transformers bascule sur une implémentation torch lente. À confirmer par Anaël.
- **Bonsai et la température** : la carte recommande T = 0,7, top_p 0,8 et presence_penalty 1,5 en non-thinking. L'évaluation reste gloutonne (protocole commun, T = 0) : c'est un écart assumé.
- **MiniCPM et transformers** : le modèle déclare `minicpmv4_7` (config écrite avec transformers 5.18.0), alors que l'épinglage est en 5.17.0 et ne connaît que `minicpmv4_6`. L'entraînement et un éventuel adaptateur lm-eval HF sont donc reportés.
- `[gguf_f16]` est épinglé pour qwen3.5-2b et minicpm, mais n'a pas été téléchargé.

## Tests
- `tests/inference/test_serveur.py` : version par modèle (Bonsai réservé, tous les autres sur b11429), version absente refusée, champ `llamacpp` validé, `ServeurLlama` par défaut et `tag_llamacpp`, version explicite incohérente refusée, binaires sous `vendor/llama.cpp/<tag>/`.
- `tests/fetch/test_llamacpp.py` : `--version` sans sources (CLI de bout en bout), tag incohérent avec le nom du fichier, configuration réservée versionnée.
- `tests/evaluation/test_assemblage.py` : génération et `llamacpp_tag` sur la version réservée, embedding sur la commune.
- `tests/benchmarks/test_orchestrateur.py` : `llamacpp_tag` du run de banc (réservé, commun, sans GGUF, modèle inconnu) et consignation dans `run.json`.
- `tests/fetch/test_verifications.py` : `test_toml_modeles_octobre` (trois slugs) et `test_toml_modeles_octobre_particularites`.
- `tests/train/test_run.py` : `test_modele_non_entrainable_refuse`.

## Auto Run Result
- Slugs `qwen3.5-2b`, `bonsai-2-4b` et `minicpm-v-4.7-1b`, hors `CANDIDATS` : c'est le choix le plus réversible.
- Champ `entrainable` plutôt qu'une liste en dur, avec le refus placé dans `train.run.executer`. Le refus ne porte pas sur l'export ni sur `eval`.
- Pour Bonsai, `source = "officielle"`, car le dépôt est celui de l'éditeur Prism ML.
- Binaire réservé : `prism-b10777-e3de715` (épinglé par Bonsai-demo) plutôt que `prism-b10776-d00e252` (cité par la carte), car c'est la recommandation la plus récente de l'éditeur. Version réservée décrite par un fichier à part (`config/llamacpp/<tag>.toml`), pour ne pas changer l'empreinte de `config/llamacpp.toml` inscrite dans les runs existants.
- Banc : `llamacpp_tag` est rempli seulement pour une sélection avec cible GGUF. Il est laissé vide si la configuration du modèle est introuvable : le moteur signale alors l'erreur lui-même.
- `version()` (`llama-server --version`) renvoie `b10777` pour le binaire réservé, pas le tag du fork. Rien ne compare ce résultat au tag aujourd'hui ; c'est à garder en tête si un contrôle est ajouté.
- Débit CPU de Bonsai (environ 6 tok/s) : la génération v1.1 sera longue en CPU. La variante CUDA est épinglée et vérifiée, mais elle n'a pas été essayée (GPU occupé).

## Revue
Revue du commit e7b651e (rebasé en 5f58408), second avis Haiku puis Opus.
- medium, second avis, corrigé : `measure run` ne comptait que les binaires de la version de génération. `_composants` consigne maintenant les binaires de chaque version servie (génération et embedding) ; clés `binaires-<tag>-<variante>` s'il y en a deux, inchangées s'il n'y en a qu'une. Test `test_composants_binaires_des_deux_versions`.
- medium, second avis, écart consigné : seuls `llama-server.exe` et `ggml-cuda.dll` sont épinglés, comme pour b11429 ; les autres DLL (`llama.dll`, `ggml*.dll` CPU) ne le sont pas, ni dans b11429. Épinglage étendu non fait, pour garder le même niveau de contrôle sur les deux versions ; la protection des DLL reste celle des archives, vérifiées par SHA-256 avant extraction, et l'extraction ne remplace aucun fichier. La phrase « binaires vérifiés » désigne donc les seuls binaires épinglés de `[binaires]`, pas tous les fichiers extraits.
- low, second avis, corrigé : `--version` validé par `MOTIF_TAG` avant toute lecture (`fichier_config`) ; test `test_version_invalide_refusee_avant_lecture`.
- low, second avis, corrigé : `[sources]` redevient obligatoire pour `config/llamacpp.toml` (`verifier_config`, contrôle contextuel commun aux deux chargeurs) ; test `test_sources_obligatoires_pour_la_version_commune`.
- low, second avis, rejeté : la cudart n'est pas retéléchargée, `fetch` la réutilise déjà par lien dur (même SHA ; run `20261017-055925-llamacpp-fdce`, « cudart réutilisée »).

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

---

# Candidats < 2B (décision du 2026-10-17)

**CroissantLLM (`croissantllm-chat`) est retiré des candidats** (décision d'Anaël du 2026-10-17) : sa licence MIT n'est pas admise en sortie (`ordre_permissivite` ne contient que `apache-2.0`) et son contexte natif de 2048 jetons est trop court pour le RAG de la Tâche Q. Son entrée de `config/publication.toml` est supprimée, ainsi que sa fiche `config/modeles/croissantllm-chat.toml`, son slug et ses assertions dans `tests/fetch/test_verifications.py` et sa mention dans `outils/migration/exporter-etat.ps1` (retrait achevé par l'orchestrateur, les suppressions ayant été refusées à l'agent de revue par le contrôle de permissions). Les runs `fetch` gardent la trace de son téléchargement et de ses contrôles ; les fichiers de `models/croissantllm-chat` (5,8 Go) sont supprimés. Les lignes qui le concernent ci-dessous restent comme trace.

Trois modèles de moins de 2B s'ajoutent, hors `CANDIDATS` (choix le plus réversible). Épinglage (révisions, SHA-256 et tailles) relevé dans l'API HF, puis **recalculé sur les fichiers de `models/`** : tous concordent.

## Fiches
| Slug | Dépôt HF (révision) | GGUF | Licence | Particularités |
|---|---|---|---|---|
| `eurollm-1.7b` | `utter-project/EuroLLM-1.7B-Instruct` (a25c7fa) | `mradermacher/EuroLLM-1.7B-Instruct-GGUF` Q4_K_M (1,05 Go) et `[gguf_f16]` (3,32 Go), communautaire | Apache 2.0 | llama dense, contexte natif 4096, `chat_template_force = true` |
| `croissantllm-chat` | `croissantllm/CroissantLLMChat-v0.1` (f05665c) | `croissantllm/CroissantLLMChat-v0.1-GGUF` Q4_K_M (872 Mo), officiel, **pas de F16** | MIT | llama dense 1,3 Md, poids HF float32 (2 shards), **contexte natif 2048** |
| `qwen3.5-0.8b` | `Qwen/Qwen3.5-0.8B` (2fc0636) | `unsloth/Qwen3.5-0.8B-GGUF` Q4_K_M (533 Mo) et `[gguf_f16]` en **BF16** (1,52 Go), communautaire | Apache 2.0 | hybride Gated DeltaNet, `exclure_vision`, `enable_thinking = false`, `chat_template_force = true` |

- Valeurs communes : cache f16, `reasoning = "off"`, `protocole_outils = "natif"` (non sondé), `lm_eval_batch_size = 2` (portable de 6 Go ; jamais `auto`).
- `config/publication.toml` : trois entrées (apache-2.0, mit, apache-2.0), sans `verifie_le`. Aucune autre liste de slugs à mettre à jour (comme pour les modèles d'octobre ; hors `CANDIDATS`).
- Les fiches du WIP 8379099 (c7e31bc après rebase) ont été relues : SHA-256 et tailles exacts ; corrigés seulement les renvois de runs périmés et les mentions « F16 non téléchargé ».

## Runs et contrôles 8.1
Runs `fetch` : `20261017-184442-modeles-29f5` (trois slugs) et `20261017-185344-modeles-9f7d` (`--f16`, eurollm-1.7b et qwen3.5-0.8b).
| Modèle | dense | fp8 | vision | chat_template | serveur CPU |
|---|---|---|---|---|---|
| eurollm-1.7b | ok | ok (bf16) | ok | HF ≠ GGUF, exporté, forcé | prêt |
| croissantllm-chat | ok | ok (float32) | ok | identiques | prêt |
| qwen3.5-0.8b | **échec** : 18 couches `linear_attention` sur 24 | ok | ok (exclue) | HF ≠ GGUF, exporté, forcé | prêt |

Le contrôle `dense` n'a pas été modifié.

## Reports et points à confirmer par Anaël
- **CroissantLLM à contexte 2048** : le prompt RAG de la Tâche Q risque de ne pas tenir (budget de prompt, F2) ; et **sans GGUF F16** (banc « avant » à décider).
- **Qwen3.5-0.8B écarté par `dense`** : même décision à prendre que pour qwen3.5-2b (admettre `linear_attention` ou non, entraînement sous Windows).
- **`lm_eval_batch_size = 2`** : valeur prudente, à confirmer par mesure.
- EuroLLM-1.7B : contexte 4096, inférieur à 8192. Valeur prudente : `max_position_embeddings` du `config.json` HF vaut 4096, mais l'en-tête du GGUF mradermacher (Q4_K_M et f16) annonce `llama.context_length = 8192` (lu dans `models/` à la revue). Passer à 8192 demande une mesure de qualité au-delà de 4096.
- Licence de sortie de CroissantLLM (MIT) : sans objet, modèle retiré (voir plus haut).
- **Licences d'EuroLLM-1.7B et de Qwen3.5-0.8B non revérifiées** depuis l'épinglage (pas de réseau en revue) ; `verifie_le` absent, donc préparation refusée (« non relue ») jusqu'à la relecture d'Anaël.
- La branche est rebasée sur main 2dc2293, qui contient F3 (champ `lm_eval_batch_size` du schéma) : le test lit `config.lm_eval_batch_size` par le schéma.
- Les empreintes des fiches consignées dans `runs/fetch/20261017-184442-modeles-29f5/run.json` (et `20261017-185344-modeles-9f7d`) sont celles du WIP (commit 8379099 avant rebase, c7e31bc après), pas celles des fiches commitées : écarts limités à `lm_eval_batch_size`, aux commentaires, et au commentaire de contexte d'EuroLLM ajouté en revue ; révisions, SHA-256 et options servies identiques. Runs non modifiés (traces).
- Tests : `test_toml_modeles_moins_2b` et `test_toml_modeles_moins_2b_particularites` dans `tests/fetch/test_verifications.py`.

## Revue
Revue de c7e31bc et 9f459f5 (rebasés sur main 2dc2293), second avis Haiku puis Opus.
- medium, second avis, écarté (sans objet) : CroissantLLM (MIT) n'avait pas de licence de sortie, `mit` absente de `ordre_permissivite` et de `config/licences/` (constat exact) ; le modèle est retiré par décision d'Anaël (licence MIT non admise, contexte 2048). Ni licence MIT ni texte ajoutés.
- low, second avis, corrigé : la spec disait la branche partie de 03d8ccf, avant F3 ; faux depuis le rebase.
- low, second avis, corrigé : le test lit `config.lm_eval_batch_size` par le schéma, plus le TOML brut (`tomllib` retiré).
- low, second avis, consigné : empreintes des fiches des runs = celles du WIP ; runs laissés tels quels.
- low, second avis, corrigé : contexte EuroLLM, commentaire et spec précisés (HF 4096, GGUF 8192, 4096 gardé), vérifié sur les GGUF de `models/`.
- low, second avis, corrigé (commentaire) : `verifie_le` absent et licences non revérifiées, explicités dans `config/publication.toml` ; `verifie_le` non posé.
- low, revue, sans objet (modèle retiré) : poids HF float32 de CroissantLLM contre « lm_eval sur HF bf16 » ; `lm_eval.py` charge de toute façon `dtype=bfloat16`.
- low, revue, corrigé : `outils/migration/exporter-etat.ps1` (ligne 45) copie encore `models\croissantllm-chat`, retiré avec le dossier.
- low, revue, vérifié : aucun consommateur ne suppose 8192 (`contexte` lu par fiche dans `serveur`, `measure`, `assemblage`) ; `test_version_llamacpp_par_modele`, qui parcourt toutes les fiches, passe.
- Complexité : aucun constat (configuration et tests seulement).
