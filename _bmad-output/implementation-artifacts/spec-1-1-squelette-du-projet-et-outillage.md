---
title: 'Story 1.1 — Squelette du projet et outillage'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: 'bd1ad853716d87db72c4b359c2f47bc9f0422e92'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      La règle AST « lecture-data/train » (AD-24) ne voit que open, .read_text, .read_bytes, .open et json.load littéral.
    evidence: |-
      import json as j; j.load(f), numpy.load(chemin), pyarrow.parquet.read_table(chemin), duckdb.read_*,
      datasets.load_dataset(data_files=...) passent. data et train sont vides aujourd'hui. À trancher avec
      core.artefacts (story 1.3) et les pipelines 9.x : faut-il interdire ces lecteurs ou les faire passer par lire() ?
    location: >-
      tests/test_architecture.py (règle lecture-data/train)
    severity: medium (unverified)
  - summary: >-
      Le SDK mcp embarque ses propres transports httpx (mcp.client.streamable_http) utilisables sans slmsp.net.client.
    evidence: |-
      mcp est dans le socle ; TID251 bannit httpx mais pas les sous-modules client du SDK. AD-4 impose d'injecter
      http_client= ; à vérifier et verrouiller par les stories 1.4 et 3.3.
    location: >-
      pyproject.toml [tool.ruff.lint.flake8-tidy-imports.banned-api]
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** le dépôt est greenfield : aucun paquet installable, aucun outillage, et les garde-fous d'architecture (couches, imports interdits, réseau dans les tests, `.gitignore` d'AD-21) ne reposent que sur la discipline des agents.

**Approach:** poser un projet `uv` / Python 3.12 (paquet `slmsp`, layout `src/`), sa CLI argparse à registre de sous-commandes, la configuration ruff (`TID251`) et pytest (marqueurs, garde réseau), un test d'architecture AST auto-testé et un `.gitignore` conforme à AD-21 — exactement les critères 1 à 10 de la story 1.1 de `epics.md`.

## Boundaries & Constraints

**Always:**
- Python `==3.12.*` via `uv` uniquement ; versions du tableau Stack du spine ; `uv.lock` versionné.
- torch seulement via l'index PyTorch CUDA `explicit = true` (cu130, roue `torch-2.14.1+cu130-cp312-win_amd64` vérifiée le 2026-10-12), relié par `[tool.uv.sources]` ; aucune dépendance lourde d'AD-2 dans le socle runtime.
- Couches d'AD-1 : core(0) < net, budget(1a) < inference, index, mcp, mistral(1b) < harness, judge(2) < fetch, indexation, evaluation, benchmarks, measure, data, train, compare(3) < cli, app(4).
- Le test AST lit les sources par `ast.parse`, sans importer les modules.
- Les tests ne font aucun accès réseau hors boucle locale ; `SLMSP_VAR_DIR` pointe sur un dossier temporaire.

**Never:**
- Ne pas installer les extras (pas de `uv sync --all-extras`, pas de téléchargement de torch) : seul `uv lock` doit les résoudre.
- Ne pas modifier `eval/`, les documents de décision, ni des fichiers hors de la zone 1.1.
- Pas de module `cli/<commande>.py` réel (ils appartiennent aux stories suivantes) ; pas de `core/erreurs.py` (story 1.2).
- Aucune donnée d'entraînement, même factice réaliste.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Aide | `slmsp --help` | liste les 12 sous-commandes, code 0 | — |
| Sans sous-commande | `slmsp` | aide sur stderr, code 2 | — |
| Module absent | `slmsp fetch modeles` sans `cli/fetch.py` | « commande non implémentée : fetch » sur stderr, code 2 | — |
| Module présent | `slmsp.cli.compare` exposant `enregistrer` | sous-parseur réel enregistré, son `func(args)` appelé, son code renvoyé | — |
| Dépendance d'un module CLI manquante | `cli/<c>.py` lève `ModuleNotFoundError` sur une autre bibliothèque | message « indisponible » citant le module manquant, code 1 ; `--help` reste fonctionnel | pas de trace |
| Connexion distante en test | `socket.connect(("93.184.216.34", 80))` | échec immédiat (`RuntimeError` explicite) | sauf test marqué `reseau` |
| Connexion locale en test | `127.0.0.1`, `::1`, `localhost` | autorisée | — |

</intent-contract>

## Code Map

- `.gitignore` -- existant ; contient `runs/` et `checkpoints/` en bloc à retirer, `var/` à garder. Attention : un motif `index/` non ancré ignorerait `src/slmsp/index/` → l'ancrer (`/index/`).
- `.env.example` -- existant ; garde les trois clés vides, ajoute `# SLMSP_VAR_DIR=` ; les lignes `BUDGET_*_EUR` sont retirées (les plafonds vivent dans `config/budgets.toml`, AD-5/AD-22, story 1.5).
- `eval/calibrage/build_calibrage.py` -- lecture seule ; importe `urllib.request` (l. 813, 843) → exclu de `TID251` (et du format s'il n'y est pas conforme). `eval/outils/` (story 7.1) idem pour `TID251`.
- `_bmad/`, `_bmad-output/`, `.claude/` -- hors code projet : exclus de ruff.
- Spine : AD-1, AD-2, AD-3 (verrou 1), AD-4 (bannissements), AD-21, AD-22, AD-24, AD-28, tableau Stack ; journal : D-nuit-A1-1, A1-15, A1-17, A1-25, A2-6.

## Tasks & Acceptance

**Execution:**
- `pyproject.toml` -- projet `slmsp`, build `uv_build`, script `slmsp = "slmsp.cli:main"`, socle (numpy 2.5.4, pydantic 2.14.1, jsonschema 4.26.0, psutil 7.2.2, nvidia-ml-py 13.615.71, python-dotenv 1.2.4, mcp 2.3.0), extras `fetch`/`data`/`judge`/`bench`/`train`/`app` d'AD-2, groupe `dev` (pytest 9.1.1, ruff 0.17.0), index `pytorch-cu130` explicite + source torch, `[tool.uv] environments` limité à Windows, ruff (`TID251`, per-file-ignores, exclusions), pytest (marqueurs, `addopts`).
- `.python-version`, `uv.lock` -- `3.12` ; lock généré par `uv lock`.
- `.gitignore`, `.env.example` -- selon le Code Map.
- `src/slmsp/__init__.py`, `src/slmsp/__main__.py`, les 18 `src/slmsp/<paquet>/__init__.py` vides -- squelette.
- `src/slmsp/cli/__init__.py` -- `CodeSortie` (IntEnum 0..5), `SOUS_COMMANDES`, `construire_parseur()`, `main(argv=None) -> int` (reconfigure stdout/stderr en UTF-8, charge `slmsp.cli.<nom>` par `importlib` et appelle `enregistrer(sous_parseurs)`, sinon parseur de remplacement « non implémentée »).
- `tests/conftest.py` -- fixtures automatiques : garde réseau (`socket.socket.connect`/`connect_ex`, `sock_connect` des boucles asyncio) sauf marqueur `reseau` ; `SLMSP_VAR_DIR` temporaire.
- `tests/test_architecture.py` -- analyseur AST `analyser(racine_src) -> list[Violation]` + test sur `src/slmsp` + test paramétré sur modules synthétiques (une violation par règle) + arbre synthétique propre.
- `tests/test_cli.py`, `tests/test_gitignore.py`, `tests/test_garde_reseau.py` -- critères 1, 2, 10 ; 8 ; 5.

**Acceptance Criteria:**
- Given un poste Windows avec uv 0.12.x, when `uv sync --python 3.12` puis `uv run slmsp --help`, then l'environnement est créé sans extras et l'aide liste `fetch`, `index`, `ask`, `mcp`, `eval`, `bench`, `measure`, `data`, `train`, `export`, `compare`, `budget`.
- Given `pyproject.toml`, when on le lit et lance `uv lock`, then `requires-python = "==3.12.*"`, le socle et les extras sont ceux d'AD-2 aux versions Stack, torch vient de l'index CUDA explicite, et le lock réussit.
- Given la config ruff, when `uv run ruff check` et `uv run ruff format --check`, then le dépôt passe et `TID251` signale `anthropic` hors `judge/`, `mistralai` hors `mistral/`, `httpx`/`httpx2`/`requests`/`urllib.request` hors `net/`, et les fonctions d'upload `huggingface_hub` partout.
- Given `uv run pytest`, when il s'exécute, then les marqueurs `reseau`, `gpu`, `lent` sont déclarés et exclus par défaut, et tous les tests passent.
- Given le test d'architecture, when il analyse `src/slmsp` et chaque arbre synthétique fautif, then il ne trouve aucune violation dans le vrai code et détecte chaque règle (couche, lourd-runtime, anthropic, judge-depuis-data/train, client-http, lecture-data/train, publication) dans son arbre synthétique.
- Given `.gitignore`, when `git check-ignore --no-index` sur les chemins du critère 8, then les chemins à ignorer le sont, les autres non, et `src/slmsp/index/__init__.py` n'est pas ignoré.
- Given `.env.example`, when on le lit, then il contient `MISTRAL_API_KEY=`, `ANTHROPIC_API_KEY=`, `HF_TOKEN=` sans valeur et `SLMSP_VAR_DIR` en commentaire.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 47 findings — high 0, medium 9, low 25, false 8, maybe-false 5
- findings:
  - `[low]` `[patch]` (intent) AC1 vérifié en processus, ni script `slmsp` ni `-m slmsp` testés — même cause que la ligne VG-1 ; tests subprocess `-m slmsp --help` et entry point ajoutés.
  - `[medium]` `[patch]` (intent) AC3 non testé (requires-python, extras, index explicite) — `tests/test_pyproject.py` ajouté ; la consignation du choix cu130 passe par l'Auto Run Result et le compte rendu (consignes : l'orchestrateur reporte au journal).
  - `[low]` `[patch]` (intent) Décisions `conflicts` fetch/train et `environments` win32 non consignées — consignées dans `## Auto Run Result`.
  - `[medium]` `[patch]` (intent) per-file-ignores TID251 en bloc, `tests/**` et `eval/outils/**` sans bannissement — ignores `tests/{judge,mistral,net}/**` retirés ; `eval/outils/**` exigé par l'AC4.
  - `[low]` `[patch]` (intent) Motifs `.gitignore` ancrés au lieu des chaînes littérales d'AD-21 — ancrage de `/index/` nécessaire (sinon `src/slmsp/index/` ignoré) ; `var/` remis non ancré (consigne de l'orchestrateur).
  - `[low]` `[patch]` (intent) Suppression des lignes `BUDGET_*_EUR` de `.env.example` sans fichier de remplacement — commentaire rappelant D1.6 et la story 1.5.
  - `[false]` `[reject]` (intent) Numérotation 0..6 des couches au lieu de 1a/1b — même ordre, mêmes interdits ; aucune règle ne change.
  - `[false]` `[reject]` (intent) `slmsp <cmd> --help` d'une commande non implémentée répond « non implémentée » code 2 — conforme à l'AC2.
  - `[false]` `[reject]` (intent) Correspondance `SlmspError` → code laissée à 1.2 — prévu par epics.md (story 1.2, critère 4).
  - `[false]` `[reject]` (intent) `tests/test_garde_reseau.py` hors liste — la table des zones donne « `tests/` racine » à 1.1.
  - `[medium]` `[patch]` (VG-1) Point d'entrée console et `__main__` jamais exécutés — `test_point_d_entree_module` (subprocess) et test `console_scripts` ajoutés.
  - `[medium]` `[patch]` (VG-2) Aucun test sur le socle runtime ni l'index CUDA — `tests/test_pyproject.py`.
  - `[medium]` `[patch]` (VG-3) Tests du registre CLI qui se sautent quand les vrais modules arrivent — réécrits avec des commandes synthétiques (`zz_*`) injectées dans `SOUS_COMMANDES`.
  - `[low]` `[patch]` (VG-4) `/data/cache/` non testé — ajouté à `IGNORES` avec d'autres motifs.
  - `[maybe-false]` `[defer]` (VG-autre) Règle AD-24 limitée (`json` aliasé, lecteurs prenant un chemin : numpy, pyarrow, duckdb, datasets) — voir `deferred`.
  - `[medium]` `[patch]` (blind) Seul `ModuleNotFoundError` est rattrapé ; `ImportError`/`OSError` (DLL) laissent passer une trace — capturés, « indisponible » code 1, test DLL ajouté.
  - `[low]` `[patch]` (blind) La dernière assertion `--help` du test de dépendance manquante ne prouve rien — module `zz_explosive` et contrôle `sys.modules`.
  - `[low]` `[patch]` (blind) `__main__.py` sans garde `if __name__` — garde ajoutée.
  - `[medium]` `[patch]` (blind) Garde réseau : DNS sortant avant connect — `socket.getaddrinfo` gardé, test `example.invalid` ; UDP `sendto` et sous-processus : low rejeté (rare, demande de nouvelles branches).
  - `[maybe-false]` `[reject]` (blind) Secrets et cache HF non neutralisés dans les tests — aucun code ne lit de secret ; story 1.2 lit `.env` par chemin via `dotenv_values`, vider l'environnement n'y changerait rien ; si vrai, low seulement.
  - `[low]` `[patch]` (blind) `PUBLICATION` incomplet (Unsloth `push_to_hub_merged/gguf`, `create_repo`) et entrées TID251 sur méthodes d'instance inopérantes — noms ajoutés, entrées inopérantes supprimées, `huggingface_hub.create_repo` banni.
  - `[low]` `[patch]` (blind) Clients HTTP manquants (`http.client`, `urllib3`, `aiohttp`) — ajoutés à l'AST et à TID251 ; `import urllib` puis `urllib.request.urlopen` : low rejeté (rare, résolution d'attributs à ajouter).
  - `[maybe-false]` `[defer]` (blind) Transports httpx propres au SDK `mcp` utilisables sans `slmsp.net.client` — à régler par 1.4/3.3 (injection `http_client=`), voir `deferred`.
  - `[maybe-false]` `[defer]` (blind) Règle AD-24 : lecteurs prenant un chemin et écritures — même racine que VG-autre ; les écritures signalées sont conformes au critère 6 (`open` interdit).
  - `[low]` `[reject]` (blind) `LOURDS` recopié à la main, sans recoupement avec `pyproject` — la liste d'AD-2 fait autorité ; un recoupement complet ajoute une table nom d'import → distribution et casserait `app` (pywebview) ; `test_pyproject` couvre le socle.
  - `[low]` `[patch]` (blind) `tests/**` et `eval/outils/**` non couverts — même racine que la ligne intent 4 ; ignores `tests/*` retirés.
  - `[low]` `[patch]` (blind) Fichiers lourds de `runs/` traçables — `*.pt`, `*.pth`, `*.ckpt` ajoutés ; versionner les sorties légères de runs est la décision d'AD-21/A1-25 ; `outputs/` et `wandb/` non ancrés : cosmétique.
  - `[low]` `[patch]` (blind) `test_gitignore` incomplet — `IGNORES` et `VERSIONNES` complétés (dont un rapport et `src/slmsp/{data,train,budget}`).
  - `[low]` `[patch]` (blind) `.env.example` renvoie à un `config/budgets.toml` absent — commentaire précisé.
  - `[low]` `[reject]` (blind) `test_var_dir_temporaire` faible, test pytester non marqué `lent` — le run prend environ 1 s ; la fixture est par test par construction (`mktemp`).
  - `[medium]` `[patch]` (edge) `ImportError`/`OSError` non rattrapés — même racine que blind « ModuleNotFoundError ».
  - `[low]` `[reject]` (edge) Module sans `enregistrer` → `AttributeError` — erreur de développeur qui échoue bruyamment, comportement acceptable.
  - `[low]` `[patch]` (edge) `func` renvoyant `None` → `TypeError` — `None` vaut `SUCCES`, test ajouté.
  - `[low]` `[reject]` (edge) `slmsp --inconnu compare x` n'affiche pas l'option fautive — usage rare, correctif = nouvelle branche.
  - `[low]` `[patch]` (edge) `reconfigure` remet `errors` de stderr à `strict` — `errors` conservé, test étendu.
  - `[medium]` `[patch]` (edge) DNS et UDP hors garde — même racine que blind « garde réseau ».
  - `[low]` `[reject]` (edge) Accès réseau depuis des fixtures de session ou à la collecte — aucun tel fixture ; installer la garde en `pytest_configure` complique la levée par marqueur.
  - `[low]` `[reject]` (edge) Imports dynamiques (`importlib.import_module("torch")`) non vus par l'AST — rare, contournement délibéré, détection partielle seulement.
  - `[maybe-false]` `[defer]` (edge) Lectures AD-24 par alias ou lecteurs de bibliothèques — même racine que VG-autre.
  - `[low]` `[patch]` (edge) Clients HTTP manquants — même racine que blind.
  - `[low]` `[patch]` (edge) Publication par `create_repo` et autres — même racine que blind ; `getattr` dynamique et `**kwargs` rejetés (rares).
  - `[low]` `[patch]` (edge) BOM UTF-8 casse `ast.parse` — lecture en `utf-8-sig`.
  - `[low]` `[patch]` (edge) Test d'aide sensible à `COLUMNS` — `COLUMNS=120` fixé.
  - `[false]` `[reject]` (edge) Sous-commande en sous-paquet `cli/<nom>/` fait échouer les tests — tests réécrits sur commandes synthétiques ; le test des 12 vraies commandes vérifie aussi `cli/<nom>/__init__.py`.
  - `[false]` `[reject]` (edge) `data/train/**/*.jsonl` (val, test) — AD-21 ne liste que `train.jsonl` ; les autres fichiers sont petits et versionnables selon AD-21.
  - `[false]` `[reject]` (edge) Suppression de `runs/` et `checkpoints/` en bloc — exigée par l'AC8 et D-nuit-A1-25 ; poids courants ajoutés à part.
  - `[false]` `[reject]` (edge) TID251 « partout » contourné par les per-file-ignores — même racine que la ligne intent 4, déjà corrigée ; le reste est l'exclusion `eval/outils/**` imposée par l'AC4.

## Design Notes

- **Per-file-ignores et précision.** ruff ignore `TID251` en bloc par fichier : sur `src/slmsp/judge/**` il ne distingue plus `anthropic` d'`httpx`. La matrice exacte (anthropic hors judge, mistralai hors mistral, clients HTTP hors net) est donc vérifiée par le test AST ; ruff fournit le retour immédiat dans l'éditeur.
- **`push_to_hub`** est une méthode d'instance : ruff ne peut pas la résoudre. Le test AST ajoute une règle « publication » : tout attribut `.push_to_hub` ou `.upload_file`/`.upload_folder`/`.upload_large_folder`/`.create_commit` et tout import de ces noms depuis `huggingface_hub` échouent ; l'argument nommé `push_to_hub=False` reste permis (AD-4).
- **Fermeture runtime** : graphe d'import interne calculé à partir de tous les modules de core, net, budget, inference, index, mcp, harness, app ; les imports locaux (dans une fonction) comptent.
- **Lock limité à Windows** (`environments = ["sys_platform == 'win32'"]`) : le projet ne vise que Windows (D2) ; cela évite de résoudre torch CUDA et bitsandbytes pour Linux/macOS. Réversible.
- **Tests miroir** : `--import-mode=importlib` pour que `tests/<paquet>/` n'ait pas besoin de `__init__.py` ni ne collisionne.

## Verification

**Commands:**
- `uv lock` -- expected: succès, `uv.lock` écrit.
- `uv sync --python 3.12` -- expected: socle + groupe dev, aucun extra.
- `uv run slmsp --help` -- expected: 12 sous-commandes listées.
- `uv run ruff check` et `uv run ruff format --check` -- expected: aucun écart.
- `uv run pytest` -- expected: tout passe.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** Squelette `uv` / Python 3.12 du paquet `slmsp` :
- CLI argparse à registre paresseux : 12 sous-commandes déclarées, « non implémentée » code 2, « indisponible » code 1, `CodeSortie` nommés, sortie UTF-8 ;
- ruff `TID251` ;
- pytest : marqueurs exclus par défaut, garde réseau (connect, connect_ex, sock_connect, getaddrinfo), `SLMSP_VAR_DIR` temporaire ;
- test d'architecture AST auto-testé (8 règles), `.gitignore` d'AD-21, `.env.example`.

**Fichiers.**
- `pyproject.toml`, `uv.lock`, `.python-version` : projet, socle, extras d'AD-2, index `pytorch-cu130` explicite, ruff, pytest.
- `.gitignore`, `.env.example` : AD-21 (`/index/` ancré, `var/` gardé) ; trois clés vides, `SLMSP_VAR_DIR` en commentaire.
- `src/slmsp/__init__.py`, `__main__.py`, 18 `<paquet>/__init__.py` vides, `cli/__init__.py` : squelette et CLI.
- `tests/conftest.py`, `test_architecture.py`, `test_cli.py`, `test_gitignore.py`, `test_garde_reseau.py`, `test_pyproject.py` : critères 1 à 10.

**Revue.** Une passe, 47 constats.
- Correctifs : 9 entrées medium et 20 low, regroupées par cause (voir Review Triage Log).
- Reportés (`deferred`) : 2, sur la règle AD-24 étendue aux lecteurs de bibliothèques et sur les transports du SDK mcp.
- Rejetés : 8 faux et 8 low, avec leur raison dans le journal de tri. Le constat maybe-false sur les secrets dans les tests est rejeté : s'il était vrai, il ne serait que low.

**Relecture de suivi recommandée : oui.** Plusieurs entrées medium ont été corrigées (2 ou plus), dont deux à risque non vérifié :
- la nouvelle garde `getaddrinfo`, qui pourrait bloquer des bibliothèques résolvant `localhost` autrement ;
- le registre CLI élargi à `ImportError`/`OSError`.

**Vérification** (2026-10-12) :
- `uv lock --check` : OK. torch `2.14.1+cu130` vient de `download.pytorch.org/whl/cu130`.
- `uv sync --python 3.12` : socle et groupe dev, sans extras.
- `uv run slmsp --help` : 12 commandes, code 0. `slmsp fetch x` : code 2.
- `ruff check` et `ruff format --check` : propres.
- `uv run pytest` : 129 tests réussis.

**Décisions prises seul** (à reporter au journal) :
1. **Index CUDA retenu : cu130** (roue `torch-2.14.1+cu130-cp312-win_amd64` présente le 2026-10-12).
2. **`[tool.uv] conflicts = [[fetch], [train]]`.** `transformers==5.17.0` exige `huggingface-hub<2`, alors que l'extra `fetch` épingle 2.2.0 (tableau Stack). Les deux extras ne s'installent donc pas ensemble. **À trancher par Anaël** : garder ainsi, ou descendre `fetch` en hub 1.x.
3. **`[tool.uv] environments = ["sys_platform == 'win32'"]`** : le lock ne résout que pour Windows (D2).
4. **`eval/calibrage/build_calibrage.py` est exclu de ruff en entier** : il est en lecture seule et compte environ 249 écarts de style. `eval/outils/**` n'est exclu que de `TID251`.
5. **`.gitignore`** :
   - motifs racine ancrés (`/index/` est indispensable à cause de `src/slmsp/index/`) ;
   - anciennes règles conservées : `outputs/`, `*.bin`, `*.parquet`, `wandb/`, `data/cache/` ;
   - `*.pt`, `*.pth` et `*.ckpt` ajoutés.
6. **`.env.example`** : lignes `BUDGET_*_EUR` retirées, car les plafonds vont dans `config/budgets.toml` (story 1.5) ; ils sont rappelés en commentaire.
7. **Test AST** : règles en plus des critères (`mistralai`, `publication`, avec `push_to_hub=` différent de `False`) ; `open` en appel d'attribut compté comme lecture dans `data` et `train`.
8. **CLI** : seul le module de la sous-commande appelée est importé ; une sous-commande qui renvoie `None` vaut succès.

**Risques résiduels et reste à installer.**
- Les extras ne sont pas installés : `fetch`, `data`, `judge`, `bench`, `train` (torch CUDA environ 2,5 Go) et `app`. Ils ont été retenus volontairement à cause de la contrainte de bande passante jusqu'à 08h30.
- ruff ne distingue pas les bannissements dans un dossier exempté : la matrice exacte est dans le test AST.
