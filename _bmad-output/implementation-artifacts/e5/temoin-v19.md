Bootstrap apparié : 2000 tirages, graine 7, IC 95% (percentiles). Écart = B − A.

Items communs : Q 20, RD 20, CR 19, LC 20, CO 20, RE 20, CT 20, NR 20
Avertissement : jeu de développement (relu-llm) : comparaison pour décider, jamais une mesure finale

Note : le score de LC est plafonné quand le gain de Kandel-Moles du tirage passe sous le seuil ; le plafond dépend donc du tirage.

### A = `20261020-165745-minicpm5-2b-afd3` ; B = `20261020-232214-ft-minicpm5-2b-5203`

| Tâche | A | B | Écart B − A | IC 95 % de l'écart | P(écart > 0) | Tirages |
|---|---|---|---|---|---|---|
| Q | 15.0 | 10.0 | -5.0 | [-20.0 ; +10.0] | 0.181 | 2000 |
| RD | 74.8 | 81.0 | +6.2 | [-6.2 ; +18.7] | 0.833 | 2000 |
| CR | 75.3 | 49.4 | -25.9 | [-41.0 ; -10.4] | 0.000 | 2000 |
| LC | 50.0 | 35.0 | -15.0 | [-30.0 ; +5.0] | 0.035 | 2000 |
| CO | 72.1 | 84.2 | +12.1 | [+5.5 ; +19.2] | 1.000 | 2000 |
| RE | 58.5 | 46.9 | -11.6 | [-24.7 ; +2.1] | 0.052 | 2000 |
| CT | 45.0 | 51.2 | +6.2 | [+0.0 ; +13.8] | 0.957 | 2000 |
| NR | 45.0 | 45.0 | +0.0 | [-15.0 ; +15.0] | 0.351 | 2000 |
| Qualité | 54.5 | 50.4 | -4.1 | [-8.5 ; +1.1] | 0.067 | 2000 |

Bruit items de la Qualité d'un run seul (demi-écart de l'IC 95 %) :

- `20261020-165745-minicpm5-2b-afd3` : ± 4.5
- `20261020-232214-ft-minicpm5-2b-5203` : ± 4.5
