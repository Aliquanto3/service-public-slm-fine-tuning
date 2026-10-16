---
title: "Story 9.5 — Étapes `validate` et `filter`"
type: 'feature'
created: '2026-10-16'
status: review
baseline_revision: 'a02a17f'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-9-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-4-etape-generate-generation-idempotente-et-traces-d-outils.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** le pipeline `seed → generate → validate → filter → build` n'avait ni validation des exemples contre leurs sources et le Bac à sable, ni filtre des doublons et des fuites du Jeu d'évaluation. Rien ne mesurait donc le taux de rejet par motif et par Tâche (FR-30).

**Approach:** `slmsp.data.validate` et `slmsp.data.filter` lisent les réponses déjà journalisées (`core.artefacts.lire`, journal Mistral en lecteur `data`) et produisent deux runs immuables, sans appel d'API par défaut. `slmsp data validate --depuis <generate>` puis `slmsp data filter --depuis <validate>`.

## Boundaries & Constraints

**Always:**
- D1.1 : aucun texte n'est écrit. Les rejets (`rejets.jsonl`, `RejetExemple`) ne portent que des identifiants, un motif et des comptes. Les lignes conservées sont les `SessionBrute` de 9.4, inchangées.
- Verrou 6 : le seul contrôle de fidélité optionnel est `ControleMistral` (`usage = validation`, gabarit `validation`). Aucun verdict Claude, aucun import de `judge`.
- AD-24 : toutes les lectures passent par `core.artefacts.lire` ou `Run.lire_jsonl`. Le Jeu d'évaluation n'est vu qu'à travers `core.items` (empreintes, vecteurs, identifiants).
- AD-26 : un run par invocation, `rapport.json` écrit une fois, les autres fichiers en ajout seul.

**Never:** aucun appel d'API par défaut. Aucune modification de `generate`, des gabarits, du schéma du journal ni de `config/donnees.toml`.

## I/O & Edge-Case Matrix

| Scénario | Comportement | Motif |
|---|---|---|
| RD : un résultat d'outil ou une cassette diffère du rejeu, cassette illisible, appel sans équivalent exact enregistré | rejet | `trace_divergente` |
| RD : appel hors schéma `outils-mcp.toml` | rejet | `appel_non_conforme` |
| URL de la réponse absente des passages (Q), résultats d'outils (RD) et textes d'amorce | rejet | `url_inventee` |
| Q, RD, CR, LC, RE : nombre notable (hors entiers 0 à 9, URL retirées, valeur absolue) absent des sources | rejet | `valeur_absente` |
| CR, LC, RE avec `--controle-mistral` : verdict `INFIDELE` ou illisible | rejet | `infidele` |
| Réponse ou entrée recoupant un item du jeu (v1.0, v1.1, calibrage) au-delà de `anti_fuite.seuil_jaccard` | rejet | `fuite_ngram` |
| Cosinus BGE-M3 avec un vecteur d'item au-delà de `anti_fuite.seuil_cosinus` | rejet | `fuite_cosinus` |
| Texte (entrée + réponse) identique à un exemple retenu, ou Jaccard au-delà de `deduplication.seuil_jaccard` dans la même Tâche | rejet du suivant | `doublon` |
| `BudgetEpuise` pendant le contrôle de fidélité | run `partiel-budget`, code 3 | — |
| Run parent d'un autre type, en cours, sans `brut.jsonl` | rien n'est écrit | `ManifesteInvalide`, 4 |
| Appel ou amorce introuvable au journal ou au seed | exception, run `partiel-erreur` | `ProvenanceInvalide`, 4 |

</intent-contract>

## Code Map

- `src/slmsp/data/validate.py` : `LecteurGeneration` (amorces du seed et dérivées, plan, journal), rejeu sur `BacASable`, contrôles URL et valeurs (`harness.citations`, `core.texte.extraire_nombres`), `ControleMistral`, `lancer_validation`, `taux_par_tache`.
- `src/slmsp/data/filter.py` : `lancer_filtre` (réutilise `seed.Protection` et le vecteur d'items de `core.items.vecteurs_antifuite`).
- `src/slmsp/core/schemas/rejet_donnees.py` : `RejetExemple`, motifs.
- `src/slmsp/cli/data.py` : sous-commandes `validate` (`--depuis`, `--racine`, `--controle-mistral`) et `filter` (`--depuis`, `--racine`) ; il imprime exemples et taux de rejet par Tâche et par motif.
- Tests : `tests/data/test_validate.py`, `tests/data/test_filter.py` ; `tests/cli/test_data.py` ajusté (`build` reste « non implémentée »).

## Design Notes

- **Rapport (FR-30)** : `rapport.json` donne, par Tâche et au total, `exemples`, `retenus`, `rejets` par motif et `taux_rejet`. Le `filter` compte à partir des `valides` de `validate` : les deux taux ne s'additionnent pas.
- **Sources par Tâche** : Q = passages du plan ; RD = messages `tool` des requêtes journalisées (rejoués et vérifiés) ; CR = transcription (premier appel) et scénario ; LC, RE, CT, CO, générique = textes d'amorce. L'URL est contrôlée pour toutes les Tâches, les valeurs seulement pour Q, RD, CR, LC et RE.
- **Rejeu RD** : chaque `tool_call` des réponses journalisées est rejoué sur `BacASable` avec les cassettes de la session ; le contenu comparé est celui du message `tool` de la requête suivante (formes admises par le Générateur). Toute réponse « appel non prévu » du Bac à sable est une divergence.
- **Idempotence du contrôle Mistral** : avant tout appel, une ligne `validation`/`ok` de même session et de mêmes messages est relue au journal, jamais repayée.
- **Filtre** : ordre `fuite_ngram`, `fuite_cosinus`, `doublon` ; le premier exemple d'un groupe de doublons est gardé.

## Verification

- `uv run pytest -q --tb=short tests/data/test_validate.py tests/data/test_filter.py tests/cli/test_data.py` : voir `## Auto Run Result`.
- Suite complète, `ruff check`, `ruff format --check` et `outils/controle_rapide.py` : voir `## Auto Run Result`.

## Auto Run Result

**Statut :** done, en revue.

**Décisions prises seul** (« la plus simple et la plus réversible ») :
1. **Anti-fuite par inclusion** : `fuite_ngram` réutilise `seed.Protection.recouvrement` (`|A ∩ B| / min(|A|, |B|)`, seuil `anti_fuite.seuil_jaccard`), comme `seed`, plutôt qu'un Jaccard strict qui manque un item repris dans un texte plus long. La clé de configuration garde son nom.
2. **Texte comparé** : la réponse finale et l'entrée (textes d'amorce du seed) sont chacune comparées aux items ; le doublon porte sur `entrée + réponse`.
3. **Entiers de 0 à 9 ignorés** par `valeur_absente` (numérotation, petits comptes). Les URL sont retirées de la réponse avant l'extraction des nombres.
4. **Fidélité Mistral opt-in** (`--controle-mistral`, off par défaut) : la règle automatique (URL et valeurs) suffit pour l'AC 3 sans dépense. Un verdict illisible vaut `infidele`.
5. `validate` accepte un run `generate` `partiel-*` (il juge les sessions de `brut.jsonl`) ; `filter` n'accepte pas un run `validate` en cours. Pas de reprise de run pour ces deux étapes : elles sont déterministes et gratuites (contrôle Mistral relu au journal).
6. `ControleMistral` s'appuie sur `valider_gabarit` directement (le Générateur refuse la Tâche `validation`) et sur `ClientMistral.appeler("validation", …)`.
7. `validate` importe `mistral.generateur._textes_resultat` (formes admises du contenu d'un message `tool`) plutôt que de la dupliquer.

**À confirmer par Anaël :**
- Inclusion plutôt que Jaccard pour `fuite_ngram` (décision 1) et seuils de `config/donnees.toml` (0,5, 0,9, 0,8) à calibrer sur le jeu réel.
- Le motif `infidele` s'ajoute aux quatre motifs de l'epic ; les entiers de 0 à 9 sont exemptés.
- CT, CO et générique n'ont pas de contrôle de valeurs ni de fidélité (aucune source de référence).

**Reports (hors périmètre) :**
- La voie réelle de la CLI (BGE-M3 pour `filter`, Mistral pour `--controle-mistral`) n'est couverte par aucun test. Commandes à lancer en 9.8 : `uv run slmsp data validate --depuis <generate_run_id>` puis `uv run slmsp data filter --depuis <validate_run_id>`.
- `build` (9.6) doit lire `retenus.jsonl` de `data-filter`.

## Revue

Revue Opus du 2026-10-16, avec la liste du second avis (Haiku). D1 : aucun texte rédigé par Claude dans le code, les gabarits ou les fixtures (réponses `<…-factice-…>`, jetons artificiels).

- medium, corrigé : `filter` (et `validate`) écrivaient `complet` sur un parent `partiel-*`. `statut_herite` propage le statut partiel du parent (`interrompu` donne `partiel-erreur`), motif « run parent … » ; tests `test_validate_partiel_rend_filter_partiel`, `test_statut_herite_du_parent`.
- medium, corrigé (documentation) : `anti_fuite.seuil_jaccard` est un seuil de coefficient d'inclusion, pas de Jaccard. Commentaire ajouté dans `config/donnees.toml` ; seuil inchangé (sur-rejet des textes courts = côté prudent). Clé non renommée (partagée avec `seed`).
- medium, corrigé : CT et CO entrent dans `TACHES_A_VALEURS` (le gabarit CT interdit toute date ou montant inventé ; CO garde dates et montants). CO : toute valeur notable du texte de départ absente de la sortie donne `infidele` (règle automatique, AC 3). `generique` reste sans contrôle de valeurs (aucune source de référence). Tests `test_co_garde_les_valeurs_de_la_source`, `test_ct_valeur_inventee`.
- low, corrigé : `rapport.json` de `validate` porte `non_jugees` (sessions non jugées après `BudgetEpuise`).
- low, rejeté : `appel_ids[-1]` sur une session sans appel est impossible, `SessionBrute.appel_ids` impose `min_length=1`.
- low, corrigé : docstrings « sans rien écrire » de `lancer_validation` et `lancer_filtre` rectifiées (appel ou amorce introuvable : run créé puis clos `partiel-erreur`).

Suite complète : 3 échecs hors périmètre, déjà présents sans les correctifs (`anthropic` absent de l'environnement du worktree pour `test_notation`, contention du registre SQLite pour `test_concurrence`).

**Points à confirmer par Anaël :**
- Calibration de `anti_fuite.seuil_jaccard` (inclusion, 0,5) sur le jeu réel, et renommage éventuel de la clé (touche `seed`).
- CT et CO soumis à `valeur_absente` ; CO rejeté en `infidele` s'il perd une valeur ; `generique` sans contrôle.
- Un run enfant hérite du statut partiel de son parent (le code de sortie suit : 3 pour `partiel-budget`).
