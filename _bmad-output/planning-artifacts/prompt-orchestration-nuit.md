# Prompt d'orchestration — run autonome de nuit (2026-10-12)

Coller ce bloc tel quel dans une **nouvelle** session Claude Code, ouverte dans le dossier du projet, en auto mode.

---

Tu es l'orchestrateur d'un run de développement autonome de nuit, avec la méthode BMAD (installée localement dans `_bmad/`, skills dans `.claude/skills/`). Anaël dort et personne ne répondra avant 07h00. Ne pose donc aucune question et ne t'arrête pas pour demander une validation.

## Contexte obligatoire, à lire en premier
1. `_bmad-output/planning-artifacts/decisions.md` : **fait autorité**. Il contient les règles bloquantes D1, les budgets, la stack et les conditions d'arrêt. Relis D1 avant chaque phase.
2. PRD final : `_bmad-output/planning-artifacts/prds/prd-service-public-slm-fine-tuning-2026-10-11/prd.md`, son `addendum.md` et les fichiers `research-*.md` du même dossier.
3. UX finale : `_bmad-output/planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/` (DESIGN.md, EXPERIENCE.md, mockups/). Elle ne sert cette nuit qu'à cadrer l'architecture, car l'application, c'est-à-dire le jalon J4, n'est pas au programme de la nuit.
4. Jeu d'évaluation : `eval/SPEC-jeu-evaluation.md`, `eval/grille-juge-v1.md` et `eval/calibrage/`, validés par Anaël. Le calibrage est la référence de format.
5. Note de cadrage d'origine : `Note de cadrage — SLM secteur public français.md`.

## Règles d'exécution
- **Rappel des règles bloquantes (D1).**
  - Claude ne génère **aucune** Donnée d'entraînement, pas même un exemple few-shot ou une amorce destinés au générateur. C'est Mistral qui génère.
  - Aucune génération de données avant le commit de gel du jeu d'évaluation.
  - Pas de push et pas de publication.
  - Budgets durs : Mistral 30 €, Anthropic 10 €.
  - Ne jamais supprimer de données ni de checkpoints.
  - Ne pas modifier `../wavelocalai`.
- **Python** : toujours via `uv` (Python 3.12). La commande `python` du PATH n'est pas fiable. Windows natif uniquement, WSL n'est pas installé.
- **Git**
  - Si la branche `main` n'a pas de commit, faire d'abord un commit de cadrage avec l'état actuel, sans `.env` ni `data/raw/` : `chore: cadrage BMAD (PRD, UX, décisions, spécification et calibrage de l'évaluation)`.
  - Créer ensuite la branche `nuit/2026-10-12` et y rester.
  - Faire un commit local après chaque story terminée. Chaque message de commit se termine par la ligne d'attribution habituelle.
- **Délégation.** Délègue tout travail substantiel à des sous-agents pour garder ton contexte léger.
  - **Une story = un sous-agent** (`general-purpose`), lancé en **bloquant**, qui invoque le skill `bmad-build-auto` avec l'identifiant de la story et le chemin des epics.
  - Les stories indépendantes peuvent tourner en parallèle, au plus 3 à la fois. Les stories qui touchent les mêmes fichiers passent séquentiellement.
- **Commandes longues** (téléchargements, entraînement, benchmarks) : en arrière-plan (`run_in_background`), en attendant la notification de fin. Jamais de boucle de `sleep`.
- **Blocage.** Après 2 échecs sur un même problème, consigne-le, contourne-le (stub, fixture ou modèle écarté) et passe à la suite. Aucune étape ne doit bloquer toute la nuit.
- **État persistant** : tiens à jour `_bmad-output/implementation-artifacts/etat-nuit.md` (phase en cours, fait, en cours, bloqué, dépense API) après chaque phase et chaque story. Si ton contexte est résumé, relis-le avant de continuer.
- **Décisions prises seul** : les consigner dans `_bmad-output/implementation-artifacts/journal-decisions-nuit.md`.
- **Heure limite : 07h00.** À 06h30, arrête de lancer du nouveau travail et passe à la phase F.

## Phases (dans l'ordre, sauf parallélisme indiqué)

### Phase A : planification (cible : environ 1 h)
1. **Architecture.** Invoque `bmad-architecture` en mode création et sans interaction, à partir du PRD, de l'addendum, de l'UX et de `decisions.md`.
   - L'architecture respecte la stack de D3.
   - Elle tranche par la mesure, ou par une hypothèse explicite, ce que D3 laisse ouvert : stockage vectoriel, embedding, structure des modules.
   - Elle couvre en priorité les jalons J1 à J3 du PRD (§9.3) : Harnais en ligne de commande, Index local, client MCP et Bac à sable MCP, banc d'évaluation, Benchmarks standardisés, pipeline de données, entraînement et Comparatif.
   - Le jalon J4 (application pywebview) n'est esquissé qu'au niveau des interfaces.
2. **Epics et stories.** Invoque `bmad-create-epics-and-stories` sur le même périmètre. Les stories de J1 à J3 doivent être détaillées et prêtes au développement. J4 et J5 restent au niveau des epics.
3. **Sprint.** Invoque `bmad-sprint-planning`, avec le contrôle de préparation (implementation readiness) et le fichier de statut du sprint.

### Phase B : socle J1 et jeu d'évaluation complet (en parallèle)
- **Piste 1 (dev).** Stories J1 dans l'ordre du sprint : squelette du projet et outillage (pyproject, ruff, pytest), Index local, client MCP et Bac à sable MCP, Harnais en ligne de commande, banc d'évaluation (FR-25, FR-39, FR-40), Benchmarks standardisés (FR-27, FR-28) et mesures techniques (FR-26).
- **Piste 2 (jeu d'évaluation).** Un sous-agent construit les 225 items selon `eval/SPEC-jeu-evaluation.md` §2 à §5, en partant du format et des scripts de `eval/calibrage/` :
  - sources réelles et cassettes ;
  - double vérification par un second sous-agent ;
  - échantillon de revue de 20 % exporté.

  Le jeu est ensuite **figé** en `v1.0-provisoire`, avec un manifeste SHA-256 et un commit dédié : `eval: gel du jeu d'évaluation v1.0-provisoire`.
- **Fin de la phase B** : la piste 2 est figée, et le banc sait évaluer un modèle de bout en bout.

### Phase C : Baseline (J1)
1. Télécharger les Modèles de base candidats (D4), en GGUF Q4_K_M pour l'inférence et en poids HF pour l'entraînement. Respecter les points de D7 :
   - Granite : vérifier qu'il est bien dense ;
   - Ministral 3 3B : il n'existe pas de GGUF officiel et les poids sont en FP8 ;
   - Ministral 3 : exclure l'encodeur vision.
2. Exécuter la Baseline de chaque candidat sur le Jeu d'évaluation maison (Juge Claude, 20 % rejugés par Mistral), le socle de Benchmarks standardisés et les mesures de RAM, débit et latence.
3. Produire `_bmad-output/implementation-artifacts/baseline-rapport.md` : Scores de Tâche, mesures, conformité à NFR-1/2/3 et faiblesses principales par Tâche.
4. **Ne prends pas la décision go/no-go.** Prépare seulement les éléments qui permettront à Anaël de trancher.

### Phase D : données d'entraînement (J2, après le commit de gel)
1. Stories du pipeline de génération, de validation et de filtrage (FR-29 à FR-31), avec le Registre des licences et le contrôle anti-fuite.
2. Revérifier les conditions de Mistral (§3.3) et consigner la date.
3. Générer environ 600 exemples, dans la limite de 30 € de budget Mistral (moins ce qu'a coûté le second juge). Prendre les proportions de l'addendum §G et cibler en priorité les faiblesses relevées par la Baseline.
4. Valider et filtrer les exemples, puis versionner le jeu d'entraînement.

### Phase E : premier essai de fine-tuning (J3, partiel)
1. Stories des Runs d'entraînement configurables et des mesures de coût (FR-32, FR-33), de l'export GGUF (FR-35), puis un squelette du Comparatif (FR-36).
2. **Choix du modèle.** Prendre le meilleur modèle de 3B ou moins qui tient dans 5 Go selon la Baseline. À défaut, prendre Granite 4.0 1B dense (règle D4).
3. **Run M1 QLoRA** sur ce modèle, puis export GGUF et réévaluation avec le même banc.
4. **Mini-rapport.** Produire `_bmad-output/implementation-artifacts/essai-qlora-rapport.md` : gain par Tâche par rapport à la Baseline, non-régression, coût (durée, VRAM, énergie) et limites. Préciser que ce rapport n'est pas le go/no-go.
5. **S'il reste du temps avant 05h30** : lancer M3 DoRA sur le même modèle, pour tester la comparaison.

### Phase F : clôture (à partir de 06h30 au plus tard)
1. Lancer `bmad-code-review` sur chaque epic terminé non encore revu. Corriger les constats critiques s'il reste du temps, et consigner les autres.
2. Rédiger `_bmad-output/implementation-artifacts/rapport-de-nuit.md`, en français. Il doit être lisible en 5 minutes au réveil :
   - le fait et le non-fait, par phase ;
   - les scores de Baseline et de l'essai QLoRA, avec les tableaux ;
   - la dépense par API ;
   - les décisions prises seul ;
   - les blocages ;
   - **les points à trancher par Anaël**, en premier : go/no-go, échantillon de revue du jeu d'évaluation, écarts aux décisions.
   - Termine le rapport par une section « Étape suivante recommandée », au format du CLAUDE.md global : skill, prompt, modèle, effort et nouveau chat.
3. Faire un commit final sur `nuit/2026-10-12`. Ne pas fusionner dans `main`.

Commence maintenant par la lecture du contexte obligatoire, puis la phase A.
