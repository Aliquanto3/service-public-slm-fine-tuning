---
title: 'Story 4.3 — Recherche de données : boucle d''outils, Modes et repli'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '154ece10ac9173e50b525e736029b6a5a7fb9b54'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Le premier tour connecté réutilise la consigne RD.md sans passages : renvoi [1] orphelin, et forme de prompt que data/train ne produisent pas encore.
    evidence: |-
      Test réel du 2026-10-12 (Qwen3 4B, RD-001 et RD-002) : les deux réponses finissent par « [1] » sans passage fourni.
      `messages_connecte` (recherche.py) applique construire_messages sur une copie de la Tâche sans l'emplacement passages.
      La correction propre est une variante `RD-connecte` dans config/prompts/taches (hors zone, décision d'Anaël, règle D1.1), à brancher aussi dans data (9.x) et train (10.x).
    location: >-
      src/slmsp/harness/taches/recherche.py (messages_connecte)
    severity: medium
  - summary: >-
      FR-38 : en RD, les arguments d'outil générés par le modèle pourraient recopier la phrase de l'Agent vers data.gouv.
    evidence: |-
      Les arguments ne sont validés que par le schéma JSON (valider_appel). Rien ne les compare aux textes saisis. Le prompt RD demande de ne pas recopier de donnée personnelle.
      Pour trancher : un test du document témoin en RD (story 4.5) et une mesure sur le banc (termes des appels comparés aux entrées).
    location: >-
      src/slmsp/harness/taches/recherche.py (_Boucle.executer)
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** La Tâche RD est déclarée (table, prompt `RD.md`, registre `MODULES_TRAITEMENT["RD"] = "recherche"`), mais son module de traitement n'existe pas : `repondre("RD", …)` lève `TacheIndisponible`. Il n'y a ni boucle d'appels d'outils, ni `ModeSonde`/`ModeFixe`, ni repli sur l'Index local. Le banc (5.3), la CLI (4.5) et l'application en dépendent.

**Approach:** `harness/taches/recherche.py` porte la boucle : passages du catalogue data.gouv de l'Index, génération avec les outils figés en Mode connecté, validation de chaque appel (`mcp.outils.valider_appel`) avant envoi par `ToolPort`, `ResultatOutil` tel que renvoyé par l'outil, et repli sur l'Index (évènement `Repli`) sur panne, Mode perdu ou schéma dérivé. `harness/modes.py` porte `ModeSonde` (sonde `GET /health` par la passerelle `net`) et `ModeFixe`.

## Boundaries & Constraints

**Always:**
- Zone : `harness/taches/recherche.py`, `harness/modes.py` et leurs tests (`tests/harness/test_recherche.py`, `test_modes.py`, `test_repli.py`, `test_integration_recherche.py`). `harness/config.py` et `config/harnais.toml` sont lus sans modification. `harness/service.py` : rien, sauf nécessité stricte signalée.
- AD-7 : le prompt vient de `construire_messages(tache, demande, passages, tools)`, puis `ctx.messages_pour(...)`. La boucle ne fait qu'ajouter les tours d'outil : `assistant` avec `tool_calls` (`inference.client.appel_canonique`) et `tool` (contenu rendu par une seule fonction publique de `recherche.py`, réutilisable par `data`/`train`).
- AD-8 : tout `AppelOutil` du modèle passe par `valider_appel` avant envoi. S'il est invalide, il devient `AppelNonConforme` (motif = détails du validateur) et `ToolPort.appeler` n'est jamais appelé pour lui. `tools` = `ctx.outils.lister_outils()` restreint à `tache.outils_autorises`.
- Ordre des tours : au plus `config.outils.iterations_max` tours d'appels, puis une dernière génération sans `tools`. Délai d'un appel : `config.outils.delai_appel_s` (dépassement → `DelaiDepasse`).
- `ResultatOutil(id=<id de l'appel du modèle>, nom, resultat=<`result` (ou `{"error": …}`) de la réponse JSON-RPC, copie exacte>, erreur=<isError ou error>)`. L'`id` JSON-RPC (toujours 3 au rejeu, report 3.2) n'entre pas dans la trace.
- Repli (FR-9) : `DelaiDepasse`, `ErreurHttp`, `Injoignable` (`ErreurTransportMcp`), `HoteBloque`, `SchemaOutilModifie`, ou Mode non connecté à la sonde d'avant appel → `ResultatOutil(erreur=True)` pour l'appel, `Repli(vers="index", motif contenant « non vérifié en ligne »)`, détail au logger `slmsp.harness` (classe et message, sans texte saisi), plus aucun outil proposé ; la réponse finale s'appuie sur les passages déjà fournis.
- Mode : `ctx.mode` absent ou `ctx.outils` absent → traité comme hors ligne. Avant chaque appel d'outil, le Mode est re-sondé (`sonder()` si le port le permet, sinon `mode_courant()`).
- Hors ligne (FR-8, NFR-5) : aucun outil passé au modèle, aucun appel à `ToolPort`, réponse sur les passages du catalogue.
- `ModeSonde` : sonde par `slmsp.mcp.direct.sonder_sante`, profil `assistant`, Mode de garde `ModeFixe("hors-ligne-detecte")` (seule la sonde passe), délai `config.modes.delai_sonde_s` ; joignable seulement si 2xx et durée ≤ délai ; exception ou doute → `hors-ligne-detecte`. Sonde à la première lecture (démarrage), quand `periode_sonde_s` est écoulée, et à chaque `sonder()`. Hors ligne forcé : aucune sonde, aucune requête. Au passage en `connecte`, `controle_schema()` (optionnel) est appelé : `SchemaOutilModifie` → `ecarts_schema` renseigné et entrée de journal (logger `slmsp.harness`, niveau WARNING) ; autre exception → doute, reste hors ligne. Un outil inconnu du serveur est ignoré (règle de `comparer_schema_serveur`).
- `ModeFixe(mode)` : renvoie toujours `mode` (valeur de `Mode`, sinon `ValueError`), `sonder()` idem, aucune requête.
- Tests sans réseau ni modèle (sauf `integration`), fixtures factices générées (D1.1), cassettes du calibrage et du jeu gelé en lecture seule, cassettes de simulation dans `tmp_path`.

**Never:**
- Modifier `core/`, `mcp/`, `net/`, `inference/`, `harness/prompts.py`, `harness/taches/__init__.py`, `harness/config.py`, `config/`, `sprint-status.yaml`, les documents de décision, ou les fichiers des stories 4.4 et 5.5.
- Tirer une valeur de tableau du texte généré ; réécrire le texte généré ; envoyer un appel non validé ; émettre une requête en hors ligne forcé.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Connecté, appels valides | `ModeFixe("connecte")`, `BacASable(R-001)`, `FakeLlm` : tour 1 `AppelOutil(search_datasets)`, tour 2 texte | `AppelOutil`, `ResultatOutil` (même id, `resultat` = `result` de la cassette), `Jeton*`, `Sources`, `Fin` ; tour 2 reçoit `[system, user, assistant(tool_calls), tool]` | — |
| Appel non conforme | `AppelOutil` avec argument hors schéma | `AppelNonConforme`, espion `ToolPort` jamais appelé | — |
| `query_resource_data` | cassette de valeurs | `ResultatOutil.resultat` identique au `result` de la cassette | — |
| Hors ligne | `ModeFixe("hors-ligne-detecte"/"hors-ligne-force")` | `tools=None`, aucun appel `ToolPort`, `Sources` (passages du catalogue), `Avertissement(code="valeurs-mode-connecte")`, `Fin` | — |
| Panne MCP | cassette `simulation` delai_depasse / erreur_http / injoignable | `ResultatOutil(erreur=True)`, `Repli`, génération suivante sans `tools`, `Avertissement`, `Fin` | log sans texte saisi |
| Mode perdu avant appel | `sonder()` → hors ligne | pas d'appel, `Repli` | — |
| Schéma dérivé | `ModeSonde.ecarts_schema` non vide | `Repli` dès le début, aucun outil, entrée de journal | — |
| Plafond | modèle qui appelle sans fin | `iterations_max` tours, puis génération sans `tools` | — |
| Sonde | transport factice 200 / 503 / exception / lent | `connecte` / `hors-ligne-detecte` ×3 | — |
| Forcé | `ModeSonde(hors_ligne_force=True)` | `hors-ligne-force`, transport jamais appelé | — |

</intent-contract>

## Code Map

- `src/slmsp/harness/taches/__init__.py` -- `ContexteTache` (`entree`, `historique`, `textes_saisis`, `llm`, `config`, `options_llm`, `recherche`, `outils`, `mode`, `messages_pour`, `resultats_outils`), `diffuser(ctx, messages, tools)` → `(texte, fin)` (relaie `AppelOutil` quand `tools` non vide, sinon le change en `AppelNonConforme`), `avertissement`. Lecture seule.
- `src/slmsp/harness/taches/question.py` -- modèle de traitement à imiter (ordre `Jeton*`, `Sources`, `Avertissement`, `Fin` avec `urls_inventees`).
- `src/slmsp/harness/service.py:224` -- passe `outils`/`mode` si `tache.outils_autorises`, `recherche` si le prompt déclare `passages` (RD : oui). Aucun changement prévu.
- `src/slmsp/harness/recherche_index.py` -- `RechercheIndex(embedder, vector_store, k, seuil)` ; attributs publics `embedder`, `vector_store`, `k`, `seuil`.
- `src/slmsp/harness/citations.py` -- `sources_citees`, `urls_inventees`, `extraire_urls`, `normaliser_url`, `extrait`.
- `src/slmsp/harness/prompts.py:217` -- `construire_messages` (passages vides → `AUCUN_PASSAGE`).
- `src/slmsp/harness/config.py` -- `config.outils.iterations_max` (5), `delai_appel_s` (10), `config.modes.periode_sonde_s` (300), `delai_sonde_s` (3).
- `src/slmsp/mcp/outils.py` -- `valider_appel` (lève `core.erreurs.AppelNonConforme` avec `.details`), `comparer_schema_serveur` (lève `SchemaOutilModifie` avec `.ecarts`), `charger_outils`.
- `src/slmsp/mcp/bac_a_sable.py` -- `BacASable(cassettes, signaler=…)` ; `appeler` renvoie `{"jsonrpc","id","result":{"content":[{"type":"text","text":…}],"isError":…}}`, lève les pannes simulées.
- `src/slmsp/mcp/erreurs.py` -- `ErreurTransportMcp`, `DelaiDepasse`, `ErreurHttp`, `Injoignable`.
- `src/slmsp/mcp/direct.py:425` -- `sonder_sante(profil, mode=, journal=, transport_interne=, config=, liste_blanche=)` → `ResultatSante(joignable, statut, detail)` ; tests : `tests/mcp/test_direct.py:376-415` (MockTransport httpx2, `JournalMemoire`).
- `src/slmsp/net/config.py` -- `ConfigReseau.delais.sonde`, `sonde.url` ; `src/slmsp/net/profils.py` : en `hors-ligne-detecte`, seule la sonde passe.
- `src/slmsp/inference/client.py:91` -- `appel_canonique(AppelOutil)` ; `nouvel_identifiant()` ; `json-generique` : `tools` → `response_format` JSON Schema, la boucle reçoit des `AppelOutil` comme en natif.
- `src/slmsp/core/ports.py` -- `Mode`, `ModePort`, `ToolPort`, `Passage` ; `core/erreurs.py` : `HoteBloque`, `SchemaOutilModifie`, `AppelNonConforme`.
- `config/index.toml` -- source du catalogue : `nom = "data-gouv-datasets-catalog"` (`Passage.source`).
- `src/slmsp/core/items.py:655,673` -- `lire_jeu("v1.0")`, `resoudre_cassettes(jeu, item)` ; items RD gelés `eval/jeu/v1.0/items.jsonl` (`RD-001`, `RD-002` : un `search_datasets`, règle `contient_un_de`) ; `core/texte.normaliser` (spec 7.3 : fragment en début de mot).
- `tests/harness/factices.py`, `conftest.py` -- `FakeLlm` (scripts par appel, enregistre messages/tools), `FakeEmbedder`, `FakeVectorStore`, `SpyToolPort`, marqueur `integration`. `tests/harness/test_integration_question.py` -- `prerequis`, `racine_index`, `config_generation` à réutiliser (Qwen3 4B : `qwen-4b`).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/harness/modes.py` -- `ModeFixe`, `ModeSonde` (`mode_courant`, `sonder`, `forcer(hors_ligne)`, `ecarts_schema`, verrou), helpers `mode_avant_appel(port)` et `ecarts_schema(port)` -- Modes FR-10, NFR-9.
- `src/slmsp/harness/taches/recherche.py` -- `traiter(ctx)`, `contenu_resultat(reponse)` (texte des `content` ou de l'erreur, rendu unique du message `tool`), `passages_catalogue(recherche, demande)` (recherche élargie à `k × FACTEUR`, filtre `source == "data-gouv-datasets-catalog"`, `k` premiers), sources MCP, constantes de motif et d'avertissement -- FR-7, FR-8, FR-9.
- `tests/harness/test_modes.py` -- sonde (transport factice : 200, 503, exception, lenteur via horloge injectée), période, forcé, contrôle de schéma (tools-list du calibrage modifié : outil retiré, schéma changé, outil inconnu ignoré), `ModeFixe`.
- `tests/harness/test_recherche.py` -- matrice connecté, non conforme, valeurs, plafond, hors ligne, URL inventées, ids d'appel dupliqués (renommés par `nouvel_identifiant`), `json-generique` : `ClientLlama(port, protocole_outils="json-generique", transport_interne=<MockTransport httpx2 servant du SSE>)` qui renvoie `{"tool_calls": [...]}` puis `{"content": ...}` ; le corps envoyé porte `response_format` et pas `tools`, et la boucle produit les mêmes évènements qu'en natif.
- `tests/harness/test_repli.py` -- pannes simulées (3 types, cassettes `tmp_path`), `HoteBloque`, Mode perdu avant appel, schéma dérivé, logs sans texte saisi.
- `tests/harness/test_integration_recherche.py` -- `lent` + `integration` : 2 items RD gelés (RD-001, RD-002), Qwen3 4B CPU en `json-generique` (décodage contraint par schéma JSON), BGE-M3 et l'Index réel, `BacASable` des cassettes gelées, `ModeFixe("connecte")` ; vérifie l'enchaînement `AppelOutil` → `ResultatOutil` (résultat de la cassette), la règle `contient_un_de` de l'appel attendu, la fin `Fin` et l'absence d'URL inventée.

**Acceptance Criteria:**
- Given le Mode connecté et des `tool_calls` valides, when la boucle tourne, then les appels passent par `ToolPort` dans l'ordre, chaque résultat est émis en `ResultatOutil`, et `Fin.urls_inventees` est vide quand le texte ne cite que des URL des résultats ou des passages (FR-7).
- Given `protocole_outils = "json-generique"`, when la boucle tourne, then elle est inchangée : seuls les `AppelOutil` produits par l'adaptateur comptent (AC 8).
- Given `uv run pytest tests/harness -m integration -k recherche`, when Qwen3 4B traite RD-001 et RD-002 contre le Bac à sable, then chaque item produit au moins un appel valide exécuté, un `ResultatOutil` égal à la cassette et un `Fin`.

## Spec Change Log

### 2026-10-12 — Passages en Mode connecté (constat du test réel)
- **Déclencheur :** test réel (AC 3) en xfail. Qwen3 4B n'appelle aucun outil, en `json-generique` comme en `natif`. Essai isolé, même modèle, même consigne RD, `tools` identiques, RD-001 : avec le bloc de passages (réels ou `AUCUN_PASSAGE`), le modèle répond sans outil. Avec la demande seule sous la même consigne, il appelle `search_datasets` dans les deux protocoles (`query` contenant « autonomie », donc règle `contient_un_de` satisfaite).
- **Amendement (Design Notes) :** en Mode connecté, le premier tour n'a pas de passages. La règle AD-14 est « MCP d'abord, puis l'Index en repli ». Le repli et le hors ligne reconstruisent les messages avec passages, sans `tools`.
- **État évité :** une boucle d'outils que le modèle n'emprunte jamais.
- **KEEP :**
  - `modes.py` entier ;
  - dans `recherche.py` : la validation `valider_appel`, `contenu_resultat`, `_resultat_de`, le délai par fil, le renommage des ids, `sources_mcp` et `sources_recherche`, les motifs et l'avertissement, le cumul d'usage, le plafond d'itérations ;
  - les tests existants, sauf ceux qui supposent des passages au premier tour connecté.

## Review Triage Log

### 2026-10-12 — Passe de revue
- verdicts : 43 constats. High 0, medium 6, low 27, false 9, maybe-false 1.
- constats :
  - **Blind Hunter**
    - `[low]` `[patch]` Un outil exposé mais non proposé passe `valider_appel` et serait envoyé. Correctif : un nom absent des `tools` du tour devient `AppelNonConforme`. Test ajouté.
    - `[medium]` `[patch]` En connecté, une réponse sans appel ne porte aucun avertissement, alors qu'elle n'est fondée ni sur MCP ni sur l'Index. Correctif : `non_verifie` vaut aussi vrai sans résultat d'outil. Test ajouté.
    - `[low]` `[patch]` En connecté sans outil autorisé, pas d'avertissement. Même correctif que le constat précédent.
    - `[false]` `[reject]` Des erreurs de `ToolPort` échapperaient au repli.
      - `lister_outils` des deux adaptateurs lit la config locale, sans réseau.
      - `McpEnDirect` traduit ses pannes en `ErreurTransportMcp` ou `HoteBloque`.
      - Une autre exception est une erreur de programmation : elle finit en `Erreur`, comme voulu par la 4.2.
    - `[low]` `[reject]` Un schéma dérivé pendant un appel n'est pas reporté au Mode, et il n'y a pas de recontrôle en restant connecté. AD-8 prévoit le contrôle « au passage en connecté ». `McpEnDirect` refuse aussi la session à l'ouverture. Les `ecarts` restés après le hors ligne ne sont lus qu'en connecté, et le contrôle suivant les remet à zéro.
    - `[low]` `[reject]` Une sonde par appel, verrou tenu, config relue. La sonde avant chaque appel est exigée par FR-10. Le verrou garantit une seule sonde à la fois.
    - `[low]` `[reject]` Le fil d'un appel hors délai continue. C'est une décision consignée : le transport a son propre délai (`delais.mcp`), et la réponse tardive est abandonnée.
    - `[low]` `[reject]` Le repli abandonne les tours vérifiés. C'est la lecture littérale de FR-9 (« répond à partir de l'Index local »), consignée dans les Design Notes. Les `ResultatOutil` restent dans la trace.
    - `[low]` `[patch]` `texte_total` colle les tours entre eux, ce qui peut fusionner une URL avec le texte suivant. Correctif : jointure par `"\n"`.
    - `[medium]` `[defer]` La consigne RD demande `[n]` sans passage au premier tour connecté, d'où le `[1]` orphelin observé. La correction passe par une variante de prompt dans `config/` (décision d'Anaël).
    - `[low]` `[patch]` Les appels identiques ne sont pas dédoublonnés (deux fois le même appel pour RD-001 au test réel). Correctif : réutilisation du résultat dans un même `traiter`. Test ajouté.
    - `[low]` `[reject]` Le filtre du catalogue s'applique après la recherche. C'est une décision consignée (`FACTEUR_RECHERCHE`). Un filtre dans le `VectorStore` changerait le port (AD-9).
    - `[false]` `[reject]` Import de `masquer` depuis `service`. `service` n'importe pas `recherche` (chargement paresseux) : pas de cycle.
    - `[false]` `[reject]` Le test réel réimplémente `contient_un_de` et ses gardes. Le scoreur du banc (5.3) n'existe pas encore. RD-001 et RD-002 ont un seul appel obligatoire et des réponses en succès.
    - `[low]` `[patch]` Les décisions `isError` et réponse malformée ne sont pas testées. Groupé avec le constat Verification Gap n°1.
    - `[low]` `[reject]` Le document de spec n'est pas à jour. Le correctif serait une modification de la spec.
  - **Verification Gap**
    - `[medium]` `[patch]` Les réponses d'erreur JSON-RPC et `isError` ne sont jamais passées dans la boucle. Ajout de `test_resultat_en_erreur_sans_repli` (2 formes).
    - `[low]` `[patch]` Un `AppelNonConforme` de l'adaptateur sans texte n'est pas testé. Test ajouté.
    - `[medium]` `[patch]` Réponse connectée sans appel ni avertissement : doublon du constat Blind Hunter n°2, même correctif.
    - `[low]` `[patch]` Connecté sans outil, sans avertissement : doublon du constat Blind Hunter n°3.
  - **Intent Alignment**
    - `[medium]` `[defer]` Le premier tour connecté a une forme de prompt que `data`/`train` ne produisent pas encore. `messages_connecte` est publique, mais la parité reste à brancher (9.x et 10.x), et la variante `RD-connecte` est à décider.
    - `[low]` `[reject]` AC1 est contrôlé au niveau des URL et non des jeux. `urls_inventees` est le mécanisme unique de la 4.2. Reconnaître un titre cité sans URL demanderait une heuristique fragile.
    - `[false]` `[reject]` Pas de tableau rendu. AD-14 et l'UX placent le rendu dans la CLI (4.5) et l'application, depuis `ResultatOutil`, qui est copié à l'identique.
    - `[low]` `[reject]` Le branchement de `controle_schema` est hors du diff. Il relève de la racine de composition (4.5). L'API et la règle sont livrées et testées.
    - `[maybe-false]` `[defer]` FR-38 : les arguments d'outil, générés par le modèle, pourraient recopier la phrase de l'Agent. Pour trancher, un test du document témoin en RD (4.5) et une mesure sur le banc.
    - `[low]` `[reject]` Sonde paresseuse plutôt que sur minuterie. Une minuterie relève de l'application (J4). La période est respectée à chaque lecture.
    - `[low]` `[reject]` `contient_un_de` est dupliqué dans le test réel : c'est du code de test, et le scoreur partagé n'existe pas encore.
    - `[low]` `[reject]` Fichiers hors zone. Le changement de `test_service.py` est une conséquence directe de la story. Le test réel est exigé par la mission.
  - **Edge Case Hunter**
    - `[low]` `[patch]` Connecté sans outil autorisé : doublon du constat Blind Hunter n°3.
    - `[medium]` `[patch]` Premier tour connecté sans appel : doublon du constat Blind Hunter n°2.
    - `[low]` `[patch]` Appels tous refusés et texte vide : la dernière génération n'avait aucun passage. Correctif : reconstruction par `_messages_index`. Test ajouté.
    - `[low]` `[patch]` Outil non proposé : doublon du constat Blind Hunter n°1.
    - `[false]` `[reject]` Id d'appel vide. L'adaptateur natif remplace un id vide (`or nouvel_identifiant()`), et `json-generique` génère toujours l'id.
    - `[false]` `[reject]` Exception hors `_PANNES` : même motif que le constat Blind Hunter n°4.
    - `[low]` `[reject]` `ecarts_schema` acquis en cours de boucle par une autre requête. Ce cas de concurrence n'existe pas en CLI ; le tour suivant le prend en compte.
    - `[false]` `[reject]` `lister_outils` qui lève : même motif que le constat Blind Hunter n°4.
    - `[low]` `[reject]` Fil d'appel hors délai : doublon du constat Blind Hunter n°7.
    - `[low]` `[patch]` Un `result` non objet donnait `erreur=False`. Correctif : `erreur=True`.
    - `[false]` `[reject]` `ecarts` en chaîne. `comparer_schema_serveur` pose toujours un tuple.
    - `[false]` `[reject]` `ecarts_schema` en méthode. C'est une propriété dans `ModeSonde`, et elle est absente de `ModeFixe`.
    - `[low]` `[reject]` Argument `optionnel` dans le test réel : aucune règle optionnelle dans RD-001 et RD-002.
    - `[low]` `[reject]` Réponse d'erreur dans une cassette du test réel : les cassettes de RD-001 et RD-002 sont en succès.
    - `[low]` `[reject]` L'intention parlait de passages en connecté. Le correctif serait une modification de la spec ; l'amendement est consigné.

## Design Notes

Flux RD : `[Repli]` (schéma dérivé) → par tour : `Jeton*`, `AppelOutil`/`AppelNonConforme`, puis par appel `ResultatOutil` (et `Repli` en cas de panne) → `Sources` → `[Avertissement(valeurs-mode-connecte)]` si la réponse n'a pas été vérifiée en ligne (hors ligne ou repli) → `Fin(urls_inventees)`.

Passages (amendé, voir Spec Change Log) : « MCP d'abord, puis l'Index en repli » (AD-14).
- **Mode connecté sans écart de schéma.** Le premier tour est construit sans passages ni recherche dans l'Index. `messages_connecte(tache, demande, tools)` est une fonction publique de `recherche.py`, réutilisable par le banc et `data`/`train`. Elle appelle `construire_messages` sur une copie de la Tâche (`dataclasses.replace`) dont le prompt garde la consigne de `RD.md` mais retire l'emplacement `passages` : l'entrée texte est alors rendue telle quelle, selon la règle unique d'AD-7. Ni `config/` ni `prompts.py` ne sont touchés. Une variante de prompt dédiée (`RD-connecte`) est à proposer à Anaël.
- **Hors ligne, schéma dérivé, ou au premier repli.** Les messages sont reconstruits par `ctx.messages_pour(construire_messages(tache, demande, passages_catalogue(...)))`, avec le prompt complet et sans `tools`. Les tours d'outil précédents ne sont pas repris : la réponse est établie à partir de l'Index local (FR-9). Leurs `ResultatOutil` restent dans la trace.
- **Catalogue seul.** Les passages sont restreints au catalogue data.gouv, pour que la réponse s'appuie sur des jeux de données et non sur des fiches.
- **Connecté sans repli.** `passages = []`, `Sources` = sources MCP citées. `Sources` = passages cités `[n]` + URL des résultats d'outils citées dans le texte (titre lu dans le bloc du résultat, sinon l'URL) ; en hors ligne ou repli sans citation, tous les passages du catalogue, pour toujours donner le lien (FR-8).

Message `tool` d'échec : phrase fixe factuelle (« Appel non abouti : data.gouv n'a pas répondu. Données non vérifiées en ligne. »). Ce n'est pas un exemple de réponse (D1.1).

## Verification

**Commands:**
- `uv run pytest tests/harness -q` -- expected: tout passe.
- `uv run pytest -q` -- expected: aucun échec nouveau (échec connu hors zone : `test_prompts.py::test_items_reels_passent_construire_messages[CT.jsonl]`).
- `uv run ruff check` et `uv run ruff format --check` -- expected: propres.
- `SLMSP_VENDOR_DIR=<principal>/vendor SLMSP_MODELS_DIR=<principal>/models uv run pytest tests/harness/test_integration_recherche.py -m integration -s` -- expected: passe, trace affichée.

## Auto Run Result

Status: done

### Résultat final (après revue)

**Résumé.** La Tâche RD est opérationnelle.

`harness/taches/recherche.py` :
- **Boucle d'outils.** Le premier tour connecté ne porte que la demande (`messages_connecte`, l'Index n'est pas interrogé). Viennent ensuite au plus `iterations_max` tours, puis une génération sans `tools`.
- **Validation.** Chaque appel est validé par `valider_appel` et doit faire partie des outils proposés. Un appel invalide devient `AppelNonConforme` et n'est jamais envoyé.
- **Résultats.** `ResultatOutil` reçoit le `result` JSON-RPC copié à l'identique. L'`id` JSON-RPC (report 3.2) n'entre pas dans la trace.
- **Appels répétés.** Un appel identique n'est envoyé qu'une fois.
- **Repli.** Une panne (délai, HTTP, injoignable, hôte bloqué), un schéma dérivé ou un Mode perdu donnent un seul `Repli` (« non vérifié en ligne »). La réponse est alors reconstruite sur les passages du catalogue data.gouv, sans outils.
- **Avertissement.** `Avertissement(valeurs-mode-connecte)` est émis dès qu'aucune donnée n'a été vérifiée en ligne.

`harness/modes.py` :
- **`ModeSonde`.** Sonde `GET /health` par `net` (profil `assistant`, garde hors ligne détecté), au démarrage, à chaque période et avant chaque appel. En hors ligne forcé, aucune requête n'est émise. Le contrôle du schéma au passage en connecté renseigne `ecarts_schema` et laisse une entrée de journal.
- **`ModeFixe`.** Mode constant, utilisé par le banc.

**Fichiers.**
- `src/slmsp/harness/modes.py` : Modes.
- `src/slmsp/harness/taches/recherche.py` : traitement RD, `messages_connecte` et `contenu_resultat` (rendu unique du message `tool`).
- Tests : `tests/harness/test_modes.py`, `test_recherche.py`, `test_repli.py` et `test_integration_recherche.py` (réel).
- `tests/harness/test_service.py` (hors zone, conséquence directe) : le test « RD indisponible » est remplacé par « RD disponible ».
- `service.py`, `config/` et `prompts.py` ne sont pas modifiés.

**Revue.** 43 constats : 0 high, 6 medium, 27 low, 9 false, 1 maybe-false.
- **Patchs** (commit `b4383ee` ; 2 entrées medium, 6 entrées low) :
  - avertissement d'une réponse connectée sans résultat d'outil ;
  - tests `error` et `isError` dans la boucle ;
  - outil exposé mais non proposé ;
  - appels tous refusés, puis Index ;
  - jointure des tours ;
  - appels répétés ;
  - `result` non objet ;
  - `AppelNonConforme` de l'adaptateur.
- **Reportés** (`deferred`) :
  - variante `RD-connecte` et parité `data`/`train` (renvoi `[1]` orphelin) ;
  - FR-38 pour les arguments générés (non vérifié).
- **Rejetés** : motifs dans le journal de tri.

**Revue de suivi recommandée : true** (2 entrées medium patchées). Risque non vérifié : le cache d'appels identiques et la règle « non vérifié sans résultat » n'ont tourné en réel que sur des items connectés sans panne. Aucun item de repli gelé (RD-005, RD-014, RD-020, RD-032) n'a tourné avec un vrai modèle.

**Vérification finale.**
- `ruff check` et `ruff format --check` : propres.
- `uv run pytest -q` : 2330 passés, 167 ignorés, 1 échec. L'échec existait avant la story et sort de sa zone : `test_prompts.py::…[CT.jsonl]`.
- Test réel : 1 passé, en 50 s. Conditions : Qwen3 4B en CPU, `json-generique` (décodage contraint par schéma JSON), BGE-M3, Index `20260926`, Bac à sable sur les cassettes gelées.
  - Pour RD-001 et RD-002 : appel `search_datasets` conforme à la règle `contient_un_de`, `ResultatOutil` égal à la cassette, bon jeu de données, producteur et lien, `urls_inventees=[]`.
  - RD-001 : le second appel identique réutilise le résultat.
- Aucune dépense d'API.

**Risques résiduels.**
- Renvoi `[1]` orphelin en connecté.
- `json-generique` ne décrit pas les outils dans le prompt.
- Le branchement de `controle_schema` sur le `tools/list` réel relève de la 4.5.
- Pas de recontrôle du schéma tant que le Mode reste connecté.
- Le banc (5.3) doit traduire le mode `repli` des items en `ModeFixe("connecte")`.

### Historique

**Statut : done (après l'amendement du 2026-10-12).** Code, tests unitaires, lint et test réel passent.

Amendement appliqué (commit séparé) :
- `messages_connecte(tache, demande, tools)` est ajoutée.
- En Mode connecté, le premier tour n'a pas de passages et l'Index n'est pas interrogé.
- Au premier repli, les messages sont reconstruits avec les passages du catalogue, sans tour d'outil ni `tools`.
- Le hors ligne et le schéma dérivé restent servis par l'Index.
- Tests ajustés :
  - `test_connecte_appel_valide` : demande seule et Index non interrogé ;
  - `verifier_repli` : dernier appel `[system, user avec passages]`, sans message `tool`.
- `xfail` retiré du test réel.

Test réel après amendement (Qwen3 4B CPU, `json-generique`) : **1 passed en 46 s**.
- RD-001 : `search_datasets(query="allocation personnalisée d'autonomie maintien à domicile données individuelles anonymisées")`, appelé deux fois (deux tours identiques). Les deux résultats sont égaux à la cassette. La réponse cite « Bénéficiaires de l'APA à domicile : base floutée (V1) » avec son lien. La source MCP est celle-ci, sans URL inventée.
- RD-002 : `search_datasets(query="loi SRU inventaire logements sociaux communes")`, résultat égal à la cassette. La réponse cite « Communes et inventaire SRU » (Ministère de la Transition écologique) avec son lien, sans URL inventée.
- Les deux réponses finissent par un `[1]` orphelin, alors qu'aucun passage n'est fourni. Ce renvoi est ignoré par `Sources`.

Historique (avant amendement) : statut partiel, AC 3 en xfail.

- Livré : `src/slmsp/harness/modes.py` (`ModeFixe`, `ModeSonde`, `mode_courant`, `mode_avant_appel`, `ecarts_schema`), `src/slmsp/harness/taches/recherche.py` (`traiter`, `contenu_resultat`, `passages_catalogue`, `sources_mcp`, `sources_recherche`, motifs et avertissement), tests `test_modes.py` (22), `test_recherche.py` (18), `test_repli.py` (12), `test_integration_recherche.py`.
- Vérification : `uv run pytest -q` → 1 échec, le seul connu hors zone (`test_prompts.py::test_items_reels_passent_construire_messages[CT.jsonl]`) ; `ruff check` et `ruff format --check` propres.
- Fichier touché hors zone : `tests/harness/test_service.py`. `test_rd_indisponible_avant_la_4_3` affirmait que RD levait `TacheIndisponible` ; il est remplacé par `test_rd_disponible_depuis_la_4_3`. C'est une conséquence directe de la story.
- Test réel (Qwen3 4B CPU, `json-generique`, BGE-M3, Index réel, cassettes gelées) : RD-001 et RD-002 se terminent par `Fin`, sans URL inventée, mais le modèle n'appelle aucun outil. Il répond depuis les passages du catalogue. Même constat en `natif` sur RD-001 (essai exploratoire). Le test passe donc en `xfail` motivé, sur le modèle du xfail Granite de la story 4.2. La chaîne appel → résultat reste assertée dès qu'un appel est émis.
- Cause probable : en `json-generique`, le prompt ne décrit pas les outils (`construire_messages` ne les rend jamais, AD-7) et des passages pertinents sont toujours fournis (Design Notes). C'est à arbitrer hors de cette story : `prompts.py` et la règle « passages toujours fournis » sont hors zone.
- Décisions prises seul :
  - délai d'appel par fil démon (`join(delai)`), réponse abandonnée au-delà ;
  - en cas d'échec : `ResultatOutil.resultat = None` et message `tool` = phrase fixe ;
  - après un repli, les appels restants du tour reçoivent `ResultatOutil(erreur=True)` sans envoi, avec un seul `Repli` ;
  - si tous les appels d'un tour sont refusés et que le texte est vide : dernière génération sans `tools` ;
  - `isError` de MCP donne `erreur=True` sans repli ;
  - réponse JSON-RPC malformée : `erreur=True`, sans repli ;
  - les motifs commencent par « Résultat non vérifié en ligne » ;
  - l'usage de `Fin` est cumulé sur les tours ;
  - `FACTEUR_RECHERCHE = 4`.
- Dépense d'API : aucune.
