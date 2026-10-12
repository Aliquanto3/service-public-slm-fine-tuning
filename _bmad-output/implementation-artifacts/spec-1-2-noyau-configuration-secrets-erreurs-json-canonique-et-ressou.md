---
title: 'Story 1.2 — Noyau : configuration, secrets, erreurs, JSON canonique et ressources partagées'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '18faff3ff57c4ef0cedafe7da348fe3f157c83d1'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      racine_projet() suppose une installation éditable (Path(__file__).parents[3]) ; hors de ce cas, .env et models/ par défaut pointent au mauvais endroit, sans erreur.
    evidence: |-
      uv installe le projet en éditable : le cas ne se produit pas aujourd'hui. À vérifier pour l'application J4
      (PyInstaller) : chercher pyproject.toml dans les parents et lever une erreur claire, ou fixer la racine
      par configuration. Les surcharges SLMSP_ENV_FILE et SLMSP_MODELS_DIR permettent déjà de contourner.
    location: >-
      src/slmsp/core/config.py (racine_projet)
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** le paquet `slmsp` n'a ni chargement de configuration validé, ni lecture sûre des secrets, ni hiérarchie d'erreurs, ni primitives partagées (JSON canonique, `SLMSP_VAR_DIR`, SQLite, verrou GPU) : chaque story suivante coderait les siennes, en dur et de façon divergente.

**Approach:** créer en couche 0 (`slmsp.core`) les modules `config`, `secrets`, `erreurs`, `canonique` et `var` décrits par les critères 1 à 8 de la story 1.2 d'`epics.md` (AD-22, AD-27, AD-4 environnement imposé, D-nuit-A2-8), puis brancher la CLI : environnement imposé au démarrage et conversion de toute `SlmspError` en code de sortie.

## Boundaries & Constraints

**Always:**
- Couche 0 : `core` n'importe que la bibliothèque standard, `pydantic`, `python-dotenv` et `psutil` ; jamais `cli` ni un autre paquet `slmsp`.
- `CodeSortie` (IntEnum 0..5) migre dans `core/erreurs.py` ; `slmsp.cli` le réimporte (les tests 1.1 l'importent depuis `slmsp.cli`).
- Secrets : `dotenv_values` seulement, `os.environ` jamais modifié, `SecretStr` ; aucun message d'erreur ne cite une valeur.
- Aucune fonction de `core/var.py` ne supprime un fichier ; le verrou GPU repose sur un verrou d'octets du système (`msvcrt.locking`, `fcntl.lockf` hors Windows), libéré par l'OS à la mort du détenteur.
- Tests sans réseau ni secret réel : `.env` factice dans `tmp_path`, valeurs manifestement factices.

**Never:**
- Ne pas toucher `.env.example`, `pyproject.toml`, `tests/conftest.py`, `core/__init__.py`, `core/texte.py` (story 5.2) ni aucun fichier hors zone.
- Pas de fichier `config/*.toml` (ils arrivent avec leurs stories) ; pas de `uv sync` avec extras.
- Ne jamais lire le `.env` réel du dépôt principal dans les tests.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| TOML valide | `charger_toml(f, M)`, `M` dérivé de `ModeleConfig` | instance de `M` | — |
| Clé inconnue / type faux | `[a] zz = 1` ; `n = "x"` pour un `int` | `ConfigurationInvalide` (code 1) | message cite le chemin du fichier et la clé pointée (`a.zz`) |
| TOML illisible / absent | syntaxe fausse ; fichier manquant | `ConfigurationInvalide` | message cite le fichier |
| Modèle permissif | `M` sans `extra="forbid"` | `TypeError` (erreur de développeur) | — |
| Secret présent | `.env` : `MISTRAL_API_KEY=<factice>` | `SecretStr`, `repr` masqué, `os.environ` inchangé | — |
| Secret absent ou vide | clé absente ou `MISTRAL_API_KEY=` | `SecretManquant` (code 1) | cite le nom et le fichier, aucune valeur |
| Env de sous-processus | env avec `*_API_KEY`, `HF_TOKEN` | clés retirées (insensible à la casse) ; télémétrie et `HF_HOME` absolu posés | — |
| JSON canonique | `{"b": 1, "a": "é"}` | `b'{"a":"\xc3\xa9","b":1}'` | `NaN` refusé (`ValueError`) |
| Var par défaut | `SLMSP_VAR_DIR` absent | `%LOCALAPPDATA%\slmsp\var`, créé | — |
| Verrou occupé, sans attente | autre processus détient `gpu.lock` | `RessourceOccupee` (code 5) avec PID et commande du détenteur | — |
| Verrou occupé, avec attente | détenteur libère | verrou obtenu | délai dépassé → `RessourceOccupee` |
| Détenteur mort | PID mort (tué, ou fichier résiduel) | verrou obtenu sans attente | — |
| Erreur en CLI | sous-commande lève `BudgetEpuise("…")` | stderr `slmsp : …`, code 3, sans trace | — |

</intent-contract>

## Code Map

- `src/slmsp/cli/__init__.py` -- `CodeSortie` l. 22-30 à remplacer par un import de `core.erreurs` ; `main` l. 132-149 : appeler `appliquer_environnement_impose()` au début, entourer `func(args)` (l. 148) d'un `except SlmspError`.
- `src/slmsp/core/__init__.py` -- vide, à laisser tel quel.
- `tests/conftest.py` -- lecture seule ; `SLMSP_VAR_DIR` déjà temporaire par test, garde réseau active.
- `tests/test_cli.py` -- lecture seule ; importe `CodeSortie` depuis `slmsp.cli` ; modèle d'injection de sous-commandes synthétiques (`SOUS_COMMANDES` + module).
- `tests/test_architecture.py` -- lecture seule ; vérifie que `core` n'importe rien de couche supérieure.
- `pyproject.toml` -- socle : pydantic 2.14.1, python-dotenv 1.2.4, psutil 7.2.2 (rien à ajouter).
- Spine : AD-4 (environnement imposé), AD-22, AD-27, conventions « Erreurs » et « Fichiers de données » ; journal : D-nuit-A1-20, D-nuit-A2-8.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/erreurs.py` -- `CodeSortie` ; `SlmspError(Exception)` avec `code_sortie` de classe (1) ; sous-classes `BudgetEpuise` (3), `ManifesteInvalide` (4), `RessourceOccupee` (5, attributs `pid`, `commande`), `HoteBloque`, `AppelNonConforme`, `SchemaOutilModifie`, `SourceSansLicence`, `ProvenanceInvalide`, `LectureInterdite`, `TarifInconnu`, plus `ConfigurationInvalide` et `SecretManquant` (1).
- `src/slmsp/core/canonique.py` -- `json_canonique(obj) -> bytes`, `sha256_hex(bytes | str) -> str`, `sha256_fichier(chemin, taille_bloc=1 Mio) -> str` en flux.
- `src/slmsp/core/config.py` -- `racine_projet()` ; `dossier_modeles()` (`SLMSP_MODELS_DIR` sinon `<racine>/models`) ; `ModeleConfig` (`extra="forbid"`) ; `charger_toml(chemin, Modele)` ; `ENV_IMPOSE` ; `appliquer_environnement_impose()` ; `env_sous_processus(base=None) -> dict[str, str]`.
- `src/slmsp/core/secrets.py` -- `fichier_env()` (`SLMSP_ENV_FILE` sinon `<racine>/.env`) ; `secret(nom, fichier=None) -> SecretStr`.
- `src/slmsp/core/var.py` -- `dossier_var()`, `ouvrir_sqlite(chemin)`, `verrou_gpu(attendre=False, delai=None, commande=None)` (gestionnaire de contexte).
- `src/slmsp/cli/__init__.py` -- selon le Code Map.
- `tests/core/test_{config,secrets,erreurs,canonique,var}.py` -- une série par critère et par ligne de la matrice ; verrou GPU testé avec un second processus Python (`subprocess`, `sys.executable`) ; test AST : `var.py` n'appelle ni `unlink`, ni `remove`, ni `rmtree`, ni `rmdir`.

**Acceptance Criteria:**
- Given la story terminée, when `uv run pytest` puis `uv run ruff check` et `uv run ruff format --check`, then tout passe, y compris les 129 tests de 1.1 et le test d'architecture.
- Given `slmsp` lancé, when `main()` démarre, then `HF_HUB_DISABLE_TELEMETRY`, `WANDB_MODE` et `DO_NOT_TRACK` sont posés dans `os.environ` avant toute sous-commande.
- Given `from slmsp.cli import CodeSortie` et `from slmsp.core.erreurs import CodeSortie`, when on compare, then c'est la même classe.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 39 findings — high 0, medium 6, low 24, false 6, maybe-false 3
- findings:
  - `[low]` `[reject]` (VG-1) Branche `fcntl.lockf` (hors Windows) jamais exécutée — le projet ne vise que Windows (D2), sans exécuteur POSIX ; la tester demande une nouvelle plateforme.
  - `[low]` `[patch]` (VG-2) Refus du mode WAL non testé — `test_ouvrir_sqlite_wal_refuse` (`:memory:` → `SlmspError` « WAL »).
  - `[low]` `[reject]` (VG-autre) Variables de télémétrie qui restent dans `os.environ` après `main()` en test — sans effet sur aucun test, valeurs inoffensives ; la neutralisation toucherait `tests/test_cli.py` (zone 1.1).
  - `[low]` `[patch]` (intent 1) `SlmspError` levée à l'import ou dans `enregistrer()` non convertie — `construire_parseur` entouré, helper `_signaler`, tests import (code 4) et enregistrer (code 5).
  - `[false]` `[reject]` (intent 2) `env_sous_processus` non branché, `HF_HOME` par défaut lié à l'installation éditable — aucun lanceur de sous-processus n'existe encore (stories 2.2, 6.x) ; la racine est traitée par la ligne différée blind 8.
  - `[false]` `[reject]` (intent 3) `.env` par défaut = celui du worktree — `SLMSP_ENV_FILE` est prévu pour cela et documenté ; les tests ne lisent jamais le `.env` réel (exigence de la spec).
  - `[false]` `[reject]` (intent 4) `TypeError` pour un modèle permissif hors `SlmspError` — erreur de développeur, jamais déclenchée par une saisie ; comportement voulu.
  - `[low]` `[reject]` (intent 5) Second processus par `subprocess` et non `multiprocessing` — même garantie (deux processus réels) ; `multiprocessing` en spawn ne retrouve pas les fonctions d'un module de test importé en mode `importlib`. Partie « imbrication » traitée par blind 4.
  - `[false]` `[reject]` (intent 6) `ftruncate` de `gpu.lock` contraire à « ne supprime aucun fichier » — le fichier n'est pas supprimé ; `gpu.lock` n'est pas un artefact (la règle « ni ne tronque » de 1.3 vise les artefacts).
  - `[false]` `[reject]` (intent 7) Ajouts hors texte de la story (`SLMSP_ENV_FILE`, `SLMSP_MODELS_DIR`, deux erreurs, `CodeSortie` déplacé) — tous consignés dans la spec, dans la zone, sans effet nuisible nommé.
  - `[false]` `[reject]` (intent 8) Ni commit ni `## Auto Run Result` — produits à la finalisation de ce workflow.
  - `[medium]` `[patch]` (blind 1) `UnicodeDecodeError` d'un TOML non UTF-8 non converti — capturé, `ConfigurationInvalide` citant le fichier, `test_toml_non_utf8`. Le BOM donne déjà `TOMLDecodeError` (capturée).
  - `[low]` `[reject]` (blind 2) Clés non textuelles et NFC dans `json_canonique` — toutes les données hachées viennent de JSON/TOML (clés `str`) ; un parcours récursif ajoute une branche pour un cas improbable.
  - `[maybe-false]` `[reject]` (blind 3) Délai possible de libération du verrou par Windows après la mort du détenteur — six exécutions stables ; à trancher en observant des échecs aléatoires ; si vrai, low (test instable seulement).
  - `[medium]` `[patch]` (blind 4) Réentrée de `verrou_gpu` dans un même processus (attente infinie sous Windows, verrou perdu sous POSIX) — drapeau de module sous `threading.Lock`, `RessourceOccupee` immédiate, `test_verrou_gpu_reentree_refusee`.
  - `[low]` `[patch]` (blind 5) `commande` longue → JSON tronqué, « détenteur inconnu » — `commande` coupée à 1 000 caractères, lecture portée à 8 192 octets, test. Partie « secret en argument » : la CLI ne prend aucun secret en argument.
  - `[low]` `[patch]` (blind 6) Filtre de secrets trop étroit — ajout de `API_KEY`, `*_TOKEN`, `*SECRET*`, `HF_TOKEN_PATH`, test étendu.
  - `[low]` `[reject]` (blind 7) `appliquer_environnement_impose` ne pose pas `HF_HOME` — le critère 3 limite la pose en processus aux trois variables de télémétrie ; `HF_HOME` en processus relève de `fetch` (story 2.1).
  - `[maybe-false]` `[defer]` (blind 8) `racine_projet()` faux hors installation éditable — voir `deferred` ; la partie « chemin relatif de `SLMSP_ENV_FILE` » est corrigée avec edge 9.
  - `[low]` `[reject]` (blind 9) Fuite des variables de télémétrie entre tests — même cause que VG-autre.
  - `[low]` `[patch]` (blind 10) Message multi-lignes mal préfixé, `SlmspError` dans `construire_parseur` — `_signaler` préfixe chaque ligne ; même cause que intent 1.
  - `[low]` `[patch]` (blind 11) Refus WAL non testé — même cause que VG-2.
  - `[low]` `[reject]` (blind 12) `delai` négatif accepté — usage improbable ; un garde ajoute une branche, et le comportement (refus immédiat) reste correct.
  - `[low]` `[reject]` (blind 13) Processus détenteur des tests pouvant figer la suite — improbable ; une lecture à délai demande un fil supplémentaire.
  - `[low]` `[patch]` (blind 14) Assertion tautologique sur `sha256_hex(b"")` — comparée à `e3b0c442…b855`.
  - `[low]` `[reject]` (blind 15) `code_sortie` non contraint pour les sous-classes futures, `pid`/`commande` perdus au pickling — aucun appelant concerné aujourd'hui ; ajout de surface (`__init_subclass__`, `__reduce__`).
  - `[medium]` `[patch]` (edge 1) TOML non UTF-8 — même cause que blind 1.
  - `[low]` `[patch]` (edge 2) `.env` non UTF-8 ou illisible → trace — `dotenv_values` entouré, `SecretManquant` sans valeur, `test_env_non_utf8`.
  - `[low]` `[patch]` (edge 3) `SlmspError` à l'import ou dans `enregistrer()` — même cause que intent 1.
  - `[medium]` `[patch]` (edge 4) Réentrée Windows : attente infinie — même cause que blind 4.
  - `[medium]` `[patch]` (edge 5) Réentrée POSIX : verrou perdu à la fermeture — même cause que blind 4.
  - `[low]` `[patch]` (edge 6) Contenu du verrou > 4 096 octets — même cause que blind 5.
  - `[low]` `[reject]` (edge 7) Clés non textuelles — même cause que blind 2.
  - `[maybe-false]` `[defer]` (edge 8) `racine_projet()` hors installation éditable — même cause que blind 8.
  - `[low]` `[patch]` (edge 9) `SLMSP_ENV_FILE` / `SLMSP_MODELS_DIR` relatifs ou avec `~` — `expanduser().resolve()`, tests.
  - `[low]` `[patch]` (edge 10) `API_KEY`, `*_TOKEN` transmis aux sous-processus — même cause que blind 6.
  - `[low]` `[reject]` (edge 11) Fuite de télémétrie entre tests — même cause que VG-autre.
  - `[medium]` `[patch]` (edge 12) Ligne « TOML illisible » de la matrice non tenue pour un fichier non UTF-8 — même cause que blind 1.
  - `[low]` `[patch]` (edge 13) Ligne « Erreur en CLI » de la matrice : import et `enregistrer` — même cause que intent 1.

## Design Notes

- **Verrou sans suppression.** `gpu.lock` est permanent. On verrouille un octet à l'offset 1 Mio (hors du contenu) ; le contenu (JSON `pid`, `commande`, `depuis`) est réécrit en tête par le détenteur et lu par les candidats refusés. L'OS libère le verrou quand le processus meurt : un PID mort est récupéré sans nettoyage.
- **Racine et worktrees.** `racine_projet()` = `Path(__file__).parents[3]` (installation éditable d'uv). `SLMSP_ENV_FILE` et `SLMSP_MODELS_DIR` permettent à un worktree de pointer le `.env` et `models/` du dépôt principal (consignes de la nuit).
- **Message d'erreur de config** : `"<chemin> : clé « a.zz » : <message pydantic>"`, une ligne par erreur, sans la valeur saisie.

## Verification

**Commands:**
- `uv run pytest` -- expected: tout passe.
- `uv run ruff check` et `uv run ruff format --check` -- expected: aucun écart.
- `uv run slmsp --help` -- expected: code 0, 12 sous-commandes.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** Noyau de couche 0 :
- `core.erreurs` : hiérarchie `SlmspError`, `CodeSortie` ;
- `core.config` : `charger_toml` strict, environnement imposé, environnement de sous-processus filtré ;
- `core.secrets` : `secret()` en `SecretStr` par `dotenv_values` ;
- `core.canonique` : JSON canonique et SHA-256 ;
- `core.var` : `SLMSP_VAR_DIR`, SQLite WAL et `busy_timeout` 30 s, verrou GPU exclusif.

La CLI pose la télémétrie au démarrage et convertit toute `SlmspError` en code de sortie, sans trace.

**Fichiers.**
- `src/slmsp/core/erreurs.py` : `CodeSortie` déplacé ici, `SlmspError` et 12 sous-classes avec `code_sortie`.
- `src/slmsp/core/config.py` : `racine_projet`, `dossier_modeles`, `ModeleConfig`, `charger_toml`, `ENV_IMPOSE`, `appliquer_environnement_impose`, `env_sous_processus`.
- `src/slmsp/core/secrets.py` : `fichier_env`, `secret`.
- `src/slmsp/core/canonique.py` : `json_canonique`, `sha256_hex`, `sha256_fichier`.
- `src/slmsp/core/var.py` : `dossier_var`, `ouvrir_sqlite`, `verrou_gpu`.
- `src/slmsp/cli/__init__.py` : import de `CodeSortie`, environnement imposé, `_signaler`.
- `tests/core/test_{config,secrets,erreurs,canonique,var}.py` : 74 tests.

**Revue** (une passe, 39 constats).
- Correctifs : 9 entrées, dont 2 medium (TOML non UTF-8 ; réentrée du verrou GPU) et 7 low.
- Différé : 1 entrée, `racine_projet` hors installation éditable, à revoir en J4.
- Rejetés : 6 faux et 12 low ou maybe-false, raisons dans le journal de tri.

**Relecture de suivi recommandée : oui.** Deux entrées medium ont été corrigées. Le risque non vérifié porte sur le drapeau de réentrée de `verrou_gpu`, un état global du processus : son comportement sous plusieurs fils concurrents n'est testé qu'en imbrication.

**Vérification** (2026-10-12) :
- `uv run pytest` : 203 réussis ;
- `ruff check` et `ruff format --check` : propres ;
- `uv run slmsp --help` : code 0.

**Décisions prises seul** (à reporter au journal) :
1. **Deux erreurs ajoutées** : `ConfigurationInvalide` et `SecretManquant`, toutes deux en code 1.
2. **`CodeSortie` déplacé** dans `core.erreurs`, et réexporté par `slmsp.cli`.
3. **Nouvelles variables d'environnement** :
   - `SLMSP_ENV_FILE` pointe le `.env` ;
   - `SLMSP_MODELS_DIR` pointe `models/`.

   Un worktree peut ainsi viser les fichiers du dépôt principal. `HF_HOME` vaut `<models>/.cache-hf`.
4. **`charger_toml`** refuse par `TypeError` tout modèle, même imbriqué, qui ne déclare pas `extra="forbid"`.
5. **Secret** : une valeur vide ou faite d'espaces compte comme absente. `os.environ` n'est jamais consulté.
6. **Filtre des sous-processus.** Il retire :
   - `*_API_KEY` et `API_KEY` ;
   - `*_TOKEN`, `HF_TOKEN_PATH` et `HUGGING_FACE_HUB_TOKEN` ;
   - tout nom qui contient `SECRET`.

   La casse est ignorée.
7. **Verrou GPU** :
   - c'est un verrou d'octets du système, posé sur un `gpu.lock` permanent ;
   - le système le libère à la mort du détenteur, sans suppression ;
   - la réentrée dans un même processus est refusée ;
   - `commande` est coupée à 1 000 caractères.

   Le second processus des tests est lancé par `subprocess`, et non par `multiprocessing` : en spawn, `multiprocessing` ne retrouve pas un module de test importé en mode `importlib`.
8. **`json_canonique`** refuse `NaN` et les infinis.
9. **Repli de `dossier_var`** : `~/AppData/Local/slmsp/var` si `LOCALAPPDATA` est absent.

**Risques résiduels.**
- La branche POSIX (`fcntl`) n'est pas testée, faute de poste Linux.
- Les variables de télémétrie restent posées dans le processus de test après un appel à `main()`. C'est inoffensif.
- `env_sous_processus` n'a pas encore d'appelant : les lanceurs viennent avec les stories 2.2 et 6.x.
- La limite réseau a été levée en cours de run (message du coordinateur), sans effet sur cette story : aucun téléchargement n'a été fait.
