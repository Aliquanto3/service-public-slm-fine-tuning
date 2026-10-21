# Epic 16 — Leviers à 0 €, essais contre la dérive de l'adaptateur, confirmation sur dev1 + dev2

Sources : bilan et décisions d'Anaël du 21/10 (fin de `../implementation-artifacts/run-autonome.md`, entrées de 05:36 et 05:41) ; `../implementation-artifacts/diagnostic-d0.md` (leviers 3 et 5). Consignes des sous-agents : `../implementation-artifacts/consignes-sous-agents-2026-10-20.md` (inchangées : worktrees, D1, aucun appel payant par un sous-agent, pas de suite complète locale).

Constat de départ : les pertes CR, LC et RE viennent d'une **dérive générale de l'adaptateur**, pas des cibles. Seules l'atténuation (LoRA v18 à 0,25 : 55,1 sur dev1, Baseline 54,5) et le routage (base + LoRA v18 sur CO : 55,8 sur dev1, 43,6 contre 41,1 sur v1.1) tiennent.

| Story | Titre | Nature |
|---|---|---|
| 16.1 | dev2 : relance unique des 5 items rejetés, puis exclusion et gel | orchestrateur (mixte) |
| 16.2 | Q : 8 passages et dédoublonnage du préfixe des chunks (harnais v2) | code |
| 16.3 | CT : prompts d'entraînement alignés et garde-fou anti-boucle | code |
| 16.4 | `eval composer` accepte un run routé partiel (report du 21/10) | code |
| 16.5 | `eval comparer` sur jeux regroupés (dev1 + dev2) | code |
| 16.6a | Régularisation KL vers la base (auto-distillation) dans l'entraîneur | code |
| 16.6 ★ | Essais contre la dérive : taux, rang, pas, KL vers la base | runs GPU (protocole relu par Anaël) |
| 16.7 | Confirmation de l'échelle 0,25 et du routage CO sur dev1 + dev2 | runs |

Hors epic : complément de données CR (sorties de la base sans invention), **après** 16.6 (décision 4 du 21/10) ; abstention Q (levier 4 de D0) ; paires C5, E3, E6 ; toute mesure finale v1.1 (v1.1 n'est pas consulté dans cet epic).

Distillation (échange du 21/10) : CGU relues le 21/10. Mistral (texte) et DeepSeek (distillation citée, §4.2) l'autorisent ; **Z.ai (GLM) interdit d'entraîner sur ses sorties, et Kimi interdit tout modèle « potentiellement concurrent »** : GLM reste juge des seuls jeux `dev*`, aucun verdict ni texte GLM ou Kimi n'entre dans un jeu d'entraînement ni dans une sélection de cibles. La distillation des logits d'un 4B vers Qwen 0.8B est hors epic, à décider d'après la mesure de qwen-4b sur dev1 (lancée le 21/10). Attention : `qwen-4b` est Qwen3-4B (vocabulaire de 151 643 entrées) et Qwen3.5-0.8B/2B ont un autre tokeniseur (248 044 entrées) ; une distillation des logits demanderait Qwen3.5-4B.

## Règles de décision (écrites avant tout calcul)
Mêmes conventions que l'epic 15 : bootstrap apparié par `eval comparer`, IC95, juge GLM sur `dev*`, second juge désactivé (15.4), génération sur GPU, charge sur CPU.
- **Non-infériorité (règle E7)** : aucune tâche avec une borne basse < −10 contre la Baseline, et Qualité ≥ Baseline − 2.
- **16.6, configuration retenue** : passe la non-infériorité sur dev1 **et** garde le gain CO (borne basse CO > 0 contre la Baseline) ; parmi celles qui passent, la meilleure Qualité. Elle remplace le routage CO comme recommandation seulement si sa Qualité dev1 ≥ celle du routage CO − 1 (un modèle unique évite la bascule d'adaptateur par tâche) ; sinon elle est rapportée sans changer la recommandation. Décision définitive après dev2 (16.7). *Seuil « − 1 » à valider par Anaël à la relecture du protocole.*
- **16.7, routage CO confirmé** si, sur dev2 seul, la borne basse CO > 0 contre la Baseline et aucune autre tâche ne bouge (le routage n'y touche pas : contrôle de cohérence). **Échelle 0,25 confirmée** si la non-infériorité tient sur dev2 seul. dev2 tranche (jamais consulté pour choisir) ; le regroupement dev1 + dev2 est rapporté pour la précision, il ne tranche pas.
- Contrat partagé : la version du harnais passe à **2** (16.2 porte l'incrément, 16.3 ajoute sa section sans réincrémenter). Toute comparaison de 16.6 et 16.7 se fait entre runs du harnais v2 ; aucun run v1 n'est mélangé à un run v2.

## 16.1 — dev2 : relance unique, puis exclusion et gel (décision d'Anaël, 21/10)
Items : CO-609, CO-615, CT-602, CT-612, CT-614 (état et griefs : `../implementation-artifacts/spec-15-5b-dev2-corrections.md`).
- **Relance unique en l'état** de la vérification DeepSeek + GLM sur ces 5 items (mêmes consignes v3, pas de modification du texte ; ~0,05 €, lancée par l'orchestrateur). Le motif de la relance (griefs inexacts ou de convention) est consigné.
- Item retenu par les deux juges : réintégré. Item encore rejeté : **exclu, cibles abaissées** pour sa tâche (règle de CR-521 dans dev1), sans remplacement ni nouvelle relance.
- Puis **gel `relu-llm`** de dev2 (manifeste de gel, effectifs par tâche consignés).
- Aucun run de génération ou de notation sur dev2 avant le gel ; personne ne lit de sortie de modèle sur dev2 avant 16.7.
- Fini quand : dev2 gelé, effectifs par tâche au manifeste, décision par item journalisée dans `run-autonome.md`.

## 16.2 — Q : 8 passages et dédoublonnage du préfixe (harnais v2)
Levier 3 de D0 (rejeu : éléments clés dans les passages 49 → 57/69, items complets 6 → 9/17, page attendue 15 → 16/17 ; contexte ~2 k → ~3,3 k tokens, budget 7 168).
- `config/index.toml` : `k = 8` (source unique, lue aussi par l'application ; seuil de pertinence inchangé à 0,5).
- **Dédoublonnage à l'assemblage** (pas de reconstruction de l'Index) : entre passages d'une même page, le préfixe commun titre + introduction n'est gardé que dans le premier ; il est retiré des suivants. Le préfixe vient des métadonnées du chunk si elles le portent, sinon du plus long préfixe commun aux chunks de la page, avec un minimum de longueur en configuration. Le champ `extrait` des Sources porte le texte propre à chaque passage (aujourd'hui identique pour les 5 passages de F17317).
- `borner_passages` reste en place ; l'ordre des passages et la numérotation des Sources ne changent pas.
- Version du harnais à 2, consignée dans chaque run de génération ; `eval comparer` refuse de comparer deux runs de versions de harnais différentes (ou avertit avec `--autoriser-jeux-differents`, comme pour les jeux).
- Fini quand : tests sur fixtures (préfixe retiré des seuls passages suivants d'une même page, page à un seul passage intacte, préfixe trop court ignoré, `extrait` propre, version consignée, refus du mélange v1/v2) ; rejeu D0 par l'orchestrateur sur les 20 items Q de dev1 (0 €, bge-m3 CPU) qui retrouve 57/69 ; mesure CPU du premier token sur la base (prompt plus long, `measure run`).

## 16.3 — CT : prompts d'entraînement alignés et garde-fou anti-boucle
Levier 5 de D0 : 13/20 sorties CT de v18 bouclent dans le bloc d'en-tête ; 20/20 consignes CT d'évaluation imposent « exactement ces libellés », 0/30 prompts CT d'entraînement.
**Story à risque D1 : relire la spec avant le code** (la formulation ajoutée au prompt ne doit pas être un texte rédigé par Claude).
- **Données (0 €, déterministe)** : nouvelle version de build **v21** = v18 où chaque prompt CT reçoit la consigne de libellés, avec **les libellés extraits de la cible Mistral de la ligne** (le prompt s'aligne sur la cible : aucune cible réécrite, aucun appel). Formulation : reprise d'un gabarit existant d'origine non-Claude, sinon question à Anaël avant le code. Les autres tâches de v18 sont copiées telles quelles ; MANIFEST v21 avec la transformation et le compte de lignes touchées (30 attendues).
- **Décodage (harnais v2, section `[anti_boucle]`)** : arrêt déterministe quand une même ligne non vide revient au-delà d'un seuil, ou quand la part de 4-grammes répétés sur une fenêtre dépasse un seuil (seuils en configuration). La sortie est coupée avant la répétition et marquée `raison=boucle` ; aucune pénalité de répétition (les sorties qui ne bouclent pas restent identiques octet pour octet, d'où une Baseline comparable). S'applique à tous les modèles.
- La mesure CT reste rapportée **saturée** (conformité 0/20 y compris pour la base) : elle ne sert pas à trancher ; le nombre de boucles en est l'indicateur.
- Fini quand : tests (extraction des libellés, prompt v21 attendu, lignes non CT inchangées, MANIFEST) ; le garde-fou rejoué sur les sorties réelles de dev1 coupe les 13 boucles de v18 et aucune des 20 sorties CT de la Baseline (ni aucune autre sortie de la Baseline dev1) ; build v21 produit et relu par Anaël avant tout entraînement (16.6).

## 16.4 — `eval composer` : run routé partiel (report du 21/10)
Le 21/10, `eval composer` a refusé la composition v1.1 du routage CO (run routé généré avec `--items` sur les 15 items CO seulement) ; la Qualité 43,6 a été calculée à la main.
- Un run **routé** peut ne couvrir que les tâches qu'il route : pour chaque tâche routée, sa liste d'items doit être **égale** à celle du run par défaut pour cette tâche ; les tâches qu'il ne couvre pas ne peuvent pas lui être routées (refus clair). Les autres motifs de refus de 15.1 (jeu et version, grille, juge principal, version des prompts, statut `ok`, et désormais version du harnais) s'appliquent tâche par tâche.
- La provenance du run composé indique pour chaque tâche le run source et s'il était partiel.
- Fini quand : tests (routé partiel accepté, tâche routée absente refusée, liste d'items différente refusée, provenance) ; recette par l'orchestrateur : recomposer v1.1 à partir des runs du 21/10 (`20261021-033910-lora-minicpm5-2b-36d9` sur CO, Baseline `20261018-112201-minicpm5-2b-e6f2`, marque `deja-consulte`) retrouve **43,6** (0 €, aucun appel au juge).

## 16.5 — `eval comparer` sur jeux regroupés
- `eval comparer` accepte plusieurs paires de runs sur des jeux différents (par exemple `--paire A_dev1 B_dev1 --paire A_dev2 B_dev2`) : bootstrap apparié **stratifié par jeu et par tâche** (items rééchantillonnés dans leur jeu), Qualité regroupée = moyenne des Scores de Tâche calculés sur l'union des items. Chaque paire doit passer les contrôles actuels (même jeu, même juge, même version de harnais) ; les deux paires doivent avoir le même juge principal et la même grille.
- Le rapport donne dev1, dev2 et le regroupement côte à côte.
- Fini quand : tests sur fixtures (stratification, union, refus si juges ou grilles diffèrent entre paires, une seule paire = comportement actuel inchangé).
- Même zone de code que 16.4 (CLI `eval`) : pas dans la même vague.

## 16.6a — Régularisation KL vers la base (auto-distillation)
Validé par Anaël le 21/10 : la base sert de professeur pour retenir l'adaptateur près d'elle pendant l'apprentissage (l'échelle 0,25 le fait après coup). 0 € : même poids, aucune donnée nouvelle, aucun texte rédigé (D1 inchangé).
- Hyperparamètre `kl_base` (défaut 0 = comportement actuel inchangé, octet pour octet) dans `[hyperparametres]` des configs d'entraînement SFT : perte = entropie croisée + `kl_base` × KL(élève ‖ base) par token, moyennée sur les tokens de la réponse (même masque de perte que le SFT). La distribution de la base est calculée dans le même pas, adaptateur désactivé (`disable_adapter` de PEFT), sans gradient : aucune copie des poids, aucune mémoire GPU de poids en plus.
- Option `kl_temperature` (défaut 1). Le terme KL et l'entropie croisée sont journalisés séparément dans `metriques.jsonl`.
- QLoRA seulement (le chemin Unsloth et ORPO refusent `kl_base > 0` avec un message clair, plutôt qu'un comportement silencieux).
- Invariants du run : `kl_base` et `kl_temperature` consignés dans la config et dans le manifeste ; `compare comparatif` les affiche.
- Fini quand : tests (KL nulle quand l'adaptateur est nul, `kl_base = 0` identique au chemin actuel, masque respecté, refus hors QLoRA, journalisation) ; un entraînement réel de 5 pas sur v18 (orchestrateur) mesure le surcoût en temps et en VRAM (attendu : +30 à 50 % de temps, VRAM des activations seulement).

## 16.6 ★ — Essais contre la dérive : taux, rang, pas, KL vers la base
Hypothèse : l'adaptateur v18 (QLoRA, rang 16, alpha 32, taux 2e-4, 1 époque, 468 exemples, accumulation 8, soit ~58 pas, cosinus) déplace trop la base ; l'échelle 0,25 le confirme sans entraînement. Les essais cherchent un adaptateur **entraîné** qui garde CO et RD sans perdre CR, LC et RE.
**Protocole relu par Anaël avant le premier entraînement** (mémoire « relecture avant entraînement ») : grille, jeu v21, règle de décision.
- Jeu : **v21** (16.3). Graine 1234, autres hyperparamètres de v18 inchangés.
- Grille (7 entraînements MiniCPM5-2B, rapport alpha/rang constant à 2 pour isoler la capacité du rang) :

  | Essai | Rang | Alpha | Taux | Époques | Ce qu'il teste |
  |---|---|---|---|---|---|
  | T0 témoin | 16 | 32 | 2e-4 | 1 | v18 sur v21 (effet de l'alignement CT seul) |
  | T1 | 16 | 32 | 5e-5 | 1 | taux ÷ 4 (analogue entraîné de l'échelle 0,25) |
  | T2 | 16 | 32 | 1e-4 | 1 | taux ÷ 2 |
  | T3 | 4 | 8 | 2e-4 | 1 | rang |
  | T4 | 8 | 16 | 1e-4 | 1 | rang et taux |
  | T5 | 16 | 32 | 2e-4 | 0,5 | pas (planificateur calé sur la demi-époque) |
  | T6 | 16 | 32 | 2e-4 | 1 | KL vers la base (16.6a), `kl_base` choisi sur l'essai de 5 pas de 16.6a pour que le terme KL pèse environ le quart de l'entropie croisée en début d'entraînement |

- Chaque essai : export LoRA GGUF (15.6), génération dev1 à l'échelle 1 sur base Q4_K_M (harnais v2, GPU), notation GLM, `eval comparer` contre la Baseline v2. Coût : ~0,3 € de notation par essai, ~2,1 € au total (OpenRouter).
- Le meilleur essai qui passe est aussi rapporté à l'échelle 0,5 (une génération de plus) pour situer l'optimum.
- Indicateurs en plus de la Qualité : boucles CT (16.3), inventions CR et RE par item (grille D0), sorties tronquées par tâche.
- Fini quand : 7 runs entraînés, tableau dev1 dans `run-autonome.md` avec IC95 par tâche, configuration retenue (ou aucune) selon la règle écrite ; la configuration retenue entre dans 16.7.

## 16.7 — Confirmation de l'échelle 0,25 et du routage CO sur dev1 + dev2
Après 16.1 (dev2 gelé), 16.2 à 16.5 fusionnés, et 16.6 pour son candidat.
- Configurations, harnais v2, sur dev1 **et** dev2 : Baseline ; LoRA v18 à 0,25 ; routage CO (LoRA v18 à l'échelle 1, `--items` sur les items CO, composé par 16.4) ; candidat de 16.6 s'il existe.
- Notation GLM (second juge désactivé sur dev2 par 15.4) ; comparaison par `eval comparer` regroupé (16.5). Coût : ~2 € (OpenRouter).
- Décision selon les règles écrites plus haut ; le routage CO déjà retenu par Anaël reste la recommandation s'il est confirmé sur dev2 ; s'il ne l'est pas, retour à Anaël.
- Charge CPU inchangée sauf pour le candidat de 16.6 (même mesure que le 21/10 : base + LoRA, 4 threads, avec bge-m3).
- Fini quand : tableau dev1, dev2 et regroupé dans le bilan, décisions consignées, aucune lecture de v1.1.

## Vagues proposées
| Vague | Stories en parallèle | Après |
|---|---|---|
| V0 | 16.1 (orchestrateur) · 16.2 · 16.3 · 16.4 | 16.3 : spec relue avant code (D1) |
| V1 | 16.5 · 16.6a · Baseline dev1 en harnais v2 · build v21 et relecture par Anaël (humaine) | 16.5 ← 16.4 ; Baseline v2 ← 16.2, 16.3 |
| V2 | 16.6 ★ (entraînements séquentiels sur GPU) | 16.6 ← 16.6a, protocole et v21 relus par Anaël |
| V3 | 16.7 | 16.7 ← 16.1, 16.5, 16.6 |

Budget estimé : OpenRouter ~5 € (vérification dev2, notations GLM), Anthropic 0 €, Mistral 0 €.
