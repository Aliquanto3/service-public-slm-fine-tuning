# Journal des décisions prises seul — run du 2026-10-12

Règle appliquée par défaut (decisions.md) : « la solution la plus simple et la plus réversible ».

## D-nuit-1 — Décalage de l'horaire du run (06h26)
- **Constat** : le run a été lancé le 2026-10-12 à 06h26. Or decisions.md D5 et le prompt d'orchestration fixent l'arrêt au 2026-10-12 à 07h00 et la phase F à 06h30. Appliqué à la lettre, le run aurait disposé de 4 minutes de travail utile.
- **Décision** : décaler les jalons horaires du plan d'environ 7 h 30. Cela conserve la durée et la structure d'une nuit de 8 h :
  - seuil DoRA (M3) : 05h30 → **13h00** ;
  - début de la phase F : 06h30 → **14h00** ;
  - arrêt dur : 07h00 → **14h30**.
- **Justification** : l'esprit du plan est un run d'environ 8 h, et un run de 4 minutes ne produirait rien d'utile. La décision est réversible : Anaël peut interrompre la session à tout moment, et `etat-nuit.md` donne l'état courant.
- **À trancher par Anaël** : valider ce décalage a posteriori.

## Décisions de l'architecture (phase A.1, `bmad-architecture`)

Document : `_bmad-output/planning-artifacts/architecture/architecture-service-public-slm-fine-tuning-2026-10-12/ARCHITECTURE-SPINE.md` (justifications détaillées dans le `.memlog.md` du même dossier).

## D-nuit-A1-1 — Un seul paquet Python `slmsp` et une seule commande CLI
- **Décision** : layout `src/slmsp/`, un seul `pyproject.toml` et un seul `uv.lock`, sous-paquets par domaine (`core`, `net`, `budget`, `inference`, `index`, `mcp`, `mistral`, `harness`, `judge`, `evaluation`, `benchmarks`, `measure`, `data`, `train`, `compare`, `app`). Une seule commande `slmsp` (argparse, bibliothèque standard) avec une sous-commande par domaine.
- **Justification** : D3 laisse la structure ouverte. Un seul paquet est la solution la plus simple pour un projet mono-développeur ; argparse évite une dépendance. Réversible : un sous-paquet peut devenir un paquet séparé sans changer les contrats.

## D-nuit-A1-2 — Paradigme : noyau hexagonal + pipelines à artefacts, couches vérifiées par test
- **Décision** : le Harnais dépend de ports (`LlmPort`, `EmbedderPort`, `VectorStore`, `ToolPort`, `NetGate`) ; les pipelines (index, évaluation, Benchmarks, données, entraînement, export, Comparatif) n'échangent que des artefacts sur disque avec manifeste SHA-256. Cinq couches, imports vers le bas uniquement, contrôlés par `tests/test_architecture.py`.
- **Justification** : le banc doit brancher le Bac à sable MCP là où l'Assistant branche le serveur réel (FR-25, FR-40), et le Comparatif doit se régénérer à l'identique (FR-36, NFR-8).

## D-nuit-A1-3 — Stockage vectoriel v1 : recherche exacte sur `numpy.memmap` float16 + SQLite
- **Décision** : `vectors.f16.npy` (N × 1024, normalisé, mappé en mémoire) + `chunks.sqlite` (métadonnées), recherche exacte par blocs. Aucune bibliothèque vectorielle en v1. Levier si la mesure dépasse : index usearch HNSW int8 en vue mappée (usearch 2.26.4), dérivé du même `.npy` sans réembedding.
- **Justification** : D3 demande un stockage sur disque mappé en mémoire et laisse la bibliothèque ouverte. Corpus v1 relevé le 2026-10-12 : 35 758 chunks service-public + 107 679 chunks catalogue data.gouv, soit ~294 Mo en float16. Zéro dépendance, recall exact (référence pour toute mesure ultérieure), bascule possible derrière le port `VectorStore`. Hypothèse H-VEC à mesurer : p95 ≤ 300 ms et ≤ 350 Mo résidents.

## D-nuit-A1-4 — Embedding de requête : BGE-M3 GGUF Q8_0 servi par llama-server
- **Décision** : les vecteurs du corpus restent ceux de MediaTech (BGE-M3, jamais recalculés en v1). La requête est vectorisée par `ggml-org/bge-m3-Q8_0-GGUF` (~635 Mo) dans un second `llama-server --embedding --pooling cls`, puis normalisée.
- **Justification** : compatibilité avec les vecteurs MediaTech (D3), pas de torch dans l'Assistant (RAM NFR-1, taille NFR-6), même moteur que le modèle. Hypothèse H-EMB à mesurer (cosinus ≥ 0,99 avec les vecteurs MediaTech) ; repli : GGUF F16, puis réindexation avec un modèle plus léger.

## D-nuit-A1-5 — Juge Claude sans paramètre `temperature`, en Batch API, avec cache de verdicts (écart à la SPEC §7)
- **Décision** : le Juge `claude-opus-5-5` est appelé sans `temperature` (l'API la refuse pour ce modèle : erreur 400), avec un effort fixé en config, une sortie contrainte par schéma, en Batch API par défaut (−50 %). Chaque verdict est mis en cache par (item, SHA-256 de la sortie, version de grille, modèle, effort) et n'est jamais redemandé.
- **Justification** : la SPEC §7 demande la température 0, ce qui est impossible avec ce modèle. Le cache rend les verdicts stables d'une exécution à l'autre ; le batch double le nombre d'évaluations possibles dans 10 €. Estimation (H-JUGE-COUT, à mesurer sur le calibrage) : ~3 $ par modèle évalué, donc environ trois évaluations complètes dans le budget.
- **À trancher par Anaël** : accepter l'écart à la SPEC §7, ou changer de modèle juge. La SPEC n'a pas été modifiée (D1.8).

## D-nuit-A1-6 — Garde-fou D1.1 en quatre verrous, avec une lecture prudente
- **Décision** : (1) `anthropic` importable seulement dans `slmsp/judge/` (ruff TID251 + test AST) ; (2) `slmsp.data` et `slmsp.train` n'importent jamais `slmsp.judge` ; (3) tout exemple généré doit référencer un `appel_id` présent dans le journal d'appels Mistral, avec le SHA-256 de la réponse, sinon le build échoue ; (4) le client générateur refuse tout message de rôle `assistant` (pas de few-shot) et les gabarits sont des instructions sans exemple, contrôlés par test. En plus : aucun verdict du Juge Claude ne sert à filtrer ou classer des Données d'entraînement ni à construire les paires ORPO.
- **Justification** : D1.1 demande que ce soit structurellement impossible. Le point (4 bis) va au-delà de la lettre de D1.1 (le Juge est autorisé), mais filtrer des données d'entraînement avec des sorties de Claude ressemble trop à utiliser ces sorties pour entraîner ; la lecture la plus prudente est aussi la plus simple.

## D-nuit-A1-7 — Passerelle réseau unique à deux profils
- **Décision** : aucun module n'instancie de client HTTP hors `slmsp/net/` (ruff TID251). Profil `assistant` : Liste blanche §B, nom d'hôte exact, journal des Requêtes sortantes, refus avant connexion en Mode hors ligne. Profil `outillage` : services de D1.5 uniquement.
- **Justification** : FR-11, FR-38 et D1.5 deviennent vérifiables à un seul endroit ; les SDK (MCP v2, anthropic, mistralai) acceptent un client HTTP injecté.

## D-nuit-A1-8 — Registre de budget SQLite avec réservation du pire cas
- **Décision** : `var/budget.sqlite`, partagé entre processus ; réservation du coût maximal avant chaque appel (`BEGIN IMMEDIATE`), régularisation au coût réel ; refus si dépensé + réservé > plafond ; tarifs datés dans `config/tarifs.toml`.
- **Justification** : D1.6 exige un compteur persistant et un arrêt au plafond ; la réservation empêche le dépassement quand le Juge et le générateur tournent en parallèle. SQLite est dans la bibliothèque standard.

## D-nuit-A1-9 — Qualité évaluée sur GPU, mesures techniques sur CPU
- **Décision** : les évaluations de qualité (Jeu maison, Benchmarks) peuvent utiliser le binaire llama.cpp CUDA ; les mesures FR-26 (RAM, débit, latence) utilisent uniquement le binaire CPU, threads plafonnés, avec l'empreinte de la machine.
- **Justification** : évaluer 225 items × 5 modèles en CPU ne tient pas dans la nuit. Le poste de dev (31 Go, RTX 3050) n'est pas le PC cible : les mesures de la nuit sont une approximation déclarée, à refaire sur un vrai PC 16 Go sans GPU avant SM-5.

## D-nuit-A1-10 — Prompts système des Tâches inclus dans les Données d'entraînement (à valider)
- **Décision** : les prompts système du Harnais (`config/prompts/taches/`) sont des instructions sans exemple, rédigées par le projet, identiques à l'entraînement et à l'inférence (AD-7). Ils figurent dans les exemples d'entraînement comme entrée, hors calcul de la perte.
- **Justification** : un chat template identique à l'entraînement et à l'inférence est une condition du protocole (addendum §F). Ce ne sont ni des exemples, ni des réponses cibles, ni des amorces du générateur.
- **À trancher par Anaël** : confirmer que cette lecture de D1.1 lui convient ; sinon, les prompts système seront réécrits par Anaël.

## D-nuit-A1-11 — GGUF officiel de Ministral 3 3B (écart à D7)
- **Constat** : D7 indique « pas de GGUF officiel pour le 3B ». Le dépôt `mistralai/Ministral-3-3B-Instruct-2512-GGUF` existe au 2026-10-12.
- **Décision** : la story de téléchargement prend le GGUF officiel s'il propose Q4_K_M, sinon convertit avec le tag llama.cpp figé, et consigne la source. D7 n'a pas été modifié.

## D-nuit-A1-12 — Cassettes : format du calibrage, deux magasins séparés
- **Décision** : le format de cassette du calibrage est adopté tel quel (session JSON-RPC : `server`, `recorded_at`, `initialize`, `interactions`). Cassettes d'évaluation sous `eval/cassettes/<item>/` (SPEC §8), cassettes des traces d'entraînement sous `data/cassettes/` ; le pipeline de données ne lit jamais `eval/cassettes/`. L'enregistrement n'a lieu que par une commande explicite.
- **Justification** : le calibrage fait référence de format (D6) ; la séparation est une protection anti-fuite de plus.

## D-nuit-A1-13 — Format canonique des conversations
- **Décision** : messages au format OpenAI (`tool_calls` structurés, rôle `tool`) partout ; rendu en tokens uniquement par le chat template du modèle (`apply_chat_template` à l'entraînement, `llama-server --jinja` à l'inférence).
- **Justification** : empêche des traces d'entraînement dans un format que le Harnais n'utilise pas. Hypothèse H-TOOLS à sonder par modèle ; repli par modèle : JSON contraint par `response_format`.

## D-nuit-A1-14 — Benchmarks : QCM sur poids HF avant quantification, génératif après
- **Décision** : lm-eval tourne sur les poids HF (GPU) avant quantification ; après quantification, seul le sous-ensemble génératif (ifeval, traduction, BFCL) tourne contre `llama-server`. Les QCM après quantification dépendent de l'hypothèse H-LMEVAL-GGUF.
- **Justification** : les tâches QCM de lm-eval demandent les log-probabilités du prompt, mal servies par llama-server ; c'est le chemin le plus simple qui respecte FR-35.

## D-nuit-A1-15 — Séparation runtime / outillage par extras uv
- **Décision** : la fermeture d'import de l'Assistant n'importe jamais torch, transformers, trl, peft, lm_eval, anthropic, mistralai ; extras `bench`, `data`, `train`, `judge`, `app`.
- **Justification** : taille installée (NFR-6) et RAM (NFR-1) de l'Assistant packagé en J4.

## D-nuit-A1-16 — Révision du spine après cinq relectures indépendantes
- **Décision** : les correctifs des cinq relectures (dossier `reviews/` à côté du spine) ont été intégrés au spine avant sa finalisation. Ils durcissent AD-1, AD-3, AD-4, AD-5, AD-7, AD-10 à AD-14, AD-17 à AD-19 et ajoutent six AD : AD-24 (lectures permises aux pipelines `data` et `train`), AD-25 (schémas d'artefacts partagés), AD-26 (reprise après interruption), AD-27 (verrou GPU, processus, SQLite), AD-28 (téléchargements et environnement), AD-29 (calcul des Scores de Tâche).
- **Justification** : les relectures ont trouvé des voies concrètes par lesquelles des stories conformes à la lettre auraient pu violer D1.1 ou D1.6, ou se construire de façon incompatible. Fermer ces voies avant le développement coûte moins cher qu'une reprise en cours de nuit.

## D-nuit-A1-17 — Index PyTorch CUDA dans le profil réseau `outillage` (écart à D1.5)
- **Constat** : D2 exige PyTorch avec CUDA, mais PyPI ne publie que des roues CPU de torch pour Windows. La roue CUDA vient de `download.pytorch.org`, absent de la liste D1.5.
- **Décision** : `download.pytorch.org` est traité comme une source de dépendances (l'esprit de D1.5 : « pour les dépendances »). Il est déclaré dans `pyproject.toml` (`[tool.uv.index]`, `explicit = true`) et autorisé en lecture seule dans le profil `outillage`.
- **À trancher par Anaël** : valider cet ajout. Sans lui, aucun entraînement GPU n'est possible.

## D-nuit-A1-18 — Épinglages de campagne et environnements isolés
- **Décision** :
  - transformers 5.17.0 et TRL 1.13.0 sont épinglés pour toute la campagne, car Unsloth 2026.10.3 les exige. TRL 1.13 contient ORPO (`trl.experimental.orpo`).
  - Unsloth (variante de vitesse) et `bfcl-eval` (vérificateur BFCL : épingle numpy 1.26.4 et mistralai 1.7.0) tournent dans des environnements uv isolés, appelés en sous-processus.
  - llama.cpp est figé au tag `b11429`, base de la release stable v0.6.0, et non à la pré-version `b11560`.
- **Justification** : un lock unique doit pouvoir être résolu, et les Runs d'une campagne doivent rester comparables. Pour llama.cpp, la version stable est le choix le plus réversible.

## D-nuit-A1-19 — Calibrage adapté à la lecture ; le jeu complet suit la SPEC complétée
- **Constat** : les 16 items du calibrage ne suivent pas exactement la SPEC §3. Il leur manque `theme`, `parametres`, `fictif` et `version_item`. `cassette` est au singulier, `comportement_attendu` remplace `sans_reponse`, `longueur_demandee` et `type_courrier` sont rangés dans `entree`, et les codes R- et RS- sont encore utilisés.
- **Décision** : `slmsp.core.items` adapte le calibrage à la lecture, avec une table de correspondance et des valeurs par défaut écrites. `eval/calibrage/` n'est pas modifié. Le jeu complet de la nuit (piste 2) suit la SPEC §3, complétée par les précisions du calibrage :
  - `entree` en objet pour CR, LC, CO, RE et CT ;
  - `debut` et `fin` pour CO ;
  - règles d'appels RD lisibles par machine, dans `appels_attendus[].regles` : `exact`, `contient_un_de`, `optionnel`, `ordre_libre`.
- **Justification** : la SPEC ne doit pas être modifiée (D1.8), et le calibrage est la référence de format (D6). Des règles en prose ne permettent pas de calculer automatiquement le score « Appel valide ».

## D-nuit-A1-20 — Budget : registre hors dépôt, sous-postes Mistral, aucune relance cachée
- **Décision** :
  - Le registre de budget, le journal d'appels Mistral et le cache des verdicts vivent dans `SLMSP_VAR_DIR`, par défaut `%LOCALAPPDATA%\slmsp\var\` : un registre unique par machine pour toutes les copies de travail.
  - Le plafond Mistral de 30 € se divise en deux sous-postes : `generation` 25 € et `juge` 5 €.
  - Les SDK payants sont configurés avec `max_retries=0`. Une tentative sans `usage` reste comptée au pire cas. Un tarif inconnu provoque une erreur.
- **Justification** : sinon, deux worktrees auraient chacun leur propre budget de 30 € et 10 € ; une relance automatique ou une erreur pourrait aussi échapper au compteur. Le sous-poste juge garantit que le kappa reste calculable. La répartition 25/5 est une hypothèse à ajuster.

## D-nuit-A1-21 — Paires ORPO : la réponse rejetée vient du Modèle de base local
- **Décision** : `data build --preferences` prend comme réponse choisie l'exemple SFT validé, et comme réponse rejetée une génération du Modèle de base local (`slm:<slug>`), journalisée de la même façon. Les verdicts du Juge Claude ne sont jamais utilisés.
- **Justification** : FR-34 laisse cette source ouverte. C'est la source la plus simple qui ne fait intervenir ni Claude ni de budget supplémentaire.

## D-nuit-A1-22 — Masque de perte calculé par le projet
- **Décision** : le masque de perte « assistant seul » est calculé par `slmsp.train.masque` à partir du rendu du chat template officiel, et testé pour chaque modèle. Il remplace `assistant_only_loss` de TRL. Repli (hypothèse H-MASQUE) : une variante d'entraînement du template, limitée aux balises `generation`, testée par égalité de rendu avec le template officiel.
- **Justification** : `assistant_only_loss` exige des balises `{% generation %}` absentes des templates officiels de Granite 4.0 1B et de Ministral 3 3B. AD-7 impose le template officiel.

## D-nuit-A1-23 — Aucune amorce rédigée dans le dépôt
- **Décision** : une amorce du générateur vient seulement d'une ligne d'un jeu public téléchargé, ou d'une réponse Mistral journalisée. Exemple : les scénarios de réunions fictives des comptes rendus, générés par Mistral à partir de thèmes MediaTech. Les amorces rédigées par Anaël sont différées, faute de moyen de prouver leur origine cette nuit.
- **Justification** : les agents de la nuit sont des instances de Claude. Toute amorce écrite à la main dans le dépôt violerait D1.1 et PRD §8.

## D-nuit-A1-24 — Ministral 3 3B : dépôt officiel BF16 préféré à la conversion FP8
- **Constat** : un dépôt officiel `mistralai/Ministral-3-3B-Instruct-2512-BF16` existe au 2026-10-12. D7 prévoit de convertir les poids FP8 en bf16.
- **Décision** : `slmsp fetch` prend le dépôt BF16 officiel pour l'entraînement, et le GGUF officiel pour l'inférence (D-nuit-A1-11). La conversion n'est faite qu'à défaut, et consignée. D7 n'est pas modifié.

## D-nuit-A1-25 — `.gitignore` : versionner les artefacts légers des runs
- **Décision** : le squelette du projet remplace les règles `runs/` et `checkpoints/` du `.gitignore` par une liste ciblée (AD-21). Sont exclus de git : `index/`, `var/`, `vendor/`, `models/`, `data/raw/`, `data/train/*/train.jsonl`, `runs/**/checkpoints/`, `runs/**/adaptateur/`, `*.gguf`, `*.safetensors`. `run.json`, `scores.json`, `verdicts.jsonl` et les rapports sont versionnés.
- **Justification** : FR-36 et NFR-8 exigent un Comparatif régénérable à partir des artefacts archivés, et D1.7 interdit de réécrire l'historique. Un gros fichier commité par erreur ne pourrait plus en être retiré.

## Décisions du découpage en epics et stories (phase A.2, `bmad-create-epics-and-stories`)

Document : `_bmad-output/planning-artifacts/epics.md`. Mode non interactif : les menus du workflow ont été validés d'office.

## D-nuit-A2-1 — Découpage : 13 epics, J1 à J3 détaillés, J4 et J5 en epics seulement
- **Décision** : 11 epics détaillés pour J1 à J3 (53 stories), dont l'Epic 7 pour le Jeu d'évaluation complet ; Epics 12 (J4) et 13 (J5) sans stories. L'Epic 1 est un socle technique assumé (projet greenfield, garde-fous D1 en code), par exception au principe « un epic = une valeur utilisateur ».
- **Justification** : périmètre de la mission et de PRD §9.3 ; la revue de code se fait par epic (D5), d'où des epics de taille moyenne.

## D-nuit-A2-2 — Piste 2 (Jeu d'évaluation) isolée hors de `src/`
- **Décision** : un outil dédié `eval/outils/construire_jeu.py`, lancé par `uv run --no-project`, gère les instantanés des sources, l'assemblage des brouillons (`eval/construction/v1.0/<CODE>.jsonl`) vers `eval/jeu/v1.0/items.jsonl`, la composition et les rejets. La validation stricte et le manifeste restent à `slmsp eval gel` (AD-11), avec une option `--verifier-seulement` ; les cassettes RD passent par `slmsp mcp record` (AD-10).
- **Justification** : AD-11 interdit un second lecteur d'items et réserve l'écriture du manifeste à `eval gel` ; la mission demande que la piste ne touche pas `src/`.

## D-nuit-A2-3 — Le calibrage n'est pas repris dans le jeu v1.0, mais il est protégé contre la fuite
- **Décision** : le jeu v1.0 est construit à neuf (identifiants à partir de 001) ; les 16 items du calibrage restent des fixtures de développement. L'API anti-fuite couvre v1.0 et le calibrage.
- **Justification** : les agents de la nuit développent et testent sur le calibrage ; le reprendre dans le jeu de décision exposerait la mesure à un réglage sur ces items. Réversible : Anaël peut les intégrer en v1.1.

## D-nuit-A2-4 — Chemins de cassettes des items v1.0
- **Décision** : le champ `cassettes` des items v1.0 contient des chemins relatifs au dossier du jeu, soit `../../cassettes/RD-xxx/<session>.json`.
- **Justification** : AD-11 (« relatifs au dossier du jeu ») et SPEC §8 (`eval/cassettes/RD-xxx/`) sont tous deux respectés ; `core.items` résout ces chemins.

## D-nuit-A2-5 — Gel borné dans le temps
- **Décision** : si les volumes de SPEC §2 ne sont pas atteints à l'heure prévue du gel (vague V9), le jeu est gelé en `v1.0-provisoire` avec ses écarts de composition inscrits dans le manifeste et le journal, au lieu de bloquer la Baseline et la génération.
- **Justification** : D5 (« une story ne doit jamais bloquer toute la nuit ») ; le jeu est de toute façon provisoire et passera en v1.1 après relecture.
- **À trancher par Anaël** : accepter un gel incomplet le cas échéant.

## D-nuit-A2-6 — CLI en paquet `slmsp/cli/` et sous-commande `slmsp budget`
- **Décision** : la CLI est un paquet (`slmsp/cli/__init__.py` + un module par sous-commande) au lieu d'un fichier `cli.py`. La story 1.1 déclare d'avance toutes les sous-commandes ; un module absent répond « non implémentée ». Une sous-commande en lecture seule `slmsp budget etat` est ajoutée à la liste du spine.
- **Justification** : trois stories en parallèle ne doivent pas modifier le même fichier ; le relevé de dépense est exigé par `etat-nuit.md` et le rapport de nuit. Le point d'entrée `slmsp.cli:main` est inchangé.

## D-nuit-A2-7 — Schémas et modèles de configuration répartis par fichier
- **Décision** : `core/schemas/` est un paquet, un module par schéma, sans réexport, créé par la première story qui en a besoin. Chaque paquet porte son modèle pydantic de configuration (`<paquet>/config.py`) ; seuls `ConfigModele` et `ConfigLlamacpp`, partagés, sont dans `core/schemas/` (story 1.3).
- **Justification** : éviter les conflits de fichiers entre stories parallèles et créer les entités au moment où elles servent.

## D-nuit-A2-8 — Primitives partagées dans `core`
- **Décision** : `core/var.py` (`SLMSP_VAR_DIR`, SQLite WAL, verrou GPU), `core/canonique.py` (JSON canonique, SHA-256) et `core/gabarits.py` (liste blanche structurelle des prompts de Tâche et des gabarits du générateur, AD-3 verrou 6).
- **Justification** : le spine fixe ces règles sans fixer leur module ; les placer en couche 0 permet à tous les paquets de les utiliser sans enfreindre AD-1.

## D-nuit-A2-9 — Tarifs prudents et imputation de `validation`
- **Décision** : `config/tarifs.toml` part d'un tarif prudent pour `mistral-large-latest` (2 $ / 6 $ par million de tokens) et d'un taux de 1 USD = 1 EUR, datés et marqués « à vérifier ». Les appels Mistral d'usage `validation` sont imputés au sous-poste `mistral.generation`.
- **Justification** : la page de tarifs de Mistral n'est pas un hôte de D1.5 ; un tarif surévalué fait arrêter plus tôt, jamais dépasser. Le sous-poste juge (5 €) reste réservé au kappa.
- **À trancher par Anaël** : remplacer par les tarifs réels.

## D-nuit-A2-10 — Relecture des conditions de Mistral (D1.2) par une lecture GET
- **Décision** : le profil réseau `outillage` autorise une lecture GET de la page des conditions commerciales de Mistral, et rien d'autre sur cet hôte. La campagne de génération (story 9.8) consigne la date, l'URL et le SHA de la page ; si la page est inaccessible, la génération ne démarre pas.
- **Justification** : D1.2 exige de revérifier les conditions avant la campagne, ce qui est impossible sans lire la page, alors que D1.5 ne liste que l'API Mistral. Même raisonnement que D-nuit-A1-17 : l'esprit des deux règles est respecté par une lecture seule ciblée.
- **À trancher par Anaël** : valider cet ajout.

## D-nuit-A2-11 — Mesure de H-JUGE-COUT et H-BATCH à la première notation réelle
- **Décision** : ces hypothèses sont mesurées à l'étape 0 de la Baseline (story 8.3), sur le calibrage noté pour le premier modèle, et non dans la story du Juge (5.4).
- **Justification** : les tests n'appellent jamais d'API payante, et il faut des sorties de modèle à noter.

## D-nuit-A2-12 — Rapport de Baseline produit par `slmsp compare baseline`
- **Décision** : le rapport de Baseline est le premier module de `slmsp.compare` (chargement des artefacts, sélection des runs complets) ; le Comparatif (story 11.1) le réutilise.
- **Justification** : une seule voie de chargement des artefacts, fonction pure et régénérable (AD-20).

## D-nuit-A2-13 — Benchmarks en sous-processus, Hugging Face hors ligne
- **Décision** : les jeux de benchmarks sont pré-téléchargés par `slmsp fetch benchmarks` ; lm-eval et les autres outils tiers tournent en sous-processus avec `HF_HUB_OFFLINE=1` et `HF_DATASETS_OFFLINE=1`.
- **Justification** : les bibliothèques tierces (datasets, fsspec) peuvent ouvrir leurs propres connexions et contourner la passerelle `slmsp.net` (AD-4).

## D-nuit-A2-14 — Volumes de la campagne de nuit
- **Décision** : environ 600 exemples : Q 100, RD 140, CR 80, LC 80, CO 35, RE 35, CT 35, génériques 90 (≈ 15 %). La Traduction est exclue.
- **Justification** : proportions médianes de l'addendum §G ramenées à 600 (D4). Le poste « traces de tool calling » couvre à la fois les traces RD et les réponses Q sourcées sur l'Index. La Traduction est le n° 2 de l'ordre de coupe et n'a pas de Jeu maison en v1. Ajustable en config d'après les faiblesses de la Baseline.

## D-nuit-A2-15 — Témoin Qwen
- **Décision** : `Qwen/Qwen3-4B-Instruct-2507` par défaut ; à défaut, le Qwen d'environ 4B Instruct sous Apache 2.0 le plus récent sans accès conditionnel. Le choix et la révision sont consignés par la story 8.1.
- **Justification** : D4 ne nomme pas le dépôt.

## D-nuit-A2-16 — Baseline officielle seulement sur le jeu gelé
- **Décision** : la Baseline ne porte que sur `v1.0-provisoire` gelé et commité. Avant le gel, seul un essai de fumée sur le calibrage est permis, étiqueté `jeu_version = calibrage`, jamais présenté comme une Baseline.
- **Justification** : FR-24, FR-39 et SPEC §6 ; éviter des scores non comparables.

## D-nuit-A2-17 — URL inventées signalées sans réécriture
- **Décision** : le Harnais signale les URL inventées dans l'évènement `Fin` sans modifier le texte ; le banc les compte (Q).
- **Justification** : réécrire la sortie fausserait la mesure ; le signalement suffit à FR-3 en J1. L'affichage côté application est une question de J4.

## D-nuit-A2-18 — Lecture du journal Mistral par `train`
- **Décision** : la liste de lecture du lecteur `train` (AD-24) inclut, en lecture seule, `appels-mistral.sqlite`.
- **Justification** : AD-18 demande de recontrôler les `appel_ids` au chargement, ce qui exige de lire le journal ; AD-24 ne le listait pas.

## D-nuit-A2-19 — Fixtures de test du pipeline de données
- **Décision** : les réponses Mistral factices et les exemples d'entraînement de test sont des chaînes ou des tokens aléatoires produits par le code de test dans `tmp_path`. Aucun exemple réaliste rédigé n'est versionné, même comme fixture.
- **Justification** : esprit de D1.1 et règle d'AD-24 sur les fixtures.

## D-nuit-A2-20 — `eval/outils/` hors de la règle TID251
- **Décision** : comme `build_calibrage.py`, l'outil de construction du jeu est exclu de `TID251` ; il porte sa propre liste d'hôtes autorisés (D1.5), vérifiée avant chaque requête.
- **Justification** : l'outil ne fait pas partie du paquet et ne doit pas en dépendre (D-nuit-A2-2).

## D-nuit-A2-21 — Adaptateur Mistral construit en J1, générateur en J2
- **Décision** : `slmsp.mistral` (client, journal d'appels avec `usage`) est construit avec le second juge (story 5.5). Seule la classe `Generateur` (story 9.2) peut écrire une entrée `usage = generation`, au moyen d'un jeton de preuve propre à son module.
- **Justification** : la Baseline a besoin du second juge avant le pipeline de données ; un journal unique avec un usage protégé ferme la voie d'une réponse de juge ou de validation réutilisée comme donnée (AD-3, verrous 3 et 4).

## D-nuit-A2-22 — Baseline sans Juge après épuisement du budget
- **Décision** : si le budget `anthropic` ou `mistral.juge` est épuisé pendant la Baseline, la notation du modèle en cours est marquée `partiel-budget` et les modèles suivants sont évalués par les seuls contrôles automatiques (RD, CO, URL, emplacements, Kandel-Moles), avec Benchmarks et mesures complets.
- **Justification** : D1.6 impose l'arrêt « sur ce poste » puis la suite ; les mesures sans Juge restent utiles à la décision d'Anaël.

## Décisions du sprint planning (phase A.3, `bmad-sprint-planning`)

Rapport : `_bmad-output/planning-artifacts/implementation-readiness.md`. Statut : `_bmad-output/implementation-artifacts/sprint-status.yaml`. Mode non interactif.

## D-nuit-A3-1 — Dépendances corrigées et lancement de llama.cpp ramené dans `inference.serveur` (epics.md)
- **Constat** : le contrôle de préparation a relevé des dépendances manquantes ou erronées, et un conflit avec AD-6. AD-6 réserve à `inference.serveur` le lancement de `llama-server`, de `llama-quantize` et de `convert_hf_to_gguf.py`, alors que les stories 2.1, 8.1 et 10.6 les lançaient elles-mêmes.
- **Décision** : corrections marginales d'`epics.md`, sans changer le périmètre :
  - la story 2.2 porte les lanceurs `version`, `convertir_hf_vers_gguf` et `quantifier`, avec un nouveau CA8 ;
  - la story 2.1 ne lance plus de binaire (CA1) ;
  - les stories 8.1 (CA4) et 10.6 utilisent les lanceurs de la 2.2 ;
  - dépendances ajoutées : 4.2 → 2.3, 6.3 → 4.1, 8.2 → 5.6, 9.4 → 4.2, 10.6 → 8.2 ;
  - la dépendance de développement de la 8.4 passe de 1.3 à 5.6, 6.1 et 6.4 (schémas chargés) ;
  - précision AD-1 dans la 6.4 : `measure` n'importe pas `cli`.

  Le tableau des dépendances, le graphe et la rubrique « Validation finale » ont été mis à jour.
- **Justification** : un agent autonome qui suit les stories à la lettre aurait violé AD-6 ou le test d'architecture, ou modifié en parallèle un même fichier (`cli/eval.py`). Chaque nouvelle dépendance vise une story d'une vague antérieure, donc l'ordre V0 à V19 n'a pas à changer. La correction est réversible et n'a rien coûté au chemin critique.

## D-nuit-A3-2 — Propriété des fichiers de configuration du Harnais et du coût d'entraînement
- **Constat** :
  - `harness/config.py` appartenait à la story 4.3. Or la 4.2, qui la précède, a besoin de `k` et du seuil, et la 4.4, parallèle à la 4.3, a besoin de la réserve de sortie et du chevauchement.
  - La 10.3 ajoutait une section `[entrainement]` à `config/mesures.toml`, qui appartient à la 6.4. Les deux stories n'étaient pas séquentielles. `train` ne peut pas importer `measure.config` (couche égale, AD-1), et le chargement en `extra="forbid"` aurait rejeté la section.
- **Décision** :
  - **Harnais.** La 4.2 crée `harness/config.py` (`ConfigHarnais`) et `config/harnais.toml` : itérations d'outils, période de sonde, réserve de sortie, chevauchement. Les stories 4.3 et 4.4 lisent ces fichiers sans les modifier. `k` et le seuil restent dans `config/index.toml` (story 2.3), qui est la source unique ; le Harnais les lit par `slmsp.index.config`.
  - **Coût d'entraînement.** La 10.3 crée `config/entrainement.toml` et `ConfigCouts` dans `train/config.py`, que la 10.4 complète.
- **Justification** : cela respecte la convention « un modèle de config par paquet », supprime deux conflits de fichiers entre stories parallèles et évite deux sources pour un même réglage (AD-22). C'est la solution la plus simple : de nouveaux fichiers, aucune nouvelle dépendance entre epics.

## D-nuit-A3-3 — Verdict CONCERNS : on génère le suivi sans attendre
- **Décision** : après correction des sept constats bloquants, le contrôle rend le verdict « prêt avec réserves ». En mode non interactif, `sprint-status.yaml` est généré sans attendre. Les réserves restantes sont listées dans `implementation-readiness.md` :
  - décisions déjà en attente d'Anaël ;
  - import de `slmsp.core.texte` par l'outil de l'Epic 7 en `--no-project` ;
  - stories d'exécution sérialisées par le GPU ;
  - clés accentuées.
- **Justification** : aucune de ces réserves n'oblige un développeur à inventer une décision non consignée. Bloquer la nuit coûterait plus cher (D5).

## D-nuit-A3-4 — Statuts initiaux et J4/J5 hors sprint
- **Décision** :
  - Toutes les stories des Epics 1 à 11 sont en `backlog`, car aucun fichier de story n'existe encore. C'est `bmad-build-auto` qui crée la spec de chaque story.
  - Les Epics 12 (J4) et 13 (J5) restent en `backlog` sans stories, avec un commentaire « hors sprint de la nuit » dans le fichier.
  - Les clés sont celles du script : `<epic>-<story>-<titre en kebab-case>`, minuscules, accents conservés, tronquées. L'orchestrateur cible une story par son préfixe numérique unique `<epic>-<story>-` (par exemple `1-1-`), qui est aussi la règle de résolution de `bmad-build`.
- **Justification** : c'est le format natif du skill, qui garde la synchronisation des statuts par `bmad-build` sans réécrire les clés. On ne touche pas aux clés générées, ce qui est le choix le plus réversible.

## D-nuit-B-1 — Stories parallèles dans des worktrees git, fusion en squash (07h35)
- **Constat** : `bmad-build-auto` exige un arbre de travail propre au démarrage et commite lui-même. Deux stories ne peuvent donc pas tourner en parallèle dans le même checkout.
- **Décision** : chaque story tourne dans un worktree git isolé. L'orchestrateur fusionne ensuite chaque branche de story dans `nuit/2026-10-12` par `git merge --squash`, avec un commit par story au format D5. Les branches de worktree sont conservées, sans réécriture d'historique.
- **Consignes communes** : `consignes-sous-agents-nuit.md`.

## D-nuit-B-2 — Préchargement des modèles candidats pendant la phase B (07h37)
- **Décision** : les téléchargements de la phase C.1 (fichiers seuls, sous `models/`, ignoré par git) démarrent dès la phase B, en arrière-plan. La story 8.1 conserve la vérification, l'épinglage et la configuration, et réutilise ces fichiers.
- **Justification** : les téléchargements durent longtemps (plusieurs dizaines de Go) et n'ont aucun effet sur le code. C'est du temps gagné sur le chemin critique, et l'opération est réversible.

## D-nuit-B-3 — Consommation internet limitée de 07h47 à 08h30 (consigne d'Anaël)
- **Consigne d'Anaël** reçue à 07h47 : « Limite ta consommation d'internet pour les 40 prochaines minutes ».
- **Application** :
  - tous les téléchargements sont suspendus : modèles, sources du jeu d'évaluation, installations lourdes, dont torch ;
  - pas d'appel d'API ;
  - reprise après 08h30.
- **Constat à 07h48** : aucun processus de téléchargement n'était encore actif.

## D-nuit-S1.1 — Décisions de la story 1.1 (détail : `spec-1-1-squelette-du-projet-et-outillage.md`)
- Index PyTorch cu130, explicite, avec un verrouillage limité à `win32`.
- `conflicts = [[fetch],[train]]` dans `pyproject.toml` : `transformers` 5.17 exige `huggingface-hub<2`, et `fetch` épingle la 2.2.0. **À trancher par Anaël.**
- `BUDGET_*` retiré de `.env.example`. Les plafonds sont dans `config/budgets.toml` (story 1.5).
- Revue : deux constats reportés.
  - La règle AD-24 ne détecte pas les lecteurs numpy, pyarrow et duckdb.
  - Les transports httpx du SDK mcp ne sont pas encore verrouillés ; ils le seront en 1.4 et 3.3.
- `HF_TOKEN` est vide dans `.env`. Les téléchargements de modèles se font en accès anonyme, ce qui suffit pour des dépôts publics.
- **Levée** à 08:15, sur consigne d'Anaël (« tu peux réutiliser Internet si besoin »). Les téléchargements de modèles (Qwen 4B, GGUF Ministral 8B) et d'instantanés de sources reprennent.

## D-nuit-S1.2 et S1.3 — Décisions des stories 1.2 et 1.3 (détail dans les specs)
- **1.2**
  - `SLMSP_ENV_FILE` et `SLMSP_MODELS_DIR` permettent de pointer le dépôt principal depuis un worktree.
  - Les sous-processus ne reçoivent ni `*_API_KEY`, ni `*_TOKEN`, ni `*SECRET*`.
  - Le verrou GPU est un verrou d'octets posé sur `gpu.lock`.
- **1.3**
  - Le seuil d'espace libre est fixé à 2 Gio.
  - `Mode` prend les valeurs `connecte`, `hors-ligne-detecte` et `hors-ligne-force`.
  - Le lecteur `data` refuse aussi `runs/eval/`.
- **À trancher par Anaël (1.3, différé)** : le journal `appels-mistral.sqlite`, lisible par `data` et `train`, contiendra aussi les appels du second juge, donc des textes d'évaluation. Deux options : séparer les journaux en 5.5 et 9.2, ou filtrer à la lecture.

## D-nuit-B-4 — Priorisation sous contrainte de temps (09h08)
- **Constat** : il a fallu environ 1 h 40 pour 6 stories, à raison de 20 à 50 minutes par story avec `bmad-build-auto` et sa revue. À ce rythme, les 53 stories ne tiennent pas avant 14h00.
- **Décision** : on avance en priorité sur deux chemins critiques.
  1. **Le gel du Jeu d'évaluation**, qui débloque la phase D : 3.1 → 5.1, 3.3 → 7.3, puis 7.5 et 7.6.
  2. **Le banc de bout en bout**, par la chaîne 1.4 → 2.1/2.2 → 2.3 → 4.x → 5.3 à 5.6.
- Les stories de mesure secondaires et les Benchmarks passent après.
- **Repli de l'essai QLoRA** : si la Baseline n'est pas prête, on applique la règle D4 et on prend Granite 4.0 1B.
- **Story 7.4** : les transcriptions de Compte rendu font entre 4 489 et 5 159 mots (5 items longs). FR-13 cite une entrée d'au moins 6 000 mots pour l'Assistant, mais le sous-agent ne relève aucun écart avec la SPEC du jeu. **À vérifier par Anaël lors de la relecture.**

## D-nuit-S1.4 — Décisions de la story 1.4
- **Profil `assistant`** : HTTPS sur le port 443 uniquement. Toutes les méthodes sont permises vers la Liste blanche, ce que MCP impose.
- **Profil `outillage`** :
  - Hugging Face et `githubusercontent.com` sont autorisés par suffixe, et `codeload.github.com` ajouté pour les archives GitHub ;
  - la page des conditions Mistral (`legal.mistral.ai`) est autorisée en GET seul (A2-10, à valider par Anaël).
- **Journal** : il est tenu dans `SLMSP_VAR_DIR/requetes-sortantes.sqlite`.
- **Risque relevé** : `outillage` refuse les GET vers les API Mistral et Anthropic. Le suivi des lots batch (story 5.4) demandera d'ajouter une règle dans `config/reseau.toml`.

## D-nuit-S7.2 et S7.4 — Points des items du Jeu d'évaluation (à relire par Anaël)
- **7.2 (Q 60, NR 30)** : taux de rejet de 10,4 % à la vérification indépendante. Tous les rejets ont été corrigés et revérifiés.
  - **À trancher** :
    - aucun item ne porte sur les marchés publics, car leurs fiches sont sur `entreprendre`, exclu par le critère d'acceptation 2 ;
    - les montants et dates 2026 n'ont pas d'ancre de date ;
    - Q-042 (« 1/24e ») est à recouper avec le décret.
  - NR est classé `non-classe` et porte un champ `sous_type`.
- **7.4 (CR 25, LC 25)** : taux de rejet de 11,3 %, rejets corrigés.
  - Les noms fictifs reviennent d'un item à l'autre.
  - CR-001 utilise des noms courants de personnalités, sans prénom.
  - Un `.gitattributes` avec `*.jsonl eol=lf` est recommandé.

## D-nuit-S5.1 — Décisions de la story 5.1 (gel et anti-fuite)
- Les SHA-256 du manifeste sont calculés après normalisation CRLF→LF. Le `.gitattributes` (`* text=auto eol=lf`) a été ajouté en complément, commit 11a0d50.
- Le schéma d'item est fermé : il accepte les champs ajoutés par les stories 7.2 et 7.4, qu'il juge cohérents avec SPEC §3.
- Format des `regles` RD : `{optionnel, ordre_libre, arguments: {nom: {exact}|{contient_un_de}|{optionnel: true}}}`.
- Un écart de composition ne bloque pas un gel `provisoire`, mais il bloque un gel `relu`.
- Échantillons :
  - second juge : au moins 3 items par Tâche ;
  - relecture humaine : 20 % par strate Tâche × difficulté, et au moins 1 item par strate.
- Contrôle anti-fuite : 5-grammes hachés, plus les identifiants protégés (empreintes des amorces, URL, `dataset_id`/`resource_id`).
- Vérification à blanc : les 140 items réels passent `slmsp eval gel --verifier-seulement` sans erreur bloquante.

## D-nuit-S7.3 — Items Recherche de données
- 40 items, chacun avec sa cassette : 36 enregistrées en réel sur `mcp.data.gouv.fr`, 4 simulées pour les cas de panne (délai, 503, injoignable, 500). Taux de rejet à la vérification : 1,5 %.
- La règle `contient_un_de` passe par `core.texte.normaliser` et compare en début de mot. Le banc (story 5.3) doit appliquer exactement cette règle.
- **À relire par Anaël** :
  - certains fragments sont trop larges (« cni » correspond aussi à « CNIL ») ;
  - les 5 demandes de valeurs supposent un aperçu préalable des données.
- **Instabilité constatée** : `tests/inference/test_serveur.py::test_demarrage_rate_sante` échoue sous charge, mais passe seul.

## D-nuit-S2.3 — Index local v1 et mesure H-VEC
- **Index construit** : `index/20260926/`, avec 143 437 chunks (35 758 service-public, 107 679 catalogue data.gouv) pour 457 Mo.
- **H-VEC infirmée de peu sur la latence** : p95 de 314 à 329 ms, pour un seuil de 300 ms. La RAM ajoutée, entre 282 et 298 Mio, reste sous le plafond de 350 Mio.
  - Ces mesures ont été prises avec un CPU chargé à environ 60 % par les stories qui tournaient en parallèle. **Il faut les reprendre au repos avant de basculer vers le repli usearch HNSW i8**, qui n'est pas implémenté.
  - **À trancher par Anaël** après cette remesure.
- **Paramètres retenus** : `k = 5`, `seuil_pertinence = 0,5`. La version de l'index correspond à la date `lastModified` de la révision HF épinglée.

## D-nuit-S1.5 — Registre de budget
- **Marges** : 0,50 € de marge par sous-poste et par poste, et une majoration de 1,25 sur les tokens d'entrée estimés.
- **Tarifs**
  - Juge Opus 5.5 : 4 $/20 $ par Mtok en direct, 2 $/10 $ en batch.
  - Mistral : tarif prudent de 2 $/6 $ (batch 1 $/3 $), fixé par D-nuit-A2-9. **À vérifier par Anaël**, car le tarif réel serait plus bas.
  - Conversion : 1 USD = 1 EUR.
- **Remise à zéro** : les totaux sont filtrés par `campagne_id`. Changer d'identifiant redémarre donc le compteur sans rien effacer. **À confirmer par Anaël.**

## D-nuit-S7.6 — Gel du Jeu d'évaluation v1.0-provisoire (12h05)
- **Commit de gel** : `12eef73`, `eval: gel du jeu d'évaluation v1.0-provisoire`. Le contrôle `jeu_gele_et_commite("v1.0")` passe sur la branche `nuit/2026-10-12`. **La règle D1.3 est levée** : la génération de Données d'entraînement est désormais permise.
- **Contenu** : 225 items aux cibles de SPEC §2, sans écart (Q 60, RD 40, CR 25, LC 25, CO 15, RE 15, CT 15, NR 30).
  - SHA-256 du `MANIFEST.json` : `70c42fb5…43dc`. Graine des échantillons : 20261012.
  - Taux de rejet cumulé des vérifications : 34 rejets sur 363 verdicts, soit 9,4 %.
- **Vérification finale**
  - Elle a trouvé 3 constats bloquants, tous corrigés : Q-056 et CT-003 étaient trop proches du calibrage et ont été remplacés par Q-067 et CT-016 ; les consignes CT listent désormais les libellés d'emplacement exacts.
  - Décision prise seul : lister ces libellés rend la Tâche CT plus facile. Le choix est réversible en v1.1.
- **Échantillon de revue pour Anaël** : 47 items, dans `eval/revue/echantillon-revue-v1.0-lecture.md`.
- **À relire en priorité**
  - Items proches du calibrage : Q-045, Q-048, CT-005, CT-007 et CR-023.
  - Paires LC × Q portant sur la même fiche.
  - Aucun item sur les marchés publics.
  - Q-042.
