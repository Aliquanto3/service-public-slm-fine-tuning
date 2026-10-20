---
title: 'eval composer, routage par tâche (story 15.1)'
type: 'feature'
created: '2026-10-20'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred: []
---

## Intent

**Problem:** comparer un routage par tâche (une base ou un adaptateur par tâche) exige de renoter ; or les verdicts existent déjà dans les runs de notation.

**Approach:** `slmsp eval composer --route TACHE=RUN ... --defaut RUN [--marque deja-consulte]` assemble, sans appel, un run `eval-notation` (phase `composition`) lisible tel quel par `eval comparer`.

## Boundaries & Constraints

**Always:** runs sources en lecture seule ; refus avant toute écriture si une source n'est pas `complet`, est déjà composée, ou diffère par jeu et version, liste d'items, SHA de grille, modèle du juge principal, SHA des prompts de Tâche (entrée `taches` du run de génération).

**Never:** aucun appel au juge ; pas de recalcul de score (Score de Tâche, verdicts et contrôles copiés par Tâche).

## Design

`src/slmsp/evaluation/composition.py` : `composer`, `ErreurComposition`. Le run porte `config.route`, `defaut`, `sources`, `marque`, `empreintes_sources`, `generations_par_tache`. `bootstrap.charger_run` lit ce dernier (générations par Tâche depuis le run de génération de chaque source) ; le recalcul de `comparer` redonne `scores.json`. CLI `eval composer` (code 2 sur refus).

## Verification

`tests/evaluation/test_composition.py` (composition, 6 motifs de refus, lecture par `comparer`, marque, sources intactes, CLI).

## Auto Run Result

Décisions : « ok » = statut `complet` ; source déjà composée refusée (simple, réversible) ; `modele_ref` du run composé = celui du run par défaut (à confirmer par Anaël : un run composé n'a pas de modèle unique) ; pas de `relecture.md` dans le run composé. Report : le jeu de verdicts de runs `partiel-erreur` n'est pas composable (levé à la revue, voir ci-dessous).

## Revue

Base : branche sur `ffabac6`, main à `ef4082e` (un commit `docs(run)` d'écart, sans code ; pas de rebase, interdit par les consignes du run).

- HIGH · second avis · corrigé : le Comparatif (`compare/chargement._notations`) déduplique par `scores.run_generation` ; le composé, qui copie celui du défaut, remplaçait la vraie notation du modèle par défaut. Les runs de phase `composition` sont désormais exclus (motif « run composé ») ; test `test_comparatif_et_juges_tiers_ignorent_le_run_compose`.
- MEDIUM · revue · corrigé : `eval juges-tiers --depuis <composé>` aurait pris les générations du seul run par défaut pour toutes les Tâches (appariement faux, appels payants) ; refus explicite d'un run composé dans `juges_tiers.preparer`.
- MEDIUM · décision de l'orchestrateur · corrigé : la Baseline réelle de dev1 (`20261020-165745-minicpm5-2b-afd3`) est `partiel-erreur` ; sources `complet` ou `partiel-erreur` admises, le composé prend le moins bon statut et liste `config.sources_partielles` ; `partiel-budget`, `interrompu` et les autres restent refusés (test `test_source_partiel_erreur_admise_et_consignee`).
- LOW · second avis · corrigé : le contrôle du juge principal compare `modele`, `fournisseur`, `effort`, `mode_appel` ; items, SHA de grille ou juge principal absents sont refusés au lieu de passer à `None == None` (cas paramétrés ajoutés).
- LOW · revue · rejeté : `modele_ref` et `run_generation` du composé copiés du défaut ; sans incidence une fois le Comparatif et les juges tiers fermés aux runs composés, `eval comparer` lisant `generations_par_tache`.
- Complexité : 1 constat LOW · rejeté : `bootstrap._generations_du_run` relit le run de génération de la source pour chaque Tâche (8 lectures de 159 lignes) ; coût négligeable, structure bornée par le jeu.

Essai réel (copie temporaire, rien écrit dans le dépôt) : `--defaut 20261020-165745-minicpm5-2b-afd3 --route CO=20261020-181808-ft-minicpm5-2b-213f --marque deja-consulte` → composé `partiel-erreur` ; `eval comparer` défaut contre composé : CO 72,1 → 82,5 (+10,4, IC [+4,9 ; +16,3], P = 1,000), autres Tâches à +0,0, Qualité 54,5 → 55,8 (+1,3, IC [+0,6 ; +2,0], P = 1,000). M1 seul : Qualité 47,3 (−7,2).
