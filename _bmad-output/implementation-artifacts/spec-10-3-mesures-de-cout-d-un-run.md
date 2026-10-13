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

**Problem:** pour comparer le coût des méthodes M1 à M4 sur une base identique, chaque Run doit mesurer durée, débit hors padding après chauffe, VRAM maximale et énergie, selon un protocole unique réglé en config.

**Approach:** un `TrainerCallback` unique (`slmsp.train.couts`), indépendant de la méthode, qui écrit les mesures dans `metriques.jsonl` et `couts.json` du run ; le protocole (pas de chauffe, période d'échantillonnage) vit dans `config/entrainement.toml`, validé par `ConfigCouts` (`train/config.py`).

## Boundaries & Constraints

**Always:**
- torch, transformers et pynvml ne sont importés que dans les fonctions (tests sans l'extra `train`, avec `Trainer`, torch et NVML simulés) ; `appliquer_environnement_impose()` avant tout import lourd.
- Débit = tokens de `state.num_input_tokens_seen` après `pas_chauffe` pas (10), divisés par le temps écoulé depuis la fin de la chauffe ; le callback refuse de démarrer (`ConfigurationInvalide`) si `include_num_input_tokens_seen != "non_padding"` (`arguments_mesure_cout()` fournit ce réglage à la config d'entraînement). Sur reprise, la chauffe se compte à partir du pas du checkpoint.
- VRAM maximale = maximum de `max_memory_allocated`, `max_memory_reserved` (pic remis à zéro au début) et du pic de mémoire utilisée NVML (échantillonné) ; énergie (Wh) = intégrale par trapèzes de la puissance NVML échantillonnée toutes les 200 ms par un fil daemon (relevé au début et à la fin).
- Écriture par `core.artefacts.Run` : lignes `type = "cout"` (à chaque `on_log`) et `type = "couts"` (finale) dans `metriques.jsonl`, plus `couts.json` ; artefacts jamais réécrits.

**Never:**
- Aucune dépendance à la méthode ; pas de `config/mesures.toml` (story 6.4) ; pas d'import de `measure` ; ni `run.py` ni `cli/train.py` (story 10.4) ; aucune donnée d'entraînement.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Débit | 30 pas de 50 tokens hors padding (128 avec), 10 premiers lents | `tokens_par_s` = 50, calculé sur les 20 derniers pas | — |
| Chauffe non finie | ≤ 10 pas | `tokens_par_s` nul | — |
| Énergie / VRAM | NVML simulé 100 W puis 200 W ; torch 3/4 Go, NVML 5 Go | énergie = intégrale en Wh ; `vram_max_octets` = 5 Go | — |
| NVML ou CUDA absent | `nvmlInit` échoue, pas de torch | champs nuls, `nvml_disponible` faux, motif consigné | le Run n'échoue pas |
| Comptage avec padding | `include_num_input_tokens_seen="all"` | refus au démarrage | `ConfigurationInvalide` |
| Reprise | `couts.json` existe déjà | écrit `couts-2.json`, `couts-3.json` | jamais d'écrasement |
| Arrêt anormal | l'appelant invoque `suivi.terminer(complet=False)` | `couts.json` avec `complet = false` | idempotent |

</intent-contract>

## Code Map

- `src/slmsp/train/couts.py` -- `SuiviCouts` (logique), `EchantillonneurNvml` (fil 200 ms), `energie_wh`, `creer_callback` (sous-classe de `TrainerCallback` construite à l'appel), `arguments_mesure_cout`.
- `src/slmsp/train/config.py` -- `ConfigCouts`, `ConfigEntrainement`, `charger_entrainement` (créé ici, complété par 10.4).
- `config/entrainement.toml` -- section `[couts]`.
- `src/slmsp/core/artefacts.py` -- `Run.ecrire`, `Run.ajouter_jsonl` (lus, non modifiés).

## Tasks & Acceptance

**Execution:**
- `config/entrainement.toml`, `src/slmsp/train/config.py` -- protocole de mesure et son modèle strict -- réglage hors code.
- `src/slmsp/train/couts.py` -- callback unique et échantillonneur NVML -- cœur de la story.
- `tests/train/test_couts.py` -- 21 tests sur `Trainer`, torch et NVML simulés (config, critères 1 à 3, reprise, NVML absent, fil, imports paresseux).

**Acceptance Criteria:**
- Given un état simulé avec padding connu, when le callback calcule le débit, then il exclut padding et 10 premiers pas.
- Given des relevés NVML simulés, when l'entraînement se termine, then l'énergie est l'intégrale de la puissance et la VRAM maximale le maximum des sources.
- Given la fin d'un Run, when les mesures sont écrites, then elles vont dans `metriques.jsonl` et `couts.json`, quelle que soit la méthode.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run pytest -q tests/train/test_couts.py` -- expected: 21 verts sans GPU.
- `uv run ruff check` et `uv run ruff format --check` -- expected: verts.

## Auto Run Result

**Statut : review.** Code et tests livrés ; aucun entraînement ni appel d'API.

**Décisions prises seul :**
- Le callback ne voit pas les batchs : le hors-padding repose sur le compteur du `Trainer` (`include_num_input_tokens_seen="non_padding"`), qui compare `input_ids` à `pad_token_id` (sous-compte si pad = eos). Refus explicite sans ce réglage. **À confirmer par Anaël** si un comptage maison (collator) est préféré.
- NVML relève la mémoire de toute la carte (bureau et autres processus compris) ; la VRAM maximale peut donc dépasser celle du seul Run. Conservé tel que le demande la story (maximum des deux sources) ; les trois sources restent distinctes dans `couts.json`.
- Une reprise écrit `couts-2.json`, `couts-3.json` (un par segment) plutôt que d'échouer en fin de Run sur `ArtefactExistant`.
- `Trainer.on_train_end` n'est pas appelé si l'entraînement lève : l'appelant (10.4) doit invoquer `callback.suivi.terminer(complet=False)` dans son `finally`.

**Reports :**
- 10.4 : passer `arguments_mesure_cout()` dans la config d'entraînement, ajouter `creer_callback(run, charger_entrainement().couts)` aux callbacks, appeler `suivi.terminer(complet=False)` en cas d'erreur, ajouter ses sections à `entrainement.toml` / `config.py`.
- Mesure réelle (GPU) non lancée : à valider lors du premier Run réel (10.4 / 11.2) en vérifiant que `tokens_par_s` et `energie_wh` ne sont pas nuls.

**Tests :** `tests/train/test_couts.py` 21 verts ; suite complète 3282 verts, 365 sautés, 2 échecs préexistants hors zone (extras absents) : `test_notation.py::test_ouvrir_juges_surcharge_le_mode` (`anthropic`) et `tests/mistral/test_journal.py::test_generation_sans_jeton_refusee[options1]` (`mistralai`). `ruff check` et `ruff format --check` verts.
