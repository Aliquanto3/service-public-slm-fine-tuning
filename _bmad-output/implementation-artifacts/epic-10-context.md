# Epic 10 Context: Runs d'entraînement et export GGUF

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Permettre à Anaël de lancer un Run d'entraînement décrit entièrement par un fichier TOML : Modèle de base, méthode M1 à M4 ou variante, hyperparamètres et graine. Chaque Run mesure son coût (durée, débit, VRAM, énergie) et peut reprendre sur checkpoint. L'adaptateur obtenu est ensuite fusionné et exporté en GGUF (F16 puis Q4_K_M), dans le format exact de l'Assistant, pour être réévalué par le même banc. Avant le premier Run, l'epic mesure deux hypothèses : H-WIN-TRAIN (la pile d'entraînement fonctionne-t-elle sous Windows natif ?) et H-MASQUE (le masque de perte isole-t-il exactement les tours `assistant` ?). Il sert de socle à l'essai M1 QLoRA de la nuit et au Comparatif (Epic 11).

## Stories

- Story 10.1 : Environnement d'entraînement Windows et mesure H-WIN-TRAIN
- Story 10.2 : Rendu en tokens et masque de perte (H-MASQUE)
- Story 10.3 : Mesures de coût d'un Run (FR-33)
- Story 10.4 : Runs d'entraînement configurables (`slmsp train run`)
- Story 10.5 : Variante QLoRA Unsloth en environnement isolé
- Story 10.6 : Export GGUF et contrôle après quantification

## Requirements & Constraints

- **Méthodes sans code** : `methode` ∈ {`qlora` (M1), `lora` (M2, LoRA bf16 sur le plus petit candidat), `dora` (M3, sur base 4 bits), `orpo` (M4, après SFT)} ; variantes `rslora`, `pissa`, `qlora-unsloth`. Passer d'une méthode à l'autre ne change que le TOML.
- **Comparaison équitable** : une campagne partage la version du jeu, l'ordre des exemples (graine), la longueur maximale, le SHA du chat template et la version du masque. Un Run refuse de démarrer si l'un de ces éléments diffère des Runs déjà enregistrés pour la campagne. ORPO déroge au protocole, et cette dérogation est documentée.
- **Coût (FR-33)** : un callback unique mesure le débit en tokens/s hors padding après 10 pas de chauffe, la VRAM maximale (maximum entre `torch.cuda.max_memory_*` et l'échantillonnage NVML), l'énergie en Wh (puissance NVML échantillonnée toutes les 200 ms) et la durée. Les mesures vont dans `metriques.jsonl` et `couts.json`. Le protocole se règle dans `config/entrainement.toml`.
- **Reprise** : `--reprendre <run_id>` relance sur le dernier checkpoint du même dossier, en ajout seul.
- **Données (D1.1, AD-24)** : `train` lit uniquement `data/train/<version>/`, `models/` et, en lecture seule, le journal `appels-mistral.sqlite`. Toute autre lecture lève `LectureInterdite`. Au chargement, le Run vérifie que le MANIFEST vient d'un run `data-build` et recontrôle les `appel_ids`. Sans jeu construit, le Run est consigné comme bloqué : aucun jeu de dépannage, jamais. Les fixtures de test sont des tokens aléatoires générés dans `tmp_path`, jamais des exemples rédigés.
- **Export (FR-35)** : fusion en 16 bits avant toute conversion. Le GGUF F16 est conservé, puis quantifié en Q4_K_M. Le SHA du chat template embarqué doit être égal à celui du tokenizer d'entraînement. `ft:<export_run_id>` doit être résolu pour `f16` et `q4_k_m`, et le tool calling est re-testé après quantification (sonde R-001).
- **Interdits** : ne jamais définir `save_total_limit` ; ne jamais supprimer de checkpoint ni d'artefact ; aucune publication (`push_to_hub = False`) ; `report_to = "none"` et télémétrie coupée pour toute exécution d'entraînement.

## Technical Decisions

- **H-WIN-TRAIN, mesurée avant tout Run (10.1)** : `slmsp train sonde-env` exécute un pas QLoRA (nf4 4 bits + LoRA) sur des tokens aléatoires avec Granite 4.0 1B, sous le verrou GPU. Le run va dans `runs/train-sonde/<run_id>/`, avec une perte finie et la VRAM maximale relevée. `--unsloth` tente un pas équivalent dans `envs/unsloth`, en sous-processus. Si un échec est constaté, appliquer le repli et le consigner dans le journal :
  - sans Unsloth, TRL + PEFT seuls, et la 10.5 est close comme bloquée ;
  - sans bitsandbytes, LoRA bf16 sur le 1B seulement.

  Les méthodes indisponibles sont listées.
- **Matériel : RTX 3050 8 Go, architecture Ampere (capacité 8.6)**. La carte gère bf16 mais pas FP8. Le chargement refuse avec un message clair :
  - les poids FP8 (préférer le dépôt officiel bf16, sinon conversion consignée) ;
  - toute couche Mamba (Granite H hybride écarté) ;
  - l'encodeur vision de Ministral 3, s'il n'est pas exclu.

  Les poids d'entraînement sont dans `models/<slug>/hf-bf16/` (ou `hf/`).
- **Windows 11 natif, sans WSL** : aucun recours à WSL ni à Linux. Une brique qui ne fonctionne pas nativement est consignée, écartée, et le travail passe à la suite. Utiliser `pathlib` partout et un encodage explicite. Les sous-processus tournent sans fenêtre (`CREATE_NO_WINDOW`), dans un Job Object, et reçoivent `env_sous_processus()`. Ne jamais appeler la commande `python` du PATH : toujours `uv run`.
- **Verrou GPU (`gpu.lock`)** : verrou exclusif dans `SLMSP_VAR_DIR` (`%LOCALAPPDATA%\slmsp\var\`). Le prennent la sonde 10.1, chaque Run (10.4, 10.5) et la fusion de l'export (10.6). Une seconde commande CUDA attend ou échoue avec un message clair (code de sortie 5, ressource occupée). Sur 8 Go, deux charges GPU superposées provoquent des erreurs de mémoire.
- **Extras uv** :
  - la pile d'entraînement est dans l'extra `train` : torch 2.14.1 depuis l'index PyTorch CUDA `pytorch-cu130` (`explicit = true`), transformers 5.17.0, trl 1.13.0, peft 0.21.2, bitsandbytes 0.50.2, accelerate 1.15.0 ;
  - **`train` est déclaré en conflit avec `fetch`** dans `[tool.uv] conflicts`. transformers 5.17 exige `huggingface-hub<2`, alors que `fetch` épingle la 2.2.0, donc les deux extras ne s'installent jamais ensemble. Installer avec `uv sync --extra train` seul. Les poids doivent déjà être sous `models/`, téléchargés par `fetch` dans une synchronisation séparée. Ne pas toucher à ce conflit : c'est à Anaël de le trancher ;
  - les tests importent ces bibliothèques via `pytest.importorskip`.

  La 10.6 ajoute `gguf` à l'extra `train`, par chemin vers `vendor/llama.cpp/<tag>/src/gguf-py`, jamais depuis PyPI.
- **Runtime protégé (AD-2)** : torch, transformers, trl, peft, bitsandbytes et unsloth ne sont importés que dans `slmsp.train` (couche 3). Ils n'entrent jamais dans la fermeture runtime (`core`, `net`, `budget`, `inference`, `index`, `mcp`, `harness`, `app`). Le test AST le vérifie.
- **TRL + PEFT, socle de comparaison** :
  - les méthodes passent par `BitsAndBytesConfig` et `LoraConfig` (`use_dora`, `use_rslora`, `init_lora_weights="pissa"`), puis par l'entraîneur TRL ;
  - ORPO passe par `trl.experimental.orpo` ;
  - `assistant_only_loss` de TRL n'est **pas** utilisé, faute de balises `generation` dans les templates de Granite et de Ministral.
- **Rendu et masque (AD-7, H-MASQUE)** :
  - le rendu passe uniquement par le chat template officiel, `tokenizer.apply_chat_template(messages, tools=...)`, avec les `chat_template_kwargs` de `config/modeles/<slug>.toml` ;
  - `tools` vient de `config/outils-mcp.toml`, et son SHA est inscrit dans `run.json` ;
  - le masque a une seule implémentation, `slmsp.train.masque` : rendu incrémental, labels à −100 hors des tours `assistant`. Ces tours comprennent les `tool_calls` sérialisés et la fin de tour ;
  - le rendu doit être identique à celui de `llama-server --jinja` ;
  - repli si le test échoue : une variante d'entraînement du template, limitée aux balises `generation`, prouvée par égalité de rendu avec le template officiel.
- **Unsloth en variante isolée (10.5)** :
  - l'environnement uv `envs/unsloth/` est hors du lock principal : unsloth 2026.10.3, transformers 5.17.0, trl 1.13.0, torch CUDA ;
  - il est appelé en sous-processus par `uv run --project envs/unsloth` et échange des fichiers JSON : configuration et jeu pré-tokenisé avec ses labels ;
  - les `input_ids` et `labels` sont produits par `train.rendu` et `train.masque`, donc le masque est identique à celui de M1 ;
  - `slmsp` n'importe jamais `unsloth`. Cette variante sert à mesurer la vitesse : ce n'est pas une méthode comptée.
- **Export (10.6)** :
  - la fusion se fait sur la base bf16 d'origine (LoRA, QLoRA, DoRA) ou sur le modèle résiduel (PiSSA) ;
  - la conversion et la quantification passent obligatoirement par `inference.serveur.convertir_hf_vers_gguf` et `quantifier`, avec les outils du tag llama.cpp b11429 (`config/llamacpp.toml`). `train` ne lance aucun processus llama.cpp lui-même ;
  - l'espace disque est vérifié avant toute écriture de plus de 1 Go.
- **Artefacts (AD-21, AD-25)** :
  - les runs écrivent sous `runs/train/<run_id>/` (`checkpoints/`, `adaptateur/`, `metriques.jsonl`, `couts.json`, `log.jsonl`) et sous `runs/export/<run_id>/` (fusionné 16 bits, `modele-f16.gguf`, `modele-q4_k_m.gguf`) ;
  - `run_id` = `AAAAMMJJ-HHMMSS-<nom du TOML>-<4 hex>` ;
  - `run.json` (`RunManifest`) contient la config résolue, la graine, l'environnement et le SHA du chat template, avec `statut` ∈ {`en_cours`, `complet`, `partiel-budget`, `partiel-erreur`, `interrompu`, `degrade`}.
- **Zones de fichiers du module `train/`** (une story ne modifie que sa zone) :

  | Story | Fichiers |
  | --- | --- |
  | 10.1 | `train/environnement.py`, `cli/train.py` (`sonde-env`, et `run` déclaré non implémenté), `envs/unsloth/{pyproject.toml,sonde.py}` |
  | 10.2 | `train/rendu.py`, `train/masque.py` |
  | 10.3 | `train/couts.py`, `train/config.py` (création, `ConfigCouts`), `config/entrainement.toml` |
  | 10.4 | `train/config.py` (complète, `RunConfig`), `train/methodes.py`, `train/chargement.py`, `train/run.py`, `cli/train.py`, `config/runs/m{1..4}-*-granite-4.0-1b.toml` |
  | 10.5 | `envs/unsloth/entrainer.py`, `train/methodes.py` (branche `qlora-unsloth`), `config/runs/v-qlora-unsloth-granite-4.0-1b.toml` |
  | 10.6 | `train/export.py`, `cli/export.py`, `pyproject.toml` |

  Les tests vont sous `tests/train/`. `train` ne peut pas importer `measure`, `evaluation` ni `data` (même couche) : il échange avec eux des artefacts. Toutes ses lectures passent par `core.artefacts.lire(lecteur="train")`.

## Cross-Story Dependencies

- **10.1** dépend de 8.1 (modèles préparés). Elle débloque 10.2 et 10.3, qui ont des zones disjointes et peuvent tourner en parallèle.
- **10.2** dépend aussi de 4.1 (format des messages, `harness.prompts`).
- **10.4** dépend de 10.2 et 10.3. Elle complète `train/config.py`, créé par la 10.3, et reprend `cli/train.py`, créé par la 10.1 : jamais en parallèle avec ces stories. Son exécution réelle exige un jeu construit (9.6, puis 9.8 pour `data/train/v1`).
- **10.5** et **10.6** dépendent de 10.4 et ont des zones disjointes : elles peuvent tourner en parallèle. La 10.5 n'est pas nécessaire à l'essai M1 et fait partie des premières coupes en cas de retard. Elle est close comme bloquée si H-WIN-TRAIN est infirmée pour Unsloth.
- **10.6** dépend aussi de 2.2 (lanceurs llama.cpp), de 8.2 (sonde d'outils) et de `evaluation.modele_ref` (5.3).
- **Hors epic** : la 11.2 (essai M1 QLoRA) consomme 10.6, 9.8, 8.3 et 11.1. La 11.1 charge les runs `train` et `export`. Le GPU est partagé avec 8.3 et 9.8 par `gpu.lock`.
