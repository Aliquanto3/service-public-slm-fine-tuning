# slmsp — SLM du secteur public

Windows seul, Python 3.12 géré par `uv` (pas de `python` global : `uv run …`).

## Commandes
- Tests ciblés pendant le travail : `uv run pytest -q --tb=short <chemins>`
- Suite complète, une fois avant intégration : `uv run pytest -q --tb=line -p no:warnings`
- Lint et format : `uv run ruff check` et `uv run ruff format --check`
- Contrôle rapide (lint, format, règles d'architecture, ~5 s) : `uv run --no-sync python outils/controle_rapide.py`
  (également via `.claude/cost-kit/controle_rapide.py`)

## Enchaînement par story (appels bloquants, une passe de revue)
1. `dev-story` implémente et commite dans un worktree, sans fusionner.
2. `agent-cost-kit:second-avis` (Haiku, lecture seule) relit le diff.
3. `reviewer` relit avec la liste du second avis, corrige et consigne.
4. La session principale intègre.
Recherches et lecture de logs : agent `lookup`. Consignes des sous-agents : `_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md`.
