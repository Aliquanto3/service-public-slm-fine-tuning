---
title: 'Story 8.1 — Téléchargement et préparation des Modèles de base candidats'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '16a78dd83ded94cf1eedc60f642c8e1f28ce9046'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-8-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Un run lancé depuis un worktree avec --racine sur le dépôt principal inscrit dans run.json le commit du dépôt principal, pas celui du code exécuté.
    evidence: |-
      runs/fetch/20261012-130043-modeles-2524/run.json : git_commit 79f5a3a… et git_modifie false, alors que verifications.py et les TOML candidats n'existaient que dans le worktree, non commités. Comportement de core.artefacts, déjà présent pour les runs de la story 2.1.
    location: >-
      src/slmsp/core/artefacts.py (nouveau_run)
    severity: medium
---

<intent-contract>

## Intent

**Problem:** Les cinq Modèles de base candidats de D4 sont préchargés sous `<dépôt principal>/models/<slug>/{hf,gguf}/` (révisions et SHA dans `models/PRECHARGEMENT.md`, recoupés avec l'API Hugging Face le 2026-10-12 : 46 fichiers conformes). Mais aucun `config/modeles/<slug>.toml` ne les épingle, et aucun contrôle D7 n'est codé : dense, FP8, vision, chat template, démarrage de `llama-server`. Deux reports de la 2.1 bloquent aussi la reprise : un fichier HF non LFS (`config.json`, tokenizer) est refusé faute de SHA, et un GGUF venant d'un autre dépôt n'est épinglé que par son SHA (révision `main` résolue à la volée).

**Approach:** Épingler chaque candidat dans un TOML : révision HF, SHA de chaque fichier HF, GGUF avec sa révision, son SHA et sa source. Étendre le schéma `ConfigModele` sans rupture. Ajouter `slmsp fetch modeles --candidats` (ordre D4), qui obtient les fichiers (ici : tous `deja-present`, sans requête) puis exécute les contrôles de `fetch/verifications.py` et les inscrit dans le run `runs/fetch/<run_id>/controles.jsonl`.

## Boundaries & Constraints

**Always:**
- Ordre D4 : `granite-4.0-1b`, `ministral-3-3b`, `smollm3-3b`, `qwen-4b`, `ministral-3-8b`. Le 8B est en GGUF seul (`fichiers = []`).
- Les SHA viennent des fichiers préchargés et sont recoupés avec HF. Un fichier présent dont le SHA est connu en config ne déclenche aucune requête. Un `X-Linked-Etag` différent du SHA de la config lève `ShaInvalide`.
- `llama-server` n'est lancé que par `slmsp.inference.serveur.ServeurLlama`, en variante `cpu` (pas de `gpu.lock`), sans `--mmproj`.
- Le template du tokenizer est exporté sous `models/<slug>/chat_template.jinja` sans jamais écraser un fichier différent. Écriture en `.part`, puis renommage.
- Un modèle écarté l'est avec son motif, dans `controles.jsonl` et sur stderr. La commande sort alors en code 1, et le run reste `complet`.
- Tests sans réseau ni binaire : fixtures `config.json`, GGUF synthétique, serveur injecté.

**Never:**
- Retélécharger un modèle, supprimer ou réécrire un fichier sous `models/`, pousser ou publier.
- Réécrire automatiquement un TOML versionné depuis un run : la vérification signale, la story inscrit.
- Modifier `harness/`, `mistral/` ou `judge/` (stories 4.3 et 5.5 en parallèle).
- Ajouter le paquet `gguf` ou `transformers` aux dépendances : la lecture des métadonnées GGUF est faite à la main.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Dense | `layer_types` tous `*attention*` (racine ou `text_config`), ou absent | contrôle `dense` = `ok` | — |
| Hybride | une couche `mamba` | `dense` = `echec`, motif nommant les couches, modèle écarté | code 1 |
| FP8 | `quantization_config` présent, ou `dtype`/`torch_dtype` contenant `float8` | `fp8` = `echec` | code 1 |
| Vision | `vision_config` présent | `ok` si `exclure_vision`, sinon `echec` | code 1 |
| Template identique | SHA(template HF) = SHA(`tokenizer.chat_template` du GGUF) | `ok`, aucun export | — |
| Template différent | SHA différents | export du template HF ; `ok` si `chat_template_force`, sinon `echec` (« inscrire chat_template_force = true ») | code 1 |
| Export en conflit | `chat_template.jinja` déjà présent avec un autre contenu | `echec`, fichier intact | code 1 |
| Sans poids HF | `fichiers = []` (8B) ou modèle d'embedding | `dense`, `fp8`, `vision`, `chat_template` = `sans-objet` | — |
| Serveur | `ServeurLlama` démarre, `/health` = 200 | `serveur` = `ok` ; `/props` relevé (modalités) | `ErreurInference` → `echec`, fin du journal dans le motif |
| `--sans-serveur` | option | `serveur` = `sans-objet` | — |
| Arguments | `--candidats` et des slugs, ou aucun des deux | erreur d'usage, aucun run | code 2 |

</intent-contract>

## Code Map

- `src/slmsp/core/schemas/config_modele.py` -- `FichierGguf` (l. 20) et `ConfigModele` (l. 28). Ajouts compatibles : `gguf.revision: RevisionHf | None`, `gguf.source: Literal["officielle","communautaire","conversion"] | None`, `gguf.tag_conversion: str | None` (requis si et seulement si `source = "conversion"`), `sha256_fichiers: dict[str, Sha256]` (clés incluses dans `fichiers`). Hors zone : consigné.
- `src/slmsp/fetch/modeles.py` -- `_gguf` (l. 47) : utiliser `gguf.revision` s'il est donné, sinon le comportement actuel. `_fichier_hf` (l. 80) : SHA lu dans `sha256_fichiers`, sans HEAD si la destination existe ; conflit avec l'etag → `ShaInvalide`. Hors zone (2.1 fusionnée, aucune story parallèle) : consigné.
- `src/slmsp/fetch/verifications.py` (nouveau) -- `CANDIDATS` (ordre D4), `Controle(modele, controle, statut, detail, valeurs)`, `lire_metadonnees_gguf(chemin, cles)` (en-tête GGUF v2/v3, types 0 à 12, tableaux sautés), `template_hf(dossier_hf)` (`chat_template.jinja`, sinon `tokenizer_config.json["chat_template"]`, str ou liste `name=default`), `verifier_config_hf`, `verifier_chat_template`, `verifier_serveur(slug, config, fabrique=ServeurLlama)`, `verifier_modele(...) -> list[Controle]`.
- `src/slmsp/cli/fetch.py` -- `_modeles` (l. 190) : `slugs` en `nargs="*"`, plus `--candidats` et `--sans-serveur`. Après `modeles.executer`, contrôles des modèles de génération, écrits dans `controles.jsonl`. Résumé imprimé, code 1 s'il y a des écartés. `_executer` (l. 88) reçoit le code du pilote.
- `src/slmsp/inference/serveur.py` -- lecture seule : `ServeurLlama(config, "cpu", slug=...)`, gestionnaire de contexte, `port`, `journal`. Lit `models/<slug>/chat_template.jinja` si `chat_template_force`.
- `src/slmsp/net` -- `client_local(port)` pour `/props`.
- `tests/fetch/conftest.py` -- fixtures `banc`, `cli`, `outils` (`lire_run`) ; les étendre pour lire `controles.jsonl`.
- `<dépôt principal>/models/` -- fichiers préchargés, conformes à HF (voir Design Notes).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/schemas/config_modele.py` -- ajouter les champs et les validateurs ci-dessus -- AC1 et reports de la 2.1.
- `src/slmsp/fetch/modeles.py` -- révision du GGUF et SHA des fichiers HF venant de la config, sans requête si le fichier est présent -- reprise hors ligne, reports de la 2.1.
- `src/slmsp/fetch/verifications.py` -- contrôles et lecteur GGUF -- AC3 à AC7.
- `src/slmsp/cli/fetch.py` -- `--candidats`, `--sans-serveur`, `controles.jsonl`, code de sortie -- AC2 et AC7.
- `config/modeles/{granite-4.0-1b,ministral-3-3b,smollm3-3b,qwen-4b,ministral-3-8b}.toml` -- valeurs des Design Notes, et `chat_template_force` fixé d'après le run réel -- AC1, AC4, AC5, AC6.
- `tests/fetch/fixtures/{config-dense,config-hybride,config-fp8,config-vision}.json` -- `config.json` réduits (Granite dense et hybride, FP8, Ministral avec vision).
- `tests/fetch/test_verifications.py` -- matrice I/O ; lecteur GGUF sur un fichier synthétique (chaînes, tableaux de chaînes, scalaires) ; chargement et ordre des cinq TOML ; CLI `--candidats` de bout en bout (serveur factice, `CANDIDATS` réduit, serveur injecté).
- `tests/fetch/test_modeles.py` -- `gguf.revision` sans résolution de `main`, `sha256_fichiers` pour un fichier non LFS, fichier présent sans requête, conflit etag/config.
- Exécution réelle (arrière-plan) -- `slmsp fetch modeles --candidats --racine <dépôt principal>` avec `SLMSP_MODELS_DIR`, `SLMSP_VENDOR_DIR` et `SLMSP_ENV_FILE` du dépôt principal ; consigner le run.

**Acceptance Criteria:**
- Given chaque TOML candidat, when on le charge, then il porte une `revision` de 40 hex, un SHA pour chaque fichier HF, `gguf.revision`, `gguf.sha256`, `gguf.source`, et les paramètres AD-6 (`contexte`, `cache_kv`, `reasoning`, `chat_template_kwargs`, `protocole_outils`).
- Given les fichiers déjà présents, when on lance `fetch modeles --candidats`, then tous les fichiers sont `deja-present` dans l'ordre D4, sans aucune requête réseau, et le 8B n'a qu'une ligne GGUF.
- Given le run réel, when il est clos, then `controles.jsonl` contient pour chacun des 5 modèles les contrôles `dense`, `fp8`, `vision`, `chat_template` et `serveur` avec leur statut, et tout modèle écarté y figure avec son motif.
- Given Ministral 3 3B, when il est contrôlé, then `exclure_vision = true`, le serveur démarre sans projecteur et `/props` est relevé.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 45 findings — high 0, medium 4, low 38, false 3, maybe-false 0
- findings:
  - `[medium]` `[patch]` (blind) Le contrôle `serveur` relève le SHA du template servi (`/props`) sans le comparer : un fichier forcé ignoré passerait `ok`. — `verifier_serveur` reçoit les SHA HF et GGUF, inscrit `sha256_template_attendu` et `template_servi_conforme`, et passe en `echec` si le template forcé est ignoré (servi = GGUF ≠ HF). Une autre différence reste `ok` avec la mention « transformé » : llama-server b11429 réécrit les templates Mistral, forcés ou non (8B : GGUF 749c93…, servi 4ce79e…).
  - `[low]` `[reject]` (blind) `n_ctx` et `build_info` de `/props` sont relevés sans être comparés. — `ServeurLlama` passe `-c` depuis la config ; un écart est improbable et le corriger ajoute une branche. Les valeurs restent dans `controles.jsonl` (8192 et b11429 relevés).
  - `[low]` `[patch]` (blind) `dense` : le test de sous-chaîne accepte `linear_attention`. — Remplacé par la liste fermée `COUCHES_DENSES` ; test ajouté.
  - `[low]` `[reject]` (blind) `dense` : hybride déclaré sans `layer_types` (Jamba, Nemotron-H) et MoE non contrôlés. — Les candidats sont figés (Granite porte `layer_types`) ; D7 ne demande pas le MoE ; le correctif ajoute des branches spéculatives.
  - `[low]` `[reject]` (blind) Le 8B n'a de contrôle réel que `serveur`. — GGUF seul par D4 (pas de tokenizer HF), GGUF officiel Mistral. Le SHA du template GGUF est désormais relevé et comparé au template servi.
  - `[low]` `[patch]` (blind) `exporter_template` : `os.rename` remplace sous POSIX, et une `OSError` fait tomber le run en laissant un `.part`. — Commentaire corrigé (comportement propre à Windows, D2) ; `OSError` → `conflit`, et le `.part` créé par l'appel est supprimé ; tests ajoutés.
  - `[low]` `[reject]` (blind) Le lecteur GGUF ne borne pas les nombres d'éléments des tableaux. — Les GGUF sont vérifiés par SHA avant la lecture ; un fichier hostile est improbable ; le correctif est une garde de plus.
  - `[low]` `[reject]` (blind) `fetch modeles <slug>` lance maintenant les contrôles (serveur, export) par défaut. — Comportement voulu par la spec (Code Map) et documenté ; `--sans-serveur` existe ; les modèles d'embedding (seul usage antérieur) ne sont pas touchés.
  - `[low]` `[reject]` (blind) Les contrôles continuent après un premier échec. — Choix délibéré : tous les motifs sont consignés ; coût CPU marginal.
  - `[low]` `[reject]` (blind) Un téléchargement en échec empêche tous les contrôles. — Le run se termine alors en `partiel-erreur`, comme en 2.1 ; une relance reprend les fichiers.
  - `[low]` `[reject]` (blind) Le verdict d'écartement n'est pas dans `run.json` ni dans `etat.jsonl`. — `controles.jsonl` du run le porte (CA7) ; le dupliquer ajoute une surface.
  - `[low]` `[reject]` (blind) `fp8` ignore `compression_config` et les dtypes des en-têtes safetensors ; libellé trop étroit. — Les candidats sont vérifiés (bf16, sans quantification) ; le correctif est spéculatif.
  - `[low]` `[reject]` (blind) `vision` ignore `audio_config` et les autres marqueurs. — Les candidats n'en ont pas ; `/props` confirme audio = vision = video = false.
  - `[low]` `[reject]` (blind) Les tailles ne sont que des commentaires dans les TOML. — Le SHA-256 suffit à l'intégrité ; ajouter un champ au schéma est une surface de plus.
  - `[low]` `[patch]` (blind) Tests manquants. — Ajoutés : `linear_attention`, `text_config` mamba, erreur d'export et cible répertoire, template forcé ignoré ou transformé. Les autres cas cités relèvent de constats rejetés.
  - `[medium]` `[patch]` (verification-gap) `_lire_props` et la fabrique par défaut ne sont exercés par aucun test. — Test de `_lire_props` contre un `http.server` local ; test de cohérence `ServeurLlama.chat_template`/`.gguf` avec les chemins de `verifier_modele` (sans démarrage).
  - `[low]` `[reject]` (verification-gap) Chemin GGUF : nom de base dans fetch, chemin complet dans `ServeurLlama`. — Antérieur à la story ; aucun des cinq TOML n'a de sous-dossier.
  - `[low]` `[patch]` (verification-gap) Exceptions d'`exporter_template` non rattrapées. — Même correctif que la ligne export ci-dessus.
  - `[low]` `[patch]` (edge) `os.rename` remplace sous POSIX. — Même correctif (commentaire, D2).
  - `[low]` `[patch]` (edge) Une `OSError` en écriture ou au renommage fait tomber le run et laisse un `.part`. — Même correctif.
  - `[low]` `[patch]` (edge) Une cible `chat_template.jinja` qui est un répertoire lève `IsADirectoryError`. — Même correctif : `conflit` ; test ajouté.
  - `[low]` `[reject]` (edge) Un `tokenizer_config.json` qui n'est pas un objet lève `AttributeError`. — Fichiers épinglés par SHA ; cas improbable ; garde supplémentaire.
  - `[low]` `[reject]` (edge) `OverflowError` sur un nombre d'éléments corrompu. — Même motif que le lecteur GGUF non borné.
  - `[low]` `[patch]` (edge) `dense` s'arrête au premier `layer_types` (racine) et ignore `text_config`. — Les non-conformes sont collectés sur la racine et `text_config` ; test ajouté.
  - `[low]` `[patch]` (edge) `linear_attention` accepté par sous-chaîne. — Même correctif (`COUCHES_DENSES`).
  - `[low]` `[reject]` (edge) Un `layer_types` qui n'est pas une liste fait planter le contrôle. — Improbable sur des configs épinglées ; garde supplémentaire.
  - `[low]` `[reject]` (edge) Un hybride déclaré par d'autres clés passe `ok`. — Même motif que la ligne blind correspondante.
  - `[low]` `[reject]` (edge) Un `layer_types` vide donne `ok`. — Improbable ; garde supplémentaire.
  - `[low]` `[reject]` (edge) Un `modalities` de `/props` qui n'est pas un objet lève une erreur. — llama-server b11429 rend un objet (relevé réel) ; garde supplémentaire.
  - `[low]` `[reject]` (edge) `journal` vaut `None` quand le démarrage échoue. — Le message d'`ErreurInference` porte déjà le chemin et la fin du journal, et il est recopié dans `detail`.
  - `[false]` `[reject]` (edge) `dossier_modeles` passé à `verifier_modele` différent du global. — La CLI passe `dossier_modeles()` : les deux valeurs sont identiques dans tout chemin réel.
  - `[low]` `[reject]` (edge) GGUF dans un sous-dossier : téléchargé sous un chemin, cherché sous un autre par le serveur. — Antérieur ; aucun TOML concerné.
  - `[low]` `[reject]` (edge) `fetch modeles <slug>` non candidat : lance le serveur et peut sortir en 1. — Même motif que la ligne blind correspondante.
  - `[low]` `[reject]` (edge) `source = "conversion"` sans fichier présent : HEAD vers un dépôt peut-être inexistant. — Aucune config de conversion ; une erreur de téléchargement claire suffit.
  - `[low]` `[reject]` (edge) dtype seulement sous `text_config` : détail affichant `None`. — Cosmétique ; les candidats ont un dtype racine.
  - `[low]` `[patch]` (edge) Commentaire faux sur `os.rename`. — Corrigé (Windows, D2).
  - `[low]` `[patch]` (intent) Pas de test `reseau` des candidats, alors que la stratégie de test en prévoit. — `test_candidat_reel_conforme` (HEAD seulement, 5 modèles) : 5 passés avec `-m reseau`.
  - `[medium]` `[patch]` (intent) Le template imposé (AD-13) est relevé mais pas vérifié. — Même correctif que la première ligne.
  - `[low]` `[reject]` (intent) La conversion de repli de CA4 n'existe que dans le schéma. — Les GGUF officiels Q4_K_M existent (D-nuit-A1-11) : CA4 ne la demande qu'« à défaut ».
  - `[low]` `[reject]` (intent) Démarrage en CPU seulement, sans CUDA. — Choix de la spec (pas de `gpu.lock` pendant que d'autres stories tournent) ; le support par llama.cpp (D7) est prouvé ; l'évaluation CUDA relève de la 8.3.
  - `[low]` `[reject]` (intent) « Le journal » de CA7 est ambigu. — `controles.jsonl` du run et le journal de nuit (via le compte rendu) portent les motifs ; aucun modèle écarté.
  - `[false]` `[reject]` (intent) Poids BF16 sous `hf/` et non `hf-bf16/`. — CA2 autorise `{hf|hf-bf16}`.
  - `[low]` `[reject]` (intent) Fichiers hors zone (`config_modele.py`, `modeles.py`, tests). — Consignés comme décision : les reports de la 2.1 vivent là, et aucune story parallèle ne les touche.
  - `[medium]` `[defer]` (intent) Le `run.json` d'un run lancé depuis un worktree avec `--racine` sur le dépôt principal inscrit le commit du dépôt principal, pas celui du code exécuté. — Comportement de `core.artefacts`, antérieur (déjà vrai pour les runs de la 2.1) ; noté dans `deferred`.
  - `[false]` `[reject]` (intent) Rien n'est commité et `## Auto Run Result` est absent. — Instantané pris pendant la revue ; la finalisation commite et écrit la section.

## Design Notes

**Valeurs des TOML** (révisions de `models/PRECHARGEMENT.md`) :

| slug | depot_hf | GGUF (source) | particularités |
|---|---|---|---|
| granite-4.0-1b | `ibm-granite/granite-4.0-1b` | `ibm-granite/granite-4.0-1b-GGUF` (officielle) | 9 fichiers HF |
| ministral-3-3b | `mistralai/Ministral-3-3B-Instruct-2512-BF16` | `mistralai/…-GGUF` (officielle) | `exclure_vision = true`, 13 fichiers HF |
| smollm3-3b | `HuggingFaceTB/SmolLM3-3B` | `ggml-org/SmolLM3-3B-GGUF` (officielle ggml-org) | `chat_template_kwargs = { enable_thinking = false }` |
| qwen-4b | `Qwen/Qwen3-4B-Instruct-2507` | `unsloth/…-GGUF` (communautaire) | template dans `tokenizer_config.json` |
| ministral-3-8b | `mistralai/Ministral-3-8B-Instruct-2512-GGUF` | même dépôt (officielle) | `fichiers = []`, `exclure_vision = true` |

Taille et SHA-256 de chacun des 46 fichiers préchargés (calculés le 2026-10-12, recoupés avec l'API paths-info de HF aux révisions épinglées : sha256 LFS et oid git conformes) : `C:\Users\UTILIS~1\AppData\Local\Temp\claude\C--Users-Utilisateur-Documents-GitHub-service-public-slm-fine-tuning\2b525399-9658-4abc-ae6d-dabcdbffc874\scratchpad\sha_modeles.json` (clé `<slug>/<hf|gguf>/<fichier>` → `[taille, sha256]`). `fichiers` = tous les fichiers de `hf/` de cette liste.

Valeurs communes : `contexte = 8192`, `cache_kv = "f16"`, `reasoning = "off"`, `protocole_outils = "natif"` (provisoire, fixé par la story 8.2).

**Lecteur GGUF** : en-tête `GGUF` (petit-boutiste), `version` u32, `n_tenseurs` u64, `n_kv` u64, puis des paires (clé : u64 + octets, type u32, valeur). Les chaînes sont précédées de leur longueur u64. Un tableau est codé (type u32, n u64, éléments). Lecture bufferisée, arrêt dès que les clés demandées sont lues.

## Verification

**Commands:**
- `uv run pytest tests/fetch` -- expected : tout passe.
- `uv run pytest` puis `uv run ruff check` et `uv run ruff format --check` -- expected : vert, ou seuls des échecs préexistants hors zone.
- `uv run --extra fetch slmsp fetch modeles --candidats --racine <dépôt principal>` (arrière-plan) -- expected : 46 fichiers `deja-present`, 0 octet, puis 5 × 5 contrôles dans `controles.jsonl`.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** Les cinq Modèles de base candidats (D4) sont épinglés dans `config/modeles/<slug>.toml` : révision HF, SHA-256 de chaque fichier HF, GGUF avec révision, SHA et source, paramètres AD-6. `slmsp fetch modeles --candidats` (ordre D4) vérifie les fichiers préchargés sur place, sans retéléchargement. Il exécute ensuite les contrôles D7 de `fetch/verifications.py` (dense, fp8, vision, chat template, démarrage de `llama-server`) et les inscrit dans `runs/fetch/<run_id>/controles.jsonl`. Les deux reports de la 2.1 sont levés : `gguf.revision` épingle un GGUF tiers, et `sha256_fichiers` porte le SHA des fichiers non LFS.

**Résultat des contrôles** (run réel `20261012-132028-modeles-dd0b`, sous `<dépôt principal>/runs/fetch/`, statut `complet`, code 0 ; 46 fichiers `deja-present`, 0 octet transféré) :

| Modèle | dense | fp8 | vision | chat_template | serveur (cpu) |
|---|---|---|---|---|---|
| granite-4.0-1b | ok (40/40 attention) | ok (bf16) | ok (aucune) | ok (HF = GGUF) | ok |
| ministral-3-3b | ok (pas de `layer_types`) | ok (bf16) | ok (Pixtral présent, exclu) | ok (différent → forcé, exporté) | ok, sans projecteur ; template transformé par llama-server |
| smollm3-3b | ok (36/36 full_attention) | ok (bf16) | ok | ok (différent → forcé, exporté) | ok, template servi = HF |
| qwen-4b | ok (pas de `layer_types`) | ok (bf16) | ok | ok (différent → forcé, exporté) | ok, template servi = HF |
| ministral-3-8b | sans objet (GGUF seul) | sans objet | sans objet | sans objet | ok, sans projecteur ; template transformé par llama-server |

Aucun modèle écarté. `/props` donne `n_ctx` 8192, build `b11429-d81235049`, modalités vision, audio et vidéo à false pour les cinq. Les 46 fichiers ont été recoupés avec l'API paths-info de HF aux révisions épinglées (sha256 LFS et oid git conformes). Le test `reseau` (HEAD) passe pour les 5 modèles.

**Fichiers.**
- `config/modeles/{granite-4.0-1b,ministral-3-3b,smollm3-3b,qwen-4b,ministral-3-8b}.toml` : épinglage et paramètres.
- `src/slmsp/fetch/verifications.py` (nouveau) : contrôles D7, lecteur d'en-tête GGUF, export du template.
- `src/slmsp/cli/fetch.py` : `--candidats`, `--sans-serveur`, `controles.jsonl`, code 1 si un modèle est écarté.
- `src/slmsp/core/schemas/config_modele.py` (hors zone) : `gguf.revision`, `gguf.source`, `gguf.tag_conversion`, `sha256_fichiers`, avec validateurs.
- `src/slmsp/fetch/modeles.py` (hors zone) : révision GGUF et SHA des fichiers HF lus en config, aucune requête si le fichier est présent.
- `tests/fetch/test_verifications.py` (nouveau), `tests/fetch/fixtures/config-{dense,hybride,fp8,vision}.json`, `tests/fetch/test_modeles.py`, `tests/fetch/conftest.py`.
- Hors git, dans le dépôt principal : `models/{ministral-3-3b,smollm3-3b,qwen-4b}/chat_template.jinja` (templates HF exportés, nouveaux fichiers).

**Revue** (1 passe, 4 couches, 45 constats) :
- 13 lignes corrigées, dont 3 médium (template forcé non vérifié, relevé deux fois ; chemin réel de `/props` non testé) ;
- 1 différée : provenance de `run.json` lancé depuis un worktree, antérieure à la story ;
- 31 rejetées avec motif (voir le Review Triage Log) : 28 low improbables ou spéculatives, 3 false.

**Relecture complémentaire recommandée** (`true` : 3 médium corrigés). Risque précis : llama-server b11429 réécrit les templates Mistral, forcés ou non. Le template servi diffère du HF (3B) comme du GGUF (8B). Le rendu effectif des appels d'outils de Ministral est donc à confirmer par la sonde H-TOOLS (story 8.2).

**Vérification.**
- `uv run pytest` : 2374 passés, 165 sautés.
- `tests/fetch/test_verifications.py -m reseau` : 5 passés.
- `ruff check` et `ruff format --check` : propres.

**Décisions prises seul** (à reporter au journal) :
1. Schéma `ConfigModele` étendu, sans rupture, hors zone, pour lever les reports de la 2.1.
2. `fetch/modeles.py` modifié (hors zone, sans story parallèle) : un fichier présent dont le SHA est en config ne déclenche aucune requête.
3. La vérification signale et la story inscrit : aucun TOML versionné n'est réécrit par un run.
4. `chat_template_force = true` pour ministral-3-3b, smollm3-3b et qwen-4b (SHA HF ≠ GGUF) ; `false` pour Granite (identiques) et pour le 8B (pas de tokenizer HF).
5. Un modèle écarté donne un run `complet`, avec code de sortie 1.
6. `contexte = 8192`, `cache_kv = f16`, `reasoning = off` pour les cinq ; SmolLM3 : `enable_thinking = false`. `protocole_outils = "natif"` reste provisoire (story 8.2).
7. `llama-server` est démarré en variante cpu, pour ne pas prendre `gpu.lock`.
8. Le contrôle `serveur` n'échoue que si le template forcé est ignoré (template servi = GGUF ≠ HF). Une transformation par llama-server est seulement notée.
9. Ministral 3 3B : dépôts officiels BF16 et GGUF (D-nuit-A1-11, A1-24), aucune conversion. Qwen : `Qwen/Qwen3-4B-Instruct-2507` @ `cdbee75f…`, GGUF communautaire unsloth @ `a06e946b…` (D-nuit-A2-15).

**Risques résiduels.**
- Réécriture des templates Mistral par llama-server (voir plus haut).
- Démarrage CUDA non éprouvé ici (8.3).
- Provenance des runs lancés depuis un worktree (différé).
- `runs/fetch/` et les templates exportés du dépôt principal ne sont pas versionnés.
