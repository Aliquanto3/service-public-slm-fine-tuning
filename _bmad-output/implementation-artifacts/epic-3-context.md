# Epic 3 Context: Outils data.gouv : client MCP et Bac à sable rejouable

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Donner au Harnais un accès sûr et reproductible aux outils data.gouv. On fige les 5 outils exposés au modèle, on valide chaque appel avant son envoi et on fournit deux adaptateurs interchangeables du port `ToolPort` : `McpEnDirect` appelle le serveur MCP réel par la passerelle réseau, `BacASable` rejoue des cassettes de façon déterministe, pannes simulées comprises. Le Mode connecté et la recherche de données (Epic 4) en dépendent. L'évaluation sans réseau (Epic 5), les cassettes RD du Jeu d'évaluation (Epic 7) et les traces d'entraînement (Epic 9) en dépendent aussi : ces trois usages doivent partager un seul format de cassette et une seule API d'enregistrement.

## Stories

- Story 3.1 : Outils exposés figés, validation des appels et format de cassette
- Story 3.2 : Bac à sable MCP : rejeu des cassettes
- Story 3.3 : Client MCP en direct, enregistrement et `slmsp mcp record`

## Requirements & Constraints

- **Appels d'outils contraints.** Un appel non conforme au schéma JSON n'est jamais envoyé. Chaque jeu de données affiché doit provenir d'une réponse d'outil ou de l'Index local.
- **Repli.** Si un appel MCP échoue ou dépasse son délai (10 s par défaut, réglable), le Harnais se replie sur l'Index local avec la mention « non vérifié en ligne ». Le repli lui-même relève de l'Epic 4. Cet epic fournit les exceptions typées qui le déclenchent, identiques en direct et en rejeu.
- **Robustesse des schémas.** Le schéma serveur est versionné et comparé au schéma figé. Un outil inconnu est ignoré. Un outil attendu absent ou modifié provoque le repli et une entrée de journal.
- **Bac à sable.** Les réponses sont enregistrées une fois, versionnées, puis rejouées à l'identique. Deux rejeux de la même séquence donnent des réponses identiques à l'octet près, ce qui assure la reproductibilité des évaluations.
- **Serveur réel.** `https://mcp.data.gouv.fr/mcp`, en Streamable HTTP uniquement. Il est en lecture seule, sans authentification, et sa sonde de santé est `GET /health` (délai de 3 s). Le serveur est expérimental et ses outils évoluent, d'où le schéma figé et l'empreinte.
- **Tests.** Aucun réseau par défaut. Les fichiers du calibrage (`eval/calibrage/cassettes/R-001.json`, `R-002.json`, `tools-list.json`) sont lus sans jamais être modifiés. Les cassettes synthétiques sont créées dans `tmp_path`. Le seul test réel, contre `mcp.data.gouv.fr`, est marqué `reseau`.

## Technical Decisions

- **Outils figés.** Les 5 outils exposés sont `search_datasets`, `get_dataset_info`, `list_dataset_resources`, `query_resource_data` et `get_resource_info`. Leurs schémas sont tirés du `tools/list` enregistré au calibrage et éventuellement simplifiés, par exemple en masquant des paramètres optionnels. Ils sont figés dans `config/outils-mcp.toml` avec `tools_list_sha256`. Ils sont rendus au format `tools` d'OpenAI. Ces mêmes schémas servent au Harnais, au générateur Mistral et à l'entraînement : leur SHA est inscrit dans les manifestes en aval.
- **Validation.** Elle se fait avec `jsonschema` avant tout envoi. Un échec lève `AppelNonConforme`, avec le détail. Une dérive du schéma serveur lève `SchemaOutilModifie`, avec la liste des écarts. Ces deux erreurs appartiennent à la hiérarchie `SlmspError` de `core.erreurs`.
- **Erreurs de transport.** `DelaiDepasse`, `ErreurHttp` et `Injoignable` sont définies dans `mcp/erreurs.py`. Les deux adaptateurs les partagent.
- **Format de cassette unique.** Une cassette est une session JSON-RPC par fichier, au format du calibrage : `server`, `recorded_at`, `initialize`, `interactions[{request, response}]`. Elle porte en plus `tools_list_sha256`, obligatoire à l'écriture. Une interaction peut aussi porter `simulation = {type: delai_depasse | erreur_http | injoignable, statut?}`, avec `response` nul. Les cassettes héritées du calibrage sont acceptées : leur empreinte est calculée à partir de `tools-list.json`. Le modèle pydantic `Cassette` vit dans `core/schemas/cassette.py` et porte un `schema_version`.
- **Appariement en rejeu.** On cherche d'abord le même outil avec des arguments égaux en JSON canonique (clés triées, séparateurs compacts). À défaut, on prend le même outil avec le plus de paires (clé, valeur) égales, l'égalité étant départagée par l'ordre dans la cassette. À défaut encore, on renvoie la réponse vide normalisée `{"result": {"content": [{"type": "text", "text": <texte de config>}], "isError": false}}`. Les cas 2 et 3 émettent un évènement « appel non prévu », qui n'a aucun effet sur le score. L'`id` JSON-RPC de la réponse est remplacé par celui de la requête. L'adaptateur est sans état. Une cassette dont l'empreinte diffère de la config est refusée.
- **Client direct.** Il utilise le SDK `mcp` 2.3.0 en Streamable HTTP. Le client HTTP est toujours obtenu par `net.client(..., lib="httpx2", asynchrone=True)` puis injecté. `httpx`, `httpx2` et `requests` sont interdits hors de `slmsp/net/` (ruff `TID251`). Une session commence par `initialize` puis `tools/list`, comparé au schéma figé. Les délais viennent de `config/reseau.toml`. Le profil réseau est `assistant` (Liste blanche, journal des Requêtes sortantes) ou `outillage` (enregistrement de cassettes).
- **Enregistrement.** Une seule API, `slmsp.mcp.enregistrer(session, magasin)`, gère deux magasins séparés :
  - `eval` écrit dans `eval/cassettes/<ITEM>/<session>.json`. L'écriture est refusée si l'item figure dans un manifeste gelé `eval/jeu/*/MANIFEST.json`.
  - `data` écrit dans `data/cassettes/<session_id>.json`. Aucune fonction du magasin `data` ne lit `eval/cassettes/`, pour éviter toute fuite du jeu d'évaluation vers l'entraînement.

  Dans les deux cas, un fichier existant n'est jamais écrasé : les artefacts sont immuables.
- **CLI.** Le module `cli/mcp.py` porte deux commandes. `mcp record --item <ID> --appels <fichier.json> [--simulation <type>]` utilise le profil `outillage` ; avec `--simulation`, il écrit la cassette sans aucun appel réseau. `mcp sante` lance la sonde `/health`.
- **Couches.** `mcp` appartient à la couche 1b. Il n'importe que `core`, `net` et `budget`, jamais `harness`. Il fait partie de la fermeture runtime : aucune bibliothèque lourde n'y est admise (torch, anthropic, mistralai, etc.). Le test AST `tests/test_architecture.py` le vérifie.
- **Conventions.** Le code suit les termes du domaine en français sans accents. Les fichiers sont en UTF-8 avec fins de ligne LF. Les SHA-256 sont en hexadécimal minuscule. Les tests miroir vivent sous `tests/mcp/`. Le serveur MCP factice des tests tourne en processus (partie serveur du SDK `mcp`, application ASGI) et est branché comme transport interne du client fourni par `net`.

## Cross-Story Dependencies

- **3.1** dépend de 1.3 (ports dont `ToolPort`, `core.schemas`, JSON canonique, erreurs). 3.2 et 3.3 dépendent de 3.1.
- **3.3** dépend aussi de 1.4 (passerelle `net`, profils, journal). 3.2 et 3.3 ont des zones de fichiers disjointes et peuvent tourner en parallèle, mais 3.2 ajoute le texte de la réponse vide dans `config/outils-mcp.toml`, fichier créé par 3.1.
- **En aval :**
  - 4.3 (boucle d'outils, Modes, repli) consomme `BacASable` (3.2) ;
  - 4.5 (`slmsp ask`) consomme `McpEnDirect` (3.3) ;
  - 5.1 (lecteur d'items) dépend de 3.1 ;
  - 7.3 (items RD) attend `slmsp mcp record` (3.3) pour enregistrer ses cassettes ;
  - 9.4 et 9.5 (génération et validation des données) utilisent le magasin `data` et le rejeu.
- **Ordre conseillé.** 3.1 se fait dans la vague V3, puis 3.2 et 3.3 dans la vague V6. La piste du Jeu d'évaluation attend 3.3.
