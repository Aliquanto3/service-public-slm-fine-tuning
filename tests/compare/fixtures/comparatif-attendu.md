# Comparatif des méthodes de fine-tuning : campagne camp-test

## Synthèse et recommandation

| Méthode | SM-1 | Évalué sur | Détail |
|---|---|---|---|
| M1 (qlora, run 20261001-100000-m1-qlora-abcd) | satisfait | q4_k_m | seuils respectés |
| M4 (orpo, run 20261001-110000-m4-orpo-beef) | indéterminé | non mesuré | aucune évaluation du modèle fine-tuné |

**Recommandation.** M1 (qlora, run 20261001-100000-m1-qlora-abcd) satisfait SM-1 : candidat au Modèle embarqué, sous réserve de la relecture humaine des verdicts et de la décision d'Anaël.
Des Scores sont « non relus » : la relecture est exigée pour la décision finale de SM-1.

## Meilleure Baseline par Tâche

| Tâche | Score | Modèle |
|---|---|---|
| Q | 40.0 | base:granite (q4_k_m) |
| RD | 55.0 | base:autre (q4_k_m) |
| CR | 30.0 | base:granite (q4_k_m) |
| LC | 45.0 | base:granite (q4_k_m) |
| NR | 62.0 | base:autre (q4_k_m) |

## Gain par Tâche, en points, par rapport à la meilleure Baseline

### M1 (qlora, run 20261001-100000-m1-qlora-abcd)

| Tâche | Baseline | f16 | gain f16 | q4_k_m | gain q4_k_m |
|---|---|---|---|---|---|
| Q | 40.0 | 52.0 | +12.0 | 51.0 | +11.0 |
| RD | 55.0 | 68.0 | +13.0 | 67.0 | +12.0 |
| CR | 30.0 | 33.0 | +3.0 | 32.0 | +2.0 |
| LC | 45.0 | 46.0 | +1.0 | 45.0 | +0.0 |
| NR | 62.0 | 60.0 | -2.0 | 59.0 | -3.0 |

### M4 (orpo, run 20261001-110000-m4-orpo-beef)

| Tâche | Baseline | f16 | gain f16 | q4_k_m | gain q4_k_m |
|---|---|---|---|---|---|
| Q | 40.0 | non mesuré | non mesuré | non mesuré | non mesuré |
| RD | 55.0 | non mesuré | non mesuré | non mesuré | non mesuré |
| CR | 30.0 | non mesuré | non mesuré | non mesuré | non mesuré |
| LC | 45.0 | non mesuré | non mesuré | non mesuré | non mesuré |
| NR | 62.0 | non mesuré | non mesuré | non mesuré | non mesuré |

## Effet sur les Benchmarks, avant et après quantification

### M1 (qlora, run 20261001-100000-m1-qlora-abcd)

| Benchmark | avant | écart avant | après | écart après |
|---|---|---|---|---|
| arc | acc = 49.0 | -1.0 | acc = 48.5 | -0.5 |

### M4 (orpo, run 20261001-110000-m4-orpo-beef)

| Benchmark | avant | écart avant | après | écart après |
|---|---|---|---|---|
| arc | non mesuré | non mesuré | non mesuré | non mesuré |

## Coûts d'entraînement

| Méthode | Durée | VRAM maximale | Énergie | Débit (tokens/s) |
|---|---|---|---|---|
| M1 (qlora, run 20261001-100000-m1-qlora-abcd) | 3600 s | 4.00 Go | 250.5 Wh | 1200 |
| M4 (orpo, run 20261001-110000-m4-orpo-beef) | 1800 s | 5.00 Go | 140.0 Wh | non mesuré |

## Deux vues de comparaison (FR-34), gain en points par Tâche

### À tokens vus égaux

Point de comparaison : 1500 tokens (le plus petit maximum atteint).

| Méthode | Point retenu | Q | RD | CR | LC | NR |
|---|---|---|---|---|---|---|
| M1 (qlora, run 20261001-100000-m1-qlora-abcd) | 1000 tokens | +5.0 | -3.0 | non mesuré | non mesuré | non mesuré |
| M4 (orpo, run 20261001-110000-m4-orpo-beef) (hors protocole) | 1500 tokens | +8.0 | +3.0 | non mesuré | non mesuré | non mesuré |

### À budget de temps égal

Point de comparaison : 900 s (le plus petit maximum atteint).

| Méthode | Point retenu | Q | RD | CR | LC | NR |
|---|---|---|---|---|---|---|
| M1 (qlora, run 20261001-100000-m1-qlora-abcd) | 600 s | +5.0 | -3.0 | non mesuré | non mesuré | non mesuré |
| M4 (orpo, run 20261001-110000-m4-orpo-beef) (hors protocole) | 900 s | +8.0 | +3.0 | non mesuré | non mesuré | non mesuré |

## Dérogation au protocole : M4 (ORPO)

M4 déroge au protocole de comparaison équitable : ORPO a besoin de données de préférence, dérivées du jeu SFT, et passe après le SFT. Ses résultats ne sont pas strictement comparables à ceux de M1 à M3 (FR-34).

## Méthode et limites

Ce rapport est calculé uniquement à partir des résultats archivés (évaluations, Benchmarks, entraînements, exports) : il n'interroge aucun modèle et n'utilise aucun réseau. Régénéré à partir des mêmes archives, il est identique.

- Version du jeu d'évaluation : v1.1 (statut : relu). Deux versions du jeu ne sont jamais mélangées.
- Seuls les runs complets sont pris en compte ; les autres figurent dans « Runs exclus ».
- Le gain est l'écart de Score de Tâche, en points sur 100, avec le meilleur score obtenu par un Modèle de base (Baseline) sur cette Tâche.
- SM-1 : au moins 10 points de gain sur au moins 2 des Tâches prioritaires (Q, RD, CR, LC), perte d'au plus 3 points en non-régression et 3 points en moyenne sur les Benchmarks. Le verdict s'appuie sur la version quantifiée (q4_k_m) si elle est évaluée, sinon sur f16.
- Chaque Baseline est une configuration (modèle et quantification) prise comme un tout. La meilleure Baseline livrable est quantifiée q4_k_m et notée sur toutes les Tâches prioritaires (règle à confirmer par Anaël).
- Les Benchmarks servent à détecter les régressions, pas à choisir le Modèle. La métrique, son échelle et son sens sont fixés par Benchmark dans `config/comparatif.toml` ; sans cette configuration, le Benchmark est « non comparable » et SM-1 reste indéterminé.
- Une valeur « non mesuré » n'a pas été archivée ; « à compléter » signale une vue qui demande des évaluations intermédiaires. Rien n'est estimé.
- Les Scores marqués « non relus » n'ont pas été validés par une relecture humaine.
- Les mesures viennent de la machine de développement, qui n'est pas le PC cible.
