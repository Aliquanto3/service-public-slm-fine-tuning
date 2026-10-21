---
title: 'Story 16.2 : Q à 8 passages et dédoublonnage du préfixe (harnais v2)'
type: 'feature'
created: '2026-10-21'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/planning-artifacts/stories-epic-16-derive-et-confirmation.md']
warnings: []
deferred: []
---

## Intent

**Problem:** Q reçoit 5 passages dont les chunks d'une même page répètent titre et introduction ; D0 (levier 3) chiffre le gain de k = 8.

**Approach:** 8 passages pour Q seule (`[question] passages = 8` de `config/harnais.toml`, lu par `taches/question.py`, application comprise ; `config/index.toml` reste à `k = 5` pour la Recherche de données et la génération de données), préfixe commun retiré à l'assemblage des passages suivants d'une même page, version du harnais 2 consignée dans les runs de génération et vérifiée par `eval comparer`.

## Réalisé
- `config/index.toml` inchangé (`k = 5`) ; `config/harnais.toml` : `[dedoublonnage] prefixe_min_caracteres = 80` et `[question] passages = 8` ; `RechercheIndex.rechercher(requete, k=None)` accepte un `k` d'appel.
- `harness/dedoublonnage.py` : `dedoublonner_prefixes` (groupe par `doc_id`, plus long préfixe commun coupé sur une limite de mot dans tous les cas, ignoré sous le minimum ; premier passage de la page intact ; passage réduit au préfixe laissé intact ; ordre et numérotation inchangés). Appelé dans `taches/question.py` avant `borner_passages`. `extrait` des Sources vient du texte du passage, donc propre à chacun.
- `harness/config.py` : `VERSION_HARNAIS = 2` (16.3 et 16.8 n'incrémentent pas).
- `evaluation/generation.py` : `config.version_harnais` dans le `run.json` des générations (locales et distantes).
- `evaluation/bootstrap.py` : `RunCharge.version_harnais` (1 si absent ; run composé : la plus haute) ; `comparer` refuse des versions différentes, avertissement avec `--autoriser-jeux-differents` ; `eval composer` refuse des sources de versions différentes (empreinte `version_harnais`).
- Tests : `tests/harness/test_dedoublonnage.py`, cas ajouté à `test_bootstrap.py` et `test_generation.py`. Ciblés (harness, index, evaluation, app) : 1168 passés ; ruff et contrôle rapide OK.

## Décisions et reports
- Les `Passage` ne portent pas de métadonnée de préfixe : seul le plus long préfixe commun est implémenté (le cas « métadonnées » reste à faire si l'Index les expose).
- Page = `doc_id` ; dédoublonnage limité à Q (la Recherche de données n'est pas touchée). Minimum 80 caractères : à confirmer par Anaël.
- Reste à l'orchestrateur : rejeu D0 (57/69) et mesure CPU du premier token (`measure run`). Les scripts D0 `c2/c3/c5.py` ne sont pas dans le dépôt.

## Auto Run Result
Statut : review. Aucun appel payant, aucune donnée générée.

## Revue
- MEDIUM `config/index.toml` `k = 8` lu aussi par la Recherche de données (`taches/recherche.py`) et la génération de données (`recherche_index.depuis_config` → `data/generate.py`) : corrigé, `k = 5` rétabli, Q lit `[question] passages = 8` de `config/harnais.toml` (clé `passages` : `test_k_et_seuil_absents_de_harnais_toml` interdit `k =` dans ce fichier) ; tests `test_k_de_q_distinct_de_l_index_et_version_du_harnais`, `test_k_de_l_appel_remplace_celui_de_l_instance`, `test_question_avec_passages` (store appelé à 8).
- MEDIUM `eval composer` acceptait des sources de harnais différents : corrigé, `version_harnais` ajouté aux empreintes de `composition._empreintes` ; test `test_refus_versions_de_harnais_differentes`.
- LOW `dedoublonnage._prefixe_commun` coupait au milieu d'un mot quand un texte était entièrement préfixe d'un autre (« …ABCDE » / « …ABCDEF fin ») et préférait le dernier saut de ligne à un espace plus loin : corrigé, préfixe gardé entier seulement s'il s'arrête sur un blanc ou la fin de chaque texte, sinon coupé après le dernier blanc ; test `test_coupe_au_mot_quand_un_texte_est_prefixe_de_l_autre`.
- LOW un chunk d'une page qui ne commencerait pas par le titre ferait tomber le préfixe commun sous le minimum et annulerait le dédoublonnage de toute la page : rejeté, les chunks de l'Index portent tous titre et introduction ; à revoir si l'Index change.
- D1 : fixtures de `test_dedoublonnage.py` en marqueurs factices (`<titre-factice>`…), aucun contenu rédigé.
- Reste à l'orchestrateur : rejeu D0, mesure CPU du premier token ; `[question]` et `[anti_boucle]` (16.3) en fin de `config/harnais.toml` : conflit textuel trivial à la fusion.
