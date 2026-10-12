---
title: EXPERIENCE — Assistant IA local secteur public
status: final
created: 2026-10-11
updated: 2026-10-11
sources:
  - ../../prds/prd-service-public-slm-fine-tuning-2026-10-11/prd.md
---

# Assistant IA local — spécification d'expérience

Les termes avec majuscule (Agent, Assistant, Tâche, Index local, Source officielle, Liste blanche, Mode hors ligne, Mode connecté, Requête sortante, Retour) sont définis dans le glossaire du PRD (§3).

## Foundation

**Plateforme.**
- Application de bureau Windows 10/11 x64.
- Une seule fenêtre, sans compte utilisateur.
- Le Mode hors ligne est l'état par défaut et suffit à toutes les Tâches, sauf la recherche fraîche de données (voir NFR-5 du PRD).

**Technologie et références.**
- La technologie d'interface est choisie par l'architecture. `[ASSUMPTION : interface web embarquée dans une coquille de bureau légère, compatible avec le budget RAM du PRD (NFR-1)]`
- Aucun système de composants tiers n'est imposé.
- La référence d'identité visuelle est `DESIGN.md`. Ce document décrit le comportement.

**Utilisateurs.** Agents publics peu technophiles, souvent devant un Usager, parfois sur un poste partagé. L'interface doit être utilisable sans formation : une Tâche, un champ, un résultat.

## Information Architecture

Références de composition : `mockups/question.html` (Flux 1) et `mockups/compte-rendu.html` (Flux 3). En cas de conflit, les spines priment.

| Surface | Atteinte depuis | Rôle |
|---|---|---|
| Écran de bienvenue | Premier lancement uniquement | Explique ce que fait l'Assistant, rappelle qu'il ne faut pas saisir de données personnelles et affiche l'avertissement juridique. Bouton « Commencer ». |
| Question (vue par défaut) | Lancement, colonne de gauche | Dialogue sourcé sur les démarches et les droits (FR-1, FR-3, FR-5). |
| Recherche de données | Colonne de gauche | Dialogue avec les outils data.gouv. Les résultats s'affichent en cartes de jeux de données ou en tableaux (FR-7, FR-8). |
| Compte rendu | Colonne de gauche | Vue de rédaction : notes à gauche, compte rendu à droite (FR-13). |
| Langage clair | Colonne de gauche | Vue de rédaction avec les passages non simplifiés signalés (FR-16). |
| Plus › Correction | Colonne de gauche, section repliable « Plus » | Vue de rédaction ; le résultat montre les différences (FR-17). |
| Plus › Résumé | idem | Vue de rédaction avec un choix de longueur : courte, moyenne ou détaillée (FR-15). |
| Plus › Courrier type | idem | Formulaire court (type de courrier, objet, éléments connus), puis le courrier en Résultat (FR-14). |
| Plus › Traduction | idem | Vue de rédaction avec choix de la langue source et de la langue cible (FR-18). |
| Panneau Sources | Clic sur une puce de citation, ou bouton « Sources » | Détail des Sources officielles de la réponse sélectionnée (FR-3, FR-5, FR-6). |
| Historique | Colonne de gauche, sous les Tâches | Liste des conversations et des rédactions passées, avec rouverture et suppression (FR-4). |
| Journal des Requêtes sortantes | Clic sur l'indicateur de Mode › « Voir ce qui a été envoyé » | Boîte de dialogue (`dialog`) contenant un tableau, le plus récent en haut. Colonnes : Heure, Hôte, Termes envoyés, Statut (« Envoyé », « Échec », « Bloqué »). État vide : « Aucune requête n'a quitté ce poste. » (FR-38). |
| Paramètres | Icône engrenage en bas de la colonne de gauche | Boîte de dialogue à trois onglets. **Général** : Rester hors ligne (même réglage que dans le menu de l'indicateur de Mode, synchronisé), taille du texte, « Effacer tout l'historique » (annulable 5 s, comme une suppression unitaire). **Retours** : export (FR-20). **À propos** (FR-10, FR-20, FR-23). |
| À propos | Onglet de Paramètres | Versions, date de l'Index local, Liste blanche, licences, avertissement juridique, lien « Revoir l'écran de bienvenue » (FR-23). |

**Règles de navigation.**
- Changer de Tâche conserve le travail en cours de la Tâche quittée pendant toute la session.
- « Nouvelle conversation » (Question, Recherche) et « Effacer » (vues de rédaction) remettent la Tâche à zéro. Ce bouton secondaire est dans la barre supérieure, à droite du titre de la Tâche. Le bouton « Sources » est dans la même barre, à gauche de l'indicateur de Mode, et n'apparaît que si la conversation contient au moins une réponse citée.
- Une seule boîte de dialogue à la fois. Le panneau Sources n'est pas une boîte de dialogue : il reste ouvert pendant que l'Agent continue.
- **Réponse sélectionnée** (panneau Sources) : la réponse dont l'Agent a cliqué une puce ; à défaut, la dernière réponse citée. Une nouvelle réponse met à jour le panneau ouvert.
- **Cycle de vie de l'Historique.** Une entrée est créée au premier envoi (Question, Recherche) ou au premier traitement (vues de rédaction), puis mise à jour à chaque échange. Rouvrir une entrée active sa Tâche d'origine et remplace le contenu affiché ; le travail remplacé est déjà dans l'Historique s'il a été envoyé, sinon il est perdu sans confirmation (texte jamais envoyé = brouillon).

## Voice and Tone

Ce document décrit les textes de l'interface. La posture de marque est décrite dans `DESIGN.md` (Brand & Style).

**Principes.**
- **Adresse.** Vouvoiement, phrases courtes.
- **Vocabulaire.** Aucun jargon d'IA dans l'interface. Les mots modèle, tokens, RAG, LLM, prompt et inférence sont exclus.
- **Limites.** L'Assistant dit ses limites franchement, sans s'excuser à répétition.

| À faire | À ne pas faire |
|---|---|
| « Je n'ai pas trouvé de source officielle sur ce point. Le service autonomie de votre département pourra répondre. » | « Désolé, je ne peux pas répondre à cette question. » |
| « Hors ligne : je réponds à partir des documents officiels installés sur ce poste (mis à jour le 3 oct. 2026). » | « Mode dégradé : RAG local uniquement. » |
| « data.gouv ne répond pas. Voici ce que je trouve dans le catalogue installé, sans les chiffres à jour. » | « Erreur MCP : timeout. » |
| « Collez vos notes de réunion. Je produis un compte rendu sans rien ajouter. » | « Entrez votre prompt. » |
| « Traduction automatique, à vérifier avant envoi. » | « Traduction générée par IA ✨ » |
| « Ne vaut pas avis juridique. » | Un paragraphe de clauses de non-responsabilité |

**Mentions fixes**
- **Avertissement juridique** : « Ne vaut pas avis juridique. » Il figure sous chaque réponse de la Tâche Question.
- **Transparence** : la première ligne de l'écran de bienvenue dit « Cet assistant utilise l'intelligence artificielle. Ses réponses peuvent contenir des erreurs : vérifiez les sources citées. »
- **Données personnelles** : sur l'écran de bienvenue et dans la zone de saisie vide, « N'indiquez pas de nom, de numéro de sécurité sociale ou d'autre donnée personnelle. »

## Component Patterns

Ce document décrit le comportement des composants. Leur aspect visuel est décrit dans `DESIGN.md` (Components).

| Composant | Où | Règles de comportement |
|---|---|---|
| Navigation des Tâches | Colonne de gauche | Un clic active la Tâche. « Plus » se replie et se déplie, et son état est mémorisé. La Tâche active est annoncée au lecteur d'écran. |
| Zone de saisie (dialogue) | Question, Recherche | Champ multiligne. Entrée envoie, Maj+Entrée passe à la ligne. Le bouton Envoyer est inactif si le champ est vide. Pendant la génération, il devient « Arrêter ». |
| Réponse de l'Assistant | Question, Recherche | Elle s'affiche au fil de l'eau. Les puces de citation et les actions n'apparaissent qu'à la fin de la génération. Une réponse arrêtée par l'Agent porte la mention « Réponse interrompue ». L'avertissement juridique n'apparaît que sous les réponses de la Tâche Question (FR-3), pas en Recherche. « Régénérer » remplace la dernière réponse sur place, sans garder l'ancienne. |
| Puce de citation | Sous une réponse | Elle ouvre le panneau Sources sur la source correspondante. Le numéro de la puce correspond aux renvois [1], [2] du texte. Une puce ne peut exister sans source réelle (FR-3). |
| Panneau Sources | À droite | Il liste les sources de la réponse sélectionnée. Chaque carte affiche l'origine, la date, l'extrait dépliable et un bouton « Ouvrir ». En Mode hors ligne, « Ouvrir » copie le lien et affiche « Lien copié. Il s'ouvrira quand vous serez connecté. » Le panneau se ferme par Échap ou par le bouton ×. |
| Indicateur de Mode | Barre supérieure | Il affiche « Hors ligne » ou « Connecté ». Un clic ouvre un menu court avec trois éléments : la phrase d'explication, l'interrupteur « Rester hors ligne » et le lien « Voir ce qui a été envoyé ». Un changement de Mode est annoncé discrètement, une seule fois. |
| Carte de jeu de données | Recherche | Elle affiche le titre, le producteur, la date de mise à jour et le lien. L'action « Voir les données » est présente en Mode connecté seulement. Elle produit un tableau, sous la carte, plafonné à 50 lignes, avec la mention « Extrait : 50 premières lignes ». Sous le tableau, l'action « Copier le tableau » copie les lignes en texte tabulé (collable dans Excel ou Word), suivi de la ligne de source. |
| Vue de rédaction | Compte rendu, Langage clair, Correction, Résumé, Traduction | Le volet Entrée accepte le collage et la saisie, et affiche un compteur de mots. Le bouton principal « Rédiger » (ou « Réécrire », « Corriger », « Résumer », « Traduire ») lance le traitement. Le Résultat s'affiche au fil de l'eau dans le volet de droite. Un seul bouton principal est visible à la fois : « Rédiger » avant la génération, puis « Copier » après. |
| Barre d'actions du Résultat | Vues de rédaction | Elle propose quatre actions : Copier (principale, avec la confirmation « Copié »), Régénérer, Affiner et le Retour (pouce haut ou bas). Affiner ouvre un champ court (« Plus court », « Plus formel »…) qui retraite le Résultat existant. **Copier copie toujours le texte brut final, sans marquage** : en Correction, le texte corrigé sans les différences ; en Langage clair, sans surlignage ; en Courrier type, avec les emplacements entre crochets. |
| Passages signalés | Langage clair | Les passages laissés tels quels par prudence sont marqués (`flagged-passage`) dans le Résultat, avec une infobulle au survol et au focus : « Terme juridique conservé tel quel ». |
| Formulaire Courrier type | Courrier type | Il comporte un sélecteur de type (accusé de réception, demande de pièces, convocation, réponse d'information), un champ Objet et un champ « Éléments connus ». Chaque information manquante apparaît dans le courrier comme un emplacement nommé entre crochets, par exemple « [Nom de l'usager] » ou « [Date du rendez-vous] », jamais comme une valeur inventée (FR-14). Tout texte entre crochets du Résultat est affiché en `letter-placeholder`. |
| Sélecteur de langue | Traduction | Le français est toujours d'un côté. L'Agent choisit le sens (« Du français vers… » ou « Vers le français depuis… ») puis la langue : anglais, espagnol, arabe, portugais, allemand (FR-18). Le volet qui contient de l'arabe s'affiche de droite à gauche. |
| Retour | Sous chaque réponse ou résultat | Le pouce haut est enregistré immédiatement. Le pouce bas ouvre un champ facultatif « Qu'est-ce qui n'allait pas ? ». La confirmation est discrète : « Merci, retour enregistré sur ce poste ». |
| Historique | Colonne de gauche | Les entrées sont groupées par jour et titrées automatiquement avec les premiers mots. Le survol et le focus font apparaître « Supprimer ». La suppression se fait sans confirmation et efface l'entrée du disque immédiatement (FR-4). Une copie reste en mémoire 5 s : « Annuler » la réécrit ; passé ce délai, elle est détruite. |
| Taille du texte | Paramètres, Ctrl + / Ctrl − / Ctrl 0 | Cinq crans : 100, 112, 125, 137 et 150 %. Le réglage est mémorisé. Le changement s'applique immédiatement à toute l'interface. |

## State Patterns

| État | Surface | Traitement |
|---|---|---|
| Premier lancement | Global | L'écran de bienvenue s'affiche une seule fois. Il est consultable ensuite depuis À propos. |
| Démarrage, chargement du modèle | Global | Pas d'écran masquant : la vue s'affiche normalement, avec un bandeau discret en haut de la zone centrale, « Préparation de l'assistant… ». La saisie est possible ; le bouton Envoyer est inactif et libellé « Préparation… » jusqu'à la fin du chargement, puis le bandeau disparaît. La cible est inférieure à 10 s. `[ASSUMPTION : durée réelle à mesurer]` |
| Question vide | Question | Titre de bienvenue, puis trois exemples de questions cliquables, par exemple « Quelles pièces pour une demande d'APA ? ». Le rappel sur les données personnelles s'affiche dans le champ. |
| Génération en cours | Toutes | Le texte apparaît progressivement. Une animation discrète « … » s'affiche avant le premier mot. Le bouton « Arrêter » est disponible. |
| Aucune source trouvée | Question | L'Assistant répond qu'il n'a pas trouvé de Source officielle et oriente vers un service. Aucune puce de citation n'est affichée. Ce n'est pas un état d'erreur. |
| Mode hors ligne | Global | Pastille grise « Hors ligne ». Aucun bandeau d'alerte. Dans la Recherche de données, une ligne d'information sous le titre indique : « Hors ligne : catalogue installé uniquement, sans chiffres à jour. » |
| Repli data.gouv (délai dépassé ou erreur) | Recherche | La réponse est précédée d'un encart bordé de jaune : « data.gouv ne répond pas. Réponse établie à partir du catalogue installé. » Il propose une action « Réessayer ». |
| Valeurs demandées hors ligne | Recherche | L'Assistant indique que les valeurs ne sont disponibles qu'en Mode connecté et donne le lien de la ressource (FR-8). |
| Hôte bloqué (hors Liste blanche) | Global | Rien n'est affiché pendant l'échange. L'évènement est inscrit au journal des Requêtes sortantes avec le statut « Bloqué ». |
| Entrée trop longue | Vues de rédaction | Au-delà de la capacité, un message s'affiche : « Texte long : je le traite en plusieurs parties. » Une progression « Partie 2 sur 4 » suit, puis le Résultat fusionné (FR-13). |
| Erreur interne | Toutes | Encart bordé de rouge : « Un problème est survenu. Votre texte est conservé. » L'action « Réessayer » est proposée. Aucun code technique n'est affiché. Le détail technique va dans un fichier journal local. |
| Historique vide | Colonne de gauche | « Vos conversations apparaîtront ici. Elles restent sur ce poste. » |
| Export des Retours | Paramètres | L'aperçu du fichier anonymisé s'affiche avant l'enregistrement. Les éléments masqués apparaissent sous la forme [masqué]. Bouton « Enregistrer le fichier ». Aucun envoi automatique (FR-20). |

## Interaction Primitives

La souris et le clavier sont à égalité. Les agents utilisent surtout la souris, mais le clavier doit tout permettre (RGAA).

**Raccourcis clavier**

| Raccourci | Action |
|---|---|
| `Entrée` | Envoyer |
| `Maj+Entrée` | Nouvelle ligne |
| `Ctrl+N` | Nouvelle conversation ou effacer la rédaction |
| `Ctrl+1` à `Ctrl+4` | Tâches prioritaires |
| `Ctrl+Maj+C` | Copier le dernier résultat |
| `Échap` | Fermer le panneau ou la boîte de dialogue, ou arrêter la génération si le focus est sur la réponse |
| `Ctrl +` / `Ctrl −` / `Ctrl 0` | Taille du texte |

- **Copier-coller.** C'est le geste principal des vues de rédaction. Le collage conserve le texte brut et ignore la mise en forme.
- **Exclus.** Pas de glisser-déposer de fichiers en v1, pas d'ouverture de documents Word ou PDF, pas de notifications système, pas de son.

## Accessibility Floor

Ce document fixe les exigences de comportement. Les contrastes sont définis dans `DESIGN.md` : texte en ink et ink-soft sur blanc, jamais de vert en texte.

- **Critères RGAA vérifiés en v1 (NFR-7)** :
  - navigation complète au clavier ;
  - contraste d'au moins 4,5:1 ;
  - libellés accessibles sur tous les contrôles.
- **Ordre de tabulation** : colonne de gauche, puis barre supérieure, puis zone centrale, puis panneau Sources. Le focus est toujours visible (anneau violet de 2 px).
- **Lecteur d'écran.**
  - La réponse en cours est annoncée par une région `aria-live` polie, une fois la génération terminée, et non mot à mot.
  - Les puces de citation sont lues sous la forme « Source 1 : titre ».
  - Le changement de Mode est annoncé.
- **Information jamais portée par la seule couleur** : Mode (libellé), différences de correction (barré, souligné), passages signalés (infobulle et marque).
- **Taille du texte** : réglable de 100 à 150 % sans perte de contenu ni défilement horizontal dans une fenêtre de 1024×640.
- **Animations** : aucune n'est indispensable. Le réglage Windows « Réduire les animations » est respecté.

## Responsive & Platform

| Largeur de fenêtre | Comportement |
|---|---|
| 1 280 px et plus | Trois colonnes. Le panneau Sources pousse la zone centrale. |
| 1 024 à 1 279 px | Le panneau Sources recouvre la zone centrale. Dans les vues de rédaction, les volets s'empilent sous 1 200 px. |
| Moins de 1 024 px | Non visé. La colonne de gauche se réduit aux icônes. |

**Comportement Windows**
- Une seule instance de l'application.
- La fenêtre mémorise sa taille et sa position.
- Le raccourci du menu Démarrer est créé par l'installateur.
- Il n'y a pas d'icône dans la zone de notification en v1.

## Installation et premier contact

L'installation fait partie de l'expérience (UJ-5).

- **Installateur sans droits administrateur**, en trois écrans au plus : bienvenue et licence, dossier (profil utilisateur par défaut), progression.
- **Fin d'installation** : une case « Lancer l'assistant » est cochée par défaut.
- **Aucun téléchargement pendant ou après l'installation.** Le premier lancement fonctionne débranché.
- **Désinstallation** : une seule question, « Conserver l'historique et les retours sur ce poste ? », avec Oui ou Non.

## Inspiration & Anti-patterns

**Repris**
- Des assistants conversationnels grand public : le dialogue au fil de l'eau, les citations numérotées et le bouton Arrêter.
- Des outils de correction : les différences visibles et la copie en un clic.

**Rejetés**
- **Les suggestions proactives** et les messages « Vous pourriez aussi demander… » après chaque réponse : l'Agent est devant un Usager, chaque élément en trop distrait.
- **Les avatars, personnages et emojis.** L'Assistant n'a pas de personnalité affichée, c'est un outil.
- **Le « Mode hors ligne » présenté comme une panne.** C'est le fonctionnement nominal.
- **Les réglages techniques exposés à l'Agent** : température, choix du modèle, taille de contexte.
- **Les confirmations en cascade** (« Êtes-vous sûr ? »). On leur préfère l'annulation pendant 5 s.

## Key Flows

Les identifiants UJ-n renvoient aux parcours du PRD (§2.3).

### Flux 1 : Nadia répond à une usagère sur l'APA, sans réseau (UJ-1)

1. Nadia ouvre l'Assistant depuis le menu Démarrer. La vue Question s'affiche et la pastille indique « Hors ligne ».
2. Elle tape : « Ma mère de 82 ans peut-elle avoir l'APA à domicile ? Quelles pièces ? » puis Entrée.
3. Le texte de la réponse commence en moins de 5 s et s'affiche au fil de l'eau.
4. **Point culminant** : la réponse se termine. Deux puces de citation apparaissent sous le texte, suivies de « Ne vaut pas avis juridique ». Nadia clique sur la puce 2. Le panneau Sources s'ouvre sur la fiche service-public.fr « Allocation personnalisée d'autonomie à domicile », avec l'extrait de la liste des pièces et la date « Documents installés le 3 oct. 2026 ». Elle tourne l'écran vers l'usagère.
5. Nadia clique sur le pouce haut. Le message « Merci, retour enregistré sur ce poste » s'affiche discrètement.

**Échec possible** : l'aide demandée est propre au département. L'Assistant répond : « Je n'ai pas trouvé de source officielle sur ce point. Le service autonomie de votre département pourra répondre. » Aucune puce de citation n'est affichée.

### Flux 2 : Thomas cherche des données sur les EHPAD (UJ-2)

1. Thomas clique sur « Recherche de données ». La pastille indique « Connecté ».
2. Il demande quels jeux de données donnent le nombre de places en EHPAD par commune.
3. Trois cartes de jeux de données s'affichent, avec producteur, date de mise à jour et lien.
4. Sur la première carte, il clique « Voir les données » et précise « pour la Gironde ».
5. **Point culminant** : un tableau de 50 lignes s'affiche sous la carte, avec en pied « Source : data.gouv.fr, [nom du jeu], consulté le 11 oct. 2026 ». Thomas copie le tableau.
6. Par curiosité, il ouvre le menu de la pastille, puis « Voir ce qui a été envoyé ». Il y lit trois lignes horodatées vers `mcp.data.gouv.fr`, avec les termes « places EHPAD commune » et l'identifiant du jeu. Sa phrase n'y figure pas en entier.

**Échec possible** : data.gouv ne répond pas. Un encart jaune annonce un repli sur le catalogue installé, sans tableau de valeurs, avec un bouton « Réessayer ».

### Flux 3 : Thomas transforme ses notes en compte rendu (UJ-3)

1. Thomas clique sur « Compte rendu » et colle ses notes dans le volet Entrée. Le compteur affiche 2 140 mots.
2. Il clique « Rédiger ».
3. Le compte rendu s'affiche au fil de l'eau dans le volet Résultat, en quatre sections : Participants, Points abordés, Décisions, Actions (responsable, échéance).
4. **Point culminant** : Thomas relit la section Décisions. Les trois décisions de ses notes y sont, et rien d'autre. Il clique « Copier » puis colle dans Word.
5. Il clique « Affiner », tape « plus court », et obtient une version resserrée.

**Échec possible** : la transcription fait 9 000 mots. Le message « Texte long : je le traite en plusieurs parties » s'affiche, suivi de « Partie 1 sur 3 », puis du compte rendu fusionné.

### Flux 4 : Nadia rend un courrier compréhensible puis le traduit (UJ-4)

1. Nadia clique sur « Langage clair » et colle un courrier de notification de droits.
2. Elle clique « Réécrire ».
3. **Point culminant** : le Résultat est court et simple. Les montants et les dates sont identiques. Une expression reste surlignée, avec l'infobulle « Terme juridique conservé tel quel ».
4. Nadia copie le Résultat, ouvre « Plus › Traduction », le colle et choisit « Arabe ».
5. La traduction s'affiche avec la mention « Traduction automatique, à vérifier avant envoi ».

### Flux 5 : Karim installe l'Assistant sur un poste verrouillé (UJ-5)

1. Karim lance l'installateur depuis un partage réseau. Aucune demande de droits administrateur n'apparaît.
2. Il traverse trois écrans, puis l'Assistant se lance.
3. Karim débranche le câble réseau. La pastille indique « Hors ligne » et une question test obtient une réponse sourcée.
4. **Point culminant** : dans Paramètres › À propos, il lit la Liste blanche (six hôtes) et la date de l'Index local. Il peut répondre à sa DSI sur ce que l'outil contacte.

Note : au premier lancement (étape 2), l'écran de bienvenue s'affiche d'abord ; Karim clique « Commencer » et arrive sur la vue Question.

### Flux 6 : Nadia prépare une convocation (FR-14)

1. Nadia ouvre « Plus › Courrier type », choisit « Convocation », saisit l'objet « Rendez-vous dossier APA » et, dans « Éléments connus », « mardi 14 h, apporter l'avis d'imposition ».
2. Elle clique « Rédiger ». Le courrier s'affiche au fil de l'eau au format administratif.
3. **Point culminant** : le nom de l'usager et son adresse, non fournis, apparaissent comme « [Nom de l'usager] » et « [Adresse] », mis en évidence. Rien n'est inventé.
4. Nadia clique « Copier » et complète les emplacements dans son traitement de texte.

**Échec possible** : les éléments sont trop maigres. Le courrier est quand même produit, avec davantage d'emplacements, sans message d'erreur.

### Flux 7 : Thomas fait le ménage et exporte ses Retours (FR-4, FR-20)

1. Dans l'Historique, Thomas survole une conversation et clique « Supprimer ». L'entrée disparaît ; « Annuler » reste proposé 5 s. Il laisse passer le délai.
2. Il ouvre Paramètres › Retours et clique « Exporter mes retours ».
3. **Point culminant** : l'aperçu montre ses 12 Retours ; un numéro de téléphone et un nom apparaissent comme [masqué].
4. Il clique « Enregistrer le fichier ». La boîte d'enregistrement Windows s'ouvre sur Documents. Il transmet le fichier lui-même.

**Échec possible** : aucun Retour enregistré. Le bouton est inactif, avec la mention « Vous n'avez encore donné aucun retour. »

## Hors périmètre UX v1

Les éléments suivants sont repoussés :
- le thème sombre (v2, selon le réglage de Windows) ;
- les interfaces en d'autres langues que le français ;
- l'import de fichiers Word ou PDF ;
- la transcription audio ;
- la mise à jour de l'Index local depuis l'interface.

L'interface d'Anaël pour l'évaluation et le Comparatif est hors du champ de l'Assistant. Ce sont des outils en ligne de commande et des rapports, définis par l'architecture.

## Décisions par défaut (issues de la revue, réversibles)

Ces réglages ont été tranchés par défaut le 12 octobre 2026. Anaël peut les remettre en cause au réveil.

- **FR-12, vérification en ligne.** Elle est déclenchée par l'Agent, jamais automatiquement.
  - Sous une réponse de la Tâche Question, en Mode connecté, un bouton secondaire « Vérifier en ligne » consulte la page officielle correspondante sur un hôte de la Liste blanche.
  - Le résultat s'affiche en encart sous la réponse : « Vérifié sur [titre de la page] le [date] : concordant » ou « Différence relevée : [phrase] ». La page est ajoutée aux sources.
  - Si la fonctionnalité est coupée (§9.3 du PRD), le bouton n'existe pas.
- **Mode hors ligne forcé.** Le réglage est conservé d'un lancement à l'autre. La pastille affiche alors « Hors ligne (choisi) », pour le distinguer d'une absence de réseau.
- **Journal des Requêtes sortantes.** Il est conservé 30 jours glissants. Le bouton « Effacer le journal » se trouve dans Paramètres › Général.
- **Export des Retours.** Le fichier est enregistré sous `retours-assistant-AAAA-MM-JJ.json` et l'Agent choisit l'emplacement. L'architecture peut ajouter un CSV.
