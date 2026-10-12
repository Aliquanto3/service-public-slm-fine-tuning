# Rapport du run autonome — 2026-10-12 (06h26 → 18h30)

> Branche `nuit/2026-10-12` : 76 commits, **non fusionnée dans `main`** et non poussée.
> Suite de tests : **2 940 réussis, 0 échec** (ruff propre).
> Détails : `etat-nuit.md`, `journal-decisions-nuit.md`, `baseline-rapport.md`.

## 1. Points à trancher par Anaël (par priorité)

1. **Go/no-go après la Baseline**
   - Voir `baseline-rapport.md` §5. Les deux modèles échouent sur la fidélité à la source (Q, LC, RE, CT). RD (environ 73) et CO sont acceptables.
   - La règle D4 désigne Granite 4.0 1B pour l'essai QLoRA (moyenne 33,4 contre 32,2 pour Ministral 3B), mais l'écart n'est pas significatif.
2. **Relecture de l'échantillon du Jeu d'évaluation** (47 items) : `eval/revue/echantillon-revue-v1.0-lecture.md`. C'est un préalable à toute comparaison fine, car **le kappa entre les deux juges est quasi nul** (0 à 0,21). Points à regarder en priorité :
   - items proches du calibrage : Q-045, Q-048, CT-005, CT-007, CR-023 ;
   - paires LC × Q portant sur la même fiche ;
   - aucun item sur les marchés publics ;
   - Q-042 ;
   - transcriptions CR toutes sous 6 000 mots (FR-13) ;
   - fragments RD trop larges (« cni » correspond aussi à « CNIL ») ;
   - libellés CT listés dans la consigne.
3. **Écarts aux décisions** (journal)
   - **D-nuit-1, puis D-nuit-2 : horaire.** Le run a été lancé à 06h26, puis prolongé sur ta consigne.
   - **A1-5 : Juge sans `temperature`.** `claude-opus-5-5` refuse ce paramètre, à l'écart de SPEC §7 ; un cache de verdicts compense.
   - **A1-17 : `download.pytorch.org`.** Hôte ajouté hors D1.5, nécessaire pour torch CUDA.
   - **A2-10 et S1.4 : `legal.mistral.ai`.** Ajouté en GET seul, pour la vérification D1.2.
   - **S5.4 : règle `anthropic-lots`.** Elle autorise les GET vers `api.anthropic.com` sans restriction de chemin.
   - **S5.5 : deux journaux Mistral.** La génération et le second juge ont chacun le leur, alors qu'AD-3 prévoit un fichier unique. C'est voulu : aucun texte d'évaluation ne doit atteindre `data`/`train`.
   - **A1-10 : prompts système du Harnais réutilisés en entrée d'entraînement.** Ce sont des instructions sans exemple, rédigées par l'agent.
4. **Décisions techniques à valider**
   - **A2-9 et S1.5 : tarifs Mistral prudents.** 2 $ / 6 $ par million de tokens, probablement surestimés.
   - **S1.5 : remise à zéro du budget.** Elle passe par un nouveau `campagne_id`.
   - **S1.1 : conflit des extras.** `fetch` et `train` sont en conflit (huggingface-hub).
   - **S2.3 : H-VEC.** Le p95 vaut environ 320 ms pour un seuil de 300, mesuré sous charge : à remesurer au repos.
   - **S3.2 : texte de réponse vide.** Valeur retenue : « No results found. ».
   - **S5.5 : modèle réel inconnu.** L'API Mistral renvoie l'alias `mistral-large-latest`, pas la version effectivement servie.
   - **S4.3 : prompt RD en mode connecté.** Variante `RD-connecte` à décider ; FR-38 n'est pas vérifié sur les arguments d'outil.
   - **S4.2 : citations de Granite 1B.** Il ne produit aucun renvoi `[n]`.
5. **Coût Claude Code.** Le mode économe est actif : une seule couche de revue (`_bmad/custom/bmad-build-auto.toml`, supprimer ce fichier pour revenir à 4) et une story à la fois. Le coût par story passe d'environ 300 k à 120–260 k tokens.

## 2. Fait et non fait, par phase

| Phase | État | Détail |
|---|---|---|
| A. Planification | ✅ | Architecture (spine), 53 stories et 13 epics, contrôle de préparation (« prêt avec réserves »), sprint-status |
| B, piste 2 : Jeu d'évaluation | ✅ | 225 items sur sources réelles, double vérification (9,4 % de rejets, corrigés), 40 cassettes MCP (36 réelles), échantillon de revue de 20 %, **gel `v1.0-provisoire`** (commit `12eef73`, manifeste `70c42fb5…`) |
| B, piste 1 : banc | ✅ en grande partie | Socle, passerelle réseau, budget, MCP direct et Bac à sable, Index local (143 k chunks), Harnais (Q, RD, CR longs, rédaction), génération et notation (Juge Claude, second juge Mistral, kappa). **Restent** : Benchmarks standardisés (6.1 à 6.4), `slmsp ask` (4.5), mesure H-EMB (2.4) |
| C. Baseline | ⚠️ réduite | Jeu maison sur Granite 1B et Ministral 3B, sonde d'outils sur 4 modèles. **Restent** : benchmarks, FR-26, SmolLM3, Qwen 4B, Ministral 8B |
| D. Données d'entraînement | ❌ | Générateur Mistral prouvé (9.2, gabarits relus : aucun exemple). 9.1 interrompue (worktree conservé). 9.3 à 9.8 non faits. **Aucune donnée générée.** |
| E. Essai QLoRA | ❌ | 10.1 (environnement Windows) codée et mesurée, mais **non fusionnée** : la revue relève une dizaine de points à corriger. 10.2 à 11.2 non faits |
| F. Clôture | ⚠️ | Ce rapport. Les **revues de code par epic (`bmad-code-review`) n'ont pas été lancées**, par économie : seuls les epics 1, 3, 5 et 7 sont terminés |

**Stories** : 30 terminées, 3 en revue (8.3, 8.4, 10.1), 20 au backlog.

**Modèles** : 5 candidats téléchargés et vérifiés sous `models/` (39 Go). Granite est dense, Ministral 3B est en bf16 avec la vision exclue.

## 3. Scores de Baseline (provisoires, non relus)

| Tâche | Granite 4.0 1B | Ministral 3 3B |
|---|---|---|
| Q | 0,0 | 5,0 |
| RD | 73,3 | 72,8 |
| CR | 32,9 | 37,7 |
| LC | 0,0 (plafonné) | 0,0 |
| CO | 79,3 | 40,7 |
| RE | 31,9 | 34,6 |
| CT | 30,0 | 20,0 |
| NR | 20,0 | 46,7 |
| **Moyenne** | **33,4** | **32,2** |
| Durée par item (CUDA) | 3,3 s | 6,4 s |

**Essai QLoRA** : non réalisé. Il n'y a donc pas de rapport `essai-qlora-rapport.md`.

## 4. Dépense par API (RegistreBudget, campagne `nuit-2026-10-12`)

| Poste | Dépensé | Plafond |
|---|---|---|
| Anthropic (Juge) | **6,06 €** | 10 € |
| Mistral, juge | 0,47 € | 5 € |
| Mistral, génération | 0 € | 25 € |

La consommation de Claude Code (sous-agents) est à part, et elle a atteint la limite de dépense vers 14h50.

## 5. Blocages et incidents

- **07h47 à 08h15** : réseau limité à ta demande.
- **Vers 14h50** : la limite de dépense Claude a coupé 3 stories (5.3, 9.1, 10.1) et a mis le run en pause. Reprise à 15h35, en mode économe sur un périmètre réduit.
- **17h44** : la Baseline de Ministral 3B a été arrêtée par Claude Code (mémoire système critique). Elle a repris sans perte après la fermeture d'applications.
- **Sous-agents** : plusieurs ont rendu la main avant la fin (sous-agents asynchrones). Ils ont été relancés et la consigne correspondante a été ajoutée.
- **Test instable sous charge** : `tests/inference/test_serveur.py::test_demarrage_rate_sante`.
- **SmolLM3** : aucun format d'appel d'outil n'est lu par llama.cpp b11429 (0/5 à la sonde).

## 6. Travail en attente (worktrees conservés, non fusionnés)

- **9.1, registre des licences** : `.claude/worktrees/agent-a114d5fa3f921abf8`. Travail non commité.
- **10.1, environnement d'entraînement** : `.claude/worktrees/agent-ac1ba7aa2d001c9e8`, commit 793bd33.
  - Une mesure H-WIN-TRAIN réelle existe.
  - Constats de revue à corriger : provenance des runs, `uv run` sans `--frozen` sous `gpu.lock`, seuil de débordement VRAM, paramètres propres à Granite appliqués à tous les modèles, chemins absolus.

## Étape suivante recommandée

- **Avant tout** : relire l'échantillon du jeu (`eval/revue/echantillon-revue-v1.0-lecture.md`), puis trancher les points du §1. Cette relecture conditionne la fiabilité de toutes les mesures suivantes.
- **Skill** : `bmad-code-review`
- **Prompt** : « Revue de code des epics 1, 3, 5 et 7 sur la branche `nuit/2026-10-12` (commits de squash `feat(...)` depuis `3431c35`), en priorité `src/slmsp/judge/`, `src/slmsp/evaluation/` et `src/slmsp/mistral/` (verrous D1.1). Consigner les constats critiques avant toute fusion dans `main`. »
- **Modèle** : Opus 5.5
- **Effort** : medium
- **Nouveau chat** : oui, faire `/clear`.
- **Ensuite** : reprendre la phase D (9.1, puis 9.3 à 9.8) et la phase E (10.1 corrigée, puis 10.2 à 11.2), avec `bmad-build-auto` en mode économe, en plan mode, sur Opus 5.5 en effort medium (high pour 10.4).
