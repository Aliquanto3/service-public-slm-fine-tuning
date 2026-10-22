# Bilan des tentatives de fine-tuning (12 au 22 octobre 2026)

Le 22 octobre 2026, Anaël a décidé d'arrêter les tentatives de fine-tuning. La suite se concentre sur le démonstrateur, avec un SLM préexistant et/ou un modèle cloud. Ce document conserve les méthodes essayées, leurs résultats chiffrés et les leçons tirées, pour qu'on puisse reprendre un jour sans refaire les mêmes erreurs.

Chaque chiffre vient d'un fichier cité. Sauf mention contraire, les chemins sont relatifs à `_bmad-output/implementation-artifacts/` (noté `IA/`) ou à `_bmad-output/planning-artifacts/` (noté `PA/`). Une valeur qu'aucun fichier ne donne est marquée « non retrouvé ».

---

## 1. Résumé

1. **Objectif.** Fine-tuner un SLM de 2,5 B paramètres au plus, servi en local sur un PC de 16 Go sous Windows. Il doit faire mieux que son modèle de base sur 8 tâches du secteur public : Q, RD, CR, LC, CO, RE, CT et NR. Les données sont générées par Mistral, et Claude ne génère jamais de donnée d'entraînement (règle D1).
2. **Modèles entraînés.** MiniCPM5-2B (le modèle principal), Qwen3.5-2B et Qwen3.5-0.8B. Granite 4.0 1B, MiniCPM5-1B, les Granite H, EuroLLM-1.7B et qwen-4b n'ont servi qu'à la Baseline, ou ont été écartés.
3. **Méthodes.** 33 runs d'entraînement (`runs/train/`) sur 20 versions de jeu (v1 à v20 ; v21 est bloquée). On a essayé QLoRA (M1), DoRA (M3) et ORPO (M4, jamais mené à terme). Les jeux ont été nettoyés, régénérés, alignés sur la grille, vérifiés par un juge de données, puis sélectionnés parmi plusieurs candidats.
4. **Méthodes de pilotage.** Interpolation de l'adaptateur (échelles 0,25, 0,5 et 1), routage par tâche, régularisation KL vers la base, et une grille taux, rang, pas.
5. **Verdict.** **Aucun fine-tuning général ne bat la Baseline.** Sur v1.1 avec le juge Claude, tous les M1 MiniCPM5-2B restent entre 32,6 et 38,9, contre 41,1 pour la Baseline. Sur dev1 avec le juge GLM, tous les adaptateurs à pleine échelle perdent entre 4 et 10 points.
6. **Cause.** Une **dérive générale de l'adaptateur** dégrade CR, LC et RE, même quand ces tâches sont absentes du jeu. Changer les cibles, le taux, le rang ou le nombre de pas ne la corrige pas. La régularisation KL l'efface, mais elle efface aussi le gain.
7. **Ce qui tient.** Seul le **routage d'un adaptateur sur la tâche CO** (base partout, LoRA v18 sur CO) tient. Mesure finale v1.1 : CO 58,9 → 78,7, Qualité 41,1 → 43,6. Confirmé sur dev2 : CO +12,4 [+5,6 ; +18,7].
8. **Ce qui ne dépend pas du fine-tuning.** Les plafonds de Q (recherche, abstention) et la mesure CT saturée.
9. **Recommandation.** Pour le démonstrateur : la base MiniCPM5-2B, avec en option le LoRA CO routé, le garde-fou anti-boucle et le harnais v2, ou un modèle distant (Qwen3.8-27B : 74,1 sur dev1).
10. **Pour reprendre un jour.** Ne pas relancer un SFT global sur cibles Mistral. Partir de la section 5 (plus d'items, complément CR, v21, méthodes non testées).

---

## 2. Cadre de mesure

### 2.1 Jeux d'évaluation

| Jeu | Items | Juge | Statut | Usage | Source |
|---|---|---|---|---|---|
| v1.0-provisoire | 225 | Claude Opus 5.5 (Batch API) + second juge Mistral sur 34 items | gel du 12/10 (manifeste `70c42fb5…`) | première Baseline (Granite 1B, Ministral 3B) | `IA/baseline-rapport.md` |
| **v1.1** | 225 (Q 60, RD 40, CR 25, LC 25, CO 15, RE 15, CT 15, NR 30) | **Claude** | gelé | toutes les mesures jusqu'au 20/10 ; ensuite **mesure finale seulement**, une fois par configuration retenue | `IA/e1-variance.md`, `IA/plan-methodo-2026-10-20.md` §6 |
| **dev1** | 159 (20 par tâche, CR 19 après exclusion de CR-521) | **GLM-5.3** (OpenRouter) | gel `relu-llm` du 20/10 (commit 2226401) | décisions (routage, échelles, essais) | `IA/archive/run-autonome-2026-10-20.md` |
| **dev2** | 160 (601-620 par tâche) | **GLM-5.3** (section `[jeux.dev2]` ajoutée le 22/10) | gel `relu-llm` du 21/10 (fa1e3e6) | confirmation seulement, jamais consulté pour choisir | `IA/run-autonome.md` |

Pour dev1 et dev2, `relu-llm` signifie : items rédigés par un agent, relus par Claude (autorisé pour l'évaluation, jamais pour l'entraînement), contre-vérifiés par DeepSeek V4 Pro et GLM avec une consigne neutre v3. Un item rejeté par l'un ou l'autre est exclu. Anaël ne les a pas relus. v1.1 reste la seule mesure finale (`IA/plan-methodo-2026-10-20.md` §7 bis).

### 2.2 Scores

- **Qualité** = moyenne des 8 Scores de Tâche, sur 100.
- **Q** (question fondée) : un item compte seulement si l'exactitude vaut 2, c'est-à-dire si **tous** les 3 à 5 éléments clés sont présents et justes, si la pertinence de la source vaut 1 et s'il n'y a aucune URL inventée (`IA/etat-run-2026-10-19-portable.md`, 19/10 15:01).
- **CR** = moyenne(couverture, sans_invention) ; **RE** = moyenne(couverture, fidèles) (`IA/diagnostic-d0.md` §a).
- **LC** : fidélité et termes, plafonné quand le gain moyen de Kandel-Moles de la tâche passe sous le seuil (`IA/e1-variance.md`, note).
- **CT** : conformité (tous les éléments obligatoires) et emplacements. La conformité vaut 0/20 pour tous les modèles, base comprise : la mesure est **saturée** (`IA/diagnostic-d0.md` §b).
- **RD, CO, NR** : contrôles déterministes, sans juge (`IA/baseline-rapport.md` §2).

### 2.3 Fiabilité des juges

- Juge principal Claude contre second juge Mistral : kappa entre −0,00 et 0,21, calculé sur 3 à 5 items par tâche, donc non interprétable (`IA/baseline-rapport.md` §2 ; `IA/archive/run-autonome-2026-10-19.md`, 21:50).
- Juges tiers DeepSeek V4 Pro et GLM-5.3 sur 6 notations v1.1, accord brut avec Claude :

  | Critère | DeepSeek | GLM |
  |---|---|---|
  | CR sans invention | 98 % | 94 % |
  | CT conformité | 99 % | 98 % |
  | LC fidélité | 85 % | 74 % |
  | LC termes | 89 % | 93 % |
  | RE fidélité | 86 % | 76 % |

  Conclusion : **le juge principal est confirmé, et les baisses des fine-tunés sont réelles** (`IA/archive/run-autonome-2026-10-19.md`, 20/10 02:17).

### 2.4 Bruit et statistique

- **Décodage glouton** (graine 42, température 0) : deux générations d'un même GGUF sont identiques. Le bruit vient donc de l'entraînement et de l'échantillon d'items (`IA/archive/run-autonome-2026-10-20.md`, 14.16).
- **Graine d'entraînement** (E1, M1 MiniCPM5-2B v14, graines 1234 et 4321, v1.1) : 36,0 contre 36,2, écart +0,1, IC95 [−2,5 ; +2,6]. Par tâche, l'écart va jusqu'à ±5 (`IA/e1-variance.md`).
- **Items, pour un run seul** (demi-largeur de l'IC95 de la Qualité) : ±2,5 à ±3,9 sur v1.1 (`IA/e1-variance.md`), ±4,4 à ±4,9 sur dev1 (`IA/dev1-minicpm.md`, `IA/e5/e5-qwen.md`).
- **Bootstrap apparié** (`eval comparer`, 2 000 tirages, graine 7, IC95 en percentiles) : il sert à toutes les décisions à partir du 20/10.
- **Puissance.** Avec 20 items par tâche, la demi-largeur par tâche vaut ±10 à ±17. La règle « aucune borne basse < −10 » est donc **sous-puissante** : elle échoue souvent même sans effet réel (`IA/archive/run-autonome-2026-10-20-21-nuit.md`, 21/10 01:29).

### 2.5 Règles de décision, écrites avant tout calcul

| Période | Règle | Source |
|---|---|---|
| 19/10 (campagnes v2 à v14) | M3 et M4 seulement pour un modèle dont M1 dépasse **sa** Baseline v1.1. Benchmarks si +10 points sur au moins 2 tâches parmi Q, RD, CR et LC | `IA/etat-campagne-v11.md` |
| 20/10 (après E1) | Retenue si la borne basse de l'IC95 apparié du gain de Qualité est > 0, sans baisse de NR dont l'IC95 exclut 0. Décisions sur dev1, v1.1 une seule fois | `IA/archive/run-autonome-2026-10-20.md`, 08:31 ; `IA/plan-methodo-2026-10-20.md` §6 |
| Nuit 20-21/10, E5 (routage) | Adaptateur routé sur la tâche t si la borne basse de l'IC95 sur dev1 est > 0 pour t, et jamais si NR baisse significativement | `IA/archive/run-autonome-2026-10-20-21-nuit.md` |
| Nuit 20-21/10, E7 (échelle) | Aucune tâche avec une borne basse < −10, et Qualité ≥ Baseline − 2 | idem |
| Nuit 20-21/10, v20 | Qualité dev1 ≥ meilleure composition routée − 2 | idem |
| Nuit 21-22/10, 16.6 | Non-infériorité E7 **et** borne basse CO > 0 ; remplace le routage si Qualité ≥ routage − 1 | `PA/stories-epic-16-derive-et-confirmation.md` |
| Nuit 21-22/10, 16.7 | Routage confirmé si la borne basse CO sur dev2 est > 0 ; échelle 0,25 confirmée si la non-infériorité tient sur dev2 | idem |

### 2.6 Garde-fous

- **D1** : Claude ne génère aucune donnée d'entraînement, ni cible, ni few-shot, ni amorce. Mistral `mistral-large-latest` est le générateur. Aucun verdict de Claude ne filtre de données. Les conditions Mistral sont revérifiées chaque jour par un GET et un SHA (`PA/decisions.md` D1).
- **Juges de données** : DeepSeek V4 Pro est autorisé comme juge de sélection, et ses sorties ne deviennent jamais des cibles (`IA/plan-methodo-2026-10-20.md` §7 bis). Les CGU relues le 21/10 montrent que Z.ai (GLM) et Kimi interdisent d'entraîner sur leurs sorties. GLM reste donc juge des seuls jeux `dev*` (`PA/stories-epic-16-derive-et-confirmation.md`). GPT et Gemini sont exclus (licence non instruite).
- **Budgets durs** contrôlés par le code (registre SQLite, réservation au pire cas) ; plafond de 4,5 € par notation pendant les campagnes v11 et suivantes.
- **Harnais v1 et v2** : le harnais v2 du 21/10 passe Q à 8 passages, dédoublonne le préfixe des passages et ajoute le garde-fou anti-boucle. `eval comparer` refuse de mélanger des runs v1 et v2 (`PA/stories-epic-16-derive-et-confirmation.md` 16.2). La Baseline MiniCPM5-2B sur dev1 vaut 54,5 en harnais v1 et 53,0 en harnais v2.
- **Relecture d'Anaël** avant toute nouvelle phase d'entraînement (décision du 19/10 13:31). Elle a été levée pour les jeux de la méthodologie v2, à condition de consigner échantillons et rapports (`IA/plan-methodo-2026-10-20.md` §7 bis).

---

## 3. Chronologie des méthodes

### 3.0 Baselines de référence

**v1.1, juge Claude**, mesures CPU à contexte 4096 et Q4_K_M (`IA/etat-run-2026-10-18-portable.md`) :

| Modèle | Qualité | tokens/s CPU | RAM |
|---|---|---|---|
| **MiniCPM5-2B** | **41,1** | 16,7 | 3,88 Go |
| Qwen3.5-2B | 36,0 | 23,1 | 3,39 Go |
| Granite 4.0 1B | 33,4 | 14,6 | 3,88 Go |
| Granite 4.0 H 1B (Mamba) | 32,5 | 26,4 | 3,88 Go |
| Qwen3.5-0.8B | 27,5 | 43,3 | 2,26 Go |
| MiniCPM5-1B | 24,4 | 36,4 | 2,18 Go |
| EuroLLM-1.7B | 21,5 | 23,2 | 3,91 Go |
| Granite 4.0 350M | 15,9 | 39,6 | 1,73 Go |
| Granite 4.0 H 350M | 14,5 | non mesuré | — |
| qwen-4b (Qwen3-4B, hors règle de taille) | 45,9 | — | 8,47 Go (mesure du 21/10) |

Sources de la ligne qwen-4b : 45,9 dans `IA/plan-nuit-2026-10-20.md` §1, et 8,47 Go dans `IA/archive/run-autonome-2026-10-20-21-nuit.md`, 03:26. Sur v1.0 : Granite 1B 33,4 et Ministral 3 3B 32,2 (`IA/baseline-rapport.md`).

**dev1, juge GLM** :

| Modèle | Qualité | Source |
|---|---|---|
| MiniCPM5-2B, harnais v1 | 54,5 | `IA/archive/run-autonome-2026-10-20.md` |
| MiniCPM5-2B, harnais v2 | 53,0 | `IA/run-autonome.md` |
| Qwen3.5-0.8B | 36,8 | `IA/archive/run-autonome-2026-10-20.md` |
| Qwen3.5-2B | 42,7 | `IA/run-autonome.md`, 21/10 07:51 |
| Qwen3.5-4B | 54,6 | idem, 07:31 |
| Modèles distants : Qwen3.6-27B | 71,6 | `IA/run-autonome.md` |
| Modèles distants : Qwen3.8-27B | 74,1 | idem |
| Modèles distants : Mistral Small 2603 | 58,8 | idem |

**dev2, MiniCPM5-2B, harnais v2** : 55,6.

**Profil de la base** (rapport de Baseline du 12/10). Elle maîtrise RD et CO, mais échoue sur les tâches de fidélité stricte à une source : Q, LC, RE et CT. C'était l'hypothèse de départ : le fine-tuning devait améliorer ces tâches.

### 3.1 Choix du matériel et de la méthode (17 au 19/10)

- **Hypothèse.** QLoRA à 8 192 tokens tient sur le portable (RTX 3060 Laptop 6 Go, 32 Go de RAM), sous Windows natif.
- **Enquête** (`IA/enquete-entrainement-hybrides-2026-10-18.md`). Ce n'est pas Linux qui fait gagner de la mémoire : c'est l'appel `prepare_model_for_kbit_training`, qui coûte cher (cast fp32 des embeddings de 130k à 248k × 2048). Sans lui (`precision_base = "bf16"`), MiniCPM5-2B tient 8 192 tokens en 4,69 Gio (596 t/s). Pour Qwen3.5 (Gated DeltaNet), il faut triton-windows et flash-linear-attention : environ 1 050 t/s. WSL2 est inutile.
- **Validation** (`PA/decisions.md` D8). bf16 et fp32-kbit donnent la même perte à 1 % près sur 100 pas (0,533 contre 0,536). bf16 prend 3,0 Gio contre 4,85.
- **Limites mesurées.**
  - M2 (LoRA bf16 non quantifié) déborde dès 4 096 tokens sur 6 Go : il est **retiré**.
  - Granite 4.0 1B déborde dès 4 096 tokens (vocabulaire de 100k) et ne tient qu'à 3 072 : il est **retiré de la campagne** le 19/10, gardé en réserve, et n'a jamais été entraîné.
  - Unsloth refuse MiniCPM5-2B (« untrained tokens »).
  - Troncature du jeu v2 : 2 048 tokens gardent 37 % de la supervision, 4 096 en gardent 86 % et 8 192 en gardent 100 % (`IA/etat-run-2026-10-18-portable.md`).
- **Protocole M1, inchangé jusqu'au 21/10** : QLoRA nf4 sur base bf16, 8 192 tokens, rang 16, alpha 32, dropout 0, lr 2e-4, 1 époque, lot 1 × 8, cosinus, échauffement 3 %, graine 1234 (`config/runs/m1-qlora-minicpm5-2b-v18.toml`). M3 DoRA a les mêmes hyperparamètres ; M4 ORPO ajoute beta 0,1 et part du SFT M1.

### 3.2 Jeux v1 à v4 : génération Mistral brute, puis nettoyage déterministe (17 au 19/10)

- **Hypothèse.** Environ 500 exemples générés par Mistral Large 3, à partir d'amorces publiques, suffisent à améliorer les tâches faibles.
- **Jeux.**
  - **v1** : campagne 9.8, seed `20261017-111645-seed-b335`, 503 lignes.
  - **v2** : v1 avec le premier message des 91 lignes RD mis en Mode connecté.
  - **v3** : 410 paires ORPO tirées de v2.
  - **v4** : v2 nettoyé (425 lignes) : préambules « Voici… » retirés, et cibles plus longues que le `max_tokens` d'évaluation (1 024) **écartées**. Les 76 CR sont toutes écartées, donc v4 n'a plus de CR.
  - **v5** : 344 paires ORPO tirées de v4.

  Sources : `IA/etat-run-2026-10-19-portable.md` ; `IA/etat-run-2026-10-17-portable.md` pour les 503 lignes.
- **Résultats** (MiniCPM5-2B, v1.1, Claude) :

  | Run | Q | RD | CR | LC | CO | RE | CT | NR | Qualité |
  |---|---|---|---|---|---|---|---|---|---|
  | Baseline | 5,0 | 75,1 | 50,1 | 24,0 | 58,9 | 35,5 | 50,0 | 30,0 | **41,1** |
  | M1 v2 (`20261019-040548-…-1d82`) | 0,0 | 83,5 | 24,5 | 0,0 | 70,7 | 42,8 | 40,0 | 23,3 | 35,6 |
  | M3 DoRA v2 (`…-050830-…-fa99`) | 0,0 | 83,6 | 18,2 | 0,0 | 66,3 | 32,6 | 36,7 | 16,7 | 31,8 |
  | M1 v4 (`20261019-145809-…-4531`) | 0,0 | 83,0 | 37,5 | 4,0 | 76,2 | 36,8 | 36,7 | 36,7 | 38,9 |

- **M4 ORPO sur v3.** Le run tombe en OOM à 8 192 et à 4 096 tokens. Le run à 2 048 a été tué le 19/10 vers 5 h 30, quand la VRAM pleine a débordé en RAM partagée et que Claude Code a coupé ses tâches de fond. Il n'a **jamais abouti**.
- **Apprentissages.**
  - Le **style du générateur** se transmet. 65 cibles LC sur 69 commencent par « Voici », et M1 reprend ce préambule en gras. Les cibles CR ont une médiane de 5 285 caractères : M1 s'allonge, il est tronqué sur 22 CR sur 25, et son taux `sans_invention` passe de 40 % à 8 %.
  - Retirer le préambule ne suffit pas : le modèle ouvre alors par un titre en gras (144 sorties v4).
  - **CR remonte de 10,8 points sans aucune ligne CR** (v4 contre v2) : c'est le premier signe que l'adaptateur agit hors des tâches entraînées.
  - DoRA fait moins bien que QLoRA : la méthode n'est pas le levier.

### 3.3 Jeux v6 à v11 : cibles courtes et régénération ciblée (19/10)

- **Hypothèse.** Des cibles plus courtes, sans titre ni préambule, et des RD sans date inventée suppriment l'allongement et l'invention.
- **Mise en œuvre.**
  - Régénération Mistral avec des plafonds de mots par tâche (story 9.10) : Q 160, RD 120, CR 400, LC 150, CT 150, generique 200. Les `max_tokens` du générateur sont abaissés.
  - RE régénéré pour retirer « **Résumé (80 mots max.) :** » (9.11).
  - RD régénéré : producteur et date seulement s'ils figurent au résultat d'outil (9.12). Les rejets RD `valeur_absente` passent de 73 à 7.
  - Jeux : v9 a 484 lignes ; **v11** a 552 lignes (médianes en mots : Q 106, RD 46, CR 396, LC 113, CT 152, RE 112), pour environ 4,3 € de Mistral jusqu'à v9 et 1,09 € pour RD (`IA/dossier-relecture-v9.md`, `IA/etat-campagne-v11.md`).
- **Résultats M1 v11** (v1.1, Claude, `IA/etat-campagne-v11.md`) :

  | Modèle | Q | RD | CR | LC | CO | RE | CT | NR | Qualité | Baseline |
  |---|---|---|---|---|---|---|---|---|---|---|
  | MiniCPM5-2B | 3,3 | 77,8 | 21,7 | 4,0 | 71,3 | 39,0 | 13,3 | 30,0 | 32,6 | 41,1 |
  | Qwen3.5-2B | 1,7 | 66,0 | 25,2 | 0,0 | 88,5 | 27,6 | 13,3 | 40,0 | 32,8 | 36,0 |
  | Qwen3.5-0.8B | 0,0 | 67,9 | 14,2 | 0,0 | 69,3 | 21,4 | 10,0 | 16,7 | 24,9 | 27,5 |

- **Apprentissages.**
  - Les trois modèles passent sous leur Baseline : ni M3 ni M4 (règle de suite).
  - Ce n'est pas un effet de longueur, mais de **structure au sens de la grille**. Aucune des 79 cibles CR n'a à la fois « Participants » et « Décisions » ; les 35 cibles CT commencent par « Objet » ; LC tombe à 0 en fidélité.
  - Le schéma est le même pour les trois modèles : CO et RD montent, CR, LC et CT baissent.

### 3.4 Jeux v12 à v15 : jeu partiel, taux d'apprentissage, cibles alignées sur la grille (nuit du 19 au 20/10)

- **Hypothèses.**
  1. Sans les tâches mal ciblées, le fine-tuning ne nuit plus.
  2. Un taux plus bas limite l'oubli.
  3. Des cibles conformes à la grille corrigent CR et CT.
  4. Q et generique causent la chute de LC.
- **Jeux.**
  - **v12** = v11 sans CR, CT ni LC (369 lignes).
  - **v13** : CR, CT et LC régénérés par Mistral Large 3 avec des gabarits alignés sur la grille (story S5), validés à 548 sur 592.
  - **v14** = v13 nettoyé (548 lignes ; CR 77/77 avec les quatre sections ; aucun CT ne commence par « Objet »).
  - **v15** = v14 sans Q ni generique (379 lignes).
  - **v16** : 505 paires ORPO tirées de v14 (base Qwen3.5-0.8B).
- **Essai de Mistral Large 4** (préversion). Il consomme 4 000 à 5 600 tokens de raisonnement par CR, finit en ReadTimeout à 180 s puis en 429. Bilan : 39 CR sur 80 pour environ 3 €. **Abandonné** (`IA/archive/run-autonome-2026-10-19.md`, 04:28).
- **Résultats** (v1.1, Claude, `IA/archive/run-autonome-2026-10-19.md`) :

  | Run | Q | RD | CR | LC | CO | RE | CT | NR | Qualité | Baseline |
  |---|---|---|---|---|---|---|---|---|---|---|
  | MiniCPM M1 v12 (partiel) | 0,0 | 85,6 | 30,5 | 0,0 | 81,2 | 32,9 | 43,3 | 20,0 | 36,7 | 41,1 |
  | MiniCPM M1 v12, lr 1e-4 | 0,0 | 84,4 | 32,2 | 0,0 | 71,5 | 34,9 | 40,0 | 20,0 | 35,4 | 41,1 |
  | MiniCPM M1 v14 | 1,7 | 83,2 | 33,9 | 0,0 | 74,1 | 31,9 | 46,7 | 16,7 | 36,0 | 41,1 |
  | MiniCPM M1 v14, graine 4321 (E1) | 0,0 | 86,2 | 29,1 | 0,0 | 77,4 | 29,8 | 46,7 | 20,0 | 36,2 | 41,1 |
  | MiniCPM M1 v15 | 5,0 | 76,9 | 32,0 | 0,0 | 72,6 | 35,5 | 46,7 | 16,7 | 35,7 | 41,1 |
  | Qwen3.5-2B M1 v14 | 0,0 | 65,4 | 22,0 | 0,0 | 84,0 | 30,4 | 33,3 | 40,0 | 34,4 | 36,0 |
  | **Qwen3.5-0.8B M1 v14** | 0,0 | 65,3 | 14,0 | 4,0 | 73,3 | 28,1 | 46,7 | 10,0 | **30,2** | 27,5 |

  La ligne graine 4321 vient de `IA/archive/run-autonome-2026-10-20.md`.

- **Écart à la Baseline, MiniCPM M1 v14 sur v1.1** (bootstrap) : −5,0 [−9,2 ; −1,2] (`IA/e1-variance.md`). La baisse est réelle.
- **Qwen3.5-0.8B v14 sur dev1** : 34,7 contre 36,8 (−2,1 [−6,6 ; +2,1]). Le gain de +2,7 sur v1.1 n'était pas significatif (`IA/archive/run-autonome-2026-10-20.md`, 22:20).
- **Apprentissages.**
  - Sans données CT, **CT remonte** de 13,3 à 43,3 : les cibles CT de v11 nuisaient.
  - **LC tombe à 0 et CR à 30,5 sans aucune donnée LC ni CR.** Le fine-tuning dégrade les tâches absentes du jeu. Le 0 de LC vient de la fidélité (19 items sur 25 à 0) : le fine-tuning rend la réécriture plus libre.
  - Diviser le taux par 2 ne change presque rien (36,7 contre 35,4). L'hypothèse d'oubli par le taux n'est pas confirmée **à ce stade**, ce que confirmera la grille T1-T6 (§3.12).
  - Les cibles alignées font monter CT (13,3 → 46,7) et CR (21,7 → 33,9) par rapport à v11, sans atteindre la base.
  - L'hypothèse « Q et generique causent LC » est réfutée (v15).
  - Sur 8 cibles LC de v14 relues : 1 fidèle, 3 avec ajouts mineurs, 4 à 0 (obligation reformulée, condition supprimée, conseil ajouté).
  - Il y avait un écart entre entraînement et évaluation : consigne d'Agent absente à l'entraînement, entrées 2 à 3 fois plus courtes.

### 3.5 M3 DoRA et M4 ORPO sur Qwen3.5-0.8B (20/10)

Seul M1 Qwen3.5-0.8B v14 dépassait sa Baseline v1.1. La règle de suite a donc déclenché M3 et M4 (`IA/archive/run-autonome-2026-10-19.md`, 05:13 à 06:13 ; `IA/diagnostic-c3.md`, `IA/diagnostic-c4.md`).

- **M3 DoRA** (`runs/train/20261020-051347-m3-dora-qwen3.5-0.8b-v14-1f18`, 25 min). L'export échoue d'abord sur une « valeur non finie » dans `linear_attn.in_proj_qkv`.
  - Cause (C3) : 14 lignes nulles de la base bf16 donnent une norme DoRA nulle, d'où des NaN. Corrigé par `norme_dora_sure`.
  - Export `20261020-075847-ft-qwen3.5-0.8b-e69a` réussi, puis purgé le 21/10.
  - **Notation : non retrouvée** (aucune notation de ce M3 dans `runs/eval-notation/`).
- **M4 ORPO** (paires v16, 2 048 tokens). Il échoue au démarrage sur « CUDA driver error: device not ready ».
  - Cause (C4) : l'`ORPOTrainer` de TRL 1.13 ne borne pas la longueur. 177 paires sur 505 dépassent 2 048 tokens, et les logits du vocabulaire de 248k débordent en mémoire partagée WDDM (15,4 Gio alloués).
  - Correctif : les paires trop longues sont écartées (328 gardées sur 505). 5 pas sont prouvés, à environ 77 s par pas, toujours en débordement.
  - **Run complet jamais lancé** (non retrouvé).
- **Apprentissages.**
  - Sur 6 Go de VRAM, l'ORPO des modèles à grand vocabulaire n'est pas praticable sans calcul des logits par morceaux.
  - Les paires « cible = choisie, base = rejetée » vont dans le **mauvais sens** pour LC, CR et NR, où la base est meilleure (`IA/plan-methodo-2026-10-20.md` §1). La méthode M4 n'a donc jamais été testée dans de bonnes conditions.

### 3.6 Méthodologie v2, étage 1 : génération vérifiée (jeux v17 et v18, 20/10)

- **Hypothèse** (`IA/plan-methodo-2026-10-20.md`). Les cibles font le résultat, pas la méthode. Il faut « générer, vérifier, sélectionner » et aligner entraînement et évaluation.
- **Mise en œuvre.**
  - Tests déterministes nourris par les faits du seed. CR : décisions et actions avec responsable et échéance, aucun nom ni date hors des notes. LC : marqueurs de condition et d'obligation conservés, aucun nombre nouveau. CT : blocs dans l'ordre.
  - Juge de données DeepSeek V4 Pro (grilles `config/prompts/juge-donnees/{cr,lc,ct}.md`, environ 0,005 € par candidat).
  - Régénération par Mistral en 3 essais au plus, avec seulement des phrases fixes par critère et des extraits exacts. Aucun texte libre du juge n'est transmis (exigence D1, correctif de la revue O6b).
  - Consignes d'Agent ajoutées dans les entrées (O5) ; seed LC aligné sur 195 à 361 mots.
- **Calibrage sur les cibles v14.** CR 40/80 retenues (inventions 32), CT 23/35, **LC 0/80**. Les cibles v14 inventent ou trahissent la source dans une large part (`IA/archive/run-autonome-2026-10-20.md`, 09:01).
- **Jeux obtenus.** Après régénération : CR 64/80, CT 30/35, **LC 5/80**, avec 44 refus pour infidélité après 3 essais. **Mistral Large 3 ne corrige pas ses infidélités LC** sur des sources de 195 à 361 mots. Les contrôles « gain de lisibilité » et « modalité perdue » ont été rendus non bloquants par item.
  - **v17** : 468 lignes (CO 34, CR 64, CT 30, LC 5, Q 95, RD 132, RE 34, generique 74).
  - **v18** : nettoyage de v17, 468 lignes (`runs/data-build/20261020-125334-nettoyage-440e`).
- **Résultats** (dev1, GLM, `IA/archive/run-autonome-2026-10-20.md`, `IA/dev1-minicpm.md`) :

  | Run | Q | RD | CR | LC | CO | RE | CT | NR | Qualité | Écart (IC95) |
  |---|---|---|---|---|---|---|---|---|---|---|
  | MiniCPM Baseline | 15,0 | 74,8 | 75,3 | 50,0 | 72,1 | 58,5 | 45,0 | 45,0 | 54,5 | — |
  | MiniCPM M1 v14 | 10,0 | 82,3 | 51,9 | 15,0 | 78,5 | 33,4 | 50,0 | 55,0 | 47,0 | −7,5 [−12,3 ; −1,4] |
  | MiniCPM M1 v18 | 15,0 | 84,8 | 40,4 | 30,0 | 82,5 | 40,7 | 45,0 | 40,0 | 47,3 | −7,2 [−11,8 ; −1,4] |
  | Qwen 0.8B Baseline | 5,0 | 54,3 | 39,7 | 35,0 | 74,9 | 28,1 | 32,5 | 25,0 | 36,8 | — |
  | Qwen 0.8B M1 v18 | 0,0 | 55,6 | 35,3 | 15,0 | 77,0 | 29,7 | 31,6 | 10,0 | 31,8 | −5,0 [−10,3 ; +0,3] |

- **Apprentissages.**
  - Des cibles vérifiées ne suffisent pas : v18 fait comme v14. Sur MiniCPM, seul **CO** gagne de façon significative (+10,4 [+4,9 ; +16,3]).
  - CR (−34,9) et RE (−17,8) perdent de façon significative.
  - Une cible « plausible » n'est pas une cible « juste au sens de la grille ».

### 3.7 Diagnostic D0 (lecture seule, 0 €, nuit du 20 au 21/10)

Source : `IA/diagnostic-d0.md`, comparaison de la Baseline et de v18 sur dev1.

- **Inventions CR et RE.**
  - CR `sans_invention` passe de 66,7 (12/18) à 10,5 (2/19). Cela explique environ 80 % de la perte CR (−28,1 sur −34,9).
  - RE « fidèles » passe de 13/20 à 3/20, alors que la couverture RE **monte** de 52,1 à 66,5.
  - Inventions par item : CR 0,72 → 2,39 ; RE 0,60 → 2,05. Au moins 4 items CR présentent un piège du jeu (rectificatif) comme une décision.
  - Lecture : v18 a appris le style riche de Mistral (sections, attributions, précisions), que le juge compte comme invention.
- **Boucles CT.**
  - 13 sorties CT de v18 sur 20 s'arrêtent à 1 024 tokens. Ce sont des **boucles** dans le bloc d'en-tête : 4-grammes répétés à 0,85-0,97, une même ligne d'emplacement répétée 12 à 125 fois. La base finit toujours (137 à 348 tokens).
  - Cause probable : les 20 consignes CT de dev1 imposent « exactement ces libellés », mais aucun des 30 prompts CT d'entraînement ne le fait, et les cibles Mistral emploient leurs propres libellés en gras.
  - L'impact sur le score est nul, puisque la conformité est à 0/20 pour les deux modèles. Le défaut est pourtant réel en usage.
- **Plafond de Q.**
  - La page attendue figure dans les 5 passages pour 15 items sur 17 ; les éléments clés présents dans les passages font 49/69 (71 %).
  - Avec 8 passages, on passerait à 57/69 éléments et 9/17 items complets.
  - Mais sur les 6 items à couverture complète, un seul réussit : le goulot est aussi la génération.
  - Les 3 items `sans_reponse` sont à 0 pour tous les modèles. Les scores hors corpus (0,55-0,67) se mêlent à ceux du corpus (0,60-0,79), si bien que le seuil 0,5 ne déclenche jamais l'abstention.
  - **Le plafond Q (15 %) n'est pas un effet du fine-tuning** : la Baseline a le même profil.

### 3.8 Interpolation de l'adaptateur et déploiement LoRA GGUF (E7, nuit du 20 au 21/10)

- **Hypothèse.** Un adaptateur dilué garde CO et RD sans les inventions.
- **Mise en œuvre.** Story 15.6 : `export lora`, puis `lora:<id>@<échelle>` dans llama-server avec `--lora-scaled`, sur la base Q4_K_M. Adaptateur v18 de 588 tenseurs, 50 Mo. DoRA, rsLoRA et PiSSA sont refusés à l'export.
- **Test de déploiement.** LoRA à l'échelle 1 sur Q4 contre fusion f16 puis Q4 : 47,4 contre 47,3 (+0,1 [−4,2 ; +4,1]) (`IA/e5/deploiement-lora1.md`).
- **Mesure CPU** (q4_k_m, 4 threads, bge-m3 compris) :
  - base : 4,12 Go, 12,1 t/s ;
  - base + LoRA : 4,13 Go, **10,8 t/s (−11 %)**, premier token 0,72 s.
- **Résultats** (dev1, GLM, `IA/archive/run-autonome-2026-10-20-21-nuit.md`, `IA/e5/e7-*.md`) :

  | Échelle | Q | RD | CR | LC | CO | RE | CT | NR | Qualité | Écart (IC95) |
  |---|---|---|---|---|---|---|---|---|---|---|
  | 1 (sur Q4) | 20,0 | 82,3 | 52,3 | 25,0 | 81,2 | 43,1 | 35,0 | 40,0 | 47,4 | −7,1 [−11,6 ; −1,5] |
  | 0,5 | 15,0 | 79,7 | 59,0 | 30,0 | 77,0 | 43,6 | 42,5 | 45,0 | 49,0 | −5,5 [−9,7 ; +0,0] |
  | 0,25 | 20,0 | 82,3 | 64,8 | 40,0 | 75,1 | 60,8 | 42,5 | 55,0 | 55,1 | +0,6 [−3,5 ; +5,4] |

- **Décision.** Aucune échelle n'est retenue. L'échelle 0,25 passe la Qualité, mais les bornes basses de CR, LC et RE sont sous −10.
- **Confirmation sur dev2** (harnais v2, 22/10). L'échelle 0,25 fait 50,6, soit −5,0 [−9,5 ; −0,1] : **non confirmée**. Sur dev1 en harnais v2, elle faisait 55,4, soit +2,4 [−1,5 ; +7,1] (`IA/run-autonome.md`).
- **Apprentissage.** L'atténuation ramène au niveau de la base sur dev1, mais ne tient pas sur des items neufs. C'est un indice de sur-ajustement des décisions sur dev1, ou de bruit à 20 items par tâche.

### 3.9 Routage par tâche (E5) et mesure finale v1.1

- **Hypothèse.** Utiliser la base partout et l'adaptateur seulement là où il gagne significativement.
- **Choix sur dev1** (`IA/e5/e5-minicpm.md`, `IA/e5/e5-qwen.md`) :
  - MiniCPM : seul **CO** est routé, vers M1 v18 (+10,4 [+4,9 ; +16,3] ; v14 donne +6,4 [+2,6 ; +10,7]).
  - Qwen3.5-0.8B : aucune tâche routée (la borne basse de CT v14 vaut +0,0, pas > 0).
- **Composition dev1** (`20261020-230351-compose-0d5a`) : 54,5 → **55,8** (+1,3 [+0,6 ; +2,0]).
- **Mesure finale v1.1**, items CO seuls, les autres tâches de v1.1 n'étant pas consultées :
  - CO **58,9 → 78,7** (+19,8 [+10,4 ; +30,5]) ;
  - Qualité composée **43,6** contre 41,1 (+2,5 ; la recette du 21/10 donne 43,54) ;
  - runs `20261021-033754-lora-minicpm5-2b-ce8b` et `20261021-033910-lora-minicpm5-2b-36d9`, détail dans `IA/e5/v11-co-lora.md`.
- **Confirmation sur dev2** (harnais v2, GLM, 22/10) : CO **+12,4 [+5,6 ; +18,7]**, autres tâches inchangées, Qualité 57,1 contre 55,6 (+1,5 [+0,7 ; +2,3]), run `20261022-061137-compose-34c1`. **Routage CO confirmé** selon la règle écrite avant calcul. Sur dev1 en harnais v2 : 54,1 (+1,1 ; CO +9,1).
- **Apprentissage.** Un adaptateur spécialisé, appliqué seulement à la tâche où il gagne, est la seule configuration qui améliore le système. Le gain total reste modeste, puisqu'il ne porte que sur 1 tâche sur 8.

### 3.10 Témoin sans CR, LC ni RE (jeu v19) et sélection de candidats (jeu v20)

- **Hypothèse du témoin.** Si les pertes CR, LC et RE viennent des cibles de ces tâches, un jeu qui ne les contient pas ne les perd pas.
  - **v19** = v18 sans CR, LC ni RE, soit 365 lignes (`runs/data-build/20261020-224334-sous-ensemble-6d33`).
  - Résultat sur dev1 : 50,4 contre 54,5 (−4,1 [−8,5 ; +1,1]) ; **CR −25,9 [−41,0 ; −10,4] sans aucune ligne CR**, CO +12,1 (`IA/e5/temoin-v19.md`).
- **Hypothèse de la sélection** (étage 2, O2 et O3). Mettre la base en candidate : sa sortie devient la cible quand elle gagne.
  - Candidats CR : 64 de Mistral et 125 de la base, à températures 0,3 et 0,7. Candidats LC : 5 de Mistral, 10 de la base et 5 de DeepSeek.
  - Jugement DeepSeek (1,17 €) : CR 100/189 acceptés, LC 5/19.
  - **v20** : 433 lignes. CR 64 retenues (45 de Mistral, 19 de la base), LC 4, **RE retirée** (34 lignes), car la grille de jugement de données ne couvre pas RE (`runs/data-build/20261021-004859-selection-0193`).
  - Résultat sur dev1 : 46,3 contre 54,5 (−8,1 [−12,4 ; −2,7]) ; CR −25,6 malgré 19 cibles de la base ; **RE −21,6 [−36,4 ; −7,0] alors que RE est absente du jeu** ; LC −35 ; CO +9,8 (`IA/e5/v20.md`).
- **Apprentissage, central.** Les pertes CR, LC et RE viennent d'une **dérive générale de l'adaptateur** (la force de l'adaptation), pas des cibles de ces tâches. Corriger ou sélectionner les cibles ne suffit pas.

### 3.11 Modèles hors fine-tuning mesurés pour la décision

| Modèle | Mesure | Source |
|---|---|---|
| qwen-4b (Qwen3-4B) | 8,47 Go de RAM, 5,6 t/s CPU, NFR-1, 2, 3 et 6 non conformes ; tokenizer incompatible avec Qwen3.5 (pas de distillation des logits possible) | `IA/archive/run-autonome-2026-10-20-21-nuit.md`, 03:26 ; `PA/stories-epic-16-derive-et-confirmation.md` |
| Qwen3.5-4B | 54,6 sur dev1 (hors règle de taille) | `IA/run-autonome.md` |
| EuroLLM-1.7B | Baseline seulement : template sans outils, RD 0 | `PA/decisions.md` D8 |
| Granite 4.0 H (Mamba) | abandonnés : 122 min de bench GGUF contre 73 pour le dense, sans gain de qualité (32,5 contre 33,4) | `PA/decisions.md` D8 |
| Décodage spéculatif (CPU) | ralentit : 8,0 t/s avec brouillon MiniCPM5-1B (5,59 Go), 12,7 t/s en ngram, contre 15,0 sans | `IA/etat-run-2026-10-19-portable.md`, 11:01 |

### 3.12 Essais contre la dérive, T1 à T6 (nuit du 21 au 22/10)

- **Hypothèse.** L'adaptateur v18 déplace trop la base (environ 58 pas, rang 16, lr 2e-4). Un adaptateur **entraîné** moins agressif, ou régularisé vers la base, garderait CO sans perdre CR, LC et RE.
- **Mise en œuvre.** Le jeu prévu était v21 (CT aligné), mais il est **bloqué par D1** : il n'existe aucune formulation d'origine non-Claude pour la consigne de libellés. Les essais tournent donc sur **v18**, avec T0 = M1 v18 existant. Le rapport alpha/rang est constant à 2, et l'évaluation se fait en LoRA GGUF à l'échelle 1, harnais v2, juge GLM. La KL utilise la story 16.6a : perte = entropie croisée + `kl_base` × KL(élève ‖ base), base obtenue en désactivant l'adaptateur, calcul par tranches.
  - Essai de 5 pas : VRAM 4,27 Go, KL moyenne 0,137 pour une entropie croisée de 1,04, d'où `kl_base` = 1,9.
  - T6 prend 42 min (+24 %).
- **Résultats** (dev1, Baseline v2 = 53,0, `IA/run-autonome.md`) :

  | Essai | Rang | Alpha | lr | Époques | Qualité dev1 | Écart (IC95) |
  |---|---|---|---|---|---|---|
  | T1 taux ÷ 4 | 16 | 32 | 5e-5 | 1 | 45,1 | −7,9 [−11,8 ; −2,4] |
  | T2 taux ÷ 2 | 16 | 32 | 1e-4 | 1 | 42,7 | −10,3 [−14,0 ; −5,5] |
  | T3 rang 4 | 4 | 8 | 2e-4 | 1 | 45,7 | −7,4 [−11,3 ; −2,2] |
  | T4 rang 8, taux ÷ 2 | 8 | 16 | 1e-4 | 1 | 44,4 | −8,6 [−12,6 ; −3,6] |
  | T5 demi-époque | 16 | 32 | 2e-4 | 0,5 | 45,0 | −8,0 [−11,8 ; −3,3] |
  | T6 KL vers la base | 16 | 32 | 2e-4 | 1 | 53,3 | +0,3 [−3,4 ; +4,4], CO +2,0 non significatif |

- **Décision.** Aucun essai ne passe la règle : T1 à T5 échouent la non-infériorité, et T6 n'a pas de gain CO.
- **Apprentissages.**
  - Réduire le taux, le rang ou les pas **ne corrige pas la dérive** : même 29 pas environ (T5) ou un taux divisé par 4 perdent 7 à 8 points.
  - La KL vers la base supprime la dérive, mais efface aussi ce que l'adaptateur apprenait.
  - Il n'existe, à ce stade, aucun réglage qui garde le gain sans la perte. Une seule valeur de `kl_base` a été testée.

---

## 4. Apprentissages transverses

| # | Constat | Pourquoi on le pense | Niveau de preuve |
|---|---|---|---|
| 1 | **Le fine-tuning général dérive** : CR, LC et RE baissent, quelle que soit la composition du jeu | Témoin v19 sans CR : CR −25,9. v20 sans RE : RE −21,6. v12 sans LC : LC 0. v4 sans CR : CR varie quand même. Mêmes pertes sur 3 modèles | **Fort** : significatif sur dev1, reproduit sur v1.1 et sur plusieurs jeux |
| 2 | **La qualité des cibles n'explique pas tout** | v14 alignées puis v18 vérifiées : même Qualité dev1 (47,0 et 47,3). La sélection base + Mistral (v20) ne corrige rien | Fort sur MiniCPM5-2B. La sélection n'a été essayée qu'une fois |
| 3 | La qualité des cibles explique une partie | v11 → v14 : CT 13,3 → 46,7, CR 21,7 → 33,9 (v1.1). Cibles CT v11 nuisibles (CT 43,3 sans elles) | Moyen : écarts nets, un seul run par jeu |
| 4 | **Les hyperparamètres ne sont pas le levier** | lr 1e-4 contre 2e-4 : 35,4 contre 36,7. T1-T5 : −7 à −10. DoRA ≤ QLoRA | Fort pour la dérive. Pas de recherche fine autour de la KL |
| 5 | **LC et fidélité** : Mistral Large 3 reformule les obligations, supprime des conditions, ajoute des conseils | v14 : 4 cibles LC sur 8 à 0. Vérification v17 : LC 5/80 retenues après 3 essais. Tous les fine-tunés sont à LC 0 sur v1.1 | Fort. Aucun générateur alternatif autorisé n'a été testé en entier (DeepSeek : 5 candidats) |
| 6 | Le **style du générateur** passe dans le modèle : allongement, préambules, titres en gras, attributions riches comptées comme inventions | Analyses de sorties v2 et v4 ; D0 (inventions par item ×3) | Fort |
| 7 | **Boucles CT** dues à un écart de prompt entre entraînement et évaluation | 13 boucles sur 20 en v18 ; consigne « exactement ces libellés » absente de l'entraînement | Moyen : la cause est probable, l'alignement (v21) n'a pas été testé |
| 8 | **Q limité par la recherche et l'abstention, pas par le fine-tuning** | D0 : 71 % des éléments clés dans les passages, 3 items sans réponse à 0 partout. Base et v18 ont le même profil | Fort pour le constat. k = 8 n'a montré aucun gain mesurable (Baseline v2 : Q 5 sur dev1, 20 sur dev2) |
| 9 | **Le bruit à 20 items par tâche** rend la non-infériorité par tâche sous-puissante (demi-largeur ±10 à ±17) | E7 ; échelle 0,25 retenable sur dev1, rejetée sur dev2 | Fort. Seule une réduction du bruit (plus d'items, ou regroupement dev1 + dev2) changerait cela |
| 10 | **Le routage CO tient** | dev1, v1.1 (+19,8 sur CO) et dev2 (+12,4) | Fort : trois jeux, dont un neuf |
| 11 | La graine d'entraînement compte peu | +0,1 [−2,5 ; +2,6] | Moyen : une seule paire de graines |
| 12 | Une LoRA GGUF à chaud sur Q4 vaut la fusion | 47,4 contre 47,3 ; RAM +0,05 Go ; débit −11 % | Fort |

### 4.1 Pièges opérationnels (à relire avant de relancer)

- **Veille du PC.** Le PC s'est mis en veille de 19 h 53 à 22 h 03 le 21/10, faute de bloqueur. Lancer `veille.ps1` (SetThreadExecutionState) pendant tout travail GPU (`IA/run-autonome.md`).
- **Tâches de fond coupées par Claude Code.** Sous pression mémoire, Claude Code coupe ses tâches de fond : un export monte à environ 22 Go sur 32. Relancer Claude Code avec `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` (`IA/etat-campagne-v11.md`, 20:46).
- **VRAM de 6 Go.** Sous WDDM, un dépassement passe en mémoire partagée au lieu d'un OOM net : c'est lent, puis le pilote échoue avec « device not ready ». Mettre `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` et une garde RAM à 28 Go. ORPO, M2 et Granite 1B au-delà de 3 072 tokens ne tiennent pas.
- **Juge par jeu.** Un jeu `dev*` sans section dans `config/juges.toml` a été noté par le juge de test Claude (3,68 € perdus le 22/10). Vérifier `[jeux.<nom>]` avant toute notation.
- **Options oubliées dans les scripts.** `--quantification` et `--jeu` ont été oubliés deux fois, ce qui a coûté environ 40 min de générations le 22/10.
- **Coût du juge.** Un lot batch dont la création échoue réservait le pire cas : 8,67 € bloqués le 19/10. C'est corrigé (INC-1 à INC-3), avec une estimation avant notation.
- **Réutilisation des réponses journalisées.** Une réponse tronquée (`finish_reason=length`) ne doit jamais être réutilisée, et `max_tokens` doit faire partie de la clé (C2).
- **`eval run --reprendre`.** Un item en erreur compte comme présent, ce qui a causé une double notation (0,64 €). Pour la notation, utiliser `--phase notation --depuis`.
- **Disque.** Chaque export garde environ 9,4 Go d'intermédiaires (`hf-f16`, `modele-f16.gguf`), et le disque a saturé plusieurs fois. Purger avec `export purger --tous-notes`. Le classifieur de permissions refuse les suppressions sans accord explicite.
- **Windows.**
  - `WinError 32` au renommage d'un `.gguf.part` de 5 Go (antivirus) : corrigé par des réessais bornés à 60 s.
  - `slmsp.exe` verrouillé pendant une tâche longue : passer par `python -m slmsp` et `uv run --no-sync`.
- **Fournisseurs.**
  - Mistral Large 4 (préversion) : raisonnement long, timeouts, 429.
  - DeepSeek coupé à 8 000 tokens de raisonnement : `max_tokens` porté à 16 000.
  - GLM sans effort ni schéma rend des sorties vides.
  - Second juge Mistral en limite de débit.
  - Conditions Mistral à revérifier chaque jour, faute de quoi la génération s'arrête à minuit.
- **Run composé.** Il n'a pas d'empreinte de grille, ce qui bloque le regroupement dev1 + dev2 du routage (report du 22/10).

---

## 5. Ce qu'on garde, et ce qui reste ouvert

### 5.1 À garder dans le produit

- **Routage CO, optionnel.** Base MiniCPM5-2B Q4_K_M, avec le LoRA v18 GGUF (`runs/export-lora/20261020-233144-lora-minicpm5-2b-d9f3`) appliqué à l'échelle 1 sur la seule tâche CO. Coût : RAM +0,05 Go, débit −11 % sur CO. Retenu par Anaël le 21/10 et confirmé sur dev2.
- **Garde-fou anti-boucle** (16.3, harnais v2). Il coupe les 13 boucles v18 et aucune sortie de la Baseline : seuils de 12 lignes, 300 mots, 0,8. Il s'applique à tous les modèles, y compris distants.
- **Abstention Q** (16.8). Elle est codée mais **désactivée par défaut**. Ses textes fixes (`config/prompts/q-abstention.toml`) sont à relire par Anaël, puis elle est à mesurer selon la règle écrite : au moins la moitié des items `sans_reponse` en abstention correcte, au plus 1 fausse abstention, une exactitude Q qui ne baisse pas de plus de 5 points. C'est le premier risque produit : réponse inventée à un Agent.
- **Harnais v2** : 8 passages et dédoublonnage du préfixe. Aucun gain mesuré, mais pas de perte.
- **Banc de mesure.** dev1, dev2, `eval comparer` (bootstrap), `eval composer`, juges tiers, juge de données, et les règles de décision écrites avant calcul. Ils resservent tels quels pour comparer des modèles préexistants ou distants.
- **NFR à surveiller.** NFR-3 (p95 du premier token < 5 s) n'est conforme pour aucun modèle local : p95 de 63 à 66 s avec la recherche (`IA/archive/run-autonome-2026-10-20-21-nuit.md`, 02:55).

### 5.2 Ce qui reste ouvert si on reprend

1. **v21 (CT aligné)** est bloqué par D1 : il faut une formulation d'une ligne contenant `{libelles}`, d'origine non-Claude, inscrite dans `[alignement_ct] origines_admises` de `config/donnees.toml`. Ensuite, tester l'effet de l'alignement seul (T0 sur v21).
2. **Complément de données CR** (sorties de la base sans invention). Il a été reporté après les essais contre la dérive, qui ont échoué. Seul, il ne corrigera pas la dérive (§3.10).
3. **Réduire le bruit avant tout nouvel essai.** Agrandir dev1 et dev2, ou les regrouper (corriger d'abord l'empreinte de grille des runs composés). Avec 40 items par tâche, la non-infériorité devient testable.
4. **Méthodes non testées ou non abouties.**
   - ORPO ou DPO sur paires **notées** (meilleur contre moins bon, C5 et E3). Il faut d'abord régler la mémoire des logits sur 6 Go.
   - M2 LoRA bf16 sur une machine de 8 Go ou plus.
   - Balayage de `kl_base` entre 0 et 1,9, pour chercher un point qui garde CO.
   - Adaptateurs par tâche entraînés séparément (le témoin v19 suggère que c'est possible pour CO et RD).
   - Distillation des logits de Qwen3.5-4B vers Qwen3.5-0.8B (même tokenizer).
   - Report de la recette sur d'autres modèles (E6).
5. **Générateur LC alternatif** (E4) : DeepSeek, autorisé par ses CGU. Le test n'a porté que sur 5 candidats.
6. **Mesure CT** : relire le critère de conformité, saturé à 0/20, avant de s'en servir pour décider.
7. **M3 DoRA Qwen3.5-0.8B v14** : entraîné et exporté, mais sa notation n'est pas retrouvée. L'adaptateur est gardé dans `runs/train/`.

---

## 6. Index des runs et fichiers de référence

### 6.1 Documents

| Fichier | Contenu |
|---|---|
| `PA/decisions.md` | D1 (règles bloquantes), D8 (registre des modèles, règle de 2,5 B, bf16, sondes VRAM), D9 (option hybride) |
| `PA/epics.md`, epics 9 à 11 | pipeline de données, `train run` (M1 à M4), Comparatif, essai M1 initial |
| `PA/sprint-change-proposal-2026-10-20.md` | epic 14 (méthodologie v2, correctifs C1 à C9) |
| `PA/stories-epic-15-nuit-2026-10-20.md` | routage, candidats, sélection, LoRA GGUF, dev2 |
| `PA/stories-epic-16-derive-et-confirmation.md` | leviers à 0 €, grille T0 à T6, règles 16.6, 16.7 et 16.8 |
| `IA/baseline-rapport.md` | première Baseline v1.0 (12/10) |
| `IA/enquete-entrainement-hybrides-2026-10-18.md` | VRAM, `prepare_model_for_kbit_training`, Qwen3.5 sous Windows |
| `IA/etat-run-2026-10-17-portable.md`, `IA/etat-run-2026-10-18-portable.md` | Baselines v1.1, sondes |
| `IA/etat-run-2026-10-19-portable.md` | jeux v2 à v11, M1 et M3 v2, M1 v4, ORPO v3, cibles courtes |
| `IA/dossier-relecture-v9.md` | longueurs et comptes v4 → v9 |
| `IA/etat-campagne-v11.md` | M1 v11 sur 3 modèles |
| `IA/archive/run-autonome-2026-10-19.md` | v12 à v16, lr, Large 4, juges tiers, M3 et M4 Qwen |
| `IA/plan-methodo-2026-10-20.md` | méthodologie v2, décisions d'Anaël §7 bis |
| `IA/archive/run-autonome-2026-10-20.md` | E1, juge de données, v17 et v18, dev1 |
| `IA/e1-variance.md`, `IA/e1-bootstrap.md`, `IA/dev1-minicpm.md` | bootstraps v1.1 et dev1 |
| `IA/diagnostic-c3.md`, `IA/diagnostic-c4.md`, `IA/diagnostic-c7.md` | DoRA NaN, ORPO VRAM, juges tiers en échec |
| `IA/plan-nuit-2026-10-20.md`, `IA/archive/run-autonome-2026-10-20-21-nuit.md` | D0, E5, E7, témoin, v20, qwen-4b |
| `IA/diagnostic-d0.md` | inventions CR et RE, boucles CT, plafond Q |
| `IA/e5/` | `e5-minicpm.md`, `e5-qwen.md`, `deploiement-lora1.md`, `e7-*.md`, `temoin-v19.md`, `v20.md`, `v11-co-lora.md` |
| `IA/run-autonome.md` (fin) | T1-T6, confirmation dev2, bilan du 22/10 |
| `IA/journal-decisions-nuit.md` | décisions d'architecture (paires ORPO, masque, D1 en quatre verrous) |
| Mémoire `methodo-v2.md` | résumé des étapes du 20 au 22/10 |

### 6.2 Runs d'entraînement (`runs/train/`)

| Run | Méthode, jeu | Résultat |
|---|---|---|
| `20261018-231156-…-85d8`, `20261018-233341-…-aa7d` | validation fp32-kbit / bf16, 100 pas | même perte |
| `20261019-000939-m1-qlora-minicpm5-2b-4423` | M1 v2 | v1.1 35,6 |
| `20261019-011031-m3-dora-minicpm5-2b-b9bb` | M3 v2 | v1.1 31,8 |
| `20261019-030205-…-263d`, `…-053013-…-8742`, `…-053250-…-b525` | M4 ORPO v3 (8192, 4096, 2048) | OOM ou tués |
| `20261019-081352-essai-qwen35-2b-e2c9` | essai Qwen3.5-2B, 20 pas | chemin validé |
| `20261019-084321-m1-qlora-minicpm5-2b-v4-53fc` | M1 v4 | v1.1 38,9 |
| `20261019-195316-…-v11-e3e4`, `…-201519-…qwen3.5-2b-v11-af61`, `…-212023-…qwen3.5-0.8b-v11-b7c4` | M1 v11 | 32,6 / 32,8 / 24,9 |
| `20261019-215640-…-v11-partiel-7a6e` | M1 v12 | 36,7 |
| `20261019-231422-…-v12-lr1e4-b5e6` | M1 v12, lr 1e-4 | 35,4 |
| `20261020-005124-…-v14-fab9`, `…-064228-…-v14-graine4321-a7d1` | M1 v14 (2 graines) | 36,0 / 36,2 ; dev1 47,0 |
| `20261020-020612-…qwen3.5-2b-v14-c6a9` | M1 v14 | 34,4 |
| `20261020-030433-…-v15-cbdf` | M1 v15 | 35,7 |
| `20261020-042850-…qwen3.5-0.8b-v14-4346` | M1 v14 | v1.1 30,2 ; dev1 34,7 |
| `20261020-051347-m3-dora-qwen3.5-0.8b-v14-1f18` | M3 v14 | notation non retrouvée |
| `20261020-061130-…-b90c`, `…-061248-…-a0b4` | M4 ORPO v16 | device not ready |
| `20261020-125424-…-v18-82ef` | M1 v18 MiniCPM | dev1 47,3 ; LoRA du routage CO |
| `20261020-151705-…qwen3.5-0.8b-v18-fa23` | M1 v18 Qwen 0.8B | dev1 31,8 |
| `20261020-224411-…-v19-sous-ensemble-8a7d` | témoin v19 | dev1 50,4 |
| `20261021-012949-…-v20-selection-60b2` | M1 v20 | dev1 46,3 |
| `20261021-224834-…-t1-4ac0` … `20261022-012713-…-t6-8807` (et `…-kl-essai-7ab0`) | T1 à T6 sur v18 | dev1 42,7 à 53,3 |

### 6.3 Notations et compositions clés

| Mesure | Runs |
|---|---|
| Baseline MiniCPM5-2B v1.1 | `runs/eval-notation/20261018-112201-minicpm5-2b-e6f2` |
| Baseline MiniCPM5-2B dev1, harnais v1 | génération `20261020-163743-minicpm5-2b-f9fc`, notation `20261020-165745-minicpm5-2b-afd3` |
| Baseline MiniCPM5-2B, harnais v2 | dev1 `20261022-025237-minicpm5-2b-fb47` (génération `20261022-020909-…-4d6d`) ; dev2 notation `20261022-055524-minicpm5-2b-01f1` (génération `20261022-023026-…-ec6a`) |
| M1 v18 sur dev1 | génération `20261020-175424-ft-minicpm5-2b-35b9`, notation `20261020-181808-ft-minicpm5-2b-213f` |
| LoRA v18 à l'échelle 1 sur Q4 (déploiement) | `runs/eval-notation/20261021-002259-lora-minicpm5-2b-456f` |
| Routage CO | dev1 `20261020-230351-compose-0d5a` ; v1.1 `20261021-033910-lora-minicpm5-2b-36d9` ; dev2 `20261022-061137-compose-34c1` (CO `20261022-061117-lora-minicpm5-2b-d154`) |
| Échelle 0,25 sur dev2 | `20261022-060230-lora-minicpm5-2b-c0a9` |
| Notations dev2 avec le juge Claude, **à écarter** | `20261022-053207-…-d828`, `20261022-054028-…-bd32` |
| Mesures CPU | base `runs/measure/20261021-023836-h-ram-f89e` ; base + LoRA `20261021-024545-h-ram-31af` ; qwen-4b `20261021-030201-h-ram-4e18` |

### 6.4 Builds de jeux (`runs/data-build/`)

| Jeu | Build |
|---|---|
| v4 | `20261019-084237-nettoyage-7b09` |
| v5 (paires) | `20261019-101146-preferences-8576` |
| v9 | `20261019-173901-nettoyage-3ed6` |
| v11 | `20261019-194543-nettoyage-c782` |
| v12 | `20261019-215607-sous-ensemble-bfcf` |
| v14 | `20261020-005014-nettoyage-6fc8` |
| v15 | `20261020-023752-sous-ensemble-acee` |
| v17 | `20261020-125304-build-90b1` |
| v18 | `20261020-125334-nettoyage-440e` |
| v19 | `20261020-224334-sous-ensemble-6d33` |
| v20 | `20261021-004859-selection-0193` |

Autres runs : candidats `runs/data-candidats/20261020-232707-candidats-a5fd`, jugement `runs/data-juger/20261021-000207-juger-6e70`. Builds de v1, v2, v3 et v16 : non retrouvés sous ce format dans les fichiers lus.
