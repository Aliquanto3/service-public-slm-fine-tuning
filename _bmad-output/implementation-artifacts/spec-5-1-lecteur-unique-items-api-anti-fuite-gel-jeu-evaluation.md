---
title: "Story 5.1 — Lecteur unique d'items, API anti-fuite et gel du Jeu d'évaluation"
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '3e8b5b87de6ccd25b0dbb4d2a1dd928dc66b90a2'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/eval/SPEC-jeu-evaluation.md'
warnings: ['oversized']
deferred:
  - summary: >-
      `jeu_gele_et_commite` n'a pas de test avec une racine située sous la racine du dépôt git (branche de rebasage des chemins).
    evidence: |-
      Tous les tests passent la racine git elle-même ; supprimer le rebasage (gel.py, `if depot != base`) ne fait échouer aucun test. Aucun appelant actuel ne passe une telle racine : à couvrir quand le premier consommateur (D1.3, `data generate`) arrivera.
    location: >-
      src/slmsp/evaluation/gel.py (jeu_gele_et_commite)
    severity: low
---

<intent-contract>

## Intent

**Problem:** rien ne lit encore les items du Jeu d'évaluation ni ne le gèle. Sans lecteur unique, banc, juge et pipeline `data` liraient les items chacun à leur façon. Sans manifeste SHA-256 ni contrôle git, aucune évaluation ne peut prouver qu'elle porte sur un jeu intact, et la génération de données (D1.3) ne peut pas vérifier le gel. Sans API anti-fuite, `data` devrait lire le texte des items.

**Approach:** `slmsp.core.items` est le seul lecteur, avec des modèles pydantic fermés par Tâche, un mode souple qui adapte le calibrage et un mode strict pour v1.0, le rendu `vers_requete` et l'API anti-fuite (empreintes, vecteurs, identifiants). `slmsp.evaluation.gel` vérifie le jeu (schéma, cassettes, composition), écrit le manifeste `ManifesteJeu` avec les deux échantillons tirés par graine et l'export de revue, puis contrôle le manifeste et son commit. La CLI `slmsp eval gel` expose le tout.

## Boundaries & Constraints

**Always:**
- Zone : `src/slmsp/core/items.py`, `src/slmsp/core/schemas/manifeste_jeu.py`, `src/slmsp/evaluation/{gel,config}.py`, `src/slmsp/cli/eval.py`, `tests/core/test_items.py`, `tests/core/test_antifuite.py`, `tests/evaluation/test_gel.py`. Pas de `__init__.py` dans `tests/`.
- Couches : `core.items` n'importe que `core.*` (pas `mcp`). Lecture des cassettes et de `config/outils-mcp.toml` dans `evaluation.gel`, par `slmsp.mcp.cassettes.lire_cassette` et `slmsp.mcp.outils.charger_config`.
- Codes faisant foi Q, RD, CR, LC, CO, RE, CT, NR ; table libellé ↔ code (avec l'alias « Non-régression générale »). L'`id` vaut `<CODE>-NNN` et son code égale celui de `tache`.
- Schéma fermé : les clés inconnues d'un item sont refusées, en strict comme en souple. Les champs ajoutés par 7.2 et 7.4 sont déclarés explicitement : `sous_type` (NR, ∈ {question, consigne}), `type_reunion` et `participants_reference` (CR), `version_texte` (LC), `amorce_usager`, `mention_obligatoire`, `orientation_attendue` et `verification_absence` (Q), ainsi que les extras du calibrage (`nb_fautes`, `note_positions`, `base_reglementaire`, `criteres` en RD, `valeurs_interdites`). Les clés de `entree` et de `provenance[]` restent ouvertes : seul `consulte_le` (date ou date-heure ISO) est exigé pour une provenance.
- Mode souple (calibrage) : `R`→`RD`, `RS`→`RE`, `cassette`→`cassettes` (liste), `comportement_attendu="absence_de_source"`→`sans_reponse=true`, `entree.longueur_demandee`→`longueur_demandee`, `entree.type`→`type_courrier`, défauts `mode="connecte"` (RD), `version_item=0`, `theme="non-classe"`, `parametres={}`, `fictif` vrai si une `provenance[].source` contient « fictif », « fictive » ou « rédigé(e)(s) pour l'évaluation ». Aucune écriture sous `eval/`.
- Mode strict (v1.0) : exige `theme` (l'un des 6 slugs SPEC pour Q, RD, LC et RE ; sinon un slug, `non-classe` compris), `parametres`, `fictif`, `version_item` (entier ≥ 1), `provenance` non vide et les champs de référence de SPEC §3. Pour RD : `appels_attendus[].regles`, `mode` ∈ {connecte, hors-ligne, repli} et `cassettes`. Pour CO : `entree.texte[debut:fin] == erreur`. Pour NR : `reponse_reference` ou `criteres`. Tout refus cite l'item et le champ ; toutes les erreurs du fichier sont rassemblées.
- Format `regles` (fixé ici, à suivre par 7.3) : `{"optionnel": bool=false, "ordre_libre": bool=false, "arguments": {<nom>: {"exact": <valeur>} | {"contient_un_de": [str, …]} | {"optionnel": true}, avec "optionnel" combinable}}`.
- Chemins `cassettes` relatifs au dossier du jeu, POSIX, jamais absolus, résolus sous `<racine>/eval/`.
- Empreintes du manifeste : SHA-256 du contenu aux fins de ligne normalisées en LF (CRLF→LF), car `core.autocrlf=true` sans `.gitattributes` rend les octets du disque dépendants du checkout. La règle est inscrite dans le manifeste.
- Manifeste écrit en `json_canonique + "\n"`, par ouverture exclusive (`xb`). Refus si `MANIFEST.json` ou l'export de revue existe déjà.
- Échantillons tirés par `random.Random(f"{graine}:{nom}:{strate}")` sur des identifiants triés, puis triés. Second juge : par Tâche jugée présente (Q, CR, LC, RE, CT, NR), `min(n, max(3, ceil(0,2 n)))`. Relecture : par strate Tâche × difficulté, `min(n, max(1, ceil(0,2 n)))`.
- Écarts de composition non bloquants en `provisoire` (D-nuit-A2-5) et bloquants en `relu`. `--verifier-seulement` n'écrit rien et sort en 0 si aucune erreur bloquante.

**Never:**
- Ne pas exécuter le gel réel de `v1.0`, ni écrire `eval/jeu/`, `eval/revue/` ou `eval/cassettes/` dans le dépôt. Aucun fichier de `eval/` modifié.
- Aucun texte d'item renvoyé par l'API anti-fuite. Aucun réseau, aucune API payante. Pas de `config/evaluation.toml` (zone de 5.6).
- Ne pas modifier `core/erreurs.py`, `cli/__init__.py`, `mcp/*` ni `eval/outils/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Calibrage | `lire_jeu("calibrage")` | 16 items adaptés, `RD`/`RE`, cassettes en liste | aucune |
| Strict, champ manquant | item v1.0 sans `theme` | refus | `ItemInvalide` « Q-003 : `theme` : … » |
| Strict, RD sans `regles` | `appels_attendus[0]` sans `regles` | refus | `ItemInvalide` cite l'item et `appels_attendus.0.regles` |
| Clé inconnue | `"cassete": …` | refus | `ItemInvalide` cite la clé |
| Vérification | jeu valide, RD absents | rapport + écarts listés, code 0, rien écrit | — |
| Cassette absente ou empreinte ≠ config | item RD | erreur bloquante | `JeuNonConforme`, code 1 |
| Gel | `--statut provisoire --graine 7` | `MANIFEST.json` + `eval/revue/echantillon-revue-v1.0.md` | refus si l'un existe |
| Altération | 1 octet changé dans un fichier listé | — | `ManifesteInvalide` (code 4) |
| Non commité / modifié / commit non ancêtre | `jeu_gele_et_commite` | — | `ManifesteInvalide` |
| `eval run`, `eval sonde-outils` | CLI | « non implémentée » | code 2 |

</intent-contract>

## Code Map

- `src/slmsp/core/erreurs.py` -- `SlmspError`, `ManifesteInvalide` (code 4), `CodeSortie` ; ne pas modifier, sous-classer localement (`ItemInvalide`, `JeuNonConforme`).
- `src/slmsp/core/schemas/__init__.py` -- `SchemaBase` (extra interdit, `schema_version`), `SousSchema`, `Sha256` ; modèle de `run.py` (`AwareDatetime`, `Literal`).
- `src/slmsp/core/canonique.py` -- `json_canonique`, `sha256_hex` pour le manifeste et les empreintes.
- `src/slmsp/core/texte.py` -- `normaliser`, `ngrammes`, `compter_mots`, `VERSION_TEXTE` : anti-fuite et seuil CR de 4 000 mots.
- `src/slmsp/core/ports.py:63` -- `EmbedderPort.vectoriser(textes) -> NDArray[float32]` pour `vecteurs_antifuite`.
- `src/slmsp/core/config.py:36` -- `racine_projet()`, racine par défaut.
- `src/slmsp/core/artefacts.py:77,182` -- `ArtefactExistant` ; modèle d'appel `git` (`env_sous_processus`, `CREATE_NO_WINDOW`, délai).
- `src/slmsp/mcp/cassettes.py:84` -- `lire_cassette` (cassettes héritées comprises, `CassetteInvalide`) ; `src/slmsp/mcp/outils.py:24,103` -- `OUTILS_AUTORISES`, `charger_config(chemin).tools_list_sha256` et `outils[].parametres.properties`.
- `src/slmsp/cli/__init__.py` -- le module `cli/eval.py` expose `enregistrer(sous_parseurs)` ; `func(args) -> int` ; une `SlmspError` est convertie en code de sortie.
- `eval/outils/construire_jeu.py:58-137,933-956` -- constantes SPEC §2 (cibles, thèmes, seuils), `producteurs_rd`, `amorce_reelle`, comptage CR hors `consigne` : à reproduire dans `evaluation/config.py` et `gel.py`, sans import (outil hors paquet).
- `eval/calibrage/echantillon-calibrage.jsonl`, `eval/calibrage/cassettes/` -- 16 items du mode souple ; cassettes héritées avec `tools-list.json`.
- `eval/construction/v1.0/{Q,NR,CR,LC}.jsonl` -- 148 brouillons, dont 140 retenus après `assembler` ; format strict réel.
- `eval/grille-juge-v1.md` -- grille hachée dans le manifeste.
- `tests/test_architecture.py:27` -- couches : `core` 0, `mcp` 2, `evaluation` 4, `cli` 5.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/items.py` -- table des codes et des thèmes, modèles par Tâche (`ItemQ` … `ItemNR`, `AppelAttendu`, `ReglesAppel`, `RegleArgument`, `Faute`, `Provenance`), `lire_items(chemin, strict)`, `lire_jeu(version, racine)` → `Jeu`, `resoudre_cassettes`, `vers_requete` → `RequeteTache`, et l'API anti-fuite (`empreintes_antifuite`, `vecteurs_antifuite`, `identifiants_proteges`) avec ses types de retour -- lecteur unique AD-11, AD-24.
- `src/slmsp/core/schemas/manifeste_jeu.py` -- `ManifesteJeu`, `FichierManifeste` -- AD-25.
- `src/slmsp/evaluation/config.py` -- cibles SPEC §2, parts des thèmes, seuils, Tâches jugées, parts et minima des échantillons, chemins (jeu, revue, grille, config des outils).
- `src/slmsp/evaluation/gel.py` -- `verifier_jeu` → `RapportVerification`, `tirer_echantillons`, `gel`, `verifier_manifeste`, `jeu_gele_et_commite`, rendu de l'export de revue.
- `src/slmsp/cli/eval.py` -- `gel --version [--verifier-seulement | --statut --graine] [--racine]`, `run` et `sonde-outils` en « non implémentée » (code 2).
- `tests/core/test_items.py`, `tests/core/test_antifuite.py`, `tests/evaluation/test_gel.py` -- critères ci-dessous ; jeu factice dans `tmp_path` (dépôt git de fixture pour le gel), calibrage réel en lecture seule, chaînes factices.

**Acceptance Criteria:**
- Given les 16 items du calibrage, when on les lit, then ils sont tous acceptés avec l'adaptation décrite, et aucun fichier de `eval/` ne change (comparaison des SHA avant et après).
- Given un item v1.0 sans `theme`, `parametres`, `fictif`, `version_item` ou, en RD, sans `regles`, when on le lit en strict, then `ItemInvalide` cite l'item et le champ.
- Given un dossier de jeu, when `slmsp eval gel --version v1.0 --verifier-seulement`, then items stricts, cassettes existantes et empreintes conformes à la config sont vérifiés, la composition est comparée à SPEC §2 (Tâche × difficulté, thèmes, ≥ 6 producteurs, 8 Q sans réponse, 5 RD de valeurs, 4 RD de repli, 5 CR > 4 000 mots), et rien n'est écrit.
- Given un jeu valide, when `--statut provisoire --graine <n>`, then le manifeste (SHA de items, cassettes et grille, statut, date, écarts, deux échantillons) et `eval/revue/echantillon-revue-v1.0.md` sont écrits ; un second gel est refusé.
- Given un manifeste, when un fichier listé change d'un octet, then `verifier_manifeste` lève `ManifesteInvalide` (code 4).
- Given `jeu_gele_et_commite("v1.0")`, then il vérifie les SHA, `git diff --quiet HEAD --` sur les chemins du manifeste, le suivi git de ces chemins et l'ascendance du commit d'ajout du manifeste ; sinon `ManifesteInvalide`.
- Given l'API anti-fuite sur v1.0 et calibrage, then elle renvoie des empreintes hachées, des vecteurs et des identifiants protégés (empreintes des `amorce_usager`, URL de provenance, `dataset_id`/`resource_id`), et aucune chaîne renvoyée ne contient de texte d'item.
- Given deux tirages de même graine, then les échantillons sont identiques ; avec une autre graine, ils diffèrent.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 57 findings (56 des couches + 1 de l'orchestrateur) — high 0, medium 14, low 36, false 7, maybe-false 0
- findings:
  - **Blind Hunter (15)**
    - `medium` `patch` `splitlines()` coupe un item contenant U+2028/U+2029 — découpe sur "\n" seulement, "\r" final retiré ; test ajouté.
    - `low` `patch` `--version 1.0` donne une trace Python, code 1 — version contrôlée dans `executer_gel`, code 2 ; tests CLI ajoutés.
    - `medium` `patch` Schéma fermé mais coercition lâche (`"fictif": "yes"`, `version_item: "2"`) — `strict=True` sur les modèles fermés (Provenance reste ouverte) ; tests.
    - `medium` `patch` Champs de référence vides acceptés en strict — chaînes requises non vides, `elements_cles` 3 à 5, listes `points_cles_reference`, `elements_obligatoires`, `decisions_reference`, `fautes` non vides ; listes vides légitimes conservées ; tests.
    - `false` `reject` Réutiliser `valider_appel` pour les `appels_attendus` — les arguments attendus sont un sous-ensemble par construction (« outil + arguments clés », SPEC §3) : exiger les arguments `required` serait faux ; noms d'arguments déjà contrôlés contre le schéma figé.
    - `low` `reject` Cassettes non confrontées aux appels attendus — aucun item RD n'existe encore ; les cassettes viennent de `mcp record` (7.3) et le rejeu signale « appel non prévu » (SPEC §4) ; logique supplémentaire non justifiée.
    - `low` `reject` Manifeste sans `tools_list_sha256` ni `VERSION_TEXTE` — les outils sont figés dans la config versionnée et l'empreinte de chaque cassette est déjà vérifiée au gel ; ajouter des champs au schéma pour un changement improbable n'est pas justifié.
    - `medium` `patch` Manifeste réécrit par un commit ultérieur accepté — `jeu_gele_et_commite` compare le blob du manifeste au commit de gel et à HEAD ; test « réécrit ».
    - `low` `patch` Métadonnées du manifeste non contrôlées — validateur : chemins uniques, exactement un fichier `items` et une `grille` ; tests. Le contrôle des identifiants d'échantillon contre les items est écarté (lecture des items dans `verifier_manifeste`, gain faible).
    - `low` `patch` `gel` non atomique — l'export de revue est supprimé si l'écriture du manifeste échoue ; test.
    - `medium` `patch` Textes de moins de n mots sans empreinte — empreinte du tuple complet de jetons ; test.
    - `low` `reject` Entrées anti-fuite trop larges (`consigne`) ou trop étroites (`contient_un_de`, URL non normalisées) — la `consigne` fait partie du texte d'item ; les seuils de `data` (9.5) absorbent les faux positifs ; extensions sans cas réel.
    - `low` `patch` Texte « 20 % … au moins 1 » codé en dur dans l'export — dérivé de `cfg.PART_RELECTURE` et `cfg.MIN_RELECTURE`. L'incohérence alléguée du statut `relu` est fausse : un gel `relu` porte sur une nouvelle version (v1.1, SPEC §6), avec un nouvel échantillon.
    - `low` `reject` Cohérence CO (`nb_fautes`, chevauchements, texte corrigé) — déjà contrôlée sur les brouillons par `construire_jeu.py composition` (`_anomalies_co`) ; aucun item CO v1.0 n'existe encore.
    - `false` `reject` Spec absente du diff — exclue volontairement du diff relu ; elle existe et sera commitée.
  - **Intent Alignment (8)**
    - `medium` `patch` Aucun test sur les items réels — test en lecture seule de toutes les lignes de `eval/construction/v1.0/*.jsonl` en strict (même racine que la constatation Verification Gap).
    - `false` `reject` La commande de l'AC3 sans `--racine` échoue dans le dépôt — comportement correct : `eval/jeu/v1.0/items.jsonl` n'existe qu'après l'assemblage de 7.6 ; la vérification réelle passe avec `--racine`.
    - `low` `reject` Empreinte après normalisation CRLF→LF — décision consignée (autocrlf sans `.gitattributes`) ; une conversion CRLF est attrapée par `git diff` dans `jeu_gele_et_commite`.
    - `low` `reject` `regles: {}` accepté en strict — format valide (« appeler cet outil, arguments libres ») ; 7.3 écrira les règles selon le format documenté.
    - `medium` `patch` API anti-fuite par objets `Jeu` (le pipeline `data` aurait dû lire les textes) — l'API accepte des noms de version avec `racine` ; tests réécrits (groupé avec la constatation de l'orchestrateur).
    - `false` `reject` Échantillon de relecture sur les 8 Tâches et non sur les seules Tâches jugées — conforme à l'AC4, AD-11 et SPEC §5.4.
    - `false` `reject` Décisions non consignées — elles le sont dans `## Auto Run Result` à la finalisation.
    - `false` `reject` Périmètre — aucun fichier hors zone : constat neutre.
  - **Verification Gap (11)**
    - `low` `patch` `--version` invalide sans test CLI — même racine que Blind Hunter ; corrigé et testé.
    - `medium` `patch` Branche « commit non ancêtre » jamais atteinte — fixture avec un ajout du manifeste sur `main` et un ajout plus récent sur une branche ; `commit_gel` = commit de `main`.
    - `low` `patch` RD sans cassette non testé — bloquant en `connecte`, accepté en `hors-ligne` ; test.
    - `low` `patch` `amorce_reelle` testée seulement dans le sens positif — cas négatif et écart « Q issus d'amorces réelles » testés.
    - `medium` `patch` Références anti-fuite de CR, LC, CO, RE et CT non vérifiées — items ajoutés, un n-gramme par champ de référence et clés `#reference` vérifiés.
    - `medium` `patch` Lecteur strict jamais testé sur les brouillons réels — test ajouté (même racine que l'Intent Alignment).
    - `low` `patch` Cibles de composition recopiées sans test de cohérence — test qui compare à `construire_jeu.py`, chargé par `spec_from_file_location`.
    - `low` `defer` Racine sous la racine du dépôt git non testée — aucun appelant actuel ; reporté (frontmatter `deferred`).
    - `low` `patch` (autres) Trace sur `--version` invalide — doublon, corrigé.
    - `low` `reject` (autres) Comptage CR par `compter_mots` et repli sur `producteur` si `producteurs` est vide — `core.texte` est la règle partagée voulue (AD-29) ; un écart de quelques mots au seuil des 4 000 n'a pas de cas réel (CR longs à plus de 4 400 mots).
    - `low` `patch` (autres) Export de revue orphelin — doublon de Blind Hunter, corrigé.
  - **Edge Case Hunter (22)**
    - `low` `patch` `--version` invalide — doublon, corrigé.
    - `low` `patch` `tache` non hachable (liste) donne un TypeError — contrôle `isinstance(str)` dans les deux modes ; test.
    - `medium` `patch` U+2028 dans un item — doublon, corrigé.
    - `medium` `patch` Coercition de types — doublon, corrigé.
    - `low` `patch` Chemin de cassette avec « : » qui fait planter `gel` — refusé à la lecture de l'item ; test.
    - `low` `patch` Export orphelin si le manifeste échoue — doublon, corrigé.
    - `low` `reject` OSError autre que FileExistsError à l'écriture — disque plein ou droits refusés : improbable, et la trace reste explicite.
    - `low` `reject` Lien symbolique hors racine — configuration improbable dans ce dépôt.
    - `low` `reject` `maintenant` sans fuseau — paramètre interne de test ; l'erreur pydantic est explicite.
    - `medium` `patch` Textes courts sans empreinte — doublon, corrigé.
    - `low` `patch` Forme de la matrice d'embedding non contrôlée — `ndim == 2` et `shape == (len, dimension)` exigés ; test.
    - `low` `patch` Booléens pris pour des identifiants — exclus ; test.
    - `low` `patch` Amorce normalisée vide hachée — ignorée ; test.
    - `low` `reject` Deux `Jeu` de même version écrasés — erreur d'appel improbable.
    - `low` `patch` `longueur_demandee` remontée pour toute Tâche en souple — seulement pour RE ; test.
    - `medium` `patch` Références vides acceptées — doublon, corrigé.
    - `low` `reject` `valeurs_attendues` falsy non compté — une demande de valeurs porte des valeurs ; une liste vide ne doit pas compter.
    - `low` `reject` `tools-list.json` voisin des cassettes héritées non haché — seules les cassettes du calibrage sont héritées ; le calibrage n'est jamais gelé.
    - `low` `reject` Chemins cités par git (guillemets, contrôle) — les chemins de `eval/` sont des slugs ASCII.
    - `low` `reject` Clone superficiel — hors usage (dépôt local complet).
    - `low` `reject` Triple accent grave dans l'export de revue — aucun item n'en contient ; rendu cosmétique.
    - `false` `reject` « Une autre graine donne un autre échantillon » — vrai pour les strates où `k < n` (testé sur un jeu de taille réelle) ; une strate entièrement prise est identique par construction.
  - **Orchestrateur (1)**
    - `medium` `patch` Signature anti-fuite `(jeux: Jeu)` au lieu de `(versions)` (epics.md) : `data` aurait reçu les textes via `lire_jeu` (AD-24) — groupé avec l'Intent Alignment ; corrigé.

## Design Notes

Vérification réelle (sans gel) : copier `eval/` et `config/` dans un dossier temporaire, y lancer `construire_jeu.py assembler --racine <tmp> --version v1.0`, puis `uv run slmsp eval gel --version v1.0 --verifier-seulement --racine <tmp>`. Résultat attendu : 140 items stricts acceptés, écarts RD, CO, RE et CT listés, code 0.

`RequeteTache` : `tache` (code), `entree` (copie profonde : str ou dict), `options` = `mode` (RD), `longueur_demandee` (RE), `type_courrier` (CT) et `parametres`. Le rendu des clés en messages reste à la story 4.1.

Anti-fuite : textes = `entree`, `amorce_usager` et champs de référence (sans `mention_obligatoire`, `provenance` ni métadonnées). N-grammes de `core.texte.ngrammes` (n = 5 par défaut), hachés en SHA-256 tronqué à 16 hex, groupés par clé `<version>/<id>`. Vecteurs : un par item pour l'entrée, un pour la référence si elle existe, avec les clés `<version>/<id>#entree|reference`.

## Verification

**Commands:**
- `uv run pytest tests/core/test_items.py tests/core/test_antifuite.py tests/evaluation/test_gel.py -q` -- expected: verts.
- `uv run pytest -q` et `uv run ruff check` -- expected: verts.
- Vérification réelle décrite en Design Notes -- expected: 140 items acceptés, code 0, aucun fichier écrit dans le dépôt.

## Auto Run Result

Status: done
Blocking condition: aucune

Story réalisée par le sous-agent de story 5.1 le 2026-10-12 (bmad-build-auto, mode autonome, sans push). **Le gel réel de `v1.0` n'a pas été exécuté** : il revient à la story 7.6.

**Résumé.**
- `slmsp.core.items` est le lecteur unique : modèles pydantic fermés par Tâche, mode souple (calibrage adapté à la lecture) et mode strict (v1.0), `vers_requete`, résolution des cassettes sous `eval/`, et API anti-fuite par noms de version (empreintes de n-grammes hachées, vecteurs, identifiants protégés).
- `slmsp.evaluation.gel` vérifie le jeu (items stricts, cassettes et `tools_list_sha256`, arguments connus de l'outil, composition SPEC §2), puis gèle : manifeste `ManifesteJeu` avec deux échantillons tirés par graine, et export de revue.
- `slmsp.evaluation.gel` contrôle aussi le manifeste (`verifier_manifeste`, code 4) et le gel commité (`jeu_gele_et_commite`).
- CLI : `slmsp eval gel` ; `run` et `sonde-outils` répondent « non implémentée » (code 2).

**Fichiers.**
- `src/slmsp/core/items.py` : lecteur, modèles, rendu, API anti-fuite.
- `src/slmsp/core/schemas/manifeste_jeu.py` : `ManifesteJeu`, `FichierManifeste`, `Echantillons`.
- `src/slmsp/evaluation/config.py` : cibles SPEC §2, parts des échantillons, chemins.
- `src/slmsp/evaluation/gel.py` : vérification, tirage, gel, contrôles du manifeste et de git.
- `src/slmsp/cli/eval.py` : sous-commande `eval`.
- `tests/core/test_items.py`, `tests/core/test_antifuite.py`, `tests/evaluation/test_gel.py` : tests de la story.

**Vérification.**
- `uv run ruff check` : propre. `uv run pytest -q` : 1212 passed, 117 skipped.
- **Vérification réelle**, sur une copie temporaire de `eval/` et `config/` :
  - `construire_jeu.py assembler` écrit 140 items (8 brouillons rejetés exclus).
  - `slmsp eval gel --version v1.0 --verifier-seulement --racine <copie>` : **140 items stricts acceptés, 0 erreur bloquante, code 0**.
  - 21 écarts de composition non bloquants : RD, CO, RE et CT absents (stories 7.3 et 7.5), donc thèmes sous la cible. Q (60, 8 sans réponse), CR (25, 5 de plus de 4 000 mots), LC (25) et NR (30) sont conformes.
- `slmsp eval gel --version 1.0` : message d'usage, code 2.
- Aucun fichier écrit sous `eval/` dans le dépôt.

**Revue** (4 couches + orchestrateur, 57 constats : medium 14, low 36, false 7) :
- Corrections appliquées : 9 entrées medium et 12 entrées low (voir le journal de triage).
  - Découpage JSONL sur "\n".
  - Modèles en `strict=True` et références vides refusées.
  - Manifeste réécrit refusé.
  - Empreintes des textes courts.
  - API anti-fuite par noms de version.
  - Validateur du manifeste et gel atomique pour l'export de revue.
  - Tests ajoutés : brouillons réels lus en strict, ascendance du commit, références anti-fuite par Tâche, cohérence avec `construire_jeu.py`.
- Reporté : 1 entrée (racine sous la racine git, frontmatter `deferred`).
- Rejetés : 23 constats, motifs dans le journal de triage.

**Revue de suivi recommandée : `true`.** Neuf entrées medium ont été corrigées en une seule passe. Le risque nommé est le resserrement du mode strict (`strict=True`, références non vides), vérifié seulement sur les brouillons Q, NR, CR et LC existants. Les items RD, CO, RE et CT (stories 7.3 et 7.5) n'ont encore jamais été confrontés au lecteur.

**Décisions prises seul** (règle « la plus simple et la plus réversible ») :
1. **Empreintes SHA-256 sur le contenu aux fins de ligne normalisées en LF.** Le dépôt a `core.autocrlf=true` sans `.gitattributes`, donc les octets sur disque dépendent du checkout. La règle est inscrite dans chaque manifeste (`regle_empreinte`).
   - **Recommandation pour Anaël ou 7.6** : ajouter un `.gitattributes` (`eval/** -text` ou `eol=lf`), hors de la zone de cette story.
2. **Schéma d'item fermé**, en strict comme en souple. Les champs ajoutés par 7.2 et 7.4 sont jugés cohérents avec SPEC §3 et déclarés :
   - `sous_type` (NR, ∈ {question, consigne}), `type_reunion` et `participants_reference` (CR), `version_texte` (LC) ;
   - les extras Q : `amorce_usager`, `mention_obligatoire`, `orientation_attendue`, `verification_absence` ;
   - `entree.nb_mots` et la provenance enrichie passent par des clés ouvertes (`entree`, `provenance[]`) ;
   - aucun champ réel n'a été refusé.
3. **Format `regles` des appels RD**, fixé ici et à suivre par 7.3 : `{"optionnel", "ordre_libre", "arguments": {<nom>: {"exact"} | {"contient_un_de"} | {"optionnel": true}}}`.
4. **Libellés et thèmes.**
   - Alias de libellé « Non-régression générale » accepté.
   - Thème libre (slug, `non-classe` compris) pour CR, CO, CT et NR ; thème SPEC exigé pour Q, RD, LC et RE.
5. **Échantillons** (`ceil` en fractions exactes) :
   - second juge : Q, CR, LC, RE, CT et NR, au moins 3 par Tâche ;
   - relecture : 20 % de chaque strate Tâche × difficulté, sur les 8 Tâches, au moins 1 par strate.
6. **Gel et vérification.**
   - Les écarts de composition bloquent en `relu`, pas en `provisoire` (D-nuit-A2-5).
   - `--verifier-seulement` sort en 0 si aucune erreur n'est bloquante.
   - Un RD sans cassette est bloquant, sauf en `hors-ligne`.
7. **API anti-fuite.**
   - N-grammes de 5 mots par défaut (paramètre), SHA-256 tronqué à 16 hex.
   - La `consigne` est incluse.
   - URL protégées : provenance et `sources_attendues` des Q.

**Risques résiduels.**
- Un gel `relu` exige des thèmes exactement à la cible : à surveiller en v1.1.
- `.gitattributes` absent : voir la décision 1.
- `slmsp eval gel` sur le dépôt réel exige `eval/jeu/v1.0/items.jsonl` (assemblage de 7.6).
- Aucune dépense d'API.
