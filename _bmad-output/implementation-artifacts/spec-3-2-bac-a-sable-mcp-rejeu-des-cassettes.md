---
title: 'Story 3.2 — Bac à sable MCP : rejeu des cassettes'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: 'a1895d874b5daf560ab086237c3ce6f01e7bd715'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Le Harnais n'a qu'un adaptateur `ToolPort` en direct (3.3). Sans rejeu déterministe des cassettes, deux évaluations du même modèle ne voient pas les mêmes réponses d'outils, et le repli sur panne MCP n'est pas testable sans réseau (FR-9, FR-25, FR-40, NFR-8, AD-10, SPEC §4).

**Approach:** Ajouter `BacASable`, second adaptateur de `ToolPort`, qui charge les cassettes d'un item, refuse celles dont l'empreinte diffère de la config, et répond à chaque appel par l'appariement AD-10 (exact, puis le plus proche du même outil, puis réponse vide normalisée), en levant les exceptions de transport du client direct pour les interactions `simulation`. Le texte de la réponse vide est ajouté à `config/outils-mcp.toml`.

## Boundaries & Constraints

**Always:**
- Zone : `src/slmsp/mcp/bac_a_sable.py`, `src/slmsp/mcp/outils.py` (champ `texte_reponse_vide` de `ConfigOutilsMcp` seulement), `config/outils-mcp.toml` (clé `texte_reponse_vide`, placée avant `[[outils]]` ; rien d'autre ne change, `tools_list_sha256` compris), `tests/mcp/test_bac_a_sable.py`, ajustements de `tests/mcp/test_outils.py` si nécessaire, et ce fichier de spec.
- `mcp` n'importe que `slmsp.core` (et `slmsp.mcp`) ; aucune bibliothèque lourde ; pas de `net`, pas de `harness`.
- Adaptateur sans état : aucune donnée ne change après `__init__` ; chaque réponse est une copie profonde ; deux rejeux de la même séquence donnent des `json_canonique` égaux.
- Chaque appel passe d'abord par `valider_appel(nom, arguments, chemin=chemin_outils)` comme `McpEnDirect.appeler` (`AppelNonConforme` levée telle quelle).
- Seules les interactions `request.method == "tools/call"` servent à l'appariement ; leur ordre est celui des cassettes passées, puis des interactions.
- Égalité des arguments et des valeurs : par `json_canonique` (`slmsp.core.canonique`).
- « Appel non prévu » : `slmsp.core.evenements.Avertissement(code="appel-non-prevu", message=…)` passé au rappel `signaler` s'il est fourni ; sans effet sur la réponse.
- Tests sans réseau ; fichiers de `eval/` lus seulement (empreinte SHA-256 et mtime inchangés).

**Never:**
- Modifier `eval/**`, `core/evenements.py`, `core/ports.py`, `core/erreurs.py`, `mcp/direct.py`, `mcp/enregistrement.py`, `mcp/cassettes.py`, `harness/`, `judge/`, `config/reseau.toml`.
- Implémenter le repli, le Mode ou la boucle d'outils (Epic 4).
- Écrire des Données d'entraînement réalistes dans les fixtures (textes factices `"<réponse-factice-1>"`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Appariement exact | arguments de JSON canonique égal à une interaction | sa `response` (copie), `id` remplacé par `id_requete` ; aucun évènement | — |
| `id_requete` omis | `appeler(nom, args)` | `id` = `PREMIER_ID_APPEL` (3) | — |
| Le plus proche | même outil, aucun égal exact | interaction au plus grand nombre de paires (clé, valeur) égales (0 permis), premier rang en cas d'égalité ; un `Avertissement` `appel-non-prevu` | — |
| Aucun appel du même outil | outil exposé absent des cassettes | `{"jsonrpc":"2.0","id":id,"result":{"content":[{"type":"text","text":<texte_reponse_vide>}],"isError":false}}` ; un `Avertissement` | — |
| Simulation rejouée | interaction appariée (exacte ou proche) avec `simulation` | aucune réponse | `PAR_TYPE_SIMULATION[type]` ; `ErreurHttp.statut` = `simulation.statut` |
| Appel non conforme | outil non exposé ou arguments invalides | rien n'est rejoué | `AppelNonConforme` |
| Empreinte différente | cassette dont `tools_list_sha256` ≠ config | refus au chargement | `SchemaOutilModifie`, attribut `ecarts` (tuple) citant le nom du fichier ou le rang |
| Cassette illisible | chemin absent / JSON invalide | refus au chargement | `CassetteInvalide` (de `lire_cassette`) |
| Interaction `tools/call` malformée | `params.name` non chaîne ou `arguments` non objet | refus au chargement | `CassetteInvalide` |
| Cassettes héritées | `R-001.json`, `R-002.json`, `tools-list.json` | acceptées (empreinte du voisin = config) ; `tools/list` ignoré | — |
| Config | `texte_reponse_vide` absent, vide, ou clé inconnue | refus | `ConfigurationInvalide` |

</intent-contract>

## Code Map

- `src/slmsp/core/ports.py:94` -- LECTURE SEULE : `ToolPort` (`lister_outils`, `appeler(nom, arguments) -> dict`). `BacASable.appeler` ajoute le mot-clé facultatif `id_requete`.
- `src/slmsp/mcp/direct.py:338-379` -- LECTURE SEULE : référence de forme. `appeler` valide, puis renvoie la réponse JSON-RPC complète (`jsonrpc`, `id`, `result` ou `error`) en copie profonde ; `lister_outils` = `charger_outils(chemin_outils)`.
- `src/slmsp/mcp/erreurs.py` -- LECTURE SEULE : `PAR_TYPE_SIMULATION`, `ErreurHttp(message, statut=)`, `CassetteInvalide`.
- `src/slmsp/mcp/cassettes.py:84` -- LECTURE SEULE : `lire_cassette(chemin) -> Cassette` (héritées acceptées).
- `src/slmsp/core/schemas/cassette.py` -- LECTURE SEULE : `Cassette.interactions[Interaction(request, response, simulation)]`, `Simulation(type, statut)`.
- `src/slmsp/mcp/enregistrement.py:37` -- LECTURE SEULE : `PREMIER_ID_APPEL = 3`.
- `src/slmsp/mcp/outils.py:63` -- `ConfigOutilsMcp(ModeleConfig)`, extra=forbid : y ajouter `texte_reponse_vide`.
- `src/slmsp/core/erreurs.py` -- LECTURE SEULE : `SchemaOutilModifie`, `ConfigurationInvalide`.
- `src/slmsp/core/evenements.py` -- LECTURE SEULE : `Avertissement(code, message)`, `Evenement`.
- `tests/mcp/test_outils.py:111-150` -- `_ecrire_config` / `_config_reelle` reprennent les clés de la config réelle : la nouvelle clé y passe d'elle-même.
- `eval/cassettes/RD-*/s1.json` -- LECTURE SEULE : 40 cassettes gelées, `schema_version` 1, 75 `tools/call`, 4 simulations (RD-005 `delai_depasse`, RD-014 `erreur_http` 503, RD-020 `injoignable`, RD-032 `erreur_http` 500).
- `eval/calibrage/cassettes/` -- LECTURE SEULE : `R-001.json`, `R-002.json`, `tools-list.json`.
- `tests/conftest.py` -- garde réseau autouse.

## Tasks & Acceptance

**Execution:**
- `config/outils-mcp.toml` -- ajouter `texte_reponse_vide = "No results found."` après `tools_list_sha256`, avec une ligne de commentaire d'en-tête -- texte de la réponse vide normalisée (AD-10).
- `src/slmsp/mcp/outils.py` -- ajouter `texte_reponse_vide: str = Field(min_length=1)` à `ConfigOutilsMcp` -- report de la 3.1.
- `src/slmsp/mcp/bac_a_sable.py` -- créer `CODE_APPEL_NON_PREVU = "appel-non-prevu"`, `reponse_vide(id_requete, texte) -> dict` et `BacASable(cassettes: Sequence[Cassette | str | Path], *, chemin_outils=None, signaler: Callable[[Evenement], None] | None = None)` avec `lister_outils()` et `appeler(nom, arguments, *, id_requete=PREMIER_ID_APPEL)` -- adaptateur de rejeu AD-10.
- `tests/mcp/test_bac_a_sable.py` -- couvrir chaque ligne de la matrice (cassettes synthétiques dans `tmp_path` construites avec `Cassette`/`ecrire_cassette`, textes factices) ; rejouer R-001/R-002 ; rejouer les 40 cassettes RD gelées : chaque `tools/call` sans simulation renvoie exactement la `response` enregistrée (avec `id_requete` = id enregistré) sans évènement, chaque simulation lève la bonne exception ; vérifier `eval/` inchangé ; `isinstance(bac, ToolPort)`.

**Acceptance Criteria:**
- Given une séquence d'appels mêlant les trois cas, when on la rejoue deux fois (même instance puis nouvelle instance), then les réponses ont des `json_canonique` égaux et les évènements sont identiques.
- Given le dépôt après la story, when on lance `uv run pytest` et `uv run ruff check`, then tout passe, `tests/test_architecture.py` compris, sans réseau, et `git status --short eval/` est vide.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 31 findings — high 0, medium 0, low 22, false 9, maybe-false 0
- findings:
  - `[low]` `[reject]` (blind) Config relue à chaque appel (`valider_appel`, `lister_outils`) : une édition du TOML après `__init__` change la validation mais pas l'index — l'édition de la config pendant un rejeu n'arrive pas en usage courant ; même comportement que `McpEnDirect` ; le correctif ajoute un instantané des validateurs.
  - `[low]` `[reject]` (blind) `signaler` et `chemin_outils` publics et réassignables — convention Python du dépôt (`McpEnDirect` idem) ; réassigner `chemin_outils` est un usage hors contrat ; le correctif ajoute des propriétés.
  - `[low]` `[reject]` (blind) Interactions enregistrées non validées au chargement (entrées mortes) — les cassettes viennent de `mcp record`, qui valide ; une entrée morte ne fausse aucune réponse ; ajout d'une branche de validation.
  - `[low]` `[reject]` (blind) Doublons `(outil, arguments)` : seule la première interaction est rejouée — règle AD-10 (adaptateur sans état, ordre de la cassette) ; aucun conflit dans les 40 cassettes RD (test vert sur les 75 appels) ; une consommation en ordre rendrait l'adaptateur à état.
  - `[low]` `[reject]` (blind) `id_requete` hors du protocole `ToolPort` : appelé via le port, l'`id` vaut toujours 3, alors que `McpEnDirect` numérote 3, 4, 5… — choix consigné en Design Notes ; `core/ports.py` est hors zone et un compteur casserait l'absence d'état ; le Harnais lit `result`, pas l'`id` ; à reprendre en 4.3 si besoin.
  - `[low]` `[reject]` (blind) `ecarts` posé par attribut sur `SchemaOutilModifie` — motif déjà établi par `comparer_schema_serveur` (3.1) ; `core/erreurs.py` hors zone ; une sous-classe dupliquerait la hiérarchie.
  - `[low]` `[patch]` (blind) L'avertissement « le plus proche » ne cite que le rang global, pas la cassette — `_Enregistre.origine` (chemin ou « cassette de rang N », indice d'interaction) cité dans le message ; assertion ajoutée dans `test_le_plus_proche_premier_rang`.
  - `[low]` `[patch]` (blind) Aucun test ne rejoue une réponse JSON-RPC `error` ni un `result` `isError: true` — `test_reponses_d_erreur_rejouees_telles_quelles` ajouté.
  - `[low]` `[patch]` (blind) Le test de déterminisme ne couvre pas une simulation appariée par proximité ; `_rejouer` n'attrape que `ErreurHttp` — `_rejouer` attrape `ErreurTransportMcp` ; séquence complétée d'une panne `delai_depasse` atteinte par proximité.
  - `[false]` `[reject]` (blind) `test_config_texte_reponse_vide` ne recalcule pas l'empreinte de la source — l'invariant est déjà vérifié par `tests/mcp/test_outils.py::test_tools_list_sha256_egal_empreinte_calibrage`.
  - `[false]` `[reject]` (blind) `assert choisi.reponse is not None` disparaît sous `-O` — `Interaction` garantit `response` non nul sans `simulation` (validateur `_reponse_ou_simulation`) ; la branche est inatteignable.
  - `[low]` `[reject]` (edge) `id` toujours 3 via `ToolPort` — même cause que la ligne `id_requete` ci-dessus ; même motif.
  - `[low]` `[reject]` (edge) `page_size=5.0` accepté par jsonschema mais non apparié exactement à `5` — cas rare (llama.cpp émet des entiers) ; l'effet se limite à un avertissement et au rejeu du voisin ; une normalisation des nombres ajoute une couche.
  - `[low]` `[reject]` (edge) Surrogate isolé dans un argument → `UnicodeEncodeError` dans `json_canonique` — sortie de modèle analysée en JSON valide ; cas irréaliste ; garde supplémentaire.
  - `[false]` `[reject]` (edge) Une exception levée par `signaler` interrompt l'appel — propager l'erreur du rappel de l'appelant est le comportement correct.
  - `[low]` `[reject]` (edge) Une cassette malformée placée avant des cassettes d'empreinte différente masque ces écarts — l'échec reste bruyant (`CassetteInvalide`) ; réordonner les contrôles ajoute une passe.
  - `[low]` `[patch]` (edge) `tools/call` sans `params.arguments` (permis par MCP) refusé — absence traitée comme `{}` ; `test_tools_call_sans_arguments` ajouté ; le cas `arguments: None` reste refusé.
  - `[low]` `[reject]` (edge) Config modifiée après `__init__` — même cause que la première ligne « blind » ; même motif.
  - `[low]` `[reject]` (edge) Appels identiques enregistrés plusieurs fois : la première réponse gagne toujours — même cause que la ligne « doublons » ; même motif.
  - `[low]` `[patch]` (verification-gap) `test_modeles_et_chemins_melanges` ne peut pas échouer — le test modifie désormais un texte de `response` et un `simulation.statut` du modèle passé, puis vérifie le rejeu inchangé.
  - `[low]` `[patch]` (verification-gap) Réunion de plusieurs écarts d'empreinte non testée — cas à deux cassettes fautives (chemin et modèle) ajouté à `test_empreinte_differente_refusee`.
  - `[low]` `[patch]` (verification-gap) `chemin_outils` non vérifié pour `lister_outils` et la validation — `test_chemin_outils_respecte` ajouté (config réduite à deux outils).
  - `[low]` `[reject]` (intent) `id` honoré seulement hors du port — même cause que la ligne `id_requete` ; même motif.
  - `[low]` `[reject]` (intent) « Appel non prévu » passe par un rappel et pas par le flux d'évènements — le branchement sur la trace relève de 4.3 (boucle d'outils) ; l'`Avertissement` est déjà un évènement sérialisable du flux.
  - `[false]` `[reject]` (intent) Portée « cassettes de l'item » laissée à l'appelant — AD-10 fixe la portée par l'appelant (item côté banc, session côté données) ; l'adaptateur reçoit exactement ces cassettes.
  - `[false]` `[reject]` (intent) `Repli` non déclenché — le repli relève de l'Epic 4 ; l'AC4 de la story s'arrête à l'exception levée, identique au direct.
  - `[false]` `[reject]` (intent) Reproductibilité vérifiée à la surface de l'adaptateur seulement — l'AC6 porte sur l'adaptateur ; les runs relèvent d'AD-13 (Epic 5).
  - `[false]` `[reject]` (intent) Réponse vide augmentée de `jsonrpc` et `id` — la charge `result` est exactement celle d'AD-10 ; l'enveloppe JSON-RPC suit la forme des réponses enregistrées et de `McpEnDirect`.
  - `[false]` `[reject]` (intent) Appariement à zéro paire égale — lecture littérale de l'AC2 (« une interaction du même outil existe ») ; l'AC3 ne vaut qu'en l'absence d'appel du même outil.
  - `[false]` `[reject]` (intent) Champ `texte_reponse_vide` obligatoire — tous les lecteurs chargent le fichier réel ou une copie, qui porte la clé ; suite complète verte sur ce point.
  - `[low]` `[reject]` (intent) Texte de la réponse vide choisi par l'agent (question ouverte de `review-reconcile-eval.md:98`) — AD-10 renvoie au texte de config ; décision consignée, modifiable dans le TOML seul ; à valider par Anaël. Le chemin « le plus proche » et la réponse vide ne sont pas exercés sur les cassettes réelles : la logique est couverte par les cassettes synthétiques (même ligne, même motif).

## Design Notes

**`id` de réponse.** `ToolPort.appeler` ne porte pas d'`id` ; un compteur rendrait l'adaptateur à état. `id_requete` est donc passé par l'appelant (la boucle d'outils de 4.3), avec `PREMIER_ID_APPEL` par défaut. La réponse vide porte aussi `jsonrpc` et `id`, pour garder la forme de `McpEnDirect.appeler` et des `response` des cassettes.

**Évènement.** `core.evenements` n'a pas de type « appel non prévu » et ce module est hors zone : on émet un `Avertissement` à code dédié, qui est déjà un évènement de trace sérialisable.

**Texte de la réponse vide.** Court, neutre et en anglais comme les réponses du serveur data.gouv. Ce n'est pas une Donnée d'entraînement (D1.1), mais une sortie fixe de l'outillage, comme un message d'erreur.

Exemple d'appariement le plus proche : enregistré `{query: "a", page_size: 5}` et `{query: "b"}` ; appel `{query: "b", page_size: 5}` → 1 paire égale chacun → le premier rang (`query: "a"`) est rejoué.

## Verification

**Commands:**
- `uv run pytest tests/mcp -q` -- expected: tous les tests passent.
- `uv run pytest -q` -- expected: suite complète verte (ou échecs préexistants hors zone listés).
- `uv run ruff check` -- expected: aucun diagnostic.
- `git status --short eval/` -- expected: vide.

## Auto Run Result

Status: done

**Résumé.** `BacASable`, second adaptateur de `ToolPort`, rejoue les cassettes d'un item sans réseau et sans état. Il refuse au chargement une cassette dont l'empreinte diffère de la config (`SchemaOutilModifie`, tous les écarts réunis). Chaque appel est validé comme en direct, puis apparié selon AD-10 : exact, puis le plus proche du même outil (avertissement `appel-non-prevu`), puis réponse vide normalisée. Une simulation appariée lève l'exception de transport du client direct. Le texte de la réponse vide est dans `config/outils-mcp.toml` (`texte_reponse_vide`), champ obligatoire de `ConfigOutilsMcp`.

**Fichiers.**
- `config/outils-mcp.toml` : clé `texte_reponse_vide = "No results found."` ; empreinte inchangée.
- `src/slmsp/mcp/outils.py` : champ `texte_reponse_vide` (non vide).
- `src/slmsp/mcp/bac_a_sable.py` : `CODE_APPEL_NON_PREVU`, `reponse_vide`, `BacASable` (créé).
- `tests/mcp/test_bac_a_sable.py` : tests de la matrice, déterminisme, R-001/R-002, 40 cassettes RD gelées (75 appels rejoués à l'identique, 4 simulations), `eval/` inchangé (créé).

**Revue.** 31 constats : 0 high, 0 medium, 22 low, 9 false.
- 7 patchs low : origine citée dans l'avertissement ; `tools/call` sans `arguments` accepté ; tests ajoutés (réponses d'erreur, simulation par proximité dans le déterminisme, mutation imbriquée du modèle, écarts multiples, `chemin_outils`).
- 0 différé.
- 24 rejetés (15 low, 9 false), motifs dans le Review Triage Log.

**Revue de suivi recommandée : non.** Aucun patch high ni medium.

**Vérification.**
- `uv run pytest tests/mcp -q` : 217 passed.
- `uv run pytest -q` : tout passe sauf 1 échec préexistant hors zone, `tests/harness/test_prompts.py::test_items_reels_passent_construire_messages[CT.jsonl]` (clé d'entrée `type` des items CT inconnue de `harness.prompts`).
- `uv run ruff check` : propre.
- `git status --short eval/` : vide.

**Décisions prises seul.**
- Texte de la réponse vide : « No results found. », court, neutre, en anglais comme le serveur. Question ouverte de la revue d'architecture (C7) : à valider par Anaël.
- Réponse vide en enveloppe JSON-RPC (`jsonrpc`, `id`) autour de la charge `result` d'AD-10.
- `id` de réponse : mot-clé `id_requete` (défaut `PREMIER_ID_APPEL`), car `ToolPort` ne porte pas d'`id` et un compteur casserait l'absence d'état.
- « Appel non prévu » : `Avertissement(code="appel-non-prevu")` passé au rappel `signaler`, car `core.evenements` est hors zone.
- Appariement « le plus proche » permis à zéro paire égale (lecture littérale de l'AC2).
- `ecarts` cite le chemin passé, ou « cassette de rang N » pour un modèle ; un `tools/call` sans `arguments` vaut `{}`.

**Risques résiduels.**
- Via le seul protocole `ToolPort`, l'`id` vaut toujours 3 (le direct numérote 3, 4, 5…) : à traiter en 4.3 si la trace en dépend.
- Des appels identiques enregistrés plusieurs fois rejouent toujours la première réponse (règle sans état).
- Toute config `outils-mcp.toml` écrite à la main sans `texte_reponse_vide` est désormais refusée.
