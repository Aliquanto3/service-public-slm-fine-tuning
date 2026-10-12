---
title: 'Story 7.4 — Items Compte rendu (25) et Langage clair (25)'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '6db33d0f2b422295c80865b5cee2cb732a4e2b29'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/eval/SPEC-jeu-evaluation.md'
  - '{project-root}/eval/grille-juge-v1.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-7-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Le contrôle du verbatim LC est ignoré dans une exécution par défaut, sans les instantanés locaux.
    evidence: |-
      Sans SLMSP_EVAL_SOURCES, les 25 test_verbatim_lc sont ignorés : les instantanés de data/raw/eval-sources ne sont pas versionnés, et le worktree ne les contient pas. Il faut relancer pytest tests/eval_outils avec SLMSP_EVAL_SOURCES avant le gel (story 7.6).
    location: >-
      tests/eval_outils/test_items_cr_lc.py:test_verbatim_lc
    severity: medium
  - summary: >-
      Un verdict de vérification n'est pas lié au contenu de l'item qu'il approuve (pas de hachage).
    evidence: |-
      Le format des verdicts est fixé par le README v1.0 (story 7.1) : id, verdict, motif, detail, verifie_le. Un item modifié après son dernier « accepte », sans nouvelle ligne, passe test_verdicts_acceptes. Corriger supposerait d'ajouter un champ au format commun (7.1 ou 7.6).
    location: >-
      eval/construction/v1.0/README.md (format des verdicts)
    severity: medium
  - summary: >-
      Les champs ajoutés (version_texte, type_reunion, entree.nb_mots, provenance LC étendue) ne sont pas confrontés à la validation stricte de slmsp eval gel.
    evidence: |-
      La story 5.1 (core.items, eval gel --verifier-seulement) n'est pas présente dans ce worktree. Pour trancher : lancer eval gel --version v1.0 --verifier-seulement en 7.6 et vérifier que ces champs sont tolérés.
    location: >-
      eval/construction/v1.0/{CR,LC}.jsonl
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** Le Jeu d'évaluation v1.0 n'a encore aucun item Compte rendu (CR) ni Langage clair (LC). Sans eux, le banc ne peut mesurer ni la couverture et l'absence d'invention des comptes rendus, ni la fidélité et le gain de lisibilité des réécritures (grille v1, sections CR et LC).

**Approach:** Rédiger 25 CR fictifs annotés (notes et transcriptions de réunions du secteur public) et 25 LC dont le texte est un extrait **verbatim** de sources officielles figées (`AgentPublic/service-public`, `AgentPublic/legi`), annotés et dotés de `kandel_moles_entree` calculé par `slmsp.core.texte`. Les faire relire par un vérificateur indépendant qui écrit `verification/{CR,LC}.jsonl`, remplacer ou corriger les rejets, et verrouiller le tout par des tests de structure.

## Boundaries & Constraints

**Always:**
- Format : celui de `eval/calibrage/echantillon-calibrage.jsonl` (CR-001, LC-001), complété par les champs communs de SPEC §3 : `id`, `tache`, `difficulte`, `theme`, `entree` (objet), `parametres`, `provenance[]` (avec `consulte_le` = `2026-10-12`), `licence_source`, `fictif`, `version_item = 1`. JSONL UTF-8, LF, `ensure_ascii=False`, un item par ligne.
- Composition : CR 8/10/7 dont au moins 5 entrées de plus de 4 000 mots (`entree.transcription`), LC 8/10/7. Thèmes LC selon SPEC §2 (environ 7 social-autonomie, 4 état civil, 4 travail, 4 collectivités, 4 famille-éducation-santé, 2 fiscalité locale).
- CR : `fictif: true` ; `entree` = `{consigne, notes|transcription, nb_mots}` ; `participants_reference`, `decisions_reference`, `actions_reference[]` (`action`, `responsable`, `echeance`, avec « non précisé » / « non fixée » quand l'entrée ne les donne pas) et `pieges` (au moins 3 : éléments évoqués mais non décidés, erratums, conditions). Toute décision et action de référence figure dans l'entrée ; aucun piège n'y est décidé. Personnes, collectivités et chiffres imaginaires.
- LC : `fictif: false` ; `entree` = `{consigne, texte, nb_mots}` ; `entree.texte` composé uniquement de lignes recopiées telles quelles de la source (la sélection de lignes ou de paragraphes est permise, la réécriture non) ; `provenance[0]` lisible par machine (`type` `service-public` avec `doc_id` et `chunks`, ou `legi` avec `code` et `articles`), plus `url`, `revision` du dépôt HF et `consulte_le` ; `informations_a_conserver` (montants, dates, délais, conditions, obligations) et `termes_juridiques_a_conserver` tirés du texte ; `kandel_moles_entree` = `round(kandel_moles(texte), 2)` et `version_texte` = `VERSION_TEXTE`.
- `nb_mots` = `compter_mots` de `core.texte` sur le texte d'entrée.
- `core.texte` et `construire_jeu.py` sont chargés par chemin de fichier, en lecture seule.
- Double vérification par un sous-agent indépendant (sans le contexte du rédacteur), verdicts en ajout seul dans `eval/construction/v1.0/verification/{CR,LC}.jsonl` au format du README (motifs SPEC §5.2) ; les rejetés sont corrigés sous le même `id` ou remplacés au numéro libre suivant, puis revérifiés ; le taux de rejet est consigné.

**Never:**
- Modifier `src/`, `config/`, `eval/outils/construire_jeu.py`, `eval/construction/v1.0/README.md`, la SPEC, la grille ou `eval/calibrage/`.
- Reprendre les items du calibrage (D-nuit-A2-3) ou leurs réunions et fiches (CR-001, CR-002, F34440, CRPA L112-3/R112-5/L112-6).
- Écrire une référence LC de mémoire : chaque information à conserver se lit dans `entree.texte`.
- Lancer Légifrance (403) ou un hôte hors D1.5 ; geler le jeu (story 7.6) ; écrire `eval/jeu/`.
- Faire un appel réseau dans les tests.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Composition | `CR.jsonl`, `LC.jsonl` et leurs vérifications | `composition` : CR 25 (8/10/7), LC 25 (8/10/7), « CR transcriptions > 4000 mots » ≥ 5, aucune anomalie CR/LC | — |
| Structure CR | un item CR | champs complets, `fictif` vrai, actions avec responsable et échéance | test en échec qui nomme l'item |
| Kandel-Moles | un item LC | recalcul par `core.texte` = `kandel_moles_entree` (à 0,005 près), `version_texte` = `VERSION_TEXTE` | test en échec qui nomme l'item |
| Verbatim LC | parquet présent (`SLMSP_EVAL_SOURCES` ou `<racine>/data/raw/eval-sources`) | chaque ligne de `entree.texte` se retrouve dans les chunks ou articles cités | test ignoré (skip) si les instantanés ou duckdb manquent |
| Verdicts | `verification/{CR,LC}.jsonl` | chaque item a un dernier verdict `accepte` | test en échec qui liste les items non vérifiés ou rejetés |

</intent-contract>

## Code Map

- `eval/calibrage/echantillon-calibrage.jsonl` lignes 5 à 8 -- golden format CR-001, CR-002, LC-001, LC-002 (provenance, licences, `pieges` avec « NON décidé »).
- `eval/outils/construire_jeu.py` -- lecture seule : `CHAMPS_COMMUNS` et `CHAMPS_TACHE` (l. 111-136), `anomalies_item` (l. 1005), `_nb_mots` (l. 923, compte toutes les valeurs de `entree` sauf `consigne`), `SEUIL_CR_LONGUE_MOTS = 4000`, `derniers_verdicts`, `cmd_composition` (l. 1072). Les tests le chargent par chemin (`importlib`), comme `tests/eval_outils/test_construire_jeu.py`.
- `src/slmsp/core/texte.py` -- lecture seule : `VERSION_TEXTE = 1`, `compter_mots`, `kandel_moles` (lève `ValueError` sans mot). Stdlib seule, chargeable par chemin.
- `<dépôt principal>/data/raw/eval-sources/hf/AgentPublic/service-public/latest/train/0000.parquet` -- rév. `29f236f8a5…` (INDEX.json) ; colonnes `doc_id`, `chunk_index`, `title`, `url`, `text`, `chunk_text`, `theme`, `audience`.
- `<dépôt principal>/data/raw/eval-sources/hf/AgentPublic/legi/data/legi-latest/legi_<code>/*.parquet` -- rév. `68b01fbbe0…` ; CASF, CRPA (sauf articles du calibrage), CGCT, code civil, commande publique.
- `eval/construction/v1.0/README.md` -- format des verdicts (`id`, `verdict`, `motif`, `detail`, `verifie_le`), dernier verdict l'emporte, fichier en ajout seul.

## Tasks & Acceptance

**Execution:**
- `eval/construction/v1.0/CR.jsonl` -- rédiger 25 items fictifs (CR-001 à CR-025) : 8 faciles (notes de 300 à 700 mots), 10 moyens (notes ou transcription de 700 à 2 000 mots), 7 difficiles dont 5 transcriptions de 4 100 à 6 000 mots ; types de réunion tous différents (conseil municipal, CCAS, COPIL, CSE, conseil d'école, commission d'appel d'offres, réunion de service, etc.) -- couverture CR de la grille.
- `eval/construction/v1.0/LC.jsonl` -- 25 items (LC-001 à LC-025) : faciles = 1 fiche service-public, 100 à 220 mots ; moyens = 220 à 400 mots, plusieurs conditions ou montants ; difficiles = articles LEGI ou extraits denses de 250 à 450 mots ; une source différente par item -- fidélité et gain de lisibilité.
- `eval/construction/v1.0/verification/CR.jsonl`, `verification/LC.jsonl` -- écrits par le vérificateur indépendant, puis complétés par les revérifications.
- `tests/eval_outils/test_items_cr_lc.py` -- tests de la matrice : structure (via `anomalies_item`), composition, longues transcriptions, Kandel-Moles recalculé, verbatim LC (skip si instantanés absents), verdicts.

**Acceptance Criteria:**
- Given les brouillons, when on lance `construire_jeu.py composition`, then les lignes CR et LC affichent 25/25 et 8/10/7 sans écart, et la contrainte des 5 transcriptions longues est atteinte.
- Given la vérification indépendante, when elle relit un CR, then elle contrôle que chaque décision et action de référence figure dans l'entrée et qu'aucun piège n'y est décidé ; when elle relit un LC, then elle contrôle le verbatim, chaque information à conserver et la provenance.
- Given `uv run --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q`, when on le lance avec `SLMSP_EVAL_SOURCES` pointant vers les instantanés, then tout passe, verbatim compris.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 41 findings — high 0, medium 9, low 22, false 9, maybe-false 1
- findings:
  - **Verification Gap (4)**
    - `medium` `patch` Aucun test ne vérifie que les `termes_juridiques_a_conserver` se lisent dans `entree.texte` (cause du rejet de LC-011). Corrigé : test paramétré, insensible à la casse.
    - `medium` `patch` Dans `_textes_source`, un `code` LEGI ou un parquet manquant donne un skip au lieu d'un échec, même quand les instantanés sont configurés. Corrigé : assertion.
    - `low` `patch` Aucun test d'unicité de `type_reunion`. Corrigé : assertion dans `test_composition_cr`.
    - `medium` `defer` Le verbatim LC est ignoré dans une exécution par défaut, sans `SLMSP_EVAL_SOURCES`. Ce skip est prévu par la spec, car les instantanés ne sont pas versionnés ; à relancer avec les instantanés au gel (7.6).
  - **Intent Alignment (9)**
    - `false` `reject` L'AC3 (contenu CR contre l'entrée) n'est pas testé automatiquement. — L'AC3 confie ce contrôle au vérificateur indépendant ; ses verdicts sont présents, et `test_verdicts_acceptes` exige un dernier verdict `accepte`.
    - `medium` `patch` Les termes ne sont contrôlés que sur la non-vacuité. Même cause que le premier constat VG. Corrigé.
    - `medium` `defer` La preuve « texte réel » dépend d'instantanés locaux. Même cause que le constat VG différé.
    - `low` `patch` Le seuil des 4 000 mots repose sur `_nb_mots` (découpage aux blancs), pas sur `compter_mots`. Corrigé : `entree.nb_mots` > 4 000 est aussi exigé. « Au moins 5 » reste conforme : il y en a exactement 5.
    - `maybe-false` `defer` La validation stricte de `slmsp eval gel` (story 5.1) n'est pas exercée sur les champs ajoutés (`version_texte`, `type_reunion`, provenance étendue). Pour trancher : lancer `eval gel --verifier-seulement` en 7.6.
    - `false` `reject` Le fichier de test est hors de la zone. — Le contexte de l'epic autorise `tests/eval_outils/`, et la consigne de la story y place ses tests.
    - `false` `reject` Les items rejetés sont corrigés plutôt que remplacés. — Le README v1.0 autorise « corrigé sous le même `id` puis revérifié ».
    - `false` `reject` `version_item` reste à 1 après correction. — Le README et `anomalies_item` imposent 1 avant le gel ; l'incrément relève de la v1.1 (SPEC §6).
    - `false` `reject` Le taux de rejet n'est consigné que dans un fichier non commité. — Ce fichier de story est commité à la finalisation, et `rejets` le recalcule depuis les verdicts.
  - **Blind Hunter (17)**
    - `medium` `defer` Un verdict n'est pas lié au contenu qu'il approuve (pas de hachage). Le format des verdicts vient du README de 7.1, hors de cette story.
    - `low` `reject` Les tranches de longueur de la spec ne sont pas testées. — Les données les respectent, et ces tranches sont indicatives ; le test ajouterait des assertions pour un risque faible.
    - `low` `patch` Unicité des types de réunion. Même cause que le constat VG. Corrigé.
    - `false` `reject` Le mélange de thèmes CR est déséquilibré. — SPEC §2 ne fixe de couverture thématique que pour Q, RD, LC et RE.
    - `medium` `patch` Termes absents du texte et casse différente (LC-002, 011, 012). Même cause que le premier constat VG ; le contrôle insensible à la casse passe sur les 25 items.
    - `low` `reject` LC-019 écrit « 72 heures » quand l'article dit « soixante-douze heures ». — L'information est la même ; le Juge note le sens, et une correction imposerait une nouvelle vérification sans bénéfice.
    - `low` `reject` Artefacts d'extraction dans les textes LC (espaces avant la ponctuation, tableau markdown). — Ils sont recopiés tels quels de la source, comme l'exige la règle du verbatim.
    - `low` `reject` Le verbatim ne contrôle ni l'ordre ni les lignes courtes. — Choix documenté (sélection de lignes permise) ; vérifier l'ordre ajouterait une logique complexe.
    - `low` `reject` Les nombres de mots cités par les vérificateurs diffèrent de `nb_mots`. — Ils ont compté par découpage aux blancs, comme l'outil ; les deux mesures dépassent 4 000 pour les 5 items longs.
    - `low` `reject` Des noms de famille fictifs se répètent d'un item à l'autre. — Ce n'est pas un motif de la SPEC §5.2, et il n'y a pas de dommage pour la notation.
    - `low` `reject` Des noms de famille de personnalités sont présents dans CR-001. — Ce sont des noms courants, sans prénom ni fonction réelle ; CR-018 avait été rejeté pour un nom complet.
    - `low` `reject` Les transcriptions CR ont pour provenance « Notes fictives… », sans `type`. — Libellé seulement ; la provenance CR n'est lue par aucun contrôle.
    - `false` `reject` La granularité des participants de CR-025 diffère. — La grille ne note pas les participants (Couverture = décisions et actions ; Structure non comptée).
    - `false` `reject` Les variantes de « non fixée » gêneraient un correcteur automatique. — AD-29 : la Tâche CR n'a aucun contrôle automatique, et le Juge lit le sens.
    - `low` `reject` La difficulté LC ne suit pas Kandel-Moles. — La difficulté reflète la densité juridique, et le seuil +10 porte sur le gain moyen.
    - `low` `reject` Les fichiers de vérification sont peu testés (LF, orphelins). — `composition` liste déjà les verdicts sans brouillon ; le README n'impose pas de forme canonique.
    - `low` `reject` Le test code en dur des valeurs (date, 8/10/7, lignes du tableau). — Ce sont les cibles de la SPEC ; la sortie de `composition` est la surface de l'AC.
  - **Edge Case Hunter (11)**
    - `false` `reject` Le test des fins de ligne accepterait un blob CRLF. — `git ls-files --eol` donne `i/lf` pour les quatre fichiers, et `core.autocrlf=true` convertit en LF au commit.
    - `low` `patch` Le seuil des transcriptions longues mesuré par `_nb_mots`. Même cause que le constat IA. Corrigé.
    - `low` `patch` Une provenance LEGI sans `legiarti` passe le test de structure. Corrigé : `legiarti` (`LEGIARTI[0-9]+`) est exigé, et l'URL doit se terminer par cet identifiant.
    - `medium` `patch` Termes non contrôlés contre le texte. Même cause que le premier constat VG. Corrigé.
    - `low` `patch` Avec un `SLMSP_EVAL_SOURCES` invalide, tous les tests verbatim sont ignorés en silence. Corrigé : `pytest.fail`.
    - `low` `reject` `rglob` prendrait les archives `.ancien-*`. — Aucune archive n'existe dans les instantanés ; ce serait une garde pour un état non démontré.
    - `low` `reject` Des entrées archivées multiples dans l'INDEX. — Même raison : aucune archive.
    - `low` `reject` Les lignes très courtes passent trivialement. — Même cause que le constat BH sur le verbatim ; rejeté.
    - `medium` `defer` Verdict non lié au contenu. Même cause que le constat BH. Différé.
    - `low` `reject` La frontière d'arrondi .xx5 pourrait faire échouer à tort. — Les valeurs sont produites par `round(x, 2)` et passent ; ce serait une garde pour un cas non rencontré.
    - `low` `reject` `KeyError` sur `p['source']` dans un message d'assertion. — Toutes les provenances LC ont `source` ; cas non démontré.

## Design Notes

- **Pourquoi `kandel_moles_entree` arrondi à 2 décimales et `version_texte` dans l'item** : le banc recalcule les deux indices à la notation (AD-29) ; la valeur figée sert de contrôle de dérive, et la version dit avec quelle règle elle a été calculée.
- **Provenance LC lisible par machine** (exemple) :
  `{"type": "service-public", "source": "MediaTech AgentPublic/service-public, fiche F1234 « … » (chunks 2, 3)", "doc_id": "F1234", "chunks": [2, 3], "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1234", "revision": "<sha40>", "consulte_le": "2026-10-12"}`.
  Pour LEGI : `{"type": "legi", "code": "<dossier legi_…>", "articles": ["L232-1"], "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI…", "note": "URL construite à partir de l'identifiant LEGIARTI (Légifrance : HTTP 403)", …}`.
- **Rédaction parallèle des CR** : cinq rédacteurs, chacun avec 1 transcription longue et 4 items de difficultés fixées, et une liste de types de réunion disjointe, pour éviter les doublons thématiques.

## Verification

**Commands:**
- `uv run --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q` (avec `SLMSP_EVAL_SOURCES=<dépôt principal>/data/raw/eval-sources`) -- expected: tous verts.
- `uv run --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py composition` -- expected: CR et LC sans écart, aucune anomalie CR ou LC.
- `uvx ruff check tests/eval_outils` et `uvx ruff format --check tests/eval_outils` -- expected: aucun écart.

## Auto Run Result

- **Statut** : done. 25 CR (8/10/7, 5 transcriptions > 4 000 mots : CR-001, 006, 011, 016, 021) et 25 LC (8/10/7 ; thèmes 7/4/4/4/4/2), tous acceptés au dernier verdict.
- **Double vérification** : CR relus par 3 vérificateurs indépendants (tranches 001-008, 009-016, 017-025), LC par 1 vérificateur ; verdicts en ajout seul dans `verification/{CR,LC}.jsonl`. Rejets corrigés sous le même `id` puis revérifiés.
- **Taux de rejet** (`construire_jeu.py rejets`) : CR 6 rejets / 41 verdicts (14,6 %) — CR-003, CR-008, CR-010, CR-011 (`fait_absent_source`, échéance ou rôle déduits), CR-015 (`ambigu`), CR-018 (`autre`, nom d'une personnalité réelle) ; LC 2 / 30 (6,7 %) — LC-011 (`autre`, terme absent du texte), LC-022 (`fait_absent_source`). Total 8 / 71 (11,3 %).
- **Décisions prises seul** :
  - Verbatim LC : une ligne peut être une sous-chaîne d'une ligne source (sélection de phrases, coupe à une frontière de phrase), et les intitulés de section (`context`), le titre de la fiche ou l'en-tête d'article LEGI (`chunk_text`, « Code … - Article … ») comptent comme lignes de la source ; le test les accepte.
  - Provenance LEGI : une entrée par article (`type`, `code` = dossier `legi_…`, `articles`, `legiarti`, `url`, `revision`, `consulte_le`) ; service-public : une entrée avec `doc_id` et `chunks`.
  - `parametres` = `{}` pour CR et LC ; champ supplémentaire `type_reunion` conservé dans les CR (aide au contrôle des doublons) ; `theme` renseigné aussi pour les CR.
  - Items corrigés après vérification : `version_item` reste 1 (le README v1.0 l'impose avant gel).
- **Remarques non bloquantes laissées** : CR-006 cite des syndicats réels de façon générique (CGT, FO, CFDT, UNSA) ; quelques items dépassent le volume indicatif d'actions (CR-013, CR-019, CR-023, CR-024) ; la remarque CCH L441-2 sur CR-010 ne porte plus sur aucune référence.
### Finalisation (revue du 2026-10-12)

- **Changement** : 25 items CR fictifs et 25 items LC extraits tels quels de service-public et de LEGI (MediaTech, révisions épinglées), avec leurs verdicts de double vérification, plus `tests/eval_outils/test_items_cr_lc.py`.
- **Fichiers** :
  - `eval/construction/v1.0/CR.jsonl` : 25 comptes rendus (8/10/7, dont 5 transcriptions de plus de 4 000 mots).
  - `eval/construction/v1.0/LC.jsonl` : 25 items Langage clair (8/10/7, thèmes 7/4/4/4/4/2).
  - `eval/construction/v1.0/verification/CR.jsonl` et `LC.jsonl` : 71 verdicts, en ajout seul.
  - `tests/eval_outils/test_items_cr_lc.py` : structure, composition, Kandel-Moles, termes, verbatim et verdicts.
- **Revue** : 41 constats (aucun high, 9 medium, 22 low, 9 false, 1 maybe-false).
  - Correctifs : 6 entrées, toutes dans le fichier de tests (commit `086a2b1`). 2 sont medium (termes juridiques contre le texte ; échec au lieu de skip pour un parquet cité manquant), 4 sont low (unicité de `type_reunion` ; seuil des 4 000 mots aussi en `compter_mots` ; `legiarti` exigé ; `SLMSP_EVAL_SOURCES` invalide qui échoue). Aucun item n'a été modifié.
  - Reportés : 3 entrées (voir `deferred`) : verbatim ignoré sans instantanés, verdicts non liés au contenu, champs ajoutés non confrontés à `eval gel`.
  - Rejetés : 13 low et 9 false, avec leurs motifs dans le journal de triage.
- **Revue de suivi recommandée** : `false`. Deux entrées medium sont corrigées, mais ce ne sont que des assertions de test, vérifiées à l'exécution ; aucun risque non vérifié n'est identifiable.
- **Vérifications** :
  - `uv run --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q` avec `SLMSP_EVAL_SOURCES` : 233 passés, verbatim compris, aucun ignoré.
  - `uv run pytest -q` : 421 passés, 27 ignorés (marqueurs hors de cette story).
  - `uv run ruff check` : aucun écart. `uvx ruff check` et `uvx ruff format --check tests/eval_outils` : aucun écart.
  - `construire_jeu.py composition` : CR et LC à 25/25 et 8/10/7 sans écart ; 5 transcriptions longues sur 5 ; aucune anomalie ; aucun item sans verdict.
  - `construire_jeu.py rejets` : CR 6/41 (14,6 %), LC 2/30 (6,7 %), total 8/71 (11,3 %).
- **Risques résiduels** :
  - Le verbatim n'est contrôlé que si les instantanés sont présents. À relancer au gel (7.6).
  - Les champs ajoutés hors de SPEC §3 (`version_texte`, `type_reunion`, `entree.nb_mots`, provenance étendue) restent à confronter à la validation stricte de la story 5.1.
  - Les textes LC gardent les artefacts d'extraction de la source (espaces avant la ponctuation, un tableau markdown dans LC-015), ce qui pèse un peu sur l'indice d'entrée.
  - Remarques non bloquantes pour la relecture d'Anaël :
    - noms de famille fictifs répétés d'un item à l'autre ;
    - noms courants de personnalités dans CR-001 (sans prénom) ;
    - canevas proche entre les transcriptions longues.
