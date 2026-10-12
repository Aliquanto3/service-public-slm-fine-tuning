---
title: 'Story 7.6 — Double vérification finale, échantillon de revue et gel v1.0-provisoire'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '3cd6c1bea221bcd53ee7b6fae8446140488eee57'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/eval/SPEC-jeu-evaluation.md'
  - '{project-root}/eval/construction/v1.0/README.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-7-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Taux de rejet par Tâche et constats non bloquants à reporter dans le journal de nuit et dans etat-nuit.md (AC 3).
    evidence: |-
      Les consignes de nuit confient le journal, etat-nuit.md et sprint-status.yaml à l'orchestrateur ; le sous-agent ne les modifie pas, pour éviter les conflits de fusion. Taux (rejets / verdicts) : Q 12/87, RD 1/65, CR 6/41, LC 2/30, CO 3/21, RE 3/34, CT 4/35, NR 3/50, soit 34/363 (9,4 %). Ces chiffres sont remis dans le compte rendu final.
    location: >-
      _bmad-output/implementation-artifacts/journal-decisions-nuit.md, etat-nuit.md
    severity: medium
  - summary: >-
      Les extraits verbatim des items Q (provenance[].extrait) ne sont pas confrontés automatiquement au parquet.
    evidence: |-
      Seuls LC, RE, CO réels et les bases CT ont un test verbatim. Pour Q, y compris Q-067, la vérification ne repose que sur le vérificateur indépendant. La lacune date de la story 7.2 ; il faut un test Q global (duckdb, SLMSP_EVAL_SOURCES).
    location: >-
      tests/eval_outils/ (aucun test Q verbatim)
    severity: medium
---

<intent-contract>

## Intent

**Problem:** Les 225 items v1.0 sont rédigés et vérifiés Tâche par Tâche, mais le jeu n'a jamais été contrôlé dans son ensemble, ni assemblé, ni gelé. Tant que le commit de gel `v1.0-provisoire` n'existe pas, la Baseline ne peut pas démarrer et aucune Donnée d'entraînement ne peut être générée (D1.3).

**Approach:** Corriger les trois constats bloquants de la double vérification finale transversale : remplacer Q-056 et CT-003, qui reprennent le calibrage, et aligner les libellés d'emplacement CT sur le contrôle automatique exact. Ajouter une sous-commande `revue` à `construire_jeu.py`, qui exporte l'échantillon de relecture en JSONL et en Markdown lisible, ainsi qu'un test transversal du jeu. Ensuite, après la revue, assembler, valider en strict, geler avec `slmsp eval gel`, exporter la revue et faire le commit de gel.

## Boundaries & Constraints

**Always:**
- Zone : `eval/construction/v1.0/**`, `eval/outils/construire_jeu.py` (ajout de la sous-commande `revue` seulement), `eval/construction/v1.0/README.md` (ligne de la commande `revue`), `tests/eval_outils/`, puis, au gel, `eval/jeu/v1.0/` et `eval/revue/`.
- **Remplacements (README v1.0).** Un item qui reprend le calibrage reçoit d'abord un verdict `rejete` (motif `doublon_thematique`, `detail` qui cite la vérification finale et la source du calibrage). Il est ensuite remplacé par un nouvel item, au numéro libre suivant, sur un autre sujet, avec la même Tâche, la même difficulté, le même thème et les mêmes caractéristiques de composition :
  - **Q-056 → Q-067.** Même thème, même difficulté et même `sans_reponse` que Q-056. L'amorce réelle est facultative : la cible des 50 % reste atteinte, mais l'amorce d'une ligne `assistant_ia` déjà prise par un autre item est interdite. La fiche doit être différente de F1878 et de toute fiche citée par le calibrage ou par un autre item v1.0. Les faits viennent du parquet service-public (rév. `29f236f8a5`) et sont recopiés tels quels, avec `chunks` et `extrait` ; même gabarit que les autres Q (story 7.2).
  - **CT-003 → CT-016.** Accusé de réception, `difficile`, même thème que CT-003. Le scénario doit être sans régime du silence vaut acceptation ni R112-5 / L112-3 / L112-6 CRPA. Base réelle facultative, tirée de LEGI ou d'une fiche, sauf les articles du calibrage ; même gabarit que les autres CT (story 7.5), consigne alignée.
  - Les composition, répartition des types CT (4/4/4/3) et thèmes de SPEC §2 restent inchangés.
- Un item modifié garde son `id` et `version_item = 1`. Il est revérifié par un sous-agent indépendant, sans le contexte du rédacteur, et le nouveau verdict est ajouté en fin de `verification/<CODE>.jsonl` (ajout seul).
- **CT, alignement des emplacements.** Le banc compare au « libellé exact entre crochets » (ARCHITECTURE-SPINE, contrôle CT). Chaque `entree.consigne` CT se termine donc par une phrase qui liste, dans l'ordre, les libellés exacts de `champs_a_laisser_en_emplacement`. Gabarit : « Laisse les informations non fournies en emplacement, avec exactement ces libellés : [A], [B], [C]. » Les 14 CT existants retenus ne changent que par cette phrase. Le verdict `rejete` de Q-056 et de CT-003 cite le constat du vérificateur final indépendant (Design Notes).
- `revue --version v1.0 [--racine]` lit `eval/jeu/<version>/MANIFEST.json` (liste `echantillons.relecture`) et `items.jsonl`. Il écrit, par création exclusive (refus si le fichier existe, code 2) :
  - `eval/revue/echantillon-revue-<version>.jsonl` : les items de l'échantillon, recopiés tels quels depuis `items.jsonl`, dans l'ordre du manifeste, en UTF-8 et LF ;
  - `eval/revue/echantillon-revue-<version>-lecture.md` : une fiche par item, avec un titre (`id`, Tâche, difficulté, thème), une case « Relu », une ligne « Remarques », puis chaque champ rendu lisiblement : texte multiligne en bloc, listes en puces, objets en sous-puces ; aucune séquence `\n` échappée.
  - Il refuse (code 2, aucun fichier) si le manifeste manque ou si un identifiant de l'échantillon est absent de `items.jsonl`.
- Graine du gel : `20261012`. Statut : `provisoire`. Fins de ligne LF (`.gitattributes` : `* text=auto eol=lf`, déjà présent).
- Tests hors réseau. Le test transversal lit les brouillons en lecture seule.

**Never:**
- Modifier `src/`, `config/`, `eval/calibrage/`, `eval/cassettes/`, la SPEC, la grille, `decisions.md` ou les autres documents de décision ; écrire le manifeste autrement que par `slmsp eval gel`.
- Exécuter le gel réel, ou écrire `eval/jeu/` ou `eval/revue/` dans le dépôt, pendant l'implémentation : le gel se fait à la finalisation, après la revue (voir « Clôture »).
- Supprimer une ligne de verdict, un brouillon ou une cassette ; réattribuer un `id`.
- Appeler le réseau ou une API payante. Faire un `push`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Revue nominale | manifeste + `items.jsonl` dans `tmp_path` | JSONL = lignes de l'échantillon, identiques à `items.jsonl`, dans l'ordre du manifeste ; Markdown avec une fiche par item, sans `\n` échappé | code 0 |
| Revue déjà exportée | l'un des deux fichiers existe | rien n'est écrit ni écrasé | code 2, message |
| Manifeste absent | pas de `MANIFEST.json` | aucun fichier écrit | code 2, message |
| Identifiant inconnu | échantillon citant un `id` absent de `items.jsonl` | aucun fichier écrit | code 2, message qui cite l'`id` |
| CT aligné | les 15 CT retenus | chaque libellé de `champs_a_laisser_en_emplacement` figure tel quel dans `entree.consigne` | test en échec qui nomme l'item |
| Source du calibrage | tout item v1.0 retenu (8 Tâches) | aucune fiche `F…` ni aucun `LEGIARTI…` cité dans le calibrage n'apparaît dans ses `provenance`, `sources_attendues` ou `base_reglementaire` | test en échec qui nomme l'item et la source |

</intent-contract>

## Code Map

- `eval/outils/construire_jeu.py:874` (`cmd_assembler`) -- modèle de sous-commande (`--version`, `--racine`, sortie Markdown, `ErreurOutil` → code 2) ; `analyser` l. 1320 et `main` l. 1367 à étendre ; `lire_jsonl` l. 772, `_ecrire_texte` l. 386 (écrit en LF, mais sans exclusivité : utiliser `open("x")`).
- `src/slmsp/evaluation/gel.py:345` (`rendre_revue`) -- export Markdown officiel du gel (`eval/revue/echantillon-revue-v1.0.md`, JSON brut indenté) ; ne pas modifier. `gel.py:388` (`gel`) écrit cet export puis `MANIFEST.json` ; `verifier_manifeste` l. 492 ; `jeu_gele_et_commite` l. 547.
- `src/slmsp/core/schemas/manifeste_jeu.py` -- `ManifesteJeu.echantillons.relecture` (liste d'`id` triés), `second_juge`, `graine`.
- `src/slmsp/evaluation/config.py:60` -- `PART_RELECTURE = 1/5`, `MIN_RELECTURE = 1` ; `chemin_revue` l. 81.
- `src/slmsp/cli/eval.py` -- `slmsp eval gel --version v1.0 (--verifier-seulement | --statut provisoire --graine N) [--racine]`.
- `src/slmsp/core/items.py` -- `lire_jeu`, `valider_item(strict=True)`, `empreintes_antifuite` (versions par nom, `racine`).
- `tests/eval_outils/test_construire_jeu.py` -- chargement de l'outil par chemin (`importlib`), fixtures `tmp_path` ; `tests/eval_outils/test_items_co_re_ct.py` -- modèle de tests CT (verdicts, lecteur strict).
- `eval/construction/v1.0/CT.jsonl` -- 15 CT ; libellés hétérogènes (`[Commune]`, `[Nom de la commune]`, `[Lieu d'émission du courrier]`…), absents des consignes.
- `eval/construction/v1.0/verification/*.jsonl` -- verdicts en ajout seul ; le dernier l'emporte.
- Sources figées (lecture seule) : `C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\data\raw\eval-sources\` (parquet service-public `hf/AgentPublic/service-public/latest/train/0000.parquet`, LEGI `hf/AgentPublic/legi/data/legi-latest/legi_<code>/*.parquet`, corpus d'amorces, `INDEX.json`). Outils d'exploration déjà écrits, dans le scratchpad `C:\Users\UTILIS~1\AppData\Local\Temp\claude\C--Users-Utilisateur-Documents-GitHub-service-public-slm-fine-tuning\2b525399-9658-4abc-ae6d-dabcdbffc874\scratchpad\` : `s75\explore.py` (`fiche F…`, `titre <motif>`), `s75\legi.py`, `fiches.py`, `recherche.py`, `titres.txt`, `sp_questions.jsonl`, `assistant_ia.jsonl`. Ils se lancent par `uv run --no-project --python 3.12 --with duckdb python -I <script>`, avec `PYTHONIOENCODING=utf-8`. Le gabarit Q est dans `spec-7-2-…md` (« Gabarit Q »), le format CT dans `spec-7-5-…md`.
- `_bmad-output/planning-artifacts/architecture/.../ARCHITECTURE-SPINE.md:555` -- contrôle CT : « libellé exact entre crochets de `champs_a_laisser_en_emplacement` ».

## Tasks & Acceptance

**Execution:**
- `eval/construction/v1.0/verification/{Q,CT}.jsonl` -- ajouter les verdicts `rejete` de Q-056 et CT-003 (constat de la vérification finale, voir Design Notes) -- traçabilité du remplacement.
- `eval/construction/v1.0/Q.jsonl` -- ajouter Q-067 (remplaçant de Q-056), écrit à partir du parquet ; Q-056 reste dans le brouillon -- règle du README.
- `eval/construction/v1.0/CT.jsonl` -- ajouter CT-016 (remplaçant de CT-003). Ajouter à chaque `entree.consigne` des 15 CT retenus la phrase des libellés exacts (gabarit ci-dessus), par script de scratchpad, avec JSON `ensure_ascii=False` et LF -- aligner sur le contrôle automatique exact.
- `eval/construction/v1.0/verification/{Q,CT}.jsonl` -- faire relire Q-067, CT-016 et les 14 autres CT modifiés par un ou plusieurs sous-agents indépendants (sans le contexte du rédacteur) ; ajouter leurs verdicts tels quels ; corriger puis revérifier tout rejet -- double vérification (SPEC §5.2).
- `tests/eval_outils/test_items_co_re_ct.py`, `test_construire_jeu.py`, `test_items_rd.py`, `test_items_cr_lc.py` -- adapter seulement les assertions qui supposent des identifiants CT contigus ou un `id` précis remplacé (par exemple CT-003) -- les remplacements créent un trou de numérotation légitime.
- `eval/outils/construire_jeu.py` -- sous-commande `revue` (matrice) ; `eval/construction/v1.0/README.md` -- une ligne dans le tableau des commandes.
- `tests/eval_outils/test_revue.py` -- lignes « Revue » de la matrice, sur un manifeste et des items factices dans `tmp_path`.
- `tests/eval_outils/test_jeu_v1.py` -- test transversal sur les brouillons réels : lignes « CT aligné » et « Source du calibrage » ; identifiants uniques entre fichiers et cohérents avec la Tâche ; dernier verdict `accepte` pour chaque item retenu ; 225 items retenus aux cibles de SPEC §2. Si `eval/jeu/v1.0/MANIFEST.json` existe : `verifier_manifeste("v1.0")` passe, `items.jsonl` contient exactement les items retenus, et l'export JSONL de revue, s'il existe, couvre exactement `echantillons.relecture`.

**Acceptance Criteria:**
- Given les brouillons corrigés, when on lance `construire_jeu.py composition`, then les 8 Tâches sont aux cibles de SPEC §2, sans anomalie et sans item sans verdict.
- Given une copie de `eval/` et `config/`, when on lance `assembler --racine <copie>` puis `uv run slmsp eval gel --version v1.0 --verifier-seulement --racine <copie>`, then 225 items stricts sont acceptés, 0 erreur bloquante, code 0.
- Given `SLMSP_EVAL_SOURCES` qui pointe vers les instantanés, when on lance les tests `tests/eval_outils`, then tout passe, y compris les tests verbatim (LC, RE, CO réels), qui ne sont pas ignorés.

## Clôture (après la revue, par l'agent de story)

1. `construire_jeu.py assembler --version v1.0` → `eval/jeu/v1.0/items.jsonl` (225 items, 0 sans verdict).
2. `uv run slmsp eval gel --version v1.0 --verifier-seulement` → code 0.
3. `uv run slmsp eval gel --version v1.0 --statut provisoire --graine 20261012` → `MANIFEST.json` et `eval/revue/echantillon-revue-v1.0.md`.
4. `construire_jeu.py revue --version v1.0` → JSONL et Markdown de lecture.
5. Contrôle par `verifier_manifeste`, et relance de `tests/eval_outils/test_jeu_v1.py`.
6. Commit de la spec et des tests, puis commit dédié `eval: gel du jeu d'évaluation v1.0-provisoire` (ligne d'attribution), limité à `eval/jeu/v1.0/`, `eval/cassettes/`, `eval/revue/` et `eval/construction/v1.0/`. Contrôle par `git show --stat`.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 38 findings — high 0, medium 7, low 25, false 6, maybe-false 0
- findings:
  - **Edge Case Hunter (12)**
    - `[low]` `[patch]` Une `OSError` autre que `FileExistsError` au second écrit laisse un export partiel, qui bloque toute reprise. Corrigé : `except OSError`, avec nettoyage des seuls fichiers créés par l'appel, et test `test_revue_echec_second_ecrit` (ENOSPC simulé).
    - `[low]` `[reject]` Un `id` dupliqué dans `items.jsonl` est écrasé sans alerte — `assembler` refuse les doublons et `eval gel` valide le fichier en strict ; garde ajoutée pour un état non démontré.
    - `[low]` `[reject]` Une ligne sans `id` est ignorée — même motif : fichier produit par `assembler` et validé au gel.
    - `[low]` `[reject]` `relecture` vide ou dupliquée — le tirage de `gel` donne au moins 1 item par strate, triés et uniques ; état inatteignable par le producteur.
    - `[low]` `[reject]` `items.jsonl` modifié après le gel non détecté par `revue` — la clôture lance `verifier_manifeste` et `test_export_revue_couvre_l_echantillon` juste après ; garde supplémentaire.
    - `[low]` `[reject]` `\r` isolé dans une valeur — aucun item n'en contient (LF contrôlé par la vérification finale).
    - `[low]` `[reject]` Saut de ligne dans `tache`, `difficulte` ou `theme` — valeurs fermées, validées par le lecteur strict.
    - `[low]` `[reject]` `MANIFEST.json` illisible (droits) donne une trace — cas improbable, trace explicite.
    - `[low]` `[reject]` Ligne de brouillon non objet : erreur de collecte — échec bruyant, déjà couvert par `ERREURS_BROUILLONS`.
    - `[medium]` `[patch]` `RE_SOURCE` ne voit que `F…` et `LEGIARTI…` — groupé avec VG « calibrage » ; corrigé.
    - `[low]` `[reject]` CT à liste d'emplacements vide : faux échec — aucun CT retenu n'a de liste vide, et le lecteur strict exige une liste non vide.
    - `[low]` `[reject]` BOM en tête d'`items.jsonl` — les fichiers sont écrits sans BOM par l'outil ; état non démontré.
  - **Intent Alignment (6)**
    - `[medium]` `[defer]` Taux de rejet par Tâche non reportés dans le journal et `etat-nuit.md` (AC 3) — les consignes de nuit confient ces fichiers à l'orchestrateur ; taux consignés dans `## Auto Run Result` et remis dans le compte rendu (frontmatter `deferred`).
    - `[low]` `[defer]` Constats non bloquants non routés vers les « points à trancher » — même cause : consignés ci-dessous et remis à l'orchestrateur.
    - `[false]` `[reject]` Gel, manifeste et commit absents du diff — prévus en clôture, après la revue, et exécutés avant le commit (voir `## Auto Run Result`).
    - `[false]` `[reject]` Contenu d'items modifié avant le gel — SPEC §5.2-§5.3 imposent rejet, remplacement et revérification avant le gel.
    - `[false]` `[reject]` Artefacts de revue en plus — additifs ; l'export officiel du gel reste inchangé, aucune attente n'est contredite.
    - `[low]` `[reject]` Outil de la story 7.1 modifié hors zone — l'outil appartient à l'epic 7, et la sous-commande est additive.
  - **Verification Gap (6)**
    - `[medium]` `[patch]` Le test « source du calibrage » n'aurait pas attrapé CT-003 (articles cités par numéro). Corrigé : les numéros d'article du calibrage ({L112-3, R112-5, L112-6}) sont comparés, sur les 8 Tâches.
    - `[medium]` `[patch]` Répartition des thèmes non contrôlée. Corrigé : 42/21/21/21/21/14 sur les 140 Q, RD, LC et RE retenus.
    - `[medium]` `[defer]` Les `extrait` des Q, Q-067 compris, ne sont pas confrontés au parquet — lacune antérieure (story 7.2), à couvrir par un test Q global (frontmatter `deferred`).
    - `[low]` `[patch]` Branche de nettoyage de `cmd_revue` jamais exécutée — groupé avec ECH « OSError » ; test ajouté.
    - `[false]` `[reject]` Tests du jeu gelé ignorés — ils tournent en clôture, après le gel (voir `## Auto Run Result`).
    - `[false]` `[reject]` Fichiers de tests listés mais non modifiés — ils passaient sans adaptation ; aucun effet.
  - **Blind Hunter (14)**
    - `[medium]` `[patch]` Le test des sources du calibrage ne couvre pas un recouvrement de scénario de type CT-003 — groupé avec VG ; corrigé.
    - `[low]` `[patch]` `RE_SOURCE` manque les références sans identifiant — groupé avec VG ; corrigé.
    - `[low]` `[reject]` Pas de contrôle d'intégrité ni de version du manifeste dans `revue` — même motif que la ligne ECH correspondante.
    - `[low]` `[patch]` Export partiel après un échec d'écriture — groupé avec ECH « OSError » ; corrigé.
    - `[low]` `[reject]` Valeurs non échappées dans le Markdown (`<a>`, `*`) — le JSONL et l'export officiel restent exacts ; l'échappement ajouterait une logique pour un rendu cosmétique.
    - `[low]` `[reject]` Identifiants dupliqués non détectés — même motif que la ligne ECH correspondante.
    - `[low]` `[reject]` Chemins non testés dans `test_revue.py` (items absents, JSON illisible, BOM, chaîne multiligne imbriquée) — erreurs bruyantes ou états non démontrés ; seul le nettoyage est testé.
    - `[low]` `[patch]` Jeu gelé sous-contrôlé. Corrigé : import direct de `slmsp.evaluation.gel`, au lieu d'un skip, et existence exigée des deux exports Markdown.
    - `[false]` `[reject]` L'amorce de Q-067 serait déjà utilisée — la ligne 2170 de `sp_questions_corpus` n'est citée que par Q-067 (contrôle par script).
    - `[medium]` `[patch]` CT-016 : en-tête du centre hospitalier exigé, mais nom ni fourni ni en emplacement. Corrigé : `[Nom du centre hospitalier]` est le premier libellé, la consigne est réalignée et un nouveau vérificateur indépendant a rendu `accepte`. La remarque CRPA (établissement public) est laissée à la relecture d'Anaël.
    - `[low]` `[reject]` Lister les libellés rend la tâche plus facile, et les difficultés n'ont pas été réévaluées — choix motivé (Design Notes) et réversible en v1.1 ; signalé à Anaël.
    - `[low]` `[reject]` Tenue de la spec (journal, `deferred`, numéros de ligne) — le correctif édite la spec ; la finalisation écrit `## Auto Run Result`.
    - `[low]` `[patch]` README : la ligne des options ignorait `revue`. Corrigé.
    - `[low]` `[patch]` `test_composition_ct` contrôlait les `objet` en double sur les CT rejetés. Corrigé : contrôle limité aux CT retenus.

## Design Notes

**Constats de la vérification finale** (sous-agent indépendant, lecture seule) : voir ci-dessous.

- **Contrôles conformes** :
  - 225 items retenus (8 exclus : Q-018, Q-033, Q-039, Q-061, Q-064, Q-065, NR-025, NR-030), tous aux cibles de SPEC §2, avec un écart nul ;
  - identifiants cohérents, aucun verdict orphelin, aucun item sans verdict ; 31 rejets sur 343 verdicts ;
  - `eval gel --verifier-seulement` sur une copie : 225 items stricts, 40 cassettes, 0 erreur ;
  - `tests/eval_outils` avec les instantanés : 413 passés et 0 ignoré, dont 62 tests verbatim ;
  - `uv run pytest` : 1 738 passés ; `ruff` propre ;
  - fichiers en LF, sans BOM.
- **Bloquant 1, Q-056** : il reprend F1878, la source de RS-001 du calibrage, et ses montants (16 5-grammes communs). C'est la seule source v1.0 partagée avec le calibrage, et aucun test ne contrôle les sources du calibrage pour Q.
- **Bloquant 2, CT-003** : il reprend le scénario de CT-002 du calibrage (accusé de réception avec silence vaut acceptation, éléments de R112-5). C'est le recouvrement maximal avec le calibrage : 42 5-grammes, 62 empreintes anti-fuite sur 180.
- **Bloquant 3, CT** : aucune consigne ne donne les libellés exacts, et ils varient (`[Commune]` ×10, `[Nom de la commune]` ×3, `[Lieu d'émission du courrier]` ×2…).
- **Non bloquant**, consigné pour la relecture d'Anaël :
  - Q-045 (F33312) est proche du sujet de LC-002 du calibrage ;
  - Q-048 suit le gabarit de Q-002 du calibrage (37 5-grammes, hors entrée) ;
  - CT-005 et CT-007 ont le même type que CT-001 du calibrage ;
  - CR-023 reprend une action de CR-001 du calibrage ;
  - des paires LC × Q partagent une fiche (LC-008/Q-031 F263, LC-006/Q-044 F1174, LC-011/Q-016, LC-002/Q-016) : l'entrée LC contient la réponse du Q ;
  - LC-002 et RE-010 portent sur le même contenu (Apa) ;
  - CO réels en `fictif: false` (contre SPEC §1.4 « textes à fautes ») ;
  - `consulte_le` mêle date et date-heure ; `licence_source` a 28 formulations.

**Pourquoi lister les libellés dans la consigne.** Le contrôle automatique CT exige le libellé exact. Sans la liste, le score mesurerait la capacité à deviner `[Commune]` plutôt que `[Nom de la commune]`, et non le refus d'inventer une valeur (FR-14). La liste garde l'épreuve : le modèle doit placer chaque emplacement au bon endroit et n'inventer aucune des `valeurs_interdites`. C'est réversible en v1.1, si le banc devient tolérant.

**Markdown de lecture en plus de l'export du gel.** L'export de `slmsp eval gel` (`echantillon-revue-v1.0.md`, SPEC §5.4) reste le document officiel, mais il contient du JSON brut, illisible pour les transcriptions longues. Le fichier `-lecture.md` présente les mêmes items, rendus champ par champ ; le JSONL sert aux outils.

## Verification

**Commands:**
- `uv run --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py composition` -- expected: 8 Tâches aux cibles, aucune anomalie, aucun item sans verdict.
- `uv run --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py rejets` -- expected: taux par Tâche affichés.
- Avec `SLMSP_EVAL_SOURCES=C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\data\raw\eval-sources` : `uv run --with duckdb pytest tests/eval_outils -q -rs` -- expected: tout passe, aucun test verbatim ignoré.
- Copie temporaire de `eval/` et `config/` : `assembler --racine <copie> --version v1.0`, puis `uv run slmsp eval gel --version v1.0 --verifier-seulement --racine <copie>` -- expected: 225 items, 0 erreur bloquante, code 0.
- `uv run pytest -q` et `uv run ruff check` -- expected: verts, ou échecs préexistants hors zone listés.

## Auto Run Result

Status: done
Blocking condition: aucune

Story réalisée par le sous-agent de story 7.6 le 2026-10-12 (bmad-build-auto, mode autonome, sans push).

**Résumé.**
- Double vérification finale transversale, par un sous-agent indépendant en lecture seule : 3 constats bloquants, tous corrigés.
  - Q-056 reprenait F1878, une source du calibrage. Il est rejeté et remplacé par Q-067 (F815, allocation de soutien familial, `moyen`, `famille-education-sante`).
  - CT-003 reprenait le scénario de CT-002 du calibrage. Il est rejeté et remplacé par CT-016 (accusé de réception d'une demande de dossier médical, F12210, `difficile`).
  - La consigne des 15 CT retenus se termine désormais par la liste des libellés exacts d'emplacement, car le contrôle automatique compare le libellé exact. `[Nom du centre hospitalier]` est ajouté à CT-016 après la revue.
- Chaque item modifié ou nouveau a été revérifié par un sous-agent indépendant, avec verdicts ajoutés en fin de fichier. CT-016 a d'abord été rejeté (`ambigu`), corrigé, puis accepté (et de nouveau après le correctif de revue).
- Nouvelle sous-commande `construire_jeu.py revue` : export JSONL et Markdown lisible de l'échantillon de relecture du manifeste.
- Nouveau test transversal `test_jeu_v1.py` : identifiants, verdicts, composition et thèmes, alignement CT, sources et articles du calibrage, jeu gelé.
- **Gel `v1.0-provisoire` exécuté** :
  - `assembler` : 225 items, 10 exclus ; SHA-256 `b6342dbb5c6b16955ec9d0763c8d5c85858b9357ebab5d181b904623a680c684`.
  - `slmsp eval gel --verifier-seulement` : 225 items stricts, 40 cassettes, 0 erreur, 0 écart.
  - `slmsp eval gel --statut provisoire --graine 20261012` : 42 fichiers empreints, second juge 34 items, relecture 47 items, 0 écart de composition.
  - SHA-256 de `MANIFEST.json` : `70c42fb539cf6a02fcc5b7239450f77946882188c04c0b2c73eef14d9ab043dc`.
  - `revue --version v1.0` : 47 items exportés.

**Décompte final.** Q 60 (20/25/15, 8 sans réponse, 49 amorces réelles), RD 40 (15/15/10), CR 25 (8/10/7), LC 25 (8/10/7), CO 15, RE 15, CT 15 (5/5/5), NR 30 (10/10/10) ; thèmes 42/21/21/21/21/14.

**Taux de rejet** (rejets / verdicts, `construire_jeu.py rejets`) : Q 12/87 (13,8 %), RD 1/65 (1,5 %), CR 6/41 (14,6 %), LC 2/30 (6,7 %), CO 3/21 (14,3 %), RE 3/34 (8,8 %), CT 4/35 (11,4 %), NR 3/50 (6,0 %) ; total 34/363 (9,4 %).

**Fichiers.**
- `eval/construction/v1.0/Q.jsonl` : ajout de Q-067. `CT.jsonl` : 14 consignes alignées, CT-016 ajouté. `verification/{Q,CT}.jsonl` : rejets et revérifications, en ajout seul. `README.md` : commande `revue`.
- `eval/outils/construire_jeu.py` : sous-commande `revue`.
- `eval/jeu/v1.0/items.jsonl`, `eval/jeu/v1.0/MANIFEST.json` : jeu gelé.
- `eval/revue/echantillon-revue-v1.0.md` (export officiel du gel), `echantillon-revue-v1.0.jsonl`, `echantillon-revue-v1.0-lecture.md`.
- `tests/eval_outils/test_revue.py`, `test_jeu_v1.py` (nouveaux) ; `test_items_co_re_ct.py` (items retenus seulement).

**Revue** (38 constats : high 0, medium 7, low 25, false 6).
- Correctifs : 7 entrées, dont 3 medium et 4 low.
  - Medium : articles du calibrage contrôlés, thèmes contrôlés, emplacement du nom du centre hospitalier dans CT-016.
  - Low : nettoyage sur toute `OSError` dans `revue`, contrôles du jeu gelé, README, `objet` CT sur les retenus.
- Reportés : 2 entrées (frontmatter `deferred`) : le journal et `etat-nuit.md`, tenus par l'orchestrateur ; le test verbatim des Q.
- Rejetés : 23, motifs dans le journal de triage.

**Revue de suivi recommandée : `true`.** Trois entrées medium ont été corrigées en une passe. Le risque non revérifié est le contrôle par numéros d'article du calibrage : il exclut le texte recopié des bases (`texte`, `extrait`) pour ne pas signaler CT-007, et un recouvrement de scénario sans article commun, comme l'était CT-003, ne reste détecté que par un vérificateur.

**Vérifications.**
- Avec `SLMSP_EVAL_SOURCES` : `uv run --with duckdb pytest tests/eval_outils -q -rs` → 452 passés, 0 ignoré, verbatim et jeu gelé compris.
- `verifier_manifeste("v1.0")` → OK (provisoire, 225 items, 47 en relecture).
- `uv run pytest -q` (avant le gel) → 1 772 passés et 1 échec : `tests/inference/test_serveur.py::test_demarrage_rate_sante` (story 2.2, hors zone, instable sous charge), qui passe seul (24 passés).
- `uv run ruff check` et `ruff format --check` → propres.
- Fichiers gelés et exports : LF, sans BOM.

**Décisions prises seul.**
- Les libellés exacts d'emplacement sont listés dans la consigne CT, ce qui aligne les items sur le contrôle exact (ARCHITECTURE-SPINE). C'est réversible en v1.1 si le banc devient tolérant.
- La graine du gel est 20261012.
- Le Markdown de lecture (`-lecture.md`) s'ajoute à l'export officiel, qui contient du JSON brut.
- Q-056 et CT-003 sont remplacés plutôt qu'acceptés tels quels, car ils reprennent le calibrage (SPEC §1.1).
- Le journal, `etat-nuit.md` et `sprint-status.yaml` ne sont pas modifiés, car ils relèvent de l'orchestrateur.
- L'ancre de date des montants annuels (report de 7.2) est laissée à la v1.1.

**Points à relire par Anaël.**
- Constats non bloquants de la vérification finale (Design Notes) :
  - Q-045 et Q-048 sont proches de sujets du calibrage ;
  - CT-005 et CT-007 ont le même type que CT-001 du calibrage ;
  - CR-023 reprend une action de CR-001 du calibrage ;
  - des paires LC × Q partagent une fiche, et l'entrée LC contient la réponse du Q ;
  - LC-002 et RE-010 portent sur l'Apa ;
  - les CO réels sont en `fictif: false` ;
  - `consulte_le` et `licence_source` sont hétérogènes.
- CT-016 : le centre hospitalier public relève aussi du CRPA. Les libellés listés rendent par ailleurs la Tâche CT plus facile.
- Reports des stories antérieures toujours ouverts :
  - aucun item sur les marchés publics ;
  - pas d'ancre de date ;
  - Q-042 (1/24e) ;
  - les « sans réponse » sont prouvés sur l'index v1 seulement ;
  - les verdicts ne sont pas liés au contenu par une empreinte.