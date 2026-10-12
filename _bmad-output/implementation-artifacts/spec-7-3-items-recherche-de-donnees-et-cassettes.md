---
title: 'Story 7.3 — Items Recherche de données (40) et cassettes'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '9e0243791ddfbbbb4d8b70aea3a419b6d5b87253'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/eval/SPEC-jeu-evaluation.md'
  - '{project-root}/eval/grille-juge-v1.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-7-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Le Jeu d'évaluation v1.0 n'a aucun item Recherche de données. Sans eux, ni « appel valide » ni « réponse exacte » (grille RD) ne peuvent être calculés contre le Bac à sable MCP, et le gel (7.6) est incomplet.

**Approach:** Rédiger 40 items RD dans `eval/construction/v1.0/RD.jsonl`. Pour chaque item connecté, explorer le serveur MCP réel, puis enregistrer la session finale par `slmsp mcp record --item RD-xxx` (magasin `eval`) ; les 4 cas de repli passent par `--simulation`. Les références sont recopiées des cassettes. Un vérificateur indépendant relit chaque item contre sa cassette et écrit `verification/RD.jsonl` ; un test hors ligne contrôle la cohérence items ↔ cassettes.

## Boundaries & Constraints

**Always:**
- Item au schéma fermé de `ItemRD` (story 5.1, `core/items.py` du worktree 5.1) : seules clés permises `id`, `tache` (« Recherche de données »), `difficulte`, `theme`, `entree` (texte), `parametres` (`{}`), `provenance`, `licence_source`, `fictif` (`false`), `version_item` (1), `appels_attendus`, `cassettes`, `reponse_reference`, `valeurs_attendues`, `mode`, `criteres`, `producteurs`. Clés d'un appel : `outil`, `arguments`, `regle` (prose), `regles`.
- `regles` (format de 5.1) : `{"optionnel": bool, "ordre_libre": bool, "arguments": {<nom>: {"exact": v} | {"contient_un_de": [..]} | {"optionnel": true}}}`. Voir Design Notes pour la sémantique.
- `appels_attendus[i].arguments` = arguments exacts d'une requête de la cassette, et la requête enregistrée satisfait ses propres `regles`.
- `cassettes` = `["../../cassettes/RD-xxx/s1.json"]`. Une session par item, `--session s1`, enregistrée une seule fois, après exploration.
- `reponse_reference` (objet) : `jeu_principal` (`id`, `titre`, `producteur`, `url`, plus `derniere_mise_a_jour`, `licence` si demandés), `autres_jeux_cites_possibles` facultatif, `texte` (réponse attendue en français). Identifiants, titres, dates et valeurs recopiés de la cassette.
- `valeurs_attendues` (5 demandes de valeurs) : `{"ressource_id", "filtre", "total_lignes", "lignes": [...]}`, valeurs identiques au texte de la réponse `query_resource_data`.
- `provenance` : entrée « Serveur MCP data.gouv » (`url` `https://mcp.data.gouv.fr/mcp`, `cassette`, `consulte_le` = `recorded_at`). Repli : plus l'entrée du catalogue local (AgentPublic/data-gouv-datasets-catalog, rév. `11f3d3c948…`).
- Composition : 40 items, 15/15/10 ; thèmes social-autonomie 12, etat-civil-papiers 6, travail-emploi 6, collectivites 6, famille-education-sante 6, fiscalite-locale 4 ; 5 demandes de valeurs (`query_resource_data` + `valeurs_attendues`) ; 4 `repli` (36 `connecte`) ; au moins 6 producteurs.
- Un jeu de données principal différent par item ; aucun sujet défibrillateurs (calibrage R-001, R-002).
- Vérificateur indépendant (sans le contexte du rédacteur) ; verdicts au format du README, en ajout seul ; rejets corrigés (même `id`, nouvelle session `s2` si la cassette change) ou remplacés (`RD-041`…), puis revérifiés.

**Never:**
- Toucher `src/`, `config/`, `eval/outils/`, `eval/jeu/`, `eval/calibrage/`, `eval/construction/v1.0/README.md`, les documents de décision, ou `tests/` hors de `tests/eval_outils/`.
- Écrire une cassette autrement que par `slmsp mcp record` ; écrire une valeur, un identifiant ou une date de mémoire.
- Supprimer une cassette : une cassette écartée avant commit est déplacée dans le scratchpad (`cassettes-ecartees/`) et consignée.
- Appeler un service payant ; réseau hors `mcp.data.gouv.fr` et `www.data.gouv.fr`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Connecté | Item RD-xxx, appels finalisés | `eval/cassettes/RD-xxx/s1.json` (initialize + `tools/call`) ; références tirées de la cassette | Erreur JSON-RPC enregistrée : appels revus, nouvelle session |
| Valeurs | `query_resource_data` filtré | `valeurs_attendues` égales aux valeurs du texte de réponse | — |
| Repli | `--simulation delai_depasse` / `erreur_http --statut 503` / `injoignable` | Cassette `initialize: null`, une interaction simulée ; référence = signalement + jeu du catalogue local, sans valeur inventée | — |
| Rejet | Verdict `rejete` | Corrigé ou remplacé, revérifié ; taux consigné | — |

</intent-contract>

## Code Map

- `src/slmsp/cli/mcp.py:119` (`_record`) -- `uv run slmsp mcp record --item RD-xxx --appels <f.json> --session s1 [--simulation T [--statut N]]` ; fichier d'appels `[{"nom", "arguments"}]` ; appels validés avant connexion ; jamais d'écrasement.
- `config/outils-mcp.toml` -- 5 outils figés et leurs paramètres (`additionalProperties = false`) : `search_datasets(query, page, page_size, sort, last_update_range)`, `get_dataset_info(dataset_id)`, `list_dataset_resources(dataset_id)`, `query_resource_data(resource_id, page, page_size, filter_column, filter_value, filter_operator, sort_column, sort_direction)`, `get_resource_info(resource_id)`.
- `eval/calibrage/echantillon-calibrage.jsonl` (R-001, R-002) et `eval/calibrage/cassettes/R-00{1,2}.json` -- référence de format (lecture seule).
- `eval/outils/construire_jeu.py:1054` -- contrôles RD de `composition` (`mode`, outils, `regles` objet) ; producteurs lus dans `producteurs`.
- `<worktree 5.1>/src/slmsp/core/items.py:165-320` (`RegleArgument`, `ReglesAppel`, `AppelAttendu`, `ItemRD`) -- schéma strict à respecter (lecture seule, non fusionné).
- `<SCRATCH>/rd/explore.py` -- exploration du serveur réel sans enregistrement (`uv run python explore.py @appels.json [max]`, liste de `[nom, {arguments}]`).
- `<SCRATCH>/rd/catalogue.py` -- recherche regex dans les titres du catalogue local (`chunk_id` = id du jeu), pour les références de repli.
- `tests/eval_outils/` -- emplacement du test de cohérence.

## Tasks & Acceptance

**Execution:**
- `<SCRATCH>/rd/lots/<LOT>.jsonl`, `<SCRATCH>/rd/appels/RD-xxx.json` -- rédaction par 4 lots parallèles (table « Lots »), exploration puis enregistrement ; chaque lot n'écrit que ses fichiers et ses cassettes.
- `eval/cassettes/RD-001/` à `RD-040/` -- cassettes `s1.json` écrites par `slmsp mcp record`.
- `eval/construction/v1.0/RD.jsonl` -- fusion des lots, triés par `id`, UTF-8, LF.
- `eval/construction/v1.0/verification/RD.jsonl` -- verdicts du vérificateur indépendant (recopiés tels quels) ; remplacements revérifiés.
- `tests/eval_outils/test_items_rd.py` -- test hors ligne : chaque item retenu a une cassette lisible (JSON) dont `tools_list_sha256` égale celle de `config/outils-mcp.toml` ; chaque appel attendu non optionnel apparaît (outil + arguments égaux) dans la cassette et la requête satisfait ses `regles` ; `valeurs_attendues` figurent dans le texte de la réponse ; `jeu_principal.id` figure dans une réponse (connecté) ; repli : interactions toutes simulées ; composition 40 / 15-15-10 / 5 valeurs / 4 repli / ≥ 6 producteurs.

**Acceptance Criteria:**
- Given les brouillons, when on lance `construire_jeu.py composition`, then RD = 40 (15/15/10), thèmes 12/6/6/6/6/4, ≥ 6 producteurs, aucune anomalie de structure, aucun item sans verdict.
- Given `construire_jeu.py rejets`, when on le lance, then le taux de rejet RD est affiché et chaque item retenu a un dernier verdict `accepte`.
- Given les items RD et le `core/items.py` de 5.1, when on les valide en mode strict, then aucun refus.
- Given `pytest tests/eval_outils`, when on le lance hors ligne, then tout passe.

## Design Notes

**Sémantique de `regles`** (consignée pour le banc, story 5.3) :
- argument `exact` : égalité JSON ; `contient_un_de` : la valeur et les chaînes passent toutes deux par `slmsp.core.texte.normaliser` (AD-29 : casse, ponctuation → espace, apostrophe typographique comprise, accents gardés) ; la règle est satisfaite si au moins une chaîne apparaît **en début de mot** dans la valeur normalisée (`(?:^| )` + fragment échappé) ; les chaînes sont écrites déjà normalisées (points fixes de `normaliser`), traits d'union et apostrophes remplacés par des espaces, et chaque fragment accentué est listé avec sa variante non accentuée (« prénom », « prenom ») ; `optionnel: true` seul : absent ou quelconque ; combiné : si présent, doit satisfaire la règle ;
- argument non listé : libre (dans le schéma de l'outil) ;
- appel `optionnel` : peut manquer (ex. recherche quand l'identifiant est dans l'entrée) ; `ordre_libre` : position libre, sinon ordre de la liste.

Exemple :

```json
{"outil": "list_dataset_resources", "arguments": {"dataset_id": "5889d03fa3a72974cbf0d5b1"},
 "regle": "dataset_id exact de l'Annuaire de l'éducation",
 "regles": {"optionnel": false, "ordre_libre": false, "arguments": {"dataset_id": {"exact": "5889d03fa3a72974cbf0d5b1"}}}}
```

**Difficulté.** Facile : une recherche (titre, producteur, lien). Moyen : recherche + `get_dataset_info` ou `list_dataset_resources` (date, licence, fréquence, format). Difficile : 3 appels ou plus avec `query_resource_data`/`get_resource_info`, filtres.

**Repli** (FR-9) : l'Assistant signale l'échec de data.gouv, répond depuis le catalogue de l'Index local et précise que les données n'ont pas été vérifiées en ligne ; pour des valeurs, il dit qu'elles ne sont disponibles qu'en Mode connecté (FR-8). `appels_attendus` = l'appel tenté ; `reponse_reference.comportement_attendu` décrit ce comportement.

## Lots

`<SCRATCH>` = `C:\Users\UTILIS~1\AppData\Local\Temp\claude\C--Users-Utilisateur-Documents-GitHub-service-public-slm-fine-tuning\2b525399-9658-4abc-ae6d-dabcdbffc874\scratchpad`.

| Lot | Ids | Thème | F/M/D | Valeurs | Repli |
|---|---|---|---|---|---|
| A | RD-001–012 | social-autonomie | 5/4/3 | 1 | 1 (`delai_depasse`) |
| B | RD-013–018 ; RD-019–024 | etat-civil-papiers (2/2/2) ; travail-emploi (2/2/2) | 4/4/4 | 2 (un par thème) | 2 (`erreur_http` 503 ; `injoignable`) |
| C | RD-025–030 ; RD-031–034 | collectivites (2/3/1) ; fiscalite-locale (2/2/0) | 4/5/1 | 1 (collectivités) | 1 (fiscalité, `erreur_http` 500) |
| D | RD-035–040 | famille-education-sante | 2/2/2 | 1 | 0 |

Les demandes de valeurs sont difficiles. Les repli sont faciles ou moyens.

## Verification

**Commands:**
- `uv run --offline --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py composition` -- expected: RD aux cibles, aucune anomalie.
- `uv run --offline --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py rejets` -- expected: taux RD affiché.
- `uv run pytest tests/eval_outils -q` -- expected: verts.
- `uv run ruff check tests/eval_outils` -- expected: aucun écart.
- Validation stricte des items RD par le `core/items.py` de 5.1, chargé par chemin depuis le scratchpad -- expected: aucun refus.
- Après fusion de 5.1 : `construire_jeu.py assembler --version v1.0 --racine <copie>` puis `uv run slmsp eval gel --version v1.0 --verifier-seulement --racine <copie>` -- expected: RD 40 items stricts, 40 cassettes vérifiées, 0 erreur bloquante.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 47 findings — high 0, medium 13, low 26, false 8, maybe-false 0
- findings:
  - **Blind Hunter (15)**
    - `[low]` `[patch]` Le contrôle LF normalisait CRLF avant l'assertion — assertion sur le texte décodé brut.
    - `[medium]` `[patch]` Les faits de `reponse_reference.texte` ne sont pas comparés à la cassette — identifiants à 24 caractères hexadécimaux, UUID et URL du texte exigés dans les réponses ; valeurs numériques de `valeurs_attendues.lignes` exigées dans le texte.
    - `[low]` `[patch]` Les champs de `jeu_principal` sont cherchés dans la concaténation de toutes les réponses — `id`, `titre`, `url` et `producteur` exigés dans un même bloc.
    - `[medium]` `[patch]` Les fragments courts de `contient_un_de` (« ase », « apa », « cni ») matchent au milieu des mots — correspondance en début de mot (même entrée que la divergence AD-29, ci-dessous).
    - `[low]` `[patch]` Les noms d'arguments des `regles` ne sont pas confrontés au schéma de l'outil — contrôle par `charger_outils()`.
    - `[low]` `[patch]` Le contrôleur n'a aucun test négatif — 4 altérations d'un item réel, chacune signalée ; cas `optionnel` combiné ajoutés.
    - `[medium]` `[patch]` Les références de repli ne sont pas vérifiées hors duckdb, et la simulation n'est pas liée au texte — fixture `catalogue_repli.json` extraite du parquet, contrôlée sans duckdb ; type et statut de simulation exigés dans `comportement_attendu` et `texte`.
    - `[low]` `[reject]` Pas de repli moyen, pas de cas « aucun résultat » ni `isError` — la composition SPEC §2 est atteinte ; ajouter des cas demande de nouveaux items et cassettes, hors des cibles.
    - `[low]` `[patch]` Aperçu « non prévu » pour les demandes de valeurs ; difficulté et répartition par thème non contrôlées — répartition F/M/D par thème ajoutée au test. L'aperçu est rejeté : il est rejoué par la cassette la plus proche (même outil), dont la réponse donne les colonnes ; c'est un évènement de trace, sans effet sur le score (AD-10). Le contrôle du nombre d'appels par difficulté est rejeté : c'est une consigne de rédaction, pas une règle.
    - `[low]` `[reject]` Espaces doubles dans `titre` (RD-013, RD-022) — « réponse exacte » porte sur les identifiants de jeux (grille RD), pas sur les titres.
    - `[low]` `[patch]` La provenance des cassettes simulées dit « réponses enregistrées » — `role` remplacé par « échec simulé (…) » pour RD-005, 014, 020 et 032.
    - `[low]` `[reject]` Dossier de spec incomplet (statut, chemin du scratchpad, scripts hors dépôt, dénominateur du taux) — le correctif édite la spec ; le dénominateur suit le README (rejets / verdicts).
    - `[low]` `[reject]` Verdicts sans identifiant de vérificateur — le format du README n'en prévoit pas ; `construire_jeu` signale déjà les verdicts sans brouillon.
    - `[low]` `[patch]` Fichiers de session orphelins non détectés — tout fichier sous `eval/cassettes/RD-*/` doit être cité, et l'inverse.
    - `[false]` `[reject]` Logement classé en social-autonomie — SPEC §2 range explicitement le logement dans « Social et autonomie ».
  - **Edge Case Hunter (17)**
    - `[medium]` `[patch]` Fragments courts en sous-chaîne — même entrée que ci-dessus (début de mot).
    - `[medium]` `[patch]` Apostrophe typographique non normalisée — `core.texte.normaliser` change toute ponctuation en espace ; les fragments sont écrits avec des espaces.
    - `[false]` `[reject]` Plantage si `regles` n'est pas un objet — `lire_items` en strict (désormais appelé) refuse ces formes ; un échec bruyant du test est le comportement voulu.
    - `[false]` `[reject]` `KeyError` sans `outil` — même motif : refus par le schéma 5.1, échec bruyant.
    - `[low]` `[reject]` `arguments` absent comparé à `None` — aucun item n'en est privé (schéma : défaut `{}`) ; garde supplémentaire.
    - `[low]` `[reject]` Appels attendus identiques en double — aucun cas réel ; garde supplémentaire.
    - `[false]` `[reject]` `recorded_at` absent ou mal formé — `lire_cassette` (désormais appelé) le refuse ; échec bruyant.
    - `[false]` `[reject]` `result: null` — même motif : refusé ou signalé par le lecteur de production.
    - `[low]` `[patch]` Cassettes non lues par le lecteur de production — `slmsp.mcp.cassettes.lire_cassette` appelé sur chaque cassette.
    - `[low]` `[reject]` `filtre` nul face à une réponse filtrée — les 5 items à valeurs ont un filtre ; garde supplémentaire.
    - `[low]` `[patch]` Préfixe d'URL ou de titre — même correctif que le bloc unique de `jeu_principal`.
    - `[medium]` `[patch]` `texte` jamais comparé aux valeurs ni à `jeu_principal` — même correctif que la ligne Blind Hunter correspondante.
    - `[medium]` `[patch]` Références de repli non vérifiées sans duckdb — fixture et contrôle sans duckdb.
    - `[low]` `[patch]` Cassettes inutilisées non détectées — contrôle des orphelines.
    - `[low]` `[patch]` Nom d'argument de règle inconnu — contrôle par le schéma.
    - `[low]` `[patch]` LF après normalisation — assertion sur le texte brut.
    - `[low]` `[reject]` Appels optionnels exigés dans la cassette — plus strict que la spec, sans faux positif : tous les appels optionnels ont été enregistrés.
  - **Verification Gap (6)**
    - `[medium]` `[patch]` Normaliseur privé, en divergence avec AD-29 (`core.texte.normaliser` garde les accents, ponctuation → espace) ; 6 items échouaient sur leur propre requête sous la règle partagée — le test utilise `core.texte.normaliser`, correspondance en début de mot, chaînes points fixes, variantes accentuée et non accentuée dans 24 items, prose `regle` mise à jour, Design Notes réécrites ; revérifié par un vérificateur indépendant (24 `accepte`).
    - `[medium]` `[patch]` Références de repli et type de simulation non contrôlés — fixture et contrôle du type.
    - `[low]` `[patch]` Cassettes non lues par `lire_cassette` — corrigé.
    - `[medium]` `[patch]` `texte` non comparé — corrigé.
    - `[medium]` `[patch]` Double définition de `contient_un_de` (autre constat) — même entrée AD-29.
    - `[low]` `[reject]` Espace double de RD-013 et RD-022 (autre constat) — même motif que la ligne Blind Hunter.
  - **Intent Alignment (9)**
    - `[low]` `[reject]` `eval gel --verifier-seulement` et le rejeu du Bac à sable ne sont pas exercés — `eval gel` lancé après la fusion de 5.1 : 40 items stricts, 40 cassettes, 0 erreur ; le test appelle désormais `lire_items(strict=True)`. Le `BacASable` (3.2) et le calcul des scores (5.3) n'existent pas encore : hors de cette story.
    - `[medium]` `[patch]` Sémantique de `regles` définie par le test, sans consommateur — alignée sur AD-29 (`core.texte.normaliser`) et consignée dans les Design Notes pour 5.3.
    - `[low]` `[reject]` Valeurs stockées en texte — recopies exactes de la réponse ; la comparaison numérique relève du banc (`core.texte.extraire_nombres`).
    - `[false]` `[reject]` `arguments` complets plutôt que les seuls arguments clés — ce qui est clé est porté par `regles` ; les arguments complets sont nécessaires à l'appariement exact de la cassette (AD-10, étape 1).
    - `[low]` `[patch]` `mode` `hors-ligne` refusé par le test — les trois modes sont acceptés.
    - `[low]` `[patch]` Clés d'item dupliquées dans le test (`CLES_ITEM`) — remplacées par `slmsp.core.items.valider_item(strict=True)`.
    - `[medium]` `[patch]` Références de repli non vérifiées, provenance trompeuse — fixture, contrôle de la simulation, `role` corrigé.
    - `[false]` `[reject]` Motif `autre` pour RD-030 — prévu par le README de `eval/construction/v1.0/`.
    - `[false]` `[reject]` Cassettes par dossier avec `tools_list_sha256` au lieu du format plat du calibrage — format imposé par AD-10 et l'AC 2 de la story.

## Auto Run Result

Statut : done (2026-10-12).

- 40 items RD rédigés par 4 lots parallèles (A 12, B 12, C 10, D 6), 40 cassettes `eval/cassettes/RD-xxx/s1.json` écrites par `slmsp mcp record` (36 connectées, 4 simulées : `delai_depasse` RD-005, `erreur_http` 503 RD-014, `injoignable` RD-020, `erreur_http` 500 RD-032). Aucune cassette écartée.
- Composition : 15/15/10 ; thèmes 12/6/6/6/6/4 ; valeurs RD-010, RD-017, RD-023, RD-030, RD-039 ; 24 producteurs distincts ; un jeu principal distinct par item.
- Double vérification : 2 vérificateurs indépendants (20 items chacun), 1 rejet (RD-030, `autre` : `filter_operator` exigé `exact` sans être optionnel alors que c'est la valeur par défaut du schéma). Corrigé sous le même `id` (règle seule, cassette inchangée, donc pas de session `s2`) et revérifié `accepte` par un troisième vérificateur. Taux de rejet RD : 1 / 41 verdicts (2,4 %).
- Vérifications : `construire_jeu.py composition` (RD 40/40, aucune anomalie, aucun item sans verdict) ; `rejets` ; `pytest tests/eval_outils` (264 passés) et suite complète (1293 passés) ; `ruff check` ; validation stricte 5.1 (`items51.py` chargé du scratchpad) : 0 refus.

Décisions prises seul :
- `valeurs_attendues.filtre` = `{"colonne", "operateur", "valeur"}` (ou `null`), comparé à la ligne `Filter:` de la réponse ; `lignes` = objets colonne → valeur en texte, comparés à un même bloc `Row n:`.
- Le test exige que **tous** les appels attendus (optionnels compris) figurent dans la cassette, et que l'ordre des appels non `ordre_libre` suive la cassette.
- Le test contrôle aussi la conformité de chaque appel au schéma figé (`slmsp.mcp.outils.valider_appel`) et, si l'instantané du catalogue est présent (`SLMSP_EVAL_SOURCES`, duckdb), que le jeu principal d'un repli est une ligne du catalogue local (ignoré sinon).
- Titres et producteurs recopiés avec leurs espaces internes doubles éventuels (RD-013, RD-022) ; espace finale du producteur CNAF et d'un titre (RD-008) omise : la valeur reste une sous-chaîne exacte de la réponse.

### Finalisation après revue (2026-10-12)

**Changement.** 40 items RD (`eval/construction/v1.0/RD.jsonl`) avec cassettes réelles ou simulées (`eval/cassettes/RD-001…040/s1.json`), verdicts indépendants (`verification/RD.jsonl`) et test de cohérence hors ligne. La branche `nuit/2026-10-12` (story 5.1 : `core/items.py`, `slmsp eval gel`) a été fusionnée dans le worktree avant la validation stricte.

**Fichiers.**
- `eval/construction/v1.0/RD.jsonl` : 40 items.
- `eval/cassettes/RD-001/` à `RD-040/` : une session `s1.json` chacun, écrite par `slmsp mcp record`.
- `eval/construction/v1.0/verification/RD.jsonl` : 65 verdicts, en ajout seul.
- `tests/eval_outils/test_items_rd.py` : cohérence items ↔ cassettes ↔ schéma 5.1 ↔ règles.
- `tests/eval_outils/fixtures/catalogue_repli.json` : les 4 lignes de référence de repli, extraites du catalogue local (rév. `11f3d3c9…`).
- Le présent fichier de story.

**Revue.** 47 constats : high 0, medium 13, low 26, false 8.
- Correctifs : 8 entrées, dont 3 medium (sémantique `contient_un_de` alignée sur AD-29, `texte` confronté à la cassette, repli vérifié sans duckdb) et 5 low (lecteur de production, LF brut, noms d'arguments, orphelines, provenance des cassettes simulées). S'y ajoutent les tests négatifs, la répartition par thème et la validation par `core.items`.
- Reportés : aucun.
- Rejetés : 18 (8 false, 10 low), avec leurs motifs dans le journal de triage.
- Après la réécriture des `regles`, les 24 items concernés ont été revérifiés par un vérificateur indépendant : 24 `accepte`.

**Taux de rejet RD** : 1 rejet sur 65 verdicts (1,5 %), soit RD-030 au premier passage. Aucun rejet à la revérification.

**Revue de suivi recommandée : `true`.** Trois entrées medium ont été corrigées en une passe. Risque non revérifié : la sémantique « début de mot après `core.texte.normaliser` » est désormais celle des 40 items, mais elle n'a pas de consommateur. Le banc (story 5.3) doit l'implémenter à l'identique, sinon le score « appel valide » divergera.

**Vérifications** (après correctifs) :
- `composition` : RD 40/40 (15/15/10), 5 valeurs, 4 repli, 24 producteurs, aucune anomalie, aucun item sans verdict.
- `rejets` : RD 1,5 %.
- `assembler` puis `slmsp eval gel --version v1.0 --verifier-seulement` sur une copie : 180 items stricts acceptés (RD 40), 40 cassettes vérifiées, 0 erreur bloquante. Les seuls écarts de composition viennent de CO, RE et CT, qui ne sont pas encore rédigés.
- `pytest tests/eval_outils` : 285 passés, 31 ignorés.
- `ruff check` et `ruff format --check` : propres.
- Suite complète : 1587 passés et 1 échec, `tests/inference/test_serveur.py::test_demarrage_rate_sante` (story 2.2, hors de ma zone). Ce test passe seul et dans son fichier (24 passés) : il est instable sous charge.

**Décision prise seul (revue).** `contient_un_de` = la chaîne, normalisée par `slmsp.core.texte.normaliser`, apparaît en début de mot dans la valeur normalisée. Les chaînes sont des points fixes de la normalisation, et chaque variante accentuée est accompagnée de sa variante non accentuée.

**Risques résiduels.**
- La comparaison des valeurs numériques au `texte` se fait par sous-chaîne : les valeurs courtes (mois « 1 », « 2 » de RD-017) sont peu contraintes.
- Quelques fragments restent larges (« cni » laisse passer « CNIL » dans RD-017 ; « recensement » et « rei » dans RD-031 ; « répertoire » dans RD-019). Ils sont notés dans le `detail` des verdicts.
- Le rejeu par le Bac à sable (3.2) et le calcul des scores (5.3) n'existent pas encore : les cassettes ne sont vérifiées que par le lecteur de production et par le test.

Risque pour le banc (story 5.3) : les 5 demandes de valeurs exigent un `filter_column` exact (`TypeTitre`, `Code Département`…) que le modèle ne peut connaître qu'après un aperçu des données ; l'appel d'aperçu sera « non prévu » (SPEC §4), sans faire échouer l'item.
