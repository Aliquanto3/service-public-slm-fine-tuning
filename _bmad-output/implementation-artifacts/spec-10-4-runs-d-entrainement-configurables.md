---
title: 'Story 10.4 — Runs d''entraînement configurables (slmsp train run)'
type: 'feature'
created: '2026-10-16'
status: 'review'
baseline_revision: 'f1e1773'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-10-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/note-conception-10-6-export-gguf.md'
warnings: []
deferred:
  - 'Contrat provisoire du jeu (`MANIFEST.json` : `type_run`, `run_id`, `version`, `sha256_train` ; lignes `messages`, `tools`, `tache`, `meta.appel_ids`) à aligner sur `ManifesteJeuEntrainement` et `LigneEntrainement` de la story 9.6, puis remplacer `chargement._Manifeste` et `_Ligne` par ces schémas.'
  - 'ORPO : format des paires (`preferences.jsonl`, story 9.7) provisoire ; lecture de l''adaptateur SFT parent refusée par AD-24 tant que la liste du lecteur `train` n''inclut pas `runs/train/*/adaptateur/` (amendement à trancher, voir note 10.6).'
  - 'W4.2 (statut de la sonde 10.1 : longueur en erreur laissée `complet`, débordement à la première longueur), W4.5 (VRAM non représentative), W4.6 (robustesse de la sonde et d''`envs/unsloth/sonde.py`), W4.7 (tests de la sonde), W4.4 (`--longueurs` non trié, `arguments_entrainement` consigné pour la première longueur seulement) : zone 10.1 (`environnement.py`), non modifiée ici.'
  - 'Premier Run réel : vérifier que `include_num_input_tokens_seen="non_padding"` alimente le débit (report 10.3) et le choix `loss_type="nll"` pour Granite (report 10.1).'
  - 'Réserve de contrôle d''environ 40 conversations (note 10.6, point 3) : non implémentée, en attente de la décision d''Anaël.'
---

<intent-contract>

## Intent

**Problem:** `slmsp train run` est déclaré non implémenté. Il faut lancer un Run M1 à M4 depuis un seul TOML, dans des conditions comparables d'un Run à l'autre d'une campagne, avec reprise sur checkpoint et coûts mesurés.

**Approach:** `RunConfig` (pydantic) valide `config/runs/<nom>.toml` ; `methodes` traduit la méthode en quantification, `LoraConfig` et entraîneur TRL ; `chargement` lit le jeu par le lecteur contrôlé, recontrôle la provenance et pré-tokenise par `train.masque` (troncature des ids et des labels ensemble) ; `run` vérifie les invariants de campagne, prend `gpu.lock`, entraîne, sauvegarde l'adaptateur et écrit les coûts (10.3).

## Boundaries & Constraints

**Always:**
- Lectures de `train` par `core.artefacts` (`lire`, `ouvrir_sqlite_lecture`, `chemin_autorise`) ; le TOML de run et `config/modeles/<slug>.toml` passent par `charger_toml` (configuration, comme 10.3).
- `report_to="none"`, `push_to_hub=False`, jamais `save_total_limit`, `save_strategy="steps"` sous `runs/train/<run_id>/checkpoints/`.
- Graine posée (`set_seed`) **avant** le chargement du modèle et la pose de LoRA ; un adaptateur neuf par Run (W4.4) ; arguments d'entraînement complets consignés à chaque segment dans `entrainement.jsonl`.
- `run.json` : config résolue (TOML + invariants + plan de méthode), `graine`, `jeu_version`, `chat_template_sha256` ; `couts.json` porte aussi config, graine et environnement.
- Exceptions : seule une erreur d'import ou de bitsandbytes devient `ErreurQuantification` ; un OOM et `prepare_model_for_kbit_training` restent hors de cette conversion (W4.3).

**Never:**
- Aucun jeu de dépannage, aucune donnée rédigée ; aucun entraînement réel ni téléchargement dans cette story.
- Ne pas modifier `core/artefacts.py` (liste AD-24), `environnement.py` (zone 10.1) ni les documents de décision.
- `qlora-unsloth` : refusé jusqu'à la story 10.5.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Deux TOML, seule `methode` diffère | m1 puis m2 | deux runs `train`, config résolue dans chaque `run.json` | — |
| Invariant de campagne différent | run enregistré avec graine 1, nouveau TOML graine 2 | refus avant le verrou, champ cité | `ConfigurationInvalide` (code 1) |
| Jeu absent | `data/train/v9/` inexistant | run créé puis `partiel-erreur`, motif « bloqué : aucun jeu construit » | code 1 |
| MANIFEST d'un autre type | `type_run` ≠ `data-build` ou SHA de `train.jsonl` différent | refus | `ManifesteInvalide` (code 4) |
| `appel_id` inconnu ou d'`usage` ≠ `generation` | journal Mistral | refus | `ManifesteInvalide` |
| Mamba, FP8, vision non exclue | `config.json` des poids | refus, message clair | `ConfigurationInvalide` |
| ORPO sans `sft_run_id`, `sft_run_id` hors ORPO, `qlora-unsloth`, clé inconnue | TOML | refus à la validation (PiSSA est toujours en bf16 : nf4 impossible par construction) | `ConfigurationInvalide` |
| Reprise | `--reprendre <id>`, `checkpoints/checkpoint-2`, `-4` | `resume_from_checkpoint` = `checkpoint-4`, `couts-2.json` | run `complet` : refus |
| Reprise, TOML modifié | config résolue différente | refus | `ConfigurationInvalide` |
| Exemple plus long que `longueur_max` | ids et labels | tronqués ensemble ; exemple sans token supervisé écarté, compté | — |
| Lecture hors liste | `runs/eval/…`, `eval/…` | refus | `LectureInterdite` |

</intent-contract>

## Code Map

- `src/slmsp/train/config.py` -- `RunConfig`, `HyperParametres`, `charger_run_config`.
- `src/slmsp/train/methodes.py` -- `PlanMethode`, `plan_methode`, `config_bnb`, `config_lora`, `arguments_entrainement`, `charger_modele`, `creer_entraineur`.
- `src/slmsp/train/chargement.py` -- jeu, MANIFEST, recontrôle des `appel_ids`, contraintes du modèle, pré-tokenisation, `CollateurMasque`.
- `src/slmsp/train/run.py` -- invariants de campagne, `dernier_checkpoint`, `executer`.
- `src/slmsp/train/couts.py` -- `ecrire_mesures(..., contexte=)`.
- `src/slmsp/cli/train.py` -- `train run --config … [--reprendre <run_id>]`.
- `config/runs/m{1..4}-*-granite-4.0-1b.toml` -- gabarits de campagne.
- `tests/train/test_config.py`, `test_methodes.py`, `test_chargement.py`, `test_run.py`.

## Tasks & Acceptance

**Execution:**
- `config.py`, `config/runs/*.toml` -- schéma strict, gabarits M1 à M4 (même campagne, mêmes invariants).
- `methodes.py` -- table des méthodes : qlora (nf4 + LoRA), lora (bf16), dora (nf4 + `use_dora`), rslora (nf4 + `use_rslora`), pissa (bf16 + `init_lora_weights="pissa"`), orpo (nf4 + LoRA, `trl.experimental.orpo`).
- `chargement.py`, `run.py`, `cli/train.py`, `couts.py` -- voir matrice.
- tests -- une ligne de la matrice au moins par test, pile simulée ; test réel `lent` (tiny modèle) par `importorskip`.

**Acceptance Criteria:**
- Given deux TOML qui ne diffèrent que par `methode`, when on lance les deux Runs, then aucun code n'est modifié et chaque `run.json` porte la config résolue.
- Given une campagne, when un Run démarre, then version et SHA du jeu, graine, longueur maximale, SHA du chat template et version du masque sont comparés aux Runs enregistrés, refus sinon.
- Given un Run, when il s'exécute, then il prend `gpu.lock`, écrit `checkpoints/` sans `save_total_limit`, `adaptateur/`, `couts.json`.
- Given `--reprendre <run_id>`, when on relance, then l'entraînement reprend sur le dernier checkpoint du même dossier.

## Design Notes

- Invariants de campagne : lus dans `runs/train/*/run.json` par `core.artefacts.ouvrir_run` (manifestes, pas des données) ; tout run de la campagne qui a consigné ses invariants compte, quel que soit son statut (le refus est le côté sûr).
- Jeu absent : un run est créé pour consigner le blocage (`partiel-erreur`, motif préfixé « bloqué : »), faute de statut `bloque` dans AD-25.
- Troncature : `input_ids` et `labels` coupés ensemble à `longueur_max` (report 10.2) ; un exemple sans aucun label supervisé après coupe est écarté et compté dans `jeu.json`.

## Verification

**Commands:**
- `uv run pytest -q --tb=short tests/train` -- expected: vert, sans extra `train`.
- `uv run pytest -q --tb=line -p no:warnings`, `uv run ruff check`, `uv run ruff format --check` -- expected: verts hors échecs préexistants.
- Commande réelle, à lancer plus tard (jeu `data/train/v1` construit, GPU libre) : `uv run --extra train slmsp train run --config config/runs/m1-qlora-granite-4.0-1b.toml`.

## Auto Run Result

**Statut : review.** Aucun entraînement réel, aucun téléchargement, aucun appel d'API. Tests : `tests/train` 148 verts (pile simulée) ; le test réel `lent` (Llama minuscule à poids aléatoires, deux pas sur CPU, `cpu=True`) est sauté sans l'extra `train` et n'a donc pas été exécuté. Suite complète : 7 échecs hors zone (extra `mistralai` absent du venv du worktree : `test_prealables` ×3, `test_journal` ×1 ; préexistants : `test_ouvrir_juges_surcharge_le_mode`, `test_concurrence` ×2).

**W4 traités ici :** W4.1 (`use_dora`, `use_rslora` et PiSSA réellement posés par `methodes.PLANS` ; PiSSA sur base bf16 seulement ; ORPO par `trl.experimental.orpo`) ; W4.2 côté Run (toute exception termine le run `partiel-erreur`, `KeyboardInterrupt` `interrompu`, code ≠ 0) ; W4.3 (seules les erreurs d'import ou de bitsandbytes deviennent `ErreurQuantification`, OOM propagé, `prepare_model_for_kbit_training` dans le même `try`) ; W4.4 (graine avant chargement et LoRA, adaptateur neuf par Run, arguments complets consignés). Les autres points W4 (sonde 10.1) sont reportés (`deferred`).

**Décisions prises seul :**
- **Lecture de l'adaptateur (conflit AD-24 / CA7, note 10.6) — à confirmer par Anaël.** Option la plus réversible : `core/artefacts.py` n'est pas modifié. Le chemin de l'adaptateur SFT d'ORPO passe par `chemin_autorise(..., "train")`, qui lève aujourd'hui `LectureInterdite` : M4 refuse donc de démarrer, avec un message clair, tant que la liste du lecteur `train` n'inclut pas `runs/train/*/adaptateur/`. Le jour de l'amendement, aucune ligne de `train` ne change. La reprise relit ses propres checkpoints par `transformers` (`resume_from_checkpoint`), hors du lecteur contrôlé : à confirmer par Anaël qu'elle ne relève pas de CA7.
- Invariants de campagne lus dans les `run.json` des runs `train` par `core.artefacts.ouvrir_run` (manifestes, pas des données) ; tout run de la campagne qui les a consignés compte, quel que soit son statut ; le SHA du jeu s'ajoute à sa version.
- Jeu absent : un run est créé puis terminé `partiel-erreur`, motif « bloqué : … » (AD-25 n'a pas de statut `bloque`).
- Contrat provisoire du jeu en attendant 9.6 (`type_run = "data-build"`, `run_id`, `version`, `sha256_<fichier>`) : à aligner, voir `deferred`.
- Troncature : ids et labels coupés ensemble ; exemple sans token supervisé écarté et compté dans `jeu.json`. `ErreurMasque` refuse le Run.
- Même optimiseur (`adamw_torch`) et mêmes hyperparamètres par défaut pour toutes les méthodes (comparaison équitable) ; `warmup_steps` calculé depuis `echauffement_ratio` (évite `warmup_ratio`, déprécié dans transformers 5).
- Pad = token de fin existant si le tokenizer n'en a pas (aucun retaillage de l'embedding, note 10.6 C1) ; LoRA `all-linear` (ni `embed_tokens` ni `lm_head`).
- `couts.json` reçoit `config`, `graine`, `environnement`, `run_id` par un paramètre `contexte` d'`ecrire_mesures` (10.3) ; `metriques.jsonl` inchangé.
- Le test d'environnement 10.1 « `train run` non implémenté » est retiré (remplacé par les tests CLI de `test_run.py`).

**Commande réelle à lancer plus tard** (jeu `data/train/v1` construit par 9.6 puis 9.8, GPU libre) : `uv run --extra train slmsp train run --config config/runs/m1-qlora-granite-4.0-1b.toml`, puis m2 et m3 ; reprise : `... --reprendre <run_id>`. Test réel minuscule : `uv run --extra train pytest -m lent tests/train/test_run.py`.

## Revue

Revue du 2026-10-16 (Opus, avec la liste du second avis Haiku). D1 : aucun contenu rédigé, les fixtures sont des balises factices (`<question-factice-n>`, `<retenue-factice-n>`, `t1 t2`).

- **medium, corrigé** — ORPO recevait des `input_ids`/`labels` SFT (et `preferences.jsonl` était validé avec le schéma SFT) : `ORPOTrainer` (TRL 1.13.0, vérifié dans le paquet) exige des colonnes `prompt`, `chosen`, `rejected`. Schéma provisoire `_Paire` (`prompt`, `chosen`, `rejected`, `tools`, `tache`, `meta.appel_ids`) et `chargement.preparer_preferences` : rendu en texte par `train.rendu` (tools si protocole `natif`, `chat_template_kwargs`), car `ORPOTrainer` ne transmet ni l'un ni l'autre au template ; collateur de paires par défaut de TRL.
- **medium, corrigé** — L'invariant de campagne portait sur le SHA du fichier lu : M4 (`preferences.jsonl`) aurait été refusé dès qu'un M1 existait. Remplacé par `jeu_build` (run `data-build` du MANIFEST) ; le SHA du fichier reste dans `jeu` de la config résolue (et donc contrôlé à la reprise).
- **medium, corrigé** — `dernier_checkpoint` prenait un checkpoint interrompu pendant sa sauvegarde : seuls les checkpoints avec `trainer_state.json`, `optimizer.pt` et `scheduler.pt` (écrits par `Trainer._save_checkpoint`, `trainer_state.json` en dernier) sont retenus.
- **low, corrigé** — Arrêt entre `save_pretrained` et `terminer` : `--reprendre` bloquait sur `ArtefactExistant`. Si l'adaptateur est complet (`adapter_config.json`, `adapter_model.safetensors`), la reprise termine le run sans réentraîner ; un adaptateur incomplet reste refusé (jamais écrasé).
- **low, corrigé** — Campagne vérifiée avant le verrou seulement : vérifiée de nouveau sous `gpu.lock`, juste avant `nouveau_run` (deux lancements concurrents).
- **low, rejeté** — Checkpoint final absent si `max_steps` n'est pas multiple de `pas_sauvegarde` : `DefaultFlowCallback` (transformers 5.17) force une sauvegarde au dernier pas avec `save_strategy="steps"`.
- **low, corrigé** — Test de `--reprendre` sans valeur (code d'usage) ajouté, avec des tests du checkpoint incomplet, de la reprise après adaptateur et d'un M4 de la même campagne qu'un M1.
- **low, consigné (à trancher par Anaël)** — Lectures hors lecteur contrôlé : `transformers` relit `runs/train/<id>/checkpoints/` à la reprise, et ORPO lit `runs/train/<sft>/adaptateur/` (refusé aujourd'hui par `chemin_autorise`, AD-24). Décision AD-24 / CA7 de la note 10.6 non tranchée ici.

Points à confirmer par Anaël :
1. Amendement AD-24 pour `runs/train/*/adaptateur/` (M4) et statut des checkpoints relus par `transformers` vis-à-vis de CA7.
2. Format des paires ORPO (`prompt`, `chosen`, `rejected` en messages) à aligner sur la story 9.7 ; les `appel_ids` d'une paire désignent la génération Mistral de la réponse retenue (la rejetée vient du Modèle de base).
3. ORPO : le débit hors padding n'est pas mesuré (les lots d'`ORPOTrainer` n'ont pas d'`input_ids`, transformers ne compte aucun token) ; la troncature est celle de TRL (`max_length`), pas celle de `pretokeniser`.
