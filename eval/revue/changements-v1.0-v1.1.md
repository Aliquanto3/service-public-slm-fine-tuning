# Changements du Jeu d'évaluation v1.1 par rapport à v1.0

- Comparaison : `eval/jeu/v1.0/items.jsonl` (référence gelée) et `eval/jeu/v1.1/items.jsonl` (assemblé, non gelé).
- Items nouveaux : 3 ; modifiés : 16 ; retirés : 3.
- Valeurs complètes : `eval/revue/changements-v1.0-v1.1.jsonl`.

# Items nouveaux (3)

## Q-068 — Question (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : F23371 « Quels sont les seuils de publicité des marchés publics ? » (entreprendre.service-public.gouv.fr/vosdroits/F23371), parquet rév. 29f236f8a5 : les 3 segments de l'extrait figurent mot pour mot dans les chunks 2 et 6 (avis obligatoire à partir de 60 000 € HT pour fournitures ou services, 100 000 € HT pour travaux, dans l'en-tête de chaque chunk ; avis non obligatoire sous 60 000 € et sous 100 000 € pour les travaux au chunk 2 ; « marchés de services inférieurs à 60 000 € HT sans publicité et ni mise en concurrence » au chunk 6). Le chunk 6 cite l'entretien de locaux comme exemple de marché de services, donc le nettoyage relève bien des services. Fiche présente dans l'Index 20260926 (6 chunks, même doc_id et même URL, textes identiques une fois les espaces normalisés). Fiche différente de F33466 et F32213 ; absente du calibrage ; pas de doublon avec RE-009, RE-013 ni les autres items retenus. Gabarit conforme. Difficulté facile cohérente (une fiche, réponse directe). Réserve mineure : le tableau du chunk 6 (autre pouvoir adjudicateur) prévoit une publicité libre ou adaptée de 60 000 à 89 999,99 € et une publicité obligatoire au BOAMP ou dans un Shal à partir de 90 000 €. Une réponse qui ajoute cette nuance est juste ; une réponse « avis obligatoire à partir de 90 000 € » serait fausse, puisque la fiche dit explicitement 60 000 € pour l'avis de marché. L'entrée reprend ce terme, donc pas d'ambiguïté bloquante.

**entree** : Notre commune veut confier le nettoyage de ses locaux à une entreprise, pour un montant estimé à 45 000 € HT. Doit-elle publier un avis de marché ? À partir de quel montant l'avis de marché devient-il obligatoire pour un marché de services, et pour un marché de travaux ?

**parametres** : {}

**reponse_reference** : Non, pas pour ce montant : l'avis de marché n'est pas obligatoire pour les marchés de fournitures et de services d'un montant inférieur à 60 000 €, et l'acheteur public peut même passer un marché de services inférieur à 60 000 € HT sans publicité ni mise en concurrence. L'acheteur public doit publier un avis de marché pour les marchés de fournitures ou de services d'un montant égal ou supérieur à 60 000 € HT. Ce seuil est porté à 100 000 € HT pour les marchés de travaux. Ne vaut pas avis juridique.

### elements_cles

- Pas d'avis de marché obligatoire pour ce marché de services de 45 000 € HT : il peut même être passé sans publicité ni mise en concurrence (moins de 60 000 € HT)
- Avis de marché obligatoire pour les marchés de fournitures ou de services à partir de 60 000 € HT
- Seuil porté à 100 000 € HT pour les marchés de travaux

### sources_attendues

- https://entreprendre.service-public.gouv.fr/vosdroits/F23371

**sans_reponse** : false

**mention_obligatoire** : Ne vaut pas avis juridique

### provenance

-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F23371 « Quels sont les seuils de publicité des marchés publics ? »
  - **url** : https://entreprendre.service-public.gouv.fr/vosdroits/F23371
  - **chunks** :
    - 2
    - 6
  - **extrait** : L’acheteur public doit publier un avis de marché pour les marchés de fournitures ou de services d’un montant égal ou supérieur à 60 000 € HT. Ce seuil est porté à 100 000 € HT pour les marchés de travaux. […] L’avis de marché n’est pas obligatoire pour les marchés de fournitures et de services d’un montant inférieur à 60 000 € et pour les marchés de travaux de moins de 100 000 € . […] L’acheteur public a la possibilité de passer les marchés de services inférieurs à 60 000 € HT sans publicité et ni mise en concurrence.
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-13

**licence_source** : Fiche : Licence Ouverte / Etalab 2.0.

**fictif** : false

**version_item** : 1

## Q-069 — Question (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : F32049 « Quelles sont les différentes procédures de marchés publics ? » (entreprendre.service-public.gouv.fr/vosdroits/F32049), parquet rév. 29f236f8a5 : les 5 segments de l'extrait figurent mot pour mot dans les chunks 6, 7 et 10. Définition du MAPA (entre 60 000 € et les seuils de procédure formalisée), liberté de l'acheteur dans le respect de l'égalité de traitement, de la transparence et de l'égalité d'accès, et, « À partir du 21 août 2026 », clause environnementale et critère environnemental pour un MAPA : chunk 6. Seuils de 5 404 000 € HT (travaux) et 216 000 € HT (fournitures ou services des collectivités locales) : chunk 7. Procédure formalisée obligatoire à partir de 216 000 € HT pour une collectivité territoriale et de 5 404 000 € HT pour les travaux : chunk 10. Un département est une collectivité territoriale, donc 216 000 € s'applique ; F23371 donne la même valeur pour un « autre pouvoir adjudicateur ». 180 000 € et 2 M€ relèvent bien du MAPA. Pas d'autre réponse plausible : l'obligation propre à la procédure formalisée (clause environnementale, critère environnemental et clause sociale, chunk 10) et la clause seule du gré à gré (chunk 2) ne s'appliquent pas ici. Fiche présente dans l'Index 20260926 (13 chunks identiques au parquet). Fiche différente de F33466 et F32213 ; absente du calibrage ; pas de doublon avec RE-009 ni RE-013. Recoupement partiel avec Q-070 (seuil de 216 000 € rappelé en appui) et avec Q-068 (60 000 €), mais la question centrale diffère (choix de procédure et obligation environnementale). Gabarit conforme. Difficulté moyen cohérente (deux marchés, deux seuils, obligation datée).

**entree** : Notre département prépare deux achats : un marché de fournitures (mobilier pour les collèges) estimé à 180 000 € HT et un marché de travaux (réfection d'une route départementale) estimé à 2 millions d'euros HT. Quelle procédure de passation s'applique à chacun, à partir de quels montants la procédure formalisée deviendrait-elle obligatoire, et quelle obligation environnementale s'impose depuis août 2026 dans ce cas ?

**parametres** : {}

**reponse_reference** : Les deux marchés relèvent de la procédure adaptée (MAPA), dont le montant hors taxes est compris entre 60 000 € et les seuils de procédure formalisée : 216 000 € HT pour les marchés de fournitures ou de services des collectivités locales, et 5 404 000 € HT pour les marchés de travaux. Pour un MAPA, l'acheteur public est libre de définir ses propres règles dans le respect des principes généraux de la commande publique (égalité de traitement des candidats, transparence des procédures, égalité d'accès à la commande publique). La procédure formalisée deviendrait obligatoire à partir de 216 000 € HT pour les fournitures et à partir de 5 404 000 € HT pour les travaux. Depuis le 21 août 2026, pour un marché en procédure adaptée, l'acheteur doit prévoir une clause environnementale et un critère environnemental. Ne vaut pas avis juridique.

### elements_cles

- Les deux marchés relèvent d'une procédure adaptée (MAPA) : montant compris entre 60 000 € et les seuils de procédure formalisée
- Seuil de procédure formalisée pour les fournitures ou services d'une collectivité territoriale : 216 000 € HT
- Seuil de procédure formalisée pour les travaux : 5 404 000 € HT
- En MAPA, l'acheteur définit librement ses règles dans le respect des principes de la commande publique (égalité de traitement, transparence, égalité d'accès)
- Depuis le 21 août 2026, un MAPA doit prévoir une clause environnementale et un critère environnemental

### sources_attendues

- https://entreprendre.service-public.gouv.fr/vosdroits/F32049

**sans_reponse** : false

**mention_obligatoire** : Ne vaut pas avis juridique

### provenance

-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F32049 « Quelles sont les différentes procédures de marchés publics ? »
  - **url** : https://entreprendre.service-public.gouv.fr/vosdroits/F32049
  - **chunks** :
    - 6
    - 7
    - 10
  - **extrait** :
    ```text
    Le MAPA (ou marché à procédure adaptée) est un marché dont le montant hors taxes est compris entre 60 000 € et les seuils de procédure formalisée. Chaque acheteur public est libre de définir ses propres règles dans le respect des principes généraux de la commande publique (égalité de traitement des candidats, transparence des procédures, égalité d'accès à la commande publique). […] À partir du 21 août 2026 , pour un marché en procédure adaptée (MAPA), l’acheteur doit prévoir une clause environnementale et un critère environnemental . […] Les procédures sont adaptées pour des marchés dont le montant est situé entre 60 000 € et les seuils de procédure formalisée suivants :
    - 5 404 000 € HT pour les marchés publics de travaux (État et collectivités locales)
    - 140 000 € HT pour les marchés publics de fournitures ou de services de l’État
    - 216 000 € HT pour les marchés public de fournitures ou de services des collectivités locales
    - 432 000 € HT pour les marchés publics de fournitures ou de services des opérateurs de réseaux , services de défense ou de sécurité
    Au-delà de ces seuils, la procédure formalisée s'applique. […] Marchés publics de fournitures et de services passés par une collectivité territoriale ou un établissement public de santé d'un montant égal ou supérieur à 216 000 € HT […] Marchés publics de travaux d'un montant égal ou supérieur à 5 404 000 € HT
    ```
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-13

**licence_source** : Fiche : Licence Ouverte / Etalab 2.0.

**fictif** : false

**version_item** : 1

## Q-070 — Question (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Les 7 segments de l'extrait figurent mot pour mot dans les chunks cités du parquet rév. 29f236f8a5. F23371 : BOAMP (MAPA et procédures formalisées) et JOUE (procédures formalisées) au chunk 3 ; ligne de tableau « À partir de 216 000 € | Publicité obligatoire au BOAMP et au JOUE pour une procédure formalisée » au chunk 6. F32049 chunk 11 : appel d'offres ouvert, 30 jours si transmission électronique, 15 jours en cas d'urgence ; appel d'offres restreint pour un pouvoir adjudicateur, 30 jours pour les candidatures (au moins 15 jours en cas d'urgence) puis 30 jours pour les offres à compter de l'invitation à soumissionner. Les 25 jours en cas de transmission électronique et les 10 jours en cas d'urgence pour les offres sont aussi au chunk 11 (« Le pouvoir adjudicateur peut ramener ce délai minimal à 25 jours si les offres sont ou peuvent être transmises par voie électronique »). Le classement de la commune comme pouvoir adjudicateur repose sur F23371 chunk 6 (« un autre pouvoir adjudicateur (collectivité territoriale ou un établissement public) »). Un marché de services informatiques de 300 000 € HT dépasse 216 000 €, ce qui est cohérent. Les deux fiches sont dans l'Index 20260926 avec des textes identiques au parquet ; sources_attendues = les 2 URL. Fiches différentes de F33466 et F32213 ; absentes du calibrage ; pas de doublon avec RE-013, qui porte sur le rejet des offres, le standstill et les recours. Gabarit conforme. Difficulté difficile cohérente (2 fiches, 3 sous-questions, distinction pouvoir adjudicateur / entité adjudicatrice). Réserves mineures : (1) l'extrait n'inclut pas la phrase des 25 jours, qui est un élément clé, ni celle qui classe la collectivité territoriale comme « autre pouvoir adjudicateur » ; elles pourraient y être ajoutées (facultatif, ces faits sont dans les chunks 11 et 6 cités) ; (2) une réponse qui ajoute la publication sur le profil acheteur (F23371 chunk 3 : chaque acheteur en dispose pour publier ses avis) est juste et ne doit pas être pénalisée ; (3) la fiche indique que le dépôt électronique est aujourd'hui la règle, donc une réponse qui donne directement 25 jours pour les offres en appel d'offres restreint est acceptable.

**entree** : Notre commune passe un marché de services informatiques estimé à 300 000 € HT, en procédure formalisée. Sur quels supports l'avis de marché doit-il être publié ? Si elle choisit un appel d'offres ouvert avec dépôt électronique, quel délai minimal doit-elle laisser aux candidats à compter de l'envoi de l'avis, et ce délai peut-il être réduit en cas d'urgence ? Si elle choisit plutôt un appel d'offres restreint, quels délais minimaux s'appliquent à la remise des candidatures, puis des offres ?

**parametres** : {}

**reponse_reference** : L'avis de marché doit être publié au BOAMP et au JOUE : le BOAMP reçoit les avis des procédures formalisées et le JOUE les annonces légales des marchés à procédure formalisée ; pour un marché de services passé par une commune (pouvoir adjudicateur), cette publicité est obligatoire à partir de 216 000 € HT, ce qui est le cas à 300 000 € HT. En appel d'offres ouvert, la candidature et l'offre sont remises en même temps ; le délai est de 30 jours à compter de l'envoi de l'avis de marché si les candidatures et les offres sont transmises par voie électronique, et de 15 jours en cas d'urgence. En appel d'offres restreint, la commune étant un pouvoir adjudicateur, les candidatures doivent être déposées dans un délai de 30 jours à partir de la date d'envoi de l'avis de marché (réductible en cas d'urgence, sans descendre sous 15 jours) ; les offres des entreprises sélectionnées doivent être transmises dans un délai de 30 jours à compter de l'envoi de l'invitation à soumissionner, que le pouvoir adjudicateur peut ramener à 25 jours si les offres sont ou peuvent être transmises par voie électronique (10 jours en cas d'urgence). Ne vaut pas avis juridique.

### elements_cles

- Avis de marché publié au BOAMP et au JOUE (obligatoire pour un marché de services d'une commune à partir de 216 000 € HT)
- Appel d'offres ouvert avec transmission électronique : 30 jours à compter de l'envoi de l'avis de marché
- Appel d'offres ouvert : délai de 15 jours en cas d'urgence
- Appel d'offres restreint : candidatures dans un délai de 30 jours à partir de l'envoi de l'avis de marché (au moins 15 jours en cas d'urgence)
- Appel d'offres restreint : offres dans un délai de 30 jours à compter de l'envoi de l'invitation à soumissionner, ramené à 25 jours si transmission électronique

### sources_attendues

- https://entreprendre.service-public.gouv.fr/vosdroits/F23371
- https://entreprendre.service-public.gouv.fr/vosdroits/F32049

**sans_reponse** : false

**mention_obligatoire** : Ne vaut pas avis juridique

### provenance

-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F23371 « Quels sont les seuils de publicité des marchés publics ? »
  - **url** : https://entreprendre.service-public.gouv.fr/vosdroits/F23371
  - **chunks** :
    - 3
    - 6
  - **extrait** : Bulletin officiel des annonces de marchés publics (BOAMP) : il concerne les avis de marchés des procédures adaptées (MAPA) et des procédures formalisées . […] Journal officiel de l'Union européenne (JOUE) : pour les annonces légales des marchés à procédure formalisée […] | À partir de 216 000 € | Publicité obligatoire au BOAMP et au JOUE pour une procédure formalisée |
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-13
-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F32049 « Quelles sont les différentes procédures de marchés publics ? »
  - **url** : https://entreprendre.service-public.gouv.fr/vosdroits/F32049
  - **chunks** :
    - 11
  - **extrait** :
    ```text
    Appel d'offres ouvert: L'appel d'offres est ouvert lorsqu’un candidat remet sa candidature ( Dume ou formulaires DC1, DC2, DC4) et une offre (réponse au besoin exprimé par l'acheteur public) en même temps . […] 30 jours à compter de l’envoi de l’avis de marché si les candidatures et les offres sont transmises par voie électronique
    - 15 jours en cas d'urgence […] Lorsque l’acheteur public est un pouvoir adjudicateur : 30 jours à partir de la date d’envoi de l' avis de marché ou de l'invitation à confirmer l’intérêt. En cas d'urgence, le pouvoir adjudicateur peut réduire ce délai de réception des candidatures mais il doit être au minimum de 15 jours. […] Lorsque l’acheteur public est un pouvoir adjudicateur : 30 jours à compter de la date d'envoi de l’ invitation à soumissionner .
    ```
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-13

**licence_source** : Fiche : Licence Ouverte / Etalab 2.0.

**fictif** : false

**version_item** : 1

# Items modifiés (16)

## Q-042 — Question (difficile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Arbitrage A option 1 (cochée, validée 2026-10-13) respectée : seuls entree, reponse_reference, elements_cles, provenance et version_item changent vs v1.0 (même id, version_item 2, difficile, mêmes champs) ; aucune occurrence de plafond/montant/maxim/24/1/ /36 000/18 000/ancienneté/rémunération/calcul dans entree, reponse_reference, elements_cles ni l'extrait ; élément clé du plafond supprimé et chunk 6 retiré (chunks [3,4,6,7] → [3,4,7]) ; calendrier et remboursement gardés. Parquet figé F31094, titre « Rupture conventionnelle dans la fonction publique » et URL concordants ; les 5 segments de l'extrait sont verbatim : lettre recommandée/remise en mains propres (chunk 3), entretien 10 jours francs à 1 mois (chunk 3), signature 15 jours francs après le dernier entretien + rétractation 15 jours francs un jour franc après la signature (chunk 4), cessation au moins 1 jour après la fin du délai de rétractation (chunk 4), remboursement si recrutement par l'État dans les 6 ans, à l'administration signataire, sous 2 ans (chunk 7, section fonctionnaire FPE). Tous les faits de reponse_reference et des 5 elements_cles sont couverts. Amorce et provenance[0] identiques à v1.0 (ligne 1187). Pas d'ambiguïté : réponse unique (séquence de délais + remboursement conditionnel) ; un ajout juste comme l'attestation sur l'honneur (chunk 7) ne contredit pas la référence. Pas de doublon parmi les Q retenus de v1.1 (aucun autre item sur F31094 ou la rupture conventionnelle ; Q-041, démission/chômage F35382, est distinct). Gabarit identique aux 47 autres Q à amorce ; reponse_reference finit par « Ne vaut pas avis juridique. ». Réserve mineure : le segment du chunk 4 dit « votre collectivité employeur » pour un agent de l'État (libellé verbatim de la fiche).

Champs changés : `entree`, `reponse_reference`, `elements_cles`, `provenance`, `version_item`.

### `entree` (modifié)

**Ancienne valeur** :

Un attaché titulaire de notre direction départementale (fonction publique d'État), avec 12 ans d'ancienneté, souhaite une rupture conventionnelle. Sa rémunération brute de l'année civile précédente est de 36 000 €. Quel est le montant maximal de son indemnité spécifique de rupture, et quel calendrier la procédure doit-elle respecter jusqu'à la cessation de ses fonctions ?

**Nouvelle valeur** :

Un attaché titulaire de notre direction départementale (fonction publique d'État) souhaite une rupture conventionnelle. Quel calendrier la procédure doit-elle respecter, de sa demande jusqu'à la cessation de ses fonctions, et que devra-t-il faire de son indemnité spécifique de rupture s'il est recruté plus tard par une administration de l'État ?

### `reponse_reference` (modifié)

**Ancienne valeur** :

Le montant de l'indemnité spécifique de rupture conventionnelle ne peut pas dépasser 1/24e de la rémunération brute annuelle perçue au cours de l'année civile précédente, par année d'ancienneté (dans la limite de 24 ans) : 36 000 € / 24 = 1 500 €, × 12 ans = 18 000 € au maximum. Pour le calendrier : la demande se fait par lettre recommandée avec accusé de réception ou remise en mains propres contre signature ; un entretien a lieu au moins 10 jours francs et au plus tard 1 mois après la réception de la demande ; la convention est signée au moins 15 jours francs après le dernier entretien ; un jour franc après la signature, chaque partie dispose d'un délai de rétractation de 15 jours francs ; la cessation définitive des fonctions intervient au moins 1 jour après la fin du délai de rétractation. S'il est recruté par une administration de l'État dans les 6 ans, il devra rembourser l'indemnité dans les 2 ans suivant ce recrutement. Ne vaut pas avis juridique.

**Nouvelle valeur** :

Pour le calendrier : la demande se fait par lettre recommandée avec accusé de réception ou remise en mains propres contre signature ; un entretien a lieu au moins 10 jours francs et au plus tard 1 mois après la réception de la demande ; la convention est signée au moins 15 jours francs après le dernier entretien ; un jour franc après la signature, chaque partie dispose d'un délai de rétractation de 15 jours francs ; la cessation définitive des fonctions intervient au moins 1 jour après la fin du délai de rétractation. S'il est recruté par une administration de l'État dans les 6 ans qui suivent la rupture conventionnelle, il devra rembourser l'indemnité à l'administration avec laquelle il a conclu la convention, dans les 2 ans suivant ce recrutement. Ne vaut pas avis juridique.

### `elements_cles` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1,3 +1,3 @@
 [
- "Plafond : 1/24e de la rémunération brute annuelle de l'année civile précédente par année d'ancienneté, soit 36 000 / 24 × 12 = 18 000 €",
+ "Demande par lettre recommandée avec accusé de réception ou remise en mains propres contre signature",
  "Entretien au moins 10 jours francs et au plus tard 1 mois après réception de la demande",
```

**Ancienne valeur** :

- Plafond : 1/24e de la rémunération brute annuelle de l'année civile précédente par année d'ancienneté, soit 36 000 / 24 × 12 = 18 000 €
- Entretien au moins 10 jours francs et au plus tard 1 mois après réception de la demande
- Signature de la convention au moins 15 jours francs après le dernier entretien
- Délai de rétractation de 15 jours francs (à partir d'un jour franc après la signature) ; cessation des fonctions au moins 1 jour après la fin de ce délai
- Remboursement de l'indemnité en cas de recrutement par une administration de l'État dans les 6 ans, dans les 2 ans suivant le recrutement

**Nouvelle valeur** :

- Demande par lettre recommandée avec accusé de réception ou remise en mains propres contre signature
- Entretien au moins 10 jours francs et au plus tard 1 mois après réception de la demande
- Signature de la convention au moins 15 jours francs après le dernier entretien
- Délai de rétractation de 15 jours francs (à partir d'un jour franc après la signature) ; cessation des fonctions au moins 1 jour après la fin de ce délai
- Remboursement de l'indemnité en cas de recrutement par une administration de l'État dans les 6 ans, dans les 2 ans suivant le recrutement

### `provenance` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -12,3 +12,2 @@
    4,
-   6,
    7
@@ -16,3 +15,3 @@
   "consulte_le": "2026-10-12",
-  "extrait": "elle en informe l'autre partie par lettre recommandée avec accusé de réception, ou remise en mains propres contre signature. […] Cet entretien doit avoir lieu au moins 10 jours francs et au plus tard 1 mois après la réception par l'une des parties du courrier de l'autre partie demandant la rupture conventionnelle. […] La date de signature de la convention de rupture est fixée par votre collectivité employeur au moins 15 jours francs après le dernier entretien préalable. Un exemplaire de la convention de rupture vous est remis. Un jour franc après la date de signature de la convention, chaque partie dispose d'un délai de rétractation de 15 jours francs. […] La date de cessation définitive des fonctions est fixée au moins 1 jour après la fin du délai de rétractation. […] Le montant de l'indemnité spécifique de rupture conventionnelle ne peut pas être supérieur au 24 e de votre rémunération brute annuelle par années d'ancienneté, dans la limite de 24 ans d’ancienneté. La rémunération brute prise en compte est votre rémunération brute annuelle perçue au cours de l'année civile précédant l’année de la rupture conventionnelle. […] Si vous êtes recruté par une administration de l’État au cours des 6 ans qui suivent votre rupture conventionnelle, vous devez rembourser l'indemnité de rupture à l’administration avec laquelle vous avez conclu votre convention de rupture conventionnelle. Le remboursement doit être effectué dans les 2 ans suivant votre recrutement.",
+  "extrait": "elle en informe l'autre partie par lettre recommandée avec accusé de réception, ou remise en mains propres contre signature. […] Cet entretien doit avoir lieu au moins 10 jours francs et au plus tard 1 mois après la réception par l'une des parties du courrier de l'autre partie demandant la rupture conventionnelle. […] La date de signature de la convention de rupture est fixée par votre collectivité employeur au moins 15 jours francs après le dernier entretien préalable. Un exemplaire de la convention de rupture vous est remis. Un jour franc après la date de signature de la convention, chaque partie dispose d'un délai de rétractation de 15 jours francs. […] La date de cessation définitive des fonctions est fixée au moins 1 jour après la fin du délai de rétractation. […] Si vous êtes recruté par une administration de l’État au cours des 6 ans qui suivent votre rupture conventionnelle, vous devez rembourser l'indemnité de rupture à l’administration avec laquelle vous avez conclu votre convention de rupture conventionnelle. Le remboursement doit être effectué dans les 2 ans suivant votre recrutement.",
   "role": "fiche de référence",
```

**Ancienne valeur** :

-
  - **source** : AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)
  - **url** : https://huggingface.co/datasets/AgentPublic/sp_questions_corpus/resolve/495a22cf7b572621a85d2f3e97783b2f4189c47e/gpt_corpus-20kq%26A.xlsx
  - **ligne** : 1187
  - **role** : amorce de question usager, reformulée par un agent
  - **consulte_le** : 2026-10-12
-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F31094 « Rupture conventionnelle dans la fonction publique »
  - **url** : https://www.service-public.gouv.fr/particuliers/vosdroits/F31094
  - **chunks** :
    - 3
    - 4
    - 6
    - 7
  - **extrait** : elle en informe l'autre partie par lettre recommandée avec accusé de réception, ou remise en mains propres contre signature. […] Cet entretien doit avoir lieu au moins 10 jours francs et au plus tard 1 mois après la réception par l'une des parties du courrier de l'autre partie demandant la rupture conventionnelle. […] La date de signature de la convention de rupture est fixée par votre collectivité employeur au moins 15 jours francs après le dernier entretien préalable. Un exemplaire de la convention de rupture vous est remis. Un jour franc après la date de signature de la convention, chaque partie dispose d'un délai de rétractation de 15 jours francs. […] La date de cessation définitive des fonctions est fixée au moins 1 jour après la fin du délai de rétractation. […] Le montant de l'indemnité spécifique de rupture conventionnelle ne peut pas être supérieur au 24 e de votre rémunération brute annuelle par années d'ancienneté, dans la limite de 24 ans d’ancienneté. La rémunération brute prise en compte est votre rémunération brute annuelle perçue au cours de l'année civile précédant l’année de la rupture conventionnelle. […] Si vous êtes recruté par une administration de l’État au cours des 6 ans qui suivent votre rupture conventionnelle, vous devez rembourser l'indemnité de rupture à l’administration avec laquelle vous avez conclu votre convention de rupture conventionnelle. Le remboursement doit être effectué dans les 2 ans suivant votre recrutement.
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-12

**Nouvelle valeur** :

-
  - **source** : AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)
  - **url** : https://huggingface.co/datasets/AgentPublic/sp_questions_corpus/resolve/495a22cf7b572621a85d2f3e97783b2f4189c47e/gpt_corpus-20kq%26A.xlsx
  - **ligne** : 1187
  - **role** : amorce de question usager, reformulée par un agent
  - **consulte_le** : 2026-10-12
-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F31094 « Rupture conventionnelle dans la fonction publique »
  - **url** : https://www.service-public.gouv.fr/particuliers/vosdroits/F31094
  - **chunks** :
    - 3
    - 4
    - 7
  - **extrait** : elle en informe l'autre partie par lettre recommandée avec accusé de réception, ou remise en mains propres contre signature. […] Cet entretien doit avoir lieu au moins 10 jours francs et au plus tard 1 mois après la réception par l'une des parties du courrier de l'autre partie demandant la rupture conventionnelle. […] La date de signature de la convention de rupture est fixée par votre collectivité employeur au moins 15 jours francs après le dernier entretien préalable. Un exemplaire de la convention de rupture vous est remis. Un jour franc après la date de signature de la convention, chaque partie dispose d'un délai de rétractation de 15 jours francs. […] La date de cessation définitive des fonctions est fixée au moins 1 jour après la fin du délai de rétractation. […] Si vous êtes recruté par une administration de l’État au cours des 6 ans qui suivent votre rupture conventionnelle, vous devez rembourser l'indemnité de rupture à l’administration avec laquelle vous avez conclu votre convention de rupture conventionnelle. Le remboursement doit être effectué dans les 2 ans suivant votre recrutement.
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-12

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

## RD-010 — Recherche de données (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0 : seuls version_item 1→2 et l'ajout de valeurs_attendues.colonnes [Nbre_bailleurs, Nbre_logements], identiques au tableau G1 et présentes dans la ligne attendue ; 67 et 113838 figurent dans la réponse query_resource_data de la cassette (ligne Code Département 91, Essonne) et dans reponse_reference.texte ; Nbre_bailleurs_consolidé, non demandé, est bien exclu ; appel_conforme vrai pour les 3 appels de la cassette ; valider_item strict OK. Réserve : la question demande aussi l'année de publication, mais Année_publication (2018) n'est pas dans les colonnes, conformément au tableau G1 validé ; elle reste exigée par les criteres (Juge).

Champs changés : `version_item`, `valeurs_attendues.colonnes`.

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

### `valeurs_attendues.colonnes` (ajouté)

**Nouvelle valeur** :

- Nbre_bailleurs
- Nbre_logements

## RD-017 — Recherche de données (difficile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0 : seuls version_item 1→2, colonnes [Nombre] (= G1, valeurs 134/137/75 dans la cassette, filtre CNI payantes, mois 1 à 3 de 2020, et dans reponse_reference.texte), contient_un_de [identité, identite, passeport, carte nationale] (points fixes de normaliser) et la prose regle, fidèle. Interprétation : comme pour RD-019, « garder » désigne la liste finale (« carte nationale » n'existait pas en v1.0), donc la liste est fidèle au texte ; le retrait de « caen » est justifié, car le nom de la ville ne signale pas le jeu CNI. appel_conforme : la requête de la cassette « Caen cartes nationales d'identité passeports » est acceptée ; CNIL, cni, « CNI Caen » et Caen sont refusés. valider_item strict OK. Réserve : la requête naturelle « CNI Caen » échoue désormais ; mot_entier_un_de [cni] l'aurait acceptée sans laisser passer CNIL.

Champs changés : `version_item`, `appels_attendus`, `valeurs_attendues.colonnes`.

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

### `appels_attendus` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -7,3 +7,3 @@
   "outil": "search_datasets",
-  "regle": "query contient « Caen », « identité », « passeport » ou « CNI » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres",
+  "regle": "query contient « identité », « passeport » ou « carte nationale » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres",
   "regles": {
@@ -12,3 +12,2 @@
      "contient_un_de": [
-      "caen",
       "identité",
@@ -16,3 +15,3 @@
       "passeport",
-      "cni"
+      "carte nationale"
      ]
```

**Ancienne valeur** :

-
  - **outil** : search_datasets
  - **arguments** :
    - **query** : Caen cartes nationales d'identité passeports
    - **page_size** : 5
  - **regle** : query contient « Caen », « identité », « passeport » ou « CNI » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **query** :
        - **contient_un_de** :
          - caen
          - identité
          - identite
          - passeport
          - cni
-
  - **outil** : list_dataset_resources
  - **arguments** :
    - **dataset_id** : 6152de005b5026338d407619
  - **regle** : dataset_id exact du jeu « Ville de Caen - Cartes nationales d'identité, Passeports »
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **dataset_id** :
        - **exact** : 6152de005b5026338d407619
-
  - **outil** : query_resource_data
  - **arguments** :
    - **resource_id** : a216f407-d9d7-44a2-845b-91736487bb24
    - **filter_column** : TypeTitre
    - **filter_value** : CNI payantes
    - **filter_operator** : exact
    - **page_size** : 3
  - **regle** : resource_id exact du fichier ville-cartesdidentite-passeports-20210101.csv ; filtre exact TypeTitre = « CNI payantes » ; taille de page libre
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **resource_id** :
        - **exact** : a216f407-d9d7-44a2-845b-91736487bb24
      - **filter_column** :
        - **exact** : TypeTitre
      - **filter_value** :
        - **exact** : CNI payantes
      - **filter_operator** :
        - **optionnel** : true
        - **exact** : exact

**Nouvelle valeur** :

-
  - **outil** : search_datasets
  - **arguments** :
    - **query** : Caen cartes nationales d'identité passeports
    - **page_size** : 5
  - **regle** : query contient « identité », « passeport » ou « carte nationale » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **query** :
        - **contient_un_de** :
          - identité
          - identite
          - passeport
          - carte nationale
-
  - **outil** : list_dataset_resources
  - **arguments** :
    - **dataset_id** : 6152de005b5026338d407619
  - **regle** : dataset_id exact du jeu « Ville de Caen - Cartes nationales d'identité, Passeports »
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **dataset_id** :
        - **exact** : 6152de005b5026338d407619
-
  - **outil** : query_resource_data
  - **arguments** :
    - **resource_id** : a216f407-d9d7-44a2-845b-91736487bb24
    - **filter_column** : TypeTitre
    - **filter_value** : CNI payantes
    - **filter_operator** : exact
    - **page_size** : 3
  - **regle** : resource_id exact du fichier ville-cartesdidentite-passeports-20210101.csv ; filtre exact TypeTitre = « CNI payantes » ; taille de page libre
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **resource_id** :
        - **exact** : a216f407-d9d7-44a2-845b-91736487bb24
      - **filter_column** :
        - **exact** : TypeTitre
      - **filter_value** :
        - **exact** : CNI payantes
      - **filter_operator** :
        - **optionnel** : true
        - **exact** : exact

### `valeurs_attendues.colonnes` (ajouté)

**Nouvelle valeur** :

- Nombre

## RD-019 — Recherche de données (facile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0 : seuls version_item 1→2, contient_un_de [répertoire opérationnel, repertoire operationnel, rome, métier, metier] (tous points fixes de normaliser, « répertoire » seul retiré conformément à G2) et la prose regle, fidèle. appel_conforme : la requête de la cassette « répertoire opérationnel des métiers ROME » est acceptée ; « répertoire » et « répertoire des emplois » sont refusés. valider_item strict OK ; la règle se sérialise sans clé mot_entier_un_de. Réserve négligeable : « rome » en début de mot laisse passer « Rome » ou « romeo ».

Champs changés : `version_item`, `appels_attendus`.

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

### `appels_attendus` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -7,3 +7,3 @@
   "outil": "search_datasets",
-  "regle": "query contient « ROME », « métier » ou « répertoire » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres",
+  "regle": "query contient « répertoire opérationnel », « ROME » ou « métier » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres",
   "regles": {
@@ -12,7 +12,7 @@
      "contient_un_de": [
+      "répertoire opérationnel",
+      "repertoire operationnel",
       "rome",
       "métier",
-      "metier",
-      "répertoire",
-      "repertoire"
+      "metier"
      ]
```

**Ancienne valeur** :

-
  - **outil** : search_datasets
  - **arguments** :
    - **query** : répertoire opérationnel des métiers ROME
    - **page_size** : 5
  - **regle** : query contient « ROME », « métier » ou « répertoire » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **query** :
        - **contient_un_de** :
          - rome
          - métier
          - metier
          - répertoire
          - repertoire

**Nouvelle valeur** :

-
  - **outil** : search_datasets
  - **arguments** :
    - **query** : répertoire opérationnel des métiers ROME
    - **page_size** : 5
  - **regle** : query contient « répertoire opérationnel », « ROME » ou « métier » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **query** :
        - **contient_un_de** :
          - répertoire opérationnel
          - repertoire operationnel
          - rome
          - métier
          - metier

## RD-023 — Recherche de données (difficile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0 : seuls version_item 1→2 et l'ajout de colonnes [Année, Note Index], identiques au tableau G1 et présentes dans les 3 lignes ; 2018/2019/2020 avec Note Index 94 (Capgemini Technology Services) figurent dans la cassette (filtre SIREN 479766842) et dans reponse_reference.texte ; appel_conforme vrai pour les 3 appels de la cassette ; valider_item strict OK. Réserve mineure : Année est gardée alors qu'elle est donnée par la question, sans effet pratique mais peu cohérent avec RD-017, qui exclut Année et Mois.

Champs changés : `version_item`, `valeurs_attendues.colonnes`.

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

### `valeurs_attendues.colonnes` (ajouté)

**Nouvelle valeur** :

- Année
- Note Index

## RD-030 — Recherche de données (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0 : seuls version_item 1→2 et l'ajout de colonnes [REG, CHEFLIEU], identiques au tableau G1 ; elles couvrent exactement la demande (code de la région, code commune du chef-lieu), DEP et LIBELLE étant donnés ou non numériques ; REG 53 et CHEFLIEU 29232 figurent dans la cassette (millésime 2026, DEP 29) et dans reponse_reference.texte ; appel_conforme vrai pour les 3 appels de la cassette ; valider_item strict OK.

Champs changés : `version_item`, `valeurs_attendues.colonnes`.

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

### `valeurs_attendues.colonnes` (ajouté)

**Nouvelle valeur** :

- REG
- CHEFLIEU

## RD-031 — Recherche de données (facile, thème `fiscalite-locale`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0 : seuls version_item 1→2, contient_un_de sans rei ni recensement (6 chaînes, points fixes de normaliser), mot_entier_un_de [REI] et la prose regle, qui décrit fidèlement le « ou » entre mot entier et début de mot. appel_conforme : « fichier REI 2024 », « REI-2024 » et la requête de la cassette « recensement des éléments d'imposition » sont acceptés ; « Reims », « reimposition » et « recensement » seul sont refusés (tous trois passaient en v1.0). valider_item strict OK. Réserve mineure : « REI » est stocké en majuscules, ce qui n'est pas un point fixe ; c'est sans effet car _mot_entier normalise le mot, mais c'est hétérogène avec les autres listes.

Champs changés : `version_item`, `appels_attendus`.

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

### `appels_attendus` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -7,3 +7,3 @@
   "outil": "search_datasets",
-  "regle": "query contient « REI », « recensement », « éléments d'imposition », « fiscalité directe locale » ou « impôts locaux » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres",
+  "regle": "query contient « REI » en mot entier, ou « éléments d'imposition », « fiscalité directe locale » ou « impôts locaux » en début de mot (après normalisation (casse, ponctuation) ; variantes accentuée et non accentuée admises) ; autres paramètres libres",
   "regles": {
@@ -12,4 +12,2 @@
      "contient_un_de": [
-      "rei",
-      "recensement",
       "éléments d imposition",
@@ -20,2 +18,5 @@
       "impots locaux"
+     ],
+     "mot_entier_un_de": [
+      "REI"
      ]
```

**Ancienne valeur** :

-
  - **outil** : search_datasets
  - **arguments** :
    - **query** : recensement des éléments d'imposition
    - **page_size** : 5
  - **regle** : query contient « REI », « recensement », « éléments d'imposition », « fiscalité directe locale » ou « impôts locaux » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **query** :
        - **contient_un_de** :
          - rei
          - recensement
          - éléments d imposition
          - elements d imposition
          - fiscalité directe locale
          - fiscalite directe locale
          - impôts locaux
          - impots locaux

**Nouvelle valeur** :

-
  - **outil** : search_datasets
  - **arguments** :
    - **query** : recensement des éléments d'imposition
    - **page_size** : 5
  - **regle** : query contient « REI » en mot entier, ou « éléments d'imposition », « fiscalité directe locale » ou « impôts locaux » en début de mot (après normalisation (casse, ponctuation) ; variantes accentuée et non accentuée admises) ; autres paramètres libres
  - **regles** :
    - **optionnel** : false
    - **ordre_libre** : false
    - **arguments** :
      - **query** :
        - **contient_un_de** :
          - éléments d imposition
          - elements d imposition
          - fiscalité directe locale
          - fiscalite directe locale
          - impôts locaux
          - impots locaux
        - **mot_entier_un_de** :
          - REI

## RD-039 — Recherche de données (difficile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0 : seuls version_item 1→2 et l'ajout de colonnes [Effectifs, IPS], identiques au tableau G1 ; ce sont les seules valeurs numériques demandées (nom et commune sont textuels) ; Effectifs 540.0 et IPS 110.4 figurent dans la cassette (UAI 0010005A, rentrée 2022-2023) et dans reponse_reference.texte ; extraire_nombres reconnaît aussi « 540 » et « 110,4 » ; appel_conforme vrai pour les 3 appels de la cassette ; valider_item strict OK.

Champs changés : `version_item`, `valeurs_attendues.colonnes`.

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

### `valeurs_attendues.colonnes` (ajouté)

**Nouvelle valeur** :

- Effectifs
- IPS

## CR-006 — Compte rendu (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : compter_mots(transcription) = 6621 (> 6500), égal à entree.nb_mots ; v1.0 = 5159. Les 197 paragraphes v1.0 sont présents, inchangés et dans l'ordre ; 40 paragraphes ajoutés en 6 blocs : point 1 avant la suspension (§92-114 : circuits, équipes, chef de centre, vestiaires, maires, coût de 1,9 M€), après le vote du point 1 (§168-170 : plaisanterie de Rouvière), point 2 (§206-220 : jours flottants, jour commun, équipement), point 3 (§334-350 : méthode du baromètre, reconnaissance, 19 % aux routes non représentatif), point 4 (§394-406 : PSSM, logiciel des aides sociales, concours), point 5 (§430-432 : chauffage de l'accueil). Aucune nouvelle décision, aucun avis, vote ou action, aucune demande à mettre dans pieges ; les précisions (entretien du chef de centre, brûleur pour tout le bâtiment, formations avant la bascule) relèvent d'actions ou de contenus déjà référencés. Présences cohérentes (Galmiche au point 1 seulement, Benslimane avant 11 h 42, Kerbrat et Maréchal à partir du point 3, excusés muets), aucun chiffre ni date contradictoire. participants_reference, decisions_reference, actions_reference, pieges, consigne, type_reunion, provenance, licence_source et fictif sont identiques à v1.0 et restent exacts. Réserves de forme : Castagnet parle deux fois de suite (§114/116, §170/172) ; le titre entre parenthèses figure désormais aussi sur une seconde prise de parole pour Vasseur (§188), Moulin (§184), Ferrand (§294), Benslimane (§270) et Arnaud (§314) ; « ce n'est pas propre à la Sarvèze » est répété (§314, §346). L'arbitrage F annonçait 5480 mots pour v1.0, compter_mots en donne 5159.

Champs changés : `entree.transcription`, `entree.nb_mots`, `version_item`.

### `entree.transcription` (modifié)

Différences, ligne à ligne :

```diff
--- ancien
+++ nouveau
@@ -92,2 +92,26 @@
 
+M. Vasseur (FO) : Moi je voudrais revenir sur les circuits, parce que la carte du dossier n'est pas très lisible, on ne distingue pas bien les couleurs. Comment c'est organisé aujourd'hui, concrètement ?
+
+M. Galmiche : Aujourd'hui, chaque centre a ses propres circuits de patrouille, sur un réseau classé par niveaux de priorité. Le niveau 1, ce sont les grands axes, les itinéraires de transport scolaire et les accès aux établissements de santé : ils sont traités en premier, dès le début de l'intervention. Le niveau 2, ce sont les liaisons entre les bourgs. Le niveau 3, c'est le reste du réseau, traité en journée, une fois les deux premiers niveaux dégagés. Le projet ne touche pas à cette hiérarchie. Ce qui change, c'est le point de départ des camions et la répartition des circuits entre les équipes regroupées. Et je m'excuse pour la carte : la version papier est effectivement peu lisible, la version numérique jointe au dossier est en couleur.
+
+M. Vasseur : Et les équipes ? Les gars de Lauzières connaissent leurs routes par cœur, ceux de Montclar connaissent les leurs. Si on mélange tout, la première année va être compliquée.
+
+M. Galmiche : C'est une crainte que les chefs de centre ont exprimée aussi. Ce n'est pas la direction qui compose les équipes, c'est le chef de centre, et rien n'empêche de garder des binômes qui connaissent bien leur ancien secteur. Mais je ne vais pas organiser les plannings en séance, ce n'est pas le lieu.
+
+M. Pallas : Et le chef de centre de Lauzières ? Il devient quoi ?
+
+M. Galmiche : Il garde son grade et ses fonctions d'encadrement. Sa situation sera vue lors de son entretien individuel, comme celle de ses collègues.
+
+Mme Moulin (CFDT) : Je voudrais dire un mot sur les vestiaires, parce qu'on en parle comme d'un détail technique. Les deux collègues qui se changent dans un bureau depuis un an, c'est une situation que la CFDT a signalée plusieurs fois. Quand on se plaint de ne pas arriver à recruter des femmes dans les métiers de la route, il faut d'abord regarder les conditions d'accueil. Pour nous, c'est un argument qui compte dans l'appréciation du projet.
+
+M. Galmiche : Je partage complètement. C'est même ce qui a pesé le plus lourd dans le choix entre la réfection et le regroupement.
+
+Mme Ferrand (conseillère départementale) : Si je peux me permettre, du côté des élus du secteur. J'ai eu plusieurs maires du nord du canton au téléphone ces dernières semaines. Ils ne contestent pas l'état du bâtiment, ils le connaissent. Leur inquiétude, c'est la même que celle de monsieur Pallas : les délais d'intervention quand il neige. Pour eux, voir les camions sortir de Lauzières à cinq heures du matin, c'est rassurant.
+
+M. Benslimane (conseiller départemental) : Et je rappelle quand même l'enjeu budgétaire. Une réfection complète à 1,9 million, pour un bâtiment qui resterait de toute façon mal situé, c'est une somme très importante au regard de ce qu'on consacre chaque année à l'entretien des routes du nord du département. Les élus ont aussi à rendre des comptes là-dessus.
+
+M. Pallas : Je ne dis pas le contraire. Je dis juste que le bâtiment, on le paie une fois, alors que les retards de salage, on les paie tous les hivers. Et ce ne sont pas les élus qui finissent dans les fossés.
+
+M. Castagnet : Monsieur Pallas, chacun a compris votre position, et elle est légitime. On ne va pas refaire tout le débat.
+
 M. Castagnet : Bon. D'autres interventions ? Madame Sissoko.
@@ -144,2 +168,6 @@
 
+M. Rouvière : Pour la CGT, ce sera la même chose, je pense que personne n'en doute. [rires]
+
+M. Castagnet : Personne n'en doute, monsieur Rouvière.
+
 M. Castagnet : Monsieur Galmiche, merci, vous pouvez nous quitter si vous voulez.
@@ -178,2 +206,18 @@
 
+M. Lhermite : Pour l'UNSA, sur le principe des jours flottants, on est plutôt favorables. Ça répond à une vraie demande des agents qui ont des contraintes ponctuelles : un rendez-vous médical, un artisan qui passe, un enfant un peu malade qui ne justifie pas forcément un congé. Aujourd'hui, ces agents posent des congés ou des RTT pour ça. Avec les jours flottants, ils pourront travailler de chez eux ces jours-là.
+
+M. Castagnet : C'est exactement l'esprit du dispositif.
+
+Mme Moulin : Je voudrais témoigner aussi, parce que je travaille à la direction de l'autonomie. Chez nous, on télétravaille deux jours depuis la charte de 2022, et les équipes se sont organisées. Il y a un jour de présence commun, le mardi, où on fait les réunions d'équipe et les synthèses de dossiers. Ça fonctionne bien. Ma seule crainte avec les jours flottants, c'est que ce jour commun se vide petit à petit.
+
+M. Oudin : C'est précisément pour ça que les jours flottants sont validés par le responsable : il garde la main sur les temps de présence collective de son équipe.
+
+M. Vasseur : Et l'équipement ? Il y a encore des agents qui télétravaillent avec leur ordinateur personnel ?
+
+Mme Arnaud (directrice générale adjointe ressources) : Non. Tous les agents en télétravail régulier sont équipés d'un ordinateur portable professionnel. Le déploiement s'est terminé l'an dernier.
+
+M. Vasseur : Bon. Parce qu'on avait eu des remontées, au début, sur des collègues qui travaillaient sur la table de la cuisine avec leur propre portable.
+
+Mme Arnaud : C'était vrai en 2022. Ça ne l'est plus.
+
 Mme Thibaud : La CFDT, de son côté, trouve que le forfait de jours flottants, c'est une vraie avancée, on le demandait depuis deux ans. Par contre, vingt-quatre heures de prévenance pour une annulation, c'est trop court. Quelqu'un qui a organisé la garde de ses enfants autour de son jour de télétravail, si on lui dit la veille à dix-sept heures qu'il doit venir, il ne peut pas. On propose un amendement : quarante-huit heures, sauf urgence dûment justifiée.
@@ -290,2 +334,20 @@
 
+M. Lhermite : Docteur, une question de méthode sur le baromètre. Les questions, elles ont été construites comment ? Parce que des agents m'ont dit qu'ils ne se reconnaissaient pas dans certaines formulations.
+
+Dr Kerbrat : Le questionnaire comptait une soixantaine de questions, construites à partir des grilles habituellement utilisées pour les risques psychosociaux : la charge et l'intensité du travail, l'autonomie, la reconnaissance, les relations avec la hiérarchie et avec les collègues, le rapport aux usagers, et la conciliation entre vie professionnelle et vie personnelle. Il a été relu par la formation spécialisée au printemps, vous vous en souvenez peut-être. Certaines formulations sont générales, c'est le prix de la comparabilité entre les directions.
+
+M. Lhermite : Et sur la reconnaissance, justement, il y a des résultats ? On n'en parle pas dans la synthèse.
+
+Dr Kerbrat : C'est plutôt un point positif, et c'est sans doute pour ça qu'il est moins mis en avant. Une large majorité des répondants se disent soutenus par leurs collègues directs, et la relation avec l'encadrant de proximité est jugée bonne dans la plupart des services. Ce qui ressort le plus négativement, ce sont la charge de travail et le rapport aux usagers, comme je l'ai dit.
+
+M. Pallas : Pour les routes, avec 19 % de réponses, je ne vois pas bien ce qu'on peut en tirer. Les collègues des centres n'ont pas d'ordinateur, ils ont reçu un lien par mail sur une adresse qu'ils ne consultent jamais.
+
+Dr Kerbrat : Vous avez raison, et je le dis clairement : avec ce taux, je ne tire aucune conclusion pour la direction des routes. Les résultats ne sont pas représentatifs.
+
+Mme Maréchal : C'est une limite connue des questionnaires en ligne dans les services techniques. Ce n'est pas propre à la Sarvèze.
+
+Mme Sissoko : Ce qui veut dire que les agents qui ont peut-être les conditions de travail les plus dures physiquement sont ceux qu'on entend le moins.
+
+Dr Kerbrat : C'est une façon juste de le dire.
+
 Mme Thibaud : Une question pour le docteur Kerbrat. Est-ce que les résultats par direction, en détail, peuvent être communiqués ? On n'a que la synthèse globale.
@@ -332,2 +394,16 @@
 
+Mme Moulin : Sur les premiers secours en santé mentale, je voulais remercier la direction, parce que c'était une demande que nous portions depuis longtemps. Est-ce que vous pouvez rappeler en quoi consiste la formation, pour ceux qui ne la connaissent pas ?
+
+Mme Arnaud : C'est une formation de deux jours qui apprend à repérer les signes d'une souffrance psychique chez un collègue ou chez un usager, à engager le dialogue et à orienter vers les bons interlocuteurs. Ce n'est pas une formation de soignant, c'est une formation de premier secours, au même titre que le secourisme classique.
+
+Dr Kerbrat : Et je confirme que c'est très complémentaire de ce qu'on fait en médecine du travail.
+
+Mme Sissoko : Sur le nouveau logiciel des aides sociales, les collègues de l'autonomie en entendent parler depuis un an et ils sont inquiets. Ils ont connu le dernier changement de logiciel, en 2019, et ça s'était très mal passé, avec des semaines de retard dans l'instruction des dossiers.
+
+Mme Arnaud : C'est justement pour ça que l'accompagnement est une priorité du plan. L'expérience de 2019 a servi : les formations sont prévues avant la bascule, par petits groupes, avec des sessions de pratique sur des dossiers fictifs, et pas seulement une démonstration en amphithéâtre.
+
+Mme Thibaud : Et sur la préparation aux concours, est-ce que les agents pourront toujours les suivre sur leur temps de travail ?
+
+Mme Arnaud : Oui, dans les mêmes conditions qu'aujourd'hui. Il n'y a pas de changement sur ce point.
+
 M. Castagnet : On vote ? Avis sur le plan de formation 2027. Collège du personnel ?
@@ -354,2 +430,6 @@
 
+Mme Sissoko : Et je précise que ce ne sont pas seulement les bureaux de l'étage qui sont concernés. À l'accueil du rez-de-chaussée, avec la porte d'entrée qui s'ouvre sans arrêt, les collègues gardent leur manteau toute la matinée.
+
+M. Oudin : C'est bien noté. Le brûleur concerne l'ensemble du bâtiment, l'accueil compris.
+
 M. Castagnet : Deuxième question, de l'UNSA, sur le stationnement à l'Hôtel du Département.
```

<details><summary>Ancienne valeur complète</summary>

```text
Transcription de l'enregistrement audio — Comité social territorial (CST) du Conseil départemental de la Sarvèze
Séance du jeudi 1er octobre 2026 — Hôtel du Département, Valdrieu, salle Ardoise — début de l'enregistrement 9 h 34
(transcription automatique relue par le secrétariat du CST ; les passages inaudibles sont signalés entre crochets)

M. Castagnet (vice-président chargé des ressources humaines, président du CST) : Bon. Bonjour à toutes et à tous. On va commencer, il est déjà neuf heures trente-cinq passées et l'ordre du jour est chargé. Je vous rappelle qu'on enregistre, comme d'habitude, pour le procès-verbal. Monsieur Oudin, est-ce que vous pouvez faire l'appel, s'il vous plaît, qu'on vérifie le quorum ?

M. Oudin (directeur des ressources humaines) : Oui. Alors pour le collège des représentants de la collectivité : monsieur Castagnet, présent ; madame Ferrand, présente ; monsieur Benslimane, présent ; madame Arnaud, directrice générale adjointe ressources, présente ; et moi-même. Donc cinq. Madame Jourdan, conseillère départementale, est excusée, et elle n'est pas remplacée aujourd'hui. Pour le collège des représentants du personnel : pour la CGT, monsieur Rouvière, madame Sissoko, monsieur Pallas, présents. Pour FO, madame Escande, monsieur Vasseur, présents. Pour la CFDT, madame Thibaud, présente ; monsieur Courtade est excusé, il est remplacé par sa suppléante, madame Moulin, qui siège donc avec voix délibérative. Pour l'UNSA, monsieur Lhermite, présent. Ça fait huit représentants du personnel sur huit, le quorum est atteint.

M. Castagnet : Merci. Je salue aussi les experts qui vont nous rejoindre selon les points : monsieur Galmiche, directeur des routes et des mobilités, est là pour le point 1 ; le docteur Kerbrat, médecin du travail, et madame Maréchal, conseillère de prévention, arriveront pour le point sur les risques psychosociaux. Le secrétariat de séance est assuré par monsieur Oudin, et le secrétaire adjoint, c'est toujours monsieur Rouvière. Ça vous va, monsieur Rouvière ?

M. Rouvière (CGT, secrétaire adjoint) : Ça me va. Mais avant de commencer, monsieur le président, j'ai une déclaration liminaire au nom de l'intersyndicale… enfin, de la CGT et de FO, pas de toute l'intersyndicale.

M. Castagnet : Allez-y, mais je vous demande d'être raisonnable sur la durée, on a cinq points.

M. Rouvière : Je serai bref. Alors, nous voulons dire notre inquiétude face à la succession des réorganisations dans les services. En moins de deux ans, on a eu la réorganisation des maisons départementales des solidarités, celle de la direction de l'autonomie, et aujourd'hui on nous présente la fusion de centres d'exploitation routière. Les agents ont l'impression qu'on les déplace comme des pions, et le baromètre social qu'on va voir tout à l'heure le montre très bien. On demande que chaque réorganisation soit précédée d'une vraie étude d'impact sur les conditions de travail, présentée en formation spécialisée avant de venir en CST. Voilà. La déclaration complète sera remise au secrétariat pour être annexée au procès-verbal.

M. Castagnet : Très bien, elle sera annexée. Je ne vais pas répondre point par point maintenant, on aura l'occasion d'en discuter sur le point 1. Madame Escande, vous vouliez ajouter quelque chose ?

Mme Escande (FO) : Juste que FO s'associe à la déclaration, et qu'on regrette d'avoir reçu les documents du point 2 seulement huit jours avant. C'est le minimum réglementaire, mais pour une charte de télétravail qui touche plus de mille agents, c'est court.

M. Castagnet : C'est noté. On essaiera de faire mieux. Bien. Premier point, l'approbation du procès-verbal de la séance du 2 juillet. Est-ce qu'il y a des remarques ?

Mme Escande : Oui. Page six, sur les astreintes, il est écrit que FO « approuve le nouveau régime d'astreinte ». Ce n'est pas ce que j'ai dit. J'ai dit que FO approuvait la revalorisation, mais pas l'élargissement des astreintes aux agents de catégorie C du service des bâtiments. Je demande que ce soit corrigé.

M. Oudin : On a l'enregistrement, on vérifiera, mais de mémoire vous avez raison. On peut écrire : « FO approuve la revalorisation des indemnités d'astreinte mais s'oppose à leur extension aux agents de catégorie C du service des bâtiments ».

Mme Escande : Voilà, c'est exactement ça.

M. Castagnet : D'autres remarques ? Non. Je mets aux voix le procès-verbal ainsi modifié. Qui est contre ? Qui s'abstient ? Donc unanimité des deux collèges, le PV du 2 juillet est approuvé avec la correction de madame Escande. Monsieur Oudin, vous mettrez la version corrigée en ligne ?

M. Oudin : Oui, elle sera mise en ligne sur l'intranet avec les autres PV d'ici la fin octobre.

M. Castagnet : Bien. Alors, point 1, la réorganisation de la direction des routes et des mobilités, et plus précisément la fusion du centre d'exploitation routière de Lauzières avec celui de Montclar-d'Orbe. Monsieur Galmiche, je vous laisse présenter.

M. Galmiche (directeur des routes et des mobilités) : Merci monsieur le président. Bonjour à tous. Je vais faire court sur le contexte, vous avez le dossier. Aujourd'hui, l'agence routière Nord compte trois centres d'exploitation : Lauzières, Montclar-d'Orbe et Saint-Fréjus. Le centre de Lauzières, c'est quatorze agents, dont un chef de centre, dans un bâtiment de 1978 qui n'est plus aux normes, avec notamment de l'amiante dans la toiture du hangar et des vestiaires qui ne permettent pas d'accueillir des femmes dans des conditions correctes. On a deux agentes d'exploitation qui sont arrivées l'an dernier et qui se changent dans un bureau, ce n'est pas acceptable. La réfection complète du bâtiment a été chiffrée à 1,9 million d'euros. En face, le centre de Montclar-d'Orbe, qui est à dix-neuf kilomètres, a été rénové en 2022 et peut accueillir les quatorze agents avec une extension modulaire. Donc la proposition, c'est de regrouper les deux centres à Montclar-d'Orbe, avec une mise en œuvre au 1er janvier 2027. Le linéaire de routes reste le même, les circuits de patrouille sont redécoupés, et on ne supprime aucun poste. Je le redis parce que j'ai entendu des rumeurs : aucun poste supprimé.

M. Pallas (CGT) : Aucun poste supprimé, mais combien de postes non remplacés dans trois ans ?

M. Galmiche : Je ne peux pas vous répondre sur ce qui se passera dans trois ans, je vous réponds sur le projet qui est présenté aujourd'hui.

M. Pallas : Ben justement. Moi je suis agent d'exploitation à Lauzières depuis quatorze ans, je connais le secteur. Le problème, ce n'est pas le bâtiment, tout le monde est d'accord que le bâtiment est pourri. Le problème, c'est la viabilité hivernale. Quand il neige sur le plateau, depuis Montclar, il faut monter le col de la Bessière avant même de commencer à saler. Vous perdez trente, quarante minutes. Et les routes du nord du canton, elles seront traitées en dernier.

M. Galmiche : On a regardé ça. Les nouveaux circuits sont construits pour que le premier passage sur le réseau prioritaire soit fait dans les mêmes délais qu'aujourd'hui…

M. Pallas : Sur le papier.

M. Galmiche : … sur le papier, oui, c'est une étude, je ne vais pas vous dire le contraire. Mais elle a été faite avec les chefs de centre.

M. Castagnet : Laissez finir monsieur Galmiche, s'il vous plaît, vous aurez la parole après.

M. Galmiche : Je termine. Concernant les agents : chacun sera reçu en entretien individuel par la DRH et par moi-même. On a déjà regardé les temps de trajet domicile-travail : pour huit agents sur quatorze, le trajet s'allonge de moins de quinze minutes ; pour quatre agents, entre quinze et trente minutes ; et pour deux agents, c'est plus long, autour de quarante minutes. Pour ceux-là, on étudiera des solutions au cas par cas, éventuellement une mobilité vers Saint-Fréjus s'ils le souhaitent.

Mme Escande : Et l'indemnité ? Parce que quand on allonge de quarante minutes le trajet de quelqu'un qui gagne mille six cents euros, ça a un coût. FO demande une prime de restructuration pour l'ensemble des quatorze agents.

M. Oudin : Alors, je précise : il existe une indemnité de restructuration de service prévue par les textes, mais elle est encadrée, elle dépend notamment du changement de résidence administrative et de la distance. On ne peut pas promettre aujourd'hui qu'elle sera versée à tout le monde. Ce qu'on s'engage à faire, c'est d'examiner chaque situation lors des entretiens individuels.

Mme Escande : Donc c'est non.

M. Oudin : Ce n'est pas non, c'est : au cas par cas, dans le cadre réglementaire.

Mme Escande : Pour les agents, c'est non.

M. Castagnet : Je comprends la demande. Je ne vais pas prendre d'engagement en séance sur un dispositif indemnitaire, il faut qu'on le chiffre. On en reparlera.

Mme Thibaud (CFDT) : Moi j'ai deux questions. La première : le calendrier. Pourquoi le 1er janvier ? C'est en plein milieu de la saison de viabilité hivernale. Si on déménage un centre en janvier avec des agents qui ne connaissent pas encore leurs nouveaux circuits, et qu'il tombe vingt centimètres de neige, ça va être le chaos. La deuxième : qu'est-ce qu'on fait du sel ? Il y a un stock à Lauzières qui sert à tout le nord.

M. Galmiche : Sur le sel, on y a pensé. L'idée serait de garder l'aire de stockage de sel de Lauzières comme dépôt avancé pour l'hiver, mais ça suppose que le hangar à sel, qui est un bâtiment séparé, soit utilisable. Il faut qu'on fasse faire un diagnostic. Si le diagnostic est bon, on le garde ; sinon, on stockera tout à Montclar.

Mme Thibaud : Et le diagnostic, il sera fait quand ?

M. Galmiche : Il est commandé, on attend la date du bureau d'études. Je ne l'ai pas encore.

Mme Thibaud : Et sur le calendrier ?

M. Galmiche : Sur le calendrier… [silence] … je vais laisser le président répondre.

M. Castagnet : Écoutez, sur le calendrier, j'entends l'argument et je le trouve fondé. Je vous propose de modifier le projet : la mise en œuvre de la fusion serait reportée au 1er mars 2027, après le pic de la viabilité hivernale, au lieu du 1er janvier. Monsieur Galmiche, c'est tenable pour vous ?

M. Galmiche : C'est tenable. Ça décale un peu les travaux d'extension, mais c'est tenable.

M. Castagnet : Donc on modifie le projet soumis à l'avis : mise en œuvre au 1er mars 2027.

M. Rouvière : Ça ne change rien sur le fond.

M. Castagnet : Ça change le calendrier, c'est déjà quelque chose.

M. Lhermite (UNSA) : Moi je voudrais dire quelque chose. L'UNSA a rencontré les agents de Lauzières la semaine dernière. Ils ne sont pas tous contre, loin de là. Les deux collègues femmes dont parlait monsieur Galmiche, elles attendent ça depuis un an. Et plusieurs agents habitent plus près de Montclar que de Lauzières, en fait. Donc il ne faut pas présenter ça comme si tout le monde était contre.

M. Pallas : Personne n'a dit que tout le monde était contre.

M. Lhermite : Si, un peu, quand même. [rires]

M. Castagnet : Bon. D'autres interventions ? Madame Sissoko.

Mme Sissoko (CGT) : Oui, je voulais revenir sur ce que disait monsieur Galmiche sur les temps de trajet. Vous avez une étude agent par agent ? Parce que nous, on ne l'a pas dans le dossier.

M. Galmiche : On l'a, mais elle est nominative, donc on ne l'a pas jointe.

Mme Sissoko : Vous pouvez l'anonymiser.

M. Galmiche : Oui, on peut l'anonymiser. Je vous la transmets.

Mme Sissoko : Avant le vote ?

M. Galmiche : Avant le vote d'aujourd'hui, non, ce n'est pas possible matériellement. Mais je vous la transmets avant le prochain CST, celui du 10 décembre.

M. Rouvière : Monsieur le président, je demande une suspension de séance de dix minutes, pour qu'on se concerte entre organisations avant le vote.

M. Castagnet : Accordée. On reprend à dix heures quarante.

[Suspension de séance de 10 h 28 à 10 h 41]

M. Castagnet : On reprend. Monsieur Rouvière, la suspension a été utile ?

M. Rouvière : Elle a été utile, on a échangé. Je fais juste une remarque avant le vote : on aurait aimé que ce projet passe d'abord en formation spécialisée, vu qu'il y a des questions d'amiante, de vestiaires, de conditions de travail. On n'a pas eu ça.

M. Castagnet : Le diagnostic amiante a été présenté à la formation spécialisée en mars, si ma mémoire est bonne.

M. Oudin : En mai. Le 12 mai.

M. Castagnet : En mai, pardon. Bon. Je vous propose de passer au vote. Je rappelle que l'avis porte sur le projet tel que modifié en séance, c'est-à-dire la fusion du centre d'exploitation de Lauzières avec celui de Montclar-d'Orbe, regroupement des quatorze agents à Montclar-d'Orbe, sans suppression de poste, avec une mise en œuvre au 1er mars 2027, et le maintien du dépôt de sel de Lauzières sous réserve du diagnostic. Et je rappelle aussi que le CST rend un avis : la décision appartient ensuite au président du conseil départemental. Collège des représentants du personnel d'abord. Qui est favorable ?

M. Oudin : Une voix pour, monsieur Lhermite, UNSA.

M. Castagnet : Qui s'abstient ?

M. Oudin : Deux abstentions, madame Thibaud et madame Moulin, CFDT.

M. Castagnet : Qui est contre ?

M. Oudin : Cinq contre : monsieur Rouvière, madame Sissoko, monsieur Pallas pour la CGT, madame Escande et monsieur Vasseur pour FO.

M. Castagnet : Donc avis défavorable du collège des représentants du personnel : cinq contre, deux abstentions, un pour. Collège des représentants de la collectivité ?

M. Oudin : Cinq pour, unanimité.

M. Castagnet : Avis favorable du collège employeur. L'avis des représentants du personnel n'étant pas défavorable à l'unanimité, il n'y a pas lieu à une nouvelle consultation. Le dossier sera soumis au président du Département.

Mme Escande : Je voudrais juste que le PV mentionne que FO votera contre aussi en commission permanente si le sujet y passe.

M. Castagnet : Madame Escande, FO ne siège pas en commission permanente. [rires] Mais votre position sera notée au PV, bien sûr.

Mme Escande : Vous m'avez comprise.

M. Castagnet : Monsieur Galmiche, merci, vous pouvez nous quitter si vous voulez.

M. Galmiche : Merci. Je confirme que l'étude anonymisée partira bien avant le 10 décembre. Et la DRH et moi, on prévoit les entretiens individuels avec les quatorze agents d'ici le 30 novembre.

M. Oudin : Oui, avant le 30 novembre, c'est calé de notre côté.

[Départ de M. Galmiche à 10 h 49]

M. Castagnet : Point 2, la modification de la charte du télétravail. Monsieur Oudin.

M. Oudin : Alors, rapidement, le bilan d'abord. Aujourd'hui, mille quatre cent vingt agents télétravaillent régulièrement sur deux mille huit cent soixante-dix agents… Pardon, je corrige tout de suite, j'ai inversé les chiffres : c'est mille deux cent quarante agents, pas mille quatre cent vingt. Mille deux cent quarante sur deux mille huit cent soixante-dix, donc à peu près 43 %. Le chiffre est juste dans le document, page trois, c'est moi qui me suis trompé.

Mme Moulin (CFDT) : Ça me paraissait beaucoup, en effet.

M. Oudin : Oui. Donc la charte actuelle, adoptée en 2022, prévoit un maximum de deux jours fixes par semaine. Ce qu'on vous propose : on garde les deux jours fixes maximum, et on ajoute un forfait annuel de vingt jours flottants, qui peuvent être posés en plus, dans la limite de trois jours télétravaillés sur une même semaine. Ensuite, on clarifie les conditions d'éligibilité des agents à temps partiel : un agent à 80 % pourra télétravailler un jour fixe, plus les jours flottants. Et on fixe un délai de prévenance quand le responsable doit annuler un jour de télétravail pour nécessité de service : aujourd'hui, il n'y a rien dans la charte, on propose vingt-quatre heures. Enfin, l'indemnité forfaitaire de télétravail reste versée au taux réglementaire, pas de changement. Entrée en vigueur au 1er janvier 2027.

M. Vasseur (FO) : Les jours flottants, c'est sur demande de l'agent, ou c'est imposé ?

M. Oudin : Sur demande de l'agent, validée par le responsable, dans l'outil de gestion des temps.

M. Vasseur : Validée comment ? Parce que dans certains services, je vous le dis, les demandes sont refusées sans explication.

M. Oudin : Tout refus devra être motivé, c'est déjà dans la charte, article 6.

M. Vasseur : C'est dans la charte, mais ce n'est pas appliqué. À la direction de l'enfance et de la famille, on a eu trois refus non motivés au printemps.

M. Oudin : Faites-nous remonter les situations, on les regardera.

Mme Sissoko : La CGT, elle, demande trois jours fixes. Beaucoup de collectivités autour l'ont fait. Les agents de l'autonomie, les instructeurs APA et PCH, ils font de l'instruction de dossiers toute la journée, ils peuvent le faire de chez eux. Et ils habitent loin, se loger à Valdrieu, c'est cher.

M. Castagnet : Trois jours fixes, ce n'est pas notre position. On a besoin de collectifs de travail. On a eu des retours de managers, des retours aussi du baromètre, sur l'isolement. Donc on reste à deux jours fixes, plus les jours flottants, ce qui permet d'aller jusqu'à trois certaines semaines. C'est un compromis.

Mme Sissoko : C'est un compromis que vous faites avec vous-même.

Mme Thibaud : La CFDT, de son côté, trouve que le forfait de jours flottants, c'est une vraie avancée, on le demandait depuis deux ans. Par contre, vingt-quatre heures de prévenance pour une annulation, c'est trop court. Quelqu'un qui a organisé la garde de ses enfants autour de son jour de télétravail, si on lui dit la veille à dix-sept heures qu'il doit venir, il ne peut pas. On propose un amendement : quarante-huit heures, sauf urgence dûment justifiée.

M. Castagnet : Monsieur Oudin ?

M. Oudin : Quarante-huit heures, on peut l'accepter. Avec la mention « sauf urgence », bien sûr.

M. Castagnet : Alors on intègre l'amendement de la CFDT : délai de prévenance de quarante-huit heures, sauf urgence.

M. Lhermite : Et les agents des collèges ? Les agents techniques des collèges n'ont pas accès au télétravail, c'est logique pour l'entretien ou la restauration, mais il y a des gestionnaires administratifs, des secrétaires…

M. Oudin : Les agents des collèges qui sont sur des fonctions administratives, c'est un sujet compliqué, parce qu'il y a la double autorité avec le chef d'établissement.

M. Lhermite : Justement, c'est pour ça qu'il faut en parler.

M. Castagnet : On peut regarder ça, oui. Il faudrait sans doute en discuter avec l'Éducation nationale. On regardera.

M. Lhermite : Qui regardera, et quand ?

M. Castagnet : On regardera, monsieur Lhermite. Je ne vais pas vous donner une date aujourd'hui.

M. Rouvière : J'ajoute une chose sur l'indemnité forfaitaire. Elle ne couvre pas l'augmentation de l'électricité. On demande une prise en charge d'une partie de l'abonnement internet.

M. Oudin : Ce n'est pas prévu, et je ne crois pas que ce soit possible juridiquement en dehors du forfait.

M. Castagnet : Ce n'est pas dans le projet. Bien. Est-ce qu'on peut voter ? Je rappelle le projet modifié : maximum deux jours fixes par semaine, forfait annuel de vingt jours flottants, plafond de trois jours télétravaillés par semaine, délai de prévenance de quarante-huit heures sauf urgence pour l'annulation par le responsable, entrée en vigueur au 1er janvier 2027. Collège du personnel, qui est pour ?

M. Oudin : Cinq pour : madame Escande, monsieur Vasseur, madame Thibaud, madame Moulin, monsieur Lhermite.

M. Castagnet : Abstentions ?

M. Oudin : Trois abstentions, la CGT.

M. Castagnet : Contre ? Aucun. Avis favorable du collège du personnel. Collège employeur ?

M. Oudin : Cinq pour.

M. Castagnet : Avis favorable des deux collèges. Merci. La charte modifiée sera…

M. Oudin : Elle sera publiée sur l'intranet avec une note de service avant le 1er décembre, pour que les agents aient le temps de faire leurs demandes pour 2027. C'est moi qui m'en occupe.

Mme Escande : Et le bilan ? On avait demandé un bilan régulier.

M. Oudin : Je vous présenterai un bilan au bout d'un an d'application, donc au CST de début 2028.

Mme Escande : Début 2028, c'est loin.

M. Castagnet : Un an d'application, c'est le minimum pour avoir du recul. Point 3, les risques psychosociaux. J'invite le docteur Kerbrat et madame Maréchal à nous rejoindre. [bruit de chaises] Monsieur Benslimane, vous deviez partir ?

M. Benslimane (conseiller départemental) : Je dois partir vers onze heures quarante, j'ai la commission d'appel d'offres à midi. Je reste pour le début.

M. Castagnet : Très bien. Docteur Kerbrat.

Dr Kerbrat (médecin du travail) : Merci. Alors je vais vous présenter les résultats du baromètre social, qui a été réalisé en mai et juin, et ensuite madame Maréchal vous présentera le projet de plan de prévention. Je précise que ce point est présenté pour information : il n'y a pas d'avis à rendre aujourd'hui sur le plan, qui sera retravaillé en formation spécialisée.

M. Rouvière : C'est bien ce qu'on regrette, d'ailleurs.

Dr Kerbrat : Le taux de réponse est de 38 %, ce qui est correct pour une première édition, mais très variable selon les directions. Il est de 61 % à la direction de l'enfance et de la famille, et de 19 % à la direction des routes, où beaucoup d'agents n'ont pas de poste informatique. Les principaux enseignements : la charge de travail est jugée excessive par 54 % des répondants ; 41 % disent avoir été confrontés à des comportements agressifs d'usagers au cours des douze derniers mois, et ce chiffre monte à 72 % dans les maisons départementales des solidarités ; et enfin, 29 % des répondants déclarent un niveau de stress élevé ou très élevé. Je voudrais attirer votre attention sur les MDS, et particulièrement sur la MDS de Saint-Fréjus, où les indicateurs sont nettement dégradés, avec un incident sérieux en août, que vous connaissez.

Mme Escande : Oui, on le connaît, une collègue a été menacée à l'accueil. Et je vais être claire : FO demande que la formation spécialisée se rende sur place. Pas dans six mois. Maintenant.

M. Castagnet : Madame Maréchal, la formation spécialisée peut organiser une visite rapidement ?

Mme Maréchal (conseillère de prévention) : Oui, une délégation de la formation spécialisée peut se rendre sur place. Je propose le mardi 20 octobre, le matin. Il faut une délégation avec au moins un représentant du personnel et un représentant de la collectivité ; je l'accompagnerai et je m'occupe de l'organisation.

M. Castagnet : Qui se propose ?

M. Rouvière : Moi.

Mme Escande : Moi aussi, évidemment.

M. Castagnet : Et pour la collectivité, madame Ferrand, vous pourriez ?

Mme Ferrand (conseillère départementale) : Le 20 au matin, oui, je peux.

M. Castagnet : Très bien, donc délégation de la formation spécialisée à la MDS de Saint-Fréjus le mardi 20 octobre au matin : monsieur Rouvière, madame Escande, madame Ferrand, accompagnés de madame Maréchal, qui organise la visite. Le compte rendu de visite sera présenté à la prochaine formation spécialisée.

Mme Maréchal : Qui est le jeudi 19 novembre.

M. Castagnet : Le 19 novembre. Bien.

Mme Sissoko : Et en attendant, l'agent de sécurité à l'accueil de Saint-Fréjus ? Depuis août, il n'y a toujours rien.

M. Oudin : Un agent de sécurité est présent à titre provisoire les mardis et jeudis, jours de forte affluence, depuis le 14 septembre. C'est déjà en place, ça a été décidé au moment de l'incident.

Mme Sissoko : Deux jours sur cinq.

M. Oudin : Pour l'instant, oui. La visite permettra d'évaluer s'il faut étendre.

Mme Maréchal : Je continue sur le plan de prévention. Il comporte trois axes. Premier axe : la prévention des violences externes. On propose une formation à la gestion des situations d'agressivité pour tous les agents d'accueil des MDS, environ cent dix agents, avec les premières sessions dès novembre si le plan est validé. Deuxième axe : la charge de travail, avec un travail par direction sur les priorités, piloté par chaque directeur. Troisième axe : l'accompagnement des encadrants, avec un module de formation à la prévention des RPS pour les managers. Et parallèlement, je mets à jour le document unique d'évaluation des risques professionnels, le DUERP, pour intégrer tout ça : l'objectif est d'avoir une version à jour avant le 31 mars 2027.

M. Vasseur : La formation aux agressions, c'est bien, mais ça ne remplace pas des effectifs. À Saint-Fréjus, il manque deux travailleurs sociaux depuis le printemps.

Mme Arnaud (directrice générale adjointe ressources) : Les deux postes sont publiés, monsieur Vasseur. On a un problème d'attractivité sur les métiers du social, vous le savez, ce n'est pas propre à la Sarvèze.

M. Vasseur : On le sait. Mais pendant ce temps-là, ce sont les collègues présents qui absorbent les dossiers. Le deuxième axe, la charge de travail, il commence quand ?

Mme Maréchal : Il démarrera après la validation du plan, direction par direction. Je n'ai pas encore de calendrier par direction.

M. Rouvière : La CGT a une proposition concrète. On demande la mise en place d'une cellule d'écoute psychologique externe, accessible vingt-quatre heures sur vingt-quatre, comme ça existe dans d'autres départements. Les agents ne veulent pas toujours parler à la médecine du travail, qui est perçue comme… enfin, comme interne.

Dr Kerbrat : Je ne le prends pas mal. [rires] Mais je rappelle qu'on a déjà une psychologue du travail, à mi-temps.

M. Rouvière : À mi-temps pour deux mille huit cents agents.

M. Castagnet : La cellule d'écoute externe, ça a un coût, ça passe par un marché. Je ne suis pas contre l'idée, mais je ne peux pas la décider aujourd'hui. Madame Arnaud, vous pouvez faire chiffrer ?

Mme Arnaud : On peut regarder ce que ça coûterait, oui, je le fais dans le cadre de la préparation budgétaire 2027.

M. Rouvière : Donc ce n'est pas acté.

M. Castagnet : Ce n'est pas acté, c'est étudié. Je ne vais pas vous mentir.

Mme Thibaud : Une question pour le docteur Kerbrat. Est-ce que les résultats par direction, en détail, peuvent être communiqués ? On n'a que la synthèse globale.

Dr Kerbrat : Oui, je peux présenter les résultats détaillés par direction, en respectant le seuil d'anonymat — on ne descend pas en dessous de dix répondants. Je propose de le faire à la formation spécialisée du 19 novembre.

M. Castagnet : Parfait. [M. Benslimane se lève] Monsieur Benslimane nous quitte.

M. Benslimane : Excusez-moi, bonne fin de séance.

[Départ de M. Benslimane à 11 h 42]

M. Castagnet : Le collège employeur compte donc quatre membres pour la suite. D'autres questions sur le point 3 ? Monsieur Pallas.

M. Pallas : Juste pour revenir au point 1, parce que je n'ai pas eu de réponse. Le dépôt de sel de Lauzières, si le diagnostic est mauvais, il se passe quoi pour l'hiver 2027-2028 ? On sale tout le nord depuis Montclar ?

M. Castagnet : Monsieur Pallas, on a voté sur le point 1. Monsieur Galmiche est parti.

M. Pallas : Je sais, mais c'est une vraie question.

M. Castagnet : C'est une vraie question. Monsieur Oudin, vous la transmettez à monsieur Galmiche, et il répondra par écrit aux organisations syndicales.

M. Oudin : Je la lui transmets aujourd'hui.

M. Castagnet : Bien. Sur le point 3, je rappelle encore une fois qu'il n'y a pas de vote : c'est une information, le plan reviendra pour avis après le travail en formation spécialisée. Point 4, le plan de formation 2027. Madame Arnaud.

Mme Arnaud : Je serai rapide puisque les documents sont détaillés. Le plan de formation 2027 reprend les orientations du plan pluriannuel. Les priorités : la prévention des risques, notamment ce qu'on vient d'évoquer sur les agressions et sur les RPS pour les encadrants ; la transition numérique, avec l'accompagnement au nouveau logiciel de gestion des aides sociales ; et la préparation aux concours et examens professionnels. Le budget prévisionnel est de 640 000 euros, en dehors de la cotisation au CNFPT. On a aussi intégré, à la demande de la CFDT l'an dernier, des formations aux premiers secours en santé mentale.

Mme Thibaud : On s'en félicite.

M. Vasseur : Pour FO, on voudrait que les agents des routes aient accès aux formations en semaine, pas le samedi.

Mme Arnaud : C'est le cas, il n'y a pas de formation le samedi.

M. Vasseur : Il y en a eu une en mars.

Mme Arnaud : C'était une exception, liée à la disponibilité du formateur. On fera attention.

M. Pallas : Et les formations CACES, pour les engins ? Il y a des agents qui attendent depuis deux ans.

Mme Arnaud : Elles sont dans le plan, page neuf, avec quarante-deux places en 2027 contre vingt-huit cette année.

M. Pallas : Bon. C'est mieux.

M. Castagnet : On vote ? Avis sur le plan de formation 2027. Collège du personnel ?

M. Oudin : Huit pour, unanimité.

M. Castagnet : Collège employeur ?

M. Oudin : Quatre pour, unanimité des présents.

M. Castagnet : Avis favorable unanime des deux collèges. Madame Arnaud, vous le transmettrez à la délégation régionale du CNFPT ?

Mme Arnaud : Oui, avant le 31 décembre, comme chaque année.

M. Castagnet : Point 5, les questions diverses. J'ai reçu deux questions écrites. La première, de la CGT, sur le chauffage du bâtiment B, rue des Tanneurs.

Mme Sissoko : Oui. Les agents du bâtiment B, c'est la direction de l'autonomie, ils ont eu dix-sept degrés la semaine dernière, alors qu'il ne fait pas encore froid. Qu'est-ce que ce sera en janvier ? La chaudière est en panne une semaine sur deux.

M. Oudin : On a eu le signalement. Le service des bâtiments doit intervenir pour remplacer le brûleur. Je m'engage à ce que l'intervention ait lieu avant le vendredi 16 octobre, et je vous en confirmerai la date par mail.

Mme Sissoko : On a déjà entendu ça au printemps.

M. Oudin : Cette fois, la pièce est commandée.

M. Castagnet : Deuxième question, de l'UNSA, sur le stationnement à l'Hôtel du Département.

M. Lhermite : Oui. Depuis la fermeture du parking de la rue Carnot pour travaux, les agents qui arrivent après huit heures trente ne trouvent plus de place. Les agents à temps partiel, ceux qui déposent les enfants, ceux qui sont en horaires décalés. On demande des places réservées ou une convention avec le parking public.

M. Castagnet : Une convention avec le parking des Halles, on y a pensé. Ça a un coût aussi. Madame Arnaud ?

Mme Arnaud : Je peux demander un devis au gestionnaire du parking.

M. Castagnet : Faites, oui. Mais je ne prends pas d'engagement sur la convention elle-même.

M. Lhermite : Dans quel délai, le devis ?

Mme Arnaud : Je n'ai pas la main sur leurs délais. Dès qu'on l'a, on le partage.

Mme Escande : J'ai une question orale, si vous permettez, qui n'était pas dans les questions écrites. Le compte épargne-temps. Les agents qui ont atteint le plafond de soixante jours perdent des jours, notamment aux routes, à cause des astreintes. On demande une ouverture de la monétisation.

M. Castagnet : Ce n'est pas à l'ordre du jour, madame Escande, et c'est un sujet qui demande une délibération. Je ne peux pas en débattre sans document. Monsieur Oudin, vous l'inscrivez à l'ordre du jour du prochain CST, avec une note ?

M. Oudin : Je l'inscris pour le 10 décembre, avec une note sur les soldes de CET par direction.

Mme Escande : Merci.

M. Rouvière : Et sur la déclaration liminaire, monsieur le président ? Sur l'étude d'impact systématique avant chaque réorganisation ?

M. Castagnet : Je vous ai entendu. C'est une demande légitime. Mais je ne vais pas créer une procédure en fin de séance. On en reparle avec la DRH dans le cadre de l'agenda social.

M. Rouvière : On le notera au PV, alors, que ce n'est pas acté.

M. Castagnet : Notez-le.

Mme Ferrand : Si je peux me permettre un mot, monsieur le président. Je voulais remercier les agents des MDS, au nom des élus, parce qu'on parle beaucoup de chiffres mais ce qu'ils vivent au quotidien est difficile.

M. Castagnet : Merci madame Ferrand. Je m'associe à vos propos. Alors, avant de clore, je vous rappelle la date du prochain CST. Je vous avais indiqué le 3 décembre dans la convocation…

M. Oudin : Le 10, monsieur le président. Le 3, c'était la date initiale, elle a été changée à cause de la session du conseil départemental.

M. Castagnet : Le jeudi 10 décembre, pardon, à neuf heures trente. Merci monsieur Oudin. Et la formation spécialisée se réunit le jeudi 19 novembre. Plus de questions ? Je vous remercie. La séance est levée.

[Fin de l'enregistrement : 12 h 21]
```

</details>

<details><summary>Nouvelle valeur complète</summary>

```text
Transcription de l'enregistrement audio — Comité social territorial (CST) du Conseil départemental de la Sarvèze
Séance du jeudi 1er octobre 2026 — Hôtel du Département, Valdrieu, salle Ardoise — début de l'enregistrement 9 h 34
(transcription automatique relue par le secrétariat du CST ; les passages inaudibles sont signalés entre crochets)

M. Castagnet (vice-président chargé des ressources humaines, président du CST) : Bon. Bonjour à toutes et à tous. On va commencer, il est déjà neuf heures trente-cinq passées et l'ordre du jour est chargé. Je vous rappelle qu'on enregistre, comme d'habitude, pour le procès-verbal. Monsieur Oudin, est-ce que vous pouvez faire l'appel, s'il vous plaît, qu'on vérifie le quorum ?

M. Oudin (directeur des ressources humaines) : Oui. Alors pour le collège des représentants de la collectivité : monsieur Castagnet, présent ; madame Ferrand, présente ; monsieur Benslimane, présent ; madame Arnaud, directrice générale adjointe ressources, présente ; et moi-même. Donc cinq. Madame Jourdan, conseillère départementale, est excusée, et elle n'est pas remplacée aujourd'hui. Pour le collège des représentants du personnel : pour la CGT, monsieur Rouvière, madame Sissoko, monsieur Pallas, présents. Pour FO, madame Escande, monsieur Vasseur, présents. Pour la CFDT, madame Thibaud, présente ; monsieur Courtade est excusé, il est remplacé par sa suppléante, madame Moulin, qui siège donc avec voix délibérative. Pour l'UNSA, monsieur Lhermite, présent. Ça fait huit représentants du personnel sur huit, le quorum est atteint.

M. Castagnet : Merci. Je salue aussi les experts qui vont nous rejoindre selon les points : monsieur Galmiche, directeur des routes et des mobilités, est là pour le point 1 ; le docteur Kerbrat, médecin du travail, et madame Maréchal, conseillère de prévention, arriveront pour le point sur les risques psychosociaux. Le secrétariat de séance est assuré par monsieur Oudin, et le secrétaire adjoint, c'est toujours monsieur Rouvière. Ça vous va, monsieur Rouvière ?

M. Rouvière (CGT, secrétaire adjoint) : Ça me va. Mais avant de commencer, monsieur le président, j'ai une déclaration liminaire au nom de l'intersyndicale… enfin, de la CGT et de FO, pas de toute l'intersyndicale.

M. Castagnet : Allez-y, mais je vous demande d'être raisonnable sur la durée, on a cinq points.

M. Rouvière : Je serai bref. Alors, nous voulons dire notre inquiétude face à la succession des réorganisations dans les services. En moins de deux ans, on a eu la réorganisation des maisons départementales des solidarités, celle de la direction de l'autonomie, et aujourd'hui on nous présente la fusion de centres d'exploitation routière. Les agents ont l'impression qu'on les déplace comme des pions, et le baromètre social qu'on va voir tout à l'heure le montre très bien. On demande que chaque réorganisation soit précédée d'une vraie étude d'impact sur les conditions de travail, présentée en formation spécialisée avant de venir en CST. Voilà. La déclaration complète sera remise au secrétariat pour être annexée au procès-verbal.

M. Castagnet : Très bien, elle sera annexée. Je ne vais pas répondre point par point maintenant, on aura l'occasion d'en discuter sur le point 1. Madame Escande, vous vouliez ajouter quelque chose ?

Mme Escande (FO) : Juste que FO s'associe à la déclaration, et qu'on regrette d'avoir reçu les documents du point 2 seulement huit jours avant. C'est le minimum réglementaire, mais pour une charte de télétravail qui touche plus de mille agents, c'est court.

M. Castagnet : C'est noté. On essaiera de faire mieux. Bien. Premier point, l'approbation du procès-verbal de la séance du 2 juillet. Est-ce qu'il y a des remarques ?

Mme Escande : Oui. Page six, sur les astreintes, il est écrit que FO « approuve le nouveau régime d'astreinte ». Ce n'est pas ce que j'ai dit. J'ai dit que FO approuvait la revalorisation, mais pas l'élargissement des astreintes aux agents de catégorie C du service des bâtiments. Je demande que ce soit corrigé.

M. Oudin : On a l'enregistrement, on vérifiera, mais de mémoire vous avez raison. On peut écrire : « FO approuve la revalorisation des indemnités d'astreinte mais s'oppose à leur extension aux agents de catégorie C du service des bâtiments ».

Mme Escande : Voilà, c'est exactement ça.

M. Castagnet : D'autres remarques ? Non. Je mets aux voix le procès-verbal ainsi modifié. Qui est contre ? Qui s'abstient ? Donc unanimité des deux collèges, le PV du 2 juillet est approuvé avec la correction de madame Escande. Monsieur Oudin, vous mettrez la version corrigée en ligne ?

M. Oudin : Oui, elle sera mise en ligne sur l'intranet avec les autres PV d'ici la fin octobre.

M. Castagnet : Bien. Alors, point 1, la réorganisation de la direction des routes et des mobilités, et plus précisément la fusion du centre d'exploitation routière de Lauzières avec celui de Montclar-d'Orbe. Monsieur Galmiche, je vous laisse présenter.

M. Galmiche (directeur des routes et des mobilités) : Merci monsieur le président. Bonjour à tous. Je vais faire court sur le contexte, vous avez le dossier. Aujourd'hui, l'agence routière Nord compte trois centres d'exploitation : Lauzières, Montclar-d'Orbe et Saint-Fréjus. Le centre de Lauzières, c'est quatorze agents, dont un chef de centre, dans un bâtiment de 1978 qui n'est plus aux normes, avec notamment de l'amiante dans la toiture du hangar et des vestiaires qui ne permettent pas d'accueillir des femmes dans des conditions correctes. On a deux agentes d'exploitation qui sont arrivées l'an dernier et qui se changent dans un bureau, ce n'est pas acceptable. La réfection complète du bâtiment a été chiffrée à 1,9 million d'euros. En face, le centre de Montclar-d'Orbe, qui est à dix-neuf kilomètres, a été rénové en 2022 et peut accueillir les quatorze agents avec une extension modulaire. Donc la proposition, c'est de regrouper les deux centres à Montclar-d'Orbe, avec une mise en œuvre au 1er janvier 2027. Le linéaire de routes reste le même, les circuits de patrouille sont redécoupés, et on ne supprime aucun poste. Je le redis parce que j'ai entendu des rumeurs : aucun poste supprimé.

M. Pallas (CGT) : Aucun poste supprimé, mais combien de postes non remplacés dans trois ans ?

M. Galmiche : Je ne peux pas vous répondre sur ce qui se passera dans trois ans, je vous réponds sur le projet qui est présenté aujourd'hui.

M. Pallas : Ben justement. Moi je suis agent d'exploitation à Lauzières depuis quatorze ans, je connais le secteur. Le problème, ce n'est pas le bâtiment, tout le monde est d'accord que le bâtiment est pourri. Le problème, c'est la viabilité hivernale. Quand il neige sur le plateau, depuis Montclar, il faut monter le col de la Bessière avant même de commencer à saler. Vous perdez trente, quarante minutes. Et les routes du nord du canton, elles seront traitées en dernier.

M. Galmiche : On a regardé ça. Les nouveaux circuits sont construits pour que le premier passage sur le réseau prioritaire soit fait dans les mêmes délais qu'aujourd'hui…

M. Pallas : Sur le papier.

M. Galmiche : … sur le papier, oui, c'est une étude, je ne vais pas vous dire le contraire. Mais elle a été faite avec les chefs de centre.

M. Castagnet : Laissez finir monsieur Galmiche, s'il vous plaît, vous aurez la parole après.

M. Galmiche : Je termine. Concernant les agents : chacun sera reçu en entretien individuel par la DRH et par moi-même. On a déjà regardé les temps de trajet domicile-travail : pour huit agents sur quatorze, le trajet s'allonge de moins de quinze minutes ; pour quatre agents, entre quinze et trente minutes ; et pour deux agents, c'est plus long, autour de quarante minutes. Pour ceux-là, on étudiera des solutions au cas par cas, éventuellement une mobilité vers Saint-Fréjus s'ils le souhaitent.

Mme Escande : Et l'indemnité ? Parce que quand on allonge de quarante minutes le trajet de quelqu'un qui gagne mille six cents euros, ça a un coût. FO demande une prime de restructuration pour l'ensemble des quatorze agents.

M. Oudin : Alors, je précise : il existe une indemnité de restructuration de service prévue par les textes, mais elle est encadrée, elle dépend notamment du changement de résidence administrative et de la distance. On ne peut pas promettre aujourd'hui qu'elle sera versée à tout le monde. Ce qu'on s'engage à faire, c'est d'examiner chaque situation lors des entretiens individuels.

Mme Escande : Donc c'est non.

M. Oudin : Ce n'est pas non, c'est : au cas par cas, dans le cadre réglementaire.

Mme Escande : Pour les agents, c'est non.

M. Castagnet : Je comprends la demande. Je ne vais pas prendre d'engagement en séance sur un dispositif indemnitaire, il faut qu'on le chiffre. On en reparlera.

Mme Thibaud (CFDT) : Moi j'ai deux questions. La première : le calendrier. Pourquoi le 1er janvier ? C'est en plein milieu de la saison de viabilité hivernale. Si on déménage un centre en janvier avec des agents qui ne connaissent pas encore leurs nouveaux circuits, et qu'il tombe vingt centimètres de neige, ça va être le chaos. La deuxième : qu'est-ce qu'on fait du sel ? Il y a un stock à Lauzières qui sert à tout le nord.

M. Galmiche : Sur le sel, on y a pensé. L'idée serait de garder l'aire de stockage de sel de Lauzières comme dépôt avancé pour l'hiver, mais ça suppose que le hangar à sel, qui est un bâtiment séparé, soit utilisable. Il faut qu'on fasse faire un diagnostic. Si le diagnostic est bon, on le garde ; sinon, on stockera tout à Montclar.

Mme Thibaud : Et le diagnostic, il sera fait quand ?

M. Galmiche : Il est commandé, on attend la date du bureau d'études. Je ne l'ai pas encore.

Mme Thibaud : Et sur le calendrier ?

M. Galmiche : Sur le calendrier… [silence] … je vais laisser le président répondre.

M. Castagnet : Écoutez, sur le calendrier, j'entends l'argument et je le trouve fondé. Je vous propose de modifier le projet : la mise en œuvre de la fusion serait reportée au 1er mars 2027, après le pic de la viabilité hivernale, au lieu du 1er janvier. Monsieur Galmiche, c'est tenable pour vous ?

M. Galmiche : C'est tenable. Ça décale un peu les travaux d'extension, mais c'est tenable.

M. Castagnet : Donc on modifie le projet soumis à l'avis : mise en œuvre au 1er mars 2027.

M. Rouvière : Ça ne change rien sur le fond.

M. Castagnet : Ça change le calendrier, c'est déjà quelque chose.

M. Lhermite (UNSA) : Moi je voudrais dire quelque chose. L'UNSA a rencontré les agents de Lauzières la semaine dernière. Ils ne sont pas tous contre, loin de là. Les deux collègues femmes dont parlait monsieur Galmiche, elles attendent ça depuis un an. Et plusieurs agents habitent plus près de Montclar que de Lauzières, en fait. Donc il ne faut pas présenter ça comme si tout le monde était contre.

M. Pallas : Personne n'a dit que tout le monde était contre.

M. Lhermite : Si, un peu, quand même. [rires]

M. Vasseur (FO) : Moi je voudrais revenir sur les circuits, parce que la carte du dossier n'est pas très lisible, on ne distingue pas bien les couleurs. Comment c'est organisé aujourd'hui, concrètement ?

M. Galmiche : Aujourd'hui, chaque centre a ses propres circuits de patrouille, sur un réseau classé par niveaux de priorité. Le niveau 1, ce sont les grands axes, les itinéraires de transport scolaire et les accès aux établissements de santé : ils sont traités en premier, dès le début de l'intervention. Le niveau 2, ce sont les liaisons entre les bourgs. Le niveau 3, c'est le reste du réseau, traité en journée, une fois les deux premiers niveaux dégagés. Le projet ne touche pas à cette hiérarchie. Ce qui change, c'est le point de départ des camions et la répartition des circuits entre les équipes regroupées. Et je m'excuse pour la carte : la version papier est effectivement peu lisible, la version numérique jointe au dossier est en couleur.

M. Vasseur : Et les équipes ? Les gars de Lauzières connaissent leurs routes par cœur, ceux de Montclar connaissent les leurs. Si on mélange tout, la première année va être compliquée.

M. Galmiche : C'est une crainte que les chefs de centre ont exprimée aussi. Ce n'est pas la direction qui compose les équipes, c'est le chef de centre, et rien n'empêche de garder des binômes qui connaissent bien leur ancien secteur. Mais je ne vais pas organiser les plannings en séance, ce n'est pas le lieu.

M. Pallas : Et le chef de centre de Lauzières ? Il devient quoi ?

M. Galmiche : Il garde son grade et ses fonctions d'encadrement. Sa situation sera vue lors de son entretien individuel, comme celle de ses collègues.

Mme Moulin (CFDT) : Je voudrais dire un mot sur les vestiaires, parce qu'on en parle comme d'un détail technique. Les deux collègues qui se changent dans un bureau depuis un an, c'est une situation que la CFDT a signalée plusieurs fois. Quand on se plaint de ne pas arriver à recruter des femmes dans les métiers de la route, il faut d'abord regarder les conditions d'accueil. Pour nous, c'est un argument qui compte dans l'appréciation du projet.

M. Galmiche : Je partage complètement. C'est même ce qui a pesé le plus lourd dans le choix entre la réfection et le regroupement.

Mme Ferrand (conseillère départementale) : Si je peux me permettre, du côté des élus du secteur. J'ai eu plusieurs maires du nord du canton au téléphone ces dernières semaines. Ils ne contestent pas l'état du bâtiment, ils le connaissent. Leur inquiétude, c'est la même que celle de monsieur Pallas : les délais d'intervention quand il neige. Pour eux, voir les camions sortir de Lauzières à cinq heures du matin, c'est rassurant.

M. Benslimane (conseiller départemental) : Et je rappelle quand même l'enjeu budgétaire. Une réfection complète à 1,9 million, pour un bâtiment qui resterait de toute façon mal situé, c'est une somme très importante au regard de ce qu'on consacre chaque année à l'entretien des routes du nord du département. Les élus ont aussi à rendre des comptes là-dessus.

M. Pallas : Je ne dis pas le contraire. Je dis juste que le bâtiment, on le paie une fois, alors que les retards de salage, on les paie tous les hivers. Et ce ne sont pas les élus qui finissent dans les fossés.

M. Castagnet : Monsieur Pallas, chacun a compris votre position, et elle est légitime. On ne va pas refaire tout le débat.

M. Castagnet : Bon. D'autres interventions ? Madame Sissoko.

Mme Sissoko (CGT) : Oui, je voulais revenir sur ce que disait monsieur Galmiche sur les temps de trajet. Vous avez une étude agent par agent ? Parce que nous, on ne l'a pas dans le dossier.

M. Galmiche : On l'a, mais elle est nominative, donc on ne l'a pas jointe.

Mme Sissoko : Vous pouvez l'anonymiser.

M. Galmiche : Oui, on peut l'anonymiser. Je vous la transmets.

Mme Sissoko : Avant le vote ?

M. Galmiche : Avant le vote d'aujourd'hui, non, ce n'est pas possible matériellement. Mais je vous la transmets avant le prochain CST, celui du 10 décembre.

M. Rouvière : Monsieur le président, je demande une suspension de séance de dix minutes, pour qu'on se concerte entre organisations avant le vote.

M. Castagnet : Accordée. On reprend à dix heures quarante.

[Suspension de séance de 10 h 28 à 10 h 41]

M. Castagnet : On reprend. Monsieur Rouvière, la suspension a été utile ?

M. Rouvière : Elle a été utile, on a échangé. Je fais juste une remarque avant le vote : on aurait aimé que ce projet passe d'abord en formation spécialisée, vu qu'il y a des questions d'amiante, de vestiaires, de conditions de travail. On n'a pas eu ça.

M. Castagnet : Le diagnostic amiante a été présenté à la formation spécialisée en mars, si ma mémoire est bonne.

M. Oudin : En mai. Le 12 mai.

M. Castagnet : En mai, pardon. Bon. Je vous propose de passer au vote. Je rappelle que l'avis porte sur le projet tel que modifié en séance, c'est-à-dire la fusion du centre d'exploitation de Lauzières avec celui de Montclar-d'Orbe, regroupement des quatorze agents à Montclar-d'Orbe, sans suppression de poste, avec une mise en œuvre au 1er mars 2027, et le maintien du dépôt de sel de Lauzières sous réserve du diagnostic. Et je rappelle aussi que le CST rend un avis : la décision appartient ensuite au président du conseil départemental. Collège des représentants du personnel d'abord. Qui est favorable ?

M. Oudin : Une voix pour, monsieur Lhermite, UNSA.

M. Castagnet : Qui s'abstient ?

M. Oudin : Deux abstentions, madame Thibaud et madame Moulin, CFDT.

M. Castagnet : Qui est contre ?

M. Oudin : Cinq contre : monsieur Rouvière, madame Sissoko, monsieur Pallas pour la CGT, madame Escande et monsieur Vasseur pour FO.

M. Castagnet : Donc avis défavorable du collège des représentants du personnel : cinq contre, deux abstentions, un pour. Collège des représentants de la collectivité ?

M. Oudin : Cinq pour, unanimité.

M. Castagnet : Avis favorable du collège employeur. L'avis des représentants du personnel n'étant pas défavorable à l'unanimité, il n'y a pas lieu à une nouvelle consultation. Le dossier sera soumis au président du Département.

Mme Escande : Je voudrais juste que le PV mentionne que FO votera contre aussi en commission permanente si le sujet y passe.

M. Castagnet : Madame Escande, FO ne siège pas en commission permanente. [rires] Mais votre position sera notée au PV, bien sûr.

Mme Escande : Vous m'avez comprise.

M. Rouvière : Pour la CGT, ce sera la même chose, je pense que personne n'en doute. [rires]

M. Castagnet : Personne n'en doute, monsieur Rouvière.

M. Castagnet : Monsieur Galmiche, merci, vous pouvez nous quitter si vous voulez.

M. Galmiche : Merci. Je confirme que l'étude anonymisée partira bien avant le 10 décembre. Et la DRH et moi, on prévoit les entretiens individuels avec les quatorze agents d'ici le 30 novembre.

M. Oudin : Oui, avant le 30 novembre, c'est calé de notre côté.

[Départ de M. Galmiche à 10 h 49]

M. Castagnet : Point 2, la modification de la charte du télétravail. Monsieur Oudin.

M. Oudin : Alors, rapidement, le bilan d'abord. Aujourd'hui, mille quatre cent vingt agents télétravaillent régulièrement sur deux mille huit cent soixante-dix agents… Pardon, je corrige tout de suite, j'ai inversé les chiffres : c'est mille deux cent quarante agents, pas mille quatre cent vingt. Mille deux cent quarante sur deux mille huit cent soixante-dix, donc à peu près 43 %. Le chiffre est juste dans le document, page trois, c'est moi qui me suis trompé.

Mme Moulin (CFDT) : Ça me paraissait beaucoup, en effet.

M. Oudin : Oui. Donc la charte actuelle, adoptée en 2022, prévoit un maximum de deux jours fixes par semaine. Ce qu'on vous propose : on garde les deux jours fixes maximum, et on ajoute un forfait annuel de vingt jours flottants, qui peuvent être posés en plus, dans la limite de trois jours télétravaillés sur une même semaine. Ensuite, on clarifie les conditions d'éligibilité des agents à temps partiel : un agent à 80 % pourra télétravailler un jour fixe, plus les jours flottants. Et on fixe un délai de prévenance quand le responsable doit annuler un jour de télétravail pour nécessité de service : aujourd'hui, il n'y a rien dans la charte, on propose vingt-quatre heures. Enfin, l'indemnité forfaitaire de télétravail reste versée au taux réglementaire, pas de changement. Entrée en vigueur au 1er janvier 2027.

M. Vasseur (FO) : Les jours flottants, c'est sur demande de l'agent, ou c'est imposé ?

M. Oudin : Sur demande de l'agent, validée par le responsable, dans l'outil de gestion des temps.

M. Vasseur : Validée comment ? Parce que dans certains services, je vous le dis, les demandes sont refusées sans explication.

M. Oudin : Tout refus devra être motivé, c'est déjà dans la charte, article 6.

M. Vasseur : C'est dans la charte, mais ce n'est pas appliqué. À la direction de l'enfance et de la famille, on a eu trois refus non motivés au printemps.

M. Oudin : Faites-nous remonter les situations, on les regardera.

Mme Sissoko : La CGT, elle, demande trois jours fixes. Beaucoup de collectivités autour l'ont fait. Les agents de l'autonomie, les instructeurs APA et PCH, ils font de l'instruction de dossiers toute la journée, ils peuvent le faire de chez eux. Et ils habitent loin, se loger à Valdrieu, c'est cher.

M. Castagnet : Trois jours fixes, ce n'est pas notre position. On a besoin de collectifs de travail. On a eu des retours de managers, des retours aussi du baromètre, sur l'isolement. Donc on reste à deux jours fixes, plus les jours flottants, ce qui permet d'aller jusqu'à trois certaines semaines. C'est un compromis.

Mme Sissoko : C'est un compromis que vous faites avec vous-même.

M. Lhermite : Pour l'UNSA, sur le principe des jours flottants, on est plutôt favorables. Ça répond à une vraie demande des agents qui ont des contraintes ponctuelles : un rendez-vous médical, un artisan qui passe, un enfant un peu malade qui ne justifie pas forcément un congé. Aujourd'hui, ces agents posent des congés ou des RTT pour ça. Avec les jours flottants, ils pourront travailler de chez eux ces jours-là.

M. Castagnet : C'est exactement l'esprit du dispositif.

Mme Moulin : Je voudrais témoigner aussi, parce que je travaille à la direction de l'autonomie. Chez nous, on télétravaille deux jours depuis la charte de 2022, et les équipes se sont organisées. Il y a un jour de présence commun, le mardi, où on fait les réunions d'équipe et les synthèses de dossiers. Ça fonctionne bien. Ma seule crainte avec les jours flottants, c'est que ce jour commun se vide petit à petit.

M. Oudin : C'est précisément pour ça que les jours flottants sont validés par le responsable : il garde la main sur les temps de présence collective de son équipe.

M. Vasseur : Et l'équipement ? Il y a encore des agents qui télétravaillent avec leur ordinateur personnel ?

Mme Arnaud (directrice générale adjointe ressources) : Non. Tous les agents en télétravail régulier sont équipés d'un ordinateur portable professionnel. Le déploiement s'est terminé l'an dernier.

M. Vasseur : Bon. Parce qu'on avait eu des remontées, au début, sur des collègues qui travaillaient sur la table de la cuisine avec leur propre portable.

Mme Arnaud : C'était vrai en 2022. Ça ne l'est plus.

Mme Thibaud : La CFDT, de son côté, trouve que le forfait de jours flottants, c'est une vraie avancée, on le demandait depuis deux ans. Par contre, vingt-quatre heures de prévenance pour une annulation, c'est trop court. Quelqu'un qui a organisé la garde de ses enfants autour de son jour de télétravail, si on lui dit la veille à dix-sept heures qu'il doit venir, il ne peut pas. On propose un amendement : quarante-huit heures, sauf urgence dûment justifiée.

M. Castagnet : Monsieur Oudin ?

M. Oudin : Quarante-huit heures, on peut l'accepter. Avec la mention « sauf urgence », bien sûr.

M. Castagnet : Alors on intègre l'amendement de la CFDT : délai de prévenance de quarante-huit heures, sauf urgence.

M. Lhermite : Et les agents des collèges ? Les agents techniques des collèges n'ont pas accès au télétravail, c'est logique pour l'entretien ou la restauration, mais il y a des gestionnaires administratifs, des secrétaires…

M. Oudin : Les agents des collèges qui sont sur des fonctions administratives, c'est un sujet compliqué, parce qu'il y a la double autorité avec le chef d'établissement.

M. Lhermite : Justement, c'est pour ça qu'il faut en parler.

M. Castagnet : On peut regarder ça, oui. Il faudrait sans doute en discuter avec l'Éducation nationale. On regardera.

M. Lhermite : Qui regardera, et quand ?

M. Castagnet : On regardera, monsieur Lhermite. Je ne vais pas vous donner une date aujourd'hui.

M. Rouvière : J'ajoute une chose sur l'indemnité forfaitaire. Elle ne couvre pas l'augmentation de l'électricité. On demande une prise en charge d'une partie de l'abonnement internet.

M. Oudin : Ce n'est pas prévu, et je ne crois pas que ce soit possible juridiquement en dehors du forfait.

M. Castagnet : Ce n'est pas dans le projet. Bien. Est-ce qu'on peut voter ? Je rappelle le projet modifié : maximum deux jours fixes par semaine, forfait annuel de vingt jours flottants, plafond de trois jours télétravaillés par semaine, délai de prévenance de quarante-huit heures sauf urgence pour l'annulation par le responsable, entrée en vigueur au 1er janvier 2027. Collège du personnel, qui est pour ?

M. Oudin : Cinq pour : madame Escande, monsieur Vasseur, madame Thibaud, madame Moulin, monsieur Lhermite.

M. Castagnet : Abstentions ?

M. Oudin : Trois abstentions, la CGT.

M. Castagnet : Contre ? Aucun. Avis favorable du collège du personnel. Collège employeur ?

M. Oudin : Cinq pour.

M. Castagnet : Avis favorable des deux collèges. Merci. La charte modifiée sera…

M. Oudin : Elle sera publiée sur l'intranet avec une note de service avant le 1er décembre, pour que les agents aient le temps de faire leurs demandes pour 2027. C'est moi qui m'en occupe.

Mme Escande : Et le bilan ? On avait demandé un bilan régulier.

M. Oudin : Je vous présenterai un bilan au bout d'un an d'application, donc au CST de début 2028.

Mme Escande : Début 2028, c'est loin.

M. Castagnet : Un an d'application, c'est le minimum pour avoir du recul. Point 3, les risques psychosociaux. J'invite le docteur Kerbrat et madame Maréchal à nous rejoindre. [bruit de chaises] Monsieur Benslimane, vous deviez partir ?

M. Benslimane (conseiller départemental) : Je dois partir vers onze heures quarante, j'ai la commission d'appel d'offres à midi. Je reste pour le début.

M. Castagnet : Très bien. Docteur Kerbrat.

Dr Kerbrat (médecin du travail) : Merci. Alors je vais vous présenter les résultats du baromètre social, qui a été réalisé en mai et juin, et ensuite madame Maréchal vous présentera le projet de plan de prévention. Je précise que ce point est présenté pour information : il n'y a pas d'avis à rendre aujourd'hui sur le plan, qui sera retravaillé en formation spécialisée.

M. Rouvière : C'est bien ce qu'on regrette, d'ailleurs.

Dr Kerbrat : Le taux de réponse est de 38 %, ce qui est correct pour une première édition, mais très variable selon les directions. Il est de 61 % à la direction de l'enfance et de la famille, et de 19 % à la direction des routes, où beaucoup d'agents n'ont pas de poste informatique. Les principaux enseignements : la charge de travail est jugée excessive par 54 % des répondants ; 41 % disent avoir été confrontés à des comportements agressifs d'usagers au cours des douze derniers mois, et ce chiffre monte à 72 % dans les maisons départementales des solidarités ; et enfin, 29 % des répondants déclarent un niveau de stress élevé ou très élevé. Je voudrais attirer votre attention sur les MDS, et particulièrement sur la MDS de Saint-Fréjus, où les indicateurs sont nettement dégradés, avec un incident sérieux en août, que vous connaissez.

Mme Escande : Oui, on le connaît, une collègue a été menacée à l'accueil. Et je vais être claire : FO demande que la formation spécialisée se rende sur place. Pas dans six mois. Maintenant.

M. Castagnet : Madame Maréchal, la formation spécialisée peut organiser une visite rapidement ?

Mme Maréchal (conseillère de prévention) : Oui, une délégation de la formation spécialisée peut se rendre sur place. Je propose le mardi 20 octobre, le matin. Il faut une délégation avec au moins un représentant du personnel et un représentant de la collectivité ; je l'accompagnerai et je m'occupe de l'organisation.

M. Castagnet : Qui se propose ?

M. Rouvière : Moi.

Mme Escande : Moi aussi, évidemment.

M. Castagnet : Et pour la collectivité, madame Ferrand, vous pourriez ?

Mme Ferrand (conseillère départementale) : Le 20 au matin, oui, je peux.

M. Castagnet : Très bien, donc délégation de la formation spécialisée à la MDS de Saint-Fréjus le mardi 20 octobre au matin : monsieur Rouvière, madame Escande, madame Ferrand, accompagnés de madame Maréchal, qui organise la visite. Le compte rendu de visite sera présenté à la prochaine formation spécialisée.

Mme Maréchal : Qui est le jeudi 19 novembre.

M. Castagnet : Le 19 novembre. Bien.

Mme Sissoko : Et en attendant, l'agent de sécurité à l'accueil de Saint-Fréjus ? Depuis août, il n'y a toujours rien.

M. Oudin : Un agent de sécurité est présent à titre provisoire les mardis et jeudis, jours de forte affluence, depuis le 14 septembre. C'est déjà en place, ça a été décidé au moment de l'incident.

Mme Sissoko : Deux jours sur cinq.

M. Oudin : Pour l'instant, oui. La visite permettra d'évaluer s'il faut étendre.

Mme Maréchal : Je continue sur le plan de prévention. Il comporte trois axes. Premier axe : la prévention des violences externes. On propose une formation à la gestion des situations d'agressivité pour tous les agents d'accueil des MDS, environ cent dix agents, avec les premières sessions dès novembre si le plan est validé. Deuxième axe : la charge de travail, avec un travail par direction sur les priorités, piloté par chaque directeur. Troisième axe : l'accompagnement des encadrants, avec un module de formation à la prévention des RPS pour les managers. Et parallèlement, je mets à jour le document unique d'évaluation des risques professionnels, le DUERP, pour intégrer tout ça : l'objectif est d'avoir une version à jour avant le 31 mars 2027.

M. Vasseur : La formation aux agressions, c'est bien, mais ça ne remplace pas des effectifs. À Saint-Fréjus, il manque deux travailleurs sociaux depuis le printemps.

Mme Arnaud (directrice générale adjointe ressources) : Les deux postes sont publiés, monsieur Vasseur. On a un problème d'attractivité sur les métiers du social, vous le savez, ce n'est pas propre à la Sarvèze.

M. Vasseur : On le sait. Mais pendant ce temps-là, ce sont les collègues présents qui absorbent les dossiers. Le deuxième axe, la charge de travail, il commence quand ?

Mme Maréchal : Il démarrera après la validation du plan, direction par direction. Je n'ai pas encore de calendrier par direction.

M. Rouvière : La CGT a une proposition concrète. On demande la mise en place d'une cellule d'écoute psychologique externe, accessible vingt-quatre heures sur vingt-quatre, comme ça existe dans d'autres départements. Les agents ne veulent pas toujours parler à la médecine du travail, qui est perçue comme… enfin, comme interne.

Dr Kerbrat : Je ne le prends pas mal. [rires] Mais je rappelle qu'on a déjà une psychologue du travail, à mi-temps.

M. Rouvière : À mi-temps pour deux mille huit cents agents.

M. Castagnet : La cellule d'écoute externe, ça a un coût, ça passe par un marché. Je ne suis pas contre l'idée, mais je ne peux pas la décider aujourd'hui. Madame Arnaud, vous pouvez faire chiffrer ?

Mme Arnaud : On peut regarder ce que ça coûterait, oui, je le fais dans le cadre de la préparation budgétaire 2027.

M. Rouvière : Donc ce n'est pas acté.

M. Castagnet : Ce n'est pas acté, c'est étudié. Je ne vais pas vous mentir.

M. Lhermite : Docteur, une question de méthode sur le baromètre. Les questions, elles ont été construites comment ? Parce que des agents m'ont dit qu'ils ne se reconnaissaient pas dans certaines formulations.

Dr Kerbrat : Le questionnaire comptait une soixantaine de questions, construites à partir des grilles habituellement utilisées pour les risques psychosociaux : la charge et l'intensité du travail, l'autonomie, la reconnaissance, les relations avec la hiérarchie et avec les collègues, le rapport aux usagers, et la conciliation entre vie professionnelle et vie personnelle. Il a été relu par la formation spécialisée au printemps, vous vous en souvenez peut-être. Certaines formulations sont générales, c'est le prix de la comparabilité entre les directions.

M. Lhermite : Et sur la reconnaissance, justement, il y a des résultats ? On n'en parle pas dans la synthèse.

Dr Kerbrat : C'est plutôt un point positif, et c'est sans doute pour ça qu'il est moins mis en avant. Une large majorité des répondants se disent soutenus par leurs collègues directs, et la relation avec l'encadrant de proximité est jugée bonne dans la plupart des services. Ce qui ressort le plus négativement, ce sont la charge de travail et le rapport aux usagers, comme je l'ai dit.

M. Pallas : Pour les routes, avec 19 % de réponses, je ne vois pas bien ce qu'on peut en tirer. Les collègues des centres n'ont pas d'ordinateur, ils ont reçu un lien par mail sur une adresse qu'ils ne consultent jamais.

Dr Kerbrat : Vous avez raison, et je le dis clairement : avec ce taux, je ne tire aucune conclusion pour la direction des routes. Les résultats ne sont pas représentatifs.

Mme Maréchal : C'est une limite connue des questionnaires en ligne dans les services techniques. Ce n'est pas propre à la Sarvèze.

Mme Sissoko : Ce qui veut dire que les agents qui ont peut-être les conditions de travail les plus dures physiquement sont ceux qu'on entend le moins.

Dr Kerbrat : C'est une façon juste de le dire.

Mme Thibaud : Une question pour le docteur Kerbrat. Est-ce que les résultats par direction, en détail, peuvent être communiqués ? On n'a que la synthèse globale.

Dr Kerbrat : Oui, je peux présenter les résultats détaillés par direction, en respectant le seuil d'anonymat — on ne descend pas en dessous de dix répondants. Je propose de le faire à la formation spécialisée du 19 novembre.

M. Castagnet : Parfait. [M. Benslimane se lève] Monsieur Benslimane nous quitte.

M. Benslimane : Excusez-moi, bonne fin de séance.

[Départ de M. Benslimane à 11 h 42]

M. Castagnet : Le collège employeur compte donc quatre membres pour la suite. D'autres questions sur le point 3 ? Monsieur Pallas.

M. Pallas : Juste pour revenir au point 1, parce que je n'ai pas eu de réponse. Le dépôt de sel de Lauzières, si le diagnostic est mauvais, il se passe quoi pour l'hiver 2027-2028 ? On sale tout le nord depuis Montclar ?

M. Castagnet : Monsieur Pallas, on a voté sur le point 1. Monsieur Galmiche est parti.

M. Pallas : Je sais, mais c'est une vraie question.

M. Castagnet : C'est une vraie question. Monsieur Oudin, vous la transmettez à monsieur Galmiche, et il répondra par écrit aux organisations syndicales.

M. Oudin : Je la lui transmets aujourd'hui.

M. Castagnet : Bien. Sur le point 3, je rappelle encore une fois qu'il n'y a pas de vote : c'est une information, le plan reviendra pour avis après le travail en formation spécialisée. Point 4, le plan de formation 2027. Madame Arnaud.

Mme Arnaud : Je serai rapide puisque les documents sont détaillés. Le plan de formation 2027 reprend les orientations du plan pluriannuel. Les priorités : la prévention des risques, notamment ce qu'on vient d'évoquer sur les agressions et sur les RPS pour les encadrants ; la transition numérique, avec l'accompagnement au nouveau logiciel de gestion des aides sociales ; et la préparation aux concours et examens professionnels. Le budget prévisionnel est de 640 000 euros, en dehors de la cotisation au CNFPT. On a aussi intégré, à la demande de la CFDT l'an dernier, des formations aux premiers secours en santé mentale.

Mme Thibaud : On s'en félicite.

M. Vasseur : Pour FO, on voudrait que les agents des routes aient accès aux formations en semaine, pas le samedi.

Mme Arnaud : C'est le cas, il n'y a pas de formation le samedi.

M. Vasseur : Il y en a eu une en mars.

Mme Arnaud : C'était une exception, liée à la disponibilité du formateur. On fera attention.

M. Pallas : Et les formations CACES, pour les engins ? Il y a des agents qui attendent depuis deux ans.

Mme Arnaud : Elles sont dans le plan, page neuf, avec quarante-deux places en 2027 contre vingt-huit cette année.

M. Pallas : Bon. C'est mieux.

Mme Moulin : Sur les premiers secours en santé mentale, je voulais remercier la direction, parce que c'était une demande que nous portions depuis longtemps. Est-ce que vous pouvez rappeler en quoi consiste la formation, pour ceux qui ne la connaissent pas ?

Mme Arnaud : C'est une formation de deux jours qui apprend à repérer les signes d'une souffrance psychique chez un collègue ou chez un usager, à engager le dialogue et à orienter vers les bons interlocuteurs. Ce n'est pas une formation de soignant, c'est une formation de premier secours, au même titre que le secourisme classique.

Dr Kerbrat : Et je confirme que c'est très complémentaire de ce qu'on fait en médecine du travail.

Mme Sissoko : Sur le nouveau logiciel des aides sociales, les collègues de l'autonomie en entendent parler depuis un an et ils sont inquiets. Ils ont connu le dernier changement de logiciel, en 2019, et ça s'était très mal passé, avec des semaines de retard dans l'instruction des dossiers.

Mme Arnaud : C'est justement pour ça que l'accompagnement est une priorité du plan. L'expérience de 2019 a servi : les formations sont prévues avant la bascule, par petits groupes, avec des sessions de pratique sur des dossiers fictifs, et pas seulement une démonstration en amphithéâtre.

Mme Thibaud : Et sur la préparation aux concours, est-ce que les agents pourront toujours les suivre sur leur temps de travail ?

Mme Arnaud : Oui, dans les mêmes conditions qu'aujourd'hui. Il n'y a pas de changement sur ce point.

M. Castagnet : On vote ? Avis sur le plan de formation 2027. Collège du personnel ?

M. Oudin : Huit pour, unanimité.

M. Castagnet : Collège employeur ?

M. Oudin : Quatre pour, unanimité des présents.

M. Castagnet : Avis favorable unanime des deux collèges. Madame Arnaud, vous le transmettrez à la délégation régionale du CNFPT ?

Mme Arnaud : Oui, avant le 31 décembre, comme chaque année.

M. Castagnet : Point 5, les questions diverses. J'ai reçu deux questions écrites. La première, de la CGT, sur le chauffage du bâtiment B, rue des Tanneurs.

Mme Sissoko : Oui. Les agents du bâtiment B, c'est la direction de l'autonomie, ils ont eu dix-sept degrés la semaine dernière, alors qu'il ne fait pas encore froid. Qu'est-ce que ce sera en janvier ? La chaudière est en panne une semaine sur deux.

M. Oudin : On a eu le signalement. Le service des bâtiments doit intervenir pour remplacer le brûleur. Je m'engage à ce que l'intervention ait lieu avant le vendredi 16 octobre, et je vous en confirmerai la date par mail.

Mme Sissoko : On a déjà entendu ça au printemps.

M. Oudin : Cette fois, la pièce est commandée.

Mme Sissoko : Et je précise que ce ne sont pas seulement les bureaux de l'étage qui sont concernés. À l'accueil du rez-de-chaussée, avec la porte d'entrée qui s'ouvre sans arrêt, les collègues gardent leur manteau toute la matinée.

M. Oudin : C'est bien noté. Le brûleur concerne l'ensemble du bâtiment, l'accueil compris.

M. Castagnet : Deuxième question, de l'UNSA, sur le stationnement à l'Hôtel du Département.

M. Lhermite : Oui. Depuis la fermeture du parking de la rue Carnot pour travaux, les agents qui arrivent après huit heures trente ne trouvent plus de place. Les agents à temps partiel, ceux qui déposent les enfants, ceux qui sont en horaires décalés. On demande des places réservées ou une convention avec le parking public.

M. Castagnet : Une convention avec le parking des Halles, on y a pensé. Ça a un coût aussi. Madame Arnaud ?

Mme Arnaud : Je peux demander un devis au gestionnaire du parking.

M. Castagnet : Faites, oui. Mais je ne prends pas d'engagement sur la convention elle-même.

M. Lhermite : Dans quel délai, le devis ?

Mme Arnaud : Je n'ai pas la main sur leurs délais. Dès qu'on l'a, on le partage.

Mme Escande : J'ai une question orale, si vous permettez, qui n'était pas dans les questions écrites. Le compte épargne-temps. Les agents qui ont atteint le plafond de soixante jours perdent des jours, notamment aux routes, à cause des astreintes. On demande une ouverture de la monétisation.

M. Castagnet : Ce n'est pas à l'ordre du jour, madame Escande, et c'est un sujet qui demande une délibération. Je ne peux pas en débattre sans document. Monsieur Oudin, vous l'inscrivez à l'ordre du jour du prochain CST, avec une note ?

M. Oudin : Je l'inscris pour le 10 décembre, avec une note sur les soldes de CET par direction.

Mme Escande : Merci.

M. Rouvière : Et sur la déclaration liminaire, monsieur le président ? Sur l'étude d'impact systématique avant chaque réorganisation ?

M. Castagnet : Je vous ai entendu. C'est une demande légitime. Mais je ne vais pas créer une procédure en fin de séance. On en reparle avec la DRH dans le cadre de l'agenda social.

M. Rouvière : On le notera au PV, alors, que ce n'est pas acté.

M. Castagnet : Notez-le.

Mme Ferrand : Si je peux me permettre un mot, monsieur le président. Je voulais remercier les agents des MDS, au nom des élus, parce qu'on parle beaucoup de chiffres mais ce qu'ils vivent au quotidien est difficile.

M. Castagnet : Merci madame Ferrand. Je m'associe à vos propos. Alors, avant de clore, je vous rappelle la date du prochain CST. Je vous avais indiqué le 3 décembre dans la convocation…

M. Oudin : Le 10, monsieur le président. Le 3, c'était la date initiale, elle a été changée à cause de la session du conseil départemental.

M. Castagnet : Le jeudi 10 décembre, pardon, à neuf heures trente. Merci monsieur Oudin. Et la formation spécialisée se réunit le jeudi 19 novembre. Plus de questions ? Je vous remercie. La séance est levée.

[Fin de l'enregistrement : 12 h 21]
```

</details>

### `entree.nb_mots` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-5159
+6621
```

**Ancienne valeur** :

5159

**Nouvelle valeur** :

6621

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

## CR-021 — Compte rendu (difficile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : compter_mots(transcription) = 6571 > 6500, égal à entree.nb_mots (v1.0 : 4739). Les 307 lignes v1.0 sont toutes présentes, inchangées et dans le même ordre ; 69 paragraphes ajoutés (1832 mots), indices v1.1 : 30, 38-40, 52-54, 68-70, 80-94, 100, 112-114, 154-166, 180, 188-196, 222-224, 232-236, 254, 258-268, 278, 282, 300, 312, 318-320, 328, 334-346, 364-366, 372-374, 390, 406-408, 418-420, 430-432, 440. Aucun nouveau vote, aucune nouvelle décision ni action, aucune proposition non retenue à ajouter aux pièges ; chiffres cohérents (9 000 €, 7-12-2, 768 h, 74 jours, 30 élèves). Présences respectées (Marchetti après 17 h 50, Lacombe à partir du point 5, Arnaud-Poitevin muette après 19 h 05, absents muets) ; répliques suivantes cohérentes, y compris l'alinéa sans nom « Ensuite, une DBM… » qui reste rattaché à Ferhat (l. 320). participants_reference, decisions_reference, actions_reference et pieges identiques à v1.0 et toujours exacts ; consigne, type_reunion, provenance, licence_source, fictif, theme, difficulte et parametres inchangés ; seuls version_item 1→2, nb_mots et la transcription changent. Réserves mineures : l. 86 Tessier dit que le téléphone est « déjà » rendu en fin de journée, en légère tension avec les confiscations de plusieurs jours évoquées par Léna ; « Des questions ? Non ? » de Cordier juste après les questions des l. 154-166 ; Saintonge, invitée pour le point voyages, intervient aussi au point 4 (l. 254, aucun départ noté) ; « Personne ne fouille les sacs » (l. 90) et fiches sanitaires (l. 166) sont des pratiques existantes, pas des décisions ni des actions.

Champs changés : `entree.transcription`, `entree.nb_mots`, `version_item`.

### `entree.transcription` (modifié)

Différences, ligne à ligne :

```diff
--- ancien
+++ nouveau
@@ -30,2 +30,4 @@
 
+Mme Delorme : Je m'en souvenais parce qu'on en avait discuté avec les élèves du foyer, ils étaient contents de cette hausse.
+
 Mme Cordier : Très bien, on corrige : 1 800 euros et non 1 500. Le procès-verbal corrigé sera mis en ligne sur l'ENT. D'autres remarques ? Non. Je mets aux voix le procès-verbal ainsi corrigé. Qui est contre ? Qui s'abstient ? Il est adopté à l'unanimité des vingt présents. Merci.
@@ -36,2 +38,6 @@
 
+M. Lebrun : Et contre qui ?
+
+M. Marchetti : Contre le collège de Lézonville, en handball. Les filles ont été formidables.
+
 Mme Cordier : Bienvenue, M. Marchetti. Nous sommes donc vingt et un. On vient d'adopter le PV du 30 juin, on passe au point 2.
@@ -46,2 +52,6 @@
 
+Mme Picot : Et je me permets d'ajouter, pour les agents, que des casiers à l'entrée, ça voulait dire aussi quelqu'un pour les ouvrir et les fermer matin et soir. On était inquiets, honnêtement.
+
+Mme Cordier : C'était une des difficultés, en effet. Mais encore une fois, ce n'est plus du tout d'actualité.
+
 M. Ostrowski : Merci de le préciser, parce que beaucoup de parents nous en ont parlé, des casiers. Mais sur le fond, nous, les parents, on n'est pas tous d'accord sur la pause méridienne. Les élèves de troisième, ils ont quatorze, quinze ans. Leur interdire le téléphone de 8 heures à 17 heures, y compris au foyer, c'est un peu…
@@ -58,2 +68,6 @@
 
+Mme Sy : Onze incidents, c'est beaucoup pour un collège comme le nôtre.
+
+M. Tessier : C'est beaucoup, oui. Et ce sont seulement ceux qui ont été portés à notre connaissance.
+
 Léna (élève) : Je peux dire quelque chose ?
@@ -66,2 +80,18 @@
 
+Mme Delorme : Une question de parent. Beaucoup d'entre nous ont donné un téléphone à leur enfant pour pouvoir le joindre à la sortie, surtout ceux qui prennent le car. Le téléphone pourra être rallumé dès qu'ils sortent du collège ?
+
+M. Vauquelin : Oui, la règle s'applique de l'entrée à la sortie. Une fois le portail franchi, le collège n'a plus à intervenir. Et en cas d'urgence pendant la journée, les familles appellent la vie scolaire, comme aujourd'hui.
+
+Mme Bellamy : Je voudrais aussi dire, du côté des enseignants, que l'usage pédagogique reste possible, et c'est important. Moi j'utilise parfois les téléphones pour des quiz ou pour enregistrer une production orale en langue. Ce sera toujours possible, sur autorisation, comme c'est écrit dans le projet.
+
+M. Tessier : Et pour la confiscation, je précise que c'est déjà comme ça qu'on procède aujourd'hui à la vie scolaire : le téléphone est déposé au bureau et l'élève le récupère en partant. Ce qui change, c'est qu'il n'y aura plus de confiscation sur plusieurs jours, comme le disait Léna.
+
+M. Benslimane : Pour les agents d'accueil, je voudrais juste qu'on soit clairs : on n'aura pas à fouiller les sacs à l'entrée.
+
+Mme Cordier : Non, évidemment. Personne ne fouille les sacs. La règle repose sur la responsabilité des élèves et sur la présence des adultes, en classe et dans la cour.
+
+Mme Kasprzak : Et franchement, dans les collèges voisins qui l'ont fait l'an dernier, les collègues disent que la cour a changé. Les élèves rejouent au ballon, ils se parlent, ils s'ennuient un peu aussi, et ce n'est pas plus mal.
+
+M. Ostrowski : Je ne doute pas que ça ait des effets positifs. Je dis juste que les troisièmes ne sont pas des sixièmes.
+
 Mme Sy : Et quand c'est remis au représentant légal, ça veut dire quoi concrètement ? Les parents doivent venir au collège ? Parce qu'avec le travail…
@@ -70,2 +100,4 @@
 
+Mme Sy : D'accord. Au moins, les choses sont claires pour tout le monde.
+
 Mme Chaumont : Madame la principale, nous demandons une suspension de séance de dix minutes. Les représentants des parents voudraient se concerter avant le vote.
@@ -80,2 +112,6 @@
 
+Mme Kasprzak : Je peux réagir ? Je comprends l'idée, mais pour nous la difficulté reste la même : au foyer, le midi, personne ne peut surveiller soixante écrans.
+
+Mme Chaumont : On l'entend. Je précise seulement que l'amendement a été rédigé pendant la suspension, à partir de ce que disait Léna sur le conseil de la vie collégienne. C'est une position d'équilibre, ce n'est pas un refus du règlement.
+
 Mme Cordier : Très bien. Je mets d'abord aux voix l'amendement, puis le règlement intérieur dans son ensemble. Je rappelle que ce sont des votes à main levée, sauf si quelqu'un demande un vote à bulletin secret.
@@ -118,2 +154,16 @@
 
+Mme Varenne : Je peux témoigner, j'avais accompagné ce séjour il y a deux ans, dans le même centre. Les élèves en parlent encore. L'encadrement sur place est très sérieux, et le centre a l'habitude d'accueillir des collèges.
+
+Yanis : Mon frère y est allé, il a dit que c'était le meilleur voyage du collège. [rires]
+
+M. Marchetti : Pour le programme, c'est ski de fond le matin, et l'après-midi raquettes ou découverte du milieu montagnard avec un animateur nature. Il y a aussi une veillée chaque soir. Le programme détaillé est en annexe du dossier que vous avez reçu.
+
+Mme Sy : Et pour les élèves qui n'ont jamais fait de ski, il y a des groupes de niveau ?
+
+M. Marchetti : Oui, les moniteurs font des groupes le premier jour. Pour le ski de fond, on part vraiment de zéro, il n'y a pas besoin d'expérience.
+
+Mme Picot : Et pour les élèves qui ont un régime alimentaire particulier, le centre est au courant ?
+
+M. Marchetti : Oui, on transmet les fiches sanitaires avant le départ, et le centre gère les régimes. Il l'a toujours fait.
+
 Mme Cordier : Des questions ? Non ? Je mets aux voix le séjour neige des cinquièmes, avec son budget et la participation des familles de 295 euros. Qui est contre ? Qui s'abstient ? Adopté à l'unanimité des vingt et un présents.
@@ -130,2 +180,4 @@
 
+Mme Saintonge : Nous avons construit le dossier en tenant compte des critères du département : un vrai projet linguistique, le carnet de voyage, les cours avec un établissement partenaire. On a de bonnes chances, mais je sais que rien n'est garanti.
+
 M. Pellerin : Alors justement, 380 euros, c'est déjà beaucoup. Et si l'aide n'arrive pas, on passe à 500 euros pour les familles ? Nous on propose de plafonner la participation des familles à 350 euros, quoi qu'il arrive.
@@ -136,2 +188,12 @@
 
+Mme Delorme : Et l'hébergement en familles, c'est encadré comment ? Des parents nous ont posé la question, ça les inquiète un peu.
+
+Mme Saintonge : C'est un organisme spécialisé qui sélectionne les familles, il travaille avec des établissements scolaires depuis longtemps. Les élèves sont hébergés par deux ou trois, jamais seuls, et le point de rendez-vous du matin est à proximité des familles. Les enseignants ont un téléphone joignable jour et nuit. On l'avait fait il y a trois ans à Salamanque, et ça s'était très bien passé.
+
+Mme Chaumont : C'est rassurant. Et pédagogiquement, il y a quoi au programme ?
+
+Mme Saintonge : La visite de l'Alcazar et de la cathédrale à Séville, l'Alhambra à Grenade, et une matinée dans un établissement partenaire, où les élèves suivent des cours avec des correspondants. Ils préparent en amont un carnet de voyage en espagnol, qui est évalué au troisième trimestre. C'est vraiment un projet construit avec les cours, pas seulement une sortie touristique.
+
+Léna : Les élèves de quatrième en parlent beaucoup, en tout cas. Ils ont hâte.
+
 Mme Cordier : Ce que je vous propose, c'est de voter le voyage sous réserve de l'obtention de l'aide départementale de 120 euros. Si l'aide est refusée, le voyage reviendra devant le conseil d'administration, on rediscutera du financement à ce moment-là. Il n'y aura pas d'augmentation automatique de la participation des familles.
@@ -160,2 +222,6 @@
 
+Mme Roussel : Je comprends la décision. On ne part pas à l'étranger avec seulement trois adultes.
+
+Mme Kasprzak : Voilà. Et je préfère le dire maintenant plutôt que d'annuler en mars, avec des familles qui auraient déjà versé des acomptes.
+
 Mme Cordier : On ne vote donc pas le séjour à Londres ce soir. Si Mme Kasprzak revient avec un projet complet, on l'examinera, mais rien n'est fixé. Enfin, le programme des sorties sans nuitée : vous avez le tableau en annexe, il y a quatorze sorties, théâtre, musée, sortie géologie pour les quatrièmes, cross départemental, etc. Toutes sont gratuites pour les familles, financées sur les crédits pédagogiques ou par le foyer. Des remarques ?
@@ -166,2 +232,8 @@
 
+Mme Varenne : Pour la sortie géologie des quatrièmes, je voulais remercier le foyer : c'est grâce à lui qu'elle reste gratuite pour les familles.
+
+Mme Chaumont : Et le foyer, c'est surtout grâce aux ventes de gâteaux et à la tombola de fin d'année. Les familles se mobilisent beaucoup.
+
+Mme Cordier : Merci à elles, vraiment.
+
 M. Pellerin : Excusez-moi, je reviens deux secondes sur le règlement intérieur. Une question qu'on m'a posée pendant la suspension : un élève qui a un problème de santé, un diabète par exemple, avec une application sur son téléphone ?
@@ -182,4 +254,18 @@
 
+Mme Saintonge : Je confirme pour l'espagnol : à trente et un, chaque élève a à peine une minute de prise de parole par séance.
+
 Mme Varenne : En technologie aussi, on a 15 postes informatiques pour 30 élèves.
 
+Mme Roussel : Et en français, même si on n'est pas concernés par les dédoublements, à trente en quatrième, la correction des copies et le suivi individuel deviennent très difficiles. Je le dis en tant qu'enseignante, pas en tant que secrétaire de séance. [rires]
+
+M. Tessier : Du côté de la vie scolaire, je confirme que le niveau quatrième concentre une bonne partie des incidents depuis la rentrée. Ce n'est pas seulement une question d'effectifs, mais des classes à trente, avec des élèves qui ont des besoins très différents, c'est plus difficile à tenir pour tout le monde.
+
+M. Ostrowski : Les parents le voient aussi. Plusieurs familles de quatrième nous disent que leurs enfants ont du mal à suivre en sciences, et qu'ils n'arrivent pas à poser leurs questions en classe.
+
+Mme Cordier : Pour que tout le monde comprenne bien, je rappelle comment fonctionne la dotation. Les heures postes, ce sont les heures assurées par des enseignants affectés au collège. Les heures supplémentaires années, ce sont des heures payées en plus, réparties sur l'année. Et les heures de marge, c'est ce qu'on peut utiliser librement, une fois assurés les horaires réglementaires, pour les dédoublements ou des dispositifs comme « Devoirs faits ». Ce que je ne peux pas faire, c'est créer des heures qu'on ne nous a pas données.
+
+Mme Varenne : En technologie, on fait tourner les élèves par demi-groupes sur les postes pendant que les autres travaillent sur papier. Ça fonctionne, mais chaque élève perd la moitié de son temps de pratique.
+
+M. N'Diaye : On le sait bien, et ce n'est pas un reproche à la direction.
+
 Mme Cordier : J'entends tout ça et je partage le constat. J'ai demandé en juin une dotation complémentaire, la DSDEN nous a accordé 6 heures, qui sont déjà dans les 768. Je n'ai pas eu d'autre réponse.
@@ -192,4 +278,8 @@
 
+Mme Cordier : Merci madame. C'est important que le département partage le constat.
+
 M. Lebrun : La commune aussi.
 
+Léna : Et au conseil de la vie collégienne, les délégués de quatrième ont dit la même chose : en sciences, à trente, ceux du fond ne voient rien des expériences.
+
 Mme Cordier : Je précise que les membres de l'administration, c'est-à-dire moi-même, M. Vauquelin, Mme Ferhat et M. Tessier, ne prennent pas part au vote sur cette motion. Ce n'est pas un désaccord sur le fond, c'est que la motion s'adresse à notre hiérarchie et que c'est moi qui la transmettrai.
@@ -210,2 +300,4 @@
 
+Mme Kasprzak : D'accord, merci.
+
 Point 5 — Budget
@@ -220,2 +312,4 @@
 
+Mme Cordier : Ne vous excusez pas, on sait ce que c'est. [rires]
+
 Mme Cordier : Mme Ferhat, le budget.
@@ -224,2 +318,6 @@
 
+M. Pellerin : Une baisse de 3 %, alors que le prix de l'énergie continue d'augmenter, ça va être serré.
+
+Mme Ferhat : Ça va être serré, oui. Les arbitrages figureront dans le budget primitif.
+
 Ensuite, une décision budgétaire modificative pour vote, la DBM n° 3. Le four mixte de la cuisine est hors service depuis le 21 septembre. Le réparateur nous dit que la carte électronique et la sonde sont à changer, c'est presque le prix d'un four neuf, et le modèle n'est plus fabriqué. Mme Picot pourra vous le confirmer.
@@ -230,2 +328,4 @@
 
+Mme Picot : Les élèves sont gentils, ils ne se plaignent pas trop. Mais les plats chauds leur manquent, surtout maintenant qu'il commence à faire froid.
+
 Mme Ferhat : Le remplacement coûte 12 400 euros toutes taxes comprises, installation comprise. Je vous propose de le financer par un prélèvement sur le fonds de roulement du service de restauration et d'hébergement. Le fonds de roulement est aujourd'hui de 186 000 euros, soit environ 74 jours de fonctionnement. Après le prélèvement, on serait à 173 600 euros.
@@ -234,2 +334,16 @@
 
+Mme Delorme : Pardon, une question peut-être naïve. Le fonds de roulement, c'est quoi exactement ? C'est de l'argent qu'on a en réserve ?
+
+M. Lacombe : Ce n'est pas naïf du tout. Le fonds de roulement, ce sont les réserves accumulées par le collège au fil des exercices, quand les recettes ont été supérieures aux dépenses. Il sert à faire face aux décalages de trésorerie et aux dépenses imprévues, comme justement une panne de four. Celui du service de restauration et d'hébergement est suivi à part, parce qu'il provient des repas payés par les familles et qu'il doit servir à la restauration.
+
+Mme Delorme : D'accord. Donc on n'utilise pas l'argent des autres activités du collège pour la cantine.
+
+M. Lacombe : Exactement : c'est l'argent de la restauration qui revient à la restauration.
+
+M. Pellerin : Et soixante-quatorze jours, c'est un niveau normal pour un collège ?
+
+M. Lacombe : C'est un niveau confortable. Beaucoup de collèges du département se situent plutôt entre quarante-cinq et soixante jours, donc vous avez de la marge, même après le prélèvement.
+
+Mme Picot : Et je peux vous dire qu'en cuisine, on a hâte. Faire tous les repas du midi avec un petit four et des plaques, ce n'est pas tenable longtemps.
+
 M. Pellerin : Une question de principe. Un four de cuisine collective, c'est de l'équipement, ce n'est pas au département de le payer ? Le département a un plan d'équipement pour les collèges. Pourquoi on ne demande pas à être inscrits sur le plan 2027 plutôt que de puiser dans nos réserves ?
@@ -250,2 +364,6 @@
 
+Mme Bellamy : « Collège au cinéma », ce sont trois films par an pour chaque classe inscrite, et les élèves adorent. Pour certains, c'est la seule occasion d'aller au cinéma.
+
+M. Lebrun : C'est justement pour ça que la commune continue à le financer.
+
 Mme Ferhat : Merci à la commune. Deux autres délibérations. D'abord, la convention d'utilisation du gymnase municipal pour l'année 2026-2027 : la commune met le gymnase à disposition pour les cours d'EPS, il faut autoriser Mme la principale à signer.
@@ -254,2 +372,6 @@
 
+M. Lebrun : Et la commune a refait l'éclairage du gymnase cet été, au passage. [rires]
+
+Mme Cordier : Ce dont nous vous remercions, monsieur Lebrun.
+
 Mme Cordier : Je mets aux voix l'autorisation de signer la convention d'utilisation du gymnase municipal pour 2026-2027. Contre ? Abstentions ? Adoptée à l'unanimité des vingt présents.
@@ -268,2 +390,4 @@
 
+Mme Cordier : Merci, c'est précieux d'avoir l'agent comptable pour l'examen du budget primitif.
+
 Point 6 — Questions diverses
@@ -282,2 +406,6 @@
 
+Mme Sy : Ce qui inquiète surtout les familles, c'est que certains élèves se retiennent toute la journée. Ce n'est pas anodin, surtout pour les plus jeunes.
+
+Mme Picot : On en est bien conscients, ce n'est pas de gaieté de cœur qu'on ferme. Quand l'équipe est au complet, le bâtiment C reste ouvert toute la journée, comme les autres années.
+
 Mme Cordier : Yanis, pour les élèves ?
@@ -290,2 +418,6 @@
 
+Yanis : Oui, c'est pour les livres et les classeurs. En conseil de la vie collégienne, on a pesé des cartables de sixièmes, il y en avait qui pesaient presque dix kilos.
+
+Mme Delorme : C'est vrai, mon fils était en sixième l'an dernier, il rentrait le soir avec le dos en compote.
+
 Mme Ferhat : Je peux chiffrer des casiers pour les sixièmes et le présenter dans le cadre du budget primitif 2027, pour le CA du 26 novembre.
@@ -298,2 +430,6 @@
 
+Mme Kasprzak : Je confirme pour la B12, j'y ai cours le lundi à 8 heures, et les élèves gardent leur manteau pendant toute la première heure.
+
+Mme Cordier : Le signalement du 28 septembre porte bien sur la B12.
+
 M. Lebrun : Oui, alors moi, c'était pour vous informer que la commune organise le forum des associations samedi… non, c'était samedi dernier, pardon, il est passé. [rires] Non, ce que je voulais dire, c'est que la commune réfléchit à un « pédibus » pour les élèves du centre-bourg, mais c'est vraiment au stade de l'idée, on n'a rien décidé en conseil municipal.
@@ -304,2 +440,4 @@
 
+Mme Delorme : Oui, je m'associe. Ces années ont été très riches. On a vu passer beaucoup de dossiers, la réforme, les années de crise sanitaire aussi, et on a toujours été écoutés, même quand on n'était pas d'accord.
+
 Mme Cordier : Merci à vous deux pour votre engagement pendant ces années. Merci à tous. La séance est levée, il est 20 h 05.
```

<details><summary>Ancienne valeur complète</summary>

```text
Transcription — Conseil d'administration du collège Les Hautes-Bruyères, Saint-Aubin-sur-Lézon
Mardi 6 octobre 2026, 17 h 30, salle polyvalente
Enregistrement réalisé pour faciliter la rédaction du procès-verbal. Secrétaire de séance : Mme Roussel.

Mme Cordier (principale, présidente) : Bon, il est 17 h 35, je crois qu'on peut commencer. Bonsoir à toutes et à tous. Je vous remercie d'être là, c'est le dernier conseil d'administration de cette mandature, puisque les élections des représentants des parents ont lieu ce vendredi 9 octobre et celles des personnels dans la foulée. Je fais l'appel, comme d'habitude, pour vérifier le quorum. Pour l'administration : moi-même, M. Vauquelin, principal adjoint, Mme Ferhat, adjointe gestionnaire, M. Tessier, CPE. Pour les collectivités : Mme Arnaud-Poitevin, conseillère départementale, qui est là, merci madame. M. Moutier, l'autre représentant du département, est excusé. M. Lebrun, adjoint au maire chargé des affaires scolaires, présent. La communauté de communes du Val de Lézon n'est pas représentée, on n'a pas eu de nouvelles.

M. Lebrun : Comme d'habitude, hein.

Mme Cordier : Je ne commente pas. [rires] Pour les personnels enseignants : Mme Roussel, Mme Kasprzak, M. N'Diaye, Mme Bellamy. M. Guérin est absent, il est remplacé par sa suppléante, Mme Varenne. M. Marchetti m'a prévenue qu'il serait en retard, il a un match UNSS qui finit à 17 h 30. Pour les personnels administratifs, techniques, sociaux et de santé : Mme Picot, M. Benslimane. Pour les parents : Mme Chaumont, M. Ostrowski, Mme Sy, M. Pellerin, Mme Delorme. M. Baudoin est excusé. Et pour les élèves : Léna, en troisième, et Yanis, en quatrième. Bienvenue à vous deux.

Mme Chaumont : Madame la principale, juste une précision, M. Baudoin m'a donné un pouvoir, il m'a envoyé un mail cet après-midi.

Mme Cordier : Alors non, je suis désolée, le vote par procuration n'existe pas au conseil d'administration. Un membre titulaire absent est remplacé par son suppléant, c'est tout. Et la suppléante de M. Baudoin ne pouvait pas venir ce soir, elle me l'a écrit. Donc on ne peut pas tenir compte du pouvoir.

Mme Chaumont : D'accord, je ne savais pas. Je lui dirai.

Mme Cordier : Donc nous sommes vingt membres présents sur vingt-quatre, le quorum est de treize, il est largement atteint. Nous avons aussi ce soir, sans voix délibérative, Mme Saintonge, professeure d'espagnol, qui vient pour présenter le voyage en Andalousie au point 3, et M. Lacombe, l'agent comptable, nous rejoindra pour le point budget, il est au conseil d'administration du lycée juste avant. Mme Roussel a accepté d'être secrétaire de séance, merci à elle. L'ordre du jour vous a été envoyé le 22 septembre. Il y a six points : l'approbation du procès-verbal du 30 juin, le règlement intérieur, les voyages et sorties, la rentrée et la dotation horaire, le budget, et les questions diverses. Est-ce que quelqu'un demande l'ajout d'un point ?

[silence]

Mme Cordier : Non. Alors on y va.

Point 1 — Approbation du procès-verbal du conseil d'administration du 30 juin 2026

Mme Cordier : Vous avez reçu le procès-verbal du 30 juin. Est-ce qu'il y a des remarques ?

Mme Delorme : Oui, page 3, il est écrit que le foyer socio-éducatif a reçu une subvention de 1 500 euros. Or, si je me souviens bien, c'était 1 800. On en avait parlé parce que c'était plus que l'année d'avant.

Mme Ferhat : Oui, Mme Delorme a raison, c'est 1 800 euros. C'est une erreur de frappe dans le PV, le montant voté était bien de 1 800.

Mme Cordier : Très bien, on corrige : 1 800 euros et non 1 500. Le procès-verbal corrigé sera mis en ligne sur l'ENT. D'autres remarques ? Non. Je mets aux voix le procès-verbal ainsi corrigé. Qui est contre ? Qui s'abstient ? Il est adopté à l'unanimité des vingt présents. Merci.

[M. Marchetti entre dans la salle, 17 h 50]

M. Marchetti : Pardon, pardon, désolé pour le retard. On a gagné, au moins. [rires]

Mme Cordier : Bienvenue, M. Marchetti. Nous sommes donc vingt et un. On vient d'adopter le PV du 30 juin, on passe au point 2.

Point 2 — Modification du règlement intérieur

Mme Cordier : Alors c'est le gros point de la soirée, je le sais. Je vais laisser M. Vauquelin présenter les modifications, et après on en discute. Je rappelle qu'on en a déjà parlé en conseil pédagogique et avec les délégués des élèves, et que le projet vous a été envoyé avec la convocation.

M. Vauquelin : Merci. Il y a trois modifications. La première, c'est l'article 12 sur le téléphone portable. Aujourd'hui, l'usage est interdit en classe mais toléré dans la cour et au foyer. On vous propose ce qu'on appelle une « pause numérique » : le téléphone est éteint et rangé dans le sac de l'entrée dans le collège jusqu'à la sortie, y compris pendant la pause méridienne. Un usage pédagogique reste possible en classe, sur autorisation explicite de l'enseignant. En cas de manquement, le téléphone est confisqué et rendu à l'élève en fin de journée ; en cas de récidive, il est remis au représentant légal. Deuxième modification, l'article 18 sur la tenue en EPS : on précise que les chaussures de sport sont obligatoires et qu'une tenue de rechange est demandée. Et troisième modification, l'article 21, l'échelle des punitions : on ajoute la retenue le mercredi après-midi, de 13 h 30 à 15 h 30, pour les manquements répétés.

Mme Cordier : Je précise une chose tout de suite, parce que je sais que la question va venir. Dans la première version, celle qui a circulé en juin, on avait envisagé de faire déposer les téléphones dans des casiers fermés à l'entrée du collège. On a abandonné cette idée. D'une part ça coûtait cher, on avait un devis à environ 9 000 euros, et d'autre part ça posait un problème de responsabilité en cas de vol ou de casse. Donc ce n'est plus du tout dans le projet. Le texte qui vous est soumis, c'est : éteint et rangé dans le sac.

M. Ostrowski : Merci de le préciser, parce que beaucoup de parents nous en ont parlé, des casiers. Mais sur le fond, nous, les parents, on n'est pas tous d'accord sur la pause méridienne. Les élèves de troisième, ils ont quatorze, quinze ans. Leur interdire le téléphone de 8 heures à 17 heures, y compris au foyer, c'est un peu…

Mme Kasprzak : Pardon, mais au foyer justement, on voit des élèves de troisième qui ne se parlent plus, qui sont chacun sur leur écran. Et les histoires de photos qui circulent, ça part souvent de là.

M. Ostrowski : Je ne dis pas le contraire, mais…

Mme Cordier : Laissez M. Ostrowski finir, s'il vous plaît.

M. Ostrowski : Je disais : on comprend l'objectif, mais on aurait préféré une gradation. Les sixièmes et cinquièmes, d'accord, interdiction totale. Les troisièmes, au moins au foyer, pendant la pause du midi, sous la surveillance des assistants d'éducation.

M. Tessier : Je peux répondre sur la surveillance ? Le foyer, le midi, c'est un assistant d'éducation pour une soixantaine d'élèves. Il ne peut pas surveiller ce que font soixante élèves sur leur téléphone. Et les incidents de cyberharcèlement qu'on a traités l'an dernier, j'en ai compté onze, il y en a au moins sept qui sont partis d'une photo ou d'une vidéo prise dans l'enceinte du collège.

Léna (élève) : Je peux dire quelque chose ?

Mme Cordier : Bien sûr, Léna.

Léna : On en a parlé au conseil de la vie collégienne. Les élèves de troisième, en majorité, ils sont contre l'interdiction au foyer. Mais il y en a aussi qui disent que ce serait plus simple pour tout le monde si c'était la même règle pour tous. Donc c'est partagé. Et la vraie demande, c'est surtout que le téléphone confisqué soit rendu le soir, pas trois jours après comme ça arrive parfois.

M. Vauquelin : C'est justement ce qu'on écrit : rendu en fin de journée. Il n'y a plus de confiscation de plusieurs jours.

Mme Sy : Et quand c'est remis au représentant légal, ça veut dire quoi concrètement ? Les parents doivent venir au collège ? Parce qu'avec le travail…

M. Vauquelin : Ça veut dire que le parent vient le récupérer à la vie scolaire, oui. Les horaires de la vie scolaire, c'est jusqu'à 17 h 30. Si ce n'est pas possible, on trouve une solution au cas par cas.

Mme Chaumont : Madame la principale, nous demandons une suspension de séance de dix minutes. Les représentants des parents voudraient se concerter avant le vote.

Mme Cordier : C'est de droit. Il est 18 h 20, on reprend à 18 h 30.

[Suspension de séance de 18 h 20 à 18 h 30]

Mme Cordier : On reprend. Il est 18 h 31. Madame Chaumont ?

Mme Chaumont : Oui. Les représentants des parents déposent un amendement à l'article 12 : autoriser l'usage du téléphone au foyer, pendant la pause méridienne, pour les seuls élèves de troisième. Le reste de l'article ne change pas.

Mme Cordier : Très bien. Je mets d'abord aux voix l'amendement, puis le règlement intérieur dans son ensemble. Je rappelle que ce sont des votes à main levée, sauf si quelqu'un demande un vote à bulletin secret.

M. Pellerin : Non, à main levée ça va.

Mme Cordier : Alors l'amendement des parents : autoriser le téléphone au foyer pendant la pause méridienne pour les troisièmes. Qui est pour ? Sept. Qui est contre ? Douze. Qui s'abstient ? Deux. L'amendement est rejeté : sept pour, douze contre, deux abstentions.

M. Benslimane : Excusez-moi, juste pour le PV, les deux abstentions c'est Léna et moi.

Mme Roussel : Je note.

Mme Cordier : Maintenant, le règlement intérieur modifié dans son ensemble, avec les trois modifications des articles 12, 18 et 21, tel qu'il vous a été envoyé. Qui est pour ? Quinze. Contre ? Quatre. Abstentions ? Deux. Le règlement intérieur modifié est adopté : quinze pour, quatre contre, deux abstentions.

M. Pellerin : Pour le PV, les quatre contre, ce sont des représentants des parents.

Mme Roussel : C'est noté, quatre voix contre chez les parents.

Mme Cordier : Le nouveau règlement intérieur entrera en application à la rentrée des vacances de la Toussaint, le lundi 2 novembre 2026. M. Vauquelin, vous vous chargez de le diffuser aux familles ?

M. Vauquelin : Oui, je le mets sur l'ENT et dans le carnet de liaison numérique, avant les vacances, donc au plus tard le vendredi 16 octobre. Et je demanderai aux professeurs principaux de le présenter aux élèves en heure de vie de classe la semaine de la rentrée, la semaine du 2 novembre.

M. Lebrun : Une question pratique, sur la retenue du mercredi après-midi. Le mercredi, le dernier car part à 12 h 15. Les élèves qui habitent dans les hameaux, comment ils rentrent à 15 h 30 ?

Mme Cordier : C'est une vraie question. La retenue reste une punition, elle est notifiée à la famille au moins quarante-huit heures avant, et c'est la famille qui assure le retour. Je sais que ce n'est pas simple pour tout le monde.

M. Lebrun : Et le transport scolaire, ce n'est pas la commune, c'est la région. Donc nous on ne pourra rien faire.

Mme Sy : Il faudrait au moins prévoir une solution pour les familles qui n'ont pas de voiture.

Mme Cordier : On regardera au cas par cas, mais je ne peux pas m'engager ce soir sur une solution de transport. On avance.

Point 3 — Voyages et sorties scolaires 2026-2027

Mme Cordier : Mme Saintonge nous a rejoints. On a trois voyages avec nuitées à examiner, plus le programme des sorties sans nuitée. Mme Ferhat a préparé les budgets. Je commence par le séjour neige des cinquièmes.

Mme Ferhat : Alors le séjour neige concerne les quatre classes de cinquième, 98 élèves, au centre d'hébergement Les Myrtilles, dans le Jura, du lundi 25 au vendredi 29 janvier 2027. Le coût total est de 420 euros par élève, transport compris. Le financement : participation des familles 295 euros, foyer socio-éducatif 35 euros, et une aide du département au titre des séjours éducatifs de 90 euros par élève, qui a déjà été notifiée. 295 plus 35 plus 90, ça fait bien 420. Les familles pourront payer en trois fois, et le fonds social collégien pourra aider les familles qui en ont besoin, après examen par la commission.

M. Marchetti : Et on a les accompagnateurs, c'est bon, on est neuf, dont deux assistants d'éducation.

Mme Cordier : Des questions ? Non ? Je mets aux voix le séjour neige des cinquièmes, avec son budget et la participation des familles de 295 euros. Qui est contre ? Qui s'abstient ? Adopté à l'unanimité des vingt et un présents.

Mme Ferhat : Il faudra que je lance la consultation pour le transporteur, je le fais avant la fin du mois d'octobre.

Mme Cordier : Très bien. Deuxième voyage, l'Andalousie. Mme Saintonge ?

Mme Saintonge : Merci. C'est un voyage pour les élèves hispanistes de quatrième, 46 élèves, à Séville et Grenade, du lundi 12 au vendredi 16 avril 2027, avec hébergement en familles. Le coût total est de 560 euros par élève. Le financement prévu : 380 euros de participation des familles, 60 euros du foyer, et 120 euros d'aide du département au titre de la mobilité internationale.

Mme Ferhat : Et là je dois être claire : cette aide de 120 euros n'est pas acquise. La campagne de demande du département est ouverte jusqu'au lundi 30 novembre 2026, et on n'aura la réponse qu'en janvier.

Mme Arnaud-Poitevin : Je confirme, la commission permanente du département statue en janvier. Je ne peux rien promettre, il y a beaucoup de demandes cette année.

M. Pellerin : Alors justement, 380 euros, c'est déjà beaucoup. Et si l'aide n'arrive pas, on passe à 500 euros pour les familles ? Nous on propose de plafonner la participation des familles à 350 euros, quoi qu'il arrive.

Mme Ferhat : Je comprends, mais à 350 il manque 30 euros par élève, soit 1 380 euros, et je n'ai pas de recette en face. Le foyer ne peut pas mettre plus de 60 euros, il a déjà le séjour neige.

Mme Saintonge : Et on a déjà réduit le programme, on a enlevé l'excursion à Cordoue pour descendre le prix.

Mme Cordier : Ce que je vous propose, c'est de voter le voyage sous réserve de l'obtention de l'aide départementale de 120 euros. Si l'aide est refusée, le voyage reviendra devant le conseil d'administration, on rediscutera du financement à ce moment-là. Il n'y aura pas d'augmentation automatique de la participation des familles.

M. Pellerin : Bon. Ça me va, à condition que ce soit écrit comme ça dans le PV.

Mme Roussel : Je l'écris comme ça.

Mme Cordier : Et donc le plafond à 350 euros, M. Pellerin, vous le maintenez comme proposition à voter ?

M. Pellerin : Non, on le retire, puisque de toute façon ça revient au CA si l'aide est refusée.

Mme Cordier : D'accord. Je mets aux voix le voyage en Andalousie des quatrièmes hispanistes, du 12 au 16 avril 2027, avec une participation des familles de 380 euros, sous réserve de l'obtention de l'aide du département de 120 euros par élève. Qui est contre ? Personne. Qui s'abstient ? Deux. Adopté : dix-neuf pour, zéro contre, deux abstentions.

Mme Saintonge : Merci. Je dépose la demande d'aide avec Mme Ferhat, avant la date limite du 30 novembre.

Mme Ferhat : Oui, on la fait ensemble.

Mme Cordier : Troisième voyage, le séjour à Londres des troisièmes. Mme Kasprzak, vous vouliez dire quelque chose ?

Mme Kasprzak : Oui. Je suis désolée, mais je retire le séjour de l'ordre du jour. On n'a que trois accompagnateurs sur les cinq nécessaires, deux collègues se sont désistés la semaine dernière. Je ne veux pas qu'on vote un voyage qu'on n'est pas sûrs de pouvoir encadrer.

M. Ostrowski : C'est dommage, les familles l'attendaient. Il sera représenté plus tard ?

Mme Kasprzak : Peut-être, si je trouve des accompagnateurs. Mais je ne peux pas promettre, et les tarifs vont augmenter si on réserve tard.

Mme Cordier : On ne vote donc pas le séjour à Londres ce soir. Si Mme Kasprzak revient avec un projet complet, on l'examinera, mais rien n'est fixé. Enfin, le programme des sorties sans nuitée : vous avez le tableau en annexe, il y a quatorze sorties, théâtre, musée, sortie géologie pour les quatrièmes, cross départemental, etc. Toutes sont gratuites pour les familles, financées sur les crédits pédagogiques ou par le foyer. Des remarques ?

Mme Bellamy : Juste une correction dans le tableau : la sortie au théâtre de Lézonville pour les sixièmes, c'est le mardi 8 décembre, pas le 1er. Le 1er il n'y avait plus de places.

Mme Cordier : C'est noté, le mardi 8 décembre. Je mets aux voix le programme des sorties sans nuitée, ainsi corrigé. Contre ? Abstentions ? Adopté à l'unanimité.

M. Pellerin : Excusez-moi, je reviens deux secondes sur le règlement intérieur. Une question qu'on m'a posée pendant la suspension : un élève qui a un problème de santé, un diabète par exemple, avec une application sur son téléphone ?

Mme Cordier : Bonne question. Les élèves qui ont un projet d'accueil individualisé gardent l'usage du téléphone prévu dans leur PAI. Ça figure déjà dans l'article 12, dernier alinéa, mais je comprends que ce n'était pas très visible. M. Vauquelin le rappellera dans le courrier aux familles.

M. Vauquelin : Oui, je l'ajoute dans le courrier.

Point 4 — Bilan de la rentrée et dotation horaire globale

Mme Cordier : On passe au bilan de rentrée. M. Vauquelin.

M. Vauquelin : Alors à la rentrée 2026, on a 642 élèves, répartis en 24 divisions, six par niveau. Les effectifs par niveau : 158 en sixième, 161 en cinquième, 178 en quatrième et 145 en troisième. Donc vous voyez tout de suite le problème, c'est la quatrième : 178 élèves pour six divisions, ça fait près de 30 élèves par classe. La dotation horaire globale de cette année, c'est 768 heures, dont 712 heures postes et 56 heures supplémentaires années. Sur les heures de marge, on a maintenu les dédoublements en sciences en sixième et en cinquième, et le dispositif « Devoirs faits » quatre soirs par semaine.

M. N'Diaye : Et pas en quatrième. Moi j'ai deux quatrièmes à 30 en maths, et en sciences on ne dédouble pas. On fait des TP de physique à 30 dans des salles prévues pour 24. C'est un problème de sécurité aussi, pas seulement de pédagogie.

Mme Bellamy : Et en langues c'est pareil, en espagnol LV2, une des classes a 31 élèves avec le regroupement.

Mme Varenne : En technologie aussi, on a 15 postes informatiques pour 30 élèves.

Mme Cordier : J'entends tout ça et je partage le constat. J'ai demandé en juin une dotation complémentaire, la DSDEN nous a accordé 6 heures, qui sont déjà dans les 768. Je n'ai pas eu d'autre réponse.

M. N'Diaye : C'est pour ça que les représentants des enseignants présentent une motion. Je la lis : « Le conseil d'administration du collège Les Hautes-Bruyères constate que les six divisions de quatrième comptent en moyenne près de 30 élèves et que les conditions d'enseignement, notamment en sciences, en technologie et en langues, ne sont pas satisfaisantes. Il demande à la direction des services départementaux de l'Éducation nationale l'attribution, dès cette année scolaire, d'une dotation complémentaire de 18 heures permettant de dédoubler les enseignements de sciences et de langues en quatrième, et l'examen attentif des effectifs de troisième pour la rentrée 2027. »

M. Ostrowski : Les parents soutiennent la motion.

Mme Arnaud-Poitevin : Je voterai pour aussi, à titre personnel et au nom du département, les effectifs de ce collège augmentent depuis trois ans, c'est connu.

M. Lebrun : La commune aussi.

Mme Cordier : Je précise que les membres de l'administration, c'est-à-dire moi-même, M. Vauquelin, Mme Ferhat et M. Tessier, ne prennent pas part au vote sur cette motion. Ce n'est pas un désaccord sur le fond, c'est que la motion s'adresse à notre hiérarchie et que c'est moi qui la transmettrai.

M. N'Diaye : On l'entend.

M. Marchetti : Et est-ce qu'on pourrait aussi demander une audience au DASEN, avec des parents et des enseignants ? Ce serait plus fort qu'un papier.

Mme Cordier : On peut en parler, mais je ne vais pas l'organiser ce soir. Ça se décide dans un autre cadre.

M. Marchetti : D'accord, on en reparlera.

Mme Cordier : Je mets aux voix la motion telle que lue par M. Nyaye… pardon, M. N'Diaye. [rires] Votants : dix-sept, puisque quatre membres ne prennent pas part au vote. Qui est pour ? Treize. Contre ? Zéro. Abstentions ? Quatre. La motion est adoptée : treize pour, zéro contre, quatre abstentions. Je la transmets à la DSDEN avant les vacances, au plus tard le vendredi 16 octobre.

Mme Kasprzak : Et la dotation pour l'année prochaine, la DHG 2027-2028, on la verra quand ?

Mme Cordier : En général elle arrive fin janvier ou début février, et elle est présentée au conseil d'administration dans la foulée. Je n'ai pas de date pour l'instant, ça dépend du calendrier du rectorat.

Point 5 — Budget

[Mme Arnaud-Poitevin quitte la séance à 19 h 05]

Mme Arnaud-Poitevin : Je vous prie de m'excuser, j'ai une réunion de commission au département à 19 h 30. Bonne fin de séance.

Mme Cordier : Merci madame. Nous sommes donc vingt. Et M. Lacombe nous a rejoints, bonsoir.

M. Lacombe (agent comptable) : Bonsoir à tous, désolé, le CA du lycée a été un peu long.

Mme Cordier : Mme Ferhat, le budget.

Mme Ferhat : Alors d'abord une information. Le département nous a notifié la dotation de fonctionnement pour 2027 : 148 600 euros. C'est une baisse d'environ 3 % par rapport à 2026, où on avait 153 200 euros. Le budget primitif 2027 sera préparé avec cette enveloppe et vous sera soumis au prochain conseil d'administration.

Ensuite, une décision budgétaire modificative pour vote, la DBM n° 3. Le four mixte de la cuisine est hors service depuis le 21 septembre. Le réparateur nous dit que la carte électronique et la sonde sont à changer, c'est presque le prix d'un four neuf, et le modèle n'est plus fabriqué. Mme Picot pourra vous le confirmer.

Mme Picot : Oui, depuis le 21 on fait avec le petit four et les plaques, on sert plus de crudités et de plats froids, les élèves l'ont remarqué.

Yanis (élève) : Ah oui, on l'a remarqué. [rires]

Mme Ferhat : Le remplacement coûte 12 400 euros toutes taxes comprises, installation comprise. Je vous propose de le financer par un prélèvement sur le fonds de roulement du service de restauration et d'hébergement. Le fonds de roulement est aujourd'hui de 186 000 euros, soit environ 74 jours de fonctionnement. Après le prélèvement, on serait à 173 600 euros.

M. Lacombe : Je confirme que le niveau du fonds de roulement le permet. Ça reste largement au-dessus du seuil prudentiel qu'on se fixe, qui est de 30 jours.

M. Pellerin : Une question de principe. Un four de cuisine collective, c'est de l'équipement, ce n'est pas au département de le payer ? Le département a un plan d'équipement pour les collèges. Pourquoi on ne demande pas à être inscrits sur le plan 2027 plutôt que de puiser dans nos réserves ?

Mme Ferhat : On peut le demander, mais le plan d'équipement 2027 sera arrêté au printemps, et le four serait livré au mieux en septembre prochain. On ne peut pas faire une année scolaire entière sans four.

M. Lebrun : Je ne peux pas parler au nom du département, Mme Arnaud-Poitevin est partie, mais je sais que le plan d'équipement est très demandé.

M. Pellerin : Dommage qu'elle soit partie justement. Bon, j'aurais préféré qu'on attende le plan, mais je comprends l'urgence.

Mme Cordier : On ne retient pas l'idée d'attendre le plan d'équipement, l'urgence est trop forte. Je mets aux voix la DBM n° 3 : prélèvement de 12 400 euros sur le fonds de roulement pour le remplacement du four mixte. Qui est contre ? Personne. Abstentions ? Trois. Adoptée : dix-sept pour, zéro contre, trois abstentions.

Mme Ferhat : Merci. Je lance la commande dès que la DBM sera exécutoire, c'est-à-dire après le délai de transmission au contrôle de légalité.

Mme Ferhat : Ensuite, pour information seulement, la DBM n° 4, qui ne se vote pas puisqu'il s'agit de recettes affectées : 3 200 euros de crédits supplémentaires de l'État pour le fonds social collégien, et 1 150 euros de la commune pour le dispositif « Collège au cinéma ».

M. Lebrun : Voilà, la commune fait sa part. [rires]

Mme Ferhat : Merci à la commune. Deux autres délibérations. D'abord, la convention d'utilisation du gymnase municipal pour l'année 2026-2027 : la commune met le gymnase à disposition pour les cours d'EPS, il faut autoriser Mme la principale à signer.

M. Marchetti : Sans le gymnase on fait cours sur le plateau extérieur, donc oui, autorisez. [rires]

Mme Cordier : Je mets aux voix l'autorisation de signer la convention d'utilisation du gymnase municipal pour 2026-2027. Contre ? Abstentions ? Adoptée à l'unanimité des vingt présents.

Mme Ferhat : Et enfin, l'acceptation d'un don. L'entreprise Menuiserie Fourcade Frères propose un don de 500 euros au club robotique… attendez, pardon, je relis le courrier : c'est 450 euros, pas 500. 450 euros, affectés à l'achat de kits de robotique pour le club.

Mme Cordier : 450 euros donc. Je mets aux voix l'acceptation du don de 450 euros de la Menuiserie Fourcade Frères au profit du club robotique. Contre ? Abstentions ? Adopté à l'unanimité.

M. Ostrowski : Et le budget primitif, on le vote quand ?

Mme Cordier : Au prochain conseil d'administration, qui sera aussi le premier conseil de la nouvelle mandature, avec l'installation des nouveaux membres. Ce sera le jeudi 19 novembre… non, pardon, je me trompe, le 19 c'est le conseil pédagogique. Le prochain CA, c'est le jeudi 26 novembre 2026, à 17 h 30.

Mme Ferhat : Et je vous enverrai les documents budgétaires au moins dix jours avant, donc au plus tard le lundi 16 novembre.

M. Lacombe : Je serai présent le 26 novembre.

Point 6 — Questions diverses

Mme Cordier : Nous avons reçu deux questions écrites, une des parents et une des élèves. Et M. Lebrun m'a dit qu'il voulait dire un mot. Mme Sy, pour les parents.

Mme Sy : Oui. Plusieurs familles nous signalent que les toilettes du bâtiment C sont fermées tous les après-midi depuis la rentrée. Les élèves doivent traverser toute la cour pour aller au bâtiment A, et certains n'y vont plus du tout de la journée.

Mme Picot : C'est parce qu'une collègue agent est en arrêt depuis début septembre et qu'elle n'est pas remplacée. On n'a pas assez de monde pour nettoyer le bâtiment C l'après-midi, alors on ferme.

Mme Cordier : Les agents sont des personnels du département. J'ai déjà signalé l'absence oralement, mais je vais écrire officiellement au département pour demander un remplacement. Je le fais cette semaine, avant le vendredi 9 octobre.

M. Lebrun : La commune ne peut pas mettre d'agent, ce n'est pas dans nos compétences, je le dis tout de suite.

Mme Sy : On ne vous demandait pas ça, monsieur. [rires]

Mme Cordier : Yanis, pour les élèves ?

Yanis : Les élèves de sixième, ils ont des cartables trop lourds, ils demandent s'il pourrait y avoir des casiers pour laisser des livres.

M. Pellerin : Des casiers ? Je croyais qu'on avait dit que c'était trop cher, tout à l'heure.

Mme Cordier : Non, là ce n'est pas la même chose. Tout à l'heure c'était des casiers pour déposer les téléphones à l'entrée, et ça on l'a abandonné. Là, Yanis parle de casiers pour les affaires des sixièmes. C'est une autre demande.

Mme Ferhat : Je peux chiffrer des casiers pour les sixièmes et le présenter dans le cadre du budget primitif 2027, pour le CA du 26 novembre.

Mme Cordier : Très bien, Mme Ferhat chiffre et on en reparle au budget primitif. Ce n'est pas décidé ce soir. Mme Bellamy, vous aviez aussi une remarque ?

Mme Bellamy : Oui, très vite, la salle B12, il fait 15 degrés le matin. Le chauffage ne fonctionne pas bien depuis la remise en route.

Mme Ferhat : C'est déjà signalé au département, le 28 septembre. L'entreprise de maintenance doit passer, je n'ai pas encore de date.

M. Lebrun : Oui, alors moi, c'était pour vous informer que la commune organise le forum des associations samedi… non, c'était samedi dernier, pardon, il est passé. [rires] Non, ce que je voulais dire, c'est que la commune réfléchit à un « pédibus » pour les élèves du centre-bourg, mais c'est vraiment au stade de l'idée, on n'a rien décidé en conseil municipal.

Mme Cordier : Merci, vous nous tiendrez informés. Dernières informations de ma part : les élections des représentants des parents ont lieu ce vendredi 9 octobre, le vote se fait par correspondance ou à l'urne, au collège, de 8 heures à 12 heures. Et je rappelle la date du prochain conseil d'administration : jeudi 26 novembre 2026, 17 h 30. Est-ce qu'il y a d'autres questions ?

M. Ostrowski : Juste un mot pour remercier, puisque c'est la dernière séance pour plusieurs d'entre nous. Mme Delorme et moi, on ne se représente pas.

Mme Cordier : Merci à vous deux pour votre engagement pendant ces années. Merci à tous. La séance est levée, il est 20 h 05.

[Fin de l'enregistrement]
```

</details>

<details><summary>Nouvelle valeur complète</summary>

```text
Transcription — Conseil d'administration du collège Les Hautes-Bruyères, Saint-Aubin-sur-Lézon
Mardi 6 octobre 2026, 17 h 30, salle polyvalente
Enregistrement réalisé pour faciliter la rédaction du procès-verbal. Secrétaire de séance : Mme Roussel.

Mme Cordier (principale, présidente) : Bon, il est 17 h 35, je crois qu'on peut commencer. Bonsoir à toutes et à tous. Je vous remercie d'être là, c'est le dernier conseil d'administration de cette mandature, puisque les élections des représentants des parents ont lieu ce vendredi 9 octobre et celles des personnels dans la foulée. Je fais l'appel, comme d'habitude, pour vérifier le quorum. Pour l'administration : moi-même, M. Vauquelin, principal adjoint, Mme Ferhat, adjointe gestionnaire, M. Tessier, CPE. Pour les collectivités : Mme Arnaud-Poitevin, conseillère départementale, qui est là, merci madame. M. Moutier, l'autre représentant du département, est excusé. M. Lebrun, adjoint au maire chargé des affaires scolaires, présent. La communauté de communes du Val de Lézon n'est pas représentée, on n'a pas eu de nouvelles.

M. Lebrun : Comme d'habitude, hein.

Mme Cordier : Je ne commente pas. [rires] Pour les personnels enseignants : Mme Roussel, Mme Kasprzak, M. N'Diaye, Mme Bellamy. M. Guérin est absent, il est remplacé par sa suppléante, Mme Varenne. M. Marchetti m'a prévenue qu'il serait en retard, il a un match UNSS qui finit à 17 h 30. Pour les personnels administratifs, techniques, sociaux et de santé : Mme Picot, M. Benslimane. Pour les parents : Mme Chaumont, M. Ostrowski, Mme Sy, M. Pellerin, Mme Delorme. M. Baudoin est excusé. Et pour les élèves : Léna, en troisième, et Yanis, en quatrième. Bienvenue à vous deux.

Mme Chaumont : Madame la principale, juste une précision, M. Baudoin m'a donné un pouvoir, il m'a envoyé un mail cet après-midi.

Mme Cordier : Alors non, je suis désolée, le vote par procuration n'existe pas au conseil d'administration. Un membre titulaire absent est remplacé par son suppléant, c'est tout. Et la suppléante de M. Baudoin ne pouvait pas venir ce soir, elle me l'a écrit. Donc on ne peut pas tenir compte du pouvoir.

Mme Chaumont : D'accord, je ne savais pas. Je lui dirai.

Mme Cordier : Donc nous sommes vingt membres présents sur vingt-quatre, le quorum est de treize, il est largement atteint. Nous avons aussi ce soir, sans voix délibérative, Mme Saintonge, professeure d'espagnol, qui vient pour présenter le voyage en Andalousie au point 3, et M. Lacombe, l'agent comptable, nous rejoindra pour le point budget, il est au conseil d'administration du lycée juste avant. Mme Roussel a accepté d'être secrétaire de séance, merci à elle. L'ordre du jour vous a été envoyé le 22 septembre. Il y a six points : l'approbation du procès-verbal du 30 juin, le règlement intérieur, les voyages et sorties, la rentrée et la dotation horaire, le budget, et les questions diverses. Est-ce que quelqu'un demande l'ajout d'un point ?

[silence]

Mme Cordier : Non. Alors on y va.

Point 1 — Approbation du procès-verbal du conseil d'administration du 30 juin 2026

Mme Cordier : Vous avez reçu le procès-verbal du 30 juin. Est-ce qu'il y a des remarques ?

Mme Delorme : Oui, page 3, il est écrit que le foyer socio-éducatif a reçu une subvention de 1 500 euros. Or, si je me souviens bien, c'était 1 800. On en avait parlé parce que c'était plus que l'année d'avant.

Mme Ferhat : Oui, Mme Delorme a raison, c'est 1 800 euros. C'est une erreur de frappe dans le PV, le montant voté était bien de 1 800.

Mme Delorme : Je m'en souvenais parce qu'on en avait discuté avec les élèves du foyer, ils étaient contents de cette hausse.

Mme Cordier : Très bien, on corrige : 1 800 euros et non 1 500. Le procès-verbal corrigé sera mis en ligne sur l'ENT. D'autres remarques ? Non. Je mets aux voix le procès-verbal ainsi corrigé. Qui est contre ? Qui s'abstient ? Il est adopté à l'unanimité des vingt présents. Merci.

[M. Marchetti entre dans la salle, 17 h 50]

M. Marchetti : Pardon, pardon, désolé pour le retard. On a gagné, au moins. [rires]

M. Lebrun : Et contre qui ?

M. Marchetti : Contre le collège de Lézonville, en handball. Les filles ont été formidables.

Mme Cordier : Bienvenue, M. Marchetti. Nous sommes donc vingt et un. On vient d'adopter le PV du 30 juin, on passe au point 2.

Point 2 — Modification du règlement intérieur

Mme Cordier : Alors c'est le gros point de la soirée, je le sais. Je vais laisser M. Vauquelin présenter les modifications, et après on en discute. Je rappelle qu'on en a déjà parlé en conseil pédagogique et avec les délégués des élèves, et que le projet vous a été envoyé avec la convocation.

M. Vauquelin : Merci. Il y a trois modifications. La première, c'est l'article 12 sur le téléphone portable. Aujourd'hui, l'usage est interdit en classe mais toléré dans la cour et au foyer. On vous propose ce qu'on appelle une « pause numérique » : le téléphone est éteint et rangé dans le sac de l'entrée dans le collège jusqu'à la sortie, y compris pendant la pause méridienne. Un usage pédagogique reste possible en classe, sur autorisation explicite de l'enseignant. En cas de manquement, le téléphone est confisqué et rendu à l'élève en fin de journée ; en cas de récidive, il est remis au représentant légal. Deuxième modification, l'article 18 sur la tenue en EPS : on précise que les chaussures de sport sont obligatoires et qu'une tenue de rechange est demandée. Et troisième modification, l'article 21, l'échelle des punitions : on ajoute la retenue le mercredi après-midi, de 13 h 30 à 15 h 30, pour les manquements répétés.

Mme Cordier : Je précise une chose tout de suite, parce que je sais que la question va venir. Dans la première version, celle qui a circulé en juin, on avait envisagé de faire déposer les téléphones dans des casiers fermés à l'entrée du collège. On a abandonné cette idée. D'une part ça coûtait cher, on avait un devis à environ 9 000 euros, et d'autre part ça posait un problème de responsabilité en cas de vol ou de casse. Donc ce n'est plus du tout dans le projet. Le texte qui vous est soumis, c'est : éteint et rangé dans le sac.

Mme Picot : Et je me permets d'ajouter, pour les agents, que des casiers à l'entrée, ça voulait dire aussi quelqu'un pour les ouvrir et les fermer matin et soir. On était inquiets, honnêtement.

Mme Cordier : C'était une des difficultés, en effet. Mais encore une fois, ce n'est plus du tout d'actualité.

M. Ostrowski : Merci de le préciser, parce que beaucoup de parents nous en ont parlé, des casiers. Mais sur le fond, nous, les parents, on n'est pas tous d'accord sur la pause méridienne. Les élèves de troisième, ils ont quatorze, quinze ans. Leur interdire le téléphone de 8 heures à 17 heures, y compris au foyer, c'est un peu…

Mme Kasprzak : Pardon, mais au foyer justement, on voit des élèves de troisième qui ne se parlent plus, qui sont chacun sur leur écran. Et les histoires de photos qui circulent, ça part souvent de là.

M. Ostrowski : Je ne dis pas le contraire, mais…

Mme Cordier : Laissez M. Ostrowski finir, s'il vous plaît.

M. Ostrowski : Je disais : on comprend l'objectif, mais on aurait préféré une gradation. Les sixièmes et cinquièmes, d'accord, interdiction totale. Les troisièmes, au moins au foyer, pendant la pause du midi, sous la surveillance des assistants d'éducation.

M. Tessier : Je peux répondre sur la surveillance ? Le foyer, le midi, c'est un assistant d'éducation pour une soixantaine d'élèves. Il ne peut pas surveiller ce que font soixante élèves sur leur téléphone. Et les incidents de cyberharcèlement qu'on a traités l'an dernier, j'en ai compté onze, il y en a au moins sept qui sont partis d'une photo ou d'une vidéo prise dans l'enceinte du collège.

Mme Sy : Onze incidents, c'est beaucoup pour un collège comme le nôtre.

M. Tessier : C'est beaucoup, oui. Et ce sont seulement ceux qui ont été portés à notre connaissance.

Léna (élève) : Je peux dire quelque chose ?

Mme Cordier : Bien sûr, Léna.

Léna : On en a parlé au conseil de la vie collégienne. Les élèves de troisième, en majorité, ils sont contre l'interdiction au foyer. Mais il y en a aussi qui disent que ce serait plus simple pour tout le monde si c'était la même règle pour tous. Donc c'est partagé. Et la vraie demande, c'est surtout que le téléphone confisqué soit rendu le soir, pas trois jours après comme ça arrive parfois.

M. Vauquelin : C'est justement ce qu'on écrit : rendu en fin de journée. Il n'y a plus de confiscation de plusieurs jours.

Mme Delorme : Une question de parent. Beaucoup d'entre nous ont donné un téléphone à leur enfant pour pouvoir le joindre à la sortie, surtout ceux qui prennent le car. Le téléphone pourra être rallumé dès qu'ils sortent du collège ?

M. Vauquelin : Oui, la règle s'applique de l'entrée à la sortie. Une fois le portail franchi, le collège n'a plus à intervenir. Et en cas d'urgence pendant la journée, les familles appellent la vie scolaire, comme aujourd'hui.

Mme Bellamy : Je voudrais aussi dire, du côté des enseignants, que l'usage pédagogique reste possible, et c'est important. Moi j'utilise parfois les téléphones pour des quiz ou pour enregistrer une production orale en langue. Ce sera toujours possible, sur autorisation, comme c'est écrit dans le projet.

M. Tessier : Et pour la confiscation, je précise que c'est déjà comme ça qu'on procède aujourd'hui à la vie scolaire : le téléphone est déposé au bureau et l'élève le récupère en partant. Ce qui change, c'est qu'il n'y aura plus de confiscation sur plusieurs jours, comme le disait Léna.

M. Benslimane : Pour les agents d'accueil, je voudrais juste qu'on soit clairs : on n'aura pas à fouiller les sacs à l'entrée.

Mme Cordier : Non, évidemment. Personne ne fouille les sacs. La règle repose sur la responsabilité des élèves et sur la présence des adultes, en classe et dans la cour.

Mme Kasprzak : Et franchement, dans les collèges voisins qui l'ont fait l'an dernier, les collègues disent que la cour a changé. Les élèves rejouent au ballon, ils se parlent, ils s'ennuient un peu aussi, et ce n'est pas plus mal.

M. Ostrowski : Je ne doute pas que ça ait des effets positifs. Je dis juste que les troisièmes ne sont pas des sixièmes.

Mme Sy : Et quand c'est remis au représentant légal, ça veut dire quoi concrètement ? Les parents doivent venir au collège ? Parce qu'avec le travail…

M. Vauquelin : Ça veut dire que le parent vient le récupérer à la vie scolaire, oui. Les horaires de la vie scolaire, c'est jusqu'à 17 h 30. Si ce n'est pas possible, on trouve une solution au cas par cas.

Mme Sy : D'accord. Au moins, les choses sont claires pour tout le monde.

Mme Chaumont : Madame la principale, nous demandons une suspension de séance de dix minutes. Les représentants des parents voudraient se concerter avant le vote.

Mme Cordier : C'est de droit. Il est 18 h 20, on reprend à 18 h 30.

[Suspension de séance de 18 h 20 à 18 h 30]

Mme Cordier : On reprend. Il est 18 h 31. Madame Chaumont ?

Mme Chaumont : Oui. Les représentants des parents déposent un amendement à l'article 12 : autoriser l'usage du téléphone au foyer, pendant la pause méridienne, pour les seuls élèves de troisième. Le reste de l'article ne change pas.

Mme Kasprzak : Je peux réagir ? Je comprends l'idée, mais pour nous la difficulté reste la même : au foyer, le midi, personne ne peut surveiller soixante écrans.

Mme Chaumont : On l'entend. Je précise seulement que l'amendement a été rédigé pendant la suspension, à partir de ce que disait Léna sur le conseil de la vie collégienne. C'est une position d'équilibre, ce n'est pas un refus du règlement.

Mme Cordier : Très bien. Je mets d'abord aux voix l'amendement, puis le règlement intérieur dans son ensemble. Je rappelle que ce sont des votes à main levée, sauf si quelqu'un demande un vote à bulletin secret.

M. Pellerin : Non, à main levée ça va.

Mme Cordier : Alors l'amendement des parents : autoriser le téléphone au foyer pendant la pause méridienne pour les troisièmes. Qui est pour ? Sept. Qui est contre ? Douze. Qui s'abstient ? Deux. L'amendement est rejeté : sept pour, douze contre, deux abstentions.

M. Benslimane : Excusez-moi, juste pour le PV, les deux abstentions c'est Léna et moi.

Mme Roussel : Je note.

Mme Cordier : Maintenant, le règlement intérieur modifié dans son ensemble, avec les trois modifications des articles 12, 18 et 21, tel qu'il vous a été envoyé. Qui est pour ? Quinze. Contre ? Quatre. Abstentions ? Deux. Le règlement intérieur modifié est adopté : quinze pour, quatre contre, deux abstentions.

M. Pellerin : Pour le PV, les quatre contre, ce sont des représentants des parents.

Mme Roussel : C'est noté, quatre voix contre chez les parents.

Mme Cordier : Le nouveau règlement intérieur entrera en application à la rentrée des vacances de la Toussaint, le lundi 2 novembre 2026. M. Vauquelin, vous vous chargez de le diffuser aux familles ?

M. Vauquelin : Oui, je le mets sur l'ENT et dans le carnet de liaison numérique, avant les vacances, donc au plus tard le vendredi 16 octobre. Et je demanderai aux professeurs principaux de le présenter aux élèves en heure de vie de classe la semaine de la rentrée, la semaine du 2 novembre.

M. Lebrun : Une question pratique, sur la retenue du mercredi après-midi. Le mercredi, le dernier car part à 12 h 15. Les élèves qui habitent dans les hameaux, comment ils rentrent à 15 h 30 ?

Mme Cordier : C'est une vraie question. La retenue reste une punition, elle est notifiée à la famille au moins quarante-huit heures avant, et c'est la famille qui assure le retour. Je sais que ce n'est pas simple pour tout le monde.

M. Lebrun : Et le transport scolaire, ce n'est pas la commune, c'est la région. Donc nous on ne pourra rien faire.

Mme Sy : Il faudrait au moins prévoir une solution pour les familles qui n'ont pas de voiture.

Mme Cordier : On regardera au cas par cas, mais je ne peux pas m'engager ce soir sur une solution de transport. On avance.

Point 3 — Voyages et sorties scolaires 2026-2027

Mme Cordier : Mme Saintonge nous a rejoints. On a trois voyages avec nuitées à examiner, plus le programme des sorties sans nuitée. Mme Ferhat a préparé les budgets. Je commence par le séjour neige des cinquièmes.

Mme Ferhat : Alors le séjour neige concerne les quatre classes de cinquième, 98 élèves, au centre d'hébergement Les Myrtilles, dans le Jura, du lundi 25 au vendredi 29 janvier 2027. Le coût total est de 420 euros par élève, transport compris. Le financement : participation des familles 295 euros, foyer socio-éducatif 35 euros, et une aide du département au titre des séjours éducatifs de 90 euros par élève, qui a déjà été notifiée. 295 plus 35 plus 90, ça fait bien 420. Les familles pourront payer en trois fois, et le fonds social collégien pourra aider les familles qui en ont besoin, après examen par la commission.

M. Marchetti : Et on a les accompagnateurs, c'est bon, on est neuf, dont deux assistants d'éducation.

Mme Varenne : Je peux témoigner, j'avais accompagné ce séjour il y a deux ans, dans le même centre. Les élèves en parlent encore. L'encadrement sur place est très sérieux, et le centre a l'habitude d'accueillir des collèges.

Yanis : Mon frère y est allé, il a dit que c'était le meilleur voyage du collège. [rires]

M. Marchetti : Pour le programme, c'est ski de fond le matin, et l'après-midi raquettes ou découverte du milieu montagnard avec un animateur nature. Il y a aussi une veillée chaque soir. Le programme détaillé est en annexe du dossier que vous avez reçu.

Mme Sy : Et pour les élèves qui n'ont jamais fait de ski, il y a des groupes de niveau ?

M. Marchetti : Oui, les moniteurs font des groupes le premier jour. Pour le ski de fond, on part vraiment de zéro, il n'y a pas besoin d'expérience.

Mme Picot : Et pour les élèves qui ont un régime alimentaire particulier, le centre est au courant ?

M. Marchetti : Oui, on transmet les fiches sanitaires avant le départ, et le centre gère les régimes. Il l'a toujours fait.

Mme Cordier : Des questions ? Non ? Je mets aux voix le séjour neige des cinquièmes, avec son budget et la participation des familles de 295 euros. Qui est contre ? Qui s'abstient ? Adopté à l'unanimité des vingt et un présents.

Mme Ferhat : Il faudra que je lance la consultation pour le transporteur, je le fais avant la fin du mois d'octobre.

Mme Cordier : Très bien. Deuxième voyage, l'Andalousie. Mme Saintonge ?

Mme Saintonge : Merci. C'est un voyage pour les élèves hispanistes de quatrième, 46 élèves, à Séville et Grenade, du lundi 12 au vendredi 16 avril 2027, avec hébergement en familles. Le coût total est de 560 euros par élève. Le financement prévu : 380 euros de participation des familles, 60 euros du foyer, et 120 euros d'aide du département au titre de la mobilité internationale.

Mme Ferhat : Et là je dois être claire : cette aide de 120 euros n'est pas acquise. La campagne de demande du département est ouverte jusqu'au lundi 30 novembre 2026, et on n'aura la réponse qu'en janvier.

Mme Arnaud-Poitevin : Je confirme, la commission permanente du département statue en janvier. Je ne peux rien promettre, il y a beaucoup de demandes cette année.

Mme Saintonge : Nous avons construit le dossier en tenant compte des critères du département : un vrai projet linguistique, le carnet de voyage, les cours avec un établissement partenaire. On a de bonnes chances, mais je sais que rien n'est garanti.

M. Pellerin : Alors justement, 380 euros, c'est déjà beaucoup. Et si l'aide n'arrive pas, on passe à 500 euros pour les familles ? Nous on propose de plafonner la participation des familles à 350 euros, quoi qu'il arrive.

Mme Ferhat : Je comprends, mais à 350 il manque 30 euros par élève, soit 1 380 euros, et je n'ai pas de recette en face. Le foyer ne peut pas mettre plus de 60 euros, il a déjà le séjour neige.

Mme Saintonge : Et on a déjà réduit le programme, on a enlevé l'excursion à Cordoue pour descendre le prix.

Mme Delorme : Et l'hébergement en familles, c'est encadré comment ? Des parents nous ont posé la question, ça les inquiète un peu.

Mme Saintonge : C'est un organisme spécialisé qui sélectionne les familles, il travaille avec des établissements scolaires depuis longtemps. Les élèves sont hébergés par deux ou trois, jamais seuls, et le point de rendez-vous du matin est à proximité des familles. Les enseignants ont un téléphone joignable jour et nuit. On l'avait fait il y a trois ans à Salamanque, et ça s'était très bien passé.

Mme Chaumont : C'est rassurant. Et pédagogiquement, il y a quoi au programme ?

Mme Saintonge : La visite de l'Alcazar et de la cathédrale à Séville, l'Alhambra à Grenade, et une matinée dans un établissement partenaire, où les élèves suivent des cours avec des correspondants. Ils préparent en amont un carnet de voyage en espagnol, qui est évalué au troisième trimestre. C'est vraiment un projet construit avec les cours, pas seulement une sortie touristique.

Léna : Les élèves de quatrième en parlent beaucoup, en tout cas. Ils ont hâte.

Mme Cordier : Ce que je vous propose, c'est de voter le voyage sous réserve de l'obtention de l'aide départementale de 120 euros. Si l'aide est refusée, le voyage reviendra devant le conseil d'administration, on rediscutera du financement à ce moment-là. Il n'y aura pas d'augmentation automatique de la participation des familles.

M. Pellerin : Bon. Ça me va, à condition que ce soit écrit comme ça dans le PV.

Mme Roussel : Je l'écris comme ça.

Mme Cordier : Et donc le plafond à 350 euros, M. Pellerin, vous le maintenez comme proposition à voter ?

M. Pellerin : Non, on le retire, puisque de toute façon ça revient au CA si l'aide est refusée.

Mme Cordier : D'accord. Je mets aux voix le voyage en Andalousie des quatrièmes hispanistes, du 12 au 16 avril 2027, avec une participation des familles de 380 euros, sous réserve de l'obtention de l'aide du département de 120 euros par élève. Qui est contre ? Personne. Qui s'abstient ? Deux. Adopté : dix-neuf pour, zéro contre, deux abstentions.

Mme Saintonge : Merci. Je dépose la demande d'aide avec Mme Ferhat, avant la date limite du 30 novembre.

Mme Ferhat : Oui, on la fait ensemble.

Mme Cordier : Troisième voyage, le séjour à Londres des troisièmes. Mme Kasprzak, vous vouliez dire quelque chose ?

Mme Kasprzak : Oui. Je suis désolée, mais je retire le séjour de l'ordre du jour. On n'a que trois accompagnateurs sur les cinq nécessaires, deux collègues se sont désistés la semaine dernière. Je ne veux pas qu'on vote un voyage qu'on n'est pas sûrs de pouvoir encadrer.

M. Ostrowski : C'est dommage, les familles l'attendaient. Il sera représenté plus tard ?

Mme Kasprzak : Peut-être, si je trouve des accompagnateurs. Mais je ne peux pas promettre, et les tarifs vont augmenter si on réserve tard.

Mme Roussel : Je comprends la décision. On ne part pas à l'étranger avec seulement trois adultes.

Mme Kasprzak : Voilà. Et je préfère le dire maintenant plutôt que d'annuler en mars, avec des familles qui auraient déjà versé des acomptes.

Mme Cordier : On ne vote donc pas le séjour à Londres ce soir. Si Mme Kasprzak revient avec un projet complet, on l'examinera, mais rien n'est fixé. Enfin, le programme des sorties sans nuitée : vous avez le tableau en annexe, il y a quatorze sorties, théâtre, musée, sortie géologie pour les quatrièmes, cross départemental, etc. Toutes sont gratuites pour les familles, financées sur les crédits pédagogiques ou par le foyer. Des remarques ?

Mme Bellamy : Juste une correction dans le tableau : la sortie au théâtre de Lézonville pour les sixièmes, c'est le mardi 8 décembre, pas le 1er. Le 1er il n'y avait plus de places.

Mme Cordier : C'est noté, le mardi 8 décembre. Je mets aux voix le programme des sorties sans nuitée, ainsi corrigé. Contre ? Abstentions ? Adopté à l'unanimité.

Mme Varenne : Pour la sortie géologie des quatrièmes, je voulais remercier le foyer : c'est grâce à lui qu'elle reste gratuite pour les familles.

Mme Chaumont : Et le foyer, c'est surtout grâce aux ventes de gâteaux et à la tombola de fin d'année. Les familles se mobilisent beaucoup.

Mme Cordier : Merci à elles, vraiment.

M. Pellerin : Excusez-moi, je reviens deux secondes sur le règlement intérieur. Une question qu'on m'a posée pendant la suspension : un élève qui a un problème de santé, un diabète par exemple, avec une application sur son téléphone ?

Mme Cordier : Bonne question. Les élèves qui ont un projet d'accueil individualisé gardent l'usage du téléphone prévu dans leur PAI. Ça figure déjà dans l'article 12, dernier alinéa, mais je comprends que ce n'était pas très visible. M. Vauquelin le rappellera dans le courrier aux familles.

M. Vauquelin : Oui, je l'ajoute dans le courrier.

Point 4 — Bilan de la rentrée et dotation horaire globale

Mme Cordier : On passe au bilan de rentrée. M. Vauquelin.

M. Vauquelin : Alors à la rentrée 2026, on a 642 élèves, répartis en 24 divisions, six par niveau. Les effectifs par niveau : 158 en sixième, 161 en cinquième, 178 en quatrième et 145 en troisième. Donc vous voyez tout de suite le problème, c'est la quatrième : 178 élèves pour six divisions, ça fait près de 30 élèves par classe. La dotation horaire globale de cette année, c'est 768 heures, dont 712 heures postes et 56 heures supplémentaires années. Sur les heures de marge, on a maintenu les dédoublements en sciences en sixième et en cinquième, et le dispositif « Devoirs faits » quatre soirs par semaine.

M. N'Diaye : Et pas en quatrième. Moi j'ai deux quatrièmes à 30 en maths, et en sciences on ne dédouble pas. On fait des TP de physique à 30 dans des salles prévues pour 24. C'est un problème de sécurité aussi, pas seulement de pédagogie.

Mme Bellamy : Et en langues c'est pareil, en espagnol LV2, une des classes a 31 élèves avec le regroupement.

Mme Saintonge : Je confirme pour l'espagnol : à trente et un, chaque élève a à peine une minute de prise de parole par séance.

Mme Varenne : En technologie aussi, on a 15 postes informatiques pour 30 élèves.

Mme Roussel : Et en français, même si on n'est pas concernés par les dédoublements, à trente en quatrième, la correction des copies et le suivi individuel deviennent très difficiles. Je le dis en tant qu'enseignante, pas en tant que secrétaire de séance. [rires]

M. Tessier : Du côté de la vie scolaire, je confirme que le niveau quatrième concentre une bonne partie des incidents depuis la rentrée. Ce n'est pas seulement une question d'effectifs, mais des classes à trente, avec des élèves qui ont des besoins très différents, c'est plus difficile à tenir pour tout le monde.

M. Ostrowski : Les parents le voient aussi. Plusieurs familles de quatrième nous disent que leurs enfants ont du mal à suivre en sciences, et qu'ils n'arrivent pas à poser leurs questions en classe.

Mme Cordier : Pour que tout le monde comprenne bien, je rappelle comment fonctionne la dotation. Les heures postes, ce sont les heures assurées par des enseignants affectés au collège. Les heures supplémentaires années, ce sont des heures payées en plus, réparties sur l'année. Et les heures de marge, c'est ce qu'on peut utiliser librement, une fois assurés les horaires réglementaires, pour les dédoublements ou des dispositifs comme « Devoirs faits ». Ce que je ne peux pas faire, c'est créer des heures qu'on ne nous a pas données.

Mme Varenne : En technologie, on fait tourner les élèves par demi-groupes sur les postes pendant que les autres travaillent sur papier. Ça fonctionne, mais chaque élève perd la moitié de son temps de pratique.

M. N'Diaye : On le sait bien, et ce n'est pas un reproche à la direction.

Mme Cordier : J'entends tout ça et je partage le constat. J'ai demandé en juin une dotation complémentaire, la DSDEN nous a accordé 6 heures, qui sont déjà dans les 768. Je n'ai pas eu d'autre réponse.

M. N'Diaye : C'est pour ça que les représentants des enseignants présentent une motion. Je la lis : « Le conseil d'administration du collège Les Hautes-Bruyères constate que les six divisions de quatrième comptent en moyenne près de 30 élèves et que les conditions d'enseignement, notamment en sciences, en technologie et en langues, ne sont pas satisfaisantes. Il demande à la direction des services départementaux de l'Éducation nationale l'attribution, dès cette année scolaire, d'une dotation complémentaire de 18 heures permettant de dédoubler les enseignements de sciences et de langues en quatrième, et l'examen attentif des effectifs de troisième pour la rentrée 2027. »

M. Ostrowski : Les parents soutiennent la motion.

Mme Arnaud-Poitevin : Je voterai pour aussi, à titre personnel et au nom du département, les effectifs de ce collège augmentent depuis trois ans, c'est connu.

Mme Cordier : Merci madame. C'est important que le département partage le constat.

M. Lebrun : La commune aussi.

Léna : Et au conseil de la vie collégienne, les délégués de quatrième ont dit la même chose : en sciences, à trente, ceux du fond ne voient rien des expériences.

Mme Cordier : Je précise que les membres de l'administration, c'est-à-dire moi-même, M. Vauquelin, Mme Ferhat et M. Tessier, ne prennent pas part au vote sur cette motion. Ce n'est pas un désaccord sur le fond, c'est que la motion s'adresse à notre hiérarchie et que c'est moi qui la transmettrai.

M. N'Diaye : On l'entend.

M. Marchetti : Et est-ce qu'on pourrait aussi demander une audience au DASEN, avec des parents et des enseignants ? Ce serait plus fort qu'un papier.

Mme Cordier : On peut en parler, mais je ne vais pas l'organiser ce soir. Ça se décide dans un autre cadre.

M. Marchetti : D'accord, on en reparlera.

Mme Cordier : Je mets aux voix la motion telle que lue par M. Nyaye… pardon, M. N'Diaye. [rires] Votants : dix-sept, puisque quatre membres ne prennent pas part au vote. Qui est pour ? Treize. Contre ? Zéro. Abstentions ? Quatre. La motion est adoptée : treize pour, zéro contre, quatre abstentions. Je la transmets à la DSDEN avant les vacances, au plus tard le vendredi 16 octobre.

Mme Kasprzak : Et la dotation pour l'année prochaine, la DHG 2027-2028, on la verra quand ?

Mme Cordier : En général elle arrive fin janvier ou début février, et elle est présentée au conseil d'administration dans la foulée. Je n'ai pas de date pour l'instant, ça dépend du calendrier du rectorat.

Mme Kasprzak : D'accord, merci.

Point 5 — Budget

[Mme Arnaud-Poitevin quitte la séance à 19 h 05]

Mme Arnaud-Poitevin : Je vous prie de m'excuser, j'ai une réunion de commission au département à 19 h 30. Bonne fin de séance.

Mme Cordier : Merci madame. Nous sommes donc vingt. Et M. Lacombe nous a rejoints, bonsoir.

M. Lacombe (agent comptable) : Bonsoir à tous, désolé, le CA du lycée a été un peu long.

Mme Cordier : Ne vous excusez pas, on sait ce que c'est. [rires]

Mme Cordier : Mme Ferhat, le budget.

Mme Ferhat : Alors d'abord une information. Le département nous a notifié la dotation de fonctionnement pour 2027 : 148 600 euros. C'est une baisse d'environ 3 % par rapport à 2026, où on avait 153 200 euros. Le budget primitif 2027 sera préparé avec cette enveloppe et vous sera soumis au prochain conseil d'administration.

M. Pellerin : Une baisse de 3 %, alors que le prix de l'énergie continue d'augmenter, ça va être serré.

Mme Ferhat : Ça va être serré, oui. Les arbitrages figureront dans le budget primitif.

Ensuite, une décision budgétaire modificative pour vote, la DBM n° 3. Le four mixte de la cuisine est hors service depuis le 21 septembre. Le réparateur nous dit que la carte électronique et la sonde sont à changer, c'est presque le prix d'un four neuf, et le modèle n'est plus fabriqué. Mme Picot pourra vous le confirmer.

Mme Picot : Oui, depuis le 21 on fait avec le petit four et les plaques, on sert plus de crudités et de plats froids, les élèves l'ont remarqué.

Yanis (élève) : Ah oui, on l'a remarqué. [rires]

Mme Picot : Les élèves sont gentils, ils ne se plaignent pas trop. Mais les plats chauds leur manquent, surtout maintenant qu'il commence à faire froid.

Mme Ferhat : Le remplacement coûte 12 400 euros toutes taxes comprises, installation comprise. Je vous propose de le financer par un prélèvement sur le fonds de roulement du service de restauration et d'hébergement. Le fonds de roulement est aujourd'hui de 186 000 euros, soit environ 74 jours de fonctionnement. Après le prélèvement, on serait à 173 600 euros.

M. Lacombe : Je confirme que le niveau du fonds de roulement le permet. Ça reste largement au-dessus du seuil prudentiel qu'on se fixe, qui est de 30 jours.

Mme Delorme : Pardon, une question peut-être naïve. Le fonds de roulement, c'est quoi exactement ? C'est de l'argent qu'on a en réserve ?

M. Lacombe : Ce n'est pas naïf du tout. Le fonds de roulement, ce sont les réserves accumulées par le collège au fil des exercices, quand les recettes ont été supérieures aux dépenses. Il sert à faire face aux décalages de trésorerie et aux dépenses imprévues, comme justement une panne de four. Celui du service de restauration et d'hébergement est suivi à part, parce qu'il provient des repas payés par les familles et qu'il doit servir à la restauration.

Mme Delorme : D'accord. Donc on n'utilise pas l'argent des autres activités du collège pour la cantine.

M. Lacombe : Exactement : c'est l'argent de la restauration qui revient à la restauration.

M. Pellerin : Et soixante-quatorze jours, c'est un niveau normal pour un collège ?

M. Lacombe : C'est un niveau confortable. Beaucoup de collèges du département se situent plutôt entre quarante-cinq et soixante jours, donc vous avez de la marge, même après le prélèvement.

Mme Picot : Et je peux vous dire qu'en cuisine, on a hâte. Faire tous les repas du midi avec un petit four et des plaques, ce n'est pas tenable longtemps.

M. Pellerin : Une question de principe. Un four de cuisine collective, c'est de l'équipement, ce n'est pas au département de le payer ? Le département a un plan d'équipement pour les collèges. Pourquoi on ne demande pas à être inscrits sur le plan 2027 plutôt que de puiser dans nos réserves ?

Mme Ferhat : On peut le demander, mais le plan d'équipement 2027 sera arrêté au printemps, et le four serait livré au mieux en septembre prochain. On ne peut pas faire une année scolaire entière sans four.

M. Lebrun : Je ne peux pas parler au nom du département, Mme Arnaud-Poitevin est partie, mais je sais que le plan d'équipement est très demandé.

M. Pellerin : Dommage qu'elle soit partie justement. Bon, j'aurais préféré qu'on attende le plan, mais je comprends l'urgence.

Mme Cordier : On ne retient pas l'idée d'attendre le plan d'équipement, l'urgence est trop forte. Je mets aux voix la DBM n° 3 : prélèvement de 12 400 euros sur le fonds de roulement pour le remplacement du four mixte. Qui est contre ? Personne. Abstentions ? Trois. Adoptée : dix-sept pour, zéro contre, trois abstentions.

Mme Ferhat : Merci. Je lance la commande dès que la DBM sera exécutoire, c'est-à-dire après le délai de transmission au contrôle de légalité.

Mme Ferhat : Ensuite, pour information seulement, la DBM n° 4, qui ne se vote pas puisqu'il s'agit de recettes affectées : 3 200 euros de crédits supplémentaires de l'État pour le fonds social collégien, et 1 150 euros de la commune pour le dispositif « Collège au cinéma ».

M. Lebrun : Voilà, la commune fait sa part. [rires]

Mme Bellamy : « Collège au cinéma », ce sont trois films par an pour chaque classe inscrite, et les élèves adorent. Pour certains, c'est la seule occasion d'aller au cinéma.

M. Lebrun : C'est justement pour ça que la commune continue à le financer.

Mme Ferhat : Merci à la commune. Deux autres délibérations. D'abord, la convention d'utilisation du gymnase municipal pour l'année 2026-2027 : la commune met le gymnase à disposition pour les cours d'EPS, il faut autoriser Mme la principale à signer.

M. Marchetti : Sans le gymnase on fait cours sur le plateau extérieur, donc oui, autorisez. [rires]

M. Lebrun : Et la commune a refait l'éclairage du gymnase cet été, au passage. [rires]

Mme Cordier : Ce dont nous vous remercions, monsieur Lebrun.

Mme Cordier : Je mets aux voix l'autorisation de signer la convention d'utilisation du gymnase municipal pour 2026-2027. Contre ? Abstentions ? Adoptée à l'unanimité des vingt présents.

Mme Ferhat : Et enfin, l'acceptation d'un don. L'entreprise Menuiserie Fourcade Frères propose un don de 500 euros au club robotique… attendez, pardon, je relis le courrier : c'est 450 euros, pas 500. 450 euros, affectés à l'achat de kits de robotique pour le club.

Mme Cordier : 450 euros donc. Je mets aux voix l'acceptation du don de 450 euros de la Menuiserie Fourcade Frères au profit du club robotique. Contre ? Abstentions ? Adopté à l'unanimité.

M. Ostrowski : Et le budget primitif, on le vote quand ?

Mme Cordier : Au prochain conseil d'administration, qui sera aussi le premier conseil de la nouvelle mandature, avec l'installation des nouveaux membres. Ce sera le jeudi 19 novembre… non, pardon, je me trompe, le 19 c'est le conseil pédagogique. Le prochain CA, c'est le jeudi 26 novembre 2026, à 17 h 30.

Mme Ferhat : Et je vous enverrai les documents budgétaires au moins dix jours avant, donc au plus tard le lundi 16 novembre.

M. Lacombe : Je serai présent le 26 novembre.

Mme Cordier : Merci, c'est précieux d'avoir l'agent comptable pour l'examen du budget primitif.

Point 6 — Questions diverses

Mme Cordier : Nous avons reçu deux questions écrites, une des parents et une des élèves. Et M. Lebrun m'a dit qu'il voulait dire un mot. Mme Sy, pour les parents.

Mme Sy : Oui. Plusieurs familles nous signalent que les toilettes du bâtiment C sont fermées tous les après-midi depuis la rentrée. Les élèves doivent traverser toute la cour pour aller au bâtiment A, et certains n'y vont plus du tout de la journée.

Mme Picot : C'est parce qu'une collègue agent est en arrêt depuis début septembre et qu'elle n'est pas remplacée. On n'a pas assez de monde pour nettoyer le bâtiment C l'après-midi, alors on ferme.

Mme Cordier : Les agents sont des personnels du département. J'ai déjà signalé l'absence oralement, mais je vais écrire officiellement au département pour demander un remplacement. Je le fais cette semaine, avant le vendredi 9 octobre.

M. Lebrun : La commune ne peut pas mettre d'agent, ce n'est pas dans nos compétences, je le dis tout de suite.

Mme Sy : On ne vous demandait pas ça, monsieur. [rires]

Mme Sy : Ce qui inquiète surtout les familles, c'est que certains élèves se retiennent toute la journée. Ce n'est pas anodin, surtout pour les plus jeunes.

Mme Picot : On en est bien conscients, ce n'est pas de gaieté de cœur qu'on ferme. Quand l'équipe est au complet, le bâtiment C reste ouvert toute la journée, comme les autres années.

Mme Cordier : Yanis, pour les élèves ?

Yanis : Les élèves de sixième, ils ont des cartables trop lourds, ils demandent s'il pourrait y avoir des casiers pour laisser des livres.

M. Pellerin : Des casiers ? Je croyais qu'on avait dit que c'était trop cher, tout à l'heure.

Mme Cordier : Non, là ce n'est pas la même chose. Tout à l'heure c'était des casiers pour déposer les téléphones à l'entrée, et ça on l'a abandonné. Là, Yanis parle de casiers pour les affaires des sixièmes. C'est une autre demande.

Yanis : Oui, c'est pour les livres et les classeurs. En conseil de la vie collégienne, on a pesé des cartables de sixièmes, il y en avait qui pesaient presque dix kilos.

Mme Delorme : C'est vrai, mon fils était en sixième l'an dernier, il rentrait le soir avec le dos en compote.

Mme Ferhat : Je peux chiffrer des casiers pour les sixièmes et le présenter dans le cadre du budget primitif 2027, pour le CA du 26 novembre.

Mme Cordier : Très bien, Mme Ferhat chiffre et on en reparle au budget primitif. Ce n'est pas décidé ce soir. Mme Bellamy, vous aviez aussi une remarque ?

Mme Bellamy : Oui, très vite, la salle B12, il fait 15 degrés le matin. Le chauffage ne fonctionne pas bien depuis la remise en route.

Mme Ferhat : C'est déjà signalé au département, le 28 septembre. L'entreprise de maintenance doit passer, je n'ai pas encore de date.

Mme Kasprzak : Je confirme pour la B12, j'y ai cours le lundi à 8 heures, et les élèves gardent leur manteau pendant toute la première heure.

Mme Cordier : Le signalement du 28 septembre porte bien sur la B12.

M. Lebrun : Oui, alors moi, c'était pour vous informer que la commune organise le forum des associations samedi… non, c'était samedi dernier, pardon, il est passé. [rires] Non, ce que je voulais dire, c'est que la commune réfléchit à un « pédibus » pour les élèves du centre-bourg, mais c'est vraiment au stade de l'idée, on n'a rien décidé en conseil municipal.

Mme Cordier : Merci, vous nous tiendrez informés. Dernières informations de ma part : les élections des représentants des parents ont lieu ce vendredi 9 octobre, le vote se fait par correspondance ou à l'urne, au collège, de 8 heures à 12 heures. Et je rappelle la date du prochain conseil d'administration : jeudi 26 novembre 2026, 17 h 30. Est-ce qu'il y a d'autres questions ?

M. Ostrowski : Juste un mot pour remercier, puisque c'est la dernière séance pour plusieurs d'entre nous. Mme Delorme et moi, on ne se représente pas.

Mme Delorme : Oui, je m'associe. Ces années ont été très riches. On a vu passer beaucoup de dossiers, la réforme, les années de crise sanitaire aussi, et on a toujours été écoutés, même quand on n'était pas d'accord.

Mme Cordier : Merci à vous deux pour votre engagement pendant ces années. Merci à tous. La séance est levée, il est 20 h 05.

[Fin de l'enregistrement]
```

</details>

### `entree.nb_mots` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-4739
+6571
```

**Ancienne valeur** :

4739

**Nouvelle valeur** :

6571

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

## CO-001 — Correction (facile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0→v1.1 limité à fictif false→true et version_item 1→2 (lignes brutes identiques par ailleurs, ordre des clés conservé). Provenance service-public F21287 chunk 9 : texte_corrige_reference = colonne text du parquet figé, URL identique ; les 6 fautes appliquées à entree.texte redonnent la référence, positions et contextes exacts. valider_item strict OK. Pas d'incohérence : source et licence mentionnent déjà les fautes injectées pour l'évaluation.

Champs changés : `fictif`, `version_item`.

### `fictif` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-false
+true
```

**Ancienne valeur** :

false

**Nouvelle valeur** :

true

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

## CO-002 — Correction (facile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0→v1.1 limité à fictif false→true et version_item 1→2 (lignes brutes identiques par ailleurs, ordre des clés conservé). Provenance service-public F21766 chunk 4 : texte_corrige_reference = colonne text du parquet figé, URL identique ; les 6 fautes appliquées à entree.texte redonnent la référence, positions et contextes exacts. valider_item strict OK. Pas d'incohérence : source et licence mentionnent déjà les fautes injectées pour l'évaluation.

Champs changés : `fictif`, `version_item`.

### `fictif` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-false
+true
```

**Ancienne valeur** :

false

**Nouvelle valeur** :

true

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

## CO-006 — Correction (moyen, thème `travail-emploi`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0→v1.1 limité à fictif false→true et version_item 1→2 (lignes brutes identiques par ailleurs, ordre des clés conservé). Provenance service-public F12391 chunk 7 : texte_corrige_reference = colonne text du parquet figé, URL identique ; les 8 fautes appliquées à entree.texte redonnent la référence, positions et contextes exacts. valider_item strict OK. Pas d'incohérence de fictif. Remarque hors G4, héritée de v1.0 : nb_mots déclaré 138 contre 143 mots découpés sur les espaces.

Champs changés : `fictif`, `version_item`.

### `fictif` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-false
+true
```

**Ancienne valeur** :

false

**Nouvelle valeur** :

true

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

## CO-007 — Correction (moyen, thème `travail-emploi`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0→v1.1 limité à fictif false→true et version_item 1→2 (lignes brutes identiques par ailleurs, ordre des clés conservé). Provenance service-public F2262 chunk 3 : texte_corrige_reference = colonne text du parquet figé, URL identique ; les 8 fautes appliquées à entree.texte redonnent la référence, positions et contextes exacts. valider_item strict OK. Pas d'incohérence : source et licence mentionnent déjà les fautes injectées pour l'évaluation.

Champs changés : `fictif`, `version_item`.

### `fictif` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-false
+true
```

**Ancienne valeur** :

false

**Nouvelle valeur** :

true

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

## CO-011 — Correction (difficile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0→v1.1 limité à fictif false→true et version_item 1→2 (lignes brutes identiques par ailleurs, ordre des clés conservé). Provenance service-public F1648 chunk 9 : texte_corrige_reference = colonne text du parquet figé, URL identique ; les 12 fautes appliquées à entree.texte redonnent la référence, positions et contextes exacts. valider_item strict OK. Pas d'incohérence : source et licence mentionnent déjà les fautes injectées pour l'évaluation.

Champs changés : `fictif`, `version_item`.

### `fictif` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-false
+true
```

**Ancienne valeur** :

false

**Nouvelle valeur** :

true

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

## CO-012 — Correction (difficile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `accepte` (-, 2026-10-13) : Diff v1.0→v1.1 limité à fictif false→true et version_item 1→2 (lignes brutes identiques par ailleurs, ordre des clés conservé). Provenance service-public F1631 chunk 5 : texte_corrige_reference = colonne text du parquet figé, URL identique ; les 12 fautes appliquées à entree.texte redonnent la référence, positions et contextes exacts. valider_item strict OK. Pas d'incohérence : source et licence mentionnent déjà les fautes injectées pour l'évaluation.

Champs changés : `fictif`, `version_item`.

### `fictif` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-false
+true
```

**Ancienne valeur** :

false

**Nouvelle valeur** :

true

### `version_item` (modifié)

Différences, ligne à ligne (JSON) :

```diff
--- ancien
+++ nouveau
@@ -1 +1 @@
-1
+2
```

**Ancienne valeur** :

1

**Nouvelle valeur** :

2

# Items retirés (3)

## Q-044 — Question (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `rejete` (autre, 2026-10-13) : Remplacement décidé par l'arbitrage E de eval/revue/arbitrages-v1.1.md (couverture : aucun item sur les marchés publics, option 1, précisée par la section « Ajustements validés (2026-10-13) », point 1) : les 60 Q suivent exactement les parts de SPEC §2, donc 3 items « collectivites » cèdent la place à 3 items sur les marchés publics, aux mêmes difficultés. Q-044 (facile) est remplacé par Q-068 (facile, collectivites, sans_reponse false). L'item lui-même n'est pas mis en cause.

Ancien item :

**entree** : Une association de quartier souhaite fixer son siège social à la mairie et utiliser une salle communale pour ses réunions. Est-ce possible, et qui fixe les conditions d'utilisation et l'éventuel montant à payer ?

**amorce_usager** : Quelle est la participation financière fixée par le conseil municipal pour la mise à disposition de locaux communaux ?

**parametres** : {}

**reponse_reference** : Oui, une mairie peut être le siège social d'une association ; l'association en fait la demande à la mairie par courrier. Si le maire le décide, des locaux communaux peuvent être mis à disposition des associations qui en font la demande, et c'est le maire qui fixe les conditions d'utilisation (par exemple jours de mise à disposition, conditions d'accès, horaires, répartition des bureaux). La mise à disposition peut être gratuite ou payante ; le montant du loyer ou de la participation est fixé par le conseil municipal. Ne vaut pas avis juridique.

### elements_cles

- Oui, une mairie peut être le siège social d'une association, sur demande par courrier
- Mise à disposition de locaux communaux si le maire le décide ; le maire fixe les conditions d'utilisation
- Mise à disposition gratuite ou payante ; le loyer ou la participation est fixé par le conseil municipal

### sources_attendues

- https://www.service-public.gouv.fr/particuliers/vosdroits/F1174

**sans_reponse** : false

**mention_obligatoire** : Ne vaut pas avis juridique

### provenance

-
  - **source** : AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)
  - **url** : https://huggingface.co/datasets/AgentPublic/sp_questions_corpus/resolve/495a22cf7b572621a85d2f3e97783b2f4189c47e/gpt_corpus-20kq%26A.xlsx
  - **ligne** : 8991
  - **role** : amorce de question usager, reformulée par un agent
  - **consulte_le** : 2026-10-12
-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F1174 « Une mairie peut-elle être le siège social d'une association ? »
  - **url** : https://www.service-public.gouv.fr/particuliers/vosdroits/F1174
  - **chunks** :
    - 1
  - **extrait** : Oui, une mairie peut être le siège social d’une association. […] L'association doit faire la demande à la mairie par courrier. Si le maire le décide, des locaux communaux peuvent être mis à disposition et utilisés par les associations qui en font la demande. Le maire fixe les conditions dans lesquelles ces locaux peuvent être utilisés. […] La mise à disposition du local peut être gratuite ou payante. Le montant du loyer ou de la participation est fixée par le conseil municipal.
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-12

**licence_source** : Amorce : MIT (carte du dataset). Fiche : Licence Ouverte / Etalab 2.0.

**fictif** : false

**version_item** : 1

## Q-046 — Question (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `rejete` (autre, 2026-10-13) : Remplacement décidé par l'arbitrage E de eval/revue/arbitrages-v1.1.md (couverture : aucun item sur les marchés publics, option 1, précisée par la section « Ajustements validés (2026-10-13) », point 1) : les 60 Q suivent exactement les parts de SPEC §2, donc 3 items « collectivites » cèdent la place à 3 items sur les marchés publics, aux mêmes difficultés. Q-046 (moyen) est remplacé par Q-069 (moyen, collectivites, sans_reponse false). L'item lui-même n'est pas mis en cause.

Ancien item :

**entree** : Je réorganise le traitement des permis de construire au service urbanisme de notre commune (projets hors secteur protégé). Quels délais d'instruction s'appliquent, comment traiter un dossier incomplet, et que se passe-t-il si nous ne répondons pas dans le délai ?

**amorce_usager** : Comment optimiser le traitement des permis de construire?

**parametres** : {}

**reponse_reference** : Hors secteur protégé, le délai d'instruction court à partir du dépôt du dossier complet en mairie : 2 mois pour une maison individuelle, 3 mois pour les autres projets. Si le dossier est incomplet, la mairie adresse au demandeur, dans le délai d'1 mois à compter de la réception ou du dépôt de la demande, une demande des pièces manquantes, par lettre ou par voie électronique ; le demandeur a 3 mois pour les envoyer, faute de quoi sa demande est considérée comme rejetée, et le délai d'instruction ne démarre que lorsque le dossier est complet. Si la mairie ne répond pas à la fin du délai d'instruction, le projet est accepté : c'est un permis de construire tacite, et la mairie doit délivrer, sur simple demande, un certificat de non-opposition. Ne vaut pas avis juridique.

### elements_cles

- Dossier complet : délai d'instruction de 2 mois pour une maison individuelle, 3 mois pour les autres projets
- Dossier incomplet : demande des pièces manquantes dans le délai d'1 mois à compter de la réception ou du dépôt
- Le demandeur a 3 mois pour fournir les pièces, sinon la demande est considérée comme rejetée ; le délai d'instruction démarre quand le dossier est complet
- Sans réponse à la fin du délai : permis de construire tacite ; certificat de non-opposition délivré sur simple demande

### sources_attendues

- https://www.service-public.gouv.fr/particuliers/vosdroits/F1986

**sans_reponse** : false

**mention_obligatoire** : Ne vaut pas avis juridique

### provenance

-
  - **source** : AgentPublic/assistant_ia_questions_corpus (evaluation_qo_assistant_ia_v1.xlsx)
  - **url** : https://huggingface.co/datasets/AgentPublic/assistant_ia_questions_corpus/resolve/62cef57af7cc5fe54862a8118c221246771ad9ea/evaluation_qo_assistant_ia_v1.xlsx
  - **ligne** : 13
  - **role** : amorce de question usager, reformulée et recentrée par un agent sur le contenu de la fiche
  - **consulte_le** : 2026-10-12
-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F1986 « Permis de construire (PC) »
  - **url** : https://www.service-public.gouv.fr/particuliers/vosdroits/F1986
  - **chunks** :
    - 10
    - 12
  - **extrait** : Pour une maison individuelle , le délai d'instruction est de 2 mois à partir de la date de dépôt du dossier complet en mairie. Pour les autres projets , le délai est de 3 mois . […] Dans le délai d'1 mois à compter de la réception ou du dépôt de votre demande de permis à la mairie, elle vous adresse par lettre ou par voie électronique une demande des pièces manquantes. Vous avez 3 mois pour envoyer les pièces demandées. Si vous ne les fournissez pas, votre demande de permis sera considérée comme rejetée. Le délai d'instruction démarre quand votre dossier est complet. […] Si vous ne recevez pas de réponse de la mairie à la fin du délai d'instruction, votre projet est accepté. Il s'agit d'un permis de construire tacite. Sur simple demande de votre part, la mairie doit vous délivrer un certificat de non-opposition.
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-12

**licence_source** : Amorce : MIT (carte du dataset). Fiche : Licence Ouverte / Etalab 2.0.

**fictif** : false

**version_item** : 1

## Q-050 — Question (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

**Dernier verdict** : `rejete` (autre, 2026-10-13) : Remplacement décidé par l'arbitrage E de eval/revue/arbitrages-v1.1.md (couverture : aucun item sur les marchés publics, option 1, précisée par la section « Ajustements validés (2026-10-13) », point 1) : les 60 Q suivent exactement les parts de SPEC §2, donc 3 items « collectivites » cèdent la place à 3 items sur les marchés publics, aux mêmes difficultés. Q-050 (difficile) est remplacé par Q-070 (difficile, collectivites, sans_reponse false). L'item lui-même n'est pas mis en cause.

Ancien item :

**entree** : Un salarié d'une entreprise privée vient d'être élu adjoint au maire d'une commune de 12 000 habitants. Il travaille à mi-temps (50 %). Quel crédit d'heures trimestriel peut-il utiliser, dans quelle limite annuelle, et comment doit-il prévenir son employeur ? Son employeur peut-il refuser ?

**amorce_usager** : Quels sont les crédits d'heures accordés à un élu municipal pour l'exercice de son mandat ?

**parametres** : {}

**reponse_reference** : Pour un adjoint au maire d'une commune de 10 000 à 29 999 habitants, le crédit d'heures légal est de 122 heures 30 par trimestre. Comme il travaille à temps partiel, ce crédit est réduit proportionnellement à la réduction de son temps de travail : à 50 %, il est de 61 heures 15 par trimestre (le crédit peut être majoré de 30 % au maximum dans certaines communes, par exemple chefs-lieux ou stations de tourisme). Les heures non utilisées ne sont pas reportées d'un trimestre à l'autre, et la durée cumulée des absences autorisées et du crédit d'heures ne peut pas dépasser 803 heures 30 par an. Il doit informer son employeur par écrit au moins 3 jours avant son absence, en indiquant la date et la durée de l'absence et le crédit d'heures qui lui reste pour le trimestre. L'employeur ne peut ni refuser ni reporter la demande, sauf si elle conduit à dépasser les 803 heures 30 annuelles. Ne vaut pas avis juridique.

### elements_cles

- Adjoint au maire d'une commune de 10 000 à 29 999 habitants : 122 heures 30 par trimestre
- Réduction proportionnelle au temps partiel : à 50 %, 61 heures 15 par trimestre (majoration possible de 30 % au maximum dans certaines communes)
- Heures non reportées d'un trimestre à l'autre ; absences autorisées et crédit d'heures cumulés plafonnés à 803 heures 30 par an
- Information écrite de l'employeur au moins 3 jours avant, avec date, durée de l'absence et crédit restant pour le trimestre
- L'employeur ne peut ni refuser ni reporter, sauf dépassement des 803 heures 30 annuelles

### sources_attendues

- https://www.service-public.gouv.fr/particuliers/vosdroits/F2310

**sans_reponse** : false

**mention_obligatoire** : Ne vaut pas avis juridique

### provenance

-
  - **source** : AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)
  - **url** : https://huggingface.co/datasets/AgentPublic/sp_questions_corpus/resolve/495a22cf7b572621a85d2f3e97783b2f4189c47e/gpt_corpus-20kq%26A.xlsx
  - **ligne** : 5989
  - **role** : amorce de question usager, reformulée par un agent
  - **consulte_le** : 2026-10-12
-
  - **source** : MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F2310 « Élu local salarié : absence et crédits d'heures »
  - **url** : https://www.service-public.gouv.fr/particuliers/vosdroits/F2310
  - **chunks** :
    - 11
    - 12
  - **extrait** :
    ```text
    | Adjoint au maire | Moins de 10 000 habitants | 70 heures | 
    | Entre 10 000 et 29 999 habitants | 122 heures 30 | […] En cas de travail à temps partiel, ce crédit d'heures est réduit proportionnellement à la réduction du temps de travail prévue pour l'emploi considéré. Les heures non utilisées ne sont pas reportées d'un trimestre à l'autre. La durée cumulée des absences autorisées et du crédit d'heures ne doit pas dépasser 803 heures 30 par an. (À noter: Le crédit d'heures peut être majoré de 30% maximum, notamment dans les communes chefs-lieux de département et d'arrondissement ou classées stations de tourisme ou sinistrées.) […] Le salarié informe son employeur par écrit 3 jours au moins avant son absence. Cet écrit doit comporter les éléments suivants :
    - Date et durée de l'absence envisagée
    - Durée du crédit d'heures à laquelle il a encore droit au titre du trimestre en cours.
    L'employeur ne peut pas refuser ou reporter la demande du salarié, sauf s'il dépasse la durée totale d'absence autorisée (crédit d'heures et autorisations d'absence cumulées) de 803 heures 30 par an.
    ```
  - **role** : fiche de référence
  - **consulte_le** : 2026-10-12

**licence_source** : Amorce : MIT (carte du dataset). Fiche : Licence Ouverte / Etalab 2.0.

**fictif** : false

**version_item** : 1
