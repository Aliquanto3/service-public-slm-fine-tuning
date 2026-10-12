# Epic 8 Context: Modèles candidats et Baseline

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Préparer les Modèles de base candidats (téléchargés à des révisions épinglées et vérifiés pour Windows natif et la RTX 3050), sonder leur tool calling (H-TOOLS), exécuter la Baseline de chacun (Jeu d'évaluation maison gelé, socle de Benchmarks, mesures techniques) et produire un rapport de Baseline régénérable à partir des seuls artefacts. Ce rapport fournit à Anaël les éléments chiffrés pour la décision go/no-go et pour le choix du modèle de l'essai M1 QLoRA. L'epic ne prend jamais cette décision. Son module de chargement des artefacts sert ensuite de socle au Comparatif.

## Stories

- Story 8.1 : Téléchargement et préparation des Modèles de base candidats
- Story 8.2 : Sonde de tool calling par modèle (H-TOOLS)
- Story 8.3 : Exécution de la Baseline (Jeu maison, Benchmarks, mesures)
- Story 8.4 : Rapport de Baseline

## Requirements & Constraints

- **Candidats et ordre de passage** (slugs) : `granite-4.0-1b`, `ministral-3-3b`, `smollm3-3b`, `qwen-4b`, puis `ministral-3-8b` en plafond de qualité, en évaluation seulement et si le temps le permet. Le 8B n'est téléchargé qu'en GGUF.
- **Formats** : GGUF Q4_K_M pour l'inférence, poids HF bf16 pour l'entraînement.
- **Contrôles par modèle** :
  - Granite 4.0 1B déclare `granitemoehybrid` : il est refusé si une couche de `config.json` n'est pas de type attention (la variante hybride Mamba est écartée sous Windows). Son support par llama.cpp se vérifie en démarrant `llama-server` sur son GGUF.
  - Ministral 3 3B : le dépôt officiel BF16 sert à l'entraînement (les poids Instruct sont en FP8, que la RTX 3050 ne gère pas). Le GGUF officiel sert à l'inférence s'il propose Q4_K_M ; à défaut, la conversion est faite et consignée. L'encodeur vision est exclu (`exclure_vision = true`, aucun projecteur multimodal chargé).
  - Témoin Qwen : `Qwen/Qwen3-4B-Instruct-2507` par défaut ; à défaut, le Qwen Instruct d'environ 4B le plus récent, sous Apache 2.0 et sans accès conditionnel. Le choix et la révision sont consignés.
  - Chat template : si celui du GGUF diffère de celui du tokenizer HF (comparaison des SHA), inscrire `chat_template_force = true` et exporter le template du tokenizer sous `models/<slug>/chat_template.jinja`.
- **H-TOOLS** : les appels d'outils doivent être valides sur les items R-001 et R-002 du calibrage en protocole `natif` (parseur `--jinja`). Sinon, on bascule par modèle sur `json-generique` (JSON contraint par `response_format`).
- **Baseline officielle seulement sur le jeu `v1.0-provisoire` gelé et commité.** Avant le gel, seul un essai de fumée sur le calibrage est permis, étiqueté `jeu_version = calibrage`, et il n'est jamais présenté comme une Baseline.
- **Budgets durs** : Anthropic 10 € (Juge principal), `mistral.juge` 5 €. Sur `BudgetEpuise`, la notation du modèle courant passe en `partiel-budget`, les Benchmarks et les mesures continuent, et les modèles suivants sont notés par les seuls contrôles automatiques (RD, CO, URL, emplacements, Kandel-Moles). Tout cela est consigné. Environ trois évaluations complètes avec Juge tiennent dans 10 €.
- **Hypothèses mesurées pendant la Baseline** :
  - H-JUGE-COUT (≈ 0,018 $ par item en batch) et H-BATCH (un lot revient avant la fin du run) : à l'étape 0, sur le calibrage noté pour Granite, avec le coût lu dans le `RegistreBudget`. Un ajustement de `config/juges.toml` (effort, `delai_max_lot`) est consigné s'il le faut.
  - H-SOCLE-2H : socle de Benchmarks d'un 3B en 4 bits en moins de 2 h ; en cas de dépassement, réduire les limites d'items en config et le consigner.
  - H-RAM : Assistant complet ≤ 5 Go, 4 Go visés.
- **Conformité aux NFR rapportée** : RAM ≤ 5 Go (NFR-1), débit ≥ 8 tokens/s (NFR-2), premier token < 5 s (NFR-3). Le rapport rappelle que la machine de dev n'est pas le PC cible.
- **Rapport** : par modèle, il présente les Scores de Tâche avec leurs statuts (« non relus », `fragile`, `plafonne_lc`, effectifs invalides et non jugés), les Benchmarks, les mesures et le coût du Juge. Il contient aussi une section « faiblesses principales par Tâche » (composantes les plus basses, motifs d'échec fréquents) et une section « éléments pour la décision d'Anaël » (meilleur modèle de 3B ou moins tenant dans 5 Go). Il ne prend aucune décision go/no-go.
- **Interdits** : ne jamais supprimer de données téléchargées ni d'artefacts d'évaluation ; aucune publication ; aucune API payante dans les tests.

## Technical Decisions

- **Téléchargement** : `slmsp fetch` est le seul téléchargeur (profil réseau `outillage`). Les poids vont sous `models/<slug>/{hf,hf-bf16,gguf}/`, avec `HF_HOME=models/.cache-hf` et un contrôle de l'espace disque avant toute écriture de plus de 1 Go. Chaque `config/modeles/<slug>.toml` épingle `revision` (commit HF), le fichier GGUF attendu et son SHA-256, la source du GGUF (officielle, communautaire réputée ou conversion maison au tag b11429) et les paramètres d'inférence : contexte, cache KV, threads, `reasoning`, `chat_template_kwargs`, `protocole_outils`. Ces valeurs valent aussi pour l'entraînement.
- **llama.cpp** : seul `slmsp.inference.serveur` lance `llama-server`, `llama-quantize` et `convert_hf_to_gguf.py` (lanceurs `convertir_hf_vers_gguf` et `quantifier` de la story 2.2). Aucune story de l'epic ne lance ces binaires elle-même.
- **Les modèles sont peut-être déjà téléchargés** en arrière-plan dans `models/` (préchargement de la phase B). La story 8.1 réutilise ces fichiers et garde la vérification, l'épinglage et la configuration.
- **Évaluation** : deux runs sans réseau, `eval-generation` puis `eval-notation` (parent : la génération). Ils tournent sur `BacASable`, `ModeFixe(item.mode)`, avec le profil réseau `aucun`, en décodage glouton, avec une graine fixe et `--parallel 1`. Le modèle est désigné par `ModeleRef` `base:<slug>` en Q4_K_M, variante `cuda` pour l'évaluation. `--chat-template-file` impose le template du tokenizer si `chat_template_force` est vrai.
- **Benchmarks** : les QCM tournent sous lm-eval sur les poids HF, avant quantification seulement (lm-eval ne charge pas ces modèles en GGUF). ifeval, la traduction et BFCL tournent contre `llama-server`.
- **Mesures** : binaire `cpu`, RAM = pic de la somme des working sets de l'arbre de processus (100 ms, psutil), Index local chargé. `measure` exige qu'aucune autre commande `slmsp` ne tourne.
- **Ressources** : toute commande CUDA (`eval` cuda, `bench`) prend `gpu.lock`. Les commandes longues tournent en arrière-plan et sont sérialisées par ce verrou. `llama-server` tourne dans un Job Object `KILL_ON_JOB_CLOSE`.
- **Artefacts** : `runs/<type>/<run_id>/` avec `run_id` = `AAAAMMJJ-HHMMSS-<slug>-<4 hex>`, et `run.json` (`RunManifest`) dont `statut` ∈ {`en_cours`, `complet`, `partiel-budget`, `partiel-erreur`, `interrompu`, `degrade`}. Aucune suppression ni réécriture ; la reprise se fait avec `--reprendre <run_id>`, en ajout seul. Fichiers lus et écrits uniquement via les schémas pydantic de `slmsp.core.schemas` (`Scores`, `ResultatBench`, `ResultatMesure`, `Verdict`, `Generation`).
- **`slmsp.compare` est une fonction pure des artefacts** : aucun appel de modèle ni de réseau. Les runs non `complet` sont exclus ou marqués. Pour une génération donnée, la notation retenue est la plus récente parmi les complètes. Le rendu refuse de mélanger deux versions du jeu. Le rendu Markdown est déterministe, régénérable à l'octet près, et testé par instantané sur des runs synthétiques. Sortie par défaut : `_bmad-output/implementation-artifacts/baseline-rapport.md`. `compare comparatif` reste déclarée « non implémentée » jusqu'à la story 11.1.
- **Couches** : `fetch`, `evaluation`, `measure`, `compare` sont de couche 3 ; `cli` de couche 4. Un module CLI par commande ; `measure` n'importe pas `cli`.
- **Tests** : vérifications de 8.1 sur des `config.json` de fixture (dense, hybride, FP8) ; téléchargements réels marqués `reseau`. Pour 8.2, un `FakeLlm` produit des appels malformés en natif et valides en JSON ; la sonde réelle est marquée `lent`. La 8.3 est une story d'exécution : sa preuve tient dans les runs archivés, le relevé `slmsp budget etat` et le journal, sans nouveau test unitaire.

## Cross-Story Dependencies

- **8.1** dépend de 2.1 (fetch) et 2.2 (lanceurs llama.cpp). Elle débloque 8.2, 9.7 et 10.1.
- **8.2** dépend de 8.1, 4.3 (boucle d'outils), 5.1 et 5.6 (assemblage d'évaluation de 5.3). Elle modifie `cli/eval.py` après 5.3 et 5.6, jamais en parallèle. Elle fixe `protocole_outils` dans chaque `config/modeles/<slug>.toml`. La 10.6 en dépend.
- **8.3** dépend de 8.2, 5.6, 6.2, 6.3, 6.4 et 7.6 (gel du jeu, déjà fait). Elle a besoin du GPU et des budgets. Après chaque modèle, elle met à jour `etat-nuit.md` avec la dépense par API.
- **8.4** se développe dès que 5.6, 6.1 et 6.4 sont faites (schémas chargés), sur fixtures, en parallèle de 8.3. Elle a besoin de 8.3 pour produire le rapport réel. La 11.1 réutilise `compare/chargement.py` et `cli/compare.py`. La 9.8 recommande ce rapport pour cibler les Données d'entraînement.
- **Hors epic** : la 11.2 choisit le modèle de l'essai M1 d'après la Baseline (meilleur Score de Tâche moyen parmi les modèles de 3B ou moins tenant dans 5 Go ; à défaut, Granite 4.0 1B). En cas de retard, Ministral 3 8B est la première coupe de la 8.3.
