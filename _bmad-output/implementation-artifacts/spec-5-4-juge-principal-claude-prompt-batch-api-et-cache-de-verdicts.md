---
title: 'Story 5.4 — Juge principal Claude : prompt, Batch API et cache de verdicts'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '28513ef7907680a6177170dea1607c65ccf1cf0b'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/eval/grille-juge-v1.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Le chemin Batch API réel (création, relevé, résultats, annulation) n'a jamais été exercé contre l'API Anthropic.
    evidence: |-
      Seul le mode direct a été validé en réel (test payant : Q-001 et CR-001, schémas acceptés). Le batch n'est couvert que par le faux serveur. À vérifier à la première notation réelle (story 8.3, mesure H-BATCH).
    location: >-
      src/slmsp/judge/claude.py
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** Le banc ne sait pas encore faire noter une sortie par le Juge principal Claude. Il faut un Juge aveugle qui note critère par critère selon la grille v1, en Batch API par défaut, sans jamais payer deux fois le même verdict et sans jamais dépasser le poste `anthropic` (10 €).

**Approach:** Le paquet `slmsp.judge` lit la grille (sections et SHA), rend le prompt du gabarit de la grille avec un schéma JSON fermé par Tâche (AD-12), met les verdicts en cache SQLite dans `SLMSP_VAR_DIR`, et appelle `claude-opus-5-5` par le SDK `anthropic` (client HTTP du profil `outillage`). Chaque appel passe par le `RegistreBudget` : réservation au pire cas, puis régularisation. Le profil `outillage` gagne une règle GET minimale vers `api.anthropic.com`, pour le suivi des lots.

## Boundaries & Constraints

**Always:**
- Zone : `src/slmsp/judge/{__init__,grille,prompt,cache,claude,config}.py`, `src/slmsp/core/schemas/verdict.py`, `config/juges.toml`, une règle ajoutée à `config/reseau.toml`, `tests/judge/*`. Les stories 4.2 (`harness/`) et 7.6 (`eval/jeu`, `eval/revue`) tournent en parallèle : ne rien toucher d'autre.
- `anthropic` n'est importé que dans `slmsp/judge/` (AD-3, verrou 1). `judge` n'importe ni `httpx`, ni `httpx2`, ni `harness` : seulement `slmsp.core`, `slmsp.net` et `slmsp.budget` (règles de `tests/test_architecture.py`). Les tests peuvent importer `httpx2` pour `MockTransport`.
- Client : `anthropic.Anthropic(api_key=secret("ANTHROPIC_API_KEY"), http_client=slmsp.net.client("outillage", transport_interne=...), max_retries=0, timeout=config.delai_appel)`. Le secret n'apparaît jamais dans un log, un message ni un fichier versionné.
- Requête (direct et batch) : `model`, `max_tokens`, un seul message `user`, `output_config = {"effort": <config>, "format": {"type": "json_schema", "schema": <schéma>}}`. Ni `temperature`, ni `top_p`, ni `top_k`, ni `thinking`, ni `fallbacks`, ni `system` (D-nuit-A1-5).
- Cécité : le contenu envoyé se limite à l'entrée rendue de l'item, au texte final, aux sources citées (URL et titre seulement), aux références de l'item et à la section de grille. `appels_outils` et toute autre clé de la sortie ou des sources ne sont jamais envoyés. Aucune API du Juge ne reçoit le nom du modèle évalué ni la méthode.
- Les verdicts ne servent qu'au banc d'évaluation (AD-3 verrou 6) : aucune fonction ne les exporte vers `data` ou `train`.
- Aucun test n'appelle l'API Anthropic, sauf le test réel unique marqué `reseau` et `payant` (exclu par défaut).

**Never:**
- Calculer un score, un rappel ou un kappa dans `judge` (c'est `evaluation.scores`, story 5.6).
- Juger un item CO (jamais jugé) : `ItemNonJugeable`.
- Relancer automatiquement dans le SDK, ou en dehors du `RegistreBudget`.
- Modifier `eval/grille-juge-v1.md`, `eval/SPEC-jeu-evaluation.md`, `pyproject.toml`, `slmsp/net/`, `slmsp/budget/` ou un autre fichier hors zone.
- Écrire sous `eval/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Batch nominal | 3 items Q/LC/CR non en cache, `mode_appel="batch"` | 1 lot : `reserver_lot` avant `POST /v1/messages/batches`, ligne de lot persistée avec le `batch_id` Anthropic avant le premier `GET`, résultats validés, `collecter_lot` avec la somme des `usage`, 3 verdicts en cache | — |
| Cache plein | même demande relancée | 0 requête HTTP, aucune ligne ajoutée au registre, résultats `depuis_cache=True`, `cout_eur=0` | — |
| Doublon dans l'appel | 2 demandes de même clé | une seule requête, deux résultats identiques | — |
| Relance après crash | lot `en_cours` dans `verdicts.sqlite` (batch_id connu) | `juger` relit ce lot (GET) et le collecte avant toute création de lot | — |
| Lot réservé non créé | lot local sans `batch_id` Anthropic | `annuler_lot(lot_id)` sans usage (pire cas), lot `abandonne`, items rejugés | — |
| Délai de lot dépassé | lot non `ended` après `delai_max_lot` | `POST .../cancel`, sondage jusqu'à `ended` (annulation confirmée), résultats déjà réussis gardés, `annuler_lot(lot_id, usage)`, items restants en appels directs | annulation non confirmée après `delai_annulation` : lot laissé ouvert, items restants `non-juge` (motif `lot-non-annule`) |
| Sortie non conforme x2 | JSON invalide ou hors schéma, deux fois | 1re : échec compté (persisté), nouvel essai direct ; 2e : verdict `invalide=True` mis en cache, statut `invalide` | aussi pour `stop_reason` `refusal` ou `max_tokens` |
| Budget épuisé | `BudgetEpuise` à `reserver` ou `reserver_lot` | arrêt : items restants `non-juge` (motif `budget`), `RapportJugement.budget_epuise=True` | aucune exception remontée à l'appelant |
| Erreur API directe | exception du SDK (5xx, réseau) | tentative comptée au pire cas par le registre, item `non-juge` (motif `erreur-api`), on continue | — |
| Résultat batch `errored`/`expired`/`canceled` | — | item repassé en appel direct, pas compté comme non conforme | — |
| Item CO ou sans référence d'éléments (CR, RE) | — | `ItemNonJugeable` levée avant tout appel | — |
| Profil réseau | `GET https://api.anthropic.com/v1/messages/batches/x` en `outillage` | autorisée ; `GET https://api.mistral.ai/v1/models` reste refusée | — |

</intent-contract>

## Code Map

- `src/slmsp/net/client.py` -- `client(profil, transport_interne=..., journal=...)` renvoie un `httpx2.Client` gardé (`trust_env=False`, délai `delais.defaut` = 30 s : le SDK le remplace par `timeout=` passé au constructeur `Anthropic`, cf. `anthropic/_base_client.py:1020`). Lecture seule.
- `src/slmsp/net/profils.py:evaluer` + `src/slmsp/net/config.py:Regle` -- règles `outillage` : `methodes`, `hotes`, `suffixes`, `chemins` (chemins **exacts** seulement, pas de préfixe). La règle `api-post` de `config/reseau.toml` ne permet que POST vers `api.anthropic.com` : ajouter une règle `anthropic-lots`, `methodes = ["GET"]`, `hotes = ["api.anthropic.com"]`, sans `chemins` (les identifiants de lot varient). `tests/net/test_profils.py:249` ne teste pas de GET Anthropic : aucun test existant ne casse.
- `src/slmsp/budget/registre.py:RegistreBudget` -- `imputer("juge-principal") -> ("anthropic", None)` ; `executer_avec_relances(appel, 1, poste, sous_poste, modele, "direct", est, max_tokens)` (appel renvoie `(résultat, UsageTokens)`, exception = pire cas puis relevée) ; `reserver_lot(batch_id, poste, sous_poste, modele, est, max_tokens, n) -> retenu` (le `batch_id` est **choisi par l'appelant**, persisté avant soumission) ; `collecter_lot(batch_id, usage)` ; `annuler_lot(batch_id, usage|None)`. `BudgetEpuise` dans `slmsp.core.erreurs`.
- `src/slmsp/budget/tarifs.py` -- `UsageTokens(entree, sortie, ecriture_cache, lecture_cache)`, `cout_reel(tarifs, modele, mode, usage)` et `cout_pire_cas` : réutiliser pour le coût par item. `config/tarifs.toml` a déjà `claude-opus-5-5` en `direct` et `batch`.
- `src/slmsp/core/items.py` -- `ItemBase` et sous-classes (`ItemQ`… `ItemNR`, `code`, `LIBELLES`), `vers_requete(item) -> RequeteTache(tache, entree, options)`, `lire_items(chemin, strict=False)` pour le calibrage (`eval/calibrage/echantillon-calibrage.jsonl`, codes `R`/`RS` adaptés en `RD`/`RE`).
- `src/slmsp/core/canonique.py` (`json_canonique`, `sha256_hex`), `core/var.py` (`dossier_var()`, `ouvrir_sqlite()` en WAL), `core/config.py` (`ModeleConfig`, `charger_toml`, `racine_projet`), `core/secrets.py` (`secret(nom)`, `SLMSP_ENV_FILE`), `core/erreurs.py` (`SlmspError`, `ConfigurationInvalide`), `core/schemas/__init__.py` (`SchemaBase`, `SousSchema` ; convention `schema_version: Literal[1] = 1`, cf. `core/schemas/run.py:62`).
- `tests/conftest.py` -- autouse : garde réseau (sauf marqueur `reseau`) et `SLMSP_VAR_DIR` temporaire par test. `tests/net/conftest.py` montre l'usage de `httpx2.MockTransport` comme `transport_interne`. `tests/budget/conftest.py` montre des TOML de budget et de tarifs de test dans `tmp_path`.
- `tests/test_architecture.py` -- `judge` en couche 3 ; `anthropic` interdit hors `judge` ; clients HTTP interdits hors `net`. `pyproject.toml` : extra `judge = ["anthropic==1.13.0"]` (installé par `uv sync --extra judge`), marqueurs stricts (`reseau`, `gpu`, `lent` ; exclus par défaut).
- `eval/grille-juge-v1.md` -- front-matter `version: 1.0` ; sections `## Principes communs`, `## Q : …`, `## RD : …`, `## CR : …`, `## LC : …`, `## CO : …`, `## RE : …`, `## CT : …`, `## NR : …`, `## Prompt du Juge (gabarit)` (citation `> ` avec `{tache}`, `{section de la Tâche}`, `{entree}`, `{champs de référence}`, `{sortie}`). Lecture seule.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/schemas/verdict.py` -- créer `NoteCritere(SousSchema)` (`note: int | float`, `justification: str`), `ElementPresent(SousSchema)` (`ref: str`, `present: int | float`, `justification: str`) et `Verdict(SchemaBase)` (`schema_version: Literal[1] = 1`, `id`, `criteres: dict[str, NoteCritere | list[ElementPresent]]`, `inventions: list[str]`, `confiance: Literal["haute","moyenne","basse"] | None`, `invalide: bool = False`) ; validateur : `invalide` ⇔ `criteres` vide et `confiance` nulle -- schéma commun aux deux juges (5.5 le réutilise).
- `config/juges.toml` + `src/slmsp/judge/config.py` -- `schema_version = 1` et section `[principal]` : `modele = "claude-opus-5-5"`, `effort = "medium"`, `mode_appel = "batch"` (`batch` | `direct`), `max_tokens = 6000`, `delai_max_lot = 3600`, `intervalle_sondage = 60`, `delai_annulation = 600`, `delai_appel = 600` (secondes), `usage_budget = "juge-principal"`, `grille = "eval/grille-juge-v1.md"`. `ConfigJuges` (`ModeleConfig`, section `second` absente pour l'instant : 5.5 l'ajoutera) et `charger_juges(chemin=None)` sur le modèle de `budget/config.py`. Chaque valeur commentée dans le TOML.
- `src/slmsp/judge/grille.py` -- `charger_grille(chemin) -> Grille` : version du front-matter, `section(code) -> SectionGrille(code, texte, sha256)` où `texte` = section « Principes communs » + section de la Tâche (titres compris), `gabarit` (texte de la citation sans les `> `) et `sha_gabarit`. Grille illisible, section ou gabarit manquant, placeholder absent : `ConfigurationInvalide`.
- `src/slmsp/judge/prompt.py` -- `schema_sortie(item) -> dict` (fermé, `additionalProperties: false` partout, `required` complet, `id` en `const`, notes en `enum` typé ; cf. Design Notes), `references(item) -> dict`, `rendre_entree(item) -> str`, `rendre_sortie(sortie) -> str`, `construire_prompt(item, sortie, grille) -> PromptJuge(texte, schema, sha_section, sha_gabarit, sha_schema)` par substitution en une passe des placeholders du gabarit, `valider_sortie(item, texte_json, schema) -> Verdict` (lève `SortieNonConforme` : JSON invalide, écart au schéma vérifié par `jsonschema`, `id` différent, `ref` manquante ou en double), et l'exception `ItemNonJugeable(SlmspError)`.
- `src/slmsp/judge/cache.py` -- `CacheVerdicts(chemin=None)` sur `dossier_var()/verdicts.sqlite` (`ouvrir_sqlite`) : `cle_verdict(item, sortie, prompt, modele, effort)` = SHA-256 du JSON canonique de {SHA de l'item canonique (`item.model_dump(mode="json")`), SHA de la sortie canonique, SHA de section, de gabarit et de schéma, modèle, effort} ; tables `verdicts` (verdict JSON, item_id, modèle, effort, mode, coût, tokens), `echecs` (compteur de sorties non conformes par clé), `appels` (journal en ajout seul de chaque tentative payée : clé, item_id, mode, lot, tokens, coût EUR, issue, horodatage) et `lots` + `lot_requetes` (lot local, `batch_id` Anthropic, statut `reserve`/`en_cours`/`collecte`/`annule`/`abandonne`, horodatage de soumission, requêtes : custom_id, clé, item_id, schéma JSON). Écritures transactionnelles, aucune suppression.
- `src/slmsp/judge/claude.py` -- `fabriquer_client(config, transport_interne=None, journal=None, fichier_env=None)` ; `DemandeJugement(item, sortie)` ; `ResultatJugement(item_id, cle, statut ∈ {"juge","invalide","non-juge"}, verdict, depuis_cache, cout_eur, tokens, mode, motif)` ; `RapportJugement(resultats, budget_epuise, cout_total_eur)` ; `JugeClaude(config, registre, cache, client, grille, *, attendre=time.sleep, horloge=time.monotonic)` avec `juger(demandes) -> RapportJugement` : (1) reprise des lots `reserve`/`en_cours` ; (2) clés et cache ; (3) mode batch par lots (réservation, lot local `slmsp-juge-<uuid4 hex>` persisté avant `create`, `batch_id` Anthropic persisté juste après, sondage, collecte ou annulation confirmée) ; (4) appels directs pour le mode `direct`, les restes de lot et le second essai d'une sortie non conforme ; (5) journal des coûts par item. Résultats dans l'ordre des demandes.
- `src/slmsp/judge/__init__.py` -- docstring du paquet (rôle, AD-3, AD-12) ; aucun réexport qui importerait `anthropic` à l'import de `slmsp.judge`.
- `config/reseau.toml` -- ajouter la règle `anthropic-lots` (GET, `api.anthropic.com`), commentée « suivi des lots batch du Juge (story 5.4) ».
- `tests/judge/conftest.py`, `test_grille.py`, `test_prompt.py`, `test_cache.py`, `test_claude.py` -- `pytest.importorskip("anthropic")` en tête des seuls tests qui en ont besoin ; faux serveur Anthropic en `httpx2.MockTransport` (routes `POST /v1/messages`, `POST /v1/messages/batches`, `GET /v1/messages/batches/{id}`, `GET .../results` en JSONL, `POST .../cancel`) qui enregistre chaque corps ; registre et tarifs de test dans `tmp_path` ; `attendre` et `horloge` factices. Un test par ligne de la matrice et par critère d'acceptation de la story ; un test du schéma de chaque Tâche (Q avec et sans `sans_reponse`, RD, CR, LC, RE, CT, NR, CO refusé) ; un test de la règle réseau via `slmsp.net.profils.evaluer` sur la vraie config.
- `tests/judge/test_claude_reel.py` -- test unique marqué `reseau` et `payant` (marqueur `payant` enregistré par `pytest_configure` dans `tests/judge/conftest.py`, sans toucher `pyproject.toml`) : `SLMSP_ENV_FILE`, `RegistreBudget` réel (chemin de `SLMSP_VAR_DIR` capturé à l'import du module, sinon `%LOCALAPPDATA%\slmsp\var`, car la fixture autouse le redirige), cache dans `tmp_path`, `mode_appel="direct"`, items `Q-001` et `Q-002` du calibrage avec leur `reponse_reference` comme sortie. Plafond dur de 0,30 € : avant chaque item, coût réel cumulé + coût pire cas de l'item ≤ 0,30 €, sinon arrêt. Affiche tokens, coût par verdict et coût total (`-s`).

**Acceptance Criteria:**
- Given une requête au Juge (direct ou batch), when son corps arrive au transport factice, then il ne contient ni `temperature`, ni `top_p`, ni une valeur sentinelle placée dans `appels_outils` ou dans une clé non autorisée d'une source.
- Given chaque Tâche jugée, when on construit le schéma, then il est fermé selon AD-12 et accepté par `jsonschema` ; un verdict hors échelle ou avec une clé en trop est refusé.
- Given un verdict en cache, when on le redemande, then aucune requête HTTP et aucune ligne de registre.
- Given un lot, when il est soumis, then la réservation précède le `POST` de création, le `batch_id` Anthropic est en base avant le premier `GET`, et un nouveau `JugeClaude` relit les lots en cours avant d'en créer un.
- Given chaque appel régularisé, when on lit la table `appels`, then tokens et coût en euros par item y figurent.
- Given `uv run pytest` et `uv run ruff check`, when on les lance, then tout passe (hors échecs préexistants listés, hors zone).

### Review Findings

Revue de code du lot 1, le 2026-10-12. Détail et constats rejetés : `revue-code-lot-1-juges-mistral.md`.

- [x] [Review][Patch] P11 (ex-D2, tranché le 2026-10-12 : arrêt du run). Un 429 arrête les appels restants du run, comme un 401 ou un 403, avec le nouveau motif `limite-debit`. L'appel est réglé à 0. Aucune relance [src/slmsp/judge/claude.py:614]
- [x] [Review][Patch] P1. Sur un échec de `batches.create`, un refus 4xx est réglé au pire cas et un 401 ou un 403 n'arrête pas la boucle de lots [src/slmsp/judge/claude.py:405]
- [x] [Review][Patch] P8. Aucun test ne couvre la reprise d'un lot déjà réglé au registre (garde `_lot_ouvert_au_registre` de `_achever_lot`) [tests/judge/test_claude.py]
- [x] [Review][Patch] P9. `cout_total_eur` n'est pas vérifié après l'échec de création d'un lot [tests/judge/test_claude.py:320]

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 38 findings — high 0, medium 11, low 20, false 7, maybe-false 0
- findings:
  - `[medium]` `[patch]` (VG) Les échecs de `retrieve`, de `results` et de `cancel` sur un lot ne sont pas testés. — Ajout de pannes par route dans `FauxAnthropic` et de 4 tests. Chacun vérifie : items `non-juge`, aucun appel direct, lot laissé ouvert, solde au `juger` suivant.
  - `[medium]` `[patch]` (VG) Les garde-fous de reprise d'un lot après un crash pendant la collecte ne sont pas testés. — Ajout de `test_reprise_apres_crash_pendant_la_collecte` et de `test_reprise_lot_reserve_sans_ligne_registre`.
  - `[medium]` `[patch]` (VG) Après une reprise, une sortie non conforme d'un lot est recomptée : deux échecs, verdict `invalide` et journal en double. — Ajout de la requête `appel_journalise(lot_id, cle)` : un résultat déjà journalisé n'est pas recompté.
  - `[low]` `[patch]` (VG) `test_reprise_avant_creation_d_un_lot` ne vérifie pas que le verdict repris est en cache. — Assertion ajoutée.
  - `[medium]` `[patch]` (BH) Le validateur de `Verdict` accepte un verdict valide à moitié rempli. — Il exige désormais des critères non vides et une confiance quand `invalide` est faux ; un test par forme incomplète.
  - `[low]` `[patch]` (BH) `cle_verdict` hache toute la sortie, y compris les clés inconnues, au lieu de la `sortie_canonique` d'AD-12. — La clé ne porte plus que sur `{texte, appels_outils, sources}` ; `rendre_sortie` refuse une source qui n'est pas un dictionnaire ; test ajouté.
  - `[low]` `[reject]` (BH) Une sortie sans `texte` est rendue vide et jugée. — L'appelant (5.3) fournit toujours `texte` ; une sortie vide reste jugeable (note basse). Un garde-fou ajouterait une branche pour un cas improbable.
  - `[medium]` `[patch]` (BH) En mode direct, aucun coupe-circuit sur une erreur systémique : un 4xx est compté au pire cas, et une clé révoquée viderait les 10 €. — Un 4xx est régularisé à 0 € et l'item passe `non-juge`. Un 401 ou un 403 arrête le run. Deux tests.
  - `[low]` `[patch]` (BH) `_suivre` abandonne dès la première erreur transitoire de `retrieve`. — 3 erreurs consécutives sont tolérées (groupé avec le premier constat VG).
  - `[medium]` `[patch]` (BH) Un lot repris repart pour un `delai_max_lot` complet, et un lot déjà en `canceling` attend puis réannule. — Le délai est mesuré depuis `soumis_le` (horloge murale injectée) ; un lot en `canceling` attend la confirmation sans nouvel ordre. Deux tests.
  - `[low]` `[reject]` (BH) Aucune taille maximale de lot (100 000 requêtes / 256 Mo). — Le jeu fait 225 items d'environ 20 Ko (environ 5 Mo) : limite inatteignable, et le découpage ajouterait de la complexité.
  - `[low]` `[reject]` (BH) Un lot orphelin (`create` qui lève alors que le serveur l'a accepté, ou crash avant `marquer_soumis`) n'est ni retrouvé ni annulé. — Le budget reste sûr, car le lot est compté au pire cas au registre. Le cas est rare, et une reprise par `batches.list` serait un nouveau mécanisme.
  - `[low]` `[patch]` (BH) Avec des demandes en double, la somme des coûts par résultat vaut le double du total. — Le coût et les tokens ne sont portés que par la première occurrence ; tests mis à jour.
  - `[low]` `[reject]` (BH) Pas de verrou entre processus sur `verdicts.sqlite` et les lots. — Une seule notation tourne à la fois ; un verrou ajouterait une mécanique pour un cas improbable.
  - `[medium]` `[patch]` (BH) Le test payant ne valide que le schéma Q contre la vraie API. — Q-002 est remplacé par CR-001 (tableau de `ref`, `enum` 0/0,5/1), validé contre l'API réelle. Le chemin batch réel reste non exercé (différé).
  - `[low]` `[reject]` (BH) Pas de protection contre une injection de consignes depuis la sortie évaluée. — Le modèle évalué n'est pas adverse ; le gabarit vient de la grille, qu'il est interdit de modifier.
  - `[low]` `[patch]` (BH) Des tests manquent : budget épuisé au second essai direct, lot partiel puis budget épuisé. — Ajout de `test_budget_epuise_au_second_essai_direct` et de `test_lot_partiel_puis_budget_epuise`.
  - `[low]` `[patch]` (BH) Le coût mis en cache d'un verdict `invalide` ignore les essais des runs précédents. — Ce coût vaut désormais la somme des lignes `appels` (`cumul_appels`) ; test ajouté.
  - `[low]` `[reject]` (BH) La règle `anthropic-lots` autorise tout GET sur `api.anthropic.com`. — Décision assumée : la config n'accepte que des chemins exacts et `slmsp.net` est hors zone. À trancher par Anaël.
  - `[false]` `[reject]` (BH) Incohérences de la spec (statut, chemin absolu, `valider_sortie`, matrice). — Le statut suit le workflow ; `valider_sortie` existe ; la correction consisterait à modifier la spec du build.
  - `[medium]` `[patch]` (ECH) `except Exception` attrape `ConfigurationInvalide` et `TarifInconnu`, levées avant tout appel. — `except SlmspError: raise` est placé avant le gestionnaire générique.
  - `[medium]` `[patch]` (ECH) Une non-conformité est recomptée après la reprise d'un lot (groupé avec le troisième constat VG). — `appel_journalise`.
  - `[low]` `[reject]` (ECH) Course entre deux processus qui soldent le même lot. — Même motif que l'absence de verrou entre processus.
  - `[medium]` `[patch]` (ECH) Verdict à moitié rempli accepté (groupé avec le constat BH sur le validateur). — Validateur renforcé.
  - `[low]` `[patch]` (ECH) Des sources objets ou un `NaN` font lever `json_canonique` (groupé avec le constat BH sur la clé de cache). — Projection canonique ; seules les sources dictionnaires sont acceptées.
  - `[low]` `[reject]` (ECH) Lot au-delà des limites de la Batch API. — Même motif que la taille maximale de lot.
  - `[low]` `[patch]` (ECH) Une section de grille en double écrase la précédente sans bruit. — `ConfigurationInvalide` ; test avec 3 cas.
  - `[low]` `[patch]` (ECH) Le coût d'un lot repris pour des clés hors des demandes manque à `cout_total_eur`. — Ajouté à `cout_hors_items`.
  - `[low]` `[patch]` (ECH) La clé de cache hache des champs jamais envoyés (groupé avec le constat BH sur la clé de cache). — Projection canonique.
  - `[false]` `[reject]` (IA) La cécité d'AC1 n'est testée que par procuration. — `DemandeJugement` n'a aucun champ pour le modèle ou la méthode. Les sentinelles placées dans `appels_outils` et dans des clés inconnues sont absentes du corps envoyé.
  - `[low]` `[patch]` (IA) La clé de cache n'est pas projetée sur la sortie canonique (groupé avec le constat BH sur la clé de cache).
  - `[low]` `[reject]` (IA) Ampleur de la règle réseau (R3a contre R3b). — Même motif que le constat BH sur la règle réseau.
  - `[medium]` `[patch]` (IA) `delai_max_lot` se compte depuis la reprise et non depuis la soumission (groupé avec le constat BH sur le délai de lot). — Le délai court depuis `soumis_le`.
  - `[false]` `[reject]` (IA) Il n'existe ni filtre de litige RD ni statut `partiel-budget`. — AC7 demande seulement que l'appelant reçoive l'information (`budget_epuise`) ; le filtre de litige relève de 5.6.
  - `[false]` `[reject]` (IA) Le test payant va au-delà de D-nuit-A2-11. — Il a été demandé explicitement par l'orchestrateur du run (mesure de H-JUGE-COUT, plafond de 0,30 €).
  - `[false]` `[reject]` (IA) Principes communs ajoutés à la section envoyée. — Décision consignée et voulue (Design Notes).
  - `[false]` `[reject]` (IA) Journal des coûts par item dans `verdicts.sqlite` plutôt qu'au registre. — AC8 est satisfait ; le registre garde une ligne par lot, par conception (1.5).
  - `[false]` `[reject]` (IA) État du processus (statut de la spec). — Le statut suit le workflow ; la correction consisterait à modifier la spec.

## Design Notes

**Schéma de sortie (exemple Q, `sans_reponse` vrai) :**
```json
{"type":"object","additionalProperties":false,"required":["id","criteres","inventions","confiance"],
 "properties":{"id":{"type":"string","const":"Q-002"},
  "criteres":{"type":"object","additionalProperties":false,
   "required":["exactitude","pertinence_source","cas_sans_reponse"],
   "properties":{"exactitude":{"$ref":"#/$defs/note_0_2"}, "...": "..."}},
  "inventions":{"type":"array","items":{"type":"string"}},
  "confiance":{"type":"string","enum":["haute","moyenne","basse"]}}}
```
Une note est `{"type":"object","additionalProperties":false,"required":["note","justification"],"properties":{"note":{"type":"integer","enum":[0,1,2]},"justification":{"type":"string"}}}` (`$defs` permis, ou schéma déplié). `presence_elements` : tableau d'objets `{ref: {"type":"string","enum":[refs]}, present: {"type":"number","enum":[0,0.5,1]} (CR) ou {"type":"integer","enum":[0,1]} (RE), justification}`. Pas de `minimum`, `maximum`, `minLength`, `minItems` (non pris en charge par la sortie structurée) : la couverture exacte des `ref` est vérifiée par `valider_sortie`. Références d'éléments : CR = décisions `D1…Dn` puis actions `A1…An` ; RE = points clés `P1…Pn`, rendus `{"ref": …, "texte": …}` (action : `{"ref", "action", "responsable", "echeance"}`) dans les RÉFÉRENCES.

**Références par Tâche** (clés à `None` omises, ordre fixe) : Q `reponse_reference`, `elements_cles`, `sources_attendues`, `sans_reponse`, `orientation_attendue`, `mention_obligatoire` ; RD `reponse_reference`, `valeurs_attendues`, `criteres` ; CR `participants_reference`, décisions, actions, `pieges` ; LC `informations_a_conserver`, `termes_juridiques_a_conserver` ; RE points clés, `longueur_demandee` ; CT `type_courrier`, `elements_obligatoires`, `champs_a_laisser_en_emplacement`, `valeurs_interdites` ; NR `sous_type`, `reponse_reference`, `criteres`. Rendu JSON (`ensure_ascii=False`, `indent=2`).

**Rendus.** Entrée : `vers_requete(item)` ; texte tel quel, objet en JSON (`indent=2`, clés triées) ; si `options` porte autre chose qu'un `parametres` vide, ajouter « Options de la demande : » et leur JSON. Sortie : le `texte`, une ligne vide, puis « Sources citées : » et une ligne « - <titre> — <url> » par source (« aucune » sinon). `{tache}` = libellé de `LIBELLES`.

**Estimation des tokens d'entrée** (pour la réservation) : `ceil(len(prompt + json(schema)) / 3) + 300`, la majoration de `budgets.toml` s'ajoute ; un lot réserve sur le maximum de ses requêtes. Coût par item = `cout_reel(tarifs, modele, mode, usage)` ; un lot est collecté avec la somme des `usage` des résultats `succeeded`.

**Choix pris seul (à consigner dans Auto Run Result) :** section envoyée = Principes communs + section de la Tâche ; pas de `fallbacks` serveur (le Juge doit rester un modèle unique, et le paramètre est refusé en batch) ; `max_tokens = 6000` et `effort = "medium"` à confirmer par la mesure ; règle GET sans restriction de chemin sur `api.anthropic.com` (la config n'accepte que des chemins exacts) ; un lot réservé mais dont la création n'est pas confirmée reste compté au pire cas.

## Verification

**Commands:**
- `uv sync --extra judge` -- expected: `anthropic 1.13.0` installé
- `uv run pytest tests/judge -q` -- expected: tous les tests passent (le test réel est désélectionné)
- `uv run pytest -q` -- expected: aucun échec (hors échecs préexistants listés)
- `uv run ruff check` et `uv run ruff format --check src/slmsp/judge src/slmsp/core/schemas/verdict.py tests/judge` -- expected: propre
- `$env:SLMSP_ENV_FILE='C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\.env'; uv run pytest tests/judge/test_claude_reel.py -m "reseau and payant" -s` -- expected: 2 verdicts valides, coût total ≤ 0,30 €. Payant : l'implémenteur ne le lance **jamais** ; seul l'orchestrateur de la story le lance, une seule fois, après la revue.

## Auto Run Result

**Statut :** done. Revue faite en 4 couches. Tests : `tests/judge` 99 réussis, le test réel étant désélectionné. Le test payant a été lancé une fois par l'orchestrateur et a réussi.

**Fichiers :**
- `src/slmsp/core/schemas/verdict.py` : `Verdict` commun.
- `src/slmsp/judge/config.py` et `config/juges.toml` : section `principal`.
- `src/slmsp/judge/grille.py` : sections, gabarit et SHA de la grille.
- `src/slmsp/judge/prompt.py` : schéma fermé par Tâche, prompt aveugle et validation.
- `src/slmsp/judge/cache.py` : `verdicts.sqlite` (verdicts, échecs, journal `appels`, lots).
- `src/slmsp/judge/claude.py` : `fabriquer_client` et `JugeClaude.juger`, en batch par défaut et en direct.
- `config/reseau.toml` : règle `anthropic-lots`.
- `tests/judge/*` : tests de la story et test réel.

**Revue :** 38 constats, soit 11 medium, 20 low et 7 false.
- 25 constats corrigés (patch), regroupés en 15 corrections par cause racine, dont 7 medium.
- 13 constats rejetés ; le motif de chacun est dans le Review Triage Log.
- 1 point différé : le chemin batch n'a pas été vérifié contre l'API réelle.

Une relecture complémentaire est recommandée, pour deux risques non vérifiés :
- le chemin Batch API réel (création, relevé, résultats JSONL, annulation) n'a été exercé que sur faux serveur ;
- la logique de reprise après crash a beaucoup changé à la correction : elle est couverte par des tests, mais n'a jamais été relue par un second regard.

**Mesure réelle (test payant, mode direct, effort `medium`, registre réel, campagne `nuit-2026-10-12`) :**

| Item | Tokens d'entrée | Tokens de sortie | Coût direct | Réservé (pire cas) |
|---|---|---|---|---|
| Q-001 (sortie : `reponse_reference`) | 2 703 | 260 | 0,0160 € | 0,1308 € |
| CR-001 (sortie : factice) | 5 016 | 969 | 0,0394 € | 0,1389 € |

- Total dépensé : 0,0555 €.
- Coût moyen : environ 0,028 € par verdict en direct, soit environ 0,014 € en batch (−50 %). Cela donne environ 2,4 € pour 170 items en batch, ce qui confirme l'estimation de H-JUGE-COUT (environ 0,018 $ par item).
- Les deux schémas ont été acceptés par l'API réelle (`const`, `enum` entier, `enum` 0/0,5/1, tableau de `ref`), et les deux verdicts sont valides.
- `max_tokens = 6000` reste très au-dessus de la sortie observée, au plus 969 tokens : la réservation pire cas est d'environ 0,13 € par appel direct.

**Vérification :**
- `uv run pytest tests/judge` : 99 réussis.
- `uv run ruff check` et `ruff format --check` : propres.
- `uv run pytest` complet : 2123 réussis, 165 ignorés, 2 en échec, tous deux hors zone :
  - l'item CT de `tests/harness/test_prompts.py`, préexistant (zone 4.2) ;
  - un test instable sous charge, qui passe quand on le relance seul : `tests/budget/test_concurrence.py::test_critere_6…` à ce passage, et `tests/inference/test_serveur.py::test_demarrage_rate_sante` au passage précédent. `slmsp/budget/` n'est pas modifié par cette story.

**Choix pris seul (Design Notes) :** section envoyée = Principes communs + section de la Tâche ; pas de `fallbacks` ; `max_tokens = 6000` et `effort = "medium"` à confirmer par la mesure ; règle réseau `anthropic-lots` en GET sans restriction de chemin sur `api.anthropic.com` ; un lot réservé dont la création n'est pas confirmée reste compté au pire cas (`annuler_lot` sans usage).

**Autres décisions prises seul :**
- `base_url="https://api.anthropic.com"` est passé explicitement au client `anthropic` : une variable `ANTHROPIC_BASE_URL` de l'environnement ne peut pas dérouter le Juge.
- Ordre de soumission d'un lot : lot local `reserve` et ses requêtes persistés, puis `reserver_lot`, puis `nb_retenu` inscrit, puis `create`, puis `batch_id` inscrit (`en_cours`). Si la réservation ne retient qu'une partie des requêtes, seules les premières sont soumises ; les suivantes partent dans un lot suivant, qui échoue en `budget` si plus rien ne tient.
- Création de lot en erreur d'API (exception du SDK, sans arrêt du processus) : lot soldé au pire cas, `abandonne`, items `non-juge` motif `erreur-api`. Pas de bascule en direct, pour ne pas multiplier les dépenses quand l'API est en panne.
- Délai d'un lot : `delai_max_lot` court depuis `soumis_le` (horloge murale UTC injectée, `maintenant`), y compris pour un lot repris. Un lot relu en `canceling` (ou avec `cancel_initiated_at`) attend la confirmation sans nouvelle annulation ; un lot terminé dont `cancel_initiated_at` est renseigné est réglé par `annuler_lot`. Trois erreurs consécutives du relevé sont tolérées (attente `intervalle_sondage` entre deux), la quatrième laisse le lot ouvert (`erreur-api`).
- Refus 4xx en appel direct : non facturé, réservation régularisée à 0, item `non-juge` (`erreur-api`) ; 401 ou 403 arrêtent tous les appels directs restants du run.
- Correctifs de revue : clé de cache sur la seule projection `{texte, appels_outils, sources}` ; coût d'un verdict en cache = somme de ses lignes `appels` (runs précédents compris) ; coût d'un doublon porté par sa première occurrence ; lot repris après un arrêt pendant la collecte : un résultat déjà journalisé n'est pas recompté ; section de grille en double refusée.
- Items d'un lot resté ouvert (annulation non confirmée, ou erreur au sondage) : `non-juge` (motif `lot-non-annule` ou `erreur-api`), jamais resoumis tant que le lot n'est pas soldé.
- Arrêt sur budget : dès qu'une réservation (lot ou direct) lève `BudgetEpuise`, tous les items restants, seconds essais directs compris, passent `non-juge` (motif `budget`).
- Coûts : `ResultatJugement.cout_eur` cumule les tentatives de l'item dans l'appel (pire cas compris pour une erreur d'API). `cout_total_eur` y ajoute les lots soldés au pire cas sans usage, non attribuables à un item.
- Validation : le verdict est validé contre le schéma stocké avec la requête (`valider_selon_schema`), ce qui permet de valider les résultats d'un lot repris sans l'item.
- Test réel : le coût pire cas d'un item compte une seule tentative. Un second essai (sortie non conforme) pourrait dépasser le plafond de 0,30 € d'au plus un appel.

**Échec hors zone, sans lien avec cette story :** `tests/harness/test_prompts.py::test_items_reels_passent_construire_messages[CT.jsonl]` (`EntreeInvalide` sur la clé `type` d'un item CT, zone de la story 4.2).
