---
title: "Story 9.6 — Étape `build` : re-dérivation, jeu versionné et verrous AD-3"
type: 'feature'
created: '2026-10-16'
status: review
baseline_revision: 'e937971'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-9-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-5-etapes-validate-et-filter.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** après `filter`, aucune étape ne produisait le jeu d'entraînement ni la preuve qu'il vient des seules réponses Mistral journalisées (D1.1, AD-3 verrou 4).

**Approach:** `slmsp data build --depuis <filter_run> --variante diffusable|recherche` refabrique chaque ligne de `retenus.jsonl` depuis le journal Mistral (`usage = generation`), les amorces vérifiées (SHA) et les cassettes, compare les octets à écrire à une nouvelle re-dérivation, puis écrit `data/train/vN/{train.jsonl, MANIFEST.json}` et un run `data-build` immuable.

## Boundaries & Constraints

**Always:**
- D1.1 : aucun texte n'est rédigé ; tout vient du journal, des amorces (`sha_texte` revérifié, texte Mistral égal à la réponse journalisée) et des cassettes. Fixtures : jetons aléatoires.
- `extraction.py` est la seule voie texte brut → texte d'entraînement ; `VERSION_EXTRACTEUR` figure dans chaque ligne et le MANIFEST.
- Une version `vN` n'est jamais réécrite (N = plus grand N existant + 1) ; échec de re-dérivation = rien sous `data/train/`.
- Lectures par `core.artefacts` (AD-24) ; un parent `filter` partiel rend le build partiel (`statut_herite`).

**Never:** appel d'API, import de `judge`/`anthropic`, dépendance à `transformers` (le rendu 10.2 n'est pas utilisé : `messages` + `tools` sont stockés bruts, le chat template s'applique à l'entraînement).

## I/O & Edge-Case Matrix

| Scénario | Comportement |
|---|---|
| Ligne altérée d'un octet, ligne en trop ou manquante | `ProvenanceInvalide`, run `partiel-erreur`, aucun `vN` |
| `appel_id` absent du journal, d'usage `validation`/`juge-second`, statut ≠ `ok` | `ProvenanceInvalide` |
| Amorce dont le SHA ou le texte Mistral diffère du journal | `ProvenanceInvalide` |
| Résultat d'outil RD absent des cassettes de la session | `ProvenanceInvalide` |
| `diffusable` et source `recherche` ; source absente du Registre | `UsageInterdit` / `SourceSansLicence`, avant tout run |
| Run d'un autre type (dont `eval-*`), en cours, ou sans retenu | `ManifesteInvalide` |

</intent-contract>

## Code Map

- `src/slmsp/data/extraction.py` : `extraire_message`, `extraire_contenu`, `VERSION_EXTRACTEUR`.
- `src/slmsp/data/build.py` : `rederiver_ligne`, `serialiser`, `verifier_octets`, `lancer_build`.
- `src/slmsp/core/schemas/entrainement.py` : `LigneEntrainement`, `MetaLigne`, `ManifesteJeuEntrainement`.
- `src/slmsp/cli/data.py` : sous-commande `build` (`--depuis`, `--variante`, `--racine`).
- Tests : `tests/data/test_extraction.py`, `test_build.py`, `test_verrous_ad3.py` ; `tests/cli/test_data.py` ajusté.

## Design Notes

- **Mise en forme** : `messages[0]` = prompt système de la Tâche (`harness.prompts.construire_messages`, passages du plan formatés pour Q). Q/RD : entrée texte de l'amorce ; RD : tours `assistant` journalisés + `tool` (contenu vérifié contre les cassettes) ; CR : transcription (1er appel) puis compte rendu (2e) ; LC/RE/CT : amorces par emplacement, réponse Mistral ; CO : texte fautif Mistral en entrée, texte public de l'amorce en cible ; `generique` : sans prompt de Tâche (`messages[0]` = user).
- **Octet par octet** : `verifier_octets` re-dérive chaque ligne du journal et compare le JSON canonique aux octets qui vont être écrits ; l'écriture est ensuite contrôlée par SHA.
- **Sources** (`meta.source`/`licence`) : dépôts des amorces publiques, `mistral/reponses-generateur` toujours, `data.gouv/reponses-outils-mcp` si cassettes. `diffusable`/`recherche` appliqués par `RegistreLicences.exiger`.
- **MANIFEST** : SHA de `train.jsonl`, comptes par Tâche, rejets amont par motif (validate + filter), instantané du registre, SHA des gabarits, prompts de Tâche et `outils-mcp.toml`, conditions Mistral (date, URL, SHA de `donnees.toml`), modèles générateurs, statut, `build_run_id`.
- **Échantillon (AC 5)** : `echantillon-relecture.jsonl` dans le run (tirage `random.Random(relecture.graine)`, `relecture.taille_echantillon` lignes complètes), non bloquant.

## Verification

- `uv run pytest -q --tb=short tests/data/test_extraction.py tests/data/test_build.py tests/data/test_verrous_ad3.py tests/cli/test_data.py` : verts.
- Suite complète : 3710 verts, 2 échecs préexistants (`test_concurrence`, `test_ouvrir_juges_surcharge_le_mode`) ; ruff et format propres.

## Auto Run Result

**Statut :** done, en revue.

**Décisions prises seul** (« la plus simple et la plus réversible ») :
1. Re-dérivation unique (`rederiver_ligne`) appelée deux fois : à la fabrication, puis par `verifier_octets` sur les octets sérialisés. Le test « exemple altéré » altère `serialiser` ; il n'existe pas de texte d'exemple stocké avant `build` à comparer autrement.
2. CO : l'entrée est la sortie fautive de Mistral, la cible le texte public de l'amorce (SHA vérifié), pas une réponse Mistral.
3. `generique` n'a pas de prompt de Tâche : `messages[0]` est le message `user`.
4. `meta.source`/`licence` sont des listes (plusieurs sources par ligne) ; `meta.version_gabarit` est un dict gabarit → version ; `meta.date` est le jour du dernier appel journalisé ; `generateur` joint les modèles résolus par « + ».
5. Texte d'une amorce Mistral comparé strictement (sans `strip`) à la réponse journalisée.
6. `tools` stocké au format OpenAI (`config/outils-mcp.toml`) pour RD seulement ; les `arguments` des `tool_calls` restent la chaîne JSON journalisée.
7. Build vide (aucun retenu) : `ManifesteInvalide` avant tout run.

**À confirmer par Anaël :**
- Les passages de l'Index (Q) n'ont pas de source au Registre des licences : seule l'amorce question est tracée.
- CO : cible = texte public de l'amorce (et non la réponse Mistral).
- `generique` sans prompt système.
- Le jeu stocke `messages`/`tools` bruts ; le rendu par chat template (10.2) et le protocole d'outils par Modèle restent à l'entraînement.

**Reports (hors périmètre) :**
- Aucun test de la voie réelle de la CLI (journal de production, registre réel). Commande de la campagne (9.8) : `uv run slmsp data build --depuis <filter_run_id> --variante diffusable`.
- 10.x doit revérifier `run_id` (run `data-build`) et les `appel_ids` contre le journal.

## Revue

Revue Opus (2026-10-16), après rebase sur main (story 10.4 incluse) ; second avis Haiku vérifié point par point. D1 : aucun contenu d'entraînement, exemple ni amorce rédigé par Claude dans le diff (lignes refabriquées du journal Mistral et des amorces vérifiées ; tests en jetons artificiels).

- HIGH, corrigé : le MANIFEST écrit par `build` (`build_run_id`, sans `type_run`) était refusé par `train.chargement` (10.4). Contrat unique `EnteteManifesteJeu` (`version`, `type_run = "data-build"`, `run_id` au motif des runs) dans `core/schemas/entrainement.py`, étendu par `ManifesteJeuEntrainement` et utilisé par `charger_jeu` ; `*_run_id` parents typés ; test d'intégration `test_jeu_construit_lu_par_train_run` (`lancer_build` puis `charger_jeu`).
- MEDIUM, corrigé : les six verrous AD-3 sautaient sans l'extra `data`. Verrous 1, 2, 5 (Registre) et 6 (gabarits) séparés dans `test_verrous_ad3.py`, sans `mistralai` (vérifié avec `mistralai` bloqué : 20 verts) ; verrous qui exigent le générateur dans `test_verrous_ad3_pipeline.py`, sautés avec un motif explicite sans l'extra.
- LOW, corrigé : `test_co_garde_les_valeurs_de_la_source` instable (déjà sur main, story 9.5) : `factice()` tirait un hex pouvant contenir « 4821 », lu comme valeur notable, d'où `infidele`. Jetons factices sans chiffre (`tests/data/conftest.py`), contrôle inchangé ; 10 lancements verts.
- LOW, rejeté : verrou 3 ne testerait que la signature ; `test_verrou_3_message_assistant_non_prouve_refuse` couvre déjà le refus d'un message `assistant` non prouvé et d'un texte libre, sans appel sortant.
- LOW, consigné : pas de contrôle anti-fuite de contenu `data/train` contre `eval/` dans 9.6 (hors AC) ; à porter par la story de décontamination ou par 9.8 avant la campagne.
- INFO, consigné : `preferences.jsonl` (paires ORPO) attendu de la story 9.7 ; `charger_jeu` garde son format provisoire.
- Environnement : `test_ouvrir_juges_surcharge_le_mode` échoue faute de `anthropic` après `uv sync --extra data` (extra `judge` retiré), sans lien avec la story.

**Décisions à confirmer par Anaël** (reprises de l'Auto Run Result) : CO avec la sortie fautive de Mistral en entrée et le texte public de l'amorce en cible ; `generique` sans prompt système ; passages de l'Index (Q) sans source au Registre des licences.
