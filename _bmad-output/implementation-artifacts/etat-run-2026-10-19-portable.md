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

## Journal de la nuit
- 01:10 : M3 (DoRA) lancé, puis export et notation de M1 (`scratchpad/nuit2.ps1`).
