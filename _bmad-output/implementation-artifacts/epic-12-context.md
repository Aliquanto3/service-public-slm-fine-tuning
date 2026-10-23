# Epic 12 Context: Application Windows de l'Agent (J4)

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Donner à un Agent d'accueil (sans droits administrateur sur son poste) une application Windows installable en quelques écrans, qui fonctionne d'abord hors ligne et couvre les Tâches prioritaires (Question, Recherche de données, Compte rendu, Langage clair). L'application réutilise le même Harnais que la CLI, affiche en permanence le Mode (connecté/hors ligne), journalise toute Requête sortante, garde l'historique et les Retours de l'Agent uniquement sur son poste, et se désinstalle proprement. C'est le socle sur lequel l'Epic 13 ajoute les Tâches secondaires.

## Stories

- Story 12.1 : Racine de composition partagée et ressources en mode installé
- Story 12.2 : Stockage local de l'application (`app.stockage`)
- Story 12.3 : Anonymisation de l'export des Retours (`app.anonymisation`)
- Story 12.4 : Socle de l'interface (jetons, disposition, navigation, zone de saisie, accessibilité)
- Story 12.5 : Pont `js_api` et flux d'évènements
- Story 12.6 : Lancement de l'application (fenêtre, instance unique, démarrage et arrêt)
- Story 12.7 : Vues Question et Recherche de données
- Story 12.8 : Vues de rédaction Compte rendu et Langage clair
- Story 12.9 : Indicateur de Mode et journal des Requêtes sortantes
- Story 12.10 : Paramètres et « À propos »
- Story 12.11 : Historique et Retours dans l'interface
- Story 12.12 : Exécutable PyInstaller avec Modèle embarqué et Index local
- Story 12.13 : Installateur Inno Setup par utilisateur et désinstallation
- Story 12.14 : Mesures FR-26 avec WebView2 et recette sur PC cible

## Requirements & Constraints

- Dialogue en français au fil de l'eau, avec choix explicite de Tâche (défaut : Question) et « Nouvelle conversation » qui vide le contexte.
- Historique des conversations stocké uniquement dans le profil Windows de l'Agent, sans synchronisation, suppression immédiate (avec un filet « Annuler » de 5 s avant effacement physique).
- L'Agent voit en permanence le Mode courant (connecté / hors ligne / hors ligne choisi) et peut forcer le hors ligne ; ce choix persiste d'un lancement à l'autre. En hors ligne forcé, aucune requête réseau n'est émise, vérifiable par capture réseau.
- Liste blanche des hôtes modifiable par fichier de configuration sans recompilation, affichée dans « À propos » ; toute requête hors liste est bloquée et journalisée (statut `bloquee-liste`).
- Le journal des Requêtes sortantes (30 jours glissants, purge automatique) ne contient jamais le texte collé par l'Agent ; un document témoin à marqueur aléatoire ne doit jamais apparaître dans ce journal pour une Tâche de rédaction.
- Compte rendu : notes/transcription jusqu'à 6000+ mots acceptées ; au-delà de la fenêtre de contexte, découpage puis fusion obligatoires, avec progression affichée.
- Langage clair : passages non simplifiés par prudence signalés à l'Agent.
- Retour (pouce haut/bas + commentaire) stocké en local avec Tâche, question, réponse, sources ; export anonymisé relu par l'Agent avant transmission, sans aucune télémétrie ni Requête sortante liée. Motifs à masquer : NIR, e-mail, téléphone, IBAN, adresse postale, noms de personnes.
- Installation sans droits administrateur, premier lancement fonctionnel hors ligne sans téléchargement complémentaire. Désinstallation sans droits admin, avec choix explicite de conserver ou supprimer historique/Retours.
- « À propos » : versions (application, Modèle embarqué, Index local), Liste blanche effective, licences, avertissement juridique.
- Accessibilité (NFR-7) : clavier intégral, ordre de focus fixe, focus visible, contrastes ≥ 4,5:1, aucune info portée uniquement par le vert/jaune/rouge, échelle de texte 100–150 % mémorisée sans défilement horizontal à 1024×640.
- Mémoire : RAM totale de l'arbre de processus (WebView2 + llama-server compris) ≤ 5 Go, cible 4 Go. Taille installée ≤ 4 Go. Au moins 8 tokens/s sur le PC cible.
- Aucun processus `llama-server` ne doit survivre à la fermeture de l'application ou à un arrêt brutal.

## Technical Decisions

- **Composition partagée.** `assembler`/`Assemblage` vivent dans `slmsp.harness.assemblage` (couche 3), importés à la fois par la CLI et par `app` ; `cli/_assemblage.py` n'est qu'un ré-export. C'est une dérogation consignée (AD-23) à la règle de couches initiale, car `app` et `cli` sont de même couche et ne peuvent pas s'importer entre eux (AD-1).
- **Lecture/écriture en mode installé.** En exécutable gelé (PyInstaller, `sys.frozen`/`sys._MEIPASS`), les ressources (config, binaires, modèles, Index) se lisent depuis le dossier d'installation (`racine_projet()`) ; toute écriture (historique, réglages, journal) va sous `%LOCALAPPDATA%\AssistantSP\` (`racine_ecriture()`), jamais dans `_MEIPASS` ni le dossier d'installation. Les variables `SLMSP_*` gardent toujours la priorité.
- **Frontière de l'application (AD-23).** L'interface pywebview n'appelle le Harnais qu'à travers une classe pont unique exposée en `js_api` (méthodes JSON in/out) ; les évènements sont poussés à l'interface via `evaluate_js`. `slmsp.app.stockage` est le seul propriétaire de l'historique, des Retours, du réglage « rester hors ligne » et de l'implémentation applicative de `JournalRequetes` (même schéma que la CLI, 30 jours glissants), en SQLite sous `%LOCALAPPDATA%\AssistantSP\`. Le journal technique ne contient jamais le texte saisi par l'Agent.
- **Harnais sans état (AD-14).** `AssistantService.repondre(tache, messages, options)` reçoit toute la conversation de l'appelant (qui la conserve) et renvoie un itérateur d'évènements typés : `Jeton`, `AppelOutil`, `ResultatOutil`, `AppelNonConforme`, `Sources`, `Avertissement`, `Progression`, `Repli`, `Fin`, `Erreur`. `config/taches.toml` déclare les Tâches et leurs `outils_autorises` : cette liste est vide pour les Tâches de rédaction (aucun outil, aucun appel réseau possible). Les tableaux de valeurs se rendent toujours depuis `ResultatOutil`, jamais depuis le texte généré.
- **Passerelle réseau (AD-4).** Toute Requête sortante passe par `slmsp.net.client(profil)` ; le profil `assistant` applique la Liste blanche en correspondance exacte de nom d'hôte et journalise systématiquement (statuts `envoyee`/`echouee`/`bloquee-liste`/`bloquee-mode`). Le Mode est porté par `ModePort` : `ModeSonde` (sonde `GET /health` < 3 s, au démarrage, toutes les 5 min, avant chaque appel d'outil) ou `ModeFixe` pour les tests. Le hors ligne forcé est une entrée injectée (CLI ou `app.stockage`) ; en hors ligne, une requête `assistant` est refusée avant toute connexion.
- **Inférence (AD-6) / Processus (AD-27).** Un seul lanceur (`slmsp.inference.serveur`) démarre `llama-server` au tag figé de `config/llamacpp.toml`, dans un Job Object Windows `KILL_ON_JOB_CLOSE` ; les orphelins sont nettoyés au démarrage. Toutes les bases SQLite sont ouvertes en WAL avec `busy_timeout` 30 s.
- **Packaging (Q3).** PyInstaller en `onedir` (jamais `onefile`, qui décompresserait plusieurs Go dans `%TEMP%` à chaque lancement) ; installation dans `%LOCALAPPDATA%\Programs\AssistantSP`, données dans `%LOCALAPPDATA%\AssistantSP\`. Budget taille approximatif : ~2 Go modèle 3B Q4_K_M + 0,6 Go BGE-M3 + 0,6 Go Index + 0,2 Go runtime ≈ 3,4 Go (marge tendue sur le plafond de 4 Go, à mesurer dès le premier build).
- **Installateur (Q2, Q4, Q6).** Inno Setup, `PrivilegesRequired=lowest`, `AppId` stable pour permettre une réinstallation par-dessus sans perte de données (pas de mise à jour auto en v1). Le runtime WebView2 est seulement détecté (pas téléchargé) ; absence → arrêt avec message clair pour la DSI. Application non signée en v1 (empreinte SHA-256 publiée) ; la signature de code reste une décision ultérieure d'Anaël.
- **Résidu réseau WebView2 (Q1, bloquant pour la promesse de confidentialité).** Désactiver au lancement ce qui peut l'être (arguments de navigateur WebView2 : SmartScreen, pings ; CSP stricte `default-src 'self'` ; toute navigation externe refusée, sauf ouverture dans le navigateur système pour une URL `https` de la Liste blanche). Mesurer ensuite par capture réseau réelle (story 12.14) et documenter noir sur blanc dans « À propos » tout résidu constaté.
- **Anonymisation (Q5).** Expressions régulières pour NIR (clé de contrôle), e-mail, téléphone (FR/international), IBAN (modulo 97), adresse postale ; pour les noms de personnes, liste des prénoms INSEE (Licence Ouverte, embarquée) + heuristique sur le mot suivant en majuscule + civilités. Pas de bibliothèque lourde (spaCy, GLiNER, modèle embarqué écartés : dépendances ou non-déterminisme). L'aperçu avant enregistrement reste le filet de sécurité.
- **Modèle embarqué indépendant (Q13).** `config/application.toml` porte le slug du Modèle embarqué (décidé par Anaël après le go/no-go) ; le développement des vues se fait avec un faux LLM, indépendamment du choix final.
- **Fermeture runtime (AD-2).** L'application ne doit jamais tirer `torch`, `transformers`, `anthropic`, `mistralai`, `huggingface_hub`, etc. ; ces dépendances restent dans des extras `uv` séparés (`train`, `judge`, `fetch`…), vérifié par un test AST (`test_architecture.py`).

## UX & Interaction Patterns

- Palette Wavestone : violet `#451DC7` (actions principales, Tâche active, puces de citation, liens, anneau de focus — contraste ~9:1, utilisable en texte) ; violet profond `#250F6B` pour survol/pressé. Vert/jaune/rouge jamais utilisés en texte sur fond clair et jamais seuls porteurs d'une information.
- Disposition trois colonnes, responsive : le panneau Sources pousse la zone centrale à partir de 1280 px, la recouvre en dessous ; pas de défilement horizontal, y compris à 150 % de taille de texte dans une fenêtre 1024×640.
- Zone de saisie : Entrée envoie, Maj+Entrée insère une ligne, Envoyer inactif si vide ; rappel sur les données personnelles affiché dans le champ vide. Raccourcis Ctrl+1 à 4 pour les Tâches prioritaires, Ctrl+/−/0 pour la taille du texte (cinq crans, mémorisés).
- Pendant la préparation de l'Assistant (pont pas encore `pret`), la saisie reste possible mais Envoyer affiche « Préparation… » et reste inactif.
- Réponses : texte au fil de l'eau, puces `[n]` devenant des `citation-chip` (« Source n : titre »), mention « Ne vaut pas avis juridique » uniquement sous les réponses de Tâche Question. Panneau Sources avec origine, date de l'Index, extrait dépliable ; hors ligne, « Ouvrir » copie le lien. Tableaux plafonnés à 50 lignes avec mention d'extrait, copiables en texte tabulé. Un `Repli` affiche un avertissement « données non vérifiées en ligne » avec « Réessayer ». « Arrêter » puis fin interrompue affiche « Réponse interrompue » et bascule sur « Régénérer ».
- Vues de rédaction (Compte rendu, Langage clair, réutilisées par l'Epic 13) : volet générique avec compteur de mots, un seul bouton principal, résultat au fil de l'eau, « Copier » le texte brut final avec confirmation qui s'efface après 3 s ; volets empilés sous 1200 px de largeur. En Langage clair, les passages non simplifiés sont surlignés avec infobulle accessible (clavier et survol) ; sans section reconnue, le texte s'affiche normalement, sans erreur.
- Pastille de Mode : « Connecté » / « Hors ligne » / « Hors ligne (choisi) », une seule annonce lecteur d'écran par changement ; menu pour « Rester hors ligne ». Journal des Requêtes : Heure, Hôte, Termes, Statut, état vide explicite, « Effacer le journal ».
- Suppressions (conversation, historique complet) : pas de confirmation bloquante mais un « Annuler » disponible 5 s avant effacement définitif (y compris `VACUUM` pour l'effacement complet).
- « À propos » en dialogue à onglets : versions, date de l'Index, Liste blanche effective, licences, avertissement juridique ; l'onglet Retours héberge l'export anonymisé avec aperçu avant tout enregistrement.

## Cross-Story Dependencies

- 12.1 (composition partagée, chemins installés) est le préalable technique de la quasi-totalité de l'epic ; 12.5 et 12.6 en dépendent directement.
- 12.2 (stockage) fournit l'implémentation de `JournalRequetes` injectée dans `assembler` (12.1) et le support de lecture des Retours utilisé par 12.3 et 12.11.
- 12.3 dépend de la décision Q5 ; sans elle, replier sur 12.8 seul (pas d'anonymisation avancée).
- 12.4 fournit le socle d'interface (navigation, jetons, modules de vue vides) dont dépendent 12.7 à 12.11 ; son pont factice permet de développer ces vues sans attendre le pont réel 12.5.
- 12.5 (pont réel) est nécessaire pour l'essai bout en bout de 12.6 à 12.11, même si les vues peuvent être développées avec le pont factice de 12.4.
- 12.9 doit précéder l'onglet « Rester hors ligne » de 12.10 (réutilisation du composant Mode).
- 12.10 doit précéder l'onglet Retours de 12.11 (le composant s'y monte).
- 12.12 (exécutable) dépend de 12.1, 12.6 et de la décision Q13 (Modèle embarqué) pour le build final ; 12.13 (installateur) dépend de 12.12 ; 12.14 (mesures sur PC cible) dépend de 12.13 et d'un accès physique au PC cible.
- Le module `src/slmsp/app/pont/redaction_outils.py`, déclaré d'avance par 12.5, est le point d'extension utilisé par les Tâches secondaires de l'Epic 13 (ex. 13.1) ; `vues/redaction.js` de 12.8 est réutilisé par plusieurs vues de l'Epic 13 sans modification.
- `config/application.toml` porte une clé partagée `langues_traduction`, déclarée par 12.1 mais consommée par la story 13.4 de l'Epic 13.
