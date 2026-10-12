---
title: PRD — Assistant IA local pour le secteur public français (SLM fine-tuné)
status: final
created: 2026-10-11
updated: 2026-10-11
---

# PRD : Assistant IA local pour le secteur public français
*Nom de travail, à confirmer.*

## 0. Objet du document

Ce PRD décline la note de cadrage du 11 octobre 2026 (`Note de cadrage — SLM secteur public français.md`, à la racine du projet), qui tient lieu de brief. Il s'adresse à Anaël, porteur du projet, et aux workflows BMAD en aval : UX, architecture, epics et stories, développement autonome.

**Organisation**
- Le vocabulaire est fixé par le glossaire (§3).
- Les exigences fonctionnelles sont groupées par fonctionnalité (§4) et numérotées globalement (FR-n). Ces numéros sont stables.
- Les hypothèses sont marquées `[ASSUMPTION]` et regroupées en §13.
- L'ordre de livraison et la règle d'arbitrage sont en §9.3. Les agents autonomes doivent les suivre.

**Documents associés**
- `addendum.md` : choix techniques, modèles candidats, outils MCP, benchmarks, méthodes, registre des risques, plan de réalisation.
- `research-*.md` : recherches de cadrage.
- `decisions.md` (dans `_bmad-output/planning-artifacts/`) : décisions pré-arbitrées pour le développement autonome, dont le budget d'API.

## 1. Vision

Un **Assistant** installé sur le PC bureautique d'un agent public répond hors ligne aux questions courantes sur les démarches, les droits et l'organisation administrative, en citant la **Source officielle**. Il aide aussi à rédiger : comptes rendus, courriers types, résumés, réécriture en langage clair, correction orthographique, traduction. Quand une connexion existe, il vérifie les données récentes auprès des sites officiels de la **Liste blanche**, dont data.gouv via son serveur MCP. Les textes et documents saisis par l'agent ne quittent jamais son poste. En Mode connecté, seules des **Requêtes sortantes** reformulées par le Harnais (termes de recherche, paramètres d'outil) partent vers la Liste blanche, et l'agent peut les consulter.

**Positionnement.** Toutes les offres de l'État en place fonctionnent dans le cloud (Assistant IA de l'État, Albert). Le créneau d'un outil **local, hors ligne, installable en un clic, spécialisé secteur public** est peu occupé `[ASSUMPTION : outils des collectivités et assistants locaux grand public non étudiés]`.

**Souveraineté.** L'exécution locale répond à la crainte des agents et des DSI de voir des données partir vers un fournisseur d'IA. Deux nuances encadrent cette promesse :
- l'ancrage culturel et réglementaire vient surtout de l'Index local (corpus officiels) et du fine-tuning sur des données françaises, pas du Modèle de base. Même un modèle d'éditeur français comme Ministral ne publie pas son corpus ;
- l'auditabilité est partielle. Un Modèle de base aux données entièrement ouvertes permet de tracer les sources et de contrôler la contamination, mais un audit exhaustif de son préentraînement reste hors de portée.

**Deux objectifs, un ordre.** Le premier objectif est le produit : un Assistant utile aux agents. Le second est un **Comparatif** rigoureux de plusieurs **Méthodes de fine-tuning** : gain de précision et coût d'entraînement sur un GPU grand public (RTX 3050, 8 Go). Il mesure aussi les Modèles fine-tunés sur des **Benchmarks standardisés** publics, et c'est un livrable présentable à des clients. La motivation de fond est la montée en compétence de bout en bout (données, fine-tuning, évaluation, packaging).

En cas de conflit de temps ou de moyens, **le banc d'évaluation et le Comparatif passent avant l'application packagée** (§9.3). Le projet commence par un démonstrateur et vise un déploiement réel si les Retours d'agents confirment le besoin.

## 2. Utilisateurs cibles

### 2.1 Jobs To Be Done
- **Agent d'accueil ou d'action sociale** : répondre vite et juste à un Usager sur ses droits et démarches, avec une source qu'il peut montrer, sans chercher dans dix sites. Être rassuré de ne rien envoyer à l'extérieur.
- **Chargé de mission ou assistante de direction** :
  - produire en quelques minutes un compte rendu, un courrier type ou un résumé présentable ;
  - rendre un texte administratif compréhensible ;
  - trouver un jeu de données public pertinent sans connaître data.gouv.
- **Agent dont l'Usager lit mal le français** : traduire un message ou un courrier simple dans une langue courante.
- **Anaël, porteur et consultant** :
  - monter en compétence de bout en bout ;
  - disposer d'un Comparatif chiffré et reproductible, présentable à des clients ;
  - montrer un démonstrateur crédible à une collectivité.
- **DSI d'une collectivité** : autoriser un outil d'IA sans ouvrir de flux vers un fournisseur d'IA et sans droits administrateur, en sachant exactement quels domaines il contacte.

### 2.2 Non-utilisateurs (v1)
- **Usagers** : l'Assistant sert l'Agent, pas l'Usager.
- **Juristes en quête d'avis engageant** : l'Assistant ne donne pas d'avis juridique engageant.
- **Agents qui traitent des dossiers nominatifs** : le traitement de données personnelles est hors périmètre.

### 2.3 Parcours utilisateurs clés

- **UJ-1. Nadia répond à une usagère sur l'APA, sans réseau.**
  Nadia est agente d'accueil dans une maison départementale des solidarités. La salle d'accueil n'a pas de Wi-Fi fiable. Une usagère demande si sa mère peut obtenir l'APA à domicile, et quelles pièces fournir.
  - Nadia ouvre l'Assistant depuis le menu Démarrer. Aucun compte n'est demandé, et l'indicateur affiche « Hors ligne ».
  - Elle tape sa question en langage courant.
  - En moins de 5 secondes, la réponse commence à s'afficher : conditions et liste des pièces, avec deux liens vers des fiches service-public.fr tirées de l'**Index local**, et la mention « Ne vaut pas avis juridique ».
  - Nadia montre la liste à l'usagère.
  - **Cas limite** : la question porte sur une aide propre au département, absente de l'Index local. L'Assistant dit qu'il ne trouve pas de Source officielle et oriente vers le service compétent.

- **UJ-2. Thomas cherche des données sur les EHPAD de son département.**
  Thomas est chargé de mission, connecté au réseau de la collectivité.
  - Il demande quels jeux de données donnent le nombre de places en EHPAD par commune.
  - En **Mode connecté**, le Harnais reformule la demande en termes de recherche (« places EHPAD commune ») et interroge le serveur MCP de data.gouv. L'Assistant présente trois jeux de données, avec producteur, date de mise à jour et lien.
  - Thomas demande un extrait pour son département et obtient un tableau sourcé.
  - Il peut ouvrir le journal des Requêtes sortantes et voir exactement ce qui a été envoyé.
  - **Cas limite** : le serveur MCP ne répond pas dans le délai. L'Assistant le signale, répond à partir du catalogue data.gouv de l'Index local (sans valeurs fraîches) et propose de réessayer.

- **UJ-3. Thomas transforme ses notes de réunion en compte rendu.**
  - Thomas colle les notes en vrac d'un comité de pilotage et choisit la Tâche « Compte rendu ».
  - Il obtient un compte rendu structuré : participants, points abordés, décisions, actions avec responsable et échéance.
  - Toutes les décisions de ses notes y figurent, et aucune n'est inventée. Thomas corrige deux noms et copie le texte dans Word.

- **UJ-4. Nadia rend un courrier compréhensible et le traduit.**
  - Nadia colle un courrier de notification de droits et choisit « Langage clair ».
  - Elle obtient une version simple. Le sens, les montants et les dates sont inchangés, et les passages non simplifiés par prudence sont signalés.
  - Elle demande ensuite la version arabe pour la famille, avec la mention « Traduction automatique, à vérifier ».

- **UJ-5. Karim, technicien informatique, installe l'Assistant sur un poste verrouillé.**
  - Karim lance l'installateur sans droits administrateur. L'installation se fait dans le profil utilisateur.
  - Le premier lancement fonctionne hors ligne.
  - Dans « À propos », Karim vérifie la liste exacte des hôtes que l'Assistant peut contacter.

- **UJ-6. Anaël compare quatre méthodes de fine-tuning et publie le Comparatif.**
  - Anaël lance la campagne sur sa RTX 3050. Chaque **Run d'entraînement** enregistre durée, débit, VRAM maximale et énergie.
  - Chaque modèle est évalué automatiquement sur le **Jeu d'évaluation maison** et sur les Benchmarks standardisés, avant et après quantification.
  - Le Comparatif sort sous forme de rapport. Anaël relit l'échantillon marqué pour relecture humaine, choisit le Modèle embarqué et publie la fiche modèle.

## 3. Glossaire

- **Agent** : agent public qui utilise l'Assistant. Distinct de l'Usager.
- **Usager** : personne servie par l'Agent. Elle n'utilise jamais l'Assistant.
- **Assistant** : application installée sur le PC cible. Elle regroupe le Modèle embarqué, l'Index local et le Harnais.
- **Harnais** : logique applicative autour du modèle. Il gère :
  - le prompt système par Tâche ;
  - la recherche dans l'Index local ;
  - l'appel des outils ;
  - le choix du Mode ;
  - la formulation des Requêtes sortantes ;
  - la mise en forme des sources.
- **Modèle de base** : petit modèle open-weight pris tel quel. Les modèles candidats sont listés dans l'addendum §C.
- **Modèle fine-tuné** : Modèle de base adapté par une Méthode de fine-tuning.
- **Modèle embarqué** : le modèle retenu et quantifié, livré dans l'Assistant. Il peut s'agir d'un Modèle de base si la Baseline gagne.
- **Baseline** : Modèle de base + Index local + prompt système, sans entraînement. C'est la référence que tout Modèle fine-tuné doit battre. Ses faiblesses désignent ce que les Données d'entraînement doivent corriger.
- **Index local** : corpus officiel découpé et vectorisé, embarqué dans l'Assistant. Il est issu de MediaTech (DINUM).
- **Source officielle** : document issu de l'Index local, d'une réponse d'outil MCP ou d'une page d'un hôte de la Liste blanche, cité avec titre et lien.
- **Liste blanche** : liste configurable des seuls hôtes que l'Assistant peut contacter. La correspondance se fait sur le nom d'hôte exact.
- **Requête sortante** : toute requête réseau émise par l'Assistant. Elle ne contient que des termes de recherche et des paramètres d'outil formulés par le Harnais, et elle est inscrite au journal local.
- **Mode hors ligne** : aucun accès réseau. Seuls l'Index local et le Modèle embarqué sont utilisés.
- **Mode connecté** : accès aux hôtes de la Liste blanche, dont le serveur MCP data.gouv.
- **Tâche** : type de travail demandé.
  - **Prioritaires** : Question, Recherche de données, Compte rendu, Langage clair.
  - **Secondaires** : Correction, Résumé, Courrier type, Traduction.
- **Jeu d'évaluation maison** : jeu de test figé, construit avant toute génération de données et jamais utilisé pour l'entraînement.
- **Grille du Juge** : barème versionné, par Tâche, que le Juge applique.
- **Juge** : grand modèle qui note des réponses selon la Grille du Juge, avec relecture humaine sur un échantillon.
- **Bac à sable MCP** : réponses enregistrées des outils MCP data.gouv, rejouables à l'identique. Il est utilisé pour l'évaluation et pour la validation des Données d'entraînement.
- **Outil d'évaluation** : logiciel public qui exécute les Benchmarks standardisés, par exemple lm-evaluation-harness. Distinct du Harnais.
- **Benchmark standardisé** : jeu d'évaluation public, téléchargeable depuis Hugging Face ou GitHub.
- **Données d'entraînement** : exemples générés ou rejoués qui servent au fine-tuning. Ils sont versionnés et tracés dans le Registre des licences.
- **Registre des licences** : inventaire des jeux de données utilisés, avec leur licence, leurs obligations et leur usage autorisé.
- **Méthode de fine-tuning** : technique d'adaptation des poids (QLoRA, LoRA, DoRA, ORPO…).
- **Run d'entraînement** : une exécution d'une Méthode de fine-tuning sur un Modèle de base, avec configuration, graine et mesures enregistrées.
- **Comparatif** : livrable qui compare les Méthodes de fine-tuning en précision et en coût.
- **Score de Tâche** : note de 0 à 100 d'un modèle sur une Tâche du Jeu d'évaluation maison. Son calcul est défini en §10.1.
- **Retour** : avis d'un Agent sur une réponse (pouce haut ou bas, commentaire facultatif).
- **PC cible** : poste Windows 10/11 x64, 16 Go de RAM, sans GPU dédié.

## 4. Fonctionnalités

Les fonctionnalités sont présentées par domaine. L'ordre de livraison est fixé en §9.3.

### 4.1 Assistant conversationnel local
**Description.** L'Agent ouvre l'Assistant, choisit éventuellement une Tâche (par défaut : Question) et dialogue en français. Les réponses s'affichent au fil de l'eau. Réalise UJ-1 à UJ-4.

#### FR-1 : Dialogue en français
L'Agent peut poser une question ou donner une consigne en langage courant, et poursuivre par des questions de suivi.
- La réponse s'affiche token par token.
- Une question de suivi tient compte des échanges précédents de la conversation.
- « Nouvelle conversation » vide le contexte.

#### FR-2 : Sélection de la Tâche
L'Agent peut choisir explicitement une Tâche.
- Chaque Tâche applique son prompt système et son format de sortie.
- Sans choix, la demande est traitée comme une Question.

#### FR-3 : Citation des sources et avertissement
L'Assistant cite les Sources officielles utilisées. Toute réponse de la Tâche Question affiche « Ne vaut pas avis juridique ».
- Chaque URL citée figure dans les passages de l'Index local retrouvés ou dans une réponse d'outil de la conversation. C'est vérifié automatiquement : aucune URL n'est inventée.
- Sans Source officielle pertinente, l'Assistant le dit et oriente vers un service ou un site officiel.

#### FR-4 : Historique local
L'Agent retrouve ses conversations, stockées uniquement dans son profil Windows, et peut les supprimer.
- Il n'y a aucune synchronisation.
- La suppression est immédiate.

### 4.2 Questions sur les démarches et les droits (Tâche prioritaire 1)
**Description.** Les réponses s'appuient sur l'Index local construit à partir de MediaTech : service-public et catalogue data.gouv au minimum, LEGI, travail-emploi, CNIL et Constitution selon la RAM disponible (NFR-1). Réalise UJ-1.

#### FR-5 : Réponse fondée sur l'Index local
L'Assistant retrouve les passages pertinents de l'Index local et construit sa réponse à partir d'eux, dans les deux Modes.
- La réponse est produite avec la carte réseau désactivée.
- L'Agent peut déplier chaque source pour voir l'extrait utilisé.

#### FR-6 : Date de fraîcheur de l'Index local
La date de constitution de l'Index local apparaît dans « À propos » et dans le détail de chaque source qui en provient.

### 4.3 Recherche de données publiques (Tâche prioritaire 2)
**Description.** En Mode connecté, l'Assistant utilise un sous-ensemble réduit des outils du serveur MCP officiel de data.gouv (5 outils au plus, schémas simples, liste dans l'addendum §B). En Mode hors ligne, il s'appuie sur le catalogue data.gouv de l'Index local. Réalise UJ-2.

#### FR-7 : Recherche et description de jeux de données
L'Agent peut demander quels jeux de données répondent à un besoin. L'Assistant renvoie les jeux pertinents, avec titre, producteur, date de mise à jour et lien.
- Les appels d'outils sont générés sous contrainte du schéma JSON de l'outil. Un appel non conforme n'est jamais envoyé.
- Chaque jeu présenté provient d'une réponse d'outil ou de l'Index local.

#### FR-8 : Interrogation d'une ressource
En Mode connecté, l'Agent peut demander des valeurs d'une ressource tabulaire. L'Assistant les affiche dans un tableau sourcé.
- Les valeurs affichées sont identiques à celles renvoyées par l'outil.
- En Mode hors ligne, l'Assistant indique que les valeurs ne sont disponibles qu'en Mode connecté et donne le lien de la ressource s'il le connaît.

#### FR-9 : Repli en cas d'indisponibilité
Si un appel MCP échoue ou dépasse le délai, l'Assistant le signale et répond à partir de l'Index local.
- Le délai est configurable, `[ASSUMPTION : 10 s par défaut]`.
- Le message précise que les données n'ont pas été vérifiées en ligne.

### 4.4 Modes, Liste blanche, Requêtes sortantes
**Description.** L'Assistant fonctionne d'abord hors ligne. Le Mode connecté n'ouvre l'accès qu'aux hôtes de la Liste blanche, avec des Requêtes sortantes minimales et journalisées. Réalise UJ-1, UJ-2 et UJ-5.

#### FR-10 : Détection et indicateur de mode
L'Agent voit en permanence le Mode courant et peut forcer le Mode hors ligne.
- Le Mode connecté est actif si la sonde `GET /health` du serveur MCP répond en moins de 3 s.
- La sonde est lancée au démarrage, toutes les 5 minutes et avant chaque appel d'outil.
- En cas d'échec ou de doute, l'Assistant reste en Mode hors ligne.
- En Mode hors ligne forcé, aucune requête réseau n'est émise. C'est vérifiable par capture réseau.

#### FR-11 : Liste blanche configurable
L'Assistant ne contacte que les hôtes de la Liste blanche, par correspondance exacte du nom d'hôte. La liste v1 est dans l'addendum §B. Elle couvre data.gouv (MCP et site), service-public.fr, legifrance.gouv.fr, entreprendre.service-public.fr et l'annuaire de l'administration.
- Une requête vers un hôte hors liste est bloquée et journalisée localement.
- La liste se modifie par fichier de configuration, sans recompilation, car elle est appelée à évoluer.
- La liste effective s'affiche dans « À propos ».

#### FR-12 : Vérification en ligne d'une page officielle (secondaire)
En Mode connecté, l'Assistant peut consulter une page d'un hôte de la Liste blanche pour vérifier une réponse issue de l'Index local, et la cite avec sa date de consultation.

#### FR-38 : Contenu et journal des Requêtes sortantes
Les Requêtes sortantes ne contiennent que des termes de recherche et des paramètres d'outil formulés par le Harnais. L'Agent peut consulter le journal local de toutes les Requêtes sortantes.
- Le texte collé par l'Agent pour une Tâche de rédaction (Compte rendu, Langage clair, Correction, Résumé, Courrier type, Traduction) ne déclenche jamais de Requête sortante.
- Test automatisé : un document témoin collé n'apparaît dans aucune Requête sortante journalisée.

### 4.5 Compte rendu (Tâche prioritaire 3)
**Description.** Un compte rendu structuré est produit à partir de notes ou d'une transcription. Réalise UJ-3.

#### FR-13 : Compte rendu
À partir de notes ou d'une transcription collées, l'Assistant produit un compte rendu avec participants, points abordés, décisions et actions (responsable, échéance).
- Couverture et absence d'invention sont mesurées par le Score de Tâche (§10.1).
- Une entrée d'au moins 6 000 mots est acceptée. Au-delà de la fenêtre de contexte du Modèle embarqué, le traitement par morceaux, suivi d'une fusion, est **obligatoire**.

### 4.6 Langage clair (Tâche prioritaire 4)
#### FR-16 : Réécriture en langage clair
L'Assistant réécrit un texte administratif en langage clair, en conservant le sens, les montants, les dates et les obligations. Réalise UJ-4.
- La lisibilité est mesurée par l'indice de Kandel-Moles. Sur le Jeu d'évaluation maison, le gain moyen est d'au moins 10 points.
- La fidélité est notée par le Juge (§10.1).
- Les passages non simplifiés par prudence, comme les termes juridiques obligatoires, sont signalés.

### 4.7 Tâches secondaires : correction, résumé, courrier type
#### FR-17 : Correction orthographique et grammaticale
L'Assistant corrige l'orthographe, la grammaire et la typographie d'un texte, et présente les corrections sous forme de différences visibles.
- Rappel des fautes et absence de modification hors faute : mesurés sur un jeu de textes à fautes injectées (§10.1).
- La version corrigée se copie en un clic.

#### FR-15 : Résumé
L'Agent fait résumer un document collé, en version courte, moyenne ou détaillée.
- Le Juge note la fidélité et la couverture (§10.1).

#### FR-14 : Courrier type
L'Agent demande un courrier administratif à partir d'un objet et de quelques éléments : accusé de réception, demande de pièces, convocation ou réponse d'information. L'Assistant le rédige au format administratif français.
- Chaque champ non fourni apparaît comme un emplacement explicite, par exemple « [Nom de l'usager] », jamais comme une valeur inventée. C'est vérifié automatiquement.

### 4.8 Traduction (secondaire)
#### FR-18 : Traduction
L'Agent traduit un texte vers ou depuis l'anglais, l'espagnol, l'arabe, le portugais ou l'allemand. La sortie porte la mention « Traduction automatique, à vérifier ». Réalise UJ-4.
- La qualité est mesurée par les Benchmarks standardisés de traduction (FR-27). Il n'y a pas de Jeu d'évaluation maison dédié en v1.
- L'arabe peut être retiré de la v1 si la Baseline le montre insuffisant.

### 4.9 Retours des Agents
#### FR-19 : Donner un Retour
L'Agent note chaque réponse (pouce haut ou bas) et peut ajouter un commentaire. Le Retour est stocké en local avec la Tâche, la question, la réponse et les sources.

#### FR-20 : Exporter les Retours
L'Agent exporte ses Retours dans un fichier anonymisé qu'il relit puis transmet lui-même.
- Aucune télémétrie automatique. Aucune Requête sortante n'est liée aux Retours.
- Les motifs suivants sont masqués :
  - NIR ;
  - adresse e-mail ;
  - numéro de téléphone ;
  - IBAN ;
  - adresse postale ;
  - noms de personnes, détectés par reconnaissance d'entités.
- Test : un export témoin qui contient chacun de ces motifs n'en contient plus aucun en clair.

### 4.10 Installation
#### FR-21 : Installation en un clic
Un utilisateur sans droits administrateur installe l'Assistant avec un seul installateur, qui inclut le Modèle embarqué et l'Index local. Réalise UJ-5.
- L'installation réussit sur un compte Windows standard.
- Le premier lancement fonctionne en Mode hors ligne, sans téléchargement complémentaire.

#### FR-22 : Désinstallation propre
L'Assistant se désinstalle sans droits administrateur et propose de conserver ou de supprimer l'historique et les Retours.
- Si l'utilisateur choisit la suppression, aucun fichier de l'Assistant ne reste dans le profil.

#### FR-23 : Informations « À propos »
L'écran « À propos » affiche :
- la version de l'application, du Modèle embarqué et de l'Index local ;
- la Liste blanche ;
- les licences des composants ;
- l'avertissement juridique.

### 4.11 Évaluation : Jeu d'évaluation maison, Baseline, mesures
**Description.** Banc d'évaluation reproductible. Il décide du go ou du no-go du fine-tuning et du choix du Modèle embarqué. Réalise UJ-6.

#### FR-24 : Jeu d'évaluation maison figé
Le jeu couvre les Tâches suivantes :

| Tâche | Nombre d'items |
|---|---|
| Question | 60 |
| Recherche de données | 40 |
| Compte rendu | 25 |
| Langage clair | 25 |
| Non-régression générale en français | 30 |
| Correction, Résumé, Courrier type | 15 chacune `[ASSUMPTION]` |

Le jeu est construit à partir des amorces AgentPublic et de questions rédigées. Il est figé (version + empreinte) avant toute génération de Données d'entraînement.
- L'empreinte est vérifiée à chaque évaluation.
- Un contrôle automatique garantit l'absence de tout item, ou quasi-doublon, dans les Données d'entraînement.
- Limite connue : la contamination par le préentraînement du Modèle de base n'est vérifiable que pour les modèles aux données ouvertes.

#### FR-39 : Grille du Juge
Une Grille du Juge versionnée définit, pour chaque Tâche notée par le Juge, les critères, l'échelle et des exemples d'ancrage. Elle est livrée et figée avec FR-24, avant la première Baseline.

#### FR-25 : Évaluation automatisée d'un modèle
Une commande unique évalue un modèle sur le Jeu d'évaluation maison, avec le Harnais complet. Le modèle peut être de base ou fine-tuné, avant ou après quantification. La commande produit un rapport de Scores de Tâche.
- Les appels d'outils sont évalués contre le Bac à sable MCP, pas contre le serveur réel.
- Juges autorisés : Claude, Gemini ou un grand modèle open-weight (§8).
- 20 % des items notés par le Juge sont exportés pour relecture humaine. Les scores restent marqués « non relus » tant qu'Anaël ne les a pas validés. La relecture ne bloque pas les pipelines. Elle n'est exigée que pour la décision finale de SM-1 et de SM-4.

#### FR-40 : Bac à sable MCP
Les réponses des outils MCP data.gouv utilisées pour l'évaluation et pour la validation des Données d'entraînement sont enregistrées une fois, versionnées et rejouées à l'identique. Le serveur réel ne sert qu'aux tests d'intégration.
- Deux évaluations successives du même modèle sur le Bac à sable MCP donnent les mêmes appels attendus et les mêmes réponses d'outils.

#### FR-26 : Mesures techniques sur le PC cible
Le banc mesure sur le PC cible, Index local chargé et selon un protocole fixe :
- le débit en tokens/s ;
- la latence au premier token ;
- la RAM maximale de l'Assistant complet ;
- la taille installée.

### 4.12 Benchmarks standardisés
#### FR-27 : Exécution du socle
Une commande unique exécute sur un modèle le socle de Benchmarks standardisés (addendum §E). Elle archive les résultats avec la version de chaque benchmark, la configuration (nombre d'exemples en few-shot, limite d'items) et l'environnement. Réalise UJ-6.

Le socle couvre :
- le français général et la compréhension ;
- le domaine France services ;
- le tool calling ;
- la traduction ;
- le suivi d'instructions ;
- les biais.

Critères d'acceptation :
- Le socle complet s'exécute en moins de 2 heures sur la RTX 3050, pour un modèle de 3B ou moins en 4 bits.
- Les benchmarks se récupèrent depuis Hugging Face ou GitHub par script, sans étape manuelle.

#### FR-28 : Benchmarks extensibles
Un benchmark s'ajoute au socle par configuration, sans modifier le code d'orchestration.

### 4.13 Données d'entraînement
**Description.** C'est le vrai travail du projet : le corpus de l'Index local existe déjà, mais les données comportementales n'existent pas et doivent être produites. Réalise UJ-6.

#### FR-29 : Génération des Données d'entraînement
Le pipeline génère les données avec un générateur autorisé (§8), dans un budget d'API plafonné et configurable (fixé dans `decisions.md`). Il produit :
- des traces de tool calling (question, appels MCP, réponse citée) ;
- des transcriptions synthétiques de réunions du secteur public et leurs comptes rendus ;
- des paires en langage clair ;
- des exemples pour les Tâches secondaires ;
- 10 à 20 % de données génériques en français.

Les volumes cibles sont dans l'addendum §G.

Critères d'acceptation :
- La génération s'arrête d'elle-même au plafond de budget.
- Chaque exemple garde sa provenance : générateur, version du prompt, source, date.

#### FR-30 : Validation et filtrage
Avant inclusion, chaque exemple est validé :
- les traces de tool calling sont rejouées contre le Bac à sable MCP, et celles qui divergent sont rejetées ;
- les réponses sourcées, les comptes rendus et les réécritures sont vérifiés contre leur source ;
- les doublons et les fuites du Jeu d'évaluation maison sont exclus.

Critères d'acceptation :
- Le taux de rejet est rapporté par motif.
- Un échantillon est exporté pour relecture humaine. Cette relecture ne bloque pas le pipeline.

#### FR-31 : Registre des licences
Chaque jeu source est inscrit au Registre des licences, avec sa licence, ses obligations (attribution Etalab 2.0, partage à l'identique) et son usage autorisé.
- La construction du jeu échoue si une source sans entrée au registre est utilisée.
- Le jeu de la version diffusée exclut les sources non commerciales, dont Claire French Dialogue (CC BY-NC-SA).
- Une variante « recherche » peut inclure ces sources. Elle est marquée comme telle et n'est jamais diffusée.

### 4.14 Fine-tuning et Comparatif
**Description.** Le projet entraîne des Modèles fine-tunés avec plusieurs Méthodes de fine-tuning, dans des conditions comparables. Le Comparatif est un livrable présentable à des clients. Réalise UJ-6.

#### FR-32 : Runs d'entraînement configurables
Anaël lance un Run d'entraînement en choisissant par configuration le Modèle de base, la Méthode de fine-tuning et les hyperparamètres. Changer de méthode ne demande aucune modification de code.

Les **4 méthodes comptées pour SM-6** sont :

| # | Méthode | Périmètre |
|---|---|---|
| M1 | QLoRA | Référence |
| M2 | LoRA bf16 | Plus petit Modèle de base candidat |
| M3 | DoRA | Sur base 4 bits |
| M4 | ORPO | Après le SFT |

Deux variantes sont mesurées en plus :
- QLoRA via Unsloth, pour la vitesse ;
- rsLoRA ou PiSSA, si le temps le permet.

#### FR-33 : Mesures de coût de chaque Run
Chaque Run d'entraînement enregistre :
- la durée et le débit (tokens/s hors padding, après chauffe) ;
- la VRAM maximale et l'énergie consommée ;
- la configuration complète, la graine et l'environnement (pilote, CUDA, versions).

Un Run interrompu reprend depuis son dernier checkpoint.

#### FR-34 : Protocole de comparaison équitable
Les Runs d'une même campagne partagent les mêmes données, le même ordre, le même chat template et le même masquage de la perte. Le Comparatif présente deux vues :
- à tokens vus égaux ;
- à budget de temps égal.

M4 (ORPO) déroge au protocole, car elle a besoin de données de préférence. Ces données sont dérivées du jeu SFT, et la dérogation est documentée dans le Comparatif.

#### FR-35 : Export et évaluation après quantification
Un Modèle fine-tuné peut être fusionné en 16 bits, converti et quantifié au format d'exécution de l'Assistant, puis réévalué via FR-25 et FR-27.
- Le Comparatif rapporte les scores avant et après quantification.
- Le tool calling est re-testé après quantification.

#### FR-36 : Rapport Comparatif
Le Comparatif est généré à partir des Runs et des évaluations. Pour chaque méthode, il présente :
- le gain par Tâche par rapport à la Baseline ;
- l'effet sur les Benchmarks standardisés ;
- les coûts : durée, VRAM, énergie ;
- une recommandation.

Critères d'acceptation :
- Le rapport se régénère à l'identique à partir des artefacts archivés.
- Il contient une section sur la méthode et ses limites, lisible par un non-spécialiste.

### 4.15 Publication
#### FR-37 : Fiche modèle et rapport publiés
Anaël peut publier sur Hugging Face, en public ou en privé, le Modèle embarqué, sa fiche modèle et le Comparatif.
- La licence de publication est Apache 2.0 si le Modèle de base le permet. Sinon, c'est la licence compatible la plus permissive.
- La fiche contient :
  - les données utilisées et le Registre des licences ;
  - les résultats d'évaluation ;
  - les limites et les usages déconseillés.
- La publication n'est jamais automatique : elle demande une action explicite d'Anaël.
- Aucune communication ne prête au Modèle embarqué ni à l'Assistant une certification qui ne le couvre pas. Par exemple, l'ISO 42001 d'IBM porte sur son système de management, pas sur Granite.

## 5. Exigences non fonctionnelles transverses

- **NFR-1 Mémoire.** La RAM maximale de l'Assistant complet (Modèle embarqué, Index local, Harnais et interface) ne dépasse pas **5 Go, avec une cible de 4 Go**. Elle est mesurée sur le PC cible pendant une génération, et la bureautique doit rester utilisable en parallèle.
  `[NOTE FOR PM : contrainte structurante. Un 3B en Q4 avec BGE-M3 et un index complet dépasse probablement 4 Go. L'architecture arbitre par la mesure, à l'aide des leviers listés dans l'addendum §D.]`
- **NFR-2 Débit.** Au moins 8 tokens/s en génération sur le PC cible.
- **NFR-3 Latence.** Premier token en moins de 5 s pour une Question avec recherche dans l'Index local.
- **NFR-4 Confidentialité.** Seules des Requêtes sortantes conformes à FR-38 quittent le poste. Les conversations, les documents collés, l'historique et les Retours restent en local.
- **NFR-5 Hors ligne.** Toutes les Tâches fonctionnent sans réseau, sauf trois cas :
  - la recherche fraîche de données (FR-7 en Mode connecté) ;
  - l'interrogation de ressource (FR-8) ;
  - la vérification en ligne (FR-12).
- **NFR-6 Installation.** L'installation se fait sans droits administrateur, sur Windows 10/11 x64. La taille installée est d'au plus 4 Go `[ASSUMPTION]`.
- **NFR-7 Accessibilité.** L'interface vise le RGAA 4.1. Trois critères sont vérifiés en v1 :
  - navigation complète au clavier ;
  - contraste d'au moins 4,5:1 ;
  - libellés accessibles sur tous les contrôles.
  L'audit formel est hors MVP.
- **NFR-8 Reproductibilité.** Évaluations, Runs d'entraînement et Comparatif sont reproductibles à partir de la configuration versionnée, de la graine et du Bac à sable MCP.
- **NFR-9 Robustesse des outils.** Le schéma des outils MCP est versionné et comparé au schéma du serveur au passage en Mode connecté.
  - Un outil inconnu est ignoré.
  - Un outil attendu mais absent, ou dont le schéma a changé, déclenche le repli FR-9 et une entrée de journal.

## 6. Contraintes et garde-fous

### 6.1 Sécurité, confiance, conformité
- La citation systématique des sources et l'avertissement juridique sont imposés (FR-3).
- **Transparence (AI Act, art. 50).** L'Agent sait qu'il interagit avec une IA, et les textes générés sont présentés comme tels.
  - La qualification visée est le risque limité, car l'Assistant ne sert pas à décider de l'accès d'un Usager à un service `[ASSUMPTION : à confirmer]`.
- Les recommandations de l'ANSSI pour un système d'IA générative (2024) servent de référentiel de conception.
- **Souveraineté et auditabilité.**
  - Le degré d'ouverture des données d'entraînement est un critère de choix du Modèle de base (addendum §C).
  - Aucune communication ne présente le Modèle de base comme garant de souveraineté culturelle, ni n'étend une certification au-delà de son périmètre.

### 6.2 Données personnelles
L'Assistant n'est pas conçu pour traiter des données personnelles. Un rappel s'affiche à la première utilisation. Tout est stocké en local, sans télémétrie.

### 6.3 Coûts et moyens
- **Budget d'API.** Le générateur de Données d'entraînement a un budget plafonné et configurable, dont le montant est fixé dans `decisions.md`.
- **Entraînement.** Il se fait uniquement sur la RTX 3050 locale, avec des séquences de 2 à 4k tokens. Aucun GPU cloud n'est prévu en v1 `[ASSUMPTION]`.

## 7. Non-objectifs
- Pas de préentraînement d'un modèle.
- Pas de mémorisation des données de data.gouv dans les poids : le savoir vient de l'Index local et des outils.
- Pas de conseil juridique engageant ni de décision sur les droits d'un Usager.
- Pas de traitement de données personnelles.
- Pas de service cloud, de compte utilisateur ni de synchronisation.
- Pas de version macOS, Linux ou mobile en v1.
- Pas d'interface destinée aux Usagers.

## 8. Règles sur les générateurs et les juges (garde-fou bloquant)

- **Claude est exclu comme générateur de Données d'entraînement.**
  - **Fondement** : les conditions d'Anthropic interdisent d'utiliser les sorties de Claude comme cibles d'entraînement d'un modèle de génération de texte ouverte sans autorisation écrite. Voir l'[article support](https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model) et les [Commercial Terms](https://www.anthropic.com/legal/commercial-terms).
  - **Portée** : l'exclusion couvre aussi les exemples few-shot et les amorces rédigées par Claude et insérés dans les prompts du générateur.
  - **Usages autorisés** : Claude peut écrire le code du pipeline, servir de Juge et rédiger le Jeu d'évaluation maison, qui n'est jamais utilisé pour l'entraînement.
  - **Levée** : seul un accord écrit d'Anthropic lèverait cette exclusion.
- **Gemini est exclu comme générateur.**
  - **Fondement** : les Gemini API Additional Terms interdisent le développement de modèles concurrents.
  - **Usage autorisé** : Gemini peut servir de Juge.
- **Générateur retenu : un grand modèle Mistral via l'API.**
  - **Fondement** : les Commercial Terms de Mistral, §3.3, en vigueur au 25 septembre 2026, ne restreignent que les sorties image. Il faut **revérifier ces conditions avant chaque campagne de génération**.
  - **Exclusions** : les modèles « Labs » ou en préversion, dont les données servent à l'entraînement de Mistral.
  - **Repli local** : Qwen3.6-35B-A3B (Apache 2.0). C'est un compromis de souveraineté assumé, puisque ce modèle n'est pas européen.
- **Origine des amorces des Données d'entraînement.** Elles viennent uniquement de sources publiques (AgentPublic, MediaTech), d'Anaël ou du générateur retenu.

## 9. Périmètre du MVP

### 9.1 Dans le périmètre
- **Assistant Windows local.**
  - Tâches prioritaires : Question, Recherche de données, Compte rendu, Langage clair.
  - Tâches secondaires : Correction, Résumé, Courrier type, Traduction (EN, ES, AR, PT, DE).
  - Mode hors ligne, et Mode connecté avec Liste blanche configurable.
  - Journal des Requêtes sortantes et Retours locaux avec export.
- **Banc d'évaluation.**
  - Jeu d'évaluation maison et Grille du Juge figés.
  - Bac à sable MCP.
  - Baseline et socle de Benchmarks standardisés.
- **Fine-tuning.**
  - Pipeline de Données d'entraînement.
  - Runs d'entraînement pour les 4 méthodes.
  - Comparatif.
- **Distribution.** Installateur sans droits administrateur et publication manuelle sur Hugging Face.

### 9.2 Hors MVP
- **Jeu d'évaluation maison pour la Traduction** : les benchmarks publics suffisent en v1.
- **Audit RGAA formel et homologation de sécurité** : ils viendront lors d'un déploiement réel.
- **Mise à jour automatique du Modèle embarqué et de l'Index local** : prévue en v2. D'ici là, FR-6 affiche la date de l'Index local.
- **Corpus propres à une collectivité** (délibérations, règlements départementaux) : prévus en v2.
  `[NOTE FOR PM : c'est probablement le vrai différenciateur d'un déploiement en conseil départemental.]`
- **Transcription audio** et **déploiement en masse par la DSI** (MSI, GPO) : prévus en v2.

### 9.3 Ordre de livraison et règle d'arbitrage

**Règle d'arbitrage.** En cas de conflit de temps ou de moyens :
1. le banc d'évaluation et le Comparatif passent avant l'application packagée ;
2. les Tâches prioritaires passent avant les Tâches secondaires.

**Ordre de coupe si la charge dérape.** On retire dans cet ordre :
1. FR-12 ;
2. la Traduction ;
3. le Courrier type et le Résumé ;
4. la Correction ;
5. les variantes non comptées (rsLoRA, PiSSA) ;
6. M3, puis M4.

**Ordre des jalons :**

| Jalon | Lot de la note | Contenu | FR principales |
|---|---|---|---|
| J0 | 0. Cadrage | Jeu d'évaluation maison et Grille du Juge figés, Registre des licences initial. Fait avec Anaël. | FR-24, FR-39, FR-31 |
| J1 | 1. Baseline | Harnais minimal en ligne de commande : Index local, outils MCP, Bac à sable MCP. Banc d'évaluation, socle de Benchmarks standardisés, mesures techniques. Baseline des Modèles de base candidats. **Décision go/no-go**, prise par Anaël. | FR-3, FR-5, FR-7 à FR-9, FR-25 à FR-28, FR-40 |
| J2 | 2. Données | Pipeline de génération, validation, filtrage. Jeu d'entraînement versionné. | FR-29 à FR-31 |
| J3 | 3. Fine-tuning | Runs M1 à M4, export GGUF, réévaluation, Comparatif. | FR-32 à FR-36 |
| J4 | 4. Packaging | Assistant Windows : Tâches prioritaires, Modes, Liste blanche, journal, Retours, installateur. | FR-1 à FR-11, FR-13, FR-16, FR-19 à FR-23, FR-38 |
| J5 | Extension | Tâches secondaires et FR-12, puis publication. | FR-12, FR-14, FR-15, FR-17, FR-18, FR-37 |

**Charge.** La note estimait 21 à 38 jours pour 4 cas d'usage et une seule méthode. Le périmètre s'est élargi avec 4 Tâches secondaires, 4 méthodes et 7 benchmarks. La charge est réestimée à 30 à 50 jours `[ASSUMPTION]`.

**Chemin no-go.** Si aucun Modèle fine-tuné ne satisfait SM-1 :
- la meilleure Baseline devient le Modèle embarqué ;
- le Comparatif est publié avec ce résultat négatif, qui est en soi un enseignement ;
- FR-37 publie le Comparatif seul.

## 10. Indicateurs de succès

### 10.1 Score de Tâche (barème de 0 à 100)

| Tâche | Composantes | Méthode | Score de Tâche |
|---|---|---|---|
| Question | Exactitude (Juge : exact, partiel ou faux). Source juste (automatique : URL présente dans les passages retrouvés, puis pertinence notée par le Juge). | Juge + automatique | % d'items exacts **et** correctement sourcés |
| Recherche de données | Appel valide : bon outil, arguments conformes au schéma (automatique). Réponse exacte par rapport au Bac à sable MCP (automatique). | Automatique | Moyenne des deux taux |
| Compte rendu | Couverture : rappel des décisions et actions de référence annotées (Juge). Absence d'invention : % de comptes rendus sans élément inventé (Juge). | Juge | Moyenne des deux |
| Langage clair | Fidélité du sens (Juge). Gain de lisibilité Kandel-Moles (automatique). | Juge + automatique | % de fidélité, à condition que le gain moyen soit d'au moins 10 points |
| Correction | Rappel des fautes injectées. Taux de modifications hors faute (automatique). | Automatique | Rappel × (1 − taux hors faute) |
| Résumé | Fidélité et couverture (Juge) | Juge | Moyenne |
| Courrier type | Conformité au format (Juge). Aucune valeur inventée (automatique). | Juge + automatique | Moyenne |
| Non-régression | Exactitude (Juge) | Juge | % exacts |

Un écart de « N points » est un écart absolu de Score de Tâche.

### 10.2 Indicateurs

**Principaux**
- **SM-1 Go du fine-tuning.** Le Modèle fine-tuné retenu gagne au moins 10 points de Score de Tâche sur au moins 2 Tâches prioritaires par rapport à la meilleure Baseline. Il perd au plus 3 points en non-régression et au plus 3 points en moyenne sur le socle de Benchmarks standardisés. Valide FR-24, FR-25, FR-32.
- **SM-2 Exactitude sourcée.** Score de Tâche Question d'au moins 80, sans aucune URL inventée. Valide FR-3, FR-5. `[ASSUMPTION : seuil à confirmer après la Baseline]`
- **SM-3 Recherche de données.** Au moins 90 % d'appels valides et au moins 80 % de réponses exactes. Valide FR-7, FR-8. `[ASSUMPTION : seuils à confirmer après la Baseline]`
- **SM-4 Fidélité rédactionnelle.**
  - Compte rendu : au moins 90 % sans invention, couverture d'au moins 80 %.
  - Langage clair : fidélité d'au moins 90 %.
  - Ces chiffres sont confirmés par la relecture humaine. Valide FR-13, FR-16. `[ASSUMPTION : seuils à confirmer après la Baseline]`
- **SM-5 Tenue sur le PC cible.** RAM d'au plus 5 Go (cible 4 Go), au moins 8 tokens/s, premier token en moins de 5 s. Valide NFR-1 à NFR-3 et FR-26.
- **SM-6 Comparatif livré.** Les méthodes M1 à M4 sont comparées selon FR-34, dans un rapport régénérable. Valide FR-33 à FR-36.

**Secondaires**
- **SM-7 Adoption de la démo.** Au moins 5 Agents testent l'Assistant et laissent au moins 50 Retours, dont plus de 70 % positifs. Valide FR-19, FR-20. `[ASSUMPTION : seuils à confirmer]`
- **SM-8 Installation.** L'Assistant s'installe sans assistance sur au moins 2 postes autres que la machine de développement. Valide FR-21.

**Contre-indicateurs (à ne pas optimiser)**
- **SM-C1 Scores des Benchmarks standardisés.** Ils servent à détecter les régressions. Ils ne sont pas un objectif, et ils ne décident pas du choix du Modèle de base. Contrebalance SM-1.
- **SM-C2 Nombre d'appels d'outils.** Plus d'appels n'est pas mieux. Contrebalance SM-3.
- **SM-C3 Taux de réponse.** « Je ne trouve pas de Source officielle » est une bonne réponse. Contrebalance SM-2.
- **SM-C4 Longueur des réponses.** L'exhaustivité ne vaut pas la qualité, surtout en langage clair. Contrebalance SM-4.

## 11. Risques

Le registre complet, avec les parades et les renvois aux exigences, figure dans l'addendum §H. Risques majeurs :
- tool calling instable à 3B ;
- dépassement de RAM ;
- Données d'entraînement fausses ;
- volume insuffisant de paires en langage clair (précédent llama-falc) ;
- instabilité du serveur MCP ;
- réponses juridiques erronées ;
- licences hétérogènes.

## 12. Questions ouvertes

1. **Modèle de base.** Quel Modèle de base tient dans 4 à 5 Go avec l'Index local ? La réponse viendra de la Baseline et des mesures sur le PC cible, pas des benchmarks publics.
2. **Corpus MediaTech.** Quel périmètre embarquer : service-public et catalogue data.gouv seuls, ou aussi LEGI, travail-emploi, CNIL, Constitution et DOLE ?
3. **Vérifications pendant la Baseline.**
   - Ministral 3 avec son encodeur vision est-il supporté par llama.cpp et par TRL ?
   - Quelle est la qualité du français de Granite ?
   - Quel est le niveau de tool calling de SmolLM3 ?
4. **Langues.** L'arabe est-il assez bien traité pour rester en v1 ?
5. **Collecte des besoins.** Quels Agents testeront le démonstrateur, et avec quel protocole de collecte des besoins ?
6. **Réglementation.** La qualification AI Act et les obligations RGPD d'un déploiement réel restent à confirmer.

## 13. Index des hypothèses

- §1 : le créneau local est peu occupé. Les outils des collectivités et les assistants locaux grand public n'ont pas été étudiés.
- FR-9 : délai MCP de 10 s par défaut.
- FR-24 : 15 items chacun pour Correction, Résumé et Courrier type.
- NFR-6 : taille installée d'au plus 4 Go.
- §6.1 : qualification AI Act en risque limité.
- §6.3 : pas de GPU cloud en v1.
- §9.3 : charge réestimée à 30 à 50 jours.
- SM-2, SM-3, SM-4, SM-7 : seuils à confirmer après la Baseline.
- Addendum §G : 200 à 500 exemples d'entraînement par Tâche secondaire.
