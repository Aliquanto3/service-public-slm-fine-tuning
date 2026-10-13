---
title: 'Story 10.3 — Mesures de coût d''un Run (FR-33)'
type: 'feature'
created: '2026-10-13'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-10-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** pour comparer le coût des méthodes M1 à M4 sur une base identique, chaque Run doit mesurer durée, débit hors padding, VRAM maximale et énergie, de la même façon quelle que soit la méthode.

**Approach:** un callback unique `CallbackCouts` (`slmsp.train.couts`), réglé par `config/entrainement.toml` (`ConfigCouts`), qui écrit une ligne `couts` dans `metriques.jsonl` et un `couts.json` dans le run.

## Boundaries & Constraints

**Always:**
- torch, transformers et pynvml importés dans les fonctions seulement ; tests sans l'extra `train`, avec `Trainer`, torch et NVML simulés.
- Débit = tokens hors padding (`state.num_input_tokens_seen`, donc `include_num_input_tokens_seen="non_padding"` côté Run) entre la fin du pas de chauffe (10) et le dernier pas ; `None` si pas assez de pas ou aucun comptage.
- VRAM max = maximum de `max_memory_allocated`, `max_memory_reserved` et de la mémoire NVML échantillonnée ; énergie = intégrale trapézoïdale de la puissance NVML (200 ms), en Wh.
- Sans NVML ou sans CUDA : valeurs `None`, jamais d'échec de l'entraînement.

**Never:** modifier `methodes.py`, `run.py`, `cli/train.py` (story 10.4) ; ajouter `RunConfig` ; lire `config/mesures.toml` (story 6.4, `train` n'importe pas `measure`).

</intent-contract>

## Code Map

- `src/slmsp/train/couts.py` -- `CallbackCouts`, `SondeNvml`, `energie_wh`, `callback_trainer` (adaptateur `TrainerCallback`).
- `src/slmsp/train/config.py` -- `ConfigCouts`, `ConfigEntrainement`, `charger_config_entrainement` ; 10.4 y ajoutera `RunConfig`.
- `config/entrainement.toml` -- `[couts]` : `pas_chauffe = 10`, `periode_echantillonnage_ms = 200`, `indice_gpu = 0`.
- `tests/train/test_couts.py` -- 12 tests sur états simulés.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/train/couts.py`, `config.py`, `config/entrainement.toml` -- créés comme ci-dessus.
- `tests/train/test_couts.py` -- débit (chauffe, padding), énergie, VRAM des deux sources, fil d'échantillonnage, écritures, config.

**Acceptance Criteria:**
- Given un état simulé avec padding connu, when le débit est calculé, then padding et 10 premiers pas sont exclus.
- Given des relevés NVML simulés, when l'entraînement se termine, then l'énergie est l'intégrale de la puissance et la VRAM max le maximum des deux sources.
- Given la fin d'un Run, when les mesures sont écrites, then `metriques.jsonl` et `couts.json` les contiennent, quelle que soit la méthode.

## Verification

**Commands:**
- `uv run pytest -q tests/train/test_couts.py` -- expected: tout passe.

## Auto Run Result

Statut : review. Décisions prises seul (solution simple et réversible) :
- Les tokens hors padding viennent de `num_input_tokens_seen` (aucun accès au batch depuis un callback). **À confirmer par Anaël / story 10.4** : le Run doit poser `include_num_input_tokens_seen="non_padding"`.
- `CallbackCouts` est duck-typé (pas de base `TrainerCallback` au niveau module) ; `callback_trainer` fournit l'adaptateur transformers, non testé sans l'extra `train`.
- `indice_gpu` ajouté à `[couts]` (hors liste de la story, nécessaire à NVML).

Reports :
- Reprise sur checkpoint : `couts.json` est créé en exclusivité (`Run.ecrire`) ; à la reprise, la 10.4 devra choisir un autre nom ou cumuler les mesures.
- Branchement dans `run.py` (ajout du callback au `Trainer`) : story 10.4.
- Mesures réelles sur GPU : non lancées (consigne de la nuit).
