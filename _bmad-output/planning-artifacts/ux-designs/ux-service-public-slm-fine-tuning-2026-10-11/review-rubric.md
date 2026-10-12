# Revue de la paire de spines (rubric walker) — Assistant IA local secteur public

- **DESIGN.md** et **EXPERIENCE.md** du dossier `ux-service-public-slm-fine-tuning-2026-10-11`
- **Source** : PRD `prd-service-public-slm-fine-tuning-2026-10-11/prd.md` (§3 à §5 et §9.3 lus)
- **Date** : 2026-10-12
- **Hors lecture** : maquettes HTML (non ouvertes), PRD §2.3 (noms des UJ non vérifiés mot pour mot)

## Verdict global

La paire est solide sur l'identité, les Tâches prioritaires et les flux UJ-1 à UJ-5 : un agent de développement peut construire les vues Question, Compte rendu et Langage clair sans deviner. Les trous sont ailleurs. Plusieurs surfaces n'ont pas de forme définie (Journal, Paramètres, À propos : boîte de dialogue ou vue ?). Des composants utilisés n'ont aucune spec visuelle (carte de jeu de données, passage signalé, encarts d'état). Il y a aussi une contradiction avec FR-4 (suppression « immédiate » contre annulation 5 s) et des comportements de copie ambigus. Les Tâches secondaires et l'export des Retours n'ont aucun flux.

## 1. Couverture des flux — mince

Vérifié : chaque FR à composante UI (FR-1 à FR-23, FR-38) a une surface dans l'IA, et chaque surface est parcourue par au moins un flux.

| FR | Surface | Flux |
|---|---|---|
| FR-1, FR-2, FR-3, FR-5, FR-6 | Question, Panneau Sources | Flux 1 |
| FR-7, FR-8, FR-9, FR-38 | Recherche, Journal | Flux 2 |
| FR-13 | Compte rendu | Flux 3 |
| FR-16, FR-18 | Langage clair, Traduction | Flux 4 |
| FR-21, FR-23, FR-11 | Installation, À propos | Flux 5 |
| FR-4 | Historique | **aucun** |
| FR-14, FR-15, FR-17 | Courrier type, Résumé, Correction | **aucun** |
| FR-19 | Retour | Flux 1 (pouce haut seulement) |
| FR-20 | Paramètres › Export | **aucun** |
| FR-10 (forçage) | Indicateur de Mode, Paramètres | **aucun** |
| FR-12 | Carte de source « Page consultée » | **aucun**, déclencheur indéfini |
| FR-22 | Désinstallation | règle seulement, pas de flux |

### Constats
- **haut** Aucun flux pour l'Historique (rouvrir, supprimer, annuler) ni pour l'export des Retours (aperçu anonymisé, enregistrement). Ce sont deux engagements de confidentialité vérifiables (FR-4, FR-20). (EXPERIENCE.md › Key Flows). *Correction :* ajouter un flux « Historique et export des Retours ». *Statut :* corrigé
- **moyen** Aucun flux pour Correction, Résumé et Courrier type (Tâches J5, premières coupées selon §9.3). *Correction :* ajouter au moins un flux Courrier type, qui a le comportement le plus spécifique (emplacements). *Statut :* corrigé
- **moyen** Flux 5 saute l'écran de bienvenue alors que c'est le premier lancement. *Correction :* l'insérer. *Statut :* corrigé
- **moyen** FR-12 (vérification en ligne) : on ne sait pas si l'Assistant vérifie de lui-même ou si l'Agent déclenche la vérification, ni ce qu'affiche la réponse. *Statut :* à trancher (décision produit ; FR-12 est le premier élément coupé).

## 2. Complétude des tokens — solide

Toutes les couleurs ont un hex. Le thème clair seul est une décision explicite. Toutes les références `{…}` de la prose se résolvent.

### Constats
- **bas** `{colors.warning}` (#FFCA4A) en bordure sur blanc fait environ 1,5:1. L'information est portée par le texte, donc c'est conforme, mais la bordure ne doit jamais être le seul signal. *Correction :* rien à changer, garder le texte toujours présent. *Statut :* sans objet
- **bas** L'anneau de focus de 2 px est cité dans EXPERIENCE.md mais sa largeur n'est pas un token. *Statut :* sans objet (valeur explicite suffisante)

## 3. Couverture des composants — mince

### Constats
- **haut** Composants utilisés sans spec visuelle dans DESIGN.md : carte de jeu de données, zone de saisie, encarts d'état (repli data.gouv en jaune, erreur en rouge), passage signalé (Langage clair), emplacement de Courrier type, boîte de dialogue, confirmation discrète (« Copié », « Merci, retour enregistré »). Un agent autonome inventera des couleurs, ce qui est interdit par « toute couleur inventée ». *Correction :* ajouter ces composants au YAML et à la prose, en n'utilisant que les tokens existants. *Statut :* corrigé
- **moyen** Le tableau de données a une spec visuelle mais pas de token YAML. *Correction :* l'ajouter. *Statut :* corrigé

## 4. Couverture des états — adéquate

### Constats
- **haut** Démarrage : « écran sobre » et « la saisie est possible » se contredisent (un écran qui masque la vue ou un bandeau ?). *Correction :* bandeau non bloquant dans la zone centrale, bouton Envoyer inactif avec libellé « Préparation… ». *Statut :* corrigé
- **moyen** Mode hors ligne forcé : le libellé de la pastille ne distingue pas « forcé » de « pas de réseau », et la persistance du réglage entre deux lancements n'est pas dite. Les deux réglages (menu de la pastille et Paramètres) doivent être un seul et même réglage. *Statut :* à trancher (persistance = choix de sécurité). La synchronisation des deux interrupteurs est corrigée.
- **moyen** Journal des Requêtes sortantes : état vide, durée de conservation et possibilité d'effacement non définis. *Correction :* état vide ajouté. *Statut :* à trancher pour la conservation.

## 5. Couverture des références visuelles — adéquate

Les deux maquettes sont citées dans DESIGN.md › Components et EXPERIENCE.md › IA, avec la règle « les spines priment ». Le contenu du dossier `mockups/` n'a pas été listé (consigne : ne pas lire les maquettes).

## 6. Surcharge et surspécification — solide

Pas de restatement significatif du PRD. La table Voice and Tone est utile. Rien à retirer.

## 7. Discipline d'héritage — adéquate

### Constats
- **haut** Contradiction avec FR-4 : le PRD exige une suppression **immédiate**, EXPERIENCE.md prévoit une annulation pendant 5 s sans dire si la donnée reste sur disque pendant ce délai. *Correction :* supprimer du disque tout de suite, garder la copie en mémoire 5 s pour « Annuler » qui la réécrit. Les deux exigences sont alors tenues. *Statut :* corrigé
- **haut** FR-14 : EXPERIENCE.md écrit « [Emplacement] » comme si c'était un libellé littéral. Le PRD veut des emplacements nommés (« [Nom de l'usager] »). *Correction :* préciser des emplacements nommés, détectés comme texte entre crochets. *Statut :* corrigé
- **moyen** FR-18 : « choix de la langue source et de la langue cible » permet anglais → espagnol, hors PRD (français d'un côté toujours). L'arabe demande un affichage de droite à gauche, non spécifié. *Correction :* sélecteur de sens + langue, `dir="rtl"` sur le volet arabe. *Statut :* corrigé
- **moyen** FR-3 : DESIGN.md › Message place l'avertissement juridique sous toute réponse, EXPERIENCE.md seulement sous les réponses de Question. *Correction :* préciser dans EXPERIENCE.md que la Recherche n'en porte pas. *Statut :* corrigé

## 8. Adéquation de forme — solide

Sections de DESIGN.md dans l'ordre canonique. Sections requises d'EXPERIENCE.md présentes ; « Installation et premier contact » et « Hors périmètre » méritent leur place.

## Ambiguïtés bloquantes pour un agent de développement autonome

- **critique** Forme des surfaces Journal, Paramètres et À propos non définie (boîte de dialogue, vue centrale ou panneau ?). Elle conditionne la règle « une seule boîte de dialogue à la fois » et le chemin Paramètres › À propos. *Correction :* Paramètres = boîte de dialogue à onglets (Général, Retours, À propos) ; Journal = boîte de dialogue avec tableau (Heure, Hôte, Termes envoyés, Statut). *Statut :* corrigé
- **haut** Cycle de vie de l'Historique : quand une entrée est créée, ce que fait la rouverture si la Tâche contient un travail en cours. *Correction :* entrée créée au premier envoi ou au premier traitement ; la rouverture bascule sur la Tâche d'origine et remplace son contenu (déjà sauvegardé s'il a été envoyé). *Statut :* corrigé
- **haut** Copie : ce que copie « Copier » en Correction (texte corrigé ou texte balisé ?) et en Langage clair (avec ou sans surlignage) ; comment copier le tableau de Flux 2 (aucune action définie). *Correction :* Copier copie toujours le texte brut sans marquage ; action « Copier le tableau » en texte tabulé avec la ligne de source. *Statut :* corrigé
- **moyen** Emplacement de « Nouvelle conversation » / « Effacer » et du bouton « Sources » non précisé ; « réponse sélectionnée » du panneau Sources non définie. *Correction :* boutons dans la barre supérieure ; par défaut la dernière réponse. *Statut :* corrigé
- **moyen** Export des Retours : format du fichier (JSON, CSV) et nom par défaut. *Statut :* à trancher (architecture).

## Corrections appliquées

- DESIGN.md : ajout au YAML et à la prose de `composer`, `dataset-card`, `data-table`, `callout-warning`, `callout-danger`, `flagged-passage`, `letter-placeholder`, `dialog`, `inline-confirmation` (tokens existants seulement).
- EXPERIENCE.md : forme du Journal et des Paramètres (boîtes de dialogue, onglet À propos), boutons de la barre supérieure, réponse sélectionnée du panneau Sources, cycle de vie de l'Historique, suppression conforme à FR-4, copie en texte brut et « Copier le tableau », emplacements nommés (FR-14), sélecteur de langue et arabe de droite à gauche (FR-18), avertissement juridique limité à Question, Régénérer, démarrage non bloquant, écran de bienvenue dans Flux 5, Flux 6 (Courrier type), Flux 7 (Historique et export des Retours).

## Notes mécaniques

- Noms de composants cohérents entre les deux fichiers pour ceux qui existent des deux côtés. « Carte de jeu de données », « Zone de saisie » et « Formulaire Courrier type » n'existaient que dans EXPERIENCE.md.
- Frontmatter `sources` d'EXPERIENCE.md résolu. DESIGN.md n'a pas de champ `sources` (bas).
- Aucun diagramme Mermaid.
