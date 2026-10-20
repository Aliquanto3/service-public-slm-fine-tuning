---
title: 'O5 - Alignement entraînement / évaluation (consigne d''Agent, longueur des sources)'
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

**Problème :** LC reste à 0 (fidélité) dans tous les fine-tunings. À l'évaluation, l'entrée porte une consigne d'Agent (« Consigne : … / Texte : … ») et des textes 2 à 3 fois plus longs ; à l'entraînement le message user n'a que « Texte : … ».

**Approche :** (1) un rapport de comparaison (gabarit, longueurs) ; (2) la consigne rendue à l'entraînement par la même fonction (`construire_messages`), tirée par graine dans des formulations génériques de `config/donnees.toml` ; (3) un filtre en mots des sources LC au seed, sans troncature.

## Constat (rapport `rapport-alignement-o5.md`, v14 contre v1.1, médianes en mots d'entrée hors consigne)

| Tâche | Éval. | Entr. v14 | Rapport | Gabarit manquant à l'entraînement |
|---|---|---|---|---|
| LC | 278 | 108 | 2,6 | Consigne |
| CO | 153 | 84 | 1,8 | Consigne |
| RE | 714 | 202 | 3,5 | Consigne (le gabarit v14 porte « Longueur demandée ») |
| CR | 1205 | 1544 | 0,8 | Consigne |
| CT | 64 | 135 | 0,5 | Consigne |

Q et RD ne sont pas comparables telle quelle (passages et outils côté entraînement).

## Réalisation

- `outils/comparer_entrainement_evaluation.py` : lecture seule, aucune consigne ni aucun item du Jeu recopié ; statistiques seulement.
- `config/donnees.toml` `[alignement]` : `consignes_agent` par Tâche (LC 4 variantes, CR, CT, RE, CO 3 chacune), `graine`, `longueur_sources_lc` (`mediane_mots = 278`, `tolerance = 0.3`). Modèle `AlignementDonnees` dans `data/config.py` (Tâches admises : CR, LC, CT, RE, CO ; défaut vide, rien n'est aligné).
- `data/build.py` : `consigne_agent` (graine + session_id), `construire_conversation(..., alignement)` ajoute la clé `consigne` à l'entrée objet, donc même rendu qu'à l'évaluation. `ContexteBuild.alignement` vient de la config ; `validate` appelle sans alignement (il ne contrôle que les refus). Config consignée dans le run `build`.
- `data/nettoyage.py` : `_source_lc` retire la consigne avant le calcul de fidélité.
- `data/seed.py` : `RegleAmorce.mots_min/mots_max`, `regles_alignees` (LC/texte : bornes en mots, bornes en caractères élargies), appliquée par `lancer_seed` et par `verifier_amorces(alignement=...)`. Texte hors bornes écarté, jamais coupé.

## Reports et points à confirmer par Anaël

- **Consignes** : formulations écrites par l'outillage (instructions neutres, aucune réponse, D1 respecté) ; la consigne n'est pas vue par le générateur (O6/generate inchangés) : elle n'entre que dans le message user de l'exemple. Les réponses ont été produites sans elle ; à confirmer par Anaël pour CR/CT/RE/CO (étendus par la même option, retirables en vidant la liste).
- **Rendement du filtre LC** : l'entrée 195-361 mots (± 30 % de 278) peut être rare dans les chunks service-public (v14 : médiane 108 mots) ; vérifier `comptes.json` du seed (`manque`). Si trop rare, élargir la tolérance ou concaténer des chunks voisins (report, hors périmètre).
- RE : la longueur d'entrée v14 (202) reste 3,5 fois sous l'évaluation ; seule la consigne est alignée.
- Rejeu nécessaire : seed LC, generate (O6), build v17 pour que les changements atteignent les données.

## Auto Run Result

- Tests ciblés : `tests/data/test_alignement_o5.py` (10), `tests/data`, `tests/outils`, `tests/cli/test_data.py`, architecture.

## Revue

Détail : `revue-o5.md`.
- medium, corrigé : consignes trop proches du Jeu (0,78 avec LC-001, préfixes) ; reformulées (max 0,48), test anti-ressemblance.
- medium, rejeté : rendement LC suffisant, 5 253 textes du pool dans [195 ; 361] mots pour 240 visés.
- medium, corrigé : test du chemin réel du filtre en mots au seed.
- low, corrigé : plancher en caractères LC conservé.
- low, corrigé : déterminisme testé sur deux contextes, alignement vide = rendu pré-O5.
- low, rejeté (code) : `verifier_amorces` sans appelant de production ; l'alignement est à lui passer (testé).
