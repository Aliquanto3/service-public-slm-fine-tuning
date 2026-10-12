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
Si votre enfant est nouveau dans un établissement, vous devez participer à une réunion d’information dans les jours **suivant** la rentrée scolaire. Des réunions peuvent aussi être **organisées** au cours de l’année scolaire, notamment pour vous informer sur la situation de la classe, sur une procédure spécifique ou sur les possibilités d’orientation. Si votre enfant est en grande difficulté scolaire, son établissement peut également vous **convoquer** à des réunions pour envisager ensemble des solutions. Si vous rencontrez un problème lié à la pédagogie, adressez-vous au professeur principal de la classe. Si votre problème concerne les absences et les questions de comportement, adressez-vous au conseiller principal d’éducation (CPE). Le chef d’établissement et les enseignants doivent faire le nécessaire pour répondre à vos demandes d’information et de rendez-vous. Toute réponse négative doit présenter les motifs.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 3,
  "fautes": 6,
  "fautes_corrigees": [
    false,
    false,
    false,
    true,
    true,
    true
  ],
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 1,
  "mots_texte": 135,
  "rappel": 0.5,
  "taux_hors_faute": 0.0074
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
**Note à l'attention des agents du service urbanisme**

**Objet : modalités du télétravail à compter du 1er décembre 2026**

À la suite de la réunion du comité social territorial du 15 octobre, le télétravail **sera** ouvert aux agents du service urbanisme dont les missions le permettent. Chaque agent pourra télétravailler un jour par semaine, **choisi** en accord avec son responsable. Les jours de permanence au guichet, le mardi et le jeudi, **ne pourront pas être télétravaillés**.

Les demandes devront être **adressées** au service des ressources humaines avant le 13 novembre, au moyen du formulaire joint. Un ordinateur portable et un casque **seront remis** à chaque agent dont la demande aura été **acceptée**. Les agents s’engagent à rester joignables pendant les plages fixes, de 9 heures à 12 heures et de 14 heures à 16 heures.

Une période d’adaptation de trois mois est prévue. À l’issue de cette période, un bilan **sera** **fais** avec chaque agent afin de vérifier que l’organisation retenue convient **à** la fois à l’agent et au service.

*La direction générale des services*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 0,
  "fautes": 8,
  "fautes_corrigees": [
    false,
    false,
    false,
    false,
    false,
    false,
    false,
    false
  ],
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 9,
  "mots_texte": 174,
  "rappel": 0.0,
  "taux_hors_faute": 0.0517
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
Si vous êtes admis à un concours d'accès à la fonction publique et si vous étiez **avant** dirigeant d'une société ou d'une association à but lucratif, vous pouvez continuer à exercer cette activité de dirigeant pendant **un an**, renouvelable une fois, à partir de votre recrutement dans la fonction publique. Cela s'applique aussi si vous êtes recruté en **temps** que contractuel dans la fonction publique. Vous devez présenter une déclaration écrite à votre autorité hiérarchique **à partir de votre nomination** en tant que fonctionnaire stagiaire ou avant la signature de votre contrat. Votre déclaration mentionne la forme et l'objet social de l'entreprise ou de l'association, son secteur et sa branche d'activité. La poursuite de cette activité de dirigeant doit être compatible avec vos obligations de service. Elle ne doit pas porter atteinte au fonctionnement normal, à l'indépendance, à la neutralité du service ou aux principes déontologiques. Cette activité ne doit pas non plus vous placer dans une situation de conflit d'intérêts.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 9,
  "fautes": 12,
  "fautes_corrigees": [
    true,
    false,
    true,
    true,
    true,
    false,
    false,
    true,
    true,
    true,
    true,
    true
  ],
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 3,
  "mots_texte": 159,
  "rappel": 0.75,
  "taux_hors_faute": 0.0189
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
**Compte rendu du 1ᵉʳ conseil d’école de l’école élémentaire du Moulin-Neuf – Sermoise-la-Haute**
*Jeudi 8 octobre 2026, salle polyvalente – 18h*

---

**Participants présents :**
- Mme Dufresne, directrice (présidente)
- Enseignants : M. Arnaud (CP), Mme Lemaire (CE1, secrétaire de séance), Mme Sow (CE2-CM1), M. Perrin (CM2)
- Représentants des parents élus : Mme Caron, M. Delattre, Mme Aït Ali, M. Brun (suppléant)
- Mairie : M. Vasseur (adjoint aux affaires scolaires)
- DDEN : Mme Roussel

**Participants absents :**
- M. Kieffer (IEN), Mme Joubert (parent titulaire)

---

### **Points abordés**

1. **Élections des représentants de parents**
   - Participation : 41 % (contre 38 % l’année précédente), avec une seule liste élue.
   - La directrice remercie les parents pour leur implication.

2. **Effectifs et organisation scolaire**
   - Nombre d’élèves : 112 (contre 121 l’an dernier).
   - Cinq classes, dont un double niveau (CE2-CM1, 24 élèves).
   - Absence de nouvelle attribution d’AESH malgré deux notifications de la MDPH, demande renouvelée auprès de l’IEN.

3. **Modification du règlement intérieur**
   - Proposition d’ouverture du portail à **8 h 20** (au lieu de 8 h 25) pour réduire la congestion sur le trottoir.
   - Demande de Mme Aït Ali d’ouvrir à **8 h 15**, mais les enseignants s’y opposent en raison d’un service de surveillance nécessaire.
   - **Décision** : adoption du règlement avec ouverture à **8 h 20**, par unanimité.
   - Transmission aux familles via le cahier de liaison et l’ENT avant le **vendredi 16 octobre**.

4. **Sécurité et PPMS**
   - Rappel de l’exercice incendie du **22 septembre**, évacuation en **2 minutes 40**.
   - **Exercice PPMS « attentat-intrusion »** prévu le **jeudi 19 novembre** (date confirmée par la directrice ; les familles seront prévenues la veille).

5. **Projets de l’année scolaire**
   - **Classe de découverte CM2** (22 élèves, 3 jours en mer en mai 2027) :
     - Coût estimé à **9 800 €** (dont 2 500 € de la coopérative scolaire et 1 980 € des familles).
     - Manque environ **5 300 €** supplémentaires.
     - M. Vasseur indique que la demande sera étudiée au **budget 2027**, sans engagement définitif.
     - **Décision** : le projet est maintenu à condition que la subvention municipale soit obtenue.
     - **Action** : M. Perrin doit déposer la demande de subvention en mairie avant le **30 novembre**.

   - **Marché de Noël de l’école** :
     - **Date** : vendredi 11 décembre, 16 h 30, dans la cour.
     - Bénéfices reversés à la coopérative scolaire.
     - **Décision** : accord du conseil.
     - **Action** : Mme Caron coordonne les stands avec les parents élus.

6. **Travaux et bâtiment**
   - **Chauffage de la classe de CE2-CM1** :
     - Température matinale à **16 °C**.
     - **Action** : intervention du service technique prévue pendant les vacances de la Toussaint.
   - **Demande d’abri vélos** :
     - Mairie : prise de note, pas de prévision concrète.

7. **Cantine et périscolaire**
   - Questions sur le bruit à la cantine.
     - M. Vasseur évoque des panneaux acoustiques pour l’année prochaine, sans chiffrage précis.
     - **Aucune décision prise**.

8. **Questions des parents**
   - **Pédibus vers le lotissement des Prés** :
     - Idée soutenue par tous, mais **aucun parent ne se porte volontaire** pour organiser la démarche ce soir.
     - **À réexaminer**.
   - **Demande de ralentisseur sur la rue de l’Église aux heures de sortie** :
     - Rue départementale, la commune doit saisir le département.
     - **M.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « Décision : adoption du règlement avec ouverture à 8 h 20, par unanimité. »
  - D2 : 1 — « Exercice PPMS « attentat-intrusion » prévu le jeudi 19 novembre […] les familles seront prévenues la veille ».
  - D3 : 1 — Le marché de Noël du vendredi 11 décembre à 16 h 30 dans la cour figure avec les bénéfices pour la coopérative et l'« accord du conseil ».
  - A1 : 0.5 — La transmission aux familles avant le vendredi 16 octobre est mentionnée, mais le responsable (Mme Dufresne) n'est pas indiqué.
  - A2 : 1 — « M. Perrin doit déposer la demande de subvention en mairie avant le 30 novembre ».
  - A3 : 1 — « Mme Caron coordonne les stands avec les parents élus » (échéance non fixée dans les notes).
  - A4 : 1 — « intervention du service technique prévue pendant les vacances de la Toussaint ».
  - A5 : 0 — La sortie, tronquée en section 8, ne mentionne pas la rédaction ni la diffusion du PV par Mme Lemaire sous 15 jours.
- `absence_invention` : 1 — Aucun élément inventé : les pièges sont correctement traités (112 élèves, 8 h 15 non retenu, classe de découverte conditionnée, abri vélos, panneaux acoustiques et pédibus non décidés).
- `structure` : 0 — Seules les sections Participants et Points abordés existent ; il n'y a pas de sections Décisions et Actions distinctes, et la sortie est tronquée (« **M. »).
- Inventions : aucune
- Confiance : haute

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
**Compte rendu de la commission d’appel d’offres (CAO) du SIAEP de la Haute-Sorelle**

**Objet** : Séance du jeudi 1er octobre 2026 – Décisions relatives aux appels d’offres pour la fourniture et la pose de compteurs d’eau, avis sur l’avenant n°2 du marché de réhabilitation du réservoir de la Butte, et points divers.

**Participants** :
**Membres à voix délibérative** (6 présents sur 6, quorum atteint) :
- M. Chaumont, 1er vice-président (président de séance)
- Mme Lebrun, M. Fabre, M. Guillot, Mme Teixeira
- M. Hamel (suppléant en remplacement de M. Pasquier)

**Voix consultative** :
- Mme Rivière (responsable marchés publics, rapporteure)
- M. Kessler (Hydraulis Conseil, AMO, présent uniquement pour le point 1)
- Représentant du service comptable public (SGC de Sorelle) – absent
- DDPP (concurrence) – non présente (courrier reçu sans observation)

---

### **Points abordés**

#### **1. Appel d’offres ouvert – Fourniture et pose de compteurs d’eau (2 lots)**
**Ordre du jour** : Attribution des lots 1 et 2.

**Lot 1 – Fourniture des compteurs (9 500 unités sur 4 ans)**
- **Offres reçues** : Quatre offres régulières évaluées selon les critères suivants (prix : 50 %, technique : 40 %, environnement : 10 %).
  - **Hydrocompt SAS** : Note 87,5/100 (estimation financière : 412 300 € HT sur 4 ans).
  - **Aqualis Mesure** : Note 82,1/100.
  - **Compteurs du Rhin** : Note 76,4/100.
  - **Metrisol** : Note 64,9/100 (prix bas mais délai de livraison de 16 semaines et faible valeur technique).
- **Débat** :
  - M. Fabre a souligné l’écart entre Metrisol et les autres offres, notamment en matière de garantie sur la durée de vie des piles radio.
  - M. Kessler a confirmé que la note technique de Metrisol (18/40) était insuffisante.
- **Décision** :
  - **Attribution du lot 1 à Hydrocompt SAS** (offre économiquement la plus avantageuse, unanimité).
  - **Actions** :
    - Envoi des courriers de rejet aux trois autres candidats dès le vendredi 2 octobre (responsable : Mme Rivière).
    - Notification du marché à Hydrocompt par Mme Rivière, **au plus tard le mardi 13 octobre** (délai de standstill respecté).

**Lot 2 – Pose des compteurs et têtes radio**
- **Offres reçues** :
  - **Réseaux Sorelle TP** : Offre irrégulière (DPGF non signée et absence de mémoire technique) → éliminée.
  - **Canalis Ouest** : Offre régulière mais **surévaluation de 31 %** (186 000 € HT contre une estimation initiale de 142 000 € HT).
- **Débat** :
  - M. Kessler a suggéré une négociation, mais Mme Rivière a rappelé qu’une telle procédure n’était pas applicable en appel d’offres ouvert.
  - Mme Teixeira a demandé si l’estimation initiale ne reflétait pas une hausse des coûts des raccordements (prix datés de 2025).
- **Décision** :
  - **Déclaration du lot 2 comme infructueux** (unanimité).
  - **Suite** :
    - **Nouvelle consultation** sur la base d’une estimation mise à jour (responsable : Mme Kessler).
    - **Relance d’un nouvel appel d’offres ouvert** avec mise à jour du DCE (responsable : Mme Rivière, à publier avant le **vendredi 6 novembre**).
    - **Mise à jour de l’estimation** par M. Kessler avant le **vendredi 23 octobre**.

---

#### **2. Avis sur l’avenant n°2 – Marché « réhabilitation du réservoir de la Butte »**
**Objet** : Travaux d’étanchéité supplémentaires (fissures sur la coupole après vid

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Le compte rendu mentionne « Attribution du lot 1 à Hydrocompt SAS (offre économiquement la plus avantageuse, unanimité) », avec la note de 87,5/100 et le montant de 412 300 € HT sur 4 ans.
  - D2 : 1 — Le compte rendu mentionne « Déclaration du lot 2 comme infructueux (unanimité) », avec l'offre irrégulière et l'offre de 186 000 € HT pour 142 000 € HT estimés.
  - D3 : 1 — La relance est présente : « Relance d'un nouvel appel d'offres ouvert avec mise à jour du DCE » et « estimation mise à jour ».
  - D4 : 0 — La sortie est tronquée au début du point 2 ; l'avis favorable sur l'avenant n° 2 et le vote (3 pour, 2 abstentions) sont absents.
  - A1 : 1 — Le compte rendu indique « Envoi des courriers de rejet aux trois autres candidats dès le vendredi 2 octobre (responsable : Mme Rivière) ».
  - A2 : 0.5 — Le responsable est correct, mais l'échéance est inversée : « au plus tard le mardi 13 octobre » au lieu de « pas avant le 13 octobre ».
  - A3 : 1 — Le compte rendu indique « Mise à jour de l'estimation par M. Kessler avant le vendredi 23 octobre ».
  - A4 : 1 — Le compte rendu indique « responsable : Mme Rivière, à publier avant le vendredi 6 novembre ».
  - A5 : 0 — Action absente : la sortie est tronquée avant cette action.
  - A6 : 0 — Action absente : la sortie est tronquée avant cette action.
  - A7 : 0 — Action absente : la sortie est tronquée avant cette action.
  - A8 : 0 — Action absente : la sortie est tronquée avant cette action.
- `absence_invention` : 0 — La formule « au plus tard le mardi 13 octobre » contredit les notes (pas avant le 13/10), « (responsable : Mme Kessler) » attribue une responsabilité inexistante à une personne mal nommée, et M. Fabre se voit prêter l'argument sur la garantie des piles radio, qui est en réalité de M. Kessler.
- `structure` : 0 — Seules les sections Participants et Points abordés existent ; il n'y a pas de sections Décisions et Actions distinctes, et la sortie est tronquée.
- Inventions : Notification à Hydrocompt « au plus tard le mardi 13 octobre » (les notes disent pas avant le 13/10); « Nouvelle consultation … (responsable : Mme Kessler) » : responsable inventé et personne mal nommée; M. Fabre aurait souligné la garantie sur la durée de vie des piles radio (propos de M. Kessler)
- Confiance : haute

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
**Compte rendu de la séance du Comité Social Territorial (CST) du 1er octobre 2026**

**Participants**
Présents :
- Collège des représentants de la collectivité : M. Castagnet (vice-président RH), Mme Ferrand, Mme Arnaud (DGA Ressources), M. Oudin (DRH).
- Collège des représentants du personnel : CGT (M. Rouvière, Mme Sissoko, M. Pallas), FO (Mme Escande, M. Vasseur), CFDT (Mme Thibaud, Mme Moulin), UNSA (M. Lhermite).
- Experts : M. Galmiche (DRM), Dr Kerbrat (médecin du travail), Mme Maréchal (conseillère de prévention).

**Points abordés**

1. **Approbation du procès-verbal du 2 juillet 2026**
   - Correction apportée par la FO : suppression de l’approbation du nouveau régime d’astreinte pour les agents de catégorie C du service des bâtiments, remplacée par une opposition à son extension.
   - Vote : Unanimité des deux collèges.

2. **Réorganisation du centre d’exploitation routière de Lauzières (fusion avec Montclar-d’Orbe)**
   - Modification du calendrier : report de la mise en œuvre au **1er mars 2027**.
   - Maintien du dépôt de sel de Lauzières sous réserve d’un diagnostic à transmettre avant le **10 décembre 2026**.
   - Avis du CST :
     - Collège employeur : Favorable (5 voix).
     - Collège du personnel : Défavorable (5 voix contre, 2 abstentions, 1 voix pour).
   - Décision : Le dossier sera soumis au président du département.
   - **Actions à mener** :
     - M. Galmiche : Transmettre l’étude anonymisée des temps de trajet avant le 10 décembre.
     - DRH : Organiser des entretiens individuels avec les 14 agents concernés avant le 30 novembre.
     - Mme Escande : Préparer une note pour que la FO vote contre en commission permanente si le sujet est repris.

3. **Modification de la charte du télétravail**
   - Nouveaux éléments : introduction d’un forfait annuel de 20 jours flottants sur demande, validé par le responsable, et un délai de prévenance de 48 heures pour l’annulation d’un jour de télétravail (sauf urgence).
   - Entrée en vigueur prévue au **1er janvier 2027**.
   - Avis du CST :
     - Collège employeur : Favorable (5 voix).
     - Collège du personnel : Favorable (5 voix pour, 3 abstentions).
   - **Actions à mener** :
     - M. Oudin : Publier la charte modifiée sur l’intranet avant le 1er décembre.
     - M. Oudin : Présenter un bilan d’application au CST de début 2028.

4. **Risques psychosociaux**
   - Résultats du baromètre social (mai-juin 2026) :
     - Charge de travail excessive : 54 % des répondants.
     - Violences externes : 41 % des agents (72 % dans les MDS).
     - Stress élevé : 29 % des répondants.
   - Propositions du plan de prévention :
     - Formation à la gestion des agressions pour 110 agents d’accueil des MDS (début novembre si validé).
     - Travail par direction sur la charge de travail.
     - Formation des encadrants sur les risques psychosociaux.
     - Mise à jour du DUERP avant le **31 mars 2027**.
   - **Visite de la MDS de Saint-Fréjus** : organisée le **20 octobre 2026** par Mme Maréchal.

5. **Plan de formation 2027**
   - Priorités : prévention des risques (agressions, RPS pour les encadrants), transition numérique, préparation aux concours et examens professionnels.
   - Budget : 640 000 € (hors cotisation CNFPT).
   - Disponibilité des formations : aucune le samedi, exception en mars pour les agents des routes.
   - **CACES** : 42 places prévues en 2027 (contre 28 cette année).
   - Décision : Avis favorable unanime. Transmission au CNFPT avant le **31 décembre 2026**.

6. **Questions diverses**
   - **Chauffage du bâtiment B (rue des Tanneurs)**

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0.5 — L'approbation unanime du PV est présente, mais la correction est déformée : l'approbation de la revalorisation des astreintes n'est pas mentionnée.
  - D2 : 1 — « report de la mise en œuvre au 1er mars 2027 » est bien indiqué.
  - D3 : 1 — L'avis des deux collèges est présent (employeur 5 pour ; personnel 5 contre, 2 abstentions, 1 pour), ainsi que la soumission au président du Département.
  - D4 : 1 — Le délai de prévenance de 48 heures, sauf urgence, est mentionné.
  - D5 : 0.5 — L'avis favorable, les votes et l'entrée en vigueur au 1er janvier 2027 sont présents, mais les 2 jours fixes maximum et le plafond de 3 jours par semaine manquent.
  - D6 : 0.5 — La visite du 20 octobre est citée, sans la composition de la délégation (Rouvière, Escande, Ferrand) ni la précision du matin.
  - D7 : 1 — « Avis favorable unanime » est indiqué, avec le budget de 640 000 € hors cotisation CNFPT.
  - A1 : 0 — La mise en ligne du PV corrigé d'ici fin octobre est absente.
  - A2 : 1 — « M. Galmiche : Transmettre l'étude anonymisée des temps de trajet avant le 10 décembre » est présent.
  - A3 : 0.5 — Les entretiens avant le 30 novembre sont attribués à la seule DRH ; M. Galmiche est omis comme co-responsable.
  - A4 : 0 — La transmission à M. Galmiche de la question sur le salage est absente.
  - A5 : 1 — « M. Oudin : Publier la charte modifiée sur l'intranet avant le 1er décembre » est présent.
  - A6 : 1 — « M. Oudin : Présenter un bilan d'application au CST de début 2028 » est présent.
  - A7 : 1 — « Visite... organisée le 20 octobre 2026 par Mme Maréchal » est présent.
  - A8 : 0 — La présentation du compte rendu de visite à la formation spécialisée du 19 novembre est absente.
  - A9 : 0 — La présentation des résultats détaillés par direction par le Dr Kerbrat est absente.
  - A10 : 0.5 — La mise à jour du DUERP avant le 31 mars 2027 est citée, mais sans responsable (Mme Maréchal).
  - A11 : 0 — Le chiffrage de la cellule d'écoute par Mme Arnaud est absent.
  - A12 : 0.5 — La transmission au CNFPT avant le 31 décembre est mentionnée, sans responsable (Mme Arnaud).
  - A13 : 0 — Les questions diverses sont tronquées : seul le titre « Chauffage du bâtiment B » apparaît, sans l'action ni l'échéance.
  - A14 : 0 — La demande de devis pour le parking des Halles est absente.
  - A15 : 0 — L'inscription du CET au CST du 10 décembre est absente.
- `absence_invention` : 0 — Le compte rendu invente « un diagnostic à transmettre avant le 10 décembre 2026 » pour le dépôt de sel, alors que la date du diagnostic est inconnue, ainsi que l'action « Mme Escande : Préparer une note pour que la FO vote contre en commission permanente ».
- `structure` : 0 — Il n'y a pas de sections distinctes « Décisions » et « Actions » : ces éléments sont dispersés dans les points abordés, et le document est tronqué.
- Inventions : Diagnostic du dépôt de sel « à transmettre avant le 10 décembre 2026 »; Action attribuée à Mme Escande : « Préparer une note pour que la FO vote contre en commission permanente »
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
**Compte rendu de réunion d’équipe – Médiathèque intercommunale La Filature**
*Date : mardi 15 septembre 2026*
*Lieu : Salle d’animation (avant ouverture au public)*
*Durée : 9h00 – 10h45*

---

### **Participants présents**
- C. Aubertin (directrice, animatrice)
- T. Fabre (responsable jeunesse)
- M. N’Diaye (responsable adultes + numérique)
- J. Leroux (accueil/prêt)
- S. Combes (responsable réseau des bibliothèques relais)
- Lucas P. (volontaire service civique, présent jusqu’à 10h)

**Excusés** : A. Gerbier (en congés)

---

### **Points abordés**

1. **Bilan de l’été (juillet-août)**
   - Fréquentation : **+8 % d’entrées** par rapport à 2025 (contre +12 % initialement évoqué pour les prêts).
   - Activités en plein air : 9 lectures, bonne participation sauf au plan d’eau (interruption liée à la pluie).
   - **Action** : Leroux rappelle le prestataire de l’automate de prêt n°2 avant le **vendredi 18/09**.

2. **Horaires – Ouverture le dimanche matin**
   - Proposition de Fabre : ouverture le dimanche matin (10h–13h) **au moins l’hiver**, avec demande de familles.
   - Opposition de Leroux : besoin de renforts avant d’envisager cette ouverture.
   - **Décision** : Pas de décision définitive. À réexaminer après le retour de Gerbier (date non précisée).

3. **Navette documentaire (bibliothèques relais)**
   - Changement de jour de passage : **jeudi → mercredi** (non applicable).
   - **Décision** : Passage du mercredi au jeudi à partir du **jeudi 1er octobre 2026**.
   - **Action** : Combes informe les 7 bibliothèques relais avant le **vendredi 25/09**.

4. **Désherbage et vente de livres**
   - Documents désherbés : ~1 200 depuis le printemps (romans abîmés, documents périmés).
   - Idée d’une vente le **samedi 17 octobre 2026** à 1 €/livre et 0,50 €/revue (recettes pour l’achat de jeux).
   - **Conditions** :
     - Délibération du conseil communautaire obligatoire (sortie d’inventaire + tarifs) le **mardi 29/09**.
     - **Si délibération votée** : vente prévue le 17/10.
     - **Sinon** : report.
   - **Actions** :
     - Aubertin finalise la délibération et l’envoie au secrétariat général avant le **vendredi 18/09**.
     - N’Diaye propose d’offrir le reste à une association (Emmaüs ?) – **non tranché**.

5. **Accueil des classes**
   - Trop de demandes le lundi, avec un seul accueillant.
   - **Décision** : À partir de la rentrée de la Toussaint, accueil des classes uniquement le **mardi et jeudi matin** (plus le lundi).
   - **Action** : Fabre envoie le nouveau planning aux écoles du territoire avant les vacances de la Toussaint.

6. **Mois du film documentaire (novembre)**
   - **Décision** : Participation avec deux projections-débats :
     - Vendredi 13 novembre 2026 à 20h
     - Vendredi 27 novembre 2026 à 20h *(correction de l’ordre du jour initial : 20h au lieu de 20h le 13/11)*
   - **Actions** :
     - N’Diaye réserve les films auprès de la médiathèque départementale avant le **vendredi 9 octobre**.
     - Lucas P. souhaite animer un débat – **à confirmer**.

---
### **Divers**
- **Abonnement presse en ligne** : Pas de budget 2026, éventuellement budget projet 2027 – **pas de décision**.

---
### **Prochaine réunion**
- **Mardi 13 octobre 2026, 9h** *(date et lieu confirmés)*.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — La décision est bien formulée au point 3 : « Passage du mercredi au jeudi à partir du jeudi 1er octobre 2026 ».
  - D2 : 1 — Le point 5 indique l'accueil des classes « uniquement le mardi et jeudi matin (plus le lundi) » à partir de la rentrée de la Toussaint.
  - D3 : 1 — Le point 6 mentionne les deux projections-débats, les vendredis 13 et 27 novembre 2026 à 20h.
  - A1 : 1 — L'action est présente avec son responsable et son échéance : « Leroux rappelle le prestataire de l'automate de prêt n°2 avant le vendredi 18/09 ».
  - A2 : 1 — L'action est présente avec son responsable et son échéance : « Combes informe les 7 bibliothèques relais avant le vendredi 25/09 ».
  - A3 : 1 — L'action est présente avec son responsable et son échéance : « Aubertin finalise la délibération et l'envoie au secrétariat général avant le vendredi 18/09 ».
  - A4 : 1 — L'action est présente avec son responsable et son échéance : « Fabre envoie le nouveau planning aux écoles du territoire avant les vacances de la Toussaint ».
  - A5 : 1 — L'action est présente avec son responsable et son échéance : « N'Diaye réserve les films auprès de la médiathèque départementale avant le vendredi 9 octobre ».
- `absence_invention` : 0 — Plusieurs éléments ne figurent pas dans les notes ou les contredisent : « (date et lieu confirmés) » pour la prochaine réunion alors qu'aucun lieu n'est mentionné, « Changement de jour de passage : jeudi → mercredi (non applicable) » qui inverse le sens du changement, et « correction de l'ordre du jour initial : 20h au lieu de 20h le 13/11 » qui déforme la correction (le 27 au lieu du 20).
- `structure` : 0 — Les sections Participants et Points abordés existent, mais les décisions et les actions sont dispersées dans les points et ne forment pas de sections dédiées « Décisions » et « Actions ».
- Inventions : « (date et lieu confirmés) » : aucun lieu n'est indiqué pour la prochaine réunion dans les notes; « Changement de jour de passage : jeudi → mercredi (non applicable) » : sens inversé par rapport aux notes; « correction de l'ordre du jour initial : 20h au lieu de 20h le 13/11 » : correction erronée, les notes indiquent le 27 au lieu du 20 novembre; « budget projet 2027 » : interprétation non vérifiable de « BP 2027 »
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
**Compte rendu du conseil d’administration**

**Objet** : Réunion du conseil d’administration du 6 octobre 2026

**Participants** :
- Administration : Mme Cordier (présidente), M. Vauquelin (principal adjoint), Mme Ferhat (adjointe gestionnaire), M. Tessier (CPE).
- Collectivités : Mme Arnaud-Poitevin (conseillère départementale), M. Lebrun (adjoint au maire).
- Personnels enseignants : Mme Roussel (secrétaire de séance), Mme Kasprzak, M. N’Diaye, Mme Bellamy, Mme Varenne, M. Guérin absent.
- Personnels administratifs/techniques/sociaux : Mme Picot, M. Benslimane.
- Représentants des parents : Mme Chaumont, M. Ostrowski, Mme Sy, M. Pellerin, Mme Delorme, Léna (remplaçant de M. Baudoin).
- Représentants des élèves : Léna (3ᵉ), Yanis (4ᵉ).
- Invités : Mme Saintonge (présentation du voyage en Andalousie), M. Lacombe (agent comptable).

---

### **Points abordés**

1. **Approbation du procès-verbal (PV) du 30 juin 2026**
   - Correction de l’erreur de frappe concernant la subvention du foyer socio-éducatif.
   - **Décision** : Adoption du PV corrigé à l’unanimité.

2. **Modification du règlement intérieur**
   - **Articles modifiés** :
     - Interdiction du téléphone en classe, avec tolérance en cour et foyer (pause numérique : téléphone éteint et rangé dès l’entrée jusqu’à la sortie, y compris pendant la pause méridienne, sauf usage pédagogique sur autorisation).
     - Obligation des chaussures de sport et tenue de rechange en EPS.
     - Ajout de la retenue le mercredi après-midi (13h30–15h30).
   - **Débat** : Critiques sur la pause numérique pour les troisièmes et les risques de cyberharcèlement.
   - **Amendement** : Autorisation de l’usage du téléphone *uniquement pour les troisièmes* au foyer pendant la pause méridienne.
   - **Vote** : 15 voix pour, 4 contre, 2 abstentions.
   - **Application** : Entrée en vigueur à la rentrée des vacances de la Toussaint (2 novembre 2026).
   - **Actions** :
     - Diffusion du texte sur l’ENT et dans les carnets de liaison numérique avant le **16 octobre**.
     - Présentation aux élèves en heure de vie de classe la semaine du **2 novembre**.

3. **Voyages et sorties scolaires**
   - Présentation de la proposition de voyage en Andalousie par Mme Saintonge.

4. **Bilan de la rentrée et dotation horaire globale**
   - **Suite de la discussion** (non détaillée dans ce compte rendu).

---
### **Décisions et actions**

1. **Toilettes du bâtiment C**
   - **Action** : Demande officielle au département pour un remplacement avant le **vendredi 9 octobre**.
   - **Responsable** : Mme Cordier.

2. **Demande d’élèves de sixième pour des casiers**
   - **Action** : Proposition de chiffrer des casiers pour les sixièmes, à présenter dans le cadre du **budget primitif 2027** au CA du **26 novembre 2026**.
   - **Responsable** : Mme Ferhat.

3. **Problème de chauffage dans la salle B12**
   - **Action** : Intervention de l’entreprise de maintenance prévue, date non encore confirmée.
   - **Responsable** : Mme Ferhat.

4. **Élections des représentants des parents**
   - **Date** : **Vendredi 9 octobre 2026** (vote par correspondance ou à l’urne, collège, 8h–12h).

5. **Prochaine séance du conseil d’administration**
   - **Date** : **Jeudi 26 novembre 2026, 17h30**.

---
**Ambiguïtés ou points non résolus** :
- Le projet de pédibus reste au stade de la réflexion sans décision municipale définitive.
- Aucune date précise n’a été fixée pour l’intervention du chauffage de la salle B12.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Le compte rendu indique : « Adoption du PV corrigé à l'unanimité », avec la correction de la subvention, sans en préciser le montant (1 800 €).
  - D2 : 0 — L'amendement des parents est décrit, mais son rejet (7 pour, 12 contre, 2 abstentions) n'est jamais mentionné.
  - D3 : 0.5 — Le vote (15-4-2) et l'application au 2 novembre figurent, mais l'article 12 est décrit de façon contradictoire (« tolérance en cour et foyer »), et la répartition des voix contre n'est pas indiquée.
  - D4 : 0 — Le séjour neige des 5e et son vote sont absents.
  - D5 : 0 — Seule la présentation du voyage en Andalousie est mentionnée ; l'adoption sous réserve de l'aide et le vote 19-0-2 sont absents.
  - D6 : 0 — Le programme des sorties sans nuitée est absent.
  - D7 : 0 — Le point 4 est déclaré « non détaillé » et la motion sur la DHG est absente.
  - D8 : 0 — La DBM n° 3 (four mixte, 12 400 €) est absente.
  - D9 : 0 — La convention du gymnase est absente.
  - D10 : 0 — Le don de 450 € est absent.
  - A1 : 0 — La mise en ligne du PV corrigé sur l'ENT n'est pas mentionnée.
  - A2 : 0.5 — La diffusion sur l'ENT et le carnet avant le 16 octobre est présente, mais sans le responsable (M. Vauquelin) ni le rappel relatif aux PAI.
  - A3 : 0.5 — La présentation en heure de vie de classe la semaine du 2 novembre est présente, mais sans responsable.
  - A4 : 0 — La consultation du transporteur est absente.
  - A5 : 0 — La demande d'aide départementale avant le 30 novembre est absente.
  - A6 : 0 — La transmission de la motion à la DSDEN est absente.
  - A7 : 0 — La commande du four est absente.
  - A8 : 0 — L'envoi des documents budgétaires avant le 16 novembre est absent.
  - A9 : 1 — Le compte rendu mentionne la demande officielle au département avant le vendredi 9 octobre, sous la responsabilité de Mme Cordier.
  - A10 : 1 — Le chiffrage des casiers par Mme Ferhat pour le CA du 26 novembre est présent.
- `absence_invention` : 0 — La sortie écrit « Léna (remplaçant de M. Baudoin) » parmi les parents, alors que le pouvoir a été refusé et que Léna est élève ; elle présente aussi une action « Responsable : Mme Ferhat » pour le chauffage de B12, qui n'a pas été décidée.
- `structure` : 1 — Les sections Participants, Points abordés et « Décisions et actions » (regroupées) sont présentes.
- Inventions : Léna présentée comme remplaçante de M. Baudoin parmi les représentants des parents; Action sur le chauffage de B12 attribuée à Mme Ferhat comme responsable, alors qu'aucune action n'a été décidée; Article 12 décrit avec une « tolérance en cour et foyer », contraire au texte adopté
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
**Compte rendu du comité de pilotage du Contrat local de santé (CLS) 2024-2028 – Pontcarel**
*Jeudi 17 septembre 2026, salle Marianne, hôtel de ville*

---

### **Participants présents**
- M. Desbrosses, maire de Pontcarel (coprésident)
- Mme Laborde, délégation départementale ARS (coprésidente)
- M. Ogier, conseiller municipal délégué à la santé
- Mme Benamar, coordinatrice CLS (ville)
- Dr Lemaire, président de la CPTS du Haut-Pontcarel (en visio)
- Mme Ricard, CPAM, chargée de mission prévention
- M. Vasseur, département, service autonomie
- Mme Tran, directrice adjointe du centre hospitalier de Pontcarel
- Mme Haddou, Point Écoute Jeunes (invitée pour le point 3)

---

### **Points abordés**

1. **Bilan mi-parcours du CLS**
   - Présentation des 18 fiches-actions : 4 terminées, 11 engagées, 3 non démarrées (dont « santé des aidants » et « habitat indigne »).
   - **Points forts** : ateliers nutrition dans le quartier Les Coudrais (212 participants depuis 2024) et permanences CPAM au CCAS.
   - **Points faibles** : faible avancée sur l’axe santé environnement et manque de données.
   - **Décision** : validation à l’unanimité du bilan par le COPIL.
   - Préparation d’une note de synthèse pour le conseil municipal du **12 novembre 2026** (transmission au cabinet du maire avant le **30 octobre**).

2. **Accès aux soins**
   - **Contexte** : départ en retraite de deux médecins généralistes en fin 2026, entraînant une estimation de 2 600 patients sans médecin traitant.
   - **Projets** :
     - Projet de **maison de santé pluriprofessionnelle (MSP)** libérale porté par la CPTS (3 médecins intéressés, mais pas de signature).
     - Proposition d’un **centre de santé municipal** (modèle d’une ville voisine), critiqué pour son coût initial.
   - **Décision** :
     - Lancement d’une **étude d’opportunité comparant les deux scénarios** (coût estimé à 28 000 € TTC).
     - Financement partiel par l’ARS (50 % max. 15 000 € via le FIR), reste à charge de la ville.
     - Montée du dossier FIR par Mme Benamar avec l’appui de l’ARS, **dépôt avant le 13 novembre 2026**.
     - Attente de l’étude pour trancher entre MSP et centre de santé.
   - **Autres actions** :
     - Campagne « M’T dents » dans les écoles élémentaires (interventions prévues **janvier-mars 2027**).

3. **Santé mentale**
   - **Contexte** : hausse des demandes au Point Écoute (+35 % en un an) et délais longs pour les CMP (4 à 6 mois pour un premier rendez-vous).
   - **Propositions** :
     - Formation de **24 personnes** (agents municipaux, CCAS, animateurs jeunesse, bénévoles) aux **Premiers secours en santé mentale (PSSM)**.
     - **Décision** : 2 sessions de formation au **1er semestre 2027** (financement ARS déjà inclus dans la fiche-action 7).
     - Proposition de créer un **conseil local de santé mentale (CLSM)**, non retenue pour l’instant.
     - Demande de subvention complémentaire pour le Point Écoute (+5 000 €), à traiter par la commission des subventions.

4. **Prévention / nutrition / santé environnement**
   - **Ateliers nutrition** : **reconduction en 2027** (format inchangé, financement CPAM confirmé pour 4 500 €).
   - **Collaboration avec l’Éducation nationale** : contact pris pour intégrer les infirmières scolaires aux ateliers nutrition.
   - **Santé environnement** :
     - **Campagne d’information** sur le moustique tigre (flyers + réunions de quartier) au **printemps 2027**.
     - **État des lieux** sur la qualité de l’air intérieur dans les écoles (demande à Ogier pour les services techniques).
   - **Idée

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « Décision : validation à l'unanimité du bilan par le COPIL » reprend D1.
  - D2 : 0.5 — L'étude comparative à 28 000 € TTC est présente, mais le cofinancement ARS est présenté comme acquis (« Financement partiel par l'ARS ») sans la réserve du comité FIR.
  - D3 : 1 — Le compte rendu reprend les 2 sessions PSSM au 1er semestre 2027, les 24 personnes et le financement ARS de la fiche-action 7 (montant de 6 000 € omis).
  - D4 : 1 — « Reconduction en 2027 (format inchangé, financement CPAM confirmé pour 4 500 €) » reprend D4.
  - D5 : 1 — La campagne d'information sur le moustique tigre au printemps 2027 (flyers et réunion) est présente.
  - D6 : 0 — La sortie est tronquée au point 4 : l'accord de principe sur l'avenant n° 1 est absent.
  - A1 : 0.5 — La note de synthèse pour le CM du 12 novembre, à transmettre avant le 30 octobre, est mentionnée sans le responsable (Mme Benamar).
  - A2 : 1 — « Montée du dossier FIR par Mme Benamar avec l'appui de l'ARS, dépôt avant le 13 novembre 2026 » reprend A2.
  - A3 : 0.5 — M'T dents (janvier-mars 2027) est mentionnée sans la responsable (Mme Ricard) ni le ciblage CP / écoles du QPV.
  - A4 : 0 — L'action consistant à solliciter des organismes PSSM et à proposer des dates au prochain COPIL est absente.
  - A5 : 0.5 — La sortie mentionne « contact pris » avec l'Éducation nationale, sans responsable et en présentant l'action comme déjà réalisée.
  - A6 : 0 — Le pilotage par M. Ogier et la présentation du plan de campagne au COPIL de mars sont absents.
  - A7 : 0.5 — L'état des lieux de la qualité de l'air est mentionné, mais le rôle est inversé (« demande à Ogier pour les services techniques »).
  - A8 : 0 — La rédaction de la fiche de l'avenant avant le 15 janvier 2027 est absente (sortie tronquée).
  - A9 : 0 — L'envoi du sondage pour fixer la date du prochain COPIL est absent.
  - A10 : 0 — La diffusion du compte rendu sous 15 jours est absente.
- `absence_invention` : 0 — La sortie présente le cofinancement ARS comme acquis (« Financement partiel par l'ARS ») alors qu'il est sous réserve du comité FIR (piège), et affirme « contact pris » alors que le contact reste à prendre.
- `structure` : 0 — La sortie, tronquée au point 4, ne contient ni section Décisions ni section Actions.
- Inventions : Cofinancement ARS présenté comme acquis, sans la réserve du comité FIR de décembre; « contact pris » avec l'Éducation nationale, alors que Mme Benamar doit encore prendre contact; « demande à Ogier pour les services techniques » : inversion du rôle, c'est M. Ogier qui demande l'état des lieux aux services techniques
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
**[Nom de la commune],**

**[Nom du maire],**

**Maire de [Nom de la commune],**

**Salle du Conseil Municipal, Mairie**

**Lundi 16 novembre 2026**

**Objet : Convocation en urgence du Conseil Municipal**

Madame, Monsieur,

Par la présente, je vous convie à une séance du Conseil Municipal de **[Nom de la commune]**, qui aura lieu **le mercredi 18 novembre 2026 à 18 h 30** dans la salle du conseil municipal de la mairie.

Cette séance est convoquée en **urgence** en raison de la nécessité de traiter les points suivants :
- la **demande d’aide exceptionnelle de l’État pour la réparation de la toiture de l’école**, endommagée par la tempête du 12 novembre 2026, devant être déposée avant le **20 novembre 2026** ;
- l’**approbation du devis des travaux de mise hors d’eau de l’école**.

Cette réunion est obligatoire pour les conseillers municipaux en exercice.

Je vous prie d’agréer, Madame, Monsieur, l’expression de mes salutations distinguées.

**[Nom du maire]**
Maire de **[Nom de la commune]**

*Copie : [Liste des conseillers municipaux concernés si nécessaire]*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Nom de la commune]": true,
    "[Nom du maire]": true
  },
  "emplacements_reussis": true
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : aucun bloc destinataire « Mesdames et messieurs les conseillers municipaux » (seulement « Madame, Monsieur »), et aucune mention que le maire rendra compte de l'urgence dès l'ouverture de la séance, que le conseil se prononcera sur celle-ci et pourra renvoyer la discussion ; le délai abrégé n'est pas non plus explicité.
- Inventions : « Cette réunion est obligatoire pour les conseillers municipaux en exercice » : affirmation absente de l'entrée et des références.; « Copie : [Liste des conseillers municipaux concernés si nécessaire] » : emplacement non demandé.; « endommagée par la tempête du 12 novembre 2026 » : année ajoutée, non précisée dans l'entrée.
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
**[Nom de la commune],**

**[Nom du maire],**

**Monsieur le Maire,**

Par la présente, nous vous convions à la séance du conseil municipal de **[Nom de la commune]**, qui se tiendra le **[mardi 24 novembre 2026]** à **[19 h 00]** dans la **[salle du conseil municipal, hôtel de ville]**.

Conformément aux **[modalités de consultation fixées par le règlement intérieur]**, cette séance aura pour ordre du jour :
- l’**approbation du procès-verbal de la séance du 13 octobre 2026** ;
- l’**attribution de la délégation de service public pour l’exploitation de la piscine municipale** ;
- la **garantie d’emprunt accordée à un bailleur social** ;
- les **créations et suppressions de postes au tableau des effectifs**.

Une **note explicative de synthèse** sur les affaires soumises à délibération est jointe à ce courrier.

Veuillez agréer, **[Nom de la commune]**, le salut de nos respects.

**[Signature]**
*[Nom du fonctionnaire ou du service compétent]*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Modalités de consultation fixées par le règlement intérieur]": false,
    "[Nom de la commune]": true,
    "[Nom du maire]": true
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : les destinataires (« Monsieur le Maire » au lieu de mesdames et messieurs les conseillers municipaux), la date d'envoi du mercredi 18 novembre 2026, l'objet, la mention de la consultation du projet de contrat de DSP, et la signature du maire (remplacée par « [Nom du fonctionnaire ou du service compétent] ») ; le registre est en outre inadapté (« Veuillez agréer, [Nom de la commune], le salut de nos respects »).
- Inventions : Destinataire « Monsieur le Maire » non conforme à l'entrée (convocation adressée aux conseillers municipaux); Emplacement « [Nom du fonctionnaire ou du service compétent] » substitué à la signature du maire; Formule « le salut de nos respects » adressée à « [Nom de la commune] », sans fondement dans l'entrée
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
**[Date du courrier]**

**Club de randonnée « Les Sentiers de la vallée »**
Monsieur le Trésorier Bernard Lefèvre,

Par la présente, nous répondons à votre demande concernant la **taxe foncière** pour le local de réunion dont votre association est propriétaire.

D’après les informations disponibles sur le site [service-public.fr](https://www.service-public.fr), la **taxe foncière** s’applique aux **bâtiments et terrains** utilisés à des fins **privatives ou professionnelles**, y compris ceux appartenant à des associations. Comme votre association en est propriétaire, elle doit donc **payer cette taxe**, sous réserve de vérifier les éventuelles exonérations spécifiques (par exemple, pour les locaux utilisés à des fins associatives ou culturelles).

Pour confirmer les modalités exactes de calcul et les éventuelles réductions, nous vous invitons à consulter votre **notice individuelle de taxe foncière** ou à contacter directement votre **collectivité territoriale** ([Commune]) ou votre **service des impôts fonciers**.

Nous vous prions d’agréer, Monsieur le Trésorier, l’expression de nos salutations distinguées.

**[Nom et qualité du signataire]**
*Responsable de l’Espace France Services*
[Adresse de l’association]

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Adresse de l'association]": false,
    "[Commune]": true,
    "[Date du courrier]": true,
    "[Nom et qualité du signataire]": true
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : pas d'en-tête d'expéditeur, pas de lieu, pas d'objet, pas de liste des exonérations limitées, pas de mention de l'envoi des justificatifs aux impôts ; la formule d'appel « Monsieur le Trésorier Bernard Lefèvre, » remplace « Monsieur, » ; une exonération interdite est inventée (« pour les locaux utilisés à des fins associatives ou culturelles »).
- Inventions : Exonération inventée « pour les locaux utilisés à des fins associatives ou culturelles » (valeur interdite); Critère d'application inventé : « bâtiments et terrains utilisés à des fins privatives ou professionnelles »; Renvoi non sourcé à une « notice individuelle de taxe foncière »; Invitation non sourcée à contacter la « collectivité territoriale » ou le « service des impôts fonciers » pour les modalités de calcul et les réductions; Qualité du signataire inventée hors emplacement : « Responsable de l'Espace France Services »
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
**Vous pouvez être le siège d’une association en mairie ?**

Oui, certaines associations choisissent de s’installer dans une mairie. C’est souvent le cas pour celles qui :
- Ont des activités locales (rencontres, événements, etc.).
- Travaillent avec les communes ou les villes.

**Comment faire ?**
Pour demander à utiliser des locaux municipaux, l’association doit envoyer une lettre à la mairie.

**Les règles en vigueur :**
Le maire peut décider de mettre à disposition des espaces (bureaux, salles) pour les associations qui le demandent.
Il fixe les conditions d’utilisation :
- Quand et comment les locaux peuvent être utilisés (ex. : un jour par semaine).
- Qui peut y accéder et à quelles heures.
- Comment les bureaux sont répartis entre plusieurs associations.

**Le coût :**
Les locaux peuvent être **gratuits** ou payants. Le prix (appelé *loyer* ou *participation*) est fixé par le conseil municipal.

---
**À noter :**
Le siège social d’une association peut aussi être :
- Au domicile d’un membre.
- Dans des locaux publics (écoles, bibliothèques…).
- Dans un bureau commercial ou privé.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 12.6661,
  "km_entree": 62.48,
  "km_sortie": 75.1461
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie ajoute des informations absentes de l'entrée, comme « (rencontres, événements, etc.) » et « espaces (bureaux, salles) ». Elle affaiblit aussi l'information principale : « s'installer dans une mairie » remplace « une mairie peut être le siège social ». Enfin, elle change « locaux institutionnels » en « locaux publics ».
- `termes_juridiques` : 0 — « locaux communaux » est remplacé par « locaux municipaux » et « espaces », et « siège social » n'est pas employé dans la réponse sur la mairie (« s'installer dans une mairie »).
- `clarte_percue` : 3 — La structure en rubriques et listes aide à la lecture, mais le titre « Vous pouvez être le siège d'une association en mairie ? » est incorrect et déroutant pour un usager.
- Inventions : Exemples d'activités locales : « rencontres, événements, etc. »; Précision « espaces (bureaux, salles) » non présente dans l'entrée
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
**Voici comment les prestations familiales peuvent être saisies :**

En général, les aides familiales ne peuvent pas être enlevées. Cependant, certaines peuvent être **saisies** (c’est-à-dire prélevées) dans deux cas précis :

1. **Si vous ne payez pas de pension alimentaire** (comme une somme versée pour aider votre enfant ou votre ex-conjoint).
2. **Si vous ne remboursez pas d’autres dépenses liées à l’enfant** (comme des frais d’hôpital, de cantine scolaire, etc.).

Voici les prestations familiales qui peuvent être concernées :
- **Allocation de base** (versée pour élever votre enfant).
- **Prestation partagée d’éducation de l’enfant** (si vous en bénéficiez).
- **Allocations familiales** (versées chaque mois pour votre enfant).
- **Complément familial** (si vous avez droit à des aides supplémentaires).
- **Allocation de rentrée scolaire (ARS)** (versée en septembre pour aider à payer les frais de l’école).
- **Allocation de soutien familial (ASF)** (si vous recevez une aide pour aider un enfant).
- **Allocation d’éducation de l’enfant handicapé (AEEH)** (si votre enfant a un handicap).

**Le montant prélevé dépend de vos revenus et de vos dépenses.** La Caf (ou la MSA, selon votre situation) peut limiter la somme saisie pour ne pas trop vous toucher.

---
**Attention** : Si vous avez **faux** ou **trompé** la Caf ou la MSA en demandant ces aides, elles peuvent **récupérer** ce qu’elles ont versé à tort. Ensuite, elles peuvent **retenir** une partie de vos prochaines prestations familiales pour vous rembourser.

*(Ce passage reste technique et juridique, car il concerne des sanctions en cas de fraude.)*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 10.2503,
  "km_entree": 60.18,
  "km_sortie": 70.4303
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie modifie plusieurs informations : « montant mensuel fixé » devient « La Caf (ou la MSA, selon votre situation) peut limiter la somme saisie pour ne pas trop vous toucher » (caractère mensuel perdu et pouvoir discrétionnaire ajouté) ; la cantine passe de la dette alimentaire aux « autres dépenses » ; des précisions non vérifiables sont ajoutées (« versée en septembre », « versées chaque mois »).
- `termes_juridiques` : 0 — « insaisissables » est remplacé par « ne peuvent pas être enlevées », tandis que « dette alimentaire » et « indu » disparaissent (« ce qu'elles ont versé à tort »).
- `clarte_percue` : 3 — La structure en liste aide, mais des formulations fautives ou confuses (« Si vous avez faux », « pour vous rembourser ») et des descriptions erronées (ASF « si vous recevez une aide pour aider un enfant ») gênent la compréhension.
- Inventions : La Caf (ou la MSA, selon votre situation) peut limiter la somme saisie pour ne pas trop vous toucher; Allocation de rentrée scolaire versée en septembre; Allocations familiales versées chaque mois; Allocation de soutien familial (si vous recevez une aide pour aider un enfant); Complément familial (si vous avez droit à des aides supplémentaires); pour vous rembourser; Ce passage reste technique et juridique, car il concerne des sanctions en cas de fraude
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
**Demande d’Aide Sociale à l’Hébergement (ASH) pour une personne âgée**

Pour obtenir l’ASH, voici les conditions que vous devez remplir :

1. **Âge et situation de santé**
   - Avoir **plus de 65 ans** (ou **plus de 60 ans** si vous êtes reconnu incapable de travailler).
   - Vivre **de manière stable et régulière en France**. Si vous êtes étranger, vous devez avoir un **titre de séjour valide**.

2. **Hébergement dans un établissement adapté**
   - Être hébergé dans un **établissement spécialisé** (comme un **Ehpad**, une **résidence autonomie** ou une **USLD**), qui accepte les personnes aidées par l’Aide Sociale.

3. **Vos revenus doivent être insuffisants**
   - Vos revenus mensuels doivent être **inférieurs aux frais d’hébergement** que l’établissement vous facture.

---
**Quand faire la demande ?**
Pour que l’aide commence dès votre entrée dans l’établissement, il faut la demander **dans les 2 mois maximum après votre arrivée**. Il est donc conseillé de la faire **en même temps que votre admission**.

---
**Qui finance l’ASH ?**
L’Aide Sociale est versée par votre **département**. Chaque département a ses propres règles, donc les montants peuvent varier.

**Comment est calculé le montant de l’Aide ?**
Le département prend en compte :
- Vos **revenus personnels** (sauf certaines pensions comme l’Allocation de Reconnaissance du Combattant ou la Légion d’Honneur).
- Les revenus de votre **conjoint(e), partenaire de Pacs, concubin(e)** ou de vos **obligés alimentaires** (comme vos enfants, gendres ou belles-filles).

⚠️ **Exception** : Vos petits-enfants ne doivent pas contribuer si vous demandez l’Aide pour l’un de vos grands-parents.

---
**Que couvre l’Aide Sociale ?**
L’ASH peut payer **une partie ou la totalité** des frais d’hébergement. Elle peut aussi financer le **tarif dépendance** si vous êtes en Ehpad ou USLD.

**Objectifs du montant** :
- Vous laisser **au moins 10 % de vos revenus** chaque mois (soit au minimum **125 €**).
- Si votre conjoint(e) ou partenaire reste à domicile, l’Aide doit permettre à cette personne de garder **au moins 1 043,59 € par mois**.

---
*Passage à conserver tel quel (termes juridiques obligatoires) :*
**À noter : Le petit-enfant est dispensé de l'obligation alimentaire en cas de demande d'ASH pour le compte de l'un de ses grands-parents. Cette dispense s'étend aux descendants de ce petit-enfant.**

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 4.2636,
  "km_entree": 69.54,
  "km_sortie": 73.8036
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs conditions sont déformées : « Vos petits-enfants ne doivent pas contribuer si vous demandez l'Aide pour l'un de vos grands-parents » inverse la logique de la dispense. « au moins 10 % de vos revenus (soit au minimum 125 €) » transforme le plancher indépendant de 125 € en simple équivalent. « qui accepte les personnes aidées » remplace la condition de places réservées. La liste cumulative des revenus devient « ou ».
- `termes_juridiques` : 0 — Le terme « règlement d'aide sociale » disparaît : il est remplacé par « Chaque département a ses propres règles ».
- `clarte_percue` : 3 — La structure est claire. En revanche, le « vous » est incohérent (petits-enfants et grands-parents), le passage final est redondant, et la mention méta « Passage à conserver tel quel » brouille la compréhension.
- Inventions : « Vos revenus mensuels » : la précision « mensuels » est absente de l'entrée.; « établissement spécialisé » : ce qualificatif ne figure pas dans l'entrée.; « soit au minimum 125 € » : présente 125 € comme équivalent des 10 %, ce que le texte source ne dit pas.
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
**Vous pouvez aider votre enfant à payer sa cantine scolaire selon son âge et votre situation.**

### **Pour les enfants en primaire (maternelle et élémentaire)**
Les prix de la cantine sont fixés par votre commune. Certaines villes ajustent ces tarifs en fonction de vos revenus et de vos charges, grâce à un calcul appelé *quotient familial*. Certaines communes proposent aussi des aides pour réduire le coût de la cantine.

- **Comment faire ?**
  - Contactez votre mairie pour savoir si des aides existent.
  - Vous pouvez aussi demander de l’aide à l’**assistante sociale scolaire** de votre école.

⚠️ **Cas particulier** : Si votre enfant est scolarisé dans une école éloignée et doit rester à la cantine, certaines communes peuvent vous aider. Parlez-en au **directeur d’école** dès le début de l’année scolaire.

---

### **Pour les collèges et lycées**
Certains établissements publics (collèges et lycées) proposent un **fonds social** pour aider les familles à payer la cantine.

- **Comment en bénéficier ?**
  - Vous devez vous adresser à l’**assistante sociale** de votre établissement ou au secrétariat.
  - Le chef d’établissement décide des conditions d’attribution. Il vous informera en début d’année scolaire.

Les tarifs de la cantine sont fixés par le **département** pour les collèges et par la **région** pour les lycées. Certaines collectivités (départements ou régions) peuvent aussi ajuster les prix en fonction de vos revenus grâce au *quotient familial*. Certaines d’entre elles proposent des aides supplémentaires.

- **Comment savoir si vous avez droit ?**
  - Contactez votre **collectivité locale** (département ou région) pour vérifier les dispositifs disponibles.

---
*Passage à conserver tel quel (termes juridiques obligatoires) :*
*"Le quotient familial"* et *"collectivité"* sont des termes techniques utilisés dans ce texte pour désigner des calculs financiers et des institutions publiques.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": -1.9773,
  "km_entree": 65.57,
  "km_sortie": 63.5927
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations sont modifiées. Le cas de l'école éloignée relève de « certains départements » et vise une « école élémentaire », alors que la sortie écrit « certaines communes peuvent vous aider » à propos d'« une école éloignée ». Le chef d'établissement attribue l'aide et informe des conditions, alors que la sortie dit qu'il « décide des conditions d'attribution ». Le fonds devient une aide proposée par « certains établissements publics ». Enfin, la première phrase transforme l'aide aux familles en « Vous pouvez aider votre enfant » et fait dépendre l'aide de « son âge » au lieu du niveau de scolarisation.
- `termes_juridiques` : 0 — Le terme « fonds social pour les cantines » est réduit à « fonds social ». La note finale présente à tort « collectivité » comme terme obligatoire. « quotient familial », « chef d'établissement » et « assistante sociale scolaire » sont bien conservés.
- `clarte_percue` : 3 — La structure en rubriques et les consignes « Comment faire ? » sont claires. En revanche, la phrase d'accroche est confuse (« aider votre enfant à payer sa cantine ») et la note finale sur les termes techniques est un ajout parasite qui peut dérouter l'usager.
- Inventions : certaines communes peuvent vous aider (cas de l'école éloignée, attribué aux départements dans l'entrée); Certains établissements publics (collèges et lycées) proposent un fonds social; Le chef d'établissement décide des conditions d'attribution; selon son âge; Passage à conserver tel quel : « Le quotient familial » et « collectivité » sont des termes techniques… (note méta absente de l'entrée)
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
**Demande d’aide sociale : où et comment faire ?**

Pour demander une aide sociale (sauf pour les cas liés à l’aide sociale à l’enfance), vous devez vous adresser :
- **Soit** à votre **centre communal ou intercommunal d’action sociale** (CCAS ou CIAS), si votre commune en a un.
- **Sinon**, à la mairie de votre domicile.

Une fois votre demande reçue, le CCAS ou la mairie va préparer un dossier complet pour vous.

**Délai** : votre dossier doit être transmis à l’administration (représentant de l’État ou président du département) **dans les 1 mois** après votre demande.

L’administration va étudier votre dossier avec l’avis du CCAS ou de la mairie. Si le maire ou le CCAS demande l’avis du conseil municipal, celui-ci sera consulté.

---
**Pour les personnes sans domicile stable** (qui n’ont pas de lieu fixe pour vivre), vous devez choisir un endroit précis pour être en règle avec les services sociaux. Vous pouvez le faire :
- **Soit** auprès d’un **centre communal ou intercommunal d’action sociale** (CCAS ou CIAS).
- **Soit** auprès d’un **organisme agréé** par le département pour ce type de demande.

L’organisme qui gère votre dossier dépend du département où vous avez choisi de vous installer.

---
**À noter** :
- Les aides comme l’**allocation personnalisée d’autonomie (APA)**, la **prestation de compensation du handicap (PCH)** ou le **revenu de solidarité active (RSA)** sont gérées par le département où vous êtes enregistré.
- Pour bénéficier de ces aides, vous devez respecter les règles légales et conventionnelles en vigueur.

---
*Termes juridiques non simplifiés :*
- **CCAS** : Centre Communal d’Action Sociale
- **CIAS** : Centre Intercommunal d’Action Sociale
- **Représentant de l’État** : Personne désignée par l’État pour agir au nom du département (généralement le préfet).
- **Prestations sociales légales** : Aides financières ou services obligatoires par la loi.
- **Élu domicile** : Choisir un lieu précis pour être enregistré auprès des services publics.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 19.0891,
  "km_entree": 48.65,
  "km_sortie": 67.7391
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations obligatoires sont supprimées : la réserve de l'article L. 252-1, les visiteurs-enquêteurs, ainsi que les droits civils, le titre national d'identité, les listes électorales et l'aide juridictionnelle. Des ajouts non vérifiables apparaissent aussi : « organisme agréé par le département », « vous devez respecter les règles légales et conventionnelles en vigueur ».
- `termes_juridiques` : 0 — Plusieurs termes à conserver sont absents : « visiteurs-enquêteurs », « aide juridictionnelle », « demandes d'admission » et « département débiteur ». « Élire domicile » est en outre remplacé à tort par « choisi de vous installer ».
- `clarte_percue` : 3 — La structure est lisible, mais « dans les 1 mois » et « le département où vous avez choisi de vous installer » risquent d'induire l'usager en erreur.
- Inventions : organisme agréé par le département pour ce type de demande; Pour bénéficier de ces aides, vous devez respecter les règles légales et conventionnelles en vigueur; L'organisme qui gère votre dossier dépend du département où vous avez choisi de vous installer; Représentant de l'État : Personne désignée par l'État pour agir au nom du département (généralement le préfet); préparer un dossier complet pour vous
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
**Voici comment les marchés publics doivent payer leurs fournisseurs :**

### **1. Délai de paiement général**
Les collectivités, entreprises ou organismes qui achètent des biens ou services (**appelés "pouvoirs adjudicateurs"**) doivent payer les factures dans les délais prévus dans le contrat.
Si le contrat ne précise pas de délai, celui-ci est fixé par des règles légales et peut varier selon le type d’organisme.

---
**⚠️ Terme juridique non simplifié :**
*"pouvoirs adjudicateurs"* → Organismes publics ou privés qui achètent des produits ou services via un marché public.

---

### **2. Délai standard**
Pour la plupart des marchés, le délai de paiement est de **30 jours** après la réception de la facture.

---
**⚠️ Terme juridique non simplifié :**
*"délai de paiement"* → Temps imparti pour régler une facture après réception.

---

### **3. Délais exceptionnels**
Certains organismes ont des délais plus longs :
- **50 jours** pour les hôpitaux publics et les établissements militaires.
- **60 jours** pour certaines entreprises publiques (sauf les collectivités locales).

---
**⚠️ Terme juridique non simplifié :**
*"entreprises publiques"* → Sociétés contrôlées par l’État ou des collectivités.

---

### **4. Que faire en cas de retard ?**
Si le fournisseur ne reçoit pas son paiement à l’échéance :
- **Le retard commence dès le lendemain** de la date limite.
- Le fournisseur a droit à des **intérêts de retard** (calculés selon une règle légale).
- Il peut aussi demander une **indemnité forfaitaire** pour les frais de recouvrement (paiement des frais administratifs).
- Si les frais dépassent cette indemnité, il peut demander une **indemnisation supplémentaire** en justifiant les dépenses.

---
**⚠️ Terme juridique non simplifié :**
*"intérêts moratoires"* → Intérêts calculés automatiquement pour compenser le retard.
*"indemnité forfaitaire"* → Montant fixe accordé pour les frais de recouvrement.
*"indemnisation complémentaire"* → Remboursement supplémentaire si les frais dépassent le montant forfaitaire.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 9.1161,
  "km_entree": 50.13,
  "km_sortie": 59.2461
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations sont modifiées, supprimées ou ajoutées : ajout de « après la réception de la facture », « sauf les collectivités locales » au lieu de « établissements publics locaux », « Il peut aussi demander une indemnité forfaitaire » alors qu'elle est due de plein droit ; le taux (BCE + 8 points), le plafond du délai contractuel et la condition du créancier ayant rempli ses obligations sont supprimés.
- `termes_juridiques` : 0 — « entités adjudicatrices » et « de plein droit » sont absents, « créancier » est remplacé par « fournisseur », et « retard de paiement » n'est pas conservé comme terme.
- `clarte_percue` : 4 — Le texte est structuré et rédigé simplement, donc facile à lire pour un usager, mais il reste trompeur sur le fond (indemnité présentée comme à demander, exception mal formulée).
- Inventions : le délai de 30 jours court « après la réception de la facture »; « pour la plupart des marchés »; « sauf les collectivités locales »; « établissements militaires » (au lieu de « établissements du service de santé des armées »); pouvoirs adjudicateurs définis comme « organismes publics ou privés »; entreprises publiques définies comme « sociétés contrôlées par l'État ou des collectivités »; indemnité forfaitaire assimilée au « paiement des frais administratifs »
- Confiance : haute

**Juge second** : juge

- `fidelite` : 2 — Toutes les informations_a_conserver sont présentes et exactes, sans ajout ni modification de sens.
- `termes_juridiques` : 1 — Tous les termes_juridiques_a_conserver sont conservés et expliqués sans remplacement erroné.
- `clarte_percue` : 5 — La reformulation est accessible à un usager sans connaissance administrative, avec une structure claire et des explications intégrées.
- Inventions : aucune
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
En France, le mandat du Président de la République est de **5 ans**.

Il peut être renouvelé **une seule fois consécutivement**, soit un total maximum de **7 ans** (soit deux mandats de 5 ans chacun). Ce plafond a été instauré par la réforme constitutionnelle de 2008.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La durée (5 ans) et le renouvellement unique sont corrects, mais la réponse affirme à tort « soit un total maximum de 7 ans (soit deux mandats de 5 ans chacun) », ce qui est faux (10 ans) et contradictoire.
- Inventions : soit un total maximum de 7 ans; Ce plafond a été instauré par la réforme constitutionnelle de 2008
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
En France, l'élection des représentants au Parlement européen se déroule en **un seul tour**.

L'élection suivante après celle des **8 et 9 juin 2024** aura lieu en **2029**.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse indique correctement « un seul tour » et « 2029 », en français correct, conformément aux trois critères de la référence.
- Inventions : aucune
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
**Date limite de réponse :** **1er mars 2026**

**Raisonnement :**
1. **Date de réception :** Vendredi 27 février 2026.
2. **Ajout de 15 jours :**
   - 27 février + 15 jours = **11 mars 2026** (date calculée sans tenir compte des week-ends).
3. **Vérification du jour de la semaine :**
   - Le 11 mars tombe un **dimanche**.
4. **Report au lundi suivant :**
   - Le lundi suivant le dimanche 11 mars est le **12 mars 2026** (mais ce n’est pas la bonne approche ici).
   - **Correction :** Le 11 mars est un dimanche, donc on ajuste en comptant **1 jour de plus** pour atteindre le **mardi 13 mars** (ce qui ne correspond pas à la logique initiale).
   - **Réévaluation correcte :**
     - **15 jours après le 27 février** = **11 mars** (dimanche).
     - Puis, on **reporte au lundi suivant** (car le dimanche est exclu) :
       - **12 mars** (lundi).

   **Erreur initiale corrigée :**
   - La bonne méthode est de **comptabiliser 15 jours après le 27 février** (soit **11 mars**), puis de vérifier si ce jour est un week-end.
   - Si c’est un week-end, on **reporte au lundi suivant** (donc **12 mars**).
   - Cependant, en réalité, la règle standard est de **reporter au premier jour ouvrable suivant** (lundi) si la date tombe un week-end.
   - **Donc, la date limite est bien le 12 mars 2026** (lundi).

*(Note : Si la règle précise un report strictement au lundi suivant le week-end, alors la réponse est 12 mars. Si elle impose un report au premier jour ouvrable, c’est le même résultat.)*

---
**Réponse finale :** La date limite est **12 mars 2026** (lundi).

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse : elle annonce d'abord « 1er mars 2026 », puis conclut « La date limite est 12 mars 2026 (lundi) », alors que la bonne réponse est le lundi 16 mars 2026. Le calcul intermédiaire est faux (« 27 février + 15 jours = 11 mars ») au lieu du samedi 14 mars, et les 28 jours de février 2026 ne sont pas pris en compte.
- Inventions : Date limite « 1er mars 2026 » (incohérente avec le calcul); « 27 février + 15 jours = 11 mars 2026 » (faux, c'est le 14 mars); « Le 11 mars tombe un dimanche » (faux : le 11 mars 2026 est un mercredi); « mardi 13 mars » (le 13 mars 2026 est un vendredi); « Le lundi 12 mars 2026 » (le 12 mars 2026 est un jeudi)
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
Voici la répartition des jours de travail en fonction des contraintes données :

- **Alice** travaille le **mardi**.
  *Justification* : Comme Chloé travaille le lendemain de celui d’Alice, elle ne peut pas travailler le lundi (car Bruno ne travaille pas ce jour-là). Le mercredi est donc le seul jour restant pour Alice.

- **Bruno** travaille le **mercredi**.
  *Justification* : Il ne travaille pas le lundi, et il reste le mercredi comme seul jour possible pour lui.

- **Chloé** travaille le **jeudi** *(si on considère que les contraintes s'appliquent sur les jours travaillés par les trois agents, et que les jours sont étendus à une semaine plus large pour respecter la contrainte "le lendemain")*.
  *Justification* : Comme Alice travaille le mardi, Chloé travaille donc le mercredi suivant (soit le **jeudi** si on étend la logique à une semaine).

---
**Remarque** :
Si les trois agents ne travaillent que le lundi, mardi et mercredi, la contrainte "Chloé travaille le lendemain du jour d’Alice" implique que :
- Alice travaille le **mardi** (car elle ne peut pas travailler le lundi, sinon Chloé le mercredi, mais Bruno ne travaille pas le lundi).
- Bruno travaille alors le **mercredi**.
- Chloé travaille le **mercredi suivant** (hors cadre des trois jours), ce qui n’est pas possible.

**Solution valide dans le cadre des trois jours** :
Il semble que la contrainte ne soit pas compatible avec trois agents travaillant uniquement le lundi, mardi et mercredi. Il faut donc supposer que les jours sont étendus à une semaine plus large (ex. : Alice le mardi, Chloé le mercredi suivant, etc.).

---
**Réponse finale (en supposant une extension des jours)** :
- **Alice** : **Mardi**
- **Bruno** : **Mercredi**
- **Chloé** : **Jeudi** *(le lendemain du mardi d’Alice)*.

Si les contraintes doivent rester strictement dans les trois jours, il n’existe pas de solution possible.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse : elle attribue « Alice : Mardi », « Bruno : Mercredi », « Chloé : Jeudi », alors que la référence attend Alice le lundi, Chloé le mardi et Bruno le mercredi ; elle conclut à tort qu'« il n'existe pas de solution possible » dans les trois jours et sa justification est incohérente.
- Inventions : Chloé travaille le jeudi (jour hors du cadre lundi-mardi-mercredi de l'énoncé); Hypothèse d'une « extension des jours à une semaine plus large », absente de l'énoncé; Affirmation qu'il n'existe pas de solution dans le cadre des trois jours
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
### **Heures d'ouverture par semaine**

#### **1. Calcul des heures d'ouverture selon les jours**
- **Lundi, mardi, jeudi et vendredi** :
  - **Matin** : 8 h 30 → 12 h 15 → **3 h 45**
  - **Après-midi** : 13 h 45 → 17 h → **3 h 15**
  - **Total par jour** : 3 h 45 + 3 h 15 = **6 h 60 = 6 h 30**

- **Mercredi** :
  - **Fermé l'après-midi** (13 h 45 → 17 h).
  - **Seule la matinée** : 8 h 30 → 12 h 15 → **3 h 45**

#### **2. Heures totales par semaine**
- **4 jours ouvrés complets** (Lundi, Mardi, Jeudi, Vendredi) × 6 h 30 = **25 h 12**
- **1 jour partiel** (Mercredi) × 3 h 45 = **3 h 45**
- **Total hebdomadaire** : 25 h 12 + 3 h 45 = **28 h 57**

*(Note : 60 secondes = 1 minute, donc 60 secondes en moins ne change pas significativement la durée en heures.)*

---
### **Durée moyenne d'ouverture par jour ouvré**

- **Nombre total de jours ouvrés** : 5 (Lundi à Vendredi).
- **Heures totales d'ouverture** : **28 h 57** (soit 28,95 heures).
- **Moyenne par jour** : 28 h 57 ÷ 5 ≈ **5 h 49** (soit **5 heures et 49 minutes**).

---
### **Résumé**
- **Ouverture hebdomadaire totale** : **28 heures et 57 minutes**.
- **Moyenne par jour ouvré** : **5 heures et 49 minutes**.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse : elle calcule « 3 h 45 + 3 h 15 = 6 h 60 = 6 h 30 » au lieu de 7 h et donne « Total hebdomadaire : 28 h 57 » et « Moyenne par jour : 5 h 49 », alors que la référence attend 31 h 45 et 6 h 21.
- Inventions : 6 h 60 = 6 h 30; 4 × 6 h 30 = 25 h 12; Total hebdomadaire : 28 h 57; Note : 60 secondes = 1 minute, donc 60 secondes en moins ne change pas significativement la durée; Moyenne par jour : 5 h 49
- Confiance : haute

**Juge second** : juge

- `exactitude` : 0 — La réponse contient des erreurs de calcul (ex. : 6 h 60 = 6 h 30, total hebdomadaire incorrect de 28 h 57 au lieu de 31 h 45, moyenne de 5 h 49 au lieu de 6 h 21) et ne respecte pas les étapes de référence (3 h 45 × 5 matins et 3 h 15 × 4 après-midi).
- Inventions : 25 h 12 (calcul incorrect des 4 jours ouvrés complets); 28 h 57 (total hebdomadaire erroné); 5 h 49 (moyenne incorrecte par jour ouvré); 6 h 60 = 6 h 30 (conversion erronée)
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
Voici la liste chronologique des étapes prévues **après le comité de pilotage**, dans l'ordre et sous la forme demandée :

- **30 avril** : Validation du cahier des charges.
- **15 mai** : Lancement de l'appel d'offres.
- **20 juin** : Réception des candidatures.
- **3 juillet** : Réunion de la commission.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — Les quatre étapes attendues sont présentes au format « date : action », dans l'ordre chronologique (30 avril, 15 mai, 20 juin, 3 juillet), sans le comité du 4 avril ni le vote du budget ; l'omission de « au plus tard » et la formule « Réception des candidatures » pour une date limite (« jusqu'au 20 juin ») restent des imprécisions mineures, sans ajout ni étape inventée.
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
Voici les réponses basées sur les passages fournis :

### **Qu’est-ce que la Garantie Visale ?**
La **Garantie Visale** est une **caution locative gratuite** proposée par **Action Logement** pour certains logements en **métropole, DROM ou à Saint-Martin** ([1], [2], [3], [4], [5]).
Elle permet au locataire de bénéficier d’une garantie contre :
- **Les impayés de loyer** ([1], [2], [3]).
- **Les dégradations locatives** ([1], [2], [3]).

Pour en bénéficier, le locataire doit obtenir le **visa d’Action Logement** et le bailleur doit accepter l’acte de cautionnement ([1], [2], [3], [5]).

---

### **Que se passe-t-il si la locataire ne peut plus payer son loyer ?**
Si la locataire ne peut plus payer son loyer avec la Garantie Visale :
1. **Action Logement verse d’abord le montant dû au bailleur** ([1], [2], [3]).
2. **Elle se fait ensuite rembourser par le locataire** ([1], [2], [3]).

---
### **À vérifier pour la locataire :**
- **Son éligibilité** :
  - Elle doit avoir un **contrat de travail en cours** (ou une promesse d’embauche dans les 3 mois) ou être **salariée du secteur privé** (CDD, CDI, intérim, etc.) ([2], [3]).
  - Le logement doit respecter les **montants maximaux de loyer** (ex. : **1 365 € max** en métropole pour un salarié avec un salaire net ≤ 1 710 €/mois) ([2], [3]).
  - Si elle est **colocataire**, chaque personne doit faire une demande individuelle ([2]).
- **La demande doit être faite dans les 6 mois suivant l’embauche ou la mutation** ([2], [3]).

---
### **Que faire si la locataire ne respecte pas ses obligations ?**
Si la locataire ne rembourse pas Action Logement après un impayé ou des dégradations, **le bailleur peut se retourner contre elle directement** ([1], [2], [3]).

---
### **Recommandation pour l’Agent :**
Pour confirmer les détails précis (montant exact du loyer, ressources, etc.), il est conseillé de :
- **Vérifier les justificatifs fournis par la locataire** (contrat de travail, revenus, etc.).
- **Consulter le site officiel** (Visale.fr) pour les dernières règles ([4]).

Si la locataire n’est pas éligible ou ne respecte pas les conditions, elle devra alors trouver une autre garantie (comme une caution classique).

Sources citées :
- Garantie Visale : caution pour le locataire (impayés et dégradations) — https://www.service-public.gouv.fr/particuliers/vosdroits/F33453
- Garantie Visale : caution pour le locataire (impayés et dégradations) — https://www.service-public.gouv.fr/particuliers/vosdroits/F33453
- Garantie Visale : caution pour le locataire (impayés et dégradations) — https://www.service-public.gouv.fr/particuliers/vosdroits/F33453
- Garantie Visale : caution pour le locataire (impayés et dégradations) — https://www.service-public.gouv.fr/particuliers/vosdroits/F33453
- Garantie Visale : caution pour le locataire (impayés et dégradations) — https://www.service-public.gouv.fr/particuliers/vosdroits/F33453
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Les quatre éléments clés sont présents, mais la réponse contredit le mécanisme décrit par la source : « le bailleur peut se retourner contre elle directement ». Selon la référence, c'est Action Logement qui paie le bailleur, puis se fait rembourser par la locataire. S'y ajoutent des conditions d'éligibilité chiffrées invérifiables.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F33453) traite précisément de la garantie Visale et correspond à la source attendue.
- Inventions : Si la locataire ne rembourse pas Action Logement, le bailleur peut se retourner contre elle directement; Elle doit avoir un contrat de travail en cours (ou une promesse d'embauche dans les 3 mois) ou être salariée du secteur privé; 1 365 € max en métropole pour un salarié avec un salaire net ≤ 1 710 €/mois; Si elle est colocataire, chaque personne doit faire une demande individuelle; La demande doit être faite dans les 6 mois suivant l'embauche ou la mutation; Consulter le site officiel (Visale.fr)
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
Voici les réponses basées sur les passages fournis :

1. **Oui, le bénéficiaire peut cumuler son AAH et son salaire**, mais sous conditions :
   - Pendant les **6 premiers mois** de travail, il continue de percevoir **l’AAH complète** sans que ses revenus professionnels soient pris en compte.
   - **À partir du 7ᵉ mois**, l’AAH est réduite en fonction de ses revenus nets imposables déclarés à la Caf ou MSA.
     - **Jusqu’à 560,11 € net/mois** : 20 % de ce montant sont déduits de l’AAH (soit 80 % de cette partie est retenue).
     - **Au-delà de 560,11 € net/mois** : 60 % de cette partie est déduite de l’AAH (soit 40 % est conservée).
   → [Passage 1]

2. **Pour calculer l’AAH**, les revenus nets imposables déclarés trimestriellement sont pris en compte, et une déclaration est obligatoire tous les 3 mois.
   → [Passage 1]

3. **Si le salarié travaille uniquement en milieu ordinaire (entreprise classique)**, les règles générales s’appliquent (pas de plafond spécifique comme en Ésat).
   → Les abattements s’appliquent sur ses revenus nets imposables déclarés, sans distinction avec un Ésat.

**À vérifier** :
- Le bénéficiaire doit déclarer ses revenus trimestriellement à sa **Caf ou MSA** pour que l’AAH soit ajustée correctement.
- Si le salarié travaille **simultanément en Ésat et en milieu ordinaire**, les deux rémunérations sont prises en compte séparément avec leurs abattements respectifs.
  → [Passage 1 et 3]

**Recommandation** :
Pour une estimation précise, il est conseillé de **simuler ses droits** via le simulateur officiel ou de **contacter sa Caf/MSA** pour confirmer les montants exacts.
→ [Passage 1]

---
**À noter** :
- Aucune perte automatique de l’AAH n’est prévue dès la signature du contrat, mais une réduction progressive intervient après 6 mois.
- Les plafonds spécifiques (comme ceux pour les Ésat) ne s’appliquent pas ici.

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

- `exactitude` : 1 — Les quatre éléments clés figurent dans la réponse : cumul en milieu ordinaire, AAH complète les 6 premiers mois, taux de 20 % et 60 % autour de 560,11 €, déclaration trimestrielle à la Caf ou à la MSA ; mais les parenthèses « soit 80 % de cette partie est retenue » et « soit 40 % est conservée » contredisent la référence (« 20 % retenus ») et rendent le calcul de l'AAH différentielle imprécis.
- `pertinence_source` : 0 — La sortie indique « Sources citées : aucune » et ne renvoie qu'à des « Passage 1 / 3 » non identifiés ; la source attendue (service-public.gouv.fr F21615) n'est pas citée.
- Inventions : « soit 80 % de cette partie est retenue » / « soit 40 % est conservée » : interprétation contraire à la référence; « pas de plafond spécifique comme en Ésat » : non vérifiable dans les références; « les deux rémunérations sont prises en compte séparément avec leurs abattements respectifs » (cumul Ésat et milieu ordinaire) : non vérifiable; Base de calcul sur les « revenus nets imposables » : non présente dans les références; Renvoi à un « simulateur officiel » : non vérifiable
- Confiance : moyenne

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
D'après les passages fournis, voici comment calculer le reste à charge de l'épouse pour l'Apa dans votre situation :

### **1. Calcul des ressources du couple pour l'Apa**
- Les **ressources prises en compte** du couple sont de **3 400 €/mois**.
- Pour déterminer le **montant total des ressources du couple**, il faut diviser ce montant par **1,7** (selon le passage [1] et [3]).
  → **Montant total des ressources du couple = 3 400 € / 1,7 ≈ 2 000 €/mois** [1, 3].

### **2. L'APL n'est pas prise en compte pour le reste à charge de l'Apa**
- Les **ressources exclues** pour le calcul du reste à charge de l'Apa incluent :
  - **Les aides au logement (APL, ALS)** [1, 3, 5].
  → **L'APL ne figure pas dans la liste des ressources prises en compte pour l'Apa**, donc elle n'affecte pas le calcul du reste à charge de l'Apa.

### **3. Tranche de ressources et calcul du reste à charge**
- Le couple a un **montant total de ressources de 2 000 €/mois** (après ajustement).
- Ce montant se situe **dans la tranche "supérieure à 933,89 € et jusqu'à 3 439,31 €"** [1, 3, 5].
- Dans cette tranche, le **reste à charge varie progressivement de 0 % à 90 % du montant du plan d'aide accepté** [1, 3, 5].

### **Ce qui reste à vérifier**
- Le **montant exact du plan d'aide accepté** par l'Apa (pour appliquer le pourcentage du reste à charge).
- Si l'épouse vit **à domicile** ou en **établissement médico-social** (les règles diffèrent légèrement selon le contexte).

---
**Recommandation** :
Pour affiner le calcul, consultez :
- Le **plan d'aide accepté** par l'Apa (via votre dossier).
- Le **GIR (Groupe Iso-Ressources)** de l'épouse si elle est hébergée en Ehpad (pour vérifier si le tarif dépendance est différent).

*(L'APL ne modifie pas le reste à charge de l'Apa, mais elle peut réduire le coût global du logement.)*

Sources citées :
- Apa : quel est le montant de votre reste à charge ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F1802
- Allocation personnalisée d'autonomie (Apa) — https://www.service-public.gouv.fr/particuliers/vosdroits/F10009
- Apa : quel est le montant de votre reste à charge ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F1802
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La division par 1,7, l'exclusion de l'APL, le calcul 3 400 € / 1,7 = 2 000 € et la tranche progressive de 0 % à 90 % sont justes, mais le cinquième élément clé manque (aucun reste à charge jusqu'à 933,89 € et 90 % au-delà de 3 439,31 €) ; la réponse s'interroge aussi à tort sur le lieu de vie (« Si l'épouse vit à domicile ou en établissement »), alors que l'entrée précise le domicile.
- `pertinence_source` : 1 — La source F1802 citée, attendue par les références, traite directement du calcul du reste à charge de l'Apa.
- Inventions : « le GIR de l'épouse si elle est hébergée en Ehpad (pour vérifier si le tarif dépendance est différent) » : non vérifiable dans les références et hors sujet pour un maintien à domicile; « elle peut réduire le coût global du logement » : affirmation non vérifiable dans les références
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
Voici ce que vous pouvez expliquer à l’usager en vous basant sur les passages fournis :

1. **Raison de l’amende majorée** :
   L’usager reçoit une amende majorée **car son adresse sur la carte grise n’était pas à jour** lors de l’infraction [1, 2, 3, 4, 5].
   → Il n’a pas reçu l’avis de contravention initial car le véhicule était immatriculé à une adresse incorrecte.

2. **Procédure pour contester la majoration** :
   - Il doit **justifier son changement d’adresse** auprès du service en charge des cartes grises dans un délai de **3 mois** après la réception de l’avis d’amende majorée.
   - Une fois cette justification faite, il a **45 jours** pour payer le montant initial de l’amende (avant la majoration) [1].
   - **Attention** : Si le paiement est effectué après ce délai, il ne bénéficiera plus du montant minoré [1].

3. **Ce qui reste à vérifier** :
   - Les passages ne précisent pas comment **contester l’infraction elle-même** (ex. : erreur de radar), mais seulement la majoration liée à l’adresse non mise à jour.
   - Si l’usager souhaite contester l’infraction (et non la majoration), il devra suivre la procédure spécifique pour réclamation (en ligne ou par courrier) en se basant sur l’avis d’amende majorée [4].

---
**Recommandation** :
Pour une réponse complète, l’usager doit consulter :
- Le service en charge des cartes grises pour confirmer son changement d’adresse.
- L’avis d’amende majorée pour les détails sur la réclamation (ex. : formulaire à remplir).

Sources citées :
- Comment contester une amende majorée si l’on n’a pas reçu l'avis de contravention ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F18510
- Comment contester une amende majorée si l’on n’a pas reçu l'avis de contravention ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F18510
- Comment contester une amende majorée si l’on n’a pas reçu l'avis de contravention ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F18510
- Comment contester une amende majorée si l’on n’a pas reçu l'avis de contravention ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F18510
- Comment contester une amende majorée si l’on n’a pas reçu l'avis de contravention ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F18510
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie contredit la source en écrivant « Si le paiement est effectué après ce délai, il ne bénéficiera plus du montant minoré », alors que le montant minoré est perdu dans tous les cas ; elle fait aussi courir le délai de 3 mois à partir de la « réception » au lieu de l'« envoi » de l'avis majoré, et omet la condition liée au radar automatique ainsi que la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F18510) traite précisément de la contestation d'une amende majorée en cas de non-réception de l'avis de contravention.
- Inventions : « Si le paiement est effectué après ce délai, il ne bénéficiera plus du montant minoré » : condition non présente dans la référence, qui exclut le montant minoré dans tous les cas; Délai de 3 mois « après la réception de l'avis d'amende majorée » : la référence indique « à partir de la date d'envoi »
- Confiance : moyenne

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
Voici les réponses basées sur les passages fournis :

1. **Délai pour le recensement citoyen** :
   - Votre fils doit faire son recensement citoyen **entre le 12 septembre 2026 et le 31 décembre 2026** (car il a 16 ans le 12 septembre 2026).
   - [À vérifier : si le recensement est fait après le 31 décembre 2026, il devra le faire avant ses 25 ans, selon le passage [2].]

2. **Comment le faire ?** :
   - Il peut le faire **en ligne** ou **en mairie**.
     - En ligne : l’attestation sera disponible dans son **compte personnel en ligne** ou envoyée par la mairie sous 10 jours.
     - En mairie : la mairie lui remet l’attestation **le jour-même**.
   - [Source : passages [1] et [2].]

3. **À quoi sert l’attestation de recensement ?** :
   - Elle sert à prouver qu’il a effectué cette démarche obligatoire.
   - Elle est nécessaire pour des démarches ultérieures (ex. : inscription en lycée, service national, etc.).
   - [Pas de précision explicite sur son utilité dans les passages fournis, mais elle est liée à des obligations administratives ultérieures.]

**À signaler** :
- Si le recensement n’est pas fait dans les 3 mois suivant ses 16 ans, il devra le faire avant ses 25 ans (selon [2]).
- Aucune mention ne précise si l’attestation est obligatoire pour des démarches spécifiques (ex. : permis de conduire, contrat de travail), mais elle est souvent requise pour des étapes administratives ultérieures.

**Conseil** :
Pour des précisions sur les usages de l’attestation, consultez le site officiel du **Service Public** ([F870](https://www.service-public.gouv.fr/particuliers/vosdroits/F870)) ou contactez la mairie pour confirmation.

Sources citées :
- Recensement citoyen — https://www.service-public.gouv.fr/particuliers/vosdroits/F870
- Recensement citoyen — https://www.service-public.gouv.fr/particuliers/vosdroits/F870
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Plusieurs éléments clés manquent : les pièces à fournir (pièce d'identité, livret de famille) et la possibilité pour un représentant légal de faire la démarche ne sont pas mentionnées. L'usage de l'attestation est faux ou imprécis (« inscription en lycée, service national ») au lieu de l'inscription avant 18 ans aux examens et concours administratifs.
- `pertinence_source` : 1 — La source citée, service-public.gouv.fr F870, est celle attendue et traite bien du recensement citoyen.
- Inventions : Elle est nécessaire pour des démarches ultérieures (ex. : inscription en lycée, service national, etc.); elle est souvent requise pour des étapes administratives ultérieures
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
D'après les passages fournis dans l'Index local, voici ce que vous pouvez indiquer à l'usagère concernant son compagnon décédé :

1. **Statut légal du mariage posthume** :
   Les passages ne mentionnent **pas** explicitement si le mariage à titre posthume est possible en France. Les informations disponibles concernent uniquement les **démarches après un décès** (comme organiser les obsèques ou gérer les cendres), sans traiter des aspects juridiques spécifiques comme le mariage posthume.
   → **À vérifier** auprès du **service juridique des tribunaux** ou du **ministère de la Justice** pour une réponse précise.

2. **Démarches à engager** :
   Les passages indiquent que les proches doivent :
   - **Organiser les obsèques** (cimetière, dispersion, etc.) [1].
   - **Informer les organismes** (banque, employeur, etc.) [2, 3, 4].
   - **Prévenir les héritiers potentiels** (famille, proches) pour gérer la succession [3].

   Aucune mention n’est faite sur la possibilité de mariage posthume, mais l’usagère pourrait envisager :
   - **Un contrat de mariage** (si elle souhaite officialiser sa relation avec les héritiers du défunt).
   - **Une demande de reconnaissance de paternité/maternité** (si applicable, via les services de l’État civil).

---
**Recommandation** :
L’usagère doit consulter :
- **Le site officiel du ministère de la Justice** ([https://www.justice.gouv.fr](https://www.justice.gouv.fr)) pour les règles sur les unions posthumes.
- **Un notaire** pour évaluer les implications légales de sa situation (succession, droits successoraux).

Sources citées :
- Un proche est décédé — https://www.service-public.gouv.fr/particuliers/vosdroits/F16507
- Un proche est décédé — https://www.service-public.gouv.fr/particuliers/vosdroits/F16507
- Un proche est décédé — https://www.service-public.gouv.fr/particuliers/vosdroits/F16507
- Un proche est décédé — https://www.service-public.gouv.fr/particuliers/vosdroits/F16507
```

### Contrôles automatiques

```text
{
  "urls_inventees": [
    "https://www.justice.gouv.fr"
  ]
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie indique bien que les passages ne traitent pas du mariage posthume, mais elle invente des pistes erronées : « Un contrat de mariage (si elle souhaite officialiser sa relation avec les héritiers du défunt) » est juridiquement absurde, et la reconnaissance de paternité est hors sujet. Elle oriente aussi vers le « service juridique des tribunaux » ou le « ministère de la Justice » plutôt que vers l'état civil de la mairie, et omet la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 0 — La seule source citée, la fiche F16507 « Un proche est décédé », ne traite pas du point demandé (le mariage posthume), et elle est répétée quatre fois.
- `cas_sans_reponse` : 0 — Malgré l'aveu initial d'absence de source, l'Assistant invente des démarches (« Un contrat de mariage », « reconnaissance de paternité/maternité ») et des autorités compétentes. Il présente aussi le site du ministère de la Justice comme donnant « les règles sur les unions posthumes », ce qui ne correspond pas à l'orientation attendue.
- Inventions : Un contrat de mariage (si elle souhaite officialiser sa relation avec les héritiers du défunt); Une demande de reconnaissance de paternité/maternité (si applicable, via les services de l'État civil); À vérifier auprès du service juridique des tribunaux ou du ministère de la Justice; Le site officiel du ministère de la Justice (https://www.justice.gouv.fr) pour les règles sur les unions posthumes; Informer les organismes (banque, employeur, etc.) [2, 3, 4] et Prévenir les héritiers potentiels [3] : références numérotées attribuées à une source unique non vérifiable
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
D'après les passages fournis ([1], [2], [3]) :

### **Pour un montant ≤ 300 € (comme votre cas de 250 €)**
✅ **Oui, c'est possible** de payer en espèces.
- **Conditions** :
  - Votre avis doit comporter un **QR code** et la mention *« payable auprès d’un buraliste »*.
  - Vous recevrez un **reçu** pour justifier le paiement.
- **Moyens** :
  - **En espèces** ou **par carte bancaire** chez un **buraliste partenaire** (vérifiez la présence du QR code sur votre avis).

---
### **Si le montant dépassait 300 €**
❌ **Non, ce mode de paiement n’est pas autorisé** :
- Selon les passages ([1], [2], [3]), **seuls les paiements en ligne ou par prélèvement automatique** sont obligatoires pour les montants supérieurs à 300 €.
- Les autres méthodes (chèque, virement, TIP, etc.) ne sont pas mentionnées pour ce cas précis.

---
### **Recommandation**
- Pour un montant ≤ 300 €, vérifiez bien la présence du **QR code** sur votre avis avant de vous rendre chez un buraliste.
- Pour un montant > 300 €, vous devrez obligatoirement payer **en ligne** ou par **prélèvement automatique**.

*(Si votre avis ne mentionne pas explicitement le QR code, contactez le service des impôts pour confirmation.)*

Sources citées :
- Comment payer ses impôts locaux ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F31686
- Comment payer ses impôts locaux ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F31686
- Comment payer ses impôts locaux ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F31686
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse traite correctement le paiement en espèces ou par carte chez un buraliste partenaire jusqu'à 300 €, la condition du QR code avec la mention « payable auprès d'un buraliste » et l'obligation de payer en ligne ou par prélèvement au-delà de 300 €. Elle omet toutefois l'élément clé des autres moyens possibles jusqu'à 300 € (chèque à l'ordre du Trésor public avec le talon, TIP Sepa, virement, prélèvement).
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F31686, « Comment payer ses impôts locaux ? ») est la source attendue et traite exactement du point demandé.
- Inventions : « contactez le service des impôts pour confirmation » : orientation non présente dans les références (mineure)
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
Voici les réponses basées sur les passages fournis :

1. **Exonération des enfants** :
   Les enfants de moins de 18 ans sont **exonérés de la taxe de séjour** [1].
   → Les deux enfants de 9 et 13 ans n’ont donc pas à payer.

2. **Qui doit payer ?** :
   La taxe de séjour doit être payée par le **vacancier** (ici, le couple) dans le **meublé de tourisme** concerné [1].
   → Le couple doit collecter la taxe auprès d’eux-mêmes (ou du professionnel de réservation si utilisé).

3. **Comment connaître le montant ?** :
   Le montant de la taxe de séjour dépend de la commune et peut être vérifié :
   - **En mairie** ou à l’**office du tourisme** concerné [1].
   - Via un **téléservice** (référence dans [1] et [2]).
   → *À vérifier* : Les passages ne précisent pas si le simulateur en ligne est accessible gratuitement pour les particuliers.

4. **À qui reverser ?** :
   Le montant perçu doit être reversé **à la commune** [1, 2, 3].

---
**À préciser** :
- Les passages ne mentionnent pas si la taxe est automatiquement prélevée par le meublé ou la plateforme de réservation (ex. Airbnb). Si c’est le cas, la plateforme pourrait gérer le paiement et le reversement.
- Aucune information sur les éventuelles taxes additionnelles (comme en Île-de-France) ou les montants exacts.

**Recommandation** :
Pour confirmer les montants et modalités exactes, consultez directement la **mairie de la commune** ou l’**office du tourisme** concerné.

Sources citées :
- Qu'est-ce que la taxe de séjour ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F2048
- Faire de sa résidence secondaire une location de vacances (meublé de tourisme) — https://www.service-public.gouv.fr/particuliers/vosdroits/F2043
- Faire de sa résidence principale une location de vacances (meublé de tourisme) — https://www.service-public.gouv.fr/particuliers/vosdroits/F33175
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie commet une erreur sur le circuit de paiement (« Le couple doit collecter la taxe auprès d'eux-mêmes ») au lieu d'indiquer qu'elle se paie au logeur ou au propriétaire, qui la reverse à la commune ; elle omet aussi le « par personne et par nuit », la variation selon le type et le classement de l'hébergement, ainsi que l'affichage chez le logeur et la mention sur la facture.
- `pertinence_source` : 1 — La fiche F2048 « Qu'est-ce que la taxe de séjour ? », qui est la source attendue, est citée et traite directement du point demandé.
- Inventions : Montant consultable via un « téléservice » ou un « simulateur en ligne » (non vérifiable dans les références); « Le couple doit collecter la taxe auprès d'eux-mêmes » (contraire à la référence); Le montant « dépend de la commune » présenté comme seul critère, sans mention du type d'hébergement ni du classement
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
Voici les réponses basées sur les passages fournis :

1. **Obligation de payer la taxe sur les logements vacants (TLV) :**
   - Oui, le propriétaire doit payer la **taxe annuelle sur les logements vacants (TLV)**.
   - Ce logement est concerné car il est **non meublé, inoccupé depuis au moins 1 an (depuis janvier 2024)** et situé dans une **commune en zone tendue** (définie par un déséquilibre marqué entre offre et demande de logements ou une proportion élevée de logements vacants) **[1, 2]**.

2. **Calcul de la taxe :**
   - La taxe est calculée sur la **valeur locative cadastrale** de l’appartement.
   - Le montant est obtenu en multipliant cette valeur par un taux d’imposition :
     - **17 % pour la 1re année d’imposition** (2025, car l’inoccupation commence en janvier 2024) ;
     - **34 % pour les années suivantes** (2026 et au-delà) **[4]**.
   - *Note :* Si le logement était occupé en 2024, la taxe ne serait pas applicable pour 2025. Ici, comme il est inoccupé depuis janvier 2024, la 1re année d’imposition (2025) est déjà passée, et la taxe pour 2026 est calculée au taux de 34 %.

3. **Avis reçu :**
   - L’avis indique bien le montant de la TLV pour 2026, et il peut être consulté sur l’espace personnel de télédéclarant sur **impots.gouv.fr** **[5]**.

---
**À vérifier :**
- Confirmez que la commune est bien **en zone tendue** (définition précise : zone d’urbanisation continue > 50 000 habitants ou déséquilibre marqué entre offre/demande de logements) **[1]**.
- Vérifiez si le logement a été **mis en vente dès janvier 2024** (sans achèvement) : si le propriétaire a tenté de le vendre mais n’a pas trouvé d’acquéreur, cela ne change pas le statut de "vacant" pour l’imposition.

---
**Rappel :** Pour les détails sur le montant exact, consultez l’avis ou votre espace personnel sur impots.gouv.fr. Pour les communes concernées, vérifiez la liste officielle sur le site de votre mairie ou le site des impôts locaux.

Sources citées :
- Taxe annuelle sur les logements vacants (TLV) et taxe d'habitation sur les logements vacants (THLV) — https://www.service-public.gouv.fr/particuliers/vosdroits/F17293
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

- `exactitude` : 0 — Erreur factuelle grave contredisant la source : la sortie affirme « Oui, le propriétaire doit payer » et que la mise en vente sans acquéreur « ne change pas le statut de "vacant" pour l'imposition », alors que la vacance indépendante de sa volonté (mise en vente au prix du marché sans acquéreur) ouvre droit à exonération ; la réclamation et le sursis de paiement sont absents, et le taux de 34 % est affirmé pour 2026 sans réserve, alors qu'une 1re année d'imposition en 2025 n'est pas établie.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F17293) correspond à la source attendue et traite bien de la TLV.
- Inventions : Affirmation que la mise en vente sans acquéreur « ne change pas le statut de "vacant" pour l'imposition », contraire à la référence; Affirmation que 2025 est la 1re année d'imposition et que 2026 est taxée à 34 %, non vérifiable dans l'entrée; Définition de la zone tendue « zone d'urbanisation continue > 50 000 habitants », non vérifiable dans les références; Consultation de l'avis sur l'espace personnel « de télédéclarant » sur impots.gouv.fr, non vérifiable dans les références
- Confiance : haute

**Juge second** : juge

- `exactitude` : 1 — Un élément clé est imprécis : l'exonération possible en cas de mise en vente au prix du marché sans acquéreur est mentionnée dans les références mais absente de la réponse, ce qui constitue une omission. La réponse indique à tort que la taxe est due sans nuance.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr) est pertinente et traite bien du sujet de la TLV, conformément aux références attendues.
- Inventions : L'affirmation selon laquelle le propriétaire doit payer la TLV sans mentionner l'exonération possible en cas de mise en vente infructueuse au prix du marché; La mention de l'avis consultable sur impots.gouv.fr et la référence à un espace personnel de télédéclarant [5], non vérifiables dans les références; La précision sur la définition de la zone tendue (urbanisation continue > 50 000 habitants), non présente dans les références
- Confiance : moyenne

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
Voici les réponses basées sur les passages fournis :

1. **Durée minimale légale hebdomadaire pour un salarié en CDI à temps partiel** :
   En l’absence de convention collective ou d’accord de branche, la durée minimale légale est de **24 heures par semaine** [1, 2].
   *(Si une convention collective ou un accord de branche fixe une durée inférieure, celle-ci s’applique.)*

2. **Possibilité de travailler moins de 24 heures par semaine** :
   Elle peut demander une **durée minimale inférieure à 24 heures** sous certaines conditions, à condition que cela soit justifié par :
   - **Des contraintes personnelles** (raisons de santé ou familiales) : sa demande doit être écrite et motivée, mais l’employeur n’est pas obligé d’accepter [1, 2].
   - **Un cumul d’activités** : si elle souhaite combiner plusieurs emplois pour atteindre un temps plein équivalent, elle doit faire une demande écrite motivée [1, 2].
   - **Une poursuite d’études** : si elle a moins de 26 ans, elle peut demander à travailler moins de 24 heures pour étudier, mais l’employeur n’est pas obligé d’accepter [1, 2].

3. **Cas particuliers à vérifier** :
   - Si elle est embauchée dans une **branche avec une convention collective spécifique**, la durée minimale peut être différente (à confirmer auprès de la convention concernée).
   - Si elle travaille dans un **secteur où des dérogations sont possibles** (ex. : remplacement d’un collègue absent), elle peut être dispensée de respecter la durée minimale légale [1, 2].

**Recommandation** :
Pour une réponse précise, vérifiez si une convention collective s’applique à son entreprise et consultez les accords internes. Si nécessaire, elle peut solliciter son employeur pour une dérogation écrite motivée.

Sources citées :
- Salarié à temps partiel : quelle est la durée hebdomadaire minimale de travail ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F1915
- Temps partiel d'un salarié dans le secteur privé — https://www.service-public.gouv.fr/particuliers/vosdroits/F32428
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse donne les trois éléments clés : renvoi à la convention ou à l'accord de branche, 24 heures à défaut, et demande écrite et motivée pour contraintes personnelles ou cumul d'activités sans obligation pour l'employeur. Elle ajoute cependant des affirmations non vérifiables dans les références, notamment « si elle a moins de 26 ans… l'employeur n'est pas obligé d'accepter », et une imprécision sur le cumul (« pour atteindre un temps plein équivalent »). La mention « Ne vaut pas avis juridique » est absente.
- `pertinence_source` : 1 — La source F1915 citée est exactement la source attendue et traite de la durée hebdomadaire minimale du temps partiel.
- Inventions : Poursuite d'études pour les moins de 26 ans : « l'employeur n'est pas obligé d'accepter » (absent des références); Dérogation pour « remplacement d'un collègue absent » permettant d'être dispensé de la durée minimale (absent des références); Cumul d'activités « pour atteindre un temps plein équivalent » (absent des références)
- Confiance : moyenne

**Juge second** : juge

- `exactitude` : 1 — Un élément clé est imprécis : la sortie mentionne des conditions supplémentaires (poursuite d'études pour les moins de 26 ans) qui ne figurent pas dans les références, sans erreur grave mais avec une légère invention.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr/F1915) traite bien du sujet, mais une seconde source (F32428) est hors sujet pour la question posée (durée minimale spécifique).
- Inventions : La possibilité de travailler moins de 24 heures pour des raisons de poursuite d'études si elle a moins de 26 ans; Les dérogations possibles dans certains secteurs (ex. : remplacement d'un collègue absent)
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
Voici la procédure et les délais applicables pour contester le refus d’inscription sur la liste électorale, **hors période électorale**, après notification par courrier du maire :

1. **Recours administratif préalable obligatoire** :
   - **Délai** : **5 jours** à compter de la réception de la notification du refus.
   - **À faire** : Saisir la **commission de contrôle des listes électorales** de la commune.
   - **Forme** : Par courrier ou mail avec accusé de réception.
   - **Documents à joindre** :
     - Copie de la notification du maire.
     - Preuve du bien-fondé de votre inscription (ex. : justificatif de domicile, pièce d’identité, etc.).
   - **Informations à mentionner** :
     - Vos nom, prénom, adresse, date et lieu de naissance.
     - Date et nature de la décision du maire.
   - [Source : passage [3]]

2. **Si la commission ne répond pas dans les 30 jours** (hors période électorale) :
   - Vous pouvez **saisir directement le tribunal judiciaire** pour un recours contentieux.
   - **Délai** : **7 jours** après la notification de refus de la commission ou après l’absence de réponse.
   - [Source : passage [5]]

3. **Si vous recevez une décision de la commission** :
   - Vous pouvez **contester cette décision devant le tribunal judiciaire** dans les **7 jours** après la notification.
   - [Source : passage [5]]

4. **Si vous recevez une décision du tribunal judiciaire** :
   - Vous pouvez former un **pourvoi en cassation** dans les **10 jours** après la notification de cette décision.
   - [Source : passage [4]]

---
**À vérifier** :
- Aucune mention dans les passages ne précise si la commission de contrôle des listes électorales est une instance locale spécifique (ex. : composée de membres désignés par le maire ou d’autres autorités). Pour confirmer son existence et ses modalités de saisine, il faudrait consulter :
  - Le **règlement municipal** de la commune.
  - Le **service des élections** de la mairie ou un **avocat spécialisé en droit électoral**.

Pour les détails sur la composition de cette commission, consultez directement la mairie ou un **service compétent en droit administratif** (ex. : préfecture ou tribunal administratif).

Sources citées :
- Que faire en cas de refus d'inscription ou de radiation de la liste électorale par le maire ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F34809
- Que faire en cas de refus d'inscription ou de radiation de la liste électorale par le maire ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F34809
- Que faire en cas de refus d'inscription ou de radiation de la liste électorale par le maire ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F34809
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse donne correctement le RAPO devant la commission sous 5 jours, l'envoi par courrier ou mail avec AR, les pièces à joindre, le délai de 30 jours, le recours au tribunal judiciaire sous 7 jours et le pourvoi en cassation sous 10 jours, mais elle omet le délai de décision du tribunal (« dans les 8 jours »). Elle ajoute aussi des orientations douteuses, comme le « règlement municipal » ou le « tribunal administratif » cité comme service compétent, et ne reprend pas la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — La source citée, la fiche F34809 de service-public.gouv.fr, traite précisément du refus d'inscription sur la liste électorale par le maire et correspond à la source attendue.
- Inventions : Informations à mentionner : « Vos nom, prénom, adresse, date et lieu de naissance. Date et nature de la décision du maire. »; Exemples de preuves : « justificatif de domicile, pièce d'identité »; Orientation vers le « règlement municipal » pour confirmer l'existence et les modalités de saisine de la commission; Orientation vers un « service compétent en droit administratif (ex. : préfecture ou tribunal administratif) »
- Confiance : moyenne

**Juge second** : juge

- `exactitude` : 2 — Tous les éléments clés sont présents et justes, sans erreur factuelle ni omission majeure. Les délais et procédures sont correctement repris de la référence.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr) est pertinente et traite bien du sujet demandé.
- Inventions : L'ajout d'informations non vérifiables dans la référence, comme les détails sur la composition de la commission de contrôle ('instance locale spécifique', 'membres désignés par le maire ou d’autres autorités') et les 'informations à mentionner' (nom, prénom, adresse, etc.), qui ne figurent pas dans les éléments clés ou la réponse de référence.; La suggestion de consulter le règlement municipal ou un avocat spécialisé, qui n'est pas mentionnée dans les références.
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
D'après les passages fournis, voici les réponses à votre question :

### **Droit à la prime à la naissance**
- **Oui**, le couple a droit à la prime à la naissance.
  - Le couple est considéré comme ayant **deux revenus** (chacun perçoit plus de 6 306 € en 2024).
  - Le revenu net catégoriel du foyer (54 000 €) est **inférieur au plafond pour 2 enfants en couple avec deux revenus** (56 478 €).
  - L'enfant à naître compte comme un enfant à charge supplémentaire (soit 2 enfants au total).
  - Le couple respecte donc les conditions de ressources pour bénéficier de la prime.
  [1], [2]

---

### **Montant de la prime**
- Le montant de la prime à la naissance est de **1 093,11 € par enfant**.
  - Comme il s'agit d'un deuxième enfant, la prime sera versée **pour 2 enfants** (soit 2 × 1 093,11 €).
  [1], [2]

---

### **Date de versement**
- La prime est versée **avant le dernier jour du mois civil suivant le 6ᵉ mois de grossesse**.
  - Si la déclaration de grossesse a eu lieu au **2ᵉ mois**, on considère que le 6ᵉ mois commence vers le **12ᵉ mois** (en supposant une grossesse de 9 mois).
  - Le versement aura donc lieu **avant le dernier jour du mois suivant le 12ᵉ mois** (soit avant le dernier jour du mois suivant la déclaration).
  *(Note : Les passages ne précisent pas exactement la date exacte de déclaration, mais on peut estimer que la grossesse est considérée comme étant au moins 6 mois avancée à ce stade.)*
  [1], [5]

---
### **Remarques complémentaires**
- Aucune mention dans les passages fournis ne précise si la future mère doit fournir une attestation médicale pour les naissances multiples (ici, il s'agit d'un seul enfant).
- Les passages ne précisent pas si la prime est versée sous forme de **Paje** ou directement par un autre organisme (à vérifier auprès du service compétent si nécessaire).
- Aucune information sur les éventuelles aides supplémentaires (comme la prime de déménagement) n'est disponible dans les passages fournis.

**Pour plus de précisions sur la date exacte de versement ou les démarches administratives**, consultez directement le site officiel du **Service Public** ([https://www.service-public.gouv.fr](https://www.service-public.gouv.fr)) ou contactez la **Caisse d’Allocations Familiales (CAF)** ou la **Maison Départementale des Personnes Handicapées (MDPH)** selon votre situation.

Sources citées :
- Je deviens parent — https://www.service-public.gouv.fr/particuliers/vosdroits/F16225
- Prestation d'accueil du jeune enfant (Paje) : prime à la naissance — https://www.service-public.gouv.fr/particuliers/vosdroits/F2550
- Prestation d'accueil du jeune enfant (Paje) : prime à la naissance — https://www.service-public.gouv.fr/particuliers/vosdroits/F2550
```

### Contrôles automatiques

```text
{
  "urls_inventees": [
    "https://www.service-public.gouv.fr"
  ]
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie commet une erreur factuelle grave sur le montant (« la prime sera versée pour 2 enfants (soit 2 × 1 093,11 €) ») alors que la prime de 1 093,11 € est due pour l'enfant à naître. Elle raisonne aussi de façon erronée sur le versement (« le 6ᵉ mois commence vers le 12ᵉ mois »). Enfin, elle ne valide pas les conditions de grossesse (examen prénatal, déclaration avant la fin du 3e mois).
- `pertinence_source` : 1 — La source citée F2550 (Paje : prime à la naissance) traite bien du point demandé et correspond à la source attendue.
- Inventions : La prime serait versée pour 2 enfants (2 × 1 093,11 €); Le 6ᵉ mois commencerait vers le 12ᵉ mois / versement avant le dernier jour du mois suivant la déclaration; Orientation vers la MDPH, sans rapport avec la question
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
D'après l'**Index local** sur data.gouv.fr, voici un jeu de données qui pourrait correspondre à vos besoins :

- **[Logements sociaux en France : données par commune](https://www.data.gouv.fr/fr/datasets/donnees-sur-les-logements-sociaux-en-france/)** (référence **[1](https://www.data.gouv.fr/fr/datasets/donnees-sur-les-logements-sociaux-en-france)**).
  - **Producteur** : Agence nationale de la rénovation urbaine (ANRU) et autres acteurs locaux.
  - **Date de dernière mise à jour** : À vérifier en ligne (le jeu de données est régulièrement mis à jour).

Si ce jeu ne contient pas les informations exactes sur la loi SRU et l'inventaire des logements sociaux par commune, je peux chercher d'autres pistes ou vous proposer des jeux de données complémentaires. Souhaitez-vous que je vérifie cette information en ligne ?

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "appariement": [
    null
  ],
  "appels_attendus": 1,
  "appels_valides": 0,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": false
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
Le jeu de données correspondant à votre recherche est le suivant :

- **Titre** : *Établissements habilités au titre de l'aide sociale à l'enfance (ASE)*
- **Producteur** : Département des Hauts-de-Seine
- **Date de dernière mise à jour** : Non précisée directement dans le résultat, mais le jeu est disponible sur le site.
- **Lien** : [Établissements habilités au titre de l'aide sociale à l'enfance (ASE)](https://www.data.gouv.fr/datasets/etablissements-habilites-au-titre-de-laide-sociale-a-lenfance-ase)

Ce jeu de données semble correspondre à votre demande. Souhaitez-vous consulter les ressources associées (comme les fichiers disponibles) pour accéder aux informations détaillées ?

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
Le jeu de données correspondant à l'évaluation du RSA de la **Cour des comptes** est :

- **Titre** : *Le revenu de solidarité active (RSA)*
- **Producteur** : Cour des comptes
- **Date de dernière mise à jour** : [Vérifiez sur data.gouv.fr pour la date exacte]
- **Lien** : [https://www.data.gouv.fr/datasets/le-revenu-de-solidarite-active-rsa](https://www.data.gouv.fr/datasets/le-revenu-de-solidarite-active-rsa)

Ce jeu contient **8 fichiers de ressources**.

Pour déterminer les départements couverts dans les données brutes, je vais consulter les ressources de ce jeu de données.Voici les informations demandées pour le jeu de données *Le revenu de solidarité active (RSA)* :

- **Nombre de fichiers** : Ce jeu contient **8 ressources** (fichiers), tous au format **CSV/UTF-8**.

- **Département(s) couverts dans les données brutes** :
  Les données brutes sont regroupées en trois ensembles selon les départements :
  1. **[Allier, Aude, Gironde]** ([Lien](https://www.ccomptes.fr/sites/default/files/2022-01/RSA-donnees-brutes-csv-Allier-Aude-Gironde.zip)) — [Resource ID : e404ced4-a689-42f6-bfd5-f95b6bbbe4b9].
  2. **[Ille-et-Vilaine, Pas-de-Calais, Bas-Rhin]** ([Lien](https://www.ccomptes.fr/sites/default/files/2022-01/RSA-donnees-brutes-csv-Ille-et-Villaine-Pas-de-Calais-Bas-Rhin.zip)) — [Resource ID : 3cced813-17f0-408b-9399-7a9120274994].
  3. **[Seine-Saint-Denis, Martinique, La Réunion]** ([Lien](https://www.ccomptes.fr/sites/default/files/2022-01/RSA-donnees-brutes-csv-Seine-Saint-Denis-La-Reunion-Martinique.zip)) — [Resource ID : 6ab7d7ed-e291-49c3-b115-5122bef564f8].

Les autres ressources sont des données enrichies (graphiques) et ne concernent pas les données brutes.

Si vous souhaitez consulter les données d'un département spécifique, je peux vous aider à les interroger.

Sources citées :
- Le revenu de solidarité active (RSA) — https://www.data.gouv.fr/datasets/le-revenu-de-solidarite-active-rsa
- Données brutes : Allier, Aude et Gironde — https://www.ccomptes.fr/sites/default/files/2022-01/RSA-donnees-brutes-csv-Allier-Aude-Gironde.zip
- Données brutes : Ille-et-Vilaine, Pas-de-Calais et Bas-Rhin — https://www.ccomptes.fr/sites/default/files/2022-01/RSA-donnees-brutes-csv-Ille-et-Villaine-Pas-de-Calais-Bas-Rhin.zip
- Données brutes : Seine-Saint-Denis, Martinique et La Réunion — https://www.ccomptes.fr/sites/default/files/2022-01/RSA-donnees-brutes-csv-Seine-Saint-Denis-La-Reunion-Martinique.zip
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
Les résultats de la recherche ne correspondent pas exactement à la période demandée (janvier, février, mars 2020). Cependant, voici les ressources disponibles dans le jeu de données :

- **Titre** : Ville de Caen - Cartes nationales d'identité, passeports
- **Producteur** : Ville de Caen
- **Lien** : [Détails du jeu de données](https://www.data.gouv.fr/datasets/ville-de-caen-cartes-nationales-didentite-passeports)

### Ressources disponibles :
1. **Fichier CSV** : `ville-cartesdidentite-passeports-20210101.csv`
   - Ce fichier semble correspondre à une mise à jour récente (janvier 2021) et ne couvre pas les données de 2020.

2. **Fichier Excel** : `ville-caen-opendata-sft-citoyennete-identites.xlsx`
   - Ce fichier est une documentation et ne contient probablement pas les données mensuelles détaillées pour 2020.

---

### Piste alternative :
D'après l'**Index local** ([1]), il semble que les données sur les cartes nationales d'identité délivrées par la Ville de Caen soient disponibles dans des rapports annuels ou mensuels, mais souvent sous forme de fichiers plus anciens ou de synthèses globales.

Pour obtenir les données exactes de **janvier, février et mars 2020**, je vous recommande de :
- Consulter directement les archives internes de la Ville de Caen (service des identités).
- Vérifier si des rapports spécifiques ou des fichiers historiques sont disponibles sur leur site officiel ou sur des plateformes comme [Open Data Caen](https://opendata.caen.fr/) (si elles existent).

Si vous souhaitez explorer d'autres jeux de données similaires sur data.gouv.fr, je peux affiner la recherche en fonction d'autres mots-clés pertinents.

Sources citées :
- Ville de Caen - Cartes nationales d'identité, Passeports — https://www.data.gouv.fr/datasets/ville-de-caen-cartes-nationales-didentite-passeports
```

### Contrôles automatiques

```text
{
  "appariement": [
    0,
    2,
    null
  ],
  "appels_attendus": 3,
  "appels_valides": 2,
  "litige": false,
  "methode": "valeurs",
  "reponse_exacte": false,
  "valeurs_manquantes": [
    "134",
    "137",
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
Le jeu de données qui correspond à vos besoins est :

- **Titre** : *Effectifs de la fonction publique par département depuis 2010*
- **Producteur** : Direction Générale de l'Administration et de la Fonction Publique
- **Date de dernière mise à jour** : [À vérifier en ligne, mais le jeu de données semble récent et couvre les années 2010 à aujourd'hui]
- **Lien** : [https://www.data.gouv.fr/datasets/effectifs-de-la-fonction-publique-par-departement-depuis-2010](https://www.data.gouv.fr/datasets/effectifs-de-la-fonction-publique-par-departement-depuis-2010)
- **Licence** : [À vérifier en ligne, mais généralement ouverte sur data.gouv.fr, souvent sous licence **OuvreData** ou similaire.]

Je vais vérifier les détails exacts de la licence et de la dernière mise à jour pour vous. Je vais aussi consulter les ressources disponibles dans ce jeu de données.Il semble que les données aient été mises à jour le **21 juin 2019**, mais je vais vérifier si des mises à jour récentes ont eu lieu depuis cette date. Je vais aussi consulter les ressources disponibles pour confirmer la structure des données.Il semble que les ressources ne soient pas directement listées dans cet outil pour ce jeu de données. Je vais vérifier la dernière mise à jour et les informations disponibles sur le site officiel pour confirmer si des données récentes sont disponibles.

D'après l'Index local [1], ce jeu de données semble être un ensemble de séries temporelles couvrant les années 2010 à 2019. Il est possible que les données aient été mises à jour plus récemment via une autre méthode ou que les ressources soient disponibles sous une autre forme.

Je vais vérifier si des données plus récentes existent en cherchant explicitement les dernières publications sur le site officiel ou en proposant une autre approche.Il semble que les données les plus récentes disponibles sur data.gouv.fr pour les effectifs de la fonction publique par département depuis 2010 soient celles publiées en **2019** ([lien](https://www.data.gouv.fr/datasets/effectifs-de-la-fonction-publique-par-departement-depuis-2010)).

### Propositions pour obtenir des données plus récentes :
1. **Vérifier les sites officiels des ministères** :
   - La Direction Générale de l'Administration et de la Fonction Publique (DGAFP) ou le ministère de la Fonction Publique pourraient publier des données plus récentes sur leurs propres sites.
   - Consultez [https://www.fonction-publique.gouv.fr/](https://www.fonction-publique.gouv.fr/) pour voir si des rapports ou tableaux de bord sont disponibles.

2. **Demander aux services concernés** :
   - Contactez directement la DGAFP ou les services compétents pour obtenir des données actualisées.

3. **Autres sources officielles** :
   - Le site de l'**INSEE** ([https://www.insee.fr/](https://www.insee.fr/)) ou celui de la **Caisse des Dépôts** pourraient avoir des données complémentaires ou des séries temporelles complètes.

Si vous souhaitez explorer d'autres pistes, je peux vous aider à chercher des jeux de données similaires sur d'autres plateformes ou sites officiels. Souhaitez-vous que je vérifie une autre source ?

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
D'après l'**Index local des données publiques** ([1]), voici un jeu de données qui correspond à votre demande :

- **Titre** : *Nombre d'apprentis, taux d'insertion et taux de rupture par spécialité*
- **Producteur** : Dares (Direction de l'animation de la recherche, des études et des statistiques)
- **Date de dernière mise à jour** : 2023-06-01 (ou une date similaire récente, vérifiez en ligne pour confirmation).
- **Lien** : [data.gouv.fr - Dares : Nombre d'apprentis, taux d'insertion et taux de rupture](https://www.data.gouv.fr/fr/datasets/dares-nombre-dapprentis-taux-dinsertion-et-taux-de-rupture-par-specialite/) (à consulter directement sur le site).

---
### **Format des données**
Sur ce jeu de données, les données sont généralement disponibles sous forme de **fichiers CSV ou Excel** pour chaque année scolaire. Vous pouvez vérifier les ressources associées dans la page du jeu de données pour identifier les fichiers correspondants.

---
### **Prochaines étapes**
1. **Consultez la page du jeu de données** sur data.gouv.fr pour identifier le fichier exact correspondant à l'année scolaire souhaitée.
2. Si vous souhaitez interroger les données directement, je peux vous aider à extraire les informations via l'API Tabular si le fichier est en CSV/Excel.

Souhaitez-vous que je vérifie les ressources disponibles pour une année précise ?

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "appariement": [
    null,
    null
  ],
  "appels_attendus": 2,
  "appels_valides": 0,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": false
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
D'après l'**Index local des jeux de données publics** sur data.gouv.fr, je n'ai pas trouvé de jeu de données spécifique intitulé *"médecins accrédités par la Haute Autorité de Santé (HAS)"* directement accessible.

Cependant, voici une piste alternative mentionnée dans les résultats de l'Index local :
- **[Haute Autorité de Santé (HAS) - Accréditation des établissements de santé]** ([lien vers la page de la HAS](https://www.has-sante.fr/)) :
  Bien que ce ne soit pas directement un jeu de données sur data.gouv.fr, la HAS publie des informations sur ses accréditations sur son site officiel. Ces données peuvent être consultées directement auprès de leur site ou en contactant leur service.

Si vous souhaitez explorer des jeux de données liés à la santé ou aux établissements médicaux, je peux vous aider à chercher des données plus générales sur les établissements de santé ou les pratiques médicales sur data.gouv.fr. Souhaitez-vous que je recherche des jeux de données sur ce thème ?

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "appariement": [
    null
  ],
  "appels_attendus": 1,
  "appels_valides": 0,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": false
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
Le jeu de données correspondant à l'extraction non géolocalisée du **Fichier des Établissements Sanitaires et Sociaux (FINESS)** est :

- **Titre** : *FINESS Extraction du Fichier des établissements*
- **Producteur** : Ministère des Solidarités et de la Santé
- **Date de dernière mise à jour** : [à vérifier en ligne]
- **Lien** : [https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements](https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements)

Le fichier correspondant à l'extraction **non géolocalisée** du FINESS est :

- **Titre du fichier** : *Extraction Finess des Etablissements au 04/05/2026*
- **Format** : CSV
- **Taille** : **34,1 Mo**
- **URL de téléchargement** : [https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv](https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv)

### Interrogation via l'API tabulaire
Ce fichier est **interrogeable via l'API tabulaire de data.gouv.fr**. Je peux vous aider à interroger ses données en ligne sans le télécharger. Souhaitez-vous que je procède à une première consultation pour explorer sa structure ?

Sources citées :
- FINESS Extraction du Fichier des établissements — https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements
- Extraction Finess des Etablissements au 04/05/2026. — https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv
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
**Résumé pour un étudiant (200 mots max) :**

Vous pouvez bénéficier d’une aide au logement (APL, ALF ou ALS) sous conditions, pour payer votre loyer. **Trois types d’aides existent** :
- **APL** (Aide personnalisée au logement),
- **ALF** (Allocation de logement familiale),
- **ALS** (Allocation de logement sociale).

**Conditions générales** :
- Être **français ou étranger en situation régulière** (titre de séjour valide).
- Louer un **logement décent** sans lien de parenté avec le propriétaire.
- Avoir des **ressources modestes**.

**Pour les étudiants étrangers hors UE/EEE/Suisse** (depuis le 1ᵉʳ juillet 2026) :
- **Seulement si** vous percevez une **bourse du CROUS** ou une bourse régionale alignée, **travaillez**, ou êtes en **contrat d’apprentissage/professionnalisation**.

**Démarche** :
- **En ligne**, dès votre installation.
- En cas de **colocation**, chaque colocataire doit faire sa demande **individuellement** (le loyer est partagé dans le calcul).
- **Paiement** : généralement **2 mois après la demande** (ex. : demande en février → 1ᵉʳ paiement en avril).

**À noter** :
- Si vos **parents perçoivent des allocations familiales**, vous devez choisir entre l’aide au logement ou rester à leur charge (risque de suppression ou réduction de leurs allocations).
- Ces aides sont **cumulables** avec d’autres dispositifs comme **Visale**, **Loca-Pass** ou **Mobili-Jeune**, sous réserve des critères de chacun.

Pour plus d’informations, contactez le **numéro dédié aux aides étudiantes**.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "moyenne",
  "mots": 197,
  "plafond_mots": 200,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé élargit la restriction à tous les « étudiants étrangers hors UE/EEE/Suisse » sans préciser qu'elle ne vise que les titulaires d'un titre de séjour délivré pour les études. Il réduit aussi « bourse sur critères sociaux » à « bourse du CROUS », deux déformations du document.
- `presence_elements` :
  - P1 : 1 — « Vous pouvez bénéficier d'une aide au logement (APL, ALF ou ALS) sous conditions ».
  - P2 : 1 — Les quatre conditions sont listées : nationalité ou titre de séjour valide, logement décent, absence de lien de parenté, ressources modestes.
  - P3 : 1 — La restriction depuis le 1er juillet 2026 et ses trois cas sont mentionnés, bien que la condition du titre pour études soit omise.
  - P4 : 1 — « vous devez choisir entre l'aide au logement ou rester à leur charge (risque de suppression ou réduction de leurs allocations) ».
  - P5 : 1 — « En ligne, dès votre installation » ; en colocation, une demande individuelle par colocataire, avec partage du loyer dans le calcul.
  - P6 : 1 — « généralement 2 mois après la demande ».
  - P7 : 1 — « cumulables avec d'autres dispositifs comme Visale, Loca-Pass ou Mobili-Jeune ».
- Inventions : Restriction présentée comme s'appliquant à tous les étudiants étrangers hors UE/EEE/Suisse, sans la condition du titre de séjour délivré pour les études; « bourse du CROUS » au lieu de « bourse sur critères sociaux »; « numéro dédié aux aides étudiantes » au lieu de « numéro dédié aux aides au logement étudiant »
- Confiance : moyenne

**Juge second** : juge

- `fidelite` : 1 — Aucune information absente du document ni déformée ; tous les éléments sont fidèlement restitués.
- `presence_elements` :
  - P1 : 1 — Les trois types d'aides (APL, ALF, ALS) et leur caractère conditionnel sont mentionnés.
  - P2 : 1 — Les quatre conditions générales (nationalité/titre de séjour, logement décent, absence de lien de parenté, faibles ressources) sont citées.
  - P3 : 1 — Les restrictions pour les étudiants hors UE/EEE/Suisse depuis juillet 2026 (bourse, travail, apprentissage) sont correctement rapportées.
  - P4 : 1 — L'impact sur les allocations familiales des parents et le choix à faire sont expliqués.
  - P5 : 1 — La demande en ligne dès l'installation et les modalités pour la colocation sont précisées.
  - P6 : 1 — Le délai de 2 mois pour le premier paiement est indiqué.
  - P7 : 1 — Le cumul avec Visale, Loca-Pass et Mobili-Jeune est mentionné.
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
**Résumé de la demande d’APA à domicile (200 mots max) – Pour une personne âgée**

L’**Allocation Personnalisée d’Autonomie (APA)** permet de financer, en tout ou partie, les dépenses liées au maintien à domicile ou à un établissement médico-social (comme un Ehpad), sous conditions strictes.

**Conditions d’éligibilité** :
- Être âgé d’au moins **60 ans**.
- Présenter une **perte d’autonomie** (GIR 1 à 4, selon la grille AGIR).
- Résider **stablement en France** (à son domicile, chez un proche, en résidence autonomie ou chez un accueillant familial).
- Ne pas percevoir certaines aides (comme l’ASPA, les aides de retraite ou la PCH).

**Démarche** :
- **Demande possible en ligne ou par formulaire** (Cerfa n°16301) selon le département.
- **Pièces à fournir** : pièce d’identité, dernier avis d’imposition, RIB, parfois avis de taxe foncière.
- **Délai d’instruction** : 10 jours pour l’accusé de réception. En cas d’urgence médicale ou sociale, une **APA forfaitaire de 1 040,16 €** peut être attribuée provisoirement.

L’APA est versée par le **département** et peut être suspendue en cas de changement de situation (ex. : retour à une autonomie accrue). En cas de trop-perçu, une récupération sur succession est possible.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "moyenne",
  "mots": 178,
  "plafond_mots": 200,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé contient des affirmations absentes du document ou déformées : « peut être suspendue en cas de changement de situation (ex. : retour à une autonomie accrue) », « En cas de trop-perçu, une récupération sur succession est possible » et « l'ASPA » au lieu de l'allocation simple d'aide sociale. Il présente aussi le délai d'accusé de réception comme un « délai d'instruction ».
- `presence_elements` :
  - P1 : 1 — Le résumé indique le financement « en tout ou partie » du maintien à domicile ou d'un établissement (Ehpad) et précise que l'Apa est « versée par le département ».
  - P2 : 1 — Les trois conditions y figurent : au moins 60 ans, GIR 1 à 4 et résidence stable en France.
  - P3 : 1 — La non-cumulabilité est mentionnée avec « les aides de retraite ou la PCH ». La majoration pour tierce personne et le choix avec la PCRTP sont toutefois omis.
  - P4 : 1 — Le résumé cite la demande en ligne ou par Cerfa n°16301 selon le département, ainsi que la pièce d'identité, l'avis d'imposition, le RIB et parfois l'avis de taxe foncière.
  - P5 : 1 — Le résumé mentionne l'accusé de réception sous 10 jours et l'APA forfaitaire provisoire de 1 040,16 € en cas d'urgence.
- Inventions : L'APA peut être suspendue en cas de changement de situation (ex. : retour à une autonomie accrue); En cas de trop-perçu, une récupération sur succession est possible; Désignation « ASPA » pour l'allocation simple d'aide sociale pour les personnes âgées; Qualification du délai de 10 jours comme « délai d'instruction »
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
**Résumé détaillé pour les élus de la commission des finances**

La commune ou l’EPCI peut instaurer une **taxe de séjour**, soit **au réel** (payée directement par les résidents occasionnels), soit **au forfait** (perçue par les hébergements marchands sur leurs clients). Cette décision doit être adoptée **avant le 1er juillet** pour une application effective au **1er janvier de l’année suivante**, en fixant les critères (période de perception, tarifs selon le classement des hébergements).

### **Hébergements concernés**
Les établissements éligibles incluent :
- Chambres d’hôtes,
- Hébergements de plein air (camping, caravanage, aires de camping-cars),
- Hôtels de tourisme,
- Meublés de tourisme,
- Palaces,
- Ports de plaisance,
- Résidences de tourisme,
- Villages de vacances.

### **Critères et modalités de la taxe**
La délibération détermine si la taxe est **au réel** (calculée par nuitées) ou **au forfait** (basée sur la capacité d’accueil, avec un abattement entre 10 % et 80 % selon la durée d’ouverture). Aucune exemption n’est autorisée pour certaines catégories d’hébergements.

#### **Taxe au réel**
- **Redevable** : Personnes non domiciliées dans la commune.
- **Exonérations** : Moins de 18 ans, travailleurs saisonniers, bénéficiaires d’un relogement temporaire, occupants de locaux dont le loyer est inférieur à un seuil fixé par le conseil municipal.

#### **Taxe au forfait**
- **Redevable** : Logeurs, hôteliers ou propriétaires hébergeant à titre onéreux.
- **Calcul** : Base sur le nombre de personnes accueillies (avec abattement), versée avant le départ des clients.
- **Exonérations** : Aucune mention spécifique dans le texte, mais les hébergements en résidence principale (meublés de tourisme) peuvent être concernés sous conditions.

### **Tarifs et obligations**
Les tarifs doivent être fixés entre un **plancher et un plafond** (basés sur le classement officiel des hébergements) et affichés en mairie ainsi que chez les prestataires. Une **taxe additionnelle départementale** (10 % en général, 200 % en Île-de-France) peut s’ajouter, reversée au département.

### **Déclaration et paiement**
- **Taxe au réel** : Les logeurs doivent verser le montant collecté au comptable local selon les dates fixées par le conseil municipal.
- **Taxe au forfait** : Déclaration obligatoire **1 mois avant la saison touristique**, précisant la nature de l’hébergement, la période d’ouverture et la capacité d’accueil. Le paiement doit être effectué selon les mêmes modalités que pour la taxe au réel.

### **Sanctions en cas de non-respect**
En cas d’absence de déclaration ou de retard de paiement, le maire ou le président de l’EPCI peut engager une **taxation d’office** après mise en demeure. Un **intérêt de retard de 0,20 % par mois** est appliqué en cas de non-régularisation.

*Note* : La déclaration de location (obligatoire pour les particuliers hébergeant leur résidence principale ou non) reste distincte de celle de la taxe de séjour.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 412,
  "plafond_mots": 400,
  "respect_longueur": false
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé déforme plusieurs points du document. Il calcule la taxe au forfait sur une « Base sur le nombre de personnes accueillies », alors que le texte la dit indépendante du nombre réel de personnes et assise sur la capacité d'accueil. Il invente une exonération liée à la résidence principale pour les meublés de tourisme. Il présente les 200 % d'Île-de-France comme une taxe départementale. Il limite l'intérêt de retard aux cas de « non-régularisation » au lieu de tout retard. Enfin, il contredit l'exception résidence principale de la déclaration de location.
- `presence_elements` :
  - P1 : 1 — Le résumé mentionne l'institution par la commune ou l'EPCI, les deux modes (réel et forfait), le délai du 1er juillet pour le 1er janvier suivant, la période de perception et les tarifs.
  - P2 : 1 — La liste des hébergements taxés est reprise, avec l'interdiction d'exempter une catégorie.
  - P3 : 0 — Redevables, nuitées et la plupart des exonérations figurent, mais la mention distincte sur la facture et l'exclusion de la base de TVA sont absentes.
  - P4 : 0 — La capacité d'accueil et l'abattement de 10 % à 80 % sont cités, mais l'inclusion dans la base de TVA manque et le calcul est déformé en « nombre de personnes accueillies ».
  - P5 : 1 — Le plancher et le plafond selon le classement, ainsi que l'affichage en mairie et chez les prestataires, figurent. La perception avant le départ est mentionnée, mais rattachée au seul forfait.
  - P6 : 1 — La taxe additionnelle de 10 % et les 200 % en Île-de-France sont mentionnés.
  - P7 : 1 — Le versement au comptable local aux dates fixées et la déclaration au plus tard 1 mois avant la saison pour le forfait sont présents.
  - P8 : 1 — La taxation d'office après mise en demeure et l'intérêt de 0,20 % par mois sont présents, mais le délai de 30 jours de l'avis motivé est omis.
- Inventions : Calcul de la taxe au forfait sur « le nombre de personnes accueillies » (le document dit indépendante du nombre réel de personnes); Exonération possible de la taxe au forfait pour les meublés de tourisme en résidence principale; La taxe de 200 % en Île-de-France présentée comme une taxe additionnelle départementale; Intérêt de retard appliqué « en cas de non-régularisation » (le document dit : tout retard); Déclaration de location obligatoire pour les particuliers « hébergeant leur résidence principale ou non » (le document exclut le meublé de tourisme en résidence principale)
- Confiance : haute
