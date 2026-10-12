---
title: 'Story 5.3 — Évaluation, phase génération, sans réseau'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: 'cb829a4d41e654023420ee67392e1c96d0881d52'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Une panne d'infrastructure en cours de run (llama-server qui tombe) marque chaque item restant en erreur, et une reprise ne les relance jamais.
    evidence: |-
      generer_item capture toute Exception et écrit une ligne statut=erreur ; reprendre_generation saute tout item présent, en erreur compris (choix consigné, et l'intent interdit de relancer un item présent). Il faudrait distinguer les erreurs d'infrastructure (ErreurInference) et finir le run en `interrompu`, ou bien prévoir une option de nouvel essai explicite (story 5.6 ou suivante).
    location: >-
      src/slmsp/evaluation/generation.py generer_item / reprendre_generation
    severity: medium
---

<intent-contract>

## Intent

**Problem:** Le banc n'a pas de phase génération : `slmsp eval run` répond « non implémentée ». Il faut faire produire au Harnais complet (`AssistantService`) la sortie de chaque item du Jeu d'évaluation, contre le Bac à sable MCP et sans réseau, dans un run immuable et reprenable. Ces sorties seront jugées plus tard (story 5.6) sans regénérer (FR-25, FR-40, NFR-8, AD-13).

**Approach:** Trois modules dans `slmsp.evaluation` :
- `modele_ref` résout `base:<slug>` ou `ft:<export_run_id>` × `f16`/`q4_k_m` en GGUF et en `ConfigModele` ;
- `assemblage` monte le Harnais d'évaluation : serveurs `llama-server`, Index, puis, par item, `BacASable` et `ModeFixe`, avec une garde « profil aucun » ;
- `generation` vérifie le manifeste, crée le run `eval-generation`, puis écrit une ligne `Generation` par item, en ajout seul.

La CLI `eval run --phase generation` branche le tout.

## Boundaries & Constraints

**Always:**
- **Zone.** `src/slmsp/evaluation/{generation,assemblage,modele_ref}.py`, `src/slmsp/core/schemas/generation.py`, la sous-commande `run` de `src/slmsp/cli/eval.py`, et `tests/evaluation/{conftest,test_generation,test_modele_ref,test_generation_reel}.py`. Les stories 9.2 et 10.1 tournent en parallèle : ne rien toucher d'autre.
- **Couches (AD-1, `tests/test_architecture.py`).** `evaluation` (couche 4) n'importe ni `fetch`, ni `judge`, ni `cli`. Aucun client HTTP hors `slmsp.net`.
- **Manifeste vérifié avant tout.** Pour un jeu `vN[.M]`, `gel.verifier_manifeste(version, racine)` passe avant la résolution du modèle, le démarrage d'un serveur ou une écriture ; `ManifesteInvalide` donne le code 4. `calibrage` est admis sans manifeste (essai de fumée, `jeu_version = "calibrage"`).
- **Item → requête.** La seule voie est `core.items.vers_requete(item)`, puis `harness.prompts.entree_de_requete`.
  - Appel : `service.repondre(code, [{"role": "user", "content": <contenu>}], {"entree": entree, **OPTIONS_LLM})`.
  - `<contenu>` vaut l'entrée texte, ou le message `user` rendu par `construire_messages(fiche, entree)` pour une entrée objet.
  - Ni `parametres` ni `mode` ne vont au `LlmPort`.
- **Décodage et Modes.**
  - `OPTIONS_LLM = {"temperature": 0.0, "seed": GRAINE, "max_tokens": MAX_TOKENS}` : constantes de `generation.py`, inscrites dans `run.json`.
  - Pour RD seulement, `ModeFixe` est construit selon le mode de l'item : `connecte` et `repli` → `"connecte"` (une cassette `simulation` déclenche le repli) ; `hors-ligne` → `"hors-ligne-force"`.
  - Le `BacASable` est construit sur `resoudre_cassettes(jeu, item)`, avec `signaler` : les avertissements « appel non prévu » entrent dans la trace à leur place.
- **Sortie canonique.** `sortie_canonique = {texte: jetons concaténés, appels_outils: [{nom, arguments}] des AppelOutil (sans id), sources: Source du dernier évènement Sources}`.
  - Aucune durée ni identifiant aléatoire n'y figure.
  - `trace` = évènements en dicts (`vers_dict`), avertissements du Bac à sable inclus, jetons consécutifs fusionnés.
  - `duree_ms` est hors de la sortie canonique.
- **Run.** `nouveau_run("eval-generation", slug, …, racine=racine)` est créé après le démarrage du Harnais et porte les champs suivants :
  - `modele_ref`, `quantification`, `variante_llamacpp`, `llamacpp_tag`, `chat_template_sha256` (SHA-256 du `chat_template` servi par `GET /props`), `jeu_version`, `index_version`, `graine` ;
  - `config` : options LLM, ids des items, description du serveur, `chat_template_force`, `profil_reseau = "aucun"` ;
  - `entrees` : manifeste du jeu, `config/outils-mcp.toml`, `taches.toml`, `harnais.toml`, `modeles/<slug>.toml`.

  Statut final : `complet`, ou `partiel-erreur` si au moins une ligne est en erreur, ou `interrompu` sur une exception hors item (relancée ensuite).
- **GPU.** La variante `cuda` prend `verrou_gpu` pour tout le run, et les serveurs démarrent avec `prendre_verrou_gpu=False`. L'embedding (`bge-m3`) tourne toujours en `cpu`.
- **Sans réseau.** La boucle des items tourne dans `assemblage.sans_reseau()`. Ce gestionnaire remplace `socket.socket.connect`, `connect_ex` et `socket.getaddrinfo` : toute cible hors boucle locale lève `HoteBloque` (« profil aucun »). Les originaux sont restaurés à la sortie.
- **D1.1.** Les doublures `FakeLlm` produisent des mots aléatoires, jamais un texte rédigé.

**Never:**
- Implémenter la phase notation, `--depuis` ou `config/evaluation.toml` (story 5.6) ; écrire sous `eval/` ; modifier `harness/`, `mcp/`, `inference/`, `index/`, `core/` (hors `schemas/generation.py`) ou `pyproject.toml`.
- Réécrire une ligne de `generations.jsonl` ou `run.json` ; relancer un item déjà présent lors d'une reprise.
- Lancer un vrai `llama-server` dans un test non marqué `integration` + `lent`.

## I/O & Edge-Case Matrix

| Scénario | Entrée / état | Résultat attendu | Erreurs |
|---|---|---|---|
| Nominal | jeu gelé intact, 8 items, `FakeLlm` | 8 lignes `Generation` `ok`, `run.json` complet, statut `complet` | — |
| Manifeste altéré | un octet de `items.jsonl` changé | `ManifesteInvalide`, code 4 | aucun run créé, aucun serveur lancé |
| Item en échec | `FakeLlm` lève sur un item | ligne de cet item `statut="erreur"`, évènement `Erreur` en fin de trace ; items suivants traités | statut `partiel-erreur` |
| Erreur avant flux | `repondre` lève (`EntreeInvalide`, `SchemaOutilModifie` du Bac à sable) | `Erreur(code="erreur-evaluation")` dans la trace, run continue | idem |
| Reprise | `--reprendre <id>` après 3 items sur 8 | 5 lignes ajoutées, 3 sautées, même dossier ; `etat.jsonl` : `en_cours` (reprise) puis final | run `complet` → `SlmspError` ; type ≠ `eval-generation` ou modèle différent → `ManifesteInvalide` |
| Réseau | un `ToolPort` tente une connexion vers `192.0.2.1:443` | `HoteBloque` « profil aucun » ; aucune connexion ne part | traité comme une panne MCP (repli) par le Harnais |
| Modes RD | item `hors-ligne` | aucun appel au Bac à sable, `Avertissement` hors ligne | — |
| `base:<slug>` `q4_k_m` | config de `config/modeles/<slug>.toml` | GGUF `<models>/<slug>/gguf/<gguf.fichier>` | GGUF absent → `ConfigurationInvalide` |
| `base:<slug>` `f16` | — | refus (`ConfigurationInvalide` : pas de GGUF F16 de base) | — |
| Template exporté non forcé | `<models>/<slug>/chat_template.jinja` présent, `chat_template_force = false` | `ConfigurationInvalide` (AD-13 : imposer le template du tokenizer) | — |
| `ft:<id>` | run `runs/export/<id>/`, `complet`, `modele_ref = base:<slug>` | `modele-f16.gguf` ou `modele-q4_k_m.gguf` du run, config de `<slug>` avec `chat_template_force = false` | run absent, non complet, ou sans `modele_ref` de base → `ConfigurationInvalide` |
| Phase non générée | `--phase notation` ou `toutes` | message « non implémentée (story 5.6) », code 2 | — |

</intent-contract>

## Code Map

- `src/slmsp/cli/eval.py` -- remplacer le `run` « non implémenté » par un vrai sous-parseur. `sonde-outils` reste non implémentée (8.2). Imports paresseux dans la fonction, comme `executer_gel`.
- `src/slmsp/core/artefacts.py:332` `nouveau_run(type, slug, config, parents, entrees, graine, *, racine, **champs)` ; `:404` `ouvrir_run` ; `:425` `reprendre(run_id, fichier=, cle=, racine=)` (inscrit `en_cours`, refuse un run `complet`) ; `Run.ajouter_jsonl/lire_jsonl/terminer/statut_courant`. Lecture seule.
- `src/slmsp/core/schemas/run.py` -- `RunManifest` : champs `modele_ref` (motif `ModeleRef`), `quantification`, `variante_llamacpp`, `llamacpp_tag`, `chat_template_sha256`, `jeu_version`, `index_version`, `couverture` ; `MOTIF_RUN_ID`.
- `src/slmsp/evaluation/gel.py:492` `verifier_manifeste(version, racine)` (code 4) ; `config.chemin_manifeste`.
- `src/slmsp/core/items.py` -- `lire_jeu(version, racine)`, `Jeu.items`, `resoudre_cassettes(jeu, item)`, `vers_requete(item)`, `ItemRD.mode` ∈ {`connecte`, `hors-ligne`, `repli`}, `VERSION_CALIBRAGE`.
- `src/slmsp/harness/service.py:110` `AssistantService(llm, embedder, vector_store, outils, mode, config, *, taches)` ; `repondre` lève tout de suite les erreurs de l'appelant et, sinon, renvoie un flux terminé par `Fin` ou `Erreur`. `harness/prompts.py:246,301` : `construire_messages`, `entree_de_requete`. `harness/modes.py:53` `ModeFixe`. `harness/config.py` `charger_config_harnais`, `harness/taches` `charger_taches().tache(code)`.
- `src/slmsp/mcp/bac_a_sable.py:80` `BacASable(cassettes, *, signaler=)` ; il accepte aussi les cassettes héritées du calibrage.
- `src/slmsp/inference/serveur.py:336` `ServeurLlama(config, variante, *, slug, gguf, prendre_verrou_gpu)`, avec `.client()`, `.embedder()`, `.port`, `.description()` et `charger_config_modele(slug)`. `charger_config_llamacpp().tag`. `inference/client.py:33` : `OPTIONS_AUTORISEES` (une option inconnue lève `ValueError`).
- `src/slmsp/index/lecture.py:313` `ouvrir_index(racine)` est un gestionnaire de contexte, avec `.version`.
- `src/slmsp/net/__init__.py` `client_local(port)` (lecture de `/props`) ; `core/erreurs.py` : `HoteBloque`, `ConfigurationInvalide`, `ManifesteInvalide`, `CodeSortie` ; `core/var.py:156` `verrou_gpu(commande=…)` ; `core/config.py` `dossier_modeles()`, `racine_projet()`.
- `src/slmsp/core/evenements.py` : `Source`, `vers_dict`, `depuis_dict` et les types d'évènements.
- `tests/harness/factices.py` : `FakeLlm`, `FakeEmbedder`, `FakeVectorStore`, `passage`, `mots`. Les charger dans `tests/evaluation/conftest.py` comme `tests/harness/conftest.py` (nom `harness_factices`). `tests/conftest.py` : la garde réseau des tests et le `SLMSP_VAR_DIR` temporaire sont autouse.
- `tests/harness/test_integration_question.py` : `prerequis`, `racine_index` et le modèle du test réel (marqueurs `lent` + `integration`).
- Données : `eval/calibrage/` (16 items, cassettes héritées `R-001`, `R-002`) et `eval/jeu/v1.0/` gelé (225 items, `MANIFEST.json` qui liste `items.jsonl`, `eval/cassettes/RD-*/s1.json` et `eval/grille-juge-v1.md`). Les tests les copient dans `tmp_path` et ne les modifient jamais en place.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/schemas/generation.py` -- Modèles :
  - `AppelCanonique(nom, arguments)` et `SortieCanonique(texte, appels_outils, sources: list[Source])` (`SousSchema`) ;
  - `Generation(SchemaBase)` : `schema_version = 1`, `item_id`, `tache` (code), `statut` ∈ {`ok`, `erreur`}, `sortie_canonique`, `trace: list[dict]` (chaque dict est validé par `depuis_dict`), `duree_ms ≥ 0`.
- `src/slmsp/evaluation/modele_ref.py` -- `ModeleResolu` (dataclass figée : `ref`, `genre`, `quantification`, `slug`, `slug_run`, `config`, `gguf`) et `resoudre(ref, quantification, *, racine=None)`.
  - Le motif de `ref` est celui de `ModeleRef` ; `quantification` ∈ {`f16`, `q4_k_m`}.
  - Règles de la matrice ; un modèle d'embedding est refusé.
  - `slug_run` vaut `<slug>` pour `base`, `ft-<slug>` pour `ft`.
- `src/slmsp/evaluation/assemblage.py` -- Contenu :
  - `MODES_RD`, `SLUG_EMBEDDING = "bge-m3"`, `PROFIL_RESEAU = "aucun"` ;
  - `HarnaisEvaluation` (llm, embedder, vector_store, config harnais, table des Tâches, `description: dict`, `chat_template_sha256`, `index_version`, `llamacpp_tag`) et sa méthode `service(item, jeu, signaler)`, qui rend un `AssistantService` frais (`BacASable` et `ModeFixe` pour RD seulement) ;
  - `ouvrir_harnais(modele, variante, racine)`, gestionnaire de contexte réel : serveurs de génération et d'embedding, Index, SHA du template par `/props` ;
  - `sans_reseau()`.
- `src/slmsp/evaluation/generation.py` -- Contenu :
  - constantes `TYPE_RUN`, `FICHIER_GENERATIONS`, `GRAINE`, `MAX_TOKENS`, `OPTIONS_LLM` ;
  - `generer_item(harnais, jeu, item) -> Generation` ;
  - `lancer_generation(modele_ref, quantification, jeu, *, variante="cpu", items=None, racine=None, fabrique=ouvrir_harnais, rapporter=None) -> RapportGeneration` ;
  - `reprendre_generation(run_id, *, racine=None, fabrique=ouvrir_harnais, rapporter=None)`. La reprise relit `run.json` (modèle, quantification, variante, jeu, items), revérifie le manifeste et refuse un `chat_template_sha256` différent.
  - `RapportGeneration` porte `run`, les comptes `ok`/`erreur`/`sautes`, `statut` et `durees_ms`.
  - Un id d'`--items` inconnu lève `ValueError`.
- `src/slmsp/cli/eval.py` -- `eval run --modele --quantification {f16,q4_k_m} --jeu [--variante cpu|cuda] [--phase generation|notation|toutes] [--items ID,ID…] [--reprendre RUN_ID] [--racine DIR]`.
  - `--phase` vaut `toutes` par défaut ; `notation` et `toutes` sont refusées (code 2) tant que la story 5.6 n'est pas faite.
  - Sans `--reprendre`, `--modele`, `--quantification` et `--jeu` sont requis ; avec `--reprendre`, ils sont facultatifs mais doivent égaler ceux du run.
  - Une ligne de progression par item ; à la fin : chemin du run, statut, durée moyenne par item.
  - Code de sortie : 0 si `complet`, 1 si `partiel-erreur`, 2 pour une `ValueError` d'usage.
- `tests/evaluation/conftest.py` -- Contenu :
  - chargement de `harness_factices` ;
  - `FakeLlmDeterministe` : mots aléatoires semés par le SHA des `(role, content)`. Pour RD avec `tools` et sans message `tool`, un `AppelOutil` `search_datasets` à requête aléatoire ;
  - fabrique de `HarnaisEvaluation` factice (`FakeEmbedder`, `FakeVectorStore` avec passages factices, `chat_template_sha256` fixe) ;
  - copie de `eval/` (jeu v1.0, cassettes, grille, calibrage) dans `tmp_path`.
- `tests/evaluation/test_generation.py` -- Un test par ligne de la matrice (sauf les lignes `modele_ref`) et par critère ci-dessous, via `lancer_generation` et via `slmsp.cli.main` (code 4, code 2, reprise).
- `tests/evaluation/test_modele_ref.py` -- Lignes `modele_ref` de la matrice, avec `SLMSP_MODELS_DIR` dans `tmp_path`, des GGUF factices (octets quelconques) et un run d'export factice créé par `nouveau_run("export", …, modele_ref="base:<slug>")`.
- `tests/evaluation/test_generation_reel.py` -- Test `lent` + `integration` : `base:granite-4.0-1b` `q4_k_m` `cpu` sur 8 items (un par Tâche) du jeu v1.0 ; `run.json` et 8 lignes valides. Sauté si un prérequis manque (mêmes règles que `test_integration_question.prerequis`).

**Acceptance Criteria:**
- Given un jeu gelé, when on lance `slmsp eval run --phase generation`, then le manifeste est revérifié avant tout (code 4 en cas d'écart).
- Given un `ModeleRef`, when le run démarre, then `runs/eval-generation/<run_id>/run.json` porte `modele_ref`, `quantification`, `variante_llamacpp`, `jeu_version`, `index_version` et `chat_template_sha256`. Un template HF exporté sans `chat_template_force` est refusé.
- Given chaque item, when il est traité, then une ligne `Generation` est ajoutée (`item_id`, `sortie_canonique`, trace), sans durée dans `sortie_canonique`.
- Given une évaluation en cours, when un composant tente une connexion hors boucle locale, then elle est refusée (`HoteBloque`, profil aucun). Un test d'un run complet (`FakeLlm`, Bac à sable réel) relève zéro tentative de connexion sortante.
- Given la variante `cuda`, when le run démarre, then `gpu.lock` est détenu pendant la génération et `variante_llamacpp = "cuda"`.
- Given un `FakeLlm` déterministe, when on lance deux fois la phase génération, then les `json_canonique(sortie_canonique)` sont identiques octet pour octet.
- Given `uv run pytest` et `uv run ruff check`, when on les lance, then tout passe, test d'architecture compris, hors échecs préexistants listés.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 15 findings — high 0, medium 2, low 10, false 3, maybe-false 0
- findings:
  - `low` `patch` La docstring de `sans_reseau` promettait plus que les trois points d'entrée remplacés (gethostbyname, sendto UDP, ConnectEx Proactor, processus enfants) — docstring du module `assemblage` restreinte à ce qui est réellement couvert ; le périmètre des remplacements est celui de l'intent.
  - `medium` `defer` Une panne d'infrastructure en cours de run fige les items restants en erreur, et la reprise ne peut pas les relancer — l'intent interdit de relancer un item présent ; consigné dans `deferred`.
  - `low` `reject` La reprise d'un run `partiel-erreur` déjà entièrement traité relance les serveurs pour rien — cas rare, sans perte de données ; la correction ajoute une branche de garde.
  - `medium` `patch` La reprise ne comparait que le SHA du template, pas `index_version` ni `llamacpp_tag` : un run repris pouvait mélanger deux Index — la reprise refuse désormais aussi un `index_version` ou un `llamacpp_tag` différent, avec un test (`test_reprise_refusee`).
  - `low` `reject` `entrees` n'inscrit pas `llamacpp.toml`, `bge-m3.toml`, les cassettes ni le GGUF — la liste des `entrees` est fixée par l'intent ; `llamacpp_tag` et `description` du serveur sont déjà dans `run.json`.
  - `low` `reject` `connexions_bloquees` n'est pas persisté — un `HoteBloque` levé dans un port apparaît déjà dans la trace de l'item (repli, avertissement) ; le persister ajouterait un champ public.
  - `false` `reject` Les espions réseau des tests, installés sous la garde, ne verraient jamais les appels bloqués — c'est voulu : l'espion observe ce qui atteint la couche socket réelle, et un appel non local qui passerait la garde ferait échouer l'assertion.
  - `false` `reject` `_contenu` suppose le message `user` à l'indice 1 — `construire_messages` a pour contrat de rendre `[system, user]` (docstring de `harness/prompts.py:254`).
  - `low` `reject` `--phase toutes` par défaut échoue toujours — choix explicite et consigné de la spec ; le changer reviendrait à modifier la spec.
  - `low` `patch` Le résumé de reprise mélangeait les comptes de la session et le statut du run — libellés « Statut du run » et « cette session » dans la CLI, tests ajustés.
  - `low` `reject` Le schéma `Generation` ne vérifie pas ses invariants croisés et redéfinit `CodeTache` — `generer_item` est la seule source des lignes ; un validateur croisé ajouterait de la complexité sans défaut observé.
  - `low` `reject` Les choix `--quantification` et `--variante` sont recopiés dans la CLI — les importer casserait la convention d'imports paresseux de `cli/` ; `resoudre` revalide de toute façon.
  - `false` `reject` Codes de sortie incomplets et vérification de `variante` avant le manifeste — le contrôle de `variante` n'a aucun effet de bord (ni serveur, ni écriture), et `ConfigurationInvalide` et `RessourceOccupee` suivent le code générique de `slmsp.cli.main`.
  - `low` `reject` La troncature à `MAX_TOKENS` n'est pas exposée hors de la trace — la `raison` de `Fin` reste dans la trace, lisible par la notation (5.6).
  - `low` `reject` Tests manquants (IPv6, KeyboardInterrupt, reprise `partiel-erreur`, `ft:` de bout en bout) et test réel limité à Windows — le projet est Windows natif ; ajouter ces tests sort du mode économe sans défaut identifié.

## Design Notes

**Pourquoi `/props` pour le SHA du template.** Le paquet `gguf` n'est pas installé, et le lecteur GGUF de `fetch.verifications` est interdit à `evaluation` (même couche). La décision « imposer le template du tokenizer » est déjà portée par `chat_template_force`, fixé par la story 8.1 après comparaison des SHA. Le banc enregistre donc le template **réellement servi**. Il refuse aussi l'état incohérent où 8.1 a exporté le template HF (ils diffèrent) sans le forcer.

**Garde `sans_reseau`.** Aucun port du Harnais d'évaluation n'ouvre de client réseau : `BacASable`, `ModeFixe`, et `llama-server` en boucle locale. La garde rend le profil `aucun` effectif pour le processus entier, y compris pour une bibliothèque tierce.

**Choix pris seul (à consigner dans l'Auto Run Result) :**
- `calibrage` admis sans manifeste ;
- `base` × `f16` refusé ;
- contrat `ft` sur `runs/export/<id>/modele-<q>.gguf` avec `modele_ref = base:<slug>` dans le `run.json` de l'export ;
- `GRAINE = 42` et `MAX_TOKENS = 1024`, constantes en attendant `config/evaluation.toml` (story 5.6) ;
- `--phase` vaut `toutes` par défaut et est refusée en 5.3 ;
- run créé après le démarrage des serveurs ;
- une reprise saute aussi les items en erreur ;
- dossier `runs/eval-generation/` (AD-13), et non `runs/eval/`.

## Verification

**Commands:**
- `uv run pytest tests/evaluation tests/test_architecture.py -q` -- expected: tout passe (test réel désélectionné)
- `uv run pytest -q` et `uv run ruff check` puis `uv run ruff format --check src/slmsp/evaluation src/slmsp/cli/eval.py src/slmsp/core/schemas/generation.py tests/evaluation` -- expected: propre, hors échecs préexistants listés
- `$env:SLMSP_VENDOR_DIR='<principal>\vendor'; $env:SLMSP_MODELS_DIR='<principal>\models'; uv run slmsp eval run --modele base:granite-4.0-1b --quantification q4_k_m --jeu v1.0 --phase generation --items Q-001,RD-001,CR-001,LC-001,CO-001,RE-001,CT-001,NR-001 --racine <principal>` -- expected: run `complet` sous `<principal>\runs\eval-generation\`, 8 lignes (lancé par l'orchestrateur de la story, en arrière-plan)

## Auto Run Result

Statut : done.

**Changement.** Phase génération du banc : `slmsp eval run --phase generation` vérifie le manifeste du jeu, résout le `ModeleRef`, monte le Harnais d'évaluation (llama-server de génération + bge-m3 en CPU, Index, Bac à sable et `ModeFixe` par item RD), crée le run `eval-generation` et écrit une ligne `Generation` par item sous la garde `sans_reseau` ; reprise en ajout seul.

**Fichiers.**
- `src/slmsp/core/schemas/generation.py` : schémas `AppelCanonique`, `SortieCanonique`, `Generation`.
- `src/slmsp/evaluation/modele_ref.py` : résolution `base:`/`ft:` × `f16`/`q4_k_m` en GGUF et `ConfigModele`.
- `src/slmsp/evaluation/assemblage.py` : `HarnaisEvaluation`, `ouvrir_harnais` (SHA du template par `/props`), `sans_reseau`.
- `src/slmsp/evaluation/generation.py` : `generer_item`, `lancer_generation`, `reprendre_generation`, `RapportGeneration`.
- `src/slmsp/cli/eval.py` : sous-commande `eval run`.
- `tests/evaluation/{conftest,test_generation,test_modele_ref,test_generation_reel}.py` : tests de la matrice, test réel `lent` + `integration`.

**Revue (une couche, Blind Hunter, mode économe).** 15 constats : 3 corrigés (reprise refusée si `index_version` ou `llamacpp_tag` diffère, medium ; docstring de `sans_reseau` restreinte, low ; libellés du résumé CLI, low), 1 différé (panne d'infrastructure figée en erreur, medium), 11 rejetés avec motif dans le Review Triage Log. Revue de suivi recommandée : `false` (un seul medium corrigé, aucun high).

**Vérifications.**
- `uv run pytest tests/evaluation tests/test_architecture.py tests/cli -q` : 210 passed, 1 deselected.
- `uv run pytest -q` : 2516 passed, 169 skipped, 26 deselected ; `uv run ruff check` et `ruff format --check` propres.
- Run réel (Granite 1B q4_k_m, CPU, 8 items du jeu v1.0, un par Tâche) : `runs/eval-generation/20261012-155024-granite-4.0-1b-0cdc` du dépôt principal, statut `complet`, 8 `ok`, 2 min 41 s au total. Durée moyenne 19,6 s par item (médiane ~8,7 s ; CR-001 à 90,7 s, NR-001 à 1,4 s). Extrapolation à 225 items : environ 1 h 15 en CPU.

**Décisions prises seul.**
- Reprise de la story après coupure : l'implémentation déjà écrite par le sous-agent précédent a été prise comme sortie de l'étape d'implémentation. Aucun nouveau sous-agent d'implémentation n'a été lancé (mode économe), et les correctifs de revue ont été appliqués directement.
- Le choix des décisions listées dans les Design Notes reste inchangé.
- La reprise compare aussi `index_version` et `llamacpp_tag` (correctif de revue).

**Risques résiduels.** Une panne de llama-server en cours de run fige les items restants en erreur sans relance possible (différé). `sans_reseau` ne couvre que `connect`, `connect_ex` et `getaddrinfo`. `_bmad/custom/bmad-build-auto.toml` reste non suivi dans le worktree : c'est la surcharge de l'orchestrateur, hors zone, et elle n'est pas commitée.
