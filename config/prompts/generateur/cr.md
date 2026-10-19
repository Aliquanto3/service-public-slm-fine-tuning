---
id: cr
version: 2
tache: CR
max_tokens: 1600
---

## Consigne

Tu rédiges le compte rendu de la réunion dont un Agent du service public te transmet la transcription ci-dessous.

- Rapporte seulement ce qui figure dans la transcription : n'ajoute aucun fait, aucun nom, aucune date et aucun chiffre.
- Structure le compte rendu : objet de la réunion et participants, points abordés, décisions prises, actions à mener avec leur responsable et leur échéance quand elles sont indiquées.
- Écris des phrases complètes, dans un style neutre et administratif.
- Signale les points ambigus ou incomplets au lieu de les compléter.
- Donne seulement le compte rendu.
- Ta réponse ne dépasse pas {plafond_mots_tache} mots.
- Commence directement par le contenu : pas de titre ni d'intertitre en première ligne, pas de phrase d'annonce ou d'introduction.

Transcription de la réunion.

{transcription}

## Emplacements

- transcription : transcription de la réunion, réponse Mistral journalisée du gabarit transcription-cr.
- plafond_mots_tache : plafond de mots de la réponse pour la tâche du gabarit, lu dans la table generateur.plafonds_mots de config/donnees.toml (consigne de longueur, jamais une amorce).
