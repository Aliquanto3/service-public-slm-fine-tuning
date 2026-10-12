# Relecture des verdicts

2 item(s) de l'échantillon de relecture. Les Scores restent « non relus » tant que `relecture-validee.json` (objet JSON avec une clé `date` ISO) n'est pas déposé dans ce run.

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
