# Epic 9 Context: Données d'entraînement prouvées

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Livrer un jeu d'entraînement versionné et immuable (`data/train/vN/`), généré par Mistral seul, validé contre ses sources et le Bac à sable, filtré des doublons et de toute fuite du Jeu d'évaluation, tracé au Registre des licences, et dont chaque ligne est re-dérivable octet par octet depuis les réponses Mistral journalisées. C'est la preuve exigée par la règle bloquante « Claude ne génère aucune Donnée d'entraînement », et le jeu v1 (~600 exemples) qui alimente l'essai QLoRA de la nuit.

## Stories

- Story 9.1: Registre des licences et configuration des données
- Story 9.2: Générateur Mistral prouvé (gabarits sans exemple, journal d'appels)
- Story 9.3: Étape `seed` : amorces publiques ou Mistral, exclusion anti-fuite
- Story 9.4: Étape `generate` : génération idempotente et traces d'outils
- Story 9.5: Étapes `validate` et `filter`
- Story 9.6: Étape `build` : re-dérivation, jeu versionné et suite des verrous AD-3
- Story 9.7: Paires de préférence ORPO
- Story 9.8: Campagne de génération de la nuit (jeu v1)

## Requirements & Constraints

- **Génération** par un générateur autorisé, budget plafonné, arrêt au plafond, provenance par exemple (générateur, version du gabarit, source, date).
- **Validation et filtrage** : rejeu des traces contre le Bac à sable, vérification contre la source, doublons et fuites exclus ; taux de rejet par motif et par Tâche ; échantillon de relecture humaine non bloquant.
- **Licences** : toute source absente du registre fait échouer la construction ; la variante diffusable refuse toute source non `diffusable` ; la variante `recherche` est marquée comme telle ; les sources `evaluation_seulement` sont refusées dès `seed`.
- **Pas de génération avant le gel** : `generate` refuse (code 4) si le commit de gel du Jeu d'évaluation `v1.0` n'existe pas ou n'est pas un ancêtre de `HEAD`.
- **Budget** : `mistral.generation` ≤ 25 € (sur 30 € Mistral) ; ordre de dépense Q, RD, CR, LC, puis génériques, puis CT, RE, CO ; sur `BudgetEpuise`, run marqué `partiel-budget`.
- **Volumes de la nuit** : Q 100, RD 140, CR 80, LC 80, CO 35, RE 35, CT 35, génériques 90 ; Traduction exclue.
- **Paires ORPO** : `chosen` = exemple SFT validé, `rejected` = génération du Modèle de base local ; dérogation d'équité documentée dans le MANIFEST.
- **Tests** : aucun appel d'API payante ; transport Mistral factice ; aucune fixture, aucun test et aucun fichier du dépôt ne contient d'exemple d'entraînement rédigé. Les réponses factices et données de test sont des chaînes ou tokens aléatoires produits par le code de test dans `tmp_path`.

## Technical Decisions

**Garde-fou D1.1 / AD-3 : Claude ne produit aucune Donnée d'entraînement** (ni exemple, ni réponse cible, ni few-shot, ni amorce, ni scénario, ni verdict, ni fixture, même reformulé par Mistral). Six verrous, tous testés et regroupés dans `tests/data/test_verrous_ad3.py` (story 9.6) :

1. **Imports** : `anthropic` importable seulement dans `slmsp/judge/` (ruff `TID251` + `per-file-ignores`) ; `slmsp.data` et `slmsp.train` n'importent jamais `slmsp.judge`.
2. **Lectures (AD-24)** : toute lecture de `data`/`train` passe par `core.artefacts.lire(chemin, lecteur=...)` ; test AST interdisant `open`, `Path.read_*`, `json.load` ailleurs. `data` lit seulement `data/raw/`, `data/cassettes/`, ses runs `runs/data-*`, `config/prompts/`, `config/outils-mcp.toml`, `data/registre-licences.toml`, les journaux de `SLMSP_VAR_DIR` et l'Index local. Le Jeu d'évaluation n'est visible que via l'API anti-fuite de `core.items` (empreintes, n-grammes, jamais de texte). Refus de `eval/`, `runs/eval-*`, du cache des verdicts et de tout fichier écrit à la main.
3. **Requête prouvée** : `Generateur.generer(gabarit_id, amorce_ids, session_id, tache, messages_precedents=None)` n'a aucun paramètre de texte libre ; il résout lui-même gabarit et amorces (artefact `seed`, `sha_texte` revérifié). Un message `assistant` précédent n'est accepté que si son JSON canonique égale une réponse journalisée de la même `session_id` ; un message `tool` seulement s'il vient d'une cassette `data/cassettes/` de la même session ; sinon `ProvenanceInvalide`.
4. **Réponse prouvée** : `build` refabrique chaque ligne depuis les réponses brutes journalisées `usage = generation` seulement, via l'extracteur pur et versionné `slmsp.data.extraction` (`VERSION_EXTRACTEUR`), puis compare octet par octet. Seules transformations admises : prompt système de Tâche (SHA consigné), passages formatés par `harness.prompts`, messages `tool` des cassettes de la même session. Un `appel_id` inconnu ou d'usage `juge-second`/`validation` fait échouer le build.
5. **Amorces** : uniquement une ligne d'un jeu public téléchargé (`jeu`, `revision`, `ligne`, `sha_texte`) ou une réponse Mistral journalisée (`appel_id`, ex. scénarios de réunions fictives à partir de thèmes MediaTech). `RegistreLicences` porte `auteur_contenu` ∈ {`public`, `mistral`, `anael`} et `genere_par` ; `claude`, `inconnu` ou une source distillée d'un modèle non autorisé lèvent `ProvenanceInvalide`. Aucun fichier d'amorces rédigé dans le dépôt n'est accepté ; les amorces d'Anaël restent différées.
6. **Gabarits et verdicts** : gabarits (`config/prompts/generateur/`) et prompts de Tâche passent la liste blanche structurelle de `core.gabarits` (front-matter, sections « Consigne » et « Emplacements », longueur maximale, aucun bloc de code, aucun JSON, aucun exemple de sortie ; SHA au MANIFEST). Aucun verdict ni justification du Juge Claude ne sert à filtrer, classer ou construire des données ou des paires ORPO ; aucun chemin de verdict n'est accepté en entrée du pipeline.

**D1.2 : générateur = Mistral via l'API, `mistral-large-latest` en version stable**, jamais un modèle « Labs » ni une préversion. Préalable de `generate` : `config/donnees.toml` doit porter une date de vérification des conditions commerciales Mistral égale au jour même et un modèle résolu présent dans la liste stable autorisée, sinon refus de démarrer. La campagne relit la page des conditions par GET (profil `outillage`) et inscrit date, URL et SHA ; page inaccessible = pas de génération, blocage consigné. Repli local du générateur non outillé.

**Journal `appels-mistral.sqlite`** (dans `SLMSP_VAR_DIR`, hors dépôt, jamais supprimé) : chaque entrée porte `session_id`, `usage` ∈ {`generation`, `juge-second`, `validation`}, le modèle résolu, la requête complète (SHA du gabarit, `amorce_ids`), la réponse brute intégrale, son SHA et la référence `RegistreBudget`. Seul `Generateur` peut écrire `usage = generation` (jeton de preuve propre au module). Le contrôle de fidélité de `validate` utilise `usage = validation` et le gabarit `validation`. Le journal sert aussi à l'idempotence : une clé (amorce, gabarit, version) déjà journalisée réutilise la réponse sans nouvel appel.

**AD-17 : pipeline `seed → generate → validate → filter → build`**, chaque étape étant un run `runs/data-<etape>/<run_id>/` lancé par `slmsp data <etape> --depuis <run_id parent>` :
- `seed` : amorces conformes au verrou 5 ; exclut dès ce stade les amorces dont le texte normalisé ou l'identifiant correspond à une `amorce_usager`, une `provenance` ou un `dataset_id`/`resource_id` d'un item (v1.0 et calibrage) ; produit `amorces.jsonl` et les comptes par Tâche et par motif.
- `generate` : idempotent ; traces RD avec `tool_calls` validés contre `config/outils-mcp.toml`, exécutés en direct (profil `outillage`) et enregistrés par `mcp.enregistrer(session, "data")` sous `data/cassettes/<session_id>.json` ; CR en deux temps (transcription puis compte rendu) ; une ligne par session dans `brut.jsonl` ; `--reprendre` en ajout seul (AD-26).
- `validate` : rejeu sur `BacASable` (`trace_divergente`, `appel_non_conforme`), URL et valeurs de la réponse finale présentes dans les résultats d'outils ou passages via `harness.citations` et `core.texte.extraire_nombres` (`url_inventee`, `valeur_absente`) ; fidélité par règle ou Mistral, jamais par le Juge Claude.
- `filter` : doublons exacts et proches (`doublon`), anti-fuite par Jaccard de n-grammes hachés (`fuite_ngram`) et cosinus BGE-M3 (`fuite_cosinus`), seuils dans `config/donnees.toml`.
- `build` : `vN` par incrément, `train.jsonl` au schéma `LigneEntrainement` (`messages[0]` = prompt de Tâche, `tools`, `tache`, `meta{generateur, appel_ids, session_id, version_gabarit, version_extracteur, source, licence, date}`) ; `MANIFEST.json` (`ManifesteJeuEntrainement`) avec SHA, comptes par Tâche, rejets par motif, instantané du registre, SHA des gabarits, prompts et `outils-mcp.toml`, date de vérification Mistral et modèle générateur. Une version n'est jamais réécrite. `train.jsonl` reste hors git, MANIFEST et registre sont commités.

**Autres conventions** : budget par `RegistreBudget` (réservation au pire cas, `max_retries=0`) ; clients réseau obtenus via `slmsp.net.client(profil)` ; schémas dans `slmsp.core.schemas/<nom>.py` avec `schema_version` ; sous-commandes dans `src/slmsp/cli/data.py` ; ORPO journalisé dans `SLMSP_VAR_DIR/generations-locales.sqlite` (même forme, `generateur = slm:<slug>`).

## Cross-Story Dependencies

- Chaîne interne : 9.1 → 9.2 → 9.3 → 9.4 → 9.5 → 9.6 → 9.7 et 9.8.
- Prérequis externes : 1.3 (artefacts/budget), 2.1 et 2.3 (téléchargement, embedder BGE-M3), 3.2 et 3.3 (Bac à sable, `mcp.enregistrer`, client MCP), 4.1 et 4.2 (`harness.prompts`, `harness.recherche_index`), 5.1 (API anti-fuite de `core.items`), 5.5 (adaptateur Mistral et journal), 8.1 (Modèle de base local pour ORPO).
- Exécution réelle de `generate` et campagne 9.8 seulement après le gel 7.6 ; 8.4 (faiblesses de la Baseline) recommandée avant 9.8.
- L'Epic 10 consomme `data/train/vN/` : `train` revérifie que le MANIFEST vient d'un run `data-build` et recontrôle les `appel_ids` contre le journal ; sans jeu construit, le Run est consigné bloqué.
