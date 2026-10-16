---
title: 'Story 11.1 — Squelette du Comparatif (slmsp compare comparatif)'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred: []
---

## Intent

**Problem:** aucun rapport ne rassemble Baseline, entraînements, export, benchmarks et coûts pour présenter à un client le gain et le coût de chaque méthode (FR-36, SM-1, SM-6), y compris en cas de no-go.

**Approach:** `slmsp.compare` est une fonction pure des artefacts de `runs/` (AD-20) : `chargement.py` lit les runs par les schémas d'AD-25 (et des modèles tolérants pour `couts.json` / `metriques.jsonl`), `comparatif.py` rend un Markdown déterministe. Toute valeur absente s'affiche « non mesuré » ; une vue sans évaluation intermédiaire s'affiche « à compléter ».

## Boundaries & Constraints

**Always:** aucun chiffre inventé ; runs non `complet` exclus et listés ; une seule version du jeu (refus sinon, ou `--jeu`) ; rendu sans horodatage ni identifiant du run de sortie (octet-identique) ; seuils SM-1 lus dans `config/comparatif.toml` (AD-22).

**Never:** import de `inference`, `judge`, `mistral`, `net` ; appel modèle ou réseau ; décision go/no-go (le rapport recommande, Anaël décide).

## Conventions d'artefacts

- Run `train` (réel, story 10.4) : `config.campagne`, méthode dans `config.toml.methode`, `couts.json` / `couts-N.json` (`ecrire_mesures`, story 10.3). Testé sur un Run produit par `train.run.executer` (`tests/train/test_lecture_comparatif.py`).
- Évaluations intermédiaires (vues FR-34) : 10.4 n'en écrit pas. Convention supposée, **à confirmer** : lignes `{"evenement": "evaluation", "tokens_vus", "duree_s", "scores": {tache: score}}` dans `metriques.jsonl`. Tant qu'elles manquent, les vues affichent « à compléter ».
- Run `export` (10.6, pas encore codé) : convention supposée, **à confirmer** : `runs/export/<id>/run.json`, `parents` = run d'entraînement ; un `ft:<X>` se résout si X est le run `train` ou son export.
- Scores (`Scores`) et Benchmarks (`ResultatBench`) lus par les schémas de `core/schemas`. Une Baseline est une configuration (modèle, quantification) ; par Tâche, la notation la plus récente. Métrique d'un Benchmark : `[benchmarks.<nom>]` de `config/comparatif.toml` (clé, échelle, sens), sinon « non comparable ». Verdict SM-1 sur q4_k_m si présent, sinon f16.

## Code Map

- `src/slmsp/compare/chargement.py` -- chargement des runs `eval-notation`, `bench`, `train`, `export` ; sélection (statut, notation la plus récente, version du jeu).
- `src/slmsp/compare/comparatif.py` -- configuration, calculs (gains, vues, SM-1) et rendu Markdown.
- `src/slmsp/cli/compare.py` -- `compare comparatif --campagne <id> [--racine] [--jeu]`.
- `config/comparatif.toml` -- seuils SM-1 et Tâches prioritaires.
- `tests/compare/` -- fixtures synthétiques, instantané, octet-identité, imports.

## Auto Run Result

- `chargement.py` et `cli/compare.py` créés ici (8.3/8.4 sont des stories d'exécution, sans code dans `compare/`).
- Formats `train` alignés sur le code fusionné de 10.4 (rebase sur main) ; seuls les évaluations intermédiaires et le run `export` restent en convention.
- Échelle des Benchmarks : points tels qu'archivés, sans conversion.
- Aucune donnée réelle : tests sur runs factices.

## Revue

Revue du 2026-10-16 (Opus, avec la liste du second avis Haiku). Corrections dans `chargement.py`, `comparatif.py`, `config/comparatif.toml`, tests.

- high, corrigé : meilleure Baseline no-go calculée sur les seules Tâches prioritaires mesurées (une Baseline notée sur Q seul battait une Baseline complète). Seules les Baselines notées sur toutes les Tâches prioritaires sont éligibles, sinon « indéterminée ».
- high, corrigé : `_fusionner_baseline` prenait le maximum par Tâche toutes quantifications et toutes notations confondues (Baseline composite, f16 non livrable, sélection du meilleur essai). Une Baseline est désormais la configuration (modèle, quantification), affichée ; par Tâche, la mesure la plus récente ; seule une Baseline `q4_k_m` est candidate au no-go.
- high, corrigé : la métrique d'un Benchmark était la première clé non nulle par ordre alphabétique. Avec les moteurs réels, c'était souvent `n_items` (bfcl) ou une fraction 0-1 comparée à des seuils en points. Métrique, échelle et sens désormais explicites par Benchmark (`[benchmarks.<nom>]`), même clé des deux côtés ; sans cela « non comparable » et SM-1 indéterminé.
- medium, corrigé : le chemin no-go était annoncé alors que SM-1 restait indéterminé pour une méthode. Il est désormais « Recommandation suspendue », avec la Baseline comme simple repli ; le no-go n'est annoncé que si toutes les méthodes sont non satisfaites (ou absentes).
- medium, corrigé : la phrase « le plafond de 5 Go est vérifié dans le rapport de Baseline » n'était fondée sur aucune donnée lue. Elle devient « Plafond de RAM de 5 Go (cible 4 Go, NFR-1) : non vérifié par ce rapport ».
- low, corrigé : les résultats de Benchmark invalides ou en échec et les notations `ft:` sans quantification étaient ignorés sans apparaître dans « Runs exclus ». Ils y figurent désormais.
- low, corrigé : `_point` prenait le dernier point par `tokens_vus`, même pour la vue en durée. Il prend maintenant le maximum sur la clé de la vue.
- low, corrigé : le `jeu_statut` des notations n'apparaissait pas dans le rapport. Il est maintenant rapporté dans « Méthode et limites ».
- low, rejeté (consigne) : le test d'imports est statique (AST) et ne voit pas `importlib`, ce qui reste acceptable pour AC-6. L'instantané est produit par le code lui-même : il fige le rendu, mais ne prouve pas sa justesse. Les assertions ciblées des autres tests compensent.
- D1 : aucune donnée d'entraînement ni amorce rédigée par Claude ; les fixtures sont des chiffres factices.

**À confirmer par Anaël :**
- la règle d'éligibilité de la Baseline no-go (`q4_k_m` et couverture complète des Tâches prioritaires) ;
- les métriques des Benchmarks réels à renseigner dans `config/comparatif.toml` (clé exacte, `echelle = 100` pour les fractions, `sens = "bas"` pour crows_pairs par exemple). Tant qu'elles ne sont pas renseignées, SM-1 reste indéterminé ;
- le traitement « aucun Run d'entraînement » comme no-go (actuellement no-go) ;
- la convention des évaluations intermédiaires (`metriques.jsonl`) et du run `export`.
