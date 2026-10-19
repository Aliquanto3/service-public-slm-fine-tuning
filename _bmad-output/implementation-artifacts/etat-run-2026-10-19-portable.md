# État du run, portable, nuit du 18 au 19 octobre 2026

Point de reprise après `/clear`. Il fait suite à `etat-run-2026-10-18-portable.md`. Nuit menée en autonomie, sur consigne d'Anaël : avancer seul sur tout ce qui ne dépend pas de lui. Un blocage ne suspend que ses suites.

## Décisions d'Anaël du 18 au soir (consignées dans decisions.md et budgets.toml)
- **Règle d'abandon des hybrides** : un hybride beaucoup plus lent que son équivalent dense, sans gain de qualité, est abandonné. Appliquée aux **Granite H** : plus de bench ni de mesure. La mesure de Granite H 350M n'est pas refaite.
- **Fine-tuning de la nuit** : campagne complète sur MiniCPM5-2B, puis Granite 4.0 1B si le temps le permet.
- **Budget** : campagne `finetune-minicpm5-2b-2026-10-19`. Anthropic dispose de 15,09 € (3,09 € reportés + 12 €) pour noter les runs de MiniCPM5-2B. Granite 1B est entraîné sans être noté.

## Fait cette nuit (main)
- Benchs GGUF des Granite et sonde EuroLLM commités. Les runs ratés et 9 worktrees fusionnés sont supprimés, avec l'accord d'Anaël. Graphique de Pareto rafraîchi avec les Granite (https://claude.ai/artifact/JaoY5EntJqPKKeqFk5Grwh).
- Sonde precision_base de minicpm5-2b : bf16 tient 8192 (4,6 Gio), fp32-kbit déborde dès 4096.
- Validation à 100 pas, 2048 tokens : bf16 et fp32-kbit ont la même perte à moins de 1 % près. La campagne part en bf16 à 8192.
- **Story C** fusionnée : `config/runs/m1…m4-minicpm5-2b.toml` et `m1…m4-granite-4.0-1b-v2.toml`.
- **Story B1** fusionnée : extra `gdn`, contrôle du chemin rapide, uv passé en 0.13.1. **Story B2** fusionnée : Qwen3.5 entraînables, vision gelée, option de fiche `bloc_amorce_historique`. Correctif de `data build --preferences` fusionné : une requête plus longue que le contexte est écartée avec le motif `contexte`.
- Suite complète verte sur main après ces fusions : 5 217 tests passés.
- Sondes : le LoRA (M2) de minicpm5-2b déborde dès 4096, il est donc **retiré de la campagne**. granite-4.0-1b déborde dès 4096, en QLoRA bf16 comme en LoRA.
- **M1** de minicpm5-2b terminé : `runs/train/20261019-000939-m1-qlora-minicpm5-2b-4423`, en 40 min.

## En cours
Voir la section « Journal de la nuit » ci-dessous, tenue à jour.

## Reste à faire
- L'extra `gdn` n'est **pas encore installé** dans le venv. Il le sera après la campagne MiniCPM5-2B : triton pourrait changer le chemin de bitsandbytes ou d'accelerate, et fausser la comparaison entre M1, M3 et M4. Commande : `uv sync --extra data --extra judge --extra bench --extra train --extra gdn --extra app`. Viendront ensuite les mesures GPU de B1 et B2 : `train sonde-env --modele qwen3.5-2b --precision-base bf16 --longueurs 2048,4096,8192`, la même pour 0.8b, puis un court `train run` SFT.
- Story B3 (export multimodal) : voir le journal.
- Mesures CPU du décodage spéculatif. Elles attendent que le GPU et le CPU soient libres.
- Granite 1B : retenir la plus grande longueur qui tient, entre 2048 et 4096 (sonder 3072), puis ajuster `m*-granite-4.0-1b-v2.toml`.
- Points restés ouverts au fichier du 18 : story de cache lm_eval, 9.8, `verifie_le` des licences, micro_lot, bug json-generique, v0.2.0.
- Arrêter le bloqueur de veille une fois le GPU et les mesures terminés.

## Résultat principal : le fine-tuning dégrade MiniCPM5-2B (à arbitrer par Anaël)
| Tâche | Baseline | M1 QLoRA | M3 DoRA |
|---|---|---|---|
| Q | 5,0 | 0,0 | 0,0 |
| RD | 75,1 | 83,5 | 83,6 |
| CR | 50,1 | 24,5 | 18,2 |
| LC | 24,0 | 0,0 | 0,0 |
| CO | 58,9 | 70,7 | 66,3 |
| RE | 35,5 | 42,8 | 32,6 |
| CT | 50,0 | 40,0 | 36,7 |
| NR | 30,0 | 23,3 | 16,7 |
| **Qualité** | **41,1** | **35,6** | **31,8** |

Notations : `runs/eval-notation/20261019-040548-ft-minicpm5-2b-1d82` (M1, 2,98 €) et `…-050830-…-fa99` (M3, 2,91 €). **Cause probable : le style du générateur dans le jeu v2.**
- 65 réponses LC sur 69 commencent par « Voici », comme 59 Q sur 92 et 59 RD sur 91. M1 en reprend le préambule en gras (16 sorties LC sur 25) et paraphrase les termes : sa fidélité tombe à 0.
- Les réponses CR du jeu ont une médiane de 5 285 caractères : M1 s'allonge, il est tronqué dans 22 sorties CR sur 25 (12 pour la Baseline) et il invente davantage (`sans_invention` passe de 40 % à 8 %). Les sorties sont plus longues dans presque toutes les tâches (CT : 723 contre 2 574 caractères).
- Q reste à 0 avant comme après : l'exactitude n'atteint jamais 2. Ce problème précède le fine-tuning.

Pistes, à décider par Anaël : filtrer les préambles et borner les longueurs au `max_tokens` de l'évaluation dans `data filter` ou `data build` ; contrôler la fidélité des cibles LC ; peut-être régénérer en partie (appel Mistral payant). **La notation de M4 est suspendue** jusqu'à son avis, puisque M4 part de M1. Elle coûterait environ 3 € et il reste environ 9,2 € au plafond.

## Journal de la nuit
- 01:10 : M3 (DoRA) lancé, puis export et notation de M1 (`scratchpad/nuit2.ps1`).
- 02:05 : M3 terminé (`runs/train/20261019-011031-m3-dora-minicpm5-2b-b9bb`, 55 min). L'export de M1 échoue : `convert_hf_to_gguf.py` importe `sentencepiece` sans condition. Corrigé : `sentencepiece` est ajouté à l'extra `train` et installé par `uv sync --inexact --no-install-project`, ce qui ne retire rien du venv.
- 02:07 à 03:00 : 410 paires ORPO dans `data/train/v3` (93 écartées : 77 `non_texte`, 14 `tronquee`, 2 `contexte`). `jeu_version` est un invariant de campagne : M4 part donc dans la campagne `minicpm5-2b-v2-orpo`, en v3. **Story à créer** pour aligner l'invariant sur les paires ORPO.
- B3 (export multimodal) et la story `bench cache-hf` sont fusionnées. La spec B est `done`. Les points `micro_lot` et json-generique sont reportés : le premier changerait la RAM mesurée avant les mesures spéculatives, le second ne touche plus qu'EuroLLM.
- 03:02 : M4 à 8192 tombe en OOM (deux séquences par pas). Les exports de M1 (`runs/export/20261019-030446-ft-minicpm5-2b-1752`) et de M3 (`…-030722-…-d543`) sont complets. Les notations ont échoué sur `--quantification` et `--jeu` manquants. Elles sont relancées en `q4_k_m`, jeu v1.1 (comme la Baseline), suivies de M4 à 4096 puis 2048 (`scratchpad/nuit5.ps1` et `nuit4.ps1`).
