---
title: 'Story 6.1 — Orchestrateur déclaratif de benchmarks et téléchargement des benchmarks'
type: 'feature'
created: '2026-10-13'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred:
  - summary: >-
      Les jeux des 9 benchmarks ne sont pas épinglés : aucune révision ni SHA-256 réels n'ont été relevés (pas de téléchargement dans ce run).
    evidence: >-
      config/benchmarks/*.toml ne déclare de [[jeux]] que pour mcq_eval (AgentPublic/MCQ-eval) et traduction (FLORES-200, accès conditionnel), sans revision ni fichiers ; fetch benchmarks les consigne `non-epingle` et les saute.
    location: config/benchmarks/
    severity: medium
---

<intent-contract>

## Intent

**Problem:** Les benchmarks standardisés (FR-27) n'ont ni description déclarative, ni commande de lancement, ni téléchargement épinglé de leurs jeux ; `slmsp bench` et `slmsp fetch benchmarks` répondent « non implémentée ».

**Approach:** Un fichier `config/benchmarks/<nom>.toml` par benchmark, un orchestrateur qui sélectionne, prend le verrou GPU si besoin, confie chaque benchmark au moteur nommé (registre paresseux) et archive un `ResultatBench` par benchmark et variante dans un run `bench`. `fetch benchmarks` télécharge les jeux déclarés à leur révision épinglée.

## Boundaries & Constraints

**Always:** moteurs réels chargés paresseusement (jamais importés par les tests) ; sous-processus d'outil tiers lancés avec `env_sous_processus()` plus `HF_HUB_OFFLINE=1` et `HF_DATASETS_OFFLINE=1` ; une erreur de benchmark n'arrête pas les autres ; verrou GPU pris avant l'ouverture du run.

**Never:** aucun moteur réel (stories 6.2 et 6.3), aucune donnée d'entraînement, aucun réseau ni outil tiers dans les tests, pas d'invention de révisions ou de SHA-256.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nouveau benchmark | `x.toml`, moteur connu | `bench run --benchmarks x` l'exécute sans changer le code | — |
| Moteur inconnu | `moteur = "inexistant"` | refus avant tout run, message nommant benchmark et moteur | code 1 |
| Moteur livré mais module absent | `lm_eval` avant la story 6.2 | résultat `erreur`, les autres benchmarks continuent | run `partiel-erreur`, code 1 |
| Saut | moteur rend `saute="motif"` | résultat `saute`, motif consigné | run `complet` |
| GPU occupé | cible `hf` ou CUDA, verrou pris | refus sans run | code 5 |
| Jeu conditionnel refusé | HTTP non 200 sur un jeu `conditionnel` | ligne `acces-conditionnel`, jeu sauté | run `complet` |
| Jeu non épinglé | sans révision ou sans fichiers | ligne `non-epingle`, jeu sauté | run `complet` |

</intent-contract>

## Code Map

- `src/slmsp/core/schemas/bench.py` -- `JeuBench`, `FichierJeu`, `ResultatBench`.
- `src/slmsp/benchmarks/config.py` -- `BenchmarkConfig`, `charger_benchmarks`.
- `src/slmsp/benchmarks/moteurs/__init__.py` -- registre paresseux, `ContexteBench`, `SortieMoteur`, `env_outil`, `lancer_outil`.
- `src/slmsp/benchmarks/orchestrateur.py` -- `selectionner`, `lancer`.
- `src/slmsp/cli/bench.py` -- `bench liste`, `bench run`.
- `src/slmsp/fetch/benchmarks.py`, `src/slmsp/cli/fetch.py` -- `fetch benchmarks [BENCHMARK...]`.
- `config/benchmarks/*.toml` -- 9 benchmarks du socle.

## Tasks & Acceptance

**Execution:**
- Schémas, configuration, registre, orchestrateur et CLI `bench` (liste, run).
- `fetch benchmarks` branché sur le run `fetch` existant (profil `outillage`, `Telechargeur`).
- `tests/benchmarks/test_orchestrateur.py` (17 tests) et `tests/fetch/test_benchmarks.py` (6 tests) ; les deux anciens tests de délégation de `test_sources.py` sont retirés.

**Acceptance Criteria:**
- Given `config/benchmarks/`, when `slmsp bench liste`, then nom, moteur, cible, quantification, few-shot, limite et socle s'affichent.
- Given un `x.toml` au moteur connu, when `bench run --benchmarks x`, then il s'exécute ; un moteur inconnu est refusé.
- Given `fetch benchmarks`, when il tourne, then chaque jeu épinglé va sous `data/raw/benchmarks/<jeu>/<révision>/` ; conditionnel refusé et non épinglé sont consignés et sautés.
- Given un run terminé, then `runs/bench/<run_id>/<benchmark>--<variante>.json` porte scores, version du jeu, outil et version, configuration, durée ; `run.json` porte l'environnement.
- Given un outil tiers, then il reçoit `env_outil()`. Given cible `hf` ou CUDA, then le verrou GPU est pris. Given un échec, then le run finit `partiel-erreur`.

## Design Notes

- `cible = "hf"` impose `quantification = "avant"` (poids HF, avant quantification seulement). `--cible` et `--quantification` filtrent la sélection ; ils ne remplacent pas la configuration.
- Un moteur est un module `executer(config, contexte) -> SortieMoteur` ; l'orchestrateur ajoute durée, configuration et jeu.
- `fetch` et `benchmarks` sont au même niveau de couche : `JeuBench` vit dans `core/schemas/bench.py` et `fetch/benchmarks.py` lit lui-même les `[[jeux]]` des TOML.

## Verification

**Commands:**
- `uv run pytest -q --tb=short tests/benchmarks tests/fetch` -- expected: tout passe
- `uv run ruff check` et `uv run ruff format --check` -- expected: propres

## Auto Run Result

**Statut :** review.

**Décisions prises seul (solution la plus simple et la plus réversible).**
- 9 fichiers TOML au lieu de 7 : les 7 groupes de l'addendum §E, avec `ifeval`, `mmlu` et `crows_pairs_french` séparés (une tâche lm-eval chacun, un `ResultatBench` chacun). Tous `socle = true`. À confirmer par Anaël.
- `mmlu` limité à 500 items : le « limité » de l'énoncé n'a pas de valeur ; à confirmer par Anaël.
- Jeux non épinglés : voir `deferred` ; la commande à lancer plus tard est `uv run slmsp fetch benchmarks` une fois révisions et SHA-256 relevés dans les TOML.
- `--cible` et `--quantification` sont des filtres. Le verrou GPU est pris sans attente (échec rapide, code 5), une fois pour tout le run.
- Un fichier de résultat par benchmark et par variante (`<benchmark>--<variante>.json`), y compris en erreur ou saut.
- `worktree` : `uv sync` n'avait pas été fait (venv absent), je l'ai lancé.

**Reports.** Moteurs réels (6.2, 6.3), épinglage des jeux, tâche lm-eval personnalisée MCQ-eval.

## Revue

- medium, corrigé : une exception hors moteur (écriture du résultat, score refusé par `json_canonique`) laissait le run `en_cours` ; elle le termine maintenant en `partiel-erreur` avant de remonter (test ajouté).
- low, rejeté : une panne réseau épuisant les essais sur un jeu `conditionnel` est consignée `acces-conditionnel` avec le motif de l'erreur ; conforme à l'AC 3, sans risque pour les données.
- low, rejeté : si le 2e fichier d'un jeu conditionnel est refusé, les lignes du 1er ne sont pas consignées ; le jeu est sauté en entier, cohérent.
- Sans constat : AC 1 à 7, moteur inconnu refusé avant run, TOML invalide, noms uniques par fichier, couches, tests hors réseau.
