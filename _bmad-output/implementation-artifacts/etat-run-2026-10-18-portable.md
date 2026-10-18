# État du run, portable, 2026-10-18 (fin de journée)

Point de reprise après `/clear`. Il fait suite à `etat-run-2026-10-17-portable.md` (nuit du 17 au 18). Portable : 32 Go de RAM, RTX 3060 Laptop 6 Go. main est à jour et poussé.

## Décisions d'Anaël du 2026-10-18 (consignées dans decisions.md)
- **Méthode** : la qualité (Baseline, benchmarks) se mesure sur GPU (`--variante cuda`, `bench --variante-llamacpp cuda --parallele 4`), et la charge sur CPU (`measure run`). Le verrou GPU reste tenu pendant tout un bench (AD-27), ce qui est voulu.
- **Règle de taille relevée à 2,5B.** **MiniCPM5-2B** est candidat au fine-tuning et en tête de la Baseline.
- **EuroLLM-1.7B** passe en Baseline seulement : aucun protocole d'outils (R7 §4, option D).
- **R7 §0** : on normalise au build. Le jeu **data/train/v2** reprend v1, sauf le premier message des 91 lignes RD, mis en Mode connecté. Pour reconstruire `train.jsonl`, qui n'est pas suivi par git, lancer `data build` (voir spec-rd-connecte.md).
- **Granite H** (Mamba) est admis en Baseline (llama.cpp les sert sous Windows), `entrainable = false`. Granite 4.0 350M dense est entraînable.
- **Entraînement hors Windows natif** : accepté si l'inférence reste sous Windows. L'enquête montre que Windows natif suffit (triton-windows + fla).
- **Qwen3.5 entraînables**, avec la tour vision conservée, ce qui révise D8. La spec B est prête : `spec-qwen35-entrainable.md`, `ready-for-dev`, branche feat/qwen35-entrainable (commit 8fd5909). Décisions intégrées : sans fla, refus sauf `repli_torch` (4096 tokens au plus) ; ORPO multimodal refusé et reporté ; pas de mmproj de base épinglé ; ordre de CANDIDATS par qualité. Reste ouvert : `verifie_le` de la licence Apache-2.0 des Qwen3.5.
- **Écartés** : Gemma 4 E2B (trop gros) et Wyat-1-800M (pas de génération, licence non commerciale).
- **Budget** : campagne `baseline-2026-10-18c`, anthropic 10,09 € (reste 3,09 €). Les tests de budget lisent désormais `budgets.toml` : une nouvelle campagne ne demande plus de retoucher les tests.

## Intégré aujourd'hui (main)
- `bench run --parallele N`
- R7 : rendu des outils aligné sur llama-server, 205/205 sur granite, minicpm5-1b et minicpm5-2b
- data v2
- les trois petits Granite
- `precision_base` (`fp32-kbit` par défaut, `bf16` évite `prepare_model_for_kbit_training`) et `sonde-env --precision-base les-deux`
- décodage spéculatif mesurable : `measure run --speculatif {aucun,brouillon,ngram} --brouillon <slug>`, taux d'acceptation dans resultat.json, CPU seulement
- cache HF des jeux lm_eval rempli à la main (515 Mo), sans commande d'outillage : **story à créer**

Suite complète verte sur main avant les dernières fusions (5 099). Tests ciblés verts après.

## Baseline (jeu v1.1 ; mesures CPU du portable, contexte 4096, Q4_K_M)
| Modèle | Qualité /100 | tokens/s | RAM Go | Statut |
|---|---|---|---|---|
| **minicpm5-2b** | **41,1** | 16,7 | 3,88 | candidat choisi |
| qwen3.5-2b | 36,0 | 23,1 | 3,39 | Baseline seulement, entraînable après B |
| granite-4.0-1b | 33,4 | 14,6 | 3,88 | candidat |
| granite-4.0-h-1b | 32,5 | 26,4 | 3,88 | Baseline seulement (Mamba) |
| qwen3.5-0.8b | 27,5 | 43,3 | 2,26 | Baseline seulement |
| minicpm5-1b | 24,4 | 36,4 | 2,18 | candidat |
| eurollm-1.7b | 21,5 | 23,2 | 3,91 | Baseline seulement |
| granite-4.0-350m | 15,9 | 39,6 | 1,73 | candidat (trop faible) |
| granite-4.0-h-350m | 14,5 | mesure plantée, à refaire | — | Baseline seulement |

Qualité = moyenne des 8 Scores de Tâche. Graphiques de Pareto (privés) : https://claude.ai/artifact/JaoY5EntJqPKKeqFk5Grwh. Leurs données sont figées : à rafraîchir avec les Granite.

## Entraînement (enquête `enquete-entrainement-hybrides-2026-10-18.md`)
- MiniCPM5-2B, Windows natif, `precision_base = "bf16"` : 4096 tokens en 3,72 Gio (766 t/s), 8192 tokens en 4,69 Gio (596 t/s). Le fine-tuning à 8192 tokens tient sur le portable.
- Troncature du jeu v2 : 2048 garde 37 % de la supervision, 4096 en garde 86 %, 8192 en garde 100 %.
- Unsloth refuse minicpm5-2b (« untrained tokens »), et ce n'est plus nécessaire.

## En cours au moment du /clear
- **Benchmarks des trois Granite** (GGUF cuda `--parallele 4`, puis HF) : tâche de fond lancée par `scratchpad/suite`, script `reprise_h350m.ps1`, qui tient `gpu.lock`. Le script se termine par `=== fin`. Ensuite, commiter les runs `runs/bench/2026101818*` et suivants.
- **Bloqueur de veille** actif (processus PowerShell). L'arrêter une fois le GPU libre et les mesures faites.

## À faire, dans l'ordre
1. Après les benchmarks des Granite (GPU libre) :
   - `slmsp train sonde-env --modele minicpm5-2b --precision-base les-deux --longueurs 2048,4096,8192` ;
   - puis un court run QLoRA bf16 de validation sur minicpm5-2b (une centaine de pas, comparé à fp32 à 2048) ;
   - mesures CPU du spéculatif : minicpm5-2b `aucun`, `--brouillon minicpm5-1b`, `--speculatif ngram`. Selon la revue, `ngram-simple` ne propose rien en CPU, essayer `ngram-mod` si besoin ;
   - refaire la mesure de granite-4.0-h-350m.
2. Story **C** : configs de la campagne minicpm5-2b (`config/runs/m1…m4`, jeu v2, `longueur_max = 8192`, `precision_base = "bf16"`). C'est mécanique, après le run de validation.
3. Story **B1** (spec prête) : extra `gdn`, triton-windows + fla, contrôle du chemin rapide. Partir de main. **`uv self update` d'abord** : le uv 0.11.7 du portable est plus ancien que celui qui a écrit `uv.lock`. Ensuite B2 (chargement multimodal, `entrainable = true`), puis B3 (export avec mmproj).
4. Story : commande d'outillage pour remplir le cache HF des jeux lm_eval (snapshot, `refs/main`, `load_dataset` aux révisions épinglées), ou l'inclure dans l'export d'état.
5. Point du matin du 17, encore ouvert :
   - 9.8, relecture de l'échantillon de 30 lignes ;
   - `verifie_le` des licences (EuroLLM, Qwen3.5, Granite 350M dans `publication.toml`) ;
   - micro_lot des passages à 1536, avec troncature de la requête (`recherche_index.py:45`) ;
   - bug json-generique de b11429.
6. v0.2.0 après la Baseline (release annotée, topic `status-bench`).

## Points d'environnement
- **Téléchargements** : venv séparé `C:\Users\Anael\dev\slmsp-venv-fetch` (extras de la phase 1). Lancer avec `$env:UV_PROJECT_ENVIRONMENT = "C:\Users\Anael\dev\slmsp-venv-fetch"; uv run --no-sync slmsp fetch modeles …`. Le venv principal reste en phase 2.
- **`eval run --reprendre`** enchaîne génération et notation par défaut (`--phase toutes`). Un item en erreur compte comme « déjà présent » et n'est pas rejoué. Granite H 350M a ainsi été noté deux fois (0,64 € de trop) ; le doublon `runs/eval-notation/20261018-182840-…-70ce` n'est pas suivi.
- **Runs ratés non suivis, à supprimer avec accord** : `runs/bench/20261018-0441*`, `0444*`, `0447*`, `0450*`, `0559*`, `1458*` (EuroLLM, partiel), `runs/measure/20261018-180957-h-ram-b59e`.
- **Worktrees fusionnés à retirer** sous `C:\Users\Anael\dev\slmsp-wt\` : hybrides-baseline, candidats-registre, masque-minicpm5, bench-parallele, outils-rendu, rd-connecte, granite-petits, precision-base, decodage-speculatif. Garder qwen35-entrainable : la spec B n'est pas fusionnée.
- **Cache HF des jeux lm_eval** : `models/.cache-hf`. `NLTK_DATA=data/cache/nltk_data` doit être défini pour les benchmarks.
