# Consignes des sous-agents — run méthodologie v2 (2026-10-20, PC portable)

Complète `consignes-sous-agents-nuit.md` (règles D1, Definition of Done) ; ce fichier prime en cas d'écart (chemins du portable).

## Environnement d'un worktree
- Dépôt principal : `C:\Users\Anael\dev\service-public-slm-fine-tuning` (venv, `models/`, `vendor/`, `data/`, `runs/`). Worktrees : `C:\Users\Anael\dev\slmsp-wt\<story>`, sans venv.
- Avant toute commande (Bash) :
  `export SLMSP_RACINE='C:\Users\Anael\dev\slmsp-wt\<story>' PYTHONPATH='C:\Users\Anael\dev\slmsp-wt\<story>\src' SLMSP_MODELS_DIR='C:\Users\Anael\dev\service-public-slm-fine-tuning\models' SLMSP_VENDOR_DIR='C:\Users\Anael\dev\service-public-slm-fine-tuning\vendor' PATH="/c/Users/Anael/dev/service-public-slm-fine-tuning/.venv/Scripts:$PATH"`
  puis `python -m pytest -q --tb=short <chemins>`, `ruff check`, `ruff format --check`, `python outils/controle_rapide.py` (venv principal, jamais `uv sync` dans le worktree). La CLI : `slmsp.exe`.
- N'écris **que** dans ton worktree. Ne modifie jamais le dépôt principal. Ne lis jamais `.env`.

## Règles
- D1 : Claude ne rédige aucune donnée d'entraînement, aucun exemple de réponse, aucun few-shot dans un gabarit de générateur. Fixtures : chaînes manifestement factices (`"<réponse-factice-1>"`).
- Aucun appel d'API payant (Anthropic, Mistral, OpenRouter), aucun entraînement ni génération réels : mocks et fixtures. Les runs réels sont lancés par l'orchestrateur.
- Pas de push, pas de suppression de données ni de runs, pas de `git checkout/switch/stash/reset --hard/rebase`.
- Tests ciblés pendant le travail ; pas de suite complète locale (l'orchestrateur la lance). `ruff check`, `ruff format --check` et le contrôle rapide avant le commit.
- Commit : `feat(<zone>): <titre> (story <ID>)` ou `fix(...)`, terminé par `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Compte rendu final en 8 lignes au plus : statut, branche, tests, fichiers hors zone, décisions prises seul, blocages.
- Spec de la story : `sprint-change-proposal-2026-10-20.md` (planning-artifacts) et, pour O1, O3, O4, O6, C5, `spec-<id>-*.md` (implementation-artifacts).
