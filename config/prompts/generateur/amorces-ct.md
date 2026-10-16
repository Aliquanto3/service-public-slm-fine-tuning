---
id: amorces-ct
version: 1
tache: CT
max_tokens: 800
---

## Consigne

Tu prépares la demande qu'un Agent du service public adresserait à un assistant pour faire rédiger un courrier administratif. La demande porte sur une situation plausible en lien avec le sujet de démarche indiqué ci-dessous. Tu ne rédiges pas le courrier lui-même.

- type_courrier : la nature du courrier, en quelques mots.
- objet : l'objet du courrier, en une phrase courte.
- elements_connus : les faits que l'Agent connaît déjà, en deux à six phrases ou lignes. Ils doivent suffire à rédiger le courrier sans le compléter entièrement : certaines informations peuvent manquer.
- Varie la nature du courrier, le destinataire et la situation d'une demande à l'autre.
- Tous les noms de personnes, d'organismes locaux, d'adresses, de dates et de références sont manifestement fictifs. N'utilise aucune donnée personnelle réelle.
- Écris en français, dans un registre administratif.
- Réponds par un seul objet JSON, sans texte avant ni après et sans bloc de code. Il contient exactement les trois clés type_courrier, objet et elements_connus, dont chaque valeur est une chaîne de caractères non vide.

Sujet de démarche.

{sujet}

## Emplacements

- sujet : sujet de démarche administrative, issu d'un jeu public.
