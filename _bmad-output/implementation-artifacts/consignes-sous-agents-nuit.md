# Consignes communes aux sous-agents de story — run du 2026-10-12

Ce fichier est lu par chaque sous-agent de story avant de commencer. Il fait autorité au même titre que `decisions.md`.

## Contexte d'exécution
- **Run autonome, sans humain.** Ne pose aucune question et n'attends aucune validation. Une décision non couverte se tranche selon « la solution la plus simple et la plus réversible ». Elle est consignée dans le fichier d'histoire de la story (section `## Auto Run Result`) et dans ton compte rendu final. L'orchestrateur la reporte ensuite au journal.
- **Worktree isolé.** Tu travailles dans un worktree git dédié, sur une branche dédiée. Plusieurs stories tournent en parallèle dans d'autres worktrees.
  - Ne touche qu'aux fichiers de la zone de ta story (« Fichiers et modules », et la table « Dépendances et zones de fichiers » de `epics.md`).
  - Ne fais jamais de `git checkout` ni de `git switch` vers une autre branche, de `git stash`, de `git reset --hard`, de `git rebase` ni de `git push`, et ne réécris pas l'historique.
- **Dépôt principal** (lecture des fichiers non versionnés) : `C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning`.
  - Les secrets sont dans `<dépôt principal>\.env`. Lis-les par chemin absolu. Ne recopie jamais leur valeur dans un fichier versionné ni dans un log.
  - Les données brutes sont dans `<dépôt principal>\data\raw\` (lecture seule).
  - **État machine** : registre de budget, cache des verdicts, `gpu.lock` et `pids/`. Il va dans `SLMSP_VAR_DIR`, selon l'architecture (par défaut `%LOCALAPPDATA%\slmsp\var\`). Ce dossier est partagé par tous les worktrees.
  - **Téléchargements lourds** : modèles, corpus, binaires llama.cpp.
    - Ils restent dans le dépôt principal, sous `models/`, `data/` et `var/`, qui sont ignorés par git. Accède-y par chemin absolu, ou par une variable d'environnement de configuration que tu documentes.
    - Ne télécharge jamais deux fois le même fichier. Un worktree de story de code ne télécharge rien de lourd : ses tests utilisent des fixtures.

## Règles bloquantes (decisions.md D1, rappel)
1. **Claude ne génère aucune Donnée d'entraînement** : ni exemple, ni réponse cible, ni few-shot, ni amorce insérée dans un prompt du générateur. C'est Mistral `mistral-large-latest` qui génère. Les gabarits du générateur ne contiennent aucun exemple de réponse. Dans les tests, les fixtures de « données d'entraînement » sont des chaînes factices manifestement artificielles (`"<réponse-factice-1>"`), jamais du contenu réaliste rédigé par Claude.
2. **Pas de génération** de Données d'entraînement avant le commit de gel du Jeu d'évaluation `v1.0-provisoire`.
3. **Aucune publication** : pas de push et rien sur Hugging Face. Réseau limité à la liste D1.5, plus `download.pytorch.org` (D-nuit-A1-17).
4. **Budgets durs** : Mistral 30 € et Anthropic 10 €, sur toute la nuit et pour tous les agents. Les tests unitaires ne font **aucun** appel d'API payant : mocks et cassettes uniquement.
5. **Ne jamais supprimer** de données, de checkpoints ni d'artefacts d'évaluation.
6. **Ne pas modifier** `../wavelocalai`, ni les documents de décision : PRD, UX, decisions.md, SPEC, grille, architecture.

## Outillage
- **Python 3.12 via `uv` uniquement** (`uv sync`, `uv run pytest`, `uv run ruff check`). La commande `python` du PATH n'est pas fiable. Windows natif, sans WSL.
- **Commandes longues** (plus de 2 minutes) : en arrière-plan, puis attendre la notification de fin. Jamais de boucle de `sleep`.
- **Blocage** : après 2 échecs sur le même problème, consigne-le, contourne-le (stub, mock ou fixture) et termine la story avec un statut honnête.

## Definition of Done
- Les tests de la story passent, ainsi que `uv run pytest` sur l'ensemble et `uv run ruff check`, ou la liste exacte des échecs préexistants hors de ta zone.
- Commits dans ton worktree au format `feat(<epic>): <titre court> (story X.Y)`. Chaque message se termine par la ligne :
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
- **Compte rendu final** (10 lignes au plus) :
  - le statut : done, partiel ou bloqué ;
  - le nom de ta branche et le chemin de ton worktree ;
  - le résultat des tests ;
  - les fichiers touchés hors de ta zone, s'il y en a ;
  - les décisions prises seul ;
  - les blocages ;
  - la dépense d'API, s'il y en a eu.

## Sous-agents asynchrones (constat de 08h00)
Dans cet environnement, **tout lancement de sous-agent est asynchrone**, même quand le workflow BMAD exige un appel bloquant. Lance les sous-agents demandés par une étape, puis attends la notification de fin de chacun avant de passer à la suite. **Ne rends jamais la main** (compte rendu final) avant le HALT final du workflow, avec `## Auto Run Result` écrit et le commit fait. Rendre la main pendant qu'un sous-agent tourne interrompt la story.

## Accès au dépôt principal depuis un worktree (story 1.2, fusionnée)
- `SLMSP_ENV_FILE=C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\.env` donne accès aux secrets.
- `SLMSP_MODELS_DIR=C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\models` donne accès aux modèles, avec `HF_HOME=<models>/.cache-hf`. Les modèles candidats sont déjà préchargés : voir `models/PRECHARGEMENT.md`.
- Le verrou GPU est `gpu.lock`, dans `SLMSP_VAR_DIR`. Toute commande CUDA le prend.
- `SLMSP_VENDOR_DIR=C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\vendor` contient les binaires llama.cpp b11429, en variantes cpu et cuda. Le modèle d'embedding BGE-M3 est sous `models/bge-m3/gguf/`. Le corpus MediaTech est sous `data/raw/mediatech/`.
- Les tests réels de llama-server sont marqués `integration` (story 2.2). Granite 1B en CPU débite environ 42 tokens/s.
