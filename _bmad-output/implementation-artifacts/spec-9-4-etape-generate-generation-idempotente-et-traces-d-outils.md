---
title: "Story 9.4 — Étape `generate` : génération idempotente et traces d'outils"
type: 'feature'
created: '2026-10-13'
status: review
baseline_revision: 'f556fab'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-9-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/brouillon-spec-9-4-generate.md'
warnings: ['oversized', 'hors-zone-declare']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Le pipeline `seed → generate → validate → filter → build` n'avait pas d'étape `generate`. Le Générateur de 9.2 ne savait ni envoyer `tools` aux traces RD, ni remplir l'emplacement `passages` de `traces-q`, ni enchaîner les deux appels du CR, ni relire plusieurs cassettes par session.

**Approach:** extensions minimales du Générateur, sans paramètre de texte libre et sans changer la signature de `generer` (verrou 3). Puis `slmsp.data.generate` (pré-vol, plan à `session_id` déterministe, exécution dans l'ordre d'AD-5, bilan) et `slmsp.data.sessions` (un appel, Q, CR en deux temps, tours d'outils RD). Avant chaque appel, on cherche une réponse déjà journalisée pour ne jamais repayer un appel. `slmsp data generate --depuis | --reprendre` expose le tout.

## Boundaries & Constraints

**Always:**
- D1.1 : le seul générateur est `Generateur.generer`. Les fixtures sont des jetons aléatoires `<…-factice-xxxx>` produits par le test.
- Verrou 3 : `generer(gabarit_id, amorce_ids, session_id, tache, messages_precedents)` reste inchangé. Les passages viennent de `rendre_passages(session_id)`, injecté à la construction et rempli depuis le plan. Les outils sont lus par le Générateur dans `config/outils-mcp.toml`. Une amorce dérivée provient d'un `appel_id` admis au journal.
- AD-1 : `data` n'importe pas `evaluation` (le gel est contrôlé par la CLI) et `mistral` n'importe pas `mcp`.
- AD-24 : les lectures passent par `core.artefacts.lire`. Le journal est ouvert avec `lecteur="data"`. Le Jeu d'évaluation n'est vu qu'à travers `IdentifiantsProteges`.
- AD-26 : `plan.jsonl` est écrit une seule fois, les autres fichiers en ajout seul. Les cassettes passent par `mcp.enregistrer(…, "data")`, sans écrasement.

**Never:** aucun appel réel (Mistral, MCP, BGE-M3) dans les tests. Aucune logique de `validate`, `filter` ou `build`. Aucune modification du schéma du journal, de `harness/`, `index/`, `mcp/`, `core/gabarits.py`, `config/donnees.toml`, ni des gabarits. Aucune relance automatique d'un appel en erreur.

## I/O & Edge-Case Matrix

| Scenario | Comportement | Statut / code |
|---|---|---|
| Tâche à un appel (LC, CO, RE, CT, generique) | 1 appel, 1 ligne `brut.jsonl` (`cassettes=[]`) | — |
| Q | passages cherchés au plan, URL protégées retirées et comptées, rendu `formater_passages` (`AUCUN_PASSAGE` si vide) | — |
| CR | `transcription-cr`, puis amorce dérivée `<sid>.transcription` (une fois dans `amorces-derivees.jsonl`), puis `cr` | — |
| RD, plusieurs tours | tous les appels validés avant envoi, puis une connexion MCP par session et un segment de cassette `data/cassettes/<sid>.t<k>.json` par tour | — |
| RD, refus avant envoi | outil inconnu, arguments hors schéma ou JSON illisible donnent `appel_non_conforme` ; un identifiant protégé en argument donne `fuite_identifiant` | abandon |
| RD, autres fins | `tours_max`, `sans_appel_outil`, `erreur_outil` (après l'écriture de la cassette), `cassette_incoherente` | abandon |
| Réponse tronquée, ou contenu absent | `reponse_tronquee`, `sans_contenu` | abandon |
| Amorce corrompue | `provenance_invalide`, puis la session suivante | abandon |
| Panne de transport MCP | ligne `incidents.jsonl`, session réessayée à la reprise | `partiel-erreur`, 1 |
| Appel déjà journalisé (nouveau run ou reprise) | 0 requête, 0 réservation, `appels_reutilises` incrémenté | — |
| `BudgetEpuise` | arrêt propre, aucune session suivante | `partiel-budget`, 3 |
| `ErreurApiMistral`, `ModeleMistralRefuse`, jour changé | arrêt immédiat | `partiel-erreur`, 1 |
| Ctrl+C | `interrompu`, puis exception relevée | 1 |
| Gel v1.0 absent ou non ancêtre | aucun run, aucun journal, aucune requête | 4 |
| Conditions Mistral non vérifiées du jour | rien n'est écrit | 1 |
| Seed absent, d'un autre type ou non `complet` ; reprise avec un SHA changé (amorces, gabarit, outils) | rien n'est écrit | `ManifesteInvalide`, 4 |
| `--reprendre` d'un run `complet` | rien n'est écrit | 1 |

</intent-contract>

## Code Map

- `src/slmsp/mistral/generateur.py` : `TACHES_OUTILLEES`, `outils()`, `gabarit()`, `rendre_passages`, `deriver_amorce`, `_cassettes` (`<sid>.json` puis `.t1`, `.t2`…), forme `"\n".join` admise pour le résultat d'un outil, `raison_de_fin`.
- `src/slmsp/mistral/client.py` : `_appeler(…, tools=, tool_choice=)`.
- `src/slmsp/core/schemas/session_donnees.py` : `RefGabarit`, `PassagePlan`, `SessionPlanifiee`, `SessionBrute`, `AbandonSession`, `IncidentSession`.
- `src/slmsp/data/sessions.py` : `ExecuteurSessions`, `ResolveurPassages`, `SessionOutils`, recherche d'appel réutilisable par projection des messages.
- `src/slmsp/data/generate.py` : `ORDRE_TACHES`, `CHAINES`, `planifier`, `lancer_generation`, `seed_du_run`.
- `src/slmsp/cli/data.py` : sous-commande `generate`, recherche paresseuse dans l'Index (BGE-M3 et `ouvrir_index`) et `McpEnDirect("outillage")`.

## Tasks & Acceptance

**Execution :** tâches faites (voir Code Map). Tests : `tests/data/{conftest,test_sessions,test_generate,test_prealables}.py`. Les tests mis à jour sont `tests/mistral/test_generateur.py` (fixture `fichier_outils` et dix tests des extensions) et `tests/cli/test_data.py` (`generate` est implémentée).

**Acceptance Criteria :**
- Given un gel v1.0 absent ou dont le commit n'est pas un ancêtre de `HEAD`, when on lance `slmsp data generate --depuis <seed>`, then la commande sort en 4, sans run, sans journal et sans requête (`test_prealables.py`).
- Given des appels déjà journalisés, when on relance sur un nouveau run ou en reprise, then aucune requête n'est faite et aucune réservation n'est prise (`test_nouveau_run_sur_le_meme_seed_ne_paie_rien`, reprises).
- Given une trace RD, when Mistral émet des `tool_calls`, then ils sont validés, exécutés et enregistrés par tour, puis renvoyés en messages `assistant` et `tool` que le Générateur revérifie. Chaque requête RD porte `tools` et `tool_choice: "auto"`.
- Given toutes les Tâches, when le plan s'exécute, then les requêtes suivent l'ordre Q, RD, CR, LC, generique, CT, RE, CO. `BudgetEpuise` donne `partiel-budget`.
- Given une session close, when on reprend le run, then elle est inscrite dans `brut.jsonl` ou `abandons.jsonl` et `--reprendre` ne la rejoue pas.
- Given le code de la story, when on lance `test_architecture.py` et la signature de `Generateur.generer` (test de 9.2), then rien ne change.

## Design Notes

- **`session_id`** vaut `<tâche>-<24 hex>`, calculés sur le JSON canonique de la Tâche, des gabarits (id, version, SHA), des amorces (id, `sha_texte`), du SHA des passages rendus (Q) et de `tools_list_sha256` (RD). Un Index différent donne donc une autre session.
- **Réutilisation d'un appel.** La première ligne `generation`/`ok` de la session qui remplit toutes ces conditions est réutilisée :
  - modèle stable ;
  - gabarit identique (id, version et SHA) ;
  - mêmes `amorce_ids` ;
  - même nombre de messages ;
  - même projection des messages précédents (`content`, ainsi que l'id, le nom et les arguments décodés des appels ; pour un `tool`, `tool_call_id` et `content`).
- **Regroupement des amorces.** Pour un gabarit à un seul emplacement (hors `passages`), on fait une session par amorce. Sinon, on regroupe les amorces de même origine (`jeu`, `revision`, `ligne` ou `appel_id`), avec exactement un emplacement chacune. Le reste est compté dans `amorces_incompletes` ou `amorces_ignorees`. On garde au plus `ceil(volume × (1 + surplus))` groupes, triés par `amorce_id`, et l'écart va dans `deficit`.
- **Le CR a deux appels.** `brut.appel_ids` vaut `[transcription, cr]` : le dernier appel donne la réponse finale. 9.6 doit le savoir.

## Verification

- `uv run pytest -q --tb=short tests/data tests/mistral tests/cli tests/test_architecture.py tests/test_cli.py` : 570 passés, 7 ignorés.
- `uv run ruff check` et `uv run ruff format --check` : propres. `outils/controle_rapide.py` : OK.
- `uv run pytest -q --tb=line -p no:warnings` : 3480 passés, 343 ignorés, 1 échec préexistant hors zone (`tests/evaluation/test_notation.py::test_ouvrir_juges_surcharge_le_mode`, extra `judge`/`anthropic` non installé).
- Avec seulement `uv sync`, les tests Mistral sont ignorés. Pour les jouer, il faut l'extra `data` (`uv sync --extra data`).

## Auto Run Result

**Statut :** done, en revue.

**Décisions prises seul** (« la plus simple et la plus réversible ») :
1. La signature de `generer` est inchangée (remarque du juge). Les passages Q passent par `rendre_passages(session_id)`, injecté à la construction. L'emplacement `passages` est réservé : une amorce qui le vise est refusée.
2. Les outils sont envoyés **par Tâche** (`TACHES_OUTILLEES = {"RD"}`) et non par une clé de front-matter : `traces-rd.md` n'est pas modifié, ce qui évite la question de version soulevée par le juge. La projection `[[outils]]` → `tools` est dupliquée dans `mistral`, qui ne peut pas importer `mcp`. Un test vérifie l'égalité avec `charger_outils()`.
3. Pas de table `[generation]` : `config/donnees.toml` et `data/config.py` restent intacts.
   - `--surplus` est une option de la CLI, à **0** par défaut. Le plan reste ainsi aligné sur les volumes (remarque du juge).
   - `TOURS_OUTILS_MAX` vaut 4.
   - Les versions anti-fuite viennent de `seed.versions_protegees`.
4. Une connexion MCP par session et un segment de cassette par tour (`<sid>.t<k>.json`, remarque du juge). Un tour dont la cassette existe est relu, jamais rejoué.
5. Le Générateur admet aussi `"\n".join` pour le résultat d'un outil, la forme de `contenu_resultat` (écart relevé par le juge).
6. Ajout du motif `sans_contenu` : une réponse non RD sans contenu texte est abandonnée. Une RD sans aucun appel d'outil donne l'abandon `sans_appel_outil`.
7. Anti-fuite dès `generate` :
   - toute chaîne des arguments d'outil est comparée aux `dataset_ids` et `resource_ids` protégés ;
   - les URL des passages sont comparées aux URL protégées, avec la normalisation `_url_canonique` du seed.
8. Le gel exigé est celui de `v1.0` (AC1 de l'epic) ; `partiel-budget` sort en code 3.
9. À la reprise, les SHA des entrées sont recalculés par `core.canonique.sha256_fichier`, comme le fait `nouveau_run`. C'est un hachage, pas une lecture de contenu par `data`.
10. `--reprendre` reprend le plan, `tours_outils_max` et `index_version` de la création. `--surplus` n'y a pas d'effet.

**À confirmer par Anaël :**
- La valeur de `--surplus` pour 9.8. À 0, les rejets de `validate` et `filter` feront passer les volumes sous la cible.
- CT et RE n'ont toujours aucune source d'amorce complète (report de 9.3). Leur `deficit` sera égal à la cible tant que `seed` ne les fournit pas.
- `HoteBloque` levée par le transport Mistral : arrêt en `partiel-erreur`. La même erreur levée côté MCP donne un incident.
- Un résultat MCP avec un élément non texte : le Générateur refuse le rendu de `contenu_resultat` et la session est abandonnée en `provenance_invalide`. Ce cas est rare, mais il faudra trancher (adapter le générateur ou la règle) si 9.8 le rencontre.

**Reports (hors périmètre) :**
- La voie réelle de la CLI n'est couverte par aucun test (BGE-M3, Index et `McpEnDirect` en direct). Commande à lancer en 9.8, après la relecture des conditions Mistral du jour : `uv run slmsp data generate --depuis <seed_run_id>`, puis `--reprendre <run_id>` en cas d'arrêt.
- Un seul écrivain par run : deux `--reprendre` simultanés ne sont pas pris en charge.

## Revue

Revue Opus du 2026-10-16, sur la liste du second avis (Haiku). D1 : aucun texte rédigé par Claude dans le code, les gabarits ou les fixtures (jetons `<…-factice-xxxx>`).

- medium, corrigé : reprise d'un run arrêté entre `nouveau_run` et l'écriture de `plan.jsonl` (ou plan tronqué). Le plan relu était vide, et le run passait `complet` avec zéro session. Désormais, `_plan_du_run` vérifie, avant toute écriture, la présence du plan, sa conformité et son nombre de sessions par rapport à `comptes_plan`. Sinon : `ManifesteInvalide`. Test : `test_reprise_sans_plan_refusee`. (Point 6 du second avis, relevé de low à medium.)
- low, corrigé : `proteges.amorces_sha256` n'était pas contrôlé à la génération. `planifier` écarte maintenant toute amorce dont `sha256(normaliser(texte))` est protégée, avant tout appel payé, et la compte dans `amorces_protegees`. C'est une défense en profondeur si les versions protégées ont changé depuis le seed. Test : `test_amorce_usager_protegee_ecartee_avant_tout_appel`. (Point 3.)
- medium, rejeté : `generer` n'a pas de paramètre `passage_ids` (point 1). La variante choisie est notée dans le brouillon (« variante plus sûre ») et dans la décision 1. Le verrou 3 tient : les passages viennent du plan, résolus par `session_id`, et aucun texte libre n'est admis. L'écart avec l'AC « signature exacte » du brouillon est à confirmer (voir plus bas).
- low, rejeté : pas de clé `outils` dans `traces-rd.md` (point 2). C'est la décision 2, prise pour ne pas toucher aux gabarits ni à leur version. Le test d'égalité avec `charger_outils()` couvre la projection.
- low, à confirmer (point 4) : les identifiants protégés ne sont cherchés que dans les arguments d'outil, pas dans les résultats MCP. Ce périmètre est conforme à la spec. Un contrôle des résultats (recherche de sous-chaîne dans les textes) pourrait abandonner beaucoup de traces RD, car les résultats de recherche citent souvent des jeux populaires. C'est une décision de politique anti-fuite.
- low, rejeté : le (`tours_outils_max`+1)-ième appel (point 5) est nécessaire pour obtenir la réponse finale après le dernier tour admis. Il n'est perdu que si Mistral demande encore un outil. Variante possible : `tool_choice: "none"` sur ce dernier appel (à confirmer).
- low, rejeté : `sha256_fichier` sans garde (point 7). Ce cas est inaccessible : seed absent, gabarit absent ou `outils-mcp.toml` absent sont refusés avant, par la construction du Générateur (`ProvenanceInvalide`), par `_gabarits` (`GabaritInvalide`) ou par `charger_config`.
- low, rejeté : `etat.jsonl` contre `bilan.jsonl` (point 8). Le statut `partiel-budget` est bien inscrit dans `etat.jsonl` par `run.terminer`, et `bilan.jsonl` s'y ajoute. L'AC4 est tenu.

**À confirmer par Anaël (en plus de la liste de l'Auto Run Result) :**
- Signature de `generer` sans `passage_ids` : faut-il accepter l'écart avec l'AC du brouillon ?
- Anti-fuite sur les résultats d'outils RD (abandon, ou laisser la question à `filter`).
- `tool_choice: "none"` sur le dernier appel admis d'une trace RD.
