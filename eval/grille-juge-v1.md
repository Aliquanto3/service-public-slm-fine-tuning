---
title: Grille du Juge
version: 1.0
status: validé par Anaël le 2026-10-12 (v1.0) ; items à challenger plus tard par un agent public réel
applique: PRD §10.1 (Score de Tâche 0–100), FR-39
---

# Grille du Juge, v1

## Principes communs
- **Questions fermées.** Le Juge note critère par critère sur une échelle courte, ancrée par des exemples. Il ne donne jamais de note globale « au ressenti ».
- **Une justification par critère.** Chaque note s'accompagne d'une justification d'une phrase, qui cite le passage fautif quand il y en a un.
- **Doute = note basse.** Une information impossible à vérifier contre l'entrée ou les références compte comme une invention.
- **Pas de bonus de longueur.** Une réponse plus longue n'est jamais mieux notée pour sa longueur (SM-C4).
- **Contrôles automatiques à part.** Les critères vérifiables par programme (URL, schéma d'appel, lisibilité, fautes, emplacements) sont calculés par le banc, pas par le Juge.

Format de sortie du Juge, par item :

```json
{"id": "Q-001", "criteres": {"exactitude": {"note": 2, "justification": "…"}}, "inventions": ["…"], "confiance": "haute | moyenne | basse"}
```

## Q : Question

| Critère | Échelle | Ancrage |
|---|---|---|
| Exactitude | 0 / 1 / 2 | **2** : tous les `elements_cles` sont présents et justes, sans erreur. **1** : un élément clé manque ou est imprécis, sans erreur grave. **0** : erreur factuelle, contradiction avec la source, ou au moins deux éléments clés manquants. |
| Pertinence de la source | 0 / 1 | **1** : au moins une source citée (déjà vérifiée par le banc dans les passages retrouvés) traite bien du point demandé. **0** : les sources citées sont hors sujet. |
| Cas « sans réponse » | 0 / 1 | Ce critère ne s'applique que si `sans_reponse` est vrai. **1** : l'Assistant dit ne pas avoir trouvé de Source officielle et oriente, conformément à `orientation_attendue`. **0** : il invente une réponse. |

**Score de l'item** : il est réussi si Exactitude = 2 **et** Pertinence = 1 **et** aucune URL n'est inventée (contrôle automatique du banc). Pour un item sans réponse, il est réussi si le critère « Cas sans réponse » vaut 1. Score de Tâche = % d'items réussis.

## RD : Recherche de données (automatique, le Juge n'intervient qu'en cas de litige)

| Composante | Calcul |
|---|---|
| Appel valide | % d'appels conformes au schéma et au bon outil, d'après `appels_attendus` |
| Réponse exacte | % d'items où les jeux cités ou les valeurs affichées correspondent aux cassettes (correspondance exacte des identifiants de jeux ; valeurs numériques identiques) |

**Score de Tâche** = moyenne des deux. Si le libellé d'un jeu est correct mais que son identifiant est absent, le cas est soumis au Juge (0 ou 1).

## CR : Compte rendu

| Critère | Échelle | Ancrage |
|---|---|---|
| Couverture | rappel de 0 à 1 | Part des `decisions_reference` et `actions_reference` présentes dans le compte rendu. Une action sans son responsable ou son échéance (quand ils sont connus) compte pour moitié. |
| Absence d'invention | 0 / 1 | **1** : aucune décision, action, personne, date ou chiffre absent des notes. **0** : au moins une invention, y compris un élément de `pieges` présenté comme décidé. |
| Structure | 0 / 1 | **1** : les quatre sections sont présentes (Participants, Points abordés, Décisions, Actions). Ce critère est rapporté, mais n'entre pas dans le score. |

**Score de Tâche** = moyenne de (couverture moyenne × 100) et (% de comptes rendus sans invention).

## LC : Langage clair

| Critère | Échelle | Ancrage |
|---|---|---|
| Fidélité | 0 / 1 / 2 | **2** : sens intact, et tous les `informations_a_conserver` sont présents et exacts. **1** : nuance perdue sans conséquence pratique. **0** : montant, date, condition ou obligation modifié ou supprimé, ou ajout d'une information. |
| Termes juridiques | 0 / 1 | **1** : les `termes_juridiques_a_conserver` sont conservés, ou expliqués sans être remplacés à tort. |
| Clarté perçue | 1 à 5 | Ce critère est rapporté, mais n'entre pas dans le score. **5** : un Usager sans connaissance administrative comprend du premier coup. |

**Lisibilité (automatique)** : gain de Kandel-Moles = indice de la sortie − indice de l'entrée.

**Score de Tâche** = % d'items avec Fidélité = 2 et Termes = 1, **à condition** que le gain moyen de Kandel-Moles soit d'au moins +10. Sinon, le score est plafonné à 50 et signalé.

## CO : Correction (automatique)

| Composante | Calcul |
|---|---|
| Rappel | Fautes de `fautes` corrigées ÷ fautes injectées |
| Modifications hors faute | Mots modifiés hors des positions de faute ÷ nombre de mots du texte. Les reformulations de ponctuation typographique tolérées sont exclues. |

**Score de l'item** = rappel × (1 − taux hors faute). **Score de Tâche** = moyenne × 100.

## RE : Résumé

| Critère | Échelle | Ancrage |
|---|---|---|
| Fidélité | 0 / 1 | **1** : aucune information absente du document ni déformée. |
| Couverture | rappel de 0 à 1 | Part des `points_cles_reference` présents. |
| Respect de la longueur | 0 / 1 | Courte : 80 mots au plus. Moyenne : 200 mots au plus. Détaillée : 400 mots au plus. Ce critère est rapporté, mais n'entre pas dans le score. |

**Score de Tâche** = moyenne de (% de résumés fidèles) et (couverture moyenne × 100).

## CT : Courrier type

| Critère | Échelle | Ancrage |
|---|---|---|
| Conformité | 0 / 1 / 2 | **2** : tous les `elements_obligatoires` sont présents, et le format administratif français est respecté (expéditeur, destinataire, objet, références, formule d'appel, corps, formule de politesse, signature). **1** : un élément manque. **0** : au moins deux éléments manquent, ou le registre est inadapté. |
| Emplacements (automatique) | 0 / 1 | **1** : chaque champ de `champs_a_laisser_en_emplacement` apparaît comme [Emplacement], et aucune valeur n'est inventée. |

**Score de Tâche** = moyenne de (Conformité ÷ 2 × 100) et (% d'emplacements réussis).

## NR : Non-régression

| Critère | Échelle | Ancrage |
|---|---|---|
| Exactitude | 0 / 1 | Questions : **1** si la réponse est juste. Consignes de rédaction : **1** si tous les `criteres` sont respectés. |

**Score de Tâche** = % exacts.

## Prompt du Juge (gabarit)

> Tu évalues la sortie d'un assistant pour agents publics, sur la Tâche {tache}. Applique strictement la grille ci-dessous, critère par critère. Tu ne connais pas l'identité du système évalué. Considère comme une invention toute information que tu ne peux pas vérifier dans l'ENTRÉE ou dans les RÉFÉRENCES. Ne récompense jamais la longueur. Réponds uniquement en JSON, selon le schéma fourni.
>
> GRILLE : {section de la Tâche}
> ENTRÉE : {entree}
> RÉFÉRENCES : {champs de référence}
> SORTIE À ÉVALUER : {sortie}
