# Epic 2 Context: Moteurs locaux : modèles servis et Index local interrogeable

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Cet epic fournit les briques locales dont dépendent le Harnais, le banc d'évaluation, les Benchmarks et les mesures. Il comprend un téléchargeur unique et épinglé (llama.cpp, corpus MediaTech, BGE-M3), un pilotage propre de `llama-server` sous Windows en génération et en embedding, sans processus orphelin, et un Index local daté, interrogeable en recherche exacte. Il mesure aussi deux hypothèses d'architecture : H-VEC (latence et RAM de la recherche) et H-EMB (compatibilité de l'embedding de requête avec les vecteurs MediaTech). Sans cet epic, aucune réponse fondée sur des passages officiels ni aucune évaluation de modèle n'est possible.

## Stories

- Story 2.1 : Téléchargeur unique `slmsp fetch` (llama.cpp, corpus MediaTech, BGE-M3)
- Story 2.2 : Inférence par `llama-server` géré (génération et embedding)
- Story 2.3 : Index local : construction, recherche exacte et mesure H-VEC
- Story 2.4 : Mesure H-EMB : compatibilité de l'embedding de requête avec les vecteurs MediaTech

## Requirements & Constraints

- **Réponse fondée et datée** : les réponses s'appuient sur les passages de l'Index local, y compris hors ligne. La date du snapshot de l'Index doit être lisible, par le manifeste et par `index info`.
- **Budgets de performance de l'Assistant complet** : RAM ≤ 5 Go (cible 4 Go), premier token < 5 s pour une Question avec recherche dans l'Index. Le choix du corpus et de l'index en dépend.
- **Seuils des hypothèses** :
  - H-VEC : recherche exacte sur environ 143 k chunks (35 758 service-public et 107 679 catalogue data.gouv), avec p95 ≤ 300 ms et ≤ 350 Mo résidents. Si elle est infirmée, le repli (index usearch HNSW int8 en vue mappée, dérivé du même `.npy`, derrière `VectorStore`) est consigné comme à faire, sans être implémenté.
  - H-EMB : cosinus moyen ≥ 0,99 sur 200 chunks tirés avec une graine, et recall@10 en baisse de 2 points au plus. Sinon, la mesure est refaite avec le GGUF F16. La réindexation reste une décision d'Anaël.
  - Chaque résultat est consigné dans le journal des décisions de la nuit.
- **Périmètre de l'Index v1** : service-public et catalogue data.gouv seulement. Les autres sources (LEGI, travail-emploi, CNIL) attendent la mesure de la RAM.
- **Réseau** : tout téléchargement passe par le profil `outillage`. Le datasets-server de Hugging Face est instable : les parquet sont lus directement, avec reprises sur les erreurs 429 et 500.
- **Artefacts immuables** : rien n'est jamais supprimé ni écrasé (un fichier `.part` est repris, jamais effacé). Un index existant pour une même date n'est pas reconstruit. Toute écriture de plus de 1 Go vérifie d'abord l'espace libre.
- **Tests** : les vrais téléchargements sont marqués `reseau`, les exécutions réelles (vrai binaire, vraie construction, vraie mesure) `lent`. Chaque story les exécute au moins une fois et consigne le résultat.

## Technical Decisions

- **Téléchargeur unique** : `slmsp fetch {llamacpp, sources, modeles, benchmarks}`, sans autre téléchargeur dans le code.
  - Révisions épinglées par commit et SHA-256 vérifiés. Un SHA faux ne crée pas le fichier final. Un fichier déjà présent avec le bon SHA n'est pas retéléchargé.
  - Client HF injecté par `huggingface_hub.set_client_factory(net.fabrique_hf())`, avec `HF_HOME=models/.cache-hf` et la télémétrie coupée. `HF_TOKEN` n'est remis qu'au client HF.
  - Les transferts hf-xet échappent au client Python : ils sont journalisés au niveau de l'appel (dépôt, fichier, révision, octets).
  - Dispositions : `vendor/llama.cpp/b11429/{bin-cpu,bin-cuda,src}`, `data/raw/mediatech/<jeu>/<revision>/`, `models/<slug>/{hf,hf-bf16,gguf}/`.
  - Chaque exécution écrit un run `runs/fetch/<run_id>/` (fichier, révision, SHA).
  - `fetch` ne lance jamais de binaire llama.cpp.
- **llama.cpp figé au tag `b11429`** (base de la release stable v0.6.0, pas la pré-version b11560). Assets : `win-cpu-x64`, `win-cuda-12.4-x64` avec `cudart`, et l'archive des sources du même tag. Le paquet `gguf` s'installe depuis `src/gguf-py` de ce tag.
- **Seul lanceur llama.cpp** : `slmsp.inference.serveur` lance `llama-server`, `llama-quantize` et `convert_hf_to_gguf.py`.
  - Il expose `version(variante)`, `convertir_hf_vers_gguf` et `quantifier`, réutilisés plus tard par les stories 8.1 et 10.6.
  - Le serveur écoute sur `127.0.0.1`, sur un port libre, et se pilote par l'API compatible OpenAI en flux.
  - Les paramètres viennent de `config/modeles/<slug>.toml` : contexte, cache KV, threads, `reasoning`, `chat_template_kwargs`, `protocole_outils` (`natif` ou `json-generique`), `chat_template_force`. Les évaluations tournent avec `--parallel 1`, et la variante (`cpu` ou `cuda`) est inscrite dans `run.json`.
  - L'Assistant lance deux instances au plus : génération (`--jinja`) et embedding (`--embedding --pooling cls`).
- **Processus Windows** : chaque processus est lancé dans un Job Object `KILL_ON_JOB_CLOSE` (par `ctypes`), avec `CREATE_NO_WINDOW`.
  - Son PID et son port sont inscrits dans `SLMSP_VAR_DIR/pids/`. Les orphelins sont nettoyés au démarrage et consignés.
  - Les sous-processus reçoivent `env_sous_processus()`, sans aucune clé d'API.
- **Adaptateurs de ports** :
  - `LlmPort` : flux de tokens, `tool_calls` au format canonique OpenAI, `temperature` et `seed` transmis, usage et délai au premier token, `compter_tokens` par `/tokenize`. Avec `json-generique`, les outils passent par `response_format` (schéma JSON) et la sortie est reconvertie en `tool_calls`.
  - `EmbedderPort` : vecteurs float32 de dimension 1024, normalisés L2. Le même embedder sert au Harnais, à l'anti-fuite et à la déduplication.
  - Les échanges HTTP avec le serveur passent uniquement par `net.client_local(port)` : la boucle locale n'est permise que vers les ports des `llama-server` gérés.
- **Format de l'Index** : `index/<AAAAMMJJ>/` (version = date du snapshot), en lecture seule.
  - `vectors.f16.npy` : N × 1024, float16, normalisé L2, ouvert en `numpy.memmap`.
  - `chunks.sqlite` : `chunk_id`, `doc_id`, `source`, `titre`, `url`, `texte`, `date_snapshot`. La ligne `i` correspond au vecteur `i`.
  - `MANIFEST.json` : SHA-256 des fichiers, date du snapshot, modèle d'embedding, nombre de chunks par source. Schéma dans `core/schemas/manifeste_index.py`.
  - Les vecteurs du corpus sont ceux de MediaTech, lus depuis la colonne JSON et jamais recalculés. La requête est vectorisée par `ggml-org/bge-m3-Q8_0-GGUF`.
- **Recherche exacte** : produit scalaire par blocs sur le memmap, avec top-k. Le résultat doit être identique à une recherche de référence numpy float32. Taille de bloc, k et seuil de pertinence sont dans `config/index.toml`. Aucune bibliothèque vectorielle en v1.
- **Séparation construction et lecture** : `slmsp.indexation` (couche 3, extra `data`, pyarrow) construit l'index et fait les mesures. `slmsp.index` (couche 1b, runtime) lit l'index et n'importe jamais pyarrow ni duckdb (le test d'architecture le vérifie).
- **Mesures** : résultats au schéma `ResultatMesure` (`core/schemas/mesure.py`, première version créée par 2.3), dans `runs/measure/<run_id>/`. H-VEC : 200 requêtes tirées du corpus avec une graine, latences p50 et p95, mémoire résidente ajoutée. Le protocole RAM global (somme des working sets de l'arbre de processus, binaire CPU) relève de l'Epic 6.
- **Épinglages utiles** : numpy 2.5.4, pyarrow 26.0.0 (extra `data`), huggingface-hub 2.2.0 (extra `fetch`), psutil 7.2.2.

## Cross-Story Dependencies

- 2.1 et 2.2 dépendent seulement de la story 1.4 (passerelle réseau) et peuvent tourner en parallèle, car leurs zones de fichiers sont disjointes. 2.3 dépend de 2.1 et 2.2, et 2.4 de 2.3. Les stories 2.3 et 2.4 partagent `cli/index.py` : 2.4 y ajoute `index verifier-embedding`.
- La sous-commande `fetch benchmarks` délègue à `slmsp.fetch.benchmarks` (story 6.1). Elle répond « non implémentée » tant que ce module n'existe pas.
- `core/schemas/mesure.py` est créé par 2.3 puis étendu par la story 6.4.
- En aval, l'Index (2.3) est requis par le Harnais (4.2, 4.5) et par la validation des données (9.5). Le téléchargeur et l'inférence (2.1, 2.2) sont requis par les modèles candidats (8.1), les Benchmarks (6.1 à 6.3), l'évaluation (5.3) et l'export GGUF (10.6).
