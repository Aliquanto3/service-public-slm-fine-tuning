---
type: review-rubric
target: ../ARCHITECTURE-SPINE.md
reviewer: relecteur autonome (lecture seule)
date: 2026-10-12
referentiel: checklist « good spine » (6 points)
sources_lues:
  - ARCHITECTURE-SPINE.md, .memlog.md
  - _bmad-output/planning-artifacts/decisions.md (fait autorité)
  - prd.md (§4, §5, §8, §9.3), addendum.md (§B, §F, §G)
  - eval/SPEC-jeu-evaluation.md (§3 à §8), eval/grille-juge-v1.md, eval/calibrage/cassettes/
  - prompt-orchestration-nuit.md, .gitignore du dépôt
---

# Revue du spine d'architecture `slmsp` (2026-10-12)

## Verdict

**Bon spine, mais pas encore prêt pour une nuit sans humain.** Le paradigme est juste, le garde-fou D1.1 est traité sérieusement et la plupart des AD ont une règle testable. Trois défauts bloquent pourtant un build autonome :

1. la règle de couches d'AD-1 contredit AD-4, AD-5 et AD-9, si bien que le test AST ne pourra pas passer tel qu'écrit ;
2. les contrats d'artefacts entre pipelines ne sont pas fixés (MANIFEST, `generations.jsonl`, `scores.json`, identité du modèle évalué, statut de complétude). Or la piste 2 (gel du jeu) et la piste 1 (banc) tournent en parallèle, et `compare` consomme quatre producteurs ;
3. l'enveloppe opérationnelle est presque muette : reprise après crash, réservations de budget orphelines, lots Batch en cours, concurrence GPU, processus `llama-server` orphelins, téléchargements et `.gitignore`.

Chacun se corrige par un ajout court au spine (correctifs précis ci-dessous). Aucune décision de `decisions.md` n'est contredite.

Échelle de sévérité : **Bloquant** (à corriger avant de lancer les stories), **Majeur** (divergence probable entre stories ou incident de nuit), **Mineur** (cohérence, confort).

---

## Constats bloquants

### B1. AD-1 rend AD-4, AD-5 et AD-9 impossibles (points 2 et 6)

**Constat.**
- AD-1 : « une couche n'importe que les couches de rang inférieur ». Or `net`, `budget`, `inference`, `index`, `mcp` et `mistral` sont tous en couche 1.
- AD-4 impose pourtant que `mcp`, `mistral` et `index` (téléchargements) obtiennent leur client par `slmsp.net.client(profil)`. AD-5 impose que `mistral` passe par `slmsp.budget.Registre`. Enfin, `inference` doit parler HTTP à `llama-server`, alors que `httpx` est banni hors de `net`.
- Ce sont donc des imports L1 → L1, interdits par la règle.
- AD-4 ajoute un import montant : « `slmsp.net` consulte » `slmsp.harness.modes` (L1 → L2).
- Enfin, le spine ne dit pas où vivent les ports (`LlmPort`, `EmbedderPort`, `VectorStore`, `ToolPort`, `NetGate`). S'ils sont dans `harness`, les adaptateurs de L1 qui les implémentent importent L2.

**Risque.** Le premier agent écrit un test AST strict, et les stories suivantes le cassent ou l'affaiblissent chacune à sa façon. Les dépendances réelles finissent par diverger du diagramme.

**Correctif.** Remplacer la couche 1 par deux sous-couches explicites et préciser l'inversion de dépendance :
- `L1a` : `net`, `budget` (n'importent que `core`) ;
- `L1b` : `inference`, `index`, `mcp`, `mistral` (importent `core` et `L1a`).

Ajouter à AD-1 deux règles :
- « Les protocoles de ports vivent dans `slmsp.core.ports` ; les adaptateurs les implémentent sans importer `harness`. »
- « `net` reçoit l'état du Mode par un protocole `FournisseurDeMode` (défini dans `core.ports`), injecté par `harness.modes` ; `net` n'importe jamais `harness`. »

Mettre à jour le diagramme. Il doit aussi montrer L4 → L1 et L4 → core si « rang inférieur » veut dire « toute couche inférieure ». Dans le cas contraire, écrire « couche immédiatement inférieure + core ».

### B2. Contrats d'artefacts entre pipelines non fixés (points 1 et 4)

**Constat.** AD-1 impose que les pipelines de la couche 3 n'échangent que des artefacts, et AD-20 que `compare` soit une fonction pure de `runs/`. Pourtant aucun AD ne fixe le schéma de ces artefacts, ni l'endroit où il est défini. Cinq trous en découlent :
- **`MANIFEST.json` du jeu gelé.** Il est produit par la piste 2 (sous-agent de construction du jeu, en parallèle de la piste 1) et consommé par `eval run` (AD-11) et `data generate`. Le format n'est pas fixé et aucune commande de gel n'est nommée (« seule la commande de gel crée une nouvelle version » : laquelle ?). La piste 2 écrira probablement son propre script.
- **`generations.jsonl`** (phase 1 → phase 2 d'AD-13). La clé du cache de verdicts d'AD-12 utilise le « SHA-256 de la sortie », mais rien ne dit de quel texte il s'agit (texte final assistant ? avec ou sans trace ?).
- **`scores.json`, résultats de benchmarks, mesures et coûts de Run**, que lit `compare`.
- **Identité du modèle évalué.** Rien ne relie un `runs/eval/<id>` à un Modèle de base (slug), à un `runs/train/<id>` ou à un GGUF précis (hash, quantification). `compare` ne peut pas construire « gain par méthode vs Baseline » ni « avant/après quantification » (FR-35, FR-36).
- **Statut de complétude.** `run.json` n'a pas de champ d'état. Un run interrompu en pleine nuit sera lu par `compare` comme un run valide.

**Correctif.** Ajouter un AD « Schémas d'artefacts » (ou étendre AD-21) :
- Chaque artefact échangé entre pipelines a un modèle pydantic dans `slmsp.core.schemas`, avec un champ `schema_version`. Producteurs et consommateurs n'utilisent que ce modèle.
- `run.json` porte au minimum :
  - `type` ;
  - `statut` (`en_cours | termine | echoue | interrompu`) et `termine_le` ;
  - `modele` : `{slug, origine: base|<run_train_id>, format: hf|gguf, quantification, sha256}` ;
  - `jeu_eval` : `{version, sha256_manifeste}`.
- `compare` et tout consommateur ignorent les runs dont `statut != termine`.
- `MANIFEST.json` suit un schéma unique : `{version, cree_le, fichiers: {chemin_posix_relatif: sha256}}`. Il est produit uniquement par `slmsp eval freeze`, que la piste 2 doit utiliser.
- `generations.jsonl` contient une ligne par item : `{item_id, modele, messages (AD-7), evenements, sortie, sha256_sortie}`, où `sortie` est la concaténation des `Jeton` du dernier tour assistant.

### B3. Reprise après crash : non décidée, et contradictoire (points 4 et 6)

**Constat.**
- **Contradiction.** AD-18 : « Reprise depuis le dernier checkpoint ». AD-21 : « chaque exécution écrit dans un nouveau dossier… une reprise écrit à côté ». Une reprise d'entraînement lit-elle les checkpoints du dossier précédent ou crée-t-elle un nouveau `run_id` ? Les deux à la fois, sans règle de chaînage ?
- **Évaluation.** AD-13 dit seulement « chaque phase peut être relancée seule ». Rien sur une phase interrompue (225 items × plusieurs modèles, de l'ordre d'une heure par modèle) : faut-il repartir de zéro ou compléter ?
- **Réservations de budget orphelines (AD-5).** Si le processus meurt entre la réservation et la régularisation, la réservation reste. Avec 10 € côté Anthropic (environ 3 évaluations), quelques réservations « pire cas » orphelines bloquent le Juge pour la nuit. À l'inverse, une implémentation qui les ignore au redémarrage peut dépasser le plafond.
- **Lots Batch (AD-12).** Un lot peut rester en cours plusieurs heures. Si l'identifiant du lot n'est pas persisté avant l'attente, un crash fait repayer le lot entier : le cache de verdicts ne protège qu'après réception. La réservation doit aussi survivre au processus qui a soumis le lot.
- **Génération de données (AD-17).** Rien n'impose de réutiliser les réponses déjà journalisées dans `var/appels-mistral.sqlite` après un crash. Une relance repaie la génération.

**Correctif.** Ajouter un AD « Reprise » :
- `--reprendre <run_id>` complète le même dossier en ajout seul : les items et exemples déjà présents sont sautés, et `statut` repasse à `en_cours`. Cela vaut pour l'entraînement (checkpoints du même dossier). Dans AD-21, remplacer « une reprise écrit à côté » par « une reprise complète le même run en ajout seul, sans réécrire de ligne existante ».
- Une réservation porte `pid`, `cree_le` et `lot_id` éventuel. Au démarrage, `Registre` régularise les réservations sans lot dont le `pid` est mort, au coût pire cas : elles restent comptées comme dépensées, ce qui est prudent. Les réservations liées à un lot sont régularisées quand le lot est relu.
- Le `lot_id` Batch est écrit dans `var/` avant toute attente. Une relance commence par relire les lots en cours.
- `data generate` est idempotent : la clé (amorce, gabarit, version) est cherchée dans le journal Mistral avant tout nouvel appel.

---

## Constats majeurs

### M1. AD-4 ne tient pas sa promesse sur les bibliothèques tierces (point 2)

**Constat.** *Prevents* annonce « un hôte hors Liste blanche contacté par une bibliothèque tierce ». Mais la règle (ruff `TID251` sur `httpx`/`requests`) ne s'applique qu'au code du projet. Or `transformers` (`from_pretrained`), `datasets`, `lm_eval`, `bfcl_eval`, `unsloth` (statistiques d'usage), `codecarbon` (mode en ligne par défaut), `wandb` via `report_to` et la télémétrie `huggingface_hub` ouvrent leurs propres connexions. Ce n'est pas un détail : D1.4 et D1.5 sont bloquants (« aucun envoi vers un service hors de la liste »).

Deux autres trous dans AD-4 :
- **Sonde bloquée en hors ligne.** « En Mode hors ligne (détecté ou forcé), la requête est refusée avant toute connexion » s'applique aussi à la sonde `GET /health`. Une implémentation littérale ne repasse jamais en Mode connecté.
- **Journal des Requêtes sortantes sans propriétaire en J1.** AD-23 en fait la propriété exclusive de `app.stockage` (J4, couche 4), alors qu'AD-4 exige que `net` l'écrive dès J1, et `net` ne peut pas importer `app`.

**Correctif.** Ajouter à AD-4 :
- « Tout point d'entrée `slmsp` de l'outillage fixe, avant tout import tiers :
  - `HF_HUB_DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1`, `UNSLOTH_DISABLE_STATISTICS=1` (nom exact à vérifier) ;
  - `report_to="none"` ;
  - CodeCarbon en `OfflineEmissionsTracker` seulement.

  Un test vérifie ces réglages. Le trafic tiers résiduel est limité aux hôtes D1.5 et journalisé quand c'est possible (par exemple `huggingface_hub.set_client_factory`). »
- « La sonde `/health` est permise en hors ligne *détecté*, interdite en hors ligne *forcé*. »
- « Le journal des Requêtes sortantes est un port `JournalRequetes` (`core.ports`). `net` l'implémente en SQLite à un chemin pris en config (J1 : `var/requetes-sortantes.sqlite`). `app.stockage` réutilise ce port en J4. » Corriger AD-23 en conséquence.

### M2. Mode et réseau pendant l'évaluation : non décidés (point 1)

**Constat.** Le Mode a un propriétaire unique, `GestionnaireDeMode`, qui sonde `mcp.data.gouv.fr/health` « avant chaque appel d'outil ». Dans `eval run`, le Harnais complet tourne avec `BacASable`. Or les items RD portent un champ `mode` (connecté / hors ligne / repli, SPEC §3). Le spine ne dit ni comment le banc impose le Mode de chaque item, ni que le banc s'exécute sans réseau. Une story « Harnais » et une story « banc » vont diverger, et le score dépendra de la disponibilité réelle du serveur, ce qui contredit FR-40 et NFR-8.

**Correctif.** Dans AD-13 ou AD-14 : « Le Mode est une entrée de `repondre(…, options.mode)`, ou `GestionnaireDeMode` est un port avec un adaptateur `ModeFixe`. Le banc fixe le Mode à partir du champ `mode` de l'item et utilise un `NetGate` sans aucun hôte autorisé. Un test vérifie qu'une évaluation complète n'émet aucune requête. »

### M3. Verrou de provenance d'AD-3 : sous-spécifié (point 2)

**Constat.** Le garde-fou le plus important de la nuit repose sur une règle ambiguë. Deux implémentations conformes au texte n'offrent pas la même protection :
- **`appel_id` est au singulier**, alors qu'une trace de tool calling multi-tours demande plusieurs appels Mistral.
- **« SHA-256 du contenu de réponse » n'est relié à rien.** Rien ne dit qu'il faut comparer ce hash aux messages `assistant` de l'exemple final. Une implémentation qui vérifie seulement que l'`appel_id` existe laisse passer un texte réécrit après coup.
- **Les tours `user` et les amorces ne sont pas vérifiés.** Les agents de la nuit sont des instances de Claude : toute amorce rédigée à la main dans un fichier du dépôt viole D1.1, et rien ne l'empêche structurellement. La règle « amorces publiques rattachées au Registre » n'est pas contrôlée au build.
- **Pas de distinction juge / générateur.** Les appels du second juge Mistral passent par le même `slmsp.mistral` et le même journal. Un `appel_id` de jugement pourrait servir de provenance.

**Correctif.** Réécrire le verrou 2 :
- « Chaque exemple porte `appel_ids: list`. Au build, chaque message `assistant` (contenu + `tool_calls` en JSON canonique) doit avoir un hash égal à une réponse journalisée de l'un de ses `appel_ids`, avec `usage = "generateur"`.
- Chaque message `user` provient soit d'une réponse journalisée, soit d'une amorce dont l'artefact `seed` donne `{jeu, revision, ligne}`. Le build relit cette ligne dans `data/raw/` et compare son hash.
- Aucun fichier d'amorces rédigé dans le dépôt n'est accepté. »

Ajouter un champ `usage` (`generateur | juge`) au journal Mistral.

### M4. Construction des messages d'entrée : pas de source unique (point 1)

**Constat.** AD-7 unifie le format des messages et le rendu en tokens, mais pas la *construction* du contexte :
- comment les passages retrouvés sont injectés (message système, message `user`, ou pseudo-outil de recherche ?) ;
- comment l'entrée de chaque Tâche est encadrée ;
- quels schémas d'outils (simplifiés, AD-8) sont passés dans `tools`.

Les traces d'entraînement Q et RD (AD-17) et le Harnais (AD-14) seront écrits par des stories différentes : c'est le décalage entre entraînement et inférence le plus probable du projet. AD-8 ne lie pas `slmsp.data`.

**Correctif.**
- Dans AD-7 : « Les messages d'entrée sont construits par une seule fonction pure, `slmsp.harness.prompts.construire_messages(tache, entree, passages, outils)`. Le pipeline de données l'appelle (L3 → L2 autorisé) et ne compose jamais de prompt lui-même. »
- Ajouter `slmsp.data` aux *Binds* d'AD-8 : le générateur reçoit les schémas figés de `config/outils-mcp.toml`, et les `tool_calls` des traces sont validés contre eux.

### M5. Concurrence entre processus et ressources partagées (point 4)

**Constat.** Seul le budget est protégé (SQLite partagé). L'orchestration lance pourtant jusqu'à 3 stories en parallèle et les commandes longues en arrière-plan. Plusieurs situations restent sans règle :
- **VRAM.** Une évaluation CUDA (deux `llama-server`), lm-eval sur poids HF et un Run QLoRA peuvent se superposer sur 8 Go, d'où des erreurs de mémoire GPU difficiles à diagnostiquer.
- **Mesures FR-26 faussées.** Elles se font sur CPU pendant qu'une autre charge tourne.
- **`llama-server` orphelins.** Sous Windows, ils survivent au crash du parent et retiennent RAM et VRAM.
- **Collision de `run_id`.** Deux runs lancés la même seconde avec le même slug obtiennent le même identifiant.
- **Accès SQLite concurrents.** Le cache de verdicts et le journal Mistral sont partagés ; ni mode WAL ni délai d'attente (`busy_timeout`) ne sont fixés.

**Correctif.** Ajouter un AD « Ressources partagées » :
- **Verrou GPU.** Un verrou de fichier exclusif `var/gpu.lock` est pris par toute commande qui utilise CUDA ; une seconde commande attend ou échoue avec un message clair.
- **Mesures FR-26.** `slmsp measure` exige l'absence d'autre processus `slmsp` actif (vérifié par les fichiers PID) et enregistre la charge CPU de fond.
- **Processus orphelins.** `slmsp.inference` lance `llama-server` dans un Job Object Windows `KILL_ON_JOB_CLOSE`, écrit `var/pids/` et nettoie les orphelins au démarrage.
- **`run_id`.** Il reçoit un suffixe aléatoire de 4 caractères hexadécimaux.
- **SQLite.** Toutes les bases sont ouvertes en WAL avec `busy_timeout` de 30 s.

### M6. Téléchargements, poids et environnement d'entraînement (point 4)

**Constat.** Aucune commande ne télécharge quoi que ce soit, alors que la CLI fixe la liste des sous-commandes. Sont concernés : les Modèles de base (HF et GGUF), les binaires llama.cpp (« par script » : lequel ?), les jeux de benchmarks et les amorces. Chaque story écrira son propre téléchargeur. Plus précisément :
- **Disposition des poids.** Celle de `models/` n'est pas fixée : `models/gguf/...` apparaît dans un seul diagramme. Le cache HF par défaut (profil utilisateur) n'est pas décidé.
- **Révisions non épinglées.** Les révisions HF des modèles et des jeux ne le sont pas, ce qui contredit NFR-8. Seul le snapshot MediaTech est daté.
- **Conversion bf16 de Ministral.** Elle est exigée par AD-18, mais aucune commande n'en est propriétaire et son emplacement n'est pas défini.
- **Script de conversion GGUF.** `convert_hf_to_gguf.py` ne figure pas dans les archives de binaires Windows et dépend du `gguf-py` *du même tag*. Le spine liste `gguf` 0.19.0 de PyPI, ce qui risque une incompatibilité de version avec AD-19. La variante CUDA a aussi besoin de l'archive `cudart` séparée.
- **torch CUDA.** « torch CUDA, extra `train` » ne dit pas d'où vient la roue. Sous Windows, PyPI ne fournit que des roues CPU de torch (à vérifier pour la version 2.14.1). De plus, l'extra `bench` (lm-eval, backend `hf`) tire aussi torch : sans source épinglée globalement, `uv` peut résoudre une version CPU.

**Correctif.**
- Ajouter la sous-commande `slmsp fetch {modeles,llamacpp,benchmarks,amorces}`, seule autorisée à télécharger :
  - poids sous `models/<slug>/{hf,hf-bf16,gguf}/`, avec `HF_HOME=models/.cache-hf` ;
  - chaque `config/modeles/<slug>.toml` épingle `revision` (hash de commit HF) et le fichier GGUF attendu, avec son SHA-256 ;
  - `vendor/llama.cpp/<tag>/` contient `bin-cpu/`, `bin-cuda/` (avec cudart) et `src/` (script de conversion + `gguf-py`).
- Installer `gguf` depuis `vendor/llama.cpp/<tag>/src/gguf-py` (dépendance par chemin), pas depuis PyPI.
- Épingler torch sur l'index PyTorch CUDA (`[tool.uv.index]` avec `explicit = true` et `[tool.uv.sources]`) pour tous les extras. Un test marqué `gpu` vérifie `torch.cuda.is_available()`.

### M7. `.gitignore` en contradiction avec AD-21, et suppression de checkpoints (points 4 et 6)

**Constat.**
- **`runs/` ignoré en bloc.** Le `.gitignore` existant ignore tout `runs/`, alors qu'AD-21 versionne `run.json`, `scores.json` et les rapports. Les artefacts légers ne seront jamais commités, et le Comparatif ne sera pas régénérable par un tiers.
- **Gros fichiers non ignorés.** `index/` (≈ 300 Mo de `.npy`), `var/` (SQLite), `vendor/` (`.exe` et `.dll`) ne sont pas ignorés. Le premier `git add -A` d'un agent commite des centaines de Mo, et l'historique ne doit jamais être réécrit (D1.7).
- **Suppression de checkpoints.** Le `save_total_limit` de TRL supprime des checkpoints, ce qui est interdit par D1.7 (« ne jamais supprimer de checkpoints »). Rien dans AD-18 ne l'interdit.
- **Espace disque.** Aucune règle n'en tient compte, alors que « ne jamais supprimer » fait croître le disque sans limite : plusieurs fusions 16 bits d'environ 6 Go, et des poids bf16 pour 5 modèles. Environ 475 Go sont libres aujourd'hui sur C:, donc pas de risque cette nuit, mais rien ne prévient la saturation ensuite.

**Correctif.**
- Dans AD-21, donner la liste exacte que le squelette écrit dans `.gitignore` : `index/`, `var/`, `vendor/`, `models/`, `data/raw/`, `runs/**/checkpoints/`, `runs/**/*.gguf`, `runs/**/adaptateur/`. Retirer `runs/` et `checkpoints/` en bloc.
- Ajouter : « `save_total_limit` n'est jamais défini. Toute commande qui écrit plus de 1 Go vérifie l'espace libre (seuil en config) avant de démarrer. »

### M8. Capacités silencieuses exigées dès J1 (point 1)

**Constat.**
- **Tâches non cartographiées.** La carte Capacité → Architecture omet FR-2 (sélection de la Tâche), FR-14, FR-15, FR-16 et FR-17. Le Jeu d'évaluation maison contient pourtant des items CR, LC, CO, RE, CT et NR dès la Baseline. Une story « Harnais minimal » peut ne traiter que Q et RD, et la Baseline ne notera alors pas la moitié des Tâches.
- **Délai des lots Batch.** Le Juge est en Batch par défaut (AD-12), mais un lot peut prendre jusqu'à 24 h, alors que la nuit s'arrête à 07h00. Il n'y a ni délai maximal ni repli en appels directs, dont le coût est double : à arbitrer avec le budget.

**Correctif.**
- Ajouter à la carte : « FR-2, FR-14 à FR-17 (Tâches du Harnais) → `harness`, `config/prompts/taches/` ; AD-7, AD-14 », et préciser dans AD-14 que `repondre` accepte les 8 codes de Tâche dès J1.
- Dans AD-12 : « `mode_appel = batch|direct` et `delai_max_lot` dans `config/juges.toml`. Au-delà du délai, les items restants passent en direct dans la limite du budget. »

---

## Constats mineurs

| # | Point | Constat | Correctif |
| --- | --- | --- | --- |
| m1 | 6 | AD-11 : « le code ne réécrit jamais `eval/` ». Or `slmsp mcp record` (AD-10) écrit dans `eval/cassettes/`, et l'export de relecture va dans `eval/revue/` (SPEC §5). | « Seuls `eval freeze` et `mcp record` écrivent sous `eval/`, et uniquement de nouveaux fichiers ; rien n'est écrit sous une version gelée. » |
| m2 | 1 | Cassettes : la SPEC §4 exige la « version du schéma de l'outil », absente du format de calibrage adopté tel quel. La portée de l'appariement (cassettes de l'item seulement, ou magasin entier ?) n'est pas définie, ni la disposition de `data/cassettes/`. | Ajouter `empreinte_tools_list` à la cassette (champ optionnel pour le calibrage). L'appariement se limite aux cassettes de l'item en évaluation ; `data/cassettes/<exemple_id>/`. |
| m3 | 6 | Le *frontmatter* `binds` omet FR-1, FR-2, FR-4, FR-12, FR-14 à FR-17 et NFR-6, cités ailleurs ou nécessaires. | Aligner `binds` sur les *Binds* des AD et sur la carte. |
| m4 | 4 | Fichiers de config non nommés : seuils anti-fuite (AD-17), délai MCP et sonde (AD-8, AD-4), liste du profil `outillage` (AD-4). Deux stories peuvent créer deux fichiers pour la même valeur. | Nommer `config/donnees.toml`, `config/reseau.toml` (profils, délais, sonde) ; `liste-blanche.toml` = profil `assistant`. |
| m5 | 2 | SPEC §7 : « pour les comparaisons, l'ordre de présentation est aléatoire » n'est pas repris dans AD-12. | Une ligne dans AD-12 (graine fixe). |
| m6 | 2 | AD-19 : avec QLoRA, la fusion doit se faire sur la base bf16 d'origine, pas sur la base NF4 déquantifiée, sinon les modèles exportés ne sont pas comparables. | Préciser dans AD-19. |
| m7 | 4 | Le second juge Mistral partage le plafond de 30 € avec la génération, sans sous-plafond : une évaluation peut consommer le budget des données. | Sous-poste `mistral.juge` dans `budgets.toml` (ex. 5 €). |
| m8 | 2 | Liste blanche à correspondance exacte d'hôte : les redirections (`www.service-public.fr` → `.gouv.fr`) ne sont pas encadrées. | « Chaque saut de redirection est revérifié contre la Liste blanche. » (utile dès FR-12) |
| m9 | 2 | AD-5 « tokens d'entrée comptés » : pour Anthropic, compter exactement demande un appel `count_tokens` ; pour Mistral, un tokenizer. | Autoriser une estimation majorée documentée (ex. caractères / 3), plus simple et sûre. |
| m10 | 3 | *Deferred* : « Repli local Qwen… même verrou de provenance qu'AD-3 ». Mais le verrou 2 exige `mistral-large-latest` : la phrase est contradictoire. | « … exigerait d'étendre le verrou 2 par une décision d'Anaël. » |
| m11 | 6 | Le diagramme des couches dessine L3 → L1, mais ni L4 → L1 ni L4 → core. Ambiguïté avec « rang inférieur » (voir B1). | Voir B1. |

## Détail d'implémentation à alléger (point 5)

Ces éléments n'empêchent aucune divergence entre unités ; ils alourdissent le spine et peuvent vieillir vite :
- **Tableau Stack.** Retirer `usearch` (« non installé en v1 », déjà dans H-VEC), `codecarbon` (optionnel, déjà dans *Deferred*) et la version d'`uv`. Garder les versions qui conditionnent un contrat : llama.cpp, mcp, torch, transformers/TRL/PEFT, anthropic, mistralai.
- **AD-18.** « 10 pas de chauffe », « `power.draw` à 200 ms intégré en Wh », « `torch.cuda.max_memory_*` + nvidia-smi » : le callback de coût vit dans une seule unité. Garder « métriques de coût calculées par un seul callback, protocole dans `config/runs/` » et renvoyer le détail à la story.
- **AD-5.** `BEGIN IMMEDIATE` peut rester, car il fixe la sémantique inter-processus ; acceptable, mais à la limite.
- **AD-9.** Le nom de colonne `embeddings_bge-m3` relève de la story d'index. `--pooling cls` doit rester, car il conditionne H-EMB.
- **Environnements.** La version exacte du pilote (610.62) peut rester dans D7 : `run.json` l'enregistre de toute façon.

## Grille de la checklist

| # | Critère | Évaluation | Constats |
| --- | --- | --- | --- |
| 1 | Fixe les vrais points de divergence | Partiel. Points bien couverts : Harnais, format des messages, index, cassettes, Juges, budget. Il manque les contrats d'artefacts, la construction des prompts, le Mode en évaluation et la couverture des Tâches. | B2, M2, M4, M8, m2 |
| 2 | Chaque Rule empêche réellement la divergence | Majoritairement oui. Exceptions : AD-1 (non satisfiable), AD-4 (bibliothèques tierces, sonde), AD-3 verrou 2 (contournable). | B1, M1, M3, m5, m6, m8, m9 |
| 3 | Rien dans *Deferred* ne permet de diverger | Oui, sauf une formulation contradictoire. | m10 |
| 4 | Toute dimension décidée, différée ou ouverte | Non pour l'enveloppe opérationnelle (voir tableau suivant). | B3, M5, M6, M7, m4, m7 |
| 5 | Reste terse | Globalement oui ; quelques détails d'implémentation à alléger. | section précédente |
| 6 | Cohérence interne | Quatre contradictions : AD-1/AD-4/AD-5, AD-18/AD-21, AD-23/AD-4 (journal), AD-11/AD-10 ; plus un écart avec le `.gitignore` existant. | B1, B3, M1, M7, m1, m3 |

## Dimensions de l'enveloppe opérationnelle

| Dimension | État dans le spine | Commentaire |
| --- | --- | --- |
| Environnements | Décidé | Tableau clair (poste de dev / PC cible / profils réseau). |
| Déploiement | Différé (J4) | Correct pour la nuit. |
| Opérations (lancement, arrêt, nettoyage) | **Silencieux** | Pas de nettoyage des `llama-server` orphelins (M5). |
| Reprise après crash ou interruption | **Contradictoire / silencieux** | B3. |
| Concurrence entre processus | Partiel (budget seulement) | GPU, mesures, `run_id`, SQLite (M5). |
| Observabilité | Partiel | `log.jsonl` par run, évènement `Progression` ; il manque `statut` dans `run.json` (B2) et la persistance de l'état des lots (B3). |
| Téléchargements de modèles et poids | **Silencieux** | M6. |
| Gestion du disque | **Silencieux** | M7. |
| Secrets | Décidé | AD-22. |
| Réseau et télémétrie tierce | Partiel | M1. |
| Budgets | Décidé, avec trous | Réservations orphelines (B3), sous-plafond du juge Mistral (m7). |
| Git et versionnement des artefacts | Décidé, mais contredit par le dépôt | M7. |

## Points forts à conserver

- **Paradigme.** L'hexagone pour le Harnais et les pipelines à artefacts manifestés pour le reste répondent bien à NFR-8 et FR-36.
- **D1.1 en verrous testables.** Le principe est excellent ; seul le verrou 2 est à préciser (M3).
- **AD-7.** Le rendu exclusif par le chat template, des deux côtés, élimine la première source classique de décalage entre entraînement et inférence.
- **AD-13 et le cache de verdicts.** Deux phases séparées, et un verdict jamais repayé.
- **Section « Hypothèses à mesurer ».** Chaque hypothèse a un seuil, une story de mesure et un repli : exemplaire pour un run autonome.
- **AD-15.** Il sépare honnêtement le binaire CUDA (qualité) du binaire CPU (mesures FR-26).
- **Écarts signalés.** Ceux avec la SPEC et D7 sont signalés sans redécider, dans le respect de D1.8.

## Correctifs à appliquer avant le lancement des stories (ordre recommandé)

1. **B1.** Sous-couches L1a/L1b, `core.ports`, `FournisseurDeMode`, diagramme.
2. **B2.** AD « Schémas d'artefacts » (`core.schemas`, `run.json.statut` et `modele`, `MANIFEST.json`, `eval freeze`, `generations.jsonl`).
3. **B3.** AD « Reprise » (`--reprendre`, réservations orphelines, `lot_id` persisté, idempotence de `data generate`) ; corriger AD-21.
4. **M2 et M4.** Mode fixé par l'item et réseau nul en évaluation ; `construire_messages` unique ; `data` lié par AD-8.
5. **M3.** Verrou de provenance par message et `usage` dans le journal Mistral.
6. **M1, M5, M6, M7.** Télémétrie tierce, sonde, port `JournalRequetes` ; verrou GPU et Job Object ; `slmsp fetch`, révisions épinglées, index torch CUDA, `gguf-py` du tag ; `.gitignore` et `save_total_limit`.
7. **M8**, puis les mineurs.
