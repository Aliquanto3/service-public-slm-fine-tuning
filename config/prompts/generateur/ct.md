---
id: ct
version: 2
tache: CT
max_tokens: 800
---

## Consigne

Tu rédiges un courrier administratif du type indiqué ci-dessous, à partir de son objet et des éléments connus fournis par un Agent du service public.

- Utilise seulement les éléments connus. N'invente aucun nom, aucune date, aucune référence, aucun montant et aucune adresse.
- Pour chaque information nécessaire au courrier qui manque, place un emplacement entre crochets qui nomme l'information à compléter.
- Respecte les usages du courrier administratif français : lieu et date, objet, formule d'appel, corps structuré, formule de politesse, signature.
- Adopte un ton courtois, neutre et précis.
- Donne seulement le courrier.
- Ta réponse ne dépasse pas {plafond_mots_tache} mots.
- Commence directement par le contenu : pas de titre ni d'intertitre en première ligne, pas de phrase d'annonce ou d'introduction.

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
