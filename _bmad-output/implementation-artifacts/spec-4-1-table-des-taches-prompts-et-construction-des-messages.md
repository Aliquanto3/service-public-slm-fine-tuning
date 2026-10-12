---
title: 'Story 4.1 — Table des Tâches, prompts de Tâche et construction unique des messages'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: 'ab6a93571a20539d05839ac1778f0660b7854891'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Le module harness/taches.py entrera en collision avec le paquet harness/taches/ que crée la story 4.2.
    evidence: |-
      epics.md place harness/taches.py dans la story 4.1 et harness/taches/__init__.py dans la story 4.2. Quand un paquet et un module portent le même nom, Python importe le paquet. Le module devient alors invisible, et l'import de prompts.py (EMPLACEMENTS_TEXTE, Tache, VarianteInconnue) casse. La story 4.2 doit déplacer le contenu de taches.py dans le paquet ou le réexporter.
    location: >-
      src/slmsp/harness/taches.py
    severity: medium
---

<intent-contract>

## Intent

**Problem:** L'inférence (4.2 à 4.4), le banc (5.3), les benchmarks (6.3), le pipeline `data` (9.2, 9.4) et `train` (10.2) doivent voir exactement la même forme d'entrée. Il n'existe encore ni table des Tâches, ni prompt de Tâche, ni fonction unique qui construit les messages (AD-7, AD-14).

**Approach:** Une table `config/taches.toml` (9 codes), onze prompts système `config/prompts/taches/*.md` faits de consignes seulement, un validateur structurel commun dans `core.gabarits` (AD-3 verrou 6, D-nuit-A2-8), un chargeur `harness.taches` et une fonction pure `harness.prompts.construire_messages(tache, entree, passages, outils)` avec `formater_passages`.

## Boundaries & Constraints

**Always:**
- D1.1 et D-nuit-A1-10 : les prompts de Tâche sont des instructions sans aucun exemple. Pas de question ou réponse modèle, pas de réponse cible, pas de few-shot, pas d'amorce, pas de ligne de dialogue, pas d'emplacement rempli à titre d'illustration. Ils seront réutilisés tels quels comme entrée d'entraînement.
- Les fixtures de test sont des chaînes manifestement factices (`"<texte-factice-1>"`) ou générées dans le test, jamais du contenu réaliste.
- `construire_messages` est pure : aucune lecture de fichier, aucun état. La même entrée donne le même JSON canonique à l'octet près. Sa sortie passe `core.messages.valider_conversation`.
- `harness` n'importe que `core` et `mcp` (couche inférieure, AD-1), sans dépendance lourde (AD-2).
- Toute config passe par `core.config.charger_toml`, avec des modèles `ModeleConfig`.

**Never:**
- Toucher à un fichier hors de la zone (`config/taches.toml`, `config/prompts/taches/`, `core/gabarits.py`, `harness/{taches,prompts}.py`, leurs tests), à `sprint-status.yaml` ou aux documents de décision.
- Écrire `harness/service.py`, `harness/config.py` ou `harness/taches/` (stories 4.2 à 4.4). Le module `harness/taches.py` reste un module : la story 4.2 le convertira en paquet si besoin.
- Rendre les outils dans le texte des messages : `tools` va au chat template (AD-7).
- Appeler le réseau ou une API.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Question avec passages | Q, entrée texte, 2 `Passage` | `[system(consigne Q), user("Passages de l'Index local :\n[1] …\n\n[2] …\n\nQuestion :\n<entrée>")]` | — |
| Question sans passage | Q, `passages=[]` ou `None` | bloc passages = phrase fixe « Aucun passage pertinent n'a été trouvé dans l'Index local. » | — |
| NR | entrée texte, sans passage | `user.content == entree` verbatim | — |
| Entrée objet (CR, LC, CO, RE, CT, TR) | dict à clés nommées | une section par clé, ordre fixe `ORDRE_CLES`, « Libellé :\nvaleur », séparées par une ligne vide ; `nb_mots` ignoré | — |
| Clé inconnue ou non déclarée | `{"autre": "x"}` pour LC | — | `EntreeInvalide`, nomme la clé |
| Type d'entrée inattendu | dict pour Q, ou str pour CR | — | `EntreeInvalide` |
| Passages pour une Tâche sans emplacement `passages` | LC + passages non vides | — | `EntreeInvalide` |
| Outil hors `outils_autorises` | CR + un outil | — | `EntreeInvalide` (FR-38) |
| Variante CR | `variante="morceau"` ou `"fusion"` | `messages[0]` = consigne de `CR-morceau` ou `CR-fusion` | variante inconnue → `EntreeInvalide` |
| Prompt fautif | bloc de code, JSON, section ou mot « Exemple », ligne de dialogue, front-matter absent, longueur > max | — | `GabaritInvalide` qui liste toutes les fautes |

</intent-contract>

## Code Map

- `src/slmsp/core/messages.py` -- `valider_conversation`, `vers_dicts` : contrôle de la sortie (lecture seule).
- `src/slmsp/core/canonique.py` -- `sha256_hex`, `json_canonique` : empreinte des prompts et test de pureté.
- `src/slmsp/core/config.py` -- `charger_toml`, `ModeleConfig`, `racine_projet()` : chargement de `taches.toml`.
- `src/slmsp/core/erreurs.py` -- `SlmspError`, `ConfigurationInvalide` : bases des nouvelles erreurs (lecture seule).
- `src/slmsp/core/ports.py:27` -- `Passage(chunk_id, doc_id, source, titre, url, texte, date_snapshot, score)` : entrée de `formater_passages`.
- `src/slmsp/core/items.py:54,697-719` -- `CODES` (8 codes sans TR), `RequeteTache`, `vers_requete` : `longueur_demandee` (RE) et `type_courrier` (CT) sont dans `options`, pas dans `entree`.
- `src/slmsp/mcp/outils.py:24` -- `OUTILS_AUTORISES` (les 5 outils) ; `charger_outils()` renvoie des dicts `{"type": "function", "function": {"name": …}}`.
- `eval/**/*.jsonl` -- clés observées dans `entree` : CR `consigne, notes|transcription, nb_mots` ; LC et CO `consigne, texte, nb_mots` ; RE (calibrage) `consigne, document, longueur_demandee` ; CT `consigne, objet, elements_connus` (dict, avec des listes imbriquées) et `type`, normalisé par `core.items`.
- `tests/test_architecture.py:24-48` -- couches : `harness` = 3, `mcp` = 2, `core` = 0.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/gabarits.py` -- `valider_gabarit(source, *, cles_requises=("id","version","tache"), cles_optionnelles=(), longueur_max=LONGUEUR_MAX) -> GabaritValide(id, version, front_matter, consigne, emplacements, sha256)`, où `source` est un `Path` ou du texte. `GabaritInvalide(SlmspError)` rassemble toutes les fautes. Règles :
  - front-matter `---` simple (`cle: valeur`), clés exactes, `version` entier ≥ 1 ;
  - corps fait exactement de `## Consigne` puis `## Emplacements`, sans autre titre ;
  - Emplacements : des lignes `- nom : description`, avec `nom` en `[a-z_]+` ;
  - longueur du fichier ≤ `longueur_max` (4 000 caractères par défaut) ;
  - aucun caractère backtick (U+0060) ni bloc indenté de 4 espaces ou d'une tabulation ;
  - aucune accolade, sauf `{identifiant}` ; aucune ligne qui se décode en JSON ;
  - aucun mot de la famille « exemple » ou « example », « par ex », « e.g. », « few-shot », « réponse type », « modèle de réponse » ou « voici », comparé sans accent ni casse ;
  - aucune citation `>` ; aucune ligne de dialogue (rôle suivi de `:`, comme Question, Réponse, Q, R, Utilisateur, Assistant, Agent, Usager, Système, Entrée, Sortie, User, Input, Output) ; aucun jeton de chat (`<|`, `[INST]`).
  - Renvoie le SHA-256 des octets du fichier. Couche 0 : aucun import hors `core`.
- `config/prompts/taches/{Q,RD,CR,CR-morceau,CR-fusion,LC,CO,RE,CT,NR,TR}.md` -- consignes rédigées par le projet, en français, courtes, sans exemple. Front-matter `id` (nom du fichier), `version: 1`, `tache` (code). Les emplacements sont pris dans le vocabulaire de `harness.taches`. Q exige des réponses fondées sur les passages, cite les passages par leur numéro et oriente l'Agent quand aucun passage ne convient. CT demande un emplacement entre crochets pour chaque champ manquant, sans en écrire. TR demande la traduction seule.
- `config/taches.toml` -- `schema_version = 1`, `defaut = "Q"`, `[taches.<code>]` pour les 9 codes : `libelle`, `actif = true`, `prompt`, `outils_autorises` (les 5 outils pour RD, vide pour les autres), `avertissement` (Q seulement : « Ne vaut pas avis juridique. »), `variantes = {morceau = "CR-morceau.md", fusion = "CR-fusion.md"}` (CR seulement).
- `src/slmsp/harness/taches.py` -- `EMPLACEMENTS` (vocabulaire fermé), `PromptTache`, `Tache` (avec `.prompt_pour(variante)`), `TableTaches` (`.tache(code)`, `.defaut`), `TacheInconnue`, `charger_taches(chemin=None, dossier_prompts=None)`. Le chargement :
  - exige les 9 codes, un `defaut` connu et des outils inclus dans `OUTILS_AUTORISES` ;
  - valide chaque prompt par `valider_gabarit`, avec `id` = nom du fichier, `tache` = code et des emplacements dans le vocabulaire ;
  - lève `ConfigurationInvalide`.
- `src/slmsp/harness/prompts.py` -- `formater_passages`, `construire_messages(tache, entree, passages=None, outils=None, *, variante=None) -> list[dict]`, `entree_de_requete(requete)` (fusionne `longueur_demandee` et `type_courrier` des options dans l'entrée objet), `ORDRE_CLES`, `LIBELLES_CLES`, `EntreeInvalide`. La règle unique de rendu est documentée dans la docstring du module.
- `tests/core/test_gabarits.py`, `tests/harness/test_taches.py`, `tests/harness/test_prompts.py` -- toute la matrice I/O. Tous les prompts réels passent le validateur. Des fichiers fautifs sont fabriqués dans `tmp_path`. Un test D1.1 dédié parcourt les prompts réels et refuse tout motif d'exemple ou de dialogue. Le test de pureté compare le JSON canonique de deux appels.

**Acceptance Criteria:**
- Given `config/taches.toml`, when on le charge, then les 9 codes sont présents, Q est la Tâche par défaut et `outils_autorises` est vide pour CR, LC, CO, RE, CT, NR et TR.
- Given chaque fichier de `config/prompts/taches/`, when `valider_gabarit` l'analyse, then il passe ; and un fichier avec un bloc de code, du JSON, une section « Exemple », sans front-matter ou trop long est refusé.
- Given une Tâche, une entrée, des passages et des outils, when on appelle `construire_messages`, then la sortie passe `valider_conversation`, `messages[0]` est le prompt système de la Tâche, les passages sont numérotés `[1]`, `[2]`… avec titre, URL et date, et deux appels identiques donnent le même JSON canonique.
- Given une entrée objet (CR, LC, CO, RE, CT), when on construit les messages, then les clés nommées sont rendues par la règle unique documentée.
- Given les prompts de Tâche, when on les relit, then ils ne contiennent ni exemple de sortie, ni réponse type, ni amorce, ni ligne de dialogue.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Revue
- verdicts : 50 constats — high 0, medium 13, low 21, false 16, maybe-false 0.
- constats :
  - **Blind Hunter**
    - `[medium]` `[patch]` Le validateur est plus faible que le test D1.1 (mots « réponse/sortie attendue », « i.e. »). Ajoutés à `_MOTS_INTERDITS`.
    - `[low]` `[reject]` Les emplacements `{identifiant}` sont admis mais jamais remplis. Aucun prompt de Tâche n'en contient, et la tolérance sert aux gabarits du générateur (9.2). Il faudrait un garde de plus pour un cas improbable.
    - `[medium]` `[patch]` Aucune clé de contenu n'est exigée et les valeurs vides passent. Ajouté : `CLES_CONTENU`, refus des valeurs vides et de l'entrée texte vide.
    - `[low]` `[patch]` Les chaînes multilignes imbriquées sortent mal indentées. Corrigé avec `_element`, qui indente les lignes de suite.
    - `[low]` `[reject]` Assainissement des passages et injection. Les passages viennent de l'Index local ; c'est improbable, et la correction ajoute de la complexité.
    - `[low]` `[patch]` BOM écrit en littéral invisible. Remplacé par `"﻿"`, avec un test BOM et `\r`.
    - `[low]` `[patch]` `RecursionError` dans `_decode_en_json`. Désormais rattrapée.
    - `[low]` `[patch]` CR-fusion ignore les marqueurs posés par CR-morceau. Deux consignes ajoutées.
    - `[false]` `[reject]` `actif` n'est pas appliqué. Ce drapeau sert à l'ordre de coupe ; son application revient au service (4.2), pas à la construction des messages.
    - `[false]` `[reject]` Le contrôle de couches est incomplet. `tests/test_architecture.py` contrôle déjà les couches pour tout le paquet (`COUCHES`, `core` = 0), y compris `ast.Import`.
    - `[false]` `[reject]` La provenance du prompt n'est pas renvoyée. Elle reste disponible par `tache.prompt_pour(variante).sha256`, sans divergence possible.
    - `[low]` `[reject]` Nombres au format anglais, NaN. Les items JSON ne portent que des chaînes ; c'est improbable.
    - `[medium]` `[patch]` RD.md ne demande aucune traçabilité (FR-7). Consignes ajoutées : titre, producteur, date de mise à jour et lien, plus la citation `[n]`.
    - `[false]` `[reject]` RE déclare `texte` et `document`. `document` est l'alias du calibrage, documenté dans la spec ; pas de défaut.
    - `[low]` `[patch]` « agents » en minuscule dans Q et NR. Mis en majuscule.
    - `[low]` `[reject]` Aucun test à la borne exacte de longueur. C'est une comparaison simple `>`, avec un risque négligeable.
  - **Intent Alignment**
    - `[false]` `[reject]` Les outils ne sont pas couplés aux messages. AD-7 dit que `tools` vient de `outils-mcp.toml` et passe au chat template, pas dans les messages.
    - `[false]` `[reject]` La signature prend un objet `Tache` et un mot-clé `variante`. Les 4 paramètres positionnels du spine sont conservés.
    - `[false]` `[reject]` Seule la « Consigne » est envoyée, et le SHA porte sur le fichier. AD-3 demande le SHA du fichier de prompt.
    - `[false]` `[reject]` Un seul tour. L'historique de conversation est fourni par l'appelant (4.2, FR-1) ; ce n'est pas une composition de prompt.
    - `[medium]` `[patch]` FR-18 : la mention de traduction est absente de la table. `avertissement` ajouté sur TR.
    - `[medium]` `[patch]` FR-16 : LC ne signale pas les passages non simplifiés. Consigne ajoutée. Pour FR-17, la vue en différences relève de l'application ; ce volet est `false`.
    - `[low]` `[patch]` La validation en attente (D-nuit-A1-10) n'apparaît pas dans le dépôt. Commentaire ajouté en tête de `taches.toml`.
    - `[false]` `[reject]` Les tests du validateur passent surtout par du texte. Après lecture, le chemin est identique ; les chemins `Path` sont testés.
    - `[false]` `[reject]` Surface ajoutée (`entree_de_requete`, variantes). Elle est prévue par la spec.
    - `[medium]` `[defer]` Collision entre le module `harness/taches.py` et le paquet de la story 4.2. Voir `deferred`.
    - `[false]` `[reject]` `core.items.CODES` n'a pas TR. Le jeu d'évaluation n'a pas d'item TR (SPEC §2).
  - **Verification Gap**
    - `[medium]` `[patch]` Aucun test ne fait passer les items réels. Test paramétré ajouté : 204 items passent.
    - `[low]` `[patch]` BOM et `\r` non testés. Test ajouté.
    - `[low]` `[patch]` Outils en double non testés. `test_outil_en_double` ajouté.
    - `[low]` `[patch]` Variantes de soulignement et de jetons de chat non testées. Cas ajoutés.
  - **Edge Case Hunter**
    - `[medium]` `[patch]` Un bloc indenté de 5 espaces ou plus échappe au contrôle. Remplacé par `_indentation_interdite`.
    - `[medium]` `[patch]` Les clôtures `~~~` passent. `_RE_CLOTURE_TILDE` ajouté.
    - `[low]` `[patch]` Le soulignement `--` passe. Motif changé en `-{2,}`.
    - `[low]` `[reject]` Titre imbriqué dans une liste, ou balise HTML. Le mot « exemple » reste bloqué ; c'est improbable, et la correction ajoute un garde.
    - `[low]` `[reject]` JSON sur plusieurs lignes. Les accolades sont interdites, et un tableau découpé ne porte aucune clé ; improbable.
    - `[low]` `[patch]` Les abréviations « p. ex. » et « ex. » passent. Ajoutées au même groupe que le premier constat.
    - `[medium]` `[patch]` « réponse attendue » : doublon du premier constat du Blind Hunter, même correctif.
    - `[low]` `[patch]` Rôle de dialogue entouré de `_` ou de guillemets. `_RE_DIALOGUE` étendu.
    - `[low]` `[patch]` Jetons `<s>`, `<start_of_turn>`, etc. `_RE_JETON_CHAT` étendu.
    - `[low]` `[patch]` Le message d'erreur recopiait le texte des titres. Il ne donne plus que les numéros de ligne.
    - `[false]` `[reject]` Version à 4 300 chiffres. Impossible sous `LONGUEUR_MAX` = 4000.
    - `[false]` `[reject]` Clés de types mixtes. Une entrée vient de JSON, donc ses clés sont toujours des chaînes.
    - `[low]` `[patch]` Chaînes multilignes imbriquées : même correctif que le constat du Blind Hunter.
    - `[medium]` `[patch]` Liste ou dict vide : même groupe que les entrées vides.
    - `[false]` `[reject]` Tuple ou Mapping imbriqué refusé. Le JSON ne produit que des listes et des dicts.
    - `[medium]` `[patch]` Entrée objet sans clé de contenu : même groupe que les entrées vides.
    - `[medium]` `[patch]` Entrée texte vide : même groupe que les entrées vides.
    - `[false]` `[reject]` Tâche par défaut inactive. Relève du service, comme pour `actif`.
    - `[false]` `[reject]` `ast.ImportFrom` seul. `tests/test_architecture.py` couvre déjà ce cas.

## Design Notes

Règle unique de rendu d'une entrée objet : on garde les clés présentes de `ORDRE_CLES`, dans cet ordre fixe : `consigne, type_courrier, objet, elements_connus, longueur_demandee, langue_source, langue_cible, partie, notes, transcription, texte, document, parties`. Chaque clé produit `"<Libellé> :\n<valeur>"`, et les sections sont jointes par `"\n\n"`. Une valeur chaîne est rendue telle quelle. Un nombre est rendu par `str` et un booléen par « oui » ou « non ». Une liste donne une ligne `- élément` par élément, et un dict une ligne `- clé (underscores → espaces) : valeur` par clé triée. Les valeurs imbriquées sont indentées de 2 espaces. La clé `nb_mots`, une métadonnée, est ignorée. Toute autre clé lève une erreur, tout comme une clé absente des emplacements du prompt.

Emplacements par prompt : Q `question, passages` ; RD `demande, passages` ; NR `demande` ; CR `consigne, notes, transcription` ; CR-morceau `consigne, partie, notes, transcription` ; CR-fusion `consigne, parties` ; LC et CO `consigne, texte` ; RE `consigne, texte, document, longueur_demandee` ; CT `consigne, type_courrier, objet, elements_connus` ; TR `consigne, langue_source, langue_cible, texte`. Pour une entrée texte (Q, RD, NR), un prompt qui déclare `passages` donne `formater_passages(...)` précédé de « Passages de l'Index local : », puis une ligne vide, puis `"<Libellé de l'emplacement texte> :\n<entrée>"`. Sans `passages` déclaré, l'entrée est rendue telle quelle.

Les sections `Emplacements` servent au Harnais : elles déclarent les clés admises pour chaque prompt et ne sont pas envoyées au modèle. Le message système contient seulement le texte de « Consigne ».

## Verification

**Commands:**
- `uv run pytest tests/core/test_gabarits.py tests/harness -q` -- expected: tout passe.
- `uv run pytest -q` -- expected: aucun échec nouveau.
- `uv run ruff check` -- expected: aucune erreur.

## Auto Run Result

Status: done

**Résumé.** La story livre :
- la table des 9 Tâches ;
- 11 prompts système de Tâche, faits de consignes sans aucun exemple (D1.1, D-nuit-A1-10) ;
- le validateur structurel commun `core.gabarits` (AD-3 verrou 6) ;
- la construction unique et pure des messages, `harness.prompts.construire_messages` (AD-7).

**Fichiers.**
- `config/taches.toml` : 9 codes et `defaut = "Q"`. Les 5 outils sont réservés à RD. Q et TR portent un avertissement, CR ses variantes. Un commentaire renvoie à D-nuit-A1-10.
- `config/prompts/taches/{Q,RD,CR,CR-morceau,CR-fusion,LC,CO,RE,CT,NR,TR}.md` : consignes en français, avec un front-matter (`id`, `version`, `tache`) et les sections « Consigne » et « Emplacements ».
- `src/slmsp/core/gabarits.py` : `valider_gabarit` renvoie un `GabaritValide` avec le SHA-256 des octets. `GabaritInvalide` liste toutes les fautes.
- `src/slmsp/harness/taches.py` : `charger_taches`, `TableTaches`, `Tache`, `PromptTache`, le vocabulaire fermé `EMPLACEMENTS`, et les erreurs `TacheInconnue` et `VarianteInconnue`.
- `src/slmsp/harness/prompts.py` : `construire_messages`, `formater_passages` et `entree_de_requete`. La règle unique de rendu est documentée dans la docstring. Les erreurs lèvent `EntreeInvalide`.
- `tests/core/test_gabarits.py`, `tests/harness/test_taches.py`, `tests/harness/test_prompts.py` : 178 tests, dont :
  - un test D1.1 sur les prompts réels, qui refuse tout exemple et tout dialogue ;
  - un test de pureté en JSON canonique ;
  - un test qui fait passer les 204 items réels.

**Revue.** 50 constats :
- **26 corrigés** (13 medium, 13 low) :
  - verrou lexical D1.1 renforcé ;
  - entrées vides refusées ;
  - indentation des valeurs multilignes corrigée ;
  - prompts RD, LC et CR-fusion complétés (FR-7, FR-16) ;
  - avertissement FR-18 ajouté sur TR ;
  - tests ajoutés.
- **1 reporté** : la collision entre `harness/taches.py` et le paquet `harness/taches/` de la story 4.2.
- **23 rejetés**, avec leur motif dans le journal de tri.

**Revue de suivi recommandée : true.** Le verrou D1.1 de `core.gabarits` reste une liste noire lexicale, renforcée pendant cette passe. Une nouvelle passe pourrait trouver des tournures d'exemple qui y échappent encore. Constats corrigés : 13 medium, 13 low.

**Vérification.**
- `uv run pytest tests/core/test_gabarits.py tests/harness -q` : 178 passés.
- `uv run pytest -q` : 1 766 passés, 124 ignorés, 11 désélectionnés, 0 échec.
- `uv run ruff check` : propre.
- Aucun appel réseau ni d'API, aucune dépense.

**Décisions prises seul.**
- Les sections « Emplacements » déclarent les clés d'entrée admises et ne sont pas envoyées au modèle. Le message système ne contient que la « Consigne ».
- Les variantes CR passent par le mot-clé `variante`.
- La mention FR-18 « Traduction automatique, à vérifier. » est l'`avertissement` de TR. La story 4.2 doit l'émettre sans la confondre avec l'avertissement juridique.
- `entree_de_requete` réinjecte `longueur_demandee` et `type_courrier`, que `core.items` range dans les options.

**Risques résiduels.**
- Les prompts ont été rédigés par l'agent. Leur usage comme entrée d'entraînement attend la validation d'Anaël (D-nuit-A1-10).
- La collision de module avec la story 4.2 reste à résoudre.
- `core.items.CODES` ne contient pas TR : c'est voulu, le jeu d'évaluation n'a pas d'item TR.
