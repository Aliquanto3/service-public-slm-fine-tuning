---
title: 'Commande bench cache-hf (cache HF des jeux lm_eval)'
type: 'feature'
created: '2026-10-19'
status: 'review'
baseline_commit: 'c86843d'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/etat-run-2026-10-17-portable.md (incident du cache HF)'
warnings: []
deferred:
  - 'Non exécuté en réel (consigne : aucun téléchargement) : `get_dataset_config_names` hors ligne et le chargement de toutes les configurations (cais/mmlu, Global-MMLU-Lite) sont à valider par un premier `slmsp bench cache-hf` en phase 1. Si une configuration inutile alourdit le cache, ajouter une liste de configurations par dépôt dans `[options]`.'
---

## Intent
Aucune commande ne remplissait le cache HF des jeux `lm_eval` : 7 benchmarks HF avaient échoué, le cache a été rempli à la main (515 Mo).

## Approach
- `slmsp bench cache-hf [DEPOT...]` (`src/slmsp/benchmarks/cache_hf.py`, `src/slmsp/cli/bench.py`). Dépôts et révisions : union des `[options.jeux_hf]` de `config/benchmarks/*.toml` (deux révisions pour un dépôt : erreur ; dépôt demandé absent de la config : `ConfigurationInvalide`).
- Par jeu : `snapshot_download(repo_type="dataset", revision)`, `refs/main` écrit sur la révision, `load_dataset(depot, <chaque configuration>, revision)` en ligne. Idempotent : un contrôle hors ligne préalable (sous-processus, `HF_DATASETS_OFFLINE=1`, `HF_HUB_OFFLINE=1`) saute le jeu déjà lisible dont snapshot et `refs/main` sont corrects ; un snapshot présent n'est pas retéléchargé.
- Contrôle final hors ligne de tous les jeux traités ; `CacheHorsLigneInvalide` (code d'erreur) sinon.
- Journal : run `fetch` de slug `jeux-hf`, `fichiers.jsonl` (une ligne par jeu : `telecharge` ou `deja-present`), `partiel-erreur` en cas d'échec, comme les autres sous-commandes.
- Emplacement : `bench`, pas `fetch` : `tests/fetch/test_hf.py` interdit à `fetch` `snapshot_download` et `subprocess` (AD-28, transfert hors client gardé), que cette commande exige. `preparer()` rebranche la passerelle `net` sur `huggingface_hub` comme `preparer_hf`. Le run reste de type `fetch` (slug `cache-hf`), comme les autres téléchargements. Venv : celui de la phase 1 (`fetch` + `bench`) : `huggingface-hub` 2.2.0 vient de `fetch`, `datasets` de `lm-eval` (extra `bench`, qui ne conflit pas avec `fetch`) ; `fetch` et `train` étant en conflit, la phase 2 ne convient pas. Imports de `huggingface_hub` et `datasets` à l'appel ; le contrôle utilise `sys.executable`. Le contrôle de `fetch` (`controle_rapide`) reste vert : `benchmarks` n'importe pas `fetch`.
- Doc : `docs/reprise-deuxieme-pc.md` (phase 1) ; note dans l'en-tête de `outils/migration/restaurer-etat.ps1`.

## Tests
`tests/benchmarks/test_cache_hf.py` : mocks de `snapshot_download`, `load_dataset` et du contrôle hors ligne ; idempotence, `refs/main` (écriture et correction), contrôle hors ligne en échec, jeu absent de la config, révisions contradictoires, run journalisé de bout en bout, lecture du sous-processus de contrôle.

## Auto Run Result
- Statut : review. Pas de fusion, aucun accès réseau, `models/.cache-hf` du dépôt principal intact.
- Décisions seul : toutes les configurations de chaque dépôt sont chargées (la config ne nomme pas les sous-ensembles) ; pas de jeton HF (jeux publics) ; `--racine` ne déplace que le run, le cache suit `SLMSP_MODELS_DIR`. À confirmer par Anaël : le premier passage réel (voir `deferred`).
