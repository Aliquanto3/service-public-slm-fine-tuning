---
story: E1b
status: review
---

# E1b — Bootstrap apparié des scores

Outil : `slmsp eval comparer --runs <A> <B> [...] [--bootstrap 2000] [--graine 7] [--sortie f.md] [--racine DIR]`
(module `src/slmsp/evaluation/bootstrap.py`). Lecture seule, aucun appel au juge. Le recalcul sans
rééchantillonnage redonne `scores.json` (vérifié, sinon erreur). Rééchantillonnage des `item_id` par
Tâche, mêmes items pour tous les runs ; Qualité = moyenne des scores de Tâche ; IC en percentiles.

## Décisions
- Premier run = référence A ; écart = B − A ; P(écart > 0) strict (les égalités comptent comme non).
- Seuils lus dans `config/evaluation.toml` de `racine_projet()` (comme la notation) ; items communs aux runs si leurs sélections diffèrent.
- Le second juge n'entre pas dans le bootstrap (il n'influe pas sur les scores, seulement sur le kappa).

## Résultat réel (jeu v1.1, q4_k_m, 2000 tirages, graine 7)
A = Baseline `base:minicpm5-2b` (`20261018-112201-minicpm5-2b-e6f2`) ; B = M1 v14 (`20261020-020503-ft-minicpm5-2b-2083`) puis v15 (`20261020-040734-ft-minicpm5-2b-8953`).

Bootstrap apparié : 2000 tirages, graine 7, IC 95% (percentiles). Écart = B − A.

Items communs : Q 60, RD 40, CR 25, LC 25, CO 15, RE 15, CT 15, NR 30

Revue : colonne « Tirages » (tirages valides) et note sur le plafond de LC ajoutées à la sortie ; avertissements si les ensembles de tâches ou d'items diffèrent (aucun ici). Chiffres inchangés.

### A = `20261018-112201-minicpm5-2b-e6f2` ; B = `20261020-020503-ft-minicpm5-2b-2083`

| Tâche | A | B | Écart B − A | IC 95 % de l'écart | P(écart > 0) |
|---|---|---|---|---|---|
| Q | 5.0 | 1.7 | -3.3 | [-8.3 ; +0.0] | 0.000 |
| RD | 75.1 | 83.2 | +8.1 | [-2.0 ; +18.4] | 0.932 |
| CR | 50.1 | 33.9 | -16.2 | [-27.7 ; -5.5] | 0.001 |
| LC | 24.0 | 0.0 | -24.0 | [-40.0 ; -8.0] | 0.000 |
| CO | 58.9 | 74.1 | +15.2 | [+7.4 ; +25.3] | 1.000 |
| RE | 35.5 | 31.9 | -3.5 | [-17.4 ; +8.7] | 0.291 |
| CT | 50.0 | 46.7 | -3.3 | [-10.0 ; +0.0] | 0.000 |
| NR | 30.0 | 16.7 | -13.3 | [-26.7 ; -3.3] | 0.000 |
| Qualité | 41.1 | 36.0 | -5.0 | [-9.2 ; -1.2] | 0.004 |

### A = `20261018-112201-minicpm5-2b-e6f2` ; B = `20261020-040734-ft-minicpm5-2b-8953`

| Tâche | A | B | Écart B − A | IC 95 % de l'écart | P(écart > 0) |
|---|---|---|---|---|---|
| Q | 5.0 | 5.0 | +0.0 | [-6.7 ; +6.7] | 0.394 |
| RD | 75.1 | 76.9 | +1.8 | [-9.8 ; +13.6] | 0.600 |
| CR | 50.1 | 32.0 | -18.1 | [-28.5 ; -9.0] | 0.000 |
| LC | 24.0 | 0.0 | -24.0 | [-40.0 ; -8.0] | 0.000 |
| CO | 58.9 | 72.6 | +13.8 | [+6.0 ; +24.0] | 1.000 |
| RE | 35.5 | 35.5 | +0.1 | [-11.6 ; +9.1] | 0.518 |
| CT | 50.0 | 46.7 | -3.3 | [-10.0 ; +0.0] | 0.000 |
| NR | 30.0 | 16.7 | -13.3 | [-26.7 ; -3.3] | 0.000 |
| Qualité | 41.1 | 35.7 | -5.4 | [-9.3 ; -1.7] | 0.001 |

Bruit items de la Qualité d'un run seul (demi-écart de l'IC 95 %) :

- `20261018-112201-minicpm5-2b-e6f2` : ± 3.9
- `20261020-020503-ft-minicpm5-2b-2083` : ± 2.7
- `20261020-040734-ft-minicpm5-2b-8953` : ± 2.6

## Lecture
Bruit items de la Qualité d'un run seul : environ ± 2,6 à 3,9 points (IC 95 %). Les écarts de Qualité Baseline → M1 (−5,0 et −5,4) sortent de ce bruit (IC de l'écart [−9,2 ; −1,2] et [−9,3 ; −1,7]), mais v14 et v15 ne se distinguent pas entre eux à cette échelle. Q, RE, RD : IC de l'écart contenant 0.

## Auto Run Result
Statut : review. Tests : `tests/evaluation/test_bootstrap.py` (6). Report : comparaison v14 vs v15 directe (passer v14 en A) non lancée ; variance d'entraînement non couverte (seuls les items sont rééchantillonnés).
