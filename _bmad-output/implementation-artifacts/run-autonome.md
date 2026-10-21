# Run autonome du 21 octobre 2026 : modèle distant, mode hybride, comparatif et observabilité (epic 17)

Stories : `../planning-artifacts/stories-epic-17-modele-distant.md` ; specs `spec-17-1-modele-distant.md`, `spec-17-1b-mistral-ovh.md` (dans la branche fusionnée), `spec-17-4-mode-hybride-app.md`, `spec-17-5-onglet-comparatif-modeles.md`, `spec-17-6-observabilite-app.md`. Consignes des sous-agents : `consignes-sous-agents-2026-10-20.md`. Run précédent (nuit du 20-21/10, epic 15) : `archive/run-autonome-2026-10-20-21-nuit.md`.
Demande d'Anaël (21/10 matin) : release v0.3.0 sur GitHub avec un installateur testable sur le PC cible (modèle externe réglable dans l'application) ; débordement en fin de journée accepté.
Budget : campagne `demo-2026-10-21` depuis 11 h 45 (anthropic 50 €, mistral 7,78 €, openrouter 14,22 €, ovh 2 €), avant : `nuit-2026-10-20`.

## Périmètre
| Périmètre | Epics | Note |
|---|---|---|
| Dans le run | Epics 17 à 17 | 17.1 modèle distant (eval), 17.1b Mistral et OVH, 17.4 mode hybride, 17.5a et 17.5b onglet Modèles, 17.6 observabilité ; mesures 17.2 (Qwen3.6-27B, Mistral Small) ; release v0.3.0 |
| Dans le run (nuit) | Epics 16 à 16 | stories de code seulement : 16.2, 16.3, 16.4, 16.5, 16.8, 16.6a ; **hors** 16.1 (vérification payante de dev2), 16.6 (entraînements : protocole à relire par Anaël), 16.7 |

Au plus 3 stories en développement à la fois.

## Sprint 1 — journée du 21/10
| Vague | Stories en parallèle | Après |
|---|---|---|
| V0 | 17.1 ★ | |
| V1 | 17.4 · 17.5a | 17.4 ← 17.1 |
| V2 | 17.5b · 17.1b | 17.5b ← 17.4 ; 17.1b ← 17.4 |
| V3 | 17.6 | 17.6 ← 17.4 |

## Sprint 2 — nuit du 21-22/10 (Anaël absent, « je te laisse avancer sur ces sujets toute la nuit »)
| Vague | Stories en parallèle | Après |
|---|---|---|
| V0 | 17.3 · 16.4 · 16.2 | 17.2 (Qwen3.8-27B, vitesses CPU) en parallèle, machine au calme pour les mesures CPU |
| V1 | 16.5 · 16.3 · 16.6a | 16.5 ← 16.4 |
| V2 | 16.8 | 16.8 ← 16.2 (même zone du Harnais Q) |
Règles de la nuit : aucune release, aucun push hors fusion locale dans main, aucun entraînement, aucun appel payant sauf les mesures 17.2 (≤ 1 € de génération + 1 € de notation par modèle) ; bloqueur de veille actif.

## Journal
- 2026-10-21 · 17.1 · dev · lancé · —
- 2026-10-21 · 17.1 · dev · fini · 29e5069
- 2026-10-21 · 17.1 · second-avis · 1 medium, 4 low · —
- 2026-10-21 · 17.1 · review · Opus, corrigé · 3b19984
- 2026-10-21 · 17.4 · dev · lancé · —
- 2026-10-21 · 17.4 · dev · fini (partiel, puis amendement 14) · 5bc85a1
- 2026-10-21 · 17.4 · second-avis · 1 medium, 2 low · —
- 2026-10-21 · 17.4 · review · Opus, corrigé · 3af4339
- 2026-10-21 · 17.5a · dev · fini · 7727332
- 2026-10-21 · 17.5a · second-avis · 2 medium · —
- 2026-10-21 · 17.5a · review · Opus, corrigé · 66b1e5c
- 2026-10-21 · 17.5b · dev · fini · aa28609
- 2026-10-21 · 17.5b · second-avis · 6 low · —
- 2026-10-21 · 17.5b · review · Sonnet, corrigé · 8883753
- 2026-10-21 · 17.5b · fusion · squash dans main · 50317d1
- 2026-10-21 · 17.1b · dev · fini · d7dce2b
- 2026-10-21 · 17.1b · second-avis · 7 low · —
- 2026-10-21 · 17.1b · review · Sonnet, corrigé · 4787e11
- 2026-10-21 · 17.1b · fusion · squash dans main · f9d97ba
- 2026-10-21 · 17.6 · dev · lancé · —
- 2026-10-21 07:31 · disque · purge validée par Anaël : 13 exports antérieurs à v18 retirés de `runs/export` (1752, d543, 3425, ad30, 1581, 0462, 3934, a5ad, 5883, b7bd, f4f4, 5606, e69a ; adaptateurs gardés dans `runs/train`, réexport possible), intermédiaires f16 de 4d47 et fb99 retirés (q4_k_m gardés), `models/qwen-4b` retiré (Qwen3-4B, tokenizer incompatible ; fiche gardée), WSL Ubuntu, ancienne installation llama.cpp b10537 et llama-env, doublons Ollama (qwen3.5 0.8b/2b/4b, minicpm5) et Qwen3.6-35B-A3B de D:. C: 20 → 101 Go libres, D: 60 → 87 Go · —
- 2026-10-21 07:31 · qwen3.5-4b · fetch (`20261021-055429-modeles-18cb`, même tokenizer que 0.8B et 2B) puis dev1 en cuda : génération `20261021-064322-qwen3.5-4b-b0bc`, notation `20261021-072300-qwen3.5-4b-d113` (0,32 €). **Qualité 54,6** (Q 25,0 ; RD 84,7 ; CR 69,2 ; LC 25,0 ; CO 92,7 ; RE 60,5 ; CT 20,0 ; NR 60,0), au niveau de MiniCPM5-2B (54,5) et +17,8 [+11,1 ; +24,6] sur Qwen3.5-0.8B (36,8). Run Qwen3-4B `20261021-055157-qwen-4b-42e7` annulé en génération (0 €), à ignorer · —
- 2026-10-21 07:51 · qwen3.5-2b · dev1 en cuda : génération `20261021-073330-qwen3.5-2b-8b5f` (12 tronquées), notation `20261021-075050-qwen3.5-2b-9ed5` (relancée pour 1 item CT, 0,36 € au total). **Qualité 42,7** (Q 5,0 ; RD 68,3 ; CR 48,1 ; LC 30,0 ; CO 88,1 ; RE 47,3 ; CT 25,0 ; NR 30,0) : −11,7 [−17,3 ; −5,1] sous MiniCPM5-2B, −11,9 [−18,5 ; −5,3] sous Qwen3.5-4B ; CO +16,0 sur MiniCPM · —
- 2026-10-21 09:20 · 17.1 · fusion · squash dans main (87310a9) après second avis (1 medium, 4 low) et revue Opus (3b19984 : flux mal formé, réservations abandonnées, Retry-After plafonné) ; métadonnées suivies des exports purgés restaurées (`git restore runs/export`) · 87310a9
- 2026-10-21 09:20 · 17.1 · essai réel · `distant:qwen3.6-27b` sur Q-501 et RD-502 (`20261021-091955-distant-qwen3.6-27b-9498`) : 2 ok, hébergeur DeepInfra et modèle conformes, `reasoning_tokens` 0 (`reasoning.enabled=false` confirmé), outils RD OK, ~0,001 € par appel, premier token 0,5-0,8 s ; mesure dev1 complète lancée (plafonds 1 € + 1 €) · —
- 2026-10-21 09:20 · OVH AI Endpoints · joignable sans clé (2 requêtes/min), Qwen3.6-27B et outils OK, `chat_template_kwargs` refusé (HTTP 400), raisonnement actif par défaut ; clé à créer par Anaël (projet Public Cloud, crédit de 200 € pour un premier projet) · —
- 2026-10-21 09:42 · 17.2 · qwen3.6-27b dev1 (OpenRouter, DeepInfra fp8) : génération `20261021-092032-distant-qwen3.6-27b-3ae2` (2 RD en 429 rejoués par `--reprendre`, 0,18 €), notation `20261021-094134-distant-qwen3.6-27b-fc13` (0,30 €). **Qualité 71,6** contre MiniCPM5-2B 54,5 (+17,1 [+11,8 ; +23,7]) : Q 35,0 ; RD 87,4 ; CR 86,5 ; LC 30,0 ; CO 96,9 ; RE 89,6 ; CT 52,5 ; NR 95,0 · —
- 2026-10-21 09:42 · main · suite complète après fusion 17.1 : verte (code de sortie 0) · —
- 2026-10-21 09:42 · 17.4 · dev · partiel (f33a1ef) : exigences 1-9 et amendements 1-13 faits ; amendement 14 (plusieurs fournisseurs) refusé par le classifieur dans le sous-agent (changement de périmètre reçu par message) ; Anaël l'a confirmé dans la session principale (« OK pour tes recommandations de développement », preset openrouter-eu retiré) : relancé par un nouvel agent avec le périmètre dans sa consigne · f33a1ef
- 2026-10-21 11:07 · 17.5a · fusion · squash dans main (1c364f7) après second avis (coût sous-estimé, appariement) et revue Opus (933cdcd, 66b1e5c) ; référence MiniCPM5-2B re-notée complète (`20261021-095813-minicpm5-2b-47d5`, 0,02 €, Qualité 54,3) ; Qwen3.6-27B : 1,16 € / 1 000 demandes, 90 tokens/s · 1c364f7
- 2026-10-21 11:07 · 17.4 · fusion · squash dans main (f584f62) après second avis (clé liée à l'id) et revue Opus (3af4339 : clé liée à l'hôte et au preset, vérification sur le même fournisseur, saisies conservées) · f584f62
- 2026-10-21 11:07 · 17.5b · dev lancé (Sonnet) ; 17.1b · dev lancé (Opus) ; suite complète sur main lancée · —
- 2026-10-21 11:37 · 17.2 · mistral-small-2603 dev1 (API Mistral directe) : génération `20261021-112139-distant-mistral-small-mistral-0b86` (CO-501 rejoué après ConnectError, 0,07 €), notation `20261021-113707-distant-mistral-small-mistral-938a` (0,30 €). **Qualité 58,8** contre MiniCPM5-2B 54,3 (+4,5 [−0,4 ; +10,8]) : Q 15,0 ; RD 88,6 ; CR 79,9 ; LC 10,0 ; CO 90,5 ; RE 68,5 ; CT 32,5 ; NR 85,0 · —
- 2026-10-21 11:37 · budget · campagne nuit-2026-10-20 close (anthropic 0 €, mistral 0,07 €, openrouter 5,78 €) ; campagne demo-2026-10-21 ouverte avec les restes et le poste ovh 2 € (accord d'Anaël) · —
- 2026-10-21 11:37 · OVH · essai `distant:qwen3.6-27b-ovh` : HTTP 401 « Your token is not allowed to perform the required actions on any tenant » sur les 2 items, 0 € : clé à vérifier par Anaël · —
- 2026-10-21 11:37 · 17.6 · dev lancé (Opus) après second avis de la spec (6 high intégrés en amendements) · —
- 2026-10-21 19:16 · run · décision · journal de la journée séparé du run de nuit (archivé) ; périmètre epic 17 et sprint status mis à jour après un rapport d'avancement trompeur (périmètre resté sur l'epic 15) · —
- 2026-10-21 19:47 · 17.6 · dev · fini · 8505cfd
- 2026-10-21 19:47 · 17.6 · second-avis · 2 medium, 3 low · —
- 2026-10-21 19:47 · 17.6 · review · Opus, corrigé, impact réaligné sur EcoLogits (page relevée le 21/10, valeurs vérifiées à la main) · ef86d61
- 2026-10-21 19:47 · 17.6 · fusion · squash dans main · f4e58ff
- 2026-10-21 19:47 · main · décision · test_aucun_innerhtml (commentaire de vues/modeles.js) et test d'imputation OVH corrigés · 1dacc17
- 2026-10-21 19:47 · 17.4b · dev · lancé (OVH sans clé, demande d'Anaël) · —
- 2026-10-21 22:21 · 17.4b · fusion · squash dans main après second avis (1 high : hôte non vérifié en accès gratuit) et revue Sonnet (8e84c85) · a4f9c58
- 2026-10-21 22:21 · main · suite complète : 6 385 passés, 1 échec (liste des postes sans ovh) corrigé · b2124d8
- 2026-10-21 22:21 · release · version 0.3.0 (39441c5) ; application construite (3 070 Mo) ; installateur (2,68 Go) ; installation silencieuse et démarrage vérifiés sur ce PC ; mesure Qwen3.8-27B interrompue à 120/159 pour la construction (reprise possible) · 39441c5
- 2026-10-21 22:28 · release · v0.3.0 publiée (https://github.com/Aliquanto3/service-public-slm-fine-tuning/releases/tag/v0.3.0), 4 fichiers vérifiés (tailles), main et tag poussés · 39441c5
- 2026-10-21 22:28 · 17.2 · reprise de la mesure Qwen3.8-27B (`--reprendre`) · —
- 2026-10-21 22:28 · run · décision · **Anaël autorise les entraînements de 16.6 cette nuit** (« Je t'autorise à relancer les entraînements si tu as du temps ») à la place de la relecture du protocole ; pas de clé OVH corrigée (OVH abandonné pour la nuit) ; 16.1 (relance unique de 5 items dev2, ~0,05 €) lancée selon sa décision du 21/10 05:41 · —
- 2026-10-21 22:36 · 16.2 · dev · lancé · —
- 2026-10-21 22:36 · 16.3 · dev · lancé · —
- 2026-10-21 22:36 · 16.6a · dev · lancé · —
- 2026-10-21 22:36 · 16.2 · dev · fini · 24b4489
- 2026-10-21 22:36 · 16.2 · second-avis · lancé · —
- 2026-10-21 22:36 · 16.1a · dev · lancé (option --forcer de la vérification, sans quoi la relance « en l'état » de 16.1 ne rappelle aucun juge) · —
- 2026-10-21 22:47 · 16.1a · fusion · squash dans main après second avis (1 medium : un échec forcé réintégrait un item rejeté) et revue Sonnet ; correctif de l'orchestrateur : items forcés repris des brouillons · 0c8abc8
- 2026-10-21 22:47 · 16.1 · relance forcée DeepSeek + GLM de CO-609, CO-615, CT-602, CT-612, CT-614 (~0,05 €) : **5 retenus** ; aucun item exclu ; dev2 assemblé 160 items, composition conforme, gelé `relu-llm` (graine 42) · fa1e3e6
- 2026-10-21 22:47 · 16.3 · dev · partiel (1f8d73f) : anti-boucle livré (13 boucles v18 coupées, 0 sortie Baseline coupée) ; **build v21 bloqué par D1** : aucune formulation d'origine non-Claude pour la consigne de libellés → **attente humaine** (Anaël doit fournir une ligne contenant {libelles} et son origine) · 1f8d73f
- 2026-10-21 22:47 · 16.6 · décision · essais de la nuit sur **v18** (v21 bloqué) : T1 à T6 de la grille, T0 = M1 v18 existant · —
- 2026-10-21 22:47 · 16.6a · second-avis · 1 high (mémoire : logits pleins élève et base) · — 
- 2026-10-21 22:50 · 16.2 · review · Opus, corrigé (Q seule à 8 passages, refus des versions mélangées à la composition, coupe au mot) · 62794ca
- 2026-10-21 22:50 · 16.2 · fusion · squash dans main · 1428794
- 2026-10-21 22:50 · 16.3 · second-avis · 5 medium (faux positifs, interface, tronquee, conflit 16.2), 3 low · —
- 2026-10-21 22:50 · 16.3 · review · lancée (Opus) · —
- 2026-10-21 22:50 · 16.6 · T1 · entraînement lancé (chaîne T1 à T5, train puis export LoRA) · —
- 2026-10-21 22:50 · 16.4 · dev · lancé · —
- 2026-10-21 22:56 · 16.6a · review · Opus, KL par tranches (pic estimé < 1 Go en plus, au lieu de 9 à 25 Go) · 93fd972
- 2026-10-21 22:56 · 16.6a · fusion · squash dans main · cd86314
- 2026-10-21 22:56 · 16.6 · décision · après T1-T5 : essai KL de 5 pas (VRAM, rapport KL / entropie croisée), puis T6 avec kl_base tel que kl_base × KL ≈ entropie croisée / 4 (script `chaine-kl.sh` du scratchpad) · —
