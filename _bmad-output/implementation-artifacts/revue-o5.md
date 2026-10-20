# Revue — story O5 (alignement entraînement / évaluation)

Branche `story/o5-alignement-lc`, mise à jour sur `main` (C1, C2, E1b) avant revue, fusion sans conflit.

| # | Sévérité | Décision | Constat et motif |
|---|---|---|---|
| 1 | medium | corrigé | Consignes de `[alignement.consignes_agent]` trop proches du Jeu (difflib 0,78 avec LC-001, préfixes de LC-001/CR-007/RE-001…). Reformulées en consignes d'outillage neutres (« Tâche : … », « Objectif : … »), ratio max 0,48 ; test `test_consignes_de_config_eloignees_du_jeu_d_evaluation` (ratio < 0,6 et aucun préfixe, v1.0 et v1.1 lus sans copie). Formulations à confirmer par Anaël. |
| 2 | medium | rejeté (mesuré) | Rendement : le pool service-public (33 792 textes uniques, médiane 121 mots) compte 5 253 textes dans [195 ; 361] mots, contre 240 amorces visées (LC 80 × facteur 3). Les 27/240 du seed b335 venaient de l'ancienne borne 300-1500 caractères (≈ 250 mots max) ; la règle alignée élargit cette borne. Aucune concaténation nécessaire. Repères : ± 40 % → 8 123, ± 50 % → 11 184. |
| 3 | medium | corrigé | Filtre neutralisé dans les tests : ajout de `test_filtre_lc_en_mots_actif_au_seed` (executer_seed, filtre actif, textes de 3, 10, 12 et 30 mots ; seuls 10 et 12 tirés, texte au-delà de l'ancienne borne en caractères gardé). |
| 4 | low | corrigé | `regles_alignees` remettait le plancher en caractères à 1 : plancher d'origine conservé (300 pour LC), testé. |
| 5 | low | corrigé | Déterminisme tautologique : test sur deux contextes distincts, et alignement vide = messages de `construire_conversation(..., None)` (rendu pré-O5). |
| 6 | low | corrigé (test) / rejeté (code) | `verifier_amorces` n'a aucun appelant de production ; le test du point 3 montre qu'il faut lui passer l'alignement du seed (sans lui, `ProvenanceInvalide`). Lire l'alignement depuis le manifeste du seed reste à faire quand un appelant réel apparaîtra. |

Tests : `tests/data`, `tests/cli/test_data.py`, `tests/outils` (560 passés) ; ruff, format et contrôle rapide OK.
