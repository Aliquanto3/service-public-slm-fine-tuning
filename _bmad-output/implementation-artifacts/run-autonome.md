# Run autonome du 20 octobre 2026 : méthodologie v2 (étage 1)

Décisions d'Anaël : `plan-methodo-2026-10-20.md` §7 bis (E1 à E6 autorisées, étages graduels, DeepSeek juge de sélection, budgets, purge des intermédiaires, jeu dev `relu-llm`, relecture avant entraînement levée sous condition de consigner). Stories : `../planning-artifacts/sprint-change-proposal-2026-10-20.md`. Consignes des sous-agents : `consignes-sous-agents-2026-10-20.md`.
Garde-fous : D1 ; v1.1 gelé, mesure finale une fois par configuration retenue ; aucun push ; appels payants lancés par l'orchestrateur seulement ; qualité sur GPU, charge sur CPU.
Budget : campagne `methodo-v2-2026-10-20` — anthropic 40,5 €, mistral 10 € (génération 8, juge 2), openrouter 13,5 €.

## Périmètre
| Périmètre | Epics | Note |
|---|---|---|
| Dans le run | Stories C1 à C9, O1 à O6 ; expériences E1, E5 | hors epics.md, specs dans `spec-<id>-*.md` |
| Hors run | O2, O3, C5, E2, E3, E4, E6 | étage 2, seulement si la base reste meilleure sur des tâches |

Au plus 3 stories en développement à la fois.

## Sprint 1 — correctifs et étage 1
| Vague | Stories en parallèle | Après |
|---|---|---|
| V0 | C1 · C2 · E1 (mixte) | |
| V1 | O1 ★ · C8 · O4 ★ | specs relues |
| V2 | O6 ★ · O5 | O6 ← O1 ; O6 ← C2 |
| V3 | C3 · C4 · C6 · C7 · C9 | GPU libre pour C3, C4 |
| V4 | génération vérifiée v17 (mixte) · M1 MiniCPM5-2B v17 (mixte) · gel jeu dev (mixte) | v17 ← O6, O5 ; M1 ← v17 |
| V5 | notation dev puis v1.1 · décision | |

## Journal
- 2026-10-20 · run · décision · campagne de budget `methodo-v2-2026-10-20` ouverte ; ancien run archivé (`archive/run-autonome-2026-10-19.md`) · cb49933
- 2026-10-20 · C1 · dev · lancé · —
- 2026-10-20 · C2 · dev · lancé · —
- 2026-10-20 · E1 · décision · le décodage d'évaluation est glouton (graine 42, température 0) : deux générations d'un même GGUF sont identiques. E1 = variance d'entraînement (M1 MiniCPM5-2B v14, graine 4321, noté) + bootstrap apparié des items sur les notations existantes · —
- 2026-10-20 · disque · **blocked** · 20 Go libres (96 %) ; la purge des intermédiaires des 7 exports déjà notés (~70 Go, autorisée au §7 bis) est refusée par le classifieur de permissions de Claude Code (« suppression irréversible »). **Pour Anaël** : autoriser la suppression ou la faire (liste : exports 20261020-032933, 012603, 023537, 044718 ; 20261019-090952, 030722, 030446 ; dossiers `hf-f16/` et `modele-f16.gguf`). Assez de place pour E1 ; C8 apportera la purge par l'outil · —
- 2026-10-20 06:42 · E1 · dev · lancé : bloqueur de veille actif, `campagne-run.ps1` (train → export cuda → génération q4_k_m v1.1 cuda → notation, plafond 4,5 €), run `runs/train/20261020-064228-m1-qlora-minicpm5-2b-v14-graine4321-a7d1` · —
- 2026-10-20 · C1 · dev · fini (4 tests lisent la config) · b71f669
- 2026-10-20 06:45 · C1 · second-avis · 1 medium (Retry-After > 300 s jamais attendu avec délai 600 et durée totale 900 : défaut de production), 6 low · —
- 2026-10-20 06:45 · C2 · dev · fini (tronquée jamais réutilisée, max_tokens comparé, ancien journal réutilisé si `stop`) · abc540d
- 2026-10-20 06:45 · O1, O3, O4, O6, C5 · décision · specs écrites, relecture avant code lancée (Opus) · —
- 2026-10-20 · C1 · review · medium corrigé (`duree_totale_max_appel` 900 → 1800), 3 low · 2e8222e
- 2026-10-20 · C1 · fusion · squash dans main · 6258ae7
- 2026-10-20 06:47 · C2 · second-avis · 1 high (`reponse_journalisee` du chemin seed CT sans filtre), 4 medium (`model_length` et finish_reason absent réutilisés, estimation de coût incohérente, test qui n'exerce pas le chemin réel) ; review lancée (Opus) · —
- 2026-10-20 06:47 · C8 · dev · lancé · —
- 2026-10-20 06:47 · O5 · dev · lancé · —
- 2026-10-20 06:47 · E1b · dev · lancé (outil de bootstrap apparié des scores, lecture seule) · —
- 2026-10-20 06:52 · C8 · dev · fini (`--purger-intermediaires`, `export purger` limité aux exports notés, contrôle d'espace `facteur_espace` 3) ; second-avis lancé · a46530e
- 2026-10-20 06:52 · E1b · dev · fini · bootstrap apparié v1.1 (2000 tirages) : Qualité Baseline MiniCPM 41,1, M1 v14 36,0 (écart −5,0, IC95 [−9,2 ; −1,2]), v15 35,7 (−5,4, [−9,3 ; −1,7]) ; bruit items d'un run seul ±2,6 à ±3,9. Les baisses sous la Baseline sont réelles ; v14 et v15 indiscernables ; second-avis lancé · 1376d5f
