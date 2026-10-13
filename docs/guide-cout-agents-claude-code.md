# Réduire le coût du développement par agents avec Claude Code : apprentissages consolidés

> **Statut** : consolidation v1 du 2026-10-13, tirée de deux projets. Elle sera confrontée aux mesures d'un troisième projet, puis servira de base à un guide public (dépôt GitHub dédié et post LinkedIn).
> **Sources** : ce dépôt (projet « slm », fine-tuning d'un petit modèle pour le secteur public) et `usine-migration-jira-demo` (projet « jira », usine de migration de tickets). Le retour d'expérience détaillé du second est dans son `docs/retour-experience-couts-agents.md`.
> **Niveau de preuve** : chaque constat porte un niveau.
> - **Mesuré** : chiffré sur au moins une tâche réelle.
> - **Convergent** : mesuré dans les deux projets.
> - **Observé** : constaté, sans mesure.
> - **Documenté** : issu de la doc officielle.
>
> Les bancs ne comptent qu'un essai par case. Ce sont des indications fortes, pas des statistiques.

## 1. Contexte des deux projets

| | jira | slm |
|---|---|---|
| Période | 10 au 13 octobre 2026 | 12 et 13 octobre 2026 |
| Volume | environ 60 stories | 53 stories planifiées, dont 33 livrées au 2026-10-13 |
| Pile | Python, uv, pytest (2 800 tests), mypy, import-linter | Python, uv, pytest (3 400 tests), ruff, test d'architecture |
| Méthode | BMAD v6 ; orchestrateur Claude Code (Opus 5.5) qui lance des sous-agents dans des worktrees git | idem, plus un run autonome de nuit, puis de jour |
| Système | Windows 11 natif | Windows 11 natif, GPU 8 Go |

Prix API par Mtok (octobre 2026) :

| Modèle | Entrée | Sortie | Lecture du cache |
|---|---|---|---|
| Haiku 5.5 | 0,10 $ | 0,50 $ | non publiée (supposée à 0,01 $) |
| Sonnet 5.5 | 2 $ | 10 $ | 0,20 $ |
| Opus 5.5 | 4 $ | 20 $ | 0,20 $ |
| Fable 5.1 | 10 $ | 50 $ | 0,25 $ |

Une écriture dans le cache coûte 1,25 fois le prix d'entrée avec un TTL de 5 minutes, et 2 fois avec un TTL d'une heure.

## 2. Comment on a mesuré

1. **Coût réel plutôt que nombre de tokens.**
   - Le total affiché à la fin d'un sous-agent ne correspond pas à la facture. Il mélange des tokens dont le prix varie de 1 à 100 : une lecture du cache coûte 100 fois moins qu'un token de sortie.
   - Dans slm, une story affichée à 192 k tokens représentait en réalité 8,6 M tokens lus depuis le cache, soit environ 4,10 $.
   - `outils/cout_sous_agents.py` additionne l'usage de chaque réponse de la transcription (`~/.claude/projects/<projet>/<session>/subagents/agent-<id>.jsonl`) par catégorie, puis applique les prix.
2. **Banc à consigne identique.**
   - La même tâche réelle du projet est confiée à Haiku, à Sonnet et à Opus. Le prompt est identique ; seul le paramètre `model` de l'outil Agent change.
   - Pour le code, chaque modèle travaille dans un worktree isolé.
   - Les tâches de revue, de spec, d'architecture et de recherche se font en lecture seule, avec un fichier de sortie hors du dépôt.
3. **Qualité.**
   - Code : tests, puis lecture du diff par l'orchestrateur.
   - Revue : comparaison avec les défauts déjà connus.
   - Spec, architecture et recherche web : **juge Opus en aveugle**. Les fichiers sont renommés A, B et C dans un ordre tiré au hasard. Le juge note sur 10, selon une grille de 5 critères, et doit vérifier lui-même les affirmations dans le dépôt ou sur le web. Un juge coûte entre 0,30 $ et 0,90 $.
4. **Limites.**
   - Un seul essai par case.
   - Le juge Opus peut favoriser le style d'Opus. L'aveugle limite ce biais sans le supprimer.
   - Le prix de lecture du cache de Haiku est supposé.

## 3. Résultats des bancs

### 3.1 Projet jira (coût en tokens de sous-agent, qualité vérifiée par l'orchestrateur et les tests)

| Tâche | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|
| Implémentation (petit correctif d'UI avec test) | 52,7 k ; correct, mais tests lancés en arrière-plan malgré la consigne | 43,2 k ; correct, un cas multiligne oublié | 46,4 k ; le plus complet |
| Revue (commit de 660 lignes) | 88,7 k ; 4 medium et 6 low ; trouvailles vérifiées en exécutant du code | 55,4 k ; 5 medium et 5 low | 82,7 k ; **seul à classer « high » le défaut principal** |
| Recherche dans le dépôt | 36,4 k ; exact | 18,6 k ; exact | 18,4 k ; exact, le plus complet |
| Spec (conteneur et note de portage) | 112 k ; juste | 92 k ; la plus concrète | 112 k ; la plus fidèle aux contraintes |

### 3.2 Projet slm (coût réel en équivalent API ; notes sur 10 données par le juge en aveugle)

| Tâche | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 | Écart Sonnet / Opus |
|---|---|---|---|---|
| Revue d'un commit (environ 3 300 lignes de code et de tests, lecture seule) | 0,03 $ ; 14 constats, les plus précis, preuves tirées des runs | 0,50 $ ; 15 constats | 0,67 $ ; 15 constats, 2 « high » | −25 % |
| Implémentation multi-fichiers (réglages en config et indicateur de troncature) | 0,06 $ ; correct mais minimal, sans contrôle à la reprise | 1,01 $ ; même conception qu'Opus | 2,25 $ | −55 % |
| Spec d'une story transverse | 6,2 ; 0,07 $ ; couches violées, test de signature cassé | 8,0 ; 1,86 $ ; la plus exacte sur le code existant | **8,4** ; 2,77 $ ; la plus fidèle aux contraintes | −33 % |
| Note d'architecture | 7,0 ; 0,05 $ | 7,5 ; 0,62 $ | **8,5** ; 1,12 $ ; seul à voir un conflit entre deux documents | −45 % |
| Recherche web pour une décision | 6,4 ; 0,02 $ ; vraie cause manquée, erreurs factuelles | 7,8 ; 0,57 $ ; 2 erreurs | **8,4** ; 0,69 $ ; aucune erreur | −17 % |

## 4. Constats consolidés

### 4.1 D'où vient le coût

1. **La relecture du contexte fait l'essentiel du coût d'un sous-agent** (mesuré dans slm). Sur une story typique sur Opus :
   - écriture du cache : 47 % ;
   - lecture du cache : 40 % ;
   - sortie : 13 % ;
   - entrée hors cache : négligeable.

   Pour réduire le coût, il faut d'abord **moins de tours et un contexte plus petit**.
2. **À tâche égale, les trois modèles consomment à peu près le même nombre de tokens** (convergent). Haiku en consomme parfois deux fois plus, parce qu'il tâtonne.
3. **Sonnet ne coûte pas la moitié d'Opus à la tâche** : il coûte de 17 à 55 % de moins (mesuré dans slm). La lecture du cache coûte le même prix chez les deux, et le gain de Sonnet vient surtout de ce qu'il fait moins de tours (33 appels contre 57 en implémentation).
4. **La revue de code multi-agents est le poste le plus cher** (convergent).
   - Dans slm, une revue de lot à 4 relecteurs sur Opus coûte environ 4,20 $ pour l'orchestrateur seul, à cause de 10 M de tokens relus.
   - Dans jira, passer à une seule passe de revue a fait baisser le coût par story d'environ 40 %, sans perte de qualité visible.
5. **Le cache expire pendant les tests** (convergent). Une suite pytest de 4 à 5 minutes dépasse le TTL par défaut des sous-agents (5 minutes). Le contexte est alors relu au prix fort. Le remède est de lancer la suite complète une seule fois et de régler le TTL du cache des sous-agents à 1 h.
6. **Les sous-agents partis en arrière-plan coûtent des reprises** (convergent). Un agent de story qui lance ses propres sous-agents s'arrête parfois avant leur résultat. Dans jira, environ 300 k tokens ont été perdus sur 3 stories. Dans slm, des rapports « intermédiaires » ont imposé des relances.
7. **Le parallélisme accélère la dépense sans la grossir** (observé dans slm). Jusqu'à 11 agents simultanés n'ont pas augmenté le coût par tâche. Limiter le parallélisme protège un plafond de dépense par période, pas le coût total.
8. **Le contexte fixe se paie à chaque tour, dans chaque sous-agent** (documenté et observé) : liste des skills, serveurs MCP, CLAUDE.md, snapshot git. Les skills synchronisés depuis claude.ai et les MCP sans rapport avec le projet sont du poids mort.

### 4.2 Quel modèle pour quel rôle

| Rôle | Modèle | Niveau de preuve | Pourquoi |
|---|---|---|---|
| Orchestration, architecture, PRD, découpage en stories | Opus | mesuré dans slm (architecture) | Opus était 1 point au-dessus de Sonnet en architecture, et seul à voir un conflit entre documents. Les décisions s'y propagent partout. |
| Spec d'une story transverse ou à risque | Opus | convergent | le plus fidèle aux contraintes |
| Spec d'une story courante | Sonnet | convergent | la plus concrète, et exacte sur le code, pour 33 % de moins |
| Implémentation d'une story bien cadrée | Sonnet | convergent | qualité équivalente, de 50 à 55 % moins cher ; reprise avec Opus après deux échecs |
| Implémentation transverse ou à risque | Opus | observé | Sonnet et Haiku oublient des cas limites |
| Revue courante | Sonnet, avec Haiku en second avis en lecture seule | convergent | Haiku fait des constats précis pour presque rien, et la réunion des deux listes vaut mieux que chacune seule |
| Revue d'un commit à risque (argent, sécurité, données) | Opus | convergent, mais nuancé | il juge mieux la gravité que Sonnet ; Haiku a aussi classé juste des « high » dans slm |
| Lookup dans le dépôt, logs, sortie de tests | Haiku | mesuré dans jira | réponse exacte pour presque rien |
| Recherche web qui fonde une décision | Opus | mesuré dans slm | Haiku y fait des erreurs factuelles, et Opus coûte à peine plus que Sonnet |
| Problème où Opus en effort high échoue deux fois | Fable 5.1 | non testé | environ 2,5 fois le prix d'Opus |

**Haiku** est excellent en lecture : revue, lookup, preuves tirées des fichiers. En revanche, il est faible dès qu'il faut concevoir (spec, architecture), synthétiser des sources externes ou respecter des consignes de processus.

### 4.3 Pièges rencontrés

- **Classifieur du mode auto** : il bloque comme « modification de ressource partagée » des actions pourtant autorisées : gel d'un jeu de données, commit dans un autre dépôt, ajout de hooks en cours de session. Prévois la commande `!` à donner à l'utilisateur, ou une règle de permission.
- **Changements de configuration** : les hooks, les agents et les réglages ne se chargent qu'au démarrage d'une session. Il faut redémarrer sans `--continue`, sinon on recharge une longue conversation, puis reprendre depuis un fichier d'état.
- **Worktrees sous Windows**
  - Un chemin trop long fait échouer `git worktree remove`. On supprime alors le dossier avec `Remove-Item -LiteralPath '\\?\C:\...'`, puis on lance `git worktree prune`.
  - Un worktree reste verrouillé par le processus Claude Code qui l'a créé. `/clear` garde le même processus.
  - Le répertoire courant est réinitialisé entre deux commandes : passe toujours des chemins absolus.
  - Il faut lancer `uv sync` dans chaque worktree.
- **Fichiers partagés modifiés par des agents en parallèle** : deux agents ont numéroté leurs reports W1 et W2 dans le même fichier, d'où un conflit à la fusion. Il faut attribuer d'avance une plage de numéros à chaque agent.
- **Dépassement de périmètre** : un agent de recherche web a tenté de lancer un serveur et de télécharger des fichiers. Une consigne « lecture seule » ne suffit pas : retire les outils inutiles avec `tools` ou `disallowedTools`.
- **Cache** : changer de modèle l'invalide. Changer l'effort ne l'invalide pas avec les modèles 5.5. Un changement de CLAUDE.md ne s'applique qu'après `/clear`.
- **Agents intégrés** : `claude-code-guide` tourne sur Haiku par défaut. Il convient pour lire la doc officielle (0,03 $ pour une synthèse sourcée), mais vérifie ses conclusions avant une décision.

## 5. Recommandations, des plus rentables aux moins rentables

1. **Une seule passe de revue par story**, sur Sonnet. Haiku peut s'ajouter en second avis. Garde la revue multi-relecteurs pour une revue d'epic ou de lot.
2. **Router les modèles par rôle** (tableau du § 4.2) : Sonnet pour coder et relire, Opus pour décider, Haiku pour chercher dans le dépôt.
3. **Des agents de story qui ne peuvent pas lancer de sous-agents** (`disallowedTools: Agent, Workflow`). L'orchestrateur enchaîne `dev-story` puis `reviewer`, chacun par un appel qui attend le résultat.
4. **La suite de tests complète une seule fois**, juste avant l'intégration. Pendant le développement, seulement les tests ciblés, en `-q --tb=short`, et un contrôle rapide (lint, format, architecture, environ 10 s) dans un hook `Stop`.
5. **Cache des sous-agents à 1 h** (`subagentPromptCacheTtl`).
6. **Contexte fixe minimal pour chaque projet** : désactiver les MCP sans rapport (`/mcp`), masquer les skills claude.ai (`syncClaudeAiSkills: false`), garder un CLAUDE.md court.
7. **Rapports de sous-agent courts**, de 5 à 8 lignes. Seul le rapport final revient à l'orchestrateur, mais il y revient en entier.
8. **Un plafond de tokens par run, et un fichier d'état** : l'orchestrateur tient le décompte et s'arrête proprement après la story en cours. On reprend dans une session neuve à partir du fichier d'état, plutôt que de recharger la conversation.
9. **Mesurer le coût réel** avec `outils/cout_sous_agents.py`, et `/usage` avant et après un changement de méthode.
10. **Consignes de story à la Spotify** : une seule modification par story, décrite par l'état final voulu ; au plus 3 cycles de correction sur un même échec, puis un rapport `bloque`.

## 6. Installer la configuration sur son propre projet

Les fichiers de référence sont dans ce dépôt :

| Fichier | Rôle |
|---|---|
| `.claude/agents/dev-story.md` | Sonnet, effort medium, sans sous-agents, hook `Stop` de contrôle rapide |
| `.claude/agents/reviewer.md` | Sonnet, effort medium, sans sous-agents ; corrige les constats medium et high |
| `.claude/agents/lookup.md` | Haiku, effort low, lecture seule (`tools: Read, Grep, Glob, Bash`) |
| `.claude/settings.json` | `"subagentPromptCacheTtl": "1h"` et `env.CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH = "2"` |
| `.claude/settings.local.json` (non versionné) | `"syncClaudeAiSkills": false` |
| `outils/controle_rapide.py` | contrôle de quelques secondes, n'affiche que les erreurs, sort en code 2 pour le hook, bloque au plus deux fois par agent |
| `outils/cout_sous_agents.py` | coût réel par catégorie de tokens |
| CLAUDE.md global | grille modèle et effort par étape BMAD |

Étapes :
1. Copier les fichiers, puis adapter les commandes du contrôle rapide au projet (linter, typage, règles d'architecture).
2. Adapter les règles métier bloquantes dans `dev-story` et `reviewer` (secrets, données, budget d'API).
3. Désactiver les MCP inutiles avec `/mcp`, puis redémarrer Claude Code.
4. Vérifier avec `/agents`, `/mcp` et `/hooks`.

## 7. Protocole pour le troisième projet

Pour que les résultats soient comparables, il faut reprendre le même protocole.

1. **Mesure de départ.** Avant tout changement, faire 3 à 5 stories avec la méthode habituelle. Noter pour chacune :
   - le coût réel (`outils/cout_sous_agents.py`) ;
   - le nombre de tours ;
   - la réussite au premier passage ;
   - le nombre de constats de revue.
2. **Après installation de la configuration du § 6** : mêmes mesures sur 5 stories comparables.
3. **Banc par modèle**, sur de vraies tâches du projet : Haiku, Sonnet et Opus, avec un prompt identique, sur 5 tâches.
   - les tâches : implémentation, revue, spec, architecture, recherche web ;
   - **3 essais par case si le budget le permet**, pour sortir de l'essai unique ;
   - juge Opus en aveugle pour les tâches sans test automatique.
4. **Hypothèses encore à tester**
   - **Effort** : low, medium ou high sur Sonnet en implémentation. Le guide Anthropic dit qu'un modèle plus fort en effort bas bat souvent un modèle plus faible en effort haut.
   - **Contexte fixe** : effet mesuré de `syncClaudeAiSkills: false` et de la désactivation des MCP sur le coût d'un sous-agent, à tâche identique.
   - **Cache** : effet mesuré du TTL d'une heure sur une story dont la suite de tests dépasse 5 minutes.
   - **Revue** : apport réel d'un second avis Haiku sur la revue Sonnet, en défauts trouvés en plus pour le coût ajouté.
   - **Spec écrite d'avance** : coût total d'une story dont la spec est écrite par Opus, puis l'implémentation faite par Sonnet, comparé à une story faite entièrement par Sonnet.
   - **Juge** : biais du juge Opus, à mesurer en faisant aussi juger par Sonnet et en comparant les classements.
5. **Tableau de restitution** : une ligne par tâche et par modèle, avec le coût réel, le nombre de tours, la note ou le résultat des tests, et un commentaire. Utiliser les mêmes colonnes qu'au § 3.2 pour comparer directement.

## 8. Avant publication (dépôt GitHub et post LinkedIn)

- **Anonymiser les projets**. Les noms des dépôts, le contenu métier et les identifiants de run ne sont pas nécessaires. Garder la nature des tâches, les volumes et les chiffres.
- **Revérifier les prix et les noms de réglages** contre la doc officielle du jour : `subagentPromptCacheTtl`, `syncClaudeAiSkills`, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `disallowedTools`, et le frontmatter `model` et `effort` des agents.
- **Indiquer clairement le niveau de preuve** : essai unique par case, juge LLM, deux ou trois projets, Windows. Mettre en avant les constats convergents.
- **Fournir le protocole et les scripts**, pour que chacun puisse reproduire sur son propre projet.
- **Structure suggérée du post** :
  1. le problème : un run autonome a atteint la limite de dépense ;
  2. la découverte : 85 % du coût vient de la relecture du contexte ;
  3. le banc à trois modèles et le juge en aveugle ;
  4. le routage retenu ;
  5. les 5 réglages à copier ;
  6. le lien vers le dépôt.

## 9. Sources

- Documentation Claude Code :
  - [coûts](https://code.claude.com/docs/en/costs.md)
  - [sous-agents](https://code.claude.com/docs/en/sub-agents.md)
  - [configuration des modèles](https://code.claude.com/docs/en/model-config.md)
  - [cache de prompt](https://code.claude.com/docs/en/prompt-caching.md)
  - [MCP](https://code.claude.com/docs/en/mcp.md)
  - [skills](https://code.claude.com/docs/en/skills.md)
  - [worktrees](https://code.claude.com/docs/en/worktrees.md)
- Anthropic :
  - [système de recherche multi-agents](https://www.anthropic.com/engineering/multi-agent-research-system)
  - guide « What a task costs on Opus 5.5 » (septembre 2026)
  - guide d'optimisation des coûts de l'API : « coût par tâche réussie, pas par token »
- Spotify, agent de migration « Honk » : [partie 2, ingénierie du contexte](https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2) et [partie 3, boucles de rétroaction](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3).
- Données brutes de slm : `_bmad-output/implementation-artifacts/etat-run-2026-10-13.md` (décompte, bancs, conclusions) et `rapport-de-nuit.md` (run de nuit, mode économe).
