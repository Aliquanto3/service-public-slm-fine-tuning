---
title: Décisions pré-arbitrées pour le développement autonome
status: final
created: 2026-10-12
owner: Anaël
applies_to: tout agent BMAD (architecture, stories, dev, review) travaillant sur ce dépôt
---

# Décisions pré-arbitrées

Ce document **fait autorité** pour les agents autonomes. En cas de conflit :
1. il s'aligne sur le PRD et l'UX ;
2. il prime sur toute préférence d'agent.

Une décision qui n'est couverte ni ici ni dans le PRD ou l'UX est prise par l'agent selon la règle « la solution la plus simple et la plus réversible ». Elle est consignée dans `_bmad-output/implementation-artifacts/journal-decisions-nuit.md`, avec sa justification.

## D1. Règles bloquantes (jamais d'exception)

1. **Claude ne génère aucune Donnée d'entraînement.** L'interdiction couvre les exemples, les réponses cibles, les exemples few-shot et les amorces insérés dans les prompts du générateur (PRD §8). Claude peut faire tout le reste : le code, le Juge et les items du Jeu d'évaluation maison.
2. **Le générateur de Données d'entraînement est Mistral via l'API**, avec le modèle `mistral-large-latest` en version stable (jamais un modèle « Labs » ni une préversion). Revérifier les conditions §3.3 avant la campagne et consigner la date de vérification.
3. **Pas de génération avant le gel.** Aucune Donnée d'entraînement n'est générée avant le commit de gel du Jeu d'évaluation maison `v1.0-provisoire` (manifeste SHA-256 ; `eval/SPEC-jeu-evaluation.md` §6).
4. **Aucune publication.** Pas de push vers un dépôt distant, pas de publication sur Hugging Face, aucun envoi vers un service hors de la liste ci-dessous.
5. **Seuls services réseau autorisés pendant la nuit :**
   - Hugging Face, en téléchargement de modèles et de jeux de données ;
   - PyPI et GitHub, en lecture, pour les dépendances et les benchmarks ;
   - l'API Mistral ;
   - l'API Anthropic, pour le Juge ;
   - `mcp.data.gouv.fr` et `www.data.gouv.fr` ;
   - les hôtes de la Liste blanche (addendum §B).
6. **Budgets durs, contrôlés par le code** (compteur persistant, arrêt automatique au plafond) :

   | Service | Plafond pour la nuit | Usage |
   |---|---|---|
   | Mistral | **30 €** | Génération des données et second juge |
   | Anthropic | **10 €** | Juge principal |

   Au-delà, l'agent s'arrête sur ce poste et passe à la suite.
7. **Ne jamais supprimer** de données téléchargées, de checkpoints ni d'artefacts d'évaluation. Ne jamais réécrire l'historique git.
8. **Ne jamais modifier** les décisions explicites du PRD, de l'UX, de la spécification du Jeu d'évaluation maison, de la Grille du Juge ou du présent document. Un désaccord se signale dans le journal de la nuit.
9. **Ne pas modifier le dépôt voisin `../wavelocalai`.** Il est consultable en lecture seule (voir D6).

## D2. Environnement

- **Python 3.12 via `uv`.**
  - La commande `python` du PATH n'est pas fiable : toujours passer par `uv run` ou par l'environnement du projet (`uv venv --python 3.12`, `pyproject.toml`).
  - PyTorch avec CUDA, compatible avec le pilote 610.x de la RTX 3050 (8 Go).
- **Windows 11 natif uniquement cette nuit.** WSL2 n'est pas installé sur le poste (constaté le 2026-10-12, l'installation demande un redémarrage). Si une brique refuse de fonctionner nativement (noyaux Mamba, bitsandbytes…), l'agent consigne le blocage, l'écarte (ex. modèles Granite H) et passe à la suite.
- **Secrets** : dans `.env`, non versionné. Variables : `MISTRAL_API_KEY`, `ANTHROPIC_API_KEY`, `HF_TOKEN`. Un fichier `.env.example` est versionné.

## D3. Stack technique retenue

| Brique | Choix | Raison |
|---|---|---|
| Langage | Python 3.12 pour tout : Harnais, banc d'évaluation, pipeline de données, entraînement, application | Une seule langue, un seul outillage de tests |
| Inférence | llama.cpp avec `llama-server` (binaire Windows embarqué, CPU), modèles GGUF, décodage contraint par grammaire ou schéma JSON pour les appels d'outils | Pas de dépendance à installer chez l'Agent, et RAM maîtrisée |
| Client MCP | SDK Python officiel MCP, transport Streamable HTTP | Conforme au serveur data.gouv |
| Index local | Corpus MediaTech pré-vectorisé ; stockage sur disque, mappé en mémoire | Imposé par NFR-1 |
| Entraînement | TRL + PEFT, avec Unsloth en variante de vitesse | Décision du PRD |
| Benchmarks standardisés | lm-evaluation-harness ; BFCL via `bfcl-eval` ; sacrebleu | Addendum §E |
| Application (J4) | pywebview (WebView2) + interface HTML/CSS/JS sans framework lourd ; PyInstaller ; installateur Inno Setup par utilisateur, sans droits administrateur | Décision d'Anaël du 2026-10-12 |
| Tests | pytest ; ruff | |

L'architecture fixe la bibliothèque vectorielle et le modèle d'embedding, par la mesure, sous la contrainte NFR-1. Le premier choix par défaut est BGE-M3, pour rester compatible avec les vecteurs MediaTech. Un modèle plus léger n'est retenu que si la mesure dépasse le budget de RAM.

## D4. Données et périmètre

- **Index local v1** : service-public et catalogue data.gouv. LEGI, travail-emploi, CNIL et Constitution viennent en extension si la mesure de RAM le permet.
- **Modèles de base candidats pour la Baseline**, par ordre de passage :
  1. Granite 4.0 1B dense ;
  2. Ministral 3 3B ;
  3. SmolLM3 3B ;
  4. le témoin Qwen d'environ 4B ;
  5. Ministral 3 8B, en plafond de qualité, en évaluation seulement et si le temps le permet.

  Les modèles sont téléchargés en GGUF Q4_K_M pour l'inférence, et en poids HF pour l'entraînement.
- **Premier essai de fine-tuning (cette nuit)** : M1 QLoRA. Choix du modèle :
  - **par défaut** : le meilleur Score de Tâche moyen de Baseline parmi les modèles de 3B ou moins qui tiennent dans 5 Go de RAM ;
  - **si la Baseline n'est pas terminée à temps** : Granite 4.0 1B dense.

  L'essai entraîne sur le jeu disponible, évalue et produit un mini-rapport. **Ce n'est pas la décision go/no-go**, qui revient à Anaël.
- **Volumes de données pour la nuit**, dans le budget de 30 € : visez environ 600 exemples, avec les proportions de l'addendum §G, dont 10 à 20 % de données génériques.

## D5. Méthode de travail BMAD pour la nuit

- **Ordre de travail** : PRD §9.3. Le banc d'évaluation et le Comparatif passent avant l'application. J4 et J5 ne sont pas attendus cette nuit.
- **Git.**
  - Commit local après chaque story terminée et testée, au format `feat(<epic>): <story> (story X.Y)` avec la ligne d'attribution.
  - Branche de travail `nuit/2026-10-12`, puisque la branche `main` reçoit le commit de cadrage.
- **Qualité.**
  - Une story est terminée quand ses tests passent.
  - La code review BMAD est faite pour chaque epic, pas pour chaque story, afin de tenir le budget de temps.
- **Blocage.**
  - Après deux tentatives infructueuses sur un même problème, consigner, contourner (stub, mock ou fixture) et passer à la story suivante.
  - Une story ne doit jamais bloquer toute la nuit.
- **Fin de nuit.** Le run s'arrête au plus tard le **2026-10-12 à 07h00**, ou plus tôt quand le travail planifié est terminé. Il produit alors `_bmad-output/implementation-artifacts/rapport-de-nuit.md`, qui contient :
  - le fait et le non-fait ;
  - les scores de Baseline ;
  - le résultat de l'essai QLoRA ;
  - la dépense par API ;
  - les décisions prises seul ;
  - les points à trancher par Anaël.

## D6. Réutilisation

- **`../wavelocalai`** (projet d'Anaël, Streamlit) : il contient un banc de benchmark de SLM (`benchmarks/`) et la mesure carbone avec CodeCarbon. Il peut servir de référence ou d'inspiration en lecture seule. Le code utile est recopié et adapté, sans dépendance croisée.
- **Calibrage du Jeu d'évaluation** : `eval/calibrage/` (16 items validés, script `build_calibrage.py`, cassettes MCP). C'est la référence de format pour le jeu complet.

## D7. Constats d'environnement (2026-10-12)

- Les fiches service-public sont servies sur `www.service-public.gouv.fr`.
- Légifrance refuse la lecture automatique (HTTP 403).
- Le serveur datasets-server de Hugging Face est instable (erreurs 500 et 429) : préférer la lecture directe des fichiers parquet, avec des reprises après échec.
- Le serveur MCP data.gouv a bien répondu le 2026-10-12.
- **Modèles candidats sur Hugging Face** (vérifié le 2026-10-12, aucun accès conditionnel signalé ; licences Apache 2.0) :
  - **Granite.** `ibm-granite/granite-4.0-1b` déclare l'architecture `granitemoehybrid`.
    - Vérifier dans `config.json` que toutes les couches sont de type attention (variante dense). Sinon, il s'agit de la variante hybride Mamba, à écarter sous Windows natif.
    - Vérifier aussi le support par llama.cpp.
  - **Ministral.**
    - Les dépôts disponibles sont `mistralai/Ministral-3-3B-Instruct-2512`, `-3B-Base-2512` et `-8B-Instruct-2512` (+ GGUF officiel pour le 8B).
    - **Pas de GGUF officiel pour le 3B** : il faut le convertir soi-même ou prendre une conversion communautaire réputée (consigner la source).
    - Les poids Instruct sont étiquetés **FP8** : la RTX 3050 (Ampere) ne gère pas le FP8. Il faut obtenir ou produire une version bf16 avant QLoRA, et consigner la méthode.
    - L'architecture `mistral3` comprend un encodeur vision, à exclure.
  - **SmolLM3.** `HuggingFaceTB/SmolLM3-3B`.
- **Corpus de l'Index local** : `AgentPublic/service-public` et `AgentPublic/data-gouv-datasets-catalog`, sous licence Etalab 2.0, mis à jour fin septembre 2026.

## D8. Hybrides Gated DeltaNet et registre des Modèles de base (2026-10-17)

Décisions d'Anaël du 2026-10-17, confirmées en session principale le même jour. Elles remplacent la décision du 2026-10-17 à 09h (`etat-run-2026-10-16.md`, « exclusion des modèles de 2B paramètres et plus ») et la formule « < 2B » de la passation du même fichier : **Qwen3.5-2B reste dans la Baseline**. D8 précise D7 :

- **Mamba restait écarté sous Windows natif** (D2, D7) : un modèle dont `config.json` a une couche `mamba`, ou d'un type inconnu, était écarté par le contrôle `dense` de la story 8.1. **Révisé le 2026-10-18** (voir plus bas) : `mamba` est admis comme `linear_attention`, en Baseline seulement ; un type inconnu reste écarté.
- **Gated DeltaNet (`linear_attention`) est admis pour l'inférence et la Baseline** (option retenue parmi celles proposées : admettre ces hybrides en Baseline seulement, plutôt que les écarter ou les entraîner), avec `entrainable = false` dans la fiche du modèle. llama.cpp b11429 le sert (contrôles `serveur` ok). Le contrôle `dense` échoue si une fiche à couches `linear_attention` ne porte pas `entrainable = false`, et `train run` comme `train sonde-env` (avec ou sans `--unsloth`) refusent un modèle non entraînable.
  - Motif : sous Windows natif, sans `flash-linear-attention` ni `causal-conv1d`, transformers prend une implémentation torch lente. Seuls l'entraînement et `lm_eval` HF sont touchés (source : `spec-modeles-octobre-2026.md`, section « Écarts et points à confirmer par Anaël », contrôle `dense`).
  - **L'entraînement sera rouvert** seulement si un Qwen3.5 sort bien de la Baseline, après un court essai QLoRA qui mesure la vitesse sous Windows.
- **Règle de taille** : 2,5B au plus (relevée de 2B le 2026-10-18 par Anaël, après la Baseline de MiniCPM5-2B, meilleure que granite sur 7 Tâches sur 8), en paramètres du modèle texte servi, tour vision exclue (cible : PC de 16 Go avec Teams, Edge et Outlook). Les modèles écartés « taille > 2B » du registre dépassent aussi 2,5B.
  - Méthode de comptage : en-têtes safetensors des dépôts HF (`huggingface_hub.get_safetensors_metadata`), relevés par l'orchestrateur le 2026-10-17. Les modules exclus du modèle servi (tour vision, audio, tête MTP) ne comptent pas.

### Registre des Modèles de base candidats

Paramètres en milliards (B). « Mesuré » : comptage safetensors du 2026-10-17 ; sinon, taille d'après le nom ou la source citée.

| Slug | Dépôt HF | Paramètres texte servis | Statut | Raison | Date | Source |
|---|---|---|---|---|---|---|
| `granite-4.0-1b` | `ibm-granite/granite-4.0-1b` | 1,63 (mesuré) | candidat au fine-tuning | `granitemoehybrid` sans couche Mamba (variante dense) | 2026-10-17 | D4, D7 ; `etat-run-2026-10-16.md` (décision de 09h, passation) |
| `minicpm5-1b` | `openbmb/MiniCPM5-1B` | 1,08 (mesuré) | candidat au fine-tuning | llama dense, texte seul | 2026-10-17 | `spec-modeles-octobre-2026.md` (seconde campagne) ; `etat-run-2026-10-16.md` (décision de 09h) |
| `eurollm-1.7b` | `utter-project/EuroLLM-1.7B-Instruct` | 1,66 (mesuré) | Baseline seulement | llama dense ; contexte 4096 ; `entrainable = false` le 2026-10-18 (Anaël, option D de `spec-outils-rendu.md` §4) : template sans outils, aucun protocole valide, Baseline la plus faible | 2026-10-18 | `spec-modeles-octobre-2026.md` (« Candidats < 2B ») |
| `granite-4.0-350m` | `ibm-granite/granite-4.0-350m` | 0,35 (mesuré) | candidat au fine-tuning | `granitemoehybrid` dense (28 couches d'attention, aucune Mamba), même architecture que `granite-4.0-1b` ; GGUF officiel `-GGUF` | 2026-10-18 | D8 (décision d'Anaël du 2026-10-18) |
| `granite-4.0-h-350m` | `ibm-granite/granite-4.0-h-350m` | 0,34 (mesuré) | Baseline seulement | hybride Mamba-2 (28 couches mamba sur 32), `entrainable = false` ; GGUF officiel `-GGUF` ; entraînement rouvert après l'enquête WSL2 | 2026-10-18 | D8 (révision du 2026-10-18) |
| `granite-4.0-h-1b` | `ibm-granite/granite-4.0-h-1b` | 1,46 (mesuré) | Baseline seulement | hybride Mamba-2 (36 couches mamba sur 40), `entrainable = false` ; GGUF officiel `-GGUF` ; entraînement rouvert après l'enquête WSL2 | 2026-10-18 | D8 (révision du 2026-10-18) |
| `qwen3.5-0.8b` | `Qwen/Qwen3.5-0.8B` | 0,75 (mesuré : 0,87 au total, dont 0,12 de vision et MTP exclus) | Baseline seulement | hybride Gated DeltaNet, `entrainable = false` | 2026-10-17 | D8 ; `spec-modeles-octobre-2026.md` (« Candidats < 2B ») |
| `qwen3.5-2b` | `Qwen/Qwen3.5-2B` | 1,88 (mesuré : 2,27 au total, dont 0,39 de vision et MTP exclus) | Baseline seulement | hybride Gated DeltaNet, `entrainable = false` | 2026-10-17 | D8 (règle de taille) ; `spec-modeles-octobre-2026.md` |
| `minicpm5-2b` | `openbmb/MiniCPM5-2B` | 2,52 (mesuré, texte seul) | candidat au fine-tuning | llama dense, texte seul ; écarté le 2026-10-17 (taille > 2B), réintégré comme référence puis candidat le 2026-10-18 (règle relevée à 2,5B, Anaël) ; masque par défaut validé sur le tokenizer réel | 2026-10-18 | D8 ; `etat-run-2026-10-17-portable.md` |
| `gemma-4-e2b` | `google/gemma-4-E2B-it` | 4,65 (mesuré : 5,12 au total ; hors vision et audio, dont 2,39 d'embeddings par couche) | écarté | taille > 2B | 2026-10-17 | D8 ; `etat-run-2026-10-16.md` (décision de 09h, « 5B réels ») |
| `ministral-3-3b` | `mistralai/Ministral-3-3B-Instruct-2512-BF16` | ≈ 3 (nom) | écarté | taille > 2B, cible 16 Go | 2026-10-17 | `etat-run-2026-10-16.md` (décision de 09h, passation) |
| `ministral-3-8b` | `mistralai/Ministral-3-8B-Instruct-2512-GGUF` | ≈ 8 (nom) | écarté | taille > 2B, cible 16 Go | 2026-10-17 | `etat-run-2026-10-16.md` (passation : seuls les modèles < 2B restent candidats) |
| `qwen-4b` | `Qwen/Qwen3-4B-Instruct-2507` | ≈ 4 (nom) | écarté | taille > 2B, cible 16 Go ; modèle lent | 2026-10-17 | `etat-run-2026-10-16.md` (réponses d'Anaël, décision de 09h, passation) |
| `smollm3-3b` | `HuggingFaceTB/SmolLM3-3B` | ≈ 3 (nom) | écarté | taille > 2B, cible 16 Go | 2026-10-17 | `etat-run-2026-10-16.md` (décision de 09h, passation) |
| `bonsai-2-4b` | `prism-ml/Ternary-Bonsai-2-4B-gguf` | ≈ 4 (source) | écarté | ternaire Q2_0, non entraînable (`entrainable = false`), taille > 2B | 2026-10-17 | `spec-modeles-octobre-2026.md` ; `etat-run-2026-10-16.md` (décision de 09h, « 4B ») |
| `minicpm-v-4.7-1b` | `openbmb/MiniCPM-V-4.7-1B` | non mesuré | écarté | retiré de la Baseline (seconde campagne) | 2026-10-17 | `spec-modeles-octobre-2026.md` ; `etat-run-2026-10-16.md` |
| LFM2.5 (pas de fiche) | non épinglé | non mesuré | écarté | licence LFM 1.0 (usage commercial limité aux entités de moins de 10 M$ de chiffre d'affaires) | 2026-10-17 | `etat-run-2026-10-16.md` (candidats ajoutés) |
| Granite 4.0 H micro (pas de fiche) | `ibm-granite/granite-4.0-h-micro` | ≈ 3 (nom) | écarté | taille > 2,5B | 2026-10-18 | D8 (révision du 2026-10-18) |
| Granite 4.0 H tiny (pas de fiche) | `ibm-granite/granite-4.0-h-tiny` | ≈ 7 (nom) | écarté | taille > 2,5B | 2026-10-18 | D8 (révision du 2026-10-18) |
| Granite 4.0 H small (pas de fiche) | `ibm-granite/granite-4.0-h-small` | ≈ 32 (nom) | écarté | taille > 2,5B | 2026-10-18 | D8 (révision du 2026-10-18) |
| `croissantllm-chat` (fiche supprimée, runs `fetch` conservés) | `croissantllm/CroissantLLMChat-v0.1` | ≈ 1,3 (source) | écarté | licence MIT non admise en sortie ; contexte natif 2048 | 2026-10-17 | `spec-modeles-octobre-2026.md` (« Candidats < 2B ») |

Décisions d'Anaël du 2026-10-18 (Granite) :

- **Granite 4.0 350M dense** ajouté à la Baseline et au fine-tuning (même architecture que `granite-4.0-1b`).
- **Granite 4.0 H (hybrides Mamba) admis en Baseline quand llama.cpp les sert sous Windows** : révision de D2 et du premier point de D8 (Mamba n'est plus écarté sous Windows natif). L'entraînement peut se faire hors Windows natif (WSL2/Linux), tant que l'inférence reste réalisable sous Windows. `granite-4.0-h-350m` et `granite-4.0-h-1b` sont en `entrainable = false` pour l'instant, comme les Qwen3.5 ; leur entraînement sera rouvert après l'enquête WSL2. Le contrôle `dense` admet `mamba` à cette seule condition (`COUCHES_INFERENCE_SEULE`) ; un type de couche inconnu reste écarté.
- Les autres Granite H (micro, tiny, small) dépassent la règle de 2,5B : écartés, motif « taille ».
- `CANDIDATS` : `granite-4.0-1b`, `granite-4.0-350m`, `minicpm5-1b`, `minicpm5-2b`, `eurollm-1.7b`, `granite-4.0-h-350m`, `granite-4.0-h-1b`, `qwen3.5-0.8b`, `qwen3.5-2b`.

Les sources citées sont sous `_bmad-output/implementation-artifacts/`.

Liste `--candidats` alignée sur le registre de D8 le 2026-10-17 (décision d'Anaël) : `verifications.CANDIDATS` = `granite-4.0-1b`, `minicpm5-1b`, `eurollm-1.7b`, `qwen3.5-0.8b`, `qwen3.5-2b`. Elle remplace l'ordre de passage D4 initial, sans le réécrire. Le 2026-10-18 : `minicpm5-2b` y est ajouté (règle relevée à 2,5B) et `eurollm-1.7b` passe en Baseline seulement ; ordre : `granite-4.0-1b`, `minicpm5-1b`, `minicpm5-2b`, puis `eurollm-1.7b`, `qwen3.5-0.8b`, `qwen3.5-2b`. Le 2026-10-18 (Granite) : `granite-4.0-350m` et les deux Granite H y sont ajoutés ; ordre : `granite-4.0-1b`, `granite-4.0-350m`, `minicpm5-1b`, `minicpm5-2b`, puis `eurollm-1.7b`, `granite-4.0-h-350m`, `granite-4.0-h-1b`, `qwen3.5-0.8b`, `qwen3.5-2b` (les entraînables d'abord).

Décisions d'Anaël du 2026-10-18 sur R7 (`spec-outils-rendu.md`) : §0, **normaliser au build** (option A : le premier message `user` des lignes RD est recomposé comme en Mode connecté, dans une nouvelle version du jeu, sans appel payant ni réécriture de v1) ; §4, **option D** (EuroLLM en Baseline seulement).
