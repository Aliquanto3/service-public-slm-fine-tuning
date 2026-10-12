# Note de cadrage — SLM secteur public français

Oct 11, 2026 · @Anaël Yahi

## Objectif et périmètre

Construire un assistant IA local pour les agents du secteur public français, qui tourne hors ligne sur un PC bureautique de 16 Go de RAM, s'installe en un clic et vérifie les données officielles quand une connexion est disponible. Objectif secondaire : monter en compétence de bout en bout (données, fine-tuning, évaluation, packaging).

**Cas d'usage cibles (par priorité)**

1. Répondre aux questions courantes des agents sur les démarches, les droits et l'organisation administrative, en citant la source officielle.
2. Trouver et interroger un jeu de données public (data.gouv) via des outils.
3. Rédiger un compte rendu de réunion à partir de notes ou d'une transcription.
4. Réécrire un document administratif en langage clair.

**Hors périmètre** : préentraînement d'un modèle de zéro, mémorisation des données de data.gouv dans les poids, conseil juridique engageant, traitement de données personnelles.

## Architecture cible

Trois briques aux rôles séparés : le fine-tuning pour le comportement, le RAG local pour le savoir, le serveur MCP officiel de data.gouv pour la fraîcheur des données.

&#91;embedded content: architecture cible · 3 briques, 2 modes\]

Hors ligne, le harnais interroge l'index embarqué ; connecté, il vérifie sur le MCP data.gouv et retombe sur le RAG en cas d'échec. Rien de data.gouv n'est mémorisé dans les poids du modèle.

## Choix du modèle de base

Shortlist pour la baseline : **Ministral 3 3B** (qualité et souveraineté), **Granite 4.0 1B** (palier léger, gouvernance documentée) et **SmolLM3 3B** (données d'entraînement entièrement publiées). Ministral 3 8B sert de plafond de qualité. Le choix final se fait sur le jeu d'évaluation et le débit mesuré sur le PC cible, pas sur les benchmarks publics.

| Modèle | Paramètres | Licence | Données d'entraînement | Atouts | Limites |
| --- | --- | --- | --- | --- | --- |
| [Ministral 3 3B](https://getdeploying.com/llms/ministral-3-3b) | 3,8 B (dont encodeur vision) | Apache 2.0 | Non publiées | Éditeur français, multilingue natif, tool use natif, \~2,5 Go en Q4 | En retrait du 8B ; encodeur vision inutile (support Unsloth et llama.cpp à vérifier) |
| [Ministral 3 8B](https://getdeploying.com/llms/ministral-3-8b) | 8,8 B | Apache 2.0 | Non publiées | Plafond de qualité de la famille | QLoRA à la limite des 8 Go de VRAM ; lent sur CPU |
| [Granite 4.0 1B](https://huggingface.co/ibm-granite/granite-4.0-h-1b) (version dense) | 1,6 B | Apache 2.0 | Sources documentées ; jeux et code non publiés | Conçu pour l'edge, tool calling renforcé, AIMS d'IBM certifié ISO 42001, cohérent avec le partenariat IBM | Français parmi 12 langues, qualité à valider |
| [SmolLM3 3B](https://huggingface.co/HuggingFaceTB/SmolLM3-3B-Base/blob/refs%2Fpr%2F4/README.md) | 3 B | Apache 2.0 | **Entièrement ouvertes** (mélange de données et configurations publiés) | Français natif parmi 6 langues, recette reproductible | Tool calling et publication des données de post-entraînement à vérifier |
| [CroissantLLM](https://arxiv.org/abs/2402.00786v2) | 1,3 B | Ouverte | **Entièrement ouvertes**, ratio français / anglais 1:1 | Seul modèle réellement bilingue FR/EN, 81 % des critères FMTI | Génération 2024, nettement en retrait en qualité et en tool calling |
| [OLMo 2 1B](https://allenai.org/olmo) | 1 B | Apache 2.0 | **Entièrement ouvertes**, toutes étapes | Référence de transparence et de reproductibilité | Centré sur l'anglais |
| [EuroLLM 1.7B](https://arxiv.org/abs/2409.16235v1) | 1,7 B | Apache 2.0 | Publication des données annoncée (à vérifier) | 24 langues officielles de l'UE | Version instruct orientée traduction |
| [Lucie-7B](https://dblp.org/pid/116/4970) (OpenLLM-France) | 7 B | Ouverte | Corpus publié, majoritairement francophone | Ancrage français le plus fort | Trop gros pour la cible |
| Témoin non européen (famille Qwen, \~4B) | \~4 B | Apache 2.0 | Non publiées | Référence forte en tool calling | Hors objectif de souveraineté |

**Auditabilité** : un modèle entièrement ouvert permet de tracer les sources et leurs licences, et de vérifier que le jeu d'évaluation n'a pas fuité dans l'entraînement. Un audit exhaustif de milliers de milliards de tokens reste hors de portée. La certification ISO 42001 de Granite porte sur le système de management d'IBM, pas sur le modèle ni sur l'application qui l'utilise.

**Nuance sur la souveraineté culturelle** : Mistral est un éditeur français, mais le corpus de Ministral n'est pas publié. Dans cette architecture, l'ancrage culturel et réglementaire vient surtout du RAG sur les corpus officiels et du fine-tuning sur des données françaises, pas du modèle de base.

**Contraintes matérielles** : entraînement QLoRA 4 bits sur RTX 3050 8 Go (séquences de 2 à 4k tokens) ; inférence cible en GGUF Q4 sur CPU, 16 Go de RAM partagés avec l'index RAG et la bureautique.

## Données

Le corpus RAG existe déjà, prêt à l'emploi : la collection MediaTech de la DINUM. Le vrai travail porte sur les données d'entraînement comportementales, qui n'existent pas et doivent être générées.

| Source | Contenu | Usage | Licence |
| --- | --- | --- | --- |
| [MediaTech (AgentPublic)](https://huggingface.co/collections/AgentPublic/mediatech) | service-public, travail-emploi, LEGI, CNIL, Constitution, DOLE, [catalogue data.gouv](https://huggingface.co/datasets/AgentPublic/data-gouv-datasets-catalog) ; déjà découpés et vectorisés en BGE-M3 | Index RAG embarqué | Etalab 2.0 |
| [AgentPublic](https://huggingface.co/AgentPublic) : sp\_questions\_corpus, MCQ-eval, piaf, retriever\_dataset | Questions usagers, QCM, questions-réponses | Jeu d'évaluation, amorces de questions | À vérifier par jeu |
| [Claire French Dialogue](https://huggingface.co/datasets/OpenLLM-France/Claire-Dialogue-French-0.1) | \~160 M mots de transcriptions orales | Entrées pour générer des comptes rendus | CC BY-NC-SA (usage non commercial) |
| [french\_simplified](https://huggingface.co/datasets/esoria3/french_simplified) | 333 paires texte / version simplifiée | Évaluation du langage clair uniquement | À vérifier |
| Serveur MCP data.gouv | Réponses réelles des outils | Traces de tool calling rejouées | Données Etalab |

**Données synthétiques : Claude exclu comme générateur.** Les conditions d'Anthropic interdisent d'utiliser les sorties de Claude comme cibles d'entraînement d'un modèle de génération de texte ouverte sans autorisation écrite ([article support](https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model), [Commercial Terms](https://www.anthropic.com/legal/commercial-terms)). Ce SLM entre dans ce cas. Claude reste utilisable comme juge pour évaluer le modèle final.

**Générateur retenu : un grand modèle Mistral via l'API.** Les conditions commerciales de Mistral (en vigueur au 25 septembre 2026) ne restreignent que les sorties *image* pour entraîner un générateur d'images concurrent ; les sorties texte sont utilisables pour l'entraînement ([Commercial Terms Mistral, §3.3](https://legal.mistral.ai/terms/commercial-terms-of-service)). Éviter les modèles « Labs » ou en préversion, dont les données servent à l'entraînement de Mistral. Repli local : Qwen3.6-35B-A3B.

**Gemini exclu comme générateur** : les conditions de l'API interdisent de l'utiliser pour développer des modèles concurrents de ses services ([Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms)). Il reste utilisable comme juge d'évaluation.

**Volumes cibles** (ordre de grandeur, à ajuster après la baseline) :

- 1 500 à 3 000 traces de tool calling (question, appels MCP, réponse citée), validées contre les réponses réelles des outils ;
- 500 à 1 000 comptes rendus à partir de transcriptions ;
- 500 à 1 000 paires de réécriture en langage clair, générées puis filtrées par relecture d'échantillon ;
- 10 à 20 % de données génériques en français pour limiter l'oubli des capacités générales.

Un projet public de fine-tuning FALC sur un 3B a échoué faute de paires alignées en nombre suffisant (\~22) : la qualité et le volume du jeu priment sur le modèle ([llama-falc](https://huggingface.co/gpnd/llama-falc)).

## Évaluation

Le fine-tuning n'est justifié que s'il bat la baseline : modèle de base + RAG + prompt système, sans entraînement. Le jeu d'évaluation est construit avant toute génération de données et n'est jamais utilisé pour l'entraînement.

| Cas d'usage | Jeu de test | Métriques |
| --- | --- | --- |
| Questions démarches et droits | 60 questions (amorces AgentPublic + questions rédigées) | Exactitude, présence et justesse de la source citée |
| Recherche data.gouv | 40 requêtes | Taux d'appels valides (bon outil, arguments conformes au schéma), réponse exacte |
| Compte rendu | 25 transcriptions | Couverture des décisions et actions, absence d'invention |
| Langage clair | 25 textes administratifs | Lisibilité (indice adapté au français), fidélité au sens, juge LLM + relecture humaine |
| Non-régression | 30 questions générales en français | Écart avec le modèle de base |

**Mesures techniques** sur le PC cible 16 Go : débit en tokens/s, latence au premier token, RAM maximale avec l'index chargé. L'application de benchmark de SLM existante peut servir de banc de mesure.

**Juge** : Claude ou un grand modèle open-weight, sur grille notée, avec relecture humaine d'un échantillon de 20 %.

## Plan de réalisation

Charge totale estimée : **21 à 38 jours**, soit 3 à 6 mois en side project. Le jalon clé est la fin du lot 1 : la baseline décide de ce que le fine-tuning doit corriger.

| Lot | Contenu | Livrable | Charge (j) |
| --- | --- | --- | --- |
| 0. Cadrage | Cas d'usage, jeu d'évaluation, grille du juge | Jeu de test figé | 3–5 |
| 1. Baseline | Index RAG MediaTech, client MCP data.gouv, harnais sur llama.cpp, comparaison des modèles de base | Scores de référence ; **go / no-go** du fine-tuning | 5–8 |
| 2. Données | Génération synthétique, rejeu des outils, filtrage, déduplication | Jeu d'entraînement versionné | 5–10 |
| 3. Fine-tuning | QLoRA (Unsloth), 3 à 5 itérations, fusion et quantification GGUF | Modèle retenu + rapport d'évaluation | 5–10 |
| 4. Packaging | Installateur Windows, index embarqué, mode hors ligne / en ligne | Application installable sur un PC 16 Go | 3–5 |

## Risques et points de vigilance

| Risque | Impact | Parade |
| --- | --- | --- |
| Tool calling instable à 3B | Appels malformés, réponses non vérifiées | Peu d'outils aux schémas simples, décodage contraint par schéma JSON dans llama.cpp, traces d'entraînement dédiées |
| Oubli des capacités générales après fine-tuning | Régression hors domaine | LoRA de rang modéré, mélange de données génériques, jeu de non-régression |
| Données synthétiques fausses | Le modèle apprend des erreurs | Vérification contre le corpus source, relecture d'un échantillon, rejet des traces dont les outils divergent |
| Index RAG trop lourd pour le package | Installation lourde, RAM saturée | Sous-ensemble ciblé (service-public, catalogue data.gouv), vecteurs quantifiés, modèle d'embedding plus léger que BGE-M3 si besoin |
| Serveur MCP data.gouv expérimental et instable | Mode en ligne indisponible | Délais courts, repli automatique sur le RAG local, message explicite à l'utilisateur |
| Réponses juridiques erronées | Risque pour l'agent et l'usager | Citation systématique de la source, mention « ne vaut pas avis juridique » |
| Licences hétérogènes | Diffusion bloquée | Registre des licences par jeu ; Claire (NC) réservé à l'usage non commercial |

## Sources

- [data.gouv.fr — Expérimentation autour d'un serveur MCP pour datagouv (25 février 2026)](https://www.data.gouv.fr/posts/experimentation-autour-dun-serveur-mcp-pour-datagouv)
- [Banque des Territoires — Data.gouv facilite l'accès des IA génératives aux données publiques](https://www.banquedesterritoires.fr/datagouv-facilite-lacces-des-ia-generatives-aux-donnees-publiques)
- [AgentPublic sur Hugging Face](https://huggingface.co/AgentPublic)
- [Collection MediaTech](https://huggingface.co/collections/AgentPublic/mediatech)
- [Catalogue data.gouv vectorisé (AgentPublic)](https://huggingface.co/datasets/AgentPublic/data-gouv-datasets-catalog)
- [Tutoriel RAG MediaTech (GitHub etalab-ia)](https://github.com/etalab-ia/mediatech/blob/main/docs/hugging_face_rag_tutorial.ipynb)
- [Ministral 3 3B — fiche](https://getdeploying.com/llms/ministral-3-3b)
- [Ministral 3 8B — fiche](https://getdeploying.com/llms/ministral-3-8b)
- [Ministral 3 — LM Studio](https://lmstudio.ai/blog/lmstudio-v0.3.33)
- [Anthropic — Can I use my Outputs to train an AI model?](https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model)
- [Anthropic — Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms)
- [The Claire French Dialogue Dataset (arXiv)](https://arxiv.org/abs/2311.16840v1)
- [llama-falc — retour d'expérience de fine-tuning FALC](https://huggingface.co/gpnd/llama-falc)
- [french\_simplified](https://huggingface.co/datasets/esoria3/french_simplified)
- [Publications OpenLLM-France / Lucie-7B (dblp)](https://dblp.org/pid/116/4970)
