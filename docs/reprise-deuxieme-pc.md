# Reprise du projet sur un deuxième PC

PC portable : 32 Go de RAM DDR4, GPU NVIDIA de 6 Go de VRAM.
- Le code et les tests tournent sur CPU.
- Les benchmarks et l'essai QLoRA des modèles de moins de 2B doivent tenir sur 6 Go avec un batch fixe.
- Si le fine-tuning bloque sur 6 Go, reprendre sur la tour.

Tout vient de GitHub, sans copie de disque à disque :
- le code et les runs : dépôt privé `Aliquanto3/service-public-slm-fine-tuning` ;
- l'état machine : release privée `etat-2026-10-17`, environ 10 Mo. Elle contient les journaux Mistral et le registre des budgets, indispensables pour la provenance et les plafonds ;
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

Lancer les commandes dans l'ordre, en arrêtant au premier échec. Après `uv sync`, toujours utiliser `uv run --no-sync`.

```powershell
git config core.longpaths true
powershell -NoProfile -ExecutionPolicy Bypass -File outils/migration/restaurer-etat.ps1
uv sync --extra fetch --extra data --extra judge --extra bench --extra train --extra app
uv run --no-sync python -m playwright install msedge
uv run --no-sync slmsp fetch llamacpp
uv run --no-sync slmsp fetch sources
uv run --no-sync slmsp index build
uv run --no-sync slmsp fetch benchmarks
uv run --no-sync slmsp fetch modeles bge-m3 bge-m3-f16 granite-4.0-1b minicpm5-1b
uv run --no-sync slmsp fetch modeles granite-4.0-1b minicpm5-1b --f16
```

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
uv run --no-sync pytest -q --tb=line -p no:warnings   # suite complète, une fois (4 992 passés sur la tour)
```

Si `slmsp budget etat` montre un registre vide, la restauration a échoué : ne lancer **aucun** appel payant.

## 4. Prompt de reprise (nouvelle session Claude Code, Opus, effort medium)

> Reprise du projet slmsp sur ce PC portable (32 Go RAM, GPU 6 Go). Le dépôt est cloné et `.env` est rempli (ne le lis jamais). Lis `docs/reprise-deuxieme-pc.md` et exécute toi-même l'installation (section 2) puis les vérifications (section 3), en t'arrêtant au premier échec pour me le signaler. Ensuite lis la section « Passation » de `_bmad-output/implementation-artifacts/etat-run-2026-10-16.md` et `sprint-status.yaml`, rappelle-moi les décisions en attente, et enchaîne le travail restant dans l'ordre de la passation. Pour l'étape 2 (candidats < 2B), reprends la branche `feat/modeles-moins-2b` (commit WIP non relu). Respecte CLAUDE.md : enchaînement dev-story → second-avis → reviewer, D1 (Claude ne génère jamais de données d'entraînement), appels payants par l'orchestrateur seulement, toujours `uv run --no-sync`, batch lm_eval fixe sur 6 Go de VRAM (jamais `auto`). Fais-moi un point avant tout appel payant non couvert par un plafond existant.

## 5. Particularités du portable (6 Go de VRAM)

- **lm_eval en HF bf16.** Un batch fixe est obligatoire : `lm_eval_batch_size` dans `config/modeles/<slug>.toml`. Partir de 2 ; minicpm5-1b est à 4. En `auto`, on a vu un OOM même sur 8 Go.
- **QLoRA (story 11.2).** Charger en 4 bits, avec le gradient checkpointing, batch 1 et accumulation. Si l'OOM persiste à la séquence cible, revenir sur la tour.
- **Mesures CPU (H-RAM).** Elles restent indicatives : le portable a 32 Go de RAM, la cible 16 Go.

## Annexe : transfert par disque

`outils/migration/exporter-etat.ps1` et `importer-etat.ps1` copient le même état, plus les modèles et l'index, par un disque externe : environ 25 Go avec `-AvecModeles`. C'est utile seulement si le réseau est lent.
