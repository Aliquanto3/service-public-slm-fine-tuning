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
Si votre enfant est nouveau dans un établissement, vous devez participer à une réunion d'information dans les jours qui suivent la rentrée scolaire. Des réunions peuvent aussi être organisées au cours de l'année scolaire, notamment pour vous informer sur la situation de la classe, sur une procédure spécifique ou sur les possibilités d'orientation. Si votre enfant est en grande difficulté scolaire, son établissement peut également vous convier à des réunions pour envisager ensemble des solutions. Si vous rencontrez un problème lié à la pédagogie, adressez-vous au professeur principal de la classe. Si votre problème concerne les absences et les questions de comportement, adressez-vous au conseiller principal d'éducation (CPE). Le chef d'établissement et les enseignants doivent faire le nécessaire pour répondre à vos demandes d'information et de rendez-vous. Tout réponse négative doit présenter les motifs.

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
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 0,
  "mots_texte": 135,
  "rappel": 0.8333,
  "taux_hors_faute": 0.0
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

À la suite de la réunion du comité social territorial du 15 octobre, le télétravail sera ouvert aux agents du service urbanisme dont les missions le permettent. Chaque agent pourra télétravailler un jour par semaine, choisit en accord avec son responsable. Les jours de permanence au guichet, le mardi et le jeudi, ne pourront pas être télétravailler.

Les demandes devront être adressé au service des ressources humaines avant le 13 novembre, au moyen du formulaire joint. Un ordinateur portable et un casque sera remis à chaque agent dont la demande aura été acceptée. Les agents s'engagent à rester joignables pendant les plages fixes, de 9 heures à 12 heures et de 14 heures à 16 heures.

Une période d'adaptation de trois mois est prévue. À l'issue de cette période, un bilan sera fait avec chaque agent afin de vérifier que l'organisation retenue convient à la fois à l'agent et au service.

La direction générale des services

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 4,
  "fautes": 8,
  "fautes_corrigees": [
    true,
    false,
    false,
    false,
    false,
    true,
    true,
    true
  ],
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 0,
  "mots_texte": 174,
  "rappel": 0.5,
  "taux_hors_faute": 0.0
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
Si vous êtes admis à un concours d’accès à la fonction publique et si vous étiez auparavant dirigeant d’une société ou d’une association à but lucratif, vous pouvez continuer à exercer cette activité de dirigeant pendant 1 an, renouvelable une fois, à partir de votre recrutement dans la fonction publique. Cela s’applique également si vous êtes recruté en temps que contractuel dans la fonction publique. Vous devez présenter une déclaration écrite à votre autorité hiérarchique de votre nomination en tant que fonctionnaire stagiaire ou avant la signature de votre contrat. Votre déclaration mentionne la forme et l’objet social de l’entreprise ou de l’association, son secteur et son branche d’activité. La poursuite de cette activité de dirigeant doit être compatible avec vos obligations de service. Elle ne doit pas porter atteinte au fonctionnement normal, à l’indépendance, à la neutralité du service ou aux principes déontologiques. Cette activité ne doit pas non plus vous placer dans une situation de conflit d’intérêts.

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
    true,
    true,
    true,
    true,
    false,
    false,
    true,
    false,
    true,
    true,
    true
  ],
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 1,
  "mots_texte": 159,
  "rappel": 0.75,
  "taux_hors_faute": 0.0063
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
**Compte rendu de point hebdomadaire de service**

**Objet de la réunion et participants**
La réunion avait pour objet l’organisation et la planification des activités de nettoyage urbain et de gestion des dépôts sauvages. Les participants étaient :
- R. Duquesne, responsable du service propreté et animateur ;
- P. Ribeiro, cheffe d’équipe du secteur nord ;
- G. Tessier, cheffe d’équipe du secteur sud ;
- K. Bouaziz, agent de maîtrise, atelier véhicules ;
- Mme Loiseau, adjointe au maire cadre de vie.

**Points abordés**
1. **Dépôts sauvages rue du Moulin-Brûlé**
   - Un dépôt en 15 jours (gravats et électroménager) a été enlevé par l’équipe nord, accompagné de deux rotations de camion.
   - Mme Loiseau a proposé l’installation d’une caméra pour identifier l’auteur des dépôts sauvages. Cette proposition a été rejetée, car la vidéoprotection est assurée par la police municipale et le délibéré du conseil.
   - Duquesne transmet les photos et le numéro d’un courrier retrouvé dans les gravats à la police municipale pour identifier l’auteur.
   - Loiseau a proposé l’organisation d’un article dans le bulletin municipal sur les dépôts sauvages et la déchèterie, mais cette initiative n’a pas été menée.

2. **Balayeuse n°2 en panne**
   - La pièce commandée a été identifiée comme une pompe hydraulique HS, avec un délai de fournisseur de trois semaines.
   - Duquesne a décidé de louer une balayeuse de remplacement pour trois semaines, avec un devis annoncé. Bouaziz a confirmé la réservation de la balayeuse de location, livraison prévue au plus tard le jeudi 1er octobre.

3. **Plan feuilles mortes**
   - Un décret a été pris pour le démarrage du ramassage des feuilles mortes le lundi 12 octobre. Deux agents en renfort ont été pris sur les espaces verts, accord obtenu avec le chef des espaces verts.
   - Tessier a réalisé un planning des circuits de ramassage, priorisant les abords écoles et pistes cyclables, à présenter au point hebdo du lundi 5 octobre.
   - Ribeiro a proposé de tester le broyage des feuilles pour paillage, mais cette initiative n’a pas été adoptée cette année, avec une éventuelle mise en œuvre en 2027.

4. **Cimetière / Toussaint**
   - Un nettoyage renforcé des allées et abords du cimetière a été décidé pour la semaine du 26 octobre, avant le 1er novembre. G. Tessier a coordonné cette opération avec le conservateur du cimetière.

5. **Tags école Jean-Moulin**
   - Les tags signalés sur le mur côté cour ont été traités par l’équipe sud, avec l’hydrogommeuse, avant le vendredi 2 octobre.

6. **Divers / sécurité**
   - Ribeiro a signalé la présence de deux agents sans gilets haute visibilité neufs. Duquesne a transmis la commande d’EPI cette semaine.
   - Tessier a demandé l’utilisation des horaires d’hiver dès octobre, au lieu du 1er décembre, mais cette proposition n’a pas été approuvée, car l’avis du CST est nécessaire.

**Décisions prises**
- La location d’une balayeuse de remplacement pour trois semaines a été approuvée, avec une livraison prévue.
- Le ramassage des feuilles mortes a été mis en place le lundi 12 octobre, avec deux agents en renfort.
- Le nettoyage renforcé des allées et abords du cimetière a été fixé pour la semaine du 26 octobre.
- Les tags école Jean-Moulin ont été traités avant le vendredi 2 octobre.

**Actions à mener**
| Action | Responsable | Échéance |
|--------|-------------|-----------|
| Transmettre les photos et le numéro d’un courrier retrouvé dans les gravats à la police municipale pour identifier l’auteur des dépôts sauvages | R. Duquesne | Aucune indication

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0.5 — La location pour trois semaines figure, mais le montant de 2 040 € HT et l'imputation sur le budget de fonctionnement manquent (« avec un devis annoncé »).
  - D2 : 1 — Le démarrage au lundi 12 octobre et les deux agents en renfort pris sur les espaces verts sont mentionnés.
  - D3 : 1 — Le nettoyage renforcé de la semaine du 26 octobre, avant le 1er novembre, est présent, même si l'équipe sud n'est pas explicitement rattachée à la décision.
  - A1 : 0.5 — L'action et son responsable (R. Duquesne) figurent, mais l'échéance est donnée comme « Aucune indication » alors que les notes indiquent « aujourd'hui ».
  - A2 : 1 — Bouaziz et la livraison au plus tard le jeudi 1er octobre sont mentionnés, bien que l'action soit formulée au passé (« a confirmé la réservation »).
  - A3 : 1 — Tessier, le planning des circuits et sa présentation au point du 5 octobre sont présents, mais l'action est présentée à tort comme réalisée (« a réalisé un planning »).
  - A4 : 1 — La coordination de Tessier avec le conservateur est mentionnée, sans échéance à fixer, mais au passé (« a coordonné »).
  - A5 : 0.5 — L'intervention de l'équipe sud à l'hydrogommeuse avant le 2 octobre figure, mais le responsable G. Tessier n'est pas indiqué.
  - A6 : 1 — La commande d'EPI par Duquesne cette semaine est mentionnée, au passé (« a transmis la commande »).
- `absence_invention` : 0 — Le compte rendu contient des éléments absents des notes ou contraires à elles : « Un dépôt en 15 jours » au lieu du 3e, « Un décret a été pris », les tags présentés comme une décision déjà traitée, et des actions futures présentées comme accomplies.
- `structure` : 1 — Les sections Participants, Points abordés, Décisions prises et Actions à mener sont présentes, même si le tableau des actions est tronqué après la première ligne.
- Inventions : « Un dépôt en 15 jours » alors que les notes indiquent le 3e dépôt en 15 jours; « Un décret a été pris » pour le ramassage des feuilles; « Les tags école Jean-Moulin ont été traités avant le vendredi 2 octobre » présenté comme une décision accomplie; « Tessier a réalisé un planning » alors qu'il reste à faire; « G. Tessier a coordonné cette opération » présenté comme déjà fait; « Duquesne a transmis la commande d'EPI » présenté comme déjà fait; « Cette proposition a été rejetée » (caméra) alors que les notes disent seulement « Pas décidé »; Échéance de A1 donnée comme « Aucune indication » au lieu de « aujourd'hui »; « G. Tessier, cheffe d'équipe » au lieu de chef d'équipe
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
**Compte rendu de la réunion de l'équipe pluridisciplinaire RSA**

**Objet de la réunion et participants**
La réunion avait pour objet d’examiner six dossiers de situations sociales au RSA. Les participants étaient :
- La présidente du conseil départemental, présidente par délégation ;
- Un représentant de France Travail ;
- Une assistante sociale de la Maison départementale des solidarités (MDS) ;
- Un représentant des allocataires ;
- Un représentant de l’Atelier du Pont ;
- Le secrétaire de l’équipe pluridisciplinaire ;
- Une conseillère en insertion du département, excusée en raison d’une formation.

**Points abordés**

1. **Dossier de Mme L. D.** (41 ans, parcours social, réorientation vers le parcours professionnel, suivi par France Travail)
   - La demande a été évoquée, avec un parcours social actuel et un parcours professionnel en cours.
   - Les difficultés de santé de l’année dernière ont été mentionnées, ainsi que le logement réglé.
   - La référente de la MDS a indiqué que l’allocataire souhaitait retravailler dans l’aide à domicile.
   - Un permis de conduire n’ayant pas été obtenu, un avis favorable a été rendu pour la réorientation, suivi par France Travail.

2. **Dossier de M. K. A.** (56 ans, parcours professionnel, réorientation vers le parcours social, suivi par la MDS)
   - L’allocataire était hébergé chez un ami, perdu son logement et présentait des problèmes de santé non traités.
   - Il était assidu aux rendez-vous, mais un référent social de la MDS n’avait pas été désigné sous un mois.
   - Un avis favorable a été rendu pour la réorientation, suivi par la MDS.

3. **Dossier de M. R. S.** (29 ans, parcours professionnel, dossier de manquement)
   - Deux rendez-vous non honorés et zéro heure d’activité prévues à son contrat d’engagement depuis juin.
   - Un courrier lui avait été envoyé pour présenter ses observations, sans réponse.
   - Un signal a été émis, avec une suspension-remobilisation de 30 % pendant un mois, levée dès la reprise de contact.
   - Un avis défavorable a été exprimé, avec une tentative de joindre l’allocataire avant la décision.

4. **Dossier de Mme F. M.** (34 ans, parcours social, absences aux ateliers collectifs)
   - Des absences ont été signalées, mais un justificatif de hospitalisation a été reçu.
   - Un avis de maintien du RSA, sans sanction, a été rendu.

5. **Dossier de M. J.-P. V.** (47 ans, parcours professionnel, absence des heures d’activité en août)
   - L’allocataire avait commencé une mission d’intérim, ce qui a justifié son absence aux ateliers.
   - Un avis de maintien du RSA, sans réduction, a été rendu, avec la mise à jour du contrat d’engagement.

6. **Dossier de Mme N. R.**
   - L’allocataire avait reçu sa convocation, mais n’avait pas pu se libérer.
   - Le dossier a été reporté à la prochaine équipe pluridisciplinaire.

**Décisions prises**

- **Mme L. D.** : Réorientation vers le parcours professionnel, suivi par France Travail.
- **M. K. A.** : Réorientation vers le parcours social, suivi par la MDS.
- **M. R. S.** : Suspension-remobilisation de 30 % pendant un mois, levée dès la reprise de contact.
- **Mme F. M.** : Maintien du RSA, sans sanction.
- **M. J.-P. V.** : Maintien du RSA, sans réduction, avec mise à jour du contrat d’engagement.
- **Mme N. R.** : Reconvoque à temps, avec possibilité d’accompagnement.

**Actions à mener**

| Responsable                  | Action                                                                 | Échéance       |
|-------------------------------|------------------------------------------------------------------------|-----------------|
| M. Faure                     | Transmettre l’avis de maintien du RSA pour M. J.-P. V.              | Avant le jeudi 15 octobre |
| M. Gal

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Le compte rendu indique un « avis favorable a été rendu pour la réorientation, suivi par France Travail » ; seule l'unanimité n'est pas précisée.
  - D2 : 1 — Le compte rendu indique un « avis favorable a été rendu pour la réorientation, suivi par la MDS ».
  - D3 : 0.5 — La suspension-remobilisation de 30 % pendant un mois, levée dès la reprise de contact, figure bien, mais « Un avis défavorable a été exprimé » est ambigu : ni la majorité ni M. Gallet ne sont mentionnés.
  - D4 : 1 — Le compte rendu mentionne « Un avis de maintien du RSA, sans sanction, a été rendu » après réception du justificatif.
  - D5 : 1 — Le compte rendu mentionne « Un avis de maintien du RSA, sans réduction, a été rendu » après la mission d'intérim.
  - D6 : 0.5 — Le report « à la prochaine équipe pluridisciplinaire » est mentionné, mais sans la date du 15 octobre, et la section Décisions indique seulement « Reconvoque à temps ».
  - A1 : 0 — La désignation d'un conseiller France Travail et le premier rendez-vous avant le 16 octobre sont absents.
  - A2 : 0 — Le compte rendu déforme l'engagement en un constat (« un référent social de la MDS n'avait pas été désigné sous un mois ») au lieu d'une action confiée à Mme Nkomo.
  - A3 : 0.5 — La « tentative de joindre l'allocataire avant la décision » est mentionnée, mais sans responsable (M. Faure) ni échéance (18 septembre).
  - A4 : 0 — La réinscription de Mme F. M. aux ateliers d'octobre n'est pas mentionnée.
  - A5 : 0.5 — La « mise à jour du contrat d'engagement » est citée sans responsable ; la ligne attribuée à M. Faure porte sur une autre action (« Transmettre l'avis »).
  - A6 : 0.5 — La mention « Reconvoque à temps » ne donne ni responsable (Mme Jacquet) ni échéance (30 septembre).
  - A7 : 0 — La transmission des avis au service RSA d'ici le 25 septembre est absente (tableau tronqué).
- `absence_invention` : 0 — Le compte rendu invente « La présidente du conseil départemental, présidente par délégation » ainsi que l'action « M. Faure – Transmettre l'avis de maintien du RSA pour M. J.-P. V. – Avant le jeudi 15 octobre », qui ne figure pas dans les notes.
- `structure` : 1 — Les sections Participants, Points abordés, Décisions et Actions sont présentes, même si le tableau des actions est tronqué.
- Inventions : La présidente du conseil départemental, présidente par délégation (Mme Aubertin préside par délégation du président, elle n'est pas présidente du conseil départemental); M. Faure : Transmettre l'avis de maintien du RSA pour M. J.-P. V. avant le jeudi 15 octobre (action inexistante); Un référent social de la MDS n'avait pas été désigné sous un mois (déformation d'un engagement en constat); Un avis défavorable a été exprimé (dossier M. R. S., présenté de façon ambiguë)
- Confiance : moyenne

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
**Compte rendu de la réunion publique de concertation**

**Objet de la réunion et participants**
La réunion avait pour objet de discuter de la mise en place d’un projet visant à redonner envie de venir dans le bourg, notamment en améliorant la RD 812, la place de la Halle (parking six jours sur sept, commerces fermés) et les trottoirs peu larges. Les participants étaient :
- M. Bernard Lacoste (maire),
- Mme Isabelle Fauré (1re adjointe à l’urbanisme),
- M. Didier Roucayrol (adjoint au commerce et à l’artisanat),
- Mme Anne Teyssier (directrice générale des services),
- Mme Solène Marquet (paysagiste-urbaniste, cheffe de projet, Atelier Paysage & Territoires),
- M. Hugo Brissac (ingénieur VRD, Atelier Paysage & Territoires),
- Mme Lucie Garrigues (conseillère municipale d’opposition),
- M. Gérard Pons (riverain rue de la République),
- M. Jean-Marc Cazals (boulanger, président de l’union commerciale Valbrézac Commerces),
- Mme Odile Vergnes (présidente du club des aînés),
- M. Kevin Lafarge (association Valbrézac à vélo),
- Mme Martine Delpech (riveraine de la place de la Halle),
- Mme Fatima Ould-Ali (parent d’élève, école du Bourg),
- Mme Sandrine Mathieu (assistante maternelle),
- M. Lucien Arnal (maraîcher, exposant du marché),
- Plusieurs habitants non identifiés.

**Points abordés**
1. **Cadre du projet** : Le centre-bourg, notamment la RD 812, la place de la Halle (parking six jours sur sept, commerces fermés) et les trottoirs peu larges, a été identifié comme un secteur à améliorer. Le projet vise à redonner envie de venir dans le bourg.
2. **Diagnostic du périmètre d’étude** :
   - La RD 812 a été identifiée comme un secteur à améliorer, avec un nombre élevé de véhicules et de poids lourds.
   - La place de la Halle a été identifiée comme un secteur à améliorer, avec un nombre élevé de places de stationnement et de commerces fermés.
   - Les trottoirs de la rue de la République ont été identifiés comme souvent moins larges et non conformes pour les personnes à mobilité réduite.
   - Les platanes ont été identifiés comme présentant des signes de faiblesse, dont un regard visuel non phytosanitaire.
3. **Trois scénarios proposés** :
   - **Scénario A** (plus ambitieux) : place de la Halle entièrement piétonne (64 places supprimées), parking de 30 places derrière la poste (terrain de l’ancienne coopérative, à acquérir), rue de la République en sens unique (1,80 mètre), 2,4 millions d’euros hors taxes.
   - **Scénario B** (place partagée) : 22 places conservées, espace piéton avec terrasses, bancs, plantations, traversée en zone de rencontre (20 km/h, priorité aux piétons), trottoirs élargis là où possible, 1,9 million d’euros hors taxes.
   - **Scénario C** (minimal) : reprendre les trottoirs, refaire les revêtements, traversées aux normes, ne toucher pas au stationnement, 900 000 euros hors taxes.
4. **Questions posées** :
   - Abattre les platanes (diagnostic phytosanitaire nécessaire).
   - Stationnement et livraisons des commerces (commerçants craignent pour le stationnement de passage, livraisons non étudiées).
   - Sécurité devant l’école et poids lourds en transit (demande au département).
   - Sens unique de la rue de la République (opposition des riverains, pétition signée).
   - Bancs et toilettes pour les aînés.
   - Zone 30 sur toute l’agglomération (idée retenue, pas encore étudiée).
   - Halle vitrée (coût non chiffré, accord de l’architecte des Bâtiments de France nécessaire).
   - Navette gratuite le

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0 — Le scénario C est décrit, mais son abandon par la municipalité n'est jamais mentionné.
  - D2 : 0 — La prolongation du registre et de l'adresse mail jusqu'au 13 novembre est absente.
  - D3 : 0 — La balade urbaine du 17 octobre n'est pas mentionnée.
  - D4 : 0 — Le maintien du marché sur la place de la Halle est absent.
  - D5 : 0 — La création du comité de suivi est absente.
  - D6 : 0.5 — « Abattre les platanes (diagnostic phytosanitaire nécessaire) » reprend la condition, mais seulement comme question, sans la décision ni la commande du diagnostic des sept platanes.
  - D7 : 0 — Le conseil municipal du 10 décembre n'est pas mentionné.
  - D8 : 0 — La deuxième réunion publique prévue en janvier n'est pas mentionnée.
  - A1 : 0 — Aucune action de commande du diagnostic, ni responsable ni échéance.
  - A2 : 0 — Seule la mention « livraisons non étudiées » figure, sans action, responsable ni échéance.
  - A3 : 0 — Le contact du propriétaire et de l'établissement public foncier est absent.
  - A4 : 0 — « demande au département » est cité sans le courrier du maire ni son objet (déviation des poids lourds par la rocade de Fontcalm).
  - A5 : 0 — La pétition est citée, mais pas son annexion au registre par Mme Teyssier.
  - A6 : 0 — Les dossiers de subvention sont absents.
  - A7 : 0 — Le comptage du stationnement est absent.
  - A8 : 0 — La variante « B plus » est absente.
  - A9 : 0 — L'espace de jeux est absent (sortie tronquée).
  - A10 : 0 — L'organisation de la balade urbaine est absente.
  - A11 : 0 — La centralisation des candidatures au comité de suivi est absente.
  - A12 : 0 — La mise en ligne sous quinze jours est absente.
- `absence_invention` : 0 — « Zone 30 sur toute l'agglomération (idée retenue, pas encore étudiée) » présente comme retenue un élément des pièges, alors que le maire ne s'est pas engagé.
- `structure` : 0 — La sortie est tronquée (« Navette gratuite le ») et les sections Décisions et Actions sont absentes.
- Inventions : Zone 30 sur toute l'agglomération présentée comme « idée retenue »
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
**Compte rendu de réunion de chantier**

**Objet de la réunion et participants**
La réunion de chantier n°14, consacrée à la rénovation du gymnase des Aubiers, a eu lieu sur site. Les participants étaient :
- L’architecte mandataire et conducteur d’opération de l’Atelier Vernhes ;
- La commune (MOA) ;
- Les maçons de l’Atelier Lacombe ;
- L’Étanch'Ouest ;
- Les Sols & Sports Duclos.
Un membre de la CSPS a été excusé de présence.

**Points abordés**
1. **Avancement des travaux**
   - Le lot 2 (gros œuvre) : la dalle de la salle principale a été terminée, le séchage en cours, et une mesure d’humidité a été effectuée.
   - Le lot 4 (couverture-étanchéité) : la couverture est finie, mais une infiltration a été constatée côté nord après la pluie. Ce défaut a été relevé et attribué à l’Étanch'Ouest, qui l’a reconnu et a indiqué que la réparation devait être effectuée avant la prochaine réunion.
   - Le lot 7 (sols sportifs) : la pose du sol est attendue, conditionée par le séchage de la dalle (taux d’humidité inférieur à un seuil spécifique). La pose du sol prendra trois semaines.
   - Le lot 9 (électricité) : les chemins de câbles ont été posés à un taux non précisé, mais aucun planning n’a été reçu.

2. **Planning et réception**
   - Un retard cumulé a été constaté, lié au séchage de la dalle et au lot 9.
   - L’architecte mandataire a proposé de décaler la réception, mais la commune a accepté la proposition, bien que les clubs (basket, hand) devraient être prévenus rapidement. La réception a été reportée à une date ultérieure.
   - Les pénalités de retard pour le lot 9 ont été discutées, mais aucune mesure n’a été prise pour leur application.

3. **Travaux supplémentaires**
   - Deux portes coupe-feu non conformes ont été identifiées, nécessitant un devis. Le maçonnier a présenté un devis, qui a été accepté par la commune. L’architecte mandataire a indiqué que l’ordre de service sera émis avant une date ultérieure.
   - La repeinture des murs de la salle principale a été proposée, mais aucune décision n’a été prise, car le budget n’était pas disponible.

4. **Choix techniques**
   - Les coloris du sol sportif ont été validés : bleu (terrain) et gris clair (hors jeu).
   - La question de l’ajout du volley à la liste des installations (basket, hand, badminton) a été soulevée, mais la réponse n’a pas été donnée.
   - Un échantillon du revêtement a été apporté pour la prochaine réunion.

5. **Lot 9**
   - Un courrier de mise en demeure a été envoyé à l’Électricité Mérignon, en raison des absences et du manque de planning.
   - Un éclairage LED renforcé a été mentionné, demandé par les clubs pour la compétition, mais aucun devis n’a été demandé et aucune action n’a été prise.

6. **Sécurité**
   - La clôture de chantier côté parking a été déplacée, conditionée par un vent.

**Décisions prises**
- La réception du chantier a été reportée à une date ultérieure.
- Le devis pour les portes coupe-feu a été accepté, et l’ordre de service sera émis avant une date ultérieure.
- Les coloris du sol sportif ont été validés.
- Un courrier de mise en demeure a été envoyé à l’Électricité Mérignon.

**Actions à mener**
- **Responsable** : Atelier Vernhes
  **Échéance** : Avant vendredi 2/10
  **Action** : Émettre l’ordre de service pour les portes coupe-feu.

- **Responsable** : Atelier Vernhes
  **Échéance** : Avant vendredi 2/10
  **Action**

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0.5 — Le report est mentionné, mais la date du 27/11/2026 manque : « La réception du chantier a été reportée à une date ultérieure ».
  - D2 : 0.5 — L'acceptation du devis des portes coupe-feu figure, mais sans le montant de 3 840 € HT.
  - D3 : 1 — « Les coloris du sol sportif ont été validés : bleu (terrain) et gris clair (hors jeu) ».
  - A1 : 0 — La mesure d'humidité est présentée comme déjà faite (« une mesure d'humidité a été effectuée »), sans responsable ni échéance du 2/10.
  - A2 : 1 — La reprise par Étanch'Ouest avant la prochaine réunion est indiquée, même si la prise en charge à ses frais n'est pas précisée.
  - A3 : 0.5 — Le compte rendu indique que les clubs « devraient être prévenus rapidement », sans Mme Ferrand comme responsable ni l'échéance du 16/10.
  - A4 : 1 — L'action « Émettre l'ordre de service pour les portes coupe-feu » est attribuée à l'Atelier Vernhes, avant le vendredi 2/10.
  - A5 : 0 — La question du volley est seulement soulevée (« la réponse n'a pas été donnée »), sans action de consultation des clubs ni responsable.
  - A6 : 0.5 — Le texte indique « Un échantillon du revêtement a été apporté pour la prochaine réunion », une formulation confuse et sans Mme Duclos comme responsable.
  - A7 : 0.5 — Le courrier de mise en demeure est mentionné, mais présenté comme déjà envoyé, sans M. Hamon ni l'échéance « cette semaine ».
  - A8 : 0 — Seul le déplacement de la clôture est relevé ; sa remise en place par M. Lacombe le jour même est absente.
- `absence_invention` : 0 — La sortie présente comme accomplis des faits non réalisés, par exemple « une mesure d'humidité a été effectuée » et « Un courrier de mise en demeure a été envoyé », et elle classe ce courrier parmi les décisions.
- `structure` : 1 — Les quatre sections (participants, points abordés, décisions, actions) sont présentes, même si la section Actions est tronquée et la liste des participants incomplète.
- Inventions : Mesure d'humidité présentée comme déjà effectuée, alors qu'elle est prévue le 2/10; Courrier de mise en demeure présenté comme déjà envoyé et classé comme décision; « Électricité Mérignon » au lieu d'Elec Mérignon; « Atelier Lacombe » au lieu de Maçonnerie Lacombe; Seconde action dupliquée et tronquée attribuée à l'Atelier Vernhes avant le 2/10
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
**Compte rendu de la réunion du comité de pilotage du Contrat local de santé (CLS) 2024-2028 de Pontcarel**

**Objet de la réunion et participants**
La réunion avait pour objet de faire un bilan du contrat local de santé (CLS) 2024-2028, d’évaluer les pistes d’amélioration et de définir les prochaines actions. Les participants étaient :
- Le maire de Pontcarel (coprésident),
- La délégation départementale ARS (coprésidente),
- Le conseiller municipal délégué à la santé,
- La coordinatrice CLS de la ville,
- Le président de la CPTS du Haut-Pontcarel (en visio),
- La CPAM chargée de mission prévention,
- Le directeur du département, service autonomie (représentant la directrice enfance-famille-autonomie),
- La directrice adjointe du centre hospitalier de Pontcarel,
- L’association Point Écoute Jeunes (invitée pour le point 3).

**Points abordés**

1. **Bilan mi-parcours du CLS**
   Un bilan a été présenté, indiquant que 18 fiches-actions étaient en cours : 4 terminées, 11 engagées et 3 non démarrées (dont la fiche « santé des aidants » et la fiche « habitat indigne »). Les points forts identifiés étaient les ateliers nutritionnels QPV Les Coudrais et les permanences CPAM au centre commun d’accueil des personnes handicapées et personnes à besoins spécifiques (CCAS). Les points faibles concernaient l’axe santé environnement, qui était très en retard, ainsi que la faible quantité de données disponibles.

   Le maire a souhaité présenter ce bilan au conseil municipal, mais ce dernier a été reporté au 12 novembre. La coordinatrice CLS a préparé une note de synthèse pour le transmettre au cabinet du maire avant le 30 octobre. La délégation départementale a validé le bilan, indiquant qu’il n’y avait rien à redire.

2. **Accès aux soins**
   Un contexte a été évoqué concernant la départure de deux médecins généralistes du centre-ville en retraite, entraînant un manque de médecin traitant pour un certain nombre de patients. Le président de la CPTS a présenté un projet de maison de santé pluriprofessionnelle (MSP) libérale, tandis que le conseiller municipal délégué à la santé a proposé un centre de santé municipal avec médecins salariés. Le débat a révélé des divergences entre les deux propositions, notamment sur la concurrence entre MSP et centre de santé. La délégation départementale a indiqué que les deux scénarios ne s’excluaient pas forcément, mais il fallait objectiver.

   La ville a décidé de lancer une étude d’opportunité comparant les deux scénarios, avec un coût estimé. Le financement a été partagé entre la ville et la délégation départementale, dans la limite d’un montant fixé par le FIR, sous réserve de validation du dossier par le comité FIR. Le choix entre MSP et centre de santé n’a pas été tranché, et la ville a indiqué ne pas vouloir écrire qu’elle lance un centre de santé.

   La directrice adjointe du centre hospitalier a indiqué que l’hôpital pourrait mettre à disposition des consultations avancées de spécialistes dans la future structure, mais elle devait en parler à sa direction. La CPAM a proposé une campagne M'T dents dans les écoles élémentaires, avec un accord de tous les participants. Les interventions auraient lieu au 2e trimestre scolaire.

3. **Santé mentale**
   Un hôte invité a indiqué une hausse forte des demandes des 15-25 ans au Point Écoute, ainsi que des délais de consultation médicale (CMP) pour un premier rendez-vous. La directrice adjointe du centre hospitalier a confirmé les délais CMP et le problème de recrutement de psychologues et pédopsychiatre. La coordinatrice CLS a proposé de former des agents municipaux et associatifs aux Premiers secours en santé mentale (PSSM). La délégation départementale a indiqué que la création d’un conseil local de santé mentale (CLSM) n’avait

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0.5 — La sortie indique seulement que « La délégation départementale a validé le bilan » : la validation à l'unanimité des membres présents du COPIL n'apparaît pas.
  - D2 : 0.5 — L'étude d'opportunité est mentionnée, mais sans le montant de 28 000 € TTC ni le cofinancement de 50 % dans la limite de 15 000 € (« avec un coût estimé »).
  - D3 : 0 — La sortie est tronquée au point 3 : la décision des 2 sessions PSSM (24 personnes, 6 000 € ARS) n'est pas mentionnée, seule la proposition l'est.
  - D4 : 0 — Le point 4 est absent : la reconduction des ateliers nutrition n'est pas mentionnée.
  - D5 : 0 — La campagne d'information sur le moustique tigre est absente.
  - D6 : 0 — L'accord de principe sur l'avenant n° 1 est absent.
  - A1 : 1 — « La coordinatrice CLS a préparé une note de synthèse pour le transmettre au cabinet du maire avant le 30 octobre » : le responsable et l'échéance sont présents.
  - A2 : 0 — Le montage et le dépôt du dossier FIR par Mme Benamar avant le 13 novembre ne sont pas mentionnés.
  - A3 : 0.5 — La campagne M'T dents et l'échéance du 2e trimestre scolaire sont citées, mais l'action d'organisation par Mme Ricard avec les directeurs d'école (CP, 2 écoles du QPV) n'est pas clairement attribuée.
  - A4 : 0 — Cette action est absente (sortie tronquée).
  - A5 : 0 — Cette action est absente.
  - A6 : 0 — Cette action est absente.
  - A7 : 0 — Cette action est absente.
  - A8 : 0 — Cette action est absente.
  - A9 : 0 — Cette action est absente.
  - A10 : 0 — Cette action est absente.
- `absence_invention` : 0 — Plusieurs éléments ne figurent pas dans les notes, par exemple « ce dernier a été reporté au 12 novembre » (il s'agissait d'une correction de date, pas d'un report), « centre commun d'accueil des personnes handicapées... (CCAS) », « Le directeur du département » ou l'attribution à l'ARS d'une position sur le CLSM.
- `structure` : 0 — Les sections Décisions et Actions sont absentes : seules « Objet de la réunion et participants » et « Points abordés » figurent, et la sortie est tronquée.
- Inventions : Conseil municipal « reporté au 12 novembre » (les notes indiquent une simple correction de date, pas un report); CCAS développé en « centre commun d'accueil des personnes handicapées et personnes à besoins spécifiques »; M. Vasseur présenté comme « Le directeur du département, service autonomie »; « La coordinatrice CLS a préparé une note de synthèse » : action présentée comme déjà réalisée; CMP développé en « consultation médicale »; Position sur le CLSM attribuée à la délégation départementale (ARS), alors que c'est le maire qui a différé; « Le financement a été partagé entre la ville et la délégation départementale » : formulation présentant le cofinancement comme acquis
- Confiance : haute

**Juge second** : juge

- `presence_elements` :
  - D1 : 1 — La décision de validation du bilan à mi-parcours est correctement mentionnée.
  - D2 : 0.5 — L'étude d'opportunité est mentionnée, mais le cofinancement ARS sous réserve du comité FIR n'est pas précisé (piège).
  - D3 : 1 — Les sessions PSSM sont correctement décrites avec leur financement.
  - D4 : 1 — La reconduction des ateliers nutrition est correctement mentionnée avec le financement CPAM.
  - D5 : 1 — La campagne moustique tigre est correctement mentionnée.
  - D6 : 0.5 — L'accord de principe pour l'avenant est mentionné, mais pas le fait qu'il n'est pas encore adopté (piège).
  - A1 : 1 — L'action de préparation de la note de synthèse est correctement mentionnée avec responsable et échéance.
  - A2 : 0.5 — L'action de dépôt du dossier FIR est mentionnée, mais sans préciser l'appui de l'ARS (responsable incomplet).
  - A3 : 1 — L'action M'T dents est correctement mentionnée avec responsable et échéance.
  - A4 : 0.5 — L'action PSSM est mentionnée, mais sans échéance précise (prochain COPIL).
  - A5 : 0.5 — L'action de contact avec l'infirmière scolaire est mentionnée, mais sans responsable précis (Benamar implicite).
  - A6 : 1 — La campagne moustique tigre est correctement mentionnée avec responsable et échéance.
  - A7 : 0.5 — L'état des lieux qualité de l'air est mentionné, mais sans échéance (non fixée dans les références).
  - A8 : 0.5 — La rédaction de la fiche-action est mentionnée, mais sans préciser que Vasseur et Benamar en sont responsables.
  - A9 : 0 — L'envoi du sondage pour le prochain COPIL n'est pas mentionné.
  - A10 : 0 — La diffusion du compte rendu n'est pas mentionnée.
- `absence_invention` : 0 — Plusieurs inventions : mention du 'centre commun d’accueil des personnes handicapées et personnes à besoins spécifiques (CCAS)' au lieu de CCAS seul ; 'campagne M'T dents dans les écoles élémentaires' sans préciser les 2 écoles du QPV ; absence de mention des pièges (ex. : choix non tranché entre MSP et centre de santé).
- `structure` : 0 — Les quatre sections requises (Participants, Points abordés, Décisions, Actions) ne sont pas clairement distinguées. La section 'Décisions' est absente en tant que telle.
- Inventions : Mention du 'centre commun d’accueil des personnes handicapées et personnes à besoins spécifiques (CCAS)' au lieu de CCAS seul; Campagne M'T dents sans préciser les 2 écoles du QPV; Absence de mention explicite des pièges (ex. : choix non tranché entre MSP et centre de santé)
- Confiance : moyenne

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
**Compte rendu de la réunion de gestion annuel**

**Objet de la réunion et participants**
La réunion avait pour objet de discuter de l’évolution des indicateurs du Compte Précautionnel de l’Autonomie et de la situation financière et tarifaire du service, ainsi que des demandes de l’association. Les participants étaient :
- La directrice de l’autonomie du département ;
- Le chef du service tarification et contrôle et la chargée de tarification du département ;
- Le président, la directrice et le responsable administratif et financier de l’association.

**Points abordés**
1. **Indicateurs du CPOM** :
   - Le volume d’heures réalisées et l’objectif fixé.
   - Le taux de rotation du personnel d’intervention.
   - Le délai moyen de démarrage d’une intervention.
   - Les heures non réalisées et les réclamations écrites.

2. **Situation financière et tarif** :
   - Le déficit de l’exercice 2025 du service.
   - La question de la reprise du déficit par le département.
   - Le tarif 2027 et son éventuelle majoration pour les zones éloignées.

3. **Demandes de l’association** :
   - La question des véhicules de service pour les intervenantes sans ou en mauvais état.
   - Une aide pour la formation des intervenantes à l’accompagnement des personnes atteintes de troubles cognitifs.

**Décisions prises**
1. **Objectif des heures réalisées** :
   - L’objectif a été ramené à 150 000 heures par an pour 2026 et 2027, conformément à la rythme actuel.

2. **Délai de démarrage d’intervention** :
   - L’objectif de 7 jours a été maintenu, mais calculé à partir de la réception de la notification par le service, et non de la date de décision du plan d’aide.

3. **Retrait des communes de l’association** :
   - Il a été constaté que le retrait de Saint-Fulbert et des Granges-Hautes de la zone d’intervention de l’association n’était pas possible, car le service était le seul service dans ces communes.

4. **Plan de retour à l’équilibre** :
   - Un plan de retour à l’équilibre a été engagé pour 2027 et 2028, avec une échéance fixée avant le lundi 16 novembre.

5. **Dotation complémentaire** :
   - Un avenant n° 2 a été proposé pour intégrer la dotation complémentaire de 3 euros par heure au CPOM, conditionné à l’assurance des interventions les dimanches et jours fériés et à la mise en place d’actions de lutte contre l’isolement.

6. **Co-financement des véhicules de service** :
   - Le département a décidé de co-financer la location de quatre véhicules de service en 2027, dans la limite de 12 000 euros, dans la mesure où la location de six véhicules de service n’était pas possible.

7. **Aide pour la formation des intervenantes** :
   - Une aide pour la formation des intervenantes à l’accompagnement des personnes atteintes de troubles cognitifs a été évoquée, mais aucune action concrète n’a été prise.

**Actions à mener**
| **Action**                          | **Responsable**                          | **Échéance**          |
|-------------------------------------|------------------------------------------|------------------------|
| Rédiger le projet d’avenant n° 2   | Chef du service tarification et contrôle | Avant le vendredi 30 octobre |
| Envoyer les devis pour la location de véhicules de service | Responsable administratif et financier | Avant le 16 novembre   |
| Envoyer le relevé de conclusions   | Chargée de tarification                 | Sous huit jours       |
| Fixer la date de la revue intermédiaire | Chargée de tarification                 | Plus tard              |

**Points ambigus ou incomplets**
- La majoration du tarif 2027 pour les zones éloignées n’a pas été définie.
- La question de la formation des intervenantes à l’accompagnement des personnes atteintes de troubles cognitifs n’a pas donné de réponse concrète.
- La date de la revue intermédiaire du CPOM n

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « L'objectif a été ramené à 150 000 heures par an pour 2026 et 2027 ».
  - D2 : 1 — Objectif de 7 jours maintenu, calculé « à partir de la réception de la notification par le service ».
  - D3 : 1 — Le retrait de Saint-Fulbert et des Granges-Hautes est présenté comme « pas possible ».
  - D4 : 0 — Le suivi trimestriel du taux de rotation et des heures non réalisées n'apparaît nulle part.
  - D5 : 0 — La reprise du déficit n'est citée que comme « question » dans les points abordés ; ni le refus ni le montant de 84 000 € ne figurent.
  - D6 : 1 — Le plan de retour à l'équilibre 2027-2028 est mentionné avec l'échéance « avant le lundi 16 novembre ».
  - D7 : 0.5 — L'avenant n° 2 et ses deux conditions sont cités, mais pas les réserves d'approbation par le CA de l'association et par la commission permanente du 7 décembre.
  - D8 : 0.5 — Quatre véhicules dans la limite de 12 000 € sont mentionnés, mais le taux de cofinancement de 50 % est omis.
  - A1 : 0 — L'envoi de la procédure de raccordement à la notification dématérialisée est absent.
  - A2 : 0 — Le recalcul du délai du premier semestre 2026 par M. Kerbrat est absent.
  - A3 : 0 — L'étude d'une majoration n'apparaît que comme point ambigu, sans action ni responsable.
  - A4 : 0 — L'envoi du premier tableau trimestriel au 15 janvier 2027 est absent.
  - A5 : 0.5 — L'échéance du plan est donnée, mais les responsables (Mme Roux-Delattre et M. Kerbrat) ne sont pas indiqués.
  - A6 : 1 — « Rédiger le projet d'avenant n° 2 » est attribué au chef du service tarification, avant le vendredi 30 octobre.
  - A7 : 0 — L'inscription de l'avenant à la commission permanente du 7 décembre est absente.
  - A8 : 0 — L'approbation de l'avenant par le CA de l'association est absente.
  - A9 : 1 — Les devis des véhicules sont attribués au responsable administratif et financier, avant le 16 novembre.
  - A10 : 1 — La date de la revue intermédiaire est attribuée à la chargée de tarification, « plus tard » (échéance non fixée).
  - A11 : 1 — L'envoi du relevé de conclusions est attribué à la chargée de tarification, sous huit jours.
- `absence_invention` : 0 — Le sigle CPOM est développé en « Compte Précautionnel de l'Autonomie », dénomination absente des notes et inventée.
- `structure` : 1 — Les sections Participants, Points abordés, Décisions et Actions sont présentes, bien que la sortie soit tronquée à la fin.
- Inventions : « Compte Précautionnel de l'Autonomie » (développement inventé du sigle CPOM)
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
**[Adresse du demandeur]**
**[Commune]**
**[Référence du dossier]**
**[Date du courrier]**

**Objet : Demande d’aide exceptionnelle au paiement d’une facture d’énergie : pièces manquantes**

**Objet de la demande**
Je vous adresse ce courrier pour solliciter l’aide exceptionnelle au paiement d’une facture d’énergie, ainsi que les pièces manquantes à fournir.

**Description de la situation**
J’ai reçu, le [Date de réception], un accusé de réception du CCAS concernant une facture d’énergie. J’ai demandé l’aide exceptionnelle au paiement de cette facture, mais certaines pièces manquantes m’ont été signalées.

**Pièces manquantes à fournir**
Pour finaliser ma demande d’aide exceptionnelle, je vous serais gré de bien vouloir m’envoyer les pièces manquantes suivantes :
- [Copie de la facture d’énergie concernée]
- [Justificatifs des ressources du foyer des trois derniers mois]

**Délai de réponse**
Le CCAS a indiqué un délai de 15 jours à compter de la réception de ce courrier pour fournir ces pièces manquantes. Le silence gardé pendant deux mois sur la demande vaut, selon le service, décision de rejet.

**Signataire**
[Nom et qualité du signataire]

**CCAS**
[Adresse, téléphone et courriel du CCAS]

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Adresse du demandeur]": true,
    "[Adresse, téléphone et courriel du CCAS]": true,
    "[Commune]": true,
    "[Date du courrier]": true,
    "[Nom et qualité du signataire]": true,
    "[Référence du dossier]": true
  },
  "emplacements_reussis": true
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Le courrier est rédigé du point de vue du demandeur, qui écrit au CCAS (« Je vous adresse ce courrier pour solliciter l'aide… je vous serais gré de bien vouloir m'envoyer les pièces manquantes »), ce qui rend le registre inadapté ; de nombreux éléments obligatoires manquent en outre : en-tête du CCAS, bloc destinataire « M. Julien Petitjean », formule d'appel « Monsieur, », rappel de la réception le 30 septembre 2026, mention de la suspension du délai de rejet implicite et de la fin de cette suspension, et formule de politesse.
- Inventions : Emplacement non demandé [Date de réception] alors que la date de réception (30 septembre 2026) était fournie.; Inversion de la situation : l'accusé de réception aurait été reçu par le demandeur à une date inconnue, et c'est le demandeur qui demande au CCAS de lui envoyer les pièces.
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
**[Adresse de la candidate]**
**[Commune]**
**[Date du courrier]**

**[Adresse de l'hôtel de ville]**

**Objet : Convocation à un entretien de recrutement**

Madame Élodie Garcia,

Je vous écris pour vous confirmer la convocation à un entretien de recrutement, qui se tiendra le [date entretien].

**Dernière confirmation** : Veuillez confirmer votre présence avant le [28 octobre 2026].

**Duree et heure** : L’entretien durera environ 30 minutes, à [heure].

**Lieu** : Salle du conseil, [lieu].

**Poste** : Agent d’accueil et d’état civil (catégorie C), à temps complet.

**Service** : Service des ressources humaines.

**Jury** : Le directeur général des services et la responsable des ressources humaines.

**Documents à apporter** :
- Pièce d’identité
- Copie des diplômes

**Téléphone et courriel du service des ressources humaines** : [Téléphone et courriel du service des ressources humaines].

Je reste à votre disposition pour tout renseignement complémentaire.

**[Nom et qualité du signataire]**
Service des ressources humaines
[Service]

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Adresse de l'hôtel de ville]": true,
    "[Adresse de la candidate]": true,
    "[Commune]": true,
    "[Date du courrier]": true,
    "[Nom et qualité du signataire]": true,
    "[Téléphone et courriel du service des ressources humaines]": true
  },
  "emplacements_reussis": true
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : pas d'en-tête d'expéditeur (mairie, service des ressources humaines), pas de bloc destinataire nommant Mme Élodie Garcia, une formule d'appel non conforme (« Madame Élodie Garcia, » au lieu de « Madame, »), une date et une heure fournies mais remplacées par « [date entretien] » et « [heure] », un lieu incomplet (« Salle du conseil, [lieu] ») et aucune formule de politesse (« Je reste à votre disposition… » n'en tient pas lieu).
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
**[Adresse de l'association]**
[Commune]
[Date du courrier]

**Objet : Communication des procès-verbaux et du budget de la commune**

Madame, Monsieur,

Je vous écris pour vous informer des procès-verbaux et du budget de la commune, ainsi que de l’availability de ces documents.

**1. Procès-verbaux des séances du conseil municipal**
Les procès-verbaux des séances du conseil municipal de 2025 sont disponibles pour consultation sur place au secrétariat général aux heures d’ouverture, ou par envoi d’une copie sur demande écrite. Vous pouvez les consulter [Horaires d’ouverture du secrétariat général].

**2. Budget primitif 2026**
Le budget primitif 2026 de la commune est également disponible pour consultation sur place au secrétariat général aux heures d’ouverture, ou par envoi d’une copie sur demande écrite.

**3. Publication dans la lettre d’information**
L’association « Vivre au village » peut obtenir les procès-verbaux et le budget primitif 2026, et les publier dans sa lettre d’information, sous réserve de leur consultation sur place au secrétariat général.

**Service concerné :**
Sécrétariat général de la mairie.

**[Téléphone et courriel du secrétariat général]**

**[Nom et qualité du signataire]**
Service public de la commune.

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

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : pas d'en-tête de l'expéditeur ni de bloc destinataire nommant l'association et Mme Sandrine Morel (seul « [Adresse de l'association] » figure), formule d'appel « Madame, Monsieur, » au lieu de « Madame, », aucun rappel du droit de toute personne physique ou morale prévu par l'article L. 2121-26, aucune mention de la communication auprès des services déconcentrés de l'État, et aucune formule de politesse ; le registre est en outre défaillant (« l'availability de ces documents », « Sécrétariat »).
- Inventions : « sous réserve de leur consultation sur place au secrétariat général » : condition à la publication non prévue par l'article L. 2121-26, qui relève des restrictions interdites.; « Service public de la commune. » : mention de signature non fournie dans l'entrée.
- Confiance : haute

**Juge second** : juge

- `conformite` : 1 — Un élément obligatoire manque : la référence explicite au droit de toute personne physique ou morale de demander communication des documents (article L. 2121-26 du CGCT). De plus, la formule d'appel 'Madame, Monsieur' est incorrecte (devrait être 'Madame,'), et la mention 'Service public de la commune' en signature est inadaptée (emplacement non respecté).
- Inventions : L'expression 'availability de ces documents' est incorrecte et inventée.; La restriction 'sous réserve de leur consultation sur place au secrétariat général' pour la publication est une invention non prévue par les références.; La mention 'Service public de la commune' en signature est une invention.
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
**Voici votre RSA : un texte simplifié pour vous**

**Non, vous ne pouvez pas percevoir le RSA si vous êtes étudiant.**

**Mais vous pouvez le demander dans 2 cas :**

1. **Vous êtes jeune actif** (18 à 25 ans) et avez travaillé **au moins 2 ans** (3 214 heures) dans un emploi à temps plein** (un emploi à temps plein, ou un ensemble d’emplois qui compte comme un seul) dans les 3 ans précédant votre demande.

2. **Vous êtes parent isolé** (vivez seul(e) avec un ou plusieurs enfants à charge).

**Vos autres obligations :**
- Vous devez résider en France **stable et effective** (au moins 9 mois par année civile).
- Vos ressources ne doivent pas dépasser un plafond, qui dépend de la composition de votre foyer.

**Un simulateur vous aide :**
- Pour vérifier si vous avez droit au RSA.
- Pour estimer son montant.
*Note : Le montant sera plus faible si vous bénéficiez déjà de l’**ARE** (Allocation Chômage d’Aide au Retour à l’Emploi).*

---
*Passage conservé sans modification (termes juridiques obligatoires) :*
*« Allocation Chômage d’Aide au Retour à l’Emploi (ARE) »*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 7.085,
  "km_entree": 77.32,
  "km_sortie": 84.405
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie ajoute une précision absente de l'entrée : « (un emploi à temps plein, ou un ensemble d'emplois qui compte comme un seul) ». Selon la grille, tout ajout d'information entraîne la note 0, même si les 7 informations à conserver sont présentes.
- `termes_juridiques` : 1 — Les cinq termes à conserver figurent tous dans la sortie : RSA, jeune actif, parent isolé, enfants à charge et « ARE (Allocation Chômage d'Aide au Retour à l'Emploi) ».
- `clarte_percue` : 3 — La structure en listes aide à la lecture, mais plusieurs éléments gênent : la tournure fautive « résider en France stable et effective », un astérisque de gras orphelin, la parenthèse inventée qui embrouille, un titre maladroit (« Voici votre RSA ») et une note méta inutile pour l'usager.
- Inventions : (un emploi à temps plein, ou un ensemble d'emplois qui compte comme un seul)
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
**Votre coût de la convention de Pacs**

Le prix de votre contrat de Pacs (convention de Pacs) dépend de la façon dont vous l’écrivez :

- **Vous écrivez la convention avec votre futur partenaire** :  
  Aucun frais n’est à payer.

- **Vous faites appel à un notaire** :  
  Le coût de la rédaction de votre contrat par un notaire est de **101,41 € TTC** (TTC = Taux d’Importation et Taux de Vente, c’est le prix à payer pour l’acte notarié).  
  Ce coût est le même pour la modification de votre Pacs.  
  **Il faut aussi payer un droit d’enregistrement de 125 €** (un frais fixe pour l’enregistrement de l’acte notarié dans les registres officiels).

**Coûts supplémentaires** :  
Des frais peuvent s’ajouter, comme :
- Les émoluments de formalités (copies notariées de la convention, transcription sur les actes d’état civil des partenaires).
Ces frais sont fixés par le tarif des notaires.

---
*Passage conservé sans modification (termes juridiques obligatoires) :*  
*« TTC » (Taux d’Importation et Taux de Vente), *« actes d’état civil »* (les documents officiels qui prouvent la naissance, le mariage, etc. d’un couple).

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 7.7892,
  "km_entree": 71.12,
  "km_sortie": 78.9092
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie ajoute une information fausse : « TTC = Taux d'Importation et Taux de Vente », alors que TTC signifie « toutes taxes comprises ». Elle ajoute aussi une précision invérifiable, « enregistrement de l'acte notarié dans les registres officiels ». Les montants et conditions sont pourtant conservés.
- `termes_juridiques` : 1 — Les sept termes à conserver sont présents et non remplacés : Pacs, convention de Pacs, notaire, droit d'enregistrement, émoluments de formalités, actes d'état civil, tarif des notaires.
- `clarte_percue` : 3 — La structure en cas distincts est claire. En revanche, la fausse définition de TTC induit en erreur, « émoluments de formalités » n'est pas expliqué, et la note finale « Passage conservé sans modification » est confuse pour un usager.
- Inventions : TTC = Taux d'Importation et Taux de Vente, c'est le prix à payer pour l'acte notarié; un frais fixe pour l'enregistrement de l'acte notarié dans les registres officiels; les documents officiels qui prouvent la naissance, le mariage, etc. d'un couple
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
**Faut-il faire une déclaration en cas de perte ou de vol du livret de famille ?**

Non, il n’est pas obligatoire de faire une déclaration en cas de perte ou de vol de votre livret de famille. Cependant, pour limiter les risques de fraude, il est fortement recommandé de le faire en vous rendant au commissariat de police ou à la brigade de gendarmerie. Un récépissé vous sera remis.

---
*Passage conservé sans modification (termes juridiques obligatoires) :*
*« Le livret est fourni par la mairie qui conserve l'acte de mariage ou, pour les livrets de parents naturels, l'acte de naissance du 1er enfant et est complété par tous les officiers de l'état civil détenant un acte dont un extrait doit y figurer. Une mention "second livret" doit être inscrite sur la première page. En cas de détérioration de votre 1er livret de famille, celui-ci peut être remplacé. Vous devrez le présenter à la mairie pour en obtenir une reproduction (duplicata). (À savoir: Lorsqu'un livret devenu inutilisable est échangé contre un second, il doit être remis à l'officier pour être détruit. Mais si vous manifestez un attachement à ce document, il pourra vous être laissé après qu'une mention "annulé" ait été apposée sur chaque page.) »*

---
**Si vous êtes les parents et cherchez un second livret de famille, voici ce que vous devrez fournir :**

1. **Justificatif de votre identité** (p. ex. passeport, carte d'identité, titre de séjour, etc.).
2. **Justificatif de domicile** (p. ex. titre de propriété, avis d'imposition, certificat de non-imposition, quittance de loyer, facture d'assurance du logement, facture de gaz, d'électricité ou de téléphone).
3. **Informations sur les actes du livret à reconstituer** :
   - Nom, prénoms, date et lieu de naissance de chaque personne (et date et lieu du mariage, si vous vous êtes mariés).

---
**Si vous êtes tuteur d'un mineur, ajoutez deux documents supplémentaires :**

1. **Décision de justice** qui prouve que vous êtes le tuteur.
2. **Acte de naissance** de votre mineur.

Dans ce cas, le second livret est établi par reconstitution. Le livret est fourni par la mairie qui conserve l'acte de mariage (pour les livrets de parents naturels, l'acte de naissance du 1er enfant). Le livret est complété par tous les officiers de l'état civil détenant un acte dont un extrait doit y figurer. Une mention *« second livret »* doit être inscrite sur la première page.

---
**Si votre 1er livret de famille est détériorisé, celui-ci peut être remplacé.** Vous devrez le présenter à la mairie pour en obtenir une reproduction (duplicata). (À savoir: Lorsqu'un livret devenu inutilisable est échangé contre un second, il doit être remis à l'officier pour être détruit. Mais si vous manifestez un attachement à ce document, il pourra vous être laissé après qu'une mention *« annulé »* ait été apposée sur chaque page.)

---
**Délai et délivrance :**
- Le délai varie selon le nombre d'actes à inscrire sur le livret. En général, cela prend quelques semaines.
- Vous pourrez retirer le second livret sur présentation d'une pièce d'identité auprès de la mairie où vous avez fait votre demande (mairie du lieu de votre domicile).
- La délivrance d'un second livret de famille est **gratuite**.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 3.5976,
  "km_entree": 66.64,
  "km_sortie": 70.2376
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie ajoute des exemples absents du texte source (« p. ex. passeport, carte d'identité, titre de séjour, etc. ») et transforme une possibilité en obligation : « peuvent vous être demandés » devient « voici ce que vous devrez fournir ».
- `termes_juridiques` : 1 — Les sept termes à conserver figurent tous dans la sortie : livret de famille, récépissé, tuteur, décision de justice, reconstitution, officiers de l'état civil et duplicata.
- `clarte_percue` : 2 — Un long passage technique est recopié tel quel puis répété plus loin (« Passage conservé sans modification… »), des phrases complexes restent intactes et une faute apparaît (« détériorisé ») ; cela gêne la compréhension d'un usager.
- Inventions : Exemples de justificatifs d'identité : « p. ex. passeport, carte d'identité, titre de séjour, etc. »; Obligation de fournir les pièces (« vous devrez fournir ») au lieu de « peuvent vous être demandés »
- Confiance : haute

**Juge second** : juge

- `fidelite` : 2 — Toutes les informations à conserver sont présentes et exactes, sans ajout ni suppression. Les nuances (ex. : 'fortement recommandé', 'mention « second livret »') sont fidèlement restituées.
- `termes_juridiques` : 1 — Tous les termes juridiques à conserver sont présents et non remplacés à tort, y compris les passages explicitement cités comme devant être conservés sans modification.
- `clarte_percue` : 5 — La structure en listes, les exemples concrets (p. ex. types de justificatifs) et la mise en forme facilitent la compréhension immédiate pour un usager sans connaissance administrative.
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
**Voici votre texte réécrit en langage clair :**

---

**Où puis-je payer la cantine de mon enfant ?**

Oui, vous pouvez obtenir des aides pour payer la cantine de votre enfant, sous certaines conditions. Les options dépendent du niveau de scolarisation de votre enfant :
- **Primaire** (maternelle et élémentaire) : les tarifs sont fixés par la commune.
- **Collège ou lycée** : les tarifs sont fixés par le département (collège) ou la région (lycée).

**Pour les enfants scolarisés en primaire :**
- La commune peut appliquer un *quotient familial* (un système qui ajuste le tarif selon vos revenus et vos charges) au tarif du repas.
- Dans certaines communes, vous pouvez bénéficier d’aides pour payer les frais de cantine. **Renseignez-vous auprès de votre mairie.**
- Vous pouvez aussi vous rapprocher de l’*assistante sociale scolaire* (une personne qui vous aide à trouver les aides).

**Pour les enfants scolarisés en collège ou lycée :**
- Si votre enfant est scolarisé dans une école éloignée de chez vous et qu’il doit rester à la cantine, vous pouvez bénéficier d’une aide. **Renseignez-vous auprès du directeur d’école en début d’année scolaire.**

---

**Qu’est-ce que le *fonds social pour les cantines* au collège et au lycée ?**

Le *fonds social pour les cantines* est une aide financière du collège ou du lycée, que vous pouvez obtenir pour payer la cantine de votre enfant. Pour l’obtenir :
- **Collège** : vous adressez votre demande à l’*assistante sociale du collège* ou au *secrétariat de l’établissement scolaire*.
- **Lycée** : vous adressez votre demande à l’*assistante sociale du lycée* ou au *secrétariat de l’établissement scolaire*.

L’*assistante sociale* vous informe en début d’année scolaire des conditions d’attribution de ce fonds social.

**Tarifs et aides :**
- Les tarifs de la cantine sont fixés par le département (collège) ou la région (lycée).
- Le département ou la région peut appliquer un *quotient familial* au tarif du repas, pour l’ajuster selon vos revenus et vos charges.
- Dans certaines départements ou régions, vous pouvez bénéficier d’aides pour payer les frais de cantine. **Renseignez-vous auprès de votre collectivité (département ou région).**

---
**Passage conservé sans modification (termes juridiques obligatoires) :**
*Le fonds social pour les cantines* est une aide financière du collège ou du lycée que vous pouvez obtenir pour payer la cantine de votre enfant. Vous devez pour cela vous adresser à l’*assistante sociale du collège ou du lycée ou au secrétariat de l’établissement scolaire*. L’*assistante sociale* vous informe en début d’année scolaire des conditions d’attribution de ce fonds social.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 1.7263,
  "km_entree": 65.57,
  "km_sortie": 67.2963
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations sont modifiées ou supprimées : l'aide pour une école élémentaire éloignée est déplacée dans la partie « collège ou lycée », sans la condition « dans certains départements ». La phrase « L'aide est attribuée par le chef d'établissement » disparaît, et l'information sur les conditions est attribuée à tort à l'assistante sociale (« L'assistante sociale vous informe en début d'année scolaire des conditions d'attribution »).
- `termes_juridiques` : 0 — Le terme « chef d'établissement » est absent : il est remplacé à tort par « assistante sociale », alors que les autres termes (quotient familial, fonds social pour les cantines, assistante sociale scolaire) sont conservés.
- `clarte_percue` : 2 — La mise en forme aide la lecture, mais le titre « Où puis-je payer la cantine de mon enfant ? » est hors sujet, les informations sont mal classées et le passage final, présenté à tort comme « conservé sans modification », répète le texte et sème la confusion.
- Inventions : L'aide pour une école éloignée du domicile s'appliquerait aux enfants scolarisés en collège ou lycée (l'entrée parle d'école élémentaire, dans certains départements).; L'assistante sociale informerait en début d'année des conditions d'attribution du fonds social (selon l'entrée, c'est le chef d'établissement).; Le passage final est annoncé comme « conservé sans modification » alors qu'il est modifié par rapport à l'entrée.; Titre « Où puis-je payer la cantine de mon enfant ? » sans correspondance dans l'entrée.
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
**Articles réécrits pour un usager**

---

**Article L131-1**
*Les demandes d’admission à l’aide sociale*

*Texte réécrit :*
*Les demandes d’admission à l’aide sociale (sauf celles pour l’aide sociale à l’enfant) sont déposées au centre communal ou intercommunal d’action sociale (CCIAS) ou, s’il n’y a pas de CCIAS, à la mairie de résidence de l’intéressé.*
*Un dossier est établi par le CCIAS (ou la mairie, si le CCIAS n’y a pas de présence).*
*Les demandes sont transmises, dans un mois, au représentant de l’État ou au président du conseil départemental (CD), qui les examine. Ce dernier peut aussi consulter le maire et le conseil municipal, si l’intéressé a demandé cette consultation.*

*Passage conservé sans simplification (termes juridiques obligatoires) :*
*« centre communal ou intercommunal d'action sociale (CCIAS) »* (termes juridiques obligatoires).

---

**Article L264-1**
*Les personnes sans domicile stable*

*Texte réécrit :*
*Les personnes sans domicile stable (sans domicile fixe) doivent choisir un lieu de domicile auprès d’un CCIAS ou d’un organisme agréé pour cela.*
*Le CCIAS ou l’organisme agréé est celui dans le ressort duquel l’intéressé a élu domicile.*
*Les prestations sociales (allocation personnalisée d’autonomie, prestation de compensation du handicap, revenu de solidarité active) sont attribuées dans le département dans lequel l’intéressé a élu domicile.*

*Passage conservé sans simplification (termes juridiques obligatoires) :*
*« prestations sociales légales, réglementaires et conventionnelles »* (termes juridiques obligatoires).
*« allocation personnalisée d’autonomie, prestation de compensation du handicap, revenu de solidarité active »* (termes juridiques obligatoires).

---
*Note :* Les termes juridiques conservés (CCIAS, prestations sociales, etc.) sont restés tels quels, car ils sont des termes obligatoires dans le code.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 2.8102,
  "km_entree": 48.65,
  "km_sortie": 51.4602
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations obligatoires sont supprimées ou modifiées : la réserve de l'article L. 252-1, les visiteurs-enquêteurs, l'avis du CCAS/CIAS, les droits visés (droits civils, titre d'identité, listes électorales, aide juridictionnelle) et le délai « dans le mois de leur dépôt » devenu « dans un mois » ; la condition de consultation est faussée (« si l'intéressé a demandé cette consultation ») ; « Le CCIAS ou l'organisme agréé est celui dans le ressort duquel… » remplace à tort l'organisme compétent pour attribuer la prestation ; un rôle de la mairie est ajouté.
- `termes_juridiques` : 0 — « visiteurs-enquêteurs », « aide juridictionnelle » et « département débiteur » sont absents, et « élire domicile » est remplacé par « choisir un lieu de domicile » dans la première phrase.
- `clarte_percue` : 2 — Le texte reste jargonneux (« dans le ressort duquel », « l'intéressé ») ; l'acronyme inventé « CCIAS » et la phrase incohérente sur le CCIAS embrouillent un usager non initié.
- Inventions : Acronyme « CCIAS », qui n'existe pas (les sigles usuels sont CCAS et CIAS); « Un dossier est établi par le CCIAS (ou la mairie, si le CCIAS n'y a pas de présence) » : rôle de la mairie ajouté; « si l'intéressé a demandé cette consultation » : la demande émane en réalité du maire ou du CCAS/CIAS; « Ce dernier peut aussi consulter le maire » : la consultation du maire est présentée comme facultative, alors que son avis intervient à défaut du CCAS/CIAS; « Le CCIAS ou l'organisme agréé est celui dans le ressort duquel l'intéressé a élu domicile »; Équivalence « sans domicile stable (sans domicile fixe) »; Sigle « CD » pour conseil départemental; Affirmation que les termes conservés sont « obligatoires dans le code »
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
**Articles réécrits pour un usager**

---

**Article L2192-10**
Les pouvoirs qui accordent des marchés (y compris les entités qui agissent en tant qu’*entités adjudicatrices*) doivent payer les sommes dues en principal dans un délai fixé par le marché, ou, si le marché ne précise pas, dans un délai fixé par la réglementation (ce délai peut varier selon le type de pouvoir).  
*Termes juridiques conservés* : *entités adjudicatrices*, *pouvoirs adjudicateurs*.

---

**Article R2192-10**
Le délai de paiement pour les pouvoirs adjudicateurs (y compris les entités adjudicatrices) est de **trente jours**.

---

**Article R2192-11**
Le délai de paiement est fixé différemment selon le type de pouvoir :
1. **Cinquante jours** pour les établissements publics de santé et les établissements du service de santé des armées.
2. **Soixante jours** pour les entreprises publiques (définition de *entreprises publiques* : *établissements publics* au sens de l’ordonnance n° 2004-503 du 7 juin 2004 portant transposition de la directive 80/723/ CEE relative à la transparence des relations financières entre les Etats membres et les entreprises publiques), à l’exception des établissements publics locaux.

---

**Article L2192-12**
Le retard de paiement se produit si les sommes dues au créancier (qui a payé ses obligations) ne sont pas versées par le pouvoir adjudicateur :
- à l’échéance prévue par le marché, ou
- à l’expiration du délai de paiement.

---

**Article L2192-13**
Dès le lendemain de l’expiration du délai de paiement ou de l’échéance, le retard de paiement fait courir **des intérêts moratoires** (intérêts liés à un retard de paiement) :
- **Dès le lendemain de l’expiration**, le taux des intérêts est fixé par la réglementation.
- Le créancier peut demander :
  - une **indemnité forfaitaire** (montant fixé par la réglementation) pour frais de recouvrement (délai de paiement retardé), et
  - une **indemnisation complémentaire** (montant fixé par la réglementation) si les frais de recouvrement dépasse l’indemnité forfaitaire.

---

**Article R2192-31**
Le taux des intérêts moratoires est :
- **Égal au taux d’intérêt appliqué par la Banque centrale européenne** à ses opérations principales de refinancement les plus récentes, en vigueur au **premier jour du semestre de l’année civile** au cours duquel les intérêts moratoires ont commencé à courir.
- **Majoré de huit points de pourcentage**.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 10.4419,
  "km_entree": 50.13,
  "km_sortie": 60.5719
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs éléments sont supprimés ou modifiés. La règle selon laquelle le délai prévu par le marché ne peut pas dépasser le délai réglementaire a disparu. Le caractère automatique (« de plein droit et sans autre formalité ») devient « Le créancier peut demander ». La condition « sur justification » a disparu. Le créancier « qui a rempli ses obligations » devient « qui a payé ses obligations ». Enfin, la sortie ajoute « (montant fixé par la réglementation) » pour l'indemnisation complémentaire.
- `termes_juridiques` : 0 — « de plein droit » est supprimé. « pouvoirs adjudicateurs » est remplacé par « Les pouvoirs qui accordent des marchés » dans L2192-10, alors que la sortie prétend l'avoir conservé. « indemnité forfaitaire pour frais de recouvrement » est mal expliquée par « (délai de paiement retardé) ».
- `clarte_percue` : 2 — La mise en forme aide, mais le texte reste confus pour un usager. Il garde la longue référence à l'ordonnance, répète « Dès le lendemain » et contient des parenthèses erronées ou peu claires.
- Inventions : indemnisation complémentaire « (montant fixé par la réglementation) »; définition des entreprises publiques comme « établissements publics » au sens de l'ordonnance n° 2004-503; « Le créancier peut demander » une indemnité forfaitaire (caractère automatique supprimé); « (délai de paiement retardé) » comme explication des frais de recouvrement; créancier « qui a payé ses obligations »
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
**Calcul :**

1. **Total des demandes reçues en mars** : 240.
2. **Pourcentage de demandes incomplètes** : 15 %.
3. **Nombre de demandes incomplètes** :
   - 15 % de 240 = (15/100) × 240 = 0,15 × 240 = **36**.
4. **Nombre de demandes complètes** :
   - Total des demandes – Nombre de demandes incomplètes = 240 – 36 = **204**.

**Réponse** : 204 demandes étaient complètes.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse donne le bon résultat final (« 204 demandes étaient complètes »), l'étape intermédiaire juste (« 15 % de 240 = … = 36 ») et est rédigée en français correct, ce qui respecte les trois critères.
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
Voici les conditions à remplir pour être tiré au sort comme juré d'assises, selon les règles de l’article 5 de la Loi sur l’instruction des affaires pénales (LIIP) :

1. **Être majeur** (au moins 18 ans).
2. **Être âgé de 18 à 40 ans** (pour les jurés d’assises, l’âge minimum est 18, l’âge maximum n’est pas fixé, mais l’âge de 40 ans est souvent mentionné dans les textes).
3. **Être sans faute** (aucune infraction récente, notamment pour les jurés d’assises, il faut être sans infraction récente, et pour les jurés de cour, sans infraction récente).
4. **Être sans délai de justice** (aucune infraction récente, et pour les jurés d’assises, il faut être sans infraction récente, et pour les jurés de cour, sans infraction récente).
5. **Être sans délai de justice** (aucune infraction récente, et pour les jurés d’assises, il faut être sans infraction récente, et pour les jurés de cour, sans infraction récente).
6. **Être sans délai de justice** (aucune infraction récente, et pour les jurés d’assises, il faut être sans infraction récente, et pour les jurés de cour, sans infraction récente).
7. **Être sans délai de justice** (aucune infraction récente, et pour les jurés d’assises, il faut être sans infraction récente, et pour les jurés de cour, sans infraction récente).
8. **Être sans délai de justice** (aucune infraction récente, et pour les jurés d’assises, il faut être sans infraction récente, et pour les jurés de cour, sans infraction récente).
9. **Être sans délai de justice** (aucune infraction récente, et pour les jurés d’assises, il faut être sans infraction récente, et pour les jurés de cour, sans infraction récente).
10. **Être sans délai de justice** (aucune infraction récente, et pour les jurés d’assises, il faut être sans infraction récente, et pour les jurés de cour, sans infraction récente).

**Liste complète des conditions** :
- Majeur (18 ans ou plus).
- Âge de 18 à 40 ans (pour les jurés d’assises, l’âge maximum n’est pas fixé, mais l’âge de 40 ans est souvent mentionné).
- Sans faute (aucune infraction récente).
- Sans délai de justice (aucune infraction récente).
- Sans délai de justice (aucune infraction récente).
- Sans délai de justice (aucune infraction récente).
- Sans délai de justice (aucune infraction récente).
- Sans délai de justice (aucune infraction récente).
- Sans délai de justice (aucune infraction récente).
- Sans délai de justice (aucune infraction récente).
- Sans délai de justice (aucune infraction récente).

**Note** : Les conditions pour les jurés d’assises incluent également :
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).
- Être sans délai de justice (aucune infraction récente).

**Source** : Article 5 de la Loi sur l’instruction des affaires pénales (LIIP).

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse : elle invente une « Loi sur l'instruction des affaires pénales (LIIP) », indique un âge minimal de 18 ans (« Être majeur (au moins 18 ans) ») au lieu de plus de 23 ans, omet la nationalité française, la maîtrise du français écrit et les droits politiques, civils et de famille, et répète en boucle « Être sans délai de justice ».
- Inventions : Article 5 de la Loi sur l'instruction des affaires pénales (LIIP); Âge minimum de 18 ans pour être juré d'assises; Âge de 40 ans « souvent mentionné dans les textes »; Condition « Être sans faute (aucune infraction récente) »; Condition « Être sans délai de justice »; Distinction entre « jurés d'assises » et « jurés de cour »
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
**Alice :**
- **Lundi** (premier agent du lundi).
- **Mardi** (deuxième agent du mardi).
- **Mercredi** (deuxième agent du mercredi).

**Bruno :**
- **Mardi** (deuxième agent du mardi, car il ne travaille pas le lundi).
- **Mercredi** (deuxième agent du mercredi).
- **Jeudi** (deuxième agent du jeudi, car Chloé travaille le lendemain du jour d'Alice, soit le jeudi).

**Chloé :**
- **Lundi** (deuxième agent du lundi, car Alice travaille le lundi).
- **Mardi** (deuxième agent du mardi, car Bruno ne travaille pas le lundi, donc Chloé le travaille).
- **Jeudi** (deuxième agent du jeudi, car Chloé travaille le lendemain du jour d'Alice, soit le jeudi).

**Justification :**
- **Alice** travaille le lundi, le mardi et le mercredi, un agent par jour.
- **Bruno** ne travaille pas le lundi, donc il travaille le mardi, le mercredi et le jeudi.
- **Chloé** travaille le lendemain du jour d'Alice, soit le jeudi, et un agent par jour.
- **Mardi** : Alice et Chloé (Bruno ne travaille pas).
- **Mercredi** : Alice et Bruno.
- **Jeudi** : Bruno et Chloé.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse et incohérente : elle attribue plusieurs jours à chaque agent (« Alice travaille le lundi, le mardi et le mercredi »), introduit un jeudi inexistant et n'aboutit pas à la solution attendue (Alice lundi, Chloé mardi, Bruno mercredi).
- Inventions : Jeudi comme jour d'accueil (« Bruno : Jeudi », « Chloé : Jeudi »); Notion de « premier agent » et « deuxième agent » par jour, contraire à l'énoncé (un agent par jour); Alice travaille le lundi, le mardi et le mercredi; Bruno travaille le mardi, le mercredi et le jeudi; Chloé travaille le lendemain du jour d'Alice, soit le jeudi
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
La question prioritaire de constitutionnalité (QPC) est jugée dans l’instance compétente, qui est le tribunal administratif compétent pour l’affaire. La QPC est alors jugée dans un délai de 30 jours, à l’expiration duquel elle est automatiquement rejetée. La décision finale peut faire l’objet d’un appel, qui sera alors jugée dans le tribunal judiciaire compétent, dans un délai de 30 jours.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse sur tous les points : elle affirme que la QPC est « jugée dans l'instance compétente, qui est le tribunal administratif », sans transmission au Conseil d'État puis au Conseil constitutionnel. Elle invente un délai de « 30 jours » au lieu de 3 mois et affirme à tort que « la décision finale peut faire l'objet d'un appel » devant le tribunal judiciaire, alors qu'aucun appel n'est possible contre une décision du Conseil constitutionnel.
- Inventions : La QPC est jugée par le tribunal administratif compétent pour l'affaire; La QPC est jugée dans un délai de 30 jours, à l'expiration duquel elle est automatiquement rejetée; La décision finale peut faire l'objet d'un appel jugé par le tribunal judiciaire compétent dans un délai de 30 jours
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
**Calcul du taux d'activité moyen annuel**

**Étape 1 : Calcul du taux d'activité par mois**
- **Janvier à avril** (4 mois) : 80 % de chaque mois.
  Taux total pour ces 4 mois : 4 × 80 % = 320 %.
- **May à décembre** (8 mois) : 100 % de chaque mois.
  Taux total pour ces 8 mois : 8 × 100 % = 800 %.

**Étape 2 : Calcul du taux d'activité annuel**
- Taux total pour l'année : 320 % + 800 % = 1 120 %.
- Taux d'activité moyen annuel : 1 120 % ÷ 12 mois = 93,33 %.

**Étape 3 : Arrondi au dixième**
- Arrondi : 93,33 % → **93 %**.

**Explication** :
L'agent travaille 80 % de janvier à avril (4 mois) et 100 % de mai à décembre (8 mois). Le taux d'activité moyen est obtenu en additionnant les taux de chaque mois, puis en divisant par le nombre de mois. Le résultat est arrondi au dixième pour une présentation claire.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Le résultat final est « 93,33 % → **93 %** », arrondi à l'unité et non au dixième (93,3 % attendu) ; la réponse contient aussi l'anglicisme « May à décembre », ce qui contrevient au critère de français correct.
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
Votre accueil sera suspendu le 3 juin pour des travaux.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La phrase « Votre accueil sera suspendu le 3 juin pour des travaux. » respecte tous les critères : une seule phrase de 10 mots, date et cause conservées, formule supprimée, rien d'ajouté, langue correcte ; seuls « Votre accueil » (légèrement inexact au lieu de « L'accueil ») et « suspendu » (moins simple que « fermé ») sont discutables.
- Inventions : aucune
- Confiance : moyenne

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
Voici la réponse à l'Agent, fondée uniquement sur les passages fournis :

**Réponse à l'Agent :**

L’Anah (Agence Nationale de l’Habitat) est l’agence publique qui met en œuvre la politique nationale d’amélioration du parc de logements privés existants. Elle accorde des aides financières aux propriétaires occupants et bailleurs, ainsi qu’aux syndicats de copropriétaires, pour réaliser des travaux lourds ou des améliorations de leur habitat sous certaines conditions [1][2].

**À préciser pour l’Agent :**
- L’Anah octroie des subventions via des dispositifs opérationnels mis en œuvre par les Collectivités locales [1][2].
- Pour les travaux dans son logement, l’Anah peut accorder une aide financière, sous conditions, et l’usagère doit transmettre la facture des artisans à l’Anah pour demander le versement de l’aide [5].

**À vérifier :**
- Les modalités concrètes des aides (conditions, montants, délais) ne sont pas détaillées dans les passages fournis.
- Les dispositifs opérationnels mis en œuvre par les Collectivités locales ne sont pas listés dans les passages fournis.

**Source officielle à consulter :**
- [1] Liste des opérations programmées de l’Anah [1]
- [2] Liste des communes couvertes par une opération programmée [2]
- [5] Aides financières de l’Anah pour réaliser des travaux dans son logement [5]

Sources citées :
- Liste des opérations programmées de l'Anah (en cours et terminées) — https://www.data.gouv.fr/datasets/liste-des-operations-programmees-de-lanah-en-cours-et-terminees
- Liste des communes couvertes par une opération programmée — https://www.data.gouv.fr/datasets/liste-des-communes-couvertes-par-une-operation-programmee
- Aides financières de l'Anah pour réaliser des travaux dans son logement — https://www.service-public.gouv.fr/particuliers/vosdroits/F1328
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Seul le premier élément clé est présent (Agence nationale de l'habitat, aide financière sous conditions pour des travaux). Quatre éléments clés manquent : MaPrimeRénov', MaPrimeRénov' Copropriété et Loc'Avantages ; MaPrimeAdapt' ; Ma Prime Logement décent ; la demande en ligne depuis un compte personnel et le contact gratuit avec un conseiller France Rénov'. La réponse indique même que « les modalités concrètes des aides […] ne sont pas détaillées ».
- `pertinence_source` : 1 — La source [5] (https://www.service-public.gouv.fr/particuliers/vosdroits/F1328) correspond à la source attendue et traite bien des aides de l'Anah aux particuliers ; les deux jeux de données data.gouv.fr cités sont en revanche périphériques.
- Inventions : « met en œuvre la politique nationale d'amélioration du parc de logements privés existants » (non vérifiable dans les références); « aux propriétaires occupants et bailleurs, ainsi qu'aux syndicats de copropriétaires » (non vérifiable dans les références); « pour réaliser des travaux lourds » (non vérifiable dans les références); « L'Anah octroie des subventions via des dispositifs opérationnels mis en œuvre par les Collectivités locales » (non vérifiable dans les références); « l'usagère doit transmettre la facture des artisans à l'Anah pour demander le versement de l'aide » (non vérifiable dans les références)
- Confiance : haute

**Juge second** : juge

- `exactitude` : 1 — Un élément clé manque (les dispositifs spécifiques comme MaPrimeRénov', MaPrimeAdapt', etc.) et des précisions non vérifiables dans les références sont ajoutées (ex. : 'dispositifs opérationnels mis en œuvre par les Collectivités locales').
- `pertinence_source` : 0 — Les sources citées ([1] et [2]) sont hors sujet (données ouvertes sur les opérations programmées, non mentionnées dans les références), seule la source [5] est pertinente mais insuffisante seule.
- Inventions : L’Anah octroie des subventions via des dispositifs opérationnels mis en œuvre par les Collectivités locales; L’usagère doit transmettre la facture des artisans à l’Anah pour demander le versement de l’aide (modalité non précisée dans les références); Les modalités concrètes des aides (conditions, montants, délais) ne sont pas détaillées dans les passages fournis (invention de l'absence d'information); Les dispositifs opérationnels mis en œuvre par les Collectivités locales ne sont pas listés dans les passages fournis (invention de l'absence d'information)
- Confiance : haute

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
Voici les informations à transmettre à l'Agent concernant l'évaluation de la perte d'autonomie et les conditions d'attribution de l'Apa pour la fille de 82 ans :

1. **Évaluation de la perte d'autonomie** :
   - La perte d'autonomie de la mère sera évaluée par un professionnel de l'équipe médico-sociale (EMS) de son département lors d'une visite à domicile. Cette évaluation se fait sur la base de la grille Aggir, qui définit plusieurs degrés de perte d'autonomie, allant du Gir 1 (perte d'autonomie la plus forte) au Gir 6 (perte d'autonomie la plus faible) [1][2][5].

2. **Niveaux d'attribution de l'Apa** :
   - Seuls les personnes classées en Gir 1, Gir 2, Gir 3 ou Gir 4 peuvent obtenir l'Apa [1][5].
   - Si la perte d'autonomie de la mère est classée dans l'un de ces degrés, l'Apa peut être accordé en établissement (tarif dépendance) ou à domicile, selon le plan d'aide proposé par l'EMS [5].
   - Les services du département décident de l'attribution de l'Apa, et la décision est notifiée dans les 2 mois suivant la réception du dossier de demande complet [3][5].

3. **Cas particulier** :
   - Si la perte d'autonomie de la mère est classée en Gir 5 ou Gir 6, l'Apa ne peut être accordé à domicile, mais une aide peut être demandée auprès de la caisse de retraite [5].

**À vérifier** :
- Le degré de perte d'autonomie de la mère (Gir 1 à 6) et son évaluation par l'EMS.
- La décision du département d'attribution de l'Apa, qui intervient dans les 2 mois suivant la réception du dossier [3][5].

L'Agent peut orienter l'Agent vers le service des agents du service public pour obtenir ces informations.

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

- `exactitude` : 0 — Les 10 activités discriminantes et les 7 activités illustratives de la grille Aggir manquent, et le cas des Gir 5-6 est faussé : « l'Apa ne peut être accordé à domicile » laisse croire à une Apa possible en établissement et omet l'aide ménagère ; s'y ajoutent l'erreur « la fille de 82 ans » et l'absence de la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — La fiche F10009 de service-public.gouv.fr sur l'Apa traite bien de l'évaluation par la grille Aggir et des Gir 1 à 4 ouvrant droit à l'Apa, même si elle diffère de la source attendue (F1229) et qu'elle est citée quatre fois à l'identique sous des numéros différents.
- Inventions : Décision notifiée dans les 2 mois suivant la réception du dossier complet (non vérifiable dans les références); Évaluation par un professionnel de l'équipe médico-sociale (EMS) lors d'une visite à domicile (non vérifiable dans les références); Apa en établissement au titre du « tarif dépendance » (non vérifiable dans les références); Attribution de l'Apa « selon le plan d'aide proposé par l'EMS » (non vérifiable dans les références); Orientation vers « le service des agents du service public » (non vérifiable dans les références)
- Confiance : moyenne

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
Oui, l'allocation aux adultes handicapés (AAH) et le revenu de solidarité active (RSA) peuvent être cumulés, sous certaines conditions [1]. Cependant, le montant du RSA sera réduit par rapport au montant de l'AAH percevé, car l'AAH ne peut pas être perçue dans son intégralité [1].

**À vérifier** :
- Les conditions d'attribution de l'AAH (taux d'incapacité, cotisations, etc.) [2][4][5].
- Le montant maximal de l'AAH (1 041,59 €) et son éventuelle augmentation liée à la réforme des retraites [2].
- Les dispositions particulières en Guadeloupe, Guyane, Martinique, La Réunion, Saint-Barthélemy, Saint-Martin, Saint-Pierre-et-Miquelon et Mayotte [2][4][5].

**Source** : [1][2][3][4][5] (Index local). Pour une réponse complète, consultez le site officiel de l'Index local ou le service compétent.

Sources citées :
- Peut-on cumuler l'allocation adulte handicapé (AAH) et le RSA ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F20209
- Allocation aux adultes handicapés (AAH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F12242
- Allocation aux adultes handicapés (AAH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F12242
- Allocation aux adultes handicapés (AAH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F12242
- Allocation aux adultes handicapés (AAH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F12242
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse dit que « l'AAH ne peut pas être perçue dans son intégralité », alors que la référence indique que c'est le RSA qui n'est pas versé en intégralité ; elle omet aussi l'intérêt possible de conserver la seule AAH et la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — La source [1] (service-public.gouv.fr F20209, « Peut-on cumuler l'AAH et le RSA ? ») traite précisément du point demandé.
- Inventions : L'AAH ne peut pas être perçue dans son intégralité (contredit la référence : c'est le RSA qui est réduit); Montant maximal de l'AAH de 1 041,59 €; Éventuelle augmentation de l'AAH liée à la réforme des retraites; Cotisations parmi les conditions d'attribution de l'AAH
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
**Réponse à l'Agent :**

1. **Possibilité de demander la PCH à 63 ans** :
   - La PCH est accessible à toute personne de 20 ans ou plus, sous certaines conditions [1].
   - Pour les personnes de 60 ans ou plus, la demande peut être faite sans limite d'âge *si* l’attribution a déjà été effectuée avant 60 ans ou si la personne continue à travailler [1].
   - **À vérifier** : La femme ne travaille plus, mais elle a perdu son autonomie depuis 50 ans. Elle ne remplit pas les conditions d’attribution avant 60 ans. **Elle ne peut donc pas demander la PCH** [1].

2. **Comptabilité des revenus** :
   - Les ressources (revenu fiscal de référence, RFR) sont prises en compte pour déterminer le taux de prise en charge de ses dépenses [4].
   - **À vérifier** : Le montant du RFR de la femme, car il influence le taux de prise en charge.

3. **Où déposer sa demande** :
   - La demande peut être faite en ligne via un téléservice (si proposé par la MDPH) ou par courrier avec formulaire et documents justificatifs [2].
   - **À vérifier** : La présence d’un téléservice de la MDPH de son lieu de résidence.

**Conclusion** : La femme ne peut pas demander la PCH car il n’y a pas d’attribution antérieure et il ne travaille plus. Il faut orienter l’Agent vers la source officielle (Service Public) pour toute demande ultérieure.

Sources citées :
- Prestation de compensation du handicap (PCH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F14202
- Prestation de compensation du handicap (PCH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F14202
- Prestation de compensation du handicap (PCH) — https://www.service-public.gouv.fr/particuliers/vosdroits/F14202
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Erreur grave contredisant la source : la sortie conclut « Elle ne peut donc pas demander la PCH » en exigeant une attribution antérieure, alors que la référence admet la demande après 60 ans si les conditions d'attribution étaient déjà remplies avant 60 ans, ce qui semble être le cas d'un handicap survenu à 50 ans ; manquent en outre les critères de difficulté absolue ou grave, l'absence de condition de ressources avec le seuil de 31 162,62 € et les taux de 100 % ou 80 %, le délai de 4 mois de la CDAPH valant rejet implicite, et la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — La source citée, service-public.gouv.fr F14202, traite bien de la PCH et correspond à la source attendue.
- Inventions : « si l'attribution a déjà été effectuée avant 60 ans » : condition déformée, la référence parle de conditions d'attribution remplies avant 60 ans, et non d'une attribution effective.; « Elle ne remplit pas les conditions d'attribution avant 60 ans » : affirmation non étayée, contraire aux faits de l'entrée (handicap depuis 50 ans).
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
**Réponse à l'Agent :**

**1. Éligibilité à MaPrimeAdapt' :**
Oui, la locataire peut bénéficier de MaPrimeAdapt' [1][5].
- **Condition de perte d'autonomie** : Elle a 66 ans et est classée en Gir 4 (groupe iso-ressources) [5].
- **Condition de ressources** : Son revenu fiscal de référence (20 000 €) est inférieur au plafond des ménages aux ressources modestes hors Île-de-France (jusqu'à 22 259 € pour 1 personne) [1].
- **Condition de logement** : L'appartement est du parc privé et situé hors Île-de-France [5].

**2. Taux de prise en charge et plafond :**
- **Taux** : 50 % (car son revenu fiscal de référence est inférieur au plafond des ménages aux ressources très modestes, et elle n’a pas 70 ans ou un taux d’incapacité d’au moins 50 %) [1][3].
- **Plafond** : 22 000 € HT (hors taxes) [3].

**3. Démarches à suivre :**
- **Demande d’aide** : Déposer sur le site [4] (monprojetanah) depuis l’entrée « Je suis propriétaire occupant » (car elle est locataire) [4].
- **Simulation du montant** : Utiliser le simulateur du site [1] pour estimer l’aide [1].
- **Cumul avec d’autres aides** : MaPrimeAdapt' peut se cumuler avec la PCH (prestation de compensation du handicap) [3][5]. Vérifier avec sa mairie pour les aides locales [1][5].

**À vérifier** :
- Le détail de son éligibilité à la PCH (si elle l’a obtenue) [5].
- Les aides locales disponibles dans son département [1][5].

**Source** : [1][3][4][5].

Sources citées :
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse contient une erreur factuelle : elle justifie le taux de 50 % par « son revenu fiscal de référence est inférieur au plafond des ménages aux ressources très modestes », alors que 20 000 € dépasse ce plafond (17 363 €). Plusieurs éléments clés manquent aussi : l'accord du bailleur, le montant de 5 000 €, l'accord de l'Anah à attendre avant les travaux et le plafond des très modestes.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F37501) est la fiche MaPrimeAdapt' attendue et traite bien du point demandé.
- Inventions : « son revenu fiscal de référence est inférieur au plafond des ménages aux ressources très modestes » (contredit la référence); « elle n'a pas 70 ans ou un taux d'incapacité d'au moins 50 % » comme critère de taux, invérifiable dans les références; « MaPrimeAdapt' peut se cumuler avec la PCH », invérifiable dans les références; « Condition de logement : situé hors Île-de-France » présentée comme condition d'éligibilité, invérifiable
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
Voici les informations à transmettre à l'usager :

1. **Mise à jour du livret de famille** : Il doit se rendre à la mairie où a été célébré le mariage, avec son **carte d'identité et le jugement du divorce** [1].
2. **Extrait d'acte de mariage** : Le divorce apparaîtra sur le livret avec l'extrait d'acte de mariage [2].
3. **Décès des époux** : Si l'un des époux a décédé, l'extrait de l'acte de décès sera inscrit sur le livret, mentionnant uniquement le lieu et la date du décès [3].
4. **Demande d'un second livret** : Comme son ex-épouse garde le livret original, il peut demander un second livret pour effectuer certaines démarches (ex. : inscription scolaire des enfants, demande de prestation familiale) [4].

**À vérifier** :
- Le lieu de résidence de l'usager (mairie où réside-t-il actuellement) [4].
- Les modalités de demande d'un second livret (mairie, formulaire à remplir, ou autorités consulaires en cas d'étranger) [4].

**Source** : Les passages [1], [2], [3] et [4] couvrent les points ci-dessus. Le passage [5] ne s'applique pas à ce cas (remise automatique du livret lors du mariage, mais l'usager a divorcé).

Sources citées :
- Mise à jour du livret de famille à la suite d'un changement d'état civil (naissance, divorce, etc.) — https://www.service-public.gouv.fr/particuliers/vosdroits/F18910
- Mise à jour du livret de famille à la suite d'un changement d'état civil (naissance, divorce, etc.) — https://www.service-public.gouv.fr/particuliers/vosdroits/F18910
- Mise à jour du livret de famille à la suite d'un changement d'état civil (naissance, divorce, etc.) — https://www.service-public.gouv.fr/particuliers/vosdroits/F18910
- Demande d'un second livret de famille en cas de divorce ou de séparation — https://www.service-public.gouv.fr/particuliers/vosdroits/F11996
- Remise automatique du livret de famille lors du mariage — https://www.service-public.gouv.fr/particuliers/vosdroits/F1345
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Deux éléments clés manquent : le rôle de l'officier de l'état civil (remplir, dater, signer et tamponner le livret) et la possibilité de passer par la mairie de résidence, qui n'accepte pas toujours de servir d'intermédiaire, alors que l'usager habite justement ailleurs ; le point 3 sur le décès est en outre hors sujet.
- `pertinence_source` : 1 — La source citée F18910 (« Mise à jour du livret de famille à la suite d'un changement d'état civil ») correspond à la source attendue et traite bien du point demandé.
- Inventions : « pour effectuer certaines démarches (ex. : inscription scolaire des enfants, demande de prestation familiale) » : non vérifiable dans les références; « autorités consulaires en cas d'étranger » : non vérifiable dans les références; « Si l'un des époux a décédé, l'extrait de l'acte de décès sera inscrit sur le livret, mentionnant uniquement le lieu et la date du décès » : non vérifiable dans les références
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
Voici la réponse à l’Agent :

**Réponse :**

L’usagère ne peut pas épouser son compagnon à titre posthume, car le décès brutal de son compagnon, alors qu’ils préparaient leur mariage, constitue un décès subitif. Dans ce cas, l’usagère doit :

1. **Contacter l’employeur ou les employeurs de la personne décédée** pour prévenir son employeur ou ses employeurs, et demander un congé ou une autorisation d’absence [4].
2. **Vérifier si la personne décédée avait indiqué ses dernières volontés** (décès subitif) [1].
3. **Contacter l’employeur ou les employeurs de la personne décédée** pour prévenir son employeur ou ses employeurs, et demander un congé ou une autorisation d’absence [4].
4. **Prévenir les membres de la famille, les amis, les voisins, les associations ou clubs fréquentés par la personne décédée** [5].
5. **Vérifier l'état général du domicile et ses équipements**, enlevant le périssable et les ordures, mais sans vider précipitamment les meubles [5].
6. **Prévenir la banque de la personne décédée** [3].
7. **Contacter les organismes sociaux pour obtenir le versement de prestations** (pension de réversion, etc.) [3].
8. **Gérer les papiers et les données personnelles de la personne décédée** [3].

**À vérifier :**
- Les coordonnées de l’employeur ou les employeurs de la personne décédée (bulletin de salaire récent) [4].
- Les spécificités du décès subitif (décès brutal, préparation du mariage) [1].

**Source :** Les passages [1], [3], [4], [5].

Sources citées :
- Un proche est décédé — https://www.service-public.gouv.fr/particuliers/vosdroits/F16507
- Un proche est décédé — https://www.service-public.gouv.fr/particuliers/vosdroits/F16507
- Un proche est décédé — https://www.service-public.gouv.fr/particuliers/vosdroits/F16507
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

- `exactitude` : 0 — La réponse affirme sans source « L'usagère ne peut pas épouser son compagnon à titre posthume, car [...] constitue un décès subitif », ce qui est une affirmation non sourcée, juridiquement inexacte (le mariage posthume existe en droit français) et fondée sur une notion inventée ; elle ne dit pas qu'aucune source ne traite du sujet, n'oriente ni vers l'état civil ni vers un professionnel du droit et omet la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 0 — La seule fiche citée, « Un proche est décédé » (F16507), porte sur les démarches après un décès et ne traite pas du mariage posthume, point demandé.
- `cas_sans_reponse` : 0 — Au lieu de signaler l'absence de source officielle et d'orienter vers la mairie ou un avocat/notaire, l'Assistant invente une réponse (« ne peut pas épouser [...] à titre posthume ») et une liste de démarches sans rapport avec la question.
- Inventions : Affirmation selon laquelle l'usagère ne peut pas épouser son compagnon à titre posthume; Notion de « décès subitif » présentée comme motif juridique d'impossibilité; Rattachement de « Vérifier si la personne décédée avait indiqué ses dernières volontés (décès subitif) » au passage [1]; « Les spécificités du décès subitif (décès brutal, préparation du mariage) [1] » attribuées à une source
- Confiance : haute

**Juge second** : juge

- `exactitude` : 0 — La sortie invente une réponse (affirmation que l'usagère ne peut pas épouser son compagnon à titre posthume) et des démarches (étapes 1 à 8) non présentes dans les références, alors que le cas est marqué 'sans_reponse'. Plusieurs éléments clés manquent ou sont erronés, notamment l'absence de mention explicite qu'aucune source officielle ne traite du mariage posthume.
- `pertinence_source` : 0 — Les sources citées traitent du décès d'un proche (démarches funéraires, administratives), mais aucune ne traite du mariage posthume, qui est le sujet de la question.
- `cas_sans_reponse` : 0 — L'assistant invente une réponse et des démarches au lieu de dire qu'aucune source officielle n'est disponible et d'orienter vers le service de l'état civil ou un professionnel du droit.
- Inventions : Affirmation que l'usagère ne peut pas épouser son compagnon à titre posthume; Liste des démarches à engager (étapes 1 à 8) non pertinentes pour le mariage posthume; Mention d'un 'décès subitif' comme obstacle au mariage posthume; Orientation vers l'employeur, la banque ou les organismes sociaux au lieu du service de l'état civil ou d'un professionnel du droit; Absence de mention 'Ne vaut pas avis juridique'
- Confiance : haute

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
Voici la réponse à la question de l'Agent, fondée uniquement sur les passages fournis :

**1. Qu'est-ce que la journée de solidarité ?**
C'est une journée supplémentaire de travail de 7 heures non rémunérée, destinée au financement d'actions en faveur de l'autonomie des personnes âgées ou handicapées. Elle est applicable aux fonctionnaires et aux contractuels [1][2].

**2. Comment peut-elle être accomplie ?**
- **Cas général** (hors Alsace-Moselle) :
  - Travail un jour férié précédemment chômé (sauf le 1ᵉʳ mai) [1][2].
  - Suppression d'une journée de RTT [1][2].
  - Toute autre organisation permettant le travail de 7 heures précédemment non travaillées, sauf suppression d'un jour de congé annuel [1][2].
- **Cas Alsace-Moselle** (Moselle, Bas-Rhin, Haut-Rhin) :
  - Travail un jour férié normalement chômé (sauf le 1ᵉʳ mai, les 25 et 26 décembre, le Vendredi Saint) [1].
  - Suppression d'une journée de RTT [1].
  - Toute autre organisation permettant le travail de 7 heures précédemment non travaillées, sauf suppression d'un jour de congé annuel [1].

**3. Qui fixe les modalités d'accomplissement ?**
- **Fonction publique d'État** : arrêté ministériel après avis du comité social d'administration ministériel [1].
- **Fonction publique territoriale** (SST) : délibération après avis du comité social territorial [1].
- **Fonction publique hospitalière** : décision du directeur de l'établissement, après avis du comité social d'établissement [1].

**4. Quelle source à consulter pour les modalités précises ?**
Les passages fournis ne précisent pas les modalités concrètes pour les agents territoriaux (SST) en cas de changement d'employeur, ni les modalités d'accomplissement pour les agents de la fonction publique d'État. Pour ces éléments, l'Agent doit consulter :
- Le **comité social d'administration ministériel** (pour la fonction publique d'État) [1].
- Le **comité social territorial** (pour la fonction publique territoriale) [1].
- Le **comité social d'établissement** (pour la fonction publique hospitalière) [1].

**À vérifier** :
- Les modalités concrètes pour les agents territoriaux (SST) en cas de changement d'employeur (rémunération, contrepartie de repos) [2].
- Les modalités d'accomplissement pour les agents de la fonction publique d'État (arrêté ministériel) [1].

**Source officielle** : Les passages fournis (Index local) sont les seuls sources à consulter.

Sources citées :
- Comment la journée de solidarité est-elle accomplie dans la fonction publique ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F2859
- Jours fériés et ponts dans le secteur privé — https://entreprendre.service-public.gouv.fr/vosdroits/F2405
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — Trois éléments clés sont justes : 7 heures non rémunérées pour les fonctionnaires et les contractuels, les modalités du cas général hors 1er mai et congé annuel, et la délibération après avis du comité social territorial. En revanche, la réduction proportionnelle des 7 heures pour les agents à temps partiel ou à temps non complet manque. La section 4 est aussi confuse : elle renvoie l'agent vers les comités pour « consulter » les modalités, alors qu'ils ne rendent qu'un avis, et elle contredit la section 3 sur la fonction publique d'État. La mention « Ne vaut pas avis juridique » est absente.
- `pertinence_source` : 1 — La source F2859 de service-public.gouv.fr, citée par la réponse, traite bien de la journée de solidarité dans la fonction publique. La seconde source citée (F2405, secteur privé) est hors sujet.
- Inventions : Liste des jours exclus en Alsace-Moselle (« sauf le 1ᵉʳ mai, les 25 et 26 décembre, le Vendredi Saint »), non vérifiable dans les références; Modalités pour la fonction publique d'État (« arrêté ministériel après avis du comité social d'administration ministériel ») et pour la fonction publique hospitalière (« décision du directeur de l'établissement »), non vérifiables dans les références; « modalités concrètes pour les agents territoriaux (SST) en cas de changement d'employeur (rémunération, contrepartie de repos) » attribuées à la source [2] relative au secteur privé; Sigle « SST » accolé à la fonction publique territoriale, sans fondement dans les références
- Confiance : moyenne

**Juge second** : juge

- `exactitude` : 1 — Un élément clé est imprécis : la sortie mentionne des modalités spécifiques pour l'Alsace-Moselle et des détails sur la fonction publique d'État et hospitalière, qui ne font pas partie des éléments clés attendus pour la fonction publique territoriale (FPT).
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr) traite bien du sujet de la journée de solidarité dans la fonction publique, conformément à la référence attendue.
- Inventions : Modalités spécifiques pour l'Alsace-Moselle (ex. : exclusion des 25 et 26 décembre, Vendredi Saint); Détails sur la fixation des modalités pour la fonction publique d'État (arrêté ministériel) et hospitalière (décision du directeur); Mention des comités sociaux pour la fonction publique d'État et hospitalière; Questions à vérifier sur les modalités en cas de changement d'employeur ou pour la fonction publique d'État
- Confiance : haute

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
Oui, un jour de carence doit être retenu sur le traitement indiciaire de l'adjoint administratif, car le médecin a coché la case « prolongation » et le nouvel arrêt de travail a été considéré comme une prolongation de l'arrêt initial. Le délai de carence ne s'applique pas dans ce cas, selon les passages [1], [2], [3] et [4].

**Règle générale** :
- Un jour de carence est appliqué lors de chaque arrêt de travail, sauf dans les cas suivants [1], [2], [3] et [4] :
  - **Prolongeant l'arrêt initial** (2e arrêt de maladie pour la même affection, reprise entre 2 arrêts < 48 h, ou arrêt de nouveau 1 ou 2 jours plus tard, ou non-consulter le médecin un samedi, dimanche ou jour férié) [1], [2], [3].
  - **Affection de longue durée (ALD)** (1er arrêt de maladie pour une ALD, puis 3 ans sans arrêt) [1], [2], [3].
  - **Congés spécifiques** (Citis, CLM, CLD, congé de grossesse avant congé de maternité, etc.) [1], [2], [3].

**À vérifier** :
- Le délai de 48 heures (commençant du 1er jour suivant le dernier arrêt initial) [1], [2], [3].
- Les éléments de rémunération non versés le 1er jour (traitement indiciaire, primes, indemnités liées à la grossesse, etc.) [1], [2], [3].
- Les indemnités journalières de la Sécurité sociale (versées à partir du 4ᵉ jour, soit 3 jours après le 1ᵉᵈ jour de carence) [4].

**Source** : [1], [2], [3], [4].

Sources citées :
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

- `exactitude` : 0 — La conclusion est erronée et contradictoire (« Oui, un jour de carence doit être retenu… Le délai de carence ne s'applique pas dans ce cas »), alors que la référence conclut qu'aucun nouveau jour de carence n'est dû ; en outre, le principe de rémunération à partir du 2e jour et le maintien du SFT manquent, l'IR et la NBI ne sont pas mentionnées, et le décompte en jours calendaires n'est pas précisé.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F13861, sur le délai de carence dans la fonction publique) traite bien du point demandé et correspond à la source attendue.
- Inventions : « indemnités liées à la grossesse » parmi les éléments non versés le 1er jour (non vérifiable dans les références); Indemnités journalières de la Sécurité sociale versées à partir du 4e jour (non vérifiable dans les références et hors sujet pour un fonctionnaire titulaire); Exception ALD « 1er arrêt de maladie pour une ALD, puis 3 ans sans arrêt » (non vérifiable dans les références); Exceptions pour congés spécifiques (Citis, CLM, CLD, congé de grossesse avant congé de maternité) (non vérifiables dans les références); Cas « non-consulter le médecin un samedi, dimanche ou jour férié » (non vérifiable dans les références)
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
**Réponse à l'Agent :**

1. **Possibilité de télétravailler 4 jours par semaine** :
   Oui, l’agente peut télétravailler 4 jours par semaine en raison de sa grossesse, comme indiqué dans les passages [1] et [2] [1] : *"Si vous remplissez les conditions pour bénéficier d'un congé de proche aidant"* (grossesse). Les passages ne précisent pas les conditions exactes, mais l’agent doit vérifier les critères de congé de proche aidant.

2. **Comment faire sa demande** :
   - L’agent doit informer son supérieur hiérarchique de sa nécessité de venir sur site un jour pour lequel elle bénéficiera d’une autorisation de télétravail et demander à déplacer ce jour [3].
   - L’autorisation peut être accordée pour un recours régulier ou ponctuel, avec une période d’adaptation maximale de 3 mois [4].
   - Si refus, l’agent peut saisir la CAP (fonctionnaire) ou la CCP (contractuel) [4].

3. **Montant du forfait télétravail** :
   - Le forfait est versé sur la base du nombre de jours de télétravail autorisés [2].
   - Le montant est fixé à 2,88 € par journée, dans la limite de 253,44 € par an (88 jours indemnisés) [2].
   - L’agent percevra donc 4 jours × 2,88 € = **11,52 €** (sous la limite annuelle) [2].

**À vérifier** :
- Les conditions exactes du congé de proche aidant (durée, critères) [1].
- Les plages horaires et les conditions de mise en œuvre du télétravail dans l’autorisation [4].
- Les documents d’information et les conditions de mise en place du télétravail [4].

**Source** : Passages [1], [2], [3], [4].

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

- `exactitude` : 0 — La réponse contient une erreur factuelle grave en rattachant la grossesse au « congé de proche aidant » (« Si vous remplissez les conditions pour bénéficier d'un congé de proche aidant » (grossesse)). Elle omet le principe des 3 jours maximum avec 2 jours sur site, ainsi que la demande écrite et la décision écrite dans le mois suivant la réception. Elle omet aussi le versement trimestriel et présente un calcul erroné et ambigu (« 4 jours × 2,88 € = 11,52 € »).
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F13974, Télétravail dans la fonction publique) correspond à la source attendue et traite bien du point demandé.
- Inventions : Lien entre grossesse et conditions du congé de proche aidant pour autoriser le télétravail 4 jours; Procédure de demande décrite comme le fait d'informer le supérieur hiérarchique pour déplacer un jour de télétravail, au lieu d'une demande écrite; Calcul « 4 jours × 2,88 € = 11,52 € » présenté comme le montant perçu, sans période de référence; Absence de la mention obligatoire « Ne vaut pas avis juridique »
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
Voici les informations disponibles sur l'ARS Bourgogne-Franche-Comté, basées sur les passages fournis :

**Statut et missions** :
- L'ARS Bourgogne-Franche-Comté est l'**Agence régionale de santé** de la Région Bourgogne-Franche-Comté. Elle a pour mission de **coordonner et assurer la prise en charge des soins et la santé publique** dans son territoire, en assurant la **coordination et la complémentarité** dans la prise en charge des patients [2].
- Elle vise également à **réduire les inégalités entre les territoires** et à **offrir des services de soins et de santé publique** [2].

**Organisation** :
- L'ARS Bourgogne-Franche-Comté est **DREAL** (DREAL Bourgogne-Franche-Comté), ce qui signifie qu'elle est une **agence régionale de santé** (ARS) [4, 5].
- Elle répertorie les **établissements de santé** (hôpitaux, cliniques, etc.) dans son territoire, avec leur **géolocalisation** [1].

**À vérifier** :
- Les passages ne précisent pas les **missions détaillées** (ex. : coordination, mutualisation, etc.) ou l'**organisation interne** (ex. : structure, services, etc.) de l'ARS. Pour ces éléments, l'Agent peut consulter le site officiel de l'ARS Bourgogne-Franche-Comté.

**Source** :
- Les passages [1], [2], [4], [5] sont les seuls à fournir des informations sur l'ARS Bourgogne-Franche-Comté.

Sources citées :
- Maisons régionales de santé en Provence Alpes Côte d'Azur — https://www.data.gouv.fr/datasets/maisons-regionales-sante-provence-alpes-cote-d-azur
- Zone de sauvegarde (ZS) et ressources stratégiques associées (RS) en Bourgogne-Franche-Comté — https://www.data.gouv.fr/datasets/ressources-strategiques-pour-lalimentation-en-eau-potable-aep
- Zone de sauvegarde (ZS) et ressources stratégiques associées (RS) en Bourgogne-Franche-Comté — https://www.data.gouv.fr/datasets/zone-de-sauvegarde-zs-et-ressources-strategiques-associees-rs-en-bourgogne-franche-comte
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

- `exactitude` : 0 — La sortie présente une description non sourcée des missions (« coordonner et assurer la prise en charge des soins et la santé publique », « réduire les inégalités entre les territoires ») et contient une erreur grave (« L'ARS Bourgogne-Franche-Comté est DREAL »), au lieu de dire qu'aucune source officielle ne la présente ; la mention « Ne vaut pas avis juridique » est absente.
- `pertinence_source` : 0 — Les sources citées (maisons de santé en PACA, zones de sauvegarde pour l'eau potable, liste d'établissements de santé) ne traitent ni du statut, ni des missions, ni de l'organisation de l'ARS Bourgogne-Franche-Comté.
- `cas_sans_reponse` : 0 — L'item est sans réponse, mais l'Assistant invente une présentation de l'ARS (missions, « est DREAL ») au lieu de déclarer l'absence de source officielle, même s'il oriente partiellement vers le site officiel.
- Inventions : L'ARS a pour mission de coordonner et assurer la prise en charge des soins et la santé publique, en assurant la coordination et la complémentarité dans la prise en charge des patients; Elle vise à réduire les inégalités entre les territoires et à offrir des services de soins et de santé publique; L'ARS Bourgogne-Franche-Comté est DREAL (DREAL Bourgogne-Franche-Comté); Elle répertorie les établissements de santé dans son territoire avec leur géolocalisation; Attribution de ces informations sur l'ARS aux passages [1], [2], [4], [5], qui ne les contiennent pas
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
Voici les réponses à votre question, fondées sur les passages fournis :

1. **Locaux concernés** :
   La taxe sur les friches commerciales ne serait appliquée qu'aux **friches issues de l'EPFN** (Établissement Public Foncier de Normandie) dans l'Orne, **sauf si la présence de bâtiments dégradés est relevée** [4].

2. **Taux applicable** :
   Aucun passage ne précise le taux de la taxe sur les friches commerciales. Il reste à vérifier auprès de la Direction Départementale des Territoires de l'Orne ou de l'EPFN.

3. **Date de délibération** :
   La taxe d'aménagement est appliquée sur le territoire de la commune **après délibération** [1]. La date de délibération n'est pas fixée dans les passages fournis. Il faut consulter le service compétent pour connaître la délai.

**À vérifier** :
- Le taux de la taxe sur les friches commerciales.
- La date de délibération pour l'application de la taxe d'aménagement.

**Source officielle** :
- Direction Départementale des Territoires de l'Orne (friches issues de l'EPFN) [4].
- Service public des impôts (taxe d'aménagement) [3].

Sources citées :
- Friches issues de l' EPFN dans l'Orne en 2026 — https://www.data.gouv.fr/datasets/friches-issues-de-l-epfn-dans-lorne-en-2026
- Taxe d'aménagement dans le cadre de la fiscalité de l'urbanisme pour 2021 — https://www.data.gouv.fr/datasets/taxe-damenagement-dans-le-cadre-de-la-fiscalite-de-lurbanisme-pour-2021
- Quels sont les travaux à déclarer aux impôts ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F35742
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie invente une réponse sourcée (« ne serait appliquée qu'aux friches issues de l'EPFN dans l'Orne, sauf si la présence de bâtiments dégradés est relevée ») et confond la taxe sur les friches commerciales avec la taxe d'aménagement, sans dire qu'aucune source ne traite du sujet ; elle omet aussi l'orientation vers la DDFiP et la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 0 — Les sources citées (jeu de données sur les friches EPFN de l'Orne, taxe d'aménagement 2021, fiche F35742 sur les travaux à déclarer) ne traitent pas de la taxe sur les friches commerciales, et une fiche service-public est citée alors qu'aucune n'aurait dû l'être.
- `cas_sans_reponse` : 0 — Au lieu de déclarer l'absence de source officielle et d'orienter vers la direction départementale des finances publiques, l'Assistant avance des conditions non sourcées et oriente vers la DDT de l'Orne et l'EPFN.
- Inventions : La taxe sur les friches commerciales ne serait appliquée qu'aux friches issues de l'EPFN dans l'Orne, sauf si la présence de bâtiments dégradés est relevée; Assimilation de la délibération à celle de la taxe d'aménagement (« La taxe d'aménagement est appliquée sur le territoire de la commune après délibération »); Orientation vers la Direction Départementale des Territoires de l'Orne ou l'EPFN comme service compétent pour le taux
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
Voici le jeu de données national sur **inventaire SRU** (loi SRU, *Inventaire des logements sociaux*):

- **Titre** : *Communes et inventaire SRU*
- **Producteur** : *Ministère de la Transition écologique*
- **Lien** : [Accéder au jeu de données](https://www.data.gouv.fr/datasets/communes-et-inventaire-sru)

---
**Autres jeux de données pertinents (non exclusifs) :**
- *Observatoire de l'habitat* (Grand Paris Seine Ouest) – [Accéder](https://www.data.gouv.fr/datasets/observatoire-de-lhabitat)
- *Communes SRU et DALO* (Région Occitanie / Pyrénées Méditerranée) – [Accéder](https://www.data.gouv.fr/datasets/communes-sru-et-dalo)
- *Application de l’article L.302-5 du Code de la construction et de l’habitation en Bretagne* (DRAMB) – [Accéder](https://www.data.gouv.fr/datasets/application-de-larticle-l-302-5-du-code-de-la-construction-et-de-lhabitation-en-bretagne)

---
**Prochaine étape** :
Si vous souhaitez explorer les données de l'un de ces jeux de données, précisez lequel et je vous aiderai à consulter ses ressources.

Sources citées :
- Communes et inventaire SRU — https://www.data.gouv.fr/datasets/communes-et-inventaire-sru
- Observatoire de l'habitat — https://www.data.gouv.fr/datasets/observatoire-de-lhabitat
- Communes SRU et DALO — https://www.data.gouv.fr/datasets/communes-sru-et-dalo
- Application de l’article L.302-5 du Code de la construction et de l’habitation en Bretagne — https://www.data.gouv.fr/datasets/application-de-larticle-l-302-5-du-code-de-la-construction-et-de-lhabitation-en-bretagne
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
Voici le jeu de données qui correspond à ta recherche :

**Titre** : RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National]
**Producteur** : Caisse Nationale des Allocations familiales (CNAF)
**Date de dernière mise à jour** : *Non précisée dans les métadonnées initiales* (à vérifier sur la page du jeu de données).
**Lien** : [Accéder au jeu de données](https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national)

---
### Prochaine étape
Pour obtenir la **date de dernière mise à jour**, la **licence** et la **fréquence de mise à jour**, je vais consulter les métadonnées détaillées du jeu de données.
Voici les informations demandées pour le jeu de données **"RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National]"** :

- **Titre** : RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National]
- **Producteur** : Caisse Nationale des Allocations familiales (CNAF)
- **Date de dernière mise à jour** : 9 octobre 2026
- **Lien** : [Accéder au jeu de données](https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national)
- **Licence** : [LOV2](https://www.data.gouv.fr/legal/lov2)
- **Fréquence de mise à jour** : Mensuelle

---
### Prochaine étape
Si tu souhaites explorer les **ressources** (fichiers) de ce jeu de données, je peux lister les fichiers disponibles (format, taille, lien). Souhaites-tu que je procède à cette étape ?

Sources citées :
- RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National] — https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national
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
Voici les informations concernant le jeu de données **"Les bénéficiaires de l'aide sociale à l'enfance"** (producteur : *Ministère des Solidarités et de la Santé* / DREES) :

- **Nombre de fichiers** : 20.
- **Fichier de séries longues le plus récent** :
  - **Titre** : *Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2024).xlsx*
  - **Format** : Fichier Excel (XLSX).
  - **Lien** : [Accéder au fichier](https://data.drees.solidarites-sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2024_xlsx)

---
*Source : [Index local](https://www.data.gouv.fr/explore/dataset/les-beneficiaires-de-laide-sociale-a-lenfance) et [Page de la DREES](https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance).*

Sources citées :
- Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2024).xlsx — https://data.drees.solidarites-sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2024_xlsx
- Les bénéficiaires de l'aide sociale à l'enfance — https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance
```

### Contrôles automatiques

```text
{
  "appariement": [
    0,
    2
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
Voici un jeu de données qui correspond à un **répertoire national des élus** couvrant les maires, conseillers municipaux, départementaux et régionaux :

- **Titre** : Répertoire national des élus
- **Producteur** : Ministère de l'intérieur
- **Dernière mise à jour** : Non précisée dans les métadonnées initiales (lien : [https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1](https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1))

---
**Autres jeux de données pertinents (non couvrant l'ensemble des élus, mais des sous-catégories) :**

1. **Répertoire national des élus locaux - Communautaires de Grand Poitiers CU**
   - Producteur : Grand Poitiers Open Data
   - Lien : [https://www.data.gouv.fr/datasets/repertoire-national-des-elus-locaux-communautaires-de-grand-poitiers-cu](https://www.data.gouv.fr/datasets/repertoire-national-des-elus-locaux-communautaires-de-grand-poitiers-cu)

2. **Répertoire national des élus locaux  : Municipaux des 40 communes membres de Grand Poitiers CU**
   - Producteur : Grand Poitiers Open Data
   - Lien : [https://www.data.gouv.fr/datasets/repertoire-national-des-elus-locaux-municipaux-des-40-communes-membres-de-grand-poitiers-cu](https://www.data.gouv.fr/datasets/repertoire-national-des-elus-locaux-municipaux-des-40-communes-membres-de-grand-poitiers-cu)

3. **Elections municipales 2026 - Maires et conseillers municipaux sortants**
   - Producteur : Ministère de l'intérieur
   - Lien : [https://www.data.gouv.fr/datasets/elections-municipales-2026-maires-et-conseillers-municipaux-sortants](https://www.data.gouv.fr/datasets/elections-municipales-2026-maires-et-conseillers-municipaux-sortants)

---
**Prochaine piste** : Si l'ensemble des élus (départementaux et régionaux) n'est pas couvert par le premier jeu de données, vous pouvez explorer les **départementaux et régionaux** via les jeux de données dédiés à chaque département ou région (ex. : *[Répertoire national des élus départementaux](https://www.data.gouv.fr/datasets/repertoire-national-des-elus-departementaux-1)* ou *[Répertoire national des élus régionaux](https://www.data.gouv.fr/datasets/repertoire-national-des-elus-regionaux-1)*).

Sources citées :
- Répertoire national des élus — https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1
- Répertoire national des élus locaux - Communautaires de Grand Poitiers CU — https://www.data.gouv.fr/datasets/repertoire-national-des-elus-locaux-communautaires-de-grand-poitiers-cu
- Répertoire national des élus locaux  : Municipaux des 40 communes membres de Grand Poitiers CU — https://www.data.gouv.fr/datasets/repertoire-national-des-elus-locaux-municipaux-des-40-communes-membres-de-grand-poitiers-cu
- Elections municipales 2026 - Maires et conseillers municipaux sortants — https://www.data.gouv.fr/datasets/elections-municipales-2026-maires-et-conseillers-municipaux-sortants
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
Voici un jeu national de l'annuaire Service-public recensant les guichets publics locaux sur **data.gouv.fr** :

- **Titre** : *Annuaire de l'administration - Base de données locales*
- **Producteur** : *Région des Pays de la Loire*
- **Date de dernière mise à jour** : *Non précisée dans les métadonnées initiales* (à vérifier sur le lien du jeu de données).
- **Lien** : [Accéder au jeu de données](https://www.data.gouv.fr/datasets/annuaire-de-ladministration-base-de-donnees-locales)

---
**À vérifier** :
- La **licence** (ex. : Open Data France, Open Government Licence) et la **fréquence de mise à jour** (ex. : *"Mise à jour mensuelle"* ou *"Mise à jour trimestrielle"*) sont disponibles dans les métadonnées complètes du jeu de données (lien ci-dessus).
- Si la région de votre département n'est pas concernée, consultez les jeux de données de la **Région Île-de-France** (*Annuaire de l'administration francilienne*) ou de la **Région Centre-Val de Loire** (à vérifier sur [data.gouv.fr](https://www.data.gouv.fr/explore/datasets?search=annuaire+guichets+mairie)).

Souhaitons que cela vous aide !

Sources citées :
- Annuaire de l’administration - Base de données locales — https://www.data.gouv.fr/datasets/annuaire-de-ladministration-base-de-donnees-locales
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
Voici le jeu de données correspondant à ta recherche :

- **Titre** : Médecins accrédités par la HAS
- **Producteur** : Haute Autorité de santé
- **Lien** : [Accéder au jeu de données](https://www.data.gouv.fr/datasets/medecins-accredites-par-la-has)

---
**Autres jeux de données liés à la HAS** (non pertinents pour ta demande initiale, mais disponibles si tu les cherches par curiosité) :

- **Textes des publications de la HAS** (producteur : Haute Autorité de santé)
- **Métadonnées des publications de la HAS** (producteur : Haute Autorité de santé)

Si tu veux explorer les ressources de ce jeu de données, je peux te les lister.

Sources citées :
- Médecins accrédités par la HAS — https://www.data.gouv.fr/datasets/medecins-accredites-par-la-has
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
Voici les informations concernant l'indice de position sociale (IPS) du collège dont l'UAI est **0010005A** à la rentrée scolaire 2022-2023, selon les données nationales publiées sur **data.gouv.fr** :

---

### **1. Indice de position sociale (IPS)**
- **IPS** : **110,4** (donnée pour la rentrée scolaire 2022-2023).
- **Écart-type de l'IPS** : **31,3** (donnée pour la rentrée scolaire 2022-2023).

---

### **2. Nom du collège, commune et effectifs**
- **Nom de l'établissement** : **COLLEGE ROGER POULNARD**
- **Commune** : **BAGE DOMMARTIN** (département AIN, 01)
- **Effectifs** : **540** (donnée pour la rentrée scolaire 2022-2023).

---

### **Source**
- **Jeu de données** : *Indices de position sociale dans les collèges (2022)* [lien](https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-colleges-a-partir-de-2022)
- **Producteur** : Ministères de l'Éducation nationale.
- **Dernière mise à jour** : *Non précisée dans les métadonnées du jeu de données* (vérification via l'outil `get_dataset_info`).

---

### **Prochaine piste**
Si vous souhaitez explorer d'autres jeux de données (ex. : indices de position sociale des lycées, ou des données régionales comme la Haute-Garonne), je peux effectuer une recherche supplémentaire.

Sources citées :
- Indices de position sociale dans les collèges (2022) — https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-colleges-a-partir-de-2022
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
Voici les informations concernant le fichier **FINESS Extraction du Fichier des établissements** (non géolocalisé) sur **data.gouv.fr** :

### 1. Interrogeable via l'API tabulaire ?
**Oui**, le fichier **"Extraction Finess des Etablissements au 04/05/2026"** (CSV, 34,1 MB) est interrogeable via l'API tabulaire de data.gouv.fr. Il contient des données tabulaires (établissements, adresses, etc.) et peut être consulté directement sans téléchargement.

---

### 2. Si ce n'est pas le cas, la taille et l'URL du fichier
Le fichier **"Extraction Finess des Etablissements géolocalisés au 04/05/2026"** (CSV, 45,7 MB) est **non interrogeable** via l'API tabulaire (car il est géolocalisé). Sa taille et son URL de téléchargement sont :
- **Taille** : 45,7 MB
- **URL** : [Télécharger le fichier](https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091152/etalab-cs1100507-stock-20260512-0339.csv)

---

### Prochaine étape
Si vous souhaitez interroger le fichier **non géolocalisé** (établissements sans adresse), vous pouvez utiliser l'API tabulaire pour cette ressource. Si vous avez besoin d'une autre piste, je peux explorer les autres jeux de données (ex. : *"FINESS Extraction des entités juridiques"* ou *"FINESS Extraction des autorisations d'activités de soin"*).

Sources citées :
- Extraction Finess des Etablissements géolocalisés au 04/05/2026. — https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091152/etalab-cs1100507-stock-20260512-0339.csv
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
  "litige": true,
  "methode": "identifiant",
  "reponse_exacte": null
}
```

### Verdicts

**Juge principal** : juge

- `libelle_correct` : 0 — Le libellé « FINESS Extraction du Fichier des établissements » est correct mais sans identifiant, et la réponse affirme à tort « Oui, ... est interrogeable via l'API tabulaire » alors que la référence indique « Not available via Tabular API », puis fournit la taille (45,7 MB) et l'URL de la version géolocalisée au lieu de 34.1 MB et de l'URL etalab-cs1100502.
- Inventions : Le fichier non géolocalisé serait interrogeable via l'API tabulaire; Le fichier géolocalisé serait non interrogeable « car il est géolocalisé »; Taille de 45,7 MB pour le fichier géolocalisé (non vérifiable dans les références); URL https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091152/etalab-cs1100507-stock-20260512-0339.csv (non vérifiable dans les références); Le fichier non géolocalisé décrit comme « établissements sans adresse »; Jeux « FINESS Extraction des entités juridiques » et « FINESS Extraction des autorisations d'activités de soin » (non vérifiables)
- Confiance : haute

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
**Résumé (80 mots max.)**

Votre demande de logement peut être radiée pour plusieurs raisons :
- Revenus supérieurs au plafond.
- Non renouvelée dans 11 mois.
- Non réponsive aux courriers.
- Non signee au bail.
- Plusieurs demandes regroupées.

**Délais et obligations** :
- Avertissement par lettre recommandée, puis radiée 1 mois après.
- Contester : adressez-vous à l’organisme qui a radié (mairie ou HLM).
- Si radiée, un nouveau numéro d’enregistrement est attribué.
- Si radiée, un nouveau logement social est demandé.

**Personnes concernées** :
- Les maires et organismes HLM.
- Les guichetts enregistreurs (départements listés).

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "courte",
  "mots": 84,
  "plafond_mots": 80,
  "respect_longueur": false
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé déforme le document : « Non signee au bail » inverse le motif réel (la radiation intervient à la signature du bail), et il généralise à toute radiation le nouveau numéro et la nouvelle demande, qui ne concernent que le non-renouvellement.
- `presence_elements` :
  - P1 : 1 — Les revenus supérieurs au plafond, l'absence de réponse aux courriers, l'« avertissement par lettre recommandée, puis radiée 1 mois après » sont mentionnés.
  - P2 : 0 — Le « Non renouvelée dans 11 mois » et le nouveau numéro sont cités, mais la radiation sans délai est absente et le nouveau numéro est faussement étendu à tous les cas.
  - P3 : 0 — La signature du bail est déformée en « Non signee au bail » et la renonciation écrite est absente.
  - P4 : 1 — Le résumé indique « Contester : adressez-vous à l'organisme qui a radié » et mentionne les guichets enregistreurs des départements listés.
- Inventions : Non signee au bail (motif de radiation inversé par rapport au document); Si radiée, un nouveau numéro d'enregistrement est attribué (généralisé à toutes les radiations); Si radiée, un nouveau logement social est demandé (formulation déformée); Personnes concernées : les maires et organismes HLM (catégorie absente du document)
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
**Résumé de la procédure de changement de prénom**

La procédure de changement de prénom est ouverte à :
- Français né en France ;
- Français né à l’étranger dont l’acte de naissance a été déclaré aux postes consulaires français ou transcrit au service central d’état civil ;
- Etranger né en France ;
- Personne bénéficiant de la protection internationale.

**Cas majeur** : La demande est faite par le demandeur. Depuis le 1er juillet 2022, un majeur sous tutelle peut demander sans être représenté par son tuteur.

**Cas mineur** : La demande doit être faite par le représentant légal de l’enfant. Si l’enfant a plus de 13 ans, son accord est nécessaire. En cas d’exercice conjoint de l’autorité parentale, les deux parents doivent demander. Si les parents sont en désaccord, le parent qui veut demander saisit le juge aux affaires familiales.

**Objet de la demande** :
- L’ajout, la suppression ou la modification de l’ordre des prénoms ;
- L’intérêt légitime doit être justifié (usage prolongé d’un prénom, suppression d’un prénom jugé ridicule, association nom/prénoms jugée ridicule, ajout/suppression d’un tiret, transidentité du demandeur).

**Exclusions** :
- La demande ne peut pas être contraire à l’intérêt de l’enfant ou aux droits d’autres personnes à voir.
- Si l’intérêt est jugé inutile, l’officier de l’état civil saisit le procureur de la République.
- Les motifs de transidentité ne doivent pas être motivés par l’adéquation physique du prénom.

**Délais et obligations** :
- La démarche est gratuite.
- La demande doit être déposée à la mairie du lieu de résidence, à la mairie qui détient l’acte de naissance (si né en France), à l’ambassade/consulat (si réside en France), ou à l’Office français de protection des réfugiés et apatrides (Ofpra) (si certificat d’acte de naissance).
- Un récépissé de dépôt est remis.
- Si l’acte de naissance est mis à jour, les titres d’identité (carte d’identité, passeport) doivent être modifiés dans un délai de 3 mois.
- Les actes de l’état civil sont mis à jour.

**Risques** :
- L’usage d’un titre d’identité qui ne correspond pas à l’état civil est puni de 5 ans d’emprisonnement maximum et d’une amende pouvant aller jusqu’à 50 000 €.
- En cas de refus, le recours est possible auprès du juge aux affaires familiales (avocat obligatoire).

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 352,
  "plafond_mots": 400,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé contient plusieurs déformations : « à l'ambassade/consulat (si réside en France) » au lieu d'un résident à l'étranger, « Si l'intérêt est jugé inutile » au lieu de « n'a pas d'intérêt légitime », une phrase tronquée sur les droits des tiers (« droits d'autres personnes à voir. ») et une reformulation erronée de la règle sur la transidentité.
- `presence_elements` :
  - P1 : 1 — Les quatre catégories de bénéficiaires sont listées.
  - P2 : 1 — Le cas majeur (y compris sous tutelle depuis le 1er juillet 2022) et le cas mineur (représentant légal, accord au-delà de 13 ans, deux parents, juge aux affaires familiales en cas de désaccord) sont repris.
  - P3 : 1 — L'ajout, la suppression, l'ordre, l'intérêt légitime et l'intérêt de l'enfant sont mentionnés ; la partie sur les droits des tiers est tronquée.
  - P4 : 0 — La règle selon laquelle tout prénom de l'acte peut devenir prénom usuel est absente.
  - P5 : 1 — La gratuité, les lieux de dépôt et le récépissé sont mentionnés, mais avec une erreur sur le consulat.
  - P6 : 0 — Seule la saisine pour défaut d'intérêt figure ; les condamnations, le Fijait/Fijaisv, l'information du demandeur et la décision du procureur manquent.
  - P7 : 1 — Le recours devant le juge aux affaires familiales avec avocat obligatoire est cité.
  - P8 : 0 — La règle est déformée et la mention des prénoms neutre, épicène, féminin ou masculin est absente.
  - P9 : 1 — La mise à jour des actes, la modification des titres sous 3 mois et les sanctions (5 ans, 50 000 €) sont présentes.
- Inventions : à l'ambassade/consulat (si réside en France); Si l'intérêt est jugé inutile; Les motifs de transidentité ne doivent pas être motivés par l'adéquation physique du prénom
- Confiance : haute

**Juge second** : juge

- `fidelite` : 1 — Aucune information absente du document ni déformée : tous les éléments clés sont repris fidèlement et sans ajout non vérifiable.
- `presence_elements` :
  - P1 : 1 — Les bénéficiaires de la procédure sont correctement listés (Français nés en France, Français nés à l'étranger, étrangers nés en France, bénéficiaires de la protection internationale).
  - P2 : 1 — Les cas majeur (y compris sous tutelle) et mineur (accord à partir de 13 ans, rôle des parents et du juge en cas de désaccord) sont bien décrits.
  - P3 : 1 — Les possibilités de changement, ajout, suppression ou modification de l'ordre des prénoms, ainsi que la nécessité d'un intérêt légitime, sont mentionnées.
  - P4 : 1 — La mention 'Tout prénom inscrit dans l'acte de naissance peut être choisi comme prénom usuel' est implicite dans la section sur l'intérêt légitime (usage prolongé).
  - P5 : 1 — La gratuité, les lieux de dépôt (mairie, ambassade, Ofpra) et la remise d'un récépissé sont correctement indiqués.
  - P6 : 1 — Le rôle de l'officier d'état civil (saisie du procureur en cas de doute sur l'intérêt légitime ou de condamnations) est bien expliqué.
  - P7 : 1 — Le recours devant le juge aux affaires familiales en cas de refus, avec l'obligation d'un avocat, est mentionné.
  - P8 : 1 — La spécificité des motifs de transidentité (pas de motivation par l'adéquation physique, prénom neutre/épicène possible) est correctement reprise.
  - P9 : 1 — La mise à jour des actes d'état civil, l'obligation de modifier les titres d'identité sous 3 mois et les sanctions en cas de non-respect sont bien détaillées.
- Inventions : aucune
- Confiance : haute

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
**Résumé pour un couple souhaitant se pacser en mairie**

**Objet et conditions**
Un pacte civil de solidarité (Pacs) peut être conclu par un couple de même ou de sexe différent, quel que soit le pays. Les deux partenaires doivent être majeurs, non mariés ou pacsés, et ne pas avoir de lien familial direct ou trop proche. Ces conditions sont impératives.

**Documents à fournir**
- Les deux partenaires doivent remplir les conditions ci-dessus.
- Un contrat de Pacs (convention) rédigé en français, signé par les deux, avec leurs signatures.
- Une attestation sur l’honneur pour déclarer l’adresse commune.
- Un dossier contenant les documents justificatifs (pièces d’identité, justificatifs de revenus, etc.).

**Types de contrat**
- **Convention minimale** : reprend le texte standard de la loi du 15 novembre 1999 modifiée et les articles 515-1 à 515-7 du code civil. Les biens sont séparés (régime de séparation).
- **Convention personnalisée** : reprend le texte standard, mais précise les conditions de participation à la vie commune, y compris la partage de biens (régime de l’indivision). Les biens sont séparés en l’absence de précisions.
- **Convention rédigée par un notaire** : possible, mais coûteux.

**Enregistrement**
- Le Pacs doit être enregistré en mairie de résidence commune (gratuit). Un rendez-vous est généralement nécessaire, mais certaines communes offrent une pré-demande en ligne via le téléservice.
- L’enregistrement se fait en personne, avec l’officier d’état civil. En cas d’empêchement grave, l’enregistrement peut se faire à domicile ou à l’hôpital.
- Le contrat de Pacs est restitué, mais il ne peut pas être copié en cas de perte. En cas de perte, une convention modificative est rédigée et enregistrée.

**Effets et transmission**
- Le Pacs produit ses effets à partir de la date d’enregistrement.
- L’information est indiquée sur l’acte de naissance (si né en France) ou sur le registre des Pacs des étrangers (si né à l’étranger).
- Les références du Pacs (numéro et date d’enregistrement) sont conservées sur le récépissé d’enregistrement et l’acte de naissance.

**Personnes concernées**
- Les deux partenaires (couple).
- L’officier d’état civil de la mairie de résidence commune.
- Un notaire (option).

**Délais et montants**
- Le Pacs est gratuit en mairie.
- Le notaire est payant.
- Le téléservice de pré-demande est gratuit.
- Aucun montant n’est fixé pour l’enregistrement.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 356,
  "plafond_mots": 400,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé contient des informations absentes du document, comme « justificatifs de revenus » et « Le téléservice de pré-demande est gratuit ». Il déforme aussi « quelle que soit votre nationalité » en « quel que soit le pays ».
- `presence_elements` :
  - P1 : 1 — Le résumé indique l'ouverture aux couples de même sexe ou de sexe différent, la gratuité en mairie et le coût du notaire, mais il omet l'ambassade ou le consulat.
  - P2 : 1 — L'enregistrement « en mairie de résidence commune » est mentionné, mais pas la variation des démarches selon les communes.
  - P3 : 1 — Les trois conditions et leur caractère impératif sont repris, sans la précision sur la majorité fixée par le pays d'un partenaire étranger.
  - P4 : 0 — Seule l'attestation sur l'honneur est citée ; l'engagement à une vie commune et l'absence d'obligation de vivre ensemble manquent.
  - P5 : 1 — Le contrat en français signé par les deux, la formule légale, les conventions minimale ou personnalisée, la séparation des patrimoines et l'indivision sont présents.
  - P6 : 1 — La pré-demande en ligne, le rendez-vous, la présence en personne et le déplacement en cas d'empêchement grave sont mentionnés.
  - P7 : 1 — La restitution du contrat, l'impossibilité d'en obtenir une copie et la convention modificative sont cités, mais pas la copie du récépissé.
  - P8 : 0 — Le résumé ne distingue pas les effets entre partenaires et les effets à l'égard des tiers.
  - P9 : 0 — Les moyens de preuve de l'enregistrement ne sont pas énumérés.
- Inventions : Un dossier contenant les documents justificatifs (pièces d'identité, justificatifs de revenus, etc.); Le téléservice de pré-demande est gratuit; quel que soit le pays (déformation de « quelle que soit votre nationalité »); Aucun montant n'est fixé pour l'enregistrement
- Confiance : moyenne
