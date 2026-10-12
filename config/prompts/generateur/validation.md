---
id: validation
version: 1
tache: validation
max_tokens: 1000
---

## Consigne

Tu contrôles la fidélité d'un texte produit à sa source. Les deux textes figurent ci-dessous.

- Relève chaque affirmation du texte produit qui ne figure pas dans la source ou qui la contredit : fait, nom, date, chiffre, référence ou URL.
- Ne juge ni le style, ni la forme, ni l'exhaustivité du texte produit.
- Si tout le texte produit est appuyé par la source, réponds par le seul mot FIDELE.
- Sinon, commence par le seul mot INFIDELE sur la première ligne, puis donne une affirmation non appuyée par ligne.
- Ne donne aucune autre explication.

Source.

{source}

Texte produit.

{texte}

## Emplacements

- source : source de référence, passages, résultats d'outils ou texte de départ.
- texte : texte produit à contrôler, réponse Mistral journalisée.
