---
title: 'Story 2.2 : inférence par llama-server géré (génération et embedding)'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '436a972f697ae0d7ab05a029ff6b6070bdc7c733'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      LlmPort.generer ne déclare pas AppelNonConforme parmi les évènements du flux, alors que ClientLlama en émet.
    evidence: |-
      core/ports.py annonce Iterator[Jeton | AppelOutil | Fin] ; client.py rend AppelNonConforme pour des arguments illisibles. Un consommateur typé sur le port peut l'ignorer. core/ports.py est hors de la zone de la story 2.2.
    location: >-
      src/slmsp/core/ports.py (LlmPort.generer)
    severity: medium
---

<intent-contract>

## Intent

**Problem:** Aucun module ne lance ni n'interroge encore llama.cpp. Le Harnais, le banc, les Benchmarks, la conversion et l'export ont besoin d'un seul lanceur (AD-6), sans processus orphelin sous Windows (AD-27), et de deux adaptateurs de ports (`LlmPort`, `EmbedderPort`).

**Approach:** `inference/processus.py` lance tout sous-processus dans un Job Object `KILL_ON_JOB_CLOSE` (créé suspendu, assigné, puis repris), l'inscrit dans `SLMSP_VAR_DIR/pids/` et nettoie les orphelins. `inference/serveur.py` construit les lignes de commande depuis `ConfigModele` et `ConfigLlamacpp` (serveur, `version`, conversion, quantification). `client.py` et `embedding.py` parlent au serveur par `net.client_local(port)` seulement.

## Boundaries & Constraints

**Always:**
- Binaires pris sous `<vendor>/llama.cpp/<tag>/bin-<variante>/`, avec `<vendor>` = `SLMSP_VENDOR_DIR` s'il est défini, sinon `racine_projet()/vendor`. Le SHA-256 d'un binaire listé dans `config.binaires` est vérifié avant le premier lancement (une fois par processus).
- Tout sous-processus : `env_sous_processus()` (aucun secret), `CREATE_NO_WINDOW`, Job Object, sortie redirigée vers un fichier (jamais un tube non lu pour un serveur).
- Serveur : `--host 127.0.0.1 --port <libre> -m <gguf> -c <contexte> -ctk/-ctv <cache_kv> --parallel 1 --no-webui`, `-t` si `threads`, génération : `--jinja --reasoning <reasoning>`, `--chat-template-kwargs <json>` si non vide, `--chat-template-file models/<slug>/chat_template.jinja` si `chat_template_force` ; embedding : `--embedding --pooling <pooling>` (sans `--jinja`).
- Variante `cuda` : le serveur prend `verrou_gpu()` pendant sa vie (sauf `prendre_verrou_gpu=False`, quand l'appelant le tient déjà).
- `quantifier` et `convertir_hf_vers_gguf` refusent une sortie existante (`ArtefactExistant`) ; la conversion lance `convert_hf_to_gguf.py` de `src/` du tag avec `PYTHONPATH` préfixé par `src/gguf-py` du même tag.
- Évènements du flux : `Jeton`, `AppelOutil` (arguments en objet JSON), `AppelNonConforme` (arguments illisibles), puis un seul `Fin` dont `usage` porte `prompt_tokens`, `completion_tokens`, `total_tokens` et `delai_premier_token_ms`.

**Never:** importer `httpx`/`httpx2` ou toute bibliothèque HTTP dans `inference/` ; écrire hors de `inference/` et `tests/inference/` (pas de `config/inference.toml`, pas de `pyproject.toml`) ; composer ou modifier les messages du prompt (AD-7) ; télécharger quoi que ce soit ; lancer `llama-server` sans Job Object.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Flux texte | SSE `delta.content` puis `finish_reason=stop`, chunk `usage` | `Jeton`… puis `Fin(terminee, usage+délai)` | — |
| Appel natif | `delta.tool_calls` fragmentés par `index` | un `AppelOutil` par index, arguments réassemblés | arguments non JSON objet : `AppelNonConforme` |
| json-generique | `tools` + `protocole_outils="json-generique"` | requête sans `tools`, avec `response_format` json_schema ; sortie `{"tool_calls":[…]}` → `AppelOutil`, `{"content":…}` → `Jeton` | JSON illisible : `Jeton` du texte brut |
| Longueur | `finish_reason=length` | `Fin(raison="longueur")` | — |
| Flux coupé | fin sans `[DONE]` ni `finish_reason` | `Fin(raison="interrompue")` | — |
| HTTP ≠ 200 | 400/500 du serveur | — | `ErreurInference` (statut, extrait du corps) |
| Embedding | `vectoriser(["a","b"])` | `(2, 1024)` float32, normes 1 | dimension ≠ 1024 ou vecteur nul : `ErreurInference` ; liste vide : `(0, 1024)` |
| Démarrage raté | le processus meurt ou `/health` ≠ 200 avant le délai | processus arrêté, entrée `pids/` retirée | `ErreurInference` avec la fin du journal |
| Binaire absent / SHA faux | `vendor/` incomplet | aucun lancement | `ConfigurationInvalide` |
| Orphelin | entrée `pids/` vivante, parent mort (PID + date de création) | processus tué, ligne `arrete` dans `pids/nettoyage.jsonl` | — |
| Entrée périmée | processus disparu | entrée retirée, ligne `disparu` | — |

</intent-contract>

## Code Map

- `src/slmsp/core/schemas/config_modele.py` -- `ConfigModele` : `contexte`, `cache_kv`, `threads`, `reasoning`, `chat_template_kwargs`, `protocole_outils`, `chat_template_force`, `embedding`, `pooling`, `gguf.fichier`. Pas de chemin : le GGUF est `dossier_modeles()/<slug>/gguf/<gguf.fichier>` (ou `gguf=` explicite).
- `src/slmsp/core/schemas/config_llamacpp.py` -- `ConfigLlamacpp.tag`, `.binaires` (chemin relatif → SHA). `config/llamacpp.toml` : `b11429`, SHA de `bin-cpu/llama-server.exe` et `bin-cuda/llama-server.exe`.
- `src/slmsp/fetch/config.py` -- `charger_config_llamacpp`, `charger_config_modele(slug)` : réutilisables (inference est couche 2, fetch couche 4 : **ne pas importer**) ; recopier l'appel `charger_toml(racine_projet()/"config"/…, Modele)`.
- `src/slmsp/core/config.py` -- `env_sous_processus()`, `racine_projet()`, `dossier_modeles()`, `charger_toml`.
- `src/slmsp/core/var.py` -- `dossier_var()`, `verrou_gpu(attendre, delai, commande)` (contextmanager, refuse la ré-entrée dans un même processus).
- `src/slmsp/core/artefacts.py` -- `ajouter_jsonl(chemin, obj)`, `ArtefactExistant`.
- `src/slmsp/core/erreurs.py` -- `SlmspError`, `ConfigurationInvalide`.
- `src/slmsp/core/ports.py` -- `LlmPort.generer(messages, *, tools, options)`, `compter_tokens(messages, tools)`, `EmbedderPort.dimension`, `vectoriser`.
- `src/slmsp/core/evenements.py` -- `Jeton`, `AppelOutil(id, nom, arguments)`, `AppelNonConforme(nom, arguments_bruts, motif)`, `Fin(raison, usage: dict[str,int])`.
- `src/slmsp/net/client.py` -- `client_local(port, transport_interne=None)` : `httpx2.Client` limité à `http://127.0.0.1:<port>`, délai `config.delais.local` ; `.stream("POST", url, json=…)`, `.iter_lines()`, `.post`, `.get`.
- `tests/conftest.py` -- garde réseau (boucle locale permise), `SLMSP_VAR_DIR` temporaire par test.
- `tests/test_architecture.py` -- `inference` couche 2, paquet runtime (pas de bibliothèque lourde), clients HTTP interdits hors `net`.
- `pyproject.toml` -- marqueurs stricts `reseau`, `gpu`, `lent` (exclus par défaut) ; `psutil==7.2.2` et `numpy` disponibles.
- Relevés réels (2026-10-12) : `llama-server --version` écrit `version: 0.6.0-dev (build 11429, commit d81235049)` ; Granite 1B prêt en 1,7 s, `/health` → `{"status":"ok"}` ; SSE OpenAI avec dernier chunk `choices: []` + `usage` si `stream_options.include_usage` ; `tool_calls` natifs fragmentés (`index`, `id`, `function.arguments`) puis `finish_reason="tool_calls"` ; `/tokenize` → `{"tokens":[…]}` ; `/apply-template` → `{"prompt": …}` ; BGE-M3 `/v1/embeddings` → `data[i].embedding` de 1024, norme 1.
- Fichiers lourds (dépôt principal, lecture seule) : `vendor/llama.cpp/b11429/{bin-cpu,bin-cuda,src}`, `models/granite-4.0-1b/gguf/granite-4.0-1b-Q4_K_M.gguf` (SHA `22ec0f9c…d7f1`), `models/bge-m3/gguf/bge-m3-q8_0.gguf`.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/inference/processus.py` -- `CREATE_NO_WINDOW`, `JobObject` (ctypes : `CreateJobObjectW`, `SetInformationJobObject` étendu `KILL_ON_JOB_CLOSE`, `AssignProcessToJobObject`, `NtResumeProcess`), `EntreePid` (pid, port, role, parent_pid, parent_creation, creation, commande, demarre_le), `dossier_pids()`, `lancer(arguments, *, role, port, journal, env, cwd) -> ProcessusGere` (`arreter(delai)`, `vivant`, `code_retour`), `executer(arguments, *, delai) -> (code, sortie)` pour les commandes courtes ou longues, `nettoyer_orphelins() -> list[dict]` -- AD-27.
- `src/slmsp/inference/serveur.py` -- `Variante`, `ErreurInference`, `dossier_llamacpp`, `binaire(nom, variante)`, `version(variante)`, `commande_conversion`/`convertir_hf_vers_gguf`, `commande_quantification`/`quantifier`, `ServeurLlama(config, variante, *, slug|gguf, …)` : `arguments(port)`, `demarrer()`, `arreter()`, contexte `with`, `port`, `pid`, `description()` (pour `run.json`), `client()`, `embedder()` ; constantes de délai documentées (démarrage 180 s, arrêt 10 s, sonde 0,25 s).
- `src/slmsp/inference/client.py` -- `ClientLlama(port, *, protocole_outils, chat_template_kwargs, transport_interne)` : `generer` (flux SSE, options autorisées `temperature`, `seed`, `max_tokens`, `top_p`, `top_k`, `stop`, `chat_template_kwargs` ; inconnue → `ValueError`), `compter_tokens` (`/apply-template` puis `/tokenize`), `schema_json_generique(tools)`, `appel_canonique(AppelOutil)`.
- `src/slmsp/inference/embedding.py` -- `EmbedderLlama(port, *, dimension=1024, taille_lot=64, transport_interne)` : `vectoriser` par `/v1/embeddings`, tri par `index`, float32, renormalisation L2.
- `src/slmsp/inference/__init__.py` -- docstring du paquet (exports légers).
- `tests/inference/serveur_factice.py` -- serveur HTTP en thread (stdlib `http.server`) scénarisable : `/health`, `/v1/chat/completions` (SSE), `/tokenize`, `/apply-template`, `/v1/embeddings` ; enregistre les requêtes ; exécutable en script (`--port`, arguments llama ignorés) pour les tests de `ServeurLlama`.
- `tests/inference/conftest.py` -- marqueur `integration` enregistré ; fixtures `vendor_reel`, `modeles_reels` (saut si absents).
- `tests/inference/test_processus.py`, `test_serveur.py`, `test_client.py`, `test_embedding.py` -- matrice ci-dessus ; parent Python tué → enfant tué par le Job Object ; orphelin nettoyé ; tests réels `lent` + `integration` (Granite 1B CPU : quelques tokens, débit mesuré ; BGE-M3 CPU ; deux instances ; `version` cpu et cuda).

**Acceptance Criteria:**
- Given une `ConfigModele`, when `ServeurLlama(config, variante).arguments(port)` est construit, then il contient exactement les options tirées de la config et le binaire de `bin-<variante>/` du tag ; `lancer` reçoit `env_sous_processus()`.
- Given un serveur démarré par un processus Python, when ce parent est tué, then l'enfant meurt (Job Object) ; and `nettoyer_orphelins()` tue une entrée vivante sans parent et la consigne.
- Given un serveur de génération, when `generer(messages, tools, {"temperature": 0, "seed": 42})`, then `temperature` et `seed` figurent dans la requête, les jetons arrivent en flux, et `Fin.usage` porte l'usage et `delai_premier_token_ms`.
- Given `protocole_outils="json-generique"`, when `generer` reçoit des outils, then la requête porte `response_format` (json_schema) et la sortie devient des `AppelOutil`.
- Given BGE-M3 servi, when `vectoriser(textes)`, then float32 `(n, 1024)` de norme 1.
- Given génération et embedding démarrés ensemble, then deux ports distincts de `127.0.0.1`, deux entrées dans `pids/`.
- Given `inference/`, then aucune importation de bibliothèque HTTP (test d'architecture et ruff TID251) ; les requêtes passent par `net.client_local`.
- Given `vendor/` installé, when `version("cpu")` et `version("cuda")`, then `"b11429"` ; `commande_conversion` et `commande_quantification` n'utilisent que des chemins du tag et `env_sous_processus()`.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 43 findings — high 0, medium 9, low 26, false 7, maybe-false 1
- findings:
  - `[medium]` `[patch]` (BH) SHA : `bin-cuda/ggml-cuda.dll`, listé dans `binaires`, jamais vérifié — tout fichier listé sous `bin-<variante>/` est vérifié avant le premier lancement (refus des binaires non listés : non retenu, politique nouvelle).
  - `[low]` `[reject]` (BH) SHA du GGUF non vérifié au lancement, absent de `description()` — `fetch` vérifie le SHA au téléchargement ; hacher 1 à 5 Go à chaque démarrage coûte plusieurs secondes ; la config (avec le SHA) est archivée dans `run.json`.
  - `[medium]` `[patch]` (BH) embedding : entrées de plus de 512 tokens refusées (ubatch par défaut) — `-b`/`-ub` = `contexte` en mode embedding, test réel avec un texte long.
  - `[low]` `[patch]` (BH) `reasoning_content` ignoré : délai au premier token sous-estimé quand le raisonnement est actif — le premier `reasoning_content` non vide fixe `premier`.
  - `[low]` `[reject]` (BH) json-generique tronqué rendu en `Jeton` brut — comportement imposé par la matrice (« JSON illisible : Jeton du texte brut ») ; le changer revient à modifier la spec.
  - `[low]` `[reject]` (BH) pas de `Fin` après une erreur en flux, cause d'une coupure non consignée — l'erreur en flux lève `ErreurInference` (même contrat que HTTP ≠ 200) ; journaliser la cause ajoute du code pour un cas rare.
  - `[low]` `[patch]` (BH) `_executer_vers` : paramètre `nom` inutilisé, message qui nomme l'interpréteur — `nom` utilisé.
  - `[false]` `[reject]` (BH) `os.rename` écrase sous POSIX — projet Windows seul (D2) : `os.rename` y échoue si la cible existe.
  - `[low]` `[reject]` (BH) `AccessDenied` classé `disparu` — seuls nos propres processus (même utilisateur) sont inscrits ; psutil lit leur date de création sans droit élevé.
  - `[false]` `[reject]` (BH) `arreter` sans job ne tue pas l'arbre — sous Windows (seule cible) le job existe toujours et `TerminateJobObject` tue l'arbre (test `test_arreter_tue_les_petits_enfants`).
  - `[low]` `[reject]` (BH) course sur le port libre — fenêtre de quelques millisecondes ; une relance ajouterait une boucle pour un cas non observé.
  - `[medium]` `[patch]` (BH) ids d'appel `appel-<i>` répétés d'un tour à l'autre — ids uniques (`appel-<uuid>`).
  - `[maybe-false]` `[patch]` (BH) `compter_tokens` jamais comparé au compte du serveur — assertion ajoutée au test réel Granite (`compter_tokens == usage.prompt_tokens`) : égalité vérifiée sur Granite, aucun correctif de code nécessaire.
  - `[low]` `[reject]` (BH) fixtures réelles exigeant cpu et cuda, tag `b11429` codé en dur — poste de dev équipé des deux ; le tag égale celui de la config (AC8).
  - `[low]` `[patch]` (BH) chemins non testés (nettoyage au démarrage, coupure réelle du flux) — couverts par les tests ajoutés pour VG ; le reste (`.tmp` orphelins, types de `port`/`role`) rejeté : cas rares.
  - `[medium]` `[patch]` (EC) ubatch embedding — même correctif que BH.
  - `[low]` `[reject]` (EC) chunk SSE mal typé → `AttributeError` — serveur épinglé au tag, format relevé ; garde sans cas réel.
  - `[low]` `[patch]` (EC) `reasoning_content` — même correctif que BH.
  - `[low]` `[reject]` (EC) `compter_tokens` : corps 200 non JSON — serveur épinglé, cas non observé.
  - `[low]` `[reject]` (EC) embedding : corps 200 non JSON — même motif.
  - `[medium]` `[defer]` (EC) `LlmPort.generer` ne déclare pas `AppelNonConforme` — `core/ports.py` hors zone ; à élargir par la story 4.2 (Harnais).
  - `[low]` `[reject]` (EC) `AccessDenied` — même motif que BH.
  - `[low]` `[reject]` (EC) échec de `kill` : entrée retirée et `arrete` consigné — cas non observé, ajout d'une branche d'échec.
  - `[low]` `[reject]` (EC) fichiers `.tmp` orphelins dans `pids/` — interruption entre deux appels système, rare.
  - `[low]` `[patch]` (EC) `executer(journal=...)` sans dossier parent → `FileNotFoundError` — dossier créé.
  - `[false]` `[reject]` (EC) branche non Windows (groupe de processus, `NoSuchProcess`) — projet Windows seul (D2).
  - `[low]` `[reject]` (EC) course sur le port — même motif que BH.
  - `[low]` `[patch]` (EC) `nom` inutilisé — même correctif que BH.
  - `[false]` `[reject]` (EC) `os.rename` sous POSIX — même réfutation que BH.
  - `[low]` `[reject]` (EC) `PYTHONPATH` hérité et interpréteur hors tag — `python=` est fourni par l'appelant (8.1) ; `uv run` ne pose pas de `PYTHONPATH`.
  - `[medium]` `[patch]` (VG) coupure de transport en cours de flux jamais exercée — scénario factice au corps tronqué, `Fin(interrompue)` attendu.
  - `[medium]` `[patch]` (VG) `demarrer()` → `nettoyer_orphelins()` non vérifié — test : entrée périmée retirée au démarrage, ligne `disparu`.
  - `[medium]` `[patch]` (VG) échec de démarrage `cuda` : libération du verrou GPU non testée — test ajouté (le code la fait déjà par l'`ExitStack`).
  - `[low]` `[patch]` (VG) retour arrière de `_lancer` jamais exécuté — test avec `reprendre_processus` en échec.
  - `[low]` `[patch]` (VG) `executer` : dossier du journal — même correctif que EC.
  - `[low]` `[patch]` (VG) `nom` inutilisé — même correctif que BH.
  - `[false]` `[reject]` (IA) tests réels optionnels sans exécution consignée — exécutés (6 passés, débit mesuré), consignés dans `## Auto Run Result`.
  - `[low]` `[reject]` (IA) nettoyage des orphelins au seul démarrage du serveur (lecture R4a) — AD-27 et la spec le placent dans `slmsp.inference` au démarrage d'un serveur.
  - `[false]` `[reject]` (IA) `tool_calls` rendus en `AppelOutil` plutôt qu'en dict — `AppelOutil` est l'évènement du port (AD-14) ; `appel_canonique` donne la forme AD-7.
  - `[low]` `[reject]` (IA) le test réel json-generique n'exige pas un `AppelOutil` — dépend du modèle ; l'exécution réelle a bien produit `AppelOutil(meteo)`.
  - `[medium]` `[patch]` (IA) SHA de `ggml-cuda.dll` jamais vérifié — même correctif que BH.
  - `[low]` `[reject]` (IA) `SLMSP_VENDOR_DIR` absent de `.env.example` — fichier hors zone ; documenté dans les docstrings et le compte rendu.
  - `[false]` `[reject]` (IA) `--embedding --pooling` dans `serveur.py` et non `embedding.py` — ce sont des options de la ligne de commande du serveur ; `embedding.py` est l'adaptateur HTTP.

## Design Notes

- Job Object sans fenêtre de course : `Popen(creationflags=CREATE_SUSPENDED | CREATE_NO_WINDOW)`, assignation par `proc._handle`, puis `ntdll.NtResumeProcess`. Le handle du job n'est pas héritable ; sa fermeture (mort du parent ou `arreter`) tue l'arbre.
- Identité d'un processus du registre = PID + `create_time` (psutil) : un PID recyclé n'est jamais tué.
- `json-generique` : `tools` n'est pas transmis (le template du modèle ne le gère pas) ; le schéma est `anyOf` de `{"tool_calls":[{"name": const, "arguments": paramètres}]}` et `{"content": string}`. Décrire les outils dans le prompt reste l'affaire du Harnais (AD-7).

## Verification

**Commands:**
- `uv run pytest tests/inference` -- expected: tout passe, sans binaire réel.
- `SLMSP_VENDOR_DIR=<principal>/vendor SLMSP_MODELS_DIR=<principal>/models uv run pytest tests/inference -m integration -s` -- expected: tests réels passés, débit affiché.
- `uv run pytest` et `uv run ruff check` et `uv run ruff format --check` -- expected: aucun nouvel échec.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** Paquet `slmsp.inference`, seul lanceur llama.cpp (AD-6, AD-27) :
- `processus.py` : Job Object `KILL_ON_JOB_CLOSE` (processus créé suspendu, assigné, puis repris), registre `SLMSP_VAR_DIR/pids/` (PID et date de création), nettoyage des orphelins consigné dans `pids/nettoyage.jsonl`, `lancer` et `executer` ;
- `serveur.py` : `ServeurLlama` (ligne de commande tirée de `ConfigModele`, port libre sur `127.0.0.1`, attente de `/health`, verrou GPU en `cuda`), `version`, `convertir_hf_vers_gguf` et `quantifier` (écriture en `.part`, jamais d'écrasement), SHA des binaires vérifié ;
- `client.py` (`LlmPort`) : flux SSE, `tool_calls` natifs ou `json-generique` par `response_format`, usage et délai au premier token, `compter_tokens` ;
- `embedding.py` (`EmbedderPort`) : float32 de dimension 1024, norme 1.

Commits `741b6cb619ab2d8d63e4ffc6f65c44375e44b276` (implémentation) et `115258887962ec6e4e1a2d26c475a22f52c5edef` (correctifs de revue).

**Fichiers.**
- `src/slmsp/inference/{__init__,processus,serveur,client,embedding}.py` : modules décrits ci-dessus.
- `tests/inference/serveur_factice.py` : serveur HTTP factice scénarisable (stdlib), aussi exécutable en script.
- `tests/inference/conftest.py` : marqueur `integration`, `vendor/` factice, fixtures réelles (sautées si absentes).
- `tests/inference/test_{processus,serveur,client,embedding}.py` : 66 tests hors binaire réel, 6 tests réels `lent` et `integration`.

**Revue (1 passe, 4 couches).** 43 constats : 11 entrées corrigées (patch), 1 différée (frontmatter `deferred`), les autres rejetées avec motif (triage ci-dessus). Patchs à leur verdict d'entrée : 0 high, 6 medium (SHA des DLL de la variante, `-b`/`-ub` en embedding, ids d'appel uniques, test de coupure de flux, test du nettoyage au démarrage, test du verrou GPU après un échec cuda), 4 low, 1 maybe-false (comparaison `compter_tokens`, égalité vérifiée). Relecture complémentaire recommandée (`followup_review_recommended: true`) : la variante `cuda` n'a été lancée en réel que par `--version`, jamais en serveur (GPU non exigé cette nuit). La mort du parent n'a été éprouvée qu'avec des processus Python factices, pas avec le lanceur réel `llama-server.exe` (9 Ko, qui charge `llama-server-impl.dll`).

**Vérification** (2026-10-12) :
- `uv run pytest tests/inference` : 66 passés.
- `uv run pytest` : 1153 passés, 118 sautés, 9 désélectionnés.
- `ruff check` et `ruff format --check` : propres.
- Tests réels, avec `SLMSP_VENDOR_DIR` et `SLMSP_MODELS_DIR` sur le dépôt principal et `-m integration -s` : 6 passés en 17 s.
  - `version` cpu et cuda : `b11429`.
  - Granite 1B Q4_K_M en CPU : prêt en 1,2 s, premier token en 164 ms, 32 tokens à 42,5 tokens/s. `compter_tokens` est égal à `prompt_tokens`.
  - Granite en `json-generique` : `AppelOutil(meteo, {"ville": "Lyon"})`.
  - BGE-M3 en CPU : `(n, 1024)` float32 de norme 1, dont un texte d'environ 2 000 tokens.
  - Deux instances (génération et embedding) : ports distincts, deux entrées `pids/`, arrêt propre.

**Risques résiduels.**
- `convertir_hf_vers_gguf` prend par défaut l'interpréteur courant, sans torch ni transformers : la story 8.1 doit passer `python=`. `quantifier` n'a pas tourné sur le vrai binaire.
- Course théorique sur le port libre (choisi puis relâché avant le lancement).
- `LlmPort` ne déclare pas `AppelNonConforme` (différé, story 4.2).
- `SLMSP_VENDOR_DIR` est documenté dans les docstrings seulement, pas dans `.env.example` (hors zone).

**Décisions prises seul** (à reporter au journal) :
1. `SLMSP_VENDOR_DIR` (défaut `<racine>/vendor`) permet à un worktree d'utiliser le `vendor/` du dépôt principal.
2. Les délais (démarrage 180 s, arrêt 10 s, sonde 0,25 s, `--version` 60 s) sont des constantes documentées de `inference/`, faute de fichier de config dans la zone de la story. À déplacer dans `config/` plus tard (AD-22).
3. `--parallel 1` est toujours passé, et aucun `-ngl` n'est ajouté (llama.cpp choisit `auto`). La variante `cuda` prend `verrou_gpu()` pendant toute la vie du serveur (`prendre_verrou_gpu=False` si l'appelant le détient déjà) ; `version()` ne le prend pas.
4. En `json-generique`, `tools` n'est pas transmis au serveur. Le schéma est `anyOf` `{"tool_calls": [...]}` ou `{"content": ...}`, et un JSON illisible donne un `Jeton` brut.
5. Des arguments d'outil illisibles donnent un évènement `AppelNonConforme`, hors du type déclaré par `LlmPort`. Les ids générés sont `appel-<uuid4>`.
6. `Fin.usage` porte `delai_premier_token_ms`, sans modifier `core/evenements.py`. Le raisonnement compte pour ce délai mais n'est pas émis.
7. Le GGUF n'est pas re-haché à chaque démarrage : `fetch` le vérifie au téléchargement.
8. Les entrées `pids/` des processus arrêtés ou disparus sont supprimées : ce sont des fichiers d'état, pas des données.
9. Les journaux des serveurs vont dans `SLMSP_VAR_DIR/journaux/`. Conversion et quantification écrivent en `<sortie>.part`, et un `.part` existant bloque la relance (`ArtefactExistant`).
10. Les tests réels portent les marqueurs `lent` et `integration`. `integration` est enregistré par `tests/inference/conftest.py`, sans toucher à `pyproject.toml`.
