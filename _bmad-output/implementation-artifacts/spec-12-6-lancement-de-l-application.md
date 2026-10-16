---
title: 'Story 12.6 — Lancement de l''application'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
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
- Le chemin `NewWindowRequested` (pywebview ouvre l'URI avec `webbrowser.open` sans filtre, `OPEN_EXTERNAL_LINKS_IN_BROWSER`) n'est pas filtré par `GardeNavigation` ; l'interface n'ouvre aucune fenêtre (pas de `target=_blank`, liens via `ouvrir_lien`). À durcir si une vue en ajoute.
- 12.12 : exclure aussi `pont-factice.js` du paquet et inclure `app/ui/` en données PyInstaller.
- Durée de démarrage réelle (< 10 s) et absence de `llama-server` après fermeture/kill : non mesurées ici (GPU occupé, pas de Modèle lancé) ; à mesurer au premier lancement réel.
- Pas de mémorisation de l'état maximisé.
