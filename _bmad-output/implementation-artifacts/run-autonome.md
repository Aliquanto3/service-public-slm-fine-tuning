# Run autonome du 19 octobre 2026 au soir : audit des juges, 3e juge, jeu v12

Décisions d'Anaël (19/10, vers 21 h 40) : HTML d'audit des verdicts ; 3e juge d'une autre famille (OpenAI ou Google) **tout de suite**, en parallèle ; réécriture des données d'entraînement (CR, CT, LC) autorisée, Mistral Large 4 possible ; comparaison de modèles SOTA **comme générateurs v12** ; test d'entraînement sur une partie des tâches. Plafond : **10 € par nouveau fournisseur** (OpenAI, Google) pour l'ensemble de ces travaux. « Je t'autorise à lancer toutes les actions. »
Garde-fous inchangés : Claude ne génère jamais de données d'entraînement (D1) ; jeu d'évaluation v1.1 gelé ; l'entraînement sur un **nouveau** jeu (v12 régénéré) attend la relecture d'Anaël. Le M1 sur jeu partiel (sous-ensemble de v11, déjà relu) est autorisé.
Campagne v11 en cours en parallèle : `etat-campagne-v11.md`.

## Périmètre
| Périmètre | Epics | Note |
|---|---|---|
| Dans le run | Stories S1 à S5 | hors epics.md, specs dans ce fichier ou `spec-<story>.md` |

Au plus 3 stories en développement à la fois.

## Sprint 1 — audit et fiabilisation
| Vague | Stories en parallèle | Après |
|---|---|---|
| V0 | S1 audit-verdicts · S2 jeu-partiel | |
| V1 | S3 juge-tiers ★ · S5 cibles-v12 ★ | specs relues |
| V2 | S4 comparaison-generateurs | 4 ← 3 ; 4 ← 5 |

- S1 : HTML autonome de relecture des verdicts (juge principal, second juge, verdict humain exportable).
- S2 : `data build` d'un sous-ensemble de tâches d'un jeu SFT, puis M1 test (sans CR, CT, LC).
- S3 : client compatible OpenAI (OpenAI, Gemini), 3e juge, postes de budget `openai` et `google` à 10 €, renotation des Baselines et M1 v11.
- S5 : prompts de régénération CR / CT / LC alignés sur la grille (instructions seules, D1), validateur de structure au build, Mistral Large 4 autorisé.
- S4 : échantillon de cibles CR / CT / LC par Mistral Large 4, GPT, Gemini ; comparaison à l'aveugle dans un HTML.

## Journal
- 2026-10-19 21:40 · run · décision · périmètre et plafonds d'Anaël (ci-dessus) · —
- 2026-10-19 21:40 · S1 · dev · lancé · —
- 2026-10-19 21:40 · S2 · dev · lancé · —
- 2026-10-19 21:47 · S2 · dev · fini (jeu v12 = v11 sans CR, CT, LC : 369 lignes attendues) · 30f861c
- 2026-10-19 21:47 · S2 · second-avis · lancé · —
- 2026-10-19 21:47 · S3, S5 · décision · specs écrites (`spec-s3-juges-tiers.md`, `spec-s5-cibles-v12.md`), relecture avant code lancée · —
- 2026-10-19 21:50 · S1 · dev · fini (HTML 170 items, 110 désaccords) · 4260aba
- 2026-10-19 21:50 · S1 · second-avis · 5 medium, 6 low ; review lancée (Sonnet) · —
- 2026-10-19 21:50 · S2 · second-avis · 2 medium, 5 low ; review lancée (Opus) · —
- 2026-10-19 21:50 · S3, S5 · décision · relecture des specs : 3 high (schéma juges extra=forbid, nouvelle campagne de budget obligatoire, modèle Mistral partagé avec le second juge), 12 medium/low ; specs révisées (224c51d). Constat : kappa « 0,00 » calculé sur 3 à 5 items par tâche, non interprétable → juges tiers sur tous les items CR, LC, CT, RE · 224c51d
- 2026-10-19 21:50 · S3 · dev · lancé (Opus) · —
- 2026-10-19 21:50 · S5 · dev · lancé (Opus) · —
- 2026-10-19 21:53 · run · décision · Anaël : clé OpenRouter disponible, recommandations validées (générateurs v12 : Mistral Large 4 en référence, DeepSeek V4 Pro et GLM-5.x via OpenRouter ; GPT et Gemini en comparaison seulement, licence à trancher par Anaël), budgets Mistral et OpenRouter rechargés. Plafonds retenus : openai 10 €, google 10 €, openrouter 10 €, mistral.generation 10 € · —
- 2026-10-19 21:53 · S3 · décision · fournisseur openrouter ajouté au périmètre (message à l'agent) · —
- 2026-10-19 21:54 · S1 · review · 10 constats corrigés, tests JS rejetés · 6223c0b
- 2026-10-19 21:54 · S1 · fusion · HTML `C:\Users\Anael\dev\slmsp-auditudit-verdicts.html` (170 items, 110 désaccords) · 0032eba
- 2026-10-19 21:54 · S1 · review · 10 constats corrigés, tests JS rejetés · 6223c0b
- 2026-10-19 21:54 · S1 · fusion · HTML `C:/Users/Anael/dev/slmsp-audit/audit-verdicts.html` (170 items, 110 désaccords, 5 notations) · 65763d2
- 2026-10-19 21:55 · run · décision · Anaël : **GPT et Gemini retirés** (générateurs et juges), risque de licence non instruit. Fournisseur unique pour S3 et S4 : OpenRouter (DeepSeek, GLM, Kimi…), plus Mistral (Large 4 et Large 3). Plafonds : openrouter 10 €, mistral.generation 10 € · —
- 2026-10-19 21:56 · S2 · review · 2 medium (nettoyage depuis un sous-ensemble refusé ; préférences testées), 5 low corrigés · e7613e7
- 2026-10-19 21:56 · S2 · fusion · tests ciblés verts (93) · 2aff428
- 2026-10-19 21:56 · S2 · décision · jeu **v12** = v11 sans CR, CT, LC (369 lignes : CO 34, Q 95, RD 132, RE 34, generique 74), `runs/data-build/20261019-215607-sous-ensemble-bfcf` ; M1 test MiniCPM5-2B lancé (`config/runs/m1-qlora-minicpm5-2b-v11-partiel.toml`, autorisé par Anaël) · —
