---
id: lc-correction
version: 1
tache: LC
max_tokens: 800
---

## Consigne

Tu réécris en langage clair le texte administratif ci-dessous, pour que la personne qui le reçoit le comprenne dès la première lecture.

- Conserve tout le sens du texte : droits, obligations, conditions, démarches, délais, montants et références.
- Reprends tous les montants, toutes les dates, toutes les durées et toutes les références du texte, avec leurs valeurs exactes.
- N'ajoute aucune information absente du texte : ni fait, ni chiffre, ni date, ni démarche, ni coordonnée, ni conseil.
- Garde les termes juridiques du texte : explique-les en quelques mots, sans les remplacer.
- Écris des phrases courtes avec des mots courants, à la voix active.
- Adresse-toi directement au lecteur quand le texte s'y prête.
- Donne seulement le texte réécrit.
- Ta réponse ne dépasse pas {plafond_mots_tache} mots.
- Commence directement par le contenu : pas de titre ni d'intertitre en première ligne, pas de phrase d'annonce ou d'introduction.

Texte à réécrire.

{texte}

Une réponse précédente à cette demande a été refusée par les contrôles de l'outillage. Rédige une nouvelle réponse complète, qui respecte toutes les consignes ci-dessus et corrige chacun des points suivants.

{corrections}

## Emplacements

- texte : texte administratif, issu d'un jeu public.
- plafond_mots_tache : plafond de mots de la réponse pour la tâche du gabarit, lu dans la table generateur.plafonds_mots de config/donnees.toml (consigne de longueur, jamais une amorce).
- corrections : points à corriger, rendus par le Générateur depuis les motifs de refus structurés (phrases fixes de corrections.md, passages de la réponse refusée ou de la source, sous-chaînes exactes) ; aucun texte libre du juge de données ; jamais une amorce du seed.
