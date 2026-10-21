---
title: '15.5b — corrections des items de dev2 rejetés par la vérification croisée'
type: 'bugfix'
created: '2026-10-21'
status: 'review'
context: ['{project-root}/_bmad-output/implementation-artifacts/spec-15-5-dev2.md', '{project-root}/_bmad-output/implementation-artifacts/spec-o4d-dev1-remplacements.md', '{project-root}/_bmad-output/implementation-artifacts/spec-o4e-dev1-5-remplacements.md']
warnings: []
deferred: []
---

## Intent

**Problème :** la vérification croisée de dev2 (DeepSeek + GLM, consigne 3 neutre) donne 130 items retenus, 26 rejetés et 4 incomplets (LC-615 à LC-618, erreurs de transport). Le gel `relu-llm` exige 20 items retenus par Tâche.

**Approche :** comme O4c, O4d et O4e, lire les griefs des deux juges, puis corriger l'item (`version_item` + 1, verdict de construction 15.5b dans `verification/`) ou le remplacer (même Tâche, difficulté et thème, identifiant suivant libre, verdict `rejete` pour le remplacé). Quand un grief vise une convention commune, l'item n'est pas modifié et le grief est signalé. Les 4 incomplets ne sont pas touchés.

## Boundaries & Constraints

**Always :** items d'évaluation seulement (D1) ; faits tirés de la source citée (chunk, cassette) ; consigne CR commune conservée ; disjonction de v1.x, dev1, `data/train/v*` et des amorces seed.

**Never :** lecture d'un run de génération ou de notation ; appel payant ; plaidoyer dans un item ; changement anodin pour obtenir une nouvelle empreinte ; réécriture de `verdicts-croises.jsonl`.

## Livré

| Item | Juge, motif | Traitement |
|---|---|---|
| RD-603, RD-614, RD-617 | DeepSeek + GLM, fait absent : l'extrait ne citait que `list_dataset_resources` | Corrigés : l'extrait cite aussi `search_datasets` (titre, identifiant, producteur, URL ; jeux voisins pour 603 et 617 ; URL du ZIP `shp` pour 617) |
| RD-604, RD-606, RD-612 | DeepSeek, fait absent (même cause) | Corrigés de même (606 : jeux voisins et `Dataset ID` de `get_resource_info` ; 612 : ressource `missions-locales.csv`) |
| Q-609 | DeepSeek, incohérent : règles de création non demandées, « se faire connaître » absent de la grille | Corrigé : l'entrée demande les règles de création ; élément clé 4 complété |
| Q-612 | DeepSeek, fait absent : « sous réserve des exonérations » | Corrigé : mention retirée de la référence |
| Q-613 | DeepSeek, ambigu et fait absent : règle générale des 3 mois | Corrigé : référence et éléments 1 et 2 au plus près de F994 |
| NR-606 | DeepSeek, fait absent : « fortement recommandée » | Corrigé : extrait complété (chunk 1 de F2697) |
| LC-619 | DeepSeek, incohérent : troisième tour généralisé | Corrigé : information 3 limitée aux nominations et présentations |
| CO-618 | DeepSeek, ambigu : « reconnu » → « reconnue » ou « reconnus » | Corrigé : faute retirée (texte de la fiche rétabli), 11 fautes, positions recalculées |
| CR-619 | DeepSeek, ambigu : informations hors décisions et actions (incendie, second point, cantine) | Grief de grille (« points abordés » sans clé), non traité, signalé. Corrigé à part : 3 échéances absentes des notes deviennent « non fixée » |
| RE-602 | DeepSeek, incohérent : titres de moins de 5 ans hors consigne | Corrigé : point clé 1 ramené aux titres périmés depuis plus de 5 ans |
| RE-609 | DeepSeek, ambigu : sélection ouverte des cas, regroupement familial omis | Corrigé : la consigne nomme les cas de chaque carte, alignés sur la fiche ; point 5 complété |
| RE-611 | DeepSeek, incohérent : « sans prolongation » étendu à 2021-2022 | Corrigé : limité au 28 mai 2022-28 mai 2024 (encadré « Attention ») |
| RE-613 | DeepSeek, incohérent : époux non occupant après abandon | Corrigé : point clé 1 limité au décès |
| RE-616 | DeepSeek, incohérent : rapport à la CDAPH hors liste de la consigne | Corrigé : retiré du point clé 5 |
| RE-619 | DeepSeek, incohérent : 2 ans attribués à la personne qualifiée | Corrigé : point 4 distingue les deux suivis ; points 5 et 8 complétés |
| CO-606 | DeepSeek, incohérent : « déchéts » dans la référence (absent de l'item) | Remplacé par CO-621 (fictif, facile, collectivites, 6 fautes) |
| CO-613 | DeepSeek, incohérent : « retur », « transpore » (absents de l'item) | Remplacé par CO-622 (fictif, moyen, famille-education-sante, 8 fautes) |
| CO-615 | DeepSeek, incohérent : « prévoire » non corrigé (il l'est) | Non modifié (texte réel d'origine rétabli après revue), signalé : grief inexact, pour la décision d'Anaël |
| CO-609 | GLM, incohérent : `fictif` vrai pour un texte réel | Non modifié, signalé : convention G4 commune aux 14 CO réels (13 retenus) |
| CT-602 | DeepSeek, fait absent : formules d'appel et de politesse | Non modifié, signalé : format administratif commun aux 20 CT (17 retenus) |
| CT-612 | DeepSeek, ambigu : « plusieurs rédactions possibles » | Non modifié, signalé : rédaction ouverte, propre à la Tâche CT |
| CT-614 | DeepSeek, ambigu : formule de politesse non précisée | Non modifié, signalé : même convention que CT-602 |

Causes communes :
- RD (6 sur 6) : l'extrait de provenance ne citait que le dernier appel, alors que la référence reprend les métadonnées de `search_datasets`. Deux extraits omettaient aussi des lignes sans `[…]` (606, 614) : corrigé.
- RE (6) et Q (3) : la référence ou les points clés débordaient de la consigne ou de la lettre de la fiche.
- CO (3 : 606, 613, 615) : griefs inexacts de DeepSeek. Les fautes ou corrections citées n'existent pas dans l'item.

Contrôles :
- `construire_jeu.py assembler --version dev2` : 155 items, SHA-256 `280ce30b…`, 2 exclus par `verification/` (606, 613) et 5 par les verdicts croisés (CO-609, CO-615, CT-602, CT-612, CT-614).
- `slmsp eval gel --version dev2 --verifier-seulement` : 155 items stricts, 0 erreur bloquante. Restent 4 écarts de composition (CO moyen 6, CO difficile 5, CT facile 6, CT moyen 5), dus aux 5 items signalés.
- `verifier_jeu_croise.py disjonction --version dev2 --reference <dépôt principal>` : disjoint.
- Les segments des 6 extraits RD ont été relus dans les cassettes, blancs normalisés.

## Auto Run Result

Statut : review. Tests ciblés `tests/eval_outils` et `tests/evaluation` avec `SLMSP_EVAL_SOURCES` : 1572 passés.

Revérification par l'orchestrateur (payante) : `python eval/outils/verifier_jeu_croise.py verifier --version dev2 --juges deepseek,glm`. Il n'existe pas d'option de ciblage. L'outil reprend les verdicts à empreinte et consigne égales : seuls les 21 items à empreinte nouvelle (19 corrigés et 2 neufs) sont appelés par les deux juges, et les 4 incomplets par le juge sans verdict, soit environ 50 appels et 0,3 $. Suivent `construire_jeu.py assembler --version dev2`, puis le gel `relu-llm`.

Décisions prises seul :
- Un grief factuellement inexact ne peut pas être corrigé honnêtement. L'item est remplacé, pas retouché pour changer d'empreinte. Les 2 CO neufs (621, 622) remplacent des textes déjà fictifs : c'est plus simple, et aucune cible de composition ne fixe le nombre de CO réels.
- CR-619 : les 3 échéances inférées sont un défaut réel, trouvé en relisant l'item, et elles sont corrigées. Le grief du juge, lui, n'est pas traité.

À confirmer par Anaël (orchestrateur) :
- CO-609, CO-615, CT-602, CT-612 et CT-614 : items non modifiés (CO-615 : grief inexact, texte réel d'origine rétabli ; les quatre autres : convention commune). Trois issues possibles : relance en l'état, comme les 6 CR de dev1 en O4d ; exclusion avec cibles abaissées, comme CR-521 de dev1 ; ou remplacement. Tant que rien n'est décidé, le gel `relu-llm` échoue sur CO (18) et CT (17).
- CR-619 : si le grief « points abordés » revient, appliquer la décision prise pour dev1.

## Revue

| Sévérité | Source | Constat | Traitement |
|---|---|---|---|
| medium | second avis, orchestrateur | CR-619 : grief « points abordés » de la grille commune | Rejeté : consigne CR commune conservée (décision d'Anaël pour dev1) ; à revérifier, exclu sur décision d'Anaël comme CR-521 s'il reste rejeté |
| high | second avis, orchestrateur | RE-609 : la consigne demandait des cas absents de F11892 (départ de France pour la carte temporaire, travail sans autorisation pour la carte de résident) | Corrigé : la consigne liste les cas de chaque carte comme la fiche et les points clés |
| medium | second avis, orchestrateur | RD-606 : l'extrait omettait `list_dataset_resources` | Corrigé : segment ajouté, relu dans la cassette ; verdict 15.5b complété |
| high | orchestrateur | CO-615 (texte réel) remplacé par un texte fictif (CO-623) pour un grief inexact, contre la convention G4 | Corrigé : CO-615 d'origine rétabli, CO-623 retiré (item, verdicts) ; CO-615 laissé à la décision d'Anaël |
| medium | revue | RE-619 point 8 : distinction capable / non capable de discernement et « systématiquement » perdus | Corrigé : rétablis |
| low | revue | Réassemblage : 155 items, gel strict 0 erreur, disjonction OK | Vérifié |
