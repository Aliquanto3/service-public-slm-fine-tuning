---
title: 'Story 10.1 — Environnement d''entraînement Windows et mesure H-WIN-TRAIN'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '9959f6f69c1b4f0d79ccd0b353e2fd2e868935d4'
review_loop_iteration: 1
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-10-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** avant le premier Run, on ignore si torch CUDA, bitsandbytes (QLoRA nf4) et Unsloth fonctionnent sous Windows natif sur la RTX 3050 8 Go (pilote 610), et quelle longueur de séquence tient en VRAM (H-WIN-TRAIN).

**Approach:** un module `slmsp.train.environnement` qui contrôle le matériel et exécute quelques pas QLoRA (ou LoRA bf16 en repli) sur des tokens aléatoires via TRL + PEFT, exposé par `slmsp train sonde-env`, sous `gpu.lock`, dans un run `runs/train-sonde/<run_id>/` ; `--unsloth` tente le pas équivalent dans l'environnement uv isolé `envs/unsloth/`, en sous-processus.

## Boundaries & Constraints

**Always:**
- torch, transformers, trl, peft, bitsandbytes et datasets sont importés **dans les fonctions** de `train/environnement.py` (jamais au niveau module), pour que les tests unitaires tournent sans l'extra `train`, avec un torch simulé injecté.
- Toute exécution qui touche CUDA prend `slmsp.core.var.verrou_gpu(commande=...)` ; `RessourceOccupee` sort en code 5.
- Arguments d'entraînement : `report_to="none"`, `push_to_hub=False`, `save_strategy="no"`, jamais `save_total_limit` ; `appliquer_environnement_impose()` avant tout import lourd ; le sous-processus Unsloth reçoit `env_sous_processus()`.
- Le dossier des poids est validé par `core.artefacts.chemin_autorise(dossier, "train")` (`<SLMSP_MODELS_DIR>/<slug>/hf/`).
- Refus clairs (`ConfigurationInvalide`) : poids FP8 (`quantization_config` FP8), couche Mamba (`layer_types` contenant `mamba`), `vision_config` présent (le modèle multimodal n'est pas chargé par la sonde).
- Repli du spine, consigné dans `methodes.json` du run : sans bitsandbytes → LoRA bf16 sur `granite-4.0-1b` seulement, `qlora` et `dora` listées indisponibles ; sans Unsloth → `qlora-unsloth` indisponible, TRL + PEFT seuls.
- Mesures par longueur : perte, finitude, `max_memory_allocated`/`max_memory_reserved`, tokens/s hors padding après 1 pas de chauffe (batch 1, aucune troncature ni padding), statut `ok` / `oom` / `debordement` (VRAM réservée > 90 % de la mémoire totale, `FRACTION_DEBORDEMENT` : débordement probable en mémoire partagée WDDM).

**Never:**
- Aucune donnée d'entraînement réelle ni rédigée : uniquement des tokens aléatoires (graine fixe).
- Ne pas importer `unsloth` dans `slmsp` ; ne pas toucher au conflit `fetch`/`train` de `pyproject.toml` ; pas de `slmsp train run` réel (déclaré « non implémenté » jusqu'à 10.4) ; pas de Ministral 3 (vision) dans la sonde.
- Ne rien écrire hors de `train/environnement.py`, `cli/train.py`, `envs/unsloth/`, `tests/train/`, `runs/train-sonde/` et la spec.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Sonde nominale | `slmsp train sonde-env` (Granite 1B, qlora) | run `train-sonde` `complet`, `sonde.json` (contrôles + mesures), `methodes.json`, code 0 | — |
| Pas de CUDA | `torch.cuda.is_available()` faux | run `partiel-erreur`, motif « CUDA indisponible », code 1 | message sur stderr |
| bitsandbytes en échec | chargement 4 bits lève | repli LoRA bf16 si slug = 1B, run `degrade`, `qlora`/`dora` indisponibles | autre slug : `partiel-erreur` |
| OOM à une longueur | `OutOfMemoryError` | statut `oom` pour cette longueur, longueurs suivantes non tentées | cache CUDA vidé |
| Unsloth | `--unsloth` | `uv run --project envs/unsloth python envs/unsloth/sonde.py` via `inference.processus.executer`, résultat JSON dans `unsloth.json` | échec → `qlora-unsloth` indisponible, run `degrade` |
| GPU occupé | `gpu.lock` pris | code 5, message avec le détenteur | — |
| `train run` | toute invocation | « non implémentée (story 10.4) », code 2 | — |

</intent-contract>

## Code Map

- `src/slmsp/core/var.py:156` -- `verrou_gpu(attendre, delai, commande)` : verrou exclusif.
- `src/slmsp/core/config.py:109-136` -- `appliquer_environnement_impose()`, `env_sous_processus()`, `dossier_modeles()`, `racine_projet()`.
- `src/slmsp/core/artefacts.py:332` -- `nouveau_run(type, slug, config, racine=...)` ; `Run.ecrire`, `Run.ajouter_jsonl`, `Run.terminer(statut, motif)` ; `chemin_autorise` l.473 (lecteur `train` : `data/train`, `dossier_modeles()`).
- `src/slmsp/inference/processus.py:512` -- `executer(arguments, delai, role, journal, env)` : Job Object, `pids/`, env filtré par défaut (couche 2, importable par `train`, couche 4).
- `src/slmsp/inference/serveur.py:85` -- `charger_config_modele(slug)` (`exclure_vision`, etc.).
- `src/slmsp/cli/__init__.py` -- registre : `cli/train.py` expose `enregistrer(sous_parseurs)` ; `RessourceOccupee`/`SlmspError` traduits en code par `main`.
- `src/slmsp/cli/fetch.py` -- modèle de sous-commandes avec `--racine`.
- `tests/test_architecture.py` -- `train` : pas d'`open()`, `.read_text()`, `json.load` ; `push_to_hub` seulement `False` ; pas d'import de `fetch`/`measure`/`judge`.
- `tests/test_cli.py:83` -- le test « non implémentée » se saute dès que `cli/train.py` existe.
- `C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\models\{granite-4.0-1b,smollm3-3b}\hf\` -- poids bf16 réels (Granite : `granitemoehybrid`, tout attention).
- `.venv` du worktree -- torch 2.14.1+cu130 (CUDA OK, capacité 8.6, bf16), bitsandbytes 0.50.2, trl 1.13.0, peft 0.21.2, datasets 5.1.0 ; SFTTrainer accepte un jeu pré-tokenisé (`input_ids`).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/train/environnement.py` -- contrôles matériels (`controler_materiel(torch)`), contrôles de config du modèle, `arguments_entrainement(...)` (dict SFTConfig sûr), `sonder(...)` (chargement 4 bits nf4 ou bf16, LoRA PEFT, SFTTrainer sur tokens aléatoires, mesures par longueur), `sonder_unsloth(...)`, calcul des méthodes disponibles -- cœur de H-WIN-TRAIN.
- `src/slmsp/cli/train.py` -- `sonde-env [--modele] [--methode qlora|lora] [--longueurs] [--pas] [--unsloth] [--racine]` sous verrou GPU et run `train-sonde` ; `run` → non implémentée -- surface de la story.
- `envs/unsloth/pyproject.toml`, `envs/unsloth/sonde.py` -- projet uv isolé (unsloth 2026.10.3, transformers 5.17.0, trl 1.13.0, torch cu130) et script JSON entrée/sortie -- variante isolée.
- `tests/train/test_environnement.py` -- torch simulé (absence de CUDA, capacité < 8, bf16, FP8 refusé, Mamba refusé, vision refusée), arguments d'entraînement, CLI (run créé, verrou pris, `train run` code 2, repli bnb, sous-processus Unsloth avec env filtré), plus tests réels `gpu`+`lent`.
- Exécution réelle (arrière-plan, `gpu.lock`) : Granite 1B qlora et SmolLM3 3B qlora sur longueurs 512→4096, puis `--unsloth` ; runs versionnés sous `runs/train-sonde/`.

**Acceptance Criteria:**
- Given `uv sync --extra train`, when `pytest -m gpu tests/train` tourne, then torch vient de l'index cu130 et `torch.cuda.is_available()` est vrai.
- Given Granite 4.0 1B, when `slmsp train sonde-env` tourne, then un pas QLoRA nf4 s'exécute sous `gpu.lock`, perte finie, VRAM max relevée dans `runs/train-sonde/<run_id>/sonde.json`.
- Given `--unsloth`, when la sonde tourne, then un pas est tenté dans `envs/unsloth` en sous-processus avec `env_sous_processus()`, et un échec est consigné comme repli.
- Given une exécution d'entraînement, when elle démarre, then `report_to="none"`, `push_to_hub=False` et `ENV_IMPOSE` sont appliqués.

## Spec Change Log

- 2026-10-13 (revue) : seuil de `debordement` abaissé de 100 % à 90 % de la mémoire totale (`FRACTION_DEBORDEMENT`) ; `loss_type` et `router_aux_loss_coef` ne sont plus posés que si la configuration du modèle les exige (`arguments_specifiques`) ; `uv run --frozen` pour la sonde Unsloth ; artefacts du run sans chemin absolu ; provenance du code dans `run.json`.

## Review Triage Log

Revue Blind Hunter du 2026-10-12, interrompue par la limite de dépense (D-nuit-3). Les constats retenus sont ceux du journal (`journal-decisions-nuit.md`, D-nuit-3), traités le 2026-10-13 sans relancer de revue (mode économe) :

| # | Constat | Décision | Correctif | Test |
|---|---|---|---|---|
| 1 | Provenance des runs : `run.json` donne `git_commit` 9959f6f et `git_modifie: false`, alors que le code de la sonde n'était pas encore commité (`git_modifie` ignore les fichiers non suivis) | retenu | `cli/train.py` : `provenance_code()` (SHA-256 de `FICHIERS_CODE`, fichiers non commités y compris non suivis, `code_commite`) dans la config du run. `core/artefacts.py`, hors zone, n'est pas modifié | `test_cli_provenance_du_code`, `test_provenance_signale_le_code_non_suivi` |
| 2 | `uv run` sans `--frozen` sous `gpu.lock` : uv peut résoudre de nouveau et réécrire `envs/unsloth/uv.lock` pendant la mesure | retenu | `commande_unsloth` : `uv run --frozen --project envs/unsloth …` | `test_commande_unsloth`, `test_cli_unsloth_sous_processus` |
| 3 | Seuil de débordement trop permissif (VRAM réservée > 100 % de `total_memory`) : sous WDDM, le bureau et le pilote tiennent une part de la carte | retenu | `FRACTION_DEBORDEMENT = 0.90`, `seuil_debordement` consigné par mesure, indicateur `debordement` dans `unsloth.json` | `test_sonde_debordement_avant_la_memoire_totale`, `test_deborde` |
| 4 | `loss_type="nll"` et `router_aux_loss_coef=0.0`, propres à Granite, appliqués à tous les modèles | retenu | `arguments_specifiques(config)` : `nll` si `logits_scaling` ≠ 1, `router_aux_loss_coef=0.0` si routeur déclaré sans expert ; transmis aussi à `envs/unsloth/sonde.py` ; un argument spécifique ne peut pas écraser un argument sûr | `test_arguments_specifiques_granite_seulement`, `test_arguments_specifiques_ajoutes_sans_ecraser`, `test_sonde_parametres_propres_au_modele`, `test_arguments_acceptes_par_sftconfig` (lent) |
| 5 | Chemins absolus dans les artefacts versionnés (`run.json`, `sonde.json`, `unsloth.json`, `unsloth-entree.json`) | retenu | `chemin_portable` / `commande_portable` : `$SLMSP_MODELS_DIR/…`, `$SLMSP_VAR_DIR/…`, chemins relatifs à la racine ; clé `racine` retirée de la config ; l'entrée réelle du sous-processus va sous `SLMSP_VAR_DIR/unsloth/`, le run garde une copie portable | `test_chemin_portable`, `test_cli_aucun_chemin_absolu_dans_le_run` |

Le rapport de nuit évoque « une dizaine de points » ; seuls ces cinq ont été consignés avant l'interruption. Les autres sont perdus et n'ont pas été reconstitués.

## Verification

**Commands:**
- `uv run pytest tests/train` -- expected: tests unitaires verts sans GPU.
- `uv run pytest -m "gpu and lent" tests/train` -- expected: sonde réelle verte (sous verrou).
- `uv run pytest` et `uv run ruff check` -- expected: verts, ou échecs préexistants hors zone listés.
- `uv run slmsp train sonde-env --modele granite-4.0-1b` -- expected: code 0, run `complet` ou `degrade` consigné.

## Auto Run Result

### Reprise de revue (2026-10-13, code seul, sans API)

**Statut : done.** Les cinq constats de revue sont corrigés et testés (voir Review Triage Log). Aucun entraînement, aucune mesure réelle ni aucun appel d'API : tests sur pile simulée et fixtures.

**Décisions prises seul :**
- `bmad-build-auto` n'est pas relancé : sur une spec `in-review`, il reprend à l'étape de revue (step-04), donc relancerait une revue, alors que le triage était vide et que le mode économe interdit une revue de plus. Correctifs appliqués directement, d'après la liste du journal.
- Seuil de débordement : 90 % de `total_memory`. C'est la règle la plus simple qui écarte le cas observé (95 %). Une mesure de la mémoire libre (`mem_get_info`) avant chargement reste possible en 10.4.
- Les runs du 2026-10-12 sont immuables et ne sont pas réécrits. **Lecture corrigée de leurs mesures** :
  - leur `git_commit` (9959f6f) désigne le parent : le code qui les a produits est celui du commit 793bd33 ;
  - leurs fichiers contiennent encore des chemins absolus ;
  - avec le nouveau seuil (7,73 Go réservés), SmolLM3 3B à 2048 (8,21 Go) passe en `debordement` : sa longueur maximale sans débordement est **1024**. Granite 1B reste à 2048 (6,51 Go).
- Commande à lancer plus tard (GPU libre, hors de ce run) pour confirmer SmolLM3 : `uv run slmsp train sonde-env --modele smollm3-3b --longueurs 1024,1536,2048`. Elle utilise TRL par défaut (`chunked_nll`), puisque SmolLM3 n'a pas de `logits_scaling`.

**Tests :**
- `pytest tests/train tests/test_architecture.py tests/test_cli.py` : 187 verts, 6 sautés.
- `test_arguments_acceptes_par_sftconfig` (lent, sans GPU) : vert, Granite compris.
- `ruff check` : vert.
- Suite complète : 3396 verts, 2 échecs hors zone.
  - `tests/budget/test_concurrence.py::test_critere_6_…` est intermittent (charge machine) : il passe seul.
  - `tests/eval_outils/test_jeu_v1.py::test_v1_1_export_des_changements` échoue parce que le jeu v1.1 n'est pas assemblé dans cette copie (`eval/jeu/v1.1/` n'est pas commité, il attend la relecture d'Anaël). `eval/` est hors périmètre.

### Run initial (2026-10-12)

**Statut : done.** H-WIN-TRAIN confirmée sous Windows natif (RTX 3050 8 Go, pilote 610.62, torch 2.14.1+cu130) : QLoRA nf4 (TRL + PEFT + bitsandbytes) et Unsloth fonctionnent, aucun repli nécessaire.

**Runs réels** (`runs/train-sonde/`, 3 pas mesurés après 1 pas de chauffe, batch 1, tokens aléatoires graine 1234) :

| Run | Longueur | Statut | VRAM réservée max | tokens/s |
|---|---|---|---|---|
| `20261012-134219-granite-4.0-1b-14bd` (qlora) | 512 / 1024 / 2048 / 4096 | ok / ok / ok / debordement | 3,03 / 4,26 / 6,51 / 10,33 Go | 606 / 650 / 633 / 524 |
| `20261012-134457-smollm3-3b-6168` (qlora) | 512 / 1024 / 2048 / 4096 | ok / ok / ok / debordement | 4,52 / 5,57 / 8,21 / 12,62 Go | 395 / 432 / 437 / 387 |
| Granite, `--unsloth` (même run 14bd) | 2048 | ok | 2,16 Go | 844 |

Pertes finies partout (~12-13 sur tokens aléatoires). Longueur maximale tenue sans débordement : 2048 pour les deux (SmolLM3 à 2048 est à 95 % de la mémoire de la carte). À 4096, le pilote WDDM déborde en mémoire partagée au lieu de lever un OOM.

**Décisions prises seul :**
- `loss_type="nll"` imposé : la perte par défaut de TRL 1.13 (`chunked_nll`) recalcule les logits sans `logits_scaling` de Granite (perte ~70-97 au lieu de ~13). **À reprendre en 10.4** : soit garder `nll` (plus de VRAM : logits complets en mémoire), soit poser `config.logit_scale = 1/logits_scaling` pour `chunked_nll`.
- `router_aux_loss_coef=0.0` : Granite 4.0 1B déclare `output_router_logits` sans experts ; TRL le prenait pour un MoE (`AttributeError: num_experts`).
- Après un `debordement` (comme après un `oom`), les longueurs suivantes ne sont pas tentées (statut `non-tentee`).
- `envs/unsloth/pyproject.toml` : `override-dependencies` réécrit le marqueur `triton ; 'linux' in sys_platform` d'unsloth (uv ne sait pas l'écarter pour win32) ; `triton-windows==3.8.0.post29` ajouté. Lock `envs/unsloth/uv.lock` versionné.
- Le sous-processus Unsloth tourne avec `cwd = SLMSP_VAR_DIR/unsloth` : Unsloth y écrit `unsloth_compiled_cache/` (sinon dans le dépôt).
- Résultat Unsloth rendu sur stdout (`SLMSP-RESULTAT <json>`) : `train` ne peut pas lire `runs/` par le lecteur contrôlé.
- `train run` répond « non implémentée (story 10.4) », code 2, quelles que soient les options (`_remplacement=True` sur son sous-parseur).
- Statuts de `methodes.json` : `verifiee`, `deduite`, `indisponible`, `non-sondee`.

**Tests :** `pytest tests/train` 39 verts sans GPU ; `pytest -m "gpu or lent" tests/train` 3 verts (sonde réelle sous le vrai `gpu.lock`) ; `ruff check` vert. Suite complète : 2641 verts, 1 échec intermittent hors zone (`tests/inference/test_serveur.py::test_demarrage_rate_sante`, délai de 2 s du serveur factice sur machine chargée ; vert au premier passage complet).
