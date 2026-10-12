---
title: "Story 5.5 — Adaptateur Mistral et second juge sur l'échantillon de 20 %"
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '024eb451da021e9df1ba3159145cfdbcfdc3d1a0'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-5-4-juge-principal-claude-prompt-batch-api-et-cache-de-verdicts.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Le banc n'a ni adaptateur Mistral ni second juge. Il faut un point d'appel Mistral unique qui réserve au budget, vérifie le modèle résolu (D1.2) et journalise chaque appel (AD-3 verrou 3). Il faut aussi un second juge qui renote l'échantillon du manifeste, sans que les textes d'évaluation qu'il envoie deviennent lisibles par les pipelines `data` et `train` (D1.1, AD-24 ; différé de la story 1.3).

**Approach:** Le paquet `slmsp.mistral` contient la config, un journal SQLite et un client sur le SDK `mistralai` (client `httpx` gardé du profil `outillage`, sans relance). Les journaux sont **séparés par usage** : `generation` et `validation` vont dans `SLMSP_VAR_DIR/appels-mistral.sqlite` (lisible par `data` et `train`, AD-24) ; `juge-second` va dans `SLMSP_VAR_DIR/appels-mistral-juge.sqlite`, que la liste d'accès de `core.artefacts` refuse déjà. `slmsp.judge.second.JugeMistral` reprend le prompt, le schéma, la validation et le cache de verdicts de la story 5.4, avec `temperature=0` et un `response_format` JSON au schéma de la story 5.4, imputé à `mistral.juge`.

## Boundaries & Constraints

**Always:**
- Zone : `src/slmsp/mistral/{__init__,config,journal,client}.py`, `src/slmsp/judge/second.py`, une extension minimale de `src/slmsp/judge/config.py` (champ `second`, rendue nécessaire par le `[second]` de `juges.toml`), `config/juges.toml`, `config/mistral.toml`, `tests/mistral/*`, `tests/judge/test_second.py` et `tests/judge/test_second_reel.py`. Les stories 3.2 (`mcp/bac_a_sable`) et 4.4 (`harness/`) tournent en parallèle : ne rien toucher d'autre.
- `mistralai` n'est importé que dans `slmsp/mistral/`, au niveau des modules qui en ont besoin (`client.py`). `slmsp.mistral` n'importe ni `slmsp.judge`, ni `httpx`/`httpx2` en dehors des annotations, ni `harness`.
- Client SDK : `Mistral(api_key=secret("MISTRAL_API_KEY"), server_url="https://api.mistral.ai", client=slmsp.net.client("outillage", lib="httpx", ...), async_client=slmsp.net.client("outillage", lib="httpx", asynchrone=True, ...), retry_config=None, timeout_ms=...)` ; `retries=None` à chaque appel (aucune relance). Le secret n'apparaît jamais dans un log, un message, le journal ou un fichier versionné.
- Chaque appel : une réservation `RegistreBudget.reserver` au sous-poste de son `usage` (`registre.imputer(usage)`), un appel unique, puis `regulariser(reservation_id, usage)` ou `compter_pire_cas(reservation_id)` sur une exception sans `usage`. La ligne du journal porte `reservation_id` (« référence budget »).
- Le modèle demandé doit figurer dans `modeles_autorises` de `config/mistral.toml` (vérifié avant tout appel). Le modèle **résolu** (champ `model` de la réponse) doit y figurer aussi et ne correspondre à aucun motif interdit (`labs`, `preview`, `beta`, `-rc`, `experimental`, insensible à la casse) ; sinon `ModeleMistralRefuse`, après journalisation et régularisation de l'appel payé.
- L'appel générique refuse `usage="generation"` (`UsageInterdit`), avant toute réservation et toute requête.
- Le second juge envoie exactement le texte de `construire_prompt(item, sortie, grille).texte` (même cécité que la story 5.4) et valide avec `valider_selon_schema` ; verdicts dans le même `CacheVerdicts`, clé `cle_verdict(..., modele, effort="temperature-0")`.
- Aucun test n'appelle l'API Mistral, sauf le test réel unique marqué `reseau` et `payant`.

**Never:**
- Écrire un appel `juge-second` dans `appels-mistral.sqlite`, ou un appel `generation`/`validation` dans `appels-mistral-juge.sqlite` (le journal refuse l'usage étranger).
- Modifier `slmsp/core/`, `slmsp/net/`, `slmsp/budget/`, `judge/{claude,prompt,cache,grille}.py`, `pyproject.toml`, `tests/test_architecture.py`, `eval/` ou la grille.
- Implémenter `Generateur` (story 9.2), un mode batch Mistral, ou calculer un score ou un kappa (story 5.6).
- Une relance automatique, ou une seconde tentative hors réservation.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Appel nominal `juge-second` | réponse 200, `model` autorisé | `ReponseMistral` (texte, modèle résolu, tokens, coût, `appel_id`) ; une ligne dans `appels-mistral-juge.sqlite` avec requête canonique, corps brut de la réponse en octets, SHA-256 du corps, `reservation_id` ; registre régularisé au coût réel | — |
| Usage `generation` | `appeler(usage="generation", ...)` | `UsageInterdit` | 0 requête, 0 réservation, 0 ligne |
| Jeton de génération | `_appeler(..., usage="generation", jeton=object())` | `UsageInterdit` (le jeton attendu vient de `slmsp.mistral.generateur`, absent en 5.5) | idem |
| Modèle demandé hors liste | config `modele="labs-x"` ou `"mistral-large-2512-preview"` | `ModeleMistralRefuse` | avant toute réservation |
| Modèle résolu interdit | réponse 200 avec `model="labs-mistral-large"` | `ModeleMistralRefuse` | appel journalisé (`statut="modele-refuse"`) et régularisé au coût réel |
| Budget épuisé | `reserver` lève `BudgetEpuise` | exception propagée | 0 requête, 0 ligne |
| Erreur HTTP 5xx / réseau | exception du SDK | ligne `statut="erreur"` (corps brut si disponible), réservation comptée au pire cas | exception propagée (`ErreurApiMistral`, `statut_http`) |
| Refus 4xx | `MistralError` 400/401/403/422 | ligne `statut="erreur"`, réservation régularisée à 0 (non facturé) | `ErreurApiMistral` ; le second juge arrête tout sur 401/403 |
| Second juge nominal | demandes dont l'id est dans `echantillon` | `RapportJugement` (types de `judge.claude`), statut `juge`, verdict au schéma 5.4, `mode="direct"`, coût par item | — |
| Hors échantillon | demande dont l'id n'est pas dans `echantillon` | ignorée (absente du rapport) | — |
| Cache plein | verdict déjà en cache | 0 requête, 0 réservation, `depuis_cache=True`, `cout_eur=0` | — |
| Sortie non conforme x2 | JSON invalide, hors schéma ou `finish_reason` `length` | 1re : échec compté, nouvel essai ; 2e : `Verdict.invalide_pour`, statut `invalide`, en cache | — |
| Budget épuisé en cours | `BudgetEpuise` au 2e item | items restants `non-juge` motif `budget` (« non rejugés »), `budget_epuise=True` | rien n'est remonté |
| Item CO | — | `ItemNonJugeable` avant tout appel | — |

</intent-contract>

## Code Map

- `src/slmsp/judge/claude.py` -- modèle à suivre et types à réutiliser (import) : `DemandeJugement`, `ResultatJugement`, `RapportJugement`, constantes `ECHECS_MAX`, `MOTIF_BUDGET`, `MOTIF_ERREUR_API`, `ISSUE_*`, `STATUTS_ARRET` ; boucle `_juger_en_direct` / `_juger_un_direct` (l.591-698) et `_echec` / `_mettre_en_cache` (l.546-587) : même logique de cache, d'échecs et de coûts, à reproduire dans `second.py` sur le client Mistral. Importer `judge.claude` charge `anthropic` : les tests du second juge font `importorskip("anthropic")` et `importorskip("mistralai")`. Lecture seule.
- `src/slmsp/judge/prompt.py` -- `construire_prompt`, `estimer_tokens_entree`, `valider_selon_schema`, `SortieNonConforme`, `ItemNonJugeable`. `src/slmsp/judge/cache.py` -- `CacheVerdicts` (`lire`, `ecrire`, `compter_echec`, `journaliser_appel`, `cumul_appels`), `cle_verdict`. Lecture seule.
- `src/slmsp/judge/config.py` -- `ConfigJuges` (`ModeleConfig`, champs fermés) : ajouter `ConfigSecondJuge` et `second: ConfigSecondJuge` (le `[second]` de `juges.toml` ferait échouer `charger_juges` sinon).
- `src/slmsp/budget/registre.py` -- `imputer(usage) -> (poste, sous_poste)` (l.287 ; `juge-second` → `mistral.juge`, `generation`/`validation` → `mistral.generation` dans `config/budgets.toml`) ; `reserver(poste, sous_poste, modele, mode, tokens_estimes, max_tokens) -> int` (l.382) ; `regulariser(id, usage) -> float` ; `compter_pire_cas(id) -> float`. `budget/tarifs.py` : `UsageTokens`, `cout_reel`. `config/tarifs.toml` tarife `mistral-large-latest` (direct et batch) : la réservation et le coût se font sur le modèle **demandé** (`mistral-large-latest`), seul tarifé ; le modèle résolu n'est que vérifié.
- `src/slmsp/net/client.py:53` -- `client(profil, lib="httpx", asynchrone=..., journal=..., transport_interne=...)` ; `LIBS = ("httpx2", "httpx")`. Le profil `outillage` permet déjà `POST api.mistral.ai` (règle `api-post` de `config/reseau.toml`) : **aucune règle réseau à ajouter** (pas de GET).
- `src/slmsp/core/artefacts.py:59,488-521` -- `NOM_JOURNAL_MISTRAL = "appels-mistral.sqlite"` ; `chemin_autorise` n'admet dans `SLMSP_VAR_DIR` que ce fichier exact pour `data` et `train` : un autre nom (`appels-mistral-juge.sqlite`) est refusé (`LectureInterdite`). Réutiliser la constante `NOM_JOURNAL_MISTRAL` ; lecture seule.
- `src/slmsp/core/var.py` (`dossier_var`, `ouvrir_sqlite`), `core/secrets.py` (`secret(nom, fichier_env)`), `core/canonique.py` (`json_canonique`, `sha256_hex`), `core/config.py` (`ModeleConfig`, `charger_toml`, `racine_projet`), `core/erreurs.py` (`SlmspError`, `BudgetEpuise`, `ConfigurationInvalide`).
- SDK `mistralai==3.2.0` (extra `data`, `uv sync --extra data --extra judge`) : `from mistralai.client import Mistral` ; `sdk.chat.complete(model=, messages=, temperature=, max_tokens=, response_format=, retries=, timeout_ms=)` → `ChatCompletionResponse(id, model, usage{prompt_tokens, completion_tokens}, choices[0].message.content, choices[0].finish_reason)` ; erreurs `mistralai.client.errors.MistralError` (`status_code`, `raw_response`). Le corps brut d'un succès n'est pas exposé : l'obtenir par un hook `after_success` enregistré sur `sdk.sdk_configuration.__dict__["_hooks"]` (`register_after_success_hook`, objet avec `after_success(hook_ctx, response) -> response`), qui garde `response.content`. Le `TracingHook` du SDK est inerte sans `TracerProvider`.
- `tests/judge/conftest.py` -- `texte_budgets`, marqueur `payant` (`pytest_configure`), fixtures `grille`, `items`, `sortie_factice`, `verdict_conforme(schema)` ; `tests/judge/test_claude_reel.py` -- modèle du test payant (`VAR_REEL`, `RegistrePlafonne`). `tests/conftest.py` : garde réseau et `SLMSP_VAR_DIR` temporaire autouse.
- `src/slmsp/core/schemas/manifeste_jeu.py:46` -- `Echantillons.second_juge: list[IdItem]` : l'appelant (5.6) passe cette liste à `JugeMistral.juger`.

## Tasks & Acceptance

**Execution:**
- `config/mistral.toml` + `src/slmsp/mistral/config.py` -- `schema_version = 1` ; `modele = "mistral-large-latest"` ; `modeles_autorises = ["mistral-large-latest", "mistral-large-2411", "mistral-large-2512"]` (liste stable : alias et versions datées stables de Mistral Large, sans Labs ni préversion ; une version résolue absente est refusée, à ajouter seulement après vérification) ; `motifs_interdits` ; `delai_appel` (secondes) ; `fichier_journal_donnees = "appels-mistral.sqlite"` et `fichier_journal_juge = "appels-mistral-juge.sqlite"` (noms validés : différents, pas de séparateur de chemin, le premier égal à `core.artefacts.NOM_JOURNAL_MISTRAL`). `ConfigMistral` + `charger_mistral(chemin=None)` ; validateur : le modèle par défaut est autorisé et ne correspond à aucun motif interdit. Chaque valeur commentée dans le TOML.
- `src/slmsp/mistral/journal.py` -- `USAGES = ("generation", "juge-second", "validation")` ; `JournalMistral(chemin, usages_admis)` ; `journal_pour(usage, config, dossier=None)` choisit le fichier (`juge-second` → journal du juge, sinon journal des données) ; table `appels` en ajout seul (`appel_id` uuid4 hex, `session_id`, `usage`, `modele_demande`, `modele_resolu`, `requete` JSON canonique sans secret, `reponse_brute` BLOB, `sha256_reponse`, `reservation_id`, `statut` ∈ {`ok`, `modele-refuse`, `erreur`}, `statut_http`, `horodatage` UTC ISO) ; `inscrire(...)` lève `UsageInterdit` pour un usage hors `usages_admis` ; `lire(appel_id)` et `appels()` pour les tests. Aucune suppression, aucune mise à jour.
- `src/slmsp/mistral/client.py` -- exceptions `UsageInterdit`, `ModeleMistralRefuse`, `ErreurApiMistral(statut_http)` (sous `SlmspError`) ; `fabriquer_sdk(config, transport_interne=None, journal_requetes=None, fichier_env=None)` ; `ReponseMistral` ; `ClientMistral(config, registre, sdk, *, dossier_journaux=None)` avec `appeler(usage, session_id, messages, *, max_tokens, tokens_entree_estimes, temperature=None, response_format=None) -> ReponseMistral` qui délègue à `_appeler(..., jeton=None)` ; `_appeler` refuse `generation` sauf si `jeton is _jeton_generateur()`, qui renvoie `slmsp.mistral.generateur._JETON` si ce module existe, sinon `None` (donc refus en 5.5). Ordre : contrôles (usage, modèle demandé) → réservation → appel → journal → régularisation → contrôle du modèle résolu.
- `src/slmsp/mistral/__init__.py` -- docstring du paquet (rôle, AD-3 verrous 1 et 3, séparation des journaux) ; aucun import de `mistralai` à l'import du paquet.
- `config/juges.toml` + `src/slmsp/judge/config.py` -- section `[second]` : `modele = "mistral-large-latest"`, `temperature = 0.0`, `max_tokens = 4000`, `usage_budget = "juge-second"`, `effort_cache = "temperature-0"`, `format_reponse = "json_schema"` ; `ConfigSecondJuge` et champ `second` dans `ConfigJuges`. Mettre à jour le commentaire d'en-tête du TOML.
- `src/slmsp/judge/second.py` -- `JugeMistral(config, client: ClientMistral, cache, grille)` ; `juger(demandes, echantillon: Collection[str]) -> RapportJugement` : filtre sur l'échantillon (ordre des demandes), prépare (prompt, clé, estimation), lit le cache, puis appels directs un par un avec `session_id = "juge-second-<uuid4 hex>"` par appel à `juger`, `messages=[{"role":"user","content": prompt.texte}]`, `temperature=0`, `response_format={"type":"json_schema","json_schema":{"name":"verdict","schema":prompt.schema,"strict":True}}`. Sorties non conformes, cache, coûts (`cache.journaliser_appel`), `BudgetEpuise` et 4xx comme `JugeClaude` en direct. `ModeleMistralRefuse` remonte à l'appelant (configuration à corriger, pas un aléa).
- `tests/mistral/conftest.py`, `test_config.py`, `test_journal.py`, `test_client.py` -- faux serveur Mistral en `httpx.MockTransport` injecté comme `transport_interne` (route `POST /v1/chat/completions`, corps enregistrés, réponses factices `<verdict-factice>`/JSON) ; registre et tarifs de test dans `tmp_path`. Un test par ligne « client » de la matrice ; refus de lecture du journal du juge par `chemin_autorise(..., "data")` et `(..., "train")`, et acceptation du journal des données ; corps brut journalisé égal octet pour octet au corps servi ; absence de la clé factice dans le journal ; `temperature` et `response_format` présents dans le corps envoyé ; garde `retries` (une seule requête sur 500).
- `tests/judge/test_second.py` -- une ligne de matrice « second juge » par test ; verdict validé au même schéma que le principal (Q et CR) ; imputation `mistral.juge` lue au registre ; aucune ligne dans `appels-mistral.sqlite` après un jugement.
- `tests/judge/test_second_reel.py` -- test unique `reseau` + `payant` : registre réel (`VAR_REEL`), registre plafonné à **0,20 €** (même principe que `RegistrePlafonne`), cache dans `tmp_path`, journaux dans `tmp_path`, items `Q-001` et premier CR du calibrage (sorties comme dans `test_claude_reel.py`). Affiche modèle résolu, tokens et coûts.

**Acceptance Criteria:**
- Given tout appel Mistral, when il part, then une réservation au sous-poste de son `usage` le précède, la requête et la réponse brute intégrale sont journalisées avec leur SHA et le `reservation_id`, et le modèle résolu est vérifié contre la liste stable.
- Given `ClientMistral.appeler(usage="generation")`, when on l'appelle, then `UsageInterdit` sans requête, réservation ni ligne de journal.
- Given l'échantillon du second juge, when il note un item, then il rend un `Verdict` au schéma du principal, avec `temperature=0` dans le corps envoyé, imputé à `mistral.juge`.
- Given `BudgetEpuise` sur `mistral.juge`, when il survient, then les items restants de l'échantillon sont `non-juge` (motif `budget`) et `budget_epuise=True`.
- Given le lecteur `data` ou `train`, when il demande `appels-mistral-juge.sqlite`, then `LectureInterdite`.
- Given `uv run pytest` et `uv run ruff check`, when on les lance, then tout passe (test d'architecture compris), hors échecs préexistants listés hors zone.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 40 findings — high 0, medium 8, low 23, false 9, maybe-false 0
- findings:
  - `[medium]` `[patch]` (BH) `usage_budget` libre : `"validation"` enverrait les prompts d'évaluation dans `appels-mistral.sqlite` (fuite AD-24). — `Literal["juge-second"]` dans `ConfigSecondJuge` ; test de refus.
  - `[medium]` `[patch]` (BH) La clé de cache ne suit ni `temperature` ni `format_reponse`. — `temperature` bornée à 0 ; clé = `effort_cache + "+" + format_reponse` (`effort_cle`) ; test de deux formats.
  - `[low]` `[reject]` (BH) `ModeleMistralRefuse` : appel payé absent de `cache.appels`, rapport partiel perdu. — Le registre (source de vérité) compte l'appel et le journal Mistral le garde ; l'erreur est une configuration à corriger qui arrête le run, comme voulu ; un report de coût ajouterait un champ public pour un cas rare.
  - `[low]` `[reject]` (BH) Une 200 qui échoue à la validation du SDK est comptée au pire cas comme erreur. — Prudent pour le budget ; cas improbable avec un SDK épinglé ; un traitement « non conforme » ajouterait une branche.
  - `[low]` `[reject]` (BH) Corps brut absent si le hook ne se déclenche pas. — SDK épinglé (3.2.0) et égalité octet pour octet du corps testée (`test_appel_nominal_juge_second`) : une montée de version casserait ce test.
  - `[low]` `[reject]` (BH) Pas de ligne de journal sur `KeyboardInterrupt`, et une panne SQLite du journal masque `ErreurApiMistral`. — Réservation comptée au pire cas dans les deux cas ; garde supplémentaire pour un cas exceptionnel.
  - `[low]` `[reject]` (BH) 429 traité item par item, sans arrêt. — Refus non facturé (0 €) ; les items passent `non-juge` et seront repris par le cache au run suivant ; pas de perte d'argent.
  - `[low]` `[reject]` (BH) Ids d'échantillon sans demande ignorés en silence ; chaîne nue découpée en caractères. — La story 5.6 connaît l'échantillon du manifeste et calcule le kappa sur l'effectif disponible ; l'annotation de type couvre la chaîne nue.
  - `[false]` `[reject]` (BH) Dérive de spec non consignée (httpx, journal de la nuit, Auto Run Result). — L'Auto Run Result est écrit à la finalisation et consigne ces écarts ; le journal de la nuit est tenu par l'orchestrateur (consignes).
  - `[low]` `[reject]` (BH) Capture partagée entre appels concurrents, hooks réenregistrés. — Le second juge est séquentiel ; aucun appelant concurrent ni asynchrone.
  - `[medium]` `[patch]` (BH) Tests manquants : jeton du générateur, lignes `erreur-api`, test réel sans contrôle du journal, `_texte` en morceaux. — Tests ajoutés pour le jeton (accepté, import imbriqué en échec), les lignes `erreur-api` (groupé avec VG) et le journal du test réel ; `_texte` en morceaux rejeté (format non utilisé par le juge).
  - `[false]` `[reject]` (BH) Chemin personnel dans la Verification de la spec. — La correction consisterait à modifier la spec du build ; même convention que la story 5.4.
  - `[low]` `[patch]` (BH) Test des commentaires trop étroit (`schema_version` sauté). — `schema_version` commenté et vérifié (groupé avec ECH « schema_version »).
  - `[medium]` `[patch]` (VG) Lignes `erreur-api` du second juge dans `cache.appels()` jamais vérifiées. — Assertions 5xx et 4xx, et test non conforme → 500 → rejugé avec coût cumulé.
  - `[medium]` `[patch]` (VG) `usage_budget` libre (groupé avec BH). — Même correctif.
  - `[low]` `[reject]` (IA) Écart à AD-3 (deux fichiers) et à la lettre d'AD-24 non reporté au spine. — Les documents d'architecture sont en lecture seule (consignes) ; l'écart est consigné ici et remonté au journal de la nuit par le compte rendu.
  - `[false]` `[reject]` (IA) Modèle résolu réel non vérifié. — Vérifié au test payant : l'API renvoie `mistral-large-latest`, accepté par la liste.
  - `[false]` `[reject]` (IA) `json_schema` strict non confirmé. — Confirmé au test payant : Q-001 et CR-001 jugés, schémas acceptés.
  - `[false]` `[reject]` (IA) Le manifeste n'est pas lu. — Choix voulu : l'appelant (5.6) passe `Echantillons.second_juge` ; `judge` ne dépend pas d'`evaluation`.
  - `[false]` `[reject]` (IA) Plafond réel de 5 € non vérifié. — `config/budgets.toml` porte `juge = 5.0` (story 1.5) et l'imputation `juge-second = "mistral.juge"`.
  - `[low]` `[patch]` (IA) Seul le SHA de la réponse est journalisé, pas celui de la requête. — Colonne `sha256_requete` ajoutée et testée.
  - `[low]` `[reject]` (ECH) Nom de journal avec point ou espace final (Windows). — Config versionnée et relue ; garde pour une saisie improbable.
  - `[medium]` `[patch]` (ECH) `usage_budget` libre (groupé avec BH). — Même correctif.
  - `[low]` `[reject]` (ECH) `dossier_journaux` sous `data/`. — Paramètre réservé aux tests ; en production, `SLMSP_VAR_DIR`.
  - `[medium]` `[patch]` (ECH) Température non nulle avec `effort_cache` fixe (groupé avec BH clé de cache). — Même correctif.
  - `[medium]` `[patch]` (ECH) `format_reponse` hors de la clé (groupé avec BH clé de cache). — Même correctif.
  - `[low]` `[reject]` (ECH) Le modèle résolu derrière l'alias peut changer entre deux runs. — L'API renvoie l'alias lui-même ; le changement n'est pas observable côté client (voir risques résiduels).
  - `[low]` `[reject]` (ECH) `echantillon` passé en chaîne nue. — Annotation de type ; appelant unique (5.6).
  - `[low]` `[reject]` (ECH) Ids d'échantillon sans demande (groupé avec BH). — Même motif.
  - `[low]` `[reject]` (ECH) `ModeleMistralRefuse` hors de `cache.appels` (groupé avec BH). — Même motif.
  - `[low]` `[patch]` (ECH) `HoteBloque` avant envoi compté au pire cas. — Un `SlmspError` levé par l'appel est réglé à 0, ligne `erreur` gardée ; test via `ClientMistral`.
  - `[low]` `[reject]` (ECH) `SlmspError` ou `sqlite3.Error` interrompt `juger` sans rapport. — Erreur de configuration ou de disque : l'arrêt est voulu.
  - `[false]` `[reject]` (ECH) Réponse 200 sans `usage` réglée à 0. — `usage` est un champ obligatoire de `ChatCompletionResponse` : le SDK lève une erreur de validation, comptée au pire cas.
  - `[low]` `[reject]` (ECH) Corps brut absent si le hook ne se déclenche pas (groupé avec BH). — Même motif.
  - `[low]` `[patch]` (ECH) Exception entre `reserver` et l'appel (message mal formé) : réservation laissée ouverte. — `parametres` construit avant la réservation ; test.
  - `[low]` `[reject]` (ECH) Appels concurrents sur un même client (groupé avec BH). — Même motif.
  - `[low]` `[reject]` (ECH) `_regler_echec` qui lève dans `finally` masque l'erreur d'API. — Cas exceptionnel (registre illisible) ; l'erreur du registre reste visible.
  - `[false]` `[reject]` (ECH) La spec demande `lib="httpx"`, le code prend `httpx2`. — `mistralai 3.2.0` importe `httpx2 as httpx` : le code est juste, et la correction modifierait la spec. Écart consigné dans l'Auto Run Result.
  - `[low]` `[patch]` (ECH) `schema_version` non commenté dans `mistral.toml`. — Commentaire ajouté.
  - `[false]` `[reject]` (ECH) Rien n'impose `temperature=0`. — Corrigé par le patch de la clé de cache (`temperature` bornée à 0) ; la constatation ne vaut plus.

## Design Notes

**Séparation plutôt que marquage.** La liste d'accès d'AD-24 est appliquée par chemin dans `core.artefacts` (hors zone) : un journal à part est refusé aux lecteurs `data` et `train` sans toucher au lecteur, alors qu'un filtrage à la lecture dépendrait de chaque requête SQL de 9.2. Le schéma de ligne et la colonne `usage` restent communs aux deux fichiers, et chacun refuse les usages de l'autre. AD-3 parle d'un seul fichier `var/appels-mistral.sqlite` : l'écart est assumé, à consigner au journal de la nuit.

**Jeton de preuve.** `_jeton_generateur()` fait `importlib.import_module("slmsp.mistral.generateur")` dans un `try` ; `ModuleNotFoundError` (sur ce nom précis) donne `None`. Un appelant ne peut pas fabriquer le jeton : il faudrait écrire le module de la story 9.2.

**Estimation.** `tokens_entree_estimes = estimer_tokens_entree(prompt)` (story 5.4) ; la majoration du registre s'ajoute.

**Choix pris seul (à consigner dans Auto Run Result) :** journaux séparés ; réservation et coût au tarif du modèle demandé ; `response_format` `json_schema` strict avec le schéma de la story 5.4 (à confirmer par le test réel, sinon `json_object`) ; `max_tokens = 4000` ; second juge en appels directs uniquement (5 € suffisent pour environ 45 items) ; `effort_cache = "temperature-0"` dans la clé de cache.

## Verification

**Commands:**
- `uv sync --extra data --extra judge` -- expected: `mistralai 3.2.0` et `anthropic 1.13.0` installés
- `uv run pytest tests/mistral tests/judge -q` -- expected: tout passe (tests réels désélectionnés)
- `uv run pytest -q` -- expected: aucun échec hors échecs préexistants listés
- `uv run ruff check` et `uv run ruff format --check src/slmsp/mistral src/slmsp/judge tests/mistral tests/judge` -- expected: propre
- `$env:SLMSP_ENV_FILE='C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\.env'; uv run pytest tests/judge/test_second_reel.py -m "reseau and payant" -s` -- expected: 2 verdicts valides, coût total ≤ 0,20 €. Payant : l'implémenteur ne le lance **jamais** ; seul l'orchestrateur de la story le lance, une fois, après la revue.

## Auto Run Result

**Statut :** done. La revue a eu lieu en 4 couches (40 constats) et les correctifs ont été appliqués. Le test payant a été lancé une fois par l'orchestrateur et a réussi.

**Résumé :** le paquet `slmsp.mistral` (config, journal, client) et le second juge `slmsp.judge.second.JugeMistral` sont en place.
- **Client.** Chaque appel Mistral fait une réservation au sous-poste de son usage, puis un appel unique sans relance. Il est journalisé : requête canonique et son SHA, corps brut de la réponse et son SHA, `reservation_id`. Il est ensuite régularisé, puis le modèle résolu est vérifié contre la liste stable.
- **Usage `generation`.** Il est refusé, sauf avec le jeton du futur module `slmsp.mistral.generateur` (story 9.2).
- **Journaux séparés.** Les appels `juge-second` vont dans `SLMSP_VAR_DIR/appels-mistral-juge.sqlite`, que `core.artefacts` refuse aux lecteurs `data` et `train`. Les appels `generation` et `validation` vont dans `appels-mistral.sqlite`. Chaque journal refuse les usages de l'autre, et des déclencheurs SQLite le rendent ajout seul.
- **Second juge.** Il reprend le prompt, le schéma, la validation et le cache de la story 5.4. Il appelle avec `temperature=0` et `response_format` `json_schema` strict, imputé à `mistral.juge`. Sur `BudgetEpuise`, les items restants passent `non-juge` (motif `budget`).

**Fichiers :**
- `config/mistral.toml`, `src/slmsp/mistral/config.py` : modèle `mistral-large-latest`, liste stable, motifs interdits, noms des deux journaux.
- `src/slmsp/mistral/journal.py` : `JournalMistral`, `journal_pour`, `UsageInterdit`.
- `src/slmsp/mistral/client.py` : `fabriquer_sdk`, `ClientMistral`, `ModeleMistralRefuse`, `ErreurApiMistral`.
- `src/slmsp/mistral/__init__.py` : docstring seule, aucun import de `mistralai`.
- `config/juges.toml`, `src/slmsp/judge/config.py` : section `[second]` et `ConfigSecondJuge` (`usage_budget` fixé à `juge-second`, `temperature` à 0).
- `src/slmsp/judge/second.py` : `JugeMistral.juger(demandes, echantillon)`.
- `tests/mistral/*`, `tests/judge/test_second.py`, `tests/judge/test_second_reel.py`.

**Revue :** 40 constats, soit 8 medium, 23 low et 9 false.
- 12 constats corrigés (patch), regroupés en 9 correctifs, dont 3 entrées medium :
  - `usage_budget` fermé ;
  - température et format dans la clé de cache ;
  - tests des lignes `erreur-api` et du jeton.
- Correctifs low : SHA de la requête, `HoteBloque` réglé à 0, paramètres construits avant la réservation, `schema_version` commenté, contrôle du journal dans le test réel.
- 28 constats rejetés ; le motif de chacun est dans le Review Triage Log.
- Aucun différé.

**Relecture complémentaire recommandée :** oui. Trois entrées medium ont été corrigées, et un risque reste non vérifié. L'API Mistral renvoie l'alias `mistral-large-latest` dans le champ `model`. Le contrôle du « modèle résolu » ne voit donc pas la version sous-jacente : seul le motif Labs ou préversion d'un nom renvoyé serait détecté.

**Vérification :**
- `uv run pytest tests/mistral tests/judge tests/test_architecture.py` : 280 réussis, 2 désélectionnés (tests réels).
- `uv run ruff check` et `ruff format --check` : propres.
- `uv run pytest` complet : 2371 réussis, 157 ignorés, 2 en échec, tous deux préexistants et hors zone :
  - l'item CT de `tests/harness/test_prompts.py` (zone 4.2) ;
  - `tests/inference/test_serveur.py::test_demarrage_rate_sante`, instable sous charge (déjà relevé en 5.4).

  Un premier passage avait échoué sur `tests/budget/test_concurrence.py::test_critere_6…`, test instable connu ; il passe au second passage.
- **Test payant** (une fois, registre réel, plafond 0,20 €) : Q-001 et CR-001 ont été jugés. Le `json_schema` strict a été accepté, le modèle résolu est `mistral-large-latest` et les deux lignes de journal sont `ok`. Coût réel : **0,0139 €**.

**Choix pris seul :**
- **Journaux séparés** plutôt que marqués. C'est un écart assumé à AD-3, qui décrit un fichier unique, et à la lettre d'AD-24 (« les journaux ») : à reporter au journal de la nuit et à valider par Anaël.
- **Client HTTP `httpx2`** (la spec disait `httpx`) : `mistralai 3.2.0` importe `httpx2 as httpx`.
- **Coût et réservation** au tarif du modèle demandé.
- **Sortie du second juge :** `max_tokens = 4000`, appels directs seulement, et `json_object` gardé en repli de configuration.
- **Clé de cache** : effort `temperature-0+<format>`.
- **Codes d'erreur :** un 4xx (429 compris) est réglé à 0, et un 401 ou un 403 arrête le run du second juge.
- **Erreurs locales :** une erreur `SlmspError` levée avant envoi (garde réseau) est réglée à 0.
- **Modèle :** `ModeleMistralRefuse` remonte à l'appelant, et `JugeMistral` refuse un modèle de `juges.toml` différent de celui de `mistral.toml`.
- **Mécanisme de capture :** corps brut capturé par un hook `after_success` du SDK (API interne `sdk_configuration._hooks`, version épinglée).
- **Liste stable :** `mistral-large-latest`, `mistral-large-2411`, `mistral-large-2512`.

**Risques résiduels :**
- le contrôle du modèle résolu ne voit que l'alias (voir plus haut) ;
- les hooks reposent sur une API interne du SDK : une montée de version casserait le test d'égalité du corps brut ;
- un 429 n'arrête pas le run : les items restants passent `non-juge` sans coût.
