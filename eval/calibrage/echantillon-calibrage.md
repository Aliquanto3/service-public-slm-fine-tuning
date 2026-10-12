# Échantillon de calibrage du Jeu d'évaluation maison

16 items (2 par Tâche). Construit le 2026-10-12 par `build_calibrage.py`. Empreinte SHA-256 du JSONL : `8eb31fdb4f6d34fac1ccb22caf94f7560e21b093082579c76fcf6a616628cedc`.

Usage : évaluation uniquement, jamais d'entraînement. Les textes longs sont tronqués à 15 lignes ; le JSONL fait foi.

| id | Tâche | difficulté | sujet |
|---|---|---|---|
| Q-001 | Question | facile | Carte d'identité perdue : gratuité et démarche |
| Q-002 | Question | difficile | Sigle « PPG » : question sans source officielle |
| R-001 | Recherche de données | facile | Jeux de données sur les défibrillateurs (Géo'DAE) |
| R-002 | Recherche de données | difficile | Nombre de DAE à Lorient via l'API tabulaire |
| CR-001 | Compte rendu | facile | COPIL France services itinérant (intercommunalité) |
| CR-002 | Compte rendu | difficile | Commission travaux municipale, notes en désordre |
| LC-001 | Langage clair | facile | Forfait post-stationnement : délai et majoration |
| LC-002 | Langage clair | difficile | CRPA : accusé de réception (L. 112-3, R. 112-5, L. 112-6) |
| CO-001 | Correction | facile | Avis de fermeture de médiathèque, 8 fautes |
| CO-002 | Correction | difficile | Note interne permanences, 12 fautes |
| RS-001 | Résumé | facile | Allocation de rentrée scolaire 2026 (résumé court) |
| RS-002 | Résumé | difficile | Ombrières des parkings de plus de 1 500 m² (résumé moyen) |
| CT-001 | Courrier type | facile | Demande de pièces, inscription périscolaire |
| CT-002 | Courrier type | difficile | Accusé de réception d'une demande d'occupation du domaine public |
| NR-001 | Non-régression | facile | Calcul d'horaire |
| NR-002 | Non-régression | moyen | Reformulation en registre soutenu |

---

## Q-001 · Question · facile

### Entrée

> Une usagère vient de perdre sa carte d'identité en France. Elle me demande si la nouvelle carte est gratuite et ce qu'elle doit faire. Que dois-je lui répondre ?

*Amorce usager (AgentPublic) :* « Est que la carte d’identité est gratuite en cas de pert e? »

### Référence


**reponse_reference** :

```text
Non, le renouvellement d'une carte d'identité perdue n'est pas gratuit : il faut un timbre fiscal de 25 € (12,50 € en Guyane). Si elle refait sa carte tout de
suite, la déclaration de perte se fait au guichet de la mairie au moment du dépôt du dossier (cerfa n°14011), sans passer par la police. Elle peut déposer sa
demande dans n'importe quelle mairie équipée d'une station d'enregistrement, souvent sur rendez-vous, avec une photo de moins de 6 mois, un justificatif de
domicile, la déclaration de perte et le timbre fiscal (plus son passeport s'il est valide ou périmé depuis moins de 5 ans). Sa présence est obligatoire pour
les empreintes, et la carte doit être retirée dans les 3 mois. Ne vaut pas avis juridique.
```

**sources_attendues** :

- https://www.service-public.gouv.fr/particuliers/vosdroits/F1344

**elements_cles** :

- Pas gratuit : timbre fiscal de 25 € (12,50 € en Guyane)
- Déclaration de perte faite en mairie lors du dépôt si nouvelle demande immédiate (sinon commissariat ou gendarmerie)
- Dépôt dans n'importe quelle mairie équipée d'une station d'enregistrement, souvent sur rendez-vous
- Pièces : photo de moins de 6 mois, justificatif de domicile, déclaration de perte (cerfa n°14011), timbre fiscal
- Présence obligatoire (empreintes) et retrait de la carte dans les 3 mois

- **mention_obligatoire** : Ne vaut pas avis juridique

### Provenance

- **source** : AgentPublic/assistant_ia_questions_corpus (evaluation_qo_assistant_ia_v1.xlsx) ; **url** : https://huggingface.co/datasets/AgentPublic/assistant_ia_questions_corpus/resolve/main/evaluation_qo_assistant_ia_v1.xlsx ; **role** : amorce de question usager, reformulée par un agent ; **consulte_le** : 2026-10-12
- **source** : MediaTech AgentPublic/service-public, fiche F1344 « Carte d'identité d'un majeur : renouvellement en cas de perte » ; **url** : https://www.service-public.gouv.fr/particuliers/vosdroits/F1344 ; **role** : fiche de référence (chunks 2 à 8, cas « En France ») ; **consulte_le** : 2026-10-12

**Licence** : Amorce : MIT (carte du dataset). Fiche : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face).

---

## Q-002 · Question · difficile

### Entrée

> Dans une note de la préfecture, on nous demande de suivre « l'avancement des PPG » pour notre territoire. Qu'est-ce que les PPG et où trouver la liste officielle ?

*Amorce usager (AgentPublic) :* « Qu’est ce que les PPG ? »

### Référence

- **reponse_reference** : Je ne trouve pas de source officielle sur les « PPG » dans les fiches dont je dispose. Je ne peux donc pas vous en donner une définition ni une liste sourcées. Je vous conseille de vous adresser au service de la préfecture qui a émis la note, ou de consulter les publications officielles du Gouvernement. Ne vaut pas avis juridique.
- **comportement_attendu** : absence_de_source
**sources_attendues** :



**elements_cles** :

- Dit explicitement qu'aucune source officielle de l'Index local ne traite des PPG
- N'invente aucune URL et ne cite aucune fiche service-public comme source
- Oriente vers le service émetteur de la note (préfecture) ou les publications officielles du Gouvernement
- Si un développement du sigle est proposé (p. ex. « politiques prioritaires du Gouvernement »), il est présenté comme non sourcé et à vérifier

- **mention_obligatoire** : Ne vaut pas avis juridique
**verification_absence** :

- **corpus** : AgentPublic/service-public (config latest)
- **motifs_recherches_regex_insensible_casse** : 
  - politiques? prioritaires? du gouvernement
  - \bPPG\b
  - baromètre de l.action publique
- **resultat** : 0 fiche trouvée pour chaque motif (contrôle positif « journée de solidarité » : 3 fiches)
- **date** : 2026-10-12


### Provenance

- **source** : AgentPublic/assistant_ia_questions_corpus (evaluation_qo_assistant_ia_v1.xlsx) ; **url** : https://huggingface.co/datasets/AgentPublic/assistant_ia_questions_corpus/resolve/main/evaluation_qo_assistant_ia_v1.xlsx ; **role** : amorce « Qu'est-ce que les PPG ? » ; **consulte_le** : 2026-10-12
- **source** : Recherche plein texte dans le parquet MediaTech service-public ; **url** : https://huggingface.co/datasets/AgentPublic/service-public/resolve/refs%2Fconvert%2Fparquet/latest/train/0000.parquet ; **role** : preuve d'absence de source ; **consulte_le** : 2026-10-12

**Licence** : Amorce : MIT. Corpus vérifié : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face).

---

## R-001 · Recherche de données · facile

### Entrée

> Je prépare une carte des défibrillateurs pour la commune. Quels jeux de données existent sur data.gouv.fr ? Pour la base nationale, donne-moi le producteur et la date de dernière mise à jour.

### Référence

**appels_attendus** :

- **outil** : search_datasets ; **arguments** : **query** : défibrillateurs ; **regle** : query contient « défibrillateur » ou « DAE » (insensible à la casse et aux accents) ; autres paramètres optionnels
- **outil** : get_dataset_info ; **arguments** : **dataset_id** : 61556e1e9d6adb2df86eb0fc ; **regle** : dataset_id exact

**reponse_reference** :

- **jeu_principal** : 
  - **titre** : Géo'DAE - Base Nationale des Défibrillateurs
  - **producteur** : Atlasanté
  - **derniere_mise_a_jour** : 2026-10-12T01:01:09.414000+00:00
  - **url** : https://www.data.gouv.fr/datasets/geodae-base-nationale-des-defibrillateurs/
  - **licence** : lov2
- **autres_jeux_cites_possibles** : 
  - **titre** : Défibrillateurs du réseau RATP ; **producteur** : Régie autonome des transports parisiens (RATP)
  - **titre** : Equipements Défibrillateurs ; **producteur** : SNCF
  - **titre** : Défibrillateurs gérés par GPSO ; **producteur** : Grand Paris Seine Ouest
  - **titre** : Défibrillateurs dans les gares SNCF d'Île-de-France ; **producteur** : Région Île-de-France
- **texte** : La base nationale est « Géo'DAE - Base Nationale des Défibrillateurs », produite par Atlasanté, mise à jour le 2026-10-12 (licence lov2) : https://www.data.gouv.fr/datasets/geodae-base-nationale-des-defibrillateurs/. D'autres jeux existent, par exemple ceux de Régie autonome des transports parisiens (RATP), SNCF, Grand Paris Seine Ouest.

- **cassette** : cassettes/R-001.json

### Provenance

- **source** : Serveur MCP data.gouv (search_datasets, get_dataset_info) ; **url** : https://mcp.data.gouv.fr/mcp ; **role** : réponses enregistrées (Bac à sable MCP) ; **consulte_le** : 2026-10-12T05:43:56+02:00

**Licence** : Métadonnées data.gouv.fr ; licence du jeu déclarée : lov2 (Licence Ouverte v2).

---

## R-002 · Recherche de données · difficile

### Entrée

> Combien de défibrillateurs sont recensés dans la base nationale Géo'DAE pour Lorient (code INSEE 56121) ? Donne le nombre et les 5 premiers lieux renvoyés, dans un tableau sourcé.

### Référence

**appels_attendus** :

- **outil** : search_datasets ; **arguments** : **query** : défibrillateurs ; **regle** : query contient « défibrillateur », « DAE » ou « Géo'DAE » ; peut être omis si le modèle passe directement l'identifiant connu
- **outil** : list_dataset_resources ; **arguments** : **dataset_id** : 61556e1e9d6adb2df86eb0fc ; **regle** : dataset_id exact
- **outil** : query_resource_data ; **arguments** : **resource_id** : edb6a9e1-2f16-4bbf-99e7-c3eb6b90794c ; **filter_column** : c_com_insee ; **filter_value** : 56121 ; **filter_operator** : exact ; **page_size** : 5 ; **regle** : resource_id exact (ressource CSV, pas JSON) ; filtre c_com_insee = 56121 (exact) ; page_size >= 5

**reponse_reference** :

- **nombre_total** : 208
- **cinq_premiers** : 
  - **c_nom** : DAE G5 CARDIAC SCIENCE ; **adresse** : 9 Cours Louis de Chazelles ; **c_etat_valid** : validées
  - **c_nom** : DEKRA Industrial Lorient ; **adresse** : 18 Rue Robert Caignan ; **c_etat_valid** : en attente de validation
  - **c_nom** : TJ Lorient ; **adresse** : 1 Rue maître Pierre Esvelin ; **c_etat_valid** : validées
  - **c_nom** : DECATHLON ; **adresse** : 4 Rue Antoine de Saint-Exupéry ; **c_etat_valid** : validées
  - **c_nom** : DAE DE LA GARE de LORIENT ; **adresse** : 34 RUE DE BEAUVAIS ; **c_etat_valid** : en attente de validation
- **precision** : Le total est celui de l'API tabulaire au moment de l'enregistrement ; il inclut des DAE « en attente de validation ».
- **texte** : La base Géo'DAE recense 208 défibrillateurs pour Lorient (56121), selon l'API tabulaire de data.gouv.fr.

**criteres** :

- Valeurs du tableau identiques à la cassette (FR-8)
- Lien vers le jeu ou la ressource cité
- Ne pas confondre avec le nombre de pages ni filtrer sur c_com_nom (casse variable)

- **cassette** : cassettes/R-002.json

### Provenance

- **source** : Serveur MCP data.gouv (search_datasets, list_dataset_resources, query_resource_data) ; **url** : https://mcp.data.gouv.fr/mcp ; **role** : réponses enregistrées (Bac à sable MCP) ; **consulte_le** : 2026-10-12T05:44:00+02:00

**Licence** : Géo'DAE (Atlasanté) : Licence Ouverte v2 (lov2) selon get_dataset_info.

---

## CR-001 · Compte rendu · facile

### Entrée

- **consigne** : Rédige le compte rendu de cette réunion : participants, points abordés, décisions, actions (responsable, échéance).

**notes** :

```text
COPIL France services itinérant – jeudi 08/10/2026 – 10h – salle du conseil, CC du Pays de Valmont
Présents : M. Garnier (vice-président CC, préside), Mme Okafor (DGS CC), Mme Ruiz (coordinatrice France services), M. Lambert (conseiller numérique), Mme Petit
(CAF, partenaire), M. Diallo (préfecture, en visio la 1re heure seulement)
Excusée : Mme Roche (MSA), envoie ses chiffres par mail

Garnier ouvre, rappelle que c'est le 3e COPIL de l'année, ordre du jour envoyé la semaine dernière, pas d'ajout.

1. Bilan T3 (juillet-septembre)
- Ruiz : 1 412 accompagnements sur le trimestre, +18 % par rapport au T2. Été plus chargé que prévu, surtout fin août (rentrée).
- Top 3 des démarches : ANTS (cartes grises, titres d'identité), CAF (prime d'activité surtout), impôts (corrections de déclaration en ligne).
- Le bus passe dans 9 communes sur 11. Mornay et Les Essarts ne sont plus desservies depuis juin : à Mornay, plus de place pour stationner place de l'Église
(marché déplacé) ; aux Essarts, travaux de voirie jusqu'à une date inconnue.
- Lambert : beaucoup de personnes âgées sans adresse mail, on en crée à chaque permanence, ça prend du temps. Il aimerait un support papier type pas-à-pas. Pas
de suite donnée pour l'instant, Ruiz dit qu'elle en parlera en réunion d'équipe.
- Petit (CAF) : demande si on peut avoir un créneau de rendez-vous en visio avec un conseiller CAF dans le bus, une fois par mois. Ruiz : d'accord sur le
[… tronqué : 29 lignes de plus, texte complet dans le JSONL]
```

- **nb_mots** : 677

### Référence

**participants_reference** :

- M. Garnier (président de séance)
- Mme Okafor
- Mme Ruiz
- M. Lambert
- Mme Petit (CAF)
- M. Diallo (préfecture, en visio la 1re heure seulement)
- Excusée : Mme Roche (MSA)

**decisions_reference** :

- Le bus France services revient à Mornay à partir du lundi 2 novembre 2026, sur le parking de la salle des fêtes, le lundi matin
- Achat d'un ordinateur portable de remplacement sur le budget 2026 (environ 900 €)
- Accord de principe pour un créneau mensuel de rendez-vous en visio avec la CAF dans le bus
- Le bilan annuel sera présenté au conseil communautaire de décembre

**actions_reference** :

- **action** : Lancer le bon de commande de l'ordinateur ; **responsable** : Mme Okafor ; **echeance** : avant le vendredi 16 octobre 2026
- **action** : Inscrire le bilan à l'ordre du jour du conseil communautaire ; **responsable** : Mme Okafor ; **echeance** : conseil communautaire de décembre 2026
- **action** : Fournir la fréquentation par arrêt sur 2026 ; **responsable** : Mme Ruiz ; **echeance** : prochain COPIL (fin janvier 2027)
- **action** : Caler les modalités et la date de démarrage du créneau visio CAF ; **responsable** : Mme Ruiz et Mme Petit ; **echeance** : non fixée
- **action** : Préparer le dossier de labellisation France services ; **responsable** : Mme Ruiz ; **echeance** : premier jet fin janvier 2027 ; dépôt avant le 31 mars 2027
- **action** : Réaliser et diffuser le flyer (nouveaux horaires, retour à Mornay) dans les 11 mairies ; **responsable** : M. Lambert ; **echeance** : avant le 1er novembre 2026
- **action** : Voir avec le service communication pour un article dans le magazine intercommunal ; **responsable** : Mme Okafor ; **echeance** : magazine de décembre 2026
- **action** : Envoyer le sondage pour fixer la date du prochain COPIL ; **responsable** : Mme Ruiz ; **echeance** : non précisée (COPIL fin janvier 2027)

**pieges** :

- Arrêt au hameau de Saint-Rémy : débattu, NON décidé
- Imprimante portable : proposée, NON décidée (éventuellement BP 2027)
- Les Essarts : aucune décision ; l'information des habitants n'a pas de responsable désigné
- Support papier pas-à-pas : simple idée, pas d'action ni de responsable
- Créneau visio CAF : aucune date de démarrage fixée, ne pas en inventer
- Relais de la CAF sur ses réseaux : proposition conditionnelle, pas une action actée
- M. Diallo n'a assisté qu'à la première heure


### Provenance

- **source** : Notes fictives rédigées pour l'évaluation (collectivité, personnes et chiffres imaginaires) ; **consulte_le** : 2026-10-12

**Licence** : Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce

---

## CR-002 · Compte rendu · difficile

### Entrée

- **consigne** : Rédige le compte rendu de cette commission : participants, points abordés, décisions, actions (responsable, échéance).

**notes** :

```text
Commission Travaux – Cadre de vie — mardi 6/10/26, 18h30, mairie de Belcourt-sur-Vanne (salle 2)
pst : JP Morel (adjoint travaux, préside), C. Benoît, A. Haddad, L. Fontaine (conseillers maj.), N. Vidal (conseiller opposition), S. Marchal (DST), + M. Royer
(asso Vivre à Belcourt) invité pour le pt 3 uniquement
abs. : F. Leclerc (excusé ; il voulait donner pouvoir à Morel → non, pas de pouvoir en commission, simple excuse)
secrétaire de séance : Fontaine (prend les notes, désolée pour le désordre)

pt 1 – école J. Ferry, réfection toiture (bât. B)
Marchal : consultation close le 25/09, 3 offres reçues. Moins-disante : Couverture Delmas 48 600 € HT, délai 10 semaines. Bati Ouest : 51 200 € HT, délai 6
semaines. 3e offre (Toitures du Val) 57 900 € HT, écartée (dossier incomplet ?? à confirmer par Marchal, je n'ai pas bien noté).
Discussion : on veut que ce soit fini avant l'hiver, les fuites dans la classe de CM1 empirent. Haddad demande si on peut mettre des pénalités de retard →
Marchal : oui, déjà prévues au CCAP.
Benoît : Delmas a déjà travaillé pour la commune (salle des sports), bon souvenir. Mais le délai…
Le règlement de consultation pondère le délai à 40 %. Marchal : avec la grille, Bati Ouest arrive 1er.
AVIS de la commission : favorable à l'attribution à Bati Ouest – 5 pour, 1 abstention (Vidal, veut voir le rapport d'analyse complet avant de se prononcer).
Rappel Morel : la commission donne un avis, l'attribution sera votée au conseil municipal.
[… tronqué : 37 lignes de plus, texte complet dans le JSONL]
```

- **nb_mots** : 754

### Référence

**participants_reference** :

- J.-P. Morel (adjoint aux travaux, président)
- C. Benoît
- A. Haddad
- L. Fontaine (secrétaire de séance)
- N. Vidal (opposition)
- S. Marchal (DST)
- M. Royer (association Vivre à Belcourt, point 3 seulement)
- Excusé : F. Leclerc (sans pouvoir)

**decisions_reference** :

- Avis favorable à l'attribution de la réfection de la toiture de l'école Jules-Ferry à Bati Ouest (51 200 € HT, 6 semaines) : 5 pour, 1 abstention (N. Vidal). Il s'agit d'un AVIS ; l'attribution sera votée au conseil municipal du 22 octobre 2026
- Expérimentation d'extinction de l'éclairage public de 23 h à 5 h, pendant 6 mois, au seul lotissement des Tilleuls, avec bilan en commission (unanimité)
- Pose de 2 arceaux vélo supplémentaires (10 places) place du Marché, en régie, sur le budget de fonctionnement voirie, avant fin novembre (unanimité)

**actions_reference** :

- **action** : Envoyer le rapport d'analyse des offres à tous les membres ; **responsable** : S. Marchal ; **echeance** : avant le vendredi 9 octobre 2026
- **action** : Inscrire l'attribution du marché toiture au conseil municipal ; **responsable** : non précisé ; **echeance** : conseil municipal du 22 octobre 2026
- **action** : Demander au SIEV une date de reprogrammation des horloges ; **responsable** : S. Marchal ; **echeance** : non fixée
- **action** : Consulter la gendarmerie sur l'extinction nocturne ; **responsable** : C. Benoît ; **echeance** : avant fin octobre 2026
- **action** : Poser les 2 arceaux vélo ; **responsable** : services techniques (régie) ; **echeance** : avant fin novembre 2026
- **action** : Chiffrer les deux options de bancs (2 ou 4) ; **responsable** : S. Marchal ; **echeance** : prochaine commission, mardi 17 novembre 2026
- **action** : Vérifier le reliquat du budget voirie 2026 pour le trottoir rue des Lavandières et revenir vers J.-P. Morel ; **responsable** : S. Marchal ; **echeance** : non fixée
- **action** : Confirmer le motif d'éviction de la 3e offre (Toitures du Val) ; **responsable** : S. Marchal ; **echeance** : non fixée

**pieges** :

- L'attribution du marché n'est PAS décidée par la commission (avis seulement)
- Couverture Delmas, moins-disante, n'est pas retenue
- Extinction dans tous les lotissements (proposition initiale) : NON retenue, seulement les Tilleuls
- Extinction à partir de minuit : proposée par L. Fontaine, NON retenue
- Réunion publique avec les habitants des Tilleuls : évoquée, aucun responsable, non décidée
- Passage de tout le parc en LED (environ 380 k€) : renvoyé au débat budgétaire, rien décidé
- Nombre de bancs (2 ou 4) : non décidé
- Végétalisation de la place : renvoyée au projet 2027-2028 ; l'étude n'est pas lancée, aucune date ne doit apparaître
- Réfection définitive du trottoir rue des Lavandières : ni décidée ni datée
- Chemin de la Garenne : compétence à vérifier, rien décidé
- Panneau d'affichage de l'école : commande déjà en cours, pas une décision de la séance
- F. Leclerc n'a pas donné de pouvoir
- Le conseil municipal a lieu le 22 octobre, pas le 20 (erratum)


### Provenance

- **source** : Notes fictives rédigées pour l'évaluation (commune, personnes, entreprises et montants imaginaires) ; **consulte_le** : 2026-10-12

**Licence** : Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce

---

## LC-001 · Langage clair · facile

### Entrée

- **consigne** : Réécris ce texte en langage clair pour un usager, sans perdre d'information.

**texte** :

```text
Vous devez payer le forfait de post-stationnement (FPS) dans un délai de 3 mois. Le délai court à partir de la notification de l'avis de paiement. La date
limite de paiement est indiquée sur l'avis de paiement.
Si vous ne payez pas le forfait de post-stationnement (FPS) dans un délai de 3 mois, le montant est majoré. Le délai de 3 mois court à partir de la
notification de l'avis de paiement. Un titre exécutoire est émis et vous recevez un avertissement vous invitant à payer le FPS et la majoration.
Le montant de la majoration est fixé à 20 % du montant du FPS impayé restant dû, sans pouvoir être inférieur à 50 €.
Vous devez payer le FPS impayé et la majoration dans un délai d'1 mois à partir de l'envoi de l'avertissement pour bénéficier d'une diminution de 20 % de la
majoration. Si vous ne respectez pas ce délai, le comptable public peut mettre en œuvre des actions en recouvrement. Vous risquez des poursuites sur vos biens,
comptes bancaires, salaires, véhicules...
Si vous avez des difficultés à payer le forfait de post-stationnement (FPS) majoré, vous pouvez demander un délai de paiement ou une remise gracieuse.
Adressez-vous à la trésorerie dont les coordonnées sont précisées sur l'avertissement, seule compétente pour accorder un délai de paiement.
```

- **nb_mots** : 217

### Référence

**informations_a_conserver** :

- Le FPS se paie dans un délai de 3 mois à partir de la notification de l'avis de paiement
- La date limite figure sur l'avis de paiement
- Sans paiement dans les 3 mois : majoration, émission d'un titre exécutoire et envoi d'un avertissement
- Majoration = 20 % du FPS impayé restant dû, au minimum 50 €
- Payer FPS + majoration dans 1 mois après l'envoi de l'avertissement donne droit à une diminution de 20 % de la majoration
- Au-delà : le comptable public peut engager le recouvrement (biens, comptes bancaires, salaires, véhicules)
- Délai de paiement ou remise gracieuse : s'adresser à la trésorerie indiquée sur l'avertissement, seule compétente pour un délai

**termes_juridiques_a_conserver** :

- forfait post-stationnement (FPS)
- avis de paiement
- titre exécutoire
- majoration
- avertissement
- comptable public
- remise gracieuse
- trésorerie


### Provenance

- **source** : MediaTech AgentPublic/service-public, fiche F34440 « Forfait post-stationnement en cas de stationnement non payé » (chunks 5, 7, 8, 9, 10) ; **url** : https://www.service-public.gouv.fr/particuliers/vosdroits/F34440 ; **consulte_le** : 2026-10-12

**Licence** : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)

---

## LC-002 · Langage clair · difficile

### Entrée

- **consigne** : Réécris ces articles en langage clair pour expliquer à un usager ce qu'est un accusé de réception et à quoi il sert. Signale les termes juridiques que tu ne simplifies pas.

**texte** :

```text
Article L. 112-3 : Toute demande adressée à l'administration fait l'objet d'un accusé de réception.
Les dispositions de l'alinéa précédent ne sont pas applicables :
1° Aux demandes abusives, notamment par leur nombre ou leur caractère répétitif ou systématique ;
2° Aux demandes, définies par décret en Conseil d'Etat, pour lesquelles l'administration dispose d'un bref délai pour répondre ou qui n'appellent pas d'autre
réponse que le service d'une prestation ou la délivrance d'un document prévus par les lois ou règlements.
Les modalités d'application du présent article sont fixées par décret en Conseil d'Etat.
Article R. 112-5 : L'accusé de réception prévu par l'article L. 112-3 comporte les mentions suivantes :
1° La date de réception de la demande et la date à laquelle, à défaut d'une décision expresse, celle-ci sera réputée acceptée ou rejetée ;
2° La désignation, l'adresse postale et, le cas échéant, électronique, ainsi que le numéro de téléphone du service chargé du dossier ;
3° Le cas échéant, les informations mentionnées à l'article L. 114-5, dans les conditions prévues par cet article.
Il indique si la demande est susceptible de donner lieu à une décision implicite de rejet ou à une décision implicite d'acceptation. Dans le premier cas,
l'accusé de réception mentionne les délais et les voies de recours à l'encontre de la décision. Dans le second cas, il mentionne la possibilité offerte au
demandeur de se voir délivrer l'attestation prévue à l'article L. 232-3.
Article L. 112-6 : Les délais de recours ne sont pas opposables à l'auteur d'une demande lorsque l'accusé de réception ne lui a pas été transmis ou ne comporte
pas les indications exigées par la réglementation.Le défaut de délivrance d'un accusé de réception n'emporte pas l'inopposabilité des délais de recours à
[… tronqué : 2 lignes de plus, texte complet dans le JSONL]
```

- **nb_mots** : 317

### Référence

**informations_a_conserver** :

- Toute demande adressée à l'administration fait l'objet d'un accusé de réception (L. 112-3)
- Exceptions : demandes abusives (nombre, caractère répétitif ou systématique) et demandes définies par décret en Conseil d'État (bref délai de réponse, ou simple prestation ou délivrance d'un document prévus par les textes)
- L'accusé de réception indique la date de réception de la demande et la date à laquelle, sans décision expresse, elle sera réputée acceptée ou rejetée
- Il indique le service chargé du dossier : désignation, adresse postale, le cas échéant électronique, et numéro de téléphone
- Il précise si le silence vaut rejet (et alors mentionne délais et voies de recours) ou acceptation (et alors la possibilité d'obtenir l'attestation prévue à l'article L. 232-3)
- Sans accusé de réception transmis ou complet, les délais de recours ne sont pas opposables au demandeur (L. 112-6)
- Exception : ils restent opposables si une décision expresse a été régulièrement notifiée avant la naissance de la décision implicite

**termes_juridiques_a_conserver** :

- accusé de réception
- décision implicite d'acceptation
- décision implicite de rejet
- décision expresse
- délais et voies de recours
- opposables / inopposabilité
- décret en Conseil d'État
- notifiée


### Provenance

- **source** : MediaTech AgentPublic/legi, Code des relations entre le public et l'administration, article L112-3 (en vigueur depuis 2016-01-01) ; **url** : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367338 ; **note** : URL Légifrance construite à partir de l'identifiant LEGIARTI (site non joignable en lecture automatique : HTTP 403) ; **consulte_le** : 2026-10-12
- **source** : MediaTech AgentPublic/legi, Code des relations entre le public et l'administration, article R112-5 (en vigueur depuis 2016-01-01) ; **url** : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031369981 ; **note** : URL Légifrance construite à partir de l'identifiant LEGIARTI (site non joignable en lecture automatique : HTTP 403) ; **consulte_le** : 2026-10-12
- **source** : MediaTech AgentPublic/legi, Code des relations entre le public et l'administration, article L112-6 (en vigueur depuis 2016-01-01) ; **url** : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367340 ; **note** : URL Légifrance construite à partir de l'identifiant LEGIARTI (site non joignable en lecture automatique : HTTP 403) ; **consulte_le** : 2026-10-12

**Licence** : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)

---

## CO-001 · Correction · facile

### Entrée

- **consigne** : Corrige l'orthographe, la grammaire et la typographie de ce texte. Ne modifie rien d'autre.

**texte** :

```text
Madame, Monsieur,

Nous vous informons que la médiathèque municipale sera fermé du lundi 2 novembre au samedi 7 novembre 2026 inclus, afin de permettre la réalisation de travaus
de mise en accessibilité. Pendant cette période, les documents emprunter pourrons être déposés dans la boîte de retour situé à l'entrée du bâtiment. Aucune
pénalitée de retard ne sera appliquée aux usagers concernés.

Durant la fermeture, l'espace numérique de l'hôtel de ville, au rez-de-chaussée, accueillera les personnes qui souhaitent consulter la presse ou accéder à
internet, aux horaires habituels d'ouverture de la mairie.

Les réservations effectués avant la fermeture seront conservées et mises à votre disposition des la réouverture, le mardi 10 novembre à 10 heures. Les agents
de la médiathèque restent joignables par courriel pour toute question relative à votre abonnement ou à vos prêts en cours.

Nous vous remercions de votre compréhension et vous prions d'agréer, Madame, Monsieur, l'expression de nos salutations distinguées.

La direction de la médiathèque
```

- **nb_mots** : 158

### Référence

**fautes** :

| # | position | erreur | correction | type |
|---|---|---|---|---|
| 1 | 74-79 | fermé | fermée | accord du participe passé |
| 2 | 170-177 | travaus | travaux | orthographe lexicale |
| 3 | 241-250 | emprunter | empruntés | confusion é/er |
| 4 | 251-259 | pourrons | pourront | conjugaison |
| 5 | 297-302 | situé | située | accord du participe passé |
| 6 | 334-343 | pénalitée | pénalité | orthographe lexicale |
| 7 | 628-637 | effectués | effectuées | accord du participe passé |
| 8 | 704-707 | des | dès | accent / homophone |
- **nb_fautes** : 8

**texte_corrige_reference** :

```text
Madame, Monsieur,

Nous vous informons que la médiathèque municipale sera fermée du lundi 2 novembre au samedi 7 novembre 2026 inclus, afin de permettre la réalisation de travaux
de mise en accessibilité. Pendant cette période, les documents empruntés pourront être déposés dans la boîte de retour située à l'entrée du bâtiment. Aucune
pénalité de retard ne sera appliquée aux usagers concernés.

Durant la fermeture, l'espace numérique de l'hôtel de ville, au rez-de-chaussée, accueillera les personnes qui souhaitent consulter la presse ou accéder à
internet, aux horaires habituels d'ouverture de la mairie.

Les réservations effectuées avant la fermeture seront conservées et mises à votre disposition dès la réouverture, le mardi 10 novembre à 10 heures. Les agents
de la médiathèque restent joignables par courriel pour toute question relative à votre abonnement ou à vos prêts en cours.

Nous vous remercions de votre compréhension et vous prions d'agréer, Madame, Monsieur, l'expression de nos salutations distinguées.

La direction de la médiathèque
```

- **note_positions** : debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte

### Provenance

- **source** : Avis aux usagers d'une médiathèque municipale (texte fictif) ; **consulte_le** : 2026-10-12

**Licence** : Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce

---

## CO-002 · Correction · difficile

### Entrée

- **consigne** : Corrige l'orthographe, la grammaire et la typographie de ce texte. Ne modifie rien d'autre.

**texte** :

```text
Objet : organisation des permanences d'accueil pendant les congés de fin d'année

Comme chaque année, les permanences d'accueil seront assurées par roulement entre le 21 décembre 2026 et le 1er janvier 2027. Les agents qui se sont porté
volontaires lors de la réunion du 6 octobre recevrons leur planning définitif au plus tard le 20 novembre. Quelque soient les contraintes de chacun, il est
indispensable que l'accueil est ouvert tous les jours ouvrées de 9 heures à 12 heures.

Les demandes de congés que vous avez déposé avant le 15 octobre seront examinés en priorité. Au delà de cette date, elles ne pourront être acceptées que si la
continuité du service est garantie. Bien que le nombre de volontaires est encore insuffisant, nous avons choisi de ne pas imposer de permanence aux agents à
temps partiel.

Les responsables d'équipe veilleront à ce que leur collaborateurs disposent des consignes nécessaires. Une fiche récapitulative, que nous vous avons transmis
par courriel, précise les numéros d'astreinte et la conduite a tenir en cas d'incident. Nous vous remercions de bien vouloir la conserver et la consulter avant
chaque permanence.

Pour toute question, vous pouvez vous adresser au secrétariat de la direction des ressources humaines.
```

- **nb_mots** : 200

### Référence

**fautes** :

| # | position | erreur | correction | type |
|---|---|---|---|---|
| 1 | 231-236 | porté | portés | accord du participe passé (être) |
| 2 | 281-290 | recevrons | recevront | conjugaison |
| 3 | 344-358 | Quelque soient | Quelles que soient | quel que / quelque |
| 4 | 421-424 | est | soit | subjonctif après « il est indispensable que » |
| 5 | 447-454 | ouvrées | ouvrés | accord de l'adjectif |
| 6 | 518-524 | déposé | déposées | accord du participe passé (avoir, COD antéposé) |
| 7 | 552-560 | examinés | examinées | accord du participe passé |
| 8 | 574-581 | Au delà | Au-delà | trait d'union |
| 9 | 710-713 | est | soit | subjonctif après « bien que » |
| 10 | 859-863 | leur | leurs | accord de « leur » |
| 11 | 962-970 | transmis | transmise | accord du participe passé (avoir, COD antéposé) |
| 12 | 1021-1022 | a | à | homophone a/à |
- **nb_fautes** : 12

**texte_corrige_reference** :

```text
Objet : organisation des permanences d'accueil pendant les congés de fin d'année

Comme chaque année, les permanences d'accueil seront assurées par roulement entre le 21 décembre 2026 et le 1er janvier 2027. Les agents qui se sont portés
volontaires lors de la réunion du 6 octobre recevront leur planning définitif au plus tard le 20 novembre. Quelles que soient les contraintes de chacun, il est
indispensable que l'accueil soit ouvert tous les jours ouvrés de 9 heures à 12 heures.

Les demandes de congés que vous avez déposées avant le 15 octobre seront examinées en priorité. Au-delà de cette date, elles ne pourront être acceptées que si
la continuité du service est garantie. Bien que le nombre de volontaires soit encore insuffisant, nous avons choisi de ne pas imposer de permanence aux agents
à temps partiel.

Les responsables d'équipe veilleront à ce que leurs collaborateurs disposent des consignes nécessaires. Une fiche récapitulative, que nous vous avons transmise
par courriel, précise les numéros d'astreinte et la conduite à tenir en cas d'incident. Nous vous remercions de bien vouloir la conserver et la consulter avant
chaque permanence.

Pour toute question, vous pouvez vous adresser au secrétariat de la direction des ressources humaines.
```

- **note_positions** : debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte

### Provenance

- **source** : Note interne de service sur les permanences de fin d'année (texte fictif) ; **consulte_le** : 2026-10-12

**Licence** : Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce

---

## RS-001 · Résumé · facile

### Entrée

- **consigne** : Fais un résumé court (3 à 5 phrases) de ce document pour un collègue d'accueil.
- **longueur_demandee** : courte (3 à 5 phrases)

**document** :

```text
Les ressources de la famille ne doivent pas dépasser un certain plafond. Pour la rentrée scolaire 2026, le revenu net catégoriel de l'année 2024 sert de
référence. Le plafond des ressources à ne pas dépasser pour bénéficier de l'ARS varie selon le nombre d' enfants à charge :
Cas 1: 28 956 €:
Cas 2: 35 638 €:
Cas 3 enfants ou +: 42 320 € + 6 682 € par enfant supplémentaire:
Le plafond est identique, quelle que soit la situation de la famille bénéficiaire. (Attention: En cas de léger dépassement du plafond, une allocation
dégressive appelée allocation différentielle , calculée en fonction des revenus, peut être versée.)
L'enfant doit avoir entre 6 et 18 ans. Ainsi, pour la rentrée scolaire 2026, l'enfant doit être né entre le 16 septembre 2008 et le 31 décembre 2020 (inclus).
Cas Cas général: L'enfant doit être scolarisé ou inscrit au Cned à la rentrée 2026. (À savoir: si votre enfant est instruit dans la famille, vous n'avez pas
droit à l'ARS.)
Cas Enfant en apprentissage: Si votre enfant est en apprentissage et que sa rémunération dépasse un certain plafond , vous ne pouvez pas bénéficier de l'ARS.
Cas Enfant scolarisé et confié par le juge à l'aide sociale à l'enfance: Si votre enfant scolarisé est confié par le juge à l'aide sociale à l'enfance (Ase) ou
à un service ou établissement sanitaire ou d'éducation, l'ARS sera conservée sur un compte bloqué auprès de la Caisse des dépôts et consignations. Elle sera
versée à l'enfant, à sa demande, quand il sera majeur, pour l'accompagner dans son autonomie.
Les montants versés pour la rentrée 2026 varient selon l'âge de l'enfant au 31 décembre 2025 :
[… tronqué : 15 lignes de plus, texte complet dans le JSONL]
```

- **nb_mots** : 521

### Référence

**points_cles_reference** :

- L'ARS est soumise à un plafond de ressources (revenus 2024) : 28 956 € (1 enfant), 35 638 € (2 enfants), 42 320 € + 6 682 € par enfant supplémentaire (3 enfants ou plus) ; une allocation différentielle est possible en cas de léger dépassement
- L'enfant doit avoir entre 6 et 18 ans (né entre le 16 septembre 2008 et le 31 décembre 2020) et être scolarisé ou inscrit au Cned (pas d'ARS pour l'instruction en famille)
- Montants rentrée 2026 selon l'âge au 31 décembre 2025 : 426,87 € (6-10 ans), 450,41 € (11-14 ans), 466,02 € (15-18 ans), après CRDS
- Versement à partir du 18 août 2026 (4 août 2026 à La Réunion)


### Provenance

- **source** : MediaTech AgentPublic/service-public, fiche F1878 « Allocation de rentrée scolaire (ARS) », cas général (chunks 2, 3, 4, 5, 7) ; **url** : https://www.service-public.gouv.fr/particuliers/vosdroits/F1878 ; **consulte_le** : 2026-10-12

**Licence** : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)

---

## RS-002 · Résumé · difficile

### Entrée

- **consigne** : Résume ce document en version moyenne (150 à 200 mots) pour les élus de la commission urbanisme.
- **longueur_demandee** : moyenne (150 à 200 mots)

**document** :

```text
Les parcs de stationnement extérieurs d'une superficie supérieure à 1 500 m2 en France métropolitaine, en Guadeloupe et à la Martinique devront être équipés,
sur au moins la moitié de leur superficie, d'ombrières produisant de l'énergie renouvelable. L’obligation s’appliquera aux parcs de stationnement extérieurs
d'une superficie supérieure à 1 000 m2 à La Réunion et d'une superficie supérieure à 2 500 m2 en Guyane. L'obligation concernera les parcs de stationnement
existants. Les propriétaires de ces parcs seront responsables de la mise en œuvre de cette obligation. Lorsque le parc de stationnement extérieur est géré en
concession ou en délégation de service public ou en application d'une autorisation d'occupation du domaine public, les obligations mentionnées dans cette fiche
s'appliquent au concessionnaire, au délégataire ou au titulaire de l'autorisation. (À noter: À l'occasion de leur construction ou de rénovations lourdes, les
parcs de stationnement extérieurs de plus de 500 m2 doivent également intégrer sur au moins 50 % de leur surface des dispositifs d'ombrage et de gestion des
eaux pluviales. Une fiche dédiée à ces obligations est disponible .)
Dans certains cas, les propriétaires de parcs de stationnement adjacents peuvent mutualiser leur obligation. Les parcs de stationnement sont considérés
adjacents lorsqu'ils appartiennent à la même unité foncière. Connaître les conditions de mutualisation des obligations pour les propriétaires de parcs de
stationnement adjacents: Lorsque plusieurs parcs de stationnement sont adjacents, les propriétaires peuvent mutualiser leur obligation, d'un commun accord dont
ils doivent attester. La mutualisation est possible sous réserve que la superficie des ombrières réalisées corresponde à la somme des ombrières devant être
installées sur chacun des parcs de stationnement concernés. L'attestation d'accord indique les conditions techniques de la mise en œuvre de cette
mutualisation. Exemple: 2 parcs de stationnement de même superficie sont adjacents et leurs propriétaires décident de mutualiser leur obligation. Pour
respecter l'obligation de couvrir 50 % de la surface totale des 2 parcs d'ombrières photovoltaïques, ils couvrent d'ombrières :
[… tronqué : 33 lignes de plus, texte complet dans le JSONL]
```

- **nb_mots** : 885

### Référence

**points_cles_reference** :

- Les parcs de stationnement extérieurs existants de plus de 1 500 m² (métropole, Guadeloupe, Martinique ; 1 000 m² à La Réunion, 2 500 m² en Guyane) doivent avoir des ombrières produisant de l'énergie renouvelable sur au moins la moitié de leur superficie
- L'obligation pèse sur le propriétaire, ou sur le concessionnaire, le délégataire ou le titulaire de l'autorisation d'occupation du domaine public
- Les propriétaires de parcs adjacents (même unité foncière) peuvent mutualiser l'obligation par un accord attesté
- Exceptions : parcs ombragés par des arbres sur la moitié de la surface (1 arbre pour 3 emplacements) ou produisant autrement une énergie renouvelable équivalente
- Calendrier hors concession : 1er juillet 2026 pour 10 000 m² et plus, 1er juillet 2028 entre 1 500 et 10 000 m² ; en concession, selon la date du contrat ; délai supplémentaire possible accordé par la préfecture
- Les ombrières intègrent des panneaux photovoltaïques sur toute leur partie supérieure
- Sanction jusqu'à 20 000 € (1 500 à 10 000 m²) ou 40 000 € (10 000 m² et plus), après procédure contradictoire, renouvelable chaque année jusqu'à la mise en conformité


### Provenance

- **source** : MediaTech AgentPublic/service-public, fiche F38187 « Ombrage des parcs de stationnement existants de plus de 1 500 m2 » (chunks 2, 9, 12, 13, 14, 15) ; **url** : https://entreprendre.service-public.gouv.fr/vosdroits/F38187 ; **consulte_le** : 2026-10-12

**Licence** : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)

---

## CT-001 · Courrier type · facile

### Entrée

- **type** : demande de pièces
- **objet** : Dossier d'inscription à l'accueil périscolaire incomplet
- **elements_connus** : 
  - **destinataire** : Mme Sophie Lemaire
  - **date_reception_dossier** : 2 octobre 2026
  - **pieces_manquantes** : 
    - attestation d'assurance responsabilité civile
    - justificatif de domicile de moins de 3 mois
  - **delai_pour_fournir** : 15 jours à compter de la réception du courrier
  - **service** : Service enfance-jeunesse de la mairie
- **consigne** : Rédige le courrier au format administratif français.

### Référence

**elements_obligatoires** :

- En-tête de l'expéditeur (mairie, service enfance-jeunesse)
- Bloc destinataire (Mme Sophie Lemaire)
- Lieu et date
- Objet
- Référence du dossier (en emplacement)
- Formule d'appel « Madame, »
- Rappel de la réception du dossier le 2 octobre 2026
- Liste des 2 pièces manquantes, exactement
- Délai de 15 jours à compter de la réception du courrier
- Modalités de transmission (en emplacement si non fournies)
- Coordonnées du service pour toute question (en emplacement)
- Formule de politesse
- Signature : nom et qualité du signataire (en emplacement)

**champs_a_laisser_en_emplacement** :

- [Adresse de l'usager]
- [Commune]
- [Référence du dossier]
- [Adresse, téléphone, courriel du service]
- [Nom et qualité du signataire]
- [Date du courrier]

**valeurs_interdites** :

- toute adresse postale, tout numéro de téléphone ou courriel inventé
- toute pièce supplémentaire non demandée
- tout nom de signataire inventé


### Provenance

- **source** : Demande d'agent rédigée pour l'évaluation (scénario fictif) ; **consulte_le** : 2026-10-12

**Licence** : Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce

---

## CT-002 · Courrier type · difficile

### Entrée

- **type** : accusé de réception
- **objet** : Demande d'autorisation d'occupation temporaire du domaine public (terrasse de café)
- **elements_connus** : 
  - **demandeur** : M. Karim Benali, gérant du café « Le Central »
  - **date_reception** : 5 octobre 2026
  - **service_charge_du_dossier** : Service urbanisme et domaine public
  - **regime_du_silence** : selon le service, le silence gardé pendant 2 mois vaudra rejet de la demande
- **consigne** : Rédige l'accusé de réception conforme au code des relations entre le public et l'administration (article R. 112-5).

### Référence

**elements_obligatoires** :

- Date de réception de la demande : 5 octobre 2026
- Date à laquelle, à défaut de décision expresse, la demande sera réputée rejetée (5 décembre 2026, ou formulation équivalente « deux mois après la réception »)
- Désignation du service chargé du dossier : service urbanisme et domaine public
- Adresse postale, le cas échéant électronique, et numéro de téléphone du service (en emplacement)
- Mention que la demande est susceptible de donner lieu à une décision implicite de rejet
- Mention des délais et voies de recours contre la décision implicite de rejet (contenu en emplacement si non fourni)
- Format administratif : en-tête, destinataire, objet, référence, formule d'appel, formule de politesse, signature

**base_reglementaire** :

- **article** : CRPA R. 112-5
- **url** : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031369981
- **texte** : L'accusé de réception prévu par l'article L. 112-3 comporte les mentions suivantes :
1° La date de réception de la demande et la date à laquelle, à défaut d'une décision expresse, celle-ci sera réputée acceptée ou rejetée ;
2° La désignation, l'adresse postale et, le cas échéant, électronique, ainsi que le numéro de téléphone du service chargé du dossier ;
3° Le cas échéant, les informations mentionnées à l'article L. 114-5, dans les conditions prévues par cet article.
Il indique si la demande est susceptible de donner lieu à une décision implicite de rejet ou à une décision implicite d'acceptation. Dans le premier cas, l'accusé de réception mentionne les délais et les voies de recours à l'encontre de la décision. Dans le second cas, il mentionne la possibilité offerte au demandeur de se voir délivrer l'attestation prévue à l'article L. 232-3.

**champs_a_laisser_en_emplacement** :

- [Adresse du demandeur]
- [Commune]
- [Référence du dossier]
- [Adresse postale du service]
- [Courriel du service]
- [Téléphone du service]
- [Nom et qualité du signataire]
- [Délais et voies de recours]

**valeurs_interdites** :

- adresse, téléphone ou courriel du service inventés
- annonce d'une décision implicite d'acceptation (le silence vaut rejet ici)
- délai de recours chiffré présenté comme certain sans source fournie
- mention de l'attestation de l'article L. 232-3 (réservée au cas d'acceptation implicite)


### Provenance

- **source** : Demande d'agent rédigée pour l'évaluation (scénario fictif) ; **consulte_le** : 2026-10-12
- **source** : MediaTech AgentPublic/legi, CRPA article R112-5 ; **url** : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031369981 ; **role** : liste des mentions obligatoires ; **consulte_le** : 2026-10-12

**Licence** : Scénario : Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce. Article R. 112-5 : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face).

---

## NR-001 · Non-régression · facile

### Entrée

> Une réunion commence à 9 h 45 et dure 2 h 50. Elle est suivie d'une pause déjeuner de 45 minutes. À quelle heure reprend le travail ? Explique ton calcul.

### Référence

- **reponse_reference** : 13 h 20 (9 h 45 + 2 h 50 = 12 h 35 ; 12 h 35 + 45 min = 13 h 20).
**criteres** :

- Résultat final : 13 h 20
- Étape intermédiaire juste (12 h 35)
- Réponse en français correct


### Provenance

- **source** : Question rédigée pour l'évaluation (raisonnement, vérifiable par calcul) ; **consulte_le** : 2026-10-12

**Licence** : Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce

---

## NR-002 · Non-régression · moyen

### Entrée

> Reformule en une seule phrase, dans un registre soutenu adapté à un courrier administratif, sans changer le sens : « On n'a pas pu traiter votre dossier parce qu'il manquait des papiers, renvoyez-les vite. »

### Référence

- **reponse_reference** : Votre dossier n'a pas pu être traité, car il était incomplet ; nous vous remercions de bien vouloir nous transmettre les pièces manquantes dans les meilleurs délais.
**criteres** :

- Une seule phrase
- Registre soutenu : vouvoiement, pas de « on » familier, pas de « papiers » ni de « vite »
- Sens conservé : dossier non traité, cause = pièces manquantes, demande d'envoi rapide
- Aucun ajout : pas de délai chiffré, pas de liste de pièces, pas de nom de service inventés
- Orthographe et ponctuation correctes


### Provenance

- **source** : Consigne rédigée pour l'évaluation ; **consulte_le** : 2026-10-12

**Licence** : Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce
