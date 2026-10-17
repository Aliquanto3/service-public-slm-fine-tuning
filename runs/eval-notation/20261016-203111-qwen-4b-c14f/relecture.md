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
Si votre enfant est nouveau dans un établissement, vous devez participer à une réunion d'information dans les jours qui suivent la rentrée scolaire. Des réunions peuvent aussi être organisées au cours de l'année scolaire, notamment pour vous informer sur la situation de la classe, sur une procédure spécifique ou sur les possibilités d'orientation. Si votre enfant est en grande difficulté scolaire, son établissement peut également vous inviter à des réunions pour envisager ensemble des solutions. Si vous rencontrez un problème lié à la pédagogie, adressez-vous au professeur principal de la classe. Si votre problème concerne les absences et les questions de comportement, adressez-vous au conseiller principal d'éducation (CPE). Le chef d'établissement et les enseignants doivent faire le nécessaire pour répondre à vos demandes d'information et de rendez-vous. Toute réponse négative doit présenter les motifs.

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
    false,
    true,
    true,
    true
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

À la suite de la réunion du comité social territorial du 15 octobre, le télétravail sera ouvert aux agents du service urbanisme dont les missions le permettent. Chaque agent pourra télétravailler un jour par semaine, choisi en accord avec son responsable. Les jours de permanence au guichet, le mardi et le jeudi, ne pourront pas être télétravaillés.

Les demandes devront être adressées au service des ressources humaines avant le 13 novembre, au moyen du formulaire joint. Un ordinateur portable et un casque sera remis à chaque agent dont la demande aura été acceptée. Les agents s'engagent à rester joignables pendant les plages fixes, de 9 heures à 12 heures et de 14 heures à 16 heures.

Une période d'adaptation de trois mois est prévue. À l'issue de cette période, un bilan sera fait avec chaque agent afin de vérifier que l'organisation retenue convient à la fois à l'agent et au service.

La direction générale des services

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "corrigees": 7,
  "fautes": 8,
  "fautes_corrigees": [
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
  "mots_modifies_hors_faute": 0,
  "mots_texte": 174,
  "rappel": 0.875,
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
Si vous êtes admis à un concours d'accès à la fonction publique et si vous étiez auparavant dirigeant d'une société ou d'une association à but lucratif, vous pouvez continuer à exercer cette activité de dirigeant pendant 1 an, renouvelable une fois, à partir de votre recrutement dans la fonction publique. Cela s'applique aussi si vous êtes recruté en tant que contractuel dans la fonction publique. Vous devez présenter une déclaration écrite à votre autorité hiérarchique soit à la date de votre nomination en tant que fonctionnaire stagiaire, soit avant la signature de votre contrat. Votre déclaration mentionne la forme et l'objet social de l'entreprise ou de l'association, son secteur et sa branche d'activité. La poursuite de cette activité de dirigeant doit être compatible avec vos obligations de service. Elle ne doit pas porter atteinte au fonctionnement normal, à l'indépendance, à la neutralité du service ou aux principes déontologiques. Cette activité ne doit pas non plus vous placer dans une situation de conflit d'intérêts.

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
    false,
    true,
    true,
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
**Compte rendu du point hebdomadaire de service – Propreté urbaine**

**Objet** : Réunion de suivi des actions de propreté urbaine  
**Date** : Lundi 28 septembre 2026  
**Lieu** : Centre technique municipal (CTM), Ville de Saint-Ambrel-les-Forges  
**Heure** : 7h30 – 8h40  

**Participants** :  
- R. Duquesne (responsable service propreté, animateur)  
- P. Ribeiro (chef d'équipe secteur nord)  
- G. Tessier (chef d'équipe secteur sud)  
- K. Bouaziz (agent de maîtrise, atelier véhicules)  
- Mme Loiseau (adjointe au maire, cadre de vie) – présent de 7h45 à 8h05  

**Absents** :  
- D. Kowalski (chef d'équipe centre-ville) – en formation CACES, remplacement effectué par P. Ribeiro  

---

**Points abordés**  

1. **Dépôts sauvages rue du Moulin-Brûlé**  
   - Troisième dépôt en 15 jours (gravats et électroménager), enlevé jeudi par l'équipe nord avec deux rotations de camion.  
   - Mme Loiseau propose l’installation d’une caméra sur le lieu. Duquesne précise que la vidéoprotection relève de la police municipale et du vote du conseil, pas du service propreté. Aucune décision prise.  
   - Duquesne transmet les photos et le numéro d’un courrier retrouvé dans les gravats à la police municipale pour identification de l’auteur, action menée aujourd’hui.  
   - Proposition d’un article dans le bulletin municipal sur les dépôts sauvages et la déchèterie. Tous les participants sont d’accord sur l’idée, mais aucune personne n’est désignée pour l’organiser. Mme Loiseau quitte la réunion avant qu’un responsable ne soit désigné.  

2. **Balayeuse n°2 en panne**  
   - Problème de pompe hydraulique, pièce commandée, délai fournisseur de 3 semaines.  
   - Décision : location d’une balayeuse de remplacement pour 3 semaines. Devis initial annoncé à 2 400 € HT, corrigé par Bouaziz à 2 040 € HT (sur budget fonctionnement propreté).  
   - Bouaziz réserve la balayeuse de location, livraison au plus tard le jeudi 1er octobre.  

3. **Plan feuilles mortes**  
   - Décision : démarrage du ramassage des feuilles le lundi 12 octobre 2026. Deux agents en renfort pris sur les espaces verts (accord du chef des espaces verts déjà obtenu).  
   - Tessier élaborera le planning des circuits, avec priorité sur les abords des écoles et les pistes cyclables, à présenter au point hebdo du lundi 5 octobre.  
   - Proposition de test du broyage des feuilles pour paillage par Ribeiro. Pas de temps disponible cette année, à revoir en 2027. Aucune décision prise.  

4. **Cimetière / Toussaint**  
   - Décision : nettoyage renforcé des allées et abords du cimetière la semaine du 26 octobre 2026, avant le 1er novembre. Équipe sud chargée.  
   - Tessier coordonne avec le conservateur du cimetière.  

5. **Tags école Jean-Moulin**  
   - Tags signalés sur le mur côté cour, par la directrice, vendredi.  
   - Tessier fait intervenir l’équipe sud avec l’hydrogommeuse avant le vendredi 2 octobre.  

6. **Divers / sécurité**  
   - Ribeiro demande deux agents sans gilets haute visibilité (nouveaux). Duquesne passe la commande d’EPI cette semaine.  
   - Tessier demande de passer aux horaires d’hiver (poste à 7h au lieu de 6h) dès octobre. Duquesne indique que cela nécessite l’avis du CST, pas possible cette année. Aucune modification prévue.  

---

**Décisions prises**  
- Location d’une balayeuse de

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — Point 2 : « location d'une balayeuse de remplacement pour 3 semaines », « corrigé par Bouaziz à 2 040 € HT (sur budget fonctionnement propreté) ».
  - D2 : 1 — Point 3 : « démarrage du ramassage des feuilles le lundi 12 octobre 2026. Deux agents en renfort pris sur les espaces verts ».
  - D3 : 1 — Point 4 : « nettoyage renforcé des allées et abords du cimetière la semaine du 26 octobre 2026, avant le 1er novembre. Équipe sud chargée ».
  - A1 : 1 — Point 1 : Duquesne transmet photos et numéro de courrier à la police municipale, « action menée aujourd'hui » (responsable et échéance présents).
  - A2 : 1 — Point 2 : « Bouaziz réserve la balayeuse de location, livraison au plus tard le jeudi 1er octobre ».
  - A3 : 1 — Point 3 : « Tessier élaborera le planning des circuits [...] à présenter au point hebdo du lundi 5 octobre ».
  - A4 : 1 — Point 4 : « Tessier coordonne avec le conservateur du cimetière » ; aucune échéance n'était fixée dans les notes.
  - A5 : 1 — Point 5 : « Tessier fait intervenir l'équipe sud avec l'hydrogommeuse avant le vendredi 2 octobre ».
  - A6 : 1 — Point 6 : « Duquesne passe la commande d'EPI cette semaine » (responsable et échéance présents, malgré la formulation confuse « Ribeiro demande deux agents sans gilets »).
- `absence_invention` : 1 — Aucun fait absent des notes : caméra, article du bulletin, broyage et horaires d'hiver sont présentés comme non décidés, le montant retenu est 2 040 € HT ; seules des maladresses apparaissent (« chef d'équipe » pour Ribeiro, « présent » pour Mme Loiseau).
- `structure` : 0 — La sortie est tronquée à « Location d'une balayeuse de » : la section Décisions est inachevée et la section Actions est absente.
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
**Compte rendu de la séance de l'équipe pluridisciplinaire RSA**  
**Objet** : Évaluation et décision sur six dossiers de parcours professionnels ou sociaux  
**Participants** : Mme Aubertin (présidente par délégation), M. Faure (France Travail), Mme Nkomo (assistante sociale), M. Gallet (représentant des allocataires), M. Le Goff (Atelier du Pont), Mme Jacquet (secrétariat). Mme Rambert (conseillère en insertion) est excusée.  

**Points abordés** :  
- Réorientation de Mme L. D. vers le parcours professionnel (suivi par France Travail).  
- Réorientation de M. K. A. vers le parcours social (suivi par la MDS).  
- Suspension-remobilisation de 30 % pour M. R. S. (délai de reprise de contact, avis à la majorité, M. Gallet défavorable).  
- Maintien du RSA pour Mme F. M. (justification de l’absence liée à l’hospitalisation de son fils).  
- Maintien du RSA sans réduction pour M. J.-P. V. (justification de mission d’intérim).  
- Report du dossier de Mme N. R. à la prochaine séance en raison de retard de convocation.  

**Décisions prises** :  
- Avis favorable à la réorientation de Mme L. D. vers le parcours professionnel, suivi par France Travail.  
- Avis favorable à la réorientation de M. K. A. vers le parcours social, suivi par la MDS.  
- Suspension-remobilisation de 30 % pour M. R. S. pendant un mois, levée dès reprise de contact.  
- Maintien du RSA sans sanction pour Mme F. M.  
- Maintien du RSA sans réduction pour M. J.-P. V.  
- Report du dossier de Mme N. R. à la prochaine séance.  

**Actions à mener** :  
- M. Faure : transmettre un avis à France Travail pour Mme L. D. (désignation d’un conseiller, premier rendez-vous avant le 16 octobre) ; vérifier le contrat de mission de M. J.-P. V. et mettre à jour le contrat d’engagement avant le 15 octobre.  
- Mme Nkomo : désigner un référent social de la MDS pour M. K. A. dans un délai de un mois (évaluation des charges de travail).  
- Mme Jacquet : transmettre l’ensemble des avis au service RSA pour décision du président d’ici le 25 septembre ; envoyer la convocation à Mme N. R. avant le 30 septembre et la prévenir par téléphone ; indiquer à Mme N. R. qu’elle peut être accompagnée.  
- M. Faure : appeler M. R. S. le vendredi 18 octobre, et en cas de non-réponse, passer par sa sœur.  

**Échéances** :  
- Transmission des avis au service RSA : vendredi 25 septembre.  
- Première rencontre avec Mme L. D. : avant le 16 octobre.  
- Vérification du contrat de mission et mise à jour du contrat d’engagement : avant le 15 octobre.  
- Réunion suivante : jeudi 15 octobre.  

**Points ambigus ou incomplets** :  
- Nature exacte des courriers de convocation (proposition de simplification non traitée).  
- Délai de mise à jour du contrat d’engagement pour M. J.-P. V. (non précisé dans la transcription).  
- Responsable de la mise en place d’un relais pour M. K. A. (non précisé, dépend de la charge de travail de Mme Nkomo).

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « Avis favorable à la réorientation de Mme L. D. vers le parcours professionnel, suivi par France Travail » figure dans le compte rendu.
  - D2 : 1 — « Avis favorable à la réorientation de M. K. A. vers le parcours social, suivi par la MDS » figure dans le compte rendu.
  - D3 : 1 — Le compte rendu indique 30 % pendant un mois, la levée dès la reprise de contact et l'avis à la majorité avec M. Gallet défavorable (dans les Points abordés).
  - D4 : 1 — « Maintien du RSA sans sanction pour Mme F. M. » figure, avec le motif de l'hospitalisation du fils.
  - D5 : 1 — « Maintien du RSA sans réduction pour M. J.-P. V. » figure, avec la mission d'intérim.
  - D6 : 1 — Le report « à la prochaine séance » est mentionné, et la réunion suivante est datée du jeudi 15 octobre dans les Échéances.
  - A1 : 1 — M. Faure est indiqué pour la désignation d'un conseiller, avec un premier rendez-vous avant le 16 octobre.
  - A2 : 1 — Mme Nkomo est indiquée pour la désignation d'un référent social MDS dans un délai d'un mois.
  - A3 : 0.5 — Le responsable et l'action sont présents, mais l'échéance est fausse : « le vendredi 18 octobre » au lieu du vendredi 18 septembre.
  - A4 : 0 — La réinscription éventuelle de Mme F. M. aux ateliers d'octobre par M. Le Goff est absente du compte rendu.
  - A5 : 1 — M. Faure est indiqué pour vérifier le contrat de mission et mettre à jour le contrat d'engagement « avant le 15 octobre ».
  - A6 : 1 — Mme Jacquet est indiquée pour envoyer la convocation avant le 30 septembre et prévenir Mme N. R. par téléphone.
  - A7 : 1 — Mme Jacquet est indiquée pour transmettre les avis au service RSA d'ici le 25 septembre.
- `absence_invention` : 0 — La date « appeler M. R. S. le vendredi 18 octobre » est inventée : la transcription dit demain, soit le vendredi 18 septembre.
- `structure` : 1 — Les sections Participants, Points abordés, Décisions prises et Actions à mener sont présentes.
- Inventions : Appel de M. R. S. fixé au « vendredi 18 octobre » (la transcription indique le vendredi 18 septembre); Affirmation erronée que le délai de mise à jour du contrat d'engagement de M. J.-P. V. n'est « pas précisé dans la transcription » (M. Faure a dit avant le jeudi 15 octobre)
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
**Compte rendu de la réunion publique de concertation**  
**Date :** Jeudi 1er octobre 2026  
**Lieu :** Salle des fêtes de Valbrézac  

**Participants :**  
M. Bernard Lacoste (maire), Mme Isabelle Fauré (1re adjointe à l'urbanisme), M. Didier Roucayrol (adjoint au commerce et à l'artisanat), Mme Anne Teyssier (directrice générale des services), Mme Solène Marquet (paysagiste-urbaniste, cheffe de projet, Atelier Paysage & Territoires), M. Hugo Brissac (ingénieur VRD, Atelier Paysage & Territoires), Mme Lucie Garrigues (conseillère municipale d'opposition), M. Gérard Pons (riverain rue de la République), M. Jean-Marc Cazals (boulanger, président de l'union commerciale Valbrézac Commerces), Mme Odile Vergnes (présidente du club des aînés), M. Kevin Lafarge (association Valbrézac à vélo), Mme Martine Delpech (riveraine de la place de la Halle), Mme Fatima Ould-Ali (parent d'élève, école du Bourg), Mme Sandrine Mathieu (assistante maternelle), M. Lucien Arnal (maraîcher, exposant du marché), et d'autres habitants.

---

**Points abordés :**  
- Présentation du projet « Cœur de bourg » visant à redonner de l’attrait au centre-bourg en améliorant l’accessibilité, la sécurité et la qualité de l’espace public.  
- Diagnostic de l’Atelier Paysage & Territoires :  
  - 6 800 véhicules par jour sur la RD 812, avec 9 % de poids lourds (données 2025).  
  - 112 places de stationnement, 64 sur la place de la Halle.  
  - Trottoirs de la rue de la République souvent inférieurs à 1 mètre, non conformes aux personnes à mobilité réduite.  
  - Sept platanes sur la place, dont trois présentent des signes de faiblesse, sans diagnostic phytosanitaire.  
- Présentation des trois scénarios :  
  - **Scénario A (ambitieux)** : place de la Halle entièrement piétonne, suppression des 64 places, création d’un parking de 30 places derrière la poste, rue de la République en sens unique avec trottoirs élargis à 1,80 m. Coût estimé : 2,4 millions d’euros hors taxes.  
  - **Scénario B (partagé)** : 22 places conservées sur la place de la Halle, le reste devient espace piéton avec terrasses, bancs, plantations, traversée du centre en zone de rencontre (20 km/h, priorité aux piétons), rue de la République à double sens avec trottoirs élargis où possible. Coût estimé : 1,9 million d’euros hors taxes.  
  - **Scénario C (minimal)** : réparation des trottoirs, amélioration des traversées, stationnement conservé. Coût estimé : 900 000 euros hors taxes.  
- Les toilettes publiques sont incluses dans les trois scénarios et seront refaites à neuf.  
- Les platanes ne seront pas abattus sans diagnostic phytosanitaire.  

**Sondage à main levée sur les scénarios A et B :**  
- Environ 25 personnes préfèrent le scénario A.  
- Environ 50 personnes (52) préfèrent le scénario B.  
- Une quinzaine de personnes ne se prononce pas.  
- Le maire précise que ce sondage est indicatif et ne constitue pas une décision. Le choix final sera fait au conseil municipal.

**Proposition d’une variante « B plus » :**  
- Mme Marquet propose une version améliorée du scénario B : place entièrement piétonne le dimanche matin et les jours de fête, avec des bornes amovibles.  
- M. Lacoste demande à Mme Marquet d’étudier cette variante pour la prochaine ré

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 0 — L'éviction du scénario C n'est pas mentionnée. Seul le choix final au conseil est évoqué, à propos du sondage.
  - D2 : 0 — La prolongation de la concertation jusqu'au 13 novembre est absente.
  - D3 : 0 — La balade urbaine du 17 octobre est absente.
  - D4 : 0 — Le maintien du marché sur la place de la Halle n'est pas mentionné.
  - D5 : 0 — La création du comité de suivi est absente.
  - D6 : 0.5 — La sortie indique « Les platanes ne seront pas abattus sans diagnostic phytosanitaire », mais ne mentionne pas la commande du diagnostic des sept platanes.
  - D7 : 0 — Le conseil municipal du 10 décembre n'est pas mentionné.
  - D8 : 0 — La deuxième réunion publique de janvier n'est pas explicitement actée. Seule figure l'allusion tronquée « prochaine ré ».
  - A1 : 0 — La commande du diagnostic par Mme Fauré avant fin octobre est absente.
  - A2 : 0 — L'étude des itinéraires de livraison est absente.
  - A3 : 0 — Le contact avec le propriétaire et l'EPF est absent.
  - A4 : 0 — Le courrier au président du département est absent.
  - A5 : 0 — L'annexion de la pétition au registre est absente.
  - A6 : 0 — La préparation des dossiers de subvention est absente.
  - A7 : 0 — Le comptage du stationnement est absent.
  - A8 : 1 — La sortie indique « M. Lacoste demande à Mme Marquet d'étudier cette variante pour la prochaine ré[union] » : le responsable et l'échéance sont présents, malgré la troncature.
  - A9 : 0 — L'étude de l'espace de jeux est absente.
  - A10 : 0 — L'organisation de la balade urbaine est absente.
  - A11 : 0 — La centralisation des candidatures au comité est absente.
  - A12 : 0 — La mise en ligne de la présentation et du compte rendu est absente.
- `absence_invention` : 1 — Les chiffres (coût du B à 1,9 M€, sondage), les personnes et les faits repris sont conformes à la transcription. Le sondage est bien présenté comme indicatif.
- `structure` : 0 — Le compte rendu est tronqué : les sections Décisions et Actions sont absentes, seules Participants et Points abordés figurent.
- Inventions : aucune
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
**Compte rendu de réunion de chantier n°14 – rénovation du gymnase des Aubiers – Courtenac-sur-Brize**

**Objet de la réunion** : Avancement des travaux, planning, décisions techniques et actions à mener.

**Participants** :  
- Maîtrise d’œuvre (MOE) : Mme Vernhes (architecte mandataire), M. Hamon (conducteur d’opération)  
- Commune (MOA) : M. Paquet (responsable bâtiments, services techniques), Mme Ferrand (adjointe aux sports, présente jusqu’à 10h)  
- Lot 2 gros œuvre : M. Lacombe (Maçonnerie Lacombe)  
- Lot 4 couverture-étanchéité : M. Diaz (Étanch'Ouest)  
- Lot 7 sols sportifs : Mme Duclos (Sols & Sports Duclos)  

**Excusé** : M. Lenoir (CSPS), visite prévue jeudi  
**Absent (non excusé)** : lot 9 électricité, Elec Mérignon → 2e absence consécutive  

---

**Points abordés** :  

1. **Avancement des lots**  
- Lot 2 : reprise dalle salle principale terminée, séchage en cours. Mesure d’humidité prévue le 2/10.  
- Lot 4 : couverture finie, infiltration constatée côté nord après pluie du 24/09. Défaut d’étanchéité en acrotère relevé. M. Diaz reconnaît le défaut, reprise à ses frais, à effectuer avant la prochaine réunion (6/10).  
- Lot 7 : attend la dalle sèche (taux < 3 %) pour pose. Pose prévue en 3 semaines.  
- Lot 9 : chemins de câbles posés à 60 % (constat visuel), aucun planning reçu.  

2. **Planning et réception**  
- Retard cumulé estimé à environ 2 semaines (séchage dalle + lot 9).  
- Proposition de décalage de la réception : initialement annoncée le 20 novembre, corrigée au vendredi 27 novembre 2026.  
- Mme Ferrand valide la proposition de la commune, mais souligne la nécessité de prévenir rapidement les clubs (basket, hand). Elle s’engage à les informer avant le 16/10.  
- Décision MOA : réception reportée au vendredi 27/11/2026 (au lieu du 13/11).  
- Question sur les pénalités de retard pour le lot 9 : M. Paquet demande leur application. Mme Vernhes estime que cela est prématuré, car le planning n’est pas encore défini. Aucune décision prise.  

3. **Travaux supplémentaires**  
- M. Lacombe signale que deux portes coupe-feu (local rangement et chaufferie) ne sont pas conformes au marché. Devis présenté (3 840 € HT).  
- M. Paquet confirme la disponibilité des crédits.  
- Décision MOA : devis accepté. Mme Vernhes émet l’ordre de service avant vendredi 2/10.  
- Proposition de repeinture des murs de la salle principale (option ~11 000 € HT) formulée par M. Lacombe. Mme Ferrand considère que cela serait bénéfique, mais M. Paquet indique l’absence de budget, à étudier pour 2027. Aucune décision prise.  

4. **Choix techniques**  
- Sol sportif : Mme Duclos présente trois nuanciers. Mme Ferrand choisit le bleu (terrain) et le gris clair (hors jeu).  
- Décision : coloris validé bleu / gris clair.  
- Tracés : basket, hand, badminton prévus. Demande de volley formulée par Mme Duclos. Mme Ferrand est incertaine, demande aux clubs de confirmer. En attente.  
- Mme Duclos apporte un échantillon du revêtement à la prochaine réunion.  

5. **Lot 9**  
- M. Hamon prévoit d’envoyer un courrier de mise en demeure à Elec Mérignon

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « Décision MOA : réception reportée au vendredi 27/11/2026 (au lieu du 13/11) », avec la bonne date après correction.
  - D2 : 1 — « Décision MOA : devis accepté » pour les deux portes coupe-feu à 3 840 € HT, avec émission de l'ordre de service.
  - D3 : 1 — « Décision : coloris validé bleu / gris clair ».
  - A1 : 0.5 — « Mesure d'humidité prévue le 2/10 » : l'échéance est donnée, mais M. Lacombe n'est pas nommé comme responsable.
  - A2 : 1 — M. Diaz, reprise à ses frais, « avant la prochaine réunion (6/10) ».
  - A3 : 1 — Mme Ferrand « s'engage à les informer avant le 16/10 ».
  - A4 : 1 — « Mme Vernhes émet l'ordre de service avant vendredi 2/10 ».
  - A5 : 1 — Mme Ferrand « demande aux clubs de confirmer » ; l'échéance n'est pas fixée dans les notes.
  - A6 : 1 — « Mme Duclos apporte un échantillon du revêtement à la prochaine réunion ».
  - A7 : 0.5 — « M. Hamon prévoit d'envoyer un courrier de mise en demeure à Elec Mérignon » : la phrase est tronquée et l'échéance « cette semaine » manque.
  - A8 : 0 — Le point Sécurité (remise en place de la clôture par M. Lacombe) est absent, car la sortie est tronquée.
- `absence_invention` : 1 — Aucune décision, personne, date ou chiffre inventé ; les pièges (date du 20 novembre, pénalités, peinture, volley) sont présentés comme non décidés, malgré de légères reformulations (« valide la proposition de la commune »).
- `structure` : 0 — Seules les sections Participants et Points abordés sont présentes ; les sections Décisions et Actions manquent, car la sortie s'interrompt au point 5.
- Inventions : aucune
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
**Compte rendu de la réunion du comité de pilotage du Contrat local de santé (CLS) 2024-2028 – Pontcarel**

**Objet de la réunion**  
Bilan mi-parcours du CLS et approfondissement des axes clés : accès aux soins, santé mentale, prévention, et proposition d’avenant sur la santé des aînés.

**Participants**  
- M. Desbrosses, maire de Pontcarel (coprésident)  
- Mme Laborde, délégation départementale ARS (coprésidente)  
- M. Ogier, conseiller municipal délégué à la santé  
- Mme Benamar, coordinatrice CLS (ville)  
- Dr Lemaire, président de la CPTS du Haut-Pontcarel (en visio, quitte à 11h)  
- Mme Ricard, CPAM, chargée de mission prévention  
- M. Vasseur, département, service autonomie (représente la directrice enfance-famille-autonomie)  
- Mme Tran, directrice adjointe du centre hospitalier de Pontcarel  
- Mme Haddou, asso Point Écoute Jeunes (invitée pour le point 3)

**Points abordés**  
1. **Bilan mi-parcours**  
   - 18 fiches-actions : 4 terminées, 11 engagées, 3 non démarrées (santé des aidants, habitat indigne).  
   - Points forts : ateliers nutrition QPV Les Coudrais (212 participants depuis 2024), permanences CPAM au CCAS.  
   - Points faibles : axe santé environnement en retard, manque de données.  
   - Le bilan est validé à l’unanimité des membres présents.  

2. **Accès aux soins**  
   - Problème de succession de 2 médecins généralistes (fin 2026), ~2 600 patients sans médecin traitant.  
   - Projet de maison de santé pluriprofessionnelle (MSP) libérale (Dr Lemaire) : 3 jeunes médecins intéressés, mais pas de contrat signé.  
   - Proposition de centre de santé municipal (M. Ogier), modèle inspiré d’une ville voisine.  
   - Débat sur la concurrence entre les deux modèles.  
   - Décision : lancer une étude d’opportunité comparant les deux scénarios (MSP ou centre de santé municipal), coût estimé à 28 000 € TTC.  
   - Financement : ARS peut cofinancer 50 % (jusqu’à 15 000 €) via le FIR, sous réserve de validation par le comité FIR (prochain comité en décembre). Le reste à charge de la ville.  
   - Dossier FIR à préparer par Mme Benamar avec l’appui de l’ARS, dépôt avant le 13 novembre.  
   - Choix entre MSP et centre de santé : non tranché, à attendre l’étude.  
   - Possibilité d’intégrer des consultations avancées de spécialistes (cardio, gynéco) dans la future structure (à confirmer avec l’hôpital).  
   - Campagne M'T dents dans les écoles élémentaires (2 écoles du QPV), renforcement de l’intervention en classe de CP, à organiser par Mme Ricard au 2e trimestre scolaire (janvier-mars 2027).  

3. **Santé mentale**  
   - Augmentation de 35 % des demandes des 15-25 ans au Point Écoute, délais CMP de 4 à 6 mois.  
   - Problème de recrutement de psychologues et pédopsychiatres.  
   - Proposition de formation des agents municipaux et associatifs aux Premiers secours en santé mentale (PSSM).  
   - Décision : 2 sessions PSSM au 1er semestre 2027 (12 stagiaires par session, 24 personnes au total). Financement ARS déjà prévu dans la fiche-action 7 (6 000 €), pas de nouveau financement à demander.  
   - Mme Benamar sollicite des organismes de formation agréés, dates à proposer au prochain COPIL.  
   - Proposition de création d’un conseil local de santé

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « Le bilan est validé à l'unanimité des membres présents » figure au point 1.
  - D2 : 1 — L'étude d'opportunité (28 000 € TTC) et le cofinancement ARS de 50 % dans la limite de 15 000 €, sous réserve du comité FIR, sont mentionnés.
  - D3 : 1 — Les 2 sessions PSSM au 1er semestre 2027 (24 personnes, 6 000 € ARS, fiche-action 7) sont mentionnées.
  - D4 : 0 — La sortie est tronquée au point 3 ; la reconduction des ateliers nutrition en 2027 n'est pas mentionnée.
  - D5 : 0 — La campagne moustique tigre est absente (sortie tronquée).
  - D6 : 0 — L'accord de principe sur l'avenant n°1 est absent (sortie tronquée).
  - A1 : 0 — La note de synthèse pour le conseil municipal du 12 novembre (Benamar, avant le 30 octobre) n'est pas mentionnée.
  - A2 : 1 — « Dossier FIR à préparer par Mme Benamar avec l'appui de l'ARS, dépôt avant le 13 novembre » : responsable et échéance sont présents.
  - A3 : 1 — « À organiser par Mme Ricard au 2e trimestre scolaire (janvier-mars 2027) » : responsable et échéance sont présents.
  - A4 : 1 — « Mme Benamar sollicite des organismes de formation agréés, dates à proposer au prochain COPIL » : responsable et échéance sont présents.
  - A5 : 0 — Le contact avec l'infirmière conseillère technique est absent (sortie tronquée).
  - A6 : 0 — Le pilotage de la campagne moustique tigre par M. Ogier est absent.
  - A7 : 0 — L'état des lieux de la qualité de l'air intérieur dans les écoles est absent.
  - A8 : 0 — La rédaction de la fiche-action de l'avenant (Vasseur et Benamar, avant le 15 janvier 2027) est absente.
  - A9 : 0 — L'envoi du sondage pour fixer la date du prochain COPIL est absent.
  - A10 : 0 — La diffusion du compte rendu sous 15 jours est absente.
- `absence_invention` : 1 — Aucune information absente des notes : le choix MSP / centre de santé est bien présenté comme « non tranché », le FIR comme « sous réserve », et les consultations avancées comme « à confirmer avec l'hôpital ».
- `structure` : 0 — La sortie, tronquée au milieu du point 3 (« Proposition de création d'un conseil local de santé »), ne comporte pas de sections Décisions et Actions.
- Inventions : aucune
- Confiance : haute

**Juge second** : juge

- `presence_elements` :
  - D1 : 1 — La décision D1 est correctement mentionnée dans la section 'Bilan mi-parcours' : 'Le bilan est validé à l’unanimité des membres présents.'
  - D2 : 1 — La décision D2 est correctement mentionnée dans la section 'Accès aux soins' : 'Décision : lancer une étude d’opportunité comparant les deux scénarios (MSP ou centre de santé municipal), coût estimé à 28 000 € TTC.'
  - D3 : 1 — La décision D3 est correctement mentionnée dans la section 'Santé mentale' : 'Décision : 2 sessions PSSM au 1er semestre 2027 (12 stagiaires par session, 24 personnes au total). Financement ARS déjà prévu dans la fiche-action 7 (6 000 €).'
  - D4 : 1 — La décision D4 est partiellement mentionnée dans la section 'Prévention / nutrition / santé environnement' (non explicitement séparée dans la SORTIE) : 'Campagne M'T dents dans les écoles élémentaires [...] à organiser par Mme Ricard au 2e trimestre scolaire (janvier-mars 2027).' Cependant, la reconduction des ateliers nutrition est absente, donc comptée pour moitié.
  - D5 : 0.5 — La décision D5 est partiellement mentionnée : 'campagne d’information des habitants sur le moustique tigre' est évoquée, mais sans précision sur le printemps 2027 ou les modalités (flyers + réunion de quartier).
  - D6 : 1 — La décision D6 est correctement mentionnée dans la section 'Avenant au CLS' (non explicitement séparée dans la SORTIE) : 'Décision : accord de principe pour préparer un avenant n°1 intégrant une fiche-action « prévention des chutes et isolement des personnes âgées ».'
  - A1 : 1 — L'action A1 est correctement mentionnée dans la section 'Bilan mi-parcours' : 'Mme Benamar prépare une note de synthèse pour le conseil municipal du 12 novembre, à transmettre au cabinet du maire avant le 30 octobre.'
  - A2 : 1 — L'action A2 est correctement mentionnée dans la section 'Accès aux soins' : 'Dossier FIR à préparer par Mme Benamar avec l’appui de l’ARS, dépôt avant le 13 novembre.'
  - A3 : 1 — L'action A3 est correctement mentionnée dans la section 'Accès aux soins' : 'Campagne M'T dents [...] à organiser par Mme Ricard au 2e trimestre scolaire (janvier-mars 2027).'
  - A4 : 1 — L'action A4 est correctement mentionnée dans la section 'Santé mentale' : 'Mme Benamar sollicite des organismes de formation agréés, dates à proposer au prochain COPIL.'
  - A5 : 0.5 — L'action A5 est partiellement mentionnée : 'Prendre contact avec l'infirmière conseillère technique' est évoqué dans l'ENTRÉE, mais absent de la SORTIE. Seule la contribution écrite de l'Éducation nationale est citée sans lien avec les ateliers nutrition.
  - A6 : 0.5 — L'action A6 est partiellement mentionnée : 'campagne d’information des habitants sur le moustique tigre' est évoquée, mais sans précision sur le pilotage par M. Ogier ou la présentation au COPIL de mars 2027.
  - A7 : 0 — L'action A7 est absente de la SORTIE : 'Demander aux services techniques un état des lieux de la surveillance de la qualité de l'air intérieur dans les écoles' n'est pas mentionné.
  - A8 : 1 — L'action A8 est correctement mentionnée dans la section 'Avenant au CLS' : 'Rédiger la fiche-action de l’avenant n°1 et l’envoyer aux membres avant le 15 janvier 2027.'
  - A9 : 0 — L'action A9 est absente de la SORTIE : 'Envoyer le sondage pour fixer la date du prochain COPIL' n'est pas mentionné.
  - A10 : 1 — L'action A10 est correctement mentionnée dans la section 'Divers' (non explicitement séparée) : 'Compte rendu diffusé à tous par Mme Benamar sous 15 jours.'
- `absence_invention` : 0 — Invention détectée : la SORTIE mentionne 'Décision : accord de principe pour préparer un avenant n°1' sans préciser que l'adoption formelle est reportée au prochain COPIL (piège). De plus, la 'création d’un conseil local de santé mentale' est présentée comme une proposition en cours, alors qu'elle est explicitement non décidée (piège).
- `structure` : 1 — Les quatre sections requises (Participants, Points abordés, Décisions, Actions) sont présentes, bien que les sections 'Décisions' et 'Actions' ne soient pas explicitement séparées.
- Inventions : L'adoption formelle de l'avenant n°1 est présentée comme en cours, alors qu'elle est reportée au prochain COPIL (piège).; La proposition de conseil local de santé mentale est mentionnée sans préciser qu'elle est non décidée (piège).
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
**Compte rendu de la réunion de gestion annuelle du CPOM – 2024-2028**  
**Date :** 29 septembre 2026  
**Lieu :** Hôtel du Département, salle 3  

---

**Participants :**  
- Côté département : Mme Massard (directrice de l'autonomie), M. Tavernier (chef du service tarification et contrôle), Mme Gaudry (chargée de tarification)  
- Côté association : M. Peyrac (président), Mme Roux-Delattre (directrice), M. Kerbrat (responsable administratif et financier)  

---

**Points abordés :**  
1. **Indicateurs du CPOM (2025)**  
   - Heures réalisées : 148 300 (objectif initial : 155 000)  
   - Répartition : 112 000 heures APA, 21 500 heures PCH, 14 800 heures pour les caisses de retraite et mutuelles  
   - Taux de rotation du personnel : 28 % (objectif : sous 20 %)  
   - Délai moyen de démarrage d’intervention : 11 jours (objectif : 7 jours)  
   - Heures notifiées non réalisées : 6 %  
   - Réclamations écrites : 37 (22 sur des changements d’intervenant non prévenus)  

2. **Revue de l’objectif d’heures**  
   - L’association demande une révision de l’objectif de 155 000 heures en raison de la perte de 14 intervenantes.  
   - Proposition d’objectif de 145 000 heures.  
   - Décision : l’objectif est fixé à 150 000 heures par an pour 2026 et 2027, en lien avec le rythme actuel.  

3. **Délai de démarrage d’intervention**  
   - Le délai de 11 jours est calculé à partir de la décision du plan d’aide, mais la notification arrive parfois 5 à 6 jours plus tard.  
   - Décision : l’objectif de 7 jours est maintenu, mais calculé à partir de la réception de la notification par le service.  
   - Mme Gaudry envoie la procédure de raccordement à la notification dématérialisée.  
   - M. Kerbrat effectue un calcul du délai pour le premier semestre 2026 sur cette base, à envoyer avant fin octobre.  

4. **Taux de rotation et déplacements**  
   - Le taux de rotation de 28 % est considéré comme préoccupant.  
   - L’association mentionne le tutorat mis en place en mars, mais les résultats sont encore préliminaires.  
   - Les déplacements dans les communes de Saint-Fulbert et Les Granges-Hautes sont très longs (40 minutes de route pour une heure d’intervention).  
   - Rejet du retrait de ces communes : le CPOM engage sur la zone d’intervention, et l’association est le seul service présent.  
   - Étude d’une majoration pour les zones rurales proposée par M. Tavernier, sans date de réponse.  

5. **Suivi des indicateurs**  
   - Suivi trimestriel du taux de rotation et des heures non réalisées mis en place.  
   - Le premier rapport trimestriel doit être envoyé avant le 15 janvier 2027, couvrant le quatrième trimestre 2026.  

6. **Situation financière**  
   - Déficit de 84 000 euros en 2025, principalement lié aux revalorisations salariales et aux frais kilométriques.  
   - Refus de la reprise du déficit par le département.  
   - Demande d’un plan de retour à l’équilibre chiffré pour 2027 et 2028.  
   - Délai : le plan doit être envoyé avant le 16 novembre 2026.  

7. **Tarif 2027**  
   - Tarif actuel : 25,40 euros de l’heure.  
   - Besoin de 27,10 euros pour cou

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `presence_elements` :
  - D1 : 1 — « l'objectif est fixé à 150 000 heures par an pour 2026 et 2027 ».
  - D2 : 1 — « l'objectif de 7 jours est maintenu, mais calculé à partir de la réception de la notification par le service ».
  - D3 : 1 — « Rejet du retrait de ces communes » (Saint-Fulbert et Les Granges-Hautes).
  - D4 : 1 — « Suivi trimestriel du taux de rotation et des heures non réalisées mis en place ».
  - D5 : 1 — « Refus de la reprise du déficit par le département », avec un déficit de 84 000 € correct.
  - D6 : 1 — Plan de retour à l'équilibre chiffré 2027-2028 « avant le 16 novembre 2026 ».
  - D7 : 0 — Sortie tronquée au point Tarif 2027 : l'avenant n° 2 et la dotation de 3 €/h sont absents.
  - D8 : 0 — Le cofinancement des 4 véhicules est absent (sortie tronquée).
  - A1 : 0.5 — « Mme Gaudry envoie la procédure de raccordement » : l'échéance « cette semaine » est omise.
  - A2 : 1 — Action attribuée à M. Kerbrat, « à envoyer avant fin octobre ».
  - A3 : 1 — Étude de la majoration par M. Tavernier, « sans date de réponse ».
  - A4 : 0.5 — Premier rapport « avant le 15 janvier 2027 », mais le responsable (Mme Roux-Delattre) n'est pas indiqué.
  - A5 : 0.5 — Plan à envoyer avant le 16 novembre, sans responsable (Mme Roux-Delattre et M. Kerbrat).
  - A6 : 0 — Le projet d'avenant à rédiger par M. Tavernier est absent.
  - A7 : 0 — L'inscription à la commission permanente du 7 décembre est absente.
  - A8 : 0 — L'approbation par le CA de l'association est absente.
  - A9 : 0 — Les devis des véhicules sont absents.
  - A10 : 0 — Les dates de la revue intermédiaire sont absentes.
  - A11 : 0 — L'envoi du relevé de conclusions sous huit jours est absent.
- `absence_invention` : 1 — Aucun chiffre, aucune date ni aucune décision n'est inventé ; les pièges présents (145 000 h, déficit de 84 000 €, retrait des communes) sont correctement traités, et la seule imprécision est d'attribuer à M. Tavernier la proposition de majoration, faite en réalité par Mme Massard.
- `structure` : 0 — Les sections Décisions et Actions manquent : la sortie s'interrompt au point 7 (« pour cou »).
- Inventions : aucune
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
[Adresse du demandeur]  
[Commune]  
[Date du courrier]  

À l'attention du [Nom et qualité du signataire]  
Centre communal d'action sociale (CCAS)  
[Adresse, téléphone et courriel du CCAS]  

Objet : Demande d’aide exceptionnelle au paiement d’une facture d’énergie – pièces manquantes  

Madame, Monsieur,  

Je vous écris en qualité de demandeur de l’aide exceptionnelle au paiement d’une facture d’énergie, dans le cadre de la procédure prévue par l’article L. 114-5 du code des relations entre le public et l’administration.  

Le 30 septembre 2026, j’ai déposé ma demande auprès de votre service. Un accusé de réception a été envoyé le 2 octobre 2026, confirmant la réception de mon dossier.  

Conformément aux dispositions du même article, je vous demande de me fournir les pièces suivantes afin de permettre le traitement de ma demande :  
- une copie de la facture d’énergie concernée ;  
- les justificatifs des ressources du foyer pour les trois derniers mois.  

Le délai de réponse prévu par votre service est de quinze jours à compter de la réception de ce courrier.  

Je tiens à préciser que, selon le régime du silence établi par votre service, le silence gardé pendant deux mois sur la demande vaut décision de rejet.  

Je reste à votre disposition pour tout complément d’information ou pour toute clarification nécessaire.  

Veuillez agréer, Madame, Monsieur, l’expression de mes salutations distinguées.  

M. Julien Petitjean  
Demandeur de l’aide exceptionnelle au paiement d’une facture d’énergie  
Référence du dossier : [Référence du dossier]

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

- `conformite` : 0 — La lettre est rédigée à l'envers, du demandeur vers le CCAS (« Je vous écris en qualité de demandeur… je vous demande de me fournir les pièces suivantes »), ce qui rend le registre et l'énonciation inadaptés. Plusieurs éléments obligatoires manquent : l'en-tête du CCAS, le bloc destinataire M. Julien Petitjean, la formule d'appel « Monsieur, » (remplacée par « Madame, Monsieur, »), la mention de la suspension du délai de rejet implicite et celle de la fin de cette suspension à la production des pièces, ainsi que la signature par le nom et la qualité du signataire du CCAS (signature « M. Julien Petitjean »).
- Inventions : Inversion de l'expéditeur et du destinataire : la lettre est présentée comme émanant de M. Julien Petitjean et adressée au CCAS, ce qui ne figure ni dans l'entrée ni dans les références.; « À l'attention du [Nom et qualité du signataire] » : l'emplacement du signataire est détourné en destinataire.; « Le délai de réponse prévu par votre service » : le délai de 15 jours pour fournir les pièces est requalifié en délai de réponse du service.
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

À l'attention de Mme Élodie Garcia  
[Adresse de la candidate]  
[Commune]

Objet : Convocation à un entretien de recrutement

Madame Mme Élodie Garcia,

Vous êtes conviée à un entretien de recrutement pour le poste d’agent d’accueil et d’état civil (catégorie C), à temps complet, dans le cadre du recrutement du service des ressources humaines.

L’entretien aura lieu le mardi 3 novembre 2026, à 14 h 30, dans la salle du conseil, hôtel de ville.

Le jury composé du directeur général des services et de la responsable des ressources humaines vous recevra pour une durée d’environ 30 minutes.

Vous êtes priés de vous présenter avec les documents suivants :  
- une pièce d’identité  
- une copie des diplômes

Veuillez confirmer votre présence avant le 28 octobre 2026, par courrier ou par téléphone au [Téléphone et courriel du service des ressources humaines].

Toute absence non justifiée entraînera l’annulation de votre candidature.

Nous vous remercions de votre collaboration et vous prions de bien vouloir agréer, Madame, l’expression de nos salutations distinguées.

[Nom et qualité du signataire]  
Service des ressources humaines  
[Adresse de l'hôtel de ville]

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

- `conformite` : 0 — Plusieurs éléments obligatoires manquent ou sont défaillants : l'en-tête de l'expéditeur est absent en haut du courrier (le service n'apparaît qu'au bloc signature), le lieu manque dans « Lieu et date » (seul « [Date du courrier] » figure), et la formule d'appel « Madame Mme Élodie Garcia, » ne respecte pas « Madame, » ; de plus, l'objet omet la mention du poste.
- Inventions : Toute absence non justifiée entraînera l'annulation de votre candidature.; par courrier (mode de confirmation non fourni dans l'entrée)
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

À l'attention de Mme Sandrine Morel,  
Secrétaire de l’association « Vivre au village »  

Objet : Communication des procès-verbaux et du budget de la commune  

Madame,  

Votre demande relative à l’obtention des procès-verbaux des séances du conseil municipal de 2025 et du budget primitif 2026, ainsi que à leur publication dans la lettre d’information de l’association, est bien reçue.  

Conformément à l’article L. 2121-26 du code général des collectivités territoriales, les procès-verbaux des séances du conseil municipal et les documents financiers, y compris le budget primitif, sont accessibles aux associations, sur demande, dans les conditions suivantes :  

Les documents peuvent être consultés sur place au secrétariat général, au [Horaires d'ouverture du secrétariat général], ou envoyés par courrier ou en échange d’une demande écrite accompagnée d’un justificatif d’inscription de l’association auprès de la mairie.  

Concernant la publication des documents dans la lettre d’information de l’association, il convient de noter que, selon les dispositions de l’article L. 2121-26, les documents administratifs et financiers peuvent être reproduits et diffusés par les associations, sous réserve de ne pas en faire une utilisation commerciale ou de diffuser des informations sensibles ou confidentielles. Ainsi, la publication des procès-verbaux et du budget primitif dans votre publication est autorisée, à condition que les documents soient reproduits fidèlement et que l’origine du document soit clairement indiquée.  

Pour obtenir une copie des documents, veuillez nous envoyer une demande écrite, accompagnée de votre nom, de l’adresse de l’association [Adresse de l'association], de la commune [Commune], et de la mention de la publication prévue dans la lettre d’information.  

Vous pouvez contacter le secrétariat général au [Téléphone et courriel du secrétariat général] pour toute information complémentaire.  

Veuillez agréer, Madame, l’expression de nos salutations distinguées.  

[Nom et qualité du signataire]  
Secrétariat général de la mairie

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
    "[Horaires d'ouverture du secrétariat général]": true,
    "[Nom et qualité du signataire]": true,
    "[Téléphone et courriel du secrétariat général]": true
  },
  "emplacements_reussis": true
}
```

### Verdicts

**Juge principal** : juge

- `conformite` : 0 — Plusieurs éléments obligatoires manquent : l'en-tête de l'expéditeur, le lieu (seul « [Date du courrier] » figure), le droit de « toute personne physique ou morale » (réduit aux « associations », sans délibérations, comptes ni arrêtés) et la communication auprès des services déconcentrés de l'État ; la publication « sous sa responsabilité » est remplacée par des conditions et restrictions inventées.
- Inventions : « accompagnée d'un justificatif d'inscription de l'association auprès de la mairie » : condition de communication non prévue par l'article; « sous réserve de ne pas en faire une utilisation commerciale ou de diffuser des informations sensibles ou confidentielles » : restriction non prévue par l'article; « à condition que les documents soient reproduits fidèlement et que l'origine du document soit clairement indiquée » : condition inventée; « la mention de la publication prévue dans la lettre d'information » exigée dans la demande écrite : exigence inventée; « envoyés par courrier ou en échange d'une demande écrite » : formulation qui déforme les modalités locales fournies; Attribution à l'article L. 2121-26 de restrictions de diffusion qu'il ne contient pas
- Confiance : haute

**Juge second** : juge

- `conformite` : 2 — Tous les éléments obligatoires sont présents et le format administratif français est respecté (expéditeur, destinataire, objet, références légales, rappel de la demande, modalités locales, formule d'appel, corps, formule de politesse, signature). Les emplacements sont correctement laissés vides avec les libellés exacts.
- Inventions : La mention 'en échange d’une demande écrite accompagnée d’un justificatif d’inscription de l’association auprès de la mairie' est une invention, car non prévue par l'article L. 2121-26 ni mentionnée dans les références.; La précision sur l'interdiction d'utilisation commerciale ou de diffusion d'informations sensibles/confidentielles est une interprétation non vérifiable dans les références fournies.
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
Non, vous ne pouvez pas avoir le RSA si vous êtes étudiant.

Mais vous pouvez demander le RSA dans deux cas précis :

1. **Vous êtes jeune actif** et avez entre 18 et 25 ans.  
   Pour cela, vous devez avoir travaillé au moins 2 ans à temps plein (soit au moins 3 214 heures) dans les 3 ans précédant votre demande.

2. **Vous êtes parent isolé** : c’est-à-dire que vous vivez seul(e) avec un ou plusieurs enfants à charge.

Vous devez aussi vivre en France de façon stable et effective, au moins 9 mois par an.  
Le montant du RSA dépend de votre situation familiale : il y a un plafond de ressources que vous ne pouvez pas dépasser.

Un simulateur en ligne vous permet de savoir si vous avez droit au RSA et d’estimer le montant que vous pourriez recevoir.  
⚠️ *Attention : si vous recevez déjà l’allocation chômage d’aide au retour à l’emploi (ARE), le montant du RSA sera plus faible.*

---

*Note : Ce passage contient un terme juridique obligatoire ("allocation chômage d’aide au retour à l’emploi" ou ARE), qui ne peut être remplacé sans perte d’information.*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 5.2089,
  "km_entree": 77.32,
  "km_sortie": 82.5289
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La condition de ressources est déformée : « Le montant du RSA dépend de votre situation familiale » remplace « un plafond qui dépend de la composition de votre foyer ». De plus, « simulateur en ligne » ajoute une information absente de l'entrée, et « 9 mois par an » perd la précision « par année civile ».
- `termes_juridiques` : 1 — Les termes RSA, jeune actif, parent isolé, enfants à charge et allocation chômage d'aide au retour à l'emploi (ARE) sont tous conservés.
- `clarte_percue` : 4 — La structure en liste numérotée et les phrases courtes rendent le texte facile à suivre, mais la phrase sur le plafond de ressources est confuse et la note finale méta-textuelle peut dérouter l'usager.
- Inventions : « Un simulateur en ligne » : le caractère en ligne n'est pas mentionné dans l'entrée; « Le montant du RSA dépend de votre situation familiale » : l'entrée dit que c'est le plafond de ressources qui dépend de la composition du foyer
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
Voici le coût de votre convention de Pacs selon la manière dont vous la rédigez :

🔹 Si vous rédigez le pacte seul avec votre partenaire :  
Aucun frais n’est à payer.

🔹 Si vous faites appel à un notaire :  
Le notaire vous facture 101,41 € TTC pour écrire votre convention de Pacs (ou la modifier). Ce montant est le même pour la création ou la modification du pacte.

En plus de cela, il faut payer un droit d’enregistrement de 125 €.  
Des frais supplémentaires peuvent arriver, par exemple pour des copies notariées ou pour inscrire les informations dans les actes d’état civil.  
Ces frais sont fixés par le tarif des notaires.

⚠️ Remarque : Ce texte contient des termes juridiques comme « droit d’enregistrement » ou « tarif des notaires », qui sont obligatoires dans le cadre juridique. Ils sont présents ici pour respecter la précision du texte d’origine.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 7.9464,
  "km_entree": 71.12,
  "km_sortie": 79.0664
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 1 — Les montants (101,41 € TTC, 125 €), la gratuité sans notaire, le coût identique pour une modification et le tarif des notaires sont conservés. En revanche, des nuances sont perdues sans conséquence pratique : « montant fixe » devient « droit d'enregistrement de 125 € », « futur partenaire » devient « votre partenaire » et « des partenaires » disparaît après « actes d'état civil ». La remarque finale ajoute aussi une affirmation invérifiable sur le caractère « obligatoire » de ces termes.
- `termes_juridiques` : 0 — Le terme « émoluments de formalités » est supprimé et remplacé par « frais supplémentaires » sans être cité ni expliqué.
- `clarte_percue` : 4 — Le texte est bien structuré et simple, mais il comporte une redondance (« (ou la modifier). Ce montant est le même pour la création ou la modification ») et une remarque finale sur les termes juridiques qui n'aide pas l'usager.
- Inventions : « qui sont obligatoires dans le cadre juridique » : affirmation absente de l'entrée et des références
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
**Est-ce que je dois déclarer la perte ou le vol de mon livret de famille ?**

Non, ce n’est pas obligatoire. Mais pour éviter les risques de fraude, on vous conseille fortement de faire une déclaration au commissariat de police ou à la brigade de gendarmerie. Vous recevrez un récépissé à la fin de la démarche.

**Quels documents dois-je fournir si je veux obtenir un second livret de famille ?**

Si vous êtes les parents :

- Une preuve de votre identité (par exemple, votre carte d’identité ou votre passeport)
- Une preuve de domicile (comme un titre de propriété, un avis d’imposition, une quittance de loyer, une facture de gaz, d’électricité ou de téléphone)

Et aussi :

- Les informations des personnes concernées (nom, prénom, date et lieu de naissance)
- Si vous êtes mariés, la date et le lieu de votre mariage

**Et si je suis tuteur d’un mineur ?**

Alors, il faut ajouter deux documents :

- Une décision de justice qui prouve que vous êtes le tuteur
- L’acte de naissance du mineur

Dans ce cas, le second livret est fait en reconstituant les actes. Il est établi par la mairie, qui conserve l’acte de mariage (pour les couples mariés) ou l’acte de naissance du premier enfant (pour les parents naturels). Tous les officiers de l’état civil qui ont un acte concerné peuvent compléter le livret. Une mention « second livret » est inscrite sur la première page.

Si votre premier livret est endommagé, il peut être remplacé. Vous devez le présenter à la mairie pour obtenir une copie (duplicata).  
**À savoir** : Si vous échangez votre premier livret contre un second, il doit être remis à l’officier pour être détruit. Mais si vous voulez garder le premier livret, il peut rester, à condition qu’une mention « annulé » soit ajoutée sur chaque page.

**Combien de temps dure la procédure ?**

Le délai dépend du nombre d’actes à inscrire. En général, cela prend quelques semaines.

**Où puis-je récupérer mon second livret ?**

Vous pouvez le récupérer à la mairie où vous avez fait votre demande, en présentant une pièce d’identité.

**Est-ce que la demande de second livret est gratuite ?**

Oui, la délivrance d’un second livret de famille est gratuite.

---

*Note : Ce passage contient des termes juridiques comme "tuteur", "décision de justice", "reconstitution", "duplicata" ou "annulé", qui sont obligatoires dans le cadre juridique. Ils sont conservés car ils sont essentiels à la compréhension du processus, mais leur sens est expliqué dans le texte.*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 10.0447,
  "km_entree": 66.64,
  "km_sortie": 76.6847
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie ajoute des informations absentes de la source (« par exemple, votre carte d'identité ou votre passeport »), affaiblit une obligation (« peuvent compléter le livret » au lieu de « est complété par tous les officiers ») et supprime des éléments : la précision « mairie du lieu de votre domicile » pour le retrait, ainsi que le certificat de non-imposition et la quittance d'assurance du logement.
- `termes_juridiques` : 1 — Les termes livret de famille, récépissé, tuteur, décision de justice, officiers de l'état civil et duplicata sont conservés ; reconstitution apparaît sous la forme verbale « en reconstituant les actes », sans remplacement erroné.
- `clarte_percue` : 4 — Le découpage en questions-réponses et les phrases courtes rendent le texte facile à suivre, mais « récépissé » et « parents naturels » ne sont pas expliqués, malgré ce qu'affirme la note finale.
- Inventions : « par exemple, votre carte d'identité ou votre passeport » : exemples de justificatifs d'identité absents de la source; « peuvent compléter le livret » : obligation transformée en simple possibilité; « Vous recevrez un récépissé à la fin de la démarche » : précision temporelle non présente dans la source; Note finale affirmant que le sens des termes juridiques est expliqué dans le texte, ce qui n'est pas vérifiable pour la plupart d'entre eux
- Confiance : haute

**Juge second** : juge

- `fidelite` : 2 — Toutes les informations_a_conserver sont présentes et exactes, sans ajout ni suppression. Les détails comme la mention 'second livret', les pièces à fournir, ou la gratuité sont fidèlement restitués.
- `termes_juridiques` : 1 — Tous les termes_juridiques_a_conserver sont conservés et leur sens est préservé, sans remplacement inapproprié. Certains sont accompagnés d'explications contextuelles (ex: 'reconstitution' ou 'duplicata').
- `clarte_percue` : 5 — La structure en questions-réponses, les phrases courtes, et le vocabulaire accessible permettent une compréhension immédiate par un usager sans connaissance administrative.
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
Oui, vous pouvez obtenir de l’aide pour payer la cantine de votre enfant, mais cela dépend de son niveau de scolarisation : primaire (maternelle ou élémentaire), collège ou lycée.

**Pour les enfants en primaire :**  
Les tarifs de la cantine sont fixés par votre commune (village ou ville). Certaines communes appliquent le **quotient familial** (un calcul basé sur vos revenus et vos charges) pour adapter le prix du repas à votre situation. Cela peut faire baisser le montant à payer.  
Vous pouvez demander de l’aide en contactant votre mairie ou l’**assistante sociale scolaire** (personne qui aide les familles dans les questions scolaires et sociales).

**Si votre enfant est en école élémentaire éloignée de chez vous et qu’il doit rester à la cantine :**  
Dans certains départements, vous pouvez bénéficier d’une aide. Il faut en parler au **directeur de l’école** au début de l’année scolaire.

**Pour les enfants en collège ou en lycée :**  
Il existe un **fonds social pour les cantines**. C’est une aide financière que l’école peut vous donner pour payer la cantine.  
Pour demander cette aide, vous devez vous adresser à l’**assistante sociale de l’école** ou au **secrétariat de l’établissement scolaire**.  
Le chef d’école (le responsable de l’école) décide si vous pouvez bénéficier de cette aide. Il vous informe en début d’année scolaire des conditions.

**Les tarifs de la cantine en collège ou lycée :**  
Ils sont fixés par le **département** (pour les collèges) ou la **région** (pour les lycées).  
Dans certains cas, le département ou la région applique le **quotient familial** pour adapter le prix à votre situation financière.  
Dans certains départements ou régions, des aides supplémentaires peuvent être disponibles.  
Pour savoir si vous en bénéficiez, contactez votre **collectivité** (ville, département ou région).

---

*Note : Ce texte a été réécrit pour être clair et direct. Certains termes techniques comme "quotient familial" ou "collectivité" sont présents car ils sont obligatoires dans le cadre juridique. Leur sens est expliqué dans le texte.*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 6.7088,
  "km_entree": 65.57,
  "km_sortie": 72.2788
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie ajoute des informations absentes de l'entrée : « Cela peut faire baisser le montant à payer » et « collectivité (ville, département ou région) », la ville n'étant pas compétente pour le collège ou le lycée ; elle supprime aussi la condition « sous certaines conditions » et le fait que seules « certaines communes » accordent des aides.
- `termes_juridiques` : 0 — « chef d'établissement » est remplacé à tort par « Le chef d'école (le responsable de l'école) », et l'« assistante sociale du collège ou du lycée » devient l'« assistante sociale de l'école ».
- `clarte_percue` : 4 — Le texte est bien structuré, avec des explications simples des termes, mais la confusion entre école et établissement, ainsi que la note finale méta, peuvent gêner l'usager.
- Inventions : Cela peut faire baisser le montant à payer.; collectivité (ville, département ou région); Certains termes techniques comme "quotient familial" ou "collectivité" sont présents car ils sont obligatoires dans le cadre juridique.; une aide financière que l'école peut vous donner
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
**Article L131-1 – Langage clair :**

Pour demander de l’aide sociale (sauf pour l’aide à l’enfance), tu dois déposer ta demande soit au centre communal ou intercommunal d’action sociale, soit, si ce centre n’existe pas, à la mairie de ton lieu de résidence.

Le centre communal ou intercommunal d’action sociale prend en charge ton dossier. Il peut envoyer des personnes chargées d’aller te voir pour faire une enquête.

Dans les 30 jours suivant le dépôt de ta demande, ce centre transmet ton dossier au représentant de l’État ou au président du conseil départemental. Ce dernier examine ta demande, en tenant compte de l’avis du centre d’action sociale ou, s’il n’y a pas de centre, de ton maire et du conseil municipal, si tu as demandé qu’ils participent à l’examen.

➡️ *Terme juridique non simplifié : "représentant de l'État" – ce terme désigne une personne désignée par l’État pour représenter ses intérêts dans les décisions locales.*

---

**Article L264-1 – Langage clair :**

Si tu n’as pas de domicile stable, pour exercer certains droits (comme avoir un titre d’identité, voter, accéder à l’aide juridictionnelle ou bénéficier d’une prestation sociale), tu dois choisir un domicile officiel. Ce domicile peut être :

- un centre communal ou intercommunal d’action sociale,  
- ou un organisme agréé (c’est-à-dire un service autorisé à t’accompagner).

L’organisme qui t’attribue une prestation sociale (comme l’allocation d’autonomie, la prestation de compensation du handicap ou le revenu de solidarité active) est celui qui est compétent dans la commune où tu as choisi de vivre.

➡️ *Terme juridique non simplifié : "ressort duquel" – cela signifie la zone géographique ou administrative où une personne est considérée comme habitante, pour les questions de compétence administrative.*  
➡️ *Terme juridique non simplifié : "allocation personnalisée d'autonomie", "prestation de compensation du handicap", "revenu de solidarité active" – ces termes désignent des aides financières spécifiques prévues par la loi.*

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 4.1619,
  "km_entree": 48.65,
  "km_sortie": 52.8119
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Plusieurs conditions et obligations sont modifiées ou supprimées. La consultation du conseil municipal est attribuée à l'usager (« si tu as demandé qu'ils participent à l'examen ») alors que le texte la réserve au maire ou au CCAS. La compétence est rattachée à « la commune où tu as choisi de vivre » au lieu du lieu d'élection de domicile. Enfin, la réserve de l'article L. 252-1, les droits civils et la règle du département débiteur de l'Apa, de la PCH et du RSA ont disparu.
- `termes_juridiques` : 0 — Plusieurs termes à conserver sont remplacés ou absents. « Élire domicile » devient « choisir un domicile officiel » et « visiteurs-enquêteurs » devient « des personnes chargées d'aller te voir ». « Demandes d'admission » et « département débiteur » n'apparaissent pas.
- `clarte_percue` : 4 — Le texte est simple, adressé directement à l'usager et bien structuré, mais certaines formulations erronées peuvent induire l'usager en erreur.
- Inventions : Consultation du conseil municipal « si tu as demandé qu'ils participent à l'examen » : condition attribuée à l'usager, non présente dans le texte; Compétence fixée par « la commune où tu as choisi de vivre » : le texte vise le lieu d'élection de domicile, pas le lieu de vie; « Il peut envoyer des personnes chargées d'aller te voir » : la visite à l'usager n'est pas précisée dans le texte; Définition du représentant de l'État comme « personne désignée par l'État pour représenter ses intérêts dans les décisions locales » : non vérifiable dans l'entrée ni dans les références; « Ressort duquel » est présenté comme terme non simplifié alors qu'il ne figure pas dans la sortie, et sa définition comme zone « où une personne est considérée comme habitante » n'est pas vérifiable
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
Voici le texte réécrit en langage clair et simple, adapté à un usager :

---

**Quand un marché public est conclu, le pouvoir adjudicateur (c’est-à-dire l’entreprise ou l’organisme qui achète) doit payer les sommes dues au créancier (le fournisseur ou le prestataire) dans un délai précis.**

Ce délai est soit :
- **Prévu dans le marché** (c’est-à-dire écrit dans le contrat),
- **Ou fixé par la réglementation** (c’est-à-dire par une règle officielle).

👉 **Important** : Si le marché prévoit un délai de paiement, ce délai **ne peut pas dépasser** celui fixé par la réglementation.

**Délai de paiement standard**  
Pour la plupart des pouvoirs adjudicateurs (comme les services publics ou les entreprises publiques), le délai de paiement est de **30 jours** à compter de la date d’échéance prévue dans le marché.

**Exceptions**  
Dans certains cas, le délai peut être plus long :
- **50 jours** pour les établissements publics de santé (comme les hôpitaux) et les établissements du service de santé des armées.
- **60 jours** pour certaines entreprises publiques (celles qui sont classées comme telles selon une loi du 7 juin 2004), **sauf** si elles sont des établissements publics locaux (comme une mairie ou une commune).

👉 *Ce point est important : le terme "entreprise publique" est défini par une loi (ordonnance n° 2004-503 du 7 juin 2004). Ce terme est technique et ne peut pas être simplifié sans perdre de précision.*

---

**Quand le paiement est en retard**  
Le retard de paiement survient **lorsque le pouvoir adjudicateur ne paie pas** les sommes dues **à l’échéance prévue dans le marché ou dans le délai réglementaire**.

👉 *Ce terme juridique "retard de paiement" est obligatoire dans le cadre du droit public et ne peut être simplifié sans perte de sens.*

---

**Conséquences du retard de paiement**  
À partir du **jour suivant** l’échéance ou la fin du délai de paiement, **des intérêts moratoires** (c’est-à-dire des intérêts pour retard) **commencent automatiquement**.  
Ce taux est fixé par la réglementation (pas par le marché).

En plus de ces intérêts, le pouvoir adjudicateur doit :
- **Verser une indemnité forfaitaire** (un montant fixe, prévu par la réglementation) pour couvrir les frais de recouvrement (c’est-à-dire les frais de demander le paiement).
- **Si les frais réels de recouvrement sont supérieurs à cette indemnité**, le créancier (le fournisseur) peut demander une **indemnisation complémentaire**, à condition de justifier les frais.

👉 *Le taux des intérêts moratoires est fixé par la Banque centrale européenne (BCE) : il correspond au taux d’intérêt appliqué par la BCE aux opérations de refinancement les plus récentes, au début du semestre où le retard a commencé, **ajouté de 8 points de pourcentage**.*

---

✅ **En résumé** :  
- Le paiement doit être effectué dans un délai précis (30 jours pour la plupart des cas).  
- Pour certains secteurs (santé, entreprises publiques), ce délai peut être plus long.  
- Si le paiement est en retard, des intérêts et des frais sont automatiquement dus.  
- Le créancier peut demander une compensation si les frais réels sont supérieurs à l’indemnité forfaitaire.

---

⚠️ *Termes juridiques non simplifiés* :  
- **Pouvoir adjudicateur** : terme juridique désignant l’organisme ou l’entreprise qui achète.  
- **Retard de paiement** : terme juridique précisant la situation de non-paiement à l’échéance.  
- **Intérêts moratoires** : intérêts automatiquement dus en cas de retard.  
- **Indemnité forfaitaire** : montant fixe versé pour frais de recouvrement.  
- **Entreprise publique** :

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "gain_km": 15.8224,
  "km_entree": 50.13,
  "km_sortie": 65.9524
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La sortie supprime la condition selon laquelle le créancier doit avoir « rempli ses obligations légales et contractuelles », ajoute un point de départ inventé (« 30 jours à compter de la date d'échéance prévue dans le marché ») et range à tort les entreprises publiques dans le délai de 30 jours, alors qu'elles relèvent de 60 jours.
- `termes_juridiques` : 0 — Le terme « entités adjudicatrices » est absent et « de plein droit » est remplacé par « automatiquement » sans être conservé.
- `clarte_percue` : 3 — La structure est accessible, mais des erreurs (« comme une mairie ou une commune », « taux fixé par la BCE ») et une liste finale tronquée (« Entreprise publique : ») peuvent induire l'usager en erreur.
- Inventions : Délai de 30 jours « à compter de la date d'échéance prévue dans le marché »; Les entreprises publiques citées comme exemple de pouvoirs adjudicateurs soumis au délai de 30 jours; Établissements publics locaux « comme une mairie ou une commune »; « Le taux des intérêts moratoires est fixé par la Banque centrale européenne »; Qualification de l'ordonnance du 7 juin 2004 comme « une loi »; Pouvoir adjudicateur défini comme « l'entreprise ou l'organisme qui achète »
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
15 % des 240 demandes sont incomplètes.

Calcul du nombre de demandes incomplètes :  
15 % de 240 = \( \frac{15}{100} \times 240 = 36 \) demandes incomplètes.

Le nombre de demandes complètes est :  
\( 240 - 36 = 204 \).

**Réponse : 204 demandes étaient complètes.**

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse donne le bon résultat (« 204 demandes étaient complètes »), l'étape intermédiaire juste (« 15 % de 240 = … = 36 demandes incomplètes ») et est rédigée en français correct.
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
Pour être tiré au sort comme juré d'assises, il faut remplir les conditions suivantes :

1. Être citoyen de France.  
2. Avoir au moins 18 ans.  
3. Être domicilié en France.  
4. Être en situation de droit de vote (c’est-à-dire être inscrit sur les listes électorales).  
5. Être en bonne santé physique et mentale (capacité à assister à un procès et à rendre un jugement).  
6. Ne pas être en situation de détention ou de restriction de liberté.  
7. Ne pas être en situation de déchéance de droit de vote (ex. : condamnation pour certaines infractions).  
8. Être inscrit dans le registre des personnes susceptibles d’être tirées au sort (le « registre des citoyens »).  

Ces conditions sont fixées par la loi et les règles du procès pénal. Le tirage au sort est effectué par le tribunal de grande instance, en fonction des critères ci-dessus.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse est fausse : elle indique « Avoir au moins 18 ans » au lieu de plus de 23 ans, omet l'obligation de savoir lire et écrire en français et ajoute des conditions non prévues (« registre des citoyens », « bonne santé physique et mentale », « tribunal de grande instance »).
- Inventions : Avoir au moins 18 ans; Être domicilié en France; Être en bonne santé physique et mentale; Être inscrit dans le registre des personnes susceptibles d'être tirées au sort (le « registre des citoyens »); Le tirage au sort est effectué par le tribunal de grande instance
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
On sait que :

- Trois agents : Alice, Bruno et Chloé.
- Ils tiennent l'accueil les trois jours consécutifs : lundi, mardi, mercredi.
- Un agent par jour, un jour chacun.
- Bruno ne travaille pas le lundi.
- Chloé travaille le lendemain du jour d’Alice.

Analysons les contraintes.

**Étape 1 : Bruno ne travaille pas le lundi.**  
Donc Bruno travaille soit le mardi, soit le mercredi.

**Étape 2 : Chloé travaille le lendemain du jour d’Alice.**

Cela signifie que Chloé est le jour suivant celui d’Alice.

Les jours sont : lundi, mardi, mercredi.

Les paires possibles (Alice, Chloé) :

- Si Alice = lundi → Chloé = mardi  
- Si Alice = mardi → Chloé = mercredi  
- Si Alice = mercredi → Chloé = jeudi → impossible (pas de jeudi)

Donc Alice ne peut pas travailler le mercredi.

Donc Alice = lundi ou mardi.

Cas 1 : Alice = lundi → Chloé = mardi  
Alors Bruno doit travailler le mercredi (seul jour restant).

Bruno = mercredi → pas le lundi → OK.

Cas 2 : Alice = mardi → Chloé = mercredi  
Alors Bruno doit travailler le lundi → mais Bruno ne travaille pas le lundi → contradiction.

Donc ce cas est impossible.

**Seul cas possible :**  
- Alice = lundi  
- Chloé = mardi  
- Bruno = mercredi

**Vérification :**  
- Bruno ne travaille pas le lundi → oui, il travaille le mercredi → OK.  
- Chloé travaille le lendemain de Alice → lundi → mardi → OK.  
- Un agent par jour → oui.

✅ Réponse :  
**Alice travaille le lundi, Chloé travaille le mardi, Bruno travaille le mercredi.**

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse donne la bonne attribution (« Alice travaille le lundi, Chloé travaille le mardi, Bruno travaille le mercredi ») et écarte explicitement Alice le mercredi (« pas de jeudi ») et le cas Alice mardi (« contradiction »). Le français est correct malgré une légère faute d'élision (« le lendemain de Alice »), qui ne remet pas en cause le critère.
- Inventions : aucune
- Confiance : moyenne

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
Une question prioritaire de constitutionnalité (QPC) est soumise à la **Cour constitutionnelle**.

Elle passe par les **délais suivants** :

- La **Cour constitutionnelle** doit **se prononcer dans un délai de 3 mois** à compter de la date de la demande, sauf si la question est complexe ou si elle relève d’un domaine particulier, ce qui peut entraîner une extension motivée.

La décision de la Cour constitutionnelle **ne peut pas être appelée**. Elle est **irrévocable** et **finale**.

Ainsi, la QPC est **examinée directement par la Cour constitutionnelle**, qui est la seule juridiction compétente, sans recours ultérieur.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La réponse parle d'une « Cour constitutionnelle » au lieu du Conseil constitutionnel. Elle omet l'examen immédiat par le tribunal administratif ainsi que le filtrage par le Conseil d'État en 3 mois, et affirme à tort que la QPC est « examinée directement par la Cour constitutionnelle, qui est la seule juridiction compétente ».
- Inventions : Juridiction dénommée « Cour constitutionnelle » (il s'agit du Conseil constitutionnel); « sauf si la question est complexe ou si elle relève d'un domaine particulier, ce qui peut entraîner une extension motivée »; « à compter de la date de la demande »; QPC « examinée directement par la Cour constitutionnelle, qui est la seule juridiction compétente »
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
Pour calculer le taux d'activité moyen sur l'année, on considère la durée de travail en pourcentage par mois.

L'agent travaille :
- À 80 % de janvier à avril (4 mois),
- À 100 % de mai à décembre (8 mois).

**Étape 1 : Calculer la part totale de l'année en pourcentage**

On calcule le total de l'activité pondérée par le nombre de mois :

\[
(4 \times 80) + (8 \times 100) = 320 + 800 = 1120
\]

**Étape 2 : Diviser par le nombre total de mois (12)**

\[
\frac{1120}{12} \approx 93.3
\]

**Résultat :** Le taux d'activité moyen est de **93,3 %**.

**Explication :**  
On multiplie le taux d'activité par le nombre de mois pour chaque période, on additionne ces valeurs, puis on divise par 12 (le nombre total de mois). Cela donne le taux moyen d'activité sur l'année.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 1 — La réponse respecte tous les critères : décompte juste (« 4 mois » à 80 % et « 8 mois » à 100 %), moyenne pondérée « (4 × 80) + (8 × 100) = 1120 » divisée par 12, résultat final « 93,3 % » arrondi au dixième, le tout en français correct (seule la notation « 93.3 » dans la formule utilise un point décimal, sans incidence sur le résultat énoncé).
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
Les travaux fermeront le service le 3 juin.

Sources citées :
aucune
```

### Contrôles automatiques

Aucun.

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La phrase est courte (8 mots), conserve la date et la cause et supprime la formule administrative, mais « Les travaux fermeront le service » remplace « l'accueil du public » par « le service » : le lecteur peut croire que tout le service est fermé, ce qui déforme l'information d'origine.
- Inventions : Fermeture du « service » dans son ensemble, alors que la source ne mentionne que la suspension de l'accueil du public
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
L'Agence nationale de l'habitat (Anah) est une agence qui met en œuvre la politique nationale d'amélioration du parc de logements privés existants. Elle accorde des aides financières aux propriétaires occupants, bailleurs et aux syndicats de copropriétaires pour la réalisation de travaux lourds ou d'amélioration de leur habitat, sous certaines conditions [1].

Pour les particuliers, l'Anah peut notamment :
- Accorder une aide financière pour des travaux tels que la rénovation énergétique ou l'adaptation à la perte d'autonomie [5].
- Proposer des dispositifs d'intermédiation locative, qui permettent de sécuriser et simplifier les relations avec le locataire, en confiant la gestion locative à une agence immobilière sociale ou à un organisme agréé par l'État, avec des avantages comme une réduction fiscale ou une prime d'intermédiation locative [3].

Ainsi, l'Anah sert de soutien concret aux particuliers en leur offrant des aides financières pour améliorer leurs logements et des outils de gestion locative pour les propriétaires.

Sources citées :
- Liste des opérations programmées de l'Anah (en cours et terminées) — https://www.data.gouv.fr/datasets/liste-des-operations-programmees-de-lanah-en-cours-et-terminees
- Aides financières de l'Anah pour réaliser des travaux dans son logement — https://www.service-public.gouv.fr/particuliers/vosdroits/F1328
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

- `exactitude` : 0 — Seul le premier élément clé est présent ; manquent MaPrimeRénov'/MaPrimeRénov' Copropriété/Loc'Avantages, MaPrimeAdapt', Ma Prime Logement décent, ainsi que la demande en ligne et le conseiller France Rénov'. La réponse évoque seulement « la rénovation énergétique ou l'adaptation à la perte d'autonomie » sans nommer les dispositifs, et omet la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — La source citée https://www.service-public.gouv.fr/particuliers/vosdroits/F1328 (« Aides financières de l'Anah pour réaliser des travaux dans son logement ») correspond à la source attendue et traite du point demandé.
- Inventions : « met en œuvre la politique nationale d'amélioration du parc de logements privés existants » : non vérifiable dans les références; « aux propriétaires occupants, bailleurs et aux syndicats de copropriétaires pour la réalisation de travaux lourds » : précision non vérifiable dans les références; Détails sur l'intermédiation locative (gestion confiée à « une agence immobilière sociale ou à un organisme agréé par l'État », « réduction fiscale », « prime d'intermédiation locative ») : non vérifiables dans les références; Appels de citation [1], [5], [3] incohérents avec les trois sources listées
- Confiance : haute

**Juge second** : juge

- `exactitude` : 1 — Un élément clé manque (Ma Prime Logement décent pour les logements indignes ou dégradés) et un autre est imprécis (les dispositifs spécifiques comme MaPrimeRénov', MaPrimeAdapt' ne sont pas cités explicitement).
- `pertinence_source` : 1 — La source https://www.service-public.gouv.fr/particuliers/vosdroits/F1328 traite bien du sujet, mais les autres sources citées sont partiellement hors sujet (ex. : liste des opérations programmées de l'Anah).
- Inventions : Les dispositifs d'intermédiation locative (réduction fiscale, prime d'intermédiation locative) ne sont pas mentionnés dans les éléments clés de la référence, bien qu'ils soient partiellement évoqués dans une source secondaire.
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
La perte d'autonomie de votre mère sera évaluée par un professionnel de l'équipe médico-sociale (EMS) de votre département, qui se déplace à son domicile pour effectuer une évaluation sur la base de la grille Aggir [2]. Cette grille définit plusieurs degrés de perte d'autonomie, allant du Gir 1 (perte d'autonomie la plus forte) au Gir 6 (perte d'autonomie la plus faible) [1].

L’Allocation personnalisée d’autonomie (Apa) peut être accordée **si votre mère est classée en Gir 1, Gir 2, Gir 3 ou Gir 4** [1]. Si elle est classée en Gir 5 ou Gir 6, elle ne peut pas obtenir l’Apa à domicile, mais elle peut demander une aide auprès de sa caisse de retraite [5].

Le professionnel de l’EMS évaluera non seulement la perte d’autonomie, mais aussi la situation et les besoins de votre mère, ainsi que ceux de votre proche aidant, si applicable [2].

La décision d’attribution de l’Apa est prise par les services du département et doit être rendue dans les 2 mois suivant la réception du dossier complet [3].

> **Résumé à transmettre à la fille** :  
> La perte d'autonomie sera évaluée par un professionnel de l'EMS sur la grille Aggir. L’Apa peut être accordée si la personne est classée en Gir 1, 2, 3 ou 4. Si elle est classée en Gir 5 ou 6, l’Apa n’est pas disponible à domicile, mais une aide peut être demandée auprès de la caisse de retraite. La décision du département est prise dans les 2 mois suivant le dépôt du dossier complet.

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

- `exactitude` : 1 — La réponse cite bien la grille Aggir, les Gir 1 à 6, l'Apa du Gir 1 au Gir 4 et l'orientation vers la caisse de retraite en Gir 5-6, mais elle omet l'élément clé des 10 activités discriminantes et des 7 activités illustratives. Elle est aussi imprécise sur deux points : « elle ne peut pas obtenir l'Apa à domicile » (la référence exclut l'Apa en Gir 5-6 sans restriction au domicile) et l'absence de mention de l'Apa en établissement pour les Gir 1 à 4.
- `pertinence_source` : 1 — La fiche F10009 (Apa à domicile) traite bien de l'évaluation Aggir et des Gir ouvrant droit à l'Apa, même si ce n'est pas la source attendue F1229 ; l'appel [5] ne renvoie à aucune source listée (4 entrées seulement, toutes identiques).
- Inventions : Évaluation par un professionnel de l'équipe médico-sociale (EMS) du département qui se déplace au domicile, non vérifiable dans les références; Évaluation de la situation et des besoins du proche aidant par l'EMS, non vérifiable dans les références; Décision du département rendue dans les 2 mois suivant la réception du dossier complet, non vérifiable dans les références; Appel de source [5] sans source correspondante dans la liste citée
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
Oui, une personne qui perçoit l'allocation aux adultes handicapés (AAH) peut aussi percevoir le RSA, mais le montant du RSA sera réduit par le montant de l'AAH perçu.  

Cela est précisé dans le passage [1] : « Oui, vous pouvez cumuler le revenu de solidarité active (RSA) et l'allocation aux adultes handicapés (AAH) si vous remplissez les conditions requises. Cependant, si vous percevez l'AAH, vous ne pouvez pas percevoir le RSA dans son intégralité. Le montant de votre RSA sera alors réduit par rapport au montant de votre AAH que vous percevez. »  

Il est également mentionné dans le passage [3] que « Si vous percevez d'autres allocations (par exemple : pension d'invalidité, RSA ), vous recevez une AAH réduite », ce qui confirme que le cumul est possible mais avec une réduction du RSA.  

Ainsi, la réponse est fondée sur les passages [1] et [3].

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

- `exactitude` : 0 — Le troisième élément clé manque : il n'est pas dit qu'il peut être plus avantageux de conserver la seule AAH. La réponse contredit aussi le passage [3], qui dit « vous recevez une AAH réduite », en affirmant que cela « confirme que le cumul est possible mais avec une réduction du RSA ».
- `pertinence_source` : 1 — La source F20209 citée traite exactement du cumul AAH/RSA, ce qui correspond à la question posée.
- Inventions : Interprétation du passage [3] comme confirmant « une réduction du RSA », alors que le passage cité parle d'une AAH réduite
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
La femme de 63 ans peut encore demander la prestation de compensation du handicap (PCH), car elle a déjà rempli les conditions d’attribution avant 60 ans (elle est en situation de handicap depuis l’âge de 50 ans), ce qui lui permet de demander la PCH au-delà de 60 ans, sans limite d’âge [1].

Les revenus de la personne sont pris en compte pour déterminer le taux de prise en charge de ses dépenses liées à la perte d’autonomie :  
- Si ses ressources annuelles sont inférieures ou égales à 31 162,62 €, ses dépenses sont prises en charge à 100 % ;  
- Si elles sont supérieures, le taux de prise en charge est de 80 % [4].  
Cependant, la prestation est attribuée sans condition de ressources en termes d’éligibilité, mais les ressources influencent le montant de la prise en charge des dépenses [4].

La demande peut être faite en ligne ou par courrier, en joignant les documents justificatifs (scannés ou imprimés) à la MDPH de son lieu de résidence [2].

**Réponse complète :**  
Oui, la femme de 63 ans peut demander la prestation de compensation du handicap (PCH) car elle a déjà été en situation de handicap avant 60 ans [1]. Ses revenus sont pris en compte pour déterminer le taux de prise en charge de ses dépenses (100 % si ses ressources annuelles sont inférieures ou égales à 31 162,62 €, ou 80 % sinon) [4]. Elle doit déposer sa demande auprès de la MDPH de son lieu de résidence, soit en ligne (si la MDPH le propose), soit par courrier en joignant les documents justificatifs [2].

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

- `exactitude` : 0 — Deux éléments clés manquent : le critère de difficulté (absolue pour 1 activité ou grave pour au moins 2, sur au moins 1 an) et la décision de la CDAPH sous 4 mois avec rejet implicite. En outre, la réponse affirme sans réserve qu'« elle a déjà rempli les conditions d'attribution avant 60 ans », alors qu'avoir un handicap depuis 50 ans ne suffit pas à le garantir. La mention « Ne vaut pas avis juridique » est absente.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F14202) est la fiche officielle sur la PCH et traite bien de l'âge, des ressources et du dépôt de la demande.
- Inventions : « en joignant les documents justificatifs (scannés ou imprimés) » : détail invérifiable dans l'entrée et les références.; « elle a déjà rempli les conditions d'attribution avant 60 ans » : conclusion présentée comme certaine, non déductible de l'entrée.
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
Oui, cette locataire peut bénéficier de MaPrimeAdapt'.

**1. Éligibilité :**  
Elle est éligible car :  
- Elle est locataire d’un logement du parc privé (condition requise pour les locataires)  
- Elle a 66 ans, ce qui la place entre 60 et 69 ans  
- Elle est classée dans un groupe iso-ressources (GIR) après hospitalisation (condition requise)  
- Elle vit hors Île-de-France  

Ces conditions sont explicitement mentionnées dans le passage [5] :  
> « Vous ou un membre de votre foyer avez entre 60 et 69 ans, et êtes classé dans un groupe iso-ressources (GIR) »  
> « Vous ou un membre de votre foyer avez obtenu l'accord de votre bailleur pour réaliser des travaux d'adaptation du logement à votre perte d'autonomie »  

Elle respecte donc les conditions d’éligibilité pour être bénéficiaire de MaPrimeAdapt'.

**2. Taux de prise en charge :**  
Le taux de prise en charge dépend du niveau de ressources.  
Elle a un revenu fiscal de référence (RFR) de 20 000 €.  

Dans le cas hors Île-de-France, pour un ménage de 1 personne (elle vit seule), les plafonds sont :  
- Ressources très modestes : jusqu’à 17 363 €  
- Ressources modestes : jusqu’à 22 259 €  

Son RFR (20 000 €) est inférieur au plafond des ressources modestes (22 259 €), donc elle est classée dans le groupe des **ressources modestes**.

Selon le passage [3] :  
> « Cas Modestes : Vous pouvez bénéficier d'une prise en charge de 50 % de vos travaux, dans la limite d'un plafond de 22 000 € hors taxes. »

Donc, elle peut bénéficier d’un **taux de 50 %** sur les travaux, dans la limite de 22 000 € HT.

Le devis est de 10 000 € HT, donc :  
50 % de 10 000 € = 5 000 € d’aide.

**3. Démarches à effectuer :**  
Elle doit :  
- Déposer sa demande d’aide en ligne sur le site **monprojetanah**  
- Créer un compte personnel sur ce site  
- Faire sa demande depuis l’entrée « Je suis propriétaire occupant » ? → **Non**, car elle est locataire.  

Cependant, le passage [4] précise :  
> « Si vous êtes locataire, vous devez faire votre demande d'aide MaPrimeAdapt' depuis l'entrée « Je suis propriétaire occupant » »  

Cela semble contradictoire. Or, le passage [5] précise que les locataires peuvent bénéficier de MaPrimeAdapt' **si elles ont obtenu l'accord de leur bailleur**.  

Il est donc nécessaire de clarifier :  
Le passage [4] indique une erreur ou une incohérence dans la procédure. En effet, le texte dit que les locataires doivent faire la demande depuis « Je suis propriétaire occupant », ce qui est incorrect.  

**Conclusion :**  
Le passage [5] précise que les locataires peuvent bénéficier de MaPrimeAdapt' et que la demande doit être faite **en ligne sur monprojetanah**, mais **sans préciser la page de demande**. Le passage [4] contient une erreur : il est erroné de dire que les locataires doivent faire la demande depuis « Je suis propriétaire occupant ».  

Cependant, **aucun passage ne précise clairement la page ou le formulaire spécifique pour les locataires**.  

**Réponse finale :**

✅ **Oui**, cette locataire peut bénéficier de MaPrimeAdapt'.  
✅ **Taux de prise en charge : 50 %** (car elle a des ressources modestes hors Île-de-France).  
✅ **Montant de l’aide : 5 000 €** (50 % de 10 000 € HT).  
✅ **Démarches :** Elle doit déposer sa demande en ligne sur le site **monprojetanah**, en se connectant avec un compte personnel.  

**Sources :**  
- [5] : conditions d’éligibilité pour les locataires (

Sources citées :
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

- `exactitude` : 0 — La sortie contredit la source en affirmant que « le passage [4] contient une erreur : il est erroné de dire que les locataires doivent faire la demande depuis « Je suis propriétaire occupant » », alors que c'est la procédure attendue ; elle omet aussi l'accord de l'Anah à attendre avant les travaux et ne présente pas l'accord du bailleur comme une démarche à accomplir, malgré des éléments justes sur l'âge, le Gir, la catégorie « modestes », le taux de 50 % et le montant de 5 000 €.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F37501) correspond à la source attendue et traite bien de MaPrimeAdapt'.
- Inventions : Affirmation que le passage [4] est erroné ou incohérent sur l'entrée « Je suis propriétaire occupant » pour les locataires; Affirmation que le passage [5] précise que la demande doit être faite en ligne sur monprojetanah, invérifiable; Obligation de « créer un compte personnel » sur le site, invérifiable dans les références
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
L’usager doit être informé que, puisque le mariage a été célébré en France, il doit se rendre à la mairie où a été célébré le mariage (dans la commune où le mariage a eu lieu) pour mettre à jour son livret de famille.

Cependant, comme le livret original est détenue par son ex-épouse, il est nécessaire de préciser que, en cas de divorce ou de séparation, un second livret peut être remis à celui qui ne possède pas le livret original [2].

Concernant la mise à jour du livret, puisque le divorce est un changement d’état civil, il faut procéder à une mise à jour du livret de famille [1]. Cette mise à jour peut être effectuée à la mairie où a été célébré le mariage, car le mariage a eu lieu en France [1].

Il est donc recommandé de lui indiquer que :

- Il doit se rendre à la mairie où a été célébré le mariage (dans la commune où le mariage a eu lieu) pour faire inscrire le divorce sur le livret de famille.
- Puisque le livret original est détenue par son ex-épouse, il peut demander un second livret de famille, qui peut être nécessaire pour certaines démarches administratives [4].
- La demande d’un second livret peut être faite à la mairie où il réside (dans la commune où il habite désormais) [4].

**Résumé des points à lui indiquer :**

1. Le divorce doit être inscrit sur le livret de famille à la mairie où a été célébré le mariage (commune du mariage) [1].
2. Un second livret peut être demandé à la mairie de résidence (dans la commune où il habite désormais) en cas de perte du livret original [2][4].

> **Note** : Le passage [1] indique que pour un mariage en France, on doit se rendre à la mairie où a été célébré le mariage avec carte d’identité et jugement de divorce. Cependant, ce passage ne précise pas explicitement que le livret doit être mis à jour par le demandeur ou que le second livret peut être demandé à la mairie de résidence. Cependant, le passage [4] précise que la demande d’un second livret peut être faite à la mairie de résidence, et le passage [2] confirme que un second livret peut être remis à celui qui ne possède pas le livret original.

✅ Donc, les affirmations sont fondées sur les passages [1], [2] et [4].

Sources citées :
- Mise à jour du livret de famille à la suite d'un changement d'état civil (naissance, divorce, etc.) — https://www.service-public.gouv.fr/particuliers/vosdroits/F18910
- Mise à jour du livret de famille à la suite d'un changement d'état civil (naissance, divorce, etc.) — https://www.service-public.gouv.fr/particuliers/vosdroits/F18910
- Demande d'un second livret de famille en cas de divorce ou de séparation — https://www.service-public.gouv.fr/particuliers/vosdroits/F11996
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie omet l'élément clé sur le rôle de l'officier de l'état civil (remplir, dater, signer, tamponner) et celui sur la transmission possible par la mairie de résidence avec la réserve que toutes les mairies n'acceptent pas de servir d'intermédiaire ; elle ne mentionne la carte d'identité et le jugement de divorce que dans la note, et affirme sans source que le second livret est demandé « en cas de perte du livret original », ce qui est erroné. La mention « Ne vaut pas avis juridique » est également absente.
- `pertinence_source` : 1 — La source F18910 citée correspond à la source attendue et traite bien de la mise à jour du livret de famille après un divorce.
- Inventions : « Un second livret peut être demandé à la mairie de résidence [...] en cas de perte du livret original » : le motif de perte ne figure pas dans les références, qui visent le cas du divorce.; « La demande d'un second livret peut être faite à la mairie où il réside » : non vérifiable dans l'entrée ni dans les références.; « un second livret de famille, qui peut être nécessaire pour certaines démarches administratives » : non vérifiable dans les références.
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
Aucun des passages de l'Index local ne mentionne la possibilité d'épouser un décedé à titre posthume, ni la démarche à suivre pour cela. Les passages traitent uniquement des démarches liées au décès (ex : organiser les obsèques, prévenir les organismes, gérer la succession, déterminer les obligations fiscales, etc.), mais aucune référence n'est faite à la notion d'union à titre posthume ou à la possibilité d'un mariage posthume.

Il n'est donc pas possible de répondre à la question sur la possibilité d'épouser un décedé à titre posthume, car ce sujet n'est pas abordé dans les passages fournis.

👉 **Orientation** : La question de la possibilité d'un mariage à titre posthume relève de la législation sur les unions civiles et les droits de la personne décédée. Cette information ne figure pas dans les passages fournis. L'usagère doit consulter un avocat ou un service de droit de la famille ou de la succession pour obtenir une réponse juridique précise.

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

- `exactitude` : 1 — La sortie dit bien qu'aucun passage ne traite du mariage posthume, ne cite aucune fiche et oriente vers un avocat. Elle ajoute cependant une affirmation non sourcée et imprécise (« relève de la législation sur les unions civiles et les droits de la personne décédée ») sans la signaler clairement comme à vérifier. Elle n'oriente pas vers l'état civil de la mairie et omet la mention « Ne vaut pas avis juridique ».
- `pertinence_source` : 1 — Aucune source n'est citée (« Sources citées : aucune »), ce qui est conforme à sources_attendues vide pour un item sans réponse ; aucune source hors sujet n'est présentée comme traitant du point.
- `cas_sans_reponse` : 1 — L'Assistant déclare « Il n'est donc pas possible de répondre à la question… ce sujet n'est pas abordé dans les passages fournis » et oriente vers « un avocat », conformément à l'orientation attendue (professionnel du droit), sans inventer de procédure.
- Inventions : « La question de la possibilité d'un mariage à titre posthume relève de la législation sur les unions civiles et les droits de la personne décédée » : rattachement juridique non vérifiable dans l'entrée ou les références, et imprécis.; « un service de droit de la famille ou de la succession » : interlocuteur non défini, absent des références.
- Confiance : moyenne

**Juge second** : juge

- `exactitude` : 2 — Tous les éléments clés sont présents et justes : la sortie indique explicitement qu'aucune source officielle ne traite du mariage posthume, n'invente ni procédure ni condition, et ne présente aucune fiche comme traitant du sujet. Elle oriente vers un professionnel du droit (avocat) et mentionne que les éléments avancés sont non sourcés.
- `pertinence_source` : 1 — Aucune source n'est citée, ce qui est cohérent avec l'absence de sources disponibles dans les références. Le critère est donc respecté.
- `cas_sans_reponse` : 1 — La sortie indique clairement qu'aucune réponse sourcée n'est possible et oriente vers les autorités compétentes (avocat, service de droit de la famille), conformément à l'orientation attendue.
- Inventions : aucune
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
La journée de solidarité s'applique aux agents territoriaux, comme aux fonctionnaires et aux contractuels, et consiste en une journée supplémentaire de travail de 7 heures non rémunérée. Pour les agents travaillant à temps partiel ou à temps non complet, les 7 heures sont réduites en proportion de leur durée de travail.

Les modalités d’accomplissement de la journée de solidarité varient selon le territoire :

- **Dans le cas général (sur le reste du territoire français)** : la journée peut être accomplie par :
  - Le travail d’un jour férié précédemment chômé, autre que le 1er mai,
  - La suppression d’une journée de RTT,
  - Toute autre organisation permettant le travail de 7 heures précédemment non travaillées, sauf suppression d’un jour de congé annuel.

- **Dans les départements de la Moselle, du Bas-Rhin et du Haut-Rhin (Alsace-Moselle)** : la journée peut être accomplie par :
  - Le travail d’un jour férié normalement chômé, autre que le 1er mai, les 25 et 26 décembre et le Vendredi Saint,
  - La suppression d’une journée de RTT,
  - Toute autre organisation permettant le travail de 7 heures précédemment non travaillées, sauf suppression d’un jour de congé annuel.

Les conditions d’accomplissement de la journée de solidarité sont fixées :
- **Dans la fonction publique territoriale**, par délibération après avis du comité social territorial.

Cela répond à la question de la nature de la journée de solidarité, de son mode d’accomplissement et de l’organisme qui fixe les modalités pour les agents territoriaux.

[1]

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

- `exactitude` : 2 — Les quatre éléments clés sont présents et justes : la journée de 7 heures non rémunérée pour fonctionnaires et contractuels, la proratisation pour le temps partiel ou non complet, les trois modalités du cas général avec l'exclusion du congé annuel, et la délibération après avis du comité social territorial ; aucune contradiction avec la référence n'apparaît, mais le développement sur l'Alsace-Moselle n'est pas vérifiable dans les références.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F2859) correspond exactement à la source attendue et traite bien de l'accomplissement de la journée de solidarité dans la fonction publique.
- Inventions : Modalités spécifiques à l'Alsace-Moselle : « travail d'un jour férié normalement chômé, autre que le 1er mai, les 25 et 26 décembre et le Vendredi Saint » (non vérifiable dans l'entrée ni dans les références, qui indiquent seulement « Hors Alsace-Moselle »)
- Confiance : moyenne

**Juge second** : juge

- `exactitude` : 2 — Tous les éléments clés sont présents et justes, sans erreur factuelle. La distinction pour l'Alsace-Moselle, bien que non mentionnée dans les éléments clés, est exacte et ne contredit pas la référence.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr) est pertinente et traite bien du sujet demandé.
- Inventions : aucune
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
**Règle générale :**  
Oui, lorsqu’un agent public est en congé de maladie, un jour de carence (jour non rémunéré) est appliqué lors de chaque arrêt de travail, sauf dans certains cas précis [1].

**Cas spécifique de la question :**  
Un jour de carence **doit être retenu** dans ce cas, sauf si la situation relève d’une exception.  

Cependant, selon le passage [2] et [3], **le jour de carence ne s'applique pas** dans le cas de **prolongation de congé de maladie dans les 48 heures**, lorsque :  
- le nouvel arrêt de travail prolonge l’arrêt précédent,  
- le médecin prescripteur a coché la case « prolongation »,  
- et que la reprise du travail entre deux congés pour la même affection n’a pas dépassé 48 heures.  

Dans ce cas, **le nouvel arrêt est considéré comme une rechute et une prolongation**, et **le jour de carence ne s'applique pas**.  

👉 **Conclusion :**  
Dans le cas décrit (reprise le lundi, arrêt le mardi pour la même affection, avec case « prolongation »), **le jour de carence ne doit pas être retenu**.  

**Référence :**  
[2] – « Le jour de carence ne s'applique pas lors du 2 e congé de maladie, lorsque la reprise du travail entre 2 congés de maladie pour la même affection n'a pas dépassé 48 heures. Il en est ainsi lorsque le nouvel arrêt de travail prolonge l'arrêt précédent et que le médecin prescripteur a coché la case prolongation. »  
[3] – Même règle formulée de façon identique.  

✅ **Réponse finale :**  
Non, un nouveau jour de carence ne doit pas être retenu. La règle générale est que chaque arrêt de maladie est suivi d’un jour de carence non rémunéré, sauf dans les cas de prolongation dans les 48 heures, où le jour de carence ne s’applique pas.

Sources citées :
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

- `exactitude` : 0 — La réponse omet au moins deux éléments clés : rien sur les éléments non versés le 1er jour (traitement, primes, IR, NBI ; SFT maintenu), rien sur le décompte des 48 heures en jours calendaires, et la rémunération à partir du 2e jour n'est pas explicitée ; elle se contredit aussi en affirmant d'abord « Un jour de carence doit être retenu dans ce cas » avant de conclure l'inverse.
- `pertinence_source` : 1 — La fiche service-public.gouv.fr F13861, citée, traite bien du jour de carence dans la fonction publique et de l'exception de prolongation dans les 48 heures.
- Inventions : « le nouvel arrêt est considéré comme une rechute et une prolongation » : la qualification de « rechute » ne figure ni dans l'entrée ni dans les références
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
Oui, il est possible pour une agente de la préfecture (fonction publique d'État), à temps plein et enceinte, de télétravailler plus de 3 jours par semaine.

**Justification :**  
Selon le passage [1], « si vous remplissez les conditions pour bénéficier d'un congé de proche aidant » ou « pendant votre grossesse », vous pouvez demander à télétravailler plus de 3 jours par semaine. Cela s'applique à la fonction publique d'État (FPE), comme la préfecture. Ainsi, étant enceinte, elle peut demander un télétravail de plus de 3 jours par semaine.

**Procédure de demande :**  
Elle doit formuler sa demande auprès de son supérieur hiérarchique, en précisant son besoin de télétravail en raison de sa grossesse. Le passage [3] indique que « vous pouvez informer votre supérieur hiérarchique de votre nécessité de venir sur site un jour pour lequel vous bénéficiez d'une autorisation de télétravail et demander à déplacer ce jour de télétravail ». De plus, l'autorisation de télétravail doit être accompagnée d’un document d’information précisant les conditions d’application, notamment les plages horaires, le lieu de travail, et les conditions de contrôle (passage [4]).  

Le passage [4] précise que l’autorisation peut prévoir une période d’adaptation de 3 mois maximum, et que le refus doit être motivé et précédé d’un entretien. Cependant, dans le cas de la grossesse, la demande est justifiée par une situation exceptionnelle perturbant l’accès au service ou le travail sur site, donc elle peut être acceptée sans besoin de refus.

**Indemnité forfaitaire (forfait télétravail) :**  
Le passage [2] précise que le forfait télétravail est de **2,88 € par journée de télétravail**, avec un plafond annuel de **253,44 € (soit 88 jours indemnisés)**.  

Or, l’agent souhaite télétravailler **4 jours par semaine**.  
- 4 jours/semaine × 52 semaines = 208 jours par an.  
- Cependant, le forfait est limité à **88 jours par an** (soit 253,44 €).  

Donc, **elle percevra 2,88 € par jour de télétravail, mais uniquement jusqu’à 88 jours par an**.  

**Conclusion :**  
✅ Oui, elle peut télétravailler 4 jours par semaine en raison de sa grossesse.  
✅ Elle doit faire sa demande auprès de son supérieur hiérarchique, en justifiant sa situation de grossesse.  
✅ Elle percevra un forfait télétravail de **2,88 € par jour**, **mais uniquement pour un maximum de 88 jours par an** (soit 253,44 €).  

**Références :**  
- [1] : justification de la possibilité de télétravail pendant la grossesse  
- [2] : montant et limite du forfait télétravail  
- [3] : procédure de demande à l’entente avec le supérieur hiérarchique  
- [4] : conditions d’autorisation et de document d’information

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

- `exactitude` : 0 — Plusieurs éléments clés manquent : le principe de 3 jours maximum avec au moins 2 jours sur site n'est pas énoncé, la demande écrite et la décision écrite sous un mois sont absentes (« auprès de son supérieur hiérarchique »), et le versement trimestriel du forfait n'est pas mentionné ; la réponse contient en outre des erreurs, comme « elle peut être acceptée sans besoin de refus » ou « Oui, elle peut télétravailler 4 jours par semaine », alors qu'il s'agit seulement d'une possibilité de demande.
- `pertinence_source` : 1 — La source citée (service-public.gouv.fr F13974, « Télétravail dans la fonction publique ») traite bien du télétravail des agents publics, y compris pendant la grossesse, et du forfait.
- Inventions : « dans le cas de la grossesse, la demande est justifiée par une situation exceptionnelle perturbant l'accès au service ou le travail sur site, donc elle peut être acceptée sans besoin de refus »; « Elle doit faire sa demande auprès de son supérieur hiérarchique, en justifiant sa situation de grossesse » (procédure non conforme à la référence, qui prévoit une demande écrite et une décision sous un mois)
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
Aucun des passages fournis ne mentionne l'Agence Régionale de Santé (ARS) Bourgogne-Franche-Comté, ni son statut, ses missions ou son organisation.

Les passages disponibles concernent des établissements de santé, des maisons régionales de santé (dans la région PACA), des aires de covoiturage et des zones de sauvegarde, mais aucun ne fournit des informations sur l'ARS.

**Conseil** : Pour obtenir des informations précises sur l'Agence Régionale de Santé de Bourgogne-Franche-Comté, je vous recommande de consulter le site officiel de l'ARS Bourgogne-Franche-Comté ou les documents de l'Agence de Santé ou du ministère de la Santé.

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

- `exactitude` : 2 — Les quatre éléments clés sont présents : la sortie dit qu'« aucun des passages fournis ne mentionne l'Agence Régionale de Santé (ARS) Bourgogne-Franche-Comté, ni son statut, ses missions ou son organisation ». Elle n'avance ni statut, ni date, ni missions, ne cite aucune URL et oriente vers le site officiel de l'ARS. La mention obligatoire « Ne vaut pas avis juridique » est toutefois absente.
- `pertinence_source` : 1 — Aucune source n'est citée, ce qui est conforme pour un item sans réponse dont les sources attendues sont vides ; aucune source hors sujet n'est donc présentée.
- `cas_sans_reponse` : 1 — L'Assistant déclare ne pas disposer d'information officielle sur l'ARS et recommande de « consulter le site officiel de l'ARS Bourgogne-Franche-Comté », conformément à l'orientation attendue.
- Inventions : Description non vérifiable du contenu des passages retrouvés : « maisons régionales de santé (dans la région PACA), des aires de covoiturage et des zones de sauvegarde »; Orientation vague et non vérifiable vers « les documents de l'Agence de Santé »
- Confiance : moyenne

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
Aucun des passages fournis ne mentionne la possibilité d'instituer une taxe sur les friches commerciales, ni ne précise quelles zones ou locaux seraient concernés, quel serait le taux applicable, ni la date de délibération nécessaire pour une application l'année suivante.

Les passages disponibles traitent uniquement des suivants :

- La **taxe d'aménagement** dans le cadre de la fiscalité de l'urbanisme [1] ;
- La **fiscalité locale millésimée** (taxe d'habitation, cotisation foncière des entreprises, taxe sur le foncier bâti et non bâti) [2] ;
- Les **travaux à déclarer aux impôts** (construction, démolition, agrandissement) [3] ;
- La **définition des friches** issues de l'EPFN dans l'Orne en 2026 [4] ;
- Une carte départementale des impôts locaux dans le Meurthe-et-Moselle (non applicable à l'Orne) [5].

Concernant les friches :

- Le passage [4] définit une friche comme un espace ayant eu une activité urbaine ou économique, non utilisé ou marginalement utilisé, sans usage pérenne, et peut être traité (déconstruction, dépollution), mais sans retour d’usage.
- Il précise que **les friches faisant l’objet de projets de recyclage sont recensées tant que les travaux d’aménagement ou de construction ne sont pas commencés**.
- Il précise que **les friches agricoles ne sont pas prises en compte**, sauf présence de bâtiments dégradés.

Cependant, **aucun élément ne permet de conclure** que :

- Une taxe sur les friches commerciales pourrait être instituée ;
- Quels locaux seraient concernés (ex : friches commerciales, zones industrielles, etc.) ;
- Quel serait le taux applicable ;
- Quelle est la date de délibération nécessaire pour une application l'année suivante.

👉 **Conclusion** :  
**Il n'est pas possible de répondre aux élus** sur la question posée, car **aucun des passages fournis ne contient les informations nécessaires** sur la création d'une taxe sur les friches commerciales, ni sur les critères d'application, le taux ou la procédure de délibération.

➡️ **Recommandation** :  
Vous devez consulter le **service compétent** (ex : Direction Départementale des Territoires et de la Mer, ou le conseil général de l'Orne) ou **la réglementation en vigueur sur la fiscalité des espaces inoccupés ou en friche**, notamment en lien avec la fiscalité de l'urbanisme ou la taxe d'aménagement, pour évaluer la faisabilité et les modalités d'une telle mesure.

👉 **Source à consulter** :  
[Direction Départementale des Territoires et de la Mer de l'Eure](https://www.data.gouv.fr/datasets/taxe-damenagement-dans-le-cadre-de-la-fiscalite-de-lurbanisme-pour-2021)  
[Observatoire de l'EPFN – Friches dans l'Orne](https://www.data.gouv.fr/datasets/friches-issues-de-l-epfn-dans-lorne-en-2026)

Sources citées :
- Taxe d'aménagement dans le cadre de la fiscalité de l'urbanisme pour 2021 — https://www.data.gouv.fr/datasets/taxe-damenagement-dans-le-cadre-de-la-fiscalite-de-lurbanisme-pour-2021
- Fiscalité locale - Millésimé — https://www.data.gouv.fr/datasets/fiscalite-locale-millesime
- Quels sont les travaux à déclarer aux impôts ? — https://www.service-public.gouv.fr/particuliers/vosdroits/F35742
- Friches issues de l' EPFN dans l'Orne en 2026 — https://www.data.gouv.fr/datasets/friches-issues-de-l-epfn-dans-lorne-en-2026
- Impôts locaux Moyen par actifs - Carte départementale 54 Meurthe et Moselle 2015 — https://www.data.gouv.fr/datasets/impots-locaux-moyen-par-actifs-carte-departementale-54-meurthe-et-moselle-2015
```

### Contrôles automatiques

```text
{
  "urls_inventees": []
}
```

### Verdicts

**Juge principal** : juge

- `exactitude` : 0 — La sortie dit bien qu'aucun passage ne traite de la taxe, mais elle n'oriente pas vers la DDFiP ni vers les publications officielles de fiscalité locale, cite la fiche service-public F35742 parmi ses « Sources citées » et omet la mention « Ne vaut pas avis juridique » : au moins deux éléments clés manquent ou sont enfreints.
- `pertinence_source` : 0 — Aucune des sources citées ne traite de la taxe sur les friches commerciales : elles portent sur la taxe d'aménagement, la fiscalité millésimée, les travaux à déclarer, les friches EPFN de l'Orne et une carte de Meurthe-et-Moselle.
- `cas_sans_reponse` : 0 — L'absence de source est reconnue, mais l'orientation n'est pas conforme : la sortie renvoie vers « la Direction Départementale des Territoires et de la Mer, ou le conseil général de l'Orne » et vers la taxe d'aménagement au lieu de la DDFiP, et présente comme « Source à consulter » un lien mal étiqueté.
- Inventions : Libellé « Direction Départementale des Territoires et de la Mer de l'Eure » attribué à un jeu de données data.gouv.fr sur la taxe d'aménagement; Rattachement de la commune à l'Orne (« conseil général de l'Orne »), alors que l'entrée ne précise aucun département; Orientation vers la DDTM ou le conseil général, non vérifiable dans les références
- Confiance : moyenne

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
Le jeu de données national pertinent pour vérifier les communes soumises à la loi SRU et l'état de leur inventaire de logements sociaux est : 

- **Titre** : Communes et inventaire SRU
- **Producteur** : Ministère de la Transition écologique
- **Date de dernière mise à jour** : Non précisée dans les résultats
- **Lien** : https://www.data.gouv.fr/datasets/communes-et-inventaire-sru

[1]

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
Le jeu de données correspondant à l'information demandée est :

**Titre** : RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National]  
**Producteur** : Caisse Nationale des Allocations familiales  
**Date de dernière mise à jour** : Non disponible dans les résultats fournis  
**Licence** : Non disponible dans les résultats fournis  
**Fréquence de mise à jour** : Non disponible dans les résultats fournis  

[1]

*Note : Les informations sur la date de mise à jour, la licence et la fréquence de mise à jour ne sont pas disponibles dans les résultats fournis. Pour obtenir ces détails, il serait nécessaire de consulter directement la ressource ou son détail sur data.gouv.fr.*

Sources citées :
aucune
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
  "litige": true,
  "methode": "identifiant",
  "reponse_exacte": null
}
```

### Verdicts

**Juge principal** : juge

- `libelle_correct` : 1 — Le titre cité, « RSA - Répartition des allocataires selon le type de RSA et la situation familiale [National] », et le producteur (CNAF) correspondent exactement au jeu national de référence et l'identifient sans ambiguïté par rapport à la version départementale ; en revanche, l'identifiant 66d1e5a979919854e97093bd et l'URL sont absents, et la date, la licence et la fréquence demandées sont déclarées « Non disponible », ce qui pèse sur la composante « Réponse exacte » du banc et non sur ce critère.
- Inventions : aucune
- Confiance : moyenne

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
Le jeu de données national sur les bénéficiaires de l'aide sociale à l'enfance, publié par le Ministère des Solidarités et de la Santé, est intitulé « Les bénéficiaires de l'aide sociale à l'enfance ». Il propose 20 ressources (fichiers). 

Parmi ces ressources, le fichier de séries longues le plus récent est intégré dans ce jeu de données, mais son nom exact et son format ne sont pas précisés dans les résultats disponibles. Il est possible que ce fichier soit disponible sous forme de fichier CSV ou de fichier Excel, mais aucune information précise sur le format ou le nom exact du fichier de séries longues n'est fournie dans les résultats actuels.

[1]

Sources citées :
aucune
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
  "litige": true,
  "methode": "identifiant",
  "reponse_exacte": null
}
```

### Verdicts

**Juge principal** : juge

- `libelle_correct` : 1 — Le libellé « Les bénéficiaires de l'aide sociale à l'enfance » et le producteur « Ministère des Solidarités et de la Santé » correspondent exactement à la référence, mais l'identifiant 62e325ed203e2e75a70505d1 est absent. La réponse indique bien 20 ressources, en revanche elle ne désigne pas le fichier « séries longues (1996-2024).xlsx » (« son nom exact et son format ne sont pas précisés »).
- Inventions : aucune
- Confiance : moyenne

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
Oui, un jeu de données correspond à votre demande. Voici le répertoire national des élus : 

- **Titre** : Répertoire national des élus
- **Producteur** : Ministère de l'intérieur
- **Date de dernière mise à jour** : Non précisée dans les résultats
- **Lien** : [https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1](https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1)

Ce jeu de données inclut des informations sur les conseillers municipaux, départementaux, régionaux et communautaires, ce qui répond à votre besoin d’un répertoire national des élus en fonction.

[1]

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
Le jeu de données le plus pertinent pour votre demande est : 

- **Titre** : Service-public.gouv.fr - Annuaire de l’administration - Base de données locales
- **Producteur** : Premier ministre
- **Date de dernière mise à jour** : Non précisée dans les résultats
- **Lien** : https://www.data.gouv.fr/datasets/service-public-gouv-fr-annuaire-de-ladministration-base-de-donnees-locales

Ce jeu de données recense les guichets publics locaux, y compris les mairies, avec des informations comme les adresses, téléphones et horaires d'ouverture.

Cependant, **la licence et la fréquence de mise à jour** de ce jeu de données ne sont pas indiquées dans les résultats fournis. Il est recommandé de consulter directement la page du jeu de données ou son documentation pour obtenir ces informations.

[1]

Sources citées :
- Service-public.gouv.fr - Annuaire de l’administration - Base de données locales — https://www.data.gouv.fr/datasets/service-public-gouv-fr-annuaire-de-ladministration-base-de-donnees-locales
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
Le jeu de données correspondant à la question est : 

- **Titre** : Médecins accrédités par la HAS
- **Producteur** : Haute Autorité de santé
- **Date de dernière mise à jour** : Non indiquée dans les résultats
- **Lien** : https://www.data.gouv.fr/datasets/medecins-accredites-par-la-has

[1]

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
Le collège dont l'UAI est 0010005A est le COLLEGE ROGER POULNARD, situé à BAGE DOMMARTIN (code INSEE 01025), dans le département de l'Ain (code 001), en académie de LYON. À la rentrée scolaire 2022-2023, son indice de position sociale (IPS) est de 110,4. L'effectif est de 540 élèves. 

Ces données proviennent du jeu de données « Indices de position sociale dans les collèges (2022) » publié par les Ministères de l'Éducation nationale [1].

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
Le jeu de données "FINESS Extraction du Fichier des établissements" (ID: 53699569a3a729239d2046eb) est publié par le Ministère des Solidarités et de la Santé et inclut une ressource en format CSV. Ce fichier est accessible via l'API tabulaire de data.gouv.fr, ce qui permet d'interroger directement les données en ligne sans les télécharger.

Il n'est pas nécessaire de connaître la taille du fichier ou de fournir son URL de téléchargement, car les données peuvent être consultées et interrogeées via l'API tabulaire, accessible directement à partir de l'URL de la ressource.

[1]

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
Votre demande de logement peut être radiée si elle est irrecevable, non renouvelée à l’anniversaire, sans réponse aux courriers ou après signature du bail. Un avertissement est envoyé ; la radiation suit 1 mois plus tard. Pour contester, adressez-vous à la mairie ou à l’organisme HLM. Si plusieurs demandes sont faites, elles sont regroupées en une seule avec un numéro unique national, conservant les anciennetés acquises.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "courte",
  "mots": 65,
  "plafond_mots": 80,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — La phrase « Un avertissement est envoyé ; la radiation suit 1 mois plus tard » est appliquée à tous les cas, y compris le non-renouvellement et la signature du bail, alors que le document prévoit dans ces cas une radiation sans délai ou immédiate ; de même, « adressez-vous à la mairie ou à l'organisme HLM » omet le guichet enregistreur prévu en cas de non-renouvellement.
- `presence_elements` :
  - P1 : 1 — Les cas « irrecevable » et « sans réponse aux courriers » sont cités avec l'avertissement et la radiation 1 mois plus tard, sans mention toutefois de la lettre recommandée.
  - P2 : 0 — Le non-renouvellement est cité, mais ni la radiation sans délai ni la procédure à recommencer avec un nouveau numéro n'apparaissent ; le délai d'un mois est même implicitement appliqué à ce cas.
  - P3 : 0 — La signature du bail est mentionnée, mais la renonciation écrite est absente.
  - P4 : 0 — Seule la contestation auprès de la mairie ou de l'organisme HLM est mentionnée ; le guichet enregistreur du département est omis.
- Inventions : Généralisation du délai d'un mois après avertissement à tous les cas de radiation, y compris le non-renouvellement et la signature du bail (déformation)
- Confiance : haute

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
**Résumé détaillé pour un agent de l'État civil**

La procédure de changement de prénom est ouverte aux personnes suivantes : Français né en France, Français né à l’étranger avec déclaration au poste consulaires ou transcrit au service central d’état civil, étrangers né en France, et personnes bénéficiant de la protection internationale. Elle s’applique aux majeurs et mineurs.

Pour un majeur, la demande peut être faite par la personne elle-même depuis le 1er juillet 2022, même sous tutelle, sans représentation. Pour un mineur, la demande doit être présentée par le représentant légal ; si l’enfant a plus de 13 ans, son accord est nécessaire. En cas d’exercice conjoint de l’autorité parentale, les deux parents doivent s’engager. En cas de désaccord entre parents séparés, le demandeur doit saisir le juge aux affaires familiales.

La demande peut inclure l’ajout, la suppression ou la modification de l’ordre des prénoms. Elle doit avoir un intérêt légitime : usage prolongé d’un prénom, suppression d’un prénom jugé ridicule, ajout d’un tiret, ou transidentité. Elle ne doit pas nuire à l’intérêt de l’enfant ou aux droits d’autrui. Tout prénom figurant dans l’acte de naissance peut être choisi comme prénom usuel.

La démarche est gratuite. La demande doit être déposée à la mairie de résidence, à celle détention de l’acte de naissance (si né en France), à l’ambassade ou consulat compétent (si à l’étranger), ou à l’Ofpra si certificat d’acte de naissance est disponible. Un récépissé est remis.

Si l’officier d’état civil estime que la demande n’a pas d’intérêt légitime, ou si le demandeur est condamné pour terrorisme, infraction sexuelle sur mineur, violation d’interdiction de sortie ou non-respect de retour, ou est inscrit au Fijait ou Fijaisv, il saisi le procureur de la République. Ce dernier peut accepter ou refuser la demande. En cas de refus, un recours peut être intenté devant le juge aux affaires familiales, avec recours obligatoire à un avocat. Si la demande repose sur la transidentité, la décision ne doit pas s’appuyer sur l’adéquation physique-prénom.

Une fois l’acte mis à jour, les titres d’identité (carte d’identité, passeport) doivent être modifiés dans un délai de 3 mois. L’usage d’un titre d’identité incohérent avec l’état civil est puni de 5 ans de prison et d’une amende jusqu’à 50 000 €.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 369,
  "plafond_mots": 400,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Deux passages déforment le document : « Pour un majeur, la demande peut être faite par la personne elle-même depuis le 1er juillet 2022 » rattache à tout majeur une date qui ne concerne que le majeur sous tutelle, et « puni de 5 ans de prison » supprime le mot « maximum » du document.
- `presence_elements` :
  - P1 : 1 — Les quatre catégories de bénéficiaires sont citées, y compris la déclaration consulaire et la transcription.
  - P2 : 1 — Le résumé couvre le majeur, même sous tutelle, ainsi que le représentant légal, l'accord de l'enfant de plus de 13 ans, les deux parents et le juge aux affaires familiales, malgré la date mal rattachée.
  - P3 : 1 — Le résumé mentionne l'ajout, la suppression et l'ordre des prénoms, l'intérêt légitime, l'intérêt de l'enfant et les droits d'autrui.
  - P4 : 1 — Le point figure dans la phrase « Tout prénom figurant dans l'acte de naissance peut être choisi comme prénom usuel ».
  - P5 : 1 — Le résumé cite la gratuité, les quatre lieux de dépôt et la remise du récépissé.
  - P6 : 1 — La saisine du procureur, ses motifs et l'acceptation ou le refus sont présents, mais l'information du demandeur est omise.
  - P7 : 1 — Le recours devant le juge aux affaires familiales avec avocat obligatoire est mentionné.
  - P8 : 0 — Seule l'absence de lien avec l'apparence physique est reprise ; la possibilité d'un prénom neutre, épicène, féminin ou masculin est omise.
  - P9 : 1 — Le résumé couvre la mise à jour de l'acte, la modification des titres dans les 3 mois et les sanctions, même si le mot « maximum » est omis.
- Inventions : Rattachement de la date du 1er juillet 2022 à la demande de tout majeur, et non au seul majeur sous tutelle; Peine présentée comme fixe (« 5 ans de prison ») au lieu d'un maximum
- Confiance : moyenne

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
Un couple souhaitant se pacsé doit respecter plusieurs conditions : être majeur, ne pas être marié ni pacsé, et ne pas avoir de lien familial direct avec l’autre. Si l’un des partenaires est étranger, il doit avoir l’âge de la majorité dans son pays. Le Pacs est un contrat (convention) signé par les deux partenaires, rédigé en français, et doit inclure leurs signatures. Il peut être minimal (régime de séparation des patrimoines) ou personnalisé (avec précisions sur la participation aux charges ou la propriété des biens). Le contrat est obligatoirement rédigé en français et peut être utilisé un formulaire Cerfa n°15726 ou rédigé par soi-même, avec conseil possible dans une maison de la justice ou auprès d’un notaire.

Le Pacs doit être enregistré en mairie de la commune de résidence commune, ou dans une ambassade/consulat si le couple réside à l’étranger. La démarche est gratuite. Une pré-demande en ligne est possible dans certaines communes via le service public (connexion avec compte ou FranceConnect). Le dépôt se fait sur rendez-vous, souvent avec un délai entre le dépôt du dossier et l’enregistrement. L’officier d’état civil enregistre le Pacs en personne, sans garder de copie du contrat, qui est restitué aux partenaires. Ce document doit être conservé : en cas de perte, une déclaration de modification du Pacs peut être faite avec les références du Pacs initial (numéro et date), et une nouvelle convention sera enregistrée.

Le Pacs prend effet à la date de son enregistrement. Pour les tiers, il est prouvé par une mention sur l’acte de naissance (si né en France) ou sur le registre des Pacs des étrangers (si né à l’étranger). Le couple peut prouver l’enregistrement par le récépissé, la mention sur l’acte de naissance ou une attestation du service central d’état civil. L’officier peut se déplacer en cas d’empêchement grave.

Sources citées :
aucune
```

### Contrôles automatiques

```text
{
  "longueur_demandee": "detaillee",
  "mots": 300,
  "plafond_mots": 400,
  "respect_longueur": true
}
```

### Verdicts

**Juge principal** : juge

- `fidelite` : 0 — Le résumé déforme plusieurs passages. « L'officier d'état civil enregistre le Pacs en personne » alors que ce sont les deux partenaires qui doivent se présenter en personne et ensemble. « Pour les tiers, il est prouvé par une mention » alors que le document parle de la date de prise d'effet à l'égard des tiers. « Le dépôt se fait sur rendez-vous, souvent avec un délai » ajoute une précision absente du document.
- `presence_elements` :
  - P1 : 0 — L'ouverture aux couples de même sexe ou de sexe différent quelle que soit la nationalité, ainsi que le recours payant au notaire, sont absents.
  - P2 : 1 — « Le Pacs doit être enregistré en mairie de la commune de résidence commune » ; la variation selon les communes est évoquée pour la pré-demande.
  - P3 : 1 — Les trois conditions et la règle de majorité pour l'étranger sont reprises, mais sans le caractère impératif ni l'absence de dispense.
  - P4 : 0 — L'engagement de vie commune, l'attestation sur l'honneur de résidence commune et l'absence d'obligation de vivre ensemble ne sont pas mentionnés.
  - P5 : 1 — Le contrat signé par les deux, en français, minimal ou personnalisé, le cerfa n°15726 et la séparation des patrimoines sont présents ; la formule légale obligatoire manque.
  - P6 : 0 — La pré-demande, le rendez-vous et le déplacement en cas d'empêchement sont présents, mais l'obligation de présence des deux partenaires est déformée en « l'officier d'état civil enregistre le Pacs en personne ».
  - P7 : 1 — Le résumé indique que l'officier ne garde pas de copie, que la convention est restituée et doit être conservée, et qu'une convention modificative est possible en cas de perte.
  - P8 : 0 — L'effet entre partenaires est présent, mais l'effet à l'égard des tiers est transformé en mode de preuve (« Pour les tiers, il est prouvé par une mention »).
  - P9 : 1 — Le récépissé, la mention sur l'acte de naissance et l'attestation du service central d'état civil sont cités ; le visa sur la convention manque.
- Inventions : L'officier d'état civil enregistre le Pacs en personne; Pour les tiers, il est prouvé par une mention sur l'acte de naissance; Le dépôt se fait sur rendez-vous, souvent avec un délai entre le dépôt du dossier et l'enregistrement
- Confiance : moyenne
