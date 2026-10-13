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
deferred: []
---

<intent-contract>

## Intent

**Problem:** pour comparer le coût des méthodes M1 à M4 sur une base identique, chaque Run doit mesurer durée, débit hors padding, VRAM maximale et énergie de la même façon, quelle que soit la méthode.

**Approach:** un callback unique `slmsp.train.couts` (`MesureCouts`, enveloppé en `TrainerCallback` par `creer_callback`), dont le protocole (pas de chauffe, période NVML) est lu dans `config/entrainement.toml` (`ConfigCouts`, `train/config.py`), et qui écrit `metriques.jsonl` et `couts.json` dans le run.

## Boundaries & Constraints

**Always:**
- torch, transformers et pynvml ne sont importés que dans les fonctions (injectables : `torch=`, `nvml=`, `transformers=`) ; les tests tournent sans l'extra `train`, sans GPU.
- Débit = tokens vus hors padding entre la fin du pas de chauffe et la fin de l'entraînement, divisés par la durée correspondante ; les pas se comptent depuis le début de la session (reprise sur checkpoint comprise).
- VRAM maximale = max(`torch.cuda.max_memory_allocated`, `max_memory_reserved`, mémoire NVML utilisée) ; les pics torch sont remis à zéro au début du Run.
- Énergie (Wh) = intégrale de la puissance NVML par la règle des trapèzes, échantillonnée toutes les `periode_nvml_ms` par un fil daemon (relevés au début et à l'arrêt compris).
- Écriture par `Run.ajouter_jsonl("metriques.jsonl")` et `Run.ecrire("couts.json")` ; un `couts.json` existant n'est jamais réécrit (`couts-2.json`, …).

**Never:**
- Pas de `slmsp train run` ni de câblage dans un Trainer (story 10.4) ; pas d'entraînement ni de mesure réels ; pas de `config/mesures.toml` (story 6.4) ; aucune donnée d'entraînement.
- Ne rien écrire hors de `train/couts.py`, `train/config.py`, `config/entrainement.toml`, `tests/train/test_couts.py` et la spec.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Nominal | 14 pas de 100 tokens utiles en 1 s, chauffe 10 | 4 pas mesurés, 400 tokens, 100 tokens/s | — |
| Moins de pas que la chauffe | ≤ 10 pas | `tokens_par_s = null`, `pas_mesures = 0` | pas d'erreur |
| Reprise | `global_step` part de 200 | la chauffe se compte depuis le début de la session | — |
| Compte avec padding | `include_num_input_tokens_seen` ≠ `"non_padding"` | refus au `on_train_begin` | `ConfigurationInvalide` |
| NVML absent ou en échec | `nvmlInit` lève | `energie.wh = null`, VRAM torch seule, motif consigné | Run non interrompu |
| Entraînement interrompu | exception avant `on_train_end` | `terminer()` (idempotent) écrit les mesures | appel en `finally` par 10.4 |
| Reprise : `couts.json` existe | second callback sur le même run | `couts-2.json` | pas de réécriture |

</intent-contract>

## Code Map

- `src/slmsp/train/couts.py` -- `EchantillonneurNvml` (fil, trapèzes), `MesureCouts` (événements du Trainer, résultat, écriture), `creer_callback`, `ARGUMENTS_COMPTE_TOKENS`.
- `src/slmsp/train/config.py` -- `ConfigCouts`, `ConfigEntrainement`, `charger_config_entrainement` (la 10.4 y ajoute `RunConfig`).
- `config/entrainement.toml` -- `pas_chauffe = 10`, `periode_nvml_ms = 200`.
- `src/slmsp/core/artefacts.py` -- `Run.ecrire`, `Run.ajouter_jsonl` ; `core/config.py` -- `charger_toml`.
- `src/slmsp/core/artefacts.py:140` -- usage existant de `pynvml` (`nvidia-ml-py` est une dépendance du cœur).
- `tests/train/test_couts.py` -- Trainer, torch et NVML simulés.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/train/config.py`, `config/entrainement.toml` -- créer `ConfigCouts` et le fichier de protocole -- protocole en config (AD-18).
- `src/slmsp/train/couts.py` -- callback unique de mesure -- FR-33.
- `tests/train/test_couts.py` -- débit hors padding, énergie, VRAM, NVML absent, écriture, reprise, callback, config.

**Acceptance Criteria:**
- Given un état d'entraînement simulé avec padding connu, when le callback calcule le débit, then il exclut le padding et les 10 premiers pas.
- Given des relevés NVML simulés, when l'entraînement se termine, then l'énergie en Wh est l'intégrale de la puissance et la VRAM maximale le maximum des deux sources.
- Given la fin d'un Run, when les mesures sont écrites, then elles vont dans `metriques.jsonl` et `couts.json`, quelle que soit la méthode.

## Design Notes

- Le compte de tokens vient de `state.num_input_tokens_seen`. Le `Trainer` l'alimente hors padding avec `include_num_input_tokens_seen="non_padding"` : `ARGUMENTS_COMPTE_TOKENS` est à fusionner dans les arguments d'entraînement par la 10.4. Le callback refuse tout autre mode, pour qu'un débit avec padding ne fausse jamais la comparaison.
- La mémoire NVML est celle du GPU entier (autres processus compris, bureau Windows compris) : c'est pourquoi le maximum est pris avec les compteurs torch, sans les remplacer.

## Verification

**Commands:**
- `uv run pytest -q tests/train/test_couts.py tests/test_architecture.py` -- expected: vert.
- `uv run pytest -q --tb=line -p no:warnings`, `uv run ruff check`, `uv run ruff format --check` -- expected: verts, hors échec préexistant `test_notation.py::test_ouvrir_juges_surcharge_le_mode`.

## Auto Run Result

**Statut : review.** Code et tests écrits ; aucun entraînement, aucune mesure réelle, aucun appel d'API.

**Décisions prises seul :**
- `MesureCouts` (logique pure, testable) est séparé de `creer_callback`, qui construit une sous-classe de `transformers.TrainerCallback` à l'appel : la classe ne peut pas hériter de `TrainerCallback` au niveau module sans importer transformers.
- Débit pris sur `state.num_input_tokens_seen` plutôt que par un collator enveloppé : plus simple et réversible. **À confirmer à l'installation de l'extra `train`** (non installé ici) : la valeur `"non_padding"` de `include_num_input_tokens_seen` dans transformers 5.17. Si elle diffère, ne changer que `MODE_TOKENS_HORS_PADDING`.
- Reprise sur checkpoint : `couts.json` n'est jamais réécrit, la mesure suivante va dans `couts-2.json` (et une ligne de plus dans `metriques.jsonl`). **À confirmer par Anaël** si la 10.4 préfère un seul fichier cumulé.
- `ConfigEntrainement` porte `schema_version = 1` et `couts` ; la 10.4 y ajoute ses sections sans changer ces clés.

**Reports (pour la 10.4) :**
- Fusionner `ARGUMENTS_COMPTE_TOKENS` dans les arguments du Trainer, ajouter `creer_callback(MesureCouts(run, config.couts))` aux callbacks, et appeler `mesure.terminer()` dans un `finally`.
- Vérifier sur un vrai Trainer, GPU libre sous `gpu.lock` : `uv run slmsp train run --config … ` (quand la 10.4 existera) puis contrôler `runs/train/<run_id>/couts.json` (débit, VRAM, énergie non nuls).
- L'énergie NVML est celle de la carte entière (pas de la seule process) ; la tarification en kWh/€ n'est pas dans la story.
