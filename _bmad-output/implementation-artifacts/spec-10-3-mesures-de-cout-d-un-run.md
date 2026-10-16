---
title: 'Story 10.3 — Mesures de coût d''un Run (FR-33)'
type: 'feature'
created: '2026-10-13'
status: 'review'
baseline_revision: 'f556fab38f8a973eba4ce8087789f9c3842d4108'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-10-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred:
  - 'Brancher `creer_callback` et `ARGUMENTS_TRAINER` dans le Run (story 10.4) : `Trainer.add_callback`, `ecrire_mesures(run, callback.mesures())` dans un `finally`.'
  - 'Vérifier avec l''extra `train` (transformers 5.17.0) que `include_num_input_tokens_seen="non_padding"` alimente `state.num_input_tokens_seen` hors padding (hypothèse non testée ici : extra absent).'
---

<intent-contract>

## Intent

**Problem:** FR-33 exige de comparer le coût des méthodes M1 à M4 sur une base identique (durée, débit hors padding, VRAM, énergie). Aucun module ne le mesure.

**Approach:** un callback `Trainer` unique, `slmsp.train.couts.CallbackCouts`, indépendant de la méthode, dont le protocole (pas de chauffe, période NVML) vit dans `config/entrainement.toml` (`ConfigCouts`). Les mesures vont dans `metriques.jsonl` et `couts.json` du run.

## Boundaries & Constraints

**Always:**
- torch, transformers et pynvml ne sont importés que dans les fonctions (ou injectés) : tests sans l'extra `train` ni GPU.
- Débit = tokens de `state.num_input_tokens_seen` (différence, donc valable en reprise) entre la fin du pas `pas_chauffe` et le dernier pas, divisés par le temps écoulé. Si `args.include_num_input_tokens_seen != "non_padding"` ou si le compteur manque : aucun débit, un avertissement (jamais un débit avec padding).
- VRAM maximale = max(`max_memory_allocated`, `max_memory_reserved`, mémoire utilisée max relevée par NVML). Énergie = intégrale trapézoïdale de la puissance NVML (W) échantillonnée toutes les `periode_echantillonnage` s.
- NVML ou CUDA indisponible, relevé en erreur : la mesure concernée vaut `None`, un avertissement est consigné, l'entraînement continue.
- Un fichier de mesures existant n'est jamais écrasé (`couts-2.json` pour un segment de reprise).

**Never:**
- Ne pas importer `measure` (AD-1) : le protocole est dans `config/entrainement.toml`, pas dans `config/mesures.toml`.
- Ne pas câbler le callback dans un Run (`train run` : story 10.4) ni toucher à `environnement.py`, `cli/train.py`, `pyproject.toml`.
- Aucune donnée d'entraînement réelle ; aucun appel d'API.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Débit nominal | 12 pas de 20 tokens hors padding (32 avec), chauffe 10 | `tokens_mesures` = 40, débit 20 tok/s, padding et 10 premiers pas exclus | — |
| Moins de pas que la chauffe | 10 pas, chauffe 10 | `debit_tokens_par_s` = None | avertissement « chauffe » |
| Comptage avec padding | `include_num_input_tokens_seen` ∈ {no, all, True} | débit None | avertissement `non_padding` |
| Reprise sur checkpoint | compteur de tokens déjà à 5000 | débit calculé en différence | — |
| NVML simulé | 100 W puis 200 W puis 200 W | énergie = intégrale en Wh ; VRAM max = max des deux sources | — |
| NVML indisponible | `nvmlInit` lève | énergie et VRAM NVML None, VRAM torch conservée | avertissement NVML |
| CUDA indisponible | `is_available()` faux | VRAM torch None, énergie conservée | avertissement CUDA |
| Fin de Run | mesures prêtes | ligne `couts` dans `metriques.jsonl` + `couts.json`, quelle que soit la méthode | `ValueError` si une mesure n'est pas finie |
| Seconde écriture (reprise) | `couts.json` existe | `couts-2.json`, `segment` = 2 | — |

</intent-contract>

## Code Map

- `src/slmsp/train/couts.py` -- `CallbackCouts`, `EchantillonneurNvml`, `integrer_energie_wh`, `creer_callback`, `ecrire_mesures`, `MesuresCout`, `ARGUMENTS_TRAINER`.
- `src/slmsp/train/config.py` -- `ConfigCouts`, `ConfigEntrainement`, `charger_config_couts` (créé ici ; `RunConfig` en 10.4).
- `config/entrainement.toml` -- `[couts]` : `pas_chauffe = 10`, `periode_echantillonnage = 0.2`, `indice_gpu = 0`.
- `tests/train/test_couts.py` -- Trainer, torch, NVML et horloge simulés.
- `src/slmsp/core/artefacts.py` -- `Run.ecrire`, `Run.ajouter_jsonl` (écriture des mesures).

## Tasks & Acceptance

**Execution:**
- `config/entrainement.toml`, `src/slmsp/train/config.py` -- protocole de coût validé (`extra="forbid"`) -- AD-18.
- `src/slmsp/train/couts.py` -- callback, échantillonneur NVML en fil, mesures, écriture -- cœur de FR-33.
- `tests/train/test_couts.py` -- un test par ligne de la matrice, plus la config et l'absence d'import lourd.

**Acceptance Criteria:**
- Given un état d'entraînement simulé avec padding connu, when le callback calcule le débit, then il exclut le padding et les 10 premiers pas.
- Given des relevés NVML simulés, when l'entraînement se termine, then l'énergie en Wh est l'intégrale de la puissance et la VRAM maximale le maximum des deux sources.
- Given la fin d'un Run, when les mesures sont écrites, then elles vont dans `metriques.jsonl` et `couts.json`, avec les mêmes clés pour qlora, lora, dora et orpo.

## Spec Change Log

## Review Triage Log

## Design Notes

`CallbackCouts` n'hérite pas de `TrainerCallback` au niveau module (import de transformers interdit au chargement). `creer_callback` fabrique à l'exécution `type("CallbackCoutsTrainer", (CallbackCouts, TrainerCallback), {})` : nos trois événements priment, les autres viennent de la base. La VRAM torch n'est pas remise à zéro au début : elle inclut le chargement du modèle, qui fait partie du coût d'un Run.

## Verification

**Commands:**
- `uv run pytest -q --tb=short tests/train/test_couts.py` -- expected: vert, sans GPU.
- `uv run pytest -q --tb=line -p no:warnings` puis `uv run ruff check` et `uv run ruff format --check` -- expected: verts, hors `test_notation.py::test_ouvrir_juges_surcharge_le_mode` (extra `anthropic` absent).

## Auto Run Result

**Statut : review.** Aucun entraînement, aucune mesure réelle, aucun appel d'API.

**Décisions prises seul :**
- Tokens hors padding lus dans `state.num_input_tokens_seen` (fourni par `include_num_input_tokens_seen="non_padding"`) plutôt que par un collator enveloppé : plus simple, réversible. Hypothèse à vérifier au premier Run réel (report 10.4).
- Reprise sur checkpoint : un segment de plus (`couts-2.json`, ligne `segment` = 2 dans `metriques.jsonl`) au lieu d'écraser ou d'échouer. À confirmer par Anaël si une autre convention (un seul `couts.json` cumulé) est préférée.
- Pas de remise à zéro des pics `torch.cuda` : la VRAM maximale inclut le chargement du modèle. Si la 10.4 veut la VRAM du seul entraînement, appeler `torch.cuda.reset_peak_memory_stats()` avant `on_train_begin`.
- La VRAM NVML est celle de la carte entière (autres processus et bureau WDDM compris), d'où le maximum avec torch plutôt qu'une moyenne.
- `indice_gpu` ajouté au protocole (défaut 0), faute de quoi NVML interrogerait une carte arbitraire sur une machine multi-GPU.

**Reports :** câblage dans `train run` et vérification du compteur de tokens avec transformers 5.17.0 (story 10.4, voir `deferred`).

## Revue

- low, corrigé : test d'hygiène d'import dépendait de l'install éditable du venv (`-I` ignore PYTHONPATH) ; remplacé par `-s` (PYTHONPATH honoré, src du checkout prioritaire).
- low, corrigé : `_importer("torch")` n'attrapait que ImportError ; il attrape désormais toute exception (OSError de DLL CUDA) et le callback dégrade en avertissement.
- low, corrigé : VRAM torch lue sur `indice_gpu` (et non le device courant), cohérente avec NVML.
- low, rejeté : énergie/VRAM NVML de la carte entière, déjà documenté (docstring et décisions prises seul).
- low, rejeté : trapèze à travers des relevés de puissance absents ; l'intégrale reste correcte sur les instants valides et les erreurs NVML sont déjà signalées en avertissement.
- low, consigné : `couts.json` ne porte ni configuration, ni graine, ni environnement (ils vivent dans le Run) ; `ecrire_mesures` n'est pas câblé dans un Run, reporté en 10.4.
