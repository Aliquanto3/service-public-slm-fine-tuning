---
title: 'Story 4.2 — AssistantService : flux d''évènements, Question fondée sur l''Index local, Tâches de rédaction'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '001df9ccc4395314daaa12615d432496418c9652'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Les items CT réels (story 7.5) portent une clé « type » que construire_messages (story 4.1) refuse.
    evidence: |-
      tests/harness/test_prompts.py::test_items_reels_passent_construire_messages[CT.jsonl] échoue déjà à la révision de base 001df9c (EntreeInvalide : clé d'entrée « type » inconnue). Ni prompts.py ni eval/construction ne sont dans la zone de la 4.2.
    location: >-
      src/slmsp/harness/prompts.py:185
    severity: medium
  - summary: >-
      Granite 1B de base n'écrit aucun renvoi [n] : la Question renvoie Sources vide malgré des passages pertinents.
    evidence: |-
      tests/harness/test_integration_question.py (Granite) est en xfail : 5 passages réels F21089 au-dessus du seuil, réponse sans renvoi. Le témoin Qwen3 4B cite [1] à [4] avec le même Harnais. À traiter par le choix du modèle ou l'affinage, pas par le Harnais (le texte n'est jamais réécrit).
    location: >-
      tests/harness/test_integration_question.py
    severity: medium
---

<intent-contract>

## Intent

**Problem:** Le Harnais n'a pas encore de service : ni flux d'évènements, ni Question fondée sur l'Index local, ni Tâches de rédaction. La CLI (4.5), le banc (5.3), `data` (9.4) et l'application en dépendent. Deux reports bloquent aussi : le module `harness/taches.py` (4.1) masquerait le paquet `harness/taches/`, et `LlmPort.generer` ne déclare pas `AppelNonConforme` (2.2).

**Approach:** On crée `AssistantService.repondre(tache, messages, options)`, un service sans état qui valide l'entrée tout de suite, puis délègue à un traitement chargé paresseusement par un registre (`harness/taches/`). Ce traitement fait la recherche dans l'Index pour Q, appelle `construire_messages`, diffuse la génération du LLM et contrôle les citations (`harness.citations`). Le contenu de `harness/taches.py` passe dans `harness/taches/__init__.py`, avec la même API publique.

## Boundaries & Constraints

**Always:**
- AD-7 : le prompt est composé uniquement par `construire_messages`. Le service se contente d'insérer l'historique fourni par l'appelant entre `system` et le nouveau `user`, et valide le tout avec `valider_conversation`.
- AD-14 / FR-1 : aucun état entre deux appels. Tâche `None` → Q (`defaut`).
- Tâches de rédaction (CR, LC, CO, RE, CT, NR, TR) : `tools=None`, et le contexte ne contient ni `ToolPort`, ni Mode, ni recherche dans l'Index. Pas d'avertissement juridique. TR émet l'avertissement FR-18 de la table (code `traduction-automatique`), distinct de l'avertissement juridique de Q (code `avis-juridique`).
- Erreurs de l'appelant (Tâche inconnue ou inactive, module de traitement absent, conversation invalide, entrée invalide) : `SlmspError` levée **au moment de l'appel** à `repondre`, avant toute itération. Erreurs d'exécution (LLM, embedder, Index) : un évènement `Erreur(code="erreur-interne", message="Un problème est survenu. Votre texte est conservé.")` clôt le flux. Le détail part au logger `slmsp.harness`, avec la classe de l'exception, son message où les textes saisis sont masqués, et la pile sans les variables locales.
- `k` et `seuil_pertinence` sont lus par `slmsp.index.config` (source unique). Un passage est pertinent si `score >= seuil`.
- Tests sans réseau, sans modèle réel (sauf le test `integration`), avec des chaînes factices générées dans le test (D1.1).

**Never:**
- Toucher hors de la zone. Exceptions, tenues au minimum : `core/ports.py` (report), `core/evenements.py` (champs `Fin.urls_inventees` et `Source.numero`, avec valeur par défaut, exigés par les AC 2 et 4), et le remplacement de `harness/taches.py`. Ne pas toucher à `sprint-status.yaml`, à `pyproject.toml` ni aux documents de décision.
- Réécrire le texte généré (D-nuit-A2-17) ; inventer une source ; lister une source non citée.
- Écrire `taches/recherche.py`, `taches/compte_rendu.py` ou `harness/modes.py` (4.3, 4.4).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Q avec passages | 3 passages ≥ seuil, sortie qui cite `[1]` et `[3]` | `Jeton`… puis `Sources([n°1, n°3])` (titre, URL, date, extrait), `Avertissement(avis-juridique)`, puis `Fin` | — |
| Q sans passage pertinent | tous les scores < seuil | prompt avec `AUCUN_PASSAGE`, `Sources([])`, `Avertissement`, `Fin` | pas d'erreur |
| Citation hors plage | `[9]` avec 2 passages | ignorée dans `Sources` | — |
| URL inventée | sortie avec une URL absente des passages, des résultats d'outils et des textes saisis | `Fin.urls_inventees=[url]`, texte intact | — |
| Rédaction | LC, texte collé | `tools=None`, aucun espion appelé, pas de `Sources` ni d'avertissement juridique | — |
| TR | texte | `Avertissement(traduction-automatique)` | — |
| Entrée objet | `options["entree"]` dict (banc) | utilisé tel quel | `EntreeInvalide` levée tout de suite |
| Entrée brute, Tâche objet | LC + texte utilisateur seul | `{premier emplacement de CLES_CONTENU du prompt : texte}` | — |
| RD avant la 4.3 | `tache="RD"` | — | `TacheIndisponible` levée tout de suite |
| Conversation invalide | vide, `system` fourni, ou dernier message non `user` | — | `ConversationInvalide` tout de suite |
| Erreur du modèle | `FakeLlm` lève une exception pendant le flux | `Erreur` sans détail, aucun `Fin` après ; log sans le texte saisi | — |
| Appel d'outil inattendu | `AppelOutil` émis alors que `tools=None` | `AppelNonConforme(motif=…)`, jamais exécuté | — |

</intent-contract>

## Code Map

- `src/slmsp/harness/taches.py` -- 4.1 : `CODES_TACHES`, `EMPLACEMENTS(_TEXTE)`, `PromptTache`, `Tache`, `TableTaches`, `TacheInconnue`, `VarianteInconnue`, `charger_taches`. À déplacer **tel quel** dans `taches/__init__.py`. Importé par `harness/prompts.py:41`, `tests/harness/test_taches.py:15` et `test_prompts.py:30`.
- `src/slmsp/harness/prompts.py:217` -- `construire_messages(tache, entree, passages, outils, *, variante)` → `[system, user]` ; `CLES_CONTENU`, `EntreeInvalide`, `AUCUN_PASSAGE`. Lecture seule.
- `config/taches.toml` -- `avertissement` de Q (« Ne vaut pas avis juridique. ») et de TR (« Traduction automatique, à vérifier. »). Lecture seule.
- `src/slmsp/core/evenements.py:107` -- `Fin(raison, usage)` ; `Source(titre, url, origine, date, extrait)` (ligne 54). Ajouter `Fin.urls_inventees: list[str] = []` et `Source.numero: int | None = None`.
- `src/slmsp/core/ports.py:44` -- `LlmPort.generer -> Iterator[Jeton | AppelOutil | Fin]`. Ajouter `AppelNonConforme` (report 2.2, `spec-2-2` `deferred`).
- `src/slmsp/core/messages.py:107` -- `valider_conversation`, `ConversationInvalide`.
- `src/slmsp/index/config.py:96` -- `charger_config_index()` → `.k` (5), `.seuil_pertinence` (0.5).
- `src/slmsp/index/lecture.py:79,313` -- `IndexLocal` (`VectorStore`), `ouvrir_index(racine, version)` ; l'Index réel est dans `<dépôt principal>/index/20260926/`.
- `src/slmsp/inference/client.py:33,258,366` -- `OPTIONS_AUTORISEES` (une clé inconnue lève `ValueError`) ; `Fin.usage` porte déjà `delai_premier_token_ms`.
- `src/slmsp/inference/serveur.py:339,575,587` -- `ServeurLlama(config, "cpu", slug=…)`, `.client()`, `.embedder()`. Modèle à imiter pour le test réel : `tests/inference/test_serveur.py:483-517` (`config_granite`, `GRANITE_GGUF`, `BGE_GGUF`, marqueurs `lent` + `integration` enregistrés par un `conftest`).
- `tests/test_architecture.py:28` -- `harness` = couche 3 : il peut importer `core`, `index`, `mcp` et `inference`, mais pas `torch` ni un client HTTP.
- `src/slmsp/core/config.py:48,77` -- `ModeleConfig` (extra forbid), `charger_toml`, `racine_projet`.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/harness/taches.py` → `src/slmsp/harness/taches/__init__.py` -- déplacer le contenu (`git mv`), puis ajouter :
  - `TacheIndisponible(SlmspError)` ;
  - `MODULES_TRAITEMENT` (Q → `question`, RD → `recherche`, CR → `compte_rendu`, les autres → `redaction`), avec le repli `compte_rendu` → `redaction` ;
  - `traitement(code)` paresseux et mis en cache, qui lève `TacheIndisponible` si le module manque et qu'aucun repli n'existe ;
  - `ContexteTache` (dataclass figée : `tache`, `entree`, `historique`, `textes_saisis`, `llm`, `config`, `options_llm`, `recherche`, `outils`, `mode`, avec `messages_pour(construits)`) ;
  - `diffuser(ctx, messages, tools=None)`, générateur qui renvoie `(texte, fin)` ;
  - `avertissement(tache)`, qui produit l'`Avertissement` codé selon `CODES_AVERTISSEMENT`.
  -- Ces éléments sont partagés par 4.2, 4.3 et 4.4.
- `src/slmsp/harness/taches/question.py` -- `traiter(ctx)` : recherche, `construire_messages`, `diffuser`, `Sources` des passages cités, avertissement, puis `Fin` avec `urls_inventees`.
- `src/slmsp/harness/taches/redaction.py` -- `traiter(ctx)` : `construire_messages` sans passage ni outil, `diffuser`, avertissement de la table s'il existe (TR), `Fin` avec `urls_inventees`.
- `src/slmsp/harness/citations.py` --
  - `extraire_urls`, `normaliser_url`, `urls_inventees(texte, passages=(), resultats_outils=(), textes_fournis=())` : les URL connues viennent des URL et des textes des passages, de toutes les chaînes des résultats d'outils (parcours récursif), et des textes saisis ;
  - `numeros_cites(texte, nb)` (`[n]`, `[n, m]`, `[n-m]`, dans la plage, ordre de première apparition) ;
  - `sources_citees(texte, passages)`.
- `src/slmsp/harness/recherche_index.py` -- `RechercheIndex(embedder, vector_store, k, seuil).rechercher(requete) -> list[Passage]` (score ≥ seuil) ; `depuis_config(...)`.
- `src/slmsp/harness/config.py` + `config/harnais.toml` --
  - `ConfigHarnais`, figée : `outils` (`iterations_max`, `delai_appel_s`), `modes` (`periode_sonde_s`, `delai_sonde_s`), `compte_rendu` (`reserve_sortie_tokens`, `chevauchement_paragraphes`), `recherche` (`k`, `seuil_pertinence`, lus par `charger_config_index`) ;
  - `charger_config_harnais(chemin=None, *, config_index=None)`.
- `src/slmsp/harness/service.py` -- `AssistantService(llm, embedder, vector_store, outils, mode, config, *, taches=None)` ; `repondre(tache=None, messages=…, options=None)`. Le service :
  - valide tout de suite, puis renvoie le générateur ;
  - mesure `delai_premier_token_ms` depuis le début de l'itération jusqu'au premier `Jeton`, et l'écrit dans `Fin.usage` ;
  - garantit un `Fin` final, ou un `Erreur` final ;
  - retire `entree` des options transmises au LLM.
- `src/slmsp/core/evenements.py`, `src/slmsp/core/ports.py` -- les champs et l'annotation décrits dans le Code Map.
- `tests/harness/factices.py` + `tests/harness/conftest.py` -- `FakeLlm` (scripts d'évènements ou d'exceptions, enregistre messages, tools et options), `FakeEmbedder`, `FakeVectorStore`, `SpyToolPort`, `SpyModePort` et `SpyNetGate` (échouent s'ils sont appelés). Le `conftest` enregistre aussi le marqueur `integration`.
- `tests/harness/test_service.py`, `test_question.py`, `test_redaction.py`, `test_citations.py`, `test_recherche_index.py`, `test_config_harnais.py` -- toute la matrice I/O et les AC ; `tests/core/test_ports.py` et `test_evenements.py` -- les nouveaux champs et l'annotation.
- `tests/harness/test_integration_question.py` -- `lent` + `integration` : Granite 1B CPU, BGE-M3 CPU et l'Index réel (racine : `SLMSP_INDEX_RACINE`, sinon la racine du projet, sinon le dépôt principal via `git rev-parse --git-common-dir`). Le test vérifie des `Sources` réelles et l'avertissement juridique ; il est sauté si un fichier manque.

**Acceptance Criteria:**
- Given deux appels successifs, when `repondre` est appelé, then aucun état ne passe d'un appel à l'autre (même sortie pour la même entrée) et tous les évènements sont des types de `core.evenements`.
- Given des options `temperature=0, seed=7`, when le service appelle `LlmPort`, then elles sont transmises telles quelles (sans `entree`), et `Fin.usage` porte l'usage du modèle et `delai_premier_token_ms`.
- Given une conversation de plusieurs tours, when on répond, then `messages` envoyés = `[system] + historique + [user construit]`, validés par `valider_conversation`.
- Given `uv run pytest tests/harness -m integration` avec les modèles et l'Index du dépôt principal, when on pose une Question, then le flux contient des `Jeton`, des `Sources` réelles (URL de l'Index) et l'avertissement juridique.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Passe de revue
- verdicts : 34 constats — high 0, medium 2, low 21, false 11, maybe-false 0.
- constats :
  - **Verification Gap**
    - `[low]` `[patch]` Une entrée texte valide passée par `options["entree"]` n'est jamais testée. Ajout de `test_entree_texte_par_options` (embedder, messages et options vérifiés).
  - **Intent Alignment**
    - `[false]` `[reject]` « NetGate non appelé par construction ». Le service ne reçoit aucun NetGate ; le contexte de rédaction n'a ni outils, ni Mode, ni recherche, ce qu'un test vérifie. Le test du document témoin est l'AC 4 de la story 4.5.
    - `[low]` `[reject]` URL connues élargies aux textes saisis. Choix documenté dans les Design Notes : il évite les faux signalements en rédaction. Le banc appellera la même fonction.
    - `[low]` `[reject]` Le texte de la spec ne citait pas le témoin Qwen. Le corriger revient à modifier la spec : c'est fait dans le résultat final.
    - `[medium]` `[patch]` Masquage partiel des textes saisis dans le journal. Groupé avec le constat Blind Hunter n°2.
    - `[low]` `[reject]` La recherche ne porte que sur le dernier message `user`. Reformuler une question de suivi demande une conception à part, en J4. L'historique est bien transmis au modèle.
    - `[false]` `[reject]` `Fin(interrompue)` sur un flux coupé. C'est le comportement de `inference/client.py` pour un flux coupé, et l'UX ne l'interdit pas.
    - `[false]` `[reject]` FR-18 traité au niveau évènement. C'est la lecture voulue : pas de réécriture du texte (D-nuit-A2-17).
    - `[false]` `[reject]` Un CR long passe par la rédaction. Le repli `compte_rendu` vers `redaction` est prévu par la story « tant que `compte_rendu` n'existe pas » (4.4).
    - `[false]` `[reject]` L'émission d'`AppelNonConforme` par l'adaptateur n'est pas testée ici. Elle est testée par `tests/inference/test_client.py` (story 2.2).
  - **Blind Hunter**
    - `[low]` `[reject]` Une option LLM inconnue échoue tard. Les options viennent de la racine de composition, pas de l'Agent. Les valider dans le Harnais couplerait le service à l'adaptateur (AD-1).
    - `[medium]` `[patch]` `masquer` ignorait les formes échappées en JSON, et les clés de l'entrée objet masquaient des mots ordinaires. Correctifs : masquage de `json.dumps(fragment)[1:-1]`, et seules les valeurs sont collectées (`chaines(..., cles=False)`). Tests ajoutés.
    - `[low]` `[reject]` Multi-tour : la recherche ne porte que sur le dernier tour, et les URL d'un tour précédent sont signalées. Le signalement ne réécrit rien, et la conception du multi-tour relève de J4. Consigné en risque résiduel.
    - `[low]` `[reject]` La taille du contexte n'est pas contrôlée. La politique de troncature est à concevoir (4.4, J4). En attendant, un dépassement donne un `Erreur` propre. Risque résiduel.
    - `[low]` `[reject]` Les URL sans schéma ne sont pas extraites. Il faudrait une heuristique de domaines, source de faux positifs, pour un cas rare.
    - `[low]` `[patch]` Un renvoi de plus de 4 300 chiffres fait échouer `int()`. Chaque nombre est désormais limité par `\d{1,6}`. Test ajouté.
    - `[low]` `[patch]` Tests manquants. Ajout de `test_fermeture_du_flux_ferme_le_modele` et de `test_erreur_du_vector_store`. Le cas d'un import de module qui échoue est rejeté (constat suivant).
    - `[false]` `[reject]` Un module de traitement qui échoue à l'import lève une erreur hors `SlmspError`. C'est une erreur de programmation qui doit échouer bruyamment.
    - `[low]` `[reject]` `_tache` accepte n'importe quel objet `Tache`. C'est une surface voulue pour les appelants internes. La casse des codes sera traitée par les choix de la CLI (4.5).
    - `[low]` `[reject]` Frontmatter de la spec incomplet. La correction est une modification de la spec, faite à la finalisation.
    - `[false]` `[reject]` Le test d'intégration ne tourne que sous Windows. Le projet vise uniquement Windows 11 natif (D2).
    - `[false]` `[reject]` Les tests de configuration figent des valeurs. Les stories 4.3 et 4.4 lisent ces valeurs sans les modifier (D-nuit-A3-2) : elles font partie du contrat.
  - **Edge Case Hunter**
    - `[low]` `[patch]` Dépassement de `int()` sur un renvoi : doublon du Blind Hunter, même correctif.
    - `[low]` `[patch]` `urlsplit` lève `ValueError` (caractère `／` pleine chasse, `[` non fermé) et le flux se termine en `Erreur`. Repli sur une forme simple en minuscules. Test ajouté.
    - `[low]` `[patch]` Une URL de passage avec parenthèses, citée telle quelle, était signalée comme inventée. Les formes de `extraire_urls(passage.url)` sont ajoutées aux URL connues. Test ajouté.
    - `[low]` `[patch]` Avec `tools=[]`, `diffuser` relayait l'`AppelOutil`. La condition devient `if not tools`. Test ajouté.
    - `[low]` `[reject]` Option LLM inconnue : doublon du Blind Hunter, même motif.
    - `[medium]` `[patch]` Masquage des formes échappées : groupé avec le constat Blind Hunter n°2.
    - `[low]` `[patch]` Les clés de l'entrée objet masquaient des mots du journal : groupé avec le constat Blind Hunter n°2.
    - `[false]` `[reject]` Un module sans `traiter` lève `AttributeError`. C'est une erreur de programmation qui doit échouer bruyamment.
    - `[false]` `[reject]` Une Tâche d'un type inattendu lève `TypeError`. La signature est typée.
    - `[low]` `[patch]` Le test réel décomposait les évènements avant de vérifier le `Fin`. Il vérifie d'abord `isinstance(evenements[-1], Fin)`.
    - `[low]` `[reject]` L'AC 4 était déclarée satisfaite avec Granite. Le résultat final le corrige : Granite est en `xfail`, et le témoin Qwen montre la chaîne complète.
    - `[false]` `[reject]` `chaines` ne parcourt pas les dataclasses. Les résultats d'outils sont du JSON (dicts) renvoyé par `ToolPort.appeler`.

## Design Notes

Ordre du flux pour Q : `Jeton*`, `Sources`, `Avertissement`, `Fin`. Pour la rédaction : `Jeton*`, puis l'`Avertissement` éventuel (TR), puis `Fin`. `Sources` ne liste que les passages cités, chacun avec son `numero` : une réponse sans renvoi `[n]` donne donc `Sources([])`. Ce choix suit la lecture littérale de l'AC 2 et d'UX (« une puce ne peut exister sans source réelle »). Il évite aussi de gonfler la mesure du banc.

Les textes saisis (contenus `user` et chaînes de `options["entree"]`) comptent comme des URL connues. Sinon, une URL présente dans un texte à réécrire serait signalée à tort.

## Verification

**Commands:**
- `uv run pytest tests/harness tests/core -q` -- expected: tout passe.
- `uv run pytest -q` -- expected: aucun échec nouveau.
- `uv run ruff check` -- expected: aucune erreur.
- `SLMSP_VENDOR_DIR=… SLMSP_MODELS_DIR=… uv run pytest tests/harness -m integration -s` -- expected: le test réel passe et affiche la réponse, les sources et l'avertissement.

## Auto Run Result

Status: done

**Résumé.** `AssistantService.repondre(tache, messages, options)` est un service sans état :
- les erreurs de l'appelant (`SlmspError`) sont levées dès l'appel ;
- la réponse est un flux d'évènements typés.

La story couvre :
- **Question fondée sur l'Index local** : top-k avec seuil, `Sources` numérotées, avertissement juridique et `Fin.urls_inventees` ;
- **Tâches de rédaction** : sans outil, sans Index et sans réseau. La Traduction porte son propre avertissement FR-18 (`traduction-automatique`), distinct de l'avertissement juridique.

Les deux reports sont traités :
- `harness/taches.py` a été déplacé par renommage dans `harness/taches/__init__.py`, qui porte en plus le registre paresseux ;
- `LlmPort.generer` déclare `AppelNonConforme`.

**Fichiers.**
- `src/slmsp/harness/service.py` : `AssistantService`, masquage du journal, délai au premier token.
- `src/slmsp/harness/taches/__init__.py` :
  - table des Tâches (4.1) ;
  - `MODULES_TRAITEMENT`, avec le repli de CR vers la rédaction ;
  - `ContexteTache`, `diffuser`, `avertissement`.
- `src/slmsp/harness/taches/question.py` et `redaction.py` : traitements de Q et de la rédaction.
- `src/slmsp/harness/citations.py` : URL, renvois `[n]` et `sources_citees`. C'est la fonction unique, réutilisable par le banc.
- `src/slmsp/harness/recherche_index.py` : `RechercheIndex`, avec `k` et le seuil lus par `slmsp.index.config`.
- `src/slmsp/harness/config.py` et `config/harnais.toml` : `ConfigHarnais`.
- `src/slmsp/core/evenements.py` (hors zone, autorisé par la spec) : `Fin.urls_inventees` et `Source.numero`, avec des valeurs par défaut.
- `src/slmsp/core/ports.py` (report de la 2.2) : `AppelNonConforme` dans le type de retour de `generer`.
- Tests :
  - `tests/harness/{factices,conftest,test_service,test_question,test_redaction,test_citations,test_recherche_index,test_config_harnais,test_integration_question}.py` ;
  - `tests/core/{test_ports,test_evenements}.py`.

**Revue.** 34 constats : 0 high, 2 medium, 21 low, 11 false.
- **Corrigés** (1 entrée medium et 7 entrées low) :
  - masquage du journal ;
  - test de l'entrée texte passée par les options ;
  - borne des renvois `[n]` ;
  - repli de `normaliser_url` ;
  - URL de passage avec parenthèses ;
  - `tools=[]` ;
  - tests de fermeture du flux et d'erreur du `VectorStore` ;
  - garde du test réel.
- **Reportés** : aucun constat de revue. Les points ouverts hors zone sont dans `deferred`.
- **Rejetés** : les autres, avec leur motif dans le journal de tri.

**Revue de suivi recommandée : false.** Une seule entrée medium a été corrigée, et aucune high.

**Vérification.**
- `uv run ruff check` et `ruff format --check` : propres.
- `uv run pytest -q` : 2030 passés, 164 ignorés, 1 échec.
  - L'échec existait avant la story et sort de sa zone : `tests/harness/test_prompts.py::test_items_reels_passent_construire_messages[CT.jsonl]`.
  - Les items CT de la 7.5 portent une clé `type` que `construire_messages` (4.1) refuse. Ce point est reporté dans `deferred`.
- Test réel : `uv run pytest tests/harness/test_integration_question.py -m integration -s`, avec `SLMSP_VENDOR_DIR` et `SLMSP_MODELS_DIR` du dépôt principal. Résultat : 1 passé, 1 xfail, en 93 s.
  - **Index `20260926`** : 5 passages réels au-dessus du seuil (fiche F21089, score d'environ 0,79).
  - **Granite 1B en CPU** : les points suivants sont vérifiés :
    - les `Jeton` ;
    - l'ordre `Sources`, `Avertissement`, `Fin` ;
    - l'avertissement « Ne vaut pas avis juridique. » ;
    - le délai au premier token ;
    - l'absence d'URL inventée.

    Granite 1B de base n'écrit en revanche aucun renvoi `[n]`, donc `Sources` reste vide. Le test est marqué xfail explicitement.
  - **Témoin Qwen3 4B en CPU**, même Harnais : la réponse cite `[1]`, `[4]`, `[3]` et `[2]`. `Sources` contient 4 sources réelles (URL service-public F21089, date 2026-09-25), suivies de l'avertissement juridique. La chaîne complète est donc démontrée avec des citations réelles.
- Aucune dépense d'API.

**Décisions prises seul.**
- Les erreurs de l'appelant sont levées dès l'appel, après une validation préalable par `construire_messages` sans passage.
- `delai_premier_token_ms` est mesuré par le service : il inclut la recherche.
- `Sources` ne contient que les passages cités par `[n]`, selon une lecture littérale de l'AC 2 et de l'UX.
- Sont aussi traitées comme URL connues :
  - les URL des textes saisis ;
  - celles des messages `tool` de l'historique ;
  - celles contenues dans le texte des passages.
- Codes d'avertissement : `avis-juridique` (Q) et `traduction-automatique` (TR).
- Valeurs de `config/harnais.toml` : 5 itérations, 10 s par appel d'outil, sonde toutes les 300 s avec un délai de 3 s, réserve de sortie de 1024 tokens, chevauchement d'1 paragraphe.
- Le test réel est paramétré avec Qwen3 4B comme témoin, en plus de Granite 1B.

**Risques résiduels.**
- Granite 1B de base ne suit pas la consigne de citation. C'est à suivre pour la Baseline et l'affinage.
- En multi-tour, la recherche ne porte que sur le dernier message.
- La taille du contexte n'est pas contrôlée : un dépassement produit une `Erreur`.
- Le masquage du journal est fait au mieux et ne couvre pas un extrait tronqué.
- `test_demarrage_rate_sante` (2.2) est instable sous charge : un échec observé pendant l'implémentation, aucun lors des vérifications finales.
