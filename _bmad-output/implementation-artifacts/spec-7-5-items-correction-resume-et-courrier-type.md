---
title: 'Story 7.5 — Items Correction, Résumé et Courrier type (3 × 15)'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: 'fad05df8be7badd7d05eaf4815f4e5d8a6e9454d'
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
      Un verdict de vérification n'est pas lié au contenu de l'item qu'il approuve.
    evidence: |-
      Le format des verdicts (README v1.0, story 7.1) n'a ni empreinte ni version d'item : un item modifié après son dernier « accepte » passe test_verdicts_acceptes. Ici, chaque item modifié a été revérifié volontairement. Déjà différé par la story 7.4.
    location: >-
      eval/construction/v1.0/README.md (format des verdicts)
    severity: medium
  - summary: >-
      Les tests verbatim CO, RE et CT sont ignorés par un simple `uv run pytest`.
    evidence: |-
      duckdb n'est pas dans l'environnement du projet et les instantanés ne sont pas versionnés : 32 tests sont ignorés sans SLMSP_EVAL_SOURCES. Ils passent avec `uv run --no-project --with pytest --with duckdb` et SLMSP_EVAL_SOURCES. À relancer au gel (7.6).
    location: >-
      tests/eval_outils/test_items_co_re_ct.py (fixture sources)
    severity: medium
  - summary: >-
      Les libellés d'emplacements CT varient d'un item à l'autre et les consignes ne rappellent pas la convention [Emplacement].
    evidence: |-
      Exemples : [Commune] / [Nom de la commune] / [Lieu d'émission du courrier]. Si le contrôle automatique des emplacements compare les libellés exactement, le score mesure la capacité à deviner le libellé. Pour trancher : lire la règle de correspondance du banc (story du contrôle automatique CT) ; s'il est strict, normaliser les libellés en v1.1.
    location: >-
      eval/construction/v1.0/CT.jsonl (champs_a_laisser_en_emplacement)
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** Le Jeu d'évaluation v1.0 n'a encore aucun item Correction (CO), Résumé (RE) ni Courrier type (CT). Sans eux, le banc ne peut calculer ni le rappel des fautes et les modifications hors faute (CO, automatique), ni la fidélité et la couverture des résumés (RE), ni la conformité et les emplacements des courriers (CT).

**Approach:** Rédiger 15 items par Tâche (5/5/5) au format du calibrage, conforme au lecteur strict `slmsp.core.items` : RE sur des extraits **verbatim** de fiches service-public figées ; CO sur des textes réels figés ou fictifs dans lesquels des fautes documentées sont injectées, positions calculées par programme ; CT sur des demandes fictives couvrant les quatre types de courrier (FR-14), dont certaines appuyées sur un article LEGI ou une fiche réelle. Faire relire par un vérificateur indépendant (`verification/{CO,RE,CT}.jsonl`), corriger ou remplacer les rejets, et verrouiller par des tests.

## Boundaries & Constraints

**Always:**
- Champs communs SPEC §3 : `id`, `tache`, `difficulte`, `theme`, `entree` (objet), `parametres` (`{}`), `provenance[]` (`consulte_le` = `2026-10-12`), `licence_source`, `fictif`, `version_item = 1`. JSONL UTF-8, LF, `json.dumps(ensure_ascii=False)`, un item par ligne, ids `CO-001`… sans trou. Schéma fermé du lecteur : aucune clé de premier niveau hors de `ItemCO`/`ItemRE`/`ItemCT`.
- **CO** : `entree` = `{consigne, texte, nb_mots}` ; `fautes[]` = `{debut, fin, erreur, correction, type, contexte_fautif}` avec `texte[debut:fin] == erreur`, sans chevauchement ; appliquer les fautes donne exactement `texte_corrige_reference` ; `nb_fautes`, `note_positions`. Facile 5 à 7 fautes courantes, moyen 7 à 10, difficile 10 à 14 fautes fines (subjonctif, participe avec COD antéposé, quel que, trait d'union…). Chaque faute n'a qu'une correction juste ; le texte corrigé ne contient aucune autre faute. Texte réel : `texte_corrige_reference` = extrait verbatim (chunk entier) d'une fiche figée, `fictif: false`. Texte fictif : `fictif: true`.
- **RE** : `entree` = `{consigne, document, nb_mots}`, `document` = `"\n".join(text)` de chunks entiers d'une fiche service-public figée (rév. `29f236f8a5…`), `fictif: false`, provenance machine (`type`, `doc_id`, `chunks`, `url`, `depot`, `revision`) ; `longueur_demandee` ∈ {courte, moyenne, detaillee}, 5 de chaque ; consigne cohérente avec la grille (≤ 80 / 200 / 400 mots) ; `points_cles_reference` (3 à 9) lisibles dans `document`. Thèmes : 5 social-autonomie, 2 de chacun des cinq autres. Une fiche différente par item, hors fiches déjà citées par Q, LC et le calibrage.
- **CT** : `entree` = `{type, objet, elements_connus, consigne}` ; `type_courrier` ∈ {accusé de réception, demande de pièces, convocation, réponse d'information} (4/4/4/3) ; `elements_obligatoires`, `champs_a_laisser_en_emplacement` (chaînes `[…]`, aucune valeur de `elements_connus`), `valeurs_interdites` ; `fictif: true` ; une base réelle (article LEGI ou fiche) passe par `base_reglementaire` et une entrée de provenance.
- `nb_mots` = `compter_mots` de `core.texte` (chargé par chemin, lecture seule).
- Double vérification par un sous-agent indépendant, sans contexte du rédacteur : verdicts en ajout seul au format du README v1.0 ; rejet = correction sous le même `id` ou remplacement au numéro libre suivant, puis revérification ; taux de rejet consigné.

**Never:**
- Modifier `src/`, `config/`, `eval/outils/`, `eval/calibrage/`, `eval/construction/v1.0/README.md`, la SPEC, la grille, ou les fichiers des autres Tâches.
- Reprendre les items ou sources du calibrage (F1878, F38187, scénarios CT-001/CT-002) ; écrire une référence de mémoire.
- Geler, écrire `eval/jeu/` dans le dépôt, appeler le réseau dans les tests.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Composition | brouillons + verdicts | `composition` : CO, RE, CT à 15/15 et 5/5/5 sans écart, aucune anomalie CO/RE/CT | — |
| Positions CO | un item CO | `texte[debut:fin] == erreur`, corrections appliquées = `texte_corrige_reference`, `nb_fautes` = `len(fautes)` | test en échec qui nomme l'item |
| Verbatim RE / CO réel | instantané parquet présent | `document` (RE) ou `texte_corrige_reference` (CO réel) = jointure des chunks cités | skip si instantanés ou duckdb absents |
| Lecteur strict | les 45 items | `valider_item(…, strict=True)` accepte chaque item | test en échec qui cite l'erreur |
| Verdicts | `verification/{CO,RE,CT}.jsonl` | dernier verdict `accepte` pour chaque item | test qui liste les non acceptés |

</intent-contract>

## Code Map

- `eval/calibrage/echantillon-calibrage.jsonl` l. 9-14 -- format CO-001/002, RS-001/002, CT-001/002 (fautes, `note_positions`, `elements_connus`, `valeurs_interdites`, `base_reglementaire`).
- `src/slmsp/core/items.py` -- lecture seule : `ItemCO` (l. 361), `ItemRE` (l. 374), `ItemCT` (l. 385), `Faute` (clés fermées), `_controles_stricts` (l. 484 : listes non vides, positions CO), `valider_item`.
- `eval/outils/construire_jeu.py` -- lecture seule : `CHAMPS_TACHE` (l. 122, CT exige `valeurs_interdites`), `LONGUEURS_RE` (l. 108), `_anomalies_co` (l. 962), `anomalies_item` (l. 1005), `cmd_composition`, `derniers_verdicts`.
- `src/slmsp/core/texte.py` -- `compter_mots`.
- `tests/eval_outils/test_items_cr_lc.py` -- modèle de tests (chargement par chemin, `sans_reseau`, `_dossier_sources`, verbatim duckdb, verdicts).
- `<dépôt principal>/data/raw/eval-sources/hf/AgentPublic/service-public/latest/train/0000.parquet` -- colonnes `doc_id`, `chunk_index`, `title`, `url`, `text` ; `legi/.../legi_<code>/*.parquet` -- `doc_id` (LEGIARTI), `number`, `status`, `text`.
- Fiches RE candidates (non citées par Q, LC ni le calibrage ; « mots » = somme sur toute la fiche, sélectionner des chunks) : social-autonomie F32881 (radiation demande HLM, 576), F1563 (aide au logement étudiant, 473), F33667 (chèque énergie, 3384), F10009 (APA, 5394), F16871 (Aspa, 6205) ; état civil F885 (changement de prénom, 1631), F1618 (se pacser, 6858) ; travail F34154 (congé mariage/Pacs, 545), F16920 (congé de proche aidant, 1581) ; collectivités F32213 (rejet d'offre à un marché public, 2038), F33466 (qu'est-ce qu'un marché public, 2363) ; famille F1883 (bourse école élémentaire, 411), F12214 (bourse étudiant, 1183) ; fiscalité locale F42 (THRS, 1634), F59 (taxe foncière, 7072). Fiches déjà citées par Q/LC/calibrage (à exclure) : `grep -ohE 'F[0-9]+' eval/construction/v1.0/{Q,LC}.jsonl eval/calibrage/echantillon-calibrage.jsonl`.
- Scripts d'exploration (scratchpad, lecture seule, `uv run --no-project --python 3.12 --with duckdb python -I <script> …`) : `C:\Users\UTILIS~1\AppData\Local\Temp\claude\C--Users-Utilisateur-Documents-GitHub-service-public-slm-fine-tuning\2b525399-9658-4abc-ae6d-dabcdbffc874\scratchpad\s75\explore.py` (`fiche F1883` : chunks et `text` ; `titre <motif>…`) et `legi.py` (`legi.py <dossier legi_…> L114-5 …`). Lancer depuis la racine du worktree, PYTHONIOENCODING=utf-8 ; écrire les scripts de génération dans le même dossier scratchpad (pas dans le dépôt).
- Bases CT repérées : CRPA L114-5 (LEGIARTI000031367402), L232-3 (LEGIARTI000031367635) ; CASF R232-23 (LEGIARTI000032138723) ; CGCT L2121-10 (LEGIARTI000041410274), L5211-11 (LEGIARTI000006392814).

## Tasks & Acceptance

**Execution:**
- `eval/construction/v1.0/RE.jsonl` -- 15 items RE-001…015 (facile : documents de 250 à 650 mots ; moyen : 500 à 1 000 ; difficile : 900 à 1 700) -- fidélité et couverture.
- `eval/construction/v1.0/CO.jsonl` -- 15 items CO-001…015, dont au moins 5 sur texte réel -- rappel et modifications hors faute.
- `eval/construction/v1.0/CT.jsonl` -- 15 items CT-001…015 -- conformité et emplacements.
- `eval/construction/v1.0/verification/{CO,RE,CT}.jsonl` -- verdicts du vérificateur indépendant puis revérifications.
- `tests/eval_outils/test_items_co_re_ct.py` -- tests de la matrice.

**Acceptance Criteria:**
- Given les brouillons, when on lance `construire_jeu.py composition`, then CO, RE et CT affichent 15/15 et 5/5/5 sans écart, sans anomalie.
- Given une copie de `eval/` et `config/`, when on lance `construire_jeu.py assembler --racine <copie> --version v1.0` puis `uv run slmsp eval gel --version v1.0 --verifier-seulement --racine <copie>`, then aucune erreur bloquante sur CO, RE et CT (code 0).
- Given `uv run --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q` avec `SLMSP_EVAL_SOURCES`, then tout passe, verbatim compris.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 34 findings — high 0, medium 6, low 22, false 5, maybe-false 1
- findings:
  - **Verification Gap (2)**
    - `low` `patch` Provenance LEGI des CT : `depot` non contrôlé et révision acceptée à `None`. Corrigé : `depot == "AgentPublic/legi"` exigé ; `_verifier_revision` impose l'égalité avec INDEX.json quand il est présent (3 tests verbatim).
    - `low` `patch` Les articles LEGI du calibrage ne sont pas exclus. Corrigé : `test_sources_hors_calibrage` vérifie qu'aucun `LEGIARTI` du calibrage n'est cité par un CT.
  - **Edge Case Hunter (12)**
    - `low` `reject` `importorskip("slmsp.core.items")` masquerait un module cassé — dans l'environnement du projet, `tests/core/test_items.py` échouerait de toute façon ; garde supplémentaire sans cas réel.
    - `low` `patch` `SLMSP_EVAL_SOURCES` défini sans duckdb : skip silencieux. Corrigé : `pytest.fail`.
    - `low` `reject` Limite de mots de la consigne contrôlée par sous-chaîne — les 15 consignes ne portent qu'une limite (vérifié par la couche) ; regex supplémentaire sans cas réel.
    - `low` `patch` `contexte_fautif` non unique ou n'englobant pas la faute. Corrigé : unicité et englobement exigés (groupé avec BH « contexte_fautif »).
    - `low` `reject` Plusieurs instantanés service-public sous le dossier — un seul parquet épinglé existe ; état non démontré.
    - `low` `patch` Révision non comparée si le dépôt manque à l'INDEX. Groupé avec le constat VG « provenance LEGI » ; corrigé.
    - `low` `reject` Plusieurs révisions par dépôt dans l'INDEX — état non démontré (une entrée par fichier, une révision par dépôt).
    - `low` `patch` Base LEGI tronquée acceptée par `in`. Corrigé : égalité exacte avec l'article, sauf `extrait` (CT-012 seul).
    - `low` `reject` `base_reglementaire.article`/`titre` non confrontés à la provenance — normalisation de libellés à écrire pour un risque faible ; le vérificateur a relu chaque base.
    - `false` `reject` `valeurs_interdites` contenue dans `elements_connus` — ce sont des descriptions de comportements interdits, pas des valeurs ; la couche confirme qu'aucune ne figure dans les éléments connus.
    - `low` `reject` Verdict d'un autre code dans un fichier de vérification — `derniers_verdicts` (7.1) lit par fichier ; état non démontré.
    - `medium` `defer` Verdict non lié au contenu approuvé (pas d'empreinte). Format commun du README (7.1), déjà différé par 7.4.
  - **Intent Alignment (6)**
    - `false` `reject` Contrôles dans les tests plutôt que dans l'outil — `eval/outils/` est hors de la zone de la story (consignes de nuit) ; l'outil fait déjà le contrôle des positions CO (`_anomalies_co`).
    - `low` `reject` La chaîne `assembler` + `eval gel --verifier-seulement` n'est pas un test — exécutée sur copie à chaque passe (résultats ci-dessous) ; l'automatiser relève de 7.6.
    - `medium` `defer` Verbatim ignoré dans `uv run pytest` (duckdb absent de l'environnement du projet). Même report que 7.4 ; relancer avec `SLMSP_EVAL_SOURCES` au gel.
    - `medium` `patch` Fichier de story mal encodé (double encodage), sans `## Auto Run Result`, modifications non commitées. Corrigé : réencodage UTF-8, section écrite, commit final. `sprint-status.yaml` est tenu par l'orchestrateur (hors zone).
    - `false` `reject` Rejets corrigés sous le même `id` plutôt que remplacés — le README v1.0 l'autorise ; CT-010 reste une convocation du conseil municipal (même sujet).
    - `low` `reject` Sémantique de `fictif` (CO réels à `false`, CT à `true`) — choix consigné ci-dessous ; aucun critère d'acceptation ne le tranche.
  - **Blind Hunter (14)**
    - `false` `reject` Taux de rejet non consigné — consigné dans `## Auto Run Result` et recalculable par `construire_jeu.py rejets`.
    - `medium` `defer` Verdict non lié à la version de l'item. Groupé avec le constat ECH correspondant.
    - `medium` `patch` Points clés RE plus longs que la limite demandée (courte 82 à 114 mots, moyenne jusqu'à 227). Corrigé : points resserrés (courte 48 à 58, moyenne 109 à 162) sur RE-001, 002, 003, 005, 006, 008, 010, 013, 014, revérifiés ; plafond 60/170/400 testé.
    - `low` `reject` Étiquettes `type` des fautes non normalisées — la grille CO ne calcule pas de rappel par type.
    - `low` `reject` CO-011/CO-012 (réels, difficiles) avec peu de fautes « fines » — 12 fautes chacun, dont trait d'union, homophones, mots soudés ; acceptés par le vérificateur.
    - `low` `reject` Tournures officielles (« 1 ou plusieurs », fragment « Par exemple, … ») qu'un correcteur pourrait toucher — la consigne limite la correction à l'orthographe et la grammaire ; ce ne sont pas des fautes.
    - `medium` `patch` CO-004 « tout renseignement complémentaires » admet deux corrections, comme CO-014 rejeté. Corrigé : « pour répondre à vos questions complémentaire » → « complémentaires », revérifié.
    - `maybe-false` `defer` Libellés d'emplacements CT variables et convention `[…]` absente des consignes — dépend de la tolérance du contrôle automatique (story du banc) ; à trancher en lisant la règle de correspondance des emplacements.
    - `low` `reject` Pas de test « élément (en emplacement) ↔ champ » — correspondance floue à coder ; relue par le vérificateur.
    - `low` `patch` `contexte_fautif` contrôlé en présence seulement. Groupé avec le constat ECH ; corrigé.
    - `low` `patch` Tests verbatim non liés à la révision citée. Groupé avec le constat VG « provenance LEGI » ; corrigé.
    - `false` `reject` Thèmes CO et CT non équilibrés — SPEC §2 ne fixe la couverture thématique que pour Q, RD, LC et RE.
    - `low` `reject` Comparaison des scénarios CT au calibrage par `objet` exact — les bases LEGI sont désormais comparées ; le doublon de sujet est un contrôle du vérificateur.
    - `low` `reject` Largeur des spans de fautes variable (« à pour ») — un span plus large ne fait qu'élargir la zone tolérée ; sans effet sur le rappel.

## Design Notes

- **CO réel** : le texte de référence est un chunk entier ; les fautes sont injectées dans une copie. La correction attendue ramène exactement au texte officiel, ce qui rend le contrôle « hors faute » objectif. On choisit des chunks en prose propre (sans « Cas 1: », listes ou espaces parasites).
- **Génération** : un script de scratchpad (non versionné) écrit les items depuis des gabarits à balises `{{erreur|correction|type}}` et calcule `debut`/`fin` ; les tests recontrôlent tout.

## Verification

**Commands:**
- `uv run --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q` (avec `SLMSP_EVAL_SOURCES=<dépôt principal>/data/raw/eval-sources`) -- expected: tous verts.
- `uv run --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py composition` -- expected: CO, RE, CT sans écart ni anomalie.
- `uv run pytest -q` et `uv run ruff check` -- expected: verts.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** 45 items v1.0 : 15 Correction, 15 Résumé, 15 Courrier type, chacun en 5/5/5, avec la double vérification indépendante et un module de tests. Aucun fichier hors de la zone de la story n'est modifié. Ni `src/`, ni `eval/outils/`, ni la SPEC, ni la grille, ni le calibrage ne sont touchés.

**Fichiers.**
- `eval/construction/v1.0/CO.jsonl` : 15 items Correction.
  - 6 partent d'un chunk réel de service-public, recopié tel quel en `texte_corrige_reference` (F21287, F21766, F12391, F2262, F1648, F1631). Les 9 autres sont des textes fictifs : courriels, notes, avis, courriers, rapport.
  - Nombre de fautes : 6 ou 7 (facile), 8 ou 9 (moyen), 11 à 13 (difficile).
- `eval/construction/v1.0/RE.jsonl` : 15 items Résumé.
  - Chacun repose sur des chunks entiers d'une fiche service-public figée, chaque fois différente et jamais citée par Q, LC ou le calibrage.
  - Longueurs : 5 courte, 5 moyenne, 5 détaillée. Thèmes : 5 social-autonomie, 2 pour chacun des cinq autres.
- `eval/construction/v1.0/CT.jsonl` : 15 items Courrier type, tous fictifs.
  - Types : 4 accusés de réception, 4 demandes de pièces, 4 convocations, 3 réponses d'information.
  - 11 items ont une `base_reglementaire` réelle : 9 articles LEGI (CRPA, CASF, CGCT, commande publique) et 2 fiches (F34103, F15133).
- `eval/construction/v1.0/verification/{CO,RE,CT}.jsonl` : 72 verdicts, écrits en ajout seul.
- `tests/eval_outils/test_items_co_re_ct.py` : tests du format, des positions, du lecteur strict, du verbatim (duckdb), de `composition`, de l'exclusion des sources du calibrage et des verdicts.

**Double vérification et taux de rejet.**
- Les vérificateurs sont des sous-agents indépendants : 3 au premier passage, puis 3 revérificateurs successifs. Ils n'avaient pas le contexte du rédacteur.
- Premier passage : 6 items rejetés sur 45 (13,3 %).
  - RE-001 et RE-008 (`fait_absent_source`) : un point déformé.
  - CO-007 et CO-014 (`ambigu`) : deux corrections justes possibles.
  - CT-010 (`doublon_thematique`).
  - CT-012 (`ambigu`) : lieu sans emplacement.
- Après correction : 2 nouveaux rejets.
  - CO-005 (`autre`) : `contexte_fautif` non mis à jour.
  - RE-001 (`fait_absent_source`) : une nuance de contestation.
- Taux par verdicts (`construire_jeu.py rejets`) : CO 3/21 (14,3 %), RE 3/34 (8,8 %), CT 2/17 (11,8 %), soit 8/72 (11,1 %) au total.
- Tous les rejets ont été corrigés sous le même `id`, puis revérifiés. Le dernier verdict des 45 items est `accepte`.

**Revue (34 constats : 0 high, 6 medium, 22 low, 5 false, 1 maybe-false).**
- **Correctifs.**
  - Tests :
    - provenance LEGI (`depot`, révision exigée quand l'INDEX est présent) ;
    - articles du calibrage exclus ;
    - échec si `SLMSP_EVAL_SOURCES` est défini sans duckdb ;
    - `contexte_fautif` unique et englobant ;
    - base LEGI égale à l'article ;
    - plafond de longueur des points RE.
  - Données :
    - CO-004 n'admet plus qu'une correction ;
    - points RE resserrés sur 9 items, dans la longueur demandée.
  - Fichier de story réencodé en UTF-8.
  - Les items modifiés ont tous été revérifiés et acceptés.
- **Reportés** (3, voir `deferred`) : verdict non lié au contenu ; verbatim ignoré sans instantanés ; libellés d'emplacements CT.
- **Rejetés** : 11 low et 5 false, avec leurs motifs dans le journal de triage.

**Revue de suivi recommandée : `false`.** Trois entrées medium ont été corrigées : l'encodage du fichier de story, les points RE et CO-004. Chaque correctif de données a été revérifié par un vérificateur indépendant, et chaque correctif de test a été exécuté. Aucun risque non vérifié n'est identifiable. Corrigés par verdict : medium 3, low 8.

**Décisions prises seul.**
- **CO réels en `fictif: false`.** Le texte de référence est officiel et recopié tel quel ; les fautes injectées sont documentées dans `provenance` et `licence_source`.
- **CT en `fictif: true`.** C'est vrai même quand une base réelle est citée, car le scénario est fictif.
- **Consigne CO limitée à « orthographe et grammaire ».** Certains textes officiels mélangent les styles d'apostrophe, qu'une passe typographique modifierait.
- **Fiches fiscalité locale RE.** F42 et F59, prévues comme candidates, sont déjà citées par Q et LC. Elles sont remplacées par F34106 (taxe d'habitation des associations) et F743 (taxe de séjour).
- **Format.** `longueur_demandee` est au premier niveau (lecteur strict) et `parametres` vaut `{}`. CT garde `entree.type` en plus de `type_courrier`, comme le calibrage. La base réglementaire CT figure aussi dans `provenance`, avec `type`, `depot` et `revision`.
- **Plafond des points RE**, appliqué pour que la couverture reste atteignable : 60, 170 et 400 mots pour les longueurs courte, moyenne et détaillée.

**Vérifications.**
- `uv run --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q`, avec `SLMSP_EVAL_SOURCES` : 330 passés, verbatim compris.
- `uv run pytest -q` : 1508 passés, 152 ignorés.
- `uv run ruff check` et `ruff format --check tests/eval_outils` : aucun écart.
- `construire_jeu.py composition` : CO, RE et CT à 15/15 et 5/5/5, sans anomalie.
- Sur une copie de `eval/` et `config/` :
  - `construire_jeu.py assembler --version v1.0` produit 185 items.
  - `uv run slmsp eval gel --version v1.0 --verifier-seulement` : 185 items stricts acceptés, 0 erreur bloquante, code 0.
  - Les écarts restants concernent RD (story 7.3) et les thèmes qui en découlent.
- Aucun gel n'a été exécuté et rien n'a été écrit dans `eval/jeu/` du dépôt. Aucune dépense d'API.

**Risques résiduels.**
- **Remarques non bloquantes des vérificateurs**, pour la relecture d'Anaël en v1.1 :
  - CT-010 et CT-011 sont deux convocations du conseil municipal, l'une en urgence (L. 2121-11), l'autre ordinaire (L. 2121-12).
  - Dans RE-008, le délai d'un mois ne s'applique qu'à défaut d'accord collectif.
  - Le point 4 de RE-001 reste général (« selon le cas »).
- **Écart à la SPEC** : la couverture thématique de SPEC §2 ne vise pas CO et CT, mais CO n'a aucun item en fiscalité locale et CT aucun en état civil.
