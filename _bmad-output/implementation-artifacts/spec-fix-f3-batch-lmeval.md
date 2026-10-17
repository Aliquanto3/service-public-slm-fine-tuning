---
title: 'lm-eval : batch_size par modèle'
type: 'bugfix'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** `--batch_size auto` de lm_eval provoque des OOM CUDA pour MiniCPM5-1B (HF bf16, carte de 8 Go : belebele et french_bench_mc demandent 9,2 Go). La seule surcharge était par benchmark.

**Approach:** clé `lm_eval_batch_size` (entier > 0, optionnelle) dans `config/modeles/<slug>.toml`, validée par `ConfigModele`.

## Boundaries & Constraints

**Always:** priorité `options.batch_size` du benchmark > `lm_eval_batch_size` du modèle > `auto`. Le lot effectif reste consigné dans `SortieMoteur.batch_size` (`"1"` hors cible `hf`). Config du modèle absente : `auto`.

**Never:** aucun lancement GPU, lm_eval ou serveur (tests avec fakes).

</intent-contract>

## Code Map

- `src/slmsp/core/schemas/config_modele.py` : champ `lm_eval_batch_size`.
- `src/slmsp/benchmarks/moteurs/lm_eval.py` : `lot_modele`, `taille_lot(config, slug)`, `_lancer(..., lot)`.
- `config/modeles/minicpm5-1b.toml` : `lm_eval_batch_size = 4`.
- `tests/benchmarks/test_lm_eval.py` : priorité, config absente, validation.

## Verification

- `uv run pytest -q --tb=short tests/benchmarks tests/core tests/fetch`
- `uv run --no-sync python outils/controle_rapide.py`

## Auto Run Result

- `lm_eval_batch_size = 4` pour `minicpm5-1b` : valeur prudente, **à confirmer par mesure** (par Anaël, GPU).
- Report : RAM CPU (~12,75 Go sur mcq_eval) non traitée ici.

## Revue

- medium, corrigé : `lot_modele` avalait `ConfigurationInvalide` et ramenait l'OOM sans signal. Désormais seul un fichier absent donne `auto` (avertissement journalisé) ; un fichier présent mais invalide fait échouer le benchmark avec le message de `charger_toml`.
- low, corrigé : trois tests du chemin réel de `lot_modele` (config absente + journal, valeur 4, config invalide) sur une racine de projet factice.
- low, rejeté (acté, code inchangé) : la clé ne s'applique qu'aux références `base:<slug>`. La variante `apres` est sautée avant `taille_lot` (« seuls les modèles base:<slug> sont gérés ») ; les QCM HF ne portent donc que sur le modèle de base.
