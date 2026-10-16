---
title: 'Story 12.4 — Socle de l''interface (jetons, disposition, navigation, zone de saisie, accessibilité)'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/DESIGN.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/EXPERIENCE.md'
warnings: []
deferred: []
---

## Intent

**Problem:** l'Agent n'a pas de fenêtre : ni disposition, ni navigation entre Tâches, ni zone de saisie, ni garantie d'accessibilité (FR-2, NFR-7).

**Approach:** interface 100 % locale sous `src/slmsp/app/ui/`, sans framework ni build (modules ES natifs, CSP `default-src 'self'`). Un socle (`js/socle/`) porte le routeur, le client du pont, le bus, les raccourcis, les annonces et la zone de saisie. Chaque vue est un module `monter(conteneur, pont, contexte)` vide (« non disponible »), déclaré d'avance avec son CSS (convention §3 des Epics 12 et 13).

## Boundaries & Constraints

**Always:** tailles de texte en rem (échelle 100 à 150 % sur la racine) ; vert, jaune, rouge et gris jamais en `color` ; aucune ressource ni police externe ; textes de l'interface au vouvoiement, sans jargon d'IA ; données de test factices (`<réponse-factice-1>`).

**Never:** toucher à `index.html` depuis une story de vue ; ajouter un évènement parallèle à `core.evenements` (seul `{type: "pret"}` est propre à l'interface) ; code Python dans `src/` (aucun fichier `.py` ajouté) ; téléchargement de navigateur.

## Code Map

- `ui/index.html` -- squelette (colonne, barre, zone centrale, Sources, dialogue Paramètres, région `aria-live`), CSP, liens vers les 14 feuilles de style.
- `ui/css/{jetons,socle}.css` -- jetons de DESIGN.md ; disposition grille ; `<1 280 px` les Sources recouvrent ; `.volets` s'empilent sous 1 200 px ; `prefers-reduced-motion`.
- `ui/js/socle/` -- `app.js` (Tâches, routeur, états globaux), `composer.js` (zone de saisie), `clavier.js` (UX-DR20), `annonces.js` (file `aria-live`), `bus.js`, `pont-client.js` (file d'évènements `window.slmspRecevoir`, mémoire locale), `pont-factice.js` (`?pont=factice`).
- `ui/js/vues/*.js`, `ui/css/<vue>.css` -- 12 modules vides ; `redaction` sert Compte rendu et Langage clair.
- `tests/app/ui/test_socle_statique.py` (contrastes, CSP, déclarations) ; `tests/app/ui/test_socle.py` (marqué `ui`, Edge).
- `pyproject.toml` -- marqueur `ui` exclu par défaut ; `playwright==1.64.0` dans le groupe `dev` (sans `playwright install`).

## Acceptance (état)

1. 1 024 × 640 à 150 % : aucun débordement horizontal sur les 8 Tâches, Sources ouvertes comprises ; Sources poussent à 1 280 px, recouvrent à 1 100 px (testé).
2. Ordre de tabulation, focus violet 2 px, libellés ; Ctrl+1 à 4 et annonce de la Tâche active (testé).
3. Entrée envoie, Maj+Entrée ligne, Envoyer inactif si vide, rappel données personnelles en placeholder, « Arrêter » en génération (testé).
4. Couples texte/fond ≥ 4,5:1 sur les jetons ; aucune couleur d'état en texte (testé, sans navigateur).
5. Aucune requête hors du serveur local, CSP effective (un `fetch` externe est refusé) (testé).
6. Sans `pret` : bandeau « Préparation de l'assistant… », saisie possible, bouton « Préparation… » inactif (testé).

## Auto Run Result

Décisions prises seul (réversibles) :
- Tâches reprises de `config/taches.toml` : Q, RD, CR, LC (Ctrl+1 à 4) puis CO, RE, CT, TR sous « Plus ». Une section de vue par Tâche (le module `redaction` est monté deux fois, avec `contexte.tache`).
- Vues transverses ancrées par le socle : `mode` (barre), `historique` (colonne), `verification` (sous les vues), `parametres` et `retours` (dialogue Paramètres, montés à la première ouverture).
- La zone de saisie du socle sert les Tâches de dialogue (Q, RD). Elle appelle `pont.envoyer(tache, [{role: "user", content}], {})` et `pont.arreter()` (contrat de 12.5) et émet `envoi` sur le bus.
- Le brouillon de saisie est conservé par Tâche ; « taille du texte », « Plus » et « bienvenue vue » sont mémorisés en `localStorage` (par `memoire` de `pont-client.js`), faute de contrat de réglages avant 12.2/12.5.
- Le pont réel n'est attendu qu'à l'évènement `pywebviewready` ; le pont factice n'est actif qu'avec `?pont=factice`.
- Les annonces passent par une file (aucun message écrasé) ; un essai sans file perdait la Tâche active si `pret` arrivait en même temps.
- Les tests `ui` attendent par `wait_for_function` en mode `polling=50` : le mode par défaut (rAF) bloque quand Edge juge la page masquée. Expressions JS sous forme de fonctions (la CSP interdit `eval`).
- `uv.lock` et `pyproject.toml` modifiés pour `playwright` (dépendance de dev épinglée).

**À confirmer par Anaël :**
- l'évènement `{type: "pret"}` poussé par Python via `evaluate_js("window.slmspRecevoir(...)")`, et la liste de méthodes du pont (`envoyer`, `arreter`, `appeler`) : à aligner sur 12.5 ;
- le service des fichiers : les icônes sont des masques CSS (`mask-image`), qui exigent un schéma `http(s)` (pywebview `http_server=True`) et non `file://` : à vérifier en 12.6 ;
- la persistance des préférences d'interface dans `localStorage` de WebView2 plutôt que dans `app.stockage` (12.2) ;
- polices Inter et Manrope non embarquées (aucun fichier fourni, licence OFL) : repli sur Aptos puis Segoe UI ; logo Wavestone non intégré (nom de produit à trancher) ;
- la dépendance de dev `playwright==1.64.0` (roue Python, pilote Node inclus, aucun navigateur) et le marqueur `ui` ajouté au `-m` par défaut de pytest ;
- `Échap` arrête la génération seulement si le focus est dans un élément `[data-reponse]` (à poser par la vue Question).

**Reports :** écran « Question vide » et ses trois exemples (UX-DR19), erreurs propres à chaque vue, panneau Sources lui-même (le socle n'en fournit que le conteneur et les évènements `sources:ouvrir`, `sources:fermer`, `sources:disponibles`).
