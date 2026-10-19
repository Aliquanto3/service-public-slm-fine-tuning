---
id: ct
version: 3
tache: CT
max_tokens: 800
---

## Consigne

Tu rédiges un courrier administratif du type indiqué ci-dessous, à partir de son objet et des éléments connus fournis par un Agent du service public.

- Utilise seulement les éléments connus. N'invente aucun nom, aucune date, aucune référence, aucun montant et aucune adresse.
- Respecte le format complet du courrier administratif français, avec ces blocs dans cet ordre : expéditeur, destinataire, lieu et date, objet, références, formule d'appel, corps, formule de politesse, signature.
- Écris la ligne de l'objet en la commençant par le mot Objet suivi de deux points.
- Chaque information nécessaire au courrier qui ne figure pas dans les éléments connus est remplacée par un emplacement entre crochets qui nomme le champ à compléter. Ne donne jamais de valeur inventée à la place.
- Quand aucune référence n'est connue, le bloc des références porte un emplacement entre crochets.
- Structure le corps en paragraphes courts : le contexte, l'objet de la demande ou de la décision, puis les suites à donner.
- Termine par une formule de politesse administrative complète, puis par le bloc de signature.
- Adopte un ton courtois, neutre et précis.
- Donne seulement le courrier.
- Ta réponse ne dépasse pas {plafond_mots_tache} mots.
- Commence directement par le bloc de l'expéditeur : pas de titre, pas de phrase d'annonce ou d'introduction.

Type de courrier.

{type_courrier}

Objet du courrier.

{objet}

Éléments connus.

{elements_connus}

## Emplacements

- type_courrier : type de courrier à rédiger, issu d'un jeu public ou d'une réponse Mistral journalisée.
- objet : objet du courrier, issu d'un jeu public ou d'une réponse Mistral journalisée.
- elements_connus : éléments connus à reprendre, issus d'un jeu public ou d'une réponse Mistral journalisée.
- plafond_mots_tache : plafond de mots de la réponse pour la tâche du gabarit, lu dans la table generateur.plafonds_mots de config/donnees.toml (consigne de longueur, jamais une amorce).
