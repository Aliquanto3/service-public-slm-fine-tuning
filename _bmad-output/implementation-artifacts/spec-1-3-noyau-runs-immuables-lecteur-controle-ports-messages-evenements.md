---
title: 'Story 1.3 — Noyau : runs immuables, lecteur contrôlé, ports, messages et évènements'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '3c276e7e134bc0b470b7fbd2a2f1f1f6119d82f2'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Le journal appels-mistral.sqlite, lisible par les lecteurs data et train, contiendra aussi les appels du second juge (usage juge-second), donc des textes du Jeu d'évaluation.
    evidence: |-
      AD-3.3 : le journal enregistre usage ∈ {generation, juge-second, validation} avec la requête complète.
      AD-24 et D-nuit-A2-18 autorisent la lecture du fichier entier. data build ne garde que usage = generation
      (AD-3.4), mais rien n'empêche une lecture des lignes juge-second par data ou train.
      À trancher (stories 5.5 et 9.2) : journal séparé pour le second juge, ou vue filtrée par usage
      exposée par core.artefacts.
    location: >-
      src/slmsp/core/artefacts.py (chemin_autorise, NOM_JOURNAL_MISTRAL)
    severity: medium
---

<intent-contract>

## Intent

**Problem:** aucun pipeline ne peut encore écrire un résultat rattaché à sa configuration sans risque d'écrasement, `data` et `train` n'ont pas de point de contrôle de lecture (AD-24, garde-fou D1.1), et le Harnais n'a ni ports, ni format de conversation, ni évènements typés : les stories 3.1, 4.1, 5.1 et 9.1 n'ont rien sur quoi s'appuyer.

**Approach:** ajouter en couche 0 (`slmsp.core`) les modules `artefacts` (runs immuables, reprise, lecteur contrôlé, espace disque), `ports` (protocoles), `messages` (conversation OpenAI validée) et `evenements` (évènements sérialisables), et le paquet `core/schemas/` (`SchemaBase`, `RunManifest`, `ConfigModele`, `ConfigLlamacpp`), selon les 11 critères de la story 1.3 d'`epics.md` (AD-1, AD-6, AD-7, AD-14, AD-21, AD-24 à AD-26, AD-28 ; D-nuit-A2-7, A2-18).

## Boundaries & Constraints

**Always:**
- Couche 0 : les nouveaux modules n'importent que la bibliothèque standard, `pydantic`, `numpy` (sous `TYPE_CHECKING` seulement), `pynvml` (paquet `nvidia-ml-py`, import paresseux en `try`) et `slmsp.core.*`. Jamais `httpx`, ni un paquet `slmsp` de couche supérieure.
- Réutiliser `core.canonique` (`json_canonique`, `sha256_fichier`), `core.config` (`racine_projet`, `dossier_modeles`, `env_sous_processus`), `core.var.dossier_var`, `core.erreurs` (`SlmspError`, `LectureInterdite`, `ManifesteInvalide`).
- Aucune fonction d'`artefacts.py` ne supprime, ne renomme, ne remplace ni ne tronque un fichier : création exclusive (`"xb"`), ajout (`"ab"`), jamais de mode `"w"`.
- Tous les schémas dérivent de `SchemaBase` (`extra="forbid"`, `schema_version`) ; `core/schemas/__init__.py` ne réexporte rien.
- Fichiers JSONL : UTF-8, LF, une ligne = `json_canonique(obj) + b"\n"`. Dates ISO 8601 avec fuseau.
- Tests sans réseau ni secret ; fixtures factices ; racine de projet factice dans `tmp_path` (avec `git init` quand le commit est testé).

**Never:**
- Ne toucher à aucun fichier hors zone : `core/{config,secrets,erreurs,canonique,var,texte}.py`, `core/__init__.py`, `cli/`, `pyproject.toml`, `tests/conftest.py`, `tests/test_architecture.py`, `eval/`.
- Pas de fichier `config/*.toml` réel (arrivent avec 2.1, 2.2, 8.1) ; les TOML de test sont écrits dans `tmp_path`.
- Pas d'implémentation concrète des ports (adaptateurs des epics 2 à 4), pas de `core/schemas/journal_requetes.py` (story 1.4).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nouveau run | `nouveau_run("eval-generation", "granite-4.0-1b", config, [], {"jeu": f}, 42, racine=tmp)` | `tmp/runs/eval-generation/<run_id>/run.json` valide `RunManifest`, `statut="en_cours"`, `etat.jsonl` à une ligne `en_cours` | — |
| Slug ou type invalide | slug `"Mon Slug"` ; type `"../x"` | refus | `ValueError` |
| Collision de `run_id` | dossier déjà présent | nouveau suffixe hexadécimal tiré | après 20 essais : `SlmspError` |
| Hors dépôt git | racine sans `.git` ou `git` absent | `git_commit=None`, `git_modifie=None` | — |
| Réécriture | `run.ecrire("scores.json", ...)` deux fois | 1re écriture faite | 2e : `ArtefactExistant`, contenu inchangé |
| Nom hors du run | `run.ecrire("../x", ...)`, chemin absolu | refus | `ValueError` |
| Fin de run | `run.terminer("complet")` | ligne ajoutée à `etat.jsonl`, `run.json` intact, `statut_courant(run)=="complet"` | statut hors liste ou `en_cours` → `ValueError` |
| Reprise | run `interrompu`, `generations.jsonl` de 3 lignes à clé `item_id` | ligne `en_cours` ajoutée, 3 lignes intactes, retourne `(run, {"Q-001","Q-002","Q-003"})` | run `complet` → `SlmspError` ; `run_id` inconnu → `ManifesteInvalide` |
| Lecture `data` permise | `data/raw/x.parquet`, `runs/data-seed/<id>/a.jsonl`, `config/outils-mcp.toml`, `<var>/appels-mistral.sqlite` | octets du fichier | — |
| Lecture `data` refusée | `eval/jeu/v1/Q.jsonl`, `runs/eval-generation/...`, `data/raw/../../eval/x`, lien vers `eval/`, `<var>/cache-verdicts.sqlite`, `config/taches.toml` | — | `LectureInterdite` (code 1), message cite le chemin résolu et le lecteur |
| Lecture `train` | `data/train/v1/train.jsonl`, `<models>/x`, `<var>/appels-mistral.sqlite` permis ; `data/raw/x` refusé | — | `LectureInterdite` |
| Lecteur inconnu | `lecteur="eval"` | — | `ValueError` |
| Espace disque | libre < `octets + seuil` | — | `EspaceInsuffisant` citant libre, demandé, seuil |
| Conversation valide | system, user, assistant(`tool_calls`), tool(`tool_call_id` connu), assistant | liste de messages typés | — |
| Conversation invalide | rôle `developer` ; `arguments` non JSON ou non objet ; `type != "function"` ; `tool_call_id` inconnu ou avant son appel ; `id` d'appel dupliqué ; assistant sans `content` ni `tool_calls` | — | `ConversationInvalide` (code 1) citant l'index du message |
| Évènements | chacun des 10 types | `vers_dict` → dict JSON avec clé `type` ; `depuis_dict(vers_dict(e)) == e` ; `json_canonique` identique sur deux appels | type inconnu → `ValidationError` pydantic |

</intent-contract>

## Code Map

- `src/slmsp/core/erreurs.py` -- lecture seule ; `SlmspError` (code 1), `LectureInterdite` (code 1), `ManifesteInvalide` (code 4). Les nouvelles erreurs de cette story sont des sous-classes de `SlmspError` déclarées dans le module qui les lève (zone 1.2 intouchable).
- `src/slmsp/core/canonique.py` -- `json_canonique(obj) -> bytes`, `sha256_fichier(chemin)`, à réutiliser pour JSONL et SHA des entrées.
- `src/slmsp/core/config.py` -- `racine_projet()` (racine par défaut), `dossier_modeles()` (racine `models/` du lecteur `train`, suit `SLMSP_MODELS_DIR`), `env_sous_processus()` (environnement de l'appel `git`), `ModeleConfig` (non utilisé : les schémas ont leur propre base).
- `src/slmsp/core/var.py` -- `dossier_var()` : emplacement du journal `appels-mistral.sqlite`.
- `tests/conftest.py` -- lecture seule ; `SLMSP_VAR_DIR` temporaire par test, garde réseau (le `git` local ne fait pas de réseau).
- `tests/test_architecture.py` -- lecture seule ; impose que `core` n'importe aucun paquet de couche supérieure ni client HTTP ; ses arbres synthétiques mentionnent déjà `slmsp.core.artefacts.lire`.
- `pyproject.toml` -- lecture seule ; `nvidia-ml-py` (module `pynvml`) et `pydantic` 2.14.1 déjà au socle ; pytest en `--import-mode=importlib`.
- Spine : AD-21 (dossier de run, `run_id`), AD-25 (champs `RunManifest`, statuts), AD-26 (reprise), AD-24 + D-nuit-A2-18 (listes de lecture), AD-1/AD-14 (ports, évènements), AD-7 (messages), AD-6/AD-28 + epics 2.2, 8.1 (`chat_template_force` booléen, template exporté sous `models/<slug>/chat_template.jinja`).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/schemas/__init__.py` -- `SchemaBase(BaseModel)` : `model_config = ConfigDict(extra="forbid")`, champ `schema_version: int`. Aucun import de sous-module.
- `src/slmsp/core/schemas/run.py` -- `Statut` (Literal des 6 statuts), `STATUTS_FINAUX` (5, sans `en_cours`), `ModeleRef` (motif `^(base:[a-z0-9.-]+|ft:\d{8}-\d{6}-[a-z0-9.-]+-[0-9a-f]{4})$`), `Environnement` (`os`, `machine`, `cpu`, `nb_coeurs`, `python`, `gpus: list[Gpu(nom, memoire_octets)]`, `pilote_nvidia`, `cuda`, `paquets: dict[str, str]`, `git_commit`, `git_modifie`), `RunManifest(schema_version: Literal[1]=1)` avec `type`, `run_id` (motif AC 1), `cree_le`, `parents: list[str]`, `modele_ref`, `quantification: Literal["f16","q4_k_m"]|None`, `variante_llamacpp: Literal["cpu","cuda"]|None`, `llamacpp_tag`, `chat_template_sha256`, `jeu_version`, `index_version`, `statut` (`en_cours` par défaut), `couverture: dict[str, Any]|None`, `config: dict[str, Any]`, `graine: int|None`, `environnement`, `entrees: dict[str, str]` (nom → SHA-256), et `EtatRun(schema_version: Literal[1]=1, horodatage, statut, pid, motif: str|None)` pour `etat.jsonl`.
- `src/slmsp/core/schemas/config_modele.py` -- `ConfigModele` (AD-6, AD-28) : `depot_hf`, `revision` (SHA de commit 40 hex), `fichiers: list[str]`, `gguf: FichierGguf(depot, fichier, sha256)`, `contexte: int>0`, `cache_kv: Literal["f16","q8_0","q4_0"]="f16"`, `threads: int|None`, `reasoning: Literal["off","on","auto"]="off"`, `chat_template_kwargs: dict[str, Any]={}`, `protocole_outils: Literal["natif","json-generique"]`, `exclure_vision: bool=False`, `chat_template_force: bool=False`, `embedding: bool=False`, `pooling: Literal["cls","mean","last"]|None`.
- `src/slmsp/core/schemas/config_llamacpp.py` -- `ConfigLlamacpp` : `tag` (motif `^b\d+$`), `depot="ggml-org/llama.cpp"`, `assets: dict[Literal["cpu","cuda","cudart"], Asset(nom, sha256)]`, `sources: Asset`, `binaires: dict[str, str]={}` (chemin relatif → SHA-256). Tous les SHA : motif `^[0-9a-f]{64}$`.
- `src/slmsp/core/artefacts.py` -- erreurs `ArtefactExistant`, `EspaceInsuffisant` (sous-classes de `SlmspError`) ; classe `Run` (`dossier`, `run_id`, `type`, `manifeste`) avec `ecrire(nom, contenu: bytes|str)`, `ajouter_jsonl(nom, obj)`, `lire_jsonl(nom)`, `terminer(statut, motif=None)`, `statut_courant()` ; fonctions `nouveau_run(type, slug, config, parents=(), entrees=None, graine=None, *, racine=None, **champs)` (`champs` = autres champs facultatifs de `RunManifest`), `ouvrir_run(run_id, *, racine=None)`, `reprendre(run_id, *, fichier="resultats.jsonl", cle="cle", racine=None) -> tuple[Run, set[str]]`, `ajouter_jsonl(chemin, obj)`, `empreinte_environnement(racine)`, `chemin_autorise(chemin, lecteur, *, racine=None) -> Path`, `lire(chemin, lecteur, *, racine=None) -> bytes`, `lire_texte(...)`, `ouvrir_sqlite_lecture(chemin, lecteur, *, racine=None)` (URI `mode=ro`), `verifier_espace(chemin, octets, *, seuil_octets=SEUIL_ESPACE_LIBRE)`.
- `src/slmsp/core/ports.py` -- `Passage` (dataclass figée : `chunk_id, doc_id, source, titre, url, texte, date_snapshot, score`), `Mode` (Literal `connecte`, `hors-ligne-detecte`, `hors-ligne-force`), protocoles `runtime_checkable` : `LlmPort.generer(messages, *, tools=None, options=None) -> Iterator[Jeton | AppelOutil | Fin]` et `compter_tokens(messages, tools=None) -> int` ; `EmbedderPort.dimension` + `vectoriser(textes) -> ndarray (n, dim) float32` ; `VectorStore.rechercher(vecteur, k) -> list[Passage]` ; `ToolPort.lister_outils() -> list[dict]` + `appeler(nom, arguments) -> dict` ; `NetGate.client(profil) -> Any` + `verifier(profil, methode, url, *, outil=None, termes=None) -> None` ; `ModePort.mode_courant() -> Mode` ; `JournalRequetes.inscrire(entree: Any) -> None` + `lister(limite=None) -> list[Any]` (entrée = `EntreeJournalRequetes` de la story 1.4).
- `src/slmsp/core/messages.py` -- `ConversationInvalide(SlmspError)` ; modèles pydantic `extra="forbid"` `MessageSysteme`, `MessageUtilisateur`, `MessageAssistant` (`content: str|None`, `tool_calls: list[AppelFonction]|None`), `MessageOutil` (`tool_call_id`, `content`, `name` facultatif), `AppelFonction(id, type: Literal["function"], function: Fonction(name, arguments: str))` ; `Message` (union discriminée par `role`) ; `valider_conversation(messages) -> list[Message]` ; `vers_dicts(messages) -> list[dict]` (sans les champs `None`).
- `src/slmsp/core/evenements.py` -- modèles figés discriminés par `type` : `Jeton(texte)`, `AppelOutil(id, nom, arguments: dict)`, `ResultatOutil(id, nom, resultat: Any, erreur: bool=False)`, `AppelNonConforme(nom: str|None, arguments_bruts: str, motif)`, `Source(titre, url, origine: Literal["index","mcp"], date: str|None, extrait: str|None)`, `Sources(sources: list[Source])`, `Avertissement(code, message)`, `Progression(etape, fait, total: int|None)`, `Repli(motif, vers: Literal["index"])`, `Fin(raison: Literal["terminee","longueur","interrompue"], usage: dict[str,int]|None)`, `Erreur(code, message)` ; `Evenement` (union) ; `vers_dict(ev) -> dict`, `depuis_dict(d) -> Evenement`.
- `tests/core/test_schemas_run.py` -- critères 1 (forme du manifeste) et 11 (TOML de test `ConfigModele`, `ConfigLlamacpp` par `charger_toml`, clé inconnue refusée, `protocole_outils` hors liste refusé).
- `tests/core/test_artefacts.py` -- critères 1 à 4 et 7, lignes de la matrice ; racine factice avec `git init` (commit et indicateur de modification) ; test AST : `artefacts.py` n'appelle ni `unlink`, `remove`, `rmtree`, `rmdir`, `rename`, `replace`, `truncate`, `write_text`, `write_bytes`, ni `open` en mode contenant `"w"`.
- `tests/core/test_lecteur.py` -- critères 5 et 6, traversée `..`, lien symbolique (sauté si Windows refuse sa création), insensibilité à la casse sous Windows, lecteur inconnu, `ouvrir_sqlite_lecture` refuse l'écriture.
- `tests/core/test_ports.py` -- critère 8 : chaque protocole existe ; une doublure minimale passe `isinstance`.
- `tests/core/test_messages.py` -- critère 9 et lignes de la matrice.
- `tests/core/test_evenements.py` -- critère 10, aller-retour paramétré sur les 10 types.

**Acceptance Criteria:**
- Given la story terminée, when `uv run pytest`, `uv run ruff check` et `uv run ruff format --check`, then tout passe, y compris `tests/test_architecture.py` et les tests existants.
- Given `nouveau_run(...)` appelé dans un dépôt git factice avec un fichier suivi modifié, when on lit `run.json`, then `environnement.git_commit` vaut le SHA complet de `HEAD` et `environnement.git_modifie` vaut `true`.
- Given `runs/<type>/<run_id>/run.json` écrit, when on appelle `terminer`, `reprendre`, `ajouter_jsonl`, then les octets de `run.json` sont identiques avant et après.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 61 findings — high 0, medium 6, low 40, false 5, maybe-false 10
- findings (intent alignment) :
  - `[low]` `[reject]` (intent 1) `reprendre(run_id)` a des valeurs par défaut `fichier`/`cle` qu'aucun pipeline n'utilise — l'appel nu fonctionne ; les valeurs par défaut sont documentées, chaque pipeline passe les siennes.
  - `[low]` `[reject]` (intent 2) Seuil d'espace en constante, non lu d'un TOML — constante surchargée par `seuil_octets` ; aucun `config/*.toml` n'est dans la zone de 1.3.
  - `[false]` `[reject]` (intent 3) `data` ne lit qu'`appels-mistral.sqlite` et pas « les journaux » d'AD-24 — le critère 5 de la story, plus précis, fait foi.
  - `[false]` `[reject]` (intent 4) `nouveau_run` ne remplit pas tag, variante et SHA du template — `core` ne peut pas les connaître ; l'appelant les passe par `**champs`.
  - `[false]` `[reject]` (intent 5) `terminer` est une méthode de `Run` — comportement du critère 3 tenu et testé.
  - `[false]` `[reject]` (intent 6) `tool_call_id` exigé sur un appel antérieur — lecture conforme de « existant ».
  - `[low]` `[reject]` (intent 7) `test_ports.py` et noms ajoutés hors liste ; homonymie `AppelNonConforme` — nom imposé par le critère 10, modules distincts, tous dans la zone.
  - `[false]` `[reject]` (intent 8) Ni commit ni `Auto Run Result` — produits à la finalisation.
- findings (verification gap) :
  - `[low]` `[patch]` (VG-1) `verifier_espace` : le faux `disk_usage` ignorait son argument — argument vérifié, appel réel non simulé, valeurs négatives testées.
  - `[low]` `[patch]` (VG-2) Branches « ambigu » et « incohérent » d'`ouvrir_run` non testées — deux tests ajoutés.
  - `[low]` `[patch]` (VG-3) Chemins NVML (succès, erreur) non testés — faux module `pynvml` (octets, CUDA 12040 → « 12.4 ») et `nvmlInit` en erreur.
  - `[low]` `[patch]` (VG-4) Config non sérialisable avant création du dossier non vérifiée — même cause que VG-autre.
  - `[medium]` `[patch]` (VG-autre) NaN dans `config` écrit `null` en silence par `model_dump` — `json_canonique(dict(config))` et `json_canonique(couverture)` avant le `RunManifest` ; NaN, inf, `object()`, `Path` refusés sans dossier créé.
- findings (blind) :
  - `[medium]` `[patch]` (blind 1) Sous Windows, `run.json.`, `run.json ` ou `run.json::$DATA` passent la garde des noms réservés et ouvrent `run.json` en ajout — segments finissant par `.`/espace ou contenant `:` refusés, chemin résolu comparé aux fichiers réservés, `_nom_normalise` dans `ajouter_jsonl` ; tests.
  - `[maybe-false]` `[reject]` (blind 2) Pas de `fsync` : coupure de courant → `run.json` vide, dossier orphelin — à établir par un test de coupure ; si vrai, low : événement rare, et le `fsync` de dossier n'existe pas sous Windows.
  - `[low]` `[reject]` (blind 3) `reprendre` sans garde de processus vivant ; `terminer` accepte un second statut final — un seul orchestrateur lance les runs cette nuit ; la garde par PID ajoute une branche et un état.
  - `[low]` `[patch]` (blind 4) `ajouter_jsonl` non atomique entre écrivains — documenté : un seul écrivain par fichier, aucun verrou entre processus.
  - `[medium]` `[patch]` (blind 5) `git status --porcelain` compte les fichiers non suivis : `git_modifie` presque toujours vrai — `--untracked-files=no`, test « non suivi seul → false ».
  - `[maybe-false]` `[defer]` (blind 6) Le journal Mistral, lisible par `data` et `train`, contiendra les appels `juge-second` (textes d'évaluation) — voir `deferred` ; à vérifier quand le journal existera (stories 5.5, 9.2).
  - `[low]` `[patch]` (blind 7) Test SQLite en lecture seule sur une base non WAL ; connexion perdue si le PRAGMA lève — base créée par `var.ouvrir_sqlite`, `try/except` qui ferme.
  - `[low]` `[patch]` (blind 8) `assets` accepte un jeu incomplet — validateur : exactement `cpu`, `cuda`, `cudart`. Partie `binaires` (clés absolues) rejetée : improbable, ajoute un validateur.
  - `[low]` `[reject]` (blind 9) `FichierGguf` sans `revision` — le SHA-256 détecte toute dérive ; ajouter un champ obligatoire change la surface publique.
  - `[low]` `[patch]` (blind 10) `embedding`/`pooling` incohérents acceptés — validateur `(pooling is not None) == embedding` ; partie `fichiers` vide rejetée (modèle GGUF seul possible).
  - `[low]` `[patch]` (blind 11) `parents` et `llamacpp_tag` non contraints — motifs `MOTIF_RUN_ID` et `^b\d+$` ; `git_commit` et réutilisation du motif dans `ModeleRef` rejetés (cosmétique).
  - `[low]` `[patch]` (blind 12) `Passage.url` facultatif, `Source.url` obligatoire — `Passage.url` obligatoire.
  - `[maybe-false]` `[reject]` (blind 13) `resultat: Any` sans garantie d'aller-retour ; figé superficiel — à établir sur un résultat MCP réel ; ceux-ci sont du JSON natif ; si vrai, low.
  - `[low]` `[patch]` (blind 14) Contrôles de conversation manquants — corrigé : assistant à `content` vide sans appel, double réponse au même `tool_call_id` ; rejeté : ordre `tool` après `user`, appels sans réponse (fin de conversation légitime), `name` comparé.
  - `[low]` `[patch]` (blind 15) Tests dépendant de `pydantic==2.14.1` et de `nvidia-ml-py` — `metadata.version("pydantic")`, `nvidia-ml-py` non exigé.
  - `[low]` `[patch]` (blind 16) Chemins d'erreur non testés ; docstring `runs/eval*` — tests ajoutés (VG-2, espace, ligne tronquée d'`etat.jsonl`), docstring corrigée.
- findings (edge) :
  - `[medium]` `[patch]` (edge 1) Noms réservés contournables sous Windows — même cause que blind 1.
  - `[low]` `[patch]` (edge 2) `reprendre` marque `en_cours` avant de valider `fichier` — `run._chemin(fichier)` d'abord ; test.
  - `[low]` `[reject]` (edge 3) `reprendre` sur un run `en_cours` vivant — même raison que blind 3.
  - `[low]` `[reject]` (edge 4) `terminer` après `complet` — même raison que blind 3.
  - `[medium]` `[patch]` (edge 5) NaN, `Path`, `set` convertis en silence — même cause que VG-autre.
  - `[low]` `[patch]` (edge 6) `PydanticSerializationError` non documentée — même cause que VG-autre (`TypeError` désormais).
  - `[low]` `[reject]` (edge 7) Entrée absente → `FileNotFoundError` brute — échec bruyant, avant toute création de dossier.
  - `[low]` `[patch]` (edge 8) `parents` passé en chaîne → liste de caractères — même cause que blind 11.
  - `[low]` `[patch]` (edge 9) `ecrire("n.bin", 5)` écrit 5 octets nuls — seuls `bytes`, `bytearray`, `memoryview`, `str` acceptés, sinon `TypeError`.
  - `[maybe-false]` `[reject]` (edge 10) Écriture interrompue après création exclusive — à établir par un disque plein simulé ; si vrai, low (rare).
  - `[maybe-false]` `[reject]` (edge 11) Dossier orphelin après un arrêt entre `mkdir` et `run.json` — même note que blind 2.
  - `[low]` `[reject]` (edge 12) Slug très long ou type `con`/`nul` → `OSError` — échec bruyant, cas improbable.
  - `[maybe-false]` `[reject]` (edge 13) Ajouts concurrents entrelacés — documenté (blind 4) ; aucune concurrence prévue ; si vrai, low.
  - `[low]` `[reject]` (edge 14) Échec partiel de NVML : toutes les infos GPU perdues — valeur absente, jamais fausse ; découpage en plusieurs `try` = branches en plus.
  - `[maybe-false]` `[reject]` (edge 15) Distributions en double sous le même nom normalisé — à établir sur un environnement réel ; uv n'en installe qu'une ; si vrai, low.
  - `[low]` `[reject]` (edge 16) Clé `None` devient `"None"` — les clés des pipelines sont des identifiants textuels.
  - `[low]` `[patch]` (edge 17) Bases du lecteur non résolues : une jonction `data/raw` refuse une lecture légitime — toutes les bases résolues ; test de jonction.
  - `[maybe-false]` `[reject]` (edge 18) Lien physique vers `eval/` dans `data/raw` — demande un acte délibéré ; un contrôle `st_nlink` refuserait les liens légitimes ; si vrai, low.
  - `[low]` `[patch]` (edge 19) Connexion SQLite perdue si le PRAGMA lève — même cause que blind 7.
  - `[low]` `[reject]` (edge 20) Lecteur inexistant (`Q:/x`) → `FileNotFoundError` — échec bruyant.
  - `[low]` `[patch]` (edge 21) Assistant `content=""` sans appel accepté — même cause que blind 14.
  - `[low]` `[patch]` (edge 22) `NaN`/`Infinity` dans `arguments` acceptés — `parse_constant` qui lève ; test.
  - `[low]` `[patch]` (edge 23) Double réponse au même `tool_call_id` — même cause que blind 14.
  - `[maybe-false]` `[reject]` (edge 24) Instance typée mutée après construction — à établir sur un appelant réel ; usage improbable ; si vrai, low.
  - `[low]` `[patch]` (edge 25) `Progression` négative acceptée — `ge=0` sur `fait` et `total`.
  - `[maybe-false]` `[reject]` (edge 26) `resultat`/`arguments` non JSON — même note que blind 13.
  - `[low]` `[patch]` (edge 27) `assets` incomplet — même cause que blind 8.
  - `[low]` `[reject]` (edge 28) Clés de `binaires` absolues ou avec `..` — improbable ; validateur supplémentaire.
  - `[low]` `[patch]` (edge 29) `pooling`/`embedding` incohérents — même cause que blind 10.
  - `[low]` `[patch]` (edge 30) Motifs de `parents` et `llamacpp_tag` — même cause que blind 11.
  - `[low]` `[patch]` (edge 31) Tests dépendant de l'environnement — même cause que blind 15.
  - `[medium]` `[patch]` (edge 32, affirmation) « `run.json` intact après `ajouter_jsonl` » faux sous Windows — même cause que blind 1.

## Design Notes

- **Racine.** Toutes les fonctions prennent `racine` (racine du projet, défaut `racine_projet()`) : les runs vont sous `<racine>/runs/`, les listes de lecture sont résolues contre `<racine>`, sauf `models/` (`dossier_modeles()`) et le journal (`dossier_var() / "appels-mistral.sqlite"`). Un chemin relatif est résolu contre `racine`, puis `Path.resolve()` (liens et `..`).
- **Ordre de contrôle du lecteur.** Refus explicite d'abord (`<racine>/eval/**`, `<racine>/runs/eval-*/**`), puis liste d'accès ; sinon `LectureInterdite`. `runs/data-*` : premier niveau sous `runs/` commençant par `data-`.
- **Statut.** `run.json` garde `statut = en_cours` à jamais ; le statut courant est la dernière ligne valide d'`etat.jsonl` (`EtatRun`).
- **Reprise.** `fichier` et `cle` désignent le JSONL de résultats du pipeline et son champ clé (`generations.jsonl`/`item_id` pour l'évaluation) ; fichier absent = ensemble vide. Une dernière ligne tronquée (crash en cours d'écriture) est ignorée à la lecture, jamais réécrite.
- **Empreinte.** NVML en `try` (absent ou en erreur → `gpus=[]`, `pilote_nvidia=None`, `cuda=None`) ; paquets = toutes les distributions installées (`importlib.metadata`), noms normalisés en minuscules ; `git rev-parse HEAD` et `git status --porcelain` via `subprocess.run` avec `env_sous_processus()`, `CREATE_NO_WINDOW` sous Windows, délai 10 s ; échec → `None`.
- **`run_id`.** Heure locale `AAAAMMJJ-HHMMSS`, slug validé par `^[a-z0-9.-]+$`, 4 hex de `secrets.token_hex(2)` ; création du dossier par `mkdir(exist_ok=False)`.
- **Espace.** `SEUIL_ESPACE_LIBRE = 2 Gio` (constante surchargée par l'appelant depuis sa config) ; erreur si `shutil.disk_usage(premier parent existant).free < octets + seuil_octets`.

## Verification

**Commands:**
- `uv run pytest` -- expected: tout passe.
- `uv run ruff check` et `uv run ruff format --check` -- expected: aucun écart.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** Noyau de couche 0 :
- runs immuables `runs/<type>/<run_id>/` avec `run.json` (`RunManifest`) écrit une fois, statut en ajout dans `etat.jsonl`, reprise en ajout seul ;
- lecteur contrôlé `data`/`train` (AD-24, D-nuit-A2-18) ;
- contrôle d'espace disque ;
- ports du Harnais ;
- conversations OpenAI validées ;
- 10 évènements sérialisables en aller-retour ;
- schémas `RunManifest`, `EtatRun`, `ConfigModele`, `ConfigLlamacpp`.

**Fichiers.**
- `src/slmsp/core/schemas/__init__.py` : `SchemaBase`, `SousSchema`, type `Sha256`, sans réexport.
- `src/slmsp/core/schemas/run.py` : `Statut`, `STATUTS_FINAUX`, `ModeleRef`, `Gpu`, `Environnement`, `RunManifest`, `EtatRun`.
- `src/slmsp/core/schemas/config_modele.py` : `ConfigModele`, `FichierGguf` (AD-6, AD-28).
- `src/slmsp/core/schemas/config_llamacpp.py` : `ConfigLlamacpp`, `Asset`.
- `src/slmsp/core/artefacts.py` :
  - runs : `Run`, `nouveau_run`, `ouvrir_run`, `reprendre`, `ajouter_jsonl`, `empreinte_environnement` ;
  - lecteur : `chemin_autorise`, `lire`, `lire_texte`, `ouvrir_sqlite_lecture` ;
  - disque : `verifier_espace` ;
  - erreurs : `ArtefactExistant`, `EspaceInsuffisant`.
- `src/slmsp/core/ports.py` : `Passage`, `Mode`, et sept protocoles : `LlmPort`, `EmbedderPort`, `VectorStore`, `ToolPort`, `NetGate`, `ModePort`, `JournalRequetes`.
- `src/slmsp/core/messages.py` : `ConversationInvalide`, modèles de messages, `valider_conversation`, `vers_dicts`.
- `src/slmsp/core/evenements.py` : 10 évènements, `vers_dict`, `depuis_dict`.
- `tests/core/test_{artefacts,lecteur,schemas_run,ports,messages,evenements}.py` : 210 tests, dont 2 sautés (liens symboliques refusés par Windows ; la jonction NTFS couvre le même chemin).

**Revue** (une passe, 61 constats).
- Correctifs : 6 entrées medium et 22 low.
  - Les entrées medium : noms réservés contournables sous Windows ; NaN écrit `null` en silence ; `git_modifie` faussé par les fichiers non suivis.
  - Les low : tests VG, validateurs de schémas, contrôles de conversation, bases du lecteur résolues, connexion SQLite fermée, `ecrire` typé.
- Différé : 1 entrée, le journal Mistral lisible par `data`/`train` contiendra les appels `juge-second` (stories 5.5 et 9.2).
- Rejetés : 5 faux, 10 maybe-false et 12 low. Les raisons sont au journal de tri. Les principales :
  - pas de `fsync` ;
  - pas de garde de processus vivant pour `reprendre` ;
  - pas de `revision` sur `FichierGguf`.

**Relecture de suivi recommandée : oui.** Trois causes medium ont été corrigées, dont deux dans la garde d'immuabilité. Le risque non vérifié porte sur la garde des noms réservés sous Windows : elle s'appuie sur une liste de formes (point ou espace final, `:`) et sur une comparaison des chemins résolus. D'autres formes Win32 ne sont pas testées, comme les noms courts 8.3 (`RUN~1.JSO`) ou le préfixe `\\?\`.

**Vérification** (2026-10-12) :
- `uv run pytest` : 597 réussis, 4 sautés (2 liens symboliques ; 2 `duckdb` absents, hors zone) ;
- `uv run ruff check` et `uv run ruff format --check` : propres.

**Décisions prises seul** (à reporter au journal) :
1. Les erreurs `ArtefactExistant`, `EspaceInsuffisant` et `ConversationInvalide` sont des sous-classes de `SlmspError`, déclarées dans leur module (code 1). `core/erreurs.py` est hors zone.
2. `reprendre(run_id, *, fichier="resultats.jsonl", cle="cle", racine=None)` renvoie `(Run, set[str])`. Tout statut sauf `complet` peut être repris, y compris `en_cours` après un crash.
3. Toutes les fonctions prennent `racine` (défaut `racine_projet()`). Un chemin relatif est résolu contre `racine`. `models/` suit `SLMSP_MODELS_DIR`, et le journal suit `SLMSP_VAR_DIR`.
4. Le lecteur `data` refuse aussi `runs/eval/` (spine). Il refuse toute autre base de `SLMSP_VAR_DIR` que `appels-mistral.sqlite`.
5. `SEUIL_ESPACE_LIBRE` vaut 2 Gio, surchargé par l'appelant depuis sa config. `verifier_espace` renvoie l'espace libre.
6. `run.json` est écrit en JSON canonique. Le `run_id` utilise l'heure locale. `git_modifie` ignore les fichiers non suivis.
7. Une ligne JSONL invalide est ignorée à la lecture (fragment d'un arrêt brutal). L'ajout suivant commence sur une nouvelle ligne.
8. Les évènements ont un `type` en minuscules avec tirets (`appel-outil`…). `Mode` ∈ {`connecte`, `hors-ligne-detecte`, `hors-ligne-force`}. `ToolPort` est synchrone.
9. Dans `ConfigModele` :
   - `reasoning` ∈ {`off`, `on`, `auto`} ;
   - `cache_kv` ∈ {`f16`, `q8_0`, `q4_0`} ;
   - `chat_template_force` est un booléen ;
   - `embedding` et `pooling` doivent être cohérents.

   Dans `ConfigLlamacpp`, `assets` contient exactement `cpu`, `cuda` et `cudart`.

**Risques résiduels.**
- Les ajouts JSONL supposent un seul écrivain par fichier.
- `reprendre` ne détecte pas un second processus vivant.
- Il n'y a pas de `fsync`.
- L'empreinte de l'environnement liste toutes les distributions installées. Le `run.json` est donc volumineux, mais complet.
