---
title: 'Jeu d''évaluation v1.1 : corrections arbitrées, ancre de date et export de relecture'
type: 'feature'
created: '2026-10-13'
status: 'done'
route: 'dispatch'
baseline_revision: '0ce18a8e0b1276850e5cac2383eee0310c2b5472'
baseline_commit: '0ce18a8e0b1276850e5cac2383eee0310c2b5472'
review_loop_iteration: 0
context:
  - '{project-root}/eval/revue/arbitrages-v1.1.md'
  - '{project-root}/eval/construction/v1.0/README.md'
  - '{project-root}/eval/SPEC-jeu-evaluation.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-7-6-double-verification-finale-echantillon-de-revue-et-gel-v1-0-provisoire.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Le jeu v1.0-provisoire contient une erreur de droit (Q-042), aucun item sur les marchés publics, aucune transcription au cas limite de FR-13, des contrôles RD trop larges ou incomplets et des CO réels mal marqués ; son manifeste n'a pas d'ancre de date. Tant que la v1.1 n'est pas gelée `relu`, les scores restent « non relus ».

**Approach:** Appliquer `eval/revue/arbitrages-v1.1.md` (options cochées, et la section « Ajustements validés (2026-10-13) », qui fait foi) dans des brouillons `eval/construction/v1.1`, faire revérifier chaque item modifié ou nouveau par un vérificateur indépendant, assembler et vérifier, puis exporter les changements pour la relecture d'Anaël. Le gel `--statut relu` n'a lieu qu'après cette relecture.

## Boundaries & Constraints

**Always:**
- **Base.** `eval/construction/v1.1/` part d'une copie intégrale de `v1.0/` (brouillons, `verification/` en ajout seul, README). Les verdicts v1.0 restent valables pour les items inchangés.
- **Items modifiés** (`version_item: 2`, SPEC §6, même `id`) :
  - Q-042 (A) : retirer la demande de plafond de `entree`, `reponse_reference` et `elements_cles`, et le calcul de l'extrait ; garder calendrier et remboursement, `difficile`.
  - CR-006 et CR-021 (F) : plus de 6 500 mots, par des échanges sans nouvelle décision, action ni piège ; `nb_mots` recalculé par `core.texte` ; références inchangées et revérifiées.
  - RD-010, RD-017, RD-023, RD-030, RD-039 (G1) : `valeurs_attendues.colonnes` selon le tableau G1.
  - RD-017, RD-019, RD-031 (G2) : fragments selon G2 ; « REI » en mot entier.
  - CO-001, CO-002, CO-006, CO-007, CO-011, CO-012 (G4) : `fictif: true`, rien d'autre.
- **Remplacements (E).** Q-044 (facile), Q-046 (moyen) et Q-050 (difficile) reçoivent un verdict `rejete` (motif `autre`, `detail` qui cite l'arbitrage E). Trois nouveaux Q `collectivites` sur les marchés publics, **Q-068 (facile), Q-069 (moyen) et Q-070 (difficile)** (décision d'Anaël du 2026-10-13 : Q-061 à Q-063 existent déjà, numéros libres suivants) (seuils de procédure, publicité, délais), aux mêmes difficultés, `sans_reponse: false`, gabarit Q de la story 7.2. Faits recopiés du parquet service-public (rév. `29f236f8a5`), fiches `entreprendre.service-public.gouv.fr`, présentes dans l'Index `20260926`, différentes de F33466 et F32213 (RE-009, RE-013) et sans doublon thématique avec eux. Amorce réelle facultative, jamais une ligne déjà prise.
- **Inchangés.** Tous les autres items, y compris CT-016, `consulte_le` et `licence_source`.
- **Règle RD en mot entier.** Nouvelle règle d'argument facultative (liste de mots entiers, combinée en « ou » avec `contient_un_de`) dans `RegleArgument` et `controles.py`. Le `model_dump(mode="json")` d'un item qui ne l'utilise pas reste identique octet pour octet, pour garder les clés du cache des verdicts.
- **`date_reference`.** Champ `date_reference: date | None = None` dans `ManifesteJeu` (`schema_version` reste 1, le manifeste v1.0 reste valide) ; option `--date-reference AAAA-MM-JJ` de `slmsp eval gel`, interdite avec `--verifier-seulement`, refusée si postérieure à la date du gel ; tests.
- **Double vérification (SPEC §5.2).** Chaque item modifié ou nouveau est relu par un sous-agent indépendant, sans le contexte du rédacteur, contre ses sources ; verdict ajouté en fin de `verification/<CODE>.jsonl`. Tout rejet est corrigé puis revérifié.
- **Export de relecture avant le gel.** Après `assembler --version v1.1` et `eval gel --version v1.1 --verifier-seulement` (code 0, 225 items, 0 écart), exporter les items nouveaux, modifiés et retirés par rapport à `eval/jeu/v1.0/items.jsonl` : un JSONL et un Markdown lisible dans `eval/revue/`, avec, pour chaque item modifié, l'ancienne et la nouvelle valeur de chaque champ changé.
- **Limites documentées** dans `eval/construction/v1.1/README.md` : hétérogénéité de `consulte_le` et `licence_source` (G4), mentions CRPA exactes non pénalisées pour CT-016 (D1), libellés CT listés (D2), « sans réponse » prouvés sur l'Index `20260926` seulement (H).
- Composition et thèmes de SPEC §2 inchangés ; graine du gel `20261013` ; `date_reference` `2026-10-12` ; LF, UTF-8, `ensure_ascii=False`.

**Never:**
- Produire des Données d'entraînement, des amorces ou des exemples few-shot pour l'entraînement.
- Exécuter `eval gel --statut relu` avant la relecture d'Anaël ; modifier `eval/jeu/v1.0/`, `eval/revue/*v1.0*`, `eval/calibrage/`, la grille, la SPEC ou `eval/cassettes/`.
- Supprimer une ligne de verdict ou un brouillon ; réattribuer un `id` à un autre sujet.
- Appeler une API payante, relancer la Baseline, faire un `push`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Mot entier | règle `REI`, requête « fichier REI 2024 » / « Reims » | accepté / refusé | — |
| Item RD sans la règle | RD v1.0 | `model_dump` identique à celui d'avant le changement | test en échec |
| Gel avec date | `--statut relu --graine N --date-reference 2026-10-12` | `MANIFEST.json` contient `"date_reference": "2026-10-12"` | — |
| Date invalide | `--date-reference` mal formée ou future, ou avec `--verifier-seulement` | aucun fichier écrit | code 2, message |
| Manifeste v1.0 | `eval/jeu/v1.0/MANIFEST.json` | `verifier_manifeste("v1.0")` passe | — |
| Export des changements | v1.0 gelé, v1.1 assemblé | nouveaux, modifiés (ancien / nouveau par champ) et retirés ; refus si l'export existe | code 2 |

</frozen-after-approval>

## Code Map

- `eval/outils/construire_jeu.py` -- `assembler`, `composition`, `rejets`, `revue` génériques par `--version` (défaut `v1.0`, l. 1517 : toujours passer `--version v1.1`) ; `CIBLES`/`THEMES` l. 74-98 ; `LISTE_BLANCHE` l. 146 inclut `entreprendre` ; modèle de rendu Markdown et d'écriture exclusive dans `cmd_revue` (l. 1400) à réutiliser pour la sous-commande d'export des changements.
- `src/slmsp/core/schemas/manifeste_jeu.py:54-80` -- `ManifesteJeu` (`extra="forbid"`).
- `src/slmsp/evaluation/gel.py:413` (`gel`) -- écrit le manifeste par `model_dump(mode="json")` l. 481 ; `--statut relu` exige 0 erreur et 0 écart ; refuse si `MANIFEST.json` ou l'export existe.
- `src/slmsp/cli/eval.py:61-95, 406-420` -- `executer_gel` et options de `gel`.
- `src/slmsp/core/items.py:166` (`RegleArgument`) ; `src/slmsp/evaluation/controles.py:94-116` (`_debut_de_mot`, `normaliser`) -- règle en mot entier.
- `src/slmsp/judge/cache.py:119` -- clé = SHA du `model_dump(mode="json")` de l'item : `version_item: 2` rejuge seulement les items modifiés.
- `tests/evaluation/test_gel.py` (l. 560-594 schéma, 711-757 CLI) ; `tests/eval_outils/test_jeu_v1.py` (`VERSION="v1.0"` l. 22, à paramétrer sur `v1.0` et `v1.1`) ; `test_items_co_re_ct.py` (sélection des CO réels : par `provenance`, plus par `fictif`) ; `test_items_rd.py`, `test_items_cr_lc.py`.
- Sources figées : `data/raw/eval-sources/` (parquet `hf/AgentPublic/service-public/latest/train/0000.parquet`, colonnes `doc_id`, `chunk_index`, `title`, `url`, `chunk_text`) ; candidats marchés publics : F23371 (seuils de publicité), F32049 (procédures), F23386 (paiement), F32106 (remise des offres), F23387. Index local : `index/20260926/chunks.sqlite`.
- **Révisions non épinglées par `construire_jeu.py sources`** (constat du 2026-10-17). La commande résout `main` ou `refs/convert/parquet` au moment où on la lance. Un nouveau téléchargement change donc les instantanés, et 120 tests `tests/eval_outils` échouent (ex. segment de Q-026#2 introuvable). Seule copie de référence : `data/raw/eval-sources/` de la tour, publiée dans la release `etat-2026-10-17b` du dépôt privé `Aliquanto3/slmsp-etat` (restauration : `outils/migration/restaurer-etat.ps1`). L'outil n'est pas modifié. Révisions réellement utilisées (`INDEX.json`, consultées le 2026-10-12) :
  - `AgentPublic/service-public` : `29f236f8a534bb599cd82b4f9731307bf5c0dbb1` (1 fichier) ;
  - `AgentPublic/legi` : `68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8` (5 fichiers) ;
  - `AgentPublic/data-gouv-datasets-catalog` : `11f3d3c9481ad478dbcff52e85d73b7fd10533ce` (3 fichiers) ;
  - `AgentPublic/sp_questions_corpus` : `495a22cf7b572621a85d2f3e97783b2f4189c47e` (1 fichier) ;
  - `AgentPublic/assistant_ia_questions_corpus` : `62cef57af7cc5fe54862a8118c221246771ad9ea` (1 fichier).

## Tasks & Acceptance

**Execution:**
- [x] `src/slmsp/core/items.py`, `src/slmsp/evaluation/controles.py`, `tests/` -- règle en mot entier et tests (matrice) -- G2 « REI ».
- [x] `src/slmsp/core/schemas/manifeste_jeu.py`, `src/slmsp/evaluation/gel.py`, `src/slmsp/cli/eval.py`, `tests/evaluation/test_gel.py` -- `date_reference` (matrice) -- G3.
- [x] `eval/construction/v1.1/` -- copie de v1.0, puis modifications, rejets et nouveaux Q par scripts de scratchpad -- A, E, F, G1, G2, G4.
- [x] `eval/construction/v1.1/verification/*.jsonl` -- verdicts des vérificateurs indépendants, ajoutés tels quels -- SPEC §5.2.
- [x] `eval/outils/construire_jeu.py`, `tests/eval_outils/` -- sous-commande d'export des changements (matrice) ; `test_jeu_v1.py` paramétré sur v1.1 ; sélection des CO réels.
- [x] `eval/construction/v1.1/README.md` -- commande d'export et limites documentées.
- [x] Clôture : `assembler --version v1.1`, `eval gel --version v1.1 --verifier-seulement`, export des changements, puis arrêt pour la relecture d'Anaël.

**Acceptance Criteria:**
- Given les brouillons v1.1, when on lance `composition --version v1.1`, then les 8 Tâches et les thèmes sont aux cibles de SPEC §2, sans anomalie ni item sans verdict, et chaque item retenu a pour dernier verdict `accepte`.
- Given `SLMSP_EVAL_SOURCES`, when on lance `pytest tests/eval_outils tests/evaluation tests/core`, then tout passe, verbatim compris, sans test ignoré.
- Given v1.1 assemblé, when on lance `eval gel --version v1.1 --verifier-seulement`, then 225 items stricts, 0 erreur, 0 écart, code 0.

## Implementation Notes

- **Règle en mot entier.** La clé est `mot_entier_un_de`. Un sérialiseur la retire quand elle vaut `None`, de sorte que le `model_dump` des 225 items v1.0 ne change pas (SHA figé dans `test_model_dump_v1_0_inchange`).
- **`date_reference`.** Elle est validée trois fois : par la CLI (format, date future, combinaison avec `--verifier-seulement`), par `gel()` et par le schéma. Un manifeste neuf écrit sans date contient `"date_reference": null`.
- **Sous-commande `changements --version v1.1 [--reference v1.0]`.**
  - Elle écrit `eval/revue/changements-v1.0-v1.1.{jsonl,md}`, en écriture exclusive (fonction `_ecrire_exclusifs`, commune avec `revue`).
  - Chaque fiche porte le dernier verdict de l'item.
  - Les textes multilignes et les valeurs JSON sont présentés en diff ligne à ligne.
  - `version_item` accepte désormais tout entier ≥ 1.
- **Données.**
  - Q-042 : le chunk 6 de F31094 sort de l'extrait.
  - CR-006 passe de 5 159 à 6 621 mots, CR-021 de 4 739 à 6 571 (`core.texte`).
  - RD-031 utilise `mot_entier_un_de: ["REI"]`.
  - RD-017 garde « identité », « passeport » et « carte nationale », lecture littérale de G2 : « caen » et « cni » sont retirés.
  - Q-068 (F23371), Q-069 (F32049) et Q-070 (F23371 et F32049) ont `consulte_le` au 2026-10-13.
  - Les copies v1.0 en CRLF de la copie de travail sont normalisées en LF.
- **Double vérification.** Six sous-agents indépendants ont relu les 19 items modifiés ou nouveaux : tous sont `accepte`. Le test `test_v1_1_verdicts_ajoutes_pour_les_items_touches` exige un verdict ajouté après les lignes v1.0.
- **Résultats.**
  - `assembler` : 225 items.
  - `gel --verifier-seulement` : 0 erreur, 0 écart.
  - `changements` : 3 nouveaux, 16 modifiés, 3 retirés.
  - `pytest` complet avec `SLMSP_EVAL_SOURCES` : 3 507 passés, 95 ignorés hors zone (`tests/test_cli.py` et liens symboliques sous Windows), 0 ignoré dans `tests/eval_outils`.
  - `ruff` : propre.
- **Non commité.** `eval/jeu/v1.1/items.jsonl` (assemblé, non gelé) est réservé au commit de gel `relu`, après la relecture d'Anaël.

## Spec Change Log

## Review Triage Log

### 2026-10-13 — Passe de revue 1
- Diff soumis : le code et les tests en entier, avec les différences des verdicts et du README entre `construction/v1.0` et `v1.1`, et le rendu de l'export `changements` (sans ses blocs repliés). Les copies intégrales des brouillons, trop volumineuses, ont été vérifiées par script : 225 items, items inchangés identiques octet pour octet, verdicts v1.0 en préfixe exact.
- Verdicts : 35 constats ; high 0, medium 3, low 13, false 9, maybe-false 0, et 10 renvoyés à la relecture d'Anaël ou rejetés.
- **Verification Gap**
  - `[medium]` `[patch]` `lire_items_jeu` : aucun test ne couvre une ligne illisible ni un item sans `id` ; leur suppression ne ferait échouer aucun test. Un export faux pourrait passer.
  - `[low]` `[patch]` `cmd_changements` ignore les erreurs de `derniers_verdicts` : le verdict d'un item retiré manquerait sans alerte (`assembler` et `composition`, eux, les signalent).
  - `[low]` `[patch]` `tests/harness/test_integration_recherche.py:61` recopie `appel_conforme` sans `mot_entier_un_de` ; pointé sur la v1.1, il divergerait du contrôle de production.
- **Blind Hunter**
  - `[medium]` `[patch]` `diff_champs` compare les listes en bloc : pour RD-017, RD-019 et RD-031, l'export montre les trois `appels_attendus` en entier, et Q-042 toute la `provenance`. La relecture en devient difficile.
  - `[low]` `[patch]` Le dernier verdict n'apparaît que pour les items retirés ; les réserves des vérificateurs sur les items modifiés et nouveaux échappent à la relecture.
  - `[medium]` `[patch]` Aucun contrôle n'exige qu'un item modifié ou nouveau ait un verdict ajouté après les lignes v1.0 ; un ancien `accepte` suffirait.
  - `[low]` `[reject]` Règle `version_item` diverse selon les endroits ; liste `MODIFIES_V1_1` écrite à la main — le test vérifie l'équivalence « modifié ⇔ +1 » ; un contrôle dans l'outil ajouterait une logique sans défaut démontré.
  - `[low]` `[reject]` `changements` écrit « référence gelée » sans vérifier le manifeste — la clôture lance `verifier_manifeste` ; garde pour un état non démontré.
  - `[false]` `[reject]` `date_reference` facultative pour un gel `relu` — c'est voulu (matrice : manifeste v1.0 valide). La commande de clôture du README la donne, et `test_jeu_v1.py` l'exige pour v1.1.
  - `[false]` `[reject]` `colonnes` validées seulement dans un helper de test — `verifier_jeu` (gel) exige que les `colonnes` figurent dans `lignes`, et les 5 items RD ont des valeurs numériques.
  - `[low]` `[reject]` Mot vide après normalisation accepté par le schéma ; forme « REI » en majuscules ; logique recopiée dans le helper de test — aucun item concerné ; garde pour un état non démontré.
  - `[false]` `[reject]` RD-017 sans « caen », RD-019 « rome », RD-023 `Année` — les fragments et les colonnes suivent la lettre de G1 et G2. Ce sont des choix d'arbitrage, renvoyés à la relecture d'Anaël.
  - `[low]` `[reject]` L'extrait de Q-070 ne cite pas la phrase des 25 jours — le fait est dans le chunk cité, et le vérificateur a accepté l'item ; renvoyé à la relecture d'Anaël.
  - `[low]` `[patch]` `test_items_q.py:99` : un segment d'extrait vide passe toujours (`"" in t`).
  - `[false]` `[reject]` CO-006 `nb_mots` = 138 au lieu de 143 — `core.texte.compter_mots` donne 138.
  - `[low]` `[reject]` Défauts de forme de CR-006 (intervenant deux fois de suite, titres répétés) — sans effet sur les références ; renvoyés à la relecture d'Anaël.
  - `[false]` `[reject]` L'arbitrage F annonçait 5 480 mots, contre 5 159 — les deux chiffres viennent de deux méthodes de comptage. Le README de la v1.1 donne les comptes de `core.texte`.
  - `[low]` `[reject]` Cas manquants dans `test_changements.py` (retiré sans verdict, aucun changement, clé imbriquée ajoutée, message d'erreur) — les branches sont simples ; les cas utiles sont groupés avec le premier constat Verification Gap.
  - `[low]` `[reject]` La date est validée à trois endroits — le comportement est cohérent et les trois couches sont testées.
  - `[low]` `[reject]` Plusieurs titres de niveau 1 dans l'export — c'est cosmétique.
  - `[false]` `[reject]` Rendu en Latin-1 — c'est un artefact du diff de revue ; `eval/revue/changements-v1.0-v1.1.md` est bien en UTF-8.
- **Edge Case Hunter**
  - `[low]` `[reject]` `items.jsonl` non UTF-8 ou illisible → trace — le fichier est produit par `assembler` en UTF-8 ; état non démontré.
  - `[low]` `[reject]` `mkdir` de `eval/revue` hors du `try` — cas improbable ; l'erreur reste bruyante.
  - `[false]` `[reject]` Surrogate isolé → export partiel — les contenus viennent de `json.loads` sur des fichiers UTF-8 valides ; état inatteignable.
  - `[low]` `[patch]` Erreurs de `derniers_verdicts` ignorées — groupé avec le constat Verification Gap correspondant.
  - `[low]` `[reject]` Référence non gelée ou versions inversées — groupé avec le constat Blind Hunter « référence gelée ».
  - `[false]` `[reject]` `Q-001` et `Q-0001` vus comme deux items — `assembler` refuse ces doublons.
  - `[low]` `[reject]` `mot_entier_un_de` vide après normalisation — même constat que celui de Blind Hunter.
  - `[false]` `[reject]` `lignes` à `None` dans le helper RD — le schéma et `verifier_jeu` l'interdisent.
  - `[low]` `[patch]` `test_items_cr_lc.py:153` ne voit ni une clé de premier niveau retirée ni une clé d'`entree` ajoutée ou retirée.
  - `[low]` `[patch]` `test_items_q.py` : segment vide — groupé avec le constat Blind Hunter.
  - `[false]` `[reject]` `KeyError` sur une provenance sans `url` — toute provenance Q avec `chunks` a une `url` (lecteur strict).
  - `[low]` `[patch]` `test_gel.py:804` : « demain » est calculé avant l'appel, donc le test peut échouer s'il franchit minuit.
  - `[false]` `[reject]` Tests verbatim ignorés sans duckdb — les commandes de vérification passent `--with duckdb` ; 0 test ignoré dans `tests/eval_outils`.

## Design Notes

**Pourquoi un export des changements, et non `revue`.** `revue` lit l'échantillon du manifeste, qui n'existe qu'après le gel. Or Anaël doit relire avant `--statut relu`. L'export compare `items.jsonl` v1.0 gelé et v1.1 assemblé, ce qui couvre exactement les items touchés.

**Gel `relu` en clôture différée.** Après la relecture : `eval gel --version v1.1 --statut relu --graine 20261013 --date-reference 2026-10-12`, `revue --version v1.1`, `test_jeu_v1.py`, puis un commit de gel dédié limité à `eval/jeu/v1.1/`, `eval/revue/` et `eval/construction/v1.1/`.

## Verification

**Commands:**
- `uv run --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py composition --version v1.1` -- expected: cibles atteintes, aucune anomalie.
- `SLMSP_EVAL_SOURCES=<dépôt>/data/raw/eval-sources uv run --with duckdb pytest tests/eval_outils -q -rs` -- expected: tout passe, 0 ignoré.
- `uv run pytest -q`, `uv run ruff check`, `uv run ruff format --check` -- expected: verts, ou échecs préexistants hors zone listés.
- `uv run slmsp eval gel --version v1.1 --verifier-seulement` -- expected: 225 items, 0 erreur, code 0.
