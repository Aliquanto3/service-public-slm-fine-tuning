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
Consigne :
Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.

Texte :
Note à l'attention des agents du service urbanisme

Objet : modalités du télétravail à compter du 1er décembre 2026

À la suite de la réunion du comité social territorial du 15 octobre, le télétravail sera ouvert aux agents du service urbanisme dont les missions le permettent. Chaque agent pourra télétravailler un jour par semaine, choisit en accord avec son responsable. Les jours de permanence au guichet, le mardi et le jeudi, ne pourront pas être télétravaillé.

Les demandes devront être adressées au service des ressources humaines avant le 13 novembre, au moyen du formulaire joint. Un ordinateur portable et un casque seront remis à chaque agent dont la demande aura été acceptée. Les agents s'engagent à rester joignables pendant les plages fixes, de 9 heures à 12 heures et de 14 heures à 16 heures.

Une période d'adaptation de trois mois est prévue. À l'issue de cette période, un bilan sera fait avec chaque agent afin de vérifier que l'organisation retenue convient à la fois à l'agent et au service.

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
    false,
    true,
    true,
    true,
    true,
    true
  ],
  "mots_inseres_hors_faute": 14,
  "mots_modifies_hors_faute": 0,
  "mots_texte": 174,
  "rappel": 0.75,
  "taux_hors_faute": 0.0805
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
Si vous êtes admis à un concours d'accès à la fonction publique et si vous étiez auparavant dirigeant d'une société ou d'une association à but lucratif, vous pouvez continuer à exercer cette activité de dirigeant pendant un an, renouvelable une fois, à partir de votre recrutement dans la fonction publique. Cela s'applique aussi si vous êtes recruté en tant que contractuel dans la fonction publique. Vous devez présenter une déclaration écrite à votre autorité hiérarchique dès votre nomination en tant que fonctionnaire stagiaire ou avant la signature de votre contrat. Cette déclaration mentionne la forme et l'objet social de l'entreprise ou de l'association, son secteur et son branche d'activité. La poursuite de cette activité de dirigeant doit être compatible avec vos obligations de service. Elle ne doit pas porter atteinte au fonctionnement normal, à l'indépendance, à la neutralité du service ou aux principes déontologiques. Cette activité ne doit pas non plus vous placer dans une situation de conflit d'intérêts.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 11,
  "fautes": 12,
  "fautes_corrigees": [
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    false,
    true,
    true,
    true
  ],
  "mots_inseres_hors_faute": 0,
  "mots_modifies_hors_faute": 2,
  "mots_texte": 159,
  "rappel": 0.9167,
  "taux_hors_faute": 0.0126
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
**Compte rendu du point hebdomadaire de service propreté urbaine**

**Participants :**
R. Duquesne (responsable du service propreté), P. Ribeiro (chef d'équipe secteur nord), G. Tessier (chef d'équipe secteur sud), K. Bouaziz (agent de maîtrise), Mme Loiseau (adjointe au maire cadre de vie).

**Points abordés :**
1. Dépôts sauvages rue du Moulin-Brûlé : 3e dépôt en 15 jours (gravats et électroménager). Intervention de l'équipe nord avec 2 rotations de camion.
2. Balayeuse n°2 en panne : pompe hydraulique hors service, pièce commandée avec délai de 3 semaines.
3. Plan feuilles mortes : démarrage du ramassage le lundi 12 octobre 2026 avec 2 agents en renfort.
4. Cimetière / Toussaint : nettoyage renforcé des allées et abords du cimetière la semaine du 26 octobre, avant le 1er novembre.
5. Tags école Jean-Moulin : intervention de l'équipe sud avec l'hydrogommeuse avant le vendredi 2 octobre.
6. Divers / sécurité : commande d'EPI pour 2 agents sans gilets haute visibilité neufs ; demande de passage aux horaires d'hiver en octobre au lieu du 1er décembre.

**Décisions prises :**
- Location d'une balayeuse de remplacement pour 3 semaines (devis initial 2 400 € HT, ajusté à 2 040 € HT sur le budget fonctionnement propreté) avec livraison au plus tard le jeudi 1er octobre.
- Nettoyage renforcé du cimetière la semaine du 26 octobre, avant le 1er novembre.
- Intervention de l'équipe sud sur les tags de l'école Jean-Moulin avant le vendredi 2 octobre.
- Commande d'EPI pour les agents en situation de non-respect des normes de sécurité.

**Actions à mener :**
- **Responsable :** R. Duquesne
- **Echéance :** À définir (prochain point hebdomadaire : lundi 5 octobre, 7h30).
- **Responsable :** P. Ribeiro
- **Echéance :** Avant le vendredi 2 octobre.
- **Responsable :** G. Tessier
- **Echéance :** Avant le lundi 12 octobre 2026.
- **Responsable :** K. Bouaziz
- **Echéance :** Au plus tard le jeudi 1er octobre.
- **Responsable :** R. Duquesne
- **Echéance :** À définir (prochain point hebdomadaire : lundi 5 octobre, 7h30).

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Décision présente : « Location d'une balayeuse de remplacement pour 3 semaines (…) ajusté à 2 040 € HT sur le budget fonctionnement propreté », avec le bon montant final.
  - D2 : 0.5 — Le démarrage au 12 octobre avec 2 agents en renfort figure seulement dans « Points abordés », sans être présenté comme une décision et sans préciser que les renforts viennent des espaces verts.
  - D3 : 1 — Décision présente : « Nettoyage renforcé du cimetière la semaine du 26 octobre, avant le 1er novembre » (l'équipe sud est omise dans la décision).
  - A1 : 0 — La transmission des photos et du numéro de courrier à la police municipale n'apparaît nulle part ; la ligne « R. Duquesne – À définir » ne décrit aucune action.
  - A2 : 0.5 — La ligne « K. Bouaziz – Au plus tard le jeudi 1er octobre » ne nomme pas l'action (réservation), qui ne se déduit que de la décision de location.
  - A3 : 0 — Le planning des circuits feuilles n'est pas décrit, et la ligne « G. Tessier – Avant le lundi 12 octobre 2026 » donne une échéance erronée (point hebdo du 5 octobre).
  - A4 : 0 — La coordination avec le conservateur du cimetière est absente.
  - A5 : 0.5 — L'intervention sur les tags avant le 2 octobre figure en décision, mais le responsable est faux : « P. Ribeiro – Avant le vendredi 2 octobre » au lieu de G. Tessier.
  - A6 : 0.5 — La commande d'EPI est mentionnée, mais sans responsable clairement associé ni échéance « cette semaine » (« À définir »).
- `absence_invention` : 0 — Plusieurs éléments sont absents des notes : P. Ribeiro désignée responsable avec l'échéance « Avant le vendredi 2 octobre », l'échéance « Avant le lundi 12 octobre » attribuée à Tessier, l'échéance « À définir » pour Duquesne alors que les notes indiquent « aujourd'hui » et « cette semaine », et la formule « agents en situation de non-respect des normes de sécurité ».
- `structure` : 1 — Les quatre sections (Participants, Points abordés, Décisions prises, Actions à mener) sont présentes, même si la section Actions ne décrit pas les actions.
- Inventions : P. Ribeiro responsable d'une action avec échéance « Avant le vendredi 2 octobre »; Échéance « Avant le lundi 12 octobre 2026 » pour G. Tessier; Échéance « À définir » pour R. Duquesne (les notes disent « aujourd'hui » et « cette semaine »); « agents en situation de non-respect des normes de sécurité »
- Confiance : haute

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
**Objet :** Compte rendu de la séance de l'équipe pluridisciplinaire RSA – territoire d'action sociale du Haut-Orlan

**Participants :**
M. Faure (France Travail), Mme Nkomo (assistante sociale de la MDS), M. Gallet (Atelier du Pont), M. Le Goff (Atelier du Pont), Mme Jacquet (secrétariat), Mme Aubertin (présidente de l'équipe pluridisciplinaire).

**Points abordés :**
Six dossiers ont été traités au cours de la réunion :
1.  **Mme L. D. (41 ans) :** Réorientation vers le parcours professionnel par France Travail suite à des soucis de santé stabilisés et un logement réglé. Avis unanimité.
2.  **M. K. A. (56 ans) :** Réorientation vers le parcours social suite à un logement perdu, des problèmes de santé et une absence aux rendez-vous. Avis unanimité.
3.  **M. R. S. (29 ans) :** Manquement à trois rendez-vous et absence d'activité depuis juin. Proposition initiale de suspension-remobilisation de 100 % a été modifiée par Mme Aubertin en faveur d'une suspension-remobilisation de 30 % pendant un mois avec levée en cas de reprise de contact. M. Gallet défavorable à la modification. Avis à la majorité.
4.  **Mme F. M. (34 ans) :** Absences aux ateliers collectifs. Justificatif de hospitalisation de son fils a été reçu. Avis de maintien du RSA sans sanction.
5.  **M. J.-P. V. (47 ans) :** Non-respect des heures d'activité en août suite à une mission d'intérim. Avis de maintien du RSA sans réduction.
6.  **Mme N. R. :** Demande d'audition. Convocation reçue le lundi, date limite pour audition le jeudi 15 octobre. Avis de report à la prochaine séance.

**Décisions prises :**
*   Avis unanimité sur la réorientation de Mme L. D. vers le parcours professionnel.
*   Avis unanimité sur la réorientation de M. K. A. vers le parcours social.
*   Modification de la proposition de suspension-remobilisation pour M. R. S. de 100 % à 30 % pendant un mois, avec levée en cas de reprise de contact.
*   Avis de maintien du RSA pour Mme F. M. et M. J.-P. V. sans sanction ou réduction.
*   Mise à jour du contrat d'engagement de M. J.-P. V. avant le 15 octobre.
*   Transmission de l'ensemble des avis au service RSA pour la décision du président du conseil départemental.

**Actions à mener :**
*   **Responsable :** M. Faure (France Travail).
*   **Echéance :** Transmettre les avis au service RSA d'ici le vendredi 25 septembre.
*   **Responsable :** M. Faure.
*   **Echéance :** Vérifier le contrat de mission de M. J.-P. V. et le mettre à jour avant le jeudi 15 octobre.
*   **Responsable :** M. Faure.
*   **Echéance :** Appeler M. R. S. le jeudi 15 octobre pour la convocation.
*   **Responsable :** Mme Jacquet.
*   **Echéance :** Transmettre l'ensemble des avis au service RSA d'ici le vendredi 25 septembre.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « Avis unanimité sur la réorientation de Mme L. D. vers le parcours professionnel », avec le suivi par France Travail mentionné dans les points abordés.
  - D2 : 1 — « Avis unanimité sur la réorientation de M. K. A. vers le parcours social » est présent.
  - D3 : 1 — Le compte rendu indique 30 % pendant un mois, la levée en cas de reprise de contact, l'avis à la majorité et l'opposition de M. Gallet.
  - D4 : 1 — « Avis de maintien du RSA sans sanction » pour Mme F. M. figure, au vu du justificatif d'hospitalisation.
  - D5 : 1 — « Avis de maintien du RSA sans réduction » pour M. J.-P. V. figure.
  - D6 : 1 — « Avis de report à la prochaine séance » figure, et la date du 15 octobre est mentionnée.
  - A1 : 0 — La désignation d'un conseiller et le premier rendez-vous avant le 16 octobre pour Mme L. D. sont absents.
  - A2 : 0 — La désignation d'un référent social de la MDS sous un mois par Mme Nkomo est absente.
  - A3 : 0.5 — L'appel de M. R. S. par M. Faure figure, mais l'échéance est fausse (« le jeudi 15 octobre » au lieu du vendredi 18 septembre) et l'objet est erroné (« pour la convocation »).
  - A4 : 0 — La réinscription éventuelle de Mme F. M. aux ateliers d'octobre est absente.
  - A5 : 1 — Le compte rendu indique que M. Faure vérifie le contrat de mission et met à jour le contrat d'engagement avant le jeudi 15 octobre.
  - A6 : 0 — La reconvocation de Mme N. R. par Mme Jacquet avant le 30 septembre est absente.
  - A7 : 1 — « Mme Jacquet. Transmettre l'ensemble des avis au service RSA d'ici le vendredi 25 septembre » figure.
- `absence_invention` : 0 — Plusieurs inventions figurent, dont « Manquement à trois rendez-vous » (piège : il s'agit de deux rendez-vous) et « M. Gallet (Atelier du Pont) ».
- `structure` : 1 — Les quatre sections Participants, Points abordés, Décisions et Actions sont présentes.
- Inventions : M. Gallet présenté comme membre de l'Atelier du Pont (il est représentant des allocataires); M. K. A. : « une absence aux rendez-vous » (il est assidu); M. R. S. : « Manquement à trois rendez-vous » (deux, correction en séance); M. Faure responsable de la transmission des avis au service RSA (c'est Mme Jacquet); « Appeler M. R. S. le jeudi 15 octobre pour la convocation » (appel prévu le vendredi 18 septembre, avant la notification); Mme N. R. : « date limite pour audition le jeudi 15 octobre »
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
# Compte rendu de la réunion publique de concertation sur le projet « Cœur de bourg »

**Objet :** Concertation préalable sur l'aménagement du centre-bourg (RD 812, place de la Halle, rue de la République) et suivi du projet.

**Participants :**
M. Bernard Lacoste (Maire), Mme Isabelle Fauré (1re adjointe à l'urbanisme), M. Didier Roucayrol (adjoint au commerce et à l'artisanat), Mme Anne Teyssier (Directrice générale des services), Mme Solène Marquet (Paysagiste-urbaniste), M. Hugo Brissac (Ingénieur VRD), Mme Lucie Garrigues (Conseillère municipale d'opposition), M. Gérard Pons (Riverain), M. Jean-Marc Cazals (Boulanger), Mme Odile Vergnes (Présidente du club des aînés), M. Kevin Lafarge (Association Valbrézac à vélo), Mme Martine Delpech (Riveraine), Mme Fatima Ould-Ali (Parent d'élève), Mme Sandrine Mathieu (Assistante maternelle), M. Lucien Arnal (Maraîcher), ainsi que plusieurs habitants non identifiés.

**Points abordés :**
*   **Nature de la réunion :** Concertation préalable selon le code de l'urbanisme. Le bureau d'études présentera un diagnostic et trois scénarios d'aménagement.
*   **Contexte du projet :** Redonner envie de venir dans le bourg en redéfinissant le centre-bourg (RD 812, place de la Halle, rue de la République).
*   **Diagnostic et chiffres :** RD 812 (6 800 véhicules/jour, 9 % poids lourds), périmètre d'étude (112 places de stationnement, 64 sur la place de la Halle), marché du mercredi (22 exposants en moyenne), état des platanes (7 sur la place, 3 en mauvais état).
*   **Les trois scénarios :**
    *   **Scénario A (Ambitieux) :** Place de la Halle entièrement piétonne (suppression des 64 places), création d'un parking de 30 places derrière la poste, rue de la République en sens unique, trottoirs élargis à 1,80 m. **Coût estimé : 2,4 millions d'euros hors taxes.**
    *   **Scénario B (Partagé) :** Place partagée (22 places gardées), espace piéton avec terrasses/bancs, traversée en zone de rencontre à 20 km/h, rue de la République double sens, trottoirs élargis. **Coût estimé : 1,9 million d'euros hors taxes.**
    *   **Scénario C (Minimal) :** Refonte des trottoirs et revêtements, maintien du stationnement. **Coût estimé : 900 000 euros hors taxes.**
    *   **Points communs :** Refonte des toilettes publiques (à neuf) et maintien de la halle telle qu'elle est.
*   **Questions et objections :**
    *   **Platanes :** M. Lacoste a demandé un diagnostic phytosanitaire avant abattage (Mme Fauré a commandé les 7 platanes avant la fin octobre).
    *   **Halle :** M. Arnal souhaite qu'elle reste sur la place (mercredi) ou soit transformée en marché couvert (idée de Mme Delpech, mais coût non chiffré).
    *   **Stationnement et livraisons :** M. Cazals craint l'arrêt des commerces (3 minutes de marche). M. Brissac a promis une étude des itinéraires de livraison pour les projets A et B.

**Décisions et actions :**
*   **Prolongation de la concertation :** Le registre et l'adresse mail restent ouverts jusqu'au **vendredi 13 novembre** (décalé de 18 jours par rapport au 31 octobre), en raison de la présence de nombreux intervenants et des vacances de la Toussaint.
    *   *Responsable :* M. Lacoste.
    *   *Echéance :* 13 novembre.
*   **Balade urbaine :** Organisation d'une marche dans le bourg le **samedi 17 octobre à 10 heures**, départ devant la halle, à l'organisation de Mme Fauré.
    *   *Responsable :* Mme Fauré.
    *   *Echéance :* Samedi 17 octobre à 10 heures.
*   **Création d'un comité de

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0 — Le compte rendu, tronqué, ne mentionne pas que la municipalité écarte le scénario C ; ce scénario n'apparaît que dans la description des options.
  - D2 : 1 — La prolongation est présente : « restent ouverts jusqu'au vendredi 13 novembre ».
  - D3 : 1 — La balade urbaine du samedi 17 octobre à 10 h, départ devant la halle, est mentionnée.
  - D4 : 0 — Le maintien du marché sur la place n'est pas présenté comme une décision : la sortie le formule comme un simple souhait (« M. Arnal souhaite qu'elle reste sur la place ») et confond halle et marché.
  - D5 : 0 — Le texte s'interrompt sur « Création d'un comité de », sans composition ni mention de Mme Garrigues.
  - D6 : 1 — Le principe d'aucun abattage sans diagnostic et la commande pour les 7 platanes sont mentionnés.
  - D7 : 0 — Le conseil municipal du 10 décembre n'est pas mentionné.
  - D8 : 0 — La deuxième réunion publique prévue en janvier n'est pas mentionnée.
  - A1 : 1 — L'action est présente avec Mme Fauré comme responsable et l'échéance « avant la fin octobre ».
  - A2 : 0.5 — L'étude des itinéraires par M. Brissac figure, mais sans l'échéance connue (deuxième réunion publique).
  - A3 : 0 — Le contact avec le propriétaire et l'établissement public foncier est absent.
  - A4 : 0 — Le courrier au président du conseil départemental est absent.
  - A5 : 0 — L'annexion de la pétition au registre est absente.
  - A6 : 0 — La préparation des dossiers de subvention est absente.
  - A7 : 0 — Le comptage du stationnement est absent.
  - A8 : 0 — La variante « B plus » est absente.
  - A9 : 0 — L'étude de l'espace de jeux est absente.
  - A10 : 1 — L'organisation de la balade est attribuée à Mme Fauré, avec l'échéance du 17 octobre.
  - A11 : 0 — La centralisation des candidatures au comité est absente, le texte étant tronqué.
  - A12 : 0 — La mise en ligne de la présentation et du compte rendu est absente.
- `absence_invention` : 0 — La sortie contient un chiffre faux (« décalé de 18 jours », alors que l'écart est de 13 jours) et des déformations : « 3 minutes de marche » au lieu d'un arrêt de 3 minutes, « Mme Fauré a commandé » alors que la commande est à venir, et la halle présentée comme devant « rester sur la place ».
- `structure` : 0 — Les décisions et les actions sont fusionnées en une seule section, et le compte rendu est tronqué.
- Inventions : « décalé de 18 jours par rapport au 31 octobre » (l'écart réel est de 13 jours); « M. Cazals craint l'arrêt des commerces (3 minutes de marche) » (il s'agit en réalité d'un arrêt de 3 minutes); « Mme Fauré a commandé les 7 platanes » (la commande est annoncée, pas effectuée); « M. Arnal souhaite qu'elle [la halle] reste sur la place » (confusion avec le marché); « en raison de la présence de nombreux intervenants »
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
**Objet :** Compte rendu de la réunion de chantier n°14 – rénovation du gymnase des Aubiers – Courtenac-sur-Brize

**Participants :**
- Maître d'œuvre (MOE) : Mme Vernhes (architecte mandataire, Atelier Vernhes), M. Hamon (conducteur d'opération, Atelier Vernhes)
- Commune (MOA) : M. Paquet (responsable bâtiments, services techniques), Mme Ferrand (adjointe aux sports)
- Lot 2 gros œuvre : M. Lacombe (Maçonnerie Lacombe)
- Lot 4 couverture-étanchéité : M. Diaz (Étanch'Ouest)
- Lot 7 sols sportifs : Mme Duclos (Sols & Sports Duclos)

**Points abordés :**
1. Avancement des travaux : reprise de la dalle principale (Lot 2), fin de la couverture (Lot 4), attente pour la pose des sols sportifs (Lot 7), état des chemins de câbles (Lot 9).
2. Planning et réception : retard cumulé de deux semaines, proposition de décalage de la date de réception initialement fixée au 20 novembre, correction à vendredi 27 novembre 2026.
3. Travaux supplémentaires : mise en conformité de deux portes coupe-feu (devis 3 840 € HT) et option de peinture des murs de la salle principale (devis ~11 000 € HT).
4. Choix techniques : validation des coloris du sol sportif (bleu et gris clair) et demande d'information sur l'ajout de la discipline de volley.
5. Lot 9 : mise en demeure d'absence et de non-procès des clubs pour les chemins de câbles, et évaluation de la demande d'éclairage LED renforcé.
6. Sécurité : mise en place de la clôture de chantier côté parking déplacé.

**Décisions prises :**
- La date de réception du gymnase est reportée au vendredi 27/11/2026.
- Le devis pour les deux portes coupe-feu a été accepté par la MOA et un ordre de service a été émis pour son exécution avant le 2/10.
- Les coloris du sol sportif (bleu et gris clair) sont validés.
- La demande de peinture des murs de la salle principale est reportée à l'avenir, à l'issue de l'examen budgétaire pour 2027.
- La MOA demande à M. Hamon d'envoyer un courrier de mise en demeure à l'électricité (Elec Mérignon) concernant les absences et le non-procès des clubs.
- La demande d'éclairage LED renforcé est à l'étude, mais aucun devis n'a été demandé pour l'instant.

**Actions à mener :**
- **Responsable :** M. Hamon (Atelier Vernhes)
  - Échéance : Cette semaine.
  - Action : Envoyer un courrier de mise en demeure à l'électricité (Elec Mérignon) concernant les absences et le non-procès des clubs.
- **Responsable :** M. Lacombe (Maçonnerie Lacombe)
  - Échéance : Aujourd'hui.
  - Action : Mettre en place la clôture de chantier côté parking déplacé.
- **Responsable :** M. Diaz (Étanch'Ouest)
  - Échéance : Avant la prochaine réunion (6/10).
  - Action : Réaliser les travaux d'étanchéité en acrotère suite à l'infiltration constatée côté nord après la pluie du 24/09.
- **Responsable :** Mme Duclos (Sols & Sports Duclos)
  - Échéance : Prochaine réunion.
  - Action : Apporter un échantillon du revêtement du sol sportif à la prochaine réunion.
- **Responsable :** M. Paquet (Responsable bâtiments, services techniques)
  - Échéance : À déterminer.
  - Action : Évaluer la pénalité de retard pour le lot 9 et répondre à la demande de M. Hamon concernant l'envoi du courrier de mise en demeure.
- **Responsable :** M. Ferrand (Adjointe aux sports)
  - Échéance : Avant le 16/10.
  - Action : Prévenir les clubs (basket, hand) de la réception du gymnase.
- **Responsable :** M. Hamon (Atelier Vernhes)
  - Échéance : Prochaine réunion.
  - Action : Émettre un ordre

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « La date de réception du gymnase est reportée au vendredi 27/11/2026 » figure dans les décisions.
  - D2 : 1 — L'acceptation du devis des portes coupe-feu par la MOA figure dans les décisions. Le montant de 3 840 € HT est cité dans les points abordés.
  - D3 : 1 — « Les coloris du sol sportif (bleu et gris clair) sont validés » figure dans les décisions.
  - A1 : 0 — La mesure d'humidité de la dalle prévue le 2/10 par M. Lacombe n'apparaît nulle part.
  - A2 : 1 — L'action est attribuée à M. Diaz avec l'échéance « avant la prochaine réunion (6/10) » ; seule la mention « à ses frais » est omise.
  - A3 : 1 — L'action « Prévenir les clubs (basket, hand) » est confiée à Ferrand avec l'échéance « Avant le 16/10 », malgré l'erreur « M. Ferrand ».
  - A4 : 0.5 — L'ordre de service est attribué à « M. Hamon » avec l'échéance « Prochaine réunion » au lieu de Mme Vernhes avant le 2/10, et l'action est tronquée.
  - A5 : 0.5 — La question du volley n'est évoquée que dans les points abordés (« demande d'information »), sans action ni responsable (Mme Ferrand).
  - A6 : 1 — L'action « Apporter un échantillon du revêtement » est confiée à Mme Duclos pour la prochaine réunion.
  - A7 : 1 — Le courrier de mise en demeure est confié à M. Hamon pour « cette semaine ».
  - A8 : 1 — La remise en place de la clôture est confiée à M. Lacombe pour « Aujourd'hui ».
- `absence_invention` : 0 — La sortie comporte plusieurs inventions : « date de réception initialement fixée au 20 novembre » (elle était au 13/11), la peinture présentée en décision (« reportée... examen budgétaire pour 2027 »), une action inventée pour M. Paquet sur les pénalités, et le « non-procès des clubs ».
- `structure` : 1 — Les quatre sections sont présentes : Participants, Points abordés, Décisions prises, Actions à mener.
- Inventions : Date de réception « initialement fixée au 20 novembre » (initialement le 13/11 ; le 20 n'était qu'un lapsus corrigé); Peinture des murs présentée dans les décisions comme « reportée... à l'issue de l'examen budgétaire pour 2027 » alors que rien n'a été décidé; Éclairage LED présenté dans les décisions comme « à l'étude »; « La MOA demande à M. Hamon » : c'est Hamon qui a proposé le courrier, avec l'accord de Vernhes; « non-procès des clubs » : motif inexistant dans les notes; Action inventée pour M. Paquet : « Évaluer la pénalité de retard pour le lot 9 et répondre à la demande de M. Hamon »; Ordre de service « a été émis », puis attribué à M. Hamon pour la « Prochaine réunion »; « M. Ferrand » au lieu de Mme Ferrand
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
**Compte rendu de la réunion du Comité de pilotage (COPIL) Contrat local de santé (CLS) 2024-2028**

**Objet :** Bilan et orientations du Contrat local de santé (CLS) 2024-2028 de Pontcarel.
**Participants :**
- M. Desbrosses, maire de Pontcarel (coprésident)
- Mme Laborde, délégation départementale ARS (coprésidente)
- M. Ogier, conseiller municipal délégué à la santé
- Mme Benamar, coordinatrice CLS (ville)
- Dr Lemaire, président de la CPTS du Haut-Pontcarel (visio, quitte à 11h)
- Mme Ricard, CPAM, chargée de mission prévention
- M. Vasseur, département, service autonomie (représente la directrice enfance-famille-autonomie)
- Mme Tran, directrice adjointe du centre hospitalier de Pontcarel
- Mme Haddou, asso Point Écoute Jeunes (présente pour le point 3)

**Points abordés :**
1.  **Bilan mi-parcours du CLS :** Présentation par Mme Benamar des 18 fiches-actions (4 terminées, 11 engagées, 3 non démarrées). Points forts identifiés (ateliers nutrition QPV, permanences CPAM) et faibles (axe santé environnement retardé).
2.  **Accès aux soins :** Analyse des risques liés à la retraite des médecins généralistes et l'absence de médecin traitant. Comparaison entre projet de Maison de santé pluriprofessionnelle (MSP) libérale et centre de santé municipal.
3.  **Santé mentale :** Évaluation de la hausse des demandes de soins aux 15-25 ans et des délais de prise en charge. Proposition de formation des agents municipaux et discussion sur un conseil local de santé mentale.
4.  **Prévention et santé environnementale :** Validation de la reconduction des ateliers nutrition QPV en 2027. Campagne d'information sur la détection de moustiques tigres et plan de surveillance de la qualité de l'air intérieur.
5.  **Avenant au CLS :** Adoption de principe d'un avenant n°1 intégrant la fiche-action « prévention des chutes et isolement des personnes âgées ».

**Décisions prises :**
-   La ville lance une étude d'opportunité comparant les scénarios MSP et centre de santé municipal, avec un coût estimé de 28 000 € TTC.
-   L'ARS peut cofinancer à 50 % (jusqu'à 15 000 €) via le FIR, sous réserve de validation du dossier par le comité FIR.
-   Les ateliers nutrition QPV seront reconduits en 2027 avec un financement de 4 500 € de la CPAM.
-   Une campagne d'information sur la santé environnementale sera lancée au printemps 2027.
-   Deux sessions de formation PSSM au 1er semestre 2027 seront organisées avec un financement de 6 000 € de l'ARS (déjà prévu dans la fiche-action).
-   Un avenant n°1 au CLS est adopté au COPIL pour intégrer la fiche-action sur les personnes âgées.
-   La rédaction de la fiche-action sur les personnes âgées est confiée à Mme Benamar et M. Vasseur, avec un projet à envoyer aux membres avant le 15 janvier 2027.

**Actions à mener avec responsables et échéances :**
-   **M. Desbrosses (Maire) :** Présenter le bilan au conseil municipal le jeudi 12 novembre 2026 (remplacement du 5 novembre).
-   **Mme Benamar (Coordinatrice CLS) :** Préparer la note de synthèse du CLS pour le conseil municipal avant le 30 octobre 2026.
-   **Mme Laborde (ARS) :** Valider le dossier FIR pour le cofinancement de l'avenant sur les personnes âgées avant le prochain comité FIR (début décembre 2026).
-   **M. Ogier (Conseiller municipal) :** Piloter la campagne d'information sur la santé environnementale et procéder à un état des lieux de la qualité de l'air intérieur dans les écoles.
-   **M. Vasseur (Département) :** Valider le texte de la fiche-action sur les personnes âgées et la signature de l'avenant.
-   **Mme Ricard (CPAM) :** Valider la signature

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0 — La validation du bilan à l'unanimité n'apparaît nulle part ; seule sa présentation est mentionnée.
  - D2 : 1 — Le CR indique : « La ville lance une étude d'opportunité comparant les scénarios MSP et centre de santé municipal… 28 000 € TTC », avec le cofinancement ARS sous réserve du comité FIR.
  - D3 : 1 — Le CR mentionne : « Deux sessions de formation PSSM au 1er semestre 2027… 6 000 € de l'ARS (déjà prévu dans la fiche-action) ».
  - D4 : 1 — Le CR indique : « Les ateliers nutrition QPV seront reconduits en 2027 avec un financement de 4 500 € de la CPAM ».
  - D5 : 0.5 — La décision reste vague (« campagne d'information sur la santé environnementale ») : le moustique tigre n'est cité que dans les points abordés, et les modalités (flyers, réunion de quartier) manquent.
  - D6 : 0.5 — L'avenant est mentionné mais déformé : « Un avenant n°1 au CLS est adopté au COPIL », alors qu'il ne s'agit que d'un accord de principe.
  - A1 : 1 — Le CR indique : « Mme Benamar : Préparer la note de synthèse… avant le 30 octobre 2026 ».
  - A2 : 0 — Le montage du dossier FIR par Mme Benamar est absent ; il est remplacé par une action erronée attribuée à Mme Laborde.
  - A3 : 0 — Le renforcement de M'T dents en CP n'est pas mentionné.
  - A4 : 0 — La sollicitation d'organismes de formation PSSM est absente.
  - A5 : 0 — La prise de contact avec l'infirmière conseillère technique est absente.
  - A6 : 0.5 — M. Ogier pilote bien la campagne, mais l'échéance (plan présenté au COPIL de mars) manque.
  - A7 : 1 — Le CR attribue à M. Ogier : « procéder à un état des lieux de la qualité de l'air intérieur dans les écoles » (sans date, conformément aux notes).
  - A8 : 1 — La rédaction est « confiée à Mme Benamar et M. Vasseur, avec un projet à envoyer aux membres avant le 15 janvier 2027 ».
  - A9 : 0 — L'envoi du sondage pour le prochain COPIL est absent.
  - A10 : 0 — La diffusion du compte rendu sous 15 jours est absente.
- `absence_invention` : 0 — Le CR contient plusieurs inventions et un piège : « Un avenant n°1 au CLS est adopté au COPIL », une action de Mme Laborde pour « valider le dossier FIR pour le cofinancement de l'avenant sur les personnes âgées… (début décembre 2026) » et une action de M. Vasseur pour « valider… la signature de l'avenant ».
- `structure` : 1 — Les sections Participants, Points abordés, Décisions et Actions sont présentes, même si la sortie est tronquée.
- Inventions : Avenant n°1 présenté comme « adopté au COPIL » alors qu'il ne s'agit que d'un accord de principe; Mme Laborde chargée de « valider le dossier FIR pour le cofinancement de l'avenant sur les personnes âgées » (le FIR concerne l'étude, et le dossier est monté par Mme Benamar); Comité FIR daté « début décembre 2026 » (les notes disent seulement décembre); M. Vasseur chargé de « valider le texte de la fiche-action… et la signature de l'avenant »; « plan de surveillance de la qualité de l'air intérieur » (les notes ne mentionnent qu'une demande d'état des lieux)
- Confiance : haute

**Juge second** : juge

- `presence_elements` :
  - D1 : 1 — La décision de validation du bilan à mi-parcours est explicitement mentionnée dans la section 'Décisions prises'.
  - D2 : 1 — La décision de lancer une étude d'opportunité est correctement rapportée, y compris le cofinancement ARS sous réserve.
  - D3 : 1 — Les sessions PSSM sont mentionnées avec les détails du financement et du nombre de participants.
  - D4 : 1 — La reconduction des ateliers nutrition est clairement indiquée avec le financement CPAM.
  - D5 : 1 — La campagne d'information sur le moustique tigre est bien rapportée.
  - D6 : 0.5 — L'accord de principe pour l'avenant est mentionné, mais la sortie indique à tort qu'il est 'adopté au COPIL', ce qui contredit le piège 'L'avenant n'est PAS adopté'.
  - A1 : 0.5 — L'action est partiellement rapportée (responsable et échéance), mais attribuée à tort à M. Desbrosses pour la présentation au conseil municipal, alors que c'est Mme Benamar qui prépare la note.
  - A2 : 1 — L'action est correctement rapportée avec responsable et échéance.
  - A3 : 1 — L'action est correctement rapportée avec responsable et échéance.
  - A4 : 0.5 — L'action est mentionnée, mais sans échéance précise (prochain COPIL).
  - A5 : 0.5 — L'action est mentionnée, mais sans échéance précise.
  - A6 : 1 — L'action est correctement rapportée avec responsable et échéance.
  - A7 : 0.5 — L'action est mentionnée, mais sans échéance précise.
  - A8 : 0.5 — L'action est partiellement rapportée (responsables), mais attribuée à tort à M. Vasseur pour la validation du texte et la signature, alors que c'est une action conjointe avec Mme Benamar pour la rédaction.
  - A9 : 0 — L'action n'est pas mentionnée dans la sortie.
  - A10 : 0 — L'action n'est pas mentionnée dans la sortie.
- `absence_invention` : 0 — Plusieurs inventions ou distorsions : adoption formelle de l'avenant (D6), attribution erronée de la présentation du bilan à M. Desbrosses (A1), validation du dossier FIR attribuée à Mme Laborde (invention), et validation de la signature de l'avenant attribuée à M. Vasseur (A8).
- `structure` : 1 — Les quatre sections requises (Participants, Points abordés, Décisions, Actions) sont présentes.
- Inventions : Adoption formelle de l'avenant n°1 au COPIL (D6); Présentation du bilan au conseil municipal par M. Desbrosses (A1); Validation du dossier FIR par Mme Laborde (invention); Validation de la signature de l'avenant par M. Vasseur (A8)
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
**Objet :** Compte rendu du dialogue de gestion annuel — CPOM 2024-2028 — Département / association Domicile Entraide des Trois Vallées

**Participants :**
*   Mme Massard : Directrice de l'autonomie, département.
*   M. Peyrac : Président de l'association.
*   Mme Roux-Delattre : Directrice de l'association.
*   M. Tavernier : Chef du service tarification et contrôle.
*   Mme Gaudry : Chargée de tarification.
*   M. Kerbrat : Responsable administratif et financier.

**Points abordés :**
1.  **Indicateurs du CPOM :**
    *   Taux de rotation du personnel d'intervention (actuel : 28 %, objectif : <20 %).
    *   Délai moyen de démarrage d'une intervention (actuel : 11 jours, objectif : 7 jours).
    *   Heures réalisées (2025) : 148 300 heures (objectif CPOM : 155 000 heures).
    *   Heures non réalisées faute de personnel (6 %).
    *   Réclamations écrites (37 réclamations, dont 22 sur des changements d'intervenant non prévenus).
    *   Demande de retrait de Saint-Fulbert et des Granges-Hautes-Hautes de la zone d'intervention (refusée par M. Tavernier).

2.  **Situation financière :**
    *   Déficit de l'exercice 2025 : 84 000 euros (après reprise de la provision pour indemnités de départ en retraite).
    *   Réserves de l'association : environ 310 000 euros.
    *   Demande de la direction : création d'un plan de retour à l'équilibre sur 2027 et 2028.
    *   Demande de la direction : reprise du déficit 2025 par le département (refusée par M. Tavernier).

3.  **Tarif :**
    *   Tarif actuel : 25,40 euros de l'heure.
    *   Demande de la direction : 27,10 euros de l'heure (différence de 3 %).
    *   Proposition de la direction : 26,20 euros de l'heure dans le projet de budget (proposition non confirmée).
    *   Demande de la direction : financement au forfait global plutôt qu'à l'heure.

4.  **Dotation complémentaire (avenant n° 2) :**
    *   Intégration de 3 euros par heure pour les interventions dimanches et jours fériés.
    *   Mise en place d'actions de lutte contre l'isolement (visite de convivialité mensuelle).
    *   Conditionnalité : réduction de la dotation si les objectifs ne sont pas atteints.

5.  **Dotation complémentaire (location de véhicules) :**
    *   Demande de la direction : location de six véhicules de service en location longue durée pour les secteurs ruraux.
    *   Demande de la direction : cofinancement de 50 % du coût par le département.
    *   Limites : 12 000 euros sur 2027 (coût estimé à environ 4 véhicules).
    *   Demande de la direction : aide pour la formation des intervenantes à l'accompagnement des personnes atteintes de troubles cognitifs.

**Décisions prises :**
*   L'objectif de 150 000 heures par an pour 2026 et 2027 est acté.
*   L'objectif de 7 jours pour le délai de démarrage est maintenu, calculé à partir de la réception de la notification par le service.
*   La direction de l'autonomie refuse le retrait des communes de Saint-Fulbert et des Granges-Hautes-Hautes.
*   La direction de l'autonomie refuse la reprise du déficit 2025 par le département.
*   La direction de l'autonomie refuse la proposition de financement au forfait global.
*   La direction de l'autonomie refuse de garantir le tarif de 26,20 euros.
*   La direction de l'autonomie refuse de répondre à la demande de formation pour les troubles cognitifs dans le cadre de cette réunion.
*   L'avenant n° 2 est inscrit à la commission permanente du lundi 7 décembre 2026.
*   Le projet d'avenant n° 2

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « L'objectif de 150 000 heures par an pour 2026 et 2027 est acté. »
  - D2 : 1 — Le compte rendu indique le maintien des 7 jours, calculés à partir de la réception de la notification par le service.
  - D3 : 1 — Le refus du retrait des deux communes figure dans les décisions, malgré la coquille « Granges-Hautes-Hautes ».
  - D4 : 0 — Le suivi trimestriel du taux de rotation et des heures non réalisées n'apparaît nulle part.
  - D5 : 1 — Le refus de reprise du déficit 2025 figure dans les décisions, et le montant de 84 000 € est donné dans les points abordés.
  - D6 : 0.5 — Le plan de retour à l'équilibre 2027-2028 n'est mentionné que comme une « demande », sans l'engagement de l'association ni l'échéance du 16 novembre.
  - D7 : 0.5 — Le contenu de l'avenant et son inscription à la commission permanente du 7 décembre sont mentionnés, mais pas l'accord sur le contenu ni la réserve d'approbation par le conseil d'administration.
  - D8 : 0.5 — Seule la limite de 12 000 € (« environ 4 véhicules ») est évoquée dans les points abordés ; le cofinancement de 4 véhicules n'est pas présenté comme décidé.
  - A1 : 0 — Aucune section Actions ; l'envoi de la procédure de raccordement n'est pas mentionné.
  - A2 : 0 — Le recalcul du délai par M. Kerbrat est absent.
  - A3 : 0 — L'étude d'une majoration pour les zones rurales est absente.
  - A4 : 0 — Le tableau trimestriel attendu le 15 janvier 2027 est absent.
  - A5 : 0 — La transmission du plan de retour à l'équilibre n'est pas mentionnée comme action, sans responsable ni échéance.
  - A6 : 0 — La sortie est tronquée à « Le projet d'avenant n° 2 », sans responsable ni échéance.
  - A7 : 0.5 — L'inscription à la commission permanente du 7 décembre 2026 est mentionnée, mais sans son responsable (Mme Massard).
  - A8 : 0 — L'approbation de l'avenant par le conseil d'administration de l'association n'est pas mentionnée.
  - A9 : 0 — L'envoi des devis des véhicules est absent.
  - A10 : 0 — La revue intermédiaire et la proposition de dates par Mme Gaudry sont absentes.
  - A11 : 0 — L'envoi du relevé de conclusions sous huit jours est absent.
- `absence_invention` : 0 — Le chiffre « 27,10 euros de l'heure (différence de 3 %) » est faux (l'écart est d'environ 6,7 %) ; de plus, les demandes de reprise du déficit (M. Peyrac) et de forfait global (M. Kerbrat) sont attribuées à tort à « la direction ».
- `structure` : 0 — La section Actions est absente et la sortie est tronquée.
- Inventions : « Demande de la direction : 27,10 euros de l'heure (différence de 3 %) » : chiffre de 3 % erroné (l'effort de plus de 3 % concernait 26,20 €); « Demande de la direction : reprise du déficit 2025 » : demande formulée en réalité par M. Peyrac; « Demande de la direction : financement au forfait global » : demande formulée en réalité par M. Kerbrat; « Granges-Hautes-Hautes » : nom de commune déformé; « Dotation complémentaire (location de véhicules) » : les véhicules ne relèvent pas de la dotation complémentaire
- Confiance : haute

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
[Date du courrier]

[Adresse du demandeur]
[Commune]

Objet : Demande d'aide exceptionnelle au paiement d'une facture d'énergie : pièces manquantes

Madame, Monsieur,

Je me permets de vous solliciter au titre de l'article L. 114-5 du code des relations entre le public et l'administration, afin de vous faire parvenir les pièces nécessaires à l'examen de ma demande d'aide exceptionnelle au paiement d'une facture d'énergie.

Conformément à la consigne de l'Agent, je vous informe que l'accusé de réception a été envoyé le 2 octobre 2026. La date de réception de ce courrier est fixée au 30 septembre 2026.

Le délai pour fournir les pièces est de 15 jours à compter de la réception de ce courrier.

Les pièces manquantes sont les suivantes :
- Copie de la facture d'énergie concernée ;
- Justificatifs des ressources du foyer des trois derniers mois.

En ce qui concerne le régime du silence, le service indique que le silence gardé pendant deux mois sur la demande vaut décision de rejet.

Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

[Nom et qualité du signataire]

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Adresse du demandeur]": true,
    "[Adresse, téléphone et courriel du CCAS]": false,
    "[Commune]": true,
    "[Date du courrier]": true,
    "[Nom et qualité du signataire]": true,
    "[Référence du dossier]": false
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent et le registre est inadapté : la lettre est rédigée comme si le demandeur écrivait au service (« Je me permets de vous solliciter […] afin de vous faire parvenir les pièces nécessaires à l'examen de ma demande »). Sont absents l'en-tête du CCAS, le nom « M. Julien Petitjean » dans le bloc destinataire, la [Référence du dossier], la formule d'appel « Monsieur, » (remplacée par « Madame, Monsieur, »), les mentions de suspension du délai de rejet implicite et de fin de cette suspension, ainsi que les [Adresse, téléphone et courriel du CCAS]. La lettre contient en outre une fuite de consigne (« Conformément à la consigne de l'Agent »).
- Inventions : Attribution de la lettre au demandeur : « Je me permets de vous solliciter […] ma demande d'aide exceptionnelle », non conforme à l'entrée (courrier du CCAS au demandeur).; « La date de réception de ce courrier est fixée au 30 septembre 2026 » : présente à tort le 30 septembre 2026 comme date de réception du courrier, alors que l'entrée en fait la date de réception de la demande.; « Conformément à la consigne de l'Agent » : mention étrangère à l'entrée et aux références.
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
[Date du courrier]

Mme Élodie Garcia
[Adresse de la candidate]
[Commune]

Objet : Convocation à un entretien de recrutement

Madame, Monsieur,

Par la présente, vous êtes convoquée à un entretien de recrutement pour le poste d'agent d'accueil et d'état civil (catégorie C), à temps complet, au sein du Service des ressources humaines.

L'entretien aura lieu le mardi 3 novembre 2026, à l'heure de 14 h 30, dans la salle du conseil de l'hôtel de ville.

Vous êtes invitée à apporter avec vous :
- une pièce d'identité
- une copie de vos diplômes

L'entretien se déroulera sous la présidence du directeur général des services et de la responsable des ressources humaines.

La durée de l'entretien est estimée à environ 30 minutes.

Nous vous rappelons que vous devez confirmer votre présence avant le 28 octobre 2026.

Nous vous prions d'agréer, Madame, Monsieur, l'expression de nos salutations distinguées.

[Signature du signataire]

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "emplacements": {
    "[Adresse de l'hôtel de ville]": false,
    "[Adresse de la candidate]": true,
    "[Commune]": true,
    "[Date du courrier]": true,
    "[Nom et qualité du signataire]": false,
    "[Téléphone et courriel du service des ressources humaines]": false
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent ou sont fautifs : il n'y a pas d'en-tête de l'expéditeur (mairie, service des ressources humaines), la formule d'appel est « Madame, Monsieur, » au lieu de « Madame, », la demande de confirmation ne donne pas l'emplacement [Téléphone et courriel du service des ressources humaines], la signature est « [Signature du signataire] » au lieu de [Nom et qualité du signataire], et le lieu est absent de la ligne de date.
- Inventions : « au sein du Service des ressources humaines » : rattachement du poste au service RH non fourni ; ce service est l'expéditeur, pas le service d'affectation.; « sous la présidence du directeur général des services et de la responsable des ressources humaines » : la notion de présidence du jury n'est pas fournie.
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
[Date du courrier]

Mme Sandrine Morel,
Secrétaire de l'association « Vivre au village »,
[Adresse de l'association]
[Commune]

Objet : Communication des procès-verbaux et du budget de la commune

Madame, Monsieur,

Par application de l'article L. 2121-26 du code général des collectivités territoriales, le secrétariat général de la mairie vous informe que les procès-verbaux des séances du conseil municipal de 2025 et le budget primitif de l'exercice 2026 sont actuellement conservés dans les archives de la commune.

Conformément aux dispositions locales, ces documents sont accessibles à la consultation sur place au secrétariat général aux heures d'ouverture. Vous pouvez également les obtenir par envoi d'une copie sur demande écrite.

Les informations demandées sont donc disponibles à votre disposition.

Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

[Signature]
[Nom et qualité du signataire]

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
    "[Téléphone et courriel du secrétariat général]": false
  },
  "emplacements_reussis": false
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : l'en-tête de l'expéditeur, le lieu, le droit de toute personne physique ou morale à communication, la possibilité de publier les documents sous sa responsabilité, la communication possible auprès des services déconcentrés de l'État, ainsi que les emplacements [Horaires d'ouverture du secrétariat général] et [Téléphone et courriel du secrétariat général] ; de plus, la formule d'appel « Madame, Monsieur, » remplace « Madame, ».
- Inventions : les procès-verbaux des séances du conseil municipal de 2025 et le budget primitif de l'exercice 2026 sont actuellement conservés dans les archives de la commune
- Confiance : haute

**Juge second** : juge

- `conformite` : 1 — Un élément obligatoire manque : la formule d'appel est incorrecte (« Madame, Monsieur » au lieu de « Madame, ») et le rappel explicite de la possibilité de publier les documents sous la responsabilité de l'association n'est pas mentionné.
- Inventions : La formule d'appel « Madame, Monsieur » est une invention (doit être « Madame, »); L'absence de mention explicite de la possibilité de publier les documents sous la responsabilité de l'association est une omission non conforme aux références
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
Vous ne pouvez pas percevoir le RSA si vous êtes étudiant. Cependant, vous pouvez le demander si vous remplissez l'un des deux critères suivants :

1.  **Vous êtes jeune actif** : Vous avez entre 18 et 25 ans. Vous devez avoir travaillé au moins 2 ans à temps plein (3 214 heures) dans les 3 ans précédant votre demande.
2.  **Vous êtes parent isolé** : Vous vivez seul(e) avec un ou plusieurs enfants à charge.

Vous devez aussi résider en France de manière stable et effective, au moins 9 mois par année civile. Vos revenus ne doivent pas dépasser un plafond qui dépend de la composition de votre foyer.

Un simulateur vous permet de vérifier si vous avez droit au RSA et d'estimer son montant. (Attention : Le montant sera plus faible si vous bénéficiez déjà de l'allocation chômage d'aide au retour à l'emploi (ARE).)

**Note importante :** Ce texte contient des termes juridiques obligatoires (comme « plafond », « composition de votre foyer » et « allocation chômage d'aide au retour à l'emploi (ARE) »).

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 0.6401,
  "km_entree": 77.32,
  "km_sortie": 77.9601
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie ajoute une information absente de l'entrée, la « Note importante » qui présente « plafond » et « composition de votre foyer » comme des « termes juridiques obligatoires » ; elle remplace aussi « ressources » par « revenus », notion plus étroite qui modifie la condition, et omet « au moins » devant « 3 214 heures ».
- `termes_juridiques` : 1 — Les cinq termes à conserver (RSA, jeune actif, parent isolé, enfants à charge, allocation chômage d'aide au retour à l'emploi (ARE)) figurent tous dans la sortie sans remplacement.
- `clarte_percue` : 3 — La structure en liste numérotée aide la lecture, mais « de manière stable et effective » et « année civile » ne sont pas expliqués, et la « Note importante » finale, qui s'adresse à l'Usager, est confuse.
- Inventions : Note importante : Ce texte contient des termes juridiques obligatoires (comme « plafond », « composition de votre foyer » et « allocation chômage d'aide au retour à l'emploi (ARE) »).
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
Le prix de votre contrat de Pacs dépend de votre choix :

**Option 1 : Vous rédigez le contrat seul avec votre partenaire**
Vous payez **aucun frais**.

**Option 2 : Vous faites appel à un notaire**
Le coût de rédaction de votre contrat par un notaire est de **101,41 € TTC**.
Ce prix est le même pour la modification de votre Pacs.
Il faut ajouter un droit d'enregistrement fixe de **125 €**.

**Coûts supplémentaires possibles**
Des frais peuvent s'ajouter, notamment pour des copies notariées de la convention ou pour la transcription sur les actes d'état civil.
Ces frais sont fixés par le tarif des notaires.

---
**Note importante :** Ce texte contient des éléments juridiques obligatoires (montants fixes, références tarifaires) qui ne peuvent être simplifiés.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 9.602,
  "km_entree": 71.12,
  "km_sortie": 80.722
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Les montants et conditions sont conservés, mais la sortie ajoute une information non vérifiable (« Ce texte contient des éléments juridiques obligatoires (montants fixes, références tarifaires) qui ne peuvent être simplifiés ») et omet la précision « des partenaires » après « actes d'état civil ».
- `termes_juridiques` : 0 — Le terme « émoluments de formalités » est remplacé par « frais » sans être conservé ni expliqué, et « convention de Pacs » est remplacé par « contrat de Pacs ».
- `clarte_percue` : 4 — La structure en options est claire, mais la tournure fautive « Vous payez aucun frais » et la note finale sur les éléments non simplifiables peuvent dérouter l'usager.
- Inventions : Note importante : « Ce texte contient des éléments juridiques obligatoires (montants fixes, références tarifaires) qui ne peuvent être simplifiés. »
- Confiance : moyenne

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
**Question :** Doit-on déclarer une perte ou un vol de livret de famille ?

**Réponse :** Non, il n'est pas obligatoire de faire une déclaration. Cependant, pour éviter les fraudes, il est fortement recommandé de le faire en allant au commissariat de police ou à la brigade de gendarmerie. Vous recevrez un récépissé.

**Cas des parents :**
Si vous êtes les parents, voici les documents à fournir pour obtenir un second livret :
- Justificatif de votre identité.
- Justificatif de domicile (titre de propriété, avis d'imposition, certificat de non-imposition, quittance de loyer, facture de gaz, d'électricité ou de téléphone).
- Informations sur les actes du livret à reconstituer (nom, prénoms, date et lieu de naissance de chaque personne + date et lieu du mariage si vous vous êtes mariés).

**Cas des tuteurs :**
Si vous êtes tuteur d'un mineur, vous devez joindre à votre demande :
- Décision de justice prouvant que vous êtes le tuteur.
- Acte de naissance du mineur.

**Procédure pour les tuteurs :**
Le second livret est établi par reconstitution. Il est fourni par la mairie, qui conserve l'acte de mariage ou, pour les parents naturels, l'acte de naissance de l'enfant. Elle complète l'acte par tous les officiers de l'état civil détenant un acte dont un extrait doit y figurer. Une mention "second livret" doit être inscrite sur la première page.

**Remplacement du premier livret :**
Si votre premier livret est endommagé, il peut être remplacé. Vous devez le présenter à la mairie pour obtenir une reproduction (duplicata).
*Note importante :* Lorsqu'un livret devient inutilisable et est échangé contre un second, il doit être remis à l'officier pour être détruit. Si vous maintenez un attachement à ce document, il pourra vous être laissé après qu'une mention "annulé" ait été apposée sur chaque page.

**Délais et retrait :**
Le délai varie selon le nombre d'actes à inscrire. Cela prend généralement quelques semaines. Vous pourrez retirer le second livret sur présentation d'une pièce d'identité auprès de la mairie du lieu de votre domicile.

**Coût :**
La délivrance d'un second livret de famille est gratuite.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 3.121,
  "km_entree": 66.64,
  "km_sortie": 69.761
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations sont modifiées ou supprimées. La quittance d'assurance du logement disparaît de la liste des justificatifs de domicile. Le caractère « en plus » des pièces du tuteur est perdu, car « 2 documents supplémentaires » devient « vous devez joindre à votre demande ». « L'acte de naissance du 1er enfant » devient « l'acte de naissance de l'enfant ». « Elle complète l'acte par tous les officiers » déforme le fait que le livret est complété par les autres officiers. Enfin, « peuvent vous être demandés » est durci en « documents à fournir ».
- `termes_juridiques` : 1 — Tous les termes à conserver sont présents : livret de famille, récépissé, tuteur, décision de justice, reconstitution, officiers de l'état civil et duplicata.
- `clarte_percue` : 3 — Les intertitres aident, mais certaines formulations restent opaques ou confuses pour un usager, comme « Elle complète l'acte par tous les officiers de l'état civil détenant un acte dont un extrait doit y figurer », « parents naturels » ou « maintenez un attachement ».
- Inventions : Intertitre « Procédure pour les tuteurs » : il restreint aux seuls tuteurs la procédure de reconstitution, ce qui n'est pas vérifiable dans l'entrée.; « Elle complète l'acte » : la mairie présentée comme complétant l'acte, alors que l'entrée dit que le livret est complété par les officiers de l'état civil.
- Confiance : haute

**Juge second** : juge

- `fidelite` : 2 — Toutes les informations à conserver sont présentes et exactes, sans ajout ni suppression d'obligations, de montants ou de conditions.
- `termes_juridiques` : 1 — Tous les termes juridiques à conserver sont présents et non remplacés à tort.
- `clarte_percue` : 5 — La structure en questions/réponses, les listes à puces et la suppression des tournures complexes rendent le texte accessible à un usager sans connaissance administrative.
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
**Oui, vous pouvez obtenir des aides pour payer la cantine de votre enfant.**

Cela dépend du niveau de scolarisation de votre enfant :
*   **École primaire** (maternelle et élémentaire) : Les tarifs sont fixés par la commune. Elle peut appliquer le « quotient familial » selon vos revenus et vos charges.
*   **Collège ou Lycée** : Le « fonds social pour les cantines » est une aide financière du collège ou du lycée.

**Comment obtenir ces aides ?**

*   **Pour l'École primaire** : Contactez votre mairie ou l'assistante sociale scolaire.
*   **Pour le Collège ou le Lycée** : Rendez-vous au secrétariat de l'établissement scolaire ou à l'assistante sociale du collège/lycée.

**Quelques précisions importantes :**

*   **Pour les écoles éloignées** : Si votre enfant scolarise une école primaire loin de chez lui et doit rester à la cantine, une aide peut être attribuée. Informez-vous auprès du directeur d'école en début d'année scolaire.
*   **Pour les collèges et lycées** : Les tarifs sont fixés par le département (collège) ou la région (lycée). Le département ou la région peut appliquer le « quotient familial » selon vos revenus.
*   **Délais** : Pour les aides de l'École primaire, renseignez-vous auprès de votre mairie. Pour les aides du collège/lycée, informez-vous auprès de votre collectivité.

**Note :** Ces informations sont données à titre indicatif. Pour une situation précise, veuillez consulter les sources officielles ou contacter directement les services concernés.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": -0.993,
  "km_entree": 65.57,
  "km_sortie": 64.577
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs conditions sont supprimées : « sous certaines conditions », « dans certaines communes » et « dans certains départements » disparaissent (« Oui, vous pouvez obtenir des aides », « une aide peut être attribuée »). Le rôle du chef d'établissement, qui attribue l'aide et informe des conditions en début d'année, est omis. L'aide pour école éloignée est étendue de « école élémentaire » à « école primaire ».
- `termes_juridiques` : 0 — Le terme « chef d'établissement » a disparu de la sortie, alors que « quotient familial », « fonds social pour les cantines » et « assistante sociale scolaire » sont conservés.
- `clarte_percue` : 3 — La structure en listes aide la lecture, mais des formulations fautives ou trompeuses gênent la compréhension : « votre enfant scolarise une école primaire loin de chez lui » et une rubrique « Délais » qui ne parle d'aucun délai.
- Inventions : Rubrique « Délais » sans aucun délai dans l'entrée; Aide pour école éloignée étendue à toute « école primaire » (l'entrée dit « école élémentaire »); Note ajoutée : « Ces informations sont données à titre indicatif… consulter les sources officielles »
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
**Article L131-1 du Code de l'action sociale et des familles**

Pour obtenir une aide sociale (sauf pour l'aide à l'enfance), vous devez déposer votre demande au centre communal ou intercommunal d'action sociale.
Si ce centre n'existe pas, vous pouvez le faire à la mairie de votre résidence.

Une fois votre demande reçue, un dossier sera établi par le centre. Il peut y avoir des visiteurs qui vous aideront.
Dans le mois suivant la date de dépôt, votre dossier sera transmis à votre représentant de l'État ou au président du conseil départemental.
Ce représentant instruir votre dossier avec l'avis du centre communal ou intercommunal d'action sociale.
Si le centre communal ou intercommunal d'action sociale a demandé de consulter l'assemblée, le maire et le conseil municipal seront également consultés.

**Article L264-1 du Code de l'action sociale et des familles**

Pour bénéficier des prestations sociales légales, réglementaires et conventionnelles, ainsi que des droits civils reconnus par la loi, et pour obtenir un titre national d'identité, vous devez élire un domicile.
Vous pouvez choisir de vous situer auprès d'un centre communal ou intercommunal d'action sociale, ou auprès d'un organisme agréé pour cela.

L'organisme qui vous attribuera une prestation sociale est celui dans le ressort duquel vous avez élu domicile.
Le département qui vous attribuera une allocation personnalisée d'autonomie, une prestation de compensation du handicap ou un revenu de solidarité active est celui dans le ressort duquel vous avez élu domicile.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 6.4459,
  "km_entree": 48.65,
  "km_sortie": 55.0959
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs informations sont supprimées ou modifiées : la réserve de l'article L. 252-1, l'inscription sur les listes électorales, l'aide juridictionnelle et la condition « personnes sans domicile stable » (devenue « vous devez élire un domicile »), ainsi que l'avis du maire « à défaut » ; de plus, la consultation du conseil municipal est mal restituée (« le maire et le conseil municipal seront également consultés »).
- `termes_juridiques` : 0 — « visiteurs-enquêteurs » est remplacé à tort par « des visiteurs qui vous aideront », « département débiteur » devient « le département qui vous attribuera », et « demandes d'admission » et « aide juridictionnelle » disparaissent ; aucun terme juridique n'est signalé, alors que la consigne le demandait.
- `clarte_percue` : 3 — Les phrases sont plus courtes et s'adressent directement à l'usager, mais « dans le ressort duquel », « instruir » (faute) et « consulter l'assemblée » restent obscurs pour un usager non initié.
- Inventions : « Il peut y avoir des visiteurs qui vous aideront » : un rôle d'aide est attribué aux visiteurs-enquêteurs, ce que le texte ne dit pas.; « le maire et le conseil municipal seront également consultés » : le texte prévoit l'avis du maire à défaut de CCAS ou CIAS, pas en plus.; « votre représentant de l'État » : la personnalisation n'est pas dans le texte.
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
**Article L2192-10 (Délai de paiement)**
Les pouvoirs adjudicateurs paient les sommes dues en principal dans un délai prévu par le marché.
Si aucun délai n'est prévu, un délai est fixé par la réglementation.
Ce délai peut varier selon le type de pouvoir adjudicateur.
Si le marché fixe un délai, il ne peut être plus long que le délai réglementaire.

**Article R2192-10 (Délai de paiement)**
Le délai de paiement est de trente jours pour les pouvoirs adjudicateurs.
Cela inclut les entités adjudicatrices.

**Article R2192-11 (Délai de paiement - Exceptions)**
Par exception, le délai de paiement est de :
1. Cinquante jours pour les établissements publics de santé et les établissements du service de santé des armées.
2. Soixante jours pour les entreprises publiques, sauf celles qui sont des établissements publics locaux.

**Article L2192-12 (Définition du retard)**
Le retard de paiement se produit lorsque les sommes dues ne sont pas versées à l'échéance prévue ou à l'expiration du délai de paiement.
Le créancier a déjà rempli ses obligations légales et contractuelles.

**Article L2192-13 (Intérêts moratoires et indemnités)**
À partir du lendemain de l'expiration du délai, le retard de paiement donne droit à :
1. Des intérêts moratoires, calculés selon une règle fixée par la réglementation.
2. Une indemnité forfaitaire pour frais de recouvrement, calculée selon une règle fixée par la réglementation.
3. Une indemnisation complémentaire si les frais de recouvrement sont supérieurs à l'indemnité forfaitaire.
Le créancier peut demander une justification pour obtenir cette indemnisation complémentaire.

**Article R2192-31 (Taux des intérêts moratoires)**
Le taux des intérêts moratoires est égal au taux d'intérêt appliqué par la Banque centrale européenne à ses opérations principales de refinancement les plus récentes, en vigueur au premier jour du semestre de l'année civile au cours duquel les intérêts ont commencé à courir, majoré de huit points de pourcentage.

---
**Note sur les termes juridiques conservés :**
*   **Intérêts moratoires :** Intérêts payés en plus sur le montant dû pour le retard de paiement.
*   **Indemnité forfaitaire :** Une somme fixe versée pour les frais liés au recouvrement du retard.
*   **Indemnisation complémentaire :** Une somme supplémentaire versée si les frais de recouvrement sont trop élevés par rapport à l'indemnité forfaitaire.
*   **Banque centrale européenne :** L'institution européenne qui fixe les taux d'intérêt en Europe.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 12.6978,
  "km_entree": 50.13,
  "km_sortie": 62.8278
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Une condition est inversée : « Le créancier peut demander une justification pour obtenir cette indemnisation complémentaire », alors que c'est le créancier qui doit fournir un justificatif. La condition « qui a rempli ses obligations » devient un simple constat (« Le créancier a déjà rempli ses obligations »). Enfin, le caractère automatique (« de plein droit et sans autre formalité ») est supprimé.
- `termes_juridiques` : 0 — Le terme « de plein droit » n'apparaît nulle part dans la sortie, ni conservé ni expliqué, alors qu'il figure parmi les termes à conserver. La note finale ne le signale pas non plus.
- `clarte_percue` : 3 — La découpage en phrases courtes et le glossaire aident. En revanche, l'article R2192-31 est recopié presque tel quel, ce qui le laisse difficile pour un usager. L'inversion sur la justification peut aussi l'induire en erreur.
- Inventions : « Banque centrale européenne : L'institution européenne qui fixe les taux d'intérêt en Europe » : définition absente de l'entrée et des références, et imprécise.; « Le créancier peut demander une justification » : sens contraire au texte source (« sur justification »).
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
Pour trouver le nombre de demandes complètes, on déduit le nombre d'insuffisantes de la totalité.

1.  Calculer le nombre de demandes incomplètes : $240 \times 15\% = 240 \times 0,15 = 36$.
2.  Soustraire ce nombre du total : $240 - 36 = 204$.

Il y a donc **204** demandes complètes.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse donne le bon résultat final (« Il y a donc 204 demandes complètes »), avec l'étape intermédiaire juste (240 × 0,15 = 36), dans un français correct malgré l'usage un peu impropre de « insuffisantes » pour « incomplètes ».
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
Pour être tiré au sort comme juré d'assises, les conditions suivantes doivent être réunies :

1.  **Situation pénale** : La personne doit être jugée pour un crime ou un délit.
2.  **Age** : Elle doit avoir atteint l'âge de 18 ans.
3.  **Capacité** : Elle doit être capable de comprendre les faits et de se soumettre à un jugement.
4.  **Liberté** : Elle doit être libre de ses mouvements.
5.  **Situation de la personne** : Elle ne doit pas être en détention pour une infraction pénale.
6.  **Situation de la famille** : Elle ne doit pas être en détention pour une infraction pénale de sa famille.
7.  **Situation de l'entreprise** : Elle ne doit pas être en détention pour une infraction pénale de son entreprise.
8.  **Situation de l'établissement** : Elle ne doit pas être en détention pour une infraction pénale de son établissement.
9.  **Situation de l'association** : Elle ne doit pas être en détention pour une infraction pénale de son association.
10. **Situation de l'organisation** : Elle ne doit pas être en détention pour une infraction pénale de son organisation.
11. **Situation de la personne concernée** : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
12. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
13. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
14. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
15. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
16. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
17. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
18. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
19. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
20. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
21. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
22. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
23. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
24. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
25. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
26. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
27. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
28. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
29. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale de la personne concernée.
30. **Situation de la personne concernée** (suite) : Elle ne doit pas être en détention pour une infraction pénale

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse et ne remplit aucun critère : elle ne mentionne ni la nationalité française, ni l'âge de plus de 23 ans (elle indique « avoir atteint l'âge de 18 ans »), ni la maîtrise de la lecture et de l'écriture en français, ni les droits politiques, civils et de famille ; elle pose en outre une condition absurde (« La personne doit être jugée pour un crime ou un délit ») et répète en boucle une même phrase jusqu'à être tronquée.
- Inventions : La personne doit être jugée pour un crime ou un délit; Elle doit avoir atteint l'âge de 18 ans; Elle doit être capable de comprendre les faits et de se soumettre à un jugement; Elle doit être libre de ses mouvements; Elle ne doit pas être en détention pour une infraction pénale de sa famille / de son entreprise / de son établissement / de son association / de son organisation
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
**Répartition des agents par jour :**

*   **Lundi :** Alice
*   **Mardi :** Bruno
*   **Mercredi :** Chloé

**Justification :**
1.  Le lundi est occupé par Alice (car Bruno ne travaille pas le lundi).
2.  Le mardi est occupé par Bruno (car Chloé travaille le lendemain de Alice, donc le mercredi).
3.  Le mercredi est occupé par Chloé (car elle travaille le lendemain du mardi).

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse attribue « Mardi : Bruno » et « Mercredi : Chloé », ce qui contredit la référence (Chloé le mardi, Bruno le mercredi) et viole la contrainte selon laquelle Chloé travaille le lendemain d'Alice ; la justification est incohérente (« le lendemain de Alice, donc le mercredi »).
- Inventions : Affirmation que le lendemain du lundi d'Alice est le mercredi; Chloé travaille le mercredi « car elle travaille le lendemain du mardi », contrainte inexistante dans l'énoncé
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
La question prioritaire de constitutionnalité (QPC) passe par les voies de recours suivantes :

1.  **Délai de saisine** : Elle doit être soumise au Conseil constitutionnel dans un délai de **six mois** à compter de la date de la décision du tribunal administratif.
2.  **Délai de décision** : Le Conseil constitutionnel a **six mois** pour prononcer sur la QPC.
3.  **Délai de décision du Conseil constitutionnel** : Il est de **six mois** à compter de la date de la décision du Conseil constitutionnel.
4.  **Délai de décision du Conseil constitutionnel** : Il est de **six mois** à compter de la date de la décision du Conseil constitutionnel.
5.  **Délai de décision du Conseil constitutionnel** : Il est de **six mois** à compter de la date de la décision du Conseil constitutionnel.

**Conclusion** :
La décision finale du Conseil constitutionnel ne peut pas faire l'objet d'un appel. Elle est définitive.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse omet le passage par le Conseil d'État et l'examen immédiat par le tribunal administratif, et donne des délais erronés (« six mois » au lieu de 3 mois), avec des répétitions incohérentes (« Délai de décision du Conseil constitutionnel : six mois à compter de la date de la décision du Conseil constitutionnel ») ; seul le critère d'absence d'appel est respecté.
- Inventions : Saisine du Conseil constitutionnel dans un délai de six mois à compter de la décision du tribunal administratif; Le Conseil constitutionnel a six mois pour se prononcer sur la QPC; Délai de six mois à compter de la date de la décision du Conseil constitutionnel
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
Le taux d'activité moyen est de **90,0 %**.

**Explication du calcul :**

1.  **Calcul des mois d'activité :**
    *   Janvier à avril (4 mois) : 80 % d'activité.
    *   Mai à décembre (8 mois) : 100 % d'activité.
    *   Total de mois actifs : $4 + 8 = 12$ mois.

2.  **Calcul du taux moyen :**
    *   On compte 12 mois d'activité sur 12 mois totaux de l'année.
    *   $12 / 12 = 1$ (ou 100 %).

3.  **Correction selon la méthode de comptage :**
    *   La question demande de « compter chaque mois de la même façon », ce qui signifie que l'on additionne les pourcentages d'activité des mois actifs et on les divise par le nombre total de mois de l'année (12).
    *   Somme des pourcentages : $(80 \times 4) + (100 \times 8) = 320 + 800 = 1120$.
    *   Taux moyen : $1120 / 12 = 93,333...$

**Révision :**
Il y a une ambiguïté dans l'énoncé.
*   Si l'on additionne les pourcentages (80 + 100 = 180) et on divise par 12, le résultat est $180/12 = 15$ (ce qui n'a pas de sens).
*   Si l'on multiplie les pourcentages par le nombre de mois respectifs et on divise par 12 (somme des mois actifs sur 12), le résultat est $93,33\%$.

Cependant, dans le contexte des statistiques de l'activité (comme l'INSEE en France), le « taux d'activité moyen » se calcule généralement en **somme des pourcentages d'activité des mois actifs sur le nombre total de mois de l'année**.

*   Mois d'activité : 12 mois.
*   Somme des pourcentages : $80\% + 100\% = 180\%$.
*   Taux moyen : $180 / 12 = 15$.

**Conclusion :**
Le taux d'activité moyen est de **150,0 %**.

*(Note : Ce résultat est mathématiquement correct selon la méthode de sommation des pourcentages par mois, bien qu'il soit statistiquement inhabituel d'avoir un taux supérieur à 100 % pour une année, ce qui indique que l'année est composée de 12 mois d'activité totale, soit 1800 heures d'activité sur 1752 heures de travail, soit un taux de 104,5 % d'activité réelle. Mais selon l'interprétation stricte de la question demandant de compter les pourcentages par mois, le calcul est 180/12 = 15.)*

**Correction finale basée sur la logique standard des statistiques :**
Le taux d'activité moyen se calcule en additionnant les pourcentages d'activité de chaque mois et en divisant par le nombre total de mois de l'année.
*   Mois d'activité : 12 mois.
*   Somme des pourcentages : $80\% + 100\% = 180\%$.
*   Taux moyen : $180 / 12 = 15$.

Le taux d'activité moyen est de **150,0 %**.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse annonce d'abord « 90,0 % » puis conclut « Le taux d'activité moyen est de **150,0 %** » (après un calcul 180/12 = 15), au lieu de 93,3 %, et se contredit : le calcul juste (1120/12 = 93,33) n'est pas retenu comme résultat final.
- Inventions : Affirmation que, selon l'INSEE, le taux d'activité moyen se calcule en sommant les pourcentages des mois actifs sur le nombre total de mois; « 1800 heures d'activité sur 1752 heures de travail, soit un taux de 104,5 % d'activité réelle »; Résultat final de 150,0 % présenté comme « mathématiquement correct »
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
Le service public suspendra l'accueil du public le 3 juin pour des travaux.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La phrase compte 13 mots et respecte tous les critères : date « 3 juin » et cause « travaux » conservées, formule « Il est porté à votre connaissance » supprimée, aucune information ajoutée, orthographe correcte ; le sujet générique « Le service public » et la répétition de « public » restent maladroits.
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
D'après les passages fournis, voici la réponse à la question posée par l'usagère :

**Qui est l'Anah et à quoi sert-elle concrètement ?**

L'Anah est l'Agence Nationale de l'Habitat. Elle met en œuvre la politique nationale d'amélioration du parc de logements privés existants.

Pour les particuliers, elle accorde des aides financières aux propriétaires occupants et bailleurs ainsi qu'aux syndicats de copropriétaires pour la réalisation de travaux lourds ou d'amélioration de leur habitat, sous certaines conditions. Ces aides peuvent être octroyées directement ou via des dispositifs opérationnels mis en œuvre par les Collectivités locales.

**Points clés à retenir pour l'usagère :**
*   **Objectif :** Améliorer le parc de logements privés.
*   **Cible :** Propriétaires occupants, bailleurs et syndicats de copropriétaires.
*   **Moyens :** Aides financières versées par virement bancaire après la réalisation des travaux.
*   **Note importante :** Une partie importante des subventions est octroyée par les Collectivités locales.

**Ce qui reste à vérifier (selon les passages) :**
*   Les passages ne précisent pas le montant exact des aides ou les conditions précises sous lesquelles elles sont accordées (ex: type de travaux, critères de résidence principale).
*   Il n'est pas indiqué si l'intermédiation locative est obligatoire pour bénéficier de l'aide ou si elle est optionnelle.
*   Les détails sur la réduction fiscale et la prime d'intermédiation locative ne sont pas fournis dans les passages.

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

- `exactitude` : 0 — Seul le premier élément clé est présent (« L'Anah est l'Agence Nationale de l'Habitat… accorde des aides financières… sous certaines conditions »). Quatre éléments clés manquent : MaPrimeRénov', MaPrimeRénov' Copropriété et Loc'Avantages, MaPrimeAdapt', Ma Prime Logement décent, ainsi que la demande en ligne et le conseiller France Rénov'. La mention « Ne vaut pas avis juridique » est également absente.
- `pertinence_source` : 0 — La sortie indique « Sources citées : aucune », donc aucune source traitant du point demandé n'est citée.
- Inventions : Elle met en œuvre la politique nationale d'amélioration du parc de logements privés existants; Aides financières versées par virement bancaire après la réalisation des travaux; Une partie importante des subventions est octroyée par les Collectivités locales; Ces aides peuvent être octroyées directement ou via des dispositifs opérationnels mis en œuvre par les Collectivités locales; réalisation de travaux lourds; Références à l'intermédiation locative, à la réduction fiscale et à la prime d'intermédiation locative
- Confiance : haute

**Juge second** : juge

- `exactitude` : 1 — Un élément clé manque (les dispositifs spécifiques comme MaPrimeRénov', MaPrimeAdapt' ou Ma Prime Logement décent ne sont pas mentionnés), et la précision sur la demande en ligne via un compte personnel ainsi que le contact avec un conseiller France Rénov' est absente.
- `pertinence_source` : 0 — Aucune source n'est citée dans la réponse, alors que les références en attendent une (ex: service-public.gouv.fr).
- Inventions : La mention des 'dispositifs opérationnels mis en œuvre par les Collectivités locales' comme moyen principal d'octroi des aides n'est pas explicitement vérifiable dans les références.; L'affirmation selon laquelle 'une partie importante des subventions est octroyée par les Collectivités locales' n'est pas confirmée par les références.; Les points à vérifier (montant des aides, conditions précises, intermédiation locative, réduction fiscale) sont des inventions, car ils ne figurent pas dans les éléments clés ou la réponse de référence.
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
En fonction des passages fournis, voici les informations à transmettre à la demandante :

**1. Comment la perte d'autonomie sera évaluée ?**
L'évaluation se fait par un professionnel de l'équipe médico-sociale (EMS) qui se déplace chez la mère. Ce professionnel utilise la **grille Aggir** pour déterminer le degré de perte d'autonomie.

**2. À partir de quel niveau l'Apa peut être accordée ?**
L'Apa peut être accordée uniquement si la mère est classée en **Gir 1, Gir 2, Gir 3 ou Gir 4**.
*   Si elle est classée en **Gir 5 ou Gir 6**, elle ne peut pas obtenir l'Apa à domicile, mais peut demander une aide auprès de sa caisse de retraite.

**Note importante :** La décision finale d'attribution de l'Apa est prise par les services du département, qui doivent rendre leur décision dans les **2 mois** suivant la réception du dossier complet.

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

- `exactitude` : 0 — Au moins deux éléments clés manquent : la réponse n'évoque ni les 10 activités discriminantes et 7 illustratives, ni la mention « à domicile ou en établissement » pour les Gir 1 à 4. Le classement en 6 Gir n'est pas explicité. Pour les Gir 5-6, la formulation est imprécise (« ne peut pas obtenir l'Apa à domicile ») et l'aide ménagère est omise.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), alors que la fiche F1229 de service-public.gouv.fr était attendue.
- Inventions : L'évaluation se fait par un professionnel de l'équipe médico-sociale (EMS) qui se déplace chez la mère; La décision finale d'attribution de l'Apa est prise par les services du département, qui doivent rendre leur décision dans les 2 mois suivant la réception du dossier complet
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
Oui, une personne qui perçoit l'allocation aux adultes handicapés (AAH) peut cumuler cette allocation avec le revenu de solidarité active (RSA), mais le montant du RSA sera réduit par le montant de l'AAH.

Selon les passages fournis :
- [1] : « Oui, vous pouvez cumuler le revenu de solidarité active (RSA) et l'allocation aux adultes handicapés (AAH) si vous remplissez les conditions requises. Cependant, si vous percevez l'AAH, vous ne pouvez pas percevoir le RSA dans son intégralité. Le montant de votre RSA sera alors réduit par rapport au montant de votre AAH que vous percevez. »
- [3] : « Si vous percevez d'autres allocations (par exemple : pension d'invalidité, RSA ), vous recevez une AAH réduite. »

**Note importante :** Les passages [1] et [3] mentionnent que l'AAH peut se cumuler avec la « Prime d'activité », la « Majoration pour la vie autonome » ou la « Réduction sociale téléphonique », mais ils précisent que l'AAH ne peut pas se cumuler avec l'allocation de solidarité spécifique (ASS). Le passage [1] ne mentionne pas l'ASS, donc il n'est pas nécessaire de vérifier cette condition spécifique pour la réponse à la question posée.

Sources citées :
- Peut-on cumuler l'allocation adulte handicapé (AAH) et le RSA ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F20209
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

- `exactitude` : 0 — La réponse couvre le cumul sous conditions et la réduction du RSA, mais omet qu'il peut être plus avantageux de garder la seule AAH ; elle contredit aussi la référence en citant que, si l'on perçoit le RSA, « vous recevez une AAH réduite » (c'est le RSA qui est réduit) ; enfin, sa « note importante » sur l'ASS et les autres cumuls est confuse et invérifiable.
- `pertinence_source` : 1 — La source F20209 citée est exactement la source attendue et traite directement du cumul AAH/RSA.
- Inventions : Citation du passage [3] : « Si vous percevez d'autres allocations (par exemple : pension d'invalidité, RSA), vous recevez une AAH réduite », qui contredit la référence.; Affirmation que les passages [1] et [3] mentionnent le cumul de l'AAH avec la prime d'activité, la majoration pour la vie autonome ou la réduction sociale téléphonique, et l'interdiction du cumul avec l'ASS, invérifiable dans les références.
- Confiance : moyenne

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
**Oui**, la femme peut encore demander la PCH.

**Raison :** Selon le passage [1], la PCH est attribuée « sans condition de ressources », mais les ressources sont prises en compte pour déterminer le taux de prise en charge. Elle doit avoir moins de 60 ans pour demander, mais le passage [1] précise qu'elle peut « demander la PCH au-delà de 60 ans et sans limite d'âge si vous remplissiez déjà les conditions d'attribution avant 60 ans ou si vous continuez à travailler ». Comme elle a déjà rempli les conditions avant 60 ans, elle est éligible.

**Demande :** Elle doit déposer sa demande auprès de la MDPH de son lieu de résidence. Selon le passage [2], elle peut le faire par téléservice (si la MDPH le propose) ou par courrier en joignant les documents justificatifs.

**Réponse complète :**
« Oui, la femme peut encore demander la PCH car elle a déjà rempli les conditions d'attribution avant 60 ans. Elle doit déposer sa demande auprès de la MDPH de son lieu de résidence, soit par téléservice (si disponible), soit par courrier avec les documents justificatifs. »

Sources citées :
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

- `exactitude` : 0 — Plusieurs éléments clés manquent : critères de difficulté (absolue pour 1 activité ou grave pour 2, durée ≥ 1 an), taux 100 %/80 % avec le seuil de 31 162,62 €, et délai de 4 mois de la CDAPH avec rejet implicite ; en outre, la sortie affirme sans réserve « elle a déjà rempli les conditions avant 60 ans », alors que l'entrée indique seulement un handicap depuis 50 ans, ce qui ne suffit pas à établir que les conditions étaient remplies.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F14202) traite bien de la PCH et correspond à la source attendue.
- Inventions : « Comme elle a déjà rempli les conditions avant 60 ans, elle est éligible » : affirmation non établie par l'entrée, qui mentionne seulement un handicap depuis l'âge de 50 ans
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
**Oui**, la locataire peut bénéficier de MaPrimeAdapt'.

**Taux de prise en charge :** 50 % du montant des travaux.
**Montant de l'aide :** 5 000 € HT (car le plafond de ressources pour un foyer de 1 personne en Île-de-France est de 29 253 €, et 20 000 € est inférieur).

**Démarches à suivre :**
1.  **Déposer la demande en ligne :** Elle doit créer un compte personnel sur le site **monprojetanah** (URL : https://www.monprojetanah.fr/) et y déposer sa demande.
2.  **Condition du bail :** Elle doit obtenir l'accord de son bailleur pour réaliser les travaux.
3.  **Condition de ressources :** Son revenu fiscal de référence de 20 000 € est inférieur au plafond de ressources pour un foyer de 1 personne en Île-de-France (29 253 €), ce qui lui permet d'être éligible.
4.  **Cumul possible :** Elle peut cumuler cette aide avec la PCH ou l'allocation adulte handicapé (AAH), selon les règles applicables.

*Note : Les passages [1], [2], [3] et [4] confirment que les locataires du parc privé peuvent bénéficier de l'aide sous conditions de ressources et de l'accord du bailleur. Le passage [5] précise que les travaux doivent concerner la résidence principale située en métropole ou en Outre-mer, et que l'aide est de 50 % pour les locataires, avec un plafond de 22 000 € hors taxes pour les « très modestes » (ce qui correspond à 20 000 € dans ce contexte).*

Sources citées :
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
- MaPrimeAdapt' : travaux d'adaptation du logement à la perte d'autonomie — https://www.service-public.gouv.fr/particuliers/vosdroits/F37501
```

### Contrôles automatiques

```text
{
  "urls_inventees": [
    "https://www.monprojetanah.fr/"
  ]
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse applique à tort le plafond d'Île-de-France (« plafond de ressources pour un foyer de 1 personne en Île-de-France est de 29 253 € ») alors que la locataire vit hors Île-de-France, ne qualifie pas le ménage de « modeste » (17 363 € / 22 259 €), affirme de façon erronée « 50 % pour les locataires » et associe le plafond de 22 000 € HT aux « très modestes », n'évoque ni la condition d'âge/Gir ni l'accord de l'Anah à attendre avant les travaux, et omet la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F37501) correspond à la source attendue et traite bien de MaPrimeAdapt'.
- Inventions : Plafond de ressources Île-de-France de 29 253 € appliqué à une personne vivant hors Île-de-France; « l'aide est de 50 % pour les locataires » (taux présenté comme lié au statut de locataire); Plafond de 22 000 € HT présenté comme réservé aux « très modestes » (« ce qui correspond à 20 000 € dans ce contexte »); Cumul possible avec la PCH ou l'AAH, non vérifiable dans les références; Montant de l'aide exprimé « 5 000 € HT »
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
Pour inscrire le divorce de l'usager sur son livret de famille, vous devez lui indiquer qu'un **second livret de famille** doit être remis à celui qui ne possède pas le livret original.

Selon les passages fournis, en cas de divorce ou de séparation, chaque époux ou parent peut demander un second livret. La démarche varie selon le lieu de résidence :
- Si l'usager habite en France, il doit se rendre à la mairie où il réside.
- Si l'usager habite à Paris, il doit remplir un formulaire spécifique et l'adresser à sa mairie.
- Si l'usager habite à l'étranger, il doit se rendre aux autorités consulaires françaises de son pays de résidence.

Le passage [2] précise également que les mentions de divorce apparaissent sur le livret avec l'extrait d'acte de mariage, et que le second livret est nécessaire pour effectuer certaines démarches administratives comme l'inscription scolaire des enfants.

Sources citées :
- Mise à jour du livret de famille à la suite d'un changement d'état civil (naissance, divorce, etc.) — https://www.service-public.gouv.fr/particuliers/vosdroits/F18910
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — Trois éléments clés manquent : la mise à jour par l'officier de l'état civil (remplir, dater, signer, tamponner), le déplacement à la mairie du lieu de mariage avec la carte d'identité et le jugement de divorce, et la possibilité, non garantie, de passer par la mairie de résidence ; la réponse traite surtout du second livret et affirme qu'il « doit être remis » alors que la référence indique qu'il « peut » l'être.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F18910) correspond à la source attendue et porte bien sur la mise à jour du livret de famille après un divorce.
- Inventions : Si l'usager habite à Paris, il doit remplir un formulaire spécifique et l'adresser à sa mairie; Si l'usager habite à l'étranger, il doit se rendre aux autorités consulaires françaises de son pays de résidence; Le second livret est nécessaire pour effectuer certaines démarches administratives comme l'inscription scolaire des enfants; Si l'usager habite en France, il doit se rendre à la mairie où il réside (pour le second livret)
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
En fonction des passages fournis, il est impossible de répondre à votre question.

Les documents indiquent que :
1.  **L'épousée à titre posthume n'est pas mentionnée** dans les démarches listées (seuls les obsèques, les impôts, les contrats de vie, les assurances et les successions sont évoqués).
2.  **La date de décès est fixée à 2026**, ce qui rend impossible de vérifier les conditions d'éligibilité pour une épousée posthume (qui nécessite généralement un mariage antérieur à la date du décès).
3.  **Les conditions de mariage sont strictes** : elles exigent un mariage antérieur à la date du décès et un consentement des survivants (ce qui n'est pas évoqué dans les passages).

**Orientation :**
Pour obtenir une réponse précise sur la procédure d'épousée à titre posthume, vous devez consulter le site officiel de l'État civil ou contacter le service des mariages et unions civiles, qui gère spécifiquement les cas de mariage post-mortem.

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

- `exactitude` : 0 — La sortie avance comme des faits des éléments non sourcés et erronés : « La date de décès est fixée à 2026 » et « elles exigent un mariage antérieur à la date du décès et un consentement des survivants ». Elle attribue aussi une compétence inventée à un « service des mariages et unions civiles, qui gère spécifiquement les cas de mariage post-mortem ». Enfin, elle omet l'orientation vers un professionnel du droit et la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — Aucune source n'est citée (« Sources citées : aucune »), ce qui est cohérent avec un item sans réponse dont les sources attendues sont vides ; aucune source hors sujet n'est présentée comme traitant du mariage posthume.
- `cas_sans_reponse` : 0 — La sortie dit d'abord ne pas pouvoir répondre, mais invente ensuite des conditions (« mariage antérieur à la date du décès et un consentement des survivants »). Elle oriente vers un service présenté à tort comme compétent, au lieu de renvoyer simplement à l'état civil de la mairie ou à un avocat ou notaire.
- Inventions : La date de décès est fixée à 2026; Les conditions de mariage posthume exigent un mariage antérieur à la date du décès; Les conditions exigent un consentement des survivants; Mention de démarches listées (obsèques, impôts, contrats de vie, assurances, successions) dans des documents non vérifiables; Un « service des mariages et unions civiles » gère spécifiquement les cas de mariage post-mortem; Renvoi à un « site officiel de l'État civil » non identifié
- Confiance : haute

**Juge second** : juge

- `exactitude` : 0 — La sortie invente des éléments non vérifiables dans l'entrée ou les références, comme la 'date de décès fixée à 2026' et des 'conditions de mariage strictes' (mariage antérieur au décès, consentement des survivants), alors que les références interdisent toute invention de procédure ou condition.
- `pertinence_source` : 0 — Aucune source pertinente n'est citée, et la sortie mentionne des éléments hors sujet (ex. : 'date de décès fixée à 2026') sans lien avec les références.
- `cas_sans_reponse` : 0 — La sortie invente des informations (conditions d'éligibilité, autorité compétente) au lieu de se limiter à dire qu'aucune source officielle n'est disponible et d'orienter vers la mairie ou un professionnel du droit.
- Inventions : La date de décès est fixée à 2026; Les conditions d'éligibilité pour une épousée posthume nécessitent généralement un mariage antérieur à la date du décès; Un consentement des survivants est exigé; Le service des mariages et unions civiles gère spécifiquement les cas de mariage post-mortem
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
La journée de solidarité consiste en une journée de travail supplémentaire non rémunérée destinée au financement d'actions en faveur de l'autonomie des personnes âgées ou handicapées. Elle prend la forme d'une journée de 7 heures supplémentaires, qui peuvent être réduites en proportion de la durée de travail des agents à temps partiel ou à temps non complet.

Elle peut être accomplie selon les modalités suivantes :
- Travail d'un jour férié précédemment chômé autre que le 1er mai (ex: lundi de Pentecôte) ou d'un jour férié normalement chômé dans les départements de la Moselle, du Bas-Rhin et du Haut-Rhin (ex: 25 et 26 décembre, Vendredi Saint).
- Suppression d'une journée de RTT.
- Toute autre organisation permettant le travail de 7 heures précédemment non travaillées, sauf suppression d'un jour de congé annuel.

Les modalités d'accomplissement et les conditions fixent sont fixées par des textes spécifiques selon le type de fonction publique :
- En fonction publique d'État : par arrêté ministériel après avis du comité social d'administration ministériel concerné.
- En fonction publique territoriale : par délibération après avis du comité social territorial.
- En fonction publique hospitalière : par décision du directeur de l'établissement, après avis du comité social d'établissement.

*Note : Les passages fournis ne précisent pas si cette journée s'applique aux agents territoriaux (agents de la fonction publique territoriale), mais elle est applicable aux fonctionnaires et aux contractuels.*

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

- `exactitude` : 0 — La réponse contient une erreur factuelle sur l'Alsace-Moselle : elle cite « 25 et 26 décembre, Vendredi Saint » comme exemples de jours pouvant être travaillés, alors que la référence ne vise que le cas général hors Alsace-Moselle et que ces jours sont en réalité exclus. Elle se contredit aussi en affirmant que « les passages fournis ne précisent pas si cette journée s'applique aux agents territoriaux » tout en citant la délibération en FPT. Enfin, la mention obligatoire « Ne vaut pas avis juridique » est absente.
- `pertinence_source` : 0 — La réponse indique « Sources citées : aucune », donc aucune source traitant du point demandé n'est citée (la source attendue F2859 est absente).
- Inventions : Travail d'un jour férié normalement chômé en Moselle, Bas-Rhin et Haut-Rhin (ex : 25 et 26 décembre, Vendredi Saint) comme modalité d'accomplissement; En fonction publique d'État : fixation par arrêté ministériel après avis du comité social d'administration ministériel; En fonction publique hospitalière : fixation par décision du directeur de l'établissement après avis du comité social d'établissement
- Confiance : haute

**Juge second** : juge

- `exactitude` : 1 — Un élément clé est imprécis : la mention des départements de la Moselle, du Bas-Rhin et du Haut-Rhin (Alsace-Moselle) est hors sujet pour le cas général, car la référence précise que ces modalités s'appliquent 'hors Alsace-Moselle'. De plus, la distinction des modalités selon le type de fonction publique (État, hospitalière) n'est pas un élément clé attendu pour la FPT.
- `pertinence_source` : 0 — Aucune source n'est citée, alors que la référence en attend au moins une.
- Inventions : Mention des modalités spécifiques aux départements de la Moselle, du Bas-Rhin et du Haut-Rhin (Alsace-Moselle) pour un cas général hors de ce périmètre; Détails sur les modalités de fixation dans la fonction publique d'État et hospitalière, non demandés pour la FPT
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
Non, un nouveau jour de carence ne doit pas être retenu dans ce cas précis.

Selon les passages fournis, le jour de carence ne s'applique pas lors de la prolongation de congés de maladie dans les 48 heures, lorsque le médecin prescripteur a coché la case « prolongation ». Dans votre situation, l'arrêt du mardi est considéré comme une prolongation de l'arrêt du lundi (car l'arrêt du mardi a eu lieu dans les 48 heures et le médecin a coché la case prolongation), ce qui empêche l'application du jour de carence.

La règle générale, selon les passages, est que lorsqu'un agent public est en congé de maladie, il est appliqué, lors de chaque arrêt de travail, un jour de carence, c'est-à-dire un jour non rémunéré. Cependant, cette règle ne s'applique pas si le congé de maladie est prolongé dans les 48 heures par un arrêt de travail qui prolonge l'arrêt précédent et que le médecin prescripteur a coché la case « prolongation ».

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

- `exactitude` : 0 — Au moins deux éléments clés manquent : la sortie ne précise ni les éléments non versés le 1er jour (traitement, primes, indemnité de résidence, NBI ; maintien du SFT), ni le décompte des 48 heures en jours calendaires. Elle omet aussi la condition de « même affection » dans l'énoncé de l'exception et commet une erreur en qualifiant l'arrêt du mardi de « prolongation de l'arrêt du lundi », alors que le lundi était un jour de reprise.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), alors que la fiche F13861 de service-public.gouv.fr était attendue.
- Inventions : aucune
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
**Oui**, il est possible pour une agente enceinte de télétravailler 4 jours par semaine, mais cela nécessite une demande spécifique et des conditions strictes.

**1. Possibilité de 4 jours par semaine**
Selon les passages, le nombre maximum de jours de télétravail pour un agent à temps plein est fixé à 3 jours par semaine. Cependant, l'autorisation peut prévoir l'attribution de jours de télétravail fixes ou **flottants** (passage [3]). De plus, si l'agent est enceinte, elle peut demander à télétravailler plus de 3 jours par semaine pendant 6 mois maximum renouvelables, après avis du médecin du travail (passage [1]).

**2. Comment faire sa demande**
La demande doit être adressée à son supérieur hiérarchique pour obtenir une autorisation écrite. Ce document doit préciser :
*   Les fonctions exercées en télétravail.
*   Le lieu de télétravail.
*   Les conditions de mise en œuvre et les plages horaires (passage [4]).
*   Le document d'information détaillant les conditions de contrôle, de comptabilisation du temps de travail, les équipements et l'appui technique fourni (passage [4]).

**3. Montant du forfait télétravail**
Le montant du forfait télétravail est calculé sur la base du nombre de jours de télétravail **déclarés et autorisés** par l'administration.
*   Le forfait est de **2,88 € par journée de télétravail effectuée** dans la limite de 253,44 € par an (soit 88 jours indemnisés).
*   Il est versé à la fin de chaque trimestre (passage [2]).
*   Il ne fait l'objet d'aucune cotisation (passage [2]).

**Note importante :**
Les passages fournis ne précisent pas le montant exact du forfait pour une journée de télétravail effectuée dans un télécentre (car ce montant dépend de la nature du local et de la disponibilité du service de restauration collective financé par l'administration employeur, comme indiqué dans le passage [2]). L'agent devra donc vérifier avec son administration employeur la disponibilité du télécentre pour déterminer le montant final.

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

- `exactitude` : 0 — Au moins deux éléments clés sont incomplets ou erronés : le minimum de 2 jours sur site et la décision écrite dans le mois sont absents, et la grossesse est soumise à tort à des conditions invérifiables (« pendant 6 mois maximum renouvelables, après avis du médecin du travail »).
- `pertinence_source` : 1 — La source citée, service-public.gouv.fr F13974 (Télétravail dans la fonction publique), correspond à la source attendue et traite bien du sujet.
- Inventions : Pendant la grossesse, télétravail de plus de 3 jours « pendant 6 mois maximum renouvelables, après avis du médecin du travail »; Le forfait ne fait l'objet d'aucune cotisation; Montant du forfait calculé sur les jours « déclarés et autorisés » par l'administration; Montant différent pour une journée en télécentre selon la nature du local et la restauration collective; La demande doit être adressée au supérieur hiérarchique, avec un contenu détaillé de l'autorisation (fonctions, plages horaires, document d'information)
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
Pour présenter l'ARS Bourgogne-Franche-Comté à vos partenaires médico-sociaux, voici les éléments clés à inclure, basés sur les passages fournis :

*   **Statut et Missions :** L'ARS est un établissement de santé de proximité (selon la description des Maisons régionales de santé en PACA, qui illustrent le type d'établissement de proximité concerné) qui assure la coordination et la complémentarité des soins. Ses missions incluent la réduction des inégalités territoriales, l'offres de soins et de santé publique, ainsi que la mutualisation des fonctions administratives et l'accueil d'étudiants.
*   **Organisation :** Bien que les passages ne détaillent pas la structure hiérarchique interne de l'ARS, ils confirment que l'ARS est un établissement de santé répertorié dans le système FINESS, géolocalisé en Bourgogne-Franche-Comté, et qu'il fonctionne en réseau pour répondre aux besoins de santé de la population.

**Note importante :** Les passages fournis ne contiennent aucune information sur la structure interne de l'ARS (nombre de services, hiérarchie des directions, etc.). Pour une présentation complète, il faudra consulter les documents officiels de l'ARS ou le site web de la DREAL Bourgogne-Franche-Comté pour obtenir les détails sur son organisation.

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

- `exactitude` : 0 — La sortie avance un statut et des missions non sourcés et erronés (« L'ARS est un établissement de santé de proximité », « répertorié dans le système FINESS ») et ne déclare pas l'absence de source officielle, ce qui la met en contradiction avec plusieurs éléments clés.
- `pertinence_source` : 0 — Aucune source n'est citée (« Sources citées : aucune »), et les passages invoqués (Maisons régionales de santé en PACA) sont hors sujet.
- `cas_sans_reponse` : 0 — Au lieu de dire qu'aucune source officielle ne présente l'ARS Bourgogne-Franche-Comté, l'Assistant invente une présentation et oriente vers le site de la DREAL au lieu de celui de l'ARS ; la mention « Ne vaut pas avis juridique » est absente.
- Inventions : L'ARS est un établissement de santé de proximité; Missions : réduction des inégalités territoriales, offre de soins et de santé publique, mutualisation des fonctions administratives et accueil d'étudiants; L'ARS est un établissement de santé répertorié dans le système FINESS, géolocalisé en Bourgogne-Franche-Comté; L'ARS fonctionne en réseau pour répondre aux besoins de santé de la population; Orientation vers le site web de la DREAL Bourgogne-Franche-Comté pour obtenir les détails sur l'organisation de l'ARS
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
En tant qu'Assistant des Agents du service public, je dois vous informer que **aucun passage de l'Index local fourni ne permet de répondre à votre question**.

Voici les éléments de réponse :

1.  **Absence de définition des friches commerciales** :
    *   Le passage **[4] Friches issues de l' EPFN dans l'Orne en 2026** définit la friche comme « tout espace ayant accueilli une activité urbaine, économique ou un équipement... ». Il précise que les friches agricoles ne sont pas prises en compte sauf présence de bâtiments dégradés.
    *   Il n'y a **aucun passage** qui mentionne spécifiquement les « friches commerciales » ou les locaux commerciaux. La définition fournie ne couvre pas cette catégorie.

2.  **Absence de taux et de date de délibération** :
    *   Les passages **[1]** et **[2]** concernent la fiscalité locale générale (taxe d'aménagement, taxe d'habitation, taxe foncière) mais ne précisent pas de taux spécifiques pour les friches commerciales.
    *   Le passage **[3] Quels sont les travaux à déclarer aux impôts ?** explique que les travaux à déclarer sont ceux effectués sur une construction existante (démolition, agrandissement, changement de destination), mais il ne donne pas de taux de taxe d'aménagement ou de taxe foncière applicables aux friches commerciales.
    *   Aucun passage ne mentionne de date limite pour une délibération ou d'année d'application future.

**Orientation :**
Pour obtenir les informations demandées (définition des friches commerciales, taux applicables et date de délibération), vous devez consulter les documents officiels suivants :

*   **Le Code Général des Collectivités Territoriales (CGCT)** : Il définit la notion de « friche commerciale » et les règles de taxation.
*   **Le Bulletin des lois et des décrets** : Pour connaître les taux de taxe d'aménagement et de taxe foncière en vigueur.
*   **Le site de la Direction Départementale des Territoires (DDT) de l'Orne** : Pour consulter les délibérations locales récentes et les arrêtés de fixation des taux.

Je vous recommande de consulter les sources officielles mentionnées ci-dessus pour une réponse précise et conforme à la législation en vigueur.

Sources citées :
- Friches issues de l' EPFN dans l'Orne en 2026 — https://www.data.gouv.fr/datasets/friches-issues-de-l-epfn-dans-lorne-en-2026
- Taxe d'aménagement dans le cadre de la fiscalité de l'urbanisme pour 2021 — https://www.data.gouv.fr/datasets/taxe-damenagement-dans-le-cadre-de-la-fiscalite-de-lurbanisme-pour-2021
- Fiscalité locale - Millésimé — https://www.data.gouv.fr/datasets/fiscalite-locale-millesime
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

- `exactitude` : 0 — La réponse signale bien l'absence de passage pertinent, mais elle cite une fiche service-public comme source (« Quels sont les travaux à déclarer aux impôts ? — F35742 »). Elle avance aussi un fait erroné et non sourcé : « Le Code Général des Collectivités Territoriales (CGCT) : Il définit la notion de « friche commerciale » et les règles de taxation ». Enfin, elle oriente vers la DDT de l'Orne au lieu de la direction départementale des finances publiques, si bien qu'au moins deux éléments clés manquent ou sont contredits.
- `pertinence_source` : 0 — Les sources citées (friches EPFN de l'Orne, taxe d'aménagement 2021, fiscalité locale millésimée, fiche sur les travaux à déclarer) ne traitent pas de la taxe sur les friches commerciales.
- `cas_sans_reponse` : 0 — La réponse indique ne pas avoir trouvé de passage pertinent, mais elle n'oriente pas vers la DDFiP comme attendu, renvoyant plutôt vers la « DDT de l'Orne » et le « Bulletin des lois et des décrets ». Elle avance en outre des faits non sourcés présentés comme certains, et la mention « Ne vaut pas avis juridique » est absente.
- Inventions : Le CGCT définirait la notion de « friche commerciale » et les règles de taxation (affirmation non vérifiable dans l'entrée ou les références, et inexacte); Le « Bulletin des lois et des décrets » serait la source pour connaître les taux de taxe d'aménagement et de taxe foncière en vigueur; Le site de la DDT de l'Orne permettrait de consulter les délibérations locales et les arrêtés de fixation des taux; Les passages [1] et [2] concerneraient la taxe d'habitation et la taxe foncière (contenu non vérifiable)
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
Le jeu de données national sur data.gouv.fr qui traite des communes soumises à la loi SRU et de leur inventaire de logements sociaux est :

**Titre :** Communes et inventaire SRU
**Producteur :** Ministère de la Transition écologique
**Lien :** https://www.data.gouv.fr/datasets/communes-et-inventaire-sru

Pour vérifier les informations sur les communes et leur inventaire, je vais consulter les ressources disponibles dans ce jeu de données.

Je n'ai pas pu accéder aux ressources détaillées de ce jeu de données via les outils disponibles. Cependant, en me basant sur les informations fournies dans le résultat de recherche initial, voici les détails :

**Titre :** Communes et inventaire SRU
**Producteur :** Ministère de la Transition écologique
**Lien :** https://www.data.gouv.fr/datasets/communes-et-inventaire-sru

Pour obtenir les valeurs chiffrées de mémoire (nombre de communes, nombre de logements sociaux, etc.), je vous recommande de consulter directement le site web de la base de données ou d'utiliser l'outil de recherche de la plateforme data.gouv.fr avec les filtres appropriés (date de dernière mise à jour, type de données, etc.).

Si aucun outil ne permet de récupérer ces valeurs directement, je vous suggère de consulter les passages de l'Index local pour vérifier les informations sur les communes SRU et les logements sociaux.

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
Le jeu de données correspondant est :

**Titre :** RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National]
**Producteur :** Caisse Nationale des Allocations familiales
**Lien :** https://www.data.gouv.fr/datasets/rsa-repartition-des-allocataires-selon-le-type-de-rsa-et-la-situation-familiale-national

Je vais maintenant vérifier les détails de ce jeu de données (date de dernière mise à jour, licence, fréquence de mise à jour).

Voici les informations demandées pour ce jeu de données :

**Titre :** RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National]
**Producteur :** Caisse Nationale des Allocations familiales
**Date de dernière mise à jour :** 2026-10-09
**Licence :** lov2
**Fréquence de mise à jour :** mensuelle

Le jeu de données est disponible sur le lien fourni.

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
Le jeu national sur les bénéficiaires de l'aide sociale à l'enfance est identifié sous le titre **"Les bénéficiaires de l'aide sociale à l'enfance"**.

Voici les informations demandées :
*   **Titre :** Les bénéficiaires de l'aide sociale à l'enfance
*   **Producteur :** Ministère des Solidarités et de la Santé
*   **Date de dernière mise à jour :** (À vérifier via les ressources)
*   **Lien :** https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance

Je vais maintenant vérifier le nombre de fichiers et le fichier de séries longues le plus récent.

Le jeu national propose **20 fichiers**.

Le fichier de séries longues le plus récent est :
*   **Nom exact :** `Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2024).xlsx`
*   **Format :** `xlsx` (OpenXML Spreadsheet)
*   **Lien :** https://data.drees.solidarites-sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2024_xlsx

Pour confirmer la date de dernière mise à jour, je vais consulter les informations du jeu de données.

Je n'ai pas pu obtenir les informations de mise à jour via l'outil. Je vais donc vérifier les ressources pour confirmer la date de publication des fichiers les plus récents.

<tool_call>
<function=get_dataset_info>
<parameter=dataset_id>
62e325ed203e2e75a70505d1
</parameter>
</function>
</tool_call>

Sources citées :
- Les bénéficiaires de l'aide sociale à l'enfance — https://www.data.gouv.fr/datasets/les-beneficiaires-de-laide-sociale-a-lenfance
- Les bénéficiaires de l'aide sociale à l'enfance - séries longues (1996-2024).xlsx — https://data.drees.solidarites-sante.gouv.fr/api/v2/catalog/datasets/les-beneficiaires-de-l-aide-sociale-a-l-enfance/attachments/les_beneficiaires_de_l_aide_sociale_a_l_enfance_series_longues_1996_2024_xlsx
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
Voici les jeux de données qui correspondent à votre recherche sur data.gouv.fr :

1. **Répertoire national des élus**
   - **Producteur** : Ministère de l'intérieur
   - **Lien** : https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1

2. **Répertoire national des élus locaux - Communautaires de Grand Poitiers CU**
   - **Producteur** : Grand Poitiers Open Data
   - **Lien** : https://www.data.gouv.fr/datasets/repertoire-national-des-elus-locaux-communautaires-de-grand-poitiers-cu

3. **Répertoire national des élus locaux  : Municipaux des 40 communes membres de Grand Poitiers CU**
   - **Producteur** : Grand Poitiers Open Data
   - **Lien** : https://www.data.gouv.fr/datasets/repertoire-national-des-elus-locaux-municipaux-des-40-communes-membres-de-grand-poitiers-cu

4. **Elections municipales 2026 - Maires et conseillers municipaux sortants**
   - **Producteur** : Ministère de l'intérieur
   - **Lien** : https://www.data.gouv.fr/datasets/elections-municipales-2026-maires-et-conseillers-municipaux-sortants

Ces jeux de données couvrent les élus locaux (conseillers municipaux, départementaux, régionaux et communautaires) et les élections municipales.

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
Le jeu de données qui recense les guichets publics locaux sur data.gouv.fr est :

**Annuaire de l’administration - Base de données locales**
*   **Titre :** Annuaire de l’administration - Base de données locales
*   **Producteur :** Premier ministre
*   **Date de dernière mise à jour :** (non spécifiée dans les résultats)
*   **Lien :** https://www.data.gouv.fr/datasets/service-public-gouv-fr-annuaire-de-ladministration-base-de-donnees-locales

**Licence :** (non spécifiée dans les résultats)
**Fréquence de mise à jour :** (non spécifiée dans les résultats)

Pour obtenir ces informations détaillées (licence et fréquence de mise à jour), je vais consulter les détails de ce jeu de données.

Voici les informations demandées sur le jeu de données :

*   **Titre :** Annuaire de l’administration - Base de données locales
*   **Producteur :** Premier ministre
*   **Date de dernière mise à jour :** 2026-10-09
*   **Licence :** fr-lo
*   **Fréquence de mise à jour :** Punctuelle

Cette base de données référence plus de 86 000 guichets publics locaux (mairies, organismes sociaux, services de l'état, etc.) et fournit leurs coordonnées (adresses, téléphones, site internet, horaires d'ouverture, coordonnées de géolocalisation).

Sources citées :
- Service-public.gouv.fr - Annuaire de l’administration - Base de données locales — https://www.data.gouv.fr/datasets/service-public-gouv-fr-annuaire-de-ladministration-base-de-donnees-locales
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
Le jeu de données correspondant est :

*   **Titre :** Médecins accrédités par la HAS
*   **Producteur :** Haute Autorité de santé
*   **Lien :** https://www.data.gouv.fr/datasets/medecins-accredites-par-la-has

Pour vérifier les données, je vais consulter les ressources de ce jeu de données.

Je n'ai pas pu accéder aux ressources spécifiques de ce jeu de données via les outils disponibles. L'information n'a pas été vérifiée en ligne.

Je vous propose de chercher une autre piste de recherche sur data.gouv.fr en utilisant des termes plus larges liés à la HAS et aux médecins.

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
<tool_call>
<function=get_dataset_info>
<parameter=dataset_id>
64265b62141b6f2153538672
</parameter>
</function>
</tool_call>

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "appariement": [
    null,
    null,
    null
  ],
  "appels_attendus": 3,
  "appels_valides": 0,
  "litige": false,
  "methode": "valeurs",
  "reponse_exacte": false,
  "valeurs_manquantes": [
    "540.0",
    "110.4"
  ]
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
Je vais vous aider à trouver et à examiner le fichier FINESS.

Commençons par rechercher le jeu de données correspondant à "FINESS établissements sanitaires et sociaux".

J'ai trouvé plusieurs jeux de données FINESS. Le premier correspond exactement à votre recherche : "FINESS Extraction du Fichier des établissements".

Voici les informations sur ce jeu de données :
- **Titre** : FINESS Extraction du Fichier des établissements
- **Producteur** : Ministère des Solidarités et de la Santé
- **Date de dernière mise à jour** : non spécifiée dans les résultats de recherche
- **Lien** : https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements

Maintenant, je vais vérifier les ressources disponibles dans ce jeu de données pour trouver le fichier FINESS.

J'ai trouvé les ressources du jeu de données. Le fichier FINESS non géolocalisé correspond à :

- **Resource ID** : 2ce43ade-8d2c-4d1d-81da-ca06c82abc68
- **Titre** : Extraction Finess des Etablissements au 04/05/2026
- **Format** : CSV
- **Taille** : 34.1 MB
- **URL de téléchargement** : https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv

Je vais maintenant vérifier si cette ressource est interrogeable via l'API tabulaire.

L'API tabulaire n'est pas disponible pour cette ressource (pas de résultats).

Voici les informations complètes pour vous :

**Fichier FINESS non géolocalisé**
- **Titre** : Extraction Finess des Etablissements au 04/05/2026
- **Producteur** : Ministère des Solidarités et de la Santé
- **Date de dernière mise à jour** : 04/05/2026
- **Lien** : https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv

**Informations techniques**
- **Format** : CSV
- **Taille du fichier** : 34.1 MB
- **MIME type** : text/csv
- **URL de téléchargement** : https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv

L'API tabulaire de data.gouv.fr n'est pas disponible pour cette ressource. Vous pouvez télécharger le fichier CSV directement via le lien ci-dessus.

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
Ce document explique que la demande de logement peut être radiée si les revenus sont supérieurs au plafond, si la demande n'est pas renouvelée au mois précédent, ou si le bail est signé. Une radiation peut intervenir après un mois d'envoi d'avertissement ou sans délai. Pour contester, il faut se rendre au guichet enregistreur du département concerné. La radiation intervient également si l'ancienneté acquise est conservée.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "courte",
  "mots": 66,
  "plafond_mots": 80,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé déforme le document : « La radiation intervient également si l'ancienneté acquise est conservée » contredit le texte, qui parle de conserver l'ancienneté lors du regroupement de demandes. De plus, « Pour contester, il faut se rendre au guichet enregistreur » généralise à tort une voie réservée au cas du non-renouvellement.
- `presence_elements` :
  - P1 : 1 — Le cas d'irrecevabilité (revenus supérieurs au plafond) et la radiation « après un mois d'envoi d'avertissement » sont mentionnés, mais la lettre recommandée et les courriers sans réponse manquent.
  - P2 : 0 — Le non-renouvellement est cité, mais sans lien clair avec la radiation sans délai, et l'obligation de recommencer la procédure avec un nouveau numéro est absente.
  - P3 : 0 — La signature du bail est citée, mais la renonciation écrite est absente.
  - P4 : 0 — Seul le guichet enregistreur est cité ; la contestation auprès de l'organisme ou de l'administration qui a radié est omise.
- Inventions : La radiation intervient également si l'ancienneté acquise est conservée; Pour contester, il faut se rendre au guichet enregistreur du département concerné (présenté comme règle générale)
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

La procédure de changement de prénom est ouverte aux Français nés en France, aux Français nés à l'étranger (déclarés aux consulats français ou transcrits), aux étrangers nés en France et aux bénéficiaires de la protection internationale. Elle concerne les majeurs et les mineurs.

Pour les majeurs, la demande peut être déposée par le demandeur lui-même depuis le 1er juillet 2022, même sous tutelle. Pour les mineurs, la demande doit être faite par le représentant légal. Si l'enfant a plus de 13 ans, son accord est requis. En cas d'exercice conjoint de l'autorité parentale, les deux parents doivent co-signer la demande. En cas de séparation et de désaccord, le parent souhaitant la modification doit saisir le juge aux affaires familiales.

La demande doit avoir un intérêt légitime. Les motifs acceptés incluent l'usage prolongé d'un prénom autre que celui figurant à l'état civil, la suppression d'un prénom jugé ridicule, l'ajout ou la suppression d'un tiret entre prénoms suite à un usage prolongé, ou la transidentité. La demande ne doit pas être contraire à l'intérêt de l'enfant ni aux droits des autres personnes. Tout prénom inscrit dans l'acte de naissance peut être choisi comme prénom usuel, quel que soit son ordre.

La démarche est gratuite. La demande doit être déposée au domicile de résidence, à la mairie du lieu de naissance (si né en France), à l'ambassade ou au consulat de France compétent, ou à l'Ofpra en cas de certificat d'origine. Un récépissé de dépôt est remis.

Si l'officier de l'état civil estime que la demande n'a pas d'intérêt légitime, il doit saisir le procureur de la République. Des cas de refus sont possibles en cas de condamnation pour infraction terroriste, infraction sexuelle sur mineur, violation d'interdiction de sortie, non-respect des obligations de contrôle du retour, inscription au Fijait ou Fijaisv. L'officier doit notifier le procureur de la République de la saisine. Le procureur peut accepter ou refuser la demande. En cas de refus, le demandeur peut faire un recours auprès du juge aux affaires familiales, auquel cas un avocat est obligatoire.

Une fois la décision notifiée, les actes de l'état civil sont mis à jour. Le demandeur doit ensuite modifier ses titres d'identité (carte d'identité, passeport) dans un délai de 3 mois à partir de la mise à jour de l'acte de naissance. L'usage d'un titre d'identité non conforme à l'état civil est puni de 5 ans d'emprisonnement maximum et d'une amende pouvant atteindre 50 000 €.

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

- `fidelite` : 0 — Plusieurs informations sont déformées : « L'officier doit notifier le procureur de la République de la saisine » alors que c'est le demandeur qui doit être informé, « Des cas de refus sont possibles en cas de condamnation » alors que le document prévoit une saisine du procureur, et « déposée au domicile de résidence » ou « certificat d'origine » au lieu de la mairie de résidence et du certificat tenant lieu d'acte de naissance.
- `presence_elements` :
  - P1 : 1 — Les quatre catégories de bénéficiaires sont citées correctement.
  - P2 : 1 — Le majeur sous tutelle, le représentant légal, l'accord au-delà de 13 ans, les deux parents et le JAF en cas de désaccord sont mentionnés.
  - P3 : 0 — L'intérêt légitime et les limites sont présents, mais la possibilité d'ajouter, de supprimer ou de réordonner les prénoms est omise.
  - P4 : 1 — « Tout prénom inscrit dans l'acte de naissance peut être choisi comme prénom usuel » est repris.
  - P5 : 1 — La gratuité, les lieux de dépôt (malgré des approximations) et le récépissé sont mentionnés.
  - P6 : 0 — Les cas de condamnation sont présentés comme des cas de refus et non de saisine, et l'information du demandeur est transformée en notification au procureur.
  - P7 : 1 — Le recours devant le JAF avec avocat obligatoire est mentionné.
  - P8 : 0 — La règle sur l'apparence physique et sur les prénoms neutres ou épicènes en cas de transidentité est absente.
  - P9 : 1 — La mise à jour des actes, le délai de 3 mois et les sanctions de 5 ans et 50 000 € sont présents.
- Inventions : « L'officier doit notifier le procureur de la République de la saisine » (le document prévoit l'information du demandeur); « Des cas de refus sont possibles en cas de condamnation... » (le document prévoit une saisine obligatoire du procureur, pas un refus); « déposée au domicile de résidence » (le document indique la mairie du lieu de résidence); « certificat d'origine » (le document indique un certificat tenant lieu d'acte de naissance); « les deux parents doivent co-signer » (formulation non présente dans le document)
- Confiance : haute

**Juge second** : juge

- `fidelite` : 1 — Aucune information absente du document ou déformée n'a été identifiée dans le résumé.
- `presence_elements` :
  - P1 : 1 — Le résumé couvre correctement les bénéficiaires de la procédure de changement de prénom.
  - P2 : 1 — Les conditions pour les majeurs et les mineurs, y compris l'accord des enfants de plus de 13 ans et le rôle du juge aux affaires familiales, sont bien présentes.
  - P3 : 1 — Les possibilités de modification (ajout, suppression, ordre) et la nécessité d'un intérêt légitime sont mentionnées.
  - P4 : 1 — La possibilité de choisir tout prénom inscrit comme prénom usuel est explicitement indiquée.
  - P5 : 1 — La gratuité de la démarche et les lieux de dépôt (mairie, ambassade, Ofpra) sont correctement décrits.
  - P6 : 1 — Le rôle de l'officier d'état civil et du procureur de la République est bien expliqué, y compris les cas de saisine.
  - P7 : 1 — Le recours possible devant le juge aux affaires familiales en cas de refus, avec l'obligation d'un avocat, est mentionné.
  - P8 : 1 — La mention spécifique de la transidentité et l'absence de motivation basée sur l'apparence physique sont présentes.
  - P9 : 1 — La mise à jour des actes d'état civil et l'obligation de modifier les titres d'identité sous peine de sanctions sont correctement rapportées.
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
**Résumé détaillé du Pacte Civil de Solidarité (Pacs)**

**Objet** : Conduite administrative pour l'enregistrement d'un Pacs en mairie ou auprès d'une ambassade/consulat.

**Personnes concernées** : Les futurs partenaires (de même ou de différents sexes, nationaux ou non).

**Conditions préalables** :
- Être majeurs.
- N'être pas mariés ou déjà pacsés.
- Ne pas avoir de lien familial direct ou trop proche avec l'autre partenaire.
- Si l'un est étranger, respecter l'âge de la majorité fixée par son pays.
- Une dispense n'est pas possible.

**Obligations et engagements** :
- Se pacsant, les futurs s'engagent à une vie commune.
- Ils doivent choisir une résidence commune et déclarer leur adresse par une attestation sur l'honneur.
- Ils doivent rédiger et signer un contrat de Pacs (convention). Ce contrat peut être rédigé par les futurs eux-mêmes ou par un notaire.
- Le contrat doit être rédigé en français et comporter les deux signatures.
- Le contrat doit consigner l'engagement et la volonté d'être liés par un Pacs, en reprenant le texte obligatoire de la loi du 15 novembre 1999 modifiée et des articles 515-1 à 515-7 du code civil.
- Le contrat précise les conditions de participation à la vie commune (partage de biens, régime de l'indivision, etc.).
- En l'absence de précisions dans le contrat, les patrimoines sont séparés (régime légal de séparation).

**Délais et démarches** :
- **En mairie** :
  - Dépôt du dossier : gratuit.
  - Enregistrement : généralement sur rendez-vous.
  - Présence obligatoire : les futurs doivent se présenter ensemble à l'officier d'état civil de la commune de résidence commune.
  - En cas d'empêchement grave, l'officier peut se déplacer au domicile ou à l'hôpital.
  - La convention de Pacs est restituée après l'enregistrement.
  - Une déclaration conjointe de modification de Pacs peut être effectuée si la convention initiale est perdue (en indiquant les références du Pacs initial).
- **Avec une ambassade ou un consulat** :
  - Dépôt du dossier : gratuit.
  - Enregistrement : généralement sur rendez-vous.
  - Présence obligatoire : les futurs doivent se présenter ensemble à l'officier d'état civil de l'ambassade ou du consulat.
  - En cas d'empêchement grave, l'officier peut se déplacer au domicile ou à l'hôpital.
  - La convention de Pacs est restituée après l'enregistrement.

**Montants** :
- Le dépôt du dossier en mairie est gratuit.
- Le notaire est payant.
- Aucun coût pour l'enregistrement en mairie ou à l'ambassade/consulat.

**Effets du Pacs** :
- Le Pacs produit ses effets entre les futurs à partir de la date de son enregistrement.
- Pour les tiers, l'information est indiquée sur l'acte de naissance (si né en France) ou sur le registre des Pacs des étrangers nés à l'étranger (si nationalité étrangère).
- La preuve de l'enregistrement peut être apportée par mention sur l'acte de naissance, le récépissé d'enregistrement, le visa figurant sur la convention, ou l'attestation du service central d'état civil (si étranger né à l'étranger).

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 436,
  "plafond_mots": 400,
  "respect_longueur": false
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La section « Avec une ambassade ou un consulat » prête à cette procédure des modalités que le document ne décrit que pour la mairie : « Enregistrement : généralement sur rendez-vous », présence ensemble, déplacement de l'officier « au domicile ou à l'hôpital » ; le titre « Délais » ne correspond à aucun délai du document.
- `presence_elements` :
  - P1 : 1 — Le résumé mentionne les couples de même sexe ou de sexes différents, quelle que soit la nationalité, la mairie ou l'ambassade/consulat, la gratuité et le notaire payant.
  - P2 : 0 — La mairie de résidence commune est citée, mais la variation des démarches selon les communes est absente.
  - P3 : 1 — Les trois conditions, la majorité selon le pays pour un étranger et l'impossibilité de dispense sont reprises.
  - P4 : 0 — L'absence d'obligation de vivre ensemble au moment de la déclaration est omise.
  - P5 : 0 — Le contrat unique, le choix entre convention minimale et personnalisée et le cerfa n°15726 sont absents, même si la langue, les signatures, la formule légale et la séparation des patrimoines figurent.
  - P6 : 0 — La pré-demande en ligne n'est pas mentionnée ; le résumé ne cite que le rendez-vous, la présence et l'empêchement grave.
  - P7 : 0 — La restitution et la convention modificative sont citées, mais l'absence de copie conservée et la seule copie du récépissé en cas de perte manquent.
  - P8 : 1 — Le résumé indique les effets entre partenaires dès l'enregistrement et, pour les tiers, la mention sur l'acte de naissance ou le registre des étrangers.
  - P9 : 1 — Les quatre moyens de preuve sont repris.
- Inventions : Ambassade/consulat : « Enregistrement : généralement sur rendez-vous » (non indiqué pour cette procédure); Ambassade/consulat : « En cas d'empêchement grave, l'officier peut se déplacer au domicile ou à l'hôpital » (non indiqué pour cette procédure); Ambassade/consulat : « Dépôt du dossier : gratuit » et présence obligatoire devant l'officier d'état civil de l'ambassade (modalités transposées de la mairie)
- Confiance : moyenne
