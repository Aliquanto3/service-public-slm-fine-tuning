---
title: 'Story 12.7 — Vues Question et Recherche de données'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-4-socle-de-l-interface.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/DESIGN.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/EXPERIENCE.md'
warnings: []
deferred: []
---

## Intent

**Problem:** les vues Question et Recherche affichent « non disponible » : l'Agent ne voit ni la réponse au fil de l'eau, ni les sources, ni les jeux de données (FR-1, 3, 5 à 9).

**Approach:** un fil de conversation commun (`composants/conversation.js`) monté par les deux vues. Il consomme les évènements du bus (`evenement:<type>`, format `core.evenements.vers_dict`), construit une réponse par tour (`reponse.js`), remplit le panneau Sources du socle et gère l'écran vide. Tout contenu du modèle entre dans le DOM par `textContent` (jamais `innerHTML`, vérifié par un test statique).

## Boundaries & Constraints

**Always:** CSP `default-src 'self'` ; textes d'interface au vouvoiement ; fixtures factices (`<réponse-factice-1>`) ; tableaux et cartes bâtis depuis `ResultatOutil`, jamais depuis le texte de la réponse.

**Never:** toucher à `index.html`, au socle JS, à `app/pont/` ni aux documents de décision.

## Code Map

- `js/vues/{question,recherche}.js` -- configurent le fil (titre, exemples, `legal-notice` seulement en Question, ligne « Hors ligne » seulement en Recherche).
- `js/composants/conversation.js` -- tours, écran vide, Mode, panneau Sources, régénération, nouvelle conversation, `copier-dernier`.
- `js/composants/reponse.js` -- réponse : texte brut pendant le flux ; à la fin puces, `legal-notice`, « Réponse interrompue », actions Copier et Régénérer ; `[data-reponse]` focalisable (Échap).
- `js/composants/{citations,sources,jeu-donnees,tableau,copie}.js` -- puces `[n]`, `source-card`, `dataset-card`, `data-table` (50 lignes, texte tabulé + ligne de source), copie et `inline-confirmation` 3 s.
- `css/{question,recherche}.css`, `tests/app/ui/test_vues_question_recherche.py` (17 tests Edge), test statique « aucun innerHTML ».
- Tests du socle ajustés : les vues Q et RD ne sont plus « non disponible » ; l'ordre de tabulation compte les 3 exemples ; attente de `pret` avant l'envoi dans `test_echec_du_pont_a_l_envoi_conserve_le_texte` (course préexistante, vue une fois en suite complète).

## Acceptance (état)

1. Flux Jeton, Sources, Avertissement, Fin : texte au fil de l'eau, puces « Source n : titre » à la fin seulement, `[n]` sans source laissé en texte, `legal-notice` sous Question seulement. Fait.
2. Puce : panneau Sources avec origine, date de l'Index, extrait dépliable ; Échap ou × ferme ; « Ouvrir » hors ligne copie et affiche « Lien copié… » ; connecté, lien https `target=_blank` (le pont 12.6 l'ouvre dans le navigateur système). Fait.
3. Tableau depuis `ResultatOutil`, 50 lignes, mention d'extrait, « Copier le tableau » (tabulé + source). Fait.
4. `Repli` : `callout-warning` + « Réessayer » (renvoie la dernière question, remplace sur place). Fait.
5. Arrêt : « Réponse interrompue » ; « Régénérer » remplace sur place, seulement sur la dernière réponse. Fait.
6. UX-DR19 : écran Question vide (3 exemples), aucune source (ni puce ni bouton Sources), valeurs hors ligne (ligne d'information RD), erreur en cours de flux (texte reçu conservé, « Cette réponse n'a pas pu être produite »). Fait.

## Auto Run Result

**Décisions prises seul :**
- Les 3 exemples : le premier vient d'EXPERIENCE.md ; les deux autres sont des emplacements `<exemple-à-valider-2>` et `<exemple-à-valider-3>` (D1 : je n'invente pas de texte). Clic = remplit la zone de saisie sans envoyer.
- Titres d'écran vide (« Posez votre question », « Recherchez des données publiques ») et phrases d'intro : proposés par moi.
- Contrat supposé du pont 12.5, à vérifier : `appeler("regenerer")`, `appeler("nouvelle_conversation")`, `appeler("mode")` (lecture tolérante de `hors_ligne` ou `mode`), `appeler("voir_donnees", id)` renvoyant `{resultat}` ; évènement de bus `mode:change` `{hors_ligne}` (à émettre par la vue Mode, 12.9). Tant que rien ne l'émet, le Mode est « hors ligne » et « Voir les données » reste masqué.
- Formes de `ResultatOutil` reconnues : `{content:[{type:"text"}]}` au format texte MCP observé dans les cassettes (`Found n dataset(s)…`, `Row n:`), ou `{colonnes, lignes}` et `{jeux:[…]}`. La date de mise à jour d'une carte n'est affichée que si le résultat la porte (le texte MCP de `search_datasets` n'en a pas).
- Le Retour (pouce) n'est pas posé : hors périmètre ; `.reponse-actions` est prêt à l'accueillir.

## À confirmer

- Anaël : les deux exemples restants de « Question vide » et les titres/intros proposés.
- Anaël / 12.5 : contrat des méthodes `regenerer`, `nouvelle_conversation`, `mode`, `voir_donnees` et du format de `ResultatOutil` pour les données tabulaires.
- 12.9 : émission de `mode:change` ; sinon la vue interroge `appeler("mode")` une seule fois au montage.
- Un « Réessayer » du repli relance la dernière question seule (pas l'historique du fil) ; à ajuster si 12.5 gère le contexte multi-tours.
