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
- 2026-10-19 23:14 · essai lr · M1 MiniCPM5-2B sur v12 à lr 1e-4 lancé (`config/runs/m1-qlora-minicpm5-2b-v12-lr1e4.toml`) : test de l'hypothèse d'oubli · —
- 2026-10-19 23:41 · run · **blocked** puis levé · disque plein (11,7 Go libres sur 476, un export en demande 12) : export de la variante lr 1e-4 refusé. Supprimés (produits ratés, remplacés) : `runs/export/20261019-201400-ft-minicpm5-2b-35a0` (partiel-erreur, remplacé par ad30), `…-204454-ft-qwen3.5-2b-e730` (vide), `…-020558-ft-minicpm5-2b-4384` (partiel-erreur de la nuit précédente) → 23,8 Go libres. **Pour Anaël** : chaque export garde `hf-f16` et `modele-f16.gguf` (~9,4 Go d'intermédiaires) ; à purger pour les runs sous la Baseline si vous l'approuvez · —
- 2026-10-19 23:41 · essai lr · export, génération, notation de la variante lr 1e-4 relancés · —
- 2026-10-19 23:41 · S3 · juges tiers · premier essai coupé par mon `timeout` (25 min, 80 appels séquentiels) ; 12 runs relancés en parallèle (deepseek, glm × 3 Baselines + 3 M1 v11) · —
- 2026-10-19 23:41 · fix raisonnement · dev fini (66174d9), second avis 3 low, review lancée (Sonnet) · —
- 2026-10-19 23:48 · fix raisonnement · review (1 low corrigé, 1 rejeté) 0743932 ; fusion · bf239df
- 2026-10-19 23:56 · v13 · génération Large 3 `runs/data-generate/20261019-225253-generate-9ba4` arrêtée en partiel-budget (ancienne campagne, 2,36 €) : CR 77/80 (3 abandons), LC 80/80, CT 5/35 ; reprise (`--reprendre`) dans la campagne de nuit pour les 30 CT restants · —
- 2026-10-19 23:56 · v14 · génération **Mistral Large 4** lancée en parallèle (`runs/data-generate/20261019-234849-generate-4192`), correctif de raisonnement actif : premières sessions ok · —
- 2026-10-20 00:10 · v13 · génération complète (reprise 0,10 €) ; validation `runs/data-validate/20261019-235919-validate-1010` : 548/592 retenus (CR 77/77, CT 35/35, LC 67/80 : valeur_absente 11, url_inventee 2) ; filtre, build, nettoyage en cours · —
- 2026-10-20 00:10 · v14 · génération Large 4 arrêtée à minuit par le garde-fou des conditions Mistral (vérification du jour exigée). Page relue par le client `outillage` : **SHA-256 identique** à celui du 19 (08ee882d…) → `conditions_verifiees_le = 2026-10-20` (méthode consignée dans `donnees.toml`) ; reprise `--reprendre 20261019-234849-generate-4192` · —
- 2026-10-20 00:31 · essai lr · **variante lr 1e-4 notée** (`runs/eval-notation/20261020-002336-ft-minicpm5-2b-cadb`) : Q 0,0 · RD 84,4 · CR 32,2 · LC 0,0 · CO 71,5 · RE 34,9 · CT 40,0 · NR 20,0 → **35,4** (lr 2e-4 : 36,7). Le taux d'apprentissage ne change presque rien : l'hypothèse d'oubli par lr n'est pas confirmée. LC à 0 sur tous les fine-tunés, même sans donnée LC : analyse lancée · —
- 2026-10-20 00:32 · analyse LC (lookup) · le 0 vient de la **Fidélité** (fine-tuné sans LC : 19/25 à 0, aucune à 2 ; Baseline 10/9/6), pas du plafond Kandel-Moles (gains +0,34 et +0,95, tous deux plafonnés). Conditions modifiées (« peut » → « ne doit pas »), informations supprimées, conseils ou notes ajoutés. Le fine-tuning rend la réécriture plus libre même sans données LC. Kappa principal/second sur LC : 0,13 (fragile) · —
- 2026-10-20 00:32 · juges tiers · GLM-5.3 : 6 runs finis (~0,40 € chacun, 3 partiel-erreur). Baseline MiniCPM : accord avec le principal LC fidélité 60 % (κ 0,68, n=25), termes 96 % (κ 0,88), CT conformité 93 %, RE fidélité 33 % (κ 0,07) ; CR seulement 9 paires (items en échec à revoir). DeepSeek en cours · —
- 2026-10-20 00:50 · v13/v14 · jeu **v14** (Large 3, 548 lignes) = nettoyage de v13 (`runs/data-build/20261020-005006-build-dc48` → `…-005014-nettoyage-6fc8`). Contrôle : CR 77/77 avec les quatre sections, CT 35/35 avec emplacements (aucun ne commence par « Objet »), 32/35 avec formule de politesse ; médianes en mots CR 313, CT 205, LC 96. **Entraîné sans relecture d'Anaël** (autorisation de la nuit) · —
- 2026-10-20 00:50 · v14 · M1 MiniCPM5-2B lancé (`config/runs/m1-qlora-minicpm5-2b-v14.toml`, hyperparamètres du protocole) · —
- 2026-10-20 00:52 · Large 4 · reprise `20261019-234849-generate-4192` arrêtée : 7 ok, 8 abandons `reponse_tronquee`. Journal : le gabarit `cr` consomme 4 000 à 5 600 tokens de raisonnement pour un plafond de 5 600. Marge portée à 9 000 (36e97d2) ; nouveau run de génération Large 4 lancé · —
- 2026-10-20 00:52 · budget · campagne de nuit : anthropic 2,86 € / 18,5 ; mistral 0,91 € / 10 ; openrouter 4,32 € / 10 (DeepSeek plus cher que prévu, en cours) · —
- 2026-10-20 00:53 · Large 4 · abandons du nouveau run = sessions déjà tentées : **défaut** : la réutilisation des réponses journalisées ignore `max_tokens` et reprend des réponses tronquées (finish_reason=length) après un changement de marge. Les sessions nouvelles réussissent (cr : stop à 4 676 / 10 600). ~10 CR perdues. **Story à créer** : ne jamais réutiliser une réponse tronquée, inclure `max_tokens` dans la clé de réutilisation · —
- 2026-10-20 02:05 · v14 · M1 MiniCPM5-2B entraîné (`runs/train/20261020-005124-m1-qlora-minicpm5-2b-v14-fab9`), export `20261020-012603-ft-minicpm5-2b-f16a`, génération `20261020-012947-ft-minicpm5-2b-940d` ; notation en fond · —
- 2026-10-20 02:05 · disque · 7 Go libres : **intermédiaires supprimés** (`hf-f16`, `modele-f16.gguf`) des 5 exports de cette nuit notés sous leur Baseline (ad30, 1581, 0462, 3934, a5ad) ; Q4_K_M et runs d'entraînement gardés (régénération possible) → 45,8 Go libres. **Pour Anaël** : valider cette pratique ou la proscrire · —
- 2026-10-20 02:11 · v14 · **M1 MiniCPM5-2B v14 noté** (`runs/eval-notation/20261020-020503-ft-minicpm5-2b-2083`, ~2,8 €) : Q 1,7 · RD 83,2 · CR 33,9 · LC 0,0 · CO 74,1 · RE 31,9 · CT 46,7 · NR 16,7 → **36,0** (Baseline 41,1 ; v11 32,6 ; v12 partiel 36,7). Cibles conformes : CT 13,3 → 46,7, CR 21,7 → 33,9. LC reste à 0 (fidélité), NR baisse. Sous la Baseline : ni M3 ni M4 (règle de suite). Qwen3.5-2B v14 en entraînement (Baseline 36,0, la plus proche du seuil) · —
- 2026-10-20 02:11 · décision · piste d'architecture à proposer à Anaël : **adaptateur par tâche** (Baseline pour Q, CR, LC, CT, NR, RE ; adaptateur pour RD et CO). Estimation sur les scores mesurés : (5,0 + 85,6 + 50,1 + 24,0 + 81,2 + 35,5 + 50,0 + 30,0) / 8 ≈ **45,2** > 41,1 · —
