---
title: Revue « réconciliation des entrées » du spine d'architecture
cible: ARCHITECTURE-SPINE.md (2026-10-12, draft)
sources_relues:
  - _bmad-output/planning-artifacts/decisions.md (fait autorité, lu en entier)
  - prds/prd-service-public-slm-fine-tuning-2026-10-11/prd.md
  - prds/prd-service-public-slm-fine-tuning-2026-10-11/addendum.md
  - ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/EXPERIENCE.md (State Patterns, Hors périmètre, Décisions par défaut)
  - eval/SPEC-jeu-evaluation.md §4 à §8 (pour vérifier les renvois du spine)
date: 2026-10-12
mode: lecture seule (seul ce fichier est écrit)
---

# Revue : réconciliation decisions.md / PRD / addendum / UX → spine

## Verdict

Le spine couvre bien l'essentiel des règles bloquantes et de la stack. Il reste un trou critique sur D1.1 : la provenance des **amorces** n'est verrouillée nulle part, alors que l'agent de la nuit est lui-même Claude. Trois manques sérieux s'y ajoutent : D1.4 et D1.5 face aux bibliothèques tierces, l'évaluation « avant quantification » du Jeu maison (FR-25, FR-35), et l'identité des artefacts dont dépendent le Comparatif, le chemin no-go et la règle de choix D4. Les correctifs proposés s'ajoutent aux AD existants. Aucun ne remet en cause le paradigme.

## Ce qui a bien atterri

- **D1.1 (sorties et gabarits)** : verrous d'import, de provenance, d'absence de few-shot et d'absence de verdict Claude (AD-3).
- **D1.3** : gel vérifié par `git ls-files` et `git diff --quiet` (AD-11). Le chemin `eval/jeu/v1.0/MANIFEST.json` est cohérent avec SPEC §6.
- **D1.6** : registre SQLite avec réservation (AD-5). **D1.7** : immuabilité (AD-21). **D1.8** : `eval/` jamais réécrit, écarts signalés en « Questions ouvertes ».
- **D2** : `uv`, pas de `python` du PATH, Windows natif, `.env`. **D3** : stack complète. **D4** : Index v1, slugs et ordre des modèles. **D7** : Mamba, FP8 et encodeur vision vérifiés au chargement (AD-18) ; l'écart sur le GGUF de Ministral 3B est signalé.
- **FR-3, FR-5 à FR-11, FR-13, FR-24 à FR-36, FR-39, FR-40, NFR-1 à NFR-3, NFR-8, NFR-9** : chacune a un AD gouvernant. **UX** : hôte bloqué journalisé, journal sur 30 jours, « Rester hors ligne » persistant (AD-23), repli MCP (évènement `Repli`) ; le découpage en morceaux avec progression correspond à l'évènement `Progression` (AD-14).
- **Chemin go/no-go** : il reste à Anaël (Deferred), conformément à D4.

## Constats

### C1 — Critique — Provenance des amorces non verrouillée (D1.1, PRD §8 « Origine des amorces »)

**Constat.** AD-3 verrouille la provenance du **texte généré** (`appel_id`) et le contenu des **gabarits**. Il ne dit rien de l'origine des **amorces** injectées dans les emplacements. Or :

- PRD §8 restreint les amorces à des sources publiques (AgentPublic, MediaTech), à Anaël ou au générateur retenu. D1.1 cite nommément « les amorces insérées dans les prompts du générateur ».
- L'agent qui code cette nuit est Claude. Toute liste écrite à la main dans le dépôt est une amorce rédigée par Claude : questions d'amorce de secours si AgentPublic est indisponible, thèmes et participants des « réunions fictives du secteur public » (addendum §G), sujets des 10 à 20 % de données génériques, textes administratifs à simplifier. C'est le chemin de violation le plus probable de la nuit, et aucun verrou ne le bloque.
- Le diagramme « Chaîne des pipelines » relie `jeu --> dgen` sans restriction. Le Jeu d'évaluation maison est rédigé par Claude (autorisé par D1.1, mais **uniquement pour l'évaluation**). Rien n'empêche l'étape `seed` d'y puiser.

**Correctif proposé (spine).** Ajouter à AD-3 un verrou 5, « Amorces » :

1. L'étape `seed` n'accepte que trois origines :
   - des lignes extraites d'un artefact téléchargé et inscrit au Registre (SHA-256 du fichier brut dans `data/raw/`) ;
   - un dossier `data/amorces-anael/` doté d'un manifeste, dont le contenu est validé par Anaël ;
   - des listes de scénarios ou de sujets produites par `slmsp.mistral.Generateur`, avec `appel_id` et `usage = generation`.
2. Chaque amorce porte `origine` et `source_sha256`. `build` rejette toute amorce sans l'un des trois.
3. `eval/` n'est lisible, côté `slmsp.data`, que par l'étape `filter` (anti-fuite). Le test AST ou le test de chemins le vérifie, et le diagramme est corrigé en `jeu --> filter`.
4. Le spine dit explicitement : « aucune amorce littérale rédigée par un agent dans le code, la config ou les données ».

### C2 — Haute — D1.4 et D1.5 non tenus face aux bibliothèques tierces et aux sous-processus

**Constat.** AD-4 bannit les clients HTTP **dans `slmsp`**. Son champ « Prevents » promet pourtant de bloquer « un hôte hors Liste blanche contacté par une bibliothèque tierce ». Côté outillage, ce sont justement les tierces qui ouvrent leurs propres connexions :

- `transformers` et TRL (`report_to`, qui peut envoyer vers wandb ou d'autres services si un intégrateur est installé ; `push_to_hub`) ;
- `huggingface_hub` (`upload_*`, `create_repo`, télémétrie) ;
- lm-eval (`--hf_hub_log_args`, wandb) ;
- CodeCarbon, qui géolocalise l'IP via un service externe en mode `EmissionsTracker` en ligne ;
- les sous-processus `git push`.

Le profil `outillage` parle de « services », mais D1.5 dit « Hugging Face **en téléchargement** », « PyPI et GitHub **en lecture** ». Enfin, la liste `outillage` d'AD-4 omet le dernier point de D1.5 (hôtes de la Liste blanche).

**Correctif proposé (spine, AD-4).**

1. Le profil `outillage` est en lecture seule (GET et HEAD) pour HF, PyPI et GitHub. POST n'est permis que vers l'API Mistral, l'API Anthropic et `mcp.data.gouv.fr`. Les hôtes de la Liste blanche sont ajoutés en lecture.
2. Un environnement de processus imposé par `slmsp.core.config` à toute commande d'outillage : `HF_HUB_DISABLE_TELEMETRY=1`, `WANDB_MODE=disabled`, `report_to="none"` et `push_to_hub=False` dans toute config TRL, CodeCarbon uniquement en `OfflineEmissionsTracker` avec un pays fixé.
3. Ruff `TID251` étendu à `huggingface_hub.HfApi.upload_*`, `create_repo` et `push_to_hub`. Aucun appel à `git push` dans le code.
4. Un test vérifie ces réglages sur les configs de `config/runs/` et `config/benchmarks/`.

Remarque de détail, sans incidence sur l'invariant : la correspondance exacte de nom d'hôte du profil `outillage` doit couvrir les redirections CDN de HF et GitHub (à fixer par la story « net »).

### C3 — Haute — Le Jeu maison n'a pas de chemin « avant quantification » (FR-25, FR-35, FR-36)

**Constat.** FR-25 exige une évaluation « avant ou après quantification » ; FR-35 et FR-36 exigent des scores avant et après quantification dans le Comparatif. Or AD-6 n'interroge le modèle que par `llama-server` et un GGUF, et AD-13 passe toujours par ce `LlmPort`. AD-16 donne un chemin « avant » aux QCM seulement (lm-eval sur les poids HF). Pour le Jeu d'évaluation maison, la notion « avant quantification » n'est pas définie. Une story risque d'improviser un second `LlmPort` avec `transformers`, ce qui contredit AD-6 et AD-7.

**Correctif proposé (AD-13 et AD-19).** « Avant quantification » = GGUF F16/BF16 non quantifié, produit par le même `convert_hf_to_gguf.py` (AD-19, étape intermédiaire conservée) et évalué par le même Harnais via `llama-server`, binaire CUDA autorisé. `run.json` porte `quantification ∈ {f16, q4_k_m}`. Pour la Baseline, le GGUF F16 du Modèle de base suit la même règle.

### C4 — Moyenne — Identité des artefacts insuffisante pour le Comparatif, le chemin no-go, SM-1 et la règle D4

**Constat.** AD-21 fixe le contenu générique de `run.json` (config, graine, commit, environnement). En revanche, il ne fixe pas les **clés de jointure** dont `slmsp compare` (AD-20) et les décisions ont besoin :

- **FR-36 et SM-1** : « gain par rapport à la **meilleure** Baseline », non-régression ≤ 3 points, socle ≤ 3 points en moyenne. Il faut savoir quel run est une Baseline, sur quel modèle, avec quelle quantification.
- **Chemin no-go (§9.3)** : la meilleure Baseline devient le Modèle embarqué, et le Comparatif sort avec un résultat négatif. AD-20 doit fonctionner avec zéro Modèle fine-tuné gagnant et traiter la Baseline comme une ligne de premier rang.
- **D4** : le choix du modèle de l'essai M1 est « le meilleur Score de Tâche moyen parmi les ≤ 3B qui tiennent dans 5 Go ». Il faut joindre `runs/eval` et `runs/measure` par slug de modèle, avec un agrégat « Score de Tâche moyen » défini.
- **SPEC §6** : les scores `v1.0-provisoire` sont archivés « non relus », puis tout est relancé en `v1.1`. Il ne faut jamais mélanger deux versions du jeu dans un même tableau.
- **D5** (stub, mock ou fixture après deux échecs) et **AD-5** (arrêt au plafond en cours d'évaluation) produisent des résultats **partiels ou dégradés**. Rien n'oblige à les marquer, et le rapport de nuit ou le Comparatif pourrait les présenter comme complets.

**Correctif proposé (AD-21 et AD-20).** `run.json` porte obligatoirement :

- `modele.slug`, `modele.type ∈ {base, fine-tune}`, `methode` (ou `null`) et `quantification` ;
- `jeu.version` et `jeu.manifeste_sha256` (évaluations) ;
- `statut ∈ {complet, partiel, degrade}` avec un motif (`BudgetEpuise`, stub nommé) ;
- `relecture ∈ {non_relu, relu}`.

AD-20 regroupe les résultats par version du jeu et refuse d'en mélanger deux. Il affiche les statuts partiel et dégradé, inclut la meilleure Baseline comme référence et produit un rapport valide même sans Modèle fine-tuné. Le calcul de SM-1 et l'agrégat D4 vivent dans `slmsp.compare`, à partir de ces seuls champs.

### C5 — Moyenne — Le journal Mistral mélange génération, validation et second juge (D1.1, D1.2, D1.6)

**Constat.** Le verrou 2 d'AD-3 accepte tout `appel_id` présent dans `var/appels-mistral.sqlite`. Or `slmsp.mistral` sert aussi au **second juge** (AD-12), qui reçoit des items du Jeu d'évaluation, et au contrôle de l'étape `validate` (AD-17). Un verdict ou une sortie de contrôle passerait donc le contrôle de provenance.

D1.2 et PRD §8 demandent en outre de revérifier les conditions §3.3 **avant** la campagne. Le spine ne les consigne qu'**après coup**, dans le MANIFEST de `build`. Il n'existe pas non plus de garde sur le modèle résolu par l'alias `mistral-large-latest` (jamais « Labs » ni préversion).

**Correctif proposé (AD-3 et AD-17).**

1. Le journal enregistre `usage ∈ {generation, validation, juge}` et `version_gabarit`. `build` n'accepte que `usage = generation`.
2. `slmsp data generate` refuse de démarrer sans `config/mistral.toml:conditions_verifiees_le` daté du jour de la campagne.
3. Il refuse aussi tout modèle résolu absent d'une liste de versions stables en config.

### C6 — Moyenne — La règle d'arbitrage §9.3 n'est pas appliquée à la dépense (PRD §9.3, D1.6, D4)

**Constat.** Le plafond Mistral de 30 € couvre à la fois la génération et le second juge (D1.6). Sur `BudgetEpuise`, AD-5 « passe à la suite » sans ordre de dépense. Si `generate` parcourt les Tâches dans un ordre arbitraire, le plafond peut tomber avant les Tâches prioritaires. Côté Juge, le spine ordonne les modèles (D4), mais pas les Tâches à l'intérieur d'une évaluation.

**Correctif proposé (AD-5 et AD-17).**

1. Les pipelines payants consomment dans l'ordre §9.3 : Tâches prioritaires (Q, RD, CR, LC), puis NR et données génériques, puis l'ordre de coupe inversé (Correction, puis Résumé et Courrier type).
2. Une enveloppe réservée au second juge est fixée dans `config/budgets.toml`, comme sous-poste du plafond Mistral.
3. La « période » du plafond (« pour la nuit ») est explicite, par exemple un identifiant de campagne, pour que le compteur persistant ne cumule pas les nuits sans le dire.

### C7 — Moyenne — FR-38 et NFR-4 : les Tâches de rédaction ne sont pas isolées structurellement

**Constat.** FR-38 : le texte collé pour une Tâche de rédaction ne déclenche **jamais** de Requête sortante, avec un test « document témoin ». AD-4 journalise et filtre par hôte, mais aucun AD ne dit que `AssistantService` refuse `ToolPort` et `NetGate` pour CR, LC, CO, RE, CT et Traduction. Le test FR-38 n'est rattaché à aucun AD.

**Correctif proposé (AD-14).** La table des Tâches (config) déclare `outils_autorises`. Pour les Tâches de rédaction, la liste est vide : aucun outil n'est passé au modèle et aucun appel `NetGate` n'est possible. Le test « document témoin » (FR-38) appartient à `tests/` et rejoint la liste de `test_architecture.py`.

### C8 — Moyenne — Parité entraînement / inférence incomplète (FR-34, addendum §F « même chat template », FR-13)

**Constat.** AD-7 aligne le format des messages, le chat template et les prompts système des Tâches. Deux éléments manquent pourtant à la parité :

- La **liste `tools`** passée à `apply_chat_template` à l'entraînement n'est pas liée aux schémas figés de `config/outils-mcp.toml` (AD-8). Des traces générées avec les schémas complets du serveur divergeraient de l'inférence.
- Les **prompts de découpage et de fusion** du Compte rendu long (FR-13, AD-14), qui vivent dans le Harnais, ne sont pas couverts. Avec des séquences de 2 à 4k tokens (§6.3), les exemples CR d'entraînement doivent reproduire ces sous-étapes.

**Correctif proposé (AD-7).**

1. `tools` vient toujours de `config/outils-mcp.toml`, dont l'empreinte est inscrite dans le MANIFEST du jeu d'entraînement et dans `run.json`.
2. Les prompts de morceau et de fusion sont des fichiers de `config/prompts/taches/`, partagés par le Harnais et `slmsp.data`.
3. La longueur de séquence maximale est un paramètre de campagne partagé (FR-34).

### C9 — Moyenne — FR-31 : la variante diffusable n'est pas protégée contre les sources non commerciales

**Constat.** AD-17 fait échouer `build` si une source manque au Registre, mais ne fait pas échouer la variante diffusable si une source inscrite est en usage non commercial (Claire French Dialogue, CC BY-NC-SA).

**Correctif proposé (AD-17).** Chaque entrée du Registre porte `usage ∈ {diffusable, recherche, evaluation_seulement}`. `build --variante diffusable` échoue sur toute source qui n'est pas `diffusable`. Les sources `evaluation_seulement` (`MCQ-eval`, `french_simplified`, addendum §G) sont refusées par `seed` dans les deux variantes.

### C10 — Moyenne — Contradiction interne AD-10 / AD-17 sur l'enregistrement des cassettes (FR-40)

**Constat.** AD-10 : « l'enregistrement n'a lieu que par la commande explicite `slmsp mcp record` ». AD-17 : à l'étape `generate`, « les appels d'outils proposés sont exécutés en direct et enregistrés dans `data/cassettes/` ». De plus, valider une trace par rejeu contre des cassettes enregistrées pendant cette même trace est tautologique. La validation FR-30 doit vérifier la cohérence entre la réponse finale et les réponses d'outils (fonction `citations` d'AD-14, valeurs identiques) et la conformité des appels aux schémas figés.

**Correctif proposé.**

1. AD-10 nomme deux points d'enregistrement, `slmsp mcp record` (évaluation) et `slmsp data generate` (magasin `data/cassettes/` seulement), via le même enregistreur.
2. AD-17 précise que `validate` = appels conformes à `config/outils-mcp.toml`, plus URL et valeurs de la réponse présentes dans les réponses d'outils.

### C11 — Moyenne-basse — D1.7 et bibliothèques tierces : rotation des checkpoints

**Constat.** D1.7 interdit de supprimer des checkpoints. AD-21 dit « aucun code n'efface », mais `save_total_limit` de transformers et TRL efface les checkpoints anciens.

**Correctif proposé (AD-18).** `save_total_limit = None` est imposé par la validation pydantic des configs de Run.

### C12 — Basse — Points secondaires

- **ORPO (FR-34).** La provenance des réponses « rejetées » n'est pas nommée. Si elles viennent du Modèle de base local, le verrou 2 d'AD-3 les rejette faute d'`appel_id`. Si elles viennent de Mistral, elles passent par le `Generateur`. Ajouter une origine `generateur = "slm:<slug>"` explicitement autorisée pour le côté rejeté seulement, ou trancher « Mistral uniquement ».
- **Addendum §A.** L'ordre « MCP d'abord, puis RAG en repli » en Mode connecté n'est fixé dans aucun AD. Comme il conditionne aussi la forme des traces d'entraînement, une ligne dans AD-14 suffit.
- **FR-8.** « Les valeurs affichées sont identiques à celles renvoyées par l'outil. » Le spine ne dit pas si le tableau est rendu par le Harnais à partir de `ResultatOutil` ou généré par le modèle, puis vérifié. À fixer dans AD-14, puisque FR-8 est dans J1.
- **FR-26.** La « taille installée » n'est pas mesurée par AD-15. En J1, ajouter la taille sur disque de GGUF + index + binaires comme approximation de NFR-6.
- **NFR-8.** Inscrire la variante llama.cpp (`cpu-x64` ou `cuda-12.4-x64`) dans `run.json`, puisque AD-15 autorise les deux pour des usages différents. Fixer `--parallel 1` pour les évaluations, car le batching de llama-server n'est pas déterministe.
- **D6.** Ajouter à AD-1 : aucune dépendance de chemin vers `../wavelocalai` dans `pyproject.toml`. Le code est recopié et adapté.
- **§9.3, ordre de coupe.** L'ensemble des Tâches actives est piloté par la config (prompts et table des Tâches), pour qu'une coupe (Traduction, Courrier type, Résumé, Correction, FR-12) se fasse sans toucher au code. Les méthodes M3 et M4 sont déjà des données (AD-18).
- **FR-30.** L'export d'un échantillon des Données d'entraînement pour relecture humaine, non bloquant, n'est pas mentionné dans AD-17.
- **D7.** Lecture directe des parquet avec reprises après échec, sans passer par le datasets-server : à rattacher à `slmsp.net` (politique de reprise) ou à `index build`.
- **SPEC §6.** AD-11 pourrait rappeler que le passage en `v1.1` impose de relancer toutes les évaluations. Ce point rejoint C4.

## Hors champ de cette revue

Le détail d'implémentation (syllabation, structure HTML, PyInstaller), le contenu J4 au-delà de la frontière AD-23 et la rédaction du PRD n'ont pas été examinés. Le PRD n'est pas à réécrire.
