---
title: 'Story 17.5 — Onglet « Modèles » : comparatif qualité, coût, vitesse pour les équipes techniques'
type: 'feature'
created: '2026-10-21'
status: review
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

## Auto Run Result — 17.5a (2026-10-21)
- Livré : `src/slmsp/evaluation/fiche_app.py` (et non `src/slmsp/compare/` comme prévu : `tests/test_architecture.py` interdit l'import entre paquets de même couche, or `compare` et `evaluation` sont tous deux en couche 4 et le module réutilise `evaluation.bootstrap`), sous-commande `slmsp compare fiche-app`, `config/comparatif-app.toml`, `tests/compare/test_fiche_app.py` (11 tests), JSON réel `src/slmsp/app/ui/donnees/comparatif-modeles.json`. Qualité vérifiée : 54,5 / 36,8 / 42,7 / 54,6 / 71,6 ; bootstrap apparié (2000 tirages, graine 7) via `bootstrap.comparer`.
- Décisions : (1) ~~une notation `partiel-erreur` est acceptée~~ annulée en revue : la spec est maintenue (notation `complet` seulement), la référence a été re-notée complète (`20261021-095813-minicpm5-2b-47d5`) ; (2) `run_mesure` de MiniCPM5-2B = `20261021-023836-h-ram-f89e` (base, CPU 4 threads, la plus récente) ; la mesure `…030201-h-ram-4e18` est celle de Qwen3-4B, pas retenue ; Qwen3.5-0.8B/2B/4B sans mesure (les mesures de 18/10 existent mais sous une charge différente : 16,7 contre 12,1 tokens/s pour MiniCPM5-2B), à confirmer par Anaël ; (3) ~~cloud : coût = moyenne du `cout_eur` par item sur les appels réussis~~ corrigé en revue : somme des `cout_eur` de tous les appels facturés ÷ items notés × 1000, génération seule (juge exclu) ; (4) commit de l'en-tête = HEAD du dépôt qui contient le TOML.
- Report : la vue (17.5b).

## Revue — 17.5a (2026-10-21, reviewer, avec le second avis)
- MEDIUM corrigé — coût cloud sous-estimé (dernier appel réussi par item, rejeux ignorés) : coût = somme des `cout_eur` de tous les appels facturés ÷ items notés × 1000 (1,16 €/1 000 au lieu de 1,0), libellé « coût réel par demande, relances et appels d'outils compris » ; prix par Mtok conservé.
- MEDIUM corrigé — appariement biaisé par des items non notés d'un seul côté : `bootstrap.comparer(..., exclus=)` et `bootstrap.items_non_notes` ; la fiche compare chaque modèle à la référence par paire en retirant avant tirage les items non notés dans l'un des deux runs, signalé en avertissement ; tests `test_items_exclus_retires_avant_tirage`, `test_appariement_retire_les_items_non_notes`.
- MEDIUM corrigé — run de notation `partiel-erreur` accepté : spec maintenue (`complet` seul), référence remplacée par `20261021-095813-minicpm5-2b-47d5` ; test `test_run_notation_partiel_refuse`.
- LOW corrigé — vitesse cloud : médianes sur tous les appels réussis, champ `vitesse.mention` explicite.
- LOW corrigé — erreurs de forme (journal vide ou non-objet, `cout_eur` nul, `modele_id` absent ou multiple, valeurs de mesure `None`, environnement non-objet, plage de bruit vide) : `ErreurFicheApp` ; tests paramétrés.
- LOW corrigé — note d'emplacement erronée dans « Auto Run Result » ; la règle de couches existe (`tests/test_architecture.py`, `compare` et `evaluation` en couche 4).
- MEDIUM corrigé (chasse aux cas limites) — un `run_mesure` d'un autre modèle était accepté (la mesure de Qwen3-4B a failli être retenue) : refus si `parametres.modele` ne correspond pas à l'`id` ; test.
- LOW corrigé — même run de notation cité pour deux modèles (clé du bruit écrasée) : refus à la validation ; test.
- LOW corrigé — avertissements de paire écrits avec l'identifiant de run : remplacés par le libellé du modèle.
- LOW rejeté — le `commit` de l'en-tête ne signale pas un arbre de travail modifié : le JSON est régénéré après le commit du code, dans un commit séparé, pour que `commit` désigne le code et le TOML qui l'ont produit.

## Auto Run Result — 17.5b (2026-10-21)
- Livré : `src/slmsp/app/pont/modeles.py` (domaine `modeles`, `comparatif_modeles()` lit `ui/donnees/comparatif-modeles.json`, refus `comparatif-indisponible` si absent, illisible ou `schema_version` inattendu), vue `ui/js/vues/modeles.js`, `css/modeles.css`, icône `modeles.svg`, entrée de navigation `MO` « Modèles » (rubrique « Plus » de la colonne, sans zone de saisie). Tests : `tests/app/test_pont_modeles.py` (8), `tests/app/ui/test_vue_modeles.py` (7, marqueur `ui`).
- Décisions : (1) onglet placé dans « Plus » (8 Tâches prioritaires inchangées, pas de raccourci Ctrl+n) ; (2) badges : modèle local actif = `reglages.modeles().actif` égal à l'`id` du JSON ; fournisseur externe = entrée `actif` de `reglages.fournisseurs_externes()` dont le `modele` égale `cout.prix_mtok.modele_id` ; une erreur de ces appels n'empêche pas le tableau ; (3) l'empaquetage embarque déjà tout `app/ui/` (hors `pont-factice.js`), donc `donnees/*.json` sans changement de `assistantsp.spec` ; (4) « Non-régression » (NR) libellé comme dans `config/taches.toml`.
- Report : aucun.

## Revue 17.5b (2026-10-21)
- MEDIUM corrigé — `ecart`, `ic_bas` ou `ic_haut` nuls affichés « 0,0 » ou « NaN » : « non calculé » (idem bruit, vitesse, RAM, coût) ; test `test_valeurs_nulles_jamais_zero_ni_nan`.
- MEDIUM corrigé — une erreur de rendu laissait la vue vide : message `role="alert"` « Comparatif illisible », sans détail ; test `test_rendu_impossible_donne_une_alerte`.
- LOW corrigé — encadré « Comment lire ce tableau » rouvert à chaque rendu : état conservé (variable de fermeture).
- LOW corrigé — sélecteur construit avec l'id du modèle : références d'éléments (`Map`) ; test `test_identifiant_avec_guillemet_garde_le_focus`.
- LOW corrigé — origine de la vitesse non visible : suffixe « (via réseau) » ou « (poste de développement) » et forme longue en `title`.
- LOW corrigé — statut du jeu absent de l'intro : « relu par deux LLM, pas encore par un humain » pour `relu-llm`.
- Chasse aux cas limites : `signe` et `nombre` protégés contre null/NaN ; `jeu_statut` inconnu affiché tel quel ; rien d'autre retenu.
