---
title: 'Story 9.3 — Étape seed : amorces publiques ou Mistral, exclusion anti-fuite'
type: 'feature'
created: '2026-10-13'
status: done
baseline_revision: 'bfceaef62a6e2419abba861f93d84053beb4846f'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-9-context.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Le Générateur (9.2) résout ses amorces dans `runs/data-seed/<run_id>/amorces.jsonl`, mais aucune étape ne produit ce fichier : rien ne garantit qu'une amorce vienne d'une ligne publique relue sur disque ou d'une réponse Mistral journalisée, ni qu'aucune ne recoupe le Jeu d'évaluation (v1.0 et v1.1 gelé).

**Approach:** `slmsp.data.seed` constitue les amorces par des règles fixes (jeu public, colonne, Tâche, emplacement), refuse les sources non admises par le Registre des licences, exclut les candidats qui touchent un item d'évaluation (comptés par motif), ajoute des scénarios de réunion Mistral (opt-in), et clôt un run `data-seed` portant `amorces.jsonl` et `comptes.json`. `slmsp data seed` l'expose.

## Boundaries & Constraints

**Always:**
- Zone : `src/slmsp/data/seed.py`, `src/slmsp/cli/data.py`, `config/sources.toml`, `tests/data/test_seed.py`, `tests/cli/test_data.py` (si créé), ce fichier de spec, et la mise à jour de l'assertion de `tests/fetch/test_sources.py::test_config_versionnee` (nouveau jeu `piaf`).
- D1.1 : aucun texte d'amorce, de thème ou de consigne n'est écrit dans le code, la config ou les tests. Les fixtures sont des chaînes factices manifestement artificielles (`"<question-factice-1>"`, `"<scenario-factice-1>"`), générées par le test dans `tmp_path`.
- AD-24 : `slmsp.data` ne lit aucun fichier autrement que par `core.artefacts.lire(chemin, "data", racine=...)` (le test AST de `tests/test_architecture.py` l'impose : ni `open`, ni `Path.read_*`, ni `pyarrow.parquet.read_table/ParquetFile`). Le décodage parquet est donc **injecté** : `seed.py` lit les octets avec `lire`, vérifie leur SHA-256 contre `config/sources.toml`, puis passe `(octets, colonnes)` à un `decodeur` ; la vraie implémentation (pyarrow, `ParquetFile(BytesIO).iter_batches`, import paresseux) vit dans `cli/data.py` (couche 5), les tests injectent la leur (pyarrow ou liste Python).
- `slmsp.data` n'importe ni `slmsp.fetch`, `slmsp.evaluation`, `slmsp.mistral` (même couche ou lourd) : le CLI convertit `ConfigSources` en `JeuPublic` et fournit la fabrique de scénarios.
- Le Jeu d'évaluation n'est vu que par `core.items` : `identifiants_proteges(versions, racine=)` et `empreintes_antifuite(versions, n, racine=)`. Versions : `("v1.0", "v1.1")` (obligatoires, absence = `ConfigurationInvalide`) plus `"calibrage"` si `eval/calibrage/echantillon-calibrage.jsonl` existe.
- Les n-grammes des candidats sont calculés avec `config.anti_fuite.n_ngrammes`, la même valeur que celle passée à `empreintes_antifuite` (règle le report du spec 9.1 sur `anti_fuite.n_ngrammes` pour l'usage fait par `seed`) ; le seuil est `config.anti_fuite.seuil_jaccard`.
- Chaque source utilisée passe `RegistreLicences.exiger(depot, "recherche")` avant la création du run : `evaluation_seulement` ⇒ `UsageInterdit`, absente ⇒ `SourceSansLicence`.
- Sélection déterministe : candidats dédoublonnés par texte normalisé, bornés en longueur, triés par SHA-256 de `<tache>.<emplacement>\0<texte normalisé>`, examinés dans cet ordre jusqu'à `volumes[tache] × facteur` amorces conservées (`facteur` = 3 par défaut).

**Never:**
- Aucun appel Mistral par défaut : les scénarios ne sont produits que si `nb_scenarios > 0` (`--scenarios N`, 0 par défaut), et le CLI refuse alors (code 4) si `jeu_gele_et_commite("v1.1")` échoue. Aucun appel d'API dans les tests (fabrique factice).
- Aucun paramètre de `executer_seed` ne désigne un fichier d'amorces : la seule entrée est la table de règles et les jeux de `config/sources.toml` (épinglés par révision et SHA-256).
- Ne pas modifier `core/`, `mistral/`, `evaluation/`, `eval/`, `config/donnees.toml`, `data/registre-licences.toml`, `tests/test_architecture.py`, ni les documents de décision.
- Pas de lecture de xlsx (`sp_questions_corpus`, `assistant_ia_questions_corpus`) : hors périmètre (aucun lecteur xlsx, mise en page inconnue, 56 Mo) ; consigné pour Anaël.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nominal public | jeux factices, registre de fixture admettant les sources, protection vide | run `data-seed` `complet` ; chaque amorce publique porte `jeu` (= dépôt), `revision`, `ligne`, `sha_texte` relus ; `amorces.jsonl` et `comptes.json` | — |
| Source `evaluation_seulement` | une règle vise un dépôt classé ainsi | aucun run créé | `UsageInterdit` |
| Source hors registre | dépôt absent du registre | aucun run créé | `SourceSansLicence` |
| Jeu non téléchargé ou SHA différent | fichier absent de `data/raw/mediatech/<jeu>/<rev>/` ou octets ≠ sha256 de la config | run `partiel-erreur` (ou rien créé si absent avant run) | `ConfigurationInvalide` / `ProvenanceInvalide` |
| Fuite par texte | candidat dont le texte normalisé a le SHA d'une `amorce_usager` | exclu, motif `amorce_usager` | — |
| Fuite par identifiant | `url` du candidat ∈ URL de provenance ; `doc_id`/`chunk_id` ∈ `dataset_ids` ou `resource_ids` | exclu, motifs `provenance_url`, `dataset_id`, `resource_id` | — |
| Fuite par n-grammes | recouvrement `|A∩B| / min(|A|,|B|)` ≥ seuil avec un item de v1.0 ou de v1.1 | exclu, motif `recouvrement_ngrammes` | — |
| Scénarios CR | `nb_scenarios = k`, fabrique factice | k amorces `tache=CR, emplacement=scenario, auteur_contenu=mistral, appel_id`, `sha_texte` du texte renvoyé ; ids dérivés du thème | `BudgetEpuise` ⇒ run `partiel-budget`, amorces déjà écrites conservées |
| Amorce écrite à la main | ligne sans `jeu`/`revision`/`ligne` ni `appel_id`, ou ligne publique dont le texte n'est pas à `ligne` du jeu | `verifier_amorces` refuse | `ProvenanceInvalide` |
| Sans scénario | `nb_scenarios = 0` | aucune amorce Mistral ; aucun appel de la fabrique | — |

</intent-contract>

## Code Map

- `src/slmsp/core/schemas/amorce.py` -- `Amorce` (valide la provenance : public ⇒ `jeu`/`revision`/`ligne`, mistral ⇒ `appel_id`) ; `amorce_id` `^[a-z0-9][a-z0-9._-]*$`. Lecture seule.
- `src/slmsp/mistral/generateur.py:272-295, 378-387` -- relecture d'`amorces.jsonl` par `Generateur` et contrôle d'une amorce Mistral (`message_assistant(reponse_brute)["content"] == texte`, appel `ok`, `usage=generation`). Le CLI s'en sert pour la fabrique de scénarios (`Generateur(seed_run_id, client=...).generer("scenario-reunion", [theme_id], session_id, "CR")`) ; le texte de l'amorce est `message_assistant(generation.reponse_brute)["content"]`.
- `src/slmsp/evaluation/notation.py:109-135` -- modèle pour assembler `ClientMistral(charger_mistral(), RegistreBudget(), fabriquer_sdk(config))` dans le CLI.
- `src/slmsp/evaluation/gel.py:`jeu_gele_et_commite(version, racine)`` -- précondition « pas de génération avant le gel » (CLI seulement ; lève `ManifesteInvalide`, code 4).
- `src/slmsp/core/items.py:128, 792-905` -- `N_DEFAUT`, `EmpreintesAntifuite.par_item` (clé `<version>/<id>` → frozenset d'empreintes), `IdentifiantsProteges` (`amorces_sha256` = SHA-256 de `normaliser(amorce_usager)`, `urls`, `dataset_ids`, `resource_ids`), `empreintes_antifuite`, `identifiants_proteges`. Empreinte d'un n-gramme : `sha256_hex(" ".join(gramme))[:16]` sur `core.texte.ngrammes(texte, n)` ; texte de moins de `n` mots ⇒ empreinte du tuple entier de jetons (reproduire exactement via `core.items._empreintes_texte`, privé : ré-implémenter les 6 lignes avec `core.texte.ngrammes`/`normaliser` et `core.canonique.sha256_hex`).
- `src/slmsp/core/texte.py` -- `normaliser`, `ngrammes`.
- `src/slmsp/core/artefacts.py` -- `lire`, `nouveau_run("data-seed", "seed", config, parents, entrees, racine=...)` (entrées = chemins absolus acceptés), `Run.ajouter_jsonl`, `Run.ecrire` (création exclusive), `Run.terminer(statut, motif)`.
- `src/slmsp/data/{licences,config}.py` -- `RegistreLicences.charger(racine=)`, `.exiger`, `.instantane()`, `.sha256` ; `charger_config_donnees()` (`volumes.par_tache()`, `anti_fuite.n_ngrammes`, `anti_fuite.seuil_jaccard`).
- `src/slmsp/fetch/config.py` (`charger_config_sources`, `JeuSource`, `FichierSource`) et `src/slmsp/fetch/sources.py:dossier_jeu` -- fichiers sous `<racine>/data/raw/mediatech/<nom>/<revision>/<nom du fichier>` (CLI seulement).
- `src/slmsp/cli/index.py` et `cli/train.py` -- modèle d'une sous-commande (`enregistrer(sous_parseurs)`, `--racine`, `func(args) -> int`) ; `cli/__init__.py` déclare déjà `data`.
- `config/sources.toml` -- jeux MediaTech (`service-public` : colonnes `title`, `text`, `related_questions` (JSON : liste d'objets `{sid, url, question}`), `url`, `doc_id`, `chunk_id` ; `data-gouv-datasets-catalog` : `title`, `url`, `doc_id`, `chunk_id`). À compléter par `piaf` (`AgentPublic/piaf`, colonnes `id,title,context,question,answers`).
- `tests/fetch/test_sources.py::test_config_versionnee` -- assertions sur la liste des jeux et la taille totale (663_393_073) ; ajouter `piaf` (650_352 octets).
- `tests/test_architecture.py:88-111` -- lectures interdites dans `data` (dont `pyarrow.parquet.read_table/ParquetFile`) ; couche `data` = 4 (importe `core`, `mistral`, `budget`…, jamais `fetch`/`evaluation`/`indexation`).

## Tasks & Acceptance

**Execution:**
- `config/sources.toml` -- ajouter le jeu `piaf` : `depot = "AgentPublic/piaf"`, `revision = "bda8c063bc7297180796cd835d1974c0bc71c521"`, `licence = "mit"`, fichier `plain_text/train-00000-of-00001.parquet`, `sha256 = "868b00642fd947182dd406becee1f7981c4ab69c2dc78ee5f0e6e7a42d98ebad"`, `taille = 650352` ; mettre à jour le commentaire d'en-tête (jeux d'amorces publics en plus du corpus MediaTech) -- FR-29.
- `tests/fetch/test_sources.py` -- adapter `test_config_versionnee` (3 jeux, fichiers `[1, 3, 1]`, taille totale + 650_352) -- conséquence directe du point précédent.
- `src/slmsp/data/seed.py` -- implémenter : `JeuPublic(nom, depot, revision, fichiers)` ; `RegleAmorce` et la table `REGLES` (service-public `related_questions[].question` → Q/question, 15–300 car. ; data-gouv catalog `title` → RD/demande, 10–200 ; service-public `title` → CR/theme, 10–200 ; service-public `text` → LC/texte 300–1500, CO/texte 150–800, RE/texte 800–4000 ; piaf `question` → generique/demande 10–300) ; `Protection` + `construire_protection(versions, config, racine)` (motifs `amorce_usager`, `provenance_url`, `dataset_id`, `resource_id`, `recouvrement_ngrammes`, index inversé empreinte → items) ; `executer_seed(...)` (parcours : exiger licences et jeux, construire la protection, créer le run, lire et vérifier les fichiers, sélectionner, écrire `amorces.jsonl` en ajout, scénarios, `comptes.json` : par Tâche et emplacement les amorces conservées, la cible, le manque, les exclusions par motif, les emplacements sans source publique ; statut final) ; `verifier_amorces(racine, run_id, jeux, decodeur)` (schéma `Amorce`, `sha_texte`, relecture des lignes publiques, `appel_id` Mistral présent) ; ids : `<tache en minuscules>.<emplacement>.<nom du jeu>.<ligne>[.<k>]`, scénarios `cr.scenario.<suffixe du thème>` -- FR-29, AD-3 verrou 5, FR-24.
- `src/slmsp/cli/data.py` -- `slmsp data {seed, generate, validate, filter, build}` : `seed [--racine DIR] [--facteur N] [--scenarios N]` implémenté (convertit `ConfigSources`, injecte le décodeur pyarrow paresseux, fabrique de scénarios réelle seulement si `--scenarios > 0`, précondition de gel ; codes : 0 complet, 1 erreur/partiel, 3 budget, 4 gel ou provenance) ; les quatre autres répondent « non implémentée » (code 2) -- AD-17.
- `tests/data/test_seed.py` (et `tests/cli/test_data.py` pour le CLI) -- couvrir toute la matrice avec des jeux factices, un registre de fixture, une protection fabriquée à la main plus un test sur les vrais jeux v1.0/v1.1 (`construire_protection` couvre les deux versions) et un test de `verifier_amorces` -- tests sans réseau.

**Acceptance Criteria:**
- Given `slmsp data seed` sur des jeux factices, when il tourne, then `runs/data-seed/<run_id>/` contient `amorces.jsonl` et `comptes.json`, et chaque amorce publique est relue dans `data/raw/`.
- Given `uv run pytest tests/data tests/cli tests/fetch tests/test_architecture.py -q` et `uv run ruff check`, when on les lance, then ils passent.

## Spec Change Log

## Review Triage Log

## Design Notes

Décisions autonomes (D-nuit, « la plus simple et la plus réversible ») : (1) règles dans le code, pas en config ; (2) emplacements sans source publique (CT `type_courrier`, `objet`, `elements_connus` ; RE `longueur_demandee` ; passages de Q ; xlsx) non couverts, listés dans `comptes.json` ; (3) recouvrement mesuré par le coefficient d'inclusion (≥ Jaccard, donc plus prudent) ; (4) pas de `--reprendre` en 9.3 ; (5) `generique/demande` ← questions de PIAF (hors domaine administratif, jeu générique en français inscrit au registre).

## Verification

**Commands:**
- `uv run pytest -q --tb=short tests/data tests/cli tests/fetch tests/test_architecture.py` -- expected: tous passent.
- `uv run ruff check` -- expected: aucune erreur.

### 2026-10-13 — Review pass
- Couche : Blind Hunter seule (mode économe D-nuit-4). verdicts : 11 findings — high 0, medium 0, low 5, false 3, maybe-false 3
- findings:
  - `[false]` `[reject]` Tests absents du contenu relu — le diff soumis était limité à `src/`, `config/` et `tests/fetch` ; `tests/data/test_seed.py` (37 tests) et `tests/cli/test_data.py` (20) existent et passent.
  - `[low]` `[reject]` Run `complet` malgré `manque > 0` — `comptes.json` porte `cible`, `conservees`, `manque` par emplacement et le CLI les affiche ; un statut dédié ajouterait une branche sans consommateur (`generate` lit les comptes).
  - `[low]` `[reject]` Pas de SHA des `items.jsonl` protégés dans la config du run — version et nombre d'items sont consignés ; les jeux sont gelés (MANIFEST) ; coût d'une clé supplémentaire non justifié.
  - `[low]` `[reject]` Gel de v1.1 non vérifié sans `--scenarios` — seule la génération Mistral exige le gel (règle 2) ; `seed` public ne génère rien.
  - `[low]` `[patch]` Docstring de `seed.py` promettant un contrôle d'`appel_id` que `verifier_amorces` ne fait pas — docstring corrigée (le contrôle d'appel est celui du Générateur à l'usage).
  - `[low]` `[reject]` Textes courts à empreinte « tuple entier » — comportement identique à `core.items.empreintes_antifuite`, voulu ; `filter` (9.5) ajoute le cosinus ; la clé `seuil_jaccard` reste lue comme seuil d'inclusion (documenté dans le module).
  - `[low]` `[patch]` Comparaison d'URL en chaîne exacte — `_url_canonique` (sans fragment ni barre finale, minuscules) appliquée aux deux côtés ; test `test_url_comparee_sans_barre_finale_fragment_ni_casse`. Volet « id croisé dataset/resource » rejeté : faux positif négligeable.
  - `[maybe-false]` `[reject]` Mémoire (octets + BytesIO, candidats en mémoire) — mesuré sur le vrai parquet service-public (4 règles, 35 758 lignes) : 13 s, protection en 0,6 s ; l'effet reste modeste (candidat = texte seul). À re-mesurer sur le catalogue data.gouv (460 Mo) à la campagne 9.8.
  - `[low]` `[reject]` Artefacts partiels d'un run en erreur — le statut final est inscrit dans `etat.jsonl` (`partiel-erreur`) ; `generate` doit lire le statut du run (9.4).
  - `[low]` `[patch]` Colonne parquet absente : erreur pyarrow brute — le décodeur du CLI convertit `ArrowException`/`KeyError` en `ConfigurationInvalide` nommant les colonnes.
  - `[false]` `[reject]` `RegistreBudget()` sans `racine` — le registre est un état machine partagé (`SLMSP_VAR_DIR`) par décision de l'architecture ; le passer sous `--racine` le scinderait. Codes de sortie 4 confondus, scénarios non remplacés : choix documentés, bénéfice faible.
  - `[false]` `[reject]` Doublons entre Tâches et entrée `piaf` — dédoublonnage par (Tâche, emplacement) voulu ; `AgentPublic/piaf` figure au registre (MIT, `verifie_le` 2026-10-12).

## Auto Run Result

**Statut :** done (2026-10-13).

**Résumé :** étape `seed` du pipeline de données. `slmsp data seed [--racine DIR] [--facteur N] [--scenarios N]` constitue `runs/data-seed/<run_id>/{amorces.jsonl, comptes.json}` à partir de colonnes de jeux publics épinglés (relus dans `data/raw/`, SHA-256 contrôlé) et, en option, de scénarios de réunion Mistral (`CR/scenario`, `auteur_contenu = mistral`, `appel_id`). Les candidats qui touchent le Jeu d'évaluation (v1.0, v1.1, plus calibrage s'il existe) sont exclus et comptés par motif (`amorce_usager`, `provenance_url`, `dataset_id`, `resource_id`, `recouvrement_ngrammes`). `verifier_amorces` refuse toute amorce sans origine ou non retrouvée sur disque. `generate`, `validate`, `filter` et `build` sont déclarées (« non implémentée », code 2).

**Fichiers :**
- `src/slmsp/data/seed.py` : règles, `Protection`, `executer_seed`, `verifier_amorces`.
- `src/slmsp/cli/data.py` : sous-commandes, décodeur pyarrow (AD-24 : le décodage est injecté, les octets viennent de `core.artefacts.lire`), fabrique de scénarios réelle (seulement avec `--scenarios > 0` et après `jeu_gele_et_commite("v1.1")`).
- `config/sources.toml` : jeu `piaf` (MIT, 650 352 octets, SHA épinglé) ajouté.
- `tests/data/test_seed.py`, `tests/cli/test_data.py` : matrice complète sur jeux factices ; tests sur les vrais jeux v1.0 et v1.1.
- Hors zone stricte : `tests/fetch/test_sources.py::test_config_versionnee` (trois jeux, taille totale + 650 352).

**Revue (une couche, Blind Hunter) :** 11 constats ; 3 correctifs (docstring, normalisation des URL, erreur de colonne parquet), 8 rejetés avec motif au journal ci-dessus ; aucun report. Revue de suivi recommandée : non.

**Report du spec 9.1 (`anti_fuite.n_ngrammes`) :** traité pour l'usage de `seed` : la protection est construite par `empreintes_antifuite(..., n=config.anti_fuite.n_ngrammes)` et les candidats sont hachés avec la même valeur, donc aucune dérive possible dans cette étape. Le report reste à solder en 9.5 (`filter`).

**Vérification :**
- `uv run pytest tests/data tests/cli tests/fetch tests/test_architecture.py` : tous passent.
- `uv run ruff check` et `ruff format --check` : propres.
- `uv run pytest -q --tb=line -p no:warnings` : 3417 passés, 341 ignorés, 1 échec hors zone et préexistant (`tests/evaluation/test_notation.py::test_ouvrir_juges_surcharge_le_mode` : extra `judge`/`anthropic` non installé).
- Fumée locale (hors suite, sans réseau ni API) sur le vrai parquet `service-public` avec un racine temporaire : 13 s ; 300 Q, 240 CR/theme, 240 LC, 105 CO, 105 RE ; 43 exclusions (surtout par URL de provenance).

**Décisions prises seul :**
- Règles (jeu, colonne, Tâche, emplacement, bornes) dans le code, pas en config : Q ← `related_questions` de service-public ; RD ← titres du catalogue data.gouv ; CR/theme ← titres service-public ; LC, CO, RE ← colonne `text` de service-public ; générique ← questions de PIAF.
- Recouvrement mesuré par le coefficient d'inclusion `|A∩B|/min(|A|,|B|)` (≥ Jaccard, donc plus prudent) avec le seuil `anti_fuite.seuil_jaccard`.
- Scénarios Mistral en option (`--scenarios`, 0 par défaut) et refusés (code 4) sans gel commité de v1.1 ; aucun appel dans les tests ni dans ce run.
- Pas de `--reprendre` ; sélection déterministe (tri par SHA), `facteur` 3 ; `RegistreBudget` laissé dans `SLMSP_VAR_DIR`.
- Les deux corpus xlsx (`sp_questions_corpus`, `assistant_ia_questions_corpus`) ne sont pas lus (pas de lecteur xlsx, 56 Mo, colonnes inconnues).

**À confirmer par Anaël :**
- Emplacements sans source publique (listés dans `comptes.json`) : `Q/passages` (à fournir par 9.4 depuis l'Index), `CT/type_courrier`, `CT/objet`, `CT/elements_connus`, `RE/longueur_demandee`. Sans eux, les gabarits CT et RE ne peuvent pas tourner.
- RD ← titres de jeux data.gouv est un choix faible (un titre n'est pas une demande) ; Q ← questions liées de service-public.
- `sp_questions_corpus` s'appelle `gpt_corpus-20kq&A.xlsx` : possible génération par un autre modèle, à vérifier avant tout usage (verrou 5).
- Avant la campagne : `slmsp fetch sources piaf` (650 Ko) ; puis `slmsp data seed`, et, une fois les conditions Mistral relues le jour même, `slmsp data seed --scenarios 80`.
