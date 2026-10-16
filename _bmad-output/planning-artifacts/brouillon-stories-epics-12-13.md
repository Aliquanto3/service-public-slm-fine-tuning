---
statut: brouillon, à valider par Anaël
date: 2026-10-16
portee: découpage en stories des Epics 12 (J4) et 13 (J5)
sources:
  - _bmad-output/planning-artifacts/epics.md (Epics 12 et 13, UX-DR1 à UX-DR24, conventions communes)
  - _bmad-output/planning-artifacts/prds/prd-service-public-slm-fine-tuning-2026-10-11/prd.md (FR-1 à FR-23, FR-37, FR-38, NFR-1, NFR-5 à NFR-7, §9.3)
  - _bmad-output/planning-artifacts/architecture/architecture-service-public-slm-fine-tuning-2026-10-12/ARCHITECTURE-SPINE.md (AD-1, AD-2, AD-4, AD-6, AD-14, AD-23, Deferred)
  - _bmad-output/planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/{DESIGN,EXPERIENCE}.md
  - _bmad-output/planning-artifacts/decisions.md (D1, pile J4 décidée le 2026-10-12)
  - code : harness/service.py, cli/_assemblage.py, cli/ask.py, harness/modes.py, net/journal.py, core/evenements.py, inference/, index/, tests/test_architecture.py
---

# Brouillon : stories des Epics 12 et 13

> **Statut : brouillon, à valider.** Rien ici n'est encore reporté dans `epics.md` ni dans `sprint-status.yaml`. Les questions de la section 2 doivent être tranchées avant le développement ; celles marquées **bloquante** conditionnent une ou plusieurs stories.

## 0. Synthèse

| Epic | Stories | Tailles | Stories bloquées par une question |
|---|---|---|---|
| 12 — Application Windows (J4) | 14 (12.1 à 12.14) | 11 M, 3 L | 12.3 (Q5), 12.12 et 12.13 (Q2, Q3, Q4), 12.14 (Q1) |
| 13 — Tâches secondaires, vérification en ligne, publication (J5) | 8 (13.1 à 13.8) | 4 S, 4 M | 13.4 (Q9), 13.5 et 13.6 (Q7), 13.7 (Q8) |

Le Harnais sait déjà traiter les 8 Tâches et la Traduction (`config/taches.toml`, toutes actives). Il émet un flux d'évènements typés (`core.evenements`) et `ModeSonde` gère le Mode et la sonde. Le journal SQLite existe déjà (`net.journal.JournalSqlite`). Ces deux epics sont donc surtout de la **couche application** (`slmsp.app`, HTML/CSS/JS), du **packaging** et deux ajouts au Harnais : la vérification en ligne (FR-12) et le contrôle des emplacements du Courrier type.

## 1. Garde-fous rappelés (s'appliquent à toutes les stories)

1. **Claude ne génère jamais de Données d'entraînement (D1.1, AD-3).** Les Retours des Agents, l'historique et les textes d'exemple de l'interface (les trois exemples de la vue Question vide, UX-DR19) n'alimentent jamais un jeu d'entraînement. Les tests utilisent des chaînes aléatoires produites dans `tmp_path`. Le document témoin FR-38 porte un marqueur aléatoire. Aucun fichier du dépôt ne contient d'exemple d'entraînement rédigé.
2. **Réseau seulement par la passerelle unique (AD-4).** Toute Requête sortante de l'application passe par `slmsp.net`, profil `assistant`, Liste blanche par correspondance exacte du nom d'hôte, journalisée par `JournalRequetes`. Concrètement :
   - aucun `httpx`/`requests`/`urllib` hors de `slmsp/net/` (ruff `TID251`, déjà en place) ;
   - interface 100 % locale : aucune police, icône ou script chargé depuis Internet, et une CSP `default-src 'self'` ;
   - la WebView2 ne doit naviguer vers aucune URL externe. « Ouvrir » une source passe la main au navigateur du système, hors de l'application (voir Q1) ;
   - en Mode hors ligne forcé, aucune requête, sonde comprise (FR-10).
3. **Le texte collé ne sort jamais (FR-38).** Les Tâches de rédaction n'ont aucun outil (`outils_autorises = []`). La vérification en ligne (FR-12) n'envoie qu'une URL déjà citée, jamais la question ni la réponse.
4. **Publication jamais automatique (FR-37, D1.4).** L'interdiction des fonctions d'upload `huggingface_hub` et de `push_to_hub` (ruff `TID251`) reste en place. La publication est un geste manuel d'Anaël (Q8).
5. **Couches AD-1 et fermeture runtime AD-2.** `app` est en couche 5, au même niveau que `cli` : il ne peut importer ni `cli` ni les pipelines (`evaluation`, `measure`, etc.). Il ne doit tirer aucune bibliothèque lourde (`tests/test_architecture.py`).
6. **Ordre de coupe (PRD §9.3).** Tâches prioritaires avant secondaires. FR-12, puis la Traduction, puis le Courrier type et le Résumé, puis la Correction sont les premiers retirés si la charge dérape.

## 2. Décisions à prendre par Anaël

La pile est déjà décidée (decisions.md, 2026-10-12) : pywebview 6.2.1 sur WebView2, interface HTML/CSS/JS sans framework lourd, PyInstaller, installateur Inno Setup par utilisateur. Les questions portent sur ce qui reste ouvert. **Chaque recommandation est une proposition, pas une décision.**

| # | Question | Bloque | Recommandation |
|---|---|---|---|
| **Q1** | **Réseau de la WebView2 elle-même.** Le runtime WebView2 peut contacter Microsoft (SmartScreen, mises à jour de composants, diagnostics), hors de notre passerelle. Accepte-t-on ce résidu, et comment le vérifie-t-on ? | 12.6, 12.14 (**bloquante** pour la promesse NFR-4) | Désactiver ce qui peut l'être au lancement (arguments de navigateur WebView2 : SmartScreen, pings ; CSP stricte ; navigation externe refusée). Mesurer ensuite par capture réseau en 12.14. Écrire noir sur blanc dans « À propos » ce qui reste éventuellement hors passerelle (runtime Microsoft). |
| **Q2** | **Présence du runtime WebView2 sans droits admin.** Il est livré avec Windows 11 et presque toujours avec Windows 10 à jour, mais ce n'est pas garanti. On ne peut pas le télécharger pendant l'installation (FR-21). | 12.13 | v1 : l'installateur détecte le runtime et, s'il manque, s'arrête avec un message clair pour la DSI. L'embarquer (installateur autonome d'environ 180 Mo, installable par utilisateur) reste une option si un poste cible en est dépourvu. |
| **Q3** | **Packaging.** PyInstaller en `onedir` ou `onefile` ? Taille installée ≤ 4 Go (NFR-6) avec modèle + BGE-M3 + Index. Il faut aussi télécharger Inno Setup (jrsoftware.org, hors de la liste D1.5 de la nuit) sur le poste de dev. | 12.12, 12.13 | `onedir` : `onefile` décompresserait plusieurs Go dans `%TEMP%` à chaque lancement. Installation dans `%LOCALAPPDATA%\Programs\AssistantSP`, données dans `%LOCALAPPDATA%\AssistantSP\` (AD-23). Autoriser le téléchargement d'Inno Setup pour l'outillage. Budget estimé : environ 2 Go pour un 3B Q4_K_M, 0,6 Go pour BGE-M3 Q8_0, 0,6 Go pour l'Index et 0,2 Go pour le runtime, soit environ 3,4 Go. C'est tendu : mesurer dès le premier build. |
| **Q4** | **Signature de code.** Sans signature : avertissement SmartScreen à l'installation, blocage possible par AppLocker/WDAC sur des postes de collectivité, faux positifs antivirus fréquents avec PyInstaller. Une signature coûte de l'argent (certificat, ou Azure Trusted Signing avec vérification d'identité). | 12.13, SM-8 | v1 démonstrateur **non signé**, avec l'empreinte SHA-256 publiée et une note pour la DSI. Décider de la signature au moment d'un déploiement réel. Engagement budgétaire : décision d'Anaël. |
| **Q5** | **Anonymisation FR-20 (Deferred du spine).** Quelle reconnaissance de noms de personnes, sans alourdir le runtime ? | 12.3 (**bloquante**) | Expressions régulières pour NIR, e-mail, téléphone, IBAN et adresse postale. Pour les noms : liste des prénoms INSEE (Licence Ouverte, embarquée) + heuristique sur le mot suivant en majuscule + civilités (M., Mme, Dr). L'aperçu avant enregistrement (UX-DR19) reste le filet. Écartés : spaCy (dépendances lourdes), GLiNER (torch), le modèle embarqué (non déterministe, difficile à tester). |
| **Q6** | **Mise à jour.** Le PRD repousse la mise à jour du modèle et de l'Index à la v2. Une vérification de version en ligne demanderait d'ajouter un hôte à la Liste blanche. | aucune story v1 | Pas de mise à jour automatique en v1. Une nouvelle version s'installe par-dessus l'ancienne : même `AppId` Inno Setup, données conservées. |
| **Q7** | **FR-12 (vérification en ligne) : garder ou couper ?** C'est le premier élément de l'ordre de coupe. Si on le garde : quelle page vérifier ? | 13.5, 13.6 (**bloquante**) | Le garder seulement si J4 est livré dans les temps. Page vérifiée = l'URL de la source de l'Index la mieux classée **déjà citée** dans la réponse (hôte de la Liste blanche). Aucune recherche sur le site, donc aucun terme envoyé : la Requête sortante ne contient qu'une URL. Comparaison faite localement par le Modèle embarqué avec un prompt `VE.md` (consignes seulement, D1.1). |
| **Q8** | **Publication FR-37 : qui appuie sur le bouton ?** Le code n'a pas le droit d'appeler l'upload (AD-4, ruff `TID251`). Que publie-t-on, en public ou en privé ? Publie-t-on aussi le jeu d'entraînement (généré par Mistral) ? | 13.7 (**bloquante**) | `slmsp` prépare **hors ligne** un dossier de publication vérifié (fiche, licence, GGUF, Comparatif, Registre des licences, empreintes) et une procédure. Anaël téléverse lui-même avec la CLI `hf` ou l'interface web : l'interdiction reste intacte dans le code. Dépôt d'abord en privé, puis public après relecture. Le jeu d'entraînement n'est pas publié en v1. **Le Jeu d'évaluation maison n'est jamais publié** (contamination). |
| **Q9** | **Arabe en v1 (PRD, question ouverte 4) ?** | 13.4 | Trancher sur la Baseline FR-27. La story prévoit le RTL de toute façon. Si l'arabe est retiré, il disparaît seulement du sélecteur (une ligne de config). |
| **Q10** | **Racine de composition partagée.** `cli/_assemblage.py` ne peut pas être importé par `app` (même couche, AD-1). | 12.1 | Déplacer `assembler` vers `harness/assemblage.py` (couche 3, qui n'importe que des couches inférieures). `cli/_assemblage.py` devient un ré-export. Petite entorse au spine, qui place la racine de composition dans la CLI : à consigner dans AD-23. |
| **Q11** | **Passages signalés en Langage clair (UX-DR12).** `LC.md` demande de signaler les passages « après le texte réécrit », sans format structuré. Modifier le prompt casserait la comparabilité avec la Baseline. | 12.8 | Ne pas toucher `LC.md`. L'interface extrait la section finale par une règle tolérante. Faute de section reconnue, le texte s'affiche sans surlignage (aucune erreur). |
| **Q12** | **Tests de l'interface JavaScript.** Il n'y a pas de Node sur le poste, et pas de navigateur de test à télécharger. | 12.4 et toutes les vues | Pas d'outillage Node. Les tests Python couvrent le pont, le stockage et l'anonymisation. Pour le JS : Playwright pour Python (PyPI), lancé sur **Edge déjà installé** (`channel="msedge"`, aucun téléchargement de navigateur), contre l'interface statique et un pont factice. Ces tests sont marqués `ui` et exclus par défaut, comme `lent`. |
| **Q13** | **Modèle embarqué.** Choix d'Anaël après go/no-go. | 12.12 à 12.14, 13.7 | Rendre l'application indépendante du modèle : un `config/application.toml` porte le slug. Le développement des vues se fait avec un faux LLM et le candidat le plus petit. |

## 3. Conventions propres à ces epics (pour paralléliser sans conflit)

Elles reprennent l'esprit de D-nuit-A2-6 (« un module par commande, déclaré d'avance ») :

- **Interface : un fichier par vue, déclaré d'avance.** La story 12.4 crée `src/slmsp/app/ui/index.html`, les jetons CSS, le socle JS et **un module vide par vue**, Epic 13 compris : `ui/js/vues/{question,recherche,redaction,correction,resume,courrier,traduction,mode,parametres,historique,retours,verification}.js` et le `ui/css/<vue>.css` correspondant. Chaque module vide affiche « non disponible ». Une story de vue ne modifie ensuite que ses deux fichiers, sans toucher `index.html`.
- **Pont : un module par domaine, déclaré d'avance.** La story 12.5 crée `src/slmsp/app/pont/__init__.py` (la classe `Pont` exposée en `js_api`, qui délègue) et les modules `pont/{conversation,mode,reglages,historique,retours,verification}.py`. Ceux des autres stories y sont des bouchons qui lèvent `NonImplementee`. Le contrat JSON de chaque méthode est écrit dans le docstring dès 12.5.
- **Évènements.** L'interface consomme `core.evenements.vers_dict` tel quel. Aucun format parallèle. Seule la story 13.5 ajoute un type d'évènement.
- **Stockage.** `app.stockage` est le seul propriétaire de l'historique, des Retours, des réglages et du journal J4 (AD-23). Aucune autre story n'ouvre la base SQLite de l'application.
- **Tests.** Python sous `tests/app/` (un fichier par module). Tests d'interface sous `tests/app/ui/`, marqués `ui`. Un pont factice JS (`ui/js/socle/pont-factice.js`) permet d'ouvrir l'interface dans Edge sans Python.

---

## 4. Epic 12 : Application Windows de l'Agent (J4)

### Story 12.1 : Racine de composition partagée et ressources en mode installé

En tant qu'Anaël,
je veux que la CLI et l'application assemblent l'Assistant par la même fonction, et que les chemins de configuration, de binaires, de modèles et d'Index se résolvent aussi dans un exécutable installé,
afin que l'application ne duplique pas la composition et fonctionne hors du dépôt.

**Couvre :** AD-1, AD-6, AD-14, AD-23 ; FR-21 (préalable) ; Q10, Q13.

**Fichiers et modules :**
- `src/slmsp/harness/assemblage.py` (nouveau : `assembler`, `Assemblage`, `OutilsParesseux`, `plafonner_threads`, `slug_modele` déplacés tels quels)
- `src/slmsp/cli/_assemblage.py` (devient un ré-export, pour compatibilité), `src/slmsp/cli/ask.py` (import mis à jour seulement)
- `src/slmsp/core/config.py` (`racine_projet()` : détection de l'exécutable gelé `sys.frozen` / `sys._MEIPASS`, et variable `SLMSP_RACINE`)
- `config/application.toml` + `src/slmsp/core/schemas/config_application.py` (slug du Modèle embarqué, variante `cpu`, threads, dossier de données `%LOCALAPPDATA%\AssistantSP`)
- `tests/harness/test_assemblage.py`, `tests/core/test_config_racine.py`

**Dépendances :** aucune. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** le déplacement, **quand** on lance la suite existante (`tests/cli/test_ask.py`, document témoin), **alors** tout passe sans modification de ces tests, et `test_architecture.py` ne signale aucune violation de couche.
2. **Étant donné** `assembler(..., journal=J)` avec un journal injecté, **quand** l'Assistant est assemblé, **alors** `ModeSonde` et la `Passerelle` utilisent `J`, et aucune base n'est créée sous `SLMSP_VAR_DIR`.
3. **Étant donné** un processus gelé (simulé par `sys.frozen` et `sys._MEIPASS` posés dans le test), **quand** on appelle `racine_projet()`, `dossier_vendor()` et `dossier_modeles()`, **alors** ils pointent sous le dossier d'installation, et les variables `SLMSP_*` gardent la priorité.
4. **Étant donné** `config/application.toml`, **quand** il est chargé, **alors** un slug inconnu de `config/modeles/` est refusé avec un message clair.

**Stratégie de test :** unitaires avec ports factices ; aucun serveur lancé.

### Story 12.2 : Stockage local de l'application (`app.stockage`)

En tant qu'Agent,
je veux que mes conversations, mes Retours et mes réglages restent sur mon poste, dans mon profil, et que je puisse les supprimer,
afin de garder la maîtrise de mes données (FR-4, NFR-4).

**Couvre :** FR-4, FR-19 (stockage), FR-10 (réglage persistant), FR-38 (journal J4) ; AD-4, AD-23 ; UX-DR7, UX-DR8, UX-DR17, UX-DR18 (données).

**Fichiers et modules :**
- `src/slmsp/app/stockage.py` (SQLite unique sous `%LOCALAPPDATA%\AssistantSP\assistant.sqlite`, WAL, `user_version`). Tables : `conversations` (id, tâche, titre automatique, horodatages, messages au format canonique AD-7, sources), `retours` (tâche, question, réponse, sources, pouce, commentaire), `reglages` (clé/valeur : `hors_ligne_force`, `taille_texte`, `fenetre`, `plus_deplie`), `journal_requetes` (schéma `EntreeJournalRequetes`). `JournalApplication` implémente le port `JournalRequetes` avec purge à 30 jours glissants.
- `tests/app/test_stockage.py`

**Dépendances :** aucune (réutilise `core.schemas.journal_requetes`, `core.var.ouvrir_sqlite`). **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** une conversation enregistrée, **quand** on la supprime, **alors** elle disparaît immédiatement de la base (FR-4). Une restauration n'est possible que par `annuler_suppression(id)` dans les 5 s (UX-DR17), après quoi la ligne est effacée physiquement.
2. **Étant donné** des entrées de journal de plus de 30 jours, **quand** le stockage s'ouvre ou qu'une entrée est inscrite, **alors** elles sont purgées. « Effacer le journal » vide la table.
3. **Étant donné** `hors_ligne_force = true` enregistré, **quand** l'application redémarre, **alors** le réglage est relu (UX : réglage conservé d'un lancement à l'autre).
4. **Étant donné** « Effacer tout l'historique », **quand** il est confirmé puis non annulé, **alors** conversations et Retours sont supprimés, et `VACUUM` est exécuté.
5. **Étant donné** une base d'une version de schéma inconnue, **quand** on l'ouvre, **alors** une erreur claire est levée, sans écrasement.
6. **Étant donné** le port `JournalRequetes`, **quand** `JournalApplication` est injecté dans `assembler` (12.1), **alors** le test du document témoin passe avec ce journal.

**Stratégie de test :** SQLite dans `tmp_path` ; contenus aléatoires.

### Story 12.3 : Anonymisation de l'export des Retours (`app.anonymisation`)

En tant qu'Agent,
je veux exporter mes Retours dans un fichier où les données personnelles sont masquées, que je relis avant de le transmettre moi-même,
afin de partager mes Retours sans exposer d'usager (FR-20).

**Couvre :** FR-20 ; Deferred « Anonymisation des Retours » ; Q5.

**Fichiers et modules :**
- `src/slmsp/app/anonymisation.py` (fonction pure `anonymiser(texte) -> (texte_masque, comptes_par_motif)`. Motifs : NIR avec clé de contrôle, e-mail, téléphone français et international, IBAN avec contrôle modulo 97, adresse postale (numéro + type de voie + code postal), noms de personnes selon Q5. Remplacement par `[masqué]`.)
- `src/slmsp/app/ressources/prenoms.txt` (si Q5 est retenue : extrait du fichier des prénoms INSEE, licence au Registre des licences)
- `src/slmsp/app/export_retours.py` (construction du JSON `retours-assistant-AAAA-MM-JJ.json` à partir de `stockage`, aperçu, puis écriture à l'emplacement choisi)
- `tests/app/test_anonymisation.py`, `tests/app/test_export_retours.py`

**Dépendances :** décision Q5 ; interface de lecture des Retours de 12.2 (testable avec un faux). **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** un export témoin qui contient au moins une occurrence de chaque motif FR-20 (générées aléatoirement par le test, NIR et IBAN valides), **quand** on l'anonymise, **alors** aucun motif n'apparaît en clair dans le fichier écrit.
2. **Étant donné** un texte sans donnée personnelle (montants, dates, articles de loi, numéros de dossier), **quand** on l'anonymise, **alors** il est inchangé (taux de faux positifs mesuré et consigné sur un corpus de test aléatoire).
3. **Étant donné** un export, **quand** il est produit, **alors** aucune Requête sortante n'est émise (journal inchangé) et aucune écriture n'a lieu avant la confirmation de l'Agent.
4. **Étant donné** le module, **quand** `test_architecture.py` s'exécute, **alors** aucune dépendance nouvelle n'apparaît dans la fermeture runtime (AD-2).

### Story 12.4 : Socle de l'interface (jetons, disposition, navigation, zone de saisie, accessibilité)

En tant qu'Agent,
je veux une fenêtre claire, utilisable entièrement au clavier, qui me laisse choisir ma Tâche et saisir ma demande,
afin de travailler sans formation (FR-2, NFR-7).

**Couvre :** FR-2 ; NFR-7 ; UX-DR1, UX-DR2, UX-DR3, UX-DR4, UX-DR19 (états globaux : bienvenue, « Préparation de l'assistant… », erreur interne), UX-DR20, UX-DR21, UX-DR22.

**Fichiers et modules :**
- `src/slmsp/app/ui/index.html` (squelette trois colonnes et barre supérieure, régions ARIA, CSP `default-src 'self'`)
- `src/slmsp/app/ui/css/{jetons,socle}.css` (jetons de DESIGN.md en variables CSS, tailles en rem, focus violet 2 px, `prefers-reduced-motion`)
- `src/slmsp/app/ui/js/socle/{app,pont-client,bus,clavier,annonces,pont-factice}.js` (routeur des vues, client du pont avec file d'évènements, raccourcis UX-DR20, annonces `aria-live`, pont factice pour le développement)
- `src/slmsp/app/ui/js/vues/*.js` et `ui/css/<vue>.css` : **modules vides déclarés d'avance** (convention §3)
- `src/slmsp/app/ui/icones/*.svg` (icônes locales)
- `tests/app/ui/test_socle.py` (marqué `ui`)

**Dépendances :** aucune (pont factice). **Taille :** L.

**Critères d'acceptation :**
1. **Étant donné** la fenêtre à 1 024 × 640 et le texte à 150 %, **quand** on parcourt toutes les vues, **alors** il n'y a aucun défilement horizontal, et la disposition suit UX-DR2 (Sources qui poussent la zone centrale à 1 280 px ou plus, qui la recouvrent en dessous).
2. **Étant donné** le clavier seul, **quand** on parcourt l'interface, **alors** chaque contrôle est atteignable dans l'ordre fixé, avec un focus visible et un libellé accessible. Ctrl+1 à 4 activent les Tâches prioritaires, et la Tâche active est annoncée.
3. **Étant donné** la zone de saisie, **quand** on tape, **alors** Entrée envoie, Maj+Entrée insère une nouvelle ligne, Envoyer est inactif si le champ est vide, et le rappel sur les données personnelles s'affiche dans le champ vide (UX-DR4).
4. **Étant donné** les jetons, **quand** on contrôle les couples texte/fond, **alors** tous ont un contraste d'au moins 4,5:1, et le vert, le jaune et le rouge ne portent jamais de texte (UX-DR1).
5. **Étant donné** l'interface servie, **quand** elle se charge, **alors** aucune ressource externe n'est demandée (vérifié par l'enregistrement des requêtes dans Playwright).
6. **Étant donné** le mode « Préparation », **quand** le pont n'a pas signalé `pret`, **alors** la saisie est possible, mais Envoyer est libellé « Préparation… » et inactif (UX-DR19).

**Notes :** aucun framework, modules ES natifs, pas d'étape de build. Les vues des stories suivantes s'enregistrent auprès de `app.js` par une fonction `monter(conteneur, pont)`.

### Story 12.5 : Pont `js_api` et flux d'évènements

En tant qu'Anaël,
je veux une classe pont unique entre l'interface et `AssistantService`, qui pousse les évènements au fil de l'eau et permet d'arrêter une génération,
afin que l'interface ne contourne jamais le Harnais (AD-23).

**Couvre :** FR-1, FR-2, FR-38 (bout en bout via l'application) ; AD-14, AD-23 ; UX-DR4 (« Arrêter »), UX-DR5 (régénérer).

**Fichiers et modules :**
- `src/slmsp/app/pont/__init__.py` (`Pont` : méthodes JSON in/out ; l'interface pywebview n'est vue qu'à travers un port `Fenetre` avec `evaluate_js`, factice en test)
- `src/slmsp/app/pont/conversation.py` (`envoyer(tache, messages, options)`, `arreter()`, `regenerer()`, `nouvelle_conversation()` ; un fil de travail consomme `AssistantService.repondre` et pousse chaque évènement `vers_dict` par lots ; une génération à la fois)
- `src/slmsp/app/pont/{mode,reglages,historique,retours,verification}.py` : bouchons `NonImplementee` avec le contrat écrit dans le docstring (convention §3)
- `tests/app/test_pont.py`, `tests/app/test_document_temoin_app.py`

**Dépendances :** 12.1, 12.2. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** un service avec un LLM factice, **quand** l'interface appelle `envoyer`, **alors** la fenêtre factice reçoit les évènements dans l'ordre du flux, de `Jeton` à `Fin`, sous forme de JSON valide, et l'appel rend la main immédiatement.
2. **Étant donné** une génération en cours, **quand** `arreter()` est appelé, **alors** l'itérateur est fermé, un évènement de fin marqué `interrompue` est poussé, et le processus `llama-server` reste vivant et réutilisable.
3. **Étant donné** un second `envoyer` pendant une génération, **quand** il arrive, **alors** il est refusé avec une erreur JSON explicite.
4. **Étant donné** un document témoin à marqueur aléatoire, **quand** il est soumis par le pont à chaque Tâche de rédaction en Mode connecté (vrai `NetGate`, transport interne espion), **alors** aucune Requête sortante n'est journalisée et le marqueur n'apparaît nulle part dans le journal de l'application (FR-38).
5. **Étant donné** une exception du Harnais, **quand** elle survient, **alors** un évènement `Erreur` est poussé, sans le texte saisi (journal technique, AD-23).

### Story 12.6 : Lancement de l'application (fenêtre, instance unique, démarrage et arrêt)

En tant qu'Agent,
je veux que l'Assistant s'ouvre vite, une seule fois, à la taille où je l'ai laissé, et qu'il libère la mémoire à la fermeture,
afin de l'utiliser comme une application Windows ordinaire (UX-DR23).

**Couvre :** FR-21 (premier lancement hors ligne), NFR-1 (pas de processus orphelin) ; AD-6, AD-27 ; UX-DR19 (« Préparation »), UX-DR23 (instance unique, fenêtre mémorisée) ; Q1.

**Fichiers et modules :**
- `src/slmsp/app/principal.py` (point d'entrée `python -m slmsp.app` et script `assistantsp`. Mutex nommé Windows (ctypes) : la seconde instance remet la première au premier plan. `webview.create_window` avec taille et position relues dans `stockage`, minimum 1 024 × 640. Arguments de navigateur WebView2 durcis selon Q1. Navigation externe interceptée : les URL `https` de la Liste blanche s'ouvrent dans le navigateur du système, et toute autre navigation est refusée. Assemblage lancé en arrière-plan, puis signal `pret` au pont. Arrêt propre des serveurs (`ProcessusGere`/`JobObject`) à la fermeture.)
- `src/slmsp/app/__main__.py`
- `pyproject.toml` (section `[project.scripts]` seulement)
- `tests/app/test_principal.py`

**Dépendances :** 12.5 ; 12.4 pour un essai visuel. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** une instance ouverte, **quand** on en lance une seconde, **alors** elle se termine et la première passe au premier plan.
2. **Étant donné** la fenêtre redimensionnée puis fermée, **quand** on relance, **alors** taille et position sont restaurées, et ramenées à l'écran si celui-ci a changé.
3. **Étant donné** le démarrage, **quand** les serveurs ne sont pas prêts, **alors** la fenêtre s'affiche sans attendre et le pont signale `pret` à la fin de l'assemblage. Durée mesurée et consignée (cible < 10 s, UX).
4. **Étant donné** la fermeture de la fenêtre ou la fin brutale du processus, **quand** on inspecte les processus, **alors** aucun `llama-server` ne survit (JobObject).
5. **Étant donné** `hors_ligne_force` dans le stockage, **quand** l'application démarre, **alors** `ModeSonde` est créé en hors ligne forcé avant toute sonde.

**Stratégie de test :** unitaires avec `webview` factice ; un essai réel marqué `lent`.

### Story 12.7 : Vues Question et Recherche de données

En tant qu'Agent,
je veux lire la réponse au fil de l'eau, ouvrir ses sources et, en Recherche, voir des cartes de jeux de données et des tableaux sourcés,
afin de répondre à un usager avec une Source officielle (UJ-1, UJ-2).

**Couvre :** FR-1, FR-3 (affichage), FR-5 (extrait dépliable), FR-6 (date de l'Index par source), FR-7, FR-8, FR-9 (affichage du repli) ; UX-DR5, UX-DR6, UX-DR9, UX-DR11 (Copier, Régénérer), UX-DR19 (aucune source, valeurs hors ligne, repli data.gouv avec « Réessayer »).

**Fichiers et modules :**
- `src/slmsp/app/ui/js/vues/{question,recherche}.js`, `src/slmsp/app/ui/js/composants/{reponse,citations,sources,jeu-donnees,tableau}.js` (nouveaux)
- `src/slmsp/app/ui/css/{question,recherche}.css`
- `tests/app/ui/test_vues_question_recherche.py` (marqué `ui`, pont factice qui rejoue des flux d'évènements)

**Dépendances :** 12.4 (le pont réel 12.5 n'est requis que pour l'essai bout en bout). **Taille :** L.

**Critères d'acceptation :**
1. **Étant donné** un flux `Jeton…Sources…Avertissement…Fin`, **quand** il est rejoué, **alors** le texte s'affiche au fil de l'eau, les puces `[n]` deviennent des `citation-chip` lues « Source n : titre », et `legal-notice` n'apparaît que sous les réponses Question.
2. **Étant donné** une puce activée, **quand** le panneau Sources s'ouvre, **alors** chaque `source-card` montre l'origine, la date de l'Index et l'extrait dépliable. Échap ou × ferme le panneau. Hors ligne, « Ouvrir » copie le lien et affiche « Lien copié… ».
3. **Étant donné** des `ResultatOutil` tabulaires, **quand** ils arrivent, **alors** le tableau est rendu **depuis le résultat d'outil** (jamais depuis le texte), plafonné à 50 lignes avec la mention d'extrait. « Copier le tableau » produit du texte tabulé suivi de la ligne de source.
4. **Étant donné** un évènement `Repli`, **quand** il arrive, **alors** un `callout-warning` « données non vérifiées en ligne » s'affiche avec « Réessayer ».
5. **Étant donné** « Arrêter » pendant la génération, **quand** la fin `interrompue` arrive, **alors** « Réponse interrompue » s'affiche et « Régénérer » remplace la réponse sur place.

### Story 12.8 : Vues de rédaction Compte rendu et Langage clair

En tant qu'Agent,
je veux coller mes notes ou un texte administratif dans un volet et obtenir à côté un compte rendu ou une version en langage clair, que je copie en un clic,
afin de rédiger plus vite sans que mon texte quitte le poste (UJ-3, UJ-4).

**Couvre :** FR-13 (affichage, « Partie i sur n »), FR-16 (passages signalés), FR-38 ; UX-DR10, UX-DR11, UX-DR12, UX-DR19 (entrée trop longue) ; Q11.

**Fichiers et modules :**
- `src/slmsp/app/ui/js/vues/redaction.js` (volet de rédaction générique : compteur de mots, un seul bouton principal visible, résultat au fil de l'eau, « Copier » le texte brut final ; **réutilisé par les vues de l'Epic 13**)
- `src/slmsp/app/ui/js/composants/passages-signales.js` (extraction tolérante de la section finale de LC, Q11)
- `src/slmsp/app/ui/css/redaction.css`
- `tests/app/ui/test_vue_redaction.py` (marqué `ui`)

**Dépendances :** 12.4. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** des notes de plus de 6 000 mots, **quand** le Harnais émet des `Progression`, **alors** « Partie i sur n » s'affiche, puis le résultat fusionné.
2. **Étant donné** une sortie LC avec une section de passages conservés, **quand** elle est rendue, **alors** chaque passage est surligné (`flagged-passage`) avec une infobulle accessible au survol et au focus. Sans section reconnue, le texte s'affiche normalement.
3. **Étant donné** « Copier », **quand** on l'active, **alors** le presse-papiers reçoit le texte brut final, et une `inline-confirmation` s'efface après 3 s.
4. **Étant donné** une largeur inférieure à 1 200 px, **quand** la vue s'affiche, **alors** les volets s'empilent.

### Story 12.9 : Indicateur de Mode et journal des Requêtes sortantes

En tant qu'Agent,
je veux voir en permanence si l'Assistant est connecté, pouvoir le forcer hors ligne et consulter ce qui est parti sur le réseau,
afin de répondre à ma DSI sur ce que l'outil contacte (FR-10, FR-11, FR-38).

**Couvre :** FR-10, FR-11 (application), FR-38 (consultation) ; UX-DR7, UX-DR8.

**Fichiers et modules :**
- `src/slmsp/app/pont/mode.py` (`mode()`, `forcer_hors_ligne(bool)` persistant via `stockage`, `journal(limite)`, `effacer_journal()` ; changement de Mode poussé à l'interface après chaque sonde)
- `src/slmsp/app/ui/js/vues/mode.js`, `src/slmsp/app/ui/css/mode.css`
- `tests/app/test_pont_mode.py`, `tests/app/ui/test_vue_mode.py` (marqué `ui`)

**Dépendances :** 12.5, 12.4. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** la pastille, **quand** le Mode change, **alors** elle passe de « Connecté » à « Hors ligne » ou « Hors ligne (choisi) », avec une seule annonce au lecteur d'écran.
2. **Étant donné** « Rester hors ligne » activé dans le menu de la pastille, **quand** on pose une question RD, **alors** le transport interne espion n'est jamais appelé, sonde comprise, et le réglage survit au redémarrage.
3. **Étant donné** le journal, **quand** on l'ouvre, **alors** il liste Heure, Hôte, Termes et Statut sur 30 jours glissants, avec un état vide explicite. « Effacer le journal » le vide.
4. **Étant donné** une requête vers un hôte hors liste, **quand** elle est tentée, **alors** elle apparaît au journal avec le statut `bloquee-liste`.

### Story 12.10 : Paramètres et « À propos »

En tant qu'Agent ou DSI,
je veux régler la taille du texte, effacer mon historique, et lire les versions, la date de l'Index, la Liste blanche, les licences et l'avertissement juridique,
afin de savoir ce que fait l'outil et de l'adapter (FR-23).

**Couvre :** FR-6, FR-11 (affichage de la liste effective), FR-23 ; UX-DR18, UX-DR20 (Ctrl+/−/0), UX-DR22 (mentions fixes).

**Fichiers et modules :**
- `src/slmsp/app/pont/reglages.py` (`reglages()`, `definir_reglage()`, `a_propos()` : version de l'application, Modèle embarqué (slug, empreinte du GGUF), Index (`MANIFEST.json`, date), Liste blanche lue dans `config/liste-blanche.toml`, licences)
- `src/slmsp/app/ressources/licences-tierces.json` (produit au build par 12.12 ; un fichier minimal versionné en attendant)
- `src/slmsp/app/ui/js/vues/parametres.js`, `src/slmsp/app/ui/css/parametres.css` (dialogue à trois onglets ; l'onglet Retours accueille le composant de 12.11 ; « Rester hors ligne » réutilise `vues/mode.js`)
- `tests/app/test_pont_reglages.py`, `tests/app/ui/test_vue_parametres.py` (marqué `ui`)

**Dépendances :** 12.5, 12.9 (réglage du Mode). **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** « À propos », **quand** on l'ouvre, **alors** les versions, la date de l'Index, la Liste blanche effective (huit hôtes aujourd'hui), les licences et l'avertissement juridique s'affichent.
2. **Étant donné** `liste-blanche.toml` modifié sans recompilation, **quand** on relance, **alors** « À propos » affiche la nouvelle liste.
3. **Étant donné** Ctrl+ / Ctrl− / Ctrl 0, **quand** on les presse, **alors** la taille du texte suit les cinq crans de 100 à 150 % et elle est mémorisée.
4. **Étant donné** « Effacer tout l'historique », **quand** on ne l'annule pas dans les 5 s, **alors** le stockage est vidé (12.2).

### Story 12.11 : Historique et Retours dans l'interface

En tant qu'Agent,
je veux retrouver mes conversations par jour, en supprimer, noter une réponse et exporter mes Retours après les avoir relus,
afin de garder mon travail et de faire remonter mon avis sans télémétrie (FR-4, FR-19, FR-20).

**Couvre :** FR-4, FR-19, FR-20 (interface) ; UX-DR16, UX-DR17, UX-DR19 (aperçu de l'export avec [masqué]).

**Fichiers et modules :**
- `src/slmsp/app/pont/{historique,retours}.py`
- `src/slmsp/app/ui/js/vues/{historique,retours}.js`, `src/slmsp/app/ui/css/{historique,retours}.css`
- `tests/app/test_pont_historique_retours.py`, `tests/app/ui/test_vues_historique_retours.py` (marqué `ui`)

**Dépendances :** 12.2, 12.3, 12.5 ; 12.10 pour l'onglet Retours (le composant se monte dans l'onglet). **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** un premier envoi, **quand** la réponse se termine, **alors** une entrée d'historique est créée avec un titre automatique, groupée par jour. La rouvrir réactive sa Tâche d'origine.
2. **Étant donné** « Supprimer », **quand** on l'active, **alors** l'entrée disparaît sans confirmation, et « Annuler » reste disponible 5 s.
3. **Étant donné** un pouce haut, **quand** on clique, **alors** le Retour est enregistré immédiatement. Un pouce bas ouvre un champ de commentaire facultatif. La confirmation est discrète.
4. **Étant donné** « Exporter mes retours », **quand** on clique, **alors** l'aperçu anonymisé s'affiche avant tout enregistrement, avec un dialogue « Enregistrer sous » (proposition `retours-assistant-AAAA-MM-JJ.json`). Aucune Requête sortante n'est émise.

### Story 12.12 : Exécutable PyInstaller avec Modèle embarqué et Index local

En tant qu'Anaël,
je veux construire en une commande un dossier exécutable autonome qui contient l'application, les binaires llama.cpp CPU, le Modèle embarqué, BGE-M3 et l'Index local,
afin de préparer l'installateur sans dépendance chez l'Agent (FR-21, NFR-6).

**Couvre :** FR-21 (préalable), NFR-6 (taille), AD-2, AD-6 ; Q3, Q13.

**Fichiers et modules :**
- `packaging/assistantsp.spec` (onedir ; exclut tout ce qui est lourd, AD-2 ; ressources : `config/` utile au runtime, `config/prompts/taches/`, `vendor/llama.cpp/<tag>/bin-cpu/`, `models/<slug>/*.gguf`, `models/bge-m3/*.gguf`, `index/`)
- `outils/construire_application.py` (build reproductible : vérifie les empreintes des GGUF et de l'Index, génère `licences-tierces.json`, écrit `build/manifeste-application.json` avec tailles et empreintes)
- `tests/packaging/test_spec.py` (contrôle statique de la liste des ressources et des exclusions)

**Dépendances :** 12.1, 12.6 ; Q13 (Modèle embarqué) pour le build final. **Taille :** L.

**Critères d'acceptation :**
1. **Étant donné** le build, **quand** il se termine, **alors** le dossier se lance sur le poste de dev sans `uv` ni Python installé dans le `PATH`, et répond à une Question hors ligne.
2. **Étant donné** le manifeste de build, **quand** on le lit, **alors** il donne la taille totale (≤ 4 Go, NFR-6, sinon le build échoue avec le détail par composant) et les empreintes de chaque GGUF et de l'Index.
3. **Étant donné** la fermeture runtime, **quand** on inspecte le dossier, **alors** il ne contient ni `torch`, ni `transformers`, ni les SDK `anthropic`/`mistralai`, ni `huggingface_hub`.
4. **Étant donné** une ressource manquante ou une empreinte fausse, **quand** on lance le build, **alors** il échoue avant PyInstaller.

### Story 12.13 : Installateur Inno Setup par utilisateur et désinstallation

En tant qu'Agent sur un poste verrouillé,
je veux installer l'Assistant sans droits administrateur en trois écrans, et le désinstaller en répondant à une seule question,
afin de l'adopter sans passer par ma DSI (UJ-5, FR-21, FR-22).

**Couvre :** FR-21, FR-22, NFR-6 ; UX-DR23 ; Q2, Q3, Q4, Q6.

**Fichiers et modules :**
- `packaging/assistantsp.iss` (`PrivilegesRequired=lowest`, installation dans `{localappdata}\Programs\AssistantSP`, raccourci du menu Démarrer, case « Lancer l'assistant » cochée, détection du runtime WebView2 (Q2), `AppId` stable pour réinstaller par-dessus (Q6). La désinstallation pose « Conserver l'historique et les retours sur ce poste ? » et supprime `%LOCALAPPDATA%\AssistantSP\` sur « Non ». Fichiers de plus de 2 Go : découpage `DiskSpanning` à vérifier au premier build.)
- `outils/construire_installateur.py` (appelle `ISCC.exe`, écrit l'empreinte SHA-256 de l'installateur)
- `docs/installation-dsi.md` (une page : pas de droits admin, hôtes contactés, SmartScreen si non signé, empreinte)

**Dépendances :** 12.12. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** un compte Windows standard, **quand** on lance l'installateur depuis un partage réseau, **alors** aucune élévation n'est demandée, trois écrans au plus s'affichent, et l'Assistant se lance à la fin.
2. **Étant donné** le câble réseau débranché, **quand** l'Assistant démarre la première fois, **alors** il fonctionne en Mode hors ligne sans aucun téléchargement (FR-21).
3. **Étant donné** la désinstallation avec « Non », **quand** elle se termine, **alors** aucun fichier de l'Assistant ne reste dans le profil (FR-22) ; avec « Oui », la base `assistant.sqlite` est conservée.
4. **Étant donné** une réinstallation par-dessus, **quand** elle se termine, **alors** l'historique est conservé.

**Stratégie de test :** recette manuelle consignée (compte standard créé pour l'occasion) ; c'est aussi le protocole de SM-8.

### Story 12.14 : Mesures FR-26 avec WebView2 et recette sur PC cible

En tant qu'Anaël,
je veux mesurer la RAM, le débit et la latence de l'Assistant installé sur un vrai PC de 16 Go sans GPU, et vérifier qu'il ne contacte que la Liste blanche,
afin de valider SM-5 et la promesse de confidentialité avant de montrer l'outil (NFR-1, NFR-4).

**Couvre :** NFR-1, NFR-2, NFR-3, NFR-4, NFR-7 (trois critères), SM-5 ; FR-26 ; Q1.

**Fichiers et modules :**
- `src/slmsp/measure/application.py` (mesure de l'arbre de processus de l'application installée, WebView2 compris : `msedgewebview2.exe` et `llama-server`, via `measure.ram.somme_arbre`)
- `src/slmsp/cli/measure.py` (sous-commande `measure application --exe …`)
- `docs/recette-pc-cible.md` (protocole : capture réseau en hors ligne forcé et en connecté, liste de contrôle RGAA des trois critères, consignation des résultats)
- `tests/measure/test_application.py`

**Dépendances :** 12.13 ; accès à un PC cible (Anaël). **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** l'Assistant installé sur le PC cible, **quand** une génération Question tourne, **alors** la RAM maximale de l'arbre complet, WebView2 compris, est mesurée et comparée au seuil de 5 Go (cible 4 Go). En cas de dépassement, les leviers de l'addendum §D sont proposés dans l'ordre, sans être appliqués d'office.
2. **Étant donné** le Mode hors ligne forcé et une capture réseau (pktmon ou Wireshark) pendant 10 minutes d'usage, **quand** on l'analyse, **alors** aucun paquet ne part de l'arbre de processus de l'Assistant. Tout résidu du runtime WebView2 est consigné (Q1).
3. **Étant donné** le Mode connecté, **quand** on capture, **alors** seuls les hôtes de la Liste blanche sont contactés par l'Assistant.
4. **Étant donné** la liste de contrôle NFR-7, **quand** elle est déroulée, **alors** le clavier, le contraste et les libellés sont conformes, ou leurs écarts sont listés.

---

## 5. Epic 13 : Tâches secondaires, vérification en ligne et publication (J5)

Toutes les vues de cet epic réutilisent le volet de rédaction de 12.8 et ne touchent que leurs propres fichiers (convention §3). Les Tâches CO, RE, CT et TR existent déjà au Harnais et au banc.

### Story 13.1 : Vue Correction avec différences visibles

En tant qu'Agent,
je veux voir les corrections apportées à mon texte sous forme de différences lisibles, et copier la version corrigée en un clic,
afin de vérifier chaque modification avant de l'accepter (FR-17).

**Couvre :** FR-17 ; UX-DR13.

**Fichiers et modules :**
- `src/slmsp/app/differences.py` (différences par mots avec `difflib`, côté Python pour les tester ; aucune dépendance)
- `src/slmsp/app/pont/conversation.py` : **non touché** ; la méthode `differences(avant, apres)` est ajoutée dans le module `src/slmsp/app/pont/redaction_outils.py`, déclaré d'avance par 12.5 (à ajouter à la liste de §3 lors de la validation)
- `src/slmsp/app/ui/js/vues/correction.js`, `src/slmsp/app/ui/css/correction.css`
- `tests/app/test_differences.py`, `tests/app/ui/test_vue_correction.py` (marqué `ui`)

**Dépendances :** 12.8, 12.5. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** un texte et sa correction, **quand** la génération se termine, **alors** les insertions et les suppressions sont marquées `diff-insert` et `diff-delete`, lisibles **sans la couleur** (soulignement, barré, texte annoncé au lecteur d'écran).
2. **Étant donné** « Copier la version corrigée », **quand** on l'active, **alors** le presse-papiers reçoit le texte corrigé brut.
3. **Étant donné** deux textes identiques, **quand** on calcule les différences, **alors** la vue l'indique (« Aucune correction »).

### Story 13.2 : Vue Résumé à trois longueurs

En tant qu'Agent,
je veux choisir un résumé court, moyen ou détaillé d'un document collé,
afin d'adapter le résumé à mon usage (FR-15).

**Couvre :** FR-15.

**Fichiers et modules :** `src/slmsp/app/ui/js/vues/resume.js`, `src/slmsp/app/ui/css/resume.css`, `tests/app/ui/test_vue_resume.py` (marqué `ui`).

**Dépendances :** 12.8. **Taille :** S.

**Critères d'acceptation :**
1. **Étant donné** les trois longueurs, **quand** on en choisit une, **alors** l'entrée envoyée au Harnais porte `longueur_demandee` avec la valeur du libellé, celle du jeu gelé si elle existe, pour garder les conditions du banc.
2. **Étant donné** un document plus long que la fenêtre de contexte, **quand** on le soumet, **alors** le message d'entrée trop longue (UX-DR19) s'affiche si le Harnais le refuse.

### Story 13.3 : Vue Courrier type, formulaire et emplacements

En tant qu'Agent,
je veux remplir un petit formulaire (type de courrier, objet, éléments connus) et obtenir un courrier où chaque information manquante est un emplacement visible,
afin de ne jamais envoyer une valeur inventée (FR-14).

**Couvre :** FR-14 ; UX-DR14.

**Fichiers et modules :**
- `src/slmsp/harness/emplacements.py` (détection des emplacements `[…]` et contrôle « aucun champ non fourni rendu par une valeur ». Si la règle de `evaluation/controles.py` s'applique, elle est **déplacée** ici et réexportée par `evaluation`, car `app` ne peut pas importer `evaluation` (AD-2).)
- `src/slmsp/app/ui/js/vues/courrier.js`, `src/slmsp/app/ui/css/courrier.css`
- `tests/harness/test_emplacements.py`, `tests/app/ui/test_vue_courrier.py` (marqué `ui`)

**Dépendances :** 12.8. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** le formulaire, **quand** on l'envoie, **alors** l'entrée CT porte `type_courrier` (accusé de réception, demande de pièces, convocation, réponse d'information) et les champs remplis seulement.
2. **Étant donné** la sortie, **quand** elle contient des emplacements, **alors** chacun est rendu en `letter-placeholder`, atteignable au clavier, et annoncé « à compléter ».
3. **Étant donné** un champ non fourni, **quand** le contrôle automatique détecte une valeur à sa place, **alors** un `callout-warning` le signale (FR-14, « vérifié automatiquement »).

### Story 13.4 : Vue Traduction (cinq langues, arabe en RTL)

En tant qu'Agent,
je veux traduire un texte depuis ou vers l'anglais, l'espagnol, l'arabe, le portugais ou l'allemand, avec la mention de vérification,
afin d'aider un usager non francophone (FR-18, UJ-4).

**Couvre :** FR-18 ; UX-DR15 ; Q9.

**Fichiers et modules :**
- `config/application.toml` (liste des langues proposées ; l'arabe se retire par une ligne, Q9) : **seule entrée de config partagée**, à coordonner avec 12.1 (12.1 déclare la clé `langues_traduction`)
- `src/slmsp/app/ui/js/vues/traduction.js`, `src/slmsp/app/ui/css/traduction.css`
- `tests/app/ui/test_vue_traduction.py` (marqué `ui`)

**Dépendances :** 12.8 ; 12.1 (clé de config). **Taille :** S.

**Critères d'acceptation :**
1. **Étant donné** le sélecteur, **quand** on choisit langue source et cible, **alors** l'entrée TR porte `langue_source` et `langue_cible`. Un bouton inverse le sens.
2. **Étant donné** l'arabe en sortie ou en entrée, **quand** le volet s'affiche, **alors** il est en `dir="rtl"` avec `lang="ar"`, sans casser la mise en page.
3. **Étant donné** toute traduction, **quand** elle se termine, **alors** la mention « Traduction automatique, à vérifier avant envoi » est affichée et incluse dans la copie.

### Story 13.5 : Vérification en ligne d'une page officielle, côté Harnais (FR-12)

En tant qu'Agent,
je veux demander à l'Assistant de vérifier sa réponse sur la page officielle correspondante quand je suis connecté,
afin de m'assurer qu'une information de l'Index local n'a pas changé (FR-12).

**Couvre :** FR-12, FR-38, NFR-5 ; AD-4 (profil `assistant`), AD-14 ; Q7. **À ne développer que si Q7 garde FR-12.**

**Fichiers et modules :**
- `src/slmsp/harness/verification.py` (`verifier(reponse, sources, mode, passerelle, llm)`. Choisit l'URL de la source citée la mieux classée et contrôle qu'elle est sur la Liste blanche. GET par `net.client("assistant")`, journalisé (`outil = "verification-page"`, `termes = {"url": …}`). Extraction du texte principal par `html.parser` de la bibliothèque standard. Comparaison par le Modèle embarqué avec `VE.md`. Évènements produits.)
- `src/slmsp/core/evenements.py` (nouvel évènement `Verification` : url, titre, date de consultation, verdict `concordant`/`difference`/`indisponible`, phrase)
- `config/prompts/taches/VE.md` (consignes seulement, aucun exemple, D1.1 ; validé par `core.gabarits`)
- `config/harnais.toml` (délai, taille maximale de page)
- `tests/harness/test_verification.py`

**Dépendances :** 12.1 (assemblage) ; indépendante de l'interface. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** le Mode hors ligne (détecté ou forcé), **quand** on demande une vérification, **alors** elle est refusée avant toute connexion, avec le statut `bloquee-mode` au journal.
2. **Étant donné** une réponse et ses sources, **quand** on vérifie, **alors** la seule Requête sortante est un GET de l'URL d'une source déjà citée. Le journal ne contient ni la question, ni la réponse, ni aucun texte saisi (test avec un marqueur aléatoire).
3. **Étant donné** une URL hors Liste blanche, ou une redirection qui en sort, **quand** on vérifie, **alors** la requête est bloquée (`bloquee-liste`) et le verdict est `indisponible`.
4. **Étant donné** une page récupérée (réponse HTTP factice), **quand** la comparaison se termine, **alors** un évènement `Verification` porte l'URL, le titre, la date et l'heure de consultation et le verdict. La page est ajoutée aux sources.
5. **Étant donné** un délai dépassé, **quand** la page ne répond pas, **alors** le verdict est `indisponible`, sans relance automatique.

### Story 13.6 : Bouton « Vérifier en ligne » dans la vue Question

En tant qu'Agent,
je veux un bouton secondaire « Vérifier en ligne » sous une réponse Question quand je suis connecté,
afin de lancer la vérification moi-même, jamais automatiquement (UX-DR24).

**Couvre :** FR-12 (interface) ; UX-DR24 ; Q7.

**Fichiers et modules :** `src/slmsp/app/pont/verification.py`, `src/slmsp/app/ui/js/vues/verification.js`, `src/slmsp/app/ui/css/verification.css`, `tests/app/test_pont_verification.py`, `tests/app/ui/test_vue_verification.py` (marqué `ui`).

**Dépendances :** 13.5, 12.7, 12.9. **Taille :** S.

**Critères d'acceptation :**
1. **Étant donné** le Mode hors ligne, ou FR-12 coupé dans la config, **quand** une réponse Question s'affiche, **alors** le bouton n'existe pas (absent du DOM, pas seulement grisé).
2. **Étant donné** le Mode connecté, **quand** on clique, **alors** l'encart « Vérifié sur [titre] le [date] : concordant » ou « Différence relevée : [phrase] » s'affiche sous la réponse, et la page rejoint le panneau Sources.
3. **Étant donné** le verdict `indisponible`, **quand** il arrive, **alors** un `callout-warning` l'indique sans bloquer la conversation.

### Story 13.7 : Dossier de publication et fiche modèle (FR-37)

En tant qu'Anaël,
je veux préparer hors ligne un dossier de publication complet et vérifié (Modèle embarqué, fiche modèle, Comparatif, Registre des licences), que je téléverse ensuite moi-même,
afin de publier sans risque d'envoi automatique ni d'allégation trompeuse (FR-37).

**Couvre :** FR-37 ; D1.4 ; AD-4 (interdiction d'upload intacte), AD-20, AD-21 ; Q8.

**Fichiers et modules :**
- `src/slmsp/publication/` (nouveau paquet, couche 4, hors runtime : `preparer.py`, `fiche.py`, `controles.py`), ajouté à `COUCHES` dans `tests/test_architecture.py`
- `src/slmsp/cli/publication.py` (sous-commande `publication preparer --modele … --sortie …` ; **aucune** sous-commande d'envoi)
- `config/publication.toml` (licence par Modèle de base, mentions obligatoires, liste de formulations interdites)
- `docs/procedure-publication.md` (téléversement manuel par Anaël, privé puis public)
- `tests/publication/test_preparer.py`, `test_controles.py`

**Dépendances :** Epic 11 (Comparatif, story 11.1) ; Q8, Q13 ; **indépendante de l'Epic 12**. **Taille :** M.

**Critères d'acceptation :**
1. **Étant donné** un Modèle embarqué et son Comparatif, **quand** on lance `publication preparer`, **alors** le dossier contient : `README.md` (fiche : données utilisées et Registre des licences, résultats d'évaluation, limites et usages déconseillés), `LICENSE`, le GGUF, le Comparatif et `SHA256SUMS`. Aucune connexion réseau n'a lieu (profil `aucun`).
2. **Étant donné** un Modèle de base dont la licence n'autorise pas Apache 2.0, **quand** on prépare, **alors** la licence compatible la plus permissive déclarée dans la config est retenue, ou la préparation échoue si aucune ne l'est.
3. **Étant donné** la fiche, **quand** les contrôles tournent, **alors** toute formulation de certification (« certifié », « ISO 42001 », « conforme à… ») est refusée, sauf une mention de non-certification explicite.
4. **Étant donné** le dossier, **quand** les contrôles anti-fuite tournent, **alors** il ne contient aucun texte du Jeu d'évaluation maison (API anti-fuite d'AD-11), ni aucun secret (`.env`, clés).
5. **Étant donné** le code du paquet, **quand** `ruff` et `test_architecture.py` tournent, **alors** aucune fonction d'upload n'est importée.

**Notes :** la fiche est rédigée par le code à partir des artefacts, avec un gabarit. C'est de la documentation, pas une Donnée d'entraînement. Le texte libre des limites est relu par Anaël.

### Story 13.8 : Réinstallateur J5 et recette des Tâches secondaires

En tant qu'Anaël,
je veux reconstruire l'installateur avec les vues de J5 et dérouler une recette courte sur le PC cible,
afin de livrer J5 dans les mêmes conditions que J4.

**Couvre :** FR-14, FR-15, FR-17, FR-18, FR-12 (si gardée) ; NFR-1, NFR-7.

**Fichiers et modules :** `docs/recette-pc-cible.md` (section J5), `build/` (artefacts non versionnés).

**Dépendances :** 13.1 à 13.4, 13.6 si gardée, 12.13, 12.14. **Taille :** S.

**Critères d'acceptation :**
1. **Étant donné** l'installateur J5, **quand** on l'installe par-dessus J4, **alors** l'historique est conservé et les quatre vues secondaires fonctionnent hors ligne.
2. **Étant donné** la mesure de 12.14 relancée, **quand** une Traduction ou un Résumé long tourne, **alors** la RAM reste dans le seuil NFR-1.

---

## 6. Dépendances, zones de fichiers et lots parallélisables

### Tableau des dépendances

| Story | Dépend de | Zone de fichiers principale | Taille |
|---|---|---|---|
| 12.1 | — | `harness/assemblage.py`, `cli/_assemblage.py`, `cli/ask.py` (import), `core/config.py`, `config/application.toml`, `core/schemas/config_application.py` | M |
| 12.2 | — | `app/stockage.py` | M |
| 12.3 | Q5 | `app/anonymisation.py`, `app/export_retours.py`, `app/ressources/prenoms.txt` | M |
| 12.4 | — | `app/ui/index.html`, `app/ui/css/{jetons,socle}.css`, `app/ui/js/socle/`, bouchons `app/ui/js/vues/*`, `app/ui/icones/` | L |
| 12.5 | 12.1, 12.2 | `app/pont/` (dont les bouchons des domaines) | M |
| 12.6 | 12.5 | `app/principal.py`, `app/__main__.py`, `pyproject.toml` (`[project.scripts]`) | M |
| 12.7 | 12.4 | `ui/js/vues/{question,recherche}.js`, `ui/js/composants/{reponse,citations,sources,jeu-donnees,tableau}.js` | L |
| 12.8 | 12.4 | `ui/js/vues/redaction.js`, `ui/js/composants/passages-signales.js` | M |
| 12.9 | 12.4, 12.5 | `app/pont/mode.py`, `ui/js/vues/mode.js` | M |
| 12.10 | 12.5, 12.9 | `app/pont/reglages.py`, `ui/js/vues/parametres.js`, `app/ressources/licences-tierces.json` | M |
| 12.11 | 12.2, 12.3, 12.5, 12.10 | `app/pont/{historique,retours}.py`, `ui/js/vues/{historique,retours}.js` | M |
| 12.12 | 12.1, 12.6, Q3, Q13 | `packaging/assistantsp.spec`, `outils/construire_application.py` | L |
| 12.13 | 12.12, Q2, Q4 | `packaging/assistantsp.iss`, `outils/construire_installateur.py`, `docs/installation-dsi.md` | M |
| 12.14 | 12.13, Q1 | `measure/application.py`, `cli/measure.py`, `docs/recette-pc-cible.md` | M |
| 13.1 | 12.5, 12.8 | `app/differences.py`, `app/pont/redaction_outils.py`, `ui/js/vues/correction.js` | M |
| 13.2 | 12.8 | `ui/js/vues/resume.js` | S |
| 13.3 | 12.8 | `harness/emplacements.py` (+ `evaluation/controles.py` si déplacement), `ui/js/vues/courrier.js` | M |
| 13.4 | 12.1, 12.8, Q9 | `ui/js/vues/traduction.js` | S |
| 13.5 | 12.1, Q7 | `harness/verification.py`, `core/evenements.py`, `config/prompts/taches/VE.md`, `config/harnais.toml` | M |
| 13.6 | 13.5, 12.7, 12.9 | `app/pont/verification.py`, `ui/js/vues/verification.js` | S |
| 13.7 | Epic 11 (11.1), Q8, Q13 | `publication/`, `cli/publication.py`, `config/publication.toml`, `tests/test_architecture.py` (table `COUCHES`) | M |
| 13.8 | 13.1 à 13.4, 13.6, 12.13, 12.14 | `docs/recette-pc-cible.md` (section J5) | S |

### Lots proposés (trois stories au plus en même temps, zones de fichiers disjointes)

| Lot | Stories en parallèle | Condition d'entrée | Remarque |
|---|---|---|---|
| **L1** | 12.1, 12.2, 12.4 | aucune | Les trois socles. Aucune zone commune. |
| **L2** | 12.5, 12.7, 12.3 | L1 ; Q5 pour 12.3 | Sans réponse à Q5, remplacer 12.3 par 12.8. |
| **L3** | 12.6, 12.8, 12.9 | 12.5 | 12.6 ne touche que `principal.py`. 12.9 ne touche que `pont/mode.py` et `vues/mode.js`. |
| **L4** | 12.10, 12.12, 13.5 | L3 ; Q3, Q13 pour 12.12 ; Q7 pour 13.5 | 13.5 est indépendant de l'interface et peut avancer ici, mais §9.3 conseille d'attendre que J4 soit assuré. Sinon, prendre 12.3. |
| **L5** | 12.11, 12.13, 13.1 | 12.10 ; 12.12 | 12.11 et 13.1 touchent des modules `pont/` distincts. |
| **L6** | 12.14, 13.2, 13.3 | 12.13 ; PC cible | 12.14 demande Anaël et le PC cible. |
| **L7** | 13.4, 13.6, 13.7 | 13.5 pour 13.6 ; Epic 11 pour 13.7 | 13.7 peut aussi passer dans n'importe quel lot dès que 11.1 et Q8 sont réglés : sa zone de fichiers ne croise rien. |
| **L8** | 13.8 | tout le reste | Recette finale J5. |

**Points de vigilance sur les conflits :**
- `config/application.toml` : créé par 12.1, qui déclare d'avance la clé `langues_traduction` lue par 13.4.
- `core/evenements.py` : seule 13.5 le modifie.
- `cli/measure.py` (12.14) et `cli/publication.py` (13.7) : un module par commande, comme le veut la convention existante. `cli/__init__.py` doit déclarer `publication` (petite modification, à faire dans 13.7 ou dès la validation de ce brouillon).
- `app/pont/redaction_outils.py` (13.1) : à ajouter à la liste des bouchons déclarés par 12.5.
- `tests/test_architecture.py` : seule 13.7 le modifie (nouveau paquet `publication`).

## 7. Risques signalés

- **RAM (NFR-1).** La WebView2 ajoute 150 à 300 Mo, selon les mesures publiques (à confirmer par la mesure). Avec H-RAM à 3,7–4,2 Go, la cible de 4 Go est probablement dépassée ; le plafond de 5 Go reste plausible. La mesure 12.14 tranche.
- **Taille (NFR-6).** Environ 3,4 Go estimés, pour un plafond de 4 Go. Un Index étendu (LEGI, etc.) ne tiendrait pas.
- **Antivirus et SmartScreen** sur un exécutable PyInstaller non signé : risque direct pour SM-8 (Q4).
- **Charge.** 22 stories, dont 3 L. L'ordre de coupe §9.3 permet de retirer 13.5, 13.6, puis 13.4, puis 13.2 et 13.3, puis 13.1, sans toucher l'Epic 12.

## Étape suivante recommandée

- **Skill** : `bmad-create-epics-and-stories` (report des stories validées dans `epics.md`), puis `bmad-sprint-planning` (mise à jour de `sprint-status.yaml`)
- **Prompt** : « Reporte dans `_bmad-output/planning-artifacts/epics.md` les stories des Epics 12 et 13 du brouillon `brouillon-stories-epics-12-13.md`, en appliquant mes réponses aux questions Q1 à Q13 [à compléter], puis mets à jour le tableau des dépendances et les lots. »
- **Modèle** : Opus 5.5 (spec de story, décisions de conception)
- **Effort** : medium (high si les réponses aux questions modifient le découpage)
- **Nouveau chat** : oui (`/clear`), après avoir répondu aux questions.
