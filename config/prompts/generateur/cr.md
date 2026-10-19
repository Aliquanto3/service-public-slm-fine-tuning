---
id: cr
version: 3
tache: CR
max_tokens: 1600
---

## Consigne

Tu rédiges le compte rendu de la réunion dont un Agent du service public te transmet la transcription ci-dessous.

- Rapporte seulement ce qui figure dans la transcription : n'ajoute aucun fait, aucun nom, aucune date et aucun chiffre.
- Organise le compte rendu en quatre sections, dans cet ordre, chacune ouverte par son titre seul sur sa ligne : Participants, Points abordés, Décisions, Actions.
- Dans la section Participants, nomme les personnes et les services présents tels que la transcription les désigne.
- Dans la section Points abordés, résume chaque sujet discuté en une ou deux phrases.
- Dans la section Décisions, reprends toutes les décisions prises pendant la réunion, une par ligne. Un point discuté sans décision n'y figure pas et n'est jamais présenté comme décidé.
- Dans la section Actions, reprends toutes les actions à mener, une par ligne, chacune avec son responsable et son échéance quand la transcription les donne. Quand l'un ou l'autre manque, indique qu'il n'est pas précisé, sans le deviner.
- Quand la transcription ne contient aucune décision ou aucune action, garde la section et indique-le en une phrase.
- Écris dans un style neutre et administratif.
- Signale les points ambigus ou incomplets au lieu de les compléter.
- Donne seulement le compte rendu.
- Ta réponse ne dépasse pas {plafond_mots_tache} mots.
- Commence directement par le titre de la section Participants : pas de titre général, pas de phrase d'annonce ou d'introduction.

Transcription de la réunion.

{transcription}

## Emplacements

- transcription : transcription de la réunion, réponse Mistral journalisée du gabarit transcription-cr.
- plafond_mots_tache : plafond de mots de la réponse pour la tâche du gabarit, lu dans la table generateur.plafonds_mots de config/donnees.toml (consigne de longueur, jamais une amorce).
