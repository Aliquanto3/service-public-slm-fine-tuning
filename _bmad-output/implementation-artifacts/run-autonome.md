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
