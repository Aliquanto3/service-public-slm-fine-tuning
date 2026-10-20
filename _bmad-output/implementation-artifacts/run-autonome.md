# Run autonome du 20 octobre 2026 : méthodologie v2 (étage 1)

Décisions d'Anaël : `plan-methodo-2026-10-20.md` §7 bis (E1 à E6 autorisées, étages graduels, DeepSeek juge de sélection, budgets, purge des intermédiaires, jeu dev `relu-llm`, relecture avant entraînement levée sous condition de consigner). Stories : `../planning-artifacts/sprint-change-proposal-2026-10-20.md`. Consignes des sous-agents : `consignes-sous-agents-2026-10-20.md`.
Garde-fous : D1 ; v1.1 gelé, mesure finale une fois par configuration retenue ; aucun push ; appels payants lancés par l'orchestrateur seulement ; qualité sur GPU, charge sur CPU.
Budget : campagne `methodo-v2-2026-10-20` — anthropic 40,5 €, mistral 10 € (génération 8, juge 2), openrouter 13,5 €.

## Périmètre
| Périmètre | Epics | Note |
|---|---|---|
| Dans le run | Epics 14 à 14 | méthodologie v2 : 14.1-14.9 = C1-C9 (sans C5), 14.10 O1, 14.11 O4a, 14.12 O4b, 14.13 O5, 14.14 O6a, 14.15 O6b, 14.16 E1, 14.17 jeu v17 + M1, 14.18 E5 |
| Hors run | O2, O3, C5, E2, E3, E4, E6 (non numérotées) | étage 2, seulement si la base reste meilleure sur des tâches |

Au plus 3 stories en développement à la fois.

## Sprint 1 — correctifs et étage 1
| Vague | Stories en parallèle | Après |
|---|---|---|
| V0 | 14.1 · 14.2 · 14.16 | |
| V1 | 14.10 ★ · 14.8 · 14.11 ★ · 14.13 · 14.6 · 14.9 · 14.7 | specs relues |
| V2 | 14.14 ★ · 14.12 | 14.14 ← 14.10 ; 14.12 ← 14.11 |
| V3 | 14.15 ★ · 14.3 · 14.4 | 14.15 ← 14.14 |
| V4 | 14.17 | 14.17 ← 14.15 ; 14.17 ← 14.13 |
| V5 | 14.18 | 14.18 ← 14.12 ; 14.18 ← 14.17 |

## Journal
- 2026-10-20 · run · décision · campagne de budget `methodo-v2-2026-10-20` ouverte ; ancien run archivé (`archive/run-autonome-2026-10-19.md`) · cb49933
- 2026-10-20 · 14.1 (C1) · dev · lancé · —
- 2026-10-20 · 14.2 (C2) · dev · lancé · —
- 2026-10-20 · 14.16 (E1) · décision · le décodage d'évaluation est glouton (graine 42, température 0) : deux générations d'un même GGUF sont identiques. E1 = variance d'entraînement (M1 MiniCPM5-2B v14, graine 4321, noté) + bootstrap apparié des items sur les notations existantes · —
- 2026-10-20 · disque · **blocked** · 20 Go libres (96 %) ; la purge des intermédiaires des 7 exports déjà notés (~70 Go, autorisée au §7 bis) est refusée par le classifieur de permissions de Claude Code (« suppression irréversible »). **Pour Anaël** : autoriser la suppression ou la faire (liste : exports 20261020-032933, 012603, 023537, 044718 ; 20261019-090952, 030722, 030446 ; dossiers `hf-f16/` et `modele-f16.gguf`). Assez de place pour E1 ; C8 apportera la purge par l'outil · —
- 2026-10-20 06:42 · 14.16 (E1) · dev · lancé : bloqueur de veille actif, `campagne-run.ps1` (train → export cuda → génération q4_k_m v1.1 cuda → notation, plafond 4,5 €), run `runs/train/20261020-064228-m1-qlora-minicpm5-2b-v14-graine4321-a7d1` · —
- 2026-10-20 · 14.1 (C1) · dev · fini (4 tests lisent la config) · b71f669
- 2026-10-20 06:45 · 14.1 (C1) · second-avis · 1 medium (Retry-After > 300 s jamais attendu avec délai 600 et durée totale 900 : défaut de production), 6 low · —
- 2026-10-20 06:45 · 14.2 (C2) · dev · fini (tronquée jamais réutilisée, max_tokens comparé, ancien journal réutilisé si `stop`) · abc540d
- 2026-10-20 06:45 · 14.10 (O1), O3, O4, O6, C5 · décision · specs écrites, relecture avant code lancée (Opus) · —
- 2026-10-20 · 14.1 (C1) · review · medium corrigé (`duree_totale_max_appel` 900 → 1800), 3 low · 2e8222e
- 2026-10-20 · 14.1 (C1) · fusion · squash dans main · 6258ae7
- 2026-10-20 06:47 · 14.2 (C2) · second-avis · 1 high (`reponse_journalisee` du chemin seed CT sans filtre), 4 medium (`model_length` et finish_reason absent réutilisés, estimation de coût incohérente, test qui n'exerce pas le chemin réel) ; review lancée (Opus) · —
- 2026-10-20 06:47 · 14.8 (C8) · dev · lancé · —
- 2026-10-20 06:47 · 14.13 (O5) · dev · lancé · —
- 2026-10-20 06:47 · 14.16 (E1b) · dev · lancé (outil de bootstrap apparié des scores, lecture seule) · —
- 2026-10-20 06:52 · 14.8 (C8) · dev · fini (`--purger-intermediaires`, `export purger` limité aux exports notés, contrôle d'espace `facteur_espace` 3) ; second-avis lancé · a46530e
- 2026-10-20 06:52 · 14.16 (E1b) · dev · fini · bootstrap apparié v1.1 (2000 tirages) : Qualité Baseline MiniCPM 41,1, M1 v14 36,0 (écart −5,0, IC95 [−9,2 ; −1,2]), v15 35,7 (−5,4, [−9,3 ; −1,7]) ; bruit items d'un run seul ±2,6 à ±3,9. Les baisses sous la Baseline sont réelles ; v14 et v15 indiscernables ; second-avis lancé · 1376d5f
- 2026-10-20 06:57 · 14.2 (C2) · review · 1 high et 4 medium corrigés (règle unique `reponse_reutilisable` : stop/tool_calls seulement, même max_tokens ; `model_length` traité comme tronqué ; estimation de coût alignée) · 3aa3bfd
- 2026-10-20 06:57 · 14.2 (C2) · fusion · squash dans main ; tests data, mistral, cli : 874 passés · 90c565e
- 2026-10-20 06:57 · 14.16 (E1b) · review · 3 medium corrigés (tâches absentes ou None signalées, tirages comptés) ; chiffres réels inchangés · 25d2d59
- 2026-10-20 06:57 · 14.16 (E1b) · fusion · squash dans main · 81c2c37
- 2026-10-20 06:57 · 14.13 (O5) · dev · fini · médianes d'entrée v1.1 / v14 : LC 278 / 108, CO 153 / 84, RE 714 / 202, CR 1205 / 1544, CT 64 / 135 ; consignes d'Agent génériques étendues à CR, CT, RE, CO ; filtre LC 195-361 mots au seed ; second-avis lancé · 6696c2b
- 2026-10-20 06:57 · 14.10 (O1), O3, O4, O6, C5 · décision · specs relues (O1 2 high, O6 3 high, O4 2 high, O3 2 high, C5 1 high ; tous intégrés). O6 découpée en O6a (vérification) puis O6b (régénération) ; jeu dev nommé `dev1`. **Pour Anaël** : (1) juge du jeu dev = GLM-5.3 par défaut au lieu de DeepSeek (DeepSeek sélectionne déjà les données : biais) ; (2) étage 2 : usage au Registre des sorties des Modèles de base comme cibles · 68a5bc5
- 2026-10-20 06:57 · 14.10 (O1) · dev · lancé (Opus) · —
- 2026-10-20 06:57 · 14.11 (O4a) · dev · lancé · —
- 2026-10-20 07:01 · 14.13 (O5) · second-avis · 3 medium (consignes génériques proches de consignes v1.1 : risque de fuite ; rendement du filtre LC ~11 % ; filtre jamais testé en chemin réel), 3 low ; review lancée (Opus) · —
- 2026-10-20 07:01 · 14.8 (C8) · review · 1 high (notation non complète comptée comme notée), 4 medium corrigés ; `--purger-intermediaires` retiré (purgeait sans notation) : purge seulement par `export purger --tous-notes` après notation · b519cbb
- 2026-10-20 07:01 · 14.8 (C8) · fusion · squash dans main · 8d77bb4
- 2026-10-20 07:01 · disque · **débloqué** : `slmsp export purger --tous-notes` (outil C8, notations complètes seulement) : 7 exports, 57,6 Gio libérés ; 78 Go libres · —
- 2026-10-20 07:03 · 14.6 (C6) · dev · fini : aucun défaut dans src/ (les coûts de session viennent déjà du run) ; le défaut était dans `scripts-campagne/campagne-run.ps1` (différence du registre) : coût lu dans `scores.json` du run de notation, registre en repli · voir branche feat/scripts-campagne
- 2026-10-20 07:03 · 14.6 (C6) · fini : aucun défaut dans src/ (coûts de session déjà propres au run) ; défaut dans le script hors dépôt `slmsp-wt/scripts-campagne/campagne-run.ps1` (différence du registre) : coût lu dans `scores.json` du run de notation, registre en repli · —
- 2026-10-20 07:09 · 14.9 (C9) · dev, second-avis (5 low), review (1 high : test des préalables cassé ; 4 medium : journal sous SLMSP_VAR_DIR, regex bornée à [mistral], écriture atomique, TOML illisible bloque) · fusion · e0af7e2
- 2026-10-20 07:12 · 14.13 (O5) · review · consignes reformulées (ressemblance max 0,48 avec une consigne du Jeu, test anti-fuite à 0,6) ; filtre LC suffisant (5 253 textes uniques de 195-361 mots dans service-public : un nouveau seed LC suffit) ; **Pour Anaël** : confirmer les formulations des consignes génériques · ea9d9a1
- 2026-10-20 07:12 · 14.13 (O5) · fusion · squash dans main · b90d45c
- 2026-10-20 07:12 · 14.10 (O1) · dev · fini (`data juger`, bibliothèque `JugeDonnees.juger_candidat`, grilles `config/prompts/juge-donnees/{cr,lc,ct}.md`, ~0,005 € par candidat) ; second-avis lancé · 5e20cb2
- 2026-10-20 07:13 · 14.16 (E1) · train fini (07:06), export `20261020-070658-ft-minicpm5-2b-5606` (07:08) ; génération et notation en cours · —
- 2026-10-20 07:13 · 14.11 (O4a) · dev · fini (dev1, relu-llm, juge par jeu glm, refus au Comparatif) ; second-avis lancé · d763d82
- 2026-10-20 07:13 · 14.7 (C7) · dev · lancé (diagnostic sans appel payant) · —
- 2026-10-20 07:16 · 14.6 (C6) · fusion · correctif dans le script de campagne hors dépôt, rien à fusionner · —
- 2026-10-20 07:16 · 14.9 (C9) · fusion · squash dans main · e0af7e2
- 2026-10-20 07:16 · 14.11 (O4a) · décision · Anaël : GLM-5.3 juge du jeu de développement (confirmé) · —
- 2026-10-20 07:16 · run · décision · suivi aligné sur avancement-run : stories du run numérotées en epic 14 dans sprint-status.yaml · —
- 2026-10-20 07:17 · 14.10 (O1) · second-avis · 3 medium (fusion superficielle des seuils, couverture 1,0 si le juge omet tout, injection possible sans délimiteurs), 5 low ; review lancée (Opus) · —
- 2026-10-20 07:17 · 14.11 (O4a) · second-avis · 5 medium (URL des Q et amorces seed absentes de la disjonction, --jeu incohérent à la reprise, eval comparer entre juges différents, verdicts sans empreinte d'item), 4 low ; review lancée (Opus) · —
- 2026-10-20 07:20 · 14.7 (C7) · dev · fini : causes = références d'éléments manquantes (schéma sans minItems ; GLM 105 listes vides) et sorties DeepSeek coupées à 8000 tokens (raisonnement 7 500-8 000 même en effort low) ; relance corrective, max_tokens deepseek 16000, `--rejouer-invalides` ; rejeu estimé ~2 € ; second-avis lancé · bfba6e5
- 2026-10-20 07:20 · run · décision · Anaël : amélioration continue ; branche `feat/avancement-run-ids-hors-epics` ouverte sur agent-cost-kit (clone `~/dev/agent-cost-kit`, rien poussé) · —
- 2026-10-20 07:22 · 14.7 (C7) · second-avis · 2 medium (archivage d'un invalide avant le test d'arrêt ou de budget ; estimation à un appel par item malgré la relance corrective), 2 low ; review lancée (Sonnet) · —
- 2026-10-20 07:28 · 14.11 (O4a) · review · 5 medium corrigés (disjonction avec URL des Q et amorces seed, --jeu cohérent à la reprise, eval comparer refuse jeux ou juges différents, verdicts croisés avec empreinte d'item) · ec11d98
- 2026-10-20 07:28 · 14.11 (O4a) · fusion · squash dans main ; tests evaluation, eval_outils, compare, judge : 1 463 passés · 30e47ed
- 2026-10-20 07:28 · 14.10 (O1) · review · 5 medium corrigés (seuils fusionnés par critère, couverture non évaluable = refus, balises anti-injection, max_tokens 16000, relance corrective), 6 low · dcd48be
- 2026-10-20 07:28 · 14.10 (O1) · fusion · squash dans main · 9afcc9c
- 2026-10-20 07:28 · 14.7 (C7) · review · 2 medium corrigés (archivage après réponse exploitable seulement, pire cas à 2 appels par item) · f5309a6
- 2026-10-20 07:28 · 14.7 (C7) · fusion · squash dans main (conflit avec O1 résolu : `extraire_json` déplacé dans fournisseurs/lecture) ; tests judge, juges tiers, juge de données, fournisseurs, cli : 291 passés · a25242c
- 2026-10-20 07:28 · 14.16 (E1) · génération finie (`runs/eval-generation/20261020-070903-ft-minicpm5-2b-5a5f`, 225 ok) ; notation en cours (`20261020-072634-ft-minicpm5-2b-6664`) · —
- 2026-10-20 07:28 · 14.10 (O1) · calibrage payant lancé : `data juger --depuis 20261019-225253-generate-9ba4 --limite 10 --plafond-estime 1.5` (~0,34 €) · —
- 2026-10-20 07:28 · 14.14 (O6a) · dev · lancé (Opus) · —
- 2026-10-20 07:28 · 14.12 (O4b) · dev · lancé (Opus, construction de dev1, sans appel payant) · —
- 2026-10-20 07:28 · 14.4 (C4) · dev · lancé (essais GPU courts autorisés) · —
- 2026-10-20 07:30 · run · décision · agent-cost-kit : branche `feat/avancement-run-ids-hors-epics` revue (second-avis 3 medium, review corrigée, 77 tests) et poussée ; PR à ouvrir sur accord d'Anaël · 3d6300a
- 2026-10-20 07:55 · 14.4 (C4) · dev · fini : cause = TRL 1.13 ne borne pas la longueur en ORPO (177/505 paires v16 > 2048 jetons, logits du vocabulaire Qwen3.5 248k) → débordement VRAM en mémoire partagée WDDM puis « device not ready » ; correctif : paires trop longues écartées (328/505 gardées) ; 5 pas prouvés ; second-avis lancé · 6914e7e
- 2026-10-20 07:55 · 14.14 (O6a) · dev · fini ; calibrage gratuit sur v14 : CR 0/77 écartés, CT 0/35, LC 61/80 (gain de lisibilité 47, modalité perdue 17, valeur absente 13, URL inventée 2) ; second-avis lancé · 491abf2
- 2026-10-20 07:55 · 14.14 (O6a) · décision · contrôle du gain de lisibilité LC gardé **bloquant** (la grille plafonne LC sans gain Kandel-Moles ; la régénération O6b recevra ce motif) ; réversible par config · —
- 2026-10-20 07:57 · 14.4 (C4) · second-avis · 3 medium (reprise silencieuse d'un run d'avant le correctif, filtre absent des invariants de campagne, diagnostic qui surévalue le correctif : débordement en mémoire partagée persistant), 3 low ; review lancée · —
- 2026-10-20 07:57 · 14.3 (C3) · dev · lancé (essais de fusion réels gratuits autorisés) · —
- 2026-10-20 08:00 · 14.10 (O1) · calibrage réel `runs/data-juger/20261020-072807-juger-85c1` (partiel-erreur, 0,11 €) : CR 8/10 acceptés (couverture 80 %, invention 90 %, structure 100 %), 29 extraits invalides ; **lenteur** : 11 appels en 31 min (~2,8 min par appel, raisonnement DeepSeek), puis ReadTimeout au délai de lecture par défaut (300 s) ; LC et CT non jugés. Suite : délai de lecture 900 s et appels parallèles à ajouter (revue O6a), sinon ~9 h pour 192 candidats · —
- 2026-10-20 08:01 · 14.4 (C4) · review · 2 medium corrigés (filtre dans la config résolue ORPO : reprise d'un run d'avant le correctif refusée ; diagnostic reformulé), 1 rejeté (invariants de campagne) · 807554f
- 2026-10-20 08:01 · 14.4 (C4) · fusion · squash dans main · 060a4f6
- 2026-10-20 08:02 · 14.14 (O6a) · second-avis · 1 high (`--completer-depuis` recopie des CR/LC/CT non vérifiées), 2 medium (pire cas OpenRouter ×2, motif « Signature » CT), 4 low ; review lancée (Opus) avec délais 900 s et appels parallèles pour DeepSeek · —
- 2026-10-20 08:03 · 14.3 (C3) · dev · fini : cause = 14 lignes nulles de in_proj_qkv dans la base bf16 → norme DoRA nulle → NaN ; correctif `norme_dora_sure` ; export réel du M3 DoRA Qwen3.5-0.8B réussi (`runs/export/20261020-075847-ft-qwen3.5-0.8b-e69a`) ; second-avis lancé · 810a911
- 2026-10-20 08:05 · 14.3 (C3) · second-avis · maths de la garde justes (norme sur W+ΔW, lora_B nul sur les 14 lignes) ; 2 points medium : à l'entraînement la base est nf4 (Q(W) peut être non nul → fusion bf16 divergente), test sans comparaison au forward ; review lancée (Opus, mesure sur le vrai modèle) · —
- 2026-10-20 08:11 · 14.3 (C3) · review · mesure : en nf4 les 14 lignes mortes ont une norme 0,0015-0,031 et lora_B y est nul, magnitude inchangée → fusion à 0 correcte, export e69a valable ; test de comparaison au forward ajouté · eae9481
- 2026-10-20 08:11 · 14.3 (C3) · fusion · squash dans main · cfa04ee
- 2026-10-20 08:12 · run · décision · Anaël (absent toute la journée, autonomie) : budget Anthropic relevé à 60 € à l'échelle du projet, OpenRouter à 50 $ (~46 €). Nouvelle campagne de budget à ouvrir dès qu'aucun lot n'est ouvert (notation E1 en cours) : plafonds = enveloppe − dépensé de la campagne methodo-v2 · —
- 2026-10-20 08:12 · 14.7 (C7) · rejeu de contrôle lancé : juges tiers glm puis deepseek, CR, Baseline MiniCPM (`20261018-112201-minicpm5-2b-e6f2`), `--rejouer-invalides`, plafond 1 € chacun · —
- 2026-10-20 08:29 · 14.14 (O6a) · review · 3 high corrigés (`--completer-depuis` refusé en mode vérifié pour CR/LC/CT, délais 900 s, 8 appels parallèles avec écriture ordonnée), 1 medium, 3 low · 9cf8944
- 2026-10-20 08:29 · 14.14 (O6a) · fusion · squash dans main ; tests data, budget, fournisseurs, cli data : 774 passés · e847667
- 2026-10-20 08:29 · 14.17 (V17) · calibrage gratuit sur le seed b335 + cibles v14 (`runs/data-generate/20261020-082601-generate-6eff`, 0,10 € Mistral pour 3 CR non réutilisables) : CR 80/80, CT 35/35, LC 19/80 retenues (gain de lisibilité 47, modalité perdue 17, valeur absente 13, URL inventée 2) · —
- 2026-10-20 08:29 · 14.17 (V17) · vérification payante lancée (juge DeepSeek, 8 appels parallèles, plafond OpenRouter 9 €, Mistral 0,5 €) · —
- 2026-10-20 08:31 · 14.16 (E1) · fini : M1 MiniCPM5-2B v14 graine 4321 noté (`runs/eval-notation/20261020-072634-ft-minicpm5-2b-6664`, 2,78 €) : Q 0,0 · RD 86,2 · CR 29,1 · LC 0,0 · CO 77,4 · RE 29,8 · CT 46,7 · NR 20,0 → **36,2** (graine 1234 : 36,0). Bootstrap apparié (`e1-variance.md`) : écart entre graines +0,1, IC95 [−2,5 ; +2,6] ; par tâche jusqu'à ±5 (CR −4,8, CO +3,3, NR +3,3). **Seuil de décision retenu** : une configuration n'est retenue que si la borne basse de l'IC95 apparié de son gain de Qualité est > 0 (soit un gain d'environ +2,5 à +4 points), et sans baisse de NR dont l'IC95 exclut 0 · —
- 2026-10-20 08:42 · 14.7 (C7) · rejeu de contrôle **réussi** : CR de la Baseline MiniCPM, glm `20261020-081255-glm-minicpm5-2b-0c61` et deepseek `20261020-081848-deepseek-minicpm5-2b-f7fb` **complets** (25/25 CR, contre partiel-erreur avant) ; accord structure tiers/principal 92 % (κ 0,71) et 96 % (κ 0,88) ; 0,35 € · —
- 2026-10-20 08:48 · 14.12 (O4b) · dev · fini : 160 items dev1 (20 par tâche, difficultés 7/7/6, quotas tenus), 20 cassettes RD enregistrées, disjoint de v1.0, v1.1, data/train et seeds ; 2 rejets corrigés au second passage ; gel simulé sans écart · 5066105
- 2026-10-20 08:48 · 14.12 (O4b) · second-avis · 2 medium (CO-508 référence incohérente, contrôles verbatim des tests non appliqués à dev1), 3 low ; review lancée (Opus, relecture Claude de 24 items) · —
- 2026-10-20 09:01 · 14.17 (V17) · vérification payante `runs/data-generate/20261020-082915-generate-1402` (partiel-erreur : 4 sessions non jugées, à reprendre ; 1,33 € OpenRouter, 0 € Mistral) : **CR 40/80** retenues (juge : invention 32, couverture 19), **CT 23/35** (invention 9), **LC 0/80** (tests 61 ; juge 18 : fidélité 18, termes 8). Les cibles v14 inventent ou trahissent la source dans une large part : régénération O6b indispensable · —
- 2026-10-20 09:01 · run · décision · nouvelle campagne de budget `methodo-v2-2026-10-20b` (enveloppes d'Anaël) : anthropic 57 €, mistral 9,5 € (génération 7,8, juge 1,7), openrouter 44,5 € · —
- 2026-10-20 09:06 · 14.15 (O6b) · dev · fini (gabarits de correction, phrases fixes par code, motif DeepSeek filtré, 3 essais, seed partiel LC, completer-depuis élargi ; 1 798 tests) ; second-avis lancé (D1 prioritaire) · 8b143b6
- 2026-10-20 09:08 · 14.12 (O4b) · review (relecture Claude de 24 items : 3 défauts corrigés, 12,5 % ; contrôles automatiques sur 160 items : 5 corrigés de plus ; disjonction étendue au document source et aux preferences.jsonl ; 97 tests dev1 avec sources) · 2ce0a16
- 2026-10-20 09:08 · 14.12 (O4b) · fusion · squash dans main · 6998f6c
- 2026-10-20 09:08 · 14.12 (O4b) · contre-vérification payante lancée : DeepSeek + GLM sur dev1 (~1-1,5 €, pire cas ~4 €), puis gel relu-llm · —
- 2026-10-20 09:11 · 14.15 (O6b) · second-avis · 2 high : (D1) le texte libre du motif DeepSeek hors guillemets atteignait Mistral (« écrire plutôt … ») ; la procédure v17 ne régénérait que LC, pas les 40 CR et 9 CT refusées ; 1 medium, 3 low. **Décision** : aucun texte libre du juge dans la consigne de régénération (phrases fixes par critère + extraits exacts seulement) ; review lancée (Opus) · —
- 2026-10-20 09:34 · 14.15 (O6b) · review · 2 high corrigés (D1 : plus aucun texte libre du juge ni des contrôles dans la consigne, seulement phrases fixes et extraits exacts ≤ 200 car., test octet par octet ; procédure v17 avec --taches CR,LC,CT), 1 medium (complément d'un autre seed : même modèle et mêmes gabarits exigés) · 1b35e9b
- 2026-10-20 09:34 · 14.15 (O6b) · fusion · squash dans main ; tests data, mistral, cli data, architecture : 1 103 passés · bb16057
- 2026-10-20 09:34 · 14.17 (V17) · seed LC aligné O5 `runs/data-seed/20261020-093126-seed-4fcf` (240 LC de 195-361 mots, 11 exclues par l'anti-fuite, autres tâches recopiées de b335) · —
- 2026-10-20 09:34 · 14.17 (V17) · décision · génération vérifiée avec régénération lancée (CR, LC, CT ; 3 essais) : estimation pire cas Mistral 9,12 € (attendu ~3 €, registre plafonné à 7,8 €), OpenRouter plafond d'estimation 25 € (attendu 5-8 €, dans l'enveloppe de 50 $ d'Anaël) · —
- 2026-10-20 10:26 · 14.17 (V17) · génération vérifiée `runs/data-generate/20261020-093440-generate-792d` (partiel-erreur, 18 LC non jugées ; 1,26 €) : **CR 64/80**, **CT 30/35**, **LC 2/80** ; la régénération ne corrige pas les refus LC (gain de lisibilité 42 → 38 au 3e essai, modalité perdue 28 → 23) · —
- 2026-10-20 10:26 · 14.17 (V17) · décision · `lc_gain_lisibilite` et `lc_modalite_perdue` non bloquants par item : la grille plafonne LC à 50 seulement si le gain **moyen** de la Tâche est sous gain_km_min ; la fidélité reste jugée par DeepSeek (codes transmis comme indices). Réversible par config ; second-avis lancé ; génération relancée en complément du run 792d · 6bc488d
- 2026-10-20 11:25 · 14.17 (V17) · génération vérifiée `runs/data-generate/20261020-102600-generate-a376` (0,32 € ; partiel-erreur, 26 jugements interrompus) : CR 64/80, CT 30/35, **LC 5/80** : 44 refus du juge après 3 essais (fidélité 43, termes 19). Motifs DeepSeek relus sur un échantillon : fondés (conditions préalables omises, rôle du juge attribué au médecin, droits amoindris, ajouts non sourcés). Mistral Large 3 ne corrige pas ces infidélités sur des sources de 195-361 mots. Reprise des jugements interrompus lancée · —
- 2026-10-20 12:35 · 14.17 (V17) · reprise complétée : run a376 **complet** (DeepSeek 2,04 € au total) : CR 64/80, CT 30/35, LC 5/80 ; validate `runs/data-validate/20261020-115416-validate-aaf7` (468/499 retenus hors CR/LC/CT) ; filter et build v17 en cours · —
- 2026-10-20 12:35 · 14.12 (O4b) · contre-vérification dev1 (DeepSeek + GLM) : retenus 76, rejetés 30, **incomplets 54** (GLM sans verdict valide, 2 erreurs API DeepSeek) ; story de suite O4c lancée (Opus : cause GLM, items rejetés corrigés ou remplacés) ; gel relu-llm reporté · —
- 2026-10-20 12:54 · 14.17 (V17) · jeu **v17** (`runs/data-build/20261020-125304-build-90b1`, filtre `20261020-123457-filter-f997`, 468 lignes : CO 34, CR 64, CT 30, LC 5, Q 95, RD 132, RE 34, generique 74 ; consignes d'Agent dans les entrées) puis nettoyage → **v18** (`runs/data-build/20261020-125334-nettoyage-440e`, 468 lignes). Entraîné sans relecture d'Anaël (levée au §7 bis) ; échantillons dans les runs de génération (echantillon.md) et de build · —
- 2026-10-20 12:54 · 14.17 (V17) · M1 MiniCPM5-2B v18 lancé (`config/runs/m1-qlora-minicpm5-2b-v18.toml`, hyperparamètres du protocole ; train + export seulement : notation sur dev1 d'abord, puis mesure finale v1.1 si retenu) · —
- 2026-10-20 12:54 · 14.12 (O4b) · suite O4c · dev fini : cause GLM = l'outil n'envoyait ni l'effort de raisonnement ni le schéma (50 sorties vides coupées à 8 000 tokens) ; DeepSeek : délai de lecture ; 17 items corrigés, 17 rejets contestés (justification consignée), consigne v2 ; second-avis lancé · dbec22c
- 2026-10-20 12:57 · 14.12 (O4c) · second-avis · 2 high (les rejets croisés n'excluaient aucun item du jeu ; consigne v2 plus permissive appliquée aux seuls rejets, appels rédigés par l'auteur des items), 2 medium. **Décision** : consigne unique et neutre (v3) pour les 160 items, plus de contestations, exclusion appliquée à l'assemblage et au gel relu-llm (dernier verdict « retenu » par les deux juges exigé) ; review lancée (Opus) · —
- 2026-10-20 13:11 · 14.12 (O4c) · review · 4 high corrigés (consigne neutre v3 pour tous, contestations retirées, exclusion appliquée à l'assemblage et au gel), 2 medium · 9c40cb7
- 2026-10-20 13:11 · 14.12 (O4c) · fusion · squash dans main ; tests eval_outils, evaluation : 1 397 passés · aa31761
- 2026-10-20 13:11 · 14.12 (O4c) · revérification complète de dev1 lancée (160 items, DeepSeek + GLM, consigne v3, ~1,7 $) · —
- 2026-10-20 13:28 · 14.17 (V17) · M1 MiniCPM5-2B v18 entraîné (`runs/train/20261020-125424-m1-qlora-minicpm5-2b-v18-82ef`), export `20261020-132636-ft-minicpm5-2b-3479` ; génération v1.1 lancée (sans notation) · —
- 2026-10-20 15:16 · 14.12 (O4c) · revérification dev1 (consigne v3) : **123 retenus, 37 rejetés**, 0 incomplet (CR 8, NR 8, RE 6, Q 5, CT 3, RD 3, CO 2, LC 2 rejetés) ; story O4d lancée (correction ou remplacement des 37) · —
- 2026-10-20 15:16 · 14.17 (V17) · génération v1.1 de M1 MiniCPM v18 prête (`runs/eval-generation/20261020-132839-ft-minicpm5-2b-23df`, 24 sorties tronquées) ; GPU libre utilisé : M1 Qwen3.5-0.8B v18 lancé (train + export, sans notation) · —
- 2026-10-20 15:27 · 14.12 (O4d) · dev · fini : 37 items corrigés (aucun remplacé) ; cause commune CR (consigne « points abordés » non notée par la grille → consigne des 20 CR ramenée à participants, décisions, actions) et NR (forme ouverte) ; gel simulé 0 écart ; second-avis lancé · a98328e
- 2026-10-20 15:32 · 14.12 (O4d) · second-avis · 2 high (plaidoyer dans CO-516 ; CR-518 décision et piège contradictoires), 4 medium (griefs contournés CR-511, Q-520, RD-519 ; changement de consigne CR qui casse le critère Structure « Points abordés » de la grille). **Décision** : consigne CR rétablie (comparabilité avec v1.1), pas de plaidoyer, grief traité ou item remplacé ; review lancée (Opus) · —
- 2026-10-20 15:35 · 14.17 (V17) · M1 Qwen3.5-0.8B v18 entraîné (`runs/train/20261020-151705-m1-qlora-qwen3.5-0.8b-v18-fa23`), export `20261020-153433-ft-qwen3.5-0.8b-fb99` ; génération v1.1 lancée · —
- 2026-10-20 15:43 · 14.12 (O4d) · review · 2 high et 5 medium traités (plaidoyers retirés, CR-518 cohérent, consigne CR d'origine rétablie sur les 20 CR, NR-503 rétabli) ; **décision** : les 6 CR au grief « points abordés sans référence » sont revérifiés en l'état, remplacés s'ils restent rejetés · a876c23
- 2026-10-20 15:49 · 14.17 (V17) · génération v1.1 de M1 Qwen3.5-0.8B v18 prête (`runs/eval-generation/20261020-153559-ft-qwen3.5-0.8b-50a1`, 33 sorties tronquées) · —
- 2026-10-20 16:13 · 14.12 (O4d) · revérification ciblée : **155 retenus, 5 rejetés** (CR 1, NR 3, RD 1) ; fusion O4d 2e2caca ; story O4e lancée (remplacement des 5) · —
- 2026-10-20 16:26 · 14.12 (O4e) · 5 items remplacés (second-avis sans défaut) ; fusion · vérification : **159/160 retenus**, CR-521 rejeté par DeepSeek (« points abordés » non référencés, année des dates) ; correction des dates lancée (O4f), consigne CR commune conservée · —
- 2026-10-20 16:37 · 14.12 (O4b) · **dev1 gelé relu-llm** (159 items : CR 19 car CR-521 reste rejeté par DeepSeek sur un grief de grille commun à v1.1, exclu ; tous les autres retenus par DeepSeek et GLM ; consigne de vérification v3 neutre) · 2226401
- 2026-10-20 16:37 · 14.17 (V17) · chaîne dev1 lancée (génération cuda + notation GLM, plafond 3 € par notation) : Baselines MiniCPM5-2B et Qwen3.5-0.8B, M1 v14 et M1 v18 de chacun · —
