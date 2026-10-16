---
title: 'Story 12.10 — Paramètres et À propos'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-5-pont-js-api-et-flux-d-evenements.md'
warnings: []
deferred: []
---

## Intent

**Problem:** le domaine `reglages` du pont était un bouchon et la vue `parametres` un module vide (FR-6, FR-11, FR-23).

**Approach:** `PontReglages` (`lire`, `ecrire`, `effacer_historique`, `a_propos`) sur `Stockage` ; la vue `parametres.js` monte un dialogue à trois onglets (Général, Retours, À propos). L'onglet Retours accueille `#ancre-retours` (déplacé, `index.html` intact).

## Contrat

- `reglages.lire` -> `{taille_texte: 100|112|125|137|150, hors_ligne_force}` ; `reglages.ecrire("taille_texte", cran)` (autre clé ou valeur : `reglage-invalide`) ; `reglages.effacer_historique` ; `reglages.a_propos` (détail dans le docstring de `pont/reglages.py`).
- `a_propos` relit à chaque appel `config/liste-blanche.toml`, `config/application.toml` (slug du Modèle, Q13), `config/modeles/<slug>.toml` (SHA-256 **attendu** du GGUF, aucun hachage de 800 Mo), le `MANIFEST.json` de l'Index le plus récent et `ressources/licences-tierces.json`. Toute information absente vaut `null`, affichée « non disponible ».
- Empreinte de l'application (Q4) : lue dans `ressources/empreinte-application.txt` s'il existe (produit au build, 12.12) ; absente aujourd'hui.
- Effacement : bouton, puis 5 s annulables ; passé ce délai, `reglages.effacer_historique`.
- Taille : Ctrl +/−/0 restent ceux du socle (12.4, `localStorage`, persistant car `private_mode=False`). La vue les répercute au pont (`MutationObserver`) une fois montée, et propose A−, A+, 100 %.
- « Rester hors ligne » appelle `mode.forcer_hors_ligne` et suit `evenement:mode`.

## Code Map

- `src/slmsp/app/pont/{reglages,__init__}.py`, `src/slmsp/app/ressources/licences-tierces.json`
- `src/slmsp/app/ui/js/vues/parametres.js`, `src/slmsp/app/ui/css/parametres.css`
- `tests/app/test_pont_reglages.py`, `tests/app/ui/test_vue_parametres.py` (`ui`)

## Auto Run Result

Décisions prises seul :
- Noms de méthodes : ceux du bouchon de 12.5 (`lire`, `ecrire`) et non `reglages()`/`definir_reglage()` de l'énoncé.
- `taille_texte` est stocké comme pourcentage (entier) ; la valeur par défaut « normale » du stockage se lit 100. `REGLAGES_DEFAUT` (12.2) n'est pas modifié.
- Pas de bouton de sauvegarde : chaque changement s'applique et s'enregistre aussitôt.
- Les pastilles de version affichent la version du paquet `slmsp` (`importlib.metadata`), `null` si non installé.
- Mise à jour : aucune (Q6), dite dans « À savoir ».

## À confirmer

Libellés proposés (rédigés par l'agent, non officiels), à valider par Anaël :
- `MENTION_MISE_A_JOUR` : « Cette application ne se met jamais à jour toute seule : une nouvelle version s'installe à la main. » (Q6)
- `MENTION_DONNEES` : « Vos conversations restent sur cet ordinateur. Rien n'est envoyé sans votre action. » (UX-DR22, mention « données personnelles »)
- `HORS_PASSERELLE` (Q1) : WebView2 « peut contacter des serveurs Microsoft pour son propre fonctionnement ». Affirmation à vérifier factuellement avant diffusion.
- Avertissement juridique : reprise de « Ne vaut pas avis juridique. » (texte de la Tâche Q), à compléter si une mention plus longue existe en UX.
- `licences-tierces.json` : liste minimale **provisoire** (llama.cpp MIT, Granite Apache-2.0, BGE-M3 MIT, pywebview BSD-3-Clause, WebView2 Microsoft), rédigée de mémoire, à vérifier ; remplacée au build par 12.12.
- Libellés de l'interface (onglets, « Sites que l'assistant peut contacter », « Ce que l'assistant ne contrôle pas », « Effacer tout l'historique »).
- Les raccourcis Ctrl +/−/0 ne sont répercutés au pont qu'après la première ouverture de Paramètres (la vue est montée à ce moment-là) ; `localStorage` garde la valeur dans tous les cas. Faire monter la vue au démarrage demanderait de toucher `app.js` (12.4).
- Aucun hachage du GGUF installé : on affiche l'empreinte attendue de la configuration, pas celle du fichier présent.
