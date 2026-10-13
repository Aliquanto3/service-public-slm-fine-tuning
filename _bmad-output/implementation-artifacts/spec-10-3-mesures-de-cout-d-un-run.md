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
deferred:
  - 'Branchement dans le Run (story 10.4) : appeler `compter_lot(attention_mask)` depuis le collator, passer `creer_callback(MesureurCouts(...))` au Trainer, gérer la reprise (`couts.json` existe déjà : `Run.ecrire` lève `ArtefactExistant`).'
---

<intent-contract>

## Intent

**Problem:** comparer le coût des méthodes M1 à M4 exige des mesures identiques pour tous les Runs : durée, débit hors padding, VRAM maximale, énergie.

**Approach:** un callback unique `train/couts.py` (logique pure `MesureurCouts` + `creer_callback` qui l'enveloppe dans un `TrainerCallback`), un protocole réglé dans `config/entrainement.toml` et validé par `ConfigCouts`.

## Boundaries & Constraints

**Always:**
- torch, transformers et pynvml importés dans les fonctions seulement ; tests sans l'extra `train`, avec torch, NVML et `Trainer` simulés.
- Débit = tokens au masque d'attention à 1, comptés après les `pas_chauffe` premiers pas (10).
- VRAM max = maximum de `torch.cuda.max_memory_reserved` et du pic `used` NVML (l'allouée est consignée aussi). Énergie = intégrale trapézoïdale de la puissance NVML échantillonnée toutes les 200 ms, en Wh.
- Sortie : une ligne `type = "couts"` dans `metriques.jsonl` et `couts.json` du run, quelle que soit la méthode.

**Never:** importer `measure` depuis `train` (AD-1) ; toucher à `config/mesures.toml` (story 6.4) ; créer `RunConfig` ou brancher le callback dans un Run (story 10.4).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Nominal | 5 pas, lots avec padding, chauffe 3 | débit sur les pas 4 à 5, padding exclu | — |
| Chauffe inachevée | moins de `pas_chauffe + 1` pas | `tokens_par_seconde = null` | — |
| NVML ou CUDA absent | init NVML en échec, `cuda` faux | VRAM/énergie `null`, pas d'exception | mesures partielles consignées |

</intent-contract>

## Code Map

- `src/slmsp/train/couts.py` -- `MesureurCouts`, `EchantillonneurNvml` (fil, 200 ms), `integrer_energie_wh`, `creer_callback`.
- `src/slmsp/train/config.py` -- `ConfigCouts`, `ConfigEntrainement`, `charger_config_entrainement` (créé ici, complété par 10.4).
- `config/entrainement.toml` -- `[couts] pas_chauffe = 10`, `periode_echantillonnage_ms = 200`.
- `tests/train/test_couts.py` -- 10 tests (débit, énergie, VRAM, NVML absent, écriture, fil, callback, config).

## Tasks & Acceptance

**Execution:**
- `config/entrainement.toml`, `train/config.py` -- protocole et validation (clés inconnues refusées).
- `train/couts.py` -- callback et mesures.
- `tests/train/test_couts.py` -- critères 1 à 3 et cas limites.

**Acceptance Criteria:**
- Given un état simulé avec padding connu, when le débit est calculé, then padding et 10 premiers pas sont exclus.
- Given des relevés NVML simulés, when l'entraînement se termine, then l'énergie en Wh est l'intégrale de la puissance et la VRAM max le maximum des deux sources.
- Given la fin d'un Run, when les mesures sont écrites, then elles vont dans `metriques.jsonl` et `couts.json`.

## Verification

- `uv run pytest tests/train/test_couts.py` -- vert sans GPU.
- `uv run pytest`, `uv run ruff check`, `uv run python outils/controle_rapide.py`.

## Auto Run Result

**Statut : review.** Code seul, sans GPU ni API.

**Décisions prises seul :**
- Le callback ne peut pas lire les tokens de padding dans l'état du `Trainer` : le collator (10.4) les déclare par `MesureurCouts.compter_lot(attention_mask)`. Choix le plus simple et réversible.
- `creer_callback` fabrique la sous-classe de `TrainerCallback` à l'appel (import différé), la logique reste testable sans `transformers`.
- Chronomètre du débit lancé à la fin du pas `pas_chauffe` (compté depuis le début du callback, non depuis `global_step` : robuste à la reprise).
- `ConfigEntrainement` porte la seule table `couts` ; 10.4 ajoute les siennes. À confirmer par Anaël : la VRAM « NVML » est la mémoire utilisée de tout le GPU (bureau et autres processus compris), pas celle du seul processus.

**Reports :** branchement et reprise dans le Run (10.4, voir `deferred`) ; mesure réelle (RTX 3050, `nvidia-ml-py` déjà dans les dépendances) à faire lors du premier Run réel.
