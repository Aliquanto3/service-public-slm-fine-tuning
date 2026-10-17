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

## CR-008 (CR, facile)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de ce point hebdomadaire de service : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 417,
  "notes": "Point hebdo propreté urbaine – lundi 28/09/26 – 7h30-8h40 – CTM (centre technique municipal), Ville de Saint-Ambrel-les-Forges\nPrés. : R. Duquesne (resp. service propreté, anime), P. Ribeiro (cheffe d'équipe secteur nord), G. Tessier (chef d'équipe secteur sud), K. Bouaziz (agent de maîtrise, atelier véhicules)\n+ Mme Loiseau (adjointe au maire cadre de vie) passée de 7h45 à 8h05 seulement\nAbs. : D. Kowalski (chef d'équipe centre-ville) – en formation CACES toute la semaine, Ribeiro couvre le centre en attendant\n\n1) Dépôts sauvages rue du Moulin-Brûlé\n- 3e dépôt en 15 jours (gravats + électroménager). Enlevé jeudi par l'équipe nord, 2 rotations de camion.\n- Loiseau veut « une caméra là-bas ». Duquesne : la vidéoprotection c'est la police municipale + délib. du conseil, pas nous. Pas décidé.\n- Duquesne transmet les photos et le n° d'un courrier retrouvé dans les gravats à la police municipale pour identifier l'auteur, aujourd'hui.\n- Loiseau propose un article dans le bulletin municipal sur les dépôts sauvages et la déchèterie. Tout le monde d'accord sur l'idée mais personne ne s'en charge, Loiseau partie avant qu'on en reparle.\n\n2) Balayeuse n°2 en panne\n- Bouaziz : pompe hydraulique HS, pièce commandée, délai fournisseur 3 sem.\n- DÉCISION (Duquesne) : location d'une balayeuse de remplacement pour 3 semaines. Devis annoncé 2 400 € HT, Bouaziz relit : 2 040 € HT (il avait mal lu). Sur budget fonctionnement propreté.\n- Bouaziz réserve la balayeuse de location, livraison au plus tard le jeudi 1er octobre.\n\n3) Plan feuilles mortes\n- DÉCISION : démarrage du ramassage des feuilles le lundi 12 octobre 2026. 2 agents en renfort pris sur les espaces verts (accord du chef des espaces verts déjà obtenu).\n- Tessier fait le planning des circuits feuilles (priorité abords écoles + pistes cyclables), à présenter au point hebdo du lundi 5 octobre.\n- Ribeiro voudrait tester le broyage des feuilles pour paillage. Pas le temps cette année, on verra en 2027. Pas décidé.\n\n4) Cimetière / Toussaint\n- DÉCISION : nettoyage renforcé des allées et abords du cimetière la semaine du 26 octobre, avant le 1er novembre. Équipe sud.\n- Tessier coordonne avec le conservateur du cimetière.\n\n5) Tags école Jean-Moulin\n- Tags sur le mur côté cour, signalés vendredi par la directrice.\n- Tessier fait intervenir l'équipe sud avec l'hydrogommeuse, avant le vendredi 2 octobre.\n\n6) Divers / sécurité\n- Ribeiro : 2 agents sans gilets haute visibilité neufs (taille). Duquesne passe la commande d'EPI cette semaine.\n- Tessier demande si on peut passer aux horaires d'hiver dès octobre cette année (prise de poste 7h au lieu de 6h) au lieu du 1er décembre. Duquesne : il faut l'avis du CST, pas pour cette année. Rien changé.\n- Prochain point hebdo : lundi 5 octobre, 7h30."
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "R. Duquesne (responsable du service propreté, anime)",
    "P. Ribeiro (cheffe d'équipe secteur nord)",
    "G. Tessier (chef d'équipe secteur sud)",
    "K. Bouaziz (agent de maîtrise, atelier véhicules)",
    "Mme Loiseau (adjointe au maire chargée du cadre de vie, présente de 7 h 45 à 8 h 05 seulement)",
    "Absent : D. Kowalski (chef d'équipe centre-ville, en formation CACES)"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Location d'une balayeuse de remplacement pendant 3 semaines, pour 2 040 € HT, sur le budget de fonctionnement propreté"
    },
    {
      "ref": "D2",
      "texte": "Démarrage du ramassage des feuilles mortes le lundi 12 octobre 2026, avec 2 agents en renfort pris sur les espaces verts"
    },
    {
      "ref": "D3",
      "texte": "Nettoyage renforcé des allées et abords du cimetière la semaine du 26 octobre 2026, avant le 1er novembre, par l'équipe sud"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Transmettre à la police municipale les photos et le numéro du courrier retrouvé dans les gravats pour identifier l'auteur du dépôt",
      "responsable": "R. Duquesne",
      "echeance": "le jour même (lundi 28 septembre 2026)"
    },
    {
      "ref": "A2",
      "action": "Réserver la balayeuse de location",
      "responsable": "K. Bouaziz",
      "echeance": "livraison au plus tard le jeudi 1er octobre 2026"
    },
    {
      "ref": "A3",
      "action": "Établir le planning des circuits de ramassage des feuilles (priorité aux abords des écoles et aux pistes cyclables)",
      "responsable": "G. Tessier",
      "echeance": "point hebdo du lundi 5 octobre 2026"
    },
    {
      "ref": "A4",
      "action": "Coordonner le nettoyage du cimetière avec le conservateur",
      "responsable": "G. Tessier",
      "echeance": "non fixée"
    },
    {
      "ref": "A5",
      "action": "Faire effacer les tags de l'école Jean-Moulin à l'hydrogommeuse par l'équipe sud",
      "responsable": "G. Tessier",
      "echeance": "avant le vendredi 2 octobre 2026"
    },
    {
      "ref": "A6",
      "action": "Commander les gilets haute visibilité (EPI) manquants",
      "responsable": "R. Duquesne",
      "echeance": "cette semaine (semaine du 28 septembre 2026)"
    }
  ],
  "pieges": [
    "Caméra de vidéoprotection rue du Moulin-Brûlé : demandée par Mme Loiseau, NON décidée (relève de la police municipale et du conseil)",
    "Article dans le bulletin municipal sur les dépôts sauvages : idée approuvée mais aucun responsable désigné",
    "Coût de la location : 2 040 € HT et non 2 400 € HT (erreur de lecture corrigée)",
    "Broyage des feuilles pour paillage : NON décidé, renvoyé à 2027",
    "Passage anticipé aux horaires d'hiver dès octobre (prise de poste à 7 h au lieu de 6 h) : demandé, rien changé (avis du CST nécessaire)",
    "Mme Loiseau n'a assisté qu'à une vingtaine de minutes (7 h 45-8 h 05)",
    "D. Kowalski absent ; P. Ribeiro couvre le centre-ville"
  ]
}
```

### Sortie (statut ok)

```text
**Compte rendu – Point hebdomadaire du service propreté urbaine**
*Lundi 28 septembre 2026, 7h30 – Centre technique municipal (CTM), Ville de Saint-Ambrel-les-Forges*

**Participants présents :**
- R. Duquesne (responsable service propreté, animateur)
- P. Ribeiro (cheffe d’équipe secteur nord)
- G. Tessier (chef d’équipe secteur sud)
- K. Bouaziz (agent de maîtrise, atelier véhicules)
- Mme Loiseau (adjointe au maire, cadre de vie)

**Participants absents :**
- D. Kowalski (chef d’équipe centre-ville) – en formation CACES

---

### **Points abordés**

1. **Dépôts sauvages rue du Moulin-Brûlé**
   - Trois dépôts observés en quinze jours (gravats et électroménager), éliminés jeudi par l’équipe nord (deux rotations de camion).
   - Demande de Mme Loiseau pour une caméra de surveillance : Duquesne précise que la vidéoprotection relève de la police municipale et nécessite une délibération du conseil municipal.
   - Transmission des photos et du numéro d’un courrier retrouvé dans les gravats à la police municipale pour identification.
   - Projet d’article dans le bulletin municipal sur les dépôts sauvages et la déchèterie : accord unanime, mais action reportée en raison de l’absence de Mme Loiseau.

2. **Panne de la balayeuse n°2**
   - Problème de pompe hydraulique, pièce en cours de commande avec un délai de trois semaines.
   - **Décision** : Location d’une balayeuse de remplacement pour trois semaines, coût ajusté à 2 040 € HT (contre 2 400 € initialement).
   - **Action** : K. Bouaziz réserve la balayeuse de location, livraison prévue au plus tard le jeudi 1er octobre.

3. **Ramassage des feuilles mortes**
   - **Décision** : Démarrage prévu le lundi 12 octobre 2026.
   - **Action** : G. Tessier élabore le planning des circuits (priorité abords écoles et pistes cyclables) à présenter au prochain point hebdo (lundi 5 octobre).
   - Test du broyage des feuilles pour paillage envisagé en 2027, sans décision définitive.

4. **Nettoyage renforcé du cimetière pour la Toussaint**
   - **Décision** : Nettoyage des allées et abords du cimetière la semaine du 26 octobre, avant le 1er novembre.
   - **Action** : G. Tessier coordonne avec le conservateur du cimetière.

5. **Tags sur l’école Jean-Moulin**
   - Signalés vendredi par la directrice, intervention prévue par l’équipe sud avec l’hydrogommeuse avant le vendredi 2 octobre.

6. **Sécurité et équipements**
   - **Divers** :
     - P. Ribeiro signale deux agents sans gilets haute visibilité neufs (taille). R. Duquesne passe la commande d’EPI cette semaine.
     - Demande de G. Tessier pour une adaptation des horaires d’hiver dès octobre (prise de poste à 7h au lieu de 6h) : R. Duquesne rappelle qu’une décision dépend de l’avis du Comité social et technique (CST), non encore validé pour cette année.

---
**Prochaine réunion** : Lundi 5 octobre 2026, 7h30 – CTM.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — La location de la balayeuse pendant trois semaines à 2 040 € HT figure dans le compte rendu ; l'imputation sur le budget de fonctionnement propreté est omise.
  - D2 : 0.5 — Le démarrage du ramassage le lundi 12 octobre 2026 figure, mais les 2 agents en renfort pris sur les espaces verts sont omis.
  - D3 : 0.5 — Le nettoyage du cimetière la semaine du 26 octobre, avant le 1er novembre, figure, mais l'équipe sud, chargée de l'exécution, n'est pas mentionnée.
  - A1 : 0.5 — La formulation passive « Transmission des photos… à la police municipale » ne nomme ni le responsable (Duquesne) ni l'échéance (aujourd'hui).
  - A2 : 1 — « K. Bouaziz réserve la balayeuse de location, livraison prévue au plus tard le jeudi 1er octobre » : l'action, le responsable et l'échéance sont présents.
  - A3 : 1 — G. Tessier élabore le planning des circuits, à présenter au point hebdo du lundi 5 octobre : l'action, le responsable et l'échéance sont présents.
  - A4 : 1 — « G. Tessier coordonne avec le conservateur du cimetière » : présente avec son responsable ; l'échéance n'est pas fixée dans les notes.
  - A5 : 0.5 — « intervention prévue par l'équipe sud… avant le vendredi 2 octobre » : l'échéance est présente, mais G. Tessier n'est pas nommé comme responsable.
  - A6 : 1 — « R. Duquesne passe la commande d'EPI cette semaine » : l'action, le responsable et l'échéance sont présents.
- `absence_invention` : 1 — Aucun élément des pièges n'est présenté comme décidé (caméra, broyage et horaires d'hiver restent non décidés, le coût de 2 040 € est correct) ; deux glissements restent toutefois mineurs : « action reportée en raison de l'absence de Mme Loiseau » et le lieu « CTM » ajouté pour la prochaine réunion.
- `structure` : 0 — Les sections Participants et Points abordés existent, mais il n'y a pas de sections distinctes Décisions et Actions ; les décisions et les actions sont intégrées dans les points abordés.
- Inventions : aucune
- Confiance : moyenne

## CR-015 (CR, moyen)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de cette séance de l'équipe pluridisciplinaire RSA : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 1565,
  "transcription": "Équipe pluridisciplinaire RSA – territoire d'action sociale du Haut-Orlan – jeudi 17 septembre 2026, 9h30 – Maison départementale des solidarités de Val-d'Orlan\nTranscription de l'enregistrement (usage interne du secrétariat, à détruire après validation des avis)\n\nMme Aubertin : Bon, il est 9h35, on va commencer. Je préside par délégation du président du conseil départemental, comme d'habitude. Autour de la table : M. Faure pour France Travail, Mme Nkomo, assistante sociale de la MDS, M. Gallet, représentant des allocataires, M. Le Goff pour l'Atelier du Pont, et Mme Jacquet qui assure le secrétariat. Mme Rambert, conseillère en insertion du département, est excusée, elle est en formation. Je rappelle à tout le monde, et surtout pour M. Gallet qui est nouveau : l'équipe pluridisciplinaire rend des avis. C'est le président du conseil départemental qui décide ensuite, au vu de nos avis. On a six situations ce matin.\n\nM. Gallet : Merci. Oui, c'est ma deuxième séance seulement, donc je vais peut-être poser des questions bêtes.\n\nMme Aubertin : Il n'y a pas de questions bêtes. Mme Jacquet, on y va.\n\nMme Jacquet : Premier dossier, Mme L. D., 41 ans, au RSA depuis 2023, actuellement en parcours social avec Mme Nkomo comme référente. La demande, c'est une réorientation vers le parcours professionnel.\n\nMme Nkomo : Oui. Alors Mme L. D. a eu de gros soucis de santé l'an dernier, c'est stabilisé, elle a le feu vert de son médecin. Le logement est réglé depuis juin. Elle m'a dit elle-même qu'elle voulait retravailler, dans l'aide à domicile, elle l'a déjà fait avant. Je pense qu'il est temps qu'elle soit suivie par France Travail.\n\nM. Faure : Pas d'objection de notre côté, c'est même un profil qui recrute en ce moment. Il faudra juste voir le permis, elle ne l'a pas, je crois ?\n\nMme Nkomo : Non, elle ne l'a pas. Mais il y a les lignes de bus sur Val-d'Orlan.\n\nM. Faure : D'accord. On regardera l'aide au permis plus tard, ce n'est pas l'objet aujourd'hui.\n\nMme Aubertin : Donc avis favorable à la réorientation de Mme L. D. vers le parcours professionnel, suivi par France Travail. Tout le monde est d'accord ? … Unanimité. M. Faure, vous transmettez ?\n\nM. Faure : Oui, je lui fais désigner un conseiller, et premier rendez-vous avant le vendredi 16 octobre.\n\nMme Jacquet : Deuxième dossier, M. K. A., 56 ans. C'est l'inverse : il est en parcours professionnel chez France Travail et M. Faure demande une réorientation vers le parcours social.\n\nM. Faure : Oui. M. K. A. est hébergé chez un ami depuis trois mois, il a perdu son logement, il a des problèmes de santé qu'il ne soigne pas. Honnêtement, lui proposer des offres d'emploi en ce moment, ça n'a pas de sens. Il vient aux rendez-vous, hein, il est assidu, ce n'est pas un problème de manquement. C'est qu'il faut d'abord régler le reste.\n\nM. Gallet : Je voudrais juste dire… ce genre de personne, souvent, quand on change de référent, elle décroche. Il faut que le relais se fasse vite.\n\nMme Nkomo : Je suis d'accord. Je m'engage à ce qu'un référent social de la MDS soit désigné sous un mois. Peut-être moi, ça dépend des charges de travail, je verrai avec ma cheffe.\n\nMme Aubertin : Très bien. Avis favorable à la réorientation de M. K. A. vers le parcours social, suivi par la MDS. Pas d'opposition ? … Unanimité.\n\nMme Jacquet : Troisième dossier, M. R. S., 29 ans, parcours professionnel. C'est un dossier de manquement. Il ne s'est pas présenté à trois rendez-vous…\n\nM. Faure : Deux. Deux rendez-vous, le 3 juin et le 1er juillet. Le troisième, il avait prévenu.\n\nMme Jacquet : Pardon, deux, oui, je corrige. Deux rendez-vous non honorés, et il ne fait pas les heures d'activité prévues à son contrat d'engagement depuis juin. Un courrier lui a été envoyé le 20 août pour qu'il présente ses observations, pas de réponse. Il n'est pas venu ce matin, il était convoqué.\n\nM. Faure : Pour être complet, on a essayé de l'appeler deux fois, numéro qui ne répond pas.\n\nMme Aubertin : La proposition du service, dans la fiche, c'était une suspension-remobilisation à 100 % pendant un mois.\n\nM. Gallet : Cent pour cent, c'est énorme. On ne sait même pas pourquoi il ne vient pas. Il a peut-être des problèmes qu'on ne connaît pas.\n\nM. Le Goff : Je le connais un peu, il est passé à l'Atelier au printemps, deux ou trois fois. Il a l'air un peu perdu, pas de mauvaise volonté particulière. Je serais plutôt pour quelque chose de plus léger, et qu'on essaie de le joindre autrement.\n\nMme Nkomo : Moi je suis d'accord avec M. Le Goff. Si on coupe tout, on le perd.\n\nM. Faure : Je comprends, mais il y a quand même deux rendez-vous et zéro heure d'activité depuis trois mois. Il faut un signal.\n\nMme Aubertin : Je propose qu'on retienne une suspension-remobilisation de 30 % pendant un mois, avec levée dès qu'il reprend contact. Ça fait un signal sans le mettre à la rue. M. Gallet ?\n\nM. Gallet : Je reste contre. Même 30 %. Je préfère qu'on le voie d'abord.\n\nMme Aubertin : C'est noté. Les autres ? … Donc avis : suspension-remobilisation de 30 % pendant un mois, levée dès la reprise de contact, avis à la majorité, M. Gallet défavorable. Et je voudrais qu'on tente quand même de le joindre avant que la décision lui soit notifiée.\n\nM. Faure : Je l'appelle demain, et s'il ne répond pas, je passe par sa sœur, il l'avait donnée comme contact.\n\nMme Aubertin : Vendredi 18 donc, très bien.\n\nM. Gallet : Et est-ce qu'on ne pourrait pas, en général, faire des courriers de convocation plus simples ? Celui que j'ai vu, je ne l'aurais pas compris moi-même.\n\nMme Aubertin : C'est une vraie question. On n'a pas le temps de la traiter ce matin. Il faudrait en parler au service RSA… [inaudible] … on verra.\n\nMme Jacquet : Quatrième dossier, Mme F. M., 34 ans, parcours social. Absences aux ateliers collectifs de juillet et août, signalées par l'Atelier du Pont.\n\nM. Le Goff : Oui, c'est nous qui avons signalé. Mais attendez, il y a du nouveau.\n\nMme Jacquet : Oui, on a reçu ce matin à 8h50 un justificatif : son fils a été hospitalisé à deux reprises cet été, il y a les bulletins d'hospitalisation.\n\nMme Nkomo : Je confirme, elle m'avait appelée en juillet, je n'avais pas fait le lien avec le signalement, c'est ma faute.\n\nMme Aubertin : Bon, alors là c'est clair. Avis de maintien du RSA, sans sanction. Tout le monde est d'accord ? … Unanimité.\n\nM. Le Goff : Et on la réinscrit aux ateliers d'octobre, si elle veut.\n\nMme Aubertin : Si elle le souhaite, oui.\n\nMme Jacquet : Cinquième dossier, M. J.-P. V., 47 ans, parcours professionnel. Il est là, il a demandé à être entendu.\n\nMme Aubertin : Faites-le entrer, s'il vous plaît.\n\n[M. J.-P. V. entre dans la salle à 10h40]\n\nMme Aubertin : Bonjour Monsieur. Vous savez pourquoi vous êtes convoqué : France Travail a signalé que vous n'aviez pas fait vos heures d'activité en août. Vous voulez nous expliquer ?\n\nM. J.-P. V. : Oui. En fait j'ai commencé une mission d'intérim le 10 août, dans un entrepôt à Saint-Brice-sur-Orlan, de nuit. Donc forcément je ne pouvais pas aller aux ateliers. J'ai prévenu par mail mais je crois que ça n'a pas été lu.\n\nM. Faure : Le mail, je ne l'ai pas eu, mais ça arrive, il y a eu des soucis de messagerie en août. Vous avez votre contrat de mission ?\n\nM. J.-P. V. : Oui, j'ai le contrat et les fiches de paie d'août. La mission va jusqu'à fin novembre.\n\nM. Gallet : Ben voilà, il travaille, on ne va pas le sanctionner.\n\nMme Aubertin : Merci Monsieur, vous pouvez sortir, on vous écrira.\n\n[M. J.-P. V. quitte la salle à 10h50]\n\nMme Aubertin : La fiche proposait une réduction. Vu ce qu'il nous dit, je propose un avis de maintien sans réduction.\n\nM. Faure : D'accord, mais je veux voir le contrat. Et il faut mettre à jour son contrat d'engagement, les heures de travail comptent dans les heures d'activité.\n\nMme Aubertin : Donc avis de maintien du RSA sans réduction pour M. J.-P. V. Unanimité ? … Oui. M. Faure, vous vérifiez le contrat de mission et vous mettez à jour le contrat d'engagement ?\n\nM. Faure : Avant le jeudi 15 octobre, oui.\n\nM. Le Goff : Excusez-moi, je dois partir, j'ai un atelier à 11h à l'Atelier du Pont. Le dernier dossier, je ne le connais pas de toute façon.\n\n[M. Le Goff quitte la séance à 10h55]\n\nMme Jacquet : Sixième et dernier dossier, Mme N. R. Elle a appelé hier après-midi : elle veut être entendue, mais elle a reçu sa convocation seulement lundi, elle travaille ce matin et elle n'a pas pu se libérer.\n\nMme Aubertin : Lundi ? Elle n'a pas eu le délai, alors. On ne peut pas examiner son dossier dans ces conditions. On reporte à la prochaine équipe pluridisciplinaire.\n\nMme Jacquet : C'est le jeudi 15 octobre.\n\nMme Aubertin : Le 15 octobre, oui. Vous la reconvoquez à temps cette fois-ci.\n\nMme Jacquet : Je lui envoie la convocation avant le mercredi 30 septembre, et je l'appelle aussi pour la prévenir.\n\nM. Gallet : Elle pourra venir accompagnée ?\n\nMme Aubertin : Oui, elle peut se faire accompagner par la personne de son choix, c'est indiqué dans le courrier.\n\nMme Aubertin : Bon. Pour récapituler les suites : Mme Jacquet, vous transmettez l'ensemble des avis au service RSA pour la décision du président, quand ?\n\nMme Jacquet : D'ici le vendredi 25 septembre.\n\nMme Aubertin : Parfait. Prochaine séance le jeudi 15 octobre, même heure. Merci à tous, on lève la séance. Il est 11h05."
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "Mme Aubertin (présidente de séance, par délégation du président du conseil départemental)",
    "M. Faure (France Travail)",
    "Mme Nkomo (assistante sociale, MDS)",
    "M. Gallet (représentant des allocataires du RSA)",
    "M. Le Goff (Atelier du Pont, parti à 10 h 55 avant le 6e dossier)",
    "Mme Jacquet (secrétariat de l'équipe pluridisciplinaire)",
    "Excusée : Mme Rambert (conseillère en insertion du département, en formation)",
    "M. J.-P. V. (allocataire, entendu pour son seul dossier, de 10 h 40 à 10 h 50)"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Avis favorable (unanimité) à la réorientation de Mme L. D. du parcours social vers le parcours professionnel, suivi par France Travail"
    },
    {
      "ref": "D2",
      "texte": "Avis favorable (unanimité) à la réorientation de M. K. A. du parcours professionnel vers le parcours social, suivi par la MDS"
    },
    {
      "ref": "D3",
      "texte": "Avis de suspension-remobilisation de 30 % pendant un mois pour M. R. S., levée dès la reprise de contact (avis à la majorité, M. Gallet défavorable)"
    },
    {
      "ref": "D4",
      "texte": "Avis de maintien du RSA sans sanction pour Mme F. M. (unanimité), au vu du justificatif d'hospitalisation de son fils"
    },
    {
      "ref": "D5",
      "texte": "Avis de maintien du RSA sans réduction pour M. J.-P. V. (unanimité), qui a repris une mission d'intérim"
    },
    {
      "ref": "D6",
      "texte": "Report de l'examen du dossier de Mme N. R. à l'équipe pluridisciplinaire du jeudi 15 octobre 2026 (convocation reçue trop tardivement)"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Faire désigner un conseiller France Travail pour Mme L. D. et fixer un premier rendez-vous",
      "responsable": "M. Faure",
      "echeance": "premier rendez-vous avant le vendredi 16 octobre 2026"
    },
    {
      "ref": "A2",
      "action": "Faire désigner un référent social de la MDS pour M. K. A.",
      "responsable": "Mme Nkomo",
      "echeance": "sous un mois"
    },
    {
      "ref": "A3",
      "action": "Tenter de joindre M. R. S. (puis sa sœur) avant la notification de la décision",
      "responsable": "M. Faure",
      "echeance": "vendredi 18 septembre 2026"
    },
    {
      "ref": "A4",
      "action": "Réinscrire Mme F. M. aux ateliers d'octobre, si elle le souhaite",
      "responsable": "M. Le Goff (Atelier du Pont)",
      "echeance": "ateliers d'octobre 2026"
    },
    {
      "ref": "A5",
      "action": "Vérifier le contrat de mission de M. J.-P. V. et mettre à jour son contrat d'engagement",
      "responsable": "M. Faure",
      "echeance": "avant le jeudi 15 octobre 2026"
    },
    {
      "ref": "A6",
      "action": "Reconvoquer Mme N. R. (courrier et appel téléphonique) pour la séance du 15 octobre",
      "responsable": "Mme Jacquet",
      "echeance": "avant le mercredi 30 septembre 2026"
    },
    {
      "ref": "A7",
      "action": "Transmettre l'ensemble des avis au service RSA pour décision du président du conseil départemental",
      "responsable": "Mme Jacquet",
      "echeance": "d'ici le vendredi 25 septembre 2026"
    }
  ],
  "pieges": [
    "L'équipe pluridisciplinaire rend des avis : la décision appartient au président du conseil départemental, aucune sanction n'est décidée en séance",
    "M. R. S. : la suspension-remobilisation à 100 % de la fiche n'est PAS retenue (avis à 30 % pendant un mois)",
    "M. R. S. a manqué deux rendez-vous et non trois (correction en séance)",
    "M. J.-P. V. : la réduction proposée dans la fiche n'est PAS retenue",
    "Mme N. R. : aucun avis rendu, dossier reporté au 15 octobre",
    "Simplification des courriers de convocation : question soulevée par M. Gallet, sans responsable ni décision",
    "Aide au permis pour Mme L. D. : évoquée, NON décidée (« pas l'objet aujourd'hui »)",
    "Réinscription de Mme F. M. aux ateliers d'octobre : seulement si elle le souhaite, ne pas la présenter comme acquise",
    "M. Le Goff est parti à 10 h 55 ; Mme Rambert était excusée ; M. J.-P. V. n'a assisté qu'à l'examen de son dossier"
  ]
}
```

### Sortie (statut ok)

```text
**Compte rendu – Réunion d’équipe pluridisciplinaire RSA – Haut-Orlan**
*Jeudi 17 septembre 2026, 9h30 – Maison départementale des solidarités de Val-d’Orlan*

---
**Participants présents :**
- Mme Aubertin (présidente, déléguée du président du conseil départemental)
- M. Faure (France Travail)
- Mme Nkomo (assistante sociale, MDS)
- M. Gallet (représentant des allocataires)
- M. Le Goff (Atelier du Pont)
- Mme Jacquet (secrétariat)

---
**Points abordés :**

1. **Réorientation de Mme L. D. (41 ans, RSA depuis 2023)**
   - **Situation** : Stabilité médicale et logement, souhait d’une réorientation vers le parcours professionnel en aide à domicile.
   - **Décision** : Avis favorable à la réorientation vers France Travail.
   - **Actions** :
     - M. Faure désigne un conseiller et organise un premier rendez-vous avant le **vendredi 16 octobre**.

2. **Réorientation de M. K. A. (56 ans, parcours professionnel)**
   - **Situation** : Perte de logement et problèmes de santé non soignés, hébergement temporaire chez un ami depuis trois mois.
   - **Décision** : Avis favorable à la réorientation vers le parcours social, suivi par la MDS.
   - **Actions** :
     - Mme Nkomo s’engage à désigner un référent social sous **un mois** (à confirmer selon ses charges).

3. **Dossier de manquement de M. R. S. (29 ans, parcours professionnel)**
   - **Situation** : Deux rendez-vous non honorés et absence de participation aux heures d’activité depuis juin.
   - **Décision** : Avis à majorité pour une **suspension-remobilisation à 30 % pendant un mois**, levée dès la reprise de contact.
   - **Actions** :
     - M. Faure tente de joindre M. R. S. **avant le vendredi 18 octobre** (par appel et contact familial).
     - Proposition de simplifier les courriers de convocation (à traiter ultérieurement par le service RSA).

4. **Maintien du RSA pour Mme F. M. (34 ans, parcours social)**
   - **Situation** : Absences aux ateliers collectifs de juillet et août, justifiées par l’hospitalisation de son fils.
   - **Décision** : Avis de maintien sans sanction.
   - **Actions** :
     - Réinscription aux ateliers d’octobre si elle le souhaite.

5. **Maintien du RSA pour M. J.-P. V. (47 ans, parcours professionnel)**
   - **Situation** : Participation à une mission d’intérit en août (contrat valide jusqu’à fin novembre).
   - **Décision** : Avis de maintien sans réduction.
   - **Actions** :
     - M. Faure vérifie et met à jour son contrat d’engagement **avant le jeudi 15 octobre**.

6. **Report de Mme N. R.**
   - **Situation** : Convocation reçue tardivement (délai non respecté), travail ce matin.
   - **Décision** : Report à la prochaine réunion du **jeudi 15 octobre**.
   - **Actions** :
     - Mme Jacquet reconvoque Mme N. R. **avant le mercredi 30 septembre** et l’appelle pour prévenir.

---
**Décisions générales :**
- Transmission des avis au service RSA **d’ici le vendredi 25 septembre**.
- Prochaine réunion prévue le **jeudi 15 octobre** à la même heure.
- **Fin de séance à 11h05**.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « Avis favorable à la réorientation vers France Travail » pour Mme L. D. est présent ; l'unanimité n'est pas mentionnée.
  - D2 : 1 — « Avis favorable à la réorientation vers le parcours social, suivi par la MDS » est présent.
  - D3 : 1 — « Avis à majorité pour une suspension-remobilisation à 30 % pendant un mois, levée dès la reprise de contact » est présent ; le vote défavorable de M. Gallet est omis.
  - D4 : 1 — « Avis de maintien sans sanction », justifié par l'hospitalisation du fils, est présent.
  - D5 : 1 — « Avis de maintien sans réduction » pour M. J.-P. V. est présent.
  - D6 : 1 — Le « Report à la prochaine réunion du jeudi 15 octobre » est présent.
  - A1 : 1 — « M. Faure désigne un conseiller et organise un premier rendez-vous avant le vendredi 16 octobre » : action, responsable et échéance sont corrects.
  - A2 : 1 — « Mme Nkomo s'engage à désigner un référent social sous un mois » : responsable et échéance sont présents.
  - A3 : 0.5 — L'action est attribuée à M. Faure, mais l'échéance est fausse : « avant le vendredi 18 octobre » au lieu du vendredi 18 septembre.
  - A4 : 0.5 — « Réinscription aux ateliers d'octobre si elle le souhaite » est présente, sans le responsable (M. Le Goff).
  - A5 : 1 — « M. Faure vérifie et met à jour son contrat d'engagement avant le jeudi 15 octobre » : responsable et échéance sont corrects.
  - A6 : 1 — « Mme Jacquet reconvoque Mme N. R. avant le mercredi 30 septembre et l'appelle » est présent.
  - A7 : 0.5 — « Transmission des avis au service RSA d'ici le vendredi 25 septembre » est présente, sans le responsable (Mme Jacquet).
- `absence_invention` : 0 — La date « avant le vendredi 18 octobre » ne figure pas dans les notes (il s'agit du 18 septembre). La simplification des courriers est présentée comme une action « à traiter ultérieurement par le service RSA », alors qu'elle n'a fait l'objet d'aucune décision ni attribution.
- `structure` : 0 — Il n'y a pas de section « Actions » distincte : les actions sont dispersées dans les points abordés et seule une section « Décisions générales » existe.
- Inventions : Échéance « avant le vendredi 18 octobre » pour joindre M. R. S. (le 18 septembre dans les notes); Simplification des courriers de convocation présentée comme une action confiée au service RSA, alors qu'elle n'a été ni décidée ni attribuée
- Confiance : haute

## CR-016 (CR, difficile)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de cette réunion publique de concertation : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 4602,
  "transcription": "COMMUNE DE VALBRÉZAC – Réunion publique de concertation préalable – Projet « Cœur de bourg »\nJeudi 1er octobre 2026, 19h, salle des fêtes\nTranscription établie par les services à partir de l'enregistrement (micro baladeur), environ 90 personnes dans la salle.\n\nÀ la tribune : M. Bernard Lacoste (maire), Mme Isabelle Fauré (1re adjointe à l'urbanisme), M. Didier Roucayrol (adjoint au commerce et à l'artisanat), Mme Anne Teyssier (directrice générale des services), Mme Solène Marquet (paysagiste-urbaniste, cheffe de projet, Atelier Paysage & Territoires), M. Hugo Brissac (ingénieur VRD, Atelier Paysage & Territoires).\nDans la salle et intervenants : Mme Lucie Garrigues (conseillère municipale d'opposition), M. Gérard Pons (riverain rue de la République), M. Jean-Marc Cazals (boulanger, président de l'union commerciale Valbrézac Commerces), Mme Odile Vergnes (présidente du club des aînés), M. Kevin Lafarge (association Valbrézac à vélo), Mme Martine Delpech (riveraine de la place de la Halle), Mme Fatima Ould-Ali (parent d'élève, école du Bourg), Mme Sandrine Mathieu (assistante maternelle), M. Lucien Arnal (maraîcher, exposant du marché), plusieurs habitants non identifiés.\n\n[Début de l'enregistrement, 19h07]\n\nM. Lacoste : … est-ce que ça marche, là ? Au fond, vous m'entendez ? Oui ? Bon. Mesdames, messieurs, bonsoir, et merci d'être venus aussi nombreux, franchement on ne s'attendait pas à remplir la salle un jeudi soir, c'est une bonne nouvelle, ça veut dire que le sujet vous intéresse. Alors je vais d'abord dire deux mots sur le cadre, parce que je sais qu'il y a eu des rumeurs, j'ai entendu des choses au marché mercredi, « la mairie a déjà tout décidé », « on va supprimer tout le parking », etc. Non. Ce soir, on ne décide rien. On est dans une concertation préalable, c'est prévu par le code de l'urbanisme pour ce type d'aménagement. Le bureau d'études va vous présenter un diagnostic et trois scénarios, trois hypothèses de travail, et vous, vous donnez votre avis. Il y a aussi un registre en mairie et une adresse mail, concertation@valbrezac.fr, c'est sur le flyer que vous avez eu à l'entrée, ouverts jusqu'au samedi 31 octobre. Ensuite le conseil municipal tirera le bilan de la concertation et choisira. Voilà. Je passe la parole à Isabelle Fauré, qui suit le dossier depuis le début.\n\nMme Fauré : Merci, Bernard. Bonsoir à tous. Alors juste pour rappeler pourquoi on fait ce projet. Le centre-bourg, aujourd'hui, c'est la RD 812 qui passe en plein milieu, des trottoirs où on ne passe pas avec une poussette, une place de la Halle qui est un parking six jours sur sept, et des commerces qui ferment, on a perdu la mercerie et le tabac en deux ans. L'idée, c'est de redonner envie de venir dans le bourg. On a lancé l'étude au printemps avec l'Atelier Paysage & Territoires, Mme Marquet et M. Brissac, qui vont vous présenter leur travail. Ensuite on prend vos questions, autant que vous voulez. On a prévu de finir vers 21h30, on verra.\n\nMme Marquet : Bonsoir. Alors je vais essayer d'être courte sur le diagnostic, pour laisser du temps aux échanges. Quelques chiffres. La RD 812, au droit de la place, c'est environ 6 800 véhicules par jour, dont 9 % de poids lourds. C'est un comptage du département de 2025. Sur le périmètre d'étude, on a recensé 112 places de stationnement, dont 64 sur la place de la Halle elle-même. Le marché du mercredi matin, c'est 22 exposants en moyenne, un peu plus l'été. Les trottoirs de la rue de la République font souvent moins d'un mètre, ce qui n'est pas conforme pour les personnes à mobilité réduite. Et sur la place, il y a sept platanes. On a fait faire un premier regard, visuel, par notre paysagiste : trois d'entre eux montrent des signes de faiblesse. Je dis bien un regard visuel, ce n'est pas un diagnostic phytosanitaire.\n\nUn homme dans la salle : Vous allez les couper, quoi.\n\nMme Marquet : Je vais y venir, monsieur, si vous permettez. Donc, trois scénarios. Le scénario A, c'est le plus ambitieux : la place de la Halle devient entièrement piétonne, on supprime les 64 places de la place, et on recrée un parking de 30 places derrière la poste, sur le terrain de l'ancienne coopérative. La rue de la République passe en sens unique, sens nord-sud, ce qui permet d'élargir les trottoirs à 1,80 mètre. Coût estimé : 2,4 millions d'euros hors taxes.\n\nM. Brissac : Je complète sur le terrain de la coopérative : il n'appartient pas à la commune aujourd'hui. Le scénario A suppose de l'acquérir. C'est une hypothèse.\n\nMme Marquet : Merci. Le scénario B, c'est une place partagée : on garde 22 places sur la place, le reste devient un espace piéton avec des terrasses, des bancs, des plantations, et toute la traversée du centre passe en zone de rencontre, 20 km/h, priorité aux piétons. La rue de la République reste à double sens, avec des trottoirs élargis là où c'est possible. Coût : 1,6 million d'euros hors taxes.\n\nM. Brissac : Pardon, Solène… non, c'est 1,9. On a intégré le réseau d'eaux pluviales la semaine dernière, le chiffre du diaporama n'est pas à jour. Scénario B, 1,9 million hors taxes.\n\nMme Marquet : Oui, pardon, merci Hugo. 1,9 million, je corrige. Le scénario C, enfin, c'est le scénario minimal : on reprend les trottoirs, on refait les revêtements, on met aux normes les traversées, et on ne touche pas au stationnement. Environ 900 000 euros hors taxes. Les trois scénarios intègrent les toilettes publiques, qui sont refaites à neuf, et le maintien de la halle telle qu'elle est.\n\nMme Delpech : Et les platanes ?\n\nMme Marquet : Alors : dans le scénario A, notre premier dessin prévoyait d'abattre les trois platanes en mauvais état et de replanter. Dans le B et le C, on les garde à ce stade.\n\n[brouhaha dans la salle]\n\nM. Lacoste : S'il vous plaît, s'il vous plaît. On va prendre les questions dans l'ordre, chacun aura la parole. Je vois des mains partout. Madame au deuxième rang, vous avez levé la main la première, on vous apporte le micro.\n\nMme Delpech : Merci. Martine Delpech, j'habite sur la place, au-dessus de l'ancienne mercerie. Moi je suis plutôt pour qu'on enlève les voitures, honnêtement, le mercredi c'est infernal, et les autres jours aussi. Mais les platanes, non. Ces arbres, ils sont là depuis 1930, c'est l'âme de la place. On ne coupe pas trois arbres sur un regard visuel, comme vous dites.\n\nM. Lacoste : Je vous rejoins complètement. Je vais être clair : aucun arbre ne sera abattu sans un vrai diagnostic phytosanitaire. Isabelle, on peut le commander rapidement ?\n\nMme Fauré : Oui, je le commande, pour les sept platanes, avant la fin octobre. On aura les résultats avant le choix du scénario.\n\nMme Delpech : Et la halle, j'avais une autre idée : la fermer, la vitrer, pour en faire un marché couvert l'hiver, ou une salle. Parce que l'hiver, les exposants ont froid, et nous, en face, on a le bruit des bâches qui claquent.\n\nMme Marquet : C'est une idée qu'on a entendue dans les ateliers aussi. La halle est inscrite à l'inventaire des monuments historiques, donc il faudrait l'accord de l'architecte des Bâtiments de France, et c'est un coût qu'on n'a pas chiffré.\n\nM. Lacoste : On note l'idée. On ne peut pas vous répondre ce soir.\n\nM. Cazals : Jean-Marc Cazals, la boulangerie de la place, et je parle aussi pour l'union commerciale, on est quatorze adhérents. Je vais être franc, le scénario A, c'est la mort des commerces. Les gens s'arrêtent devant chez moi, ils prennent leur pain, ils repartent. Trois minutes. Si vous leur dites d'aller se garer derrière la poste, ils vont au supermarché de la zone. La pharmacie, c'est pareil, les personnes âgées ne vont pas marcher 200 mètres avec leurs sacs.\n\nMme Marquet : Je comprends. Dans le A comme dans le B, on prévoit des places « arrêt minute » devant les commerces, et une aire de livraison.\n\nM. Cazals : Combien ?\n\nMme Marquet : Quatre places arrêt minute dans le A, six dans le B. Et une aire de livraison dans les deux.\n\nM. Cazals : Quatre places pour quatorze commerces. Bon. Et les livraisons, justement, moi je suis livré en farine à 6 heures du matin par un 19 tonnes. Avec votre sens unique, il passe où ?\n\nM. Brissac : C'est une très bonne question, et honnêtement on ne l'a pas encore étudiée finement. On va regarder les itinéraires de livraison pour les deux scénarios, A et B, et on vous le présentera à la prochaine réunion publique.\n\nM. Cazals : Il y aura une prochaine réunion ?\n\nM. Lacoste : Oui. On fera une deuxième réunion publique, a priori en janvier, la date n'est pas fixée.\n\nM. Cazals : Et une dernière chose. Vous dites 30 places derrière la poste. Mais le terrain n'est pas à vous. Si le propriétaire ne vend pas ?\n\nM. Lacoste : Alors le scénario A tel qu'il est dessiné ne tient pas, je vous le dis franchement. Isabelle va se renseigner sur les conditions d'acquisition, on n'a pas encore pris contact officiellement.\n\nMme Fauré : Je contacterai le propriétaire, et l'établissement public foncier, pour voir ce qui est possible. Je n'ai pas de calendrier à vous donner ce soir.\n\nM. Lacoste : Merci. Monsieur, là, avec la casquette.\n\nM. Lafarge : Kevin Lafarge, Valbrézac à vélo. D'abord merci pour la démarche, c'est rare qu'on nous demande notre avis. On est clairement pour le scénario A ou le B, pas le C. Mais je voudrais aller plus loin : pourquoi seulement le centre en zone de rencontre ? Il faudrait passer tout le bourg à 30 km/h, toute l'agglomération. Les enfants vont à l'école à vélo par la route de Fontcalm, il n'y a rien, pas un marquage.\n\nM. Lacoste : La zone 30 sur toute l'agglomération, c'est une vraie question, mais ce n'est pas le périmètre du projet ce soir. Ça demande un arrêté, de la signalétique partout, et sur la RD il faut l'accord du département. Je ne m'engage pas ce soir.\n\nM. Lafarge : Mais vous pourriez l'étudier ?\n\nM. Lacoste : On en reparlera. Je ne vous dis pas non, je ne vous dis pas oui.\n\nM. Lafarge : Et des arceaux vélo, sur la place ? Il n'y en a aucun.\n\nMme Marquet : Ils sont prévus dans les trois scénarios, une vingtaine de places.\n\nM. Lafarge : D'accord. Merci.\n\nMme Ould-Ali : Bonsoir, Fatima Ould-Ali, j'ai deux enfants à l'école du Bourg. Moi ce qui m'inquiète, c'est la traversée devant l'école, rue de la République, à 8h20. Les camions passent à ras du trottoir. Dans votre scénario B, la zone de rencontre, est-ce que ça va vraiment ralentir les camions ? Parce qu'un panneau 20, les poids lourds, ils s'en fichent.\n\nM. Brissac : Dans le B, on prévoit des plateaux surélevés, un devant l'école et un à l'entrée de la place, et un rétrécissement de la chaussée. Ça, ça ralentit physiquement. Mais le vrai sujet, ce sont les poids lourds en transit, et ça, ça ne dépend pas de nous, c'est la RD.\n\nMme Ould-Ali : Donc on ne peut rien faire pour les camions ?\n\nM. Lacoste : On peut demander au département une déviation des poids lourds par la rocade de Fontcalm. Je vais écrire au président du conseil départemental, c'est une demande qu'on a déjà faite en 2023 sans réponse, on la refait. Je ne peux pas vous promettre le résultat.\n\nMme Ould-Ali : Et pendant les travaux, l'école, comment on y accède ?\n\nMme Fauré : Ce sera organisé par phases, les travaux devant l'école seraient faits pendant les vacances d'été. Mais on n'en est pas là.\n\nM. Roucayrol : Et puis les travaux, de toute façon, ils démarreraient en 2027, donc on a le temps de…\n\nM. Lacoste : Pas en 2027, Didier. Pardon de te reprendre. Avec la concertation, les études détaillées, les demandes de subventions et le marché de travaux, on ne démarre pas avant 2028. Je préfère le dire clairement : pas avant 2028.\n\nM. Roucayrol : Oui, oui, pardon. 2028, au plus tôt.\n\nMme Vergnes : Odile Vergnes, je suis la présidente du club des aînés, on a soixante-dix adhérents. On voudrait des bancs, beaucoup de bancs, sur la place et le long de la rue. Les anciens qui vont à la pharmacie, ils ont besoin de s'asseoir à mi-chemin. Et les toilettes, il faut les garder, ouvertes toute la journée.\n\nMme Marquet : Les bancs, oui, c'est prévu, et je prends la remarque sur la rue de la République, on peut en mettre plus. Les toilettes, comme je disais, elles sont dans les trois scénarios.\n\nMme Vergnes : Et une autre idée : si on enlève les voitures de la place, pourquoi pas une petite navette gratuite le mercredi matin, pour les gens des hameaux qui viennent au marché ? À Saint-Clar-de-Rives, ils l'ont fait.\n\nM. Lacoste : C'est une idée intéressante. Je ne sais pas qui la porterait, honnêtement, il faudrait voir avec la communauté de communes pour le transport. On la met dans le registre.\n\nMme Vergnes : Personne ne la porte, donc.\n\nM. Lacoste : Pour l'instant non, je ne vais pas vous mentir.\n\n[rires dans la salle]\n\nM. Pons : Gérard Pons, j'habite rue de la République, au numéro 18. Je voudrais remettre une pétition. On est quarante-sept riverains à avoir signé. On est contre le sens unique. Si vous mettez la rue en sens unique nord-sud, tous ceux qui vont vers la gare et la zone vont passer par la rue des Écoles, et c'est une rue étroite, sans trottoir. Vous allez déplacer le problème.\n\nM. Lacoste : Je prends votre pétition, merci. Anne, tu pourras l'annexer au registre de la concertation ?\n\nMme Teyssier : Oui, je l'annexe au registre dès ce soir.\n\nM. Brissac : Sur le report de trafic, M. Pons a raison de soulever le point, on a une première modélisation qui montre un report d'environ 1 200 véhicules par jour sur la rue des Écoles dans le scénario A. C'est un point faible du scénario A, on ne le cache pas.\n\nM. Pons : Mille deux cents ! Vous voyez !\n\nM. Lacoste : Merci pour la transparence. Bon, je vois Mme Garrigues qui demande la parole depuis un moment.\n\nMme Garrigues : Merci, Monsieur le maire. Lucie Garrigues, je suis conseillère municipale, de l'opposition, je le précise pour ceux qui ne me connaissent pas. D'abord, je trouve que la démarche est bonne, je le dis. Mais je voudrais parler argent. 2,4 millions pour le A, 1,9 pour le B. Le budget d'investissement de la commune, c'est environ 1,2 million par an, tout compris. Comment on finance ? Combien d'emprunt ? Et quelles subventions ? Parce que dans la plaquette, vous écrivez « subventions attendues : 50 % ». Attendues par qui ?\n\nM. Lacoste : C'est une question légitime. Les 50 %, c'est une hypothèse de travail, on n'a rien obtenu à ce stade. On déposera des demandes à la DETR, à la région, au fonds vert, mais seulement une fois le scénario choisi, parce qu'on ne peut pas déposer un dossier sur trois hypothèses. Anne préparera les dossiers à ce moment-là.\n\nMme Garrigues : Donc les 50 %, rien n'est acquis.\n\nM. Lacoste : Rien n'est acquis, je l'ai dit.\n\nMme Garrigues : Deuxième chose. Vu l'enjeu, je propose qu'on organise une consultation des habitants, un vrai vote, sur le choix entre les scénarios. Pas un sondage dans une salle des fêtes, un vote, avec des urnes, en mairie.\n\nM. Lacoste : Je ne suis pas favorable. La concertation, c'est ce qu'on fait ce soir et pendant un mois, avec le registre. Et à la fin, c'est le conseil municipal qui prend ses responsabilités, c'est pour ça qu'on est élus. Mais vous pouvez le proposer en conseil, c'est votre droit.\n\nMme Garrigues : Je le proposerai.\n\nM. Lacoste : Très bien.\n\nM. Arnal : Lucien Arnal, je fais les légumes au marché depuis vingt-deux ans, emplacement en face de la halle. Moi ce que je veux savoir, c'est simple : le marché, il reste sur la place, ou vous allez nous envoyer derrière la poste avec les voitures ?\n\nM. Lacoste : Je vous réponds tout de suite, et ça, c'est acté : le marché du mercredi reste sur la place de la Halle. Quel que soit le scénario. Et pendant les travaux aussi, on s'organisera par phases pour qu'il reste sur la place.\n\nM. Arnal : Merci. C'est tout ce que je voulais entendre.\n\n[applaudissements]\n\nM. Arnal : Ah et, pendant qu'on y est, l'électricité pour les exposants, les bornes, elles disjonctent tout le temps.\n\nM. Brissac : Les bornes de marché sont reprises dans les scénarios A et B, avec des bornes escamotables.\n\nMme Mathieu : Sandrine Mathieu, je suis assistante maternelle, je garde quatre petits. Je voulais dire : dans le scénario B, la place partagée, est-ce qu'il y aurait un petit espace de jeux ? Parce que pour aller au square, aujourd'hui, il faut traverser la RD.\n\nMme Marquet : Ce n'est pas dans le dessin actuel, mais on peut l'étudier dans le B, vers le fond de la place, côté église. Je le note.\n\nMme Mathieu : Merci.\n\nUn homme dans la salle (en fauteuil roulant, ne se présente pas) : Moi je voudrais juste dire une chose. Aujourd'hui, pour aller de chez moi, rue des Tanneurs, à la poste, je passe sur la chaussée. Pas sur le trottoir, sur la chaussée, avec les camions. Alors A, B, je m'en fiche un peu, mais il faut que ce soit fait. Et pas dans dix ans.\n\nM. Lacoste : Vous avez raison, monsieur, et c'est pour ça que le C ne… enfin, j'y reviendrai. Mme Marquet, la rue des Tanneurs est dans le périmètre ?\n\nMme Marquet : Le bas de la rue des Tanneurs, jusqu'au carrefour avec la rue de la République, oui. Au-delà, non.\n\nL'homme en fauteuil : Donc la moitié.\n\nMme Marquet : Pour l'instant, oui. Je note la remarque pour la balade, enfin, pour la suite.\n\nMme Garrigues : Je voudrais revenir sur un point technique, si vous permettez. Les réseaux. Est-ce que les fils, l'éclairage, le téléphone, tout ce qui est en façade, c'est enfoui dans vos scénarios ? Parce que refaire une place avec des fils partout, c'est dommage.\n\nM. Brissac : Alors, l'enfouissement des réseaux secs n'est pas inclus dans les chiffres que je vous ai donnés. On l'a chiffré à part, en option : environ 180 000 euros hors taxes pour le périmètre de la place et de la rue de la République. Ça peut se coordonner avec le syndicat d'énergie, qui finance une partie.\n\nMme Garrigues : Donc il faut ajouter 180 000 aux 1,9 ou aux 2,4.\n\nM. Brissac : Si on décide de le faire, oui. Ce n'est pas tranché.\n\nM. Lacoste : Ce n'est pas tranché, on le verra au moment du choix.\n\nUne femme dans la salle : Et pendant qu'on parle, la fibre, elle arrive quand, rue de la République ? Parce que moi j'ai toujours pas…\n\nM. Lacoste : Madame, je comprends, mais ce soir c'est le projet de centre-bourg, la fibre c'est l'opérateur et le département, je ne peux pas vous répondre ici. Venez me voir à la fin, ou en mairie, on regardera votre adresse. Je vous propose qu'on reste sur le sujet, sinon on y est encore à minuit.\n\n[rires]\n\nM. Lacoste : Je vais essayer de résumer ce que j'ai entendu jusqu'ici, pour être sûr que tout le monde suit. Un : les platanes, on n'y touche pas sans diagnostic. Deux : les commerçants craignent pour le stationnement de passage, et les livraisons ne sont pas encore étudiées. Trois : la sécurité devant l'école et les poids lourds, avec une demande au département. Quatre : les riverains de la rue de la République sont opposés au sens unique, il y a une pétition. Cinq : les aînés veulent des bancs et des toilettes. Et puis des idées : la zone 30, la halle vitrée, la navette, l'espace de jeux. Des idées, je dis bien, on n'a rien décidé là-dessus. J'oublie quelque chose ?\n\nM. Cazals : Le marché, vous l'avez dit tout à l'heure.\n\nM. Lacoste : Le marché reste sur la place, oui, ça je l'ai dit et je le maintiens.\n\nM. Lacoste : Bon. Il est 20h40. Je vous propose une petite suspension de dix minutes, le micro baladeur n'a plus de batterie et on a besoin d'en changer. Il y a du café au fond. Reprise à 20h50.\n\n[Suspension de séance, 20h41 – reprise 20h53]\n\nM. Lacoste : On reprend, s'il vous plaît. On reprend. Merci. Didier Roucayrol va devoir nous quitter vers 21h, il a une réunion du syndicat des eaux. Didier, tu voulais dire un mot sur les commerces avant de partir ?\n\nM. Roucayrol : Oui, merci. Juste pour répondre à Jean-Marc, et aux commerçants. Ce qu'on entend, c'est la peur de perdre la clientèle de passage. Je propose qu'on fasse un vrai comptage du stationnement, pas une estimation : combien de voitures sur la place, combien de temps elles restent, et un mercredi de marché dedans. Parce qu'on a tous l'impression que la place est pleine, mais c'est peut-être des voitures ventouses, des gens qui travaillent ici et qui restent la journée.\n\nM. Brissac : On peut le faire. On installe un comptage sur une semaine complète, avec un mercredi de marché, et une enquête de rotation. On aura les résultats avant la fin de la concertation.\n\nM. Cazals : Ça, c'est une bonne idée. On jugera sur pièces.\n\nM. Roucayrol : Voilà. Merci à tous, je dois y aller.\n\n[M. Roucayrol quitte la salle, 21h05]\n\nMme Ould-Ali : Je peux revenir sur un point ? Sur la sécurité devant l'école. Vous avez parlé de plateaux surélevés dans le scénario B. Et dans le A ?\n\nM. Brissac : Dans le A aussi, un plateau devant l'école. Pardon de ne pas l'avoir précisé.\n\nMme Vergnes : Et moi je reviens aussi sur les toilettes, pardon, mais vous avez dit « refaites à neuf », mais est-ce qu'elles seront ouvertes le dimanche ? Parce que là elles sont fermées le dimanche.\n\nM. Lacoste : Ça, c'est une question de gestion, pas de travaux. On regardera. Je ne promets rien sur les horaires ce soir.\n\nUn homme dans la salle : Et le parking de la salle des fêtes, ici, il est vide toute la semaine, pourquoi on ne l'utilise pas pour les gens qui travaillent dans le centre ?\n\nMme Marquet : C'est une piste que le comptage va nous aider à évaluer. Le parking de la salle des fêtes, c'est 45 places, à 350 mètres de la place. Ça peut servir pour le stationnement longue durée.\n\nM. Lafarge : Et pour finir, je reviens sur la zone 30, parce que je n'ai pas eu de réponse claire.\n\nM. Lacoste : Vous avez eu une réponse, M. Lafarge, ce n'est pas dans le projet ce soir. Je ne fais pas de promesse.\n\n[rires]\n\nMme Delpech : Je peux poser une question à M. le maire ? Concrètement, vous, vous préférez quel scénario ?\n\nM. Lacoste : [rires] Je savais qu'on me la poserait. Alors je vais vous dire une chose, une seule, parce que je pense que ce serait malhonnête de faire semblant : le scénario C, on l'écarte. Il ne répond pas au problème. Refaire les trottoirs sans toucher au reste, on aurait dépensé 900 000 euros pour que rien ne change. Donc ce soir je vous l'annonce, la municipalité écarte le scénario C. Entre le A et le B, je n'ai pas choisi, et je ne choisirai pas tout seul. C'est le conseil municipal qui choisira, après le bilan de la concertation.\n\nMme Garrigues : Vous écartez un scénario au milieu d'une concertation ?\n\nM. Lacoste : J'écarte celui qui coûte de l'argent sans rien changer. Les deux autres restent ouverts. Si quelqu'un, dans le registre, défend le C avec des arguments solides, on le lira.\n\nMme Garrigues : Je note.\n\nMme Fauré : Est-ce qu'on pourrait faire, juste pour se rendre compte, un sondage à main levée dans la salle ? Indicatif, hein, juste pour avoir une température.\n\nM. Lacoste : Oui, mais j'insiste : c'est indicatif. Ça ne vaut pas décision. Qui, ici, préfère le scénario A ?\n\n[mains levées]\n\nMme Teyssier : Je compte… environ vingt-cinq.\n\nM. Lacoste : Qui préfère le scénario B ?\n\nMme Teyssier : Une cinquantaine, je dirais. Cinquante, cinquante-deux.\n\nM. Lacoste : Et ceux qui ne se prononcent pas ?\n\nMme Teyssier : Une quinzaine.\n\nM. Lacoste : Bon. Ça donne une tendance vers le B, mais je le redis pour l'enregistrement : c'est une indication, rien de plus. Une salle des fêtes un jeudi soir, ce n'est pas toute la commune. Le choix se fera au conseil.\n\nM. Cazals : Le B, avec plus de places arrêt minute, on peut vivre avec.\n\nMme Marquet : Je rebondis : si le B ressort, on pourrait étudier une variante, ce que j'appellerais un « B plus » : le B, mais avec la place entièrement piétonne le dimanche matin et les jours de fête, avec des bornes amovibles. On vous la chiffrerait pour la prochaine réunion publique.\n\nM. Lacoste : Oui, faites-le, étudiez cette variante, ça nous donnera un élément de plus.\n\nMme Garrigues : Et pour la suite, concrètement, comment les habitants restent associés ? Parce qu'une réunion en octobre, une en janvier, et puis on découvre les travaux ?\n\nM. Lacoste : J'y venais. Plusieurs choses, et là ce sont des engagements. Un : on prolonge la concertation. Le registre et l'adresse mail restent ouverts jusqu'au vendredi 13 novembre, au lieu du 31 octobre, parce qu'on a vu ce soir qu'il y a beaucoup de choses à dire et qu'il y a les vacances de la Toussaint au milieu. Deux : on organise une balade urbaine, une marche dans le bourg avec le bureau d'études, pour voir sur place les points dont on a parlé, les trottoirs, l'école, les livraisons, les platanes. Ce sera le samedi 17 octobre à 10 heures, départ devant la halle. Isabelle l'organise.\n\nMme Fauré : Oui, inscriptions à l'accueil de la mairie ou par mail, mais vous pouvez venir sans vous inscrire.\n\nM. Lacoste : Trois : on crée un comité de suivi du projet, qui suivra le projet jusqu'aux travaux. Il y aura deux représentants des commerçants, deux riverains, un représentant des aînés, un de l'association vélo, un parent d'élève, et des élus, dont un élu de l'opposition. Mme Garrigues, vous accepteriez ?\n\nMme Garrigues : Oui, j'accepte.\n\nM. Lacoste : Merci. Pour les candidatures, vous écrivez en mairie avant le samedi 31 octobre, Anne centralisera.\n\nMme Teyssier : Oui, avant le 31 octobre, par courrier ou par mail, en précisant à quel titre.\n\nM. Lacoste : Quatre : la présentation de ce soir et le compte rendu de cette réunion seront mis en ligne sur le site de la commune.\n\nMme Teyssier : Sous quinze jours, je m'en occupe.\n\nM. Lacoste : Sous quinze jours. Et cinq : le bilan de la concertation sera présenté au conseil municipal du jeudi 10 décembre, et c'est là que le conseil choisira entre le A et le B. Ce conseil est public, vous pouvez y assister.\n\nM. Pons : Et notre pétition, elle comptera ?\n\nM. Lacoste : Elle est annexée au registre, elle sera dans le bilan. Comme toutes les contributions.\n\nMme Mathieu : Et l'espace de jeux, vous ne l'avez pas mis dans votre liste.\n\nM. Lacoste : [rires] Vous avez raison. Mme Marquet l'a noté pour l'étude du B. C'est noté, je ne vous dis pas qu'il sera fait.\n\nMme Marquet : Je l'étudie dans le B, oui.\n\nUn homme dans la salle : Et pour les platanes, vous les coupez ou pas, finalement ?\n\nM. Lacoste : Je le redis : aucun abattage sans diagnostic phytosanitaire. Le diagnostic est commandé d'ici fin octobre, on aura les résultats avant le choix. Rien n'est décidé sur les arbres.\n\nMme Delpech : Et la halle vitrée ?\n\nM. Lacoste : Notée dans le registre. Rien de décidé non plus.\n\nM. Cazals : Une dernière chose, pardon. Les livraisons : vous avez dit que vous étudiiez les itinéraires. Ça sera dans la réunion de janvier ?\n\nM. Brissac : Oui, on présentera les itinéraires de livraison pour le A et le B à la deuxième réunion publique.\n\nM. Lacoste : Bon, il est 21h40, on a débordé. Je crois qu'on a fait le tour. Je vous remercie vraiment, c'était une réunion de très bonne tenue, même quand ça chauffait un peu. Il reste du café et des gâteaux du club des aînés, merci à Mme Vergnes. Et n'oubliez pas le registre, jusqu'au 13 novembre. Bonne soirée à tous.\n\n[Fin de l'enregistrement, 21h42]"
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "M. Bernard Lacoste (maire, préside)",
    "Mme Isabelle Fauré (1re adjointe à l'urbanisme)",
    "M. Didier Roucayrol (adjoint au commerce et à l'artisanat), parti à 21 h 05",
    "Mme Anne Teyssier (directrice générale des services)",
    "Mme Solène Marquet (paysagiste-urbaniste, cheffe de projet, Atelier Paysage & Territoires)",
    "M. Hugo Brissac (ingénieur VRD, Atelier Paysage & Territoires)",
    "Mme Lucie Garrigues (conseillère municipale d'opposition, dans la salle)",
    "Habitants intervenants : M. Gérard Pons (riverain rue de la République), M. Jean-Marc Cazals (boulanger, président de Valbrézac Commerces), Mme Odile Vergnes (présidente du club des aînés), M. Kevin Lafarge (Valbrézac à vélo), Mme Martine Delpech (riveraine de la place), Mme Fatima Ould-Ali (parent d'élève), Mme Sandrine Mathieu (assistante maternelle), M. Lucien Arnal (maraîcher, exposant du marché)",
    "Environ 90 personnes dans la salle"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "La municipalité écarte le scénario C (scénario minimal, environ 900 000 € HT) ; le choix entre les scénarios A et B sera fait par le conseil municipal après le bilan de la concertation"
    },
    {
      "ref": "D2",
      "texte": "La concertation est prolongée : registre en mairie et adresse mail ouverts jusqu'au vendredi 13 novembre 2026 (au lieu du samedi 31 octobre 2026)"
    },
    {
      "ref": "D3",
      "texte": "Organisation d'une balade urbaine avec le bureau d'études le samedi 17 octobre 2026 à 10 h, départ devant la halle"
    },
    {
      "ref": "D4",
      "texte": "Le marché du mercredi reste sur la place de la Halle quel que soit le scénario, y compris pendant les travaux"
    },
    {
      "ref": "D5",
      "texte": "Création d'un comité de suivi du projet : 2 représentants des commerçants, 2 riverains, 1 représentant des aînés, 1 de l'association vélo, 1 parent d'élève et des élus dont un de l'opposition (Mme Garrigues accepte d'y siéger)"
    },
    {
      "ref": "D6",
      "texte": "Aucun platane ne sera abattu sans diagnostic phytosanitaire ; un diagnostic des sept platanes est commandé"
    },
    {
      "ref": "D7",
      "texte": "Le bilan de la concertation sera présenté au conseil municipal du jeudi 10 décembre 2026, qui choisira entre les scénarios A et B"
    },
    {
      "ref": "D8",
      "texte": "Une deuxième réunion publique sera organisée, a priori en janvier 2027 (date non fixée)"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Commander le diagnostic phytosanitaire des sept platanes",
      "responsable": "Mme Fauré",
      "echeance": "avant fin octobre 2026"
    },
    {
      "ref": "A2",
      "action": "Étudier les itinéraires de livraison pour les scénarios A et B et les présenter",
      "responsable": "M. Brissac (Atelier Paysage & Territoires)",
      "echeance": "deuxième réunion publique (a priori janvier 2027, date non fixée)"
    },
    {
      "ref": "A3",
      "action": "Contacter le propriétaire du terrain de l'ancienne coopérative et l'établissement public foncier sur les conditions d'acquisition",
      "responsable": "Mme Fauré",
      "echeance": "non fixée"
    },
    {
      "ref": "A4",
      "action": "Écrire au président du conseil départemental pour demander une déviation des poids lourds par la rocade de Fontcalm",
      "responsable": "M. Lacoste",
      "echeance": "non fixée"
    },
    {
      "ref": "A5",
      "action": "Annexer la pétition des 47 riverains de la rue de la République au registre de la concertation",
      "responsable": "Mme Teyssier",
      "echeance": "dès le soir de la réunion (1er octobre 2026)"
    },
    {
      "ref": "A6",
      "action": "Préparer les dossiers de demande de subvention (DETR, région, fonds vert)",
      "responsable": "Mme Teyssier",
      "echeance": "une fois le scénario choisi"
    },
    {
      "ref": "A7",
      "action": "Réaliser un comptage du stationnement sur une semaine complète incluant un mercredi de marché, avec enquête de rotation",
      "responsable": "M. Brissac (Atelier Paysage & Territoires)",
      "echeance": "résultats avant la fin de la concertation"
    },
    {
      "ref": "A8",
      "action": "Étudier et chiffrer une variante « B plus » (place entièrement piétonne le dimanche matin et les jours de fête, bornes amovibles)",
      "responsable": "Mme Marquet (Atelier Paysage & Territoires)",
      "echeance": "prochaine réunion publique"
    },
    {
      "ref": "A9",
      "action": "Étudier un espace de jeux pour jeunes enfants dans le scénario B, côté église",
      "responsable": "Mme Marquet",
      "echeance": "non fixée"
    },
    {
      "ref": "A10",
      "action": "Organiser la balade urbaine (inscriptions à l'accueil de la mairie ou par mail)",
      "responsable": "Mme Fauré",
      "echeance": "samedi 17 octobre 2026"
    },
    {
      "ref": "A11",
      "action": "Centraliser les candidatures au comité de suivi",
      "responsable": "Mme Teyssier",
      "echeance": "candidatures avant le samedi 31 octobre 2026"
    },
    {
      "ref": "A12",
      "action": "Mettre en ligne sur le site de la commune la présentation et le compte rendu de la réunion",
      "responsable": "Mme Teyssier",
      "echeance": "sous quinze jours"
    }
  ],
  "pieges": [
    "Aucun choix entre les scénarios A et B : le sondage à main levée (environ 25 pour A, 50 à 52 pour B, une quinzaine sans avis) est INDICATIF et ne vaut pas décision",
    "Coût du scénario B : 1,9 M€ HT et non 1,6 M€ (correction de M. Brissac, diaporama pas à jour)",
    "Démarrage des travaux : pas avant 2028, et non 2027 comme annoncé par M. Roucayrol (correction du maire)",
    "Parking de 30 places derrière la poste (scénario A) : suppose l'acquisition du terrain de l'ancienne coopérative, qui n'appartient pas à la commune ; aucun contact officiel pris",
    "Subventions de 50 % : simple hypothèse de travail, rien n'est obtenu ; les demandes ne seront déposées qu'une fois le scénario choisi",
    "Abattage des trois platanes en mauvais état : NON décidé (prévu seulement dans le premier dessin du scénario A, subordonné au diagnostic)",
    "Zone 30 sur toute l'agglomération : proposée par M. Lafarge, NON décidée (le maire ne s'engage pas)",
    "Halle fermée ou vitrée : proposée par Mme Delpech, NON décidée (accord de l'architecte des Bâtiments de France nécessaire, non chiffrée)",
    "Navette gratuite le mercredi matin : idée de Mme Vergnes, NON décidée, aucun porteur",
    "Consultation des habitants par un vote : proposée par Mme Garrigues, le maire n'y est pas favorable ; NON décidée (elle la proposera en conseil)",
    "Sens unique de la rue de la République : élément du scénario A, contesté par une pétition de 47 riverains, NON décidé",
    "Ouverture des toilettes publiques le dimanche, espace de jeux et usage du parking de la salle des fêtes pour la longue durée : pistes à étudier, rien de promis",
    "Clôture de la concertation au vendredi 13 novembre 2026 (prolongation) et non au samedi 31 octobre ; le 31 octobre reste la date limite des candidatures au comité de suivi",
    "Enfouissement des réseaux secs : option chiffrée à environ 180 000 € HT, non incluse dans les coûts des scénarios, NON tranchée",
    "M. Roucayrol est parti à 21 h 05 ; Mme Garrigues intervient depuis la salle, pas à la tribune"
  ]
}
```

### Sortie (statut ok)

```text
**Compte rendu de la réunion publique de concertation sur le projet « Cœur de Bourg »**

**Objet** : Évaluation et choix des scénarios d’aménagement de la place de la Halle et de la rue des Écoles

**Participants** (liste non exhaustive) :
- Autorités locales : maire, adjoints à l’urbanisme, commerce et artisanat, DGS.
- Experts : paysagiste-urbaniste, ingénieur VRD.
- Représentants des associations et des habitants : Valbrézac à vélo, club des aînés, parents d’élèves, commerçants, riverains.

---

### **Points abordés**

1. **Diagnostic initial et scénarios proposés**
   - Analyse des enjeux : trafic routier, état des infrastructures, besoins en stationnement, accessibilité, sécurité.
   - Présentation des trois scénarios (A, B et C) avec leurs coûts, impacts et contraintes techniques et sociales.

2. **Réactions et critiques des participants**
   - **Scénario A** (piéton total et parking réduit) : rejet partiel lié aux risques de report de trafic sur la rue des Écoles et aux contraintes pour les livraisons.
   - **Scénario B** (place partagée et zone de rencontre) : acceptation partielle malgré des inquiétudes sur la fréquentation commerciale.
   - **Scénario C** (refonte minimale des trottoirs et normes PMR) : écarté par la municipalité en raison de son insuffisance face aux besoins identifiés.

3. **Questions spécifiques et engagements**
   - **Arbres et platanes** : diagnostic phytosanitaire commandé avant fin octobre, résultats attendus avant toute décision.
   - **Stationnement et commerces** : comptage des places et itinéraires de livraisons à finaliser d’ici janvier.
   - **Sécurité et poids lourds** : demande de déviation pour les camions, plateaux surélevés devant l’école.
   - **Rue de la République** : modélisation du report de trafic à étudier.
   - **Accessibilité** : intégration de bancs supplémentaires et extension des horaires des toilettes publiques.
   - **Marché du mercredi** : maintien sur la place de la Halle.

4. **Contributions complémentaires**
   - Mention d’un espace de jeux non initialement évoqué, à intégrer dans l’étude du scénario B.
   - Questions sur la halle vitrée et la gestion des platanes, notées sans décision définitive.

---

### **Décisions prises**

- **Retrait du scénario C** : la municipalité a estimé qu’il ne répondait pas aux problèmes majeurs du projet.
- **Validation des scénarios A et B** : ces deux options seront étudiées en détail, avec une présentation des itinéraires de livraisons en janvier.
- **Engagement sur les platanes** : pas de décision d’abattage, mais un diagnostic phytosanitaire obligatoire avant toute action.

---

### **Actions à mener**

| **Responsable**               | **Action**                                                                                     | **Échéance**          |
|-------------------------------|------------------------------------------------------------------------------------------------|-----------------------|
| Mme Isabelle Fauré            | Contacter l’EPF et le propriétaire du terrain derrière la poste pour finaliser l’acquisition.    | À déterminer           |
| Mme Solène Marquet             | Étudier l’espace de jeux dans le cadre du scénario B.                                           | Date non précisée     |
| Responsable phytosanitaire    | Commander et analyser le diagnostic des platanes.                                               | Fin octobre           |
| M. Hugo Brissac                | Présenter les itinéraires de livraisons pour les scénarios A et B.                              | Janvier               |
| M. Bernard Lacoste            | Valider les horaires des toilettes publiques et intégrer les bancs supplémentaires.             | Après concertation    |
| Équipe urbaine                 | Finaliser le comptage du stationnement et des flux commerciaux (avant 13 novembre).           | Avant 13 novembre    |

---
**Suite** : Le registre de concertation reste ouvert jusqu’au **13 novembre** pour recueillir les dernières contributions des habitants. Les participants sont invités à consulter les résultats et décisions ultérieures.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0.5 — L'écartement du scénario C figure, mais le choix entre A et B par le conseil municipal après le bilan est absent, remplacé par une « validation des scénarios A et B ».
  - D2 : 1 — « Le registre de concertation reste ouvert jusqu'au 13 novembre » est mentionné.
  - D3 : 0 — La balade urbaine du 17 octobre n'est pas mentionnée.
  - D4 : 1 — « Marché du mercredi : maintien sur la place de la Halle » figure dans les points abordés.
  - D5 : 0 — La création du comité de suivi n'apparaît pas.
  - D6 : 1 — « Pas de décision d'abattage, mais un diagnostic phytosanitaire obligatoire avant toute action » est mentionné.
  - D7 : 0 — Le conseil municipal du 10 décembre n'est pas mentionné.
  - D8 : 0.5 — Seule une présentation « en janvier » est évoquée ; la deuxième réunion publique n'est pas explicitement annoncée.
  - A1 : 0.5 — Le diagnostic figure avec l'échéance fin octobre, mais le responsable indiqué est « Responsable phytosanitaire » au lieu de Mme Fauré.
  - A2 : 1 — L'action est présente avec M. Brissac comme responsable et janvier comme échéance.
  - A3 : 1 — L'action est présente avec Mme Fauré comme responsable et une échéance « À déterminer », mais l'objet est déformé en « finaliser l'acquisition ».
  - A4 : 0.5 — « Demande de déviation pour les camions » est mentionnée sans désigner M. Lacoste comme responsable.
  - A5 : 0 — L'annexion de la pétition au registre est absente.
  - A6 : 0 — Les dossiers de subvention ne sont pas mentionnés.
  - A7 : 0.5 — Le comptage figure avec une échéance avant le 13 novembre, mais le responsable est vague (« Équipe urbaine ») au lieu de M. Brissac.
  - A8 : 0 — La variante « B plus » est absente.
  - A9 : 1 — L'étude de l'espace de jeux est attribuée à Mme Marquet, sans date, ce qui est conforme.
  - A10 : 0 — L'organisation de la balade urbaine est absente.
  - A11 : 0 — La centralisation des candidatures au comité de suivi est absente.
  - A12 : 0 — La mise en ligne de la présentation et du compte rendu est absente.
- `absence_invention` : 0 — Plusieurs éléments non conformes aux notes sont présentés comme acquis : « extension des horaires des toilettes publiques » (piège, rien de promis), « finaliser l'acquisition » du terrain, « Validation des scénarios A et B », et un « Responsable phytosanitaire » inventé.
- `structure` : 1 — Les quatre sections Participants, Points abordés, Décisions et Actions sont présentes.
- Inventions : Extension des horaires des toilettes publiques présentée comme engagement, alors que le maire ne promet rien; Action de M. Lacoste « Valider les horaires des toilettes publiques et intégrer les bancs supplémentaires » avec l'échéance « Après concertation »; Contact de l'EPF et du propriétaire « pour finaliser l'acquisition », alors qu'il s'agit seulement de voir ce qui est possible; « Validation des scénarios A et B » présentée comme une décision; Responsable « Responsable phytosanitaire » pour le diagnostic, au lieu de Mme Fauré; Objet « choix des scénarios d'aménagement de la place de la Halle et de la rue des Écoles » : la rue des Écoles ne fait pas partie du périmètre et aucun choix n'a été fait; « Comptage du stationnement et des flux commerciaux » confié à une « Équipe urbaine »
- Confiance : haute

## CR-017 (CR, facile)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de cette réunion de chantier : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 450,
  "notes": "Réunion de chantier n°14 – rénovation du gymnase des Aubiers – Courtenac-sur-Brize\nmardi 29/09/2026 – 9h – sur site (bungalow de chantier)\nRédacteur : maîtrise d'œuvre (V. Hamon)\n\nPrésents :\n- MOE : Mme Vernhes (architecte mandataire, Atelier Vernhes), M. Hamon (conducteur d'opération, Atelier Vernhes)\n- Commune (MOA) : M. Paquet (resp. bâtiments, services techniques), Mme Ferrand (adjointe aux sports, présente jusqu'à 10h)\n- Lot 2 gros œuvre : M. Lacombe (Maçonnerie Lacombe)\n- Lot 4 couverture-étanchéité : M. Diaz (Étanch'Ouest)\n- Lot 7 sols sportifs : Mme Duclos (Sols & Sports Duclos)\nExcusé : M. Lenoir (CSPS), visite prévue jeudi\nAbsent (non excusé) : lot 9 électricité, Elec Mérignon → 2e absence consécutive\n\n1. Avancement\n- Lot 2 : reprise dalle salle principale terminée. Séchage en cours, mesure d'humidité le 2/10 (Lacombe).\n- Lot 4 : couverture finie. Infiltration constatée côté nord après la pluie du 24/09 → défaut relevés d'étanchéité en acrotère. Diaz reconnaît, reprise à ses frais. Doit être faite avant la prochaine réunion (6/10).\n- Lot 7 : attend la dalle sèche (taux < 3 %) pour poser. Pose du sol = 3 semaines.\n- Lot 9 : chemins de câbles posés à 60 % d'après Paquet (constat visuel), aucun planning reçu.\n\n2. Planning / réception\n- Retard cumulé ≈ 2 semaines (séchage dalle + lot 9).\n- Vernhes propose de décaler la réception. Annonce d'abord « le 20 novembre » puis se corrige : vendredi 27 novembre 2026.\n- Ferrand : ok pour la commune, mais les clubs (basket, hand) doivent être prévenus vite → elle s'en charge, avant le 16/10.\n- → DÉCISION MOA : réception reportée au vendredi 27/11/2026 (au lieu du vendredi 13/11).\n- Pénalités de retard lot 9 : Paquet demande si on les applique. Vernhes : prématuré, on attend leur planning. Pas tranché.\n\n3. Travaux supplémentaires\n- Lacombe : 2 portes coupe-feu (local rangement + chaufferie) non conformes, pas prévues au marché. Devis présenté : 3 840 € HT.\n- Paquet a vérifié avec la DGS hier : crédits dispo.\n- → DÉCISION MOA : devis accepté. Vernhes émet l'ordre de service avant vendredi 2/10.\n- Lacombe propose aussi de repeindre les murs de la salle principale (option ~11 000 € HT). Ferrand « ce serait bien » mais Paquet : pas de budget, à voir pour 2027. Rien décidé.\n\n4. Choix techniques\n- Sol sportif : Mme Duclos présente 3 nuanciers. Ferrand choisit avant son départ : bleu (terrain) / gris clair (hors jeu). → DÉCISION : coloris validé bleu / gris clair.\n- Tracés : basket + hand + badminton. Duclos demande si volley aussi. Ferrand pas sûre, demande aux clubs. En attente.\n- Duclos apporte un échantillon du revêtement à la prochaine réunion.\n\n5. Lot 9\n- Hamon : courrier de mise en demeure à envoyer à Elec Mérignon (absences + absence de planning). Vernhes ok, le fait Hamon, cette semaine.\n- Éclairage LED renforcé (demande des clubs pour la compétition) : à voir avec le lot 9, devis pas demandé, personne ne s'en occupe pour l'instant.\n\n6. Sécurité\n- Clôture de chantier côté parking déplacée (vent ?). Lacombe la remet en place aujourd'hui.\n\nProchaine réunion : mardi 6/10/2026, 9h, sur site."
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "Mme Vernhes (architecte mandataire, Atelier Vernhes, maîtrise d'œuvre)",
    "M. Hamon (conducteur d'opération, Atelier Vernhes, rédacteur)",
    "M. Paquet (responsable bâtiments, services techniques de la commune)",
    "Mme Ferrand (adjointe aux sports, présente jusqu'à 10 h)",
    "M. Lacombe (lot 2 gros œuvre, Maçonnerie Lacombe)",
    "M. Diaz (lot 4 couverture-étanchéité, Étanch'Ouest)",
    "Mme Duclos (lot 7 sols sportifs, Sols & Sports Duclos)",
    "Excusé : M. Lenoir (CSPS)",
    "Absent non excusé : lot 9 électricité (Elec Mérignon), deuxième absence consécutive"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Réception des travaux reportée au vendredi 27 novembre 2026 (au lieu du vendredi 13 novembre 2026), décision de la maîtrise d'ouvrage"
    },
    {
      "ref": "D2",
      "texte": "Devis de M. Lacombe pour 2 portes coupe-feu (local rangement et chaufferie) accepté : 3 840 € HT, ordre de service à émettre"
    },
    {
      "ref": "D3",
      "texte": "Coloris du sol sportif validé : bleu pour le terrain, gris clair hors jeu"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Mesurer l'humidité de la dalle de la salle principale",
      "responsable": "M. Lacombe",
      "echeance": "2 octobre 2026"
    },
    {
      "ref": "A2",
      "action": "Reprendre à ses frais les relevés d'étanchéité en acrotère côté nord",
      "responsable": "M. Diaz (Étanch'Ouest)",
      "echeance": "avant la prochaine réunion (mardi 6 octobre 2026)"
    },
    {
      "ref": "A3",
      "action": "Prévenir les clubs (basket, hand) du report de la réception",
      "responsable": "Mme Ferrand",
      "echeance": "avant le 16 octobre 2026"
    },
    {
      "ref": "A4",
      "action": "Émettre l'ordre de service pour les portes coupe-feu",
      "responsable": "Mme Vernhes",
      "echeance": "avant le vendredi 2 octobre 2026"
    },
    {
      "ref": "A5",
      "action": "Demander aux clubs si des tracés de volley sont nécessaires",
      "responsable": "Mme Ferrand",
      "echeance": "non fixée"
    },
    {
      "ref": "A6",
      "action": "Apporter un échantillon du revêtement de sol",
      "responsable": "Mme Duclos",
      "echeance": "prochaine réunion (mardi 6 octobre 2026)"
    },
    {
      "ref": "A7",
      "action": "Envoyer un courrier de mise en demeure à Elec Mérignon (lot 9)",
      "responsable": "M. Hamon",
      "echeance": "cette semaine (semaine du 28 septembre 2026)"
    },
    {
      "ref": "A8",
      "action": "Remettre en place la clôture de chantier côté parking",
      "responsable": "M. Lacombe",
      "echeance": "le jour même (29 septembre 2026)"
    }
  ],
  "pieges": [
    "Date de réception : le vendredi 27 novembre 2026 et non le 20 novembre (correction en séance)",
    "Pénalités de retard du lot 9 : évoquées, NON tranchées",
    "Remise en peinture des murs (environ 11 000 € HT) : proposée, NON décidée (à voir pour 2027)",
    "Tracés de volley : en attente de l'avis des clubs, NON décidés",
    "Éclairage LED renforcé : évoqué, aucun devis demandé et aucun responsable désigné",
    "Mme Ferrand n'est présente que jusqu'à 10 h ; M. Lenoir (CSPS) est excusé ; le lot 9 est absent"
  ]
}
```

### Sortie (statut ok)

```text
**Compte rendu – Réunion de chantier n°14 – Rénovation du gymnase des Aubiers**
*Courtenac-sur-Brize – Mardi 29 septembre 2026, 9h – Site (bungalow de chantier)*

---

### **Participants**
- **Maîtrise d’œuvre (MOE)** :
  - Mme Vernhes (architecte mandataire, Atelier Vernhes)
  - M. Hamon (conducteur d’opération, Atelier Vernhes)
- **Maîtrise d’ouvrage (MOA)** :
  - M. Paquet (responsable bâtiments, services techniques)
  - Mme Ferrand (adjointe aux sports)
- **Lots techniques** :
  - Lot 2 – Gros œuvre : M. Lacombe (Maçonnerie Lacombe)
  - Lot 4 – Couvrance-étanchéité : M. Diaz (Étanch’Ouest)
  - Lot 7 – Sols sportifs : Mme Duclos (Sols & Sports Duclos)

---

### **Points abordés**

#### **1. Avancement des travaux**
- **Lot 2** : Reprise de la dalle de la salle principale terminée. Séchage en cours ; mesure d’humidité prévue le **2 octobre** (responsabilité : M. Lacombe).
- **Lot 4** : Fin de la couverture, infiltration détectée côté nord après la pluie du **24 septembre**. Défaut d’étanchéité en acrotère reconnu par M. Diaz. Reprise à ses frais, à réaliser avant la prochaine réunion du **6 octobre**.
- **Lot 7** : Attente de la dalle sèche (taux d’humidité < 3 %) pour la pose du sol sportif, prévue en **3 semaines**.
- **Lot 9** : Chemins de câbles posés à **60 %** selon M. Paquet. Aucun planning fourni ; retard cumulé estimé à **2 semaines** (séchage + lot 9).

#### **2. Planning et réception**
- **Retard cumulé** : Proposé de reporter la réception initialement prévue le **13 novembre** au **27 novembre 2026** (décision confirmée par la MOA).
  - *Prévention des clubs* : Mme Ferrand s’engage à les informer avant le **16 octobre**.
- **Pénalités de retard** pour le lot 9 : Question ouverte sur leur application ; attente de la réception du planning.

#### **3. Travaux supplémentaires**
- **Portes coupe-feu** (lot 2) :
  - Non conformes aux plans originaux ; devis présenté par M. Lacombe (**3 840 € HT**).
  - **Décision** : Acceptation du devis. Ordre de service à émettre avant le **2 octobre** (responsabilité : MOE).
- **Peinture des murs** (lot 2) :
  - Proposition de M. Lacombe (**~11 000 € HT**).
  - **Statut** : Budget non disponible pour l’instant ; à étudier pour **2027**.

#### **4. Choix techniques**
- **Sol sportif** :
  - Nuanciers proposés par Mme Duclos : **bleu (terrain) / gris clair (hors jeu)** (choix validé par Mme Ferrand).
  - **Tracés** : Basket, hand et badminton tracés. Demande de confirmation pour le volley (à vérifier auprès des clubs).
- **Échantillon** : Mme Duclos apportera un échantillon lors de la prochaine réunion.

#### **5. Lot 9 – Électricité**
- **Absences répétées** : Courrier de mise en demeure à envoyer à Elec Mérignon (responsabilité : M. Hamon, cette semaine).
- **Éclairage LED renforcé** : Demande des clubs pour les compétitions ; à étudier avec le lot 9 (pas de devis demandé pour l’instant).

#### **6. Sécurité**
- **Clôture de chantier** : Déplacée (cause indéterminée). Remise en place aujourd’hui par M. Lacombe.

---

### **Décisions et actions**

| **Action**                                                                 | **Responsable**       | **Échéance**          |
|---------------------------------------------------------------------------|-----------------------|-----------------------|
| Reprise des défauts d’étanchéité (lot 4)                                   | M. Diaz               | Avant le 6 octobre   |
| Émission de l’ordre de service pour les portes coupe-feu                     | MOE (Mme Vernhes)     | Avant le 2 octobre   |
| Prévention des clubs (retard réception)                                    | Mme Ferrand

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Le compte rendu indique le report de la réception « initialement prévue le 13 novembre au 27 novembre 2026 (décision confirmée par la MOA) ».
  - D2 : 1 — Il mentionne « Décision : Acceptation du devis » de M. Lacombe (3 840 € HT) pour les portes coupe-feu, avec l'ordre de service à émettre.
  - D3 : 1 — Il indique « bleu (terrain) / gris clair (hors jeu) (choix validé par Mme Ferrand) ».
  - A1 : 1 — Il mentionne une « mesure d'humidité prévue le 2 octobre (responsabilité : M. Lacombe) ».
  - A2 : 1 — Il indique une reprise à ses frais par M. Diaz « avant la prochaine réunion du 6 octobre ».
  - A3 : 1 — Il indique que « Mme Ferrand s'engage à les informer avant le 16 octobre ».
  - A4 : 1 — Le tableau mentionne « MOE (Mme Vernhes) – Avant le 2 octobre ».
  - A5 : 0.5 — L'action « à vérifier auprès des clubs » est présente, mais sans le responsable connu (Mme Ferrand).
  - A6 : 1 — Il indique que « Mme Duclos apportera un échantillon lors de la prochaine réunion ».
  - A7 : 1 — Il mentionne le courrier de mise en demeure avec « responsabilité : M. Hamon, cette semaine ».
  - A8 : 1 — Il indique « Remise en place aujourd'hui par M. Lacombe ».
- `absence_invention` : 0 — Le compte rendu introduit des éléments absents des notes : « Non conformes aux plans originaux » (les notes disent « pas prévues au marché ») et « pose du sol sportif, prévue en 3 semaines » (les notes indiquent une durée de pose de 3 semaines, pas une date).
- `structure` : 0 — Il n'y a pas de section Décisions distincte : décisions et actions sont fusionnées dans un tableau tronqué (« Mme Ferrand » sans échéance), qui ne reprend pas les décisions.
- Inventions : Portes coupe-feu « non conformes aux plans originaux » (non mentionné dans les notes); Pose du sol sportif « prévue en 3 semaines » (les notes indiquent une durée de pose de 3 semaines)
- Confiance : moyenne

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
- Mme Haddou, Point Écoute Jeunes (invitée ponctuelle)

---

### **Points abordés**

1. **Bilan mi-parcours du CLS**
   - Présentation des 18 fiches-actions : 4 terminées, 11 engagées, 3 non démarrées (dont « santé des aidants » et « habitat indigne »).
   - **Points forts** : ateliers nutrition dans le quartier Les Coudrais (212 participants depuis 2024) et permanences CPAM au CCAS.
   - **Points faibles** : faible avancée sur l’axe santé environnement et manque de données.
   - **Décision** : validation à l’unanimité du bilan par le COPIL. Préparation d’une note de synthèse pour le conseil municipal du **12 novembre 2026** (transmise au cabinet du maire avant le **30 octobre**).

2. **Accès aux soins**
   - **Contexte** : départ en retraite de deux médecins généralistes fin 2026, entraînant une estimation de 2 600 patients sans médecin traitant.
   - **Projets** :
     - Projet de **maison de santé pluriprofessionnelle (MSP)** libérale porté par la CPTS (3 médecins intéressés, mais pas de signature).
     - Proposition municipale d’un **centre de santé municipal** (modèle d’une ville voisine), critiqué pour son coût initial.
   - **Décision** :
     - Lancement d’une **étude d’opportunité comparant les deux scénarios** (coût estimé à 28 000 € TTC).
     - Financement partiel par l’ARS (50 % max. 15 000 € via le FIR), sous réserve de validation du dossier par le comité FIR en décembre.
     - **Montée du dossier FIR** par Mme Benamar avec l’appui de l’ARS, dépôt avant le **13 novembre 2026**.
     - **Pas de choix définitif** entre MSP et centre de santé : attendre les résultats de l’étude.
     - **Contribution hospitalière** : Mme Tran évoque une possible collaboration pour des consultations avancées (cardio, gynécologie), à confirmer avec sa direction.
     - **Campagne M’T dents** : renforcement des interventions en classe dans les écoles du quartier prioritaire, prévues pour **janvier-mars 2027**.

3. **Santé mentale**
   - **Contexte** : hausse des demandes au Point Écoute Jeunes (+35 % en un an) et délais de 4 à 6 mois pour un premier rendez-vous en CMP.
   - **Propositions** :
     - Formation de **12 stagiaires** (agents municipaux, CCAS, animateurs jeunesse, bénévoles) aux **Premiers secours en santé mentale (PSSM)** pour deux sessions en **1er semestre 2027**.
     - **Décision** : validation de ces sessions, financement ARS déjà inclus dans la fiche-action 7.
     - Proposition de création d’un **conseil local de santé mentale (CLSM)**, rejetée pour l’instant en raison de la charge de travail actuelle.
     - Demande de **subvention complémentaire** pour le Point Écoute (+5 000 €), à traiter par la commission des subventions de 2027.

4. **Prévention / nutrition / santé environnement**
   - **Ateliers nutrition** : **reconduction en 2027** avec le même format (1 atelier par mois), financement CPAM confirmé (4 500 €).
   - **Collaboration Éducation nationale** : contact pris avec l’infirmière conseillère technique pour intégrer les infirmières scolaires aux ateliers.
   - **Santé environnement

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « validation à l'unanimité du bilan par le COPIL » est présente.
  - D2 : 1 — L'étude d'opportunité à 28 000 € TTC et le cofinancement ARS « sous réserve de validation du dossier par le comité FIR » sont présents.
  - D3 : 0.5 — Les deux sessions au 1er semestre 2027 sont validées, mais le texte indique « 12 stagiaires » au lieu de 24 et omet le montant de 6 000 €.
  - D4 : 1 — La reconduction en 2027 (1 atelier par mois, financement CPAM de 4 500 €) est présente.
  - D5 : 0 — La sortie est tronquée à « **Santé environnement » : la campagne moustique tigre est absente.
  - D6 : 0 — Le point 5 (avenant n° 1) est absent du fait de la troncature.
  - A1 : 0.5 — La note de synthèse et l'échéance du 30 octobre sont présentes, mais le responsable (Mme Benamar) n'est pas nommé.
  - A2 : 1 — « Montée du dossier FIR par Mme Benamar avec l'appui de l'ARS, dépôt avant le 13 novembre 2026 » est présent.
  - A3 : 0.5 — L'action et l'échéance janvier-mars 2027 sont présentes, mais Mme Ricard n'est pas nommée comme responsable.
  - A4 : 0 — La sollicitation des organismes de formation PSSM par Mme Benamar est absente.
  - A5 : 0.5 — L'action est évoquée sans responsable et présentée à tort comme déjà réalisée (« contact pris »).
  - A6 : 0 — L'action est absente (sortie tronquée).
  - A7 : 0 — L'action est absente (sortie tronquée).
  - A8 : 0 — L'action est absente (sortie tronquée).
  - A9 : 0 — L'action est absente (sortie tronquée).
  - A10 : 0 — L'action est absente (sortie tronquée).
- `absence_invention` : 0 — La sortie contient au moins une invention : « Formation de 12 stagiaires » (24 dans les notes), « contact pris avec l'infirmière conseillère technique » (action non encore faite) et CLSM « rejetée » alors qu'il est simplement non décidé et à remettre à l'ordre du jour.
- `structure` : 0 — Les sections Décisions et Actions sont absentes : les décisions sont intégrées aux points abordés et la sortie est tronquée.
- Inventions : 12 stagiaires (au lieu de 24 personnes sur deux sessions); « contact pris avec l'infirmière conseillère technique » présenté comme fait accompli; CLSM « rejetée pour l'instant » au lieu de « non décidé, à remettre à l'ordre du jour du prochain COPIL »
- Confiance : haute

**Juge second** : juge

- `presence_elements` :
  - D1 : 1 — La décision de validation unanime du bilan mi-parcours est explicitement mentionnée dans la section 'Bilan mi-parcours'.
  - D2 : 1 — L'étude d'opportunité comparant MSP et centre de santé municipal, son coût et le cofinancement ARS sont détaillés dans la section 'Accès aux soins'.
  - D3 : 1 — Les 2 sessions PSSM au 1er semestre 2027, avec 24 personnes et le financement ARS, sont précisées dans la section 'Santé mentale'.
  - D4 : 1 — La reconduction des ateliers nutrition en 2027, avec financement CPAM, est indiquée dans la section 'Prévention / nutrition / santé environnement'.
  - D5 : 1 — La campagne d'information sur le moustique tigre au printemps 2027 est mentionnée dans la section 'Prévention / nutrition / santé environnement'.
  - D6 : 1 — L'accord de principe pour l'avenant n°1 intégrant la fiche-action 'prévention des chutes' est cité dans la section dédiée.
  - A1 : 1 — La note de synthèse pour le conseil municipal du 12 novembre, à transmettre avant le 30 octobre, est explicitement attribuée à Mme Benamar.
  - A2 : 1 — Le montage du dossier FIR par Mme Benamar avec l'ARS, à déposer avant le 13 novembre, est précisé dans la section 'Accès aux soins'.
  - A3 : 1 — L'organisation de M'T dents par Mme Ricard au 2e trimestre 2027 est mentionnée dans la section 'Accès aux soins'.
  - A4 : 1 — La sollicitation d'organismes de formation PSSM par Mme Benamar pour le prochain COPIL est indiquée dans la section 'Santé mentale'.
  - A5 : 0.5 — Le contact avec l'infirmière conseillère technique est mentionné, mais sans échéance fixée (présence partielle).
  - A6 : 1 — La campagne moustique tigre pilotée par M. Ogier pour le COPIL de mars 2027 est détaillée dans la section 'Prévention / nutrition / santé environnement'.
  - A7 : 0.5 — La demande d'état des lieux à M. Ogier est mentionnée, mais sans échéance (présence partielle).
  - A8 : 1 — La rédaction de la fiche-action de l'avenant par M. Vasseur et Mme Benamar avant le 15 janvier 2027 est précisée.
  - A9 : 0.5 — L'envoi du sondage pour le prochain COPIL est mentionné, mais sans échéance précise (présence partielle).
  - A10 : 1 — La diffusion du compte rendu sous 15 jours par Mme Benamar est indiquée dans la section 'Divers'.
- `absence_invention` : 0 — Invention détectée : la 'collaboration hospitalière pour des consultations avancées' est présentée comme décidée, alors qu'elle est seulement évoquée sans engagement (piège référencé).
- `structure` : 1 — Les quatre sections requises (Participants, Points abordés, Décisions, Actions) sont présentes et clairement identifiables.
- Inventions : La collaboration hospitalière pour des consultations avancées (cardio, gynécologie) est présentée comme acquise, alors qu'elle est conditionnelle à une validation ultérieure de la direction de l'hôpital.
- Confiance : haute

## CR-025 (CR, difficile)

### Entrée

```text
{
  "consigne": "Rédige le compte rendu de ce dialogue de gestion : participants, points abordés, décisions, actions (responsable, échéance).",
  "nb_mots": 1899,
  "transcription": "Dialogue de gestion annuel — CPOM 2024-2028 — Département / association Domicile Entraide des Trois Vallées (service autonomie à domicile)\nMardi 29 septembre 2026, 14 h, Hôtel du Département, salle 3\nTranscription de l'enregistrement\n\nMme Massard (directrice de l'autonomie, département) : Bonjour à tous. Merci d'être venus. On est là pour le dialogue de gestion annuel du CPOM, on est dans la troisième année sur cinq. Je fais les présentations pour l'enregistrement : côté département, moi-même, Corinne Massard, directrice de l'autonomie, M. Tavernier, chef du service tarification et contrôle, et Mme Gaudry, chargée de tarification, qui fera le relevé de conclusions. Côté association : M. Peyrac, président, Mme Roux-Delattre, directrice, et M. Kerbrat, responsable administratif et financier.\n\nM. Peyrac (président de l'association) : Bonjour. Je précise tout de suite que je devrai partir vers 15 h 15, j'ai un conseil d'administration de la fédération. Mme Roux-Delattre a ma délégation pour la suite.\n\nMme Massard : Très bien. On a trois sujets : les indicateurs du CPOM, la situation financière et le tarif, et les demandes de l'association. Monsieur Tavernier, les indicateurs.\n\nM. Tavernier (chef du service tarification) : Alors, sur 2025. Heures réalisées : 148 300, pour un objectif CPOM de 155 000. Dont 112 000 heures APA, 21 500 heures PCH, et 14 800 heures pour les caisses de retraite et les mutuelles. Le taux de rotation du personnel d'intervention est de 28 %, l'objectif était sous les 20 %. Le délai moyen de démarrage d'une intervention, on le mesure à 11 jours, pour un objectif de 7. Les heures notifiées non réalisées faute de personnel représentent 6 %. Et vous avez eu 37 réclamations écrites dans l'année, dont 22 sur des changements d'intervenant non prévenus.\n\nMme Roux-Delattre (directrice de l'association) : Je voudrais réagir sur deux points. D'abord le volume d'heures : l'objectif de 155 000 a été fixé en 2023, avant qu'on perde quatorze intervenantes, parties dans les EHPAD et à l'hôpital après les revalorisations. On ne peut pas faire 155 000 heures avec les effectifs qu'on a. On demande que l'objectif soit revu.\n\nMme Massard : On peut l'entendre. À combien ?\n\nMme Roux-Delattre : On propose 145 000.\n\nM. Tavernier : 145 000, ça voudrait dire acter qu'on baisse par rapport à ce que vous avez fait en 2025. Ce n'est pas un bon signal pour les personnes en attente. Sur le premier semestre 2026, vous êtes à 75 200 heures, donc sur un rythme d'environ 150 000.\n\nMme Massard : Je vous propose 150 000 heures par an, pour 2026 et pour 2027. Ça correspond à votre rythme actuel, et on regarde de nouveau à la revue de 2027.\n\nMme Roux-Delattre : [pause] D'accord pour 150 000.\n\nM. Peyrac : D'accord.\n\nMme Massard : C'est acté : objectif ramené à 150 000 heures par an pour 2026 et 2027. Deuxième point, monsieur…\n\nMme Roux-Delattre : Pardon, mon deuxième point, c'était le délai de démarrage. Les 11 jours, ils sont calculés à partir de la date de décision du plan d'aide. Or nous, on reçoit la notification parfois cinq ou six jours après. Le délai réel de notre côté, il est plutôt de 6 jours.\n\nM. Tavernier : C'est exact, la notification part par courrier. On a commencé la notification dématérialisée en juin, mais votre association n'est pas encore raccordée.\n\nMme Massard : Alors on garde l'objectif de 7 jours, mais on le calcule à partir de la réception de la notification par le service. C'est plus juste. Et Mme Gaudry, vous leur envoyez la procédure de raccordement à la notification dématérialisée ?\n\nMme Gaudry (chargée de tarification) : Oui, je l'envoie cette semaine.\n\nM. Kerbrat (responsable administratif et financier) : Et nous, on vous refait le calcul du délai pour le premier semestre 2026 sur cette base. Je peux vous l'envoyer avant la fin octobre.\n\nMme Massard : Très bien. Le taux de rotation maintenant. 28 %, c'est préoccupant.\n\nMme Roux-Delattre : C'est le problème numéro un. On a mis en place le tutorat des nouvelles intervenantes en mars, on a des premiers résultats, mais c'est trop tôt pour le voir dans les chiffres. Et les déplacements, c'est l'enfer. Saint-Fulbert, Les Granges-Hautes, ce sont des communes où une intervenante fait quarante minutes de route pour une heure d'intervention. Justement, on voulait vous demander de nous retirer ces deux communes de notre zone d'intervention.\n\nM. Tavernier : Ah non, ça, ce n'est pas possible. Le CPOM vous engage sur la zone d'intervention, et sur ces deux communes, vous êtes le seul service. Si vous partez, il n'y a plus personne.\n\nMme Massard : Je confirme, on ne peut pas accepter le retrait de Saint-Fulbert et des Granges-Hautes. Vous restez sur ces communes. En revanche, la question du coût des déplacements en zone rurale est légitime. M. Tavernier, vous pourrez étudier une majoration pour les zones les plus éloignées ?\n\nM. Tavernier : Je peux l'étudier, oui, mais je ne promets rien, il faudra voir les marges du budget. Je n'ai pas de date à donner aujourd'hui.\n\nMme Roux-Delattre : On en prend acte.\n\nMme Massard : Et pour suivre de plus près, je souhaite qu'on ait un suivi trimestriel, et pas seulement annuel, de deux indicateurs : le taux de rotation et les heures non réalisées. Vous êtes d'accord ?\n\nMme Roux-Delattre : Oui, on a les données, on peut faire un tableau trimestriel. Le premier pourrait couvrir le quatrième trimestre 2026, je vous l'envoie pour le vendredi 15 janvier 2027.\n\nMme Massard : Parfait. On passe aux finances. Monsieur Kerbrat.\n\nM. Kerbrat : Alors l'exercice 2025 du service se clôt sur un déficit de 94 000 euros… pardon, non, 84 000 euros. 94 000, c'était avant la reprise de la provision pour indemnités de départ en retraite. Le déficit est de 84 000 euros. Il s'explique principalement par les revalorisations salariales de la branche intervenues en 2025, qui ne sont pas couvertes entièrement par le tarif, et par les frais kilométriques.\n\nM. Peyrac : Et donc nous vous demandons la reprise de ce déficit par le département.\n\nM. Tavernier : Sur la reprise du déficit, la réponse est non. Le CPOM prévoit que les résultats sont affectés par l'association, ce n'est pas au département de les couvrir. Vos fonds propres le permettent, d'ailleurs, vous avez environ 310 000 euros de réserves.\n\nM. Peyrac : 310 000, mais si on les consomme, on n'a plus rien en cas de coup dur.\n\nMme Massard : J'entends, mais nous ne reprendrons pas le déficit 2025. Par contre, ce que nous demandons, c'est un plan de retour à l'équilibre. Un vrai plan, chiffré, sur 2027 et 2028.\n\nMme Roux-Delattre : On s'y engage. Pour quand ?\n\nMme Massard : Avant le budget, il faut qu'on l'ait avant le lundi 16 novembre.\n\nMme Roux-Delattre : C'est serré, mais d'accord. M. Kerbrat et moi, on vous l'envoie avant le 16 novembre.\n\nM. Peyrac : Et le tarif 2027 ? Parce que le plan de retour à l'équilibre dépend évidemment du tarif. Aujourd'hui on est à 25,40 euros de l'heure. On a besoin de 27,10 euros pour couvrir nos coûts réels, c'est ce qu'on a écrit dans notre courrier de juillet.\n\nM. Tavernier : Je vais être honnête. Le tarif 2027 sera fixé par arrêté du président du conseil départemental, après le vote du budget primitif en décembre. Je ne peux pas vous donner un chiffre définitif aujourd'hui. Ce que je peux vous dire, c'est que la direction proposera 26,20 euros dans le projet de budget. Mais c'est une proposition, ça dépend du vote de l'assemblée.\n\nM. Peyrac : 26,20, c'est très loin de 27,10.\n\nMme Massard : C'est un effort de plus de 3 % alors que le budget de l'autonomie est très contraint. Je ne peux pas aller au-delà aujourd'hui, et je ne peux même pas vous garantir 26,20.\n\nM. Kerbrat : Est-ce qu'on pourrait envisager de passer à un financement au forfait global, plutôt qu'à l'heure ? D'autres départements expérimentent ça.\n\nM. Tavernier : On connaît ces expérimentations. Mais ce n'est pas dans le CPOM actuel, et le département n'a pas pris de position là-dessus. Je ne veux pas ouvrir ce sujet aujourd'hui.\n\nMme Massard : On ne retient pas ça pour l'instant. On en reparlera peut-être pour le prochain CPOM.\n\nM. Peyrac : Bien. Je vais devoir vous quitter. Mme Roux-Delattre a toute ma confiance pour la suite. Merci, madame la directrice.\n\n[M. Peyrac quitte la réunion à 15 h 15]\n\nMme Massard : Merci, monsieur le président. On continue avec la dotation complémentaire. Monsieur Tavernier.\n\nM. Tavernier : Oui. Pour 2027, nous vous proposons d'intégrer au CPOM, par un avenant n° 2, la dotation complémentaire de 3 euros par heure. Elle est conditionnée à deux objectifs : premièrement, assurer les interventions les dimanches et jours fériés pour toutes les personnes dont le plan d'aide le prévoit ; deuxièmement, mettre en place des actions de lutte contre l'isolement, au moins une visite de convivialité par mois pour les personnes isolées repérées. Si les objectifs ne sont pas atteints, la dotation peut être réduite l'année suivante.\n\nMme Roux-Delattre : Les dimanches, on les assure déjà en grande partie. Pour l'isolement, on a un partenariat avec les bénévoles de l'épicerie sociale de Saint-Fulbert, on peut s'appuyer dessus.\n\nMme Massard : Donc on est d'accord sur le contenu de l'avenant n° 2 ?\n\nMme Roux-Delattre : Sur le contenu, oui. Il faudra que notre conseil d'administration l'approuve, évidemment, mais le président est d'accord sur le principe, on en a parlé.\n\nMme Massard : Bien sûr. De notre côté, l'avenant doit être approuvé par la commission permanente. Je l'inscris à la commission permanente du lundi 7 décembre 2026. M. Tavernier, vous rédigez le projet d'avenant ?\n\nM. Tavernier : Oui, je l'envoie à l'association avant le vendredi 30 octobre, pour qu'elle puisse le passer à son conseil d'administration.\n\nMme Massard : Dernier sujet, vos demandes. Il y avait la question des véhicules.\n\nMme Roux-Delattre : Oui. Une partie de nos intervenantes n'ont pas de voiture, ou une voiture en mauvais état. On voudrait louer en location longue durée six véhicules de service, pour les secteurs ruraux. On demandait au département de prendre en charge la moitié du coût.\n\nM. Tavernier : Six, c'est beaucoup. On a regardé : avec la ligne d'aide à la modernisation des services, on peut cofinancer à 50 %, mais dans la limite de 12 000 euros sur 2027. Ça correspond à peu près à quatre véhicules.\n\nMme Roux-Delattre : Quatre, c'est déjà bien. Les deux autres, on verra plus tard, ou sur nos fonds propres.\n\nMme Massard : Donc le département cofinance à 50 % la location de quatre véhicules de service en 2027, dans la limite de 12 000 euros. Pour les six, ce n'est pas possible. M. Kerbrat, vous nous envoyez les devis ?\n\nM. Kerbrat : Oui, je les joins au plan de retour à l'équilibre, donc avant le 16 novembre.\n\nMme Roux-Delattre : Et une dernière demande, si je peux. Une aide pour la formation des intervenantes à l'accompagnement des personnes atteintes de troubles cognitifs ?\n\nMme Massard : C'est plutôt la conférence des financeurs. Je ne peux pas vous répondre ici. Je vous invite à déposer un dossier à l'appel à projets du printemps, mais je ne m'engage pas sur le résultat.\n\nMme Roux-Delattre : Entendu.\n\nMme Massard : Pour finir : la revue intermédiaire du CPOM aura lieu en mars 2027, la date sera fixée plus tard, Mme Gaudry vous proposera des dates. Et Mme Gaudry vous enverra le relevé de conclusions de cette réunion sous huit jours. Est-ce que vous avez d'autres points ?\n\nMme Roux-Delattre : Non, merci. Juste une précision pour le relevé : nous avons bien compris que le tarif de 26,20 euros n'est pas acquis.\n\nMme Massard : Exactement, ce sera écrit comme ça. Merci à tous, la réunion est terminée. Il est 15 h 50.\n\n[Fin de l'enregistrement]"
}
```

### Références (vues par le Juge)

```text
{
  "participants_reference": [
    "Département : Mme Massard (directrice de l'autonomie, anime la réunion), M. Tavernier (chef du service tarification et contrôle), Mme Gaudry (chargée de tarification, relevé de conclusions)",
    "Association Domicile Entraide des Trois Vallées : M. Peyrac (président), parti à 15 h 15 en donnant délégation à Mme Roux-Delattre ; Mme Roux-Delattre (directrice) ; M. Kerbrat (responsable administratif et financier)"
  ],
  "decisions_reference": [
    {
      "ref": "D1",
      "texte": "Objectif d'activité du CPOM ramené de 155 000 à 150 000 heures par an pour 2026 et 2027"
    },
    {
      "ref": "D2",
      "texte": "Objectif de délai de démarrage des interventions maintenu à 7 jours, désormais calculé à partir de la réception de la notification par le service"
    },
    {
      "ref": "D3",
      "texte": "Refus du retrait de Saint-Fulbert et des Granges-Hautes de la zone d'intervention : l'association reste sur ces deux communes"
    },
    {
      "ref": "D4",
      "texte": "Mise en place d'un suivi trimestriel du taux de rotation et des heures non réalisées"
    },
    {
      "ref": "D5",
      "texte": "Refus par le département de reprendre le déficit 2025 du service (84 000 €)"
    },
    {
      "ref": "D6",
      "texte": "Engagement de l'association à présenter un plan de retour à l'équilibre chiffré sur 2027 et 2028 avant le lundi 16 novembre 2026"
    },
    {
      "ref": "D7",
      "texte": "Accord sur le contenu d'un avenant n° 2 au CPOM intégrant pour 2027 la dotation complémentaire de 3 € par heure, conditionnée à deux objectifs (interventions les dimanches et jours fériés prévues aux plans d'aide ; au moins une visite de convivialité par mois aux personnes isolées repérées), sous réserve de l'approbation par le conseil d'administration de l'association et par la commission permanente du lundi 7 décembre 2026"
    },
    {
      "ref": "D8",
      "texte": "Cofinancement par le département de 50 % de la location longue durée de 4 véhicules de service en 2027, dans la limite de 12 000 €"
    }
  ],
  "actions_reference": [
    {
      "ref": "A1",
      "action": "Envoyer à l'association la procédure de raccordement à la notification dématérialisée",
      "responsable": "Mme Gaudry",
      "echeance": "cette semaine (semaine du 28 septembre 2026)"
    },
    {
      "ref": "A2",
      "action": "Recalculer le délai de démarrage du premier semestre 2026 à partir de la réception des notifications et l'envoyer au département",
      "responsable": "M. Kerbrat",
      "echeance": "avant la fin octobre 2026"
    },
    {
      "ref": "A3",
      "action": "Étudier une majoration tarifaire pour les zones rurales les plus éloignées",
      "responsable": "M. Tavernier",
      "echeance": "non fixée"
    },
    {
      "ref": "A4",
      "action": "Envoyer le premier tableau de suivi trimestriel (4e trimestre 2026)",
      "responsable": "Mme Roux-Delattre",
      "echeance": "vendredi 15 janvier 2027"
    },
    {
      "ref": "A5",
      "action": "Transmettre le plan de retour à l'équilibre chiffré (2027-2028)",
      "responsable": "Mme Roux-Delattre et M. Kerbrat",
      "echeance": "avant le lundi 16 novembre 2026"
    },
    {
      "ref": "A6",
      "action": "Rédiger le projet d'avenant n° 2 et l'envoyer à l'association",
      "responsable": "M. Tavernier",
      "echeance": "avant le vendredi 30 octobre 2026"
    },
    {
      "ref": "A7",
      "action": "Inscrire l'avenant n° 2 à la commission permanente",
      "responsable": "Mme Massard",
      "echeance": "commission permanente du lundi 7 décembre 2026"
    },
    {
      "ref": "A8",
      "action": "Faire approuver l'avenant n° 2 par le conseil d'administration de l'association",
      "responsable": "non précisé (association)",
      "echeance": "non fixée"
    },
    {
      "ref": "A9",
      "action": "Transmettre les devis de location des véhicules, joints au plan de retour à l'équilibre",
      "responsable": "M. Kerbrat",
      "echeance": "avant le lundi 16 novembre 2026"
    },
    {
      "ref": "A10",
      "action": "Proposer des dates pour la revue intermédiaire du CPOM",
      "responsable": "Mme Gaudry",
      "echeance": "non fixée (revue en mars 2027)"
    },
    {
      "ref": "A11",
      "action": "Envoyer le relevé de conclusions de la réunion",
      "responsable": "Mme Gaudry",
      "echeance": "sous huit jours"
    }
  ],
  "pieges": [
    "Tarif horaire 2027 : NON fixé ; 26,20 € n'est qu'une proposition de la direction, sous réserve du vote du budget primitif en décembre (arrêté du président du conseil départemental)",
    "Tarif de 27,10 € demandé par l'association : NON accordé",
    "Objectif de 145 000 heures proposé par l'association : NON retenu (150 000 heures)",
    "Déficit 2025 : 84 000 € et non 94 000 € ; sa reprise par le département est REFUSÉE",
    "Dotation complémentaire de 3 € par heure : conditionnelle (deux objectifs) et avenant non encore approuvé (CA de l'association, commission permanente du 7 décembre)",
    "Véhicules : 4 cofinancés, et non les 6 demandés",
    "Retrait de Saint-Fulbert et des Granges-Hautes : demandé par l'association, REFUSÉ",
    "Majoration pour les zones rurales : seulement à étudier, aucune promesse ni date",
    "Financement au forfait global : évoqué par M. Kerbrat, NON retenu",
    "Aide à la formation aux troubles cognitifs : renvoyée à l'appel à projets de la conférence des financeurs, aucun engagement",
    "M. Peyrac a quitté la réunion à 15 h 15, avant le point sur la dotation complémentaire et les véhicules",
    "Revue intermédiaire du CPOM : mars 2027, aucune date fixée"
  ]
}
```

### Sortie (statut ok)

```text
**Compte rendu de la réunion de dialogue de gestion annuel – CPOM 2024-2028**
*Département / Association Domicile Entraide des Trois Vallées – Service autonomie à domicile*
*Date : 29 septembre 2026, 14 h – 15 h 50*
*Salle : Hôtel du Département, salle 3*

---

### **Participants**
**Représentants du département :**
- Mme Massard, directrice de l’autonomie
- M. Tavernier, chef du service tarification et contrôle
- Mme Gaudry, chargée de tarification

**Représentants de l’association :**
- M. Peyrac, président (présence jusqu’à 15 h 15)
- Mme Roux-Delattre, directrice (délégation pour la suite)
- M. Kerbrat, responsable administratif et financier

---

### **Points abordés**

#### **1. Indicateurs du CPOM (2025 et 2026)**
- **Heures réalisées en 2025** :
  - 148 300 heures (objectif initial : 155 000).
  - Répartition : 112 000 heures APA, 21 500 heures PCH, 14 800 heures pour les caisses de retraite/mutuelles.
- **Taux de rotation du personnel** : 28 % (objectif : < 20 %).
- **Délai moyen de démarrage** : 11 jours (objectif : 7 jours).
- **Heures notifiées non réalisées** : 6 % (faute de personnel).
- **Réclamations écrites** : 37 en 2025, dont 22 pour des changements d’intervenant non prévenus.

**Débat** :
- **Réduction de l’objectif annuel** :
  - Proposition de l’association : 145 000 heures (justifiée par la perte d’intervenantes en 2023).
  - Proposition du département : 150 000 heures pour 2026 et 2027, en lien avec le rythme actuel (75 200 heures sur le premier semestre 2026).
  - **Décision** : Objectif fixé à **150 000 heures/an pour 2026 et 2027**.

- **Délai de démarrage** :
  - Correction proposée : calcul à partir de la réception de la notification dématérialisée (actuellement, le délai est mesuré à partir de la date de décision du plan d’aide).
  - **Décision** : Objectif de 7 jours calculé à partir de la réception de la notification par le service. Mme Gaudry enverra la procédure de raccordement sous une semaine.
  - M. Kerbrat s’engage à recalculer les délais pour le premier semestre 2026 et à transmettre les données avant la fin octobre.

- **Taux de rotation** :
  - Mesures mises en place : tutorat des nouvelles intervenantes (depuis mars 2026).
  - **Suivi** : Suivi trimestriel proposé (premier tableau pour le 4ᵉ trimestre 2026, à envoyer avant le 15 janvier 2027).

- **Retrait de communes** :
  - Demande de l’association : retrait de Saint-Fulbert et des Granges-Hautes (zones rurales avec déplacements longs).
  - **Décision** : Refus du département. Les communes restent incluses dans la zone d’intervention de l’association.

---

#### **2. Situation financière (2025)**
- **Déficit 2025** : 84 000 € (principalement dû aux revalorisations salariales non couvertes et aux frais kilométriques).
- **Demande de l’association** : Reprise du déficit par le département.
- **Position du département** :
  - Rejet de la reprise du déficit 2025 (obligation selon le CPOM de couvrir les résultats via les fonds propres de l’association).
  - **Décision** : Demande d’un **plan de retour à l’équilibre chiffré** pour 2027 et 2028, à transmettre avant le **lundi 16 novembre 2026**.

---

#### **3. Tarif 2027**
- **Tarif

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « Objectif fixé à 150 000 heures/an pour 2026 et 2027 ».
  - D2 : 1 — « Objectif de 7 jours calculé à partir de la réception de la notification par le service ».
  - D3 : 1 — « Refus du département. Les communes restent incluses dans la zone d'intervention ».
  - D4 : 0.5 — « Suivi trimestriel proposé » figure sous le taux de rotation, sans mention des heures non réalisées et présenté comme une simple proposition.
  - D5 : 1 — « Rejet de la reprise du déficit 2025 », avec le montant de 84 000 €.
  - D6 : 1 — Le plan de retour à l'équilibre chiffré 2027-2028 « avant le lundi 16 novembre 2026 » est présent.
  - D7 : 0 — La sortie est tronquée : l'avenant n° 2 et la dotation de 3 €/h ne sont pas abordés.
  - D8 : 0 — Le cofinancement des 4 véhicules est absent (sortie tronquée).
  - A1 : 1 — « Mme Gaudry enverra la procédure de raccordement sous une semaine ».
  - A2 : 1 — « M. Kerbrat s'engage à recalculer les délais… avant la fin octobre ».
  - A3 : 0 — L'étude d'une majoration pour les zones rurales n'est pas mentionnée.
  - A4 : 0.5 — L'échéance du 15 janvier 2027 est donnée, mais la responsable (Mme Roux-Delattre) n'est pas indiquée.
  - A5 : 0.5 — L'échéance du 16 novembre est donnée, mais les responsables (Mme Roux-Delattre et M. Kerbrat) ne sont pas indiqués.
  - A6 : 0 — Absent (sortie tronquée).
  - A7 : 0 — Absent (sortie tronquée).
  - A8 : 0 — Absent (sortie tronquée).
  - A9 : 0 — Absent (sortie tronquée).
  - A10 : 0 — Absent (sortie tronquée).
  - A11 : 0 — Absent (sortie tronquée).
- `absence_invention` : 0 — « justifiée par la perte d'intervenantes en 2023 » attribue à la perte une date non dite (l'objectif a été fixé en 2023, avant la perte) ; « depuis mars 2026 » et « réception de la notification dématérialisée » ajoutent des précisions absentes des notes.
- `structure` : 0 — La sortie est tronquée : seules les sections Participants et Points abordés sont présentes, sans section Décisions ni section Actions.
- Inventions : Perte d'intervenantes datée de 2023 (« justifiée par la perte d'intervenantes en 2023 »); Tutorat « depuis mars 2026 » (année non précisée dans la transcription); Calcul « à partir de la réception de la notification dématérialisée » (la décision porte sur la réception de la notification, sans précision de mode)
- Confiance : moyenne

## CT-007 (CT, difficile)

### Entrée

```text
{
  "consigne": "Rédige la lettre de demande de pièces conforme à l'article L. 114-5 du code des relations entre le public et l'administration fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse du demandeur], [Commune], [Référence du dossier], [Date du courrier], [Adresse, téléphone et courriel du CCAS], [Nom et qualité du signataire].",
  "elements_connus": {
    "accuse_de_reception": "un accusé de réception a déjà été envoyé le 2 octobre 2026",
    "aide_demandee": "aide exceptionnelle au paiement d'une facture d'énergie",
    "date_reception": "30 septembre 2026",
    "delai_pour_fournir": "15 jours à compter de la réception du courrier",
    "demandeur": "M. Julien Petitjean",
    "pieces_manquantes": [
      "copie de la facture d'énergie concernée",
      "justificatifs des ressources du foyer des trois derniers mois"
    ],
    "regime_du_silence": "selon le service, le silence gardé pendant deux mois sur la demande vaut décision de rejet",
    "service": "Centre communal d'action sociale (CCAS)"
  },
  "objet": "Demande d'aide exceptionnelle au paiement d'une facture d'énergie : pièces manquantes",
  "type": "demande de pièces"
}

Options de la demande :
{
  "parametres": {},
  "type_courrier": "demande de pièces"
}
```

### Références (vues par le Juge)

```text
{
  "type_courrier": "demande de pièces",
  "elements_obligatoires": [
    "En-tête du CCAS",
    "Bloc destinataire (M. Julien Petitjean)",
    "Lieu et date",
    "Objet",
    "Référence du dossier (en emplacement)",
    "Formule d'appel « Monsieur, »",
    "Rappel de la réception de la demande le 30 septembre 2026 (aide exceptionnelle au paiement d'une facture d'énergie)",
    "Liste des 2 pièces manquantes, exactement",
    "Délai fixé pour les produire : 15 jours à compter de la réception du courrier",
    "Mention que le délai au terme duquel la demande est réputée rejetée est suspendu pendant le délai imparti pour produire les pièces",
    "Mention que la production des pièces avant l'expiration de ce délai met fin à la suspension",
    "Coordonnées du CCAS (en emplacement)",
    "Formule de politesse",
    "Signature : nom et qualité du signataire (en emplacement)"
  ],
  "champs_a_laisser_en_emplacement": [
    "[Adresse du demandeur]",
    "[Commune]",
    "[Référence du dossier]",
    "[Date du courrier]",
    "[Adresse, téléphone et courriel du CCAS]",
    "[Nom et qualité du signataire]"
  ],
  "valeurs_interdites": [
    "mention d'une décision implicite d'acceptation, ou d'un délai qui ne courrait qu'à la réception des pièces (régime propre à l'acceptation implicite)",
    "toute pièce supplémentaire non demandée",
    "tout montant d'aide ou toute décision annoncés",
    "toute adresse, tout numéro de téléphone ou courriel inventé"
  ]
}
```

### Sortie (statut ok)

```text
**[Ville du demandeur], le [Date du courrier]**

**Objet : Demande d’aide exceptionnelle au paiement d’une facture d’énergie – Pièces manquantes**

Madame, Monsieur,

Par courrier en date du [Date de réception], vous avez reçu ma demande d’aide exceptionnelle au paiement d’une facture d’énergie, en vue de régler [préciser si nécessaire : *une partie ou la totalité de cette facture*].

Pour que votre traitement puisse être engagé conformément à l’article L. 114-5 du code des relations entre le public et l’administration, je vous prie de bien vouloir me transmettre les pièces manquantes ci-dessous :

- **Copie de la facture d’énergie concernée** ;
- **Justificatifs des ressources du foyer des trois derniers mois** (relevés bancaires, avis d’imposition, etc.).

Je vous rappelle que le délai pour vous fournir ces documents est de **15 jours à compter de la réception de ce courrier**. En cas de silence gardé après ce délai, selon les dispositions du service, une décision de rejet sera considérée comme prononcée.

Je reste à votre disposition pour tout complément d’information.

Veuillez agréer, Madame, Monsieur, l’expression de mes salutations distinguées.

**[Nom et qualité du signataire]**
*[Nom du demandeur]*
M. Julien Petitjean

---
**À l’attention du CCAS**
[Adresse, téléphone et courriel du CCAS]

---
*Pièce jointe : Copie de l’accusé de réception du 30 septembre 2026*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Adresse du demandeur]": false,
    "[Adresse, téléphone et courriel du CCAS]": true,
    "[Commune]": false,
    "[Date du courrier]": true,
    "[Nom et qualité du signataire]": true,
    "[Référence du dossier]": false
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Le courrier est rédigé à contre-sens, du demandeur vers le CCAS (« vous avez reçu ma demande », « je vous prie de bien vouloir me transmettre les pièces manquantes »), ce qui rend le registre inadapté ; il manque en outre plusieurs éléments obligatoires : l'en-tête du CCAS, le bloc destinataire M. Julien Petitjean, la [Référence du dossier], la formule d'appel « Monsieur, » (remplacée par « Madame, Monsieur, »), la date de réception du 30 septembre 2026 (remplacée par « [Date de réception] »), ainsi que les mentions de suspension du délai de rejet implicite et de fin de cette suspension à la production des pièces.
- Inventions : Exemples de justificatifs ajoutés : « (relevés bancaires, avis d'imposition, etc.) », non prévus par l'entrée et assimilables à des pièces supplémentaires; « Pièce jointe : Copie de l'accusé de réception du 30 septembre 2026 » : l'accusé de réception date du 2 octobre 2026, et cette pièce jointe n'est pas prévue; « en vue de régler [préciser si nécessaire : une partie ou la totalité de cette facture] » : précision absente de l'entrée; « Par courrier en date du [Date de réception], vous avez reçu ma demande » : inversion de l'expéditeur et du destinataire; Emplacements non prévus par la consigne : « [Ville du demandeur] », « [Date de réception] », « [Nom du demandeur] »; « En cas de silence gardé après ce délai [...] une décision de rejet sera considérée comme prononcée » : rattache à tort le rejet implicite au délai de 15 jours
- Confiance : haute

## CT-009 (CT, facile)

### Entrée

```text
{
  "consigne": "Rédige la convocation à l'entretien de recrutement au format administratif français. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de la candidate], [Commune], [Date du courrier], [Adresse de l'hôtel de ville], [Téléphone et courriel du service des ressources humaines], [Nom et qualité du signataire].",
  "elements_connus": {
    "confirmation": "confirmer sa présence avant le 28 octobre 2026",
    "date_entretien": "mardi 3 novembre 2026",
    "destinataire": "Mme Élodie Garcia",
    "documents_a_apporter": [
      "pièce d'identité",
      "copie des diplômes"
    ],
    "duree": "environ 30 minutes",
    "heure": "14 h 30",
    "jury": "le directeur général des services et la responsable des ressources humaines",
    "lieu": "salle du conseil, hôtel de ville",
    "poste": "agent d'accueil et d'état civil (catégorie C), à temps complet",
    "service": "Service des ressources humaines"
  },
  "objet": "Convocation à un entretien de recrutement",
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
    "En-tête de l'expéditeur (mairie, service des ressources humaines)",
    "Bloc destinataire (Mme Élodie Garcia)",
    "Lieu et date",
    "Objet : convocation à un entretien de recrutement (agent d'accueil et d'état civil)",
    "Formule d'appel « Madame, »",
    "Date et heure : mardi 3 novembre 2026 à 14 h 30",
    "Lieu : salle du conseil, hôtel de ville",
    "Composition du jury : le directeur général des services et la responsable des ressources humaines",
    "Durée : environ 30 minutes",
    "Documents à apporter : pièce d'identité et copie des diplômes",
    "Demande de confirmation de présence avant le 28 octobre 2026 (coordonnées en emplacement)",
    "Formule de politesse",
    "Signature : nom et qualité du signataire (en emplacement)"
  ],
  "champs_a_laisser_en_emplacement": [
    "[Adresse de la candidate]",
    "[Commune]",
    "[Date du courrier]",
    "[Adresse de l'hôtel de ville]",
    "[Téléphone et courriel du service des ressources humaines]",
    "[Nom et qualité du signataire]"
  ],
  "valeurs_interdites": [
    "noms des membres du jury inventés",
    "rémunération ou date de prise de poste inventées",
    "tout document à apporter non demandé",
    "toute adresse, tout numéro de téléphone ou courriel inventé"
  ]
}
```

### Sortie (statut ok)

```text
**[Ville], le [Date du courrier]**

**Mme Élodie Garcia,**

Par la présente, nous vous convions à un **entretien de recrutement** pour le poste d’**agent d’accueil et d’état civil (catégorie C), à temps complet**, au sein du **Service des ressources humaines**.

**Objet : Convocation à un entretien de recrutement**

**Lieu :** Salle du conseil, [Adresse de l'hôtel de ville]
**Date :** Mardi 3 novembre 2026
**Heure :** 14 h 30
**Durée :** Environ 30 minutes

Le jury de cet entretien sera composé du **directeur général des services** et de la **responsable des ressources humaines**.

Pour ce rendez-vous, merci de vous munir de :
- une **pièce d’identité** ;
- une **copie des diplômes** obtenus.

Veuillez confirmer votre présence avant le **28 octobre 2026** par retour de courrier ou par un message au [Téléphone et courriel du service des ressources humaines].

Nous restons à votre disposition pour toute information complémentaire.

Veuillez agréer, Madame, l’expression de nos salutations distinguées.

**[Nom et qualité du signataire]**
*Service des ressources humaines*
[Adresse de l'hôtel de ville]

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Adresse de l'hôtel de ville]": true,
    "[Adresse de la candidate]": false,
    "[Commune]": false,
    "[Date du courrier]": true,
    "[Nom et qualité du signataire]": true,
    "[Téléphone et courriel du service des ressources humaines]": true
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Au moins deux éléments obligatoires manquent : il n'y a pas d'en-tête de l'expéditeur en haut du courrier (la mairie et le service n'apparaissent qu'à la signature), et la formule d'appel « Madame, » est absente, remplacée par « Mme Élodie Garcia, ». S'y ajoutent un bloc destinataire sans [Adresse de la candidate], un lieu noté « [Ville] » au lieu de « [Commune] », et un objet placé après le début du corps, contraire au format administratif.
- Inventions : aucune
- Confiance : haute

## CT-013 (CT, moyen)

### Entrée

```text
{
  "consigne": "Rédige la réponse d'information en t'appuyant sur l'article L. 2121-26 du code général des collectivités territoriales fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de l'association], [Commune], [Date du courrier], [Horaires d'ouverture du secrétariat général], [Téléphone et courriel du secrétariat général], [Nom et qualité du signataire].",
  "elements_connus": {
    "destinataire": "Association « Vivre au village », représentée par sa secrétaire, Mme Sandrine Morel",
    "modalites_locales": "consultation sur place au secrétariat général aux heures d'ouverture, ou envoi d'une copie sur demande écrite",
    "question_posee": "l'association demande si elle peut obtenir les procès-verbaux des séances du conseil municipal de 2025 et le budget primitif 2026, et si elle peut les publier dans sa lettre d'information",
    "service": "Secrétariat général de la mairie"
  },
  "objet": "Communication des procès-verbaux et du budget de la commune",
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
    "En-tête de l'expéditeur (mairie, secrétariat général)",
    "Bloc destinataire (association Vivre au village, à l'attention de Mme Sandrine Morel)",
    "Lieu et date",
    "Objet",
    "Formule d'appel « Madame, »",
    "Rappel de la demande (procès-verbaux des séances de 2025 et budget primitif 2026)",
    "Droit de toute personne physique ou morale de demander communication des délibérations, des procès-verbaux, des budgets et des comptes de la commune et des arrêtés municipaux",
    "Possibilité de publier ces documents sous sa responsabilité",
    "Communication possible auprès du maire comme des services déconcentrés de l'État",
    "Modalités locales : consultation sur place au secrétariat général aux heures d'ouverture, ou copie sur demande écrite",
    "Horaires et coordonnées du secrétariat général (en emplacement)",
    "Formule de politesse",
    "Signature : nom et qualité du signataire (en emplacement)"
  ],
  "champs_a_laisser_en_emplacement": [
    "[Adresse de l'association]",
    "[Commune]",
    "[Date du courrier]",
    "[Horaires d'ouverture du secrétariat général]",
    "[Téléphone et courriel du secrétariat général]",
    "[Nom et qualité du signataire]"
  ],
  "valeurs_interdites": [
    "frais de copie ou tarifs inventés",
    "délai de communication chiffré inventé",
    "refus de communication ou restriction non prévue par l'article",
    "toute adresse, tout numéro de téléphone ou courriel inventé"
  ]
}
```

### Sortie (statut ok)

```text
**[Date du courrier]**

Monsieur,
Madame,

Par courrier en date du [date de la demande], l’Association **« Vivre au village »**, représentée par sa secrétaire, **Mme Sandrine Morel**, nous a sollicité des informations concernant la communication des documents relatifs aux séances du conseil municipal et du budget primitif de la commune.

En application de l’**article L. 2121-26 du code général des collectivités territoriales**, les procès-verbaux des séances du conseil municipal ainsi que le budget primitif de la commune sont publics et peuvent être consultés par tout citoyen, sous réserve des dispositions locales.

Pour répondre à votre demande, vous pouvez :
- **Consulter les documents sur place** au secrétariat général de la mairie, aux **[horaires d'ouverture du secrétariat général]**, situé à **[Adresse de l'association]**, dans la **[Commune]**.
- **Recevoir une copie par courrier** sur simple demande écrite adressée au secrétariat général, dont les coordonnées sont les suivantes :
  **[Téléphone et courriel du secrétariat général]**.

En ce qui concerne la publication de ces documents dans votre lettre d’information, il est précisé que les procès-verbaux et le budget primitif sont des documents publics. Vous pouvez donc les reproduire à condition de respecter leur intégrité et de mentionner leur source.

Je vous prie d’agréer, Madame, l’expression de mes salutations distinguées.

**[Nom et qualité du signataire]**
Secrétaire général de la mairie de **[Commune]**
Secrétariat général

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
    "[Horaires d'ouverture du secrétariat général]": false,
    "[Nom et qualité du signataire]": true,
    "[Téléphone et courriel du secrétariat général]": true
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : il n'y a ni en-tête de l'expéditeur, ni bloc destinataire, ni objet, ni lieu. La formule d'appel « Monsieur, Madame, » remplace « Madame, ». La communication auprès des services déconcentrés de l'État et la publication « sous sa responsabilité » sont absentes, et le rappel de la demande ne précise pas « 2025 » ni « 2026 ».
- Inventions : « sous réserve des dispositions locales » : restriction non prévue par l'article L. 2121-26; « à condition de respecter leur intégrité et de mentionner leur source » : conditions de publication inventées; « peuvent être consultés par tout citoyen » : restriction du droit, que l'article ouvre à toute personne physique ou morale; « Secrétaire général de la mairie » : qualité du signataire inventée alors qu'elle devait rester en emplacement; « [date de la demande] » et « Par courrier en date du » : date et support de la demande non fournis dans l'entrée; « situé à [Adresse de l'association] » : l'adresse de l'association est présentée à tort comme celle du secrétariat général
- Confiance : haute

**Juge second** : juge

- `conformite` : 1 — Un élément obligatoire manque : la formule d'appel correcte est « Madame, » (au singulier), alors que la sortie utilise « Monsieur, Madame, ». De plus, l'en-tête de l'expéditeur (mairie, secrétariat général) est absent.
- Inventions : La mention « [date de la demande] » n'est pas un champ d'emplacement demandé et n'est pas justifiée par l'entrée ou les références.; L'ajout de « Secrétaire général de la mairie de [Commune] » sous la signature est une invention, car ni l'entrée ni les références ne précisent cette qualité ou cette mention.
- Confiance : haute

## LC-001 (LC, facile)

### Entrée

```text
{
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "nb_mots": 165,
  "texte": "Non, vous ne pouvez pas percevoir le RSA si vous êtes étudiant. Toutefois, vous pouvez demander à percevoir le RSA si vous êtes dans l'un des 2 cas suivants :\n- Soit vous êtes jeune actif et vous avez entre 18 et 25 ans. Vous devez avoir exercé une activité professionnelle pendant au moins 2 ans à temps plein (soit au moins 3 214 heures de travail) au cours des 3 ans précédant la date de votre demande.\n- Soit vous êtes parent isolé , c'est-à-dire que vous vivez seul(e) avec un ou plusieurs enfants à charge .\nVous devez également résider en France de manière stable et effective, au moins 9 mois par année civile. Vos ressources ne doivent pas dépasser un plafond qui dépend de la composition de votre foyer.\nUn simulateur vous permet de savoir si vous avez droit au RSA et d'estimer son montant. (À noter: Le montant du RSA sera moins important si vous bénéficiez déjà de l'allocation chômage d'aide au retour à l'emploi (ARE) .)"
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "Un étudiant ne peut pas percevoir le RSA, sauf dans l'un des 2 cas prévus",
    "Cas 1 : jeune actif de 18 à 25 ans ayant exercé une activité professionnelle pendant au moins 2 ans à temps plein (au moins 3 214 heures) au cours des 3 ans précédant la demande",
    "Cas 2 : parent isolé, vivant seul(e) avec un ou plusieurs enfants à charge",
    "Il faut aussi résider en France de manière stable et effective, au moins 9 mois par année civile",
    "Les ressources ne doivent pas dépasser un plafond qui dépend de la composition du foyer",
    "Un simulateur permet de savoir si l'on a droit au RSA et d'estimer son montant",
    "Le montant du RSA est moins important si l'on perçoit déjà l'allocation d'aide au retour à l'emploi (ARE)"
  ],
  "termes_juridiques_a_conserver": [
    "RSA",
    "jeune actif",
    "parent isolé",
    "enfants à charge",
    "allocation chômage d'aide au retour à l'emploi (ARE)"
  ]
}
```

### Sortie (statut ok)

```text
Vous n’avez pas droit au **Revenu de Solidarité Active (RSA)** si vous êtes étudiant.

Cependant, vous pouvez en bénéficier sous deux conditions principales :

1. **Être jeune actif** (entre 18 et 25 ans) et avoir travaillé **au moins 2 ans consécutifs** (soit **au moins 3 214 heures** de travail) **sur les 3 dernières années** avant votre demande.
2. **Être parent isolé**, c’est-à-dire que vous vivez seul(e) avec vos enfants à charge.

Pour que votre demande soit acceptée, vous devez aussi :
- **Vivre en France de manière stable et régulière** pendant au moins **9 mois par an**.
- **Ne pas dépasser un montant maximal de revenus** selon le nombre de personnes dans votre foyer.

Un **simulateur en ligne** vous permet de vérifier si vous avez droit au RSA et d’estimer sa taille. *(Note : Si vous bénéficiez déjà de l’**Allocation Chômage (ARE)**, votre RSA sera réduit.)*

---
**Passage à conserver tel quel** :
*À noter: Le montant du RSA sera moins important si vous bénéficiez déjà de l’allocation chômage d’aide au retour à l’emploi (ARE).*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 0.9059,
  "km_entree": 77.32,
  "km_sortie": 78.2259
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La condition d'activité est modifiée : « au moins 2 ans consécutifs » ajoute une exigence absente du texte et supprime « à temps plein ». De plus, « sous deux conditions principales » laisse croire que les deux cas sont cumulatifs, alors que le texte dit « l'un des 2 cas » ; « par année civile » devient « par an » et « effective » devient « régulière ».
- `termes_juridiques` : 1 — « RSA », « jeune actif », « parent isolé » et « enfants à charge » sont conservés. Dans le corps du texte, « allocation chômage d'aide au retour à l'emploi (ARE) » est réduit à « Allocation Chômage (ARE) », mais le terme exact figure dans le passage reproduit tel quel à la fin.
- `clarte_percue` : 3 — La structure en liste aide la lecture. En revanche, la note sur l'ARE apparaît deux fois, « estimer sa taille » est maladroit et « deux conditions principales » peut induire l'usager en erreur.
- Inventions : « au moins 2 ans consécutifs » : le caractère consécutif n'apparaît pas dans l'entrée; « simulateur en ligne » : le caractère en ligne n'est pas précisé dans l'entrée; « Pour que votre demande soit acceptée » : formulation qui suggère une acceptation, absente de l'entrée
- Confiance : haute

## LC-004 (LC, facile)

### Entrée

```text
{
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "nb_mots": 125,
  "texte": "Le coût de votre pacte varie selon que vous rédigez votre convention de Pacs seul avec votre futur partenaire ou que vous faites appel à un notaire :\nCas Vous rédigez votre convention avec votre futur partenaire: Vous n'avez aucun frais .\nCas Vous faites appel à un notaire: Le coût de la rédaction de votre contrat de Pacs (aussi appelé convention de Pacs ) par un notaire est de 101,41 € TTC . Le coût est le même pour la modification de votre Pacs . Il faut ajouter un droit d'enregistrement d'un montant fixe de 125 € . Des coûts supplémentaires peuvent s'ajouter, notamment des émoluments de formalités (par exemple, copies notariées de la convention, transcription sur les actes d'état civil des partenaires). Ces coûts sont réglementés par le tarif des notaires ."
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "Le coût dépend de la rédaction de la convention : seul avec son futur partenaire ou par un notaire",
    "Convention rédigée par les partenaires eux-mêmes : aucun frais",
    "Rédaction par un notaire : 101,41 € TTC ; même coût pour une modification du Pacs",
    "S'y ajoute un droit d'enregistrement fixe de 125 €",
    "Des coûts supplémentaires peuvent s'ajouter (émoluments de formalités : copies notariées, transcription sur les actes d'état civil des partenaires)",
    "Ces coûts sont réglementés par le tarif des notaires"
  ],
  "termes_juridiques_a_conserver": [
    "Pacs",
    "convention de Pacs",
    "notaire",
    "droit d'enregistrement",
    "émoluments de formalités",
    "actes d'état civil",
    "tarif des notaires"
  ]
}
```

### Sortie (statut ok)

```text
**Coût du Pacs selon votre choix**

Vous pouvez rédiger votre **PACS** (Partage Civil des Couples) vous-même avec votre partenaire, ou faire appel à un **notaire** pour le faire.

### **Si vous rédigez vous-même votre PACS**
→ **Aucun frais** ne sera à votre charge.

### **Si vous faites appel à un notaire**
Le notaire facture :
- **101,41 €** pour rédiger votre contrat de PACS (appelé aussi *convention de PACS*).
- Ce montant reste le même si vous modifiez votre PACS plus tard.

**À ajouter :**
Un **droit d’enregistrement** de **125 €** est obligatoire.

**Autres frais possibles :**
Le notaire peut facturer des **copies de documents** (comme une copie de votre convention de PACS) ou des **frais pour inscrire vos noms sur les actes d’état civil** (exemple : mariage, naissance). Ces coûts sont fixés par le **tarif des notaires**.

---
*Passage à conserver tel quel (termes juridiques obligatoires) :*
→ *"Convention de PACS", "droit d'enregistrement", "tarif des notaires"*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 12.9729,
  "km_entree": 71.12,
  "km_sortie": 84.0929
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie ajoute une information fausse, « PACS (Partage Civil des Couples) », alors que le Pacs est le pacte civil de solidarité. Elle déforme aussi la transcription en « inscrire vos noms sur les actes d'état civil (exemple : mariage, naissance) » et supprime la mention « TTC » ainsi que le caractère « fixe » du droit d'enregistrement.
- `termes_juridiques` : 0 — Le terme « émoluments de formalités » disparaît : il est remplacé à tort par « Autres frais possibles », sans être conservé ni expliqué.
- `clarte_percue` : 3 — La structure en cas est lisible, mais plusieurs éléments peuvent tromper un usager : le faux développement du sigle, les exemples d'actes inexacts et la note finale « Passage à conserver tel quel », qui est un résidu de méta-commentaire.
- Inventions : Développement du sigle PACS en « Partage Civil des Couples »; « inscrire vos noms sur les actes d'état civil (exemple : mariage, naissance) » : l'entrée parle seulement de transcription sur les actes d'état civil des partenaires; « Le notaire peut facturer des copies de documents » : l'entrée mentionne des copies notariées de la convention, dans le cadre des émoluments de formalités
- Confiance : haute

## LC-012 (LC, moyen)

### Entrée

```text
{
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "nb_mots": 375,
  "texte": "Faut-il faire une déclaration en cas de perte ou de vol du livret de famille ?\nNon, il n'est pas obligatoire de faire une déclaration en cas de perte ou de vol du livret de famille. Toutefois, pour limiter les cas de fraude, il est fortement recommandé d'en faire la déclaration en vous rendant au commissariat de police ou à la brigade de gendarmerie. Un récépissé vous sera remis.\nDans la pratique, si vous êtes les parents, pour obtenir un second livret de famille, les documents suivants peuvent vous être demandés :\n- Justificatif de votre identité\n- Justificatif de domicile (titre de propriété, avis d'imposition ou certificat de non-imposition, quittance de loyer, d'assurance du logement, facture de gaz, d'électricité ou de téléphone)\n- Informations concernant les actes du livret à reconstituer (nom, prénoms, date et lieu de naissance de chaque personne + date et lieu du mariage si vous vous êtes mariés).\nSi vous êtes tuteur d'un mineur, vous devrez joindre à votre demande, 2 documents supplémentaires :\n- Décision de justice qui prouve que vous êtes le tuteur\n- Acte de naissance du mineur.\nDans ce cas, le second livret est établi par reconstitution. Le livret est fourni par la mairie qui conserve l'acte de mariage ou, pour les livrets de parents naturels, l'acte de naissance du 1 er enfant et est complété par tous les officiers de l'état civil détenant un acte dont un extrait doit y figurer. Une mention \"second livret\" doit être inscrite sur la première page. En cas de détérioration de votre 1 er livret de famille, celui-ci peut être remplacé. Vous devrez le présenter à la mairie pour en obtenir une reproduction (duplicata). (À savoir: Lorsqu'un livret devenu inutilisable est échangé contre un second, il doit être remis à l'officier pour être détruit. Mais si vous manifestez un attachement à ce document, il pourra vous être laissé après qu'une mention \"annulé\" ait été apposée sur chaque page.)\nLe délai varie en fonction du nombre d'actes à inscrire sur le livret. En général, cela prend quelques semaines. Vous pourrez retirer le second livret sur présentation d'une pièce d'identité auprès de la mairie où vous avez fait votre demande (c'est-à-dire auprès de la mairie du lieu de votre domicile).\nOui, la délivrance d'un second livret de famille est gratuite."
}
```

### Références (vues par le Juge)

```text
{
  "informations_a_conserver": [
    "La déclaration de perte ou de vol du livret de famille n'est pas obligatoire, mais fortement recommandée (commissariat ou gendarmerie) ; un récépissé est remis",
    "Pièces pour les parents : justificatif d'identité, justificatif de domicile, informations sur les actes à reconstituer (nom, prénoms, date et lieu de naissance, date et lieu du mariage)",
    "Pour un tuteur : en plus, la décision de justice qui prouve la tutelle et l'acte de naissance du mineur",
    "Le second livret est établi par reconstitution par la mairie qui conserve l'acte de mariage (ou, pour les livrets de parents naturels, la mairie qui conserve l'acte de naissance du 1er enfant), puis complété par les autres officiers de l'état civil",
    "La mention « second livret » est inscrite en première page",
    "Un livret détérioré peut être remplacé par un duplicata, en le présentant en mairie ; l'ancien est détruit, ou rendu avec la mention « annulé » sur chaque page si on y tient",
    "Délai : en général quelques semaines, selon le nombre d'actes ; retrait en mairie du domicile sur présentation d'une pièce d'identité",
    "La délivrance est gratuite"
  ],
  "termes_juridiques_a_conserver": [
    "livret de famille",
    "récépissé",
    "tuteur",
    "décision de justice",
    "reconstitution",
    "officiers de l'état civil",
    "duplicata"
  ]
}
```

### Sortie (statut ok)

```text
**Que faire en cas de perte ou de vol de votre livret de famille ?**

Vous n’êtes pas obligé de déclarer sa perte ou son vol. Cependant, pour éviter que quelqu’un ne s’en serve de manière frauduleuse, il est **fortement conseillé** de le signaler.

Pour cela, rendez-vous au **commissariat de police** ou à la **brigade de gendarmerie**. Un **reçu** vous sera donné pour preuve.

---

**Comment obtenir un nouveau livret de famille si vous êtes les parents ?**

Pour en obtenir un second, vous devrez fournir ces documents :
- **Une pièce d’identité** (passeport, carte nationale d’identité, etc.).
- **Un justificatif de domicile** (facture récente d’électricité, gaz, téléphone, avis d’imposition, quittance de loyer ou titre de propriété).

Ensuite, vous devrez fournir :
- **Les informations sur les personnes présentes dans votre livret** :
  - Nom, prénom, date et lieu de naissance de chaque enfant.
  - Date et lieu de votre mariage (si vous êtes mariés).

---
**Si vous êtes le tuteur d’un mineur**, vous devrez ajouter à votre dossier :
- **La décision de justice** qui prouve que vous êtes bien le tuteur.
- **L’acte de naissance du mineur**.

Le nouveau livret sera alors **établi par reconstitution**. La mairie le remplira en se basant sur :
- L’acte de mariage (si vous êtes mariés).
- L’acte de naissance du premier enfant (pour les parents naturels).

Une mention **"second livret"** sera apposée sur la première page.

---
**Que faire si votre livret est abîmé ?**
Vous pouvez demander un **duplicata** (une copie) en le présentant à votre mairie. Pour cela, vous devrez le montrer.

⚠️ **À savoir** :
Si votre livret est trop abîmé et devient **inutilisable**, vous pouvez le remplacer par un second. Dans ce cas, vous devrez le remettre à l’officier d’état civil pour qu’il soit **destruit**. Si vous ne voulez pas le détruire, il pourra être **annulé** (avec une mention sur chaque page).

---
**Combien de temps pour obtenir le nouveau livret ?**
Le délai dépend du nombre d’informations à ajouter. En général, cela prend **quelques semaines**.

Vous pourrez le retirer à la mairie où vous avez fait votre demande, **sur présentation d’une pièce d’identité**, en indiquant votre domicile.

---
**Le nouveau livret est-il gratuit ?**
Oui, il est **gratuit** à l’obtention.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 9.6309,
  "km_entree": 66.64,
  "km_sortie": 76.2709
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie modifie et supprime des éléments : elle omet que le livret est complété par tous les officiers de l'état civil détenant un acte (« La mairie le remplira en se basant sur… »), elle remplace « chaque personne » par « chaque enfant », elle remplace la mairie du domicile par « en indiquant votre domicile », elle ne dit pas que le livret annulé est rendu à l'usager, et elle ajoute des informations absentes de l'entrée (« passeport, carte nationale d'identité », « facture récente »).
- `termes_juridiques` : 0 — « récépissé » est remplacé à tort par « reçu », et « officiers de l'état civil » disparaît du passage sur la reconstitution.
- `clarte_percue` : 3 — La structure en questions et en listes aide, mais certains passages restent confus ou maladroits (« Pour cela, vous devrez le montrer », « en indiquant votre domicile », « destruit »).
- Inventions : Exemples de pièce d'identité : « passeport, carte nationale d'identité, etc. »; Précision « facture récente » pour le justificatif de domicile; Informations demandées limitées à « chaque enfant » (l'entrée dit « chaque personne »); « en indiquant votre domicile » au lieu du retrait à la mairie du domicile
- Confiance : haute

**Juge second** : juge

- `fidelite` : 2 — Toutes les informations à conserver sont présentes et exactes, sans ajout ni modification de sens.
- `termes_juridiques` : 1 — Les termes juridiques à conserver sont tous présents, et 'reçu' est utilisé comme synonyme acceptable de 'récépissé' sans erreur.
- `clarte_percue` : 5 — La structure en questions-réponses, les listes à puces et le vocabulaire simple rendent le texte accessible à un usager sans connaissance administrative.
- Inventions : aucune
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

### **Pour les enfants en maternelle et élémentaire (école primaire)**
Les prix de la cantine sont fixés par votre commune. Certaines villes ajustent ces tarifs en fonction de vos revenus et de vos charges (c’est le *quotient familial*). Certaines communes proposent aussi des aides pour réduire le coût de la cantine.

- **Comment faire ?**
  - Contactez votre mairie pour savoir si des aides existent.
  - Vous pouvez aussi demander de l’aide à l’**assistante sociale scolaire** de votre école.

⚠️ **Cas particulier** : Si votre enfant est scolarisé dans une école éloignée et doit rester à la cantine, certaines communes peuvent vous aider. Parlez-en au **directeur d’école** dès le début de l’année.

---

### **Pour les collèges et lycées**
Certains établissements publics (collèges et lycées) proposent un **fonds social** pour aider les familles à payer la cantine.

- **Comment en bénéficier ?**
  - Parlez-en à l’**assistante sociale** de votre établissement ou au secrétariat.
  - Le chef d’établissement décide des règles et vous les explique en début d’année.

Les tarifs de la cantine sont fixés par le **département** pour les collèges et par la **région** pour les lycées. Certaines collectivités (départements ou régions) peuvent aussi ajuster les prix en fonction de vos revenus (quotient familial). Certaines zones proposent des aides supplémentaires.

- **Comment savoir ?**
  - Renseignez-vous auprès de votre **collectivité locale** (département ou région).

---
*Passage à conserver tel quel (termes juridiques obligatoires) :*
- *"Le quotient familial"* (indice calculé pour évaluer vos revenus et charges).
- *"Collectivité"* (terme désignant une institution locale comme une mairie, un département ou une région).

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": -0.5014,
  "km_entree": 65.57,
  "km_sortie": 65.0686
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Une condition est modifiée : « certaines communes peuvent vous aider » remplace « dans certains départements », et « école élémentaire éloignée de votre domicile » devient « école éloignée ». De plus, l'attribution de l'aide par le chef d'établissement devient « décide des règles », et des restrictions sont ajoutées (« Certains établissements publics »).
- `termes_juridiques` : 0 — Le terme « fonds social pour les cantines » est réduit à « fonds social ». La section finale présente à tort « Collectivité » comme un terme juridique obligatoire, alors qu'il ne figure pas dans la liste des termes à conserver.
- `clarte_percue` : 4 — La structure en sections avec des « Comment faire ? » est claire pour un usager, mais la phrase d'ouverture « Vous pouvez aider votre enfant à payer » est confuse et la note finale sur les termes est parasite.
- Inventions : Certains établissements publics (collèges et lycées) proposent un fonds social; certaines communes peuvent vous aider (cas de l'école éloignée, attribué aux départements dans le texte source); selon son âge et votre situation; Le chef d'établissement décide des règles; Le quotient familial : indice calculé pour évaluer vos revenus et charges; Collectivité : institution locale comme une mairie, un département ou une région; Certaines zones proposent des aides supplémentaires
- Confiance : moyenne

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

**Comment ça se passe ensuite ?**
Dans les **10 jours maximum** après votre demande, les services du département (représenté par le **préfet** ou le **président du conseil départemental**) vont étudier votre dossier.
Ils demanderont aussi l’avis du CCAS ou de la mairie (ou du conseil municipal si la mairie a demandé leur avis).

---
**Pour les personnes sans domicile fixe (SDF) :**
Si vous n’avez pas de domicile stable, vous devez choisir un endroit précis pour être en règle avec les services sociaux. Vous pouvez le faire :
- **Soit** auprès d’un **centre communal ou intercommunal d’action sociale** (CCAS ou CIAS).
- **Soit** auprès d’un **organisme agréé** par le département pour ce type de demande.

Le département qui doit vous aider est celui où vous avez choisi votre domicile.

---
*Passage à simplifier :*
**Termes juridiques non simplifiés :**
- *Centre communal ou intercommunal d’action sociale (CCAS ou CIAS)* : service public géré par une commune ou un groupe de communes pour aider les habitants.
- *Représentant de l’État* : le **préfet** (dans les départements) ou le **président du conseil départemental**.
- *Aide juridictionnelle* : aide financière pour payer les frais liés à un procès ou une démarche devant un tribunal.
- *Allocation personnalisée d’autonomie (APA)* : aide financière pour les personnes âgées dépendantes.
- *Prestation de compensation du handicap* : aides financières ou matérielles pour les personnes en situation de handicap.
- *Revenu de solidarité active (RSA)* : aide sociale pour les personnes en difficulté financière.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 19.6158,
  "km_entree": 48.65,
  "km_sortie": 68.2658
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le délai est modifié (« Dans les 10 jours maximum » au lieu de « dans le mois de leur dépôt »), la transmission est confondue avec l'instruction, et plusieurs informations à conserver sont supprimées : la réserve de l'article L. 252-1, les visiteurs-enquêteurs, la liste des droits ouverts par l'élection de domicile, l'organisme compétent pour attribuer une prestation, et le rattachement de l'APA, de la PCH et du RSA au département. Des précisions sont aussi ajoutées (« si votre commune en a un », « agréé par le département »).
- `termes_juridiques` : 0 — « élire domicile » est remplacé par « choisir un endroit précis », « visiteurs-enquêteurs » et « département débiteur » disparaissent, « demandes d'admission » n'est pas repris, et « représentant de l'Etat » est mal expliqué (« le préfet […] ou le président du conseil départemental »).
- `clarte_percue` : 3 — La structure est simple et lisible, mais le glossaire définit des termes absents du corps du texte (aide juridictionnelle, APA, RSA), et la mention « Passage à simplifier » ainsi que l'attribution du préfet au département créent de la confusion.
- Inventions : Dans les 10 jours maximum après votre demande; si votre commune en a un; organisme agréé par le département pour ce type de demande; les services du département (représenté par le préfet ou le président du conseil départemental); Représentant de l'État : le préfet (dans les départements) ou le président du conseil départemental; le CCAS ou la mairie va préparer un dossier complet pour vous (la mairie n'établit pas le dossier dans le texte); pour être en règle avec les services sociaux
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

### **2. Délai standard de paiement**
Pour la plupart des marchés, le délai de paiement est de **30 jours** après la réception de la facture.

---
**⚠️ Terme juridique non simplifié :**
*"délai de paiement"* → Temps imparti pour régler une facture après réception.

---

### **3. Délais exceptionnels pour certains organismes**
Certains établissements publics ont des délais plus longs :
- **50 jours** pour les hôpitaux publics et les services médicaux militaires.
- **60 jours** pour les entreprises publiques (sauf les collectivités locales).

---
**⚠️ Terme juridique non simplifié :**
*"entreprises publiques"* → Sociétés contrôlées par l’État ou des collectivités locales.

---

### **4. Que se passe-t-il en cas de retard ?**
Si le fournisseur ne reçoit pas son paiement à l’échéance :
- **Le retard commence à courir immédiatement** après la date limite.
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
  "gain_km": 8.0036,
  "km_entree": 50.13,
  "km_sortie": 58.1336
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations sont modifiées, supprimées ou ajoutées : le taux (taux BCE majoré de huit points) manque, comme la règle selon laquelle le délai du marché ne peut pas dépasser le délai réglementaire, la condition « créancier qui a rempli ses obligations » et le caractère « de plein droit » ; « sauf les collectivités locales » remplace « établissements publics locaux », « après la réception de la facture » est ajouté, et l'indemnité forfaitaire devient une chose qu'« il peut aussi demander » alors qu'elle est due de plein droit.
- `termes_juridiques` : 0 — « entités adjudicatrices » et « de plein droit » sont absents, « créancier » est remplacé par « fournisseur », et « intérêts moratoires » devient « intérêts de retard » dans le corps du texte ; « indemnité forfaitaire pour frais de recouvrement » est raccourci en « indemnité forfaitaire ».
- `clarte_percue` : 4 — La structure en sections, avec des chiffres mis en évidence et des définitions, se lit facilement, même si les blocs répétés de « termes non simplifiés » alourdissent un peu la lecture.
- Inventions : « après la réception de la facture » (point de départ du délai absent de l'entrée); « sauf les collectivités locales » (l'entrée dit « établissements publics locaux »); « paiement des frais administratifs »; Définition des pouvoirs adjudicateurs comme « organismes publics ou privés » et « entreprises »; Définition des entreprises publiques comme « sociétés contrôlées par l'État ou des collectivités locales »; « Intérêts calculés automatiquement »
- Confiance : haute

## NR-003 (NR, facile)

### Entrée

```text
Un service a reçu 240 demandes en mars ; 15 % d'entre elles étaient incomplètes. Combien de demandes étaient complètes ? Explique ton calcul.
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "204 demandes complètes (15 % de 240 = 36 demandes incomplètes ; 240 − 36 = 204).",
  "criteres": [
    "Résultat final : 204 demandes complètes",
    "Étape intermédiaire juste (36 demandes incomplètes, ou 85 % de 240)",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
Pour calculer le nombre de demandes complètes, voici la démarche :

1. **Nombre total de demandes** : 240
2. **Pourcentage de demandes incomplètes** : 15 %

**Calcul du nombre de demandes incomplètes** :
15 % de 240 = (15/100) × 240 = **36 demandes incomplètes**.

**Calcul du nombre de demandes complètes** :
240 (total) – 36 (incomplètes) = **204 demandes complètes**.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse donne le bon résultat final (« 240 (total) – 36 (incomplètes) = 204 demandes complètes »), l'étape intermédiaire juste (36 demandes incomplètes) et est rédigée en français correct.
- Inventions : aucune
- Confiance : haute

## NR-007 (NR, moyen)

### Entrée

```text
Quelles conditions faut-il remplir pour pouvoir être tiré au sort comme juré d'assises ? Donne la liste complète.
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "Il faut être de nationalité française, être âgé de plus de 23 ans, savoir lire et écrire en français, avoir l'ensemble de ses droits politiques, civils et de famille, et ne se trouver dans aucun cas d'incapacité ou d'incompatibilité.",
  "criteres": [
    "Nationalité française",
    "Être âgé de plus de 23 ans",
    "Savoir lire et écrire en français",
    "Avoir l'ensemble de ses droits politiques, civils et de famille, et n'être dans aucun cas d'incapacité ou d'incompatibilité",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
Pour être tiré au sort comme juré d’assises en France, vous devez remplir les conditions suivantes :

1. **Être français** et avoir la nationalité française.
2. **Avoir au moins 18 ans** et ne pas avoir atteint l’âge de la retraite.
3. **Être inscrit sur les listes électorales** depuis au moins **5 ans** (sauf exceptions comme les Français de l’étranger ou les personnes ayant perdu leur droit de vote).
4. **Ne pas avoir été condamné à une peine de prison ferme** (y compris avec sursis) pour un crime ou un délit puni d’une peine d’au moins **3 mois d’emprisonnement**, sauf si cette condamnation a été annulée ou si vous avez fait l’objet d’une grâce.
5. **Ne pas être atteint d’une incapacité physique ou mentale** rendant impossible l’exercice de vos fonctions de juré.
6. **Ne pas être en situation de conflit d’intérêts** avec l’affaire jugée (par exemple, être lié par un lien de parenté ou de mariage avec une personne impliquée dans le procès).
7. **Ne pas être en service militaire ou civil** en cours (sauf exceptions comme les réservistes).
8. **Ne pas être en situation de travail saisonnier** (sauf exceptions comme les travailleurs agricoles).

Si vous remplissez ces critères, vous pourrez être convoqué pour participer aux jurés d’assises.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse sur plusieurs points : « Avoir au moins 18 ans » contredit la condition d'âge de plus de 23 ans, elle omet la condition « savoir lire et écrire en français » et elle ajoute des conditions non fondées (inscription électorale depuis 5 ans, limite d'âge de la retraite, travail saisonnier, service militaire).
- Inventions : Avoir au moins 18 ans; ne pas avoir atteint l'âge de la retraite; Être inscrit sur les listes électorales depuis au moins 5 ans; Ne pas avoir été condamné à une peine de prison ferme (y compris avec sursis) pour un crime ou un délit puni d'une peine d'au moins 3 mois d'emprisonnement, sauf si cette condamnation a été annulée ou si vous avez fait l'objet d'une grâce; Ne pas être en service militaire ou civil en cours (sauf exceptions comme les réservistes); Ne pas être en situation de travail saisonnier (sauf exceptions comme les travailleurs agricoles); Ne pas être en situation de conflit d'intérêts avec l'affaire jugée, présenté comme condition pour être tiré au sort
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

- **Chloé** travaille le **jeudi** *(si on considère que les contraintes s'appliquent sur les jours travaillés par les trois agents, et que le mercredi est déjà pris par Bruno, il faut étendre la logique à un autre jour. Cependant, comme les trois agents ne travaillent qu'un jour chacun sur trois jours, il faut reformuler la question en incluant un quatrième jour ou en précisant que les contraintes s'appliquent sur un cycle plus long.)*

---
**Correction avec une interprétation plus logique** :
Si on suppose que les trois agents couvrent **trois jours consécutifs** (par exemple, lundi, mardi, mercredi), voici la répartition exacte :

- **Alice** travaille le **mardi**.
  *Justification* : Chloé travaille le lendemain (mercredi), donc Alice ne peut pas travailler le lundi (car Bruno ne travaille pas ce jour-là). Le mercredi est alors réservé à Chloé.

- **Bruno** travaille le **mercredi** *(mais cela contredit Chloé, car elle travaille aussi le mercredi)* → **Erreur dans l'interprétation initiale**.

---
**Réponse finale correcte** :
Avec les contraintes données, il est impossible de satisfaire toutes les conditions en trois jours consécutifs. Voici une solution possible si on étend la période à **quatre jours** (par exemple, lundi à jeudi) :

- **Alice** travaille le **mardi**.
- **Bruno** travaille le **jeudi** *(car il ne travaille pas le lundi)*.
- **Chloé** travaille le **mercredi** *(le lendemain de Alice)*.

*Justification* :
- Alice travaille le mardi.
- Chloé travaille le mercredi (le lendemain de Alice).
- Bruno ne travaille pas le lundi, donc il travaille le jeudi.

---
**Conclusion** :
La répartition la plus logique avec les contraintes données est :
- **Alice** → **Mardi**
- **Bruno** → **Jeudi**
- **Chloé** → **Mercredi**

*(Si les trois agents ne peuvent travailler que sur trois jours consécutifs, la question n’a pas de solution valide avec les contraintes données.)*

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse : elle conclut « Alice → Mardi, Bruno → Jeudi, Chloé → Mercredi » et affirme que « la question n'a pas de solution valide », alors que la solution unique est Alice lundi, Chloé mardi, Bruno mercredi.
- Inventions : Introduction d'un quatrième jour (jeudi) absent de l'énoncé; Affirmation erronée qu'il est impossible de satisfaire les contraintes sur trois jours
- Confiance : haute

## NR-011 (NR, difficile)

### Entrée

```text
Lors d'un procès devant un tribunal administratif, une partie pose une question prioritaire de constitutionnalité (QPC) et les conditions sont réunies. Par quelles juridictions la QPC passe-t-elle avant d'être jugée, dans quels délais chacune doit-elle se prononcer, et la décision finale peut-elle faire l'objet d'un appel ?
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "Le tribunal administratif l'examine immédiatement et la transmet au Conseil d'État, qui l'examine dans un délai de 3 mois et la transmet au Conseil constitutionnel ; celui-ci rend sa décision dans un délai de 3 mois. Il est impossible de faire appel d'une décision du Conseil constitutionnel.",
  "criteres": [
    "Tribunal administratif : examen immédiat, puis transmission au Conseil d'État",
    "Conseil d'État : examen dans un délai de 3 mois, puis transmission au Conseil constitutionnel",
    "Conseil constitutionnel : décision dans un délai de 3 mois",
    "Aucun appel possible contre la décision du Conseil constitutionnel",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
Dans un procès devant un **tribunal administratif**, une **question prioritaire de constitutionnalité (QPC)** suit un parcours spécifique :

1. **Décision initiale par le tribunal administratif** :
   - Le tribunal administratif (ex. : **Tribunal administratif de [ville]**) doit **examiner la QPC dans les 3 mois** suivant sa réception.
   - Il peut :
     - **La rejeter** (si les conditions ne sont pas remplies ou si la question n’est pas pertinente).
     - **La transmettre** au **Conseil constitutionnel** (si elle est recevable).

2. **Examen par le Conseil constitutionnel** :
   - Le Conseil constitutionnel (saisi dans les **15 jours** maximum après réception de la QPC) doit se prononcer dans un **délai de 2 mois** (art. 62 de la Constitution).
   - Il peut :
     - **Confirmer** la constitutionnalité de la norme contestée.
     - **Invalider** la norme (avec ou sans modification).
     - **Refuser de statuer** (si la question est jugée irrecevable ou non pertinente).

3. **Appel possible ?**
   - **Non**, la décision du Conseil constitutionnel est **definitive** et ne peut faire l’objet d’un appel.
   - Seule la décision du tribunal administratif (avant transmission) pourrait, en théorie, être contestée en **recours pour excès de pouvoir** devant le Conseil d’État (mais cela n’intervient pas sur la QPC elle-même).

*Remarque* : Les délais sont stricts et peuvent être suspendus en cas de recours en excès de pouvoir (mais pas d’appel).

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse omet le filtre du Conseil d'État (« La transmettre au Conseil constitutionnel » directement depuis le tribunal administratif), donne des délais erronés (« examiner la QPC dans les 3 mois » pour le TA au lieu d'un examen immédiat, « délai de 2 mois » pour le Conseil constitutionnel au lieu de 3 mois) et contient une faute (« definitive ») ; seul le critère d'absence d'appel est respecté.
- Inventions : Le tribunal administratif doit examiner la QPC dans les 3 mois suivant sa réception; Transmission directe du tribunal administratif au Conseil constitutionnel; Conseil constitutionnel saisi dans les 15 jours maximum; Décision du Conseil constitutionnel dans un délai de 2 mois (art. 62 de la Constitution); Recours pour excès de pouvoir devant le Conseil d'État contre la décision du tribunal administratif sur la QPC; Les délais peuvent être suspendus en cas de recours en excès de pouvoir
- Confiance : haute

## NR-013 (NR, difficile)

### Entrée

```text
Un agent travaille à 80 % de janvier à avril inclus, puis à 100 % de mai à décembre. En comptant chaque mois de la même façon, quel est son taux d'activité moyen sur l'année ? Arrondis au dixième et explique ton calcul.
```

### Références (vues par le Juge)

```text
{
  "sous_type": "question",
  "reponse_reference": "Environ 93,3 % ((4 × 80 + 8 × 100) ÷ 12 = 1 120 ÷ 12 ≈ 93,33).",
  "criteres": [
    "Résultat final : 93,3 % (arrondi au dixième, comme demandé)",
    "Décompte juste : 4 mois à 80 % et 8 mois à 100 %",
    "Moyenne pondérée (et non moyenne simple de 80 et 100)",
    "Réponse en français correct"
  ]
}
```

### Sortie (statut ok)

```text
Pour calculer le taux d'activité moyen annuel de l'agent, voici la méthode suivie :

1. **Taux mensuel** :
   - **Janvier à avril** : 80 % par mois → 4 mois × 80 % = **320 %**
   - **Mai à décembre** : 100 % par mois → 8 mois × 100 % = **800 %**

2. **Somme totale** :
   320 % + 800 % = **1 120 %**

3. **Nombre total de mois** : 12 mois.

4. **Taux moyen annuel** :
   1 120 % ÷ 12 = **93,3 %** (arrondi au dixième).

**Explication** : Le calcul prend en compte la proportion de temps travaillé chaque mois et divise par 12 pour obtenir une moyenne annuelle.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse donne le bon résultat « 1 120 % ÷ 12 = 93,3 % (arrondi au dixième) », avec un décompte juste (4 mois à 80 %, 8 mois à 100 %), une moyenne pondérée et un français correct : tous les critères sont respectés.
- Inventions : aucune
- Confiance : haute

## NR-018 (NR, facile)

### Entrée

```text
Réécris cette phrase en langage simple pour le grand public, en une phrase de 15 mots au plus : « Il est porté à votre connaissance que l'accueil du public sera suspendu le 3 juin en raison de travaux. »
```

### Références (vues par le Juge)

```text
{
  "sous_type": "consigne",
  "reponse_reference": "L'accueil sera fermé le 3 juin à cause de travaux.",
  "criteres": [
    "Une seule phrase de 15 mots au plus",
    "Date conservée : 3 juin",
    "Cause conservée : travaux",
    "Formule « Il est porté à votre connaissance » supprimée",
    "Aucune information ajoutée (horaires, durée, autre lieu)",
    "Orthographe, grammaire et ponctuation correctes"
  ]
}
```

### Sortie (statut ok)

```text
L’accueil sera fermé le 3 juin pour des travaux.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La phrase « L’accueil sera fermé le 3 juin pour des travaux. » compte 9 mots, conserve la date et la cause, supprime la formule administrative, n'ajoute aucune information et ne contient pas de faute : tous les critères sont respectés.
- Inventions : aucune
- Confiance : haute

## Q-001 (Q, facile)

### Entrée

```text
Une usagère me demande qui est l'Anah et à quoi elle sert concrètement pour les particuliers. Que puis-je lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "L'Anah est l'Agence nationale de l'habitat. Elle peut accorder, sous conditions, une aide financière aux particuliers qui réalisent des travaux dans leur logement (rénovation énergétique, adaptation à la perte d'autonomie…). Pour la rénovation énergétique, elle propose notamment MaPrimeRénov', MaPrimeRénov' Copropriété et Loc'Avantages ; elle propose aussi MaPrimeAdapt' pour adapter le logement à la perte d'autonomie, et Ma Prime Logement décent pour sécuriser les logements indignes (insalubres) ou dégradés. La demande se fait en ligne, depuis un compte personnel sur le site de l'Anah ; il est vivement recommandé de contacter d'abord, gratuitement, un conseiller France Rénov'. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Anah = Agence nationale de l'habitat, qui accorde sous conditions une aide financière pour des travaux dans le logement",
    "Rénovation énergétique : MaPrimeRénov', MaPrimeRénov' Copropriété, Loc'Avantages",
    "MaPrimeAdapt' pour adapter le logement à la perte d'autonomie",
    "Ma Prime Logement décent pour les logements indignes (insalubres) ou dégradés",
    "Demande en ligne (compte personnel), contact gratuit recommandé avec un conseiller France Rénov'"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F1328"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Voici les réponses basées sur les passages fournis :

1. **L’Anah est l’Agence Nationale de l’Habitat** :
   - Elle met en œuvre la politique nationale d’amélioration du parc de logements privés existants.
   - Elle accorde des aides financières aux **propriétaires occupants, bailleurs et syndicats de copropriétaires** pour réaliser des **travaux lourds ou d’amélioration de l’habitat**, sous certaines conditions.
   → [1], [2]

2. **Son rôle concret pour les particuliers** :
   - Elle finance des **subventions** pour des travaux (ex. rénovation énergétique, adaptation à la perte d’autonomie).
   - Elle intervient via des **dispositifs opérationnels mis en œuvre par les collectivités locales** pour une partie importante de ses subventions.
   → [1], [2]

3. **Pour les propriétaires bailleurs**, l’Anah ne précise pas explicitement d’autres missions spécifiques dans les passages fournis, mais elle offre des aides pour les travaux dans les logements loués (ex. rénovation).
   → Les passages ne couvrent pas les détails sur les aides spécifiques aux bailleurs autres que les occupants.

**À vérifier** :
- Les aides pour les bailleurs (ex. réduction fiscale ou prime d’intermédiation locative) ne sont pas détaillées dans les passages fournis sur l’Anah elle-même, mais uniquement sur l’intermédiation locative (voir [3], [4]).
- Pour des précisions sur les aides aux bailleurs, consultez directement le site officiel de l’Anah ou le service compétent de votre région.

---
**Pour l’usagère** :
L’Anah aide les particuliers à améliorer leur logement (via des subventions pour des travaux) et soutient les collectivités locales dans cette mission. Pour les bailleurs, les aides spécifiques (comme la prime d’intermédiation locative) ne sont pas détaillées dans les passages fournis.

Sources citées :
- Liste des opérations programmées de l'Anah (en cours et terminées) — https://www.data.gouv.fr/datasets/liste-des-operations-programmees-de-lanah-en-cours-et-terminees
- Liste des communes couvertes par une opération programmée — https://www.data.gouv.fr/datasets/liste-des-communes-couvertes-par-une-operation-programmee
- Convention Anah : qu'apporte l'intermédiation locative au propriétaire ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F34825
- Convention Anah : qu'apporte l'intermédiation locative au propriétaire ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F34825
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Seul le premier élément clé est présent (« L'Anah est l'Agence Nationale de l'Habitat… accorde des aides financières… sous certaines conditions »). MaPrimeRénov' (et ses déclinaisons Copropriété et Loc'Avantages), MaPrimeAdapt', Ma Prime Logement décent, la demande en ligne et le conseiller France Rénov' manquent tous ; la mention « adaptation à la perte d'autonomie » ne nomme pas MaPrimeAdapt'.
- `pertinence_source` : 1 — Les jeux de données sur les opérations programmées et la fiche F34825 sur la convention Anah touchent au rôle de l'Anah et à ses aides, même s'ils sont périphériques au regard de la source attendue F1328.
- Inventions : Elle met en œuvre la politique nationale d'amélioration du parc de logements privés existants; aides financières aux propriétaires occupants, bailleurs et syndicats de copropriétaires pour réaliser des travaux lourds ou d'amélioration de l'habitat; Elle intervient via des dispositifs opérationnels mis en œuvre par les collectivités locales pour une partie importante de ses subventions; soutient les collectivités locales dans cette mission; réduction fiscale ou prime d'intermédiation locative
- Confiance : moyenne

**Juge second** : juge

- `exactitude` : 1 — Un élément clé manque (Ma Prime Logement décent pour les logements indignes) et une imprécision est présente (les dispositifs MaPrimeRénov', MaPrimeRénov' Copropriété et Loc'Avantages ne sont pas explicitement cités).
- `pertinence_source` : 0 — Les sources citées (data.gouv.fr) ne traitent pas directement des aides de l'Anah pour les particuliers, contrairement à la source attendue (service-public.gouv.fr).
- Inventions : L'Anah met en œuvre la politique nationale d’amélioration du parc de logements privés existants (non vérifiable dans les références).; Elle intervient via des dispositifs opérationnels mis en œuvre par les collectivités locales pour une partie importante de ses subventions (non vérifiable dans les références).; Les aides pour les bailleurs (ex. réduction fiscale ou prime d’intermédiation locative) ne sont pas détaillées dans les passages fournis (hors sujet par rapport à la question sur les particuliers).
- Confiance : moyenne

## Q-002 (Q, facile)

### Entrée

```text
Je reçois la fille d'une dame de 82 ans qui va demander l'Apa. Elle veut savoir comment la perte d'autonomie de sa mère sera évaluée et à partir de quel niveau l'Apa peut être accordée. Que lui dire ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "La perte d'autonomie est évaluée avec la grille Aggir. Elle mesure la capacité de la personne à accomplir 10 activités corporelles et mentales (dites discriminantes : se laver, s'habiller, se déplacer, se repérer dans l'espace et le temps…), qui servent à déterminer le Gir, et 7 activités domestiques et sociales (dites illustratives), qui complètent l'information. La personne est classée dans l'un des 6 Gir. Du Gir 1 au Gir 4, elle peut obtenir l'Apa, à domicile ou en établissement. En Gir 5 ou 6, elle ne peut pas obtenir l'Apa, mais elle peut demander une aide ménagère ou une aide financière à sa caisse de retraite. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Évaluation avec la grille Aggir",
    "10 activités corporelles et mentales (discriminantes) déterminent le Gir ; 7 activités domestiques et sociales (illustratives) complètent l'évaluation",
    "Classement dans l'un des 6 Gir",
    "Apa possible du Gir 1 au Gir 4 (à domicile ou en établissement)",
    "Gir 5 et 6 : pas d'Apa, mais aide ménagère ou aide financière de la caisse de retraite"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F1229"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Voici les réponses basées sur les passages fournis :

1. **Évaluation de la perte d'autonomie** :
   La perte d'autonomie de la dame de 82 ans sera évaluée par un professionnel de l'**équipe médico-sociale (EMS)** de son département, à travers la **grille AGGIR**.
   - Ce professionnel se déplace à son domicile pour évaluer son degré de dépendance, en fonction des besoins pour accomplir les actes de la vie courante ou d’un état nécessitant une surveillance constante.
   - La grille AGGIR classe la perte d’autonomie de **Gir 1** (plus forte dépendance) à **Gir 6** (moins dépendante).
   [Citations : [1], [2], [5]]

2. **Niveaux d’éligibilité à l’APA** :
   L’**Allocation personnalisée d’autonomie (APA)** peut être accordée **uniquement si la dame est classée en Gir 1, Gir 2, Gir 3 ou Gir 4**.
   - Si elle est classée en **Gir 5 ou Gir 6**, elle ne pourra pas obtenir l’APA à domicile.
   [Citation : [1], [5]]

3. **À préciser à la fille** :
   - Elle doit vérifier si la dame remplit aussi les **conditions d’âge** (minimum 60 ans) et de **résidence** (résider en France de manière stable et effective depuis au moins un an).
   [Citation : [4]]

**À vérifier** :
- Aucune information ne précise si la dame réside en établissement médico-social ou à domicile pour l’évaluation AGGIR. Cela pourrait influencer la procédure (ex. : évaluation en établissement pour l’APA en établissement).
- Aucune mention des **conditions de résidence** (durée, lieu précis) ou des **dépenses spécifiques** à couvrir (ex. : frais de transport, aides techniques).

**Recommandation** :
Pour confirmer les détails (résidence, évaluation exacte), la fille doit contacter **les services du département** concerné ou consulter la **source officielle** (ex. : site du service public ou mairie de résidence).

Sources citées :
- Allocation personnalisée d'autonomie (Apa) — https://www.service-public.gouv.fr/particuliers/vosdroits/F10009
- Allocation personnalisée d'autonomie (Apa) — https://www.service-public.gouv.fr/particuliers/vosdroits/F10009
- Allocation personnalisée d'autonomie (Apa) — https://www.service-public.gouv.fr/particuliers/vosdroits/F10009
- Allocation personnalisée d'autonomie (Apa) — https://www.service-public.gouv.fr/particuliers/vosdroits/F10009
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Au moins deux éléments clés manquent. La réponse ne mentionne pas les 10 activités discriminantes et les 7 activités illustratives de la grille Aggir. Elle n'indique pas non plus qu'en Gir 5 ou 6 la personne peut demander une aide ménagère ou une aide financière à sa caisse de retraite. Elle limite en outre l'Apa au domicile (« elle ne pourra pas obtenir l'APA à domicile ») sans préciser que l'Apa est possible à domicile ou en établissement. Elle ajoute une condition non vérifiable (« depuis au moins un an ») et se contredit en affirmant qu'il n'y a « aucune mention des conditions de résidence ». La mention « Ne vaut pas avis juridique » est absente.
- `pertinence_source` : 1 — La source citée, service-public.gouv.fr F10009 (Apa à domicile), traite bien de l'évaluation Aggir et des Gir ouvrant droit à l'Apa, même si ce n'est pas la fiche attendue F1229.
- Inventions : Condition de résidence en France « de manière stable et effective depuis au moins un an »; Évaluation réalisée par un professionnel de l'équipe médico-sociale (EMS) du département qui se déplace au domicile (non vérifiable dans les références); Condition d'âge minimum de 60 ans (non présente dans les références)
- Confiance : haute

## Q-004 (Q, facile)

### Entrée

```text
Une personne qui perçoit l'allocation aux adultes handicapés (AAH) me demande si elle peut aussi toucher le RSA. Que lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Oui, le RSA et l'AAH peuvent se cumuler si elle remplit les conditions requises, mais elle ne percevra pas le RSA en intégralité : le montant du RSA est réduit du montant de l'AAH qu'elle perçoit. Il peut être plus avantageux de conserver la seule AAH si son montant est plus élevé que celui du RSA. Un simulateur permet d'estimer ses droits. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Oui, cumul possible si les conditions requises sont remplies",
    "Le RSA n'est pas versé en intégralité : il est réduit du montant de l'AAH perçue",
    "Il peut être plus avantageux de conserver la seule AAH si elle est plus élevée que le RSA"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F20209"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
D'après les passages fournis, voici ce que vous pouvez lui indiquer :

**Oui, elle peut théoriquement cumuler l'AAH et le RSA**, mais sous conditions :
- Le montant du RSA sera réduit du montant de l'AAH perçue.
- Elle ne percevra pas le RSA dans son intégralité, mais seulement la différence entre le montant maximal du RSA et celui de l'AAH.
- Il peut être plus avantageux pour elle de conserver uniquement l'AAH si son montant est supérieur à celui du RSA.

[1]

**À vérifier** :
- Les montants exacts du RSA et de l'AAH en vigueur (les passages ne précisent pas les montants actuels).
- Les éventuelles exceptions ou cas particuliers (comme les situations spécifiques liées à Mayotte ou aux territoires d'outre-mer, bien que non précisés ici).

Pour une réponse précise sur les montants, consultez le site officiel du **Service Public** ou contactez la **CAF (Caisse d’Allocations Familiales)** ou la **MDPH (Maison Départementale des Personnes Handicapées)** pour une estimation personnalisée.

[1]

Sources citées :
- Peut-on cumuler l'allocation adulte handicapé (AAH) et le RSA ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F20209
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 2 — Les trois éléments clés sont présents et justes : cumul possible (« Oui, elle peut théoriquement cumuler l'AAH et le RSA »), RSA réduit du montant de l'AAH et non versé en intégralité, et intérêt possible à conserver la seule AAH si elle est supérieure au RSA ; aucune contradiction avec la référence.
- `pertinence_source` : 1 — La source citée, service-public.gouv.fr F20209 (« Peut-on cumuler l'AAH et le RSA ? »), correspond exactement à la source attendue et traite directement du point demandé.
- Inventions : « seulement la différence entre le montant maximal du RSA et celui de l'AAH » : précision de calcul absente de la référence; Orientation vers la MDPH « pour une estimation personnalisée » des montants : non vérifiable dans les références
- Confiance : haute

## Q-009 (Q, moyen)

### Entrée

```text
Une femme de 63 ans, en situation de handicap depuis l'âge de 50 ans et qui ne travaille plus, me demande si elle peut encore demander la prestation de compensation du handicap (PCH), si ses revenus comptent et où déposer sa demande. Que lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "En principe, la PCH doit être demandée avant 60 ans, mais elle peut l'être au-delà, sans limite d'âge, si la personne remplissait déjà les conditions d'attribution avant 60 ans (ou si elle continue à travailler) : c'est donc possible si son handicap répondait déjà aux critères avant ses 60 ans. Il faut rencontrer une difficulté absolue pour au moins une activité importante du quotidien, ou une difficulté grave pour au moins deux, de façon définitive ou pour une durée prévisible d'au moins 1 an. La PCH est attribuée sans condition de ressources, mais les ressources fixent le taux de prise en charge : 100 % si les ressources annuelles (revenu fiscal de référence) sont inférieures ou égales à 31 162,62 €, 80 % au-delà. La demande se fait auprès de la MDPH du lieu de résidence, en ligne si elle propose un téléservice, ou par formulaire ; la CDAPH répond dans un délai de 4 mois, et son silence au-delà vaut rejet. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Après 60 ans : demande possible si elle remplissait déjà les conditions d'attribution avant 60 ans (ou si elle travaille encore)",
    "Difficulté absolue pour 1 activité importante du quotidien, ou grave pour au moins 2, définitive ou d'au moins 1 an",
    "Sans condition de ressources, mais prise en charge à 100 % si ressources annuelles ≤ 31 162,62 €, 80 % au-delà (RFR)",
    "Demande à la MDPH du lieu de résidence (téléservice ou formulaire)",
    "Décision de la CDAPH sous 4 mois ; absence de réponse au-delà = rejet implicite"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F14202"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Voici les réponses basées sur les passages fournis :

1. **Conditions d’attribution de la PCH** :
   - La femme de 63 ans **peut demander la PCH** car elle a déjà rempli les conditions avant ses 60 ans et ne travaille plus [1].
   - Aucune limite d’âge supérieure à 60 ans n’est explicitement exclue dans les passages fournis, mais elle doit prouver sa perte d’autonomie et son handicap depuis au moins 50 ans (ce point n’est pas vérifié ici).

2. **Prise en compte des revenus** :
   - Les ressources (revenu fiscal de référence) sont prises en compte pour déterminer le taux de prise en charge des dépenses, mais **la PCH est attribuée sans condition de ressources** [4]. Cependant, les dépenses sont compensées à 100 % si ses ressources annuelles sont inférieures ou égales à 31 162,62 € (ce montant n’est pas applicable ici, car il s’agit d’une simulation).

3. **Où déposer la demande** :
   - La demande peut être faite en ligne (si la MDPH de son lieu de résidence le permet) ou par courrier avec un formulaire officiel, à envoyer à la **MDPH de son lieu de résidence** [2].

---
**À vérifier** :
- Confirmation de sa perte d’autonomie et de son handicap depuis au moins 50 ans (non précisé dans les passages).
- Vérification de ses ressources réelles (pas de montant exact fourni dans les passages).

**Pour les détails sur la procédure d’examen ou de recours**, consultez directement la **MDPH** ou le site officiel de la [MDPH](https://www.service-public.fr/particuliers/vosdroits/F14202) (lien fourni dans les passages).

Sources citées :
- Prestation de compensation du handicap (PCH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F14202
- Prestation de compensation du handicap (PCH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F14202
- Prestation de compensation du handicap (PCH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F14202
```

### Contrôles automatiques

```text
{
  "urls_inventees": [
    "https://www.service-public.fr/particuliers/vosdroits/F14202"
  ]
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Plusieurs éléments clés manquent : les critères de difficulté absolue ou grave, durée d'au moins 1 an, le taux de 80 % au-delà du plafond et le délai de 4 mois de la CDAPH avec rejet implicite ; s'y ajoutent des erreurs, notamment « elle a déjà rempli les conditions avant ses 60 ans » présenté comme acquis au lieu d'une condition, « handicap depuis au moins 50 ans » (confusion avec l'âge) et « ce montant n'est pas applicable ici, car il s'agit d'une simulation ».
- `pertinence_source` : 1 — La source citée, service-public.gouv.fr F14202, porte bien sur la PCH et correspond à la source attendue.
- Inventions : « ce montant n'est pas applicable ici, car il s'agit d'une simulation »; « elle doit prouver sa perte d'autonomie et son handicap depuis au moins 50 ans »; Lien https://www.service-public.fr/particuliers/vosdroits/F14202 présenté comme « site officiel de la MDPH » (domaine différent de la source attendue)
- Confiance : haute

## Q-017 (Q, difficile)

### Entrée

```text
Une locataire d'un appartement du parc privé, 66 ans, classée en Gir 4 après une hospitalisation, vit seule hors Île-de-France avec un revenu fiscal de référence de 20 000 €. Elle veut remplacer sa baignoire par une douche (devis de 10 000 € HT). Peut-elle bénéficier de MaPrimeAdapt', à quel taux, et quelles démarches doit-elle faire ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Oui, sous conditions. Comme locataire du parc privé, elle doit d'abord obtenir l'accord de son bailleur pour ces travaux d'adaptation. Âgée de 60 à 69 ans et classée en Gir, elle remplit la condition liée à l'âge et à la perte d'autonomie. Hors Île-de-France, pour une personne seule, son revenu fiscal de référence de 20 000 € dépasse le plafond des ressources très modestes (17 363 €) mais reste sous celui des ressources modestes (22 259 €) : elle relève de la catégorie « modestes », soit une prise en charge de 50 % des travaux dans la limite de 22 000 € HT, ici 5 000 €. Elle dépose sa demande en ligne sur le site monprojetanah (pour un locataire, par l'entrée « Je suis propriétaire occupant »), accompagnée par un assistant à maîtrise d'ouvrage (AMO) agréé ; elle doit attendre l'accord de l'Anah avant de commencer les travaux, puis transmettre les factures pour obtenir le versement. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Locataire du parc privé : accord du bailleur nécessaire",
    "60 à 69 ans et classée en Gir : condition d'âge et de perte d'autonomie remplie",
    "RFR de 20 000 € pour 1 personne hors Île-de-France : au-dessus de 17 363 € (très modestes), sous 22 259 € (modestes) : ménage modeste",
    "Prise en charge de 50 % dans la limite de 22 000 € HT, soit 5 000 € pour 10 000 € HT",
    "Demande en ligne sur monprojetanah (entrée « Je suis propriétaire occupant ») et accord de l'Anah à attendre avant les travaux"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F37501"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
D'après les passages fournis, voici les réponses à votre question :

### **Conditions de éligibilité**
- **Statut** : Oui, elle peut bénéficier de MaPrimeAdapt’ car elle est **locataire d’un appartement du parc privé** [5].
- **Âge et situation** : Elle a **60 à 69 ans** et est classée en **GIR 4** (groupe iso-ressources), ce qui remplit une condition pour bénéficier de l’aide [5].
- **Revenus** : Son **revenu fiscal de référence (RFR) de 20 000 €** est inférieur au plafond des **ressources modestes hors Île-de-France** pour un ménage de 1 personne (jusqu’à **22 259 €**) [1]. Elle est donc éligible sous cette condition.

### **Taux d’aide**
- Comme son ménage est considéré comme **modeste** (car son RFR est proche du seuil), elle bénéficiera d’une prise en charge de **50 % des travaux**, dans la limite d’un plafond de **22 000 € HT** [3].

### **Montant estimé de l’aide**
- **Travaux estimés (10 000 € HT)** × 50 % = **5 000 € HT** (montant de l’aide).

### **Démarches à effectuer**
- Elle doit **déposer sa demande en ligne sur le site [monprojetanah](https://www.service-public.gouv.fr/)** (accès depuis l’option *"Je suis locataire"*).
- Elle doit s’assurer que son **bailleur a donné son accord** pour les travaux [5].
- Elle devra fournir les justificatifs de son **GIR 4** et de son **revenu fiscal de référence** (avis d’imposition de l’année précédente).

---
**À vérifier** :
- Aucune mention dans les passages ne précise si le devis doit être **obligatoirement certifié** ou si des travaux spécifiques (comme la douche) sont exclus. Vérifiez auprès de la mairie ou du service local compétent pour confirmer l’éligibilité exacte du projet.

Si des questions supplémentaires sur les démarches locales persistent, consultez votre mairie ou le site officiel de **France Rénov’**.

Sources citées :
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
```

### Contrôles automatiques

```text
{
  "urls_inventees": [
    "https://www.service-public.gouv.fr/"
  ]
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse contient une erreur factuelle : elle indique une demande « accès depuis l'option "Je suis locataire" », alors que la référence prévoit l'entrée « Je suis propriétaire occupant ». Elle omet aussi l'accord de l'Anah à attendre avant les travaux et ne situe pas le RFR au-dessus du plafond très modestes de 17 363 €, se contentant de « car son RFR est proche du seuil ».
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F37501) traite bien de MaPrimeAdapt' et des conditions demandées.
- Inventions : Accès à la demande depuis l'option « Je suis locataire » (la référence indique « Je suis propriétaire occupant »); Lien « monprojetanah » pointant vers https://www.service-public.gouv.fr/ au lieu du site monprojetanah; Justification du statut modeste par un RFR « proche du seuil »; Obligation de fournir les justificatifs du GIR 4 et l'avis d'imposition de l'année précédente (non vérifiable dans les références); Orientation vers la mairie pour confirmer l'éligibilité du projet (non vérifiable dans les références)
- Confiance : haute

## Q-024 (Q, moyen)

### Entrée

```text
Un usager divorcé, qui habite désormais notre commune, veut faire inscrire son divorce sur le livret de famille. Le mariage a été célébré en France, dans une autre commune, et c'est son ex-épouse qui a gardé le livret original. Que dois-je lui indiquer ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "La mention du divorce apparaît sur le livret de famille avec l'extrait d'acte de mariage. La mise à jour se fait en mairie : l'officier de l'état civil remplit le livret, le date, le signe et y appose le tampon de la mairie. Pour un mariage célébré en France, il doit se rendre à la mairie où le mariage a été célébré, avec sa carte d'identité et le jugement de divorce. Comme il habite ailleurs, il peut demander à la mairie de sa résidence de transmettre la demande à la mairie compétente, mais toutes les mairies n'acceptent pas de servir d'intermédiaire. Enfin, en cas de divorce, un second livret peut être remis à celui qui ne possède pas le livret original. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Mise à jour en mairie : l'officier de l'état civil remplit le livret, le date, le signe et y appose le tampon",
    "Mariage célébré en France : se rendre à la mairie où le mariage a été célébré, avec sa carte d'identité et le jugement de divorce",
    "Possibilité de demander à la mairie de résidence de transmettre la demande, mais toutes les mairies n'acceptent pas de servir d'intermédiaire",
    "Un second livret peut être remis à celui qui ne possède pas le livret original"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F18910"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
D'après les passages fournis, voici les informations à transmettre à l’usager :

1. **Mise à jour du divorce sur le livret de famille** :
   - Il doit se rendre à la mairie de sa commune actuelle de résidence pour faire inscrire son divorce.
   - Il devra fournir son **extrait d’acte de mariage** (pour confirmer le divorce) et sa **carte d’identité**.
   - Le passage [1] précise que la mention du divorce apparaît sur le livret avec l’extrait d’acte de mariage [1].

2. **À vérifier** :
   - Le passage [2] indique que le divorce est déjà mentionné sur le livret avec l’extrait d’acte de mariage, mais il ne précise pas si l’usager doit faire une démarche supplémentaire pour ajouter cette mention à son propre livret (il semble que ce soit déjà inclus dans le livret de son ex-épouse).
   - Si le livret de l’ex-épouse ne peut pas être modifié pour ajouter le divorce, il devra obtenir un **second livret** (voir ci-dessous).

3. **Demande d’un second livret de famille** (si nécessaire) :
   - Si l’usager souhaite un **second livret** (par exemple, pour des démarches administratives), il devra s’adresser à la mairie de sa commune actuelle de résidence [4].
   - À Paris, il devra remplir un formulaire spécifique et l’adresser à sa mairie [4].

**Recommandation** :
- Vérifiez avec la mairie de sa commune actuelle si le divorce peut être inscrit directement sur le livret de l’ex-épouse ou s’il doit obtenir un second livret.
- Si le divorce n’est pas encore inscrit sur le livret de l’ex-épouse, il devra faire une demande de mise à jour auprès de la mairie de sa commune actuelle.

Pour plus de précisions, consultez la mairie de sa commune actuelle ou le site officiel [Service Public](https://www.service-public.gouv.fr).

Sources citées :
- Mise à jour du livret de famille à la suite d'un changement d'état civil (naissance, divorce, etc.) — https://www.service-public.gouv.fr/particuliers/vosdroits/F18910
- Mise à jour du livret de famille à la suite d'un changement d'état civil (naissance, divorce, etc.) — https://www.service-public.gouv.fr/particuliers/vosdroits/F18910
- Demande d'un second livret de famille en cas de divorce ou de séparation — https://www.service-public.gouv.fr/particuliers/vosdroits/F11996
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

- `exactitude` : 0 — La réponse contredit la source en indiquant « Il doit se rendre à la mairie de sa commune actuelle de résidence pour faire inscrire son divorce » alors que la mairie compétente est celle du lieu de mariage ; elle demande l'extrait d'acte de mariage au lieu du jugement de divorce et omet le rôle de l'officier (remplir, dater, signer, tamponner) ainsi que la réserve sur les mairies intermédiaires.
- `pertinence_source` : 1 — La fiche F18910 citée traite bien de la mise à jour du livret de famille après un divorce, et la F11996 du second livret.
- Inventions : Se rendre à la mairie de sa commune actuelle de résidence pour faire inscrire son divorce; Fournir l'extrait d'acte de mariage (pour confirmer le divorce) comme pièce justificative; À Paris, il devra remplir un formulaire spécifique et l'adresser à sa mairie; Le second livret doit être demandé à la mairie de sa commune actuelle de résidence
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
   Les passages ne mentionnent **pas** explicitement si le mariage à titre posthume est possible en France. Ils ne traitent pas des aspects juridiques spécifiques du mariage après un décès.
   → **À vérifier** auprès du **service juridique des tribunaux civils** ou du **ministère de la Justice** pour une réponse précise.

2. **Démarches à engager pour les obsèques** :
   Les proches doivent décider du devenir des cendres selon les options suivantes :
   - **Cimetière ou site cinéraire** [1]
   - **Dispersion en pleine nature** [1]
   - **Inhumation de l'urne dans une propriété privée** [1]

   Aucune mention n'est faite sur la possibilité de célébrer un mariage posthume, mais les obsèques restent à organiser selon les choix indiqués.

---
**Recommandation** :
L’usagère doit consulter :
- **Le site officiel du ministère de la Justice** ([lien non fourni, mais à rechercher sur *service-public.fr* ou *legifrance.gouv.fr*]) pour les règles sur le mariage posthume.
- **Un notaire** pour valider les démarches administratives liées à la succession et au mariage (si applicable).

Sources citées :
- Un proche est décédé — https://www.service-public.gouv.fr/particuliers/vosdroits/F16507
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie dit bien que les passages ne traitent pas du mariage posthume, mais elle invente une autorité compétente (« service juridique des tribunaux civils », « ministère de la Justice » pour les règles sur le mariage posthume). Elle omet l'orientation vers l'état civil de la mairie, ajoute des informations hors sujet sur le devenir des cendres et ne comporte pas la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 0 — La seule source citée, la fiche F16507 « Un proche est décédé », traite des démarches après un décès et non du mariage posthume, qui est le point demandé.
- `cas_sans_reponse` : 1 — L'Assistant déclare que les passages « ne mentionnent pas explicitement si le mariage à titre posthume est possible », n'invente pas de procédure de mariage et oriente notamment vers un notaire, ce qui est conforme en substance à l'orientation attendue, même si l'orientation est imparfaite (pas de mairie, autorités inventées).
- Inventions : Orientation vers le « service juridique des tribunaux civils », autorité non vérifiable dans l'entrée ou les références; Présentation du « ministère de la Justice » comme source des règles sur le mariage posthume, non vérifiable; Rôle du notaire pour « valider les démarches administratives liées […] au mariage » posthume, non sourcé; Options sur le devenir des cendres attribuées à [1], non vérifiables dans les références et hors sujet
- Confiance : moyenne

**Juge second** : non-juge (limite-debit)

## Q-034 (Q, facile)

### Entrée

```text
Une collègue du service RH de notre collectivité me demande comment la journée de solidarité s'applique aux agents territoriaux : en quoi elle consiste, comment elle peut être accomplie et qui en fixe les modalités. Que dois-je lui répondre ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Dans la fonction publique, la journée de solidarité finance des actions en faveur de l'autonomie des personnes âgées ou handicapées et s'applique aux fonctionnaires comme aux contractuels. Elle prend la forme d'une journée supplémentaire de travail de 7 heures non rémunérée ; pour les agents à temps partiel ou à temps non complet, ces 7 heures sont réduites en proportion de leur durée de travail. Hors Alsace-Moselle, elle peut être accomplie en travaillant un jour férié précédemment chômé autre que le 1er mai (par exemple le lundi de Pentecôte), en supprimant une journée de RTT, ou par toute autre organisation permettant de travailler 7 heures précédemment non travaillées, sauf la suppression d'un jour de congé annuel. Dans la fonction publique territoriale, ces conditions sont fixées par délibération, après avis du comité social territorial. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Journée supplémentaire de travail de 7 heures non rémunérée, applicable aux fonctionnaires et aux contractuels",
    "Les 7 heures sont réduites en proportion pour les agents à temps partiel ou à temps non complet",
    "Modalités (cas général) : travail d'un jour férié précédemment chômé autre que le 1er mai, suppression d'une journée de RTT, ou autre organisation de 7 heures, sauf suppression d'un jour de congé annuel",
    "Dans la FPT, conditions fixées par délibération après avis du comité social territorial"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F2859"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Voici les réponses basées sur les passages fournis, adaptées à la **fonction publique territoriale** (votre collectivité) :

1. **En quoi consiste la journée de solidarité ?**
   Elle consiste en **7 heures de travail non rémunérées** par an, destinées à financer des actions en faveur de l’autonomie des personnes âgées ou handicapées.
   [1]

2. **Comment peut-elle être accomplie ?**
   Dans la fonction publique territoriale, elle peut être réalisée selon l’une des modalités suivantes :
   - **Travail sur un jour férié précédemment chômé** (hors 1er mai),
   - **Suppression d’une journée de RTT**,
   - **Autre organisation** (ex. : travail d’un samedi non habituel), **sauf suppression d’un jour de congé annuel**.
   [1]

3. **Qui fixe les modalités ?**
   Les conditions d’accomplissement sont fixées par **délibération** après avis du **comité social territorial**.
   [1]

---
**À vérifier** :
- Aucune précision sur les jours fériés spécifiques à votre collectivité (ex. : ponts locaux) ou les accords sectoriels.
- Les modalités peuvent varier selon les accords d’entreprise ou les conventions collectives applicables à votre territoire.

**Recommandation** :
Vérifiez auprès du **comité social territorial** ou de la **direction des ressources humaines** de votre collectivité pour confirmer les éventuelles adaptations locales.

Sources citées :
- Comment la journée de solidarité est-elle accomplie dans la fonction publique ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F2859
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réduction proportionnelle des 7 heures pour les agents à temps partiel ou à temps non complet est absente, et l'application aux fonctionnaires comme aux contractuels n'est pas mentionnée. La réponse ajoute aussi une erreur : « Les modalités peuvent varier selon les accords d'entreprise ou les conventions collectives », un cadre qui relève du droit privé et non de la FPT.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F2859) correspond à la source attendue et traite bien de la journée de solidarité dans la fonction publique.
- Inventions : Exemple « travail d'un samedi non habituel », absent des références; « Les modalités peuvent varier selon les accords d'entreprise ou les conventions collectives applicables à votre territoire »; « Aucune précision sur les jours fériés spécifiques à votre collectivité (ex. : ponts locaux) ou les accords sectoriels »
- Confiance : haute

**Juge second** : non-juge (limite-debit)

## Q-038 (Q, moyen)

### Entrée

```text
Un adjoint administratif titulaire de notre mairie a repris le travail le lundi après un arrêt maladie, puis a dû s'arrêter de nouveau dès le mardi pour la même affection ; le médecin a coché la case « prolongation ». Un nouveau jour de carence doit-il être retenu sur son traitement ? Rappelez-moi aussi la règle générale.
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "En principe, un jour de carence s'applique lors de chaque arrêt de travail : le fonctionnaire est rémunéré à partir du 2e jour de congé de maladie ; le 1er jour, son traitement indiciaire, ses primes et indemnités, ainsi que l'indemnité de résidence et la NBI, ne lui sont pas versés (le supplément familial de traitement, lui, continue d'être versé). Le jour de carence ne s'applique toutefois pas au 2e congé de maladie lorsque la reprise du travail entre les 2 congés pour la même affection n'a pas dépassé 48 heures et que le médecin a coché la case prolongation : le nouvel arrêt prolonge le précédent. Ce délai de 48 heures se décompte en jours calendaires à partir du 1er jour qui suit le dernier jour de l'arrêt initial. Ici, l'agent ne doit donc pas subir de nouveau jour de carence. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Principe : un jour de carence à chaque arrêt, rémunération à partir du 2e jour de congé de maladie",
    "Le 1er jour, pas de traitement indiciaire ni de primes et indemnités (ni indemnité de résidence ni NBI) ; le SFT reste versé",
    "Exception : pas de jour de carence pour le 2e congé si la reprise entre deux congés pour la même affection n'a pas dépassé 48 heures et que la case prolongation est cochée",
    "Les 48 heures se décomptent en jours calendaires à partir du jour qui suit le dernier jour de l'arrêt initial",
    "Conclusion : pas de nouveau jour de carence pour cet agent"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F13861"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
Voici les réponses basées sur les passages fournis :

### **Règle générale sur le jour de carence**
Oui, un **jour de carence non rémunéré** est appliqué à chaque arrêt de maladie, sauf exceptions précises [1][2][3][4][5].

---

### **Application dans votre cas**
Non, **un nouveau jour de carence ne doit pas être retenu** pour cet arrêt, car :
- Il s’agit d’une **prolongation** de l’arrêt précédent (le médecin a coché la case correspondante).
- La reprise du travail entre les deux arrêts n’a pas dépassé **48 heures** [2][3].
- Il s’agit donc d’une **rechute** et non d’un nouvel arrêt indépendant.

---
**À vérifier** :
- Si l’arrêt initial était déjà en cours au moment de la reprise, la règle de prolongation pourrait s’appliquer différemment. Vérifiez si le certificat médical précise une **interruption** ou une **continuité** de l’affection.

Sources citées :
- Y-a-t-il un délai de carence en cas de maladie dans la fonction publique ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F13861
- Y-a-t-il un délai de carence en cas de maladie dans la fonction publique ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F13861
- Y-a-t-il un délai de carence en cas de maladie dans la fonction publique ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F13861
- Y-a-t-il un délai de carence en cas de maladie dans la fonction publique ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F13861
- Y-a-t-il un délai de carence en cas de maladie dans la fonction publique ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F13861
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La conclusion (« un nouveau jour de carence ne doit pas être retenu ») et l'exception des 48 heures avec case prolongation sont justes, mais au moins deux éléments clés manquent : rien sur les éléments non versés le 1er jour (traitement, primes, IR, NBI) ni sur le maintien du SFT, rien sur le décompte en jours calendaires ; la qualification de « rechute » est en outre imprécise.
- `pertinence_source` : 1 — La source citée, la fiche service-public.gouv.fr F13861 sur le délai de carence dans la fonction publique, traite bien du point demandé.
- Inventions : « Il s'agit donc d'une rechute et non d'un nouvel arrêt indépendant » : qualification de rechute absente des références.; « Si l'arrêt initial était déjà en cours au moment de la reprise, la règle de prolongation pourrait s'appliquer différemment » : réserve non vérifiable dans les références.; « Vérifiez si le certificat médical précise une interruption ou une continuité de l'affection » : condition non vérifiable dans les références.
- Confiance : haute

## Q-040 (Q, moyen)

### Entrée

```text
Une agente de la préfecture (fonction publique d'État), à temps plein et enceinte, souhaite télétravailler 4 jours par semaine. Est-ce possible, comment doit-elle faire sa demande, et combien percevra-t-elle au titre du forfait télétravail ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "En principe, un agent à temps plein peut télétravailler au maximum 3 jours par semaine, avec au moins 2 jours de travail sur site (ces seuils peuvent être calculés sur une base mensuelle). Pendant sa grossesse, l'agente peut toutefois demander à télétravailler plus de 3 jours par semaine. Elle doit formuler sa demande par écrit (recours régulier ou ponctuel, lieu, nombre de jours souhaités) ; l'administration lui fait connaître sa décision par écrit dans le mois suivant la réception de la demande. Le forfait télétravail est de 2,88 € par journée de télétravail, dans la limite de 253,44 € par an (soit 88 jours indemnisés), versé à la fin de chaque trimestre. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Principe : 3 jours de télétravail maximum par semaine pour un agent à temps plein, au moins 2 jours sur site",
    "Pendant la grossesse, possibilité de demander plus de 3 jours par semaine",
    "Demande écrite ; décision écrite de l'administration dans le mois suivant la réception",
    "Forfait télétravail : 2,88 € par jour, dans la limite de 253,44 € par an (88 jours), versé à la fin de chaque trimestre"
  ],
  "sources_attendues": [
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F13974"
  ],
  "sans_reponse": false,
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
D'après les passages fournis, voici les réponses à votre question :

### **Possibilité de télétravail**
- **Oui, c'est possible** pour une agente enceinte, car le passage [1] précise que :
  > *« Vous pouvez aussi demander à télétravailler plus de 3 jours par semaine dans les cas suivants : [...] Pendant votre grossesse »* **[1]**.

---

### **Demande de télétravail**
- Elle doit **formuler sa demande auprès de son supérieur hiérarchique** en suivant les modalités générales de l'autorisation de télétravail (comme indiqué au passage [3] et [4]).
- **Pas de période d'adaptation obligatoire** si la demande est justifiée par sa grossesse, mais elle devra respecter les conditions fixées dans l'autorisation écrite (comme les plages horaires et les équipements fournis).
- **L'administration doit motiver son accord** et l'informer des droits et obligations liés au télétravail (comme précisé au passage [4]).

---
### **Forfait télétravail**
- **Elle a droit à une indemnité** sous forme d'un **forfait télétravail** de **2,88 € par jour** (dans la limite de **253,44 € par an**, soit **88 jours indemnisés**).
- Ce forfait est versé **trimestriellement** et peut faire l'objet d'une régularisation annuelle (passage [2]).
- **Conditions pour en bénéficier** :
  - Le télétravail doit être **autorisé** et **justifié** (ici, par sa grossesse).
  - Elle ne doit pas travailler dans un **télécentre** avec un service de restauration collective financé par l'administration (passage [2]).

---
### **Ce qui reste à vérifier**
- **Le nombre exact de jours de télétravail autorisés** par sa préfecture (certaines administrations peuvent fixer des seuils spécifiques).
- **Les modalités de calcul des jours indemnisés** (si elle télétravaille 4 jours sur 5, sera-t-elle indemnisée pour tous les jours ou seulement les jours supplémentaires ?).
- **Les éventuelles règles spécifiques à la fonction publique territoriale ou hospitalière** (les passages ne précisent pas les différences entre FPE, FPT et FPH pour les cas particuliers comme la grossesse).

---
### **Recommandation**
Pour confirmer les détails pratiques (comme les jours indemnisés ou les modalités de demande), elle devrait consulter :
- **Son service RH ou son supérieur hiérarchique** dans la préfecture.
- **La documentation interne de sa fonction publique d'État** (par exemple, les arrêtés ministériels ou les procédures locales sur le télétravail).

Sources citées :
- Télétravail dans la fonction publique — https://www.service-public.gouv.fr/particuliers/vosdroits/F13974
- Télétravail dans la fonction publique — https://www.service-public.gouv.fr/particuliers/vosdroits/F13974
- Télétravail dans la fonction publique — https://www.service-public.gouv.fr/particuliers/vosdroits/F13974
- Télétravail dans la fonction publique — https://www.service-public.gouv.fr/particuliers/vosdroits/F13974
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Deux éléments clés manquent : la règle de principe (3 jours maximum, au moins 2 jours sur site) n'est jamais énoncée, et la procédure ne mentionne ni la demande écrite ni la décision écrite dans le mois (« formuler sa demande auprès de son supérieur hiérarchique »). La réponse contient en outre une erreur : « L'administration doit motiver son accord », alors que la motivation concerne le refus.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F13974, Télétravail dans la fonction publique) traite bien du point demandé et correspond à la source attendue.
- Inventions : Pas de période d'adaptation obligatoire si la demande est justifiée par sa grossesse; L'administration doit motiver son accord; Le forfait peut faire l'objet d'une régularisation annuelle; Condition : le télétravail doit être justifié (ici, par sa grossesse) pour bénéficier du forfait; Exclusion en cas de travail dans un télécentre avec restauration collective financée par l'administration (non vérifiable dans les références)
- Confiance : haute

## Q-057 (Q, moyen)

### Entrée

```text
Pour une réunion avec nos partenaires médico-sociaux, je dois présenter en quelques lignes l'agence régionale de santé (ARS) Bourgogne-Franche-Comté : son statut, ses missions et son organisation. Que puis-je dire ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Je ne trouve pas, dans les fiches officielles dont je dispose, de source qui présente l'ARS Bourgogne-Franche-Comté (son statut, ses missions ou son organisation) : les fiches service-public ne mentionnent les agences régionales de santé qu'incidemment. Je ne peux donc pas vous en faire une présentation sourcée. Je vous conseille de consulter le site officiel de l'ARS Bourgogne-Franche-Comté ou de vous adresser directement à ses services. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Dit explicitement qu'aucune source officielle disponible ne présente l'ARS Bourgogne-Franche-Comté (statut, missions, organisation)",
    "N'invente aucune URL et ne présente aucune fiche service-public comme source d'une présentation de l'ARS Bourgogne-Franche-Comté (citer la mention incidente des ARS parmi les établissements publics administratifs, fiche F35235, est admis)",
    "N'avance ni date de création, ni statut, ni liste de missions ou d'implantations non sourcés (au plus, le développement du sigle « agence régionale de santé »)",
    "Oriente vers le site officiel ou les services de l'ARS Bourgogne-Franche-Comté"
  ],
  "sources_attendues": [],
  "sans_reponse": true,
  "orientation_attendue": "Consulter le site officiel de l'ARS Bourgogne-Franche-Comté ou s'adresser directement à ses services, sans présenter de statut, de missions ni d'organisation non sourcés.",
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
D'après les passages fournis dans l'Index local, voici ce que l'on peut confirmer concernant les établissements de santé en Bourgogne-Franche-Comté :

- **Statut** :
  Les établissements de santé en Bourgogne-Franche-Comté sont des structures géolocalisées, comme les établissements du domaine sanitaire et social, listés dans le système d’information FINESS. Leur géolocalisation repose sur les données BD-ADRESSE de l'IGN [1].

- **Missions et organisation** :
  Les informations disponibles ne concernent pas directement les **ARS** (Agences Régionales de Santé). Les passages mentionnés se limitent aux établissements de santé et aux aires de covoiturage, sans mention explicite des ARS ou de leurs missions.

**À vérifier** :
- Les missions et l'organisation des **ARS Bourgogne-Franche-Comté** ne sont pas explicitement détaillées dans les passages fournis.
- Pour obtenir des informations précises sur les ARS, je vous recommande de consulter :
  - Le site officiel de la **Direction Régionale de l’Environnement, de l’Aménagement et du Logement (DREAL)** pour les aspects liés à la santé publique et les ressources stratégiques.
  - Le site de la **Région Bourgogne-Franche-Comté** ou celui du **Ministère des Solidarités et de la Santé** pour les aspects médico-sociaux et sanitaires.

Si vous souhaitez des précisions sur les établissements de santé en BFC, je peux vous donner des éléments basés sur les données disponibles [1].

Sources citées :
- Établissements de santé en Bourgogne-Franche-Comté — https://www.data.gouv.fr/datasets/etablissements-de-sante-en-bourgogne-franche-comte
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse admet que les « missions et l'organisation des ARS Bourgogne-Franche-Comté ne sont pas explicitement détaillées », mais elle présente sous l'intitulé « Statut » des informations hors sujet sur la géolocalisation FINESS des établissements de santé. Elle oriente à tort vers la DREAL « pour les aspects liés à la santé publique » au lieu du site ou des services de l'ARS. Elle omet aussi la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 0 — La seule source citée est le jeu de données data.gouv « Établissements de santé en Bourgogne-Franche-Comté ». Elle ne traite ni du statut, ni des missions, ni de l'organisation de l'ARS BFC.
- `cas_sans_reponse` : 0 — La réponse reconnaît en partie l'absence d'information, mais n'oriente pas, comme attendu, vers le site officiel ou les services de l'ARS Bourgogne-Franche-Comté. Elle renvoie à la DREAL, à la Région et au ministère, et présente un contenu hors sujet comme réponse sur le « Statut ».
- Inventions : Orientation vers la DREAL « pour les aspects liés à la santé publique et les ressources stratégiques », information non vérifiable dans les références et erronée.; Présentation, sous l'intitulé « Statut », d'informations sur les établissements de santé (FINESS, BD-ADRESSE de l'IGN) comme réponse au statut de l'ARS, information non vérifiable dans les références.
- Confiance : haute

## Q-063 (Q, difficile)

### Entrée

```text
Le conseil municipal envisage d'instituer la taxe sur les friches commerciales. Quels locaux seraient concernés, quel serait le taux applicable et avant quelle date la délibération doit-elle être prise pour une application l'année suivante ? Que puis-je répondre aux élus ?
```

### Références (vues par le Juge)

```text
{
  "reponse_reference": "Je ne trouve pas de source officielle, dans les fiches et les données dont je dispose, qui traite de la taxe sur les friches commerciales (locaux concernés, taux, date de délibération). Je ne peux donc pas vous donner de réponse sourcée. Je vous conseille de vous rapprocher de la direction départementale des finances publiques ou de consulter les publications officielles relatives à la fiscalité locale. Ne vaut pas avis juridique.",
  "elements_cles": [
    "Dit explicitement qu'aucune source officielle de l'Index local ne traite de la taxe sur les friches commerciales (locaux concernés, taux, date de délibération)",
    "N'invente ni condition, ni montant, ni date, ni URL, et ne cite aucune fiche service-public comme source",
    "Oriente vers la direction départementale des finances publiques ou les publications officielles sur la fiscalité locale",
    "Si des éléments sur le sujet sont avancés, ils sont présentés comme non sourcés et à vérifier"
  ],
  "sources_attendues": [],
  "sans_reponse": true,
  "orientation_attendue": "Conseiller de vous rapprocher de la direction départementale des finances publiques ou de consulter les publications officielles relatives à la fiscalité locale, sans avancer de fait non sourcé.",
  "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

### Sortie (statut ok)

```text
D’après les passages fournis, voici les éléments que vous pouvez mentionner concernant votre question :

### **Locaux concernés par une éventuelle taxe sur les friches commerciales**
- **Seuls les espaces en friche ayant accueilli une activité urbaine ou économique (mais non réutilisés de manière pérenne)** sont concernés.
  [4] : *« La friche se définit comme tout espace ayant accueilli une activité urbaine, économique ou un équipement, et qui n’est plus utilisé ou marginalement lors du recensement. »*

- **Les friches agricoles ne sont pas concernées**, sauf si des bâtiments dégradés sont présents.
  [4] : *« Les friches agricoles ne sont pas prises en compte, sauf si la présence de bâtiments dégradés est relevée. »*

---
### **Taux applicable**
- **Aucune information précise sur le taux** n’est disponible dans les passages fournis.
  [1] et [2] ne mentionnent pas de taux spécifique pour une taxe sur les friches.
  **À vérifier** :
  - Les délibérations municipales ou intercommunales récentes sur la fiscalité des friches.
  - Les textes locaux ou les rapports de l’**Établissement Public Foncier de Normandie** (via [l’Observatoire des friches](https://www.datanormandie.fr/)).

---
### **Date limite pour la délibération**
- **Aucune date légale** n’est indiquée dans les passages fournis.
  [3] et [1] ne précisent pas de délai pour une application annuelle.
  **À vérifier** :
  - Les règles générales de fiscalité locale (ex. : délai de 6 mois avant l’année concernée pour les taxes votées).
  - Les procédures spécifiques de l’**Orne** (via la Direction Départementale des Territoires).

---
### **Recommandation pour les élus**
Vous pouvez indiquer :
- *« La taxe sur les friches commerciales doit concerner uniquement les espaces ayant perdu leur usage urbain ou économique, sans inclure les friches agricoles (sauf bâtiments dégradés). »*
- *« Pour un taux précis, il faudrait consulter les délibérations municipales ou les sources locales (ex. : EPFN de Normandie). »*
- *« La délibération doit être prise avant la fin de l’année civile pour une application effective l’année suivante (vérifier les délais administratifs locaux). »*

---
### **Sources officielles à consulter**
- **Direction Départementale des Territoires de l’Orne** ([site officiel](https://www.ddtemorne.fr/)) pour les règles locales.
- **Établissement Public Foncier de Normandie** ([Observatoire des friches](https://www.datanormandie.fr/)) pour les données sur les friches.
- **Conseil départemental de l’Orne** pour les délibérations fiscales.

*(Si vous avez besoin d’aide pour trouver ces sources, je peux orienter vers des liens similaires dans les données publiques.)*

Sources citées :
- Friches issues de l' EPFN dans l'Orne en 2026 — https://www.data.gouv.fr/datasets/friches-issues-de-l-epfn-dans-lorne-en-2026
- Taxe d'aménagement dans le cadre de la fiscalité de l'urbanisme pour 2021 — https://www.data.gouv.fr/datasets/taxe-damenagement-dans-le-cadre-de-la-fiscalite-de-lurbanisme-pour-2021
- Fiscalité locale - Millésimé — https://www.data.gouv.fr/datasets/fiscalite-locale-millesime
- Quels sont les travaux à déclarer aux impôts ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F35742
```

### Contrôles automatiques

```text
{
  "urls_inventees": [
    "https://www.datanormandie.fr/",
    "https://www.ddtemorne.fr/"
  ]
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie ne dit pas qu'aucune source officielle ne traite de la taxe : elle présente la définition EPFN d'une friche (« Les friches agricoles ne sont pas prises en compte ») comme critère des locaux concernés. Elle avance aussi une date non sourcée (« La délibération doit être prise avant la fin de l'année civile ») et invente des URL (ddtemorne.fr).
- `pertinence_source` : 0 — Les sources citées (recensement EPFN des friches de l'Orne, taxe d'aménagement, fiscalité locale millésimée, fiche service-public F35742 sur les travaux à déclarer) ne traitent pas de la taxe sur les friches commerciales.
- `cas_sans_reponse` : 0 — Au lieu de déclarer l'absence de source officielle et d'orienter vers la DDFiP, l'Assistant invente une réponse : locaux concernés, date limite « avant la fin de l'année civile ». Il oriente en outre vers la DDT et l'EPFN plutôt que vers la DDFiP.
- Inventions : Assimilation de la définition EPFN d'une friche aux locaux soumis à la taxe sur les friches commerciales; « Les friches agricoles ne sont pas concernées » appliqué à la taxe; « La délibération doit être prise avant la fin de l'année civile pour une application effective l'année suivante »; « délai de 6 mois avant l'année concernée pour les taxes votées »; URL https://www.ddtemorne.fr/; URL https://www.datanormandie.fr/ présentée comme Observatoire des friches de l'EPFN; Citation de la fiche service-public F35742 comme source; Orientation vers le Conseil départemental de l'Orne pour les délibérations fiscales; Absence de la mention « Ne vaut pas avis juridique »
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
Sur l'**Index local** [1], le jeu de données pertinent pour les communes soumises à la loi SRU et leur inventaire de logements sociaux est :

- **Titre** : *Logements sociaux en France – Données 2023*
- **Producteur** : Agence nationale de la rénovation urbaine (ANRU) et DREAL (Direction régionale de l'environnement, de l'aménagement et du logement)
- **Date de dernière mise à jour** : 2023 (à vérifier en ligne)
- **Lien** : [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/logements-sociaux-en-france-donnees-2023/) (à confirmer selon les résultats de recherche).

Je vais vérifier si ce jeu de données est bien disponible sur data.gouv.fr et si son contenu correspond à vos besoins.Le jeu de données le plus pertinent pour les communes soumises à la loi SRU et leur inventaire de logements sociaux est :

- **Titre** : *Communes et inventaire SRU*
- **Producteur** : Ministère de la Transition écologique
- **Date de dernière mise à jour** : [à vérifier en ligne sur le lien ci-dessous]
- **Lien** : [data.gouv.fr](https://www.data.gouv.fr/datasets/communes-et-inventaire-sru)

Ce jeu de données semble couvrir les communes concernées par la loi SRU et inclut probablement des informations sur leur inventaire de logements sociaux. Je vais maintenant consulter ses ressources pour identifier les colonnes pertinentes.Il semble que les ressources associées au jeu de données *Communes et inventaire SRU* ne soient pas directement accessibles via l'outil actuel. Cependant, selon l'**Index local** [1], ce jeu de données est censé contenir les informations sur les communes soumises à la loi SRU et leur inventaire de logements sociaux.

Je vais vérifier les détails du jeu de données pour confirmer son contenu et ses ressources disponibles.Il semble que je n'aie pas pu récupérer les informations détaillées du jeu de données *Communes et inventaire SRU* via les outils disponibles en ce moment.

D'après l'**Index local** [1], voici une autre piste possible :
- **Titre** : *Communes SRU et DALO* (produit par la Région Occitanie / Pyrénées Méditerranée)
  - **Lien** : [data.gouv.fr](https://www.data.gouv.fr/datasets/communes-sru-et-dalo)

Je vais explorer ce jeu de données pour voir s'il contient les informations recherchées.Je vais consulter les ressources disponibles pour le jeu de données *Communes et inventaire SRU* directement via leur URL pour vérifier s'il existe des fichiers accessibles. Je vais aussi essayer une autre approche pour identifier les données pertinentes.Je vais essayer de télécharger les fichiers disponibles pour le jeu de données *Communes et inventaire SRU* afin d'explorer ses ressources. Je vais aussi vérifier s'il existe une documentation ou une description des colonnes pertinentes sur la page du jeu de données.[TOOL_CALLS]download_dataset_resources[ARGS]{"dataset_id": "6564969d3579e21795ebd378"}[TOOL_CALLS]fetch_dataset_description[ARGS]{"dataset_url": "https://www.data.gouv.fr/datasets/communes-et-inventaire-sru"}

Sources citées :
- Communes et inventaire SRU — https://www.data.gouv.fr/datasets/communes-et-inventaire-sru
- Communes SRU et DALO — https://www.data.gouv.fr/datasets/communes-sru-et-dalo
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

## RD-006 (RD, moyen)

### Entrée

```text
Je suis les effectifs nationaux d'allocataires du RSA publiés par la CNAF, répartis selon le type de RSA et la situation familiale (niveau national, pas départemental). Trouve ce jeu et indique-moi sa date de dernière mise à jour, sa licence et sa fréquence de mise à jour.

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
      "id": "66d1e5a979919854e97093bd",
      "titre": "RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National]",
      "producteur": "Caisse Nationale des Allocations familiales",
      "url": "https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national/",
      "derniere_mise_a_jour": "2026-10-09T15:22:26.338000+00:00",
      "licence": "lov2"
    },
    "autres_jeux_cites_possibles": [
      {
        "id": "66d1e59e79919854e9709399",
        "titre": "RSA - Répartition des allocataires selon le type de RSA et la situation familiale [Départemental]",
        "producteur": "Caisse Nationale des Allocations familiales"
      }
    ],
    "texte": "Le jeu est « RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National] » (identifiant 66d1e5a979919854e97093bd), de la Caisse Nationale des Allocations familiales : https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national/. Dernière mise à jour : 2026-10-09T15:22:26.338000+00:00 ; licence : lov2 (Licence Ouverte v2) ; fréquence de mise à jour : monthly (mensuelle)."
  },
  "criteres": [
    "Cite le jeu national (identifiant 66d1e5a979919854e97093bd), pas la version départementale",
    "Donne la date de dernière mise à jour 2026-10-09, la licence lov2 et la fréquence mensuelle (monthly)"
  ]
}
```

### Sortie (statut ok)

```text
Le jeu de données correspondant à vos besoins est :

**[RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National]]**
- **Producteur** : Caisse Nationale des Allocations familiales (CNAF)
- **Date de dernière mise à jour** : [Vérifiez directement sur le site](https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national) (je ne peux pas afficher cette information en temps réel ici).
- **Licence** : [Vérifiez sur la page du jeu de données](https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national) (généralement en open data, souvent sous licence **CC-BY 4.0** ou similaire).
- **Fréquence de mise à jour** : [À vérifier sur la page](https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national), mais généralement **mensuelle ou trimestrielle** pour les données sociales.

---
### Prochaines étapes :
1. **Consultez la page du jeu de données** ([lien](https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national)) pour confirmer :
   - La date exacte de dernière mise à jour.
   - La licence appliquée.
   - La fréquence de mise à jour.

2. Si vous souhaitez interroger les données, je peux vous aider à :
   - Lister les ressources disponibles (fichiers CSV, JSON, etc.).
   - Extraire et analyser les valeurs si le jeu de données est accessible via une API ou un fichier téléchargeable.

Souhaitez-vous que je vérifie les ressources associées à ce jeu de données ?

Sources citées :
- RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National] — https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national
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

## RD-007 (RD, moyen)

### Entrée

```text
Je travaille sur les bénéficiaires de l'aide sociale à l'enfance à partir du jeu national publié par la DREES. Combien de fichiers ce jeu propose-t-il, et quel est le fichier de séries longues le plus récent (nom exact et format) ?

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
      "id": "62e325ed203e2e75a70505d1",
      "titre": "Les bénéficiaires de l'aide sociale à l'enfance",
      "producteur": "Ministère des Solidarités et de la Santé",
      "url": "https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance"
    },
    "texte": "Le jeu « Les bénéficiaires de l'aide sociale à l'enfance » (identifiant 62e325ed203e2e75a70505d1, Ministère des Solidarités et de la Santé, https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance) compte 20 ressources. Le fichier de séries longues le plus récent est « Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2024).xlsx » (ressource e9fb8aa6-201e-483d-b30f-a174fd42f496), au format tableur Excel (vnd.openxmlformats-officedocument.spreadsheetml.sheet)."
  },
  "criteres": [
    "Indique 20 ressources",
    "Désigne le fichier « séries longues (1996-2024) » au format xlsx, pas celui de 1996-2023"
  ]
}
```

### Sortie (statut ok)

```text
Parmi les résultats, le jeu de données pertinent pour les bénéficiaires de l'aide sociale à l'enfance est :

- **Titre** : *Les bénéficiaires de l'aide sociale à l'enfance*
  - **Producteur** : Ministère des Solidarités et de la Santé
  - **Date de dernière mise à jour** : [Vérifiez sur le site pour la date exacte, mais disponible sur data.gouv.fr]
  - **Lien** : [https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance](https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance)
  - **Nombre de fichiers (ressources)** : **20**.

---

Pour identifier le fichier de séries longues le plus récent, je vais consulter les ressources de ce jeu de données.Parmi les ressources du jeu de données *Les bénéficiaires de l'aide sociale à l'enfance*, voici les fichiers de séries longues :

- **[Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2023).xlsx]** (format Excel)
  - **ID de ressource** : `e1f1a2c3-c83c-4530-8983-a40295e62b18`
  - **Lien** : [https://data.drees.solidarites-sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2023_xlsx](https://data.drees.sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2023_xlsx)

- **[Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2024).xlsx]** (format Excel)
  - **ID de ressource** : `e9fb8aa6-201e-483d-b30f-a174fd42f496`
  - **Lien** : [https://data.drees.sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2024_xlsx](https://data.drees.sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2024_xlsx)

Le fichier le plus récent est donc :
**Nom exact** : *Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2024).xlsx*
**Format** : Excel.

Souhaitez-vous que je vérifie la structure de ce fichier pour identifier les colonnes pertinentes ?

Sources citées :
- Les bénéficiaires de l'aide sociale à l'enfance — https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance
- Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2023).xlsx — https://data.drees.solidarites-sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2023_xlsx
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

## RD-025 (RD, facile)

### Entrée

```text
Je dois écrire à l'ensemble des élus locaux du département (maires, conseillers municipaux, départementaux et régionaux). Existe-t-il sur data.gouv.fr un répertoire national de tous les élus en fonction ? Donne-moi le nom du jeu de données, son producteur et le lien.

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
      "id": "5c34c4d1634f4173183a64f1",
      "titre": "Répertoire national des élus",
      "producteur": "Ministère de l'intérieur",
      "url": "https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1"
    },
    "texte": "Le jeu national est « Répertoire national des élus » (identifiant 5c34c4d1634f4173183a64f1), produit par le Ministère de l'intérieur : https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1. Il couvre notamment les conseillers municipaux, communautaires, départementaux et régionaux."
  },
  "criteres": [
    "Cite le Répertoire national des élus (identifiant 5c34c4d1634f4173183a64f1), pas une déclinaison locale ni la liste des sortants des municipales 2026",
    "Donne le producteur et le lien data.gouv.fr"
  ]
}
```

### Sortie (statut ok)

```text
Le jeu de données qui correspond à un répertoire national de tous les élus en fonction est :

- **Titre** : Répertoire national des élus
- **Producteur** : Ministère de l'intérieur
- **Date de dernière mise à jour** : Non précisée sur le résultat actuel (consultez directement le lien pour les dernières informations).
- **Lien** : [Répertoire national des élus](https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1)

Ce jeu de données couvre les différents profils d'élus locaux (conseillers municipaux, départementaux, régionaux, etc.) et est le plus complet pour votre recherche. Vous pouvez consulter les ressources associées pour obtenir des détails supplémentaires.

Sources citées :
- Répertoire national des élus — https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1
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

## RD-029 (RD, moyen)

### Entrée

```text
Je veux mettre à jour les adresses, téléphones et horaires d'ouverture des mairies de mon département dans notre outil interne. Quel jeu national de l'annuaire Service-public recense les guichets publics locaux sur data.gouv.fr ? Donne-moi sa licence et sa fréquence de mise à jour.

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
      "id": "53699fe4a3a729239d206227",
      "titre": "Service-public.gouv.fr - Annuaire de l’administration - Base de données locales",
      "producteur": "Premier ministre",
      "url": "https://www.data.gouv.fr/datasets/service-public-gouv-fr-annuaire-de-ladministration-base-de-donnees-locales",
      "licence": "fr-lo"
    },
    "autres_jeux_cites_possibles": [
      {
        "id": "688201cd45ea9d6bf4921b95",
        "titre": "Service-public.fr - Annuaire de l’administration - Base de données locales vectorisée",
        "producteur": "Direction interministérielle du numérique"
      }
    ],
    "texte": "Le jeu est « Service-public.gouv.fr - Annuaire de l’administration - Base de données locales » (identifiant 53699fe4a3a729239d206227), produit par le Premier ministre : https://www.data.gouv.fr/datasets/service-public-gouv-fr-annuaire-de-ladministration-base-de-donnees-locales. Il référence plus de 86 000 guichets publics locaux (mairies, organismes sociaux, services de l'état, etc.) avec leurs coordonnées et horaires d'ouverture. Licence : fr-lo. Fréquence de mise à jour déclarée : punctual (ponctuelle)."
  },
  "criteres": [
    "Cite le jeu national du Premier ministre (identifiant 53699fe4a3a729239d206227), pas une déclinaison régionale",
    "Donne la licence et la fréquence telles que dans les métadonnées"
  ]
}
```

### Sortie (statut ok)

```text
D'après l'**Index local** sur data.gouv.fr, voici les jeux de données qui pourraient correspondre à votre recherche :

- **[Guichet unique des services publics (GUSP) – Données des mairies et autres établissements publics locaux]** ([lien vers le jeu de données](https://www.data.gouv.fr/fr/datasets/guichet-unique-des-services-publics-gusp-donnees-des-mairies-et-autres-etablissements-publics-locaux/)).
  - **Producteur** : Service public français (via la Direction de l'information légale et administrative, DILA).
  - **Date de dernière mise à jour** : [À vérifier en ligne, dernière mise à jour récente en 2023](https://www.data.gouv.fr/fr/datasets/guichet-unique-des-services-publics-gusp-donnees-des-mairies-et-autres-etablissements-publics-locaux/) (consultez directement la page pour la dernière date exacte).
  - **Licence** : [Licence Ouverte 2.0](https://www.data.gouv.fr/fr/licences/licence-ouverte-2-0/) (ou équivalente, selon les cas).

---
### Autres pistes possibles (selon l'Index local) :
- **[Données des collectivités territoriales – Mairies et communes](https://www.data.gouv.fr/fr/datasets/donnees-des-collectivites-territoriales-mairies-et-communes/)** (si disponible).
  - **Licence** : Généralement sous licence **Ouverte 2.0** ou **CC-BY-SA** (vérifiez en ligne).

---
### Prochaines étapes :
1. **Vérifiez la dernière mise à jour** sur le lien du jeu de données pour confirmer la fréquence de mise à jour.
2. **Consultez les ressources** (fichiers) associés pour identifier les colonnes pertinentes (adresses, horaires, etc.).
3. Si le jeu de données ne contient pas assez de détails, explorez les jeux de données locaux par département (ex. : données de votre département sur [data.gouv.fr](https://www.data.gouv.fr/)).

Souhaitez-vous que je vérifie en ligne la dernière mise à jour du jeu de données **[Guichet unique des services publics (GUSP)]** ou que je liste ses ressources pour voir les colonnes disponibles ?

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

## RD-039 (RD, difficile)

### Entrée

```text
Pour une note sur la mixité sociale, quel était l'indice de position sociale (IPS) du collège dont l'UAI est 0010005A à la rentrée scolaire 2022 ? Donne aussi le nom du collège, sa commune et ses effectifs, d'après les données nationales publiées sur data.gouv.fr.

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
      "id": "64265b62141b6f2153538672",
      "titre": "Indices de position sociale dans les collèges (2022)",
      "producteur": "Ministères de l'Éducation nationale",
      "url": "https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-colleges-a-partir-de-2022"
    },
    "texte": "D'après le jeu « Indices de position sociale dans les collèges (2022) » des Ministères de l'Éducation nationale (identifiant 64265b62141b6f2153538672, fichier fr-en-ips-colleges-ap2022.csv), le collège d'UAI 0010005A est le COLLEGE ROGER POULNARD, à BAGE DOMMARTIN (AIN, académie de LYON, secteur public). À la rentrée scolaire 2022-2023, son IPS était de 110.4 (écart-type 31.3) pour des effectifs de 540.0 élèves. Le filtre UAI exact 0010005A renvoie une seule ligne."
  },
  "valeurs_attendues": {
    "ressource_id": "28e511a7-af0d-48c7-a8bb-2f38ec003f49",
    "filtre": {
      "colonne": "UAI",
      "operateur": "exact",
      "valeur": "0010005A"
    },
    "total_lignes": 1,
    "lignes": [
      {
        "Rentrée scolaire": "2022-2023",
        "UAI": "0010005A",
        "Nom de l'établissment": "COLLEGE ROGER POULNARD",
        "Nom de la commune": "BAGE DOMMARTIN",
        "Effectifs": "540.0",
        "IPS": "110.4"
      }
    ],
    "colonnes": [
      "Effectifs",
      "IPS"
    ]
  },
  "criteres": [
    "Utilise le jeu 2022 (64265b62141b6f2153538672), pas ceux de 2016-2021 ou à partir de 2023",
    "Restitue IPS 110.4 et effectifs 540.0 sans arrondi inventé ni valeur extérieure"
  ]
}
```

### Sortie (statut ok)

```text
Le jeu de données le plus pertinent pour les données nationales sur les collèges et l'**Indice de Position Sociale (IPS)** pour la rentrée 2022 est :

**[2] Indices de position sociale dans les collèges (2022)**
- **Producteur** : Ministères de l'Éducation nationale
- **Date de dernière mise à jour** : 2022
- **Lien** : [https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-colleges-a-partir-de-2022](https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-colleges-a-partir-de-2022)

Je vais maintenant chercher les ressources associées à ce jeu de données pour identifier les fichiers contenant les informations sur les collèges et leurs effectifs.Le fichier CSV principal pour les données sur les collèges et l'**IPS** pour 2022 est :

**[1] fr-en-ips-colleges-ap2022.csv**
- **Format** : CSV
- **URL** : [Lien vers le fichier CSV](https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-colleges-ap2022/exports/csv?use_labels=true)

Je vais interroger ce fichier pour trouver les informations concernant le collège avec l'UAI **0010005A** (nommé **Collège X** selon les données disponibles dans le jeu de données).Voici les informations concernant le collège avec l'UAI **0010005A** pour la rentrée scolaire 2022 :

- **Nom du collège** : Collège Roger Poulnard
- **Commune** : Bage-Dommartin (Code INSEE : 01025)
- **Effectifs** : Environ 540 élèves
- **Indice de Position Sociale (IPS)** : **110,4**

Ces données proviennent du jeu de données **[Indices de position sociale dans les collèges (2022)](https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-colleges-a-partir-de-2022)** publié par les Ministères de l'Éducation nationale.

Sources citées :
- Indices de position sociale dans les collèges (2022) — https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-colleges-a-partir-de-2022
- fr-en-ips-colleges-ap2022.csv — https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-colleges-ap2022/exports/csv?use_labels=true
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
  "reponse_exacte": true,
  "valeurs_manquantes": []
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
Le jeu de données correspondant à l'extraction non géolocalisée du **FINESS** est :

- **Titre** : *FINESS Extraction du Fichier des établissements*
- **Producteur** : Ministère des Solidarités et de la Santé
- **Date de dernière mise à jour** : [à vérifier en ligne]
- **Lien** : [https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements](https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements)

Je vais maintenant vérifier si ce fichier est interrogeable via l'API tabulaire de data.gouv.fr et obtenir ses ressources pour confirmer.Le fichier correspondant à l'extraction **non géolocalisée** du FINESS est :

- **Titre du fichier** : *Extraction Finess des Etablissements au 04/05/2026*
- **Format** : CSV
- **Taille** : 34,1 Mo
- **URL de téléchargement** : [https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv](https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv)

Je vais vérifier si ce fichier est interrogeable via l'API tabulaire pour confirmer.Le fichier **Extraction Finess des Etablissements au 04/05/2026** n'est **pas interrogeable via l'API tabulaire** de data.gouv.fr.

Voici les informations disponibles :
- **Taille du fichier** : 34,1 Mo
- **URL de téléchargement** : [Lien du fichier](https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv).

Si vous souhaitez interroger ce fichier, vous devrez le télécharger et l'ouvrir avec un logiciel adapté (ex. : Excel, Python avec Pandas). Souhaitez-vous que je vous guide pour une lecture locale du fichier ?

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
    2
  ],
  "appels_attendus": 3,
  "appels_valides": 3,
  "litige": false,
  "methode": "identifiant",
  "reponse_exacte": true
}
```

### Verdicts

Aucun verdict.

## RE-001 (RE, facile)

### Entrée

```text
{
  "consigne": "Résume ce document en 80 mots au plus, pour un collègue de l'accueil du service logement.",
  "document": "Votre demande de logement peut être radiée lorsqu'elle est déclarée irrecevable. C'est le cas, par exemple, lorsque vos revenus sont supérieurs au plafond de revenus. Après que votre demande est déclarée irrecevable, vous recevez un avertissement par lettre recommandée avec avis de réception (ou tout moyen permettant d'attester de sa remise). Votre demande est radiée 1 mois après cet envoi. Pour contester votre radiation, vous devez vous adresser à l'organisme ou à l'administration (mairie, organisme HLM...) qui vous a radié. La démarche à effectuer vous sera alors indiquée.\nCas Mairie: \nCas Organisme HLM:\nVotre demande de logement peut être radiée si vous ne la renouvelez pas dans le mois qui précède sa date anniversaire, c'est-à-dire au bout de 11 mois. La radiation intervient sans délai. Si votre demande a été radiée, mais que vous souhaitez obtenir un logement social, vous devez recommencer toute la procédure de demande. Un nouveau numéro unique d'enregistrement vous sera attribué. Si vous étiez dans l'incapacité de renouveler votre demande, vous pouvez contester la radiation de votre demande. Pour cela, vous devez vous rendre dans un guichet enregistreur du département concerné :\n- Allier (03)\n- Bas-Rhin (67)\n- Calvados (14)\n- Cantal (15),\n- Côtes d’Armor (22)\n- Côte d’Or (21)\n- Doubs (25)\n- Finistère (29)\n- Haute Garonne (31)\n- Haute Loire (43)\n- Haute Saône (70)\n- Haut Rhin (68)\n- Ille et Vilaine (35)\n- Indre et Loire (37)\n- Jura (39)\n- Loire Atlantique (44)\n- Maine et Loire (49)\n- Manche (50)\n- Mayenne (53)\n- Morbihan (56)\n- Nièvre (58)\n- Orne (61)\n- Puy de Dôme (63)\n- Sarthe (72)\n- Territoire de Belfort (90)\n- Vendée (85)\n- Vosges (88)\n- Yonne (89)\n- Autre département .\nVotre demande peut être radiée lorsque vous ne répondez pas aux courriers qui sont envoyés à votre dernière adresse déclarée. Vous recevez un avertissement par lettre recommandée avec avis de réception (ou tout moyen permettant d'attester de sa remise). Votre demande est radiée 1 mois après cet envoi. Pour contester votre radiation, vous devez vous adresser à l'organisme ou à l'administration (mairie, office HLM...) qui vous a radié. La démarche à effectuer vous sera alors indiquée.\nCas Mairie: \nCas Organisme HLM:\nDès que vous signez le bail du logement social qui vous est attribué, votre demande est radiée.\nVous pouvez renoncer à votre demande de logement par écrit. La radiation de votre demande intervient sans délai.\nPlusieurs numéros d'enregistrement de demande de logement social vous sont attribués lorsque vous avez fait plusieurs fois au cours de la même année une demande de logement social. Dans ce cas, vos différentes demandes sont automatiquement radiées pour être regroupées en une demande unique. Un numéro unique national d'enregistrement vous est alors attribué. Pour chaque demande radiée, l'ancienneté acquise est conservée, afin qu'elle s'applique aux communes demandées. Plusieurs anciennetés sont alors attachées à votre numéro unique national.",
  "nb_mots": 453
}

Options de la demande :
{
  "longueur_demandee": "courte",
  "parametres": {}
}
```

### Références (vues par le Juge)

```text
{
  "points_cles_reference": [
    {
      "ref": "P1",
      "texte": "Demande irrecevable ou courriers sans réponse : radiation 1 mois après un avertissement par lettre recommandée"
    },
    {
      "ref": "P2",
      "texte": "Demande non renouvelée dans le mois précédant sa date anniversaire : radiation sans délai, procédure à recommencer avec un nouveau numéro"
    },
    {
      "ref": "P3",
      "texte": "Radiation à la signature du bail ou sur renonciation écrite"
    },
    {
      "ref": "P4",
      "texte": "Contestation auprès de l'organisme qui a radié ou d'un guichet enregistreur du département"
    }
  ],
  "longueur_demandee": "courte"
}
```

### Sortie (statut ok)

```text
**Résumé en 80 mots :**

Votre demande de logement peut être **radiée** si :
- Vos revenus dépassent le plafond (lettre recommandée → radiation après 1 mois).
- Vous ne renouvelez pas votre demande HLM avant sa date anniversaire (sans délai).
- Vous ne répondez pas aux courriers (lettre recommandée → radiation après 1 mois).
- Vous signez un bail ou renoncez par écrit.

Pour contester, adressez-vous à la mairie ou l’organisme concerné.
En cas de regroupement de demandes, un **numéro unique** est attribué (anciennetés conservées).

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "courte",
  "mots": 78,
  "plafond_mots": 80,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — « Pour contester, adressez-vous à la mairie ou l'organisme concerné » s'applique à tous les cas. Or le document renvoie à un guichet enregistreur du département pour le non-renouvellement. De plus, « demande HLM » qualifie à tort une demande de logement social, et « avant sa date anniversaire » déforme « dans le mois qui précède ».
- `presence_elements` :
  - P1 : 1 — Les deux cas figurent avec la lettre recommandée et la radiation après 1 mois. L'irrecevabilité est toutefois réduite au seul dépassement du plafond de revenus.
  - P2 : 0 — La radiation sans délai est mentionnée, mais ni la procédure à recommencer ni le nouveau numéro ne le sont.
  - P3 : 1 — « Vous signez un bail ou renoncez par écrit » couvre le point.
  - P4 : 0 — Seuls la mairie et l'organisme sont cités ; le guichet enregistreur du département est absent.
- Inventions : « demande HLM » : le document parle d'une demande de logement (social), pas spécifiquement HLM; Contestation auprès de la mairie ou de l'organisme généralisée à tous les cas de radiation
- Confiance : moyenne

## RE-007 (RE, moyen)

### Entrée

```text
{
  "consigne": "Fais un résumé détaillé de ce document, en 400 mots au plus, pour un agent de l'état civil.",
  "document": "La procédure de changement de prénom est ouverte aux personnes suivantes :\n- Français né en France\n- Français né à l'étranger dont la naissance a été déclarée aux postes consulaires français, ou qui a fait transcrire son acte de naissance étranger au service central d'état civil du ministère des affaires étrangères\n- Etranger né en France\n- Personne bénéficiant de la protection internationale.\nLe changement de prénom peut concerner un majeur ou un mineur :\nCas Majeur: Vous faites la demande pour vous même. Depuis le 1 er juillet 2022, un majeur sous tutelle peut demander à changer de prénom sans être représenté par son tuteur.\nCas Mineur: La demande doit être faite par le représentant légal de l'enfant. Si l'enfant a plus de 13 ans , son accord est nécessaire . En cas d'exercice conjoint de l'autorité parentale , la demande de changement de prénom doit être faite par les 2 parents, représentants légaux de l'enfant. Si les parents sont séparés et en désaccord , le parent qui veut demander la changement de prénom doit saisir le juge aux affaires familiales.\nVous pouvez demander à changer de prénom. Vous pouvez aussi demander :\n- L'ajout d'un prénom\n- La suppression d'un prénom\n- La modification de l'ordre de vos prénoms.\nLa demande de changement de prénom doit avoir un intérêt légitime. Exemples de motifs qui peuvent constituer un intérêt légitime : usage prolongé d’un prénom autre que celui figurant à l’état civil, suppression d’un prénom jugé ridicule et/ou association nom(s)/prénoms(s) jugée ridicule, ajout ou suppression d’un tiret entre 2 prénoms suite à un usage prolongé, transidentité du demandeur. La demande de changement de prénom ne doit pas être contraire à l'intérêt de l'enfant ou aux droits d'autres personnes à voir protéger leur nom de famille. (Rappel: Tout prénom inscrit dans l'acte de naissance peut être choisi comme prénom usuel, quel que soit son ordre .)\nLa démarche est gratuite.\nVous devez déposer votre demande de changement de prénom (formulaire rempli, daté et signé avec les justificatifs) :\n- à la mairie du lieu de votre résidence,\n- ou si vous êtes né(e) en France, à la mairie qui détient votre acte de naissance,\n- ou si vous résidez à l’étranger, à l’ambassade ou au consulat de France, compétent en raison du lieu de votre domicile,\n- ou si vous avez un certificat tenant lieu d’acte de naissance, à l’Office français de protection des réfugiés et apatrides (Ofpra).\nUn récépissé de dépôt de la demande vous est remis.\nSi l'officier de l'état civil estime que votre demande de changement de prénom n'a pas d'intérêt légitime, il doit saisir le procureur de la République. Il doit également saisir le procureur si vous avez été condamné pour une infraction terroriste, une infraction de nature sexuelle commise sur mineur, une violation d'une interdiction de sortie du territoire ou un non respect des obligations de contrôle du retour sur le territoire national. De même, il doit saisir le procureur si vous êtes inscrit au Fijait ou au Fijaisv. L'officier de l'état civil doit vous informer qu'il a saisi le procureur de la République. Le procureur de la République peut accepter ou refuser votre demande de changement de prénom. La décision vous est notifiée. En cas de décision de refus, vous pouvez faire un recours auprès du juge aux affaires familiales. L'avocat est obligatoire. C'est lui qui se charge de la démarche. (À savoir: Si vous demandez à changer de prénom en invoquant votre transidentité, la décision de l’officier de l’état civil ne doit pas être motivée par l'adéquation ou l'absence d'adéquation entre votre apparence physique et le prénom\ndemandé. Le prénom demandé peut être un prénom neutre, épicène , féminin ou masculin.)\nVous recevez une copie de la décision concernant votre changement de prénom. Vos actes de l'état civil sont mis à jour.\nUne fois votre acte de naissance mis à jour, vous devez modifier vos titres d'identité ( carte d'identité, passeport ). Vous devez faire la démarche dans un délai de 3 mois à partir de la mise à jour de votre acte de naissance. (À noter: L’usage d’un titre d’identité qui ne correspond pas à votre état civil est puni de 5 ans d'emprisonnement maximum et d'une amende pouvant aller jusqu'à 50 000 € .)",
  "nb_mots": 688
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
      "texte": "La procédure est ouverte aux Français nés en France, aux Français nés à l'étranger dont la naissance est déclarée ou transcrite, aux étrangers nés en France et aux bénéficiaires de la protection internationale"
    },
    {
      "ref": "P2",
      "texte": "Un majeur fait la demande pour lui-même, y compris sous tutelle sans être représenté depuis le 1er juillet 2022 ; pour un mineur, la demande est faite par le représentant légal, avec l'accord de l'enfant de plus de 13 ans, par les 2 parents en cas d'autorité parentale conjointe, et le juge aux affaires familiales tranche le désaccord de parents séparés"
    },
    {
      "ref": "P3",
      "texte": "On peut changer, ajouter ou supprimer un prénom ou en modifier l'ordre ; la demande doit avoir un intérêt légitime et ne pas être contraire à l'intérêt de l'enfant ni aux droits des tiers sur leur nom"
    },
    {
      "ref": "P4",
      "texte": "Tout prénom inscrit dans l'acte de naissance peut être choisi comme prénom usuel"
    },
    {
      "ref": "P5",
      "texte": "La démarche est gratuite ; la demande (formulaire et justificatifs) est déposée à la mairie de résidence, à la mairie qui détient l'acte de naissance, à l'ambassade ou au consulat pour un résident à l'étranger, ou à l'Ofpra ; un récépissé est remis"
    },
    {
      "ref": "P6",
      "texte": "L'officier de l'état civil saisit le procureur de la République s'il estime que l'intérêt n'est pas légitime, ou en cas de certaines condamnations ou d'inscription au Fijait ou au Fijaisv, et en informe le demandeur ; le procureur accepte ou refuse"
    },
    {
      "ref": "P7",
      "texte": "Un refus peut faire l'objet d'un recours devant le juge aux affaires familiales, avec un avocat obligatoire"
    },
    {
      "ref": "P8",
      "texte": "En cas de transidentité, la décision ne doit pas dépendre de l'adéquation entre l'apparence physique et le prénom, qui peut être neutre, épicène, féminin ou masculin"
    },
    {
      "ref": "P9",
      "texte": "Après acceptation, les actes d'état civil sont mis à jour ; la carte d'identité et le passeport doivent être modifiés dans les 3 mois (usage d'un titre non conforme puni de 5 ans d'emprisonnement et 50 000 € d'amende au maximum)"
    }
  ],
  "longueur_demandee": "detaillee"
}
```

### Sortie (statut ok)

```text
**Résumé détaillé pour un agent de l’état civil (400 mots maximum)**

### **Public concerné et conditions**
Le changement de prénom est accessible aux personnes suivantes :
- **Majeurs** : Français né en France, né à l’étranger avec une transcription de l’acte de naissance, étranger né en France, ou bénéficiaire de la protection internationale.
- **Mineurs** : Demande soumise par le représentant légal (parent ou tuteur). Si l’enfant a plus de 13 ans, son accord est requis. En cas de désaccord entre parents séparés, le juge aux affaires familiales (JAF) doit trancher.

### **Types de demandes autorisés**
La modification peut concerner :
- Un **changement de prénom**,
- L’**ajout d’un prénom**,
- La **suppression d’un prénom**,
- La **modification de l’ordre des prénoms**.

### **Critères d’intérêt légitime**
La demande doit justifier un motif sérieux, comme :
- Un usage prolongé d’un prénom différent de celui inscrit,
- La suppression d’un prénom jugé ridicule,
- Une modification de l’ordre des prénoms (ex. : ajout ou suppression d’un tiret),
- Une **transidentité** (le prénom ne doit pas être refusé en raison de l’adéquation avec l’apparence physique).

### **Démarches administratives**
La demande doit être déposée auprès :
- De la **mairie de résidence**,
- De la mairie de l’acte de naissance (si né en France),
- De l’**ambassade ou consulat** (si résident à l’étranger),
- De l’**OFPRA** (si bénéficiaire de la protection internationale).

**Pièces à fournir** : Formulaire rempli, daté et signé, avec justificatifs.

### **Récépissé et saisine du procureur**
L’officier d’état civil remet un **récépissé** de dépôt. En cas de **manque d’intérêt légitime**, ou si la demande concerne des **infraction terroriste, sexuelle sur mineur, violation d’une interdiction de sortie du territoire, ou inscription au Fijait/Fijaisv**, il doit saisir le **procureur de la République**. Ce dernier peut **accepter ou refuser** la demande.

### **Décision et recours**
En cas de **refus**, une **decision motivée** est notifiée. Un **recours devant le JAF** est possible, **obligatoirement avec un avocat**.

### **Mise à jour et obligations**
Une fois l’acte de naissance modifié, les **titres d’identité** (CNI, passeport) doivent être mis à jour dans un **délai de 3 mois**. Le non-respect est puni de **5 ans d’emprisonnement et 50 000 € d’amende**.

---
*Ce résumé reste strictement conforme au document original et ne contient aucune information supplémentaire.*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 347,
  "plafond_mots": 400,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé contient des inventions et des déformations. Il écrit « une decision motivée est notifiée » et ajoute « parent ou tuteur ». Il présente l'ajout ou la suppression d'un tiret comme une « modification de l'ordre des prénoms ». Il réserve la liste des bénéficiaires aux « Majeurs ». Il punit « le non-respect » du délai de 3 mois alors que le document punit l'usage d'un titre non conforme.
- `presence_elements` :
  - P1 : 1 — Les quatre catégories de bénéficiaires sont citées, mais elles sont attribuées aux seuls majeurs et la déclaration consulaire est omise.
  - P2 : 0 — Le cas du majeur sous tutelle depuis le 1er juillet 2022 et la demande par les 2 parents en cas d'autorité parentale conjointe sont absents.
  - P3 : 0 — Les types de demande et l'intérêt légitime sont présents, mais la condition de non-contrariété à l'intérêt de l'enfant et aux droits des tiers est omise.
  - P4 : 0 — Le choix de tout prénom inscrit comme prénom usuel n'est pas mentionné.
  - P5 : 0 — Les lieux de dépôt et le récépissé sont présents, mais la gratuité de la démarche est omise.
  - P6 : 1 — La saisine du procureur dans les cas prévus et sa décision d'accepter ou de refuser sont présentes, malgré l'omission de l'information du demandeur.
  - P7 : 1 — Le recours devant le JAF avec avocat obligatoire est mentionné.
  - P8 : 0 — La règle sur l'apparence physique est citée, mais la possibilité d'un prénom neutre, épicène, féminin ou masculin est omise.
  - P9 : 1 — Le délai de 3 mois pour la CNI et le passeport et les peines sont mentionnés, bien que l'infraction sanctionnée soit déformée.
- Inventions : « une decision motivée est notifiée » : le caractère motivé de la décision n'est pas dans le document; « parent ou tuteur » : le tuteur n'est pas mentionné pour les mineurs; « Une modification de l'ordre des prénoms (ex. : ajout ou suppression d'un tiret) » : confusion entre deux éléments distincts; « Le non-respect est puni de 5 ans d'emprisonnement » : la peine vise l'usage d'un titre non conforme, et il s'agit d'un maximum; « OFPRA (si bénéficiaire de la protection internationale) » : le document vise le titulaire d'un certificat tenant lieu d'acte de naissance; « L'officier d'état civil remet un récépissé » : l'auteur de la remise n'est pas précisé dans le document; Conditions d'éligibilité attribuées aux seuls « Majeurs »
- Confiance : haute

**Juge second** : non-juge (limite-debit)

## RE-012 (RE, difficile)

### Entrée

```text
{
  "consigne": "Fais un résumé détaillé de ce document, en 400 mots au plus, pour un couple qui veut se pacser en mairie.",
  "document": "Vous voulez conclure un pacte civil de solidarité (Pacs) ? C’est possible que vous soyez en couple de même sexe ou de sexe différent, et quelle que soit votre nationalité. Le Pacs est un contrat (aussi appelé convention ), signé par vous deux, qui organise votre vie commune (participation aux charges communes, etc.). Votre Pacs doit être enregistré (gratuit) en mairie ou, si vous résidez à l’étranger, dans une ambassade ou un consulat. Vous pouvez aussi faire appel à un notaire (payant). Nous vous guidons dans les étapes de votre démarche.\n\nVoici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Vérifier les conditions à remplir pour se pacser\n- Réunir les documents à fournir dans son dossier de Pacs\n- Rédiger son contrat de Pacs\n- Déposer son dossier et faire enregistrer son Pacs en mairie\n- Identifier l’ambassade ou le consulat auquel s’adresser\n- Déposer son dossier et faire enregistrer son Pacs auprès de l’ambassade ou du consulat\n- Rédiger son contrat de Pacs avec le notaire\n- Faire enregistrer le contrat de Pacs par le notaire\nVous devez faire enregistrer votre Pacs à la mairie qui sera (ou est déjà) celle de votre résidence commune. Certaines démarches peuvent varier selon les communes (par exemple, nombre de rendez-vous). La démarche en mairie est gratuite.\nChacun de vous 2 doit remplir toutes les conditions suivantes :\n- Être majeur\n- N'être ni marié, ni pacsé\n- Ne pas avoir de lien familial direct ou trop proche avec l'autre partenaire.\n(À savoir: Si l'un de vous est étranger , vous devez avoir l' âge de la majorité fixée par votre pays .)\nCes conditions sont impératives. Une dispense n'est pas possible, même de façon exceptionnelle.\nEn vous pacsant, vous vous engagez à une vie commune. Vous devez choisir une résidence commune. Vous déclarez votre adresse commune par une attestation sur l'honneur. Vous n'êtes pas obligés de vivre ensemble au moment de la déclaration de Pacs. L'adresse déclarée devient votre adresse commune dès l'enregistrement du Pacs.\nVous devez rédiger et signer un contrat de Pacs (aussi appelé convention de Pacs ). Il peut également être rédigé par un notaire. Un seul contrat de Pacs doit être rédigé pour vous 2. Le contrat doit être rédigé en français et comporter vos 2 signatures. Vous pouvez choisir le contenu de votre contrat de Pacs en fonction de votre situation (de vos niveaux de revenus respectifs, par exemple) et de vos patrimoines. Vous pouvez opter pour une convention minimale ou personnaliser votre convention en fonction de votre situation :\nCas Contrat de Pacs minimal: Le contrat de Pacs doit constater l'engagement et la volonté d'être liés par un Pacs. Il doit obligatoirement reprendre le texte suivant : Nous, X et Y, concluons un pacte civil de solidarité régi par les dispositions de la loi du 15 novembre 1999 modifiée et les articles 515-1 à 515-7 du code civil. En l'absence de précisions contraires dans le Pacs, vos patrimoines sont séparés : c'est le régime légal de séparation. (À noter: Pour le mariage, le régime légal est différent. C'est la communauté réduite aux acquêts .)\n Vous pouvez utiliser une convention-type (formulaire cerfa n°15726) :\nCas Contrat de Pacs personnalisé: Un seul contrat de Pacs doit être rédigé pour vous 2. Le contrat de Pacs doit constater l'engagement et la volonté d'être liés par un Pacs. Il doit obligatoirement reprendre le texte suivant : Nous, X et Y, concluons un pacte civil de solidarité régi par les dispositions de la loi du 15 novembre 1999 modifiée et les articles 515-1 à 515-7 du code civil. Le contrat précise les conditions de participation de chacun de vous 2 à la vie commune. Vous pouvez choisir de partager la propriété de certains biens que vous allez acquérir, ensemble ou séparément (régime de l'indivision ). En l'absence de précisions contraires dans le Pacs, vos patrimoines sont séparés (c'est le régime légal de séparation). (À noter: Pour le mariage, le régime légal est différent. C'est la communauté réduite aux acquêts .)\n Vous pouvez utiliser une convention-type (formulaire cerfa n°15726) : Vous pouvez aussi rédiger votre propre contrat . Si besoin, vous pouvez vous informer gratuitement dans une maison de la justice et du droit. Vous pouvez aussi prendre les conseils d'un notaire ou d'un avocat spécialisé.\nVous devez faire enregistrer votre Pacs par l'officier d'état civil (en mairie) de la commune de résidence commune.\nDans certaines communes, vous pouvez déposer une pré-demande de Pacs. Pour vérifier si votre commune vous permet d’effectuer une pré-demande de Pacs en ligne, vous pouvez utiliser le téléservice suivant : Vous devez vous connecter avec votre compte Service Public par identifiants (mail et mot de passe) ou par FranceConnect. Si votre commune vous propose ce service, vous pouvez effectuer la démarche avec le même téléservice.\nL'enregistrement se fait en général sur rendez-vous. (À savoir: Le service peut exiger que le dépôt du dossier se fasse avant l’enregistrement du Pacs, dans certains cas sur rendez-vous. Un autre rendez-vous sera fixé pour l'enregistrement du Pacs.)\nPour l'enregistrement de votre Pacs, vous devez vous présenter en personne et ensemble à l'officier d'état civil de la mairie où vous déposez votre Pacs. (À noter: En cas d'empêchement grave de l'un de vous 2, l'officier d'état civil peut se déplacer à votre domicile ou à l’hôpital pour enregistrer le Pacs.)\nL'officier d'état civil enregistre d'abord votre déclaration de Pacs. Il ne garde pas de copie de la convention. Elle vous est restituée. Vous devez donc conserver soigneusement votre convention de Pacs. (Attention: En cas de perte de votre Pacs, vous ne pourrez pas obtenir de copie de votre convention. L'officier de l'état civil pourra vous fournir uniquement une copie du récépissé d'enregistrement (sur présentation d'une pièce d'identité).)\nSavoir comment récupérer une convention de Pacs si vous avez perdu votre convention initiale: Vous avez besoin de votre convention de Pacs pour déterminer le régime applicable à vos biens (par exemple, en vue d'un achat immobilier ou de la transmission d'un bien), mais vous ne disposez plus de votre convention. Dans ce cas, vous pouvez effectuer une déclaration conjointe de modification de Pacs. Rédigez une nouvelle convention, en indiquant les références du Pacs initial (numéro et date d'enregistrement). Ces références se trouvent sur le récépissé d'enregistrement de votre Pacs initial et sur votre acte de naissance. Cette convention modificative sera enregistrée par l’officier d’état civil de l'ambassade ou du consulat. Puis elle vous sera restituée comme la convention initiale.\nVotre Pacs produit ses effets entre vous 2 à partir de la date de son enregistrement. Pour les tiers, votre Pacs produit ses effets à partir des dates suivantes :\n- Indication en marge sur l'acte de naissance si vous êtes né en France\n- Inscription sur le registre des Pacs des étrangers nés à l'étranger si vous êtes de nationalité étrangère né à l'étranger.\nL'officier d'état civil transmet l’information aux services de l’état civil. Votre Pacs est indiqué en marge sur l'acte de naissance de chacun de vous 2. Si vous êtes étranger né à l'étranger, l'information est enregistrée sur le registre des Pacs des étrangers nés à l'étranger détenu par le service central d'état civil du ministère des affaires étrangères. Vous pouvez apporter la preuve de l'enregistrement de votre Pacs par l'un des moyens suivants :\n- Mention figurant sur votre acte de naissance (établi en France)\n- Récépissé d'enregistrement remis par l'officier d'état civil\n- Visa figurant sur la convention de Pacs\n- Attestation de Pacs établie par le service central d'état civil du ministère des affaires étrangères, si vous êtes étranger et né à l'étranger.",
  "nb_mots": 1233
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
      "texte": "Le Pacs, ouvert aux couples de même sexe ou de sexe différent quelle que soit la nationalité, est un contrat qui organise la vie commune ; il est enregistré gratuitement en mairie (ou à l'ambassade ou au consulat pour un couple résidant à l'étranger), ou par un notaire (payant)"
    },
    {
      "ref": "P2",
      "texte": "Il est enregistré à la mairie de la résidence commune ; certaines démarches varient selon les communes"
    },
    {
      "ref": "P3",
      "texte": "Conditions impératives, sans dispense possible : être majeur, n'être ni marié ni pacsé, ne pas avoir de lien familial direct ou trop proche avec l'autre ; un étranger doit avoir l'âge de la majorité fixé par son pays"
    },
    {
      "ref": "P4",
      "texte": "Les partenaires s'engagent à une vie commune et déclarent sur l'honneur une résidence commune, sans obligation de vivre ensemble au moment de la déclaration"
    },
    {
      "ref": "P5",
      "texte": "Un seul contrat pour les deux, rédigé en français, signé par les deux et reprenant obligatoirement la formule légale ; convention minimale ou personnalisée (cerfa n°15726 possible) ; à défaut de précision, les patrimoines sont séparés (indivision possible)"
    },
    {
      "ref": "P6",
      "texte": "Pré-demande en ligne dans certaines communes ; enregistrement en général sur rendez-vous, en présence des deux partenaires en personne et ensemble (déplacement possible de l'officier d'état civil en cas d'empêchement grave)"
    },
    {
      "ref": "P7",
      "texte": "L'officier d'état civil enregistre la déclaration sans garder de copie de la convention, qui est restituée et doit être conservée ; en cas de perte, seule une copie du récépissé est délivrée, et une convention modificative est possible"
    },
    {
      "ref": "P8",
      "texte": "Le Pacs produit ses effets entre les partenaires dès l'enregistrement, et à l'égard des tiers à partir de la mention en marge de l'acte de naissance (ou de l'inscription au registre des Pacs des étrangers nés à l'étranger)"
    },
    {
      "ref": "P9",
      "texte": "Preuve de l'enregistrement : mention sur l'acte de naissance, récépissé d'enregistrement, visa sur la convention, ou attestation du service central d'état civil pour un étranger né à l'étranger"
    }
  ],
  "longueur_demandee": "detaillee"
}
```

### Sortie (statut ok)

```text
**Résumé détaillé pour un couple souhaitant se pacser en mairie (400 mots max.)**

### **Conditions pour conclure un Pacs**
Pour se pacser, vous devez être :
- **Majeur** (ou âgé de la majorité fixée par votre pays si vous êtes étranger).
- **En couple de même ou de sexe différent**, sans lien familial direct ou trop proche.
- **Ni marié ni pacsé** précédemment.

### **Étapes et documents nécessaires**
1. **Rédiger le contrat de Pacs** :
   - **Contrat minimal** (formulaire Cerfa n°15726) : engagement légal de séparation de patrimoines par défaut.
   - **Contrat personnalisé** : possibilité de préciser les règles de partage des biens (indivision) ou d’autres dispositions (ex. : participation aux charges).
   - Le contrat doit être **rédigé en français** et signé par les deux partenaires.

2. **Démarches en mairie** :
   - **Déposer le dossier** (pré-demande possible dans certaines communes via un téléservice en ligne, sous réserve de disponibilité).
   - **Prendre rendez-vous** pour l’enregistrement, généralement sur rendez-vous.
   - **Se présenter en personne** à l’officier d’état civil de la mairie de votre **résidence commune** (attestation sur l’honneur à fournir).
   - **Conserver soigneusement la convention** signée (la mairie ne conserve pas une copie).

3. **Enregistrement** :
   - L’officier d’état civil enregistre votre Pacs et vous remet un **récépissé** (preuve de l’enregistrement).
   - **Effets juridiques** : le Pacs prend effet à partir de la date d’enregistrement. Pour les tiers, il est notifié sur :
     - Votre **acte de naissance** (marge indiquant le Pacs).
     - Le **registre des Pacs** (si vous êtes étranger né à l’étranger).

### **Cas particuliers**
- **Perte de la convention** : Une **déclaration modificative** (nouveau contrat) peut être établie pour retrouver les détails du Pacs initial (sur présentation du récépissé et de l’acte de naissance).
- **Empêchement grave** : En cas d’impossibilité de se présenter, l’officier peut se déplacer à votre domicile ou à l’hôpital.

### **Régime juridique**
- **Par défaut** : séparation de patrimoines (sauf si le contrat prévoit une autre disposition, comme l’indivision).
- **Différence avec le mariage** : le Pacs ne crée pas de communauté réduite aux acquêts.

### **Coût et modalités**
- **Gratuit** en mairie.
- **Option payante** : possibilité de faire rédiger le contrat par un **notaire** (coût variable).

---
*Ce résumé couvre les obligations, délais et documents essentiels pour un Pacs en mairie.*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 339,
  "plafond_mots": 400,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé déforme et ajoute des informations absentes du document : « Ni marié ni pacsé précédemment », « coût variable » pour le notaire, « sur présentation du récépissé et de l'acte de naissance » et « délais ».
- `presence_elements` :
  - P1 : 0 — La gratuité en mairie, l'option payante du notaire et l'ouverture aux couples de même sexe ou de sexe différent sont citées, mais la nationalité indifférente et l'ambassade ou le consulat sont omis.
  - P2 : 1 — Le résumé indique « mairie de votre résidence commune » et signale une pré-demande possible « dans certaines communes ».
  - P3 : 1 — Les conditions de majorité (y compris pour les étrangers), d'absence de mariage ou de Pacs et d'absence de lien familial sont reprises, sans toutefois préciser qu'aucune dispense n'est possible.
  - P4 : 0 — Seule l'attestation sur l'honneur est citée ; l'engagement à une vie commune et l'absence d'obligation de vivre ensemble manquent.
  - P5 : 1 — Le contrat minimal ou personnalisé, le cerfa n°15726, la rédaction en français, la double signature, la séparation des patrimoines par défaut et l'indivision sont mentionnés ; la formule légale obligatoire est omise.
  - P6 : 1 — La pré-demande en ligne, le rendez-vous, la présence en personne et le déplacement de l'officier en cas d'empêchement grave sont présents.
  - P7 : 1 — Le résumé précise que la mairie ne conserve pas de copie, qu'il faut conserver la convention et qu'une déclaration modificative est possible en cas de perte.
  - P8 : 1 — Les effets à partir de l'enregistrement et, pour les tiers, la mention en marge de l'acte de naissance ou le registre des étrangers nés à l'étranger sont repris.
  - P9 : 0 — Seul le récépissé est présenté comme preuve ; le visa sur la convention, la mention sur l'acte de naissance et l'attestation du service central ne sont pas cités comme preuves.
- Inventions : « Ni marié ni pacsé précédemment » (le document n'exige pas de ne jamais l'avoir été); « coût variable » pour le notaire; « sur présentation du récépissé et de l'acte de naissance » / « pour retrouver les détails du Pacs initial »; « Ce résumé couvre les obligations, délais et documents essentiels » (aucun délai dans le document)
- Confiance : moyenne
