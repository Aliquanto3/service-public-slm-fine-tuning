# Revue de la story O4b — jeu de développement dev1

Revue du 2026-10-20 (reviewer, Claude Opus 5.5), qui tient lieu de **relecture Claude** du jeu (§7 bis du plan). Branche `story/o4b-construction-dev1`. Elle s'appuie sur la liste du second avis (Haiku), sur des contrôles automatiques des 160 items et sur un échantillon de 24 items relus contre leurs sources. La contre-vérification DeepSeek + GLM suit.

## Contrôles automatiques (160 items)

Ils portent sur les instantanés `data/raw/eval-sources` du dépôt principal : service-public rév. 29f236f8a5, legi rév. 68b01fbbe0, catalogue rév. 11f3d3c948. Ils sont repris dans `tests/eval_outils/test_items_dev1.py`, sautés quand les sources sont absentes.

- **CO** : sur les 20 items, appliquer les fautes déclarées à l'entrée redonne exactement `texte_corrige_reference`. Les CO réels reprennent la fiche à l'espacement près, aux coupures près et aux coquilles de la source corrigées près (CO-508 « temps de travail », CO-509 « l'acte de vente »).
- **Q** : les 20 extraits figurent dans les chunks cités. Les 6 écarts au verbatim strict ne tiennent qu'aux blancs (listes aplaties).
- **RE** : chaque document est la suite de ses chunks, sans ajout ni modification. Il n'en retire que les recouvrements entre chunks et, pour RE-502, une fin de chunk incomplète.
- **CT** : chaque article cité entre « » figure verbatim dans l'article LEGI en vigueur. Cela couvre aussi les deux items qui citent deux articles (CT-515, CT-520).
- **LC** : 5 items demandaient de conserver un terme absent du texte d'entrée (corrigés, voir plus bas). Les autres écarts ne tiennent qu'à la graphie LEGI (« Etat », « A titre »).
- **RD** : les 20 cassettes RD-501 à RD-520 sont toutes citées et aucune n'est orpheline. Les 2 replis sont recoupés avec le catalogue local, après correction de leur identifiant. Les valeurs ont été vérifiées dans les cassettes pour RD-509, RD-512 et RD-518.
- **Dates** : chaque jour de semaine associé à une date est cohérent, dans les 160 items.
- **Disjonction** (outil étendu, voir plus bas) : dev1 est disjoint de v1.0, de v1.1, des 13 `train.jsonl`, des 3 `preferences.jsonl` et des 4 runs seed.

## Échantillon relu (24 items, 3 par Tâche : 502, 509, 518)

Critères : référence appuyée par la source, consigne non ambiguë, une seule bonne réponse prévue, grille applicable.

| Tâche | Items | Constat |
|---|---|---|
| Q | 502, 509, 518 | conformes : faits relus dans F15132, F1962 et F24569 (y compris l'eau et le pain en libre accès et l'absence de collation) |
| RD | 502, 509, 518 | RD-502 : `jeu_principal.id` était le slug de l'URL, pas l'identifiant du catalogue → corrigé ; 509 et 518 : valeurs retrouvées dans les cassettes |
| CR | 502, 509, 518 | conformes : décisions, actions et pièges retrouvés dans les notes et transcriptions ; dates cohérentes |
| LC | 502, 509, 518 | LC-509 : terme « retrait-gonflement des argiles (RGA) » absent du texte (le sigle n'y figure pas) → corrigé |
| CO | 502, 509, 518 | CO-518 : faute « entrainemants » → « entraînements », alors que la graphie rectifiée « entrainements » est aussi juste ; le rappel l'aurait comptée non corrigée → faute remplacée |
| RE | 502, 509, 518 | conformes : points clés retrouvés dans le document (montants, délais, règles des congés payés) |
| CT | 502, 509, 518 | conformes ; CT-509 et CT-518 reprennent le même scénario (demande mal adressée, CRPA L. 114-2) : diversité moindre, sans défaut |
| NR | 502, 509, 518 | conformes : calculs refaits, dates cohérentes |

**Taux de défaut de l'échantillon : 3 / 24 (12,5 %)**, tous corrigés, sans item écarté. Les contrôles automatiques ont aussi corrigé 5 items hors échantillon (LC-503, LC-508, LC-511, LC-512 et RD-513).

## Constats et suites

| # | Sévérité | Constat | Suite |
|---|---|---|---|
| 1 | medium (second avis) | CO-508 garde « connaitre » alors que l'item compte 8 fautes | **Rejeté** : « connaitre » est la graphie rectifiée (1990) et il figure tel quel dans la fiche. Les 8 fautes déclarées rendent exactement la référence (contrôle automatique sur les 20 CO, désormais testé). Un modèle qui écrit « connaître » ne perd qu'un mot hors faute sur 180. |
| 2 | medium (second avis) | dev1 hors des contrôles de verbatim et de sources | **Corrigé** : nouveau `test_items_dev1.py`, vert avec `SLMSP_EVAL_SOURCES` (97 tests). Ajouter dev1 aux `VERSIONS` de v1.x aurait cassé 139 tests sur des constantes propres à v1.x (identifiants, dates, composition, verbatim strict, provenance avec `url`). |
| 3 | medium | 5 LC exigeaient un terme absent du texte d'entrée (LC-503, LC-508, LC-509, LC-511, LC-512) : critère « Termes » inapplicable | **Corrigé** : chaque terme est remplacé par sa forme présente dans le texte, ou retiré pour LC-503 (`version_item` 2) ; c'est désormais testé |
| 4 | medium | RD-502 et RD-513 (replis) : identifiant du jeu = slug, au lieu de l'identifiant du catalogue | **Corrigé** : identifiant du catalogue, cité aussi dans le texte de référence comme en v1.x (`version_item` 2) |
| 5 | medium | CO-518 : deux corrections justes pour une même faute | **Corrigé** : « entraînements » rétabli, nouvelle faute « gymnasse » et positions recalculées (`version_item` 2) |
| 6 | low (second avis) | disjonction par URL seulement : une provenance sans `url` (amorces Q de dev1 notamment) échappait au contrôle | **Corrigé** : `sources_item` compare aussi la fiche (`doc_id` ou fin d'URL), l'article LEGI (`legiarti`) et la ligne de corpus (`fichier`/URL et `ligne`) ; testé |
| 7 | low (second avis) | `preferences.jsonl` hors de la disjonction | **Corrigé** : `prompt`, `chosen` et `rejected` sont indexés ; testé. dev1 reste disjoint (22 jeux lus) |
| 8 | low (second avis) | aucun test ne vérifie que RD-501 à RD-520 sont toutes citées | **Corrigé** : `test_rd_cassettes_501_a_520_toutes_citees` |
| 9 | low | RD : fragments `contient_un_de` non normalisés (« prime d'activité ») et montants avec espace de milliers (« 15 560 ») | **Rejeté** : la notation normalise aussi le fragment (`_debut_de_mot`) et lit les nombres avec séparateur ; sans effet sur le score |
| 10 | low | CT-509 et CT-518 : même scénario et même article | **Rejeté** (signalé) : items justes, ils diffèrent par le type de courrier et l'objet |

Après correction : `items.jsonl` réassemblé (SHA-256 `43592b78…`) ; `slmsp eval gel --version dev1 --verifier-seulement` : 160 items, 0 erreur, 0 écart ; disjonction : disjoint.
