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

> **À valider par Anaël (D1)** : les exemples 2 et 3 de l'écran « Question vide » restent les
> emplacements `<exemple-à-valider-2>` et `<exemple-à-valider-3>` (`js/vues/question.js`). Aucun
> texte n'est inventé ; ils s'affichent tels quels tant qu'ils ne sont pas fournis.

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
- `css/{question,recherche}.css`, `tests/app/ui/test_vues_question_recherche.py` (tests Edge), test statique « aucun innerHTML ».
- Tests du socle ajustés : les vues Q et RD ne sont plus « non disponible » ; l'ordre de tabulation compte les 3 exemples ; attente de `pret` avant l'envoi dans `test_echec_du_pont_a_l_envoi_conserve_le_texte` (course préexistante, vue une fois en suite complète).

## Acceptance (état)

1. Flux Jeton, Sources, Avertissement, Fin : texte au fil de l'eau, puces « Source n : titre » à la fin seulement, `[n]` sans source laissé en texte, `legal-notice` sous Question seulement. Fait.
2. Puce : panneau Sources avec origine, date de l'Index, extrait dépliable ; Échap ou × ferme ; « Ouvrir » hors ligne copie et affiche « Lien copié… » ; connecté, bouton (jamais un lien) qui appelle `ouvrir_lien(url)` du pont (Liste blanche, ouverture réelle en 12.6 ; d'ici là le lien est copié). Fait.
3. Tableau depuis `ResultatOutil`, 50 lignes, mention d'extrait, « Copier le tableau » (tabulé + source). Fait. « Voir les données » n'est pas affiché (aucune méthode du pont pour lire les lignes d'un jeu).
4. `Repli` : `callout-warning` + « Réessayer » (renvoie la dernière question, remplace sur place). Fait.
5. Arrêt : « Réponse interrompue » ; « Régénérer » remplace sur place, seulement sur la dernière réponse. Fait.
6. UX-DR19 : écran Question vide (3 exemples), aucune source (ni puce ni bouton Sources), valeurs hors ligne (ligne d'information RD), erreur en cours de flux (texte reçu conservé, « Cette réponse n'a pas pu être produite »). Fait.

## Auto Run Result

**Décisions prises seul :**
- Les 3 exemples : le premier vient d'EXPERIENCE.md ; les deux autres sont des emplacements `<exemple-à-valider-2>` et `<exemple-à-valider-3>` (D1 : je n'invente pas de texte). Clic = remplit la zone de saisie sans envoyer.
- Titres d'écran vide (« Posez votre question », « Recherchez des données publiques ») et phrases d'intro : proposés par moi.
- Contrat du pont 12.5 (aligné en revue) : Régénérer et Réessayer renvoient la question du dernier tour par `envoyer` (pas `regenerer`, qui rejoue le dernier envoi du pont, éventuellement d'une autre Tâche) ; « Nouvelle conversation » appelle `arreter` si un flux est en cours, puis `nouvelle_conversation` ; Mode initial par `appeler("mode.etat")` (`{ok, mode: "connecte"|"hors_ligne"}`, bouchon jusqu'à 12.9) ; évènement de bus `mode:change` `{hors_ligne}` (à émettre par la vue Mode, 12.9). Tant que rien ne répond, le Mode est « hors ligne ».
- Formes de `ResultatOutil` reconnues : `{content:[{type:"text"}]}` au format texte MCP observé dans les cassettes (`Found n dataset(s)…`, `Row n:`), ou `{colonnes, lignes}` et `{jeux:[…]}`. La date de mise à jour d'une carte n'est affichée que si le résultat la porte (le texte MCP de `search_datasets` n'en a pas).
- Le Retour (pouce) n'est pas posé : hors périmètre ; `.reponse-actions` est prêt à l'accueillir.

## À confirmer

- Anaël : les deux exemples restants de « Question vide » et les titres/intros proposés.
- Anaël : format de `ResultatOutil` pour les données tabulaires ; besoin d'un « Voir les données » (méthode de pont à créer, appel MCP en Mode connecté).
- 12.9 : implémenter `mode.etat` et émettre `mode:change` ; la vue lit `mode.etat` une seule fois au montage.
- 12.6 : implémenter `Pont.ouvrir_lien` (le contrôle de Liste blanche est déjà fait) et intercepter toute navigation de la WebView.
- Un « Réessayer » du repli relance la dernière question seule (pas l'historique du fil) ; à ajuster si 12.5 gère le contexte multi-tours.

## Revue

Revue Opus du 2026-10-16, après rebase sur main (pont 12.5 fusionné), avec la liste du second avis (Haiku).

- high, second avis (1) : Régénérer, Réessayer et l'envoi émettaient `generation:debut` puis ignoraient un refus `{ok:false}` du pont : état figé, « Arrêter » bloqué. Corrigé : `conversation.js` exige `ok` (rejet sinon) et le refus passe par `generation:erreur` (état rétabli, bandeau d'erreur, texte restauré) ; la réponse à régénérer n'est vidée qu'au premier évènement, un refus la laisse intacte. Tests : refus rejeté et refus `ok:false` sur Régénérer, refus à l'envoi.
- high, second avis (2) : Mode lu par `appeler("mode")`, absent du pont. Corrigé : `appeler("mode.etat")`, `lireMode` strict (`connecte`/`hors_ligne`, refus = inconnu). Tests : les deux modes, et `non-implementee` reste hors ligne.
- medium, second avis (3) : `voir_donnees` inexistant. Choix : « Voir les données » masqué (bouton et code retirés) ; une méthode « résultats déjà présents » ne répondrait pas au besoin (lire les lignes d'un jeu demande un appel MCP). Le critère 3 reste couvert par les `ResultatOutil` tabulaires (test 60 lignes plafonné à 50, copie tabulée).
- medium, second avis (4) : Réessayer d'une ancienne réponse remplaçait la dernière. Corrigé : Réessayer et Régénérer seulement sur la dernière réponse, qui rejoue sa propre question. Test.
- medium, second avis (5) : flux tardif après « Nouvelle conversation » ou changement de Tâche. Corrigé : un évènement n'est reçu que par la vue qui a lancé la génération (plus de tour créé sans `generation:debut`) ; « Nouvelle conversation » arrête le flux puis appelle `nouvelle_conversation`. Le pont 12.5 n'expose pas d'identifiant de génération ; il garantit qu'aucun évènement ne suit le `Fin(interrompue)` d'`arreter`. Tests : nouvelle conversation pendant le flux, flux de Q pendant que RD est active.
- medium, second avis (6) : pas d'annonce de la réponse. Corrigé : à la fin, la réponse est lue par la région `aria-live="polite"` du socle (`#annonces`), jamais jeton par jeton (EXPERIENCE.md). Test.
- medium, second avis (7) : « Ouvrir » connecté était un `<a target="_blank">`. Corrigé : bouton (ni clic milieu, ni Ctrl+clic, ni navigation) qui appelle `Pont.ouvrir_lien(url)` ; ajouté au pont : https, port 443, sans identifiants, hôte exact de la Liste blanche, sinon `lien-refuse` ; ouverture réelle reportée à 12.6 (`non-implementee`, l'interface copie alors le lien). Tests Python (refus, acceptation) et Edge.
- medium, revue : `pont.regenerer()` rejoue le dernier envoi du pont, toutes Tâches confondues (Régénérer en Q après un envoi en RD aurait affiché la réponse RD dans Q). Corrigé par le passage à `envoyer` (constat 1).
- medium, revue : un flux de Q pendant que RD est active créait un tour dans RD (auto-création de tour). Corrigé avec le constat 5.
- low, second avis (8) : `test_socle.py` vérifie l'écran vide de Q et RD et l'ordre de tabulation par identifiants (`exemple-Q-1` à `-3`). Corrigé.
- low, second avis (9) : emplacements `<exemple-à-valider-2/3>` gardés (D1), note visible en tête de spec.
- low, revue : `test_arreter_pendant_la_generation` (12.4) échouait par intermittence (pas d'attente de `pret`). Corrigé (attente ajoutée).
- Reporté : ouverture effective des liens et blocage de la navigation de la WebView dans la vraie fenêtre (12.6) ; à vérifier : clic sur « Ouvrir » connecté ouvre le navigateur système, Ctrl+clic et clic milieu n'ouvrent rien dans l'application.
