---
title: 'Story 12.6 — Lancement de l''application'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 1
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-4-socle-de-l-interface.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-5-pont-js-api-et-flux-d-evenements.md'
warnings: []
deferred: []
---

## Intent

`python -m slmsp.app` et `assistantsp` ouvrent l'Assistant : instance unique, fenêtre à la taille mémorisée affichée sans attendre, assemblage en fil de fond puis signal `pret`, arrêt des serveurs à la fermeture (UX-DR23, FR-21, NFR-1, Q1).

## Réalisé

- `app/principal.py` :
  - `InstanceUnique` (mutex nommé `ctypes`, port `ApiInstance` ; la seconde instance restaure la première puis sort avec 0) ;
  - `geometrie_initiale` (minimum 1 024 × 640, position abandonnée si plus sur un écran, taille bornée à l'écran), mémorisée à `closing` dans le réglage `fenetre` (`x`, `y`, `largeur`, `hauteur`) ;
  - `PontDiffere` : `js_api` exposé dès la création de la fenêtre, refuse `preparation` jusqu'à l'assemblage ;
  - `Demarrage` : `assembler(base:<slug>, hors_ligne=<hors_ligne_force>, journal=JournalApplication)` dans un fil (donc `ModeSonde` forcé hors ligne avant toute sonde), `Pont(service, Window)`, puis `signaler_pret()` quand `loaded` a eu lieu et que `window.pywebview.api` et `slmspRecevoir` existent (sondés par `evaluate_js`). Échec d'assemblage : erreur générique poussée. Sortie : sortie du `with assembler` (JobObject des `ServeurLlama`) ;
  - `Chrono` : durées fenêtre et `pret` consignées au logger `slmsp.app` (cible < 10 s).
- Q1 : interface servie en HTTP local (`http_server=True`, `private_mode=False`, `storage_path` sous le dossier de données) depuis une copie temporaire sans `pont-factice.js` ; `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` coupe SmartScreen, pings, mises à jour de composants, sync ; `GardeNavigation` branchée sur `NavigationStarting` : annule tout sauf l'origine locale exacte, ouvre dans le navigateur système les `https` de la Liste blanche.
- `app/__main__.py`, `[project.scripts] assistantsp`.
- Hors zone, strict nécessaire (demande de l'orchestrateur après 12.7) : `Pont.ouvrir_lien` implémenté (`ouvreur` injectable, défaut `webbrowser.open` ; `ouverture-impossible` si échec), test `test_pont.py` mis à jour.

## Vérifications

- Tests `tests/app/test_principal.py` avec ports factices. Un test `lent` ouvre une vraie fenêtre pywebview cachée : l'interface est servie en `http://127.0.0.1`, les modules ES se chargent (`slmspRecevoir` défini), et `load_url("https://exemple.invalid/")` est annulée (la page reste locale).
- `evaluate_js` sous le verrou d'envoi : `arreter()` reste borné (test avec `evaluate_js` lent). Les appels du pont viennent de fils pywebview, jamais du fil d'interface : pas d'interblocage constaté. Risque résiduel : un `evaluate_js` bloqué retarde `arreter` d'autant.

## Décisions prises seul

- Navigation : comparaison stricte du `netloc` d'origine (`localhost` refusé si l'origine est `127.0.0.1`).
- `private_mode=False` pour que `localStorage` (préférences d'interface, 12.4) survive.
- Les arguments WebView2 passent par la variable d'environnement : pywebview 6.2.1 fixe `AdditionalBrowserArguments` sans option ; WebView2 y ajoute la variable.
- Copie temporaire de l'interface à chaque lancement plutôt que filtrer le serveur.

## À confirmer par Anaël / reports

- Les noms de commutateurs WebView2 (`msSmartScreenProtection`, `--no-pings`…) sont à valider par la capture réseau de 12.14 ; ils ne sont pas vérifiables sans trace.
- ~~`NewWindowRequested` non filtré~~ : corrigé en revue (voir ci-dessous).
- 12.12 : exclure aussi `pont-factice.js` du paquet et inclure `app/ui/` en données PyInstaller.
- Durée de démarrage réelle (< 10 s) et absence de `llama-server` après fermeture/kill : non mesurées ici (GPU occupé, pas de Modèle lancé) ; à mesurer au premier lancement réel.
- Pas de mémorisation de l'état maximisé.

## Revue

Revue Opus (2026-10-16), avec la liste du second avis (Haiku). Contournement de la Liste blanche prouvé sur une vraie WebView2 : sans correctif, `window.open('https://exemple.invalid/…')` partait dans `webbrowser.open`.

- **high** (second avis n° 2, confirmé) — `NewWindowRequested` contournait la garde (`webbrowser.open` sans filtre). **Corrigé** : `durcir_webview` pose `OPEN_EXTERNAL_LINKS_IN_BROWSER = False` (pywebview fait alors `load_url`, donc `NavigationStarting`, donc la garde) et `ALLOW_FILE_URLS = False`. Tests factice et réel (`window.open`).
- **medium** (n° 1, confirmé) — garde non branchée : l'application continuait. **Corrigé** : fenêtre détruite, message sur stderr et au logger, code 1. Test.
- **medium** (n° 3, confirmé) — tests sans le câblage de `lancer()`. **Corrigé** : test non `lent` du câblage (garde abonnée, nouvelles fenêtres, `private_mode=False`, `storage_path`) ; le test `lent` passe désormais par `lancer()` avec le vrai pywebview (fenêtre cachée, assemblage factice).
- **low** (n° 4) — `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` transmise à `llama-server`. **Corrigé** : `env_sous_processus` retire les `WEBVIEW2_*`. Test.
- **low** (n° 5) — écrans illisibles : position mémorisée gardée telle quelle. **Corrigé** : position abandonnée (fenêtre centrée). Test.
- **low** (n° 6) — mutex relâché alors que l'assemblage tourne encore. **Corrigé** : `arreter()` rend False si le fil vit encore ; le mutex est alors gardé jusqu'à la fin du processus, qui emporte les serveurs (JobObject). Test.
- **low** (n° 7) — `FindWindowW("Assistant")` et course au démarrage. **Rejeté** : `CreateMutexW` est atomique (jamais deux instances) ; au pire la seconde instance sort sans restaurer une première pas encore affichée, ou passe au premier plan une autre fenêtre intitulée « Assistant ». Sans conséquence de sécurité ; un titre propre changerait le libellé UX.
- **low** (n° 8) — `Stockage` sans fermeture. **Rejeté** : chaque opération ouvre et ferme sa connexion (`_connexion`, `closing`) ; rien ne reste ouvert.
- **low** (n° 9) — origine inconnue autorisait tout `http://127.0.0.1`. **Corrigé** : refus (pywebview fixe `real_url` dans `_initialize`, avant la WebView). Test.
- **anticipation 12.9** — l'assemblage recevait déjà `journal=JournalApplication(stockage)` ; le `Pont` reçoit désormais le même `stockage` (paramètre `stockage`, attribut `_stockage`). Test.
- **report** — durée de démarrage réelle et absence de `llama-server` après fermeture : toujours à mesurer au premier lancement avec un Modèle (GPU occupé).
