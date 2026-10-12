# Addendum technique au PRD

Ce document rassemble ce qui alimente l'architecture et les stories sans avoir sa place dans le PRD. Les sources détaillées se trouvent dans les fichiers `research-*.md` de ce dossier et dans la note de cadrage.

## A. Architecture cible (note de cadrage)

Trois briques aux rôles séparés :

| Brique | Rôle | Contenu |
|---|---|---|
| Fine-tuning | Comportement | Adaptation du modèle aux Tâches |
| RAG local | Savoir | Corpus MediaTech, déjà découpé et vectorisé en BGE-M3 |
| Serveur MCP data.gouv | Fraîcheur | Données publiques à jour |

Une quatrième brique, secondaire, consulte des pages des hôtes de la Liste blanche (FR-12).

Principes de fonctionnement :
- **Ordre d'interrogation en Mode connecté** : le MCP d'abord, puis le RAG en repli.
- **Rien de data.gouv dans les poids** : aucune donnée de data.gouv n'est mémorisée dans les poids du modèle.
- **Inférence** : GGUF Q4 avec llama.cpp sur CPU. Les appels d'outils passent par un décodage contraint par schéma JSON.

## B. Serveur MCP data.gouv et Liste blanche

État au 11 octobre 2026 (source : `github.com/datagouv/datagouv-mcp`) :

| Élément | Valeur |
|---|---|
| Production | `https://mcp.data.gouv.fr/mcp` |
| Préproduction | `mcp.preprod.data.gouv.fr` |
| Transport | Streamable HTTP uniquement |
| Accès | Lecture seule, sans authentification |
| Santé | `GET /health` |
| Hébergement | Auto-hébergeable (Docker ou Python) |
| Statut | Expérimental : les outils évoluent |

**Outils exposés par le serveur :** `search_datasets`, `get_dataset_info`, `list_dataset_resources`, `get_resource_info`, `query_resource_data`, `search_organizations`, `search_dataservices`, `get_dataservice_info`, `get_dataservice_openapi_spec`, `get_metrics`. La presse cite aussi `download_and_parse_resource`.

**Sous-ensemble exposé au modèle (5 outils au plus, parade au risque R1) :** `search_datasets`, `get_dataset_info`, `list_dataset_resources`, `query_resource_data`, et `get_resource_info` si nécessaire. Le Harnais peut simplifier les schémas, par exemple en masquant les paramètres optionnels.

**Liste blanche v1 (noms d'hôte exacts, configurables) :**
- `mcp.data.gouv.fr`
- `www.data.gouv.fr`
- `www.service-public.gouv.fr` (domaine actuel des fiches, vérifié le 2026-10-12 ; garder `www.service-public.fr` pour les redirections)
- `www.legifrance.gouv.fr` (refuse la lecture automatique, HTTP 403, constaté le 2026-10-12 : passer par le corpus LEGI de l'Index local ou l'API PISTE)
- `entreprendre.service-public.gouv.fr` (idem, avec `entreprendre.service-public.fr`)
- `lannuaire.service-public.fr`

`[ASSUMPTION : nom d'hôte actuel de l'annuaire à vérifier]`

**Bac à sable MCP (FR-40)** : cassettes enregistrées et versionnées des couples requête/réponse. Option : une instance auto-hébergée à version figée.

## C. Modèles de base candidats (note de cadrage)

**Règle de choix.** Le choix se fait sur le Jeu d'évaluation maison et sur le débit mesuré sur le PC cible, sous la contrainte NFR-1, pas sur les benchmarks publics. Critères secondaires : la licence (Apache 2.0 requise pour FR-37) et le degré d'ouverture des données d'entraînement.

**Shortlist de la Baseline :**

| Modèle | Paramètres | Licence | Données d'entraînement | Rôle | Points à vérifier |
|---|---|---|---|---|---|
| Ministral 3 3B | 3,8 B (dont un encodeur vision) | Apache 2.0 | Non publiées | Qualité, éditeur français | Exclusion de l'encodeur vision ; support par llama.cpp et TRL |
| Granite 4.0 1B, version dense | 1,6 B | Apache 2.0 | Sources documentées | Palier léger, tool calling | Qualité du français (une langue parmi 12). Éviter les variantes H/Mamba. |
| SmolLM3 3B | 3 B | Apache 2.0 | **Entièrement ouvertes** | Transparence | Tool calling ; mode think/no_think |
| Ministral 3 8B | 8,8 B | Apache 2.0 | Non publiées | Plafond de qualité, en évaluation seulement | Trop lourd pour l'entraînement (QLoRA à la limite des 8 Go) et pour NFR-1 |
| Témoin Qwen (~4B) | ~4 B | Apache 2.0 | Non publiées | Référence en tool calling | Hors objectif de souveraineté |

**Écartés :**
- CroissantLLM 1,3B : génération 2024, en retrait, malgré des données ouvertes et une proportion de français de 1:1.
- OLMo 2 1B : centré sur l'anglais.
- EuroLLM 1.7B : version instruct orientée traduction.
- Lucie-7B : trop gros.

**Garde-fous de communication :**
- La certification ISO 42001 de Granite porte sur le système de management de l'IA d'IBM, pas sur le modèle.
- Ministral est développé par un éditeur français, mais son corpus d'entraînement n'est pas publié.

## D. Contrainte de RAM (NFR-1) : leviers à arbitrer par la mesure

**Ordres de grandeur, à mesurer :**

| Composant | Mémoire |
|---|---|
| 3B en Q4_K_M | 2 à 2,5 Go, plus le cache KV |
| 1B en Q4 | 0,8 à 1 Go |
| BGE-M3 (568 M) | 0,6 à 1,2 Go |

**Leviers :**
- un modèle d'embedding plus léger, ou BGE-M3 quantifié ;
- un index sur disque en mmap, avec vecteurs int8 ou binaires et un reranking léger ;
- un corpus restreint ;
- un cache KV quantifié ;
- une fenêtre de contexte limitée. Dans ce cas, le traitement par morceaux du compte rendu devient obligatoire (FR-13).

## E. Socle de Benchmarks standardisés (FR-27)

Les détails sont dans `research-benchmarks.md`.

| # | Benchmark | Configuration |
|---|---|---|
| 1 | `french_bench_mc` (lm-evaluation-harness) | 3-shot |
| 2 | `belebele_fra_Latn` | |
| 3 | Global-MMLU fr | Version Lite ou limite de 2 000 items |
| 4 | AgentPublic/MCQ-eval | YAML lm-eval personnalisé |
| 5 | BFCL : simple, multiple, irrelevance | Sous-échantillonné |
| 6 | Traduction | WMT14 en-fr et fr-en, environ 500 phrases, chrF. FLORES-200 via sacrebleu pour ES, AR, PT et DE. |
| 7 | `ifeval` + `mmlu` (limité) + `crows_pairs_french` | |

Aucun benchmark public ne couvre le tool calling en français, le langage clair ni le RAG administratif. Le Jeu d'évaluation maison comble ces manques.

## F. Méthodes et stack d'entraînement (FR-32 à FR-36)

Les détails sont dans `research-finetuning-methodes.md`.

**Stack** (décision du 11 octobre 2026) :
- **Socle de comparaison** : TRL + PEFT. La méthode se choisit par configuration (`use_dora`, `use_rslora`, `init_lora_weights`).
- **Variante de vitesse** : Unsloth, mesuré en plus. Il est surtout utile pour l'itération rapide.
- **Raison du changement par rapport à la note** : la comparaison doit rester équitable entre les méthodes.

**Méthodes :**

| Code | Méthode | Statut |
|---|---|---|
| M1 | QLoRA | Comptée |
| M2 | LoRA bf16 sur le plus petit candidat | Comptée |
| M3 | DoRA sur base 4 bits | Comptée |
| M4 | ORPO après SFT | Comptée |
| — | QLoRA Unsloth | Variante, vitesse |
| — | rsLoRA, PiSSA | Variantes optionnelles |
| — | Full fine-tuning ou GaLore sur le 1B | Option |

**Réglages par défaut :**
- rang LoRA modéré, parade à l'oubli ;
- séquences de 2 à 4k tokens ;
- 3 à 5 itérations par campagne ;
- masquage de la perte sur la réponse de l'assistant uniquement ;
- chat template officiel du modèle.

**Mesures :**
- débit en tokens/s hors padding, après 10 étapes de chauffe ;
- VRAM via `torch.cuda.max_memory_*` et `nvidia-smi` ;
- énergie via un échantillonnage de `nvidia-smi power.draw` ou via CodeCarbon.

**Pièges :**
- Granite H (Mamba2) pose des problèmes sous Windows.
- L'encodeur vision de Ministral 3 doit être exclu.
- La fusion en 16 bits doit précéder l'export GGUF.
- Le tool calling doit être re-testé après quantification.
- Le même chat template doit servir à l'entraînement et à l'inférence.

## G. Données d'entraînement

**Volumes cibles :**

| Données | Volume |
|---|---|
| Traces de tool calling | 1 500 à 3 000 |
| Transcriptions synthétiques et comptes rendus | 500 à 1 000 |
| Paires en langage clair | 500 à 1 000 |
| Tâches secondaires | 200 à 500 par Tâche `[ASSUMPTION]` |
| Données génériques en français | 10 à 20 % du total |

**Transcriptions** (décision du 11 octobre 2026) : elles sont générées par Mistral et simulent des réunions fictives du secteur public. Claire French Dialogue (CC BY-NC-SA) est réservé à la variante « recherche ».

**Sources d'amorces :**

| Source | Usage |
|---|---|
| `AgentPublic/sp_questions_corpus` | Amorces |
| `assistant_ia_questions_corpus` | Amorces |
| `retriever_dataset` | Amorces |
| `piaf` | Amorces |
| `AgentPublic/MCQ-eval` | Évaluation seulement |
| `french_simplified` (333 paires) | Évaluation du langage clair seulement |

La licence de chaque jeu d'AgentPublic est à vérifier, puis à inscrire au Registre des licences. MediaTech est sous licence Etalab 2.0, avec obligation d'attribution.

**Leçon de llama-falc** : un fine-tuning en langage FALC sur un modèle de 3B a échoué avec environ 22 paires. Le volume et la qualité des paires en langage clair priment sur le choix du modèle.

## H. Registre des risques

| # | Risque | Impact | Parade | Renvois |
|---|---|---|---|---|
| R1 | Tool calling instable à 3B | Appels malformés | 5 outils au plus, aux schémas simples ; décodage contraint ; traces dédiées | FR-7, FR-29, §B |
| R2 | Oubli des capacités générales | Régression hors domaine | Rang LoRA modéré ; 10 à 20 % de données génériques ; non-régression et benchmarks | FR-29, SM-1 |
| R3 | Données synthétiques fausses | Le modèle apprend des erreurs | Vérification contre la source et le Bac à sable MCP ; relecture d'un échantillon | FR-30, FR-40 |
| R4 | Index local ou modèle trop lourd | RAM saturée | Leviers du §D ; mesure dès J1 | NFR-1 |
| R5 | Serveur MCP instable ou évolutif | Mode connecté indisponible, scores non reproductibles | Délais courts ; repli ; schémas versionnés ; Bac à sable MCP | FR-9, FR-40, NFR-9 |
| R6 | Réponses juridiques erronées | Risque pour l'Agent et l'Usager | Citation systématique ; avertissement ; « pas de source » accepté | FR-3, SM-C3 |
| R7 | Licences hétérogènes | Diffusion bloquée | Registre bloquant ; variante « recherche » séparée | FR-31 |
| R8 | Trop peu de paires en langage clair | Échec de la Tâche Langage clair | Volume de 500 à 1 000 paires filtrées | FR-29 |
| R9 | Conditions des générateurs modifiées | Données inutilisables | Revérification avant chaque campagne | §8 du PRD |

## I. Plan de réalisation

| Lot | Charge dans la note | Charge réestimée `[ASSUMPTION]` | Livrable |
|---|---|---|---|
| 0. Cadrage | 3 à 5 j | 3 à 5 j | Jeu d'évaluation et Grille du Juge figés |
| 1. Baseline | 5 à 8 j | 7 à 10 j (benchmarks et Bac à sable MCP en plus) | Scores de référence, go/no-go |
| 2. Données | 5 à 10 j | 7 à 12 j (Tâches secondaires en plus) | Jeu d'entraînement versionné |
| 3. Fine-tuning | 5 à 10 j | 8 à 15 j (4 méthodes et Comparatif) | Modèle retenu et Comparatif |
| 4. Packaging | 3 à 5 j | 5 à 8 j (journal, Retours, Tâches) | Application installable |

## J. Paysage

Les détails sont dans `research-paysage-reglementation.md`.

- **Assistant IA de l'État** : 43 000 utilisateurs en août 2026. Il fonctionne dans le cloud, avec un modèle Mistral sur l'infrastructure Albert.
- **Albert** : non généralisé dans sa forme actuelle.
- **LLaMandement** : cas d'usage étroit.
