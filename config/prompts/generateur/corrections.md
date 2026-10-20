---
id: corrections
version: 1
tache: verification
---

## Consigne

Phrases fixes de l'outillage, une par code de motif de refus (contrôles déterministes de slmsp.data.verification, critères du juge de données préfixés par juge_). Le Générateur en compose l'emplacement corrections des gabarits de correction : la phrase de chaque code refusé, puis les passages vérifiés (sous-chaînes exactes) de la réponse refusée ou de la source ; aucun texte libre du juge n'y entre. Ce sont des consignes ; aucune ne donne une formulation de réponse.

## Emplacements

- libelle_extraits : Passages concernés
- url_inventee : N'écris aucune adresse web qui ne figure pas dans le texte fourni.
- valeur_absente : N'écris aucun nombre, aucune date, aucun montant et aucune référence qui ne figurent pas dans le texte fourni.
- lc_valeur_perdue : Reprends tous les montants, toutes les dates, toutes les durées et toutes les références du texte, avec leurs valeurs exactes.
- cr_sections_manquantes : Donne les quatre sections Participants, Points abordés, Décisions et Actions, chacune ouverte par son titre seul sur sa ligne.
- cr_sections_desordre : Présente les quatre sections dans l'ordre Participants, Points abordés, Décisions, Actions.
- cr_plafond_mots : Respecte le plafond de mots fixé par la consigne.
- cr_actions_vide : Remplis la section Actions avec une action par ligne, ou indique en une phrase qu'aucune action n'a été décidée.
- ct_format_incomplet : Donne tous les blocs du courrier administratif, dont la ligne d'objet ouverte par le mot Objet suivi de deux points et la formule de politesse.
- ct_blocs : Présente les blocs du courrier dans l'ordre demandé, du lieu et de la date jusqu'à la signature.
- ct_sans_emplacement : Remplace chaque information inconnue par un emplacement entre crochets qui nomme le champ à compléter.
- lc_modalite_perdue : Garde chaque condition, restriction, obligation, permission, interdiction et échéance du texte.
- lc_modalite_reduite : Garde toutes les conditions, restrictions, obligations, permissions, interdictions et échéances du texte, sans en omettre.
- lc_conseil_ajoute : N'ajoute aucun conseil ni aucune recommandation absents du texte.
- lc_titre : Commence directement par le contenu, sans titre en première ligne.
- lc_gain_lisibilite : Rends le texte nettement plus facile à lire que l'original, avec des phrases plus courtes et des mots plus courants, sans perdre de sens.
- nom_absent : N'écris aucun nom de personne, de lieu ou d'organisme qui ne figure pas dans le texte fourni.
- juge_invention : Retire toute information absente du texte fourni.
- juge_structure : Respecte la structure demandée par la consigne.
- juge_couverture : Reprends toutes les décisions et toutes les actions de la transcription.
- juge_fidelite : Rends exactement le sens du texte, droits, obligations, conditions, délais et montants compris, sans en changer la portée.
- juge_termes : Garde les termes juridiques du texte et explique chacun en quelques mots.
- juge_conformite : Respecte le format complet du courrier administratif demandé.
