---
title: 'Story 1.4 — Passerelle réseau unique (profils, Liste blanche, journal des Requêtes sortantes)'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '9c241e197bcdce59dcde874ec28c65f2f2a68a17'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Le verrou contre les clients MCP créés hors passerelle n'existe que comme test AST dans tests/net, limité à src/slmsp ; ni ban ruff, ni règle de tests/test_architecture.py, ni garde à l'exécution.
    evidence: |-
      Suite du constat différé de la story 1.1. pyproject.toml et tests/test_architecture.py sont hors de la zone de 1.4
      (consignes de la nuit). Restent ouverts : Client(variable_str), getattr/importlib dynamiques, http_client=<variable None>,
      arbres hors src/slmsp (eval/outils exclu de TID251 par choix). À verrouiller par la story 3.3 (mcp/direct.py, seul site
      légitime) ou 9.x : ban TID251 de mcp.shared._httpx_utils, mcp.client.sse, mcp.client.session_group, et règle AST dans
      test_architecture.py reprenant verrou_mcp.
    location: >-
      tests/net/test_client.py (verrou_mcp) ; pyproject.toml [tool.ruff.lint.flake8-tidy-imports.banned-api]
    severity: medium
---

<intent-contract>

## Intent

**Problem:** aucun client HTTP gardé n'existe : rien n'empêche encore un hôte hors liste, une requête en Mode hors ligne forcé ou une requête non journalisée, et les stories 2.1, 2.2, 3.3 et 5.4 n'ont pas de client à injecter dans les SDK. Constat différé de 1.1 : le SDK `mcp` sait créer son propre client `httpx2` (`streamable_http_client(url)` sans `http_client=`, `mcp.Client("https://…")`), hors passerelle.

**Approach:** créer `slmsp.net` (couche 1a) : une fabrique unique `client(profil, …)` dont le transport gardé vérifie profil, Mode et Liste blanche avant le transport interne, journalise chaque requête dans un `JournalRequetes` SQLite (`SLMSP_VAR_DIR`), et lit `config/reseau.toml` et `config/liste-blanche.toml` ; plus `client_local(port)`, `fabrique_hf()` et un verrou AST (dans `tests/net/`) contre les clients MCP créés hors passerelle. Exactement les 8 critères de la story 1.4 d'`epics.md`.

## Boundaries & Constraints

**Always:**
- Zone : `src/slmsp/net/{__init__,profils,client,transport,journal,config}.py`, `src/slmsp/core/schemas/journal_requetes.py`, `config/reseau.toml`, `config/liste-blanche.toml`, `tests/net/`.
- `net` n'importe que la bibliothèque standard, `pydantic`, `httpx2` (socle), `httpx` en import paresseux dans une fonction (absent du socle, extra `train`) et `slmsp.core.*`. Jamais `harness`, `budget`, `mcp`, `huggingface_hub`.
- Tout refus (`HoteBloque`, de `core.erreurs`) a lieu avant tout appel au transport interne et est journalisé ; tout client est créé avec `trust_env=False` (sinon un proxy d'environnement monté par httpx court-circuite le transport gardé).
- HTTPS seulement et port par défaut (443) pour `assistant` et `outillage` ; adresse IP refusée ; nom d'hôte normalisé (minuscules, point final retiré) puis comparé exactement (`assistant`) ou par règle (`outillage`).
- Entrée de journal : exactement `horodatage` (ISO 8601 avec fuseau), `profil`, `hote`, `methode`, `outil`, `termes`, `statut`, `mode` ; ni URL complète, ni en-têtes, ni corps hors `termes`, ni secret.
- Tests : transports internes factices (`MockTransport`) qui comptent leurs appels ; journal dans `tmp_path` ; aucun réseau réel ; variante `httpx` sautée par `pytest.importorskip` si le paquet est absent.

**Never:**
- Ne pas modifier `pyproject.toml`, `uv.lock`, `tests/conftest.py`, `tests/test_architecture.py`, `core/` hors `core/schemas/journal_requetes.py`, ni `eval/` (stories 7.2 et 7.4 en parallèle).
- Pas d'implémentation de `ModeSonde`/`ModeFixe` (Epic 4) : doublures dans les tests. Pas de client MCP, anthropic, mistralai (3.3, 5.4, 5.5). Pas de relance automatique (`retries=0`).
- Aucun appel réseau, aucun téléchargement de paquet supplémentaire.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Liste blanche | `assistant`, Mode `connecte`, `GET https://www.data.gouv.fr/x`, `https://MCP.DATA.GOUV.FR./mcp` | transport interne appelé, entrée `envoyee` | — |
| Hors liste | `mcp.data.gouv.fr.exemple.com`, `evil-data.gouv.fr`, `https://1.2.3.4/`, `https://[::1]/`, `http://www.data.gouv.fr/`, `https://www.data.gouv.fr:8443/`, `https://mcp.data.gouv.fr@evil.com/` | transport interne jamais appelé, entrée `bloquee-liste` | `HoteBloque` (code 1) citant profil, méthode, hôte |
| Hors ligne forcé | `ModePort` → `hors-ligne-force` ; `GET https://mcp.data.gouv.fr/health` ou toute requête | jamais appelé, entrée `bloquee-mode` | `HoteBloque` |
| Hors ligne détecté | Mode `hors-ligne-detecte` ; sonde `GET <sonde.url>` ; autre requête | sonde : `envoyee` ; autre : `bloquee-mode` | `HoteBloque` pour l'autre |
| Appel d'outil | POST JSON-RPC `{"method":"tools/call","params":{"name":"search_datasets","arguments":{"q":"x"}}}` | entrée `outil="search_datasets"`, `termes='{"q":"x"}'` (JSON canonique) | corps illisible ou autre méthode → `outil=None`, `termes=None` |
| Échec réseau | transport interne lève `ConnectError` | entrée `echouee` | exception relancée telle quelle |
| `outillage` lecture | GET/HEAD `huggingface.co`, `cas-bridge.xethub.hf.co`, `cdn-lfs.huggingface.co`, `pypi.org`, `files.pythonhosted.org`, `github.com`, `objects.githubusercontent.com`, `download.pytorch.org`, hôte de la Liste blanche, `GET https://legal.mistral.ai/terms/commercial-terms-of-service` | `envoyee`, `mode=None` | — |
| `outillage` POST | `api.mistral.ai`, `api.anthropic.com`, `mcp.data.gouv.fr` | `envoyee` | — |
| `outillage` refus | POST `huggingface.co` ; GET `api.mistral.ai` ; GET autre chemin de `legal.mistral.ai` ; HEAD page Mistral ; `evil-huggingface.co` ; DELETE partout | jamais appelé, `bloquee-liste` | `HoteBloque` |
| `aucun` | toute requête | jamais appelé, `bloquee-liste` | `HoteBloque` |
| Redirection | `follow_redirects=True`, 302 de `www.service-public.fr` vers `www.service-public.gouv.fr` puis vers `evil.com` | 2 entrées `envoyee`, puis `bloquee-liste` ; transport interne appelé 2 fois | `HoteBloque` au 3e saut |
| Local | `client_local(8080)` : `http://127.0.0.1:8080/v1/x` ; `:8081`, `localhost`, `https://example.org` | passe ; autres refusés sans appel | `HoteBloque` ; port hors 1–65535 → `ValueError` |
| Arguments | profil inconnu, `lib="requests"`, `assistant` sans `mode` | — | `ValueError` |
| Config | TOML avec clé inconnue, hôte IP ou `*.x`, méthode inconnue, règle dans `aucun` | — | `ConfigurationInvalide` (via `core.config.charger_toml`) |

</intent-contract>

## Code Map

- `src/slmsp/core/erreurs.py` -- lecture seule ; `HoteBloque(SlmspError)` (code 1), `ConfigurationInvalide` existent déjà.
- `src/slmsp/core/ports.py` -- lecture seule ; `Mode` (`connecte`, `hors-ligne-detecte`, `hors-ligne-force`), protocoles `NetGate.client(profil)` + `verifier(profil, methode, url, *, outil=None, termes=None)`, `ModePort.mode_courant()`, `JournalRequetes.inscrire(entree)` + `lister(limite=None)`.
- `src/slmsp/core/config.py` -- `charger_toml(chemin, modele)`, `ModeleConfig` (`extra="forbid"`), `racine_projet()` (racine des `config/*.toml`).
- `src/slmsp/core/var.py` -- `dossier_var()`, `ouvrir_sqlite(chemin)` (WAL, `busy_timeout` 30 s).
- `src/slmsp/core/canonique.py` -- `json_canonique(obj) -> bytes` pour `termes`.
- `src/slmsp/core/schemas/__init__.py` -- `SchemaBase` (`extra="forbid"`, `schema_version`), sans réexport.
- `tests/conftest.py` -- lecture seule ; garde réseau autouse (DNS et connexions hors boucle locale), `SLMSP_VAR_DIR` temporaire par test.
- `tests/test_architecture.py` -- lecture seule ; `net` couche 1a, seul paquet autorisé à importer `httpx`/`httpx2` ; doit continuer à passer.
- `.venv/Lib/site-packages/httpx2` -- API identique à httpx (`BaseTransport.handle_request`, `AsyncBaseTransport.handle_async_request`, `MockTransport`, `HTTPTransport(retries=0)`) ; les redirections du client repassent par le transport à chaque saut.
- `.venv/Lib/site-packages/mcp/client/streamable_http.py:713` -- `streamable_http_client(url, http_client: httpx2.AsyncClient | None)` ; sans client, `create_mcp_http_client()` (`mcp/shared/_httpx_utils.py:32`) crée un client non gardé ; `mcp/client/client.py:399` (`Client(str)`) et `session_group.py:320-337` aussi.
- `huggingface_hub` 2.2.0 (extra `fetch`, absent du venv) -- `set_client_factory(f)` / `set_async_client_factory(f)` attendent une fonction sans argument renvoyant `httpx2.Client` / `AsyncClient` ; la fabrique par défaut fixe `follow_redirects=True`, `timeout=None`.
- Page des conditions de Mistral (D-nuit-A2-10) : `https://legal.mistral.ai/terms/commercial-terms-of-service` (note de cadrage).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/schemas/journal_requetes.py` -- `StatutRequete` (Literal des 4 statuts), `ProfilReseau` (Literal `assistant`, `outillage`, `aucun`), `EntreeJournalRequetes(SchemaBase)` figée : `schema_version: Literal[1]=1`, `horodatage: AwareDatetime`, `profil`, `hote`, `methode`, `outil: str|None`, `termes: str|None`, `statut`, `mode: Mode|None`.
- `src/slmsp/net/config.py` -- modèles `ModeleConfig` : `Delais` (`defaut=30`, `mcp=10`, `sonde=3`, `local=600`, > 0), `Sonde(url)` (https), `Regle(nom, methodes, hotes=[], suffixes=[], chemins=[])`, `ConfigProfil(liste_blanche_en_lecture=False, regles=[])`, `Profils(outillage, aucun)` (`aucun` sans règle ni lecture), `ConfigReseau(delais, sonde, profils)`, `ConfigListeBlanche(hotes)` ; hôtes validés et normalisés (`normaliser_hote` de `profils.py`) ; `charger_config_reseau(chemin=None)`, `charger_liste_blanche(chemin=None)` (défaut `racine_projet()/config/…`).
- `src/slmsp/net/profils.py` -- `PROFILS`, `normaliser_hote`, `est_adresse_ip`, `Verdict` (statut bloquant + motif, ou autorisé) et `evaluer(profil, methode, url, *, mode, config, liste_blanche) -> Verdict` : contrôle du Mode d'abord (forcé : tout refusé ; détecté : seule la sonde), puis schéma/port/IP, puis Liste blanche (`assistant`), règles (`outillage`), refus total (`aucun`).
- `src/slmsp/net/journal.py` -- `NOM_JOURNAL = "requetes-sortantes.sqlite"`, `JournalSqlite(chemin=None)` (table `requetes` aux 8 colonnes exactement, `PRAGMA user_version = 1`, connexion par opération via `ouvrir_sqlite`, `lister` du plus récent au plus ancien), `JournalMemoire` (doublure pour les tests des stories suivantes), `extraire_appel_outil(contenu: bytes) -> (outil, termes)`.
- `src/slmsp/net/transport.py` -- `Garde` (profil, mode, journal, config, liste blanche) : `controler(requete)` journalise et lève `HoteBloque`, `consigner(requete, statut)` ; `transport_garde(lib, asynchrone, garde, interne)` construit la sous-classe de `BaseTransport`/`AsyncBaseTransport` du module `lib` qui contrôle puis délègue, journalise `envoyee` ou `echouee` ; `transport_local(...)` (seul `http://127.0.0.1:<port>`, sans journal).
- `src/slmsp/net/client.py` -- `client(profil, lib="httpx2", asynchrone=False, mode=None, journal=None, transport_interne=None, *, usage=None, config=None, liste_blanche=None, follow_redirects=False)` (`usage` ∈ {`mcp`, `sonde`, None} → délai ; `assistant` exige un `mode`) ; `client_local(port, …)` ; `fabrique_hf()` et `fabrique_hf_async()` (profil `outillage`, `follow_redirects=True`) ; `Passerelle` (implémente `NetGate`).
- `src/slmsp/net/__init__.py` -- réexporte `client`, `client_local`, `fabrique_hf`, `fabrique_hf_async`, `Passerelle` (`slmsp.net.client(profil)` d'AD-4).
- `config/reseau.toml`, `config/liste-blanche.toml` -- valeurs de la matrice (règles Hugging Face par hôtes et suffixes `huggingface.co`/`hf.co`, PyPI, GitHub + suffixe `githubusercontent.com`, `download.pytorch.org`, page Mistral GET seul, POST vers les 3 hôtes ; Liste blanche §B à 8 hôtes ; sonde `https://mcp.data.gouv.fr/health`).
- `tests/net/test_profils.py` -- critères 2, 3, 5, 6 et lignes « config » de la matrice, sur les vrais TOML et sur des TOML de `tmp_path`.
- `tests/net/test_client.py` -- critères 1 et 8, `client_local`, `fabrique_hf`, `trust_env`, arguments invalides, variantes `httpx2`/`httpx` et sync/async ; verrou AST sur `src/slmsp` : aucune référence à `create_mcp_http_client`, `ClientSessionGroup`, `mcp.client.sse` ; tout appel `streamable_http_client(...)` porte `http_client=` ; `Client(...)` importé de `mcp` jamais appelé avec une URL littérale ; auto-test du verrou sur du code synthétique.
- `tests/net/test_journal.py` -- critère 4 : colonnes exactes, aller-retour, extraction `tools/call`, absence d'en-tête `Authorization`, de corps et de chaîne de requête dans la base, fichier dans `SLMSP_VAR_DIR` par défaut.
- `tests/net/test_redirections.py` -- critère 7.

**Acceptance Criteria:**
- Given la story terminée, when `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, then tout passe, y compris `tests/test_architecture.py`.
- Given chaque scénario de refus de la matrice, when la requête est émise par le client (sync et async), then le compteur du transport interne factice reste à 0 et le journal contient une entrée bloquée.
- Given `client("assistant", asynchrone=True, usage="mcp", mode=…)`, when on l'inspecte, then c'est un `httpx2.AsyncClient` au délai de 10 s, injectable dans `streamable_http_client(http_client=…)`.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 38 findings — high 0, medium 6, low 31, false 1, maybe-false 0
- findings (verification gap) :
  - `[low]` `[reject]` (VG-1) Variante `httpx` (78 cas) et `set_client_factory` sautés dans le venv par défaut — vérifiés hors venv : `uv run --with httpx==0.28.1 --with huggingface-hub==2.2.0 pytest tests/net` → 322 passés, 0 sauté ; un environnement de test `train`/`fetch` dépasse la story.
  - `[medium]` `[patch]` (VG-autre) Mode hors Literal traité comme connecté : requête partie puis `ValidationError` au journal — `lire_mode` ferme : `bloquee-mode`, `mode=None`, `HoteBloque` chaînée ; tests sync/async, httpx2/httpx.
- findings (blind) :
  - `[low]` `[reject]` (B1) `assistant` sans restriction de méthode — le MCP exige POST, GET et DELETE ; PUT/PATCH vers ces hôtes publics en lecture seule n'a pas d'effet ; une liste par méthode ajoute une règle.
  - `[low]` `[reject]` (B2) `fabrique_hf` et `outillage` ignorent le Mode forcé — le Mode est celui de l'Assistant (FR-10, AD-4 : « requête du profil `assistant` ») ; l'outillage n'a pas de Mode ; critère 3 tenu.
  - `[low]` `[patch]` (B3) `Passerelle.verifier` : `termes` non sérialisables → `TypeError` sans journal — repli `termes=None` ; test.
  - `[low]` `[reject]` (B4) Une panne du journal remplace l'issue d'origine — rare (disque plein, verrou 30 s) ; échec bruyant, requête bloquée non envoyée, exception d'origine conservée dans `__context__`.
  - `[low]` `[reject]` (B5) Écriture SQLite synchrone dans le transport async — quelques ms hors contention ; un seul processus MCP ; `to_thread` change l'ordre des entrées.
  - `[medium]` `[patch]` (B6) `mode_courant()` qui lève : ni entrée ni `HoteBloque` — même cause que VG-autre.
  - `[low]` `[reject]` (B7) URL de sonde non recoupée avec la Liste blanche — configuration livrée cohérente (testée) ; un contrôle croisé ajoute une branche.
  - `[low]` `[reject]` (B8) `termes` non bornés, non expurgés, sans rétention — imposé par le critère 4 ; arguments d'outils data.gouv sans secret ; rétention de 30 jours en J4 (`app.stockage`).
  - `[low]` `[reject]` (B9) Requêtes GET avec chaîne de requête libre (page Mistral, suffixes) — menace d'exfiltration hors modèle ; la page reste la seule permise sur l'hôte.
  - `[low]` `[reject]` (B10) Ni CA ni proxy configurables — httpx2 lit le magasin du système (truststore) ; aucun proxy requis cette nuit.
  - `[low]` `[patch]` (B11) `JournalMemoire.lister(-1)` diffère de `JournalSqlite` — `ValueError` ; test.
  - `[low]` `[patch]` (B12) `PROFILS` duplique `ProfilReseau` — `get_args(ProfilReseau)` ; reste (contrôles répétés, `methode: str`) rejeté : cosmétique.
  - `[low]` `[patch]` (B13) Verrou MCP contournable par alias — alias de `streamable_http_client` et `from mcp.client import client` suivis ; 2 cas fautifs ; le reste (dynamique, autres arbres) différé avec I1.
  - `[low]` `[reject]` (B14) Hygiène des tests (doublures redéfinies, attributs privés, variantes `client_local`) — cosmétique ; la restauration `default_client_factory` existe dans huggingface_hub 2.2.0 (test passé hors venv).
- findings (edge) :
  - `[medium]` `[patch]` (E1) Mode inconnu accepté (fail-open) — même cause que VG-autre.
  - `[medium]` `[patch]` (E2) Requête envoyée sans entrée de journal (mode invalide) — même cause que VG-autre.
  - `[medium]` `[patch]` (E3) `mode_courant()` qui lève avant le journal — même cause que VG-autre.
  - `[low]` `[reject]` (E4) Erreur SQLite masque `HoteBloque` — même raison que B4.
  - `[low]` `[reject]` (E5) Boucle async bloquée par le journal — même raison que B5.
  - `[low]` `[patch]` (E6) `verifier` et `termes` NaN — même correctif que B3.
  - `[low]` `[reject]` (E7) Sonde hors Liste blanche — même raison que B7.
  - `[low]` `[patch]` (E8) Suffixe d'un seul label (`co`) ouvre un TLD — deux labels exigés ; tests.
  - `[low]` `[patch]` (E9) Délai `inf` accepté — `Field(gt=0, allow_inf_nan=False)` ; tests `inf`, `nan`.
  - `[low]` `[reject]` (E10) `transport_interne` sync/async inversé → `AttributeError` — paramètre de test, erreur bruyante.
  - `[low]` `[patch]` (E11) `JournalMemoire` limite négative — même correctif que B11.
  - `[low]` `[reject]` (E12) Base `user_version 0` avec une table étrangère — fichier propre à la passerelle ; cas improbable.
  - `[low]` `[reject]` (E13) Lot JSON-RPC sans `outil` — le SDK MCP n'envoie pas de lots.
  - `[low]` `[patch]` (E14) Alias de `streamable_http_client` non suivi — même correctif que B13.
  - `[low]` `[patch]` (E15) `from mcp.client import client as c` non détecté — même correctif que B13.
  - `[low]` `[reject]` (E16) HF sort en Mode forcé — même raison que B2.
  - `[low]` `[patch]` (E17) Refus non journalisé (termes non sérialisables) — même correctif que B3.
- findings (intent alignment) :
  - `[medium]` `[defer]` (I1) Verrou MCP en test seulement, sans ban ruff ni règle `test_architecture.py` ni garde runtime — fichiers hors zone (consignes) ; voir `deferred`.
  - `[low]` `[reject]` (I2) Injection dans les SDK vérifiée à l'API seulement — httpx et `set_client_factory` exécutés hors venv (322 passés) ; une session MCP réelle relève de 3.3.
  - `[low]` `[reject]` (I3) Mode forcé limité à l'`assistant` — même raison que B2.
  - `[low]` `[reject]` (I4) Suffixes HF et GitHub plus larges que des hôtes nommés — hôtes CDN et Xet variables ; domaines tenus par HF et GitHub ; sosies refusés (testé).
  - `[false]` `[reject]` (I5) Ni commit ni `Auto Run Result` — produits à la finalisation.
- constat de l'orchestrateur (hors décompte) : `codeload.github.com` manquait, les archives de sources GitHub (redirection 302) auraient été refusées — ajouté à la règle github ; test.

## Design Notes

- **Nom `client`.** `net/__init__.py` réexporte la fonction `client` : l'attribut `slmsp.net.client` désigne la fonction, pas le module. Importer les autres symboles par `from slmsp.net.client import …`, jamais `import slmsp.net.client as m` (qui renverrait la fonction) ; dans les tests, le module est `sys.modules["slmsp.net.client"]`.
- **Ordre des contrôles.** Mode, puis forme de l'URL, puis profil. Un hôte hors liste en Mode forcé est donc `bloquee-mode`.
- **Journal après coup.** L'entrée `envoyee`/`echouee` est écrite quand l'issue est connue (en-têtes reçus, ou exception). Une requête bloquée est écrite avant la levée.
- **Termes.** Seul le JSON-RPC `tools/call` (POST, corps déjà en mémoire, objet JSON) donne `outil` et `termes` ; le SDK MCP envoie depuis une tâche de fond, un `contextvar` n'y serait pas visible.
- **Verrou MCP.** Le SDK reste importable (`mcp.client.streamable_http` sert à 3.3) ; le verrou porte sur les points qui fabriquent un client non gardé. Les cas dynamiques (`Client(variable_str)`) restent à 3.3.

## Verification

**Commands:**
- `uv run pytest tests/net` -- expected: tout passe.
- `uv run pytest` -- expected: tout passe (sautés autorisés : liens symboliques, `duckdb`, `httpx` absent).
- `uv run ruff check` et `uv run ruff format --check` -- expected: aucun écart.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** Passerelle réseau unique `slmsp.net` (couche 1a, AD-4) :
- fabrique `client(profil, lib, asynchrone, mode, journal, transport_interne, *, usage, config, liste_blanche, follow_redirects)` ; son transport gardé contrôle chaque requête et chaque saut de redirection avant le transport interne (`retries=0`, `trust_env=False`) ;
- profils `assistant` (Liste blanche §B, nom d'hôte exact), `outillage` (règles de `config/reseau.toml`), `aucun` (tout refusé) ;
- Mode : hors ligne forcé → tout refusé ; hors ligne détecté → seule la sonde `GET https://mcp.data.gouv.fr/health` ; Mode illisible → refus (fermé) ;
- journal des Requêtes sortantes : `JournalSqlite` (`SLMSP_VAR_DIR/requetes-sortantes.sqlite`, 8 colonnes exactement), `JournalMemoire` ; `outil`/`termes` tirés du JSON-RPC `tools/call` ;
- `client_local(port)` (seul `http://127.0.0.1:<port>`), `fabrique_hf`/`fabrique_hf_async` (`huggingface_hub.set_client_factory`), `Passerelle` (implémente `NetGate`) ;
- constat différé de 1.1 : client gardé injectable dans `streamable_http_client(http_client=…)` (httpx2.AsyncClient, délai MCP 10 s) et verrou AST dans `tests/net` ; le reste est différé (voir `deferred`).

**Fichiers.**
- `src/slmsp/core/schemas/journal_requetes.py` : `StatutRequete`, `ProfilReseau`, `EntreeJournalRequetes` (figée).
- `src/slmsp/net/profils.py` : `PROFILS`, `normaliser_hote`, `est_adresse_ip`, `lire_mode`, `Verdict`, `evaluer`.
- `src/slmsp/net/config.py` : modèles de `reseau.toml` et `liste-blanche.toml`, chargeurs.
- `src/slmsp/net/journal.py` : `JournalSqlite`, `JournalMemoire`, `extraire_appel_outil`.
- `src/slmsp/net/transport.py` : `Garde`, `GardeLocale`, transports gardés httpx2/httpx, sync/async.
- `src/slmsp/net/client.py` : `client`, `client_local`, `fabrique_hf`, `fabrique_hf_async`, `Passerelle`.
- `src/slmsp/net/__init__.py` : réexport (l'attribut `slmsp.net.client` est la fonction).
- `config/reseau.toml`, `config/liste-blanche.toml`.
- `tests/net/{conftest,test_profils,test_client,test_journal,test_redirections}.py`.

**Revue** (une passe, 38 constats).
- Correctifs : 1 entrée medium (Mode illisible ou en erreur : fail-open et requête non journalisée → refus fermé), 6 entrées low (`termes` non sérialisables dans `verifier`, limite négative de `JournalMemoire`, `PROFILS` dérivé du Literal, suffixe d'un seul label, délai `inf`/`nan`, alias contournant le verrou MCP). Constat de l'orchestrateur : `codeload.github.com` ajouté.
- Différé : 1 entrée (verrou MCP à porter dans ruff/`test_architecture.py`, stories 3.3 ou 9.x).
- Rejetés : 1 faux, 23 low ; raisons au journal de tri (principales : pas de Mode pour l'outillage, journal synchrone, pas de restriction de méthode pour `assistant`, CA du système via truststore).

**Relecture de suivi recommandée : non.** Patchés : 1 medium, 6 low, 0 high.

**Vérification** (2026-10-12) :
- `uv run pytest` : 832 passés, 91 sautés (87 variante `httpx` et `huggingface_hub` absents du venv, 2 liens symboliques, 2 `duckdb`) ;
- `uv run --with httpx==0.28.1 --with huggingface-hub==2.2.0 pytest tests/net` : 322 passés, aucun saut ;
- `uv run ruff check` et `uv run ruff format --check` : propres.

**Décisions prises seul** (à reporter au journal) :
1. Toutes les méthodes sont permises vers la Liste blanche pour `assistant` (MCP : POST, GET, DELETE).
2. HTTPS et port 443 seulement ; IP (y compris formes numériques abrégées) et identifiants dans l'URL refusés.
3. `outillage` : Hugging Face et `githubusercontent.com` par suffixe (frontière de label) ; GitHub `github.com`, `api.github.com`, `codeload.github.com` ; page Mistral `https://legal.mistral.ai/terms/commercial-terms-of-service` en GET seul ; POST seulement vers `api.mistral.ai`, `api.anthropic.com`, `mcp.data.gouv.fr`.
4. Ordre des contrôles : Mode, forme de l'URL, profil. Le Mode ne s'applique que si un `ModePort` est injecté (obligatoire pour `assistant`) ; un Mode illisible bloque.
5. Journal : une entrée par requête et par saut, écrite à l'issue (`envoyee` aux en-têtes, `echouee` sur exception, `bloquee-*` avant la levée) ; horodatage UTC ; `lister` du plus récent au plus ancien ; profils `outillage` et `aucun` journalisés aussi.
6. `client_local` n'est pas journalisé (boucle locale). Délais : défaut 30 s, MCP 10 s, sonde 3 s, local 600 s.

**Risques résiduels.**
- `outillage` refuse le GET vers les API Anthropic et Mistral : le suivi des lots batch (story 5.4) exigera une règle dans `config/reseau.toml`.
- Le verrou MCP reste un test de `tests/net` (voir `deferred`).
- Journal SQLite synchrone dans le transport async ; une panne du journal remplace l'issue d'origine (bruyante).
