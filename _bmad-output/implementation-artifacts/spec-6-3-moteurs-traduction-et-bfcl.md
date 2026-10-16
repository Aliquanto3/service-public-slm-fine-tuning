---
title: 'Story 6.3 — Moteurs de traduction (sacrebleu) et BFCL (vérificateur isolé)'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred:
  - summary: >-
      Les formats de fichiers des jeux WMT14, FLORES-200 et BFCL (noms, colonnes) ne sont pas connus : rien n'est téléchargé. Le moteur lit des JSONL normalisés (`<paire>.jsonl` source/reference ; `<cat>.jsonl` et `reponses/<cat>.jsonl` au format BFCL), à confirmer et à produire au premier `fetch benchmarks`.
    evidence: config/benchmarks/traduction.toml et bfcl.toml, jeux sans revision ni fichiers.
    location: src/slmsp/benchmarks/moteurs/traduction.py, bfcl.py
    severity: medium
  - summary: >-
      Signature de `ast_checker` de bfcl-eval 2026.3.23 écrite de mémoire (jamais exécutée) ; `envs/bfcl/uv.lock` absent (réseau requis au premier `uv run`).
    evidence: envs/bfcl/verifier.py `controle_ast`.
    location: envs/bfcl/verifier.py
    severity: medium
---

<intent-contract>

## Intent

**Problem:** FR-18 (traduction) et le tool calling comparable avant/après quantification n'ont pas de moteur : le registre de la 6.1 nomme `traduction` et `bfcl` sans module.

**Approach:** Deux moteurs qui génèrent par `LlmPort.generer` (GGUF servi par `llama-server`, `ClientLlama`). La traduction calcule le chrF par sacrebleu ; BFCL écrit les sorties en JSON et confie la vérification AST à `envs/bfcl` en sous-processus.

## Boundaries & Constraints

**Always:** prompt de la Tâche TR via `construire_messages` ; `tools` natifs pour BFCL ; vérificateur lancé par `lancer_outil` (`env_sous_processus()`) ; `sacrebleu` et `bfcl_eval` jamais importés au chargement (import à la demande / env isolé) ; verrou GPU laissé à l'orchestrateur.

**Never:** aucun téléchargement, aucun appel réel à sacrebleu/bfcl-eval/llama-server en test, aucune donnée réaliste (fixtures factices).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Traduction | jeu épinglé + `<paire>.jsonl` | `<paire>.chrf`, `<paire>.n_items`, signature sacrebleu archivée dans `details.signatures` | — |
| FLORES conditionnel absent | jeu non épinglé ou fichier absent | paire sautée, consignée dans `details.paires_sautees` | run non échoué ; aucune paire : `saute` |
| GGUF non servable | pas de GGUF pour la variante | `saute` avec motif | — |
| BFCL | jeu épinglé | `<cat>.precision` et `<cat>.n_items` (simple, multiple, irrelevance) | catégorie inconnue : `ConfigurationInvalide` |
| Appel non conforme | `AppelNonConforme` | consigné (`non_conformes`), non compté comme appel | — |
| Vérificateur en échec | code non nul / JSON illisible | `BfclEchoue` (résultat `erreur`) | queue de stderr dans le motif |

</intent-contract>

## Code Map

- `src/slmsp/benchmarks/moteurs/llm.py` -- `llm_gguf` : `ClientLlama` du GGUF de la variante (ou `options.base_url`).
- `src/slmsp/benchmarks/moteurs/traduction.py`, `bfcl.py` -- les deux moteurs.
- `envs/bfcl/pyproject.toml`, `envs/bfcl/verifier.py` -- environnement isolé (`bfcl-eval==2026.3.23`) et vérificateur (entrée/sortie JSON).
- `config/benchmarks/traduction.toml`, `bfcl.toml` -- jeux `wmt14` et `bfcl` déclarés, non épinglés.
- `tests/benchmarks/test_traduction.py`, `test_bfcl.py` ; `test_orchestrateur.py` (moteur « absent » devient un module fantôme, `bfcl` existant désormais).

## Auto Run Result

Décisions prises seul :
- Un seul `ResultatBench` par benchmark (contrainte de l'orchestrateur 6.1) : les trois catégories BFCL sont des clés de `scores` (`simple.precision`…), pas trois résultats. À confirmer par Anaël si trois fichiers sont voulus.
- Sous-échantillon BFCL : 50 par catégorie (`options.effectif`, ou `limite`), graine 1234 ; WMT14 : 500 premières phrases. À confirmer par Anaël.
- Noms de fonctions BFCL « a.b » envoyés « a_b » à l'API puis restitués au vérificateur.
- Vérification des catégories `simple`/`multiple` par `ast_checker` de bfcl-eval ; `irrelevance` jugée sans bfcl-eval (aucun appel = correct).
- Surcharge `SLMSP_BFCL_VERIFIER_CMD` (comme `SLMSP_LM_EVAL_CMD`) pour les tests.

Mesures réelles non lancées. Commandes à lancer plus tard, après `slmsp fetch benchmarks` et `uv sync --extra bench` :
`uv run slmsp bench run --modele base:<slug> --benchmarks traduction bfcl`
(le premier `uv run --project envs/bfcl` crée l'environnement et son lock).

Tests : `tests/benchmarks` 59 passés, 1 ignoré (chrF réel si sacrebleu absent).

## Revue

- high, corrigé : `verifier.py` avalait ImportError/TypeError de bfcl_eval par item (précision 0.0 publiée). Nouvelle `ErreurEnvironnement` (import, signature vérifiée par `inspect.signature().bind`) qui traverse le `except` par item et fait échouer le vérificateur (code non nul, `BfclEchoue`). Les erreurs propres à l'item restent par item.
- medium, corrigé : réponses attendues absentes (fichier `reponses/<cat>.jsonl` ou ids manquants) pour simple/multiple : `ConfigurationInvalide` explicite côté moteur, `ErreurEnvironnement` côté vérificateur ; le test qui figeait le 0.0 est remplacé.
- medium, rejeté (écart consigné) : AC 4 « un `ResultatBench` par catégorie ». L'orchestrateur 6.1 fait un `ResultatBench` par benchmark (`SortieMoteur` unique) ; en séparer exigerait une refonte. Clés `<cat>.precision` / `<cat>.n_items` conservées ; à confirmer par Anaël.
- low, corrigé : timeout de 1800 s sur le vérificateur (`BfclEchoue`) ; `verdicts.json` supprimé avant l'appel (plus de verdicts périmés).
- low, corrigé : paires/langues invalides en `ConfigurationInvalide` (plus de KeyError) ; une paire présente dans WMT et FLORES reçoit des clés distinctes `<jeu>.<paire>`.
- low, consignés sans correctif : points 6, 7 et 9 du second avis.
