# Reprise du projet sur un deuxième PC

Procédure pour reprendre les travaux sur le PC portable : 32 Go de RAM DDR4 et GPU NVIDIA de 6 Go de VRAM.
- Le code et les tests tournent sur CPU.
- Les benchmarks et l'essai QLoRA des modèles de moins de 2B doivent tenir sur 6 Go de VRAM avec un batch fixe.
- Si le fine-tuning bloque sur 6 Go, il reprend sur la tour.

Ce qui vit dans git est cloné. Le reste se copie avec `outils/migration/` ou se retélécharge avec `slmsp fetch`.

## 1. Sur la tour, avant de partir

1. Laisser finir les traitements en cours (campagne 9.8, benchmarks). Le script d'export refuse de tourner s'il en reste.
2. Committer et pousser :
   ```powershell
   git status
   git push
   ```
   `runs/` et `data/cassettes/` sont versionnés.
3. Exporter l'état hors git :
   ```powershell
   powershell -File outils\migration\exporter-etat.ps1 -Destination E:\slmsp-transfert -AvecModeles
   ```
   Contenu de l'export :

   | Élément | Taille | Importance |
   |---|---|---|
   | `var` : budget, journaux Mistral (`appels-mistral*.sqlite`), verdicts du Juge, requêtes sortantes | ≈ 40 Mo | **Indispensable.** Sans les journaux, build ne peut plus prouver la provenance des données, et il faut tout régénérer en payant. |
   | `index/` | 456 Mo | — |
   | `data/raw`, `data/cache` | ≈ 0,9 Go | Retéléchargeable avec `slmsp fetch sources`. La copie évite d'attendre. |
   | `data/train` | — | — |
   | Mémoire Claude Code du projet et `CLAUDE.md` globaux | — | — |
   | Avec `-AvecModeles` : modèles de moins de 2B et BGE-M3 (bge-m3, bge-m3-f16, granite-4.0-1b, minicpm5-1b, qwen3.5-0.8b, eurollm-1.7b, croissantllm-chat) | ≈ 30 Go | — |

   `.env` n'est **jamais** copié.

## 2. Sur le portable

### Prérequis

- Git
- uv
- gh
- un pilote NVIDIA récent (`nvidia-smi` doit répondre)
- Claude Code avec le plugin `agent-cost-kit`
- Inno Setup seulement pour reconstruire l'installateur : `outils/installer_inno_setup.py`

### Cloner au même chemin que sur la tour

Cloner au même chemin garde la clé de la mémoire Claude Code.

```powershell
cd C:\Users\<vous>\Documents\GitHub
gh repo clone Aliquanto3/service-public-slm-fine-tuning
cd service-public-slm-fine-tuning
```

### Importer l'état

```powershell
powershell -File outils\migration\importer-etat.ps1 -Source E:\slmsp-transfert
```

Remettre les `CLAUDE.md` globaux s'ils manquent. Ils se trouvent dans `E:\slmsp-transfert\claude\` :
- `CLAUDE-global.md` va dans `%USERPROFILE%\.claude\CLAUDE.md` ;
- `CLAUDE-GitHub.md` va dans `Documents\GitHub\CLAUDE.md`.

### Secrets

Copier `.env.example` en `.env`, puis remplir à la main `MISTRAL_API_KEY`, `ANTHROPIC_API_KEY` et `HF_TOKEN`.

### Environnement Python

```powershell
uv sync --extra fetch --extra data --extra judge --extra bench --extra train --extra app
uv run --no-sync python -m playwright install msedge   # tests UI (-m ui)
```

Si la roue CUDA de torch ne correspond pas au pilote, voir la règle `pytorch` de `config/reseau.toml` (index `download.pytorch.org`).

### Binaires et modèles

Ces téléchargements sont épinglés et vérifiés par SHA-256.

```powershell
uv run --no-sync slmsp fetch llamacpp
uv run --no-sync slmsp fetch modeles granite-4.0-1b      # si non copié ; idem pour chaque slug
uv run --no-sync slmsp fetch modeles minicpm5-1b --f16   # F16 pour BFCL
uv run --no-sync slmsp fetch benchmarks
```

## 3. Vérifier

```powershell
uv run --no-sync python outils/controle_rapide.py
uv run pytest -q --tb=line -p no:warnings          # suite complète, une fois
uv run --no-sync slmsp budget etat                 # doit montrer la campagne baseline-2026-10-17 et ses dépenses
nvidia-smi
```

Si `slmsp budget etat` montre un registre vide, `var` n'a pas été importé : ne lancer **aucun** appel payant avant de corriger.

## 4. Particularités du portable (6 Go de VRAM)

- **lm_eval en HF bf16.** Batch fixe obligatoire : `lm_eval_batch_size` dans `config/modeles/<slug>.toml`. La valeur 4 est posée pour minicpm5-1b. Pour granite-4.0-1b et les nouveaux modèles, partir de 2. En mode `auto`, on a vu un OOM même sur 8 Go.
- **QLoRA (story 11.2).** Charger en 4 bits, avec gradient checkpointing, batch 1 et accumulation. Si un OOM persiste à la séquence cible, revenir sur la tour.
- **Mesures CPU (H-RAM).** Elles restent indicatives : le portable a 32 Go, la cible 16 Go.
- **Verrou GPU.** `var/gpu.lock` est propre à chaque machine. Ne pas copier un verrou actif.

## 5. Reprendre avec Claude Code

L'état détaillé du run est dans `_bmad-output/implementation-artifacts/etat-run-2026-10-16.md`, section « Passation ». Le sprint est dans `_bmad-output/implementation-artifacts/sprint-status.yaml`.

Prompt de reprise, à coller dans une nouvelle session (Opus, effort medium) :

> Reprise du projet slmsp sur le PC portable (32 Go RAM, GPU 6 Go). Lis `docs/reprise-deuxieme-pc.md` (section 3, vérifier l'installation), puis la section « Passation » de `_bmad-output/implementation-artifacts/etat-run-2026-10-16.md` et `sprint-status.yaml`. Vérifie l'installation (contrôle rapide, `slmsp budget etat`, `nvidia-smi`), signale tout écart, puis enchaîne le travail restant dans l'ordre de la passation, en respectant CLAUDE.md (enchaînement dev-story → second-avis → reviewer, D1 : Claude ne génère jamais de données d'entraînement, appels payants par l'orchestrateur seulement, ne jamais lire `.env`). Fais-moi un point avant tout appel payant non couvert par un plafond existant.
