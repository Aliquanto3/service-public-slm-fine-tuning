# Reprise du projet sur un deuxième PC

PC portable : 32 Go de RAM DDR4, GPU NVIDIA de 6 Go de VRAM.
- Le code et les tests tournent sur CPU.
- Les benchmarks et l'essai QLoRA des modèles de moins de 2B doivent tenir sur 6 Go avec un batch fixe.
- Benchmarks GGUF : sur GPU, `--variante-llamacpp cuda --parallele 4` (requêtes simultanées, `-c` de llama-server multiplié par N, donc plus de VRAM) ; mesures de charge (`measure run`) toujours sur CPU, séquentielles.
- Si le fine-tuning bloque sur 6 Go, reprendre sur la tour.

Tout vient de GitHub, sans copie de disque à disque :
- le code et les runs : dépôt privé `Aliquanto3/service-public-slm-fine-tuning` ;
- l'état machine : release `etat-2026-10-17` du dépôt **privé** `Aliquanto3/slmsp-etat`, environ 12 Mo. Le dépôt du projet est public : l'état n'y est jamais joint. Elle contient les journaux Mistral et le registre des budgets, indispensables pour la provenance et les plafonds ;
- les sources figées du Jeu d'évaluation `data/raw/eval-sources` (avec `INDEX.json`) : release `etat-2026-10-17b` du même dépôt, environ 900 Mo. Elles ne se reconstruisent pas : `construire_jeu.py sources` n'épingle pas les révisions et un nouveau téléchargement fait échouer 120 tests `tests/eval_outils` ;
- modèles, llama.cpp, sources et index : retéléchargés ou reconstruits par `slmsp`, avec des SHA-256 épinglés.

## 1. Ce que fait Anaël (une fois)

1. Installer Git, uv, GitHub CLI et Claude Code (avec le plugin `agent-cost-kit`), et avoir un pilote NVIDIA à jour.
   ```powershell
   winget install Git.Git astral-sh.uv GitHub.cli
   gh auth login
   ```
2. Cloner au même chemin que sur la tour. La mémoire de Claude Code est rangée selon ce chemin.
   ```powershell
   cd C:\Users\Utilisateur\Documents\GitHub
   gh repo clone Aliquanto3/service-public-slm-fine-tuning
   ```
3. Copier `.env.example` en `.env`, puis remplir `MISTRAL_API_KEY`, `ANTHROPIC_API_KEY` et `HF_TOKEN`. Claude ne lit jamais ce fichier.
4. Ouvrir Claude Code dans le dépôt (Opus, effort medium) et coller le prompt de la section 4.

## 2. Ce que fait Claude Code (installation)

Lancer les commandes dans l'ordre, en arrêtant au premier échec. Après `uv sync`, toujours utiliser `uv run --no-sync` : un `uv run` simple resynchronise sans extras.

Les extras `fetch` et `train` sont déclarés en conflit dans `pyproject.toml` (transformers 5.17 exige `huggingface-hub<2`, `fetch` épingle la 2.2.0) : ils ne s'installent jamais ensemble. On synchronise donc deux fois : d'abord avec `fetch` pour les téléchargements, puis avec `train` pour l'entraînement et les benchmarks (lm-eval importe torch).

```powershell
git config core.longpaths true
powershell -NoProfile -ExecutionPolicy Bypass -File outils/migration/restaurer-etat.ps1
# Phase 1 : téléchargements (sans train)
uv sync --extra fetch --extra data --extra judge --extra bench --extra app
uv run --no-sync python -m playwright install msedge
uv run --no-sync slmsp fetch llamacpp
uv run --no-sync slmsp fetch sources
uv run --no-sync slmsp index build
uv run --no-sync slmsp fetch benchmarks
uv run --no-sync slmsp bench cache-hf
uv run --no-sync slmsp fetch modeles bge-m3 bge-m3-f16 granite-4.0-1b minicpm5-1b
uv run --no-sync slmsp fetch modeles granite-4.0-1b minicpm5-1b --f16
# Phase 2 : environnement de travail, comme sur la tour (retire fetch, installe torch cu130)
uv sync --extra data --extra judge --extra bench --extra train --extra gdn --extra app
```

L'extra `gdn` (triton-windows 3.8.0.post29, flash-linear-attention 0.5.2) fournit les noyaux du chemin rapide Gated DeltaNet des Qwen3.5 : sans lui, `train run` refuse un modèle à couches `linear_attention` (sauf `repli_torch = true`, plus lent, `longueur_max <= 4096`). Il est en conflit avec `fetch` pour la même raison que `train` et ne figure donc jamais en phase 1.

`bench cache-hf` remplit le cache HF des jeux de `lm_eval` (`<models>/.cache-hf`, environ 515 Mo) pour chaque dépôt de `[options.jeux_hf]` : `snapshot_download` à la révision épinglée, `refs/main` sur cette révision, `load_dataset` en ligne (cache `datasets`), puis relecture de chaque jeu hors ligne (`HF_DATASETS_OFFLINE=1`, `HF_HUB_OFFLINE=1`) ; la commande échoue sinon. Elle est idempotente : un jeu déjà lisible hors ligne n'est pas retéléchargé. C'est une sous-commande de `bench` (le paquet `fetch` s'interdit `snapshot_download` et les sous-processus). Elle se lance en **phase 1** (venv `fetch` + `bench`, `datasets` vient de lm-eval), car elle a besoin du réseau et d'`huggingface-hub` 2.2.0 ; le cache vit dans `models/`, donc la phase 2 le retrouve. Sans elle, `bench run` refuse les benchmarks HF (`verifier_cache_hf`). Ce cache n'est ni exporté ni publié avec l'état : il se reconstruit par cette commande (`restaurer-etat.ps1` ne le copie pas).

Pour télécharger un modèle plus tard, repasser par la phase 1, puis revenir à la phase 2.

`restaurer-etat.ps1` restaure aussi `data/raw/eval-sources`. Sur un PC déjà restauré avec l'ancien script (le portable), ajouter seulement les sources, sans toucher au reste ni écraser un fichier existant :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File outils/migration/restaurer-etat.ps1 -SeulementEvalSources
$env:SLMSP_EVAL_SOURCES = "$PWD\data\raw\eval-sources"   # sinon 244 tests sont ignorés
```

Ne pas lancer `construire_jeu.py sources` pour reconstruire ce dossier.

Points de vigilance :
- **Vecteurs de l'Index.** `index build` reconstruit l'Index depuis les parquet MediaTech, avec des vecteurs fournis par MediaTech et non recalculés. Vérifier avec `slmsp index info` que la version est `20260926`, comme sur la tour.
- **Candidats EuroLLM-1.7B, CroissantLLM et Qwen3.5-0.8B.** Leurs fiches ne sont que sur la branche `feat/modeles-moins-2b` (travail interrompu, non relu). Les télécharger depuis cette branche, au moment de les traiter.
- **Torch et le pilote.** Si la roue CUDA de torch ne correspond pas au pilote, voir la règle `pytorch` de `config/reseau.toml`.

## 3. Vérifier

```powershell
uv run --no-sync python outils/controle_rapide.py
uv run --no-sync slmsp budget etat     # campagne baseline-2026-10-17, génération Mistral 10,64 € dépensés
uv run --no-sync slmsp index info
nvidia-smi
$env:SLMSP_EVAL_SOURCES = "$PWD\data\raw\eval-sources"
uv run --no-sync pytest -q --tb=line -p no:warnings   # suite complète, une fois (4 992 passés sur la tour)
```

Si `slmsp budget etat` montre un registre vide, la restauration a échoué : ne lancer **aucun** appel payant.

## 4. Prompt de reprise (nouvelle session Claude Code, Opus, effort medium)

> Reprise du projet slmsp sur ce PC portable (32 Go RAM, GPU 6 Go). Le dépôt est cloné et `.env` est rempli (ne le lis jamais). Lis `docs/reprise-deuxieme-pc.md` et exécute toi-même l'installation (section 2) puis les vérifications (section 3), en t'arrêtant au premier échec pour me le signaler. Ensuite lis la section « Passation » de `_bmad-output/implementation-artifacts/etat-run-2026-10-16.md` et `sprint-status.yaml`, rappelle-moi les décisions en attente, et enchaîne le travail restant dans l'ordre de la passation. Pour l'étape 2 (candidats < 2B), reprends la branche `feat/modeles-moins-2b` (commit WIP non relu). Respecte CLAUDE.md : enchaînement dev-story → second-avis → reviewer, D1 (Claude ne génère jamais de données d'entraînement), appels payants par l'orchestrateur seulement, toujours `uv run --no-sync`, batch lm_eval fixe sur 6 Go de VRAM (jamais `auto`). Fais-moi un point avant tout appel payant non couvert par un plafond existant.

## 5. Particularités du portable (6 Go de VRAM)

- **lm_eval en HF bf16.** Un batch fixe est obligatoire : `lm_eval_batch_size` dans `config/modeles/<slug>.toml`. Partir de 2 ; minicpm5-1b est à 4. En `auto`, on a vu un OOM même sur 8 Go.
- **QLoRA (story 11.2).** Charger en 4 bits, avec le gradient checkpointing, batch 1 et accumulation. Si l'OOM persiste à la séquence cible, revenir sur la tour.
- **Entraînement 4096 à 8192 tokens.** `precision_base = "bf16"` dans le TOML de run (qlora, dora, orpo, rslora) évite le cast fp32 de `prepare_model_for_kbit_training` ; MiniCPM5-2B tient alors 4096 tokens en 3,72 Gio et 8192 en 4,69. À valider par un court run ; la sonde `slmsp train sonde-env --precision-base les-deux` mesure les deux variantes.
- **Mesures CPU (H-RAM).** Elles restent indicatives : le portable a 32 Go de RAM, la cible 16 Go.

## Annexe : transfert par disque

`outils/migration/exporter-etat.ps1` et `importer-etat.ps1` copient le même état, plus les modèles et l'index, par un disque externe : environ 25 Go avec `-AvecModeles`. C'est utile seulement si le réseau est lent.

## Annexe : publier un nouvel état

Sur le PC source, `outils/migration/publier-etat.ps1 [-Date AAAA-MM-JJ]` construit l'archive, refuse tout `.env` ou motif de clé, crée au besoin le dépôt privé `Aliquanto3/slmsp-etat` et publie la release `etat-<date>` sans la marquer « Latest ». Avec `-SansPublier`, il s'arrête après le SHA-256. Reporter ensuite le tag, le nom d'archive et le SHA-256 en valeurs par défaut de `restaurer-etat.ps1`.
