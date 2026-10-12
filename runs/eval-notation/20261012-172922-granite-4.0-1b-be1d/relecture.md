# Relecture des verdicts

47 item(s) de l'échantillon de relecture. Les Scores restent « non relus » tant que `relecture-validee.json` (objet JSON avec une clé `date` ISO) n'est pas déposé dans ce run.

## CO-001 (CO, facile)

### Entrée

```text
{
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "nb_mots": 135,
  "texte": "Si votre enfant est nouveau dans un établissement, vous devez participer à une réunion d'information dans les jours qui suive la rentrée scolaire. Des réunions peuvent aussi être organisés au cours de l'année scolaire, notamment pour vous informer sur la situation de la classe, sur une procédure spécifique ou sur les possibilités d'orientation. Si votre enfant est en grande difficulté scolaire, son établissement peut également vous convié à des réunions pour envisager ensemble des solutions. Si vous rencontrer un problème lié à la pédagogie, adressez vous au professeur principal de la classe. Si votre problème concerne les absences et les questions de comportement, adressez-vous au conseiller principal d'éducation (CPE). Le chef d'établissement et les enseignants doivent faire le nécessaire pour répondre à vos demandes d'information et de rendez-vous. Tout réponse négative doit présenter les motifs."
}
```

### Sortie (statut ok)

```text
Texte corrigé :
Si votre enfant est nouveau dans un établissement, vous devez participer à une réunion d'information dans les jours qui suivent la rentrée scolaire. Des réunions peuvent également être organisées au cours de l'année scolaire, notamment pour vous informer sur la situation de la classe, sur une procédure spécifique ou sur les possibilités d'orientation. Si votre enfant est en grande difficulté scolaire, son établissement peut également vous convier à des réunions pour envisager ensemble des solutions. Si vous rencontrez un problème lié à la pédagogie, adressez-vous au professeur principal de la classe. Si votre problème concerne les absences et les questions de comportement, adressez-vous au conseiller principal d'éducation (CPE). Le chef d'établissement et les enseignants doivent faire le nécessaire pour répondre à vos demandes d'information et de rendez-vous. Tout réponse négative doit présenter les motifs.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 5,
  "fautes": 6,
  "fautes_corrigees": [
    true,
    true,
    true,
    true,
    true,
    false
  ],
  "mots_inseres_hors_faute": 2,
  "mots_modifies_hors_faute": 1,
  "mots_texte": 135,
  "rappel": 0.8333,
  "taux_hors_faute": 0.0222
}
```

### Verdicts

Aucun verdict.

## CO-008 (CO, moyen)

### Entrée

```text
{
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "nb_mots": 174,
  "texte": "Note à l'attention des agents du service urbanisme\n\nObjet : modalités du télétravail à compter du 1er décembre 2026\n\nÀ la suite de la réunion du comité social territorial du 15 octobre, le télétravail seras ouvert aux agents du service urbanisme dont les missions le permettent. Chaque agent pourra télétravailler un jour par semaine, choisit en accord avec son responsable. Les jours de permanence au guichet, le mardi et le jeudi, ne pourront pas être télétravailler.\n\nLes demandes devront être adressé au service des ressources humaines avant le 13 novembre, au moyen du formulaire joint. Un ordinateur portable et un casque sera remis à chaque agent dont la demande aura été accepter. Les agents s'engagent à rester joignables pendant les plages fixes, de 9 heures à 12 heures et de 14 heures à 16 heures.\n\nUne période d'adaptation de trois mois est prévue. À l'issue de cette période, un bilan sera fais avec chaque agent afin de vérifier que l'organisation retenue convient a la fois à l'agent et au service.\n\nLa direction générale des services"
}
```

### Sortie (statut ok)

```text
Note à l'attention des agents du service urbanisme

Objet : modalités du télétravail à compter du 1er décembre 2026

À la suite de la réunion du comité social territorial du 15 octobre, le télétravail sera ouvert aux agents du service urbanisme dont les missions le permettent. Chaque agent pourra télétravailler un jour par semaine, en accord avec son responsable. Les jours de permanence au guichet, le mardi et le jeudi, ne peuvent pas être télétravaillés.

Les demandes devront être adressées au service des ressources humaines avant le 13 novembre, au moyen du formulaire joint. Un ordinateur portable et un casque seront remis à chaque agent dont la demande aura été acceptée. Les agents s'engagent à rester joignables pendant les plages fixes, de 9 heures à 12 heures et de 14 heures à 16 heures.

Une période d'adaptation de trois mois est prévue. À l'issue de cette période, un bilan sera réalisé avec chaque agent afin de vérifier que l'organisation retenue convient à la fois à l'agent et au service.

La direction générale des services

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 6,
  "fautes": 8,
  "fautes_corrigees": [
    true,
    false,
    true,
    true,
    true,
    true,
    false,
    true
  ],
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 1,
  "mots_texte": 174,
  "rappel": 0.75,
  "taux_hors_faute": 0.0057
}
```

### Verdicts

Aucun verdict.

## CO-011 (CO, difficile)

### Entrée

```text
{
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "nb_mots": 159,
  "texte": "Si vous êtes admit à un concours d'accès à la fonction publique et si vous étiez au paravant dirigeant d'une société ou d'une association à but lucrative, vous pouvez continuer à exercer cette activité de dirigeant pendant 1 an, renouvelables une fois, à partir de votre recrutement dans la fonction publique. Cela s'appliquent aussi si vous êtes recruté en temps que contractuel dans la fonction publique. Vous devez présenter une déclaration écrite à votre autorité hiérarchique des votre nomination en tant que fonctionnaire stagiaire ou avant la signature de votre contrat. Votre déclaration mentionnes la forme et l'objet social de l'entreprise ou de l'association, son secteur et son branche d'activité. La poursuite de cette activité de dirigeant doit être compatibles avec vos obligations de service. Elle ne doit pas porter atteinte au fonctionnement normal, à l'indépendance, à la neutralitée du service ou aux principes déontologiques. Cette activité ne doit pas non-plus vous placer dans une situation de conflit d'intérêts."
}
```

### Sortie (statut ok)

```text
Si vous êtes admis à un concours d'accès à la fonction publique et si vous étiez auparavant chef d'une société ou d'une association à but lucratif, vous pouvez continuer à exercer cette activité de chef pendant 1 an, renouvelables une fois, à partir de votre recrutement dans la fonction publique. Cela s'applique également si vous êtes recruté en tant que contractuel dans la fonction publique. Vous devez présenter une déclaration écrite à votre autorité hiérarchique de votre nomination en tant que fonctionnaire stagiaire ou avant la signature de votre contrat. Votre déclaration mentionne la forme et l'objet social de l'entreprise ou de l'association, son secteur et son domaine d'activité. La poursuite de cette activité de chef doit être compatible avec vos obligations de service. Elle ne doit pas porter atteinte au fonctionnement normal, à l'indépendance, à la neutralité du service ou aux principes déontologiques. Cette activité ne doit pas non plus vous placer dans une situation de conflit d'intérêts.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 8,
  "fautes": 12,
  "fautes_corrigees": [
    true,
    false,
    true,
    false,
    true,
    true,
    false,
    true,
    false,
    true,
    true,
    true
  ],
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 4,
  "mots_texte": 159,
  "rappel": 0.6667,
  "taux_hors_faute": 0.0252
}
```

### Verdicts

Aucun verdict.

## CR-003 (CR, facile)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de ce conseil d'école : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 468,
  "notes": "1er conseil d'école – école élémentaire du Moulin-Neuf, Sermoise-la-Haute – jeudi 8/10/2026 – 18h – salle polyvalente de l'école\nPrésents :\n- Mme Dufresne, directrice (préside)\n- enseignants : M. Arnaud (CP), Mme Lemaire (CE1, secrétaire de séance), Mme Sow (CE2-CM1), M. Perrin (CM2)\n- représentants des parents élus : Mme Caron, M. Delattre, Mme Aït Ali, + M. Brun (suppléant, siège à la place de Mme Joubert, titulaire, excusée)\n- mairie : M. Vasseur (adjoint aux affaires scolaires)\n- DDEN : Mme Roussel\nExcusés : M. Kieffer (IEN), Mme Joubert (parent titulaire)\n\n1. Élections des représentants de parents (vendredi 2/10)\nParticipation 41 % (38 % l'an dernier). 4 sièges, une seule liste. Dufresne remercie les parents.\n\n2. Effectifs / organisation\nDufresne annonce 121 élèves… puis se reprend : 112 élèves (121 c'était l'an dernier). 5 classes, 1 double niveau (CE2-CM1, 24 élèves). Pas d'AESH supplémentaire obtenue malgré 2 notifications MDPH, demande renouvelée auprès de l'IEN.\n\n3. Règlement intérieur\nModif proposée : ouverture du portail à 8h20 au lieu de 8h25 (trop de monde sur le trottoir). Mme Aït Ali demande 8h15 → enseignants contre (service de surveillance). Pas retenu.\nVOTE : règlement intérieur adopté avec ouverture à 8h20 – unanimité.\n→ Dufresne le transmet aux familles avant le vendredi 16 octobre (cahier de liaison + ENT).\n\n4. Sécurité / PPMS\nExercice incendie fait le 22/09, évacuation en 2 min 40. Exercice PPMS « attentat-intrusion » fixé au jeudi 19 novembre (date communiquée par la directrice, familles prévenues la veille seulement).\n\n5. Projets de l'année\n- Classe de découverte CM2 (22 élèves, 3 jours, mer, mai 2027), coût estimé 9 800 €. Coop scolaire 2 500 €, familles 90 €/enfant max (soit 1 980 €). Il manque environ 5 300 €. Vasseur : « on étudiera la demande au budget 2027 mais je ne peux rien promettre ». → le projet n'est maintenu que si la subvention municipale est obtenue.\n→ Perrin dépose la demande de subvention en mairie avant le 30 novembre.\n- Marché de Noël de l'école : vendredi 11 décembre, 16h30, dans la cour. Bénéfices à la coopérative scolaire. Accord du conseil. Mme Caron coordonne les stands avec les parents élus.\n\n6. Travaux / bâtiment (mairie)\n- Chauffage de la classe de CE2-CM1 : 16 °C le matin. Vasseur : le service technique intervient pendant les vacances de la Toussaint.\n- Parents demandent un abri vélos. Vasseur prend note, rien de prévu.\n\n7. Cantine / périscolaire\nQuestions des parents sur le bruit à la cantine. Vasseur évoque des panneaux acoustiques « à voir l'an prochain », pas de chiffrage. Rien décidé.\n\n8. Questions des parents\n- M. Delattre propose de lancer un pédibus vers le lotissement des Prés. Tout le monde trouve l'idée bonne mais aucun parent ne se porte volontaire pour l'organiser ce soir. À reparler.\n- Vitesse rue de l'Église aux heures de sortie : demande d'un ralentisseur. Vasseur : rue départementale, la commune doit saisir le département ; il « en parlera au maire ». Pas d'engagement.\n\nPV rédigé par Mme Lemaire, diffusé aux membres sous 15 jours.\nProchain conseil d'école : mardi 2 février 2027, 18h.\nFin 19h50."
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "Mme Dufresne (directrice, présidente du conseil d'école)",
    "M. Arnaud (enseignant de CP)",
    "Mme Lemaire (enseignante de CE1, secrétaire de séance)",
    "Mme Sow (enseignante de CE2-CM1)",
    "M. Perrin (enseignant de CM2)",
    "Représentants des parents élus : Mme Caron, M. Delattre, Mme Aït Ali, M. Brun (suppléant, siège à la place de Mme Joubert)",
    "M. Vasseur (adjoint aux affaires scolaires, mairie)",
    "Mme Roussel (DDEN)",
    "Excusés : M. Kieffer (IEN), Mme Joubert (représentante titulaire des parents)"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Règlement intérieur adopté à l'unanimité, avec ouverture du portail à 8 h 20 au lieu de 8 h 25"
    },
    {
      "ref": "D2",
      "texte": "Exercice PPMS « attentat-intrusion » fixé au jeudi 19 novembre 2026 (familles prévenues la veille)"
    },
    {
      "ref": "D3",
      "texte": "Marché de Noël de l'école le vendredi 11 décembre 2026 à 16 h 30 dans la cour, bénéfices à la coopérative scolaire (accord du conseil)"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Transmettre le règlement intérieur aux familles (cahier de liaison et ENT)",
      "responsable": "Mme Dufresne",
      "echeance": "avant le vendredi 16 octobre 2026"
    },
    {
      "ref": "A2",
      "action": "Déposer en mairie la demande de subvention pour la classe de découverte des CM2",
      "responsable": "M. Perrin",
      "echeance": "avant le 30 novembre 2026"
    },
    {
      "ref": "A3",
      "action": "Coordonner les stands du marché de Noël avec les parents élus",
      "responsable": "Mme Caron",
      "echeance": "non fixée"
    },
    {
      "ref": "A4",
      "action": "Intervenir sur le chauffage de la classe de CE2-CM1",
      "responsable": "service technique de la mairie",
      "echeance": "pendant les vacances de la Toussaint"
    },
    {
      "ref": "A5",
      "action": "Rédiger et diffuser le procès-verbal aux membres",
      "responsable": "Mme Lemaire",
      "echeance": "sous 15 jours"
    }
  ],
  "pieges": [
    "Effectif : 112 élèves et non 121 (chiffre corrigé en séance)",
    "Ouverture du portail à 8 h 15 : demandée par Mme Aït Ali, NON retenue",
    "Classe de découverte des CM2 : maintenue seulement si la subvention municipale est obtenue ; la mairie ne s'est pas engagée",
    "Abri vélos : demandé par les parents, rien de prévu",
    "Panneaux acoustiques à la cantine : évoqués, ni chiffrés ni décidés",
    "Pédibus : idée de M. Delattre, aucun responsable désigné, NON décidé",
    "Ralentisseur rue de l'Église : aucun engagement (rue départementale)",
    "M. Brun siège comme suppléant de Mme Joubert, excusée"
  ]
}
```

### Sortie (statut ok)

```text
**Compte rendu du conseil d'École**

**Objet** : Conseil d'École de l'école élémentaire du Moulin-Neuf, Sermoise-la-Haute, le 8/10/2026.

**Participants** :
- Mme Dufresne, directrice (présidente)
- M. Arnaud (CP), Mme Lemaire (CE1, secrétaire de séance), Mme Sow (CE2-CM1), M. Perrin (CM2)
- Représentants des parents élus : Mme Caron, M. Delattre, Mme Aït Ali, M. Brun (suppléant, siège de Mme Joubert, titulaire, excusée)
- Mairie : M. Vasseur (adjoint aux affaires scolaires)
- DDEN : Mme Roussel

**Points abordés** :
1. Élections des représentants de parents (vendredi 2/10)
   - Participation 41 % (38 % l'an dernier). 4 sièges, une seule liste. Dufresne remercie les parents.
2. Effectifs / organisation
   - Dufresne annonce 121 élèves (actuellement 112). 5 classes, 1 double niveau (CE2-CM1, 24 élèves). Pas d'AESH supplémentaire obtenue malgré 2 notifications MDPH, demande renouvelée auprès de l'IEN.
3. Règlement intérieur
   - Modif proposé : ouverture du portail à 8h20 au lieu de 8h25 (trop de monde sur le trottoir). Mme Aït Ali demande 8h15 → enseignants contre (service de surveillance). Pas retenu.
   - VOTE : règlement intérieur adopté avec ouverture à 8h20 – unanimité.
   - Dufresne transmet le règlement aux familles avant le vendredi 16 octobre (cahier de liaison + ENT).
4. Sécurité / PPMS
   - Exercice incendie fait le 22/09, évacuation en 2 min 40. Exercice PPMS « attentat-intrusion » fixé au jeudi 19 novembre (date communiquée par la directrice, familles prévenues la veille seulement).
5. Projets de l'année
   - Classe de découverte CM2 (22 élèves, 3 jours, mer, mai 2027), coût estimé 9 800 €. Coop scolaire 2 500 €, familles 90 €/enfant max (soit 1 980 €). Il manque environ 5 300 €. Vasseur : « on étudiera la demande au budget 2027 mais je ne peux rien promettre ». → le projet n'est maintenu que si la subvention municipale est obtenue.
   - Marché de Noël de l'école : vendredi 11 décembre, 16h30, dans la cour. Bénéfices à la coopérative scolaire. Accord du conseil d'école. Mme Caron coordonne les stands avec les parents élus.
6. Travaux / bâtiment (mairie)
   - Chauffage de la classe de CE2-CM1 : 16 °C le matin. Vasseur : le service technique intervient pendant les vacances de la Toussaint.
   - Parents demandent un abri vélos. Vasseur prend note, rien de prévu.
7. Cantine / périscolaire
   - Questions des parents sur le bruit à la cantine. Vasseur évoque des panneaux acoustiques « à voir l'an prochain », pas de chiffrage. Rien décidé.
8. Questions des parents
   - M. Delattre propose de lancer un pédibus vers le lotissement des Prés. Tout le monde trouve l'idée bonne mais aucun parent ne se porte volontaire pour l'organiser ce soir. À reparler.
   - Vitesse rue de l'Église aux heures de sortie : demande d'un ralentisseur. Vasseur : rue départementale, la commune doit saisir le département ; il « en parlera au maire ». Pas d'engagement.

**Décisions** :
- Élections des représentants de parents (vendredi 2/10)
- Adoption du règlement intérieur avec ouverture du portail à 8h20
- Maintien du projet de classe de découver

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Présent : « VOTE : règlement intérieur adopté avec ouverture à 8h20 – unanimité », repris dans la section Décisions.
  - D2 : 1 — Présent dans les points abordés : « Exercice PPMS « attentat-intrusion » fixé au jeudi 19 novembre (… familles prévenues la veille seulement) ».
  - D3 : 1 — Présent dans les points abordés : « Marché de Noël de l'école : vendredi 11 décembre, 16h30, dans la cour. Bénéfices à la coopérative scolaire. Accord du conseil d'école ».
  - A1 : 1 — Présent avec responsable et échéance : « Dufresne transmet le règlement aux familles avant le vendredi 16 octobre (cahier de liaison + ENT) ».
  - A2 : 0 — Absent : la ligne « Perrin dépose la demande de subvention en mairie avant le 30 novembre » a disparu du point 5.
  - A3 : 1 — Présent : « Mme Caron coordonne les stands avec les parents élus » ; aucune échéance n'est fixée dans les notes.
  - A4 : 1 — Présent : « le service technique intervient pendant les vacances de la Toussaint ».
  - A5 : 0 — Absent : aucune mention de la rédaction ni de la diffusion du PV par Mme Lemaire sous 15 jours.
- `absence_invention` : 0 — La section Décisions présente « Maintien du projet de classe de découver[te] » comme décidé, alors que ce maintien reste conditionné à une subvention non obtenue (piège) ; elle range aussi les élections parmi les décisions et déforme l'effectif en écrivant « Dufresne annonce 121 élèves (actuellement 112) ».
- `structure` : 0 — La sortie est tronquée : la section Actions est absente et la section Décisions est inachevée.
- Inventions : Décision « Maintien du projet de classe de découver[te] » présentée sans la condition de la subvention municipale; Les élections des représentants de parents présentées comme une décision du conseil; « Dufresne annonce 121 élèves (actuellement 112) » : présente 121 comme le chiffre annoncé, alors qu'il a été corrigé en séance
- Confiance : moyenne

## CR-004 (CR, moyen)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de cette commission d'appel d'offres : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 926,
  "notes": "SIAEP de la Haute-Sorelle (syndicat intercommunal d'adduction d'eau potable, 14 communes)\nCommission d'appel d'offres (CAO) – jeudi 1er octobre 2026 – 14h – siège du syndicat, salle du comité\nNotes prises par N. Rivière (resp. marchés publics)\n\nMembres à voix délibérative :\n- M. Chaumont, 1er vice-président, représentant le président (arrêté de délégation du 12/06/2026) → préside\n- titulaires : Mme Lebrun, M. Fabre, M. Guillot, Mme Teixeira\n- suppléant : M. Hamel, siège en remplacement de M. Pasquier (titulaire, excusé)\n→ 6 membres à voix délib. présents sur 6, quorum atteint.\nVoix consultative / assistent :\n- Mme Rivière (responsable marchés publics, rapporteure)\n- M. Kessler (bureau d'études Hydraulis Conseil, AMO), pour le pt 1 uniquement\n- comptable public (SGC de Sorelle) : convoqué, absent, pas de représentant\n- DDPP (concurrence) : convoquée, ne siège pas (courrier reçu, pas d'observation)\n\nOrdre du jour : 1/ AOO « compteurs d'eau » (2 lots) – attribution ; 2/ avis sur avenant n°2 réservoir de la Butte ; 3/ divers\n\n1. Appel d'offres ouvert – fourniture et pose de compteurs d'eau à radio-relève (accord-cadre à bons de commande, 4 ans)\nRappel Rivière : avis publié au BOAMP et au JOUE le 10/07, remise des offres le 4/09 à 12h, ouverture des plis le 7/09. Critères : prix 50 %, valeur technique 40 %, performance environnementale 10 %.\nKessler présente le rapport d'analyse (envoyé aux membres le 25/09).\n\nLot 1 – fourniture des compteurs (env. 9 500 compteurs sur 4 ans)\n4 offres reçues, toutes régulières :\n- Hydrocompt SAS : note 87,5/100\n- Aqualis Mesure : 82,1\n- Compteurs du Rhin : 76,4\n- Metrisol : 64,9 (prix bas mais délais de livraison 16 sem., valeur technique faible)\nMontant estimatif sur DQE Hydrocompt : Kessler dit « 421 300 € HT », puis corrige après vérif du tableau : 412 300 € HT (inversion de chiffres dans sa présentation, le rapport écrit est juste).\nFabre demande pourquoi pas Metrisol, moins cher. Kessler : note technique 18/40, pas de garantie sur la durée de vie des piles radio. Fabre satisfait de la réponse.\nDÉCISION CAO : lot 1 attribué à Hydrocompt SAS (offre économiquement la plus avantageuse, 87,5/100, 412 300 € HT estimatifs sur 4 ans) – unanimité (6 voix).\n→ Rivière envoie les courriers de rejet aux 3 autres candidats dès demain (vendredi 2/10), avec les motifs et le délai de suspension.\n→ notification du marché à Hydrocompt par Rivière, pas avant le mardi 13/10 (fin du délai de standstill de 11 jours).\n\nLot 2 – pose des compteurs et des têtes radio\n2 offres :\n- Réseaux Sorelle TP : offre irrégulière (DPGF non signée et pas de mémoire technique) → éliminée\n- Canalis Ouest : régulière mais 186 000 € HT pour une estimation de 142 000 € HT (+31 %) → offre inacceptable (crédits budgétaires insuffisants)\nKessler suggère de « négocier un peu » avec Canalis. Rivière rappelle qu'on ne négocie pas en appel d'offres ouvert. Chaumont : non.\nMme Teixeira se demande si l'estimation n'était pas trop basse (prix des fournitures de raccordement en hausse). Kessler reconnaît qu'elle date de 2025.\nDÉCISION CAO : lot 2 déclaré infructueux – unanimité.\nSuite : nouvelle consultation sur la base d'une estimation mise à jour. Débat : Hamel propose de passer en procédure négociée sans publicité avec Canalis seul ; Rivière : pas possible ici car la seule offre régulière est inacceptable pour raison budgétaire et les conditions du marché vont changer (estimation revue) → pas retenu. Chaumont tranche : relance d'un appel d'offres ouvert, même allotissement, DCE mis à jour.\n→ Kessler met à jour l'estimation du lot 2 et la transmet à Rivière avant le vendredi 23/10.\n→ Rivière publie le nouvel avis avant le vendredi 6/11.\nKessler quitte la séance après le pt 1 (14h55).\nM. Guillot quitte aussi à 15h (autre réunion) → 5 membres à voix délib., quorum toujours atteint (Chaumont vérifie).\n\n2. Avis sur l'avenant n°2 – marché de travaux « réhabilitation du réservoir de la Butte » (titulaire : Bâtiments & Ouvrages du Val, marché initial 492 000 € HT)\nRivière : travaux d'étanchéité supplémentaires découverts après vidange de la cuve (fissures sur la coupole). Montant avenant n°2 : 38 400 € HT. Avec l'avenant n°1 (9 600 € HT, déjà passé), cumul des avenants : 48 000 € HT, soit +9,8 % du marché initial.\nAvenant > 5 % → avis préalable de la CAO obligatoire avant le vote du comité syndical.\nLebrun : pourquoi ce n'était pas vu au diagnostic ? Rivière : cuve pleine au moment du diagnostic, inspection seulement visuelle.\nFabre : le prix unitaire de l'étanchéité a-t-il été comparé ? Rivière : oui, prix du BPU du marché, pas de prix nouveau sauf pour la résine de reprise de fissures (prix nouveau n°3, 112 €/m²).\nL'entreprise demande aussi une prolongation de délai de 3 semaines. Chaumont : ce n'est pas l'objet de l'avenant présenté aujourd'hui, la CAO ne se prononce pas sur le délai ; il faut d'abord un mémoire justificatif de l'entreprise.\n→ Rivière demande à l'entreprise un mémoire justifiant la prolongation de délai (pas de date fixée).\nAVIS de la CAO : favorable à l'avenant n°2 (38 400 € HT) – 3 pour (Chaumont, Lebrun, Teixeira), 2 abstentions (Fabre, Hamel : veulent l'avis du maître d'œuvre écrit).\nRappel Chaumont : c'est un avis, c'est le comité syndical qui autorise la signature de l'avenant.\n→ Rivière inscrit l'avenant n°2 à l'ordre du jour du comité syndical du jeudi 15 octobre.\n→ Rivière joint au dossier du comité du 15/10 l'avis écrit du maître d'œuvre (demande de Fabre).\n\n3. Divers\n- Fabre souhaite qu'on mette des clauses d'insertion sociale dans les prochains marchés de travaux du syndicat. Chaumont favorable « sur le principe », mais il faut en parler en comité syndical. Pas de décision, personne de chargé du sujet pour l'instant.\n- Rivière rappelle que le PV de la CAO doit être signé par tous les membres présents : elle le fait circuler pour signature d'ici le jeudi 8/10. M. Guillot signera pour le pt 1 seulement.\n- Prochaine CAO : jeudi 19 novembre, 14h (ouverture des plis éventuelle du lot 2 si les délais le permettent, sinon décembre).\nFin 15h50."
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "M. Chaumont (1er vice-président, représentant le président, préside)",
    "Membres titulaires : Mme Lebrun, M. Fabre, M. Guillot (parti à 15 h, après le point 1), Mme Teixeira",
    "M. Hamel (suppléant, en remplacement de M. Pasquier)",
    "Excusé : M. Pasquier (titulaire)",
    "Mme N. Rivière (responsable des marchés publics, rapporteure, prise de notes)",
    "M. Kessler (Hydraulis Conseil, AMO), pour le point 1 uniquement",
    "Absents : comptable public (SGC de Sorelle) ; DDPP, qui ne siège pas"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Lot 1 (fourniture des compteurs d'eau à radio-relève) attribué à Hydrocompt SAS, offre la mieux notée (87,5/100), pour un montant estimatif de 412 300 € HT sur 4 ans : unanimité (6 voix)"
    },
    {
      "ref": "D2",
      "texte": "Lot 2 (pose des compteurs et des têtes radio) déclaré infructueux (une offre irrégulière, une offre inacceptable à 186 000 € HT pour 142 000 € HT estimés) : unanimité"
    },
    {
      "ref": "D3",
      "texte": "Relance du lot 2 par un nouvel appel d'offres ouvert, même allotissement, avec un DCE et une estimation mis à jour"
    },
    {
      "ref": "D4",
      "texte": "Avis favorable à l'avenant n° 2 du marché de réhabilitation du réservoir de la Butte (38 400 € HT ; cumul des avenants 48 000 € HT, +9,8 %) : 3 pour, 2 abstentions (M. Fabre, M. Hamel). Il s'agit d'un avis : le comité syndical autorise la signature"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Envoyer les courriers de rejet motivés aux 3 candidats non retenus du lot 1",
      "responsable": "Mme Rivière",
      "echeance": "vendredi 2 octobre 2026"
    },
    {
      "ref": "A2",
      "action": "Notifier le marché du lot 1 à Hydrocompt SAS",
      "responsable": "Mme Rivière",
      "echeance": "pas avant le mardi 13 octobre 2026 (fin du délai de suspension)"
    },
    {
      "ref": "A3",
      "action": "Mettre à jour l'estimation du lot 2 et la transmettre à Mme Rivière",
      "responsable": "M. Kessler",
      "echeance": "avant le vendredi 23 octobre 2026"
    },
    {
      "ref": "A4",
      "action": "Publier le nouvel avis d'appel d'offres pour le lot 2",
      "responsable": "Mme Rivière",
      "echeance": "avant le vendredi 6 novembre 2026"
    },
    {
      "ref": "A5",
      "action": "Inscrire l'avenant n° 2 à l'ordre du jour du comité syndical",
      "responsable": "Mme Rivière",
      "echeance": "comité syndical du jeudi 15 octobre 2026"
    },
    {
      "ref": "A6",
      "action": "Joindre au dossier du comité syndical l'avis écrit du maître d'œuvre sur l'avenant n° 2",
      "responsable": "Mme Rivière",
      "echeance": "comité syndical du jeudi 15 octobre 2026"
    },
    {
      "ref": "A7",
      "action": "Demander à l'entreprise un mémoire justifiant la prolongation de délai de 3 semaines",
      "responsable": "Mme Rivière",
      "echeance": "non fixée"
    },
    {
      "ref": "A8",
      "action": "Faire signer le procès-verbal de la CAO par les membres présents",
      "responsable": "Mme Rivière",
      "echeance": "d'ici le jeudi 8 octobre 2026"
    }
  ],
  "pieges": [
    "Montant du lot 1 : 412 300 € HT et non 421 300 € HT (erreur orale corrigée en séance)",
    "Metrisol, offre la moins chère du lot 1, n'est pas retenue",
    "Négociation avec Canalis Ouest : suggérée par M. Kessler, écartée (interdite en appel d'offres ouvert)",
    "Procédure négociée sans publicité avec Canalis Ouest seul : proposée par M. Hamel, NON retenue",
    "Avenant n° 2 : simple avis de la CAO ; la signature n'est pas encore autorisée (comité syndical du 15 octobre)",
    "Prolongation de délai de 3 semaines : la CAO ne s'est PAS prononcée, rien n'est accordé",
    "Clauses d'insertion sociale : favorable « sur le principe », NON décidées, personne n'en est chargé",
    "M. Guillot et M. Kessler sont partis après le point 1 ; l'avis sur l'avenant est rendu à 5 votants",
    "M. Hamel siège comme suppléant de M. Pasquier ; le comptable public est absent",
    "Prochaine CAO du jeudi 19 novembre : l'ouverture des plis du lot 2 n'est qu'éventuelle"
  ]
}
```

### Sortie (statut ok)

```text
**Compte rendu de la réunion de la Commission d'appel d'offres**

**Participants :**
- M. Chaumont, 1er vice-président, représentant le président (arrêté de délégation du 12/06/2026) → préside
- Mme Lebrun, M. Fabre, M. Guillot, Mme Teixeira (titulaires)
- M. Hamel (suppléant, siège en remplacement de M. Pasquier, titulaire, excusé)
- N. Rivière (responsable des marchés publics, rapporteure)
- M. Kessler (bureau d'études Hydraulis Conseil, AMO), pour le lot 1 uniquement
- Comptable public (SGC de Sorelle) : convoqué, absent, pas de représentant
- DDPP (concurrence) : convoquée, ne siège pas (courrier reçu, pas d'observation)

**Points abordés :**

1. **Lot 1 - Fourniture de compteurs d'eau**
   - Rappel Rivière : avis publié au BOAMP et au JOUE le 10/07, remise des offres le 4/09 à 12h, ouverture des plis le 7/09.
   - Critères : prix 50 %, valeur technique 40 %, performance environnementale 10 %.
   - 4 offres reçues, toutes régulières.
     - Hydrocompt SAS : note 87,5/100
     - Aqualis Mesure : 82,1
     - Compteurs du Rhin : 76,4
     - Metrisol : 64,9 (prix bas mais délais de livraison 16 sem., valeur technique faible)
   - Kessler présente le rapport d'analyse (envoyé aux membres le 25/09).
   - Montant estimatif sur DQE Hydrocompt : Kessler dit « 421 300 € HT », puis corrige après vérif du tableau : 412 300 € HT (inversion de chiffres dans sa présentation, le rapport écrit est juste).
   - Fabre demande pourquoi pas Metrisol, moins cher. Kessler : note technique 18/40, pas de garantie sur la durée de vie des piles radio. Fabre satisfait de la réponse.
   - DÉCISION CAO : lot 1 attribué à Hydrocompt SAS (offre économiquement la plus avantageuse, 87,5/100, 412 300 € HT estimatifs sur 4 ans) – unanimité (6 voix).
   - Rivière envoie les courriers de rejet aux 3 autres candidats dès demain (vendredi 2/10), avec les motifs et le délai de suspension.
   - Notification du marché à Hydrocompt par Rivière, pas avant le mardi 13/10 (fin du délai de standstill de 11 jours).

2. **Lot 2 - Pose des compteurs et des têtes radio**
   - 2 offres :
     - Réseaux Sorelle TP : offre irrégulière (DPGF non signée et pas de mémoire technique) → éliminée
     - Canalis Ouest : régulière mais 186 000 € HT pour une estimation de 142 000 € HT (+31 %) → offre inacceptable (crédits budgétaires insuffisants)
   - Kessler suggère de « négocier un peu » avec Canalis. Rivière rappelle qu'on ne négocie pas en appel d'offres ouvert.
   - Chaumont : non.
   - Mme Teixeira se demande si l'estimation n'était pas trop basse (prix des fournitures de raccordement en hausse). Kessler reconnaît qu'elle date de 2025.
   - DÉCISION CAO : lot 2 déclaré infructueux – unanimité.
   - Suite : nouvelle consultation sur la base d'une estimation mise à jour. Hamel propose de passer en procédure négociée sans publicité avec Canalis seul ; Rivière : pas possible ici car la seule offre régulière est inacceptable pour raison budgétaire et les conditions du marché vont changer (estimation revue) → pas retenu.
   - Chaumont tranche : relance d'un appel d'offres ouvert, même allotissement, DCE mis à jour.
   - Kessler met à jour l'estimation du lot 2 et la transmet à Rivière avant le vendredi 23/10.
   - Riv

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « DÉCISION CAO : lot 1 attribué à Hydrocompt SAS (offre économiquement la plus avantageuse, 87,5/100, 412 300 € HT estimatifs sur 4 ans) – unanimité (6 voix) » : la décision est présente avec le bon montant corrigé.
  - D2 : 1 — « DÉCISION CAO : lot 2 déclaré infructueux – unanimité » figure, avec les motifs (offre irrégulière, offre inacceptable à 186 000 € HT pour 142 000 € HT).
  - D3 : 1 — « Chaumont tranche : relance d'un appel d'offres ouvert, même allotissement, DCE mis à jour » figure, avec l'estimation mise à jour.
  - D4 : 0 — La sortie est tronquée avant le point 2 : l'avis favorable sur l'avenant n° 2 est absent.
  - A1 : 1 — « Rivière envoie les courriers de rejet aux 3 autres candidats dès demain (vendredi 2/10) » : l'action, la responsable et l'échéance sont présentes.
  - A2 : 1 — « Notification du marché à Hydrocompt par Rivière, pas avant le mardi 13/10 » : l'action est complète.
  - A3 : 1 — « Kessler met à jour l'estimation du lot 2 et la transmet à Rivière avant le vendredi 23/10 » : l'action est complète.
  - A4 : 0 — La sortie s'interrompt sur « Riv » : la publication du nouvel avis avant le 6/11 est absente.
  - A5 : 0 — L'action est absente (sortie tronquée avant le point 2).
  - A6 : 0 — L'action est absente (sortie tronquée avant le point 2).
  - A7 : 0 — L'action est absente (sortie tronquée avant le point 2).
  - A8 : 0 — L'action est absente (sortie tronquée avant le point 3).
- `absence_invention` : 1 — La sortie ne contient aucune décision, action, date ou chiffre absent des notes, et les pièges (421 300 €, négociation, procédure négociée) sont présentés comme écartés ; seule imprécision : « pour le lot 1 uniquement », alors que les notes disent « pt 1 », qui couvre les deux lots.
- `structure` : 0 — Seules les sections Participants et Points abordés sont présentes ; la sortie est tronquée et ne contient pas de sections Décisions ni Actions.
- Inventions : aucune
- Confiance : moyenne

## CR-006 (CR, difficile)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de cette séance du comité social territorial : participants, points abordés, décisions et avis rendus, actions (responsable, échéance).",
  "nb_mots": 5159,
  "transcription": "Transcription de l'enregistrement audio — Comité social territorial (CST) du Conseil départemental de la Sarvèze\nSéance du jeudi 1er octobre 2026 — Hôtel du Département, Valdrieu, salle Ardoise — début de l'enregistrement 9 h 34\n(transcription automatique relue par le secrétariat du CST ; les passages inaudibles sont signalés entre crochets)\n\nM. Castagnet (vice-président chargé des ressources humaines, président du CST) : Bon. Bonjour à toutes et à tous. On va commencer, il est déjà neuf heures trente-cinq passées et l'ordre du jour est chargé. Je vous rappelle qu'on enregistre, comme d'habitude, pour le procès-verbal. Monsieur Oudin, est-ce que vous pouvez faire l'appel, s'il vous plaît, qu'on vérifie le quorum ?\n\nM. Oudin (directeur des ressources humaines) : Oui. Alors pour le collège des représentants de la collectivité : monsieur Castagnet, présent ; madame Ferrand, présente ; monsieur Benslimane, présent ; madame Arnaud, directrice générale adjointe ressources, présente ; et moi-même. Donc cinq. Madame Jourdan, conseillère départementale, est excusée, et elle n'est pas remplacée aujourd'hui. Pour le collège des représentants du personnel : pour la CGT, monsieur Rouvière, madame Sissoko, monsieur Pallas, présents. Pour FO, madame Escande, monsieur Vasseur, présents. Pour la CFDT, madame Thibaud, présente ; monsieur Courtade est excusé, il est remplacé par sa suppléante, madame Moulin, qui siège donc avec voix délibérative. Pour l'UNSA, monsieur Lhermite, présent. Ça fait huit représentants du personnel sur huit, le quorum est atteint.\n\nM. Castagnet : Merci. Je salue aussi les experts qui vont nous rejoindre selon les points : monsieur Galmiche, directeur des routes et des mobilités, est là pour le point 1 ; le docteur Kerbrat, médecin du travail, et madame Maréchal, conseillère de prévention, arriveront pour le point sur les risques psychosociaux. Le secrétariat de séance est assuré par monsieur Oudin, et le secrétaire adjoint, c'est toujours monsieur Rouvière. Ça vous va, monsieur Rouvière ?\n\nM. Rouvière (CGT, secrétaire adjoint) : Ça me va. Mais avant de commencer, monsieur le président, j'ai une déclaration liminaire au nom de l'intersyndicale… enfin, de la CGT et de FO, pas de toute l'intersyndicale.\n\nM. Castagnet : Allez-y, mais je vous demande d'être raisonnable sur la durée, on a cinq points.\n\nM. Rouvière : Je serai bref. Alors, nous voulons dire notre inquiétude face à la succession des réorganisations dans les services. En moins de deux ans, on a eu la réorganisation des maisons départementales des solidarités, celle de la direction de l'autonomie, et aujourd'hui on nous présente la fusion de centres d'exploitation routière. Les agents ont l'impression qu'on les déplace comme des pions, et le baromètre social qu'on va voir tout à l'heure le montre très bien. On demande que chaque réorganisation soit précédée d'une vraie étude d'impact sur les conditions de travail, présentée en formation spécialisée avant de venir en CST. Voilà. La déclaration complète sera remise au secrétariat pour être annexée au procès-verbal.\n\nM. Castagnet : Très bien, elle sera annexée. Je ne vais pas répondre point par point maintenant, on aura l'occasion d'en discuter sur le point 1. Madame Escande, vous vouliez ajouter quelque chose ?\n\nMme Escande (FO) : Juste que FO s'associe à la déclaration, et qu'on regrette d'avoir reçu les documents du point 2 seulement huit jours avant. C'est le minimum réglementaire, mais pour une charte de télétravail qui touche plus de mille agents, c'est court.\n\nM. Castagnet : C'est noté. On essaiera de faire mieux. Bien. Premier point, l'approbation du procès-verbal de la séance du 2 juillet. Est-ce qu'il y a des remarques ?\n\nMme Escande : Oui. Page six, sur les astreintes, il est écrit que FO « approuve le nouveau régime d'astreinte ». Ce n'est pas ce que j'ai dit. J'ai dit que FO approuvait la revalorisation, mais pas l'élargissement des astreintes aux agents de catégorie C du service des bâtiments. Je demande que ce soit corrigé.\n\nM. Oudin : On a l'enregistrement, on vérifiera, mais de mémoire vous avez raison. On peut écrire : « FO approuve la revalorisation des indemnités d'astreinte mais s'oppose à leur extension aux agents de catégorie C du service des bâtiments ».\n\nMme Escande : Voilà, c'est exactement ça.\n\nM. Castagnet : D'autres remarques ? Non. Je mets aux voix le procès-verbal ainsi modifié. Qui est contre ? Qui s'abstient ? Donc unanimité des deux collèges, le PV du 2 juillet est approuvé avec la correction de madame Escande. Monsieur Oudin, vous mettrez la version corrigée en ligne ?\n\nM. Oudin : Oui, elle sera mise en ligne sur l'intranet avec les autres PV d'ici la fin octobre.\n\nM. Castagnet : Bien. Alors, point 1, la réorganisation de la direction des routes et des mobilités, et plus précisément la fusion du centre d'exploitation routière de Lauzières avec celui de Montclar-d'Orbe. Monsieur Galmiche, je vous laisse présenter.\n\nM. Galmiche (directeur des routes et des mobilités) : Merci monsieur le président. Bonjour à tous. Je vais faire court sur le contexte, vous avez le dossier. Aujourd'hui, l'agence routière Nord compte trois centres d'exploitation : Lauzières, Montclar-d'Orbe et Saint-Fréjus. Le centre de Lauzières, c'est quatorze agents, dont un chef de centre, dans un bâtiment de 1978 qui n'est plus aux normes, avec notamment de l'amiante dans la toiture du hangar et des vestiaires qui ne permettent pas d'accueillir des femmes dans des conditions correctes. On a deux agentes d'exploitation qui sont arrivées l'an dernier et qui se changent dans un bureau, ce n'est pas acceptable. La réfection complète du bâtiment a été chiffrée à 1,9 million d'euros. En face, le centre de Montclar-d'Orbe, qui est à dix-neuf kilomètres, a été rénové en 2022 et peut accueillir les quatorze agents avec une extension modulaire. Donc la proposition, c'est de regrouper les deux centres à Montclar-d'Orbe, avec une mise en œuvre au 1er janvier 2027. Le linéaire de routes reste le même, les circuits de patrouille sont redécoupés, et on ne supprime aucun poste. Je le redis parce que j'ai entendu des rumeurs : aucun poste supprimé.\n\nM. Pallas (CGT) : Aucun poste supprimé, mais combien de postes non remplacés dans trois ans ?\n\nM. Galmiche : Je ne peux pas vous répondre sur ce qui se passera dans trois ans, je vous réponds sur le projet qui est présenté aujourd'hui.\n\nM. Pallas : Ben justement. Moi je suis agent d'exploitation à Lauzières depuis quatorze ans, je connais le secteur. Le problème, ce n'est pas le bâtiment, tout le monde est d'accord que le bâtiment est pourri. Le problème, c'est la viabilité hivernale. Quand il neige sur le plateau, depuis Montclar, il faut monter le col de la Bessière avant même de commencer à saler. Vous perdez trente, quarante minutes. Et les routes du nord du canton, elles seront traitées en dernier.\n\nM. Galmiche : On a regardé ça. Les nouveaux circuits sont construits pour que le premier passage sur le réseau prioritaire soit fait dans les mêmes délais qu'aujourd'hui…\n\nM. Pallas : Sur le papier.\n\nM. Galmiche : … sur le papier, oui, c'est une étude, je ne vais pas vous dire le contraire. Mais elle a été faite avec les chefs de centre.\n\nM. Castagnet : Laissez finir monsieur Galmiche, s'il vous plaît, vous aurez la parole après.\n\nM. Galmiche : Je termine. Concernant les agents : chacun sera reçu en entretien individuel par la DRH et par moi-même. On a déjà regardé les temps de trajet domicile-travail : pour huit agents sur quatorze, le trajet s'allonge de moins de quinze minutes ; pour quatre agents, entre quinze et trente minutes ; et pour deux agents, c'est plus long, autour de quarante minutes. Pour ceux-là, on étudiera des solutions au cas par cas, éventuellement une mobilité vers Saint-Fréjus s'ils le souhaitent.\n\nMme Escande : Et l'indemnité ? Parce que quand on allonge de quarante minutes le trajet de quelqu'un qui gagne mille six cents euros, ça a un coût. FO demande une prime de restructuration pour l'ensemble des quatorze agents.\n\nM. Oudin : Alors, je précise : il existe une indemnité de restructuration de service prévue par les textes, mais elle est encadrée, elle dépend notamment du changement de résidence administrative et de la distance. On ne peut pas promettre aujourd'hui qu'elle sera versée à tout le monde. Ce qu'on s'engage à faire, c'est d'examiner chaque situation lors des entretiens individuels.\n\nMme Escande : Donc c'est non.\n\nM. Oudin : Ce n'est pas non, c'est : au cas par cas, dans le cadre réglementaire.\n\nMme Escande : Pour les agents, c'est non.\n\nM. Castagnet : Je comprends la demande. Je ne vais pas prendre d'engagement en séance sur un dispositif indemnitaire, il faut qu'on le chiffre. On en reparlera.\n\nMme Thibaud (CFDT) : Moi j'ai deux questions. La première : le calendrier. Pourquoi le 1er janvier ? C'est en plein milieu de la saison de viabilité hivernale. Si on déménage un centre en janvier avec des agents qui ne connaissent pas encore leurs nouveaux circuits, et qu'il tombe vingt centimètres de neige, ça va être le chaos. La deuxième : qu'est-ce qu'on fait du sel ? Il y a un stock à Lauzières qui sert à tout le nord.\n\nM. Galmiche : Sur le sel, on y a pensé. L'idée serait de garder l'aire de stockage de sel de Lauzières comme dépôt avancé pour l'hiver, mais ça suppose que le hangar à sel, qui est un bâtiment séparé, soit utilisable. Il faut qu'on fasse faire un diagnostic. Si le diagnostic est bon, on le garde ; sinon, on stockera tout à Montclar.\n\nMme Thibaud : Et le diagnostic, il sera fait quand ?\n\nM. Galmiche : Il est commandé, on attend la date du bureau d'études. Je ne l'ai pas encore.\n\nMme Thibaud : Et sur le calendrier ?\n\nM. Galmiche : Sur le calendrier… [silence] … je vais laisser le président répondre.\n\nM. Castagnet : Écoutez, sur le calendrier, j'entends l'argument et je le trouve fondé. Je vous propose de modifier le projet : la mise en œuvre de la fusion serait reportée au 1er mars 2027, après le pic de la viabilité hivernale, au lieu du 1er janvier. Monsieur Galmiche, c'est tenable pour vous ?\n\nM. Galmiche : C'est tenable. Ça décale un peu les travaux d'extension, mais c'est tenable.\n\nM. Castagnet : Donc on modifie le projet soumis à l'avis : mise en œuvre au 1er mars 2027.\n\nM. Rouvière : Ça ne change rien sur le fond.\n\nM. Castagnet : Ça change le calendrier, c'est déjà quelque chose.\n\nM. Lhermite (UNSA) : Moi je voudrais dire quelque chose. L'UNSA a rencontré les agents de Lauzières la semaine dernière. Ils ne sont pas tous contre, loin de là. Les deux collègues femmes dont parlait monsieur Galmiche, elles attendent ça depuis un an. Et plusieurs agents habitent plus près de Montclar que de Lauzières, en fait. Donc il ne faut pas présenter ça comme si tout le monde était contre.\n\nM. Pallas : Personne n'a dit que tout le monde était contre.\n\nM. Lhermite : Si, un peu, quand même. [rires]\n\nM. Castagnet : Bon. D'autres interventions ? Madame Sissoko.\n\nMme Sissoko (CGT) : Oui, je voulais revenir sur ce que disait monsieur Galmiche sur les temps de trajet. Vous avez une étude agent par agent ? Parce que nous, on ne l'a pas dans le dossier.\n\nM. Galmiche : On l'a, mais elle est nominative, donc on ne l'a pas jointe.\n\nMme Sissoko : Vous pouvez l'anonymiser.\n\nM. Galmiche : Oui, on peut l'anonymiser. Je vous la transmets.\n\nMme Sissoko : Avant le vote ?\n\nM. Galmiche : Avant le vote d'aujourd'hui, non, ce n'est pas possible matériellement. Mais je vous la transmets avant le prochain CST, celui du 10 décembre.\n\nM. Rouvière : Monsieur le président, je demande une suspension de séance de dix minutes, pour qu'on se concerte entre organisations avant le vote.\n\nM. Castagnet : Accordée. On reprend à dix heures quarante.\n\n[Suspension de séance de 10 h 28 à 10 h 41]\n\nM. Castagnet : On reprend. Monsieur Rouvière, la suspension a été utile ?\n\nM. Rouvière : Elle a été utile, on a échangé. Je fais juste une remarque avant le vote : on aurait aimé que ce projet passe d'abord en formation spécialisée, vu qu'il y a des questions d'amiante, de vestiaires, de conditions de travail. On n'a pas eu ça.\n\nM. Castagnet : Le diagnostic amiante a été présenté à la formation spécialisée en mars, si ma mémoire est bonne.\n\nM. Oudin : En mai. Le 12 mai.\n\nM. Castagnet : En mai, pardon. Bon. Je vous propose de passer au vote. Je rappelle que l'avis porte sur le projet tel que modifié en séance, c'est-à-dire la fusion du centre d'exploitation de Lauzières avec celui de Montclar-d'Orbe, regroupement des quatorze agents à Montclar-d'Orbe, sans suppression de poste, avec une mise en œuvre au 1er mars 2027, et le maintien du dépôt de sel de Lauzières sous réserve du diagnostic. Et je rappelle aussi que le CST rend un avis : la décision appartient ensuite au président du conseil départemental. Collège des représentants du personnel d'abord. Qui est favorable ?\n\nM. Oudin : Une voix pour, monsieur Lhermite, UNSA.\n\nM. Castagnet : Qui s'abstient ?\n\nM. Oudin : Deux abstentions, madame Thibaud et madame Moulin, CFDT.\n\nM. Castagnet : Qui est contre ?\n\nM. Oudin : Cinq contre : monsieur Rouvière, madame Sissoko, monsieur Pallas pour la CGT, madame Escande et monsieur Vasseur pour FO.\n\nM. Castagnet : Donc avis défavorable du collège des représentants du personnel : cinq contre, deux abstentions, un pour. Collège des représentants de la collectivité ?\n\nM. Oudin : Cinq pour, unanimité.\n\nM. Castagnet : Avis favorable du collège employeur. L'avis des représentants du personnel n'étant pas défavorable à l'unanimité, il n'y a pas lieu à une nouvelle consultation. Le dossier sera soumis au président du Département.\n\nMme Escande : Je voudrais juste que le PV mentionne que FO votera contre aussi en commission permanente si le sujet y passe.\n\nM. Castagnet : Madame Escande, FO ne siège pas en commission permanente. [rires] Mais votre position sera notée au PV, bien sûr.\n\nMme Escande : Vous m'avez comprise.\n\nM. Castagnet : Monsieur Galmiche, merci, vous pouvez nous quitter si vous voulez.\n\nM. Galmiche : Merci. Je confirme que l'étude anonymisée partira bien avant le 10 décembre. Et la DRH et moi, on prévoit les entretiens individuels avec les quatorze agents d'ici le 30 novembre.\n\nM. Oudin : Oui, avant le 30 novembre, c'est calé de notre côté.\n\n[Départ de M. Galmiche à 10 h 49]\n\nM. Castagnet : Point 2, la modification de la charte du télétravail. Monsieur Oudin.\n\nM. Oudin : Alors, rapidement, le bilan d'abord. Aujourd'hui, mille quatre cent vingt agents télétravaillent régulièrement sur deux mille huit cent soixante-dix agents… Pardon, je corrige tout de suite, j'ai inversé les chiffres : c'est mille deux cent quarante agents, pas mille quatre cent vingt. Mille deux cent quarante sur deux mille huit cent soixante-dix, donc à peu près 43 %. Le chiffre est juste dans le document, page trois, c'est moi qui me suis trompé.\n\nMme Moulin (CFDT) : Ça me paraissait beaucoup, en effet.\n\nM. Oudin : Oui. Donc la charte actuelle, adoptée en 2022, prévoit un maximum de deux jours fixes par semaine. Ce qu'on vous propose : on garde les deux jours fixes maximum, et on ajoute un forfait annuel de vingt jours flottants, qui peuvent être posés en plus, dans la limite de trois jours télétravaillés sur une même semaine. Ensuite, on clarifie les conditions d'éligibilité des agents à temps partiel : un agent à 80 % pourra télétravailler un jour fixe, plus les jours flottants. Et on fixe un délai de prévenance quand le responsable doit annuler un jour de télétravail pour nécessité de service : aujourd'hui, il n'y a rien dans la charte, on propose vingt-quatre heures. Enfin, l'indemnité forfaitaire de télétravail reste versée au taux réglementaire, pas de changement. Entrée en vigueur au 1er janvier 2027.\n\nM. Vasseur (FO) : Les jours flottants, c'est sur demande de l'agent, ou c'est imposé ?\n\nM. Oudin : Sur demande de l'agent, validée par le responsable, dans l'outil de gestion des temps.\n\nM. Vasseur : Validée comment ? Parce que dans certains services, je vous le dis, les demandes sont refusées sans explication.\n\nM. Oudin : Tout refus devra être motivé, c'est déjà dans la charte, article 6.\n\nM. Vasseur : C'est dans la charte, mais ce n'est pas appliqué. À la direction de l'enfance et de la famille, on a eu trois refus non motivés au printemps.\n\nM. Oudin : Faites-nous remonter les situations, on les regardera.\n\nMme Sissoko : La CGT, elle, demande trois jours fixes. Beaucoup de collectivités autour l'ont fait. Les agents de l'autonomie, les instructeurs APA et PCH, ils font de l'instruction de dossiers toute la journée, ils peuvent le faire de chez eux. Et ils habitent loin, se loger à Valdrieu, c'est cher.\n\nM. Castagnet : Trois jours fixes, ce n'est pas notre position. On a besoin de collectifs de travail. On a eu des retours de managers, des retours aussi du baromètre, sur l'isolement. Donc on reste à deux jours fixes, plus les jours flottants, ce qui permet d'aller jusqu'à trois certaines semaines. C'est un compromis.\n\nMme Sissoko : C'est un compromis que vous faites avec vous-même.\n\nMme Thibaud : La CFDT, de son côté, trouve que le forfait de jours flottants, c'est une vraie avancée, on le demandait depuis deux ans. Par contre, vingt-quatre heures de prévenance pour une annulation, c'est trop court. Quelqu'un qui a organisé la garde de ses enfants autour de son jour de télétravail, si on lui dit la veille à dix-sept heures qu'il doit venir, il ne peut pas. On propose un amendement : quarante-huit heures, sauf urgence dûment justifiée.\n\nM. Castagnet : Monsieur Oudin ?\n\nM. Oudin : Quarante-huit heures, on peut l'accepter. Avec la mention « sauf urgence », bien sûr.\n\nM. Castagnet : Alors on intègre l'amendement de la CFDT : délai de prévenance de quarante-huit heures, sauf urgence.\n\nM. Lhermite : Et les agents des collèges ? Les agents techniques des collèges n'ont pas accès au télétravail, c'est logique pour l'entretien ou la restauration, mais il y a des gestionnaires administratifs, des secrétaires…\n\nM. Oudin : Les agents des collèges qui sont sur des fonctions administratives, c'est un sujet compliqué, parce qu'il y a la double autorité avec le chef d'établissement.\n\nM. Lhermite : Justement, c'est pour ça qu'il faut en parler.\n\nM. Castagnet : On peut regarder ça, oui. Il faudrait sans doute en discuter avec l'Éducation nationale. On regardera.\n\nM. Lhermite : Qui regardera, et quand ?\n\nM. Castagnet : On regardera, monsieur Lhermite. Je ne vais pas vous donner une date aujourd'hui.\n\nM. Rouvière : J'ajoute une chose sur l'indemnité forfaitaire. Elle ne couvre pas l'augmentation de l'électricité. On demande une prise en charge d'une partie de l'abonnement internet.\n\nM. Oudin : Ce n'est pas prévu, et je ne crois pas que ce soit possible juridiquement en dehors du forfait.\n\nM. Castagnet : Ce n'est pas dans le projet. Bien. Est-ce qu'on peut voter ? Je rappelle le projet modifié : maximum deux jours fixes par semaine, forfait annuel de vingt jours flottants, plafond de trois jours télétravaillés par semaine, délai de prévenance de quarante-huit heures sauf urgence pour l'annulation par le responsable, entrée en vigueur au 1er janvier 2027. Collège du personnel, qui est pour ?\n\nM. Oudin : Cinq pour : madame Escande, monsieur Vasseur, madame Thibaud, madame Moulin, monsieur Lhermite.\n\nM. Castagnet : Abstentions ?\n\nM. Oudin : Trois abstentions, la CGT.\n\nM. Castagnet : Contre ? Aucun. Avis favorable du collège du personnel. Collège employeur ?\n\nM. Oudin : Cinq pour.\n\nM. Castagnet : Avis favorable des deux collèges. Merci. La charte modifiée sera…\n\nM. Oudin : Elle sera publiée sur l'intranet avec une note de service avant le 1er décembre, pour que les agents aient le temps de faire leurs demandes pour 2027. C'est moi qui m'en occupe.\n\nMme Escande : Et le bilan ? On avait demandé un bilan régulier.\n\nM. Oudin : Je vous présenterai un bilan au bout d'un an d'application, donc au CST de début 2028.\n\nMme Escande : Début 2028, c'est loin.\n\nM. Castagnet : Un an d'application, c'est le minimum pour avoir du recul. Point 3, les risques psychosociaux. J'invite le docteur Kerbrat et madame Maréchal à nous rejoindre. [bruit de chaises] Monsieur Benslimane, vous deviez partir ?\n\nM. Benslimane (conseiller départemental) : Je dois partir vers onze heures quarante, j'ai la commission d'appel d'offres à midi. Je reste pour le début.\n\nM. Castagnet : Très bien. Docteur Kerbrat.\n\nDr Kerbrat (médecin du travail) : Merci. Alors je vais vous présenter les résultats du baromètre social, qui a été réalisé en mai et juin, et ensuite madame Maréchal vous présentera le projet de plan de prévention. Je précise que ce point est présenté pour information : il n'y a pas d'avis à rendre aujourd'hui sur le plan, qui sera retravaillé en formation spécialisée.\n\nM. Rouvière : C'est bien ce qu'on regrette, d'ailleurs.\n\nDr Kerbrat : Le taux de réponse est de 38 %, ce qui est correct pour une première édition, mais très variable selon les directions. Il est de 61 % à la direction de l'enfance et de la famille, et de 19 % à la direction des routes, où beaucoup d'agents n'ont pas de poste informatique. Les principaux enseignements : la charge de travail est jugée excessive par 54 % des répondants ; 41 % disent avoir été confrontés à des comportements agressifs d'usagers au cours des douze derniers mois, et ce chiffre monte à 72 % dans les maisons départementales des solidarités ; et enfin, 29 % des répondants déclarent un niveau de stress élevé ou très élevé. Je voudrais attirer votre attention sur les MDS, et particulièrement sur la MDS de Saint-Fréjus, où les indicateurs sont nettement dégradés, avec un incident sérieux en août, que vous connaissez.\n\nMme Escande : Oui, on le connaît, une collègue a été menacée à l'accueil. Et je vais être claire : FO demande que la formation spécialisée se rende sur place. Pas dans six mois. Maintenant.\n\nM. Castagnet : Madame Maréchal, la formation spécialisée peut organiser une visite rapidement ?\n\nMme Maréchal (conseillère de prévention) : Oui, une délégation de la formation spécialisée peut se rendre sur place. Je propose le mardi 20 octobre, le matin. Il faut une délégation avec au moins un représentant du personnel et un représentant de la collectivité ; je l'accompagnerai et je m'occupe de l'organisation.\n\nM. Castagnet : Qui se propose ?\n\nM. Rouvière : Moi.\n\nMme Escande : Moi aussi, évidemment.\n\nM. Castagnet : Et pour la collectivité, madame Ferrand, vous pourriez ?\n\nMme Ferrand (conseillère départementale) : Le 20 au matin, oui, je peux.\n\nM. Castagnet : Très bien, donc délégation de la formation spécialisée à la MDS de Saint-Fréjus le mardi 20 octobre au matin : monsieur Rouvière, madame Escande, madame Ferrand, accompagnés de madame Maréchal, qui organise la visite. Le compte rendu de visite sera présenté à la prochaine formation spécialisée.\n\nMme Maréchal : Qui est le jeudi 19 novembre.\n\nM. Castagnet : Le 19 novembre. Bien.\n\nMme Sissoko : Et en attendant, l'agent de sécurité à l'accueil de Saint-Fréjus ? Depuis août, il n'y a toujours rien.\n\nM. Oudin : Un agent de sécurité est présent à titre provisoire les mardis et jeudis, jours de forte affluence, depuis le 14 septembre. C'est déjà en place, ça a été décidé au moment de l'incident.\n\nMme Sissoko : Deux jours sur cinq.\n\nM. Oudin : Pour l'instant, oui. La visite permettra d'évaluer s'il faut étendre.\n\nMme Maréchal : Je continue sur le plan de prévention. Il comporte trois axes. Premier axe : la prévention des violences externes. On propose une formation à la gestion des situations d'agressivité pour tous les agents d'accueil des MDS, environ cent dix agents, avec les premières sessions dès novembre si le plan est validé. Deuxième axe : la charge de travail, avec un travail par direction sur les priorités, piloté par chaque directeur. Troisième axe : l'accompagnement des encadrants, avec un module de formation à la prévention des RPS pour les managers. Et parallèlement, je mets à jour le document unique d'évaluation des risques professionnels, le DUERP, pour intégrer tout ça : l'objectif est d'avoir une version à jour avant le 31 mars 2027.\n\nM. Vasseur : La formation aux agressions, c'est bien, mais ça ne remplace pas des effectifs. À Saint-Fréjus, il manque deux travailleurs sociaux depuis le printemps.\n\nMme Arnaud (directrice générale adjointe ressources) : Les deux postes sont publiés, monsieur Vasseur. On a un problème d'attractivité sur les métiers du social, vous le savez, ce n'est pas propre à la Sarvèze.\n\nM. Vasseur : On le sait. Mais pendant ce temps-là, ce sont les collègues présents qui absorbent les dossiers. Le deuxième axe, la charge de travail, il commence quand ?\n\nMme Maréchal : Il démarrera après la validation du plan, direction par direction. Je n'ai pas encore de calendrier par direction.\n\nM. Rouvière : La CGT a une proposition concrète. On demande la mise en place d'une cellule d'écoute psychologique externe, accessible vingt-quatre heures sur vingt-quatre, comme ça existe dans d'autres départements. Les agents ne veulent pas toujours parler à la médecine du travail, qui est perçue comme… enfin, comme interne.\n\nDr Kerbrat : Je ne le prends pas mal. [rires] Mais je rappelle qu'on a déjà une psychologue du travail, à mi-temps.\n\nM. Rouvière : À mi-temps pour deux mille huit cents agents.\n\nM. Castagnet : La cellule d'écoute externe, ça a un coût, ça passe par un marché. Je ne suis pas contre l'idée, mais je ne peux pas la décider aujourd'hui. Madame Arnaud, vous pouvez faire chiffrer ?\n\nMme Arnaud : On peut regarder ce que ça coûterait, oui, je le fais dans le cadre de la préparation budgétaire 2027.\n\nM. Rouvière : Donc ce n'est pas acté.\n\nM. Castagnet : Ce n'est pas acté, c'est étudié. Je ne vais pas vous mentir.\n\nMme Thibaud : Une question pour le docteur Kerbrat. Est-ce que les résultats par direction, en détail, peuvent être communiqués ? On n'a que la synthèse globale.\n\nDr Kerbrat : Oui, je peux présenter les résultats détaillés par direction, en respectant le seuil d'anonymat — on ne descend pas en dessous de dix répondants. Je propose de le faire à la formation spécialisée du 19 novembre.\n\nM. Castagnet : Parfait. [M. Benslimane se lève] Monsieur Benslimane nous quitte.\n\nM. Benslimane : Excusez-moi, bonne fin de séance.\n\n[Départ de M. Benslimane à 11 h 42]\n\nM. Castagnet : Le collège employeur compte donc quatre membres pour la suite. D'autres questions sur le point 3 ? Monsieur Pallas.\n\nM. Pallas : Juste pour revenir au point 1, parce que je n'ai pas eu de réponse. Le dépôt de sel de Lauzières, si le diagnostic est mauvais, il se passe quoi pour l'hiver 2027-2028 ? On sale tout le nord depuis Montclar ?\n\nM. Castagnet : Monsieur Pallas, on a voté sur le point 1. Monsieur Galmiche est parti.\n\nM. Pallas : Je sais, mais c'est une vraie question.\n\nM. Castagnet : C'est une vraie question. Monsieur Oudin, vous la transmettez à monsieur Galmiche, et il répondra par écrit aux organisations syndicales.\n\nM. Oudin : Je la lui transmets aujourd'hui.\n\nM. Castagnet : Bien. Sur le point 3, je rappelle encore une fois qu'il n'y a pas de vote : c'est une information, le plan reviendra pour avis après le travail en formation spécialisée. Point 4, le plan de formation 2027. Madame Arnaud.\n\nMme Arnaud : Je serai rapide puisque les documents sont détaillés. Le plan de formation 2027 reprend les orientations du plan pluriannuel. Les priorités : la prévention des risques, notamment ce qu'on vient d'évoquer sur les agressions et sur les RPS pour les encadrants ; la transition numérique, avec l'accompagnement au nouveau logiciel de gestion des aides sociales ; et la préparation aux concours et examens professionnels. Le budget prévisionnel est de 640 000 euros, en dehors de la cotisation au CNFPT. On a aussi intégré, à la demande de la CFDT l'an dernier, des formations aux premiers secours en santé mentale.\n\nMme Thibaud : On s'en félicite.\n\nM. Vasseur : Pour FO, on voudrait que les agents des routes aient accès aux formations en semaine, pas le samedi.\n\nMme Arnaud : C'est le cas, il n'y a pas de formation le samedi.\n\nM. Vasseur : Il y en a eu une en mars.\n\nMme Arnaud : C'était une exception, liée à la disponibilité du formateur. On fera attention.\n\nM. Pallas : Et les formations CACES, pour les engins ? Il y a des agents qui attendent depuis deux ans.\n\nMme Arnaud : Elles sont dans le plan, page neuf, avec quarante-deux places en 2027 contre vingt-huit cette année.\n\nM. Pallas : Bon. C'est mieux.\n\nM. Castagnet : On vote ? Avis sur le plan de formation 2027. Collège du personnel ?\n\nM. Oudin : Huit pour, unanimité.\n\nM. Castagnet : Collège employeur ?\n\nM. Oudin : Quatre pour, unanimité des présents.\n\nM. Castagnet : Avis favorable unanime des deux collèges. Madame Arnaud, vous le transmettrez à la délégation régionale du CNFPT ?\n\nMme Arnaud : Oui, avant le 31 décembre, comme chaque année.\n\nM. Castagnet : Point 5, les questions diverses. J'ai reçu deux questions écrites. La première, de la CGT, sur le chauffage du bâtiment B, rue des Tanneurs.\n\nMme Sissoko : Oui. Les agents du bâtiment B, c'est la direction de l'autonomie, ils ont eu dix-sept degrés la semaine dernière, alors qu'il ne fait pas encore froid. Qu'est-ce que ce sera en janvier ? La chaudière est en panne une semaine sur deux.\n\nM. Oudin : On a eu le signalement. Le service des bâtiments doit intervenir pour remplacer le brûleur. Je m'engage à ce que l'intervention ait lieu avant le vendredi 16 octobre, et je vous en confirmerai la date par mail.\n\nMme Sissoko : On a déjà entendu ça au printemps.\n\nM. Oudin : Cette fois, la pièce est commandée.\n\nM. Castagnet : Deuxième question, de l'UNSA, sur le stationnement à l'Hôtel du Département.\n\nM. Lhermite : Oui. Depuis la fermeture du parking de la rue Carnot pour travaux, les agents qui arrivent après huit heures trente ne trouvent plus de place. Les agents à temps partiel, ceux qui déposent les enfants, ceux qui sont en horaires décalés. On demande des places réservées ou une convention avec le parking public.\n\nM. Castagnet : Une convention avec le parking des Halles, on y a pensé. Ça a un coût aussi. Madame Arnaud ?\n\nMme Arnaud : Je peux demander un devis au gestionnaire du parking.\n\nM. Castagnet : Faites, oui. Mais je ne prends pas d'engagement sur la convention elle-même.\n\nM. Lhermite : Dans quel délai, le devis ?\n\nMme Arnaud : Je n'ai pas la main sur leurs délais. Dès qu'on l'a, on le partage.\n\nMme Escande : J'ai une question orale, si vous permettez, qui n'était pas dans les questions écrites. Le compte épargne-temps. Les agents qui ont atteint le plafond de soixante jours perdent des jours, notamment aux routes, à cause des astreintes. On demande une ouverture de la monétisation.\n\nM. Castagnet : Ce n'est pas à l'ordre du jour, madame Escande, et c'est un sujet qui demande une délibération. Je ne peux pas en débattre sans document. Monsieur Oudin, vous l'inscrivez à l'ordre du jour du prochain CST, avec une note ?\n\nM. Oudin : Je l'inscris pour le 10 décembre, avec une note sur les soldes de CET par direction.\n\nMme Escande : Merci.\n\nM. Rouvière : Et sur la déclaration liminaire, monsieur le président ? Sur l'étude d'impact systématique avant chaque réorganisation ?\n\nM. Castagnet : Je vous ai entendu. C'est une demande légitime. Mais je ne vais pas créer une procédure en fin de séance. On en reparle avec la DRH dans le cadre de l'agenda social.\n\nM. Rouvière : On le notera au PV, alors, que ce n'est pas acté.\n\nM. Castagnet : Notez-le.\n\nMme Ferrand : Si je peux me permettre un mot, monsieur le président. Je voulais remercier les agents des MDS, au nom des élus, parce qu'on parle beaucoup de chiffres mais ce qu'ils vivent au quotidien est difficile.\n\nM. Castagnet : Merci madame Ferrand. Je m'associe à vos propos. Alors, avant de clore, je vous rappelle la date du prochain CST. Je vous avais indiqué le 3 décembre dans la convocation…\n\nM. Oudin : Le 10, monsieur le président. Le 3, c'était la date initiale, elle a été changée à cause de la session du conseil départemental.\n\nM. Castagnet : Le jeudi 10 décembre, pardon, à neuf heures trente. Merci monsieur Oudin. Et la formation spécialisée se réunit le jeudi 19 novembre. Plus de questions ? Je vous remercie. La séance est levée.\n\n[Fin de l'enregistrement : 12 h 21]"
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "M. Castagnet (vice-président chargé des ressources humaines, président du CST)",
    "Collège de la collectivité : Mme Ferrand (conseillère départementale), M. Benslimane (conseiller départemental, parti à 11 h 42, avant le vote sur le plan de formation), Mme Arnaud (DGA ressources), M. Oudin (DRH, secrétaire de séance)",
    "Excusée : Mme Jourdan (conseillère départementale), non remplacée",
    "Collège du personnel, CGT : M. Rouvière (secrétaire adjoint), Mme Sissoko, M. Pallas",
    "Collège du personnel, FO : Mme Escande, M. Vasseur",
    "Collège du personnel, CFDT : Mme Thibaud ; Mme Moulin (suppléante, siège avec voix délibérative en remplacement de M. Courtade, excusé)",
    "Collège du personnel, UNSA : M. Lhermite",
    "Experts : M. Galmiche (directeur des routes et des mobilités, point 1 seulement, parti à 10 h 49) ; Dr Kerbrat (médecin du travail) et Mme Maréchal (conseillère de prévention), à partir du point 3"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Procès-verbal de la séance du 2 juillet 2026 approuvé à l'unanimité des deux collèges, avec la correction demandée par FO sur les astreintes (approbation de la revalorisation des indemnités, opposition à leur extension aux agents de catégorie C du service des bâtiments)"
    },
    {
      "ref": "D2",
      "texte": "Projet de fusion des centres d'exploitation de Lauzières et de Montclar-d'Orbe modifié en séance : mise en œuvre reportée au 1er mars 2027 au lieu du 1er janvier 2027"
    },
    {
      "ref": "D3",
      "texte": "Avis sur la fusion du centre d'exploitation de Lauzières avec celui de Montclar-d'Orbe (regroupement des 14 agents à Montclar-d'Orbe, sans suppression de poste, mise en œuvre au 1er mars 2027, maintien du dépôt de sel de Lauzières sous réserve d'un diagnostic) : avis défavorable du collège du personnel (5 contre CGT et FO, 2 abstentions CFDT, 1 pour UNSA) et avis favorable du collège employeur (5 pour) ; avis défavorable non unanime, donc pas de nouvelle consultation ; la décision appartient au président du conseil départemental"
    },
    {
      "ref": "D4",
      "texte": "Amendement de la CFDT accepté : délai de prévenance de 48 heures, sauf urgence, pour l'annulation d'un jour de télétravail par le responsable (au lieu des 24 heures du projet)"
    },
    {
      "ref": "D5",
      "texte": "Avis favorable des deux collèges sur la modification de la charte du télétravail (2 jours fixes maximum par semaine, forfait annuel de 20 jours flottants, plafond de 3 jours télétravaillés par semaine, délai de prévenance de 48 heures sauf urgence, entrée en vigueur au 1er janvier 2027) : collège du personnel 5 pour et 3 abstentions (CGT), collège employeur 5 pour"
    },
    {
      "ref": "D6",
      "texte": "Visite d'une délégation de la formation spécialisée à la MDS de Saint-Fréjus le mardi 20 octobre 2026 au matin (M. Rouvière, Mme Escande, Mme Ferrand, accompagnés de Mme Maréchal)"
    },
    {
      "ref": "D7",
      "texte": "Avis favorable unanime des deux collèges sur le plan de formation 2027 (budget prévisionnel de 640 000 € hors cotisation CNFPT) : collège du personnel 8 pour, collège employeur 4 pour"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Mettre en ligne sur l'intranet le procès-verbal corrigé de la séance du 2 juillet 2026",
      "responsable": "M. Oudin",
      "echeance": "d'ici fin octobre 2026"
    },
    {
      "ref": "A2",
      "action": "Transmettre aux représentants du personnel l'étude anonymisée des temps de trajet des agents de Lauzières",
      "responsable": "M. Galmiche",
      "echeance": "avant le CST du jeudi 10 décembre 2026"
    },
    {
      "ref": "A3",
      "action": "Mener les entretiens individuels avec les 14 agents de Lauzières",
      "responsable": "DRH (M. Oudin) et M. Galmiche",
      "echeance": "avant le 30 novembre 2026"
    },
    {
      "ref": "A4",
      "action": "Transmettre à M. Galmiche la question sur le salage du nord si le diagnostic du hangar à sel est défavorable, pour une réponse écrite aux organisations syndicales",
      "responsable": "M. Oudin (transmission) ; M. Galmiche (réponse écrite)",
      "echeance": "transmission le jour même (1er octobre 2026) ; réponse non fixée"
    },
    {
      "ref": "A5",
      "action": "Publier la charte du télétravail modifiée sur l'intranet avec une note de service",
      "responsable": "M. Oudin",
      "echeance": "avant le 1er décembre 2026"
    },
    {
      "ref": "A6",
      "action": "Présenter un bilan de la charte du télétravail après un an d'application",
      "responsable": "M. Oudin",
      "echeance": "CST de début 2028"
    },
    {
      "ref": "A7",
      "action": "Organiser la visite de la délégation de la formation spécialisée à la MDS de Saint-Fréjus",
      "responsable": "Mme Maréchal",
      "echeance": "mardi 20 octobre 2026 (matin)"
    },
    {
      "ref": "A8",
      "action": "Présenter le compte rendu de la visite de la MDS de Saint-Fréjus en formation spécialisée",
      "responsable": "non précisé",
      "echeance": "formation spécialisée du jeudi 19 novembre 2026"
    },
    {
      "ref": "A9",
      "action": "Présenter les résultats détaillés du baromètre social par direction (seuil d'anonymat de 10 répondants)",
      "responsable": "Dr Kerbrat",
      "echeance": "formation spécialisée du jeudi 19 novembre 2026"
    },
    {
      "ref": "A10",
      "action": "Mettre à jour le document unique d'évaluation des risques professionnels (DUERP)",
      "responsable": "Mme Maréchal",
      "echeance": "avant le 31 mars 2027"
    },
    {
      "ref": "A11",
      "action": "Chiffrer le coût d'une cellule d'écoute psychologique externe",
      "responsable": "Mme Arnaud",
      "echeance": "préparation budgétaire 2027"
    },
    {
      "ref": "A12",
      "action": "Transmettre le plan de formation 2027 à la délégation régionale du CNFPT",
      "responsable": "Mme Arnaud",
      "echeance": "avant le 31 décembre 2026"
    },
    {
      "ref": "A13",
      "action": "Faire remplacer le brûleur de la chaudière du bâtiment B (rue des Tanneurs) par le service des bâtiments et confirmer la date d'intervention par mail",
      "responsable": "M. Oudin",
      "echeance": "avant le vendredi 16 octobre 2026"
    },
    {
      "ref": "A14",
      "action": "Demander un devis au gestionnaire du parking des Halles",
      "responsable": "Mme Arnaud",
      "echeance": "non fixée"
    },
    {
      "ref": "A15",
      "action": "Inscrire le compte épargne-temps à l'ordre du jour du prochain CST, avec une note sur les soldes par direction",
      "responsable": "M. Oudin",
      "echeance": "CST du jeudi 10 décembre 2026"
    }
  ],
  "pieges": [
    "La fusion des centres de Lauzières et de Montclar-d'Orbe n'est PAS décidée par le CST : il rend un avis (défavorable du collège du personnel, favorable du collège employeur), la décision appartient au président du conseil départemental",
    "La mise en œuvre de la fusion est fixée au 1er mars 2027 et non au 1er janvier 2027 (date initiale du projet, modifiée en séance)",
    "Maintien du dépôt de sel de Lauzières : conditionné au diagnostic du hangar à sel, dont la date n'est pas connue",
    "Prime de restructuration pour l'ensemble des 14 agents : demandée par FO, NON décidée (examen au cas par cas, dans le cadre réglementaire)",
    "Trois jours fixes de télétravail : demandés par la CGT, NON retenus",
    "Délai de prévenance de 24 heures (projet initial) : remplacé par 48 heures sauf urgence",
    "Nombre d'agents en télétravail : 1 240 (et non 1 420, chiffre annoncé par erreur puis corrigé)",
    "Prise en charge d'une partie de l'abonnement internet : demandée par la CGT, NON retenue",
    "Télétravail des agents administratifs des collèges : évoqué, aucune décision, ni responsable ni date",
    "Cellule d'écoute psychologique externe : proposée par la CGT, NON décidée (seulement chiffrée dans la préparation budgétaire 2027)",
    "Plan de prévention des RPS (dont formation à la gestion de l'agressivité dès novembre) : présenté pour information, aucun avis ni vote ; il reviendra pour avis après travail en formation spécialisée",
    "Agent de sécurité à la MDS de Saint-Fréjus les mardis et jeudis : déjà en place depuis le 14 septembre, ce n'est pas une décision de la séance ; son extension n'est pas décidée",
    "Convention avec le parking des Halles : NON décidée, seul un devis est demandé",
    "Étude d'impact systématique avant chaque réorganisation (déclaration liminaire CGT-FO) : renvoyée à l'agenda social, NON actée",
    "Monétisation du compte épargne-temps : non débattue, seulement inscrite au prochain CST",
    "M. Benslimane est parti à 11 h 42 : le collège employeur ne compte que 4 votants pour le plan de formation",
    "M. Courtade excusé, remplacé par sa suppléante Mme Moulin ; Mme Jourdan excusée, non remplacée",
    "Le diagnostic amiante a été présenté en formation spécialisée le 12 mai et non en mars",
    "Le prochain CST a lieu le jeudi 10 décembre 2026 et non le 3 décembre (date initiale de la convocation)"
  ]
}
```

### Sortie (statut ok)

```text
**Compte rendu de la réunion du comité social territorial**

**Participants :**
- M. Castagnet : Président du comité
- M. Oudin : Président du service social

**Points abordés :**
1. Indemnité forfaitaire de télétravail
2. Plan de prévention des violences externes
3. Module de formation à la prévention des RPS pour les managers
4. Plan de formation 2027
5. Questions diverses

**Décisions et avis rendus :**
1. **Indemnité forfaitaire de télétravail :**
   - L'indemnité forfaitaire de télétravail reste inchangée, elle est versée au taux réglementaire.
   - Le délai de prévenance pour annulation par le responsable est de quarante-huit heures, sauf urgence.
   - Les agents sont satisfaites de la situation.

2. **Plan de prévention des violences externes :**
   - Le plan de prévention des violences externes, comprenant une formation à la gestion des situations d'agressivité pour 100 agents, a été validé et commencera en novembre 2022.
   - La charge de travail sera pilotée par chaque direction, avec un travail par direction sur les priorités.

3. **Module de formation à la prévention des RPS pour les managers :**
   - Un module de formation à la prévention des RPS pour les managers a été mis en place, et le document unique d'évaluation des risques professionnels (DUERP) a été mis à jour pour intégrer ces informations.

4. **Plan de formation 2027 :**
   - Le plan de formation 2027 a été approuvé par les collèges employeur et représentant, avec un budget prévisionnel de 640 000 euros.

5. **Questions diverses :**
   - **Chauffage du bâtiment B :** Questions diverses traitant du chauffage du bâtiment B.
   - **Stationnement à l'Hôtel du Département :** Questions diverses traitant du stationnement à l'Hôtel du Département.
   - **Ouverture de la monétisation pour les agents qui ont atteint le plafond de soixante jours :** Questions diverses traitant de l'ouverture de la monétisation pour les agents qui ont atteint le plafond de soixante jours.

**Actions à mener :**
- **Responsable :** M. Castagnet
- **Échéance :** À déterminer en fonction des décisions prises lors de la réunion

**Note :** Les points traités dans les parties sont intégrés dans le compte rendu unique. Les décisions et actions à mener sont basées sur les points abordés lors de la réunion.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0 — L'approbation du procès-verbal du 2 juillet et sa correction sur les astreintes ne sont pas mentionnées.
  - D2 : 0 — Le report de la fusion au 1er mars 2027 est absent, comme tout le point 1.
  - D3 : 0 — L'avis sur la fusion Lauzières/Montclar-d'Orbe est absent du compte rendu.
  - D4 : 1 — Le compte rendu indique : « Le délai de prévenance pour annulation par le responsable est de quarante-huit heures, sauf urgence ».
  - D5 : 0 — L'avis favorable des deux collèges sur la charte du télétravail n'est pas rapporté, ni ses principales modalités (jours fixes, jours flottants, plafond, entrée en vigueur) ni le décompte des votes.
  - D6 : 0 — La visite de la délégation de la formation spécialisée à la MDS de Saint-Fréjus le 20 octobre n'est pas mentionnée.
  - D7 : 1 — Le compte rendu indique : « Le plan de formation 2027 a été approuvé par les collèges employeur et représentant, avec un budget prévisionnel de 640 000 euros ».
  - A1 : 0 — La mise en ligne du PV corrigé est absente.
  - A2 : 0 — La transmission de l'étude anonymisée des temps de trajet est absente.
  - A3 : 0 — Les entretiens individuels avec les 14 agents sont absents.
  - A4 : 0 — La transmission de la question sur le salage à M. Galmiche est absente.
  - A5 : 0 — La publication de la charte modifiée avant le 1er décembre est absente.
  - A6 : 0 — Le bilan de la charte au CST de début 2028 est absent.
  - A7 : 0 — L'organisation de la visite par Mme Maréchal est absente.
  - A8 : 0 — La présentation du compte rendu de visite le 19 novembre est absente.
  - A9 : 0 — La présentation des résultats détaillés du baromètre par direction est absente.
  - A10 : 0 — La mise à jour du DUERP est présentée comme déjà réalisée (« a été mis à jour »), sans responsable ni échéance au 31 mars 2027.
  - A11 : 0 — Le chiffrage de la cellule d'écoute psychologique externe est absent.
  - A12 : 0 — La transmission du plan de formation au CNFPT est absente.
  - A13 : 0 — Le chauffage n'est cité que comme thème (« Questions diverses traitant du chauffage »), sans l'action, son responsable ni son échéance.
  - A14 : 0 — Le stationnement n'est cité que comme thème ; la demande de devis par Mme Arnaud est absente.
  - A15 : 0 — L'inscription du compte épargne-temps à l'ordre du jour du CST du 10 décembre est absente.
- `absence_invention` : 0 — Le compte rendu présente comme décidé un élément des pièges, le plan de prévention « a été validé et commencera en novembre 2022 », alors qu'il n'a été présenté que pour information ; il contient aussi d'autres éléments absents des notes (« 100 agents », « Les agents sont satisfaites », « M. Oudin : Président du service social »).
- `structure` : 1 — Les quatre sections attendues (Participants, Points abordés, Décisions, Actions) sont présentes, même si leur contenu est très lacunaire.
- Inventions : M. Oudin qualifié de « Président du service social » (il est directeur des ressources humaines); « Les agents sont satisfaites de la situation »; Plan de prévention des violences externes « a été validé » (présenté pour information, sans vote); Formation à la gestion de l'agressivité pour « 100 agents » (environ 110 dans les notes); Début de la formation en « novembre 2022 »; Module de formation RPS pour les managers « a été mis en place »; DUERP « a été mis à jour » (mise à jour prévue avant le 31 mars 2027); Action générique attribuée à M. Castagnet avec une échéance « à déterminer »
- Confiance : haute

## CR-007 (CR, facile)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de cette réunion d'équipe : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 472,
  "notes": "Réunion d'équipe – médiathèque intercommunale La Filature (CC du Haut-Lisset) – mardi 15/09/2026, 9h-10h45, salle d'animation (avant ouverture au public)\nPrésents : C. Aubertin (directrice, anime), T. Fabre (resp. jeunesse), M. N'Diaye (resp. adultes + numérique), J. Leroux (accueil/prêt), S. Combes (réseau des bibliothèques relais), Lucas P. (volontaire service civique, présent jusqu'à 10h, part ensuite pour l'atelier numérique à l'EHPAD)\nExcusée : A. Gerbier (en congés)\nNotes : N'Diaye\n\n1. Bilan de l'été\n- Fréquentation juillet-août : 6 850 entrées, Aubertin dit d'abord « +12 % » puis corrige : +8 % par rapport à 2025 (le +12 % c'était les prêts, pas les entrées).\n- Partir en livre : 9 lectures en plein air, bonne participation sauf au plan d'eau (pluie x2).\n- Leroux : l'automate de prêt n°2 plante encore plusieurs fois par jour → il rappelle le prestataire, avant vendredi 18/09.\n\n2. Horaires / dimanche matin\n- Fabre propose d'ouvrir le dimanche matin (10h-13h) au moins l'hiver, demande des familles.\n- Leroux contre tant qu'on n'a pas de renfort : « on est déjà à flux tendu le samedi ».\n- Aubertin : c'est une décision des élus (vice-pdte culture + bureau communautaire), pas de l'équipe. Pas de note préparée pour l'instant.\n→ rien de décidé, on en reparle quand Gerbier sera rentrée. Pas de date.\n\n3. Navette documentaire (bibliothèques relais)\n- Le transporteur ne peut plus passer le mercredi.\n- DÉCISION : la navette passe du mercredi au jeudi à partir du jeudi 1er octobre 2026.\n- Combes prévient les 7 bibliothèques relais du changement de jour, avant le vendredi 25/09.\n\n4. Désherbage / vente de livres\n- ~1 200 documents désherbés depuis le printemps (romans abîmés, docs périmés).\n- Idée d'une vente le samedi 17 octobre 2026 à 1 € le livre / 0,50 € la revue, recettes pour l'achat de jeux.\n- Aubertin rappelle : il faut d'abord une délibération du conseil communautaire (sortie d'inventaire + tarifs). Le point passe au conseil communautaire du mardi 29 septembre.\n→ la vente du 17/10 n'a lieu QUE si la délibération est votée le 29/09. Sinon reporté.\n- Aubertin finalise le projet de délibération et l'envoie au secrétariat général, avant vendredi 18/09.\n- N'Diaye propose de donner le reste à une asso (Emmaüs ?). Pas tranché.\n\n5. Accueil des classes\n- Trop de demandes le lundi, on n'a qu'une personne.\n- DÉCISION : à partir de la rentrée de la Toussaint, accueil des classes uniquement le mardi et le jeudi matin (plus le lundi).\n- Fabre envoie le nouveau planning aux écoles du territoire, avant les vacances de la Toussaint.\n\n6. Mois du film documentaire (novembre)\n- DÉCISION : on participe, 2 projections-débats, vendredi 13 novembre et vendredi 27 novembre 2026 à 20h (Aubertin avait écrit le 20 dans l'ordre du jour → c'est bien le 27, le 20 la salle est prise).\n- N'Diaye réserve les films auprès de la médiathèque départementale, avant le vendredi 9 octobre.\n- Lucas aimerait animer un débat → à voir, pas décidé.\n\nDivers\n- N'Diaye : abonnement à une plateforme de presse en ligne ? Pas de budget 2026, éventuellement BP 2027. Rien décidé.\n- Prochaine réunion d'équipe : mardi 13 octobre, 9h."
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "C. Aubertin (directrice, anime la réunion)",
    "T. Fabre (responsable jeunesse)",
    "M. N'Diaye (responsable adultes et numérique, prise de notes)",
    "J. Leroux (accueil et prêt)",
    "S. Combes (réseau des bibliothèques relais)",
    "Lucas P. (volontaire en service civique, présent jusqu'à 10 h)",
    "Excusée : A. Gerbier (congés)"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "La navette documentaire vers les bibliothèques relais passe du mercredi au jeudi à partir du jeudi 1er octobre 2026"
    },
    {
      "ref": "D2",
      "texte": "À partir de la rentrée de la Toussaint, l'accueil des classes a lieu uniquement le mardi et le jeudi matin (et non plus le lundi)"
    },
    {
      "ref": "D3",
      "texte": "Participation au Mois du film documentaire avec 2 projections-débats, le vendredi 13 novembre et le vendredi 27 novembre 2026 à 20 h"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Rappeler le prestataire au sujet des pannes de l'automate de prêt n° 2",
      "responsable": "J. Leroux",
      "echeance": "avant le vendredi 18 septembre 2026"
    },
    {
      "ref": "A2",
      "action": "Prévenir les 7 bibliothèques relais du changement de jour de la navette",
      "responsable": "S. Combes",
      "echeance": "avant le vendredi 25 septembre 2026"
    },
    {
      "ref": "A3",
      "action": "Finaliser le projet de délibération (sortie d'inventaire et tarifs de la vente) et l'envoyer au secrétariat général",
      "responsable": "C. Aubertin",
      "echeance": "avant le vendredi 18 septembre 2026 (conseil communautaire du mardi 29 septembre 2026)"
    },
    {
      "ref": "A4",
      "action": "Envoyer le nouveau planning d'accueil des classes aux écoles du territoire",
      "responsable": "T. Fabre",
      "echeance": "avant les vacances de la Toussaint"
    },
    {
      "ref": "A5",
      "action": "Réserver les films du Mois du documentaire auprès de la médiathèque départementale",
      "responsable": "M. N'Diaye",
      "echeance": "avant le vendredi 9 octobre 2026"
    }
  ],
  "pieges": [
    "Ouverture le dimanche matin (10 h-13 h) : proposée, NON décidée ; elle relève des élus, aucune date pour en reparler",
    "Vente de livres désherbés le samedi 17 octobre 2026 : conditionnée au vote de la délibération par le conseil communautaire du 29 septembre, NON acquise",
    "Fréquentation de l'été : +8 % d'entrées (le +12 % annoncé d'abord concerne les prêts)",
    "La 2e projection a lieu le vendredi 27 novembre et non le 20 novembre (erreur de l'ordre du jour)",
    "Don des livres restants à une association : proposé, NON tranché",
    "Animation d'un débat par Lucas : à voir, NON décidée",
    "Abonnement à une plateforme de presse en ligne : pas de budget en 2026, rien décidé",
    "Lucas P. n'est présent que jusqu'à 10 h"
  ]
}
```

### Sortie (statut ok)

```text
**Réunion d'équipe - médiathèque intercommunale La Filature (CC du Haut-Lisset)**

**Participants :**
- C. Aubertin (directrice)
- T. Fabre (responsable des jeunes)
- M. N'Diaye (responsable des adultes et numérique)
- J. Leroux (responsable de l'accueil et du prêt)
- S. Combes (responsable du réseau des bibliothèques relais)
- Lucas P. (volontaire du service civique, présent jusqu'à 10h, part ensuite pour l'atelier numérique à l'EHPAD)

**Excusée :** A. Gerbier (en congés)

**Points abordés :**

1. Bilan de l'été
   - Fréquentation juillet-août : 6 850 entrées, augmentation de 8 % par rapport à 2025 (par rapport aux prêts, pas aux entrées).
   - Livraison de livres : 9 lectures en plein air, bonne participation, sauf au plan d'eau (pluie deux fois).
   - Leroux : l'automate de prêt n°2 plante plusieurs fois par jour, rappel du prestataire avant vendredi 18/09.

2. Horaires / dimanche matin
   - Fabre propose d'ouvrir le dimanche matin (10h-13h) au moins l'hiver, demande des familles.
   - Leroux contre, tant qu'on n'a pas de renfort : "on est déjà à flux tendu le samedi".
   - Aubertin : c'est une décision des élus (vice-président de la culture + bureau communautaire), pas de décision de l'équipe. Pas de note préparée pour l'instant.
   - Rien de décidé, on en reparle quand Gerbier sera rentrée. Pas de date.

3. Navette documentaire (bibliothèques relais)
   - Le transporteur ne peut plus passer le mercredi.
   - DÉCISION : la navette passe du mercredi au jeudi à partir du 1er octobre 2026.
   - Combes prévint les 7 bibliothèques relais du changement de jour, avant le vendredi 25/09.

4. Désherbage / vente de livres
   - ~1 200 documents désherbés depuis le printemps (romans abîmés, documents périmés).
   - Idée d'une vente le samedi 17 octobre 2026 à 1 € le livre / 0,50 € la revue, recettes pour l'achat de jeux.
   - Aubertin rappelle : il faut d'abord une délibération du conseil communautaire (sortie d'inventaire + tarifs). Le point passe au conseil communautaire du mardi 29 septembre.
   - Aubertin finalise le projet de délibération et l'envoie au secrétariat général, avant vendredi 18/09.
   - N'Diaye propose de donner le reste à une association (Emmaüs ?). Pas tranché.

5. Accueil des classes
   - Trop de demandes le lundi, on n'a qu'une personne.
   - DÉCISION : à partir de la rentrée de la Toussaint, accueil des classes uniquement le mardi et le jeudi matin (plus le lundi).
   - Fabre envoie le nouveau planning aux écoles du territoire, avant les vacances de la Toussaint.

6. Mois du film documentaire (novembre)
   - DÉCISION : on participe, 2 projections-débats, vendredi 13 novembre et vendredi 27 novembre 2026 à 20h (Aubertin avait écrit le 20 dans l'ordre du jour → c'est bien le 27, le 20 la salle est prise).
   - N'Diaye réserve les films auprès de la médiathèque départementale, avant le vendredi 9 octobre.
   - Lucas aimerait animer un débat → à voir, pas décidé.

**Divers**
- N'Diaye : abonnement à une plateforme de presse en ligne ? Pas de budget 2026, éventuellement BP 2027. Rien décidé.

**Prochaine réunion d'équipe :** mardi 13 octobre, 9h.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Le point 3 indique : « DÉCISION : la navette passe du mercredi au jeudi à partir du 1er octobre 2026 ».
  - D2 : 1 — Le point 5 indique : « accueil des classes uniquement le mardi et le jeudi matin (plus le lundi) » à partir de la rentrée de la Toussaint.
  - D3 : 1 — Le point 6 mentionne 2 projections-débats, le vendredi 13 et le vendredi 27 novembre 2026 à 20h, avec la correction du 20.
  - A1 : 1 — Le point 1 indique : « Leroux : … rappel du prestataire avant vendredi 18/09 », avec le responsable et l'échéance.
  - A2 : 1 — Le point 3 indique : « Combes prévint les 7 bibliothèques relais … avant le vendredi 25/09 », avec le responsable et l'échéance.
  - A3 : 1 — Le point 4 indique : « Aubertin finalise le projet de délibération et l'envoie au secrétariat général, avant vendredi 18/09 ».
  - A4 : 1 — Le point 5 indique : « Fabre envoie le nouveau planning aux écoles du territoire, avant les vacances de la Toussaint ».
  - A5 : 1 — Le point 6 indique : « N'Diaye réserve les films auprès de la médiathèque départementale, avant le vendredi 9 octobre ».
- `absence_invention` : 0 — La sortie déforme un chiffre visé par un piège : « augmentation de 8 % par rapport à 2025 (par rapport aux prêts, pas aux entrées) » contredit les notes, où les +8 % portent sur les entrées et les +12 % sur les prêts ; « Livraison de livres » remplace en outre à tort « Partir en livre ».
- `structure` : 0 — Les sections Participants et Points abordés sont présentes, mais il n'existe aucune section distincte « Décisions » ni « Actions » : décisions et actions restent dispersées dans les points abordés.
- Inventions : « augmentation de 8 % par rapport à 2025 (par rapport aux prêts, pas aux entrées) » : attribution inversée, les notes rattachent les +8 % aux entrées; « Livraison de livres » au lieu de l'opération « Partir en livre »
- Confiance : moyenne

## CR-021 (CR, difficile)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de cette séance du conseil d'administration : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 4739,
  "transcription": "Transcription — Conseil d'administration du collège Les Hautes-Bruyères, Saint-Aubin-sur-Lézon\nMardi 6 octobre 2026, 17 h 30, salle polyvalente\nEnregistrement réalisé pour faciliter la rédaction du procès-verbal. Secrétaire de séance : Mme Roussel.\n\nMme Cordier (principale, présidente) : Bon, il est 17 h 35, je crois qu'on peut commencer. Bonsoir à toutes et à tous. Je vous remercie d'être là, c'est le dernier conseil d'administration de cette mandature, puisque les élections des représentants des parents ont lieu ce vendredi 9 octobre et celles des personnels dans la foulée. Je fais l'appel, comme d'habitude, pour vérifier le quorum. Pour l'administration : moi-même, M. Vauquelin, principal adjoint, Mme Ferhat, adjointe gestionnaire, M. Tessier, CPE. Pour les collectivités : Mme Arnaud-Poitevin, conseillère départementale, qui est là, merci madame. M. Moutier, l'autre représentant du département, est excusé. M. Lebrun, adjoint au maire chargé des affaires scolaires, présent. La communauté de communes du Val de Lézon n'est pas représentée, on n'a pas eu de nouvelles.\n\nM. Lebrun : Comme d'habitude, hein.\n\nMme Cordier : Je ne commente pas. [rires] Pour les personnels enseignants : Mme Roussel, Mme Kasprzak, M. N'Diaye, Mme Bellamy. M. Guérin est absent, il est remplacé par sa suppléante, Mme Varenne. M. Marchetti m'a prévenue qu'il serait en retard, il a un match UNSS qui finit à 17 h 30. Pour les personnels administratifs, techniques, sociaux et de santé : Mme Picot, M. Benslimane. Pour les parents : Mme Chaumont, M. Ostrowski, Mme Sy, M. Pellerin, Mme Delorme. M. Baudoin est excusé. Et pour les élèves : Léna, en troisième, et Yanis, en quatrième. Bienvenue à vous deux.\n\nMme Chaumont : Madame la principale, juste une précision, M. Baudoin m'a donné un pouvoir, il m'a envoyé un mail cet après-midi.\n\nMme Cordier : Alors non, je suis désolée, le vote par procuration n'existe pas au conseil d'administration. Un membre titulaire absent est remplacé par son suppléant, c'est tout. Et la suppléante de M. Baudoin ne pouvait pas venir ce soir, elle me l'a écrit. Donc on ne peut pas tenir compte du pouvoir.\n\nMme Chaumont : D'accord, je ne savais pas. Je lui dirai.\n\nMme Cordier : Donc nous sommes vingt membres présents sur vingt-quatre, le quorum est de treize, il est largement atteint. Nous avons aussi ce soir, sans voix délibérative, Mme Saintonge, professeure d'espagnol, qui vient pour présenter le voyage en Andalousie au point 3, et M. Lacombe, l'agent comptable, nous rejoindra pour le point budget, il est au conseil d'administration du lycée juste avant. Mme Roussel a accepté d'être secrétaire de séance, merci à elle. L'ordre du jour vous a été envoyé le 22 septembre. Il y a six points : l'approbation du procès-verbal du 30 juin, le règlement intérieur, les voyages et sorties, la rentrée et la dotation horaire, le budget, et les questions diverses. Est-ce que quelqu'un demande l'ajout d'un point ?\n\n[silence]\n\nMme Cordier : Non. Alors on y va.\n\nPoint 1 — Approbation du procès-verbal du conseil d'administration du 30 juin 2026\n\nMme Cordier : Vous avez reçu le procès-verbal du 30 juin. Est-ce qu'il y a des remarques ?\n\nMme Delorme : Oui, page 3, il est écrit que le foyer socio-éducatif a reçu une subvention de 1 500 euros. Or, si je me souviens bien, c'était 1 800. On en avait parlé parce que c'était plus que l'année d'avant.\n\nMme Ferhat : Oui, Mme Delorme a raison, c'est 1 800 euros. C'est une erreur de frappe dans le PV, le montant voté était bien de 1 800.\n\nMme Cordier : Très bien, on corrige : 1 800 euros et non 1 500. Le procès-verbal corrigé sera mis en ligne sur l'ENT. D'autres remarques ? Non. Je mets aux voix le procès-verbal ainsi corrigé. Qui est contre ? Qui s'abstient ? Il est adopté à l'unanimité des vingt présents. Merci.\n\n[M. Marchetti entre dans la salle, 17 h 50]\n\nM. Marchetti : Pardon, pardon, désolé pour le retard. On a gagné, au moins. [rires]\n\nMme Cordier : Bienvenue, M. Marchetti. Nous sommes donc vingt et un. On vient d'adopter le PV du 30 juin, on passe au point 2.\n\nPoint 2 — Modification du règlement intérieur\n\nMme Cordier : Alors c'est le gros point de la soirée, je le sais. Je vais laisser M. Vauquelin présenter les modifications, et après on en discute. Je rappelle qu'on en a déjà parlé en conseil pédagogique et avec les délégués des élèves, et que le projet vous a été envoyé avec la convocation.\n\nM. Vauquelin : Merci. Il y a trois modifications. La première, c'est l'article 12 sur le téléphone portable. Aujourd'hui, l'usage est interdit en classe mais toléré dans la cour et au foyer. On vous propose ce qu'on appelle une « pause numérique » : le téléphone est éteint et rangé dans le sac de l'entrée dans le collège jusqu'à la sortie, y compris pendant la pause méridienne. Un usage pédagogique reste possible en classe, sur autorisation explicite de l'enseignant. En cas de manquement, le téléphone est confisqué et rendu à l'élève en fin de journée ; en cas de récidive, il est remis au représentant légal. Deuxième modification, l'article 18 sur la tenue en EPS : on précise que les chaussures de sport sont obligatoires et qu'une tenue de rechange est demandée. Et troisième modification, l'article 21, l'échelle des punitions : on ajoute la retenue le mercredi après-midi, de 13 h 30 à 15 h 30, pour les manquements répétés.\n\nMme Cordier : Je précise une chose tout de suite, parce que je sais que la question va venir. Dans la première version, celle qui a circulé en juin, on avait envisagé de faire déposer les téléphones dans des casiers fermés à l'entrée du collège. On a abandonné cette idée. D'une part ça coûtait cher, on avait un devis à environ 9 000 euros, et d'autre part ça posait un problème de responsabilité en cas de vol ou de casse. Donc ce n'est plus du tout dans le projet. Le texte qui vous est soumis, c'est : éteint et rangé dans le sac.\n\nM. Ostrowski : Merci de le préciser, parce que beaucoup de parents nous en ont parlé, des casiers. Mais sur le fond, nous, les parents, on n'est pas tous d'accord sur la pause méridienne. Les élèves de troisième, ils ont quatorze, quinze ans. Leur interdire le téléphone de 8 heures à 17 heures, y compris au foyer, c'est un peu…\n\nMme Kasprzak : Pardon, mais au foyer justement, on voit des élèves de troisième qui ne se parlent plus, qui sont chacun sur leur écran. Et les histoires de photos qui circulent, ça part souvent de là.\n\nM. Ostrowski : Je ne dis pas le contraire, mais…\n\nMme Cordier : Laissez M. Ostrowski finir, s'il vous plaît.\n\nM. Ostrowski : Je disais : on comprend l'objectif, mais on aurait préféré une gradation. Les sixièmes et cinquièmes, d'accord, interdiction totale. Les troisièmes, au moins au foyer, pendant la pause du midi, sous la surveillance des assistants d'éducation.\n\nM. Tessier : Je peux répondre sur la surveillance ? Le foyer, le midi, c'est un assistant d'éducation pour une soixantaine d'élèves. Il ne peut pas surveiller ce que font soixante élèves sur leur téléphone. Et les incidents de cyberharcèlement qu'on a traités l'an dernier, j'en ai compté onze, il y en a au moins sept qui sont partis d'une photo ou d'une vidéo prise dans l'enceinte du collège.\n\nLéna (élève) : Je peux dire quelque chose ?\n\nMme Cordier : Bien sûr, Léna.\n\nLéna : On en a parlé au conseil de la vie collégienne. Les élèves de troisième, en majorité, ils sont contre l'interdiction au foyer. Mais il y en a aussi qui disent que ce serait plus simple pour tout le monde si c'était la même règle pour tous. Donc c'est partagé. Et la vraie demande, c'est surtout que le téléphone confisqué soit rendu le soir, pas trois jours après comme ça arrive parfois.\n\nM. Vauquelin : C'est justement ce qu'on écrit : rendu en fin de journée. Il n'y a plus de confiscation de plusieurs jours.\n\nMme Sy : Et quand c'est remis au représentant légal, ça veut dire quoi concrètement ? Les parents doivent venir au collège ? Parce qu'avec le travail…\n\nM. Vauquelin : Ça veut dire que le parent vient le récupérer à la vie scolaire, oui. Les horaires de la vie scolaire, c'est jusqu'à 17 h 30. Si ce n'est pas possible, on trouve une solution au cas par cas.\n\nMme Chaumont : Madame la principale, nous demandons une suspension de séance de dix minutes. Les représentants des parents voudraient se concerter avant le vote.\n\nMme Cordier : C'est de droit. Il est 18 h 20, on reprend à 18 h 30.\n\n[Suspension de séance de 18 h 20 à 18 h 30]\n\nMme Cordier : On reprend. Il est 18 h 31. Madame Chaumont ?\n\nMme Chaumont : Oui. Les représentants des parents déposent un amendement à l'article 12 : autoriser l'usage du téléphone au foyer, pendant la pause méridienne, pour les seuls élèves de troisième. Le reste de l'article ne change pas.\n\nMme Cordier : Très bien. Je mets d'abord aux voix l'amendement, puis le règlement intérieur dans son ensemble. Je rappelle que ce sont des votes à main levée, sauf si quelqu'un demande un vote à bulletin secret.\n\nM. Pellerin : Non, à main levée ça va.\n\nMme Cordier : Alors l'amendement des parents : autoriser le téléphone au foyer pendant la pause méridienne pour les troisièmes. Qui est pour ? Sept. Qui est contre ? Douze. Qui s'abstient ? Deux. L'amendement est rejeté : sept pour, douze contre, deux abstentions.\n\nM. Benslimane : Excusez-moi, juste pour le PV, les deux abstentions c'est Léna et moi.\n\nMme Roussel : Je note.\n\nMme Cordier : Maintenant, le règlement intérieur modifié dans son ensemble, avec les trois modifications des articles 12, 18 et 21, tel qu'il vous a été envoyé. Qui est pour ? Quinze. Contre ? Quatre. Abstentions ? Deux. Le règlement intérieur modifié est adopté : quinze pour, quatre contre, deux abstentions.\n\nM. Pellerin : Pour le PV, les quatre contre, ce sont des représentants des parents.\n\nMme Roussel : C'est noté, quatre voix contre chez les parents.\n\nMme Cordier : Le nouveau règlement intérieur entrera en application à la rentrée des vacances de la Toussaint, le lundi 2 novembre 2026. M. Vauquelin, vous vous chargez de le diffuser aux familles ?\n\nM. Vauquelin : Oui, je le mets sur l'ENT et dans le carnet de liaison numérique, avant les vacances, donc au plus tard le vendredi 16 octobre. Et je demanderai aux professeurs principaux de le présenter aux élèves en heure de vie de classe la semaine de la rentrée, la semaine du 2 novembre.\n\nM. Lebrun : Une question pratique, sur la retenue du mercredi après-midi. Le mercredi, le dernier car part à 12 h 15. Les élèves qui habitent dans les hameaux, comment ils rentrent à 15 h 30 ?\n\nMme Cordier : C'est une vraie question. La retenue reste une punition, elle est notifiée à la famille au moins quarante-huit heures avant, et c'est la famille qui assure le retour. Je sais que ce n'est pas simple pour tout le monde.\n\nM. Lebrun : Et le transport scolaire, ce n'est pas la commune, c'est la région. Donc nous on ne pourra rien faire.\n\nMme Sy : Il faudrait au moins prévoir une solution pour les familles qui n'ont pas de voiture.\n\nMme Cordier : On regardera au cas par cas, mais je ne peux pas m'engager ce soir sur une solution de transport. On avance.\n\nPoint 3 — Voyages et sorties scolaires 2026-2027\n\nMme Cordier : Mme Saintonge nous a rejoints. On a trois voyages avec nuitées à examiner, plus le programme des sorties sans nuitée. Mme Ferhat a préparé les budgets. Je commence par le séjour neige des cinquièmes.\n\nMme Ferhat : Alors le séjour neige concerne les quatre classes de cinquième, 98 élèves, au centre d'hébergement Les Myrtilles, dans le Jura, du lundi 25 au vendredi 29 janvier 2027. Le coût total est de 420 euros par élève, transport compris. Le financement : participation des familles 295 euros, foyer socio-éducatif 35 euros, et une aide du département au titre des séjours éducatifs de 90 euros par élève, qui a déjà été notifiée. 295 plus 35 plus 90, ça fait bien 420. Les familles pourront payer en trois fois, et le fonds social collégien pourra aider les familles qui en ont besoin, après examen par la commission.\n\nM. Marchetti : Et on a les accompagnateurs, c'est bon, on est neuf, dont deux assistants d'éducation.\n\nMme Cordier : Des questions ? Non ? Je mets aux voix le séjour neige des cinquièmes, avec son budget et la participation des familles de 295 euros. Qui est contre ? Qui s'abstient ? Adopté à l'unanimité des vingt et un présents.\n\nMme Ferhat : Il faudra que je lance la consultation pour le transporteur, je le fais avant la fin du mois d'octobre.\n\nMme Cordier : Très bien. Deuxième voyage, l'Andalousie. Mme Saintonge ?\n\nMme Saintonge : Merci. C'est un voyage pour les élèves hispanistes de quatrième, 46 élèves, à Séville et Grenade, du lundi 12 au vendredi 16 avril 2027, avec hébergement en familles. Le coût total est de 560 euros par élève. Le financement prévu : 380 euros de participation des familles, 60 euros du foyer, et 120 euros d'aide du département au titre de la mobilité internationale.\n\nMme Ferhat : Et là je dois être claire : cette aide de 120 euros n'est pas acquise. La campagne de demande du département est ouverte jusqu'au lundi 30 novembre 2026, et on n'aura la réponse qu'en janvier.\n\nMme Arnaud-Poitevin : Je confirme, la commission permanente du département statue en janvier. Je ne peux rien promettre, il y a beaucoup de demandes cette année.\n\nM. Pellerin : Alors justement, 380 euros, c'est déjà beaucoup. Et si l'aide n'arrive pas, on passe à 500 euros pour les familles ? Nous on propose de plafonner la participation des familles à 350 euros, quoi qu'il arrive.\n\nMme Ferhat : Je comprends, mais à 350 il manque 30 euros par élève, soit 1 380 euros, et je n'ai pas de recette en face. Le foyer ne peut pas mettre plus de 60 euros, il a déjà le séjour neige.\n\nMme Saintonge : Et on a déjà réduit le programme, on a enlevé l'excursion à Cordoue pour descendre le prix.\n\nMme Cordier : Ce que je vous propose, c'est de voter le voyage sous réserve de l'obtention de l'aide départementale de 120 euros. Si l'aide est refusée, le voyage reviendra devant le conseil d'administration, on rediscutera du financement à ce moment-là. Il n'y aura pas d'augmentation automatique de la participation des familles.\n\nM. Pellerin : Bon. Ça me va, à condition que ce soit écrit comme ça dans le PV.\n\nMme Roussel : Je l'écris comme ça.\n\nMme Cordier : Et donc le plafond à 350 euros, M. Pellerin, vous le maintenez comme proposition à voter ?\n\nM. Pellerin : Non, on le retire, puisque de toute façon ça revient au CA si l'aide est refusée.\n\nMme Cordier : D'accord. Je mets aux voix le voyage en Andalousie des quatrièmes hispanistes, du 12 au 16 avril 2027, avec une participation des familles de 380 euros, sous réserve de l'obtention de l'aide du département de 120 euros par élève. Qui est contre ? Personne. Qui s'abstient ? Deux. Adopté : dix-neuf pour, zéro contre, deux abstentions.\n\nMme Saintonge : Merci. Je dépose la demande d'aide avec Mme Ferhat, avant la date limite du 30 novembre.\n\nMme Ferhat : Oui, on la fait ensemble.\n\nMme Cordier : Troisième voyage, le séjour à Londres des troisièmes. Mme Kasprzak, vous vouliez dire quelque chose ?\n\nMme Kasprzak : Oui. Je suis désolée, mais je retire le séjour de l'ordre du jour. On n'a que trois accompagnateurs sur les cinq nécessaires, deux collègues se sont désistés la semaine dernière. Je ne veux pas qu'on vote un voyage qu'on n'est pas sûrs de pouvoir encadrer.\n\nM. Ostrowski : C'est dommage, les familles l'attendaient. Il sera représenté plus tard ?\n\nMme Kasprzak : Peut-être, si je trouve des accompagnateurs. Mais je ne peux pas promettre, et les tarifs vont augmenter si on réserve tard.\n\nMme Cordier : On ne vote donc pas le séjour à Londres ce soir. Si Mme Kasprzak revient avec un projet complet, on l'examinera, mais rien n'est fixé. Enfin, le programme des sorties sans nuitée : vous avez le tableau en annexe, il y a quatorze sorties, théâtre, musée, sortie géologie pour les quatrièmes, cross départemental, etc. Toutes sont gratuites pour les familles, financées sur les crédits pédagogiques ou par le foyer. Des remarques ?\n\nMme Bellamy : Juste une correction dans le tableau : la sortie au théâtre de Lézonville pour les sixièmes, c'est le mardi 8 décembre, pas le 1er. Le 1er il n'y avait plus de places.\n\nMme Cordier : C'est noté, le mardi 8 décembre. Je mets aux voix le programme des sorties sans nuitée, ainsi corrigé. Contre ? Abstentions ? Adopté à l'unanimité.\n\nM. Pellerin : Excusez-moi, je reviens deux secondes sur le règlement intérieur. Une question qu'on m'a posée pendant la suspension : un élève qui a un problème de santé, un diabète par exemple, avec une application sur son téléphone ?\n\nMme Cordier : Bonne question. Les élèves qui ont un projet d'accueil individualisé gardent l'usage du téléphone prévu dans leur PAI. Ça figure déjà dans l'article 12, dernier alinéa, mais je comprends que ce n'était pas très visible. M. Vauquelin le rappellera dans le courrier aux familles.\n\nM. Vauquelin : Oui, je l'ajoute dans le courrier.\n\nPoint 4 — Bilan de la rentrée et dotation horaire globale\n\nMme Cordier : On passe au bilan de rentrée. M. Vauquelin.\n\nM. Vauquelin : Alors à la rentrée 2026, on a 642 élèves, répartis en 24 divisions, six par niveau. Les effectifs par niveau : 158 en sixième, 161 en cinquième, 178 en quatrième et 145 en troisième. Donc vous voyez tout de suite le problème, c'est la quatrième : 178 élèves pour six divisions, ça fait près de 30 élèves par classe. La dotation horaire globale de cette année, c'est 768 heures, dont 712 heures postes et 56 heures supplémentaires années. Sur les heures de marge, on a maintenu les dédoublements en sciences en sixième et en cinquième, et le dispositif « Devoirs faits » quatre soirs par semaine.\n\nM. N'Diaye : Et pas en quatrième. Moi j'ai deux quatrièmes à 30 en maths, et en sciences on ne dédouble pas. On fait des TP de physique à 30 dans des salles prévues pour 24. C'est un problème de sécurité aussi, pas seulement de pédagogie.\n\nMme Bellamy : Et en langues c'est pareil, en espagnol LV2, une des classes a 31 élèves avec le regroupement.\n\nMme Varenne : En technologie aussi, on a 15 postes informatiques pour 30 élèves.\n\nMme Cordier : J'entends tout ça et je partage le constat. J'ai demandé en juin une dotation complémentaire, la DSDEN nous a accordé 6 heures, qui sont déjà dans les 768. Je n'ai pas eu d'autre réponse.\n\nM. N'Diaye : C'est pour ça que les représentants des enseignants présentent une motion. Je la lis : « Le conseil d'administration du collège Les Hautes-Bruyères constate que les six divisions de quatrième comptent en moyenne près de 30 élèves et que les conditions d'enseignement, notamment en sciences, en technologie et en langues, ne sont pas satisfaisantes. Il demande à la direction des services départementaux de l'Éducation nationale l'attribution, dès cette année scolaire, d'une dotation complémentaire de 18 heures permettant de dédoubler les enseignements de sciences et de langues en quatrième, et l'examen attentif des effectifs de troisième pour la rentrée 2027. »\n\nM. Ostrowski : Les parents soutiennent la motion.\n\nMme Arnaud-Poitevin : Je voterai pour aussi, à titre personnel et au nom du département, les effectifs de ce collège augmentent depuis trois ans, c'est connu.\n\nM. Lebrun : La commune aussi.\n\nMme Cordier : Je précise que les membres de l'administration, c'est-à-dire moi-même, M. Vauquelin, Mme Ferhat et M. Tessier, ne prennent pas part au vote sur cette motion. Ce n'est pas un désaccord sur le fond, c'est que la motion s'adresse à notre hiérarchie et que c'est moi qui la transmettrai.\n\nM. N'Diaye : On l'entend.\n\nM. Marchetti : Et est-ce qu'on pourrait aussi demander une audience au DASEN, avec des parents et des enseignants ? Ce serait plus fort qu'un papier.\n\nMme Cordier : On peut en parler, mais je ne vais pas l'organiser ce soir. Ça se décide dans un autre cadre.\n\nM. Marchetti : D'accord, on en reparlera.\n\nMme Cordier : Je mets aux voix la motion telle que lue par M. Nyaye… pardon, M. N'Diaye. [rires] Votants : dix-sept, puisque quatre membres ne prennent pas part au vote. Qui est pour ? Treize. Contre ? Zéro. Abstentions ? Quatre. La motion est adoptée : treize pour, zéro contre, quatre abstentions. Je la transmets à la DSDEN avant les vacances, au plus tard le vendredi 16 octobre.\n\nMme Kasprzak : Et la dotation pour l'année prochaine, la DHG 2027-2028, on la verra quand ?\n\nMme Cordier : En général elle arrive fin janvier ou début février, et elle est présentée au conseil d'administration dans la foulée. Je n'ai pas de date pour l'instant, ça dépend du calendrier du rectorat.\n\nPoint 5 — Budget\n\n[Mme Arnaud-Poitevin quitte la séance à 19 h 05]\n\nMme Arnaud-Poitevin : Je vous prie de m'excuser, j'ai une réunion de commission au département à 19 h 30. Bonne fin de séance.\n\nMme Cordier : Merci madame. Nous sommes donc vingt. Et M. Lacombe nous a rejoints, bonsoir.\n\nM. Lacombe (agent comptable) : Bonsoir à tous, désolé, le CA du lycée a été un peu long.\n\nMme Cordier : Mme Ferhat, le budget.\n\nMme Ferhat : Alors d'abord une information. Le département nous a notifié la dotation de fonctionnement pour 2027 : 148 600 euros. C'est une baisse d'environ 3 % par rapport à 2026, où on avait 153 200 euros. Le budget primitif 2027 sera préparé avec cette enveloppe et vous sera soumis au prochain conseil d'administration.\n\nEnsuite, une décision budgétaire modificative pour vote, la DBM n° 3. Le four mixte de la cuisine est hors service depuis le 21 septembre. Le réparateur nous dit que la carte électronique et la sonde sont à changer, c'est presque le prix d'un four neuf, et le modèle n'est plus fabriqué. Mme Picot pourra vous le confirmer.\n\nMme Picot : Oui, depuis le 21 on fait avec le petit four et les plaques, on sert plus de crudités et de plats froids, les élèves l'ont remarqué.\n\nYanis (élève) : Ah oui, on l'a remarqué. [rires]\n\nMme Ferhat : Le remplacement coûte 12 400 euros toutes taxes comprises, installation comprise. Je vous propose de le financer par un prélèvement sur le fonds de roulement du service de restauration et d'hébergement. Le fonds de roulement est aujourd'hui de 186 000 euros, soit environ 74 jours de fonctionnement. Après le prélèvement, on serait à 173 600 euros.\n\nM. Lacombe : Je confirme que le niveau du fonds de roulement le permet. Ça reste largement au-dessus du seuil prudentiel qu'on se fixe, qui est de 30 jours.\n\nM. Pellerin : Une question de principe. Un four de cuisine collective, c'est de l'équipement, ce n'est pas au département de le payer ? Le département a un plan d'équipement pour les collèges. Pourquoi on ne demande pas à être inscrits sur le plan 2027 plutôt que de puiser dans nos réserves ?\n\nMme Ferhat : On peut le demander, mais le plan d'équipement 2027 sera arrêté au printemps, et le four serait livré au mieux en septembre prochain. On ne peut pas faire une année scolaire entière sans four.\n\nM. Lebrun : Je ne peux pas parler au nom du département, Mme Arnaud-Poitevin est partie, mais je sais que le plan d'équipement est très demandé.\n\nM. Pellerin : Dommage qu'elle soit partie justement. Bon, j'aurais préféré qu'on attende le plan, mais je comprends l'urgence.\n\nMme Cordier : On ne retient pas l'idée d'attendre le plan d'équipement, l'urgence est trop forte. Je mets aux voix la DBM n° 3 : prélèvement de 12 400 euros sur le fonds de roulement pour le remplacement du four mixte. Qui est contre ? Personne. Abstentions ? Trois. Adoptée : dix-sept pour, zéro contre, trois abstentions.\n\nMme Ferhat : Merci. Je lance la commande dès que la DBM sera exécutoire, c'est-à-dire après le délai de transmission au contrôle de légalité.\n\nMme Ferhat : Ensuite, pour information seulement, la DBM n° 4, qui ne se vote pas puisqu'il s'agit de recettes affectées : 3 200 euros de crédits supplémentaires de l'État pour le fonds social collégien, et 1 150 euros de la commune pour le dispositif « Collège au cinéma ».\n\nM. Lebrun : Voilà, la commune fait sa part. [rires]\n\nMme Ferhat : Merci à la commune. Deux autres délibérations. D'abord, la convention d'utilisation du gymnase municipal pour l'année 2026-2027 : la commune met le gymnase à disposition pour les cours d'EPS, il faut autoriser Mme la principale à signer.\n\nM. Marchetti : Sans le gymnase on fait cours sur le plateau extérieur, donc oui, autorisez. [rires]\n\nMme Cordier : Je mets aux voix l'autorisation de signer la convention d'utilisation du gymnase municipal pour 2026-2027. Contre ? Abstentions ? Adoptée à l'unanimité des vingt présents.\n\nMme Ferhat : Et enfin, l'acceptation d'un don. L'entreprise Menuiserie Fourcade Frères propose un don de 500 euros au club robotique… attendez, pardon, je relis le courrier : c'est 450 euros, pas 500. 450 euros, affectés à l'achat de kits de robotique pour le club.\n\nMme Cordier : 450 euros donc. Je mets aux voix l'acceptation du don de 450 euros de la Menuiserie Fourcade Frères au profit du club robotique. Contre ? Abstentions ? Adopté à l'unanimité.\n\nM. Ostrowski : Et le budget primitif, on le vote quand ?\n\nMme Cordier : Au prochain conseil d'administration, qui sera aussi le premier conseil de la nouvelle mandature, avec l'installation des nouveaux membres. Ce sera le jeudi 19 novembre… non, pardon, je me trompe, le 19 c'est le conseil pédagogique. Le prochain CA, c'est le jeudi 26 novembre 2026, à 17 h 30.\n\nMme Ferhat : Et je vous enverrai les documents budgétaires au moins dix jours avant, donc au plus tard le lundi 16 novembre.\n\nM. Lacombe : Je serai présent le 26 novembre.\n\nPoint 6 — Questions diverses\n\nMme Cordier : Nous avons reçu deux questions écrites, une des parents et une des élèves. Et M. Lebrun m'a dit qu'il voulait dire un mot. Mme Sy, pour les parents.\n\nMme Sy : Oui. Plusieurs familles nous signalent que les toilettes du bâtiment C sont fermées tous les après-midi depuis la rentrée. Les élèves doivent traverser toute la cour pour aller au bâtiment A, et certains n'y vont plus du tout de la journée.\n\nMme Picot : C'est parce qu'une collègue agent est en arrêt depuis début septembre et qu'elle n'est pas remplacée. On n'a pas assez de monde pour nettoyer le bâtiment C l'après-midi, alors on ferme.\n\nMme Cordier : Les agents sont des personnels du département. J'ai déjà signalé l'absence oralement, mais je vais écrire officiellement au département pour demander un remplacement. Je le fais cette semaine, avant le vendredi 9 octobre.\n\nM. Lebrun : La commune ne peut pas mettre d'agent, ce n'est pas dans nos compétences, je le dis tout de suite.\n\nMme Sy : On ne vous demandait pas ça, monsieur. [rires]\n\nMme Cordier : Yanis, pour les élèves ?\n\nYanis : Les élèves de sixième, ils ont des cartables trop lourds, ils demandent s'il pourrait y avoir des casiers pour laisser des livres.\n\nM. Pellerin : Des casiers ? Je croyais qu'on avait dit que c'était trop cher, tout à l'heure.\n\nMme Cordier : Non, là ce n'est pas la même chose. Tout à l'heure c'était des casiers pour déposer les téléphones à l'entrée, et ça on l'a abandonné. Là, Yanis parle de casiers pour les affaires des sixièmes. C'est une autre demande.\n\nMme Ferhat : Je peux chiffrer des casiers pour les sixièmes et le présenter dans le cadre du budget primitif 2027, pour le CA du 26 novembre.\n\nMme Cordier : Très bien, Mme Ferhat chiffre et on en reparle au budget primitif. Ce n'est pas décidé ce soir. Mme Bellamy, vous aviez aussi une remarque ?\n\nMme Bellamy : Oui, très vite, la salle B12, il fait 15 degrés le matin. Le chauffage ne fonctionne pas bien depuis la remise en route.\n\nMme Ferhat : C'est déjà signalé au département, le 28 septembre. L'entreprise de maintenance doit passer, je n'ai pas encore de date.\n\nM. Lebrun : Oui, alors moi, c'était pour vous informer que la commune organise le forum des associations samedi… non, c'était samedi dernier, pardon, il est passé. [rires] Non, ce que je voulais dire, c'est que la commune réfléchit à un « pédibus » pour les élèves du centre-bourg, mais c'est vraiment au stade de l'idée, on n'a rien décidé en conseil municipal.\n\nMme Cordier : Merci, vous nous tiendrez informés. Dernières informations de ma part : les élections des représentants des parents ont lieu ce vendredi 9 octobre, le vote se fait par correspondance ou à l'urne, au collège, de 8 heures à 12 heures. Et je rappelle la date du prochain conseil d'administration : jeudi 26 novembre 2026, 17 h 30. Est-ce qu'il y a d'autres questions ?\n\nM. Ostrowski : Juste un mot pour remercier, puisque c'est la dernière séance pour plusieurs d'entre nous. Mme Delorme et moi, on ne se représente pas.\n\nMme Cordier : Merci à vous deux pour votre engagement pendant ces années. Merci à tous. La séance est levée, il est 20 h 05.\n\n[Fin de l'enregistrement]"
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "Mme Cordier (principale, présidente de séance)",
    "M. Vauquelin (principal adjoint)",
    "Mme Ferhat (adjointe gestionnaire)",
    "M. Tessier (CPE)",
    "Mme Arnaud-Poitevin (conseillère départementale), partie à 19 h 05 avant le point budget",
    "M. Lebrun (adjoint au maire chargé des affaires scolaires)",
    "Représentants des enseignants : Mme Roussel (secrétaire de séance), Mme Kasprzak, M. N'Diaye, Mme Bellamy, Mme Varenne (suppléante de M. Guérin)",
    "M. Marchetti (enseignant), arrivé à 17 h 50 après le vote du procès-verbal",
    "Représentants des personnels ATSS : Mme Picot, M. Benslimane",
    "Représentants des parents : Mme Chaumont, M. Ostrowski, Mme Sy, M. Pellerin, Mme Delorme",
    "Représentants des élèves : Léna (3e) et Yanis (4e)",
    "Sans voix délibérative : Mme Saintonge (professeure d'espagnol, invitée pour le point voyages) ; M. Lacombe (agent comptable, présent à partir du point budget)",
    "Absent : M. Guérin (enseignant), remplacé par sa suppléante Mme Varenne",
    "Excusés : M. Moutier (département) ; M. Baudoin (parent, pouvoir à Mme Chaumont refusé, suppléante absente)",
    "Absent : représentant de la communauté de communes du Val de Lézon",
    "20 présents à l'ouverture, 21 après l'arrivée de M. Marchetti, 20 après le départ de Mme Arnaud-Poitevin (quorum : 13)"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Procès-verbal du conseil d'administration du 30 juin 2026 adopté à l'unanimité des 20 présents, après correction du montant de la subvention au foyer socio-éducatif (1 800 € et non 1 500 €)"
    },
    {
      "ref": "D2",
      "texte": "Amendement des représentants des parents (téléphone autorisé au foyer pendant la pause méridienne pour les élèves de 3e) rejeté : 7 pour, 12 contre, 2 abstentions"
    },
    {
      "ref": "D3",
      "texte": "Règlement intérieur modifié adopté (article 12 « pause numérique » : téléphone éteint et rangé dans le sac de l'entrée à la sortie, y compris pendant la pause méridienne, confisqué et rendu en fin de journée, remis au représentant légal en cas de récidive ; article 18 tenue d'EPS ; article 21 retenue le mercredi de 13 h 30 à 15 h 30) : 15 pour, 4 contre (représentants des parents), 2 abstentions ; application le lundi 2 novembre 2026"
    },
    {
      "ref": "D4",
      "texte": "Séjour neige des 5e (98 élèves, centre Les Myrtilles dans le Jura, du lundi 25 au vendredi 29 janvier 2027) adopté à l'unanimité des 21 présents : coût de 420 € par élève, dont 295 € de participation des familles, 35 € du foyer et 90 € d'aide départementale déjà notifiée"
    },
    {
      "ref": "D5",
      "texte": "Voyage en Andalousie des 4e hispanistes (46 élèves, du lundi 12 au vendredi 16 avril 2027, 560 € par élève, participation des familles de 380 €) adopté SOUS RÉSERVE de l'obtention de l'aide départementale de 120 € par élève : 19 pour, 0 contre, 2 abstentions ; en cas de refus de l'aide, retour devant le conseil d'administration"
    },
    {
      "ref": "D6",
      "texte": "Programme des 14 sorties sans nuitée (gratuites pour les familles) adopté à l'unanimité, la sortie théâtre des 6e étant fixée au mardi 8 décembre"
    },
    {
      "ref": "D7",
      "texte": "Motion demandant à la DSDEN une dotation complémentaire de 18 heures dès cette année pour dédoubler les enseignements de sciences et de langues en 4e, et l'examen des effectifs de 3e pour la rentrée 2027, adoptée : 13 pour, 0 contre, 4 abstentions (17 votants, les 4 membres de l'administration ne prenant pas part au vote)"
    },
    {
      "ref": "D8",
      "texte": "DBM n° 3 adoptée : prélèvement de 12 400 € TTC sur le fonds de roulement du service de restauration et d'hébergement pour remplacer le four mixte, 17 pour, 0 contre, 3 abstentions"
    },
    {
      "ref": "D9",
      "texte": "Autorisation donnée à la principale de signer la convention d'utilisation du gymnase municipal pour 2026-2027, à l'unanimité des 20 présents"
    },
    {
      "ref": "D10",
      "texte": "Acceptation du don de 450 € de la Menuiserie Fourcade Frères au profit du club robotique (achat de kits), à l'unanimité"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Mettre en ligne sur l'ENT le procès-verbal du 30 juin 2026 corrigé",
      "responsable": "non précisé",
      "echeance": "non fixée"
    },
    {
      "ref": "A2",
      "action": "Diffuser le règlement intérieur modifié aux familles (ENT et carnet de liaison numérique), en rappelant l'usage du téléphone prévu par les PAI",
      "responsable": "M. Vauquelin",
      "echeance": "au plus tard le vendredi 16 octobre 2026"
    },
    {
      "ref": "A3",
      "action": "Demander aux professeurs principaux de présenter le règlement intérieur aux élèves en heure de vie de classe",
      "responsable": "M. Vauquelin (présentation par les professeurs principaux)",
      "echeance": "semaine du lundi 2 novembre 2026"
    },
    {
      "ref": "A4",
      "action": "Lancer la consultation du transporteur pour le séjour neige",
      "responsable": "Mme Ferhat",
      "echeance": "avant la fin octobre 2026"
    },
    {
      "ref": "A5",
      "action": "Déposer la demande d'aide départementale à la mobilité internationale pour le voyage en Andalousie",
      "responsable": "Mme Saintonge et Mme Ferhat",
      "echeance": "avant le lundi 30 novembre 2026"
    },
    {
      "ref": "A6",
      "action": "Transmettre la motion sur la dotation horaire à la DSDEN",
      "responsable": "Mme Cordier",
      "echeance": "au plus tard le vendredi 16 octobre 2026"
    },
    {
      "ref": "A7",
      "action": "Commander le four mixte",
      "responsable": "Mme Ferhat",
      "echeance": "dès que la DBM n° 3 sera exécutoire"
    },
    {
      "ref": "A8",
      "action": "Envoyer aux membres les documents du budget primitif 2027",
      "responsable": "Mme Ferhat",
      "echeance": "au plus tard le lundi 16 novembre 2026"
    },
    {
      "ref": "A9",
      "action": "Écrire officiellement au département pour demander le remplacement de l'agent absent (toilettes du bâtiment C)",
      "responsable": "Mme Cordier",
      "echeance": "avant le vendredi 9 octobre 2026"
    },
    {
      "ref": "A10",
      "action": "Chiffrer des casiers pour les affaires des élèves de 6e",
      "responsable": "Mme Ferhat",
      "echeance": "budget primitif 2027, CA du jeudi 26 novembre 2026"
    }
  ],
  "pieges": [
    "Pouvoir de M. Baudoin à Mme Chaumont : refusé (pas de procuration au conseil d'administration)",
    "M. Marchetti est arrivé après le vote du procès-verbal ; Mme Arnaud-Poitevin est partie avant le point budget et n'a pas pris part aux votes budgétaires",
    "Subvention du foyer au PV du 30 juin : 1 800 € et non 1 500 € (erratum)",
    "Dépôt des téléphones dans des casiers fermés à l'entrée (devis d'environ 9 000 €) : abandonné, NON retenu",
    "Amendement des parents (téléphone au foyer pour les 3e) : REJETÉ, ne pas le présenter comme adopté",
    "Voyage en Andalousie : adopté sous réserve de l'aide départementale de 120 €, qui n'est PAS acquise ; pas d'augmentation automatique de la participation des familles",
    "Plafonnement de la participation des familles à 350 € : proposé puis retiré par M. Pellerin, NON voté",
    "Séjour à Londres des 3e : retiré de l'ordre du jour, NON voté, aucune date de nouvel examen",
    "Sortie théâtre des 6e : le mardi 8 décembre et non le 1er décembre",
    "Audience auprès du DASEN : évoquée par M. Marchetti, NON décidée",
    "Les membres de l'administration n'ont pas pris part au vote de la motion (ce n'est pas une abstention ni un vote contre)",
    "Présentation de la DHG 2027-2028 : aucune date fixée",
    "Attendre le plan d'équipement 2027 du département pour le four : proposé par M. Pellerin, NON retenu",
    "DBM n° 4 (3 200 € fonds social collégien, 1 150 € de la commune pour « Collège au cinéma ») : présentée pour information, NON votée",
    "Don de la Menuiserie Fourcade Frères : 450 € et non 500 €",
    "Prochain CA (installation et budget primitif 2027) : jeudi 26 novembre 2026 et non le 19 novembre",
    "Casiers pour les 6e : seulement à chiffrer, NON décidés",
    "Solution de transport pour les retenues du mercredi : aucune décision ; « pédibus » de la commune : simple idée, rien décidé",
    "Chauffage de la salle B12 : déjà signalé au département le 28 septembre, aucune date d'intervention"
  ]
}
```

### Sortie (statut ok)

```text
- M. Marchetti a approuvé l'approbation du don de 450 euros de la Menuiserie Fourcade Frères au profit du club robotique, adoptée à l'unanimité. Il a également informé les participants des élections des représentants des parents, du vote par correspondance ou par urne, et de la date du prochain conseil d'administration. Il a également noté que la commune organisera un forum des associations et qu'elle travaillera sur un "pédibus" pour les élèves du centre-bourg.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0 — L'adoption du PV du 30 juin corrigé (1 800 €) n'est pas mentionnée.
  - D2 : 0 — Le rejet de l'amendement des parents n'est pas mentionné.
  - D3 : 0 — L'adoption du règlement intérieur modifié n'est pas mentionnée.
  - D4 : 0 — Le séjour neige des 5e n'est pas mentionné.
  - D5 : 0 — Le voyage en Andalousie adopté sous réserve n'est pas mentionné.
  - D6 : 0 — Le programme des sorties sans nuitée n'est pas mentionné.
  - D7 : 0 — La motion sur la dotation horaire n'est pas mentionnée.
  - D8 : 0 — La DBM n° 3 pour le four mixte n'est pas mentionnée.
  - D9 : 0 — La convention d'utilisation du gymnase n'est pas mentionnée.
  - D10 : 1 — « l'approbation du don de 450 euros de la Menuiserie Fourcade Frères au profit du club robotique, adoptée à l'unanimité » : la décision est correcte, malgré une attribution erronée à M. Marchetti.
  - A1 : 0 — La mise en ligne du PV corrigé n'est pas mentionnée.
  - A2 : 0 — La diffusion du règlement intérieur par M. Vauquelin n'est pas mentionnée.
  - A3 : 0 — La présentation du règlement intérieur en heure de vie de classe n'est pas mentionnée.
  - A4 : 0 — La consultation du transporteur n'est pas mentionnée.
  - A5 : 0 — Le dépôt de la demande d'aide départementale n'est pas mentionné.
  - A6 : 0 — La transmission de la motion à la DSDEN n'est pas mentionnée.
  - A7 : 0 — La commande du four n'est pas mentionnée.
  - A8 : 0 — L'envoi des documents budgétaires n'est pas mentionné.
  - A9 : 0 — Le courrier au département sur l'agent absent n'est pas mentionné.
  - A10 : 0 — Le chiffrage des casiers des 6e n'est pas mentionné.
- `absence_invention` : 0 — La sortie attribue à M. Marchetti des propos tenus par Mme Cordier (« Il a également informé les participants des élections »), présente le forum des associations comme futur (« organisera ») alors qu'il est passé, et présente le pédibus comme engagé (« travaillera sur ») alors qu'il n'est qu'une idée (piège).
- `structure` : 0 — Aucune des quatre sections (Participants, Points abordés, Décisions, Actions) n'est présente.
- Inventions : M. Marchetti a approuvé le don (attribution erronée, vote du conseil à l'unanimité); M. Marchetti a informé des élections et de la date du prochain CA (propos de Mme Cordier); La commune organisera un forum des associations (il a déjà eu lieu samedi dernier); La commune travaillera sur un « pédibus » (simple idée, rien décidé)
- Confiance : haute

## CR-023 (CR, moyen)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de ce comité de pilotage : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 973,
  "notes": "COPIL Contrat local de santé (CLS) 2024-2028 de Pontcarel — jeudi 17/09/2026 — 9h30-12h15 — salle Marianne, hôtel de ville\nNotes : S. Benamar (coordinatrice CLS)\n\nPrésents :\n- M. Desbrosses, maire de Pontcarel (coprésident)\n- Mme Laborde, délégation départementale ARS (coprésidente)\n- M. Ogier, conseiller municipal délégué à la santé\n- Mme Benamar, coordinatrice CLS (ville)\n- Dr Lemaire, président de la CPTS du Haut-Pontcarel (en visio, quitte à 11h)\n- Mme Ricard, CPAM, chargée de mission prévention\n- M. Vasseur, département, service autonomie (représente la directrice enfance-famille-autonomie)\n- Mme Tran, directrice adjointe du centre hospitalier de Pontcarel\n- Mme Haddou, asso Point Écoute Jeunes (invitée pour le pt 3 seulement)\nExcusés : préfecture (délégué politique de la ville) ; Éducation nationale (infirmière conseillère technique, contribution écrite transmise, lue au pt 4)\n\nIntro Desbrosses : CLS signé en mars 2024, on est à mi-parcours. Laborde rappelle que le CLS doit rester « vivant » → possibilité d'avenants.\n\n1. Bilan mi-parcours (Benamar, diapo)\n- 18 fiches-actions : 4 terminées, 11 engagées, 3 non démarrées (dont la fiche « santé des aidants » et la fiche « habitat indigne »).\n- Points forts : ateliers nutrition QPV Les Coudrais (212 participants depuis 2024), permanences CPAM au CCAS.\n- Points faibles : axe santé environnement très en retard, peu de données.\n- Desbrosses veut présenter ce bilan au conseil municipal du 5 novembre → se corrige : conseil municipal du jeudi 12 novembre (le 5 c'est la commission finances). Benamar prépare une note de synthèse pour le CM, à transmettre au cabinet du maire avant le 30 octobre.\n- Laborde : bilan validé par le COPIL, rien à redire. → bilan mi-parcours validé à l'unanimité des membres présents.\n\n2. Accès aux soins\n- Contexte : 2 médecins généralistes du centre-ville partent en retraite fin 2026, ~2 600 patients sans médecin traitant à prévoir (estimation CPAM, Ricard).\n- Dr Lemaire : la CPTS porte un projet de maison de santé pluriprofessionnelle (MSP) libérale, 3 jeunes médecins intéressés mais « rien de signé ».\n- Ogier pousse un centre de santé municipal avec médecins salariés (modèle de la ville voisine). Desbrosses prudent : coût de fonctionnement, déficit possible les premières années.\n- Débat assez tendu entre Lemaire et Ogier (concurrence MSP / centre de santé ?). Laborde : les deux ne s'excluent pas forcément, mais il faut objectiver.\n- DÉCISION : la ville lance une étude d'opportunité comparant les deux scénarios (MSP libérale / centre de santé municipal). Coût estimé 28 000 € TTC.\n- Financement : ARS (Laborde) peut cofinancer à 50 % dans la limite de 15 000 € via le FIR, SOUS RÉSERVE de validation du dossier par le comité FIR (prochain comité en décembre). Le reste à charge ville.\n- Benamar monte le dossier FIR avec l'appui de l'ARS, dépôt avant le vendredi 13 novembre.\n- Choix entre MSP et centre de santé : PAS tranché, attendre l'étude. Desbrosses : « je ne veux pas qu'on écrive qu'on fait un centre de santé ».\n- Mme Tran : l'hôpital pourrait mettre à disposition des consultations avancées de spécialistes (cardio, gynéco) dans la future structure, mais elle doit en parler à sa direction → pas d'engagement aujourd'hui.\n- Ricard : campagne M'T dents (examen bucco-dentaire) dans les écoles élémentaires, la CPAM peut renforcer l'intervention en CP dans les 2 écoles du QPV. Accord de tous. Ricard organise avec les directeurs d'école, interventions au 2e trimestre scolaire (janvier-mars 2027).\n\n[11h : Dr Lemaire quitte la visio]\n\n3. Santé mentale (avec Mme Haddou)\n- Haddou : hausse forte des demandes des 15-25 ans au Point Écoute (+35 % en un an), délais CMP de 4 à 6 mois pour un premier RDV.\n- Tran confirme les délais CMP, problème de recrutement de psychologues et pédopsychiatre.\n- Proposition Benamar : former des agents municipaux et associatifs aux Premiers secours en santé mentale (PSSM).\n- DÉCISION : 2 sessions PSSM au 1er semestre 2027, 12 stagiaires par session (24 personnes : agents d'accueil ville et CCAS, animateurs jeunesse, bénévoles assos). Financement ARS 6 000 € déjà prévu dans la fiche-action 7 (pas de nouveau financement à demander).\n- Benamar sollicite des organismes de formation agréés et propose des dates au prochain COPIL.\n- Haddou propose de créer un conseil local de santé mentale (CLSM). Laborde intéressée, Desbrosses : « pourquoi pas mais pas maintenant, on a déjà beaucoup de chantiers ». → NON décidé, à remettre à l'ordre du jour du prochain COPIL.\n- Haddou demande aussi une subvention complémentaire de la ville pour le Point Écoute (+ 5 000 €). Desbrosses : relève du budget primitif 2027 et de la commission des subventions, pas du COPIL. Rien décidé.\n- Mme Haddou quitte la réunion à 11h30.\n\n4. Prévention / nutrition / santé environnement\n- Ateliers nutrition QPV Les Coudrais : DÉCISION de les reconduire en 2027, même format (1 atelier par mois). Financement CPAM (Ricard) confirmé pour 2027, 4 500 €.\n- Contribution écrite Éducation nationale (lue par Benamar) : souhaite associer les infirmières scolaires aux ateliers nutrition pour les familles. → Benamar prend contact avec l'infirmière conseillère technique, pas de date.\n- Santé environnement : moustique tigre détecté cet été dans 2 quartiers (signalements). DÉCISION : campagne d'information des habitants au printemps 2027 (flyers + réunion de quartier). Ogier pilote avec le service communication, plan de campagne présenté au COPIL de mars.\n- Qualité de l'air intérieur dans les écoles : Ogier rappelle obligation de surveillance, pas de point fait depuis 2023. Ogier demande un état des lieux aux services techniques, sans date.\n- Idée de parcours sport-santé dans le parc de la Moinerie (Vasseur) : évoquée, pas de suite pour l'instant.\n\n5. Avenant au CLS — santé des aînés\n- Vasseur (département) propose une nouvelle fiche-action « prévention des chutes et isolement des personnes âgées », avec la conférence des financeurs.\n- Laborde : OK sur le principe d'un avenant, mais le texte doit être validé en COPIL puis signé par tous les signataires.\n- DÉCISION : accord de principe pour préparer un avenant n°1 intégrant cette fiche ; adoption formelle au prochain COPIL.\n- Rédaction de la fiche : Vasseur et Benamar, projet à envoyer aux membres avant le vendredi 15 janvier 2027.\n- Ricard (CPAM) signale que la CPAM devra faire valider sa signature par son conseil → délai à prévoir, pas de date de signature.\n\nDivers\n- Prochain COPIL : mars 2027, date fixée par sondage (Benamar envoie le sondage).\n- Compte rendu diffusé à tous par Benamar sous 15 jours.\nFin 12h15."
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "M. Desbrosses (maire de Pontcarel, coprésident)",
    "Mme Laborde (délégation départementale de l'ARS, coprésidente)",
    "M. Ogier (conseiller municipal délégué à la santé)",
    "Mme Benamar (coordinatrice du CLS, prise de notes)",
    "Dr Lemaire (président de la CPTS du Haut-Pontcarel), en visio, parti à 11 h",
    "Mme Ricard (CPAM, chargée de mission prévention)",
    "M. Vasseur (département, service autonomie)",
    "Mme Tran (directrice adjointe du centre hospitalier de Pontcarel)",
    "Mme Haddou (association Point Écoute Jeunes), invitée pour le point 3 seulement, partie à 11 h 30",
    "Excusés : préfecture (délégué politique de la ville) ; Éducation nationale (infirmière conseillère technique, contribution écrite)"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Bilan à mi-parcours du CLS 2024-2028 validé à l'unanimité des membres présents"
    },
    {
      "ref": "D2",
      "texte": "Lancement par la ville d'une étude d'opportunité comparant une MSP libérale et un centre de santé municipal (coût estimé 28 000 € TTC), avec un cofinancement ARS de 50 % dans la limite de 15 000 € sous réserve de validation par le comité FIR"
    },
    {
      "ref": "D3",
      "texte": "Organisation de 2 sessions de formation aux Premiers secours en santé mentale au 1er semestre 2027 (24 personnes, 12 par session), financées par l'ARS à hauteur de 6 000 € déjà prévus dans la fiche-action 7"
    },
    {
      "ref": "D4",
      "texte": "Reconduction en 2027 des ateliers nutrition du QPV Les Coudrais (1 par mois), financés par la CPAM (4 500 €)"
    },
    {
      "ref": "D5",
      "texte": "Campagne d'information des habitants sur le moustique tigre au printemps 2027 (flyers et réunion de quartier)"
    },
    {
      "ref": "D6",
      "texte": "Accord de principe pour préparer un avenant n° 1 au CLS intégrant une fiche-action « prévention des chutes et isolement des personnes âgées » ; adoption formelle au prochain COPIL"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Préparer une note de synthèse du bilan à mi-parcours pour le conseil municipal du 12 novembre et la transmettre au cabinet du maire",
      "responsable": "Mme Benamar",
      "echeance": "avant le 30 octobre 2026"
    },
    {
      "ref": "A2",
      "action": "Monter et déposer le dossier de cofinancement FIR de l'étude d'opportunité",
      "responsable": "Mme Benamar (avec l'appui de l'ARS)",
      "echeance": "avant le vendredi 13 novembre 2026"
    },
    {
      "ref": "A3",
      "action": "Organiser avec les directeurs d'école le renforcement de M'T dents en CP dans les 2 écoles du QPV",
      "responsable": "Mme Ricard",
      "echeance": "interventions au 2e trimestre scolaire (janvier-mars 2027)"
    },
    {
      "ref": "A4",
      "action": "Solliciter des organismes de formation agréés PSSM et proposer des dates",
      "responsable": "Mme Benamar",
      "echeance": "prochain COPIL (mars 2027)"
    },
    {
      "ref": "A5",
      "action": "Prendre contact avec l'infirmière conseillère technique pour associer les infirmières scolaires aux ateliers nutrition",
      "responsable": "Mme Benamar",
      "echeance": "non fixée"
    },
    {
      "ref": "A6",
      "action": "Piloter la campagne moustique tigre et présenter le plan de campagne",
      "responsable": "M. Ogier (avec le service communication)",
      "echeance": "COPIL de mars 2027"
    },
    {
      "ref": "A7",
      "action": "Demander aux services techniques un état des lieux de la surveillance de la qualité de l'air intérieur dans les écoles",
      "responsable": "M. Ogier",
      "echeance": "non fixée"
    },
    {
      "ref": "A8",
      "action": "Rédiger la fiche-action de l'avenant n° 1 et l'envoyer aux membres",
      "responsable": "M. Vasseur et Mme Benamar",
      "echeance": "avant le vendredi 15 janvier 2027"
    },
    {
      "ref": "A9",
      "action": "Envoyer le sondage pour fixer la date du prochain COPIL",
      "responsable": "Mme Benamar",
      "echeance": "non précisée (COPIL en mars 2027)"
    },
    {
      "ref": "A10",
      "action": "Diffuser le compte rendu à tous les membres",
      "responsable": "Mme Benamar",
      "echeance": "sous 15 jours"
    }
  ],
  "pieges": [
    "Choix entre MSP et centre de santé municipal : NON tranché, attendre l'étude (le maire refuse qu'on écrive qu'on fait un centre de santé)",
    "Cofinancement ARS de l'étude : sous réserve du comité FIR de décembre, NON acquis",
    "Consultations avancées de spécialistes de l'hôpital : aucun engagement (Mme Tran doit en parler à sa direction)",
    "Conseil local de santé mentale : proposé, NON décidé, à remettre à l'ordre du jour du prochain COPIL",
    "Subvention complémentaire de 5 000 € au Point Écoute : relève du budget primitif 2027, rien décidé",
    "Parcours sport-santé au parc de la Moinerie : évoqué, sans suite",
    "Présentation du bilan au conseil municipal du jeudi 12 novembre et non du 5 novembre",
    "L'avenant n'est PAS adopté : seulement un accord de principe ; pas de date de signature (validation CPAM nécessaire)",
    "Dr Lemaire est parti à 11 h (absent des points 3 à 5) ; Mme Haddou n'était présente que pour le point 3",
    "Sessions PSSM : aucune date fixée"
  ]
}
```

### Sortie (statut ok)

```text
Subject: Steering Committee Meeting Report

Participants:
- Mr. Desbrosses, Mayor of Pontcarel (co-chairman)
- Ms. Laborde, Delegation of the ARS (co-chairman)
- Mr. Ogier, Municipal Delegate to Health
- Ms. Benamar, CLS Coordinator (city)
- Dr. Lemaire, President of the CPTS of Haut-Pontcarel (unpresented)
- Ms. Ricard, CPAM, Mission Preventive Charge
- Mr. Vasseur, Department, Service Autonomy
- Ms. Tran, Deputy Director of the Pontcarel Hospital Center
- Ms. Haddou, Point Écoute Jeunes (invited for item 3 only)

Points Discussed:
1. Mid-term Progress (Benamar, slide)
- 18 action items: 4 completed, 11 in progress, 3 not started (including the "health of caregivers" and "inadequate housing" action items).
- Strengths: Nutrition workshops QPV Les Coudrais (212 participants since 2024), CPAM presence at the CCAS.
- Weaknesses: Very slow progress on the health-environment axis, little data.
- Desbrosses wants to present this mid-term progress to the municipal council on November 5th -> corrected: council meeting on November 12th (the November 5th is the finance committee).
- Benamar prepared a summary note for the council, to be sent to the mayor's office before October 30th.
- Laborde: the mid-term progress is validated unanimously by the members present.

2. Access to Care
- Context: 2 general practitioners from the city center are retiring at the end of 2026, ~2,600 patients without a treating physician (CPAM estimate).
- Dr. Lemaire: the CPTS is working on a free-standing health center model, 3 young doctors interested but "nothing signed".
- Ogier pushes for a municipal health center with salaried doctors (model from the neighboring town). Desbrosses is cautious: operating costs, possible deficits in the first years.
- Debate between Lemaire and Ogier on the compatibility of the free-standing health center and the municipal health center.
- DECISION: the city launches a feasibility study comparing the two scenarios (free-standing health center / municipal health center). Estimated cost: €28,000.
- Financing: ARS (Laborde) can cofinance up to 50% (up to €15,000) via the FIR, subject to validation of the FIR committee (next committee in December). The rest is at the city's expense.
- Benamar prepares the FIR dossier with the support of the ARS, to be deposited before November 13th.
- Choice between the free-standing health center and the municipal health center: not decided, to be awaited the results of the study. Desbrosses: "I don't want to write that we are doing a health center".
- Tran: the hospital could make available advanced consultations (cardiovascular, gynecological) in the future structure, but she must discuss this with her management -> not committed today.
- Ricard: dental campaign (examination of oral health) in elementary schools, the CPAM can strengthen the intervention in the two QPV schools. Agreement of all. Ricard organizes with the school directors, interventions in the second semester of the school year (January-March 2027).

[11h: Ms. Haddou leaves]

3. Mental Health (with Ms. Haddou)
- Ms. Haddou: a significant increase in requests from young people aged 15-25, a rise in CM requests from 4 to 6 months.
- Tran confirms the CM deadlines, but there is a shortage of psychologists and child psychiatrists.
- Proposal Benamar: train municipal officials and community volunteers in mental health first aid (PSSM).
- DECISION: 2 PSSM sessions in the first semester of 2027, 12 participants per session (city officials, youth organizers, volunteers). Funding from ARS (already allocated in action 7) is confirmed for 2027, no additional funding required.
- Benamar seeks approval from recognized training centers and proposes dates to the next COPIL.
- Haddou proposes also a supplementary grant from the city for the Point Écoute (+5,000 €). Desbrosses: linked to the original budget for 2027 and the committee on subsidies, not COPIL. Not decided.
- Ms. Haddou leaves the meeting at 11:30.

4. Prevention / Nutrition / Environmental Health
- Nutrition workshops QPV Les Coudrais: DECISION to continue in 2027, even format (one workshop per month). Funding from CPAM (Ricard) confirmed for 2027, 4,500 €.
- Written contribution from Education: wishes to involve school

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Présent : « the mid-term progress is validated unanimously by the members present ».
  - D2 : 1 — Étude comparative, coût de 28 000 € et cofinancement ARS de 50 % plafonné à 15 000 € sous réserve du comité FIR : tout est présent.
  - D3 : 1 — Deux sessions PSSM au 1er semestre 2027, 12 participants par session, financement ARS fiche-action 7 ; le montant de 6 000 € est toutefois omis.
  - D4 : 1 — Reconduction 2027, un atelier par mois, financement CPAM de 4 500 € : présent.
  - D5 : 0 — Absente : la sortie est tronquée au point 4, avant la campagne moustique tigre.
  - D6 : 0 — Absente : le point 5 sur l'avenant n'est pas traité, la sortie étant tronquée.
  - A1 : 1 — Benamar, note de synthèse transmise au cabinet avant le 30 octobre : présent, bien que formulé au passé (« prepared »).
  - A2 : 1 — Benamar, dossier FIR avec l'appui de l'ARS, dépôt avant le 13 novembre : présent.
  - A3 : 1 — Ricard organise avec les directeurs d'école, janvier-mars 2027 : présent, mais « second semester » est erroné et la précision CP est absente.
  - A4 : 1 — Benamar sollicite des organismes de formation et propose des dates au prochain COPIL : présent.
  - A5 : 0 — Tronquée : la phrase « wishes to involve school » s'interrompt avant l'action.
  - A6 : 0 — Absente : la sortie est tronquée.
  - A7 : 0 — Absente : la sortie est tronquée.
  - A8 : 0 — Absente : la sortie est tronquée.
  - A9 : 0 — Absente : la sortie est tronquée.
  - A10 : 0 — Absente : la sortie est tronquée.
- `absence_invention` : 0 — La mention « [11h: Ms. Haddou leaves] » attribue à Mme Haddou le départ à 11 h de Dr Lemaire ; le financement PSSM est en outre présenté comme « confirmed for 2027 », ce que les notes ne disent pas.
- `structure` : 0 — Seules les sections Participants et Points abordés sont présentes ; il n'y a pas de sections Décisions ni Actions distinctes, et la sortie est tronquée.
- Inventions : [11h: Ms. Haddou leaves] : c'est Dr Lemaire qui quitte à 11 h; Dr Lemaire « (unpresented) » : il était présent en visio; Financement PSSM « confirmed for 2027 » : formulation non présente dans les notes; « a rise in CM requests from 4 to 6 months » : déformation des délais CMP
- Confiance : haute

## CT-010 (CT, moyen)

### Entrée

```text
{
  "consigne": "Rédige la convocation des conseillers municipaux à cette séance, en respectant l'article L. 2121-11 du code général des collectivités territoriales fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Nom de la commune], [Nom du maire].",
  "elements_connus": {
    "auteur": "le maire",
    "date_envoi": "lundi 16 novembre 2026",
    "date_seance": "mercredi 18 novembre 2026",
    "heure": "18 h 30",
    "lieu": "salle du conseil municipal, mairie",
    "motif_urgence": "la demande d'aide exceptionnelle de l'État pour la réparation de la toiture de l'école, endommagée par la tempête du 12 novembre, doit être déposée avant le 20 novembre 2026",
    "ordre_du_jour": [
      "demande d'aide exceptionnelle de l'État pour la réparation de la toiture de l'école",
      "travaux de mise hors d'eau de l'école : approbation du devis"
    ],
    "taille_de_la_commune": "commune de 1 200 habitants"
  },
  "objet": "Convocation en urgence du conseil municipal",
  "type": "convocation"
}

Options de la demande :
{
  "parametres": {},
  "type_courrier": "convocation"
}
```

### Références (vues par le Juge)

```text
{
  "type_courrier": "convocation",
  "elements_obligatoires": [
    "En-tête de la mairie",
    "Destinataires : mesdames et messieurs les conseillers municipaux",
    "Date d'envoi : lundi 16 novembre 2026",
    "Objet : convocation du conseil municipal en urgence",
    "Convocation faite par le maire",
    "Date, heure et lieu de la séance : mercredi 18 novembre 2026, 18 h 30, salle du conseil municipal de la mairie",
    "Ordre du jour : les 2 points, exactement",
    "Mention de l'urgence et de son motif (dépôt de la demande d'aide avant le 20 novembre 2026), justifiant un délai de convocation abrégé (au moins un jour franc)",
    "Mention que le maire en rendra compte dès l'ouverture de la séance et que le conseil municipal se prononcera sur l'urgence, avec la possibilité de renvoyer la discussion à une séance ultérieure",
    "Formule de politesse",
    "Signature du maire (nom en emplacement)"
  ],
  "champs_a_laisser_en_emplacement": [
    "[Nom de la commune]",
    "[Nom du maire]"
  ],
  "valeurs_interdites": [
    "toute note explicative de synthèse ou pièce jointe annoncée sans être fournie",
    "montant de l'aide, du devis ou des travaux inventé",
    "tout point ajouté à l'ordre du jour",
    "délai de convocation de trois jours francs présenté comme respecté (il est abrégé pour urgence)"
  ]
}
```

### Sortie (statut ok)

```text
[Ville], [Nom du maire].

Objet : Convocation en urgence du conseil municipal

Chers conseillers municipaux,

Le maire de [ville] vous invite à se réunir en session d'urgence le mercredi 18 novembre 2026, à 18 h 30, dans la salle du conseil municipal située à l'intérieur de la mairie.

La raison de cette convocation est la nécessité de discuter et de décider de la demande d'aide exceptionnelle de l'État pour la réparation de la toiture de l'école, endommagée par la tempête du 12 novembre. Cette demande doit être déposée avant le 20 novembre 2026.

L'ordre du jour de la session est le suivant :
1. Demandes d'aide exceptionnelle de l'État
2. Approbation du devis pour les travaux de mise hors d'eau de l'école

Veuillez se présenter à la salle du conseil municipal pour participer à cette session d'urgence.

Veuillez agréer, en tout cas, l'expression de nos salutations distinguées.

[Signature]

Le maire de [ville]

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Nom de la commune]": false,
    "[Nom du maire]": true
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : la date d'envoi (« lundi 16 novembre 2026 » absente), la mention que le maire rendra compte de l'urgence dès l'ouverture de la séance et que le conseil se prononcera sur l'urgence avec possibilité de renvoi, l'en-tête de mairie conforme (« [Ville] » au lieu de [Nom de la commune]), le destinataire formel et le nom du maire dans la signature (« [Signature] » / « Le maire de [ville] »). Le registre est en outre fautif (« vous invite à se réunir », « Veuillez se présenter », « Veuillez agréer, en tout cas »), et le premier point de l'ordre du jour est altéré (« Demandes d'aide exceptionnelle de l'État »).
- Inventions : Libellé d'emplacement non demandé « [Ville] » / « [ville] » à la place de [Nom de la commune]; Emplacement « [Signature] » non prévu
- Confiance : haute

## CT-011 (CT, difficile)

### Entrée

```text
{
  "consigne": "Rédige la convocation des conseillers municipaux, conformément à l'article L. 2121-12 du code général des collectivités territoriales fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Nom de la commune], [Nom du maire], [Modalités de consultation fixées par le règlement intérieur].",
  "elements_connus": {
    "date_envoi": "mercredi 18 novembre 2026",
    "date_seance": "mardi 24 novembre 2026",
    "heure": "19 h 00",
    "lieu": "salle du conseil municipal, hôtel de ville",
    "ordre_du_jour": [
      "approbation du procès-verbal de la séance du 13 octobre 2026",
      "attribution de la délégation de service public pour l'exploitation de la piscine municipale",
      "garantie d'emprunt accordée à un bailleur social",
      "créations et suppressions de postes au tableau des effectifs"
    ],
    "piece_jointe": "note explicative de synthèse sur les affaires soumises à délibération",
    "taille_de_la_commune": "commune de 8 400 habitants"
  },
  "objet": "Convocation à la séance du conseil municipal du mardi 24 novembre 2026",
  "type": "convocation"
}

Options de la demande :
{
  "parametres": {},
  "type_courrier": "convocation"
}
```

### Références (vues par le Juge)

```text
{
  "type_courrier": "convocation",
  "elements_obligatoires": [
    "En-tête de la mairie",
    "Destinataires : mesdames et messieurs les conseillers municipaux",
    "Date d'envoi : mercredi 18 novembre 2026",
    "Objet : convocation à la séance du conseil municipal du mardi 24 novembre 2026",
    "Date, heure et lieu : mardi 24 novembre 2026, 19 h 00, salle du conseil municipal de l'hôtel de ville",
    "Ordre du jour : les 4 points, exactement",
    "Note explicative de synthèse sur les affaires soumises à délibération, jointe à la convocation",
    "Mention que le projet de contrat de délégation de service public, accompagné de l'ensemble des pièces, peut être consulté à la mairie par tout conseiller, à sa demande, dans les conditions fixées par le règlement intérieur",
    "Formule de politesse",
    "Signature du maire (nom en emplacement)"
  ],
  "champs_a_laisser_en_emplacement": [
    "[Nom de la commune]",
    "[Nom du maire]",
    "[Modalités de consultation fixées par le règlement intérieur]"
  ],
  "valeurs_interdites": [
    "mention d'une urgence ou d'un délai abrégé (le délai de cinq jours francs est respecté)",
    "contenu de la note explicative de synthèse inventé (montants, nom du délégataire ou du bailleur)",
    "tout point ajouté à l'ordre du jour",
    "nom du maire inventé"
  ]
}
```

### Sortie (statut ok)

```text
Cher [Nom du conseiller municipal],

Vous êtes parmi nous pour la séance du conseil municipal du mardi 24 novembre 2026. Votre présence est nécessaire pour l'examen des points suivants inscrits sur l'ordre du jour : approbation du procès-verbal de la séance du 13 octobre 2026, attribution de la délégation de service public pour l'exploitation de la piscine municipale, garantie d'emprunt accordée à un bailleur social, créations et suppressions de postes au tableau des effectifs.

Veuillez vous présenter au comptoir de réception pour obtenir votre convocation. Votre participation est importante pour la bonne marche de notre commune.

N'hésitez pas à nous contacter si vous avez des questions ou des préoccupations.

Cordialement,

[Signature]
[Nom du maire]

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Modalités de consultation fixées par le règlement intérieur]": false,
    "[Nom de la commune]": false,
    "[Nom du maire]": true
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : l'en-tête de la mairie ([Nom de la commune] absent), le destinataire collectif, la date d'envoi, l'objet, l'heure et le lieu, la note explicative de synthèse jointe et la mention de consultation du projet de contrat de DSP. Le registre est inadapté (« Vous êtes parmi nous… », « Veuillez vous présenter au comptoir de réception pour obtenir votre convocation », « Cordialement »).
- Inventions : Emplacement non demandé « [Nom du conseiller municipal] » à la place des destinataires collectifs; « Veuillez vous présenter au comptoir de réception pour obtenir votre convocation » : modalité absente de l'entrée et contradictoire avec la nature du document; Emplacement non demandé « [Signature] »
- Confiance : haute

## CT-014 (CT, facile)

### Entrée

```text
{
  "consigne": "Rédige une réponse d'information en t'appuyant uniquement sur l'extrait de la fiche service-public.fr fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de l'association], [Commune], [Date du courrier], [Nom et qualité du signataire].",
  "elements_connus": {
    "destinataire": "Club de randonnée « Les Sentiers de la vallée », représenté par son trésorier, M. Bernard Lefèvre",
    "question_posee": "l'association, propriétaire d'un local de réunion acheté en 2025, demande si elle doit payer la taxe foncière",
    "service": "Espace France services de la commune"
  },
  "objet": "Taxe foncière d'une association propriétaire",
  "type": "réponse d'information"
}

Options de la demande :
{
  "parametres": {},
  "type_courrier": "réponse d'information"
}
```

### Références (vues par le Juge)

```text
{
  "type_courrier": "réponse d'information",
  "elements_obligatoires": [
    "En-tête de l'expéditeur (espace France services)",
    "Bloc destinataire (club Les Sentiers de la vallée, à l'attention de M. Bernard Lefèvre)",
    "Lieu et date",
    "Objet",
    "Formule d'appel « Monsieur, »",
    "Principe : une association propriétaire de biens immobiliers situés en France doit payer la taxe foncière sur les propriétés bâties et non bâties",
    "Exonérations limitées à certains organismes et biens (édifices du culte, bâtiments d'associations de mutilés affectés à l'hospitalisation, hangars d'associations de sauveteurs, bâtiments ruraux agricoles), sans en ajouter",
    "Si un avis de taxe est reçu alors qu'une exonération s'applique, envoi des justificatifs aux impôts",
    "Formule de politesse",
    "Signature : nom et qualité du signataire (en emplacement)"
  ],
  "champs_a_laisser_en_emplacement": [
    "[Adresse de l'association]",
    "[Commune]",
    "[Date du courrier]",
    "[Nom et qualité du signataire]"
  ],
  "valeurs_interdites": [
    "montant de taxe foncière inventé",
    "exonération inventée pour les associations de loisirs ou les locaux de réunion",
    "taux d'imposition ou délai inventés",
    "toute adresse, tout numéro de téléphone ou courriel inventé"
  ]
}
```

### Sortie (statut ok)

```text
[Adresse de l'association]  
[Commune]  

[Date du courrier]  

Monsieur [Nom et qualité du signataire]  

Objet : Taxe foncière d'une association propriétaire  

Cher M. Bernard Lefèvre,  

l'Association Club de randonnée « Les Sentiers de la vallée », propriétaire d'un local de réunion situé à [Adresse du local], demande une réponse concernant le paiement de la taxe foncière applicable à ce local.  

La taxe foncière est due annuellement et est calculée en fonction de la superficie du local et des loyers imposés. L'Association a acheté le local en [Date d'achat] et estime que la taxe doit être acquittée pour l'année [Année].  

Pourriez-vous s'il vous plaît fournir les informations nécessaires pour calculer la taxe foncière applicable à ce local, ainsi que les modalités de paiement et les délais de versement?  

Nous vous remercions de votre attention à ce sujet et nous vous attendons à une réponse dans les meilleurs délais.  

Cordialement,  

[Signature]  

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Adresse de l'association]": true,
    "[Commune]": true,
    "[Date du courrier]": true,
    "[Nom et qualité du signataire]": true
  },
  "emplacements_reussis": true
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : pas d'en-tête de l'espace France services, pas de bloc destinataire correct (« Monsieur [Nom et qualité du signataire] » confond signataire et destinataire), formule d'appel « Cher M. Bernard Lefèvre, » au lieu de « Monsieur, », absence du principe d'assujettissement des associations propriétaires, des exonérations et de l'envoi de justificatifs ; le courrier inverse en outre les rôles en demandant des informations au lieu d'en fournir, avec un registre inadapté (« Cordialement », « nous vous attendons à une réponse »).
- Inventions : « La taxe foncière est due annuellement et est calculée en fonction de la superficie du local et des loyers imposés » : modalité de calcul absente de l'extrait fourni; Emplacements non prévus et inventés : [Adresse du local], [Date d'achat], [Année], [Signature]; « l'Association ... estime que la taxe doit être acquittée pour l'année [Année] » : position attribuée à l'association, non fournie dans l'entrée
- Confiance : haute

## LC-006 (LC, facile)

### Entrée

```text
{
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "nb_mots": 158,
  "texte": "Oui, une mairie peut être le siège social d’une association. En général, les associations qui choisissent d'avoir leur siège social à la mairie sont celles qui ont des activités locales ou qui collaborent avec les autorités locales (commune, ville,...). L'association doit faire la demande à la mairie par courrier. Si le maire le décide, des locaux communaux peuvent être mis à disposition et utilisés par les associations qui en font la demande. Le maire fixe les conditions dans lesquelles ces locaux peuvent être utilisés. Par exemple : mise à disposition un jour par semaine, conditions d'accès, horaires, répartition des bureaux entre plusieurs associations. La mise à disposition du local peut être gratuite ou payante. Le montant du loyer ou de la participation est fixée par le conseil municipal. (À savoir: Le siège social d'une association peut également se situer au domicile d'un de ses membres , dans des locaux institutionnels (école, bibliothèque,...) mais encore dans un bureau commercial ou privé.)"
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "Une mairie peut être le siège social d'une association",
    "Ce sont en général des associations aux activités locales ou qui collaborent avec les autorités locales",
    "L'association doit faire la demande à la mairie par courrier",
    "Si le maire le décide, des locaux communaux peuvent être mis à disposition ; le maire fixe les conditions d'utilisation (jour, accès, horaires, répartition des bureaux)",
    "La mise à disposition peut être gratuite ou payante ; le montant du loyer ou de la participation est fixé par le conseil municipal",
    "Le siège social peut aussi être au domicile d'un membre, dans des locaux institutionnels (école, bibliothèque) ou dans un bureau commercial ou privé"
  ],
  "termes_juridiques_a_conserver": [
    "siège social",
    "association",
    "mise à disposition",
    "locaux communaux",
    "conseil municipal"
  ]
}
```

### Sortie (statut ok)

```text
Vous pouvez choisir de faire de la mairie votre siège social pour votre association. Cela est courant pour les groupes qui travaillent avec la communauté locale ou collaborent avec les autorités locales. Pour cela, vous devez envoyer un courrier à la mairie. Si le maire décide de vous accorder des locaux, ils peuvent être mis à votre disposition. Le maire fixe les conditions, comme le jour de la semaine où vous pouvez y accéder, les conditions d'accès, les horaires, et la répartition des bureaux entre différentes associations. Vous pouvez utiliser ces locaux gratuitement ou payer un loyer. Le montant du loyer ou de la participation est déterminé par le conseil municipal. En cas de besoin, vous pouvez également utiliser les locaux d'un membre de votre association, des établissements institutionnels comme des bibliothèques ou des écoles, ou des bureaux commerciaux privés.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": -1.5168,
  "km_entree": 62.48,
  "km_sortie": 60.9632
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations sont modifiées. La dernière phrase (« vous pouvez également utiliser les locaux d'un membre… ou des bureaux commerciaux privés ») ne parle plus de lieux possibles pour le siège social. Elle remplace le « domicile » par des « locaux » et fusionne « commercial ou privé » en « commerciaux privés ». De plus, « Vous pouvez utiliser ces locaux gratuitement ou payer un loyer » présente comme un choix de l'usager une modalité qui ne dépend pas de lui.
- `termes_juridiques` : 0 — Le terme « locaux communaux » a disparu : seuls « locaux » et « des locaux » subsistent, sans précision qu'il s'agit de locaux de la commune. Les autres termes (siège social, association, mise à disposition, conseil municipal) sont conservés.
- `clarte_percue` : 4 — Le texte est direct, s'adresse à l'usager et se comprend facilement, mais certaines formulations ambiguës (« en cas de besoin », « utiliser les locaux d'un membre ») brouillent le lien avec le siège social.
- Inventions : « En cas de besoin » : condition absente du texte source; « Vous pouvez utiliser ces locaux gratuitement ou payer un loyer » : présenté comme un choix de l'usager, ce que le texte source ne dit pas; « utiliser les locaux d'un membre » : le texte source parle du domicile d'un membre comme siège social; « bureaux commerciaux privés » : le texte source dit « bureau commercial ou privé »
- Confiance : haute

## LC-007 (LC, facile)

### Entrée

```text
{
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "nb_mots": 148,
  "texte": "Non, en principe, les prestations familiales sont insaisissables. Mais certaines prestations familiales peuvent être saisies en cas de non-paiement de dette alimentaire (par exemple, pension alimentaire, frais de cantine scolaire). Elles peuvent également être saisies en cas de non-paiement d'autres dépenses liées aux autres besoins de l'enfant (par exemple, frais d'hospitalisation). Il s'agit des prestations suivantes :\n- Allocation de base et prestation partagée d'éducation de l'enfant\n- Allocations familiales\n- Complément familial\n- Allocation de rentrée scolaire (ARS)\n- Allocation de soutien familial (ASF)\n- Allocation d'éducation de l'enfant handicapé (AEEH)\nLes sommes sont saisies dans la limite d'un montant mensuel fixé selon les revenus et les charges de la famille. (À savoir: Si une personne obtient une prestation familiale après avoir fraudé ou fait une fausse déclaration, la Caf (ou la MSA ) récupère cet indu . La Caf (ou MSA ) peut notamment faire une retenue sur les versements à venir d'une autre prestation familiale.)"
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "En principe, les prestations familiales sont insaisissables",
    "Certaines peuvent être saisies en cas de non-paiement d'une dette alimentaire (pension alimentaire, frais de cantine scolaire) ou d'autres dépenses liées aux besoins de l'enfant (frais d'hospitalisation)",
    "Prestations concernées : allocation de base et prestation partagée d'éducation de l'enfant, allocations familiales, complément familial, ARS, ASF, AEEH",
    "La saisie est limitée à un montant mensuel fixé selon les revenus et les charges de la famille",
    "En cas de fraude ou de fausse déclaration, la Caf (ou la MSA) récupère l'indu, notamment par retenue sur une autre prestation familiale"
  ],
  "termes_juridiques_a_conserver": [
    "prestations familiales",
    "insaisissables",
    "saisie",
    "dette alimentaire",
    "pension alimentaire",
    "indu",
    "retenue"
  ]
}
```

### Sortie (statut ok)

```text
Vous n'avez pas droit à saisir les prestations familiales en général. Cependant, dans certains cas, telles que le non-paiement de la dette alimentaire ou d'autres dépenses liées à l'enfant, vous pouvez être en mesure de saisir certaines prestations familiales. Voici les prestations familiales qui peuvent être saisies :

- Allocation de base et prestation partagée d'éducation de l'enfant
- Allocations familiales
- Complément familial
- Allocation de rentrée scolaire (ARS)
- Allocation de soutien familial (ASF)
- Allocation d'éducation de l'enfant handicapé (AEEH)

Les sommes sont saisies dans la limite d'un montant mensuel fixé selon les revenus et les charges de la famille. Si une personne obtient une prestation familiale après avoir fraudé ou fait une fausse déclaration, la Caf (ou la MSA ) peut récupérer cette prestation en faisant une retenue sur les versements à venir d'une autre prestation familiale.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 0.0755,
  "km_entree": 60.18,
  "km_sortie": 60.2555
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le sens est déformé : « Vous n'avez pas droit à saisir les prestations familiales » fait de l'usager le créancier. Les exemples (pension alimentaire, frais de cantine scolaire, frais d'hospitalisation) sont supprimés. « récupère cet indu » devient « peut récupérer cette prestation », et le « notamment » disparaît, ce qui fait de la retenue le seul moyen de récupération.
- `termes_juridiques` : 0 — Les termes « insaisissables », « pension alimentaire » et « indu » sont absents. « indu » est remplacé à tort par « cette prestation ».
- `clarte_percue` : 2 — L'adresse « vous pouvez être en mesure de saisir » est confuse : l'usager ne sait plus qui saisit ni ce qui est protégé. Elle s'ajoute à des tournures maladroites comme « telles que le non-paiement ».
- Inventions : Présentation de l'usager comme celui qui saisit les prestations (« Vous n'avez pas droit à saisir », « vous pouvez être en mesure de saisir »), absente de l'entrée.; La Caf « peut récupérer cette prestation » au lieu de récupérer l'indu : objet et caractère de la récupération modifiés.
- Confiance : haute

## LC-011 (LC, moyen)

### Entrée

```text
{
  "consigne": "Réécris ce texte en langage clair pour qu'un agent d'accueil puisse l'expliquer à un usager, sans perdre d'information.",
  "nb_mots": 377,
  "texte": "Aide sociale à l'hébergement (ASH) d'une personne âgée\nPour obtenir l'ASH, la personne âgée doit remplir toutes les conditions suivantes :\n- Elle doit avoir plus de 65 ans (ou plus de 60 ans si elle a été reconnue inapte au travail)\n- Elle doit vivre en France de façon stable et régulière. Si elle est de nationalité étrangère, elle doit en plus avoir un titre de séjour en cours de validité.\n- Elle doit être hébergée dans un établissement ( Éhpad ou résidence autonomie ou USLD ) qui a des places réservées aux bénéficiaires de l'aide sociale\n- Ses revenus doivent être inférieurs aux frais d'hébergement facturés par l'établissement.\nPour que la prise en charge des frais d'hébergement débute à partir de la date d'entrée dans l'établissement, la demande d'ASH doit être faite dans les 2 mois qui suivent cette date. Il est donc recommandé de faire la demande d'ASH en même temps que les démarches d'admission en établissement.\nL'ASH est versée par le département. Chaque département a son propre règlement d'aide sociale. Les règles de versement varient donc d'un département à l'autre. Le département peut fixer le montant de l'ASH en tenant compte des revenus des personnes suivantes :\n- Revenus de la personne âgée (sauf l'allocation de reconnaissance du combattant et les pensions attachées aux distinctions honorifiques, comme la Légion d'honneur par exemple)\n- Revenus de son époux ou épouse, de son partenaire de Pacs ou de son concubin ou concubine\n- Revenus de ses obligés alimentaires , qui peuvent être ses enfants, gendres, belles-filles.\n(À noter: Le petit-enfant est dispensé de l'obligation alimentaire en cas de demande d'ASH pour le compte de l'un de ses grands-parents. Cette dispense s'étend aux descendants de ce petit-enfant.)\nL’ASH versé peut prendre charge une partie ou la totalité des frais d’hébergement facturés à la personne âgée. L’ASH peut aussi financer le tarif dépendance pour la personne âgée hébergée en Ehpad ou en USLD. En général, le montant de l'ASH permet de laisser à la personne âgée au minimum 10 % de ses revenus par mois, et en aucun cas moins de 125 € par mois. Lorsque son époux ou épouse, partenaire de Pacs ou concubin ou concubine est resté vivre à domicile, le montant de l'ASH permet de laisser à la disposition de cette personne au minimum 1 043,59 € par mois."
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "Conditions cumulatives de l'ASH : plus de 65 ans (ou plus de 60 ans si reconnue inapte au travail)",
    "Vivre en France de façon stable et régulière ; pour une personne étrangère, avoir en plus un titre de séjour en cours de validité",
    "Être hébergée dans un établissement (Ehpad, résidence autonomie ou USLD) ayant des places réservées aux bénéficiaires de l'aide sociale",
    "Avoir des revenus inférieurs aux frais d'hébergement facturés",
    "Demande à faire dans les 2 mois suivant l'entrée en établissement pour une prise en charge dès la date d'entrée",
    "L'ASH est versée par le département ; chaque département a son règlement d'aide sociale",
    "Le montant tient compte des revenus de la personne âgée (sauf allocation de reconnaissance du combattant et pensions liées aux distinctions honorifiques), de son conjoint, partenaire de Pacs ou concubin, et de ses obligés alimentaires",
    "Le petit-enfant (et ses descendants) est dispensé de l'obligation alimentaire",
    "L'ASH peut couvrir tout ou partie des frais d'hébergement et le tarif dépendance en Ehpad ou USLD",
    "Il reste à la personne au minimum 10 % de ses revenus par mois, jamais moins de 125 € par mois",
    "Si le conjoint ou partenaire vit encore à domicile, il lui reste au minimum 1 043,59 € par mois"
  ],
  "termes_juridiques_a_conserver": [
    "aide sociale à l'hébergement (ASH)",
    "obligés alimentaires",
    "obligation alimentaire",
    "règlement d'aide sociale",
    "titre de séjour",
    "tarif dépendance",
    "Ehpad",
    "USLD"
  ]
}
```

### Sortie (statut ok)

```text
Pour recevoir l'aide sociale à l'hébergement (ASH) d'une personne âgée, celle-ci doit répondre à plusieurs conditions. Tout d'abord, elle doit avoir plus de 65 ans (ou plus de 60 ans si elle a été reconnue inapte au travail). Ensuite, elle doit vivre en France de manière stable et régulière. Si elle est de nationalité étrangère, elle doit également avoir un titre de séjour en cours de validité. Enfin, elle doit être hébergée dans un établissement (ÉHPAD ou résidence autonomie ou USLD) qui a des places réservées aux bénéficiaires de l'aide sociale.

Pour que la prise en charge des frais d'hébergement débute à partir de la date d'entrée dans l'établissement, la demande d'ASH doit être faite dans les 2 mois qui suivent cette date. Il est donc recommandé de faire la demande d'ASH en même temps que les démarches d'admission en établissement.

L'ASH est versée par le département. Chaque département a son propre règlement d'aide sociale, donc les règles de versement varient d'un département à l'autre. Le département peut fixer le montant de l'ASH en tenant compte des revenus des personnes suivantes :

- Les revenus de la personne âgée (sauf l'allocation de reconnaissance du combattant et les pensions attachées aux distinctions honorifiques, comme la Légion d'honneur par exemple)
- Les revenus de son époux ou épouse, de son partenaire de PACS ou de son concubin ou concubine
- Les revenus de ses obligés alimentaires, qui peuvent être ses enfants, parents, orphelins.

L'ASH versée peut prendre en charge une partie ou la totalité des frais d'hébergement facturés à la personne âgée. Elle peut également financer le tarif dépendance pour la personne âgée hébergée dans un ÉHPAD ou un USLD. En général, le montant de l'ASH permet de laisser à la personne âgée au moins 10 % de ses revenus par mois, et en aucun cas moins de 125 € par mois. Lorsque son époux ou épouse, partenaire de PACS ou concubin ou concubine est resté vivre à domicile, le montant de l'ASH permet de laisser à disposition cette personne au moins 1 043,59 € par mois.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": -1.3951,
  "km_entree": 69.54,
  "km_sortie": 68.1449
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La condition « revenus inférieurs aux frais d'hébergement » et la dispense d'obligation alimentaire du petit-enfant et de ses descendants sont supprimées, et la liste des obligés alimentaires est modifiée : « enfants, parents, orphelins » remplace « enfants, gendres, belles-filles ».
- `termes_juridiques` : 0 — Le terme « obligation alimentaire » disparaît avec la suppression de la note sur le petit-enfant ; les autres termes (ASH, obligés alimentaires, règlement d'aide sociale, titre de séjour, tarif dépendance, Ehpad, USLD) sont conservés.
- `clarte_percue` : 2 — Le texte reprend presque mot pour mot l'original, sans expliquer les termes techniques (« obligés alimentaires », « USLD », « tarif dépendance »), et un usager sans connaissance administrative ne le comprendrait pas du premier coup.
- Inventions : Les obligés alimentaires « peuvent être ses enfants, parents, orphelins » (l'entrée indique « enfants, gendres, belles-filles »)
- Confiance : haute

## LC-017 (LC, moyen)

### Entrée

```text
{
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "nb_mots": 278,
  "texte": "Oui, vous pouvez, sous certaines conditions, obtenir des aides pour payer la cantine de votre enfant. Les possibilités sont différentes selon le niveau de scolarisation de votre enfant : primaire (maternelle et élémentaire) ou collège ou lycée.\nLes tarifs de la cantine scolaire à l'école primaire sont fixés par la commune. La commune peut choisir d'appliquer le quotient familial au tarif du repas, pour l'adapter à vos revenus et à vos charges. Dans certaines communes, vous pouvez bénéficier d'aides pour payer les frais de cantine. Renseignez-vous auprès de votre mairie. Vous pouvez aussi vous rapprocher de l'assistante sociale scolaire.\nDans certains départements, si votre enfant est scolarisé dans une école élémentaire éloignée de votre domicile et qu'il doit rester à la cantine, vous pouvez bénéficier d'une aide. Renseignez-vous auprès du directeur d'école en début d'année scolaire.\nQu'est-ce que le fonds social pour les cantines au collège et au lycée ?\nLe fonds est une une aide financière du collège ou du lycée que vous pouvez obtenir pour payer la cantine de votre enfant. Vous devez pour cela vous adresser à l' assistante sociale du collège ou du lycée ou au secrétariat de l'établissement scolaire. L'aide est attribuée par le chef d'établissement. Il vous informe en début d'année scolaire des conditions d'attribution de ce fonds social.\nLes tarifs de la cantine scolaire sont déterminés par le département pour les collèges, et la région pour les lycées. Le département ou la région peut choisir d'appliquer le quotient familial au tarif du repas, pour l'adapter à vos revenus et à vos charges. Dans certaines départements ou certaines régions, vous pouvez bénéficier d'aides pour payer les frais de cantine. Renseignez-vous auprès de votre collectivité."
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "Des aides pour la cantine existent sous conditions ; elles dépendent du niveau : primaire ou collège/lycée",
    "Primaire : tarifs fixés par la commune, qui peut appliquer le quotient familial ; certaines communes aident ; se renseigner en mairie ou auprès de l'assistante sociale scolaire",
    "Primaire : dans certains départements, aide si l'enfant est scolarisé dans une école élémentaire éloignée du domicile et doit rester à la cantine ; se renseigner auprès du directeur d'école en début d'année",
    "Collège et lycée : le fonds social pour les cantines est une aide de l'établissement ; s'adresser à l'assistante sociale ou au secrétariat ; l'aide est attribuée par le chef d'établissement, qui informe des conditions en début d'année",
    "Tarifs fixés par le département (collèges) et la région (lycées), qui peuvent appliquer le quotient familial et accorder des aides ; se renseigner auprès de la collectivité"
  ],
  "termes_juridiques_a_conserver": [
    "quotient familial",
    "fonds social pour les cantines",
    "chef d'établissement",
    "assistante sociale scolaire"
  ]
}
```

### Sortie (statut ok)

```text
Vous pouvez obtenir des aides pour payer la cantine de votre enfant, selon son niveau d'études. Pour les enfants d'âge préscolaire, les tarifs sont fixés par la commune, qui peut appliquer le quotient familial pour tenir compte de vos revenus et de vos charges. Certaines communes offrent des aides pour payer les frais de cantine. Vérifiez auprès de votre mairie. Pour les enfants d'âge scolaire, le fonds social pour les cantines est une aide financière du collège ou du lycée que vous pouvez obtenir pour payer la cantine de votre enfant. Vous devez vous adresser à l'assistance sociale du collège ou du lycée ou au secrétariat de l'établissement scolaire pour connaître les conditions d'attribution de cette aide. Les tarifs de la cantine sont déterminés par le département pour les collèges et la région pour les lycées, et peuvent être adaptés à vos revenus et à vos charges en appliquant le quotient familial. Certaines régions offrent des aides pour payer les frais de cantine. Vérifiez auprès de votre collectivité.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 6.3881,
  "km_entree": 65.57,
  "km_sortie": 71.9581
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations sont supprimées ou modifiées. La condition (« sous certaines conditions ») a disparu. L'aide départementale pour une école élémentaire éloignée du domicile est absente. Le chef d'établissement, qui attribue l'aide et informe en début d'année, n'est plus mentionné. Les niveaux sont faussés : « enfants d'âge préscolaire » remplace le primaire, « enfants d'âge scolaire » remplace le collège et le lycée. Enfin, les aides possibles des départements sont omises (« Certaines régions offrent des aides »).
- `termes_juridiques` : 0 — « quotient familial » et « fonds social pour les cantines » sont conservés, mais « chef d'établissement » a disparu et « assistante sociale scolaire » est absent ou déformé en « assistance sociale du collège ou du lycée ».
- `clarte_percue` : 3 — Les phrases sont simples, mais les catégories « âge préscolaire » et « âge scolaire » sont trompeuses et peuvent faire mal comprendre à quel niveau s'applique chaque aide.
- Inventions : « Pour les enfants d'âge préscolaire » : catégorie absente de l'entrée, qui parle du primaire (maternelle et élémentaire); « Pour les enfants d'âge scolaire » : catégorie absente de l'entrée, qui parle du collège et du lycée; « s'adresser à l'assistance sociale [...] ou au secrétariat [...] pour connaître les conditions d'attribution » : dans l'entrée, c'est le chef d'établissement qui informe des conditions d'attribution
- Confiance : haute

## LC-020 (LC, difficile)

### Entrée

```text
{
  "consigne": "Réécris ces articles en langage clair pour un usager, sans perdre d'information. Signale les termes juridiques que tu ne simplifies pas.",
  "nb_mots": 276,
  "texte": "Code de l'action sociale et des familles - Article L131-1\nSous réserve de l'article L. 252-1, les demandes d'admission au bénéfice de l'aide sociale, à l'exception de celles concernant l'aide sociale à l'enfance, sont déposées au centre communal ou intercommunal d'action sociale ou, à défaut, à la mairie de résidence de l'intéressé.\nLes demandes donnent lieu à l'établissement d'un dossier par les soins du centre communal ou intercommunal d'action sociale. Celui-ci peut utiliser à cet effet des visiteurs-enquêteurs.\nLes demandes sont ensuite transmises, dans le mois de leur dépôt, au représentant de l'Etat ou au président du conseil départemental qui les instruit avec l'avis du centre communal ou intercommunal d'action sociale ou, à défaut, du maire et celui du conseil municipal, lorsque le maire ou le centre communal ou intercommunal d'action sociale a demandé la consultation de cette assemblée.\nCode de l'action sociale et des familles - Article L264-1\nPour prétendre au service des prestations sociales légales, réglementaires et conventionnelles, à l'exercice des droits civils qui leur sont reconnus par la loi, ainsi qu'à la délivrance d'un titre national d'identité, à l'inscription sur les listes électorales ou à l'aide juridictionnelle, les personnes sans domicile stable doivent élire domicile soit auprès d'un centre communal ou intercommunal d'action sociale, soit auprès d'un organisme agréé à cet effet.\nL'organisme compétent pour attribuer une prestation sociale légale, réglementaire ou conventionnelle est celui dans le ressort duquel la personne a élu domicile.\nLe département débiteur de l'allocation personnalisée d'autonomie, de la prestation de compensation du handicap et du revenu de solidarité active mentionnés respectivement aux articles L. 232-1, L. 245-1 et L. 262-1 est celui dans le ressort duquel l'intéressé a élu domicile."
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "Les demandes d'aide sociale (sauf aide sociale à l'enfance, et sous réserve de l'article L. 252-1) se déposent au CCAS ou CIAS, ou à défaut à la mairie de résidence",
    "Le CCAS ou CIAS établit le dossier et peut recourir à des visiteurs-enquêteurs",
    "Les demandes sont transmises dans le mois du dépôt au représentant de l'État ou au président du conseil départemental, qui les instruit",
    "L'instruction se fait avec l'avis du CCAS ou CIAS (ou à défaut du maire), et celui du conseil municipal si sa consultation a été demandée",
    "Les personnes sans domicile stable doivent élire domicile auprès d'un CCAS ou CIAS ou d'un organisme agréé pour accéder aux prestations sociales, aux droits civils, à un titre national d'identité, à l'inscription sur les listes électorales ou à l'aide juridictionnelle",
    "L'organisme compétent pour une prestation est celui du lieu d'élection de domicile",
    "Le département qui paie l'Apa, la PCH et le RSA est celui où la personne a élu domicile"
  ],
  "termes_juridiques_a_conserver": [
    "demandes d'admission",
    "aide sociale",
    "centre communal ou intercommunal d'action sociale",
    "visiteurs-enquêteurs",
    "représentant de l'Etat",
    "élire domicile",
    "organisme agréé",
    "aide juridictionnelle",
    "département débiteur"
  ]
}
```

### Sortie (statut ok)

```text
Texte réécrit :

1. Si vous avez besoin d'aide sociale, vous devez déposer votre demande au centre local ou intermunicipal d'aide sociale, ou à la mairie de votre lieu de résidence. Le centre s'occupe de créer un dossier pour vous et peut utiliser des visiteurs-enquêteurs pour vous aider. Vous recevrez une réponse dans le mois suivant la date de dépôt.

2. Pour bénéficier des prestations sociales légales, réglementaires et conventionnelles, ainsi que pour exercer vos droits civils reconnus par la loi, vous devez vivre dans un lieu déterminé. Vous avez le choix entre un centre local ou intermunicipal d'action sociale ou un organisme agréé. Le service compétent attribuera la prestation sociale légale, réglementaire ou conventionnelle en fonction du lieu où vous avez choisi de vivre.

3. Si vous avez besoin d'une aide juridictionnelle, vous devez vivre dans un lieu déterminé. Vous avez le choix entre un centre local ou intermunicipal d'action sociale ou un organisme agréé. Le service compétent attribuera l'aide juridictionnelle en fonction du lieu où vous avez choisi de vivre.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 18.4585,
  "km_entree": 48.65,
  "km_sortie": 67.1085
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs erreurs graves : « Vous recevrez une réponse dans le mois suivant la date de dépôt » remplace la transmission dans le mois par une promesse de réponse ; « vous devez vivre dans un lieu déterminé » déforme l'élection de domicile ; la réserve de l'article L. 252-1, l'exclusion de l'aide sociale à l'enfance, le « à défaut » de la mairie, l'instruction par le préfet ou le président du conseil départemental, les avis du CCAS, du maire et du conseil municipal, le titre d'identité, les listes électorales et le département débiteur de l'Apa, de la PCH et du RSA sont supprimés.
- `termes_juridiques` : 0 — « Élire domicile » est remplacé à tort par « vivre dans un lieu déterminé ». « Centre communal ou intercommunal d'action sociale » devient « centre local ou intermunicipal d'aide sociale ». « Représentant de l'Etat », « demandes d'admission » et « département débiteur » sont absents, et aucun terme juridique n'est signalé comme le demandait la consigne.
- `clarte_percue` : 3 — Les phrases sont simples et l'usager les lit facilement, mais il est induit en erreur : il croit devoir « vivre » dans un centre, et la section 3 répète la section 2.
- Inventions : Vous recevrez une réponse dans le mois suivant la date de dépôt; vous devez vivre dans un lieu déterminé; peut utiliser des visiteurs-enquêteurs pour vous aider; en fonction du lieu où vous avez choisi de vivre; centre local ou intermunicipal d'aide sociale
- Confiance : haute

## LC-024 (LC, difficile)

### Entrée

```text
{
  "consigne": "Réécris ces articles en langage clair pour un usager, sans perdre d'information. Signale les termes juridiques que tu ne simplifies pas.",
  "nb_mots": 443,
  "texte": "Code de la commande publique - Article L2192-10\nLes pouvoirs adjudicateurs, y compris lorsqu'ils agissent en tant qu'entités adjudicatrices, paient les sommes dues en principal en exécution d'un marché dans un délai prévu par le marché ou, à défaut, dans un délai fixé par voie réglementaire et qui peut être différent selon les catégories de pouvoirs adjudicateurs.Lorsqu'un délai de paiement est prévu par le marché, celui-ci ne peut excéder le délai prévu par voie réglementaire.\nCode de la commande publique - Article R2192-10\nLe délai de paiement prévu à l'article L. 2192-10 est fixé à trente jours pour les pouvoirs adjudicateurs, y compris lorsqu'ils agissent en tant qu'entité adjudicatrice.\nCode de la commande publique - Article R2192-11\nPar dérogation à l'article R. 2192-10, le délai de paiement est fixé à :\n1° Cinquante jours pour les établissements publics de santé et les établissements du service de santé des armées ;\n2° Soixante jours pour les entreprises publiques au sens du II de l'article 1er de l'ordonnance n° 2004-503 du 7 juin 2004 portant transposition de la directive 80/723/ CEE relative à la transparence des relations financières entre les Etats membres et les entreprises publiques, à l'exception de celles ayant la nature d'établissements publics locaux.\nCode de la commande publique - Article L2192-12\nLe retard de paiement est constitué lorsque les sommes dues au créancier, qui a rempli ses obligations légales et contractuelles, ne sont pas versées par le pouvoir adjudicateur à l'échéance prévue au marché ou à l'expiration du délai de paiement.\nCode de la commande publique - Article L2192-13\nDès le lendemain de l'expiration du délai de paiement ou de l'échéance prévue par le marché, le retard de paiement fait courir, de plein droit et sans autre formalité, des intérêts moratoires dont le taux est fixé par voie réglementaire.Il ouvre droit, dans les conditions prévues à la présente sous-section, à des intérêts moratoires, à une indemnité forfaitaire et, le cas échéant, à une indemnisation complémentaire versés au créancier par le pouvoir adjudicateur.Le retard de paiement donne lieu, de plein droit et sans autre formalité, au versement d'une indemnité forfaitaire pour frais de recouvrement, dont le montant est fixé par voie réglementaire.Lorsque les frais de recouvrement exposés sont supérieurs au montant de l'indemnité forfaitaire prévue à l'alinéa précédent, le créancier peut demander une indemnisation complémentaire, sur justification.\nCode de la commande publique - Article R2192-31\nLe taux des intérêts moratoires mentionnés à l'article L. 2192-13 est égal au taux d'intérêt appliqué par la Banque centrale européenne à ses opérations principales de refinancement les plus récentes, en vigueur au premier jour du semestre de l'année civile au cours duquel les intérêts moratoires ont commencé à courir, majoré de huit points de pourcentage."
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "Les pouvoirs adjudicateurs paient dans le délai prévu par le marché ou, à défaut, dans le délai réglementaire ; le délai du marché ne peut pas dépasser le délai réglementaire",
    "Délai de paiement : trente jours pour les pouvoirs adjudicateurs",
    "Par dérogation : cinquante jours pour les établissements publics de santé et du service de santé des armées ; soixante jours pour les entreprises publiques (sauf établissements publics locaux)",
    "Le retard de paiement est constitué quand les sommes dues au créancier qui a rempli ses obligations ne sont pas versées à l'échéance ou à l'expiration du délai",
    "Dès le lendemain, le retard fait courir de plein droit des intérêts moratoires, et ouvre droit à une indemnité forfaitaire pour frais de recouvrement",
    "Si les frais de recouvrement dépassent l'indemnité forfaitaire, le créancier peut demander une indemnisation complémentaire sur justification",
    "Taux des intérêts moratoires : taux de refinancement de la BCE en vigueur au premier jour du semestre où les intérêts commencent à courir, majoré de huit points de pourcentage"
  ],
  "termes_juridiques_a_conserver": [
    "pouvoirs adjudicateurs",
    "entités adjudicatrices",
    "délai de paiement",
    "retard de paiement",
    "intérêts moratoires",
    "indemnité forfaitaire pour frais de recouvrement",
    "créancier",
    "de plein droit"
  ]
}
```

### Sortie (statut ok)

```text
Article L2192-10 : Les adjudicateurs paient les sommes dues dans un délai prévu par le marché ou, à défaut, dans un délai fixé par voie réglementaire.

Article R2192-10 : Le délai de paiement est de trente jours pour les adjudicateurs.

Article R2192-11 : Pour les établissements de santé et les établissements du service de santé des armées, le délai de paiement est de cinquante jours. Pour les entreprises publiques (sauf les établissements locaux), il est de soixante jours.

Article L2192-13 : Si les sommes dues ne sont pas versées dans le délai prévu, des intérêts moratoires commencent à courir. Le taux de ces intérêts est fixé par voie réglementaire.

Article R2192-31 : Le taux des intérêts moratoires est égal au taux de l'année civile, majoré de huit points de pourcentage.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 20.3962,
  "km_entree": 50.13,
  "km_sortie": 70.5262
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations obligatoires sont supprimées ou modifiées : la règle selon laquelle le délai du marché ne peut pas dépasser le délai réglementaire, l'article L2192-12 (définition du retard de paiement et condition du créancier ayant rempli ses obligations), le point de départ « dès le lendemain », l'indemnité forfaitaire pour frais de recouvrement et l'indemnisation complémentaire. Le taux est aussi faussé : « égal au taux de l'année civile » au lieu du taux de refinancement de la BCE en vigueur au premier jour du semestre.
- `termes_juridiques` : 0 — « pouvoirs adjudicateurs » est remplacé à tort par « adjudicateurs ». « entités adjudicatrices », « retard de paiement », « indemnité forfaitaire pour frais de recouvrement », « créancier » et « de plein droit » ont disparu. Aucun terme juridique n'est signalé ni expliqué, contrairement à la consigne.
- `clarte_percue` : 2 — Le texte est court, mais il garde du jargon non expliqué (« intérêts moratoires », « par voie réglementaire », « adjudicateurs »). Sa formule de taux, incohérente (« taux de l'année civile »), est incompréhensible pour un usager.
- Inventions : Le taux des intérêts moratoires est égal au « taux de l'année civile » (formulation absente de l'entrée, qui vise le taux de refinancement de la BCE en vigueur au premier jour du semestre); « établissements de santé » au lieu d'« établissements publics de santé », ce qui élargit le champ de la dérogation; « sauf les établissements locaux » au lieu d'« établissements publics locaux »
- Confiance : haute

**Juge second** : juge

- `fidelite` : 1 — La nuance 'le délai du marché ne peut pas dépasser le délai réglementaire' (Article L2192-10) est perdue, et le taux des intérêts moratoires n'est pas précisé comme étant celui de la BCE au premier jour du semestre (Article R2192-31).
- `termes_juridiques` : 0 — Les termes 'pouvoirs adjudicateurs', 'entités adjudicatrices', 'de plein droit', 'indemnité forfaitaire pour frais de recouvrement' et 'créancier' sont soit omis, soit remplacés à tort ('adjudicateurs' au lieu de 'pouvoirs adjudicateurs').
- `clarte_percue` : 4 — La reformulation est globalement claire, mais l'omission de certains termes juridiques et la simplification excessive du taux des intérêts moratoires pourraient induire en erreur un usager non averti.
- Inventions : Remplacement de 'pouvoirs adjudicateurs' par 'adjudicateurs' sans explication; Omission de l'indemnité forfaitaire pour frais de recouvrement et de la possibilité d'indemnisation complémentaire (Article L2192-13); Précision manquante sur le taux des intérêts moratoires (taux BCE au premier jour du semestre)
- Confiance : haute

## NR-001 (NR, facile)

### Entrée

```text
Quelle est la durée du mandat du Président de la République française, et combien de fois peut-il être renouvelé consécutivement ?
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "Le mandat du Président de la République dure cinq ans ; il est renouvelable une fois consécutivement.",
  "criteres": [
    "Durée du mandat : cinq ans",
    "Renouvelable une seule fois consécutivement",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
Le mandat d'un président de la République française est de 5 ans. Il ne peut pas être renouvelé plus d'une fois consécutivement.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse indique correctement « Le mandat […] est de 5 ans » et « ne peut pas être renouvelé plus d'une fois consécutivement », ce qui correspond à la référence, en français correct.
- Inventions : aucune
- Confiance : haute

## NR-002 (NR, facile)

### Entrée

```text
En France, l'élection des représentants au Parlement européen se fait-elle en un ou en deux tours ? En quelle année aura lieu l'élection qui suit celle des 8 et 9 juin 2024 ?
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "Il n'y a qu'un seul tour. L'élection suivante aura lieu en 2029.",
  "criteres": [
    "Un seul tour de scrutin",
    "Prochaine élection : 2029",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
En France, l'élection des représentants au Parlement européen se fait en deux tours. L'élection suivante est prévue pour le 8 et 9 juin 2026.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse sur les deux points : « se fait en deux tours » contredit le scrutin à un seul tour, et « prévue pour le 8 et 9 juin 2026 » contredit l'échéance de 2029.
- Inventions : L'élection européenne en France se fait en deux tours; L'élection suivante est prévue pour les 8 et 9 juin 2026
- Confiance : haute

## NR-008 (NR, moyen)

### Entrée

```text
Un courrier est reçu le vendredi 27 février 2026. La date limite de réponse est fixée 15 jours plus tard (on ajoute 15 jours à la date de réception) ; si elle tombe un samedi ou un dimanche, elle est reportée au lundi suivant. Quelle est la date limite ? Explique ton raisonnement.
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "Le lundi 16 mars 2026 (27 février + 15 jours = samedi 14 mars 2026, car février 2026 compte 28 jours ; report au lundi suivant).",
  "criteres": [
    "Résultat final : lundi 16 mars 2026",
    "Étape intermédiaire juste : samedi 14 mars 2026",
    "Prise en compte des 28 jours de février 2026",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
La date limite de réponse est le vendredi 22 mars 2026.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie affirme « le vendredi 22 mars 2026 » au lieu du lundi 16 mars 2026 : le résultat est faux (le 22 mars 2026 est d'ailleurs un dimanche), l'étape intermédiaire du samedi 14 mars est absente, et aucun raisonnement n'est fourni, notamment sur les 28 jours de février.
- Inventions : Date limite « vendredi 22 mars 2026 », non vérifiable et contraire à la référence (le 22 mars 2026 est un dimanche).
- Confiance : haute

## NR-010 (NR, moyen)

### Entrée

```text
Trois agents, Alice, Bruno et Chloé, tiennent l'accueil le lundi, le mardi et le mercredi, un agent par jour et un jour chacun. Bruno ne travaille pas le lundi. Chloé travaille le lendemain du jour d'Alice. Qui travaille quel jour ? Justifie.
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "Alice le lundi, Chloé le mardi, Bruno le mercredi. Si Alice travaillait le mardi, Chloé serait le mercredi et Bruno le lundi, ce qui est exclu ; Alice ne peut pas être le mercredi (pas de lendemain).",
  "criteres": [
    "Alice : lundi",
    "Chloé : mardi",
    "Bruno : mercredi",
    "Justification qui écarte les autres possibilités",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
Alice travaille le lundi, Bruno ne travaille pas le lundi, et Chloé travaille le mardi.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie n'attribue jamais explicitement le mercredi à Bruno (« Bruno ne travaille pas le lundi » ne fait que reprendre l'énoncé) et ne fournit aucune justification écartant les autres possibilités, alors que la question demande « Justifie ».
- Inventions : aucune
- Confiance : haute

## NR-014 (NR, difficile)

### Entrée

```text
Un guichet est ouvert de 8 h 30 à 12 h 15 et de 13 h 45 à 17 h, du lundi au vendredi, sauf le mercredi après-midi où il est fermé. Combien d'heures est-il ouvert par semaine ? Quelle est la durée moyenne d'ouverture par jour ouvré ? Explique tes calculs.
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "31 h 45 par semaine (matins : 3 h 45 × 5 = 18 h 45 ; après-midi : 3 h 15 × 4 = 13 h). Moyenne : 1 905 min ÷ 5 = 381 min, soit 6 h 21 par jour.",
  "criteres": [
    "Total hebdomadaire : 31 h 45",
    "Étapes justes : 3 h 45 × 5 matins et 3 h 15 × 4 après-midi",
    "Moyenne par jour ouvré : 6 h 21 (381 minutes)",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
Le guichet est ouvert de 8 h 30 à 12 h 15 le lundi au vendredi, et de 13 h 45 à 17 h, du lundi au vendredi, sauf le mercredi après-midi où il est fermé.

Heures ouvertes par semaine :
- Du lundi au vendredi : (12 h 15 - 8 h 30) + (13 h 45 - 12 h 15) = 3 h 45 + 1 h 30 = 5 heures 15 minutes
- Le mercredi après-midi : pas d'ouverture
- Heures totales : 5 heures 15 minutes

Durée moyenne d'ouverture par jour ouvrable :
- Nombre de jours ouvrables : 5 (dimanche exclu)
- Durée moyenne : 5 heures 15 minutes / 5 jours = 1 heure 3 minutes

Le guichet est ouvert pendant une moyenne de 1 heure 3 minutes par jour ouvrable.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse : elle calcule « (13 h 45 - 12 h 15) = 1 h 30 » (la pause au lieu de l'après-midi), obtient un total hebdomadaire de « 5 heures 15 minutes » au lieu de 31 h 45 et une moyenne de « 1 heure 3 minutes » au lieu de 6 h 21, sans multiplier par les 5 matins et les 4 après-midi.
- Inventions : Calcul de l'après-midi comme (13 h 45 - 12 h 15) = 1 h 30, non conforme à l'entrée; Total hebdomadaire de 5 heures 15 minutes; Moyenne de 1 heure 3 minutes par jour; « dimanche exclu » comme justification du nombre de jours ouvrés
- Confiance : haute

**Juge second** : juge

- `exactitude` : 0 — Les calculs sont incorrects : la durée d'ouverture quotidienne est mal calculée (1 h 30 au lieu de 3 h 15 pour l'après-midi), et la moyenne par jour ouvré est fausse (1 h 03 au lieu de 6 h 21). Les étapes ne respectent pas les critères de référence.
- Inventions : La durée d'ouverture quotidienne est calculée à 5 h 15 au lieu de 7 h (3 h 45 le matin + 3 h 15 l'après-midi, sauf le mercredi après-midi); La moyenne par jour ouvré est indiquée comme 1 h 03 au lieu de 6 h 21; L'absence de sources citées n'est pas une invention, mais les calculs erronés le sont
- Confiance : haute

## NR-028 (NR, difficile)

### Entrée

```text
À partir du texte suivant, dresse la liste chronologique des étapes prévues après le comité de pilotage, sous la forme « date : action », sans reprendre les événements déjà passés : « Le comité de pilotage du 4 avril a décidé que l'appel d'offres serait lancé le 15 mai. Avant cela, le cahier des charges devra être validé au plus tard le 30 avril. Les candidatures seront reçues jusqu'au 20 juin, puis la commission se réunira le 3 juillet. Pour mémoire, le budget du projet avait été voté le 12 décembre 2024. »
```

### Références (vues par le Juge)

```text
{
  "sous_type": "consigne",
  "reponse_reference": "- 30 avril : validation du cahier des charges (au plus tard)\n- 15 mai : lancement de l'appel d'offres\n- 20 juin : fin de la réception des candidatures\n- 3 juillet : réunion de la commission",
  "criteres": [
    "Quatre étapes exactement, au format « date : action »",
    "Ordre chronologique : 30 avril, 15 mai, 20 juin, 3 juillet",
    "Le comité du 4 avril et le vote du budget du 12 décembre 2024 sont exclus",
    "Actions fidèles au texte, sans ajout ni étape inventée",
    "Orthographe, grammaire et ponctuation correctes"
  ]
}
```

### Sortie (statut ok)

```text
- 30 avril : validation du cahier des charges
- 15 mai : lancement de l'appel d'offres
- 20 juin : reçu des candidatures
- 3 juillet : réunion de la commission

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Les quatre étapes sont présentes, dans l'ordre chronologique, au bon format et sans les événements passés, mais « 20 juin : reçu des candidatures » est fautif : « reçu » désigne un justificatif, il fallait « réception ». Cette formulation trahit aussi le sens de « jusqu'au 20 juin », qui marque la fin de la réception ; les critères d'orthographe et de fidélité ne sont donc pas pleinement respectés.
- Inventions : aucune
- Confiance : moyenne

## Q-006 (Q, facile)

### Entrée

```text
Une locataire me demande ce qu'est la garantie Visale et ce qui se passe si elle ne peut plus payer son loyer. Que lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "La garantie Visale est une caution locative gratuite qu'Action Logement accorde pour certains logements mis en location en métropole, dans les Drom ou à Saint-Martin. Le locataire doit obtenir le visa d'Action Logement et le bailleur doit accepter l'acte de cautionnement. En cas de loyers impayés ou de dégradations locatives, Action Logement verse d'abord au bailleur le montant dû, puis se fait rembourser par le locataire : la dette reste donc due. Le locataire et le bailleur ne doivent pas être membres de la même famille (grand-parent, parent ou enfant). Ne vaut pas avis juridique.",
  "elements_cles": [
    "Caution locative gratuite accordée par Action Logement",
    "Le locataire obtient le visa d'Action Logement ; le bailleur doit accepter l'acte de cautionnement",
    "En cas d'impayés ou de dégradations, Action Logement verse d'abord au bailleur le montant dû",
    "Action Logement se fait ensuite rembourser par le locataire (la dette reste due)"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F33453"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
La garantie Visale est une caution locative gratuite accordée par Action Logement pour certains logements situés en métropole, dans les Drom ou à Saint-Martin (Com). Pour cela, le locataire doit obtenir le visa d'Action Logement et le bailleur doit accepter l'acte de cautionnement. En cas de dégradations locales ou de loyers impayés, Action Logement verse d'abord au bailleur le montant dû, et se fait ensuite rembourser par le locataire.

Si la locataire ne peut plus payer son loyer, le bailleur doit accepter l'acte de cautionnement. Le bailleur doit accepter l'acte de cautionnement et le locataire doit obtenir le visa d'Action Logement. En cas de dégradations locales ou de loyers impayés, Action Logement verse d'abord au bailleur le montant dû, et se fait ensuite rembourser par le locataire.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — Les quatre éléments clés figurent bien, mais avec une imprécision : « dégradations locales » au lieu de « dégradations locatives ». Le second paragraphe répète le premier de façon incohérente (« Si la locataire ne peut plus payer son loyer, le bailleur doit accepter l'acte de cautionnement »), ce qui brouille la réponse sans constituer une erreur grave.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), alors que la fiche service-public.gouv.fr F33453 était attendue.
- Inventions : aucune
- Confiance : haute

## Q-013 (Q, moyen)

### Entrée

```text
Un bénéficiaire de l'AAH vient de signer un contrat de travail dans une entreprise classique. Il me demande s'il va perdre son AAH et comment son salaire sera pris en compte. Que lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Il ne la perd pas forcément : le cumul de l'AAH et de revenus professionnels est possible en milieu ordinaire de travail. Pendant les 6 premiers mois, ses revenus professionnels ne sont pas pris en compte et il garde son AAH complète. Ensuite, l'AAH est réduite (AAH différentielle) : la Caf ou la MSA retient 20 % de la part du salaire jusqu'à 560,11 € par mois et 60 % de la part au-delà. Il doit déclarer ses ressources à la Caf ou à la MSA tous les 3 mois. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Cumul possible en milieu ordinaire de travail",
    "6 premiers mois : revenus non pris en compte, AAH complète",
    "Ensuite AAH différentielle : 20 % retenus jusqu'à 560,11 € par mois, 60 % au-delà",
    "Déclaration trimestrielle des ressources à la Caf ou à la MSA"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F21615"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Le bénéficiaire de l'AAH peut cumuler ses revenus professionnels avec l'allocation aux adultes handicapés (AAH) dans certaines conditions. Les règles de cumul diffèrent selon que l'activité est exercée dans une entreprise du milieu ordinaire de travail ou dans un établissement et service d'accompagnement par le travail (Ésat). Lorsque le bénéficiaire commence à travailler, ses revenus professionnels ne sont pas pris en compte pendant les 6 premiers mois, il continue donc à percevoir son AAH complet. Après ces 6 mois, son AAH est réduite (AAH différentielle). Pour calculer son AAH, la caisse d'allocations familiales (Caf) ou la mutualité sociale agricole (MSA) prend en compte ses revenus professionnels à partir desquels elle applique un abattement. Si le salaire est de 1500 € par mois, la Caf ou la MSA prend en compte 20 % des 560,11 € premiers euros, soit 109,38 €, et prend ensuite en compte 60 % du reste du salaire, soit 572,15 €. Au total, les revenus comptent pour 681,53 € dans le calcul de l'AAH. Le bénéficiaire peut utiliser un simulateur pour faire une estimation de ses droits. Pour obtenir des informations précises sur le mode de calcul, il doit contacter son Caf ou MSA.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Le calcul chiffré est faux : « 20 % des 560,11 € premiers euros, soit 109,38 € » (le bon résultat est 112,02 €), « 60 % du reste du salaire, soit 572,15 € » (le bon résultat est 563,93 €) et « au total 681,53 € » (le bon total est 675,95 €) ; de plus, la déclaration trimestrielle des ressources à la Caf ou à la MSA est absente.
- `pertinence_source` : 0 — La réponse ne cite aucune source (« Sources citées : aucune »), alors que la fiche F21615 de service-public.gouv.fr était attendue.
- Inventions : 20 % des 560,11 € premiers euros, soit 109,38 €; 60 % du reste du salaire, soit 572,15 €; Au total, les revenus comptent pour 681,53 € dans le calcul de l'AAH; Le bénéficiaire peut utiliser un simulateur pour faire une estimation de ses droits
- Confiance : haute

## Q-015 (Q, difficile)

### Entrée

```text
Un couple marié vit à domicile ; l'épouse va bénéficier de l'Apa. Les ressources du couple prises en compte s'élèvent à 3 400 € par mois, et le couple perçoit en plus l'APL. Comment calcule-t-on les ressources retenues pour son reste à charge, l'APL compte-t-elle, et dans quelle tranche se situe-t-elle ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Pour l'Apa à domicile d'une personne en couple, on additionne les ressources prises en compte du couple (revenus déclarés sur le dernier avis d'imposition, produits de placements soumis au prélèvement libératoire, biens hors résidence principale, capitaux ni exploités ni placés), évaluées par mois, puis on divise ce total par 1,7. L'APL fait partie des ressources exclues, comme l'ALF, l'ALS, les remboursements de soins, la prime de déménagement ou les apports des enfants pour la prise en charge de la perte d'autonomie. Ici, 3 400 € divisés par 1,7 donnent 2 000 € par mois. Ce montant est compris entre 933,89 € et 3 439,31 € : le reste à charge varie progressivement de 0 % à 90 % du montant du plan d'aide accepté. Jusqu'à 933,89 €, il n'y aurait aucun reste à charge ; au-delà de 3 439,31 €, il serait de 90 % du plan d'aide. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Couple à domicile : total des ressources prises en compte divisé par 1,7",
    "L'APL (comme l'ALF et l'ALS) fait partie des ressources exclues",
    "3 400 € / 1,7 = 2 000 € par mois",
    "Entre 933,89 € et 3 439,31 € : reste à charge progressif de 0 % à 90 % du plan d'aide accepté",
    "Aucun reste à charge jusqu'à 933,89 € ; 90 % du plan d'aide au-delà de 3 439,31 €"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F1802"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Le montant total des ressources par mois pour le couple marié est de 3 400 €. Cette somme est divisée par 1,7 pour obtenir le montant total des ressources de leur couple par mois, qui est de 2 000 €. L'Allocation personnelle d'autonomie (Apa) est attribuée sous conditions d'âge, de résidence et de perte d'autonomie. Une participation financière peut être laissée à leur charge, selon le montant total de leurs ressources par mois. Pour déterminer le montant total de leurs ressources par mois, seules certaines ressources sont prises en compte.

La liste de ces ressources figure dans la colonne « Ressources prises en compte (évaluées mensuellement) » du tableau qui suit. Le montant total des ressources de leur couple par mois correspond au montant total de ces ressources, évaluées par mois, et divisé par 1,7.

Le couple marié perçoit en plus l'APL. L'APL est une aide sociale à l'hébergement qui peut être accordée pour aider à payer le tarif hébergement. Pour calculer les ressources retenues pour son reste à charge, seules certaines des ressources du couple sont prises en compte. La liste de ces ressources figure dans la colonne « Ressources prises en compte (évaluées mensuellement) » du tableau qui suit.

Le montant total des ressources de leur couple par mois correspond au montant total de ces ressources, évaluées par mois, et divisé par 1,7.

Le couple marié perçoit en plus l'APL. L'APL est une aide sociale à l'hébergement qui peut être accordée pour aider à payer le tarif hébergement. Pour calculer les ressources retenues pour son reste à charge, seules certaines des ressources du couple sont prises en compte. La liste de ces ressources figure dans la colonne « Ressources prises en compte (évaluées mensuellement) » du tableau qui suit.

Le montant total des ressources de leur couple par mois correspond au montant total de ces ressources, évaluées par mois, et divisé par 1,7.

Le montant total des ressources de leur couple par mois est donc de 2 000 €. Le couple marié perçoit en plus l'APL. L'APL est une aide sociale à l'hébergement qui peut être accordée pour aider à payer le tarif hébergement. Pour calculer les ressources retenues pour son reste à charge, seules certaines des ressources du couple sont prises en compte. La liste de ces ressources figure dans la colonne « Ressources prises en compte (évaluées mensuellement) » du tableau qui suit.

Le montant total des ressources de leur couple par mois correspond au montant total de ces ressources, évaluées par mois, et divisé par 1,7.

Le montant total des ressources de leur couple par mois est donc de 2 000 €. Le couple marié perçoit en plus l'APL. L'APL est une aide sociale à l'hébergement qui peut être accordée pour aider à payer le tarif hébergement. Pour calculer les ressources retenues pour son reste à charge, seules certaines des ressources du couple sont prises en compte. La liste de ces ressources figure dans la colonne « Ressources prises en compte (évaluées mensuellement) » du tableau qui suit.

Le montant total des ressources de leur couple par mois correspond au montant total de ces ressources, évaluées par mois, et divisé par 1,7.

Le montant total des ressources de leur couple par mois est donc de 2 000 €. Le couple marié perçoit en plus l'APL. L'APL est une aide sociale à l'hébergement qui peut être accordée pour aider à payer le tarif hébergement. Pour calculer les ressources retenues pour son reste à charge, seules certaines des ressources du couple sont prises en compte. La liste de ces ressources figure dans la colonne « Ressources prises en compte (évaluées mensuellement) » du tableau qui suit.

Le montant total des ressources de leur couple par mois correspond au montant total de ces ressources, évaluées par mois, et divisé par 1,7.

Le montant total des ressources de leur couple par mois est donc de 2 000 €. Le couple marié perçoit en plus l

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie donne bien la division par 1,7 et le résultat de 2 000 €, mais elle ne dit pas que l'APL est exclue des ressources et ne donne aucune tranche (933,89 € / 3 439,31 €, 0 % à 90 %). Elle se trompe aussi sur l'APL (« L'APL est une aide sociale à l'hébergement qui peut être accordée pour aider à payer le tarif hébergement »). Le texte est répétitif et tronqué.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »).
- Inventions : L'APL est une aide sociale à l'hébergement qui peut être accordée pour aider à payer le tarif hébergement; Allocation personnelle d'autonomie (Apa) : le développement est erroné (il s'agit de l'allocation personnalisée d'autonomie); Renvoi à un « tableau qui suit » inexistant
- Confiance : haute

## Q-022 (Q, moyen)

### Entrée

```text
Un usager reçoit un avis d'amende forfaitaire majorée pour un excès de vitesse constaté par radar automatique. Il dit n'avoir jamais reçu l'avis de contravention : il a déménagé sans faire modifier l'adresse de sa carte grise. Il veut contester l'amende majorée. Que puis-je lui expliquer ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "La principale raison de la non-réception de l'avis de contravention est que la carte grise n'a pas été modifiée après le changement d'adresse. Dans ce cas, il peut obtenir une réévaluation du montant à payer. L'infraction ayant été constatée par radar automatique, il dispose de 3 mois à partir de la date d'envoi de l'avis d'amende majorée pour justifier qu'il a déclaré son changement d'adresse au service en charge des cartes grises. Il a ensuite 45 jours à partir de cette déclaration pour payer le montant de l'amende forfaitaire : ce paiement annule la majoration, mais il ne peut plus bénéficier du montant minoré. S'il conteste l'infraction elle-même, et non le montant, il peut faire une réclamation en ligne ou par courrier, selon la procédure indiquée sur l'avis d'amende majorée. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Cause principale : carte grise non modifiée après le changement d'adresse ; réévaluation du montant possible",
    "Radar automatique : 3 mois à partir de l'envoi de l'avis d'amende majorée pour justifier la déclaration du changement d'adresse au service des cartes grises",
    "45 jours à partir de cette déclaration pour payer l'amende forfaitaire, ce qui annule la majoration (sans montant minoré)",
    "Pour contester l'infraction elle-même : réclamation en ligne ou par courrier, selon la procédure indiquée sur l'avis d'amende majorée"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F18510"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Le passage indique que si l'infraction routière a été constatée par radar automatique, l'usager reçoit un avis d'amende forfaitaire majoré par lettre recommandée. Si l'adresse de la carte grise n'est pas à jour, il n'a pas reçu d'avis de contravention. Dans ce cas, l'usager peut obtenir une réévaluation du montant de l'amende à payer. Pour ce faire, il doit justifier le changement d'adresse au service en charge des cartes grises. Il a alors un délai de 45 jours à partir de la date de déclaration de son changement d'adresse pour payer le montant de l'amende forfaitaire. Le paiement de l'amende forfaitaire annule la majoration.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Au moins deux éléments clés manquent : le délai de 3 mois à compter de l'envoi de l'avis d'amende majorée pour justifier le changement d'adresse, et la voie de réclamation en ligne ou par courrier pour contester l'infraction elle-même ; la perte du montant minoré n'est pas non plus mentionnée.
- `pertinence_source` : 0 — La sortie indique « Sources citées : aucune » : aucune source ne traite du point demandé, alors que la fiche F18510 de service-public.gouv.fr était attendue.
- Inventions : L'usager reçoit un avis d'amende forfaitaire majoré « par lettre recommandée » : ce mode d'envoi n'apparaît ni dans l'entrée ni dans les références.
- Confiance : haute

## Q-025 (Q, moyen)

### Entrée

```text
Une mère dont le fils, né Français, a eu 16 ans le 12 septembre 2026 demande à l'accueil de la mairie dans quel délai il doit faire son recensement citoyen, comment le faire, et à quoi sert l'attestation. Que lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Le recensement citoyen est obligatoire. Un jeune né Français doit le faire à partir de son 16e anniversaire et dans les 3 mois qui suivent, jusqu'à la fin du 3e mois : pour un 16e anniversaire le 12 septembre 2026, entre le 12 septembre 2026 et le 31 décembre 2026. Il peut le faire en ligne (avec le livret de famille et sa carte d'identité ou son passeport en cours de validité) ou à la mairie de son domicile (carte d'identité, passeport ou autre document justifiant de la nationalité française, et livret de famille à jour). Il doit faire la démarche lui-même, mais l'un de ses représentants légaux peut la faire à sa place avant ses 18 ans. En mairie, l'attestation de recensement est remise le jour même ; elle est indispensable pour s'inscrire avant 18 ans à un examen (BEP, bac...) ou à un concours administratif. Le recensement entraîne aussi la convocation à la journée défense et citoyenneté (JDC) et l'inscription automatique sur les listes électorales à 18 ans. En ligne, l'attestation se trouve dans le porte-document du compte personnel, ou elle est envoyée par la mairie par courrier dans les 10 jours, ou remise par la mairie. En cas de retard, il faut se faire recenser le plus vite possible tant qu'on a moins de 25 ans. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Obligatoire, à partir du 16e anniversaire et dans les 3 mois : ici entre le 12 septembre 2026 et le 31 décembre 2026",
    "En ligne ou à la mairie du domicile, avec une pièce d'identité (ou un justificatif de nationalité française) et le livret de famille",
    "Un représentant légal peut faire la démarche à sa place avant ses 18 ans",
    "Attestation remise le jour même en mairie, indispensable pour s'inscrire avant 18 ans à un examen ou un concours administratif"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F870"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Une mère dont le fils, né Français, a eu 16 ans le 12 septembre 2026, doit faire son recensement citoyen dans le mois qui suit l'obtention de la nationalité française. Elle doit le faire entre le 12 septembre 2026 et le 31 octobre 2026. L'attestation de recensement citoyen est utilisée pour confirmer l'identité et les informations fournies par le jeune lors du recensement, et est obligatoire pour diverses démarches administratives et sociales.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Erreur factuelle sur le délai (« dans le mois qui suit l'obtention de la nationalité française », « entre le 12 septembre 2026 et le 31 octobre 2026 » au lieu du 31 décembre 2026), et plusieurs éléments clés manquent : modalités (en ligne ou en mairie, pièces), représentant légal, remise le jour même et usage pour les examens et concours avant 18 ans.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »).
- Inventions : Recensement à faire « dans le mois qui suit l'obtention de la nationalité française » (inapplicable à un jeune né Français, délai erroné); Délai jusqu'au « 31 octobre 2026 »; Attestation « utilisée pour confirmer l'identité et les informations fournies par le jeune »; Attestation « obligatoire pour diverses démarches administratives et sociales »
- Confiance : haute

## Q-027 (Q, difficile)

### Entrée

```text
Une usagère dont le compagnon est décédé brutalement, alors qu'ils préparaient leur mariage, demande si elle peut l'épouser à titre posthume et quelle démarche engager. Que puis-je lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Je ne trouve pas de source officielle traitant du mariage posthume dans les fiches dont je dispose : je ne peux donc pas vous indiquer, de façon sourcée, si ce mariage est possible ni quelle démarche suivre. Je vous conseille d'orienter l'usagère vers le service de l'état civil de la mairie, ou vers un professionnel du droit (avocat, notaire), pour connaître les conditions applicables. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Dit explicitement qu'aucune source officielle disponible ne traite du mariage posthume",
    "N'invente ni procédure, ni condition, ni autorité compétente, ni URL",
    "Ne présente aucune fiche service-public (par exemple « Mariage en France ») comme traitant du mariage posthume",
    "Oriente vers le service de l'état civil de la mairie ou vers un professionnel du droit (avocat, notaire)",
    "Si des éléments sur le sujet sont avancés, ils sont présentés comme non sourcés et à vérifier"
  ],
  "sources_attendues": [],
  "sans_reponse": true,
  "orientation_attendue": "Dire qu'aucune source officielle disponible ne traite du mariage posthume, sans inventer de procédure ; orienter l'usagère vers le service de l'état civil de la mairie ou vers un professionnel du droit (avocat, notaire).",
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
L'utilisateur demande si elle peut épouser son compagnon à titre posthume et quelles démarches engager.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie se contente de reformuler la question (« L'utilisateur demande si elle peut épouser son compagnon à titre posthume et quelles démarches engager. »). Il manque au moins deux éléments clés : la déclaration explicite d'absence de source officielle et l'orientation vers l'état civil de la mairie ou un professionnel du droit. La mention « Ne vaut pas avis juridique » est également absente.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), donc aucune source ne traite du point demandé ; aucune n'était d'ailleurs attendue pour cet item sans réponse.
- `cas_sans_reponse` : 0 — La sortie n'invente rien, mais elle ne dit pas qu'aucune source officielle n'a été trouvée et n'oriente l'usagère ni vers le service de l'état civil de la mairie ni vers un avocat ou un notaire, contrairement à l'orientation attendue.
- Inventions : aucune
- Confiance : haute

## Q-028 (Q, facile)

### Entrée

```text
Un usager a reçu un avis de taxe d'habitation sur sa résidence secondaire d'un montant de 250 €. Il n'a pas Internet et voudrait payer en espèces. Est-ce possible, et que se passerait-il si l'avis dépassait 300 € ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Oui : lorsque l'impôt est inférieur ou égal à 300 €, il peut payer en espèces, ou par carte bancaire, chez un buraliste partenaire, à condition que son avis comporte un « QR code » et la mention « payable auprès d'un buraliste » ; il doit recevoir un reçu. Il peut aussi payer par chèque à l'ordre du Trésor public accompagné du talon de paiement, par TIP Sepa, par virement ou par prélèvement. En revanche, lorsque le montant dépasse 300 €, il faut payer directement en ligne ou par prélèvement automatique. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Jusqu'à 300 € : paiement possible en espèces (ou par carte bancaire) chez un buraliste partenaire",
    "Condition : avis portant un « QR code » et la mention « payable auprès d'un buraliste »",
    "Au-delà de 300 € : paiement obligatoirement en ligne ou par prélèvement automatique",
    "Autres moyens possibles jusqu'à 300 € : chèque à l'ordre du Trésor public avec le talon, TIP Sepa, virement, prélèvement"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F31686"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Non, il n'est pas possible de payer en espèces un impôt d'habitation d'un montant de 250 €, car il dépasse le montant de 300 €. Selon les informations fournies dans l'Index local, lorsque le montant de l'impôt dépasse 300 €, il doit être payé directement en ligne ou par prélèvements automatiques.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Erreur factuelle grave : la sortie affirme « il n'est pas possible de payer en espèces un impôt d'habitation d'un montant de 250 €, car il dépasse le montant de 300 € », alors que 250 € est inférieur à 300 € et que le paiement en espèces chez un buraliste partenaire est possible ; la condition du QR code et de la mention « payable auprès d'un buraliste » ainsi que les autres moyens de paiement (chèque, TIP Sepa, virement, prélèvement) manquent également.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), donc aucune source ne traite du point demandé.
- Inventions : Affirmation que 250 € dépasse le montant de 300 € et que le paiement en espèces est impossible pour ce montant
- Confiance : haute

## Q-029 (Q, facile)

### Entrée

```text
Un couple en vacances avec deux enfants de 9 et 13 ans, logé dans un meublé de tourisme de la commune, demande à l'accueil de la mairie s'ils doivent tous payer la taxe de séjour, à qui, et comment en connaître le montant. Que leur répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "La taxe de séjour est due par personne et par nuit par le vacancier qui loge notamment dans un meublé de tourisme. Les enfants de moins de 18 ans en sont exonérés : seuls les deux parents la paient. Elle se paie au logeur, à l'hôtelier ou au propriétaire, ou au professionnel qui assure la réservation par internet pour leur compte, qui la reverse ensuite à la commune. Son montant varie selon le type d'hébergement et selon que l'hébergement est classé ou non ; il doit être affiché chez le logeur et figurer sur la facture, et il est aussi consultable en mairie ou à l'office du tourisme. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Due par personne et par nuit par le vacancier logé en meublé de tourisme",
    "Enfants de moins de 18 ans exonérés : seuls les parents paient",
    "Payée au logeur ou au propriétaire (ou au professionnel de la réservation en ligne), qui la reverse à la commune",
    "Montant variable selon le type d'hébergement et son classement ; affiché chez le logeur et indiqué sur la facture"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F2048"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Le couple doit demander à la mairie s'ils doivent tous payer la taxe de séjour, à qui, et comment en connaître le montant. Selon le passage, le vacancier qui loge dans l'un des hébergements mentionnés doit payer la taxe de séjour, y compris les meubles de tourisme. Le montant de la taxe doit être affiché chez le logeur, l'hôtelier ou le propriétaire du logement et figurer sur la facture remise au vacancier. Pour connaître les règles applicables à leur lieu de séjour, il est possible de contacter la mairie.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Au moins deux éléments clés manquent : l'exonération des enfants de moins de 18 ans (« seuls les parents paient ») n'est pas mentionnée, alors que c'est le cœur de la question « doivent-ils tous payer » ; la perception par le logeur et le reversement à la commune sont absents ; le caractère « par personne et par nuit » et la variation selon le type d'hébergement et son classement manquent aussi.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), alors que la fiche service-public.gouv.fr F2048 était attendue.
- Inventions : aucune
- Confiance : haute

## Q-030 (Q, moyen)

### Entrée

```text
Un propriétaire possède, dans une commune en zone tendue, un appartement non meublé inoccupé depuis janvier 2024. Il l'a mis en vente au prix du marché dès janvier 2024, sans trouver d'acquéreur. Il a reçu un avis de taxe sur les logements vacants pour 2026 et demande s'il doit vraiment la payer et comment elle est calculée. Que lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "La taxe sur les logements vacants (TLV) est due par le propriétaire ou l'usufruitier d'un logement non meublé vacant depuis au moins 1 an au 1er janvier de l'année d'imposition, dans une commune située en zone tendue. Il en est toutefois exonéré lorsque la vacance est indépendante de sa volonté, par exemple un logement mis en vente au prix du marché qui ne trouve pas d'acquéreur ; il doit justifier sa situation (preuve des conditions de mise en vente). Il peut faire une réclamation s'il estime ne pas avoir à payer la TLV, mais la réclamation ne le dispense pas du paiement ; il peut toutefois demander un sursis de paiement. La taxe est calculée sur la valeur locative cadastrale, au taux de 17 % la 1re année d'imposition et de 34 % les années suivantes (17 % si 2026 est sa 1re année d'imposition à la TLV, 34 % sinon). Ne vaut pas avis juridique.",
  "elements_cles": [
    "TLV due par le propriétaire ou l'usufruitier d'un logement non meublé vacant depuis au moins 1 an au 1er janvier, en zone tendue",
    "Exonération si la vacance est indépendante de sa volonté (logement mis en vente au prix du marché sans acquéreur), à justifier",
    "Réclamation possible, mais elle ne dispense pas du paiement ; sursis de paiement possible",
    "Calcul sur la valeur locative cadastrale : 17 % la 1re année, 34 % les années suivantes"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F17293"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Selon les passages de l'Index local fournis, un propriétaire qui possède un appartement non meublé et inoccupé depuis janvier 2024 dans une commune en zone tendue doit payer la taxe annuelle sur les logements vacants (TLV) pour 2026.

[1] Les passages indiquent que si un logement est non meublé et inoccupé depuis au moins 1 an, selon la commune où il est situé, le propriétaire peut avoir à payer la taxe annuelle sur les logements vacants (TLV) ou la taxe d'habitation sur les logements vacants (THLV).

[2] Ils précisent que si le bien est vacant depuis au moins 1 an et se situe dans une zone tendue, le propriétaire doit payer la taxe sur les logements vacants (TLV). Cette taxe est perçue par l'État.

[4] Les passages indiquent que la taxe est calculée d'après la valeur locative cadastrale de l'habitation, qui est revalorisée chaque année en fonction de l'augmentation des prix. Le montant de la taxe est obtenu en multipliant la valeur locative par un taux d'imposition fixé à 17 % pour la première année d'imposition et 34 % pour les années suivantes.

En conséquence, le propriétaire doit payer la taxe annuelle sur les logements vacants (TLV) pour 2026, calculée sur la base de la valeur locative du bien.

Sources citées :
- Taxe annuelle sur les logements vacants (TLV) et taxe d'habitation sur les logements vacants (THLV) — https://www.service-public.gouv.fr/particuliers/vosdroits/F17293
- Taxe annuelle sur les logements vacants (TLV) et taxe d'habitation sur les logements vacants (THLV) — https://www.service-public.gouv.fr/particuliers/vosdroits/F17293
- Taxe annuelle sur les logements vacants (TLV) et taxe d'habitation sur les logements vacants (THLV) — https://www.service-public.gouv.fr/particuliers/vosdroits/F17293
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie conclut que « le propriétaire doit payer la taxe annuelle sur les logements vacants (TLV) pour 2026 », ce qui contredit la source : la vacance indépendante de sa volonté (mise en vente au prix du marché sans acquéreur) ouvre droit à exonération ; elle omet aussi la réclamation et le sursis de paiement, soit deux éléments clés manquants avec une erreur grave.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F17293) traite bien de la TLV et de la THLV, qui sont l'objet de la question.
- Inventions : aucune
- Confiance : haute

**Juge second** : juge

- `exactitude` : 1 — Un élément clé manque : l'exonération possible si la vacance est indépendante de la volonté du propriétaire (logement mis en vente sans acquéreur), à justifier. La réponse indique uniquement que la TLV est due sans mentionner cette exception.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr) est pertinente et traite bien de la TLV, conformément à la référence attendue.
- Inventions : aucune
- Confiance : haute

## Q-035 (Q, facile)

### Entrée

```text
Une usagère vient d'être embauchée en CDI à temps partiel dans une entreprise. Elle me demande s'il existe une durée minimale de travail par semaine et si elle peut travailler moins. Que lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "La durée minimale de travail d'un salarié à temps partiel est fixée par la convention collective ou l'accord de branche étendu. En l'absence de précision dans la convention ou l'accord, le salarié à temps partiel (en CDI ou en CDD) doit effectuer au moins 24 heures par semaine. Une durée inférieure peut être fixée à la demande écrite et motivée du salarié, par exemple en raison de contraintes personnelles (santé, famille) ou pour cumuler plusieurs activités ; l'employeur n'est pas obligé d'accepter. Ne vaut pas avis juridique.",
  "elements_cles": [
    "La durée minimale est fixée par la convention collective ou l'accord de branche étendu",
    "À défaut de précision dans la convention ou l'accord : au moins 24 heures par semaine (CDI ou CDD)",
    "Durée inférieure possible à la demande écrite et motivée du salarié (contraintes personnelles, cumul d'activités), sans obligation d'acceptation pour l'employeur"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F1915"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
L'usagère a été embauchée en CDI à temps partiel dans une entreprise. Selon les informations fournies dans les passages de l'Index local, la durée minimale de travail pour un salarié à temps partiel dans le secteur privé est de 24 heures par semaine. Cependant, des dispositions conventionnelles peuvent prévoir une durée minimale inférieure à 24 heures par semaine dans certaines conditions.

Dans le cas spécifique de l'usagère, il n'y a pas de dispositions conventionnelles spécifiques mentionnées dans les passages. Par conséquent, la durée minimale de travail pour l'usagère est de 24 heures par semaine, conformément à la convention collective ou à l'accord de branche étendu.

En ce qui concerne la possibilité de travailler moins que la durée minimale, des cas spécifiques peuvent s'appliquer, tels que :

- Cas CDD d'une durée maximale de 7 jours
- Cas Remplacement d'un salarié absent
- Cas Dérogation demandée par le salarié (pour des contraintes personnelles)
- Cas Cumul d'activités
- Cas Poursuite des études
- Cas Contrat d'insertion (CDDI)
- Cas Contrat d'insertion par l'activité économique (IAE)

Si l'usagère souhaite travailler moins que la durée minimale de 24 heures par semaine, elle devrait contacter son employeur pour expliquer ses raisons et soumettre une demande écrite et motivée. Un modèle de lettre peut être disponible pour faciliter la demande.

En résumé, l'usagère peut travailler moins que la durée minimale de 24 heures par semaine si elle répond à l'une des conditions spécifiées dans les passages de l'Index local.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Le seuil de 24 heures est juste, mais le premier élément clé est confus et contradictoire (« la durée minimale […] est de 24 heures par semaine, conformément à la convention collective ou à l'accord de branche étendu »), et le troisième est incomplet : la réponse ne dit jamais que l'employeur n'est pas obligé d'accepter la demande.
- `pertinence_source` : 0 — La réponse indique « Sources citées : aucune » ; aucune source traitant du point demandé n'est donc citée.
- Inventions : Liste de dérogations non vérifiables dans les références : « CDD d'une durée maximale de 7 jours », « Remplacement d'un salarié absent », « Poursuite des études », « Contrat d'insertion (CDDI) », « Contrat d'insertion par l'activité économique (IAE) »; « Un modèle de lettre peut être disponible pour faciliter la demande »
- Confiance : moyenne

**Juge second** : juge

- `exactitude` : 1 — Un élément clé est imprécis : la sortie mentionne des 'dispositions conventionnelles' sans rappeler explicitement que la durée minimale de 24h/semaine s'applique *en l'absence de précision dans la convention ou l'accord*. De plus, les cas de dérogation (CDD de 7 jours, remplacement, etc.) ne sont pas cités dans les éléments clés de la référence, ce qui introduit des précisions non vérifiables.
- `pertinence_source` : 0 — Aucune source n'est citée, alors que la référence en attend au moins une (ex. service-public.gouv.fr).
- Inventions : Cas CDD d'une durée maximale de 7 jours; Cas Remplacement d'un salarié absent; Cas Poursuite des études; Cas Contrat d'insertion (CDDI); Cas Contrat d'insertion par l'activité économique (IAE); Modèle de lettre disponible pour faciliter la demande
- Confiance : moyenne

## Q-047 (Q, moyen)

### Entrée

```text
Le maire de notre commune a refusé l'inscription d'un habitant sur la liste électorale, hors période électorale, et lui a notifié ce refus par courrier. L'habitant veut le contester. Quelle est la procédure et quels délais s'appliquent ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Pour contester le refus du maire, l'habitant doit d'abord faire un recours administratif préalable obligatoire devant la commission de contrôle des listes électorales de la commune, dans un délai de 5 jours à compter de la notification de la décision, par courrier ou par mail avec accusé de réception ; il joint une copie de la notification et une preuve du bien-fondé de son inscription. Hors période électorale, la commission décide dans un délai de 30 jours après avoir été saisie ; son silence vaut refus. En cas de rejet ou de silence, il peut faire un recours contentieux devant le tribunal judiciaire dans un délai de 7 jours ; le tribunal rend sa décision dans les 8 jours. Un pourvoi en cassation est ensuite possible dans les 10 jours suivant la notification de la décision du tribunal. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Recours administratif préalable obligatoire devant la commission de contrôle des listes électorales, dans les 5 jours suivant la notification du refus",
    "Envoi par courrier ou mail avec accusé de réception, avec la copie de la notification et une preuve du bien-fondé de l'inscription",
    "Hors période électorale, la commission décide dans les 30 jours ; son silence vaut refus",
    "Puis recours contentieux devant le tribunal judiciaire dans les 7 jours ; décision du tribunal dans les 8 jours",
    "Pourvoi en cassation possible dans les 10 jours suivant la notification de la décision du tribunal"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F34809"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Pour contester le refus d'inscription du maire, l'habitant doit suivre les étapes suivantes :

1. **Recours administratif préalable obligatoire** : L'habitant doit former un recours administratif préalable obligatoire auprès de la commission de contrôle des listes électorales de sa commune. Cette démarche est nécessaire pour ensuite pouvoir saisir le tribunal judiciaire d'un recours contentieux, si nécessaire. Cette démarche doit être effectuée dans un délai de 5 jours à compter de la notification du refus du maire.

2. **Notification du refus** : Le maire a 2 jours par courrier pour informer l'habitant de sa décision de refus. Si l'habitant ne reçoit pas ce courrier et n'est pas inscrit sur les listes électorales, il peut saisir le tribunal judiciaire.

3. **Pourvoi en cassation** : Si l'habitant décide de contester la décision du maire devant la Cour de cassation, il doit le faire dans un délai de 10 jours suivant la notification de la décision du tribunal judiciaire. Le pourvoi est formé par une déclaration orale ou écrite, remise ou adressée par courrier recommandé, soit au greffe du tribunal judiciaire qui a rendu la décision attaquée, soit au greffe de la Cour de cassation. La déclaration doit inclure les informations suivantes : nom et prénoms de l'habitant, adresse, énoncé des moyens de cassation invoqués, et copie de la décision attaquée.

4. **Recours contentieux** : Si l'habitant décide de saisir le tribunal judiciaire d'un recours contentieux, il doit le faire dans un délai de 7 jours à compter de la notification du refus de la commission ou en l'absence de réponse de sa part après 30 jours (21 jours en période électorale). Le tribunal doit rendre sa décision dans les 8 jours et notifier sa décision au maire et à l'habitant par lettre recommandée avec accusé de réception, dans les 2 jours.

En résumé, l'habitant doit suivre une procédure en deux étapes : d'abord, le recours administratif préalable obligatoire auprès de la commission de contrôle des listes électorales, puis, s'il le souhaite, le recours contentieux devant le tribunal judiciaire. Les délais clés sont de 5 jours pour le recours administratif, de 10 jours pour le pourvoi en cassation, et de 7 jours pour le recours contentieux.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — Les éléments sur le RAPO de 5 jours, le recours de 7 jours, la décision en 8 jours et le pourvoi de 10 jours sont présents, mais les modalités d'envoi manquent : la réponse ne mentionne ni le courrier ou mail avec accusé de réception, ni la copie de la notification, ni la preuve du bien-fondé ; la règle « silence vaut refus » n'est qu'implicite (« en l'absence de réponse de sa part après 30 jours ») ; et la formule « contester la décision du maire devant la Cour de cassation » est imprécise, puisque le pourvoi vise la décision du tribunal.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), alors que la fiche service-public F34809 était attendue.
- Inventions : Le maire a 2 jours par courrier pour informer l'habitant de sa décision de refus; Si l'habitant ne reçoit pas ce courrier et n'est pas inscrit sur les listes électorales, il peut saisir le tribunal judiciaire; 21 jours en période électorale; Le pourvoi est formé par une déclaration orale ou écrite, remise ou adressée par courrier recommandé, au greffe du tribunal judiciaire ou de la Cour de cassation, avec nom, prénoms, adresse, moyens de cassation et copie de la décision; Le tribunal notifie sa décision au maire et à l'habitant par lettre recommandée avec accusé de réception dans les 2 jours
- Confiance : moyenne

**Juge second** : juge

- `exactitude` : 1 — Un élément clé est imprécis (délai de 2 jours pour la notification du refus par le maire, non mentionné dans les références) et un autre est manquant (preuve du bien-fondé de l'inscription à joindre au recours).
- `pertinence_source` : 0 — Aucune source n'est citée, alors que la référence attendue est précisée dans les sources_attendues.
- Inventions : Le maire a 2 jours par courrier pour informer l'habitant de sa décision de refus (non vérifiable dans les références).; La déclaration pour le pourvoi en cassation peut être orale (non vérifiable dans les références).
- Confiance : haute

## Q-059 (Q, difficile)

### Entrée

```text
Un couple attend son deuxième enfant ; l'aîné a 3 ans. Les deux conjoints travaillent et ont chacun perçu plus de 10 000 € de salaire en 2024 ; le revenu net catégoriel 2024 du foyer est de 54 000 €. La future mère a passé le premier examen prénatal et déclaré sa grossesse au cours du 2e mois. Le couple a-t-il droit à la prime à la naissance, pour quel montant, et quand sera-t-elle versée ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Oui. Pour 2026, on retient le revenu net catégoriel de 2024. L'enfant à naître compte pour 1 enfant à charge : le couple a donc 2 enfants à charge. Chacun des conjoints ayant perçu au moins 6 306 € de revenus d'activité en 2024, il s'agit d'un couple avec 2 revenus, dont le plafond est de 56 478 € pour 2 enfants : avec 54 000 €, il n'est pas dépassé. Les conditions liées à la grossesse sont remplies (premier examen prénatal passé, grossesse déclarée avant la fin du 3e mois), sous réserve de la condition de résidence en France. Le montant net de la prime est de 1 093,11 €. Elle est versée avant le dernier jour du mois civil suivant le 6e mois de grossesse. Ne vaut pas avis juridique.",
  "elements_cles": [
    "L'enfant à naître compte pour 1 enfant à charge : 2 enfants à charge",
    "Couple avec 2 revenus (chacun au moins 6 306 € en 2024) : plafond de 56 478 € pour 2 enfants, non dépassé par 54 000 €",
    "Conditions de grossesse remplies : premier examen prénatal et déclaration avant la fin du 3e mois",
    "Montant net de la prime : 1 093,11 €",
    "Versement avant le dernier jour du mois civil suivant le 6e mois de grossesse"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F2550"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Le couple a droit à la prime à la naissance pour un montant de 44 542 €, car le revenu net catégoriel 2024 du foyer est de 54 000 €, ce qui correspond au plafond de ressources pour un couple avec un seul revenu pour 2 enfants. La prime à la naissance sera versée avant le dernier jour du mois civil suivant le 6e mois de la grossesse, c'est-à-dire avant le dernier jour du mois qui suit le 6e mois de grossesse.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Erreurs factuelles graves : « pour un montant de 44 542 € » (le montant net est de 1 093,11 €) et « plafond de ressources pour un couple avec un seul revenu » (il s'agit d'un couple avec 2 revenus, plafond de 56 478 €) ; en outre, il manque le décompte de l'enfant à naître (2 enfants à charge) et les conditions de grossesse.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), alors que la fiche F2550 de service-public.gouv.fr était attendue.
- Inventions : Montant de la prime de 44 542 €; Qualification du foyer comme couple avec un seul revenu, alors que l'entrée indique que les deux conjoints travaillent; Affirmation selon laquelle 54 000 € correspond au plafond de ressources pour 2 enfants
- Confiance : haute

## RD-002 (RD, facile)

### Entrée

```text
Je dois vérifier quelles communes sont soumises à la loi SRU et où en est leur inventaire de logements sociaux. Quel est le jeu de données national sur data.gouv.fr ? Donne son nom, son producteur et le lien.

Options de la demande :
{
  "mode": "connecte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": {
    "jeu_principal": {
      "id": "6564969d3579e21795ebd378",
      "titre": "Communes et inventaire SRU",
      "producteur": "Ministère de la Transition écologique",
      "url": "https://www.data.gouv.fr/datasets/communes-et-inventaire-sru"
    },
    "autres_jeux_cites_possibles": [
      {
        "id": "5bd89da406e3e738f68c0ec7",
        "titre": "Communes SRU et DALO",
        "producteur": "Région Occitanie / Pyrénées Méditerranée"
      }
    ],
    "texte": "Le jeu national est « Communes et inventaire SRU » (identifiant 6564969d3579e21795ebd378), produit par le Ministère de la Transition écologique : https://www.data.gouv.fr/datasets/communes-et-inventaire-sru. Il existe aussi des déclinaisons régionales, par exemple « Communes SRU et DALO » (Région Occitanie / Pyrénées Méditerranée)."
  },
  "criteres": [
    "Cite le jeu national « Communes et inventaire SRU » (identifiant 6564969d3579e21795ebd378), pas une déclinaison régionale",
    "Donne le producteur et le lien data.gouv.fr"
  ]
}
```

### Sortie (statut ok)

```text
**Jeu de données national sur data.gouv.fr**

- **Nom du jeu de données** : **Communes et inventaire SRU**  
- **Producteur** : Ministère de la Transition écologique  
- **Lien vers le jeu de données** : https://www.data.gouv.fr/datasets/communes-et-inventaire-sru  

Ce jeu de données contient les informations relatives aux communes françaises qui sont soumises à la loi SRU et leur inventaire de logements sociaux.

Sources citées :
- Communes et inventaire SRU — https://www.data.gouv.fr/datasets/communes-et-inventaire-sru
```

### Contrôles automatiques

```text
{
  "appariement": [
    0
  ],
  "appels_attendus": 1,
  "appels_valides": 1,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": true
}
```

### Verdicts

Aucun verdict.

## RD-004 (RD, facile)

### Entrée

```text
Je cherche la liste des établissements habilités au titre de l'aide sociale à l'enfance (ASE) dans les Hauts-de-Seine. Ce jeu existe-t-il sur data.gouv.fr ? Donne son titre, son producteur et le lien.

Options de la demande :
{
  "mode": "connecte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": {
    "jeu_principal": {
      "id": "57868e94a3a7295d371adcf1",
      "titre": "Etablissements habilités au titre de l'aide sociale à l'enfance (ASE)",
      "producteur": "Département des Hauts-de-Seine",
      "url": "https://www.data.gouv.fr/datasets/etablissements-habilites-au-titre-de-laide-sociale-a-lenfance-ase"
    },
    "texte": "Oui : « Etablissements habilités au titre de l'aide sociale à l'enfance (ASE) » (identifiant 57868e94a3a7295d371adcf1), publié par le Département des Hauts-de-Seine : https://www.data.gouv.fr/datasets/etablissements-habilites-au-titre-de-laide-sociale-a-lenfance-ase."
  },
  "criteres": [
    "Cite le jeu du Département des Hauts-de-Seine (identifiant 57868e94a3a7295d371adcf1), pas un jeu de la Seine-Maritime",
    "Donne le lien data.gouv.fr"
  ]
}
```

### Sortie (statut ok)

```text
**Établissements habilités au titre de l'aide sociale à l'enfance (ASE) – Hauts‑de‑Seine**  
- **Titre du jeu de données** : Établissements habilités au titre de l'aide sociale à l'enfance (ASE)  
- **Producteur** : Département des Hauts‑de‑Seine  
- **Lien** : https://www.data.gouv.fr/datasets/etablissements-habilites-au-titre-de-laide-sociale-a-lenfance-ase  

Ce jeu de données contient les informations sur les établissements qui bénéficient de l’aide sociale à l’enfance dans le département des Hauts‑de‑Seine.

Sources citées :
- Etablissements habilités au titre de l'aide sociale à l'enfance (ASE) — https://www.data.gouv.fr/datasets/etablissements-habilites-au-titre-de-laide-sociale-a-lenfance-ase
```

### Contrôles automatiques

```text
{
  "appariement": [
    0
  ],
  "appels_attendus": 1,
  "appels_valides": 1,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": true
}
```

### Verdicts

Aucun verdict.

## RD-008 (RD, moyen)

### Entrée

```text
La Cour des comptes a publié sur data.gouv.fr les données de son évaluation du revenu de solidarité active (RSA). Combien de fichiers ce jeu contient-il, dans quel format, et quels départements couvrent les fichiers de données brutes ?

Options de la demande :
{
  "mode": "connecte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": {
    "jeu_principal": {
      "id": "623842c62a4a68324dbd6bbb",
      "titre": "Le revenu de solidarité active (RSA)",
      "producteur": "Cour des comptes",
      "url": "https://www.data.gouv.fr/datasets/le-revenu-de-solidarite-active-rsa"
    },
    "texte": "Le jeu « Le revenu de solidarité active (RSA) » (identifiant 623842c62a4a68324dbd6bbb) de la Cour des comptes (https://www.data.gouv.fr/datasets/le-revenu-de-solidarite-active-rsa) contient 8 ressources, toutes au format csv/utf8 (archives .zip). Les trois fichiers de données brutes couvrent : Allier, Aude et Gironde ; Ille-et-Vilaine, Pas-de-Calais et Bas-Rhin ; Seine-Saint-Denis, Martinique et La Réunion."
  },
  "criteres": [
    "Indique 8 ressources au format csv/utf8",
    "Cite les neuf départements des données brutes : Allier, Aude, Gironde, Ille-et-Vilaine, Pas-de-Calais, Bas-Rhin, Seine-Saint-Denis, Martinique, La Réunion"
  ]
}
```

### Sortie (statut ok)

```text
**Fichier(s) du jeu de données**

- **Nombre de fichiers** : **8**  
- **Formats** : tous les fichiers sont en **CSV** (format utf8).  
- **Type** : tous les fichiers sont classés comme **“main”** (données principales du jeu).

**Départements couverts par les fichiers de données brutes**

Les fichiers de données brutes (données brutes) sont organisés par département.  
Les départements couverts par les fichiers de données brutes sont :

- **Allier**  
- **Aude**  
- **Gironde**  
- **Ille‑et‑Vilaine**  
- **Pas‑de‑Calais**  
- **Bas‑Rhain**  
- **Ille‑et‑Villaine** (dans le fichier données brutes)  
- **Martinique**  
- **La Réunion**  

Ces départements correspondent aux régions pour lesquelles le jeu de données RSA fournit des données brutes.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "appariement": [
    0,
    1
  ],
  "appels_attendus": 2,
  "appels_valides": 2,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": false
}
```

### Verdicts

Aucun verdict.

## RD-017 (RD, difficile)

### Entrée

```text
Combien de cartes nationales d'identité payantes la Ville de Caen a-t-elle délivrées en janvier, février et mars 2020 ? Appuie-toi sur le jeu de données publié par la ville sur data.gouv.fr et donne les chiffres mois par mois.

Options de la demande :
{
  "mode": "connecte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": {
    "jeu_principal": {
      "id": "6152de005b5026338d407619",
      "titre": "Ville de Caen - Cartes nationales d'identité, Passeports",
      "producteur": "Ville de Caen",
      "url": "https://www.data.gouv.fr/datasets/ville-de-caen-cartes-nationales-didentite-passeports"
    },
    "texte": "D'après le jeu « Ville de Caen - Cartes nationales d'identité, Passeports » (identifiant 6152de005b5026338d407619, Ville de Caen), fichier ville-cartesdidentite-passeports-20210101.csv filtré sur TypeTitre = CNI payantes (12 lignes au total) : en 2020, mois 1 (janvier) : 134 ; mois 2 (février) : 137 ; mois 3 (mars) : 75 cartes nationales d'identité payantes. Source : https://www.data.gouv.fr/datasets/ville-de-caen-cartes-nationales-didentite-passeports"
  },
  "valeurs_attendues": {
    "ressource_id": "a216f407-d9d7-44a2-845b-91736487bb24",
    "filtre": {
      "colonne": "TypeTitre",
      "operateur": "exact",
      "valeur": "CNI payantes"
    },
    "total_lignes": 12,
    "lignes": [
      {
        "Année": "2020",
        "Mois": "1",
        "Nombre": "134"
      },
      {
        "Année": "2020",
        "Mois": "2",
        "Nombre": "137"
      },
      {
        "Année": "2020",
        "Mois": "3",
        "Nombre": "75"
      }
    ]
  },
  "criteres": [
    "Donne 134, 137 et 75 pour janvier, février et mars 2020",
    "Ne confond pas avec les passeports ni avec les CNI gratuites"
  ]
}
```

### Sortie (statut ok)

```text
<tool_call>
{"name": "query_resource_data", "arguments": {"resource_id": "a216f407-d9d7-44a2-845b-91736487bb24", "page": 2, "page_size": 20}}
</tool_call>

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "appariement": [
    0,
    1,
    null
  ],
  "appels_attendus": 3,
  "appels_valides": 2,
  "litige": false,
  "methode": "valeurs",
  "reponse_exacte": false,
  "valeurs_manquantes": [
    "2020",
    "1",
    "134",
    "2020",
    "137",
    "2020",
    "3",
    "75"
  ]
}
```

### Verdicts

Aucun verdict.

## RD-021 (RD, moyen)

### Entrée

```text
J'ai besoin des effectifs de la fonction publique ventilés par département, en série depuis 2010. Quel jeu de données data.gouv.fr utiliser, quand a-t-il été mis à jour pour la dernière fois et sous quelle licence est-il publié ?

Options de la demande :
{
  "mode": "connecte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": {
    "jeu_principal": {
      "id": "5c4b01198b4c41172131e98d",
      "titre": "Effectifs de la fonction publique par département depuis 2010",
      "producteur": "Direction Générale de l'Administration et de la Fonction Publique",
      "url": "https://www.data.gouv.fr/datasets/effectifs-de-la-fonction-publique-par-departement-depuis-2010",
      "derniere_mise_a_jour": "2019-06-21T15:46:29+00:00",
      "licence": "lov2"
    },
    "texte": "Le jeu est « Effectifs de la fonction publique par département depuis 2010 » (identifiant 5c4b01198b4c41172131e98d), produit par la Direction Générale de l'Administration et de la Fonction Publique : https://www.data.gouv.fr/datasets/effectifs-de-la-fonction-publique-par-departement-depuis-2010. Dernière mise à jour : 2019-06-21T15:46:29+00:00 (21 juin 2019, malgré une fréquence déclarée annual : les données récentes peuvent manquer). Licence : lov2 (Licence Ouverte version 2.0)."
  },
  "criteres": [
    "Cite le jeu départemental de la DGAFP, pas la série territoriale depuis 2004",
    "Date de mise à jour et licence recopiées de get_dataset_info ; signale l'ancienneté de la mise à jour"
  ]
}
```

### Sortie (statut ok)

```text
**Jeu de données à utiliser**

- **Titre** : *Effectifs de la fonction publique par département depuis 2010*  
- **Producteur** : Direction Générale de l'Administration et de la Fonction Publique  
- **Date de dernière mise à jour** : 21 juin 2019  
- **Lien** : https://www.data.gouv.fr/datasets/effectifs-de-la-fonction-publique-par-departement-depuis-2010  

**Description**  
Effectifs au 31 décembre de chaque année dans la fonction publique et taux d’administration. Série longue depuis 2010.  
Le fichier contient les données des effectifs par département pour l’ensemble de la fonction publique (fonction publique d’État, fonction publique territoriale) et la répartition pour la fonction publique d’État, la fonction publique territoriale. Les informations disponibles concernent : effectifs, taux d’administration, part des femmes, âges moyens, part des plus de 30 ans, etc.

**Licence**  
- **Type de licence** : lov2 (licence open data)  
- **Mise à jour** : annuelle  

Cette jeu de données fournit exactement les effectifs de la fonction publique ventilés par département depuis 2010, ce qui répond à la demande d'effectifs par département depuis 2010.

Sources citées :
- Effectifs de la fonction publique par département depuis 2010 — https://www.data.gouv.fr/datasets/effectifs-de-la-fonction-publique-par-departement-depuis-2010
```

### Contrôles automatiques

```text
{
  "appariement": [
    0,
    1
  ],
  "appels_attendus": 2,
  "appels_valides": 2,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": true
}
```

### Verdicts

Aucun verdict.

## RD-022 (RD, moyen)

### Entrée

```text
Je cherche la liste des centres de formation d'apprentis avec leur nombre d'élèves, leur taux d'insertion et leur taux de rupture par spécialité, publiée par la Dares. Quel est ce jeu sur data.gouv.fr, et sous quel format et pour quelle année scolaire ses données sont-elles fournies ?

Options de la demande :
{
  "mode": "connecte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": {
    "jeu_principal": {
      "id": "617a9e0887c6d1cab5c3d281",
      "titre": "Listes des centres de formation d'apprentis  (adresse, nombre d'élèves, taux d'insertion, taux de rupture par spécialité)",
      "producteur": "Dares - statistiques Travail",
      "url": "https://www.data.gouv.fr/datasets/listes-des-centres-de-formation-dapprentis-adresse-nombre-deleves-taux-dinsertion-taux-de-rupture-par-specialite"
    },
    "autres_jeux_cites_possibles": [
      {
        "id": "60b5b0ed2571d1002e2fcb3e",
        "titre": "Inserjeunes Apprentissage par centre de formation d'apprentis (CFA)",
        "producteur": "Ministères de l'Éducation nationale"
      }
    ],
    "texte": "Le jeu est « Listes des centres de formation d'apprentis (adresse, nombre d'élèves, taux d'insertion, taux de rupture par spécialité) » (identifiant 617a9e0887c6d1cab5c3d281), produit par Dares - statistiques Travail : https://www.data.gouv.fr/datasets/listes-des-centres-de-formation-dapprentis-adresse-nombre-deleves-taux-dinsertion-taux-de-rupture-par-specialite. Il contient une seule ressource, « Données - Établissements d'apprentissage 2018-2019 (XLSX, 937.48 Ko) », au format xlsx : les données portent sur l'année 2018-2019. Pour des taux d'insertion plus récents par CFA, le jeu « Inserjeunes Apprentissage par centre de formation d'apprentis (CFA) » (Ministères de l'Éducation nationale) peut compléter."
  },
  "criteres": [
    "Cite le jeu de la Dares (identifiant 617a9e0887c6d1cab5c3d281)",
    "Donne le format xlsx et l'année 2018-2019 d'après la liste des ressources"
  ]
}
```

### Sortie (statut ok)

```text
**Jeu de données**  
- **Titre** : *Listes des centres de formation d'apprentis*  
- **Producteur** : Dares – statistiques Travail  
- **Date de dernière mise à jour** : non spécifiée dans le résultat (consultez le lien direct pour le calendrier exact)  
- **Format** : données tabulaires (CSV / XLSX) – contient les informations suivantes pour chaque centre : adresse, nombre d'élèves, taux d'insertion, taux de rupture par spécialité.  

**Année scolaire / période**  
- Les données sont fournies pour **l'année scolaire** (par exemple, l'année 2024‑2025) pour laquelle le jeu de données a été créé.  
- Vous pouvez consulter le lien direct (https://www.data.gouv.fr/datasets/listes-des-centres-de-formation-dapprentis-adresse-nombre-deleves-taux-dinsertion-taux-de-rupture-par-specialite) pour afficher la description complète et voir la date de la dernière mise à jour, ce qui indique la période couverte par le jeu de données.

Sources citées :
- Listes des centres de formation d'apprentis  (adresse, nombre d'élèves, taux d'insertion, taux de rupture par spécialité) — https://www.data.gouv.fr/datasets/listes-des-centres-de-formation-dapprentis-adresse-nombre-deleves-taux-dinsertion-taux-de-rupture-par-specialite
```

### Contrôles automatiques

```text
{
  "appariement": [
    0,
    null
  ],
  "appels_attendus": 2,
  "appels_valides": 1,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": true
}
```

### Verdicts

Aucun verdict.

## RD-036 (RD, facile)

### Entrée

```text
Un médecin de notre établissement se dit accrédité par la Haute Autorité de santé. Existe-t-il sur data.gouv.fr une liste des médecins accrédités par la HAS ? Donne-moi le nom du jeu de données, son producteur et le lien.

Options de la demande :
{
  "mode": "connecte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": {
    "jeu_principal": {
      "id": "602eaa18c7db5ddb8b0cc547",
      "titre": "Médecins accrédités par la HAS",
      "producteur": "Haute Autorité de santé",
      "url": "https://www.data.gouv.fr/datasets/medecins-accredites-par-la-has"
    },
    "texte": "Oui : le jeu « Médecins accrédités par la HAS » (identifiant 602eaa18c7db5ddb8b0cc547), produit par la Haute Autorité de santé, est disponible sur data.gouv.fr : https://www.data.gouv.fr/datasets/medecins-accredites-par-la-has."
  },
  "criteres": [
    "Cite le jeu « Médecins accrédités par la HAS » (identifiant 602eaa18c7db5ddb8b0cc547)",
    "Donne le producteur (Haute Autorité de santé) et le lien data.gouv.fr",
    "Ne présente pas les jeux de publications de la HAS comme la réponse"
  ]
}
```

### Sortie (statut ok)

```text
<tool_call>
{"name": "get_dataset_info", "arguments": {"dataset_id": "602eaa18c7db5ddb8b0cc547"}}
</tool_call>

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "appariement": [
    0
  ],
  "appels_attendus": 1,
  "appels_valides": 1,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": true
}
```

### Verdicts

Aucun verdict.

## RD-040 (RD, difficile)

### Entrée

```text
Je voudrais interroger directement en ligne, sans le télécharger, le fichier FINESS des établissements sanitaires et sociaux (extraction non géolocalisée) publié sur data.gouv.fr. Est-il interrogeable via l'API tabulaire de data.gouv.fr ? Si ce n'est pas le cas, donne-moi la taille du fichier CSV et son URL de téléchargement.

Options de la demande :
{
  "mode": "connecte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": {
    "jeu_principal": {
      "id": "53699569a3a729239d2046eb",
      "titre": "FINESS Extraction du Fichier des établissements",
      "producteur": "Ministère des Solidarités et de la Santé",
      "url": "https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements"
    },
    "autres_jeux_cites_possibles": [
      {
        "id": "67e43007cd5e91b9fdcbc7b3",
        "titre": "Réexposition des données Finess",
        "producteur": "data.gouv.fr"
      }
    ],
    "texte": "Le fichier se trouve dans le jeu « FINESS Extraction du Fichier des établissements » du Ministère des Solidarités et de la Santé (identifiant 53699569a3a729239d2046eb) : c'est la ressource « Extraction Finess des Etablissements au 04/05/2026. » (identifiant 2ce43ade-8d2c-4d1d-81da-ca06c82abc68, format csv). Elle n'est pas disponible via l'API tabulaire (« Not available via Tabular API ») : il faut la télécharger. Taille : 34.1 MB. URL de téléchargement : https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv"
  },
  "criteres": [
    "Choisit la ressource non géolocalisée (2ce43ade-8d2c-4d1d-81da-ca06c82abc68), pas la version géolocalisée",
    "Indique que l'API tabulaire n'est pas disponible pour ce fichier, sans tenter de requête de données présentée comme réussie",
    "Donne la taille 34.1 MB et l'URL static.data.gouv.fr exactes"
  ]
}
```

### Sortie (statut ok)

```text
<tool_call>
{"name": "get_dataset_info", "arguments": {"dataset_id": "53699569a3a729239d2046eb"}}
</tool_call>

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "appariement": [
    0,
    null,
    null
  ],
  "appels_attendus": 3,
  "appels_valides": 1,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": true
}
```

### Verdicts

Aucun verdict.

## RE-002 (RE, facile)

### Entrée

```text
{
  "consigne": "Résume ce document en 200 mots au plus, pour un étudiant qui se renseigne à l'accueil.",
  "document": "Oui, un étudiant peut bénéficier (sous conditions) d'une aide au logement (APL ou ALF ou ALS) pour l'aider à payer son loyer. Oui, un étudiant peut bénéficier sous conditions d'une aide au logement pour l'aider à payer son loyer. Il existe 3 types d'aides au logement :\n- Aide personnalisée au logement (APL)\n- Allocation de logement familiale (ALF)\n- Allocation de logement sociale (ALS) .\nVous pouvez bénéficier de l'une de ces 3 aides si vous respectez les 4 conditions suivantes :\n- Vous êtes français, ou étranger avec un titre de séjour en cours de validité\n- Vous louez un logement décent\n- Vous n'avez pas de lien de parenté avec le propriétaire du logement\n- Vous avez de faibles ressources.\nDepuis le 1 er juillet 2026, si vous êtes étudiant ressortissant d'un pays hors Union européenne (UE), Espace économique européen (EEE) ou Suisse et possédez un titre de séjour délivré pour les études, vous pouvez bénéficier d’une aide au logement uniquement dans l'un des 3 cas suivants :\n- Vous percevez une bourse sur critères sociaux (du centre régional des œuvres universitaires et scolaires - Crous, ou une bourse régionale sanitaire et sociale alignée sur les critères sociaux)\n- Vous exercez une activité professionnelle\n- Vous êtes engagé dans un contrat d’apprentissage ou de professionnalisation .\nVous pouvez utiliser un simulateur pour avoir une estimation du montant de l'aide au logement auquel vous pouvez prétendre : (Attention: Si vos parents perçoivent des allocations familiales et que vous demandez une aide au logement, vous n'êtes plus considéré à la charge de vos parents au sens des prestations familiales . Leurs allocations peuvent diminuer, voire être supprimées. Vous devez donc choisir entre bénéficier d'une aide au logement ou rester à la charge de vos parents .)\nVotre demande d'aide au logement doit être faite en ligne : Il est recommandé de faire votre demande d'aide au logement dès l'installation dans votre logement. En cas de colocation, chaque colocataire peut bénéficier d'une aide au logement. Il faut alors que chacun fasse sa propre demande à son nom. Le calcul de l'aide au logement prend en compte la part de loyer versée par chacun. (À savoir: Pour plus d'informations, vous pouvez appeler le numéro dédié aux aides au logement étudiant.)\nLe 1 er paiement de l'aide au logement est généralement effectué 2 mois après la demande. Exemple: Si la demande est faite en février, votre droit est ouvert en mars et le 1 er paiement s'effectue début avril. (À noter: La garantie Visale , l'avance Loca-Pass (aides pour accéder à un logement) et l'aide Mobili-Jeune (aide pour payer son loyer) sont cumulables avec l'APL, l'ALF ou l'ALS, à condition de respecter les critères d'attribution de chaque dispositif .)\n\nVoici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Par téléphone",
  "nb_mots": 449
}

Options de la demande :
{
  "longueur_demandee": "moyenne",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "points_cles_reference": [
    {
      "ref": "P1",
      "texte": "Un étudiant peut, sous conditions, bénéficier de l'APL, de l'ALF ou de l'ALS"
    },
    {
      "ref": "P2",
      "texte": "Conditions : être français ou titulaire d'un titre de séjour valide, louer un logement décent, sans lien de parenté avec le propriétaire, avoir de faibles ressources"
    },
    {
      "ref": "P3",
      "texte": "Depuis le 1er juillet 2026, l'étudiant hors UE, EEE ou Suisse avec un titre de séjour pour études n'y a droit que s'il est boursier sur critères sociaux, s'il travaille ou s'il est en apprentissage ou en contrat de professionnalisation"
    },
    {
      "ref": "P4",
      "texte": "Si les parents perçoivent des allocations familiales, l'étudiant qui demande l'aide n'est plus à leur charge : leurs allocations peuvent baisser ou être supprimées, il faut choisir"
    },
    {
      "ref": "P5",
      "texte": "Demande en ligne dès l'installation ; en colocation, une demande par colocataire, selon sa part de loyer"
    },
    {
      "ref": "P6",
      "texte": "1er paiement en général 2 mois après la demande"
    },
    {
      "ref": "P7",
      "texte": "Cumul possible avec Visale, Loca-Pass et Mobili-Jeune"
    }
  ],
  "longueur_demandee": "moyenne"
}
```

### Sortie (statut ok)

```text
L'aide au logement est une aide financière disponible pour les étudiants afin de les aider à payer leur loyer. Il existe trois types d'aides au logement : l'aide personnalisée au logement (APL), l'allocation de logement familiale (ALF) et l'allocation de logement social (ALS). Pour bénéficier de l'une de ces aides, les étudiants doivent répondre à quatre conditions : être français ou étranger avec un titre de séjour en cours de validité, louer un logement décent, ne pas avoir de lien de parenté avec le propriétaire du logement et avoir de faibles ressources. Depuis le 1er juillet 2026, les étudiants ressortissants d'un pays hors UE, Espace économique européen ou Suisse et possédant un titre de séjour délivré pour les études peuvent également bénéficier de l'aide au logement dans certains cas. Les étudiants peuvent utiliser un simulateur pour estimer le montant de l'aide au logement qu'ils peuvent prétendre à. La demande d'aide au logement doit être faite en ligne et le premier paiement est généralement effectué 2 mois après la demande.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "moyenne",
  "mots": 167,
  "plafond_mots": 200,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé déforme la règle de 2026 : « peuvent également bénéficier de l'aide au logement dans certains cas » présente comme une ouverture ce que le document formule comme une restriction (« uniquement dans l'un des 3 cas suivants »).
- `presence_elements` :
  - P1 : 1 — Le résumé indique que l'aide au logement est disponible pour les étudiants et cite l'APL, l'ALF et l'ALS, avec des conditions.
  - P2 : 1 — Les quatre conditions sont reprises : nationalité ou titre de séjour valide, logement décent, absence de lien de parenté, faibles ressources.
  - P3 : 0 — Le résumé mentionne la date et le public visé, mais omet les trois cas (boursier, activité professionnelle, apprentissage ou professionnalisation) et inverse le caractère restrictif de la règle.
  - P4 : 0 — L'avertissement sur la perte de la qualité d'enfant à charge et sur la baisse des allocations familiales des parents est absent.
  - P5 : 0 — Seule la demande en ligne est mentionnée ; la recommandation de la faire dès l'installation et la règle de colocation (une demande par colocataire) sont absentes.
  - P6 : 1 — « le premier paiement est généralement effectué 2 mois après la demande ».
  - P7 : 0 — Le cumul avec Visale, Loca-Pass et Mobili-Jeune n'est pas mentionné.
- Inventions : Formulation « peuvent également bénéficier de l'aide au logement dans certains cas », qui transforme une restriction (« uniquement ») en extension du droit
- Confiance : haute

**Juge second** : juge

- `fidelite` : 1 — Aucune information absente du document ni déformée, toutes les affirmations sont fidèles à l'entrée.
- `presence_elements` :
  - P1 : 1 — Présent : mention des trois types d'aides (APL, ALF, ALS) et de leur accessibilité sous conditions.
  - P2 : 1 — Présent : les quatre conditions (nationalité/titre de séjour, logement décent, absence de lien de parenté, faibles ressources) sont citées.
  - P3 : 0 — Absent : la condition spécifique pour les étudiants hors UE/EEE/Suisse (boursier, activité professionnelle, apprentissage) n'est pas détaillée.
  - P4 : 0 — Absent : l'impact sur les allocations familiales des parents n'est pas mentionné.
  - P5 : 0 — Absent : la précision sur la demande en ligne dès l'installation et les modalités pour la colocation ne sont pas incluses.
  - P6 : 1 — Présent : le délai de 2 mois pour le premier paiement est mentionné.
  - P7 : 0 — Absent : le cumul avec Visale, Loca-Pass et Mobili-Jeune n'est pas évoqué.
- Inventions : aucune
- Confiance : haute

## RE-010 (RE, moyen)

### Entrée

```text
{
  "consigne": "Résume ce document en 200 mots au plus, pour la famille d'une personne âgée.",
  "document": "Vous pouvez, sous conditions d'âge, de résidence et de perte d'autonomie, obtenir l' Apa . L'Apa sert à payer (en totalité ou en partie) soit les dépenses nécessaires pour rester à votre domicile ( Apa à domicile ), soit le tarif dépendance de l'établissement médico-social (exemple : Ehpad ) où vous vivez ( Apa en établissement) . Nous vous présentons les informations à connaître. Les règles sont différentes, selon que vous faites une demande d'Apa à domicile ou une demande d'Apa en établissement :\n\nVoici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Qu'est-ce que l'Apa à domicile ?\n- Quelles sont les conditions pour percevoir l'Apa à domicile ?\n- Comment demander l'Apa à domicile ?\n- Comment est étudiée la demande d'Apa à domicile ?\n- Quel est le montant de l'Apa à domicile ?\n- Comment est versée l'Apa à domicile ?\n- L’Apa à domicile peut-elle être suspendue ?\n- Comment rembourser un trop-perçu d’Apa ?\n- Y a t-il récupération sur succession de l’Apa ?\n- Quelle démarche faut-il faire après la décision d'attribution de l'Apa à domicile ?\n- Peut-on demander la révision du montant de l'Apa ?\n- Que faire en cas de litige concernant l'Apa ?\n- Quelles sont les conditions pour percevoir l'Apa en établissement ?\n- Comment demander l'Apa en établissement ?\n- Comment est étudiée la demande d'Apa en établissement ?\n- Quel est le montant de l'Apa en établissement ?\n- Comment est versée l'Apa en établissement ?\nL'Apa sert à payer (en totalité ou en partie) les dépenses nécessaires pour vous permettre de rester à votre domicile. Elle est versée par les services du département. Vidéo : Qu'est-ce que l'Apa ? CNSA - Apa: www.pour-les-personnes-agees.gouv.fr, site de la Caisse nationale de la solidarité pour l'autonomie (CNSA) Lucien ressent des difficultés dans ses tâches quotidiennes. Il fait une demande d'APA (allocation personnalisée d'autonomie). Une professionnelle du conseil départemental vient évaluer ses besoins et sa situation chez lui. Caisse nationale de solidarité pour l'autonomie (CNSA)\nVous devez respecter 4 conditions :\nVous devez être âgé d'au moins 60 ans.\nVous devez être dans une situation de perte d'autonomie (besoin d'aide pour accomplir les actes de la vie courante, ou état de santé nécessitant une surveillance constante). La perte d'autonomie se mesure à l'aide de la grille Aggir. Cette grille définit plusieurs degrés de perte d'autonomie, allant du Gir 1 (perte d'autonomie la plus forte) au Gir 6 (perte d'autonomie la plus faible). Seule la personne classée en Gir 1, Gir 2, Gir 3 ou Gir 4 peut obtenir l'Apa.\nVous devez résider en France de façon stable et régulière :\n- Soit à votre domicile\n- Soit au domicile d'un proche qui vous héberge\n- Soit chez un accueillant familial\n- Soit dans une résidence autonomie (anciennement appelé foyer-logement )\nSi vous êtes étranger, vous devez avoir une carte de résident ou un titre de séjour.\nIl n'est pas possible de recevoir l'Apa lorsque l'on reçoit au moins l'une des prestations suivantes :\n- Allocation simple d'aide sociale pour les personnes âgées\n- Aides des caisses de retraite\n- Aide financière pour rémunérer une aide à domicile\n- Prestation de compensation du handicap (PCH)\n- Majoration pour aide constante d'une tierce personne\n- Prestation complémentaire pour recours à tierce personne (PCRTP) . Mais la personne qui reçoit la PCRTP peut déposer un dossier de demande d'Apa , pour pouvoir ensuite choisir, entre ces 2 aides, celle qui lui convient le mieux.\nSelon votre département, vous pouvez faire la demande en ligne ou avec un formulaire. Pour le savoir, indiquez votre numéro de département ou votre code postal : (À savoir: Si vous avez changé de département depuis moins de 3 mois, ou si vous résidez en résidence autonomie, ou si vous vivez chez un accueillant familial, vous devez faire votre demande auprès de votre ancien lieu de résidence.)\n\nCas En ligne: Si votre département permet la demande en ligne, vous devez utiliser le téléservice suivant :\nCas Avec un formulaire: Si votre département permet de faire la demande avec un formulaire, vous devez utiliser le cerfa n°16301 :\nVous devez fournir les justificatifs suivants :\n- Photocopie de votre carte d'identité (recto et verso), de votre passeport ou du livret de famille, ou, si vous êtes étranger hors UE , EEE et Suisse, photocopie de votre carte de résident ou du titre de séjour en cours de validité\n- Photocopie de votre dernier avis d'imposition ou de non-imposition sur le revenu\n- Relevé d'identité bancaire (Rib)\n- Photocopie de votre dernier avis d'imposition de taxe foncière (dans certains cas)\n(À noter: Le dossier de demande d'Apa permet également de faire une demande simplifiée de carte mobilité inclusion (CMI) .)\nLes services du département ont 10 jours pour accuser réception de votre dossier. Si votre dossier est incomplet, les services du département vous demanderont les documents manquants. Si votre situation présente un caractère d'urgence d'ordre médical ou social (modification de l'état de santé, de l'environnement social...), l'Apa forfaitaire peut vous être attribuée en urgence et provisoirement. Elle est de 1 040,16 €. Pour connaître la démarche à accomplir, renseignez-vous auprès des services du département.",
  "nb_mots": 796
}

Options de la demande :
{
  "longueur_demandee": "moyenne",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "points_cles_reference": [
    {
      "ref": "P1",
      "texte": "L'Apa, versée par le département, finance tout ou partie des dépenses pour rester à domicile ou le tarif dépendance en établissement"
    },
    {
      "ref": "P2",
      "texte": "Apa à domicile : avoir au moins 60 ans, être classé en Gir 1 à 4 (grille Aggir) et résider en France de façon stable et régulière"
    },
    {
      "ref": "P3",
      "texte": "Non cumulable notamment avec la PCH, les aides des caisses de retraite ou la majoration pour tierce personne (choix possible entre PCRTP et Apa)"
    },
    {
      "ref": "P4",
      "texte": "Demande en ligne ou par cerfa n°16301 selon le département, avec pièce d'identité, dernier avis d'imposition, RIB et parfois avis de taxe foncière"
    },
    {
      "ref": "P5",
      "texte": "Accusé de réception sous 10 jours ; Apa forfaitaire provisoire de 1 040,16 € en cas d'urgence"
    }
  ],
  "longueur_demandee": "moyenne"
}
```

### Sortie (statut ok)

```text
L'Apa est une allocation personnalisée d'autonomie destinée aux personnes âgées qui ont des difficultés à mener leur vie quotidienne. Pour percevoir cette allocation, les personnes concernées doivent remplir certaines conditions, notamment être âgées d'au moins 60 ans, avoir une perte d'autonomie constatée par une évaluation professionnelle, et résider en France de manière stable. Les demandes peuvent être effectuées en ligne ou avec un formulaire, selon le département. Les documents à fournir incluent une photocopie de la carte d'identité, du passeport, du livret de famille, ainsi que des relevés financiers et des justificatifs de situation. Les demandes sont examinées par les services du département, qui ont un délai de réponse de 10 jours. Si la situation est urgente, une allocation forfaitaire peut être attribuée en urgence.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "moyenne",
  "mots": 125,
  "plafond_mots": 200,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé déforme le délai : « qui ont un délai de réponse de 10 jours », alors que le document prévoit 10 jours pour accuser réception du dossier. Il remplace aussi les pièces justificatives précises par des « relevés financiers et des justificatifs de situation », qui ne figurent pas dans le document.
- `presence_elements` :
  - P1 : 0 — Le résumé ne précise ni que l'Apa est versée par le département, ni qu'elle finance tout ou partie des dépenses à domicile ou le tarif dépendance en établissement.
  - P2 : 0 — L'âge de 60 ans et la résidence stable sont cités, mais la condition de classement en Gir 1 à 4 (grille Aggir) est absente : elle est remplacée par une vague « évaluation professionnelle ».
  - P3 : 0 — Aucune mention des prestations non cumulables (PCH, aides des caisses de retraite, majoration pour tierce personne) ni du choix possible entre PCRTP et Apa.
  - P4 : 0 — La demande en ligne ou par formulaire et la pièce d'identité sont citées, mais il manque le cerfa n°16301, l'avis d'imposition, le RIB et l'avis de taxe foncière, remplacés par des formulations vagues.
  - P5 : 0 — Le délai de 10 jours est présenté à tort comme un délai de réponse, et le montant de 1 040,16 € de l'Apa forfaitaire provisoire est absent.
- Inventions : Les services du département « ont un délai de réponse de 10 jours » (le document parle d'un accusé de réception sous 10 jours); Documents à fournir : « des relevés financiers et des justificatifs de situation » (non mentionnés dans le document)
- Confiance : haute

## RE-015 (RE, difficile)

### Entrée

```text
{
  "consigne": "Fais un résumé détaillé de ce document, en 400 mots au plus, pour les élus de la commission des finances.",
  "document": "Les communes ou les EPCI peuvent instituer une taxe de séjour au réel (due par les résidents occasionnels) ou au forfait (due par les logeurs ou hôteliers qui la récupèrent sur leurs clients). La décision doit être prise avant le 1 er juillet pour être applicable à compter du 1 er janvier de l’année suivante. La décision détermine aussi les critères de la taxe, tels que la période de perception (saison touristique) ou le montant applicable selon la nature et le classement de l'hébergement.\n\nVoici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Hébergements concernés\n- Critères de la taxe au réel ou au forfait\n- Tarifs\n- Déclaration et paiement\nLes hébergements taxés sont :\n- Chambre d'hôtes\n- Hébergement de plein air (camping, caravanage, aires de camping-cars et parcs de stationnement touristique)\n- Hôtel de tourisme\n- Meublé de tourisme\n- Palace\n- Port de plaisance\n- Résidence de tourisme\n- Village de vacances.\nPour être applicable, la taxe doit avoir été instituée par une délibération du conseil municipal ou de l'organe délibérant de l'EPCI. Le conseil municipal ou l'organe délibérant ne peut pas exempter une nature ou une catégorie d'hébergement à titre payant.\nC'est la délibération du conseil municipal ou de l'organe délibérant instituant la taxe de séjour qui en détermine les conditions d'application, soit au réel soit au forfait.\nConditions d'application de la taxe de séjour au réel ou au forfait:\n|  | Taxe au réel | Taxe au forfait | \n| - | - | - | \n| Redevables | Personne non domiciliée dans la commune ou sur le territoire de l'EPCI, qui séjourne dans un hébergement marchand | Logeur, hôtelier et propriétaire qui héberge à titre onéreux des personnes de passage | \n| Mode de calcul | Au nombre de nuitées effectuées | Indépendante du nombre réel de personnes hébergées. Taxe assise sur la capacité d'accueil (nombre de personnes que l'établissement peut accueillir), à laquelle est appliquée un abattement compris entre 10 % et 80 % . L'abattement est fonction de la durée d'ouverture de l'établissement | \n| Exonération | Personne âgée de moins de 18 ans Titulaire d'un contrat de travail saisonnier employé dans la commune Bénéficiaire d'un hébergement d'urgence ou d'un relogement temporaire Personne occupant des locaux dont le loyer est inférieur à un montant déterminé par le conseil municipal |  | \n| Mention sur la facture remise au client | Obligatoire Doit être distincte du prix de la chambre (taxe non incluse dans le prix de la chambre) | Non obligatoire Si la taxe est répercutée sur le prix de l'hébergement, l'hébergeur peut faire figurer sur la facture la mention taxe de séjour forfaitaire comprise | \n| TVA | Non incluse dans la base d'imposition de la TVA, car le logeur est collecteur de la taxe et doit l'intégrer dans sa facture au client | Incluse dans la base d'imposition à la TVA du logeur, car la taxe est intégrée au prix de vente |\nAvant le début de la période de perception (correspondant à la saison touristique), les tarifs de la taxe au réel ou forfaitaire sont fixés par délibération du conseil municipal, ou de l'organe délibérant de l' EPCI. Mais ces tarifs doivent être compris entre un tarif minimal (tarif plancher) et un tarif maximal (tarif plafond) pour chaque catégorie d'hébergement sur la base du classement officiel des hébergements. La taxe doit être perçue par le logeur, avant le départ des personnes hébergées, même s'il a accepté un paiement différé du loyer. Par ailleurs, le conseil départemental peut instituer sur délibération une taxe additionnelle de 10 % à la taxe de séjour perçue dans le département. Elle est recouvrée selon les mêmes critères que la taxe de séjour à laquelle elle s'ajoute. Elle est reversée par la commune au département. Pour connaître le tarif de la taxe de séjour dans une commune, ainsi que les éventuelles taxes additionnelles, vous pouvez utiliser ce téléservice : Le détail du barème 2026 est également disponible sur la page suivante : Taxe de séjour touristique : quels sont les tarifs ?. (Attention: En Île-de-France , une taxe additionnelle de 200 % s'ajoute au tarif de la taxe de séjour. D’autres taxes régionales ou départementales additionnelles peuvent s’ajouter selon la commune. Elles sont indiquées dans le simulateur des tarifs par commune .)\nLe tarif de la taxe doit être affiché en mairie et chez le logeur ou chez l'intermédiaire chargé de percevoir la taxe (agence immobilière par exemple).\nLes conditions de déclaration et de paiement diffèrent selon le type de taxe de séjour :\n- pour la taxe au réel : les logeurs ou hôteliers assujettis doivent verser le montant de la taxe collectée au comptable local aux dates fixées par le conseil municipal ou l'organe délibérant de l'EPCI\n- pour la taxe forfaitaire : le logeur ou l'hôtelier doit adresser, au plus tard 1 mois avant la période de perception, une déclaration à la mairie, indiquant la nature de leur hébergement, la période d'ouverture ou de mise en location et la capacité d'accueil qui sert de base au calcul de la taxe. Le montant forfaitisé doit être versé au comptable local aux dates fixées par le conseil municipal ou l'organe délibérant.\nLes versements de la taxe peuvent avoir lieu une seule fois ou plusieurs fois dans l'année. Certaines mairies mettent en ligne ces formulaires de déclaration ou permettent d'effectuer la déclaration directement en ligne. (À vérifier sur le site internet de la mairie ou de l'EPCI, notamment Paris.) En cas d'absence de déclaration ou de retard de paiement, le maire ou le président de l'EPCI peut engager une procédure de taxation d'office, après mise en demeure. À défaut de régularisation, un avis de taxation d'office motivé est communiqué au déclarant défaillant 30 jours au moins avant la mise en recouvrement. Tout retard dans le versement donne lieu à l'application d'un intérêt de retard de 0,20 % par mois de retard. (Attention: la déclaration pour la taxe de séjour ne doit pas être confondue avec la déclaration obligatoire que doivent réaliser, avant le début de la location, auprès de leur mairie, les particuliers qui donnent en location tout ou partie de leur habitation personnelle au cours de la période de taxation ( chambre d'hôte , meublé de tourisme ). Sauf pour le meublé de tourisme, s'il s'agit de la résidence principale (logement occupé 8 mois minimum par an sauf obligation professionnelle, raison de santé ou cas de force majeure ).)",
  "nb_mots": 1015
}

Options de la demande :
{
  "longueur_demandee": "detaillee",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "points_cles_reference": [
    {
      "ref": "P1",
      "texte": "Les communes ou les EPCI peuvent instituer, par une délibération prise avant le 1er juillet pour l'année suivante, une taxe de séjour au réel (due par les résidents occasionnels) ou au forfait (due par les logeurs ou hôteliers) ; la délibération fixe notamment la période de perception et les montants"
    },
    {
      "ref": "P2",
      "texte": "Hébergements taxés : chambres d'hôtes, hébergements de plein air, hôtels de tourisme, meublés de tourisme, palaces, ports de plaisance, résidences de tourisme et villages de vacances ; aucune catégorie d'hébergement à titre payant ne peut être exemptée"
    },
    {
      "ref": "P3",
      "texte": "Taxe au réel : due par les personnes non domiciliées sur le territoire, calculée au nombre de nuitées, avec des exonérations (mineurs, saisonniers employés dans la commune, hébergement d'urgence ou relogement temporaire, loyer inférieur à un montant fixé) ; mention distincte obligatoire sur la facture ; hors base de TVA"
    },
    {
      "ref": "P4",
      "texte": "Taxe au forfait : due par les logeurs, assise sur la capacité d'accueil avec un abattement de 10 % à 80 % selon la durée d'ouverture ; incluse dans la base de TVA"
    },
    {
      "ref": "P5",
      "texte": "Les tarifs sont fixés par délibération avant la période de perception, entre un plancher et un plafond par catégorie selon le classement ; la taxe est perçue par le logeur avant le départ du client et le tarif est affiché en mairie et chez le logeur"
    },
    {
      "ref": "P6",
      "texte": "Le conseil départemental peut instituer une taxe additionnelle de 10 % ; en Île-de-France, une taxe additionnelle de 200 % s'ajoute"
    },
    {
      "ref": "P7",
      "texte": "La taxe est versée au comptable local aux dates fixées par la collectivité ; pour la taxe au forfait, une déclaration est adressée à la mairie au plus tard 1 mois avant la période de perception"
    },
    {
      "ref": "P8",
      "texte": "En cas d'absence de déclaration ou de retard, taxation d'office après mise en demeure (avis motivé 30 jours au moins avant le recouvrement) et intérêt de retard de 0,20 % par mois"
    }
  ],
  "longueur_demandee": "detaillee"
}
```

### Sortie (statut ok)

```text
La taxe de séjour est un instrument fiscal destiné à soutenir les communes et les EPCI dans la gestion des infrastructures touristiques et des services publics. Elle peut être appliquée à la fois au niveau du logement (taxe au réel) ou du logeur/hôtelier (taxe au forfait). Cette taxe est fixée avant le 1er juillet et est effective à partir du 1er janvier de l'année suivante. Les critères de perception, tels que la période de saison touristique ou le montant applicable, sont déterminés par le conseil municipal ou l'organe délibérant de l'EPCI.

Les hébergements concernés par cette taxe sont largement définis, notamment les chambres d'hôtes, les hébergements de plein air, les hôtels de tourisme, les palaces, les ports de plaisance, les résidences de tourisme, les villages de vacances, etc. La taxe doit être instituée par une délibération du conseil municipal ou de l'organe délibérant de l'EPCI et ne peut pas exempter une nature ou une catégorie d'hébergement à titre payant.

Pour être applicable, la taxe doit être déclarée et fixée par le conseil municipal ou l'organe délibérant, avec un tarif minimum et maximum déterminé pour chaque catégorie d'hébergement. Les conditions de perception, de calcul et de déclaration diffèrent selon le type de taxe. Pour la taxe au réel, le logeur ou hôtelier doit verser le montant collecté au comptable local avant le départ des personnes hébergées. Pour la taxe forfaitaire, une déclaration doit être adressée à la mairie avant la période de perception, indiquant la nature de l'hébergement, la période d'ouverture et la capacité d'accueil.

Les versements peuvent être effectués une fois ou plusieurs fois par année, avec des délais de déclaration et de paiement spécifiques. En cas de non-respect, des procédures de taxation d'office peuvent être engagées. Les montants et les détails de la taxe sont disponibles sur les sites de la mairie et de l'EPCI, et les informations sur les tarifs et les conditions de perception sont également fournies pour faciliter la compréhension et la gestion de cette fiscalité.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 330,
  "plafond_mots": 400,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé ajoute des informations absentes du document et en déforme d'autres. Il affirme que la taxe est « destinée à soutenir les communes et les EPCI dans la gestion des infrastructures touristiques ». Il écrit que le logeur doit « verser le montant collecté au comptable local avant le départ des personnes hébergées », alors que le document distingue la perception, faite avant le départ, du versement, fait aux dates fixées par la collectivité. Il présente enfin la taxe au réel comme appliquée « au niveau du logement » au lieu des résidents occasionnels.
- `presence_elements` :
  - P1 : 1 — Le résumé mentionne l'institution par les communes ou EPCI, la décision avant le 1er juillet pour le 1er janvier suivant, les deux modes et la fixation de la période et du montant par délibération, même si le redevable de la taxe au réel est déformé.
  - P2 : 1 — La liste des hébergements est quasi complète (les meublés de tourisme sont remplacés par « etc. ») et l'interdiction d'exempter une catégorie à titre payant est reprise.
  - P3 : 0 — Le calcul au nombre de nuitées, les exonérations, la mention distincte sur la facture et l'exclusion de la base de TVA sont absents.
  - P4 : 0 — L'assiette sur la capacité d'accueil avec un abattement de 10 % à 80 % et l'inclusion dans la base de TVA sont absentes.
  - P5 : 0 — Seul le tarif minimum et maximum par catégorie est cité. La perception avant le départ est déformée en versement au comptable, et l'affichage du tarif comme la fixation avant la période de perception sont absents.
  - P6 : 0 — Le résumé ne mentionne ni la taxe additionnelle départementale de 10 % ni celle de 200 % en Île-de-France.
  - P7 : 0 — Le versement aux dates fixées par la collectivité est remplacé par un versement « avant le départ », et le délai d'un mois pour la déclaration de la taxe au forfait est omis.
  - P8 : 0 — Seule la taxation d'office est évoquée. La mise en demeure, l'avis motivé 30 jours avant le recouvrement et l'intérêt de retard de 0,20 % par mois sont absents.
- Inventions : La taxe de séjour est un instrument fiscal destiné à soutenir les communes et les EPCI dans la gestion des infrastructures touristiques et des services publics.; Elle peut être appliquée à la fois au niveau du logement (taxe au réel); Pour la taxe au réel, le logeur ou hôtelier doit verser le montant collecté au comptable local avant le départ des personnes hébergées.; Les montants et les détails de la taxe sont disponibles sur les sites de la mairie et de l'EPCI
- Confiance : moyenne
