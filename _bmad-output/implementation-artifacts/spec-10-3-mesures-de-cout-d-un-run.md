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

**Problem:** comparer le coût des méthodes M1 à M4 exige des mesures identiques (durée, débit hors padding, VRAM maximale, énergie), indépendantes de la méthode.

**Approach:** un callback unique `CallbackCouts` (`slmsp.train.couts`), branché sur le `Trainer`, dont le protocole (pas de chauffe, période NVML) vit dans `config/entrainement.toml`, validé par `ConfigCouts`.

## Boundaries & Constraints

**Always:**
- torch n'est importé que dans les fonctions ; `pynvml` (déjà dépendance de base), torch et l'horloge sont injectables ; tests sans l'extra `train` ni GPU.
- Débit = tokens du compteur `state.num_input_tokens_seen` (hors padding) entre la fin du pas `pas_chauffe` et la fin de l'entraînement.
- VRAM maximale = max(`torch.cuda.max_memory_reserved`, VRAM utilisée max relevée par NVML) ; `max_memory_allocated` relevée à part.
- Énergie (Wh) = intégrale trapézoïdale de la puissance NVML échantillonnée toutes les `periode_echantillonnage_ms` (fil daemon).
- Sortie : une ligne `{"type": "couts", ...}` dans `metriques.jsonl` et `couts.json` (création exclusive) du run.

**Never:**
- Pas de mesure réelle ni de GPU ; pas de branchement dans `slmsp train run` (story 10.4) ; pas d'import de `measure` (AD-1).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Nominal | 30 pas, 100 tokens/pas | débit = tokens des pas 11 à 30 / durée correspondante | — |
| Moins de pas que la chauffe | 5 pas | `tokens_par_s` nul | — |
| NVML absent | `pynvml` indisponible | énergie et VRAM NVML nulles, le reste est mesuré | aucune exception |
| Échantillon NVML en échec | lecture lève | échantillon ignoré | silencieux |

</intent-contract>

## Code Map

- `src/slmsp/train/couts.py` -- `EchantillonneurNvml`, `CallbackCouts`, `creer_callback`.
- `src/slmsp/train/config.py` -- `ConfigCouts`, `ConfigEntrainement`, `charger_config_entrainement` (10.4 y ajoutera `RunConfig`).
- `config/entrainement.toml` -- section `[couts]`.
- `tests/train/test_couts.py` -- `Trainer`, torch et NVML simulés.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/train/config.py`, `config/entrainement.toml` -- protocole de coût validé (`extra="forbid"`).
- `src/slmsp/train/couts.py` -- callback et échantillonneur NVML.
- `tests/train/test_couts.py` -- débit sans padding ni chauffe, énergie, VRAM, NVML absent, fil réel, écriture.

**Acceptance Criteria:**
- Given un état simulé, when le débit est calculé, then padding et 10 premiers pas sont exclus.
- Given des relevés NVML simulés, when l'entraînement se termine, then l'énergie est l'intégrale de la puissance et la VRAM maximale le maximum des deux sources.
- Given la fin d'un Run, when les mesures sont écrites, then elles sont dans `metriques.jsonl` et `couts.json`.

## Design Notes

Le `CallbackHandler` de transformers appelle chaque événement `on_*` sur chaque callback : `CallbackCouts` répond par un no-op via `__getattr__`, ce qui évite d'importer `TrainerCallback` au niveau module.

## Verification

**Commands:**
- `uv run pytest -q tests/train/test_couts.py` -- expected: tous les tests passent

## Auto Run Result

Statut : done (en revue).

Décisions prises seul :
- Débit lu dans `state.num_input_tokens_seen` : la story 10.4 doit poser `include_num_input_tokens_seen="non_padding"` dans les arguments d'entraînement (à confirmer par Anaël si un autre compteur est préféré).
- `config/entrainement.toml` est structuré en tables (`[couts]`) pour que 10.4 puisse ajouter ses sections.
- `couts.json` est créé en exclusivité : une reprise (`--reprendre`) devra écrire sous un autre nom ou le 10.4 devra gérer l'existant.

Reports :
- Branchement du callback dans le `Trainer` (10.4) ; mesure réelle sur GPU (hors périmètre du run sans entraînement).
