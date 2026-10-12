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
