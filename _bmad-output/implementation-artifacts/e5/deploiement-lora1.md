Bootstrap apparié : 2000 tirages, graine 7, IC 95% (percentiles). Écart = B − A.

Items communs : Q 20, RD 20, CR 19, LC 20, CO 20, RE 20, CT 20, NR 20
Avertissement : jeu de développement (relu-llm) : comparaison pour décider, jamais une mesure finale

Note : le score de LC est plafonné quand le gain de Kandel-Moles du tirage passe sous le seuil ; le plafond dépend donc du tirage.

### A = `20261020-181808-ft-minicpm5-2b-213f` ; B = `20261021-002259-lora-minicpm5-2b-456f`

| Tâche | A | B | Écart B − A | IC 95 % de l'écart | P(écart > 0) | Tirages |
|---|---|---|---|---|---|---|
| Q | 15.0 | 20.0 | +5.0 | [+0.0 ; +15.0] | 0.630 | 2000 |
| RD | 84.8 | 82.3 | -2.5 | [-7.5 ; +0.0] | 0.000 | 2000 |
| CR | 40.4 | 52.3 | +11.9 | [+4.5 ; +20.3] | 1.000 | 2000 |
| LC | 30.0 | 25.0 | -5.0 | [-25.0 ; +15.0] | 0.240 | 2000 |
| CO | 82.5 | 81.2 | -1.3 | [-4.4 ; +1.8] | 0.206 | 2000 |
| RE | 40.7 | 43.1 | +2.4 | [-9.5 ; +13.0] | 0.672 | 2000 |
| CT | 45.0 | 35.0 | -10.0 | [-20.1 ; +0.0] | 0.019 | 2000 |
| NR | 40.0 | 40.0 | +0.0 | [-15.0 ; +15.0] | 0.340 | 2000 |
| Qualité | 47.3 | 47.4 | +0.1 | [-4.2 ; +4.1] | 0.534 | 2000 |

Bruit items de la Qualité d'un run seul (demi-écart de l'IC 95 %) :

- `20261020-181808-ft-minicpm5-2b-213f` : ± 4.9
- `20261021-002259-lora-minicpm5-2b-456f` : ± 4.9
