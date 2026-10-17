---
id: re
version: 1
tache: RE
max_tokens: 1500
---

## Consigne

Tu résumes pour un Agent du service public le texte administratif ci-dessous.

- Garde l'essentiel : objet, décisions, obligations, délais, montants et personnes concernées.
- Rapporte seulement ce qui figure dans le texte : n'ajoute aucune information et ne donne aucun avis.
- Respecte la longueur indiquée ci-dessous : le résumé ne dépasse pas {plafond_mots} mots.
- Écris en français, de façon claire et neutre.
- Donne seulement le résumé.

Longueur du résumé.

{longueur_demandee}

Texte à résumer.

{texte}

## Emplacements

- longueur_demandee : longueur du résumé, issue d'un jeu public ou d'une réponse Mistral journalisée.
- texte : texte administratif, issu d'un jeu public.
- plafond_mots : nombre maximal de mots du résumé, dérivé de la longueur demandée par la configuration.
