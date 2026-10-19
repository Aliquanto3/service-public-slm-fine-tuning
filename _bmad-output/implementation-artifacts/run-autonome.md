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
- 2026-10-19 21:57 · S5 · décision · nommage : le jeu régénéré par S5 sera **v13** (v12 = sous-ensemble de S2, sans régénération) ; la spec garde son nom `spec-s5-cibles-v12.md` · —
- 2026-10-19 22:00 · run · décision · **Anaël part dormir** : autorise à générer les jeux nécessaires, lancer entraînements et évaluations (exception à la relecture avant entraînement, pour cette nuit). Plafond ~10 € par tâche et par API, 30 € par API à l'échelle du projet. Objectif : améliorer les modèles avec les pratiques SOTA ; sans amélioration marquante, Anaël reprendra le fond (données d'abord).
## Plan de nuit
1. M1 test MiniCPM5-2B sur v12 (sans CR, CT, LC) : borne de ce que le fine-tuning apporte sans les tâches mal ciblées.
2. S3 fusionnée → nouvelle campagne de budget (après les notations en cours) → juges tiers (OpenRouter) sur CR, LC, CT, RE des 3 Baselines et 3 M1 v11.
3. S5 fusionnée → v13 : CR, CT, LC régénérés par Mistral Large 4 (gabarits alignés sur la grille), validés ; **sélection** par un juge tiers (pas le juge principal, pour ne pas sur-apprendre le juge de l'évaluation) si le coût le permet → M1 v13 MiniCPM5-2B, puis les deux Qwen si gain.
4. Variante d'hyperparamètres SOTA pour petit jeu (2 époques, lr 1e-4) si M1 v13 approche la Baseline.
5. Règle de suite inchangée : M3, M4, benchmarks et mesures CPU pour un modèle qui dépasse sa Baseline.
- 2026-10-19 22:12 · S3 · dev · fini (client OpenRouter générique `src/slmsp/fournisseurs/`, `eval juges-tiers --verifier | --depuis --juge`, 38 tests) · 5193f21
- 2026-10-19 22:12 · S3 · second-avis · 1 medium (verdict JSON enveloppé mis en cache invalide), 3 low ; review lancée (Opus) · —
- 2026-10-19 22:12 · S2 · M1 test MiniCPM5-2B v12 entraîné en 13 min (`runs/train/20261019-215640-m1-qlora-minicpm5-2b-v11-partiel-7a6e`) ; export et génération en cours · —
- 2026-10-19 22:18 · S3 · review · 1 medium (extraction JSON tolérante, sortie illisible rejouable), 3 low corrigés, 1 rejeté · c47cd49
- 2026-10-19 22:18 · S3 · fusion · tests ciblés verts (163) ; `--verifier` : clé OpenRouter présente · dae7bfc
- 2026-10-19 22:18 · S3 · décision · juges tiers **DeepSeek V4 Pro** (`deepseek/deepseek-v4-pro`, 0,38 / 0,77 $/Mtok) et **GLM-5.2** (`z-ai/glm-5.2`, 0,62 / 2,42 $/Mtok), tarifs majorés de 30 %. Estimation : ~0,3 € et ~0,8 € par run de 80 items. Nouvelle campagne de budget ouverte quand les notations en cours (Qwen3.5-0.8B, M1 test) seront finies · —
- 2026-10-19 22:20 · S5 · dev · fini (gabarits CR/CT/LC, validateur de structure, nettoyage v3, `--modele-generateur`, `--taches --completer-depuis` ; estimation ~1,8 € pour 275 appels Mistral Large 4) · 494da31
- 2026-10-19 22:20 · S5 · second-avis · lancé · —
- 2026-10-19 22:22 · S3 · décision · GLM-5.2 remplacé par **GLM-5.3** (phare, plus récent ; question d'Anaël) ; pas de recommandation de juge trouvée chez Artificial Analysis ; le choix final du juge tiers se fera sur l'accord avec l'audit humain d'Anaël · —
- 2026-10-19 22:23 · S5 · second-avis · 3 medium (préversion trop large, faux rejets CR « Décisions prises » et CT « Objet du courrier »), 3 low ; D1 sans défaut ; review lancée (Opus) · —
- 2026-10-19 22:28 · S2 · M1 test : génération complète `runs/eval-generation/20261019-221301-ft-minicpm5-2b-2758` (export `20261019-220936-ft-minicpm5-2b-3934`), notation en fond · —
- 2026-10-19 22:37 · S5 · review · 3 medium (préversion stricte, sections CR et objet CT tolérants), 3 low corrigés · 3b473e7
- 2026-10-19 22:37 · S5 · fusion · tests ciblés verts (170) · 75eec75
- 2026-10-19 22:37 · v13 · génération CR, CT, LC par `mistral-large-4` lancée (`--completer-depuis 20261019-180544-generate-bd87`), campagne de budget actuelle (reste génération 3,11 €) · —
- 2026-10-19 22:37 · run · suite complète de mi-parcours lancée (après S1, S2, S3, S5) · —
- 2026-10-19 22:50 · run · suite complète : 5 570 passés, 2 échecs (tests S3 qui supposaient un `juges.toml` sans juge tiers, cassés par la config DeepSeek/GLM) ; tests réalignés · —
- 2026-10-19 22:52 · v13 · **blocked** · `mistral-large-4` est un modèle de raisonnement : contenu en liste de blocs (`thinking`, `text`) non lu par le client (« réponse brute sans contenu ») et réponses coupées (`finish_reason=length`, 1 882 tokens de raisonnement sur 4 000). 12 sessions CR abandonnées (`runs/data-generate/20261019-223723-generate-1778`, arrêté), ~0,25 € perdus · —
- 2026-10-19 22:52 · v13 · décision · v13 généré avec **Mistral Large 3** (`mistral-large-latest`, chaîne éprouvée) et les nouveaux gabarits ; correctif client (lecture des blocs de raisonnement, plafond de tokens) en story à part pour un v14 sous Large 4 · —
- 2026-10-19 23:13 · S2 · **M1 test noté** (`runs/eval-notation/20261019-222828-ft-minicpm5-2b-2a0e`, 2,78 € réels ; second juge arrêté par le sous-poste mistral.juge) : Q 0,0 · RD 85,6 · CR 30,5 · LC 0,0 · CO 81,2 · RE 32,9 · CT 43,3 · NR 20,0 → **qualité 36,7** (Baseline 41,1 ; M1 v11 32,6). Constats : (1) sans données CT, CT remonte de 13,3 à 43,3 (Baseline 50) : les cibles CT v11 nuisaient ; (2) **LC tombe à 0 et CR à 30,5 sans aucune donnée LC ni CR** : le fine-tuning dégrade aussi les tâches absentes du jeu (oubli, dérive de style), pas seulement par de mauvaises cibles ; (3) gains nets en RD (+10,5) et CO (+22,3). Critère de gain non atteint (RD : meilleure Baseline 86,9). Piste SOTA retenue pour la suite : limiter l'oubli (taux d'apprentissage plus bas) et réentraîner avec des cibles CR, CT, LC conformes (v13) · —
