---
title: 'Story 9.1 — Registre des licences et configuration des données'
type: 'feature'
created: '2026-10-12'
status: done
baseline_revision: '88221ad493e8fa7b7c505c5241b000a3c43e49b2'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-9-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      anti_fuite.n_ngrammes est modifiable alors que les empreintes du Jeu d'évaluation sont calculées avec N_DEFAUT.
    evidence: |-
      maybe-false : dépend de la façon dont l'étape filter (story ultérieure) consommera la clé ; si elle compare des n-grammes de taille configurée à des empreintes calculées avec N_DEFAUT, la détection de fuite est faussée en silence.
    location: >-
      src/slmsp/data/config.py:118
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** Le pipeline de données (AD-17) n'a ni Registre des licences ni configuration validée : aucune source n'est tracée (FR-31), le verrou 5 d'AD-3 (`auteur_contenu`, `genere_par`) n'existe pas, et le Générateur de la 9.2 attend `config/donnees.toml [mistral]` qui n'existe pas encore.

**Approach:** Versionner `data/registre-licences.toml` (licences relevées ce jour sur les fiches HF par le profil `outillage`) et `config/donnees.toml`, chargés et validés par `slmsp.data.licences.RegistreLicences` et `slmsp.data.config.charger_config_donnees`, avec erreurs métier explicites.

## Boundaries & Constraints

**Always:**
- Zone de fichiers : `data/registre-licences.toml`, `src/slmsp/data/{licences,config}.py`, `config/donnees.toml`, `tests/data/test_licences.py`, `tests/data/test_config_donnees.py`, et le fichier de spec.
- Le registre est lu par `slmsp.core.artefacts.lire(chemin, "data", racine=...)` (AD-24 : aucun `open`/`read_*`/`json.load` dans `slmsp.data`), puis `tomllib.loads`.
- `config/donnees.toml` est lu par `slmsp.core.config.charger_toml` (AD-22 ; modèles `ModeleConfig`, `extra="forbid"`).
- `config/donnees.toml [mistral]` reste compatible avec `slmsp.mistral.generateur.charger_prealables` : `conditions_verifiees_le` (date TOML, ou chaîne vide tant que D1.2 n'est pas vérifiée) et `modeles_stables` (liste non vide).
- `conditions_verifiees_le = ""` dans le fichier livré : le Générateur doit refuser (`PrealableNonSatisfait`).
- Tests sans réseau, fixtures dans `tmp_path`, aucune donnée d'entraînement réaliste.

**Never:**
- Inventer une date de vérification des conditions Mistral, ou une licence non lue sur la fiche.
- Modifier `core/artefacts.py`, `core/erreurs.py`, `mistral/`, `evaluation/`, `train/`, `pyproject.toml`, ni les documents de décision.
- Rendre configurable la liste des auteurs ou générateurs admis (verrou D1.1, pas un réglage).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Registre réel | `data/registre-licences.toml` du dépôt | charge, ids uniques, toutes les sources de la story présentes | — |
| Auteur interdit | entrée `auteur_contenu = "claude"` ou `"inconnu"` (ou autre hors {public, mistral, anael}) | refus au chargement | `ProvenanceInvalide` |
| Distillation | `genere_par` hors liste admise (ex. `gpt-4o`, `claude`, `inconnu`) ou incohérent avec `auteur_contenu` | refus au chargement | `ProvenanceInvalide` |
| Source absente | `exiger("x/inconnu", ...)` | — | `SourceSansLicence` |
| Usage | `exiger(id, "diffusable")` sur `recherche` ; `exiger(id, *)` sur `evaluation_seulement` | refus | `UsageInterdit` (sous-classe de `SourceSansLicence`) |
| Registre malformé | TOML invalide, clé inconnue, id en double, usage hors liste | refus | `ConfigurationInvalide` |
| Config réelle | `config/donnees.toml` | volumes Q 100, RD 140, CR 80, LC 80, CO 35, RE 35, CT 35, generique 90 ; `conditions_verifiees_le` None | — |
| Traduction | clé de volume hors des 8 Tâches (ex. `TR`) | refus | `ConfigurationInvalide` |
| Part générique | `generique / total` hors [0,10 ; 0,20] (D4) | refus | `ConfigurationInvalide` |
| Prérequis 9.2 | fichier livré passé à `charger_prealables` | refus de démarrer ; avec une date du jour en fixture : accepté | `PrealableNonSatisfait` |

</intent-contract>

## Code Map

- `src/slmsp/mistral/generateur.py:85-147` -- contrat lu : `_MistralDonnees(extra="ignore")`, `conditions_verifiees_le: date`, `modeles_stables: list[str]` (min 1) ; `""` ou absence ⇒ `PrealableNonSatisfait`. Lecture seule.
- `config/mistral.toml` -- `modeles_autorises = ["mistral-large-latest", "mistral-large-2411", "mistral-large-2512"]` : reprendre la même liste dans `modeles_stables`.
- `config/reseau.toml:43-48` -- URL des conditions : `https://legal.mistral.ai/terms/commercial-terms-of-service` (GET, profil `outillage`).
- `src/slmsp/core/artefacts.py` (`lire`, `chemin_autorise`) -- lecteur `data` autorise `data/registre-licences.toml` mais pas `config/donnees.toml` (d'où `charger_toml` pour ce dernier).
- `src/slmsp/core/config.py` (`ModeleConfig`, `charger_toml`, `racine_projet`) -- chargement TOML strict, messages sans valeur saisie.
- `src/slmsp/core/erreurs.py` -- `SourceSansLicence`, `ProvenanceInvalide`, `ConfigurationInvalide` existent.
- `src/slmsp/core/schemas/amorce.py` -- `AuteurContenu = Literal["public","mistral","anael"]` : réutiliser.
- `src/slmsp/core/items.py:117` -- `N_DEFAUT = 5` (n-grammes anti-fuite) : même valeur par défaut en config.
- `src/slmsp/core/canonique.py` -- `json_canonique`, `sha256_hex` pour l'instantané du registre.
- `tests/test_architecture.py` -- AST AD-24 sur `slmsp/data` ; couche `data` = 4 (peut importer `core`).
- `src/slmsp/data/__init__.py` -- paquet vide existant.

## Tasks & Acceptance

**Execution:**
- `data/registre-licences.toml` -- créer (`schema_version = 1`, `[[sources]]`) avec les entrées et valeurs de la table des Design Notes -- FR-31, AC3.
- `src/slmsp/data/licences.py` -- `SourceLicence` (pydantic strict), `RegistreLicences.charger(chemin=None, *, racine=None)`, `.source(id)`, `.exiger(id, variante)`, `.ids`, `.instantane()` (dict JSON trié) et `.sha256` (octets lus), `UsageInterdit(SourceSansLicence)`, constantes `USAGES`, `VARIANTES`, `GENERE_PAR_ADMIS` -- verrou 5, AC1, AC2.
- `config/donnees.toml` -- créer : `schema_version = 1`, `[mistral]` (`conditions_verifiees_le = ""`, `methode_verification`, `conditions_url`, `conditions_sha256 = ""`, `modeles_stables`), `[volumes]`, `[deduplication]` (`n_ngrammes = 5`, `seuil_jaccard = 0.8`), `[anti_fuite]` (`n_ngrammes = 5`, `seuil_jaccard = 0.5`, `seuil_cosinus = 0.9`), `[relecture]` (`taille_echantillon = 30`, `graine = 42`), chaque clé commentée -- AC4, D1.2.
- `src/slmsp/data/config.py` -- `ConfigDonnees` et sous-modèles (`ModeleConfig`), `charger_config_donnees(chemin=None)` ; `""` ⇒ `None` pour la date et le SHA ; SHA = 64 hex ou vide ; seuils dans ]0, 1] ; volumes ≥ 0 ; part générique dans [0,10 ; 0,20] ; propriété `total` -- AC4.
- `tests/data/test_licences.py`, `tests/data/test_config_donnees.py` -- couvrir la matrice I/O, le registre et la config réels, et la compatibilité `charger_prealables`.

**Acceptance Criteria:**
- Given le registre réel, when on le charge, then chaque jeu AgentPublic porte `licence`, `verifie_le = 2026-10-12` et la `revision` lue ; `MCQ-eval` et `french_simplified` sont `evaluation_seulement`, Claire French Dialogue est `recherche`.
- Given `uv run pytest` et `uv run ruff check`, when on les lance, then ils passent (test AST AD-24 compris).

## Design Notes

Relevé du 2026-10-12 (API `huggingface.co/api/datasets`, profil `outillage`) :

| id | licence | usage | auteur / genere_par | revision |
|---|---|---|---|---|
| AgentPublic/service-public | etalab-2.0 (attribution) | diffusable | public / humain | 7ddda096b33d48dbda8143fc8c349a8b0e031a3a |
| AgentPublic/data-gouv-datasets-catalog | etalab-2.0 (attribution) | diffusable | public / humain | 11f3d3c9481ad478dbcff52e85d73b7fd10533ce |
| AgentPublic/sp_questions_corpus | mit | diffusable | public / humain | 495a22cf7b572621a85d2f3e97783b2f4189c47e |
| AgentPublic/assistant_ia_questions_corpus | mit (fiche : « generated and improved using non-expert knowledge », mode non précisé) | diffusable | public / humain | 62cef57af7cc5fe54862a8118c221246771ad9ea |
| AgentPublic/retriever_dataset | non déclarée (pas de fiche) | recherche (prudence) | public / humain | aab978b2db590116dadd108f337bfbda036887e1 |
| AgentPublic/piaf | mit (crowdsourced) | diffusable | public / humain | bda8c063bc7297180796cd835d1974c0bc71c521 |
| AgentPublic/MCQ-eval | etalab-2.0 | evaluation_seulement | public / humain | d104aa4fef453abe9716e8866c68778a0804198c |
| esoria3/french_simplified | non déclarée (source : alector_corpus) | evaluation_seulement | public / humain | baebde461d0fd28baba32671a9af16826c55ccee |
| OpenLLM-France/Claire-Dialogue-French-0.1 | cc-by-nc-sa-4.0 | recherche | public / humain | 2d003b86aff5b622533ecfea29ada554f3e6db03 |
| mistral/reponses-generateur | conditions commerciales Mistral | diffusable | mistral / mistral | — (`verifie_le` absent : date portée par `donnees.toml`) |
| data.gouv/reponses-outils-mcp | etalab-2.0 (métadonnées data.gouv) | diffusable | public / api-publique | — (`verifie_le` absent) |

`GENERE_PAR_ADMIS = {"humain": {"public", "anael"}, "mistral": {"mistral"}, "api-publique": {"public"}}`. `auteur_contenu` et `genere_par` sont vérifiés sur le TOML brut avant pydantic, pour lever `ProvenanceInvalide` et non `ConfigurationInvalide`. `verifie_le` et `revision` sont facultatifs ; `notes` facultatif. Licences incertaines (`retriever_dataset`, `french_simplified`, nature de `assistant_ia_questions_corpus`, réponses d'outils) : à consigner dans `## Auto Run Result` pour Anaël.

## Verification

**Commands:**
- `uv run pytest tests/data -q` -- expected: tous les tests passent.
- `uv run pytest -q` -- expected: aucun échec nouveau.
- `uv run ruff check` -- expected: aucune erreur.

## Review Triage Log

### 2026-10-13 — Review pass
- Couches : Blind Hunter seule (mode économe D-nuit-4) ; edge-case-hunter et verification-gap sautées.
- verdicts: 20 findings — high 0, medium 1, low 12, false 4, maybe-false 3
- findings:
  - `[medium]` `[patch]` Date de vérification Mistral admise sans SHA de la page relue (et l'inverse) — `MistralDonnees._date_et_sha_ensemble` exige les deux ou aucun ; commentaires de `config/donnees.toml` et fixtures mis à jour, tests `test_date_sans_sha_refusee` et `test_sha_sans_date_refuse`.
  - `[low]` `[reject]` Deux parseurs de `[mistral]` (`data.config` et `mistral.generateur`) — dérive possible, mais le contrat est imposé par la spec et l'intention interdit de modifier `mistral/` ; le test `charger_prealables` sur le fichier livré garde la compatibilité.
  - `[low]` `[reject]` Typage non strict : date en chaîne ou `true` pour un seuil acceptés — une chaîne ISO acceptée a le même sens qu'une date TOML (aucune issue fausse) et un booléen pour un seuil est improbable ; ajouter `Strict` changerait aussi l'acceptation des entiers.
  - `[low]` `[reject]` Pas de contrôle licence ↔ usage — le classement `usage` est un relevé humain fixé par la spec ; une liste de licences connues ajoute une surface que l'intention ne demande pas.
  - `[maybe-false]` `[reject]` `data.gouv/reponses-outils-mcp` en `diffusable` alors que la licence de chaque jeu reste à confirmer — valeur fixée par les Design Notes, la corriger reviendrait à modifier la spec ; consignée pour Anaël. Pour trancher : licence de chaque jeu interrogé par les outils.
  - `[maybe-false]` `[reject]` `assistant_ia_questions_corpus` en `humain / diffusable` malgré une génération non précisée — valeur fixée par les Design Notes ; consignée pour Anaël. Pour trancher : documentation du producteur sur le mode de génération.
  - `[false]` `[reject]` `mistral/reponses-generateur` diffusable sans lien avec la vérification — aucune donnée de cette source ne peut exister tant que `charger_prealables` refuse (date vide ⇒ `PrealableNonSatisfait`).
  - `[false]` `[reject]` `mistral-large-latest` dans `modeles_stables` — liste imposée par la spec (identique à `config/mistral.toml` ; D1 : générateur `mistral-large-latest`).
  - `[maybe-false]` `[defer]` `anti_fuite.n_ngrammes` modifiable alors que les empreintes du Jeu sont calculées avec `N_DEFAUT` — dépend de la façon dont l'étape `filter` (story ultérieure) consommera la clé ; medium si avéré.
  - `[low]` `[reject]` `revision` en texte libre (`"main"` accepté) — le champ reste générique pour des sources non HF ; toutes les entrées réelles portent un commit de 40 hex.
  - `[low]` `[reject]` Aucun champ d'attribution (producteur, URL) — l'id `org/nom` et la licence identifient le producteur ; l'attribution relève de la publication, hors de cette story, et demanderait de nouveaux champs.
  - `[low]` `[reject]` Le verrou 5 ne s'applique qu'au chargement TOML, pas à `SourceLicence` construit directement — aucun appelant ne construit le registre hors de `charger` ; garde sur un état non démontré.
  - `[low]` `[patch]` Docstring « jamais la valeur saisie » contredite par l'id cité dans les messages — docstring corrigée (clés fautives et id de la source, jamais les autres valeurs). Volet AD-24 réfuté : le lecteur `data` n'autorise pas `config/`, d'où `charger_toml`, comme le prévoit la spec.
  - `[low]` `[patch]` `test_chaque_cle_est_commentee` ignore les clés contenant un chiffre et lit `lignes[-1]` à l'indice 0 — regex `^[A-Za-z_][A-Za-z0-9_]* = ` et garde `indice > 0`.
  - `[low]` `[reject]` Pas de test pour `sources` non liste — le cas lève `ConfigurationInvalide` par le schéma (`_verifier_provenance` n'est appelé que sur une liste) ; la matrice I/O est couverte.
  - `[low]` `[reject]` Pas de test chaîne/booléen pour la date et les seuils — suit le rejet du typage non strict ci-dessus.
  - `[low]` `[reject]` Bornes de `seuil_jaccard` non testées — même type `Seuil` que `seuil_cosinus`, déjà testé aux bornes.
  - `[false]` `[reject]` `n_ngrammes` flottant ou booléen non testé en `[anti_fuite]` — `StrictInt` les refuse ; type partagé avec `[deduplication]`.
  - `[low]` `[patch]` `test_sources_immuables` attrape `Exception` nu — attrape `pydantic.ValidationError`, `noqa` retiré.
  - `[false]` `[reject]` Tests 9.2 ignorés par `importorskip("mistralai")` — `mistralai` est installé : les trois tests ont tourné (0 ignoré dans `tests/data`).

## Auto Run Result

**Statut :** done (2026-10-13).

**Résumé :** Registre des licences versionné (`data/registre-licences.toml`, 11 sources relevées le 2026-10-12) et configuration du pipeline de données (`config/donnees.toml`), chargés et validés par `slmsp.data.licences.RegistreLicences` (verrou 5 d'AD-3 : `ProvenanceInvalide`, `SourceSansLicence`, `UsageInterdit`) et `slmsp.data.config.charger_config_donnees`. Brouillon du 2026-10-12 (`3c7cd63`) repris après fusion de `nuit/2026-10-12`, vérifié, puis revu.

**Fichiers :**
- `data/registre-licences.toml` : 11 sources (licence, usage, provenance, révision).
- `config/donnees.toml` : préalables Mistral (vides), volumes, déduplication, anti-fuite, relecture ; chaque clé commentée.
- `src/slmsp/data/licences.py` : `SourceLicence`, `RegistreLicences` (`charger`, `source`, `exiger`, `ids`, `instantane`, `sha256`), `UsageInterdit`.
- `src/slmsp/data/config.py` : `ConfigDonnees` et sous-modèles, `charger_config_donnees`.
- `tests/data/test_licences.py`, `tests/data/test_config_donnees.py` : matrice I/O, fichiers réels, compatibilité `charger_prealables`.

**Revue (une couche, Blind Hunter) :** 20 constats. 4 correctifs (1 medium : date et SHA Mistral exigés ensemble ; 3 low : docstring, regex du test des commentaires, `ValidationError`). 1 reporté (`anti_fuite.n_ngrammes`). 15 rejetés, motifs au journal de tri ci-dessus.

**Revue de suivi recommandée :** non. Correctifs par verdict : medium 1, low 3, high 0.

**Vérification :**
- `uv run pytest tests/data -q` : 108 passés, 0 ignoré.
- `uv run ruff check` : aucune erreur.
- `uv run pytest -q` : 3285 passés, 341 ignorés, 2 échecs hors zone et préexistants : `tests/eval_outils/test_jeu_v1.py::test_v1_1_export_des_changements` (export `eval/revue/changements-v1.0-v1.1.jsonl` non versionné, jeu v1.1 en attente de relecture) et `tests/evaluation/test_notation.py::test_ouvrir_juges_surcharge_le_mode` (extra `judge`, paquet `anthropic`, non installé dans ce worktree).

**Décisions prises seul :**
- Reprise d'une spec `in-progress` : `baseline_revision` conservé à `88221ad` (début de la story) ; le diff de revue est restreint aux fichiers de la zone, que la fusion de `nuit/2026-10-12` ne touche pas.
- `exiger(id, variante)` lève `ValueError` pour une variante hors `VARIANTES`.
- `verifie_le` doit être une date TOML ; `revision` et `notes` non vides s'ils sont présents.
- Volumes tous nuls refusés (part générique indéfinie).
- `conditions_verifiees_le` et `conditions_sha256` renseignés ensemble ou vides ensemble.

**Licences incertaines, à confirmer par Anaël avant toute diffusion :**
- `AgentPublic/retriever_dataset` : aucune fiche ni licence déclarée ; classé `recherche` par prudence.
- `esoria3/french_simplified` : aucune licence déclarée (source alector_corpus) ; `evaluation_seulement`.
- `AgentPublic/assistant_ia_questions_corpus` : MIT, mais la fiche dit « generated and improved using non-expert knowledge » sans préciser le mode ; inscrit `public / humain`. Si un modèle non autorisé l'a produit, le verrou 5 impose de le retirer.
- `data.gouv/reponses-outils-mcp` : Licence Ouverte 2.0 pour les métadonnées data.gouv ; la licence de chaque jeu interrogé (ODbL possible) reste à confirmer.

**Risques résiduels :** la campagne 9.8 doit relire la page des conditions Mistral le jour même et renseigner date et SHA ; `anti_fuite.n_ngrammes` doit rester égal à `N_DEFAUT` tant que l'étape `filter` ne recalcule pas les empreintes avec la valeur configurée.
