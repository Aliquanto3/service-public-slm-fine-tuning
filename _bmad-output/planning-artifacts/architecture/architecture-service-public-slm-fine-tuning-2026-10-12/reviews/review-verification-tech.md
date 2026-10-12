---
review-of: ARCHITECTURE-SPINE.md
lens: 'Vérification sur sources primaires des affirmations techniques porteuses (versions, existence et adéquation des technologies nommées)'
reviewer: relecteur automatique (lecture seule)
date: 2026-10-12
method: 'Métadonnées PyPI (JSON API), code et README aux tags concernés sur GitHub (raw.githubusercontent.com, api.github.com), fichiers de dépôts Hugging Face. Aucun téléchargement > 50 Mo, aucune API payante.'
---

# Revue « vérification technique » du spine

## Verdict

Le socle de versions est exact (toutes les versions du tableau Stack existent sur PyPI au 2026-10-12, sauf `uv`, voir V-16), et la plupart des API nommées existent bien. En revanche, cinq affirmations porteuses ne tiennent pas une fois confrontées au code, et chacune casserait une story de la nuit :

1. le `train` ne peut pas co-installer Unsloth avec transformers 5.19 / TRL 1.15 ;
2. `assistant_only_loss` de TRL échoue sur les templates officiels de Granite 4.0 1B et de Ministral 3 3B, ce qui heurte AD-7 ;
3. `bfcl-eval` ne peut pas vivre dans le même `uv.lock` que le socle, et il ne passe pas par le chemin `--jinja` ;
4. `lm-eval hf` + `gguf_file` ne charge pas 3 des 4 candidats (transformers ne connaît pas ces architectures GGUF) ;
5. `torch` CUDA sous Windows ne vient pas de PyPI, et l'hôte nécessaire manque au profil `outillage`.

Il y a aussi deux points de vigilance : le tag llama.cpp choisi est une pré-version (nightly), et l'export d'un adaptateur PiSSA a besoin d'un traitement particulier.

## Tableau de synthèse

| # | Affirmation du spine | Statut | Source primaire consultée |
| --- | --- | --- | --- |
| V-1 | mcp 2.3.0 : `streamable_http_client(url, http_client=httpx2.AsyncClient)` | **Confirmé** | `src/mcp/client/streamable_http.py` @ v2.3.0 |
| V-2 | Compatibilité du SDK MCP v2 avec le serveur data.gouv (protocole 2025-06-18) | **Confirmé** (avec une réserve) | `src/mcp-types/mcp_types/version.py`, `src/mcp/client/session.py` @ v2.3.0 |
| V-3 | anthropic 1.x accepte un client HTTP injecté | **Confirmé** : `httpx2.Client` / `httpx2.AsyncClient` | `src/anthropic/_client.py` @ v1.13.0 |
| V-4 | mistralai 3.x accepte un client HTTP injecté | **Confirmé**, mais les paramètres s'appellent `client=` / `async_client=` | `src/mistralai/client/sdk.py` @ v3.2.0 |
| V-5 | Téléchargements Hugging Face via `slmsp.net` | **Douteux** (hf-xet contourne le client Python) | `utils/_http.py`, `constants.py` @ huggingface_hub v2.2.0 ; métadonnées PyPI |
| V-6 | llama.cpp b11560 = « dernière release », binaires `win-cpu-x64` et `win-cuda-12.4-x64` | **Partiellement infirmé** (b11560 est une pré-version) | API GitHub releases |
| V-7 | `llama-server` : `--jinja`, outils natifs + grammaire, `--embedding --pooling cls`, `response_format` json_schema, `--cache-type-k q8_0` | **Confirmé** | `tools/server/README.md`, `docs/function-calling.md`, `tests/test-chat.cpp` @ b11560 |
| V-8 | `convert_hf_to_gguf.py` gère Granite 4.0 dense, Ministral 3, SmolLM3 | **Confirmé**, mais le script n'est pas dans les binaires | `convert_hf_to_gguf.py`, `conversion/granite.py`, `conversion/mistral3.py`, `conversion/llama.py` @ b11560 |
| V-9 | bfcl-eval peut viser un serveur compatible OpenAI déjà lancé | **Confirmé** pour le mécanisme, **infirmé** pour l'intégration prévue (dépendances, chemin de prompt, modèles) | README et `base_oss_handler.py` (branche main) ; métadonnées PyPI bfcl-eval 2026.3.23 |
| V-10 | lm-eval 0.4.13 : backend `hf` avec `gguf_file` | Paramètre **confirmé** ; usage **infirmé** pour Granite, Ministral 3 et SmolLM3 | `lm_eval/models/huggingface.py` @ v0.4.13 ; `modeling_gguf_pytorch_utils.py`, `integrations/ggml.py` @ transformers v5.19.0 |
| V-11 | PEFT 0.21 : `use_dora`, `use_rslora`, `init_lora_weights="pissa"` | **Confirmé** (avec une réserve sur l'export PiSSA) | `src/peft/tuners/lora/config.py` @ v0.21.2 |
| V-12 | TRL 1.15 : `ORPOTrainer` | **Infirmé** pour `trl.ORPOTrainer` : il est dans `trl.experimental.orpo` | arbre et `trl/__init__.py` @ v1.15.0 |
| V-13 | TRL 1.15 : SFT avec perte sur l'assistant seul | **Confirmé** (`assistant_only_loss`), mais **infirmé** pour Granite 4.0 1B et Ministral 3 3B | `trl/trainer/sft_trainer.py`, `trl/chat_template_utils.py`, `trl/chat_templates/` @ v1.15.0 ; `chat_template.jinja` des dépôts HF |
| V-14 | Unsloth sous Windows natif, dans le même extra `train` | Windows **confirmé** ; co-installation **infirmée** | README Unsloth (main) ; métadonnées PyPI unsloth et unsloth-zoo 2026.10.3 |
| V-15 | bitsandbytes 0.50 sous Windows natif (RTX 3050, sm86) | **Confirmé** (sur le papier ; H-WIN-TRAIN reste à mesurer) | PyPI (roue `win_amd64`) ; `docs/source/installation.mdx` (main) |
| V-16 | Versions du tableau Stack « relevées sur PyPI » | **Confirmé** sauf `uv` (0.12.23 installé, 0.13.0 publié le 2026-10-09) | API JSON PyPI |
| V-17 | torch 2.14.1 CUDA dans l'extra `train` | **Infirmé** pour PyPI : la roue Windows de PyPI est CPU seule | métadonnées PyPI torch 2.14.1 |
| V-18 | pywebview 6.x : `js_api` et `evaluate_js` | **Confirmé** | `webview/__init__.py`, `webview/window.py` @ 6.2.1 |
| V-19 | Artefacts HF : BGE-M3 GGUF, GGUF officiel de Ministral 3, Granite 4.0 1B dense, poids FP8 de Ministral 3 | **Confirmé**, avec une simplification possible | API Hugging Face, `config.json` des dépôts |

## Détail par point

### V-1 — `streamable_http_client` du SDK MCP v2 : confirmé

Au tag `v2.3.0`, `src/mcp/client/streamable_http.py` contient :

```python
@asynccontextmanager
async def streamable_http_client(
    url: str,
    *,
    http_client: httpx2.AsyncClient | None = None,
    terminate_on_close: bool = True,
    max_sse_event_size: int | None = DEFAULT_MAX_SSE_EVENT_SIZE,
) -> AsyncGenerator[TransportStreams, None]:
```

`http_client` est un argument nommé seul (keyword-only). Quand le client est fourni, le SDK ne gère pas son cycle de vie (`client_provided`), et c'est bien `slmsp.net` qui doit l'ouvrir et le fermer. Le SDK ne suit une redirection que si elle reste sur la même origine, quel que soit `follow_redirects` : c'est compatible avec la Liste blanche à correspondance exacte. `mcp` 2.3.0 dépend de `httpx2>=2.10.0`, ce qui confirme le bannissement conjoint de `httpx` et `httpx2` dans AD-4.

Remarque mineure : `mcp` 2.3.0 ajoute à la fermeture runtime `starlette`, `uvicorn`, `sse-starlette`, `opentelemetry-api` et `pywin32` (Windows). C'est sans effet sur AD-2, mais à prévoir dans la spec PyInstaller (J4).

### V-2 — Négociation de protocole : confirmé, avec une réserve

`KNOWN_PROTOCOL_VERSIONS` vaut `2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25, 2026-07-28`. `ClientSession.initialize()` propose `LATEST_HANDSHAKE_VERSION` (= `2025-11-25`) et accepte toute version de `HANDSHAKE_PROTOCOL_VERSIONS`, donc le `2025-06-18` du serveur data.gouv. La révision `2026-07-28` (« stateless per-request envelope », sonde `server/discover`) existe désormais.

**Réserve.** Le format de cassette adopté (AD-10 : `initialize` + `interactions` JSON-RPC) correspond à l'ère « handshake ». Si mcp.data.gouv.fr passe à la révision 2026-07-28, les cassettes enregistrées ne décriront plus l'échange réel. **Correctif proposé (AD-8/AD-10)** : inscrire `protocolVersion` négociée dans la cassette et dans `config/outils-mcp.toml`. Au passage en Mode connecté, un changement de version déclenche le même repli FR-9 qu'une dérive de schéma.

### V-3 — anthropic 1.13.0 : confirmé (httpx2)

`src/anthropic/_client.py` @ v1.13.0 : `import httpx2` ; `Anthropic(..., http_client: httpx2.Client | None = None)` ; `AsyncAnthropic(..., http_client: httpx2.AsyncClient | None = None)`. Dépendance PyPI : `httpx2<3,>=2.0.0`. J'ai aussi vérifié que `output_config` (avec `format` et `effort` ∈ low…max) existe dans `message_create_params.py`, et que `temperature` n'y figure plus. C'est cohérent avec AD-12.

### V-4 — mistralai 3.2.0 : confirmé, à préciser

`src/mistralai/client/sdk.py` @ v3.2.0 : `import httpx2 as httpx` ; `Mistral(..., client: Optional[HttpClient] = None, async_client: Optional[AsyncHttpClient] = None)`. Ce sont des protocoles, qu'un `httpx2.Client` satisfait. Le client par défaut est `httpx.AsyncClient(follow_redirects=True)`. **Correctif proposé (AD-4)** : écrire « SDK mistralai via `client=` / `async_client=` » plutôt que de laisser entendre un paramètre `http_client`. Le client par défaut suit les redirections, il faut donc impérativement injecter celui de `slmsp.net`.

### V-5 — Téléchargements Hugging Face : douteux

`huggingface_hub` 2.2.0 dépend de `httpx2` et expose `set_client_factory()` / `set_async_client_factory()` (`utils/_http.py`). Le branchement sur `slmsp.net` est donc possible pour les appels HTTP Python. Mais le paquet dépend aussi de `hf-xet` (sur x86_64/AMD64), dont les transferts de gros fichiers passent par un client Rust, hors de toute fabrique Python, vers les hôtes CAS Xet. Je n'ai trouvé aucune variable `HF_HUB_DISABLE_XET` dans `constants.py` @ v2.2.0 (seulement `HF_XET_HIGH_PERFORMANCE`). Les bibliothèques tierces de l'outillage (`datasets` sous lm-eval, `bfcl-eval` via `requests`) font elles aussi leurs propres requêtes.

**Correctif proposé (AD-4)** : pour le profil `outillage`, préciser que la journalisation se fait au niveau de l'appel de haut niveau (dépôt, fichier, révision, octets) et non requête par requête. Ajouter les hôtes Xet de Hugging Face à la liste D1.5 (à faire valider), ou documenter que les téléchargements de poids sont hors de `slmsp.net`. Le profil `assistant` n'est pas concerné : il ne télécharge rien.

### V-6 — llama.cpp b11560 : partiellement infirmé

La release `b11560` existe (publiée le 2026-10-12T03:57Z), avec `llama-b11560-bin-win-cpu-x64.zip` (19 Mo) et `llama-b11560-bin-win-cuda-12.4-x64.zip` (265 Mo). Mais :

- **elle est marquée `prerelease: true`**, comme tous les tags `bNNNNN` récents. La release « latest » du dépôt est **`v0.6.0`** (2026-10-05), dont le fichier `nightly-tag.txt` pointe sur **`b11429`**, qui a les mêmes binaires Windows. Le `.memlog` (« dernière release b11560 ») confond donc la dernière nightly avec la dernière version stable ;
- les DLL CUDA sont livrées à part (`cudart-llama-bin-win-cuda-12.4-x64.zip`, 391 Mo) : le script `vendor/` doit télécharger les deux archives ;
- une variante `cuda-13.4-x64` existe aussi (153 Mo + 423 Mo de cudart). Avec le pilote 610, les deux conviennent ; le choix 12.4 n'est pas un problème.

**Correctif proposé (AD-6, Stack)** : figer `b11429` (= v0.6.0, stable) ou assumer explicitement une nightly (« b11560, pré-version, choisie pour … »). Ajouter le téléchargement de l'archive `cudart` correspondante.

### V-7 — Fonctions de `llama-server` : confirmé

Dans `tools/server/README.md` @ b11560 :

- `--jinja, --no-jinja` : « default: enabled ». Le drapeau existe ; il est désormais actif par défaut, et le passer explicitement reste sans danger.
- appels d'outils OpenAI « supported with the `--jinja` flag ». `docs/function-calling.md` décrit les gestionnaires natifs et génériques. `tests/test-chat.cpp` teste les templates `ibm-granite-granite-4.0.jinja` et `mistralai-Ministral-3-14B-Reasoning-2512.jinja` (peg_tester) et la grammaire paresseuse (`grammar_lazy`, déclencheurs). `models/templates/HuggingFaceTB-SmolLM3-3B.jinja` est présent. H-TOOLS reste une mesure légitime ; le mécanisme existe.
- `--embedding, --embeddings` et `--pooling {none,mean,cls,last,rank}` : confirmés. Les plongements poolés sont **déjà normalisés L2** par le serveur. La normalisation côté Harnais (AD-9) est redondante mais sans risque.
- `response_format` avec `{"type": "json_schema", "schema": …}` : confirmé (repli H-TOOLS valide).
- `-ctk, --cache-type-k` avec `q8_0` : confirmé ; `-ctv` aussi. **Non vérifié ici** : quantifier le cache V exige-t-il toujours Flash Attention (`-fa` vaut `auto` par défaut) ? À vérifier dans la story de mesure H-RAM.
- **Point nouveau** : `--reasoning [on|off|auto]` vaut `auto` par défaut (détecté depuis le template), et `--reasoning-format` aussi. SmolLM3 et Qwen3 ont un mode de pensée. **Correctif proposé (AD-13, `config/modeles/<slug>.toml`)** : figer `reasoning` et les `chat_template_kwargs` (par exemple `enable_thinking`) par modèle, appliquer la même valeur à l'entraînement (AD-7) et les archiver dans `run.json`. Sinon la Baseline et les Runs ne sont pas comparables.

### V-8 — `convert_hf_to_gguf.py` : confirmé, mais il n'est pas dans les binaires

Au tag b11560, `convert_hf_to_gguf.py` ne fait plus que 13 Ko : il importe un paquet `conversion/` du dépôt et insère `gguf-py/` du dépôt dans `sys.path`. Les enregistrements trouvés :

- `conversion/granite.py` : `@ModelBase.register("GraniteMoeHybridForCausalLM", "BambaForCausalLM")`. S'il n'y a pas de couche SSM, l'architecture est rabattue sur `GRANITE` (« some models in this family are non-hybrid »). `ibm-granite/granite-4.0-1b/config.json` a `architectures = ["GraniteMoeHybridForCausalLM"]` et `layer_types` = {attention} seulement : variante dense confirmée ;
- `conversion/mistral3.py` : `@ModelBase.register("Mistral3ForConditionalGeneration", "Ministral3ForCausalLM")`, avec un traitement dédié de `ministral3` (RoPE yarn) ;
- `conversion/llama.py` : `@ModelBase.register("SmolLM3ForCausalLM")`.

**Correctif proposé (AD-6/AD-19)** : les archives `bin-win-*` ne contiennent pas le script Python. Le script `vendor/` doit aussi récupérer les sources au **même tag** (`convert_hf_to_gguf.py`, `conversion/`, `gguf-py/`) dans `vendor/llama.cpp/<tag>/src/`, et l'export doit utiliser ce `gguf-py` plutôt que `gguf` 0.19.0 de PyPI, sinon les deux versions peuvent diverger. La ligne « gguf (convert) 0.19.0 » du tableau Stack devient informative.

### V-9 — bfcl-eval : mécanisme confirmé, intégration prévue infirmée

Ce qui est **confirmé** (README de `berkeley-function-call-leaderboard`, section « For Pre-existing OpenAI-compatible Endpoints », et `base_oss_handler.py`) : `bfcl generate --model … --test-category … --skip-server-setup`, avec les variables `LOCAL_SERVER_ENDPOINT` et `LOCAL_SERVER_PORT` (défaut `localhost:1053`) ou `REMOTE_OPENAI_BASE_URL` / `REMOTE_OPENAI_API_KEY` / `REMOTE_OPENAI_TOKENIZER_PATH`.

Ce qui **infirme** l'intégration telle que décrite (AD-2, AD-16, H-BFCL) :

1. **Dépendances incompatibles avec le lock unique.** `bfcl-eval` 2026.3.23 épingle `numpy==1.26.4` (le socle prévoit numpy 2.5.4) et `mistralai==1.7.0` (l'extra `data` prévoit 3.2.0). Il tire aussi `sentence-transformers` et `faiss-cpu==1.11.0`, donc torch. L'extra `bench` ne peut pas cohabiter avec le socle dans un seul environnement. Les roues Windows cp312 existent (`faiss-cpu`, `tree-sitter`), donc un environnement isolé est viable.
2. **Le chemin de prompt diffère de celui du Harnais.** Les gestionnaires OSS appellent `client.completions.create` (`/v1/completions`) avec un prompt formaté par BFCL (`_format_prompt` propre à chaque famille) et un tokenizer HF chargé par `AutoTokenizer`. Ils ne passent ni par le chat template `--jinja` ni par le parseur d'appels d'outils de llama-server. Le score BFCL ne mesure donc pas la chaîne utilisée par l'Assistant (AD-7, AD-8).
3. **Les modèles doivent être connus de BFCL.** `SUPPORTED_MODELS.md` liste `Qwen3-4B-Instruct-2507` (FC et Prompt) et `Granite-4.0-350m` (un gestionnaire `granite_4.py` existe), mais ni SmolLM3 ni Ministral 3. Un modèle affiné doit être rattaché à un gestionnaire existant ou recevoir un gestionnaire maison.

**Correctif proposé** : sortir `bfcl-eval` du `uv.lock` principal et le placer dans un environnement d'outil isolé (sous-projet `tools/bfcl/` avec son propre lock, lancé en sous-processus par `slmsp.benchmarks`). Dans AD-16, préciser que le score BFCL est obtenu avec le format de prompt de BFCL, puis choisir explicitement entre les gestionnaires « Prompt » de BFCL et le repli déjà prévu par H-BFCL (lanceur maison qui réutilise données et vérificateur AST de BFCL via `/v1/chat/completions` + `tools`). Le second est plus fidèle à la chaîne du Harnais ; je recommande d'en faire le **choix par défaut**.

### V-10 — lm-eval 0.4.13 `hf` + `gguf_file` : paramètre confirmé, usage infirmé

`lm_eval/models/huggingface.py` @ v0.4.13 accepte bien `gguf_file` et le transmet à `from_pretrained`. Le chargement est fait par transformers, et à la v5.19.0, `modeling_gguf_pytorch_utils.py` lève `ValueError("GGUF model with architecture {architecture} is not supported yet.")` pour toute architecture absente de `GGUF_TO_TRANSFORMERS_MAPPING`. La table de `integrations/ggml.py` couvre `llama, mistral, qwen2, qwen2_moe, gpt_oss, lfm2, qwen3, qwen3_moe, falcon, phi3, bloom, t5, stablelm, gpt2, starcoder2, mamba, nemotron, gemma2/3/4, umt5, deci, minimax_m2`. **`granite`, `mistral3` et `smollm3` n'y sont pas.** Seul le témoin Qwen (qwen3) passerait.

L'autre backend, `gguf` (`lm_eval/models/gguf.py`), envoie `/v1/completions` avec `echo: True` pour obtenir les logprobs du prompt. Le README de llama-server @ b11560 ne documente pas `echo` (seulement `n_probs` sur les tokens générés) : **non vérifiable** ici, probablement non supporté.

**Correctif proposé (H-LMEVAL-GGUF)** : l'hypothèse est infirmée pour 3 candidats sur 4. Appliquer le repli par défaut : QCM rapportés avant quantification seulement. L'effet de la quantification se mesure par le sous-ensemble génératif contre llama-server (ifeval, traduction, outils), éventuellement complété par une perplexité `llama-perplexity` sur un texte fixe (présence de l'outil dans les binaires à vérifier).

### V-11 — PEFT 0.21.2 : confirmé, avec une réserve sur l'export PiSSA

`src/peft/tuners/lora/config.py` @ v0.21.2 : `use_rslora: bool`, `use_dora: bool` et `init_lora_weights` accepte `"pissa"` et `"pissa_niter_[n]"` (ainsi que `olora`, `corda`, `loftq`, `eva`…). DoRA est incompatible avec `lora_bias=True`. PEFT avertit qu'avec `use_rslora` + `rank_pattern`/`alpha_pattern`, la conversion post-entraînement de PiSSA (`path_initial_model_for_weight_conversion`) n'est plus possible.

**Réserve (AD-19).** PiSSA modifie les poids de base (modèle résiduel). Fusionner l'adaptateur sur le modèle de base d'origine, comme le décrit AD-19 (« fusion de l'adaptateur en 16 bits »), donne un modèle faux. Pour la variante `pissa` sur base 4 bits, la décomposition se fait en pleine précision, puis on quantifie le modèle résiduel. **Correctif proposé** : dans AD-18/AD-19, la méthode `pissa` enregistre le modèle résiduel (ou convertit l'adaptateur en LoRA équivalent via `path_initial_model_for_weight_conversion`) et l'export fusionne sur ce résiduel. Ajouter un test de non-régression : la perplexité du modèle fusionné doit être proche de celle du modèle PEFT. Je n'ai pas vérifié à ce tag la prise en charge de DoRA sur bnb 4 bits ; la story « Environnement d'entraînement » doit l'essayer.

### V-12 — TRL 1.15 : `ORPOTrainer` déplacé

Dans l'arbre @ v1.15.0, ORPO n'existe plus que sous `trl/experimental/orpo/` (`orpo_trainer.py`, `orpo_config.py`). `trl/__init__.py` exporte `SFTTrainer` et `DPOTrainer`, mais pas `ORPOTrainer`. La docstring parle de `experimental.orpo.ORPOConfig`. **Correctif proposé (AD-18)** : écrire « ORPO via `trl.experimental.orpo.ORPOTrainer` (API expérimentale, sujette à changement) » et figer la version de TRL pour toute la campagne. L'arbre @ v1.13.0 contient aussi `trl/experimental/orpo/` (vérifié).

### V-13 — `assistant_only_loss` : infirmé pour Granite 4.0 1B et Ministral 3 3B

`SFTConfig.assistant_only_loss` existe @ v1.15.0 (et @ v1.13.0). Si le chat template n'a pas de marqueurs `{% generation %}`, `SFTTrainer` appelle `get_training_chat_template()`. Celle-ci ne sait remplacer que des templates qu'elle connaît (`trl/chat_templates/*_training.jinja` : cohere, deepseek, gemma, glm4moe, gptoss, lfm2, llama3, phi3, qwen2.5/3/3.5/3.6/3.8, qwen3_instruct_2507, smolvlm…) et lève sinon :

> `ValueError: The chat template is not training-compatible (missing prefix-preservation or {% generation %} markers) and patching is not supported for this template. Please manually modify the chat template for training.`

Contrôle des `chat_template.jinja` officiels sur Hugging Face :

| Modèle | Marqueurs `{% generation %}` | Template de substitution TRL | Résultat avec `assistant_only_loss=True` |
| --- | --- | --- | --- |
| `ibm-granite/granite-4.0-1b` | absents | aucun | **ValueError** |
| `mistralai/Ministral-3-3B-Instruct-2512` | absents | aucun | **ValueError** |
| `HuggingFaceTB/SmolLM3-3B` | présents | inutile | OK |
| Qwen3 4B (témoin) | selon la variante | `qwen3*_training` | OK |

AD-7 interdit pourtant tout « gabarit de rendu maison ». **Correctif proposé (AD-7, AD-18)** : autoriser une « variante d'entraînement » du template officiel qui n'ajoute **que** les balises `{% generation %}…{% endgeneration %}` (fin de tour incluse, voir l'avertissement TRL sur le jeton de fin de tour). Elle serait versionnée dans `config/modeles/<slug>/`, avec un test qui vérifie que son rendu, balises retirées, est identique octet pour octet à celui du template officiel sur les traces du calibrage. Autre option : calculer le masque assistant hors de TRL (rendu incrémental de préfixes) et passer `assistant_masks` dans le jeu. Dans les deux cas, le GGUF embarque le template officiel, sans les balises.

### V-14 — Unsloth : Windows confirmé, co-installation infirmée

Le README d'Unsloth (main) documente une installation Windows native (`uv venv`, `uv pip install torchao`, puis `uv pip install unsloth --torch-backend=auto`). Les métadonnées d'unsloth 2026.10.3 dépendent de `triton-windows` et de `xformers` sur win32. Mais **unsloth 2026.10.3 et unsloth-zoo 2026.10.3 épinglent `transformers<=5.17.0` et `trl<=1.13.0`** (ainsi que `torch<2.15.0` et `datasets<5.0.0`). Le tableau Stack retient transformers 5.19.0 et TRL 1.15.0 : l'extra `train` « unsloth en option » ne se résout pas.

**Correctif proposé (Stack, AD-18)** : pour garder des Runs comparables (même TRL et même transformers pour toutes les méthodes, exigence d'équité FR-34), figer toute la campagne sur **transformers 5.17.0 et TRL 1.13.0**. TRL 1.13 a `assistant_only_loss` et `trl/experimental/orpo/` (vérifié). L'autre option est un extra `unsloth` déclaré en conflit (`[tool.uv] conflicts`), mais la variante `qlora-unsloth` ne tournerait alors pas sur la même pile, ce qu'il faut consigner dans le Comparatif. La note de README sur `torchao` sous Windows (installé d'abord, sinon résolution silencieuse d'un vieil Unsloth) est à reprendre dans la story d'environnement.

### V-15 — bitsandbytes 0.50.2 sous Windows : confirmé (sur le papier)

PyPI publie `bitsandbytes-0.50.2-…-win_amd64.whl`. `docs/source/installation.mdx` liste « Windows x86-64 » pour CUDA 11.8–12.6 (sm50…sm90, dont sm86), 12.8 et 13.0–13.2. La RTX 3050 (Ampere, sm86) est couverte. H-WIN-TRAIN reste à mesurer (pilote 610 et torch CUDA réellement installé, voir V-17).

### V-16 — Versions PyPI : confirmées, sauf `uv`

Vérifiées le 2026-10-12 via l'API JSON de PyPI, toutes égales au tableau : mcp 2.3.0, anthropic 1.13.0, mistralai 3.2.0, trl 1.15.0, peft 0.21.2, transformers 5.19.0, accelerate 1.15.0, bitsandbytes 0.50.2, unsloth 2026.10.3, lm-eval 0.4.13, bfcl-eval 2026.3.23, sacrebleu 2.6.0, pywebview 6.2.1, torch 2.14.1, numpy 2.5.4, pydantic 2.14.1, jsonschema 4.26.0, psutil 7.2.2, nvidia-ml-py 13.615.71, python-dotenv 1.2.4, duckdb 1.5.6, pyarrow 26.0.0, huggingface-hub 2.2.0, gguf 0.19.0, codecarbon 3.3.1, pyinstaller 6.22.3, pytest 9.1.1, ruff 0.17.0, usearch 2.26.4.

**Écart :** `uv` 0.12.23 est la version **installée** sur le poste (2026-10-03) ; la dernière publiée est **0.13.0** (2026-10-09). C'est sans conséquence, mais la ligne doit dire « installé » ou passer à 0.13.0. Il manque aussi `httpx2` (2.13.1 sur PyPI) au tableau, alors qu'AD-4 en dépend directement.

### V-17 — torch CUDA sous Windows : infirmé pour PyPI

La roue `torch-2.14.1-cp312-cp312-win_amd64.whl` de PyPI pèse 124 Mo, et les dépendances `nvidia-*` sont conditionnées à `platform_system == "Linux"`. C'est une construction **CPU seule**. Le torch CUDA pour Windows vient de l'index PyTorch (`download.pytorch.org`), hôte que je n'ai pas pu consulter (hors périmètre réseau autorisé) : **non vérifiable** pour la disponibilité exacte de 2.14.1 en cu12x/cu13x.

**Correctif proposé (AD-2, AD-4, Environnements)** : déclarer l'index PyTorch dans `pyproject.toml` (`[[tool.uv.index]]` explicite + `[tool.uv.sources] torch = { index = … }` pour l'extra `train`, et pour `bench` puisque `lm-eval[hf]` exige torch et transformers). Ajouter `download.pytorch.org` à la liste D1.5 / profil `outillage` (à faire valider par Anaël, car D1.5 est une liste fermée).

### V-18 — pywebview 6.2.1 : confirmé

`webview/__init__.py` @ 6.2.1 : `create_window(..., js_api: Any = None, ...)`. `webview/window.py` : `Window.evaluate_js(script, callback=None)`, `Window.run_js(script)` et `Window.expose(*functions)`. Suggestion pour J4 : pour pousser un flux de jetons, `run_js` (sans attente de résultat) ou un regroupement des évènements coûte moins cher qu'un `evaluate_js` par jeton.

### V-19 — Artefacts Hugging Face : confirmé, avec une simplification

- `ggml-org/bge-m3-Q8_0-GGUF` contient `bge-m3-q8_0.gguf` : confirmé.
- `mistralai/Ministral-3-3B-Instruct-2512-GGUF` existe avec `…-Q4_K_M.gguf`, `Q5_K_M`, `Q8_0`, `BF16` et `BF16-mmproj` : confirmé (la question ouverte du spine est juste).
- `mistralai/Ministral-3-3B-Instruct-2512/config.json` : `quantization_config.quant_method = "fp8"`, vision et `lm_head` exclus : la contrainte FP8 d'AD-18 est confirmée. **Mais `mistralai/Ministral-3-3B-Instruct-2512-BF16` existe.** **Correctif proposé (AD-18)** : remplacer « conversion bf16 préalable, méthode consignée » par « partir du dépôt officiel `-BF16` » (une conversion maison seulement en repli). On supprime ainsi une étape et une source d'écart.

## Correctifs proposés pour le spine (récapitulatif)

| Priorité | Section | Correctif |
| --- | --- | --- |
| Bloquant | Stack, AD-18 | Figer transformers 5.17.0 et TRL 1.13.0 pour toute la campagne (contrainte Unsloth), ou isoler Unsloth dans un extra en conflit et consigner l'écart. |
| Bloquant | AD-7, AD-18 | Autoriser une variante d'entraînement du template officiel, limitée aux balises `{% generation %}` et testée par égalité de rendu, pour Granite 4.0 1B et Ministral 3 3B ; ou un masque assistant calculé hors de TRL. |
| Bloquant | AD-2, AD-16, H-BFCL | Placer bfcl-eval dans un environnement isolé (lock séparé) ; faire du lanceur maison (données et vérificateur AST de BFCL, `/v1/chat/completions` + `tools`) le choix par défaut. |
| Bloquant | H-LMEVAL-GGUF | Hypothèse infirmée pour granite, mistral3 et smollm3 dans transformers 5.19 : appliquer le repli par défaut. |
| Bloquant | AD-2, AD-4, Environnements | Index PyTorch CUDA dans `pyproject.toml` ; `download.pytorch.org` à ajouter à D1.5 (validation d'Anaël). |
| Important | AD-6, Stack | b11560 est une pré-version : figer b11429 (= v0.6.0) ou assumer la nightly ; télécharger aussi l'archive `cudart`. |
| Important | AD-6, AD-19 | Récupérer `convert_hf_to_gguf.py` + `conversion/` + `gguf-py/` au même tag (absents des binaires) et utiliser ce `gguf-py`. |
| Important | AD-19 | Export PiSSA : fusion sur le modèle résiduel ou conversion via `path_initial_model_for_weight_conversion`, avec un test de perplexité. |
| Important | AD-12/AD-13, config modèles | Figer `--reasoning` et `chat_template_kwargs` (pensée) par modèle, identiques à l'entraînement et à l'inférence. |
| Mineur | AD-18 | `trl.experimental.orpo.ORPOTrainer` (API expérimentale). |
| Mineur | AD-4 | mistralai : `client=` / `async_client=` ; transferts hf-xet hors de `slmsp.net` ; journalisation de l'outillage au niveau de l'appel. |
| Mineur | AD-8, AD-10 | Inscrire la version de protocole MCP négociée dans les cassettes ; un changement déclenche le repli FR-9. |
| Mineur | AD-18 | Ministral 3 : partir de `mistralai/Ministral-3-3B-Instruct-2512-BF16`. |
| Mineur | Stack | `uv` 0.13.0 (ou mention « installé ») ; ajouter `httpx2` 2.13.1. |

## Ce qui n'a pas pu être vérifié

- Disponibilité de torch 2.14.1 CUDA pour Windows sur `download.pytorch.org` (hôte hors périmètre).
- Exigence de Flash Attention pour un cache V quantifié dans llama-server b11560.
- Prise en charge des logprobs de prompt (`echo`) par `/v1/completions` de llama-server (non documentée).
- DoRA sur base bnb 4 bits dans PEFT 0.21.2 (à essayer dans la story d'environnement).
- Comportement réel sur le poste (pilote 610, RTX 3050) : relève des hypothèses H-WIN-TRAIN, H-TOOLS, H-EMB et H-RAM, que le spine prévoit déjà de mesurer.
