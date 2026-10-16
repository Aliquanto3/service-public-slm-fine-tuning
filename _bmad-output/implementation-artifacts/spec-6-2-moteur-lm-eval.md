---
title: 'Story 6.2 — Moteur lm-eval : QCM sur poids HF et ifeval contre llama-server'
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
      Le schéma réel d'AgentPublic/MCQ-eval n'est pas connu (jeu non épinglé, rien téléchargé) : le chargeur accepte des noms de colonnes courants, à confirmer au premier fetch.
    evidence: >-
      config/benchmarks/mcq_eval.toml sans revision ni fichiers ; utils.py devine question, choices/options/choix ou A..H, answer/reponse.
    location: src/slmsp/benchmarks/taches_lmeval/agentpublic_mcq/utils.py
    severity: medium
  - summary: >-
      ifeval a besoin des dépendances optionnelles de lm-eval (langdetect, immutabledict, nltk) ; l'extra `bench` n'épingle que lm-eval==0.4.13. Pyproject et uv.lock non modifiés.
    evidence: pyproject.toml, extra bench.
    location: pyproject.toml
    severity: medium
---

<intent-contract>

## Intent

**Problem:** Les benchmarks lm-evaluation-harness du socle (QCM français et domaine, biais, ifeval) n'ont pas de moteur : le registre de la 6.1 nomme `lm_eval` sans module.

**Approach:** Un moteur `lm_eval` qui lance `lm_eval` en sous-processus (backend `hf` sur les poids HF, `local-chat-completions` vers `llama-server` pour ifeval), puis analyse le JSON en `SortieMoteur`. Une tâche lm-eval personnalisée lit le jeu MCQ-eval local.

## Boundaries & Constraints

**Always:** `lm_eval` jamais importé (sous-processus, `env_outil()` : HF hors ligne, sans secret) ; serveur sur `127.0.0.1` ; verrou GPU laissé à l'orchestrateur (`prendre_verrou_gpu=False`) ; tâche MCQ-eval sans réseau.

**Never:** aucun appel réel à lm-eval, aucun téléchargement, aucune donnée d'entraînement (fixtures factices), pas de changement de `pyproject.toml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| QCM sur poids HF | `base:<slug>`, `models/<slug>/hf-bf16` ou `hf` | `--model hf`, few-shot et `--limit` de la config, scores | — |
| GGUF seul (Ministral 3 8B) | ni `hf-bf16` ni `hf` | `saute` avec motif nommant le modèle | — |
| ifeval | GGUF de la variante | `local-chat-completions` vers `http://127.0.0.1:<port>/v1/chat/completions` | — |
| GGUF absent pour la variante | base × `avant` (pas de F16) | `saute` avec le motif de `resoudre` | — |
| MCQ-eval | jeu non épinglé ou absent | `saute` avec motif | — |
| `lm_eval` échoue | code non nul ou sans `results*.json` | `LmEvalEchoue` (résultat `erreur`) | queue de stderr dans le motif |

</intent-contract>

## Code Map

- `src/slmsp/benchmarks/moteurs/lm_eval.py` -- moteur : `executer`, `analyser`, `serveur_llama`.
- `src/slmsp/benchmarks/taches_lmeval/agentpublic_mcq/` -- YAML lm-eval (`custom_dataset`) et `utils.py` (chargeur local).
- `src/slmsp/benchmarks/moteurs/__init__.py` -- `lancer_outil` gagne `env_supplementaire`.
- `tests/benchmarks/test_lm_eval.py`, `tests/benchmarks/fixtures/` -- faux `lm_eval` et sortie JSON factice.

## Tasks & Acceptance

**Execution:**
- Moteur, tâche MCQ-eval et chargeur local, `env_supplementaire` pour la clé factice d'API locale.
- `tests/benchmarks/test_lm_eval.py` (26 tests) ; test réel marqué `gpu` + `lent`, non lancé. `test_orchestrateur.py` : le moteur « livré mais absent » devient `bfcl` (6.3), `lm_eval` existant désormais.

**Acceptance Criteria:**
- Given `base:<slug>` avec poids HF, when cible `hf`, then `--model hf` sur `hf-bf16` ou `hf`, few-shot et limite de la config (french_bench_mc 3-shot, global_mmlu_fr 2 000…).
- Given un GGUF, when ifeval, then `local-chat-completions` vers `127.0.0.1`, avant et après quantification.
- Given la sortie JSON, then métrique, valeur, erreur standard, version de lm-eval et nombre d'items par tâche (`<tache>.<métrique>`, `_stderr`, `n_items`).
- Given MCQ-eval, then le YAML lit le dossier local (`SLMSP_MCQ_EVAL_DIR`), sans `dataset_path` Hub.
- Given un GGUF seul, then QCM sautés avec motif.

## Verification

**Commands:**
- `uv run pytest -q --tb=short tests/benchmarks` -- expected: tout passe
- Plus tard, avec l'extra `bench` et le GPU : `uv run --extra bench slmsp bench run --modele base:<slug> --socle`.

## Auto Run Result

**Statut :** review.

**Décisions prises seul (solution la plus simple et la plus réversible).**
- Un `ResultatBench` par benchmark (un benchmark = une tâche lm-eval) ; les scores sont `<tache>.<métrique>`, `<tache>.<métrique>_stderr`, `<tache>.n_items`, et `details.taches` détaille groupes et sous-tâches. Filtre `none` omis du nom.
- Version de lm-eval : `lm_eval_version` de la sortie, sinon `importlib.metadata` (sans import).
- Base × `avant` en ifeval : aucun GGUF F16 de base n'existe (`evaluation.modele_ref`, que `benchmarks` ne peut importer (même couche) : `resoudre_gguf` refait la résolution) : le benchmark est sauté avec motif. À confirmer par Anaël (préparer un F16, ou accepter q4_k_m seul pour ifeval de base).
- Modèles `ft:` pour les QCM HF : sautés (poids fusionnés non définis). À confirmer par Anaël.
- Commande remplaçable par `SLMSP_LM_EVAL_CMD` ; défaut `python -m lm_eval` ; sortie cherchée par `results*.json` sous le dossier du run (`lm_eval/<benchmark>--<variante>/`).
- `lancer_outil` (6.1) étendu par `env_supplementaire` (clé factice `OPENAI_API_KEY`, qu'exige `local-chat-completions`).

**Reports.** Voir `deferred` (schéma MCQ-eval, dépendances ifeval). Run réel non lancé.

## Revue

- medium, corrigé : `options.base_url` acceptait n'importe quel hôte, contre l'exigence `127.0.0.1` (AC 2) ; refusé hors `127.0.0.1`, `localhost`, `::1` (motif de saut), test ajouté.
- low, corrigé : `analyser` levait `AttributeError` sur une sortie JSON non standard (racine non objet, `n-samples` ou `versions` non objets, section de tâche non objet) ; tolérés ou `LmEvalEchoue`, test ajouté.
- low, rejeté : pas de délai maximal pour `lm_eval` ; les runs GPU sont longs et le délai relève de l'orchestrateur.
- low, rejeté : `shlex.split(posix=False)` conserve les guillemets sous Windows ; `SLMSP_LM_EVAL_CMD` est un levier de test.
- RAS : QCM hf avant seulement (`BenchmarkConfig` impose `avant`), `env_outil()` avec les deux `HF_*_OFFLINE=1`, verrou GPU à l'orchestrateur, aucun `import lm_eval`, `benchmarks` n'importe ni `evaluation` ni `train`.
- medium, corrigé en partie (second avis 1) : les benchmarks lm-eval du socle n'ont pas de `[[jeux]]` ; l'épinglage (révision, SHA-256) exige un vrai fetch, interdit à la revue. Les en-têtes des TOML disent désormais que le jeu n'est pas épinglé et que lm_eval lit le cache HF local ; l'échec hors ligne ajoute ce rappel au motif. Reste à épingler au premier fetch réel (Anaël).
- medium, corrigé (2) : `langdetect`, `immutabledict` et `nltk` (3.10.3, version déjà verrouillée) ajoutés à l'extra `bench`, `uv.lock` mis à jour. Reste : les données nltk (`punkt_tab`) d'ifeval, à placer dans le cache avant le run hors ligne.
- medium, corrigé (3) : `--seed` explicite (`options.seed`, 1234 par défaut), `options.batch_size` (auto par défaut) ; `seed` et `batch_size` consignés dans `ResultatBench.configuration` ; `jeu_version` = `lm-eval <tâche>@v<version>` quand aucun jeu n'est épinglé. Test ajouté.
- low, rejeté (4) : couverture déplacée vers tests/fetch/test_benchmarks.py.
- low, corrigé (5) : `fetch/benchmarks.executer` consigne chaque fichier dès son téléchargement ; un refus en accès conditionnel ne perd plus les lignes déjà obtenues.
