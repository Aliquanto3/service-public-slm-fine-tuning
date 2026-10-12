---
title: 'Story 3.3 — Client MCP en direct, enregistrement et `slmsp mcp record`'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '9de2257781c5630ece9bfec10c4f8af623130190'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Le verrou client-mcp reste statique : importlib/getattr dynamiques, `from mcp import *`, `http_client=<variable None>` et arbres hors src/slmsp ne sont pas détectés.
    evidence: |-
      Écart déjà ouvert par le constat différé de 1.4 ; 3.3 ferme les imports, alias, chaînes d'attributs,
      http_client absent ou None littéral, stdio, Client et create_mcp_http_client réexporté. Fermer le reste
      demande une garde à l'exécution (net) ou une analyse de flux, hors zone.
    location: >-
      tests/test_architecture.py (_constats_client_mcp)
    severity: low
  - summary: >-
      verifier_item_libre repère un item gelé par une heuristique sur le JSON brut des MANIFEST.json, faute de schéma ManifesteJeu (story 5.1).
    evidence: |-
      ManifesteJeu n'existe pas encore dans src/. Quand 5.1 le livrera, la vérification devra lire la liste
      des items et des cassettes par ce schéma (risque : faux négatif si le manifeste nomme l'item autrement).
    location: >-
      src/slmsp/mcp/enregistrement.py (verifier_item_libre)
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** Aucun adaptateur `ToolPort` n'appelle le serveur MCP réel : le Mode connecté (4.5), les cassettes RD du Jeu d'évaluation (7.3) et les traces d'entraînement (9.4) n'ont ni client gardé, ni API d'enregistrement unique, ni commande `slmsp mcp record`. Le verrou contre les clients MCP créés hors passerelle n'existe qu'en test dans `tests/net` (constat différé de 1.1 et 1.4).

**Approach:** `McpEnDirect` (façade synchrone de `ToolPort`, SDK `mcp` 2.3.0 en Streamable HTTP, client `httpx2` asynchrone de `slmsp.net.client` injecté par `http_client=`) ouvre une session `initialize` → `tools/list` → `comparer_schema_serveur`, valide chaque appel avant envoi et retient les interactions. `enregistrer(session, magasin)` écrit la cassette dans `eval/cassettes/<ITEM>/` ou `data/cassettes/`. `cli/mcp.py` porte `record` et `sante`. Le verrou MCP passe dans ruff (TID251) et `tests/test_architecture.py`.

## Boundaries & Constraints

**Always:**
- Zone : `src/slmsp/mcp/{direct,enregistrement}.py`, `src/slmsp/cli/mcp.py`, `tests/mcp/{test_direct,test_enregistrement,test_cli_mcp,serveur_mcp_factice}.py`, plus diff minimal signalé dans `pyproject.toml` (bans TID251) et `tests/test_architecture.py` (règle `client-mcp`).
- `mcp` (couche 1b) n'importe que `slmsp.core`, `slmsp.net`, `slmsp.budget`, le SDK `mcp` et `anyio` ; jamais `httpx`/`httpx2` (classer les exceptions httpx par le nom de classe de leur MRO, modules `httpx*`).
- Client HTTP : toujours `net.client(profil, lib="httpx2", asynchrone=True, usage="mcp", ...)`, injecté dans `streamable_http_client(url, http_client=..., terminate_on_close=False)` (le profil `outillage` refuse `DELETE`). `ClientSession(..., read_timeout_seconds=delais.mcp)` ; `initialize()` (handshake, jamais `server/discover`).
- Un appel non conforme (`valider_appel`) n'est jamais envoyé ; `record` valide tous les appels et vérifie l'item libre avant toute connexion.
- Cassette : `tools_list_sha256` = celui de `config/outils-mcp.toml` ; seules les interactions `tools/call` y figurent ; écrite par `ecrire_cassette` (jamais d'écrasement).
- Tests sans réseau sauf un test marqué `reseau` ; fixtures factices (`"<reponse-factice-…>"`) ; `eval/**` jamais modifié ; aucune cassette produite sous `eval/` par les tests.

**Never:**
- Modifier `src/slmsp/net/**`, `src/slmsp/core/**`, `src/slmsp/mcp/{outils,cassettes,erreurs}.py`, `config/**`, `tests/net/**`, `eval/**`.
- Utiliser `mcp.Client`, `ClientSessionGroup`, `mcp.client.sse`, `create_mcp_http_client`, ou `streamable_http_client` sans `http_client=`.
- Implémenter le rejeu (3.2), le repli ou `ModeSonde` (4.3).
- Lire `eval/` depuis une fonction du magasin `data`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Connexion | serveur factice exposant le `tools/list` du calibrage | requêtes `initialize` puis `tools/list` ; journal `envoyee` ; `lister_outils()` = `charger_outils()` | — |
| Schéma dérivé | serveur dont un des 5 outils manque ou change | aucune `tools/call` envoyée | `SchemaOutilModifie` à l'entrée du contexte |
| Appel | `appeler("search_datasets", {"query": "x"})` | `{"jsonrpc": "2.0", "id": n, "result": {content, structuredContent, isError}}`, retenu pour la cassette | — |
| Non conforme | `appeler("get_metrics", {})`, `{"query": 3}` | aucune requête HTTP | `AppelNonConforme` |
| Délai | outil plus lent que `delais.mcp` | — | `DelaiDepasse` |
| Erreur HTTP | statut 503 sur le POST `tools/call` | — | `ErreurHttp`, `statut == 503` |
| Injoignable | transport qui lève une erreur de connexion | — | `Injoignable` |
| Erreur JSON-RPC | le serveur répond 200 avec `error` | réponse `{"jsonrpc", "id", "error"}` renvoyée et retenue | — |
| Hôte refusé | profil `assistant`, Mode `hors-ligne-force` | aucune requête émise | `HoteBloque` |
| Magasin eval | session (item `RD-007`, id `s1`) | `eval/cassettes/RD-007/s1.json` relu par `lire_cassette` | — |
| Item gelé | `eval/jeu/v1.0/MANIFEST.json` cite `RD-007` | rien d'écrit | `ItemGele` |
| Manifeste illisible | `MANIFEST.json` non JSON | rien d'écrit | `ManifesteInvalide` |
| Fichier existant | même chemin déjà écrit | fichier inchangé | `ArtefactExistant` |
| Magasin data | session id `abc` | `data/cassettes/abc.json` ; aucun accès à `eval/` | — |
| Identifiant fautif | item ou session vide, avec `/`, `\`, `..` ; item absent pour `eval` | rien d'écrit | `ValueError` |
| record simulé | `--simulation erreur_http --statut 503` | cassette `initialize: null`, une interaction par appel avec `simulation`, `response: null` ; zéro requête | — |
| Fichier d'appels fautif | JSON invalide, pas une liste, clé inconnue | code 2, rien d'écrit | message sans trace |
| sante | `GET /health` → 200 | ligne « joignable » ; code 0 ; délai 3 s | non 2xx ou panne → code 1 |

</intent-contract>

## Code Map

- `src/slmsp/net/client.py:58` -- `client(profil, lib, asynchrone, mode, journal, transport_interne, *, usage, config, liste_blanche)` : `usage="mcp"` → délai 10 s, `"sonde"` → 3 s ; `assistant` exige `mode`. Le client expose `event_hooks` (crochet de réponse pour relever le statut HTTP).
- `src/slmsp/net/config.py` -- `charger_config_reseau()` → `delais.mcp`, `delais.sonde`, `sonde.url` (`https://mcp.data.gouv.fr/health`).
- `config/reseau.toml` -- `outillage` : POST `mcp.data.gouv.fr`, GET Liste blanche ; pas de DELETE.
- `src/slmsp/net/journal.py:93` -- `JournalMemoire` pour les tests.
- `src/slmsp/mcp/outils.py` -- `charger_config(chemin).tools_list_sha256`, `charger_outils`, `valider_appel(nom, arguments, *, chemin)`, `comparer_schema_serveur(tools, *, chemin)`.
- `src/slmsp/mcp/cassettes.py` -- `ecrire_cassette` (`open("xb")` → `ArtefactExistant`), `lire_cassette`.
- `src/slmsp/mcp/erreurs.py` -- `DelaiDepasse`, `ErreurHttp(statut=)`, `Injoignable`.
- `src/slmsp/core/schemas/cassette.py` -- `Cassette`, `Interaction`, `Simulation`, `TypeSimulation`.
- `src/slmsp/core/erreurs.py` -- `SlmspError`, `ManifesteInvalide`, `HoteBloque`, `CodeSortie`.
- `src/slmsp/core/config.py:36` -- `racine_projet()`.
- `src/slmsp/cli/__init__.py` -- registre : `slmsp.cli.mcp.enregistrer(sous_parseurs)` ; `SlmspError` → code de sortie.
- SDK (`.venv/Lib/site-packages/mcp`) -- `mcp.client.streamable_http.streamable_http_client(url, *, http_client, terminate_on_close)` produit `(lecture, ecriture)` ; `mcp.client.session.ClientSession(lecture, ecriture, read_timeout_seconds=)` ; erreurs `mcp.shared.exceptions.MCPError` (`code` : `-32001` délai, `-32603` « Server returned an error response » sur statut ≥ 400, `CONNECTION_CLOSED`) ; une erreur de transport httpx sort en `ExceptionGroup`. Serveur factice : `mcp.server.lowlevel.server.Server(nom, on_list_tools=, on_call_tool=)`, `.streamable_http_app(json_response=, transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))`, `session_manager.run()` obligatoire ; `call_tool` exige `structuredContent` quand l'outil a un `outputSchema`.
- `eval/calibrage/cassettes/tools-list.json` -- LECTURE SEULE : outils du serveur factice.
- `tests/net/test_client.py:374` -- `verrou_mcp` à reprendre (motifs fautifs) dans `test_architecture.py`.
- `tests/test_architecture.py:92,225,463` -- `REGLES`, `analyser`, `CAS_FAUTIFS`, `CAS_RUFF`.
- `tests/conftest.py` -- garde réseau autouse, levée par le marqueur `reseau`.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/mcp/enregistrement.py` -- `SessionMcp` (dataclass figée : `cassette`, `session_id`, `item`), `nouvel_identifiant_session()`, `verifier_item_libre(item, *, racine)`, `ItemGele(SlmspError)`, `session_de_panne(appels, type, *, statut, item, session_id, serveur, chemin_outils)`, `enregistrer(session, magasin, *, racine=None) -> Path` -- API unique AD-10.
- `src/slmsp/mcp/direct.py` -- `URL_SERVEUR`, `McpEnDirect` (context manager ; portail `anyio.from_thread.start_blocking_portal` ; `lister_outils`, `appeler`, `session(item=, session_id=)`), traduction des erreurs, `ResultatSante` et `sonder_sante(...)` -- adaptateur direct de `ToolPort`.
- `src/slmsp/cli/mcp.py` -- `enregistrer(sous_parseurs)` : `mcp record --item --appels [--simulation] [--statut] [--session]`, `mcp sante`.
- `tests/mcp/serveur_mcp_factice.py` -- serveur bas niveau en processus (outils du calibrage, comportements : lent, statut HTTP sur le n-ième POST, outil retiré, erreur JSON-RPC), lancement paresseux de `session_manager.run()` dans la boucle de la requête, exposé en `transport_interne` (`httpx2.ASGITransport`, `# noqa: TID251`).
- `tests/mcp/test_direct.py`, `tests/mcp/test_enregistrement.py`, `tests/mcp/test_cli_mcp.py` -- couvrir la matrice ; test `reseau` de `slmsp mcp record` réel (un appel `search_datasets`) écrit sous `tmp_path` (`racine_projet` remplacé), plus `mcp sante` réel.
- `pyproject.toml` -- bans TID251 : `mcp.client.sse`, `mcp.client.session_group`, `mcp.ClientSessionGroup`, `mcp.shared._httpx_utils`, `mcp.Client`, `mcp.client.Client`, `mcp.client.client`.
- `tests/test_architecture.py` -- règle `client-mcp` (imports interdits ci-dessus, `mcp.client.streamable_http` hors du paquet `mcp`, `streamable_http_client` sans `http_client=` ou avec `None`) ; cas fautifs et cas ruff.

**Acceptance Criteria:**
- Given `uv run pytest` et `uv run ruff check`, when on les lance, then tout passe sans réseau, y compris `test_architecture.py` et ses nouveaux cas.
- Given `uv run pytest -m reseau tests/mcp`, when le serveur réel répond, then `slmsp mcp record` écrit une cassette relue par `lire_cassette` sous un dossier temporaire et `slmsp mcp sante` sort en 0.
- Given `git status` après les tests, then rien sous `eval/` n'a changé.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 40 findings — high 0, medium 3, low 33, false 3, maybe-false 1
- findings:
  - `[low]` `[patch]` (blind) `create_mcp_http_client` réexporté par `mcp.client.streamable_http` échappe au verrou — nom importé de `MCP_NOMS_INTERDITS` signalé, ban ruff ajouté, cas fautif et cas ruff.
  - `[low]` `[reject]` (blind) Chaîne d'attributs `mcp.client.streamable_http.streamable_http_client` hors `slmsp/mcp/` non signalée — contournement délibéré ; l'appel exige toujours `http_client=` ; fermer demande une branche de plus.
  - `[low]` `[patch]` (blind) Transport stdio ni banni ni signalé (AD-10 : Streamable HTTP seul) — `mcp.client.stdio` et `mcp.stdio_client` ajoutés aux interdits et aux bans ruff, avec cas.
  - `[medium]` `[patch]` (blind) Item gelé contournable sous Windows (casse, point final) — `_IDENTIFIANT` refuse le point final (fullmatch), comparaison casefold ; tests `rd-007`, `RD-007.`.
  - `[low]` `[reject]` (blind) Pagination `tools/list` tronquée après 20 pages sans erreur — le serveur expose 10 outils sur une page ; garde supplémentaire pour un cas improbable.
  - `[low]` `[reject]` (blind) Statut HTTP non rattaché à sa requête ; 400 avec corps JSON-RPC traité en `ErreurHttp` — POST parasite dans la fenêtre improbable (liste vidée à chaque appel) ; un 4xx serveur traité en panne (repli) reste défendable ; correctif = branches supplémentaires.
  - `[low]` `[patch]` (blind) Bords de `McpEnDirect` : appels `client()` positionnels, exceptions avalées à la fermeture, fuite du client si le portail échoue — arguments nommés et `except Exception` appliqués ; la fuite (échec du portail lui-même) est rejetée comme improbable.
  - `[low]` `[reject]` (blind) `--simulation erreur_http` sans `--statut` accepté — conforme au contrat `Simulation` de 3.1 (`statut` facultatif) ; le rejeu lève `ErreurHttp(statut=None)`.
  - `[low]` `[reject]` (blind) `record` sort en 0 sur erreur JSON-RPC enregistrée ; panne au k-ième appel sans rang cité — comportement voulu par la matrice (erreur JSON-RPC enregistrée) ; le message cite déjà l'outil en erreur JSON-RPC.
  - `[low]` `[patch]` (blind) Chemins non testés (double entrée, erreur JSON-RPC à l'ouverture, etc.) — tests `test_double_entree`, `test_erreur_jsonrpc_a_l_initialize`, `test_tools_list_lent` ajoutés ; le reste (4xx sur `tools/list`, groupe imbriqué, 3xx sonde) rejeté comme faible valeur.
  - `[low]` `[reject]` (blind) Doublon `_charger_factice`, tâche du serveur factice non déclarée — cosmétique de test, refactor sans effet.
  - `[medium]` `[patch]` (verification-gap) `terminate_on_close=False` jamais vérifié (serveur factice sans état) — option `avec_session` et `test_session_avec_identifiant_jamais_de_delete` (aucun DELETE au serveur ni au journal).
  - `[low]` `[patch]` (verification-gap) Pagination de `tools/list` jamais exercée — option `taille_page` et `test_tools_list_pagine` (curseurs `None, 3, 6, 9`).
  - `[low]` `[patch]` (verification-gap) Erreur JSON-RPC et délai à l'ouverture non testés — `test_erreur_jsonrpc_a_l_initialize` (`Injoignable`), `test_tools_list_lent` (`DelaiDepasse`).
  - `[low]` `[reject]` (edge) Pagination au-delà de `_PAGES_MAX` — même racine que la ligne « blind » correspondante ; rejet.
  - `[low]` `[reject]` (edge) Statut d'une POST étrangère attribué à l'appel — même motif que la ligne « blind » ; rejet.
  - `[low]` `[reject]` (edge) 400 avec corps JSON-RPC non enregistré — repli défendable, branches supplémentaires.
  - `[low]` `[reject]` (edge) `MCPError` fabriquée par le SDK (202, redirection, type de contenu) enregistrée comme réponse — cas absents du serveur data.gouv ; branches supplémentaires.
  - `[low]` `[reject]` (edge) `ValidationError` d'un `CallToolResult` malformé remonte brute — serveur conforme au SDK ; garde supplémentaire.
  - `[low]` `[reject]` (edge) Feuille d'exception inconnue à l'ouverture remonte brute — même racine ; improbable.
  - `[low]` `[reject]` (edge) Délai httpx égal au délai de session : survie de la session aléatoire après délai — les deux chemins donnent `DelaiDepasse` ; le repli (4.3) suit dans les deux cas.
  - `[low]` `[patch]` (edge) Ctrl-C avalé par `_fermer` — `except Exception` au lieu de `BaseException`.
  - `[low]` `[reject]` (edge) Client HTTP non fermé si le portail échoue avant la tâche — échec du démarrage d'un portail anyio improbable ; garde supplémentaire.
  - `[low]` `[patch]` (edge) `session()` rend une cassette après un échec d'ouverture (schéma refusé) — `_initialize` et `_interactions` remis à zéro ; assertion dans `test_schema_derive`.
  - `[medium]` `[patch]` (edge) Item gelé contournable par casse ou point final sous Windows — même racine que la ligne « blind » ; même correctif.
  - `[low]` `[reject]` (edge) Noms réservés Windows (`CON`, `NUL`) acceptés — usage improbable pour un id d'item ; garde supplémentaire.
  - `[low]` `[patch]` (edge) Manifeste citant `eval/cassettes/RD-007` sans barre finale non détecté — correspondance « se termine par `cassettes/<item>` » ajoutée, testée.
  - `[low]` `[reject]` (edge) `session_de_panne` avec itérateur ou liste vide — signature `Sequence` ; la CLI refuse la liste vide.
  - `[low]` `[reject]` (edge) Copie superficielle des arguments dans `requete_appel` — la cassette est construite et revalidée aussitôt ; mutation ultérieure par l'appelant improbable.
  - `[low]` `[patch]` (edge) `--session ''` remplacé en silence — test `is not None`, cas `session-vide` (code 2).
  - `[low]` `[reject]` (edge) `from mcp import *` contourne la règle — délibéré ; garde supplémentaire.
  - `[low]` `[patch]` (edge) stdio non banni — même racine que la ligne « blind » ; même correctif.
  - `[low]` `[defer]` (edge) Contournements dynamiques (importlib, getattr, variable None) — écart préexistant (constat 1.4), voir `deferred`.
  - `[low]` `[patch]` (intent) `slmsp.mcp.enregistrer` (nom d'AD-10) ne résout pas — réexport de `enregistrer` et `SessionMcp` dans `slmsp/mcp/__init__.py`, test `test_api_unique_reexportee`.
  - `[false]` `[reject]` (intent) Réponse « telle quelle » reconstituée par le SDK, ids renumérotés — le contenu est le message JSON-RPC parsé, réémis avec `exclude_unset` ; le test réel montre `result` complet ; les ids sont remplacés au rejeu (AD-10).
  - `[maybe-false]` `[defer]` (intent) Gel détecté par heuristique faute de `ManifesteJeu` — à confronter au schéma de 5.1 ; voir `deferred`.
  - `[low]` `[reject]` (intent) AC4 vérifiée par un test dynamique seulement — le module `data` n'a qu'une fonction de chemin, sans lecture ; une règle AST ajouterait une couche pour un seul site.
  - `[false]` `[reject]` (intent) Passerelle exercée par serveur factice seulement — les tests `reseau` passent contre le serveur réel par le même client gardé.
  - `[low]` `[defer]` (intent) Constat différé traité en partie — même racine que la ligne « edge » des contournements dynamiques.
  - `[false]` `[reject]` (intent) `pyproject.toml` et `test_architecture.py` hors zone — autorisés explicitement par l'invocation (diff minimal signalé).

## Design Notes

**Façade synchrone.** `ToolPort` est synchrone ; la session asynchrone vit dans un portail anyio (un fil, une boucle) ouvert par `__enter__` et fermé par `__exit__`. Chaque `appeler` passe par `portail.call`.

**Réponse et ids.** `appeler` renvoie la réponse JSON-RPC reconstituée du message du SDK (`model_dump(mode="json", by_alias=True, exclude_unset=True)`) ; c'est la même forme que `response` dans la cassette et que la réponse vide de 3.2. Les `id` sont renumérotés par l'enregistreur (1 `initialize`, 2 `tools/list`, puis 3, 4…) : le rejeu les remplace.

**Erreurs.** Un statut HTTP ≥ 400 relevé par le crochet pendant l'appel → `ErreurHttp(statut)` ; `MCPError` délai ou exception httpx `*Timeout*` → `DelaiDepasse` ; connexion fermée ou erreur réseau httpx → `Injoignable` ; `HoteBloque` et `SchemaOutilModifie` remontent tels quels.

**Item gelé.** `ManifesteJeu` (5.1) n'existe pas encore : un item est gelé si une chaîne du JSON d'un `eval/jeu/*/MANIFEST.json` égale l'id, une clé l'égale, ou une chaîne contient `cassettes/<ID>/` ; manifeste illisible → refus.

## Verification

**Commands:**
- `uv run pytest tests/mcp tests/test_architecture.py -q` -- expected: tout passe.
- `uv run pytest -q` -- expected: suite verte.
- `uv run ruff check` -- expected: aucun diagnostic.
- `uv run pytest -m reseau tests/mcp -q` -- expected: tests réels passent.
- `git status --short eval/` -- expected: vide.

## Auto Run Result

Status: done

**Résumé.** `McpEnDirect` est l'adaptateur direct de `ToolPort`. C'est une façade synchrone sur un portail anyio, avec le SDK `mcp` 2.3.0 en Streamable HTTP.
- Le client `httpx2` asynchrone vient de `slmsp.net.client(..., usage="mcp")` et il est injecté par `http_client=`, avec `terminate_on_close=False`.
- La session enchaîne `initialize`, `tools/list` (paginé) puis `comparer_schema_serveur`.
- Chaque appel est validé avant envoi.
- Les pannes donnent `DelaiDepasse`, `ErreurHttp(statut)` ou `Injoignable`.
- `slmsp.mcp.enregistrer(session, magasin)` écrit dans `eval/cassettes/<ITEM>/<session>.json` ou dans `data/cassettes/<session_id>.json`. Le magasin `eval` refuse un item gelé.
- La CLI porte `slmsp mcp record` (en direct ou `--simulation`) et `slmsp mcp sante`.
- Le constat différé de 1.1 et 1.4 est traité par des bans TID251 et une règle `client-mcp`.

**Fichiers.**
- `src/slmsp/mcp/direct.py` : `McpEnDirect`, traduction des erreurs, `sonder_sante`.
- `src/slmsp/mcp/enregistrement.py` : `SessionMcp`, `enregistrer`, `verifier_item_libre`, `ItemGele`, `session_de_panne`, `chemin_cassette`.
- `src/slmsp/mcp/__init__.py` : réexport de `enregistrer` et `SessionMcp` (nom d'AD-10).
- `src/slmsp/cli/mcp.py` : `mcp record`, `mcp sante`.
- `tests/mcp/serveur_mcp_factice.py` : serveur bas niveau en processus. Options : sans état ou avec session, pagination, lenteurs, statut HTTP, erreurs JSON-RPC.
- `tests/mcp/test_direct.py`, `test_enregistrement.py`, `test_cli_mcp.py` : matrice complète, plus 2 tests `reseau`.
- `pyproject.toml` (hors zone, diff minimal) : bans TID251 du SDK MCP (sse, session_group, `_httpx_utils`, Client, stdio, `create_mcp_http_client` réexporté).
- `tests/test_architecture.py` (hors zone, diff minimal) : règle `client-mcp`, cas fautifs et cas ruff.

**Revue.** 40 constats.
- 13 lignes corrigées (patch), dont 2 entrées medium : contournement de l'item gelé sous Windows, et DELETE jamais vérifié en session avec état.
- 3 lignes différées : contournements dynamiques du verrou, et heuristique de gel en attendant `ManifesteJeu`.
- 24 rejetées, dont 3 false. Les motifs sont dans le Review Triage Log.

**Revue de suivi recommandée : oui.** Deux entrées medium ont été corrigées en une seule passe, sans revue indépendante :
- la normalisation des identifiants et la comparaison insensible à la casse de `verifier_item_libre` ;
- le chemin avec session (flux GET SSE, absence de DELETE), exercé seulement par le serveur factice.

Corrigés par verdict : medium 2 entrées, low 11 lignes.

**Vérification.**
- `uv run pytest -q` : 1152 passés, 117 ignorés (préexistants), 2 désélectionnés (`reseau`).
- `uv run ruff check` et `ruff format --check` : propres.
- `uv run pytest -m reseau tests/mcp` : 2 passés contre `mcp.data.gouv.fr`. Le record réel écrit sous `tmp_path`.
- `git status --short eval/` : vide.
- Aucune dépense d'API payante.

**Décisions prises seul.**
- `appeler` renvoie la réponse JSON-RPC reconstituée par le SDK (`exclude_unset`). Les `id` sont renumérotés : 1 `initialize`, 2 `tools/list`, puis 3 et suivants.
- Seules les interactions `tools/call` vont dans la cassette. `tools_list_sha256` est celui de la config.
- Les erreurs JSON-RPC sont renvoyées et enregistrées. Les pannes de transport ne sont pas enregistrées.
- `send_request` remplace `call_tool`, pour éviter la revalidation `outputSchema` côté client.
- Une session est morte après une panne de transport fatale. Elle survit à un délai dépassé ou à un HTTP ≥ 400.
- Pas de DELETE (`terminate_on_close=False`), parce que le profil `outillage` le refuse.
- Un item gelé est repéré par heuristique (égalité, `cassettes/<ID>/`, insensible à la casse) en attendant `ManifesteJeu` (5.1).
- Format du fichier d'appels : `[{"nom", "arguments"}]`. Options `--statut` et `--session` ajoutées.
- Identifiants : `[A-Za-z0-9_.-]`, sans point final ni `..`.
- `ItemGele` sort en code 1, `ManifesteInvalide` en code 4.

**Risques résiduels.**
- Le flux GET SSE est seulement traversé, sans assertion directe.
- Un statut HTTP ≥ 400 relevé pendant un appel est attribué à cet appel.
- Le verrou MCP reste statique.
- Le gel par heuristique est à aligner sur `ManifesteJeu`.
