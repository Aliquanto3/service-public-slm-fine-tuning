---
title: 'Story 17.5 — Onglet « Modèles » : comparatif qualité, coût, vitesse pour les équipes techniques'
type: 'feature'
created: '2026-10-21'
status: ready-for-dev
context:
  - '{project-root}/_bmad-output/planning-artifacts/stories-epic-17-modele-distant.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-2026-10-20.md'
---

## Intention
Demande d'Anaël du 21/10 : un onglet de l'application, pour la démonstration, destiné aux équipes techniques de la collectivité qui arbitrent le modèle cible. Il montre, pour chaque modèle mesuré (local sur le poste ou dans le cloud), la qualité par tâche, le coût et la vitesse, avec les réserves de mesure. Données **figées à la construction** (aucun réseau, aucune lecture de `runs/` par l'application installée).

Découpage : **17.5a** (données : commande de génération du JSON, parallélisable avec 17.4) puis **17.5b** (vue, après la fusion de 17.4, qui touche aussi `index.html`, la navigation et le pont).

## 17.5a — Données (`slmsp compare fiche-app`)
- Sélection déclarative `config/comparatif-app.toml` (`schema_version = 1`), une entrée par modèle : `id`, `libelle`, `emplacement` (`poste` | `cloud`), `run_notation` (dev1), `run_generation` (cloud : coût et vitesse lus dans `appels-distants.jsonl`), `run_mesure` (poste : `runs/measure/<id>/resultat.json`, facultatif), `licence`, `hebergement` (texte court : « Poste de l'Agent », « OpenRouter → DeepInfra (États-Unis) », « Mistral AI (France) »…), `note` facultative.
- Commande `slmsp compare fiche-app [--config config/comparatif-app.toml] --sortie <fichier.json>` : lecture seule des runs, aucun appel. Pour chaque entrée :
  - Qualité et Scores de Tâche (8 tâches) du run de notation, avec le bruit items (demi-largeur de l'IC95, même calcul qu'`eval comparer`) ; écart à une **référence** désignée dans le TOML (MiniCPM5-2B), avec IC95 apparié (réutiliser le code d'`eval comparer`, pas de recalcul divergent).
  - Coût : cloud = coût réel moyen par item × 1000 (« € pour 1 000 demandes », jeu dev1), et prix par million de tokens (entrée / sortie, `config/tarifs.toml`, date de relevé) ; poste = 0 € d'API (champ explicite `cout_api = 0`, avec la mention « coût matériel et énergie non chiffrés »).
  - Vitesse : poste = débit médian (tokens/s), premier token médian, RAM maximale et description machine du run de mesure, ou `null` si absent ; cloud = médianes de `delai_premier_token_ms` et `debit_tokens_s` des appels réussis, mesurées depuis le poste de développement.
  - Métadonnées : jeu, nombre d'items, juge principal, date des runs, identifiants de runs (traçabilité).
- En-tête du JSON : date de génération, commit, avertissements fixes : jeu dev1 (159 items fictifs rédigés pour le projet), juge GLM, bruit ±4,5 à ±5,5 points sur la Qualité, vitesses du poste mesurées sur la machine de développement (pas le PC cible), vitesses cloud dépendantes du réseau.
- Refus clair si un run cité manque, n'est pas `ok`/complet, ou n'est pas sur le même jeu et le même juge que la référence.
- Fichier de sortie destiné à `src/slmsp/app/ui/donnees/comparatif-modeles.json` (embarqué : vérifier `packaging/assistantsp.spec` pour les données de l'UI).
- Tests sur fixtures (runs factices) : agrégats, coût cloud et poste, vitesse absente, refus (run manquant, jeu ou juge différents), JSON conforme à un schéma pydantic.
- Fichiers : `src/slmsp/compare/` (nouveau module), `src/slmsp/cli/compare.py`, `config/comparatif-app.toml`, `tests/compare/`. Ne touche ni `app/` ni `ui/`.

## 17.5b — Vue « Modèles » (après fusion de 17.4)
- Nouvel onglet de navigation « Modèles » (libellé court), vue en lecture seule chargée depuis le JSON embarqué via le pont (une méthode `comparatif_modeles()`), sans réseau.
- Tableau accessible (`<table>` avec en-têtes, tri par colonne au clavier) : Modèle, Où il tourne, Qualité (± bruit) et écart à la référence, Coût (€ / 1 000 demandes ; « 0 € d'API » pour le poste), Vitesse (tokens/s ; premier token), RAM du poste, Licence, Hébergement. Ligne dépliable : les 8 Scores de Tâche avec une barre horizontale simple (CSS, jetons existants), et les identifiants de runs.
- Encadré « Comment lire ce tableau » : avertissements du JSON, rappel que la qualité n'est comparable qu'entre modèles mesurés sur le même jeu et le même juge, et que le choix dépend aussi de la confidentialité (poste) et de la disponibilité (cloud).
- Mise en avant (badge) du modèle actif localement et des fournisseurs externes configurés (17.4), sans autre interaction.
- Tests du pont et de la vue (comme les autres vues) ; aucun réseau.

## Hors story
Mesures elles-mêmes (l'orchestrateur lance les mesures CPU manquantes et choisit les runs du TOML) ; graphiques élaborés ; mise à jour en ligne des données.
