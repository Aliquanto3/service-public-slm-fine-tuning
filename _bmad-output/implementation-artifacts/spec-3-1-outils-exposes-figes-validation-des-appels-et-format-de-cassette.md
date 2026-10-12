---
title: 'Story 3.1 — Outils exposés figés, validation des appels et format de cassette'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '08766f0921d24db346bba19f227e021ea389e94d'
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

**Problem:** Le Harnais, le générateur Mistral et l'entraînement n'ont pas encore de schémas d'outils data.gouv figés, ni de validation des appels avant envoi, ni de format de cassette unique : un appel non conforme pourrait partir, une dérive du serveur passerait inaperçue, et les cassettes du calibrage, du jeu et des données divergeraient (FR-7, NFR-9, AD-8, AD-10).

**Approach:** Figer les 5 outils autorisés dans `config/outils-mcp.toml`, à partir du `tools/list` enregistré au calibrage, avec son empreinte. Exposer `charger_outils`, `valider_appel` et `comparer_schema_serveur` dans `slmsp.mcp.outils`, un modèle `Cassette` versionné et un module de lecture et d'écriture des cassettes qui accepte les cassettes héritées du calibrage.

## Boundaries & Constraints

**Always:**
- Zone de fichiers : `config/outils-mcp.toml`, `src/slmsp/mcp/{outils,cassettes,erreurs}.py`, `src/slmsp/core/schemas/cassette.py`, `tests/mcp/`. Rien d'autre, sauf le fichier de spec.
- `mcp` (couche 1b) n'importe que `slmsp.core` (pas `net`, pas `harness`) et aucune bibliothèque lourde ; `jsonschema` et `pydantic` sont déjà au socle.
- Les 5 noms autorisés sont exactement `search_datasets`, `get_dataset_info`, `list_dataset_resources`, `query_resource_data`, `get_resource_info`.
- Descriptions des outils : celles du serveur, recopiées telles quelles après `strip()`. Claude ne rédige aucune description ni aucun exemple (D1.1 : ces schémas entrent dans les prompts du générateur et les traces d'entraînement).
- `tools_list_sha256` = SHA-256 (hex minuscule) de `json_canonique(tools)`, où `tools` est la liste `result.tools` de la réponse `tools/list`.
- Erreurs : `AppelNonConforme` et `SchemaOutilModifie` de `slmsp.core.erreurs` ; `ArtefactExistant` de `slmsp.core.artefacts` pour le refus d'écrasement ; JSON canonique via `slmsp.core.canonique`.
- Fichiers écrits en UTF-8, fins de ligne LF.
- Tests sans réseau ; fichiers de `eval/` lus seulement, jamais modifiés.

**Never:**
- Modifier `eval/**`, `src/slmsp/core/erreurs.py`, `core/config.py`, `core/ports.py`, ou tout fichier hors zone.
- Implémenter le rejeu (3.2), le client en direct, `enregistrer` ou la CLI (3.3), ou quoi que ce soit dans `net/`.
- Ajouter un outil hors des 5, ou écrire des Données d'entraînement réalistes dans les fixtures.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Outils chargés | `config/outils-mcp.toml` réel | 5 dicts `{"type":"function","function":{name,description,parameters}}` ; `tools_list_sha256` égal à l'empreinte de `eval/calibrage/cassettes/tools-list.json` | — |
| Config fautive | outil hors des 5, doublon, plus de 5 outils, `parametres` qui n'est pas un JSON Schema valide, clé inconnue | refus au chargement | `ConfigurationInvalide` |
| Appel conforme | `valider_appel("search_datasets", {"query": "x", "page_size": 5})` | retourne `None` | — |
| Type faux | `{"query": 3}` | refus | `AppelNonConforme` dont le message cite le chemin et le message jsonschema ; attributs `nom`, `details` (liste de chaînes) |
| Requis absent / argument inconnu | `{}` ou `{"query": "x", "inexistant": 1}` | refus | `AppelNonConforme` |
| Outil inconnu | `valider_appel("get_metrics", {})` ou arguments non-dict | refus | `AppelNonConforme` |
| Serveur identique | `tools` de `tools-list.json` | retourne `None` (les 5 outils non exposés sont ignorés) | — |
| Outil inconnu ajouté côté serveur | liste réelle + un outil `nouveau` | retourne `None` | — |
| Outil absent / schéma changé | un des 5 retiré, ou son `inputSchema` modifié | refus | `SchemaOutilModifie` ; attribut `ecarts` (tuple de chaînes « `<nom>` : absent du serveur » / « `<nom>` : schéma modifié »), tous les écarts listés |
| Cassette héritée | `R-001.json`, `R-002.json` (sans `schema_version`) | `Cassette` avec `schema_version=1` et `tools_list_sha256` calculé depuis le `tools-list.json` du même dossier ; fichiers `eval/` inchangés (octets et mtime) | — |
| Héritée sans voisin | cassette sans `schema_version` dans un dossier sans `tools-list.json`, ou portant déjà `tools_list_sha256` | refus | `CassetteInvalide` |
| Cassette illisible | JSON invalide, champ manquant, clé inconnue | refus, message citant le fichier et les clés (jamais les valeurs) | `CassetteInvalide` |
| Écriture | `Cassette` valide, chemin libre (parents créés) | JSON UTF-8 LF avec `schema_version` et `tools_list_sha256` ; relu à l'identique par `lire_cassette` | — |
| Simulation | interaction `simulation={"type":"erreur_http","statut":503}`, `response=None` | écrite avec `"response": null` ; pas de clé `simulation` sur les interactions normales | — |
| Simulation incohérente | `simulation` avec `response` non nul, ni `simulation` ni `response`, `statut` hors `erreur_http` ou hors 100–599, type inconnu, `tools_list_sha256` absent ou non hex-64 | refus de construction | `pydantic.ValidationError` (modèle) |
| Écrasement | chemin existant | fichier inchangé | `ArtefactExistant` |

</intent-contract>

## Code Map

- `src/slmsp/core/erreurs.py` -- LECTURE SEULE : `SlmspError`, `AppelNonConforme`, `SchemaOutilModifie`, `ConfigurationInvalide` (pas d'attributs : poser `nom`, `details`, `ecarts` sur l'instance après construction).
- `src/slmsp/core/artefacts.py:77` -- LECTURE SEULE : `ArtefactExistant` à réutiliser ; `Run.ecrire` (l. 284) montre le motif `open("xb")` → `ArtefactExistant`.
- `src/slmsp/core/canonique.py` -- `json_canonique`, `sha256_hex` à réutiliser.
- `src/slmsp/core/config.py` -- `charger_toml(chemin, modele)`, `ModeleConfig` (extra=forbid, vérifié récursivement), `racine_projet()` → `config/outils-mcp.toml`.
- `src/slmsp/core/schemas/__init__.py` -- `SchemaBase` (extra=forbid + `schema_version`), `SousSchema`, `Sha256`.
- `src/slmsp/core/ports.py:94` -- `ToolPort.lister_outils()` attend le format `tools` OpenAI : `charger_outils` le produit.
- `eval/calibrage/cassettes/tools-list.json` -- LECTURE SEULE : cassette au format calibrage dont l'unique interaction est `tools/list` ; 10 outils, dont les 5 exposés. `inputSchema` contient `title`, `default: null`, `anyOf [{type:string},{type:null}]` (null non représentable en TOML).
- `eval/calibrage/cassettes/R-001.json`, `R-002.json` -- LECTURE SEULE : clés `server`, `recorded_at` (ISO avec fuseau), `initialize` (réponse JSON-RPC), `interactions[{request, response}]` ; écrits en indent 1, CRLF.
- `tests/test_architecture.py` -- couches (`mcp` = 2, runtime) : ne pas importer `net`, `harness` ni bibliothèque lourde dans `mcp`.
- `tests/conftest.py` -- garde réseau autouse ; rien à ajouter.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/mcp/erreurs.py` -- créer `ErreurTransportMcp(SlmspError)` avec `type_simulation: ClassVar[str]`, et ses sous-classes `DelaiDepasse` (`delai_depasse`), `ErreurHttp` (`erreur_http`, attribut `statut: int | None`), `Injoignable` (`injoignable`) ; `PAR_TYPE_SIMULATION` (type → classe) ; `CassetteInvalide(SlmspError)` -- exceptions partagées par les deux adaptateurs de `ToolPort` (3.2, 3.3).
- `src/slmsp/core/schemas/cassette.py` -- créer `Simulation(SousSchema)` (`type: Literal[...]`, `statut: int | None`, 100–599, seulement pour `erreur_http`), `Interaction(SousSchema)` (`request: dict`, `response: dict | None`, `simulation: Simulation | None`, cohérence response/simulation), `Cassette(SchemaBase)` (`schema_version: Literal[1]`, `server: str`, `recorded_at: AwareDatetime`, `initialize: dict | None`, `tools_list_sha256: Sha256`, `interactions: list[Interaction]`) -- format unique AD-10 ; `initialize` nul permis pour les cassettes de panne écrites sans réseau (3.3).
- `src/slmsp/mcp/cassettes.py` -- créer `empreinte_tools_list(tools)`, `extraire_tools_list(donnees)` (réponse de l'interaction `tools/list` → `result.tools`, sinon `CassetteInvalide`), `lire_cassette(chemin) -> Cassette` (héritée si pas de `schema_version`, cf. matrice), `ecrire_cassette(cassette, chemin) -> Path` (`json.dumps(indent=1, ensure_ascii=False)` + `\n`, `open("xb")`, parents créés, `simulation`/`statut` omis quand nuls, `response` toujours présent) -- lecture et écriture au format du calibrage.
- `config/outils-mcp.toml` -- créer : `schema_version = 1`, `source` (chemin de `tools-list.json`), `tools_list_sha256`, et 5 tables `[[outils]]` (`nom`, `description`, `sha256_schema_serveur` = SHA de `json_canonique(inputSchema)` du serveur, `parametres`) ; `parametres` = `inputSchema` du serveur sans aucun `title`, sans `default` nul, avec `additionalProperties = false` à la racine -- produire le fichier par un script jetable du scratchpad, pas à la main.
- `src/slmsp/mcp/outils.py` -- créer `OUTILS_AUTORISES`, le modèle `ConfigOutilsMcp(ModeleConfig)` (validation : ≤ 5, noms autorisés et uniques, `parametres` valide selon `Draft202012Validator.check_schema`), `charger_config(chemin=None)`, `charger_outils(chemin=None) -> list[dict]` (copies), `valider_appel(nom, arguments, *, chemin=None) -> None`, `comparer_schema_serveur(tools, *, chemin=None) -> None` -- AD-8 ; cache par chemin résolu permis.
- `tests/mcp/test_outils.py` -- couvrir les lignes « Outils », « Config fautive », « Appel », « Serveur » de la matrice ; vérifier aussi que chaque `parametres` du TOML réel égale la simplification du `inputSchema` de `tools-list.json` et que chaque description égale celle du serveur après `strip()` ; configs fautives écrites dans `tmp_path`.
- `tests/mcp/test_cassettes.py` -- couvrir les lignes « Cassette », « Écriture », « Simulation », « Écrasement » de la matrice ; empreinte SHA-256 + mtime de tout `eval/calibrage/cassettes/*` avant/après ; cassettes synthétiques dans `tmp_path` avec des textes factices (`"<réponse-factice-1>"`).

**Acceptance Criteria:**
- Given le dépôt après la story, when on lance `uv run pytest` et `uv run ruff check`, then tout passe, y compris `tests/test_architecture.py`, sans aucun accès réseau.
- Given `charger_outils()`, when on passe le résultat à `jsonschema.Draft202012Validator.check_schema` pour chaque `parameters`, then aucun schéma n'est rejeté, et les arguments de toutes les interactions `tools/call` de `R-001.json` et `R-002.json` passent `valider_appel`.
- Given un `git status` après les tests, when on l'inspecte, then aucun fichier sous `eval/` n'est modifié.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 28 findings — high 0, medium 1, low 21, false 6, maybe-false 0
- findings:
  - `[low]` `[patch]` (verification-gap) Branche non UTF-8 de `_lire_json` jamais testée — ajout de `test_fichier_non_utf8` (`b"\xff\xfe{"` → `CassetteInvalide` citant le chemin).
  - `[low]` `[patch]` (verification-gap, autre) `valider_appel(None, …)` posait `nom == "None"` alors que l'évènement attend `str | None` — `_refus` pose `nom` brut si chaîne, sinon `None` ; test `test_nom_non_chaine`.
  - `[low]` `[reject]` (edge-case) `NaN`/`Infinity` acceptés par `json.loads` à la lecture — le serveur MCP émet du JSON standard, sans ces constantes ; correctif = garde supplémentaire pour un cas improbable.
  - `[low]` `[reject]` (edge-case) `tools-list.json` voisin non canonisable → `ValueError` brute — même cause improbable (fichier enregistré par le client JSON-RPC) ; garde supplémentaire.
  - `[low]` `[reject]` (edge-case) Écriture interrompue → fichier tronqué qui bloque toute réécriture — panne disque rare ; même motif que `core.artefacts.Run.ecrire` ; correctif = garde/rollback.
  - `[low]` `[reject]` (edge-case) `$ref` non résoluble accepté par `check_schema` — la config est produite par script depuis le serveur et ne contient aucun `$ref`.
  - `[low]` `[reject]` (edge-case) Cache périmé si réécriture de même taille dans la résolution du mtime — NTFS a une résolution de 100 ns ; cas irréaliste.
  - `[low]` `[reject]` (edge-case) Messages `AppelNonConforme` contenant les valeurs d'arguments — la matrice exige le message jsonschema ; ce sont des arguments d'outil, pas des secrets.
  - `[low]` `[reject]` (edge-case) Nom d'outil en double côté serveur : seule la première entrée compte — MCP impose des noms uniques ; garde supplémentaire.
  - `[false]` `[reject]` (edge-case) `tools` nul ou dict → `TypeError` ou tous absents — échec bruyant (`TypeError` ou `SchemaOutilModifie` complet) sur une entrée hors contrat (`Sequence`) ; comportement correct.
  - `[false]` `[reject]` (intent) Empreinte du `tools/list` complet plutôt que des 5 outils exposés — AD-8 dit « empreinte du `tools/list` enregistré » ; la dérive outil par outil est couverte par `sha256_schema_serveur`.
  - `[false]` `[reject]` (intent) Durcissement `additionalProperties = false` hors des cas listés par l'AC2 — l'AC2 n'interdit pas d'autres refus ; les appels réels de R-001/R-002 passent ; choix consigné en Design Notes.
  - `[low]` `[reject]` (intent) Changement de `description` côté serveur non détecté — NFR-9 porte sur les schémas ; la description figée reste valide pour l'appel ; ajout d'un champ et d'une branche.
  - `[false]` `[reject]` (intent) Repli, journal et évènement `AppelNonConforme` non branchés — la story 3.1 s'arrête aux exceptions ; le branchement relève de 3.2/3.3/4.3.
  - `[false]` `[reject]` (intent) Spec et contexte d'epic non suivis, sprint-status non mis à jour — la spec est commise à la finalisation ; le sprint-status est tenu par l'orchestrateur.
  - `[false]` `[reject]` (blind) Aucune empreinte de ce que voit le modèle — les manifestes en aval inscrivent le SHA du fichier `outils-mcp.toml` (AD-7), qui change à toute édition ; la cassette porte l'empreinte du `tools/list` comme le veut AD-8.
  - `[low]` `[reject]` (blind) Dérive des descriptions non détectée — même racine que la ligne « intent » correspondante ; rejet pour la même raison.
  - `[low]` `[reject]` (blind) `OutilFige` n'impose ni `additionalProperties = false` ni `type = "object"` — le test sur la config réelle garde ces invariants ; ajout de validations.
  - `[low]` `[reject]` (blind) Valeurs d'arguments non tronquées dans les messages — même racine que la ligne « edge-case » ; exigé par la matrice.
  - `[low]` `[patch]` (blind) `ecrire_cassette` écrivait une cassette mutée ou `model_construct` sans revalidation, fichier illisible et non réécrivable — revalidation `Cassette.model_validate(cassette.model_dump())` avant encodage ; test `test_ecriture_revalide_une_cassette_mutee`.
  - `[low]` `[reject]` (blind) Écriture non atomique — même racine que la ligne « edge-case » ; rejet.
  - `[low]` `[reject]` (blind) `Interaction.request` sans contrainte (`method`) — cassettes écrites par notre enregistreur ; contrainte à poser si 3.2 en a besoin.
  - `[low]` `[reject]` (blind) Interaction `tools/list` propre à une cassette non confrontée à son empreinte — cas absent des cassettes réelles (seul `tools-list.json` en porte une) ; branche supplémentaire.
  - `[low]` `[reject]` (blind) Script générateur de la config non versionné — la règle de simplification est écrite en en-tête du TOML et vérifiée par `_simplifier` du test ; régénérer après dérive est une décision à part.
  - `[low]` `[reject]` (blind) Paramètres énumérés typés `string` libre ; descriptions évoquant un « fetch » direct — simplification fidèle au serveur ; consigné en risque résiduel.
  - `[low]` `[reject]` (blind) `_CACHE` sans éviction et sans test d'invalidation — la config change rarement ; quelques entrées en test.
  - `[low]` `[patch]` (blind) Cas de test manquants — ajoutés : non UTF-8, voisin sans `tools/list`, nom non chaîne ; rejetés : BOM (refus bruyant correct) et contenu des messages déjà couverts ailleurs.
  - `[medium]` `[patch]` (orchestrateur, vérification) `test_config_reelle_lf_utf8` exigeait l'absence de `\r` alors que le dépôt a `core.autocrlf=true` sans `.gitattributes` : la suite échouerait après checkout ailleurs — assertion `\r` retirée (tomllib normalise CRLF), test renommé `test_config_reelle_utf8`.

## Design Notes

**Empreinte.** `tools_list_sha256` empreinte le `tools/list` complet dont les schémas figés sont tirés (référence de provenance). Une cassette porte l'empreinte de la config sous laquelle elle a été enregistrée ; 3.2 refusera toute autre valeur. La dérive du serveur se détecte, elle, outil par outil via `sha256_schema_serveur`, ce qui laisse libre la simplification exposée au modèle et ignore les outils non exposés.

**Simplification minimale.** On retire seulement ce que TOML ne sait pas porter (`null`) ou qui n'aide pas le modèle (`title`), et on ajoute `additionalProperties = false` pour qu'un paramètre halluciné soit refusé avant envoi. Exemple pour `query_resource_data.filter_column` :

```toml
[outils.parametres.properties.filter_column]
anyOf = [{ type = "string" }, { type = "null" }]
```

**Cassette héritée.** Un fichier sans `schema_version` est au format brut du calibrage ; son empreinte vient du `tools-list.json` voisin. La lecture n'écrit jamais rien.

## Verification

**Commands:**
- `uv run pytest tests/mcp -q` -- expected: tous les tests passent.
- `uv run pytest -q` -- expected: suite complète verte (ou échecs préexistants hors zone listés).
- `uv run ruff check` -- expected: aucun diagnostic.
- `git status --short eval/` -- expected: vide.

## Auto Run Result

Status: done

**Résumé.** Les 5 outils data.gouv autorisés sont figés dans `config/outils-mcp.toml`. Le fichier a été produit par script depuis `eval/calibrage/cassettes/tools-list.json` : descriptions du serveur, schémas sans `title` ni `default` nul, `additionalProperties = false`, `tools_list_sha256` = `38bdeb31…5b15`, plus un SHA par outil. `slmsp.mcp.outils` expose `charger_config`, `charger_outils` (format `tools` OpenAI), `valider_appel` (jsonschema → `AppelNonConforme`, attributs `nom`, `details`) et `comparer_schema_serveur` (→ `SchemaOutilModifie`, attribut `ecarts`). Le format unique de cassette `Cassette` (schema_version 1) est lu et écrit par `slmsp.mcp.cassettes`, qui accepte aussi les cassettes héritées du calibrage. Les exceptions de transport sont partagées par les deux adaptateurs.

**Fichiers.**
- `config/outils-mcp.toml` : outils figés, empreintes.
- `src/slmsp/core/schemas/cassette.py` : `Simulation`, `Interaction`, `Cassette`.
- `src/slmsp/mcp/erreurs.py` : `ErreurTransportMcp`, `DelaiDepasse`, `ErreurHttp(statut)`, `Injoignable`, `PAR_TYPE_SIMULATION`, `CassetteInvalide`.
- `src/slmsp/mcp/cassettes.py` : `empreinte_tools_list`, `extraire_tools_list`, `lire_cassette`, `ecrire_cassette`.
- `src/slmsp/mcp/outils.py` : `OUTILS_AUTORISES`, `ConfigOutilsMcp`, chargement avec cache, validation, comparaison.
- `tests/mcp/test_outils.py` et `tests/mcp/test_cassettes.py` : 64 tests, fixtures factices.

**Revue.** 28 constats.
- 5 entrées corrigées : 1 medium (test LF incompatible avec autocrlf) et 4 low (non UTF-8, nom non chaîne, revalidation avant écriture, tests manquants).
- 0 différé.
- 23 rejetés, motifs dans le Review Triage Log : 6 false et 17 low improbables ou exigés par la matrice.

**Revue de suivi recommandée : non.** Une seule entrée medium corrigée, aucune high.

**Vérification.**
- `uv run pytest tests/mcp -q` : 64 passed.
- `uv run pytest -q` : 769 passed, 29 skipped.
- `uv run ruff check` : propre.
- `git status --short eval/` : vide.

**Décisions prises seul.**
- `tools_list_sha256` empreinte le `result.tools` complet. La dérive se détecte outil par outil, par le SHA de `inputSchema`.
- Durcissement `additionalProperties = false`.
- `schema_version` est écrit sur disque. Son absence marque une cassette héritée, dont l'empreinte vient du `tools-list.json` voisin.
- `initialize` peut être nul (cassette de panne écrite sans réseau).
- `statut` n'est permis que pour `erreur_http`, entre 100 et 599.
- La config porte de 1 à 5 outils.
- En cas de doublon côté serveur, la première entrée compte.

**Risques résiduels.**
- Les paramètres énumérés (`filter_operator`, `sort_direction`, `sort`, `last_update_range`) restent des chaînes libres.
- Les descriptions du serveur évoquent un téléchargement direct d'URL, que le modèle ne peut pas faire.
- Un changement de description côté serveur n'est pas détecté.
- La story 3.2 devra ajouter un champ à `ConfigOutilsMcp`, qui refuse les clés inconnues, pour le texte de la réponse vide.
