<!-- Brouillon rédigé le 2026-10-13 pendant le test comparatif des modèles (version Opus, classée première en aveugle : 8,4 sur 10). Ce n'est pas une spec active : la story 9.4 doit la reprendre dans bmad-build-auto, avec les remarques du juge en fin de fichier. -->

---
title: "Story 9.4 — Étape `generate` : génération idempotente et traces d'outils"
type: 'feature'
created: '2026-10-13'
status: 'ready-for-dev'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-9-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-2-generateur-mistral-prouve-gabarits-sans-exemple-journal-d-appels.md'
warnings: ['oversized', 'hors-zone-declare']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Le pipeline `seed → generate → validate → filter → build` n'a pas d'étape `generate`. Il faut produire, avec le seul `Generateur` Mistral (9.2), les sessions de génération de chaque Tâche (Q, RD, CR, LC, CO, RE, CT, génériques) dans l'ordre de dépense d'AD-5. Les traces RD doivent être exécutées en direct et enregistrées en cassettes. Un appel déjà journalisé ne doit jamais être repayé (D1.2, D1.3, D1.6, AD-26). Le Générateur livré par 9.2 ne sait pas encore faire quatre choses dont 9.4 a besoin : envoyer `tools` (constat différé de 9.2), remplir l'emplacement `passages` de `traces-q`, réutiliser une réponse Mistral de la session comme amorce (étape 2 du CR) et lire plusieurs cassettes par session (traces RD à plusieurs tours d'outils).

**Approach:** On étend d'abord le Générateur de façon minimale, sans aucun paramètre de texte libre (verrou 3 intact) :
- outils déclarés par le gabarit ;
- `passage_ids` résolus par un rendu injecté ;
- `deriver_amorce(appel_id, …)` ;
- cassettes `<session_id>.t<k>.json`.

On écrit ensuite `slmsp.data.generate`, qui fait le pré-vol (gel D1.3, préalables D1.2, seed, gabarits), planifie des sessions à identifiant déterministe et écrit `plan.jsonl`. Il exécute ensuite chaque session par `slmsp.data.sessions`, après avoir cherché dans le journal Mistral une réponse réutilisable avant tout appel, et écrit une ligne par session dans `brut.jsonl`. `slmsp data generate --depuis <seed_run> | --reprendre <run_id>` assemble le tout.

## Boundaries & Constraints

**Always:**
- **D1.1 absolue.** Aucun texte rédigé dans le code, les tests ou les fixtures. Les réponses Mistral factices, les résultats d'outils, les amorces et les passages de test sont des chaînes aléatoires produites dans `tmp_path`, par exemple `"<faux-" + secrets.token_hex(6) + ">"`. Le seul générateur est `Generateur.generer`. `data` n'appelle jamais `ClientMistral` directement.
- **Verrou 3.** `Generateur.generer` n'accepte que des identifiants : `gabarit_id`, `amorce_ids`, `session_id`, `tache`, `messages_precedents` (prouvés) et `passage_ids`. Toute valeur d'emplacement vient d'une amorce du seed, d'une amorce dérivée vérifiée contre le journal, ou du rendu des passages de l'Index.
- **Couches (AD-1).** `data` (couche 4) peut importer `core`, `mistral`, `mcp`, `index`, `harness` et `budget`, mais pas `evaluation`. Le contrôle du gel (`slmsp.evaluation.gel.jeu_gele_et_commite`) est donc fait par `cli/data.py`, en couche 5. `mistral` n'importe ni `mcp`, ni `harness`, ni `index`.
- **Lectures (AD-24).** `data` lit seulement par `core.artefacts.lire` et `ouvrir_sqlite_lecture`, et ouvre le journal Mistral avec `journal_pour("generation", cfg, lecteur="data")`. Le Jeu d'évaluation n'est vu qu'à travers `core.items.identifiants_proteges(("v1.0", "v1.1", "calibrage"))`.
- **Écritures (AD-21, AD-26).** Le run est `runs/data-generate/<run_id>/` (`nouveau_run`, `parents=[seed_run_id]`). `plan.jsonl` est écrit une seule fois, par création exclusive. Les autres fichiers sont en ajout seul. Les cassettes passent par `mcp.enregistrement.enregistrer(session, "data")`, sans jamais écraser un fichier. Rien n'est supprimé.
- **Ordre de dépense (AD-5) :** `ORDRE_TACHES = ("Q", "RD", "CR", "LC", "generique", "CT", "RE", "CO")`. Les sessions s'exécutent strictement dans l'ordre du plan.
- **Zone de la story :** `src/slmsp/data/{generate,sessions}.py`, `src/slmsp/cli/data.py` (sous-commande `generate`), `tests/data/{test_generate,test_sessions,test_prealables}.py`, et `tests/data/conftest.py`, à créer ou à compléter s'il a été créé par 9.3. On y ajoute un schéma partagé, `src/slmsp/core/schemas/session_donnees.py` (convention 5 : il est créé par la première story qui en a besoin, ici pour 9.5 et 9.6).
- **Extensions hors zone, déclarées et minimales**, comme 9.2 l'a fait pour `client.py` :
  - `src/slmsp/mistral/generateur.py` et `src/slmsp/mistral/client.py` ;
  - `config/prompts/generateur/traces-rd.md` (front-matter seulement) ;
  - `src/slmsp/data/config.py` et `config/donnees.toml` (table `[generation]`, facultative avec ses valeurs par défaut) ;
  - les tests miroirs `tests/mistral/test_generateur.py`, `test_client.py`, `test_gabarits_generateur.py` et `tests/data/test_config_donnees.py`.
- **Prérequis :** la branche part de `main` **après la fusion de 9.3**. `cli/data.py` et le contrat `amorces.jsonl` en viennent.

**Never:**
- Aucun appel réel : ni Mistral, ni MCP, ni HF. La campagne réelle, c'est 9.8.
- Aucune logique de `validate`, `filter` ou `build` (9.5, 9.6).
- Aucune modification du schéma du journal Mistral ni de ses usages.
- Aucune écriture dans la table `[mistral]` de `donnees.toml` (9.8).
- Aucune lecture de `eval/` par `data`.
- Aucune relance automatique d'un appel Mistral en erreur.
- Aucun verdict de juge en entrée.
- Aucun `tool` fabriqué : un message `tool` vient toujours d'une interaction enregistrée.
- Ne pas modifier `harness/`, `index/`, `mcp/` ni `core/gabarits.py`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Tâche à un appel (LC, CO, RE, CT, generique) | groupe d'amorces complet pour le gabarit | 1 appel `generer`, puis 1 ligne `brut.jsonl` (`appel_ids` à 1 élément, `cassettes=[]`) | — |
| Q nominal | amorce `question` ; passages trouvés au plan | `generer("traces-q", [q], sid, "Q", passage_ids=[…])` ; consigne rendue par `formater_passages` ; `brut.passages` = chunk_ids, `index_version` | — |
| Q, passage protégé | URL d'un passage ∈ `identifiants_proteges().urls` | passage retiré au plan, compteur `passages_proteges` | session maintenue |
| Q sans passage | aucun score ≥ seuil, ou tous retirés | `passage_ids=[]`, rendu `AUCUN_PASSAGE` | session maintenue |
| RD sur plusieurs tours | A0 avec `tool_calls`, puis A1 avec `tool_calls`, puis A2 final | tours k = 1, 2 : appels validés, exécutés par `McpEnDirect("outillage")`, cassette `data/cassettes/<sid>.t<k>.json` ; messages `assistant` + `tool` renvoyés ; `brut.cassettes` = [t1, t2] | — |
| RD, appel non conforme | outil inconnu, arguments hors schéma ou JSON illisible | aucun envoi MCP, aucune cassette | abandon `appel_non_conforme` |
| RD, identifiant protégé | argument `dataset_id`/`resource_id` ∈ ids protégés | aucun envoi MCP | abandon `fuite_identifiant` |
| RD, trop de tours | tour d'outils n° `tours_outils_max + 1` demandé | arrêt de la session | abandon `tours_max` |
| RD sans outil | réponse finale dès A0 | — | abandon `sans_appel_outil` |
| RD, erreur JSON-RPC | réponse MCP avec `error` | cassette du tour écrite (preuve) | abandon `erreur_outil` |
| RD, panne de transport | `DelaiDepasse`, `ErreurHttp`, `Injoignable`, `HoteBloque` | ligne `incidents.jsonl`, aucune ligne `brut` ni `abandons` ; la session suivante continue ; statut final `partiel-erreur` | réessayée à la reprise, réponses Mistral réutilisées |
| CR en deux temps | amorce `scenario` (Mistral, seed) | appel 1 `transcription-cr` ; `deriver_amorce(appel1, amorce_id=f"{sid}.transcription", tache="CR", emplacement="transcription")` ajoutée une fois à `amorces-derivees.jsonl` ; appel 2 `cr` | — |
| Réponse tronquée | `finish_reason == "length"` à n'importe quel appel | arrêt de la session | abandon `reponse_tronquee` |
| Clé déjà journalisée | nouveau run sur le même seed, ou reprise | 0 requête Mistral, 0 réservation ; `brut.appels_reutilises` = nombre d'appels | — |
| Arrêt brutal en pleine session | appel 1 journalisé, cassette t1 écrite, pas de ligne `brut` | `--reprendre` : appel 1 et cassette t1 réutilisés, seuls les appels manquants sont faits | — |
| Reprise incohérente | SHA du seed, d'un gabarit ou de `outils-mcp.toml` ≠ `run.json` / plan | rien n'est écrit | `ManifesteInvalide` (code 4) |
| Budget épuisé | `BudgetEpuise` levée par la réservation | le run est marqué `partiel-budget` et les sessions suivantes ne sont pas tentées | code 3 |
| Erreur d'API | `ErreurApiMistral` (4xx, 5xx, réseau) | arrêt immédiat (pas de rafale au pire cas), `partiel-erreur` | code 1 |
| Modèle résolu refusé | `ModeleMistralRefuse` | arrêt immédiat, `partiel-erreur` | code 1 |
| Changement de jour | `PrealableNonSatisfait` levée en cours de run (passage de minuit) | arrêt, `partiel-erreur`, motif « conditions Mistral à revérifier » | code 1 |
| Gel absent ou non ancêtre | `jeu_gele_et_commite("v1.0")` lève une exception | aucun run, aucun journal, aucune requête | code 4 |
| Seed invalide | run absent, de type autre que `data-seed`, ou non `complet` | rien n'est écrit | `ManifesteInvalide` (4) |
| Groupe d'amorces incomplet | un emplacement requis du gabarit manque | groupe ignoré au plan, compté dans `amorces_incompletes[T]` | — |
| Amorces insuffisantes | groupes < volume visé | toutes les sessions possibles sont planifiées, `deficit[T]` > 0 | statut `complet` |
| Amorce corrompue | `sha_texte` faux, amorce Mistral non journalisée | — | abandon `provenance_invalide`, la session suivante continue |
| Run déjà complet | `--reprendre` d'un run `complet` | rien n'est écrit | `SlmspError` (1) |
| Interruption clavier | Ctrl+C | `terminer("interrompu")` | code 1 |

</intent-contract>

## Code Map

- `src/slmsp/mistral/generateur.py` : `Generateur`. À étendre : outils, `passage_ids`, `deriver_amorce`, cassettes multiples, forme `"\n".join` des résultats. À réutiliser : `message_assistant`, `CLES_OPTIONNELLES_GABARIT`, `_normaliser_assistant`.
- `src/slmsp/mistral/client.py` : `ClientMistral._appeler`. Ajouter `tools` et `tool_choice` aux paramètres envoyés. Le corps capturé (et donc journalisé) les contient.
- `src/slmsp/mistral/journal.py` : `journal_pour(..., lecteur="data")`, `appels_session`, `LigneAppel` (colonnes `gabarit_id`, `version_gabarit`, `sha256_gabarit`, `amorce_ids`, `requete`, `reponse_brute`, `statut`, `modele_resolu`). Lecture seule.
- `src/slmsp/core/artefacts.py` : `nouveau_run`, `ouvrir_run`, `reprendre(run_id, fichier="brut.jsonl", cle="session_id")`, `Run.ecrire`, `Run.ajouter_jsonl`, `Run.lire_jsonl`, `Run.terminer`, `lire`.
- `src/slmsp/core/schemas/amorce.py` : `Amorce` (contrat seed). `src/slmsp/core/schemas/cassette.py` : `Cassette`. `src/slmsp/core/schemas/run.py` : statuts.
- `src/slmsp/core/gabarits.py` : `valider_gabarit(chemin, cles_optionnelles=…)` (`.id`, `.version`, `.sha256`, `.emplacements`), utilisé au pré-vol.
- `src/slmsp/core/items.py` : `identifiants_proteges(versions)` (`urls`, `dataset_ids`, `resource_ids`).
- `src/slmsp/mcp/direct.py` : `McpEnDirect("outillage")`, `.appeler(nom, args)`, `.session(session_id=…)`. `src/slmsp/mcp/outils.py` : `valider_appel`, `charger_outils`, `charger_config().tools_list_sha256`. `src/slmsp/mcp/enregistrement.py` : `enregistrer`, `chemin_cassette("data", sid)`.
- `src/slmsp/harness/recherche_index.py` : `RechercheIndex.rechercher` / `depuis_config`. `src/slmsp/harness/prompts.py` : `formater_passages`. `src/slmsp/harness/taches/recherche.py` : `contenu_resultat` (règle unique du contenu d'un message `tool`).
- `src/slmsp/evaluation/gel.py` : `jeu_gele_et_commite(version, racine)`, appelé par la CLI seulement.
- `src/slmsp/evaluation/assemblage.py` : modèle d'assemblage `ServeurLlama` (BGE-M3) + `ouvrir_index`, à reproduire dans la CLI.
- `src/slmsp/data/config.py` : `ConfigDonnees` (volumes, `[mistral]`), à étendre avec `[generation]`.
- `src/slmsp/cli/eval.py` : modèle pour les sous-commandes, `--racine`, les codes `CodeSortie` et l'affichage de progression.
- `tests/mistral/conftest.py` : modèle du faux serveur Mistral (`httpx2.MockTransport` via `slmsp.net`) et de `texte_budgets`. Avec `--import-mode=importlib`, on le recopie dans `tests/data/conftest.py` plutôt que de l'importer.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/mistral/client.py` : ajouter à `_appeler` les paramètres mot-clé `tools: Sequence[Mapping] | None = None` et `tool_choice: str | None = None`, ajoutés à `parametres` s'ils ne sont pas `None`. `appeler()` public reste inchangé. Raison : AD-8, le générateur reçoit les mêmes schémas.
- `src/slmsp/mistral/generateur.py` : apporter les extensions (a) à (f) des Design Notes. Garder la signature d'identifiants. Raison : préalables techniques de 9.4, et constat différé « traces-rd sans outils » de 9.2.
- `config/prompts/generateur/traces-rd.md` : ajouter au front-matter `outils: mcp-data-gouv`, sans toucher à la consigne. `version` reste 1, puisqu'aucun appel n'a été journalisé avec ce gabarit (0 € dépensé) et que `sha256_gabarit` distingue déjà les deux contenus. Décision à consigner.
- `src/slmsp/data/config.py` + `config/donnees.toml` : ajouter `GenerationDonnees` (`surplus: float` dans [0, 1], 0,2 par défaut ; `tours_outils_max: int ≥ 1`, 4 par défaut ; `versions_antifuite: list[str]`, `["v1.0", "v1.1", "calibrage"]` par défaut) sous `ConfigDonnees.generation`, avec une valeur par défaut pour que les registres et tests de 9.1 restent valides. Écrire la table commentée dans `donnees.toml`.
- `src/slmsp/core/schemas/session_donnees.py` : créer `RefGabarit`, `PassagePlan`, `SessionPlanifiee`, `SessionBrute`, `AbandonSession` et `IncidentSession` (champs en Design Notes, `schema_version: Literal[1]`, `extra="forbid"`).
- `src/slmsp/data/sessions.py` : exécuter une session `SessionPlanifiee` selon sa Tâche (un appel, Q, CR, RD), avec la recherche d'appel réutilisable, la projection des messages, l'exécution et la relecture des tours d'outils, et les contrôles anti-fuite des appels. Le module expose le protocole `SessionOutils` (`appeler`, `session`) et `ResolveurPassages`. Raison : logique de session testable sans CLI.
- `src/slmsp/data/generate.py` : regrouper les amorces, planifier, calculer `session_id`, ouvrir le run (nouveau ou reprise, avec les contrôles de cohérence), boucler sur le plan avec la politique d'erreurs, puis écrire `bilan.jsonl` et le statut final. Point d'entrée : `lancer_generation(...)` (Design Notes).
- `src/slmsp/cli/data.py` : implémenter `generate`, avec `--depuis SEED_RUN_ID` ou `--reprendre RUN_ID` (mutuellement exclusifs, l'un des deux requis) et `--racine DIR`. Ordre des étapes :
  1. `jeu_gele_et_commite("v1.0", racine)` (code 4) ;
  2. assemblage : `RegistreBudget`, `charger_mistral`, `ClientMistral(…, fabriquer_sdk(…))`, fabrique du `Generateur`, fabrique `McpEnDirect("outillage")`, `RechercheIndex` (BGE-M3 + `ouvrir_index`) seulement si un nouveau run planifie des sessions Q ;
  3. une ligne de progression par session, puis le tableau par Tâche, le chemin du run, son statut et la dépense de l'invocation.

  Codes de sortie : 0 `complet`, 3 `partiel-budget`, 1 `partiel-erreur` ou `interrompu`, 4 gel ou manifeste, 2 usage.
- `tests/data/conftest.py` : doublures. Faux serveur Mistral scriptable (réponses texte ou `tool_calls` aléatoires, `finish_reason` réglable, compteur de requêtes et corps capturés), registre de budget de test, seed synthétique écrit par `nouveau_run("data-seed", …)` + `amorces.jsonl`, faux `SessionOutils` qui produit une `Cassette` et l'enregistre par `mcp.enregistrement.enregistrer` sous `tmp_path`, fausse recherche d'index (`Passage` aléatoires).
- `tests/data/test_sessions.py` : une ligne de la matrice par test au niveau de la session (Q, RD sur plusieurs tours et ses six abandons, CR, troncature, provenance), plus la réutilisation à l'intérieur d'une session.
- `tests/data/test_generate.py` : plan et ordre, idempotence entre deux runs, reprise après arrêt brutal, reprise incohérente (4), `BudgetEpuise`, `ErreurApiMistral`, `ModeleMistralRefuse`, changement de jour, incidents, contenu de `brut.jsonl` et de `bilan.jsonl`, déficit et groupes incomplets.
- `tests/data/test_prealables.py` : `main(["data", "generate", "--depuis", …, "--racine", depot])` sur un dépôt git de fixture (`git init` dans `tmp_path`). Deux cas :
  - gel absent ou non commité, avec un vrai `jeu_gele_et_commite` ;
  - commit de gel qui n'est pas un ancêtre de `HEAD`, avec `jeu_gele_et_commite` remplacé par monkeypatch pour lever `ManifesteInvalide`, la logique git étant couverte par `tests/evaluation/test_gel.py`.

  Dans les deux cas : code 4, ni `runs/data-generate/`, ni journal, ni requête. Préalables D1.2 : une date de vérification d'hier donne le code 1 (`PrealableNonSatisfait`), sans rien écrire.
- `tests/mistral/test_generateur.py`, `test_client.py`, `test_gabarits_generateur.py`, `tests/data/test_config_donnees.py` : couvrir les extensions (a) à (f), `tools` dans le corps envoyé, la clé `outils` et la nouvelle table. Adapter les tests existants touchés, par exemple ceux qui fournissaient une amorce `passages`.

**Acceptance Criteria:**
- Given `slmsp data generate --depuis <seed_run>`, when le gel `v1.0` n'est pas commité ou que son commit n'est pas un ancêtre de `HEAD`, then la commande sort en 4 sans créer de run, sans ligne de journal et sans requête (D1.3, AC1 de l'epic).
- Given une session dont chaque appel (gabarit, version, SHA, amorces, messages précédents) figure déjà au journal en `generation`/`ok` avec un modèle stable, when on relance `generate`, sur un nouveau run ou en reprise, then le faux serveur Mistral ne reçoit aucune requête et le registre de budget ne bouge pas (AC2).
- Given une trace RD, when Mistral émet des `tool_calls`, then chacun est validé par `valider_appel` contre `config/outils-mcp.toml` avant tout envoi, exécuté par le port d'outils, enregistré sous `data/cassettes/<session_id>.t<k>.json`, et renvoyé au Générateur en messages `assistant` + `tool` que `Generateur._precedents` accepte. Chaque requête RD porte `tools` et `tool_choice: "auto"` (AC3).
- Given un plan couvrant toutes les Tâches, when il s'exécute, then l'ordre des requêtes suit Q, RD, CR, LC, generique, CT, RE, CO. Sur `BudgetEpuise`, `etat.jsonl` se termine par `partiel-budget`, aucune session suivante n'est tentée et la CLI sort en 3 (AC4).
- Given une session terminée, when elle est consignée, then `brut.jsonl` reçoit une ligne `SessionBrute` (`session_id`, `tache`, `appel_ids`, `amorce_ids`, `cassettes`, …). `--reprendre <run_id>` ne rejoue aucune session présente dans `brut.jsonl` ou `abandons.jsonl` (AC5).
- Given le module `slmsp.mistral.generateur`, when on inspecte `Generateur.generer`, then ses paramètres sont exactement `gabarit_id`, `amorce_ids`, `session_id`, `tache`, `messages_precedents` et `passage_ids`. Aucune ligne `generation` n'est écrite sans le jeton (tests 9.2 toujours verts).
- Given `uv run pytest tests/test_architecture.py`, when il analyse `data/generate.py`, `data/sessions.py` et `cli/data.py`, then aucune règle n'est violée : pas d'import de `evaluation` ni de `judge` depuis `data`, pas de lecture directe, journal ouvert avec `lecteur`, pas d'usage de `_appeler` ni de `_JETON` hors du Générateur.
- Given tous les tests de la story, when on les parcourt, then aucun ne contient de texte réaliste rédigé : toutes les chaînes de contenu sont aléatoires (D1.1).

## Spec Change Log

## Review Triage Log

## Design Notes

**Extensions du Générateur** (une seule PR, un commit distinct conseillé avant `data`) :
- **(a) Outils.** `CLES_OPTIONNELLES_GABARIT = ("max_tokens", "outils")`. La seule valeur admise est `mcp-data-gouv`. Un gabarit qui la porte fait lire au Générateur `config/outils-mcp.toml` (`lire(…, "data")` puis `tomllib.loads`), projeté au format `tools` d'OpenAI (`{"type": "function", "function": {name, description, parameters}}` par entrée `[[outils]]`, dans l'ordre). Ces outils sont envoyés à **chaque** appel de ce gabarit, avec `tool_choice="auto"`. Un gabarit `tache: RD` sans `outils` lève `GabaritInvalide`. Un test vérifie l'égalité avec `slmsp.mcp.outils.charger_outils()`. On duplique la projection parce que `mistral` ne peut pas importer `mcp`, qui est dans la même couche.
- **(b) Passages.** L'emplacement `passages` est réservé : une amorce qui le vise lève `GabaritInvalide`. `Generateur(..., rendre_passages: Callable[[Sequence[str]], str] | None = None)` et `generer(..., passage_ids: Sequence[str] | None = None)`. Si le gabarit déclare `passages`, `passage_ids` doit être fourni (liste vide permise) et `rendre_passages` présent, sinon `ProvenanceInvalide`. La valeur de l'emplacement vaut `rendre_passages(passage_ids)`. Si le gabarit ne déclare pas `passages` et que `passage_ids` est fourni, `ProvenanceInvalide`. L'emplacement `passages` est exclu du contrôle « emplacement sans amorce ».
- **(c) Amorce dérivée.** `deriver_amorce(appel_id, *, amorce_id, tache, emplacement) -> Amorce`. La ligne du journal doit être admise (`_ligne_admise`), `message_assistant(brut)` doit avoir un `content` non vide et aucun `tool_calls`, et la réponse ne doit pas être tronquée (`finish_reason != "length"`). Le résultat est un `Amorce(auteur_contenu="mistral", appel_id=…, sha_texte=sha256_hex(texte))`, enregistré dans `self._amorces`. Le même id avec un autre SHA lève `ProvenanceInvalide`. Le même id avec le même SHA est idempotent.
- **(d) Cassettes de session.** `_cassette` devient `_cassettes(session_id)` : `data/cassettes/<sid>.json` s'il existe, puis `<sid>.t1.json`, `<sid>.t2.json`, … jusqu'au premier absent. `_resultat_de_cassette` cherche dans toutes ces cassettes.
- **(e) Contenu d'outil.** `_textes_resultat` admet aussi `"\n".join(textes)`, la forme de `harness…contenu_resultat` quand tous les éléments sont `text`.
- **(f) Estimation.** `tokens_entree_estimes` compte aussi `json_canonique(tools)`.

**Identifiant et clé de session.** Les calculs se font au plan.

`cle = json_canonique({"tache", "gabarits": [[id, version, sha256]…], "amorces": [[amorce_id, sha_texte]…], "passages": [chunk_id…] | None, "index_version": … | None, "outils": tools_list_sha256 | None})`, et `session_id = f"{tache.lower()}-{sha256_hex(cle)[:24]}"`. La forme est compatible avec `_RE_SESSION_ID`, avec les noms de cassette et avec le motif d'`amorce_id` (minuscules).

Les passages entrent dans la clé : un Index différent donne une autre session, et aucune réponse fondée sur d'autres passages n'est réutilisée.

**Recherche d'un appel réutilisable** (`sessions.py`, avant chaque `generer`). Parmi `journal.appels_session(sid)` (lecteur `data`), on prend la **première** ligne (ordre d'inscription) qui remplit toutes ces conditions :
- `usage == "generation"`, `statut == "ok"` et `modele_resolu ∈ generateur.prealables.modeles_stables` ;
- `gabarit_id`, `version_gabarit` et `sha256_gabarit` égaux ;
- `amorce_ids == json_canonique(list(ids)).decode()` ;
- `len(json.loads(requete)["messages"]) == 1 + len(precedents)` ;
- `projection(messages[1:]) == projection(precedents)`.

La projection garde, pour un `assistant` : `content` (s'il est non vide) et `tool_calls` réduits à (`id`, `function.name`, arguments décodés). Pour un `tool` : (`tool_call_id`, `content`). Elle ignore donc les champs que le SDK ajoute en sérialisant.

Le message `assistant` réutilisé vaut `message_assistant(ligne.reponse_brute)`, et `finish_reason` est lu dans `choices[0]`. Sans ligne trouvée, on appelle `generateur.generer(...)`.

**Session RD.**
1. A0 = `generer("traces-rd", ids, sid, "RD")`.
2. Tant que la réponse porte des `tool_calls` :
   - k += 1 ; si k > `tours_outils_max`, abandon `tours_max` ;
   - on décode les arguments, puis on applique `valider_appel` à **tous** les appels avant d'en exécuter un seul ;
   - on compare `dataset_id` et `resource_id` aux ids protégés ;
   - si `data/cassettes/<sid>.t<k>.json` existe (reprise ou autre run), on le relit et on l'apparie appel par appel (même nom, mêmes arguments en JSON canonique, dans l'ordre), sinon abandon `cassette_incoherente`. Sinon, on ouvre un `SessionOutils` neuf, on exécute dans l'ordre, puis `enregistrer(outils.session(session_id=f"{sid}.t{k}"), "data")` ;
   - une réponse `error` donne l'abandon `erreur_outil`, après l'enregistrement ;
   - précédents += [assistant, *{"role": "tool", "tool_call_id", "name", "content": contenu_resultat(reponse)}] ;
   - appel suivant.
3. Une réponse finale à k == 0 donne l'abandon `sans_appel_outil`.

`brut.cassettes` liste les chemins relatifs POSIX, dans l'ordre des tours.

**Session CR.** Le seed fournit l'amorce `scenario` (Mistral). Appel 1 `transcription-cr`. On dérive ensuite l'amorce `f"{sid}.transcription"`, qu'on ajoute à `amorces-derivees.jsonl` si elle est absente (relue par `Run.lire_jsonl`). Appel 2 `cr` avec `[id dérivé]`. `brut.appel_ids = [transcription, cr]` : la dernière réponse est toujours la réponse finale, ce que 9.6 doit savoir. `brut.amorces_derivees = [id dérivé]`.

**Plan** (`generate.py`, nouveau run seulement, écrit dans `plan.jsonl` puis relu à la reprise) :
- **Regroupement.** On regroupe les amorces du seed d'une Tâche par origine : (`jeu`, `revision`, `ligne`) ou `appel_id`. Un groupe dont l'ensemble des emplacements est exactement celui du premier gabarit de la chaîne, hors `passages`, devient une session. Sinon il compte dans `amorces_incompletes`. C'est un **contrat déduit d'`epics.md` pour 9.3** : si 9.3 groupe autrement, seule `grouper_amorces` change.
- **Volume.** Les groupes sont triés par plus petit `amorce_id`. On en prend `ceil(volume[T] × (1 + surplus))` et l'écart va dans `deficit[T]`.
- **Chaînes de gabarits :** Q→`traces-q` ; RD→`traces-rd` ; CR→`transcription-cr`,`cr` ; LC→`lc` ; CO→`co` ; RE→`re` ; CT→`ct` ; generique→`generique`.
- **Passages Q.** Pour Q, on appelle `recherche(texte de l'amorce question)` au plan, on retire les URL protégées, et on stocke les `Passage` complets dans `SessionPlanifiee.passages` : la reprise n'a ni embedder ni nouvelle recherche. `ResolveurPassages` se charge depuis le plan.

**Entrée.** `lancer_generation(*, racine, config: ConfigDonnees, commit_gel, fabriquer_generateur: Callable[[str, ResolveurPassages], Generateur], ouvrir_outils: Callable[[], ContextManager[SessionOutils]], recherche: Callable[[str], list[Passage]] | None, index_version, seed_run_id=None, reprendre_run_id=None, ecrire=print) -> ResultatGeneration(run, statut, bilan)`.

Le run reçoit :
- `config` = {`seed_run_id`, `commit_gel`, `volumes`, `surplus`, `tours_outils_max`, `versions_antifuite`, `index_version`} ;
- `entrees` = SHA de `amorces.jsonl`, de `config/outils-mcp.toml` et de chaque gabarit utilisé.

À la reprise, ces SHA sont recalculés : un écart lève `ManifesteInvalide`.

**Fichiers du run** :
- `plan.jsonl` (`SessionPlanifiee`) ;
- `brut.jsonl` (`SessionBrute`) ;
- `abandons.jsonl` (`AbandonSession`, `motif` parmi `appel_non_conforme`, `fuite_identifiant`, `tours_max`, `sans_appel_outil`, `erreur_outil`, `reponse_tronquee`, `cassette_incoherente`, `provenance_invalide`) ;
- `incidents.jsonl` (`IncidentSession`) ;
- `amorces-derivees.jsonl` (`Amorce`) ;
- `bilan.jsonl`, une ligne par invocation : statut, motif, par Tâche {planifiees, completes, abandons par motif, incidents, appels_nouveaux, appels_reutilises}, `cout_eur` (somme des `ReponseMistral.cout_eur` des appels nouveaux), `amorces_incompletes`, `deficit`, `passages_proteges`.

**Politique d'erreurs** :
- statut `complet` si toutes les sessions du plan sont dans `brut.jsonl` ou `abandons.jsonl` ;
- `partiel-erreur` s'il reste des incidents ;
- `BudgetEpuise` donne `partiel-budget` ;
- `ErreurApiMistral`, `ModeleMistralRefuse` et `PrealableNonSatisfait` arrêtent le run en `partiel-erreur` (un 5xx est compté au pire cas : on ne boucle pas) ;
- `GabaritInvalide` est détecté au pré-vol, avant la création du run.

Un seul écrivain par run : deux `generate --reprendre` simultanés sur le même run ne sont pas pris en charge (documenté).

**Décisions prises seul (à consigner au journal)** :
- extensions hors zone du Générateur ;
- `traces-rd` reste en version 1 ;
- une cassette par tour (`.t<k>`) ;
- abandon RD sans outil ;
- contrôle anti-fuite des identifiants d'outils et des URL de passages dès `generate` ;
- gel exigé = `v1.0` (D1.3 et AC1), v1.1 servant à l'anti-fuite ;
- code 3 pour `partiel-budget` (la commande `eval` sort en 1).

## Verification

**Commands:**
- `uv run pytest -q --tb=short tests/data tests/mistral` -- expected: tout passe, aucun réseau, aucune requête hors du faux transport
- `uv run pytest -q --tb=short tests/test_architecture.py tests/test_cli.py` -- expected: vert ; `slmsp data generate --help` décrit `--depuis`, `--reprendre` et `--racine`
- `uv run ruff check` et `uv run ruff format --check` -- expected: aucun écart
- `uv run pytest -q --tb=line -p no:warnings` (une seule fois, à la fin) -- expected: vert, sinon liste exacte des échecs préexistants hors zone

**Manual checks (if no CLI):**
- Relire les fixtures de `tests/data/` : aucune phrase réaliste, seulement des jetons aléatoires (D1.1).
- Vérifier que `config/prompts/generateur/traces-rd.md` n'a changé que par la ligne `outils: mcp-data-gouv` du front-matter.

## Remarques du juge (à intégrer)

- **Surplus de 20 %** : il dépasse les volumes de `config/donnees.toml:28-45`. À aligner sur AC4.
- **`traces-rd.md`** : il est modifié sans changer de version.
- **Connexion MCP** : la spec en ouvre une neuve à chaque tour. Or `McpEnDirect.session()` est cumulative (`mcp/direct.py:383-404`) : enregistrer un segment de cassette par tour.
- **Signature de `generer`** : ajouter `passage_ids` impose de réécrire le test de signature (`tests/mistral/test_generateur.py:179-188`). Variante plus sûre de la version Sonnet : garder la signature intacte (verrou 3).
- **Écart à traiter** : `_textes_resultat` donne `""` (`generateur.py:226`), alors que `contenu_resultat` donne `"\n"` (`harness/taches/recherche.py:164`).
